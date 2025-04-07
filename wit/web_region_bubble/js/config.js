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
        "Singapore":              "logos/Singapore%20Flag%20Icon.png",
        "China":                  "logos/China%20Flag%20Icon.png",
        "India":                  "logos/India%20Icon.png",
        "Indonesia":              "logos/Indonesia%20Flag.png",
        "Malaysia":               "logos/Malaysia%20Icon.png",
        "Thailand":               "logos/Thailand%20Icon.png",
        "Vietnam":                "logos/Vietnam%20Icon.png",
        "Philippines":            "logos/Philippines%20Icon.png",
        "Japan":                  "logos/Japan%20Icon.png",
        "South Korea":            "logos/Korea%20Icon.png",
        "Hong Kong":              "logos/Hong%20Kong%20Icon.png",
        "Taiwan":                 "logos/Taiwan%20Icon.png",
        "Macau":                  "logos/Macau%20Icon.png",
        "Australia & New Zealand":"logos/Australia%20Icon.png"
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
        frameDelay: 5000,    // 增加帧之间的延迟，确保完整的两步动画有足够时间完成
        duration: 1800,      // 每一步动画的持续时间
        transitionDuration: 1800  // 保持一致的持续时间
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