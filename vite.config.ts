import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// base './' permite publicar en GitHub Pages bajo cualquier subruta
// (https://usuario.github.io/netflix-catalog-pulse/).
export default defineConfig({
  base: "./",
  plugins: [react()],
  server: {
    // El ETL reescribe data/*.duckdb y Parquet; evita que el watcher bloquee el archivo.
    watch: { ignored: ["**/data/**", "**/etl/**"] },
  },
  build: {
    outDir: "dist",
    assetsInlineLimit: 0,
    chunkSizeWarningLimit: 900,
  },
});
