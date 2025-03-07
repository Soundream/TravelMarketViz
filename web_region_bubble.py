import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from matplotlib.image import imread

# 配置参数
REGION_COLORS = {
    'Asia-Pacific': '#FF4B4B',
    'Europe': '#4169E1',
    'Eastern Europe': '#9370DB',
    'Latin America': '#32CD32',
    'Middle East': '#DEB887',
    'North America': '#40E0D0'
}

BOOKINGS_SCALE_FACTOR = 1e-9
MIN_BUBBLE_SIZE = 100
MAX_BUBBLE_SIZE = 2000

def get_era_text(year):
    """获取年份对应的时代背景文本"""
    year = int(year)
    if 2005 <= year <= 2007:
        return "Growth of WWW"
    elif 2007 <= year <= 2008:
        return "Great Recession"
    elif 2009 <= year <= 2018:
        return "Growth of Mobile"
    elif 2019 <= year <= 2020:
        return "Global Pandemic"
    elif 2021 <= year <= 2023:
        return "Post-Pandemic Recovery"
    return ""

def process_data(excel_path):
    """处理Excel数据"""
    # 读取Excel文件，指定sheet_name
    df = pd.read_excel(excel_path, sheet_name='Visualization Data')
    
    # 重命名地区
    df['Region'] = df['Region'].replace({
        'APAC': 'Asia-Pacific',
        'LATAM': 'Latin America'
    })
    
    # 按年份和地区分组计算
    grouped = df.groupby(['Year', 'Region']).agg({
        'Gross Bookings': 'sum',
        'Online Bookings': 'sum'
    }).reset_index()
    
    # 计算在线渗透率
    grouped['Online Penetration'] = grouped['Online Bookings'] / grouped['Gross Bookings']
    
    # 应用缩放因子
    grouped['Gross Bookings_Scaled'] = grouped['Gross Bookings'] * BOOKINGS_SCALE_FACTOR
    grouped['Online Bookings_Scaled'] = grouped['Online Bookings'] * BOOKINGS_SCALE_FACTOR
    
    return grouped

def create_bubble_chart(data, year, output_dir):
    """为特定年份创建气泡图"""
    year_data = data[data['Year'] == year]
    
    # 创建图形
    plt.figure(figsize=(16, 9), dpi=100)
    
    # 设置背景色为白色
    plt.gca().set_facecolor('#ffffff')
    plt.gcf().set_facecolor('#ffffff')
    
    # 去掉边框
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)
    
    # 添加世界地图背景
    try:
        world_map = imread('wit/web_region_bubble/assets/world-map.png')
        plt.imshow(world_map, extent=[0, 100, 0, data['Online Bookings_Scaled'].max() * 1.1],
                  aspect='auto', alpha=0.15, zorder=0)
    except:
        print("Warning: Could not load world map background")
    
    # 绘制时代背景文字（居中且更大）
    plt.text(0.5, 0.5, get_era_text(year),
             fontsize=60, alpha=0.15,
             ha='center', va='center',
             transform=plt.gca().transAxes)
    
    # 绘制气泡
    for _, row in year_data.iterrows():
        # 使用与原始JavaScript相同的气泡大小计算方式
        size = np.sqrt(row['Gross Bookings_Scaled']) * 3
        size = np.clip(size, 15, 80)  # 使用原始的最小/最大值
        # 由于matplotlib和plotly的大小单位不同，需要调整系数
        size = size * 200  # 调整系数使大小更接近原始效果
        
        plt.scatter(row['Online Penetration'] * 100,
                   row['Online Bookings_Scaled'],
                   s=size,
                   c=REGION_COLORS[row['Region']],
                   alpha=0.75,  # 使用原始的透明度
                   edgecolor='white',
                   linewidth=1.5,  # 使用原始的线宽
                   zorder=2)
    
    # 设置轴标签
    plt.xlabel('Share of Online Bookings (%)', fontsize=12)
    plt.ylabel('Online Bookings (USD bn)', fontsize=12)
    
    # 设置轴范围
    plt.xlim(-5, 105)  # 使用原始的轴范围
    
    # 设置非均匀的y轴刻度
    max_value = data['Online Bookings_Scaled'].max()
    custom_ticks = [0, 10, 40, 90, 160, 250, 400, 600, 800, 1000]  # 使用原始的刻度值
    custom_ticks = [t for t in custom_ticks if t <= max_value * 1.1]
    plt.yticks(custom_ticks)
    plt.ylim(0, max_value * 1.1)
    
    # 添加网格线（只显示水平线）
    plt.grid(True, axis='y', alpha=0.2, linestyle='--', color='#eee')  # 使用原始的网格线颜色
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片（使用白色背景）
    output_path = os.path.join(output_dir, f'frame_{year}.png')
    plt.savefig(output_path, bbox_inches='tight', dpi=100, transparent=False, facecolor='white')
    plt.close()
    
    return output_path

def main():
    # 创建输出目录
    output_dir = 'frames'
    os.makedirs(output_dir, exist_ok=True)
    
    # 读取和处理数据
    data = process_data('wit/web_region_bubble/travel_market_summary.xlsx')
    
    # 获取所有年份
    years = sorted(data['Year'].unique())
    
    # 为每一年创建一帧
    frame_files = []
    for year in years:
        frame_path = create_bubble_chart(data, year, output_dir)
        frame_files.append(frame_path)
        print(f"Generated frame for year {year}")
    
    print(f"\nGenerated {len(frame_files)} frames in {output_dir}/")
    print("You can use these frames to create a video using ffmpeg:")
    print(f"ffmpeg -framerate 1 -pattern_type glob -i '{output_dir}/frame_*.png' -c:v libx264 -pix_fmt yuv420p -r 30 travel_market_evolution.mp4")

if __name__ == '__main__':
    main() 