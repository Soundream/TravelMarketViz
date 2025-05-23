// Global variables
let isPlaying = true;
let playInterval;
let currentYearIndex = 0;
let years = Array.from({length: 2026 - 2010 + 1}, (_, i) => 2010 + i);
let timeline;

// Function to create timeline
function createTimeline() {
    const timelineWidth = document.getElementById('timeline').offsetWidth;
    const margin = { left: 80, right: 80 };
    const width = timelineWidth - margin.left - margin.right;

    // Create SVG
    const svg = d3.select('#timeline')
        .append('svg')
        .attr('width', timelineWidth)
        .attr('height', 60);

    const g = svg.append('g')
        .attr('transform', `translate(${margin.left}, 30)`);

    // Create scale
    const xScale = d3.scaleLinear()
        .domain([2010, 2026])
        .range([0, width]);

    // Create axis
    const xAxis = d3.axisBottom(xScale)
        .tickFormat(d => d.toString())
        .ticks(years.length)
        .tickValues(years);

    // Add axis
    g.append('g')
        .attr('class', 'timeline-axis')
        .call(xAxis)
        .selectAll('text')
        .style('text-anchor', 'middle')
        .style('font-family', 'Monda')
        .style('font-size', '18px');

    // Make timeline ticks more visible
    g.selectAll('.tick line')
        .style('stroke', '#ccc')
        .style('stroke-width', '1px')
        .attr('y2', '8');

    // Add triangle marker
    const triangle = g.append('path')
        .attr('d', d3.symbol().type(d3.symbolTriangle).size(100))
        .attr('fill', '#4CAF50')
        .attr('transform', `translate(${xScale(years[currentYearIndex])}, -10) rotate(180)`);

    timeline = {
        scale: xScale,
        triangle: triangle
    };
}

// Function to update timeline
function updateTimeline(year) {
    if (timeline && timeline.triangle) {
        timeline.triangle
            .transition()
            .duration(500)
            .attr('transform', `translate(${timeline.scale(year)}, -10) rotate(180)`);
    }
}

// Initialize the visualization
function init() {
    try {
        currentYearIndex = 0;
        createTimeline();
        
        // Optimized animation loop
        setTimeout(() => {
            isPlaying = true;
            let startTime = null;
            const animationDuration = 335500; // Adjusted: 27 years, keep per-year speed same as before
            const frameInterval = 50; // Limit updates to every 50ms (20fps)
            let lastUpdateTime = 0;
            
            function animate(currentTime) {
                if (!isPlaying) return;
                
                if (!startTime) startTime = currentTime;
                const now = currentTime;
                
                // Limit frame rate
                if (now - lastUpdateTime < frameInterval) {
                    requestAnimationFrame(animate);
                    return;
                }
                
                const elapsed = (now - startTime) % animationDuration;
                const progress = elapsed / animationDuration;
                const indexFloat = progress * (years.length - 1);
                const currentIndex = Math.floor(indexFloat);
                
                // Update timeline marker
                if (timeline && timeline.triangle) {
                    const currentYear = years[currentIndex];
                    const nextYear = years[Math.min(currentIndex + 1, years.length - 1)];
                    const yearProgress = indexFloat - currentIndex;
                    const currentX = timeline.scale(currentYear);
                    const nextX = timeline.scale(nextYear);
                    const interpolatedX = currentX + (nextX - currentX) * yearProgress;
                    timeline.triangle.attr('transform', `translate(${interpolatedX}, -10) rotate(180)`);
                }
                
                lastUpdateTime = now;
                requestAnimationFrame(animate);
            }
            
            requestAnimationFrame(animate);
        }, 500);
        
    } catch (error) {
        console.error('Error initializing visualization:', error);
        document.getElementById('timeline').innerHTML = `
            <div style="color: red; padding: 20px;">
                Error loading visualization: ${error.message}<br>
                Please check the browser console for more details.
            </div>
        `;
    }
}

// Start the visualization when the page loads
document.addEventListener('DOMContentLoaded', init); 