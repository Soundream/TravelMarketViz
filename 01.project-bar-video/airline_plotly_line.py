import pandas as pd
import os
import plotly.graph_objs as go
import plotly.io as pio
import numpy as np

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

# 只显示最新季度收入前8的公司
latest_quarter = revenue_data.index[-1]
top_airlines = revenue_data.loc[latest_quarter].sort_values(ascending=False).head(8).index.tolist()
revenue_data = revenue_data[top_airlines]
valid_airlines = top_airlines

# 打印有效的航空公司名称
print("仅显示前8大航空公司:", valid_airlines)

# 创建航空公司名称映射表，解决名称不一致问题
airline_name_mapping = {
    "Norwegian Air Shuttle": "Norwegian",
    "Deutsche Lufthansa": "Lufthansa"
}

# 反向映射表
reverse_mapping = {v: k for k, v in airline_name_mapping.items()}

# 根据映射表调整有效航空公司名称
mapped_valid_airlines = set()
for airline in valid_airlines:
    mapped_valid_airlines.add(airline)
    if airline in airline_name_mapping:
        mapped_valid_airlines.add(airline_name_mapping[airline])

# 打印有效的航空公司
print("Valid airlines:", valid_airlines)
print("Mapped valid airlines:", mapped_valid_airlines)

# 生成插值后的数值型x轴
quarters = revenue_data.index.tolist()
quarter_numeric = np.arange(len(quarters))
interp_steps = 4
interp_x = np.linspace(0, len(quarters)-1, num=(len(quarters)-1)*interp_steps+1)

# 计算帧数
total_frames = (len(quarters)-1)*interp_steps+1
print(f"总帧数: {total_frames}")

# 根据总时长和总帧数计算帧持续时间
target_duration_sec = 60
frame_duration = int(target_duration_sec * 1000 / total_frames)
print(f"每帧持续时间: {frame_duration}毫秒")

# 设置过渡时间
frame_transition = max(frame_duration - 10, 10)

# 对每家公司的数据做线性插值
interp_revenue = {}
for airline in valid_airlines:
    y = revenue_data[airline].values
    interp_y = np.interp(interp_x, quarter_numeric, y)
    interp_revenue[airline] = interp_y

# 计算全局y轴固定范围（适用于所有帧）
# y轴最小值设为0
y_min = 0
# 计算出所有帧数据中的最大值并增加20%的缓冲
all_values = []
for airline in valid_airlines:
    all_values.extend(interp_revenue[airline])
y_max = max(all_values) * 1.2

print(f"固定Y轴范围: {y_min} 到 {y_max:.2f}")

# 创建初始数据
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
        uid=f"{airline}_line"
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
        uid=f"{airline}_point"
    ))

# 创建帧
frames = []
fixed_x = 0.8  # 点固定在x轴80%位置

# 创建基础数据框架
base_frame_data = []
for airline in valid_airlines:
    region = metadata.loc['Region', airline] if airline in metadata.columns else 'Unknown'
    color = region_colors.get(region, '#808080')
    
    # 线
    base_frame_data.append(go.Scatter(
        x=[], y=[], 
        mode='lines', 
        name=airline,
        line=dict(color=color, width=2, shape='spline', smoothing=1.3), 
        hoverinfo='skip', 
        showlegend=False,
        uid=f"{airline}_line"
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
        uid=f"{airline}_point"
    ))

# 创建帧数据
for i in range(len(interp_x)):
    # 复制基础数据结构
    frame_data = []
    for base_trace in base_frame_data:
        # 获取基础属性
        line_props = {} if 'line' not in base_trace else base_trace['line']
        marker_props = {} if 'marker' not in base_trace else base_trace['marker']
        
        # 创建新的trace
        new_trace = go.Scatter(
            x=[], 
            y=[], 
            mode=base_trace['mode'] if 'mode' in base_trace else 'lines',
            name=base_trace['name'] if 'name' in base_trace else '',
            line=line_props,
            marker=marker_props,
            hoverinfo=base_trace['hoverinfo'] if 'hoverinfo' in base_trace else 'all',
            showlegend=base_trace['showlegend'] if 'showlegend' in base_trace else False,
            uid=base_trace['uid'] if 'uid' in base_trace else None
        )
        frame_data.append(new_trace)
    
    # 获取当前帧的时间点
    nearest_q_idx = min(int(round(interp_x[i])), len(quarters)-1)
    current_quarter = quarters[nearest_q_idx]
    
    # 为每个航空公司生成线和点
    for idx, airline in enumerate(valid_airlines):
        # 线的x坐标：从0到fixed_x
        x_hist = np.linspace(0, fixed_x, i+1)
        
        # 线的y坐标
        y_hist = list(interp_revenue[airline][:i+1])
        
        region = metadata.loc['Region', airline] if airline in metadata.columns else 'Unknown'
        color = region_colors.get(region, '#808080')
        
        # 更新线的数据
        line_trace_idx = idx * 2
        point_trace_idx = idx * 2 + 1
        
        if line_trace_idx < len(frame_data):
            frame_data[line_trace_idx]['x'] = x_hist
            frame_data[line_trace_idx]['y'] = y_hist
            if 'line' not in frame_data[line_trace_idx]:
                frame_data[line_trace_idx]['line'] = {}
            frame_data[line_trace_idx]['line']['color'] = color
            frame_data[line_trace_idx]['line']['shape'] = 'spline'
            frame_data[line_trace_idx]['line']['smoothing'] = 1.3

        # 更新点的数据
        if point_trace_idx < len(frame_data):
            frame_data[point_trace_idx]['x'] = [fixed_x]
            frame_data[point_trace_idx]['y'] = [y_hist[-1]]
            frame_data[point_trace_idx]['text'] = [current_quarter]
            if 'marker' not in frame_data[point_trace_idx]:
                frame_data[point_trace_idx]['marker'] = {}
            frame_data[point_trace_idx]['marker']['color'] = color
            frame_data[point_trace_idx]['marker']['size'] = 12
    
    # 创建当前帧的布局，使用固定的y轴范围
    custom_layout = go.Layout(
        yaxis=dict(
            range=[y_min, y_max],  # 使用固定Y轴范围，防止抖动
            title='Revenue (Million USD)',
            linecolor='gray', 
            showgrid=True, 
            gridcolor='lightgray', 
            griddash='dash', 
            zeroline=False,
            fixedrange=True,
            autorange=False  # 禁用自动范围调整
        ),
        xaxis=dict(
            fixedrange=True,
            autorange=False  # 禁用自动范围调整
        )
    )
    
    # 添加帧
    frames.append(go.Frame(
        data=frame_data, 
        name=str(i),
        layout=custom_layout
    ))

# 初始帧数据
initial_data = []
for idx, airline in enumerate(valid_airlines):
    x_hist = np.linspace(0, fixed_x, 1)
    
    # 获取初始位置
    initial_y = interp_revenue[airline][0]
    
    y_hist = [initial_y]
    region = metadata.loc['Region', airline] if airline in metadata.columns else 'Unknown'
    color = region_colors.get(region, '#808080')
    
    initial_data.append(go.Scatter(
        x=x_hist, 
        y=y_hist, 
        mode='lines', 
        name=airline,
        line=dict(color=color, shape='spline', smoothing=1.3), 
        hoverinfo='skip', 
        showlegend=False,
        uid=f"{airline}_line"
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
        uid=f"{airline}_point"
    ))

# 构建图表
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
            fixedrange=True,
            autorange=False  # 禁用自动范围调整
        ),
        yaxis=dict(
            title='Revenue (Million USD)', 
            range=[y_min, y_max],  # 使用固定Y轴范围，防止抖动
            linecolor='gray', 
            showgrid=True, 
            gridcolor='lightgray', 
            griddash='dash', 
            zeroline=False,
            fixedrange=True,
            autorange=False  # 禁用自动范围调整
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
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
                         "transition": {"duration": frame_transition, "easing": "linear"},
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
        # 固定图表宽高比，避免图表尺寸变化引起的抖动
        height=600,
        width=800,
        margin=dict(l=50, r=50, t=80, b=50)
    ),
    frames=frames
)

# 设置HTML输出配置
output_file = "output/airline_revenue_linechart.html"
html_content = pio.to_html(
    fig, 
    include_plotlyjs='cdn',
    full_html=True,
    config={
        'responsive': True,
        'showAxisDragHandles': False,
        'staticPlot': False,
        'displayModeBar': False,
        'displaylogo': False,
        'scrollZoom': False,
        'doubleClick': False,
        'toImageButtonOptions': {
            'format': 'png',
            'width': 1200,
            'height': 800,
            'scale': 2
        }
    },
    animation_opts=dict(
        frame=dict(duration=frame_duration, redraw=False),
        transition=dict(duration=frame_transition, easing="linear"),
        mode="immediate"
    )
)

# 添加简单的CSS优化动画
custom_css = """
<style>
/* 简化全局设置 */
.js-plotly-plot {
  position: relative;
}

/* 为线条和点提供平滑过渡 */
.scatterlayer .trace {
  transition: transform 20ms linear !important;
}

/* 曲线光滑渲染 */
.js-plotly-plot .scatterlayer .js-line {
  shape-rendering: geometricPrecision;
  stroke-linejoin: round;
  stroke-linecap: round;
  vector-effect: non-scaling-stroke;
}

/* 防止坐标轴抖动 */
.js-plotly-plot .yaxislayer-above {
  transition: none !important;
  animation: none !important;
}
</style>
"""

# 添加坐标轴稳定性JavaScript
axis_stabilizer_js = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    // 稳定坐标轴的脚本
    const plotDiv = document.querySelector('.js-plotly-plot');
    if (plotDiv) {
        // 确保y轴范围固定
        const yAxisRange = [""" + str(y_min) + """, """ + str(y_max) + """];
        
        // 强制锁定y轴范围
        function enforceAxisRange() {
            Plotly.relayout(plotDiv, {
                'yaxis.range': yAxisRange,
                'yaxis.autorange': false,
                'yaxis.fixedrange': true
            });
        }
        
        // 在页面加载和动画每一帧后应用
        enforceAxisRange();
        
        // 监听动画事件
        plotDiv.on('plotly_animatingframe', function() {
            enforceAxisRange();
        });
    }
});
</script>
"""

# 插入CSS和JavaScript
html_content = html_content.replace('</head>', f'{custom_css}</head>')
html_content = html_content.replace('</body>', f'{axis_stabilizer_js}</body>')

# 保存最终的HTML文件
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"动画保存至 {output_file}")
print(f"动画总时长: {target_duration_sec}秒 ({total_frames}帧，每帧{frame_duration}毫秒)")
print(f"使用固定Y轴范围: {y_min} 到 {y_max:.2f}，避免坐标轴抖动")