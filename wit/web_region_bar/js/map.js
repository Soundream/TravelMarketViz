// 更准确的世界地图区域定义
const regionPaths = {
    'Europe': 'M 160 20 L 200 20 L 200 60 L 160 60 Z',
    'Eastern Europe': 'M 200 20 L 240 20 L 240 60 L 200 60 Z',
    'North America': 'M 80 20 L 160 20 L 160 60 L 80 60 Z',
    'Latin America': 'M 80 60 L 160 60 L 160 100 L 80 100 Z',
    'Middle East (sum)': 'M 200 60 L 240 60 L 240 100 L 200 100 Z',
    'Asia-Pacific': 'M 240 60 L 280 40 L 300 80 L 280 120 L 240 100 Z'
};

function createMapLegend() {
    // 定义区域和对应的国家代码
    const regionCountries = {
        'Europe': ['DEU', 'FRA', 'GBR', 'ITA', 'ESP', 'NLD', 'CHE', 'AUT', 'BEL', 'PRT', 'IRL', 'GRC', 'DNK', 'NOR', 'SWE', 'FIN', 'ISL'],
        'Eastern Europe': ['RUS', 'UKR', 'POL', 'CZE', 'HUN', 'ROU', 'SVK', 'SVN', 'HRV', 'SRB', 'MNE', 'ALB', 'MKD', 'BGR', 'BLR', 'EST', 'LVA', 'LTU'],
        'North America': ['USA', 'CAN', 'MEX'],
        'Latin America': ['BRA', 'ARG', 'COL', 'CHL', 'PER', 'VEN', 'BOL', 'ECU', 'PRY', 'URY', 'PAN', 'CRI', 'GTM', 'SLV', 'HND', 'NIC', 'DOM', 'CUB', 'JAM'],
        'Middle East (sum)': ['SAU', 'ARE', 'TUR', 'IRN', 'ISR', 'EGY', 'IRQ', 'QAT', 'KWT', 'JOR', 'LBN', 'OMN', 'BHR', 'SYR', 'YEM'],
        'Asia-Pacific': ['CHN', 'JPN', 'KOR', 'AUS', 'IDN', 'IND', 'SGP', 'MYS', 'NZL', 'THA', 'VNM', 'PHL', 'TWN', 'HKG']
    };

    // 创建数据
    const data = [];
    Object.entries(regionCountries).forEach(([region, countries]) => {
        // Use the original color key for Asia-Pacific
        const colorKey = region === 'Asia-Pacific' ? 'Asia-Pacific' : region;
        
        data.push({
            type: 'choropleth',
            locations: countries,
            z: Array(countries.length).fill(1),
            name: region,
            showscale: false,
            colorscale: [[0, appConfig.regionColors[colorKey]], [1, appConfig.regionColors[colorKey]]],
            marker: {
                line: {
                    color: 'white',
                    width: 0.5
                }
            },
            hoverinfo: 'name',
            showlegend: true,
            legendgroup: region
        });
    });

    // 创建布局
    const layout = {
        title: {
            font: {
                family: 'Monda',
                size: 10,
                color: 'rgba(0, 0, 0, 0.8)'
            },
            y: 0.98
        },
        geo: {
            scope: 'world',
            showframe: false,
            showcoastlines: true,
            coastlinecolor: '#ddd',
            showland: true,
            landcolor: 'rgb(250, 250, 250)',
            showocean: true,
            oceancolor: 'white',
            showlakes: false,
            showcountries: false,
            lataxis: {range: [-40, 70]},
            lonaxis: {range: [-150, 180]},
            projection: {
                type: 'miller',
                scale: 0.48
            },
            domain: {
                x: [0.02, 1],
                y: [0, 0.9]
            },
            center: {
                lat: 20,
                lon: 20
            }
        },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        margin: {
            l: 0,
            r: 0,
            t: 0,
            b: 0,
            pad: 0
        },
        dragmode: false,
        height: 250,
        width: 450,
        showlegend: false,
        autosize: false
    };

    // 创建配置
    const config = {
        displayModeBar: false,
        responsive: true,
        staticPlot: true
    };

    // 渲染地图
    Plotly.newPlot('map-legend', data, layout, config);

    // 添加交互效果
    const mapElement = document.getElementById('map-legend');
    mapElement.on('plotly_hover', function(data) {
        if (data.points && data.points[0]) {
            const region = data.points[0].data.name;
            highlightRegion(region);
        }
    });

    mapElement.on('plotly_unhover', function() {
        resetHighlight();
    });
}

function highlightRegion(region) {
    const traces = document.getElementById('bubble-chart').data;
    if (!traces) return;

    traces.forEach((trace, i) => {
        if (trace.name === region) {
            Plotly.restyle('bubble-chart', {
                'marker.opacity': 1,
                'marker.line.width': 3
            }, [i]);
        } else if (trace.name) {
            Plotly.restyle('bubble-chart', {
                'marker.opacity': 0.3,
                'marker.line.width': 1
            }, [i]);
        }
    });
}

function resetHighlight() {
    const traces = document.getElementById('bubble-chart').data;
    if (!traces) return;

    traces.forEach((trace, i) => {
        if (trace.name) {
            Plotly.restyle('bubble-chart', {
                'marker.opacity': 0.8,
                'marker.line.width': 2
            }, [i]);
        }
    });
} 