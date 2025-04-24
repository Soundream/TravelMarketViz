// Main.js - Entry point for Airline Revenue Visualization

// Configuration is loaded from config.js

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', () => {
    // Load frame data and convert it to the right format
    prepareData()
        .then(() => {
            console.log('Data preparation complete, initializing visualization');
            // Initialize the visualization after data is loaded
            const visualization = new AirlineVisualization({
                containerId: 'chart-container',
                config: CONFIG
            });
            visualization.initialize();
            initializeUI();
        })
        .catch(error => {
            console.error('Error preparing data:', error);
            displayErrorMessage('Failed to load visualization data. Please try again later.');
        });
});

// Parse quarter string, e.g., "2000'Q1" to {year: 2000, quarter: 1}
function parseQuarter(quarterStr) {
    const parts = quarterStr.split("'");
    const year = parseInt(parts[0]);
    const quarter = parseInt(parts[1].substring(1));
    return { year, quarter };
}

// Format revenue for display
function formatRevenue(value) {
    if (value >= 1000) {
        return `$${(value/1000).toFixed(1)}B`;
    }
    return `$${value.toFixed(0)}M`;
}

// Prepare and convert frame data to JSON format
async function prepareData() {
    console.log('Using CSV data path:', CONFIG.csvDataPath);
    
    try {
        // Fetch the CSV data
        const response = await fetch(CONFIG.csvDataPath);
        if (!response.ok) {
            throw new Error(`Failed to fetch CSV data: ${response.status} ${response.statusText}`);
        }
        
        const csvText = await response.text();
        console.log('CSV data fetched successfully');
        
        // Parse CSV data
        const lines = csvText.split('\n');
        if (lines.length < 8) {
            throw new Error('CSV file format is invalid - not enough lines');
        }
        
        // Extract metadata and revenue data
        const metadata = [];
        for (let i = 0; i < 7; i++) {
            metadata.push(lines[i].split(','));
        }
        
        // Process metadata
        const airlineNames = metadata[0].slice(1); // First row is airline names
        const regions = {};
        const statuses = {};
        const countries = {};
        const iataCodes = {};
        
        // Map regions to colors
        const regionColors = {
            'North America': '#40E0D0',  // Turquoise
            'Europe': '#4169E1',         // Royal Blue
            'Asia Pacific': '#FF4B4B',   // Red
            'Latin America': '#32CD32',  // Lime Green
            'China': '#FF4B4B',          // Red (same as Asia Pacific)
            'Middle East': '#DEB887',    // Burlywood
            'Russia': '#FF4B4B',         // Red (same as Asia Pacific)
            'Turkey': '#DEB887',         // Burlywood (same as Middle East)
            'India': '#FF9900',          // Orange
            'Africa': '#9932CC'          // Dark Orchid
        };
        
        // Parse metadata
        for (let i = 0; i < airlineNames.length; i++) {
            const airline = airlineNames[i];
            regions[airline] = metadata[3][i + 1]; // Region is in the 4th row
            statuses[airline] = metadata[1][i + 1]; // Status is in the 2nd row
            countries[airline] = metadata[2][i + 1]; // Country is in the 3rd row
            iataCodes[airline] = metadata[4][i + 1]; // IATA Code is in the 5th row
        }
        
        // Parse revenue data
        const revenueData = {};
        for (let i = 7; i < lines.length; i++) {
            const line = lines[i].trim();
            if (!line) continue;
            
            const values = line.split(',');
            const quarter = values[0]; // e.g., "2000'Q1"
            
            if (!quarter || quarter.length < 3) continue;
            
            const { year, quarter: quarterNum } = parseQuarter(quarter);
            
            // Skip if not in configured year range
            if (year < CONFIG.startYear || year > CONFIG.endYear) continue;
            
            // Create data object for this year
            if (!revenueData[year]) {
                revenueData[year] = [];
            }
            
            // Parse revenue for each airline
            for (let j = 1; j < values.length && j <= airlineNames.length; j++) {
                const airline = airlineNames[j - 1];
                const revenueStr = values[j];
                
                // Skip empty values
                if (!revenueStr || revenueStr.trim() === '') continue;
                
                // Convert revenue string to number (remove " M" suffix and parse as float)
                let revenue = parseFloat(revenueStr.replace(' M', ''));
                
                // Skip invalid revenue
                if (isNaN(revenue) || revenue <= 0) continue;
                
                // Create airline data object
                const airlineData = {
                    airline: airline,
                    iataCode: iataCodes[airline] || '',
                    revenue: revenue,
                    region: regions[airline] || '',
                    country: countries[airline] || '',
                    status: statuses[airline] || '',
                    quarter: quarterNum,
                    color: regionColors[regions[airline]] || '#999999' // Add color based on region
                };
                
                // Add to this year's data
                revenueData[year].push(airlineData);
            }
            
            // Only keep data for Q4 of each year
            if (quarterNum === 4) {
                // Sort by revenue
                revenueData[year].sort((a, b) => b.revenue - a.revenue);
                
                // Limit number of airlines
                revenueData[year] = revenueData[year].slice(0, CONFIG.maxAirlines);
                
                // Store in localStorage
                localStorage.setItem(`airlineData_${year}`, JSON.stringify(revenueData[year]));
            }
        }
        
        console.log('Airline data processed successfully');
        console.log(`Years with data: ${Object.keys(revenueData).join(', ')}`);
        
        return true;
    } catch (error) {
        console.error('Error processing CSV data:', error);
        throw error;
    }
}

// Initialize the user interface
function initializeUI() {
    // Create visualization SVG
    const vizContainer = document.getElementById('chart-container');
    if (!document.getElementById('visualization')) {
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.id = 'visualization';
        svg.classList.add('visualization');
        svg.setAttribute('width', '100%');
        svg.setAttribute('height', '100%');
        vizContainer.appendChild(svg);
    }
    
    // Set up event listeners for controls
    setupEventListeners();
}

// Setup event listeners for the UI controls
function setupEventListeners() {
    const yearSlider = document.getElementById('year-slider');
    const yearDisplay = document.getElementById('year-display');
    const prevButton = document.getElementById('prev-year');
    const nextButton = document.getElementById('next-year');
    const playButton = document.getElementById('play-pause');
    
    if (yearSlider) {
        yearSlider.min = CONFIG.startYear;
        yearSlider.max = CONFIG.endYear;
        yearSlider.value = CONFIG.startYear;
        
        yearSlider.addEventListener('input', () => {
            const year = parseInt(yearSlider.value);
            if (yearDisplay) {
                yearDisplay.textContent = year;
            }
            // Update visualization for the selected year
            const viz = new AirlineVisualization({
                containerId: 'chart-container',
                config: CONFIG
            });
            viz.updateYear(year);
        });
    }
    
    if (prevButton) {
        prevButton.addEventListener('click', () => {
            if (yearSlider) {
                const currentYear = parseInt(yearSlider.value);
                if (currentYear > CONFIG.startYear) {
                    yearSlider.value = currentYear - 1;
                    yearSlider.dispatchEvent(new Event('input'));
                }
            }
        });
    }
    
    if (nextButton) {
        nextButton.addEventListener('click', () => {
            if (yearSlider) {
                const currentYear = parseInt(yearSlider.value);
                if (currentYear < CONFIG.endYear) {
                    yearSlider.value = currentYear + 1;
                    yearSlider.dispatchEvent(new Event('input'));
                }
            }
        });
    }
    
    let isPlaying = false;
    let animationInterval;
    
    if (playButton) {
        playButton.addEventListener('click', () => {
            if (isPlaying) {
                clearInterval(animationInterval);
                playButton.textContent = '▶';
            } else {
                playButton.textContent = '⏸';
                animationInterval = setInterval(() => {
                    if (yearSlider) {
                        const currentYear = parseInt(yearSlider.value);
                        if (currentYear < CONFIG.endYear) {
                            yearSlider.value = currentYear + 1;
                            yearSlider.dispatchEvent(new Event('input'));
                        } else {
                            clearInterval(animationInterval);
                            playButton.textContent = '▶';
                            isPlaying = false;
                        }
                    }
                }, 1000); // Change frame every second
            }
            isPlaying = !isPlaying;
        });
    }
}

// Display error message to the user
function displayErrorMessage(message) {
    const errorContainer = document.getElementById('error-container');
    if (errorContainer) {
        errorContainer.textContent = message;
        errorContainer.style.display = 'block';
    } else {
        console.error(message);
    }
} 