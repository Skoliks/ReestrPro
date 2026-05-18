/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      boxShadow: {
        glow: "0 20px 80px rgba(2, 12, 27, 0.45)",
      },
      colors: {
        ink: "#050b16",
        panel: "#0d1728",
        accent: "#6ee7f2",
        accentSoft: "#8b5cf6",
      },
    },
  },
  plugins: [],
};
