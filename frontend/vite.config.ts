import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  
  // 개발 서버 설정
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true,
        secure: false
      },
      '/socket.io': {
        target: 'http://localhost:5001',
        changeOrigin: true,
        ws: true
      }
    }
  },

  // 경로 별칭 설정
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components'),
      '@pages': resolve(__dirname, 'src/pages'),
      '@hooks': resolve(__dirname, 'src/hooks'),
      '@services': resolve(__dirname, 'src/services'),
      '@utils': resolve(__dirname, 'src/utils'),
      '@types': resolve(__dirname, 'src/types'),
      '@stores': resolve(__dirname, 'src/stores'),
      '@assets': resolve(__dirname, 'src/assets')
    }
  },

  // 빌드 설정
  build: {
    outDir: 'dist',
    sourcemap: true,
    target: 'esnext',
    minify: 'esbuild',
    
    // 청크 분할 최적화
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          babylonjs: ['@babylonjs/core', '@babylonjs/loaders', '@babylonjs/materials'],
          mui: ['@mui/material', '@mui/icons-material'],
          utils: ['lodash', 'date-fns', 'uuid']
        }
      }
    },

    // 파일 크기 제한 경고 설정
    chunkSizeWarningLimit: 1000
  },

  // 테스트 설정
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/tests/setup.ts']
  },

  // CSS 설정
  css: {
    modules: {
      localsConvention: 'camelCase'
    },
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@/assets/styles/variables.scss";`
      }
    }
  },

  // 환경 변수 설정
  define: {
    __DEV__: JSON.stringify(process.env.NODE_ENV === 'development'),
    __PROD__: JSON.stringify(process.env.NODE_ENV === 'production')
  },

  // 최적화 설정
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      '@babylonjs/core',
      '@babylonjs/loaders',
      '@mui/material',
      'lodash'
    ],
    exclude: ['@babylonjs/inspector']
  }
})