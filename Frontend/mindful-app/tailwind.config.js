/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Cream-inspired, earthy, and calming color palette
        cream: {
          50: '#fffdf7',
          100: '#f8f4e9',
          200: '#f0e9d6',
          300: '#e7ddc2',
          400: '#daccaa',
          500: '#ceba91',
          600: '#b9a378',
          700: '#9e8a63',
          800: '#7d6d50',
          900: '#5f5340',
        },
        sage: {
          50: '#f4f6f4',
          100: '#e5eae3',
          200: '#d0d9cc',
          300: '#b3c1ac',
          400: '#97a78e',
          500: '#808f76',
          600: '#6a7761',
          700: '#56604f',
          800: '#444c40',
          900: '#353b33',
        },
        mist: {
          50: '#f6f7f7',
          100: '#e9edef',
          200: '#d5dde1',
          300: '#b7c6ce',
          400: '#96aab7',
          500: '#7e939f',
          600: '#697a84',
          700: '#58656d',
          800: '#485258',
          900: '#3a4347',
        },
      },
      borderRadius: {
        xl: '1rem',
        '2xl': '1.5rem',
        '3xl': '2rem',
      },
      boxShadow: {
        soft: '0 8px 20px -8px rgba(126, 113, 89, 0.1)',
        'inner-soft': 'inset 0 2px 4px 0 rgba(126, 113, 89, 0.05)',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
        serif: ['Georgia', 'ui-serif'],
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}; 