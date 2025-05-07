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
warnings.filterwarnings('ignore')

# Add argument parser
parser = argparse.ArgumentParser(description='Generate hotel revenue visualization using Plotly')
parser.add_argument('--output', type=str, default='output/hotel_revenue_plotly.html', 
                    help='Output HTML file path')
parser.add_argument('--frames-per-year', type=int, default=4, 
                    help='Number of frames to generate per year (default: 4 for quarterly)')
parser.add_argument('--height', type=int, default=800, 
                    help='Height of the visualization in pixels (default: 800)')
parser.add_argument('--width', type=int, default=1600, 
                    help='Width of the visualization in pixels (default: 1600)')
parser.add_argument('--max-hotels', type=int, default=15, 
                    help='Maximum number of hotels to display (default: 15)')
parser.add_argument('--transition-duration', type=int, default=500, 
                    help='Transition duration between frames in ms (default: 500)')
args = parser.parse_args()

# Create required directories
output_dir = os.path.dirname(args.output)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Created directory: {output_dir}")

# Create a color mapping for regions
region_colors = {
    'US': '#40E0D0',        # Turquoise
    'CA': '#40E0D0',        # Turquoise (same as US)
    'GB': '#4169E1',        # Royal Blue
    'BM': '#4169E1',        # Royal Blue (same as GB)
    'FR': '#4169E1',        # Royal Blue (same as GB)
    'ES': '#4169E1',        # Royal Blue (same as GB)
    'IE': '#4169E1',        # Royal Blue (same as GB)
    'SE': '#4169E1',        # Royal Blue (same as GB)
    'CN': '#FF4B4B',        # Red
    'HK': '#FF4B4B',        # Red (same as CN)
    'MY': '#FF4B4B',        # Red (same as CN)
    'SG': '#FF4B4B',        # Red (same as CN)
    'TH': '#FF4B4B',        # Red (same as CN)
    'JP': '#FF4B4B',        # Red (same as CN)
    'KR': '#FF4B4B',        # Red (same as CN)
    'IN': '#32CD32',        # Lime Green
    'AU': '#9932CC',        # Dark Orchid
    'ZA': '#DAA520',        # Goldenrod
    'AE': '#DEB887',        # Burlywood
    'MO': '#FF4B4B'         # Red (same as CN)
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

def get_logo_path(hotel, year, ticker):
    """Get the appropriate logo path based on hotel name, year and ticker"""
    logo_mapping = {
        "Marriott": [
            {"start_year": 1989, "end_year": 2013, "file": "../99.utility/hospitality-bar-video/logos/Marriott-Logo-1989-2013.png"},
            {"start_year": 2013, "end_year": 2025, "file": "../99.utility/hospitality-bar-video/logos/Marriott-logo-2025.jpg"}
        ],
        "Starwood": [
            {"start_year": 1999, "end_year": 2025, "file": "../99.utility/hospitality-bar-video/logos/Starwood-2025.jpeg"}
        ],
        "Hyatt": [
            {"start_year": 1990, "end_year": 2013, "file": "../99.utility/hospitality-bar-video/logos/Hyatt-Logo-1990-2013.jpg"},
            {"start_year": 2013, "end_year": 2025, "file": "../99.utility/hospitality-bar-video/logos/Hyatt-logo-2025.jpg"}
        ],
        "Hilton": [
            {"start_year": 1999, "end_year": 2010, "file": "../99.utility/hospitality-bar-video/logos/Hilton-Logo-2010.jpg"},
            {"start_year": 2010, "end_year": 2025, "file": "../99.utility/hospitality-bar-video/logos/Hilton-logo-2025.jpg"}
        ],
        "Wyndham": [
            {"start_year": 1999, "end_year": 2025, "file": "../99.utility/hospitality-bar-video/logos/Wyndham-2025.jpeg"}
        ],
        "Choice Hotels": [
            {"start_year": 1999, "end_year": 2015, "file": "../99.utility/hospitality-bar-video/logos/Comfort-Inn-Logo-2015.jpg"},
            {"start_year": 2015, "end_year": 2025, "file": "../99.utility/hospitality-bar-video/logos/Comfort-Inn-Logo-2025.jpg"}
        ],
        "La Quinta": [
            {"start_year": 1999, "end_year": 2025, "file": "../99.utility/hospitality-bar-video/logos/La Quinta-2025.webp"}
        ],
        "Extended Stay America": [
            {"start_year": 1995, "end_year": 2012, "file": "../99.utility/hospitality-bar-video/logos/Extended-Stay-America-Logo-1995-2012.jpg"},
            {"start_year": 2012, "end_year": 2025, "file": "../99.utility/hospitality-bar-video/logos/Extended-Stay-America-Logo-2025.jpg"}
        ],
        "Four Seasons": [
            {"start_year": 1999, "end_year": 2025, "file": "../99.utility/hospitality-bar-video/logos/Four-Seasons-Logo-2025.jpg"}
        ],
        "Fairmont": [
            {"start_year": 1999, "end_year": 2025, "file": "../99.utility/hospitality-bar-video/logos/Fairmont-Logo-2025.png"}
        ],
        "Four Seasons ": [  # Note the trailing space in the hotel name
            {"start_year": 1999, "end_year": 2025, "file": "../99.utility/hospitality-bar-video/logos/Four-Seasons-Logo-2025.jpg"}
        ],
        "Fairmont ": [  # Note the trailing space in the hotel name
            {"start_year": 1999, "end_year": 2025, "file": "../99.utility/hospitality-bar-video/logos/Fairmont-Logo-2025.png"}
        ],
        "IHG": [
            {"start_year": 1999, "end_year": 2003, "file": "../99.utility/hospitality-bar-video/logos/IHG-Logo-2003-2017.png"},
            {"start_year": 2003, "end_year": 2017, "file": "../99.utility/hospitality-bar-video/logos/IHG-Logo-2003-2017.png"},
            {"start_year": 2017, "end_year": 2021, "file": "../99.utility/hospitality-bar-video/logos/IHG-Logo-2017-2021.png"},
            {"start_year": 2021, "end_year": 2025, "file": "../99.utility/hospitality-bar-video/logos/IHG-Logo-2025.jpg"}
        ],
        "Millennium": [
            {"start_year": 1999, "end_year": 2025, "file": "../99.utility/hospitality-bar-video/logos/Millennium-2025.png"}
        ],
        "Belmond": [
            {"start_year": 1999, "end_year": 2025, "file": "../99.utility/hospitality-bar-video/logos/Belmond-Logo-2025.png"}
        ],
        "Accor": [
            {"start_year": 1997, "end_year": 2007, "file": "../99.utility/hospitality-bar-video/logos/Accor-Logo-1997-2007.png"},
            {"start_year": 2007, "end_year": 2010, "file": "../99.utility/hospitality-bar-video/logos/Accor-Logo-2007-2010.png"},
            {"start_year": 2010, "end_year": 2015, "file": "../99.utility/hospitality-bar-video/logos/Accor-Logo-2010-2015.png"},
            {"start_year": 2015, "end_year": 2019, "file": "../99.utility/hospitality-bar-video/logos/Accor-Logo-2015-2019.png"},
            {"start_year": 2019, "end_year": 2025, "file": "../99.utility/hospitality-bar-video/logos/Accor-Logo-2025.jpg"}
        ],
        "Meliá": [
            {"start_year": 1999, "end_year": 2025, "file": "../99.utility/hospitality-bar-video/logos/Meliá-2025.png"}
        ],
        "NH Hotels": [
            {"start_year": 1999, "end_year": 2025, "file": "../99.utility/hospitality-bar-video/logos/NH Hotels-2025.png"}
        ],
        "Dalata": [
            {"start_year": 1999, "end_year": 2025, "file": "../99.utility/hospitality-bar-video/logos/NH Hotels-2025.png"}  # Using similar logo since Dalata logo is missing
        ],
        "Scandic": [
            {"start_year": 1999, "end_year": 2025, "file": "../99.utility/hospitality-bar-video/logos/Scandic-2025.png"}
        ],
        "H World": [
            {"start_year": 1999, "end_year": 2025, "file": "../99.utility/hospitality-bar-video/logos/H World-Logo-2025.jpg"}
        ],
        "Jin Jiang": [
            {"start_year": 1999, "end_year": 2025, "file": "../99.utility/hospitality-bar-video/logos/Jin Jiang-2025.png"}
        ],
        "IHCL": [
            {"start_year": 1999, "end_year": 2025, "file": "../99.utility/hospitality-bar-video/logos/IHCL-2025.png"}
        ],
        "EIH": [
            {"start_year": 1999, "end_year": 2025, "file": "../99.utility/hospitality-bar-video/logos/EIH-Logo-2025.png"}
        ],
        "Shangri-La Hotels (Malaysia) Berhad": [
            {"start_year": 1999, "end_year": 2025, "file": "../99.utility/hospitality-bar-video/logos/hangri-La Hotels (Malaysia) Berhad.png"}
        ],
        "Far East Orchard": [
            {"start_year": 1999, "end_year": 2025, "file": "../99.utility/hospitality-bar-video/logos/Far East Orchard-Logo-2025.png"}
        ],
        "Shangri-La Asia Limited": [
            {"start_year": 1999, "end_year": 2025, "file": "../99.utility/hospitality-bar-video/logos/Shangri-La Asia Limited-2025.png"}
        ],
        "Shangri-La Asia Limited ": [  # Note the trailing space in the hotel name
            {"start_year": 1999, "end_year": 2025, "file": "../99.utility/hospitality-bar-video/logos/Shangri-La Asia Limited-2025.png"}
        ],
        "Mandarin Oriental": [
            {"start_year": 1999, "end_year": 2025, "file": "../99.utility/hospitality-bar-video/logos/Mandarin Oriental-2025.jpg"}
        ],
        "Dusit Thani": [
            {"start_year": 1999, "end_year": 2025, "file": "../99.utility/hospitality-bar-video/logos/Dusit Thani-Logo-2025.jpg"}
        ],
        "Erawan Group": [
            {"start_year": 1999, "end_year": 2025, "file": "../99.utility/hospitality-bar-video/logos/Erawan Group-Logo-2025.jpeg"}
        ],
        "Minor International": [
            {"start_year": 1999, "end_year": 2025, "file": "../99.utility/hospitality-bar-video/logos/Minor International-2025.png"}
        ],
        "Tsogo Sun Hotels (Southern Sun)": [
            {"start_year": 1999, "end_year": 2025, "file": "../99.utility/hospitality-bar-video/logos/Tsogo Sun Hotels (Southern Sun).png"}
        ],
        "Shilla Hotels & Resorts": [
            {"start_year": 1999, "end_year": 2025, "file": "../99.utility/hospitality-bar-video/logos/Shilla Hotels & Resorts-2025.png"}
        ]
    }
    
    if hotel not in logo_mapping:
        print(f"Logo not found for {hotel}")
        return None
        
    logo_versions = logo_mapping[hotel]
    
    # Find the appropriate logo based on year
    for version in logo_versions:
        if version["start_year"] <= year <= version["end_year"]:
            logo_path = version["file"]
            if os.path.exists(logo_path):
                return logo_path
            else:
                print(f"Logo file not found: {logo_path}")
                return None
    
    return None

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
    """Create interactive Plotly visualization for hotel revenue data"""
    # Load the data from CSV
    df = pd.read_csv('../99.utility/hospitality-bar-video/hotel_final.csv')
    
    # Process metadata
    metadata = df.iloc[:5].copy()
    revenue_data = df.iloc[7:].copy()
    
    metadata.set_index(metadata.columns[0], inplace=True)
    
    # Convert revenue columns
    for col in revenue_data.columns[1:]:
        # Check if the column contains string values before using str methods
        if revenue_data[col].dtype == 'object':
            # If it's a string column, use str methods to clean it
            revenue_data[col] = pd.to_numeric(revenue_data[col].str.replace(',', '').str.replace(' M', ''), errors='coerce')
        else:
            # If it's already numeric, just ensure it's properly converted
            revenue_data[col] = pd.to_numeric(revenue_data[col], errors='coerce')
    
    # Set the index 
    revenue_data.set_index(revenue_data.columns[0], inplace=True)
    
    # Get unique quarters and sort them
    quarters = sorted(list(set([q for q in revenue_data.index.tolist() if isinstance(q, str) and "'" in q])))
    print(f"Found {len(quarters)} unique quarters: {quarters[:5]}...")
    
    # 准备所有季度的数据
    all_quarters_data = []
    
    # Process each quarter
    for quarter in tqdm(quarters, desc="Processing data"):
        year, q = parse_quarter(quarter)
        month = q * 3
        
        # Get all rows for this quarter and combine them 
        # (in case there are multiple rows with the same quarter)
        quarter_rows = revenue_data.loc[quarter]
        
        # If we got a Series (single row), convert to DataFrame
        if isinstance(quarter_rows, pd.Series):
            quarter_rows = pd.DataFrame([quarter_rows])
        
        # Combine rows by taking the first non-NA value for each column
        combined_data = {}
        for col in quarter_rows.columns:
            non_na_values = quarter_rows[col].dropna()
            if len(non_na_values) > 0:
                combined_data[col] = non_na_values.iloc[0]
        
        # Create Series from the combined data
        quarter_data = pd.Series(combined_data)
        quarter_data = quarter_data.dropna()
        
        hotels = []
        revenues = []
        colors = []
        hover_texts = []
        logos = []
        y_positions = []  # Add numerical y positions
        
        # Check if we have data after combining and cleaning
        if len(quarter_data) > 0:
            # Sort hotels by revenue
            top_hotels = quarter_data.sort_values(ascending=False).head(args.max_hotels)
            
            # Create lists for each hotel's data
            for i, (hotel, revenue) in enumerate(top_hotels.items()):
                if pd.notna(revenue) and revenue > 0:
                    region = metadata.loc['Region', hotel]
                    ticker = metadata.loc['Ticker', hotel] if 'Ticker' in metadata.index else ""
                    color = region_colors.get(region, '#808080')
                    
                    # Get logo path and encode it
                    logo_path = get_logo_path(hotel, year, ticker)
                    encoded_logo = get_encoded_image(logo_path) if logo_path else None
                    
                    # Use ticker as label if available, otherwise use the first 3 characters of hotel name
                    hotel_label = ticker if ticker and pd.notna(ticker) and ticker.strip() != "" else hotel[:3]
                    
                    hotels.append(hotel_label)  # Use ticker as label
                    revenues.append(revenue)
                    colors.append(color)
                    logos.append(encoded_logo)
                    y_positions.append(i)  # Use numerical position
                    
                    hover_text = f"<b>{hotel}</b><br>"
                    hover_text += f"Revenue: {format_revenue(revenue)}<br>"
                    hover_text += f"Region: {region}<br>"
                    hover_text += f"Ticker: {ticker}"
                    hover_texts.append(hover_text)
        
        # Skip quarters with no data
        if not hotels:
            continue
            
        # Store data (already sorted by revenue due to top_hotels being sorted)
        quarter_info = {
            'quarter': quarter,
            'hotels': hotels,
            'revenues': revenues,
            'colors': colors,
            'hover_texts': hover_texts,
            'formatted_revenues': [format_revenue(rev) for rev in revenues],
            'logos': logos,
            'y_positions': y_positions  # Add y_positions to the data
        }
        all_quarters_data.append(quarter_info)
    
    # Return None if no quarters have data
    if not all_quarters_data:
        print("No quarters with data found. Check the CSV format and content.")
        return None
        
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
                marker=dict(color=initial_data['colors'][::-1],
                            line=dict(width=0, color='rgba(0,0,0,0)')),
                hoverinfo='none',
                width=0.8,
                showlegend=False
            )
    )
    
    # Add text layer with transparent bars - Add vertical offset
    fig.add_trace(
            go.Bar(
                x=initial_data['revenues'][::-1],
                y=[y - 0.05 for y in initial_data['y_positions'][::-1]],  # Add small offset for text
                orientation='h',
                marker=dict(color='rgba(0,0,0,0)',
                            line=dict(width=0, color='rgba(0,0,0,0)')),
                text=initial_data['formatted_revenues'][::-1],
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
                width=0.8,
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
    max_revenue = revenue_data.max().max()
    global_x_offset = max_revenue * 1.05
    fixed_logo_width = max_revenue * 0.2
    
    for i, (hotel, revenue, logo) in enumerate(zip(initial_data['hotels'], initial_data['revenues'], initial_data['logos'])):
        if logo:
            fig.add_layout_image(
                dict(
                    source=logo,
                    xref="x",
                    yref="y",
                    x=global_x_offset,
                    y=i - 0.05,  # Add small offset for logo
                    sizex=fixed_logo_width,
                    sizey=0.8,
                    xanchor="left",
                    yanchor="middle",
                    sizing="contain",
                    opacity=0.95
                )
            )

    # 调整x轴以容纳logo
    x_axis_range = [0, max_revenue * 1.5]  # 确保图表有足够空间显示logo

    # Update layout with numerical yaxis
    fig.update_layout(
        title={
            'text': "Hotel Revenue Visualization",
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
                'text': "Revenue",
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
                'text': "Hotel",
                'font': {'family': 'Monda', 'size': 16}
            },
            tickmode='array',
            tickvals=initial_data['y_positions'],
            ticktext=initial_data['hotels'],
            tickfont={'family': 'Monda', 'size': 14},
            fixedrange=True,
            autorange='reversed'
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
        bargap=0.15,
        bargroupgap=0.1,
        uniformtext=dict(
            mode='hide',
            minsize=14
        ),
        # Add timestamp annotation to the upper left corner
        annotations=[
            dict(
                text=initial_data['quarter'],
                x=0.02,
                y=0.98,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(
                    family="Monda",
                    size=24,
                    color="black"
                ),
                align="left"
            )
        ]
    )
    
    # Convert to HTML
    html_content = pio.to_html(
        fig,
        include_plotlyjs=False,
        full_html=False,
        div_id='hotel-chart'
    )
    
    # Convert data to JSON for JavaScript
    import json
    quarters_data_json = json.dumps(all_quarters_data)
    
    # Create custom HTML with updated JavaScript
    custom_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Hotel Revenue Visualization</title>
    <style>
        body {{
            font-family: 'Monda', Arial, sans-serif;
            margin: 0;
            padding: 20px;
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
    <script src="https://cdn.plot.ly/plotly-2.27.1.min.js" defer></script>
</head>
<body>
    {html_content}
    
    <div class="control-panel">
        <div class="quarter-display">
            <span id="current-quarter">{initial_quarter}</span>
        </div>
        <div class="slider-container">
            <input type="range" id="quarter-slider" min="0" max="{max_quarters}" step="1" value="0">
        </div>
        <div class="button-container">
            <button id="play-button">Play</button>
            <button id="pause-button">Pause</button>
            <button id="reset-button">Reset</button>
        </div>
    </div>
    
    <script>
        window.addEventListener('load', async function() {{
            while (!window.Plotly) {{
                await new Promise(resolve => setTimeout(resolve, 100));
            }}

            const allQuartersData = {quarters_data};
            let currentQuarterIndex = 0;
            const animationDuration = {animation_duration};
            let isPlaying = false;
            let playInterval = null;
            
            const chartDiv = document.getElementById('hotel-chart');
            const currentQuarterDisplay = document.getElementById('current-quarter');
            const quarterSlider = document.getElementById('quarter-slider');
            const playButton = document.getElementById('play-button');
            const pauseButton = document.getElementById('pause-button');
            const resetButton = document.getElementById('reset-button');
            
            const initialData = allQuartersData[0];
            
            // Create traces array with the bar chart and region legends
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
                    y: initialData.y_positions,
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
            
            const regions = {{
                'US': '#40E0D0',
                'CA': '#40E0D0',
                'GB': '#4169E1',
                'BM': '#4169E1',
                'FR': '#4169E1',
                'ES': '#4169E1',
                'IE': '#4169E1',
                'SE': '#4169E1',
                'CN': '#FF4B4B',
                'HK': '#FF4B4B',
                'MY': '#FF4B4B',
                'SG': '#FF4B4B',
                'TH': '#FF4B4B',
                'JP': '#FF4B4B',
                'KR': '#FF4B4B',
                'IN': '#32CD32',
                'AU': '#9932CC',
                'ZA': '#DAA520',
                'AE': '#DEB887',
                'MO': '#FF4B4B'
            }};
            
            Object.entries(regions).forEach(([region, color]) => {{
                traces.push({{
                    type: 'scatter',
                    x: [NaN],
                    y: [NaN],
                    mode: 'markers',
                    marker: {{
                        size: 20,
                        color: color
                    }},
                    name: region,
                    showlegend: true,
                    hoverinfo: 'skip',
                    visible: 'legendonly'
                }});
            }});
            
            const layout = {{
                title: {{
                    text: "Hotel Revenue Visualization",
                    y: 0.95,
                    x: 0.5,
                    xanchor: 'center',
                    yanchor: 'top',
                    font: {{family: 'Monda', size: 24}}
                }},
                width: {width},
                height: {height},
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
                        text: "Hotel",
                        font: {{family: 'Monda', size: 16}}
                    }},
                    tickmode: 'array',
                    tickvals: initialData.y_positions,
                    ticktext: initialData.hotels,
                    tickfont: {{family: 'Monda', size: 14}},
                    autorange: 'reversed'
                }},
                plot_bgcolor: 'white',
                paper_bgcolor: 'white',
                hovermode: "closest",
                font: {{family: "Monda", size: 14}},
                margin: {{l: 100, r: 150, t: 100, b: 140}},
                showlegend: true,
                legend: {{
                    itemsizing: 'constant',
                    title: {{text: 'Regions'}},
                    tracegroupgap: 0,
                    orientation: "h",
                    yanchor: "top",
                    y: -0.15,
                    xanchor: "left",
                    x: 0.1
                }},
                images: initialData.logos.map((logo, i) => 
                    logo ? {{
                        source: logo,
                        xref: "x",
                        yref: "y",
                        x: initialData.revenues[0] * 1.05,
                        y: i,
                        sizex: initialData.revenues[0] * 0.2,
                        sizey: 0.8,
                        xanchor: "left",
                        yanchor: "middle",
                        sizing: "contain",
                        opacity: 0.95
                    }} : null
                ).filter(img => img !== null),
                annotations: [
                    {{
                        text: initialData.quarter,
                        x: 0.02,
                        y: 0.98,
                        xref: "paper",
                        yref: "paper",
                        showarrow: false,
                        font: {{
                            family: "Monda",
                            size: 24,
                            color: "black"
                        }},
                        align: "left"
                    }}
                ]
            }};
            
            await Plotly.newPlot(chartDiv, traces, layout);
            
            let historicalMaxRevenue = Math.max(...initialData.revenues);
            
            async function playAnimation() {{
                if (isPlaying) return;
                isPlaying = true;
                
                let lastFrameTime = performance.now();
                const frameDuration = 16;
                const quarterDuration = 2500;
                let currentTime = 0;
                
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
                    
                    const interpolatedData = currentData.revenues.map((startVal, i) => ({{
                        hotel: currentData.hotels[i],
                        revenue: startVal + (nextData.revenues[i] - startVal) * progress,
                        logo: currentData.logos[i],
                        color: currentData.colors[i],
                        formattedRevenue: formatRevenue(startVal + (nextData.revenues[i] - startVal) * progress),
                        y_position: i
                    }}));
                    
                    interpolatedData.sort((a, b) => b.revenue - a.revenue);
                    
                    const hotelsSorted = interpolatedData.map(d => d.hotel);
                    const revenuesSorted = interpolatedData.map(d => d.revenue);
                    const logosSorted = interpolatedData.map(d => d.logo);
                    const colorsSorted = interpolatedData.map(d => d.color);
                    const formattedRevenuesSorted = interpolatedData.map(d => d.formattedRevenue);
                    const yPositionsSorted = interpolatedData.map((d, i) => i);
                    
                    const currentMaxRevenue = Math.max(...revenuesSorted);
                    historicalMaxRevenue = Math.max(historicalMaxRevenue, currentMaxRevenue);
                    const xAxisMax = historicalMaxRevenue * 1.5;
                    
                    try {{
                        const globalXOffset = historicalMaxRevenue * 1.05;
                        const fixedLogoWidth = historicalMaxRevenue * 0.2;
                        
                        Plotly.update(chartDiv, {{
                            'x': [revenuesSorted, revenuesSorted],
                            'y': [yPositionsSorted, yPositionsSorted.map(y => y - 0.05)],  // Add offset for text
                            'marker.color': [colorsSorted, Array(colorsSorted.length).fill('rgba(0,0,0,0)')],
                            'text': [[], formattedRevenuesSorted],
                            'width': [0.8, 0.8]
                        }}, {{
                            'yaxis.ticktext': hotelsSorted,
                            'yaxis.tickvals': yPositionsSorted,
                            'yaxis.autorange': 'reversed',
                            'xaxis.range': [0, xAxisMax],
                            'images': logosSorted.map((logo, i) => 
                                logo ? {{
                                    source: logo,
                                    xref: "x",
                                    yref: "y",
                                    x: revenuesSorted[i] + xAxisMax * 0.08,
                                    y: i - 0.05,  // Add offset for logo
                                    sizex: fixedLogoWidth * 0.7,
                                    sizey: 0.8,
                                    xanchor: "left",
                                    yanchor: "middle",
                                    sizing: "contain",
                                    opacity: 0.95
                                }} : null
                            ).filter(img => img !== null),
                            'annotations': [
                                {{
                                    text: interpolateQuarters(currentData.quarter, nextData.quarter, progress),
                                    x: 0.02,
                                    y: 0.98,
                                    xref: "paper",
                                    yref: "paper",
                                    showarrow: false,
                                    font: {{
                                        family: "Monda",
                                        size: 24,
                                        color: "black"
                                    }},
                                    align: "left"
                                }}
                            ]
                        }});
                        
                        const quarterText = interpolateQuarters(currentData.quarter, nextData.quarter, progress);
                        currentQuarterDisplay.textContent = quarterText;
                        
                    }} catch (e) {{
                        console.error("Animation error:", e);
                    }}
                    
                    requestAnimationFrame(animate);
                }}
                
                requestAnimationFrame(animate);
            }}
            
            function formatRevenue(value) {{
                if (value >= 1000) {{
                    return '$' + (value/1000).toFixed(1) + 'B';
                }}
                return '$' + Math.round(value) + 'M';
            }}
            
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
            
            function pauseAnimation() {{
                isPlaying = false;
                if (playInterval) {{
                    clearTimeout(playInterval);
                    playInterval = null;
                }}
            }}
            
            async function resetAnimation() {{
                pauseAnimation();
                quarterSlider.value = 0;
                await updateChart(0);
            }}
            
            quarterSlider.addEventListener('input', async function() {{
                pauseAnimation();
                const newIndex = parseInt(this.value);
                if (newIndex !== currentQuarterIndex) {{
                    await updateChart(newIndex);
                }}
            }});
            
            playButton.addEventListener('click', playAnimation);
            pauseButton.addEventListener('click', pauseAnimation);
            resetButton.addEventListener('click', resetAnimation);
            
            setTimeout(playAnimation, 1000);
        }});
    </script>
</body>
</html>
    """.format(
        html_content=html_content,
        initial_quarter=initial_data['quarter'],
        max_quarters=len(quarters) - 1,
        quarters_data=quarters_data_json,
        animation_duration=args.transition_duration,
        width=args.width,
        height=args.height
    )

    
    # Save HTML file
    with open(args.output, 'w') as f:
        f.write(custom_html)
    
    print(f"Visualization saved successfully to {args.output}")
    
    return fig

if __name__ == "__main__":
    print("Starting Plotly Hotel Revenue Visualization")
    fig = create_visualization()
    print("Visualization complete!") 