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

# 固定 y 轴下限（只计算一次）
global_min_value = float('inf')
for i in range(len(interp_x)):
    current_y_values = [interp_revenue[airline][i] for airline in valid_airlines]
    frame_min = min(current_y_values)
    if frame_min < global_min_value:
        global_min_value = frame_min

# 确保最小值有足够的下方空间
min_y_buffer = abs(global_min_value) * 0.1 if global_min_value > 0 else abs(global_min_value) * 0.2
global_min_with_buffer = global_min_value - min_y_buffer

# 简化 y 轴上限平滑计算
max_values_by_frame = [
    max([interp_revenue[airline][i] for airline in valid_airlines])
    for i in range(len(interp_x))
]

# 检测并修正异常值（防止突然的峰值导致跳跃）
def detect_and_fix_outliers(values, threshold=1.5):
    """检测并平滑异常值，避免突然跳跃"""
    smoothed = values.copy()
    for i in range(2, len(values)-2):
        # 计算当前点与前后点的变化率
        prev_rate = values[i] / max(values[i-1], 0.001)  # 避免除零
        next_rate = values[i+1] / max(values[i], 0.001)
        
        # 如果变化率超过阈值，且下一帧又恢复，则可能是孤立峰值
        if (prev_rate > threshold and next_rate < 1/threshold) or \
           (prev_rate < 1/threshold and next_rate > threshold):
            # 使用前后点的中间值平滑
            smoothed[i] = (values[i-1] + values[i+1]) / 2
    return smoothed

# 应用异常值检测和修正
max_values_by_frame = detect_and_fix_outliers(max_values_by_frame)

# 增强平滑强度 - 使用更大的窗口和更强的权重
window_size = 25  # 增加窗口大小，让平滑更强
padded_max = [max_values_by_frame[0]] * (window_size // 2) + max_values_by_frame + [max_values_by_frame[-1]] * (window_size // 2)

smoothed_y_max = []
for i in range(len(max_values_by_frame)):
    window = padded_max[i:i+window_size]
    # 使用高斯权重，中心权重更强
    weights = np.exp(-0.3 * np.linspace(-3, 3, window_size)**2)  # 更平坦的权重分布
    avg = np.sum(np.array(window) * weights) / np.sum(weights)
    smoothed_y_max.append(avg * 1.15)  # 增加顶部padding到15%，确保空间足够

# 再次平滑处理，确保曲线绝对光滑
double_smoothed_y_max = []
window_size_2 = 15
padded_smooth = [smoothed_y_max[0]] * (window_size_2 // 2) + smoothed_y_max + [smoothed_y_max[-1]] * (window_size_2 // 2)

for i in range(len(smoothed_y_max)):
    window = padded_smooth[i:i+window_size_2]
    weights = np.exp(-0.5 * np.linspace(-2, 2, window_size_2)**2)
    avg = np.sum(np.array(window) * weights) / np.sum(weights)
    double_smoothed_y_max.append(avg)

# 使用最终双重平滑后的结果
smoothed_y_max = double_smoothed_y_max

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
            # 使用自然样条边界条件确保更平滑的过渡
            cs = CubicSpline(frames, values, bc_type='natural')
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
min_displacement_factor = 0.3  # 减少位移量，避免过度调整
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
    y_range = [global_min_with_buffer, smoothed_y_max[i]]  # 使用新的固定下限和动态上限
    y_range_size = y_range[1] - y_range[0]
    logo_height = logo_size * y_range_size
    min_required_gap = logo_height * 1.05
    
    # 调整位置以避免重叠，但减小调整幅度
    adjusted_y_positions = list(sorted_y_values)
    for j in range(1, len(adjusted_y_positions)):
        curr_pos = adjusted_y_positions[j]
        prev_pos = adjusted_y_positions[j-1]
        
        # 检查是否需要移动以避免重叠
        if curr_pos - prev_pos < min_required_gap:
            # 计算需要移动的距离
            move_distance = min_required_gap - (curr_pos - prev_pos)
            # 使用较小的位移因子，使调整更平滑
            adjusted_move = move_distance * min_displacement_factor
            # 移动当前点，使其与前一个点保持最小间距
            adjusted_y_positions[j] = prev_pos + min_required_gap - (min_required_gap - (curr_pos - prev_pos)) * (1 - min_displacement_factor)
    
    # 确保所有位置都在y轴范围内
    y_min, y_max = y_range
    margin = logo_height / 2
    
    for j in range(len(adjusted_y_positions)):
        if adjusted_y_positions[j] - margin < y_min:
            adjusted_y_positions[j] = y_min + margin
        elif adjusted_y_positions[j] + margin > y_max:
            adjusted_y_positions[j] = y_max - margin
    
    # 存储调整后的位置
    adjusted_positions_by_frame[i] = {}
    for idx, airline in enumerate(sorted_airlines):
        # 添加一个小的偏移量，使位置更平稳
        original_pos = sorted_y_values[idx]
        new_pos = adjusted_y_positions[idx]
        
        # 使用更渐进的调整（部分原始值，部分调整值）
        blend_factor = 0.7  # 较大的blend_factor会使调整更加渐进
        blended_pos = original_pos * blend_factor + new_pos * (1-blend_factor)
        
        adjusted_positions_by_frame[i][airline] = blended_pos

# 为每个航空公司跨帧平滑位置变化
final_positions = {}

# 增加平滑窗口大小，使运动更连贯
for airline in valid_airlines:
    frames_with_airline = []
    positions = []
    
    for i in range(len(interp_x)):
        if i in adjusted_positions_by_frame and airline in adjusted_positions_by_frame[i]:
            frames_with_airline.append(i)
            positions.append(adjusted_positions_by_frame[i][airline])
    
    # 如果航空公司在多个帧中出现，平滑其位置
    if len(frames_with_airline) > 1:
        # 使用更大的窗口平滑，增加平滑效果
        window_size = min(25, len(frames_with_airline))  # 增加窗口大小从15到25
        if window_size > 1:
            # 使用加权平均，中心点权重最高
            weights = np.concatenate([
                np.arange(1, window_size//2 + 1),
                [window_size//2 + 1],
                np.arange(window_size//2, 0, -1)
            ])
            weights = weights / np.sum(weights)
            
            # 对位置数据应用滑动加权平均
            smoothed = np.convolve(positions, weights, mode='valid')
            padded_smoothed = [positions[0]] * (window_size//2) + list(smoothed) + [positions[-1]] * ((window_size-1)//2)
            
            # 存储最终平滑后的位置
            for frame_idx, frame in enumerate(frames_with_airline):
                if frame not in final_positions:
                    final_positions[frame] = {}
                
                # 混合原始位置和平滑位置
                original_pos = positions[frame_idx]
                smoothed_pos = padded_smoothed[frame_idx]
                
                # 使用更强的平滑，减少原始值的权重
                blend_factor = 0.4  # 降低blend_factor，增加平滑效果
                blended_pos = original_pos * blend_factor + smoothed_pos * (1-blend_factor)
                
                final_positions[frame][airline] = blended_pos
        else:
            # 如果窗口大小为1，直接使用原始位置
            for frame_idx, frame in enumerate(frames_with_airline):
                if frame not in final_positions:
                    final_positions[frame] = {}
                final_positions[frame][airline] = positions[frame_idx]

# 设置每一帧的持续时间，让动画更平滑
frame_duration = 70  # 进一步缩短每帧持续时间，让动画更流畅
frame_transition = 0  # 将过渡时间设为0，强制立即更新所有元素

# 重新创建帧，使用预计算的布局，确保y轴和数据点同步移动
frames = []
for i in range(len(interp_x)):
    frame_data = []
    
    # 获取当前帧的时间点
    nearest_q_idx = min(int(round(interp_x[i])), len(quarters)-1)
    current_quarter = quarters[nearest_q_idx]
    
    # 收集当前帧的所有logo位置，与数据点保持一致
    frame_logos = []
    logo_positions = {}
    
    # 为每个航空公司生成线和点
    for airline in valid_airlines:
        # 线的x坐标：从0到fixed_x
        x_hist = np.linspace(0, fixed_x, i+1)
        
        # 为线创建y坐标，确保最后一个点与平滑后的marker位置一致
        y_hist = list(interp_revenue[airline][:i])  # 前i个点使用原始插值
        
        # 获取当前点的y值，优先使用平滑后的位置以保持与marker同步
        current_y = interp_revenue[airline][i]
        if i in final_positions and airline in final_positions[i]:
            current_y = final_positions[i][airline]
            
        # 将当前点添加到线的历史中，确保线与marker精确对齐
        y_hist.append(current_y)
        
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
        
        # 使用平滑调整后的位置绘制点
        if i in final_positions and airline in final_positions[i]:
            # 保存当前航空公司的logo位置，与数据点保持一致
            logo_positions[airline] = current_y
            
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
    
    # 为当前帧直接使用数据点的位置生成logo
    if logo_positions:
        # 按y值排序
        sorted_airlines = sorted(logo_positions.keys(), key=lambda a: logo_positions[a])
        
        # 计算logo高度
        y_range = [global_min_with_buffer, smoothed_y_max[i]]  # 使用新的固定下限和动态上限
        y_range_size = y_range[1] - y_range[0]
        logo_height = logo_size * y_range_size
        
        # 生成logo images，直接使用数据点的位置
        for airline in sorted_airlines:
            if airline in airline_to_logo_map:
                logo_path = airline_to_logo_map[airline]
                if logo_path in logo_cache:
                    logo_data = logo_cache[logo_path]
                    y_val = logo_positions[airline]
                    
                    # 确保y值在有效范围内，避免logo闪烁
                    y_val = max(global_min_with_buffer, min(y_val, smoothed_y_max[i]))
                    
                    frame_logos.append(dict(
                        source=logo_data,
                        xref="x", yref="y",
                        x=fixed_x + logo_offset, 
                        y=y_val,
                        sizex=logo_offset, 
                        sizey=logo_height,
                        xanchor="left", 
                        yanchor="middle",
                        sizing="contain",
                        opacity=1,
                        layer="above"
                    ))
    
    # 创建当前帧的自定义布局，使用固定下限和动态上限
    custom_layout = go.Layout(
        yaxis=dict(
            range=[global_min_with_buffer, smoothed_y_max[i]],  # 下限固定，上限动态
            title='Revenue (Million USD)',
            linecolor='gray', 
            showgrid=True, 
            gridcolor='lightgray', 
            griddash='dash', 
            zeroline=False
        ),
        images=frame_logos
    )
    
    # 将当前帧的数据和布局添加到frames
    frames.append(go.Frame(
        data=frame_data, 
        name=str(i),
        layout=custom_layout
    ))

# 初始帧数据
initial_data = []
for airline in valid_airlines:
    x_hist = np.linspace(0, fixed_x, 1)
    
    # 获取初始位置，优先使用平滑后的值
    initial_y = interp_revenue[airline][0]
    if 0 in final_positions and airline in final_positions[0]:
        initial_y = final_positions[0][airline]
        
    y_hist = [initial_y]  # 确保初始帧线与点同步
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
        y=[initial_y], 
        mode='markers', 
        name=airline,
        marker=dict(color=color, size=12), 
        hoverinfo='text+y', 
        text=[quarters[0]], 
        showlegend=False
    ))

# 初始帧logo images - 直接使用数据点的位置
initial_images = []
initial_logo_positions = {}

# 收集初始帧的logo位置
for airline in valid_airlines:
    if 0 >= first_data_frame.get(airline, float('inf')):
        initial_quarter = quarters[0]
        raw_val = revenue_data.at[initial_quarter, airline] if initial_quarter in revenue_data.index else None
        
        if not pd.isna(raw_val) and raw_val > 0:
            # 使用与数据点完全相同的位置
            if 0 in final_positions and airline in final_positions[0]:
                y_val = final_positions[0][airline]
            else:
                y_val = interp_revenue[airline][0]
            initial_logo_positions[airline] = y_val

# 按y值排序
if initial_logo_positions:
    sorted_airlines = sorted(initial_logo_positions.keys(), key=lambda a: initial_logo_positions[a])
    
    # 计算logo高度，使用固定下限和动态上限
    initial_y_range = [global_min_with_buffer, smoothed_y_max[0]]
    initial_y_range_size = initial_y_range[1] - initial_y_range[0]
    initial_logo_height = logo_size * initial_y_range_size
    
    # 生成logo images
    for airline in sorted_airlines:
        if airline in airline_to_logo_map:
            logo_path = airline_to_logo_map[airline]
            if logo_path in logo_cache:
                logo_data = logo_cache[logo_path]
                
                # 使用与数据点完全相同的位置
                y_val = initial_logo_positions[airline]
                
                initial_images.append(dict(
                    source=logo_data,
                    xref="x", yref="y",
                    x=fixed_x + logo_offset, 
                    y=y_val,
                    sizex=logo_offset, 
                    sizey=initial_logo_height,
                    xanchor="left", 
                    yanchor="middle",
                    sizing="contain",
                    opacity=1,
                    layer="above"
                ))

# Build figure，使用固定下限和动态上限
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
            range=[global_min_with_buffer, smoothed_y_max[0]],  # 下限固定，上限动态
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
                         "frame": {"duration": frame_duration, "redraw": True},
                         "fromcurrent": True, 
                         "transition": {"duration": 0, "easing": "linear"},
                         "mode": "immediate"
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
                    "args": [None, {
                        "frame": {"duration": frame_duration, "redraw": True}, 
                        "transition": {"duration": 0, "easing": "linear"},
                        "mode": "immediate",
                        "fromcurrent": True
                    }],
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
    ],
    layout={
        "transition": {"duration": 0},  # 强制所有布局变化立即生效
        "yaxis": {
            "range": [global_min_with_buffer, smoothed_y_max[0]],  # 确保y轴范围初始化正确
            "autorange": False   # 防止自动调整范围
        }
    }
)

# 确保动画完全同步，使用特定的animate参数
for i, frame in enumerate(frames):
    frame.layout.datarevision = i  # 给每一帧添加唯一的数据修订号
    # 防止任何自动调整y轴范围
    if "yaxis" in frame.layout:
        frame.layout.yaxis.autorange = False

# 预加载所有图片，减少logo闪烁
all_logos = {}
for i, frame in enumerate(frames):
    if hasattr(frame.layout, "images") and frame.layout.images:
        for img in frame.layout.images:
            img_key = f"{img.source}_{img.x}_{img.y}"
            all_logos[img_key] = img

# Save HTML with embedded plotly.js to ensure consistent playback
output_file = "output/airline_revenue_linechart.html"
pio.write_html(fig, file=output_file, auto_open=True, include_plotlyjs='embed', auto_play=False, config={
    'responsive': True,
    'showAxisDragHandles': False,  # 禁用坐标轴拖动，避免用户交互影响动画
    'staticPlot': False,           # 动态图
    'doubleClick': 'reset',        # 双击重置视图
    'displayModeBar': False,       # 隐藏模式栏
    'displaylogo': False,          # 不显示plotly logo
    'toImageButtonOptions': {
        'format': 'png',           # 保存为png
        'width': 1200,
        'height': 800,
        'scale': 2                 # 高分辨率
    }
})
print(f"Animation saved to {output_file}")