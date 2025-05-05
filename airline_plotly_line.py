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
        "easyJet": [{"start_year": 1999, "end_year": 9999, "file": "airline-bar-video/logos/easyJet-1999-now.jpg"}],
        "Emirates": [{"start_year": 1999, "end_year": 9999, "file": "airline-bar-video/logos/Emirates-logo.jpg"}],
        "Air France-KLM": [
            {"start_year": 1999, "end_year": 2004, "file": "airline-bar-video/logos/klm-1999-now.png", "iata": "KL"},
            {"start_year": 2004, "end_year": 9999, "file": "airline-bar-video/logos/Air-France-KLM-Holding-Logo.png", "iata": "AF"}
        ],
        "American Airlines": [
            {"start_year": 1999, "end_year": 2013, "file": "airline-bar-video/logos/american-airlines-1967-2013.jpg"},
            {"start_year": 2013, "end_year": 9999, "file": "airline-bar-video/logos/american-airlines-2013-now.jpg"}
        ],
        "United Airlines": [
            {"start_year": 1998, "end_year": 2010, "file": "airline-bar-video/logos/united-airlines-1998-2010.jpg"},
            {"start_year": 2010, "end_year": 9999, "file": "airline-bar-video/logos/united-airlines-2010-now.jpg"}
        ],
        "Delta Air Lines": [
            {"start_year": 2000, "end_year": 2007, "file": "airline-bar-video/logos/delta-air-lines-2000-2007.png"},
            {"start_year": 2007, "end_year": 9999, "file": "airline-bar-video/logos/delta-air-lines-2007-now.jpg"}
        ],
        "Southwest Airlines": [
            {"start_year": 1989, "end_year": 2014, "file": "airline-bar-video/logos/southwest-airlines-1989-2014.png"},
            {"start_year": 2014, "end_year": 9999, "file": "airline-bar-video/logos/southwest-airlines-2014-now.png"}
        ],
        "Lufthansa": [
            {"start_year": 1999, "end_year": 2018, "file": "airline-bar-video/logos/Deutsche Lufthansa-1999-2018.png"},
            {"start_year": 2018, "end_year": 9999, "file": "airline-bar-video/logos/Deutsche Lufthansa-2018-now.jpg"}
        ],
        "Deutsche Lufthansa": [
            {"start_year": 1999, "end_year": 2018, "file": "airline-bar-video/logos/Deutsche Lufthansa-1999-2018.png"},
            {"start_year": 2018, "end_year": 9999, "file": "airline-bar-video/logos/Deutsche Lufthansa-2018-now.jpg"}
        ],
        "Air China": [{"start_year": 1999, "end_year": 9999, "file": "airline-bar-video/logos/Air China-1999-now.png"}],
        "China Southern": [{"start_year": 1999, "end_year": 9999, "file": "airline-bar-video/logos/China Southern-1999-now.jpg"}],
        "China Eastern": [{"start_year": 1999, "end_year": 9999, "file": "airline-bar-video/logos/China Eastern-1999-now.jpg"}],
        "Singapore Airlines": [{"start_year": 1999, "end_year": 9999, "file": "airline-bar-video/logos/Singapore Airlines-1999-now.jpg"}],
        "LATAM Airlines": [
            {"start_year": 1999, "end_year": 2016, "file": "airline-bar-video/logos/LATAM Airlines-1999-2016.png"},
            {"start_year": 2016, "end_year": 9999, "file": "airline-bar-video/logos/LATAM Airlines-2016-now.jpg"}
        ],
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
            {"start_year": 2008, "end_year": 9999, "file": "airline-bar-video/logos/skywest-2018-now.jpg"}
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
        "Cathay Pacific": [{"start_year": 1999, "end_year": 9999, "file": "airline-bar-video/logos/Cathay Pacific-1999-now.png"}],
        "Qantas Airways": [{"start_year": 1999, "end_year": 9999, "file": "airline-bar-video/logos/Qantas Airways-1999-now.jpg"}],
        "Finnair": [
            {"start_year": 1999, "end_year": 2010, "file": "airline-bar-video/logos/Finnair-1999-2010.jpg"},
            {"start_year": 2010, "end_year": 9999, "file": "airline-bar-video/logos/Finnair-2010-now.jpg"}
        ],
        "Alaska Air": [
            {"start_year": 1972, "end_year": 2014, "file": "airline-bar-video/logos/alaska-air-1972-2014.png"},
            {"start_year": 2014, "end_year": 2016, "file": "airline-bar-video/logos/alaska-air-2014-2016.png"},
            {"start_year": 2016, "end_year": 9999, "file": "airline-bar-video/logos/alaska-air-2016-now.jpg"}
        ],
        "Norwegian": [{"start_year": 1999, "end_year": 9999, "file": "airline-bar-video/logos/norwegian-logo.jpg"}]
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
file_path = "./airline-bar-video/airlines_final.csv"
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

# 为每一帧计算y轴范围（根据当前帧的数据动态调整）
all_frame_y_ranges = []
for i in range(len(interp_x)):
    current_y_values = [interp_revenue[airline][i] for airline in valid_airlines]
    ymin = min(current_y_values)
    ymax = max(current_y_values)
    
    # 添加少量缓冲，但保持轴范围紧凑
    y_buffer = (ymax - ymin) * 0.05
    
    # 确保不同点之间有足够空间显示logo
    # 计算最小间距
    sorted_y = sorted(current_y_values)
    min_gap = float('inf')
    for j in range(1, len(sorted_y)):
        gap = sorted_y[j] - sorted_y[j-1]
        if gap < min_gap:
            min_gap = gap
    
    # 如果点之间的最小间距太小，适当扩大y轴范围
    if min_gap < (ymax - ymin) * 0.1 and len(current_y_values) > 5:
        y_buffer = (ymax - ymin) * 0.15
    
    all_frame_y_ranges.append([ymin - y_buffer, ymax + y_buffer])

# 找出所有帧中的全局最小值，确保所有线条都可见
global_min_value = float('inf')
for i in range(len(interp_x)):
    current_y_values = [interp_revenue[airline][i] for airline in valid_airlines]
    frame_min = min(current_y_values)
    if frame_min < global_min_value:
        global_min_value = frame_min

# 确保最小值有足够的下方空间
min_y_buffer = abs(global_min_value) * 0.1 if global_min_value > 0 else abs(global_min_value) * 0.2
global_min_with_buffer = global_min_value - min_y_buffer

# 双速率"即时扩张 + 慢速收缩"生成动态范围
decay = 0.05    # 收缩系数：越小收缩越慢
dyn_high = all_frame_y_ranges[0][1]
dyn_low = min(all_frame_y_ranges[0][0], global_min_with_buffer)  # 使用全局最小值或第一帧最小值的较小者
dyn_ranges = [[dyn_low, dyn_high]]

for low, high in all_frame_y_ranges[1:]:
    # 如果new high > 现有dyn_high，就立刻扩张到new high；否则只慢慢收缩
    dyn_high = high if high > dyn_high else dyn_high*(1-decay) + high*decay
    
    # 确保下限始终不高于全局最小值（带缓冲）
    adjusted_low = min(low, global_min_with_buffer)
    
    # 对下限应用双速率规则：如果新下限低于当前下限，立即扩展；否则慢慢抬升
    dyn_low = adjusted_low if adjusted_low < dyn_low else dyn_low*(1-decay) + adjusted_low*decay
    
    dyn_ranges.append([dyn_low, dyn_high])

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

# 生成动画帧，每帧使用动态的y轴范围
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
                y_val = interp_revenue[airline][i]
                valid_y_values.append(y_val)
                valid_airlines_in_frame.append(airline)
    
    # 按y值对航空公司进行排序（从小到大）
    sorted_indices = np.argsort(valid_y_values)
    sorted_airlines = [valid_airlines_in_frame[idx] for idx in sorted_indices]
    sorted_y_values = [valid_y_values[idx] for idx in sorted_indices]
    
    # 计算logo高度（基于当前y轴范围）
    y_range = dyn_ranges[i]
    y_range_size = y_range[1] - y_range[0]
    logo_height = logo_size * y_range_size
    
    # 调整logo位置，避免重叠
    adjusted_y_positions = list(sorted_y_values)  # 初始位置与数据点相同
    
    # 第一步：计算理想间距和每个点的影响范围
    min_required_gap = logo_height * 1.05  # 减小最小所需间距（从1.1减到1.05）
    logo_influences = []  # 存储每个logo的影响范围[下边界, 上边界]

    for pos in adjusted_y_positions:
        half_gap = min_required_gap / 2
        logo_influences.append([pos - half_gap, pos + half_gap])

    # 第二步：检测并修复重叠
    has_overlap = True
    max_iterations = 10  # 防止无限循环
    iteration = 0

    while has_overlap and iteration < max_iterations:
        has_overlap = False
        iteration += 1
        
        # 从第二个logo开始，向上检查重叠
        for j in range(1, len(logo_influences)):
            # 当前logo与上一个logo的重叠
            curr_lower = logo_influences[j][0]
            prev_upper = logo_influences[j-1][1]
            
            if curr_lower < prev_upper:  # 存在重叠
                has_overlap = True
                overlap_amount = prev_upper - curr_lower
                
                # 向上或向下移动以解决重叠
                # 如果当前logo更接近顶部或前一个logo更接近底部，则向下移动前一个logo
                # 否则向上移动当前logo
                if j < len(logo_influences) / 2:  # 前半部分倾向于向下移动
                    # 向下移动前一个logo
                    shift = -overlap_amount - 0.01 * logo_height  # 额外一点空间
                    logo_influences[j-1][0] += shift
                    logo_influences[j-1][1] += shift
                    adjusted_y_positions[j-1] += shift
                else:  # 后半部分倾向于向上移动
                    # 向上移动当前logo
                    shift = overlap_amount + 0.01 * logo_height  # 额外一点空间
                    logo_influences[j][0] += shift
                    logo_influences[j][1] += shift
                    adjusted_y_positions[j] += shift

    # 第三步：确保所有logo都在视图范围内
    # 获取当前y轴范围
    y_min, y_max = dyn_ranges[i]
    margin = logo_height / 2  # logo中心点到边缘的距离

    # 检查所有logo是否在视图范围内
    for j in range(len(adjusted_y_positions)):
        if adjusted_y_positions[j] - margin < y_min:
            # logo底部超出下边界
            adjusted_y_positions[j] = y_min + margin + 0.01 * logo_height
        elif adjusted_y_positions[j] + margin > y_max:
            # logo顶部超出上边界
            adjusted_y_positions[j] = y_max - margin - 0.01 * logo_height

    # 为当前帧生成logo images
    images_i = []
    for idx, airline in enumerate(sorted_airlines):
        # 获取对应的logo
        if airline in airline_to_logo_map:
            logo_path = airline_to_logo_map[airline]
            if logo_path in logo_cache:
                logo_data = logo_cache[logo_path]
                
                # 使用调整后的y位置
                adjusted_y = adjusted_y_positions[idx]
                
                images_i.append(dict(
                    source=logo_data,
                    xref="x", yref="y",
                    x=fixed_x + logo_offset, 
                    y=adjusted_y,  # 使用调整后的位置，避免重叠
                    sizex=logo_offset, 
                    sizey=logo_height,
                    xanchor="left", 
                    yanchor="middle",
                    sizing="contain",
                    opacity=1,
                    layer="above"
                ))
    
    # 将当前帧的数据、images和双速率动态y轴范围打包到Frame中
    frames.append(go.Frame(
        data=frame_data, 
        name=str(i),
        layout=go.Layout(
            images=images_i,
            yaxis=dict(
                range=dyn_ranges[i],  # 使用双速率动态范围
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
            y_val = interp_revenue[airline][0]
            valid_y_values_initial.append(y_val)
            valid_airlines_in_initial_frame.append(airline)

# 按y值对初始帧的航空公司进行排序（从小到大）
sorted_indices_initial = np.argsort(valid_y_values_initial)
sorted_airlines_initial = [valid_airlines_in_initial_frame[idx] for idx in sorted_indices_initial]
sorted_y_values_initial = [valid_y_values_initial[idx] for idx in sorted_indices_initial]

# 计算初始帧logo高度
initial_y_range = dyn_ranges[0]
initial_y_range_size = initial_y_range[1] - initial_y_range[0]
initial_logo_height = logo_size * initial_y_range_size

# 调整初始帧logo位置，避免重叠
adjusted_y_positions_initial = list(sorted_y_values_initial)

# 第一步：计算理想间距和每个点的影响范围
min_required_gap_initial = initial_logo_height * 1.05  # 减小最小所需间距
logo_influences_initial = []  # 存储每个logo的影响范围[下边界, 上边界]

for pos in adjusted_y_positions_initial:
    half_gap = min_required_gap_initial / 2
    logo_influences_initial.append([pos - half_gap, pos + half_gap])

# 第二步：检测并修复重叠
has_overlap = True
max_iterations = 10  # 防止无限循环
iteration = 0

while has_overlap and iteration < max_iterations:
    has_overlap = False
    iteration += 1
    
    # 从第二个logo开始，检查重叠
    for j in range(1, len(logo_influences_initial)):
        # 当前logo与上一个logo的重叠
        curr_lower = logo_influences_initial[j][0]
        prev_upper = logo_influences_initial[j-1][1]
        
        if curr_lower < prev_upper:  # 存在重叠
            has_overlap = True
            overlap_amount = prev_upper - curr_lower
            
            # 向上或向下移动以解决重叠
            if j < len(logo_influences_initial) / 2:  # 前半部分倾向于向下移动
                # 向下移动前一个logo
                shift = -overlap_amount - 0.01 * initial_logo_height
                logo_influences_initial[j-1][0] += shift
                logo_influences_initial[j-1][1] += shift
                adjusted_y_positions_initial[j-1] += shift
            else:  # 后半部分倾向于向上移动
                # 向上移动当前logo
                shift = overlap_amount + 0.01 * initial_logo_height
                logo_influences_initial[j][0] += shift
                logo_influences_initial[j][1] += shift
                adjusted_y_positions_initial[j] += shift

# 第三步：确保所有logo都在视图范围内
# 获取初始帧y轴范围
y_min_initial, y_max_initial = dyn_ranges[0]
margin_initial = initial_logo_height / 2

# 检查所有logo是否在视图范围内
for j in range(len(adjusted_y_positions_initial)):
    if adjusted_y_positions_initial[j] - margin_initial < y_min_initial:
        # logo底部超出下边界
        adjusted_y_positions_initial[j] = y_min_initial + margin_initial + 0.01 * initial_logo_height
    elif adjusted_y_positions_initial[j] + margin_initial > y_max_initial:
        # logo顶部超出上边界
        adjusted_y_positions_initial[j] = y_max_initial - margin_initial - 0.01 * initial_logo_height

# 初始帧logo images
initial_images = []
for idx, airline in enumerate(sorted_airlines_initial):
    # 获取对应的logo
    if airline in airline_to_logo_map:
        logo_path = airline_to_logo_map[airline]
        if logo_path in logo_cache:
            logo_data = logo_cache[logo_path]
            
            # 使用调整后的y位置
            adjusted_y = adjusted_y_positions_initial[idx]
            
            initial_images.append(dict(
                source=logo_data,
                xref="x", yref="y",
                x=fixed_x + logo_offset, 
                y=adjusted_y,  # 使用调整后的位置，避免重叠
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
            range=dyn_ranges[0],  # 使用初始帧的双速率动态范围
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
                         "transition": {"duration": 0}  # 关闭布局过渡效果，消除振荡缩放
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
# 修复：不能直接设置fig.layout.frame，需要使用animation_opts
fig.update(
    layout_updatemenus=[
        {
            "buttons": [
                {
                    "args": [None, {"frame": {"duration": 100, "redraw": True}, "transition": {"duration": 0}}],
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
