function createRaceChart(data, year) {
    // 计算所有年份的最大值，用于固定坐标轴范围
    const maxValue = Math.max(...data.map(d => {
        const bookings = parseFloat(d['Gross Bookings']) || 0;
        return bookings * (appConfig.dataProcessing?.bookingsScaleFactor || 1e-9);
    }));

    // 保存全局最大值供后续使用
    window.globalMaxValue = maxValue;

    // 按国家分组并计算总预订量
    const yearData = data.filter(d => d.Year === year);

    // 创建条形图数据
    const baseTrace = {
        type: 'bar',
        orientation: 'h',
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
        width: Array(15).fill(0.25)
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
        .sort((a, b) => b.value - a.value)
        .slice(0, 15);

    // 填充图表数据
    const barData = {
        ...baseTrace,
        y: sortedData.map(d => d.market),
        x: sortedData.map(d => d.value),
        marker: {
            color: sortedData.map(d => d.color)
        },
        text: sortedData.map(d => d.value)
    };

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

    // 保存当前数据和布局用于插值
    window.currentRaceData = sortedData;
    window.raceChartLayout = layout;
    window.baseTrace = baseTrace;
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

    // 创建动画帧
    const frameCount = 30;
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
                ...window.baseTrace,
                y: interpolatedData.map(d => d.market),
                x: interpolatedData.map(d => d.value),
                marker: {
                    color: interpolatedData.map(d => d.color)
                },
                text: interpolatedData.map(d => d.value.toFixed(1))
            }],
            layout: window.raceChartLayout
        });
    }

    // 执行动画
    Plotly.animate('race-chart', frames, {
        transition: {
            duration: 800 / frameCount,
            easing: 'linear'
        },
        frame: {
            duration: 800 / frameCount,
            redraw: false
        },
        mode: 'immediate'
    });

    // 更新当前数据
    window.currentRaceData = targetData;
} 