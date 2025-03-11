function createRaceChart(data, year) {
    // 计算所有年份的最大值，用于固定坐标轴范围
    const maxValue = Math.max(...data.map(d => d.GrossBookings * appConfig.dataProcessing.bookingsScaleFactor));

    // 按国家分组并计算总预订量
    const yearData = data.filter(d => d.Year === year);

    // 创建条形图数据
    const barData = {
        type: 'bar',
        x: [],
        y: [],
        orientation: 'h',
        marker: {
            color: 'rgb(255, 75, 75)',  // 设置所有bar的颜色
        },
        text: [],
        textposition: 'outside',
        hoverinfo: 'text',
        texttemplate: '%{text:$.1f}B',
        textfont: {
            family: 'Monda',
            size: 14  // 统一文本大小
        },
        cliponaxis: false,  // 防止文本被裁剪
        textangle: 0,
        outsidetextfont: {
            family: 'Monda',
            size: 14  // 统一文本大小
        },
        textoffset: 15  // 统一文本偏移量
    };

    // 处理数据
    const sortedData = yearData
        .map(d => ({
            market: d.Market,
            code: appConfig.countryCodes[d.Market] || d.Market,
            value: d.GrossBookings * appConfig.dataProcessing.bookingsScaleFactor
        }))
        .sort((a, b) => a.value - b.value);

    // 填充图表数据
    barData.y = sortedData.map(d => d.code);
    barData.x = sortedData.map(d => d.value);
    barData.text = sortedData.map(d => d.value);

    // 创建布局
    const layout = {
        title: {
            text: '',
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
            ticklabelposition: 'outside left',
            ticktext: sortedData.map(d => d.code),  // 使用国家代码
            tickmode: 'array',
            tickvals: Array.from({length: sortedData.length}, (_, i) => i)
        },
        margin: {
            l: 120,
            r: 100,  // 进一步增加右边距
            t: 20,   // 增加顶部边距
            b: 60    // 增加底部边距给x轴标题和标签留出空间
        },
        height: 400,
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        showlegend: false,
        barmode: 'group',
        bargap: 0.25,
        font: {
            family: 'Monda'
        },
        updatemenus: [{
            type: 'buttons',
            showactive: false,
            visible: false
        }],
        images: sortedData.map((d, i) => ({
            source: `flags/${d.code} Icon.png`,  // 使用国家代码
            x: -0.15,  // 调整图标位置
            y: i,
            xref: 'paper',
            yref: 'y',
            sizex: 0.1,
            sizey: 0.8,
            xanchor: 'right',
            yanchor: 'middle'
        }))
    };

    // 创建配置
    const config = {
        displayModeBar: false,
        responsive: true,
        staticPlot: false  // 改为 false 以支持动画
    };

    // 渲染图表
    Plotly.newPlot('race-chart', [barData], layout, config);
}

// 更新race chart的函数
function updateRaceChart(data, year) {
    // 处理数据
    const sortedData = data
        .filter(d => d.Year === year)
        .map(d => ({
            market: d.Market,
            code: appConfig.countryCodes[d.Market] || d.Market,
            value: d.GrossBookings * appConfig.dataProcessing.bookingsScaleFactor
        }))
        .sort((a, b) => a.value - b.value);

    // 使用 Plotly.restyle 而不是 animate 来更新数据
    Plotly.restyle('race-chart', {
        'y': [sortedData.map(d => d.code)],
        'x': [sortedData.map(d => d.value)],
        'text': [sortedData.map(d => d.value)],
        'marker.color': 'rgb(255, 75, 75)'  // 确保更新时也设置统一的颜色
    });

    // 更新y轴标签和图片
    Plotly.relayout('race-chart', {
        'yaxis.ticktext': sortedData.map(d => d.code),
        'images': sortedData.map((d, i) => ({
            source: `flags/${d.code} Icon.png`,
            x: -0.15,
            y: i,
            xref: 'paper',
            yref: 'y',
            sizex: 0.1,
            sizey: 0.8,
            xanchor: 'right',
            yanchor: 'middle'
        }))
    });
} 