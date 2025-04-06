// 定义国家代码映射
const countryCodeMapping = {
    "Singapore": "SG",
    "China": "CN",
    "India": "IN",
    "Indonesia": "ID",
    "Malaysia": "MY",
    "Thailand": "TH",
    "Vietnam": "VN",
    "Philippines": "PH",
    "Japan": "JP",
    "South Korea": "KR",
    "Hong Kong": "HK",
    "Taiwan": "TW",
    "Macau": "MO",
    "Australia & New Zealand": "AU/NZ"
};

// 获取国家代码的辅助函数
function getCountryCode(countryName) {
    return countryCodeMapping[countryName] || countryName;
}

function createRaceChart(data, year) {
    console.log("Creating race chart for year:", year);
    // 计算所有年份的最大值，用于固定坐标轴范围
    const allYearsData = [];
    // 先收集所有区域数据
    data.forEach(d => {
        allYearsData.push({
            value: d['Gross Bookings'] * appConfig.dataProcessing.bookingsScaleFactor
        });
    });
    
    // 收集所有国家数据
    if (window.processedCountriesData) {
        window.processedCountriesData.forEach(c => {
            allYearsData.push({
                value: c.GrossBookings * appConfig.dataProcessing.bookingsScaleFactor
            });
        });
    }
    
    // 计算全局最大值
    const maxValue = Math.max(...allYearsData.map(d => d.value));
    
    // 将最大值保存到window对象，确保所有图表使用相同的范围
    window.globalMaxValue = maxValue;
    
    // 按区域分组并计算总预订量
    const yearData = data.filter(d => d.Year === year);
    
    // 获取APAC国家数据 - 排除Macau, Taiwan, Hong Kong
    const excludedCountries = ['Macau', 'Taiwan', 'Hong Kong'];
    const apacCountriesData = window.processedCountriesData ? 
        window.processedCountriesData.filter(d => 
            d.Year === year && !excludedCountries.includes(d.Market)) : [];
    
    // 组合区域和国家数据
    let combinedData = [...yearData];
    
    // 添加Asia-Pacific (sum)数据，确保它存在
    const apacSumExists = combinedData.some(d => d.Region === 'Asia-Pacific (sum)');
    
    if (!apacSumExists && apacCountriesData.length > 0) {
        // 计算Asia-Pacific (sum)的总数据
        const apacSum = {
            Region: 'Asia-Pacific (sum)',
            Year: year,
            'Gross Bookings': apacCountriesData.reduce((sum, c) => sum + c.GrossBookings, 0),
            'Online Bookings': apacCountriesData.reduce((sum, c) => sum + c.OnlineBookings, 0),
            'Online Penetration': 0 // 稍后计算
        };
        
        // 计算在线渗透率
        apacSum['Online Penetration'] = apacSum['Online Bookings'] / apacSum['Gross Bookings'];
        
        // 添加到数据中
        combinedData.push(apacSum);
    }
    
    // 添加APAC国家数据
    apacCountriesData.forEach(country => {
        combinedData.push({
            Region: country.Market,
            'Gross Bookings': country.GrossBookings,
            'Online Bookings': country.OnlineBookings,
            'Online Penetration': country.OnlinePenetration,
            Year: country.Year
        });
    });
    
    // 确保所有主要区域都有数据
    const requiredRegions = [
        'Europe', 
        'Eastern Europe', 
        'Latin America', 
        'Middle East', 
        'North America',
        'Asia-Pacific (sum)'
    ];
    
    // 检查每个必须的区域是否存在，如果不存在则添加默认值
    requiredRegions.forEach(region => {
        const exists = combinedData.some(d => d.Region === region);
        if (!exists && region !== 'Asia-Pacific (sum)') {
            // 如果是必要的区域但在数据中不存在，添加一个占位符
            combinedData.push({
                Region: region,
                Year: year,
                'Gross Bookings': 0.1, // 小值但不为0，以便显示
                'Online Bookings': 0.1,
                'Online Penetration': 0.1
            });
        }
    });
    
    // 创建条形图数据
    const barData = {
        type: 'bar',
        x: [],
        y: [],
        orientation: 'h',
        marker: {
            color: [],
            width: 0.6
        },
        text: [],
        textposition: 'outside',
        hoverinfo: 'text',
        texttemplate: '%{text:$.1f}B',
        textfont: {
            family: 'Monda',
            size: 14
        },
        cliponaxis: false
    };

    // 处理数据
    const processedData = combinedData.map(d => {
        let color;
        const regionName = d.Region;
        const isApacCountry = apacCountriesData.some(c => c.Market === regionName);
        // 为APAC国家使用国家代码而不是全名
        const displayName = isApacCountry ? getCountryCode(regionName) : regionName;
        
        // 确定颜色：APAC国家和APAC总和使用红色，其他区域使用其原有颜色
        if (regionName === 'Asia-Pacific (sum)' || 
            (apacCountriesData.some(c => c.Market === regionName))) {
            color = '#FF4B4B'; // 使用硬编码的红色，不依赖config
        } else if (regionName === 'Europe') {
            color = '#4169E1'; // 确保Europe总是蓝色
        } else if (regionName === 'Eastern Europe') {
            color = '#9370DB'; // 紫色
        } else if (regionName === 'Latin America') {
            color = '#32CD32'; // 绿色
        } else if (regionName === 'Middle East') {
            color = '#DEB887'; // 棕色
        } else if (regionName === 'North America') {
            color = '#40E0D0'; // 绿松石色
        } else {
            // 如果找不到预定义的颜色，使用默认颜色
            color = '#888888';
        }
        
        // 确保值是有效的数字，避免出现NaN或undefined
        const grossBookings = d['Gross Bookings'] || 0;
        const value = grossBookings * appConfig.dataProcessing.bookingsScaleFactor;
        
        return {
            region: regionName,
            displayName: displayName,
            value: isNaN(value) ? 0 : value, // 确保值是有效的数字
            color: color,
            isApacCountry: isApacCountry
        };
    });
    
    // 按照值从小到大排序
    const sortedData = processedData.sort((a, b) => a.value - b.value);
    
    // 只取前15名
    const top15Data = sortedData.slice(-15);

    // 填充图表数据
    barData.y = top15Data.map(d => d.displayName);
    barData.x = top15Data.map(d => d.value);
    barData.marker.color = top15Data.map(d => d.color);
    barData.text = top15Data.map(d => d.value);

    // 创建布局
    const layout = {
        title: {
            text: '',
            font: {
                family: 'Monda',
                size: 16
            },
            y: 0.95
        },
        xaxis: {
            title: {
                text: 'Gross Bookings (USD bn)',
                font: {
                    family: 'Monda',
                    size: 16
                },
                standoff: 15
            },
            showgrid: true,
            gridcolor: '#eee',
            gridwidth: 1,
            zeroline: true,
            zerolinecolor: '#eee',
            tickfont: {
                family: 'Monda',
                size: 14
            },
            range: [0, window.globalMaxValue * 1.2], // 使用全局最大值，确保所有年份使用相同的范围
            fixedrange: true,
            ticks: 'outside',
            ticklen: 8,
            tickwidth: 1,
            tickcolor: '#ccc'
        },
        yaxis: {
            showgrid: false,
            tickfont: {
                family: 'Monda',
                size: 14
            },
            fixedrange: true,
            automargin: true
        },
        margin: {
            l: 120,
            r: 60,
            t: 10,
            b: 50
        },
        height: 550,
        width: 400, // 固定宽度，避免波动
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        showlegend: false,
        barmode: 'group',
        bargap: 0.15,
        font: {
            family: 'Monda'
        }
    };

    // 创建配置
    const config = {
        displayModeBar: false,
        responsive: false, // 固定大小，避免自动响应式调整
        staticPlot: false
    };

    // 初始化全局动画配置
    if (!window.raceChartConfig) {
        window.raceChartConfig = {
            animationDuration: 30000, // 默认30秒总时长
            transitionDuration: 700 // 帧之间的过渡时间
        };
    }
    console.log("Race chart animation duration:", window.raceChartConfig.animationDuration);
    
    // 渲染图表
    Plotly.newPlot('race-chart', [barData], layout, config);
    
    // 存储当前数据以便进行平滑过渡
    window.raceChartData = top15Data;
    window.previousSortedData = top15Data.map(d => ({...d}));
}

// 添加线性插值函数
function lerp(start, end, t) {
    return start * (1 - t) + end * t;
}

// 添加动画状态变量
let animationFrameId = null;
let animationStartTime = null;
let animationDuration = 800; // 动画持续时间（毫秒）

function updateRaceChart(data, year, forceUpdate = false) {
    // 如果没有设置全局最大值，重新绘制整个图表
    if (window.globalMaxValue === undefined) {
        createRaceChart(data, year);
        return;
    }

    // 取消之前的动画
    if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
    }

    // 获取当前年份的数据
    const yearData = data.filter(d => d.Year === year);
    const excludedCountries = ['Macau', 'Taiwan', 'Hong Kong'];
    const apacCountriesData = window.processedCountriesData ? 
        window.processedCountriesData.filter(d => 
            d.Year === year && !excludedCountries.includes(d.Market)) : [];

    // 组合并处理数据
    let combinedData = [...yearData];

    // 添加 Asia-Pacific (sum) 数据
    const apacSumExists = combinedData.some(d => d.Region === 'Asia-Pacific (sum)');
    if (!apacSumExists && apacCountriesData.length > 0) {
        const apacSum = {
            Region: 'Asia-Pacific (sum)',
            Year: year,
            'Gross Bookings': apacCountriesData.reduce((sum, c) => sum + c.GrossBookings, 0),
            'Online Bookings': apacCountriesData.reduce((sum, c) => sum + c.OnlineBookings, 0),
            'Online Penetration': 0
        };
        apacSum['Online Penetration'] = apacSum['Online Bookings'] / apacSum['Gross Bookings'];
        combinedData.push(apacSum);
    }

    // 添加 APAC 国家数据
    apacCountriesData.forEach(country => {
        combinedData.push({
            Region: country.Market,
            'Gross Bookings': country.GrossBookings,
            'Online Bookings': country.OnlineBookings,
            'Online Penetration': country.OnlinePenetration,
            Year: year
        });
    });

    // 确保所有必要区域都存在
    const requiredRegions = [
        'Europe', 
        'Eastern Europe', 
        'Latin America', 
        'Middle East', 
        'North America',
        'Asia-Pacific (sum)'
    ];

    requiredRegions.forEach(region => {
        const exists = combinedData.some(d => d.Region === region);
        if (!exists && region !== 'Asia-Pacific (sum)') {
            combinedData.push({
                Region: region,
                Year: year,
                'Gross Bookings': 0.1,
                'Online Bookings': 0.1,
                'Online Penetration': 0.1
            });
        }
    });

    // 处理数据
    const processedData = combinedData.map(d => {
        const regionName = d.Region;
        const isApacCountry = apacCountriesData.some(c => c.Market === regionName);
        const displayName = isApacCountry ? getCountryCode(regionName) : regionName;

        let color;
        if (regionName === 'Asia-Pacific (sum)' || isApacCountry) {
            color = '#FF4B4B';
        } else if (regionName === 'Europe') {
            color = '#4169E1';
        } else if (regionName === 'Eastern Europe') {
            color = '#9370DB';
        } else if (regionName === 'Latin America') {
            color = '#32CD32';
        } else if (regionName === 'Middle East') {
            color = '#DEB887';
        } else if (regionName === 'North America') {
            color = '#40E0D0';
        } else {
            color = '#888888';
        }

        const grossBookings = d['Gross Bookings'] || 0;
        const value = grossBookings * appConfig.dataProcessing.bookingsScaleFactor;

        return {
            region: regionName,
            displayName: displayName,
            value: isNaN(value) ? 0 : value,
            color: color
        };
    });

    // 按值排序并取前15名
    const targetData = processedData
        .filter(d => d.value > 0.1)
        .sort((a, b) => a.value - b.value)
        .slice(-15);

    // 获取当前显示的数据
    const currentData = window.raceChartData || targetData;

    // 如果是强制更新或者第一次更新，直接设置数据
    if (forceUpdate || !window.raceChartData) {
        Plotly.animate('race-chart', {
            data: [{
                y: targetData.map(d => d.displayName),
                x: targetData.map(d => d.value),
                marker: { color: targetData.map(d => d.color) },
                text: targetData.map(d => d.value.toFixed(1))
            }]
        }, {
            transition: { duration: 0 },
            frame: { duration: 0 }
        });
        window.raceChartData = targetData;
        return;
    }

    // 开始动画
    animationStartTime = performance.now();

    function animate(currentTime) {
        if (!animationStartTime) animationStartTime = currentTime;
        const progress = Math.min(1, (currentTime - animationStartTime) / animationDuration);

        // 创建当前帧的数据
        const frameData = targetData.map((target, i) => {
            const current = currentData.find(c => c.displayName === target.displayName) || 
                          { value: 0, color: target.color };
            
            return {
                displayName: target.displayName,
                value: lerp(current.value, target.value, progress),
                color: target.color
            };
        });

        // 排序并更新图表
        const sortedFrameData = frameData.sort((a, b) => a.value - b.value);

        Plotly.animate('race-chart', {
            data: [{
                y: sortedFrameData.map(d => d.displayName),
                x: sortedFrameData.map(d => d.value),
                marker: { color: sortedFrameData.map(d => d.color) },
                text: sortedFrameData.map(d => d.value.toFixed(1))
            }]
        }, {
            transition: { duration: 0,easing: 'linear' },
            frame: { duration: 0 }
        });

        if (progress < 1) {
            animationFrameId = requestAnimationFrame(animate);
        } else {
            window.raceChartData = targetData;
            animationFrameId = null;
            animationStartTime = null;
        }
    }

    animationFrameId = requestAnimationFrame(animate);
} 