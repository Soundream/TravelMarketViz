import pandas as pd
import plotly.graph_objects as go

# 读取 Excel 文件
df = pd.read_excel('utilities/travel_market_summary.xlsx', sheet_name='Visualization Data')

# 筛选美国和加拿大的数据
na_data = df[df['Market'].isin(['U.S.', 'Canada'])]

# 按年份计算总和
yearly_total = na_data.groupby('Year')['Gross Bookings'].sum().reset_index()

# 将数据转换为十亿美元单位
yearly_total['Gross Bookings'] = yearly_total['Gross Bookings'] / 1e9

# 创建图表
fig = go.Figure()

# 添加总量数据
fig.add_trace(
    go.Scatter(
        x=yearly_total['Year'],
        y=yearly_total['Gross Bookings'],
        name='Total North America',
        mode='lines+markers',
        line=dict(width=3, color='#003480'),
        marker=dict(size=8, color='#003480')
    )
)

# 更新布局
fig.update_layout(
    title={
        'text': 'North America Total Travel Market Gross Bookings',
        'y': 0.95,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': dict(family='Monda', size=24)
    },
    xaxis_title='Year',
    yaxis_title='Gross Bookings (USD Billion)',
    font=dict(family='Monda'),
    plot_bgcolor='white',
    hovermode='x',
    showlegend=False,
    width=1000,
    height=600
)

# 更新坐标轴
fig.update_xaxes(
    showgrid=True,
    gridwidth=1,
    gridcolor='#eee',
    tickfont=dict(family='Monda', size=12)
)

fig.update_yaxes(
    showgrid=True,
    gridwidth=1,
    gridcolor='#eee',
    tickfont=dict(family='Monda', size=12)
)

# 添加悬停模板
fig.update_traces(
    hovertemplate='<b>%{x}</b><br>' +
                  'Total Gross Bookings: $%{y:.1f}B<br>'
)

# 显示图表
fig.show()

# 保存为HTML文件
fig.write_html('north_america_total_gross_bookings.html')