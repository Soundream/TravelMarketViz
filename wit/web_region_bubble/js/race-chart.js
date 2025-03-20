function createRaceChart(data, year) {
    // 计算所有年份的最大值，用于固定坐标轴范围
    const maxValue = Math.max(...data.map(d => d['Gross Bookings'] * appConfig.dataProcessing.bookingsScaleFactor));
    // 确保最大值至少是200，防止小值情况下空间太小
    const axisMaxValue = Math.max(maxValue, 200);

    // 按区域分组并计算总预订量
    const yearData = data.filter(d => d.Year === year);

    // 创建条形图数据
    const barData = {
        type: 'bar',
        x: [],
        y: [],
        orientation: 'h',
        marker: {
            color: [],
            width: 0.6 // 减小柱子的宽度
        },
        text: [],
        textposition: 'outside',
        hoverinfo: 'text',
        texttemplate: '%{text:$.1f}B',
        textfont: {
            family: 'Monda',
            size: 16
        },
        cliponaxis: false // 防止数据点被裁切
    };

    // 处理数据
    const sortedData = yearData
        .map(d => ({
            region: d.Region,
            value: d['Gross Bookings'] * appConfig.dataProcessing.bookingsScaleFactor,
            color: appConfig.regionColors[d.Region]
        }))
        .sort((a, b) => a.value - b.value);

    // 填充图表数据
    barData.y = sortedData.map((d, i) => i.toString()); // Using indices instead of region names
    barData.x = sortedData.map(d => d.value);
    barData.marker.color = sortedData.map(d => d.color);
    barData.text = sortedData.map(d => d.value);

    // 创建布局
    const layout = {
        title: {
            text: '',  // 移除标题
            font: {
                family: 'Monda',
                size: 16
            },
            y: 0.95
        },
        xaxis: {
            title: {
                text: 'Gross Bookings (USD bn)',
                font: {
                    family: 'Monda',
                    size: 20
                },
                standoff: 15
            },
            showgrid: true,
            gridcolor: '#eee',
            gridwidth: 1,
            zeroline: true,
            zerolinecolor: '#eee',
            tickfont: {
                family: 'Monda',
                size: 16
            },
            range: [0, axisMaxValue * 1.2],  // 增加范围系数，确保能显示所有数值
            fixedrange: true,  // 固定范围，防止自动调整
            ticks: 'outside',
            ticklen: 8,
            tickwidth: 1,
            tickcolor: '#ccc',
            tickprefix: '  ',  // 为刻度值添加前缀空格，避免刻度值被裁切
            automargin: true   // 允许自动调整边距以适应轴标签
        },
        yaxis: {
            showgrid: false,
            showticklabels: false, // Hide y-axis tick labels completely
            fixedrange: true,  // 固定范围，防止自动调整
        },
        margin: {
            l: 5, // 增加左边距，防止零刻度被裁切
            r: 60, // 进一步增加右边距，确保'B'后缀完全显示
            t: -20,  // 使用负值来减少与上方地图的距离
            b: 60 // 保持底部边距以适应更大的字体
        },
        width: 350, // 保持图表宽度
        height: 300,
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        showlegend: false,
        barmode: 'group',
        bargap: 0.1, // 减小柱子之间的间距
        bargroupgap: 0.05, // 减小组之间的间距
        font: {
            family: 'Monda'
        },
        annotations: [] // 删除所有注释
    };

    // 创建配置
    const config = {
        displayModeBar: false,
        responsive: true,
        staticPlot: true
    };

    // 渲染图表
    Plotly.newPlot('race-chart', [barData], layout, config);
}

// 更新race chart的函数
function updateRaceChart(data, year) {
    const yearData = data.filter(d => d.Year === year);
    
    // 获取当前最大值
    const maxValue = Math.max(...yearData.map(d => d['Gross Bookings'] * appConfig.dataProcessing.bookingsScaleFactor));
    // 确保最大值至少是200，防止小值情况下空间太小
    const axisMaxValue = Math.max(maxValue, 200);
    
    // 处理数据
    const sortedData = yearData
        .map(d => ({
            region: d.Region,
            value: d['Gross Bookings'] * appConfig.dataProcessing.bookingsScaleFactor,
            color: appConfig.regionColors[d.Region]
        }))
        .sort((a, b) => a.value - b.value);

    // 准备更新数据
    const updateData = {
        y: [sortedData.map((d, i) => i.toString())], // Using indices instead of region names
        x: [sortedData.map(d => d.value)],
        'marker.color': [sortedData.map(d => d.color)],
        text: [sortedData.map(d => d.value)],
        cliponaxis: false // 防止数据点被裁切
    };
    
    // 更新坐标轴范围和边距
    const updateLayout = {
        'xaxis.range': [0, axisMaxValue * 1.2],
        'margin.r': 60 // 确保右侧边距足够显示完整的文本
    };

    // 更新数据和布局
    Plotly.restyle('race-chart', updateData);
    Plotly.relayout('race-chart', updateLayout);
} 