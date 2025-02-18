const appConfig = {
    // Region colors based on representative flags
    regionColors: {
        'Asia-Pacific': '#DE2910',        // China's flag red
        'Europe': '#003399',      // 深蓝色
        'Eastern Europe': '#4B0082', // 靛蓝色
        'Latin America': '#009B3A',       // Brazil's flag green
        'Middle East': '#8B4513',  // 棕色
        'North America': '#00BCD4' // 浅蓝色
    },

    // Animation settings
    animation: {
        duration: 800,            // 减少每个动画的持续时间
        frameDelay: 1200,         // 减少帧之间的延迟
    },

    // Chart settings
    chart: {
        minBubbleSize: 10,
        maxBubbleSize: 100,
        defaultYear: 2005,        // Starting year
        xAxisTitle: 'Share of Online Bookings (%)',
        yAxisTitle: 'Online Bookings (USD bn)',
        sizeMetric: 'Gross Bookings'
    },

    // Data processing
    dataProcessing: {
        onlinePenetrationMultiplier: 100,  // Convert decimal to percentage
        bookingsScaleFactor: 1e-9,         // Convert to billions
        roundDecimals: 2
    }
}; 