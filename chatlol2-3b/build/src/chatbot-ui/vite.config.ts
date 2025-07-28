import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { fileURLToPath } from 'url'
import { dirname, resolve } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 8501,
    watch: {
      usePolling: false,
      interval: 1000
    },
    proxy: {
      '/ws': {
        target: 'http://localhost:8090',
        ws: true,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/ws/, ''),
      },
    },
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, './src')
    }
  }
})
