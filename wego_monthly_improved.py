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
    df['month_num'] = df['date'].dt.month
    df['month_name'] = df['date'].dt.strftime('%b')
    df['year_month'] = df['date'].dt.strftime('%Y-%m')
    return df

appannie_data = process_date_column(appannie_data)
similarweb_data = process_date_column(similarweb_data)

# Print earliest data months for both datasets
earliest_app_month = appannie_data['date'].min().strftime('%Y-%m')
earliest_web_month = similarweb_data['date'].min().strftime('%Y-%m')
print(f"\nEarliest app data month: {earliest_app_month}")
print(f"Earliest web data month: {earliest_web_month}")

# Get Wego data
wego_appannie_data = appannie_data[appannie_data['company'] == 'Wego'].copy()
wego_similarweb_data = similarweb_data[similarweb_data['company'] == 'Wego'].copy()

# Get all MENA data (for calculating Wego's percentage in MENA)
mena_appannie_data = appannie_data[appannie_data['region'] == 'MENA'].copy()
mena_similarweb_data = similarweb_data[similarweb_data['region'] == 'MENA'].copy()

# Function to analyze monthly app downloads
def analyze_monthly_app_downloads():
    if wego_appannie_data.empty:
        print("No AppAnnie data available for Wego analysis.")
        return
    
    # Get first and last months in data
    min_month = wego_appannie_data['date'].min().strftime('%Y-%m')
    max_month = wego_appannie_data['date'].max().strftime('%Y-%m')
    print(f"\nApp Downloads Monthly Data Range: {min_month} to {max_month}")
    
    # Sort data by date
    data = wego_appannie_data.sort_values('date')
    mena_data = mena_appannie_data.sort_values('date')
    
    # Group data by year and month
    global_monthly = data[data['country'] == 'Worldwide'].groupby(['year', 'month_num', 'year_month']).agg({
        'downloads': 'sum',
        'date': 'first'
    }).reset_index()
    
    mena_monthly = data[data['region'] == 'MENA'].groupby(['year', 'month_num', 'year_month']).agg({
        'downloads': 'sum',
        'date': 'first'
    }).reset_index()
    
    total_mena_monthly = mena_data.groupby(['year', 'month_num', 'year_month']).agg({
        'downloads': 'sum',
        'date': 'first'
    }).reset_index().rename(columns={'downloads': 'total_mena_downloads'})
    
    # Merge results
    result = pd.merge(
        global_monthly, 
        mena_monthly, 
        on=['year', 'month_num', 'year_month', 'date'], 
        suffixes=('_global', '_mena'),
        how='outer'
    )
    
    result = pd.merge(
        result, 
        total_mena_monthly, 
        on=['year', 'month_num', 'year_month', 'date'],
        how='outer'
    )
    
    # Handle NaN values
    result = result.fillna(0)
    
    # Calculate percentages
    result['mena_percentage_of_global'] = np.where(
        result['downloads_global'] > 0,
        (result['downloads_mena'] / result['downloads_global'] * 100).round(2),
        0
    )
    
    result['wego_percentage_of_mena'] = np.where(
        result['total_mena_downloads'] > 0,
        (result['downloads_mena'] / result['total_mena_downloads'] * 100).round(2),
        0
    )
    
    # Add month name for better readability
    result['month_name'] = pd.DatetimeIndex(result['date']).strftime('%b')
    
    # Sort by date
    result = result.sort_values('date')
    
    # Create a new column for year-month labels
    result['period'] = result['date'].dt.strftime('%Y-%m')
    
    # 2017数据特殊处理：汇总2017下半年数据作为全年数据
    data_2017 = result[result['year'] == 2017].copy()
    
    if not data_2017.empty:
        print("\n=== 2017 App Downloads Analysis (Using H2 2017 data as full year) ===")
        global_2017 = data_2017['downloads_global'].sum()
        mena_2017 = data_2017['downloads_mena'].sum()
        total_mena_2017 = data_2017['total_mena_downloads'].sum()
        
        pct_of_global_2017 = (mena_2017 / global_2017 * 100).round(2) if global_2017 > 0 else 0
        pct_of_mena_2017 = (mena_2017 / total_mena_2017 * 100).round(2) if total_mena_2017 > 0 else 0
        
        print(f"Global Downloads (H2 2017): {int(global_2017):,}")
        print(f"MENA Region Downloads (H2 2017): {int(mena_2017):,}")
        print(f"Total MENA Market Downloads (H2 2017): {int(total_mena_2017):,}")
        print(f"MENA as % of Global: {pct_of_global_2017}%")
        print(f"Wego's % Share of MENA Market: {pct_of_mena_2017}%")
    
    # Show first few rows
    print("\n=== First Few Months of App Download Data ===")
    first_months = result.head(5).copy()
    for _, row in first_months.iterrows():
        month = row['period']
        global_dl = int(row['downloads_global'])
        mena_dl = int(row['downloads_mena'])
        total_mena = int(row['total_mena_downloads'])
        pct_of_global = row['mena_percentage_of_global']
        pct_of_mena = row['wego_percentage_of_mena']
        
        print(f"\nMonth: {month}")
        print(f"Global Downloads: {global_dl:,}")
        print(f"MENA Region Downloads: {mena_dl:,}")
        print(f"Total MENA Market Downloads: {total_mena:,}")
        print(f"MENA as % of Global: {pct_of_global}%")
        print(f"Wego's % Share of MENA Market: {pct_of_mena}%")
    
    # Overall statistics
    total_global = result['downloads_global'].sum()
    total_mena = result['downloads_mena'].sum()
    total_all_mena = result['total_mena_downloads'].sum()
    avg_pct_of_global = (total_mena / total_global * 100).round(2) if total_global > 0 else 0
    avg_pct_of_mena = (total_mena / total_all_mena * 100).round(2) if total_all_mena > 0 else 0
    
    print("\nOverall Statistics (All Months):")
    print(f"Total Global Downloads: {int(total_global):,}")
    print(f"Total MENA Downloads: {int(total_mena):,}")
    print(f"Total MENA Market Downloads: {int(total_all_mena):,}")
    print(f"Overall MENA as % of Global: {avg_pct_of_global}%")
    print(f"Overall Wego's % Share of MENA Market: {avg_pct_of_mena}%")
    
    return result

# Function to analyze monthly web visits
def analyze_monthly_web_visits():
    if wego_similarweb_data.empty:
        print("No SimilarWeb data available for Wego analysis.")
        return
    
    # Get first and last months in data
    min_month = wego_similarweb_data['date'].min().strftime('%Y-%m')
    max_month = wego_similarweb_data['date'].max().strftime('%Y-%m')
    print(f"\nWeb Visits Monthly Data Range: {min_month} to {max_month}")
    
    # Determine visit column name
    visit_column = 'country_visits' if 'country_visits' in wego_similarweb_data.columns else 'visits'
    
    # Sort data by date
    data = wego_similarweb_data.sort_values('date')
    mena_data = mena_similarweb_data.sort_values('date')
    
    # Group data by year and month
    global_monthly = data.groupby(['year', 'month_num', 'year_month']).agg({
        visit_column: 'sum',
        'date': 'first'
    }).reset_index()
    
    mena_monthly = data[data['region'] == 'MENA'].groupby(['year', 'month_num', 'year_month']).agg({
        visit_column: 'sum',
        'date': 'first'
    }).reset_index()
    
    total_mena_monthly = mena_data.groupby(['year', 'month_num', 'year_month']).agg({
        visit_column: 'sum',
        'date': 'first'
    }).reset_index().rename(columns={visit_column: 'total_mena_visits'})
    
    # Merge results
    result = pd.merge(
        global_monthly, 
        mena_monthly, 
        on=['year', 'month_num', 'year_month', 'date'], 
        suffixes=('_global', '_mena'),
        how='outer'
    )
    
    result = pd.merge(
        result, 
        total_mena_monthly, 
        on=['year', 'month_num', 'year_month', 'date'],
        how='outer'
    )
    
    # Handle NaN values
    result = result.fillna(0)
    
    # Calculate percentages
    result['mena_percentage_of_global'] = np.where(
        result[f'{visit_column}_global'] > 0,
        (result[f'{visit_column}_mena'] / result[f'{visit_column}_global'] * 100).round(2),
        0
    )
    
    result['wego_percentage_of_mena'] = np.where(
        result['total_mena_visits'] > 0,
        (result[f'{visit_column}_mena'] / result['total_mena_visits'] * 100).round(2),
        0
    )
    
    # Add month name for better readability
    result['month_name'] = pd.DatetimeIndex(result['date']).strftime('%b')
    
    # Sort by date
    result = result.sort_values('date')
    
    # Create a new column for year-month labels
    result['period'] = result['date'].dt.strftime('%Y-%m')
    
    # 2017数据特殊处理：汇总2017下半年数据作为全年数据
    data_2017 = result[result['year'] == 2017].copy()
    
    if not data_2017.empty:
        print("\n=== 2017 Web Visits Analysis (Using H2 2017 data as full year) ===")
        global_2017 = data_2017[f'{visit_column}_global'].sum()
        mena_2017 = data_2017[f'{visit_column}_mena'].sum()
        total_mena_2017 = data_2017['total_mena_visits'].sum()
        
        pct_of_global_2017 = (mena_2017 / global_2017 * 100).round(2) if global_2017 > 0 else 0
        pct_of_mena_2017 = (mena_2017 / total_mena_2017 * 100).round(2) if total_mena_2017 > 0 else 0
        
        print(f"Global Web Visits (H2 2017): {int(global_2017):,}")
        print(f"MENA Region Web Visits (H2 2017): {int(mena_2017):,}")
        print(f"Total MENA Market Web Visits (H2 2017): {int(total_mena_2017):,}")
        print(f"MENA as % of Global: {pct_of_global_2017}%")
        print(f"Wego's % Share of MENA Market: {pct_of_mena_2017}%")
    
    # Show first few rows
    print("\n=== First Few Months of Web Visit Data ===")
    first_months = result.head(5).copy()
    for _, row in first_months.iterrows():
        month = row['period']
        global_visits = int(row[f'{visit_column}_global'])
        mena_visits = int(row[f'{visit_column}_mena'])
        total_mena = int(row['total_mena_visits'])
        pct_of_global = row['mena_percentage_of_global']
        pct_of_mena = row['wego_percentage_of_mena']
        
        print(f"\nMonth: {month}")
        print(f"Global Web Visits: {global_visits:,}")
        print(f"MENA Region Web Visits: {mena_visits:,}")
        print(f"Total MENA Market Web Visits: {total_mena:,}")
        print(f"MENA as % of Global: {pct_of_global}%")
        print(f"Wego's % Share of MENA Market: {pct_of_mena}%")
    
    # Overall statistics
    total_global = result[f'{visit_column}_global'].sum()
    total_mena = result[f'{visit_column}_mena'].sum()
    total_all_mena = result['total_mena_visits'].sum()
    avg_pct_of_global = (total_mena / total_global * 100).round(2) if total_global > 0 else 0
    avg_pct_of_mena = (total_mena / total_all_mena * 100).round(2) if total_all_mena > 0 else 0
    
    print("\nOverall Statistics (All Months):")
    print(f"Total Global Web Visits: {int(total_global):,}")
    print(f"Total MENA Web Visits: {int(total_mena):,}")
    print(f"Total MENA Market Web Visits: {int(total_all_mena):,}")
    print(f"Overall MENA as % of Global: {avg_pct_of_global}%")
    print(f"Overall Wego's % Share of MENA Market: {avg_pct_of_mena}%")
    
    return result

# Function to create monthly visualizations
def create_monthly_visualizations(app_data, web_data):
    # App Downloads Monthly Trend
    if app_data is not None:
        plt.figure(figsize=(15, 8))
        dates = app_data['date']
        
        # Plot global and MENA downloads
        plt.plot(dates, app_data['downloads_global'], marker='o', linestyle='-', label='Global Downloads')
        plt.plot(dates, app_data['downloads_mena'], marker='s', linestyle='-', label='MENA Downloads')
        
        # Set title and labels
        plt.title('Wego Monthly App Downloads Trend')
        plt.xlabel('Month')
        plt.ylabel('Downloads')
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Format x-axis to show only selected months
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('wego_monthly_app_downloads.png', dpi=300)
        print("\nMonthly app downloads visualization saved as 'wego_monthly_app_downloads.png'")
        
        # App Downloads Percentage Plot
        plt.figure(figsize=(15, 8))
        plt.plot(dates, app_data['mena_percentage_of_global'], marker='o', linestyle='-', color='green', label='MENA % of Global')
        plt.plot(dates, app_data['wego_percentage_of_mena'], marker='s', linestyle='-', color='purple', label='Wego % of MENA Market')
        plt.title('Wego App Downloads - Monthly Market Share Analysis')
        plt.xlabel('Month')
        plt.ylabel('Percentage (%)')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('wego_monthly_app_market_share.png', dpi=300)
        print("Monthly app download market share visualization saved as 'wego_monthly_app_market_share.png'")
    
    # Web Visits Monthly Trend
    if web_data is not None:
        plt.figure(figsize=(15, 8))
        dates = web_data['date']
        visit_column = 'country_visits' if 'country_visits_global' in web_data.columns else 'visits'
        
        # Plot global and MENA web visits
        plt.plot(dates, web_data[f'{visit_column}_global'], marker='o', linestyle='-', label='Global Web Visits')
        plt.plot(dates, web_data[f'{visit_column}_mena'], marker='s', linestyle='-', label='MENA Web Visits')
        
        # Set title and labels
        plt.title('Wego Monthly Web Visits Trend')
        plt.xlabel('Month')
        plt.ylabel('Web Visits')
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Format x-axis
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('wego_monthly_web_visits.png', dpi=300)
        print("Monthly web visits visualization saved as 'wego_monthly_web_visits.png'")
        
        # Web Visits Percentage Plot
        plt.figure(figsize=(15, 8))
        plt.plot(dates, web_data['mena_percentage_of_global'], marker='o', linestyle='-', color='green', label='MENA % of Global')
        plt.plot(dates, web_data['wego_percentage_of_mena'], marker='s', linestyle='-', color='purple', label='Wego % of MENA Market')
        plt.title('Wego Web Visits - Monthly Market Share Analysis')
        plt.xlabel('Month')
        plt.ylabel('Percentage (%)')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('wego_monthly_web_market_share.png', dpi=300)
        print("Monthly web visit market share visualization saved as 'wego_monthly_web_market_share.png'")

# Run the analysis
monthly_app_analysis = analyze_monthly_app_downloads()
monthly_web_analysis = analyze_monthly_web_visits()

# Save results to CSV
if monthly_app_analysis is not None:
    monthly_app_analysis.to_csv('wego_monthly_app_downloads_analysis.csv', index=False)
    print("\nMonthly app downloads analysis saved to 'wego_monthly_app_downloads_analysis.csv'")
    
if monthly_web_analysis is not None:
    monthly_web_analysis.to_csv('wego_monthly_web_visits_analysis.csv', index=False)
    print("Monthly web visits analysis saved to 'wego_monthly_web_visits_analysis.csv'")

# Create visualizations
create_monthly_visualizations(monthly_app_analysis, monthly_web_analysis)

print("\nMonthly analysis complete!") 