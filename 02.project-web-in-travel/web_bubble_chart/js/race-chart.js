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
            color: [],
        },
        text: [],
        textposition: 'outside',
        hoverinfo: 'text',
        texttemplate: '%{text:$.1f}B',
        textfont: {
            family: 'Monda',
            size: 12
        },
        cliponaxis: false  // 防止文本被裁剪
    };

    // 处理数据
    const sortedData = yearData
        .map(d => ({
            market: appConfig.countryCodes[d.Market] || d.Market,
            value: d.GrossBookings * appConfig.dataProcessing.bookingsScaleFactor,
            color: appConfig.colorDict[d.Market]
        }))
        .sort((a, b) => a.value - b.value);

    // 填充图表数据
    barData.y = sortedData.map(d => d.market);
    barData.x = sortedData.map(d => d.value);
    barData.marker.color = sortedData.map(d => d.color);
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
                    size: 12
                },
                standoff: 10
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
            range: [0, maxValue * 1.2],
            fixedrange: true
        },
        yaxis: {
            showgrid: false,
            tickfont: {
                family: 'Monda',
                size: 10
            },
            fixedrange: true,
            ticklabelposition: 'outside left'
        },
        margin: {
            l: 120,
            r: 0,
            t: -20,
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
        },
        updatemenus: [{
            type: 'buttons',
            showactive: false,
            visible: false
        }]
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
        .map(d => ({
            market: appConfig.countryCodes[d.Market] || d.Market,
            value: d.GrossBookings * appConfig.dataProcessing.bookingsScaleFactor,
            color: appConfig.colorDict[d.Market]
        }))
        .sort((a, b) => a.value - b.value);

    // 创建新的数据帧
    const newFrame = {
        data: [{
            y: sortedData.map(d => d.market),
            x: sortedData.map(d => d.value),
            marker: {
                color: sortedData.map(d => d.color)
            },
            text: sortedData.map(d => d.value),
            texttemplate: '%{text:$.1f}B',
            textposition: 'outside'
        }]
    };

    // 使用 Plotly.animate 来实现平滑过渡
    Plotly.animate('race-chart', newFrame, {
        transition: {
            duration: 0,  // 设置为0以实现实时更新
            easing: 'linear'
        },
        frame: {
            duration: 0,
            redraw: true
        }
    });
} 