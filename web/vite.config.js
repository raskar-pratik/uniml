import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Vite config for the UniML dashboard.
// - Dev: proxy API + health/info to the FastAPI backend on :8000
// - Build: emit a static bundle into web/dist (served by FastAPI in prod)
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
      '/health': { target: 'http://localhost:8000', changeOrigin: true },
      '/info': { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    sourcemap: false,
  },
})
