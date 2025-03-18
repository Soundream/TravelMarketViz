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
    'North America': '#2ecc71',  # Green
    'Europe': '#3498db',         # Blue
    'Asia Pacific': '#e74c3c',   # Red
    'Latin America': '#f1c40f',  # Yellow
    'China': '#9b59b6',          # Purple
    'Middle East': '#e67e22',    # Orange
    'Russia': '#95a5a6',         # Gray
    'Turkey': '#34495e'          # Dark Blue
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

# Create a mapping for company logos
logo_mapping = {
    "American Airlines": [
        {"start_year": 1967, "end_year": 2013, "file": "logos/american-airlines-1967-2013.jpg"},
        {"start_year": 2013, "end_year": 9999, "file": "logos/american-airlines-2013-now.jpg"}
    ],
    "Delta Air Lines": [
        {"start_year": 2000, "end_year": 2007, "file": "logos/delta-air-lines-2000-2007.png"},
        {"start_year": 2007, "end_year": 9999, "file": "logos/delta-air-lines-2007-now.jpg"}
    ],
    "Southwest Airlines": [
        {"start_year": 2014, "end_year": 9999, "file": "logos/southwest-airlines-2014-now.png"}
    ],
    "United Airlines": [
        {"start_year": 1998, "end_year": 2010, "file": "logos/united-airlines-1998-2010.jpg"},
        {"start_year": 2010, "end_year": 9999, "file": "logos/united-airlines-2010-now.jpg"}
    ],
    "Air France-KLM": [{"start_year": 1999, "end_year": 9999, "file": "logos/klm-1999-now.png"}],
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
    "IAG": [{"start_year": 1999, "end_year": 9999, "file": "logos/IAG-1999-now.png"}]
}

def get_logo_path(airline, year, iata_code):
    """Get the appropriate logo path based on airline name and year"""
    if airline not in logo_mapping:
        print(f"No logo mapping found for {airline}")
        return None
        
    logo_versions = logo_mapping[airline]
    
    # Find the appropriate logo version for the given year
    for version in logo_versions:
        if version["start_year"] <= year <= version["end_year"]:
            logo_path = version["file"]
            if os.path.exists(logo_path):
                print(f"Found logo for {airline} ({year}): {logo_path}")
                return logo_path
            else:
                print(f"Logo file not found: {logo_path}")
                return None
    
    print(f"No logo version found for {airline} in year {year}")
    return None

def create_frame(frame):
    """优化的帧创建函数，样式更接近原始data-viz"""
    optimize_figure_for_performance()
    
    # Create figure with optimized settings
    fig = plt.figure(figsize=FIGURE_SIZE, facecolor='white')
    
    # Create a gridspec with space for timeline and bars
    gs = fig.add_gridspec(2, 1, height_ratios=[0.15, 1], hspace=0.1,
                         top=0.95, bottom=0.05)
    
    # Create axis for timeline
    ax_timeline = fig.add_subplot(gs[0])
    
    # Create main axis for bar chart
    ax = fig.add_subplot(gs[1])

    # Get data for the current quarter
    quarter_data = []
    colors = []
    labels = []
    logos = []
    
    # Get the current quarter's data
    current_quarter = quarters[frame]
    current_data = revenue_data.loc[current_quarter]
    
    # Parse quarter info
    year, quarter = parse_quarter(current_quarter)
    quarter_display = f"{year} Q{quarter}"
    
    print(f"\nProcessing frame for {quarter_display}")
    print(f"Current data for {quarter_display}: {current_data}")  # Debugging line
    
    # Iterate through airlines
    for airline in current_data.index:
        value = current_data[airline]
        print(f"{airline}: {value}")  # Debugging line
        if pd.notna(value) and value > 0:  # Only include positive non-null values
            quarter_data.append(value)
            region = metadata.loc['Region', airline]
            colors.append(region_colors.get(region, '#808080'))  # Default to gray if region not found
            # Use IATA code instead of full name
            iata_code = metadata.loc['IATA', airline]
            labels.append(iata_code if pd.notna(iata_code) else airline[:3])
            
            # Get logo path using IATA code
            logo_path = get_logo_path(airline, year, iata_code)
            logos.append(logo_path)
    
    # Check if we have any valid data
    if not quarter_data:
        print(f"\nWarning: No valid data for quarter {current_quarter}")
        frame_path = os.path.join(frames_dir, f'frame_{frame:04d}.png')
        ax.text(0.5, 0.5, f'No data available for {current_quarter}',
                ha='center', va='center', transform=ax.transAxes)
        plt.savefig(frame_path, dpi=OUTPUT_DPI, bbox_inches='tight')
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
                img = plt.imread(logo_path)
                
                # Calculate logo size maintaining aspect ratio
                img_height = BAR_HEIGHT * 0.8
                aspect_ratio = img.shape[1] / img.shape[0]
                img_width = img_height * aspect_ratio
                
                # Preprocess logo with calculated size
                img = preprocess_logo(img, target_size=(int(img_width * 72), int(img_height * 72)))
                
                # Calculate logo position (right of the value label)
                value = quarter_data[i]
                value_width = len(format_revenue(value, None)) * 10  # Approximate width of value text
                x = value + (max(quarter_data) * 0.02) + (value_width / 100)  # Place logo after value label
                
                # Create OffsetImage and AnnotationBbox
                imagebox = OffsetImage(img, zoom=0.5)  # Adjust zoom to match calculated size
                imagebox.image.axes = ax
                
                # Add the logo
                ab = AnnotationBbox(imagebox, (x, y),
                                  box_alignment=(0, 0.5),  # Align left center
                                  frameon=False)
                ax.add_artist(ab)
            except Exception as e:
                print(f"Error loading logo {logo_path}: {e}")
    
    # Customize the plot
    ax.set_yticks(y_positions)
    ax.set_yticklabels(labels, fontsize=TICK_FONT_SIZE)
    
    # Add value labels at the end of the bars
    for i, bar in enumerate(bars):
        value = quarter_data[i]
        value_text = format_revenue(value, None)
        ax.text(value + (max(quarter_data) * 0.01), y_positions[i], value_text,
                va='center', ha='left', fontsize=VALUE_FONT_SIZE)
    
    # Format x-axis with custom formatter
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_revenue))
    
    # Set axis limits with padding for logos and labels
    max_value = max(quarter_data) if quarter_data else 0
    ax.set_xlim(0, max_value * 1.3)  # Add extra space on the right for logos and labels
    
    # Set fixed y-axis limits
    total_height = MAX_BARS * TOTAL_BAR_HEIGHT
    ax.set_ylim(total_height, -BAR_PADDING)
    
    # Add grid lines
    ax.grid(True, axis='x', alpha=0.3, which='major', linestyle='--')
    
    # Style the axes
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.tick_params(axis='y', which='both', left=False)
    
    # Set up timeline
    ax_timeline.set_facecolor('none')  # Transparent background
    
    # Get min and max quarters for timeline
    min_quarter = quarters[0]
    max_quarter = quarters[-1]
    min_year, min_q = parse_quarter(min_quarter)
    max_year, max_q = parse_quarter(max_quarter)
    
    # Create timeline tick positions
    timeline_ticks = np.linspace(0, len(quarters) - 1, num=len(quarters))
    
    # Set timeline limits with padding
    ax_timeline.set_xlim(-1, len(quarters))
    ax_timeline.set_ylim(-1, 1)
    
    # Draw timeline base line
    ax_timeline.axhline(y=0, color='black', linewidth=1, alpha=0.3)
    
    # Add quarter markers
    for i, quarter in enumerate(quarters):
        year, q = parse_quarter(quarter)
        if q == 1:  # Major tick for Q1
            ax_timeline.plot([i, i], [-0.2, 0.2], color='black', linewidth=1, alpha=0.5)
            ax_timeline.text(i, -0.5, str(year), ha='center', va='top', fontsize=8)
        else:  # Minor tick for other quarters
            ax_timeline.plot([i, i], [-0.1, 0.1], color='black', linewidth=1, alpha=0.3)
    
    # Add current position marker (green arrow)
    marker_height = 0.4
    arrow_width = 0.3
    ax_timeline.plot([frame, frame], [0, marker_height], color='#2ecc71', linewidth=2)
    ax_timeline.plot([frame - arrow_width, frame, frame + arrow_width], 
                    [marker_height - arrow_width, marker_height, marker_height - arrow_width],
                    color='#2ecc71', linewidth=2)
    
    # Add current quarter text
    ax_timeline.text(frame, marker_height + 0.1, quarter_display, 
                    ha='center', va='bottom', fontsize=9,
                    color='#2ecc71', fontweight='bold')
    
    # Remove timeline axis lines
    ax_timeline.set_xticks([])
    ax_timeline.set_yticks([])
    for spine in ax_timeline.spines.values():
        spine.set_visible(False)
    
    # Save the frame
    frame_path = os.path.join(frames_dir, f'frame_{frame:04d}.png')
    plt.savefig(frame_path, dpi=OUTPUT_DPI, bbox_inches='tight')
    plt.close(fig)
    return frame_path

def main():
    # Print logo files at start
    print("\nLogo files in logos directory:")
    logo_files = os.listdir(logos_dir)
    print("\n".join(sorted(logo_files)))
    print(f"\nTotal logo files found: {len(logo_files)}\n")

    print("\n开始生成帧...")
    
    # Get the total number of frames
    total_frames = len(quarters)
    
    # Create progress bar
    with tqdm(total=total_frames, desc="Generating frames") as pbar:
        # Create frames
        if args.publish:
            # Use multiple processes for publishing mode
            with mp.Pool() as pool:
                for _ in pool.imap_unordered(create_frame, range(total_frames)):
                    pbar.update(1)
        else:
            # Use single process for preview mode
            for frame in range(total_frames):
                create_frame(frame)
                pbar.update(1)

    print("\n\n所有帧生成完成！")
    print(f"帧文件保存在: {frames_dir}")

if __name__ == '__main__':
    main() 