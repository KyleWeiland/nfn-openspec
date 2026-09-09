import { defineConfig } from 'astro/config';

// https://astro.build/config
export default defineConfig({
  output: 'static',
  // Served from the root of the custom domain. Revert both of these to
  // base: '/nfn-openspec/' if the site moves back to github.io.
  site: 'https://nofrills.news',
  base: '/',
  build: {
    assets: '_assets'
  },
  prefetch: {
    prefetchAll: true,
    defaultStrategy: 'viewport',
  }
});
