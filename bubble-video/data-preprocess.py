import pandas as pd
import re

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

# 找到指标的起始位置
first_col = ttm_bounded_df.iloc[:, 0].astype(str)
revenue_growth_start = first_col[first_col == "Revenue Growth YoY"].index[0]
ebitda_margin_start = first_col[first_col == "EBITDA Margin"].index[0]

# 获取季度列表
quarters = []
for value in first_col[revenue_growth_start + 1:ebitda_margin_start]:
    year_quarter = extract_year_quarter(value)
    if year_quarter is not None:
        quarters.append((year_quarter, value))

if not quarters:
    raise ValueError("未找到有效的年份季度，请检查 Excel 文件。")

# 创建一个空的列表来存储所有季度的数据
all_data = []

# 处理每个季度的数据
for numeric_year, quarter_str in quarters:
    # 找到当前季度在两个指标中的行索引
    revenue_growth_index = revenue_growth_start + 1 + [q[1] for q in quarters].index(quarter_str)
    ebitda_margin_index = ebitda_margin_start + 1 + [q[1] for q in quarters].index(quarter_str)
    
    # 获取指标数据（假设数据在第二列）
    revenue_growth = ttm_bounded_df.iloc[revenue_growth_index, 1]
    ebitda_margin = ttm_bounded_df.iloc[ebitda_margin_index, 1]
    
    # 从 Revenue sheet 获取收入数据
    companies = revenue_df.columns[1:]  # 假设第一列是季度，其他列是公司
    try:
        quarter_revenues = revenue_df.loc[revenue_df.iloc[:, 0] == quarter_str].iloc[0, 1:].values
        
        # 为每个公司创建一条记录
        for company, revenue in zip(companies, quarter_revenues):
            all_data.append({
                "Company": company,
                "Numeric_Year": numeric_year,
                "Quarter": quarter_str,
                "Revenue": revenue,
                "EBITDA Margin (%)": ebitda_margin,
                "Revenue Growth (%)": revenue_growth
            })
    except IndexError:
        print(f"警告: 在Revenue sheet中未找到季度 {quarter_str} 的数据")
        continue

# 创建 DataFrame
formatted_df = pd.DataFrame(all_data)

# 去除 NaN 数据
formatted_df.dropna(inplace=True)

# 按公司和时间排序
formatted_df.sort_values(["Company", "Numeric_Year"], inplace=True)

# 保存结果
formatted_df.to_excel("formatted_data.xlsx", index=False)
print(f"数据处理完成，已保存为 formatted_data.xlsx")
print(f"\n数据统计:")
print(f"总行数: {len(formatted_df)}")
print(f"公司数量: {len(formatted_df['Company'].unique())}")
print(f"季度范围: {formatted_df['Quarter'].min()} 到 {formatted_df['Quarter'].max()}")

# 打印调试信息
print(f"\n调试信息:")
print(f"Revenue Growth YoY 起始行: {revenue_growth_start}")
print(f"EBITDA Margin 起始行: {ebitda_margin_start}")