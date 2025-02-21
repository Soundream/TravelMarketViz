function createRaceChart(data, year) {
    // 首先列出所有需要的国旗
    console.log('\n=== Required Flags List ===');
    const allMarkets = [...new Set(data.map(d => d.Market))].sort();
    console.log('All markets in data:', allMarkets.join(', '));
    console.log('\nFlags needed:');
    allMarkets.forEach(market => {
        console.log(`'${market}': '${market} Icon.png',`);
    });
    console.log('=== End of Flags List ===\n');

    // 添加国旗映射
    const flagMapping = {
        'Japan': 'Japan Icon.png',
        'China': 'China Icon.png',
        'Russia': 'Russia Icon.png',
        'Hong Kong': 'Hong Kong Icon.png',
        'U.K.': 'UK Icon.png',
        'Chile': 'Chile Icon.png',
        'U.S.': 'USA Icon.png',
        'Brazil': 'Brazil Icon.png',
        'Colombia': 'Colombia Icon.png',
        'Spain': 'Spain Icon.png',
        'Mexico': 'Mexico Icon.png',
        'Canada': 'Canada Icon.png',
        'U.A.E.': 'UAE Icon.png',
        'Australia-New Zealand': 'Australia Icon.png',
        'France': 'France Icon.png',
        'Germany': 'Germany Icon.png',
        'Italy': 'Italy Icon.png',
        'Rest of Europe': 'Europe Icon.png',
        'India': 'India Icon.png',
        'Scandinavia': 'Sweden Icon.png'
    };

    // 添加国家代码映射
    const countryCodeMapping = {
        'Japan': 'JPN',
        'China': 'CHN',
        'Russia': 'RUS',
        'Hong Kong': 'HKG',
        'U.K.': 'GBR',
        'Chile': 'CHL',
        'U.S.': 'USA',
        'Brazil': 'BRA',
        'Colombia': 'COL',
        'Spain': 'ESP',
        'Mexico': 'MEX',
        'Canada': 'CAN',
        'U.A.E.': 'UAE',
        'Australia-New Zealand': 'AUS',
        'India': 'IND',
        'Singapore': 'SGP',
        'Indonesia': 'IDN',
        'Malaysia': 'MYS',
        'Thailand': 'THA',
        'Taiwan': 'TWN',
        'France': 'FRA',
        'Germany': 'DEU',
        'Italy': 'ITA',
        'South Korea': 'KOR',
        'Rest of Europe': 'EUR'
    };

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
        texttemplate: '%{text}B',
        textfont: {
            family: 'Monda',
            size: 11,
            color: '#333'
        },
        cliponaxis: false,
        textangle: 0,
        offsetgroup: 1,
        width: 0.6,
        constraintext: false,
        outsidetextfont: {
            family: 'Monda',
            size: 11,
            color: '#333'
        }
    };

    // 处理数据
    const sortedData = yearData
        .map(d => {
            const market = d.Market;
            const bookings = parseFloat(d['Gross Bookings']) || 0;
            const penetration = parseFloat(d['Online Penetration']) || 0;
            
            // 检查并输出没有国旗的国家
            if (!flagMapping[market]) {
                console.log('Missing flag for country:', market);
            }

            return {
                market: market,
                originalMarket: market,
                value: bookings * (appConfig.dataProcessing?.bookingsScaleFactor || 1e-9),
                penetration: penetration,
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
        text: sortedData.map(d => d.value.toFixed(1)),
        textposition: 'outside',
        hovertemplate: '%{y}<br>Gross Bookings: $%{x:.1f}B<extra></extra>'
    };

    // 添加在线渗透率数据
    const penetrationData = {
        type: 'scatter',
        mode: 'text',
        x: Array(sortedData.length).fill(-0.5),  // 放在条形图左侧
        y: sortedData.map(d => d.market),
        text: sortedData.map(d => `${(d.penetration * 100).toFixed(1)}%`),
        textposition: 'middle left',
        textfont: {
            family: 'Monda',
            size: 11,
            color: '#666'
        },
        hoverinfo: 'none',
        showlegend: false
    };

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
            range: [-1, maxValue * 1.4],  // 增加空间以显示数值
            fixedrange: true,
            ticklen: 6,
            ticksuffix: ' ',
            automargin: true,
            layer: 'below traces'  // 确保轴线在数据下方
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
            ticktext: sortedData.map(d => flagMapping[d.originalMarket] ? '' : (countryCodeMapping[d.originalMarket] || d.originalMarket)),
            tickmode: 'array',
            tickvals: Array.from({length: sortedData.length}, (_, i) => i),
            ticklabelposition: 'inside',
            autorange: 'reversed',
            layer: 'below traces'  // 确保轴线在数据下方
        },
        images: sortedData.map((d, i) => ({
            source: flagMapping[d.originalMarket] ? 'flags/' + flagMapping[d.originalMarket] : null,
            xref: 'paper',
            yref: 'y',
            x: -0.15,
            y: i,
            sizex: 0.25,
            sizey: 1.2,
            xanchor: 'right',
            yanchor: 'middle',
            visible: flagMapping[d.originalMarket] ? true : false
        })),
        margin: {
            l: 150,
            r: 150,  // 增加右边距以确保数值标签显示
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
        annotations: [{
            x: -0.5,
            y: 1.1,
            xref: 'paper',
            yref: 'paper',
            text: 'Online<br>Penetration',
            showarrow: false,
            font: {
                family: 'Monda',
                size: 11,
                color: '#666'
            },
            align: 'center'
        }],
        uniformtext: {
            mode: 'show',
            minsize: 8
        }
    };

    // 创建配置
    const config = {
        displayModeBar: false,
        responsive: true,
        staticPlot: false
    };

    // 渲染图表
    Plotly.newPlot('race-chart', [barData, penetrationData], layout, config);

    // 保存当前数据和布局用于插值
    window.currentRaceData = sortedData;
    window.raceChartLayout = layout;
    window.baseTrace = baseTrace;
}

// 更新race chart的函数
function updateRaceChart(data, year) {
    const yearData = data.filter(d => d.Year === year);
    
    // 处理数据
    const sortedData = yearData
        .map(d => ({
            market: d.Market,
            originalMarket: d.Market,
            value: d['Gross Bookings'] * (appConfig.dataProcessing?.bookingsScaleFactor || 1e-9),
            penetration: parseFloat(d['Online Penetration']) || 0,
            color: (appConfig.colorDict?.[d.Market] || appConfig.regionColors?.[d.Region] || '#999999'),
            region: d.Region
        }))
        .sort((a, b) => b.value - a.value)
        .slice(0, 15);

    // 更新图表数据
    const updatedData = [{
        ...window.baseTrace,
        y: sortedData.map(d => d.market),
        x: sortedData.map(d => d.value),
        marker: {
            color: sortedData.map(d => d.color)
        },
        text: sortedData.map(d => d.value.toFixed(1)),
        textposition: 'outside',
        texttemplate: '%{text}B',
        textfont: {
            family: 'Monda',
            size: 11,
            color: '#333'
        },
        cliponaxis: false,
        textangle: 0,
        outsidetextfont: {
            family: 'Monda',
            size: 11,
            color: '#333'
        },
        offsetgroup: 1,
        width: 0.6,
        constraintext: false
    },
    {
        type: 'scatter',
        mode: 'text',
        x: Array(sortedData.length).fill(-0.5),
        y: sortedData.map(d => d.market),
        text: sortedData.map(d => `${(d.penetration * 100).toFixed(1)}%`),
        textposition: 'middle left',
        textfont: {
            family: 'Monda',
            size: 11,
            color: '#666'
        },
        hoverinfo: 'none',
        showlegend: false
    }];

    // 使用 Plotly.react 来更新图表
    Plotly.react('race-chart', updatedData, window.raceChartLayout);

    // 更新当前数据
    window.currentRaceData = sortedData;
} 