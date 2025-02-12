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
        y: yearData.map(d => Math.sqrt(d.OnlineBookings / 1e9)), // Convert to billions and apply sqrt
        text: yearData.map(d => d.Market),
        mode: 'markers',
        marker: {
            size: yearData.map(d => Math.sqrt(d.GrossBookings / 1e9) * 5000), // Significantly increased size multiplier
            color: "rgba(0,0,0,0)" // Make markers completely transparent
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
            range: [0, 1], // Fixed range from 0 to 100%
            gridcolor: '#eee'
        },
        yaxis: {
            title: 'Online Bookings Volume (Billion USD)',
            range: [0, Math.sqrt(250)], // Square root of max value
            gridcolor: '#eee',
            ticktext: ['0', '10', '40', '90', '160', '250'],
            tickvals: [0, Math.sqrt(10), Math.sqrt(40), Math.sqrt(90), Math.sqrt(160), Math.sqrt(250)],
            tickmode: 'array'
        },
        showlegend: false,
        hovermode: 'closest',
        plot_bgcolor: 'white',
        paper_bgcolor: 'white',
        images: []
    };

    // Add flag images
    yearData.forEach(d => {
        const logo = window.appConfig.companyLogos[d.Market];
        if (logo) {
            // Calculate size based on gross bookings relative to maximum
            const maxGrossBookings = d3.max(data, d => d.GrossBookings);
            const relativeSize = Math.sqrt(d.GrossBookings / maxGrossBookings);
            const size = relativeSize * 1.5 + 0.4; // Significantly increased base size and multiplier

            layout.images.push({
                source: logo,
                xref: "x",
                yref: "y",
                x: d.OnlinePenetration,
                y: Math.sqrt(d.OnlineBookings / 1e9), // Convert to billions and apply sqrt
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