#!/usr/bin/env python
import os
import argparse
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from PIL import Image
import plotly.express as px
import plotly.io as pio
from tqdm import tqdm
import warnings
import base64
import webbrowser
from pathlib import Path
import json
warnings.filterwarnings('ignore')

# Add argument parser
parser = argparse.ArgumentParser(description='Generate travel company revenue visualization using Plotly')
parser.add_argument('--output', type=str, default='output/travel_revenue_plotly.html', 
                    help='Output HTML file path')
parser.add_argument('--frames-per-year', type=int, default=4, 
                    help='Number of frames to generate per year (default: 4 for quarterly)')
parser.add_argument('--height', type=int, default=800, 
                    help='Height of the visualization in pixels (default: 800)')
parser.add_argument('--width', type=int, default=1600, 
                    help='Width of the visualization in pixels (default: 1600)')
parser.add_argument('--max-companies', type=int, default=15, 
                    help='Maximum number of companies to display (default: 15)')
parser.add_argument('--transition-duration', type=int, default=500, 
                    help='Transition duration between frames in ms (default: 500)')
args = parser.parse_args()

# Create required directories
output_dir = os.path.dirname(args.output)
if output_dir and not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Created directory: {output_dir}")

# Update region colors
region_colors = {
    'North America': '#778899',  # 灰蓝色
    'Europe': '#778899',         # 灰蓝色
    'Asia Pacific': '#778899',   # 灰蓝色
    'Latin America': '#778899',  # 灰蓝色
    'China': '#2577e3',          # 蓝色（与TCOM相同）
    'Middle East': '#778899',    # 灰蓝色
    'India': '#e74c3c',          # 红色（与印度公司相同）
    'Australia': '#e74c3c'       # 红色（与Webjet相同）
}

# Company specific color configuration
company_colors = {
    'ABNB': '#778899',      # 灰蓝色
    'BKNG': '#778899',      # 灰蓝色
    'PCLN': '#778899',      # 灰蓝色
    'DESP': '#778899',      # 灰蓝色
    'EASEMYTRIP': '#00a0e2', # 浅蓝色
    'EaseMyTrip': '#00a0e2', # 浅蓝色
    'EDR': '#778899',       # 灰蓝色
    'EXPE': '#778899',      # 灰蓝色
    'LMN': '#778899',       # 灰蓝色
    'MMYT': '#e74c3c',      # 红色
    'OWW': '#778899',       # 灰蓝色
    'SEERA': '#778899',     # 灰蓝色
    'TCOM': '#2577e3',      # 蓝色
    'TRIP': '#778899',      # 灰蓝色
    'TRVG': '#778899',      # 灰蓝色
    'WBJ': '#e74c3c',       # 红色
    'Webjet': '#e74c3c',    # 红色
    'YTRA': '#e74c3c',      # 红色
    'Yatra': '#e74c3c',     # 红色
    'IXIGO': '#e74c3c',     # 红色
    'Ixigo': '#e74c3c',     # 红色
    'FLT': '#e74c3c',       # 红色
    'LONG': '#E60010',      # 红色 (RGB 230,0,16)
    'TCEL': '#5B318F'       # 紫色 (RGB 91,49,143)
}

# Define ticker to company name mapping
ticker_to_company = {
    'ABNB': 'Airbnb',
    'BKNG': 'Booking Holdings',
    'PCLN': 'Priceline',
    'DESP': 'Despegar',
    'EASEMYTRIP': 'EaseMyTrip',
    'EDR': 'Endeavor',
    'EXPE': 'Expedia',
    'LMN': 'Lastminute.com',
    'MMYT': 'MakeMyTrip',
    'OWW': 'Orbitz Worldwide',
    'SEERA': 'Seera Group',
    'TCOM': 'Trip.com Group',
    'TRIP': 'TripAdvisor',
    'TRVG': 'Trivago',
    'WBJ': 'Webjet',
    'YTRA': 'Yatra',
    'IXIGO': 'Ixigo',
    'FLT': 'Flight Centre',
    'LONG': 'Elong',
    'TCEL': 'TongCheng'
}

# Define company to region mapping
company_to_region = {
    'ABNB': 'North America',
    'BKNG': 'North America',
    'PCLN': 'North America',
    'DESP': 'Latin America',
    'EASEMYTRIP': 'India',
    'EXPE': 'North America',
    'LMN': 'Europe',
    'MMYT': 'India',
    'OWW': 'North America',
    'SEERA': 'Middle East',
    'TCOM': 'China',
    'TRIP': 'North America',
    'TRVG': 'Europe',
    'WBJ': 'Australia',
    'YTRA': 'India',
    'IXIGO': 'India',
    'FLT': 'Australia',
    'LONG': 'China',
    'TCEL': 'China',
    'Orbitz': 'North America',
    'Travelocity': 'North America',
    'Webjet': 'Australia',
    'EaseMyTrip': 'India',
    'Yatra': 'India',
    'Almosafer': 'Middle East',
    'Wego': 'Middle East',
    'Skyscanner': 'Europe',
    'Etraveli': 'Europe',
    'Kiwi': 'Europe',
    'Cleartrip': 'India',
    'Traveloka': 'Asia Pacific',
    'Cleartrip ME & Flyin': 'Middle East',
    'Cleartrip Arabia': 'Middle East',
    'Webjet OTA': 'Australia',
    'EDR': 'North America'
}

def parse_quarter(quarter_str):
    """Parse quarter string into (year, quarter)"""
    year, quarter = quarter_str.split("'")
    year = int(year)  # Year is already in 4-digit format
    quarter = int(quarter[1])  # Extract quarter number
    return year, quarter

def format_revenue(value):
    """Format revenue values with B for billions and M for millions"""
    if value <= 0:  # 对于零值或负值返回空字符串
        return ''
    elif value >= 1000:
        return f'${value/1000:.1f}B'
    return f'${value:.0f}M'

def get_logo_path(company, year):
    """Get the appropriate logo path based on company name and year"""
    logo_base_path = 'bar-video/logos/'
    
    # 处理特殊公司和按年份变化的logo
    if company == 'BKNG' or company == 'PCLN':
        if year < 2014.25:
            return f'{logo_base_path}PCLN_logo.png'
        elif year < 2018.08:
            return f'{logo_base_path}1PCLN_logo.png'
        else:
            return f'{logo_base_path}BKNG_logo.png'
    elif company == 'TRVG':
        if year < 2013.0:
            return f'{logo_base_path}Trivago1.jpg'
        elif year < 2023.0:
            return f'{logo_base_path}Trivago2.jpg'
        else:
            return f'{logo_base_path}TRVG_logo.png'
    elif company == 'EXPE':
        if year < 2010.0:
            return f'{logo_base_path}1_expedia.png'
        elif year < 2012.0:
            return f'{logo_base_path}Expedia2.jpg'
        else:
            return f'{logo_base_path}EXPE_logo.png'
    elif company == 'TCOM':
        if year < 2019.75:
            return f'{logo_base_path}1TCOM_logo.png'
        else:
            return f'{logo_base_path}TCOM_logo.png'
    elif company == 'TRIP':
        if year < 2020.0:
            return f'{logo_base_path}1TRIP_logo.png'
        else:
            return f'{logo_base_path}TRIP_logo.png'
    elif company == 'SEERA':
        if year < 2019.25:
            return f'{logo_base_path}1SEERA_logo.png'
        else:
            return f'{logo_base_path}SEERA_logo.png'
    elif company == 'LMN':
        if year >= 2014.0 and year < 2015.42:
            return f'{logo_base_path}1LMN_logo.png'
        else:
            return f'{logo_base_path}LMN_logo.png'
    elif company == 'Orbitz':
        if year < 2005.0:
            return f'{logo_base_path}Orbitz1.png'
        else:
            return f'{logo_base_path}Orbitz_logo.png'
    elif company == 'TCEL':
        return f'{logo_base_path}TongCheng_logo.png'
    elif company == 'LONG':
        return f'{logo_base_path}Elong_logo.png'
    elif company == 'FLT':
        return f'{logo_base_path}FlightCentre_logo.png'
    elif company == 'WBJ' or company == 'Webjet':
        return f'{logo_base_path}Webjet_logo.png'
    elif company == 'Webjet':
        return f'{logo_base_path}Webjet_logo.png'
    elif company == 'ABNB':
        return f'{logo_base_path}ABNB_logo.png'
    else:
        # 检查是否有温度logo，如果有则优先使用
        temp_logo_path = f'{logo_base_path}{company}_temp_logo.png'
        if os.path.exists(temp_logo_path):
            return temp_logo_path
        
        # 尝试匹配不同格式的logo文件
        for file_extension in ['png', 'jpg', 'jpeg', 'svg']:
            logo_path = f'{logo_base_path}{company}_logo.{file_extension}'
            if os.path.exists(logo_path):
                return logo_path
    
    print(f"Warning: Logo not found for {company}")
    return None

def get_encoded_image(logo_path):
    """将logo转换为base64编码以便直接在Plotly中使用"""
    if not logo_path or not os.path.exists(logo_path):
        return None
    
    try:
        with open(logo_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            # 判断文件类型
            if logo_path.lower().endswith('.png'):
                return f'data:image/png;base64,{encoded_string}'
            elif logo_path.lower().endswith(('.jpg', '.jpeg')):
                return f'data:image/jpeg;base64,{encoded_string}'
            elif logo_path.lower().endswith('.svg'):
                return f'data:image/svg+xml;base64,{encoded_string}'
            else:
                return None
    except Exception as e:
        print(f"Error encoding image {logo_path}: {e}")
        return None

def get_color(company):
    """获取公司颜色，优先使用公司特定颜色，如果没有则使用区域颜色"""
    # 首先检查公司特定颜色
    if company in company_colors:
        return company_colors[company]
    
    # 然后检查区域颜色
    region = company_to_region.get(company, 'Other')
    return region_colors.get(region, '#808080')

def create_visualization():
    """Create interactive Plotly visualization for travel company revenue data"""
    print("Starting Plotly Travel Company Revenue Visualization.")
    
    # Load the data from CSV
    data = pd.read_csv('bar-video/Animated Bubble Chart_ Historic Financials Online Travel Industry - Revenue1.csv')
    print(f"Loaded {len(data)} rows of data.")
    
    # Handle "Revenue" row
    if "Revenue" in data.iloc[0].values:
        data = data.iloc[1:].reset_index(drop=True)
        print(f"Processed quarterly data down to {len(data)} rows.")
    
    # Set the first column as index (quarter)
    quarters = data.iloc[:, 0].tolist()
    data.set_index(data.columns[0], inplace=True)
    
    # 准备所有季度的数据
    all_quarters_data = []
    
    # 确保每个时间点始终显示固定数量的柱状图
    fixed_bar_count = args.max_companies
    
    # Process each quarter
    iterations = 0
    start_time = pd.Timestamp.now()
    
    for quarter in tqdm(quarters, desc="Processing data"):
        iterations += 1
        year, q = parse_quarter(quarter)
        decimal_year = year + (q - 1) * 0.25
        
        quarter_data = data.loc[quarter].copy()
        
        # Convert values to numeric
        for col in quarter_data.index:
            if pd.notna(quarter_data[col]) and quarter_data[col] != '':
                # Remove $, commas, and 'M' or 'B' indicators
                value_str = str(quarter_data[col]).replace('$', '').replace(',', '').strip()
                if 'B' in value_str:
                    # Convert billions to millions
                    quarter_data[col] = float(value_str.replace('B', '')) * 1000
                elif 'M' in value_str:
                    quarter_data[col] = float(value_str.replace('M', ''))
                else:
                    try:
                        quarter_data[col] = float(value_str)
                    except:
                        quarter_data[col] = np.nan
            else:
                quarter_data[col] = np.nan
        
        # Drop NaN values and get top companies by revenue
        quarter_data = quarter_data.dropna()
        top_companies = quarter_data.sort_values(ascending=False).head(fixed_bar_count)
        
        companies = []
        revenues = []
        colors = []
        hover_texts = []
        logos = []
        y_positions = []  # Add numerical y positions
        
        # 计算实际有效的公司数量
        actual_company_count = len(top_companies)
        
        # Create lists for each company's data
        for i, (company, revenue) in enumerate(top_companies.items()):
            if pd.notna(revenue) and revenue > 0:
                # Get company full name and region
                company_name = ticker_to_company.get(company, company)
                region = company_to_region.get(company, 'Other')
                # 使用get_color函数获取颜色
                color = get_color(company)
                
                # Get logo path and encode it
                logo_path = get_logo_path(company, decimal_year)
                encoded_logo = get_encoded_image(logo_path) if logo_path else None
                
                companies.append(company)
                revenues.append(revenue)
                colors.append(color)
                logos.append(encoded_logo)
                y_positions.append(i)  # Use numerical position
                
                hover_text = f"<b>{company_name}</b><br>"
                hover_text += f"Revenue: {format_revenue(revenue)}<br>"
                hover_text += f"Region: {region}<br>"
                hover_text += f"Ticker: {company}"
                hover_texts.append(hover_text)
        
        # 添加虚拟空白bar来填满固定数量的位置
        for i in range(actual_company_count, fixed_bar_count):
            companies.append("")
            revenues.append(0)  # 零收入的bar不会显示
            colors.append('rgba(0,0,0,0)')  # 透明颜色
            logos.append(None)
            y_positions.append(i)
            hover_texts.append("")
        
        # Store data
        quarter_info = {
            'quarter': quarter,
            'companies': companies,
            'revenues': revenues,
            'colors': colors,
            'hover_texts': hover_texts,
            'formatted_revenues': [format_revenue(rev) for rev in revenues],  # 使用修改后的format_revenue函数
            'logos': logos,
            'y_positions': y_positions,  # Add y_positions to the data
            'actual_company_count': actual_company_count  # 记录实际公司数量
        }
        all_quarters_data.append(quarter_info)
    
    end_time = pd.Timestamp.now()
    elapsed_time = (end_time - start_time).total_seconds()
    iterations_per_second = iterations / elapsed_time if elapsed_time > 0 else 0
    print(f"Completed visualization data preparation for {iterations} rows at {iterations_per_second:.2f} iterations per second.")
    
    # Get initial data
    initial_data = all_quarters_data[0]
    
    # Create initial chart
    fig = go.Figure()
    
    # Add traces - Note: Using numerical y positions
    fig.add_trace(
            go.Bar(
                x=initial_data['revenues'],
                y=initial_data['y_positions'],
                orientation='h',
                marker=dict(color=initial_data['colors'],
                            line=dict(width=0, color='rgba(0,0,0,0)')),
                hoverinfo='none',
                width=0.7,
                showlegend=False
            )
    )
    
    # Add text layer with transparent bars - Add vertical offset
    fig.add_trace(
            go.Bar(
                x=initial_data['revenues'],
                y=[y - 0.05 for y in initial_data['y_positions']],  # Add small offset for text
                orientation='h',
                marker=dict(color='rgba(0,0,0,0)',
                            line=dict(width=0, color='rgba(0,0,0,0)')),
                text=initial_data['formatted_revenues'],
                textposition='outside',
                textfont=dict(
                    family='Monda',
                    size=14,
                    color='black'
                ),
                cliponaxis=False,
                textangle=0,
                constraintext='none',
                hoverinfo='none',
                width=0.7,
                showlegend=False
            )
    )
    
    # Add logos with consistent size and proper alignment
    max_revenue = max([max([r for r in quarter_info['revenues'] if r > 0] or [1]) for quarter_info in all_quarters_data])
    
    # 修改初始图表的logo显示位置，使其显示在revenue数字旁边，增大logo
    for i, (company, revenue, logo, formatted_revenue) in enumerate(zip(
        initial_data['companies'], 
        initial_data['revenues'], 
        initial_data['logos'], 
        initial_data['formatted_revenues']
    )):
        if logo and revenue > 0:
            # 计算logo位置 - 放在revenue文本右侧，增加偏移量
            logo_x = revenue + (max_revenue * 0.07)  # 增加偏移量，确保不覆盖文本
            logo_y = i
            logo_width = max_revenue * 0.15  # 增加logo大小
            
            fig.add_layout_image(
                dict(
                    source=logo,
                    xref="x",
                    yref="y",
                    x=logo_x,
                    y=logo_y,
                    sizex=logo_width,
                    sizey=1.0,  # 增加高度
                    xanchor="left",
                    yanchor="middle",
                    sizing="contain",
                    opacity=1.0
                )
            )

    # 调整x轴以容纳logo和文本
    x_axis_range = [0, max_revenue * 1.5]  # 进一步增加空间
    
    # 设置固定的y轴范围
    y_axis_range = [-0.5, fixed_bar_count - 0.5]
    
    # Update layout with fixed yaxis range
    fig.update_layout(
        title={
            'text': "Travel Companies Revenue Visualization",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'family': 'Monda', 'size': 24}
        },
        width=args.width,
        height=args.height,
        xaxis=dict(
            title={
                'text': "Revenue (Million USD)",
                'font': {'family': 'Monda', 'size': 16}
            },
            tickformat="$,.0f",
            range=x_axis_range,
            showgrid=True,
            gridcolor='lightgrey',
            gridwidth=1,
            griddash='dot',
            tickfont={'family': 'Monda', 'size': 14}
        ),
        yaxis=dict(
            title={
                'text': "Company",
                'font': {'family': 'Monda', 'size': 16}
            },
            tickmode='array',
            tickvals=initial_data['y_positions'][:initial_data['actual_company_count']],  # 只显示有效公司的刻度
            ticktext=initial_data['companies'][:initial_data['actual_company_count']],    # 只显示有效公司的名称
            tickfont={'family': 'Monda', 'size': 14},
            fixedrange=True,
            range=y_axis_range,  # 使用固定的y轴范围
            autorange='reversed'  # 保持反向排序
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode="closest",
        font=dict(family="Monda", size=14),
        margin=dict(l=100, r=150, t=100, b=140),
        showlegend=False,
        xaxis_range=x_axis_range,
        bargap=0.25,
        bargroupgap=0.1,
        uniformtext=dict(
            mode='hide',
            minsize=14
        ),
        barmode='group'
    )
    
    # Convert to HTML
    html_content = pio.to_html(
        fig,
        include_plotlyjs=False,
        full_html=False,
        div_id='travel-chart'
    )
    
    # Convert data to JSON for JavaScript
    quarters_data_json = json.dumps(all_quarters_data)
    
    # Create custom HTML with updated JavaScript
    custom_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Travel Company Revenue Visualization</title>
    <script src="https://cdn.plot.ly/plotly-2.27.1.min.js"></script>
    <style>
        body {{
            font-family: 'Monda', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: white;
        }}
        .control-panel {{
            text-align: center;
            margin-top: 20px;
            margin-bottom: 30px;
        }}
        .quarter-display {{
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .slider-container {{
            width: 80%;
            margin: 0 auto;
            margin-bottom: 15px;
        }}
        .button-container {{
            margin-top: 10px;
        }}
        button {{
            font-family: 'Monda', Arial, sans-serif;
            padding: 8px 20px;
            margin: 0 5px;
            cursor: pointer;
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 4px;
        }}
        button:hover {{
            background-color: #e0e0e0;
        }}
        #quarter-slider {{
            width: 100%;
        }}
    </style>
</head>
<body>
    {html_content}
    
    <div class="control-panel">
        <div class="quarter-display">
            <span id="current-quarter">{initial_data['quarter']}</span>
        </div>
        <div class="slider-container">
            <input type="range" id="quarter-slider" min="0" max="{len(quarters) - 1}" value="0">
        </div>
        <div class="button-container">
            <button id="play-button">Play</button>
            <button id="pause-button">Pause</button>
            <button id="reset-button">Reset</button>
        </div>
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const allQuartersData = {quarters_data_json};
            let currentQuarterIndex = 0;
            let isPlaying = false;
            let animationInterval = null;
            const chartDiv = document.getElementById('travel-chart');
            const currentQuarterDisplay = document.getElementById('current-quarter');
            const quarterSlider = document.getElementById('quarter-slider');
            const playButton = document.getElementById('play-button');
            const pauseButton = document.getElementById('pause-button');
            const resetButton = document.getElementById('reset-button');
            
            // 初始数据设置
            const initialData = allQuartersData[0];
            const traces = [
                {{
                    type: 'bar',
                    x: initialData.revenues,
                    y: initialData.y_positions,
                    orientation: 'h',
                    marker: {{
                        color: initialData.colors,
                        line: {{
                            width: 0,
                            color: 'rgba(0,0,0,0)'
                        }}
                    }},
                    hoverinfo: 'none',
                    width: 0.8,
                    showlegend: false
                }},
                {{
                    type: 'bar',
                    x: initialData.revenues,
                    y: initialData.y_positions.map(y => y - 0.05),  // 文本的轻微偏移
                    orientation: 'h',
                    marker: {{
                        color: 'rgba(0,0,0,0)',
                        line: {{
                            width: 0,
                            color: 'rgba(0,0,0,0)'
                        }}
                    }},
                    text: initialData.formatted_revenues,
                    textposition: 'outside',
                    textfont: {{
                        family: 'Monda',
                        size: 14,
                        color: 'black'
                    }},
                    cliponaxis: false,
                    textangle: 0,
                    constraintext: 'none',
                    hoverinfo: 'none',
                    width: 0.8,
                    showlegend: false
                }}
            ];
            
            const layout = {{
                title: {{
                    text: "Travel Company Revenue Visualization",
                    y: 0.95,
                    x: 0.5,
                    xanchor: 'center',
                    yanchor: 'top',
                    font: {{family: 'Monda', size: 24}}
                }},
                width: {args.width},
                height: {args.height},
                xaxis: {{
                    title: {{
                        text: "Revenue",
                        font: {{family: 'Monda', size: 16}}
                    }},
                    tickformat: "$,.0f",
                    range: [0, Math.max(...initialData.revenues) * 1.5],
                    showgrid: true,
                    gridcolor: 'lightgrey',
                    gridwidth: 1,
                    griddash: 'dot',
                    tickfont: {{family: 'Monda', size: 14}}
                }},
                yaxis: {{
                    title: {{
                        text: "Company",
                        font: {{family: 'Monda', size: 16}}
                    }},
                    tickmode: 'array',
                    tickvals: initialData.y_positions,
                    ticktext: initialData.companies,
                    tickfont: {{family: 'Monda', size: 14}},
                    autorange: 'reversed',
                    fixedrange: true
                }},
                plot_bgcolor: 'white',
                paper_bgcolor: 'white',
                hovermode: "closest",
                font: {{family: "Monda", size: 14}},
                margin: {{l: 100, r: 150, t: 100, b: 140}},
                showlegend: false,  // 关闭图例显示
                images: initialData.logos.map((logo, i) => 
                    logo ? {{
                        source: logo,
                        xref: "x",
                        yref: "y",
                        x: initialData.revenues[i] + (Math.max(...initialData.revenues) * 0.07),
                        y: i,
                        sizex: Math.max(...initialData.revenues) * 0.15,  // 增大logo尺寸
                        sizey: 1.0,  // 增加高度
                        xanchor: "left",
                        yanchor: "middle",
                        sizing: "contain",
                        opacity: 1.0
                    }} : null
                ).filter(img => img !== null)
            }};
            
            // 初始化图表
            Plotly.newPlot(chartDiv, traces, layout);
            
            // 历史最大值记录
            let historicalMaxRevenue = Math.max(...initialData.revenues);
            
            // 平滑动画函数
            function playAnimation() {{
                if (isPlaying) return;
                isPlaying = true;
                
                let lastFrameTime = performance.now();
                const quarterDuration = {args.transition_duration};  // 每个季度持续时间
                let currentTime = 0;
                
                // 平滑动画帧函数
                function animate() {{
                    if (!isPlaying) return;
                    
                    const now = performance.now();
                    const deltaTime = now - lastFrameTime;
                    lastFrameTime = now;
                    
                    currentTime += deltaTime;
                    const totalDuration = quarterDuration * (allQuartersData.length - 1);
                    const normalizedTime = (currentTime % totalDuration) / totalDuration;
                    
                    const exactIndex = normalizedTime * (allQuartersData.length - 1);
                    const currentIndex = Math.floor(exactIndex);
                    const nextIndex = (currentIndex + 1) % allQuartersData.length;
                    const progress = exactIndex - currentIndex;
                    
                    quarterSlider.value = currentIndex;
                    
                    const currentData = allQuartersData[currentIndex];
                    const nextData = allQuartersData[nextIndex];
                    
                    // 构建插值数据
                    const interpolatedData = currentData.revenues.map((startVal, i) => {{
                        // 确保索引在两个数据集中都存在
                        if (i < nextData.revenues.length) {{
                            return {{
                                company: currentData.companies[i],
                                revenue: startVal + (nextData.revenues[i] - startVal) * progress,
                                logo: currentData.logos[i],
                                color: currentData.colors[i],
                                formattedRevenue: formatRevenue(startVal + (nextData.revenues[i] - startVal) * progress),
                                y_position: i
                            }};
                        }} else {{
                            return {{
                                company: currentData.companies[i],
                                revenue: startVal,
                                logo: currentData.logos[i],
                                color: currentData.colors[i],
                                formattedRevenue: formatRevenue(startVal),
                                y_position: i
                            }};
                        }}
                    }});
                    
                    // 按收入排序
                    interpolatedData.sort((a, b) => b.revenue - a.revenue);
                    
                    // 提取已排序的数据
                    const companiesSorted = interpolatedData.map(d => d.company);
                    const revenuesSorted = interpolatedData.map(d => d.revenue);
                    const logosSorted = interpolatedData.map(d => d.logo);
                    const colorsSorted = interpolatedData.map(d => d.color);
                    const formattedRevenuesSorted = interpolatedData.map(d => d.formattedRevenue);
                    const yPositionsSorted = interpolatedData.map((d, i) => i);
                    
                    // 计算当前最大收入和历史最大收入
                    const currentMaxRevenue = Math.max(...revenuesSorted);
                    historicalMaxRevenue = Math.max(historicalMaxRevenue, currentMaxRevenue);
                    const xAxisMax = historicalMaxRevenue * 1.5;
                    
                    try {{
                        // 更新图表
                        Plotly.update(chartDiv, {{
                            'x': [revenuesSorted, revenuesSorted],
                            'y': [yPositionsSorted, yPositionsSorted.map(y => y - 0.05)],  // 文本偏移
                            'marker.color': [colorsSorted, Array(colorsSorted.length).fill('rgba(0,0,0,0)')],
                            'text': [[], formattedRevenuesSorted]
                        }}, {{
                            'yaxis.ticktext': companiesSorted,
                            'yaxis.tickvals': yPositionsSorted,
                            'xaxis.range': [0, xAxisMax],
                            'images': logosSorted.map((logo, i) => 
                                logo ? {{
                                    source: logo,
                                    xref: "x",
                                    yref: "y",
                                    x: revenuesSorted[i] + (xAxisMax * 0.05),
                                    y: i,
                                    sizex: historicalMaxRevenue * 0.15,  // 增加logo大小
                                    sizey: 1.0,  // 增加高度
                                    xanchor: "left",
                                    yanchor: "middle",
                                    sizing: "contain",
                                    opacity: 1.0
                                }} : null
                            ).filter(img => img !== null)
                        }});
                        
                        // 更新季度显示
                        const quarterText = interpolateQuarters(currentData.quarter, nextData.quarter, progress);
                        currentQuarterDisplay.textContent = quarterText;
                        
                    }} catch (e) {{
                        console.error("Animation error:", e);
                    }}
                    
                    requestAnimationFrame(animate);
                }}
                
                requestAnimationFrame(animate);
            }}
            
            // 格式化收入显示，修改为零值不显示
            function formatRevenue(value) {{
                if (value <= 0) {{
                    return '';  // 零值或负值返回空字符串
                }}
                if (value >= 1000) {{
                    return '$' + (value/1000).toFixed(1) + 'B';
                }}
                return '$' + Math.round(value) + 'M';
            }}
            
            // 季度插值函数
            function interpolateQuarters(q1, q2, progress) {{
                const [year1, quarter1] = q1.split("'").map(x => parseInt(x.replace('Q', '')));
                let [year2, quarter2] = q2.split("'").map(x => parseInt(x.replace('Q', '')));
                
                if (year2 < year1) {{
                    year2 = year1;
                }}
                
                const yearDiff = year2 - year1;
                const quarterDiff = quarter2 - quarter1;
                const totalQuarters = yearDiff * 4 + quarterDiff;
                const interpolatedQuarters = quarter1 + totalQuarters * progress;
                
                const interpolatedYear = Math.floor(year1 + (interpolatedQuarters - 1) / 4);
                const interpolatedQuarter = Math.floor(((interpolatedQuarters - 1) % 4) + 1);
                
                return interpolatedYear + "'Q" + interpolatedQuarter;
            }}
            
            // 暂停动画
            function pauseAnimation() {{
                isPlaying = false;
            }}
            
            // 重置动画
            function resetAnimation() {{
                pauseAnimation();
                quarterSlider.value = 0;
                currentQuarterIndex = 0;
                updateChart(0);
            }}
            
            // 更新图表到特定季度
            function updateChart(index) {{
                if (index < 0 || index >= allQuartersData.length) return;
                
                const currentData = allQuartersData[index];
                currentQuarterIndex = index;
                
                try {{
                    // 更新图表数据
                    Plotly.update(chartDiv, {{
                        'x': [currentData.revenues, currentData.revenues],
                        'y': [currentData.y_positions, currentData.y_positions.map(y => y - 0.05)],
                        'marker.color': [currentData.colors, Array(currentData.colors.length).fill('rgba(0,0,0,0)')],
                        'text': [[], currentData.formatted_revenues]
                    }}, {{
                        'yaxis.ticktext': currentData.companies,
                        'yaxis.tickvals': currentData.y_positions,
                        'xaxis.range': [0, Math.max(...currentData.revenues) * 1.5]
                    }});
                    
                    // 更新logo
                    const actualCompanyCount = Math.min(currentData.companies.length, {args.max_companies});
                    const revenues = currentData.revenues.slice(0, actualCompanyCount);
                    const logos = currentData.logos.slice(0, actualCompanyCount);
                    const maxRevenue = Math.max(...revenues);
                    
                    // 只为有实际收入和logo的公司添加logo
                    const newImages = [];
                    for (let i = 0; i < actualCompanyCount; i++) {{
                        const logo = logos[i];
                        const revenue = revenues[i];
                        if (logo && revenue > 0) {{
                            // 计算logo位置 - 放在revenue文本右侧，增加偏移量
                            const logoX = revenue + (maxRevenue * 0.07);
                            
                            newImages.push({{
                                source: logo,
                                xref: "x",
                                yref: "y",
                                x: logoX,
                                y: i,
                                sizex: maxRevenue * 0.15,  // 增加logo大小
                                sizey: 1.0,  // 增加高度
                                xanchor: "left",
                                yanchor: "middle",
                                sizing: "contain",
                                opacity: 1.0
                            }});
                        }}
                    }}
                    
                    // 应用logo变更
                    if (newImages.length > 0) {{
                        Plotly.relayout(chartDiv, {{
                            'images': newImages,
                            'xaxis.range': [0, maxRevenue * 1.5]
                        }});
                    }}
                    
                    // 更新季度显示
                    currentQuarterDisplay.textContent = currentData.quarter;
                    
                }} catch (e) {{
                    console.error("Update error:", e);
                }}
            }}
            
            // 事件监听器设置
            quarterSlider.addEventListener('input', function() {{
                pauseAnimation();
                updateChart(parseInt(this.value));
            }});
            
            playButton.addEventListener('click', playAnimation);
            pauseButton.addEventListener('click', pauseAnimation);
            resetButton.addEventListener('click', resetAnimation);
            
            // 自动开始动画
            setTimeout(playAnimation, 1000);
        }});
    </script>
</body>
</html>
"""

    
    # Save HTML file
    with open(args.output, 'w') as f:
        f.write(custom_html)
    
    print(f"Visualization saved successfully to {args.output}")
    
    # Automatically open the HTML file in browser
    output_path = Path(args.output).resolve()
    webbrowser.open('file://' + str(output_path), new=2)
    
    return fig

if __name__ == "__main__":
    print("Starting Plotly Travel Company Revenue Visualization")
    fig = create_visualization()
    print("Visualization complete!") 