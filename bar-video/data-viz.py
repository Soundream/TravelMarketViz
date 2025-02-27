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
data = pd.read_csv('Animated Bubble Chart_ Historic Financials Online Travel Industry - Revenue.csv')
print(f"Loaded {len(data)} rows of data")

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
interp_data = interpolate_data(data)

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
    'TCOM_pre2019': {'zoom': 0.05, 'offset': 450},
    'TRIP': {'zoom': 0.07, 'offset': 420},
    'TRIP_pre2020': {'zoom': 0.07, 'offset': 440},
    'TRVG': {'zoom': 0.07, 'offset': 400},
    'Webjet': {'zoom': 0.07, 'offset': 470},
    'Yatra': {'zoom': 0.06, 'offset': 400},
    'MMYT': {'zoom': 0.06, 'offset': 450},
    'Ixigo': {'zoom': 0.07, 'offset': 400}
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

# Setup the figure and gridspec for the layout
fig = plt.figure(figsize=(19.2, 10.8), dpi=300)
gs = fig.add_gridspec(2, 1, height_ratios=[0.3, 4], hspace=0.2,
                     top=0.98, bottom=0.12)  # 增加底部边距以显示标签

# Timeline spanning the full width (top row)
ax_timeline = fig.add_subplot(gs[0])

# Bubble chart (bottom)
ax = fig.add_subplot(gs[1])

# Animation update function
def update(frame, preview=False):
    """
    更新动画帧
    frame: 当前时间点
    preview: 是否为预览模式
    """
    # Use the correct figure and axes based on whether this is a preview or animation
    if preview:
        current_fig = fig_preview
        current_ax = ax_preview
        current_ax_timeline = ax_timeline_preview
    else:
        current_fig = fig
        current_ax = ax
        current_ax_timeline = ax_timeline
    
    # Clear all axes
    current_ax.clear()
    current_ax_timeline.clear()
    
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
        if company == 'LMN':
            if frame >= 2003.75 and frame < 2014.0:  # 2003Q3 to 2014
                continue
        filtered_companies.append(company)
    
    yearly_data = yearly_data[yearly_data['Company'].isin(filtered_companies)]
    
    # Handle BKNG/PCLN name change
    if frame < 2018.08:
        yearly_data.loc[yearly_data['Company'] == 'BKNG', 'Company'] = 'PCLN'

    # Sort by revenue in descending order (largest to smallest)
    sorted_data = yearly_data.sort_values('Revenue', ascending=False)
    
    available_companies = len(sorted_data)
    top_companies = sorted_data  # No need for tail since we want all companies
    
    num_bars = 16  # 增加条数以适应更多公司
    bar_height = 0.9  # 保持条形高度
    spacing = 1.2  # 稍微减小间距以适应更多条形
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
        
        # Skip if LMN and revenue is negative or less than 0.009, or if revenue is zero for others
        if (company == 'LMN' and (width < 0 or abs(width) < 0.009)) or abs(width) < 0.01:
            continue
        
        # Add revenue label with fixed offset from the end of the bar
        revenue_offset = current_x_limit * 0.02  # 2% of the x-axis range
        # Format revenue with 2 decimal places
        revenue_text = f'{width:,.2f}'
        current_ax.text(width + revenue_offset, y_pos, revenue_text,
                va='center', ha='left', fontsize=14,
                fontproperties=open_sans_font)
        
        # Add logo with company-specific size and position
        if company == 'PCLN' or company == 'BKNG':
            if frame < 2014.25:  # Before April 2014
                logo_key = 'PCLN_pre2014'
            elif frame < 2018.08:  # Between April 2014 and BKNG change
                logo_key = 'PCLN_post2014'
            else:  # After BKNG change
                logo_key = 'BKNG'
        elif company == 'TCOM':
            logo_key = 'TCOM_pre2019' if frame < 2019.75 else 'TCOM'  # 2019.75 represents September 2019
        elif company == 'TRIP':
            logo_key = 'TRIP_pre2020' if frame < 2020.0 else 'TRIP'
        elif company == 'SEERA':
            logo_key = 'SEERA_pre2019' if frame < 2019.25 else 'SEERA'  # 2019.25 represents April 2019
        elif company == 'LMN':
            if frame >= 2014.0 and frame < 2015.42:  # 2014 to May 2015
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
            data_offset = (pixel_offset / fig_width_pixels) * current_x_limit
            
            imagebox = OffsetImage(image, zoom=zoom)
            ab = AnnotationBbox(imagebox, (width + data_offset, y_pos),
                              frameon=False, box_alignment=(0.5, 0.5))
            current_ax.add_artist(ab)
    
    # Set y-ticks for all positions but only label the ones with companies
    current_ax.set_yticks(all_positions)
    labels = [''] * num_bars  # Initialize empty labels for all positions
    
    # Fill in labels from top to bottom, skip companies with zero revenue
    companies_with_revenue = []
    positions_with_revenue = []
    for i, (company, revenue) in enumerate(zip(top_companies['Company'], top_companies['Revenue'])):
        if not ((company == 'LMN' and (revenue < 0 or abs(revenue) < 0.009)) or abs(revenue) < 0.01):
            companies_with_revenue.append(company)
            positions_with_revenue.append(all_positions[i])
    
    # Update y-ticks to only show positions with revenue
    current_ax.set_yticks(positions_with_revenue)
    current_ax.set_yticklabels(companies_with_revenue, fontsize=14, fontproperties=open_sans_font)
    
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
    
    # Set up the timeline
    current_ax_timeline.set_xlim(1996.5, 2025.5)  # 保持时间轴范围
    current_ax_timeline.set_ylim(-0.2, 0.2)  # 减小纵向范围使时间轴显得更宽
    current_ax_timeline.get_yaxis().set_visible(False)

    # 增加时间轴的可见度
    current_ax_timeline.spines['top'].set_visible(False)
    current_ax_timeline.spines['right'].set_visible(False)
    current_ax_timeline.spines['left'].set_visible(False)
    current_ax_timeline.spines['bottom'].set_visible(True)
    current_ax_timeline.spines['bottom'].set_linewidth(1.5)
    current_ax_timeline.spines['bottom'].set_color('#808080')  # 改为灰色
    current_ax_timeline.spines['bottom'].set_position(('data', 0))

    # 设置刻度
    current_ax_timeline.tick_params(axis='x', which='major', labelsize=12, length=6, width=1, colors='#808080')  # 改为灰色
    current_ax_timeline.xaxis.set_major_locator(MultipleLocator(1))  # 每年显示一次刻度
    current_ax_timeline.xaxis.set_minor_locator(MultipleLocator(0.5))  # 保持每半年的小刻度
    current_ax_timeline.set_xticks(np.arange(1997, 2025, 1))  # 每年显示一次年份
    current_ax_timeline.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x)}'))

    # Moving marker on timeline
    marker_position = frame
    marker_triangle = current_ax_timeline.plot([marker_position], [0.05], marker='v',  # 调整marker位置从0.02到0.01
                                    color='#4e843d', markersize=10, zorder=5)[0]  # 同时稍微减小marker大小

    # 添加年份标签和刻度（只在下方显示）
    for year in range(1997, 2025):
        # 年份刻度线
        current_ax_timeline.vlines(year, -0.03, 0, colors='#808080', linewidth=1)  # 改为灰色
        
        # 只在偶数年显示年份标签
        if year % 2 == 0:
            current_ax_timeline.text(year, -0.07, str(year), ha='center', va='top', fontsize=12, color='#808080')  # 改为灰色
        
        # 每季度刻度线
        for quarter in [0.25, 0.5, 0.75]:
            quarter_year = year + quarter
            if quarter_year < 2025:
                current_ax_timeline.vlines(quarter_year, -0.02, 0, colors='#808080', linewidth=0.5, alpha=0.7)  # 改为灰色

    # 移除原有的x轴标签
    current_ax_timeline.set_xticklabels([])

    artists_to_return = [marker_triangle]
    
    return bars

# Generate preview frames for all quarters
print("\nGenerating preview frames for all quarters...")
preview_dir = os.path.join(output_dir, 'previews')
if not os.path.exists(preview_dir):
    os.makedirs(preview_dir)

# Generate preview times for all quarters from 1997 to 2024
preview_times = []
for year in range(1997, 2025):  # From 1997 to 2024
    for quarter in [0.0, 0.25, 0.5, 0.75]:  # Four quarters per year
        preview_times.append(year + quarter)

# Generate preview for each quarter
for time_point in preview_times:
    year = int(time_point)
    quarter = int((time_point - year) * 4) + 1
    print(f"\nGenerating preview for {year}'Q{quarter}")
    
    # Create preview figure and axes with the same layout as main figure
    plt.close('all')
    fig_preview = plt.figure(figsize=(19.2, 10.8), dpi=100)
    gs_preview = fig_preview.add_gridspec(2, 1, height_ratios=[0.3, 4], hspace=0.2,
                                        top=0.98, bottom=0.12)
    ax_timeline_preview = fig_preview.add_subplot(gs_preview[0])
    ax_preview = fig_preview.add_subplot(gs_preview[1])

    # Set the current figure
    plt.figure(fig_preview.number)

    # Update the visualization for this quarter
    update(time_point, preview=True)

    # Save preview with quarter information
    preview_path = os.path.join(preview_dir, f'preview_{year}_Q{quarter}.png')
    plt.savefig(preview_path, dpi=300)
    plt.close(fig_preview)
    print(f"Preview saved as {preview_path}")
    time.sleep(0.1)  # Add a small delay to ensure proper cleanup

print(f"\nAll preview frames saved in {preview_dir}")

# Ask user if they want to continue
input("Previews generated. Press Enter to continue with animation generation...")

# Create main figure and axes for animation with the same layout
plt.close('all')
fig = plt.figure(figsize=(19.2, 10.8), dpi=150)  # 降低DPI从300到150
gs = fig.add_gridspec(2, 1, height_ratios=[0.3, 4], hspace=0.2,
                     top=0.98, bottom=0.12)
ax_timeline = fig.add_subplot(gs[0])
ax = fig.add_subplot(gs[1])

# Set the current figure
plt.figure(fig.number)

# Create animation
print("\nGenerating animation...")
ani = FuncAnimation(fig, update,
                   frames=np.unique(interp_data['Year']),
                   interval=50, repeat=False)

# Save animation
print("\nSaving animation...")
ani.save('output/evolution_of_online_travel.mp4', 
         writer='ffmpeg', fps=24, bitrate=2000)  # 降低比特率从5000到2000

print("\nAnimation saved successfully!")
plt.show()