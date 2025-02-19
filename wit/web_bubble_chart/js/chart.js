// Global variables
let isPlaying = true;
let playInterval;
let currentYearIndex = 0;
let years;
let processedData;
let timeline;
let selectedCompanies = appConfig.defaultSelectedCompanies;
let backgroundTrace;
let currentTraces;
let layout;
let config;

// Create layout configuration
layout = {
    xaxis: {
        title: {
            text: 'Share of Online Bookings (%)',
            font: {
                family: 'Monda',
                size: 14
            },
            standoff: 10
        },
        tickformat: ',.0%',
        range: [-0.05, 1.05],
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
            size: 12
        },
        tickmode: 'array',
        ticktext: ['0%', '20%', '40%', '60%', '80%', '100%'],
        tickvals: [0, 0.2, 0.4, 0.6, 0.8, 1.0],
        fixedrange: true
    },
    yaxis: {
        title: {
            text: 'Online Bookings (USD bn)',
            font: {
                family: 'Monda',
                size: 14
            },
            standoff: 10
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
            size: 12
        },
        tickmode: 'array',
        ticktext: ['0.1', '0.5', '1', '5', '10', '40', '90', '160', '250', '400', '500'],
        tickvals: [0.1, 0.5, 1, 5, 10, 40, 90, 160, 250, 400, 500],
        range: [Math.log10(0.05), Math.log10(500)],
        autorange: false,
        fixedrange: true
    },
    showlegend: false,
    margin: {
        l: 80,
        r: 20,
        t: 100,
        b: 150
    },
    height: 650,
    annotations: [
        {
            text: 'Source: Phocal Point',
            x: 0,
            y: -0.25,
            xref: 'paper',
            yref: 'paper',
            showarrow: false,
            font: {
                family: 'Monda',
                size: 12,
                color: 'rgba(0, 0, 0, 0.6)'
            },
            xanchor: 'left'
        },
        {
            text: 'Note: Online bookings comprise of online direct and via OTA.',
            x: 0,
            y: -0.29,
            xref: 'paper',
            yref: 'paper',
            showarrow: false,
            font: {
                family: 'Monda',
                size: 12,
                color: 'rgba(0, 0, 0, 0.6)'
            },
            xanchor: 'left'
        },
        {
            text: '2005-2008 figures extrapolated based on GDP trends for the period. 2024-2027 figures are estimates.',
            x: 0,
            y: -0.33,
            xref: 'paper',
            yref: 'paper',
            showarrow: false,
            font: {
                family: 'Monda',
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
            family: 'Monda',
            size: 12
        },
        bordercolor: '#666'
    },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    autosize: true
};

// Create config
config = {
    responsive: true,
    displayModeBar: false,
    staticPlot: true
};

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
    const margin = { left: 80, right: 80 };
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

// Function to process Excel data
async function fetchData() {
    try {
        const response = await fetch('travel_market_summary.xlsx');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const arrayBuffer = await response.arrayBuffer();
        const data = new Uint8Array(arrayBuffer);
        
            const workbook = XLSX.read(data, { type: 'array' });
            const sheet = workbook.Sheets['Visualization Data'];
            if (!sheet) {
                throw new Error("Sheet 'Visualization Data' not found");
            }
            
            const jsonData = XLSX.utils.sheet_to_json(sheet);

        // Process data
            const processedData = jsonData
            .filter(row => row['Region'] === 'APAC' && row['Market'] && row['Year'])
                .map(row => ({
                    Market: row['Market'],
                    Year: row['Year'],
                OnlinePenetration: row['Online Penetration'] / 100, // Convert to decimal
                    OnlineBookings: row['Online Bookings'],
                    GrossBookings: row['Gross Bookings']
                }));

            return processedData;
    } catch (error) {
        console.error('Error loading data:', error);
        return [];
    }
}

// Function to create bubble chart
function createBubbleChart(data, year) {
    const yearData = data.filter(d => d.Year === year && selectedCompanies.includes(d.Market));
    
    // 只在2005年输出原始数据和计算后的值
    if (year === 2005) {
        yearData.forEach(d => {
            const rawValue = d.OnlineBookings;
            const scaledValue = rawValue / 1e9; // 直接转换为十亿
            console.log(`${d.Market}:`);
            console.log(`  Raw: ${rawValue}`);
            console.log(`  Scaled (bn): ${scaledValue}`);
            console.log('-------------------');
        });
    }

    // 输出中国的数据
    const chinaData = yearData.find(d => d.Market === 'China');
    if (chinaData) {
        const rawValue = chinaData.OnlineBookings;
        const scaledValue = rawValue / 1e9; // 转换为十亿
        const safeValue = Math.max(scaledValue, 0.1);
        const logValue = Math.log10(safeValue);
        console.log(`Year ${year} China:`);
        console.log(`  Raw Online Bookings: ${rawValue.toLocaleString()}`);
        console.log(`  Billions: ${scaledValue.toFixed(2)}B`);
        console.log(`  Log Value: ${logValue.toFixed(2)}`);
        console.log('-------------------');
    }

    // Create background text trace
    backgroundTrace = {
        x: [0.5],
        y: [10],
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

    // Create base scatter plot with invisible markers
    const trace = {
        x: yearData.map(d => d.OnlinePenetration),
        y: yearData.map(d => {
            const rawValue = d.OnlineBookings / 1e9;
            const safeValue = Math.max(rawValue, 0.1);
            return Math.log10(safeValue);
        }),
        mode: 'none',  // 完全移除所有可视元素
        showlegend: false,
        hoverinfo: 'none',
        visible: true,
        customdata: yearData.map(d => [
            d.GrossBookings / 1e9,
            d.OnlineBookings / 1e9
        ]),
        hovertemplate: '<b>%{text}</b><br>' +
                      'Online Penetration: %{x:.1%}<br>' +
                      'Online Bookings: $%{customdata[1]:.1f}B<br>' +
                      'Gross Bookings: %{customdata[0]:$,.1f}B<br>' +
                      '<extra></extra>'
    };

    // Create images
    const images = yearData.map(d => {
        const logo = appConfig.companyLogos[d.Market];
        if (!logo) {
            console.warn('No logo found for market:', d.Market);
            return null;
        }

        const maxGrossBookings = d3.max(data, d => d.GrossBookings);
        const relativeSize = Math.pow(d.GrossBookings / maxGrossBookings, 0.4);
        const targetSize = relativeSize * 0.5 + 0.02;

        // 计算对数坐标系下的y值
        const rawValue = d.OnlineBookings / 1e9;
        const safeValue = Math.max(rawValue, 0.1);
        const yValue = Math.log10(safeValue);

        // 只在2005年输出调试信息
        if (year === 2005) {
            console.log(`${d.Market}:`);
            console.log(`  Raw Online Bookings: ${d.OnlineBookings}`);
            console.log(`  Converted to billions: ${rawValue}`);
            console.log(`  Safe value: ${safeValue}`);
            console.log(`  Final log10 y-value: ${yValue}`);
            console.log(`  Pixel position: ${layout.yaxis.range[0] + (Math.log10(safeValue) / Math.log10(1000)) * (layout.yaxis.range[1] - layout.yaxis.range[0])}`);
            console.log('-------------------');
        }

        return {
            source: logo,
            xref: "x",
            yref: "y",
            x: d.OnlinePenetration,
            y: yValue,
            sizex: targetSize,
            sizey: targetSize,
            sizing: "contain",
            opacity: 0.8,
            layer: "above",
            xanchor: "center",
            yanchor: "middle"
        };
    }).filter(Boolean);

    // Check if the chart already exists
    const chartDiv = document.getElementById('bubble-chart');
    if (!chartDiv.data) {
        console.log('Initial chart creation');
        // First time creation
        Plotly.newPlot('bubble-chart', [backgroundTrace, trace], {
            ...layout,
            images: images,
            datarevision: Date.now()  // 添加数据修订标记
        }, {
            ...config,
            doubleClick: false,  // 禁用双击事件
            displayModeBar: false,  // 确保不显示模式栏
            staticPlot: true  // 使用静态绘图模式
        }).then(() => {
            Plotly.relayout('bubble-chart', { images });
        });
        // Create race chart
        createRaceChart(data, year);
    } else {
        // Update existing chart with animation
        Plotly.animate('bubble-chart', {
            data: [backgroundTrace, trace],
            layout: {
                ...layout,
                images,
                datarevision: Date.now()  // 添加数据修订标记
            }
        }, {
            transition: {
                duration: 400,
                easing: 'cubic-in-out'
            },
            frame: {
                duration: 400,
                redraw: true
            }
        });
        // Update race chart
        updateRaceChart(data, year);
    }
}

// Initialize the visualization
async function init() {
    try {
        processedData = await fetchData();
        
        if (!processedData || processedData.length === 0) {
            throw new Error('No data loaded');
        }
        
        years = [...new Set(processedData.map(d => d.Year))].sort();
        currentYearIndex = years.indexOf(appConfig.chart.defaultYear);
        
        // Create timeline
        createTimeline();
        
        // Create initial chart
        createBubbleChart(processedData, years[currentYearIndex]);
        
        // Start animation
        setTimeout(() => {
            isPlaying = true;
            let lastTime = 0;
            let lastUpdateTime = 0;
            const animationDuration = 20000;
            const updateInterval = 500;
            let lastYearIndex = currentYearIndex;
        
            function animate(currentTime) {
                if (!isPlaying) {
                    return;
                }

                if (!lastTime) lastTime = currentTime;
                const elapsed = currentTime - lastTime;
                
                const totalProgress = (elapsed % animationDuration) / animationDuration;
                const indexFloat = totalProgress * (years.length - 1);
                const currentIndex = Math.floor(indexFloat);

                // Update timeline marker smoothly
                if (timeline && timeline.triangle) {
                    const nextIndex = (currentIndex + 1) % years.length;
                    const progress = indexFloat - currentIndex;
                    const currentX = timeline.scale(years[currentIndex]);
                    const nextX = timeline.scale(years[nextIndex]);
                    const interpolatedX = currentX + (nextX - currentX) * progress;
                    timeline.triangle.attr('transform', `translate(${interpolatedX}, -10) rotate(180)`);
                }

                // Only update chart when year changes and enough time has passed
                if (currentTime - lastUpdateTime >= updateInterval && currentIndex !== lastYearIndex) {
                    lastUpdateTime = currentTime;
                    lastYearIndex = currentIndex;
                    
                    const currentYearData = processedData.filter(d => d.Year === years[currentIndex]);
                    createBubbleChart(currentYearData, years[currentIndex]);
                }

                requestAnimationFrame(animate);
            }

            requestAnimationFrame(animate);
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