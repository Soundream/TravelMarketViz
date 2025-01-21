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
  'ABNB': '/logos/ABNB_logo.png',
  'BKNG': '/logos/BKNG_logo.png',
  'EXPE': '/logos/EXPE_logo.png',
  'TCOM': '/logos/TCOM_logo.png',
  'TRIP': '/logos/TRIP_logo.png',
  'TRVG': '/logos/TRVG_logo.png',
  'EDR': '/logos/EDR_logo.png',
  'DESP': '/logos/DESP_logo.png',
  'MMYT': '/logos/MMYT_logo.png',
  'Ixigo': '/logos/IXIGO_logo.png',
  'SEERA': '/logos/SEERA_logo.png',
  'Webjet': '/logos/WEB_logo.png',
  'LMN': '/logos/LMN_logo.png',
  'Yatra': '/logos/YTRA_logo.png',
  'Orbitz': '/logos/OWW_logo.png',
  'Travelocity': '/logos/Travelocity_logo.png',
  'EaseMyTrip': '/logos/EASEMYTRIP_logo.png',
  'Wego': '/logos/Wego_logo.png',
  'Skyscanner': '/logos/Skyscanner_logo.png',
  'Etraveli': '/logos/Etraveli_logo.png',
  'Kiwi': '/logos/Kiwi_logo.png',
  'Cleartrip': '/logos/Cleartrip_logo.png',
  'Traveloka': '/logos/Traveloka_logo.png',
  'FLT': '/logos/FlightCentre_logo.png',
  'Almosafer': '/logos/Almosafer_logo.png',
  'Webjet OTA': '/logos/OTA_logo.png'
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
  const reader = new FileReader();
  reader.onload = (e) => {
    const data = new Uint8Array(e.target.result);
    const workbook = XLSX.read(data, { type: 'array' });
    
    // Get the TTM sheet
    const ttmSheet = workbook.Sheets['TTM (bounded)'];
    if (!ttmSheet) {
      console.error('TTM (bounded) sheet not found');
      return;
    }

    // Convert sheet to JSON with headers
    const jsonData = XLSX.utils.sheet_to_json(ttmSheet, { header: 1 });
    
    // First row contains company names (headers)
    const headers = jsonData[0];
    
    // Process data for each year/quarter
    const processedData = [];
    years = []; // Reset years array
    
    // Create maps to store revenue growth and EBITDA margin data
    const revenueGrowthData = new Map(); // key: 'company_quarter', value: growth value
    const ebitdaMarginData = new Map(); // key: 'company_quarter', value: margin value
    
    // Process revenue growth data (first half)
    for (let i = 2; i < 113; i++) {
      const row = jsonData[i];
      const yearQuarter = row[0];
      if (yearQuarter && !years.includes(yearQuarter)) {
        years.push(yearQuarter);
      }
      
      // Process each company's revenue growth
      for (let j = 1; j < headers.length; j++) {
        const company = headers[j];
        if (!company) continue;
        
        const value = row[j];
        if (value !== undefined) {
          // Convert to decimal if it's a number
          const numValue = typeof value === 'number' ? value : parseFloat(value);
          if (!isNaN(numValue)) {
            revenueGrowthData.set(`${company}_${yearQuarter}`, numValue);
          }
        }
      }
    }
    
    // Process EBITDA margin data (second half)
    for (let i = 116; i < jsonData.length; i++) {
      const row = jsonData[i];
      const yearQuarter = row[0];
      if (!yearQuarter) continue;
      
      // Process each company's EBITDA margin
      for (let j = 1; j < 227; j++) {
        const company = headers[j];
        if (!company) continue;
        
        const value = row[j];
        if (value !== undefined) {
          // Convert to decimal if it's a number
          const numValue = typeof value === 'number' ? value : parseFloat(value);
          if (!isNaN(numValue)) {
            ebitdaMarginData.set(`${company}_${yearQuarter}`, numValue);
          }
        }
      }
    }
    
    // Combine the data
    years.forEach(yearQuarter => {
      headers.slice(1).forEach(company => {
        if (!company) return;
        
        const revenueGrowth = revenueGrowthData.get(`${company}_${yearQuarter}`);
        const ebitdaMargin = ebitdaMarginData.get(`${company}_${yearQuarter}`);
        
        // Only add if we have both values and they're within our domain ranges
        if (revenueGrowth !== undefined && ebitdaMargin !== undefined &&
            revenueGrowth >= globalYDomain[0] && revenueGrowth <= globalYDomain[1] &&
            ebitdaMargin >= globalXDomain[0] && ebitdaMargin <= globalXDomain[1]) {
          
          // Find previous quarter's data for trend calculation
          const quarterIndex = years.indexOf(yearQuarter);
          let revenueTrend = null;
          let ebitdaTrend = null;
          
          if (quarterIndex > 0) {
            const prevQuarter = years[quarterIndex - 1];
            const prevRevenueGrowth = revenueGrowthData.get(`${company}_${prevQuarter}`);
            const prevEbitdaMargin = ebitdaMarginData.get(`${company}_${prevQuarter}`);
            
            if (prevRevenueGrowth !== undefined) {
              revenueTrend = revenueGrowth > prevRevenueGrowth ? 'increase' : 
                            revenueGrowth < prevRevenueGrowth ? 'decrease' : 'neutral';
            }
            
            if (prevEbitdaMargin !== undefined) {
              ebitdaTrend = ebitdaMargin > prevEbitdaMargin ? 'increase' : 
                           ebitdaMargin < prevEbitdaMargin ? 'decrease' : 'neutral';
            }
          }
          
          processedData.push({
            year: yearQuarter,
            company: company,
            ebitdaMargin: ebitdaMargin,
            revenueGrowth: revenueGrowth,
            ebitdaTrend: ebitdaTrend,
            revenueTrend: revenueTrend
          });
        }
      });
    });

    // Sort years chronologically
    years.sort((a, b) => {
      const [aYear, aQ] = a.split('Q').map(n => parseInt(n));
      const [bYear, bQ] = b.split('Q').map(n => parseInt(n));
      return aYear !== bYear ? aYear - bYear : aQ - bQ;
    });

    // Update the data
    mergedData.value = processedData;
    currentYearIndex = 0;
    
    // Initialize the visualization
    initChart();
  };
  reader.readAsArrayBuffer(file);
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