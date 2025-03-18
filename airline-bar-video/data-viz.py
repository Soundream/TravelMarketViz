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

# Process metadata
metadata = df.iloc[:7].copy()  # First 7 rows contain metadata
revenue_data = df.iloc[7:].copy()  # Revenue data starts from row 8

# Set proper index for metadata
metadata.set_index(metadata.columns[0], inplace=True)

# Convert revenue columns by removing ' M' suffix and converting to float
for col in revenue_data.columns[1:]:  # Skip the first column which contains row labels
    revenue_data[col] = pd.to_numeric(revenue_data[col].str.replace(' M', ''), errors='coerce')

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
BAR_HEIGHT = 0.7  # Fixed bar height
BAR_SPACING = 1.0  # Space between bars
TICK_FONT_SIZE = 12
LABEL_FONT_SIZE = 10
TITLE_FONT_SIZE = 18
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
    year = int("20" + year)  # Convert 2-digit year to 4-digit
    quarter = int(quarter[1])  # Extract quarter number
    return year, quarter

def create_frame(frame):
    """优化的帧创建函数，样式更接近原始data-viz"""
    optimize_figure_for_performance()
    
    # Create figure with optimized settings
    fig = plt.figure(figsize=FIGURE_SIZE, facecolor='white')
    
    # Create a gridspec with space at the top for logos and title
    gs = fig.add_gridspec(3, 1, height_ratios=[0.6, 0.3, 4], hspace=0.2,
                         top=0.95, bottom=0.07)
    
    # Create axis for title/logos area (can be used later for logos)
    ax_title = fig.add_subplot(gs[0])
    ax_title.axis('off')  # Hide axis
    
    # Create axis for timeline
    ax_timeline = fig.add_subplot(gs[1])
    
    # Create main axis for bar chart
    ax = fig.add_subplot(gs[2])

    # Get data for the current quarter
    quarter_data = []
    colors = []
    labels = []
    
    # Get the current quarter's data
    current_quarter = quarters[frame]
    current_data = revenue_data.loc[current_quarter]
    
    # Parse quarter info
    year, quarter = parse_quarter(current_quarter)
    quarter_display = f"Q{quarter} {year}"
    
    # Iterate through airlines
    for airline in current_data.index:
        value = current_data[airline]
        if pd.notna(value) and value > 0:  # Only include positive non-null values
            quarter_data.append(value)
            region = metadata.loc['Region', airline]
            colors.append(region_colors.get(region, '#808080'))  # Default to gray if region not found
            labels.append(airline)
    
    # Check if we have any valid data
    if not quarter_data:
        print(f"\nWarning: No valid data for quarter {current_quarter}")
        frame_path = os.path.join(frames_dir, f'frame_{frame:04d}.png')
        # Create an empty frame with a message
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
    
    # Limit to top N airlines
    if len(quarter_data) > MAX_BARS:
        quarter_data = quarter_data[:MAX_BARS]
        colors = colors[:MAX_BARS]
        labels = labels[:MAX_BARS]
    
    # Create bars - from top to bottom (like original dataviz)
    y_pos = np.arange(len(labels))[::-1] * BAR_SPACING  # Reverse order for top-to-bottom
    bars = ax.barh(y_pos, quarter_data, color=colors, height=BAR_HEIGHT, edgecolor='none')
    
    # Customize the plot
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels[::-1], fontsize=TICK_FONT_SIZE)  # Reverse labels to match bars
    
    # Create title in the title axis
    title_text = f'Global Airline Revenue Rankings - {quarter_display}'
    ax_title.text(0.5, 0.5, title_text, fontsize=TITLE_FONT_SIZE, fontweight='bold',
                ha='center', va='center', transform=ax_title.transAxes)
    
    # Add value labels inside or end of the bars
    for i, bar in enumerate(bars):
        value = quarter_data[i]
        value_text = format_revenue(value, None)
        # Position the text at the end of the bar with small padding
        ax.text(value + (max(quarter_data) * 0.01), y_pos[i], value_text,
                va='center', ha='left', fontsize=VALUE_FONT_SIZE)
    
    # Format x-axis with custom formatter
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_revenue))
    
    # Set axis limits with padding
    max_value = max(quarter_data) if quarter_data else 0
    ax.set_xlim(0, max_value * 1.15)
    
    # Set y-axis limits with padding
    if y_pos.size > 0:
        ax.set_ylim(min(y_pos) - BAR_SPACING, max(y_pos) + BAR_SPACING)
    
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
    
    # Create timeline tick positions (one for each year)
    timeline_years = list(range(min_year, max_year + 1))
    timeline_ticks = [f"{year}'Q{q}" for year in timeline_years for q in range(1, 5)]
    timeline_ticks = [q for q in timeline_ticks if q in quarters]
    
    # Set timeline limits
    ax_timeline.set_xlim(0, len(quarters) - 1)
    ax_timeline.set_ylim(-0.5, 0.5)
    
    # Create tick positions
    tick_positions = [quarters.index(q) for q in timeline_ticks if q in quarters]
    tick_labels = [q.split("'")[0] + " " + q.split("'")[1] for q in timeline_ticks]
    
    # Only show year labels, not quarters
    simplified_tick_labels = []
    prev_year = None
    for q in tick_labels:
        year = q.split(" ")[0]
        if year != prev_year and int(q.split("Q")[1]) == 1:  # Only show Q1 of each year
            simplified_tick_labels.append(year)
            prev_year = year
        else:
            simplified_tick_labels.append("")
    
    # Set timeline ticks
    ax_timeline.set_xticks(tick_positions)
    ax_timeline.set_xticklabels(simplified_tick_labels, fontsize=8)
    ax_timeline.tick_params(axis='y', which='both', left=False, labelleft=False)
    
    # Add timeline marker - a vertical line for current quarter
    ax_timeline.axvline(x=frame, color='red', linewidth=2, alpha=0.7)
    
    # Add current quarter text above the line
    ax_timeline.text(frame, 0.3, quarter_display, 
                     ha='center', va='bottom', fontsize=9, 
                     bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=1))
    
    # Draw a horizontal line for the timeline
    ax_timeline.axhline(y=0, color='black', linewidth=1, alpha=0.3)
    
    # Remove timeline spines
    for spine in ax_timeline.spines.values():
        spine.set_visible(False)
    
    # Save the frame
    frame_path = os.path.join(frames_dir, f'frame_{frame:04d}.png')
    plt.savefig(frame_path, dpi=OUTPUT_DPI, bbox_inches='tight')
    plt.close(fig)
    return frame_path

def main():
    """主函数，使用多进程处理帧生成"""
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

if __name__ == '__main__':
    print("\n开始生成帧...")
    main()
    print("\n\n所有帧生成完成！")
    print(f"帧文件保存在: {frames_dir}") 