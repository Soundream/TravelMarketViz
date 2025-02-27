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
    'EXPE': {'zoom': 0.06, 'offset': 150},
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
    
    # Filter selected companies
    yearly_data = yearly_data[yearly_data['Company'].isin(selected_companies)]
    
    # Handle BKNG/PCLN name change
    if frame < 2018.08:
        yearly_data.loc[yearly_data['Company'] == 'BKNG', 'Company'] = 'PCLN'
    
    # Sort by revenue in descending order (largest to smallest)
    sorted_data = yearly_data.sort_values('Revenue', ascending=False)
    
    available_companies = len(sorted_data)
    top_companies = sorted_data  # No need for tail since we want all companies
    
    num_bars = 12  # 保持条数
    bar_height = 0.9  # 增加条形高度
    spacing = 1.4  # 增加条形间距
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
    marker_triangle = current_ax_timeline.plot([marker_position], [0.01], marker='v',  # 调整marker位置从0.02到0.01
                                    color='#4e843d', markersize=8, zorder=5)[0]  # 同时稍微减小marker大小

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
for quarter in preview_times:
    print(f"\nGenerating preview for Q{int((quarter % 1) * 4 + 1)}'{int(quarter)}")
    
    # Create preview figure and axes with the same layout as main figure
    plt.close('all')  # Close any existing figures
    fig_preview = plt.figure(figsize=(19.2, 10.8), dpi=100)
    gs_preview = fig_preview.add_gridspec(2, 1, height_ratios=[0.3, 4], hspace=0.2,
                                        top=0.98, bottom=0.12)  # 同步预览图的布局
    ax_timeline_preview = fig_preview.add_subplot(gs_preview[0])
    ax_preview = fig_preview.add_subplot(gs_preview[1])

    # Set the current figure
    plt.figure(fig_preview.number)

    # Update the visualization for this quarter
    update(quarter, preview=True)

    # Save preview
    quarter_str = f"{int(quarter)}_{int((quarter % 1) * 4 + 1)}"
    preview_path = os.path.join(preview_dir, f'preview_{quarter_str}.png')
    plt.savefig(preview_path, dpi=300)
    plt.close(fig_preview)
    print(f"Preview saved as {preview_path}")
    time.sleep(0.1)  # Add a small delay to ensure proper cleanup

print("\nAll preview frames saved in {preview_dir}")

# Ask user if they want to continue
input("Previews generated. Press Enter to continue with animation generation...")

# Create main figure and axes for animation with the same layout
plt.close('all')
fig = plt.figure(figsize=(19.2, 10.8), dpi=300)
gs = fig.add_gridspec(2, 1, height_ratios=[0.3, 4], hspace=0.2,
                     top=0.98, bottom=0.12)  # 同步动画的布局
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
         writer='ffmpeg', fps=24, bitrate=5000)

print("\nAnimation saved successfully!")
plt.show()