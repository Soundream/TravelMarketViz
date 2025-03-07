import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

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
MIN_BUBBLE_SIZE = 15
MAX_BUBBLE_SIZE = 80

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
    # 读取Excel文件
    df = pd.read_excel(excel_path)
    
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

def create_bubble_chart(data):
    """创建交互式气泡图"""
    years = sorted(data['Year'].unique())
    
    # 创建图形
    fig = go.Figure()
    
    # 为每个年份创建一帧
    frames = []
    for year in years:
        year_data = data[data['Year'] == year]
        
        frame = go.Frame(
            data=[
                # 背景文字
                go.Scatter(
                    x=[50],
                    y=[40],
                    mode='text',
                    text=[get_era_text(year)],
                    textfont=dict(
                        size=60,
                        family='Arial',
                        color='rgba(200,200,200,0.3)'
                    ),
                    showlegend=False,
                    hoverinfo='skip'
                )
            ] +
            [
                # 每个地区的气泡
                go.Scatter(
                    x=[row['Online Penetration'] * 100],
                    y=[row['Online Bookings_Scaled']],
                    mode='markers',
                    name=region,
                    marker=dict(
                        size=np.sqrt(row['Gross Bookings_Scaled']) * 3,
                        sizemin=MIN_BUBBLE_SIZE,
                        sizemax=MAX_BUBBLE_SIZE,
                        color=REGION_COLORS[region],
                        opacity=0.75,
                        line=dict(
                            color='rgba(255, 255, 255, 0.8)',
                            width=1.5
                        )
                    ),
                    hovertemplate=(
                        f"<b>{region}</b><br>" +
                        "Share of Online Bookings: %{x:.1f}%<br>" +
                        "Online Bookings: $%{y:.1f}B<br>" +
                        f"Gross Bookings: ${row['Gross_Bookings_Scaled']:.1f}B<br>" +
                        "<extra></extra>"
                    )
                )
                for _, row in year_data.iterrows()
                for region in [row['Region']]
            ],
            name=str(year)
        )
        frames.append(frame)
    
    # 设置初始显示（使用第一年的数据）
    first_year_data = data[data['Year'] == years[0]]
    
    # 添加背景文字
    fig.add_trace(
        go.Scatter(
            x=[50],
            y=[40],
            mode='text',
            text=[get_era_text(years[0])],
            textfont=dict(
                size=60,
                family='Arial',
                color='rgba(200,200,200,0.3)'
            ),
            showlegend=False,
            hoverinfo='skip'
        )
    )
    
    # 添加初始气泡
    for _, row in first_year_data.iterrows():
        fig.add_trace(
            go.Scatter(
                x=[row['Online Penetration'] * 100],
                y=[row['Online Bookings_Scaled']],
                mode='markers',
                name=row['Region'],
                marker=dict(
                    size=np.sqrt(row['Gross_Bookings_Scaled']) * 3,
                    sizemin=MIN_BUBBLE_SIZE,
                    sizemax=MAX_BUBBLE_SIZE,
                    color=REGION_COLORS[row['Region']],
                    opacity=0.75,
                    line=dict(
                        color='rgba(255, 255, 255, 0.8)',
                        width=1.5
                    )
                ),
                hovertemplate=(
                    f"<b>{row['Region']}</b><br>" +
                    "Share of Online Bookings: %{x:.1f}%<br>" +
                    "Online Bookings: $%{y:.1f}B<br>" +
                    f"Gross Bookings: ${row['Gross_Bookings_Scaled']:.1f}B<br>" +
                    "<extra></extra>"
                )
            )
        )
    
    # 更新布局
    fig.update_layout(
        title='Travel Market Evolution',
        xaxis=dict(
            title='Share of Online Bookings (%)',
            range=[0, 100]
        ),
        yaxis=dict(
            title='Online Bookings (USD bn)',
            range=[0, data['Online Bookings_Scaled'].max() * 1.1]
        ),
        showlegend=True,
        updatemenus=[
            {
                'type': 'buttons',
                'showactive': False,
                'buttons': [
                    {
                        'label': 'Play',
                        'method': 'animate',
                        'args': [None, {
                            'frame': {'duration': 800, 'redraw': True},
                            'fromcurrent': True,
                            'transition': {'duration': 300}
                        }]
                    },
                    {
                        'label': 'Pause',
                        'method': 'animate',
                        'args': [[None], {
                            'frame': {'duration': 0, 'redraw': False},
                            'mode': 'immediate',
                            'transition': {'duration': 0}
                        }]
                    }
                ]
            }
        ],
        sliders=[{
            'currentvalue': {'prefix': 'Year: '},
            'steps': [
                {
                    'label': str(year),
                    'method': 'animate',
                    'args': [[str(year)], {
                        'frame': {'duration': 300, 'redraw': True},
                        'mode': 'immediate',
                        'transition': {'duration': 300}
                    }]
                }
                for year in years
            ]
        }]
    )
    
    # 添加帧
    fig.frames = frames
    
    return fig

def main():
    # 读取和处理数据
    data = process_data('wit/web_region_bubble/travel_market_summary.xlsx')
    
    # 创建可视化
    fig = create_bubble_chart(data)
    
    # 保存为HTML文件
    fig.write_html('travel_market_bubble.html')

if __name__ == '__main__':
    main() 