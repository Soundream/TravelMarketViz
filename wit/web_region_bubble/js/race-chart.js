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
            size: 14
        },
        cliponaxis: false,  // 防止文本被裁剪
        textangle: 0,
        outsidetextfont: {
            family: 'Monda',
            size: 14
        },
        offsetgroup: 1,
        textoffset: 15
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
    barData.y = sortedData.map(d => d.region);
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
                    size: 14
                },
                standoff: 30  // 增加标题与轴的距离
            },
            showgrid: true,
            gridcolor: '#eee',
            gridwidth: 1,
            zeroline: true,
            zerolinecolor: '#eee',
            tickfont: {
                family: 'Monda',
                size: 13
            },
            range: [0, maxValue * 1.3],  // 增加范围给标签留出更多空间
            fixedrange: true,
            ticklen: 10,  // 增加刻度线长度
            ticksuffix: '   '  // 在刻度标签后添加空格
        },
        yaxis: {
            showgrid: false,
            tickfont: {
                family: 'Monda',
                size: 13
            },
            fixedrange: true,
            ticklabelposition: 'outside left'
        },
        margin: {
            l: 120,
            r: 100,  // 增加右边距
            t: 20,   // 增加顶部边距
            b: 60    // 增加底部边距
        },
        height: 300,  // 恢复原有高度
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        showlegend: false,
        barmode: 'group',
        bargap: 0.25,
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
        .sort((a, b) => a.value - b.value);

    // 准备更新数据
    const updateData = {
        y: [sortedData.map(d => d.region)],
        x: [sortedData.map(d => d.value)],
        'marker.color': [sortedData.map(d => d.color)],
        text: [sortedData.map(d => d.value)],
        texttemplate: ['%{text:$.1f}B'],
        textposition: ['outside'],
        textfont: [{
            family: 'Monda',
            size: 14
        }],
        cliponaxis: [false],
        textangle: [0],
        outsidetextfont: [{
            family: 'Monda',
            size: 14
        }],
        offsetgroup: [1],
        textoffset: [15]
    };

    // 使用Plotly.restyle来更新数据
    Plotly.restyle('race-chart', updateData);
} 