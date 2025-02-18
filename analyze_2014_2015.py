import pandas as pd
import numpy as np

def analyze_2014_2015():
    # Read the Excel file
    df = pd.read_excel('wit/web_region_bubble/travel_market_summary.xlsx', sheet_name='Summary')
    
    # Create a function to format numbers in billions
    def format_billions(x):
        return f"${x/1e9:.2f}B"
    
    # Filter for 2014 and 2015 years
    df_filtered = df[df['Year'].isin([2014, 2015])]
    
    # Calculate total bookings for each year
    yearly_totals = df_filtered.groupby('Year')['Total Market Gross Bookings'].sum()
    
    difference = yearly_totals[2015] - yearly_totals[2014]
    pct_change = (difference / yearly_totals[2014]) * 100
    
    print("\nTotal Market Gross Bookings Analysis for 2014-2015:")
    print("-" * 50)
    print(f"2014 Total: {format_billions(yearly_totals[2014])}")
    print(f"2015 Total: {format_billions(yearly_totals[2015])}")
    print(f"Absolute Change: {format_billions(difference)}")
    print(f"Percentage Change: {pct_change:.2f}%")
    
    print("\nBreakdown by Region:")
    print("-" * 50)
    region_analysis = df_filtered.groupby(['Year', 'Region'])['Total Market Gross Bookings'].sum().unstack()
    region_diff = region_analysis.diff().iloc[1]
    region_pct = (region_analysis.pct_change().iloc[1] * 100)
    
    for region in region_analysis.columns:
        print(f"\n{region}:")
        print(f"2014: {format_billions(region_analysis.loc[2014, region])}")
        print(f"2015: {format_billions(region_analysis.loc[2015, region])}")
        print(f"Change: {format_billions(region_diff[region])} ({region_pct[region]:.2f}%)")

if __name__ == "__main__":
    analyze_2014_2015() 