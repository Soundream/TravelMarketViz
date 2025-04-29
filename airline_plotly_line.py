import pandas as pd
import os
import plotly.graph_objs as go
import plotly.io as pio
from tqdm import tqdm

# Load uploaded CSV
file_path = "./airline-bar-video/airlines_final.csv"
df = pd.read_csv(file_path)

# Prepare metadata and revenue data
metadata = df.iloc[:7].copy()
revenue_data = df.iloc[7:].copy()
metadata.set_index(metadata.columns[0], inplace=True)

# Clean revenue data
for col in revenue_data.columns[1:]:
    revenue_data[col] = pd.to_numeric(revenue_data[col].str.replace(',', '').str.replace(' M', ''), errors='coerce')
revenue_data.set_index(revenue_data.columns[0], inplace=True)

# Define colors by region
region_colors = {
    'North America': '#40E0D0',
    'Europe': '#4169E1',
    'Asia Pacific': '#FF4B4B',
    'Latin America': '#32CD32',
    'China': '#FF4B4B',
    'Middle East': '#DEB887',
    'Russia': '#FF4B4B',
    'Turkey': '#DEB887'
}

# Keep airlines with at least 10 quarters of data
min_quarters = 10
valid_airlines = revenue_data.notna().sum()[revenue_data.notna().sum() >= min_quarters].index.tolist()
revenue_data = revenue_data[valid_airlines]

# Prepare animation frames
quarters = revenue_data.index.tolist()
frames = []
for i in tqdm(range(len(quarters)), desc="Building frames"):
    quarter = quarters[i]
    frame_data = []
    for airline in valid_airlines:
        y = revenue_data.loc[:quarter, airline].dropna()
        x = y.index.tolist()
        y_values = y.values.tolist()
        region = metadata.loc['Region', airline] if airline in metadata.columns else 'Unknown'
        color = region_colors.get(region, '#808080')
        frame_data.append(go.Scatter(x=x, y=y_values, mode='lines+markers', name=airline,
                                     line=dict(color=color), hoverinfo='name+y'))
    frames.append(go.Frame(data=frame_data, name=quarter))

# Create initial traces
initial_quarter = quarters[0]
initial_data = []
for airline in valid_airlines:
    y = revenue_data.loc[:initial_quarter, airline].dropna()
    x = y.index.tolist()
    y_values = y.values.tolist()
    region = metadata.loc['Region', airline] if airline in metadata.columns else 'Unknown'
    color = region_colors.get(region, '#808080')
    initial_data.append(go.Scatter(x=x, y=y_values, mode='lines+markers', name=airline,
                                   line=dict(color=color), hoverinfo='name+y'))

# Build figure
fig = go.Figure(
    data=initial_data,
    layout=go.Layout(
        title='Airline Revenue Over Time',
        xaxis=dict(title='Quarter'),
        yaxis=dict(title='Revenue (Million USD)'),
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            y=1.15,
            x=1.05,
            xanchor="right",
            yanchor="top",
            buttons=[
                dict(label="Play",
                     method="animate",
                     args=[None, {"frame": {"duration": 500, "redraw": True},
                                  "fromcurrent": True, "transition": {"duration": 300}}]),
                dict(label="Pause",
                     method="animate",
                     args=[[None], {"frame": {"duration": 0, "redraw": False},
                                    "mode": "immediate",
                                    "transition": {"duration": 0}}])
            ]
        )],
        sliders=[{
            "steps": [{
                "method": "animate",
                "args": [[q], {"frame": {"duration": 300, "redraw": True},
                               "mode": "immediate",
                               "transition": {"duration": 300}}],
                "label": q
            } for q in quarters],
            "transition": {"duration": 0},
            "x": 0.1,
            "xanchor": "left",
            "y": -0.2,
            "yanchor": "top"
        }]
    ),
    frames=frames
)

# Save HTML
output_file = "output/airline_revenue_linechart.html"
pio.write_html(fig, file=output_file, auto_open=False)
output_file
