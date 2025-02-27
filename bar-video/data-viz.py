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
        
        try:
            # Create interpolation points (quarterly)
            years = np.arange(min_year, max_year + 0.25, 0.25)  # 0.25 represents quarters
            
            # Create interpolated DataFrame
            company_interp = pd.DataFrame()
            company_interp['Year'] = years
            company_interp['Company'] = company
            
            # Use cubic spline interpolation for smoother transitions
            from scipy.interpolate import CubicSpline
            cs = CubicSpline(company_data['Year'], company_data['Revenue'])
            company_interp['Revenue'] = cs(years)
            
            # Ensure original points are preserved
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
    return f"Q{quarter}'{str(year)[-2:]}"

# Function to calculate zoom factor for logos
def get_zoom_factor(image, desired_width, ax):
    data_width = ax.get_xlim()[1] - ax.get_xlim()[0]
    fig_width = fig.get_size_inches()[0]
    scale = data_width / (fig_width * fig.dpi)
    native_width = image.shape[1]
    return (desired_width * fig.dpi) / (native_width * scale)

# Set up the figure
fig = plt.figure(figsize=(19.2, 10.8), dpi=300)
ax = fig.add_subplot(111)

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
    
    # Sort by revenue
    sorted_data = yearly_data.sort_values('Revenue', ascending=True)
    
    # Get top companies
    num_companies = min(len(sorted_data), 16)
    top_companies = sorted_data.tail(num_companies)
    
    # Create bar positions
    y_positions = np.arange(num_companies)[::-1]
    
    # Create bars
    bars = ax.barh(y_positions, top_companies['Revenue'],
                   color=[color_dict.get(company, '#808080') for company in top_companies['Company']],
                   height=0.8)
    
    # Set axis limits
    ax.set_ylim(-0.5, num_companies - 0.5)
    max_revenue = top_companies['Revenue'].max()
    ax.set_xlim(0, max_revenue * 1.4)
    
    # Add labels and logos
    for i, (bar, revenue, company) in enumerate(zip(bars, top_companies['Revenue'], top_companies['Company'])):
        width = bar.get_width()
        y_pos = bar.get_y() + bar.get_height() / 2
        
        # Add revenue label
        ax.text(width * 1.02, y_pos, f'{width:,.0f}',
                va='center', ha='left', fontsize=14,
                fontproperties=open_sans_font)
        
        # Add logo
        if company in logos:
            image = logos[company]
            zoom = get_zoom_factor(image, 0.006, ax)
            imagebox = OffsetImage(image, zoom=zoom)
            ab = AnnotationBbox(imagebox, (width * 1.20, y_pos),
                              frameon=False, box_alignment=(0.5, 0.5))
            ax.add_artist(ab)
    
    # Customize axes
    ax.set_yticks(y_positions)
    ax.set_yticklabels(top_companies['Company'], fontsize=14, fontproperties=open_sans_font)
    ax.invert_yaxis()
    
    # Add grid lines
    max_value = max_revenue * 1.4
    if max_value > 10000:
        interval = 2000
    elif max_value > 5000:
        interval = 1000
    elif max_value > 2000:
        interval = 500
    else:
        interval = 200
    
    grid_positions = np.arange(0, max_value, interval)
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