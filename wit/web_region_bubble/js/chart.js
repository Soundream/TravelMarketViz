// Global variables
let isPlaying = true; // 默认为播放状态
let playInterval;
let currentYearIndex = 0;
let years;
let processedData;
let timeline;
let uniqueRegions;
let backgroundTrace;
let currentTraces;
let layout;
let config;

// Add getEraText function at the top level
function getEraText(year) {
    const yearNum = parseInt(year);
    if (yearNum >= 2005 && yearNum <= 2007) {
        return "Growth of WWW";
    } else if (yearNum >= 2007 && yearNum <= 2008) {
        return "Great Recession";
    } else if (yearNum >= 2009 && yearNum <= 2018) {
        return "Growth of Mobile";
    } else if (yearNum >= 2019 && yearNum <= 2020) {
        return "Global Pandemic";
    } else if (yearNum >= 2021) {
        return "Post-Pandemic Recovery";
    }
    return "";
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
        .style('font-size', '18px');

    // Make timeline ticks more visible
    g.selectAll('.tick line')
        .style('stroke', '#ccc')
        .style('stroke-width', '1px')
        .attr('y2', '8');

    // Add triangle marker
    const triangle = g.append('path')
        .attr('d', d3.symbol().type(d3.symbolTriangle).size(100))
        .attr('fill', '#4CAF50')
        .attr('transform', `translate(${xScale(years[currentYearIndex])}, -10) rotate(180)`);

    timeline = {
        scale: xScale,
        triangle: triangle
    };
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

// Function to process Excel data by region
function processDataByRegion(jsonData) {
    console.log('Processing data:', jsonData); // Debug log
    const regionData = {};
    
    // Get unique regions first, excluding 'Asia-Pacific'
    uniqueRegions = [...new Set(jsonData.map(row => {
        // Map old region names to new ones
        const region = row['Region'];
        if (region === 'APAC') return 'Asia-Pacific (sum)';
        if (region === 'LATAM') return 'Latin America';
        return region;
    }))].filter(region => region !== 'Asia-Pacific (sum)'); // Filter out Asia-Pacific
    
    jsonData.forEach(row => {
        const year = row['Year'];
        let region = row['Region'];
        // Map old region names to new ones
        if (region === 'APAC') region = 'Asia-Pacific (sum)';
        if (region === 'LATAM') region = 'Latin America';
        
        // Skip Asia-Pacific region
        if (region === 'Asia-Pacific (sum)') return;
        
        if (!regionData[year]) {
            regionData[year] = {};
        }
        
        if (!regionData[year][region]) {
            regionData[year][region] = {
                'Gross Bookings': 0,
                'Online Bookings': 0,
                'count': 0
            };
        }
        
        regionData[year][region]['Gross Bookings'] += row['Gross Bookings'] || 0;
        regionData[year][region]['Online Bookings'] += row['Online Bookings'] || 0;
        regionData[year][region]['count']++;
    });
    
    // Calculate averages and online penetration
    const processedData = [];
    Object.entries(regionData).forEach(([year, regions]) => {
        Object.entries(regions).forEach(([region, data]) => {
            const onlinePenetration = data['Online Bookings'] / data['Gross Bookings'];
            processedData.push({
                Year: parseInt(year),
                Region: region,
                'Gross Bookings': data['Gross Bookings'],
                'Online Bookings': data['Online Bookings'],
                'Online Penetration': onlinePenetration
            });
        });
    });
    
    console.log('Processed data:', processedData); // Debug log
    return processedData;
}

// Function to create the bubble chart
function createBubbleChart(data, year) {
    console.log('Creating chart for year:', year, 'with data:', data);
    const yearData = data.filter(d => d.Year === year);
    
    // 计算所有年份的最大值，用于固定坐标轴范围
    const allYears = data.reduce((acc, curr) => {
        acc.maxOnlineBookings = Math.max(acc.maxOnlineBookings, curr['Online Bookings']);
        acc.maxOnlinePenetration = Math.max(acc.maxOnlinePenetration, curr['Online Penetration']);
        return acc;
    }, { maxOnlineBookings: 0, maxOnlinePenetration: 0 });

    // 创建背景文字
    backgroundTrace = {
        x: [50],
        y: [50],  // 调整垂直位置使文字更好地居中
        mode: 'text',
        text: [getEraText(year)],
        textposition: 'middle center',
        textfont: {
            size: 60,
            family: 'Monda, Arial',
            color: 'rgba(200,200,200,0.3)'
        },
        hoverinfo: 'skip',
        showlegend: false
    };

    // 创建图例数据
    currentTraces = uniqueRegions.map(region => {
        const regionData = yearData.filter(d => d.Region === region);
        // Get the correct color for Asia-Pacific (sum)
        const colorKey = region === 'Asia-Pacific (sum)' ? 'Asia-Pacific' : region;
        
        return {
            name: region,
            x: regionData.map(d => d['Online Penetration'] * appConfig.dataProcessing.onlinePenetrationMultiplier),
            y: regionData.map(d => d['Online Bookings'] * appConfig.dataProcessing.bookingsScaleFactor),
            mode: 'markers',
            hoverinfo: 'text',
            hovertext: regionData.map(d => `
                <b style="font-family: Monda">${d.Region}</b><br>
                <span style="font-family: Monda">Share of Online Bookings: ${(d['Online Penetration'] * 100).toFixed(1)}%<br>
                Online Bookings: $${(d['Online Bookings'] * appConfig.dataProcessing.bookingsScaleFactor).toFixed(1)}B<br>
                Gross Bookings: $${(d['Gross Bookings'] * appConfig.dataProcessing.bookingsScaleFactor).toFixed(1)}B</span>
            `),
            marker: {
                size: regionData.map(d => {
                    const size = Math.sqrt(d['Gross Bookings'] * appConfig.dataProcessing.bookingsScaleFactor) * 3;
                    return Math.max(appConfig.chart.minBubbleSize, 
                           Math.min(appConfig.chart.maxBubbleSize, size));
                }),
                color: appConfig.regionColors[colorKey],
                opacity: 0.75,
                line: {
                    color: 'rgba(255, 255, 255, 0.8)',
                    width: 1.5
                }
            },
            showlegend: true,
            legendgroup: region,
            type: 'scatter'
        };
    });

    // 合并背景文字和数据轨迹
    const allTraces = [backgroundTrace, ...currentTraces];

    // 初始化全局 layout 变量
    layout = {
        title: {
            text: '',  // 移除标题
            font: {
                family: 'Monda',
                size: 24
            },
            y: 0.95
        },
        xaxis: {
            title: {
                text: 'Share of Online Bookings (%)',
                font: {
                    family: 'Monda',
                    size: 22
                },
                standoff: 15
            },
            range: [-5, 105],  // 进一步扩大横轴范围
            showgrid: true,
            gridcolor: '#eee',
            gridwidth: 1,
            zeroline: true,
            zerolinecolor: '#eee',
            showline: true,
            linecolor: '#ccc',
            linewidth: 1,
            tickfont: {
                family: 'Monda',
                size: 20
            },
            tickmode: 'array',
            ticktext: ['0%', '20%', '40%', '60%', '80%', '100%'],
            tickvals: [0, 20, 40, 60, 80, 100],
            dtick: 20,
            showticklabels: true,
            ticks: 'outside',
            ticklen: 8,
            tickwidth: 1,
            tickcolor: '#ccc'
        },
        yaxis: {
            title: {
                text: 'Online Bookings (USD bn)',
                font: {
                    family: 'Monda',
                    size: 22
                },
                standoff: 20
            },
            type: 'log',
            showgrid: true,
            gridcolor: '#eee',
            gridwidth: 1,
            zeroline: true,
            zerolinecolor: '#eee',
            showline: true,
            linecolor: '#ccc',
            linewidth: 1,
            tickfont: {
                family: 'Monda',
                size: 20
            },
            tickmode: 'array',
            ticktext: ['0', '10', '40', '90', '160', '250', '400', '600', '800'],
            tickvals: [0, 10, 40, 90, 160, 250, 400, 600, 800],
            range: [0, Math.log10(900)],
            autorange: false,
            showticklabels: true,
            ticks: 'outside',
            ticklen: 8,
            tickwidth: 1,
            tickcolor: '#ccc'
        },
        showlegend: false,
        margin: {
            l: 80,
            r: 0,
            t: 100,
            b: 150
        },
        width: null,
        height: 650,  // 增加图表高度
        
        hovermode: 'closest',
        hoverlabel: {
            bgcolor: 'white',
            font: { 
                family: 'Monda',
                size: 16
            },
            bordercolor: '#666'
        },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        autosize: true
    };

    // 初始化全局 config 变量
    config = {
        responsive: true,
        displayModeBar: false
    };

    // 使用 Plotly.animate 实现平滑动画
    if (document.getElementById('bubble-chart').data) {
        // 获取之前的数据
        const chartDiv = document.getElementById('bubble-chart');
        const prevData = chartDiv.data;
        
        // 创建插值帧
        const numFrames = 35;  // 增加帧数以获得更平滑的动画
        const frames = [];
        
        for (let i = 0; i <= numFrames; i++) {
            const t = i / numFrames; // 插值因子 (0 到 1)
            
            // 为每个轨迹创建插值数据
            const interpolatedTraces = allTraces.map((trace, traceIndex) => {
                const prevTrace = prevData[traceIndex];
                
                // 如果是背景文字，直接返回新的轨迹
                if (trace.mode === 'text') return trace;
                
                return {
                    ...trace,
                    x: trace.x.map((x, idx) => {
                        const prevX = prevTrace.x[idx] || 0;
                        return prevX + (x - prevX) * t;
                    }),
                    y: trace.y.map((y, idx) => {
                        const prevY = prevTrace.y[idx] || 0;
                        return prevY + (y - prevY) * t;
                    }),
                    marker: {
                        ...trace.marker,
                        size: trace.marker.size.map((size, idx) => {
                            const prevSize = prevTrace.marker.size[idx] || 0;
                            return prevSize + (size - prevSize) * t;
                        })
                    }
                };
            });
            
            frames.push({
                data: interpolatedTraces,
                traces: Array.from({ length: allTraces.length }, (_, i) => i),
                layout: layout
            });
        }
        
        // 使用 Plotly.animate 播放动画帧
        Plotly.animate('bubble-chart', frames, {
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
    } else {
        Plotly.newPlot('bubble-chart', allTraces, layout, config);
    }

    // 创建race chart
    createRaceChart(data, year);

    // 更新时间轴
    updateTimeline(year);
}

// Function to handle play/pause
function togglePlay() {
    if (isPlaying) {
        let lastTime = 0;
        let lastUpdateTime = 0;
        const animationDuration = 30000; // 30秒完成一个完整循环
        const updateInterval = 1000 / 30; // 30fps
        
        function animate(currentTime) {
            if (!isPlaying) return;  // 如果停止播放则退出动画
            
            if (!lastTime) lastTime = currentTime;
            const elapsed = currentTime - lastTime;
            
            // 计算进度 (0 到 1)
            const totalProgress = (elapsed % animationDuration) / animationDuration;
            const indexFloat = totalProgress * (years.length - 1);
            const currentIndex = Math.floor(indexFloat);
            const nextIndex = (currentIndex + 1) % years.length;
            const progress = indexFloat - currentIndex;

            // 平滑更新时间轴三角形位置
            if (timeline && timeline.triangle) {
                const currentX = timeline.scale(years[currentIndex]);
                const nextX = timeline.scale(years[nextIndex]);
                const interpolatedX = currentX + (nextX - currentX) * progress;
                timeline.triangle.attr('transform', `translate(${interpolatedX}, -10) rotate(180)`);
            }

            // 仅在指定间隔更新图表
            if (currentTime - lastUpdateTime >= updateInterval) {
                lastUpdateTime = currentTime;

                // 获取当前和下一年的数据
                const currentYearData = processedData.filter(d => d.Year === years[currentIndex]);
                const nextYearData = processedData.filter(d => d.Year === years[nextIndex]);

                // 创建插值数据
                const interpolatedData = currentYearData.map(d => {
                    const nextData = nextYearData.find(nd => nd.Region === d.Region) || d;
                    return {
                        Region: d.Region,
                        Year: years[currentIndex],
                        'Online Penetration': d['Online Penetration'] + (nextData['Online Penetration'] - d['Online Penetration']) * progress,
                        'Online Bookings': d['Online Bookings'] + (nextData['Online Bookings'] - d['Online Bookings']) * progress,
                        'Gross Bookings': d['Gross Bookings'] + (nextData['Gross Bookings'] - d['Gross Bookings']) * progress
                    };
                });

                // 更新图表
                const chartDiv = document.getElementById('bubble-chart');
                if (chartDiv && chartDiv.data) {
                    // 创建新的轨迹数据
                    const traces = uniqueRegions.map(region => {
                        const regionData = interpolatedData.filter(d => d.Region === region);
                        return {
                            name: region,
                            x: regionData.map(d => d['Online Penetration'] * appConfig.dataProcessing.onlinePenetrationMultiplier),
                            y: regionData.map(d => d['Online Bookings'] * appConfig.dataProcessing.bookingsScaleFactor),
                            mode: 'markers',
                            marker: {
                                size: regionData.map(d => {
                                    const size = Math.sqrt(d['Gross Bookings'] * appConfig.dataProcessing.bookingsScaleFactor) * 3;
                                    return Math.max(appConfig.chart.minBubbleSize, 
                                           Math.min(appConfig.chart.maxBubbleSize, size));
                                }),
                                color: appConfig.regionColors[region],
                                opacity: 0.75,
                                line: {
                                    color: 'rgba(255, 255, 255, 0.8)',
                                    width: 1.5
                                }
                            }
                        };
                    });

                    // 更新气泡图
                    Plotly.animate('bubble-chart', {
                        data: [backgroundTrace, ...traces],
                        traces: Array.from({ length: traces.length + 1 }, (_, i) => i),
                        
                    }, {
                        transition: {
                            duration: 0,
                            easing: 'linear'
                        },
                        frame: {
                            duration: 0,
                            redraw: false
                        }
                    });

                    // 更新背景文字
                    backgroundTrace = {
                        x: [50],
                        y: [50],
                        mode: 'text',
                        text: [getEraText(years[currentIndex])],
                        textposition: 'middle center',
                        textfont: {
                            size: 60,
                            family: 'Monda, Arial',
                            color: 'rgba(200,200,200,0.3)'
                        },
                        hoverinfo: 'skip',
                        showlegend: false
                    };

                    // 更新race chart
                    updateRaceChart(interpolatedData, years[currentIndex]);
                }
            }

            requestAnimationFrame(animate);
        }

        requestAnimationFrame(animate);
    }
}

// Initialize the visualization
async function init() {
    try {
        console.log('Initializing visualization...');
        const response = await fetch('./travel_market_summary.xlsx');
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
        
        // Filter out Taiwan, Hong Kong, and Macau
        const filteredData = jsonData.filter(row => {
            const market = row['Market'];
            return market !== 'Taiwan' && market !== 'Hong Kong' && market !== 'Macau';
        });
        
        // Process region data
        processedData = processDataByRegion(filteredData);
        years = [...new Set(processedData.map(d => d.Year))].sort();
        currentYearIndex = years.indexOf(appConfig.chart.defaultYear);
        
        // Process APAC countries data for the race chart
        const apacCountriesData = filteredData
            .filter(row => row['Region'] === 'APAC' && row['Market'] && row['Year'])
            .map(row => {
                // 标准化市场名称
                let market = row['Market'];
                if (market === 'Australia-New Zealand' || market === 'Australia/New Zealand') {
                    market = 'Australia & New Zealand';
                }
                return {
                    Market: market,
                    Year: row['Year'],
                    OnlinePenetration: row['Online Penetration'] / 100,
                    OnlineBookings: row['Online Bookings'],
                    GrossBookings: row['Gross Bookings']
                };
            });
            
        // Store APAC countries data globally so race-chart.js can access it
        window.processedCountriesData = apacCountriesData;
        
        // 创建时间轴
        createTimeline();
        
        // 先创建初始图表数据
        createBubbleChart(processedData, years[currentYearIndex]);

        // 清空并重新创建地图图例
        document.getElementById('map-legend').innerHTML = '';
        createMapLegend();
        
        // 确保图表已经完全加载后再开始动画
        setTimeout(() => {
            isPlaying = true;
            togglePlay();
        }, 500);
        
    } catch (error) {
        console.error('Error initializing visualization:', error);
        document.getElementById('bubble-chart').innerHTML = `
            <div style="color: red; padding: 20px;">
                Error loading visualization: ${error.message}<br>
                Please check the browser console for more details.
            </div>
        `;
    }
}

// Start the visualization when the page loads
document.addEventListener('DOMContentLoaded', init); 