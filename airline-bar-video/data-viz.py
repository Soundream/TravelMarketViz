import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from matplotlib.animation import FuncAnimation
import matplotlib.colors as mcolors
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
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
import warnings
import matplotlib.font_manager as fm
matplotlib.use('Agg')  # Use Agg backend for better performance

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
    LOGO_DPI = 300       # Increased from 216 to 300 for sharper logos
else:
    if args.quarters_only:
        print("\n警告: --quarters-only 参数只在 --publish 模式下生效")
    if args.frames_per_year:
        print("\n警告: --frames-per-year 参数只在 --publish 模式下生效")
    FRAMES_PER_YEAR = 48   # Preview frames
    OUTPUT_DPI = 72      # Keep preview DPI at 72
    FIGURE_SIZE = (16, 9)  # Smaller size for preview
    LOGO_DPI = 200      # Increased from 144 to 200 for sharper preview logos

# Create required directories
logos_dir = 'logos'
output_dir = 'output'
frames_dir = os.path.join(output_dir, 'frames')
for directory in [logos_dir, output_dir, frames_dir]:
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

# Global variable for frame indices
frame_indices = []

# Load the data from CSV
print("Loading data...")
df = pd.read_csv('airlines_original.csv')

# Print all airline data from the CSV
print("\nAll airline data from CSV:")
print(df.iloc[7:])

# Process metadata
metadata = df.iloc[:7].copy()  # First 7 rows contain metadata
revenue_data = df.iloc[7:].copy()  # Revenue data starts from row 8

# Set proper index for metadata
metadata.set_index(metadata.columns[0], inplace=True)

# Print raw revenue data before conversion
print("\nRaw revenue data before conversion:")
print(revenue_data.head())

# Convert revenue columns by removing ' M' suffix, commas, and converting to float
for col in revenue_data.columns[1:]:  # Skip the first column which contains row labels
    revenue_data[col] = pd.to_numeric(revenue_data[col].str.replace(',', '').str.replace(' M', ''), errors='coerce')

# Create a color mapping for regions
region_colors = {
    'North America': '#40E0D0',  # 鲜艳的绿松石色
    'Europe': '#4169E1',         # 鲜艳的蓝色
    'Asia Pacific': '#FF4B4B',   # 鲜艳的红色
    'Latin America': '#32CD32',  # 鲜艳的绿色
    'China': '#FF4B4B',          # Purple
    'Middle East': '#DEB887',    # 鲜艳的棕色
    'Russia': '#FF4B4B',         # Gray
    'Turkey': '#DEB887'          # Dark Blue
}

# Set index for revenue data
revenue_data.set_index(revenue_data.columns[0], inplace=True)

# Get the quarters from the revenue data index
quarters = revenue_data.index.tolist()

# Define constants for visualization
MAX_BARS = 15  # Maximum number of bars to show
BAR_HEIGHT = 0.8  # Height of each bar
BAR_PADDING = 0.2  # Padding between bars
TOTAL_BAR_HEIGHT = BAR_HEIGHT + BAR_PADDING  # Total height including padding
TICK_FONT_SIZE = 10
LABEL_FONT_SIZE = 10
VALUE_FONT_SIZE = 10

def optimize_figure_for_performance():
    """优化matplotlib的性能设置"""
    plt.rcParams['path.simplify'] = True
    plt.rcParams['path.simplify_threshold'] = 1.0
    plt.rcParams['agg.path.chunksize'] = 10000
    plt.rcParams['figure.dpi'] = OUTPUT_DPI
    plt.rcParams['savefig.dpi'] = OUTPUT_DPI
    plt.rcParams['savefig.bbox'] = 'standard'  # 改为standard，不使用tight
    plt.rcParams['figure.autolayout'] = False  # 关闭autolayout
    plt.rcParams['figure.constrained_layout.use'] = False  # 关闭constrained_layout
    plt.rcParams['savefig.format'] = 'png'
    plt.rcParams['savefig.pad_inches'] = 0.1  # 固定的padding
    plt.rcParams['figure.figsize'] = FIGURE_SIZE
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Helvetica', 'sans-serif']
    plt.rcParams['axes.facecolor'] = 'white'
    plt.rcParams['axes.grid'] = False
    plt.rcParams['axes.edgecolor'] = '#dddddd'
    plt.rcParams['axes.linewidth'] = 0.8
    plt.rcParams['grid.color'] = '#dddddd'
    plt.rcParams['grid.linestyle'] = '--'
    plt.rcParams['grid.linewidth'] = 0.5

# Cache for preprocessed logos
logo_cache = {}

def preprocess_logo(image_array, target_size=None, upscale_factor=4):
    """优化的logo预处理函数"""
    cache_key = f"{hash(str(image_array.tobytes()))}-{str(target_size)}"
    if cache_key in logo_cache:
        print(f"Using cached logo for size {target_size}")
        return logo_cache[cache_key]

    try:
        if isinstance(image_array, np.ndarray):
            if image_array.dtype == np.float32:
                image_array = (image_array * 255).astype(np.uint8)
            image = Image.fromarray(image_array)
        else:
            image = image_array

        original_mode = image.mode
        original_size = image.size
        print(f"Original logo size: {original_size}, mode: {original_mode}")

        if target_size:
            w, h = target_size
            if args.publish:
                # Use a larger upscale for better quality
                large_size = (w * 3, h * 3)  # Increased upscale factor from 2 to 3
                print(f"Resizing to intermediate size: {large_size} using LANCZOS")
                image = image.resize(large_size, Image.Resampling.LANCZOS)

                # Apply stronger sharpening and contrast enhancement
                if original_mode == 'RGBA':
                    r, g, b, a = image.split()
                    rgb = Image.merge('RGB', (r, g, b))
                    
                    # Apply stronger sharpening
                    enhancer = ImageEnhance.Sharpness(rgb)
                    rgb = enhancer.enhance(1.8)  # Increased from 1.5 to 1.8
                    
                    # Add contrast enhancement
                    contrast = ImageEnhance.Contrast(rgb)
                    rgb = contrast.enhance(1.3)  # Increased from 1.2 to 1.3
                    
                    # Restore alpha channel
                    r, g, b = rgb.split()
                    image = Image.merge('RGBA', (r, g, b, a))
                else:
                    # Apply stronger sharpening
                    enhancer = ImageEnhance.Sharpness(image)
                    image = enhancer.enhance(1.8)  # Increased from 1.5 to 1.8
                    
                    # Add contrast enhancement
                    contrast = ImageEnhance.Contrast(image)
                    image = contrast.enhance(1.3)  # Increased from 1.2 to 1.3

                # Apply unsharp mask filter for additional sharpness
                print("Applying UnsharpMask filter")
                image = image.filter(ImageFilter.UnsharpMask(radius=1.2, percent=180, threshold=3))
                
                # Resize to target size with high-quality resampling
                print(f"Final resize to target size: {target_size} using LANCZOS")
                image = image.resize(target_size, Image.Resampling.LANCZOS)
            else:
                # Improved processing for preview mode too
                large_size = (w * 2, h * 2)
                print(f"Preview mode: Resizing to intermediate size: {large_size}")
                image = image.resize(large_size, Image.Resampling.LANCZOS)
                
                # Apply moderate sharpening and contrast
                if original_mode == 'RGBA':
                    r, g, b, a = image.split()
                    rgb = Image.merge('RGB', (r, g, b))
                    enhancer = ImageEnhance.Sharpness(rgb)
                    rgb = enhancer.enhance(1.5)  # Increased from 1.3 to 1.5
                    contrast = ImageEnhance.Contrast(rgb)
                    rgb = contrast.enhance(1.2)  # Increased from 1.1 to 1.2
                    r, g, b = rgb.split()
                    image = Image.merge('RGBA', (r, g, b, a))
                else:
                    enhancer = ImageEnhance.Sharpness(image)
                    image = enhancer.enhance(1.5)  # Increased from 1.3 to 1.5
                    contrast = ImageEnhance.Contrast(image)
                    image = contrast.enhance(1.2)  # Increased from 1.1 to 1.2
                    
                image = image.filter(ImageFilter.UnsharpMask(radius=1.0, percent=150, threshold=3))
                image = image.resize(target_size, Image.Resampling.LANCZOS)

        result = np.array(image)
        print(f"Processed logo array shape: {result.shape}")
        logo_cache[cache_key] = result
        return result
        
    except Exception as e:
        print(f"Error in preprocess_logo: {e}")
        import traceback
        traceback.print_exc()
        # If preprocessing fails, return the original image
        return image_array

def format_revenue(value, pos):
    """Format revenue values with B for billions and M for millions"""
    if value >= 1000:
        return f'${value/1000:.1f}B'
    return f'${value:.0f}M'

def parse_quarter(quarter_str):
    """Parse quarter string into (year, quarter)"""
    year, quarter = quarter_str.split("'")
    year = int(year)  # Year is already in 4-digit format
    quarter = int(quarter[1])  # Extract quarter number
    return year, quarter

def is_before_may_2004(year, quarter):
    """Helper function to check if date is before May 2004"""
    if year < 2004:
        return True
    elif year == 2004:
        return quarter <= 1  # Q1 and earlier are before May
    return False

# Create a mapping for company logos
logo_mapping = {
    "easyJet": [{"start_year": 1999, "end_year": 9999, "file": "logos/easyJet-1999-now.jpg"}],
    "Air France-KLM": [
        {"start_year": 1999, "end_year": 2004, "file": "logos/klm-1999-now.png"},
        {"start_year": 2004, "end_year": 9999, "file": "logos/Air-France-KLM-Holding-Logo.png"}
    ],
    "American Airlines": [
        {"start_year": 1967, "end_year": 2013, "file": "logos/american-airlines-1967-2013.jpg"},
        {"start_year": 2013, "end_year": 9999, "file": "logos/american-airlines-2013-now.jpg"}
    ],
    "Delta Air Lines": [
        {"start_year": 2000, "end_year": 2007, "file": "logos/delta-air-lines-2000-2007.png"},
        {"start_year": 2007, "end_year": 9999, "file": "logos/delta-air-lines-2007-now.jpg"}
    ],
    "Southwest Airlines": [
        {"start_year": 1989, "end_year": 2014, "file": "logos/southwest-airlines-1989-2014.png"},
        {"start_year": 2014, "end_year": 9999, "file": "logos/southwest-airlines-2014-now.png"}
    ],
    "United Airlines": [
        {"start_year": 1998, "end_year": 2010, "file": "logos/united-airlines-1998-2010.jpg"},
        {"start_year": 2010, "end_year": 9999, "file": "logos/united-airlines-2010-now.jpg"}
    ],
    "Alaska Air": [
        {"start_year": 1972, "end_year": 2014, "file": "logos/alaska-air-1972-2014.png"},
        {"start_year": 2014, "end_year": 2016, "file": "logos/alaska-air-2014-2016.png"},
        {"start_year": 2016, "end_year": 9999, "file": "logos/alaska-air-2016-now.jpg"}
    ],
    "Finnair": [
        {"start_year": 1999, "end_year": 2010, "file": "logos/Finnair-1999-2010.jpg"},
        {"start_year": 2010, "end_year": 9999, "file": "logos/Finnair-2010-now.jpg"}
    ],
    "Deutsche Lufthansa": [
        {"start_year": 1999, "end_year": 2018, "file": "logos/Deutsche Lufthansa-1999-2018.png"},
        {"start_year": 2018, "end_year": 9999, "file": "logos/Deutsche Lufthansa-2018-now.jpg"}
    ],
    "Singapore Airlines": [{"start_year": 1999, "end_year": 9999, "file": "logos/Singapore Airlines-1999-now.jpg"}],
    "Qantas Airways": [{"start_year": 1999, "end_year": 9999, "file": "logos/Qantas Airways-1999-now.jpg"}],
    "Cathay Pacific": [{"start_year": 1999, "end_year": 9999, "file": "logos/Cathay Pacific-1999-now.png"}],
    "LATAM Airlines": [
        {"start_year": 1999, "end_year": 2016, "file": "logos/LATAM Airlines-1999-2016.png"},
        {"start_year": 2016, "end_year": 9999, "file": "logos/LATAM Airlines-2016-now.jpg"}
    ],
    "Air China": [{"start_year": 1999, "end_year": 9999, "file": "logos/Air China-1999-now.png"}],
    "China Eastern": [{"start_year": 1999, "end_year": 9999, "file": "logos/China Eastern-1999-now.jpg"}],
    "China Southern": [{"start_year": 1999, "end_year": 9999, "file": "logos/China Southern-1999-now.jpg"}],
    "Hainan Airlines": [
        {"start_year": 1999, "end_year": 2004, "file": "logos/Hainan Airlines-1999-2004.png"},
        {"start_year": 2004, "end_year": 9999, "file": "logos/Hainan Airlines-2004-now.jpg"}
    ],
    "Qatar Airways": [{"start_year": 1999, "end_year": 9999, "file": "logos/Qatar Airways-1999-now.jpg"}],
    "Turkish Airlines": [
        {"start_year": 1999, "end_year": 2018, "file": "logos/Turkish Airlines-1999-2018.png"},
        {"start_year": 2018, "end_year": 9999, "file": "logos/Turkish Airlines-2018-now.png"}
    ],
    "JetBlue": [{"start_year": 1999, "end_year": 9999, "file": "logos/jetBlue-1999-now.jpg"}],
    "SkyWest": [
        {"start_year": 1972, "end_year": 2001, "file": "logos/skywest-1972-2001.png"},
        {"start_year": 2001, "end_year": 2008, "file": "logos/skywest-2001-2008.png"},
        {"start_year": 2018, "end_year": 9999, "file": "logos/skywest-2018-now.jpg"}
    ],
    "Northwest Airlines": [
        {"start_year": 1989, "end_year": 2003, "file": "logos/northwest-airlines-1989-2003.png"},
        {"start_year": 2003, "end_year": 9999, "file": "logos/northwest-airlines-2003-now.jpg"}
    ],
    "TWA": [{"start_year": 1999, "end_year": 9999, "file": "logos/TWA-1999-now.png"}],
    "Air Canada": [
        {"start_year": 1995, "end_year": 2005, "file": "logos/air-canada-1995-2005.jpg"},
        {"start_year": 2005, "end_year": 9999, "file": "logos/air-canada-2005-now.png"}
    ],
    "IAG": [{"start_year": 1999, "end_year": 9999, "file": "logos/IAG-1999-now.png"}],
    "Ryanair": [
        {"start_year": 1999, "end_year": 2001, "file": "logos/Ryanair-1999-2001.png"},
        {"start_year": 2001, "end_year": 2013, "file": "logos/Ryanair-2001-2013.jpg"},
        {"start_year": 2013, "end_year": 9999, "file": "logos/Ryanair-2013-now.jpg"}
    ],
    "Aeroflot": [
        {"start_year": 1999, "end_year": 2003, "file": "logos/Aeroflot-1999-2003.jpg"},
        {"start_year": 2003, "end_year": 9999, "file": "logos/Aeroflot-2003-now.jpg"}
    ]
}

def get_logo_path(airline, year, iata_code):
    """Get the appropriate logo path based on airline name and year"""
    if airline not in logo_mapping:
        print(f"No logo mapping found for {airline} (IATA: {iata_code})")
        return None
        
    logo_versions = logo_mapping[airline]
    print(f"Found {len(logo_versions)} logo versions for {airline}")
    
    # Find the appropriate logo version for the given year
    for version in logo_versions:
        if version["start_year"] <= year <= version["end_year"]:
            logo_path = version["file"]
            print(f"Selected logo for {airline} ({year}): {logo_path}")
            
            if os.path.exists(logo_path):
                print(f"Verified logo file exists: {logo_path}")
                return logo_path
            else:
                print(f"ERROR: Logo file not found: {logo_path}")
                # 显示当前工作目录和目标文件的绝对路径，以便进行调试
                print(f"Current working directory: {os.getcwd()}")
                print(f"Absolute path would be: {os.path.abspath(logo_path)}")
                return None
    
    print(f"No logo version found for {airline} in year {year}")
    return None

# Set up font configurations
plt.rcParams['font.family'] = 'sans-serif'

# Check for Monda font, otherwise use a system sans-serif font
font_path = None
system_fonts = fm.findSystemFonts()
for font in system_fonts:
    if 'monda' in font.lower():
        font_path = font
        break

if font_path:
    monda_font = fm.FontProperties(fname=font_path)
    print(f"Found Monda font at: {font_path}")
else:
    monda_font = fm.FontProperties(family='sans-serif')
    print("Monda font not found, using default sans-serif")

def create_frame(frame_idx):
    """优化的帧创建函数，样式更接近原始data-viz"""
    optimize_figure_for_performance()
    
    # 处理分数帧索引用于插值
    frame_int = int(frame_idx)
    frame_fraction = frame_idx - frame_int
    
    # 设置严格统一的图像尺寸
    fig_width = FIGURE_SIZE[0]
    fig_height = FIGURE_SIZE[1]
    
    # 创建图形并严格设置尺寸
    fig = plt.figure(figsize=(fig_width, fig_height), facecolor='white', dpi=OUTPUT_DPI)
    
    # 确保图形尺寸是严格统一的
    fig.set_size_inches(fig_width, fig_height, forward=True)
    
    # Get the frame number for file naming
    global frame_indices
    if frame_indices and frame_idx in frame_indices:
        frame_position = frame_indices.index(frame_idx)
    else:
        # Fallback if frame_indices is not set
        frame_position = int(frame_idx * 100)
    
    # Handle fractional frame indices for interpolation
    frame_int = int(frame_idx)
    frame_fraction = frame_idx - frame_int
    
    # If this is an exact quarter frame (or we're in quarters-only mode)
    if frame_fraction == 0 or (args.publish and args.quarters_only):
        current_quarter = quarters[frame_int]
        quarter_data_main = revenue_data.loc[current_quarter]
        
        # For exact quarters, we just use the quarter data directly
        print(f"\nProcessing exact quarter frame for {current_quarter}")
        interpolated_data = quarter_data_main
    else:
        # For in-between frames, interpolate between adjacent quarters
        if frame_int < len(quarters) - 1:
            q1 = quarters[frame_int]
            q2 = quarters[frame_int + 1]
            q1_data = revenue_data.loc[q1]
            q2_data = revenue_data.loc[q2]
            
            print(f"\nProcessing interpolated frame between {q1} and {q2} (fraction: {frame_fraction:.3f})")
            
            # Create interpolated data frame
            interpolated_data = q1_data * (1 - frame_fraction) + q2_data * frame_fraction
        else:
            # Fallback for last frame
            current_quarter = quarters[frame_int]
            interpolated_data = revenue_data.loc[current_quarter]
    
    # Create figure with optimized settings
    print(f"\nCreating frame {frame_idx} with figure size {FIGURE_SIZE}, DPI {OUTPUT_DPI}")
    
    # Set consistent color for all text elements and grid lines
    text_color = '#808080'
    
    # Create a gridspec with space for timeline and bars - adjusted ratios for layout
    gs = fig.add_gridspec(2, 1, height_ratios=[0.15, 1], 
                          left=0.1, right=0.9,  # 固定左右边距
                          bottom=0.1, top=0.95,  # 固定上下边距
                          hspace=0.05)
    
    # Create axis for timeline
    ax_timeline = fig.add_subplot(gs[0])
    
    # Create main axis for bar chart
    ax = fig.add_subplot(gs[1])

    # Get data for the current quarter
    quarter_data = []
    colors = []
    labels = []
    logos = []
    logos_data = []
    
    # Get the current quarter from integer part of frame_idx
    if frame_int < len(quarters):
        current_quarter = quarters[frame_int]
    else:
        current_quarter = quarters[-1]
    
    # Parse quarter info
    year, quarter = parse_quarter(current_quarter)
    
    # If we're at an interpolated frame, adjust the quarter display
    if frame_fraction > 0:
        # Calculate the exact decimal year
        year_fraction = year + (quarter - 1) * 0.25 + frame_fraction * 0.25
        year_integer = int(year_fraction)
        month = int((year_fraction - year_integer) * 12) + 1
        quarter_display = f"{year_integer} {month:02d}"
    else:
        quarter_display = f"{year} Q{quarter}"
    
    print(f"\nProcessing frame for {quarter_display}")
    
    # Iterate through airlines
    for airline in interpolated_data.index:
        value = interpolated_data[airline]
        if pd.notna(value) and value > 0:  # Only include positive non-null values
            quarter_data.append(value)
            region = metadata.loc['Region', airline]
            colors.append(region_colors.get(region, '#808080'))  # Default to gray if region not found
            
            # Special handling for Air France-KLM label
            if airline == "Air France-KLM":
                if is_before_may_2004(year, quarter):
                    labels.append("KL")
                else:
                    # Use IATA code instead of full name
                    iata_code = metadata.loc['IATA', airline]
                    labels.append(iata_code if pd.notna(iata_code) else airline[:3])
            else:
                # Use IATA code instead of full name
                iata_code = metadata.loc['IATA', airline]
                labels.append(iata_code if pd.notna(iata_code) else airline[:3])
            
            # Get logo path using IATA code
            logo_path = get_logo_path(airline, year, iata_code)
            logos.append(logo_path)
    
    # Check if we have any valid data
    if not quarter_data:
        print(f"\nWarning: No valid data for quarter {current_quarter}")
        frame_path = os.path.join(frames_dir, f'frame_{frame_position:04d}.png')
        ax.text(0.5, 0.5, f'No data available for {current_quarter}',
                ha='center', va='center', transform=ax.transAxes)
        plt.savefig(frame_path, dpi=OUTPUT_DPI, bbox_inches=None, pad_inches=0.1, facecolor=fig.get_facecolor(), edgecolor='none', transparent=False, metadata={'Software': 'matplotlib'}, pil_kwargs={'quality': 95 if args.publish else 85, 'optimize': True})
        plt.close(fig)
        return frame_path
    
    # Sort data in descending order
    sorted_indices = np.argsort(quarter_data)[::-1]  # Reverse order for descending
    quarter_data = [quarter_data[i] for i in sorted_indices]
    colors = [colors[i] for i in sorted_indices]
    labels = [labels[i] for i in sorted_indices]
    logos = [logos[i] for i in sorted_indices]
    
    # Limit to top N airlines
    if len(quarter_data) > MAX_BARS:
        quarter_data = quarter_data[:MAX_BARS]
        colors = colors[:MAX_BARS]
        labels = labels[:MAX_BARS]
        logos = logos[:MAX_BARS]
    
    # Calculate fixed positions for bars
    num_bars = len(quarter_data)
    y_positions = np.arange(num_bars) * TOTAL_BAR_HEIGHT
    
    # Create bars
    bars = ax.barh(y_positions, quarter_data, 
                   height=BAR_HEIGHT, 
                   color=colors,
                   edgecolor='none')
    
    # Add logos
    for i, (logo_path, y) in enumerate(zip(logos, y_positions)):
        if logo_path and os.path.exists(logo_path):
            try:
                print(f"Loading logo from: {logo_path}")
                img = plt.imread(logo_path)
                
                # 计算logo尺寸，保持纵横比
                img_height = BAR_HEIGHT * 0.8  # 设置为条形高度的80%
                aspect_ratio = img.shape[1] / img.shape[0]
                img_width = img_height * aspect_ratio
                
                # 计算以像素为单位的目标尺寸
                target_height_pixels = int(40)  # 固定高度为40像素 (reduced from 60)
                target_width_pixels = int(target_height_pixels * aspect_ratio)
                
                print(f"Processing logo with size: {target_width_pixels}x{target_height_pixels} pixels")
                
                # 处理logo图像
                # 转换到PIL图像进行处理
                if isinstance(img, np.ndarray):
                    if img.dtype == np.float32:
                        img = (img * 255).astype(np.uint8)
                    pil_img = Image.fromarray(img)
                else:
                    pil_img = img
                
                # 使用高质量调整大小
                pil_img = pil_img.resize((target_width_pixels, target_height_pixels), Image.Resampling.LANCZOS)
                
                # 应用锐化增强
                if pil_img.mode == 'RGBA':
                    r, g, b, a = pil_img.split()
                    rgb = Image.merge('RGB', (r, g, b))
                    enhancer = ImageEnhance.Sharpness(rgb)
                    rgb = enhancer.enhance(1.8)
                    contrast = ImageEnhance.Contrast(rgb)
                    rgb = contrast.enhance(1.3)
                    r, g, b = rgb.split()
                    pil_img = Image.merge('RGBA', (r, g, b, a))
                else:
                    enhancer = ImageEnhance.Sharpness(pil_img)
                    pil_img = enhancer.enhance(1.8)
                    contrast = ImageEnhance.Contrast(pil_img)
                    pil_img = contrast.enhance(1.3)
                
                # 转回numpy数组
                img_array = np.array(pil_img)
                
                # 转换回matplotlib可以使用的格式
                if img_array.dtype != np.float32 and img_array.max() > 1.0:
                    img_array = img_array.astype(np.float32) / 255.0
                
                # 保存处理好的logo数据，稍后在计算好display_max后添加
                logos_data.append({
                    'img_array': img_array,
                    'index': i,
                    'y': y
                })
                
                print(f"Processed logo successfully")
            except Exception as e:
                print(f"Error loading logo {logo_path}: {e}")
                # 打印完整的异常堆栈跟踪以便调试
                import traceback
                traceback.print_exc()
                # Don't let logo issues stop processing
                continue
    
    # Customize the plot
    ax.set_yticks(y_positions)
    ax.set_yticklabels(labels, fontsize=TICK_FONT_SIZE, fontproperties=monda_font, color=text_color)
    
    # Add value labels at the end of the bars
    for i, bar in enumerate(bars):
        value = quarter_data[i]
        value_text = format_revenue(value, None)
        ax.text(value + (max(quarter_data) * 0.01), y_positions[i], value_text,
                va='center', ha='left', fontsize=VALUE_FONT_SIZE, fontproperties=monda_font)
    
    # Format x-axis with custom formatter and set consistent colors
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_revenue))
    ax.xaxis.set_tick_params(labelsize=TICK_FONT_SIZE, colors=text_color)
    for label in ax.get_xticklabels():
        label.set_fontproperties(monda_font)
        label.set_color(text_color)
    
    # Set axis limits with padding for logos and labels
    max_value = max(quarter_data) if quarter_data else 0
    
    # Get historical maximum value across all quarters up to current frame
    historical_max = 0
    for i in range(frame_int + 1):
        quarter_historical = quarters[i]
        historical_data = revenue_data.loc[quarter_historical]
        quarter_max = historical_data.max()
        if pd.notna(quarter_max) and quarter_max > historical_max:
            historical_max = quarter_max
    
    # Use max of current frame and historical max
    display_max = max(max_value, historical_max)
    ax.set_xlim(0, display_max * 1.3)  # Add extra space on the right for logos and labels
    
    # Now add all processed logos with adjusted positions based on display_max
    for logo_data in logos_data:
        i = logo_data['index']
        y = logo_data['y']
        img_array = logo_data['img_array']
        
        # 计算logo位置（条形的右侧）
        value = quarter_data[i]
        value_width = len(format_revenue(value, None)) * 10  # 文本宽度的近似值
        
        # 降低常规情况下的基础偏移量
        base_offset_percentage = 0.04  # 从0.07降低到0.04
        text_padding = value_width / 100
        
        # 确保logo与数字之间有最小距离，防止重叠
        min_offset = display_max * 0.08  # 从0.12降低到0.08
        x_offset = max(min_offset, display_max * base_offset_percentage + text_padding)
        
        # 对于非常短的条形，进一步增加偏移量
        if value < display_max * 0.1:  # 如果值小于display_max的10%
            x_offset *= 1.5  # 增加50%的偏移量
        
        x = value + x_offset  # 计算最终位置
        
        # 创建OffsetImage并添加到图表
        imagebox = OffsetImage(img_array, zoom=0.8)  # 保持缩小的zoom因子
        ab = AnnotationBbox(imagebox, (x, y),
                          box_alignment=(0, 0.5),  # 左中对齐
                          frameon=False)
        ax.add_artist(ab)
        print(f"Added logo successfully at position ({x}, {y})")
    
    # Set fixed y-axis limits - reduced padding to move bars up
    total_height = MAX_BARS * TOTAL_BAR_HEIGHT
    ax.set_ylim(total_height, -BAR_PADDING * 2)  # Reduced negative padding to move bars up closer to timeline
    
    # Add grid lines
    ax.grid(True, axis='x', alpha=0.3, which='major', linestyle='--')
    
    # Style the axes
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)  # Hide bottom spine
    ax.tick_params(axis='y', which='both', left=False)
    
    # Add simplified Revenue label at the bottom with consistent color
    ax.set_xlabel('Revenue', fontsize=12, labelpad=10, fontproperties=monda_font, color=text_color)
    
    # Set up timeline - New style matching data-viz.py
    ax_timeline.set_facecolor('none')  # Transparent background
    
    # Get min and max quarters for timeline
    min_quarter = quarters[0]
    max_quarter = quarters[-1]
    min_year, min_q = parse_quarter(min_quarter)
    max_year, max_q = parse_quarter(max_quarter)
    
    # Set timeline limits with padding
    ax_timeline.set_xlim(-1, len(quarters))
    ax_timeline.set_ylim(-0.2, 0.2)
    
    # Set up timeline styling similar to data-viz.py
    ax_timeline.spines['top'].set_visible(False)
    ax_timeline.spines['right'].set_visible(False)
    ax_timeline.spines['left'].set_visible(False)
    ax_timeline.spines['bottom'].set_visible(True)
    ax_timeline.spines['bottom'].set_linewidth(1.5)
    ax_timeline.spines['bottom'].set_color(text_color)
    ax_timeline.spines['bottom'].set_position(('data', 0))
    
    # Add quarter markers with vertical lines
    for i, quarter in enumerate(quarters):
        year, q = parse_quarter(quarter)
        if q == 1:  # Major tick for Q1
            ax_timeline.vlines(i, -0.03, 0, colors=text_color, linewidth=1.5)
            # Show label for every year instead of just even years
            ax_timeline.text(i, -0.07, str(year), ha='center', va='top', 
                           fontsize=12, color=text_color, fontproperties=monda_font)
        else:  # Minor tick for other quarters
            ax_timeline.vlines(i, -0.02, 0, colors=text_color, linewidth=0.5, alpha=0.7)
    
    # Add current position marker (inverted triangle)
    timeline_position = frame_int + frame_fraction
    ax_timeline.plot(timeline_position, 0.03, marker='v', color='#4e843d', markersize=10, zorder=5)
    
    # Remove timeline ticks
    ax_timeline.set_xticks([])
    ax_timeline.set_yticks([])
    
    # Save the frame with sequential numbering and fixed size
    frame_path = os.path.join(frames_dir, f'frame_{frame_position:04d}.png')
    print(f"Saving frame to: {frame_path}")
    
    # 使用固定尺寸设置保存图像，不使用bbox_inches='tight'
    plt.savefig(
        frame_path,
        dpi=OUTPUT_DPI,
        bbox_inches=None,  # 不使用bbox_inches，使用固定的尺寸
        pad_inches=0.1,
        facecolor=fig.get_facecolor(),
        edgecolor='none',
        transparent=False,
        metadata={'Software': 'matplotlib'},
        pil_kwargs={
            'quality': 95 if args.publish else 85,
            'optimize': True,
        }
    )
    
    plt.close(fig)
    
    # 验证生成的帧尺寸
    try:
        img = Image.open(frame_path)
        print(f"Frame saved with dimensions: {img.size[0]}x{img.size[1]} pixels")
        img.close()
    except Exception as e:
        print(f"Error checking frame dimensions: {e}")
        
    return frame_path

def main():
    # Print logo files at start
    print("\nLogo files in logos directory:")
    logo_files = os.listdir(logos_dir)
    print("\n".join(sorted(logo_files)))
    print(f"\nTotal logo files found: {len(logo_files)}\n")

    print("\n开始生成帧...")
    
    # 在开始前先确认所有需要用到的目录
    for directory in [logos_dir, output_dir, frames_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
            
    # 清空输出目录中的现有帧文件，确保重新开始
    if os.path.exists(frames_dir):
        existing_frames = glob.glob(os.path.join(frames_dir, 'frame_*.png'))
        if existing_frames and input(f"Found {len(existing_frames)} existing frames. Clear them? (y/n): ").lower() == 'y':
            for f in existing_frames:
                try:
                    os.remove(f)
                except:
                    pass
            print(f"Cleared {len(existing_frames)} existing frames.")

    # Get the total number of frames to generate based on the number of quarters
    total_quarters = len(quarters)
    
    # Use the global frame_indices
    global frame_indices
    
    if args.publish and args.quarters_only:
        # In quarters-only mode, generate exactly one frame per quarter
        frame_indices = list(range(total_quarters))
        total_frames = total_quarters
        print(f"Quarters-only mode: Generating {total_frames} frames (one per quarter)")
    else:
        # In normal mode, generate multiple frames between quarters based on FRAMES_PER_YEAR
        frames_per_quarter = FRAMES_PER_YEAR // 4
        print(f"Normal mode: Generating approximately {frames_per_quarter} frames per quarter")
        
        # Create frame indices with appropriate interpolation between quarters
        frame_indices = []
        
        # Generate frames based on FRAMES_PER_YEAR
        for i in range(total_quarters - 1):
            # Add the main quarter frame
            frame_indices.append(i)
            
            # Add interpolated frames between quarters if not in quarters-only mode
            if not (args.publish and args.quarters_only):
                for j in range(1, frames_per_quarter):
                    # Calculate fractional index for interpolation
                    fraction = j / frames_per_quarter
                    frame_indices.append(i + fraction)
        
        # Add the last quarter
        frame_indices.append(total_quarters - 1)
        total_frames = len(frame_indices)
        
        # Sort frames to ensure sequential generation
        frame_indices.sort()
        
        print(f"Total frames to generate: {total_frames}")
        print(f"First few frame indices: {frame_indices[:10]}")
    
    # Create progress bar
    with tqdm(total=total_frames, desc="Generating frames") as pbar:
        # Create frames
        if args.publish:
            # Use multiple processes for publishing mode
            with mp.Pool() as pool:
                for _ in pool.imap_unordered(create_frame, frame_indices):
                    pbar.update(1)
        else:
            # Use single process for preview mode
            for frame_idx in frame_indices:
                create_frame(frame_idx)
                pbar.update(1)

    print("\n\n所有帧生成完成！")
    print(f"帧文件保存在: {frames_dir}")

if __name__ == '__main__':
    try:
        # 设置显示更多调试信息
        print("Running in DEBUG mode with extra logging...")
        
        # 检查logos目录中的文件
        print("\nChecking logo files in logos directory...")
        logo_files = os.listdir(logos_dir)
        print(f"Found {len(logo_files)} logo files:")
        for file in sorted(logo_files):
            print(f"  - {file}")
        
        # 检查一些常见的logo文件是否存在
        important_logos = [
            "logos/american-airlines-2013-now.jpg",
            "logos/delta-air-lines-2007-now.jpg",
            "logos/southwest-airlines-2014-now.png"
        ]
        
        print("\nVerifying key logo files:")
        for logo in important_logos:
            if os.path.exists(logo):
                print(f"  ✓ {logo} exists")
            else:
                print(f"  ✗ {logo} MISSING")
        
        # 运行主程序
        main()
    except Exception as e:
        print(f"ERROR in main program execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 