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

    // Create layout with flag images
    const layout = {
        title: `APAC Travel Market ${year}`,
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
        images: [],
        dragmode: false,
        annotations: [{
            text: getEraText(year),
            x: 0.5,
            y: Math.sqrt(250)/2,
            xref: 'paper',
            yref: 'paper',
            showarrow: false,
            font: {
                family: 'Montserrat, Arial',
                size: 60,
                color: 'rgba(200, 200, 200, 0.3)'
            }
        },
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
        }]
    };

    // Add flag images
    yearData.forEach(d => {
        const logo = window.appConfig.companyLogos[d.Market];
        if (logo) {
            const maxGrossBookings = d3.max(data, d => d.GrossBookings);
            const relativeSize = Math.pow(d.GrossBookings / maxGrossBookings, 0.25);
            const size = relativeSize * 2.5 + 0.15;

            layout.images.push({
                source: logo,
                xref: "x",
                yref: "y",
                x: d.OnlinePenetration,
                y: Math.sqrt(d.OnlineBookings / 1e9),
                sizex: size,
                sizey: size,
                sizing: "contain",
                opacity: 0.8,
                layer: "above",
                xanchor: "center",
                yanchor: "middle"
            });
        }
    });

    Plotly.react('bubble-chart', [trace], layout, { responsive: true });
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
        .duration(300)
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
        }, 1000);
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

    // Event listeners
    document.getElementById('play-button').addEventListener('click', handlePlayPause);
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