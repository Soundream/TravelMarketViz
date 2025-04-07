import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# File paths
appannie_files = [
    "random/appannie.csv",
    "random/appannie-2.csv",
    "random/appannie-3.csv",
    "random/appannie-4.csv"
]

similarweb_files = [
    "random/similarweb.csv",
    "random/similarweb-2.csv",
    "random/similarweb-3.csv",
    "random/similarweb-4.csv"
]

# Function to read and filter data
def load_data(file_path):
    if not os.path.exists(file_path):
        print(f"Warning: File {file_path} does not exist. Skipping...")
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return pd.DataFrame()

# Function to load and combine data from multiple files, handling duplicates
def load_combined_data(file_list):
    all_data = pd.DataFrame()
    
    for file in file_list:
        df = load_data(file)
        if not df.empty:
            all_data = pd.concat([all_data, df], ignore_index=True)
    
    # Check for potential duplicates by creating a composite key
    if not all_data.empty:
        # Create a composite key for identifying potential duplicates
        if 'country_code' in all_data.columns and 'store' in all_data.columns:
            # For AppAnnie data
            all_data['composite_key'] = all_data['month'] + '_' + all_data['country_code'] + '_' + all_data['store'] + '_' + all_data['company']
        elif 'country_code' in all_data.columns and 'device' in all_data.columns:
            # For SimilarWeb data
            all_data['composite_key'] = all_data['month'] + '_' + all_data['country_code'] + '_' + all_data['device'] + '_' + all_data['company']
        
        # Remove duplicates if any
        if 'composite_key' in all_data.columns:
            initial_count = len(all_data)
            all_data = all_data.drop_duplicates(subset=['composite_key'])
            final_count = len(all_data)
            
            if initial_count > final_count:
                print(f"Removed {initial_count - final_count} duplicate entries.")
                
            # Drop the composite key as it's no longer needed
            all_data = all_data.drop(columns=['composite_key'])
    
    return all_data

# Load and combine all data
print("Loading and processing AppAnnie data...")
appannie_data = load_combined_data(appannie_files)

print("Loading and processing SimilarWeb data...")
similarweb_data = load_combined_data(similarweb_files)

# Extract year from month column and add date columns
def process_date_column(df):
    df['date'] = pd.to_datetime(df['month'], format='%Y-%m')
    df['year'] = df['date'].dt.year
    df['month_name'] = df['date'].dt.strftime('%b')
    df['year_month'] = df['date'].dt.strftime('%Y-%m')
    return df

appannie_data = process_date_column(appannie_data)
similarweb_data = process_date_column(similarweb_data)

# Get Wego data
wego_appannie_data = appannie_data[appannie_data['company'] == 'Wego'].copy()
wego_similarweb_data = similarweb_data[similarweb_data['company'] == 'Wego'].copy()

# Get all MENA data (for calculating Wego's percentage in MENA)
mena_appannie_data = appannie_data[appannie_data['region'] == 'MENA'].copy()
mena_similarweb_data = similarweb_data[similarweb_data['region'] == 'MENA'].copy()

# Function to analyze app downloads
def analyze_app_downloads():
    if wego_appannie_data.empty:
        print("No AppAnnie data available for Wego analysis.")
        return
    
    # Get first and last months in data
    min_month = wego_appannie_data['date'].min().strftime('%Y-%m')
    max_month = wego_appannie_data['date'].max().strftime('%Y-%m')
    print(f"\nApp Downloads Data Range: {min_month} to {max_month}")
    
    # Global downloads by year for Wego
    global_downloads = wego_appannie_data[wego_appannie_data['country'] == 'Worldwide'].groupby('year')['downloads'].sum().reset_index()
    
    # MENA region downloads by year for Wego
    mena_downloads = wego_appannie_data[wego_appannie_data['region'] == 'MENA'].groupby('year')['downloads'].sum().reset_index()
    
    # Total MENA region downloads across all companies
    total_mena_downloads = mena_appannie_data.groupby('year')['downloads'].sum().reset_index().rename(columns={'downloads': 'total_mena_downloads'})
    
    # Merge results
    result = pd.merge(global_downloads, mena_downloads, on='year', suffixes=('_global', '_mena'))
    result = pd.merge(result, total_mena_downloads, on='year')
    
    # Calculate percentages
    result['mena_percentage_of_global'] = (result['downloads_mena'] / result['downloads_global'] * 100).round(2)
    result['wego_percentage_of_mena'] = (result['downloads_mena'] / result['total_mena_downloads'] * 100).round(2)
    
    print("\n=== Wego App Downloads Analysis ===")
    print("\nAnnual Breakdown:")
    for _, row in result.iterrows():
        year = row['year']
        global_dl = int(row['downloads_global'])
        mena_dl = int(row['downloads_mena'])
        total_mena = int(row['total_mena_downloads'])
        pct_of_global = row['mena_percentage_of_global']
        pct_of_mena = row['wego_percentage_of_mena']
        
        print(f"\nYear: {year}")
        print(f"Global Downloads: {global_dl:,}")
        print(f"MENA Region Downloads: {mena_dl:,}")
        print(f"Total MENA Market Downloads: {total_mena:,}")
        print(f"MENA as % of Global: {pct_of_global}%")
        print(f"Wego's % Share of MENA Market: {pct_of_mena}%")
    
    # Overall statistics
    total_global = result['downloads_global'].sum()
    total_mena = result['downloads_mena'].sum()
    total_all_mena = result['total_mena_downloads'].sum()
    avg_pct_of_global = (total_mena / total_global * 100).round(2)
    avg_pct_of_mena = (total_mena / total_all_mena * 100).round(2)
    
    print("\nOverall Statistics (All Years):")
    print(f"Total Global Downloads: {total_global:,}")
    print(f"Total MENA Downloads: {total_mena:,}")
    print(f"Total MENA Market Downloads: {total_all_mena:,}")
    print(f"Overall MENA as % of Global: {avg_pct_of_global}%")
    print(f"Overall Wego's % Share of MENA Market: {avg_pct_of_mena}%")
    
    return result

# Function to analyze web visits
def analyze_web_visits():
    if wego_similarweb_data.empty:
        print("No SimilarWeb data available for Wego analysis.")
        return
    
    # Get first and last months in data
    min_month = wego_similarweb_data['date'].min().strftime('%Y-%m')
    max_month = wego_similarweb_data['date'].max().strftime('%Y-%m')
    print(f"\nWeb Visits Data Range: {min_month} to {max_month}")
    
    # Determine visit column name
    visit_column = 'country_visits' if 'country_visits' in wego_similarweb_data.columns else 'visits'
    
    # Global web visits by year for Wego (sum of all countries)
    global_visits = wego_similarweb_data.groupby('year')[visit_column].sum().reset_index()
    
    # MENA region web visits by year for Wego
    mena_visits = wego_similarweb_data[wego_similarweb_data['region'] == 'MENA'].groupby('year')[visit_column].sum().reset_index()
    
    # Total MENA region web visits across all companies
    total_mena_visits = mena_similarweb_data.groupby('year')[visit_column].sum().reset_index().rename(columns={visit_column: 'total_mena_visits'})
    
    # Merge results
    result = pd.merge(global_visits, mena_visits, on='year', suffixes=('_global', '_mena'))
    result = pd.merge(result, total_mena_visits, on='year')
    
    # Calculate percentages
    result['mena_percentage_of_global'] = (result[f'{visit_column}_mena'] / result[f'{visit_column}_global'] * 100).round(2)
    result['wego_percentage_of_mena'] = (result[f'{visit_column}_mena'] / result['total_mena_visits'] * 100).round(2)
    
    print("\n=== Wego Web Visits Analysis ===")
    print("\nAnnual Breakdown:")
    for _, row in result.iterrows():
        year = row['year']
        global_visits = int(row[f'{visit_column}_global'])
        mena_visits = int(row[f'{visit_column}_mena'])
        total_mena = int(row['total_mena_visits'])
        pct_of_global = row['mena_percentage_of_global']
        pct_of_mena = row['wego_percentage_of_mena']
        
        print(f"\nYear: {year}")
        print(f"Global Web Visits: {global_visits:,}")
        print(f"MENA Region Web Visits: {mena_visits:,}")
        print(f"Total MENA Market Web Visits: {total_mena:,}")
        print(f"MENA as % of Global: {pct_of_global}%")
        print(f"Wego's % Share of MENA Market: {pct_of_mena}%")
    
    # Overall statistics
    total_global = result[f'{visit_column}_global'].sum()
    total_mena = result[f'{visit_column}_mena'].sum()
    total_all_mena = result['total_mena_visits'].sum()
    avg_pct_of_global = (total_mena / total_global * 100).round(2)
    avg_pct_of_mena = (total_mena / total_all_mena * 100).round(2)
    
    print("\nOverall Statistics (All Years):")
    print(f"Total Global Web Visits: {total_global:,}")
    print(f"Total MENA Web Visits: {total_mena:,}")
    print(f"Total MENA Market Web Visits: {total_all_mena:,}")
    print(f"Overall MENA as % of Global: {avg_pct_of_global}%")
    print(f"Overall Wego's % Share of MENA Market: {avg_pct_of_mena}%")
    
    return result

# Function to create visualizations
def create_visualizations(app_data, web_data):
    plt.figure(figsize=(16, 12))
    
    # App Downloads Plot - Wego in Global vs MENA
    plt.subplot(2, 2, 1)
    if app_data is not None:
        years = app_data['year']
        plt.bar(years, app_data['downloads_global'], label='Global')
        plt.bar(years, app_data['downloads_mena'], label='MENA')
        plt.title('Wego Annual App Downloads')
        plt.xlabel('Year')
        plt.ylabel('Downloads')
        plt.legend()
        plt.xticks(rotation=45)
        
        # Add value labels on bars
        for i, v in enumerate(app_data['downloads_global']):
            plt.text(i, v, f'{int(v):,}', ha='center', va='bottom', rotation=90, fontsize=8)
    
    # App Downloads Percentage Plot
    plt.subplot(2, 2, 2)
    if app_data is not None:
        plt.plot(years, app_data['mena_percentage_of_global'], marker='o', linestyle='-', color='green', label='MENA % of Global')
        plt.plot(years, app_data['wego_percentage_of_mena'], marker='s', linestyle='-', color='purple', label='Wego % of MENA Market')
        plt.title('Wego App Downloads - Market Share Analysis')
        plt.xlabel('Year')
        plt.ylabel('Percentage (%)')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        plt.xticks(rotation=45)
        
        # Add value labels on points
        for i, v in enumerate(app_data['mena_percentage_of_global']):
            plt.text(i, v, f'{v}%', ha='center', va='bottom')
        
        for i, v in enumerate(app_data['wego_percentage_of_mena']):
            plt.text(i, v, f'{v}%', ha='center', va='bottom')
    
    # Web Visits Plot - Wego in Global vs MENA
    plt.subplot(2, 2, 3)
    if web_data is not None:
        years = web_data['year']
        visit_column = 'country_visits' if 'country_visits_global' in web_data.columns else 'visits'
        
        plt.bar(years, web_data[f'{visit_column}_global'], label='Global')
        plt.bar(years, web_data[f'{visit_column}_mena'], label='MENA')
        plt.title('Wego Annual Web Visits')
        plt.xlabel('Year')
        plt.ylabel('Visits')
        plt.legend()
        plt.xticks(rotation=45)
        
        # Add value labels on bars
        for i, v in enumerate(web_data[f'{visit_column}_global']):
            plt.text(i, v, f'{int(v):,}', ha='center', va='bottom', rotation=90, fontsize=8)
    
    # Web Visits Percentage Plot
    plt.subplot(2, 2, 4)
    if web_data is not None:
        plt.plot(years, web_data['mena_percentage_of_global'], marker='o', linestyle='-', color='green', label='MENA % of Global')
        plt.plot(years, web_data['wego_percentage_of_mena'], marker='s', linestyle='-', color='purple', label='Wego % of MENA Market')
        plt.title('Wego Web Visits - Market Share Analysis')
        plt.xlabel('Year')
        plt.ylabel('Percentage (%)')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        plt.xticks(rotation=45)
        
        # Add value labels on points
        for i, v in enumerate(web_data['mena_percentage_of_global']):
            plt.text(i, v, f'{v}%', ha='center', va='bottom')
            
        for i, v in enumerate(web_data['wego_percentage_of_mena']):
            plt.text(i, v, f'{v}%', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('wego_improved_analysis_visualization.png', dpi=300)
    print("\nVisualization saved as 'wego_improved_analysis_visualization.png'")

# Run the analysis
app_analysis = analyze_app_downloads()
web_analysis = analyze_web_visits()

# Save results to CSV
if app_analysis is not None:
    app_analysis.to_csv('wego_app_downloads_improved_analysis.csv', index=False)
    print("\nApp downloads analysis saved to 'wego_app_downloads_improved_analysis.csv'")
    
if web_analysis is not None:
    web_analysis.to_csv('wego_web_visits_improved_analysis.csv', index=False)
    print("Web visits analysis saved to 'wego_web_visits_improved_analysis.csv'")

# Create visualizations
create_visualizations(app_analysis, web_analysis)

print("\nAnalysis complete!") 