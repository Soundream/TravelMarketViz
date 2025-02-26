// Your Google Sheets ID
const sheetId = '2PACX-1vQYwQTSYwig7AZ0fjPniLVfUUJnLz3PP4f4fBtqkBNPYqrkKtQyZDaB99kHk2eCzuCh5i8oxTPCHeQ9';

// Sheet names for each table (Revenue Growth, EBITDA Margin, Revenue)
const sheetNames = {
    revenueGrowth: 'Revenue Growth YoY',
    ebitdaMargin: 'EBITDA_MARGIN',
    revenue: 'Revenue'
};

// Company logos mapping
const companyLogos = {
    "ABNB": "logos/ABNB_logo.png",
    "BKNG": "logos/BKNG_logo.png",
    "EXPE": "logos/EXPE_logo.png",
    "TCOM": "logos/TCOM_logo.png",
    "TRIP": "logos/TRIP_logo.png",
    "TRVG": "logos/TRVG_logo.png",
    "EDR": "logos/EDR_logo.png",
    "DESP": "logos/DESP_logo.png",
    "MMYT": "logos/MMYT_logo.png",
    "Ixigo": "logos/IXIGO_logo.png",
    "SEERA": "logos/SEERA_logo.png",
    "Webjet": "logos/WEB_logo.png",
    "LMN": "logos/LMN_logo.png",
    "Yatra": "logos/YTRA_logo.png",
    "Orbitz": "logos/OWW_logo.png",
    "Travelocity": "logos/Travelocity_logo.png",
    "EaseMyTrip": "logos/EASEMYTRIP_logo.png",
    "Wego":  "logos/Wego_logo.png",
    "Skyscanner":  "logos/Skyscanner_logo.png",
    "Etraveli":  "logos/Etraveli_logo.png",
    "Kiwi":  "logos/Kiwi_logo.png",
    "Cleartrip": "logos/Cleartrip_logo.png",
    "Traveloka": "logos/Traveloka_logo.png",
    "FLT": "logos/FlightCentre_logo.png",
    "Almosafer": "logos/Almosafer_logo.png",
    "Webjet OTA": "logos/OTA_logo.png",

    // Add other company logos here...
};

// Raw color dictionary with potential leading/trailing spaces
const color_dict_raw = {
    'ABNB': '#ff5895',
    'Almosafer': '#bb5387',
    'BKNG': '#003480',
    'DESP': '#755bd8',
    'EXPE': '#fbcc33',
    'EaseMyTrip': '#00a0e2',
    'Ixigo': '#e74c3c',
    'MMYT': '#e74c3c',
    'TRIP': '#00af87',
    'TRVG': '#e74c3c',
    'Wego': '#4e843d',
    'Yatra': '#e74c3c',
    'TCOM': '#2577e3',
    'EDR': '#2577e3',
    'LMN': '#fc03b1',
    'Webjet': '#e74c3c',
    'SEERA': '#750808',
    'PCLN': '#003480',
    'Orbitz': '#8edbfa',
    'Travelocity': '#1d3e5c',
    'Skyscanner': '#0770e3',
    'Etraveli': '#b2e9ff',
    'Kiwi': '#e5fdd4',
    'Cleartrip': '#e74c3c',
    'Traveloka': '#38a0e2',
    'FLT': '#d2b6a8',
    'Almosafer': '#ba0d86',
    'Webjet OTA': '#e74c3c',
    
};

// Mapping of company symbols to full names
const companyNames = {
    "ABNB": "Airbnb",
    "BKNG": "Booking.com",
    "EXPE": "Expedia",
    "TCOM": "Trip.com",
    "TRIP": "TripAdvisor",
    "TRVG": "Trivago",
    "EDR": "Edreams",
    "DESP": "Despegar",
    "MMYT": "MakeMyTrip",
    "Ixigo": "Ixigo",
    "SEERA": "Seera Group",
    "Webjet": "Webjet",
    "LMN": "Lastminute",
    "Yatra": "Yatra.com",
    "Orbitz": "Orbitz",
    "Travelocity": "Travelocity",
    "EaseMyTrip": "EaseMyTrip",
    "Wego": "Wego",
    "Skyscanner": "Skyscanner",
    "Etraveli": "Etraveli",
    "Kiwi": "Kiwi",
    "Cleartrip": "Cleartrip",
    "FLT": "Flight Centre",
    "Almosafer": "Almosafer",

};

// Array of company symbols to be selected by default (after companyNames is defined)
const defaultSelectedCompanies = [
    "ABNB",     // Airbnb
    "BKNG",     // Booking.com
    "DESP",     // Despegar
    "EaseMyTrip", // EaseMyTrip
    "EDR",      // Edreams
    "LMN",      // Lastminute
    "SEERA",    // Seera Group
    "TCOM",     // Trip.com
    "TRIP",     // TripAdvisor
    "TRVG",     // Trivago
    "Webjet",   // Webjet
    "Yatra"     // Yatra.com
];

// Global variables
let maxRevenueValue = 10000; // Initialize with a default value
let isPlaying = false;
let playInterval;
let currentQuarterIndex = 0;
let uniqueQuarters;
let mergedData;
let timelineTriangle;
let xScaleTimeline;
let timelineHeight = 80;
let selectedCompanies = []; // Initialize with no companies selected

// Add a variable to store race bar chart data globally
let raceBarChartData = null;

// Global variables for interpolation
let currentInterpolationFrame = 0;
let interpolationFrames = [];
let isInterpolating = false;

// Add easing function at the top of the file after the color_dict definition
function easeInOutCubic(t) {
    return t < 0.5
        ? 4 * t * t * t
        : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

// Function to clean the color dictionary by trimming keys
function cleanColorDict(rawDict) {
    const cleanedDict = {};
    for (const [key, value] of Object.entries(rawDict)) {
        const cleanKey = key.trim();
        cleanedDict[cleanKey] = value;
    }
    return cleanedDict;
}

// Cleaned color dictionary without leading/trailing spaces
const color_dict = cleanColorDict(color_dict_raw);

// Function to get companies with data for a specific quarter
function getCompaniesWithData(quarter, data) {
    return data
        .filter(d => d.quarter === quarter && d.revenue != null && d.revenue > 0)
        .map(d => d.company);
}

// Function to parse CSV data into a usable array of objects
function processData(csvText) {
    console.log('Starting to process CSV data');
    const rows = csvText.split('\n').map(row => 
        row.split(',').map(cell => {
            // Remove quotes and trim whitespace
            const cleaned = cell.trim().replace(/^["']|["']$/g, '');
            // Try to convert to number if possible
            const num = parseFloat(cleaned);
            return isNaN(num) ? cleaned : num;
        })
    );

    // Find EBITDA row
    const ebitdaStartIndex = rows.findIndex(row => 
        row[0] && String(row[0]).toLowerCase().includes('ebitda margin')
    );

    if (ebitdaStartIndex === -1) {
        throw new Error('EBITDA Margin row not found');
    }

    // Get headers (company names)
    const headers = rows[0].slice(1).map(h => h ? h.trim() : null).filter(Boolean);
    console.log('Processed headers:', headers);

    // Process data rows
    const processedData = [];
    const quarters = new Set();
    let maxRevenue = 0;
    
    // Process rows between headers and EBITDA row
    let currentYear = null;
    let quarterCount = 0;

    for (let i = 1; i < ebitdaStartIndex; i++) {
        const row = rows[i];
        
        if (!row || !row[0]) {
            console.log(`Skipping row ${i}: Empty row`);
            continue;
        }
        
        // Get year from first column
        const year = String(row[0]).trim();
        if (!year || year === 'Revenue Growth YoY') {
            console.log(`Skipping row ${i}: Invalid year or header row`);
            continue;
        }
        
        // Reset quarter count when year changes
        if (year !== currentYear) {
            currentYear = year;
            quarterCount = 1;
        } else {
            quarterCount++;
        }
        
        // Get corresponding EBITDA row
        const ebitdaRow = rows[ebitdaStartIndex + (i - 1)];
        if (!ebitdaRow) {
            console.log(`Skipping row ${i}: No corresponding EBITDA row`);
            continue;
        }
        
        const quarter = `${year}'Q${quarterCount}`;
        
        // Process each company's data
        headers.forEach((company, j) => {
            const colIndex = j + 1;
            let revenueGrowth = parseFloat(row[colIndex]);
            let ebitdaMargin = parseFloat(ebitdaRow[colIndex]);
            
            if (!isNaN(revenueGrowth) && !isNaN(ebitdaMargin)) {
                // Convert to percentage if the values are in decimal format
                revenueGrowth = revenueGrowth <= 1 && revenueGrowth >= -1 ? revenueGrowth * 100 : revenueGrowth;
                ebitdaMargin = ebitdaMargin <= 1 && ebitdaMargin >= -1 ? ebitdaMargin * 100 : ebitdaMargin;
                
                // Use a scaled revenue value for bubble size
                const revenue = 1000 + Math.abs(revenueGrowth * 50); // Adjusted scaling factor
                maxRevenue = Math.max(maxRevenue, revenue);

                processedData.push({
                quarter,
                    company,
                    revenueGrowth: revenueGrowth,
                    ebitdaMargin: ebitdaMargin,
                    revenue: revenue
                });
                quarters.add(quarter);
            }
        });
    }

    // Update global maxRevenueValue
    maxRevenueValue = maxRevenue;

    console.log('Final processed data:', {
        totalQuarters: quarters.size,
        quarters: Array.from(quarters).sort(),
        totalDataPoints: processedData.length,
        sampleData: processedData.slice(0, 5),
        maxRevenue: maxRevenue
    });

    return processedData;
}

// Function to initialize company filters
function initializeCompanyFilters(data) {
    const companies = [...new Set(data.map(d => d.company))].sort();
    const filterContainer = d3.select("#company-filters");

    // Clear any existing filters
    filterContainer.html('');

    companies.forEach(companySymbol => {
        const id = `filter-${companySymbol}`;
        const companyName = companyNames[companySymbol] || companySymbol;

        const label = filterContainer.append("label")
            .attr("for", id)
            .style("display", "flex")
            .style("align-items", "center")
            .style("margin-bottom", "5px");

        const input = label.append("input")
            .attr("type", "checkbox")
            .attr("id", id)
            .attr("value", companySymbol)
            .property("checked", false) // Initialize all checkboxes as unchecked
            .on("change", handleFilterChange);

        label.append("span")
            .html(`${companySymbol} - ${companyName}`);
    });
}

// Function to handle filter changes
function handleFilterChange() {
    const checkedBoxes = d3.selectAll("#company-filters input[type='checkbox']")
        .nodes()
        .filter(d => d.checked)
        .map(d => d.value);

    selectedCompanies = checkedBoxes;

    const selectedQuarter = uniqueQuarters[currentQuarterIndex];
    updateBubbleChart(selectedQuarter, mergedData);
    updateBarChart(selectedQuarter, mergedData);
    updateLineCharts(mergedData);
}

// Function to fetch and process data from Google Sheet
async function importFromGoogleSheet() {
    const sheetUrl = `https://docs.google.com/spreadsheets/d/e/${sheetId}/pub?output=csv`;
    
    try {
        console.log('Starting Google Sheet import...');
        console.log('Using sheet URL:', sheetUrl);
        const response = await fetch(sheetUrl, {
            mode: 'cors',
            headers: {
                'Accept': 'text/csv'
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch data from Google Sheet');
        }
        
        const csvText = await response.text();
        console.log('Received CSV response length:', csvText.length);
        
        // Process the data
        mergedData = processData(csvText);
        
        // Initialize the visualization
        initializeVisualization(mergedData);
        
    } catch (error) {
        console.error('Error importing from Google Sheet:', error);
        console.error('Error stack:', error.stack);
        alert('Failed to import data: ' + error.message);
    }
}

// Function to initialize the visualization
function initializeVisualization(data) {
    // Sort quarters chronologically
    uniqueQuarters = [...new Set(data.map(d => d.quarter))].sort((a, b) => {
        // Parse YYYY'QN format
        const [yearA, quarterA] = a.split("'");
        const [yearB, quarterB] = b.split("'");
        
        // Compare years first
        const yearDiff = parseInt(yearA) - parseInt(yearB);
        if (yearDiff !== 0) return yearDiff;
        
        // If years are same, compare quarters (Q1, Q2, Q3, Q4)
        return parseInt(quarterA.substring(1)) - parseInt(quarterB.substring(1));
    });

    // Set initial quarter index to 0 (first quarter) instead of the last quarter
    currentQuarterIndex = 0;

    // Extract unique years and find Q1 indices
    let uniqueYears = [...new Set(uniqueQuarters.map(q => {
        const parts = q.split("'");
        return parts[0] || "";
    }))].filter(year => year !== "");

    // Add 2025 if it's not already included
    if (!uniqueYears.includes("2025")) {
        uniqueYears.push("2025");
    }

    const yearIndices = uniqueQuarters.reduce((acc, q, i) => {
        if (q.includes("Q1")) acc.push(i);
        return acc;
    }, []);

    // Add index for 2025 if it's not already included
    if (!yearIndices.includes(uniqueQuarters.length)) {
        yearIndices.push(uniqueQuarters.length);
    }

    // Initialize company filters
    initializeCompanyFilters(data);

    // Create timeline
    createTimeline(uniqueQuarters, data, yearIndices, uniqueYears);

    // Update initial charts
    updateBubbleChart(uniqueQuarters[currentQuarterIndex], data);
    updateBarChart(uniqueQuarters[currentQuarterIndex], data);
    updateLineCharts(data);
}

// Auto import data when page loads
document.addEventListener('DOMContentLoaded', async () => {
    try {
        await importFromGoogleSheet();
        raceBarChartData = await fetchRaceBarData();
        console.log('Successfully fetched race bar chart data');
        
        const firstQuarter = uniqueQuarters[0];

        // Initialize selectedCompanies with defaultSelectedCompanies
        selectedCompanies = [...defaultSelectedCompanies];

        // Set checkbox states based on defaultSelectedCompanies
        d3.selectAll("#company-filters input[type='checkbox']")
            .property("checked", function() {
                const company = this.value;
                return defaultSelectedCompanies.includes(company);
            });

        // Update charts with selected companies
        updateBubbleChart(firstQuarter, mergedData);
        updateBarChart(firstQuarter, mergedData);
        updateLineCharts(mergedData);

        // 确保 controls 元素存在
        let controlsElement = document.getElementById('controls');
        if (!controlsElement) {
            controlsElement = document.createElement('div');
            controlsElement.id = 'controls';
            document.body.appendChild(controlsElement);
        }

        // 添加视频生成按钮
        const videoButton = document.createElement('button');
        videoButton.innerHTML = '<i class="fas fa-video"></i> Generate Video';
        videoButton.className = 'control-button';
        videoButton.style.marginLeft = '10px';
        controlsElement.appendChild(videoButton);

        // Add click event listener to the video button
        videoButton.addEventListener('click', async () => {
            videoButton.disabled = true;
            videoButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
            try {
                await generateRaceBarChartVideo();
                videoButton.innerHTML = '<i class="fas fa-video"></i> Generate Video';
    } catch (error) {
                console.error('Error generating video:', error);
                videoButton.innerHTML = '<i class="fas fa-video"></i> Retry Generate';
            }
            videoButton.disabled = false;
        });

        // Automatically start playing the animation
        setTimeout(() => {
            const playButton = document.getElementById('play-button');
            if (playButton && !isPlaying) {
                playButton.click();
            }
        }, 1000);

    } catch (error) {
        console.error('Failed to load data:', error);
    }
});

// Function to create the interactive timeline using D3.js
function createTimeline(quarters, data, yearIndices, uniqueYears) {
    const timelineWidth = document.getElementById('timeline').offsetWidth;
    const margin = { left: 80, right: 80 };
    const width = timelineWidth - margin.left - margin.right;
    const height = 60;
    
    // Clear any existing timeline
    d3.select("#timeline svg").remove();
    
    const svg = d3.select("#timeline")
        .append('svg')
        .attr('width', timelineWidth)
        .attr('height', height);
    
    const g = svg.append('g')
        .attr('transform', `translate(${margin.left}, 30)`);
    
    // Create scale with extended domain to include 2025
    xScaleTimeline = d3.scaleLinear()
        .domain([0, quarters.length])  // Extended by 1 to include 2025
        .range([0, width]);
    
    // Define tick values for every quarter plus 2025
    const allTickValues = d3.range(0, quarters.length + 1);  // Added +1 to include 2025
    
    // Define the tick format to show year labels only for Q1 and 2025
    const axisBottom = d3.axisBottom(xScaleTimeline)
        .tickValues(allTickValues)
        .tickFormat((d, i) => {
            if (i === quarters.length) {
                return '2025';
            }
            if (yearIndices.includes(i)) {
                const yearIndex = yearIndices.indexOf(i);
                return uniqueYears[yearIndex] || '';
            }
            return '';
        });
    
    // Append the x-axis to the SVG
    g.append("g")
        .attr("class", "timeline-axis")
        .call(axisBottom)
        .selectAll("text")
        .style("text-anchor", "middle")
        .style("font-family", "Monda")
        .style("font-size", "12px");
    
    // Style the axis lines
    g.selectAll(".timeline-axis path, .timeline-axis line")
        .style("stroke", "#ccc")
        .style("stroke-width", "1px");
    
    // Differentiate tick lengths
    g.selectAll(".timeline-axis .tick line")
        .attr("y2", d => yearIndices.includes(d) || d === quarters.length ? 8 : 4)
        .attr("stroke", "#ccc");
    
    // Create the triangle indicator
    timelineTriangle = g.append("path")
        .attr("d", d3.symbol().type(d3.symbolTriangle).size(100))
        .attr("fill", "#4CAF50")
        .attr("transform", `translate(${xScaleTimeline(currentQuarterIndex)}, -10) rotate(180)`);

    // Make the timeline responsive
    window.addEventListener('resize', () => {
        const newWidth = document.getElementById('timeline').offsetWidth;
        const width = newWidth - margin.left - margin.right;
        svg.attr("width", newWidth);
        xScaleTimeline.range([0, width]);
        g.select(".timeline-axis")
            .call(axisBottom.scale(xScaleTimeline));

        const newX = xScaleTimeline(currentQuarterIndex);
        timelineTriangle
            .attr("transform", `translate(${newX}, -10) rotate(180)`);
    });
}

// Function to update the timeline triangle position with fractional positions
function updateTimelineTriangle(position) {
    if (!timelineTriangle) return;
    
    const timelineWidth = document.getElementById('timeline').offsetWidth;
    const margin = { left: 80, right: 80 };
    const width = timelineWidth - margin.left - margin.right;
    xScaleTimeline.range([0, width]);
    
    const x = xScaleTimeline(position);
    timelineTriangle
        .transition()
        .duration(0) // Immediate update for smooth movement
        .attr("transform", `translate(${x}, -10) rotate(180)`);
}

// Function to update the bubble chart
function updateBubbleChart(quarter, sheetData) {
    // Filter data for the selected quarter and selected companies
    const quarterData = sheetData
        .filter(d => {
            // Only include companies that have both revenue growth and EBITDA margin data
            // AND are within the plot range for current quarter
            const isInCurrentRange = d.quarter === quarter && 
                   selectedCompanies.includes(d.company) && 
                   d.revenueGrowth != null && 
                   d.ebitdaMargin != null &&
                   d.ebitdaMargin >= -60 && d.ebitdaMargin <= 60 && // Within x-axis range
                   d.revenueGrowth >= -49 && d.revenueGrowth <= 120; // Within y-axis range
            return isInCurrentRange;
        });

    if (quarterData.length === 0) {
        Plotly.react('bubble-chart', [], { title: `No data available for ${quarter}` });
        return;
    }

    // Get the current chart state
    const chartDiv = document.getElementById('bubble-chart');
    const currentLayout = chartDiv.layout || {};
    const currentImages = currentLayout.images || [];

    // Create a map of existing images by company
    const existingImageMap = new Map(
        currentImages.map(img => {
            // Extract company from source path
            const company = Object.entries(companyLogos).find(([_, path]) => path === img.source)?.[0];
            return [company, img];
        }).filter(([company]) => company) // Only keep images we can map to companies
    );

    // Prepare the bubble data
    const bubbleData = [{
        x: quarterData.map(d => d.ebitdaMargin),
        y: quarterData.map(d => d.revenueGrowth),
        text: quarterData.map(d => ''),
        mode: 'markers',
        marker: {
            size: quarterData.map(d => Math.sqrt(Math.abs(d.revenue)) * 0.7),
            color: quarterData.map(d => color_dict[d.company] || '#999999'),
            sizemode: 'area',
            sizeref: 2.0 * Math.max(...quarterData.map(d => Math.sqrt(Math.abs(d.revenue)))) / (20**2),
            sizemin: 8,
            line: {
                color: 'white',
                width: 1
            }
        },
        customdata: quarterData.map(d => d.company),
        hoverinfo: 'text',
        hovertext: quarterData.map(d => `${d.company}<br>Revenue Growth: ${d.revenueGrowth.toFixed(1)}%<br>EBITDA Margin: ${d.ebitdaMargin.toFixed(1)}%<br>Revenue: $${d3.format(",")(d.revenue)}M`)
    }];

    // Prepare images array, starting with all existing images
    let images = [...currentImages];

    // Update positions for existing images and add new ones only for new companies
    quarterData.forEach(d => {
        const existingImage = existingImageMap.get(d.company);
        if (existingImage) {
            // Update position of existing image
            const imageIndex = images.findIndex(img => img.source === existingImage.source);
            if (imageIndex !== -1) {
                images[imageIndex] = {
                    ...existingImage,
                    x: d.ebitdaMargin,
                    y: d.revenueGrowth + 14
                };
            }
        } else {
            // Only create new image if company doesn't already have one
            const logoPath = companyLogos[d.company];
            if (logoPath) {
                images.push({
                    source: logoPath,
                    xref: 'x',
                    yref: 'y',
                    x: d.ebitdaMargin,
                    y: d.revenueGrowth + 14,
                    sizex: 16,
                    sizey: 16,
                    xanchor: 'center',
                    yanchor: 'center',
                    layer: 'above',
                    sizing: 'contain',
                    opacity: 1,
                    rendering: 'crispEdges',
                    visible: true
                });
            }
        }
    });

    // Remove images for companies that are no longer in the data
    const currentCompanies = new Set(quarterData.map(d => d.company));
    images = images.filter(img => {
        const company = Object.entries(companyLogos).find(([_, path]) => path === img.source)?.[0];
        return company && currentCompanies.has(company);
    });

    // Define the layout with images
    const layout = {
        title: {
            text: `Revenue Growth vs EBITDA Margin for ${quarter}`,
            font: {
                family: 'Monda',
                size: 16
            }
        },
        xaxis: { 
            title: {
                text: 'EBITDA Margin (%)',
                font: {
                    family: 'Monda',
                    size: 12
                }
            },
            range: [-60, 60], 
            gridcolor: '#eee',
            zeroline: true,
            zerolinecolor: '#4e843d',
            zerolinewidth: 1,
            tickfont: {
                family: 'Monda',
                size: 10
            }
        },
        yaxis: { 
            title: {
                text: 'Revenue Growth YoY (%)',
                font: {
                    family: 'Monda',
                    size: 12
                }
            },
            range: [-49, 120], 
            gridcolor: '#eee',
            zeroline: true,
            zerolinecolor: '#4e843d',
            zerolinewidth: 1,
            tickfont: {
                family: 'Monda',
                size: 10
            }
        },
        margin: { t: 60, l: 80, r: 80, b: 80 },
        showlegend: false,
        hovermode: 'closest',
        plot_bgcolor: 'white',
        paper_bgcolor: 'white',
        font: {
            family: 'Monda'
        },
        images: images,
        datarevision: Date.now(),
        config: {
            responsive: true,
            displayModeBar: false,
            staticPlot: false
        }
    };

    // Check if the chart already exists
    if (chartDiv.data && chartDiv.data.length > 0) {
        // Update existing chart with no animation for data points
        Plotly.react('bubble-chart', bubbleData, layout, {
            displayModeBar: false,
            responsive: true,
            toImageButtonOptions: {
                format: 'png',
                filename: 'bubble_chart',
                height: 1000,
                width: 1000,
                scale: 2
            }
        });
    } else {
        // Initial render
        Plotly.newPlot('bubble-chart', bubbleData, layout, {
            displayModeBar: false,
            responsive: true,
            toImageButtonOptions: {
                format: 'png',
                filename: 'bubble_chart',
                height: 1000,
                width: 1000,
                scale: 2
            }
        });
    }
}

// Function to find the next different value for a company
function findNextDifferentValue(company, currentQuarter, data) {
    const allQuarters = [...new Set(data.map(d => d.quarter))].sort();
    const currentIndex = allQuarters.indexOf(currentQuarter);
    
    // Look forward
    for (let i = currentIndex + 1; i < allQuarters.length; i++) {
        const nextValue = data.find(d => d.company === company && d.quarter === allQuarters[i])?.revenue;
        if (nextValue !== undefined && nextValue > 0) {
            return nextValue;
        }
    }
    
    // If not found looking forward, look backward
    for (let i = currentIndex - 1; i >= 0; i--) {
        const prevValue = data.find(d => d.company === company && d.quarter === allQuarters[i])?.revenue;
        if (prevValue !== undefined && prevValue > 0) {
            return prevValue;
        }
    }
    
    return null;
}

// Function to create interpolated frames between two quarters
function createInterpolatedFrames(startData, endData, numFrames = 60) {
    const frames = [];
    
    // Get all unique companies that have data in either quarter
    const allCompanies = new Set([
        ...startData.map(d => d.company),
        ...endData.map(d => d.company)
    ]);
    
    // Create company states with extended transition timing
    const companyStates = {};
    allCompanies.forEach(company => {
        const startPoint = startData.find(d => d.company === company);
        const endPoint = endData.find(d => d.company === company);
        
        if (startPoint || endPoint) {
            companyStates[company] = {
                start: startPoint ? {
                    revenue: startPoint.revenue,
                    revenueGrowth: startPoint.revenueGrowth,
                    ebitdaMargin: startPoint.ebitdaMargin,
                    quarter: startPoint.quarter
                } : null,
                end: endPoint ? {
                    revenue: endPoint.revenue,
                    revenueGrowth: endPoint.revenueGrowth,
                    ebitdaMargin: endPoint.ebitdaMargin,
                    quarter: endPoint.quarter
                } : null,
                // Add transition type flag
                transitionType: startPoint && endPoint ? 'persist' :
                              startPoint ? 'fadeOut' : 'fadeIn'
            };
        }
    });
    
    // Create interpolated frames with improved timing
    for (let frame = 0; frame <= numFrames; frame++) {
        const t = frame / numFrames;
        const easedT = easeInOutCubic(t);
        const frameData = [];
        
        Object.entries(companyStates).forEach(([company, state]) => {
            if (!selectedCompanies.includes(company)) return;
            
            const { start, end, transitionType } = state;
            let interpolatedData = null;
            
            switch (transitionType) {
                case 'persist':
                    // Normal interpolation for persistent companies
                    interpolatedData = {
                        company,
                        revenue: start.revenue + (end.revenue - start.revenue) * easedT,
                        revenueGrowth: start.revenueGrowth + (end.revenueGrowth - start.revenueGrowth) * easedT,
                        ebitdaMargin: start.ebitdaMargin + (end.ebitdaMargin - start.ebitdaMargin) * easedT,
                        quarter: start.quarter
                    };
                    break;
                    
                case 'fadeOut':
                    // Slower fade out (stay visible longer)
                    if (t < 0.7) { // Stay fully visible for 70% of the transition
                        interpolatedData = {
                            company,
                            revenue: start.revenue,
                            revenueGrowth: start.revenueGrowth,
                            ebitdaMargin: start.ebitdaMargin,
                            quarter: start.quarter
                        };
                    } else {
                        // Fade out in the last 30% of the transition
                        const fadeOutT = 1 - ((t - 0.7) / 0.3);
                        interpolatedData = {
                            company,
                            revenue: start.revenue * fadeOutT,
                            revenueGrowth: start.revenueGrowth,
                            ebitdaMargin: start.ebitdaMargin,
                            quarter: start.quarter
                        };
                    }
                    break;
                    
                case 'fadeIn':
                    // Slower fade in (appear earlier and stay longer)
                    if (t > 0.3) { // Start appearing at 30% of the transition
                        const fadeInT = (t - 0.3) / 0.7;
                        const easedFadeIn = easeInOutCubic(fadeInT);
                        interpolatedData = {
                            company,
                            revenue: end.revenue * easedFadeIn,
                            revenueGrowth: end.revenueGrowth,
                            ebitdaMargin: end.ebitdaMargin,
                            quarter: end.quarter
                        };
                    }
                    break;
            }
            
            if (interpolatedData && interpolatedData.revenue > 0) {
                frameData.push({
                    ...interpolatedData,
                    companyName: companyNames[company] || company,
                    color: color_dict[company] || '#999999'
                });
            }
        });
        
        frames.push(frameData.sort((a, b) => b.revenue - a.revenue));
    }
    
    return frames;
}

function updateBarChart(quarter, sheetData) {
    if (!raceBarChartData) return;

    // If we're currently interpolating, use the current interpolation frame
    if (isInterpolating && interpolationFrames.length > 0) {
        const frameData = interpolationFrames[currentInterpolationFrame];
        renderBarChart(frameData);
        return;
    }

    // Get companies that have data for this quarter
    const companiesWithData = getCompaniesWithData(quarter, raceBarChartData);

    // Get data for current quarter, filtering out companies with zero or null revenue
    // and only include companies that are both selected and have data
    const quarterData = raceBarChartData
        .filter(d => {
            return d.quarter === quarter && 
                   d.revenue != null && 
                   d.revenue > 0 &&
                   selectedCompanies.includes(d.company) &&
                   companiesWithData.includes(d.company);
        })
        .sort((a, b) => b.revenue - a.revenue);

    renderBarChart(quarterData);
}

function renderBarChart(data) {
    if (data.length === 0) {
        Plotly.purge('bar-chart');
        return;
    }

    const margin = { l: 120, r: 120, t: 40, b: 50, autoexpand: false };
    const width = 450;
    const height = 400; // Fixed height
    const barHeight = 0.4; // Fixed bar height
    const maxBars = 15; // Maximum number of bars to show
    const barSpacing = 0.15; // Fixed spacing between bars

    // Calculate the maximum revenue across all quarters for consistent scaling
    const maxRevenue = Math.max(...raceBarChartData.map(d => d.revenue));

    // Sort data by revenue in descending order and limit to maxBars
    const sortedData = data
        .sort((a, b) => b.revenue - a.revenue)
        .slice(0, maxBars);

    // Prepare the bar chart data
    const barData = [{
        type: 'bar',
        x: sortedData.map(d => d.revenue),
        y: sortedData.map(d => d.company), // Use company symbol instead of full name
        orientation: 'h',
        marker: {
            color: sortedData.map(d => d.color || color_dict[d.company] || '#999999') // Use provided color or lookup
        },
        text: sortedData.map(d => {
            const value = d.revenue;
            if (value < 1) {
                return d3.format("$,.2f")(value) + "M";
            }
            return d3.format("$,.1f")(value) + "M";
        }),
        textposition: 'outside',
        hoverinfo: 'text',
        hovertext: sortedData.map(d => `${companyNames[d.company] || d.company}: $${d3.format(",")(d.revenue)}M`), // Keep full name in hover text
        textfont: {
            family: 'Monda',
            size: 11,
            color: '#333'
        },
        cliponaxis: false,
        textangle: 0,
        width: barHeight,
        constraintext: 'none'
    }];

    // Create layout with fixed range for both x and y axes
    const layout = {
        title: {
            text: `Revenue by Company (${sortedData[0]?.quarter || ''})`,
            font: { family: 'Monda', size: 16 }
        },
        width: width,
        height: height,
        xaxis: {
            title: {
                text: 'Revenue (USD M)',
                font: { family: 'Monda', size: 12 },
                standoff: 20
            },
            showgrid: true,
            gridcolor: '#eee',
            gridwidth: 1,
            zeroline: true,
            zerolinecolor: '#eee',
            tickfont: { family: 'Monda', size: 11 },
            range: [0, maxRevenue * 1.1],
            fixedrange: true,
            ticklen: 6,
            ticksuffix: '   ',
            automargin: true
        },
        yaxis: {
            showgrid: false,
            tickfont: { family: 'Monda', size: 11 },
            fixedrange: true,
            ticklabelposition: 'outside left',
            automargin: true,
            range: [maxBars - 0.5, -0.5], // Fixed range based on maxBars
            dtick: 1,
            side: 'left',
            autorange: false
        },
        margin: margin,
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        showlegend: false,
        barmode: 'group',
        bargap: barSpacing,
        bargroupgap: 0,
        font: { family: 'Monda' },
        uniformtext: {
            mode: 'show',
            minsize: 10
        }
    };

    // Check if the chart exists
    const chartDiv = document.getElementById('bar-chart');
    if (chartDiv.data && chartDiv.data.length > 0) {
        // Update with animation
        Plotly.animate('bar-chart', {
            data: barData,
            layout: layout,
            traces: [0]
        }, {
            transition: {
                duration: 0, // Remove transition duration for immediate update
                easing: 'linear'
            },
            frame: {
                duration: 0,
                redraw: true // Set to true to ensure proper redraw of bars
            }
        });
    } else {
        // Initial render
        Plotly.newPlot('bar-chart', barData, layout, {
            displayModeBar: false,
            responsive: true,
            staticPlot: false
        });
    }
}

function updateLineCharts(mergedData) {
    // Prepare the data for the line charts
    const quarters = [...new Set(mergedData.map(d => d.quarter))];

    // Sort the quarters in chronological order
    quarters.sort((a, b) => {
        try {
            const [aYear, aQ] = a.split("'");
            const [bYear, bQ] = b.split("'");
            const aQuarter = parseInt(aQ.substring(1));
            const bQuarter = parseInt(bQ.substring(1));
            return (parseInt(aYear) - parseInt(bYear)) || (aQuarter - bQuarter);
        } catch (error) {
            console.warn('Error parsing quarter:', error);
            return 0;
        }
    });
    
    // For each selected company, create traces for each metric
    const ebitdaMarginTraces = [];
    const revenueGrowthTraces = [];
    const revenueTraces = [];
    
    selectedCompanies.forEach(company => {
        const companyData = mergedData.filter(d => d.company === company);
        
        // Ensure data is sorted by quarter
        companyData.sort((a, b) => quarters.indexOf(a.quarter) - quarters.indexOf(b.quarter));
        
        // Get x (quarters) and y (values)
        const x = companyData.map(d => d.quarter);
        const yEbitdaMargin = companyData.map(d => d.ebitdaMargin * 100); // Convert to percentage
        const yRevenueGrowth = companyData.map(d => d.revenueGrowth * 100); // Convert to percentage
        const yRevenue = companyData.map(d => d.revenue);
        
        // Create traces for EBITDA Margin
        ebitdaMarginTraces.push({
            x: x,
            y: yEbitdaMargin,
            mode: 'lines+markers',
            name: company,
            line: { color: color_dict[company] || 'gray' },
            hovertemplate: `%{x}<br>${company}<br>EBITDA Margin: %{y:.1f}%<extra></extra>`
        });
        
        // Create traces for Revenue Growth
        revenueGrowthTraces.push({
            x: x,
            y: yRevenueGrowth,
            mode: 'lines+markers',
            name: company,
            line: { color: color_dict[company] || 'gray' },
            hovertemplate: `%{x}<br>${company}<br>Revenue Growth: %{y:.1f}%<extra></extra>`
        });
        
        // Create traces for Revenue
        revenueTraces.push({
            x: x,
            y: yRevenue,
            mode: 'lines+markers',
            name: company,
            line: { color: color_dict[company] || 'gray' },
            hovertemplate: `%{x}<br>${company}<br>Revenue: $%{y:,.0f}M<extra></extra>`
        });
    });
    
    // Define layouts for each chart
    const layoutEbitdaMargin = {
        title: 'EBITDA Margin Over Time',
        xaxis: { 
            title: 'Quarter', 
            tickangle: -45,
            categoryorder: 'array',
            categoryarray: quarters
        },
        yaxis: { 
            title: 'EBITDA Margin (%)',
            range: [-60, 60],
            zeroline: true,
            zerolinecolor: '#4e843d',
            zerolinewidth: 1
        },
        hovermode: 'x unified',
        margin: { t: 50, l: 80, r: 50, b: 100 },
        plot_bgcolor: 'white',
        paper_bgcolor: 'white'
    };
    
    const layoutRevenueGrowth = {
        title: 'Revenue Growth Over Time',
        xaxis: { 
            title: 'Quarter', 
            tickangle: -45,
            categoryorder: 'array',
            categoryarray: quarters
        },
        yaxis: { 
            title: 'Revenue Growth YoY (%)',
            range: [-40, 110],
            zeroline: true,
            zerolinecolor: '#4e843d',
            zerolinewidth: 1
        },
        hovermode: 'x unified',
        margin: { t: 50, l: 80, r: 50, b: 100 },
        plot_bgcolor: 'white',
        paper_bgcolor: 'white'
    };
    
    const layoutRevenue = {
        title: 'Revenue Over Time',
        xaxis: { 
            title: 'Quarter', 
            tickangle: -45,
            categoryorder: 'array',
            categoryarray: quarters
        },
        yaxis: { 
            title: 'Revenue (in Millions)',
            zeroline: true,
            zerolinecolor: '#4e843d',
            zerolinewidth: 1
        },
        hovermode: 'x unified',
        margin: { t: 50, l: 80, r: 50, b: 100 },
        plot_bgcolor: 'white',
        paper_bgcolor: 'white'
    };
    
    // Plot the charts using Plotly
    try {
    Plotly.react('line-chart-ebitda-margin', ebitdaMarginTraces, layoutEbitdaMargin, { responsive: true });
    Plotly.react('line-chart-revenue-growth', revenueGrowthTraces, layoutRevenueGrowth, { responsive: true });
    Plotly.react('line-chart-revenue', revenueTraces, layoutRevenue, { responsive: true });
    } catch (error) {
        console.error('Error updating line charts:', error);
}
}

// Function to get Q2 data for a specific year
function getQ2DataForYear(data, year) {
    return data.filter(d => {
        const quarter = d.quarter;
        const [dataYear, quarterNum] = quarter.split("'Q");
        return dataYear === year && quarterNum === "2";
    });
}

// Function to handle the Play/Pause button
function handlePlayPause() {
    const playButton = document.getElementById('play-button');
    const playIcon = playButton.querySelector('i');
    if (isPlaying) {
        clearInterval(playInterval);
        playButton.textContent = '';
        playButton.appendChild(playIcon);
        playButton.appendChild(document.createTextNode(' Play'));
        isPlaying = false;
        isInterpolating = false;
    } else {
        playButton.textContent = '';
        playButton.appendChild(playIcon);
        playButton.appendChild(document.createTextNode(' Pause'));
        isPlaying = true;
        
        const totalDuration = 30000; // 30秒总时长
        let startTime = null;
        let lastFrameTime = 0;
        const minFrameInterval = 1000 / 60; // 60FPS
        
        function animate(timestamp) {
            if (!isPlaying) return;
            
            // 控制帧率
            const deltaFrame = timestamp - lastFrameTime;
            if (deltaFrame < minFrameInterval) {
                requestAnimationFrame(animate);
                return;
            }
            lastFrameTime = timestamp;
            
            if (!startTime) {
                startTime = timestamp;
            }
            
            // 计算动画进度 (0 到 1)
            const progress = Math.min((timestamp - startTime) / totalDuration, 1);
            
            // 计算当前应该在哪个季度之间
            const totalQuarters = uniqueQuarters.length - 1; // 总季度间隔数
            const quarterPosition = progress * totalQuarters;
            const currentQuarterIndex = Math.floor(quarterPosition);
            const nextQuarterIndex = Math.min(currentQuarterIndex + 1, uniqueQuarters.length - 1);
            const quarterProgress = quarterPosition - currentQuarterIndex; // 在当前季度对中的进度
            
            // 更新时间轴位置
            updateTimelineTriangle(quarterPosition);
            
            // 获取当前和下一个季度的数据
            const currentQuarter = uniqueQuarters[currentQuarterIndex];
            const nextQuarter = uniqueQuarters[nextQuarterIndex];
            
            // 预先过滤和排序数据
            const currentData = mergedData
                .filter(d => d.quarter === currentQuarter && d.revenue > 0 && selectedCompanies.includes(d.company))
                .sort((a, b) => b.revenue - a.revenue);
            const nextData = mergedData
                .filter(d => d.quarter === nextQuarter && d.revenue > 0 && selectedCompanies.includes(d.company))
                .sort((a, b) => b.revenue - a.revenue);
            
            // 使用 easeInOutCubic 使过渡更平滑
            const easedProgress = easeInOutCubic(quarterProgress);
            
            // 计算插值数据
            const interpolatedData = currentData.map(current => {
                const next = nextData.find(d => d.company === current.company) || current;
                return {
                    company: current.company,
                    quarter: current.quarter,
                    revenueGrowth: current.revenueGrowth + (next.revenueGrowth - current.revenueGrowth) * easedProgress,
                    ebitdaMargin: current.ebitdaMargin + (next.ebitdaMargin - current.ebitdaMargin) * easedProgress,
                    revenue: current.revenue + (next.revenue - current.revenue) * easedProgress
                };
            });
            
            // 更新图表
            requestAnimationFrame(() => {
                updateBubbleChart(currentQuarter, interpolatedData);
                updateBarChart(currentQuarter, interpolatedData);
            });
            
            // 如果动画还没结束，继续下一帧
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                // 动画结束，重新开始
                startTime = timestamp;
                requestAnimationFrame(animate);
            }
        }
        
        requestAnimationFrame(animate);
    }
}

// Tooltip Functions
const tooltip = d3.select("#chart-tooltip");

function showTooltip(event, content) {
    tooltip
        .html(content)
        .style("left", (event.pageX + 15) + "px")
        .style("top", (event.pageY - 28) + "px")
        .transition()
        .duration(200)
        .style("opacity", .9);
}

function moveTooltip(event) {
    tooltip
        .style("left", (event.pageX + 15) + "px")
        .style("top", (event.pageY - 28) + "px");
}

function hideTooltip() {
    tooltip
        .transition()
        .duration(500)
        .style("opacity", 0);
}

// Debounce Function to limit the rate of function execution
function debounce(func, delay) {
    let timeout;
    return function(...args) {
        const context = this;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), delay);
    };
}

// Enhanced Search Functionality with Debounce and Highlighting
d3.select("#search-input").on("input", debounce(function() {
    const searchTerm = this.value.trim().toLowerCase();

    d3.selectAll("#company-filters label")
        .style("display", function() {
            const companySymbol = d3.select(this).select("input").attr("value");
            const companyName = companyNames[companySymbol] || companySymbol;

            // Check if either symbol or name includes the search term
            const symbolMatch = companySymbol.toLowerCase().includes(searchTerm);
            const nameMatch = companyName.toLowerCase().includes(searchTerm);

            if (symbolMatch || nameMatch) {
                // Highlight matching parts
                let displayText = `${companySymbol} - ${companyName}`;

                if (searchTerm !== "") {
                    const regex = new RegExp(`(${searchTerm})`, 'gi');
                    displayText = displayText.replace(regex, '<span class="highlight">$1</span>');
                }

                d3.select(this).select("span").html(displayText);
                return "flex";
            } else {
                // Remove any existing highlights and hide the label
                d3.select(this).select("span").html(`${companySymbol} - ${companyName}`);
                return "none";
            }
        });
}, 300)); // 300ms delay

// Select All and Deselect All Button Functions
d3.select("#select-all").on("click", () => {
    d3.selectAll("#company-filters input[type='checkbox']")
        .property("checked", true)
        .each(function() {
            const company = this.value;
            if (!selectedCompanies.includes(company)) {
                selectedCompanies.push(company);
            }
        });
    updateBubbleChart(uniqueQuarters[currentQuarterIndex], mergedData);
    updateBarChart(uniqueQuarters[currentQuarterIndex], mergedData);
    updateLineCharts(mergedData); // Update line charts
});

d3.select("#deselect-all").on("click", () => {
    d3.selectAll("#company-filters input[type='checkbox']")
        .property("checked", false);
    selectedCompanies = [];
    updateBubbleChart(uniqueQuarters[currentQuarterIndex], mergedData);
    updateBarChart(uniqueQuarters[currentQuarterIndex], mergedData);
    updateLineCharts(mergedData); // Update line charts
});

// Initialize Tooltip for Play Button
const playTooltip = d3.select("#play-tooltip");

d3.select("#play-button")
    .on("mouseover", function(event) {
        playTooltip
            .style("opacity", 1)
            .style("left", (event.pageX + 10) + "px")
            .style("top", (event.pageY - 10) + "px")
            .text(isPlaying ? "Click to Pause" : "Click to Play");
    })
    .on("mousemove", function(event) {
        playTooltip
            .style("left", (event.pageX + 10) + "px")
            .style("top", (event.pageY - 10) + "px");
    })
    .on("mouseout", function() {
        playTooltip
            .style("opacity", 0);
    });

// Event listener for the Play/Pause button
document.getElementById('play-button').addEventListener('click', handlePlayPause);

// Function to fetch and process race bar chart data
async function fetchRaceBarData() {
    const sheetId = '2PACX-1vQYwQTSYwig7AZ0fjPniLVfUUJnLz3PP4f4fBtqkBNPYqrkKtQyZDaB99kHk2eCzuCh5i8oxTPCHeQ9';
    const gid = '621483928';  // Specific sheet ID for Revenue data
    const sheetUrl = `https://docs.google.com/spreadsheets/d/e/${sheetId}/pub?gid=${gid}&output=csv`;
    
    try {
        console.log('Starting Race Bar Chart data import...');
        console.log('Using sheet URL:', sheetUrl);
        
        const response = await fetch(sheetUrl, {
            mode: 'cors',
            headers: {
                'Accept': 'text/csv'
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch Race Bar Chart data');
        }
        
        const csvText = await response.text();
        console.log('Received Race Bar CSV response length:', csvText.length);
        
        // Split into lines first
        const lines = csvText.split('\n');
        console.log('Total number of lines:', lines.length);
        
        // Process each line, properly handling quoted fields that may contain commas
        const rows = lines.map(line => {
            const row = [];
            let inQuotes = false;
            let currentValue = '';
            
            for (let i = 0; i < line.length; i++) {
                const char = line[i];
                
                if (char === '"') {
                    inQuotes = !inQuotes;
                    continue;
                }
                
                if (char === ',' && !inQuotes) {
                    row.push(currentValue.trim());
                    currentValue = '';
                    continue;
                }
                
                currentValue += char;
            }
            
            // Push the last value
            row.push(currentValue.trim());
            return row;
        });
        
        // Get headers (company names)
        const headers = rows[0].filter(Boolean);
        console.log('Race Bar Chart Headers (Companies):', headers);
        console.log('Number of companies:', headers.length);
        
        // Debug: Print first few rows of raw data
        console.log('=== Raw Data Sample ===');
        for (let i = 0; i < Math.min(5, rows.length); i++) {
            console.log(`Row ${i}:`, rows[i]);
        }
        
        // Process data rows
        const processedData = [];
        const quarterData = {}; // Object to store data by quarter
        
        // Function to clean and parse revenue values
        function parseRevenue(value) {
            if (!value || value.trim() === '') return null;
            
            // Remove $ sign, commas, and any quotes
            const cleanValue = value.replace(/[$,'"]/g, '');
            
            // Parse the clean value
            const number = parseFloat(cleanValue);
            
            // Return null if not a valid number or negative
            return !isNaN(number) ? number : null;
        }
        
        for (let i = 1; i < rows.length; i++) {
            const row = rows[i];
            if (!row[0] || row[0] === 'Revenue') continue;  // Skip empty rows and the 'Revenue' row
            
            const quarter = row[0];
            if (!quarterData[quarter]) {
                quarterData[quarter] = [];
            }
            
            headers.forEach((company, j) => {
                const revenue = parseRevenue(row[j + 1]);
                if (revenue !== null) {
                    const dataPoint = {
                        quarter,
                        company,
                        revenue
                    };
                    processedData.push(dataPoint);
                    quarterData[quarter].push(dataPoint);
                }
            });
        }
        
        // Log detailed information about the data
        console.log('=== Race Bar Chart Data Summary ===');
        console.log('Total data points:', processedData.length);
        console.log('Quarters found:', Object.keys(quarterData).filter(q => quarterData[q].length > 0));
        console.log('\nData by Quarter:');
        Object.entries(quarterData).forEach(([quarter, data]) => {
            if (data.length > 0) {  // Only show quarters with data
                console.log(`\n${quarter}:`);
                console.log('Number of companies:', data.length);
                console.log('Companies and revenues:');
                data.sort((a, b) => b.revenue - a.revenue)  // Sort by revenue in descending order
                    .forEach(({company, revenue}) => {
                        console.log(`${company}: ${revenue.toLocaleString()}`);
                    });
            }
        });
        
        console.log('\nSample of processed data:', processedData.slice(0, 5));
        console.log('=== End of Race Bar Chart Data Summary ===');
        
        return processedData;
        
    } catch (error) {
        console.error('Error importing Race Bar Chart data:', error);
        throw error;
    }
}

// Function to generate and download race bar chart video
async function generateRaceBarChartVideo() {
    // Ensure the bar chart is visible and rendered
    const barChart = document.getElementById('bar-chart');
    if (!barChart) {
        throw new Error('Bar chart element not found');
    }

    // Create MediaRecorder with high quality settings
    const stream = barChart.captureStream(60); // 60fps
    const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'video/webm;codecs=vp9',
        videoBitsPerSecond: 5000000 // 5Mbps for high quality
    });

    const chunks = [];
    mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
    
    // Create a promise that resolves when recording is complete
    const recordingPromise = new Promise((resolve, reject) => {
        mediaRecorder.onstop = () => {
            try {
                const blob = new Blob(chunks, { type: 'video/webm' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'race_bar_chart.webm';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                resolve();
            } catch (error) {
                reject(error);
            }
        };
    });

    // Start recording
    mediaRecorder.start();
    console.log('Started recording...');

    // Simulate the animation for video
    const uniqueYears = [...new Set(uniqueQuarters.map(q => q.split("'")[0]))].sort();
    let currentYearIndex = 0;
    const totalDuration = 30000; // 30 seconds
    const transitionDuration = totalDuration / (uniqueYears.length - 1);

    try {
        while (currentYearIndex < uniqueYears.length - 1) {
            const currentYear = uniqueYears[currentYearIndex];
            const nextYear = uniqueYears[currentYearIndex + 1];
            
            const currentData = getQ2DataForYear(raceBarChartData, currentYear)
                .filter(d => d.revenue > 0)
                .sort((a, b) => b.revenue - a.revenue);
            const nextData = getQ2DataForYear(raceBarChartData, nextYear)
                .filter(d => d.revenue > 0)
                .sort((a, b) => b.revenue - a.revenue);
            
            const frames = createInterpolatedFrames(currentData, nextData, 60);
            const frameDelay = transitionDuration / frames.length;
            
            for (let i = 0; i < frames.length; i++) {
                const frameData = frames[i];
                renderBarChart(frameData);
                await new Promise(resolve => setTimeout(resolve, frameDelay));
            }
            
            currentYearIndex++;
        }

        // Ensure we stay on the last frame for a moment
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Stop recording and wait for the file to be processed
        mediaRecorder.stop();
        await recordingPromise;
        
        console.log('Video generation completed');
    } catch (error) {
        console.error('Error during video generation:', error);
        mediaRecorder.stop();
        throw error;
    }
}