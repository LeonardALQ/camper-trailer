import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// Static output only. The dev and preview servers bind to loopback.
// SITE_URL and SITE_BASE are set when the site is built for GitHub Pages (https://leonardalq.github.io/camper-trailer/).
// A plain local build is served from the root.
export default defineConfig({
  site: process.env.SITE_URL || 'http://127.0.0.1:8791',
  base: process.env.SITE_BASE || '/',
  server: { host: '127.0.0.1', port: 8791 },
  integrations: [
    starlight({
      title: 'Camper trailer design',
      description: 'Design, model, drawings and build steps for a one-off off-road camper trailer.',
      customCss: ['./src/styles/site.css'],
      sidebar: [
        { label: 'Home', link: '/' },
        { label: 'Whole trailer', link: '/trailer/' },
        { label: 'Garage and bed', link: '/garage-bed/' },
        { label: 'Measurements', link: '/measurements/' },
        { label: 'Drawings', link: '/drawings/' },
        { label: 'Build steps (draft)', items: [{ autogenerate: { directory: 'steps' } }] },
        { label: 'Research', items: [{ autogenerate: { directory: 'research' } }] },
        { label: 'Downloads', link: '/downloads/' },
      ],
    }),
  ],
});
