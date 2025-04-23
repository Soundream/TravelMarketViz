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
        # More logo mappings here...
    }
    
    if iata_code == "DY":
        norwegian_logo = "airline-bar-video/logos/norwegian-logo.jpg"
        return norwegian_logo if os.path.exists(norwegian_logo) else None
        
    if airline not in logo_mapping:
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
                return None
    
    return None

def create_visualization():
    """Create interactive Plotly visualization for airline revenue data"""
    # Load the data from CSV
    df = pd.read_csv('airline-bar-video/airlines_final.csv')
    
    # Process metadata
    metadata = df.iloc[:7].copy()  # First 7 rows contain metadata
    revenue_data = df.iloc[7:].copy()  # Revenue data starts from row 8
    
    # Set proper index for metadata
    metadata.set_index(metadata.columns[0], inplace=True)
    
    # Convert revenue columns by removing ' M' suffix, commas, and converting to float
    for col in revenue_data.columns[1:]:  # Skip the first column which contains row labels
        revenue_data[col] = pd.to_numeric(revenue_data[col].str.replace(',', '').str.replace(' M', ''), errors='coerce')
    
    # Set index for revenue data
    revenue_data.set_index(revenue_data.columns[0], inplace=True)
    
    # Get the quarters from the revenue data index
    quarters = revenue_data.index.tolist()
    
    # Initialize figure with subplots
    fig = make_subplots(
        rows=1, cols=1,
        specs=[[{"type": "bar"}]],
        subplot_titles=["Airline Revenue Over Time"]
    )
    
    # Create frames for animation
    frames = []
    
    # Process each quarter
    for quarter in tqdm(quarters, desc="Generating frames"):
        year, q = parse_quarter(quarter)
        
        # Get data for current quarter
        quarter_data = revenue_data.loc[quarter].dropna()
        
        # Sort airlines by revenue and take top N
        top_airlines = quarter_data.sort_values(ascending=False).head(args.max_airlines)
        
        # Create frame data
        airlines = []
        revenues = []
        colors = []
        hover_texts = []
        
        for airline, revenue in top_airlines.items():
            if pd.notna(revenue) and revenue > 0:
                region = metadata.loc['Region', airline]
                color = region_colors.get(region, '#808080')
                
                iata_code = metadata.loc['IATA Code', airline]
                label = iata_code if pd.notna(iata_code) else airline[:3]
                
                airlines.append(label)
                revenues.append(revenue)
                colors.append(color)
                
                # Create hover text with detailed information
                hover_text = f"<b>{airline}</b><br>"
                hover_text += f"Revenue: {format_revenue(revenue)}<br>"
                hover_text += f"Region: {region}<br>"
                hover_text += f"IATA Code: {iata_code}"
                hover_texts.append(hover_text)
        
        # Create a frame
        frame = go.Frame(
            data=[
                go.Bar(
                    x=revenues[::-1],
                    y=airlines[::-1],
                    orientation='h',
                    marker=dict(color=colors[::-1]),
                    text=[format_revenue(rev) for rev in revenues[::-1]],
                    textposition='outside',
                    hovertext=hover_texts[::-1],
                    hoverinfo='text',
                )
            ],
            name=quarter,
            layout=go.Layout(
                title=f"Airline Revenue - {quarter}",
                xaxis=dict(
                    title="Revenue",
                    tickformat="$,.0f",
                    range=[0, revenue_data.max().max() * 1.1]
                ),
                yaxis=dict(
                    title="Airline",
                )
            )
        )
        frames.append(frame)
    
    # Get data for initial frame
    initial_quarter = quarters[0]
    initial_data = revenue_data.loc[initial_quarter].dropna()
    top_initial = initial_data.sort_values(ascending=False).head(args.max_airlines)
    
    initial_airlines = []
    initial_revenues = []
    initial_colors = []
    initial_hover_texts = []
    
    for airline, revenue in top_initial.items():
        if pd.notna(revenue) and revenue > 0:
            region = metadata.loc['Region', airline]
            color = region_colors.get(region, '#808080')
            
            iata_code = metadata.loc['IATA Code', airline]
            label = iata_code if pd.notna(iata_code) else airline[:3]
            
            initial_airlines.append(label)
            initial_revenues.append(revenue)
            initial_colors.append(color)
            
            # Create hover text with detailed information
            hover_text = f"<b>{airline}</b><br>"
            hover_text += f"Revenue: {format_revenue(revenue)}<br>"
            hover_text += f"Region: {region}<br>"
            hover_text += f"IATA Code: {iata_code}"
            initial_hover_texts.append(hover_text)
    
    # Create initial bar chart
    fig.add_trace(
        go.Bar(
            x=initial_revenues[::-1],
            y=initial_airlines[::-1],
            orientation='h',
            marker=dict(color=initial_colors[::-1]),
            text=[format_revenue(rev) for rev in initial_revenues[::-1]],
            textposition='outside',
            hovertext=initial_hover_texts[::-1],
            hoverinfo='text',
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
            'font': {'size': 24}
        },
        width=args.width,
        height=args.height,
        xaxis=dict(
            title="Revenue",
            tickformat="$,.0f",
            range=[0, revenue_data.max().max() * 1.1]
        ),
        yaxis=dict(
            title="Airline",
        ),
        plot_bgcolor='white',  # 设置绘图区背景为白色
        paper_bgcolor='white',  # 设置整个图表纸背景为白色
        updatemenus=[
            {
                "type": "buttons",
                "direction": "right",
                "active": 0,
                "x": 0.1,
                "y": 1.15,
                "buttons": [
                    {
                        "label": "Play",
                        "method": "animate",
                        "args": [
                            None,
                            {
                                "frame": {"duration": args.transition_duration, "redraw": True},
                                "fromcurrent": True,
                                "transition": {"duration": args.transition_duration, "easing": "linear"}
                            }
                        ]
                    },
                    {
                        "label": "Pause",
                        "method": "animate",
                        "args": [
                            [None],
                            {
                                "frame": {"duration": 0, "redraw": False},
                                "mode": "immediate",
                                "transition": {"duration": 0}
                            }
                        ]
                    }
                ]
            }
        ],
        sliders=[
            {
                "active": 0,
                "steps": [
                    {
                        "label": quarter,
                        "method": "animate",
                        "args": [
                            [quarter],
                            {
                                "frame": {"duration": args.transition_duration, "redraw": True},
                                "mode": "immediate",
                                "transition": {"duration": args.transition_duration}
                            }
                        ]
                    }
                    for quarter in quarters
                ],
                "x": 0.1,
                "y": 0,
                "currentvalue": {
                    "visible": True,
                    "prefix": "Quarter: ",
                    "xanchor": "right",
                    "font": {"size": 16}
                },
                "len": 0.9
            }
        ],
        hovermode="closest",
        font=dict(family="Arial, sans-serif", size=14),
        margin=dict(l=100, r=20, t=100, b=80),
    )
    
    # Add frames to the figure
    fig.frames = frames
    
    # Add legend for regions
    for region, color in region_colors.items():
        fig.add_trace(
            go.Bar(
                x=[None],
                y=[None],
                orientation='h',
                marker=dict(color=color),
                name=region,
                showlegend=True,
                hoverinfo='none'
            )
        )
    
    # Save to HTML file
    print(f"Saving visualization to {args.output}...")
    pio.write_html(fig, args.output, auto_open=False)
    print(f"Visualization saved successfully to {args.output}")
    
    return fig

if __name__ == "__main__":
    print("Starting Plotly Airline Revenue Visualization")
    fig = create_visualization()
    print("Visualization complete!") 