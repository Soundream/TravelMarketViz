#!/usr/bin/env python
import os
import argparse
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from PIL import Image
import plotly.io as pio
from tqdm import tqdm
import warnings
import base64
warnings.filterwarnings('ignore')

# Add argument parser
parser = argparse.ArgumentParser(description='Generate travel company revenue visualization using Plotly')
parser.add_argument('--output', type=str, default='output/travel_company_revenue_plotly.html', 
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

# Input CSV path (same as travelcompany viz)
input_csv = 'Animated Bubble Chart_ Historic Financials Online Travel Industry - Revenue1.csv'

# Color mapping from travelcompany visualization (from second script)
color_dict = {
    'ABNB': '#778899', 'BKNG': '#778899', 'PCLN': '#778899',
    'DESP': '#778899', 'EaseMyTrip': '#00a0e2', 'EDR': '#778899',
    'EXPE': '#778899', 'LMN': '#778899', 'MMYT': '#e74c3c',
    'Ixigo': '#e74c3c', 'OWW': '#778899', 'SEERA': '#778899',
    'TCOM': '#2577e3', 'TRIP': '#778899', 'TRVG': '#778899',
    'Webjet': '#e74c3c', 'Yatra': '#e74c3c', 'Travelocity': '#778899',
    'Orbitz': '#778899', 'LONG': '#E60010', 'TCEL': '#5B318F'
}

# Logo file mapping: ticker -> logo path
logo_mapping = {
    'ABNB': 'logos/ABNB_logo.png',
    'BKNG': 'logos/BKNG_logo.png',
    'PCLN': 'logos/PCLN_logo.png',
    'DESP': 'logos/DESP_logo.png',
    'EaseMyTrip': 'logos/EaseMyTrip_logo.png',
    'EDR': 'logos/EDR_logo.png',
    'EXPE': 'logos/EXPE_logo.png',
    'LMN': 'logos/LMN_logo.png',
    'MMYT': 'logos/MMYT_logo.png',
    'Ixigo': 'logos/Ixigo_logo.png',
    'OWW': 'logos/OWW_logo.png',
    'SEERA': 'logos/SEERA_logo.png',
    'TCOM': 'logos/TCOM_logo.png',
    'TRIP': 'logos/TRIP_logo.png',
    'TRVG': 'logos/TRVG_logo.png',
    'Webjet': 'logos/Webjet_logo.png',
    'Yatra': 'logos/Yatra_logo.png',
    'Travelocity': 'logos/Travelocity_logo.png',
    'Orbitz': 'logos/Orbitz_logo.png',
    'LONG': 'logos/Elong_logo.png',
    'TCEL': 'logos/TongCheng_logo.png'
}

def parse_quarter(quarter_str):
    """Parse quarter string into (year, quarter)"""
    year, quarter = quarter_str.split("'")
    return int(year), int(quarter[1])


def format_revenue(value):
    """Format revenue values with B for billions and M for millions"""
    if value >= 1000:
        return f'${value/1000:.1f}B'
    return f'${value:.0f}M'


def encode_logo(path):
    """Convert logo file to base64 string for HTML embedding"""
    try:
        if path and os.path.exists(path):
            with open(path, 'rb') as f:
                data = base64.b64encode(f.read()).decode()
            return f"data:image/png;base64,{data}"
    except Exception as e:
        print(f"Error encoding logo {path}: {e}")
    return None


def create_visualization():
    # Load the data from CSV
    df = pd.read_csv(input_csv)
    df.columns = df.columns.str.strip()

    # Process revenue columns
    for col in df.columns[1:]:
        df[col] = pd.to_numeric(
            df[col].str.replace(',', '').str.replace(' M', ''),
            errors='coerce'
        )

    df.set_index(df.columns[0], inplace=True)
    quarters = df.index.tolist()

    all_quarters_data = []
    for quarter in tqdm(quarters, desc="Processing data"):
        year, q = parse_quarter(quarter)
        month = q * 3
        quarter_series = df.loc[quarter].dropna()
        top_companies = quarter_series.sort_values(ascending=False).head(args.max_companies)

        tickers = top_companies.index.tolist()
        revenues = top_companies.values.tolist()
        colors = [color_dict.get(t, '#808080') for t in tickers]
        hover_texts = [f"<b>{t}</b><br>Revenue: {format_revenue(r)}" for t, r in zip(tickers, revenues)]
        logos = [encode_logo(logo_mapping.get(t)) for t in tickers]
        y_positions = list(range(len(tickers)))

        all_quarters_data.append({
            'quarter': quarter,
            'tickers': tickers,
            'revenues': revenues,
            'colors': colors,
            'hover_texts': hover_texts,
            'logos': logos,
            'y_pos': y_positions
        })

    # Initial data for first quarter
    initial = all_quarters_data[0]

    # Create figure
    fig = go.Figure()
    # Bar trace
    fig.add_trace(
        go.Bar(
            x=initial['revenues'],
            y=initial['y_pos'],
            orientation='h',
            marker=dict(color=initial['colors'][::-1]),
            hoverinfo='none',
            showlegend=False
        )
    )
    # Text overlay
    fig.add_trace(
        go.Bar(
            x=initial['revenues'][::-1],
            y=[y - 0.05 for y in initial['y_pos'][::-1]],
            orientation='h',
            marker=dict(color='rgba(0,0,0,0)'),
            text=[format_revenue(r) for r in initial['revenues'][::-1]],
            textposition='outside',
            textfont=dict(size=14, color='black'),
            hoverinfo='none',
            showlegend=False
        )
    )
    # Legend points for colors
    for ticker, color in color_dict.items():
        fig.add_trace(
            go.Scatter(
                x=[None], y=[None], mode='markers',
                marker=dict(size=20, color=color), name=ticker,
                showlegend=True
            )
        )

    # Add logo images for initial quarter
    max_rev = max([d['revenues'] for d in all_quarters_data])[0] if all_quarters_data else 0
    x_offset = max_rev * 1.05
    logo_width = max_rev * 0.2
    for i, (logo, rev) in enumerate(zip(initial['logos'], initial['revenues'])):
        if logo:
            fig.add_layout_image(
                dict(
                    source=logo,
                    xref='x', yref='y',
                    x=x_offset, y=i - 0.05,
                    sizex=logo_width, sizey=0.8,
                    xanchor='left', yanchor='middle', sizing='contain', opacity=0.95
                )
            )

    # Update layout
    fig.update_layout(
        title=dict(text='Travel Company Revenue Visualization', x=0.5, y=0.95),
        width=args.width, height=args.height,
        xaxis=dict(title='Revenue', tickformat='$,', range=[0, max_rev * 1.5]),
        yaxis=dict(
            title='Company', tickmode='array',
            tickvals=initial['y_pos'], ticktext=initial['tickers'], autorange='reversed'
        ),
        plot_bgcolor='white', paper_bgcolor='white', hovermode='closest',
        margin=dict(l=100, r=150, t=100, b=140),
        legend=dict(orientation='h', y=-0.15, x=0.5, xanchor='center')
    )

    # Convert to HTML
    html_content = pio.to_html(fig, include_plotlyjs=False, full_html=False, div_id='chart')

    # Simple HTML wrapper
    html = f"""
<!DOCTYPE html>
<html><head><title>Travel Company Revenue</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head><body>{html_content}</body></html>
"""

    with open(args.output, 'w') as f:
        f.write(html)
    print(f"Saved visualization to {args.output}")

if __name__ == '__main__':
    print('Starting Travel Company Plotly Visualization')
    create_visualization()
    print('Visualization complete!')
