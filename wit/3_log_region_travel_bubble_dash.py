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
    selected_year = years_sorted[slider_value]
    filtered_df = df[df['Year'] == selected_year]
    
    filtered_df = filtered_df[~((filtered_df['Online Bookings'] == 0) & 
                               (filtered_df['Gross Bookings'] == 0) & 
                               (filtered_df['Online Penetration'] == 0))]
    
    # 更鲜艳的配色方案
    color_sequence = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFBE0B', '#FF006E']
    
    # 创建主图表
    fig = px.scatter(
        filtered_df,
        x='Online Penetration',
        y='Transformed Online Bookings',
        size='Gross Bookings',
        color='Market',
        hover_name='Market',
        size_max=60,
        color_discrete_sequence=color_sequence
    )
    
    # 更新气泡样式
    fig.update_traces(
        marker=dict(
            opacity=0.8,  # 略微提高不透明度
            line=dict(width=1.5, color='white')  # 加粗白色边框
        )
    )
    
    # 添加年份水印（作为普通注释）
    fig.add_annotation(
        text=str(selected_year),
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(
            size=200,
            color='rgba(180, 180, 180, 0.3)'  # 调整颜色和透明度，使其更明显
        ),
        textangle=0,
        opacity=0.3  # 略微提高整体不透明度
    )
    
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(
            family="Arial, sans-serif",
            size=12,
            color="#444"
        ),
        xaxis=dict(
            title=dict(
                text='Online Penetration',
                font=dict(size=14)
            ),
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(200, 200, 200, 0.2)',  # 更淡的网格线
            zeroline=False,
            tickformat=',.0%',
            range=[0, max(df['Online Penetration'].max() * 1.1, 0.6)],
            showline=True,
            linewidth=1,
            linecolor='#444'
        ),
        yaxis=dict(
            title=dict(
                text='Online Bookings Volume',
                font=dict(size=14)
            ),
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(200, 200, 200, 0.2)',  # 更淡的网格线
            zeroline=False,
            tickprefix='$',
            tickformat=',',
            range=[y_min, y_max],
            showline=True,
            linewidth=1,
            linecolor='#444'
        ),
        showlegend=True,
        legend=dict(
            title=dict(text='Markets'),
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
