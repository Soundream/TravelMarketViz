import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import pandas as pd
import numpy as np
from matplotlib.ticker import FuncFormatter
import matplotlib.font_manager as fm
import os
import time

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

# Function to calculate zoom factor for logos with fixed scale
def get_fixed_zoom_factor(image):
    return 0.12  # Reduced zoom factor for smaller logos

# Set up the figure with fixed dimensions and margins
def setup_figure():
    fig = plt.figure(figsize=(19.2, 10.8), dpi=300)
    ax = fig.add_subplot(111)
    # Set fixed margins to maintain consistent figure size
    plt.subplots_adjust(left=0.2, right=0.95, top=0.95, bottom=0.1)
    return fig, ax

# Animation update function
def update(frame):
    ax.clear()
    
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
    
    # Get available companies (might be less than 10)
    available_companies = len(sorted_data)
    top_companies = sorted_data  # No need for tail since we want all companies
    
    # Create fixed bar positions with equal spacing (always 10 positions)
    num_bars = 10
    bar_height = 0.6  # Fixed bar height
    spacing = 1.0  # Fixed spacing between bars
    all_positions = np.arange(num_bars) * spacing
    
    # Calculate positions starting from the top
    y_positions = all_positions[:available_companies]
    
    # Get current maximum revenue for dynamic x-axis scaling
    current_max_revenue = top_companies['Revenue'].max()
    current_x_limit = current_max_revenue * 1.4  # Add 40% margin
    
    # Create bars only for available companies
    bars = ax.barh(y_positions, top_companies['Revenue'],
                   color=[color_dict.get(company, '#808080') for company in top_companies['Company']],
                   height=bar_height)
    
    # Set axis limits
    ax.set_ylim((num_bars - 1) * spacing + spacing/2, -spacing/2)  # Fixed y-axis limits
    ax.set_xlim(0, current_x_limit)  # Dynamic x-axis limits
    
    # Add labels and logos only for available companies
    for i, (bar, revenue, company) in enumerate(zip(bars, top_companies['Revenue'], top_companies['Company'].values)):
        width = bar.get_width()
        y_pos = bar.get_y() + bar.get_height() / 2
        
        # Add revenue label with fixed offset from the end of the bar
        revenue_offset = current_x_limit * 0.02  # 2% of the x-axis range
        ax.text(width + revenue_offset, y_pos, f'{width:,.0f}',
                va='center', ha='left', fontsize=14,
                fontproperties=open_sans_font)
        
        # Add logo with fixed size and position
        if company in logos:
            image = logos[company]
            zoom = get_fixed_zoom_factor(image)
            imagebox = OffsetImage(image, zoom=zoom)
            # Use fixed offset from the end of the x-axis
            logo_offset = current_x_limit * 0.15  # 15% of the x-axis range
            ab = AnnotationBbox(imagebox, (width + logo_offset, y_pos),
                              frameon=False, box_alignment=(0.5, 0.5))
            ax.add_artist(ab)
    
    # Set y-ticks for all positions but only label the ones with companies
    ax.set_yticks(all_positions)
    labels = [''] * num_bars  # Initialize empty labels for all positions
    # Fill in labels from top to bottom
    companies_list = top_companies['Company'].values.tolist()
    for i, company in enumerate(companies_list):
        labels[i] = company
    ax.set_yticklabels(labels, fontsize=14, fontproperties=open_sans_font)
    
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
    ax.set_xticks(grid_positions)
    ax.grid(axis='x', linestyle='--', alpha=0.3, color='gray')
    ax.set_xticklabels([f'{int(x):,}' for x in grid_positions], fontsize=12)
    
    # Customize appearance
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.set_xlabel('Revenue TTM (in Millions)', fontsize=16, labelpad=33)
    
    # Add quarter/year text
    ax.text(0.02, 0.98, get_quarter_year(frame),
            transform=ax.transAxes, fontsize=20,
            fontproperties=open_sans_font, va='top')
    
    return bars

# Generate preview frames for each quarter
print("\nGenerating preview frames...")
preview_dir = os.path.join(output_dir, 'previews')
if not os.path.exists(preview_dir):
    os.makedirs(preview_dir)

# Get unique years and quarters for previews
min_year = int(interp_data['Year'].min())
max_year = int(interp_data['Year'].max())
preview_times = []

# Generate quarterly time points
for year in range(min_year, max_year + 1):
    for quarter in range(4):
        time_point = year + quarter * 0.25
        if time_point >= interp_data['Year'].min() and time_point <= interp_data['Year'].max():
            preview_times.append(time_point)

# Generate preview for each quarter
for time_point in preview_times:
    # Create a new figure for each preview
    plt.close('all')  # Close all existing figures
    fig, ax = setup_figure()
    
    # Generate frame for this time point
    update(time_point)

    # Save preview without tight layout
    quarter_year = get_quarter_year(time_point)
    preview_path = os.path.join(preview_dir, f'preview_{quarter_year}.png')
    plt.savefig(preview_path, dpi=300, bbox_inches=None)
    print(f"Generated preview for {quarter_year}")
    plt.close(fig)  # Properly close the figure
    time.sleep(0.1)  # Add a small delay to ensure proper cleanup

print(f"\nAll preview frames saved in {preview_dir}")

# Ask user if they want to continue
input("Previews generated. Press Enter to continue with animation generation...")

# Create a new figure for the animation
plt.close('all')  # Close all existing figures
fig, ax = setup_figure()

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