/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'critical': '#ef4444',
        'warning': '#f59e0b',
        'minor': '#3b82f6',
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
