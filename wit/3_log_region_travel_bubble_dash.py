from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import numpy as np

# Initialize the Dash app
app = Dash(__name__)

# Read the visualization data
df = pd.read_excel('travel_market_summary.xlsx', sheet_name='Visualization Data')

# Convert Online Penetration to decimal format (if it's in percentage)
df['Online Penetration'] = df['Online Penetration'] / 100

# Remove rows where all numeric values are 0
df = df[~((df['Online Bookings'] == 0) & 
          (df['Gross Bookings'] == 0) & 
          (df['Online Penetration'] == 0))]

# Filter to only include APAC region
df = df[df['Region'] == 'APAC']

# Apply square root transformation to Online Bookings for moderate scaling
df['Transformed Online Bookings'] = np.sqrt(df['Online Bookings'])

# Get sorted unique years for the slider
years_sorted = sorted(df['Year'].unique())

# Precompute global y-axis range to make it fixed
y_min = df['Transformed Online Bookings'].min() - 20000
y_max = df['Transformed Online Bookings'].max() + 60000

# Create the app layout
app.layout = html.Div([
    # Title
    html.H1('APAC Travel Market Evolution', 
            style={'textAlign': 'center', 'padding': '20px'}),
    
    # Main chart
    dcc.Graph(id='bubble-chart', style={'height': '600px'}),
    
    html.Div([
        html.Div(id='year-display', style={
            'textAlign': 'center',
            'fontSize': '18px',
            'margin': '10px 0'
        }),
        
        dcc.Slider(
            id='year-slider',
            min=0,
            max=len(years_sorted)-1,
            step=1,
            value=0,
            marks=None,
            included=True,
            tooltip={"placement": "bottom", "always_visible": True}
        )
    ], style={'padding': '20px 50px 50px 50px', 'margin': '0 auto', 'maxWidth': '1200px'})
])

@app.callback(
    Output('year-display', 'children'),
    Input('year-slider', 'value')
)
def update_year_display(slider_value):
    return f'Year: {years_sorted[slider_value]}'

@app.callback(
    Output('bubble-chart', 'figure'),
    Input('year-slider', 'value')
)
def update_figure(slider_value):
    # Get data for the selected year
    selected_year = years_sorted[slider_value]
    filtered_df = df[df['Year'] == selected_year]
    
    # Remove rows where values are 0
    filtered_df = filtered_df[~((filtered_df['Online Bookings'] == 0) & 
                               (filtered_df['Gross Bookings'] == 0) & 
                               (filtered_df['Online Penetration'] == 0))]
    
    # Create the bubble chart
    fig = px.scatter(
        filtered_df,
        x='Online Penetration',
        y='Transformed Online Bookings',  # Use transformed y-axis data
        size='Gross Bookings',  # Keep original bubble size
        color='Market',
        hover_name='Market',
        size_max=60
    )
    
    # Update layout
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12),
        xaxis=dict(
            title=dict(
                text='Online Penetration (%)',
                font=dict(size=14)
            ),
            showgrid=True,
            gridwidth=1,
            gridcolor='LightGray',
            zeroline=True,
            zerolinecolor='LightGray',
            tickformat=',.0%',
            range=[0, max(df['Online Penetration'].max() * 1.1, 0.6)]
        ),
        yaxis=dict(
            title=dict(
                text='Square Root of Online Bookings ($)',
                font=dict(size=14)
            ),
            showgrid=True,
            gridwidth=1,
            gridcolor='LightGray',
            zeroline=True,
            zerolinecolor='LightGray',
            tickprefix='$',
            tickformat=',',
            range=[y_min, y_max]  # Fix y-axis range
        ),
        showlegend=True,
        legend=dict(
            title=dict(text='Country'),
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.02,
            bgcolor='rgba(255, 255, 255, 0.8)'
        ),
        margin=dict(l=80, r=150, t=50, b=80)
    )
    
    # Add annotation for bubble size explanation
    fig.add_annotation(
        text="Bubble size represents Total Market Size (Gross Bookings)",
        xref="paper", yref="paper",
        x=0, y=-0.15,
        showarrow=False,
        font=dict(size=12)
    )
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
