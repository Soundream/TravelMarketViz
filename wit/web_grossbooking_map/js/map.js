let isPlaying = false;
let currentFrame = 0;
let animationInterval;
let data;

// Initialize the visualization
async function init() {
    try {
        console.log('Initializing visualization...');
        const response = await fetch('../../../utilities/travel_market_summary.xlsx');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const arrayBuffer = await response.arrayBuffer();
        const data = new Uint8Array(arrayBuffer);
        
        const workbook = XLSX.read(data, { type: 'array' });
        const sheet = workbook.Sheets['Visualization Data'];
        if (!sheet) {
            throw new Error("Sheet 'Visualization Data' not found in Excel file");
        }
        
        const jsonData = XLSX.utils.sheet_to_json(sheet);
        console.log('Loaded data:', jsonData); // Debug log
        const processedData = processData(jsonData);
        createMap(processedData, appConfig.map.defaultYear);
        setupControls();
    } catch (error) {
        console.error('Error loading data:', error);
        document.getElementById('map-container').innerHTML = `
            <div style="color: red; padding: 20px;">
                Error loading visualization: ${error.message}<br>
                Path tried: ../../../utilities/travel_market_summary.xlsx<br>
                Please make sure you're running this through a web server and the Excel file is accessible.
            </div>
        `;
    }
}

// Process the data for visualization
function processData(rawData) {
    console.log('Raw data:', rawData);
    const years = [...new Set(rawData.map(row => row['Year']))].sort();
    console.log('Years found:', years);
    const processedData = [];

    // 创建一个Set来跟踪已添加的区域
    const addedRegions = new Set();

    // 国家坐标映射
    const countryCoords = {
        // North America
        'U.S.': { lat: 37.0902, lon: -95.7129 },
        'Canada': { lat: 56.1304, lon: -106.3468 },
        // Latin America
        'Brazil': { lat: -14.2350, lon: -51.9253 },
        'Argentina': { lat: -38.4161, lon: -63.6167 },
        'Colombia': { lat: 4.5709, lon: -74.2973 },
        'Chile': { lat: -35.6751, lon: -71.5430 },
        'Mexico': { lat: 23.6345, lon: -102.5528 },
        // Europe
        'U.K.': { lat: 55.3781, lon: -3.4360 },
        'France': { lat: 46.2276, lon: 2.2137 },
        'Germany': { lat: 51.1657, lon: 10.4515 },
        'Italy': { lat: 41.8719, lon: 12.5674 },
        'Spain': { lat: 40.4637, lon: -3.7492 },
        'Scandinavia': { lat: 60.1282, lon: 18.6435 },
        'Rest of Europe': { lat: 48.6390, lon: 15.9700 }, // 放在奥地利附近，代表中欧位置
        // Eastern Europe
        'Russia': { lat: 61.5240, lon: 105.3188 },
        'Poland': { lat: 51.9194, lon: 19.1451 },
        'Ukraine': { lat: 48.3794, lon: 31.1656 },
        'Czech Republic': { lat: 49.8175, lon: 15.4730 },
        'Hungary': { lat: 47.1625, lon: 19.5033 },
        'Romania': { lat: 45.9432, lon: 24.9668 },
        'Bulgaria': { lat: 42.7339, lon: 25.4858 },
        'Greece': { lat: 39.0742, lon: 21.8243 },
        // Middle East
        'Saudi Arabia': { lat: 23.8859, lon: 45.0792 },
        'U.A.E.': { lat: 23.4241, lon: 53.8478 },
        'Qatar': { lat: 25.3548, lon: 51.1839 },
        'Egypt': { lat: 26.8206, lon: 30.8025 },
        'Rest of Middle East': { lat: 33.2232, lon: 43.6793 }, // 放在伊拉克附近，代表中东中心位置
        // Asia Pacific
        'China': { lat: 35.8617, lon: 104.1954 },
        'Japan': { lat: 36.2048, lon: 138.2529 },
        'South Korea': { lat: 35.9078, lon: 127.7669 },
        'Australia-New Zealand': { lat: -25.2744, lon: 133.7751 },
        'India': { lat: 20.5937, lon: 78.9629 },
        'Singapore': { lat: 1.3521, lon: 103.8198 },
        'Indonesia': { lat: -0.7893, lon: 113.9213 },
        'Malaysia': { lat: 4.2105, lon: 101.9758 },
        'Thailand': { lat: 15.8700, lon: 100.9925 },
        'Taiwan': { lat: 23.6978, lon: 120.9605 },
        'Hong Kong': { lat: 22.3193, lon: 114.1694 },
        'Macau': { lat: 22.1987, lon: 113.5439 }
    };
    
    // 为每年创建一个新的数据集
    years.forEach(year => {
        // 只获取当前年份的数据
        const yearData = rawData.filter(row => row['Year'] === parseInt(year));
        console.log(`Processing data for year ${year}:`, yearData);
        
        // 创建一个Map来存储每个国家在当前年份的数据
        const marketMap = new Map();
        
        // 处理当前年份的所有数据
        yearData.forEach(row => {
            const market = row['Market'];
            const grossBookings = row['Gross Bookings'] / 1e9; // 转换为十亿
            
            // 如果这个市场已经存在，跳过（确保每个市场只出现一次）
            if (marketMap.has(market)) {
                console.log(`Duplicate market ${market} found for year ${year}, skipping...`);
                return;
            }
            
            // 确定国家所属的区域
            const region = row['Region'];
            let mappedRegion = region;
            if (region === 'APAC') mappedRegion = 'Asia-Pacific';
            if (region === 'LATAM') mappedRegion = 'Latin America';

            // 获取国家坐标
            const coords = countryCoords[market];
            if (!coords) {
                console.log(`No coordinates found for market: ${market}`);
                return;
            }

            if (grossBookings > 0) {
                marketMap.set(market, {
                    type: 'scattergeo',
                    lon: [coords.lon],
                    lat: [coords.lat],
                    text: [market],
                    customdata: [[grossBookings.toFixed(1), year]],
                    mode: 'markers',
                    marker: {
                        size: scaleMarkerSize(grossBookings),
                        color: appConfig.regionColors[mappedRegion],
                        line: {
                            color: 'white',
                            width: 1
                        },
                        sizemode: 'area'
                    },
                    name: mappedRegion, // 使用区域名称而不是国家名称
                    legendgroup: mappedRegion,
                    showlegend: !addedRegions.has(mappedRegion), // 每个区域只在图例中显示一次
                    hovertemplate: '<b>%{text}</b><br>' +
                                 'Gross Bookings: $%{customdata[0]}B<br>' +
                                 'Year: %{customdata[1]}<br>' +
                                 'Region: ' + mappedRegion,
                    frame: year
                });

                // 记录该区域已被添加到图例
                addedRegions.add(mappedRegion);
            }
        });
        
        // 将当前年份的所有数据添加到processedData
        processedData.push(...marketMap.values());
    });
    
    console.log('Processed data:', processedData);
    return processedData;
}

// Scale marker sizes
function scaleMarkerSize(value) {
    const size = Math.max(appConfig.map.minBubbleSize, 
           Math.min(appConfig.map.maxBubbleSize, 
           Math.sqrt(value) * 2));  // 调整系数使气泡大小更合适
    console.log('Scaling value', value, 'to size', size);
    return size;
}

// Create the map visualization
function createMap(data, year) {
    const layout = {
        title: {
            text: 'Global Travel Market Gross Bookings',
            font: {
                family: 'Monda',
                size: 24
            }
        },
        geo: {
            scope: 'world',
            projection: {
                type: appConfig.map.projection
            },
            showland: true,
            landcolor: 'rgb(243, 243, 243)',
            countrycolor: 'rgb(204, 204, 204)',
            showocean: true,
            oceancolor: 'rgb(250, 250, 250)',
            showframe: false
        },
        legend: {
            title: {
                text: 'Regions',
                font: {
                    family: 'Monda',
                    size: 14
                }
            },
            itemsizing: 'constant',
            itemwidth: 30,
            traceorder: 'normal'
        },
        sliders: [{
            currentvalue: {
                prefix: 'Year: ',
                xanchor: 'right'
            },
            steps: [...new Set(data.map(d => d.frame))].sort().map(year => ({
                label: year.toString(),
                method: 'animate',
                args: [[year], {
                    mode: 'immediate',
                    frame: {
                        duration: appConfig.animation.duration,
                        redraw: true
                    }
                }]
            }))
        }]
    };

    // 存储全局数据供后续更新使用
    window.mapData = data;

    Plotly.newPlot('map-container', 
        data.filter(d => d.frame === year),
        layout,
        {displayModeBar: false}
    );
}

// Set up control elements
function setupControls() {
    const playButton = document.getElementById('play-button');
    const yearSlider = document.getElementById('year-slider');
    const yearDisplay = document.getElementById('year-display');

    // 设置年份范围
    const years = [...new Set(window.mapData.map(d => d.frame))].sort();
    yearSlider.min = years[0];
    yearSlider.max = years[years.length - 1];
    yearSlider.value = years[0];
    yearDisplay.textContent = years[0];

    playButton.addEventListener('click', togglePlay);
    yearSlider.addEventListener('input', () => {
        const year = parseInt(yearSlider.value);
        yearDisplay.textContent = year;
        updateMap(year);
    });
}

// Toggle play/pause
function togglePlay() {
    isPlaying = !isPlaying;
    const playButton = document.getElementById('play-button');
    playButton.textContent = isPlaying ? 'Pause' : 'Play';

    if (isPlaying) {
        animationInterval = setInterval(() => {
            const yearSlider = document.getElementById('year-slider');
            const currentYear = parseInt(yearSlider.value);
            const nextYear = currentYear >= parseInt(yearSlider.max) 
                ? parseInt(yearSlider.min) 
                : currentYear + 1;
            
            yearSlider.value = nextYear;
            document.getElementById('year-display').textContent = nextYear;
            updateMap(nextYear);
        }, appConfig.animation.frameDelay);
    } else {
        clearInterval(animationInterval);
    }
}

// Update the map for a specific year
function updateMap(year) {
    if (!window.mapData) return;
    
    const yearData = window.mapData.filter(d => d.frame === year);
    
    // 保持现有的图例可见性
    const currentData = document.getElementById('map-container').data;
    if (currentData) {
        yearData.forEach((trace, i) => {
            if (currentData[i]) {
                trace.showlegend = currentData[i].showlegend;
            }
        });
    }
    
    Plotly.animate('map-container', {
        data: yearData,
        traces: Array.from({ length: yearData.length }, (_, i) => i)
    }, {
        transition: {
            duration: appConfig.animation.duration
        },
        frame: {
            duration: appConfig.animation.duration,
            redraw: true
        }
    });
}

// Initialize when the page loads
document.addEventListener('DOMContentLoaded', init); 