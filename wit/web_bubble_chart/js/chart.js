// Global variables
let isPlaying = false;
let playInterval;
let currentQuarterIndex = 0;
let uniqueQuarters;
let mergedData;
let timelineTriangle;
let xScaleTimeline;
let selectedCompanies = window.appConfig.defaultSelectedCompanies;
let globalMaxOnlinePenetration;
let globalMaxOnlineBookings;

// Function to initialize global max values
function initializeGlobalMaxValues(data) {
    globalMaxOnlinePenetration = d3.max(data, d => d.OnlinePenetration);
    globalMaxOnlineBookings = d3.max(data, d => Math.sqrt(d.OnlineBookings));
}

// Function to fetch and process Excel data
async function fetchData() {
    try {
        const response = await fetch('travel_market_summary.xlsx');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const arrayBuffer = await response.arrayBuffer();
        const data = new Uint8Array(arrayBuffer);
        
        try {
            const workbook = XLSX.read(data, { type: 'array' });
            
            // Read the 'Visualization Data' sheet
            const sheet = workbook.Sheets['Visualization Data'];
            if (!sheet) {
                throw new Error("Sheet 'Visualization Data' not found");
            }
            
            const jsonData = XLSX.utils.sheet_to_json(sheet);
            console.log('Raw data:', jsonData); // Debug log

            // Process data similar to Python code
            const processedData = jsonData
                .filter(row => row['Region'] === 'APAC')
                .filter(row => !(row['Online Bookings'] === 0 && 
                               row['Gross Bookings'] === 0 && 
                               row['Online Penetration'] === 0))
                .map(row => ({
                    Market: row['Market'],
                    Year: row['Year'],
                    OnlinePenetration: row['Online Penetration'] / 100,
                    OnlineBookings: row['Online Bookings'],
                    GrossBookings: row['Gross Bookings']
                }));

            console.log('Processed data:', processedData); // Debug log
            return processedData;
        } catch (parseError) {
            console.error('Error parsing Excel file:', parseError);
            throw new Error('Failed to parse Excel file: ' + parseError.message);
        }
    } catch (error) {
        console.error('Error loading data:', error);
        return [];
    }
}

// Function to update bubble chart
function updateBubbleChart(data, year) {
    const yearData = data.filter(d => d.Year === year && selectedCompanies.includes(d.Market));
    
    // Create background text trace
    const backgroundTrace = {
        x: [0.5], // Center of x-axis
        y: [Math.sqrt(250/4)], // Lower the position by using one-third of max value
        mode: 'text',
        text: [getEraText(year)],
        textposition: 'middle center',
        textfont: {
            size: 60,
            family: 'Montserrat, Arial',
            color: 'rgba(200,200,200,0.3)'
        },
        hoverinfo: 'skip',
        showlegend: false
    };

    // Create base scatter plot with invisible markers
    const trace = {
        x: yearData.map(d => d.OnlinePenetration),
        y: yearData.map(d => Math.sqrt(d.OnlineBookings / 1e9)),
        text: yearData.map(d => d.Market),
        mode: 'markers',
        marker: {
            size: yearData.map(d => Math.pow(d.GrossBookings / 1e9, 0.15) * 4000),
            color: "rgba(0,0,0,0)"
        },
        hovertemplate: '<b>%{text}</b><br>' +
                      'Online Penetration: %{x:.1%}<br>' +
                      'Online Bookings: %{customdata[0]:$,.0f}B<br>' +
                      'Gross Bookings: %{customdata[1]:$,.0f}B<br>' +
                      '<extra></extra>',
        customdata: yearData.map(d => [d.OnlineBookings / 1e9, d.GrossBookings / 1e9])
    };

    // Create layout
    const layout = {
        title: 'APAC Travel Market',
        xaxis: {
            title: 'Online Penetration',
            tickformat: ',.0%',
            range: [0, 1],
            gridcolor: '#eee'
        },
        yaxis: {
            title: 'Online Bookings Volume (Billion USD)',
            range: [0, Math.sqrt(250)],
            gridcolor: '#eee',
            ticktext: ['0', '10', '40', '90', '160', '250'],
            tickvals: [0, Math.sqrt(10), Math.sqrt(40), Math.sqrt(90), Math.sqrt(160), Math.sqrt(250)],
            tickmode: 'array'
        },
        showlegend: false,
        hovermode: 'closest',
        plot_bgcolor: 'white',
        paper_bgcolor: 'white',
        dragmode: false,
        annotations: [{
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
        }]
    };

    // Check if the chart already exists
    const chartDiv = document.getElementById('bubble-chart');
    if (!chartDiv.data) {
        // First time creation
        Plotly.newPlot('bubble-chart', [backgroundTrace, trace], layout, { 
            responsive: true,
            displayModeBar: false
        }).then(() => {
            // Add company logos after initial plot
            const images = yearData.map(d => {
                const logo = window.appConfig.companyLogos[d.Market];
                if (!logo) return null;

                const maxGrossBookings = d3.max(data, d => d.GrossBookings);
                const relativeSize = Math.pow(d.GrossBookings / maxGrossBookings, 0.25);
                const targetSize = relativeSize * 2.5 + 0.15;

                return {
                    source: logo,
                    xref: "x",
                    yref: "y",
                    x: d.OnlinePenetration,
                    y: Math.sqrt(d.OnlineBookings / 1e9),
                    sizex: targetSize,
                    sizey: targetSize,
                    sizing: "contain",
                    opacity: 0.8,
                    layer: "above",
                    xanchor: "center",
                    yanchor: "middle"
                };
            }).filter(Boolean);

            Plotly.relayout('bubble-chart', { images });
        });
    } else {
        // Get the previous data
        const prevData = chartDiv.data[1]; // Index 1 is the bubble trace
        const prevImages = chartDiv._fullLayout.images || [];
        
        // Create interpolated frames for smooth transition
        const numFrames = 35;
        const frames = [];
        
        for (let i = 0; i <= numFrames; i++) {
            const t = i / numFrames; // Interpolation factor (0 to 1)
            
            // Interpolate data points
            const frameTrace = {
                x: yearData.map((d, idx) => {
                    const prevX = prevData.x[idx] || 0;
                    return prevX + (d.OnlinePenetration - prevX) * t;
                }),
                y: yearData.map((d, idx) => {
                    const prevY = prevData.y[idx] || 0;
                    const targetY = Math.sqrt(d.OnlineBookings / 1e9);
                    return prevY + (targetY - prevY) * t;
                }),
                text: yearData.map(d => d.Market),
                mode: 'markers',
                marker: {
                    size: yearData.map((d, idx) => {
                        const prevSize = prevData.marker.size[idx] || 0;
                        const targetSize = Math.pow(d.GrossBookings / 1e9, 0.15) * 4000;
                        return prevSize + (targetSize - prevSize) * t;
                    }),
                    color: "rgba(0,0,0,0)"
                }
            };

            // Interpolate images
            const frameImages = yearData.map((d, idx) => {
                const logo = window.appConfig.companyLogos[d.Market];
                if (!logo) return null;

                const maxGrossBookings = d3.max(data, d => d.GrossBookings);
                const relativeSize = Math.pow(d.GrossBookings / maxGrossBookings, 0.25);
                const targetSize = relativeSize * 2.5 + 0.15;
                
                const prevImage = prevImages[idx] || {};
                const prevX = prevImage.x || 0;
                const prevY = prevImage.y || 0;
                const prevSize = prevImage.sizex || 0;

                return {
                    source: logo,
                    xref: "x",
                    yref: "y",
                    x: prevX + (d.OnlinePenetration - prevX) * t,
                    y: prevY + (Math.sqrt(d.OnlineBookings / 1e9) - prevY) * t,
                    sizex: prevSize + (targetSize - prevSize) * t,
                    sizey: prevSize + (targetSize - prevSize) * t,
                    sizing: "contain",
                    opacity: 0.8,
                    layer: "above",
                    xanchor: "center",
                    yanchor: "middle"
                };
            }).filter(Boolean);

            frames.push({
                data: [backgroundTrace, frameTrace],
                layout: {
                    ...layout,
                    images: frameImages
                }
            });
        }

        // Animate through the frames
        let currentFrame = 0;
        const animate = () => {
            if (currentFrame >= frames.length) return;
            
            Plotly.animate('bubble-chart', frames[currentFrame], {
                transition: {
                    duration: 35,
                    easing: 'linear'
                },
                frame: {
                    duration: 35,
                    redraw: false
                }
            });
            
            currentFrame++;
            requestAnimationFrame(animate);
        };

        animate();
    }
}

// Function to create timeline
function createTimeline(years) {
    const width = document.getElementById('timeline').clientWidth;
    const height = 80;
    
    const svg = d3.select("#timeline")
        .append("svg")
        .attr("width", width)
        .attr("height", height);

    xScaleTimeline = d3.scaleLinear()
        .domain([0, years.length - 1])
        .range([50, width - 50]);

    const axis = d3.axisBottom(xScaleTimeline)
        .tickFormat(i => years[i])
        .ticks(years.length);

    svg.append("g")
        .attr("transform", `translate(0,${height - 30})`)
        .call(axis);

    // Add triangle indicator
    timelineTriangle = svg.append("path")
        .attr("d", d3.symbol().type(d3.symbolTriangle).size(200))
        .attr("transform", `translate(${xScaleTimeline(0)},${height/2}) rotate(180)`)
        .attr("fill", "#666");

    // Make timeline responsive
    window.addEventListener('resize', () => {
        const newWidth = document.getElementById('timeline').clientWidth;
        svg.attr("width", newWidth);
        xScaleTimeline.range([50, newWidth - 50]);
        svg.select("g").call(axis);
        updateTimelineTriangle(currentQuarterIndex);
    });
}

// Function to update timeline triangle position
function updateTimelineTriangle(index) {
    const x = xScaleTimeline(index);
    timelineTriangle
        .transition()
        .duration(1800)  // Increased from 1200 to 1800 to match slower animation
        .ease(d3.easeCubicInOut)
        .attr("transform", `translate(${x},${40}) rotate(180)`);
}

// Function to handle play/pause
function handlePlayPause() {
    const button = document.getElementById('play-button');
    if (isPlaying) {
        clearInterval(playInterval);
        button.innerHTML = '<i class="fas fa-play"></i> Play';
        isPlaying = false;
    } else {
        button.innerHTML = '<i class="fas fa-pause"></i> Pause';
        isPlaying = true;
        playInterval = setInterval(() => {
            currentQuarterIndex = (currentQuarterIndex + 1) % uniqueQuarters.length;
            updateTimelineTriangle(currentQuarterIndex);
            updateBubbleChart(mergedData, uniqueQuarters[currentQuarterIndex]);
        }, 2000); // Increased from 800 to 2000 to give more time between transitions
    }
}

// Initialize the visualization
async function initialize() {
    mergedData = await fetchData();
    uniqueQuarters = [...new Set(mergedData.map(d => d.Year))].sort();
    
    // Initialize global max values
    initializeGlobalMaxValues(mergedData);
    
    createTimeline(uniqueQuarters);
    updateBubbleChart(mergedData, uniqueQuarters[currentQuarterIndex]);

    // Remove play button event listener and hide the button
    const playButton = document.getElementById('play-button');
    if (playButton) {
        playButton.style.display = 'none';
    }

    // Automatically start playing
    isPlaying = true;
    playInterval = setInterval(() => {
        currentQuarterIndex = (currentQuarterIndex + 1) % uniqueQuarters.length;
        updateTimelineTriangle(currentQuarterIndex);
        updateBubbleChart(mergedData, uniqueQuarters[currentQuarterIndex]);
    }, 1500); // Changed from 2000 to 1000 for faster year transitions
}

// Load XLSX library and initialize
const script = document.createElement('script');
script.src = 'https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js';
script.onload = initialize;
document.head.appendChild(script);

// Add this new function at the end of the file
function getEraText(year) {
    const yearNum = parseInt(year);
    if (yearNum >= 2005 && yearNum <= 2008) {
        return "Growth of WWW";
    } else if (yearNum >= 2009 && yearNum <= 2010) {
        return "Great Recession";
    } else if (yearNum >= 2011 && yearNum <= 2019) {
        return "Growth of Mobile";
    } else if (yearNum >= 2020 && yearNum <= 2021) {
        return "Global Pandemic";
    } else if (yearNum >= 2022) {
        return "Post-Pandemic Recovery";
    }
    return "";
} 