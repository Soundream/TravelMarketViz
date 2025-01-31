from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import numpy as np

# Initialize the Dash app
app = Dash(__name__)

df = pd.read_excel('travel_market_summary.xlsx', sheet_name='Visualization Data')

df['Online Penetration'] = df['Online Penetration'] / 100

# Remove rows where all numeric values are 0
df = df[~((df['Online Bookings'] == 0) &
          (df['Gross Bookings'] == 0) &
          (df['Online Penetration'] == 0))]
df = df[df['Region'] == 'APAC']

df['Transformed Online Bookings'] = np.sqrt(df['Online Bookings'])

# Get sorted unique years for the slider
years_sorted = sorted(df['Year'].unique())

# Precompute global y-axis range to make it fixed
y_min = df['Transformed Online Bookings'].min() - 20000
y_max = df['Transformed Online Bookings'].max() + 60000

# Create the app layout
app.layout = html.Div([
    html.H1('APAC Travel Market Evolution',
            style={'textAlign': 'center', 'padding': '20px'}),
    dcc.Graph(id='bubble-chart', style={'height': '600px'})
])

@app.callback(
    Output('bubble-chart', 'figure'),
    Input('bubble-chart', 'id')  # Triggered when the page loads
)
def generate_animation(_):
    # Create the animation figure
    fig = px.scatter(
        df,
        x='Online Penetration',
        y='Transformed Online Bookings',
        size='Gross Bookings',
        color='Market',
        animation_frame='Year',
        hover_name='Market',
        size_max=60,
        color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFBE0B', '#FF006E']
    )

    # Style the chart
    fig.update_traces(
        marker=dict(
            opacity=0.8,
            line=dict(width=1.5, color='white')
        )
    )

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
            title='Square Root of Online Bookings Volume',
            tickprefix='$',
            tickformat=',',
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
        margin=dict(l=80, r=150, t=50, b=80)
    )
    return fig


if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
