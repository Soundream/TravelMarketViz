import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# 更新文件路径，包含新添加的2024和2025年数据
appannie_files = [
    "random/appannie.csv",
    "random/appannie-2.csv",
    "random/appannie-3.csv",
    "random/appannie-4.csv",
    "random/appanie_202412.csv",  # 2024年12月数据
    "random/bq-results-20250407-062455-1744007100217.csv"  # 2025年2月数据
]

similarweb_files = [
    "random/similarweb.csv",
    "random/similarweb-2.csv",
    "random/similarweb-3.csv",
    "random/similarweb-4.csv",
    "random/similarweb_202412.csv",  # 2024年12月数据
    "random/bq-results-20250407-062205-1744007072562.csv"  # 2025年2月数据
]

# Function to read and filter data
def load_data(file_path):
    if not os.path.exists(file_path):
        print(f"Warning: File {file_path} does not exist. Skipping...")
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(file_path)
        # 简化公司类型过滤逻辑，因为所有文件都使用 company_type 列
        df = df[df['company_type'].isin(['OTA', 'Meta'])]
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

# Print earliest and latest data months for both datasets
earliest_app_month = appannie_data['date'].min().strftime('%Y-%m')
latest_app_month = appannie_data['date'].max().strftime('%Y-%m')
earliest_web_month = similarweb_data['date'].min().strftime('%Y-%m')
latest_web_month = similarweb_data['date'].max().strftime('%Y-%m')

print(f"\nApp downloads data range: {earliest_app_month} to {latest_app_month}")
print(f"Web visits data range: {earliest_web_month} to {latest_web_month}")

# Get Wego data
wego_appannie_data = appannie_data[appannie_data['company'] == 'Wego'].copy()
wego_similarweb_data = similarweb_data[similarweb_data['company'] == 'Wego'].copy()

# Get all MENA data (for calculating Wego's percentage in MENA)
mena_appannie_data = appannie_data[appannie_data['region'] == 'MENA'].copy()
mena_similarweb_data = similarweb_data[similarweb_data['region'] == 'MENA'].copy()

# Function to analyze monthly app downloads with correct global calculation
def analyze_monthly_app_downloads():
    if wego_appannie_data.empty:
        print("No AppAnnie data available for Wego analysis.")
        return
    
    # Sort data by date
    wego_data = wego_appannie_data.sort_values('date')
    mena_data = mena_appannie_data.sort_values('date')
    
    # 按月汇总Wego所有国家的下载量作为全球数据
    global_monthly = wego_data.groupby(['year', 'month_num', 'year_month']).agg({
        'downloads': 'sum',
        'date': 'first'
    }).reset_index()
    global_monthly.rename(columns={'downloads': 'downloads_global'}, inplace=True)
    
    # MENA地区的Wego下载量
    mena_monthly = wego_data[wego_data['region'] == 'MENA'].groupby(['year', 'month_num', 'year_month']).agg({
        'downloads': 'sum',
        'date': 'first'
    }).reset_index()
    mena_monthly.rename(columns={'downloads': 'downloads_mena'}, inplace=True)
    
    # MENA地区所有公司的总下载量
    total_mena_monthly = mena_data.groupby(['year', 'month_num', 'year_month']).agg({
        'downloads': 'sum',
        'date': 'first'
    }).reset_index().rename(columns={'downloads': 'total_mena_downloads'})
    
    # 合并结果
    result = pd.merge(
        global_monthly, 
        mena_monthly, 
        on=['year', 'month_num', 'year_month', 'date'], 
        how='outer'
    )
    
    result = pd.merge(
        result, 
        total_mena_monthly, 
        on=['year', 'month_num', 'year_month', 'date'],
        how='outer'
    )
    
    # 处理缺失值
    result = result.fillna(0)
    
    # 计算百分比
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
    
    # 添加月份名称以提高可读性
    result['month_name'] = pd.DatetimeIndex(result['date']).strftime('%b')
    
    # 按日期排序
    result = result.sort_values('date')
    
    # 创建年月标签列
    result['period'] = result['date'].dt.strftime('%Y-%m')
    
    # 年度分析（2017-2025）
    years = sorted(result['year'].unique())
    print("\n======== APP DOWNLOADS YEARLY ANALYSIS ========")
    
    for year in years:
        year_data = result[result['year'] == year].copy()
        
        # 如果是2025年，虽然只有部分数据，但按要求把它当作全年数据分析
        if year == 2025:
            available_months = len(year_data)
            print(f"\n=== {year} App Downloads Analysis (Using {available_months} months data as full year) ===")
        # 2017年特殊处理：汇总2017下半年数据作为全年数据
        elif year == 2017:
            print(f"\n=== {year} App Downloads Analysis (Using H2 2017 data as full year) ===")
        else:
            print(f"\n=== {year} App Downloads Analysis ===")
            
        global_year = year_data['downloads_global'].sum()
        mena_year = year_data['downloads_mena'].sum()
        total_mena_year = year_data['total_mena_downloads'].sum()
        
        pct_of_global = (mena_year / global_year * 100).round(2) if global_year > 0 else 0
        pct_of_mena = (mena_year / total_mena_year * 100).round(2) if total_mena_year > 0 else 0
        
        print(f"Global Downloads ({year}): {int(global_year):,}")
        print(f"MENA Region Downloads ({year}): {int(mena_year):,}")
        print(f"Total MENA Market Downloads ({year}): {int(total_mena_year):,}")
        print(f"MENA as % of Global: {pct_of_global}%")
        print(f"Wego's % Share of MENA Market: {pct_of_mena}%")
    
    # 总体统计
    total_global = result['downloads_global'].sum()
    total_mena = result['downloads_mena'].sum()
    total_all_mena = result['total_mena_downloads'].sum()
    avg_pct_of_global = (total_mena / total_global * 100).round(2) if total_global > 0 else 0
    avg_pct_of_mena = (total_mena / total_all_mena * 100).round(2) if total_all_mena > 0 else 0
    
    print("\n=== Overall App Downloads Statistics (All Years) ===")
    print(f"Total Global Downloads: {int(total_global):,}")
    print(f"Total MENA Downloads: {int(total_mena):,}")
    print(f"Total MENA Market Downloads: {int(total_all_mena):,}")
    print(f"Overall MENA as % of Global: {avg_pct_of_global}%")
    print(f"Overall Wego's % Share of MENA Market: {avg_pct_of_mena}%")
    
    # 年度变化分析
    yearly_data = result.groupby('year').agg({
        'downloads_global': 'sum',
        'downloads_mena': 'sum',
        'total_mena_downloads': 'sum'
    }).reset_index()
    
    yearly_data['mena_percentage_of_global'] = np.where(
        yearly_data['downloads_global'] > 0,
        (yearly_data['downloads_mena'] / yearly_data['downloads_global'] * 100).round(2),
        0
    )
    
    yearly_data['wego_percentage_of_mena'] = np.where(
        yearly_data['total_mena_downloads'] > 0,
        (yearly_data['downloads_mena'] / yearly_data['total_mena_downloads'] * 100).round(2),
        0
    )
    
    return result, yearly_data

# Function to analyze monthly web visits with correct global calculation
def analyze_monthly_web_visits():
    if wego_similarweb_data.empty:
        print("No SimilarWeb data available for Wego analysis.")
        return
    
    # Determine visit column name
    visit_column = 'country_visits' if 'country_visits' in wego_similarweb_data.columns else 'visits'
    
    # Sort data by date
    wego_data = wego_similarweb_data.sort_values('date')
    mena_data = mena_similarweb_data.sort_values('date')
    
    # 按月汇总Wego所有国家的访问量作为全球数据
    global_monthly = wego_data.groupby(['year', 'month_num', 'year_month']).agg({
        visit_column: 'sum',
        'date': 'first'
    }).reset_index()
    global_monthly.rename(columns={visit_column: f'{visit_column}_global'}, inplace=True)
    
    # MENA地区的Wego访问量
    mena_monthly = wego_data[wego_data['region'] == 'MENA'].groupby(['year', 'month_num', 'year_month']).agg({
        visit_column: 'sum',
        'date': 'first'
    }).reset_index()
    mena_monthly.rename(columns={visit_column: f'{visit_column}_mena'}, inplace=True)
    
    # MENA地区所有公司的总访问量
    total_mena_monthly = mena_data.groupby(['year', 'month_num', 'year_month']).agg({
        visit_column: 'sum',
        'date': 'first'
    }).reset_index().rename(columns={visit_column: 'total_mena_visits'})
    
    # 合并结果
    result = pd.merge(
        global_monthly, 
        mena_monthly, 
        on=['year', 'month_num', 'year_month', 'date'], 
        how='outer'
    )
    
    result = pd.merge(
        result, 
        total_mena_monthly, 
        on=['year', 'month_num', 'year_month', 'date'],
        how='outer'
    )
    
    # 处理缺失值
    result = result.fillna(0)
    
    # 计算百分比
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
    
    # 添加月份名称以提高可读性
    result['month_name'] = pd.DatetimeIndex(result['date']).strftime('%b')
    
    # 按日期排序
    result = result.sort_values('date')
    
    # 创建年月标签列
    result['period'] = result['date'].dt.strftime('%Y-%m')
    
    # 年度分析（2017-2025）
    years = sorted(result['year'].unique())
    print("\n======== WEB VISITS YEARLY ANALYSIS ========")
    
    for year in years:
        year_data = result[result['year'] == year].copy()
        
        # 如果是2025年，虽然只有部分数据，但按要求把它当作全年数据分析
        if year == 2025:
            available_months = len(year_data)
            print(f"\n=== {year} Web Visits Analysis (Using {available_months} months data as full year) ===")
        # 2017年特殊处理：汇总2017下半年数据作为全年数据
        elif year == 2017:
            print(f"\n=== {year} Web Visits Analysis (Using H2 2017 data as full year) ===")
        else:
            print(f"\n=== {year} Web Visits Analysis ===")
            
        global_year = year_data[f'{visit_column}_global'].sum()
        mena_year = year_data[f'{visit_column}_mena'].sum()
        total_mena_year = year_data['total_mena_visits'].sum()
        
        pct_of_global = (mena_year / global_year * 100).round(2) if global_year > 0 else 0
        pct_of_mena = (mena_year / total_mena_year * 100).round(2) if total_mena_year > 0 else 0
        
        print(f"Global Web Visits ({year}): {int(global_year):,}")
        print(f"MENA Region Web Visits ({year}): {int(mena_year):,}")
        print(f"Total MENA Market Web Visits ({year}): {int(total_mena_year):,}")
        print(f"MENA as % of Global: {pct_of_global}%")
        print(f"Wego's % Share of MENA Market: {pct_of_mena}%")
    
    # 总体统计
    total_global = result[f'{visit_column}_global'].sum()
    total_mena = result[f'{visit_column}_mena'].sum()
    total_all_mena = result['total_mena_visits'].sum()
    avg_pct_of_global = (total_mena / total_global * 100).round(2) if total_global > 0 else 0
    avg_pct_of_mena = (total_mena / total_all_mena * 100).round(2) if total_all_mena > 0 else 0
    
    print("\n=== Overall Web Visits Statistics (All Years) ===")
    print(f"Total Global Web Visits: {int(total_global):,}")
    print(f"Total MENA Web Visits: {int(total_mena):,}")
    print(f"Total MENA Market Web Visits: {int(total_all_mena):,}")
    print(f"Overall MENA as % of Global: {avg_pct_of_global}%")
    print(f"Overall Wego's % Share of MENA Market: {avg_pct_of_mena}%")
    
    # 年度变化分析
    yearly_data = result.groupby('year').agg({
        f'{visit_column}_global': 'sum',
        f'{visit_column}_mena': 'sum',
        'total_mena_visits': 'sum'
    }).reset_index()
    
    yearly_data['mena_percentage_of_global'] = np.where(
        yearly_data[f'{visit_column}_global'] > 0,
        (yearly_data[f'{visit_column}_mena'] / yearly_data[f'{visit_column}_global'] * 100).round(2),
        0
    )
    
    yearly_data['wego_percentage_of_mena'] = np.where(
        yearly_data['total_mena_visits'] > 0,
        (yearly_data[f'{visit_column}_mena'] / yearly_data['total_mena_visits'] * 100).round(2),
        0
    )
    
    return result, yearly_data, visit_column

# Function to create visualizations
def create_visualizations(app_monthly, app_yearly, web_monthly, web_yearly, web_visit_column):
    # 创建保存图表的目录
    os.makedirs('charts', exist_ok=True)
    
    # 年度App下载量趋势图
    plt.figure(figsize=(15, 8))
    
    plt.plot(app_yearly['year'], app_yearly['downloads_global'], 
             marker='o', linestyle='-', linewidth=2, label='Global Downloads')
    plt.plot(app_yearly['year'], app_yearly['downloads_mena'], 
             marker='s', linestyle='-', linewidth=2, label='MENA Downloads')
    
    plt.title('Wego Annual App Downloads Trend (2017-2025)', fontsize=16)
    plt.xlabel('Year', fontsize=14)
    plt.ylabel('Number of Downloads', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)
    plt.xticks(app_yearly['year'])
    
    # 将2025年的标记为预估值
    if 2025 in app_yearly['year'].values:
        max_y = max(app_yearly['downloads_global'].max(), app_yearly['downloads_mena'].max()) * 1.1
        plt.annotate('*Estimated based on\navailable 2025 data', 
                     xy=(2025, app_yearly[app_yearly['year']==2025]['downloads_global'].values[0]),
                     xytext=(2024.7, max_y * 0.9),
                     fontsize=10, color='red')
    
    plt.tight_layout()
    plt.savefig('charts/wego_annual_app_downloads_trend.png', dpi=300)
    print("\nAnnual app downloads trend visualization saved as 'charts/wego_annual_app_downloads_trend.png'")
    
    # 年度App下载市场份额趋势图
    plt.figure(figsize=(15, 8))
    
    plt.plot(app_yearly['year'], app_yearly['mena_percentage_of_global'], 
             marker='o', linestyle='-', linewidth=2, color='green', label='MENA % of Global')
    plt.plot(app_yearly['year'], app_yearly['wego_percentage_of_mena'], 
             marker='s', linestyle='-', linewidth=2, color='purple', label='Wego % of MENA Market')
    
    plt.title('Wego App Downloads - Annual Market Share Analysis (2017-2025)', fontsize=16)
    plt.xlabel('Year', fontsize=14)
    plt.ylabel('Percentage (%)', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)
    plt.xticks(app_yearly['year'])
    
    # 将2025年的标记为预估值
    if 2025 in app_yearly['year'].values:
        max_y = max(app_yearly['mena_percentage_of_global'].max(), app_yearly['wego_percentage_of_mena'].max()) * 1.1
        plt.annotate('*Estimated based on\navailable 2025 data', 
                     xy=(2025, app_yearly[app_yearly['year']==2025]['mena_percentage_of_global'].values[0]),
                     xytext=(2024.7, max_y * 0.9),
                     fontsize=10, color='red')
    
    plt.tight_layout()
    plt.savefig('charts/wego_annual_app_market_share.png', dpi=300)
    print("Annual app market share visualization saved as 'charts/wego_annual_app_market_share.png'")
    
    # 年度Web访问量趋势图
    plt.figure(figsize=(15, 8))
    
    plt.plot(web_yearly['year'], web_yearly[f'{web_visit_column}_global'], 
             marker='o', linestyle='-', linewidth=2, label='Global Web Visits')
    plt.plot(web_yearly['year'], web_yearly[f'{web_visit_column}_mena'], 
             marker='s', linestyle='-', linewidth=2, label='MENA Web Visits')
    
    plt.title('Wego Annual Web Visits Trend (2017-2025)', fontsize=16)
    plt.xlabel('Year', fontsize=14)
    plt.ylabel('Number of Visits', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)
    plt.xticks(web_yearly['year'])
    
    # 将2025年的标记为预估值
    if 2025 in web_yearly['year'].values:
        max_y = max(web_yearly[f'{web_visit_column}_global'].max(), web_yearly[f'{web_visit_column}_mena'].max()) * 1.1
        plt.annotate('*Estimated based on\navailable 2025 data', 
                     xy=(2025, web_yearly[web_yearly['year']==2025][f'{web_visit_column}_global'].values[0]),
                     xytext=(2024.7, max_y * 0.9),
                     fontsize=10, color='red')
    
    plt.tight_layout()
    plt.savefig('charts/wego_annual_web_visits_trend.png', dpi=300)
    print("Annual web visits trend visualization saved as 'charts/wego_annual_web_visits_trend.png'")
    
    # 年度Web访问市场份额趋势图
    plt.figure(figsize=(15, 8))
    
    plt.plot(web_yearly['year'], web_yearly['mena_percentage_of_global'], 
             marker='o', linestyle='-', linewidth=2, color='green', label='MENA % of Global')
    plt.plot(web_yearly['year'], web_yearly['wego_percentage_of_mena'], 
             marker='s', linestyle='-', linewidth=2, color='purple', label='Wego % of MENA Market')
    
    plt.title('Wego Web Visits - Annual Market Share Analysis (2017-2025)', fontsize=16)
    plt.xlabel('Year', fontsize=14)
    plt.ylabel('Percentage (%)', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)
    plt.xticks(web_yearly['year'])
    
    # 将2025年的标记为预估值
    if 2025 in web_yearly['year'].values:
        max_y = max(web_yearly['mena_percentage_of_global'].max(), web_yearly['wego_percentage_of_mena'].max()) * 1.1
        plt.annotate('*Estimated based on\navailable 2025 data', 
                     xy=(2025, web_yearly[web_yearly['year']==2025]['mena_percentage_of_global'].values[0]),
                     xytext=(2024.7, max_y * 0.9),
                     fontsize=10, color='red')
    
    plt.tight_layout()
    plt.savefig('charts/wego_annual_web_market_share.png', dpi=300)
    print("Annual web market share visualization saved as 'charts/wego_annual_web_market_share.png'")
    
    # 新增：App下载和Web访问在MENA市场份额的对比图
    plt.figure(figsize=(15, 8))
    
    plt.plot(app_yearly['year'], app_yearly['wego_percentage_of_mena'], 
             marker='o', linestyle='-', linewidth=2, color='blue', label='App Downloads % of MENA')
    plt.plot(web_yearly['year'], web_yearly['wego_percentage_of_mena'], 
             marker='s', linestyle='-', linewidth=2, color='orange', label='Web Visits % of MENA')
    
    plt.title('Wego Market Share Comparison in MENA Region (2017-2025)', fontsize=16)
    plt.xlabel('Year', fontsize=14)
    plt.ylabel('Percentage of MENA Market (%)', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)
    plt.xticks(app_yearly['year'])
    
    # 将2025年的标记为预估值
    if 2025 in app_yearly['year'].values:
        max_y = max(app_yearly['wego_percentage_of_mena'].max(), web_yearly['wego_percentage_of_mena'].max()) * 1.1
        plt.annotate('*Estimated based on\navailable 2025 data', 
                     xy=(2025, app_yearly[app_yearly['year']==2025]['wego_percentage_of_mena'].values[0]),
                     xytext=(2024.7, max_y * 0.9),
                     fontsize=10, color='red')
    
    plt.tight_layout()
    plt.savefig('charts/wego_mena_market_share_comparison.png', dpi=300)
    print("MENA market share comparison visualization saved as 'charts/wego_mena_market_share_comparison.png'")

# 运行分析并生成报告
print("\nRunning updated analysis including 2024-2025 data...")
monthly_app_analysis, yearly_app_analysis = analyze_monthly_app_downloads()
monthly_web_analysis, yearly_web_analysis, web_visit_column = analyze_monthly_web_visits()

# 保存详细结果到CSV
if monthly_app_analysis is not None:
    monthly_app_analysis.to_csv('wego_monthly_app_downloads_2017_2025.csv', index=False)
    yearly_app_analysis.to_csv('wego_yearly_app_downloads_2017_2025.csv', index=False)
    print("\nApp downloads analysis results saved to CSV files.")
    
if monthly_web_analysis is not None:
    monthly_web_analysis.to_csv('wego_monthly_web_visits_2017_2025.csv', index=False)
    yearly_web_analysis.to_csv('wego_yearly_web_visits_2017_2025.csv', index=False)
    print("Web visits analysis results saved to CSV files.")

# 创建可视化
create_visualizations(
    monthly_app_analysis, 
    yearly_app_analysis, 
    monthly_web_analysis, 
    yearly_web_analysis,
    web_visit_column
)

print("\nUpdated analysis complete with 2024-2025 data included!") 