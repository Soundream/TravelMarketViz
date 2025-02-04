<template>
  <div class="chart-container" ref="chartRef">
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

#additional-chart {
  width: 100%;
  height: 100%;
  min-height: 800px;
}

svg {
  font-family: system-ui, -apple-system, sans-serif;
}

.x-label, .y-label {
  font-size: 14px;
  fill: #475569;
}

.quarter-display {
  font-size: 24px;
  fill: #1e293b;
  font-weight: 600;
}

.bubble circle {
  transition: all 0.3s ease;
}

.bubble:hover circle {
  opacity: 0.9;
  filter: brightness(1.1);
}

.bubble image {
  pointer-events: none;
}

/* Axes styling */
.domain {
  stroke: #cbd5e1;
}

.tick line {
  stroke: #e2e8f0;
}

.tick text {
  fill: #64748b;
  font-size: 12px;
}

/* Grid lines */
.grid line {
  stroke: #e2e8f0;
  stroke-opacity: 0.5;
  shape-rendering: crispEdges;
}

.grid path {
  stroke-width: 0;
}

/* Quadrant labels */
.quadrant-label {
  font-size: 12px;
  fill: #94a3b8;
  text-anchor: middle;
}

/* Animation controls */
.controls {
  display: none;
}

.control-button {
  display: none;
}

/* Tooltip */
.tooltip {
  position: absolute;
  padding: 8px 12px;
  background: white;
  border-radius: 6px;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  font-size: 14px;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.tooltip.visible {
  opacity: 1;
}

.tooltip-company {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4px;
}

.tooltip-data {
  color: #64748b;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

/* Legend */
.legend {
  position: absolute;
  top: 20px;
  right: 20px;
  background: white;
  padding: 12px;
  border-radius: 8px;
  box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
}

.legend-title {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-label {
  font-size: 12px;
  color: #64748b;
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

/* Slider container */
.slider-container {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 80%;
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  z-index: 1000; /* Ensure slider is above chart */
}

.slider-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.slider-title {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.slider-value {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
}

/* Custom slider styling */
input[type="range"] {
  -webkit-appearance: none;
  width: 100%;
  height: 4px;
  border-radius: 2px;
  background: #e2e8f0;
  outline: none;
  margin: 10px 0;
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}

input[type="range"]::-webkit-slider-thumb:hover {
  background: #2563eb;
  transform: scale(1.1);
}

input[type="range"]::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}

input[type="range"]::-moz-range-thumb:hover {
  background: #2563eb;
  transform: scale(1.1);
}

.logo {
  cursor: move;
  user-select: none;
}
</style>

<script setup>
import { onMounted, onUnmounted, ref, computed } from 'vue';
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
import ALMOSAFER_LOGO from '/logos/Almosafer_logo.png'
import OTA_LOGO from '/logos/OTA_logo.png'

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
  'Almosafer': ALMOSAFER_LOGO,
  'Webjet OTA': OTA_LOGO
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

const currentYearIndex = ref(0);
const years = ref([]);
const mergedData = ref([]);

// Add emit definition
const emit = defineEmits(['data-update', 'company-select', 'quarters-loaded']);

// Add these as component-level variables to maintain consistent scales
let xScale, yScale;
let globalXDomain = [-0.5, 0.8];  // EBITDA margin range: -50% to 80%
let globalYDomain = [-0.3, 1.0]; // Revenue growth range: -30% to 100%

// Add chart dimensions
const margin = { top: 50, right: 100, bottom: 50, left: 60 };
const chartRef = ref(null);
let update; // Declare update function reference

// Function to get chart dimensions
const getChartDimensions = () => {
  const container = document.getElementById('additional-chart');
  if (!container) return { width: 800, height: 600 };
  return {
    width: container.clientWidth,
    height: container.clientHeight
  };
};

// Function to process XLSX data
const processExcelData = (file) => {
  console.log('Starting to process Excel file:', file.name);
  const reader = new FileReader();
  
  reader.onload = async (e) => {
    try {
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
      console.log('First row (headers):', jsonData[0]);
      
      // Get headers (company names) from first row, skip first column
      const headers = jsonData[0].slice(1).map(h => h ? h.trim() : null).filter(Boolean);
      console.log('Processed headers:', headers);
      
      // Find EBITDA Margin row
      const ebitdaStartIndex = jsonData.findIndex(row => 
        row && row[0] && String(row[0]).toLowerCase().includes('ebitda margin')
      );
      
      if (ebitdaStartIndex === -1) {
        throw new Error('EBITDA Margin row not found');
      }
      
      // Process data rows
      const processedData = [];
      const quarters = new Set();
      
      // Log the data structure
      console.log('Data structure check:', {
        totalRows: jsonData.length,
        ebitdaStartIndex,
        firstDataRow: jsonData[1],
        firstEbitdaRow: jsonData[ebitdaStartIndex + 1]
      });
      
      // Process rows between headers and EBITDA row
      let currentYear = null;
      let quarterCount = 0;
      
      for (let i = 1; i < ebitdaStartIndex; i++) {
        const row = jsonData[i];
        
        if (!row || !row[0]) {
          console.log(`Skipping row ${i}: Empty row`);
          continue;
        }
        
        // Get year from first column
        const year = String(row[0]).trim();
        if (!year || year === 'Revenue Growth YoY') {
          console.log(`Skipping row ${i}: Invalid year or header row`);
          continue;
        }
        
        // Reset quarter count when year changes
        if (year !== currentYear) {
          currentYear = year;
          quarterCount = 1;
        } else {
          quarterCount++;
        }
        
        // Get corresponding EBITDA row
        const ebitdaRow = jsonData[ebitdaStartIndex + (i - 1)];
        if (!ebitdaRow) {
          console.log(`Skipping row ${i}: No corresponding EBITDA row`);
          continue;
        }
        
        // Check if the row has any valid data
        let hasAnyData = false;
        for (let j = 1; j < row.length; j++) {
          if (row[j] !== undefined && row[j] !== null && row[j] !== '') {
            hasAnyData = true;
            break;
          }
        }
        
        if (!hasAnyData) {
          console.log(`Skipping row ${i}: No data in row`);
          continue;
        }
        
        const quarter = `${year}'Q${quarterCount}`;
        
        let hasValidData = false;
        let rowData = [];
        
        // Process each company's data
        headers.forEach((company, j) => {
          const colIndex = j + 1;
          const revenueGrowth = parseFloat(row[colIndex]);
          const ebitdaMargin = parseFloat(ebitdaRow[colIndex]);
          
          if (!isNaN(revenueGrowth) && !isNaN(ebitdaMargin)) {
            const dataPoint = {
              quarter,
              company,
              revenueGrowth: revenueGrowth / 100,
              ebitdaMargin: ebitdaMargin / 100,
              hasBothQuarters: true
            };
            processedData.push(dataPoint);
            rowData.push(dataPoint);
            hasValidData = true;
          }
        });
        
        if (hasValidData) {
          quarters.add(quarter);
          console.log(`Processed ${quarter}: ${rowData.length} valid data points`);
        } else {
          console.log(`No valid data for ${quarter}`);
        }
      }
      
      console.log('Final processed data:', {
        totalQuarters: quarters.size,
        quarters: Array.from(quarters).sort(),
        totalDataPoints: processedData.length,
        sampleData: processedData.slice(0, 5)
      });
      
      if (processedData.length === 0) {
        throw new Error('No valid data points found');
      }
      
      // Sort quarters chronologically
      const sortedQuarters = Array.from(quarters).sort((a, b) => {
        // Parse YYYY'QN format
        const [yearA, quarterA] = a.split("'");
        const [yearB, quarterB] = b.split("'");
        
        // Compare years first
        const yearDiff = parseInt(yearA) - parseInt(yearB);
        if (yearDiff !== 0) return yearDiff;
        
        // If years are same, compare quarters (Q1, Q2, Q3, Q4)
        return parseInt(quarterA.substring(1)) - parseInt(quarterB.substring(1));
      });
      
      // Update data
      years.value = sortedQuarters;
      mergedData.value = processedData;
      currentYearIndex.value = years.value.length - 1; // Start from the latest quarter
      
      // Emit quarters loaded event
      emit('quarters-loaded', {
        quarters: years.value,
        currentIndex: currentYearIndex.value
      });

      // Initialize chart
      console.log('Initializing chart with:', {
        quarters: years.value,
        currentIndex: currentYearIndex.value,
        dataPoints: mergedData.value.length
      });
      initChart();
      update(currentYearIndex.value);  // Initial update
      
    } catch (error) {
      console.error('Error processing Excel file:', error);
      console.error('Error stack:', error.stack);
      alert('处理数据时出错：' + error.message);
    }
  };
  
  reader.onerror = (error) => {
    console.error('Error reading file:', error);
    console.error('Error stack:', error.stack);
    alert('读取文件时出错');
  };
  
  reader.readAsArrayBuffer(file);
};

// Add computed property for current quarter display
const currentQuarter = computed(() => {
  if (!years.value.length) return '';
  return years.value[currentYearIndex.value];
});

// Handle slider change
const handleSliderChange = (event) => {
  currentYearIndex.value = parseInt(event.target.value);
  if (update) update(currentYearIndex.value);
};

// Add save chart function
const saveChart = async () => {
  try {
    const svgNode = document.querySelector('#additional-chart svg');
    const svgWidth = svgNode.viewBox.baseVal.width || 1200;
    const svgHeight = svgNode.viewBox.baseVal.height || 840;
    
    // First, load all images
    const images = svgNode.querySelectorAll('image');
    await Promise.all(Array.from(images).map(async (image) => {
      try {
        const url = image.getAttribute('href') || image.getAttribute('xlink:href');
        const response = await fetch(url);
        if (!response.ok) throw new Error('Image load failed');
        const blob = await response.blob();
        const base64 = await new Promise((resolve) => {
          const reader = new FileReader();
          reader.onload = () => resolve(reader.result);
          reader.readAsDataURL(blob);
        });
        image.setAttribute('href', base64);
      } catch (error) {
        image.remove();
      }
    }));
    
    const svgData = new XMLSerializer().serializeToString(svgNode);
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();
    
    // Set ultra-high resolution scale
    const scale = 8;  // Increased from 4 to 8 for maximum quality
    canvas.width = svgWidth * scale;
    canvas.height = svgHeight * scale;
    
    // Enable maximum quality image rendering
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';
    
    // Set white background
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Set image source with proper SVG dimensions
    const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
    const svgUrl = URL.createObjectURL(svgBlob);
    
    return new Promise((resolve, reject) => {
      img.onload = () => {
        try {
          ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
          URL.revokeObjectURL(svgUrl);
          
          // Convert to PNG and download
          const link = document.createElement('a');
          link.download = `market_performance_${years.value[currentYearIndex.value]}.png`;
          link.href = canvas.toDataURL('image/png');
          link.click();
          resolve();
        } catch (error) {
          reject(error);
        }
      };
      img.onerror = () => {
        URL.revokeObjectURL(svgUrl);
        reject(new Error('Failed to load SVG'));
      };
      img.src = svgUrl;
    });
  } catch (error) {
    console.error('Error saving chart:', error);
    throw error;
  }
};

// Initialize the chart
const initChart = () => {
  const { width, height } = getChartDimensions();
  console.log('Initializing chart with dimensions:', width, height);
  
  // Clear existing SVG
  d3.select('#additional-chart').selectAll("*").remove();
    
  // Create SVG with viewBox for better scaling
  const svg = d3.select('#additional-chart')
    .append("svg")
    .attr("width", "100%")
    .attr("height", "100%")
    .attr("viewBox", "0 0 1200 840")
    .attr("preserveAspectRatio", "xMidYMid meet");
    
  // Add background
  svg.append("rect")
    .attr("width", "100%")
    .attr("height", "100%")
    .attr("fill", "white");
    
  // Create scales
  xScale = d3.scaleLinear()
    .domain(globalXDomain)
    .range([margin.left, width - margin.right]);

  yScale = d3.scaleLinear()
    .domain(globalYDomain)
    .range([height - margin.bottom, margin.top]);

  // Add axes
  const xAxis = d3.axisBottom(xScale)
    .ticks(8)  // Increased number of ticks
    .tickFormat(d => (d * 100).toFixed(0) + "%");
    
  const yAxis = d3.axisLeft(yScale)
    .ticks(8)  // Increased number of ticks
    .tickFormat(d => (d * 100).toFixed(0) + "%");
    
  svg.append("g")
    .attr("transform", `translate(0,${height - margin.bottom})`)
    .call(xAxis);

  svg.append("g")
    .attr("transform", `translate(${margin.left},0)`)
    .call(yAxis);

  // Add labels
  svg.append("text")
    .attr("class", "x-label")
    .attr("text-anchor", "middle")
    .attr("x", width / 2)
    .attr("y", height - 10)
    .text("EBITDA Margin (%)");
    
  svg.append("text")
    .attr("class", "y-label")
    .attr("text-anchor", "middle")
    .attr("transform", "rotate(-90)")
    .attr("x", -height / 2)
    .attr("y", 15)
    .text("Revenue Growth YoY (%)");
    
    /* Remove quarter display
    const quarterDisplay = svg.append("text")
      .attr("class", "quarter-display")
      .attr("x", width - margin.right)
      .attr("y", margin.top)
      .attr("text-anchor", "end")
      .attr("font-size", "24px")
      .attr("font-weight", "bold");
    */
    
    // Add tooltip
    const tooltip = d3.select(chartRef.value)
      .append("div")
      .attr("class", "tooltip");

    // Define update function
    update = (quarterIndex) => {
      console.log('Updating chart for quarter:', years.value[quarterIndex]);
      
      // Filter data for current quarter
      const currentData = mergedData.value.filter(d => d.quarter === years.value[quarterIndex]);
      console.log('Current quarter data:', currentData);
      
      // Emit the current data
      emit('data-update', currentData);
      
      // Update bubbles
      const bubbles = svg.selectAll(".bubble")
        .data(currentData, d => d.company);
        
      // Remove old bubbles
      bubbles.exit().remove();
      
      // Add new bubbles
      const bubblesEnter = bubbles.enter()
        .append("g")
        .attr("class", "bubble")
        .attr("transform", d => `translate(${xScale(d.ebitdaMargin)},${yScale(d.revenueGrowth)})`)
        .style("cursor", "pointer")
        .on("click", (event, d) => {
          // Emit company selection event
          emit('company-select', d);
        });

      // Update bubble and logo sizes
      bubblesEnter.append("circle")
        .attr("r", 6)
        .attr("fill", d => colorDict[d.company] || "#64748b")
        .attr("stroke", "white")
        .attr("stroke-width", "2px")
        .attr("opacity", 0.8);

      // Create a group for the logo to make dragging more stable
      const logoGroups = bubblesEnter.append("g")
        .attr("class", "logo-group")
        .style("cursor", "move");

      // Add the logo image
      const logoSize = 96;
      logoGroups.append("image")
        .attr("class", "logo")
        .attr("xlink:href", d => logoDict[d.company] || "")
        .attr("x", -logoSize/2)
        .attr("y", -logoSize/2)
        .attr("width", logoSize)
        .attr("height", logoSize)
        .style("pointer-events", "auto");

      // Add invisible background rect to make dragging easier
      logoGroups.insert("rect", "image")
        .attr("class", "logo-hit-area")
        .attr("x", -logoSize/2)
        .attr("y", -logoSize/2)
        .attr("width", logoSize)
        .attr("height", logoSize)
        .attr("fill", "transparent");

      // Apply drag behavior to the logo groups
      logoGroups.call(d3.drag()
        .on("start", function() {
          d3.select(this).raise();
        })
        .on("drag", function(event) {
          const dx = event.dx;
          const dy = event.dy;
          
          // Update both rect and image positions
          const currentX = parseFloat(d3.select(this).select('image').attr('x'));
          const currentY = parseFloat(d3.select(this).select('image').attr('y'));
          
          d3.select(this).select('rect')
            .attr('x', currentX + dx)
            .attr('y', currentY + dy);
            
          d3.select(this).select('image')
            .attr('x', currentX + dx)
            .attr('y', currentY + dy);
        }));

      // Update existing bubbles with transition
      bubbles.transition()
        .duration(1000)
        .attr("transform", d => `translate(${xScale(d.ebitdaMargin)},${yScale(d.revenueGrowth)})`);

      // Add zero lines
      const zeroLines = svg.selectAll(".zero-line").data([
        { x1: xScale(0), y1: 0, x2: xScale(0), y2: height - margin.bottom },
        { x1: margin.left, y1: yScale(0), x2: width - margin.right, y2: yScale(0) }
      ]);
      
      zeroLines.enter()
        .append("line")
        .attr("class", "zero-line")
        .merge(zeroLines)
        .attr("x1", d => d.x1)
        .attr("y1", d => d.y1)
        .attr("x2", d => d.x2)
        .attr("y2", d => d.y2)
        .attr("stroke", "#4e843d")
        .attr("stroke-dasharray", "4,4")
        .attr("opacity", 0.5);
    };

    // Initial update
    if (years.value.length > 0) {
      update(currentYearIndex.value);
    }
};

// Expose methods
defineExpose({
  processExcelData,
  saveChart,
  currentYearIndex,
  handleSliderChange: () => {
    if (update) update(currentYearIndex.value);
  }
});
</script> 