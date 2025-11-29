// frontend/tailwind.config.js

/** @type {import('tailwindcss').Config} */
export default {
  // ✅ FIX: ADDED SAFELIST
  // These classes are required for your dynamic styling (e.g., the colors you had in index.html)
  // and utility classes used for different components/roles.
  safelist: [
    "bg-[#E50914]",
    "hover:bg-[#B80010]",
    "bg-[#0A0A0A]",
    "bg-[#1C1C1C]",
    "text-[#FFFFFF]",
    "text-[#AAAAAA]",
    "shadow-red-900/50",
    "bg-red-800",
    "hover:bg-red-900",
    "bg-neutral-800",
    "hover:bg-neutral-900",
  ],
  // 1. CONTENT: Tell Tailwind where your project files are located.
  // It needs to scan these files to find and compile used classes.
  content: [
    "./index.html",
    // Ensure it scans your React component files (jsx and js)
    "./src/**/*.{js,ts,jsx,tsx}",
    // Specifically target the components folder as a fallback
    "./src/components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // 2. THEME: Define the custom colors used in LoginPage.jsx
      // This is crucial for Tailwind to recognize classes like 'bg-cine-primary'
      colors: {
        "cine-primary": "#E50914", // Vibrant Cinema Red
        "cine-secondary": "#B80010", // Darker Red
        "cine-background": "#0A0A0A", // Deep Black
        "cine-surface": "#1C1C1C", // Slightly lighter black for card/form
        "cine-text": "#FFFFFF", // White text
        "cine-text-secondary": "#AAAAAA", // Light grey for hints
      },
    },
  },
  plugins: [],
};
