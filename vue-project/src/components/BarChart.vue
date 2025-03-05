<template>
  <div class="bg-white rounded-lg shadow-lg p-6 mb-8">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl font-semibold text-wego-gray">Bar Chart Analysis</h2>
      <div class="flex items-center gap-4">
        <Popover class="relative">
          <PopoverButton class="inline-flex items-center gap-x-1 text-sm/6 font-semibold text-gray-900 px-4 py-2 bg-gray-50 rounded-lg hover:bg-gray-100">
            <span>{{ currentPeriod || 'Select Quarter' }}</span>
            <ChevronDownIcon class="size-5" aria-hidden="true" />
          </PopoverButton>

          <transition 
            enter-active-class="transition ease-out duration-200" 
            enter-from-class="opacity-0 translate-y-1" 
            enter-to-class="opacity-100 translate-y-0" 
            leave-active-class="transition ease-in duration-150" 
            leave-from-class="opacity-100 translate-y-0" 
            leave-to-class="opacity-0 translate-y-1"
          >
            <PopoverPanel class="absolute left-1/2 z-10 mt-5 flex w-screen max-w-min -translate-x-1/2 px-4">
              <div class="w-48 shrink rounded-xl bg-white p-4 text-sm/6 font-semibold text-gray-900 shadow-lg ring-1 ring-gray-900/5 max-h-80 overflow-y-auto">
                <a 
                  v-for="period in periods.slice().reverse()" 
                  :key="period"
                  href="#"
                  @click.prevent="selectPeriod(period)"
                  class="block p-2 hover:text-wego-green"
                  :class="{ 'text-wego-green': currentPeriod === period }"
                >
                  {{ period }}
                </a>
              </div>
            </PopoverPanel>
          </transition>
        </Popover>
        <!-- <button 
          @click="saveChart"
          class="px-4 py-2 bg-wego-green text-white rounded hover:bg-wego-green-dark flex items-center gap-2"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path d="M7.707 10.293a1 1 0 10-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 11.586V6h-2v5.586l-1.293-1.293z" />
            <path d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" />
          </svg>
          Save Chart
        </button> -->
      </div>
    </div>
    <div ref="chartContainer" class="h-[840px]"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { Popover, PopoverButton, PopoverPanel } from '@headlessui/vue'
import { ChevronDownIcon } from '@heroicons/vue/20/solid'
import * as d3 from 'd3'
import Papa from 'papaparse'

const chartContainer = ref(null)
const chartData = ref([])
const periods = ref([])
const currentPeriodIndex = ref(0)
const currentPeriod = ref('')

// Company colors mapping
const companyColors = {
  'BKNG': '#2557A7',  // Booking Holdings - Dark Blue
  'EXPE': '#00A4BB',  // Expedia - Teal
  'TCOM': '#003580',  // Trip.com - Navy Blue
  'ABNB': '#FF5A5F',  // Airbnb - Coral Red
  'TRIP': '#34E0A1',  // TripAdvisor - Mint Green
  'TRVG': '#007FAD',  // Trivago - Light Blue
  'EDR': '#FF6B6B',   // eDreams - Coral
  'DESP': '#4A90E2',  // Despegar - Sky Blue
  'MMYT': '#F5A623',  // MakeMyTrip - Orange
  'Ixigo': '#7ED321',  // Ixigo - Green
  'SEERA': '#9013FE',  // Seera - Purple
  'Webjet': '#4A4A4A',  // Webjet - Dark Gray
  'LMN': '#50E3C2',    // Lastminute - Turquoise
  'Yatra': '#B8E986',  // Yatra - Light Green
  'Orbitz': '#F5A623',  // Orbitz - Orange
  'Travelocity': '#D0021B',  // Travelocity - Red
  'EaseMyTrip': '#417505',  // EaseMyTrip - Dark Green
  'Wego': '#10B981',   // Wego - Original Green
  'Skyscanner': '#0770E3',  // Skyscanner - Blue
  'Etraveli': '#BD10E0',  // Etraveli - Purple
  'Kiwi': '#00A651',   // Kiwi - Green
  'Cleartrip': '#1BA0E2',  // Cleartrip - Light Blue
  'FLT': '#D35400',    // Flight Centre - Orange
  'Almosafer': '#8E44AD',  // Almosafer - Purple
  'Webjet OTA': '#2C3E50'  // Webjet OTA - Dark Blue
}

// Default color for companies without specific colors
const defaultColor = '#10B981'  // Wego green as default

// Function to get color for a company
const getCompanyColor = (company) => companyColors[company] || defaultColor

// Company names mapping (reuse from App.vue)
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
}

const importFromGoogleSheet = async () => {
  // Google Sheets ID and GID for bar chart data
  const sheetId = '2PACX-1vQYwQTSYwig7AZ0fjPniLVfUUJnLz3PP4f4fBtqkBNPYqrkKtQyZDaB99kHk2eCzuCh5i8oxTPCHeQ9'
  const gid = '621483928'
  const sheetUrl = `https://docs.google.com/spreadsheets/d/e/${sheetId}/pub?gid=${gid}&output=csv`
  
  try {
    console.log('Starting Google Sheet import for bar chart...')
    console.log('Sheet URL:', sheetUrl)
    
    const response = await fetch(sheetUrl)
    console.log('Response status:', response.status)
    
    if (!response.ok) {
      throw new Error(`Failed to fetch data: ${response.status} ${response.statusText}`)
    }
    
    const csvText = await response.text()
    console.log('CSV Text length:', csvText.length)
    console.log('First 100 chars of CSV:', csvText.substring(0, 100))
    
    const parsedData = Papa.parse(csvText, { 
      header: true,
      skipEmptyLines: true,
      transformHeader: (header) => header.trim()
    })
    
    console.log('Parsed data rows:', parsedData.data.length)
    console.log('Sample parsed data:', parsedData.data.slice(0, 2))
    
    if (parsedData.errors.length > 0) {
      console.warn('Parse errors:', parsedData.errors)
    }
    
    // Process the data
    chartData.value = processData(parsedData.data)
    console.log('Processed chart data:', chartData.value.slice(0, 2))
    
    periods.value = [...new Set(chartData.value.map(d => d.period))]
    console.log('Available periods:', periods.value)
    
    currentPeriod.value = periods.value[currentPeriodIndex.value]
    console.log('Current period:', currentPeriod.value)
    
    // Initial render
    console.log('Calling renderChart...')
    renderChart()
  } catch (error) {
    console.error('Error importing from Google Sheet:', error)
  }
}

const processData = (rawData) => {
  // Transform the data into the format needed for the bar chart
  const result = [];
  
  console.log('Processing raw data:', {
    totalRows: rawData.length,
    firstRow: rawData[0],
    secondRow: rawData[1]
  });
  
  // Skip the first row (headers)
  for (let i = 1; i < rawData.length; i++) {
    const row = rawData[i];
    const period = row[''];  // Empty string is the period column
    
    // Skip the "Revenue" row
    if (period === 'Revenue') {
      console.log('Skipping Revenue row:', row);
      continue;
    }
    
    // Process each company's data
    Object.entries(row).forEach(([company, value]) => {
      // Skip the period column and empty values
      if (company === '' || !value || value === '') return;
      
      // Clean up the value string and convert to number
      const cleanValue = value.toString().trim().replace(/[$,\s]/g, '');
      const numValue = parseFloat(cleanValue);
      
      if (!isNaN(numValue) && numValue > 0) {
        result.push({
          period,
          company,
          value: numValue
        });
      } else {
        console.log(`Skipping invalid value for ${company} in ${period}:`, value);
      }
    });
  }
  
  console.log('Processed data summary:', {
    totalItems: result.length,
    uniquePeriods: [...new Set(result.map(d => d.period))],
    uniqueCompanies: [...new Set(result.map(d => d.company))],
    sample: result.slice(0, 5)
  });
  
  return result;
}

const renderChart = () => {
  console.log('renderChart called')
  if (!chartContainer.value) {
    console.error('Chart container not found')
    return
  }
  
  // Clear previous chart
  d3.select(chartContainer.value).selectAll('*').remove()
  
  // Filter data for current period
  const currentData = chartData.value
    .filter(d => d.period === periods.value[currentPeriodIndex.value])
    .sort((a, b) => b.value - a.value)
    .slice(0, 15) // Show top 15 companies
  
  if (currentData.length === 0) {
    console.warn('No data available for current period')
    d3.select(chartContainer.value)
      .append('div')
      .attr('class', 'text-center py-8 text-gray-500')
      .text('No data available for this period')
    return
  }
  
  // Set up dimensions with more space for logos
  const margin = { top: 20, right: 160, bottom: 40, left: 250 } // Increased right margin for larger logos
  const width = chartContainer.value.clientWidth - margin.left - margin.right
  const height = chartContainer.value.clientHeight - margin.top - margin.bottom
  
  // Create SVG with explicit dimensions
  const svg = d3.select(chartContainer.value)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)
  
  // Set up scales
  const x = d3.scaleLinear()
    .domain([0, d3.max(currentData, d => d.value) * 1.1]) // Add 10% padding
    .range([0, width])
  
  // Set fixed spacing between bars
  const fixedBarSpacing = 20 // Fixed spacing between bars
  const barHeight = 36 // Bar height
  
  // Calculate total height needed
  const totalHeight = (barHeight + fixedBarSpacing) * currentData.length - fixedBarSpacing
  
  // Set up scales with fixed spacing
  const y = d3.scaleBand()
    .domain(currentData.map(d => d.company))
    .range([0, totalHeight])
    .padding(0) // No padding as we're manually controlling spacing
  
  // Adjust SVG height to match total height needed
  const svgHeight = totalHeight + margin.top + margin.bottom
  
  // Update SVG height
  d3.select(chartContainer.value)
    .select('svg')
    .attr('height', svgHeight)
  
  // Update bar positions with fixed spacing
  const bars = svg.selectAll('rect')
    .data(currentData)
    .enter()
    .append('rect')
    .attr('y', (d, i) => i * (barHeight + fixedBarSpacing))
    .attr('height', barHeight)
    .attr('x', 0)
    .attr('width', d => x(d.value))
    .attr('fill', d => getCompanyColor(d.company))
    .attr('rx', 6)
    .attr('ry', 6)
    .style('opacity', 0.85)
    .style('filter', 'drop-shadow(0 1px 2px rgb(0 0 0 / 0.1))')

  // Update other elements positions
  const tickers = svg.selectAll('.ticker-label')
    .data(currentData)
    .enter()
    .append('text')
    .attr('class', 'ticker-label')
    .attr('x', -10)
    .attr('y', (d, i) => i * (barHeight + fixedBarSpacing) + barHeight / 2 - 8)
    .attr('dy', '0.35em')
    .attr('text-anchor', 'end')
    .style('font-size', '15px')
    .style('font-weight', 'bold')
    .attr('fill', '#111827')
    .text(d => d.company)
  
  const companyLabels = svg.selectAll('.company-label')
    .data(currentData)
    .enter()
    .append('text')
    .attr('class', 'company-label')
    .attr('x', -10)
    .attr('y', (d, i) => i * (barHeight + fixedBarSpacing) + barHeight / 2 + 12)
    .attr('dy', '0.35em')
    .attr('text-anchor', 'end')
    .style('font-size', '13px')
    .attr('fill', '#6B7280')
    .text(d => companyNames[d.company] || d.company)
  
  const valueLabels = svg.selectAll('.value-label')
    .data(currentData)
    .enter()
    .append('text')
    .attr('class', 'value-label')
    .attr('x', d => x(d.value) + 5)
    .attr('y', (d, i) => i * (barHeight + fixedBarSpacing) + barHeight / 2)
    .attr('dy', '0.35em')
    .text(d => d3.format(',.0f')(d.value))
    .attr('fill', '#6B7280')
    .style('font-size', '13px')
  
  const logoSize = 120
  const logos = svg.selectAll('.company-logo')
    .data(currentData)
    .enter()
    .append('image')
    .attr('class', 'company-logo')
    .attr('x', d => x(d.value) + 60)
    .attr('y', (d, i) => i * (barHeight + fixedBarSpacing) + (barHeight - logoSize) / 2)
    .attr('width', logoSize)
    .attr('height', logoSize)
    .attr('preserveAspectRatio', 'xMidYMid meet')
    .attr('data-company', d => d.company)
    .attr('href', d => `/logos/${d.company}_logo.png`)
    .on('error', function() {
      const element = d3.select(this)
      const company = element.datum().company
      element.attr('href', `/logos/${company}_temp_logo.png`)
        .on('error', function() {
          element.remove()
        })
    })
}

const selectPeriod = (period) => {
  currentPeriod.value = period
  currentPeriodIndex.value = periods.value.indexOf(period)
  renderChart()
}

const saveChart = async () => {
  const svg = chartContainer.value.querySelector('svg')
  if (!svg) return

  try {
    // 创建一个新的 SVG 元素用于导出
    const svgData = new XMLSerializer().serializeToString(svg)
    const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' })
    const URL = window.URL || window.webkitURL || window
    const blobURL = URL.createObjectURL(svgBlob)

    // 创建图片元素并加载 SVG
    const image = new Image()
    image.src = blobURL

    // 等待图片加载完成
    await new Promise((resolve, reject) => {
      image.onload = resolve
      image.onerror = reject
    })

    // 创建 canvas
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    
    // 设置 canvas 尺寸为 SVG 的 2 倍以获得更高的清晰度
    const scale = 2
    canvas.width = svg.clientWidth * scale
    canvas.height = svg.clientHeight * scale
    
    // 设置白色背景
    ctx.fillStyle = 'white'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    
    // 绘制 SVG
    ctx.scale(scale, scale)
    ctx.drawImage(image, 0, 0)

    // 获取所有 logo 图片
    const logoPromises = []
    const logos = svg.querySelectorAll('.company-logo')
    
    logos.forEach((logo) => {
      const logoPromise = new Promise((resolve) => {
        const img = new Image()
        img.crossOrigin = 'anonymous' // 允许跨域加载图片
        img.onload = () => {
          const x = parseFloat(logo.getAttribute('x'))
          const y = parseFloat(logo.getAttribute('y'))
          const width = parseFloat(logo.getAttribute('width'))
          const height = parseFloat(logo.getAttribute('height'))
          
          // 在正确的位置绘制 logo
          ctx.drawImage(img, x * scale, y * scale, width * scale, height * scale)
          resolve()
        }
        img.onerror = () => {
          // 如果主 logo 加载失败，尝试加载临时 logo
          const company = logo.getAttribute('data-company')
          img.src = `/logos/${company}_temp_logo.png`
        }
        img.src = logo.getAttribute('href')
      })
      logoPromises.push(logoPromise)
    })

    // 等待所有 logo 加载完成
    await Promise.all(logoPromises)

    // 转换为 PNG 并下载
    const pngURL = canvas.toDataURL('image/png')
    const downloadLink = document.createElement('a')
    downloadLink.href = pngURL
    downloadLink.download = `bar-chart-${currentPeriod.value}.png`
    document.body.appendChild(downloadLink)
    downloadLink.click()
    document.body.removeChild(downloadLink)

    // 清理
    URL.revokeObjectURL(blobURL)
  } catch (error) {
    console.error('Error saving chart:', error)
  }
}

// Watch for window resize
let resizeTimeout
window.addEventListener('resize', () => {
  clearTimeout(resizeTimeout)
  resizeTimeout = setTimeout(renderChart, 250)
})

// Add watcher for chartData
watch(chartData, (newData) => {
  console.log('chartData changed:', newData.length)
  if (newData.length > 0) {
    renderChart()
  }
})

// Add watcher for currentPeriodIndex
watch(currentPeriodIndex, (newIndex) => {
  console.log('currentPeriodIndex changed:', newIndex)
  currentPeriod.value = periods.value[newIndex]
  renderChart()
})

onMounted(async () => {
  console.log('BarChart component mounted')
  await importFromGoogleSheet()
  
  // Set default period to 2024'Q4
  const defaultPeriod = "2024'Q4"
  if (periods.value.includes(defaultPeriod)) {
    selectPeriod(defaultPeriod)
  }
})
</script>

<style scoped>
/* Add any component-specific styles here */
</style> 