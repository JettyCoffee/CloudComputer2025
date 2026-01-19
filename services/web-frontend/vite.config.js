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
        // 如果需要，可以在这里重写路径
        // rewrite: (path) => path.replace(/^\/api/, '/api')
      }
    }
  }
})
