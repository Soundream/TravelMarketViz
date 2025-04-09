// Global variables
let isPlaying = true; // 修改为默认播放状态
let playInterval;
let currentYearIndex = 0;
let years;
let processedRegionData;
let processedCountryData;
let timeline;
let uniqueRegions;
let selectedCountries;
let backgroundTrace;
let currentTraces;
let layout;
let config;
let flagImages = {}; // 新增：存储国旗图像对象
let resizeTimeout; // 新增：用于处理窗口调整大小事件

// Debug logger function - logs to both console and debug panel
function logMessage(message, type = 'info') {
    // Log to console
    if (type === 'error') {
        console.error(message);
    } else if (type === 'warn') {
        console.warn(message);
    } else {
        console.log(message);
    }
    
    // Also log to debug panel if it exists
    const debugConsole = document.getElementById('debug-console');
    if (debugConsole) {
        const logLine = document.createElement('div');
        logLine.className = `log-line log-${type}`;
        logLine.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
        debugConsole.appendChild(logLine);
        debugConsole.scrollTop = debugConsole.scrollHeight;
    }
}

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
    console.log('Creating timeline with years:', years);
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
    
    console.log('Timeline created successfully');
}

// Function to update timeline
function updateTimeline(year) {
    console.log('Updating timeline to year:', year);
    if (timeline && timeline.triangle) {
        timeline.triangle
            .transition()
            .duration(appConfig.animation.duration)
            .attr('transform', `translate(${timeline.scale(year)}, -10) rotate(180)`);
    } else {
        console.warn('Timeline or triangle is undefined');
    }
}

// 添加统一的气泡大小计算函数
function computeBubbleSize(grossBookings, maxGrossBookings, minSize = 10, maxSize = 120) {
    // 处理无效值
    if (!grossBookings || !maxGrossBookings || maxGrossBookings === 0 || 
        isNaN(grossBookings) || isNaN(maxGrossBookings)) {
        console.warn('Invalid gross bookings values:', { grossBookings, maxGrossBookings });
        return minSize;
    }

    // 平滑映射 + 范围限制
    const ratio = Math.sqrt(grossBookings / maxGrossBookings);
    const clamped = Math.max(0, Math.min(1, ratio)); // 限制在 [0, 1]
    const size = minSize + (maxSize - minSize) * clamped;

    // Debug 日志 - 使用 window.debug 标志来控制是否输出调试信息
    if (window.debug) {
        console.debug('Bubble size calculation:', {
            grossBookings,
            maxGrossBookings,
            ratio,
            clamped,
            finalSize: size
        });
    }

    return size;
}

// Function to process Excel data by region
function processDataByRegion(jsonData) {
    console.log('Processing region data with', jsonData.length, 'rows'); // Debug log
    const regionData = {};
    
    // Get unique regions, now including Asia-Pacific
    uniqueRegions = [...new Set(jsonData.map(row => {
        // Map old region names to new ones
        const region = row['Region'];
        if (region === 'APAC') return 'Asia-Pacific';
        if (region === 'LATAM') return 'Latin America';
        if (region === 'Middle East') return 'Middle East (sum)';
        return region;
    }))];
    
    console.log('Unique regions:', uniqueRegions);
    
    jsonData.forEach(row => {
        const year = row['Year'];
        let region = row['Region'];
        // Map old region names to new ones
        if (region === 'APAC') region = 'Asia-Pacific';
        if (region === 'LATAM') region = 'Latin America';
        if (region === 'Middle East') region = 'Middle East (sum)';
        
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
    
    console.log('Processed region data:', processedData.length, 'entries'); // Debug log
    return processedData;
}

// Function to process Excel data by country (similar to web_bubble_chart)
function processDataByCountry(jsonData) {
    console.log('Processing country data with', jsonData.length, 'rows'); // Debug log
    
    // Set selected countries from config
    selectedCountries = appConfig.defaultSelectedCountries || [];
    console.log('Selected countries:', selectedCountries);
    
    // Modify the data processing logic to ensure that the Middle Eastern countries are included and processed correctly
    const middleEastCountriesData = jsonData
        .filter(row => {
            // Filter for Middle Eastern region with market and year data
            if (!['Egypt', 'Qatar', 'Rest of Middle East', 'Saudi Arabia', 'U.A.E.', 'Malaysia', 'Indonesia'].includes(row['Market']) || !row['Year']) {
                return false;
            }
            
            // Standardize market name for matching
            let market = row['Market'];

            // Print original data
            console.error(`Original data - ${row['Year']} ${market}:`, {
                'Country/Region': market,
                'Year': row['Year'],
                'Online Bookings in Excel': row['Online Bookings'],
                'Gross Bookings in Excel': row['Gross Bookings'],
                'Online Penetration in Excel': ((row['Online Bookings'] / row['Gross Bookings']) * 100).toFixed(1) + '%'
            });
            
            return true;
        })
        .map(row => {
            const processedData = {
                Market: row['Market'],
                Year: row['Year'],
                OnlinePenetration: row['Online Bookings'] / row['Gross Bookings'],
                OnlineBookings: row['Online Bookings'],
                GrossBookings: row['Gross Bookings']
            };

            // Print processed data
            console.error(`Processed data for Race Chart - ${row['Year']} ${row['Market']}:`, {
                'Country/Region': row['Market'],
                'Year': row['Year'],
                'Online Bookings for Race Chart': processedData.OnlineBookings,
                'Gross Bookings for Race Chart': processedData.GrossBookings,
                'Online Penetration for Race Chart': (processedData.OnlinePenetration * 100).toFixed(1) + '%'
            });

            return processedData;
        });

    // Store Middle Eastern countries data globally so race-chart.js can access it
    window.processedCountriesData = middleEastCountriesData;
    
    // Process data for APAC countries - 这里保留所有国家数据，后续在可视化时再过滤
    const processedData = jsonData
        .filter(row => row['Region'] === 'APAC' && row['Market'] && row['Year'])
        .map(row => {
            // Standardize market names
            let market = row['Market'];
            if (market === 'Australia-New Zealand' || market === 'Australia/New Zealand') {
                market = 'Australia & New Zealand';
            }
            return {
                Year: parseInt(row['Year']),
                Country: market,
                'Gross Bookings': row['Gross Bookings'] || 0,
                'Online Bookings': row['Online Bookings'] || 0,
                'Online Penetration': (row['Online Bookings'] / row['Gross Bookings']) || 0
            };
        });
    
    console.log('Processed country data:', processedData.length, 'entries'); // Debug log
    console.log('Sample country data:', processedData.slice(0, 2));
    return processedData;
}

// Function to create the bubble chart with both regions and countries
function createBubbleChart(regionData, countryData, year) {
    logMessage('Creating chart for year: ' + year);
    
    // Filter data for the current year
    const yearRegionData = regionData.filter(d => d.Year === year);
    
    // 需要在气泡图中过滤掉的国家 - 但不在总和计算中排除
    const excludedCountries = ['Taiwan', 'Hong Kong', 'Macau'];
    
    // 最小在线预订值阈值(十亿)
    const minOnlineBookingsThreshold = 0.2;
    
    // Filter country data - 仅在气泡图显示中排除特定国家
    const yearCountryData = countryData.filter(d => {
        const matchesYear = d.Year === year;
        const isSelected = selectedCountries.includes(d.Country);
        const isExcluded = excludedCountries.includes(d.Country);
        const hasEnoughOnlineBookings = d['Online Bookings'] >= minOnlineBookingsThreshold;
        
        return matchesYear && isSelected && !isExcluded && hasEnoughOnlineBookings;
    });
    logMessage('Year country data count: ' + yearCountryData.length);
    
    // 计算全局最大 Gross Bookings（排除无效值）
    const allData = [...regionData, ...countryData].filter(d => 
        d['Gross Bookings'] && !isNaN(d['Gross Bookings']) && d['Gross Bookings'] > 0
    );
    const maxGrossBookings = d3.max(allData, d => d['Gross Bookings']);
    console.log('Global max Gross Bookings:', maxGrossBookings);

    // 定义y轴范围
    const yAxisRange = [Math.log10(0.1), Math.log10(800)];
    
    // 创建背景文字
    backgroundTrace = {
        y: [50],  // 水平居中
        x: [Math.pow(10, (yAxisRange[0] + yAxisRange[1]) / 2)],  // 在对数坐标系中垂直居中
        mode: 'text',
        text: [getEraText(year)],
        textposition: 'middle center',
        textfont: {
            size: 60,
            family: 'Monda',
            color: 'rgba(200,200,200,0.3)'
        },
        hoverinfo: 'skip',
        showlegend: false
    };

    // 创建区域气泡轨迹
    const regionTraces = uniqueRegions.map(region => {
        const regionData = yearRegionData.filter(d => d.Region === region);
        const colorKey = region === 'Asia-Pacific' ? 'Asia-Pacific' : region;

        // 获取所有区域的 Gross Bookings 并排序
        const allRegionsGrossBookings = yearRegionData.map(d => ({
            region: d.Region,
            grossBookings: d['Gross Bookings']
        }));
        allRegionsGrossBookings.sort((a, b) => b.grossBookings - a.grossBookings);
        
        // 检查当前区域是否在后三名
        const isSmallRegion = allRegionsGrossBookings.findIndex(d => d.region === region) >= allRegionsGrossBookings.length - 3;
        
        return {
            name: region,
            y: regionData.map(d => d['Online Penetration'] * 100),
            x: regionData.map(d => d['Online Bookings'] * appConfig.dataProcessing.bookingsScaleFactor),
            mode: 'markers',
            hoverinfo: 'text',
            hovertext: regionData.map(d => `
                <b style="font-family: Monda">${d.Region}</b><br>
                <span style="font-family: Monda">Share of Online Bookings: ${(d['Online Penetration'] * 100).toFixed(1)}%<br>
                Online Bookings: $${(d['Online Bookings']).toFixed(1)}B<br>
                Gross Bookings: $${(d['Gross Bookings']).toFixed(1)}B<br>
                Bubble Size: ${computeBubbleSize(d['Gross Bookings'], maxGrossBookings, 
                    appConfig.chart.minBubbleSize, appConfig.chart.maxBubbleSize).toFixed(1)}</span>
            `),
            marker: {
                size: regionData.map(d => {
                    let size = computeBubbleSize(
                        d['Gross Bookings'],
                        maxGrossBookings,
                        appConfig.chart.minBubbleSize || 10,
                        appConfig.chart.maxBubbleSize || 120
                    );
                    
                    // 如果是较小的区域，增加气泡大小
                    if (isSmallRegion) {
                        // 增加 50% 的大小，但不超过中等大小气泡
                        const mediumSize = (appConfig.chart.maxBubbleSize + appConfig.chart.minBubbleSize) / 2;
                        size = Math.min(size * 1.15, mediumSize);
                    }
                    
                    console.log(`${year} - Region ${d.Region} bubble:`, {
                        grossBookings: d['Gross Bookings'],
                        size: size,
                        isSmallRegion: isSmallRegion
                    });
                    return size;
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
    
    // 更新组合国家轨迹
    const combinedCountryTrace = {
        name: 'Country Bubbles',
        x: [],
        y: [],
        mode: 'markers',  // 移除 text 模式
        hoverinfo: 'text',
        hovertext: [],
        marker: {
            size: [],
            color: 'rgba(255,255,255,0)',
            line: {
                color: 'rgba(200,200,200,0)',
                width: 0
            }
        },
        showlegend: false,
        _flagSizes: [],
        _countries: []
    };

    // 获取所有国家的 Gross Bookings 并排序
    const allCountriesGrossBookings = yearCountryData.map(d => ({
        country: d.Country,
        grossBookings: d['Gross Bookings']
    }));
    allCountriesGrossBookings.sort((a, b) => b.grossBookings - a.grossBookings);

    // 填充组合轨迹的数据
    yearCountryData.forEach(d => {
        const yPos = d['Online Penetration'] * 100;
        const xPos = d['Online Bookings'] * appConfig.dataProcessing.bookingsScaleFactor;
        
        // 检查当前国家是否在后五名
        const isSmallCountry = allCountriesGrossBookings.findIndex(c => c.country === d.Country) >= allCountriesGrossBookings.length - 5;
        
        // 使用统一的气泡大小计算函数
        let size = computeBubbleSize(
            d['Gross Bookings'],
            maxGrossBookings,
            appConfig.chart.minBubbleSize || 10,
            appConfig.chart.maxBubbleSize || 120
        );

        // 如果是较小的国家，减小气泡大小
        if (isSmallCountry) {
            // 减小 30% 的大小，但不小于最小气泡尺寸
            const minSize = appConfig.chart.minBubbleSize || 10;
            size = Math.max(size * 0.7, minSize);
        }

        console.log(`${year} - Country ${d.Country} bubble:`, {
            grossBookings: d['Gross Bookings'],
            size: size,
            isSmallCountry: isSmallCountry
        });

        combinedCountryTrace.x.push(xPos);
        combinedCountryTrace.y.push(yPos);
        combinedCountryTrace._flagSizes.push(size);
        combinedCountryTrace._countries.push(d.Country);
        combinedCountryTrace.hovertext.push(`
            <b style="font-family: Monda">${d.Country}</b><br>
            <span style="font-family: Monda">Share of Online Bookings: ${(d['Online Penetration'] * 100).toFixed(1)}%<br>
            Online Bookings: $${(d['Online Bookings']).toFixed(1)}B<br>
            Gross Bookings: $${(d['Gross Bookings']).toFixed(1)}B<br>
            Bubble Size: ${size.toFixed(1)}</span>
        `);
        combinedCountryTrace.marker.size.push(size);
    });

    // 更新标志轨迹
    const flagTraces = yearCountryData.map(d => {
        const yPos = d['Online Penetration'] * 100;
        const xPos = d['Online Bookings'] * appConfig.dataProcessing.bookingsScaleFactor;
        const logoUrl = appConfig.countryLogos[d.Country];
        
        if (!logoUrl) return null;

        return {
            name: d.Country + ' flag',
            x: [xPos],
            y: [yPos],
            mode: 'markers',
            type: 'scatter',
            hoverinfo: 'skip',
            showlegend: false,
            marker: {
                size: 1,
                opacity: 0
            },
            customdata: [{
                logoUrl: './' + logoUrl.replace(/^[./]+/, ''),
                country: d.Country
            }]
        };
    }).filter(trace => trace !== null);

    // 合并所有轨迹
    const allTraces = [backgroundTrace, ...regionTraces, combinedCountryTrace, ...flagTraces];
    
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
            ticktext: ['0.1', '0.5', '1', '2', '5', '10', '20', '50', '100', '200', '500', '800'],
            tickvals: [0.1, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 800],
            range: [Math.log10(0.1), Math.log10(800)],
            autorange: false,
            showticklabels: true,
            ticks: 'outside',
            ticklen: 8,
            tickwidth: 1,
            tickcolor: '#ccc',
            fixedrange: true
        },
        yaxis: {
            title: {
                text: 'Share of Online Bookings (%)',
                font: {
                    family: 'Monda',
                    size: 22
                },
                standoff: 15
            },
            range: [-5, 105],
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
            tickcolor: '#ccc',
            fixedrange: true
        },
        showlegend: false,
        margin: {
            l: 80,
            r: 80,  // Increase right margin
            t: 80,
            b: 100
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
        autosize: true,
        font: {
            family: 'Monda'
        },
        transition: {
            duration: appConfig.animation.duration,
            easing: 'linear'
        },
        datarevision: Date.now()
    };

    // 初始化全局 config 变量
    config = {
        responsive: true,
        displayModeBar: false
    };

    logMessage(`Plotting chart with ${allTraces.length} traces (${flagTraces.length} flag traces)`);
    
    // 如果是第一次渲染，使用 newPlot，否则使用分步动画实现平滑过渡
    const chartDiv = document.getElementById('bubble-chart');
    
    if (!chartDiv.data) {
        // 初次渲染使用 newPlot
        Plotly.newPlot('bubble-chart', allTraces, layout, config).then(function() {
            logMessage('Chart created successfully');
            // 初始渲染后更新国旗图像
            updateFlagImagesFromTraces(chartDiv, 0); // 初始化不需要动画
        }).catch(error => {
            logMessage('Error creating chart: ' + error, 'error');
        });
    } else {
        // 使用 animate 一次性更新所有 traces（包括透明国旗点），实现平滑过渡
        const animationConfig = {
            transition: { 
                duration: appConfig.animation.duration, 
                easing: 'linear' 
            },
            frame: { 
                duration: appConfig.animation.duration,
                redraw: false // 避免不必要的重绘
            }
        };
        
        // 确保现有标记点能够平滑过渡
        try {
            // 对图表进行深度更新，确保所有元素都平滑过渡
            Plotly.animate('bubble-chart', {
                data: allTraces,
                traces: Array.from(Array(allTraces.length).keys()) // 更新所有轨迹
            }, animationConfig).then(() => {
                // 动画完成后更新国旗图像
                updateFlagImagesFromTraces(chartDiv, appConfig.animation.duration);
                logMessage('Chart and flag images updated with linear transition');
            }).catch(error => {
                logMessage('Error updating chart: ' + error, 'error');
            });
        } catch (error) {
            logMessage('Animation error, falling back to update: ' + error, 'warn');
            // 如果动画失败，回退到更新
            Plotly.update('bubble-chart', 
                {data: allTraces},
                layout
            ).then(() => {
                // 更新完成后更新国旗
                updateFlagImagesFromTraces(chartDiv);
            });
        }
    }

    // 更新时间轴
    updateTimeline(year);
    
    // 更新 race-chart
    try {
        if (typeof updateRaceChart === 'function') {
            updateRaceChart(regionData, year);
        }
    } catch (error) {
        logMessage('Error updating race chart: ' + error, 'error');
    }
}

// Add styles to the page for country flags
function addFlagStyles() {
    // Check if styles already exist
    if (document.getElementById('country-flag-styles')) return;
    
    // Create style element
    const style = document.createElement('style');
    style.id = 'country-flag-styles';
    style.textContent = `
        #bubble-chart {
            position: relative; /* 确保容器是定位上下文 */
        }
        .country-flag {
            position: absolute;
            pointer-events: none;
            z-index: 999;
            border-radius: 50%;
            object-fit: cover;
            transition-property: left, top, width, height, opacity;
            transition-timing-function: linear;
            transition-duration: ${appConfig?.animation?.duration || 800}ms;
            box-shadow: 0 0 1px rgba(0,0,0,0.3);
            will-change: left, top, width, height, opacity;
            backface-visibility: hidden;
        }
        
        .country-flag.entering {
            opacity: 0;
        }
    `;
    document.head.appendChild(style);
    logMessage('Added styles for country flags');
}

// 新函数：根据当前的透明标记点位置更新国旗图像
function updateFlagImagesFromTraces(chartDiv, duration = null, progress = 0) {
    const plotElement = chartDiv;
    if (!plotElement || !plotElement.data) {
        logMessage('Cannot update flag images: chart not initialized', 'error');
        return;
    }

    // 找到组合国家轨迹
    const countryTrace = plotElement.data.find(trace => 
        trace.name === 'Country Bubbles' && 
        Array.isArray(trace._countries));

    if (!countryTrace) {
        logMessage('Cannot find country trace', 'error');
        return;
    }

    // 获取图表区域信息
    const plotArea = chartDiv.querySelector('.subplot.xy');
    if (!plotArea) return;

    const plotRect = plotArea.getBoundingClientRect();
    const chartRect = chartDiv.getBoundingClientRect();
    const plotOffsetX = plotRect.left - chartRect.left;
    const plotOffsetY = plotRect.top - chartRect.top;
    const horizontalOffset = window.flagOffsetX || 47;
    const verticalOffset = window.flagOffsetY || 10;

    // 更新最小x值为0.2
    const minXValue = 0.2;

    // 更新每个国家的旗帜位置
    countryTrace._countries.forEach((country, index) => {
        if (!selectedCountries.includes(country)) return;

        const xData = countryTrace.x[index];
        const yData = countryTrace.y[index];
        
        // 获取或创建国旗图像元素
        let flagImg = flagImages[country];
        
        // 如果x值小于最小值，隐藏国旗
        if (xData < minXValue) {
            if (flagImg) {
                flagImg.style.opacity = '0';
                flagImg.style.visibility = 'hidden';
            }
            return;
        }

        const xPx = plotElement._fullLayout.xaxis.d2p(xData);
        const yPx = plotElement._fullLayout.yaxis.d2p(yData);
        const finalX = plotOffsetX + xPx + horizontalOffset;
        const finalY = plotOffsetY + yPx + verticalOffset;
        const bubbleSize = countryTrace._flagSizes[index];

        const logoUrl = appConfig.countryLogos[country];
        if (logoUrl) {
            // 如果是新创建的国旗或之前是隐藏状态，先淡入显示但不移动位置
            const isNewOrHidden = !flagImg || flagImg.style.visibility === 'hidden';
            
            createFlagImage(
                country,
                './' + logoUrl.replace(/^[./]+/, ''),
                finalX,
                finalY,
                bubbleSize,
                isNewOrHidden ? 0 : (duration || appConfig.animation.duration) // 新显示的国旗立即定位，不使用动画
            );
            
            // 确保国旗可见
            if (flagImg) {
                if (isNewOrHidden) {
                    // 新显示的国旗使用淡入效果
                    flagImg.style.transition = `opacity ${appConfig.animation.duration}ms linear`;
                    flagImg.style.visibility = 'visible';
                    setTimeout(() => {
                        flagImg.style.opacity = '1';
                    }, 10);
                } else {
                    // 已显示的国旗保持正常动画
                    flagImg.style.transition = `all ${duration || appConfig.animation.duration}ms linear`;
                    flagImg.style.opacity = '1';
                    flagImg.style.visibility = 'visible';
                }
            }
        }
    });
}

// 更新createFlagImage函数
function createFlagImage(country, logoUrl, x, y, size, duration) {
    const chartContainer = document.getElementById('bubble-chart');
    if (!chartContainer) return;
    
    const img = flagImages[country] || document.createElement('img');
    
    if (!flagImages[country]) {
        img.src = logoUrl;
        img.alt = country;
        img.className = 'country-flag';
        img.style.position = 'absolute';
        img.style.opacity = '0';
        img.style.visibility = 'hidden';
        chartContainer.appendChild(img);
        flagImages[country] = img;
        
        // 错误处理
        img.onerror = () => {
            logMessage(`Error loading flag image for ${country}: ${logoUrl}`, 'error');
            img.style.backgroundColor = 'rgba(200, 200, 200, 0.8)';
            img.style.border = '1px solid white';
        };
    }
    
    // 设置位置和大小
    img.style.left = `${Math.round(x - size/2)}px`;
    img.style.top = `${Math.round(y - size/2)}px`;
    img.style.width = `${Math.round(size)}px`;
    img.style.height = `${Math.round(size)}px`;
}

// Toggle Play/Pause Function
function togglePlay() {
    logMessage('Toggle play/pause. Current state: ' + isPlaying);
    isPlaying = !isPlaying;
    
    const playIcon = document.getElementById('playIcon');
    const pauseIcon = document.getElementById('pauseIcon');
    
    if (isPlaying) {
        logMessage('Starting animation');
        if (playIcon) playIcon.style.display = 'none';
        if (pauseIcon) pauseIcon.style.display = 'inline-block';
        
        if (playInterval) {
            clearInterval(playInterval);
        }
        
        // 创建动画控制器
        const animationController = {
            startTime: Date.now(),
            totalDuration: appConfig.animation.duration * years.length,
            frameDuration: appConfig.animation.duration,
            lastFrameTime: Date.now(),
            lastFlagUpdateTime: Date.now(),
            animationInProgress: false,
            currentTransform: null // 用于存储当前的变换状态
        };
        
        // 确保开始时国旗图像就正确定位
        const chartDiv = document.getElementById('bubble-chart');
        if (chartDiv && chartDiv.data) {
            updateFlagImagesFromTraces(chartDiv, 0);
        }
        
        // 使用requestAnimationFrame实现平滑动画
        const renderFrame = () => {
            if (!isPlaying) return;
            
            const now = Date.now();
            const elapsedSinceStart = now - animationController.startTime;
            const cyclePosition = (elapsedSinceStart % animationController.totalDuration) / animationController.totalDuration;
            const yearPosition = cyclePosition * years.length;
            const currentYearIndex = Math.floor(yearPosition);
            const nextYearIndex = (currentYearIndex + 1) % years.length;
            
            // 计算当前帧在两年之间的插值比例 (0-1)
            const frameProgress = yearPosition - currentYearIndex;
            
            // 获取当前年份和下一年份的数据
            const currentYear = years[currentYearIndex];
            const nextYear = years[nextYearIndex];
            
            // 仅在年份变化时更新主气泡图
            if (currentYearIndex !== window.lastYearIndex) {
                window.lastYearIndex = currentYearIndex;
                createBubbleChart(processedRegionData, processedCountryData, currentYear);
            }
            
            // 平滑更新国旗位置
            if (chartDiv && chartDiv.data && now - animationController.lastFlagUpdateTime >= 16) {
                const remainingDuration = animationController.frameDuration * (1 - frameProgress);
                updateFlagImagesFromTraces(chartDiv, remainingDuration, frameProgress);
                animationController.lastFlagUpdateTime = now;
            }
            
            requestAnimationFrame(renderFrame);
        };
        
        requestAnimationFrame(renderFrame);
        
    } else {
        logMessage('Stopping animation');
        if (playIcon) playIcon.style.display = 'inline-block';
        if (pauseIcon) pauseIcon.style.display = 'none';
        clearInterval(playInterval);
    }
}

// Function to display error messages
function showError(message) {
    logMessage(message, 'error');
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }
}

// Function to preload all country logo images
function preloadCountryLogos(callback) {
    if (!appConfig || !appConfig.countryLogos) {
        logMessage('No country logos found in config', 'warn');
        if (callback) callback();
        return;
    }
    
    const logoUrls = Object.values(appConfig.countryLogos);
    logMessage(`Preloading ${logoUrls.length} country logos`);
    
    let loadedCount = 0;
    const totalCount = logoUrls.length;
    
    // If no logos to load, call callback immediately
    if (totalCount === 0) {
        if (callback) callback();
        return;
    }
    
    // Preload each image
    Object.entries(appConfig.countryLogos).forEach(([country, url]) => {
        if (!url) {
            loadedCount++;
            logMessage(`No logo URL for country: ${country}`, 'warn');
            if (loadedCount === totalCount && callback) callback();
            return;
        }
        
        // Ensure path is correct
        let logoPath = url;
        if (!url.startsWith('http') && !url.startsWith('/') && !url.startsWith('./')) {
            logoPath = './' + url;
        }
        
        logMessage(`Attempting to load logo for ${country}: ${logoPath}`);
        
        const img = new Image();
        img.onload = () => {
            loadedCount++;
            logMessage(`Loaded logo ${loadedCount}/${totalCount}: ${country} (${logoPath})`);
            if (loadedCount === totalCount && callback) callback();
        };
        img.onerror = () => {
            loadedCount++;
            logMessage(`Failed to load logo for ${country}: ${logoPath}`, 'error');
            if (loadedCount === totalCount && callback) callback();
        };
        img.src = logoPath;
    });
}

// Add this function after preloadCountryLogos
function verifyCountryLogosConfiguration() {
    if (!appConfig || !appConfig.countryLogos) {
        logMessage('WARNING: appConfig.countryLogos is not defined. Country logos will not be displayed.', 'warn');
        return;
    }
    
    logMessage(`Country logos configuration contains ${Object.keys(appConfig.countryLogos).length} entries`);
    
    // Check configuration for selected countries
    if (selectedCountries && selectedCountries.length > 0) {
        const missingLogos = selectedCountries.filter(country => !appConfig.countryLogos[country]);
        if (missingLogos.length > 0) {
            logMessage(`WARNING: The following selected countries have no logo configured: ${missingLogos.join(', ')}`, 'warn');
        }
        
        // Log all country logo mappings for debugging
        logMessage('Country logo configuration:');
        selectedCountries.forEach(country => {
            const logo = appConfig.countryLogos[country];
            logMessage(`  ${country}: ${logo || 'No logo configured'}`, logo ? 'info' : 'warn');
        });
    }
}

// Main initialization function
async function init() {
    try {
        logMessage('Initializing visualization...');
        
        // 添加国旗样式
        addFlagStyles();
        
        // 添加窗口大小改变事件处理器
        window.addEventListener('resize', handleWindowResize);
        
        // Check if required elements exist
        if (!document.getElementById('bubble-chart')) {
            showError('Error: bubble-chart element not found in the DOM');
            return;
        }
        
        // Clear any previous error messages
        const errorDiv = document.getElementById('error-message');
        if (errorDiv) errorDiv.style.display = 'none';
        
        // Verify country logos configuration
        verifyCountryLogosConfiguration();
        
        // Ensure appConfig.countryLogos exists - if not, create it from the web_bubble_chart example
        if (!appConfig.countryLogos || Object.keys(appConfig.countryLogos).length === 0) {
            logMessage('WARNING: appConfig.countryLogos not found or empty, creating default configuration', 'warn');
            
            // Use the same logos as in web_bubble_chart
            appConfig.countryLogos = {
                "Singapore": "logos/Singapore Flag Icon.png",
                "China": "logos/China Flag Icon.png",
                "India": "logos/India Icon.png",
                "Indonesia": "logos/Indonesia Flag.png",
                "Malaysia": "logos/Malaysia Icon.png",
                "Thailand": "logos/Thailand Icon.png",
                "Vietnam": "logos/China Flag Icon.png",
                "Philippines": "logos/Singapore Flag Icon.png",
                "Japan": "logos/Japan Icon.png",
                "South Korea": "logos/Korea Icon.png",
                "Hong Kong": "logos/Hong Kong Icon.png",
                "Taiwan": "logos/Taiwan Icon.png",
                "Macau": "logos/Macau Icon.png",
                "Australia & New Zealand": "logos/Australia Icon.png"
            };
            
            logMessage('Created default country logos configuration with ' + Object.keys(appConfig.countryLogos).length + ' entries');
        }
        
        // Load Excel file
        logMessage('Loading Excel file...');
        const response = await fetch('travel_market_summary.xlsx');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const arrayBuffer = await response.arrayBuffer();
        const data = new Uint8Array(arrayBuffer);
        
        logMessage('Parsing Excel data...');
        const workbook = XLSX.read(data, { type: 'array' });
        logMessage('Available sheets: ' + workbook.SheetNames.join(', '));
        
        // Read visualization data sheet
        const sheetName = workbook.SheetNames.includes('Visualization Data') 
            ? 'Visualization Data' 
            : workbook.SheetNames[0];
        
        logMessage('Using sheet: ' + sheetName);
        const sheet = workbook.Sheets[sheetName];
        const jsonData = XLSX.utils.sheet_to_json(sheet);
        logMessage('Loaded ' + jsonData.length + ' rows from Excel');
        
        if (!jsonData || jsonData.length === 0) {
            throw new Error('No data found in Excel file');
        }
        
        // Ensure config fields exist
        if (!appConfig) {
            throw new Error('Configuration not found. Make sure config.js is loaded.');
        }
        
        logMessage('App configuration loaded:', appConfig ? 'yes' : 'no');
        
        // Set animation settings if not already set
        if (!appConfig.animation) {
            appConfig.animation = {
                frameDelay: 1500,
                duration: 800
            };
        }
        
        if (!appConfig.defaultSelectedCountries) {
            logMessage('No default countries found in config, using fallback list', 'warn');
            appConfig.defaultSelectedCountries = [
                'China', 'Japan', 'South Korea', 'Australia & New Zealand', 
                'India', 'Indonesia', 'Singapore', 'Malaysia', 'Thailand', 
                'Vietnam', 'Philippines', 'Hong Kong', 'Taiwan', 'Macau'
            ];
        }
        
        // Set selected countries from config
        selectedCountries = [...appConfig.defaultSelectedCountries];
        logMessage('Selected countries: ' + selectedCountries.join(', '));
        
        // Process data for regions and countries
        logMessage('Processing region data...');
        processedRegionData = processDataByRegion(jsonData);
        logMessage('Processed ' + processedRegionData.length + ' region records');
        
        logMessage('Processing country data...');
        processedCountryData = processDataByCountry(jsonData);
        logMessage('Processed ' + processedCountryData.length + ' country records');
        
        if (processedRegionData.length === 0) {
            throw new Error('No region data processed from Excel file');
        }
        
        // Extract unique regions for chart traces
        uniqueRegions = [...new Set(processedRegionData.map(d => d.Region))];
        logMessage('Unique regions: ' + uniqueRegions.join(', '));
        
        // Extract all years from the data
        years = [...new Set(processedRegionData.map(d => d.Year))].sort();
        logMessage('Years in data: ' + years.join(', '));
        
        currentYearIndex = years.indexOf(appConfig.chart.defaultYear) !== -1 
            ? years.indexOf(appConfig.chart.defaultYear) 
            : 0;
        
        logMessage('Starting at year: ' + years[currentYearIndex]);
        
        // Create timeline
        logMessage('Creating timeline...');
        createTimeline();
        
        // Preload all country logos before creating charts
        preloadCountryLogos(() => {
            // Create initial chart
            logMessage('Creating initial bubble chart...');
            createBubbleChart(processedRegionData, processedCountryData, years[currentYearIndex]);
            
            // Setup race chart
            logMessage('Setting up race chart...');
            if (typeof createRaceChart === 'function') {
                createRaceChart(processedRegionData, years[currentYearIndex]);
            } else {
                logMessage('createRaceChart function not defined', 'warn');
            }
            
            // Add click event listener for play/pause
            logMessage('Adding event listeners...');
            document.getElementById('playButton').addEventListener('click', function() {
                togglePlay();
            });
            
            // 设置为播放状态，显示暂停按钮
            const playIcon = document.getElementById('playIcon');
            const pauseIcon = document.getElementById('pauseIcon');
            if (playIcon) playIcon.style.display = 'none';
            if (pauseIcon) pauseIcon.style.display = 'inline-block';
            
            // 自动开始动画
            logMessage('自动开始动画...');
            togglePlay();
        });
        
    } catch (error) {
        showError(`Error initializing visualization: ${error.message}`);
        console.error('Full error:', error);
    }
}

// 处理窗口大小改变，确保国旗图像正确定位
function handleWindowResize() {
    // 使用防抖动，避免过多更新
    if (resizeTimeout) clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
        logMessage('Window resized, repositioning flag images');
        const chartDiv = document.getElementById('bubble-chart');
        if (chartDiv && chartDiv.data) {
            // 窗口调整大小后，使用0时间立即重新定位图像，避免动画
            updateFlagImagesFromTraces(chartDiv, 0);
        }
    }, 100);
}

// Initialize the application
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    // If DOMContentLoaded has already fired, run init directly
    setTimeout(init, 0);
}

// 添加一个微调国旗位置的控制面板，便于实时调整 (仅在调试模式下显示)
window.adjustFlagPositions = function(xOffset, yOffset) {
    // 更新全局偏移量
    window.flagOffsetX = xOffset !== undefined ? xOffset : (window.flagOffsetX || 0);
    window.flagOffsetY = yOffset !== undefined ? yOffset : (window.flagOffsetY || 0);
    
    logMessage(`Adjusting flag positions: X offset=${window.flagOffsetX}, Y offset=${window.flagOffsetY}`);
    
    // 刷新所有国旗位置
    const chartDiv = document.getElementById('bubble-chart');
    if (chartDiv && chartDiv.data) {
        updateFlagImagesFromTraces(chartDiv);
    }
    
    return `Flags adjusted: X=${window.flagOffsetX}, Y=${window.flagOffsetY}`;
};

// 修改刷新国旗的函数，考虑调整参数
window.refreshFlags = function() {
    const chartDiv = document.getElementById('bubble-chart');
    if (chartDiv && chartDiv.data) {
        logMessage('Manual refresh of flag positions');
        updateFlagImagesFromTraces(chartDiv);
    }
    
    // 添加调试提示
    logMessage('提示: 您可以使用 window.adjustFlagPositions(xOffset, yOffset) 微调国旗位置');
    logMessage('例如: window.adjustFlagPositions(2, -1) 将国旗向右移动2px，向上移动1px');
}; 