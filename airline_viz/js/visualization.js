// Airline Revenue Visualization
// Main visualization module using D3.js

class AirlineVisualization {
    constructor(options) {
        this.options = options;
        this.config = options.config;
        this.containerId = options.containerId;
        this.currentYear = this.config.startYear;
        this.svg = null;
        this.chart = null;
        this.initialized = false;
        this.animationInProgress = false;
    }

    // 初始化可视化
    initialize() {
        // 创建基本 SVG 元素
        this.createSvgElement();
        
        // 初始化 D3 图表
        this.initChart();
        
        // 注册事件监听器
        this.registerEventListeners();
        
        // 设置窗口更新函数
        window.updateVisualization = this.updateYear.bind(this);
        
        // 设置为已初始化
        this.initialized = true;
        
        // 加载初始年份的数据
        this.updateYear(this.currentYear);
        
        console.log('Visualization initialized');
    }
    
    // 创建 SVG 元素
    createSvgElement() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Container with ID "${this.containerId}" not found`);
            return;
        }
        
        // 清除容器内容
        container.innerHTML = '';
        
        // 创建 SVG 元素
        this.svg = d3.select(container)
            .append('svg')
            .attr('width', '100%')
            .attr('height', '100%')
            .attr('viewBox', `0 0 ${this.config.width} ${this.config.height}`)
            .attr('preserveAspectRatio', 'xMidYMid meet');
            
        // 添加图表组
        this.chart = this.svg.append('g')
            .attr('class', 'chart')
            .attr('transform', `translate(${this.config.margin.left}, ${this.config.margin.top})`);
            
        // 添加标题组
        this.titleGroup = this.svg.append('g')
            .attr('class', 'title-group')
            .attr('transform', `translate(${this.config.width / 2}, 30)`);
            
        // 添加标题
        this.titleGroup.append('text')
            .attr('class', 'chart-title')
            .attr('text-anchor', 'middle')
            .style('font-size', '24px')
            .style('font-weight', 'bold')
            .text('Top Airline Revenues');
            
        // 添加副标题（年份）
        this.yearTitle = this.titleGroup.append('text')
            .attr('class', 'year-title')
            .attr('text-anchor', 'middle')
            .attr('y', 30)
            .style('font-size', '20px')
            .text(`Year: ${this.currentYear}`);
            
        console.log('SVG element created');
    }
    
    // 初始化图表
    initChart() {
        // 创建轴和比例尺
        this.initAxes();
        
        // 添加 x 轴标签
        this.chart.append('text')
            .attr('class', 'x-axis-label')
            .attr('text-anchor', 'middle')
            .attr('x', (this.config.width - this.config.margin.left - this.config.margin.right) / 2)
            .attr('y', this.config.height - this.config.margin.top - 10)
            .style('font-size', '14px')
            .text(this.config.xAxisLabel);
            
        console.log('Chart initialized');
    }
    
    // 初始化坐标轴和比例尺
    initAxes() {
        // 获取图表可用宽度和高度
        const chartWidth = this.config.width - this.config.margin.left - this.config.margin.right;
        const chartHeight = this.config.height - this.config.margin.top - this.config.margin.bottom;
        
        // 创建 x 轴比例尺（线性比例尺，用于收入）
        this.xScale = d3.scaleLinear()
            .range([0, chartWidth]);
            
        // 创建 y 轴比例尺（带区域的比例尺，用于航空公司）
        this.yScale = d3.scaleBand()
            .range([0, chartHeight])
            .padding(0.3);
            
        // 创建颜色比例尺（类别比例尺，用于区域颜色）
        this.colorScale = d3.scaleOrdinal()
            .domain(['North America', 'Europe', 'Asia Pacific', 'Latin America', 'Middle East', 'China', 'Russia', 'India', 'Turkey', 'Africa'])
            .range(['#40E0D0', '#4169E1', '#FF4B4B', '#32CD32', '#DEB887', '#FF4B4B', '#FF4B4B', '#FF9900', '#DEB887', '#9932CC']);
            
        // 创建 x 轴
        this.xAxis = this.chart.append('g')
            .attr('class', 'x-axis')
            .attr('transform', `translate(0, ${chartHeight})`);
            
        // 创建 y 轴
        this.yAxis = this.chart.append('g')
            .attr('class', 'y-axis');
            
        console.log('Axes and scales initialized');
    }
    
    // 注册事件监听器
    registerEventListeners() {
        // 窗口大小变化时重新渲染
        window.addEventListener('resize', this.handleResize.bind(this));
        
        console.log('Event listeners registered');
    }
    
    // 处理窗口大小变化
    handleResize() {
        // 重新计算 SVG 大小
        const container = document.getElementById(this.containerId);
        if (!container) return;
        
        // 重新渲染图表
        this.updateYear(this.currentYear, false);
        
        console.log('Visualization resized');
    }
    
    // 更新年份
    updateYear(year, animate = true) {
        if (this.animationInProgress) return;
        
        this.currentYear = parseInt(year);
        console.log(`Updating visualization to year ${this.currentYear}`);
        
        // 更新年份标题
        this.yearTitle.text(`Year: ${this.currentYear}`);
        
        // 从 localStorage 获取该年份的数据
        const data = this.getYearData(this.currentYear);
        
        if (!data || data.length === 0) {
            console.warn(`No data available for year ${this.currentYear}`);
            this.showNoDataMessage();
            return;
        }
        
        // 更新并渲染数据
        this.updateChart(data, animate);
    }
    
    // 获取特定年份的数据
    getYearData(year) {
        try {
            const storedData = localStorage.getItem(`airlineData_${year}`);
            if (!storedData) {
                console.warn(`No data found in localStorage for year ${year}`);
                return [];
            }
            
            return JSON.parse(storedData);
        } catch (error) {
            console.error(`Error retrieving data for year ${year}:`, error);
            return [];
        }
    }
    
    // 显示无数据消息
    showNoDataMessage() {
        // 清除现有条形图
        this.chart.selectAll('.bar-group').remove();
        
        // 添加无数据消息
        const chartWidth = this.config.width - this.config.margin.left - this.config.margin.right;
        const chartHeight = this.config.height - this.config.margin.top - this.config.margin.bottom;
        
        this.chart.append('text')
            .attr('class', 'no-data-message')
            .attr('x', chartWidth / 2)
            .attr('y', chartHeight / 2)
            .attr('text-anchor', 'middle')
            .style('font-size', '18px')
            .style('fill', '#999')
            .text(`No data available for ${this.currentYear}`);
    }
    
    // 更新图表
    updateChart(data, animate) {
        // 设置动画标志
        if (animate) {
            this.animationInProgress = true;
        }
        
        // 获取图表尺寸
        const chartWidth = this.config.width - this.config.margin.left - this.config.margin.right;
        const chartHeight = this.config.height - this.config.margin.top - this.config.margin.bottom;
        
        // 清除现有内容
        this.chart.selectAll('.no-data-message').remove();
        
        // 更新刻度
        const maxRevenue = d3.max(data, d => d.revenue);
        this.xScale.domain([0, maxRevenue * 1.1]);  // 添加 10% 的空间
        this.yScale.domain(data.map(d => d.airline));
        
        // 更新 x 轴
        this.xAxis.transition()
            .duration(animate ? this.config.animationDuration : 0)
            .call(d3.axisBottom(this.xScale)
                .ticks(5)
                .tickFormat(d => {
                    if (d >= 1000) {
                        return `$${d/1000}B`;
                    }
                    return `$${d}M`;
                })
            );
            
        // 更新 y 轴
        this.yAxis.transition()
            .duration(animate ? this.config.animationDuration : 0)
            .call(d3.axisLeft(this.yScale));
            
        // 选择现有的条形图组
        const barGroups = this.chart.selectAll('.bar-group')
            .data(data, d => d.airline);
            
        // 移除不再存在的条形图
        barGroups.exit()
            .transition()
            .duration(animate ? this.config.animationDuration / 2 : 0)
            .attr('transform', `translate(${-chartWidth}, 0)`)
            .remove();
            
        // 创建新的条形图组
        const newBarGroups = barGroups.enter()
            .append('g')
            .attr('class', 'bar-group')
            .attr('transform', `translate(${-chartWidth}, 0)`); // 从左侧开始
            
        // 添加条形图
        newBarGroups.append('rect')
            .attr('class', 'bar')
            .attr('y', d => this.yScale(d.airline))
            .attr('height', this.yScale.bandwidth())
            .attr('width', 0)
            .attr('fill', d => this.getColorForAirline(d))
            .attr('rx', 3)
            .attr('ry', 3);
            
        // 添加文本标签（航空公司名称）
        newBarGroups.append('text')
            .attr('class', 'airline-label')
            .attr('x', 5)
            .attr('y', d => this.yScale(d.airline) + this.yScale.bandwidth() / 2)
            .attr('dy', '0.35em')
            .style('font-size', '14px')
            .style('fill', '#fff')
            .style('font-weight', 'bold')
            .text(d => `${d.airline} ${d.iataCode ? `(${d.iataCode})` : ''}`);
            
        // 添加收入值标签
        newBarGroups.append('text')
            .attr('class', 'revenue-label')
            .attr('y', d => this.yScale(d.airline) + this.yScale.bandwidth() / 2)
            .attr('dy', '0.35em')
            .attr('text-anchor', 'end')
            .style('font-size', '14px')
            .style('fill', '#fff')
            .style('font-weight', 'bold')
            .text(d => this.formatRevenue(d.revenue));
            
        // 创建更新后的选择集
        const allBarGroups = newBarGroups.merge(barGroups);
            
        // 更新所有条形图的位置和大小
        allBarGroups.transition()
            .duration(animate ? this.config.animationDuration : 0)
            .attr('transform', 'translate(0, 0)')
            .on('end', () => {
                if (animate) {
                    this.animationInProgress = false;
                }
            });
            
        allBarGroups.select('.bar')
            .transition()
            .duration(animate ? this.config.animationDuration : 0)
            .attr('y', d => this.yScale(d.airline))
            .attr('height', this.yScale.bandwidth())
            .attr('width', d => this.xScale(d.revenue));
            
        allBarGroups.select('.airline-label')
            .transition()
            .duration(animate ? this.config.animationDuration : 0)
            .attr('y', d => this.yScale(d.airline) + this.yScale.bandwidth() / 2);
            
        allBarGroups.select('.revenue-label')
            .transition()
            .duration(animate ? this.config.animationDuration : 0)
            .attr('x', d => this.xScale(d.revenue) - 10)
            .attr('y', d => this.yScale(d.airline) + this.yScale.bandwidth() / 2)
            .text(d => this.formatRevenue(d.revenue));
            
        console.log(`Chart updated with ${data.length} airlines for year ${this.currentYear}`);
    }
    
    // 获取航空公司的颜色
    getColorForAirline(airline) {
        if (!airline || !airline.region) {
            return this.config.defaultColor;
        }
        
        return this.colorScale(airline.region);
    }
    
    // 格式化收入数据
    formatRevenue(value) {
        if (value >= 1000) {
            return `$${(value/1000).toFixed(1)}B`;
        }
        return `$${value.toFixed(0)}M`;
    }
}

// Initialize visualization when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Check if CONFIG is available globally
    if (typeof CONFIG !== 'undefined') {
        // Create visualization instance
        const visualization = new AirlineVisualization({
            containerId: 'chart-container',
            config: CONFIG
        });
        
        // Initialize
        visualization.initialize();
    } else {
        console.warn('CONFIG not found, visualization may not work correctly');
    }
}); 