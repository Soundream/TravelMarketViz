// Configuration for Airline Revenue Visualization

const CONFIG = {
    // Data source
    dataPath: '../data/',
    csvDataPath: '../data/airlines_final.csv',
    
    // Time configuration
    startYear: 2000,
    endYear: 2023,
    
    // Animation
    animationDuration: 800,  // milliseconds
    playSpeed: 1000,         // milliseconds between frames when playing
    
    // Visualization settings
    maxAirlines: 15,         // Maximum number of airlines to show
    barColors: [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    ],
    defaultColor: '#7f7f7f',  // Default color for undefined regions
    
    // Chart dimensions
    width: 900,              // Total width of the SVG
    height: 600,             // Total height of the SVG
    margin: {
        top: 50,
        right: 50,
        bottom: 70,
        left: 120
    },
    
    // Axes labels
    xAxisLabel: 'Revenue (Million USD)',
    yAxisLabel: 'Airlines',
};

// Export the configuration
if (typeof module !== 'undefined') {
    module.exports = CONFIG;
} 