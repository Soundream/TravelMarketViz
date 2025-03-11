// Global variables
let isPlaying = true;
let currentYearIndex = 0;
let years;
let processedData;
let timeline;
let selectedCompanies = appConfig.defaultSelectedCompanies;
let layout;
let config;

// Add export functions
let mediaRecorder;
let recordedChunks = [];

// Function to load image and convert to base64
async function loadBackgroundImage() {
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.crossOrigin = "Anonymous";
        img.onload = function() {
            const canvas = document.createElement('canvas');
            canvas.width = img.width;
            canvas.height = img.height;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0);
            const base64String = canvas.toDataURL();
            layout.images = [{
                source: base64String,
                xref: "paper",
                yref: "paper",
                x: 0,
                y: 1,
                sizex: 1,
                sizey: 1,
                sizing: "stretch",
                opacity: 0.15,
                layer: "below"
            }];
            console.log("Background image loaded successfully!");
            resolve();
        };
        img.onerror = function(error) {
            console.error('Error loading image:', error);
            reject(error); // Changed to reject on error
        };
        img.src = '../../assets/mascot.png'; // Fixed path to point to correct location
    });
}

// Create layout configuration
layout = {
    xaxis: {
        title: {
            text: 'Share of Online Bookings (%)',
            font: {
                family: 'Monda',
                size: 20
            },
            standoff: 15
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
        linewidth: 2,
        tickfont: {
            family: 'Monda',
            size: 18
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
                size: 20
            },
            standoff: 15
        },
        type: 'log',
        showgrid: true,
        gridcolor: '#eee',
        gridwidth: 1,
        zeroline: true,
        zerolinecolor: '#eee',
        showline: true,
        linecolor: '#ccc',
        linewidth: 2,
        tickfont: {
            family: 'Monda',
            size: 18
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
        l: 100,
        r: 30,
        t: 30,
        b: 80
    },
    height: 700,
    width: 1600,
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    autosize: false
};

// Create config
config = {
    responsive: true,
    displayModeBar: false,
    staticPlot: false
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
    } else if (yearNum >= 2021 && yearNum <= 2023) {
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

        // 获取所有年份和市场
        const allYears = [...new Set(processedData.map(d => d.Year))].sort();
        const allMarkets = [...new Set(processedData.map(d => d.Market))];

        // 处理缺失数据
        const interpolatedData = [];
        allMarkets.forEach(market => {
            const marketData = processedData.filter(d => d.Market === market);
            const marketYears = marketData.map(d => d.Year);

            allYears.forEach(year => {
                if (!marketYears.includes(year)) {
                    // 找到最近的前后年份数据
                    const prevYear = Math.max(...marketYears.filter(y => y < year));
                    const nextYear = Math.min(...marketYears.filter(y => y > year));
                    
                    if (prevYear && nextYear) {
                        const prevData = marketData.find(d => d.Year === prevYear);
                        const nextData = marketData.find(d => d.Year === nextYear);
                        
                        // 线性插值
                        const progress = (year - prevYear) / (nextYear - prevYear);
                        const interpolated = {
                            Market: market,
                            Year: year,
                            OnlinePenetration: prevData.OnlinePenetration + (nextData.OnlinePenetration - prevData.OnlinePenetration) * progress,
                            OnlineBookings: prevData.OnlineBookings + (nextData.OnlineBookings - prevData.OnlineBookings) * progress,
                            GrossBookings: prevData.GrossBookings + (nextData.GrossBookings - prevData.GrossBookings) * progress
                        };
                        interpolatedData.push(interpolated);
                    }
                }
            });
        });

        // 合并原始数据和插值数据
        const finalData = [...processedData, ...interpolatedData].sort((a, b) => {
            if (a.Year === b.Year) {
                return a.Market.localeCompare(b.Market);
            }
            return a.Year - b.Year;
        });

        return finalData;
    } catch (error) {
        console.error('Error loading data:', error);
        return [];
    }
}

// Function to create bubble chart
function createBubbleChart(data, year) {
    const yearData = data.filter(d => d.Year === year && selectedCompanies.includes(d.Market));
    
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
        const relativeSize = Math.pow(d.GrossBookings / maxGrossBookings, 0.6);
        const targetSize = relativeSize * 0.8 + 0.01;

        // 计算对数坐标系下的y值
        const rawValue = d.OnlineBookings / 1e9;
        const safeValue = Math.max(rawValue, 0.1);
        const yValue = Math.log10(safeValue);

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
        Plotly.newPlot('bubble-chart', [trace], {
            ...layout,
            images: images,
            datarevision: Date.now()
        }, {
            ...config,
            doubleClick: false,
            displayModeBar: false,
            staticPlot: false
        }).then(() => {
            Plotly.relayout('bubble-chart', { images });
        });
        // Create race chart
        createRaceChart(data, year);
    } else {
        // Update existing chart with animation
        Plotly.animate('bubble-chart', {
            data: [trace],
            layout: {
                ...layout,
                images: images,
                datarevision: Date.now()
            }
        }, {
            transition: {
                duration: 0,
                easing: 'linear'
            },
            frame: {
                duration: 0,
                redraw: true
            },
            mode: 'immediate'
        });
        // Update race chart
        updateRaceChart(data, year);
    }
}

// Function to export current chart
function exportChart() {
    const bubbleChart = document.getElementById('bubble-chart');
    const raceChart = document.getElementById('race-chart');
    const timeline = document.getElementById('timeline');
    
    // 固定导出尺寸
    const COMBINED_WIDTH = 1920;
    const COMBINED_HEIGHT = 700;
    const BUBBLE_WIDTH = 1500;
    const RACE_WIDTH = 420;
    const RACE_HEIGHT = 500;
    const TIMELINE_HEIGHT = 60;

    // 创建一个临时canvas来合并图表（不包含时间轴）
    const chartCanvas = document.createElement('canvas');
    chartCanvas.width = COMBINED_WIDTH;
    chartCanvas.height = COMBINED_HEIGHT;
    const chartCtx = chartCanvas.getContext('2d');
    chartCtx.fillStyle = 'rgba(0,0,0,0)';
    chartCtx.fillRect(0, 0, COMBINED_WIDTH, COMBINED_HEIGHT);

    // 创建一个临时canvas用于时间轴
    const timelineCanvas = document.createElement('canvas');
    timelineCanvas.width = COMBINED_WIDTH;
    timelineCanvas.height = TIMELINE_HEIGHT;
    const timelineCtx = timelineCanvas.getContext('2d');
    timelineCtx.fillStyle = 'rgba(0,0,0,0)';
    timelineCtx.fillRect(0, 0, COMBINED_WIDTH, TIMELINE_HEIGHT);

    // 导出所有图表
    return Promise.all([
        // 导出气泡图
        Plotly.toImage(bubbleChart, {
            format: 'png',
            width: BUBBLE_WIDTH,
            height: COMBINED_HEIGHT,
            scale: 1
        }),
        // 导出竞赛图
        Plotly.toImage(raceChart, {
            format: 'png',
            width: RACE_WIDTH,
            height: RACE_HEIGHT,
            scale: 1
        }),
        // 导出时间轴（包含当前状态）
        new Promise(resolve => {
            // 获取当前的时间轴状态
            const svgString = new XMLSerializer().serializeToString(timeline.querySelector('svg'));
            const DOMURL = window.URL || window.webkitURL || window;
            const img = new Image();
            const svg = new Blob([svgString], {type: 'image/svg+xml;charset=utf-8'});
            const url = DOMURL.createObjectURL(svg);
            
            img.onload = function() {
                timelineCtx.drawImage(img, 0, 0, COMBINED_WIDTH, TIMELINE_HEIGHT);
                DOMURL.revokeObjectURL(url);
                resolve(timelineCanvas.toDataURL('image/png'));
            };
            img.src = url;
        })
    ]).then(([bubbleImage, raceImage, timelineImage]) => {
        return new Promise((resolve) => {
            // 加载气泡图
            const bubbleImg = new Image();
            bubbleImg.onload = () => {
                chartCtx.drawImage(bubbleImg, 0, 0);
                
                // 加载竞赛图
                const raceImg = new Image();
                raceImg.onload = () => {
                    // 将竞赛图垂直居中放置
                    const yOffset = (COMBINED_HEIGHT - RACE_HEIGHT) / 2;
                    chartCtx.drawImage(raceImg, BUBBLE_WIDTH, yOffset);
                    
                    // 返回合并后的图像和时间轴
                    resolve({
                        chartImage: chartCanvas.toDataURL('image/png'),
                        timelineImage: timelineImage,
                        time: Date.now()
                    });
                };
                raceImg.src = raceImage;
            };
            bubbleImg.src = bubbleImage;
        });
    });
}

// Initialize the visualization
async function init() {
    try {
        // 加载数据
        data = await d3.csv('data/travel_market_summary.csv');
        
        // 数据预处理
        data.forEach(d => {
            d.Year = +d.Year;
            d.GrossBookings = +d.GrossBookings;
            d.OnlineBookings = +d.OnlineBookings;
            d.OnlinePenetration = +d.OnlinePenetration;
        });

        // 获取所有年份并排序
        years = [...new Set(data.map(d => d.Year))].sort();
        currentYearIndex = 0;

        // 创建初始图表
        createBubbleChart(data, years[currentYearIndex]);
        createRaceChart(data, years[currentYearIndex]);

        // 创建时间轴
        createTimeline();

        // 开始循环播放
        playAnimation();

    } catch (error) {
        console.error('Error loading the data:', error);
    }
}

function playAnimation() {
    if (!data || years.length === 0) return;

    // 更新图表
    createBubbleChart(data, years[currentYearIndex]);
    updateRaceChart(data, years[currentYearIndex]);
    updateTimeline(years[currentYearIndex]);
    
    // 更新年份索引
    currentYearIndex = (currentYearIndex + 1) % years.length;

    // 设置下一帧动画
    setTimeout(playAnimation, 1000);
}

// 启动可视化
document.addEventListener('DOMContentLoaded', init); 