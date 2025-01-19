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
  'ABNB': '#FF5A5F',
  'BKNG': '#003580',
  'EXPE': '#00355F',
  'TCOM': '#003580',
  'TRIP': '#34E0A1',
  'Almosafer': '#bb5387',
  'Cleartrip': '#e74c3c',
  'EaseMyTrip': '#00a0e2',
  'Ixigo': '#e74c3c',
  'MMYT': '#e74c3c',
  'Skyscanner': '#0770e3',
  'Wego': '#4e843d',
  'Yatra': '#e74c3c'
};

// Company logos
const logoDict = {
  'ABNB': '/logos/ABNB_logo.png',
  'BKNG': '/logos/BKNG_logo.png',
  'EXPE': '/logos/EXPE_logo.png',
  'TCOM': '/logos/TCOM_logo.png',
  'TRIP': '/logos/TRIP_logo.png',
  'Almosafer': '/logos/Almosafer_logo.png',
  'Cleartrip': '/logos/Cleartrip_logo.png',
  'EaseMyTrip': '/logos/EASEMYTRIP_logo.png',
  'Ixigo': '/logos/IXIGO_logo.png',
  'MMYT': '/logos/MMYT_logo.png',
  'Skyscanner': '/logos/Skyscanner_logo.png',
  'Wego': '/logos/Wego_logo.png',
  'Yatra': '/logos/YTRA_logo.png'
};

let mergedData = ref([]);
let isPlaying = ref(false);
let animationInterval = null;
let currentYearIndex = 0;
let years = [];

// Add these as component-level variables to maintain consistent scales
let xScale, yScale;
let globalXDomain = [-60, 60];  // Fixed domain for EBITDA margin
let globalYDomain = [-40, 110]; // Fixed domain for revenue growth

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

    // Convert sheet to JSON
    const jsonData = XLSX.utils.sheet_to_json(ttmSheet, { header: 1 });
    
    // First row contains company names (headers)
    const headers = jsonData[0];
    
    // Process data for each year
    const processedData = [];
    years = []; // Reset years array
    
    for (let i = 1; i < jsonData.length; i++) {
      const row = jsonData[i];
      const year = row[0]; // First column is year
      if (!years.includes(year)) {
        years.push(year);
      }
      
      // Process each company's data
      for (let j = 1; j < headers.length; j++) {
        const company = headers[j];
        const value = row[j];
        
        // Skip if no value or company
        if (!company || value === undefined) continue;
        
        // Determine if it's an increase or decrease
        const prevValue = i > 1 ? jsonData[i-1][j] : null;
        let trend = null;
        if (prevValue !== null && value !== null) {
          trend = value > prevValue ? 'increase' : value < prevValue ? 'decrease' : 'neutral';
        }
        
        processedData.push({
          year: year,
          company: company,
          value: value,
          trend: trend,
          x: value, // Store original position
          y: value  // Store original position
        });
      }
    }

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
      .attr('stroke', '#ccc')
      .attr('stroke-dasharray', '4,4');

    g.append('line')
      .attr('class', 'zero-line')
      .attr('x1', 0)
      .attr('y1', yScale(0))
      .attr('x2', width)
      .attr('y2', yScale(0))
      .attr('stroke', '#ccc')
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
      const bubblesEnter = bubbles.enter()
        .append('circle')
        .attr('class', 'bubble')
        .attr('r', 8)
        .attr('fill', d => colorDict[d.company])
        .attr('cx', d => xScale(d.value))
        .attr('cy', height); // Start from bottom

      // Update existing bubbles
      bubbles.merge(bubblesEnter)
        .transition()
        .duration(750)
        .attr('cx', d => xScale(d.value))
        .attr('cy', d => yScale(d.value))
        .attr('fill', d => colorDict[d.company]);

      // Remove old bubbles
      bubbles.exit()
        .transition()
        .duration(750)
        .attr('cy', height)
        .remove();

      // Update logos with proper transitions
      const logos = g.selectAll('.logo')
        .data(yearData, d => d.company);

      // Enter new logos
      const logosEnter = logos.enter()
        .append('image')
        .attr('class', 'logo')
        .attr('width', 30)
        .attr('height', 30)
        .attr('xlink:href', d => logoDict[d.company])
        .attr('x', d => xScale(d.value) - 15)
        .attr('y', height - 35)
        .call(dragLogo);

      // Update existing logos
      logos.merge(logosEnter)
        .transition()
        .duration(750)
        .attr('x', d => xScale(d.value) - 15)
        .attr('y', d => yScale(d.value) - 35);

      // Remove old logos
      logos.exit()
        .transition()
        .duration(750)
        .attr('y', height - 35)
        .remove();

      // Update trend indicators
      const trends = g.selectAll('.trend')
        .data(yearData, d => d.company);

      // Enter new trends
      const trendsEnter = trends.enter()
        .append('text')
        .attr('class', 'trend')
        .attr('text-anchor', 'middle')
        .attr('x', d => xScale(d.value))
        .attr('y', height + 20);

      // Update existing trends
      trends.merge(trendsEnter)
        .transition()
        .duration(750)
        .attr('x', d => xScale(d.value))
        .attr('y', d => yScale(d.value) + 20)
        .text(d => {
          if (d.trend === 'increase') return '↑';
          if (d.trend === 'decrease') return '↓';
          return '→';
        })
        .attr('fill', d => {
          if (d.trend === 'increase') return '#4CAF50';
          if (d.trend === 'decrease') return '#F44336';
          return '#9E9E9E';
        });

      // Remove old trends
      trends.exit()
        .transition()
        .duration(750)
        .attr('y', height + 20)
        .remove();

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