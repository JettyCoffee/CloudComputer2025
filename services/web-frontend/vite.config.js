import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      // 将 /api 请求代理到 search-agent 服务
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      // 将 /kg-api 请求代理到 knowledge-engine 服务
      '/kg-api': {
        target: 'http://localhost:8002',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/kg-api/, '/api')
      }
    }
  }
})
