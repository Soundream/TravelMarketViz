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

// 在文件开头添加一个变量来跟踪历史最大值
let historicalMaxValue = 0;

function createRaceChart(data, year) {
    console.log("Creating race chart for year:", year);
    console.log("Raw data received:", data);

    // 数据验证
    if (!data || !Array.isArray(data)) {
        console.error("Invalid data received:", data);
        return;
    }

    // 计算所有年份的最大值
    const allYearsData = data.map(d => d['Gross Bookings'] * appConfig.dataProcessing.bookingsScaleFactor);
    const maxValueAllYears = Math.max(...allYearsData);
    
    // 更新历史最大值
    historicalMaxValue = Math.max(historicalMaxValue, maxValueAllYears);
    console.log("Historical max value:", historicalMaxValue);

    // 验证年份数据
    const yearData = data.filter(d => d.Year === year);
    console.log(`Data for year ${year}:`, yearData);

    if (yearData.length === 0) {
        console.error(`No data found for year ${year}`);
        return;
    }

    // 获取APAC国家数据
    const excludedCountries = ['Macau', 'Taiwan', 'Hong Kong'];
    const apacCountriesData = window.processedCountriesData ? 
        window.processedCountriesData.filter(d => {
            const matches = d.Year === year && !excludedCountries.includes(d.Market);
            if (matches) {
                console.log(`APAC country data for ${d.Market}:`, d);
            }
            return matches;
        }) : [];

    console.log("APAC countries data:", apacCountriesData);

    // 组合区域和国家数据
    let combinedData = [...yearData];

    // 添加Asia-Pacific (sum)数据
    const apacSumExists = combinedData.some(d => d.Region === 'Asia-Pacific (sum)');
    
    if (!apacSumExists && apacCountriesData.length > 0) {
        const apacSum = {
            Region: 'Asia-Pacific (sum)',
            Year: year,
            'Gross Bookings': apacCountriesData.reduce((sum, c) => sum + c.GrossBookings, 0),
            'Online Bookings': apacCountriesData.reduce((sum, c) => sum + c.OnlineBookings, 0)
        };
        
        // 计算在线渗透率
        apacSum['Online Penetration'] = apacSum['Online Bookings'] / apacSum['Gross Bookings'];
        
        console.log("Calculated Asia-Pacific (sum):", apacSum);
        combinedData.push(apacSum);
    }

    // 添加APAC国家数据
    apacCountriesData.forEach(country => {
        const countryData = {
            Region: country.Market,
            'Gross Bookings': country.GrossBookings,
            'Online Bookings': country.OnlineBookings,
            'Online Penetration': country.OnlinePenetration,
            Year: country.Year
        };
        console.log(`Adding country data for ${country.Market}:`, countryData);
        combinedData.push(countryData);
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

    requiredRegions.forEach(region => {
        const exists = combinedData.some(d => d.Region === region);
        if (!exists && region !== 'Asia-Pacific (sum)') {
            console.warn(`Adding placeholder for missing region: ${region}`);
            combinedData.push({
                Region: region,
                Year: year,
                'Gross Bookings': 0.1,
                'Online Bookings': 0.1,
                'Online Penetration': 0.1
            });
        }
    });

    // 处理数据前先打印
    console.log("Combined data before processing:", combinedData);

    // 处理数据
    const processedData = combinedData.map(d => {
        const regionName = d.Region;
        const isApacCountry = apacCountriesData.some(c => c.Market === regionName);
        const displayName = isApacCountry ? getCountryCode(regionName) : regionName;
        
        // 确保数值是有效的
        const grossBookings = parseFloat(d['Gross Bookings']) || 0;
        const value = grossBookings * appConfig.dataProcessing.bookingsScaleFactor;
        
        console.log(`Processing ${regionName}:`, {
            originalValue: d['Gross Bookings'],
            processedValue: value,
            scaleFactor: appConfig.dataProcessing.bookingsScaleFactor
        });

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

        return {
            region: regionName,
            displayName: displayName,
            value: value,
            originalValue: grossBookings,
            color: color,
            isApacCountry: isApacCountry
        };
    });

    // 按值排序并取前15名
    const sortedData = processedData
        .filter(d => d.value > 0.1)
        .sort((a, b) => a.value - b.value);

    console.log("Sorted data before top 15 selection:", sortedData.map(d => ({
        region: d.region,
        value: d.value,
        originalValue: d.originalValue
    })));

    const top15Data = sortedData.slice(-15);

    console.log("Final top 15 data:", top15Data.map(d => ({
        region: d.region,
        value: d.value,
        originalValue: d.originalValue
    })));

    // 填充图表数据
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

    barData.y = top15Data.map(d => d.displayName);
    barData.x = top15Data.map(d => d.value);
    barData.marker.color = top15Data.map(d => d.color);
    barData.text = top15Data.map(d => d.value);

    // 获取当前最大值（第一名的值）
    const currentTopValue = top15Data[top15Data.length - 1].value;
    console.log("Current top value:", currentTopValue);
    console.log("Historical max value:", historicalMaxValue);
    
    // 使用历史最大值和当前最大值中的较大值
    const xAxisMax = Math.max(currentTopValue, historicalMaxValue);
    console.log("Using x-axis max:", xAxisMax);

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
            range: [0, xAxisMax * 1.2], // 使用计算出的最大值
            fixedrange: false, // 允许动态更新
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
    if (typeof historicalMaxValue === 'undefined') {
        createRaceChart(data, year);
        return;
    }

    // 取消之前的动画
    if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
    }

    // 获取当前年份的数据并处理
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
    const mainRegions = [
        'Europe', 
        'Eastern Europe', 
        'Latin America', 
        'Middle East', 
        'North America',
        'Asia-Pacific (sum)'
    ];

    mainRegions.forEach(region => {
        if (!combinedData.some(d => d.Region === region) && region !== 'Asia-Pacific (sum)') {
            combinedData.push({
                Region: region,
                Year: year,
                'Gross Bookings': 0.1,
                'Online Bookings': 0.1,
                'Online Penetration': 0.1
            });
        }
    });

    // 处理数据并分离regions和countries
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
            color: color,
            isRegion: mainRegions.includes(regionName)
        };
    });

    // 分别排序regions和countries
    const regions = processedData
        .filter(d => d.isRegion && d.value > 0.1)
        .sort((a, b) => b.value - a.value);

    const countries = processedData
        .filter(d => !d.isRegion && d.value > 0.1)
        .sort((a, b) => b.value - a.value);

    // 合并数据，保持regions在上，countries在下，然后反转顺序
    // 因为Plotly条形图是从下往上绘制的，所以需要反转来保持正确的显示顺序
    const targetData = [...regions, ...countries].reverse();

    // 获取当前最大值
    const currentTopValue = Math.max(...targetData.map(d => d.value));
    historicalMaxValue = Math.max(historicalMaxValue, currentTopValue);
    const xAxisMax = historicalMaxValue;

    // 打印排序后的数据用于调试
    console.error(`${year}年排序后的数据:`, targetData.map(d => ({
        region: d.region,
        displayName: d.displayName,
        value: d.value.toFixed(1),
        isRegion: d.isRegion
    })));

    // 创建图表数据
    const trace = {
        type: 'bar',
        orientation: 'h',
        x: targetData.map(d => d.value),
        y: targetData.map(d => d.displayName),
        text: targetData.map(d => d.value.toFixed(1)),
        textposition: 'outside',
        marker: {
            color: targetData.map(d => d.color),
            width: 0.1
        },
        hoverinfo: 'text',
        texttemplate: '%{text:$.1f}B',
        textfont: { family: 'Monda', size: 14 }
    };

    const layout = {
        xaxis: {
            range: [0, xAxisMax * 1.2],
            title: {
                text: 'Gross Bookings (USD bn)',
                font: { family: 'Monda', size: 16 }
            },
            fixedrange: false,
            showgrid: true,
            gridcolor: '#eee',
            gridwidth: 1,
            zeroline: true,
            zerolinecolor: '#eee',
            tickfont: { family: 'Monda', size: 14 },
            ticks: 'outside',
            ticklen: 8,
            tickwidth: 1,
            tickcolor: '#ccc'
        },
        yaxis: {
            autorange: false,
            fixedrange: true,
            showgrid: false,
            tickfont: { family: 'Monda', size: 14 },
            ticktext: targetData.map(d => d.displayName),
            tickvals: targetData.map((_, i) => i),
            tickmode: 'array',
            range: [-1, targetData.length]
        },
        margin: { l: 120, r: 60, t: 30, b: 50 },
        height: 650,
        width: 400,
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        showlegend: false,
        bargap: 0.08,
        font: { family: 'Monda' }
    };

    const config = {
        displayModeBar: false,
        responsive: false
    };

    // 使用 Plotly.animate 进行更新
    if (!window.raceChartData) {
        // 首次初始化
        Plotly.newPlot('race-chart', [trace], layout, config);
    } else {
        // 后续更新使用 animate
        const animateConfig = {
            data: [{
                x: targetData.map(d => d.value),
                y: targetData.map(d => d.displayName),
                text: targetData.map(d => d.value.toFixed(1)),
                marker: {
                    color: targetData.map(d => d.color),
                    width: 0.1
                }
            }],
            layout: {
                xaxis: {
                    range: [0, xAxisMax * 1.2]
                },
                yaxis: {
                    ticktext: targetData.map(d => d.displayName),
                    tickvals: targetData.map((_, i) => i),
                    tickmode: 'array',
                    range: [-1, targetData.length]
                }
            },
            traces: [0]
        };

        const transitionConfig = {
            transition: {
                duration: appConfig.animation.duration,
                easing: 'linear'
            },
            frame: {
                duration: appConfig.animation.duration,
                redraw: false
            }
        };
        
        Plotly.animate('race-chart', animateConfig, transitionConfig);
    }

    // 更新存储的数据
    window.raceChartData = targetData;
}