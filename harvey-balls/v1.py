import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd

def draw_harvey_ball(ax, x, y, percentage, size=0.1):
    """绘制 Harvey Balls (0% - 100%)"""
    ax.add_patch(patches.Circle((x, y), size, color='black', fill=False))
    if percentage > 0:
        ax.add_patch(patches.Wedge((x, y), size, 90, 90 + 3.6 * percentage, color='black'))

def normalize_values(values):
    """将数据归一化到 0%-100% 并匹配 Harvey Balls 等级"""
    min_val, max_val = values.min(), values.max()
    return ((values - min_val) / (max_val - min_val) * 100).round()

def plot_harvey_balls_chart(df, categories):
    """绘制 Harvey Balls 图表"""
    fig, ax = plt.subplots(figsize=(10, len(df) * 0.5))
    ax.set_xlim(-1, len(categories))
    ax.set_ylim(-1, len(df))
    ax.set_xticks(range(len(categories)))
    ax.set_xticklabels(categories, fontsize=12)
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(df['Company'], fontsize=12)
    
    for i, row in df.iterrows():
        for j, category in enumerate(categories):
            draw_harvey_ball(ax, j, len(df) - i - 1, row[category])
    
    ax.set_xticklabels(categories, fontsize=12, rotation=45)
    ax.set_yticklabels(df['Company'], fontsize=12)
    ax.set_frame_on(False)
    ax.set_xticks([])
    ax.set_yticks([])
    
    plt.show()

# 示例数据
data = {
    'Company': ['Company A', 'Company B', 'Company C', 'Company D', 'Company E'],
    'Revenue': [500, 1200, 800, 950, 700],
    'EBITDA': [200, 500, 300, 400, 250],
    'Revenue Growth': [5, 12, 8, 10, 6],
    'EBITDA Growth': [3, 8, 6, 7, 4],
    'Overall Score': [60, 85, 75, 80, 65]
}

df = pd.DataFrame(data)
categories = ['Revenue', 'EBITDA', 'Revenue Growth', 'EBITDA Growth', 'Overall Score']

# 归一化数据并计算 Harvey Balls 评分
for col in categories:
    df[col] = normalize_values(df[col])

# 绘制 Harvey Balls 图表
plot_harvey_balls_chart(df, categories)
