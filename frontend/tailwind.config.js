/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#1E2123", // un poco más oscuro que el gris anterior
        primary: {
          700: "#004046", // teal oscuro, elegante
          600: "#007D85", // teal medio, más sobrio
          500: "#00A0A7", // cyan/teal claro pero menos brillante
        },
        muted: "#9CA3AF", // gris más neutro y equilibrado
      },
    },
  },
  plugins: [],
};
