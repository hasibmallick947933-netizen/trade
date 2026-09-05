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
        background: "#0a0d14",
        surface: "#111622",
        "surface-raised": "#181f2f",
        border: "#232b3e",
        "border-light": "#2e3952",
        bullish: "#10b981",
        "bullish-dark": "#064e3b",
        bearish: "#ef4444",
        "bearish-dark": "#7f1d1d",
        warning: "#f59e0b",
        info: "#3b82f6",
        accent: "#6366f1",
      },
      fontFamily: {
        mono: ["JetBrains Mono", "SF Mono", "Menlo", "Courier New", "monospace"],
      },
    },
  },
  plugins: [],
};
