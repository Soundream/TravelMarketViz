from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from PIL import Image
import os

print("Current working directory:", os.getcwd())

# Create assets directory if it doesn't exist
os.makedirs('assets', exist_ok=True)

# Initialize the Dash app with correct assets folder
app = Dash(__name__, assets_folder='wit/assets')  # Point to wit/assets folder

df = pd.read_excel('travel_market_summary.xlsx', sheet_name='Visualization Data')

df['Online Penetration'] = df['Online Penetration'] / 100

# Remove rows where all numeric values are 0
df = df[~((df['Online Bookings'] == 0) &
          (df['Gross Bookings'] == 0) &
          (df['Online Penetration'] == 0))]
df = df[df['Region'] == 'APAC']

# Print unique markets for debugging
print("Markets in the data:", df['Market'].unique())

df['Transformed Online Bookings'] = np.sqrt(df['Online Bookings'])

# Get sorted unique years for the slider
years_sorted = sorted(df['Year'].unique())

# Precompute global y-axis range to make it fixed
y_min = 0  # Start from 0 for better visualization
y_max = df['Transformed Online Bookings'].max() * 1.3  # Increase padding to 30%

# Create non-linear tick positions based on square root transformation
actual_values = [0, 10e9, 40e9, 90e9, 160e9, 250e9, 350e9]
tick_positions = [np.sqrt(val) for val in actual_values]
tick_labels = ['0', '10B', '40B', '90B', '160B', '250B', '350B']

# Flag image paths in wit/assets folder
flag_paths = {
    'Singapore': 'Singapore Flag Icon.png',  # Simplified path
    'China': 'China Flag Icon.png'  # Simplified path
}

# Create the app layout
app.layout = html.Div([
    html.H1('APAC Travel Market Evolution',
            style={'textAlign': 'center', 'padding': '20px'}),
    dcc.Graph(id='bubble-chart', style={'height': '600px'})
])

@app.callback(
    Output('bubble-chart', 'figure'),
    Input('bubble-chart', 'id')
)
def generate_animation(_):
    # Create base scatter plot with invisible markers
    fig = px.scatter(
        df,
        x='Online Penetration',
        y='Transformed Online Bookings',
        size='Gross Bookings',
        color='Market',
        animation_frame='Year',
        hover_name='Market',
        size_max=60,
    )
    
    # Make the original markers transparent
    fig.update_traces(marker=dict(opacity=0))
    
    # Get the maximum dimension for scaling
    maxDim = df[['Online Penetration', 'Transformed Online Bookings']].max().max()
    
    # Add flag images for each data point
    for year in df['Year'].unique():
        year_data = df[df['Year'] == year]
        for _, row in year_data.iterrows():
            if row['Market'] in flag_paths:
                # Calculate size based on Gross Bookings
                size_factor = np.sqrt(row['Gross Bookings'] / df['Gross Bookings'].max()) * maxDim * 0.2 + maxDim * 0.05
                
                try:
                    image_path = os.path.join('wit/assets', flag_paths[row['Market']])
                    print(f"Trying to load image from: {image_path}")
                    
                    # Check if file exists
                    if not os.path.exists(image_path):
                        print(f"Image file does not exist: {image_path}")
                        continue
                        
                    # Read the image file
                    with Image.open(image_path) as img:
                        # Convert PIL image to base64 string
                        import base64
                        from io import BytesIO
                        
                        # Keep RGBA format to preserve transparency
                        buffered = BytesIO()
                        img.save(buffered, format="PNG")
                        img_str = base64.b64encode(buffered.getvalue()).decode()
                        
                        print(f"Successfully loaded image for {row['Market']} at position ({row['Online Penetration']}, {row['Transformed Online Bookings']})")
                        
                        # Add image for the current frame
                        fig.add_layout_image(
                            dict(
                                source=f'data:image/png;base64,{img_str}',
                                xref="x",
                                yref="y",
                                x=row['Online Penetration'],
                                y=row['Transformed Online Bookings'],
                                sizex=size_factor,
                                sizey=size_factor,
                                xanchor="center",
                                yanchor="middle",
                                sizing="contain",
                                opacity=1,
                                layer="above",
                                visible=True,
                                name=f"flag_{row['Market']}_{year}",
                                **{f"visible{year}": True}
                            )
                        )
                except Exception as e:
                    print(f"Error loading image for {row['Market']}: {str(e)}")
                    import traceback
                    traceback.print_exc()

    # Update layout with animation settings
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12, color="#444"),
        xaxis=dict(
            title='Online Penetration',
            tickformat=',.0%',
            range=[0, max(df['Online Penetration'].max() * 1.1, 0.6)],
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(200, 200, 200, 0.2)',
            showline=True,
            linewidth=1,
            linecolor='#444'
        ),
        yaxis=dict(
            title='Online Bookings Volume',
            tickvals=tick_positions,
            ticktext=tick_labels,
            range=[y_min, y_max],
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(200, 200, 200, 0.2)',
            showline=True,
            linewidth=1,
            linecolor='#444'
        ),
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.02,
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='#444',
            borderwidth=1
        ),
        margin=dict(l=80, r=150, t=50, b=80),
        # Add animation settings
        updatemenus=[{
            'buttons': [
                {
                    'args': [None, {
                        'frame': {'duration': 1000, 'redraw': True},
                        'fromcurrent': True,
                        'transition': {'duration': 0}
                    }],
                    'label': 'Play',
                    'method': 'animate'
                },
                {
                    'args': [[None], {
                        'frame': {'duration': 0, 'redraw': False},
                        'mode': 'immediate',
                        'transition': {'duration': 0}
                    }],
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
        # Add slider
        sliders=[{
            'active': 0,
            'yanchor': 'top',
            'xanchor': 'left',
            'currentvalue': {
                'font': {'size': 20},
                'prefix': 'Year:',
                'visible': True,
                'xanchor': 'right'
            },
            'transition': {'duration': 300, 'easing': 'cubic-in-out'},
            'pad': {'b': 10, 't': 50},
            'len': 0.9,
            'x': 0.1,
            'y': 0,
            'steps': [
                {
                    'args': [[str(year)], {
                        'frame': {'duration': 300, 'redraw': True},
                        'mode': 'immediate',
                        'transition': {'duration': 300}
                    }],
                    'label': str(year),
                    'method': 'animate'
                } for year in years_sorted
            ]
        }]
    )

    # Create frames for animation
    frames = []
    for year in years_sorted:
        frame = go.Frame(
            name=str(year),
            data=[go.Scatter(
                x=year_data['Online Penetration'],
                y=year_data['Transformed Online Bookings'],
                mode='markers',
                marker=dict(opacity=0),
                showlegend=False
            ) for year_data in [df[df['Year'] == year]]]
        )
        frames.append(frame)
    
    fig.frames = frames

    return fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
