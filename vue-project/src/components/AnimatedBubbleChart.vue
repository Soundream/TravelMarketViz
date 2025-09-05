<template>
  <div class="chart-container" ref="chartRef">
    <div id="additional-chart" class="w-full h-full"></div>

    <!-- Chart Controls Section -->
    <form class="mt-8">
      <div class="space-y-12">
        <div class="grid grid-cols-1 gap-x-8 gap-y-10 border-b border-gray-900/10 pb-12 md:grid-cols-3">
          <div>
            <h2 class="text-base/7 font-semibold text-gray-900">Chart Settings</h2>
            <p class="mt-1 text-sm/6 text-gray-600">Adjust the chart dimensions and axis ranges to customize the visualization.</p>
          </div>

          <div class="grid max-w-2xl grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-6 md:col-span-2">
            <!-- Chart Dimensions -->
            <div class="sm:col-span-3">
              <label for="chart-width" class="block text-sm/6 font-medium text-gray-900">Width (px)</label>
              <div class="mt-2 grid grid-cols-1">
                <input 
                  type="text" 
                  id="chart-width" 
                  v-model="chartDimensions.width" 
                  @input="validateAndUpdateDimensions('width')"
                  :class="[
                    'col-start-1 row-start-1 block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6',
                    chartDimensions.widthError ? 'outline-red-300 focus:outline-red-600' : 'outline-gray-300 focus:outline-indigo-600'
                  ]"
                  placeholder="1200"
                />
                <ExclamationCircleIcon 
                  v-if="chartDimensions.widthError"
                  class="pointer-events-none col-start-1 row-start-1 mr-3 size-5 self-center justify-self-end text-red-500 sm:size-4" 
                />
              </div>
              <p v-if="chartDimensions.widthError" class="mt-1 text-sm text-red-600">{{ chartDimensions.widthError }}</p>
            </div>

            <div class="sm:col-span-3">
              <label for="chart-height" class="block text-sm/6 font-medium text-gray-900">Height (px)</label>
              <div class="mt-2 grid grid-cols-1">
                <input 
                  type="text" 
                  id="chart-height" 
                  v-model="chartDimensions.height" 
                  @input="validateAndUpdateDimensions('height')"
                  :class="[
                    'col-start-1 row-start-1 block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6',
                    chartDimensions.heightError ? 'outline-red-300 focus:outline-red-600' : 'outline-gray-300 focus:outline-indigo-600'
                  ]"
                  placeholder="840"
                />
                <ExclamationCircleIcon 
                  v-if="chartDimensions.heightError"
                  class="pointer-events-none col-start-1 row-start-1 mr-3 size-5 self-center justify-self-end text-red-500 sm:size-4" 
                />
              </div>
              <p v-if="chartDimensions.heightError" class="mt-1 text-sm text-red-600">{{ chartDimensions.heightError }}</p>
            </div>

            <!-- X-Axis Range -->
            <div class="sm:col-span-3">
              <label for="x-min" class="block text-sm/6 font-medium text-gray-900">X-Axis Min (%)</label>
              <div class="mt-2 grid grid-cols-1">
                <input 
                  type="text" 
                  id="x-min" 
                  v-model="xAxisRange.min" 
                  @input="validateAndUpdateRange('x', 'min')"
                  :class="[
                    'col-start-1 row-start-1 block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6',
                    xAxisRange.minError ? 'outline-red-300 focus:outline-red-600' : 'outline-gray-300 focus:outline-indigo-600'
                  ]"
                  placeholder="-50"
                />
                <ExclamationCircleIcon 
                  v-if="xAxisRange.minError"
                  class="pointer-events-none col-start-1 row-start-1 mr-3 size-5 self-center justify-self-end text-red-500 sm:size-4" 
                />
              </div>
              <p v-if="xAxisRange.minError" class="mt-1 text-sm text-red-600">{{ xAxisRange.minError }}</p>
            </div>

            <div class="sm:col-span-3">
              <label for="x-max" class="block text-sm/6 font-medium text-gray-900">X-Axis Max (%)</label>
              <div class="mt-2 grid grid-cols-1">
                <input 
                  type="text" 
                  id="x-max" 
                  v-model="xAxisRange.max" 
                  @input="validateAndUpdateRange('x', 'max')"
                  :class="[
                    'col-start-1 row-start-1 block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6',
                    xAxisRange.maxError ? 'outline-red-300 focus:outline-red-600' : 'outline-gray-300 focus:outline-indigo-600'
                  ]"
                  placeholder="80"
                />
                <ExclamationCircleIcon 
                  v-if="xAxisRange.maxError"
                  class="pointer-events-none col-start-1 row-start-1 mr-3 size-5 self-center justify-self-end text-red-500 sm:size-4" 
                />
              </div>
              <p v-if="xAxisRange.maxError" class="mt-1 text-sm text-red-600">{{ xAxisRange.maxError }}</p>
            </div>

            <!-- Y-Axis Range -->
            <div class="sm:col-span-3">
              <label for="y-min" class="block text-sm/6 font-medium text-gray-900">Y-Axis Min (%)</label>
              <div class="mt-2 grid grid-cols-1">
                <input 
                  type="text" 
                  id="y-min" 
                  v-model="yAxisRange.min" 
                  @input="validateAndUpdateRange('y', 'min')"
                  :class="[
                    'col-start-1 row-start-1 block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6',
                    yAxisRange.minError ? 'outline-red-300 focus:outline-red-600' : 'outline-gray-300 focus:outline-indigo-600'
                  ]"
                  placeholder="-30"
                />
                <ExclamationCircleIcon 
                  v-if="yAxisRange.minError"
                  class="pointer-events-none col-start-1 row-start-1 mr-3 size-5 self-center justify-self-end text-red-500 sm:size-4" 
                />
              </div>
              <p v-if="yAxisRange.minError" class="mt-1 text-sm text-red-600">{{ yAxisRange.minError }}</p>
            </div>

            <div class="sm:col-span-3">
              <label for="y-max" class="block text-sm/6 font-medium text-gray-900">Y-Axis Max (%)</label>
              <div class="mt-2 grid grid-cols-1">
                <input 
                  type="text" 
                  id="y-max" 
                  v-model="yAxisRange.max" 
                  @input="validateAndUpdateRange('y', 'max')"
                  :class="[
                    'col-start-1 row-start-1 block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6',
                    yAxisRange.maxError ? 'outline-red-300 focus:outline-red-600' : 'outline-gray-300 focus:outline-indigo-600'
                  ]"
                  placeholder="100"
                />
                <ExclamationCircleIcon 
                  v-if="yAxisRange.maxError"
                  class="pointer-events-none col-start-1 row-start-1 mr-3 size-5 self-center justify-self-end text-red-500 sm:size-4" 
                />
              </div>
              <p v-if="yAxisRange.maxError" class="mt-1 text-sm text-red-600">{{ yAxisRange.maxError }}</p>
            </div>
          </div>
        </div>

        <!-- Companies Section -->
        <div class="grid grid-cols-1 gap-x-8 gap-y-10 border-b border-gray-900/10 pb-12 md:grid-cols-3">
          <div>
            <h2 class="text-base/7 font-semibold text-gray-900">Companies to Display</h2>
            <p class="mt-1 text-sm/6 text-gray-600">Select which companies you want to show on the chart.</p>
          </div>

          <div class="max-w-2xl space-y-10 md:col-span-2">
            <fieldset>
              <div class="mt-6 divide-y divide-gray-200 border-b border-t border-gray-200 max-h-60 overflow-y-auto">
                <div v-for="company in Object.keys(companyNames)" 
                     :key="company" 
                     class="relative flex gap-3 py-2 cursor-pointer hover:bg-gray-50"
                     @click="toggleCompany(company)">
                  <div class="min-w-0 flex-1 text-sm/6">
                    <label :for="`company-${company}`" class="select-none font-medium text-gray-900">
                      {{ companyNames[company] }}
                    </label>
                  </div>
                  <div class="flex h-6 shrink-0 items-center">
                    <div class="group grid size-4 grid-cols-1">
                      <input 
                        :id="`company-${company}`" 
                        :name="`company-${company}`" 
                        type="checkbox" 
                        v-model="selectedCompanies[company]"
                        class="col-start-1 row-start-1 appearance-none rounded border border-gray-300 bg-white checked:border-wego-green checked:bg-wego-green focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-wego-green disabled:border-gray-300 disabled:bg-gray-100 disabled:checked:bg-gray-100 forced-colors:appearance-auto"
                        @click.stop
                      />
                      <svg class="pointer-events-none col-start-1 row-start-1 size-3.5 self-center justify-self-center stroke-white group-has-[:disabled]:stroke-gray-950/25" viewBox="0 0 14 14" fill="none">
                        <path class="opacity-0 group-has-[:checked]:opacity-100" d="M3 8L6 11L11 3.5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                      </svg>
                    </div>
                  </div>
                </div>
              </div>
            </fieldset>
          </div>
        </div>
      </div>
    </form>
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
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #4e843d;  /* Wego green */
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}

input[type="range"]::-webkit-slider-thumb:hover {
  background: #3d6a31;  /* Darker Wego green */
  transform: scale(1.1);
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15);
}

input[type="range"]::-moz-range-thumb {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #4e843d;  /* Wego green */
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}

input[type="range"]::-moz-range-thumb:hover {
  background: #3d6a31;  /* Darker Wego green */
  transform: scale(1.1);
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15);
}

/* Add track styling for better visual feedback */
input[type="range"]::-webkit-slider-runnable-track {
  width: 100%;
  height: 4px;
  background: linear-gradient(to right, #4e843d 0%, #4e843d var(--range-progress, 50%), #e2e8f0 var(--range-progress, 50%));
  border-radius: 2px;
  border: none;
}

input[type="range"]::-moz-range-track {
  width: 100%;
  height: 4px;
  background: linear-gradient(to right, #4e843d 0%, #4e843d var(--range-progress, 50%), #e2e8f0 var(--range-progress, 50%));
  border-radius: 2px;
  border: none;
}

input[type="range"]:focus {
  outline: none;
}

input[type="range"]:focus::-webkit-slider-thumb {
  box-shadow: 0 0 0 3px rgba(78, 132, 61, 0.2);  /* Wego green with opacity */
}

input[type="range"]:focus::-moz-range-thumb {
  box-shadow: 0 0 0 3px rgba(78, 132, 61, 0.2);  /* Wego green with opacity */
}

.logo {
  cursor: move;
  user-select: none;
}
</style>

<script setup>
import { onMounted, onUnmounted, ref, computed } from 'vue';
import { ExclamationCircleIcon } from '@heroicons/vue/16/solid';
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
import KYAK_LOGO from '/logos/KYAK_logo.png'
import ELONG_LOGO from '/logos/ELONG_logo.png'
import Tongcheng_LOGO from '/logos/Tongcheng_logo.png'


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
  'Webjet OTA': '#e74c3c',
  'KYAK': '#ff690f',
  'eLong': '#2141b2',
  'Tongcheng': '#5b318f',
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
  'Webjet OTA': OTA_LOGO,
  'KYAK': KYAK_LOGO,
  'eLong': ELONG_LOGO,
  'Tongcheng': Tongcheng_LOGO,
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
  'Webjet OTA': 'Webjet OTA',
  'Traveloka': 'Traveloka',
  'KYAK': 'KYAK',
  'eLong': 'eLong',
  'Tongcheng': 'Tongcheng',
};

const currentYearIndex = ref(0);
const years = ref([]);
const mergedData = ref([]);

// Add emit definition
const emit = defineEmits(['data-update', 'company-select', 'quarters-loaded']);

// Add these as component-level variables to maintain consistent scales
let xScale, yScale;
let globalXDomain = [-0.5, 0.8];  // EBITDA margin range: -50% to 80%
let globalYDomain = [-0.3, 1.1]; // Revenue growth range: -30% to 100%

// Add chart dimensions
const margin = { top: 50, right: 100, bottom: 50, left: 60 };
const chartRef = ref(null);
let update; // Declare update function reference

// Add selected companies state
const selectedCompanies = ref({});

// Add axis range state
const xAxisRange = ref({
  min: '-50',
  max: '80',
  minError: '',
  maxError: ''
});

const yAxisRange = ref({
  min: '-30',
  max: '110',
  minError: '',
  maxError: ''
});

// Add after the axis range state declarations
const chartDimensions = ref({
  width: '1200',
  height: '840',
  widthError: '',
  heightError: ''
});

// Add new validation function for dimensions
const validateAndUpdateDimensions = (dimension) => {
  const value = parseInt(chartDimensions.value[dimension]);
  
  // Clear error first
  chartDimensions.value[`${dimension}Error`] = '';
  
  // Validate input is a number
  if (isNaN(value)) {
    chartDimensions.value[`${dimension}Error`] = 'Please enter a valid number';
    return;
  }
  
  // Validate minimum size
  if (value < 200) {
    chartDimensions.value[`${dimension}Error`] = 'Value must be at least 200px';
    return;
  }
  
  // Validate maximum size
  if (value > 5000) {
    chartDimensions.value[`${dimension}Error`] = 'Value must not exceed 5000px';
    return;
  }
  
  // Update chart if input is valid
  if (!chartDimensions.value.widthError && !chartDimensions.value.heightError) {
    console.log('Updating chart dimensions:', {
      width: parseInt(chartDimensions.value.width),
      height: parseInt(chartDimensions.value.height)
    });
    initChart();
    update(currentYearIndex.value);
  }
};

// Add validation and update function
const validateAndUpdateRange = (axis, bound) => {
  const range = axis === 'x' ? xAxisRange.value : yAxisRange.value;
  const value = parseFloat(range[bound]);
  
  // Clear error first
  range[`${bound}Error`] = '';
  
  // Validate input is a number
  if (isNaN(value)) {
    range[`${bound}Error`] = 'Please enter a valid number';
    return;
  }
  
  // Validate min is less than max
  const otherBound = bound === 'min' ? 'max' : 'min';
  const otherValue = parseFloat(range[otherBound]);
  
  if (!isNaN(otherValue)) {
    if (bound === 'min' && value >= otherValue) {
      range[`${bound}Error`] = 'Min value must be less than max';
      return;
    }
    if (bound === 'max' && value <= otherValue) {
      range[`${bound}Error`] = 'Max value must be greater than min';
      return;
    }
  }
  
  // Update global domain and redraw chart if input is valid
  if (axis === 'x') {
    const xMin = parseFloat(xAxisRange.value.min) / 100;
    const xMax = parseFloat(xAxisRange.value.max) / 100;
    if (!isNaN(xMin) && !isNaN(xMax) && xMin < xMax) {
      globalXDomain = [xMin, xMax];
      console.log('Updated X axis domain:', globalXDomain);
    }
  } else {
    const yMin = parseFloat(yAxisRange.value.min) / 100;
    const yMax = parseFloat(yAxisRange.value.max) / 100;
    if (!isNaN(yMin) && !isNaN(yMax) && yMin < yMax) {
      globalYDomain = [yMin, yMax];
      console.log('Updated Y axis domain:', globalYDomain);
    }
  }
  
  // Only update chart if both values are valid and min < max
  if (!range.minError && !range.maxError) {
    console.log('Updating chart with new domains:', { 
      xDomain: globalXDomain, 
      yDomain: globalYDomain 
    });
    initChart();
    update(currentYearIndex.value);
  }
};

// Function to initialize selected companies
const initializeSelectedCompanies = () => {
  const companies = Object.keys(companyNames);
  companies.forEach(company => {
    selectedCompanies.value[company] = true;
  });
  console.log('Initialized selected companies:', selectedCompanies.value);
};

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
      
      // Initialize selected companies
      initializeSelectedCompanies();
      
      // Find Revenue Growth row
      const revenueGrowthRowIndex = jsonData.findIndex(row => 
        row && row[0] && String(row[0]) === 'Rev Growth YoY'
      );
      
      // Find EBITDA Margin row
      const ebitdaStartIndex = jsonData.findIndex(row => 
        row && row[0] && String(row[0]) === 'EBITDA Margin % Quarterly'
      );
      
      if (revenueGrowthRowIndex === -1) {
        throw new Error('Revenue Growth row not found');
      }
      
      if (ebitdaStartIndex === -1) {
        throw new Error('EBITDA Margin row not found');
      }
      
      // Process data rows
      const processedData = [];
      const quarters = new Set();
      
      // 记录所有数据的最大最小值
      let globalMinEbitda = globalXDomain[0];
      let globalMaxEbitda = globalXDomain[1];
      let globalMinRevenue = globalYDomain[0];
      let globalMaxRevenue = globalYDomain[1];
      
      // Function to check if a string is a valid quarter
      const isValidQuarter = (str) => {
        if (!str) return false;
        str = String(str).trim();
        // Remove any potential whitespace or special characters
        str = str.replace(/\s+/g, '');
        const quarterPattern = /^\d{4}'Q[1-4]$/;
        if (!quarterPattern.test(str)) {
          console.log(`Quarter ${str} rejected: invalid format`);
          return false;
        }
        
        // Extract year and quarter
        const match = str.match(/^(\d{4})'Q(\d)$/);
        const yearNum = parseInt(match[1]);
        const quarterNum = parseInt(match[2]);
        
        // Only accept data between 2016'Q1 and 2025'Q1
        if (yearNum < 2016 || yearNum > 2025) {
          console.log(`Quarter ${str} rejected: year ${yearNum} outside range 2016-2025`);
          return false;
        }
        
        console.log(`Quarter ${str} accepted: within valid range`);
        return true;
      };
      
      // Process revenue growth data
      let currentRowIndex = revenueGrowthRowIndex + 1;
      
      // Debug log for revenue growth section
      console.log('=== Revenue Growth Section ===');
      console.log('First 5 rows after Revenue Growth:');
      for (let i = revenueGrowthRowIndex; i < revenueGrowthRowIndex + 6; i++) {
        console.log(`Row ${i}:`, jsonData[i]);
      }
      
      let currentQuarter = jsonData[currentRowIndex]?.[0];
      if (currentQuarter) {
        currentQuarter = String(currentQuarter).trim().replace(/\s+/g, '');
      }
      
      // Add safety check for data
      if (!currentQuarter) {
        console.error('No quarter data found at row:', currentRowIndex);
        console.error('Row data:', jsonData[currentRowIndex]);
        throw new Error('No valid quarter data found after Revenue Growth row');
      }
      
      while (currentRowIndex < jsonData.length && currentRowIndex < ebitdaStartIndex) {
        const rowData = jsonData[currentRowIndex];
        if (!rowData || !Array.isArray(rowData)) {
          console.warn(`Invalid row data at index ${currentRowIndex}`);
          currentRowIndex++;
          currentQuarter = jsonData[currentRowIndex]?.[0];
          if (currentQuarter) {
            currentQuarter = String(currentQuarter).trim().replace(/\s+/g, '');
          }
          continue;
        }
        
        currentQuarter = String(rowData[0] || '').trim().replace(/\s+/g, '');
        if (isValidQuarter(currentQuarter)) {
          quarters.add(currentQuarter);
          
          // Store revenue growth data for this quarter
          headers.forEach((company, j) => {
            if (!company) return;
            
            const colIndex = j + 1;
            const revenueGrowth = parseFloat(rowData[colIndex]);
            
            if (!isNaN(revenueGrowth)) {
              processedData.push({
                quarter: currentQuarter,
                company,
                revenueGrowth: revenueGrowth / 100,
                ebitdaMargin: null,
                hasBothQuarters: false
              });
            }
          });
        }
        
        currentRowIndex++;
      }
      
      // Process EBITDA margin data
      currentRowIndex = ebitdaStartIndex + 1;
      
      // Debug log for EBITDA section
      console.log('=== EBITDA Section ===');
      console.log('EBITDA start index:', ebitdaStartIndex);
      console.log('Next 5 rows after EBITDA Margin row:');
      for (let i = ebitdaStartIndex; i < ebitdaStartIndex + 6; i++) {
        console.log(`Row ${i}:`, jsonData[i]);
      }
      
      currentQuarter = jsonData[currentRowIndex]?.[0];
      if (currentQuarter) {
        currentQuarter = String(currentQuarter).trim().replace(/\s+/g, '');
      }
      
      while (currentRowIndex < jsonData.length) {
        const rowData = jsonData[currentRowIndex];
        if (!rowData || !Array.isArray(rowData)) {
          console.warn(`Invalid row data at index ${currentRowIndex}`);
          currentRowIndex++;
          currentQuarter = jsonData[currentRowIndex]?.[0];
          if (currentQuarter) {
            currentQuarter = String(currentQuarter).trim().replace(/\s+/g, '');
          }
          continue;
        }
        
        currentQuarter = String(rowData[0] || '').trim().replace(/\s+/g, '');
        if (isValidQuarter(currentQuarter)) {
          console.log(`Processing EBITDA data for quarter: ${currentQuarter}`);
          
          // Update EBITDA margin for existing data points
          headers.forEach((company, j) => {
            if (!company) return;
            
            const colIndex = j + 1;
            const ebitdaMargin = parseFloat(rowData[colIndex]);
            
            if (!isNaN(ebitdaMargin)) {
              const existingDataPoint = processedData.find(
                d => d.quarter === currentQuarter && d.company === company
              );
              
              if (existingDataPoint) {
                console.log(`Updating EBITDA for ${company} in ${currentQuarter}: ${ebitdaMargin}`);
                existingDataPoint.ebitdaMargin = ebitdaMargin / 100;
                existingDataPoint.hasBothQuarters = true;
              } else {
                console.log(`No revenue data found for ${company} in ${currentQuarter}, EBITDA: ${ebitdaMargin}`);
              }
            }
          });
        }
        
        currentRowIndex++;
      }
      
      // Filter out incomplete data points
      mergedData.value = processedData.filter(d => d.hasBothQuarters);
      
      // 计算所有数据点的最小和最大值，并与默认值比较，如果超出则扩展范围
      if (mergedData.value.length > 0) {
        const ebitdaValues = mergedData.value.map(d => d.ebitdaMargin);
        const minEbitda = Math.min(...ebitdaValues);
        const maxEbitda = Math.max(...ebitdaValues);
        
        const revenueValues = mergedData.value.map(d => d.revenueGrowth);
        const minRevenue = Math.min(...revenueValues);
        const maxRevenue = Math.max(...revenueValues);
        
        // 添加10%的边距
        const ebitdaMargin = (maxEbitda - minEbitda) * 0.1;
        const revenueMargin = (maxRevenue - minRevenue) * 0.1;
        
        // 比较默认值和实际数据范围，取较大范围
        globalXDomain = [
          Math.min(globalXDomain[0], minEbitda - ebitdaMargin),
          Math.max(globalXDomain[1], maxEbitda + ebitdaMargin)
        ];
        globalYDomain = [
          Math.min(globalYDomain[0], minRevenue - revenueMargin),
          Math.max(globalYDomain[1], maxRevenue + revenueMargin)
        ];
        
        // 更新UI中显示的范围值
        xAxisRange.value.min = (globalXDomain[0] * 100).toFixed(0);
        xAxisRange.value.max = (globalXDomain[1] * 100).toFixed(0);
        yAxisRange.value.min = (globalYDomain[0] * 100).toFixed(0);
        yAxisRange.value.max = (globalYDomain[1] * 100).toFixed(0);
        
        console.log('自动调整后的坐标轴范围:', {
          xDomain: globalXDomain.map(v => (v*100).toFixed(1) + '%'),
          yDomain: globalYDomain.map(v => (v*100).toFixed(1) + '%')
        });
      }
      
      console.log('=== Data Processing Debug ===')
      console.log('Total processed data points before filtering:', processedData.length);
      console.log('Sample of processed data before filtering:', processedData.slice(0, 5));
      console.log('Total merged data points after filtering:', mergedData.value.length);
      console.log('Sample of merged data after filtering:', mergedData.value.slice(0, 5));
      console.log('Quarters with data:', years.value);
      
      if (mergedData.value.length === 0) {
        throw new Error('No valid data points found after processing');
      }
      
      // Sort quarters chronologically
      years.value = Array.from(quarters).sort((a, b) => {
        const [yearA, quarterA] = a.split("'");
        const [yearB, quarterB] = b.split("'");
        return parseInt(yearA) - parseInt(yearB) || 
               parseInt(quarterA.slice(1)) - parseInt(quarterB.slice(1));
      });
      
      if (years.value.length === 0) {
        throw new Error('No valid quarters found after processing');
      }
      
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
  const width = parseInt(chartDimensions.value.width);
  const height = parseInt(chartDimensions.value.height);
  console.log('Initializing chart with dimensions:', width, height);
  
  // Clear existing SVG
  d3.select('#additional-chart').selectAll("*").remove();
    
  // Create SVG with viewBox for better scaling
  const svg = d3.select('#additional-chart')
    .append("svg")
    .attr("width", "100%")
    .attr("height", "100%")
    .attr("viewBox", `0 0 ${width} ${height}`)
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
    .attr("class", "x-axis")
    .call(xAxis);

  svg.append("g")
    .attr("transform", `translate(${margin.left},0)`)
    .attr("class", "y-axis")
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
      console.log('=== Update Function Start ===');
      console.log('Updating chart for quarter:', years.value[quarterIndex]);
      console.log('Selected companies state:', selectedCompanies.value);
      console.log('Current mergedData:', mergedData.value);
      
      // Filter data for current quarter and selected companies
      const currentData = mergedData.value.filter(d => {
        const isSelectedQuarter = d.quarter === years.value[quarterIndex];
        const isSelectedCompany = selectedCompanies.value[d.company] === true;
        return isSelectedQuarter && isSelectedCompany;
      });
      
      console.log('Filtered data for rendering:', currentData);
      
      // 计算当前季度数据的范围，如果超出全局范围则调整
      if (currentData.length > 0) {
        // 提取当前季度的数值范围
        const ebitdaValues = currentData.map(d => d.ebitdaMargin);
        const minEbitda = Math.min(...ebitdaValues);
        const maxEbitda = Math.max(...ebitdaValues);
        
        const revenueValues = currentData.map(d => d.revenueGrowth);
        const minRevenue = Math.min(...revenueValues);
        const maxRevenue = Math.max(...revenueValues);
        
        // 添加边距
        const ebitdaMargin = (maxEbitda - minEbitda) * 0.1;
        const revenueMargin = (maxRevenue - minRevenue) * 0.1;
        
        // 检查当前季度数据是否超出默认范围
        const defaultXDomain = [-0.5, 0.8]; // 原始默认值
        const defaultYDomain = [-0.3, 1.1]; // 原始默认值
        
        // 使用默认值，除非数据超出范围
        const currentXDomain = [
          Math.min(defaultXDomain[0], minEbitda - ebitdaMargin),
          Math.max(defaultXDomain[1], maxEbitda + ebitdaMargin)
        ];
        
        const currentYDomain = [
          Math.min(defaultYDomain[0], minRevenue - revenueMargin),
          Math.max(defaultYDomain[1], maxRevenue + revenueMargin)
        ];
        
        // 更新比例尺
        xScale.domain(currentXDomain);
        yScale.domain(currentYDomain);
        
        // 更新UI中显示的范围值
        xAxisRange.value.min = (currentXDomain[0] * 100).toFixed(0);
        xAxisRange.value.max = (currentXDomain[1] * 100).toFixed(0);
        yAxisRange.value.min = (currentYDomain[0] * 100).toFixed(0);
        yAxisRange.value.max = (currentYDomain[1] * 100).toFixed(0);
        
        console.log(`季度 ${years.value[quarterIndex]} 调整后的坐标轴范围:`, {
          xDomain: currentXDomain.map(v => (v*100).toFixed(1) + '%'),
          yDomain: currentYDomain.map(v => (v*100).toFixed(1) + '%')
        });
        
        // 更新坐标轴
        svg.select(".x-axis").transition().duration(750).call(
          d3.axisBottom(xScale).ticks(8).tickFormat(d => (d * 100).toFixed(0) + "%")
        );
        svg.select(".y-axis").transition().duration(750).call(
          d3.axisLeft(yScale).ticks(8).tickFormat(d => (d * 100).toFixed(0) + "%")
        );
      }
      
      // Emit the current data
      emit('data-update', currentData);
    
    // Update bubbles
    const bubbles = svg.selectAll(".bubble")
      .data(currentData, d => d.company);
        
      console.log('Existing bubbles count:', bubbles.size());
      console.log('Entering bubbles count:', bubbles.enter().size());
      console.log('Exiting bubbles count:', bubbles.exit().size());
      
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
        .attr("y", -logoSize/2 - 25)
        .attr("width", logoSize)
        .attr("height", logoSize)
        .style("pointer-events", "auto");

      // Add invisible background rect to make dragging easier
      logoGroups.insert("rect", "image")
        .attr("class", "logo-hit-area")
        .attr("x", -logoSize/2)
        .attr("y", -logoSize/2 - 20)
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

      console.log('=== Update Function End ===');
  };

    // Initial update
    if (years.value.length > 0) {
      console.log('Performing initial update with index:', currentYearIndex.value);
      update(currentYearIndex.value);
    } else {
      console.warn('No years data available for initial update');
    }
};

// Add company selection handler
const handleCompanySelection = () => {
  if (update) update(currentYearIndex.value);
};

// Add this after the existing script setup imports
const toggleCompany = (company) => {
  selectedCompanies.value[company] = !selectedCompanies.value[company];
  handleCompanySelection();
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