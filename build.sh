#!/bin/bash
# Build script for Vercel deployment

# Build Svelte frontend
cd svelte && npm install && npm run build

# Copy assets to public directory that Vercel can serve
cd ..
mkdir -p public/assets
cp svelte/dist/assets/* public/assets/
cp svelte/dist/.vite/manifest.json public/

echo "Build completed - assets copied to public/"