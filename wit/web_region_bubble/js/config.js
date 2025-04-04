const appConfig = {
    // Region colors with vibrant values
    regionColors: {
        // 'Asia-Pacific': '#FF4B4B',        // Removed Asia-Pacific
        'Europe': '#4169E1',              // 鲜艳的蓝色
        'Eastern Europe': '#9370DB',      // 鲜艳的紫色
        'Latin America': '#32CD32',       // 鲜艳的绿色
        'Middle East': '#DEB887',         // 鲜艳的棕色
        'North America': '#40E0D0'        // 鲜艳的绿松石色
    },

    // Country colors
    countryColors: {
        'Singapore': '#ff5895',
        'China': '#003480',
        'India': '#ff9933',
        'Indonesia': '#ff0000',
        'Malaysia': '#cc0001',
        'Thailand': '#00247d',
        'Vietnam': '#da251d',
        'Philippines': '#0038a8',
        'Japan': '#bc002d',
        'South Korea': '#cd2e3a',
        'Hong Kong': '#de2910',
        'Taiwan': '#fe0000',
        'Macau': '#00785e',
        'Australia & New Zealand': '#00008b'
    },

    // Country logos for bubbles
    countryLogos: {
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
    },

    // Default countries to display
    defaultSelectedCountries: [
        'China',
        'Japan',
        'South Korea',
        'Australia & New Zealand',
        'India',
        'Indonesia',
        'Singapore',
        'Malaysia',
        'Thailand',
        'Vietnam',
        'Philippines',
        'Hong Kong',
        'Taiwan',
        'Macau'
    ],

    // Animation settings
    animation: {
        duration: 800,            
        frameDelay: 1200,         
    },

    // Chart settings
    chart: {
        minBubbleSize: 15,        // 增加最小气泡大小
        maxBubbleSize: 80,        // 减小最大气泡大小
        defaultYear: 2005,        
        xAxisTitle: 'Share of Online Bookings (%)',
        yAxisTitle: 'Online Bookings (USD bn)',
        sizeMetric: 'Gross Bookings'
    },

    // Data processing
    dataProcessing: {
        onlinePenetrationMultiplier: 100,  
        bookingsScaleFactor: 1e-9,         
        roundDecimals: 2
    }
}; 