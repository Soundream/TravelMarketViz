import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd

def draw_harvey_ball(ax, x, y, percentage, size=0.1, color='black'):
    """绘制 Harvey Balls (0% - 100%)"""
    ax.add_patch(patches.Circle((x, y), size, color=color, fill=False))
    if percentage > 0:
        ax.add_patch(patches.Wedge((x, y), size, 90, 90 + 3.6 * percentage, color=color))

def normalize_values(values):
    """将数据归一化到 0%-100% 并匹配 Harvey Balls 等级"""
    min_val, max_val = values.min(), values.max()
    if max_val > min_val:
        return ((values - min_val) / (max_val - min_val) * 100).round()
    else:
        return 50  # 若所有值相等，则归一化为50%

def plot_harvey_balls_chart(df, categories, color_dict, company_abbr):
    """绘制 Harvey Balls 图表，按顺序排列数据，并在左侧添加公司缩写"""
    print("Columns:", categories)  # 在 Console 中打印列名
    print(df.to_string(index=False))  # 打印完整 DataFrame
    
    df = df.sort_values(by='Overall Score', ascending=False)  # 按 Overall Score 排序
    
    fig, ax = plt.subplots(figsize=(12, len(df) * 0.8))
    ax.set_xlim(-1, len(categories))
    ax.set_ylim(-1, len(df))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)
    
    for i, row in df.iterrows():
        company_abbreviation = company_abbr.get(row['Company'], row['Company'])
        ax.text(-0.8, len(df) - i - 1, company_abbreviation, fontsize=12, fontweight='bold', ha='right', fontfamily='monospace')  # 添加公司缩写
        for j, category in enumerate(categories):
            color = color_dict.get(row['Company'], 'black')
            draw_harvey_ball(ax, j, len(df) - i - 1, row[category], color=color)
    
    plt.show()

# Public 公司的 2024'Q3 数据
data = {
    'Company': ['Airbnb', 'Booking.com', 'Despegar', 'EaseMyTrip', 'Edreams', 'Lastminute', 'Seera Group', 'Trip.com', 'TripAdvisor', 'Trivago', 'Webjet', 'Yatra.com'],
    'Revenue': [3732, 7994, 193.9, 12.844471, 184.58, 500, 600, 2265, 532, 146.087, 700, 28.216],
    'EBITDA Margin': [0.464898, 0.358894, 0.037592, 0.34594, 0.11919, 0.2, 0.15, 0.437969, 0.12406, -0.125754, 0.25, -0.000035],
    'Revenue Growth': [0.098616, 0.088952, 0.088714, -0.115832, -0.010029, 0.05, 0.07, 0.201592, -0.001876, -0.07459, 0.03, 1.474003],
    'EBITDA Growth': [0.12, 0.10, 0.08, -0.05, 0.02, 0.06, 0.07, 0.14, 0.03, -0.02, 0.05, 0.08]
}

df = pd.DataFrame(data)
categories = ['Overall Score', 'Revenue', 'EBITDA Margin', 'Revenue Growth', 'EBITDA Growth']

# 计算 Overall Score
weights = {
    "Revenue": 0.35,
    "Revenue Growth": 0.15,
    "EBITDA Margin": 0.35,
    "EBITDA Growth": 0.15
}

for col in ['Revenue', 'Revenue Growth', 'EBITDA Margin', 'EBITDA Growth']:
    df[col] = normalize_values(df[col])

df['Overall Score'] = (
    df['Revenue'] * weights['Revenue'] +
    df['Revenue Growth'] * weights['Revenue Growth'] +
    df['EBITDA Margin'] * weights['EBITDA Margin'] +
    df['EBITDA Growth'] * weights['EBITDA Growth']
)

df = df.sort_values(by='Overall Score', ascending=False)

color_dict = {
    'Airbnb': '#ff5895', 'Booking.com': '#003480', 'Despegar': '#755bd8', 'EaseMyTrip': '#00a0e2',
    'Edreams': '#2577e3', 'Lastminute': '#fc03b1', 'Seera Group': '#750808', 'Trip.com': '#2577e3',
    'TripAdvisor': '#00af87', 'Trivago': '#e74c3c', 'Webjet': '#e74c3c', 'Yatra.com': '#e74c3c'
}

company_abbr = {
    "Airbnb": "ABNB", "Booking.com": "BKNG", "Despegar": "DESP", "EaseMyTrip": "EaseMyTrip",
    "Edreams": "EDR", "Lastminute": "LMN", "Seera Group": "SEERA", "Trip.com": "TCOM",
    "TripAdvisor": "TRIP", "Trivago": "TRVG", "Webjet": "Webjet", "Yatra.com": "Yatra"
}

plot_harvey_balls_chart(df, categories, color_dict, company_abbr)
