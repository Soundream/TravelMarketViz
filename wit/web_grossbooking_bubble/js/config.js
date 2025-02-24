const appConfig = {
    // 大洲颜色
    regionColors: {
        'Asia-Pacific': '#DE2910',  // 中国红
        'Europe': '#003399',        // 欧盟蓝
        'Eastern Europe': '#4B0082', // 深紫色
        'Latin America': '#009B3A',  // 巴西绿
        'Middle East': '#8B4513',    // 棕色
        'North America': '#00BCD4'   // 青色
    },

    // 国家颜色字典（基于所属大洲）
    colorDict: {
        // 北美洲
        'U.S.': '#00BCD4',
        'Canada': '#00BCD4',
        'Mexico': '#00BCD4',
        
        // 拉丁美洲
        'Brazil': '#009B3A',
        'Argentina': '#009B3A',
        'Colombia': '#009B3A',
        'Chile': '#009B3A',
        
        // 欧洲
        'U.K.': '#003399',
        'France': '#003399',
        'Germany': '#003399',
        'Italy': '#003399',
        'Spain': '#003399',
        'Netherlands': '#003399',
        'Switzerland': '#003399',
        
        // 东欧
        'Russia': '#4B0082',
        
        // 亚太地区
        'China': '#DE2910',
        'Japan': '#DE2910',
        'South Korea': '#DE2910',
        'India': '#DE2910',
        'Australia': '#DE2910',
        'Singapore': '#DE2910',
        'Indonesia': '#DE2910',
        'Malaysia': '#DE2910',
        'Thailand': '#DE2910',
        'Taiwan': '#DE2910',
        'Hong Kong': '#DE2910'
    },

    // 动画设置
    animation: {
        duration: 800,
        frameDelay: 1200,
    },

    // 数据处理
    dataProcessing: {
        bookingsScaleFactor: 1e-9, // 转换为十亿
        roundDecimals: 2
    }
}; 