const appConfig = {
    // Region colors based on representative flags
    regionColors: {
        'APAC': '#DE2910',        // China's flag red
        'Europe': '#003399',      // EU flag blue
        'Eastern Europe': '#1B4B9E', // Darker blue
        'LATAM': '#009B3A',       // Brazil's flag green
        'Middle East': '#8B4513',  // 改为棕色
        'North America': '#002868' // US flag blue
    },

    // Animation settings
    animation: {
        duration: 1000,           // Duration of each animation frame in ms
        frameDelay: 2000,         // Delay between frames in ms
    },

    // Chart settings
    chart: {
        minBubbleSize: 10,
        maxBubbleSize: 100,
        defaultYear: 2005,        // Starting year
        xAxisTitle: 'Online Penetration (%)',
        yAxisTitle: 'Online Bookings (USD)',
        sizeMetric: 'Gross Bookings'
    },

    // Data processing
    dataProcessing: {
        onlinePenetrationMultiplier: 100,  // Convert decimal to percentage
        bookingsScaleFactor: 1e-9,         // Convert to billions
        roundDecimals: 2
    }
}; 