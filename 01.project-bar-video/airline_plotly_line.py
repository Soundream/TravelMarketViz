import pandas as pd
import os
import plotly.graph_objs as go
import plotly.io as pio
from tqdm import tqdm
import numpy as np
import base64
from PIL import Image

def get_logo_path(airline, year, iata_code, month=6):
    logo_mapping = {
        "easyJet": [{"start_year": 1999, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/easyJet-1999-now.jpg"}],
        "Emirates": [{"start_year": 1999, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Emirates-logo.jpg"}],
        "Air France-KLM": [
            {"start_year": 1999, "end_year": 2004, "file": "../99.utility/airline-bar-video/logos/klm-1999-now.png", "iata": "KL"},
            {"start_year": 2004, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Air-France-KLM-Holding-Logo.png", "iata": "AF"}
        ],
        "American Airlines": [
            {"start_year": 1999, "end_year": 2013, "file": "../99.utility/airline-bar-video/logos/american-airlines-1967-2013.jpg"},
            {"start_year": 2013, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/american-airlines-2013-now.jpg"}
        ],
        "United Airlines": [
            {"start_year": 1998, "end_year": 2010, "file": "../99.utility/airline-bar-video/logos/united-airlines-1998-2010.jpg"},
            {"start_year": 2010, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/united-airlines-2010-now.jpg"}
        ],
        "Delta Air Lines": [
            {"start_year": 2000, "end_year": 2007, "file": "../99.utility/airline-bar-video/logos/delta-air-lines-2000-2007.png"},
            {"start_year": 2007, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/delta-air-lines-2007-now.jpg"}
        ],
        "Southwest Airlines": [
            {"start_year": 1989, "end_year": 2014, "file": "../99.utility/airline-bar-video/logos/southwest-airlines-1989-2014.png"},
            {"start_year": 2014, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/southwest-airlines-2014-now.png"}
        ],
        "Lufthansa": [
            {"start_year": 1999, "end_year": 2018, "file": "../99.utility/airline-bar-video/logos/Deutsche Lufthansa-1999-2018.png"},
            {"start_year": 2018, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Deutsche Lufthansa-2018-now.jpg"}
        ],
        "Deutsche Lufthansa": [
            {"start_year": 1999, "end_year": 2018, "file": "../99.utility/airline-bar-video/logos/Deutsche Lufthansa-1999-2018.png"},
            {"start_year": 2018, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Deutsche Lufthansa-2018-now.jpg"}
        ],
        "Air China": [{"start_year": 1999, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Air China-1999-now.png"}],
        "China Southern": [{"start_year": 1999, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/China Southern-1999-now.jpg"}],
        "China Eastern": [{"start_year": 1999, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/China Eastern-1999-now.jpg"}],
        "Singapore Airlines": [{"start_year": 1999, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Singapore Airlines-1999-now.jpg"}],
        "LATAM Airlines": [
            {"start_year": 1999, "end_year": 2016, "file": "../99.utility/airline-bar-video/logos/LATAM Airlines-1999-2016.png"},
            {"start_year": 2016, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/LATAM Airlines-2016-now.jpg"}
        ],
        "Hainan Airlines": [
            {"start_year": 1999, "end_year": 2004, "file": "../99.utility/airline-bar-video/logos/Hainan Airlines-1999-2004.png"},
            {"start_year": 2004, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Hainan Airlines-2004-now.jpg"}
        ],
        "Qatar Airways": [{"start_year": 1999, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Qatar Airways-1999-now.jpg"}],
        "Turkish Airlines": [
            {"start_year": 1999, "end_year": 2018, "file": "../99.utility/airline-bar-video/logos/Turkish Airlines-1999-2018.png"},
            {"start_year": 2018, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Turkish Airlines-2018-now.png"}
        ],
        "JetBlue": [{"start_year": 1999, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/jetBlue-1999-now.jpg"}],
        "SkyWest": [
            {"start_year": 1972, "end_year": 2001, "file": "../99.utility/airline-bar-video/logos/skywest-1972-2001.png"},
            {"start_year": 2001, "end_year": 2008, "file": "../99.utility/airline-bar-video/logos/skywest-2001-2008.png"},
            {"start_year": 2008, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/skywest-2018-now.jpg"}
        ],
        "Northwest Airlines": [
            {"start_year": 1989, "end_year": 2003, "file": "../99.utility/airline-bar-video/logos/northwest-airlines-1989-2003.png"},
            {"start_year": 2003, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/northwest-airlines-2003-now.jpg"}
        ],
        "TWA": [{"start_year": 1999, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/TWA-1999-now.png"}],
        "Air Canada": [
            {"start_year": 1995, "end_year": 2005, "file": "../99.utility/airline-bar-video/logos/air-canada-1995-2005.jpg"},
            {"start_year": 2005, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/air-canada-2005-now.png"}
        ],
        "IAG": [{"start_year": 1999, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/IAG-1999-now.png"}],
        "Ryanair": [
            {"start_year": 1999, "end_year": 2001, "file": "../99.utility/airline-bar-video/logos/Ryanair-1999-2001.png"},
            {"start_year": 2001, "end_year": 2013, "file": "../99.utility/airline-bar-video/logos/Ryanair-2001-2013.jpg"},
            {"start_year": 2013, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Ryanair-2013-now.jpg"}
        ],
        "Aeroflot": [
            {"start_year": 1999, "end_year": 2003, "file": "../99.utility/airline-bar-video/logos/Aeroflot-1999-2003.jpg"},
            {"start_year": 2003, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Aeroflot-2003-now.jpg"}
        ],
        "Cathay Pacific": [{"start_year": 1999, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Cathay Pacific-1999-now.png"}],
        "Qantas Airways": [{"start_year": 1999, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Qantas Airways-1999-now.jpg"}],
        "Finnair": [
            {"start_year": 1999, "end_year": 2010, "file": "../99.utility/airline-bar-video/logos/Finnair-1999-2010.jpg"},
            {"start_year": 2010, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Finnair-2010-now.jpg"}
        ],
        "Alaska Air": [
            {"start_year": 1972, "end_year": 2014, "file": "../99.utility/airline-bar-video/logos/alaska-air-1972-2014.png"},
            {"start_year": 2014, "end_year": 2016, "file": "../99.utility/airline-bar-video/logos/alaska-air-2014-2016.png"},
            {"start_year": 2016, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/alaska-air-2016-now.jpg"}
        ],
        "Norwegian": [{"start_year": 1999, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/norwegian-logo.jpg"}]
    }
    if airline not in logo_mapping:
        return None
    logo_versions = logo_mapping[airline]
    for version in logo_versions:
        if version["start_year"] <= year <= version["end_year"]:
            logo_path = version["file"]
            if os.path.exists(logo_path):
                return logo_path
    return None

def get_encoded_image(logo_path):
    try:
        if logo_path and os.path.exists(logo_path):
            with open(logo_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
                return f"data:image/png;base64,{encoded_string}"
    except Exception as e:
        print(f"Error encoding image {logo_path}: {e}")
    return None

# Load uploaded CSV
file_path = "../99.utility/../99.utility/airline-bar-video/airlines_final.csv"
df = pd.read_csv(file_path)

# Prepare metadata and revenue data
metadata = df.iloc[:7].copy()
revenue_data = df.iloc[7:].copy()
metadata.set_index(metadata.columns[0], inplace=True)

# Clean revenue data
for col in revenue_data.columns[1:]:
    revenue_data[col] = pd.to_numeric(revenue_data[col].str.replace(',', '').str.replace(' M', ''), errors='coerce')
revenue_data.set_index(revenue_data.columns[0], inplace=True)

# Define colors by region
region_colors = {
    'North America': '#40E0D0',
    'Europe': '#4169E1',
    'Asia Pacific': '#FF4B4B',
    'Latin America': '#32CD32',
    'China': '#FF4B4B',
    'Middle East': '#DEB887',
    'Russia': '#FF4B4B',
    'Turkey': '#DEB887'
}

# 只显示最新季度收入前15的公司
latest_quarter = revenue_data.index[-1]
top_airlines = revenue_data.loc[latest_quarter].sort_values(ascending=False).head(15).index.tolist()
revenue_data = revenue_data[top_airlines]
valid_airlines = top_airlines

# 打印有效的航空公司名称，用于调试
print("Valid airlines:", valid_airlines)

# 创建航空公司名称映射表，解决名称不一致问题
airline_name_mapping = {
    "Norwegian Air Shuttle": "Norwegian",  # 修复Norwegian名称不匹配问题
    "Deutsche Lufthansa": "Lufthansa"      # 修复Lufthansa名称不匹配问题
}

# 反向映射表，确保不会错误地显示映射的logo
reverse_mapping = {v: k for k, v in airline_name_mapping.items()}

# 根据映射表调整有效航空公司名称
mapped_valid_airlines = set()
for airline in valid_airlines:
    mapped_valid_airlines.add(airline)
    if airline in airline_name_mapping:
        mapped_valid_airlines.add(airline_name_mapping[airline])

# 打印所有有效的航空公司以及其映射名称
print("Valid airlines:", valid_airlines)
print("Mapped valid airlines:", mapped_valid_airlines)

# 生成插值后的数值型x轴
quarters = revenue_data.index.tolist()
quarter_numeric = np.arange(len(quarters))
interp_steps = 2  # 从10降低到5，减少总帧数，使动画更快
interp_x = np.linspace(0, len(quarters)-1, num=(len(quarters)-1)*interp_steps+1)

# 对每家公司的数据做线性插值（仅用于点）
interp_revenue = {}
for airline in valid_airlines:
    y = revenue_data[airline].values
    interp_y = np.interp(interp_x, quarter_numeric, y)
    interp_revenue[airline] = interp_y

# 计算全局y轴范围（所有帧所有airline的最大最小值）
all_y_values = []
for airline in valid_airlines:
    all_y_values.extend(interp_revenue[airline])
global_ymin = min(all_y_values)
global_ymax = max(all_y_values)

# Logo设置
fixed_x = 0.8  # 点固定在x轴80%位置
logo_offset = 0.05  # logo在点右侧的x偏移
logo_size = 0.05   # 减小logo高度（从0.08减小到0.05，约减少40%）

# 缓存所有航空公司的logo数据，避免重复加载
logo_cache = {}
airline_to_logo_map = {}  # 用于跟踪每个airline使用的是哪个logo

for airline in valid_airlines:
    # 检查是否需要映射航空公司名称
    lookup_names = [airline]
    if airline in airline_name_mapping:
        lookup_names.append(airline_name_mapping[airline])
    
    for lookup_name in lookup_names:
        for quarter_idx, quarter_str in enumerate(quarters):
            year = int(quarter_str[:4])
            iata_code = metadata.loc['IATA Code', airline] if 'IATA Code' in metadata.index else ''
            logo_path = get_logo_path(lookup_name, year, iata_code)
            if logo_path and logo_path not in logo_cache:
                logo_data = get_encoded_image(logo_path)
                if logo_data:
                    logo_cache[logo_path] = logo_data
                    # 记录airline与logo的对应关系
                    if airline not in airline_to_logo_map:
                        airline_to_logo_map[airline] = logo_path
                    
                    # 确保反向映射的航空公司不会错误地使用这个logo
                    if lookup_name in reverse_mapping and reverse_mapping[lookup_name] != airline:
                        print(f"ALERT: Prevented logo of {lookup_name} from being used by {reverse_mapping[lookup_name]}")

# 打印每个有效航空公司使用的logo
print("\nAirline to logo mapping:")
for airline, logo in sorted(airline_to_logo_map.items()):
    if airline in valid_airlines:
        print(f"{airline}: {logo}")

# 为每一帧计算所有航空公司的最大值
max_values_by_frame = []
for i in range(len(interp_x)):
    current_y_values = [interp_revenue[airline][i] for airline in valid_airlines]
    max_values_by_frame.append(max(current_y_values))

# 计算平滑的y轴上限
window_size = 10  # 平滑窗口大小
smoothed_max = []

# 在最大值序列前后添加填充，用于处理边界情况
padded_max = [max_values_by_frame[0]] * (window_size // 2) + max_values_by_frame + [max_values_by_frame[-1]] * (window_size // 2)

# 计算平滑的移动平均窗口
for i in range(len(max_values_by_frame)):
    start_idx = i
    end_idx = i + window_size
    window_avg = np.mean(padded_max[start_idx:end_idx])
    smoothed_max.append(window_avg)

# 增加一些上下边距
padding_factor = 0.1
y_max_with_padding = [val * (1 + padding_factor) for val in smoothed_max]

# 找出所有帧中的全局最小值
global_min_value = float('inf')
for i in range(len(interp_x)):
    current_y_values = [interp_revenue[airline][i] for airline in valid_airlines]
    frame_min = min(current_y_values)
    if frame_min < global_min_value:
        global_min_value = frame_min

# 确保最小值有足够的下方空间
min_y_buffer = abs(global_min_value) * 0.1 if global_min_value > 0 else abs(global_min_value) * 0.2
global_min_with_buffer = global_min_value - min_y_buffer

# 为所有帧使用统一的y轴下限，但使用平滑的上限
y_axis_ranges = [[global_min_with_buffer, y_max_with_padding[i]] for i in range(len(interp_x))]

# 计算每家航空公司首次出现非零数据的帧
first_data_frame = {}
for airline in valid_airlines:
    # 找到revenue_data中第一个非零、非NaN的值
    mask = (revenue_data[airline] > 0) & (~pd.isna(revenue_data[airline]))
    if mask.any():
        first_q_idx = np.where(mask)[0][0]  # 获取第一个非零索引
        first_q = quarters[first_q_idx]     # 获取对应的季度
        # 计算对应的帧号
        first_frame_idx = first_q_idx * interp_steps
        first_data_frame[airline] = first_frame_idx
    else:
        first_data_frame[airline] = float('inf')  # 如果没有有效数据，设为无穷大（不会显示）

# 打印每家航空公司首次出现数据的帧和季度，便于调试
print("\nFirst data appearance by airline:")
for airline in sorted(first_data_frame.keys()):
    frame_idx = first_data_frame[airline]
    if frame_idx < float('inf'):
        q_idx = int(frame_idx / interp_steps)
        quarter = quarters[q_idx] if q_idx < len(quarters) else "unknown"
        print(f"{airline}: frame {frame_idx}, quarter {quarter}")
    else:
        print(f"{airline}: never appears")

# 预计算每一帧每个航空公司的调整后位置
# 这将使得相邻帧之间的位置变化更平滑
adjusted_positions_by_frame = {}

# 首先收集每一帧每个航空公司的原始位置
original_positions = {}
for i in range(len(interp_x)):
    nearest_q_idx = min(int(round(interp_x[i])), len(quarters)-1)
    current_quarter = quarters[nearest_q_idx]
    
    frame_positions = {}
    for airline in valid_airlines:
        if i >= first_data_frame.get(airline, float('inf')):
            raw_val = revenue_data.at[current_quarter, airline] if current_quarter in revenue_data.index else None
            if not pd.isna(raw_val) and raw_val > 0:
                frame_positions[airline] = interp_revenue[airline][i]
    
    original_positions[i] = frame_positions

# 对每个航空公司，对其位置应用平滑
smoothed_positions = {}
for airline in valid_airlines:
    airline_positions = []
    for i in range(len(interp_x)):
        if airline in original_positions[i]:
            airline_positions.append((i, original_positions[i][airline]))
    
    # 如果航空公司至少在两帧中有数据，进行平滑处理
    if len(airline_positions) >= 2:
        frames, values = zip(*airline_positions)
        
        # 为所有帧创建平滑的位置序列
        all_frames = list(range(len(interp_x)))
        # 使用cubic spline插值确保平滑过渡
        from scipy.interpolate import CubicSpline
        if len(frames) > 3:  # 需要至少4个点才能使用三次样条
            cs = CubicSpline(frames, values)
            smoothed_values = cs(all_frames)
        else:  # 点太少，使用线性插值
            smoothed_values = np.interp(all_frames, frames, values)
        
        # 存储每帧的平滑位置
        for frame, value in zip(all_frames, smoothed_values):
            if frame in original_positions and airline in original_positions[frame]:
                if frame not in smoothed_positions:
                    smoothed_positions[frame] = {}
                smoothed_positions[frame][airline] = value

# 现在处理每一帧的重叠
for i in range(len(interp_x)):
    if i not in smoothed_positions:
        continue
    
    # 获取这一帧的所有航空公司和它们平滑后的位置
    airlines_in_frame = list(smoothed_positions[i].keys())
    y_values = [smoothed_positions[i][airline] for airline in airlines_in_frame]
    
    # 按y值排序
    sorted_indices = np.argsort(y_values)
    sorted_airlines = [airlines_in_frame[idx] for idx in sorted_indices]
    sorted_y_values = [y_values[idx] for idx in sorted_indices]
    
    # 计算这一帧的logo高度
    y_range = y_axis_ranges[i]
    y_range_size = y_range[1] - y_range[0]
    logo_height = logo_size * y_range_size
    min_required_gap = logo_height * 1.05
    
    # 调整位置以避免重叠
    adjusted_y_positions = list(sorted_y_values)
    for j in range(1, len(adjusted_y_positions)):
        curr_pos = adjusted_y_positions[j]
        prev_pos = adjusted_y_positions[j-1]
        
        # 检查是否需要移动以避免重叠
        min_gap_needed = min_required_gap
        if curr_pos - prev_pos < min_gap_needed:
            # 移动当前点，使其与前一个点保持最小间距
            adjusted_y_positions[j] = prev_pos + min_gap_needed
    
    # 确保所有位置都在y轴范围内
    y_min, y_max = y_axis_ranges[i]
    margin = logo_height / 2
    
    for j in range(len(adjusted_y_positions)):
        if adjusted_y_positions[j] - margin < y_min:
            adjusted_y_positions[j] = y_min + margin
        elif adjusted_y_positions[j] + margin > y_max:
            adjusted_y_positions[j] = y_max - margin
    
    # 存储调整后的位置
    adjusted_positions_by_frame[i] = {}
    for idx, airline in enumerate(sorted_airlines):
        adjusted_positions_by_frame[i][airline] = adjusted_y_positions[idx]

# 再次平滑调整后的位置，确保帧间的平滑过渡
final_positions = {}
for airline in valid_airlines:
    frames_with_airline = []
    positions = []
    
    for i in range(len(interp_x)):
        if i in adjusted_positions_by_frame and airline in adjusted_positions_by_frame[i]:
            frames_with_airline.append(i)
            positions.append(adjusted_positions_by_frame[i][airline])
    
    # 如果航空公司在多个帧中出现，平滑其位置
    if len(frames_with_airline) > 1:
        # 使用更小的窗口平滑
        window_size = min(5, len(frames_with_airline))
        if window_size > 1:
            smoothed = np.convolve(positions, np.ones(window_size)/window_size, mode='valid')
            padded_smoothed = [positions[0]] * (window_size//2) + list(smoothed) + [positions[-1]] * ((window_size-1)//2)
            
            # 存储最终平滑后的位置
            for frame_idx, frame in enumerate(frames_with_airline):
                if frame not in final_positions:
                    final_positions[frame] = {}
                final_positions[frame][airline] = padded_smoothed[frame_idx]
        else:
            # 如果窗口大小为1，直接使用原始位置
            for frame_idx, frame in enumerate(frames_with_airline):
                if frame not in final_positions:
                    final_positions[frame] = {}
                final_positions[frame][airline] = positions[frame_idx]

# 生成动画帧，使用最终平滑的位置
frames = []
for i in range(len(interp_x)):
    frame_data = []
    
    # 获取当前帧的时间点
    nearest_q_idx = min(int(round(interp_x[i])), len(quarters)-1)
    current_quarter = quarters[nearest_q_idx]
    current_year = int(current_quarter[:4])
    
    # 为每个航空公司生成线和点
    for airline in valid_airlines:
        # 线的x坐标：从0到fixed_x，y坐标为历史到当前
        x_hist = np.linspace(0, fixed_x, i+1)
        y_hist = interp_revenue[airline][:i+1]
        region = metadata.loc['Region', airline] if airline in metadata.columns else 'Unknown'
        color = region_colors.get(region, '#808080')
        
        frame_data.append(go.Scatter(
            x=x_hist, 
            y=y_hist, 
            mode='lines', 
            name=airline,
            line=dict(color=color), 
            hoverinfo='skip', 
            showlegend=False
        ))
        
        # 点固定在fixed_x，y为当前帧y
        current_y = interp_revenue[airline][i]
        frame_data.append(go.Scatter(
            x=[fixed_x], 
            y=[current_y], 
            mode='markers', 
            name=airline,
            marker=dict(color=color, size=12), 
            hoverinfo='text+y', 
            text=[current_quarter], 
            showlegend=False
        ))
    
    # 收集当前帧所有有效的y值和对应的航空公司
    valid_y_values = []
    valid_airlines_in_frame = []
    
    for airline in valid_airlines:
        # 只考虑当前帧有效的航空公司
        if i >= first_data_frame.get(airline, float('inf')):
            # 获取当前帧对应的原始季度
            raw_val = revenue_data.at[current_quarter, airline] if current_quarter in revenue_data.index else None
            
            # 如果这一季度有有效数据，记录这个航空公司和它的y值
            if not pd.isna(raw_val) and raw_val > 0:
                # 使用平滑调整后的位置
                if i in final_positions and airline in final_positions[i]:
                    y_val = final_positions[i][airline]
                else:
                    y_val = interp_revenue[airline][i]
                valid_y_values.append(y_val)
                valid_airlines_in_frame.append(airline)
    
    # 按y值对航空公司进行排序（从小到大）
    sorted_indices = np.argsort(valid_y_values)
    sorted_airlines = [valid_airlines_in_frame[idx] for idx in sorted_indices]
    sorted_y_values = [valid_y_values[idx] for idx in sorted_indices]
    
    # 计算logo高度（基于当前y轴范围）
    y_range = y_axis_ranges[i]
    y_range_size = y_range[1] - y_range[0]
    logo_height = logo_size * y_range_size
    
    # 为当前帧生成logo images
    images_i = []
    for idx, airline in enumerate(sorted_airlines):
        # 获取对应的logo
        if airline in airline_to_logo_map:
            logo_path = airline_to_logo_map[airline]
            if logo_path in logo_cache:
                logo_data = logo_cache[logo_path]
                
                # 使用平滑调整后的位置
                adjusted_y = sorted_y_values[idx]
                
                images_i.append(dict(
                    source=logo_data,
                    xref="x", yref="y",
                    x=fixed_x + logo_offset, 
                    y=adjusted_y,
                    sizex=logo_offset, 
                    sizey=logo_height,
                    xanchor="left", 
                    yanchor="middle",
                    sizing="contain",
                    opacity=1,
                    layer="above"
                ))
    
    # 将当前帧的数据、images和平滑的y轴范围打包到Frame中
    frames.append(go.Frame(
        data=frame_data, 
        name=str(i),
        layout=go.Layout(
            images=images_i,
            yaxis=dict(
                range=y_axis_ranges[i],  # 使用平滑的y轴范围
                title='Revenue (Million USD)',
                linecolor='gray', 
                showgrid=True, 
                gridcolor='lightgray', 
                griddash='dash', 
                zeroline=False
            )
        )
    ))

# 初始帧数据
initial_data = []
for airline in valid_airlines:
    x_hist = np.linspace(0, fixed_x, 1)
    y_hist = interp_revenue[airline][:1]
    region = metadata.loc['Region', airline] if airline in metadata.columns else 'Unknown'
    color = region_colors.get(region, '#808080')
    
    initial_data.append(go.Scatter(
        x=x_hist, 
        y=y_hist, 
        mode='lines', 
        name=airline,
        line=dict(color=color), 
        hoverinfo='skip', 
        showlegend=False
    ))
    
    initial_data.append(go.Scatter(
        x=[fixed_x], 
        y=[interp_revenue[airline][0]], 
        mode='markers', 
        name=airline,
        marker=dict(color=color, size=12), 
        hoverinfo='text+y', 
        text=[quarters[0]], 
        showlegend=False
    ))

# 收集初始帧所有有效的y值和对应的航空公司
valid_y_values_initial = []
valid_airlines_in_initial_frame = []

for airline in valid_airlines:
    # 只考虑初始帧有效的航空公司
    if 0 >= first_data_frame.get(airline, float('inf')):
        # 获取初始帧对应的原始季度
        initial_quarter = quarters[0]
        raw_val = revenue_data.at[initial_quarter, airline] if initial_quarter in revenue_data.index else None
        
        # 如果这一季度有有效数据，记录这个航空公司和它的y值
        if not pd.isna(raw_val) and raw_val > 0:
            # 使用平滑调整后的位置
            if 0 in final_positions and airline in final_positions[0]:
                y_val = final_positions[0][airline]
            else:
                y_val = interp_revenue[airline][0]
            valid_y_values_initial.append(y_val)
            valid_airlines_in_initial_frame.append(airline)

# 按y值对初始帧的航空公司进行排序（从小到大）
sorted_indices_initial = np.argsort(valid_y_values_initial)
sorted_airlines_initial = [valid_airlines_in_initial_frame[idx] for idx in sorted_indices_initial]
sorted_y_values_initial = [valid_y_values_initial[idx] for idx in sorted_indices_initial]

# 计算初始帧logo高度
initial_y_range = y_axis_ranges[0]
initial_y_range_size = initial_y_range[1] - initial_y_range[0]
initial_logo_height = logo_size * initial_y_range_size

# 初始帧logo images
initial_images = []
for idx, airline in enumerate(sorted_airlines_initial):
    # 获取对应的logo
    if airline in airline_to_logo_map:
        logo_path = airline_to_logo_map[airline]
        if logo_path in logo_cache:
            logo_data = logo_cache[logo_path]
            
            # 使用平滑调整后的位置
            adjusted_y = sorted_y_values_initial[idx]
            
            initial_images.append(dict(
                source=logo_data,
                xref="x", yref="y",
                x=fixed_x + logo_offset, 
                y=adjusted_y,
                sizex=logo_offset, 
                sizey=initial_logo_height,
                xanchor="left", 
                yanchor="middle",
                sizing="contain",
                opacity=1,
                layer="above"
            ))

# Build figure
fig = go.Figure(
    data=initial_data,
    layout=go.Layout(
        title='Airline Revenue Over Time',
        xaxis=dict(
            title='', 
            range=[0, 1], 
            linecolor='gray', 
            showgrid=False, 
            zeroline=False, 
            showticklabels=False
        ),
        yaxis=dict(
            title='Revenue (Million USD)', 
            range=y_axis_ranges[0],  # 使用平滑后的y轴范围
            linecolor='gray', 
            showgrid=True, 
            gridcolor='lightgray', 
            griddash='dash', 
            zeroline=False
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        images=initial_images,
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            y=1.15,
            x=1.05,
            xanchor="right",
            yanchor="top",
            buttons=[
                dict(label="Play",
                     method="animate",
                     args=[None, {
                         "frame": {"duration": 100, "redraw": True},
                         "fromcurrent": True, 
                         "transition": {"duration": 50}  # 增加过渡时间，让动画更平滑
                     }]),
                dict(label="Pause",
                     method="animate",
                     args=[[None], {
                         "frame": {"duration": 0, "redraw": False},
                         "mode": "immediate",
                         "transition": {"duration": 0}
                     }])
            ]
        )],
        sliders=[]
    ),
    frames=frames
)

# 设置全局默认的frame和transition参数，确保自动播放也能平滑进行
fig.update(
    layout_updatemenus=[
        {
            "buttons": [
                {
                    "args": [None, {"frame": {"duration": 100, "redraw": True}, "transition": {"duration": 50}}],
                    "label": "Play",
                    "method": "animate"
                },
                {
                    "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate", "transition": {"duration": 0}}],
                    "label": "Pause",
                    "method": "animate"
                }
            ],
            "showactive": False,
            "type": "buttons",
            "x": 1.05,
            "y": 1.15,
            "xanchor": "right",
            "yanchor": "top"
        }
    ]
)

# Save HTML with embedded plotly.js to ensure consistent playback
output_file = "output/airline_revenue_linechart.html"
pio.write_html(fig, file=output_file, auto_open=True, include_plotlyjs='embed', auto_play=True)
print(f"Animation saved to {output_file}")