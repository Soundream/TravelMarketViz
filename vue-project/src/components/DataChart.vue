<template>
  <div class="w-full h-[400px] bg-white rounded-lg shadow p-4">
    <Line v-if="chartData" :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { Line } from 'vue-chartjs';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import * as XLSX from 'xlsx';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const chartData = ref(null);
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top',
      labels: {
        color: '#4A4A4A'
      }
    },
    title: {
      display: true,
      text: 'Market Data Visualization',
      color: '#4A4A4A'
    }
  },
  scales: {
    x: {
      ticks: {
        color: '#4A4A4A'
      },
      grid: {
        color: 'rgba(74, 74, 74, 0.1)'
      }
    },
    y: {
      ticks: {
        color: '#4A4A4A'
      },
      grid: {
        color: 'rgba(74, 74, 74, 0.1)'
      }
    }
  }
};

const processExcelData = (file) => {
  const reader = new FileReader();
  reader.onload = (e) => {
    const data = new Uint8Array(e.target.result);
    const workbook = XLSX.read(data, { type: 'array' });
    const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
    const jsonData = XLSX.utils.sheet_to_json(firstSheet);

    // Assuming the Excel file has 'date' and 'value' columns
    const labels = jsonData.map(row => row.date);
    const values = jsonData.map(row => row.value);

    chartData.value = {
      labels,
      datasets: [{
        label: 'Market Value',
        data: values,
        borderColor: '#75B143',
        backgroundColor: 'rgba(117, 177, 67, 0.1)',
        tension: 0.1,
        fill: true
      }]
    };
  };
  reader.readAsArrayBuffer(file);
};

defineExpose({ processExcelData });
</script> 