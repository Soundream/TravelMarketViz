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
        cliponaxis: false,  // 防止文本被裁剪
        textangle: 0,
        offsetgroup: 1,
        width: 0.6,
        textposition: 'outside',
        constraintext: 'none'  // 确保文本始终显示
    };

    // 处理数据
    const sortedData = yearData
        .map(d => {
            const market = d.Market;
            const bookings = parseFloat(d['Gross Bookings']) || 0;
            
            // 检查并输出没有国旗的国家
            if (!flagMapping[market]) {
                console.log('Missing flag for country:', market);
            }

            return {
                market: market,
                originalMarket: market,
                value: bookings * (appConfig.dataProcessing?.bookingsScaleFactor || 1e-9),
                color: (appConfig.colorDict?.[market] || appConfig.regionColors?.[d.Region] || '#999999'),
                region: d.Region
            };
        })
        .sort((a, b) => b.value - a.value)
        .slice(0, 15);

    // 填充图表数据
    barData.x = sortedData.map(d => d.value);
    barData.y = sortedData.map(d => d.market);
    barData.marker.color = sortedData.map(d => d.color);
    barData.text = sortedData.map(d => d.value.toFixed(1));

    // 创建布局
    const layout = {
        width: 450,  // 增加宽度
        height: 400,  // 固定高度
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
            range: [0, maxValue * 1.3],  // 增加范围给标签留出更多空间
            fixedrange: true,
            ticklen: 6,
            ticksuffix: '   ',  // 在刻度标签后添加空格
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
            ticktext: sortedData.map(d => flagMapping[d.originalMarket] ? '' : (countryCodeMapping[d.originalMarket] || d.originalMarket)),
            tickmode: 'array',
            tickvals: Array.from({length: sortedData.length}, (_, i) => i),
            ticklabelposition: 'inside',
            autorange: 'reversed'
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
            l: 120,  // 左边距用于国旗和国家名称
            r: 120,  // 增加右边距以容纳数值标签
            t: 40,
            b: 50,
            autoexpand: false  // 禁用自动扩展
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
            mode: 'show',  // 始终显示文本
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

// 更新race chart的函数
function updateRaceChart(data, year) {
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

    const yearData = data.filter(d => d.Year === year);
    
    // 处理目标数据
    const targetData = yearData
        .map(d => {
            const market = d.Market;
            const bookings = parseFloat(d['Gross Bookings']) || 0;
            
            return {
                market: market,
                originalMarket: market,
                value: bookings * (appConfig.dataProcessing?.bookingsScaleFactor || 1e-9),
                color: (appConfig.colorDict?.[market] || appConfig.regionColors?.[d.Region] || '#999999'),
                region: d.Region
            };
        })
        .sort((a, b) => b.value - a.value)
        .slice(0, 15);

    // 更新图表数据
    const updatedData = [{
        ...window.baseTrace,
        y: targetData.map(d => d.market),
        x: targetData.map(d => d.value),
        marker: {
            color: targetData.map(d => d.color)
        },
        text: targetData.map(d => d.value.toFixed(1))
    }];

    // 更新布局
    const updatedLayout = {
        ...window.raceChartLayout,
        yaxis: {
            ...window.raceChartLayout.yaxis,
            ticktext: targetData.map(d => flagMapping[d.originalMarket] ? '' : (countryCodeMapping[d.originalMarket] || d.originalMarket)),
            autorange: 'reversed'
        },
        images: targetData.map((d, i) => ({
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
        }))
    };

    // 直接更新图表
    Plotly.react('race-chart', updatedData, updatedLayout);

    // 更新当前数据
    window.currentRaceData = targetData;
} 