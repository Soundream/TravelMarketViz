import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import pandas as pd
import numpy as np
from matplotlib.ticker import FuncFormatter
import matplotlib.font_manager as fm
import os
import time
from matplotlib.ticker import MultipleLocator

# Set up font configurations
plt.rcParams['font.family'] = 'sans-serif'

# Check for Open Sans font, otherwise use a system sans-serif font
font_path = None
system_fonts = fm.findSystemFonts()
for font in system_fonts:
    if 'opensans' in font.lower() or 'open-sans' in font.lower():
        font_path = font
        break

if font_path:
    open_sans_font = fm.FontProperties(fname=font_path)
else:
    open_sans_font = fm.FontProperties(family='sans-serif')

# Create required directories
logos_dir = 'logos'
output_dir = 'output'
for directory in [logos_dir, output_dir]:
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

# Load the data from CSV
print("Loading data...")
data = pd.read_csv('Animated Bubble Chart_ Historic Financials Online Travel Industry - Raw_ Annual Revenue.csv')
print(f"Loaded {len(data)} rows of data")

# Print data info for debugging
print("\nData Info:")
print(data.info())
print("\nFirst few rows:")
print(data.head())

# Function to convert revenue string to numeric value
def revenue_to_numeric(revenue):
    try:
        if pd.isna(revenue):
            return None
        if isinstance(revenue, (int, float)):
            return float(revenue)
        # Remove commas and spaces
        revenue = str(revenue).replace(',', '').strip()
        # Remove 'M' and convert to float
        if revenue.endswith('M'):
            return float(revenue[:-1])
        return float(revenue)
    except (ValueError, TypeError) as e:
        print(f"Warning: Could not convert {revenue} to float: {e}")
        return None

# Function to convert year to numeric format
def year_to_numeric(year):
    try:
        return float(year)
    except (ValueError, TypeError) as e:
        print(f"Warning: Could not convert {year} to float: {e}")
        return None

# Drop the first row that contains 'Revenue'
data = data[data.iloc[:, 0] != 'Revenue'].copy()

# Convert the first column to numeric year and clean data
print("\nConverting years to numeric format...")
data.iloc[:, 0] = data.iloc[:, 0].apply(year_to_numeric)
data = data.dropna(subset=[data.columns[0]])
print(f"After cleaning: {len(data)} rows")

# Interpolate the data for smoother animation
def interpolate_data(data, multiple=20):
    all_interpolated = []
    
    # Get all companies (excluding the first column which is year)
    companies = data.columns[1:]
    print(f"\nFound {len(companies)} companies to process:")
    print(companies.tolist())
    
    for company in companies:
        try:
            print(f"\nProcessing {company}...")
            
            # Get current company's data
            company_data = data[[data.columns[0], company]].copy()
            company_data.columns = ['Year', 'Revenue']
            
            # Convert revenue to numeric and drop NaN
            company_data['Revenue'] = company_data['Revenue'].apply(revenue_to_numeric)
            company_data = company_data.dropna()
            
            print(f"Valid data points for {company}: {len(company_data)}")
            
            if len(company_data) < 2:
                print(f"Skipping {company} - insufficient data points")
                continue
                
            # Get time range
            min_year = company_data['Year'].min()
            max_year = company_data['Year'].max()
            print(f"Year range for {company}: {min_year} to {max_year}")
            
            # Create quarterly points
            quarters = np.arange(min_year, max_year + 0.25, 0.25)
            
            # Create additional points between quarters
            years = []
            for i in range(len(quarters)-1):
                segment = np.linspace(quarters[i], quarters[i+1], multiple, endpoint=False)
                years.extend(segment)
            years.append(max_year)
            years = np.array(years)
            
            # Create interpolated DataFrame
            company_interp = pd.DataFrame()
            company_interp['Year'] = years
            company_interp['Company'] = company
            
            # Use cubic spline interpolation
            from scipy.interpolate import CubicSpline
            cs = CubicSpline(company_data['Year'], company_data['Revenue'])
            company_interp['Revenue'] = cs(years)
            
            # Preserve original points
            for _, row in company_data.iterrows():
                mask = np.abs(years - row['Year']) < 1e-10
                if any(mask):
                    company_interp.loc[mask, 'Revenue'] = row['Revenue']
            
            print(f"Successfully interpolated {len(company_interp)} points for {company}")
            all_interpolated.append(company_interp)
            
        except Exception as e:
            print(f"Error interpolating {company}: {e}")
            continue

    if not all_interpolated:
        raise ValueError("No data could be interpolated. Please check your input data.")
    
    # Combine all interpolated data
    print("\nCombining interpolated data...")
    result = pd.concat(all_interpolated, ignore_index=True)
    print(f"Final interpolated data shape: {result.shape}")
    return result.sort_values('Year').reset_index(drop=True)

# Generate interpolated data
print("\nInterpolating data...")
interp_data = interpolate_data(data)

# Save interpolated data for verification
interp_data.to_excel('output/interpolated_data.xlsx', index=False)
print(f"\nSaved interpolated data to output/interpolated_data.xlsx")

# Define the list of companies to display
selected_companies = [
    'ABNB', 'BKNG', 'DESP', 'EaseMyTrip', 'EDR', 'EXPE', 'LMN',
    'OWW', 'SEERA', 'TCOM', 'TRIP', 'TRVG', 'WEB', 'YTRA'
]

# Color dictionary for companies
color_dict = {
    'ABNB': '#ff5895', 'BKNG': '#003480', 'PCLN': '#003480',
    'DESP': '#755bd8', 'EaseMyTrip': '#00a0e2', 'EDR': '#2577e3',
    'EXPE': '#fbcc33', 'LMN': '#fc03b1', 'OWW': '#8edbfa',
    'SEERA': '#750808', 'TCOM': '#2577e3', 'TRIP': '#00af87',
    'TRVG': '#c71585', 'WEB': '#fa8072', 'YTRA': '#800080'
}

# Company-specific settings for logos
logo_settings = {
    'ABNB': {'zoom': 0.12, 'offset': 100},
    'BKNG': {'zoom': 0.15, 'offset': 120},
    'PCLN': {'zoom': 0.15, 'offset': 120},
    'DESP': {'zoom': 0.10, 'offset': 90},
    'EaseMyTrip': {'zoom': 0.11, 'offset': 95},
    'EDR': {'zoom': 0.12, 'offset': 100},
    'EXPE': {'zoom': 0.13, 'offset': 110},
    'LMN': {'zoom': 0.12, 'offset': 100},
    'OWW': {'zoom': 0.11, 'offset': 95},
    'SEERA': {'zoom': 0.12, 'offset': 100},
    'TCOM': {'zoom': 0.11, 'offset': 95},
    'TRIP': {'zoom': 0.12, 'offset': 100},
    'TRVG': {'zoom': 0.11, 'offset': 95},
    'WEB': {'zoom': 0.12, 'offset': 100},
    'YTRA': {'zoom': 0.11, 'offset': 95}
}

# Load company logos
logos = {}
for company in selected_companies:
    logo_path = os.path.join(logos_dir, f'{company}_logo.png')
    if os.path.exists(logo_path):
        try:
            logos[company] = plt.imread(logo_path)
        except Exception as e:
            print(f"Error loading logo for {company}: {e}")
            # Create text-based placeholder
            fig_temp = plt.figure(figsize=(1, 1))
            ax_temp = fig_temp.add_subplot(111)
            ax_temp.text(0.5, 0.5, company, ha='center', va='center', fontsize=9)
            ax_temp.axis('off')
            temp_path = os.path.join(logos_dir, f'{company}_temp_logo.png')
            fig_temp.savefig(temp_path, transparent=True, bbox_inches='tight')
            plt.close(fig_temp)
            logos[company] = plt.imread(temp_path)

# Function to get quarter and year from numeric year
def get_quarter_year(time_value):
    year = int(time_value)
    quarter = int((time_value - year) * 4) + 1
    return f"{str(year)}'Q{quarter}"

# Function to get logo settings for specific company
def get_logo_settings(company):
    default_settings = {'zoom': 0.12, 'offset': 100}
    return logo_settings.get(company, default_settings)

# Set up the figure with fixed dimensions and margins
def setup_figure():
    fig = plt.figure(figsize=(19.2, 10.8), dpi=300)
    gs = fig.add_gridspec(2, 2, width_ratios=[3, 1], height_ratios=[0.4, 4.5], hspace=0.15,
                         top=0.95, bottom=0.15)
    
    # Timeline spanning both columns (top row)
    ax_timeline = fig.add_subplot(gs[0, :])
    
    # Bubble chart (bottom-left)
    ax = fig.add_subplot(gs[1, 0])
    
    # Bar chart timeline (above bar chart)
    ax_bar_timeline = fig.add_subplot(gs[0, 1])
    
    # Bar chart (bottom-right)
    ax_barchart = fig.add_subplot(gs[1, 1])
    
    # Set fixed margins to maintain consistent figure size
    plt.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.1)
    
    return fig, ax, ax_timeline, ax_barchart, ax_bar_timeline

# Animation update function
def update(frame, preview=False):
    # Use the correct figure and axes based on whether this is a preview or animation
    if preview:
        current_fig = fig_preview
        current_ax = ax_preview
        current_ax_timeline = ax_timeline_preview
        current_ax_bar = ax_barchart_preview
        current_ax_bar_timeline = ax_bar_timeline_preview
    else:
        current_fig = fig
        current_ax = ax
        current_ax_timeline = ax_timeline
        current_ax_bar = ax_barchart
        current_ax_bar_timeline = ax_bar_timeline
    
    # Clear all axes
    current_ax.clear()
    current_ax_timeline.clear()
    current_ax_bar.clear()
    current_ax_bar_timeline.clear()
    
    # Filter data for current frame
    yearly_data = interp_data[
        (interp_data['Year'] >= frame - 0.001) & 
        (interp_data['Year'] <= frame + 0.001)
    ].copy()
    
    # Filter selected companies
    yearly_data = yearly_data[yearly_data['Company'].isin(selected_companies)]
    
    # Handle BKNG/PCLN name change
    if frame < 2018.08:
        yearly_data.loc[yearly_data['Company'] == 'BKNG', 'Company'] = 'PCLN'
    
    # Sort by revenue in descending order (largest to smallest)
    sorted_data = yearly_data.sort_values('Revenue', ascending=False)
    
    # Get available companies (might be less than 15)
    available_companies = len(sorted_data)
    top_companies = sorted_data  # No need for tail since we want all companies
    
    # Create fixed bar positions with equal spacing (always 15 positions)
    num_bars = 15
    bar_height = 0.6  # Fixed bar height
    spacing = 1.0  # Fixed spacing between bars
    all_positions = np.arange(num_bars) * spacing
    
    # Calculate positions starting from the top
    y_positions = all_positions[:available_companies]
    
    # Get current maximum revenue for dynamic x-axis scaling
    current_max_revenue = top_companies['Revenue'].max()
    current_x_limit = current_max_revenue * 1.4  # Add 40% margin
    
    # Create bars only for available companies
    bars = current_ax.barh(y_positions, top_companies['Revenue'],
                   color=[color_dict.get(company, '#808080') for company in top_companies['Company']],
                   height=bar_height)
    
    # Set axis limits
    current_ax.set_ylim((num_bars - 1) * spacing + spacing/2, -spacing/2)  # Fixed y-axis limits
    current_ax.set_xlim(0, current_x_limit)  # Dynamic x-axis limits
    
    # Calculate figure width in pixels
    fig_width_inches = current_fig.get_size_inches()[0]
    dpi = current_fig.dpi
    fig_width_pixels = fig_width_inches * dpi
    
    # Add labels and logos only for available companies
    for i, (bar, revenue, company) in enumerate(zip(bars, top_companies['Revenue'], top_companies['Company'].values)):
        width = bar.get_width()
        y_pos = bar.get_y() + bar.get_height() / 2
        
        # Add revenue label with fixed offset from the end of the bar
        revenue_offset = current_x_limit * 0.02  # 2% of the x-axis range
        current_ax.text(width + revenue_offset, y_pos, f'{width:,.0f}',
                va='center', ha='left', fontsize=14,
                fontproperties=open_sans_font)
        
        # Add logo with company-specific size and position
        if company in logos:
            image = logos[company]
            settings = get_logo_settings(company)
            zoom = settings['zoom']
            # Convert pixel offset to data coordinates
            pixel_offset = settings['offset']
            data_offset = (pixel_offset / fig_width_pixels) * current_x_limit
            
            imagebox = OffsetImage(image, zoom=zoom)
            # Position logo using the custom offset
            ab = AnnotationBbox(imagebox, (width + data_offset, y_pos),
                              frameon=False, box_alignment=(0.5, 0.5))
            current_ax.add_artist(ab)
    
    # Set y-ticks for all positions but only label the ones with companies
    current_ax.set_yticks(all_positions)
    labels = [''] * num_bars  # Initialize empty labels for all positions
    # Fill in labels from top to bottom
    companies_list = top_companies['Company'].values.tolist()
    for i, company in enumerate(companies_list):
        labels[i] = company
    current_ax.set_yticklabels(labels, fontsize=14, fontproperties=open_sans_font)
    
    # Add grid lines with fixed intervals based on current maximum revenue
    if current_x_limit > 10000:
        interval = 2000
    elif current_x_limit > 5000:
        interval = 1000
    elif current_x_limit > 2000:
        interval = 500
    else:
        interval = 200
    
    grid_positions = np.arange(0, current_x_limit, interval)
    current_ax.set_xticks(grid_positions)
    current_ax.grid(axis='x', linestyle='--', alpha=0.3, color='gray')
    current_ax.set_xticklabels([f'{int(x):,}' for x in grid_positions], fontsize=12)
    
    # Customize appearance
    current_ax.spines['top'].set_visible(False)
    current_ax.spines['right'].set_visible(False)
    current_ax.spines['left'].set_visible(False)
    current_ax.spines['bottom'].set_visible(False)
    current_ax.set_xlabel('Revenue TTM (in Millions)', fontsize=16, labelpad=33)
    
    # Add quarter/year text
    current_ax.text(0.02, 0.98, get_quarter_year(frame),
            transform=current_ax.transAxes, fontsize=20,
            fontproperties=open_sans_font, va='top')
    
    # Set up the bar chart timeline
    current_ax_bar_timeline.set_xlim(1998.8, 2025)
    current_ax_bar_timeline.set_ylim(-0.04, 0.12)
    current_ax_bar_timeline.get_yaxis().set_visible(False)
    current_ax_bar_timeline.spines['top'].set_visible(False)
    current_ax_bar_timeline.spines['right'].set_visible(False)
    current_ax_bar_timeline.spines['left'].set_visible(False)
    current_ax_bar_timeline.spines['bottom'].set_position(('data', 0))
    current_ax_bar_timeline.spines['bottom'].set_color('black')
    current_ax_bar_timeline.tick_params(axis='x', which='major', labelsize=10, colors='black')
    current_ax_bar_timeline.xaxis.set_major_locator(MultipleLocator(1))
    current_ax_bar_timeline.xaxis.set_minor_locator(MultipleLocator(0.25))
    current_ax_bar_timeline.set_xticks(np.arange(1999, 2025, 1))
    current_ax_bar_timeline.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x)}'))
    
    # Add marker to bar chart timeline
    bar_marker = current_ax_bar_timeline.plot([frame], [0.02], marker='v', color='#4e843d', markersize=10)[0]
    artists_to_return = [bar_marker]
    
    return artists_to_return

# Before preview generation
print("\nGenerating preview images for each quarter...")
preview_dir = os.path.join(output_dir, 'previews')
if not os.path.exists(preview_dir):
    os.makedirs(preview_dir)

# Get all unique quarters from interpolated data
all_quarters = []
min_year = int(interp_data['Year'].min())
max_year = int(interp_data['Year'].max())

# Generate only actual quarter points (Q1, Q2, Q3, Q4) for each year
for year in range(min_year, max_year + 1):
    for quarter in [0, 0.25, 0.5, 0.75]:
        quarter_point = year + quarter
        if quarter_point >= min_year and quarter_point <= max_year:
            all_quarters.append(quarter_point)

all_quarters = sorted(all_quarters)
print(f"\nGenerating previews for {len(all_quarters)} quarters...")

# Generate preview for each quarter
for quarter in all_quarters:
    print(f"\nGenerating preview for Q{int((quarter % 1) * 4 + 1)}'{int(quarter)}")
    
    # Create preview figure and axes with the new setup
    fig_preview = plt.figure(figsize=(19.2, 10.8), dpi=100)
    gs_preview = fig_preview.add_gridspec(2, 2, width_ratios=[3, 1], height_ratios=[0.4, 4.5], hspace=0.15,
                                        top=0.95, bottom=0.15)
    ax_timeline_preview = fig_preview.add_subplot(gs_preview[0, :])
    ax_preview = fig_preview.add_subplot(gs_preview[1, 0])
    ax_bar_timeline_preview = fig_preview.add_subplot(gs_preview[0, 1])
    ax_barchart_preview = fig_preview.add_subplot(gs_preview[1, 1])
    
    # Set current figure and axes for the update function
    current_fig = fig_preview
    current_ax = ax_preview
    current_ax_timeline = ax_timeline_preview
    current_ax_bar = ax_barchart_preview
    current_ax_bar_timeline = ax_bar_timeline_preview
    
    # Update the visualization for this quarter
    update(quarter, preview=True)
    
    # ... [rest of the preview generation code remains the same] ...

# Create main figure and axes for animation with the new setup
fig, ax, ax_timeline, ax_barchart, ax_bar_timeline = setup_figure()

# Create animation
print("\nGenerating animation...")
ani = FuncAnimation(fig, update,
                   frames=np.unique(interp_data['Year']),
                   interval=50, repeat=False)

# Save animation
print("\nSaving animation...")
ani.save('output/evolution_of_online_travel.mp4', 
         writer='ffmpeg', fps=24, bitrate=5000)

print("\nAnimation saved successfully!")
plt.show()