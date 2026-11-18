// Headless Chromium screenshots of the built site served on 127.0.0.1 (Playwright image, --network host).
// Usage: node shot.mjs [port]. Writes PNGs and report.json into ../build/shots/.
import { chromium } from 'playwright';
import fs from 'node:fs';

const port = process.argv[2] || '8791';
const base = `http://127.0.0.1:${port}`;
const out = '../build/shots';
fs.mkdirSync(out, { recursive: true });

const steps = fs.readdirSync('../site/dist/steps').filter((d) => /^\d\d-/.test(d)).sort();
const pick = (n) => steps.find((s) => s.startsWith(n));
const jobs = [
  { path: '/', name: 'home', full: true },
  { path: '/garage-bed/', name: 'garage-bed', viewer: true, sections: ['checks', 'mass-and-centre-of-gravity', 'bill-of-materials'] },
  { path: '/trailer/', name: 'trailer', viewer: true, full: true, sections: ['load-cases', 'checks', 'body-length', 'chassis-inputs'] },
  { path: '/trailer/', name: 'trailer-dark', viewer: true, full: true, theme: 'dark', sections: ['load-cases', 'checks'] },
  { path: `/steps/${pick('03')}/`, name: 'step-03', viewer: true, full: true },
  { path: `/steps/${pick('10')}/`, name: 'step-10', viewer: true },
  { path: `/steps/${pick('11')}/`, name: 'step-11', viewer: true },
  { path: '/drawings/', name: 'drawings', full: true },
  { path: '/research/03-bike-restraint-garage/', name: 'research-03' },
  { path: '/downloads/', name: 'downloads', full: true },
];
const browser = await chromium.launch({
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'],
});
const report = [];
for (const j of jobs) {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1100 } });
  if (j.theme) await page.addInitScript((t) => localStorage.setItem('starlight-theme', t), j.theme);
  const logs = [];
  page.on('console', (m) => logs.push(`${m.type()}: ${m.text()}`.slice(0, 300)));
  page.on('pageerror', (e) => logs.push(`pageerror: ${e.message}`.slice(0, 300)));
  const t0 = Date.now();
  const resp = await page.goto(base + j.path, { waitUntil: 'networkidle' });
  let ready = null;
  if (j.viewer) {
    try {
      await page.waitForFunction(() => document.body.dataset.cadReady === 'yes', null, { timeout: 60000 });
      ready = Date.now() - t0;
    } catch {
      ready = false;
    }
    await page.waitForTimeout(2500);
  }
  const files = [];
  const shoot = async (file, opts) => {
    await page.screenshot({ path: `${out}/${file}`, ...opts });
    files.push(file);
  };
  await shoot(`${j.name}.png`, { fullPage: !!j.full });
  if (j.viewer) {
    const el = await page.$('cad-viewer');
    if (el) {
      const r = await el.evaluate((e) => { const b = e.getBoundingClientRect(); return { y: b.top + window.scrollY, h: b.height }; });
      // the viewer plus the text that follows it, to check nothing overlaps
      await shoot(`${j.name}-viewer.png`, { clip: { x: 0, y: Math.max(0, r.y - 20), width: 1440, height: Math.min(r.h + 160, 1400) }, fullPage: true });
    }
  }
  for (const id of j.sections || []) {
    const h = await page.$(`h2#${id}`);
    if (h) {
      const y = await h.evaluate((e) => e.getBoundingClientRect().top + window.scrollY);
      await shoot(`${j.name}-${id}.png`, { clip: { x: 0, y: y - 10, width: 1440, height: 1000 }, fullPage: true });
    }
  }
  const info = await page.evaluate(() => {
    const c = document.querySelector('cad-viewer canvas');
    const v = document.querySelector('cad-viewer');
    const next = v ? v.nextElementSibling : null;
    const vb = v ? v.getBoundingClientRect() : null;
    const nb = next ? next.getBoundingClientRect() : null;
    let lowest = 0;
    if (v) v.querySelectorAll('*').forEach((e) => { const r = e.getBoundingClientRect(); if (r.height > 0) lowest = Math.max(lowest, r.bottom); });
    return {
      canvas: c ? { w: c.width, h: c.height } : null,
      viewerBottom: vb ? Math.round(vb.bottom) : null,
      contentBottom: v ? Math.round(lowest) : null,
      nextTop: nb ? Math.round(nb.top) : null,
      title: document.title,
    };
  });
  report.push({ path: j.path + (j.theme ? ` (${j.theme})` : ''), status: resp ? resp.status() : null, ready, ...info, files, logs: logs.slice(0, 12) });
  await page.close();
}
await browser.close();
fs.writeFileSync(`${out}/report.json`, JSON.stringify(report, null, 1));
console.log(JSON.stringify(report, null, 1));
