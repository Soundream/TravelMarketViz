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

# Create a color mapping for regions
region_colors = {
    'North America': '#40E0D0',  # Turquoise
    'Europe': '#4169E1',         # Royal Blue
    'Asia Pacific': '#FF4B4B',   # Red
    'Latin America': '#32CD32',  # Lime Green
    'China': '#FF4B4B',          # Red (same as Asia Pacific)
    'Middle East': '#DEB887',    # Burlywood
    'India': '#FFA500',          # Orange
    'Australia': '#9932CC'       # Purple
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
    if value >= 1000:
        return f'${value/1000:.1f}B'
    return f'${value:.0f}M'

def get_logo_path(company, year):
    """Get the appropriate logo path based on company name and year"""
    # Handle company and logo variations based on the year
    if company == 'BKNG' or company == 'PCLN':
        if year < 2014.25:
            return 'logos/PCLN_logo.png'
        elif year < 2018.08:
            return 'logos/1PCLN_logo.png'
        else:
            return 'logos/BKNG_logo.png'
    elif company == 'TRVG':
        if year < 2013.0:
            return 'logos/Trivago1.jpg'
        elif year < 2023.0:
            return 'logos/Trivago2.jpg'
        else:
            return 'logos/TRVG_logo.png'
    elif company == 'EXPE':
        if year < 2010.0:
            return 'logos/1_expedia.png'
        elif year < 2012.0:
            return 'logos/EXPE_logo.png'
        else:
            return 'logos/EXPE_logo.png'
    elif company == 'TCOM':
        if year < 2019.75:
            return 'logos/1TCOM_logo.png'
        else:
            return 'logos/TCOM_logo.png'
    elif company == 'TRIP':
        if year < 2020.0:
            return 'logos/1TRIP_logo.png'
        else:
            return 'logos/TRIP_logo.png'
    elif company == 'SEERA':
        if year < 2019.25:
            return 'logos/1SEERA_logo.png'
        else:
            return 'logos/SEERA_logo.png'
    elif company == 'LMN':
        if year >= 2014.0 and year < 2015.42:
            return 'logos/1LMN_logo.png'
        else:
            return 'logos/LMN_logo.png'
    elif company == 'Orbitz':
        if year < 2005.0:
            return 'logos/Orbitz1.png'
        else:
            return 'logos/Orbitz_logo.png'
    elif company == 'TCEL':
        return 'logos/TongCheng_logo.png'
    elif company == 'LONG':
        return 'logos/Elong_logo.png'
    else:
        # Default logo path pattern
        return f'logos/{company}_logo.png'

def get_encoded_image(logo_path):
    """Convert image to base64 string for HTML embedding"""
    try:
        if logo_path and os.path.exists(logo_path):
            with open(logo_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
                return f"data:image/png;base64,{encoded_string}"
    except Exception as e:
        print(f"Error encoding image {logo_path}: {e}")
    return None

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
                color = region_colors.get(region, '#808080')
                
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
            'formatted_revenues': [format_revenue(rev) if rev > 0 else "" for rev in revenues],
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
    
    # Add region colors to legend using scatter points
    for region, color in region_colors.items():
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode='markers',
                marker=dict(size=20, color=color),
                name=region,
                showlegend=True
            )
        )

    # Add logos with consistent size and proper alignment
    max_revenue = max([max([r for r in quarter_info['revenues'] if r > 0] or [1]) for quarter_info in all_quarters_data])
    global_x_offset = max_revenue * 1.05
    fixed_logo_width = max_revenue * 0.2
    
    for i, (company, revenue, logo) in enumerate(zip(initial_data['companies'], initial_data['revenues'], initial_data['logos'])):
        if logo and revenue > 0:
            fig.add_layout_image(
                dict(
                    source=logo,
                    xref="x",
                    yref="y",
                    x=global_x_offset,
                    y=i - 0.05,  # Add small offset for logo
                    sizex=fixed_logo_width,
                    sizey=0.7,
                    xanchor="left",
                    yanchor="middle",
                    sizing="contain",
                    opacity=0.95
                )
            )

    # 调整x轴以容纳logo
    x_axis_range = [0, max_revenue * 1.5]  # 确保图表有足够空间显示logo
    
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
        showlegend=True,
        legend=dict(
            itemsizing='constant',
            title=dict(text='Regions'),
            tracegroupgap=0,
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5
        ),
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
    <title>Travel Companies Revenue Visualization</title>
    <script src="https://cdn.plot.ly/plotly-2.14.0.min.js"></script>
    <style>
        body {{
            font-family: 'Monda', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: white;
        }}
        #chart-container {{
            width: 100%;
            max-width: {args.width}px;
            margin: 0 auto;
            position: relative;
        }}
        #quarter-display {{
            position: absolute;
            top: 60px;
            right: 50px;
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }}
        .controls {{
            margin: 20px auto;
            text-align: center;
            max-width: {args.width}px;
        }}
        #play-button, #pause-button {{
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
            margin: 0 10px;
        }}
        #pause-button {{
            background-color: #f44336;
        }}
        #quarter-slider {{
            width: 80%;
            margin: 20px auto;
        }}
    </style>
</head>
<body>
    <div id="chart-container">
        <div id="chart"></div>
        <div id="quarter-display"></div>
    </div>
    <div class="controls">
        <button id="play-button">Play</button>
        <button id="pause-button">Pause</button>
        <br>
        <input type="range" id="quarter-slider" min="0" max="{len(all_quarters_data) - 1}" value="0">
    </div>
    <script>
        // Data for animation
        const allQuartersData = {quarters_data_json};
        const chartDiv = document.getElementById('chart');
        const currentQuarterDisplay = document.getElementById('quarter-display');
        const playButton = document.getElementById('play-button');
        const pauseButton = document.getElementById('pause-button');
        const quarterSlider = document.getElementById('quarter-slider');
        
        let currentQuarterIndex = 0;
        let animationInterval = null;
        let historicalMaxRevenue = 0;
                
        // 设置固定的y轴范围
        const yAxisRange = [-0.5, {args.max_companies} - 0.5];
        
        async function updateChart(quarterIndex) {{
            if (quarterIndex < 0 || quarterIndex >= allQuartersData.length) return;
            
            currentQuarterIndex = quarterIndex;
            const currentData = allQuartersData[quarterIndex];
            
            if (!currentData || !currentData.companies || !currentData.revenues) {{
                console.error('Invalid data for quarter', quarterIndex);
                return;
            }}
            
            const companies = currentData.companies;
            const revenues = currentData.revenues;
            const colors = currentData.colors;
            const formattedRevenues = currentData.formatted_revenues;
            const logos = currentData.logos;
            const yPositions = currentData.y_positions;
            // 获取实际公司数量
            const actualCompanyCount = currentData.actual_company_count;
            
            // 仅考虑实际公司的收入来计算最大值
            const validRevenues = revenues.filter((rev, idx) => idx < actualCompanyCount);
            const currentMaxRevenue = Math.max(...validRevenues);
            historicalMaxRevenue = Math.max(historicalMaxRevenue, currentMaxRevenue);
            const xAxisMax = historicalMaxRevenue * 1.5;
            
            try {{
                // 使用 Plotly.react 进行可靠的更新
                Plotly.react(chartDiv, 
                    [
                        {{
                            x: revenues,
                            y: yPositions,
                            type: 'bar',
                            orientation: 'h',
                            marker: {{
                                color: colors,
                                line: {{ width: 0, color: 'rgba(0,0,0,0)' }}
                            }},
                            hoverinfo: 'none',
                            width: 0.7,  // 固定柱状图宽度
                            showlegend: false
                        }},
                        {{
                            x: revenues,
                            y: yPositions.map(y => y - 0.05),
                            type: 'bar',
                            orientation: 'h',
                            marker: {{
                                color: 'rgba(0,0,0,0)',
                                line: {{ width: 0, color: 'rgba(0,0,0,0)' }}
                            }},
                            text: formattedRevenues,
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
                            width: 0.7,  // 固定柱状图宽度
                            showlegend: false
                        }}
                    ],
                    {{
                        title: {{
                            text: "Travel Companies Revenue Visualization",
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
                                text: "Revenue (Million USD)",
                                font: {{family: 'Monda', size: 16}}
                            }},
                            tickformat: "$,.0f",
                            range: [0, xAxisMax],
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
                            tickvals: yPositions.slice(0, actualCompanyCount),  // 只显示有效公司的刻度
                            ticktext: companies.slice(0, actualCompanyCount),   // 只显示有效公司的名称
                            tickfont: {{family: 'Monda', size: 14}},
                            fixedrange: true,
                            range: yAxisRange,  // 使用固定的y轴范围
                            autorange: 'reversed' // 保持反向排序
                        }},
                        plot_bgcolor: 'white',
                        paper_bgcolor: 'white',
                        hovermode: "closest",
                        margin: {{l: 100, r: 150, t: 100, b: 140}},
                        bargap: 0.25,      // 柱状图之间的间距
                        bargroupgap: 0.1,
                        uniformtext: {{
                            mode: 'hide',
                            minsize: 14
                        }},
                        barmode: 'group'  // 确保正确对齐
                    }}
                );
                
                // 只为有实际收入和logo的公司添加logo
                const globalXOffset = historicalMaxRevenue * 1.05;
                const fixedLogoWidth = historicalMaxRevenue * 0.2;
                
                const newImages = [];
                for (let i = 0; i < actualCompanyCount; i++) {{
                    const logo = logos[i];
                    const revenue = revenues[i];
                    if (logo && revenue > 0) {{
                        newImages.push({{
                            source: logo,
                            xref: "x",
                            yref: "y",
                            x: globalXOffset,
                            y: i - 0.05,  // Add offset for logo
                            sizex: fixedLogoWidth,
                            sizey: 0.7,
                            xanchor: "left",
                            yanchor: "middle",
                            sizing: "contain",
                            opacity: 0.95
                        }});
                    }}
                }}
                
                if (newImages.length > 0) {{
                    Plotly.relayout(chartDiv, {{
                        'images': newImages
                    }});
                }}
                
                // Update quarter display
                currentQuarterDisplay.textContent = currentData.quarter;
                
            }} catch (e) {{
                console.error("Update error:", e);
            }}
        }}
        
        // Initial chart
        updateChart(0);
        
        // Play/pause functionality
        function startAnimation() {{
            if (animationInterval) clearInterval(animationInterval);
            
            animationInterval = setInterval(() => {{
                currentQuarterIndex = (currentQuarterIndex + 1) % allQuartersData.length;
                updateChart(currentQuarterIndex);
                quarterSlider.value = currentQuarterIndex;
            }}, {args.transition_duration});
        }}
        
        function pauseAnimation() {{
            if (animationInterval) {{
                clearInterval(animationInterval);
                animationInterval = null;
            }}
        }}
        
        playButton.addEventListener('click', startAnimation);
        pauseButton.addEventListener('click', pauseAnimation);
        
        // Quarter slider
        quarterSlider.addEventListener('input', function() {{
            pauseAnimation();
            updateChart(parseInt(this.value));
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