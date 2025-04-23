#!/usr/bin/env python
import os
import argparse
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import plotly.io as pio
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# Add argument parser
parser = argparse.ArgumentParser(description='Export airline revenue visualization as PNG frames or MP4 video')
parser.add_argument('--output-dir', type=str, default='output/frames', 
                    help='Output directory for PNG frames')
parser.add_argument('--output-video', type=str, default='output/airline_revenue_plotly.mp4', 
                    help='Output MP4 file path')
parser.add_argument('--frames-per-year', type=int, default=4, 
                    help='Number of frames to generate per year (default: 4 for quarterly)')
parser.add_argument('--height', type=int, default=800, 
                    help='Height of the visualization in pixels (default: 800)')
parser.add_argument('--width', type=int, default=1200, 
                    help='Width of the visualization in pixels (default: 1200)')
parser.add_argument('--max-airlines', type=int, default=15, 
                    help='Maximum number of airlines to display (default: 15)')
parser.add_argument('--fps', type=int, default=2, 
                    help='Frames per second for the video (default: 2)')
parser.add_argument('--format', type=str, choices=['png', 'mp4', 'both'], default='both',
                    help='Output format: png, mp4, or both (default: both)')
args = parser.parse_args()

# Create required directories
if not os.path.exists(args.output_dir):
    os.makedirs(args.output_dir)
    print(f"Created directory: {args.output_dir}")

video_dir = os.path.dirname(args.output_video)
if not os.path.exists(video_dir):
    os.makedirs(video_dir)
    print(f"Created directory: {video_dir}")

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

def export_visualization():
    """Create and export Plotly visualization for airline revenue data"""
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
    
    # Create frames for all quarters
    frame_files = []
    
    # Process each quarter
    for i, quarter in enumerate(tqdm(quarters, desc="Generating frames")):
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
        
        # Create the figure for this frame
        fig = go.Figure()
        
        # Add the bars
        fig.add_trace(
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
        )
        
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
        
        # Update layout
        fig.update_layout(
            title={
                'text': f"Airline Revenue - {quarter}",
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
            hovermode="closest",
            font=dict(family="Arial, sans-serif", size=14),
            margin=dict(l=100, r=20, t=100, b=80),
        )
        
        # Save frame as PNG
        if args.format in ['png', 'both']:
            frame_filename = f"{args.output_dir}/frame_{i:03d}.png"
            fig.write_image(frame_filename)
            frame_files.append(frame_filename)
    
    # Create MP4 video using ffmpeg if requested
    if args.format in ['mp4', 'both'] and frame_files:
        try:
            import ffmpeg
            print(f"Creating MP4 video at {args.output_video}...")
            
            # Create MP4 video from PNG frames using ffmpeg
            import subprocess
            
            # Construct the ffmpeg command
            cmd = [
                'ffmpeg',
                '-y',  # Overwrite output file if it exists
                '-framerate', str(args.fps),
                '-i', f"{args.output_dir}/frame_%03d.png",
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-crf', '23',  # Quality (lower is better)
                args.output_video
            ]
            
            # Execute the command
            subprocess.run(cmd, check=True)
            
            print(f"Video saved successfully to {args.output_video}")
            
        except Exception as e:
            print(f"Failed to create video: {e}")
            print("Make sure ffmpeg is installed on your system.")

if __name__ == "__main__":
    print("Starting Plotly Airline Revenue Export")
    export_visualization()
    print("Export complete!") 