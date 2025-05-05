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

# Color dictionary for companies - adapted from the bar-video script
color_dict = {
    'ABNB': '#778899', 'BKNG': '#778899', 'PCLN': '#778899',
    'DESP': '#778899', 'EASEMYTRIP': '#00a0e2', 'EDR': '#778899',
    'EXPE': '#778899', 'LMN': '#778899', 'OWW': '#778899',
    'SEERA': '#778899', 'TCOM': '#2577e3', 'TRIP': '#778899',
    'TRVG': '#778899', 'WBJ': '#e74c3c', 'YTRA': '#e74c3c',
    'MMYT': '#e74c3c', 'IXIGO': '#e74c3c', "Travelocity": '#778899', 
    'Orbitz': '#778899', 'Webjet': '#e74c3c', 'Yatra': '#e74c3c',
    'Ixigo': '#e74c3c', 'EaseMyTrip': '#00a0e2',
    'LONG': '#E60010', 'TCEL': '#5B318F'
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
    'LONG': 'Elong',
    'TCEL': 'TongCheng'
}

# Reverse mapping (company name to ticker)
company_to_ticker = {
    'EaseMyTrip': 'EASEMYTRIP',
    'Ixigo': 'IXIGO',
    'Yatra': 'YTRA',
    'Webjet': 'WBJ'
}

def parse_quarter(quarter_str):
    """Parse quarter string into (year, quarter)"""
    year, quarter = quarter_str.split("'")
    year = int(year)
    quarter = int(quarter[1])
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

def process_quarterly_data(data):
    """Process the data following the same approach as the bar-video script"""
    # Remove the 'Revenue' row if present
    data = data[data.iloc[:, 0] != 'Revenue'].copy()
    data = data.reset_index(drop=True)
    
    # Convert the first column to a decimal year format
    def convert_to_decimal_year(year_quarter):
        year = float(year_quarter.split("'")[0])
        quarter = int(year_quarter.split("Q")[1])
        # Convert quarter to decimal (Q1->0.0, Q2->0.25, Q3->0.5, Q4->0.75)
        quarter_decimal = (quarter - 1) * 0.25
        return year + quarter_decimal
    
    # Extract year and quarter information
    data['Year'] = data.iloc[:, 0].apply(convert_to_decimal_year)
    
    # Convert all revenue columns to numeric
    for col in data.columns[1:-1]:
        data[col] = data[col].replace('', np.nan).replace('nan', np.nan)
        data[col] = pd.to_numeric(data[col].apply(lambda x: str(x).replace('$', '').replace(',', '') if pd.notnull(x) else np.nan), errors='coerce')
    
    # For years before 2024, keep all quarters
    pre_2024 = data[data['Year'] < 2024.0].copy()
    
    # For 2024, keep only Q1 and Q3
    year_2024 = data[(data['Year'] >= 2024.0) & (data['Year'] < 2025.0)].copy()
    year_2024 = year_2024[year_2024['Year'].isin([2024.0, 2024.5])]
    
    # Combine the data
    processed_data = pd.concat([pre_2024, year_2024])
    
    # For 2024 Q3, set the year to 2025 for interpolation
    processed_data.loc[processed_data['Year'] == 2024.5, 'Year'] = 2025.0
    
    # Drop the original year column
    processed_data = processed_data.drop(columns=[processed_data.columns[0]])
    
    return processed_data

def create_visualization():
    """Create interactive Plotly visualization for travel company revenue data"""
    # Load the data from CSV - using the same file as bar-video
    print("Loading data...")
    data = pd.read_csv('bar-video/Animated Bubble Chart_ Historic Financials Online Travel Industry - Revenue1.csv')
    print(f"Loaded {len(data)} rows of data")
    
    # Process the data
    print("\nProcessing quarterly data...")
    processed_data = process_quarterly_data(data)
    print(f"After processing: {len(processed_data)} rows")
    
    # Define the list of companies to display
    selected_companies = [
        'ABNB', 'BKNG', 'DESP', 'EaseMyTrip', 'EDR', 'EXPE', 'LMN',
        'MMYT', 'Ixigo', 'OWW', 'SEERA', 'TCOM', 'TRIP', 'TRVG', 'Webjet', 'Yatra', 
        "Travelocity", 'Orbitz', 'LONG', 'TCEL'
    ]
    
    # Prepare all quarters for visualization
    all_quarters_data = []
    
    # Get unique years from processed data
    unique_years = sorted(processed_data['Year'].unique())
    
    # Process each quarter
    for year in tqdm(unique_years, desc="Processing data"):
        quarter_str = f"{int(year)}'Q{int((year - int(year)) * 4) + 1}"
        quarter_data = processed_data[processed_data['Year'] == year].copy()
        
        if len(quarter_data) == 0:
            continue
            
        quarter_series = quarter_data.iloc[0].drop('Year')
        
        # Extract data for each company
        companies = []
        revenues = []
        colors = []
        hover_texts = []
        logos = []
        y_positions = []
        
        for company in selected_companies:
            # Apply time-based restrictions
            if company == 'Travelocity' and (year > 2002.25 or year < 2000.25):
                continue
            if company == 'DESP' and year < 2017.45:
                continue
            if company == 'BKNG' and year < 1999.17:
                continue
            if company == 'EXPE' and year < 1999.83:
                continue
            if company == 'TCOM' and year < 2003.92:
                continue
            if company == 'Orbitz' and (year < 2003.92 or (year > 2004.92 and year < 2007.55)):
                continue
            if company == 'SEERA' and year < 2012.25:
                continue
            if company == 'EDR' and year < 2014.25:
                continue
            if company == 'LMN' and (year < 2000.33 or (year >= 2003.75 and year < 2014.0)):
                continue
            if company == 'TRVG' and year < 2016.92:
                continue
            if company == 'ABNB' and year < 2020.92:
                continue
            if company == 'EASEMYTRIP' and year < 2021.17:
                continue
            if company == 'EaseMyTrip' and year < 2021.17:
                continue
            if company == 'IXIGO' and year < 2024.42:
                continue
            if company == 'Ixigo' and year < 2024.42:
                continue
            if company == 'TRIP' and year < 2011.92:
                continue
            if company == 'MMYT' and year < 2011.0:
                continue
            
            # Get revenue for this company
            if company in quarter_series.index:
                revenue = quarter_series[company]
                if pd.notna(revenue) and revenue > 0:
                    # Handle BKNG/PCLN name change
                    display_company = company
                    if company == 'BKNG' and year < 2018.08:
                        display_company = 'PCLN'
                    
                    # Get logo path and encode it
                    logo_path = get_logo_path(display_company, year)
                    encoded_logo = get_encoded_image(logo_path)
                    
                    companies.append(display_company)
                    revenues.append(revenue)
                    colors.append(color_dict.get(display_company, '#808080'))
                    logos.append(encoded_logo)
                    y_positions.append(len(companies) - 1)
                    
                    hover_text = f"<b>{ticker_to_company.get(display_company, display_company)}</b><br>"
                    hover_text += f"Revenue: {format_revenue(revenue)}"
                    hover_texts.append(hover_text)
        
        # Sort companies by revenue for this quarter
        if companies:
            # Sort by revenue (descending)
            idx = np.argsort(revenues)[::-1][:args.max_companies]
            
            sorted_companies = [companies[i] for i in idx]
            sorted_revenues = [revenues[i] for i in idx]
            sorted_colors = [colors[i] for i in idx]
            sorted_logos = [logos[i] for i in idx]
            sorted_hover_texts = [hover_texts[i] for i in idx]
            sorted_y_positions = list(range(len(sorted_companies)))
            
            # Store data for this quarter
            quarter_info = {
                'quarter': quarter_str,
                'year': year,
                'companies': sorted_companies,
                'revenues': sorted_revenues,
                'colors': sorted_colors,
                'hover_texts': sorted_hover_texts,
                'formatted_revenues': [format_revenue(rev) for rev in sorted_revenues],
                'logos': sorted_logos,
                'y_positions': sorted_y_positions
            }
            all_quarters_data.append(quarter_info)
    
    if not all_quarters_data:
        print("Error: No data available after filtering.")
        return None
    
    # Sort quarters chronologically
    all_quarters_data = sorted(all_quarters_data, key=lambda x: x['year'])
    
    # Get initial data for the first frame
    initial_data = all_quarters_data[0]
    
    # Create initial chart
    fig = go.Figure()
    
    # Add bar chart trace
    fig.add_trace(
        go.Bar(
            x=initial_data['revenues'],
            y=initial_data['y_positions'],
            orientation='h',
            marker=dict(color=initial_data['colors'],
                      line=dict(width=0, color='rgba(0,0,0,0)')),
            hovertext=initial_data['hover_texts'],
            hoverinfo='text',
            width=0.8,
            showlegend=False
        )
    )
    
    # Add text layer with formatted revenues
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
                family='Arial',
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
    
    # Add logos with consistent size and proper alignment
    max_revenue = max([max(q['revenues']) for q in all_quarters_data])
    global_x_offset = max_revenue * 1.05
    fixed_logo_width = max_revenue * 0.2
    
    for i, (company, revenue, logo) in enumerate(zip(initial_data['companies'], initial_data['revenues'], initial_data['logos'])):
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

    # Set x-axis range to accommodate logos
    x_axis_range = [0, max_revenue * 1.5]
    
    # Update layout
    fig.update_layout(
        title={
            'text': "Online Travel Companies Revenue Visualization",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'family': 'Arial', 'size': 24}
        },
        width=args.width,
        height=args.height,
        xaxis=dict(
            title={
                'text': "Revenue TTM (in Millions)",
                'font': {'family': 'Arial', 'size': 16}
            },
            tickformat="$,.0f",
            range=x_axis_range,
            showgrid=True,
            gridcolor='lightgrey',
            gridwidth=1,
            griddash='dot',
            tickfont={'family': 'Arial', 'size': 14}
        ),
        yaxis=dict(
            title={
                'text': "Company",
                'font': {'family': 'Arial', 'size': 16}
            },
            tickmode='array',
            tickvals=initial_data['y_positions'],
            ticktext=initial_data['companies'],
            tickfont={'family': 'Arial', 'size': 14},
            fixedrange=True,
            autorange='reversed'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode="closest",
        font=dict(family="Arial", size=14),
        margin=dict(l=100, r=150, t=100, b=140),
        xaxis_range=x_axis_range,
        bargap=0.15,
        bargroupgap=0.1
    )
    
    # Create a frame list for animation
    frames = []
    
    # Create frames for each period
    for i, period_data in enumerate(all_quarters_data):
        frame = go.Frame(
            data=[
                go.Bar(
                    x=period_data['revenues'],
                    y=period_data['y_positions'],
                    orientation='h',
                    marker=dict(color=period_data['colors']),
                    hovertext=period_data['hover_texts'],
                    hoverinfo='text',
                    width=0.8
                ),
                go.Bar(
                    x=period_data['revenues'],
                    y=[y - 0.05 for y in period_data['y_positions']],
                    orientation='h',
                    marker=dict(color='rgba(0,0,0,0)'),
                    text=period_data['formatted_revenues'],
                    textposition='outside',
                    textfont=dict(family='Arial', size=14, color='black'),
                    cliponaxis=False,
                    textangle=0,
                    constraintext='none',
                    hoverinfo='none',
                    width=0.8
                )
            ],
            layout=go.Layout(
                yaxis=dict(
                    tickmode='array',
                    tickvals=period_data['y_positions'],
                    ticktext=period_data['companies'],
                    autorange='reversed'
                ),
                xaxis=dict(
                    range=[0, max([max(q['revenues']) for q in all_quarters_data]) * 1.5]
                ),
                updatemenus=[dict(
                    type="buttons",
                    showactive=False,
                    buttons=[dict(
                        label="Play",
                        method="animate",
                        args=[None, dict(
                            frame=dict(duration=args.transition_duration, redraw=True),
                            fromcurrent=True,
                            mode="immediate"
                        )]
                    )]
                )]
            ),
            name=period_data['quarter']
        )
        frames.append(frame)
    
    # Add frames to figure
    fig.frames = frames
    
    # Add animation controls
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        args=[None, dict(
                            frame=dict(duration=args.transition_duration, redraw=True),
                            fromcurrent=True,
                            mode="immediate"
                        )]
                    ),
                    dict(
                        label="Pause",
                        method="animate",
                        args=[[None], dict(
                            frame=dict(duration=0, redraw=True),
                            mode="immediate",
                            transition=dict(duration=0)
                        )]
                    )
                ],
                direction="left",
                pad=dict(r=10, t=10),
                x=0.1,
                y=-0.15,
                xanchor="right",
                yanchor="bottom"
            )
        ],
        sliders=[
            dict(
                active=0,
                steps=[
                    dict(
                        method="animate",
                        args=[
                            [frame.name],
                            dict(
                                mode="immediate",
                                frame=dict(duration=args.transition_duration, redraw=True),
                                transition=dict(duration=args.transition_duration)
                            )
                        ],
                        label=frame.name
                    )
                    for frame in frames
                ],
                x=0.1,
                y=-0.1,
                len=0.9,
                xanchor="left",
                yanchor="bottom",
                currentvalue=dict(
                    font=dict(size=16),
                    prefix="Quarter: ",
                    visible=True,
                    xanchor="right"
                ),
                transition=dict(
                    duration=args.transition_duration,
                    easing="cubic-in-out"
                )
            )
        ]
    )
    
    # Save as HTML
    html_file = args.output
    pio.write_html(fig, file=html_file, auto_open=False, include_plotlyjs='cdn')
    
    print(f"Visualization saved successfully to {args.output}")
    return fig

if __name__ == "__main__":
    print("Starting Plotly Travel Company Revenue Visualization")
    fig = create_visualization()
    print("Visualization complete!") 