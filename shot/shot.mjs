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
  { path: '/ute-garage/', name: 'ute-garage', viewer: true, full: true, sections: ['checks', 'mass'] },
  { path: '/ute-garage/', name: 'ute-garage-loading', viewer: true, nth: 1 },
  { path: '/tow-vehicle/', name: 'tow-vehicle', full: true },
  { path: '/drawings/', name: 'drawings', full: true },
  { path: '/research/03-bike-restraint-garage/', name: 'research-03' },
  { path: '/downloads/', name: 'downloads', full: true },
  // the trailer page's floor plan (H28), probed by pointing at the washer and clicking it, and the viewers' plan view
  { path: '/trailer/', name: 'trailer-floorplan', el: '.fp', probe: 'LA-02' },
  { path: '/trailer/', name: 'trailer-floorplan-dark', el: '.fp', theme: 'dark' },
  { path: '/trailer/', name: 'trailer-plan-view', viewer: true, plan: true },
  { path: '/body/', name: 'body-inside-plan-view', viewer: true, nth: 1, plan: true },
  { path: '/body/', name: 'body-inside-night-plan-view', viewer: true, nth: 2, plan: true },
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
  const probe = {};
  if (j.plan) {
    // press the viewer's Floor plan button, then point at the middle of the canvas and read the tooltip
    const v = (await page.$$('cad-viewer'))[j.nth || 0];
    const b = v && (await v.$('.cad-plan button'));
    if (b) {
      await b.click();
      await page.waitForTimeout(2500);
      const c = await (await v.$('canvas')).boundingBox();
      await page.mouse.move(c.x + c.width * 0.45, c.y + c.height * 0.5);
      await page.waitForTimeout(1200);
      probe.button = await b.textContent();
      probe.tip = await v.$eval('.cad-tip', (t) => (t.hidden ? null : t.textContent));
      // click the part for its card, hide it with the card and show it again
      await page.mouse.click(c.x + c.width * 0.45, c.y + c.height * 0.5);
      await page.waitForTimeout(800);
      probe.card = await v.$eval('.cad-card', (t) => (t.hidden ? null : t.querySelector('h4')?.textContent));
      const hide = await v.$('.cad-card button[data-act="hide"]');
      if (hide) {
        await hide.click();
        await page.waitForTimeout(500);
        probe.hidden = await v.$eval('.cad-card button[data-act="hide"]', (t) => t.textContent);
        await (await v.$('.cad-card button[data-act="hide"]')).click();
        await page.waitForTimeout(500);
        await (await v.$('.cad-card button[data-act="close"]')).click();
        await page.waitForTimeout(800);
      }
    } else probe.button = null;
  }
  if (j.el) {
    const e = await page.$(j.el);
    if (e) {
      await e.screenshot({ path: `${out}/${j.name}.png` });
      files.push(`${j.name}.png`);
    }
    if (e && j.probe) {
      // point at a part of the plan, read the tooltip, click it and read where the row was found
      const p = await e.$(`.fp-part[data-iid="${j.probe}"]`);
      const r = await p.boundingBox();
      await page.mouse.move(r.x + r.width / 2, r.y + r.height / 2);
      await page.waitForTimeout(300);
      probe.tip = await e.$eval('.fp-tip', (t) => (t.hidden ? null : t.textContent));
      await page.mouse.click(r.x + r.width / 2, r.y + r.height / 2);
      await page.waitForTimeout(1500);
      probe.msg = await e.$eval('.fp-msg', (t) => t.textContent);
      probe.selected = await page.evaluate(() => Array.from(document.querySelectorAll('tr.is-selected'), (r) => r.cells[0]?.textContent));
    }
  } else await shoot(`${j.name}.png`, { fullPage: !!j.full });
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
  report.push({ path: j.path + (j.theme ? ` (${j.theme})` : ''), status: resp ? resp.status() : null, ready, ...info, files,
    ...(Object.keys(probe).length ? { probe } : {}), logs: logs.slice(0, 12) });
  await page.close();
}
await browser.close();
fs.writeFileSync(`${out}/report.json`, JSON.stringify(report, null, 1));
console.log(JSON.stringify(report, null, 1));
