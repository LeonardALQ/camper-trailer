// Checks that the built site scrolls: mouse wheel over text, mouse wheel over the 3D model, Ctrl+wheel zooms the
// model instead, and PageDown. Full-page screenshots cannot catch a page that will not scroll, so this does.
// Usage: node scroll-check.mjs [port] [base path, for example /camper-trailer for the GitHub Pages build].
// Writes ../build/shots/scroll-check.json and exits 1 if a check fails.
import { chromium } from 'playwright';
import fs from 'node:fs';

const port = process.argv[2] || '8791';
const base = `http://127.0.0.1:${port}${(process.argv[3] || '').replace(/\/$/, '')}`;
const steps = fs.readdirSync('../site/dist/steps').filter((d) => /^\d\d-/.test(d)).sort();
const pages = [
  { path: '/', viewer: false },
  { path: '/garage-bed/', viewer: true },
  { path: '/garage-bed/', viewer: true, theme: 'dark' },
  { path: '/trailer/', viewer: true },
  { path: '/trailer/', viewer: true, theme: 'dark' },
  { path: '/measurements/', viewer: false },
  { path: `/steps/${steps.find((s) => s.startsWith('03'))}/`, viewer: true },
  { path: '/drawings/', viewer: false },
  { path: '/research/03-bike-restraint-garage/', viewer: false },
];

const browser = await chromium.launch({
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'],
});
const results = [];
let failed = 0;

for (const p of pages) {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  if (p.theme) await page.addInitScript((t) => localStorage.setItem('starlight-theme', t), p.theme);
  await page.goto(base + p.path, { waitUntil: 'networkidle' });
  if (p.viewer) {
    await page.waitForFunction(() => document.body.dataset.cadReady === 'yes', null, { timeout: 60000 });
    await page.waitForTimeout(1500);
  }
  const r = { page: p.path + (p.theme ? ` (${p.theme})` : ''), checks: {} };
  const check = (name, ok, detail) => {
    r.checks[name] = { ok, ...detail };
    if (!ok) failed += 1;
  };
  const scrollY = () => page.evaluate(() => Math.round(window.scrollY));

  const css = await page.evaluate(() => {
    const probe = document.createElement('div');
    probe.style.backgroundColor = 'var(--sl-color-bg)';
    document.body.append(probe);
    const want = getComputedStyle(probe).backgroundColor;
    probe.remove();
    const b = getComputedStyle(document.body);
    return { html: getComputedStyle(document.documentElement).overflowY, body: b.overflowY, select: b.userSelect,
      bg: b.backgroundColor, want, room: document.documentElement.scrollHeight - window.innerHeight };
  });
  check('page styles', css.html !== 'hidden' && css.body !== 'hidden' && css.select !== 'none' && css.bg === css.want, css);

  // Wheel over a paragraph of text near the top of the page.
  await page.evaluate(() => window.scrollTo(0, 0));
  const para = await page.evaluate(() => {
    const el = [...document.querySelectorAll('main p')].find((e) => {
      const b = e.getBoundingClientRect();
      return b.height > 0 && b.top > 0 && b.bottom < window.innerHeight;
    });
    if (!el) return null;
    const b = el.getBoundingClientRect();
    return { x: b.left + 20, y: b.top + b.height / 2 };
  });
  if (para) {
    await page.mouse.move(para.x, para.y);
    await page.mouse.wheel(0, 500);
    await page.waitForTimeout(600);
    const y = await scrollY();
    check('wheel over text scrolls the page', css.room <= 0 || y > 0, { scrollY: y, room: css.room });
  }

  // Keyboard scrolling after clicking into the text.
  await page.evaluate(() => window.scrollTo(0, 0));
  if (para) await page.mouse.click(para.x, para.y);
  await page.keyboard.press('PageDown');
  await page.waitForTimeout(600);
  const yk = await scrollY();
  check('PageDown scrolls the page', css.room <= 0 || yk > 0, { scrollY: yk });

  if (p.viewer) {
    const zoom = () => page.evaluate(() => document.querySelector('cad-viewer')?.viewer?.getCameraZoom?.() ?? null);
    // Put the model's canvas in the middle of the window, then point at its centre.
    await page.evaluate(() => {
      const c = document.querySelector('cad-viewer canvas').getBoundingClientRect();
      window.scrollTo(0, window.scrollY + c.top + c.height / 2 - window.innerHeight / 2);
    });
    await page.waitForTimeout(300);
    const c = await page.evaluate(() => {
      const b = document.querySelector('cad-viewer canvas').getBoundingClientRect();
      return { x: b.left + b.width / 2, y: b.top + b.height / 2 };
    });
    await page.mouse.move(c.x, c.y);
    const y0 = await scrollY();
    const z0 = await zoom();
    await page.mouse.wheel(0, 300);
    await page.waitForTimeout(150);
    const hint = await page.evaluate(() => {
      const h = document.querySelector('.cad-wheel-hint');
      return h ? Number(getComputedStyle(h).opacity) : null;
    });
    await page.waitForTimeout(450);
    const y1 = await scrollY();
    const z1 = await zoom();
    check('wheel over the model scrolls the page and leaves the zoom alone', y1 > y0 && z1 === z0,
      { scrollY: [y0, y1], zoom: [z0, z1], hintOpacity: hint });

    // Ctrl+wheel over the model (also what a trackpad pinch sends) zooms the model and leaves the page alone.
    await page.mouse.move(c.x, c.y - (y1 - y0));
    const y2 = await scrollY();
    await page.keyboard.down('Control');
    await page.mouse.wheel(0, -300);
    await page.keyboard.up('Control');
    await page.waitForTimeout(600);
    const y3 = await scrollY();
    const z3 = await zoom();
    check('Ctrl+wheel over the model zooms it', y3 === y2 && z3 !== null && z3 !== z1, { scrollY: [y2, y3], zoom: [z1, z3] });
  }
  results.push(r);
  await page.close();
}
await browser.close();
fs.mkdirSync('../build/shots', { recursive: true });
fs.writeFileSync('../build/shots/scroll-check.json', JSON.stringify(results, null, 1));
for (const r of results) {
  for (const [name, v] of Object.entries(r.checks)) {
    const { ok, ...detail } = v;
    console.log(`${ok ? 'PASS' : 'FAIL'}  ${r.page}  ${name}  ${JSON.stringify(detail)}`);
  }
}
console.log(failed ? `${failed} check(s) failed` : 'all scroll checks passed');
process.exit(failed ? 1 : 0);
