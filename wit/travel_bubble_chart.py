import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Read the visualization data
df = pd.read_excel('travel_market_summary.xlsx', sheet_name='Visualization Data')

# Define color scheme for regions
color_map = {
    'APAC': '#FF6B6B',           # Coral Red
    'Eastern Europe': '#4ECDC4',  # Turquoise
    'Europe': '#45B7D1',         # Ocean Blue
    'LATAM': '#96CEB4',          # Sage Green
    'Middle East': '#D4A5A5',    # Dusty Rose
    'North America': '#9B59B6'   # Purple
}

# Create the animated bubble chart
fig = px.scatter(
    df,
    x='Online Penetration',
    y='Online Bookings',
    animation_frame='Year',
    animation_group='Market',
    size='Gross Bookings',
    color='Region',
    color_discrete_map=color_map,
    hover_name='Market',
    size_max=60,
    text='Market',
    range_x=[0, df['Online Penetration'].max() * 1.1],
    range_y=[0, df['Online Bookings'].max() * 1.1]
)

# Update layout
fig.update_layout(
    title=dict(
        text='Travel Market Evolution: Online Penetration vs Online Bookings (2005-Present)',
        font=dict(size=24),
        x=0.5,
        xanchor='center',
        y=0.95
    ),
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
        zerolinecolor='LightGray'
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
        zerolinecolor='LightGray'
    ),
    showlegend=True,
    legend=dict(
        title=dict(text='Region'),
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=1.02,
        bgcolor='rgba(255, 255, 255, 0.8)'
    ),
    margin=dict(l=80, r=150, t=100, b=80)
)

# Update traces
fig.update_traces(
    textposition='top center',
    textfont=dict(size=10),
    marker=dict(
        opacity=0.8,
        line=dict(width=1, color='DarkSlateGrey')
    ),
    hovertemplate="<br>".join([
        "<b>%{hovertext}</b>",
        "Region: %{customdata[0]}",
        "Online Penetration: %{x:.1f}%",
        "Online Bookings: $%{y:,.0f}",
        "Total Market Size: $%{customdata[1]:,.0f}",
        "<extra></extra>"
    ]),
    customdata=df[['Region', 'Gross Bookings']]
)

# Customize animation
fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 1000
fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 500
fig.layout.sliders[0].currentvalue["prefix"] = "Year: "

# Format axis labels
fig.update_xaxes(ticksuffix='%')
fig.update_yaxes(tickprefix='$', tickformat=',')

# Add annotations
fig.add_annotation(
    text="Bubble size represents Total Market Size (Gross Bookings)",
    xref="paper", yref="paper",
    x=0, y=-0.15,
    showarrow=False,
    font=dict(size=12)
)

# Save the plot as HTML file
fig.write_html('travel_market_evolution.html', auto_open=True)

print("Interactive bubble chart has been created and saved as 'travel_market_evolution.html'")
print("\nVisualization features:")
print("- X-axis: Online Penetration (%)")
print("- Y-axis: Online Bookings ($)")
print("- Bubble size: Total Market Size (Gross Bookings)")
print("- Color: Regions")
print("- Animation: Year progression")
print("- Interactive elements: Hover details, Play/Pause, Timeline slider")
print("- Additional features: Grid lines, Legend, Title, Annotations") 