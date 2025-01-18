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
</style>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue';
import * as d3 from 'd3';
import { revenueGrowthData, ebitdaMarginData } from '../data/marketData';

// Company colors
const colorDict = {
  'abnb': '#FF5A5F',
  'bkng': '#003580',
  'expe': '#00355F',
  'tcom': '#003580',
  'sabr': '#E31837',
  'trip': '#34E0A1'
};

// Company logos
const logoDict = {
  'abnb': '/logos/airbnb.png',
  'bkng': '/logos/booking.png',
  'expe': '/logos/expedia.png',
  'tcom': '/logos/trip-com.png',
  'sabr': '/logos/sabre.png',
  'trip': '/logos/tripadvisor.png'
};

// Function to process local data
const processData = () => {
  const merged = [];
  const quarters = ['2024 q2', '2024 q3'];
  const companies = ['abnb', 'bkng', 'expe', 'trip', 'tcom', 'wego'];

  quarters.forEach(quarter => {
    const revenueData = revenueGrowthData.find(d => d.quarter.toLowerCase() === quarter.toLowerCase());
    const ebitdaData = ebitdaMarginData.find(d => d.quarter.toLowerCase() === quarter.toLowerCase());

    if (revenueData && ebitdaData) {
      companies.forEach(company => {
        if (revenueData[company] !== undefined && ebitdaData[company] !== undefined) {
          merged.push({
            company: company,
            quarter: quarter.toLowerCase(),
            revenueGrowth: revenueData[company] / 100,
            ebitdaMargin: ebitdaData[company] / 100,
          });
        }
      });
    }
  });

  return merged;
};

// Initialize chart
const initChart = () => {
  try {
    // Create SVG
    const svg = d3.select('#additional-chart').append('svg')
      .attr('width', 1200)
      .attr('height', 840);

    const margin = { top: 40, right: 20, bottom: 50, left: 60 };
    const width = 1200 - margin.left - margin.right;
    const height = 840 - margin.top - margin.bottom;

    const g = svg.append("g")
      .attr("transform", `translate(${margin.left}, ${margin.top})`);

    let mergedData = processData();
    console.log('Processed Data:', mergedData);

    // Compute min and max values for the scales
    const ebitdaMargins = mergedData.map(d => d.ebitdaMargin);
    const revenueGrowths = mergedData.map(d => d.revenueGrowth);

    const xMin = d3.min(ebitdaMargins);
    const xMax = d3.max(ebitdaMargins);
    const yMin = d3.min(revenueGrowths);
    const yMax = d3.max(revenueGrowths);

    // Add padding to the domains
    const xPadding = (xMax - xMin) * 0.1 || 0.1;
    const yPadding = (yMax - yMin) * 0.1 || 0.1;

    // Adjust the domains to include 0% for x and y axes
    const xDomain = [
      Math.min(xMin - xPadding, 0),
      Math.max(xMax + xPadding, 0)
    ];

    const yDomain = [
      Math.min(yMin - yPadding, 0),
      Math.max(yMax + yPadding, 0)
    ];

    // Create scales
    const xScale = d3.scaleLinear()
      .domain(xDomain)
      .range([0, width]);

    const yScale = d3.scaleLinear()
      .domain(yDomain)
      .range([height, 0]);

    // Create axes
    const xAxis = d3.axisBottom(xScale)
      .tickFormat(d3.format(".0%"));

    const yAxis = d3.axisLeft(yScale)
      .tickFormat(d3.format(".0%"));

    // Draw axes
    g.append("g")
      .attr("class", "x-axis")
      .attr("transform", `translate(0, ${height})`)
      .call(xAxis)
      .selectAll(".tick text")
      .style("font-family", "Open Sans")
      .style("font-size", 14);

    g.append("g")
      .attr("class", "y-axis")
      .call(yAxis)
      .selectAll(".tick text")
      .style("font-family", "Open Sans")
      .style("font-size", 14);

    // Add axis labels
    g.append("text")
      .attr("class", "x-label")
      .attr("text-anchor", "middle")
      .attr("x", width / 2)
      .attr("y", height + 40)
      .text("EBITDA Margin")
      .style("font-family", "Open Sans")
      .style("font-size", 20);

    g.append("text")
      .attr("class", "y-label")
      .attr("text-anchor", "middle")
      .attr("transform", `rotate(-90)`)
      .attr("y", -65)
      .attr("x", -height / 2)
      .attr("dy", "1em")
      .text("Revenue Growth YoY")
      .style("font-family", "Open Sans")
      .style("font-size", 20);

    // Add zero lines
    if (yScale(0) >= 0 && yScale(0) <= height) {
      g.append("line")
        .attr("class", "zero-line")
        .attr("x1", 0)
        .attr("y1", yScale(0))
        .attr("x2", width)
        .attr("y2", yScale(0))
        .attr("stroke", "green")
        .attr("stroke-width", 1)
        .attr("stroke-dasharray", "4,2");
    }

    if (xScale(0) >= 0 && xScale(0) <= width) {
      g.append("line")
        .attr("class", "zero-line")
        .attr("x1", xScale(0))
        .attr("y1", 0)
        .attr("x2", xScale(0))
        .attr("y2", height)
        .attr("stroke", "green")
        .attr("stroke-width", 1)
        .attr("stroke-dasharray", "4,2");
    }

    // Separate data for Q2 and Q3
    const dataQ3 = mergedData.filter(d => d.quarter === '2024 q3');
    const dataQ2 = mergedData.filter(d => d.quarter === '2024 q2');

    // Draw Q3 dots with logos
    const dotsQ3 = g.selectAll(".dot.q3")
      .data(dataQ3)
      .enter()
      .append("circle")
      .attr("class", "dot q3")
      .attr("r", 5)
      .attr("cx", d => xScale(d.ebitdaMargin))
      .attr("cy", d => yScale(d.revenueGrowth))
      .attr("fill", d => colorDict[d.company] || '#000000');

    // Draw Q2 crosses
    const symbolCross = d3.symbol().type(d3.symbolCross).size(100);

    const crossesQ2 = g.selectAll(".cross.q2")
      .data(dataQ2)
      .enter()
      .append("path")
      .attr("class", "cross q2")
      .attr("d", symbolCross)
      .attr("transform", d => `translate(${xScale(d.ebitdaMargin)},${yScale(d.revenueGrowth)})`)
      .attr("fill", d => colorDict[d.company] || '#000000');

    // Add quarter labels
    g.selectAll(".quarter-label")
      .data(mergedData)
      .enter()
      .append("text")
      .attr("class", "quarter-label")
      .text(d => d.quarter.toUpperCase().replace('2024 ', ''))
      .attr("x", d => xScale(d.ebitdaMargin) + 8)
      .attr("y", d => yScale(d.revenueGrowth) + 4)
      .style("font-size", "12px")
      .style("font-family", "Open Sans")
      .style("fill", "black");

    // Add company logos for Q3 data
    g.selectAll(".logo")
      .data(dataQ3)
      .enter()
      .append("image")
      .attr("class", "logo")
      .attr("xlink:href", d => logoDict[d.company] || '')
      .attr("width", 80)
      .attr("height", 80)
      .attr("x", d => xScale(d.ebitdaMargin) - 40)
      .attr("y", d => yScale(d.revenueGrowth) - 62);

  } catch (error) {
    console.error('Error initializing chart:', error);
  }
};

// Lifecycle hooks
onMounted(() => {
  initChart();
});

onUnmounted(() => {
  // Cleanup
  d3.select('#additional-chart').selectAll('*').remove();
});
</script> 