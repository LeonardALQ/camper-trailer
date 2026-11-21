// Checks that the built site scrolls: mouse wheel over text, mouse wheel over the 3D model, Ctrl+wheel zooms the
// model instead, and PageDown. Full-page screenshots cannot catch a page that will not scroll, so this does.
// Usage: node scroll-check.mjs [port] [base path, for example /camper-trailer for the GitHub Pages build].
// Writes ../build/shots/scroll-check.json and exits 1 if a check fails.
import { chromium } from 'playwright';
import fs from 'node:fs';

const port = process.argv[2] || '8791';
const base = `http://127.0.0.1:${port}${(process.argv[3] || '').replace(/\/$/, '')}`;
const pages = [
  { path: '/', viewer: false },
  { path: '/ute-garage/', viewer: true },
  { path: '/ute-garage/', viewer: true, theme: 'dark' },
  { path: '/trailer/', viewer: true, cog: 4, off: 5 },
  { path: '/trailer/', viewer: true, theme: 'dark' },
  { path: '/measurements/', viewer: false },
  { path: '/body/', viewer: true },
  { path: '/tow-vehicle/', viewer: false },
  { path: '/drawings/', viewer: false },
  { path: '/research/03-bike-restraint-garage/', viewer: false },
  { path: '/research/18-trailer-layout-79/', viewer: false, off: 1 },
  { path: '/research/', viewer: false, off: 1 },
  { path: '/electrical/', viewer: false, off: 3 },
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

  // The tables' footer on Sum: blank where a sum means nothing, and the centre of gravity of the rows weighted by
  // their mass in the CoG columns, worked out here from the cells.
  const foot = await page.evaluate(() => {
    const num = (s) => {
      const m = (s || '').replace(/,/g, '').replace('−', '-').match(/[+-]?\d+(?:\.\d+)?/);
      return m ? Number(m[0]) : null;
    };
    const out = { off: 0, cog: 0, bad: [] };
    document.querySelectorAll('table.sheet-table').forEach((t, k) => {
      const cells = [...(t.tFoot?.rows[0]?.cells ?? [])];
      const rows = [...t.tBodies[0].rows].filter((r) => !r.classList.contains('row-total')
        && !r.classList.contains('sheet-out') && ![...r.cells].some((c) => c.colSpan > 1));
      const mass = cells.findIndex((c) => c.hasAttribute('data-mass'));
      const heads = [...(t.tHead?.rows[t.tHead.rows.length - 1]?.cells ?? [])].map((h) => h.textContent.trim());
      // a cell's number and unit by the sheet's own rule (sheet.ts parseNumber): one number, an allowed prefix and unit
      const PREFIXES = new Set(['', 'AUD', 'A$', '$', 'US$', 'USD', 'EUR', '€', 'GBP', '£', '~', '≈', 'about']);
      const NUMBER = /^([A-Za-z$€£~≈]{0,5})\s?([+\-−]?)(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?(?:\s?(.*))?$/;
      const UNIT = /^(?:[A-Za-zµ°%²³·/]{1,8}(?: [A-Za-zµ°%²³·/]{1,8})?)?(?: ?\((?:est\.?|estimate)\))?$/;
      const CUR = { AUD: 'AUD', A$: 'AUD', $: 'AUD', US$: 'USD', USD: 'USD', EUR: 'EUR', '€': 'EUR', GBP: 'GBP', '£': 'GBP' };
      const unit = (raw) => {
        const s = (raw || '').replace(/\s+/g, ' ').trim();
        const m = s && s.length <= 40 ? s.match(NUMBER) : null;
        if (!m || !PREFIXES.has(m[1]) || !UNIT.test(m[5] ?? '')) return null;
        return { suf: (m[5] ?? '').replace(/\s*\((?:est\.?|estimate)\)$/, ''), cur: CUR[m[1]] ?? '' };
      };
      cells.forEach((td, c) => {
        const text = td.textContent.trim();
        if (td.dataset.sum === 'sum') {
          const parsed = rows.map((r) => r.cells[c]?.textContent.trim() ?? '').filter(Boolean).map(unit);
          const units = new Set(parsed.filter(Boolean).map((u) => u.suf));
          const curs = new Set(parsed.filter(Boolean).map((u) => u.cur).filter(Boolean));
          if (parsed.includes(null)) out.bad.push(`table ${k + 1} column ${c + 1} sums a column with cells that are not one number`);
          if (units.size > 1 || curs.size > 1) out.bad.push(`table ${k + 1} column ${c + 1} sums mixed units: ${[...units, ...curs].join(', ')}`);
          if (c === 0 || /^(id|report|no\.?|number|#|mark|line|ref|revision|rev)$/i.test(heads[c] ?? '')) {
            out.bad.push(`table ${k + 1} column ${c + 1} (${heads[c]}) sums ids`);
          }
        }
        if (td.dataset.sum === 'off') {
          out.off += 1;
          if (text) out.bad.push(`table ${k + 1} column ${c + 1} shows ${text}`);
        } else if (td.dataset.sum === 'cog') {
          out.cog += 1;
          let m = 0;
          let mx = 0;
          for (const r of rows) {
            const w = num(r.cells[mass]?.textContent);
            const x = num(r.cells[c]?.textContent);
            if (w !== null && x !== null) {
              m += w;
              mx += w * x;
            }
          }
          const dec = (text.split(' ')[0].split('.')[1] ?? '').length;
          const got = num(text);
          if (got === null || Math.abs(got - mx / m) > 0.5 * 10 ** -dec + 1e-6) {
            out.bad.push(`table ${k + 1} column ${c + 1} shows ${text}, the weighted centre is ${(mx / m).toFixed(2)}`);
          }
        }
      });
    });
    return out;
  });
  check('footer Sum blank where a sum means nothing, CoG weighted by mass',
    !foot.bad.length && foot.cog >= (p.cog ?? 0) && foot.off >= (p.off ?? 0), foot);

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
