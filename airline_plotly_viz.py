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
parser = argparse.ArgumentParser(description='Generate airline revenue visualization using Plotly')
parser.add_argument('--output', type=str, default='output/airline_revenue_plotly.html', 
                    help='Output HTML file path')
parser.add_argument('--frames-per-year', type=int, default=4, 
                    help='Number of frames to generate per year (default: 4 for quarterly)')
parser.add_argument('--height', type=int, default=800, 
                    help='Height of the visualization in pixels (default: 800)')
parser.add_argument('--width', type=int, default=1200, 
                    help='Width of the visualization in pixels (default: 1200)')
parser.add_argument('--max-airlines', type=int, default=15, 
                    help='Maximum number of airlines to display (default: 15)')
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
    'North America': '#40E0D0',  # Turquoise
    'Europe': '#4169E1',         # Royal Blue
    'Asia Pacific': '#FF4B4B',   # Red
    'Latin America': '#32CD32',  # Lime Green
    'China': '#FF4B4B',          # Red (same as Asia Pacific)
    'Middle East': '#DEB887',    # Burlywood
    'Russia': '#FF4B4B',         # Red (same as Asia Pacific)
    'Turkey': '#DEB887'          # Burlywood (same as Middle East)
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

def get_logo_path(airline, year, iata_code, month=6):
    """Get the appropriate logo path based on airline name, year and month"""
    logo_mapping = {
        "easyJet": [{"start_year": 1999, "end_year": 9999, "file": "airline-bar-video/logos/easyJet-1999-now.jpg"}],
        "Emirates": [{"start_year": 1999, "end_year": 9999, "file": "airline-bar-video/logos/Emirates-logo.jpg"}],
        "Air France-KLM": [
            {"start_year": 1999, "end_year": 2004, "file": "airline-bar-video/logos/klm-1999-now.png"},
            {"start_year": 2004, "end_year": 9999, "file": "airline-bar-video/logos/Air-France-KLM-Holding-Logo.png"}
        ],
        "American Airlines": [{"start_year": 1999, "end_year": 9999, "file": "airline-bar-video/logos/aa-logo.png"}],
        "United Airlines": [{"start_year": 1999, "end_year": 9999, "file": "airline-bar-video/logos/ua-logo.png"}],
        "Delta Air Lines": [{"start_year": 1999, "end_year": 9999, "file": "airline-bar-video/logos/delta-logo.png"}],
        "Southwest Airlines": [{"start_year": 1999, "end_year": 9999, "file": "airline-bar-video/logos/southwest-logo.png"}],
        "Lufthansa": [{"start_year": 1999, "end_year": 9999, "file": "airline-bar-video/logos/lufthansa-logo.png"}],
        "British Airways": [{"start_year": 1999, "end_year": 9999, "file": "airline-bar-video/logos/ba-logo.png"}],
        "Air China": [{"start_year": 1999, "end_year": 9999, "file": "airline-bar-video/logos/air-china-logo.png"}],
        "China Southern": [{"start_year": 1999, "end_year": 9999, "file": "airline-bar-video/logos/china-southern-logo.png"}],
        "China Eastern": [{"start_year": 1999, "end_year": 9999, "file": "airline-bar-video/logos/china-eastern-logo.png"}],
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
            {"start_year": 2018, "end_year": 9999, "file": "airline-bar-video/logos/skywest-2018-now.jpg"}
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
        ]
    }
    
    if iata_code == "DY":
        norwegian_logo = "airline-bar-video/logos/norwegian-logo.jpg"
        return norwegian_logo if os.path.exists(norwegian_logo) else None
        
    if airline not in logo_mapping:
        print(f"Logo not found for {airline}")
        return None
        
    logo_versions = logo_mapping[airline]
    
    if airline == "Air France-KLM":
        if year < 2004 or (year == 2004 and month < 5):
            for version in logo_versions:
                if version["file"] == "airline-bar-video/logos/klm-1999-now.png":
                    logo_path = version["file"]
                    return logo_path if os.path.exists(logo_path) else None
        else:
            for version in logo_versions:
                if version["file"] == "airline-bar-video/logos/Air-France-KLM-Holding-Logo.png":
                    logo_path = version["file"]
                    return logo_path if os.path.exists(logo_path) else None
    
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
    """Create interactive Plotly visualization for airline revenue data"""
    # Load the data from CSV
    df = pd.read_csv('airline-bar-video/airlines_final.csv')
    
    # Process metadata
    metadata = df.iloc[:7].copy()
    revenue_data = df.iloc[7:].copy()
    
    metadata.set_index(metadata.columns[0], inplace=True)
    
    # Convert revenue columns
    for col in revenue_data.columns[1:]:
        revenue_data[col] = pd.to_numeric(revenue_data[col].str.replace(',', '').str.replace(' M', ''), errors='coerce')
    
    revenue_data.set_index(revenue_data.columns[0], inplace=True)
    quarters = revenue_data.index.tolist()
    
    # 准备所有季度的数据
    all_quarters_data = []
    
    # Process each quarter
    for quarter in tqdm(quarters, desc="Processing data"):
        year, q = parse_quarter(quarter)
        month = q * 3
        
        quarter_data = revenue_data.loc[quarter].dropna()
        top_airlines = quarter_data.sort_values(ascending=False).head(args.max_airlines)
        
        airlines = []
        revenues = []
        colors = []
        hover_texts = []
        logos = []
        
        for airline, revenue in top_airlines.items():
            if pd.notna(revenue) and revenue > 0:
                region = metadata.loc['Region', airline]
                color = region_colors.get(region, '#808080')
                iata_code = metadata.loc['IATA Code', airline]
                label = iata_code if pd.notna(iata_code) else airline[:3]
                
                # Get logo path and encode it
                logo_path = get_logo_path(airline, year, iata_code, month)
                encoded_logo = get_encoded_image(logo_path) if logo_path else None
                
                airlines.append(label)
                revenues.append(revenue)
                colors.append(color)
                logos.append(encoded_logo)
                
                hover_text = f"<b>{airline}</b><br>"
                hover_text += f"Revenue: {format_revenue(revenue)}<br>"
                hover_text += f"Region: {region}<br>"
                hover_text += f"IATA Code: {iata_code}"
                hover_texts.append(hover_text)
        
        # Store data in reverse order
        quarter_info = {
            'quarter': quarter,
            'airlines': airlines[::-1],
            'revenues': revenues[::-1],
            'colors': colors[::-1],
            'hover_texts': hover_texts[::-1],
            'formatted_revenues': [format_revenue(rev) for rev in revenues[::-1]],
            'logos': logos[::-1]
        }
        all_quarters_data.append(quarter_info)
    
    # Get initial data
    initial_data = all_quarters_data[0]
    
    # Create initial chart
    fig = go.Figure()
    
    # Add single bar trace
    fig.add_trace(
            go.Bar(
                x=initial_data['revenues'],
                y=initial_data['airlines'],
                orientation='h',
                marker=dict(color=initial_data['colors']),
                text=initial_data['formatted_revenues'],
                textposition='outside',
            hoverinfo='none',  # Remove hover text since we have values shown outside
            textfont={"family": "Monda", "size": 14},
            width=0.8,
            showlegend=False
        )
    )
    
    # Create a legend trace for each region without using bars
    fig.update_layout(
        showlegend=True,
        legend=dict(
            itemsizing='constant',
            title=dict(text='Regions'),
            tracegroupgap=0
        )
    )
    
    # Add region colors to legend using scatter points
    for region, color in region_colors.items():
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode='markers',
                marker=dict(size=10, color=color),
                name=region,
                showlegend=True
            )
        )
    
    # Add logos
    for i, (airline, revenue, logo) in enumerate(zip(initial_data['airlines'], initial_data['revenues'], initial_data['logos'])):
        if logo:
            fig.add_layout_image(
                dict(
                    source=logo,
                    xref="x",
                    yref="y",
                    x=revenue,
                    y=airline,
                    sizex=revenue * 0.05,
                    sizey=0.6,
                    xanchor="left",
                    yanchor="middle",
                    sizing="contain"
                )
            )
    
    # Update layout
    fig.update_layout(
        title={
            'text': "Airline Revenue Visualization",
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
            range=[0, revenue_data.max().max() * 1.2],
            showgrid=True,
            gridcolor='lightgrey',
            gridwidth=1,
            griddash='dot',
            tickfont={'family': 'Monda', 'size': 14}
        ),
        yaxis=dict(
            title={
                'text': "Airline",
                'font': {'family': 'Monda', 'size': 16}
            },
            tickfont={'family': 'Monda', 'size': 14}
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode="closest",
        font=dict(family="Monda", size=14),
        margin=dict(l=100, r=100, t=100, b=140)
    )
    
    # Convert to HTML
    html_content = pio.to_html(
        fig,
        include_plotlyjs=False,
        full_html=False,
        div_id='airline-chart'
    )
    
    # Convert data to JSON for JavaScript
    import json
    quarters_data_json = json.dumps(all_quarters_data)
    
    # Create custom HTML
    custom_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Airline Revenue Visualization</title>
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
            <span id="current-quarter">{initial_data['quarter']}</span>
        </div>
        <div class="slider-container">
            <input type="range" id="quarter-slider" min="0" max="{len(quarters) - 1}" step="1" value="0">
        </div>
        <div class="button-container">
            <button id="play-button">Play</button>
            <button id="pause-button">Pause</button>
            <button id="reset-button">Reset</button>
        </div>
    </div>
    
    <script>
        // Wait for Plotly to load and initialize
        window.addEventListener('load', async function() {{
            // Wait for Plotly to be available
            while (!window.Plotly) {{
                await new Promise(resolve => setTimeout(resolve, 100));
            }}

        const allQuartersData = {quarters_data_json};
        let currentQuarterIndex = 0;
        const animationDuration = {args.transition_duration};
        let isPlaying = false;
        let playInterval = null;
        
            const chartDiv = document.getElementById('airline-chart');
        const currentQuarterDisplay = document.getElementById('current-quarter');
        const quarterSlider = document.getElementById('quarter-slider');
        const playButton = document.getElementById('play-button');
        const pauseButton = document.getElementById('pause-button');
        const resetButton = document.getElementById('reset-button');
        
            // Initialize the plot with the first dataset
            const initialData = allQuartersData[0];
            
            // Create traces array with the bar chart and region legends
            const traces = [
                // Main bar chart
                {{
                    type: 'bar',
                    x: initialData.revenues,
                    y: initialData.airlines,
                    orientation: 'h',
                    marker: {{
                        color: initialData.colors
                    }},
                    text: initialData.formatted_revenues,
                    textposition: 'outside',
                    hoverinfo: 'none',
                    width: 0.8,
                    showlegend: false
                }}
            ];
            
            // Add region legends using scatter points
            const regions = {{
                'North America': '#40E0D0',
                'Europe': '#4169E1',
                'Asia Pacific': '#FF4B4B',
                'Latin America': '#32CD32',
                'China': '#FF4B4B',
                'Middle East': '#DEB887',
                'Russia': '#FF4B4B',
                'Turkey': '#DEB887'
            }};
            
            Object.entries(regions).forEach(([region, color]) => {{
                traces.push({{
                    type: 'scatter',
                    x: [null],
                    y: [null],
                    mode: 'markers',
                    marker: {{
                        size: 10,
                        color: color
                    }},
                    name: region,
                    showlegend: true
                }});
            }});

            const layout = {{
                title: {{
                    text: "Airline Revenue Visualization",
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
                    range: [0, Math.max(...initialData.revenues) * 1.2],
                    showgrid: true,
                    gridcolor: 'lightgrey',
                    gridwidth: 1,
                    griddash: 'dot',
                    tickfont: {{family: 'Monda', size: 14}}
                }},
                yaxis: {{
                    title: {{
                        text: "Airline",
                        font: {{family: 'Monda', size: 16}}
                    }},
                    tickfont: {{family: 'Monda', size: 14}}
                }},
                plot_bgcolor: 'white',
                paper_bgcolor: 'white',
                hovermode: "closest",
                font: {{family: "Monda", size: 14}},
                margin: {{l: 100, r: 100, t: 100, b: 140}},
                showlegend: true,
                legend: {{
                    itemsizing: 'constant',
                    title: {{text: 'Regions'}},
                    tracegroupgap: 0
                }},
                images: initialData.logos.map((logo, i) => 
                    logo ? {{
                        source: logo,
                        xref: "x",
                        yref: "y",
                        x: initialData.revenues[i],
                        y: initialData.airlines[i],
                        sizex: initialData.revenues[i] * 0.05,
                        sizey: 0.6,
                        xanchor: "left",
                        yanchor: "middle",
                        sizing: "contain"
                    }} : null
                ).filter(img => img !== null)
            }};

            // Create the initial plot with all traces
            await Plotly.newPlot(chartDiv, traces, layout);
            
            // Animation helper function
            function animate(fromData, toData) {{
                return new Promise((resolve) => {{
                    const startTime = performance.now();
                    
                    function step(currentTime) {{
                        const elapsedTime = currentTime - startTime;
                        const progress = Math.min(elapsedTime / animationDuration, 1);
                        
                        // Interpolate revenue values
                        const interpolatedRevenues = fromData.revenues.map((startVal, i) => {{
                            return startVal + (toData.revenues[i] - startVal) * progress;
                        }});
                        
                        // Calculate current max for axis scaling
                        const maxRevenue = Math.max(...interpolatedRevenues);
                        
                        // Update bar chart with current values
                        Plotly.update(chartDiv, 
                            // Data update
                            {{
                                x: [interpolatedRevenues]
                            }},
                            // Layout update
                            {{
                                xaxis: {{
                                    range: [0, maxRevenue * 1.2]
                                }},
                                images: toData.logos.map((logo, i) => 
                                    logo ? {{
                                        source: logo,
                                        xref: "x",
                                        yref: "y",
                                        x: interpolatedRevenues[i],
                                        y: toData.airlines[i],
                                        sizex: interpolatedRevenues[i] * 0.05,
                                        sizey: 0.6,
                                        xanchor: "left",
                                        yanchor: "middle",
                                        sizing: "contain"
                                    }} : null
                                ).filter(img => img !== null)
                            }}
                        );
                        
                        if (progress < 1) {{
                            requestAnimationFrame(step);
                        }} else {{
                            // Final update with exact values
                            Plotly.update(chartDiv,
                                {{
                                    x: [toData.revenues],
                                    y: [toData.airlines],
                                    'marker.color': [toData.colors],
                                    text: [toData.formatted_revenues]
                                }},
                                {{
                                    xaxis: {{
                                        range: [0, Math.max(...toData.revenues) * 1.2]
                                    }},
                                    images: toData.logos.map((logo, i) => 
                                        logo ? {{
                                            source: logo,
                                            xref: "x",
                                            yref: "y",
                                            x: toData.revenues[i],
                                            y: toData.airlines[i],
                                            sizex: toData.revenues[i] * 0.05,
                                            sizey: 0.6,
                                            xanchor: "left",
                                            yanchor: "middle",
                                            sizing: "contain"
                                        }} : null
                                    ).filter(img => img !== null)
                                }}
                            );
                            resolve();
                        }}
                    }}
                    
                    requestAnimationFrame(step);
                }});
            }}
            
            // Update chart function
            async function updateChart(index) {{
                const fromData = allQuartersData[currentQuarterIndex];
                const toData = allQuartersData[index];
                
                currentQuarterDisplay.textContent = toData.quarter;
                
                // Animate transition
                await animate(fromData, toData);
                
                // Update current index after animation completes
                currentQuarterIndex = index;
            }}
            
            // Play animation function
            async function playAnimation() {{
                if (isPlaying) return;
                isPlaying = true;
                
                async function playNext() {{
                    if (!isPlaying) return;
                    
                    const nextIndex = currentQuarterIndex + 1;
                    if (nextIndex < allQuartersData.length) {{
                        quarterSlider.value = nextIndex;
                        await updateChart(nextIndex);
                        playInterval = setTimeout(playNext, 100);
                    }} else {{
                        // Reset to beginning if at the end
                        quarterSlider.value = 0;
                        await updateChart(0);
                        isPlaying = false;
                    }}
                }}
                
                await playNext();
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
            
            // Start animation automatically after plot is created
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
    
    return fig

if __name__ == "__main__":
    print("Starting Plotly Airline Revenue Visualization")
    fig = create_visualization()
    print("Visualization complete!") 