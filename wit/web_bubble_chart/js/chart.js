// Global variables
let isPlaying = false;
let playInterval;
let currentQuarterIndex = 0;
let uniqueQuarters;
let mergedData;
let timelineTriangle;
let xScaleTimeline;
let selectedCompanies = window.appConfig.defaultSelectedCompanies;

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
            console.log('Loaded data:', jsonData); // Debug log

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
        y: yearData.map(d => Math.sqrt(d.OnlineBookings)),
        text: yearData.map(d => d.Market),
        mode: 'markers',
        marker: {
            size: yearData.map(d => Math.sqrt(d.GrossBookings / 1e9) * 50),
            color: "rgba(0,0,0,0)" // Make markers completely transparent
        },
        hovertemplate: '<b>%{text}</b><br>' +
                      'Online Penetration: %{x:.1%}<br>' +
                      'Online Bookings: %{customdata[0]:$,.0f}M<br>' +
                      'Gross Bookings: %{customdata[1]:$,.0f}M<br>' +
                      '<extra></extra>',
        customdata: yearData.map(d => [d.OnlineBookings, d.GrossBookings])
    };

    // Get maximum dimension for scaling
    const maxDim = Math.max(
        d3.max(yearData, d => d.OnlinePenetration),
        d3.max(yearData, d => Math.sqrt(d.OnlineBookings))
    );

    // Create layout with flag images
    const layout = {
        title: `APAC Travel Market ${year}`,
        xaxis: {
            title: 'Online Penetration',
            tickformat: ',.0%',
            range: [0, Math.max(1, d3.max(yearData, d => d.OnlinePenetration) * 1.1)]
        },
        yaxis: {
            title: 'Online Bookings Volume',
            range: [0, d3.max(yearData, d => Math.sqrt(d.OnlineBookings)) * 1.3]
        },
        showlegend: false,
        hovermode: 'closest',
        images: []
    };

    // Add flag images
    yearData.forEach(d => {
        const logo = window.appConfig.companyLogos[d.Market];
        if (logo) {
            // Calculate size based on gross bookings relative to maximum
            const maxGrossBookings = d3.max(yearData, d => d.GrossBookings);
            const relativeSize = Math.sqrt(d.GrossBookings / maxGrossBookings);
            const size = relativeSize * maxDim * 0.2 + maxDim * 0.05;

            layout.images.push({
                source: logo,
                xref: "x",
                yref: "y",
                x: d.OnlinePenetration,
                y: Math.sqrt(d.OnlineBookings),
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