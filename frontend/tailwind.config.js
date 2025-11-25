/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx,js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["system-ui", "ui-sans-serif", "sans-serif"],
      },
      colors: {
        background: "#050816",
        surface: "#0f172a",
        surfaceAlt: "#020617",
        accent: "#38bdf8",
      },
    },
  },
  plugins: [],
};

