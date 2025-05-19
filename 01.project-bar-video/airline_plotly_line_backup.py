import pandas as pd
import os
import plotly.graph_objs as go
import plotly.io as pio
from tqdm import tqdm
import numpy as np
import base64
from PIL import Image
import json

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

# 只显示最新季度收入前8的公司，而不是之前的15家
latest_quarter = revenue_data.index[-1]
top_airlines = revenue_data.loc[latest_quarter].sort_values(ascending=False).head(8).index.tolist()
revenue_data = revenue_data[top_airlines]
valid_airlines = top_airlines

# 打印有效的航空公司名称，用于调试
print("仅显示前8大航空公司:", valid_airlines)

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
interp_steps = 4  # 从2增加到4，创建更多中间帧
interp_x = np.linspace(0, len(quarters)-1, num=(len(quarters)-1)*interp_steps+1)

# 计算帧数（以便于后面设置动画总时长）
total_frames = (len(quarters)-1)*interp_steps+1
print(f"总帧数: {total_frames}")

# 根据总时长和总帧数计算帧持续时间
target_duration_sec = 60  # 目标时长为60秒
frame_duration = int(target_duration_sec * 1000 / total_frames)  # 转换为毫秒
print(f"每帧持续时间: {frame_duration}毫秒")

# 设置更短的过渡时间，使用线性插值实现真正平滑的效果
frame_transition = max(frame_duration - 10, 10)  # 确保有足够的过渡时间

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

# 计算全局Y轴范围，用于固定Y轴
global_y_min = 0  # Y轴最小值设为0
global_y_max = revenue_data.max().max() * 1.2  # Y轴最大值比最大收入高20%

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

# 设置持久化模式，防止元素重绘导致闪烁
persistent_mode = True  # 启用元素持久化以防止闪烁

# 设置补间动画模式为linear，确保匀速过渡
easing_function = "linear"  # 改为linear，确保匀速平滑过渡

# 检测并修正异常值（防止突然的峰值导致跳跃）
def detect_and_fix_outliers(values, threshold=1.2):
    """检测并平滑异常值，避免突然跳跃"""
    smoothed = values.copy()
    # 首先应用移动平均进行初步平滑
    window = 5
    for i in range(len(values)):
        # 获取窗口内的值
        start = max(0, i - window//2)
        end = min(len(values), i + window//2 + 1)
        window_vals = values[start:end]
        # 计算窗口均值
        smoothed[i] = sum(window_vals) / len(window_vals)
    
    # 然后检测和修正特别严重的异常
    for i in range(2, len(smoothed)-2):
        # 计算相邻差值
        diff_prev = abs(smoothed[i] - smoothed[i-1])
        diff_next = abs(smoothed[i] - smoothed[i+1])
        
        # 计算局部变化率
        rate_prev = smoothed[i] / max(smoothed[i-1], 0.001)  # 避免除零
        rate_next = smoothed[i+1] / max(smoothed[i], 0.001)
        
        # 使用多个条件来检测异常
        is_outlier = False
        
        # 条件1: 与前后帧相比变化率超过阈值
        if (rate_prev > threshold and rate_next < 1/threshold) or \
           (rate_prev < 1/threshold and rate_next > threshold):
            is_outlier = True
        
        # 条件2: 与前后帧差值显著大于局部平均差值
        avg_diff = (diff_prev + diff_next) / 2
        if diff_prev > avg_diff * 2 and diff_next > avg_diff * 2:
            is_outlier = True
            
        # 条件3: 当前值远离相邻5个点的均值
        neighbors = smoothed[max(0, i-2):i] + smoothed[i+1:min(len(smoothed), i+3)]
        neighbor_mean = sum(neighbors) / len(neighbors)
        if abs(smoothed[i] - neighbor_mean) > neighbor_mean * 0.3:  # 偏离30%以上
            is_outlier = True
            
        # 修正异常值 - 使用更稳健的插值
        if is_outlier:
            # 使用更多点的加权平均来修正
            weights = [0.1, 0.2, 0.4, 0.2, 0.1]  # 权重数组
            indices = [i-2, i-1, i, i+1, i+2]
            valid_weights = []
            valid_values = []
            
            for idx, w in zip(indices, weights):
                if 0 <= idx < len(smoothed) and idx != i:  # 排除当前点
                    valid_weights.append(w)
                    valid_values.append(smoothed[idx])
            
            # 重新归一化权重
            weight_sum = sum(valid_weights)
            valid_weights = [w/weight_sum for w in valid_weights]
            
            # 计算加权平均
            smoothed[i] = sum(v*w for v, w in zip(valid_values, valid_weights))
    
    return smoothed

# 应用异常值检测和修正
max_values_by_frame = detect_and_fix_outliers(max_values_by_frame, threshold=1.2)  # 进一步降低阈值以处理早期帧的异常

# 增强平滑强度 - 使用更大的窗口和更强的权重
window_size = 41  # 增加窗口大小，让平滑更强
padded_max = np.pad(max_values_by_frame, (window_size // 2, window_size // 2), mode='edge')

smoothed_y_max = []
for i in range(len(max_values_by_frame)):
    window = padded_max[i:i+window_size]
    # 使用高斯权重，中心权重更强
    weights = np.exp(-0.15 * np.linspace(-3, 3, window_size)**2)  # 使用更平坦的权重分布
    avg = np.sum(np.array(window) * weights) / np.sum(weights)
    # 对早期帧添加更多的余量防止闪烁
    padding_factor = 1.2 if i < 30 else 1.15
    smoothed_y_max.append(avg * padding_factor)  # 早期帧使用20%的padding而不是15%

# 对平滑后的y轴范围应用缓动函数，确保过渡绝对平滑
def ease_function(t):
    """应用二次缓动函数，使变化更加自然"""
    # 使用平滑的三次方缓动函数
    if t < 0.5:
        return 4 * t * t * t
    else:
        return 1 - pow(-2 * t + 2, 3) / 2

# 再次处理y轴最大值，应用缓动进一步平滑过渡
eased_y_max = []
window_size_ease = 5  # 使用小窗口应用缓动

for i in range(len(smoothed_y_max)):
    if i < window_size_ease or i >= len(smoothed_y_max) - window_size_ease:
        # 对于边缘帧，直接使用当前值
        eased_y_max.append(smoothed_y_max[i])
    else:
        # 对于中间帧，使用缓动函数应用平滑
        values = smoothed_y_max[i-window_size_ease:i+window_size_ease+1]
        weights = [ease_function((idx + 0.5) / (2 * window_size_ease + 1)) for idx in range(2 * window_size_ease + 1)]
        
        # 标准化权重
        weights_sum = sum(weights)
        weights = [w / weights_sum for w in weights]
        
        # 应用加权平均
        eased_value = sum(v * w for v, w in zip(values, weights))
        eased_y_max.append(eased_value)

# 使用最终缓动后的y轴范围
smoothed_y_max = eased_y_max

# 对早期帧进行特殊处理，强制使用更加平缓的y轴范围变化
# 这会确保前30帧有非常平滑的过渡
early_frame_count = 30
if len(smoothed_y_max) > early_frame_count:
    # 找到第30帧的y轴上限值
    target_value = smoothed_y_max[early_frame_count]
    
    # 计算起始值（第一帧）
    start_value = smoothed_y_max[0]
    
    # 对前30帧应用更加线性的平滑过渡
    for i in range(early_frame_count):
        # 使用缓动函数进行过渡
        progress = i / early_frame_count
        # 使用更平滑的三次方缓动
        eased_progress = progress * progress * (3 - 2 * progress)
        
        # 线性插值并略微提高上限，确保稳定性
        smoothed_y_max[i] = start_value + (target_value - start_value) * eased_progress
        # 添加额外的上方空间，确保早期帧不会有紧凑感
        smoothed_y_max[i] *= 1.1

# 确保动画的连续性 - 在结尾几帧保持y轴范围一致
for i in range(max(0, len(smoothed_y_max) - 3), len(smoothed_y_max)):
    if i > 0:
        smoothed_y_max[i] = smoothed_y_max[i-1]

# 添加下方缓冲区，确保图表有足够的空间
# global_min_with_buffer = global_y_min  # 简单起见，当前可以直接使用global_y_min (已在前面计算)

# 更新动画设置，使用advanced-easing实现平滑过渡
animation_opts = dict(
    frame=dict(
        duration=frame_duration,
        redraw=False  # 减少重绘次数
    ),
    transition=dict(
        duration=frame_transition,
        easing='linear'  # 确保线性过渡
    ),
    mode="immediate"
)

# 高级平滑HTML设置
custom_css = """
<style>
/* 确保动画平滑运行的基本设置 */
body {
  margin: 0;
  padding: 0;
}

/* 设置更好的渲染性能 */
.js-plotly-plot {
  position: relative;
}

/* 曲线平滑插值的视觉优化 */
.js-plotly-plot .scatterlayer .js-line {
  shape-rendering: geometricPrecision;
  stroke-linejoin: round;
  stroke-linecap: round;
  vector-effect: non-scaling-stroke;
}

/* 预加载图像，防止闪烁 */
.js-plotly-plot .layer-above img {
  opacity: 1;
}
</style>
"""

# 使用requestAnimationFrame实现高度平滑的线性动画
animation_js = """
<script>
// 等待DOM完全加载
document.addEventListener('DOMContentLoaded', function() {
    // 等待Plotly完全初始化
    setTimeout(function() {
        const plot = document.querySelector('.js-plotly-plot');
        if (!plot) return;
        
        // 基本Y轴稳定
        const yaxisRange = [""" + str(global_y_min) + """, """ + str(global_y_max) + """];
        
        // 强制固定Y轴范围
        Plotly.relayout(plot, {
            'yaxis.range': yaxisRange,
            'yaxis.fixedrange': true,
            'yaxis.autorange': false
        });
        
        // 创建高级动画控制器
        const smoothAnimator = {
            // 动画状态
            isPlaying: false,
            currentFrameIndex: 0,
            totalFrames: """ + str(total_frames) + """,
            frameDuration: """ + str(frame_duration) + """,
            lastTimestamp: 0,
            
            // 动画递归函数
            animate: function(timestamp) {
                if (!this.isPlaying) return;
                
                // 计算时间差
                if (!this.lastTimestamp) {
                    this.lastTimestamp = timestamp;
                }
                
                const elapsed = timestamp - this.lastTimestamp;
                const framesElapsed = elapsed / this.frameDuration;
                
                if (framesElapsed >= 0.9) { // 稍微提前一点执行，保证平滑
                    // 更新时间戳
                    this.lastTimestamp = timestamp;
                    
                    // 计算下一帧，实现线性平滑递进
                    this.currentFrameIndex = (this.currentFrameIndex + 1) % this.totalFrames;
                    
                    // 应用新帧
                    Plotly.animate(plot, [this.currentFrameIndex.toString()], {
                        transition: {
                            duration: """ + str(frame_transition) + """,
                            easing: 'linear'
                        },
                        frame: {
                            duration: """ + str(frame_duration) + """,
                            redraw: false
                        }
                    });
                    
                    // 立即强制Y轴保持固定
                    Plotly.relayout(plot, {
                        'yaxis.range': yaxisRange,
                        'yaxis.autorange': false
                    });
                }
                
                // 请求下一帧
                requestAnimationFrame(this.animate.bind(this));
            },
            
            // 播放控制
            play: function() {
                if (this.isPlaying) return;
                this.isPlaying = true;
                this.lastTimestamp = 0;
                requestAnimationFrame(this.animate.bind(this));
            },
            
            pause: function() {
                this.isPlaying = false;
            },
            
            // 重置并播放
            reset: function() {
                this.currentFrameIndex = 0;
                Plotly.animate(plot, ['0'], {
                    transition: {duration: 0},
                    frame: {duration: 0}
                });
                this.play();
            }
        };
        
        // 拦截原始播放按钮点击
        const buttons = plot.querySelectorAll('a[data-attr="play"], .plotly-notifier button');
        buttons.forEach(button => {
            if (button) {
                const originalClick = button.onclick;
                button.onclick = function(e) {
                    // 阻止原始点击事件
                    e.preventDefault();
                    e.stopPropagation();
                    
                    // 使用我们的平滑播放器
                    smoothAnimator.play();
                    
                    return false;
                };
            }
        });
        
        // 添加自定义控制按钮
        const controlDiv = document.createElement('div');
        controlDiv.style.position = 'absolute';
        controlDiv.style.top = '10px';
        controlDiv.style.right = '10px';
        controlDiv.style.zIndex = '1000';
        
        const playBtn = document.createElement('button');
        playBtn.textContent = '播放';
        playBtn.style.marginRight = '5px';
        playBtn.onclick = function() {
            smoothAnimator.play();
        };
        
        const pauseBtn = document.createElement('button');
        pauseBtn.textContent = '暂停';
        pauseBtn.onclick = function() {
            smoothAnimator.pause();
        };
        
        controlDiv.appendChild(playBtn);
        controlDiv.appendChild(pauseBtn);
        plot.appendChild(controlDiv);
        
        // 自动开始播放
        setTimeout(function() {
            smoothAnimator.play();
        }, 500);
    }, 500);
});
</script>
"""

# 修改优化配置
optimized_config = {
    'responsive': True,
    'staticPlot': False,
    'displayModeBar': False,
    'displaylogo': False,
    'showAxisDragHandles': False,
    'showTips': False,
    'doubleClick': False,
    'scrollZoom': False,
    'showLink': False,
    'sendData': False,
    'linkText': '',
    'showSources': False,
    'modeBarButtonsToRemove': ['zoom2d', 'pan2d', 'select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 
                              'autoScale2d', 'resetScale2d', 'toggleSpikelines', 
                              'hoverCompareCartesian', 'hoverClosestCartesian']
}

# 创建初始数据 - 如果尚未创建
if 'initial_data' not in locals():
    initial_data = []
    for airline in valid_airlines:
        region = metadata.loc['Region', airline] if airline in metadata.columns else 'Unknown'
        color = region_colors.get(region, '#808080')
        
        # 添加线和点的初始数据
        initial_data.append(go.Scatter(
            x=[], y=[], mode='lines', name=airline, 
            line=dict(color=color, width=3, shape='spline', smoothing=1.3),
            hoverinfo='skip', showlegend=False, uid=f"{airline}_line"
        ))
        initial_data.append(go.Scatter(
            x=[], y=[], mode='markers', name=airline, 
            marker=dict(color=color, size=12), hoverinfo='text+y',
            text=[], showlegend=False, uid=f"{airline}_point"
        ))

# 创建空的frames列表 - 如果尚未创建
if 'frames' not in locals() or not frames:
    frames = []
    # 创建一个简单的帧列表，稍后可以被替换
    for i in range(len(interp_x)):
        frames.append(go.Frame(
            data=initial_data,
            layout=go.Layout(yaxis=dict(range=[global_min_with_buffer, smoothed_y_max[i]])),
            name=str(i)
        ))

# 创建初始图表
fig = go.Figure(
    data=initial_data,
    layout=go.Layout(
        title='Airline Revenue Over Time',
        xaxis=dict(
            title='', range=[0, 1], linecolor='gray', showgrid=False, 
            zeroline=False, showticklabels=False, fixedrange=True
        ),
        yaxis=dict(
            title='Revenue (Million USD)', 
            range=[global_min_with_buffer, smoothed_y_max[0]],
            linecolor='gray', showgrid=True, gridcolor='lightgray', 
            griddash='dash', zeroline=False, fixedrange=True
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        images=initial_images if 'initial_images' in locals() else [],
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            y=1.15, x=1.05,
            xanchor="right", yanchor="top",
            buttons=[
                dict(label="播放",
                     method="animate",
                     args=[None, {
                         "frame": {"duration": frame_duration, "redraw": True},
                         "fromcurrent": True, 
                         "transition": {"duration": frame_transition, "easing": easing_function},
                         "mode": "immediate"
                     }]),
                dict(label="暂停",
                     method="animate",
                     args=[[None], {
                         "frame": {"duration": 0, "redraw": False},
                         "mode": "immediate",
                         "transition": {"duration": 0}
                     }])
            ]
        )],
        sliders=[],
        uirevision='constant',
        datarevision=1
    ),
    frames=frames
)

# 生成优化的HTML
html_content = pio.to_html(
    fig, 
    include_plotlyjs='cdn',
    full_html=True,
    config=optimized_config,
    animation_opts=animation_opts,
    validate=False,
    auto_play=False
)

# 插入自定义CSS和动画JS
html_content = html_content.replace('</head>', f'{custom_css}</head>')
html_content = html_content.replace('</body>', f'{animation_js}</body>')

# 保存最终HTML文件
output_file = "output/airline_revenue_linechart.html"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"已优化动画性能和平滑度，保存至 {output_file}")
print(f"最终动画: 总时长{target_duration_sec}秒 ({total_frames}帧，每帧{frame_duration}毫秒，过渡时间{frame_transition}毫秒)")

# ... existing code ...

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

# 设置持久化模式，防止元素重绘导致闪烁
persistent_mode = True  # 启用元素持久化以防止闪烁

# 设置补间动画模式为linear，确保匀速过渡
easing_function = "linear"  # 改为linear，确保匀速平滑过渡

# 检测并修正异常值（防止突然的峰值导致跳跃）
def detect_and_fix_outliers(values, threshold=1.2):
    """检测并平滑异常值，避免突然跳跃"""
    smoothed = values.copy()
    # 首先应用移动平均进行初步平滑
    window = 5
    for i in range(len(values)):
        # 获取窗口内的值
        start = max(0, i - window//2)
        end = min(len(values), i + window//2 + 1)
        window_vals = values[start:end]
        # 计算窗口均值
        smoothed[i] = sum(window_vals) / len(window_vals)
    
    # 然后检测和修正特别严重的异常
    for i in range(2, len(smoothed)-2):
        # 计算相邻差值
        diff_prev = abs(smoothed[i] - smoothed[i-1])
        diff_next = abs(smoothed[i] - smoothed[i+1])
        
        # 计算局部变化率
        rate_prev = smoothed[i] / max(smoothed[i-1], 0.001)  # 避免除零
        rate_next = smoothed[i+1] / max(smoothed[i], 0.001)
        
        # 使用多个条件来检测异常
        is_outlier = False
        
        # 条件1: 与前后帧相比变化率超过阈值
        if (rate_prev > threshold and rate_next < 1/threshold) or \
           (rate_prev < 1/threshold and rate_next > threshold):
            is_outlier = True
        
        # 条件2: 与前后帧差值显著大于局部平均差值
        avg_diff = (diff_prev + diff_next) / 2
        if diff_prev > avg_diff * 2 and diff_next > avg_diff * 2:
            is_outlier = True
            
        # 条件3: 当前值远离相邻5个点的均值
        neighbors = smoothed[max(0, i-2):i] + smoothed[i+1:min(len(smoothed), i+3)]
        neighbor_mean = sum(neighbors) / len(neighbors)
        if abs(smoothed[i] - neighbor_mean) > neighbor_mean * 0.3:  # 偏离30%以上
            is_outlier = True
            
        # 修正异常值 - 使用更稳健的插值
        if is_outlier:
            # 使用更多点的加权平均来修正
            weights = [0.1, 0.2, 0.4, 0.2, 0.1]  # 权重数组
            indices = [i-2, i-1, i, i+1, i+2]
            valid_weights = []
            valid_values = []
            
            for idx, w in zip(indices, weights):
                if 0 <= idx < len(smoothed) and idx != i:  # 排除当前点
                    valid_weights.append(w)
                    valid_values.append(smoothed[idx])
            
            # 重新归一化权重
            weight_sum = sum(valid_weights)
            valid_weights = [w/weight_sum for w in valid_weights]
            
            # 计算加权平均
            smoothed[i] = sum(v*w for v, w in zip(valid_values, valid_weights))
    
    return smoothed

# 应用异常值检测和修正
max_values_by_frame = detect_and_fix_outliers(max_values_by_frame, threshold=1.2)  # 进一步降低阈值以处理早期帧的异常

# 增强平滑强度 - 使用更大的窗口和更强的权重
window_size = 41  # 增加窗口大小，让平滑更强
padded_max = np.pad(max_values_by_frame, (window_size // 2, window_size // 2), mode='edge')

smoothed_y_max = []
for i in range(len(max_values_by_frame)):
    window = padded_max[i:i+window_size]
    # 使用高斯权重，中心权重更强
    weights = np.exp(-0.15 * np.linspace(-3, 3, window_size)**2)  # 使用更平坦的权重分布
    avg = np.sum(np.array(window) * weights) / np.sum(weights)
    # 对早期帧添加更多的余量防止闪烁
    padding_factor = 1.2 if i < 30 else 1.15
    smoothed_y_max.append(avg * padding_factor)  # 早期帧使用20%的padding而不是15%

# 对平滑后的y轴范围应用缓动函数，确保过渡绝对平滑
def ease_function(t):
    """应用二次缓动函数，使变化更加自然"""
    # 使用平滑的三次方缓动函数
    if t < 0.5:
        return 4 * t * t * t
    else:
        return 1 - pow(-2 * t + 2, 3) / 2

# 再次处理y轴最大值，应用缓动进一步平滑过渡
eased_y_max = []
window_size_ease = 5  # 使用小窗口应用缓动

for i in range(len(smoothed_y_max)):
    if i < window_size_ease or i >= len(smoothed_y_max) - window_size_ease:
        # 对于边缘帧，直接使用当前值
        eased_y_max.append(smoothed_y_max[i])
    else:
        # 对于中间帧，使用缓动函数应用平滑
        values = smoothed_y_max[i-window_size_ease:i+window_size_ease+1]
        weights = [ease_function((idx + 0.5) / (2 * window_size_ease + 1)) for idx in range(2 * window_size_ease + 1)]
        
        # 标准化权重
        weights_sum = sum(weights)
        weights = [w / weights_sum for w in weights]
        
        # 应用加权平均
        eased_value = sum(v * w for v, w in zip(values, weights))
        eased_y_max.append(eased_value)

# 使用最终缓动后的y轴范围
smoothed_y_max = eased_y_max

# 对早期帧进行特殊处理，强制使用更加平缓的y轴范围变化
# 这会确保前30帧有非常平滑的过渡
early_frame_count = 30
if len(smoothed_y_max) > early_frame_count:
    # 找到第30帧的y轴上限值
    target_value = smoothed_y_max[early_frame_count]
    
    # 计算起始值（第一帧）
    start_value = smoothed_y_max[0]
    
    # 对前30帧应用更加线性的平滑过渡
    for i in range(early_frame_count):
        # 使用缓动函数进行过渡
        progress = i / early_frame_count
        # 使用更平滑的三次方缓动
        eased_progress = progress * progress * (3 - 2 * progress)
        
        # 线性插值并略微提高上限，确保稳定性
        smoothed_y_max[i] = start_value + (target_value - start_value) * eased_progress
        # 添加额外的上方空间，确保早期帧不会有紧凑感
        smoothed_y_max[i] *= 1.1

# 确保动画的连续性 - 在结尾几帧保持y轴范围一致
for i in range(max(0, len(smoothed_y_max) - 3), len(smoothed_y_max)):
    if i > 0:
        smoothed_y_max[i] = smoothed_y_max[i-1]

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

# 创建一个跟踪每帧显示的logo的缓存，确保连续性
frame_logo_tracker = {}

# 预计算每一帧每个航空公司的调整后位置
# 这将使得相邻帧之间的位置变化更平滑
adjusted_positions_by_frame = {}

# 预处理步骤：为每个航空公司建立存在的连续区间
# 这有助于确保航空公司在短暂消失后能够保持位置的一致性
airline_presence = {}

for airline in valid_airlines:
    # 查找每个航空公司在哪些帧中存在有效数据
    present_frames = []
    for i in range(len(interp_x)):
        nearest_q_idx = min(int(round(interp_x[i])), len(quarters)-1)
        current_quarter = quarters[nearest_q_idx]
        
        raw_val = revenue_data.at[current_quarter, airline] if current_quarter in revenue_data.index else None
        if not pd.isna(raw_val) and raw_val > 0:
            present_frames.append(i)
    
    # 如果航空公司有数据
    if present_frames:
        # 根据存在帧确定连续区间
        intervals = []
        start = present_frames[0]
        prev = start
        
        for frame in present_frames[1:]:
            # 如果与前一帧相隔超过5帧，认为是新区间
            if frame > prev + 5:
                intervals.append((start, prev))
                start = frame
            prev = frame
        
        # 添加最后一个区间
        intervals.append((start, prev))
        airline_presence[airline] = intervals

# 打印每家航空公司的存在区间，便于调试
print("\nAirline presence intervals:")
for airline, intervals in sorted(airline_presence.items()):
    print(f"{airline}: {intervals}")

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

# 创建初始数据和图表布局
initial_data = []

# 为每个航空公司创建初始数据
for airline in valid_airlines:
    region = metadata.loc['Region', airline] if airline in metadata.columns else 'Unknown'
    color = region_colors.get(region, '#808080')
    
    # 添加线 - 初始为空
    initial_data.append(go.Scatter(
        x=[], 
        y=[], 
        mode='lines', 
        name=airline,
        line=dict(color=color, width=3, shape='spline', smoothing=1.3),
        hoverinfo='none', 
        showlegend=False,
        uid=f"{airline}_line"  # 添加唯一ID确保一致性
    ))
    
    # 添加点 - 初始为空
    initial_data.append(go.Scatter(
        x=[], 
        y=[], 
        mode='markers', 
        name=airline,
        marker=dict(color=color, size=12), 
        hoverinfo='text+y', 
        text=[], 
        showlegend=False,
        uid=f"{airline}_point"  # 添加唯一ID确保一致性
    ))

# 重新创建帧，使用预计算的布局，确保y轴和数据点同步移动
frames = []

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

# 创建字典记录每个航空公司上一帧的状态
prev_frame_logos = {}

# 创建一个包含所有航空公司的完整数据框架
# 这样每一帧都有完全相同的数据结构，减少闪烁
base_frame_data = []
for airline in valid_airlines:
    region = metadata.loc['Region', airline] if airline in metadata.columns else 'Unknown'
    color = region_colors.get(region, '#808080')
    
    # 为每个航空公司添加两个基础图表元素（线和点）
    # 线
    base_frame_data.append(go.Scatter(
        x=[], y=[], 
        mode='lines', 
        name=airline,
        line=dict(color=color, width=2, shape='spline', smoothing=1.3), 
        hoverinfo='skip', 
        showlegend=False,
        uid=f"{airline}_line",  # 添加唯一ID确保一致性
        # 添加持久化设置，防止元素闪烁
        ids=[f"{airline}_line"] if persistent_mode else None,
        customdata=[airline]  # 添加自定义数据，确保识别
    ))
    
    # 点
    base_frame_data.append(go.Scatter(
        x=[], y=[], 
        mode='markers', 
        name=airline,
        marker=dict(color=color, size=12), 
        hoverinfo='text+y', 
        text=[], 
        showlegend=False,
        uid=f"{airline}_point",  # 添加唯一ID确保一致性
        # 添加持久化设置，防止元素闪烁
        ids=[f"{airline}_point"] if persistent_mode else None,
        customdata=[airline]  # 添加自定义数据，确保识别
    ))

for i in range(len(interp_x)):
    # 复制基础数据结构，确保每帧结构一致
    frame_data = []
    for base_trace in base_frame_data:
        # 获取基础属性
        line_props = {} if 'line' not in base_trace else base_trace['line']
        marker_props = {} if 'marker' not in base_trace else base_trace['marker']
        
        # 创建新的trace，而不是尝试复制
        new_trace = go.Scatter(
            x=[], 
            y=[], 
            mode=base_trace['mode'] if 'mode' in base_trace else 'lines',
            name=base_trace['name'] if 'name' in base_trace else '',
            line=line_props,
            marker=marker_props,
            hoverinfo=base_trace['hoverinfo'] if 'hoverinfo' in base_trace else 'all',
            showlegend=base_trace['showlegend'] if 'showlegend' in base_trace else False,
            uid=base_trace['uid'] if 'uid' in base_trace else None,
            # 添加持久化设置，防止元素闪烁
            ids=[base_trace['uid']] if persistent_mode and 'uid' in base_trace else None
        )
        frame_data.append(new_trace)
    
    # 获取当前帧的时间点
    nearest_q_idx = min(int(round(interp_x[i])), len(quarters)-1)
    current_quarter = quarters[nearest_q_idx]
    
    # 收集当前帧的所有logo位置，与数据点保持一致
    frame_logos = []
    logo_positions = {}
    
    # 为每个航空公司生成线和点
    for idx, airline in enumerate(valid_airlines):
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
        
        # 更新线的数据 - 找到对应的trace进行更新
        line_trace_idx = idx * 2  # 每个航空公司有两个trace：线和点
        point_trace_idx = idx * 2 + 1
        
        # 更新线的数据
        if line_trace_idx < len(frame_data):
            # 使用字典更新方式
            frame_data[line_trace_idx]['x'] = x_hist
            frame_data[line_trace_idx]['y'] = y_hist
            if 'line' not in frame_data[line_trace_idx]:
                frame_data[line_trace_idx]['line'] = {}
            frame_data[line_trace_idx]['line']['color'] = color
            # 添加曲线插值，设置smoothing为1.3以获得最大平滑度
            frame_data[line_trace_idx]['line']['shape'] = 'spline'
            frame_data[line_trace_idx]['line']['smoothing'] = 1.3

        # 更新点的数据
        if point_trace_idx < len(frame_data):
            frame_data[point_trace_idx]['x'] = [fixed_x]
            frame_data[point_trace_idx]['y'] = [current_y]
            frame_data[point_trace_idx]['text'] = [current_quarter]
            if 'marker' not in frame_data[point_trace_idx]:
                frame_data[point_trace_idx]['marker'] = {}
            frame_data[point_trace_idx]['marker']['color'] = color
            frame_data[point_trace_idx]['marker']['size'] = 12
        
        # 使用平滑调整后的位置绘制点
        if i in final_positions and airline in final_positions[i]:
            # 保存当前航空公司的logo位置，与数据点保持一致
            logo_positions[airline] = current_y
            
    # 处理logo显示的连续性问题
    active_airlines_current = set(logo_positions.keys())

    # 初始帧需要特殊处理 - 给前30帧增加特殊稳定性措施
    is_early_frame = i < 30

    # 检查当前帧是否在某个航空公司的存在区间之间（短暂消失期）
    for airline in valid_airlines:
        # 如果航空公司当前帧不存在但在airline_presence中有记录
        if airline not in active_airlines_current and airline in airline_presence:
            intervals = airline_presence[airline]
            
            # 如果是前30帧，对短暂消失的航空公司更加宽容
            if is_early_frame:
                # 查找最接近的存在区间
                nearest_interval = None
                min_distance = float('inf')
                
                for interval in intervals:
                    start, end = interval
                    if start <= i <= end:  # 在区间内
                        nearest_interval = interval
                        min_distance = 0
                        break
                    elif i < start:  # 在区间前
                        distance = start - i
                        if distance < min_distance:
                            min_distance = distance
                            nearest_interval = interval
                    else:  # 在区间后
                        distance = i - end
                        if distance < min_distance:
                            min_distance = distance
                            nearest_interval = interval
                
                # 如果最近的区间距离小于10帧，平滑过渡
                if nearest_interval and min_distance <= 15:  # 早期帧使用更大的容忍度
                    start, end = nearest_interval
                    if start > i:  # 即将出现的航空公司
                        next_frame = start
                        if next_frame in final_positions and airline in final_positions[next_frame]:
                            next_y = final_positions[next_frame][airline]
                            # 提前显示即将出现的航空公司，透明度降低
                            progress = 1 - min_distance / 15
                            interp_y = next_y
                            logo_positions[airline] = interp_y
                    elif end < i:  # 刚刚消失的航空公司
                        prev_frame = end
                        if prev_frame in final_positions and airline in final_positions[prev_frame]:
                            prev_y = final_positions[prev_frame][airline]
                            # 让刚刚消失的航空公司逐渐淡出
                            progress = 1 - min_distance / 15
                            logo_positions[airline] = prev_y
            
            # 检查当前帧是否在任意两个区间之间且间隔小于15帧（早期帧放宽标准）
            max_gap = 15 if is_early_frame else 10
            for idx in range(len(intervals) - 1):
                interval_end = intervals[idx][1]
                next_interval_start = intervals[idx + 1][0]
                
                # 如果当前帧在两个区间之间且间隔合理
                if interval_end < i < next_interval_start and next_interval_start - interval_end < max_gap:
                    # 找到前一个区间的最后位置和下一个区间的开始位置
                    if interval_end in final_positions and airline in final_positions[interval_end] and \
                       next_interval_start in final_positions and airline in final_positions[next_interval_start]:
                        
                        # 使用线性插值计算过渡期间的位置
                        prev_y = final_positions[interval_end][airline]
                        next_y = final_positions[next_interval_start][airline]
                        progress = (i - interval_end) / (next_interval_start - interval_end)
                        
                        # 平滑的插值过渡
                        interp_y = prev_y * (1 - progress) + next_y * progress
                        
                        # 添加到当前帧的logo位置
                        logo_positions[airline] = interp_y

    # 如果是第一帧之后的帧，检查上一帧有而这一帧没有的航空公司
    if i > 0 and prev_frame_logos:
        active_airlines_prev = set(prev_frame_logos.keys())
        
        # 找出上一帧有但当前帧没有的航空公司
        missing_airlines = active_airlines_prev - active_airlines_current
        
        # 如果有突然消失的航空公司，保持其上一帧的logo，但渐变淡出
        for airline in missing_airlines:
            # 只有当该航空公司有合法的上一帧位置时才保留
            if airline in prev_frame_logos and airline in airline_to_logo_map:
                prev_y = prev_frame_logos[airline]
                
                # 检查此航空公司是否会在未来5帧内重新出现
                will_reappear = False
                for future_frame in range(i+1, min(i+5, len(interp_x))):
                    if future_frame in final_positions and airline in final_positions[future_frame]:
                        will_reappear = True
                        break
                
                # 如果将要重新出现，则保留logo以避免闪烁
                if will_reappear:
                    logo_positions[airline] = prev_y
    
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
                    y_val = max(y_range[0] + logo_height/2, min(y_val, y_range[1] - logo_height/2))
                    
                    # 检查是否是即将出现或刚刚消失的航空公司
                    opacity = 1.0
                    
                    # 对于早期帧，所有logo都使用完全不透明度，避免闪烁
                    if i < 30:
                        opacity = 1.0
                    elif airline not in prev_frame_logos and i > 0:
                        # 新出现的logo，渐变显示
                        opacity = min(0.2 + 0.8 * (i % 5) / 5, 1.0)
                    
                    # 为早期帧的logo应用额外的稳定措施
                    if i < 30 and i > 0 and airline in prev_frame_logos:
                        # 对早期帧，通过与前一帧进行插值获得更平滑的轨迹
                        prev_y = prev_frame_logos[airline]
                        # 轻微地平滑早期帧移动，但允许足够的变化以反映实际数据
                        smoothing = 0.4  # 40%的前一帧位置，60%的当前位置
                        y_val = prev_y * smoothing + y_val * (1-smoothing)
                    
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
                        opacity=opacity,
                        layer="above"
                    ))
    
    # 保存当前帧的logo位置，用于下一帧的连续性检查
    prev_frame_logos = logo_positions.copy()
    
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
for idx, airline in enumerate(valid_airlines):
    x_hist = np.linspace(0, fixed_x, 1)
    
    # 获取初始位置，优先使用平滑后的值
    initial_y = interp_revenue[airline][0]
    if 0 in final_positions and airline in final_positions[0]:
        initial_y = final_positions[0][airline]
        
    y_hist = [initial_y]  # 确保初始帧线与点同步
    region = metadata.loc['Region', airline] if airline in metadata.columns else 'Unknown'
    color = region_colors.get(region, '#808080')
    
    # 使用与帧数据相同的UID，确保一致性
    initial_data.append(go.Scatter(
        x=x_hist, 
        y=y_hist, 
        mode='lines', 
        name=airline,
        line=dict(color=color, shape='spline', smoothing=1.3), 
        hoverinfo='skip', 
        showlegend=False,
        uid=f"{airline}_line"  # 添加相同的唯一ID确保一致性
    ))
    
    initial_data.append(go.Scatter(
        x=[fixed_x], 
        y=[initial_y], 
        mode='markers', 
        name=airline,
        marker=dict(color=color, size=12), 
        hoverinfo='text+y', 
        text=[quarters[0]], 
        showlegend=False,
        uid=f"{airline}_point"  # 添加相同的唯一ID确保一致性
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
            showticklabels=False,
            fixedrange=True  # 锁定x轴范围，防止缩放导致的重绘
        ),
        yaxis=dict(
            title='Revenue (Million USD)', 
            range=[global_min_with_buffer, smoothed_y_max[0]],  # 下限固定，上限动态
            linecolor='gray', 
            showgrid=True, 
            gridcolor='lightgray', 
            griddash='dash', 
            zeroline=False,
            fixedrange=True  # 锁定y轴范围，防止缩放导致的重绘
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
                dict(label="播放",
                     method="animate",
                     args=[None, {
                         "frame": {"duration": frame_duration, "redraw": True},
                         "fromcurrent": True, 
                         "transition": {"duration": frame_transition, "easing": easing_function},
                         "mode": "immediate"
                     }]),
                dict(label="暂停",
                     method="animate",
                     args=[[None], {
                         "frame": {"duration": 0, "redraw": False},
                         "mode": "immediate",
                         "transition": {"duration": 0}
                     }])
            ]
        )],
        sliders=[],
        uirevision='constant',  # 防止UI状态重置导致的闪烁
        datarevision=1  # 一个固定的数据修订号，确保所有元素同步更新
    ),
    frames=frames
)

# 确保动画完全同步，使用特定的animate参数
for i, frame in enumerate(frames):
    frame.layout.datarevision = i  # 给每一帧添加唯一的数据修订号
    frame.layout.uirevision = 'constant'  # 保持UI状态一致，避免重绘
    # 防止任何自动调整y轴范围
    if "yaxis" in frame.layout:
        frame.layout.yaxis.autorange = False
        frame.layout.yaxis.fixedrange = True
    if "xaxis" in frame.layout:
        frame.layout.xaxis.fixedrange = True
    
    # 确保每个帧内的所有元素都有相同的修订号，强制同步更新
    if hasattr(frame, "data"):
        for trace in frame.data:
            if hasattr(trace, "uid"):
                trace._datarevision = i

# 设置全局默认的frame和transition参数，确保自动播放也能平滑进行
fig.update(
    layout_updatemenus=[
        {
            "buttons": [
                {
                    "args": [None, {
                        "frame": {"duration": frame_duration, "redraw": False}, 
                        "fromcurrent": True,
                        "transition": {"duration": frame_transition, "easing": easing_function},
                        "mode": "immediate"
                    }],
                    "label": "播放",
                    "method": "animate"
                },
                {
                    "args": [[None], {
                        "frame": {"duration": 0, "redraw": False}, 
                        "mode": "immediate", 
                        "transition": {"duration": 0}
                    }],
                    "label": "暂停",
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
        "transition": {"duration": frame_transition, "easing": easing_function},  # 使用线性缓动确保匀速过渡
        "yaxis": {
            "range": [global_min_with_buffer, smoothed_y_max[0]],  # 确保y轴范围初始化正确
            "autorange": False   # 防止自动调整范围
        }
    }
)

# 预加载所有图片，减少logo闪烁
all_logos = {}
for i, frame in enumerate(frames):
    if hasattr(frame.layout, "images") and frame.layout.images:
        for img in frame.layout.images:
            img_key = f"{img.source}_{img.x}_{img.y}"
            all_logos[img_key] = img

# 将所有图片预先添加到初始布局中，但设置为不可见，这样浏览器会预加载它们
for logo_path, logo_data in logo_cache.items():
    if logo_path in logo_cache:
        # 添加一个不可见的图像到初始布局
        fig.add_layout_image(
            dict(
                source=logo_data,
                xref="paper", yref="paper",
                x=0, y=0,
                sizex=0.001, sizey=0.001,  # 极小尺寸
                xanchor="left", yanchor="bottom",
                sizing="contain",
                opacity=0.01,  # 几乎不可见，但会被浏览器加载
                layer="below"
            )
        )

# 修改按钮动画设置，确保过渡更平滑
for button in fig.layout.updatemenus[0].buttons:
    if isinstance(button, dict) and "args" in button and len(button.args) > 1 and "transition" in button.args[1]:
        # 播放按钮 - 使用接近帧持续时间的过渡持续时间
        button.args[1]["transition"]["duration"] = frame_transition
        button.args[1]["transition"]["easing"] = easing_function
        
        # 使过渡更加平滑
        if "frame" in button.args[1]:
            button.args[1]["frame"]["redraw"] = False  # 降低重绘频率，提高性能

# 更新全局动画配置
fig.update(
    layout_updatemenus=[
        {
            "buttons": [
                {
                    "args": [None, {
                        "frame": {"duration": frame_duration, "redraw": False}, 
                        "fromcurrent": True,
                        "transition": {"duration": frame_transition, "easing": easing_function},
                        "mode": "immediate"
                    }],
                    "label": "播放",
                    "method": "animate"
                },
                {
                    "args": [[None], {
                        "frame": {"duration": 0, "redraw": False}, 
                        "mode": "immediate", 
                        "transition": {"duration": 0}
                    }],
                    "label": "暂停",
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
        "transition": {"duration": frame_transition, "easing": easing_function},  # 使用线性缓动确保匀速过渡
        "yaxis": {
            "range": [global_min_with_buffer, smoothed_y_max[0]],  # 确保y轴范围初始化正确
            "autorange": False   # 防止自动调整范围
        }
    }
)

# 在最后再添加一个通用的图片预加载函数到布局中
fig.update_layout(
    annotations=[
        dict(
            x=0.5,
            y=1.05,
            xref="paper",
            yref="paper",
            text="Airline Revenue Trends",
            showarrow=False,
            font=dict(size=16)
        )
    ]
)

# 添加自定义CSS到HTML头部，确保平滑过渡
custom_css = """
<style>
/* 应用于所有Plotly图形元素的过渡效果 */
.plotly .lines, .plotly .points, .plotly .text, .plotly .images {
  transition: all %dms linear !important;
  animation-timing-function: linear !important;
}

/* 确保图像与图表元素同步移动 */
.plotly .layer-above {
  will-change: transform;
  transform: translateZ(0);
  transition: all %dms linear !important;
}

/* 减少重绘和闪烁 */
.plotly {
  transform: translateZ(0);
  backface-visibility: hidden;
  perspective: 1000px;
}

/* 强制使用硬件加速和线性动画 */
.js-plotly-plot, .plotly {
  -webkit-animation-timing-function: linear !important;
  animation-timing-function: linear !important;
  -webkit-transition-timing-function: linear !important;
  transition-timing-function: linear !important;
}

/* 确保所有动画元素使用相同的transition属性 */
.js-plotly-plot .scatterlayer .trace, .js-plotly-plot .imagelayer .layer-above {
  transition: transform %dms linear, opacity %dms linear !important;
}
</style>
""" % (frame_transition, frame_transition, frame_transition, frame_transition)

# Save HTML with embedded plotly.js to ensure consistent playback
output_file = "output/airline_revenue_linechart.html"
html_content = pio.to_html(
    fig, 
    include_plotlyjs='embed', 
    full_html=True,
    config={
    'responsive': True,
    'showAxisDragHandles': False,  # 禁用坐标轴拖动，避免用户交互影响动画
    'staticPlot': False,           # 动态图
    'doubleClick': 'reset',        # 双击重置视图
    'displayModeBar': False,       # 隐藏模式栏
    'displaylogo': False,          # 不显示plotly logo
        'scrollZoom': False,           # 禁用滚轮缩放，避免意外的重绘
        'doubleClick': False,          # 禁用双击缩放，避免意外的重绘
    'toImageButtonOptions': {
        'format': 'png',           # 保存为png
        'width': 1200,
        'height': 800,
        'scale': 2                 # 高分辨率
    }
    },
    animation_opts=dict(
        frame=dict(duration=frame_duration, redraw=False),
        transition=dict(duration=frame_transition, easing=easing_function),
        mode="immediate"
    )
)

# 在HTML的头部插入自定义CSS，确保平滑过渡
html_content = html_content.replace('</head>', f'{custom_css}</head>')

# 添加额外的JavaScript以确保平滑动画
animation_js = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    // 确保动画平滑的配置
    var config = {
        // 设置全局的Plotly配置
        displayModeBar: false,
        staticPlot: false
    };
    
    // 更新现有图表的配置
    if (window.Plotly) {
        var plots = document.querySelectorAll('.js-plotly-plot');
        plots.forEach(function(plot) {
            // 添加平滑处理
            applySmoothing(plot);
        });
    }
    
    // 应用平滑处理到所有动画元素
    function applySmoothing(container) {
        setTimeout(function() {
            // 获取所有图形元素和图像
            var allElements = container.querySelectorAll('.scatter, .lines, .points, .layer-above, .imagelayer');
            
            // 应用高级平滑设置
            allElements.forEach(function(el) {
                // 设置CSS属性以启用硬件加速和平滑过渡
                el.style.transition = 'all %dms linear';
                el.style.webkitTransition = 'all %dms linear';
                el.style.animationTimingFunction = 'linear';
                el.style.webkitAnimationTimingFunction = 'linear';
                el.style.transitionTimingFunction = 'linear';
                el.style.webkitTransitionTimingFunction = 'linear';
                el.style.willChange = 'transform, opacity';
                el.style.transform = 'translateZ(0)';
                
                // 防止闪烁
                el.style.backfaceVisibility = 'hidden';
                el.style.webkitBackfaceVisibility = 'hidden';
            });
            
            // 专门处理图像层，确保与数据点同步
            var images = container.querySelectorAll('.layer-above');
            var points = container.querySelectorAll('.points');
            
            // 尝试同步图像和点
            if (images.length > 0 && points.length > 0) {
                images.forEach(function(img) {
                    img.style.transition = 'all %dms linear';
                });
                
                points.forEach(function(point) {
                    point.style.transition = 'all %dms linear';
                });
            }
        }, 500); // 等待500ms确保图表完全加载
    }
});
</script>
""" % (frame_transition, frame_transition, frame_transition, frame_transition)

# 在HTML的</body>标签前插入自定义JavaScript
html_content = html_content.replace('</body>', f'{animation_js}</body>')

# 写入最终的HTML文件
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"动画保存至 {output_file}")
print(f"动画总时长: {target_duration_sec}秒 ({total_frames}帧，每帧{frame_duration}毫秒，过渡时间{frame_transition}毫秒)")

# 通过多层平滑处理和一致性检查解决闪烁问题
def ensure_frame_consistency(frames_data):
    """确保所有帧的数据连续性，防止闪烁"""
    if not frames_data or len(frames_data) <= 1:
        return frames_data
        
    # 检测异常帧 - 与前后帧相比发生突变的帧
    anomaly_frames = []
    for i in range(1, len(frames_data)-1):
        for trace_idx in range(len(frames_data[i].data)):
            # 跳过空的trace
            if not hasattr(frames_data[i].data[trace_idx], 'y') or not frames_data[i].data[trace_idx].y:
                continue
                
            # 跳过非线条数据
            if frames_data[i].data[trace_idx].mode != 'lines' and 'line' not in frames_data[i].data[trace_idx]:
                continue
                
            # 检查当前帧与前后帧的y值差异
            if hasattr(frames_data[i-1].data[trace_idx], 'y') and hasattr(frames_data[i+1].data[trace_idx], 'y'):
                # 确保有数据可比较
                if frames_data[i-1].data[trace_idx].y and frames_data[i+1].data[trace_idx].y and frames_data[i].data[trace_idx].y:
                    # 获取最后一个点作为比较点
                    y_prev = frames_data[i-1].data[trace_idx].y[-1] if frames_data[i-1].data[trace_idx].y else None
                    y_curr = frames_data[i].data[trace_idx].y[-1] if frames_data[i].data[trace_idx].y else None
                    y_next = frames_data[i+1].data[trace_idx].y[-1] if frames_data[i+1].data[trace_idx].y else None
                    
                    # 如果有数据可比较
                    if y_prev is not None and y_curr is not None and y_next is not None:
                        # 计算与前后帧的差异
                        diff_prev = abs(y_curr - y_prev)
                        diff_next = abs(y_next - y_curr)
                        avg_diff = (abs(y_next - y_prev)) / 2
                        
                        # 如果当前帧与前后帧差异很大，标记为异常
                        if diff_prev > 3 * avg_diff and diff_next > 3 * avg_diff:
                            if i not in anomaly_frames:
                                anomaly_frames.append(i)
                                break
    
    # 修复异常帧 - 使用前后帧的平均值
    print(f"检测到 {len(anomaly_frames)} 个异常帧，正在修复...")
    for i in anomaly_frames:
        for trace_idx in range(len(frames_data[i].data)):
            # 只处理有y值的trace
            if not hasattr(frames_data[i].data[trace_idx], 'y') or not frames_data[i].data[trace_idx].y:
                continue
                
            # 检查前后帧是否有数据
            if (hasattr(frames_data[i-1].data[trace_idx], 'y') and frames_data[i-1].data[trace_idx].y and
                hasattr(frames_data[i+1].data[trace_idx], 'y') and frames_data[i+1].data[trace_idx].y):
                
                # 使用前后帧的线性插值
                x_values = frames_data[i].data[trace_idx].x
                if len(x_values) == 0:  # 修复：使用长度检查替代 not x_values
                    continue
                    
                # 获取前后帧的对应y值
                interp_y = []
                for x_idx, x in enumerate(x_values):
                    # 在前一帧找到最接近的x值
                    prev_x = frames_data[i-1].data[trace_idx].x
                    prev_y = frames_data[i-1].data[trace_idx].y
                    next_x = frames_data[i+1].data[trace_idx].x
                    next_y = frames_data[i+1].data[trace_idx].y
                    
                    # 如果前后帧没有足够多的点，跳过
                    if len(prev_x) <= x_idx or len(prev_y) <= x_idx or len(next_x) <= x_idx or len(next_y) <= x_idx:
                        if len(interp_y) > 0:
                            interp_y.append(interp_y[-1])  # 使用上一个值
                        else:
                            interp_y.append(frames_data[i].data[trace_idx].y[x_idx])  # 保持原值
                        continue
                    
                    # 使用线性插值
                    interp_y.append((prev_y[x_idx] + next_y[x_idx]) / 2)
                
                # 更新异常帧的y值
                frames_data[i].data[trace_idx].y = interp_y
        
        # 修复y轴范围 - 使用前后帧的平均值
        if hasattr(frames_data[i].layout, 'yaxis') and hasattr(frames_data[i-1].layout, 'yaxis') and hasattr(frames_data[i+1].layout, 'yaxis'):
            if hasattr(frames_data[i].layout.yaxis, 'range') and hasattr(frames_data[i-1].layout.yaxis, 'range') and hasattr(frames_data[i+1].layout.yaxis, 'range'):
                prev_range = frames_data[i-1].layout.yaxis.range
                next_range = frames_data[i+1].layout.yaxis.range
                avg_range = [(prev_range[0] + next_range[0])/2, (prev_range[1] + next_range[1])/2]
                frames_data[i].layout.yaxis.range = avg_range
    
    # 确保图像连续性 - 修复突然消失的图像
    for i in range(1, len(frames_data)-1):
        prev_images = []
        next_images = []
        
        # 获取前后帧的图像
        if hasattr(frames_data[i-1].layout, 'images') and frames_data[i-1].layout.images:
            prev_images = frames_data[i-1].layout.images
        if hasattr(frames_data[i+1].layout, 'images') and frames_data[i+1].layout.images:
            next_images = frames_data[i+1].layout.images
        
        # 如果当前帧没有图像但前后帧有
        if (not hasattr(frames_data[i].layout, 'images') or not frames_data[i].layout.images) and prev_images and next_images:
            # 从前后帧合成图像
            merged_images = []
            
            # 为每个在前后帧都存在的图像创建插值版本
            prev_img_dict = {f"{img.x}_{img.y}": img for img in prev_images}
            next_img_dict = {f"{img.x}_{img.y}": img for img in next_images}
            
            # 添加前后帧都有的图像
            for key in prev_img_dict:
                if key in next_img_dict:
                    prev_img = prev_img_dict[key]
                    next_img = next_img_dict[key]
                    
                    # 创建插值图像
                    interp_img = dict(
                        source=prev_img.source,  # 使用前一帧的图像源
                        xref=prev_img.xref,
                        yref=prev_img.yref,
                        x=(prev_img.x + next_img.x) / 2,  # 位置插值
                        y=(prev_img.y + next_img.y) / 2,
                        sizex=prev_img.sizex,
                        sizey=prev_img.sizey,
                        xanchor=prev_img.xanchor,
                        yanchor=prev_img.yanchor,
                        sizing=prev_img.sizing,
                        opacity=prev_img.opacity,
                        layer=prev_img.layer
                    )
                    merged_images.append(interp_img)
            
            # 设置合成图像到当前帧
            if merged_images:
                frames_data[i].layout.images = merged_images
    
    return frames_data

# ... existing code ...
# 在最后的frames生成完成后，应用一致性检查
frames = ensure_frame_consistency(frames)
print(f"已完成 {len(frames)} 帧动画数据的一致性检查")

# 添加持久化保障机制
for i, frame in enumerate(frames):
    # 确保每个帧都有相同的数据元素数量
    if i > 0 and len(frame.data) != len(frames[0].data):
        # 如果当前帧的元素数量与第一帧不一致，从上一帧复制
        frame.data = frames[i-1].data
    
    # 确保所有图像元素都存在
    if hasattr(frames[0].layout, 'images') and frames[0].layout.images:
        if not hasattr(frame.layout, 'images') or not frame.layout.images:
            # 如果此帧没有图像但第一帧有，从上一帧复制
            if i > 0 and hasattr(frames[i-1].layout, 'images') and frames[i-1].layout.images:
                frame.layout.images = frames[i-1].layout.images

# 强制固定渲染元素数量
for i in range(len(frames)):
    if hasattr(frames[i], 'data'):
        # 确保所有trace都有配置
        for trace in frames[i].data:
            # 线条特性设置
            if 'line' not in trace and trace.mode == 'lines':
                trace.line = dict(shape='spline', smoothing=1.3)
            elif 'line' in trace and trace.mode == 'lines':
                trace.line.shape = 'spline'
                trace.line.smoothing = 1.3

# ... existing code ...
# 在生成HTML时添加额外的稳定性配置
custom_css = """
<style>
/* 全局设置 */
body {
  margin: 0;
  padding: 0;
  overflow: hidden;
}

/* Plotly容器设置 */
.js-plotly-plot {
  position: relative;
}

/* 防止闪烁的关键设置 */
.js-plotly-plot:not([data-unformatted]) .plotly .main-svg {
  transform: translateZ(0);
  backface-visibility: hidden;
  will-change: transform;
  contain: strict;
}

/* 图像层渲染稳定性设置 */
.js-plotly-plot .infolayer .images {
  contain: size layout paint;
  will-change: transform, opacity;
  transform: translateZ(0);
}

/* 线条和点渲染特殊处理 */
.js-plotly-plot .scatterlayer .trace {
  contain: strict;
  will-change: transform;
  transform-style: preserve-3d;
}

/* 曲线光滑渲染 */
.js-plotly-plot .scatterlayer .js-line {
  shape-rendering: geometricPrecision;
  stroke-linejoin: round;
  stroke-linecap: round;
  vector-effect: non-scaling-stroke;
}

/* SVG特定设置 */
svg path.lines, svg .point, svg circle, svg .layer-above image {
  transition: all 120ms linear !important;
  animation-timing-function: linear !important;
  vector-effect: non-scaling-stroke;
  shape-rendering: geometricPrecision;
}

/* 图像平滑设置 */
.smooth-animate-img {
  transition: y 100ms linear, opacity 100ms linear;
  will-change: transform, opacity;
  contain: strict;
}

/* 确保WebGL渲染器使用GPU加速 */
.gl-container {
  transform: translateZ(0);
  will-change: transform;
  contain: strict;
}

/* 动画控制按钮美化 */
.animation-controls {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 1000;
}

.animation-controls button {
  background: rgba(255,255,255,0.8);
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 5px 15px;
  margin: 0 5px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
}

.animation-controls button:hover {
  background: rgba(255,255,255,1);
  border-color: #aaa;
}

/* 确保所有文本清晰 */
text {
  font-smooth: always;
  -webkit-font-smoothing: antialiased;
}
</style>
"""

# ... existing code ...

# 添加防闪烁的JavaScript脚本
animation_js = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    // 全局配置
    var config = {
        displayModeBar: false,
        staticPlot: false
    };
    
    // 更新现有图表的配置
    if (window.Plotly) {
        var plots = document.querySelectorAll('.js-plotly-plot');
        plots.forEach(function(plot) {
            applyAntiFlickerMeasures(plot);
        });
    }
    
    // 应用防闪烁措施
    function applyAntiFlickerMeasures(container) {
        // 为图表元素添加contain属性，优化渲染性能
        container.style.contain = 'strict';
        
        // 准备防闪烁对象
        var antiFlicker = {
            // 存储前一帧的状态，用于检测异常变化
            previousFrameState: null,
            // 缓存每个轨迹的状态
            traceCache: {},
            // 记录异常帧，便于调试
            anomalyFrames: [],
            // 监听帧变化的处理函数
            handleFrameChange: function(frameIndex) {
                // 获取当前帧的所有轨迹
                var allTraces = container.querySelectorAll('.scatterlayer .trace');
                var currentState = {};
                
                // 收集当前帧状态
                allTraces.forEach(function(trace, idx) {
                    var points = trace.querySelectorAll('.point');
                    var lines = trace.querySelectorAll('.js-line');
                    
                    // 存储位置信息
                    currentState[idx] = {
                        points: Array.from(points).map(function(p) {
                            return { 
                                transform: p.getAttribute('transform'),
                                visible: p.style.visibility !== 'hidden'
                            };
                        }),
                        lines: Array.from(lines).map(function(l) {
                            return { 
                                d: l.getAttribute('d'),
                                visible: l.style.visibility !== 'hidden'
                            };
                        })
                    };
                });
                
                // 检查与上一帧的差异
                if (this.previousFrameState) {
                    var hasAnomalyDetected = false;
                    
                    // 检查每个轨迹
                    for (var idx in currentState) {
                        if (!this.previousFrameState[idx]) continue;
                        
                        // 检查点的剧烈变化
                        for (var i = 0; i < currentState[idx].points.length; i++) {
                            if (i >= this.previousFrameState[idx].points.length) continue;
                            
                            // 如果上一帧可见但当前帧不可见，可能是闪烁
                            if (this.previousFrameState[idx].points[i].visible && 
                                !currentState[idx].points[i].visible) {
                                // 记录异常并修复
                                if (!hasAnomalyDetected) {
                                    console.log('检测到异常帧: ' + frameIndex);
                                    this.anomalyFrames.push(frameIndex);
                                    hasAnomalyDetected = true;
                                }
                                
                                // 使用缓存状态修复
                                if (this.traceCache[idx] && this.traceCache[idx].points[i]) {
                                    var point = points[i];
                                    // 将点恢复为上一个已知的好状态
                                    point.setAttribute('transform', this.traceCache[idx].points[i].transform);
                                    point.style.visibility = 'visible';
                                    point.style.opacity = '1';
                                }
                            }
                        }
                        
                        // 检查线的剧烈变化
                        for (var i = 0; i < currentState[idx].lines.length; i++) {
                            if (i >= this.previousFrameState[idx].lines.length) continue;
                            
                            // 如果线段发生剧烈变化或消失
                            if (this.previousFrameState[idx].lines[i].visible && 
                                !currentState[idx].lines[i].visible) {
                                // 记录异常并修复
                                if (!hasAnomalyDetected) {
                                    console.log('检测到线条异常: ' + frameIndex);
                                    this.anomalyFrames.push(frameIndex);
                                    hasAnomalyDetected = true;
                                }
                                
                                // 使用缓存状态修复
                                if (this.traceCache[idx] && this.traceCache[idx].lines[i]) {
                                    var line = lines[i];
                                    // 将线恢复为上一个已知的好状态
                                    line.setAttribute('d', this.traceCache[idx].lines[i].d);
                                    line.style.visibility = 'visible';
                                    line.style.opacity = '1';
                                }
                            }
                        }
                    }
                    
                    // 检查图像层
                    var images = container.querySelectorAll('.layer-above image');
                    var previousImages = this.previousFrameState.images || [];
                    
                    // 如果前一帧有图像但当前帧没有，可能是闪烁
                    if (previousImages.length > 0 && images.length === 0) {
                        // 使用缓存恢复图像
                        if (this.traceCache.images && this.traceCache.images.length > 0) {
                            var imageContainer = container.querySelector('.layer-above');
                            this.traceCache.images.forEach(function(imgData) {
                                var img = document.createElementNS('http://www.w3.org/2000/svg', 'image');
                                for (var attr in imgData) {
                                    img.setAttribute(attr, imgData[attr]);
                                }
                                imageContainer.appendChild(img);
                            });
                        }
                    }
                }
                
                // 只有在没有检测到异常时更新缓存
                if (!hasAnomalyDetected) {
                    // 更新缓存状态
                    for (var idx in currentState) {
                        this.traceCache[idx] = JSON.parse(JSON.stringify(currentState[idx]));
                    }
                    
                    // 缓存图像状态
                    var images = container.querySelectorAll('.layer-above image');
                    if (images.length > 0) {
                        this.traceCache.images = Array.from(images).map(function(img) {
                            var attributes = {};
                            Array.from(img.attributes).forEach(function(attr) {
                                attributes[attr.name] = attr.value;
                            });
                            return attributes;
                        });
                    }
                    
                    // 更新状态
                    currentState.images = images.length;
                    this.previousFrameState = currentState;
                }
            }
        };
        
        // 存储防闪烁对象到容器
        container._antiFlicker = antiFlicker;
        
        // 为滑块添加事件监听
        var slider = document.getElementById('timeline-slider');
        if (slider) {
            slider.addEventListener('input', function(e) {
                var frameIndex = parseInt(e.target.value);
                container._antiFlicker.handleFrameChange(frameIndex);
            });
        }
        
        // 拦截animate方法，处理帧变化
        var originalAnimate = container.animate;
        if (originalAnimate) {
            container.animate = function() {
                var result = originalAnimate.apply(this, arguments);
                // 跟踪当前帧
                if (this._fullLayout && this._fullLayout._currentFrame) {
                    var frameIndex = parseInt(this._fullLayout._currentFrame.name);
                    this._antiFlicker.handleFrameChange(frameIndex);
                }
                return result;
            };
        }
        
        // 设置重要的CSS属性
        setTimeout(function() {
            var svgElements = container.querySelectorAll('svg');
            svgElements.forEach(function(svg) {
                svg.style.shapeRendering = 'geometricPrecision';
                svg.style.textRendering = 'geometricPrecision';
            });
            
            // 线条元素
            var lineElements = container.querySelectorAll('.scatterlayer .js-line');
            lineElements.forEach(function(el) {
                el.setAttribute('shape-rendering', 'geometricPrecision');
                el.setAttribute('stroke-linejoin', 'round');
                el.setAttribute('stroke-linecap', 'round');
                el.setAttribute('vector-effect', 'non-scaling-stroke');
            });
            
            // 点元素
            var pointElements = container.querySelectorAll('.scatterlayer .point');
            pointElements.forEach(function(el) {
                el.setAttribute('shape-rendering', 'geometricPrecision');
            });
            
            // 图像层元素
            var imageElements = container.querySelectorAll('.layer-above image');
            imageElements.forEach(function(el) {
                el.style.transform = 'translateZ(0)';
                el.style.willChange = 'transform';
            });
        }, 100);
    }
});
</script>
"""

# 在HTML的</body>标签前插入自定义JavaScript
html_content = html_content.replace('</body>', f'{animation_js}</body>')

# ... existing code ...

# 将动画帧间过渡时间增加，使动画更平滑
frame_transition = 100  # 增加过渡时间使动画更平滑，从0ms改为100ms

# 创建全局固定的y轴范围，防止突然变化
global_y_min = global_min_with_buffer
global_y_max = max(smoothed_y_max) * 1.1  # 使用所有帧最大值的110%，提供安全边界

print(f"锁定y轴范围: {global_y_min:.2f} 到 {global_y_max:.2f}")

# 对每个帧使用固定的y轴范围，确保稳定性
for i in range(len(frames)):
    if hasattr(frames[i].layout, 'yaxis') and hasattr(frames[i].layout.yaxis, 'range'):
        frames[i].layout.yaxis.range = [global_y_min, global_y_max]
        frames[i].layout.yaxis.autorange = False  # 禁用自动范围调整
        frames[i].layout.yaxis.fixedrange = True  # 禁止用户修改范围

# 确保初始布局也使用相同的固定范围
fig.update_layout(
    yaxis=dict(
        range=[global_y_min, global_y_max],
        autorange=False,
        fixedrange=True,
        title='Revenue (Million USD)'
    )
)

# 提高平滑度设置
for i in range(len(frames)):
    if hasattr(frames[i], 'data'):
        for trace in frames[i].data:
            if 'line' in trace and trace.mode and 'lines' in trace.mode:
                trace.line.shape = 'spline'
                trace.line.smoothing = 1.3  # 最大平滑度
                trace.line.simplify = False  # 禁用简化，保留所有点
                if 'width' in trace.line:
                    trace.line.width = max(2, trace.line.width)  # 确保线条足够粗

# 改进动画设置
animation_opts = dict(
    frame=dict(
        duration=frame_duration, 
        redraw=False  # 减少重绘次数
    ),
    transition=dict(
        duration=frame_transition,  
        easing='linear'  # 线性缓动确保平滑过渡
    ),
    mode="immediate"
)

# 更新全局动画配置
fig.update(
    frames=frames,  # 确保所有帧都被正确应用
    layout_updatemenus=[
        {
            "buttons": [
                {
                    "args": [None, {
                        "frame": {"duration": frame_duration, "redraw": False}, 
                        "fromcurrent": True,
                        "transition": {"duration": frame_transition, "easing": 'linear'},
                        "mode": "immediate"
                    }],
                    "label": "播放",
                    "method": "animate"
                },
                {
                    "args": [[None], {
                        "frame": {"duration": 0, "redraw": False}, 
                        "mode": "immediate", 
                        "transition": {"duration": 0}
                    }],
                    "label": "暂停",
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

# 改进HTML和CSS动画设置
custom_css = """
<style>
/* 全局设置 */
body {
  margin: 0;
  padding: 0;
  overflow: hidden;
}

/* Plotly容器设置 */
.js-plotly-plot {
  position: relative;
  transform: translateZ(0);
  will-change: transform;
  contain: layout style size;
}

/* 防止闪烁的关键设置 */
.js-plotly-plot .plotly .main-svg {
  transform: translateZ(0);
  backface-visibility: hidden;
  will-change: transform;
  contain: strict;
  transform-style: preserve-3d;
}

/* 图像层渲染稳定性设置 */
.js-plotly-plot .layer-above, .js-plotly-plot .imagelayer {
  contain: size layout paint style;
  will-change: transform;
  transform: translateZ(0);
  backface-visibility: hidden;
  transition: all 100ms linear !important;
}

/* 线条和点渲染特殊处理 */
.js-plotly-plot .scatterlayer .trace {
  contain: strict;
  will-change: transform;
  transform: translateZ(0);
}

/* 曲线光滑渲染 */
.js-plotly-plot .scatterlayer .js-line {
  shape-rendering: geometricPrecision;
  stroke-linejoin: round;
  stroke-linecap: round;
  vector-effect: non-scaling-stroke;
  transition: d 100ms linear !important;
}

/* 确保平滑动画过渡 */
.js-plotly-plot .scatterlayer path, 
.js-plotly-plot .imagelayer image,
.js-plotly-plot .trace,
.js-plotly-plot .point,
.js-plotly-plot .scatterlayer .points path {
  transition: all 100ms linear !important;
  animation-timing-function: linear !important;
  animation-duration: 100ms !important;
}

/* 强制平滑过渡效果 */
@keyframes smooth-fade {
  0% { opacity: 0.95; }
  100% { opacity: 1; }
}

.js-plotly-plot .scatterlayer .trace {
  animation: smooth-fade 100ms linear forwards;
}

/* 图层管理 - 确保图像始终在顶层 */
.js-plotly-plot .layer-above {
  z-index: 999 !important;
  pointer-events: none;
}

/* 确保Y轴稳定 */
.js-plotly-plot .yaxislayer-above {
  z-index: 0;
  transition: none !important;
  animation: none !important;
}

/* 动画平滑性增强 */
* {
  -webkit-transition-timing-function: linear !important;
  transition-timing-function: linear !important;
}
</style>
"""

# 增强JavaScript运行时防闪烁
animation_js = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    // 使用RequestAnimationFrame确保平滑动画
    let lastRender = 0;
    let isPaused = false;
    let plotDiv = document.querySelector('.js-plotly-plot');
    
    // 增强动画平滑性，将动画帧率最大化
    function optimizeAnimation() {
        // 强制固定y轴范围，防止自动调整
        const yaxisRange = [""" + str(global_y_min) + """, """ + str(global_y_max) + """];
        
        if (window.Plotly && plotDiv) {
            // 提供一个更平滑的动画控制器
            plotDiv._smoothAnimation = {
                frameNumber: 0,
                totalFrames: """ + str(len(frames)) + """,
                playing: false,
                
                // 平滑播放方法
                play: function() {
                    this.playing = true;
                    this.animate();
                },
                
                // 暂停方法
                pause: function() {
                    this.playing = false;
                },
                
                // 动画核心循环
                animate: function() {
                    if (!this.playing) return;
                    
                    // 使用动画帧实现更平滑的过渡
                    requestAnimationFrame(() => {
                        // 计算下一帧
                        this.frameNumber = (this.frameNumber + 1) % this.totalFrames;
                        
                        try {
                            // 强制y轴保持固定，避免突变
                            Plotly.relayout(plotDiv, {
                                'yaxis.range': yaxisRange,
                                'yaxis.autorange': false
                            });
                            
                            // 应用帧动画但保持y轴固定
                            Plotly.animate(plotDiv, [this.frameNumber.toString()], {
                                transition: {
                                    duration: """ + str(frame_transition) + """,
                                    easing: 'linear'
                                },
                                frame: {
                                    duration: """ + str(frame_duration) + """,
                                    redraw: false
                                }
                            }).then(() => {
                                // 确保图像层始终可见
                                const imageLayer = plotDiv.querySelector('.layer-above');
                                if (imageLayer) {
                                    imageLayer.style.opacity = '1';
                                    imageLayer.style.display = 'block';
                                }
                                
                                // 启动下一帧动画
                                if (this.playing) {
                                    this.animate();
                                }
                            });
                        } catch (e) {
                            console.error('Animation error:', e);
                            // 出错时仍然继续动画
                            if (this.playing) {
                                setTimeout(() => this.animate(), 10);
                            }
                        }
                    });
                }
            };
            
            // 监听原始播放按钮
            const playButton = document.querySelector('a[data-attr="play"]');
            const pauseButton = document.querySelector('a[data-attr="pause"]');
            
            if (playButton) {
                playButton.addEventListener('click', function() {
                    plotDiv._smoothAnimation.play();
                });
            }
            
            if (pauseButton) {
                pauseButton.addEventListener('click', function() {
                    plotDiv._smoothAnimation.pause();
                });
            }
            
            // 应用高级渲染优化
            applyRenderOptimizations();
        }
    }
    
    // 渲染优化函数
    function applyRenderOptimizations() {
        if (!plotDiv) return;
        
        // 强制启用图层合成
        plotDiv.style.transform = 'translateZ(0)';
        plotDiv.style.backfaceVisibility = 'hidden';
        plotDiv.style.perspective = '1000px';
        
        // 对图像层应用特殊处理
        const imageLayers = plotDiv.querySelectorAll('.layer-above, .imagelayer');
        imageLayers.forEach(layer => {
            layer.style.transform = 'translateZ(0)';
            layer.style.backfaceVisibility = 'hidden';
            layer.style.willChange = 'transform';
            layer.style.contain = 'strict';
            
            // 确保图像始终显示
            const images = layer.querySelectorAll('image');
            images.forEach(img => {
                img.style.transform = 'translateZ(0)';
                img.style.willChange = 'transform';
                img.style.transition = 'all 100ms linear';
            });
        });
        
        // 优化线条渲染
        const lines = plotDiv.querySelectorAll('.scatterlayer .js-line');
        lines.forEach(line => {
            line.style.shapeRendering = 'geometricPrecision';
            line.style.vectorEffect = 'non-scaling-stroke';
            line.setAttribute('stroke-linejoin', 'round');
            line.setAttribute('stroke-linecap', 'round');
        });
        
        // 添加高性能模式
        plotDiv.setAttribute('data-high-performance', 'true');
        document.body.classList.add('high-performance-animations');
    }
    
    // 强制实施稳定的Y轴范围
    function enforceStableYAxis() {
        if (!plotDiv) return;
        
        const yaxisRange = [""" + str(global_y_min) + """, """ + str(global_y_max) + """];
        
        // 强制锁定y轴范围
        Plotly.relayout(plotDiv, {
            'yaxis.range': yaxisRange,
            'yaxis.autorange': false,
            'yaxis.fixedrange': true
        });
        
        // 监听和拦截任何y轴变化尝试
        const observer = new MutationObserver(mutations => {
            mutations.forEach(mutation => {
                if (mutation.attributeName === 'transform' && 
                    mutation.target.closest('.yaxislayer-above')) {
                    Plotly.relayout(plotDiv, {
                        'yaxis.range': yaxisRange,
                        'yaxis.autorange': false,
                        'yaxis.fixedrange': true
                    });
                }
            });
        });
        
        // 观察y轴DOM变化
        const yaxisLayer = plotDiv.querySelector('.yaxislayer-above');
        if (yaxisLayer) {
            observer.observe(yaxisLayer, { attributes: true, subtree: true });
        }
    }
    
    // 等待页面加载完成后应用所有优化
    setTimeout(() => {
        optimizeAnimation();
        enforceStableYAxis();
        
        // 自动播放
        setTimeout(() => {
            if (plotDiv && plotDiv._smoothAnimation) {
                plotDiv._smoothAnimation.play();
            }
        }, 500);
    }, 300);
});
</script>
"""

# 在HTML的</body>标签前插入自定义JavaScript
html_content = html_content.replace('</body>', f'{animation_js}</body>')

# 在HTML的头部插入自定义CSS
html_content = html_content.replace('</head>', f'{custom_css}</head>')

# 保存最终的HTML文件
output_file = "output/airline_revenue_linechart.html"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"动画保存至 {output_file}")
print(f"动画总时长: {target_duration_sec}秒 ({total_frames}帧，每帧{frame_duration}毫秒，过渡时间{frame_transition}毫秒)")

# ... existing code ...

# 将动画帧间过渡时间减少，优化性能
frame_transition = 20  # 从100ms减少到20ms，减轻浏览器负担

# 减少动画控制器复杂度
animation_js = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    // 等待Plotly完全加载
    let waitForPlotly = setInterval(function() {
        if (window.Plotly) {
            clearInterval(waitForPlotly);
            initializeAnimation();
        }
    }, 100);
    
    function initializeAnimation() {
        const plotDiv = document.querySelector('.js-plotly-plot');
        if (!plotDiv) return;
        
        // 基本设置
        const yaxisRange = [""" + str(global_y_min) + """, """ + str(global_y_max) + """];
        
        // 创建一个高效的动画控制器
        const smoothAnimator = {
            isPlaying: false,
            currentFrameIndex: 0,
            totalFrames: """ + str(total_frames) + """,
            frameDuration: """ + str(frame_duration) + """,
            transitionDuration: """ + str(frame_transition) + """,
            lastTimestamp: 0,
            
            // 启动动画
            play: function() {
                if (this.isPlaying) return;
                
                this.isPlaying = true;
                this.lastTimestamp = 0;
                requestAnimationFrame(this.animate.bind(this));
                
                console.log('Animation started');
            },
            
            // 暂停动画
            pause: function() {
                this.isPlaying = false;
                console.log('Animation paused');
            },
            
            // 重置动画
            reset: function() {
                this.currentFrameIndex = 0;
                this.applyFrame(0, true);
                
                // 如果当前在播放，继续播放
                if (this.isPlaying) {
                    this.lastTimestamp = 0;
                    requestAnimationFrame(this.animate.bind(this));
                }
                
                console.log('Animation reset');
            },
            
            // 核心动画循环
            animate: function(timestamp) {
                if (!this.isPlaying) return;
                
                // 计算时间差
                if (!this.lastTimestamp) {
                    this.lastTimestamp = timestamp;
                }
                
                const elapsed = timestamp - this.lastTimestamp;
                
                // 控制帧率
                if (elapsed >= this.frameDuration) {
                    // 更新时间戳
                    this.lastTimestamp = timestamp;
                    
                    // 计算下一帧
                    this.currentFrameIndex = (this.currentFrameIndex + 1) % this.totalFrames;
                    
                    // 应用新帧
                    this.applyFrame(this.currentFrameIndex, false);
                }
                
                // 请求下一帧
                requestAnimationFrame(this.animate.bind(this));
            },
            
            // 应用指定帧
            applyFrame: function(frameIndex, immediate) {
                try {
                    // 强制锁定y轴范围
                    Plotly.relayout(plotDiv, {
                        'yaxis.range': yaxisRange,
                        'yaxis.autorange': false
                    });
                    
                    // 获取帧数据
                    const frame = plotDiv._transitionData._frames[frameIndex];
                    if (!frame) return;
                    
                    // 应用帧动画
                    const animationOpts = {
                        transition: {
                            duration: immediate ? 0 : this.transitionDuration,
                            easing: 'linear'
                        },
                        frame: {
                            duration: immediate ? 0 : this.frameDuration,
                            redraw: false
                        }
                    };
                    
                    Plotly.animate(plotDiv, [frameIndex.toString()], animationOpts);
                    
                    // 关键部分：强制更新图像位置
                    this.updateLogoPositions(frameIndex);
                    
                } catch (e) {
                    console.error('Error applying frame:', e);
                }
            },
            
            // 关键函数：同步Logo位置与数据点
            updateLogoPositions: function(frameIndex) {
                // 获取当前帧
                const frame = plotDiv._transitionData._frames[frameIndex];
                if (!frame || !frame.data) return;
                
                try {
                    // 找到带点的数据（每个航空公司的点）
                    const pointTraces = [];
                    
                    // 遍历所有trace找到markers
                    frame.data.forEach((trace, idx) => {
                        if (trace.mode && trace.mode.includes('markers')) {
                            pointTraces.push({
                                index: idx,
                                airline: trace.name,
                                x: trace.x[0],  // 通常只有一个点
                                y: trace.y[0]   // 通常只有一个点
                            });
                        }
                    });
                    
                    // 获取当前的image元素
                    const imageLayer = plotDiv.querySelector('.layer-above');
                    if (!imageLayer) return;
                    
                    const imageElements = imageLayer.querySelectorAll('image');
                    if (!imageElements.length) return;
                    
                    // 计算图表的数据到像素的转换
                    const xaxis = plotDiv._fullLayout.xaxis;
                    const yaxis = plotDiv._fullLayout.yaxis;
                    
                    // 处理每个图像
                    Array.from(imageElements).forEach((img, i) => {
                        // 找到对应的数据点
                        if (i < pointTraces.length) {
                            const trace = pointTraces[i];
                            
                            // 设置图像位置，与数据点关联
                            const logoX = trace.x + 0.05; // 稍微偏移
                            const logoY = trace.y;
                            
                            // 直接修改SVG属性，这比Plotly.relayout更高效
                            img.setAttribute('x', xaxis._l2p(logoX));
                            img.setAttribute('y', yaxis._l2p(logoY));
                            
                            // 确保过渡效果
                            img.style.transition = `transform ${this.transitionDuration}ms linear, x ${this.transitionDuration}ms linear, y ${this.transitionDuration}ms linear`;
                        }
                    });
                    
                } catch (e) {
                    console.error('Error updating logo positions:', e);
                }
            }
        };
        
        // 拦截原始播放按钮点击
        const buttons = plotDiv.querySelectorAll('a[data-attr="play"], .plotly-notifier button');
        buttons.forEach(button => {
            if (button) {
                const originalClick = button.onclick;
                button.onclick = function(e) {
                    // 阻止原始点击事件
                    e.preventDefault();
                    e.stopPropagation();
                    
                    // 使用我们的平滑播放器
                    smoothAnimator.play();
                    
                    return false;
                };
            }
        });
        
        // 添加自定义控制按钮
        const controlDiv = document.createElement('div');
        controlDiv.style.position = 'absolute';
        controlDiv.style.top = '10px';
        controlDiv.style.right = '10px';
        controlDiv.style.zIndex = '1000';
        
        const playBtn = document.createElement('button');
        playBtn.textContent = '播放';
        playBtn.style.marginRight = '5px';
        playBtn.onclick = function() {
            smoothAnimator.play();
        };
        
        const pauseBtn = document.createElement('button');
        pauseBtn.textContent = '暂停';
        pauseBtn.onclick = function() {
            smoothAnimator.pause();
        };
        
        controlDiv.appendChild(playBtn);
        controlDiv.appendChild(pauseBtn);
        plotDiv.appendChild(controlDiv);
        
        // 自动开始播放
        setTimeout(function() {
            smoothAnimator.play();
        }, 500);
    }
});
</script>
"""

# 简化CSS，启用过渡
custom_css = """
<style>
/* 全局设置 */
body {
  margin: 0;
  padding: 0;
}

/* 基本样式 */
.js-plotly-plot {
  position: relative;
}

/* 允许图像和元素移动的关键CSS */
.layer-above image {
  transition: x 20ms linear, y 20ms linear !important;
  will-change: x, y !important;
}

/* 确保点和线条也平滑过渡 */
.scatterlayer .trace path, 
.scatterlayer .point {
  transition: d 20ms linear, transform 20ms linear !important;
  will-change: d, transform !important;
}

/* 曲线光滑渲染 */
.js-plotly-plot .scatterlayer .js-line {
  shape-rendering: geometricPrecision;
  stroke-linejoin: round;
  stroke-linecap: round;
  vector-effect: non-scaling-stroke;
}

/* 动画控制按钮 */
.animation-controls button {
  background: rgba(255,255,255,0.8);
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 5px 15px;
  margin: 0 5px;
  cursor: pointer;
}
</style>
"""

# 创建更高效的HTML输出选项
optimized_config = {
    'responsive': True,
    'staticPlot': False,  # 不使用静态图，但后面会手动限制交互
    'displayModeBar': False,  # 隐藏模式栏
    'displaylogo': False,  # 不显示Plotly logo
    'showAxisDragHandles': False,  # 禁用轴拖拽
    'showTips': False,  # 不显示提示
    'doubleClick': False,  # 禁用双击
    'scrollZoom': False,  # 禁用滚轮缩放
    'showLink': False,     # 不显示链接
    'sendData': False,     # 不发送数据到Plotly
    'linkText': '',        # 空链接文本
    'showSources': False,  # 不显示源码
    'modeBarButtonsToRemove': ['zoom2d', 'pan2d', 'select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 
                              'autoScale2d', 'resetScale2d', 'toggleSpikelines', 
                              'hoverCompareCartesian', 'hoverClosestCartesian']  # 移除不需要的按钮
}

# 简化动画选项
animation_opts = dict(
    frame=dict(
        duration=frame_duration, 
        redraw=False  # 减少重绘次数
    ),
    transition=dict(
        duration=frame_transition,  
        easing='linear'  # 线性缓动确保平滑过渡
    ),
    mode="immediate"
)

# 生成更简化的HTML
html_content = pio.to_html(
    fig, 
    include_plotlyjs='cdn',  # 使用CDN版本减小文件大小
    full_html=True,
    config=optimized_config,
    animation_opts=animation_opts,
    validate=False,  # 跳过验证以加快生成
    auto_play=False  # 默认不自动播放，让用户手动控制
)

# 插入简化的CSS和JS
html_content = html_content.replace('</head>', f'{custom_css}</head>')
html_content = html_content.replace('</body>', f'{animation_js}</body>')

# 保存最终的HTML文件
output_file = "output/airline_revenue_linechart.html"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"已优化动画性能，保存至 {output_file}")
print(f"优化后的动画: 总时长{target_duration_sec}秒 ({total_frames}帧，过渡时间{frame_transition}毫秒)")

# 移除其他不必要的HTML文件生成代码
# ... existing code ...
# ... existing code ...