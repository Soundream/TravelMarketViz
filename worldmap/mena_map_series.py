import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def load_and_process_data(csv_path):
    # Read CSV data
    df = pd.read_csv(csv_path)
    
    # Filter only MENA region data
    mena_markets = ['Egypt', 'Qatar', 'Saudi Arabia', 'U.A.E.', 'Rest of Middle East']
    df_mena = df[df['Market'].isin(mena_markets)]
    
    print("\nMENA Region Data Sample:")
    print("========================")
    print(df_mena.head(10))
    
    # Convert Gross Bookings to numeric, removing commas
    df['Gross Bookings(US$)'] = df['Gross Bookings(US$)'].str.replace(',', '').astype(float)
    
    # Create a mapping for MENA countries
    mena_mapping = {
        'Egypt': ['Egypt'],
        'Qatar': ['Qatar'],
        'Saudi Arabia': ['Saudi Arabia'],
        'U.A.E.': ['United Arab Emirates'],
        'Rest of Middle East': [
            'Algeria', 'Bahrain', 'Iran', 'Iraq', 'Israel',
            'Jordan', 'Kuwait', 'Lebanon', 'Libya', 'Morocco', 'Oman',
            'Palestine', 'Syria', 'Tunisia', 'Yemen'
        ]
    }
    
    return df, mena_mapping

def create_color_scale(min_val, max_val, n_steps=100):
    # Create color scale from light to dark with more contrast
    light_color = np.array([242, 250, 246])  # #f2faf6 - 非常浅的绿色
    dark_color = np.array([35, 154, 106])    # #239a6a - 适中的绿色
    
    # Create linear interpolation between colors
    colors = []
    for i in range(n_steps):
        t = i / (n_steps - 1)
        # 使用非线性插值来增加中间值的差异
        t = np.power(t, 0.7)  # 调整指数可以改变颜色分布
        rgb = light_color * (1-t) + dark_color * t
        colors.append('#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2])))
    
    return colors

def get_color_for_value(value, min_val, max_val, color_scale):
    if pd.isna(value):
        return '#f0f0f0'  # Light grey for missing data
    
    # 使用更平滑的对数缩放
    if min_val <= 0:
        min_val = 1  # Avoid log(0)
    
    # 使用自然对数并调整比例
    log_min = np.log1p(min_val)  # log1p(x) = log(1 + x)
    log_max = np.log1p(max_val)
    log_value = np.log1p(value)
    
    # 使用改进的缩放公式
    scaled = (log_value - log_min) / (log_max - log_min)
    # 应用非线性变换以增加差异
    scaled = np.power(scaled, 0.8)  # 调整指数可以改变值的分布
    scaled = np.clip(scaled, 0, 1)  # 确保值在0-1之间
    
    color_idx = int(scaled * (len(color_scale) - 1))
    return color_scale[color_idx]

def create_mena_map_for_year(world, year_data, mena_mapping, color_scale, min_val, max_val, year):
    print(f"\n=== Year {year} Data ===")
    print("Available markets in CSV:")
    print(year_data[['Market', 'Gross Bookings(US$)']].to_string())
    
    # Get Rest of Middle East value for this year
    rest_of_me_data = year_data[year_data['Market'] == 'Rest of Middle East']
    if not rest_of_me_data.empty:
        rest_of_me_value = rest_of_me_data['Gross Bookings(US$)'].iloc[0]
    else:
        rest_of_me_value = 0
    
    # Create figure
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    
    # Plot all countries in very light grey first
    world.plot(ax=ax, color='#f9f9f9', edgecolor='#ffffff', linewidth=0.5)
    
    # Create a color mapping for each country
    country_colors = {}
    
    # Get all MENA countries (both direct and from Rest of Middle East)
    all_mena_countries = set()
    for countries in mena_mapping.values():
        all_mena_countries.update(countries)
    
    # 获取该年份所有值用于颜色映射
    year_values = []
    for market, value in year_data[['Market', 'Gross Bookings(US$)']].values:
        year_values.append(value)
    
    # 使用该年份的最大最小值来计算颜色
    if year_values:
        year_min = min(year_values)
        year_max = max(year_values)
    else:
        year_min = min_val
        year_max = max_val
    
    # Process each country in the world dataset
    for idx, row in world.iterrows():
        country_name = row['NAME']
        if country_name in all_mena_countries:
            # Check if country has direct mapping
            color_assigned = False
            for market, countries in mena_mapping.items():
                if country_name in countries and market != 'Rest of Middle East':
                    market_data = year_data[year_data['Market'] == market]
                    if not market_data.empty:
                        value = market_data['Gross Bookings(US$)'].iloc[0]
                        color = get_color_for_value(value, year_min, year_max, color_scale)
                        country_colors[country_name] = color
                        color_assigned = True
                        break
            
            # If no direct mapping found, use Rest of Middle East value
            if not color_assigned:
                color = get_color_for_value(rest_of_me_value, year_min, year_max, color_scale)
                country_colors[country_name] = color
    
    # Plot each MENA country with its color
    for idx, row in world.iterrows():
        country_name = row['NAME']
        if country_name in country_colors:
            world[world['NAME'] == country_name].plot(
                ax=ax,
                color=country_colors[country_name],
                edgecolor='#ffffff',
                linewidth=0.5
            )
    
    # Add title with year
    plt.title(f'MENA Region Gross Bookings - {year}', 
              pad=20, 
              fontsize=14, 
              fontweight='bold')
    
    # Set map extent to focus on MENA region
    ax.set_xlim([-20, 65])
    ax.set_ylim([10, 45])
    
    # Remove axes
    ax.axis('off')
    
    # Save the map
    output_dir = 'output/maps'
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(f'{output_dir}/mena_map_{year}.png', 
                dpi=300, 
                bbox_inches='tight',
                facecolor='white', 
                edgecolor='none')
    plt.close()
    
    print(f"\nGenerated map for year {year}")
    print("\nColor assignments:")
    for country, color in sorted(country_colors.items()):
        market = next((m for m, c in mena_mapping.items() if country in c and m != 'Rest of Middle East'), 'Rest of Middle East')
        value = year_data[year_data['Market'] == market]['Gross Bookings(US$)'].iloc[0] if market != 'Rest of Middle East' else rest_of_me_value
        print(f"- {country}: Using {market} data ({value:,.2f})")

def main():
    # Load world map data
    world = gpd.read_file("./data/ne_110m_admin_0_countries.shp")
    
    # Print all country names containing "bahrain" (case insensitive)
    print("\nSearching for Bahrain in map data:")
    bahrain_matches = [name for name in world['NAME'].values if 'bahrain' in name.lower()]
    print(f"Found matches for Bahrain: {bahrain_matches}")
    
    # Create a mapping for MENA countries with corrected names
    mena_mapping = {
        'Egypt': ['Egypt'],
        'Qatar': ['Qatar'],
        'Saudi Arabia': ['Saudi Arabia'],
        'U.A.E.': ['United Arab Emirates'],
        'Rest of Middle East': [
            'Algeria', 'Bahrain', 'Iran', 'Iraq', 'Israel',
            'Jordan', 'Kuwait', 'Lebanon', 'Libya', 'Morocco', 'Oman',
            'Palestine', 'Syria', 'Tunisia', 'Yemen'
        ]
    }
    
    # Print all available country names in map data that might be relevant
    print("\nAll country names in map data:")
    for name in sorted(world['NAME'].values):
        print(f"- {name}")
    
    # Load and process CSV data
    df, _ = load_and_process_data("./data/worldmap.csv")
    
    # Get min and max values for color scaling
    min_val = df['Gross Bookings(US$)'].min()
    max_val = df['Gross Bookings(US$)'].max()
    
    # Create color scale
    color_scale = create_color_scale(min_val, max_val)
    
    # Generate a map for each year
    for year in sorted(df['Year'].unique()):
        year_data = df[df['Year'] == year]
        create_mena_map_for_year(world, year_data, mena_mapping, color_scale, min_val, max_val, year)

if __name__ == "__main__":
    main() 