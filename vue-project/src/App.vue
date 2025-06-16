<template>
  <header class="absolute inset-x-0 top-0 z-50 flex h-16 border-b border-gray-900/10">
    <div class="mx-auto flex w-full max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
      <div class="flex flex-1 items-center gap-x-6">
        <button type="button" class="-m-3 p-3 md:hidden" @click="mobileMenuOpen = true">
          <span class="sr-only">Open main menu</span>
          <Bars3Icon class="size-5 text-wego-gray" aria-hidden="true" />
        </button>
        <div class="flex items-center gap-x-4">
          <img class="h-8 w-auto" :src="WEGO_LOGO" alt="Wego" />
          <span class="text-wego-gray font-semibold text-lg px-2">|</span>
          <span class="text-wego-gray font-semibold">Strategy team</span>
        </div>
      </div>
      <nav class="hidden md:flex md:gap-x-11 md:text-sm/6 md:font-semibold md:text-wego-gray">
        <a v-for="(item, itemIdx) in navigation" 
           :key="itemIdx" 
           :href="item.href"
           @click.prevent="currentView = item.href.substring(1)"
           :class="{ 'text-wego-green': currentView === item.href.substring(1) }">
          {{ item.name }}
        </a>
      </nav>
      <div class="flex items-center gap-x-4">
      </div>
    </div>
  </header>
  <main class="pt-16">
    <div class="relative isolate overflow-hidden">
      <header class="pb-4 pt-6 sm:pb-6">
        <div class="mx-auto flex max-w-7xl flex-wrap items-center gap-6 px-4 sm:flex-nowrap sm:px-6 lg:px-8">
          <h1 class="text-xl font-semibold text-gray-900">Travel Market Visualization</h1>
        </div>
      </header>

      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <!-- Dynamic content based on current view -->
        <template v-if="currentView === 'bubble-chart'">
          <!-- Current Company Details -->
          <div class="bg-white rounded-lg shadow-lg p-6 mb-8">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-xl font-semibold text-wego-gray">Market Performance Over Time</h2>
              <button 
                @click="saveAnimatedChart"
                class="px-4 py-2 bg-wego-green text-white rounded hover:bg-wego-green-dark flex items-center gap-2"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M7.707 10.293a1 1 0 10-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 11.586V6h-2v5.586l-1.293-1.293z" />
                  <path d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" />
                </svg>
                Save Chart
              </button>
            </div>
            <div class="mb-6">
              <div class="slider-container bg-gray-50 rounded-lg p-4">
                <div class="flex justify-between items-center mb-4">
                  <span class="text-sm font-medium text-gray-500">Current Period:</span>
                  <span class="text-lg font-semibold text-gray-900">{{ currentQuarter }}</span>
                </div>
                <input 
                  type="range" 
                  :min="0" 
                  :max="quarters.length - 1" 
                  v-model="currentQuarterIndex"
                  @input="handleSliderChange"
                  :style="{ '--range-progress': `${(currentQuarterIndex / (quarters.length - 1)) * 100}%` }"
                  class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                >
                <div class="flex justify-between mt-2">
                  <span class="text-sm text-gray-500">{{ quarters[0] || '' }}</span>
                  <span class="text-sm text-gray-500">{{ quarters[quarters.length - 1] || '' }}</span>
                </div>
              </div>
            </div>
            <AnimatedBubbleChart 
              ref="bubbleChartRef" 
              class="h-[840px]" 
              @data-update="handleDataUpdate"
              @company-select="handleCompanySelect"
              @quarters-loaded="handleQuartersLoaded"
            />
          </div>
          <!-- Selected Company -->
          <div class="bg-white rounded-lg shadow-lg p-6 mb-8">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-xl font-semibold text-wego-gray">Selected Company</h2>
            </div>
            <div v-if="selectedCompany" class="mt-5">
              <dl class="grid grid-cols-1 gap-5 sm:grid-cols-4">
                <div class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
                  <dt class="truncate text-sm font-medium text-gray-500">Company Name</dt>
                  <dd class="mt-1 text-3xl font-semibold tracking-tight text-gray-900">
                    {{ companyNames[selectedCompany.company] || selectedCompany.company }}
                  </dd>
                </div>
                <div class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
                  <dt class="truncate text-sm font-medium text-gray-500">Quarter</dt>
                  <dd class="mt-1 text-3xl font-semibold tracking-tight text-gray-900">
                    {{ selectedCompany.quarter }}
                  </dd>
                </div>
                <div class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
                  <dt class="truncate text-sm font-medium text-gray-500">Revenue Growth</dt>
                  <dd class="mt-1 text-3xl font-semibold tracking-tight"
                      :class="selectedCompany.revenueGrowth >= 0 ? 'text-green-600' : 'text-red-600'">
                    {{ formatPercentage(selectedCompany.revenueGrowth) }}
                  </dd>
                </div>
                <div class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
                  <dt class="truncate text-sm font-medium text-gray-500">EBITDA Margin</dt>
                  <dd class="mt-1 text-3xl font-semibold tracking-tight"
                      :class="selectedCompany.ebitdaMargin >= 0 ? 'text-green-600' : 'text-red-600'">
                    {{ formatPercentage(selectedCompany.ebitdaMargin) }}
                  </dd>
                </div>
              </dl>
            </div>
            <div v-else class="text-center py-8 text-gray-500">
              Click on a company in the chart above to view its details.
            </div>
          </div>
          <!-- Selected Quarter (Industry Median) -->
          <div class="bg-white rounded-lg shadow-lg p-6 mb-8">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-xl font-semibold text-wego-gray">Selected Quarter (Industry Median)</h2>
            </div>
            <div v-if="currentQuarterData.length > 0">
              <dl class="mt-5 grid grid-cols-1 gap-5 sm:grid-cols-4">
                <div class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
                  <dt class="truncate text-sm font-medium text-gray-500">Companies Tracked</dt>
                  <dd class="mt-1 text-3xl font-semibold tracking-tight text-gray-900">
                    {{ currentQuarterData.length }}
                  </dd>
                </div>
                <div class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
                  <dt class="truncate text-sm font-medium text-gray-500">Quarter</dt>
                  <dd class="mt-1 text-3xl font-semibold tracking-tight text-gray-900">
                    {{ currentQuarter }}
                  </dd>
                </div>
                <div class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
                  <dt class="truncate text-sm font-medium text-gray-500">Revenue Growth (Median)</dt>
                  <dd class="mt-1 text-3xl font-semibold tracking-tight"
                      :class="medianRevenueGrowth >= 0 ? 'text-green-600' : 'text-red-600'">
                    {{ formatPercentage(medianRevenueGrowth) }}
                  </dd>
                </div>
                <div class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
                  <dt class="truncate text-sm font-medium text-gray-500">EBITDA Margin (Median)</dt>
                  <dd class="mt-1 text-3xl font-semibold tracking-tight"
                      :class="medianEbitdaMargin >= 0 ? 'text-green-600' : 'text-red-600'">
                    {{ formatPercentage(medianEbitdaMargin) }}
                  </dd>
                </div>
              </dl>
            </div>
            <div v-else class="text-center py-8 text-gray-500">
              No data available for the current quarter. Please interact with the chart above.
            </div>
          </div>
        </template>

        <template v-else-if="currentView === 'bar-chart'">
          <BarChart />
        </template>

        <!-- Static 2024Q3 Chart -->
        <div class="bg-white rounded-lg shadow-lg p-6 mb-8">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-semibold text-wego-gray">2024 Yearly Market Performance</h2>
          </div>
          <StaticBubbleChart ref="staticBubbleChartRef" />
        </div>

        <!-- Excel Data Table -->
        <div v-if="excelData.length" class="bg-white rounded-lg shadow-lg p-6 mb-8">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-semibold text-wego-gray">Raw Data</h2>
          </div>
          <div class="overflow-auto max-h-[600px]">
            <table class="min-w-full divide-y divide-gray-200 table-fixed">
              <thead class="bg-gray-50 sticky top-0 z-10">
                <tr>
                  <th v-for="(header, index) in excelData[0]" 
                      :key="index"
                      class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
                    {{ header }}
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="(row, rowIndex) in excelData.slice(1)" :key="rowIndex">
                  <td v-for="(cell, cellIndex) in row" 
                      :key="cellIndex"
                      class="px-4 py-2 text-sm whitespace-nowrap"
                      :class="getCellStyle(cell, cellIndex)">
                    {{ formatCell(cell) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { Dialog, DialogPanel } from '@headlessui/vue'
import {
  ArrowDownCircleIcon,
  ArrowPathIcon,
  ArrowUpCircleIcon,
  Bars3Icon,
} from '@heroicons/vue/20/solid'
import { BellIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import AnimatedBubbleChart from './components/AnimatedBubbleChart.vue'
import StaticBubbleChart from './components/StaticBubbleChart.vue'
import BarChart from './components/BarChart.vue'
import * as XLSX from 'xlsx'
import WEGO_LOGO from '/logos/Wego_logo.png'
import { inject } from '@vercel/analytics'
import Papa from 'papaparse'

const currentView = ref('bubble-chart')
const bubbleChartRef = ref(null)
const staticBubbleChartRef = ref(null)
const mobileMenuOpen = ref(false)
const excelData = ref([])
const rawData = ref([])

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

const navigation = [
  { name: 'Bubble Chart', href: '#bubble-chart' },
  { name: 'Bar Chart', href: '#bar-chart' },
]

const stats = [
  { name: 'Market Cap', value: 'tbd', change: '+4.75%', changeType: 'positive' },
  { name: 'Volume 24h', value: 'tbd', change: '+54.02%', changeType: 'negative' },
  { name: 'Total Value', value: 'tbd', change: '-1.39%', changeType: 'positive' },
  { name: 'Active users', value: 'tbd', change: '+10.18%', changeType: 'negative' },
]

const statuses = {
  Increased: 'text-green-700 bg-green-50 ring-green-600/20',
  Decreased: 'text-red-700 bg-red-50 ring-red-600/10',
  Neutral: 'text-gray-600 bg-gray-50 ring-gray-500/10',
}

const days = [
  {
    date: 'Today',
    dateTime: '2024-01-18',
    transactions: [
      {
        id: 1,
        amount: '$7,600.00',
        status: 'Increased',
        client: 'BTC/USD',
        description: 'Price movement',
        icon: ArrowUpCircleIcon,
      },
      {
        id: 2,
        amount: '$10,000.00',
        status: 'Decreased',
        client: 'ETH/USD',
        description: 'Price movement',
        icon: ArrowDownCircleIcon,
      },
    ],
  },
  {
    date: 'Yesterday',
    dateTime: '2024-01-17',
    transactions: [
      {
        id: 3,
        amount: '$14,000.00',
        status: 'Neutral',
        client: 'BTC/USD',
        description: 'Price movement',
        icon: ArrowPathIcon,
      },
    ],
  },
]

const handleFileUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  
  console.log('File selected:', file.name);
  
  try {
    const reader = new FileReader();
    reader.onload = async (e) => {
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
      console.log('Loaded data:', jsonData.slice(0, 5));
      excelData.value = jsonData;
      
      // Only process for animated chart
      if (bubbleChartRef.value) {
        console.log('Processing for animated chart');
        await bubbleChartRef.value.processExcelData(file);
      }
    };
    
    reader.onerror = (error) => {
      console.error('Error reading file:', error);
    };
    
    reader.readAsArrayBuffer(file);
  } catch (error) {
    console.error('Error processing file:', error);
  }
};

// Add play/pause control for bubble chart
const toggleBubbleAnimation = () => {
  bubbleChartRef.value.togglePlay()
}

const formatCell = (value) => {
  if (typeof value === 'number') {
    // Format as percentage if it's likely a percentage value (between -1 and 1)
    if (value >= -1 && value <= 1) {
      return `${(value * 100).toFixed(1)}%`;
    }
    // Otherwise format with 2 decimal places
    return value.toFixed(2);
  }
  return value;
};

const getCellStyle = (value, columnIndex) => {
  // Skip styling for the first column (quarter names)
  if (columnIndex === 0) return 'text-gray-900';
  
  // Style numerical values
  if (typeof value === 'number') {
    if (value > 0) return 'text-green-600 font-medium';
    if (value < 0) return 'text-red-600 font-medium';
    return 'text-gray-600';
  }
  
  return 'text-gray-900';
};

const importFromGoogleSheet = async () => {
  // Google Sheets ID and GID
  const sheetId = '2PACX-1vQYwQTSYwig7AZ0fjPniLVfUUJnLz3PP4f4fBtqkBNPYqrkKtQyZDaB99kHk2eCzuCh5i8oxTPCHeQ9';
  const gid = '1144102204';
  const sheetUrl = `https://docs.google.com/spreadsheets/d/e/${sheetId}/pub?gid=${gid}&output=csv`;
  
  try {
    console.log('Starting Google Sheet import...');
    console.log('Using sheet URL:', sheetUrl);
    const response = await fetch(sheetUrl);
    if (!response.ok) {
      throw new Error('Failed to fetch data from Google Sheet');
    }
    
    const csvText = await response.text();
    console.log('Received CSV response length:', csvText.length);
    
    // Parse CSV data
    const rows = csvText.split('\n').map(row => 
      row.split(',').map(cell => {
        // Remove quotes and trim whitespace
        const cleaned = cell.trim().replace(/^["']|["']$/g, '');
        // Try to convert to number if possible
        const num = parseFloat(cleaned);
        return isNaN(num) ? cleaned : num;
      })
    );
    
    console.log('Processed data rows:', rows.length);
    console.log('First few processed rows:', rows.slice(0, 3));

    // Function to check if a string is a valid quarter - define it before using it
    const isValidQuarter = (str) => {
      if (!str) return false;
      str = String(str).trim();
      // Check if it's a year (4 digits)
      return /^\d{4}$/.test(str);
    };

    // Find Revenue Growth row
    const revenueGrowthRowIndex = rows.findIndex(row => 
      row[0] && String(row[0]) === 'Rev Growth YoY'
    );
    
    // Add debug logging for the rows after Revenue Growth
    console.log('=== Debug: Rows after Revenue Growth ===');
    for (let i = revenueGrowthRowIndex + 1; i < revenueGrowthRowIndex + 10; i++) {
      if (i < rows.length) {
        console.log(`Row ${i}:`, rows[i]);
        if (rows[i] && rows[i][0]) {
          console.log(`First column of row ${i}:`, rows[i][0], 'isValidQuarter:', isValidQuarter(rows[i][0]));
        }
      }
    }
    
    // Find EBITDA Margin row
    const ebitdaStartIndex = rows.findIndex(row => 
      row && row[0] && String(row[0]) === 'EBITDA Margin % Quarterly'
    );
    
    if (revenueGrowthRowIndex === -1) {
      throw new Error('未找到 Revenue Growth 数据行');
    }
    
    if (ebitdaStartIndex === -1) {
      throw new Error('未找到 EBITDA Margin 数据行');
    }
    
    console.log('Found EBITDA row at index:', ebitdaStartIndex);
    console.log('EBITDA row content:', rows[ebitdaStartIndex]);
    console.log('Next 5 rows after EBITDA:');
    for (let i = ebitdaStartIndex + 1; i < ebitdaStartIndex + 6; i++) {
      if (i < rows.length) {
        console.log(`Row ${i}:`, rows[i]);
      }
    }
    
    // Get headers (company names)
    const headers = rows[0];
    console.log('Headers:', headers);
    
    // Extract quarters from the first column after the Rev Growth YoY row
    let currentYear = null;
    let quarterCount = 0;
    const quarters = [];

    // Debug information
    console.log('=== Year extraction from raw data ===');
    rows.slice(revenueGrowthRowIndex + 1, ebitdaStartIndex).forEach(row => {
      const yearStr = row[0];
      if (yearStr && String(yearStr) === '2025') {
        console.log('Found 2025 in raw data:', row);
      }
    });

    // Create a map to track which years and quarters we've seen
    const yearQuarterMap = new Map();

    rows.slice(revenueGrowthRowIndex + 1, ebitdaStartIndex).forEach(row => {
      const yearStr = row[0];
      if (isValidQuarter(yearStr)) {
        // Track this year and how many quarters we've seen for it
        if (!yearQuarterMap.has(yearStr)) {
          yearQuarterMap.set(yearStr, 0);
        }
        yearQuarterMap.set(yearStr, yearQuarterMap.get(yearStr) + 1);
        
        // Check if we have data in this row (any cells have values)
        const hasData = row.slice(1).some(cell => cell !== null && cell !== undefined && cell !== '');
        if (hasData || String(yearStr) === '2025') { // Always include 2025 rows to ensure 2025Q1 is available
          if (yearStr !== currentYear) {
            currentYear = yearStr;
            quarterCount = 0;
          }
          quarterCount++;
          const quarterStr = `${currentYear}'Q${quarterCount}`;
          quarters.push(quarterStr);
          console.log(`Generated quarter: ${quarterStr} from year ${yearStr}, has data: ${hasData}`);
        }
      }
    });

    console.log('Year-Quarter mapping:', Object.fromEntries(yearQuarterMap));
    console.log('Generated quarters:', quarters);
    
    // Prepare data for workbook
    const processedRows = [headers]; // Start with headers
    
    // Add revenue growth data
    processedRows.push(['Rev Growth YoY']);
    let currentQuarterIndex = 0;
    
    rows.slice(revenueGrowthRowIndex + 1, ebitdaStartIndex).forEach(row => {
      if (isValidQuarter(row[0])) {
        const quarterData = [...row];
        quarterData[0] = quarters[currentQuarterIndex]; // Replace year with quarter string
        processedRows.push(quarterData);
        currentQuarterIndex++;
      }
    });

    // Add EBITDA margin data
    processedRows.push(['EBITDA Margin % Quarterly']);

    // 创建一个单独的数组来特别处理2025年的数据
    const data2025 = [];

    // 使用不同的索引策略，基于年份和季度来匹配
    let currentEbitdaRowIndex = ebitdaStartIndex + 1;
    let currentEbitdaYear = null;
    let yearQuarterIndex = 0;

    console.log('=== Processing EBITDA data with improved mapping ===');

    while (currentEbitdaRowIndex < rows.length) {
      const row = rows[currentEbitdaRowIndex];
      if (!row || !row[0]) {
        currentEbitdaRowIndex++;
        continue;
      }
      
      const yearStr = String(row[0]);
      
      // Check if this is a year row
      if (isValidQuarter(yearStr)) {
        if (yearStr === '2025') {
          console.log('Found 2025 EBITDA row:', row);
          // 特别处理2025年数据，使用Q1作为标识
          const q1Row = [...row];
          q1Row[0] = "2025'Q1";
          data2025.push(q1Row);
        } else {
          // Process normal year data
          if (yearStr !== currentEbitdaYear) {
            currentEbitdaYear = yearStr;
            yearQuarterIndex = 0;
          }
          
          yearQuarterIndex++;
          const quarterStr = `${yearStr}'Q${yearQuarterIndex}`;
          const quarterRow = [...row];
          quarterRow[0] = quarterStr;
          
          // Add row to processed data
          processedRows.push(quarterRow);
          console.log(`Added EBITDA data for ${quarterStr}`);
        }
      }
      
      currentEbitdaRowIndex++;
    }

    // 将2025年数据添加到处理后的数据中
    data2025.forEach(row => {
      processedRows.push(row);
      console.log(`Added special 2025 data: ${row[0]}`);
    });

    console.log(`Processed EBITDA data with ${processedRows.length - (ebitdaStartIndex + 1)} rows`);
    
    // Debug final data
    console.log('=== Final Processed Data ===');
    console.log('Total rows:', processedRows.length);
    // Find 2025'Q1 rows
    const q1_2025_rows = processedRows.filter(row => 
      row[0] === "2025'Q1"
    );
    console.log('2025\'Q1 rows found:', q1_2025_rows.length);
    console.log('2025\'Q1 data:', q1_2025_rows);

    // Create workbook
    const workbook = {
      SheetNames: ['TTM (bounded)'],
      Sheets: {
        'TTM (bounded)': XLSX.utils.aoa_to_sheet(processedRows)
      }
    };
    
    // Convert to file
    const wbout = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
    const blob = new Blob([wbout], { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    });
    const file = new File([blob], 'google_sheet_data.xlsx', { type: blob.type });
    
    // Update chart
    if (bubbleChartRef.value) {
      console.log('Preparing to update bubble chart with processed data');
      await bubbleChartRef.value.processExcelData(file);
    } else {
      console.warn('Bubble chart reference not found');
    }
    
  } catch (error) {
    console.error('Error importing from Google Sheet:', error);
    console.error('Error stack:', error.stack);
    alert('导入数据失败：' + error.message);
  }
};

// Auto import data when component is mounted
onMounted(async () => {
  try {
    await importFromGoogleSheet();
  } catch (error) {
    console.error('Failed to load initial data:', error);
  }
});

// Add new data management for interactive display
const currentQuarterData = ref([]);
const averageRevenueGrowth = computed(() => {
  if (currentQuarterData.value.length === 0) return 0;
  const sum = currentQuarterData.value.reduce((acc, curr) => acc + curr.revenueGrowth, 0);
  return sum / currentQuarterData.value.length;
});

const averageEbitdaMargin = computed(() => {
  if (currentQuarterData.value.length === 0) return 0;
  const sum = currentQuarterData.value.reduce((acc, curr) => acc + curr.ebitdaMargin, 0);
  return sum / currentQuarterData.value.length;
});

const formatPercentage = (value) => {
  return `${(value * 100).toFixed(1)}%`;
};

// Add selected company state
const selectedCompany = ref(null);

const handleDataUpdate = (data) => {
  currentQuarterData.value = data;
  selectedCompany.value = null; // Reset selected company when data updates
};

// Add company selection handler
const handleCompanySelect = (company) => {
  selectedCompany.value = company;
};

// Add time control state
const quarters = ref([]);
const currentQuarterIndex = ref(0);
const currentQuarter = computed(() => quarters.value[currentQuarterIndex.value] || '');

// Handle quarters loaded event
const handleQuartersLoaded = ({ quarters: loadedQuarters, currentIndex }) => {
  quarters.value = loadedQuarters;
  currentQuarterIndex.value = currentIndex;
};

// Handle slider change
const handleSliderChange = () => {
  if (bubbleChartRef.value) {
    console.log(`App: Slider changed to index ${currentQuarterIndex.value}, quarter: ${quarters.value[currentQuarterIndex.value] || 'unknown'}`);
    bubbleChartRef.value.currentYearIndex = currentQuarterIndex.value;
    bubbleChartRef.value.handleSliderChange();
  }
};

// Add save chart function
const saveAnimatedChart = async () => {
  if (bubbleChartRef.value) {
    await bubbleChartRef.value.saveChart();
  }
};

// Add median data calculation
const medianRevenueGrowth = computed(() => {
  if (currentQuarterData.value.length === 0) return 0;
  const sortedGrowths = [...currentQuarterData.value].sort((a, b) => a.revenueGrowth - b.revenueGrowth);
  const midIndex = Math.floor(sortedGrowths.length / 2);
  if (sortedGrowths.length % 2 === 0) {
    return (sortedGrowths[midIndex - 1].revenueGrowth + sortedGrowths[midIndex].revenueGrowth) / 2;
  } else {
    return sortedGrowths[midIndex].revenueGrowth;
  }
});

const medianEbitdaMargin = computed(() => {
  if (currentQuarterData.value.length === 0) return 0;
  const sortedMargins = [...currentQuarterData.value].sort((a, b) => a.ebitdaMargin - b.ebitdaMargin);
  const midIndex = Math.floor(sortedMargins.length / 2);
  if (sortedMargins.length % 2 === 0) {
    return (sortedMargins[midIndex - 1].ebitdaMargin + sortedMargins[midIndex].ebitdaMargin) / 2;
  } else {
    return sortedMargins[midIndex].ebitdaMargin;
  }
});

inject();
</script>

<style>
@import './style.css';
</style>