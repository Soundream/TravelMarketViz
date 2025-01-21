<template>
  <div class="chart-container">
    <div class="flex justify-end mb-4">
      <button 
        @click="saveChart"
        class="px-4 py-2 bg-wego-green text-white rounded hover:bg-wego-green-dark flex items-center gap-2"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path d="M7.707 10.293a1 1 0 10-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 11.586V6h-2v5.586l-1.293-1.293z" />
          <path d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" />
        </svg>
        Save Chart
      </button>
    </div>
    <div id="static-chart" class="w-full h-full"></div>
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

.logo {
  cursor: move;
  user-select: none;
}
</style>

<script setup>
import { onMounted, ref } from 'vue';
import * as d3 from 'd3';
import * as XLSX from 'xlsx';

// Company colors and logos (reuse from AnimatedBubbleChart)
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

let chartData = ref([]);

// Fixed domains for consistent scaling
const globalXDomain = [-0.7, 1.2];  // EBITDA margin range
const globalYDomain = [-0.3, 1.2];  // Revenue growth range

// Add state to store adjusted positions
const logoPositions = ref({});

// Add drag behavior function
const createDragBehavior = (xScale, yScale) => {
  return d3.drag()
    .on('drag', (event, d) => {
      const logo = d3.select(event.sourceEvent.target);
      const newX = parseFloat(logo.attr('x')) + event.dx;
      const newY = parseFloat(logo.attr('y')) + event.dy;
      
      logo.attr('x', newX)
          .attr('y', newY);
      
      // Store the adjusted position
      logoPositions.value[d.company] = { x: newX, y: newY };
    });
};

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
    
    // Process data for 2024Q3
    const processedData = [];
    const targetQuarter = '2024\'Q3';
    
    // Find the row index for 2024Q3
    const q3RowIndex = jsonData.findIndex(row => row[0] === targetQuarter);
    const q3MarginRowIndex = jsonData.findIndex((row, index) => index > 115 && row[0] === targetQuarter);
    
    if (q3RowIndex !== -1 && q3MarginRowIndex !== -1) {
      const revenueGrowthRow = jsonData[q3RowIndex];
      const ebitdaMarginRow = jsonData[q3MarginRowIndex];
      
      // Process each company's data
      headers.forEach((company, index) => {
        if (!company || index === 0) return;
        
        const revenueGrowth = revenueGrowthRow[index];
        const ebitdaMargin = ebitdaMarginRow[index];
        
        if (revenueGrowth !== undefined && ebitdaMargin !== undefined &&
            revenueGrowth >= globalYDomain[0] && revenueGrowth <= globalYDomain[1] &&
            ebitdaMargin >= globalXDomain[0] && ebitdaMargin <= globalXDomain[1]) {
          
          processedData.push({
            company: company,
            ebitdaMargin: ebitdaMargin,
            revenueGrowth: revenueGrowth
          });
        }
      });
    }

    // Update chart data and redraw
    chartData.value = processedData;
    initChart();
  };
  reader.readAsArrayBuffer(file);
};

// Initialize chart
const initChart = () => {
  try {
    // Clear previous chart
    d3.select('#static-chart').selectAll('*').remove();
    
    // Create SVG
    const svg = d3.select('#static-chart').append('svg')
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
    const xScale = d3.scaleLinear()
      .domain(globalXDomain)
      .range([0, width]);

    const yScale = d3.scaleLinear()
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

    // Add bubbles and logos
    chartData.value.forEach(d => {
      // Check if logo exists for this company
      if (logoDict[d.company]) {
        // Add company logo with error handling
        const img = new Image();
        img.onload = () => {
          // Calculate initial position
          const initialX = xScale(d.ebitdaMargin) - 40;
          const initialY = yScale(d.revenueGrowth) - 40;
          
          // Use stored position if available
          const storedPosition = logoPositions.value[d.company];
          const x = storedPosition ? storedPosition.x : initialX;
          const y = storedPosition ? storedPosition.y : initialY;
          
          // Add the logo
          g.append('image')
            .datum(d)  // Attach data to the element
            .attr('class', 'logo')
            .attr('width', 80)
            .attr('height', 80)
            .attr('xlink:href', logoDict[d.company])
            .attr('x', x)
            .attr('y', y)
            .style('cursor', 'move')
            .call(createDragBehavior(xScale, yScale));
          
          // Store initial position if not already stored
          if (!logoPositions.value[d.company]) {
            logoPositions.value[d.company] = { x: initialX, y: initialY };
          }
        };
        img.src = logoDict[d.company];
      }
    });

  } catch (error) {
    console.error('Error initializing chart:', error);
  }
};

// Add save chart function
const saveChart = async () => {
  try {
    const svgNode = document.querySelector('#static-chart svg');
    
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
        // If image fails to load, remove it from the SVG
        image.remove();
      }
    }));
    
    const svgData = new XMLSerializer().serializeToString(svgNode);
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();
    
    // Set canvas size to match SVG
    canvas.width = 1200;
    canvas.height = 840;
    
    img.onload = () => {
      // Fill white background
      ctx.fillStyle = 'white';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      // Draw the image
      ctx.drawImage(img, 0, 0);
      
      // Create download link
      const link = document.createElement('a');
      link.download = '2024Q3_Market_Performance.png';
      link.href = canvas.toDataURL('image/png');
      link.click();
    };
    
    img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgData)));
  } catch (error) {
    console.error('Error saving chart:', error);
  }
};

// Expose methods
defineExpose({
  processExcelData,
  saveChart
});
</script> 