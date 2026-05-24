/** @type {import('tailwindcss').Config} */
module.exports = {
  mode: 'jit',
  content: [
    './templates/**/*.html',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
