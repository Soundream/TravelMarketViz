<template>
  <div class="chart-container">
    <div id="additional-chart" class="w-full h-full"></div>
  </div>
</template>

<style scoped>
.chart-container {
  width: 100%;
  height: 100%;
  min-height: 840px;
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.zero-line {
  opacity: 0.5;
}

.dot, .cross {
  cursor: pointer;
  transition: all 0.2s ease;
}

.dot:hover, .cross:hover {
  transform: scale(1.5);
}

.quarter-label {
  pointer-events: none;
  user-select: none;
}

.active {
  stroke: #000;
  stroke-width: 2px;
}
</style>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue';
import * as d3 from 'd3';
import * as XLSX from 'xlsx';

// Import all logos
import ABNB_LOGO from '/logos/ABNB_logo.png'
import BKNG_LOGO from '/logos/BKNG_logo.png'
import EXPE_LOGO from '/logos/EXPE_logo.png'
import TCOM_LOGO from '/logos/TCOM_logo.png'
import TRIP_LOGO from '/logos/TRIP_logo.png'
import TRVG_LOGO from '/logos/TRVG_logo.png'
import EDR_LOGO from '/logos/EDR_logo.png'
import DESP_LOGO from '/logos/DESP_logo.png'
import MMYT_LOGO from '/logos/MMYT_logo.png'
import IXIGO_LOGO from '/logos/IXIGO_logo.png'
import LMN_LOGO from '/logos/LMN_logo.png'
import YTRA_LOGO from '/logos/YTRA_logo.png'
import OWW_LOGO from '/logos/OWW_logo.png'
import TRAVELOCITY_LOGO from '/logos/Travelocity_logo.png'
import EASEMYTRIP_LOGO from '/logos/EASEMYTRIP_logo.png'
import WEGO_LOGO from '/logos/Wego_logo.png'
import SKYSCANNER_LOGO from '/logos/Skyscanner_logo.png'
import ETRAVELI_LOGO from '/logos/Etraveli_logo.png'
import KIWI_LOGO from '/logos/Kiwi_logo.png'
import CLEARTRIP_LOGO from '/logos/Cleartrip_logo.png'
import TRAVELOKA_LOGO from '/logos/Traveloka_logo.png'
import FLIGHTCENTRE_LOGO from '/logos/FlightCentre_logo.png'
import SEERA_LOGO from '/logos/SEERA_logo.png'

// Company colors
const colorDict = {
  'ABNB': '#ff5895',
  'Almosafer': '#bb5387',
  'BKNG': '#003480',
  'DESP': '#755bd8',
  'EXPE': '#fbcc33',
  'EaseMyTrip': '#00a0e2',
  'Ixigo': '#e74c3c',
  'MMYT': '#e74c3c',
  'TRIP': '#00af87',
  'TRVG': '#e74c3c',
  'Wego': '#4e843d',
  'Yatra': '#e74c3c',
  'TCOM': '#2577e3',
  'EDR': '#2577e3',
  'LMN': '#fc03b1',
  'Webjet': '#e74c3c',
  'SEERA': '#750808',
  'PCLN': '#003480',
  'Orbitz': '#8edbfa',
  'Travelocity': '#1d3e5c',
  'Skyscanner': '#0770e3',
  'Etraveli': '#b2e9ff',
  'Kiwi': '#e5fdd4',
  'Cleartrip': '#e74c3c',
  'Traveloka': '#38a0e2',
  'FLT': '#d2b6a8',
  'Webjet OTA': '#e74c3c'
};

// Company logos
const logoDict = {
  'ABNB': ABNB_LOGO,
  'BKNG': BKNG_LOGO,
  'EXPE': EXPE_LOGO,
  'TCOM': TCOM_LOGO,
  'TRIP': TRIP_LOGO,
  'TRVG': TRVG_LOGO,
  'EDR': EDR_LOGO,
  'DESP': DESP_LOGO,
  'MMYT': MMYT_LOGO,
  'Ixigo': IXIGO_LOGO,
  'SEERA': SEERA_LOGO,
  'LMN': LMN_LOGO,
  'Yatra': YTRA_LOGO,
  'Orbitz': OWW_LOGO,
  'Travelocity': TRAVELOCITY_LOGO,
  'EaseMyTrip': EASEMYTRIP_LOGO,
  'Wego': WEGO_LOGO,
  'Skyscanner': SKYSCANNER_LOGO,
  'Etraveli': ETRAVELI_LOGO,
  'Kiwi': KIWI_LOGO,
  'Cleartrip': CLEARTRIP_LOGO,
  'Traveloka': TRAVELOKA_LOGO,
  'FLT': FLIGHTCENTRE_LOGO,
  'Almosafer': SEERA_LOGO,
  'Webjet OTA': SEERA_LOGO
};

// Add company names mapping
const companyNames = {
  'ABNB': 'Airbnb',
  'BKNG': 'Booking.com',
  'EXPE': 'Expedia',
  'TCOM': 'Trip.com',
  'TRIP': 'TripAdvisor',
  'TRVG': 'Trivago',
  'EDR': 'Edreams',
  'DESP': 'Despegar',
  'MMYT': 'MakeMyTrip',
  'Ixigo': 'Ixigo',
  'SEERA': 'Seera Group',
  'Webjet': 'Webjet',
  'LMN': 'Lastminute',
  'Yatra': 'Yatra.com',
  'Orbitz': 'Orbitz',
  'Travelocity': 'Travelocity',
  'EaseMyTrip': 'EaseMyTrip',
  'Wego': 'Wego',
  'Skyscanner': 'Skyscanner',
  'Etraveli': 'Etraveli',
  'Kiwi': 'Kiwi',
  'Cleartrip': 'Cleartrip',
  'FLT': 'Flight Centre',
  'Almosafer': 'Almosafer',
  'Webjet OTA': 'Webjet OTA'
};

let mergedData = ref([]);
let isPlaying = ref(false);
let animationInterval = null;
let currentYearIndex = 0;
let years = [];

// Add these as component-level variables to maintain consistent scales
let xScale, yScale;
let globalXDomain = [-0.7, 1.2];  // EBITDA margin range: -50% to 100% in decimal form
let globalYDomain = [-0.3, 1.2]; // Revenue growth range: -10% to 100% in decimal form

// Function to process XLSX data
const processExcelData = (file) => {
  console.log('Starting to process Excel file:', file.name);
  const reader = new FileReader();
  
  reader.onload = (e) => {
    try {
      console.log('File loaded, starting to parse...');
      const data = new Uint8Array(e.target.result);
      const workbook = XLSX.read(data, { type: 'array' });
      console.log('Available sheets:', workbook.SheetNames);
      
      // Get the TTM sheet
      const ttmSheet = workbook.Sheets['TTM (bounded)'];
      if (!ttmSheet) {
        throw new Error('TTM (bounded) sheet not found');
      }

      // Convert sheet to JSON with headers
      const jsonData = XLSX.utils.sheet_to_json(ttmSheet, { header: 1 });
      console.log('Raw data rows:', jsonData.length);
      
      if (jsonData.length < 3) {
        throw new Error('数据行数不足');
      }
      
      // Get headers (company names)
      const headers = jsonData[0];
      if (!headers || headers.length < 2) {
        throw new Error('表头数据无效');
      }
      console.log('Headers:', headers);
      
      // Process data
      const processedData = [];
      years = []; // Reset years array
      
      // 找到收入增长和 EBITDA 的分界点
      const ebitdaStartIndex = jsonData.findIndex(row => 
        row && row[0] && String(row[0]).toLowerCase().includes('ebitda margin')
      );

      console.log('EBITDA start index:', ebitdaStartIndex);
      console.log('Total rows:', jsonData.length);

      if (ebitdaStartIndex === -1) {
        throw new Error('未找到 EBITDA Margin 标记行');
      }

      // 获取有效的公司列表（从第3列开始，因为前两列是空的）
      const validCompanies = headers.slice(2).filter(company => company);
      console.log('Valid companies:', validCompanies);

      // 计算上半部分和下半部分的行数
      const revenueRowCount = ebitdaStartIndex - 1; // 减去表头行
      console.log('Revenue section row count:', revenueRowCount);

      // 处理每一年的数据
      for (let i = 1; i < ebitdaStartIndex; i++) {
        const revenueRow = jsonData[i];
        if (!revenueRow || !revenueRow[0]) continue;
        
        const yearStr = String(revenueRow[0]).trim();
        const yearMatch = yearStr.match(/^(\d{4})/);
        if (!yearMatch) continue;
        
        const year = yearMatch[1];
        if (!years.includes(year)) {
          years.push(year);
        }
        
        // 计算对应的 EBITDA 行索引
        // EBITDA 部分的起始位置是 ebitdaStartIndex + 1
        // 相对位置与收入部分相同
        const relativeIndex = i - 1; // 减1是因为要跳过表头行
        const ebitdaRowIndex = ebitdaStartIndex + 1 + relativeIndex;
        const ebitdaRow = jsonData[ebitdaRowIndex];
        
        console.log(`Processing year ${year}:`, {
          revenueRowIndex: i,
          ebitdaRowIndex: ebitdaRowIndex,
          hasRevenueData: !!revenueRow,
          hasEbitdaData: !!ebitdaRow,
          revenueRowSample: revenueRow.slice(0, 5),
          ebitdaRowSample: ebitdaRow ? ebitdaRow.slice(0, 5) : null,
          yearMatch: yearMatch[0]
        });
        
        if (!ebitdaRow) {
          console.log(`No EBITDA data found for year ${year} at index ${ebitdaRowIndex}`);
          continue;
        }
        
        // 处理每个公司的数据（从第3列开始）
        for (let j = 2; j < headers.length; j++) {
          const company = headers[j];
          if (!company) continue;
          
          const revenueGrowth = revenueRow[j];
          const ebitdaMargin = ebitdaRow[j];
          
          console.log(`Processing ${company} data for ${year}:`, {
            revenueGrowth,
            ebitdaMargin,
            columnIndex: j,
            rowIndex: i,
            ebitdaRowIndex
          });
          
          // 处理空值或无效值，使用默认值0
          let growth = 0;
          let margin = 0;
          
          // 处理收入增长率
          if (revenueGrowth !== undefined && revenueGrowth !== null && revenueGrowth !== '') {
            if (typeof revenueGrowth === 'string' && revenueGrowth.includes('%')) {
              growth = parseFloat(revenueGrowth.replace('%', '')) / 100;
            } else {
              growth = parseFloat(revenueGrowth);
            }
            if (isNaN(growth)) growth = 0;
          }
          
          // 处理 EBITDA 利润率
          if (ebitdaMargin !== undefined && ebitdaMargin !== null && ebitdaMargin !== '') {
            if (typeof ebitdaMargin === 'string' && ebitdaMargin.includes('%')) {
              margin = parseFloat(ebitdaMargin.replace('%', '')) / 100;
            } else {
              margin = parseFloat(ebitdaMargin);
            }
            if (isNaN(margin)) margin = 0;
          }
          
          // 添加数据点，即使值为0
          processedData.push({
            year,
            company,
            revenueGrowth: growth,
            ebitdaMargin: margin
          });
          
          // 记录日志
          if (growth !== 0 || margin !== 0) {
            console.log('Added valid data point for:', company, { 
              year, 
              growth, 
              margin,
              rawRevenue: revenueGrowth,
              rawEbitda: ebitdaMargin
            });
          }
        }
      }
      
      // Sort years
      years.sort((a, b) => parseInt(a) - parseInt(b));
      
      console.log('Final processed data:', {
        years,
        dataPoints: processedData.length,
        sample: processedData.slice(0, 5),
        yearCount: years.length,
        companyCount: validCompanies.length,
        firstFewDataPoints: processedData.slice(0, 3).map(d => ({
          year: d.year,
          company: d.company,
          growth: d.revenueGrowth,
          margin: d.ebitdaMargin,
          rawData: true
        }))
      });
      
      if (processedData.length === 0) {
        throw new Error('没有找到有效的数据点');
      }
      
      // Update the data
      mergedData.value = processedData;
      currentYearIndex = 0;
      
      // Initialize the visualization
      console.log('Initializing chart with data points:', processedData.length);
      initChart();
      
    } catch (error) {
      console.error('Error processing Excel file:', error);
      alert('处理数据时出错：' + error.message);
    }
  };
  
  reader.onerror = (error) => {
    console.error('Error reading file:', error);
    alert('读取文件时出错');
  };
  
  try {
    reader.readAsArrayBuffer(file);
  } catch (error) {
    console.error('Error starting file read:', error);
    alert('启动文件读取时出错');
  }
};

// Initialize chart
const initChart = () => {
  try {
    // Clear previous chart
    d3.select('#additional-chart').selectAll('*').remove();
    
    // Create SVG
    const svg = d3.select('#additional-chart').append('svg')
      .attr('width', '100%')
      .attr('height', '100%')
      .attr('viewBox', '0 0 1200 840')
      .attr('preserveAspectRatio', 'xMidYMid meet');

    const margin = { top: 40, right: 20, bottom: 50, left: 60 };
    const width = 1200 - margin.left - margin.right;
    const height = 840 - margin.top - margin.bottom;

    const g = svg.append("g")
      .attr("transform", `translate(${margin.left}, ${margin.top})`);

    // Initialize scales with fixed domains
    xScale = d3.scaleLinear()
      .domain(globalXDomain)
      .range([0, width]);

    yScale = d3.scaleLinear()
      .domain(globalYDomain)
      .range([height, 0]);

    // Create axes
    const xAxis = d3.axisBottom(xScale).tickFormat(d3.format('.0%'));
    const yAxis = d3.axisLeft(yScale).tickFormat(d3.format('.0%'));

    // Add axes
    g.append('g')
      .attr('class', 'x-axis')
      .attr('transform', `translate(0,${height})`)
      .call(xAxis);

    g.append('g')
      .attr('class', 'y-axis')
      .call(yAxis);

    // Add axis labels
    g.append('text')
      .attr('class', 'x-label')
      .attr('text-anchor', 'middle')
      .attr('x', width / 2)
      .attr('y', height + 40)
      .text('EBITDA Margin')
      .style('font-size', '14px');

    g.append('text')
      .attr('class', 'y-label')
      .attr('text-anchor', 'middle')
      .attr('transform', 'rotate(-90)')
      .attr('y', -45)
      .attr('x', -height / 2)
      .text('Revenue Growth YoY')
      .style('font-size', '14px');

    // Add zero lines
    g.append('line')
      .attr('class', 'zero-line')
      .attr('x1', xScale(0))
      .attr('y1', 0)
      .attr('x2', xScale(0))
      .attr('y2', height)
      .attr('stroke', '#4e843d')
      .attr('stroke-dasharray', '4,4');

    g.append('line')
      .attr('class', 'zero-line')
      .attr('x1', 0)
      .attr('y1', yScale(0))
      .attr('x2', width)
      .attr('y2', yScale(0))
      .attr('stroke', '#4e843d')
      .attr('stroke-dasharray', '4,4');

    // Define drag behaviors
    const dragLogo = d3.drag()
      .on('start', dragStarted)
      .on('drag', dragged)
      .on('end', dragEnded);

    function dragStarted(event, d) {
      d3.select(this).raise().classed('active', true);
    }

    function dragged(event, d) {
      d3.select(this)
        .attr('x', d.x = event.x)
        .attr('y', d.y = event.y);
    }

    function dragEnded(event, d) {
      d3.select(this).classed('active', false);
    }

    // Function to update chart with animation
    function updateChart(yearIndex) {
      const currentYear = years[yearIndex];
      const yearData = mergedData.value.filter(d => d.year === currentYear);

      // Update bubbles with proper transitions
      const bubbles = g.selectAll('.bubble')
        .data(yearData, d => d.company);

      // Enter new bubbles
      bubbles.enter()
        .append('circle')
        .attr('class', 'bubble')
        .attr('r', 8)
        .attr('fill', d => colorDict[d.company])
        .attr('cx', d => xScale(d.ebitdaMargin))
        .attr('cy', d => yScale(d.revenueGrowth));

      // Update all bubbles (both existing and new)
      g.selectAll('.bubble')
        .transition()
        .duration(750)
        .ease(d3.easeCubicInOut)
        .attr('cx', d => xScale(d.ebitdaMargin))
        .attr('cy', d => yScale(d.revenueGrowth))
        .attr('fill', d => colorDict[d.company]);

      // Remove old bubbles
      bubbles.exit().remove();

      // Update logos with proper transitions
      const logos = g.selectAll('.logo')
        .data(yearData, d => d.company);

      // Enter new logos
      logos.enter()
        .append('image')
        .attr('class', 'logo')
        .attr('width', 50)
        .attr('height', 50)
        .attr('xlink:href', d => logoDict[d.company])
        .attr('x', d => xScale(d.ebitdaMargin) - 25)
        .attr('y', d => yScale(d.revenueGrowth) - 55)
        .call(dragLogo);

      // Update all logos (both existing and new)
      g.selectAll('.logo')
        .transition()
        .duration(750)
        .ease(d3.easeCubicInOut)
        .attr('x', d => xScale(d.ebitdaMargin) - 25)
        .attr('y', d => yScale(d.revenueGrowth) - 55);

      // Remove old logos
      logos.exit().remove();

      // Update trend indicators
      const trends = g.selectAll('.trend')
        .data(yearData, d => d.company);

      // Enter new trends
      trends.enter()
        .append('text')
        .attr('class', 'trend')
        .attr('text-anchor', 'middle')
        .attr('x', d => xScale(d.ebitdaMargin))
        .attr('y', d => yScale(d.revenueGrowth) + 20)
        .text(d => {
          if (d.revenueTrend === 'increase') return '↑';
          if (d.revenueTrend === 'decrease') return '↓';
          return '→';
        })
        .attr('fill', d => {
          if (d.revenueTrend === 'increase') return '#4CAF50';
          if (d.revenueTrend === 'decrease') return '#F44336';
          return '#9E9E9E';
        });

      // Update all trends (both existing and new)
      g.selectAll('.trend')
        .transition()
        .duration(750)
        .ease(d3.easeCubicInOut)
        .attr('x', d => xScale(d.ebitdaMargin))
        .attr('y', d => yScale(d.revenueGrowth) + 20)
        .text(d => {
          if (d.revenueTrend === 'increase') return '↑';
          if (d.revenueTrend === 'decrease') return '↓';
          return '→';
        })
        .attr('fill', d => {
          if (d.revenueTrend === 'increase') return '#4CAF50';
          if (d.revenueTrend === 'decrease') return '#F44336';
          return '#9E9E9E';
        });

      // Remove old trends
      trends.exit().remove();

      // Update year label
      g.selectAll('.year-label').remove();
      g.append('text')
        .attr('class', 'year-label')
        .attr('x', width / 2)
        .attr('y', -10)
        .attr('text-anchor', 'middle')
        .style('font-size', '24px')
        .text(currentYear);
    }

    // Initial update
    updateChart(currentYearIndex);

    // Animation control methods
    const togglePlay = () => {
      isPlaying.value = !isPlaying.value;
      if (isPlaying.value) {
        animationInterval = setInterval(() => {
          currentYearIndex = (currentYearIndex + 1) % years.length;
          updateChart(currentYearIndex);
        }, 1000);
      } else {
        clearInterval(animationInterval);
      }
    };

    // Cleanup
    onUnmounted(() => {
      if (animationInterval) {
        clearInterval(animationInterval);
      }
    });

  } catch (error) {
    console.error('Error initializing chart:', error);
  }
};

// Expose methods
defineExpose({
  processExcelData,
  togglePlay: () => {
    isPlaying.value = !isPlaying.value;
    if (isPlaying.value) {
      animationInterval = setInterval(() => {
        currentYearIndex = (currentYearIndex + 1) % years.length;
        initChart();
      }, 1000);
    } else {
      clearInterval(animationInterval);
    }
  },
  isPlaying
});
</script> 