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

# Get sorted unique years for the slider
years_sorted = sorted(df['Year'].unique())

# Generate a color map for unique countries (markets) in APAC
unique_countries = df['Market'].unique()
color_map = {country: px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)]
             for i, country in enumerate(unique_countries)}

# Create the app layout
app.layout = html.Div([
    # Title
    html.H1('APAC Travel Market Evolution (2005-Present)', 
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
        y='Online Bookings',
        size='Gross Bookings',
        color='Market',
        color_discrete_map=color_map,
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
                text='Online Bookings ($)',
                font=dict(size=14)
            ),
            showgrid=True,
            gridwidth=1,
            gridcolor='LightGray',
            zeroline=True,
            zerolinecolor='LightGray',
            tickprefix='$',
            tickformat=',',
            range=[0, df['Online Bookings'].max() * 1.1]
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
