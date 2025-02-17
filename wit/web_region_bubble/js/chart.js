// Global variables
let isPlaying = false;
let playInterval;
let currentYearIndex = 0;
let years;
let processedData;
let timeline;
let uniqueRegions;
let backgroundTrace;
let currentTraces;

// Function to create timeline
function createTimeline() {
    const timelineWidth = document.getElementById('timeline').offsetWidth;
    const margin = { left: 50, right: 50 };
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
        .style('font-family', 'Open Sans')
        .style('font-size', '12px');

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
    
    // Get unique regions first
    uniqueRegions = [...new Set(jsonData.map(row => row['Region']))];
    
    jsonData.forEach(row => {
        const year = row['Year'];
        const region = row['Region'];
        
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
        x: [0.5],
        y: [Math.sqrt(allYears.maxOnlineBookings * appConfig.dataProcessing.bookingsScaleFactor / 4)],
        mode: 'text',
        text: [`Global Pandemic`],
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
        return {
            name: region,
            x: regionData.map(d => d['Online Penetration'] * appConfig.dataProcessing.onlinePenetrationMultiplier),
            y: regionData.map(d => d['Online Bookings'] * appConfig.dataProcessing.bookingsScaleFactor),
            mode: 'markers',
            hoverinfo: 'text',
            hovertext: regionData.map(d => `
                <b>${d.Region}</b><br>
                Online Penetration: ${(d['Online Penetration'] * 100).toFixed(1)}%<br>
                Online Bookings: $${(d['Online Bookings'] * appConfig.dataProcessing.bookingsScaleFactor).toFixed(1)}B<br>
                Gross Bookings: $${(d['Gross Bookings'] * appConfig.dataProcessing.bookingsScaleFactor).toFixed(1)}B
            `),
            marker: {
                size: regionData.map(d => {
                    const size = Math.sqrt(d['Gross Bookings'] * appConfig.dataProcessing.bookingsScaleFactor) * 3;
                    return Math.max(appConfig.chart.minBubbleSize, 
                           Math.min(appConfig.chart.maxBubbleSize, size));
                }),
                color: appConfig.regionColors[region],
                opacity: 0.8,
                line: {
                    color: 'white',
                    width: 2
                }
            },
            showlegend: true,
            legendgroup: region,
            type: 'scatter'
        };
    });

    // 合并背景文字和数据轨迹
    const allTraces = [backgroundTrace, ...currentTraces];

    const layout = {
        title: {
            text: `Global Travel Market by Region - ${year}`,
            font: {
                family: 'Montserrat',
                size: 24
            },
            y: 0.95
        },
        xaxis: {
            title: {
                text: appConfig.chart.xAxisTitle,
                font: {
                    family: 'Open Sans',
                    size: 14
                }
            },
            range: [0, 100],
            showgrid: true,
            gridcolor: '#eee',
            gridwidth: 1,
            zeroline: true,
            zerolinecolor: '#eee',
            showline: true,
            linecolor: '#ccc',
            linewidth: 1,
            tickfont: {
                family: 'Open Sans',
                size: 12
            },
            tickmode: 'array',
            ticktext: ['0%', '20%', '40%', '60%', '80%', '100%'],
            tickvals: [0, 20, 40, 60, 80, 100],
            dtick: 20,
            showticklabels: true,
            ticklen: 5,
            tickcolor: '#ccc'
        },
        yaxis: {
            title: {
                text: appConfig.chart.yAxisTitle + ' (Billions)',
                font: {
                    family: 'Open Sans',
                    size: 14
                }
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
                family: 'Open Sans',
                size: 12
            },
            tickmode: 'array',
            ticktext: ['0', '10', '40', '90', '160', '250', '400', '600'],
            tickvals: [0, 10, 40, 90, 160, 250, 400, 600],
            range: [0, Math.log10(600)],
            autorange: false,
            showticklabels: true,
            ticklen: 5,
            tickcolor: '#ccc'
        },
        showlegend: true,
        legend: {
            x: 1.05,
            y: 1,
            xanchor: 'left',
            yanchor: 'top',
            bgcolor: 'rgba(255, 255, 255, 0)',
            bordercolor: 'rgba(255, 255, 255, 0)',
            font: {
                family: 'Open Sans',
                size: 12
            },
            itemsizing: 'constant',
            itemwidth: 30,
            tracegroupgap: 8
        },
        annotations: [
            {
                text: 'Data Source: Phocal Point',
                x: 0,
                y: -0.15,
                xref: 'paper',
                yref: 'paper',
                showarrow: false,
                font: {
                    size: 12,
                    color: 'rgba(0, 0, 0, 0.6)'
                },
                xanchor: 'left'
            },
            {
                text: 'Note: 2005 - 2009 figures based on extrapolation',
                x: 0,
                y: -0.19,
                xref: 'paper',
                yref: 'paper',
                showarrow: false,
                font: {
                    size: 12,
                    color: 'rgba(0, 0, 0, 0.6)'
                },
                xanchor: 'left'
            }
        ],
        hovermode: 'closest',
        hoverlabel: {
            bgcolor: 'white',
            font: { 
                family: 'Montserrat',
                size: 12
            },
            bordercolor: '#666'
        },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        margin: {
            l: 80,
            r: 250,
            t: 100,
            b: 100
        },
        width: 950,
        height: 600
    };

    const config = {
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

    // 更新时间轴
    updateTimeline(year);
}

// Function to handle play/pause
function togglePlay() {
    const playButton = document.getElementById('playButton');
    isPlaying = !isPlaying;
    
    if (isPlaying) {
        playButton.innerHTML = '<i class="fas fa-pause"></i>';
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

            // 仅在指定间隔更新气泡图
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
                                opacity: 0.8,
                                line: {
                                    color: 'white',
                                    width: 2
                                }
                            }
                        };
                    });

                    // 更新图表
                    Plotly.animate('bubble-chart', {
                        data: [backgroundTrace, ...traces],
                        traces: Array.from({ length: traces.length + 1 }, (_, i) => i),
                        layout: {
                            title: {
                                text: `Global Travel Market by Region - ${years[currentIndex]}`
                            }
                        }
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
                }
            }

            requestAnimationFrame(animate);
        }

        requestAnimationFrame(animate);
    } else {
        playButton.innerHTML = '<i class="fas fa-play"></i>';
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
        processedData = processDataByRegion(jsonData);
        years = [...new Set(processedData.map(d => d.Year))].sort();
        currentYearIndex = years.indexOf(appConfig.chart.defaultYear);
        
        // 创建时间轴
        createTimeline();
        
        // 创建初始图表
        createBubbleChart(processedData, years[currentYearIndex]);
        
        // Setup event listeners
        document.getElementById('playButton').addEventListener('click', togglePlay);
        
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