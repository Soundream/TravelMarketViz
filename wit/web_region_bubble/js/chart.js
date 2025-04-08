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

// Function to process Excel data by region
function processDataByRegion(jsonData) {
    console.log('Processing region data with', jsonData.length, 'rows'); // Debug log
    const regionData = {};
    
    // Get unique regions first, excluding 'Asia-Pacific'
    uniqueRegions = [...new Set(jsonData.map(row => {
        // Map old region names to new ones
        const region = row['Region'];
        if (region === 'APAC') return 'Asia-Pacific (sum)';
        if (region === 'LATAM') return 'Latin America';
        return region;
    }))].filter(region => region !== 'Asia-Pacific (sum)'); // Filter out Asia-Pacific
    
    console.log('Unique regions:', uniqueRegions);
    
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
    
    console.log('Processed region data:', processedData.length, 'entries'); // Debug log
    return processedData;
}

// Function to process Excel data by country (similar to web_bubble_chart)
function processDataByCountry(jsonData) {
    console.log('Processing country data with', jsonData.length, 'rows'); // Debug log
    
    // Set selected countries from config
    selectedCountries = appConfig.defaultSelectedCountries || [];
    console.log('Selected countries:', selectedCountries);
    
    // Process data for APAC countries
    const apacCountriesData = jsonData
        .filter(row => {
            // Filter for APAC region with market and year data
            if (row['Region'] !== 'APAC' || !row['Market'] || !row['Year']) {
                return false;
            }
            
            // Standardize market name for matching
            let market = row['Market'];
            if (market === 'Australia-New Zealand' || market === 'Australia/New Zealand') {
                market = 'Australia & New Zealand';
            }
            
            // 打印原始数据
            console.error(`Excel原始数据 - ${row['Year']}年 ${market}:`, {
                '国家/地区': market,
                '年份': row['Year'],
                'Excel表格中的在线预订值': row['Online Bookings'],
                'Excel表格中的总预订值': row['Gross Bookings'],
                'Excel表格中的在线渗透率': ((row['Online Bookings'] / row['Gross Bookings']) * 100).toFixed(1) + '%'
            });
            
            // 不再排除特定市场 - 保留所有国家供race chart使用
            return true;
        })
        .map(row => {
            // 标准化市场名称
            let market = row['Market'];
            if (market === 'Australia-New Zealand' || market === 'Australia/New Zealand') {
                market = 'Australia & New Zealand';
            }

            const processedData = {
                Market: market,
                Year: row['Year'],
                OnlinePenetration: row['Online Bookings'] / row['Gross Bookings'],
                OnlineBookings: row['Online Bookings'],
                GrossBookings: row['Gross Bookings']
            };

            // 打印处理后的数据
            console.error(`Race Chart处理后数据 - ${row['Year']}年 ${market}:`, {
                '国家/地区': market,
                '年份': row['Year'],
                'Race Chart使用的在线预订值': processedData.OnlineBookings,
                'Race Chart使用的总预订值': processedData.GrossBookings,
                'Race Chart使用的在线渗透率': (processedData.OnlinePenetration * 100).toFixed(1) + '%'
            });

            return processedData;
        });
            
    // Store APAC countries data globally so race-chart.js can access it
    window.processedCountriesData = apacCountriesData;
    logMessage('Stored ' + apacCountriesData.length + ' country entries for race chart');
    
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
    
    // 需要在气泡图中过滤掉的国家
    const excludedCountries = ['Taiwan', 'Hong Kong', 'Macau'];
    
    // 最小在线预订值阈值(十亿)
    const minOnlineBookingsThreshold = 0.1;
    
    // Filter country data - 不再排除任何国家，但添加阈值过滤
    const yearCountryData = countryData.filter(d => {
        const matchesYear = d.Year === year;
        const isSelected = selectedCountries.includes(d.Country);
        // 额外过滤掉特定国家，但仅在气泡图显示中
        const isExcluded = excludedCountries.includes(d.Country);
        // 过滤掉在线预订值小于阈值的国家
        const hasEnoughOnlineBookings = d['Online Bookings'] >= minOnlineBookingsThreshold;
        
        return matchesYear && isSelected && !isExcluded && hasEnoughOnlineBookings;
    });
    logMessage('Year country data count: ' + yearCountryData.length);
    
    // Calculate max Gross Bookings for sizing
    const allData = [...regionData, ...countryData];
    const maxGrossBookings = d3.max(allData, d => {
        return d['Gross Bookings'] || 0;
    });

    // 定义y轴范围
    const yAxisRange = [Math.log10(0.1), Math.log10(800)];
    
    // 创建背景文字
    backgroundTrace = {
        x: [50],  // 水平居中
        y: [Math.pow(10, (yAxisRange[0] + yAxisRange[1]) / 2)],  // 在对数坐标系中垂直居中
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
        // Get the correct color for the region
        const colorKey = region === 'Asia-Pacific (sum)' ? 'Asia-Pacific' : region;
        
        return {
            name: region,
            x: regionData.map(d => d['Online Penetration'] * 100), // 转换为百分比
            y: regionData.map(d => d['Online Bookings'] * appConfig.dataProcessing.bookingsScaleFactor), // 应用缩放因子
            mode: 'markers',
            hoverinfo: 'text',
            hovertext: regionData.map(d => `
                <b style="font-family: Monda">${d.Region}</b><br>
                <span style="font-family: Monda">Share of Online Bookings: ${(d['Online Penetration'] * 100).toFixed(1)}%<br>
                Online Bookings: $${(d['Online Bookings']).toFixed(1)}B<br>
                Gross Bookings: $${(d['Gross Bookings']).toFixed(1)}B</span>
            `),
            marker: {
                size: regionData.map(d => {
                    const size = Math.sqrt(d['Gross Bookings']) * 3;
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
    
    // 创建国家轨迹数组和标志轨迹数组
    const countryTraces = [];
    const flagTraces = [];
    
    // 为每个国家同时创建气泡和旗帜
    yearCountryData.forEach(d => {
        // 计算实际位置
        const xPos = d['Online Penetration'] * 100; // 转换为百分比
        const yPos = d['Online Bookings'] * appConfig.dataProcessing.bookingsScaleFactor;
        
        // 计算图标大小基于总预订值
        const grossBookings = d['Gross Bookings'];
        const maxRegionGrossBookings = d3.max(yearRegionData, d => d['Gross Bookings']);
        const minSize = 15;
        const maxSize = 30;
        
        const sizeRatio = Math.sqrt(grossBookings / maxRegionGrossBookings);
        const finalSize = minSize + (maxSize - minSize) * sizeRatio;
        
        // 创建隐形国家气泡轨迹 - 用于存储位置和大小信息，但设为完全透明
        const countryTrace = {
            name: d.Country,
            x: [xPos],
            y: [yPos],
            mode: 'markers',
            text: [d.Country],
            hoverinfo: 'text',
            hovertext: `
                <b style="font-family: Monda">${d.Country}</b><br>
                <span style="font-family: Monda">Share of Online Bookings: ${(d['Online Penetration'] * 100).toFixed(1)}%<br>
                Online Bookings: $${(d['Online Bookings']).toFixed(1)}B<br>
                Gross Bookings: $${(d['Gross Bookings']).toFixed(1)}B</span>
            `,
            marker: {
                size: finalSize,
                color: 'rgba(255,255,255,0)',  // 完全透明
                line: {
                    color: 'rgba(200,200,200,0)',  // 完全透明边框
                    width: 0
                }
            },
            showlegend: false,
            _flagSize: finalSize  // 添加自定义属性存储大小，以便在标志轨迹中使用相同的值
        };
        
        // 添加到国家轨迹数组
        countryTraces.push(countryTrace);
        
        // 检查是否有国旗图标可用
        const logoUrl = appConfig.countryLogos[d.Country];
        if (logoUrl) {
            // 创建标志轨迹
            const finalLogoUrl = './' + logoUrl.replace(/^[./]+/, '');
            
            const flagTrace = {
                name: d.Country + ' flag',
                x: [xPos],
                y: [yPos],
                mode: 'markers',
                type: 'scatter',
                hoverinfo: 'skip',
                showlegend: false,
                marker: {
                    size: 1,
                    opacity: 0 // 完全透明的标记
                },
                customdata: [{
                    logoUrl: finalLogoUrl,
                    country: d.Country
                }]
            };
            
            // 添加到标志轨迹数组
            flagTraces.push(flagTrace);
        }
    });
    
    // 合并所有轨迹
    const allTraces = [backgroundTrace, ...regionTraces, ...countryTraces, ...flagTraces];
    
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
            fixedrange: true  // 防止用户意外缩放
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
            ticktext: ['0.1', '0.5', '1', '2', '5', '10', '20', '50', '100', '200', '500', '800'],
            tickvals: [0.1, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 800],
            range: [Math.log10(0.1), Math.log10(800)],
            autorange: false,
            showticklabels: true,
            ticks: 'outside',
            ticklen: 8,
            tickwidth: 1,
            tickcolor: '#ccc',
            fixedrange: true  // 防止用户意外缩放
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
    
    // 获取当前和下一年的气泡数据
    const currentBubbles = plotElement.data.filter(trace => 
        trace.name && 
        selectedCountries.includes(trace.name) &&
        !trace.customdata);
        
    // 获取图表区域信息
    const plotArea = chartDiv.querySelector('.subplot.xy');
    if (!plotArea) return;
    
    const plotRect = plotArea.getBoundingClientRect();
    const chartRect = chartDiv.getBoundingClientRect();
    
    // 计算相对于图表容器的偏移量
    const plotOffsetX = plotRect.left - chartRect.left;
    const plotOffsetY = plotRect.top - chartRect.top;
    
    // 获取水平和垂直偏移量
    const horizontalOffset = window.flagOffsetX || 47;
    const verticalOffset = window.flagOffsetY || 10;
    
    // 更新每个国家的旗帜位置
    currentBubbles.forEach(bubble => {
        const country = bubble.name;
        if (!country || !selectedCountries.includes(country)) return;
        
        // 获取当前位置
        const xData = bubble.x[0];
        const yData = bubble.y[0];
        
        // 转换为像素坐标
        const xPx = plotElement._fullLayout.xaxis.d2p(xData);
        const yPx = plotElement._fullLayout.yaxis.d2p(yData);
        
        // 计算最终位置（相对于图表容器）
        const finalX = plotOffsetX + xPx + horizontalOffset;
        const finalY = plotOffsetY + yPx + verticalOffset;
        
        // 获取气泡大小
        const bubbleSize = bubble._flagSize || 
                          (Array.isArray(bubble.marker.size) ? bubble.marker.size[0] : bubble.marker.size);
        
        // 更新或创建旗帜
        const logoUrl = appConfig.countryLogos[country];
        if (logoUrl) {
            createFlagImage(
                country,
                './' + logoUrl.replace(/^[./]+/, ''),
                finalX,
                finalY,
                bubbleSize,
                duration || appConfig.animation.duration
            );
        }
    });
}

// 更新createFlagImage函数以支持更平滑的动画
function createFlagImage(country, logoUrl, x, y, size, duration) {
    const chartContainer = document.getElementById('bubble-chart');
    if (!chartContainer) return;
    
    const img = flagImages[country] || document.createElement('img');
    
    if (!flagImages[country]) {
        img.src = logoUrl;
        img.alt = country;
        img.className = 'country-flag';
        img.style.position = 'absolute';
        img.style.transition = `all ${duration}ms linear`;
        img.style.opacity = '0';
        chartContainer.appendChild(img);
        flagImages[country] = img;
        
        // 错误处理
        img.onerror = () => {
            logMessage(`Error loading flag image for ${country}: ${logoUrl}`, 'error');
            img.style.backgroundColor = 'rgba(200, 200, 200, 0.8)';
            img.style.border = '1px solid white';
        };
        
        // 触发重排以启动动画
        setTimeout(() => {
            img.style.opacity = '1';
        }, 10);
    }
    
    // 使用绝对定位而不是transform
    img.style.left = `${Math.round(x - size/2)}px`;
    img.style.top = `${Math.round(y - size/2)}px`;
    img.style.width = `${Math.round(size)}px`;
    img.style.height = `${Math.round(size)}px`;
    img.style.transitionDuration = `${duration}ms`;
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