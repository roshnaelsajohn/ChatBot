/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#FFFFFF",      // White
        card: "#F8FAFC",            // Very Light Slate
        border: "#E2E8F0",          // Light Border
        text: "#0F172A",            // Slate 900 (Deep Navy)
        primary: "#F97316",         // Orange 500
        secondary: "#1E293B",       // Slate 800 (Navy)
      },
      fontFamily: {
        sans: ['"Funnel Sans"', 'sans-serif'],
        brand: ['"Fruktur"', 'cursive'],
      },
    },
  },
  plugins: [],
}
