/// <reference types="vitest" />
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setupTests.ts'],
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      reportsDirectory: './coverage',
      thresholds: {
        lines: 10,
        functions: 10,
        branches: 10,
        statements: 10,
      },
      exclude: [
        'node_modules/**',
        'src/test/**',
        'src/main.tsx',
        'src/vite-env.d.ts',
        '**/*.d.ts',
        '**/*.config.{ts,js}',
        'src/pages/**',
        'src/layouts/**',
        'src/hooks/**',
        'src/services/**',
        'src/store/auth-context.tsx',
        'src/components/index.ts',
        'src/components/Avatar.tsx',
        'src/components/Badge.tsx',
        'src/components/Card.tsx',
        'src/components/DropdownMenu.tsx',
        'src/components/Input.tsx',
        'src/components/Modal.tsx',
        'src/components/Table.tsx',
      ],
    },
    globals: true,
    clearMocks: true,
    restoreMocks: true,
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})