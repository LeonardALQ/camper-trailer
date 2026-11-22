// Headless Chromium screenshots of the built site served on 127.0.0.1 (Playwright image, --network host).
// Usage: node shot.mjs [port]. Writes PNGs and report.json into ../build/shots/.
import { chromium } from 'playwright';
import fs from 'node:fs';

const port = process.argv[2] || '8791';
const base = `http://127.0.0.1:${port}`;
const out = '../build/shots';
fs.mkdirSync(out, { recursive: true });

const jobs = [
  { path: '/', name: 'home', full: true },
  { path: '/trailer/', name: 'trailer', viewer: true, full: true, sections: ['load-cases', 'checks', 'chassis-inputs'] },
  { path: '/measurements/', name: 'measurements', full: true },
  { path: '/measurements/', name: 'measurements-dark', full: true, theme: 'dark' },
  { path: '/trailer/', name: 'trailer-dark', viewer: true, full: true, theme: 'dark', sections: ['load-cases', 'checks'] },
  { path: '/body/', name: 'body', viewer: true, full: true, sections: ['checks', 'panels', 'mass'] },
  { path: '/body/', name: 'body-inside', viewer: true, nth: 1 },
  // the fit-out with the body's panels hidden (H27): bed up and bed down, then into the wet room and the laundry
  { path: '/body/', name: 'body-fitout-day', viewer: true, nth: 1, look: { hide: ['/ASM-BD/Body'] } },
  { path: '/body/', name: 'body-fitout-night', viewer: true, nth: 2, look: { hide: ['/ASM-BD/Body'] } },
  { path: '/body/', name: 'body-wet-room', viewer: true, nth: 1,
    look: { hide: ['/ASM-BD/Body'], target: [5700, 0, 1500], from: [3200, -2400, 2200], zoom: 2.4 } },
  { path: '/body/', name: 'body-laundry', viewer: true, nth: 1,
    look: { hide: ['/ASM-BD/Body'], target: [4650, -650, 1500], from: [-600, 2200, 3500], zoom: 2.4 } },
  { path: '/ute-garage/', name: 'ute-garage', viewer: true, full: true, sections: ['checks', 'mass'] },
  { path: '/ute-garage/', name: 'ute-garage-loading', viewer: true, nth: 1 },
  { path: '/tow-vehicle/', name: 'tow-vehicle', full: true },
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
  if (j.look) {
    // hide groups and point the camera at a target from an offset, on the job's viewer
    await page.evaluate((look) => {
      const v = document.querySelectorAll('cad-viewer')[look.nth].viewer;
      for (const p of look.hide || []) v.setState(p, [0, 0]);
      if (look.target) {
        v.setCameraTarget(look.target);
        v.setCameraPosition(look.target.map((t, i) => t + look.from[i]));
        v.setCameraZoom(look.zoom);
      }
    }, { ...j.look, nth: j.nth || 0 });
    await page.waitForTimeout(1500);
  }
  const files = [];
  const shoot = async (file, opts) => {
    await page.screenshot({ path: `${out}/${file}`, ...opts });
    files.push(file);
  };
  await shoot(`${j.name}.png`, { fullPage: !!j.full });
  if (j.viewer) {
    const el = (await page.$$('cad-viewer'))[j.nth || 0];
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
