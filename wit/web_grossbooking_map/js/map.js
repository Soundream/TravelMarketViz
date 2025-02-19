let isPlaying = false;
let currentFrame = 0;
let animationInterval;
let data;
let timeline;
let years;
let animationFrameId = null;
let processedData = null;

// Initialize the visualization
async function init() {
    try {
        console.log('Initializing visualization...');
        const response = await fetch('/utilities/travel_market_summary.xlsx');
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
        if (!jsonData || jsonData.length === 0) {
            throw new Error("No data found in the Excel file");
        }
        console.log('Loaded data:', jsonData);
        
        processedData = processData(jsonData);
        if (!processedData || processedData.length === 0) {
            throw new Error("Failed to process data");
        }
        
        createMap(processedData, appConfig.map.defaultYear);
        createTimeline();
        
        // 自动开始动画
        startAnimation();
    } catch (error) {
        console.error('Error loading data:', error);
        document.getElementById('map-container').innerHTML = `
            <div style="color: red; padding: 20px;">
                Error loading visualization: ${error.message}<br>
                Path tried: /utilities/travel_market_summary.xlsx<br>
                Please make sure you're running this through a web server and the Excel file is accessible.
            </div>
        `;
    }
}

// Process the data for visualization
function processData(rawData) {
    console.log('Raw data:', rawData);
    console.log('Sample data row:', rawData[0]);
    const processedData = [];

    // 首先从原始数据中提取年份
    years = [...new Set(rawData.map(d => d.Year))].sort((a, b) => a - b);
    console.log('Years extracted:', years);

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
        // 重置区域跟踪器（每年都需要显示所有区域的图例）
        addedRegions.clear();
        
        // 只获取当前年份的数据
        const yearData = rawData.filter(row => row.Year === year);
        console.log(`Processing data for year ${year}, found ${yearData.length} records`);
        
        // 创建一个Map来存储每个国家在当前年份的数据
        const marketMap = new Map();
        
        // 处理当前年份的所有数据
        yearData.forEach(row => {
            const market = row.Market;
            const grossBookings = parseFloat(row['Gross Bookings']) / 1e9; // 确保转换为数字
            
            // 如果这个市场已经存在，跳过（确保每个市场只出现一次）
            if (marketMap.has(market)) {
                console.log(`Duplicate market ${market} found for year ${year}, skipping...`);
                return;
            }
            
            // 确定国家所属的区域
            const region = row.Region;
            let mappedRegion = region;
            if (region === 'APAC') mappedRegion = 'Asia-Pacific';
            if (region === 'LATAM') mappedRegion = 'Latin America';

            // 获取国家坐标
            const coords = countryCoords[market];
            if (!coords) {
                console.log(`No coordinates found for market: ${market}`);
                return;
            }

            if (!isNaN(grossBookings) && grossBookings > 0) {
                const trace = {
                    type: 'scattergeo',
                    lon: [coords.lon],
                    lat: [coords.lat],
                    text: [market],
                    customdata: [[grossBookings.toFixed(1), year]],
                    mode: 'markers',
                    marker: {
                        size: scaleMarkerSize(grossBookings),
                        color: appConfig.regionColors[mappedRegion] || '#999999',
                        line: {
                            color: 'white',
                            width: 1
                        },
                        sizemode: 'area'
                    },
                    name: mappedRegion,
                    legendgroup: mappedRegion,
                    showlegend: !addedRegions.has(mappedRegion),
                    hovertemplate: '<b>%{text}</b><br>' +
                                 'Gross Bookings: $%{customdata[0]}B<br>' +
                                 'Year: %{customdata[1]}<br>' +
                                 'Region: ' + mappedRegion,
                    frame: year.toString()
                };
                marketMap.set(market, trace);
                addedRegions.add(mappedRegion);
            } else {
                console.log(`Invalid gross bookings value for ${market}: ${grossBookings}`);
            }
        });
        
        // 将当前年份的所有数据添加到processedData
        processedData.push(...marketMap.values());
    });
    
    console.log('Processed data sample:', processedData[0]);
    console.log('Total processed data points:', processedData.length);
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

// Function to create timeline
function createTimeline() {
    const timelineWidth = document.getElementById('timeline').offsetWidth;
    const margin = { left: 80, right: 80 }; // 增加左右边距
    const width = timelineWidth - margin.left - margin.right;

    // Create SVG
    const svg = d3.select('#timeline')
        .append('svg')
        .attr('width', timelineWidth)
        .attr('height', 60);

    const g = svg.append('g')
        .attr('transform', `translate(${margin.left}, 30)`);

    // Create scale
    const xScale = d3.scaleLinear()
        .domain([d3.min(years), d3.max(years)])
        .range([0, width]);

    // Create axis
    const xAxis = d3.axisBottom(xScale)
        .tickFormat(d => d.toString())
        .ticks(years.length)
        .tickValues(years);

    // Add axis
    g.append('g')
        .attr('class', 'timeline-axis')
        .call(xAxis)
        .selectAll('text')
        .style('text-anchor', 'middle')
        .style('font-family', 'Monda')
        .style('font-size', '12px');

    // Add triangle marker
    const triangle = g.append('path')
        .attr('d', d3.symbol().type(d3.symbolTriangle).size(100))
        .attr('fill', '#4CAF50')
        .attr('transform', `translate(${xScale(years[currentFrame])}, -10) rotate(180)`);

    timeline = {
        scale: xScale,
        triangle: triangle
    };

    // Add click interaction
    svg.on('click', function(event) {
        const coords = d3.pointer(event);
        const x = coords[0] - margin.left;
        const year = Math.round(xScale.invert(x));
        if (years.includes(year)) {
            currentFrame = years.indexOf(year);
            updateVisualization(year);
        }
    });
}

// Function to update timeline
function updateTimeline(year) {
    if (timeline && timeline.triangle) {
        timeline.triangle
            .transition()
            .duration(appConfig.animation.duration)
            .attr('transform', `translate(${timeline.scale(year)}, -10) rotate(180)`);
    }
}

// Create the map visualization
function createMap(data, year) {
    console.log('Creating map with data for year:', year);
    console.log('Sample data point:', data[0]);

    const layout = {
        autosize: true,
        height: 600,
        margin: {
            l: 0,
            r: 0,
            t: 0,
            b: 0
        },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        showlegend: true,
        geo: {
            scope: 'world',
            projection: {
                type: 'equirectangular'
            },
            showland: true,
            landcolor: 'rgb(243, 243, 243)',
            countrycolor: 'rgb(204, 204, 204)',
            showocean: true,
            oceancolor: 'rgb(250, 250, 250)',
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
                range: [-90, 90],
                dtick: 30
            }
        },
        legend: {
            x: 0.01,
            y: 0.99,
            bgcolor: 'rgba(255, 255, 255, 0)',
            bordercolor: 'rgba(0,0,0,0)',
            borderwidth: 0,
            font: {
                family: 'Monda',
                size: 12
            },
            title: {
                text: '',
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

    // 存储全局数据供后续更新使用
    window.mapData = data;

    const yearStr = year.toString();
    const yearData = data.filter(d => d.frame === yearStr);
    console.log(`Filtered ${yearData.length} points for year ${year}`);

    const config = {
        displayModeBar: false,
        responsive: true,
        scrollZoom: false
    };

    try {
        Plotly.newPlot('map-container', yearData, layout, config)
            .then(() => {
                console.log('Map created successfully');
                // 强制重新计算布局
                window.dispatchEvent(new Event('resize'));
            })
            .catch(error => {
                console.error('Error creating map:', error);
            });
    } catch (error) {
        console.error('Error in map creation:', error);
    }
}

// Start the animation
function startAnimation() {
    isPlaying = true;
    let startTime = null;
    const animationDuration = 15000; // 减少总循环时间到15秒
    const frameInterval = 50; // 添加帧间隔控制
    let lastFrameTime = 0;
    
    function animate(currentTime) {
        if (!startTime) startTime = currentTime;
        
        // 控制帧率
        if (currentTime - lastFrameTime < frameInterval) {
            animationFrameId = requestAnimationFrame(animate);
            return;
        }
        
        const elapsed = currentTime - startTime;
        const totalProgress = (elapsed % animationDuration) / animationDuration;
        const indexFloat = totalProgress * (years.length - 1);
        const currentIndex = Math.floor(indexFloat);
        
        // 只在年份变化时更新
        if (currentIndex !== currentFrame) {
            currentFrame = currentIndex;
            // 使用 Plotly.animate 而不是 react 来实现更平滑的过渡
            const yearData = processedData.filter(d => d.frame === years[currentIndex].toString());
            Plotly.animate('map-container', {
                data: yearData,
                traces: [0]
            }, {
                transition: {
                    duration: 300,
                    easing: 'cubic-in-out'
                },
                frame: {
                    duration: 300,
                    redraw: false
                }
            });
            updateTimeline(years[currentIndex]);
        }
        
        lastFrameTime = currentTime;
        animationFrameId = requestAnimationFrame(animate);
    }
    
    animationFrameId = requestAnimationFrame(animate);
}

// Update the map for a specific year
function updateMap(year) {
    console.log('Updating map for year:', year);
    const yearData = processedData.filter(d => d.frame === year.toString());
    console.log(`Found ${yearData.length} data points for year ${year}`);

    // 使用 Plotly.animate 替代 Plotly.react
    Plotly.animate('map-container', {
        data: yearData,
        traces: [0]
    }, {
        transition: {
            duration: 300,
            easing: 'cubic-in-out'
        },
        frame: {
            duration: 300,
            redraw: false
        }
    });
    
    updateTimeline(year);
}

// Update both map and timeline
function updateVisualization(year) {
    updateMap(year);
    updateTimeline(year);
}

// Initialize when the page loads
document.addEventListener('DOMContentLoaded', init); 