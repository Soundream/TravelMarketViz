from dash import Dash, dcc, html
import plotly.express as px
import pandas as pd
import numpy as np

# Initialize the Dash app
app = Dash(__name__)

# Read the visualization data
df = pd.read_excel('travel_market_summary.xlsx', sheet_name='Visualization Data')

# Data preprocessing
df['Online Penetration'] = df['Online Penetration'] / 100

# Remove rows where all numeric values are 0
df = df[~((df['Online Bookings'] == 0) &
          (df['Gross Bookings'] == 0) &
          (df['Online Penetration'] == 0))]

# Filter to only include APAC region
df = df[df['Region'] == 'APAC']

# Create the app layout
app.layout = html.Div([
    html.H1('APAC Travel Market Evolution',
            style={'textAlign': 'center', 'padding': '20px', 'fontFamily': 'Arial'}),
    
    dcc.Graph(id='animated-bubble',
              style={'height': '800px'},
              config={'displayModeBar': True})
])

@app.callback(
    Output('animated-bubble', 'figure'),
    Input('animated-bubble', 'id')
)
def create_animated_bubble(_):
    # Create animated scatter plot
    fig = px.scatter(
        df,
        x='Online Penetration',
        y='Online Bookings',
        size='Gross Bookings',
        color='Market',
        animation_frame='Year',
        animation_group='Market',
        hover_name='Market',
        size_max=60,
        range_x=[0, df['Online Penetration'].max() * 1.1],
        range_y=[0, df['Online Bookings'].max() * 1.1],
        labels={
            'Online Penetration': 'Online Penetration',
            'Online Bookings': 'Online Bookings (USD)',
            'Gross Bookings': 'Total Market Size (USD)',
            'Market': 'Market'
        }
    )

    # Update layout for better appearance
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Arial', size=14),
        xaxis=dict(
            title=dict(text='Online Penetration', font=dict(size=16)),
            tickformat=',.0%',
            showgrid=True,
            gridwidth=1,
            gridcolor='LightGray',
            zeroline=True,
            zerolinecolor='LightGray'
        ),
        yaxis=dict(
            title=dict(text='Online Bookings', font=dict(size=16)),
            tickprefix='$',
            tickformat=',.0f',
            showgrid=True,
            gridwidth=1,
            gridcolor='LightGray',
            zeroline=True,
            zerolinecolor='LightGray'
        ),
        showlegend=True,
        legend=dict(
            title=dict(text='Market'),
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.02,
            bgcolor='rgba(255, 255, 255, 0.8)'
        ),
        margin=dict(l=80, r=150, t=50, b=80),
        # Animation settings for smooth transitions
        updatemenus=[{
            'type': 'buttons',
            'showactive': False,
            'buttons': [{
                'label': 'Play',
                'method': 'animate',
                'args': [None, {
                    'frame': {'duration': 1000, 'redraw': True},
                    'fromcurrent': True,
                    'transition': {'duration': 500, 'easing': 'cubic-in-out'}
                }]
            }, {
                'label': 'Pause',
                'method': 'animate',
                'args': [[None], {
                    'frame': {'duration': 0, 'redraw': False},
                    'mode': 'immediate',
                    'transition': {'duration': 0}
                }]
            }]
        }],
        # Add slider for manual control
        sliders=[{
            'currentvalue': {'prefix': 'Year: ', 'font': {'size': 16}},
            'pad': {'t': 50},
            'len': 0.9,
            'x': 0.1,
            'transition': {'duration': 500, 'easing': 'cubic-in-out'}
        }]
    )

    # Update traces for better appearance
    fig.update_traces(
        marker=dict(
            line=dict(width=1, color='DarkSlateGrey'),
            opacity=0.8
        ),
        hovertemplate="<br>".join([
            "<b>%{hovertext}</b>",
            "Online Penetration: %{x:.1%}",
            "Online Bookings: $%{y:,.0f}",
            "Total Market Size: %{marker.size:,.0f}",
            "<extra></extra>"
        ])
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8050) 