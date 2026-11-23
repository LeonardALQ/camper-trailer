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
      description: 'Design, model and drawings for a one-off off-road camper trailer and its tow vehicle, a Ford Ranger Super Duty.',
      customCss: ['./src/styles/site.css', './src/styles/sheet.css'],
      components: { Footer: './src/components/Footer.astro' },
      sidebar: [
        { label: 'Home', link: '/' },
        {
          label: 'Tow vehicle (Ranger Super Duty)',
          items: [
            { label: 'Plan and stages', link: '/tow-vehicle/' },
            { label: 'Parts list and totals', link: '/tow-vehicle/#parts-list' },
            { label: '3D model, truck and box', link: '/ute-garage/#3d-model' },
            { label: 'Drawing CT-701', link: '/drawings/#ct-701' },
            { label: 'Measurements', link: '/measurements/?part=car' },
          ],
        },
        {
          label: 'Bike box',
          items: [
            { label: 'Box design', link: '/ute-garage/' },
            { label: 'Parts list and totals', link: '/ute-garage/#parts-list' },
            { label: '3D model', link: '/ute-garage/#3d-model' },
            { label: 'Drawings CT-701 to CT-704', link: '/ute-garage/#drawings' },
            { label: 'Measurements', link: '/measurements/?part=box' },
          ],
        },
        {
          label: 'Trailer',
          items: [
            { label: 'Whole trailer', link: '/trailer/' },
            { label: 'Floor plan', link: '/trailer/#floor-plan' },
            { label: 'Chassis', link: '/chassis/' },
            { label: 'Body', link: '/body/' },
            { label: 'Electrical', link: '/electrical/' },
            { label: 'Plumbing and water', link: '/plumbing/' },
            { label: 'HVAC and fresh air', link: '/hvac/' },
            { label: 'Parts list and prices', link: '/trailer/#parts-list' },
            { label: 'Mass schedule', link: '/trailer/#every-line' },
            { label: '3D model', link: '/trailer/#3d-model' },
            { label: 'Drawings CT-001 to CT-621', link: '/drawings/#ct-001' },
            { label: 'Measurements', link: '/measurements/?part=trailer' },
          ],
        },
        { label: 'All drawings', link: '/drawings/' },
        { label: 'All measurements', link: '/measurements/' },
        { label: 'Downloads', link: '/downloads/' },
        {
          label: 'Reference',
          items: [
            { label: 'Decisions', link: '/decisions/' },
            { label: 'Research reports', collapsed: true, items: [{ autogenerate: { directory: 'research' } }] },
          ],
        },
      ],
    }),
  ],
});
