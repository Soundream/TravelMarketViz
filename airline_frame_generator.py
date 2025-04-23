import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.colors as mcolors
import argparse
from PIL import Image, ImageFilter, ImageEnhance
import sys
from tqdm import tqdm
import matplotlib
import matplotlib.font_manager as fm
from io import BytesIO
matplotlib.use('Agg')  # 使用Agg后端以提高性能

# 添加命令行参数解析
parser = argparse.ArgumentParser(description='Generate airline revenue bar chart race frames')
parser.add_argument('--frames-per-year', type=int, default=60, help='Number of frames to generate per year (default: 60)')
parser.add_argument('--quarters-only', action='store_true', help='Only generate frames for each quarter')
parser.add_argument('--output-dir', type=str, default='frames', help='Output directory for frames (default: frames)')
parser.add_argument('--dpi', type=int, default=108, help='DPI for output frames (default: 108)')
parser.add_argument('--start-idx', type=int, default=None, help='Start frame index (default: None)')
parser.add_argument('--end-idx', type=int, default=None, help='End frame index (default: None)')
args = parser.parse_args()

# 设置质量参数
FRAMES_PER_YEAR = args.frames_per_year if not args.quarters_only else 4
OUTPUT_DPI = args.dpi
FIGURE_SIZE = (19.2, 10.8)  # 1080p尺寸
LOGO_DPI = 300  # 高DPI以获得清晰的logo

# 创建所需的目录
output_dir = args.output_dir
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"创建目录: {output_dir}")

# 全局变量
frame_indices = []
logo_cache = {}  # 预处理logo的缓存

def optimize_figure_for_performance():
    """优化matplotlib性能设置"""
    plt.rcParams['path.simplify'] = True
    plt.rcParams['path.simplify_threshold'] = 1.0
    plt.rcParams['agg.path.chunksize'] = 10000
    plt.rcParams['figure.dpi'] = OUTPUT_DPI
    plt.rcParams['savefig.dpi'] = OUTPUT_DPI
    plt.rcParams['savefig.bbox'] = 'standard'
    plt.rcParams['figure.autolayout'] = False
    plt.rcParams['figure.constrained_layout.use'] = False
    plt.rcParams['savefig.format'] = 'png'
    plt.rcParams['savefig.pad_inches'] = 0.1
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

def preprocess_logo(image_array, target_size=None):
    """优化logo预处理函数"""
    cache_key = f"{hash(str(image_array.tobytes()))}-{str(target_size)}"
    if cache_key in logo_cache:
        return logo_cache[cache_key]

    try:
        if isinstance(image_array, np.ndarray):
            if image_array.dtype == np.float32:
                image_array = (image_array * 255).astype(np.uint8)
            image = Image.fromarray(image_array)
        else:
            image = image_array

        original_mode = image.mode

        if target_size:
            w, h = target_size
            large_size = (w * 5, h * 5)
            image = image.resize(large_size, Image.Resampling.LANCZOS)

            # 应用更强的锐化和对比度增强
            if original_mode == 'RGBA':
                r, g, b, a = image.split()
                rgb = Image.merge('RGB', (r, g, b))
                
                enhancer = ImageEnhance.Sharpness(rgb)
                rgb = enhancer.enhance(2.2)
                
                contrast = ImageEnhance.Contrast(rgb)
                rgb = contrast.enhance(1.6)
                
                brightness = ImageEnhance.Brightness(rgb)
                rgb = brightness.enhance(1.15)
                
                r, g, b = rgb.split()
                image = Image.merge('RGBA', (r, g, b, a))
            else:
                enhancer = ImageEnhance.Sharpness(image)
                image = enhancer.enhance(2.2)
                
                contrast = ImageEnhance.Contrast(image)
                image = contrast.enhance(1.6)
                
                brightness = ImageEnhance.Brightness(image)
                image = brightness.enhance(1.15)

            image = image.filter(ImageFilter.UnsharpMask(radius=1.5, percent=220, threshold=2))
            image = image.filter(ImageFilter.GaussianBlur(radius=0.3))
            image = image.resize(target_size, Image.Resampling.LANCZOS)

        result = np.array(image)
        logo_cache[cache_key] = result
        return result
        
    except Exception as e:
        print(f"预处理logo时出错: {e}")
        return image_array

def format_revenue(value, pos):
    """格式化收入值，使用B表示十亿，M表示百万"""
    if value >= 1000:
        return f'${value/1000:.1f}B'
    return f'${value:.0f}M'

def parse_quarter(quarter_str):
    """解析季度字符串为(年份, 季度)"""
    year, quarter = quarter_str.split("'")
    year = int(year)  # 年份已经是4位数格式
    quarter = int(quarter[1])  # 提取季度数字
    return year, quarter

def is_before_may_2004(year, quarter):
    """检查日期是否在2004年5月之前的辅助函数"""
    if year < 2004:
        return True
    elif year == 2004:
        return quarter <= 1  # Q1及更早的在5月之前
    return False

# 创建区域颜色映射
region_colors = {
    'North America': '#40E0D0',  # 青色
    'Europe': '#4169E1',         # 皇家蓝
    'Asia Pacific': '#FF4B4B',   # 红色
    'Latin America': '#32CD32',  # 酸橙绿
    'China': '#FF4B4B',          # 红色（与亚太地区相同）
    'Middle East': '#DEB887',    # 实木色
    'Russia': '#FF4B4B',         # 红色（与亚太地区相同）
    'Turkey': '#DEB887'          # 实木色（与中东相同）
}

# 定义可视化常量
MAX_BARS = 15  # 最多显示的条形数量
BAR_HEIGHT = 0.8  # 每个条形的高度
BAR_PADDING = 0.2  # 条形之间的间距
TOTAL_BAR_HEIGHT = BAR_HEIGHT + BAR_PADDING  # 包括间距的总高度
TICK_FONT_SIZE = 14  # 从10增加
LABEL_FONT_SIZE = 14  # 从10增加
VALUE_FONT_SIZE = 14  # 从10增加

# 创建公司logo的映射
logo_mapping = {
    "easyJet": [{"start_year": 1999, "end_year": 9999, "file": "airline-bar-video/logos/easyJet-1999-now.jpg"}],
    "Emirates": [{"start_year": 1999, "end_year": 9999, "file": "airline-bar-video/logos/Emirates-logo.jpg"}],
    "Air France-KLM": [
        {"start_year": 1999, "end_year": 2004, "file": "airline-bar-video/logos/klm-1999-now.png"},
        {"start_year": 2004, "end_year": 9999, "file": "airline-bar-video/logos/Air-France-KLM-Holding-Logo.png"}
    ],
    "American Airlines": [
        {"start_year": 1967, "end_year": 2013, "file": "airline-bar-video/logos/american-airlines-1967-2013.jpg"},
        {"start_year": 2013, "end_year": 9999, "file": "airline-bar-video/logos/american-airlines-2013-now.jpg"}
    ],
    "Delta Air Lines": [
        {"start_year": 2000, "end_year": 2007, "file": "airline-bar-video/logos/delta-air-lines-2000-2007.png"},
        {"start_year": 2007, "end_year": 9999, "file": "airline-bar-video/logos/delta-air-lines-2007-now.jpg"}
    ],
    "Southwest Airlines": [
        {"start_year": 1989, "end_year": 2014, "file": "airline-bar-video/logos/southwest-airlines-1989-2014.png"},
        {"start_year": 2014, "end_year": 9999, "file": "airline-bar-video/logos/southwest-airlines-2014-now.png"}
    ],
    "United Airlines": [
        {"start_year": 1998, "end_year": 2010, "file": "airline-bar-video/logos/united-airlines-1998-2010.jpg"},
        {"start_year": 2010, "end_year": 9999, "file": "airline-bar-video/logos/united-airlines-2010-now.jpg"}
    ],
    "Alaska Air": [
        {"start_year": 1972, "end_year": 2014, "file": "airline-bar-video/logos/alaska-air-1972-2014.png"},
        {"start_year": 2014, "end_year": 2016, "file": "airline-bar-video/logos/alaska-air-2014-2016.png"},
        {"start_year": 2016, "end_year": 9999, "file": "airline-bar-video/logos/alaska-air-2016-now.jpg"}
    ],
    "Finnair": [
        {"start_year": 1999, "end_year": 2010, "file": "airline-bar-video/logos/Finnair-1999-2010.jpg"},
        {"start_year": 2010, "end_year": 9999, "file": "airline-bar-video/logos/Finnair-2010-now.jpg"}
    ],
    "Deutsche Lufthansa": [
        {"start_year": 1999, "end_year": 2018, "file": "airline-bar-video/logos/Deutsche Lufthansa-1999-2018.png"},
        {"start_year": 2018, "end_year": 9999, "file": "airline-bar-video/logos/Deutsche Lufthansa-2018-now.jpg"}
    ],
    "Singapore Airlines": [{"start_year": 1999, "end_year": 9999, "file": "airline-bar-video/logos/Singapore Airlines-1999-now.jpg"}],
    "Qantas Airways": [{"start_year": 1999, "end_year": 9999, "file": "airline-bar-video/logos/Qantas Airways-1999-now.jpg"}],
    "Cathay Pacific": [{"start_year": 1999, "end_year": 9999, "file": "airline-bar-video/logos/Cathay Pacific-1999-now.png"}],
    "LATAM Airlines": [
        {"start_year": 1999, "end_year": 2016, "file": "airline-bar-video/logos/LATAM Airlines-1999-2016.png"},
        {"start_year": 2016, "end_year": 9999, "file": "airline-bar-video/logos/LATAM Airlines-2016-now.jpg"}
    ],
    "Air China": [{"start_year": 1999, "end_year": 9999, "file": "airline-bar-video/logos/Air China-1999-now.png"}],
    "China Eastern": [{"start_year": 1999, "end_year": 9999, "file": "airline-bar-video/logos/China Eastern-1999-now.jpg"}],
    "China Southern": [{"start_year": 1999, "end_year": 9999, "file": "airline-bar-video/logos/China Southern-1999-now.jpg"}],
    "Hainan Airlines": [
        {"start_year": 1999, "end_year": 2004, "file": "airline-bar-video/logos/Hainan Airlines-1999-2004.png"},
        {"start_year": 2004, "end_year": 9999, "file": "airline-bar-video/logos/Hainan Airlines-2004-now.jpg"}
    ],
    "Qatar Airways": [{"start_year": 1999, "end_year": 9999, "file": "airline-bar-video/logos/Qatar Airways-1999-now.jpg"}],
    "Turkish Airlines": [
        {"start_year": 1999, "end_year": 2018, "file": "airline-bar-video/logos/Turkish Airlines-1999-2018.png"},
        {"start_year": 2018, "end_year": 9999, "file": "airline-bar-video/logos/Turkish Airlines-2018-now.png"}
    ],
    "JetBlue": [{"start_year": 1999, "end_year": 9999, "file": "airline-bar-video/logos/jetBlue-1999-now.jpg"}],
    "SkyWest": [
        {"start_year": 1972, "end_year": 2001, "file": "airline-bar-video/logos/skywest-1972-2001.png"},
        {"start_year": 2001, "end_year": 2008, "file": "airline-bar-video/logos/skywest-2001-2008.png"},
        {"start_year": 2018, "end_year": 9999, "file": "airline-bar-video/logos/skywest-2018-now.jpg"}
    ],
    "Northwest Airlines": [
        {"start_year": 1989, "end_year": 2003, "file": "airline-bar-video/logos/northwest-airlines-1989-2003.png"},
        {"start_year": 2003, "end_year": 9999, "file": "airline-bar-video/logos/northwest-airlines-2003-now.jpg"}
    ],
    "TWA": [{"start_year": 1999, "end_year": 9999, "file": "airline-bar-video/logos/TWA-1999-now.png"}],
    "Air Canada": [
        {"start_year": 1995, "end_year": 2005, "file": "airline-bar-video/logos/air-canada-1995-2005.jpg"},
        {"start_year": 2005, "end_year": 9999, "file": "airline-bar-video/logos/air-canada-2005-now.png"}
    ],
    "IAG": [{"start_year": 1999, "end_year": 9999, "file": "airline-bar-video/logos/IAG-1999-now.png"}],
    "Ryanair": [
        {"start_year": 1999, "end_year": 2001, "file": "airline-bar-video/logos/Ryanair-1999-2001.png"},
        {"start_year": 2001, "end_year": 2013, "file": "airline-bar-video/logos/Ryanair-2001-2013.jpg"},
        {"start_year": 2013, "end_year": 9999, "file": "airline-bar-video/logos/Ryanair-2013-now.jpg"}
    ],
    "Aeroflot": [
        {"start_year": 1999, "end_year": 2003, "file": "airline-bar-video/logos/Aeroflot-1999-2003.jpg"},
        {"start_year": 2003, "end_year": 9999, "file": "airline-bar-video/logos/Aeroflot-2003-now.jpg"}
    ],
    "Norwegian Air": [{"start_year": 1999, "end_year": 9999, "file": "airline-bar-video/logos/norwegian-logo.jpg"}]
}

def get_logo_path(airline, year, iata_code, month=6):
    """根据航空公司名称、年份和月份获取适当的logo路径"""
    try:
        print(f"获取航空公司logo: {airline}, 年份: {year}, IATA: {iata_code}, 月份: {month}")
        
        # 挪威航空特殊处理
        if iata_code == "DY":
            norwegian_logo = "airline-bar-video/logos/norwegian-logo.jpg"
            if os.path.exists(norwegian_logo):
                print(f"找到挪威航空logo: {norwegian_logo}")
                return norwegian_logo
            else:
                print(f"挪威航空logo文件不存在: {norwegian_logo}")
                return None
        
        # 检查航空公司是否在映射中
        if airline not in logo_mapping:
            print(f"警告: 航空公司 '{airline}' 不在logo映射中")
            return None
        
        logo_versions = logo_mapping[airline]
        print(f"找到航空公司 '{airline}' 的 {len(logo_versions)} 个logo版本")
        
        # 特殊处理法荷航
        if airline == "Air France-KLM":
            if year < 2004 or (year == 2004 and month < 5):
                for version in logo_versions:
                    if version["file"] == "airline-bar-video/logos/klm-1999-now.png":
                        logo_path = version["file"]
                        if os.path.exists(logo_path):
                            print(f"找到法荷航(KLM时期)logo: {logo_path}")
                            return logo_path
                        else:
                            print(f"法荷航(KLM时期)logo文件不存在: {logo_path}")
                            return None
            else:
                for version in logo_versions:
                    if version["file"] == "airline-bar-video/logos/Air-France-KLM-Holding-Logo.png":
                        logo_path = version["file"]
                        if os.path.exists(logo_path):
                            print(f"找到法荷航(合并后)logo: {logo_path}")
                            return logo_path
                        else:
                            print(f"法荷航(合并后)logo文件不存在: {logo_path}")
                            return None
        
        # 一般航空公司处理 - 按年份查找
        for version in logo_versions:
            if version["start_year"] <= year <= version["end_year"]:
                logo_path = version["file"]
                if os.path.exists(logo_path):
                    print(f"找到 {airline} logo: {logo_path}")
                    return logo_path
                else:
                    print(f"警告: {airline} logo文件不存在: {logo_path}")
                    return None
        
        print(f"警告: 未找到适合 {airline} 在 {year} 年的logo")
        return None
    
    except Exception as e:
        print(f"获取logo时发生错误: {airline}, {e}")
        import traceback
        traceback.print_exc()
        return None

def create_frame(frame_idx, revenue_data, metadata, quarters):
    """为特定帧索引创建条形图"""
    optimize_figure_for_performance()
    
    # 禁用matplotlib的异步行为，确保同步渲染
    plt.ioff()  # 关闭交互模式
    
    frame_int = int(frame_idx)
    frame_fraction = frame_idx - frame_int
    
    # 创建具有固定尺寸的图形
    fig = plt.figure(figsize=FIGURE_SIZE, facecolor='white', dpi=OUTPUT_DPI)
    
    # 数据插值计算
    if frame_fraction == 0 or args.quarters_only:
        current_quarter = quarters[frame_int]
        interpolated_data = revenue_data.loc[current_quarter].copy()
    else:
        if frame_int < len(quarters) - 1:
            q1 = quarters[frame_int]
            q2 = quarters[frame_int + 1]
            q1_data = revenue_data.loc[q1]
            q2_data = revenue_data.loc[q2]
            
            # 线性插值
            interpolated_data = q1_data * (1 - frame_fraction) + q2_data * frame_fraction
        else:
            current_quarter = quarters[frame_int]
            interpolated_data = revenue_data.loc[current_quarter].copy()
    
    # 设置文本颜色
    text_color = '#808080'
    
    # 创建子图布局
    gs = fig.add_gridspec(2, 1, height_ratios=[0.15, 1], 
                         left=0.1, right=0.9,
                         bottom=0.1, top=0.95,
                         hspace=0.05)
    
    ax_timeline = fig.add_subplot(gs[0])
    ax = fig.add_subplot(gs[1])
    
    # 计算当前日期
    if frame_int < len(quarters):
        current_quarter = quarters[frame_int]
    else:
        current_quarter = quarters[-1]
    
    year, quarter = parse_quarter(current_quarter)
    
    # 日期插值计算
    if frame_fraction > 0:
        if frame_int < len(quarters) - 1:
            q1 = quarters[frame_int]
            q2 = quarters[frame_int + 1]
            year1, quarter1 = parse_quarter(q1)
            year2, quarter2 = parse_quarter(q2)
            
            # 年份和季度的线性插值
            year_fraction1 = year1 + (quarter1 - 1) * 0.25
            year_fraction2 = year2 + (quarter2 - 1) * 0.25
            year_fraction = year_fraction1 * (1 - frame_fraction) + year_fraction2 * frame_fraction
            
            year_integer = int(year_fraction)
            month = int((year_fraction - year_integer) * 12) + 1
            quarter_display = f"{year_integer} {month:02d}"
            current_month = month
            current_year = year_integer
        else:
            year_fraction = year + (quarter - 1) * 0.25 + frame_fraction * 0.25
            year_integer = int(year_fraction)
            month = int((year_fraction - year_integer) * 12) + 1
            quarter_display = f"{year_integer} {month:02d}"
            current_month = month
            current_year = year_integer
    else:
        quarter_display = f"{year} Q{quarter}"
        month_mapping = {1: 2, 2: 5, 3: 8, 4: 11}
        current_month = month_mapping[quarter]
        current_year = year
    
    # 创建统一的数据结构
    unified_bar_data = []
    
    # 收集所有公司数据
    for airline in interpolated_data.index:
        value = interpolated_data[airline]
        if pd.notna(value) and value > 0:
            region = metadata.loc['Region', airline]
            color = region_colors.get(region, '#808080')
            
            # 处理Air France-KLM标签
            if airline == "Air France-KLM":
                if current_year < 2004 or (current_year == 2004 and current_month < 5):
                    label = "KL"
                else:
                    iata_code = metadata.loc['IATA Code', airline]
                    label = iata_code if pd.notna(iata_code) else airline[:3]
            else:
                iata_code = metadata.loc['IATA Code', airline]
                label = iata_code if pd.notna(iata_code) else airline[:3]
            
            # 获取logo路径
            logo_path = get_logo_path(airline, current_year, iata_code, current_month)
            
            unified_bar_data.append({
                'airline': airline,
                'value': value,
                'region': region,
                'color': color,
                'label': label,
                'logo_path': logo_path,
                'iata_code': iata_code
            })
    
    # 检查是否有有效数据
    if not unified_bar_data:
        fig.suptitle(f'No data available for {current_quarter}', fontsize=14)
        filename = os.path.join(output_dir, f'frame_{frame_idx:05.2f}.png')
        plt.savefig(filename, dpi=OUTPUT_DPI, pad_inches=0.1)
        plt.close(fig)
        return filename
    
    # 按值排序数据
    unified_bar_data.sort(key=lambda x: x['value'], reverse=True)
    
    # 限制显示条数
    if len(unified_bar_data) > MAX_BARS:
        unified_bar_data = unified_bar_data[:MAX_BARS]
    
    # 计算显示所需的最大值
    max_value = max(item['value'] for item in unified_bar_data) if unified_bar_data else 0
    
    # 获取历史最大值
    historical_max = 0
    for i in range(frame_int + 1):
        quarter_historical = quarters[i]
        historical_data = revenue_data.loc[quarter_historical]
        quarter_max = historical_data.max()
        if pd.notna(quarter_max) and quarter_max > historical_max:
            historical_max = quarter_max
    
    # 使用当前帧和历史的最大值
    display_max = max(max_value, historical_max)
    
    # 预先计算所有元素位置 - 确保完全同步
    bars_data = []
    text_data = []
    logo_objects = []
    
    # 设置图表边界
    ax.set_xlim(0, display_max * 1.5)
    total_height = MAX_BARS * TOTAL_BAR_HEIGHT
    ax.set_ylim(total_height, -BAR_PADDING * 2)
    
    # 创建初始条形图，但先不显示 - 只是为了设置轴和布局
    y_positions = []
    values = []
    colors = []
    labels = []
    
    # 预计算所有位置，确保一致性
    for idx, item in enumerate(unified_bar_data):
        y_pos = idx * TOTAL_BAR_HEIGHT
        value = item['value']
        
        y_positions.append(y_pos)
        values.append(value)
        colors.append(item['color'])
        labels.append(item['label'])
        
        # 存储位置信息 - 同一个基准计算所有元素位置
        text_pos = value + display_max * 0.01
        logo_pos = value + display_max * 0.08
        formatted_value = format_revenue(value, None)
        
        # 统一存储所有元素数据
        bars_data.append({
            'y_position': y_pos,
            'value': value,
            'color': item['color']
        })
        
        text_data.append({
            'text': formatted_value,
            'position': (text_pos, y_pos),
            'color': text_color
        })
        
        if item['logo_path'] and os.path.exists(item['logo_path']):
            logo_objects.append({
                'path': item['logo_path'],
                'position': (logo_pos, y_pos)
            })
    
    # 设置标签
    ax.set_yticks(y_positions)
    ax.set_yticklabels(labels, fontsize=TICK_FONT_SIZE, color=text_color)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_revenue))
    ax.xaxis.set_tick_params(labelsize=TICK_FONT_SIZE, colors=text_color)
    for label in ax.get_xticklabels():
        label.set_color(text_color)
    
    # 添加网格线和样式
    ax.grid(True, axis='x', alpha=0.3, which='major', linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.tick_params(axis='y', which='both', left=False)
    ax.set_xlabel('Revenue', fontsize=16, labelpad=10, color=text_color)
    
    # 设置时间轴
    ax_timeline.set_facecolor('none')
    ax_timeline.set_xlim(-1, len(quarters) + 0.5)
    ax_timeline.set_ylim(-0.2, 0.2)
    
    ax_timeline.spines['top'].set_visible(False)
    ax_timeline.spines['right'].set_visible(False)
    ax_timeline.spines['left'].set_visible(False)
    ax_timeline.spines['bottom'].set_visible(True)
    ax_timeline.spines['bottom'].set_linewidth(1.5)
    ax_timeline.spines['bottom'].set_color(text_color)
    ax_timeline.spines['bottom'].set_position(('data', 0))
    
    # 添加季度标记
    for i, quarter in enumerate(quarters):
        year, q = parse_quarter(quarter)
        if q == 1:
            ax_timeline.vlines(i, -0.03, 0, colors=text_color, linewidth=1.5)
            if year % 2 == 1 or year == 2025:
                ax_timeline.text(i, -0.07, str(year), ha='center', va='top', 
                              fontsize=16, color=text_color)
        else:
            ax_timeline.vlines(i, -0.02, 0, colors=text_color, linewidth=0.5, alpha=0.7)
    
    # 添加2025年标记（如果需要）
    last_year, last_q = parse_quarter(quarters[-1])
    if last_year == 2024 and last_q == 4:
        next_year_pos = len(quarters)
        ax_timeline.vlines(next_year_pos, -0.03, 0, colors=text_color, linewidth=1.5)
        ax_timeline.text(next_year_pos, -0.07, "2025", ha='center', va='top', 
                      fontsize=16, color=text_color)
    
    # 添加当前位置标记
    timeline_position = frame_int + frame_fraction
    ax_timeline.plot(timeline_position, 0.03, marker='v', color='#4e843d', markersize=10, zorder=5)
    ax_timeline.set_xticks([])
    ax_timeline.set_yticks([])
    
    # 强制更新布局
    fig.tight_layout(rect=[0.1, 0.1, 0.9, 0.95])
    
    # 确保图表布局和轴设置已经完成
    fig.canvas.draw()
    
    # 绘制条形图 - 全部一次性绘制，确保同步
    bars = ax.barh(y_positions, values, height=BAR_HEIGHT, color=colors, edgecolor='none')
    
    # 添加数值文本
    text_objects = []
    for data in text_data:
        text = ax.text(data['position'][0], data['position'][1], data['text'],
                     va='center', ha='left', fontsize=VALUE_FONT_SIZE, color=data['color'])
        text_objects.append(text)
    
    # 添加logo - 一次性处理所有logo以确保同步
    for logo_info in logo_objects:
        try:
            img = plt.imread(logo_info['path'])
            
            # 处理logo图像
            target_height_pixels = int(40)
            aspect_ratio = img.shape[1] / img.shape[0]
            target_width_pixels = int(target_height_pixels * aspect_ratio)
            
            if isinstance(img, np.ndarray):
                if img.dtype == np.float32:
                    img = (img * 255).astype(np.uint8)
                pil_img = Image.fromarray(img)
            else:
                pil_img = img
            
            pil_img = pil_img.resize((target_width_pixels, target_height_pixels), Image.Resampling.LANCZOS)
            
            # 增强logo
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
            
            img_array = np.array(pil_img)
            
            if img_array.dtype != np.float32 and img_array.max() > 1.0:
                img_array = img_array.astype(np.float32) / 255.0
            
            # 创建并添加logo
            img_box = OffsetImage(img_array, zoom=0.9)
            img_box.image.axes = ax
            
            ab = AnnotationBbox(img_box, logo_info['position'],
                              frameon=False,
                              box_alignment=(0, 0.5))
            ax.add_artist(ab)
            
        except Exception as e:
            print(f"添加logo时出错: {e}")
            continue
    
    # 二次强制渲染，确保所有元素都已更新
    fig.canvas.draw()
    plt.draw()
    
    # 保存图像
    filename = os.path.join(output_dir, f'frame_{frame_idx:05.2f}.png')
    plt.savefig(filename, dpi=OUTPUT_DPI, pad_inches=0.1)
    plt.close(fig)
    
    return filename

def main():
    """主函数来生成所有帧"""
    # 加载数据
    print("正在加载数据...")
    df = pd.read_csv('airline-bar-video/airlines_final.csv')
    
    # 处理元数据
    metadata = df.iloc[:7].copy()  # 前7行包含元数据
    revenue_data = df.iloc[7:].copy()  # 收入数据从第8行开始
    
    # 设置元数据的索引
    metadata.set_index(metadata.columns[0], inplace=True)
    
    # 转换收入列
    for col in revenue_data.columns[1:]:  # 跳过第一列（包含行标签）
        revenue_data[col] = pd.to_numeric(revenue_data[col].str.replace(',', '').str.replace(' M', ''), errors='coerce')
    
    # 设置收入数据的索引
    revenue_data.set_index(revenue_data.columns[0], inplace=True)
    
    # 获取季度列表
    quarters = revenue_data.index.tolist()
    
    # 生成帧索引
    frame_indices = []
    if args.quarters_only:
        # 在仅季度模式下，每个季度生成一帧
        frame_indices = list(range(len(quarters)))
    else:
        # 生成插值帧
        frames_per_quarter = FRAMES_PER_YEAR // 4
        for i in range(len(quarters) - 1):
            # 添加主季度帧
            frame_indices.append(i)
            
            # 添加季度之间的插值帧
            for j in range(1, frames_per_quarter):
                fraction = j / frames_per_quarter
                frame_indices.append(i + fraction)
        
        # 添加最后一个季度
        frame_indices.append(len(quarters) - 1)
    
    # 如果指定了起始和结束索引，则只处理该范围内的帧
    if args.start_idx is not None:
        if args.end_idx is not None:
            frame_indices = frame_indices[args.start_idx:args.end_idx]
        else:
            frame_indices = frame_indices[args.start_idx:]
    elif args.end_idx is not None:
        frame_indices = frame_indices[:args.end_idx]
    
    # 排序帧索引
    frame_indices.sort()
    
    print(f"将生成 {len(frame_indices)} 帧...")
    
    # 生成所有帧
    for frame_idx in tqdm(frame_indices, desc="生成帧"):
        create_frame(frame_idx, revenue_data, metadata, quarters)
    
    print(f"已完成！所有帧已保存到 {output_dir} 目录")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1) 