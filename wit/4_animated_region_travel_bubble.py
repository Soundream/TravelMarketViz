import plotly.express as px
import pandas as pd
import numpy as np
import os
import imageio

# Read and preprocess data
df = pd.read_excel('travel_market_summary.xlsx', sheet_name='Visualization Data')
df['Online Penetration'] = df['Online Penetration'] / 100
df = df[~((df['Online Bookings'] == 0) &
          (df['Gross Bookings'] == 0) &
          (df['Online Penetration'] == 0))]
df = df[df['Region'] == 'APAC']
df['Transformed Online Bookings'] = np.sqrt(df['Online Bookings'])
years_sorted = sorted(df['Year'].unique())
y_min = df['Transformed Online Bookings'].min() - 20000
y_max = df['Transformed Online Bookings'].max() + 60000

# Save the animation as a GIF
def save_gif(output_file_path):
    # Create frames for each year
    frames = []
    for year in years_sorted:
        filtered_df = df[df['Year'] == year]
        fig = px.scatter(
            filtered_df,
            x='Online Penetration',
            y='Transformed Online Bookings',
            size='Gross Bookings',
            color='Market',
            hover_name='Market',
            size_max=60,
            color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFBE0B', '#FF006E']
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
            )
        )
        # Save the current frame as an image
        image_path = f"frame_{year}.png"
        fig.write_image(image_path, format="png")
        frames.append(imageio.imread(image_path))
        os.remove(image_path)  # Clean up intermediate files

    # Save all frames as a GIF
    imageio.mimsave(output_file_path, frames, duration=1)

# Output GIF path
gif_path = "assets/bubble_animation.gif"

# Ensure 'assets' directory exists
if not os.path.exists("assets"):
    os.makedirs("assets")

# Generate and save the GIF
save_gif(gif_path)

print(f"Animation saved to {gif_path}")
