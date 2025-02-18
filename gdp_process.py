import pandas as pd

# 读取 CSV 文件
file_path = "API_NY.GDP.MKTP.CD_DS2_zh_csv_v2_285.csv"
df = pd.read_csv(file_path, skiprows=4)  # 跳过元数据行

# 选择需要的列
df = df[['Country Name', '2005', '2006', '2007', '2008', '2009']]
df.iloc[:, 1:] = df.iloc[:, 1:].apply(pd.to_numeric, errors='coerce')

# 用户需要的国家/地区列表
user_countries = [
    "Argentina", "Australia-New Zealand", "Brazil", "Bulgaria", "Canada", "Chile", "China",
    "Colombia", "Czech Republic", "Egypt", "France", "Germany", "Greece", "Hong Kong", "Hungary",
    "India", "Indonesia", "Italy", "Japan", "Macau", "Malaysia", "Mexico", "Poland", "Qatar",
    "Rest of Eastern Europe", "Rest of Europe", "Rest of Middle East", "Romania", "Russia",
    "Saudi Arabia", "Scandinavia", "Singapore", "South Korea", "Spain", "Taiwan", "Thailand",
    "U.A.E.", "U.K.", "U.S.", "Ukraine"
]

# 世界银行数据中的名称映射
country_mapping = {
    "Argentina": "阿根廷",
    "Australia-New Zealand": ["澳大利亚", "新西兰"],
    "Brazil": "巴西",
    "Bulgaria": "保加利亚",
    "Canada": "加拿大",
    "Chile": "智利",
    "China": "中国",
    "Colombia": "哥伦比亚",
    "Czech Republic": "捷克共和国",
    "Egypt": "阿拉伯埃及共和国",
    "France": "法国",
    "Germany": "德国",
    "Greece": "希腊",
    "Hong Kong": "中国香港特别行政区",
    "Hungary": "匈牙利",
    "India": "印度",
    "Indonesia": "印度尼西亚",
    "Italy": "意大利",
    "Japan": "日本",
    "Macau": "中国澳门特别行政区",
    "Malaysia": "马来西亚",
    "Mexico": "墨西哥",
    "Poland": "波兰",
    "Qatar": "卡塔尔",
    "Rest of Eastern Europe": ["保加利亚", "罗马尼亚", "匈牙利", "捷克共和国", "波兰"],
    "Rest of Europe": ["法国", "德国", "意大利", "西班牙", "英国", "荷兰"],
    "Rest of Middle East": ["沙特阿拉伯", "阿拉伯联合酋长国", "卡塔尔"],
    "Romania": "罗马尼亚",
    "Russia": "俄罗斯联邦",
    "Saudi Arabia": "沙特阿拉伯",
    "Scandinavia": ["丹麦", "挪威", "瑞典"],
    "Singapore": "新加坡",
    "South Korea": "大韩民国",
    "Spain": "西班牙",
    "Taiwan": "台湾",  # 台湾可能不会出现在世界银行数据中
    "Thailand": "泰国",
    "U.A.E.": "阿拉伯联合酋长国",
    "U.K.": "英国",
    "U.S.": "美国",
    "Ukraine": "乌克兰"
}

# 处理数据匹配
processed_data = []
for user_country, wb_country in country_mapping.items():
    if isinstance(wb_country, list):
        subset = df[df['Country Name'].isin(wb_country)]
        summed_values = subset.iloc[:, 1:].sum()
        processed_data.append([user_country] + summed_values.tolist())
    else:
        subset = df[df['Country Name'] == wb_country]
        if not subset.empty:
            processed_data.append([user_country] + subset.iloc[0, 1:].tolist())
        else:
            processed_data.append([user_country] + [None] * 5)

# 转换为 DataFrame
df_final = pd.DataFrame(processed_data, columns=["Country", "2005", "2006", "2007", "2008", "2009"])

# 转换 GDP 数据为整数，并确保 NaN 变为 ""
df_final.iloc[:, 1:] = df_final.iloc[:, 1:].applymap(lambda x: str(int(x)) if pd.notna(x) else "")

# 导出到 CSV 文件（无索引、无列名）
output_path = "/Users/liugan/Library/CloudStorage/OneDrive-Personal/Files/000_Archive/TravelMarketViz/gdp_cleaned_integer.csv"
df_final.to_csv(output_path, index=False, header=False)

print(f"GDP 数据整理完成，已保存至 {output_path}")
