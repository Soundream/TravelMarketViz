function createRaceChart(data, year) {
    // 国旗映射
    const flagMapping = {
        'China': 'cn.svg',
        'U.S.': 'us.svg',
        'U.K.': 'gb.svg',
        'Japan': 'jp.svg',
        'Germany': 'de.svg',
        'France': 'fr.svg',
        'South Korea': 'kr.svg',
        'India': 'in.svg',
        'Brazil': 'br.svg',
        'Italy': 'it.svg',
        'Canada': 'ca.svg',
        'Russia': 'ru.svg',
        'Australia': 'au.svg',
        'Spain': 'es.svg',
        'Mexico': 'mx.svg',
        'Indonesia': 'id.svg',
        'Netherlands': 'nl.svg',
        'Turkey': 'tr.svg',
        'Switzerland': 'ch.svg',
        'Saudi Arabia': 'sa.svg',
        'Thailand': 'th.svg',
        'Singapore': 'sg.svg',
        'Malaysia': 'my.svg',
        'Hong Kong': 'hk.svg',
        'Taiwan': 'tw.svg'
    };

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
            size: 11,
            color: '#333'
        },
        cliponaxis: false,
        textangle: 0,
        offsetgroup: 1,
        width: 0.6,
        constraintext: 'none'
    };

    // 处理数据
    const sortedData = yearData
        .map(d => ({
            market: d.Market,
            value: d.GrossBookings * appConfig.dataProcessing.bookingsScaleFactor,
            color: appConfig.colorDict[d.Market] || '#999999',
            region: d.Region
        }))
        .sort((a, b) => b.value - a.value)
        .slice(0, 15);

    // 填充图表数据
    barData.x = sortedData.map(d => d.value);
    barData.y = sortedData.map(d => d.market);
    barData.marker.color = sortedData.map(d => d.color);
    barData.text = sortedData.map(d => d.value.toFixed(1));

    // 创建布局
    const layout = {
        width: 450,
        height: 400,
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
            range: [0, maxValue * 1.3],
            fixedrange: true,
            ticklen: 6,
            ticksuffix: '   ',
            automargin: true
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
            dtick: 1,
            ticktext: sortedData.map(d => flagMapping[d.market] ? '' : d.market),
            tickmode: 'array',
            tickvals: Array.from({length: sortedData.length}, (_, i) => i),
            ticklabelposition: 'inside',
            autorange: 'reversed'
        },
        images: sortedData.map((d, i) => ({
            source: flagMapping[d.market] ? 'flags/' + flagMapping[d.market] : null,
            xref: 'paper',
            yref: 'y',
            x: -0.15,
            y: i,
            sizex: 0.25,
            sizey: 1.2,
            xanchor: 'right',
            yanchor: 'middle',
            visible: flagMapping[d.market] ? true : false
        })),
        margin: {
            l: 120,
            r: 120,
            t: 40,
            b: 50,
            autoexpand: false
        },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        showlegend: false,
        barmode: 'group',
        bargap: 0.2,
        bargroupgap: 0.1,
        font: {
            family: 'Monda'
        },
        uniformtext: {
            mode: 'show',
            minsize: 10
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
    window.baseTrace = barData;
}

function updateRaceChart(data, year) {
    // 获取当前和目标年份的数据
    const currentData = window.currentRaceData;
    const yearData = data.filter(d => d.Year === year);

    // 处理目标数据
    const targetData = yearData
        .map(d => ({
            market: d.Market,
            value: d.GrossBookings * appConfig.dataProcessing.bookingsScaleFactor,
            color: appConfig.colorDict[d.Market] || '#999999',
            region: d.Region
        }))
        .sort((a, b) => b.value - a.value)
        .slice(0, 15);

    // 创建插值帧
    const numFrames = 30;
    const frames = [];

    for (let i = 0; i <= numFrames; i++) {
        const t = i / numFrames;
        
        // 创建当前帧的数据
        const frameData = targetData.map((target, idx) => {
            const current = currentData[idx] || { value: 0, market: target.market, color: target.color };
            return {
                market: target.market,
                value: current.value + (target.value - current.value) * t,
                color: target.color
            };
        });

        // 排序以保持顺序一致性
        frameData.sort((a, b) => b.value - a.value);

        // 创建帧
        frames.push({
            data: [{
                ...window.baseTrace,
                y: frameData.map(d => d.market),
                x: frameData.map(d => d.value),
                marker: {
                    color: frameData.map(d => d.color)
                },
                text: frameData.map(d => d.value.toFixed(1))
            }]
        });
    }

    // 使用 Plotly.animate 播放动画帧
    Plotly.animate('race-chart', frames, {
        transition: {
            duration: appConfig.animation.duration / numFrames,
            easing: 'cubic-in-out'
        },
        frame: {
            duration: appConfig.animation.duration / numFrames,
            redraw: true
        },
        mode: 'immediate'
    });

    // 更新当前数据
    window.currentRaceData = targetData;
} 