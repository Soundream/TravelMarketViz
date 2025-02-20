function createRaceChart(data, year) {
    // 计算所有年份的最大值，用于固定坐标轴范围
    const maxValue = Math.max(...data.map(d => {
        const bookings = parseFloat(d['Gross Bookings']) || 0;
        return bookings * (appConfig.dataProcessing?.bookingsScaleFactor || 1e-9);
    }));

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
            size: 11
        },
        cliponaxis: false,
        textangle: 0,
        outsidetextfont: {
            family: 'Monda',
            size: 11
        },
        offsetgroup: 1,
        textoffset: 12,
        width: Array(15).fill(0.35) // 减小柱子高度
    };

    // 处理数据
    const sortedData = yearData
        .map(d => {
            const market = d.Market;
            const bookings = parseFloat(d['Gross Bookings']) || 0;
            return {
                market: appConfig.countryCodes?.[market] || market,
                originalMarket: market,
                value: bookings * (appConfig.dataProcessing?.bookingsScaleFactor || 1e-9),
                color: (appConfig.colorDict?.[market] || appConfig.regionColors?.[d.Region] || '#999999'),
                region: d.Region
            };
        })
        .sort((a, b) => b.value - a.value) // 降序排序
        .slice(0, 15); // 只取前15个国家

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
            }
        },
        xaxis: {
            title: {
                text: 'Gross Bookings (USD bn)',
                font: {
                    family: 'Monda',
                    size: 12
                },
                standoff: 20
            },
            showgrid: true,
            gridcolor: '#eee',
            gridwidth: 1,
            zeroline: true,
            zerolinecolor: '#eee',
            tickfont: {
                family: 'Monda',
                size: 11
            },
            range: [0, maxValue * 1.15],
            fixedrange: true,
            ticklen: 6,
            ticksuffix: ' '
        },
        yaxis: {
            showgrid: false,
            tickfont: {
                family: 'Monda',
                size: 11
            },
            fixedrange: true,
            ticklabelposition: 'outside left',
            automargin: true,
            range: [-0.5, 14.5],
            dtick: 1
        },
        margin: {
            l: 90,
            r: 90,
            t: 10,
            b: 35
        },
        height: 380,
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        showlegend: false,
        barmode: 'group',
        bargap: 0.05,
        bargroupgap: 0.01,
        font: {
            family: 'Monda'
        },
        uniformtext: {
            mode: 'hide',
            minsize: 11
        }
    };

    // 创建配置
    const config = {
        displayModeBar: false,
        responsive: true,
        staticPlot: false
    };

    // 渲染图表
    Plotly.newPlot('race-chart', [barData], layout, config);

    // 保存当前数据用于插值
    window.currentRaceData = sortedData;
}

// 更新race chart的函数
function updateRaceChart(data, year) {
    const yearData = data.filter(d => d.Year === year);
    
    // 处理目标数据
    const targetData = yearData
        .map(d => {
            const market = d.Market;
            const bookings = parseFloat(d['Gross Bookings']) || 0;
            return {
                market: appConfig.countryCodes?.[market] || market,
                originalMarket: market,
                value: bookings * (appConfig.dataProcessing?.bookingsScaleFactor || 1e-9),
                color: (appConfig.colorDict?.[market] || appConfig.regionColors?.[d.Region] || '#999999'),
                region: d.Region
            };
        })
        .sort((a, b) => b.value - a.value)
        .slice(0, 15);

    // 获取当前数据
    const currentData = window.currentRaceData || targetData;
    
    // 更新布局
    Plotly.relayout('race-chart', {
        bargap: 0.05,
        bargroupgap: 0.01
    });

    // 创建动画帧
    const frameCount = 60;
    const frames = [];
    
    for (let i = 0; i <= frameCount; i++) {
        const progress = i / frameCount;
        
        const interpolatedData = targetData.map(target => {
            const current = currentData.find(c => c.originalMarket === target.originalMarket) || target;
            const value = current.value + (target.value - current.value) * progress;
            return {
                ...target,
                value: value
            };
        }).sort((a, b) => b.value - a.value);

        frames.push({
            data: [{
                y: interpolatedData.map(d => d.market),
                x: interpolatedData.map(d => d.value),
                marker: {
                    color: interpolatedData.map(d => d.color)
                },
                text: interpolatedData.map(d => d.value.toFixed(1)),
                width: Array(15).fill(0.25)  // 进一步减小柱子高度
            }]
        });
    }

    // 执行动画
    Plotly.animate('race-chart', frames, {
        transition: {
            duration: 1000 / frameCount,
            easing: 'cubic-in-out'
        },
        frame: {
            duration: 1000 / frameCount,
            redraw: false
        },
        mode: 'immediate'
    });

    // 更新当前数据
    window.currentRaceData = targetData;
} 