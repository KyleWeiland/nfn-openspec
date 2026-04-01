import { defineConfig } from 'astro/config';

// https://astro.build/config
export default defineConfig({
  output: 'static',
  base: '/', // Placeholder for GitHub Pages - update later with actual repo name
  build: {
    assets: '_assets'
  }
});
