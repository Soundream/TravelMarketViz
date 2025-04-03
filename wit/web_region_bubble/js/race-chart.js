function createRaceChart(data, year) {
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
    
    // 获取APAC国家数据
    const apacCountriesData = window.processedCountriesData ? 
        window.processedCountriesData.filter(d => d.Year === year) : [];
    
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
            value: isNaN(value) ? 0 : value, // 确保值是有效的数字
            color: color
        };
    });
    
    // 按照值从小到大排序
    const sortedData = processedData.sort((a, b) => a.value - b.value);
    
    // 只取前15名
    const top15Data = sortedData.slice(-15);

    // 填充图表数据
    barData.y = top15Data.map(d => d.region);
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

    // 渲染图表
    Plotly.newPlot('race-chart', [barData], layout, config);
    
    // 存储当前数据以便进行平滑过渡
    window.raceChartData = top15Data;
}

// 更新race chart的函数
function updateRaceChart(data, year, progress, nextIndex) {
    // 如果没有设置全局最大值，重新绘制整个图表
    if (window.globalMaxValue === undefined) {
        createRaceChart(data, year);
        return;
    }

    // 按区域分组并计算总预订量
    const yearData = data.filter(d => d.Year === year);
    
    // 如果传入了progress和nextIndex参数，说明是在动画中
    const isAnimating = progress !== undefined && nextIndex !== undefined;
    
    // 获取APAC国家数据
    const apacCountriesData = window.processedCountriesData ? 
        window.processedCountriesData.filter(d => d.Year === year) : [];
    
    // 如果是动画状态，获取下一年的数据以进行插值
    let nextYearApacData = [];
    let nextYearRegionData = [];
    if (isAnimating) {
        const nextYear = window.years[nextIndex];
        nextYearApacData = window.processedCountriesData ? 
            window.processedCountriesData.filter(d => d.Year === nextYear) : [];
        nextYearRegionData = data.filter(d => d.Year === nextYear);
    }
    
    // 组合区域和国家数据
    let combinedData = [...yearData];
    
    // 确保必要区域总是存在
    const requiredRegions = [
        'Europe', 
        'Eastern Europe', 
        'Latin America', 
        'Middle East', 
        'North America',
        'Asia-Pacific (sum)'
    ];
    
    // 检查并添加必要的区域（在最开始添加，确保它们一定会被处理）
    requiredRegions.forEach(region => {
        const exists = combinedData.some(d => d.Region === region);
        if (!exists && region !== 'Asia-Pacific (sum)') {
            // 添加必要区域的占位符
            combinedData.push({
                Region: region,
                Year: year,
                'Gross Bookings': 0.5, // 确保不会消失
                'Online Bookings': 0.5,
                'Online Penetration': 0.5
            });
        }
    });
    
    // 添加Asia-Pacific (sum)数据，确保它存在
    const apacSumExists = combinedData.some(d => d.Region === 'Asia-Pacific (sum)');
    if (!apacSumExists && apacCountriesData.length > 0) {
        // 计算Asia-Pacific (sum)的总数据
        const apacSum = {
            Region: 'Asia-Pacific (sum)',
            Year: year,
            'Gross Bookings': apacCountriesData.reduce((sum, c) => sum + c.GrossBookings, 0),
            'Online Bookings': apacCountriesData.reduce((sum, c) => sum + c.OnlineBookings, 0),
            'Online Penetration': 0
        };
        
        // 计算在线渗透率
        apacSum['Online Penetration'] = apacSum['Online Bookings'] / apacSum['Gross Bookings'];
        
        // 添加到数据中
        combinedData.push(apacSum);
    }
    
    // 为所有APAC国家准备数据，确保下一年的数据准备好进行插值
    const allCountries = new Set();
    
    // 收集当前年份的所有国家
    apacCountriesData.forEach(country => {
        allCountries.add(country.Market);
    });
    
    // 如果在动画中，也收集下一年的所有国家
    if (isAnimating) {
        nextYearApacData.forEach(country => {
            allCountries.add(country.Market);
        });
    }
    
    // 添加所有国家数据，确保平滑过渡
    Array.from(allCountries).forEach(countryName => {
        const currentCountry = apacCountriesData.find(c => c.Market === countryName);
        
        if (isAnimating) {
            const nextCountry = nextYearApacData.find(c => c.Market === countryName);
            
            if (currentCountry && nextCountry) {
                // 两年都有数据，插值计算
                combinedData.push({
                    Region: countryName,
                    'Gross Bookings': currentCountry.GrossBookings + (nextCountry.GrossBookings - currentCountry.GrossBookings) * progress,
                    'Online Bookings': currentCountry.OnlineBookings + (nextCountry.OnlineBookings - currentCountry.OnlineBookings) * progress,
                    'Online Penetration': currentCountry.OnlinePenetration + (nextCountry.OnlinePenetration - currentCountry.OnlinePenetration) * progress,
                    Year: year,
                    isCountryData: true  // 标记为国家数据
                });
            } else if (currentCountry && !nextCountry) {
                // 当前年有，下一年没有，渐变消失
                const opacity = 1 - progress;
                if (opacity > 0) {
                    combinedData.push({
                        Region: countryName,
                        'Gross Bookings': currentCountry.GrossBookings * opacity,
                        'Online Bookings': currentCountry.OnlineBookings * opacity,
                        'Online Penetration': currentCountry.OnlinePenetration,
                        Year: year,
                        fading: true,
                        isCountryData: true  // 标记为国家数据
                    });
                }
            } else if (!currentCountry && nextCountry) {
                // 当前年没有，下一年有，渐变出现
                combinedData.push({
                    Region: countryName,
                    'Gross Bookings': nextCountry.GrossBookings * progress,
                    'Online Bookings': nextCountry.OnlineBookings * progress,
                    'Online Penetration': nextCountry.OnlinePenetration,
                    Year: year,
                    fading: true,
                    isCountryData: true  // 标记为国家数据
                });
            }
        } else if (currentCountry) {
            // 非动画状态，直接使用当前年数据
            combinedData.push({
                Region: countryName,
                'Gross Bookings': currentCountry.GrossBookings,
                'Online Bookings': currentCountry.OnlineBookings,
                'Online Penetration': currentCountry.OnlinePenetration,
                Year: year,
                isCountryData: true  // 标记为国家数据
            });
        }
    });
    
    // 处理数据
    const processedData = combinedData.map(d => {
        let color;
        const regionName = d.Region;
        let isCountry = d.isCountryData || false;
        
        // 确定颜色：颜色映射必须保持一致
        if (regionName === 'Asia-Pacific (sum)' || 
            (apacCountriesData.some(c => c.Market === regionName) || 
             (nextYearApacData && nextYearApacData.some(c => c.Market === regionName)))) {
            color = '#FF4B4B'; // 红色
            // 如果是国家（而不是Asia-Pacific sum）则标记为国家数据
            if (regionName !== 'Asia-Pacific (sum)') {
                isCountry = true;
            }
        } else if (regionName === 'Europe') {
            color = '#4169E1'; // 蓝色
        } else if (regionName === 'Eastern Europe') {
            color = '#9370DB'; // 紫色
        } else if (regionName === 'Latin America') {
            color = '#32CD32'; // 绿色
        } else if (regionName === 'Middle East') {
            color = '#DEB887'; // 棕色
        } else if (regionName === 'North America') {
            color = '#40E0D0'; // 绿松石色
        } else {
            // 默认颜色
            color = '#888888';
        }
        
        // 确保值是有效的数字
        const grossBookings = d['Gross Bookings'] || 0;
        const value = grossBookings * appConfig.dataProcessing.bookingsScaleFactor;
        
        return {
            region: regionName,
            value: isNaN(value) ? 0 : value,
            color: color,
            fading: d.fading || false,
            isCountry: isCountry
        };
    });
    
    // 按照值从小到大排序，给国家数据稍微加权以保持稳定性
    const sortedData = processedData
        .filter(d => d.value > 0.1) // 过滤掉太小的值
        .sort((a, b) => {
            // 确保排序稳定，尤其是对于国家数据
            const aValue = a.isCountry ? a.value * 1.0001 : a.value;
            const bValue = b.isCountry ? b.value * 1.0001 : b.value;
            return aValue - bValue;
        })
        .slice(-15); // 只取前15名
    
    // 初始化上一次的数据，用于平滑过渡
    if (!window.previousSortedData) {
        window.previousSortedData = sortedData.map(d => ({...d}));
    }
    
    // 如果不是动画状态，直接更新图表
    if (!isAnimating) {
        Plotly.relayout('race-chart', {
            'xaxis.range': [0, window.globalMaxValue * 1.2] // 确保x轴范围始终一致
        });
        
        Plotly.animate('race-chart', {
            data: [{
                y: sortedData.map(d => d.region),
                x: sortedData.map(d => d.value),
                marker: {
                    color: sortedData.map(d => d.color)
                },
                text: sortedData.map(d => d.value.toFixed(1)),
                texttemplate: '%{text}B'
            }]
        }, {
            transition: { duration: 0 },
            frame: { duration: 0, redraw: false } // 避免重绘导致的闪烁
        });
        
        // 更新上一次的数据
        window.previousSortedData = sortedData.map(d => ({...d}));
        window.raceChartData = sortedData;
        return;
    }
    
    // 简化动画处理，避免多次小步骤动画导致的抖动
    // 创建插值数据
    const interpolatedData = [];
    
    // 收集所有区域和国家
    const allRegions = new Set();
    sortedData.forEach(d => allRegions.add(d.region));
    window.previousSortedData.forEach(d => allRegions.add(d.region));
    
    // 为每个区域创建插值
    Array.from(allRegions).forEach(regionName => {
        const currentItem = sortedData.find(d => d.region === regionName);
        const previousItem = window.previousSortedData.find(d => d.region === regionName);
        
        if (currentItem && previousItem) {
            // 计算平滑插值
            let tween = progress;
            if (currentItem.isCountry) {
                // 对国家数据使用缓动函数
                tween = Math.pow(progress, 0.8);
            }
            
            // 计算位置插值
            const currentIndex = sortedData.findIndex(d => d.region === regionName);
            const previousIndex = window.previousSortedData.findIndex(d => d.region === regionName);
            const positionTween = currentItem.isCountry ? 
                Math.pow(progress, 0.85) : // 国家位置变化更平滑
                progress;
            const position = previousIndex + (currentIndex - previousIndex) * positionTween;
            
            interpolatedData.push({
                region: regionName,
                value: previousItem.value + (currentItem.value - previousItem.value) * tween,
                color: currentItem.color,
                position: position,
                isCountry: currentItem.isCountry
            });
        } else if (previousItem && !currentItem) {
            // 淡出效果
            const fadeOutOpacity = 1 - progress;
            if (fadeOutOpacity > 0.05) {
                interpolatedData.push({
                    region: regionName,
                    value: previousItem.value * fadeOutOpacity,
                    color: previousItem.color,
                    position: window.previousSortedData.findIndex(d => d.region === regionName),
                    isCountry: previousItem.isCountry
                });
            }
        } else if (!previousItem && currentItem) {
            // 淡入效果
            interpolatedData.push({
                region: regionName,
                value: currentItem.value * progress,
                color: currentItem.color,
                position: sortedData.findIndex(d => d.region === regionName),
                isCountry: currentItem.isCountry
            });
        }
    });
    
    // 按位置排序
    interpolatedData.sort((a, b) => a.position - b.position);
    
    // 确保坐标轴范围保持一致
    Plotly.relayout('race-chart', {
        'xaxis.range': [0, window.globalMaxValue * 1.2]
    });
    
    // 更新图表，使用单步动画
    Plotly.animate('race-chart', {
        data: [{
            y: interpolatedData.map(d => d.region),
            x: interpolatedData.map(d => d.value),
            marker: {
                color: interpolatedData.map(d => d.color)
            },
            text: interpolatedData.map(d => d.value.toFixed(1)),
            texttemplate: '%{text}B'
        }]
    }, {
        transition: {
            duration: 30, // 使用更长但更平滑的过渡
            easing: 'cubic-in-out'
        },
        frame: {
            duration: 30,
            redraw: false // 避免完全重绘导致的跳动
        }
    });
    
    // 动画完成后更新参考数据
    if (progress >= 0.99) {
        window.previousSortedData = sortedData.map(d => ({...d}));
        window.raceChartData = sortedData;
    }
} 