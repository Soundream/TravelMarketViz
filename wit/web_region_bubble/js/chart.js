// Global variables
let isPlaying = true; // 默认为播放状态
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
            .ease(d3.easeLinear)  // 使用线性缓动
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
    
    // Filter country data - exclude Macau, Taiwan, and Hong Kong
    const excludedCountries = ['Macau', 'Taiwan', 'Hong Kong'];
    const yearCountryData = countryData.filter(d => {
        const matchesYear = d.Year === year;
        const isSelected = selectedCountries.includes(d.Country);
        const isNotExcluded = !excludedCountries.includes(d.Country);
        return matchesYear && isSelected && isNotExcluded;
    });
    logMessage('Year country data count: ' + yearCountryData.length);
    
    // Calculate max Gross Bookings for sizing
    const allData = [...regionData, ...countryData];
    const maxGrossBookings = d3.max(allData, d => {
        return d['Gross Bookings'] || 0;
    });
    
    // 创建背景文字
    backgroundTrace = {
        x: [50],
        y: [50],  // 调整垂直位置使文字更好地居中
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

    // Create country traces with visible markers
    const countryTraces = yearCountryData.map(d => {
        // For countries, we will use a simple marker trace but will add images separately
        return {
          type: 'scatter',
          name: d.Country,
          x: [d['Online Penetration'] * appConfig.dataProcessing.onlinePenetrationMultiplier],
          y: [d['Online Bookings'] * appConfig.dataProcessing.bookingsScaleFactor],
          mode: 'markers+text',
          text: [d.Country],
          textposition: 'bottom center',
          textfont: { family: 'Monda', size: 12, color: '#333' },
          hoverinfo: 'text',
          hovertext: `
                <b style="font-family: Monda">${d.Country}</b><br>
                <span style="font-family: Monda">Share of Online Bookings: ${(d['Online Penetration'] * 100).toFixed(1)}%<br>
                Online Bookings: $${(d['Online Bookings'] * appConfig.dataProcessing.bookingsScaleFactor).toFixed(1)}B<br>
                Gross Bookings: $${(d['Gross Bookings'] * appConfig.dataProcessing.bookingsScaleFactor).toFixed(1)}B</span>
            `,
          marker: {
            size: 3, // Tiny marker just as a fallback
            color: 'rgba(0,0,0,0)', // Transparent
            opacity: 0.3,
          },
          showlegend: false
        };
    });
    
    // Create the country logo images to add to layout
    const countryImages = yearCountryData.map(d => {
        const logoUrl = appConfig.countryLogos[d.Country];
        if (!logoUrl) {
            logMessage(`No logo URL for country: ${d.Country}`, 'warn');
            return null;
        }
        
        // Use the path that works from the debug panel
        let finalLogoUrl = './' + logoUrl.replace(/^[./]+/, '');
        
        // Make the images MUCH larger and ensure they align with bubbles
        const bubbleSize = Math.sqrt(d['Gross Bookings'] / maxGrossBookings);
        // Make images 3-5x larger than before
        const finalSize = Math.max(0.2, bubbleSize * 1.5); 
        
        return {
            source: finalLogoUrl,
            xref: "x",
            yref: "y",
            x: d['Online Penetration'] * appConfig.dataProcessing.onlinePenetrationMultiplier,
            y: d['Online Bookings'] * appConfig.dataProcessing.bookingsScaleFactor,
            sizex: finalSize,
            sizey: finalSize,
            sizing: "contain",
            opacity: 1,
            layer: "above",
            xanchor: "center", 
            yanchor: "middle"
        };
    }).filter(Boolean);
    
    // 合并所有轨迹
    const allTraces = [backgroundTrace, ...regionTraces, ...countryTraces];

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
            duration: 800,
            easing: 'linear'
        },
        // Add country logo images to layout
        images: countryImages
    };

    // 初始化全局 config 变量
    config = {
        responsive: true,
        displayModeBar: false
    };

    logMessage(`Plotting chart with ${allTraces.length} traces and ${countryImages.length} country images`);
    
    // If it's the first rendering, use newPlot. Otherwise, use react for smooth transitions
    if (document.getElementById('bubble-chart').data) {
        // Use animate for smoother transitions between frames
        Plotly.animate('bubble-chart', 
            {
                data: allTraces,
                layout: layout
            }, 
            {
                transition: {
                    duration: appConfig.animation.duration,
                    easing: 'linear'
                },
                frame: {
                    duration: appConfig.animation.duration,
                    redraw: false
                }
            }
        ).then(function() {
            logMessage('Chart updated successfully');
        }).catch(error => {
            logMessage('Error updating chart: ' + error, 'error');
        });
    } else {
        // First time rendering
        Plotly.newPlot('bubble-chart', allTraces, layout, config).then(function() {
            logMessage('Chart created successfully');
        }).catch(error => {
            logMessage('Error creating chart: ' + error, 'error');
        });
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

// Toggle Play/Pause Function
function togglePlay() {
    logMessage('Toggle play/pause. Current state: ' + isPlaying);
    isPlaying = !isPlaying;
    
    const playIcon = document.getElementById('playIcon');
    const pauseIcon = document.getElementById('pauseIcon');
    
    if (isPlaying) {
        logMessage('Starting animation');
        // Show pause icon
        if (playIcon) playIcon.style.display = 'none';
        if (pauseIcon) pauseIcon.style.display = 'inline-block';
        
        // Start animation
        let lastTime = performance.now();
        let accumulatedTime = 0;
        const frameInterval = appConfig.animation.frameDelay;
        
        const animate = (currentTime) => {
            if (!isPlaying) return;
            
            const deltaTime = currentTime - lastTime;
            accumulatedTime += deltaTime;
            
            if (accumulatedTime >= frameInterval) {
                currentYearIndex = (currentYearIndex + 1) % years.length;
                const year = years[currentYearIndex];
                logMessage('Animating to year: ' + year);
                createBubbleChart(processedRegionData, processedCountryData, year);
                accumulatedTime = 0;
            }
            
            lastTime = currentTime;
            requestAnimationFrame(animate);
        };
        
        requestAnimationFrame(animate);
    } else {
        logMessage('Stopping animation');
        // Show play icon
        if (playIcon) playIcon.style.display = 'inline-block';
        if (pauseIcon) pauseIcon.style.display = 'none';
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
                'Vietnam', 'Philippines'
            ];
        } else {
            // Filter out Macau, Taiwan, and Hong Kong from defaultSelectedCountries
            const excludedCountries = ['Macau', 'Taiwan', 'Hong Kong'];
            appConfig.defaultSelectedCountries = appConfig.defaultSelectedCountries.filter(
                country => !excludedCountries.includes(country)
            );
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
        
        // Process APAC countries data for the race chart - exclude Macau, Taiwan, and Hong Kong
        logMessage('Processing data for race chart...');
        const excludedCountries = ['Macau', 'Taiwan', 'Hong Kong'];
        
        const apacCountriesData = jsonData
            .filter(row => {
                // Filter for APAC region with market and year data, excluding specific countries
                if (row['Region'] !== 'APAC' || !row['Market'] || !row['Year']) return false;
                
                // Standardize market name for matching
                let market = row['Market'];
                if (market === 'Australia-New Zealand' || market === 'Australia/New Zealand') {
                    market = 'Australia & New Zealand';
                }
                
                // Exclude specific markets
                return !excludedCountries.includes(market);
            })
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
        logMessage('Stored ' + apacCountriesData.length + ' country entries for race chart');
        
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
            
            // Start animation after a short delay
            logMessage('Starting animation with delay...');
            setTimeout(() => {
                isPlaying = false; // Reset state
                togglePlay(); // Start playing
                logMessage('Animation started');
            }, 1000);
        });
        
    } catch (error) {
        showError(`Error initializing visualization: ${error.message}`);
        console.error('Full error:', error);
    }
}

// Initialize the application
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    // If DOMContentLoaded has already fired, run init directly
    setTimeout(init, 0);
} 