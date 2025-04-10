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

    // Apply scaling factor to increase overall size
    const scalingFactor = 3; // Increase size by 20%
    const enhancedSize = size * scalingFactor;

    // Debug 日志 - 使用 window.debug 标志来控制是否输出调试信息
    if (window.debug) {
        console.debug('Bubble size calculation:', {
            grossBookings,
            maxGrossBookings,
            ratio,
            clamped,
            finalSize: enhancedSize
        });
    }

    return enhancedSize;
}

// Function to process Excel data by region
function processDataByRegion(jsonData) {
    console.log('Processing region data with', jsonData.length, 'rows'); // Debug log
    const regionData = {};
    
    // Get unique regions first, including 'Asia-Pacific'
    uniqueRegions = [...new Set(jsonData.map(row => {
        // Map old region names to new ones
        const region = row['Region'];
        if (region === 'APAC') return 'Asia-Pacific';
        if (region === 'LATAM') return 'Latin America';
        return region;
    }))]; // Include Asia-Pacific
    
    console.log('Unique regions:', uniqueRegions);
    
    jsonData.forEach(row => {
        const year = row['Year'];
        let region = row['Region'];
        // Map old region names to new ones
        if (region === 'APAC') region = 'Asia-Pacific';
        if (region === 'LATAM') region = 'Latin America';
        
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

// Function to process Excel data by country
function processDataByCountry(jsonData) {
    console.log('Processing country data with', jsonData.length, 'rows'); // Debug log
    
    // Use the defaultSelectedCountries from appConfig
    selectedCountries = appConfig.defaultSelectedCountries;
    console.log('Selected countries:', selectedCountries);
    
    // Process data for selected countries
    const processedData = jsonData
        .filter(row => selectedCountries.includes(row['Market']) && row['Year'])
        .map(row => {
            // Standardize market names
            let market = row['Market'];
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
function createBubbleChart(regionData, countryData, year, progress = 0) {
    logMessage('Creating chart for year: ' + year);
    
    // Filter data for the current year
    const yearRegionData = regionData;  // 已经是插值后的数据
    const yearCountryData = countryData; // 已经是插值后的数据
    
    // 需要在气泡图中过滤掉的国家 - 但不在总和计算中排除
    const excludedCountries = ['Taiwan', 'Hong Kong', 'Macau'];
    
    // 最小在线预订值阈值(十亿)
    const minOnlineBookingsThreshold = 1.0;
    
    // Filter country data - 仅在气泡图显示中排除特定国家
    const filteredCountryData = yearCountryData.filter(d => {
        const matchesYear = d.Year === year;
        const isSelected = selectedCountries.includes(d.Country);
        const isExcluded = excludedCountries.includes(d.Country);
        const hasEnoughOnlineBookings = d['Online Bookings'] >= minOnlineBookingsThreshold;
        
        return matchesYear && isSelected && !isExcluded && hasEnoughOnlineBookings;
    });
    logMessage('Year country data count: ' + filteredCountryData.length);
    
    // 计算全局最大 Gross Bookings（排除无效值）
    const allData = [...regionData, ...countryData].filter(d => 
        d['Gross Bookings'] && !isNaN(d['Gross Bookings']) && d['Gross Bookings'] > 0
    );
    const maxGrossBookings = d3.max(allData, d => d['Gross Bookings']);
    console.log('Global max Gross Bookings:', maxGrossBookings);

    // 定义y轴范围
    const yAxisRange = [Math.log10(1), Math.log10(800)];
    
    // 创建背景文字
    backgroundTrace = {
        y: [50],  // Vertically centered
        x: [Math.pow(10, (Math.log10(0.5) + Math.log10(500)) / 2)],  // 使用对数中点确保水平居中
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
        // Exclude regions without PNG images
        if (!appConfig.countryLogos[region]) return null;
        if (region === 'Middle East' || region === 'Asia-Pacific') return null; // Exclude Middle East and Asia-Pacific
        const regionData = yearRegionData.filter(d => d.Region === region);
        const colorKey = appConfig.regionColors[region] || region;

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
                color: colorKey,
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
    }).filter(region => region !== null);
    
    // // Add APAC region with red color
    // const apacRegionData = yearRegionData.filter(d => d.Region === 'Asia-Pacific');
    // regionTraces.push({
    //     name: 'Asia-Pacific',
    //     y: apacRegionData.map(d => d['Online Penetration'] * 100),
    //     x: apacRegionData.map(d => d['Online Bookings'] * appConfig.dataProcessing.bookingsScaleFactor),
    //     mode: 'markers',
    //     hoverinfo: 'text',
    //     hovertext: apacRegionData.map(d => `
    //         <b style="font-family: Monda">${d.Region}</b><br>
    //         <span style="font-family: Monda">Share of Online Bookings: ${(d['Online Penetration'] * 100).toFixed(1)}%<br>
    //         Online Bookings: $${(d['Online Bookings']).toFixed(1)}B<br>
    //         Gross Bookings: $${(d['Gross Bookings']).toFixed(1)}B<br>
    //         Bubble Size: ${computeBubbleSize(d['Gross Bookings'], maxGrossBookings, 
    //             appConfig.chart.minBubbleSize, appConfig.chart.maxBubbleSize).toFixed(1)}</span>
    //     `),
    //     marker: {
    //         size: apacRegionData.map(d => computeBubbleSize(
    //             d['Gross Bookings'],
    //             maxGrossBookings,
    //             appConfig.chart.minBubbleSize || 10,
    //             appConfig.chart.maxBubbleSize || 120
    //         )),
    //         color: '#FF4B4B', // Set APAC bubble color to '#FF4B4B'
    //         opacity: 0.75,
    //         line: {
    //             color: 'rgba(255, 255, 255, 0.8)',
    //             width: 1.5
    //         }
    //     },
    //     showlegend: true,
    //     legendgroup: 'Asia-Pacific',
    //     type: 'scatter'
    // });
    
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
    const allCountriesGrossBookings = filteredCountryData.map(d => ({
        country: d.Country,
        grossBookings: d['Gross Bookings']
    }));
    allCountriesGrossBookings.sort((a, b) => b.grossBookings - a.grossBookings);

    // 填充组合轨迹的数据
    filteredCountryData.forEach(d => {
        const yPos = d['Online Penetration'] * 100;
        
        // 确保在对数刻度下正确处理x轴位置
        const xPos = Math.max(d['Online Bookings'] * appConfig.dataProcessing.bookingsScaleFactor, 0.5);
        const xPosFinal = Math.log10(xPos);  // 直接使用对数值，因为我们的轴已经是对数刻度
        
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

        combinedCountryTrace.x.push(xPosFinal);
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

    // 合并所有轨迹
    const allTraces = [backgroundTrace, ...regionTraces, combinedCountryTrace];
    
    // 创建国旗图片配置
    const flagImages = filteredCountryData.map(d => {
        // 如果 Online Bookings 小于 0.5，不显示国旗
        const onlineBookings = d['Online Bookings'] * appConfig.dataProcessing.bookingsScaleFactor;
        if (onlineBookings < 0.5) {
            return null;
        }

        // 直接使用对数值作为x坐标
        const xPosFinal = Math.log10(Math.max(onlineBookings, 0.5));
        const yPos = d['Online Penetration'] * 100;
        
        // 计算相对尺寸
        const relativeSize = Math.pow(d['Gross Bookings'] / maxGrossBookings, 0.6);
        const targetSize = (relativeSize * 0.1 + 0.01) * 0.5;
        
        const logoUrl = appConfig.countryLogos[d.Country];
        if (!logoUrl) {
            logMessage(`No logo URL found for country: ${d.Country}`, 'warn');
            return null;
        }

        // 确保路径正确
        const imagePath = './' + logoUrl.replace(/^[./]+/, '');

        // Apply scaling factor to image size
        const scalingFactor = 3;
        const scaledSizeX = targetSize * 200 * scalingFactor;
        const scaledSizeY = targetSize * 200 * scalingFactor;

        return {
            source: imagePath,
            x: xPosFinal,
            y: yPos,
            xref: 'x',
            yref: 'y',
            sizex: scaledSizeX,
            sizey: scaledSizeY,
            xanchor: 'center',
            yanchor: 'middle',
            sizing: 'contain',
            opacity: 1,
            layer: 'above',
            visible: true,
            name: d.Country  // 添加国家名称用于标识
        };
    }).filter(img => img !== null);
    
    // 初始化全局 layout 变量
    layout = {
        title: {
            text: '',
            font: {
                family: 'Monda',
                size: 24
            },
            y: 0.95
        },
        images: flagImages,
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
            ticktext: ['0.5', '1', '5', '10', '50', '100', '500'],
            tickvals: [0.5, 1, 5, 10, 50, 100, 500],
            range: [Math.log10(0.5), Math.log10(500)],  // 修改范围
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
                standoff: 5
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
            l: 120,  // 增加左边距
            r: 80,
            t: 80,
            b: 100,
            pad: 10  // 添加内边距
        },
        width: 1200,  // 增加图表宽度到1200px
        height: 650,  // 保持图表高度不变
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

    logMessage(`Plotting chart with ${allTraces.length} traces and ${flagImages.length} flag images`);
    
    // 如果是第一次渲染，使用 newPlot，否则使用分步动画实现平滑过渡
    const chartDiv = document.getElementById('bubble-chart');
    
    if (!chartDiv.data) {
        // 初次渲染使用 newPlot
        Plotly.newPlot('bubble-chart', allTraces, layout, config).then(function() {
            logMessage('Chart created successfully');
        }).catch(error => {
            logMessage('Error creating chart: ' + error, 'error');
        });
    } else {
        // 使用 animate 更新，确保图片和数据同步更新
        const animationConfig = {
            transition: { 
                duration: 0,
                easing: 'linear' 
            },
            frame: { 
                duration: 0,
                redraw: true
            },
            mode: 'immediate'
        };
        
        try {
            // 确保layout中的images数组与现有的保持一致的顺序
            const currentLayout = chartDiv.layout || {};
            const currentImages = currentLayout.images || [];
            
            // 更新现有图片的位置和大小，保持顺序不变
            const updatedImages = currentImages.map(currentImg => {
                const matchingNewImg = flagImages.find(newImg => newImg.name === currentImg.name);
                if (matchingNewImg) {
                    return {
                        ...currentImg,
                        x: matchingNewImg.x,
                        y: matchingNewImg.y,
                        sizex: matchingNewImg.sizex,
                        sizey: matchingNewImg.sizey
                    };
                }
                return currentImg;
            });

            // 添加新的图片
            flagImages.forEach(newImg => {
                if (!currentImages.find(img => img.name === newImg.name)) {
                    updatedImages.push(newImg);
                }
            });

            const updatedLayout = {
                ...layout,
                images: updatedImages
            };

            Plotly.animate('bubble-chart', {
                data: allTraces,
                layout: updatedLayout
            }, animationConfig).then(() => {
                logMessage('Chart and flag images updated with linear transition');
            }).catch(error => {
                logMessage('Error updating chart: ' + error, 'error');
            });
        } catch (error) {
            logMessage('Animation error, falling back to update: ' + error, 'warn');
            Plotly.update('bubble-chart', 
                {data: allTraces},
                layout
            );
        }
    }

    // 更新时间轴
    const timelinePosition = year + (year - year) * progress;
    if (timeline && timeline.triangle) {
        timeline.triangle
            .attr('transform', `translate(${timeline.scale(timelinePosition)}, -10) rotate(180)`);
    }
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
            totalDuration: 38000, // 38秒 = 38000毫秒
            frameDuration: 16, // 约60fps
            lastFrameTime: Date.now()
        };
        
        // 使用requestAnimationFrame实现平滑动画
        const renderFrame = () => {
            if (!isPlaying) return;
            
            const now = Date.now();
            const elapsedSinceStart = now - animationController.startTime;
            const cyclePosition = (elapsedSinceStart % animationController.totalDuration) / animationController.totalDuration;
            const yearPosition = cyclePosition * years.length;
            const currentYearIndex = Math.floor(yearPosition);
            const progress = yearPosition - currentYearIndex; // 插值进度 (0-1)
            
            // 获取当前年份和下一年份的数据
            const currentYear = years[currentYearIndex];
            const nextYearIndex = (currentYearIndex + 1) % years.length;
            const nextYear = years[nextYearIndex];
            
            // 获取当前和下一年的数据
            const currentRegionData = processedRegionData.filter(d => d.Year === currentYear);
            const nextRegionData = processedRegionData.filter(d => d.Year === nextYear);
            const currentCountryData = processedCountryData.filter(d => d.Year === currentYear);
            const nextCountryData = processedCountryData.filter(d => d.Year === nextYear);
            
            // 创建插值数据
            const interpolatedRegionData = currentRegionData.map(d => {
                const nextData = nextRegionData.find(nd => nd.Region === d.Region) || d;
                return {
                    Year: currentYear,
                    Region: d.Region,
                    'Gross Bookings': d['Gross Bookings'] + (nextData['Gross Bookings'] - d['Gross Bookings']) * progress,
                    'Online Bookings': d['Online Bookings'] + (nextData['Online Bookings'] - d['Online Bookings']) * progress,
                    'Online Penetration': d['Online Penetration'] + (nextData['Online Penetration'] - d['Online Penetration']) * progress
                };
            });
            
            const interpolatedCountryData = currentCountryData.map(d => {
                const nextData = nextCountryData.find(nd => nd.Country === d.Country) || d;
                // 在对数空间中进行插值
                const currentLogBookings = Math.log10(d['Online Bookings'] || 0.5);
                const nextLogBookings = Math.log10(nextData['Online Bookings'] || 0.5);
                const interpolatedLogBookings = currentLogBookings + (nextLogBookings - currentLogBookings) * progress;
                const interpolatedBookings = Math.pow(10, interpolatedLogBookings);

                return {
                    Year: currentYear,
                    Country: d.Country,
                    'Gross Bookings': d['Gross Bookings'] + (nextData['Gross Bookings'] - d['Gross Bookings']) * progress,
                    'Online Bookings': interpolatedBookings,
                    'Online Penetration': d['Online Penetration'] + (nextData['Online Penetration'] - d['Online Penetration']) * progress
                };
            });
            
            // 更新图表，使用插值数据
            createBubbleChart(interpolatedRegionData, interpolatedCountryData, currentYear, progress);
            
            // 更新时间轴位置（使用插值）
            const timelinePosition = currentYear + (nextYear - currentYear) * progress;
            if (timeline && timeline.triangle) {
                timeline.triangle
                    .attr('transform', `translate(${timeline.scale(timelinePosition)}, -10) rotate(180)`);
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

// 修改 handleWindowResize 函数，因为不再需要手动更新国旗位置
function handleWindowResize() {
    if (resizeTimeout) clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
        logMessage('Window resized, updating chart');
        const chartDiv = document.getElementById('bubble-chart');
        if (chartDiv && chartDiv.data) {
            Plotly.relayout(chartDiv, {
                width: chartDiv.offsetWidth,
                height: chartDiv.offsetHeight
            });
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