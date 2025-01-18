/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'wego-green': {
          light: '#8CC63F',
          DEFAULT: '#75B143',
          dark: '#5B8E33'
        },
        'wego-gray': {
          DEFAULT: '#4A4A4A',
          dark: '#333333'
        }
      }
    },
  },
  plugins: [],
}

