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

# 生成插值后的数值型x轴
quarters = revenue_data.index.tolist()
quarter_numeric = np.arange(len(quarters))
interp_steps = 5  # 从10降低到5，减少总帧数，使动画更快
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
global_ybuffer = (global_ymax - global_ymin) * 0.1
global_yaxis_range = [global_ymin - global_ybuffer, global_ymax + global_ybuffer]

# x轴tick设置
x_tickvals = quarter_numeric
x_ticktext = quarters

fixed_x = 0.8  # 点固定在x轴80%位置
num_frames = len(interp_x)

# 添加滑动窗口参数
window_size = 10  # 滑动窗口大小

# 计算每帧的y轴范围（滑动窗口）
all_frame_y_ranges = []
for i in range(num_frames):
    # 找出滑动窗口内的所有y值
    window_start = max(0, i - window_size + 1)
    window_y_vals = []
    for j in range(window_start, i+1):
        for airline in valid_airlines:
            window_y_vals.append(interp_revenue[airline][j])
    
    # 计算滑动窗口内的y轴范围
    if window_y_vals:
        ymin = min(window_y_vals)
        ymax = max(window_y_vals)
        ybuffer = (ymax - ymin) * 0.1 if ymax > ymin else 1
        yaxis_range = [ymin - ybuffer, ymax + ybuffer]
    else:
        # 防止空窗口
        yaxis_range = [0, 1]
    
    all_frame_y_ranges.append(yaxis_range)

# 生成动画帧，所有帧使用相同的全局y轴范围
frames = []
for i in range(num_frames):
    frame_data = []
    for airline in valid_airlines:
        # 线的x坐标：从0到fixed_x，y坐标为历史到当前
        x_hist = np.linspace(0, fixed_x, i+1)
        y_hist = interp_revenue[airline][:i+1]
        region = metadata.loc['Region', airline] if airline in metadata.columns else 'Unknown'
        color = region_colors.get(region, '#808080')
        frame_data.append(go.Scatter(x=x_hist, y=y_hist, mode='lines', name=airline,
                                    line=dict(color=color), hoverinfo='skip', showlegend=False))
        # 点固定在fixed_x，y为当前帧y
        nearest_q_idx = int(round(interp_x[i]))
        hovertext = quarters[nearest_q_idx] if 0 <= nearest_q_idx < len(quarters) else ''
        frame_data.append(go.Scatter(x=[fixed_x], y=[interp_revenue[airline][i]], mode='markers', name=airline,
                                    marker=dict(color=color, size=12), hoverinfo='text+y', text=[hovertext], showlegend=False))
    
    # 所有帧使用相同的全局y轴范围
    frames.append(go.Frame(data=frame_data, name=str(i)))

# 初始帧，使用相同的全局y轴范围
initial_data = []
for airline in valid_airlines:
    x_hist = np.linspace(0, fixed_x, 1)
    y_hist = interp_revenue[airline][:1]
    region = metadata.loc['Region', airline] if airline in metadata.columns else 'Unknown'
    color = region_colors.get(region, '#808080')
    initial_data.append(go.Scatter(x=x_hist, y=y_hist, mode='lines', name=airline,
                                line=dict(color=color), hoverinfo='skip', showlegend=False))
    initial_data.append(go.Scatter(x=[fixed_x], y=[interp_revenue[airline][0]], mode='markers', name=airline,
                                marker=dict(color=color, size=12), hoverinfo='text+y', text=[quarters[0]], showlegend=False))

logo_offset = 0.05  # logo在点右侧的x偏移
logo_size = 0.08   # logo高度（y轴范围的比例）

# 生成初始帧logo images
images = []
for airline in valid_airlines:
    # 取初始帧的y值
    y_val = interp_revenue[airline][0]
    # 取最新季度的年份和iata
    quarter_str = quarters[0]
    year = int(quarter_str[:4])
    iata_code = metadata.loc['IATA Code', airline] if 'IATA Code' in metadata.index else ''
    logo_path = get_logo_path(airline, year, iata_code)
    logo_data = get_encoded_image(logo_path)
    if logo_data:
        images.append(dict(
            source=logo_data,
            xref="x", yref="y",
            x=fixed_x+logo_offset, y=y_val+logo_size/2*(global_yaxis_range[1]-global_yaxis_range[0]),
            sizex=logo_offset, sizey=logo_size*(global_yaxis_range[1]-global_yaxis_range[0]),
            xanchor="left", yanchor="middle",
            sizing="contain",
            opacity=1,
            layer="above"
        ))

# Build figure
fig = go.Figure(
    data=initial_data,
    layout=go.Layout(
        title='Airline Revenue Over Time',
        xaxis=dict(title='', range=[0, 1], linecolor='gray', showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(title='Revenue (Million USD)', range=global_yaxis_range, linecolor='gray', showgrid=True, gridcolor='lightgray', griddash='dash', zeroline=False),
        plot_bgcolor='white',
        paper_bgcolor='white',
        images=images,
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
                     args=[None, {"frame": {"duration": 2, "redraw": True},  # 从10ms降到2ms
                                  "fromcurrent": True, "transition": {"duration": 0}}]),
                dict(label="Pause",
                     method="animate",
                     args=[[None], {"frame": {"duration": 0, "redraw": False},
                                    "mode": "immediate",
                                    "transition": {"duration": 0}}])
            ]
        )],
        sliders=[]
    ),
    frames=frames
)

# Save HTML
output_file = "output/airline_revenue_linechart.html"
pio.write_html(fig, file=output_file, auto_open=True)
output_file
