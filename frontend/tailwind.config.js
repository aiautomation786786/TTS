/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: '#0a0e1a',
        surface: '#0f1629',
        primary: '#6366f1',
      }
    },
  },
  plugins: [],
}
