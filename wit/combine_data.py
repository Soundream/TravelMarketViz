import pandas as pd
import numpy as np

# Define input files
files = {
    'Country Overview': 'country-gross-booking.xlsx',
    'Region Overview': 'region-gross-booking.xlsx',
    'Region Channel Split': 'region-online:offline.xlsx',
    'Country Channel Split': 'country-online:offline.xlsx',
    'Country Detailed': 'country-breakdown.xlsx',
    'Region Detailed': 'region-breakdown.xlsx'
}

# Create Excel writer object
writer = pd.ExcelWriter('travel_market_summary.xlsx', engine='openpyxl')

# Dictionary to store dataframes for summary
all_dfs = {}

# Read each file and save to new workbook
for sheet_name, file in files.items():
    df = pd.read_excel(file)
    all_dfs[sheet_name] = df
    
    # Save to sheet in new workbook
    df.to_excel(writer, sheet_name=sheet_name, index=False)

# Create summary sheet
# Start with the most detailed country data
summary_df = all_dfs['Country Detailed'].copy()

# Standardize column names
summary_df.columns = [col.strip() for col in summary_df.columns]

# Ensure numeric values are properly formatted
summary_df['Total Market Gross Bookings'] = pd.to_numeric(summary_df['Total Market Gross Bookings'], errors='coerce')

# Standardize Channel/Breakdown classification
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

# Add standardized breakdown and channel type columns
summary_df['Breakdown'] = summary_df['Channel'].apply(get_channel_type)
summary_df['Channel Type'] = summary_df['Channel'].apply(get_online_offline)

# Reorder columns
final_columns = [
    'Year',
    'Region',
    'Market',
    'Channel Type',
    'Breakdown',
    'Total Market Gross Bookings',
    "First 'ExchangeRatesV4'[Currency]"
]

# Select and reorder columns that exist
existing_columns = [col for col in final_columns if col in summary_df.columns]
summary_df = summary_df[existing_columns]

# Write summary sheet
summary_df.to_excel(writer, sheet_name='Summary', index=False)

# Save the workbook
writer.close()

print("Combined Excel file has been created as 'travel_market_summary.xlsx'") 