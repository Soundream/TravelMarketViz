import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def load_and_process_data(csv_path):
    print(f"\nAttempting to load data from: {csv_path}")
    
    # Check if file exists
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found at: {csv_path}")
    
    # Define target countries
    target_countries = [
        'Algeria', 'Bahrain', 'Egypt', 'Israel', 'Jordan', 
        'Kuwait', 'Lebanon', 'Oman', 'Qatar', 'Saudi Arabia', 
        'United Arab Emirates'
    ]
    
    # Read CSV data
    df = pd.read_csv(csv_path)
    print(f"\nOriginal data shape: {df.shape}")
    print("\nColumns in CSV:", df.columns.tolist())
    
    # Print unique companies to check the exact name
    print("\nUnique companies in data:")
    print(df['company'].unique())
    
    # Print unique stores to check the exact name
    print("\nUnique stores in data:")
    print(df['store'].unique())
    
    # Case-insensitive filter for Wego and iOS
    df_wego = df[
        (df['company'].str.lower() == 'wego') & 
        (df['store'].str.lower() == 'ios') &
        (df['country'].isin(target_countries))  # Filter only target countries
    ]
    print(f"\nData after filtering for Wego iOS in target countries: {df_wego.shape}")
    
    if df_wego.empty:
        print("\nWARNING: No data found for Wego iOS in target countries. Checking data:")
        wego_data = df[
            (df['company'].str.lower() == 'wego') & 
            (df['country'].isin(target_countries))
        ]
        print(f"\nAll Wego data in target countries: {wego_data.shape}")
        if not wego_data.empty:
            print("\nStore distribution for Wego in target countries:")
            print(wego_data['store'].value_counts())
            print("\nCountry distribution for Wego:")
            print(wego_data['country'].value_counts())
    
    # Convert month to datetime for better handling
    df_wego['month'] = pd.to_datetime(df_wego['month'])
    print("\nDate range:", df_wego['month'].min(), "to", df_wego['month'].max())
    
    # Group by month, country, and region, sum downloads
    df_grouped = df_wego.groupby(['month', 'country', 'country_code', 'region'])['downloads'].sum().reset_index()
    print(f"\nFinal grouped data shape: {df_grouped.shape}")
    print("\nSample of processed data:")
    print(df_grouped.head())
    
    return df_grouped

def create_color_scale(min_val, max_val, n_steps=100):
    # Create color scale from light to dark green
    light_color = np.array([242, 250, 246])  # #f2faf6 - very light green
    dark_color = np.array([35, 154, 106])    # #239a6a - medium green
    
    colors = []
    for i in range(n_steps):
        t = i / (n_steps - 1)
        # Non-linear interpolation for better contrast
        t = np.power(t, 0.7)
        rgb = light_color * (1-t) + dark_color * t
        colors.append('#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2])))
    
    return colors

def get_color_for_value(value, min_val, max_val, color_scale):
    if pd.isna(value):
        return '#f0f0f0'  # Light grey for missing data
    
    # Use log scale for better visualization of large ranges
    if min_val <= 0:
        min_val = 1
    
    log_min = np.log1p(min_val)
    log_max = np.log1p(max_val)
    log_value = np.log1p(value)
    
    scaled = (log_value - log_min) / (log_max - log_min)
    scaled = np.power(scaled, 0.8)
    scaled = np.clip(scaled, 0, 1)
    
    color_idx = int(scaled * (len(color_scale) - 1))
    return color_scale[color_idx]

def create_downloads_map_for_month(world, month_data, color_scale, min_val, max_val, month_date):
    print(f"\n=== Month {month_date.strftime('%Y-%m')} Data ===")
    print("Downloads by country:")
    print(month_data[['country', 'downloads']].to_string())
    
    # Create figure
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    
    # Define target countries
    target_countries = [
        'Algeria', 'Bahrain', 'Egypt', 'Israel', 'Jordan', 
        'Kuwait', 'Lebanon', 'Oman', 'Qatar', 'Saudi Arabia', 
        'United Arab Emirates'
    ]
    
    # Define surrounding countries to show in grey
    surrounding_countries = [
        'Iran', 'Iraq', 'Syria', 'Yemen', 'Turkey', 'Cyprus',
        'Sudan', 'South Sudan', 'Ethiopia', 'Eritrea', 'Djibouti',
        'Somalia', 'Libya', 'Tunisia', 'Morocco', 'Greece'
    ]
    
    # Create mapping for country names that might be different in the shapefile
    country_name_mapping = {
        'United Arab Emirates': ['United Arab Emirates', 'UAE', 'U.A.E.'],
        'Saudi Arabia': ['Saudi Arabia', 'Kingdom of Saudi Arabia', 'KSA']
    }
    
    # Plot all countries in white first
    world.plot(ax=ax, color='#ffffff', edgecolor='#ffffff', linewidth=0.5)
    
    # Create a color mapping for each country
    country_colors = {}
    
    # Process each country
    for _, row in month_data.iterrows():
        country_name = row['country']
        downloads = row['downloads']
        color = get_color_for_value(downloads, min_val, max_val, color_scale)
        country_colors[country_name] = color
        # Add alternative names if they exist
        if country_name in country_name_mapping:
            for alt_name in country_name_mapping[country_name]:
                country_colors[alt_name] = color
    
    # Plot each country
    for idx, row in world.iterrows():
        country_name = row['NAME']
        if country_name in target_countries or any(country_name in alt_names for country, alt_names in country_name_mapping.items()):
            # Target countries get their download-based color or light grey if no data
            color = country_colors.get(country_name, '#f0f0f0')
        elif country_name in surrounding_countries:
            # Surrounding countries get a medium grey
            color = '#d0d0d0'
        else:
            # Other countries remain white
            color = '#ffffff'
        
        world[world['NAME'] == country_name].plot(
            ax=ax,
            color=color,
            edgecolor='#ffffff',
            linewidth=0.5
        )
    
    # Add title with month and year
    plt.title(f"Wego iOS Downloads - {month_date.strftime('%B %Y')}", 
              pad=20, fontsize=14, fontweight='bold')
    
    # Set map extent to focus on target region
    ax.set_xlim([25, 60])  # Adjusted to focus more on the Arabian Peninsula
    ax.set_ylim([15, 40])
    
    # Remove axes
    ax.axis('off')
    
    # Save the map
    output_dir = 'output/wego_downloads'
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(f'{output_dir}/wego_ios_downloads_{month_date.strftime("%Y_%m")}.png', 
                dpi=300, 
                bbox_inches='tight',
                facecolor='white', 
                edgecolor='none')
    plt.close()
    
    print(f"\nGenerated map for {month_date.strftime('%B %Y')}")
    print("\nDownloads by country:")
    for _, row in month_data.iterrows():
        print(f"- {row['country']}: {row['downloads']:,.0f} downloads")

def main():
    try:
        print("Starting script execution...")
        
        # Load world map data
        print("\nLoading world map data...")
        world = gpd.read_file("./data/ne_110m_admin_0_countries.shp")
        print(f"World map data loaded, shape: {world.shape}")
        
        # Load and process CSV data
        print("\nProcessing CSV data...")
        df_grouped = load_and_process_data("./data/csv1.csv")
        
        if df_grouped.empty:
            print("No data found after processing. Please check the filters.")
            return
        
        # Get min and max values for color scaling
        min_val = df_grouped['downloads'].min()
        max_val = df_grouped['downloads'].max()
        print(f"\nDownload range: {min_val:,.0f} to {max_val:,.0f}")
        
        # Create color scale
        color_scale = create_color_scale(min_val, max_val)
        
        # Generate a map for each month
        months = sorted(df_grouped['month'].unique())
        print(f"\nGenerating maps for {len(months)} months")
        
        for month in months:
            month_data = df_grouped[df_grouped['month'] == month]
            print(f"\nProcessing {month.strftime('%B %Y')}, data shape: {month_data.shape}")
            create_downloads_map_for_month(world, month_data, color_scale, min_val, max_val, month)
            print(f"{month.strftime('%B %Y')}: Map has been created")
        
        print("\nScript completed successfully!")
        
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        import traceback
        print("\nFull error traceback:")
        print(traceback.format_exc())

if __name__ == "__main__":
    main() 