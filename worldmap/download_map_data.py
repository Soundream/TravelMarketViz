import requests
import os
from zipfile import ZipFile
from io import BytesIO

def download_map_data():
    """Download Natural Earth low resolution cultural vectors"""
    url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
    
    print("Downloading world map data...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Create data directory if it doesn't exist
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)
        
        # Extract the shapefile
        print("Extracting map data...")
        with ZipFile(BytesIO(response.content)) as zip_file:
            zip_file.extractall(data_dir)
        
        print("Map data downloaded and extracted successfully.")
        
    except requests.RequestException as e:
        print(f"Error downloading map data: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    download_map_data() 