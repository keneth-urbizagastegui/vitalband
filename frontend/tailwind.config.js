/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#1E2123", // un poco más oscuro que el gris anterior
        primary: {
          // --- AÑADIDO ---
          // Añadimos el color claro para el texto de los enlaces inactivos
          100: "#B2DFDB", // Un color teal muy pálido
          // --- FIN AÑADIDO ---
          700: "#004046", // teal oscuro, elegante (Este es el que usaremos de fondo)
          600: "#007D85", // teal medio, más sobrio
          500: "#00A0A7", // cyan/teal claro pero menos brillante
        },
        muted: "#9CA3AF", // gris más neutro y equilibrado
      },
    },
  },
  plugins: [],
};
