// 更准确的世界地图区域定义
const regionPaths = {
    'North America': 'M 20 40 L 80 40 L 100 80 L 60 100 L 20 80 Z',
    'Latin America': 'M 60 100 L 100 100 L 80 160 L 40 160 L 20 120 Z',
    'Europe': 'M 120 40 L 160 40 L 180 60 L 160 80 L 120 60 Z',
    'Eastern Europe': 'M 180 60 L 220 40 L 240 60 L 220 80 L 180 80 Z',
    'Middle East': 'M 180 100 L 220 80 L 240 100 L 220 120 L 180 120 Z',
    'Asia-Pacific': 'M 240 60 L 280 40 L 300 80 L 280 120 L 240 100 Z'
};

function createMapLegend() {
    // 定义区域和对应的国家代码
    const regionCountries = {
        'North America': ['USA', 'CAN', 'MEX'],
        'Latin America': ['BRA', 'ARG', 'COL', 'CHL', 'PER', 'VEN', 'ECU', 'BOL', 'PRY', 'URY'],
        'Europe': ['GBR', 'FRA', 'DEU', 'ITA', 'ESP', 'NLD', 'CHE', 'BEL', 'PRT', 'IRL', 'DNK', 'NOR', 'SWE', 'FIN'],
        'Eastern Europe': ['RUS', 'POL', 'UKR', 'CZE', 'HUN', 'ROU', 'BGR', 'SVK', 'BLR', 'LTU', 'LVA', 'EST'],
        'Middle East': ['SAU', 'ARE', 'IRN', 'ISR', 'QAT', 'KWT', 'OMN', 'BHR', 'JOR', 'LBN'],
        'Asia-Pacific': ['CHN', 'JPN', 'KOR', 'AUS', 'IDN', 'IND', 'SGP', 'MYS', 'NZL', 'THA', 'VNM', 'PHL', 'TWN', 'HKG']
    };

    // 创建数据
    const data = [];
    Object.entries(regionCountries).forEach(([region, countries]) => {
        data.push({
            type: 'choropleth',
            locations: countries,
            z: Array(countries.length).fill(1),
            name: region,
            showscale: false,
            colorscale: [[0, appConfig.regionColors[region]], [1, appConfig.regionColors[region]]],
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
            lataxis: {range: [-50, 75]},
            lonaxis: {range: [-170, 190]},
            projection: {
                type: 'miller',
                scale: 0.45
            },
            domain: {
                x: [0, 1],
                y: [0, 1]
            },
            center: {
                lat: 20,
                lon: 10
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
        height: 320,
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