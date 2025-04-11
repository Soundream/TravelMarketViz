import plotly.graph_objects as go
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import os
import argparse
from PIL import Image
import base64
from io import BytesIO
import time
from tqdm import tqdm
import multiprocessing as mp
from functools import partial
import plotly.io as pio

# Add argument parser
parser = argparse.ArgumentParser(description='Generate bar chart race visualization using Plotly')
parser.add_argument('--publish', action='store_true', help='Generate high quality version for publishing')
parser.add_argument('--quarters-only', action='store_true', help='Only generate frames for each quarter (only works with --publish)')
parser.add_argument('--frames-per-year', type=int, help='Number of frames to generate per year in publish mode (default: 192)')
parser.add_argument('--output-html', action='store_true', help='Generate interactive HTML output')
args = parser.parse_args()

# Set quality parameters based on mode
if args.publish:
    if args.quarters_only:
        FRAMES_PER_YEAR = 4
    else:
        FRAMES_PER_YEAR = args.frames_per_year if args.frames_per_year else 192
    FIGURE_WIDTH = 1920
    FIGURE_HEIGHT = 1080
else:
    if args.quarters_only:
        print("\n警告: --quarters-only 参数只在 --publish 模式下生效")
    if args.frames_per_year:
        print("\n警告: --frames-per-year 参数只在 --publish 模式下生效")
    FRAMES_PER_YEAR = 48
    FIGURE_WIDTH = 1600
    FIGURE_HEIGHT = 900

# Create required directories
logos_dir = 'logos'
output_dir = 'output'
frames_dir = os.path.join(output_dir, 'frames')
for directory in [logos_dir, output_dir, frames_dir]:
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

# Company-specific settings for logos
logo_settings = {
    'Orbitz': {'zoom': 0.30, 'offset': 130},
    'Orbitz1': {'zoom': 0.16, 'offset': 150},
    "Travelocity": {'zoom': 0.20, 'offset': 150},
    'ABNB': {'zoom': 0.25, 'offset': 150},
    'BKNG': {'zoom': 0.25, 'offset': 130},
    'PCLN_pre2014': {'zoom': 0.25, 'offset': 135},
    'PCLN_post2014': {'zoom': 0.25, 'offset': 135},
    'DESP': {'zoom': 0.28, 'offset': 120},
    'EASEMYTRIP': {'zoom': 0.34, 'offset': 100},
    'EDR': {'zoom': 0.25, 'offset': 130},
    'EXPE': {'zoom': 0.3, 'offset': 175},
    'EXPE_pre2010': {'zoom': 0.18, 'offset': 175},
    'EXPE_2010_2012': {'zoom': 0.3, 'offset': 175},
    'LMN': {'zoom': 0.45, 'offset': 140},
    'OWW': {'zoom': 0.29, 'offset': 50},
    'SEERA': {'zoom': 0.20, 'offset': 125},
    'SEERA_pre2019': {'zoom': 0.25, 'offset': 125},
    'TCOM': {'zoom': 0.30, 'offset': 130},
    'TCOM_pre2019': {'zoom': 0.25, 'offset': 130},
    'TRIP': {'zoom': 0.26, 'offset': 130},
    'TRIP_pre2020': {'zoom': 0.23, 'offset': 125},
    'TRVG': {'zoom': 0.27, 'offset': 130},
    'TRVG_pre2013': {'zoom': 0.31, 'offset': 130},
    'TRVG_2013_2023': {'zoom': 0.31, 'offset': 130},
    'WEB': {'zoom': 0.14, 'offset': 150},
    'Webjet': {'zoom': 0.23, 'offset': 125},
    'WBJ': {'zoom': 0.14, 'offset': 150},
    'Yatra': {'zoom': 0.23, 'offset': 100},
    'YTRA': {'zoom': 0.23, 'offset': 100},
    'MMYT': {'zoom': 0.25, 'offset': 130},
    'IXIGO': {'zoom': 0.26, 'offset': 120},
    'Ixigo': {'zoom': 0.26, 'offset': 120},
    'LMN_2014_2015': {'zoom': 0.27, 'offset': 130},
    'EaseMyTrip': {'zoom': 0.26, 'offset': 120},
    'LONG': {'zoom': 0.25, 'offset': 120},
    'TCEL': {'zoom': 0.35, 'offset': 120},
}

# Color dictionary for companies
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

# Define company name to ticker mapping and its reverse mapping
company_to_ticker = {
    'EaseMyTrip': 'EASEMYTRIP',
    'Ixigo': 'IXIGO',
    'Yatra': 'YTRA',
    'Webjet': 'WBJ'
}
ticker_to_company = {v: k for k, v in company_to_ticker.items()}

# Define the list of companies to display
selected_companies = [
    'ABNB', 'BKNG', 'DESP', 'EaseMyTrip', 'EDR', 'EXPE', 'LMN',
    'MMYT', 'Ixigo', 'OWW', 'SEERA', 'TCOM', 'TRIP', 'TRVG', 'Webjet',
    'Yatra', "Travelocity", 'Orbitz', 'LONG', 'TCEL'
]

def process_quarterly_data(data):
    """Process the quarterly data from CSV."""
    print("\nProcessing quarterly data...")
    
    # Remove the 'Revenue' row and reset index
    data = data[data.iloc[:, 0] != 'Revenue'].copy()
    data = data.reset_index(drop=True)
    
    # Convert the first column to proper format for processing
    def convert_to_decimal_year(year_quarter):
        year = float(year_quarter.split("'")[0])
        quarter = int(year_quarter.split("Q")[1])
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
    
    # For 2024, keep Q1 and Q3
    year_2024 = data[(data['Year'] >= 2024.0) & (data['Year'] < 2025.0)].copy()
    year_2024 = year_2024[year_2024['Year'].isin([2024.0, 2024.5])]
    
    # Combine the data
    processed_data = pd.concat([pre_2024, year_2024])
    
    # For 2024 Q3, set the year to 2025 for interpolation
    processed_data.loc[processed_data['Year'] == 2024.5, 'Year'] = 2025.0
    
    # Drop the original year column
    processed_data = processed_data.drop(columns=[processed_data.columns[0]])
    
    return processed_data

def interpolate_data(data, multiple=20):
    """Interpolate the data for smoother animation."""
    all_interpolated = []
    companies = [col for col in data.columns if col != 'Year']
    
    # Determine the overall time range
    min_year = data['Year'].min()
    max_year = data['Year'].max()
    
    # Create unified time points
    if args.publish and args.quarters_only:
        quarters_before_2024 = np.arange(min_year, 2024.0, 0.25)
        quarters_2024_2025 = np.array([2024.0, 2024.25, 2024.5, 2024.75, 2025.0])
        unified_years = np.concatenate([quarters_before_2024, quarters_2024_2025])
    else:
        sub_quarters_per_quarter = 12
        quarters_before_2024 = np.arange(min_year, 2024.0, 0.25)
        quarters_2024_2025 = np.array([2024.0, 2024.25, 2024.5, 2024.75, 2025.0])
        quarters = np.concatenate([quarters_before_2024, quarters_2024_2025])
        
        unified_years = []
        for i in range(len(quarters)-1):
            segment = np.linspace(quarters[i], quarters[i+1], sub_quarters_per_quarter * multiple, endpoint=False)
            unified_years.extend(segment)
        unified_years.append(quarters[-1])
        unified_years = np.array(unified_years)
    
    for company in companies:
        try:
            company_data = data[['Year', company]].copy()
            company_data.columns = ['Year', 'Revenue']
            company_data = company_data.dropna()
            
            if len(company_data) < 2:
                continue
            
            # Sort data by year
            company_data = company_data.sort_values('Year')
            
            # Add small variations for same values
            processed_data = company_data.copy()
            prev_value = None
            same_value_count = 0
            
            for idx, row in processed_data.iterrows():
                current_value = row['Revenue']
                if prev_value is not None and abs(current_value - prev_value) < 0.01:
                    same_value_count += 1
                    variation = current_value * 0.001 * np.sin(same_value_count * np.pi / 2)
                    processed_data.loc[idx, 'Revenue'] = current_value + variation
                else:
                    same_value_count = 0
                prev_value = current_value
            
            # Use cubic spline interpolation
            from scipy.interpolate import CubicSpline
            cs = CubicSpline(processed_data['Year'], processed_data['Revenue'], bc_type='natural')
            
            company_min_year = company_data['Year'].min()
            company_max_year = company_data['Year'].max()
            mask = (unified_years >= company_min_year) & (unified_years <= company_max_year)
            company_years = unified_years[mask]
            
            company_interp = pd.DataFrame()
            company_interp['Year'] = company_years
            company_interp['Company'] = company
            
            interpolated_values = cs(company_years)
            
            # Add small variations
            for i in range(len(interpolated_values)):
                year = company_years[i]
                base_value = interpolated_values[i]
                wave = np.sin(year * 2 * np.pi) * base_value * 0.001
                interpolated_values[i] = base_value + wave
            
            company_interp['Revenue'] = interpolated_values
            
            # Handle quarters-only mode
            if args.publish and args.quarters_only:
                for _, row in company_data.iterrows():
                    year = row['Year']
                    revenue = row['Revenue']
                    mask = np.abs(company_years - year) < 1e-10
                    if any(mask):
                        variation = revenue * 0.0005 * np.sin(year * np.pi)
                        company_interp.loc[mask, 'Revenue'] = revenue + variation
            
            all_interpolated.append(company_interp)
            
        except Exception as e:
            print(f"Error interpolating {company}: {e}")
            continue

    if not all_interpolated:
        raise ValueError("No data could be interpolated. Please check your input data.")
    
    result = pd.concat(all_interpolated, ignore_index=True)
    result = result.sort_values(['Company', 'Year']).reset_index(drop=True)
    
    return result

def encode_image(image_path):
    """Encode image to base64 string."""
    try:
        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
        return f"data:image/png;base64,{encoded}"
    except Exception as e:
        print(f"Error encoding image {image_path}: {e}")
        return None

def load_company_logos():
    """Load and encode company logos with historical versions."""
    logos = {}
    for company in selected_companies:
        if company == 'BKNG':
            # Handle BKNG/PCLN logos
            pcln_logo_path = os.path.join(logos_dir, 'PCLN_logo.png')
            pcln_logo_path_2014 = os.path.join(logos_dir, '1PCLN_logo.png')
            bkng_logo_path = os.path.join(logos_dir, 'BKNG_logo.png')
            
            if os.path.exists(pcln_logo_path):
                logos['PCLN_pre2014'] = encode_image(pcln_logo_path)
            if os.path.exists(pcln_logo_path_2014):
                logos['PCLN_post2014'] = encode_image(pcln_logo_path_2014)
            if os.path.exists(bkng_logo_path):
                logos['BKNG'] = encode_image(bkng_logo_path)
        elif company == 'TRVG':
            # Handle Trivago logos
            for version, filename in [
                ('TRVG_pre2013', 'Trivago1.jpg'),
                ('TRVG_2013_2023', 'Trivago2.jpg'),
                ('TRVG', 'TRVG_logo.png')
            ]:
                path = os.path.join(logos_dir, filename)
                if os.path.exists(path):
                    logos[version] = encode_image(path)
        else:
            # Handle regular company logos
            logo_path = os.path.join(logos_dir, f'{company}_logo.png')
            if os.path.exists(logo_path):
                logos[company] = encode_image(logo_path)
    return logos

def get_logo_key(company, year):
    """Get the appropriate logo key based on company and year."""
    if company == 'BKNG':
        if year < 2014.25:
            return 'PCLN_pre2014'
        elif year < 2018.08:
            return 'PCLN_post2014'
        return 'BKNG'
    elif company == 'TRVG':
        if year < 2013.0:
            return 'TRVG_pre2013'
        elif year < 2023.0:
            return 'TRVG_2013_2023'
        return 'TRVG'
    return company

def create_frame(frame_data, logos, frame_number, year):
    """Create a single frame of the bar chart race."""
    # Sort data by revenue
    frame_data = frame_data.sort_values('Revenue', ascending=True)
    
    # Create figure with secondary y-axis
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.1, 0.9],
        vertical_spacing=0.02,
        subplot_titles=('', '')
    )

    # Add bars
    bar_trace = go.Bar(
        x=frame_data['Revenue'],
        y=frame_data['Company'],
        orientation='h',
        marker_color=[color_dict.get(company, '#808080') for company in frame_data['Company']],
        text=frame_data['Revenue'].apply(lambda x: f'{int(x):,}' if x >= 1 else f'{x:.2f}'),
        textposition='outside',
        textfont=dict(size=14, family='Arial'),
        hoverinfo='none',
        showlegend=False
    )
    fig.add_trace(bar_trace, row=2, col=1)

    # Add logos as images
    for idx, (company, revenue) in enumerate(zip(frame_data['Company'], frame_data['Revenue'])):
        logo_key = get_logo_key(company, year)
        if logo_key in logos and logos[logo_key]:
            settings = logo_settings.get(logo_key, {'zoom': 0.25, 'offset': 120})
            
            # Calculate logo position
            y_pos = idx
            x_pos = revenue + (revenue * 0.05)  # Position logo after the bar and value
            
            # Add logo as image
            fig.add_layout_image(
                dict(
                    source=logos[logo_key],
                    xref="x2",
                    yref="y2",
                    x=x_pos,
                    y=y_pos,
                    sizex=settings['zoom'] * 100,
                    sizey=settings['zoom'] * 100,
                    xanchor="left",
                    yanchor="middle",
                    layer="above"
                )
            )

    # Add timeline marker
    timeline_trace = go.Scatter(
        x=[year],
        y=[0],
        mode='markers',
        marker=dict(
            symbol='triangle-down',
            size=15,
            color='#4e843d'
        ),
        hoverinfo='none',
        showlegend=False
    )
    fig.add_trace(timeline_trace, row=1, col=1)

    # Update layout
    fig.update_layout(
        width=FIGURE_WIDTH,
        height=FIGURE_HEIGHT,
        showlegend=False,
        margin=dict(l=200, r=200, t=50, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        bargap=0.15,
        xaxis2=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128, 128, 128, 0.2)',
            title=dict(
                text='Revenue TTM (in Millions)',
                font=dict(size=16, family='Arial')
            ),
            zeroline=False,
            side='bottom'
        ),
        yaxis2=dict(
            showgrid=False,
            zeroline=False,
            tickfont=dict(family='Arial', size=12),
            autorange='reversed'  # 确保公司名称从上到下排序
        ),
        xaxis=dict(
            range=[1996.5, 2025.5],
            showgrid=False,
            zeroline=False,
            tickmode='array',
            ticktext=[str(y) for y in range(1997, 2025, 2)],
            tickvals=list(range(1997, 2025, 2)),
            tickfont=dict(family='Arial', size=12)
        ),
        yaxis=dict(
            range=[-0.2, 0.2],
            showgrid=False,
            zeroline=True,
            zerolinewidth=1.5,
            zerolinecolor='#808080',
            showticklabels=False
        )
    )

    # 确保水平方向的条形图布局
    fig.update_yaxes(autorange="reversed", row=2, col=1)
    fig.update_xaxes(range=[0, frame_data['Revenue'].max() * 1.2], row=2, col=1)

    if args.output_html:
        # For web display, return the figure object
        return fig
    else:
        # For image output, save the frame
        frame_path = os.path.join(frames_dir, f'frame_{frame_number:04d}.png')
        fig.write_image(frame_path)
        return frame_path

def main():
    """Main function to generate the bar chart race visualization."""
    print("Loading data...")
    data = pd.read_csv('Animated Bubble Chart_ Historic Financials Online Travel Industry - Revenue1.csv')
    
    print("Processing data...")
    processed_data = process_quarterly_data(data)
    
    print("Interpolating data...")
    interp_data = interpolate_data(processed_data, multiple=FRAMES_PER_YEAR)
    
    print("Loading logos...")
    logos = load_company_logos()
    
    if args.output_html:
        print("\nGenerating interactive HTML visualization...")
        # Create frames for animation
        frames = []
        for year in tqdm(np.unique(interp_data['Year']), desc="Creating frames"):
            frame_data = interp_data[
                (interp_data['Year'] >= year - 0.01) & 
                (interp_data['Year'] <= year + 0.01)
            ].copy()
            
            if len(frame_data) == 0:
                continue
                
            frame_number = int((year - 1999) * FRAMES_PER_YEAR)
            fig = create_frame(frame_data, logos, frame_number, year)
            frames.append(go.Frame(data=fig.data, layout=fig.layout, name=f"frame_{frame_number}"))
        
        # Create the final figure with animation
        fig = frames[0]
        fig.frames = frames
        
        # Add animation settings
        fig.update_layout(
            updatemenus=[{
                'buttons': [
                    {
                        'args': [None, {'frame': {'duration': 50, 'redraw': True},
                                      'fromcurrent': True}],
                        'label': 'Play',
                        'method': 'animate'
                    },
                    {
                        'args': [[None], {'frame': {'duration': 0, 'redraw': True},
                                        'mode': 'immediate',
                                        'transition': {'duration': 0}}],
                        'label': 'Pause',
                        'method': 'animate'
                    }
                ],
                'direction': 'left',
                'pad': {'r': 10, 't': 87},
                'showactive': False,
                'type': 'buttons',
                'x': 0.1,
                'xanchor': 'right',
                'y': 0,
                'yanchor': 'top'
            }],
            sliders=[{
                'currentvalue': {
                    'font': {'size': 12},
                    'prefix': 'Year: ',
                    'visible': True,
                    'xanchor': 'right'
                },
                'pad': {'b': 10, 't': 50},
                'len': 0.9,
                'x': 0.1,
                'y': 0,
                'steps': [
                    {
                        'args': [[f.name], {
                            'frame': {'duration': 50, 'redraw': True},
                            'mode': 'immediate',
                            'transition': {'duration': 0}
                        }],
                        'label': f"{1999 + int(f.name.split('_')[1])/FRAMES_PER_YEAR:.1f}",
                        'method': 'animate'
                    } for f in frames
                ]
            }]
        )
        
        # Save as HTML
        output_path = os.path.join(output_dir, 'bar_race.html')
        fig.write_html(output_path, auto_play=False)
        print(f"\nInteractive visualization saved to: {output_path}")
    else:
        print("\nGenerating static frames...")
        with tqdm(total=len(np.unique(interp_data['Year'])), desc="Rendering frames") as pbar:
            for year in np.unique(interp_data['Year']):
                if args.publish and args.quarters_only:
                    decimal_part = year - int(year)
                    if not any(abs(decimal_part - q) < 0.01 for q in [0.0, 0.25, 0.5, 0.75]):
                        continue
                
                frame_data = interp_data[
                    (interp_data['Year'] >= year - 0.01) & 
                    (interp_data['Year'] <= year + 0.01)
                ].copy()
                
                if len(frame_data) == 0:
                    continue
                
                frame_number = int((year - 1999) * FRAMES_PER_YEAR)
                create_frame(frame_data, logos, frame_number, year)
                pbar.update(1)

if __name__ == '__main__':
    main() 