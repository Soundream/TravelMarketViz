from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
from PIL import Image
import os

# Initialize the Dash app
app = Dash(__name__)

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
    # Create base scatter plot
    fig = px.scatter(
        df,
        x='Online Penetration',
        y='Transformed Online Bookings',
        animation_frame='Year',
        hover_name='Market',
        hover_data=['Online Penetration', 'Online Bookings', 'Gross Bookings']
    )
    
    # Make markers transparent
    fig.update_traces(marker_color="rgba(0,0,0,0)")
    
    # Get maximum dimension for scaling
    maxDim = df[['Online Penetration', 'Transformed Online Bookings']].max().idxmax()
    maxi = df[maxDim].max()
    
    # Add flag images for each data point
    for _, row in df.iterrows():
        if row['Market'] in ['Singapore', 'China']:
            image_path = f"wit/assets/{row['Market']} Flag Icon.png"
            if os.path.exists(image_path):
                fig.add_layout_image(
                    dict(
                        source=Image.open(image_path),
                        xref="x",
                        yref="y",
                        x=row['Online Penetration'],
                        y=row['Transformed Online Bookings'],
                        sizex=np.sqrt(row['Gross Bookings'] / df['Gross Bookings'].max()) * maxi * 0.2 + maxi * 0.05,
                        sizey=np.sqrt(row['Gross Bookings'] / df['Gross Bookings'].max()) * maxi * 0.2 + maxi * 0.05,
                        sizing="contain",
                        opacity=0.8,
                        layer="above",
                        xanchor="center",
                        yanchor="middle"
                    )
                )

    # Update layout
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=600,
        xaxis=dict(
            title='Online Penetration',
            tickformat=',.0%',
            range=[0, max(df['Online Penetration'].max() * 1.1, 0.6)]
        ),
        yaxis=dict(
            title='Online Bookings Volume',
            range=[0, df['Transformed Online Bookings'].max() * 1.3]
        )
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
