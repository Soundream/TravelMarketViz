// Create the map visualization
const layout = {
    width: 1000,  // 减小地图宽度
    height: 600,  // 地图高度
    margin: {
        l: 0,
        r: 0,
        t: 40,  // 顶部留空
        b: 0
    },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    showlegend: true,
    geo: {
        scope: 'world',
        projection: {
            type: 'equirectangular',
            rotation: {
                lon: 0,
                lat: 0,
                roll: 0
            }
        },
        showland: true,
        landcolor: 'rgba(255, 255, 255, 0)',
        countrycolor: 'rgb(204, 204, 204)',
        showocean: true,
        oceancolor: 'rgba(255, 255, 255, 0)',
        showframe: false,
        showcountries: true,
        resolution: 50,
        lonaxis: {
            showgrid: true,
            gridwidth: 0.5,
            range: [-180, 180],
            dtick: 30
        },
        lataxis: {
            showgrid: true,
            gridwidth: 0.5,
            range: [-60, 85],  // 限制南极区域显示
            dtick: 30
        }
    },
    legend: {
        x: 0.5,  // 居中
        y: -0.1, // 放在地图下方
        xanchor: 'center',
        yanchor: 'top',
        orientation: 'h',  // 水平排列
        bgcolor: 'rgba(255, 255, 255, 0.9)',
        bordercolor: 'rgba(0, 0, 0, 0.1)',
        borderwidth: 1,
        font: {
            family: 'Monda',
            size: 12
        },
        title: {
            text: 'Regions',
            font: {
                family: 'Monda',
                size: 14,
                color: '#333'
            }
        },
        itemsizing: 'constant',
        itemwidth: 30,
        traceorder: 'normal'
    }
}; 