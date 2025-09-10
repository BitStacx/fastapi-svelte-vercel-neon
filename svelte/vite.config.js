import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [svelte()],
  build: {
    // Ensure old build files are preserved for rollbacks
    emptyOutDir: true,
    // Generate manifest file for Django to find the hashed files
    manifest: true,
    // Add content hash to file names for better caching
    rollupOptions: {
      input: {
        index: resolve(__dirname, 'src/index.js'),
        // Add additional entry points here as needed
      },
      output: {
        // Use content hashing in the output filenames
        entryFileNames: `assets/[name].[hash].js`,
        chunkFileNames: `assets/[name].[hash].js`,
        assetFileNames: `assets/[name].[hash].[ext]`,
      },
    },
  },
})
