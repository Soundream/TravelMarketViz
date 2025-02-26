import pandas as pd
import re
import numpy as np

# 读取 Excel 文件
file_path = "your_file.xlsx"  # 请替换为你的文件路径
xls = pd.ExcelFile(file_path)

# 读取相关 sheet
ttm_bounded_df = xls.parse("TTM (bounded)")
revenue_df = xls.parse("Revenue")

# 定义提取年份和季度的函数
def extract_year_quarter(value):
    match = re.match(r"(\d{4})'Q(\d)", str(value))
    if match:
        year = int(match.group(1))
        quarter = int(match.group(2))
        return year + (quarter - 1) * 0.25
    return None

# 定义收入数据处理函数
def process_revenue(value):
    try:
        # 如果是字符串，先移除逗号
        if isinstance(value, str):
            value = value.replace(',', '')
        
        # 将值转换为浮点数
        revenue = float(value)
        
        # 如果数值大于10000，认为是需要转换的公式计算值（比如413894）
        if revenue > 10000:
            return round(revenue / 1000, 2)  # 除以1000并保留两位小数
        # 如果数值在1000到10000之间，保持原值（比如1214）
        elif 1000 <= revenue <= 10000:
            return revenue
        # 如果数值小于1000，可能已经是转换后的值，保持原值
        else:
            return revenue
            
    except (ValueError, TypeError):
        return None  # 如果无法转换为数值，返回None而不是原值

# 定义安全的数值转换函数
def safe_convert_to_float(value):
    try:
        if isinstance(value, str):
            value = value.replace(',', '').replace('%', '')
        return float(value)
    except (ValueError, TypeError):
        return None

# 打印原始数据的基本信息
print("\n原始数据信息:")
print(f"TTM (bounded) sheet 形状: {ttm_bounded_df.shape}")
print(f"Revenue sheet 形状: {revenue_df.shape}")

# 找到指标的起始位置
first_col = ttm_bounded_df.iloc[:, 0].astype(str)
revenue_growth_start = first_col[first_col == "Revenue Growth YoY"].index[0]
ebitda_margin_start = first_col[first_col == "EBITDA Margin"].index[0]

print(f"\n找到的指标位置:")
print(f"Revenue Growth YoY 起始行: {revenue_growth_start}")
print(f"EBITDA Margin 起始行: {ebitda_margin_start}")

# 获取所有季度
all_quarters = []
# 从Revenue sheet获取季度
revenue_quarters = revenue_df.iloc[:, 0].dropna().tolist()
# 从TTM sheet获取季度
ttm_quarters = first_col[revenue_growth_start + 1:ebitda_margin_start].dropna().tolist()

# 合并所有季度并去重
all_quarters = list(set(revenue_quarters + ttm_quarters))
all_quarters = [q for q in all_quarters if extract_year_quarter(q) is not None]
all_quarters.sort(key=lambda x: extract_year_quarter(x))

print(f"\n季度范围:")
print(f"最早季度: {all_quarters[0]}")
print(f"最晚季度: {all_quarters[-1]}")
print(f"总季度数: {len(all_quarters)}")

# 获取公司列表（从第二列开始）
companies = revenue_df.columns[1:].tolist()
print(f"\n公司列表 ({len(companies)}家):")
print(companies)

# 创建一个空的列表来存储所有季度的数据
all_data = []

# 处理每个季度的数据
for quarter_str in all_quarters:
    numeric_year = extract_year_quarter(quarter_str)
    if numeric_year is None:
        continue
        
    # 在两个DataFrame中查找对应的季度数据
    revenue_row = revenue_df[revenue_df.iloc[:, 0] == quarter_str]
    ttm_revenue_growth_idx = first_col[first_col == quarter_str].index
    ttm_revenue_growth_idx = [idx for idx in ttm_revenue_growth_idx if revenue_growth_start < idx < ebitda_margin_start]
    ttm_ebitda_margin_idx = first_col[first_col == quarter_str].index
    ttm_ebitda_margin_idx = [idx for idx in ttm_ebitda_margin_idx if idx > ebitda_margin_start]
    
    if not revenue_row.empty and ttm_revenue_growth_idx and ttm_ebitda_margin_idx:
        revenue_data = revenue_row.iloc[0, 1:]
        revenue_growth_data = ttm_bounded_df.iloc[ttm_revenue_growth_idx[0], 1:len(companies) + 1]
        ebitda_margin_data = ttm_bounded_df.iloc[ttm_ebitda_margin_idx[0], 1:len(companies) + 1]
        
        # 处理每个公司的数据
        for i, company in enumerate(companies):
            revenue = process_revenue(revenue_data.iloc[i])
            revenue_growth = safe_convert_to_float(revenue_growth_data.iloc[i])
            ebitda_margin = safe_convert_to_float(ebitda_margin_data.iloc[i])
            
            # 只添加至少有一个非空值的数据点
            if not (pd.isna(revenue) and pd.isna(ebitda_margin) and pd.isna(revenue_growth)):
                all_data.append({
                    "Company": company,
                    "Numeric_Year": numeric_year,
                    "Quarter": quarter_str,
                    "Revenue": revenue,
                    "EBITDA Margin (%)": ebitda_margin,
                    "Revenue Growth (%)": revenue_growth
                })
    else:
        print(f"警告: 季度 {quarter_str} 在某些表格中未找到完整数据")

# 创建 DataFrame
formatted_df = pd.DataFrame(all_data)

# 按公司和时间排序
formatted_df.sort_values(["Company", "Numeric_Year"], inplace=True)

# 数据验证
print("\n数据验证:")
for company in companies:
    company_data = formatted_df[formatted_df['Company'] == company]
    if not company_data.empty:
        print(f"\n{company}:")
        print(f"数据范围: {company_data['Quarter'].min()} 到 {company_data['Quarter'].max()}")
        print(f"数据点数量: {len(company_data)}")
        
        # 安全地计算数值统计
        revenue_data = pd.to_numeric(company_data['Revenue'], errors='coerce')
        ebitda_data = pd.to_numeric(company_data['EBITDA Margin (%)'], errors='coerce')
        growth_data = pd.to_numeric(company_data['Revenue Growth (%)'], errors='coerce')
        
        if not revenue_data.empty and not revenue_data.isna().all():
            print(f"Revenue范围: {revenue_data.min():.2f} 到 {revenue_data.max():.2f}")
        if not ebitda_data.empty and not ebitda_data.isna().all():
            print(f"EBITDA Margin范围: {ebitda_data.min():.2f} 到 {ebitda_data.max():.2f}")
        if not growth_data.empty and not growth_data.isna().all():
            print(f"Revenue Growth范围: {growth_data.min():.2f} 到 {growth_data.max():.2f}")

# 保存结果
formatted_df.to_excel("formatted_data.xlsx", index=False)
print(f"\n数据处理完成，已保存为 formatted_data.xlsx")
print(f"\n总体统计:")
print(f"总行数: {len(formatted_df)}")
print(f"公司数量: {len(formatted_df['Company'].unique())}")
print(f"季度范围: {formatted_df['Quarter'].min()} 到 {formatted_df['Quarter'].max()}")

# 安全地计算总体数值统计
revenue_all = pd.to_numeric(formatted_df['Revenue'], errors='coerce')
print("\n收入范围:")
print(f"最小值: {revenue_all.min():.2f}")
print(f"最大值: {revenue_all.max():.2f}")
print(f"中位数: {revenue_all.median():.2f}")