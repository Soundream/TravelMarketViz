function createRaceChart(data, year) {
    // 计算所有年份的最大值，用于固定坐标轴范围
    const maxValue = Math.max(...data.map(d => d['Gross Bookings'] * appConfig.dataProcessing.bookingsScaleFactor));

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
        },
        text: [],
        textposition: 'outside',
        hoverinfo: 'text',
        texttemplate: '%{text:$.1f}B',
        textfont: {
            family: 'Monda',
            size: 12
        }
    };

    // 处理数据
    const sortedData = yearData
        .map(d => ({
            region: d.Region,
            value: d['Gross Bookings'] * appConfig.dataProcessing.bookingsScaleFactor,
            color: appConfig.regionColors[d.Region]
        }))
        .sort((a, b) => b.value - a.value);

    // 填充图表数据
    barData.y = sortedData.map(d => d.region);
    barData.x = sortedData.map(d => d.value);
    barData.marker.color = sortedData.map(d => d.color);
    barData.text = sortedData.map(d => d.value);

    // 创建布局
    const layout = {
        title: {
            text: 'Gross Bookings by Region',
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
                    size: 12
                }
            },
            showgrid: true,
            gridcolor: '#eee',
            gridwidth: 1,
            zeroline: true,
            zerolinecolor: '#eee',
            tickfont: {
                family: 'Monda',
                size: 10
            },
            range: [0, maxValue * 1.1],  // 使用全局最大值设置固定范围
            fixedrange: true  // 固定范围，防止自动调整
        },
        yaxis: {
            showgrid: false,
            tickfont: {
                family: 'Monda',
                size: 10
            },
            fixedrange: true  // 固定范围，防止自动调整
        },
        margin: {
            l: 120,
            r: 60,
            t: 40,
            b: 30
        },
        height: 300,
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        showlegend: false,
        barmode: 'group',
        bargap: 0.15,
        font: {
            family: 'Monda'
        }
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
    
    // 处理数据
    const sortedData = yearData
        .map(d => ({
            region: d.Region,
            value: d['Gross Bookings'] * appConfig.dataProcessing.bookingsScaleFactor,
            color: appConfig.regionColors[d.Region]
        }))
        .sort((a, b) => b.value - a.value);

    // 准备更新数据
    const updateData = {
        y: [sortedData.map(d => d.region)],
        x: [sortedData.map(d => d.value)],
        'marker.color': [sortedData.map(d => d.color)],
        text: [sortedData.map(d => d.value)]
    };

    // 使用Plotly.restyle而不是animate来更新数据
    Plotly.restyle('race-chart', updateData);
} 