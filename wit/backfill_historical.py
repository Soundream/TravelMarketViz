import pandas as pd
import numpy as np
from openpyxl import load_workbook
import os

df = pd.read_excel('travel_market_summary.xlsx')

df['Year'] = pd.to_numeric(df['Year'])

df = df.sort_values(['Market', 'Channel Type', 'Breakdown', 'Year'])

def calculate_growth_rate(start_value, end_value, years_between):
    if start_value <= 0 or end_value <= 0:
        return 0
    return (end_value / start_value) ** (1 / years_between) - 1

def backfill_data(group):
    if len(group) < 2: 
        return group
    
    earliest_years = group.nsmallest(2, 'Year')
    if len(earliest_years) < 2:
        return group
    
    start_value = earliest_years.iloc[0]['Total Market Gross Bookings']
    end_value = earliest_years.iloc[1]['Total Market Gross Bookings']
    years_between = earliest_years.iloc[1]['Year'] - earliest_years.iloc[0]['Year']
    
    growth_rate = calculate_growth_rate(start_value, end_value, years_between)
    
    new_rows = []
    earliest_year = earliest_years.iloc[0]['Year']
    earliest_value = earliest_years.iloc[0]['Total Market Gross Bookings']
    
    for year in range(2005, int(earliest_year)):
        years_projection = earliest_year - year
        new_value = earliest_value / ((1 + growth_rate) ** years_projection)
        
        new_row = earliest_years.iloc[0].copy()
        new_row['Year'] = year
        new_row['Total Market Gross Bookings'] = new_value
        new_rows.append(new_row)
    
    if new_rows:
        return pd.concat([pd.DataFrame(new_rows), group], ignore_index=True)
    return group

grouped = df.groupby(['Market', 'Channel Type', 'Breakdown'])

new_dfs = []
for name, group in grouped:
    new_group = backfill_data(group)
    new_dfs.append(new_group)

result_df = pd.concat(new_dfs, ignore_index=True)

result_df = result_df.sort_values(['Year', 'Market', 'Channel Type', 'Breakdown'])

result_df.to_excel('temp_historical.xlsx', sheet_name='Historical Data (2005-)', index=False)

temp_wb = load_workbook('temp_historical.xlsx')
temp_ws = temp_wb.active

wb = load_workbook('travel_market_summary.xlsx')

wb.create_sheet('Historical Data (2005-)')
target_ws = wb['Historical Data (2005-)']

for row in temp_ws.rows:
    for cell in row:
        target_ws[cell.coordinate] = cell.value

wb.save('travel_market_summary.xlsx')

os.remove('temp_historical.xlsx')

print("Historical data (2005 onwards) has been added as a new sheet to 'travel_market_summary.xlsx'") 