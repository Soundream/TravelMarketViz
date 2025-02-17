// Global variables
let isPlaying = false;
let playInterval;
let currentYearIndex = 0;
let years;
let processedData;
let timeline;

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
            .duration(1000)
            .attr('transform', `translate(${timeline.scale(year)}, -10) rotate(180)`);
    }
}

// Function to process Excel data by region
function processDataByRegion(jsonData) {
    console.log('Processing data:', jsonData); // Debug log
    const regionData = {};
    
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

    const trace = {
        x: yearData.map(d => d['Online Penetration'] * appConfig.dataProcessing.onlinePenetrationMultiplier),
        y: yearData.map(d => d['Online Bookings'] * appConfig.dataProcessing.bookingsScaleFactor),
        mode: 'markers+text',
        text: yearData.map(d => d.Region),
        textposition: 'top center',
        hoverinfo: 'text',
        hovertext: yearData.map(d => `
            <b>${d.Region}</b><br>
            Online Penetration: ${(d['Online Penetration'] * 100).toFixed(1)}%<br>
            Online Bookings: $${(d['Online Bookings'] * appConfig.dataProcessing.bookingsScaleFactor).toFixed(1)}B<br>
            Gross Bookings: $${(d['Gross Bookings'] * appConfig.dataProcessing.bookingsScaleFactor).toFixed(1)}B
        `),
        marker: {
            size: yearData.map(d => {
                const size = Math.sqrt(d['Gross Bookings'] * appConfig.dataProcessing.bookingsScaleFactor) * 3;
                return Math.max(appConfig.chart.minBubbleSize, 
                       Math.min(appConfig.chart.maxBubbleSize, size));
            }),
            color: yearData.map(d => appConfig.regionColors[d.Region]),
            opacity: 0.8,
            line: {
                color: 'white',
                width: 2
            }
        },
        type: 'scatter'
    };

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
            range: [0, Math.ceil(allYears.maxOnlinePenetration * appConfig.dataProcessing.onlinePenetrationMultiplier / 10) * 10],
            gridcolor: '#E5E5E5',
            zerolinecolor: '#E5E5E5',
            showgrid: true,
            gridwidth: 1,
            tickfont: {
                family: 'Open Sans',
                size: 12
            }
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
            range: [0, Math.log10(allYears.maxOnlineBookings * appConfig.dataProcessing.bookingsScaleFactor * 2)], // 扩大范围
            gridcolor: '#E5E5E5',
            zerolinecolor: '#E5E5E5',
            showgrid: true,
            gridwidth: 1,
            tickfont: {
                family: 'Open Sans',
                size: 12
            }
        },
        showlegend: false,
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
            r: 40,
            t: 80,
            b: 60
        }
    };

    const config = {
        responsive: true,
        displayModeBar: false
    };

    // 使用 Plotly.animate 实现平滑动画
    if (document.getElementById('bubble-chart').data) {
        Plotly.animate('bubble-chart', {
            data: [trace],
            layout: layout
        }, {
            transition: {
                duration: 1500,
                easing: 'cubic-in-out'
            },
            frame: {
                duration: 1500,
                redraw: true
            }
        });
    } else {
        Plotly.newPlot('bubble-chart', [trace], layout, config);
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
        playInterval = setInterval(() => {
            currentYearIndex = (currentYearIndex + 1) % years.length;
            createBubbleChart(processedData, years[currentYearIndex]);
        }, appConfig.animation.frameDelay);
    } else {
        playButton.innerHTML = '<i class="fas fa-play"></i>';
        clearInterval(playInterval);
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