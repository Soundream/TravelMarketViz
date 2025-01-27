import pandas as pd
import numpy as np

files = {
    'Country Overview': 'country-gross-booking.xlsx',
    'Region Overview': 'region-gross-booking.xlsx',
    'Region Channel Split': 'region-online:offline.xlsx',
    'Country Channel Split': 'country-online:offline.xlsx',
    'Country Detailed': 'country-breakdown.xlsx',
    'Region Detailed': 'region-breakdown.xlsx'
}

writer = pd.ExcelWriter('travel_market_summary.xlsx', engine='openpyxl')

all_dfs = {}

for sheet_name, file in files.items():
    df = pd.read_excel(file)
    df.columns = [col.strip() for col in df.columns]
    all_dfs[sheet_name] = df

country_df = all_dfs['Country Detailed'].copy()

def get_channel_type(channel):
    if pd.isna(channel):
        return 'Unknown'
    channel = str(channel).lower()
    if 'central reservation' in channel:
        return 'Central Reservation'
    elif 'online supplier-direct' in channel:
        return 'Online Supplier-Direct'
    elif 'ota' in channel:
        return 'OTA'
    elif 'travel agency' in channel or 'tmc' in channel:
        return 'Travel Agency/TMC'
    elif 'offline' in channel:
        return 'Offline'
    else:
        return channel.title()

def get_online_offline(channel):
    if pd.isna(channel):
        return 'Unknown'
    channel = str(channel).lower()
    if 'offline' in channel or 'travel agency' in channel or 'tmc' in channel:
        return 'Offline'
    elif any(term in channel for term in ['online', 'ota', 'supplier-direct']):
        return 'Online'
    elif 'central' in channel:
        return 'Central'
    else:
        return 'Other'

country_to_region = {
    # APAC
    'Australia-New Zealand': 'APAC',
    'China': 'APAC',
    'Hong Kong': 'APAC',
    'India': 'APAC',
    'Indonesia': 'APAC',
    'Japan': 'APAC',
    'Macau': 'APAC',
    'Malaysia': 'APAC',
    'Singapore': 'APAC',
    'South Korea': 'APAC',
    'Taiwan': 'APAC',
    'Thailand': 'APAC',
    
    # Eastern Europe
    'Bulgaria': 'Eastern Europe',
    'Czech Republic': 'Eastern Europe',
    'Greece': 'Eastern Europe',
    'Hungary': 'Eastern Europe',
    'Poland': 'Eastern Europe',
    'Rest of Eastern Europe': 'Eastern Europe',
    'Romania': 'Eastern Europe',
    'Russia': 'Eastern Europe',
    'Ukraine': 'Eastern Europe',
    
    # Europe
    'France': 'Europe',
    'Germany': 'Europe',
    'Italy': 'Europe',
    'Rest of Europe': 'Europe',
    'Scandinavia': 'Europe',
    'Spain': 'Europe',
    'U.K.': 'Europe',
    
    # LATAM
    'Argentina': 'LATAM',
    'Brazil': 'LATAM',
    'Chile': 'LATAM',
    'Colombia': 'LATAM',
    'Mexico': 'LATAM',
    
    # Middle East
    'Egypt': 'Middle East',
    'Qatar': 'Middle East',
    'Rest of Middle East': 'Middle East',
    'Saudi Arabia': 'Middle East',
    'U.A.E.': 'Middle East',
    
    # North America
    'Canada': 'North America',
    'U.S.': 'North America'
}

country_df['Breakdown'] = country_df['Channel'].apply(get_channel_type)
country_df['Channel Type'] = country_df['Channel'].apply(get_online_offline)
country_df['Total Market Gross Bookings'] = pd.to_numeric(country_df['Total Market Gross Bookings'], errors='coerce')
country_df['Data Level'] = 'Country'

country_df = country_df[country_df['Market'].isin(country_to_region.keys())]
country_df['Region'] = country_df['Market'].map(country_to_region)
summary_df = country_df.copy()

print("Available columns:", summary_df.columns.tolist())
print("\nUnique Markets:", sorted(summary_df['Market'].unique().tolist()))

column_mapping = {
    'Interval: - Year': 'Year',
    'First ExchangeRatesV4[Currency]': "First 'ExchangeRatesV4'[Currency]"
}

for old_name, new_name in column_mapping.items():
    if old_name in summary_df.columns:
        summary_df = summary_df.rename(columns={old_name: new_name})

desired_columns = [
    'Year',
    'Data Level',
    'Region',
    'Market',
    'Channel Type',
    'Breakdown',
    'Total Market Gross Bookings',
    "First 'ExchangeRatesV4'[Currency]"
]

existing_columns = [col for col in desired_columns if col in summary_df.columns]
summary_df = summary_df[existing_columns]

sort_columns = [col for col in ['Year', 'Data Level', 'Region', 'Market', 'Channel Type', 'Breakdown'] 
                if col in summary_df.columns]
summary_df = summary_df.sort_values(sort_columns)

summary_df.to_excel(writer, sheet_name='Summary', index=False)

writer.close()

print("\nCombined Excel file has been created as 'travel_market_summary.xlsx' with summary sheet only") 