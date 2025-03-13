import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import os

def create_mena_map():
    # Set the style
    sns.set_style("whitegrid")
    
    # Read world map data from shapefile
    shapefile_path = "./data/ne_110m_admin_0_countries.shp"
    if not os.path.exists(shapefile_path):
        print(f"Error: Could not find shapefile at {shapefile_path}")
        print("Please make sure you have the correct world map data file.")
        return
    
    try:
        # Read the shapefile
        world = gpd.read_file(shapefile_path)
        print("Successfully loaded world map data")
        
    except Exception as e:
        print(f"Error reading map data: {e}")
        return
    
    # Define MENA countries
    mena_countries = [
        'Algeria', 'Bahrain', 'Egypt', 'Iran', 'Iraq', 'Israel',
        'Jordan', 'Kuwait', 'Lebanon', 'Libya', 'Morocco', 'Oman',
        'Palestine', 'Qatar', 'Saudi Arabia', 'Syria', 'Tunisia',
        'United Arab Emirates', 'Yemen'
    ]
    
    # Try different possible column names for country names
    country_columns = ['ADMIN', 'NAME', 'SOVEREIGNT', 'NAME_LONG']
    mena = None
    used_column = None
    
    for column in country_columns:
        if column in world.columns:
            temp_mena = world[world[column].isin(mena_countries)]
            if not temp_mena.empty:
                mena = temp_mena
                used_column = column
                break
    
    if mena is None or mena.empty:
        print("\nError: Could not find MENA countries in the data")
        return
    
    # Create the figure and axis with a specific size
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    
    # Define colors
    world_color = '#f0f0f0'  # Light grey
    mena_color = '#66c2a5'   # Soft teal
    border_color = '#ffffff'  # White
    
    # Plot the world map
    world.plot(ax=ax, color=world_color, edgecolor=border_color, linewidth=0.5)
    
    # Plot MENA countries
    mena.plot(ax=ax, color=mena_color, edgecolor=border_color, linewidth=0.5)
    
    # Set map extent to focus on MENA region
    ax.set_xlim([-20, 65])
    ax.set_ylim([10, 45])
    
    # Remove axes
    ax.axis('off')
    
    # Save the map
    output_dir = 'output/maps'
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(f'{output_dir}/mena_map.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"\nMap saved to {output_dir}/mena_map.png")

if __name__ == "__main__":
    create_mena_map() 