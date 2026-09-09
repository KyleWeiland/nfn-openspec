import { defineConfig } from 'astro/config';

// https://astro.build/config
export default defineConfig({
  output: 'static',
  base: '/nfn-openspec/',
  build: {
    assets: '_assets'
  },
  prefetch: {
    prefetchAll: true,
    defaultStrategy: 'viewport',
  }
});
