<template>
  <header class="absolute inset-x-0 top-0 z-50 flex h-16 border-b border-gray-900/10">
    <div class="mx-auto flex w-full max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
      <div class="flex flex-1 items-center gap-x-6">
        <button type="button" class="-m-3 p-3 md:hidden" @click="mobileMenuOpen = true">
          <span class="sr-only">Open main menu</span>
          <Bars3Icon class="size-5 text-wego-gray" aria-hidden="true" />
        </button>
        <img class="h-8 w-auto" src="../logos/Wego_logo.png" alt="Wego" />
      </div>
      <nav class="hidden md:flex md:gap-x-11 md:text-sm/6 md:font-semibold md:text-wego-gray">
        <a v-for="(item, itemIdx) in navigation" :key="itemIdx" :href="item.href">{{ item.name }}</a>
      </nav>
      <div class="flex flex-1 items-center justify-end gap-x-8">
        <button type="button" class="-m-2.5 p-2.5 text-wego-gray hover:text-wego-gray-dark">
          <span class="sr-only">View notifications</span>
          <BellIcon class="size-6" aria-hidden="true" />
        </button>
        <a href="#" class="-m-1.5 p-1.5">
          <span class="sr-only">Your profile</span>
          <img class="size-8 rounded-full bg-wego-green" src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80" alt="" />
        </a>
      </div>
    </div>
  </header>

  <main class="pt-16">
    <div class="relative isolate overflow-hidden">
      <!-- Secondary navigation -->
      <header class="pb-4 pt-6 sm:pb-6">
        <div class="mx-auto flex max-w-7xl flex-wrap items-center gap-6 px-4 sm:flex-nowrap sm:px-6 lg:px-8">
          <h1 class="text-base/7 font-semibold text-wego-gray">Market Analysis</h1>
          <div class="order-last flex w-full gap-x-8 text-sm/6 font-semibold sm:order-none sm:w-auto sm:border-l sm:border-gray-200 sm:pl-6 sm:text-sm/7">
            <label class="relative cursor-pointer bg-wego-green text-white px-4 py-2 rounded-md hover:bg-wego-green-dark">
              Upload XLSX
              <input type="file" class="hidden" accept=".xlsx,.xls" @change="handleFileUpload" />
            </label>
          </div>
        </div>
      </header>

      <!-- Stats -->
      <div class="border-b border-b-gray-900/10 lg:border-t lg:border-t-gray-900/5">
        <dl class="mx-auto grid max-w-7xl grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 lg:px-2 xl:px-0">
          <div v-for="(stat, statIdx) in stats" :key="stat.name" :class="[statIdx % 2 === 1 ? 'sm:border-l' : statIdx === 2 ? 'lg:border-l' : '', 'flex flex-wrap items-baseline justify-between gap-x-4 gap-y-2 border-t border-gray-900/5 px-4 py-10 sm:px-6 lg:border-t-0 xl:px-8']">
            <dt class="text-sm/6 font-medium text-wego-gray">{{ stat.name }}</dt>
            <dd :class="[stat.changeType === 'negative' ? 'text-rose-600' : 'text-wego-green', 'text-xs font-medium']">{{ stat.change }}</dd>
            <dd class="w-full flex-none text-3xl/10 font-medium tracking-tight text-wego-gray-dark">{{ stat.value }}</dd>
          </div>
        </dl>
      </div>

      <!-- Chart Sections -->
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <!-- Animated Bubble Chart -->
        <div class="bg-white rounded-lg shadow-lg p-6 mb-8">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-semibold text-wego-gray">Market Performance Over Time</h2>
            <button 
              @click="toggleBubbleAnimation"
              class="px-4 py-2 bg-wego-green text-white rounded hover:bg-wego-green-dark">
              Play/Pause
            </button>
          </div>
          <AnimatedBubbleChart ref="bubbleChartRef" />
        </div>

        <!-- Static Chart -->
        <div class="bg-white rounded-lg shadow-lg p-6">
          <DataChart ref="chartRef" />
        </div>
      </div>

      <!-- Recent activity -->
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 mt-8">
        <h2 class="text-base font-semibold text-wego-gray">Recent activity</h2>
        <div class="mt-6 overflow-hidden border-t border-gray-100">
          <div class="mx-auto max-w-7xl">
            <table class="w-full text-left">
              <thead class="sr-only">
                <tr>
                  <th>Amount</th>
                  <th class="hidden sm:table-cell">Client</th>
                  <th>More details</th>
                </tr>
              </thead>
              <tbody>
                <template v-for="day in days" :key="day.dateTime">
                  <tr class="text-sm/6 text-gray-900">
                    <th scope="colgroup" colspan="3" class="relative isolate py-2 font-semibold">
                      <time :datetime="day.dateTime">{{ day.date }}</time>
                      <div class="absolute inset-y-0 right-full -z-10 w-screen border-b border-gray-200 bg-gray-50" />
                      <div class="absolute inset-y-0 left-0 -z-10 w-screen border-b border-gray-200 bg-gray-50" />
                    </th>
                  </tr>
                  <tr v-for="transaction in day.transactions" :key="transaction.id">
                    <td class="relative py-5 pr-6">
                      <div class="flex gap-x-6">
                        <component :is="transaction.icon" class="hidden h-6 w-5 flex-none text-gray-400 sm:block" aria-hidden="true" />
                        <div class="flex-auto">
                          <div class="flex items-start gap-x-3">
                            <div class="text-sm/6 font-medium text-gray-900">{{ transaction.amount }}</div>
                            <div :class="[statuses[transaction.status], 'rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset']">
                              {{ transaction.status }}
                            </div>
                          </div>
                        </div>
                      </div>
                    </td>
                    <td class="hidden py-5 pr-6 sm:table-cell">
                      <div class="text-sm/6 text-gray-900">{{ transaction.client }}</div>
                      <div class="mt-1 text-xs/5 text-gray-500">{{ transaction.description }}</div>
                    </td>
                    <td class="py-5 text-right">
                      <div class="flex justify-end">
                        <a :href="transaction.href" class="text-sm/6 font-medium text-indigo-600 hover:text-indigo-500">
                          View<span class="hidden sm:inline"> details</span>
                        </a>
                      </div>
                    </td>
                  </tr>
                </template>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import { Dialog, DialogPanel } from '@headlessui/vue'
import {
  ArrowDownCircleIcon,
  ArrowPathIcon,
  ArrowUpCircleIcon,
  Bars3Icon,
} from '@heroicons/vue/20/solid'
import { BellIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import DataChart from './components/DataChart.vue'
import AnimatedBubbleChart from './components/AnimatedBubbleChart.vue'

const chartRef = ref(null)
const bubbleChartRef = ref(null)
const mobileMenuOpen = ref(false)

const navigation = [
  { name: 'Dashboard', href: '#' },
  { name: 'Markets', href: '#' },
  { name: 'Analysis', href: '#' },
  { name: 'Reports', href: '#' },
]

const stats = [
  { name: 'Market Cap', value: '$405.09B', change: '+4.75%', changeType: 'positive' },
  { name: 'Volume 24h', value: '$12.78B', change: '+54.02%', changeType: 'negative' },
  { name: 'Total Value', value: '$245.98B', change: '-1.39%', changeType: 'positive' },
  { name: 'Active Traders', value: '30,156', change: '+10.18%', changeType: 'negative' },
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

const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    // Process the file for both charts
    chartRef.value.processExcelData(file)
    bubbleChartRef.value.processExcelData(file)
  }
}

// Add play/pause control for bubble chart
const toggleBubbleAnimation = () => {
  bubbleChartRef.value.togglePlay()
}
</script>

<style>
@import './style.css';
</style>
