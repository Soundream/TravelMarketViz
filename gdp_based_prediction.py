import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
import math

# GDP percentage data for each country
gdp_data = {
    "Country": [
        "Argentina", "Australia-New Zealand", "Brazil", "Bulgaria", "Canada", "Chile", "China",
        "Colombia", "Czech Republic", "Egypt", "France", "Germany", "Greece", "Hong Kong", "Hungary",
        "India", "Indonesia", "Italy", "Japan", "Macau", "Malaysia", "Mexico", "Poland", "Qatar",
        "Rest of Eastern Europe", "Rest of Europe", "Rest of Middle East", "Romania", "Russia",
        "Saudi Arabia", "Scandinavia", "Singapore", "South Korea", "Spain", "Taiwan", "Thailand",
        "U.A.E.", "U.K.", "U.S.", "Ukraine"
    ],
    "2005": [
        0.5968502408, 0.7717221773, 0.5348744719, 0.574134476, 0.8534025479, 0.7119317719, 0.4480790966,
        0.6263232543, 0.663202092, 0.4737091415, 0.8118832575, 0.8314824142, 0.7414140975, 0.8482652726,
        0.8637506771, 0.6113652951, 0.5297983132, 0.8440803337, 0.9134083224, 0.5632840539, 0.7096618872,
        0.9725837018, 0.6963162875, 0.455329704, 0.6823409115, 0.8602765465, 0.7093498973, 0.5654705584,
        0.6248873639, 0.76546549, 0.844450253, 0.6582933913, 0.9904222865, 0.77153356, 0.9570937674,
        0.6720314684, 0.7123618596, 1.054019327, 0.9006172578, 0.7341611201
    ],
    "2006": [
        0.6984194728, 0.8189002173, 0.6644444559, 0.6608616764, 0.9597269606, 0.8955955196, 0.5394522307,
        0.6959774997, 0.7548670686, 0.567950239, 0.8584431125, 0.875426184, 0.8232848686, 0.9041692875,
        0.8828585931, 0.7006992215, 0.6756559876, 0.8864347384, 0.8699629662, 0.6890052582, 0.8043820184,
        1.081433746, 0.7845414405, 0.6225272904, 0.7703504572, 0.9129496878, 0.8455432752, 0.7008406334,
        0.8096637557, 0.878354713, 0.9195764997, 0.7655270107, 1.115764579, 0.8431492356, 0.9887956114,
        0.7871846933, 0.8760357156, 1.122511884, 0.9542422341, 0.9204670531
    ],
    "2007": [
        0.8635159591, 0.9448268274, 0.8381028622, 0.8540862203, 1.068524329, 1.00415173, 0.6959119469,
        0.8871283474, 0.9181957462, 0.6896108562, 0.9836082493, 1.001223018, 0.9614414399, 0.9885499818,
        1.069562164, 0.9067347077, 0.8010242581, 1.005901734, 0.865820376, 0.8541858271, 0.956946538,
        1.168445874, 0.9746505868, 0.815065761, 0.974028796, 1.045941919, 0.9655954039, 1.00274682,
        1.063025262, 0.9693930965, 1.059390917, 0.9319672258, 1.242252427, 0.9867422969, 1.041138196,
        0.9333784149, 1.017230606, 1.280859981, 0.9997348403, 1.223621772
    ],
    "2008": [
        1.08583655, 1.132466755, 1.017311762, 1.047226133, 1.129755046, 1.047251095, 0.9005517335,
        1.043169205, 1.142697557, 0.8608023238, 1.083970625, 1.094541389, 1.074327372, 1.02443825,
        1.20795387, 0.893439038, 0.9456031618, 1.094150519, 0.9654382757, 0.9740238045, 1.141177301,
        1.231192914, 1.214838717, 1.178650284, 1.193194675, 1.113735966, 1.217950277, 1.230918824,
        1.358404799, 1.211371205, 1.165606294, 0.9972549088, 1.109537607, 1.093230665, 1.064150818,
        1.034334353, 1.244243353, 1.214092835, 1.020154279, 1.547569379
    ],
    "2009": [
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1
    ]
}

def load_actual_data():
    """Load actual data from 2009 onwards"""
    actual_df = pd.read_excel('wit/web_region_bubble/travel_market_summary.xlsx')
    return actual_df

def get_country_gdp_ratios(country):
    """Get GDP ratios for a specific country"""
    country_idx = gdp_data["Country"].index(country)
    return {
        "2005": gdp_data["2005"][country_idx],
        "2006": gdp_data["2006"][country_idx],
        "2007": gdp_data["2007"][country_idx],
        "2008": gdp_data["2008"][country_idx],
        "2009": 1.0
    }

def learn_channel_growth_patterns(df):
    """Learn growth patterns for each channel from 2009 onwards"""
    channel_patterns = {}
    
    # 按渠道分组计算年度增长率
    for channel in df['Channel Type'].unique():
        channel_data = df[df['Channel Type'] == channel].copy()
        yearly_total = channel_data.groupby('Year')['Total Market Gross Bookings'].sum()
        
        # 计算年度增长率
        growth_rates = yearly_total.pct_change()
        # 只使用2009年之后的数据，并移除NaN值
        growth_rates = growth_rates[growth_rates.index >= 2010]  # 从2010开始避免2009的NaN
        
        # 使用简单线性回归来学习增长趋势
        X = np.array(range(len(growth_rates))).reshape(-1, 1)
        y = growth_rates.values
        
        reg = LinearRegression()
        reg.fit(X, y)
        
        # 存储每个渠道的基准增长率和趋势
        channel_patterns[channel] = {
            'base_growth': growth_rates.iloc[0],  # 使用2010年的增长率作为基准
            'trend': reg.coef_[0],
            'intercept': reg.intercept_
        }
    
    return channel_patterns

def adjust_historical_predictions(historical_df, channel_patterns):
    """根据学习到的增长模式调整历史预测"""
    adjusted_df = historical_df.copy()
    
    for channel in historical_df['Channel Type'].unique():
        pattern = channel_patterns[channel]
        channel_mask = adjusted_df['Channel Type'] == channel
        
        # 对于每个国家分别调整
        for country in historical_df['Market'].unique():
            country_mask = adjusted_df['Market'] == country
            
            try:
                # 获取2008年的基准值
                base_value_2008 = historical_df[
                    (historical_df['Market'] == country) & 
                    (historical_df['Channel Type'] == channel) & 
                    (historical_df['Year'] == 2008)
                ]['Total Market Gross Bookings'].iloc[0]
                
                if channel == 'Online':
                    # 对在线渠道使用GDP和regression的组合，但减弱GDP对2005-2007年的影响
                    for year in range(2007, 2004, -1):
                        years_from_2008 = 2008 - year
                        growth_adjustment = pattern['base_growth'] + (pattern['trend'] * years_from_2008)
                        
                        gdp_ratio = historical_df.loc[
                            (channel_mask) & (country_mask) & (historical_df['Year'] == year),
                            'Total Market Gross Bookings'
                        ].iloc[0] / base_value_2008
                        
                        # 对2005-2007年减弱GDP的影响
                        gdp_impact = 1.5  # GDP影响力降低到30%
                        adjusted_gdp_ratio = 1.0 + (gdp_ratio - 1.0) * gdp_impact
                        
                        adjusted_value = base_value_2008 * adjusted_gdp_ratio * (1 + growth_adjustment * 0.7)
                        
                        if adjusted_value > 0:
                            adjusted_df.loc[
                                (channel_mask) & (country_mask) & (adjusted_df['Year'] == year),
                                'Total Market Gross Bookings'
                            ] = adjusted_value
                
                else:
                    # 对其他渠道使用原有的调整方法
                    for year in range(2007, 2004, -1):
                        years_from_2008 = 2008 - year
                        growth_adjustment = pattern['base_growth'] + (pattern['trend'] * years_from_2008)
                        
                        if channel == 'Offline':
                            growth_adjustment = growth_adjustment * 0.85  # 降低15%的增长率
                        
                        gdp_ratio = historical_df.loc[
                            (channel_mask) & (country_mask) & (historical_df['Year'] == year),
                            'Total Market Gross Bookings'
                        ].iloc[0] / base_value_2008
                        
                        adjusted_value = base_value_2008 * gdp_ratio * (1 + growth_adjustment * 0.7)
                        
                        if adjusted_value > 0:
                            adjusted_df.loc[
                                (channel_mask) & (country_mask) & (adjusted_df['Year'] == year),
                                'Total Market Gross Bookings'
                            ] = adjusted_value
            except (IndexError, KeyError):
                continue
    
    # 对2005-2007年的online数据进行整体上移
    online_mask = adjusted_df['Channel Type'] == 'Online'
    for year in range(2005, 2008):
        year_mask = adjusted_df['Year'] == year
        # 上移力度随着年份增加而减小
        lift_factor = 1.15 - (year - 2005) * 0.02  # 2005年提升15%，逐年略微减少
        adjusted_df.loc[online_mask & year_mask, 'Total Market Gross Bookings'] *= lift_factor
    
    return adjusted_df

def generate_historical_predictions(actual_df):
    """Generate predictions for 2005-2008 using combined GDP and growth pattern approach"""
    # 首先使用GDP比率生成基础预测
    historical_data = []
    base_data_2009 = actual_df[actual_df['Year'] == 2009].copy()
    
    for _, row in base_data_2009.iterrows():
        country = row['Market']
        channel = row['Channel Type']
        base_value = row['Total Market Gross Bookings']
        
        try:
            gdp_ratios = get_country_gdp_ratios(country)
            
            for year in range(2005, 2009):
                predicted_value = base_value * gdp_ratios[str(year)]
                historical_data.append({
                    'Year': year,
                    'Market': country,
                    'Channel Type': channel,
                    'Total Market Gross Bookings': predicted_value,
                    'Data Level': row['Data Level'],
                    'Region': row['Region'],
                    'Breakdown': row['Breakdown']
                })
        except ValueError:
            print(f"Warning: GDP data not found for {country}")
            continue
    
    # 转换为DataFrame
    historical_df = pd.DataFrame(historical_data)
    
    # 学习2009年之后的增长模式
    channel_patterns = learn_channel_growth_patterns(actual_df[actual_df['Year'] >= 2009])
    
    # 调整历史预测
    adjusted_historical_df = adjust_historical_predictions(historical_df, channel_patterns)
    
    # 合并调整后的历史数据和实际数据
    combined_df = pd.concat([
        adjusted_historical_df,
        actual_df[actual_df['Year'] >= 2009]
    ])
    
    return combined_df

def create_visualizations(df):
    """Create visualizations for the predictions"""
    plt.figure(figsize=(15, 12))
    
    # First subplot: Total Market
    plt.subplot(3, 1, 1)
    total_market = df.groupby('Year')['Total Market Gross Bookings'].sum().reset_index()
    plt.scatter(total_market['Year'], total_market['Total Market Gross Bookings'] / 1e9,
                color='blue', label='Total Market', alpha=0.6)
    
    plt.title('Total Market Gross Bookings (Country GDP-based)', fontsize=14)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Gross Bookings (USD)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=10)
    
    plt.xticks(np.arange(2005, 2026, 1), rotation=45)
    current_values = plt.gca().get_yticks()
    plt.gca().set_yticklabels(['${:.1f}B'.format(x) for x in current_values])
    plt.axvline(x=2008, color='gray', linestyle=':', label='Crisis Year (2008)')
    
    # Second subplot: Channel Comparison
    plt.subplot(3, 1, 2)
    channel_data = df.groupby(['Year', 'Channel Type'])['Total Market Gross Bookings'].sum().reset_index()
    
    for channel in channel_data['Channel Type'].unique():
        channel_subset = channel_data[channel_data['Channel Type'] == channel]
        plt.scatter(channel_subset['Year'], channel_subset['Total Market Gross Bookings'] / 1e9,
                   label=channel, alpha=0.6)
        plt.plot(channel_subset['Year'], channel_subset['Total Market Gross Bookings'] / 1e9, alpha=0.4)
    
    plt.title('Channel-wise Gross Bookings (Country GDP-based)', fontsize=14)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Gross Bookings (USD)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=10)
    
    plt.xticks(np.arange(2005, 2026, 1), rotation=45)
    current_values = plt.gca().get_yticks()
    plt.gca().set_yticklabels(['${:.1f}B'.format(x) for x in current_values])
    plt.axvline(x=2008, color='gray', linestyle=':', label='Crisis Year (2008)')
    
    # Third subplot: Year-over-Year Growth Rate
    plt.subplot(3, 1, 3)
    yoy_growth = total_market.set_index('Year')['Total Market Gross Bookings'].pct_change() * 100
    
    plt.plot(total_market['Year'], yoy_growth,
             color='purple', label='YoY Growth Rate', marker='o')
    plt.axvline(x=2008, color='gray', linestyle=':', label='Crisis Year (2008)')
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    plt.title('Year-over-Year Growth Rate (Country GDP-based)', fontsize=14)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Growth Rate (%)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=10)
    
    plt.xticks(np.arange(2005, 2026, 1), rotation=45)
    
    plt.tight_layout()
    plt.savefig('country_gdp_based_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

def calculate_online_penetration(df):
    """Calculate online penetration for each country"""
    # Calculate total gross bookings by country and year
    total_bookings = df.groupby(['Year', 'Market', 'Region'])['Total Market Gross Bookings'].sum().reset_index()
    
    # Calculate online bookings by country and year
    online_bookings = df[df['Channel Type'] == 'Online'].groupby(['Year', 'Market', 'Region'])['Total Market Gross Bookings'].sum().reset_index()
    
    # Merge total and online bookings
    penetration_df = pd.merge(total_bookings, online_bookings, 
                             on=['Year', 'Market', 'Region'], 
                             suffixes=('', '_Online'))
    
    # Calculate penetration percentage
    penetration_df = penetration_df.rename(columns={
        'Total Market Gross Bookings': 'Gross Bookings(US$)',
        'Total Market Gross Bookings_Online': 'Online Bookings(US$)'
    })
    
    penetration_df['Online Penetration %'] = (penetration_df['Online Bookings(US$)'] / 
                                            penetration_df['Gross Bookings(US$)'] * 100)
    
    # Sort by Year, Region, and Market
    penetration_df = penetration_df.sort_values(['Year', 'Region', 'Market'])
    
    return penetration_df[['Year', 'Market', 'Region', 'Gross Bookings(US$)', 
                          'Online Bookings(US$)', 'Online Penetration %']]

def main():
    # Load actual data
    actual_data = load_actual_data()
    
    # Generate predictions using country-specific GDP ratios
    combined_df = generate_historical_predictions(actual_data)
    
    # Create visualizations
    create_visualizations(combined_df)
    
    # Filter and reorder columns for Excel output
    historical_df = combined_df[combined_df['Year'].between(2005, 2008)].copy()
    historical_df['First \'ExchangeRatesV4\'[Currency]'] = 'U.S. Dollars (US$)'  
    
    # Reorder columns
    ordered_columns = [
        'Year',
        'Data Level',
        'Region',
        'Market',
        'Channel Type',
        'Breakdown',
        'Total Market Gross Bookings',
        'First \'ExchangeRatesV4\'[Currency]'
    ]
    
    # Calculate online penetration
    penetration_df = calculate_online_penetration(historical_df)
    
    # Create Excel writer object
    with pd.ExcelWriter('historical_predictions_2005_2008.xlsx', engine='openpyxl') as writer:
        # Save main data to first sheet
        historical_df[ordered_columns].to_excel(writer, sheet_name='Historical Data', index=False)
        
        # Save penetration data to second sheet
        penetration_df.to_excel(writer, sheet_name='Online Penetration', index=False, float_format='%.1f')
        
        # Format the penetration sheet
        workbook = writer.book
        worksheet = writer.sheets['Online Penetration']
        
        # Format numbers with commas and no decimal places for Gross Bookings
        for col in ['D', 'E']:  # Columns for Gross Bookings and Online Bookings
            for row in range(2, len(penetration_df) + 2):
                cell = worksheet[f'{col}{row}']
                cell.number_format = '#,##0'
        
        # Format percentages with one decimal place
        for row in range(2, len(penetration_df) + 2):
            cell = worksheet[f'F{row}']  # Column for Online Penetration %
            cell.number_format = '0.0'
    
    # Print summary by region
    region_summary = combined_df.groupby(['Year', 'Region'])['Total Market Gross Bookings'].sum().reset_index()
    pivot_region = region_summary.pivot(index='Year', columns='Region', values='Total Market Gross Bookings')
    
    print("\nRegional Summary (billions USD):")
    print((pivot_region / 1e9).round(2))
    
    print("\nHistorical predictions (2005-2008) have been saved to 'historical_predictions_2005_2008.xlsx'")
    print("Visualizations have been saved as 'country_gdp_based_analysis.png'")

if __name__ == "__main__":
    main() 