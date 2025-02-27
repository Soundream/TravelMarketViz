import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import pandas as pd
import numpy as np
from matplotlib.ticker import FuncFormatter
import matplotlib.font_manager as fm
import os
import time
from matplotlib.ticker import MultipleLocator
import glob

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
frames_dir = os.path.join(output_dir, 'frames')
for directory in [logos_dir, output_dir, frames_dir]:
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

# Load the data from CSV
print("Loading data...")
data = pd.read_csv('Animated Bubble Chart_ Historic Financials Online Travel Industry - Revenue.csv')
print(f"Loaded {len(data)} rows of data")

# Add frame control parameter at the top of the file after imports
FRAMES_PER_YEAR = 4  # Controls how many frames to generate per year (like 24fps)

# Process the data to get annual Q1 data and special handling for 2024
def process_quarterly_data(data):
    print("\nDebug: Original columns:", data.columns.tolist())
    print("\nDebug: First few rows of original data:")
    print(data.head())
    
    # Remove the 'Revenue' row and reset index
    data = data[data.iloc[:, 0] != 'Revenue'].copy()
    data = data.reset_index(drop=True)  # Reset index after removing 'Revenue' row
    
    print("\nDebug: Data after removing Revenue row:")
    print(data.head())
    
    # Convert the first column to proper format for processing
    # Extract year and quarter from the string (e.g., "2024'Q1" -> 2024.0)
    data['Year'] = data.iloc[:, 0].apply(lambda x: float(x.split("'")[0]))
    data['Quarter'] = data.iloc[:, 0].apply(lambda x: int(x.split("Q")[1]))
    
    # Convert all revenue columns to numeric, with better error handling
    for col in data.columns[1:-2]:  # Skip the original year column and the new Year/Quarter columns
        # First replace empty strings and 'nan' with NaN
        data[col] = data[col].replace('', np.nan).replace('nan', np.nan)
        # Then convert to numeric
        data[col] = pd.to_numeric(data[col].apply(lambda x: str(x).replace('$', '').replace(',', '') if pd.notnull(x) else np.nan), errors='coerce')
    
    print("\nDebug: Data after numeric conversion:")
    print(data.head())
    print("\nDebug: ABNB column after conversion:")
    print(data['ABNB'].head())
    
    # For years before 2024, only keep Q1 data
    pre_2024 = data[data['Year'] < 2024].copy()
    pre_2024 = pre_2024[pre_2024['Quarter'] == 1]
    
    # For 2024, keep both Q1 and Q3
    year_2024 = data[data['Year'] == 2024].copy()
    year_2024 = year_2024[year_2024['Quarter'].isin([1, 3])]
    
    print("\nDebug: 2024 data:")
    print(year_2024)
    
    # Combine the data
    processed_data = pd.concat([pre_2024, year_2024])
    
    # For 2024 Q3, set the year to 2025 for interpolation
    processed_data.loc[(processed_data['Year'] == 2024) & (processed_data['Quarter'] == 3), 'Year'] = 2025.0
    
    # Drop the original year column and Quarter column
    processed_data = processed_data.drop(columns=[processed_data.columns[0], 'Quarter'])
    
    print("\nDebug: Final processed data:")
    print(processed_data.head())
    print("\nDebug: ABNB in final data:")
    print(processed_data['ABNB'].dropna())
    
    return processed_data

# Process the data
print("\nProcessing quarterly data...")
data = process_quarterly_data(data)
print(f"After processing: {len(data)} rows")

# Interpolate the data for smoother animation
def interpolate_data(data, multiple=20):
    all_interpolated = []
    companies = [col for col in data.columns if col != 'Year']
    print(f"\nFound {len(companies)} companies to process:")
    print(companies)
    
    for company in companies:
        try:
            print(f"\nProcessing {company}...")
            company_data = data[['Year', company]].copy()
            company_data.columns = ['Year', 'Revenue']
            company_data = company_data.dropna()
            
            print(f"Valid data points for {company}: {len(company_data)}")
            print(f"Data points for {company}:")
            print(company_data)
            
            if len(company_data) < 2:
                print(f"Skipping {company} - insufficient data points")
                continue
            
            min_year = company_data['Year'].min()
            max_year = company_data['Year'].max()
            print(f"Year range for {company}: {min_year} to {max_year}")
            
            if min_year >= 2020:
                years = np.linspace(min_year, max_year, int((max_year - min_year) * 4 * multiple))
                company_interp = pd.DataFrame()
                company_interp['Year'] = years
                company_interp['Company'] = company
                
                from scipy.interpolate import interp1d
                f = interp1d(company_data['Year'], company_data['Revenue'])
                company_interp['Revenue'] = f(years)
            else:
                has_2025_data = 2025.0 in company_data['Year'].values
                
                if has_2025_data:
                    quarters_before_2024 = np.arange(min_year, 2024.0, 0.25)
                    quarters_2024_2025 = np.array([2024.0, 2024.25, 2024.5, 2024.75, 2025.0])
                    quarters = np.concatenate([quarters_before_2024, quarters_2024_2025])
                else:
                    quarters = np.arange(min_year, 2024.25, 0.25)
                
                years = []
                for i in range(len(quarters)-1):
                    segment = np.linspace(quarters[i], quarters[i+1], multiple, endpoint=False)
                    years.extend(segment)
                years.append(quarters[-1])
                years = np.array(years)
                
                company_interp = pd.DataFrame()
                company_interp['Year'] = years
                company_interp['Company'] = company
                
                from scipy.interpolate import CubicSpline
                cs = CubicSpline(company_data['Year'], company_data['Revenue'])
                company_interp['Revenue'] = cs(years)
            
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
    
    print("\nCombining interpolated data...")
    result = pd.concat(all_interpolated, ignore_index=True)
    print(f"Final interpolated data shape: {result.shape}")
    print("\nCompanies in final interpolated data:")
    print(sorted(result['Company'].unique()))
    
    return result.sort_values('Year').reset_index(drop=True)

# Generate interpolated data
print("\nInterpolating data...")
interp_data = interpolate_data(data, multiple=FRAMES_PER_YEAR)  # Pass the frames per year parameter

# Save interpolated data for verification
interp_data.to_excel('output/interpolated_data.xlsx', index=False)
print(f"\nSaved interpolated data to output/interpolated_data.xlsx")

# Define the list of companies to display
selected_companies = [
    'ABNB', 'BKNG', 'DESP', 'EaseMyTrip', 'EDR', 'EXPE', 'LMN',
    'MMYT', 'Ixigo', 'OWW', 'SEERA', 'TCOM', 'TRIP', 'TRVG', 'Webjet', 'Yatra'
]

# Color dictionary for companies
color_dict = {
    'ABNB': '#ff5895', 'BKNG': '#003480', 'PCLN': '#003480',
    'DESP': '#755bd8', 'EaseMyTrip': '#00a0e2', 'EDR': '#2577e3',
    'EXPE': '#fbcc33', 'LMN': '#fc03b1', 'OWW': '#8edbfa',
    'SEERA': '#750808', 'TCOM': '#2577e3', 'TRIP': '#00af87',
    'TRVG': '#c71585', 'Webjet': '#e74c3c', 'Yatra': '#e74c3c',
    'MMYT': '#e74c3c', 'Ixigo': '#e74c3c'
}

# Company-specific settings for logos
logo_settings = {
    'ABNB': {'zoom': 0.06, 'offset': 430},
    'BKNG': {'zoom': 0.06, 'offset': 440},
    'PCLN_pre2014': {'zoom': 0.07, 'offset': 480},
    'PCLN_post2014': {'zoom': 0.07, 'offset': 500},
    'DESP': {'zoom': 0.08, 'offset': 440},
    'EaseMyTrip': {'zoom': 0.07, 'offset': 490},
    'EDR': {'zoom': 0.07, 'offset': 380},
    'EXPE': {'zoom': 0.06, 'offset': 490},
    'LMN': {'zoom': 0.22, 'offset': 480},
    'OWW': {'zoom': 0.11, 'offset': 400},
    'SEERA': {'zoom': 0.06, 'offset': 380},
    'SEERA_pre2019': {'zoom': 0.06, 'offset': 380},
    'TCOM': {'zoom': 0.11, 'offset': 430},
    'TCOM_pre2019': {'zoom': 0.05, 'offset': 380},
    'TRIP': {'zoom': 0.07, 'offset': 480},
    'TRIP_pre2020': {'zoom': 0.07, 'offset': 480},
    'TRVG': {'zoom': 0.07, 'offset': 400},
    'Webjet': {'zoom': 0.07, 'offset': 470},
    'Yatra': {'zoom': 0.06, 'offset': 400},
    'MMYT': {'zoom': 0.06, 'offset': 450},
    'Ixigo': {'zoom': 0.07, 'offset': 400},
    'LMN_2014_2015': {'zoom': 0.06, 'offset': 400}
}

# Load company logos
logos = {}
for company in selected_companies:
    if company == 'BKNG':
        pcln_logo_path = os.path.join(logos_dir, 'PCLN_logo.png')
        pcln_logo_path_2014 = os.path.join(logos_dir, '1PCLN_logo.png')
        bkng_logo_path = os.path.join(logos_dir, 'BKNG_logo.png')
        
        if os.path.exists(pcln_logo_path):
            logos['PCLN_pre2014'] = plt.imread(pcln_logo_path)
        if os.path.exists(pcln_logo_path_2014):
            logos['PCLN_post2014'] = plt.imread(pcln_logo_path_2014)
        if os.path.exists(bkng_logo_path):
            logos['BKNG'] = plt.imread(bkng_logo_path)
    elif company == 'TCOM':
        tcom_logo_old = os.path.join(logos_dir, '1TCOM_logo.png')
        tcom_logo_new = os.path.join(logos_dir, 'TCOM_logo.png')
        if os.path.exists(tcom_logo_old):
            logos['TCOM_pre2019'] = plt.imread(tcom_logo_old)
        if os.path.exists(tcom_logo_new):
            logos['TCOM'] = plt.imread(tcom_logo_new)
    elif company == 'TRIP':
        trip_logo_old = os.path.join(logos_dir, '1TRIP_logo.png')
        trip_logo_new = os.path.join(logos_dir, 'TRIP_logo.png')
        if os.path.exists(trip_logo_old):
            logos['TRIP_pre2020'] = plt.imread(trip_logo_old)
        if os.path.exists(trip_logo_new):
            logos['TRIP'] = plt.imread(trip_logo_new)
    elif company == 'SEERA':
        seera_logo_old = os.path.join(logos_dir, '1SEERA_logo.png')
        seera_logo_new = os.path.join(logos_dir, 'SEERA_logo.png')
        if os.path.exists(seera_logo_old):
            logos['SEERA_pre2019'] = plt.imread(seera_logo_old)
        if os.path.exists(seera_logo_new):
            logos['SEERA'] = plt.imread(seera_logo_new)
    elif company == 'LMN':
        lmn_logo_old = os.path.join(logos_dir, '1LMN_logo.png')
        lmn_logo_new = os.path.join(logos_dir, 'LMN_logo.png')
        if os.path.exists(lmn_logo_old):
            logos['LMN_2014_2015'] = plt.imread(lmn_logo_old)
        if os.path.exists(lmn_logo_new):
            logos['LMN'] = plt.imread(lmn_logo_new)
    else:
        logo_path = os.path.join(logos_dir, f'{company}_logo.png')
        if os.path.exists(logo_path):
            try:
                logos[company] = plt.imread(logo_path)
            except Exception as e:
                print(f"Error loading logo for {company}: {e}")
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

def create_frame(frame):
    """
    创建单个帧的图表
    frame: 当前时间点
    """
    # Create figure and axes with lower DPI for consistent logo positioning
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100)  # Keep DPI at 100 for consistent positioning
    gs = fig.add_gridspec(2, 1, height_ratios=[0.3, 4], hspace=0.2,
                         top=0.98, bottom=0.12)
    ax_timeline = fig.add_subplot(gs[0])
    ax = fig.add_subplot(gs[1])
    
    # Filter data for current frame
    yearly_data = interp_data[
        (interp_data['Year'] >= frame - 0.001) & 
        (interp_data['Year'] <= frame + 0.001)
    ].copy()
    
    # Filter selected companies and apply time restrictions
    filtered_companies = []
    for company in selected_companies:
        if company == 'TRVG' and frame < 2015.75:  # Before Q4 2015
            continue
        if company == 'MMYT' and frame < 2011.0:  # Before 2011
            continue
        if company == 'LMN' and frame >= 2003.75 and frame < 2014.0:  # LMN should not appear between Q3 2003 and 2014
            continue
        filtered_companies.append(company)
    
    yearly_data = yearly_data[yearly_data['Company'].isin(filtered_companies)]
    
    # Handle BKNG/PCLN name change
    if frame < 2018.08:
        yearly_data.loc[yearly_data['Company'] == 'BKNG', 'Company'] = 'PCLN'

    # Sort by revenue in descending order (largest to smallest)
    sorted_data = yearly_data.sort_values('Revenue', ascending=False)
    
    available_companies = len(sorted_data)
    top_companies = sorted_data
    
    num_bars = 16
    bar_height = 0.9
    spacing = 1.2
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
    ax.set_ylim((num_bars - 1) * spacing + spacing/2, -spacing/2)
    ax.set_xlim(0, current_x_limit)
    
    # Calculate figure width in pixels
    fig_width_inches = fig.get_size_inches()[0]
    dpi = fig.dpi
    fig_width_pixels = fig_width_inches * dpi
    
    # Add labels and logos
    for i, (bar, revenue, company) in enumerate(zip(bars, top_companies['Revenue'], top_companies['Company'].values)):
        width = bar.get_width()
        y_pos = bar.get_y() + bar.get_height() / 2
        
        if (company == 'LMN' and (width < 0 or abs(width) < 0.009)) or abs(width) < 0.01:
            continue
        
        # Add revenue label
        revenue_offset = current_x_limit * 0.02
        revenue_text = f'{width:,.2f}'
        ax.text(width + revenue_offset, y_pos, revenue_text,
                va='center', ha='left', fontsize=14,
                fontproperties=open_sans_font)
        
        # Add logo with adjusted offset calculation
        if company == 'PCLN' or company == 'BKNG':
            if frame < 2014.25:
                logo_key = 'PCLN_pre2014'
            elif frame < 2018.08:
                logo_key = 'PCLN_post2014'
            else:
                logo_key = 'BKNG'
        elif company == 'TCOM':
            logo_key = 'TCOM_pre2019' if frame < 2019.75 else 'TCOM'
        elif company == 'TRIP':
            logo_key = 'TRIP_pre2020' if frame < 2020.0 else 'TRIP'
        elif company == 'SEERA':
            logo_key = 'SEERA_pre2019' if frame < 2019.25 else 'SEERA'
        elif company == 'LMN':
            if frame >= 2014.0 and frame < 2015.42:
                logo_key = 'LMN_2014_2015'
            else:
                logo_key = 'LMN'
        else:
            logo_key = company
            
        if logo_key in logos:
            image = logos[logo_key]
            settings = logo_settings.get(logo_key, logo_settings.get(company, {'zoom': 0.12, 'offset': 100}))
            zoom = settings['zoom']
            pixel_offset = settings['offset']
            
            # Use figure width in pixels for offset calculation
            fig_width_inches = fig.get_size_inches()[0]
            dpi = fig.dpi
            fig_width_pixels = fig_width_inches * dpi
            data_offset = (pixel_offset / fig_width_pixels) * current_x_limit
            
            imagebox = OffsetImage(image, zoom=zoom)
            ab = AnnotationBbox(imagebox, (width + data_offset, y_pos),
                              frameon=False, box_alignment=(0.5, 0.5))
            ax.add_artist(ab)
    
    # Set y-ticks
    ax.set_yticks(all_positions)
    labels = [''] * num_bars
    
    companies_with_revenue = []
    positions_with_revenue = []
    for i, (company, revenue) in enumerate(zip(top_companies['Company'], top_companies['Revenue'])):
        if not ((company == 'LMN' and (revenue < 0 or abs(revenue) < 0.009)) or abs(revenue) < 0.01):
            companies_with_revenue.append(company)
            positions_with_revenue.append(all_positions[i])
    
    ax.set_yticks(positions_with_revenue)
    ax.set_yticklabels(companies_with_revenue, fontsize=14, fontproperties=open_sans_font)
    
    # Add grid lines
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
    
    # Set up the timeline
    ax_timeline.set_xlim(1996.5, 2025.5)
    ax_timeline.set_ylim(-0.2, 0.2)
    ax_timeline.get_yaxis().set_visible(False)

    ax_timeline.spines['top'].set_visible(False)
    ax_timeline.spines['right'].set_visible(False)
    ax_timeline.spines['left'].set_visible(False)
    ax_timeline.spines['bottom'].set_visible(True)
    ax_timeline.spines['bottom'].set_linewidth(1.5)
    ax_timeline.spines['bottom'].set_color('#808080')
    ax_timeline.spines['bottom'].set_position(('data', 0))

    ax_timeline.tick_params(axis='x', which='major', labelsize=12, length=6, width=1, colors='#808080')
    ax_timeline.xaxis.set_major_locator(MultipleLocator(1))
    ax_timeline.xaxis.set_minor_locator(MultipleLocator(0.5))
    ax_timeline.set_xticks(np.arange(1997, 2025, 1))
    ax_timeline.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x)}'))

    # Moving marker on timeline
    marker_position = frame
    ax_timeline.plot([marker_position], [0.05], marker='v',
                    color='#4e843d', markersize=10, zorder=5)

    # Add year ticks and labels
    for year in range(1997, 2025):
        ax_timeline.vlines(year, -0.03, 0, colors='#808080', linewidth=1)
        if year % 2 == 0:
            ax_timeline.text(year, -0.07, str(year), ha='center', va='top', fontsize=12, color='#808080')
        for quarter in [0.25, 0.5, 0.75]:
            quarter_year = year + quarter
            if quarter_year < 2025:
                ax_timeline.vlines(quarter_year, -0.02, 0, colors='#808080', linewidth=0.5, alpha=0.7)

    ax_timeline.set_xticklabels([])
    
    # Save the frame with high DPI
    frame_number = int((frame - 1997) * 100)
    frame_path = os.path.join(frames_dir, f'frame_{frame_number:04d}.png')
    plt.savefig(frame_path, dpi=300)  # Save with high DPI
    plt.close(fig)
    
    return frame_path

def get_last_frame_number(frames_dir):
    """
    Get the number of the last generated frame from the frames directory
    """
    if not os.path.exists(frames_dir):
        return -1
        
    frames = glob.glob(os.path.join(frames_dir, 'frame_*.png'))
    if not frames:
        return -1
        
    # Extract frame numbers and find the maximum
    frame_numbers = []
    for frame in frames:
        try:
            number = int(frame.split('frame_')[-1].split('.png')[0])
            frame_numbers.append(number)
        except:
            continue
            
    return max(frame_numbers) if frame_numbers else -1

# Generate all frames
print("\nGenerating frames...")
unique_years = np.unique(interp_data['Year'])
total_frames = len(unique_years)

# Get the last frame number
last_frame = get_last_frame_number(frames_dir)
if last_frame >= 0:
    print(f"\nFound existing frames, continuing from frame {last_frame}")
    # Calculate the corresponding year index
    year_index = last_frame // 100  # Since frame numbers are year*100
    if year_index < len(unique_years):
        unique_years = unique_years[year_index:]
        print(f"Continuing from year {unique_years[0]:.2f}")
    else:
        print("All frames have been generated!")
        unique_years = []

for i, year in enumerate(unique_years):
    frame_number = int((year - 1997) * 100)
    frame_path = os.path.join(frames_dir, f'frame_{frame_number:04d}.png')
    
    # Skip if frame already exists
    if os.path.exists(frame_path):
        print(f"\rSkipping existing frame {frame_number:04d} (Year: {year:.2f})", end="", flush=True)
        continue
        
    try:
        print(f"\rGenerating frame {frame_number:04d}/{(unique_years[-1]-1997)*100:.0f} (Year: {year:.2f})", end="", flush=True)
        create_frame(year)
    except Exception as e:
        print(f"\nError generating frame for year {year:.2f}: {e}")
        continue

print("\n\nAll frames generated successfully!")
print(f"Frames are saved in: {frames_dir}")