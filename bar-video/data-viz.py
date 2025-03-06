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
import argparse
from PIL import Image
from PIL import ImageFilter
from PIL import ImageEnhance

# Add argument parser
parser = argparse.ArgumentParser(description='Generate bar chart race visualization')
parser.add_argument('--publish', action='store_true', help='Generate high quality version for publishing')
args = parser.parse_args()

# Set quality parameters based on mode
if args.publish:
    FRAMES_PER_YEAR = 96  # Increase frames for smoother animation
    OUTPUT_DPI = 300      # Increase DPI for higher quality
    FIGURE_SIZE = (25.6, 14.4)  # Larger figure size (4K aspect ratio)
else:
    FRAMES_PER_YEAR = 24   # Increase preview frames for smoother testing
    OUTPUT_DPI = 200      # Moderate DPI for preview
    FIGURE_SIZE = (19.2, 10.8)  # Same size

def preprocess_logo(image_array, target_size=None, upscale_factor=8):
    """
    预处理logo图像以提高质量
    
    Args:
        image_array: 原始图像数组
        target_size: 目标尺寸 (width, height)
        upscale_factor: 上采样倍数
    """
    if isinstance(image_array, np.ndarray):
        if image_array.dtype == np.float32:
            image_array = (image_array * 255).astype(np.uint8)
        image = Image.fromarray(image_array)
    else:
        image = image_array
        
    # 保存原始模式
    original_mode = image.mode
    
    if target_size:
        w, h = target_size
        
        if args.publish:
            # 发布模式使用两步处理
            # 第一步：放大到目标尺寸的4倍
            intermediate_size = (w * 4, h * 4)
            image = image.resize(intermediate_size, Image.Resampling.LANCZOS)
            
            # 基本图像增强
            if original_mode == 'RGBA':
                r, g, b, a = image.split()
                rgb = Image.merge('RGB', (r, g, b))
                # 适度的锐化和增强
                rgb = rgb.filter(ImageFilter.UnsharpMask(radius=0.5, percent=150, threshold=3))
                rgb = rgb.filter(ImageFilter.EDGE_ENHANCE)
                r, g, b = rgb.split()
                # 轻微增强透明通道
                a = a.filter(ImageFilter.UnsharpMask(radius=0.3, percent=130, threshold=3))
                image = Image.merge('RGBA', (r, g, b, a))
            else:
                image = image.filter(ImageFilter.UnsharpMask(radius=0.5, percent=150, threshold=3))
                image = image.filter(ImageFilter.EDGE_ENHANCE)
            
            # 第二步：缩放到目标尺寸
            image = image.resize(target_size, Image.Resampling.LANCZOS)
        else:
            # 预览模式使用单步处理
            # 放大到目标尺寸的2倍
            intermediate_size = (w * 2, h * 2)
            image = image.resize(intermediate_size, Image.Resampling.LANCZOS)
            
            # 轻量级增强
            if original_mode == 'RGBA':
                r, g, b, a = image.split()
                rgb = Image.merge('RGB', (r, g, b))
                rgb = rgb.filter(ImageFilter.EDGE_ENHANCE)
                r, g, b = rgb.split()
                image = Image.merge('RGBA', (r, g, b, a))
            else:
                image = image.filter(ImageFilter.EDGE_ENHANCE)
            
            # 缩放到最终尺寸
            image = image.resize(target_size, Image.Resampling.LANCZOS)
    
    return np.array(image)

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
    
    # First, determine the overall time range and create a unified time grid
    min_year = data['Year'].min()
    max_year = data['Year'].max()
    print(f"\nOverall year range: {min_year} to {max_year}")
    
    # Create unified time points for all companies with increased density
    if min_year >= 2020:
        # Increase the density of points for recent years
        unified_years = np.linspace(min_year, max_year, int((max_year - min_year) * 12 * multiple))
    else:
        # Create more granular quarters with sub-quarter points
        sub_quarters_per_quarter = 12  # Increase this for more smoothness
        quarters_before_2024 = np.arange(min_year, 2024.0, 0.25)
        quarters_2024_2025 = np.array([2024.0, 2024.25, 2024.5, 2024.75, 2025.0])
        quarters = np.concatenate([quarters_before_2024, quarters_2024_2025])
        
        unified_years = []
        for i in range(len(quarters)-1):
            # Create more points between quarters
            segment = np.linspace(quarters[i], quarters[i+1], sub_quarters_per_quarter * multiple, endpoint=False)
            unified_years.extend(segment)
        unified_years.append(quarters[-1])
        unified_years = np.array(unified_years)
    
    print(f"Created {len(unified_years)} unified time points")
    
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
            
            company_min_year = company_data['Year'].min()
            company_max_year = company_data['Year'].max()
            print(f"Year range for {company}: {company_min_year} to {company_max_year}")
            
            # Create interpolation for this company's date range
            mask = (unified_years >= company_min_year) & (unified_years <= company_max_year)
            company_years = unified_years[mask]
            
            company_interp = pd.DataFrame()
            company_interp['Year'] = company_years
            company_interp['Company'] = company
            
            # Use CubicSpline with more natural boundary conditions
            from scipy.interpolate import CubicSpline
            cs = CubicSpline(company_data['Year'], company_data['Revenue'], bc_type='natural')
            company_interp['Revenue'] = cs(company_years)
            
            # Ensure exact values at known data points and smooth transitions
            for _, row in company_data.iterrows():
                mask = np.abs(company_years - row['Year']) < 1e-10
                if any(mask):
                    exact_value = row['Revenue']
                    company_interp.loc[mask, 'Revenue'] = exact_value
                    
                    # Smooth out transitions near exact points
                    window = (np.abs(company_years - row['Year']) < 0.1) & (~mask)
                    if any(window):
                        weights = 1 - (np.abs(company_years[window] - row['Year']) / 0.1)
                        company_interp.loc[window, 'Revenue'] = (
                            weights * exact_value + 
                            (1 - weights) * company_interp.loc[window, 'Revenue']
                        )
            
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
    
    # Additional smoothing for the entire dataset
    result = result.sort_values(['Company', 'Year']).reset_index(drop=True)
    
    return result

# Generate interpolated data
print("\nInterpolating data...")
interp_data = interpolate_data(data, multiple=FRAMES_PER_YEAR)  # Pass the frames per year parameter

print(f"\nInterpolation complete. Generated {len(interp_data)} data points.")

# Define company name to ticker mapping and its reverse mapping
company_to_ticker = {
    'EaseMyTrip': 'EASEMYTRIP',
    'Ixigo': 'IXIGO',
    'Yatra': 'YTRA',
    'Webjet': 'WBJ'
}
ticker_to_company = {v: k for k, v in company_to_ticker.items()}

# Define the list of companies to display
selected_companies = [
    'ABNB', 'BKNG', 'DESP', 'EaseMyTrip', 'EDR', 'EXPE', 'LMN',
    'MMYT', 'Ixigo', 'OWW', 'SEERA', 'TCOM', 'TRIP', 'TRVG', 'Webjet', 'Yatra',"Travelocity",'Orbitz'
]

# Color dictionary for companies
color_dict = {
    'ABNB': '#ff5895', 'BKNG': '#003480', 'PCLN': '#003480',
    'DESP': '#755bd8', 'EASEMYTRIP': '#00a0e2', 'EDR': '#2577e3',
    'EXPE': '#fbcc33', 'LMN': '#fc03b1', 'OWW': '#8edbfa',
    'SEERA': '#750808', 'TCOM': '#2577e3', 'TRIP': '#00af87',
    'TRVG': '#c71585', 'WBJ': '#e74c3c', 'YTRA': '#e74c3c',
    'MMYT': '#e74c3c', 'IXIGO': '#e74c3c',"Travelocity":'#1d3e5c','Orbitz': '#8edbfa','Webjet': '#e74c3c',
    'Yatra': '#e74c3c',
    'Ixigo': '#e74c3c',
    'EaseMyTrip': '#00a0e2',
}

# Company-specific settings for logos
logo_settings = {
    'Orbitz':{'zoom': 0.08, 'offset': 1290},
    'Orbitz1':{'zoom': 0.027, 'offset': 1440},
    "Travelocity":{'zoom': 0.053, 'offset': 1440},
    'ABNB': {'zoom': 0.08, 'offset': 1290},
    'BKNG': {'zoom': 0.08, 'offset': 1620},
    'PCLN_pre2014': {'zoom': 0.093, 'offset': 1640},
    'PCLN_post2014': {'zoom': 0.093, 'offset': 1600},
    'DESP': {'zoom': 0.107, 'offset': 1320},
    'EASEMYTRIP': {'zoom': 0.08, 'offset': 1400},
    'EDR': {'zoom': 0.093, 'offset': 1140},
    'EXPE': {'zoom': 0.08, 'offset': 1670},
    'EXPE_pre2010': {'zoom': 0.033, 'offset': 1410},
    'EXPE_2010_2012': {'zoom': 0.08, 'offset': 1670},
    'LMN': {'zoom': 0.293, 'offset': 1640},
    'OWW': {'zoom': 0.147, 'offset': 1200},
    'SEERA': {'zoom': 0.08, 'offset': 1140},
    'SEERA_pre2019': {'zoom': 0.08, 'offset': 1140},
    'TCOM': {'zoom': 0.147, 'offset': 1290},
    'TCOM_pre2019': {'zoom': 0.067, 'offset': 1140},
    'TRIP': {'zoom': 0.093, 'offset': 1640},
    'TRIP_pre2020': {'zoom': 0.093, 'offset': 1640},
    'TRVG': {'zoom': 0.093, 'offset': 1200},
    'TRVG_pre2013': {'zoom': 0.12, 'offset': 1200},
    'TRVG_2013_2023': {'zoom': 0.12, 'offset': 1200},
    'WEB': {'zoom': 0.07, 'offset': 1400},
    'Webjet': {'zoom': 0.07, 'offset': 1400},
    'WBJ': {'zoom': 0.07, 'offset': 2000},
    'Yatra': {'zoom': 0.07, 'offset': 1300},
    'YTRA': {'zoom': 0.07, 'offset': 1300},
    'MMYT': {'zoom': 0.08, 'offset': 1350},
    'IXIGO': {'zoom': 0.14, 'offset': 1200},
    'LMN_2014_2015': {'zoom': 0.08, 'offset': 1400},
    'EaseMyTrip': {'zoom': 0.08, 'offset': 1400},
    'Ixigo': {'zoom': 0.08, 'offset': 1200}
}

# Load company logos
logos = {}
for company in selected_companies:
    if company == 'BKNG':
        pcln_logo_path = os.path.join(logos_dir, 'PCLN_logo.png')
        pcln_logo_path_2014 = os.path.join(logos_dir, '1PCLN_logo.png')
        bkng_logo_path = os.path.join(logos_dir, 'BKNG_logo.png')
        
        if os.path.exists(pcln_logo_path):
            logos['PCLN_pre2014'] = preprocess_logo(plt.imread(pcln_logo_path))
        if os.path.exists(pcln_logo_path_2014):
            logos['PCLN_post2014'] = preprocess_logo(plt.imread(pcln_logo_path_2014))
        if os.path.exists(bkng_logo_path):
            logos['BKNG'] = preprocess_logo(plt.imread(bkng_logo_path))
    elif company == 'TRVG':
        trvg_logo_old = os.path.join(logos_dir, 'Trivago1.jpg')
        trvg_logo_mid = os.path.join(logos_dir, 'Trivago2.jpg')
        trvg_logo_new = os.path.join(logos_dir, 'TRVG_logo.png')
        if os.path.exists(trvg_logo_old):
            logos['TRVG_pre2013'] = preprocess_logo(plt.imread(trvg_logo_old))
        if os.path.exists(trvg_logo_mid):
            logos['TRVG_2013_2023'] = preprocess_logo(plt.imread(trvg_logo_mid))
        if os.path.exists(trvg_logo_new):
            logos['TRVG'] = preprocess_logo(plt.imread(trvg_logo_new))
    elif company == 'EXPE':
        expe_logo_old = os.path.join(logos_dir, '1_expedia.png')
        expe_logo_mid = os.path.join(logos_dir, 'EXPE_logo.png')
        expe_logo_new = os.path.join(logos_dir, 'EXPE_logo.png')
        if os.path.exists(expe_logo_old):
            logos['EXPE_pre2010'] = preprocess_logo(plt.imread(expe_logo_old))
        if os.path.exists(expe_logo_mid):
            logos['EXPE_2010_2012'] = preprocess_logo(plt.imread(expe_logo_mid))
        if os.path.exists(expe_logo_new):
            logos['EXPE'] = preprocess_logo(plt.imread(expe_logo_new))
    elif company == 'TCOM':
        tcom_logo_old = os.path.join(logos_dir, '1TCOM_logo.png')
        tcom_logo_new = os.path.join(logos_dir, 'TCOM_logo.png')
        if os.path.exists(tcom_logo_old):
            logos['TCOM_pre2019'] = preprocess_logo(plt.imread(tcom_logo_old))
        if os.path.exists(tcom_logo_new):
            logos['TCOM'] = preprocess_logo(plt.imread(tcom_logo_new))
    elif company == 'TRIP':
        trip_logo_old = os.path.join(logos_dir, '1TRIP_logo.png')
        trip_logo_new = os.path.join(logos_dir, 'TRIP_logo.png')
        if os.path.exists(trip_logo_old):
            logos['TRIP_pre2020'] = preprocess_logo(plt.imread(trip_logo_old))
        if os.path.exists(trip_logo_new):
            logos['TRIP'] = preprocess_logo(plt.imread(trip_logo_new))
    elif company == 'SEERA':
        seera_logo_old = os.path.join(logos_dir, '1SEERA_logo.png')
        seera_logo_new = os.path.join(logos_dir, 'SEERA_logo.png')
        if os.path.exists(seera_logo_old):
            logos['SEERA_pre2019'] = preprocess_logo(plt.imread(seera_logo_old))
        if os.path.exists(seera_logo_new):
            logos['SEERA'] = preprocess_logo(plt.imread(seera_logo_new))
    elif company == 'LMN':
        lmn_logo_old = os.path.join(logos_dir, '1LMN_logo.png')
        lmn_logo_new = os.path.join(logos_dir, 'LMN_logo.png')
        if os.path.exists(lmn_logo_old):
            logos['LMN_2014_2015'] = preprocess_logo(plt.imread(lmn_logo_old))
        if os.path.exists(lmn_logo_new):
            logos['LMN'] = preprocess_logo(plt.imread(lmn_logo_new))
    elif company == 'Orbitz':
        orbitz_logo_old = os.path.join(logos_dir, 'Orbitz1.png')
        orbitz_logo_new = os.path.join(logos_dir, 'Orbitz_logo.png')
        if os.path.exists(orbitz_logo_old):
            logos['Orbitz1'] = preprocess_logo(plt.imread(orbitz_logo_old))
        if os.path.exists(orbitz_logo_new):
            logos['Orbitz'] = preprocess_logo(plt.imread(orbitz_logo_new))
    else:
        logo_path = os.path.join(logos_dir, f'{company}_logo.png')
        if os.path.exists(logo_path):
            try:
                logos[company] = preprocess_logo(plt.imread(logo_path))
            except Exception as e:
                print(f"Error loading logo for {company}: {e}")
                fig_temp = plt.figure(figsize=(1, 1))
                ax_temp = fig_temp.add_subplot(111)
                ax_temp.text(0.5, 0.5, company, ha='center', va='center', fontsize=9)
                ax_temp.axis('off')
                temp_path = os.path.join(logos_dir, f'{company}_temp_logo.png')
                fig_temp.savefig(temp_path, transparent=True, bbox_inches='tight')
                plt.close(fig_temp)
                logos[company] = preprocess_logo(plt.imread(temp_path))

# Function to get quarter and year from numeric year
def get_quarter_year(time_value):
    year = int(time_value)
    quarter = int((time_value - year) * 4) + 1
    return f"{str(year)}'Q{quarter}"

# Function to get logo settings for specific company
def get_logo_settings(company):
    # Convert ticker to company name if needed
    company_name = ticker_to_company.get(company, company)
    default_settings = {'zoom': 0.12, 'offset': 100}
    return logo_settings.get(company_name, logo_settings.get(company, default_settings))

def create_frame(frame):
    """
    创建单个帧的图表
    frame: 当前时间点
    """
    # Create figure and axes with mode-dependent DPI
    fig = plt.figure(figsize=FIGURE_SIZE, dpi=OUTPUT_DPI)
    gs = fig.add_gridspec(2, 1, height_ratios=[0.3, 4], hspace=0.2,
                         top=0.98, bottom=0.12)
    ax_timeline = fig.add_subplot(gs[0])
    ax = fig.add_subplot(gs[1])
    
    # Increase the time window to avoid missing data points
    TIME_WINDOW = 0.01  # Increased from 0.001 to 0.01
    
    # Filter data for current frame with wider window
    yearly_data = interp_data[
        (interp_data['Year'] >= frame - TIME_WINDOW) & 
        (interp_data['Year'] <= frame + TIME_WINDOW)
    ].copy()
    
    # If no data found with current window, try an even wider window
    if len(yearly_data) == 0:
        TIME_WINDOW = 0.02
        yearly_data = interp_data[
            (interp_data['Year'] >= frame - TIME_WINDOW) & 
            (interp_data['Year'] <= frame + TIME_WINDOW)
        ].copy()
    
    # Filter selected companies and apply time restrictions
    filtered_companies = []
    for company in selected_companies:
        if company == 'Travelocity':
            continue
        if company == 'DESP' and frame < 2017.45: 
            continue# Mar 1999
        # IPO date restrictions
        if company == 'BKNG' and frame < 1999.17:  # Mar 1999
            continue
        if company == 'EXPE' and frame < 1999.83:  # Nov 1999
            continue
        if company == 'TCOM' and frame < 2003.92:  # Dec 2003
            continue
        if company == 'Orbitz' and frame < 2003.92:  # Dec 2003
            continue
        if company == 'SEERA' and frame < 2012.25:  # Apr 2012
            continue
        if company == 'EDR' and frame < 2014.25:  # Apr 2014
            continue
        if company == 'LMN' and frame < 2000.33:  # Apr 2014
            continue
        if company == 'TRVG' and frame < 2016.92:  
            continue
        if company == 'ABNB' and frame < 2020.92:  # Dec 2020
            continue
        if company == 'EASEMYTRIP' and frame < 2021.17:  # Mar 2021
            continue
        if company == 'IXIGO' and frame < 2024.42:  # Jun 2024
            continue
        if company == 'TRIP' and frame < 2011.92:  
            continue
        # Existing time restrictions
        if company == 'MMYT' and frame < 2011.0:  # Before 2011
            continue
        if company == 'LMN' and frame >= 2003.75 and frame < 2014.0:  # LMN should not appear between Q3 2003 and 2014
            continue
            
        filtered_companies.append(company)
    
    yearly_data = yearly_data[yearly_data['Company'].isin(filtered_companies)]
    
    # Handle BKNG/PCLN name change
    if frame < 2018.08:
        yearly_data.loc[yearly_data['Company'] == 'BKNG', 'Company'] = 'PCLN'

    # If we have multiple rows for the same company, use the closest one to the frame
    if len(yearly_data) > len(yearly_data['Company'].unique()):
        yearly_data['time_diff'] = abs(yearly_data['Year'] - frame)
        yearly_data = yearly_data.sort_values('time_diff').groupby('Company').first().reset_index()
        yearly_data = yearly_data.drop('time_diff', axis=1)

    # Sort by revenue in descending order (largest to smallest)
    sorted_data = yearly_data.sort_values('Revenue', ascending=False)
    
    available_companies = len(sorted_data)
    top_companies = sorted_data
    # 
    # 
    
    num_bars = 18
    bar_height = 0.9
    spacing = 1.1
    all_positions = np.arange(num_bars) * spacing
    
    # Calculate positions starting from the top
    y_positions = all_positions[:available_companies]
    
    # Get current maximum revenue for dynamic x-axis scaling
    current_max_revenue = top_companies['Revenue'].max()
    
    # Get historical maximum revenue up to current frame
    historical_data = interp_data[interp_data['Year'] <= frame]
    historical_max_revenue = historical_data['Revenue'].max()
    
    # Use max of current first row and historical maximum
    max_revenue = max(current_max_revenue, historical_max_revenue)
    
    # Set x-limit based on max revenue with some padding
    current_x_limit = max_revenue * 1.2  # Add 20% margin
    
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
        
        # Convert company ticker to original name for logo lookup
        company_name = ticker_to_company.get(company, company)
        
        # Add revenue label at the end of the bar
        if width > 0:  # Only show label if revenue is positive
            if 0 < width < 1:  # Show 2 decimal places for numbers between 0 and 1
                revenue_text = f'{width:.2f}'
            else:  # Show integer for numbers >= 1
                revenue_text = f'{int(width):,}'
            ax.text(width + (current_x_limit * 0.01), y_pos, revenue_text,
                    va='center', ha='left', fontsize=14,
                    fontproperties=open_sans_font)
        
        # Add logo with adjusted offset calculation
        if company_name == 'PCLN' or company_name == 'BKNG':
            if frame < 2014.25:
                logo_key = 'PCLN_pre2014'
            elif frame < 2018.08:
                logo_key = 'PCLN_post2014'
            else:
                logo_key = 'BKNG'
        elif company_name == 'TRVG':
            if frame < 2013.0:
                logo_key = 'TRVG_pre2013'
            elif frame < 2023.0:
                logo_key = 'TRVG_2013_2023'
            else:
                logo_key = 'TRVG'
        elif company_name == 'Orbitz':
            logo_key = 'Orbitz1' if frame < 2005.0 else 'Orbitz'
        elif company_name == 'EXPE':
            if frame < 2010.0:
                logo_key = 'EXPE_pre2010'
            elif frame < 2012.0:
                logo_key = 'EXPE_2010_2012'
            else:
                logo_key = 'EXPE'
        elif company_name == 'TCOM':
            logo_key = 'TCOM_pre2019' if frame < 2019.75 else 'TCOM'
        elif company_name == 'TRIP':
            logo_key = 'TRIP_pre2020' if frame < 2020.0 else 'TRIP'
        elif company_name == 'SEERA':
            logo_key = 'SEERA_pre2019' if frame < 2019.25 else 'SEERA'
        elif company_name == 'LMN':
            if frame >= 2014.0 and frame < 2015.42:
                logo_key = 'LMN_2014_2015'
            else:
                logo_key = 'LMN'
        else:
            logo_key = company_name
            
        if logo_key in logos:
            image = logos[logo_key]
            settings = logo_settings.get(logo_key, logo_settings.get(company_name, {'zoom': 0.12, 'offset': 100}))
            zoom = settings['zoom']
            pixel_offset = settings['offset']
            
            # 计算目标尺寸
            target_height = int(image.shape[0] * zoom)
            target_width = int(image.shape[1] * zoom)
            
            # 预处理图像到目标尺寸
            processed_image = preprocess_logo(image, target_size=(target_width, target_height))
            
            # Use figure width in pixels for offset calculation
            fig_width_inches = fig.get_size_inches()[0]
            dpi = fig.dpi
            fig_width_pixels = fig_width_inches * dpi
            
            # Scale the offset based on the DPI ratio
            dpi_scale = OUTPUT_DPI / 100.0
            adjusted_offset = pixel_offset * (300.0 / OUTPUT_DPI)  # 根据300 DPI标准化偏移量
            data_offset = (adjusted_offset / fig_width_pixels) * current_x_limit
            
            # Create high quality OffsetImage with improved settings
            imagebox = OffsetImage(processed_image, zoom=1.0)
            
            # 设置更高质量的渲染参数
            imagebox.image.set_interpolation('lanczos')
            imagebox.image.set_resample(True)
            imagebox.image.set_filterrad(12.0)  # 增加滤波半径
            
            # 创建高质量的标注框
            ab = AnnotationBbox(
                imagebox,
                (width + data_offset, y_pos),
                frameon=False,
                box_alignment=(0.5, 0.5),
                pad=0,
                bboxprops=dict(alpha=0)
            )
            ax.add_artist(ab)
    
    # Set y-ticks with ticker mapping
    ax.set_yticks(all_positions)
    labels = [''] * num_bars
    
    companies_with_revenue = []
    positions_with_revenue = []
    for i, (company, revenue) in enumerate(zip(top_companies['Company'], top_companies['Revenue'])):
        if not ((company == 'LMN' and (revenue < 0 or abs(revenue) < 0.009)) or abs(revenue) < 0.01):
            # Apply ticker mapping if available
            display_name = company_to_ticker.get(company, company)
            companies_with_revenue.append(display_name)
            positions_with_revenue.append(all_positions[i])
    
    ax.set_yticks(positions_with_revenue)
    ax.set_yticklabels(companies_with_revenue, fontsize=14, fontproperties=open_sans_font)
    
    # Add grid lines with fixed interval for small values
    if current_x_limit == 400:
        interval = 50  # Fixed interval when using fixed scale
    else:
        # Dynamic interval based on current limit
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
    # TODO: 对于这个data-viz和create-video，发现创建完视频过后，如果对视频降速，会出现比较chunky的情况，需要对这个情况进行修改，能够通过增多插值数量的方法和增大fps的方法或者一些你觉得可行的方法，一方面稍微让视频的时长增大一些，另一方面，需要让它在降速过后仍然保持流畅而非chunky的样子
    # FIXME: 需要调整一些时间上的对应问题，
    # 对于matplotlib为什么渲染时间这么慢，是由于创建frame的时候，在每一帧处理的时候并不是一个连续的情况，而是一帧一帧生成的，是不是会导致这样的情况，
    
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
    
    # Save the frame with appropriate quality settings
    frame_number = int((frame - 1997) * FRAMES_PER_YEAR)
    frame_path = os.path.join(frames_dir, f'frame_{frame_number:04d}.png')
    if args.publish:
        plt.savefig(
            frame_path,
            dpi=OUTPUT_DPI,
            bbox_inches=None,
            pad_inches=0.1,
            metadata={'Software': 'matplotlib'},
            pil_kwargs={
                'quality': 100,
                'optimize': True,
                'progressive': True,
                'subsampling': 0  # 禁用色度子采样
            }
        )
    else:
        plt.savefig(frame_path, dpi=OUTPUT_DPI, bbox_inches=None)
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
    year_index = last_frame // FRAMES_PER_YEAR  # Since frame numbers are year*FRAMES_PER_YEAR
    if year_index < len(unique_years):
        unique_years = unique_years[year_index:]
        print(f"Continuing from year {unique_years[0]:.2f}")
    else:
        print("All frames have been generated!")
        unique_years = []

for i, year in enumerate(unique_years):
    frame_number = int((year - 1997) * FRAMES_PER_YEAR)
    frame_path = os.path.join(frames_dir, f'frame_{frame_number:04d}.png')
    
    # Skip if frame already exists
    if os.path.exists(frame_path):
        print(f"\rSkipping existing frame {frame_number:04d} (Year: {year:.2f})", end="", flush=True)
        continue
        
    try:
        print(f"\rGenerating frame {frame_number:04d}/{(unique_years[-1]-1997)*FRAMES_PER_YEAR:.0f} (Year: {year:.2f})", end="", flush=True)
        create_frame(year)
    except Exception as e:
        print(f"\nError generating frame for year {year:.2f}: {e}")
        continue

print("\n\nAll frames generated successfully!")
print(f"Frames are saved in: {frames_dir}")