/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#F0FDFA',
          100: '#CCFBF1',
          200: '#99F6E4',
          500: '#14B8A6',
          600: '#0D9488',
          700: '#0F766E', // Deep teal
          800: '#115E59',
          900: '#134E4A',
        },
        brand: {
          blue: '#2563EB',
          dark: '#0F172A',
          bg: '#F8FAFC',
          surface: '#FFFFFF',
          muted: '#64748B',
          success: '#15803D',
          warning: '#B45309',
          danger: '#B91C1C',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      borderRadius: {
        'civic': '12px',
        'civic-lg': '16px',
      }
    },
  },
  plugins: [],
}
