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
import sys
import multiprocessing as mp
from functools import partial
from tqdm import tqdm
import matplotlib
matplotlib.use('Agg')  # Use Agg backend for better performance

'''
this scirtp is used to generate bar chart race visualization
'''
#git add .
#git commit -m "update"
#git push
# how to setup a profe

# Add argument parser
parser = argparse.ArgumentParser(description='Generate bar chart race visualization')
parser.add_argument('--publish', action='store_true', help='Generate high quality version for publishing')
parser.add_argument('--quarters-only', action='store_true', help='Only generate frames for each quarter (only works with --publish)')
parser.add_argument('--frames-per-year', type=int, help='Number of frames to generate per year in publish mode (default: 192)')
args = parser.parse_args()

# Set quality parameters based on mode
if args.publish:
    if args.quarters_only:
        FRAMES_PER_YEAR = 4  # Fixed 4 frames for quarters only mode
    else:
        FRAMES_PER_YEAR = args.frames_per_year if args.frames_per_year else 192  # Use custom frames per year or default to 192
    OUTPUT_DPI = 108      # Further reduced from 144 to 108
    FIGURE_SIZE = (19.2, 10.8)  # 1080p size
    LOGO_DPI = 216       # Reduced from 300 to 216 for logos
else:
    if args.quarters_only:
        print("\n警告: --quarters-only 参数只在 --publish 模式下生效")
    if args.frames_per_year:
        print("\n警告: --frames-per-year 参数只在 --publish 模式下生效")
    FRAMES_PER_YEAR = 48   # Preview frames
    OUTPUT_DPI = 72      # Keep preview DPI at 72
    FIGURE_SIZE = (16, 9)  # Smaller size for preview
    LOGO_DPI = 144      # Keep preview logo DPI at 144

def optimize_figure_for_performance():
    """优化matplotlib的性能设置"""
    plt.rcParams['path.simplify'] = True
    plt.rcParams['path.simplify_threshold'] = 1.0
    plt.rcParams['agg.path.chunksize'] = 10000
    plt.rcParams['figure.dpi'] = OUTPUT_DPI
    plt.rcParams['savefig.dpi'] = OUTPUT_DPI

# Cache for preprocessed logos
logo_cache = {}

def preprocess_logo(image_array, target_size=None, upscale_factor=4):
    """优化的logo预处理函数"""
    cache_key = f"{hash(str(image_array.tobytes()))}-{str(target_size)}"
    if cache_key in logo_cache:
        return logo_cache[cache_key]

    if isinstance(image_array, np.ndarray):
        if image_array.dtype == np.float32:
            image_array = (image_array * 255).astype(np.uint8)
        image = Image.fromarray(image_array)
    else:
        image = image_array

    original_mode = image.mode

    if target_size:
        w, h = target_size
        if args.publish:
            large_size = (w * 2, h * 2)  # Reduced upscale factor
            image = image.resize(large_size, Image.Resampling.LANCZOS)

            if original_mode == 'RGBA':
                r, g, b, a = image.split()
                rgb = Image.merge('RGB', (r, g, b))
                enhancer = ImageEnhance.Sharpness(rgb)
                rgb = enhancer.enhance(1.2)
                r, g, b = rgb.split()
                image = Image.merge('RGBA', (r, g, b, a))
            else:
                enhancer = ImageEnhance.Sharpness(image)
                image = enhancer.enhance(1.2)

            image = image.resize(target_size, Image.Resampling.LANCZOS)
        else:
            image = image.resize(target_size, Image.Resampling.LANCZOS)

    result = np.array(image)
    logo_cache[cache_key] = result
    return result

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
data = pd.read_csv('Animated Bubble Chart Online Travel Revenue.csv')
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
    def convert_to_decimal_year(year_quarter):
        year = float(year_quarter.split("'")[0])
        quarter = int(year_quarter.split("Q")[1])
        # Convert quarter to decimal (Q1->0.0, Q2->0.25, Q3->0.5, Q4->0.75)
        quarter_decimal = (quarter - 1) * 0.25
        return year + quarter_decimal
    
    # Extract year and quarter information
    data['Year'] = data.iloc[:, 0].apply(convert_to_decimal_year)
    
    # Convert all revenue columns to numeric, with better error handling
    for col in data.columns[1:-1]:  # Skip the original year column and the new Year column
        # First replace empty strings and 'nan' with NaN
        data[col] = data[col].replace('', np.nan).replace('nan', np.nan)
        # Then convert to numeric
        data[col] = pd.to_numeric(data[col].apply(lambda x: str(x).replace('$', '').replace(',', '') if pd.notnull(x) else np.nan), errors='coerce')
    
    print("\nDebug: Data after numeric conversion:")
    print(data.head())
    print("\nDebug: ABNB column after conversion:")
    print(data['ABNB'].head())
    
    # For years before 2024, keep all quarters
    pre_2024 = data[data['Year'] < 2024.0].copy()
    
    # For 2024, keep Q1 and Q3
    year_2024 = data[(data['Year'] >= 2024.0) & (data['Year'] < 2025.0)].copy()
    year_2024 = year_2024[year_2024['Year'].isin([2024.0, 2024.5])]  # Keep only Q1 (0.0) and Q3 (0.5)
    
    print("\nDebug: 2024 data:")
    print(year_2024)
    
    # Combine the data
    processed_data = pd.concat([pre_2024, year_2024])
    
    # For 2024 Q3, set the year to 2025 for interpolation
    processed_data.loc[processed_data['Year'] == 2024.5, 'Year'] = 2025.0
    
    # Drop the original year column
    processed_data = processed_data.drop(columns=[processed_data.columns[0]])
    
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
    """优化的数据插值函数"""
    all_interpolated = []
    companies = [col for col in data.columns if col != 'Year']
    print(f"\nFound {len(companies)} companies to process:")
    print(companies)
    
    # First, determine the overall time range
    min_year = data['Year'].min()
    max_year = data['Year'].max()
    print(f"\nOverall year range: {min_year} to {max_year}")
    
    # Create unified time points for all companies
    if args.publish and args.quarters_only:
        # For quarters-only mode, use exact quarter points
        quarters_before_2024 = np.arange(min_year, 2024.0, 0.25)
        quarters_2024_2025 = np.array([2024.0, 2024.25, 2024.5, 2024.75, 2025.0])
        unified_years = np.concatenate([quarters_before_2024, quarters_2024_2025])
    else:
        # For normal mode, create more granular points between quarters
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
            
            if len(company_data) < 2:
                print(f"Skipping {company} - insufficient data points")
                continue
            
            # 对数据按年份排序
            company_data = company_data.sort_values('Year')
            
            # 为相同的值添加微小的变化以确保动画效果
            processed_data = company_data.copy()
            prev_value = None
            same_value_count = 0
            
            for idx, row in processed_data.iterrows():
                current_value = row['Revenue']
                if prev_value is not None and abs(current_value - prev_value) < 0.01:
                    same_value_count += 1
                    # 添加微小的波动 (±0.1%)
                    variation = current_value * 0.001 * np.sin(same_value_count * np.pi / 2)
                    processed_data.loc[idx, 'Revenue'] = current_value + variation
                else:
                    same_value_count = 0
                prev_value = current_value
            
            # 使用CubicSpline进行插值，设置边界条件使得插值更平滑
            from scipy.interpolate import CubicSpline
            cs = CubicSpline(processed_data['Year'], processed_data['Revenue'], bc_type='natural')
            
            # 创建插值结果DataFrame
            company_min_year = company_data['Year'].min()
            company_max_year = company_data['Year'].max()
            mask = (unified_years >= company_min_year) & (unified_years <= company_max_year)
            company_years = unified_years[mask]
            
            company_interp = pd.DataFrame()
            company_interp['Year'] = company_years
            company_interp['Company'] = company
            
            # 生成插值结果
            interpolated_values = cs(company_years)
            
            # 对插值结果添加小幅波动，确保没有完全静止的部分
            for i in range(len(interpolated_values)):
                year = company_years[i]
                base_value = interpolated_values[i]
                # 使用正弦函数生成周期性的小波动
                wave = np.sin(year * 2 * np.pi) * base_value * 0.001
                interpolated_values[i] = base_value + wave
            
            company_interp['Revenue'] = interpolated_values
            
            # 在季度点上使用接近原始数据的值，但保留一些微小变化
            if args.publish and args.quarters_only:
                for _, row in company_data.iterrows():
                    year = row['Year']
                    revenue = row['Revenue']
                    # 在季度点上使用接近原始数据的值
                    mask = np.abs(company_years - year) < 1e-10
                    if any(mask):
                        # 添加很小的随机变化 (±0.05%)
                        variation = revenue * 0.0005 * np.sin(year * np.pi)
                        company_interp.loc[mask, 'Revenue'] = revenue + variation
            
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
    'Orbitz': {'zoom': 0.30, 'offset': 130},
    'Orbitz1': {'zoom': 0.16, 'offset': 150},
    "Travelocity": {'zoom': 0.20, 'offset': 150},
    'ABNB': {'zoom': 0.25, 'offset': 150},
    'BKNG': {'zoom': 0.25, 'offset': 130},
    'PCLN_pre2014': {'zoom': 0.25, 'offset': 135},
    'PCLN_post2014': {'zoom': 0.25, 'offset': 135 },
    'DESP': {'zoom': 0.28, 'offset': 120},
    'EASEMYTRIP': {'zoom': 0.34, 'offset': 100},
    'EDR': {'zoom': 0.25, 'offset': 130},
    'EXPE': {'zoom': 0.3, 'offset': 175},
    'EXPE_pre2010': {'zoom': 0.18 , 'offset': 175},
    'EXPE_2010_2012': {'zoom': 0.3, 'offset': 175},
    'LMN': {'zoom': 0.45, 'offset': 140},
    'OWW': {'zoom': 0.29, 'offset': 50},
    'SEERA': {'zoom': 0.20, 'offset': 125},
    'SEERA_pre2019': {'zoom': 0.25, 'offset': 125},
    'TCOM': {'zoom': 0.30, 'offset': 130},
    'TCOM_pre2019': {'zoom': 0.25, 'offset': 130},
    'TRIP': {'zoom': 0.26, 'offset': 130},
    'TRIP_pre2020': {'zoom': 0.23, 'offset': 125},
    'TRVG': {'zoom': 0.27, 'offset': 130},
    'TRVG_pre2013': {'zoom': 0.31, 'offset': 130},
    'TRVG_2013_2023': {'zoom': 0.31, 'offset': 130},
    'WEB': {'zoom': 0.14, 'offset': 150},
    'Webjet': {'zoom': 0.23, 'offset': 125},
    'WBJ': {'zoom': 0.14, 'offset': 150},
    'Yatra': {'zoom': 0.23, 'offset': 100},
    'YTRA': {'zoom': 0.23, 'offset': 100},
    'MMYT': {'zoom': 0.25, 'offset': 130},
    'IXIGO': {'zoom': 0.26, 'offset': 120},
    'Ixigo': {'zoom': 0.26, 'offset': 120 },
    'LMN_2014_2015': {'zoom': 0.27, 'offset': 130},
    'EaseMyTrip': {'zoom': 0.26, 'offset': 120},
    
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
    """优化的帧创建函数"""
    optimize_figure_for_performance()
    
    # Create figure with optimized settings
    fig = plt.figure(figsize=FIGURE_SIZE)
    gs = fig.add_gridspec(2, 1, height_ratios=[0.3, 4], hspace=0.2,
                         top=0.98, bottom=0.12)
    ax_timeline = fig.add_subplot(gs[0])
    ax = fig.add_subplot(gs[1])

    # Use vectorized operations for data filtering
    mask = (interp_data['Year'] >= frame - 0.01) & (interp_data['Year'] <= frame + 0.01)
    yearly_data = interp_data[mask].copy()

    if len(yearly_data) == 0:
        mask = (interp_data['Year'] >= frame - 0.02) & (interp_data['Year'] <= frame + 0.02)
        yearly_data = interp_data[mask].copy()

    # Filter companies based on time restrictions
    filtered_companies = []
    for company in selected_companies:
        if company == 'Travelocity' and frame > 2002.25:
            continue
        if company == 'Travelocity' and frame < 2000.25:
            continue
        if company == 'DESP' and frame < 2017.45:
            continue
        # IPO date restrictions
        if company == 'BKNG' and frame < 1999.17:  # Mar 1999
            continue
        if company == 'EXPE' and frame < 1999.83:  # Nov 1999
            continue
        if company == 'TCOM' and frame < 2003.92:  # Dec 2003
            continue
        if company == 'Orbitz' and frame < 2003.92:  # Dec 2003
            continue
        if company == 'Orbitz' and frame > 2004.92 and frame < 2007.55:
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
        if company == 'EaseMyTrip' and frame < 2021.17: 
            continue# Mar 2021
        if company == 'IXIGO' and frame < 2024.42:  # Jun 2024
            continue
        if company == 'Ixigo' and frame < 2024.42:
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

    # Optimize sorting and data processing
    if len(yearly_data) > len(yearly_data['Company'].unique()):
        yearly_data['time_diff'] = abs(yearly_data['Year'] - frame)
        yearly_data = yearly_data.sort_values('time_diff').groupby('Company', as_index=False).first()
        yearly_data = yearly_data.drop('time_diff', axis=1)

    sorted_data = yearly_data.sort_values('Revenue', ascending=False)
    
    available_companies = len(sorted_data)
    top_companies = sorted_data
    
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
            dpi_scale = LOGO_DPI / OUTPUT_DPI
            adjusted_offset = pixel_offset * (dpi_scale * 0.8)  # 略微减小整体大小
            data_offset = (adjusted_offset / fig_width_pixels) * current_x_limit
            
            # Create high quality OffsetImage with improved settings
            imagebox = OffsetImage(processed_image, zoom=zoom)
            
            # 设置更高质量的渲染参数
            imagebox.image.set_interpolation('lanczos')
            imagebox.image.set_resample(True)
            imagebox.image.set_filterrad(4.0)  # 使用更合适的滤波半径
            
            # 使用抗锯齿设置
            plt.rcParams['agg.path.chunksize'] = 20000
            plt.rcParams['path.simplify'] = True
            plt.rcParams['path.simplify_threshold'] = 1.0
            
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
    
    # Optimize image saving
    frame_number = int((frame - 1999) * FRAMES_PER_YEAR)  # 修改基准年份为1999
    frame_path = os.path.join(frames_dir, f'frame_{frame_number:04d}.png')
    
    plt.savefig(
        frame_path,
        dpi=OUTPUT_DPI,
        bbox_inches=None,
        pad_inches=0.1,
        metadata={'Software': 'matplotlib'},
        pil_kwargs={
            'quality': 85 if args.publish else 75,
            'optimize': True,
            'progressive': True,
            'subsampling': 0
        }
    )
    plt.close(fig)
    return frame_path

def get_existing_frames(frames_dir):
    """获取已经存在的帧文件信息"""
    if not os.path.exists(frames_dir):
        print("\n未找到frames目录，将从头开始渲染")
        return set()
        
    frames = glob.glob(os.path.join(frames_dir, 'frame_*.png'))
    existing_frames = set()
    
    for frame in frames:
        try:
            number = int(frame.split('frame_')[-1].split('.png')[0])
            existing_frames.add(number)
        except:
            continue
            
    return existing_frames

def get_frame_info(frames_dir):
    """分析现有帧和缺失帧的信息"""
    existing_frames = get_existing_frames(frames_dir)
    
    if not existing_frames:
        print("\n没有找到任何已渲染的帧，将从头开始渲染")
        return existing_frames, []
    
    min_frame = min(existing_frames)
    max_frame = max(existing_frames)
    expected_frames = set(range(min_frame, max_frame + 1))
    missing_frames = sorted(list(expected_frames - existing_frames))
    
    print(f"\n已渲染帧数量: {len(existing_frames)}")
    print(f"帧范围: {min_frame} - {max_frame}")
    
    if missing_frames:
        print(f"发现 {len(missing_frames)} 个缺失的帧")
        print(f"缺失帧范围: {min(missing_frames)} - {max(missing_frames)}")
    else:
        print("在现有范围内没有缺失的帧")
    
    return existing_frames, missing_frames

def process_frame_range(frame_range):
    """按顺序处理一组帧"""
    existing_frames = get_existing_frames(frames_dir)
    
    # 创建进度条
    pbar = tqdm(sorted(frame_range), desc="渲染进度", unit="帧")
    
    for year in pbar:  # 使用tqdm进度条
        # 在quarters-only模式下，只处理季度时间点
        if args.publish and args.quarters_only:
            # 检查是否为季度时间点（年份的小数部分应该是0.0, 0.25, 0.5, 0.75）
            decimal_part = year - int(year)
            if not any(abs(decimal_part - q) < 0.01 for q in [0.0, 0.25, 0.5, 0.75]):
                continue
        
        frame_number = int((year - 1999) * FRAMES_PER_YEAR)
        frame_path = os.path.join(frames_dir, f'frame_{frame_number:04d}.png')
        
        # 如果帧已经存在，跳过
        if frame_number in existing_frames:
            continue
            
        try:
            pbar.set_postfix({"年份": f"{year:.2f}"})  # 显示当前处理的年份
            create_frame(year)
        except Exception as e:
            print(f"\n生成 {year:.2f} 年的帧时出错: {e}")
            continue

def main():
    """主函数，使用多进程处理帧生成"""
    if args.publish and args.quarters_only:
        print("\n使用季度模式，将只生成每个季度的帧")
    
    # 获取现有帧和缺失帧信息
    existing_frames, missing_frames = get_frame_info(frames_dir)
    
    # 获取需要处理的年份范围
    unique_years = np.unique(interp_data['Year'])
    unique_years = unique_years[unique_years >= 1999.0]  # 修改基准年份为1999
    
    if missing_frames:
        # 如果有缺失帧，优先处理缺失的部分
        missing_years = set([1999 + frame/FRAMES_PER_YEAR for frame in missing_frames])  # 修改基准年份为1999
        years_to_process = sorted(list(missing_years))
        print("\n将优先处理缺失的帧...")
    else:
        # 如果没有缺失帧，检查是否需要继续渲染新的帧
        if existing_frames:
            last_frame = max(existing_frames)
            last_year = 1999 + last_frame/FRAMES_PER_YEAR  # 修改基准年份为1999
            years_to_process = sorted(list(unique_years[unique_years > last_year]))
            if years_to_process:
                print(f"\n将从 {years_to_process[0]:.2f} 年继续渲染...")
            else:
                print("\n所有帧都已生成完毕！")
                return
        else:
            years_to_process = sorted(list(unique_years))
            print("\n将从头开始渲染所有帧...")
    
    # 获取CPU核心数
    num_cores = mp.cpu_count()
    pool_size = max(1, num_cores - 1)  # 保留一个核心给系统
    
    # 将年份划分为多个子集，尽量保持连续性
    chunk_size = max(1, len(years_to_process) // pool_size)
    chunks = [years_to_process[i:i + chunk_size] for i in range(0, len(years_to_process), chunk_size)]
    
    print(f"\n将使用 {len(chunks)} 个进程并行渲染")
    print(f"总计需要渲染 {len(years_to_process)} 个帧")
    
    # 创建总进度条
    with tqdm(total=len(years_to_process), desc="总体进度", unit="帧") as pbar:
        # 创建进程池并行处理
        with mp.Pool(pool_size) as pool:
            # 使用imap来获取实时进度
            for _ in pool.imap_unordered(process_frame_range, chunks):
                pbar.update(chunk_size)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate bar chart race visualization')
    parser.add_argument('--publish', action='store_true', help='Generate high quality version for publishing')
    parser.add_argument('--quarters-only', action='store_true', help='Only generate frames for each quarter (only works with --publish)')
    parser.add_argument('--frames-per-year', type=int, help='Number of frames to generate per year in publish mode (default: 192)')
    args = parser.parse_args()
    
    # ... rest of your initialization code ...
    
    print("\n开始生成帧...")
    main()
    print("\n\n所有帧生成完成！")
    print(f"帧文件保存在: {frames_dir}")