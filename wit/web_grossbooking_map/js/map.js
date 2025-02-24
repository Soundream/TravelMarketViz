let isPlaying = false;
let currentFrame = 0;
let animationInterval;
let data;
let timeline;
let years;
let animationFrameId = null;
let processedData = null;
let originalData = null;

// 添加全局变量用于时间控制
let currentExactYear = null;
let timelineAnimationId = null;
let globalStartTime = null;
const ANIMATION_DURATION = 30000; // 30秒循环

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
        
        // 保存原始数据
        originalData = jsonData;
        
        processedData = processData(jsonData);
        if (!processedData || processedData.length === 0) {
            throw new Error("Failed to process data");
        }
        
        createMap(processedData, years[0]);
        createTimeline();
        createRaceChart(originalData, years[0]);
        
        // 自动开始动画
        startAnimation();

        // 添加source和note
        const container = document.createElement('div');
        container.style.position = 'absolute';
        container.style.left = '0';
        container.style.bottom = '20px';  // 距离底部的距离
        container.style.width = '80%';
        container.style.fontFamily = 'Monda';
        container.style.fontSize = '11px';
        container.style.color = '#666666';
        container.style.padding = '0 20px';  // 左右padding

        container.innerHTML = `
            <div>Source: Phocuswright</div>
            <div style="margin-top: 5px">Note: Rest of Europe uses EU flag, Scandinavia uses Sweden flag</div>
        `;

        document.body.appendChild(container);
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
                            color: 'rgba(255, 255, 255, 0.1)',
                            width: 0.2
                        },
                        sizemode: 'area',
                        sizeref: 0.15,
                        opacity: 0.9
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
    return size;
}

// Function to create timeline
function createTimeline() {
    const timelineWidth = 1200;  // 增加时间轴宽度
    const margin = { left: 100, right: 100, top: 40, bottom: 20 };
    const width = timelineWidth - margin.left - margin.right;
    const height = 60;

    // Create SVG
    const svg = d3.select('#timeline')
        .append('svg')
        .attr('width', timelineWidth)
        .attr('height', height + margin.top + margin.bottom)
        .style('margin', '20px auto 0')
        .style('display', 'block');

    const g = svg.append('g')
        .attr('transform', `translate(${margin.left}, ${margin.top})`);

    // Create scale (现在只用于绘制轴，不用于动画)
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

    // 创建指针，初始位置在最左边
    const triangle = g.append('path')
        .attr('d', d3.symbol().type(d3.symbolTriangle).size(100))
        .attr('fill', '#4CAF50')
        .attr('transform', `translate(0, -10) rotate(180)`);

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
            .duration(300)
            .ease(d3.easeCubicInOut)
            .attr('transform', `translate(${timeline.scale(year)}, -10) rotate(180)`);
    }
}

// Create the map visualization
const layout = {
    width: 1000,
    height: 600,
    margin: {
        l: 0,
        r: 0,
        t: 40,
        b: 80  // 增加底部边距以容纳图例
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
        x: 0.5,
        y: -0.2,  // 放在地图下方
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

function createMap(data, year) {
    console.log('Creating map with data for year:', year);
    console.log('Sample data point:', data[0]);

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

// 修改startAnimation函数
function startAnimation() {
    isPlaying = true;
    globalStartTime = null;
    let lastRoundedYear = null;
    
    // 预计算所有年份的数据结构
    const baseData = processedData[0];
    const preCalculatedData = {};
    const preCalculatedRaceData = {};
    
    // 获取所有市场和区域
    const allMarkets = new Set();
    const allRegions = new Set();
    processedData.forEach(d => {
        allMarkets.add(d.text[0]);
        allRegions.add(d.name);
    });

    // 预计算race chart数据
    years.forEach(year => {
        const yearData = originalData.filter(d => d.Year === year);
        preCalculatedRaceData[year] = yearData
            .map(d => ({
                market: d.Market,
                value: parseFloat(d['Gross Bookings']),
                color: appConfig.colorDict[d.Market] || '#999999',
                region: d.Region
            }))
            .sort((a, b) => b.value - a.value)
            .slice(0, 15);
    });

    // 创建基础数据结构
    const baseTraces = Array.from(allMarkets).map(market => {
        const basePoint = processedData.find(d => d.text[0] === market);
        if (!basePoint) return null;

        return {
            type: 'scattergeo',
            lon: [basePoint.lon[0]],
            lat: [basePoint.lat[0]],
            text: [market],
            mode: 'markers',
            marker: {
                color: basePoint.marker.color,
                line: basePoint.marker.line,
                sizemode: 'area',
                sizeref: 0.15,
                opacity: 0.9
            },
            name: basePoint.name,
            legendgroup: basePoint.legendgroup,
            showlegend: !allRegions.has(basePoint.name),
            hovertemplate: basePoint.hovertemplate
        };
    }).filter(Boolean);

    // 确保每个区域只显示一次图例
    allRegions.clear();
    baseTraces.forEach(d => {
        if (!allRegions.has(d.name)) {
            d.showlegend = true;
            allRegions.add(d.name);
        }
    });

    // 预计算每个年份的地图数据
    years.forEach(year => {
        const yearData = processedData.filter(d => d.frame === year.toString());
        preCalculatedData[year] = baseTraces.map(baseTrace => {
            const yearPoint = yearData.find(d => d.text[0] === baseTrace.text[0]);
            const trace = { ...baseTrace };
            
            if (yearPoint) {
                const value = parseFloat(yearPoint.customdata[0][0]);
                trace.marker.size = scaleMarkerSize(value);
                trace.customdata = [[value.toFixed(1), year]];
            } else {
                trace.marker.size = 0;
                trace.customdata = [[0, year]];
            }
            
            return trace;
        });
    });
    
    function animate(currentTime) {
        if (!globalStartTime) globalStartTime = currentTime;
        
        const elapsed = currentTime - globalStartTime;
        const totalProgress = (elapsed % ANIMATION_DURATION) / ANIMATION_DURATION;
        
        // 计算当前年份（包括小数部分）
        const startYear = years[0];
        const endYear = years[years.length - 1];
        currentExactYear = startYear + (endYear - startYear) * totalProgress;
        
        // 获取当前年份的整数部分和小数部分
        const currentYearInt = Math.floor(currentExactYear);
        const currentYearFraction = currentExactYear - currentYearInt;
        
        // 找到当前年份在years数组中的位置
        const currentYearIndex = years.findIndex(y => y >= currentYearInt);
        if (currentYearIndex === -1) return;
        
        // 获取当前和下一个年份
        const currentYear = years[currentYearIndex];
        const nextYear = years[Math.min(currentYearIndex + 1, years.length - 1)];
        
        // 更新时间轴位置
        if (timeline && timeline.triangle) {
            const currentX = timeline.scale(currentExactYear);
            timeline.triangle.attr('transform', `translate(${currentX}, -10) rotate(180)`);
        }

        // 使用预计算的数据进行插值
        const currentData = preCalculatedData[currentYear];
        const nextData = preCalculatedData[nextYear];
        
        // 创建地图插值数据
        const interpolatedMapData = currentData.map((current, index) => {
            const next = nextData[index];
            const trace = { ...current };
            
            const currentValue = parseFloat(current.customdata[0][0]);
            const nextValue = parseFloat(next.customdata[0][0]);
            const interpolatedValue = currentValue + (nextValue - currentValue) * currentYearFraction;
            
            trace.marker.size = scaleMarkerSize(interpolatedValue);
            trace.customdata = [[interpolatedValue.toFixed(1), Math.round(currentExactYear)]];
            
            return trace;
        });

        // 更新地图
        Plotly.animate('map-container', {
            data: interpolatedMapData
        }, {
            transition: {
                duration: 0
            },
            frame: {
                duration: 0,
                redraw: false
            }
        });
        
        // 使用预计算的race chart数据进行插值
        const currentRaceData = preCalculatedRaceData[currentYear];
        const nextRaceData = preCalculatedRaceData[nextYear];
        
        // 创建一个包含所有市场的集合
        const allRaceMarkets = new Set([
            ...currentRaceData.map(d => d.market),
            ...nextRaceData.map(d => d.market)
        ]);

        // 创建race chart的插值数据
        const interpolatedRaceData = Array.from(allRaceMarkets).map(market => {
            const current = currentRaceData.find(d => d.market === market) || 
                          { market, value: 0, color: appConfig.colorDict[market] || '#999999' };
            const next = nextRaceData.find(d => d.market === market) || 
                        { market, value: 0, color: appConfig.colorDict[market] || '#999999' };
            
            return {
                Market: market,
                'Gross Bookings': current.value + (next.value - current.value) * currentYearFraction,
                Year: Math.round(currentExactYear),
                Region: current.region || next.region
            };
        });
        
        // 更新race chart
        updateRaceChart(interpolatedRaceData, Math.round(currentExactYear));
        
        // 继续动画
        if (isPlaying) {
            requestAnimationFrame(animate);
        }
    }
    
    // 初始化地图，使用预计算的第一年数据
    Plotly.newPlot('map-container', preCalculatedData[years[0]], layout, {
        displayModeBar: false,
        responsive: true,
        scrollZoom: false
    }).then(() => {
        requestAnimationFrame(animate);
    });
}

// 修改停止动画的逻辑
function stopAnimation() {
    isPlaying = false;
    if (timelineAnimationId) {
        cancelAnimationFrame(timelineAnimationId);
        timelineAnimationId = null;
    }
}

// Update the map for a specific year
function updateMap(year) {
    console.log('Updating map for year:', year);
    const yearData = processedData.filter(d => d.frame === year.toString());
    console.log(`Found ${yearData.length} data points for year ${year}`);

    // 更新每个气泡的大小
    const updatedData = yearData.map(d => {
        const value = parseFloat(d.customdata[0][0]);
        return {
            type: 'scattergeo',
            lon: d.lon,
            lat: d.lat,
            text: d.text,
            customdata: [[value.toFixed(1), year]],
            mode: 'markers',
            marker: {
                size: scaleMarkerSize(value),
                color: d.marker.color,
                line: {
                    color: 'rgba(255, 255, 255, 0.1)',
                    width: 0.2
                },
                sizemode: 'area',
                sizeref: 0.15,
                opacity: 0.9
            },
            name: d.name,
            legendgroup: d.legendgroup,
            showlegend: d.showlegend,
            hovertemplate: d.hovertemplate
        };
    });

    Plotly.animate('map-container', {
        data: updatedData,
        traces: Array.from({ length: updatedData.length }, (_, i) => i)
    }, {
        transition: {
            duration: 300,
            easing: 'cubic-in-out'
        },
        frame: {
            duration: 300,
            redraw: true
        }
    });
    
    // 更新race chart
    updateRaceChart(originalData, year);
    
    // 平滑更新时间轴
    if (timeline && timeline.triangle) {
        timeline.triangle
            .transition()
            .duration(300)
            .ease(d3.easeCubicInOut)
            .attr('transform', `translate(${timeline.scale(year)}, -10) rotate(180)`);
    }
}

// Update both map and timeline
function updateVisualization(year) {
    updateMap(year);
    updateTimeline(year);
}

// Initialize when the page loads
document.addEventListener('DOMContentLoaded', init); 