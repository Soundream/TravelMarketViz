import pandas as pd

def main():
    # 输入、输出文件名和目标 sheet
    input_file = 'travel_market_summary.xlsx'
    output_file = 'travel_market_summary_cleaned.xlsx'
    sheet_name = 'Visualization Data'

    # 1. 读取数据
    df = pd.read_excel(input_file, sheet_name=sheet_name)

    # 2. 打印原始信息
    total_rows = len(df)
    unique_combos = df.drop_duplicates(subset=['Year', 'Market']).shape[0]
    print(f'原始总行数：{total_rows}')
    print(f'唯一 (Year, Market) 组合数：{unique_combos}\n')

    # 找出所有重复项（出现超过 1 次的 Year+Market）
    dup = df[df.duplicated(subset=['Year', 'Market'], keep=False)]
    if not dup.empty:
        print('以下是重复的记录（按 Year, Market 排序）：')
        print(dup.sort_values(['Year', 'Market']), '\n')
    else:
        print('没有发现重复的 Year+Market 组合。\n')

    # 3. 去重（保留第一次出现）
    df_clean = df.drop_duplicates(subset=['Year', 'Market'], keep='first')

    # 4. 写入新的 Excel，并保留其它 sheet
    #    需要安装 openpyxl：pip install openpyxl
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # 写入清洗后的 Visualization Data
        df_clean.to_excel(writer, sheet_name=sheet_name, index=False)
        # 复制其它所有 sheet
        xls = pd.ExcelFile(input_file)
        for s in xls.sheet_names:
            if s == sheet_name:
                continue
            pd.read_excel(input_file, sheet_name=s).to_excel(writer, sheet_name=s, index=False)

    print(f'清洗后的数据已保存到：{output_file}\n')

    # 5. 按 Year 汇总 Gross Bookings
    agg = df_clean.groupby('Year', as_index=False)['Gross Bookings'].sum()
    print('按年份汇总后的 Gross Bookings：')
    print(agg)

if __name__ == '__main__':
    main()
