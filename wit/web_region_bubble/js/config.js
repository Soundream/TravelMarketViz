const appConfig = {
    // Region colors based on representative flags
    regionColors: {
        'Asia-Pacific': '#FF4B4B',        // 明亮的红色
        'Europe': '#4169E1',              // 皇家蓝
        'Eastern Europe': '#9370DB',      // 中等紫色
        'Latin America': '#32CD32',       // 鲜艳的绿色
        'Middle East': '#DEB887',         // 暖棕色
        'North America': '#40E0D0'        // 绿松石色
    },

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