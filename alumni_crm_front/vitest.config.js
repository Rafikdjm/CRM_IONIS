import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.js'],
    css: false,
    // Le pool 'forks' (défaut Vitest 4) échoue à démarrer dans certains
    // environnements Windows/OneDrive (timeout des workers) ; 'threads' est
    // plus fiable et plus rapide ici.
    pool: 'threads',
  },
})
