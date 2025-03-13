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
    print(year_data[['Market', 'Gross Bookings(US$)', 'Online Penetration %']].to_string())
    
    # Create figure
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    
    # Plot all countries in very light grey first
    world.plot(ax=ax, color='#f9f9f9', edgecolor='#ffffff', linewidth=0.5)
    
    # Create a color mapping for each country
    country_colors = {}
    
    # Custom y-offset for Qatar
    y_offsets = {
        'Qatar': 2,  # 向上移动
        'Egypt': 0,
        'Saudi Arabia': 0,
        'U.A.E.': 0
    }
    
    # 获取该年份所有值用于颜色映射（只包括主要市场，不包括Rest of Middle East）
    year_values = []
    main_markets = ['Egypt', 'Qatar', 'Saudi Arabia', 'U.A.E.']
    for market in main_markets:
        market_data = year_data[year_data['Market'] == market]
        if not market_data.empty:
            value = market_data['Gross Bookings(US$)'].iloc[0]
            year_values.append(value)
    
    # 使用该年份的最大最小值来计算颜色
    if year_values:
        year_min = min(year_values)
        year_max = max(year_values)
    else:
        year_min = min_val
        year_max = max_val
    
    # Process main markets and store centroids for bubbles
    centroids = {}
    penetration_values = {}
    for market, countries in mena_mapping.items():
        if market in main_markets:  
            market_data = year_data[year_data['Market'] == market]
            if not market_data.empty:
                value = market_data['Gross Bookings(US$)'].iloc[0]
                penetration = market_data['Online Penetration %'].iloc[0]
                penetration_values[market] = penetration
                color = get_color_for_value(value, year_min, year_max, color_scale)
                for country in countries:
                    country_colors[country] = color
                    # Calculate centroid for the country
                    country_geom = world[world['NAME'] == country].geometry.iloc[0]
                    centroid = country_geom.centroid
                    centroids[market] = (centroid.x, centroid.y + y_offsets.get(market, 0))
    
    # Set Rest of Middle East countries to grey
    rest_countries = mena_mapping['Rest of Middle East']
    for country in rest_countries:
        country_colors[country] = '#e0e0e0'  # 使用稍深的灰色
    
    # Plot each country with its color
    for idx, row in world.iterrows():
        country_name = row['NAME']
        if country_name in country_colors:
            world[world['NAME'] == country_name].plot(
                ax=ax,
                color=country_colors[country_name],
                edgecolor='#ffffff',
                linewidth=0.5
            )
    
    # Calculate bubble sizes based on penetration rates
    min_penetration = min(penetration_values.values())
    max_penetration = max(penetration_values.values())
    min_size = 0.6
    max_size = 1.2
    
    # Add bubbles for online penetration
    for market in main_markets:
        market_data = year_data[year_data['Market'] == market]
        if not market_data.empty and market in centroids:
            penetration = market_data['Online Penetration %'].iloc[0]
            x, y = centroids[market]
            
            # Calculate bubble size based on penetration rate
            size = min_size + (penetration - min_penetration) * (max_size - min_size) / (max_penetration - min_penetration)
            
            # Draw yellow circle with black edge
            circle = plt.Circle((x, y), size, color='#FFE5B4', alpha=0.9, edgecolor='black')
            ax.add_patch(circle)
            ''''''
            #Wego is a leading travel platform in the MENA region, which stands for Middle East and North Africa. It’s been the #1 meta-search and OTA app in the region for the past three months. Here are the three main services we provide to our customer: Basically, Wego helps users find the best travel deals by comparing flights, hotels, and vacation. B2B solution for corporate clients and travel agencies, and ShopCash, a cashback platform where users can earn rewards for their online purchases. 
            # The company has a strong foothold in MENA, which is a rapidly growing market with huge travel demand, and its unique positioning gives it a competitive edge., and also 
            # wego is a leading travelcom around the world , we have 
            # also in our todays    
            # "At Wego, I work as a Business Analyst, mainly focusing on data analysis, visualization, and reporting. My work revolves around two main areas—regular reporting tasks and project-based work. and project based work work mainly include two periodic report and some project-based works.
            #as a c As a CS student, stepping into this role, and I’ve been actively exploring ways to apply my technical skills in a business and data-driven environment. This led me to focus on more technical projects, where I could leverage my expertise in data visualization and automation. while in another        
            # For reporting, I work on monthly and quarterly reports, analyzing Wego’s market share, key travel brands, and ShopCash performance. These reports are used in leadership meetings to make strategic decisions.
            ''''''
            # Add penetration rate to the bubble, plt.txt
            # i know better how to use data to i am excited to continue to building on these skills in the future
            # throughout my experience in wego and the exterprise project at nus, i 
            
            # that wraps up my presentation, to summurizae i had a fantastic learning experience at wego working on data visualization
            # That wrii had a exper inter at wego workig on both data viproject 
            # things liek a/b testing and web analys relly help us to ind what if the page looks great but does not covert, then it si still not effective, lastly, i gained experience in continuous iterationg
            plt.text(x, y, f'{penetration}%', 
                    horizontalalignment='center',
                    verticalalignment='center',
                    fontsize=10,
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
    print("\nMarket data:")
    for market in main_markets:
        market_data = year_data[year_data['Market'] == market]
        if not market_data.empty:
            value = market_data['Gross Bookings(US$)'].iloc[0]
            penetration = market_data['Online Penetration %'].iloc[0]
            print(f"- {market}: Gross Bookings: ${value:,.2f}, Online Penetration: {penetration}%")

def main():
    # Load world map datalastly, i gaine experience in continuours
    # first treinforced some importance lesson to me, things like ab testging and web anlytics helps us refine i lean ab thingsli ke ab test and we rethigaine xpoerience in continuous development, second i realized a 
    # # second, i realized that a good ui ux design is not just but this project reinforce my skills, second, i just realized th
    #lastly, i gained experience in continuous in iteration based on real-time user behavior data, making sure we were constantly improving based on insights rather than assumption.add()
    world = gpd.read_file("./data/ne_110m_admin_0_countries.shp")
    
    print("\nSearching for Bahrain in map data:")
    bahrain_matches = [name for name in world['NAME'].values if 'bahrain' in name.lower()]
    print(f"Found matches for Bahrain: {bahrain_matches}")
    # print a bs in i realized that it is never abt gret datra lesson
    # wego is leading global travel platforms, 
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
        print(year,': this year has been created')

if __name__ == "__main__":
    main() 