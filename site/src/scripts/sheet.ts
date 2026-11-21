// Spreadsheet tools for every table in the page content (S-03): a frame of about 12 rows that scrolls inside itself
// with a sticky header row, first column and footer, row selection, a footer with the sum, mean, min, max or count of
// the selected rows (Sum leaves a column blank where a sum means nothing, see sumModes), sorting, a filter, copy as
// tab-separated text and CSV download. The Footer override loads it on every page. Without JavaScript the tables
// render as plain tables.
//
// Other scripts talk to it with events on `document`:
//   ct:find-row     {ids, found}  the 3D viewer's "Find in table": scroll to the first row whose first cell is one of
//                                 the ids, select it and set `found`
//   ct:parts-ready  {ids}         a 3D viewer has loaded the part ids it knows, so tables with those rows offer
//                                 "Show in 3D"
//   ct:show-parts   {ids, count}  sent by "Show in 3D". A viewer that knows the parts highlights them and sets `count`
// and with `ct:sheet-refresh` on a table when a script changes its cells. A script that hides rows of its own (the
// Measurements page's part filter) sets `data-sheet-hide` on them and sends `ct:sheet-filter` on the table: those rows
// then count as filtered out, as the filter box does.

const ROWS_VISIBLE = 12;
const FRAME_MAX_VH = 0.75;
const LONG_CHARS = 40;
const SHORT_CHARS = 24;
const BLOCKS = 'div, p, ul, ol, table, details, pre, input, select, textarea';
const STATS = ['Sum', 'Mean', 'Min', 'Max', 'Count'] as const;
type Stat = (typeof STATS)[number];
type Kind = 'group' | 'total';
// What Sum shows in a column: the sum, nothing (where a sum means nothing), or the centre of gravity of the rows
// weighted by the table's mass column.
type SumMode = 'sum' | 'off' | 'cog';

// The generated tables say what Sum does with data-sheet-sum="sum", "off" or "cog" on a header cell, or on the table
// or an element around it for every column, and name their mass column with data-sheet-mass. A table with neither is
// read by its header text: no sum for centre of gravity coordinates, positions and sizes, percentages and shares,
// limits, ratings, ranges and values per unit, and none at all where the rows are alternatives (cases, options).
const NO_SUM = /\bcog\b|centre of gravity|%|percent|\bshare\b|ratio|utilisation|factor|\bssf\b|\bcop\b|\bmm\b|^[xyz]$|position|height|station|limit|\bmax|\bmin\b|minimum|rating|rated|target|range|margin|\bmpa\b|\/|\bper\b|degree|°c|rpm|km\/h|\bpeak\b|^value$|clearance|\bgap\b/i;
const ALTERNATIVES = /^(case|cases|limit|limits|rule|check|mode|option|options|variant|candidate|design day|input|dimension|size|reading|level|speed|gear|day|unit|model|product|panel|family|kit|build|tuner|turbo|deck|track|measure)\b/i;
const COG = /\bcog\b|centre of gravity/i;
const MASS = /^(mass|kg|mass kg|mass \(kg\)|tare kg)$/i;
const ID = /^(id|report|no\.?|number|#|mark|line|ref|revision|rev)$/i;
const CURRENCY: Record<string, string> = { AUD: 'AUD', A$: 'AUD', $: 'AUD', US$: 'USD', USD: 'USD', EUR: 'EUR', '€': 'EUR', GBP: 'GBP', '£': 'GBP' };

export interface Parsed {
  v: number;
  dec: number;
  pre: string;
  suf: string;
}

// Words and symbols allowed in front of a number ("AUD 1,287") and the units allowed after it ("37 kg", "12.5 %",
// "8.95 kg/m", "3,500 kg (est.)"). Anything else, a second number included ("440 to 460"), makes a cell text.
const PREFIXES = new Set(['', 'AUD', 'A$', '$', 'US$', 'USD', 'EUR', '€', 'GBP', '£', '~', '≈', 'about']);
const NUMBER = /^([A-Za-z$€£~≈]{0,5})\s?([+\-−]?)(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?(?:\s?(.*))?$/;
const UNIT = /^(?:[A-Za-zµ°%²³·/]{1,8}(?: [A-Za-zµ°%²³·/]{1,8})?)?(?: ?\((?:est\.?|estimate)\))?$/;
const EST = /\s*\((?:est\.?|estimate)\)$/;

export function parseNumber(raw: string): Parsed | null {
  const s = raw.replace(/\s+/g, ' ').trim();
  if (!s || s.length > 40) return null;
  const m = s.match(NUMBER);
  if (!m) return null;
  const [, pre, sign, int, frac = '', suf = ''] = m;
  if (!PREFIXES.has(pre) || !UNIT.test(suf)) return null;
  const v = Number(int.replace(/,/g, '') + frac) * (sign === '-' || sign === '−' ? -1 : 1);
  return Number.isFinite(v) ? { v, dec: frac ? frac.length - 1 : 0, pre, suf: suf.replace(EST, '') } : null;
}

const norm = (s: string) => s.replace(/\s+/g, ' ').trim();

function cellText(cell: Element | null | undefined): string {
  if (!cell) return '';
  const field = cell.querySelector('input, select, textarea') as HTMLInputElement | null;
  if (field && field.type !== 'checkbox') return norm(field.value);
  return norm(cell.textContent ?? '');
}

function slug(s: string): string {
  return s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'table';
}

const INTERACTIVE = 'a, button, input, select, textarea, summary, label, [contenteditable="true"]';
const known = new Set<string>();   // part ids the page's 3D viewers know
const sheets: Sheet[] = [];
const frames = new Map<Element, Sheet>();

function fit(list: Sheet[]) {
  const m = list.map((s) => s.measure());
  list.forEach((s, i) => s.apply(m[i]));
}

// One observer for every frame, so a change of width re-measures them all in one pass. Only a change of width
// matters: the frame's own height follows from the measurement.
const resized = new ResizeObserver((entries) => {
  const list = entries.map((e) => frames.get(e.target)).filter((s): s is Sheet => !!s && s.frame.clientWidth !== s.width);
  if (list.length) fit(list);
});

class Sheet {
  readonly root = document.createElement('div');
  readonly frame = document.createElement('div');
  readonly table: HTMLTableElement;
  readonly head: HTMLTableRowElement | null;
  readonly heads: (HTMLTableCellElement | null)[] = [];
  readonly ncols: number;
  readonly order: HTMLTableRowElement[];          // every body row, in the page's order
  readonly rows: HTMLTableRowElement[];           // the data rows, in the page's order
  readonly kind = new Map<HTMLTableRowElement, Kind>();
  readonly cols = new Map<HTMLTableRowElement, (HTMLTableCellElement | null)[]>();
  readonly nums = new Map<HTMLTableRowElement, (Parsed | null)[]>();
  readonly sel = new Set<HTMLTableRowElement>();
  readonly foot: HTMLTableCellElement[] = [];
  numeric: boolean[] = [];
  mixed: boolean[] = [];   // the column mixes units or currencies, or has filled cells that are not one number
  sums: SumMode[] = [];
  mass = -1;   // the mass column the centre of gravity columns are weighted by
  fmt: { dec: number; pre: string; suf: string }[] = [];
  stat: Stat = 'Sum';
  sortCol = -1;
  sortDir = 0;   // 1 ascending, -1 descending, 0 the page's order
  anchor: HTMLTableRowElement | null = null;
  width = 0;
  ui!: {
    filter: HTMLInputElement; count: HTMLSpanElement; stat: HTMLSelectElement; show3d: HTMLButtonElement;
    msg: HTMLSpanElement;
  };

  constructor(table: HTMLTableElement, readonly index: number) {
    this.table = table;
    const headRows = table.tHead ? Array.from(table.tHead.rows) : [];
    let head = headRows.length ? headRows[headRows.length - 1] : null;
    const bodyRows = Array.from(table.tBodies).flatMap((b) => Array.from(b.rows));
    if (!head && bodyRows.length && Array.from(bodyRows[0].cells).every((c) => c.tagName === 'TH')) head = bodyRows.shift()!;
    this.head = head;
    this.order = bodyRows;
    this.ncols = Math.max(head ? this.span(head).length : 0, ...bodyRows.map((r) => this.span(r).length), 1);
    if (head) this.heads.push(...this.span(head));
    for (const r of bodyRows) {
      const cells = this.span(r);
      this.cols.set(r, cells);
      const merged = r.cells.length < this.ncols && Array.from(r.cells).some((c) => c.colSpan > 1);
      if (r.classList.contains('row-total')) this.kind.set(r, 'total');
      else if (merged) this.kind.set(r, 'group');
    }
    this.rows = bodyRows.filter((r) => !this.kind.has(r));
    this.rows.forEach((r) => this.parse(r));
    this.detect();
    this.texts();
    this.build();
  }

  // Long text gets room to read: a minimum width, so a table with many number columns does not squeeze it into a
  // column of single words. In a table that scrolls it shows two lines, so about 12 rows fit the frame. The full text
  // is in the cell's tooltip, the Wrap button shows all of it, and print always does. Cells holding blocks (lists,
  // details, inputs) keep their layout.
  texts() {
    const clamp = this.order.length > ROWS_VISIBLE;
    for (const th of this.heads) if (th && norm(th.textContent ?? '').length <= SHORT_CHARS) th.classList.add('sheet-short');
    for (const r of this.rows) {
      for (const c of Array.from(r.cells)) {
        const text = norm(c.textContent ?? '');
        if (c.querySelector(BLOCKS)) continue;
        if (text.length <= SHORT_CHARS) c.classList.add('sheet-short');
        if (text.length <= LONG_CHARS) continue;
        const d = document.createElement('div');
        d.className = 'sheet-text';
        if (clamp) d.title = text;
        d.append(...Array.from(c.childNodes));
        c.append(d);
        if (clamp) this.table.classList.add('sheet-clamped');
      }
    }
  }

  // Cells by column, so a cell spanning two columns sits in both.
  span(r: HTMLTableRowElement): (HTMLTableCellElement | null)[] {
    const out: (HTMLTableCellElement | null)[] = [];
    for (const c of Array.from(r.cells)) {
      out.push(c);
      for (let k = 1; k < c.colSpan; k++) out.push(null);
    }
    return out;
  }

  parse(r: HTMLTableRowElement) {
    this.nums.set(r, this.cols.get(r)!.map((c) => (c ? parseNumber(cellText(c)) : null)));
  }

  // A column is numeric when at least half of its filled cells hold one number, unless its header says
  // data-sheet-type="text". The footer formats its result like the column: the most decimals used, and the unit when
  // every cell shares it.
  detect() {
    this.numeric = [];
    this.mixed = [];
    this.fmt = [];
    for (let c = 0; c < this.ncols; c++) {
      let filled = 0;
      const got: Parsed[] = [];
      for (const r of this.rows) {
        if (cellText(this.cols.get(r)![c])) filled += 1;
        const p = this.nums.get(r)![c];
        if (p) got.push(p);
      }
      this.numeric.push(got.length > 0 && got.length * 2 >= filled && this.heads[c]?.dataset.sheetType !== 'text');
      const same = (k: 'pre' | 'suf') => (got.every((p) => p[k] === got[0]?.[k]) ? got[0]?.[k] ?? '' : '');
      this.fmt.push({ dec: Math.max(0, ...got.map((p) => p.dec)), pre: same('pre'), suf: same('suf') });
      // a sum needs one unit and one currency, and every filled cell a number, or it would cover only some rows
      const currencies = new Set(got.map((p) => CURRENCY[p.pre] ?? '').filter(Boolean));
      this.mixed.push(new Set(got.map((p) => p.suf)).size > 1 || currencies.size > 1 || got.length < filled);
    }
    this.sumModes();
  }

  sumModes() {
    const text = (c: number) => norm(this.heads[c]?.textContent ?? '');
    const whole = this.table.closest<HTMLElement>('[data-sheet-sum]')?.dataset.sheetSum;
    const own = (c: number) => (this.heads[c]?.dataset.sheetSum ?? whole) as SumMode | undefined;
    const marked = !!whole || this.heads.some((th) => th?.dataset.sheetSum || th?.hasAttribute('data-sheet-mass'));
    this.mass = this.heads.findIndex((th, c) => this.numeric[c]
      && (marked ? !!th?.hasAttribute('data-sheet-mass') : MASS.test(text(c))));
    const alternatives = !marked && ALTERNATIVES.test(text(0));
    this.sums = this.numeric.map((num, c) => {
      const set = own(c);
      const mode: SumMode = marked ? (set === 'off' || set === 'cog' ? set : 'sum')
        : alternatives ? 'off' : COG.test(text(c)) ? 'cog' : NO_SUM.test(text(c)) ? 'off' : 'sum';
      // never a sum of mixed units, of ids or numbers that name a row, or of the first column, which names the rows
      const naming = c === 0 || ID.test(text(c));
      return !num || this.mixed[c] || naming || (mode === 'cog' && this.mass < 0) ? 'off' : mode;
    });
  }

  // The centre of gravity of the rows in column c, weighted by the mass column, from the rows that have both.
  weighted(rows: HTMLTableRowElement[], c: number): number | null {
    let m = 0;
    let mx = 0;
    for (const r of rows) {
      const w = this.nums.get(r)![this.mass]?.v;
      const x = this.nums.get(r)![c]?.v;
      if (w === undefined || x === undefined) continue;
      m += w;
      mx += w * x;
    }
    return m ? mx / m : null;
  }

  isData(r: Element | null): r is HTMLTableRowElement {
    return !!r && this.cols.has(r as HTMLTableRowElement) && !this.kind.has(r as HTMLTableRowElement);
  }

  shown(): HTMLTableRowElement[] {
    return Array.from(this.table.querySelectorAll('tbody tr')).filter(
      (r) => this.isData(r) && !r.classList.contains('sheet-out'),
    ) as HTMLTableRowElement[];
  }

  // The rows the footer, Copy, CSV and Show in 3D act on: the selected rows still shown, or every shown row.
  target(): HTMLTableRowElement[] {
    const shown = this.shown();
    const picked = shown.filter((r) => this.sel.has(r));
    return picked.length ? picked : shown;
  }

  // ------------------------------------------------------------------ the frame, the tools and the footer
  build() {
    const t = this.table;
    const holder = t.closest('.data-table');
    holder?.classList.add('has-sheet');
    this.root.className = 'sheet';
    this.frame.className = 'sheet-frame';
    t.parentNode!.insertBefore(this.root, t);
    const tools = document.createElement('div');
    tools.className = 'sheet-tools';
    const btn = (label: string, title: string, act: () => void) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.textContent = label;
      b.title = title;
      b.addEventListener('click', act);
      return b;
    };
    const filter = document.createElement('input');
    filter.type = 'search';
    filter.placeholder = 'Filter';
    filter.setAttribute('aria-label', 'Show only the rows that contain this text');
    filter.addEventListener('input', () => this.applyFilter());
    const count = document.createElement('span');
    count.className = 'sheet-count';
    const stat = document.createElement('select');
    stat.setAttribute('aria-label', 'What the footer row shows');
    stat.title = 'What the footer row shows for each number column';
    for (const s of STATS) stat.add(new Option(s, s));
    stat.addEventListener('change', () => {
      this.stat = stat.value as Stat;
      this.refresh();
    });
    const show3d = btn('Show in 3D', 'Highlight the selected rows in the 3D model on this page', () => this.show3d());
    show3d.hidden = true;
    const wrap = btn('Wrap', 'Show all the text in every cell, or two lines of it', () => {
      const on = t.classList.toggle('sheet-wrap');
      wrap.setAttribute('aria-pressed', String(on));
      fit([this]);
    });
    wrap.setAttribute('aria-pressed', 'false');
    wrap.hidden = !t.classList.contains('sheet-clamped');
    const msg = document.createElement('span');
    msg.className = 'sheet-msg';
    msg.setAttribute('role', 'status');
    tools.append(
      filter, count,
      btn('All', 'Select every row shown', () => this.selectAll()),
      btn('None', 'Clear the selection (Escape)', () => this.clear(true)),
      stat,
      btn('Copy', 'Copy the selected rows, or every row shown, as tab-separated text for a spreadsheet', () => this.copy()),
      btn('CSV', 'Download the selected rows, or every row shown, as a CSV file', () => this.csv()),
      wrap, show3d, msg,
    );
    this.ui = { filter, count, stat, show3d, msg };
    this.root.append(tools, this.frame);
    this.frame.append(t);
    t.classList.add('sheet-table');
    t.setAttribute('role', 'grid');
    t.setAttribute('aria-multiselectable', 'true');
    // Number columns align right, as the component tables already do with their own class.
    for (let c = 0; c < this.ncols; c++) {
      if (!this.numeric[c]) continue;
      for (const cell of [this.heads[c], ...this.rows.map((r) => this.cols.get(r)![c])]) {
        if (cell && !cell.classList.contains('num') && !cell.hasAttribute('align')) cell.classList.add('sheet-num');
      }
    }
    if (this.numeric.some(Boolean)) {
      const tf = t.createTFoot();
      tf.className = 'sheet-foot';
      const tr = tf.insertRow();
      for (let c = 0; c < this.ncols; c++) {
        const td = document.createElement('td');
        if (this.numeric[c]) {
          td.className = 'num';
          td.dataset.sum = this.sums[c];
        }
        if (c === this.mass) td.dataset.mass = '';
        if (this.sums[c] === 'cog') td.title = 'Sum: the centre of gravity of these rows, weighted by their mass';
        tr.append(td);
        this.foot.push(td);
      }
    }
    this.rows.forEach((r) => {
      r.tabIndex = -1;
      r.setAttribute('aria-selected', 'false');
    });
    if (this.rows[0]) this.rows[0].tabIndex = 0;
    this.heads.forEach((th, c) => {
      if (!th || th.colSpan > 1) return;
      th.classList.add('sheet-sort');
      th.tabIndex = 0;
      th.setAttribute('aria-sort', 'none');
      th.title = 'Sort by this column. Click again to reverse, a third time for the page order';
      th.addEventListener('click', (e) => {
        if (!(e.target as Element).closest('a')) this.sortBy(c);
      });
      th.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          this.sortBy(c);
        }
      });
    });
    // Shift-click and Ctrl or Cmd-click pick rows, so they must not extend a text selection.
    this.frame.addEventListener('mousedown', (e) => {
      if ((e.shiftKey || e.ctrlKey || e.metaKey) && this.isData((e.target as Element).closest('tr'))) e.preventDefault();
    });
    this.frame.addEventListener('click', (e) => this.onClick(e));
    this.frame.addEventListener('keydown', (e) => this.onKey(e));
    // The 3D viewer listens for its own shortcut keys on the whole document. Keys typed in a table stay here.
    this.root.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && !(e.target === filter && filter.value)) this.clear(true);
      e.stopPropagation();
    });
    t.addEventListener('input', (e) => this.edited(e));
    t.addEventListener('change', (e) => this.edited(e));
    t.addEventListener('ct:sheet-refresh', () => {
      this.rows.forEach((r) => this.parse(r));
      this.refresh();
    });
    t.addEventListener('ct:sheet-filter', () => this.applyFilter());
    frames.set(this.frame, this);
    resized.observe(this.frame);
    if (this.rows.some((r) => r.hasAttribute('data-sheet-hide'))) this.applyFilter();
    else this.refresh();
    this.update3d();
  }

  edited(e: Event) {
    const r = (e.target as Element).closest('tr');
    if (this.isData(r)) {
      this.parse(r);
      this.refresh();
    }
  }

  // About 12 rows high, measured on the rows themselves, and never more than 75 % of the window. A first column wider
  // than a third of the frame does not stick, or it would cover the columns scrolled under it. All frames are measured
  // first and then sized, so the page lays out once.
  measure(): { h: number; wide: boolean } | null {
    this.width = this.frame.clientWidth;
    const body = Array.from(this.table.querySelectorAll('tbody tr')) as HTMLTableRowElement[];
    const seen = body.filter((r) => r.offsetHeight > 0).slice(0, ROWS_VISIBLE);
    if (!seen.length || !this.width) return null;
    const h = (this.table.tHead?.offsetHeight ?? 0) + (this.table.tFoot?.offsetHeight ?? 0)
      + seen.reduce((s, r) => s + r.offsetHeight, 0) + 2;
    const first = this.rows.find((r) => r.offsetHeight > 0)?.cells[0];
    return { h, wide: (first?.offsetWidth ?? 0) > this.width / 3 };
  }

  apply(m: { h: number; wide: boolean } | null) {
    if (!m) return;
    this.table.classList.toggle('sheet-free-first', m.wide);
    const scroll = this.order.length > ROWS_VISIBLE;
    this.frame.classList.toggle('sheet-scroll', scroll);
    this.frame.style.maxHeight = scroll ? `${Math.round(Math.min(m.h, window.innerHeight * FRAME_MAX_VH))}px` : '';
  }

  // ------------------------------------------------------------------ selection
  mark(r: HTMLTableRowElement, on: boolean) {
    if (on) this.sel.add(r);
    else this.sel.delete(r);
    r.classList.toggle('is-selected', on);
    r.setAttribute('aria-selected', String(on));
  }

  clear(update = false) {
    for (const r of Array.from(this.sel)) this.mark(r, false);
    if (update) this.refresh();
  }

  selectAll() {
    for (const r of this.shown()) this.mark(r, true);
    this.refresh();
  }

  range(a: HTMLTableRowElement, b: HTMLTableRowElement, add: boolean) {
    const shown = this.shown();
    const i = shown.indexOf(a);
    const j = shown.indexOf(b);
    if (i < 0 || j < 0) return;
    if (!add) this.clear();
    for (const r of shown.slice(Math.min(i, j), Math.max(i, j) + 1)) this.mark(r, true);
  }

  onClick(e: MouseEvent) {
    const target = e.target as Element;
    if (target.closest(INTERACTIVE)) return;
    const r = target.closest('tr');
    if (!this.isData(r)) return;
    const text = window.getSelection();
    if (text && !text.isCollapsed && r.contains(text.anchorNode)) return;   // the reader is selecting text
    if (e.shiftKey && this.anchor && this.shown().includes(this.anchor)) {
      this.range(this.anchor, r, e.ctrlKey || e.metaKey);
    } else if (e.ctrlKey || e.metaKey) {
      this.mark(r, !this.sel.has(r));
      this.anchor = r;
    } else {
      const only = this.sel.size === 1 && this.sel.has(r);
      this.clear();
      if (!only) this.mark(r, true);
      this.anchor = r;
    }
    this.focus(r, false);
    this.refresh();
  }

  onKey(e: KeyboardEvent) {
    const target = e.target as Element;
    if (target.closest(INTERACTIVE) || target.closest('th')) return;
    const r = target.closest('tr');
    if (!this.isData(r)) return;
    const shown = this.shown();
    const i = shown.indexOf(r);
    let next: HTMLTableRowElement | undefined;
    if (e.key === 'ArrowDown') next = shown[Math.min(i + 1, shown.length - 1)];
    else if (e.key === 'ArrowUp') next = shown[Math.max(i - 1, 0)];
    else if (e.key === 'Home') next = shown[0];
    else if (e.key === 'End') next = shown[shown.length - 1];
    if (next) {
      e.preventDefault();
      if (e.shiftKey) {
        this.anchor ??= r;
        this.range(this.anchor, next, false);
      }
      this.focus(next, true);
      this.refresh();
    } else if (e.key === ' ') {
      e.preventDefault();
      this.mark(r, !this.sel.has(r));
      this.anchor = r;
      this.refresh();
    } else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'a') {
      e.preventDefault();
      this.selectAll();
    }
  }

  // Focus a row and scroll the frame so it is not under the sticky header or footer.
  focus(r: HTMLTableRowElement, scroll: boolean) {
    for (const x of this.rows) x.tabIndex = x === r ? 0 : -1;
    r.focus({ preventScroll: true });
    if (!scroll) return;
    const f = this.frame;
    const top = this.table.tHead?.offsetHeight ?? 0;
    const bottom = this.table.tFoot?.offsetHeight ?? 0;
    if (r.offsetTop < f.scrollTop + top) f.scrollTop = r.offsetTop - top;
    else if (r.offsetTop + r.offsetHeight > f.scrollTop + f.clientHeight - bottom) {
      f.scrollTop = r.offsetTop + r.offsetHeight - f.clientHeight + bottom;
    }
    const b = r.getBoundingClientRect();
    if (b.top < 0 || b.bottom > window.innerHeight) this.root.scrollIntoView({ block: 'nearest' });
  }

  // ------------------------------------------------------------------ sort and filter
  sortBy(c: number) {
    if (this.sortCol !== c) {
      this.sortCol = c;
      this.sortDir = 1;
    } else {
      this.sortDir = this.sortDir === 1 ? -1 : this.sortDir === -1 ? 0 : 1;
    }
    this.heads.forEach((th, k) => th?.setAttribute('aria-sort',
      k !== c || this.sortDir === 0 ? 'none' : this.sortDir === 1 ? 'ascending' : 'descending'));
    const body = this.table.tBodies[0];
    const place = new Map(this.order.map((r, i) => [r, i]));
    let list: HTMLTableRowElement[];
    if (this.sortDir === 0) {
      list = this.order;
    } else {
      const num = this.numeric[c];
      const key = (r: HTMLTableRowElement): number | string | null => {
        if (num) return this.nums.get(r)![c]?.v ?? null;
        const s = cellText(this.cols.get(r)![c]);
        return s || null;
      };
      const d = this.sortDir;
      const data = this.rows.slice().sort((a, b) => {
        const ka = key(a);
        const kb = key(b);
        if (ka === null || kb === null) return ka === kb ? place.get(a)! - place.get(b)! : ka === null ? 1 : -1;
        const cmp = typeof ka === 'number' && typeof kb === 'number'
          ? ka - kb : String(ka).localeCompare(String(kb), 'en', { numeric: true, sensitivity: 'base' });
        return cmp * d || place.get(a)! - place.get(b)!;
      });
      list = [...data, ...this.order.filter((r) => this.kind.get(r) === 'total')];
    }
    body.append(...list);
    this.applyFilter();
  }

  // Group rows (a heading across the table) only make sense in the page's order with nothing filtered, and total
  // rows only with nothing filtered.
  applyFilter() {
    const q = this.ui.filter.value.trim().toLowerCase();
    let hidden = false;
    for (const r of this.rows) {
      const text = Array.from(r.cells).map(cellText).join(' ').toLowerCase();
      const out = r.hasAttribute('data-sheet-hide') || (!!q && !text.includes(q));
      hidden ||= r.hasAttribute('data-sheet-hide');
      r.classList.toggle('sheet-out', out);
      if (out && this.sel.has(r)) this.mark(r, false);
    }
    for (const [r, kind] of this.kind) r.classList.toggle('sheet-off', !!q || hidden || (kind === 'group' && this.sortDir !== 0));
    this.refresh();
  }

  // ------------------------------------------------------------------ footer and count
  format(c: number, v: number, stat: Stat): string {
    if (stat === 'Count') return v.toLocaleString('en-AU');
    const f = this.fmt[c];
    const dec = stat === 'Mean' ? Math.min(f.dec + 1, 3) : f.dec;
    const s = (Math.abs(v) < 0.5 * 10 ** -dec ? 0 : v).toLocaleString('en-AU', { minimumFractionDigits: dec, maximumFractionDigits: dec });
    const pre = f.pre ? (/^[A-Za-z]/.test(f.pre) ? `${f.pre} ` : f.pre) : '';
    return `${pre}${s}${f.suf ? ` ${f.suf}` : ''}`;
  }

  refresh() {
    // rows marked data-sheet-nosum (loads aboard in some cases only) stay out of the footer unless they are selected
    const all = this.target();
    const picked = all.filter((r) => this.sel.has(r)).length;
    const rows = picked ? all : all.filter((r) => !r.hasAttribute('data-sheet-nosum'));
    const left = all.length - rows.length;
    const shown = this.shown().length;
    this.ui.count.textContent = picked
      ? `${picked} of ${shown} selected`
      : shown === this.rows.length ? `${shown} rows` : `${shown} of ${this.rows.length} rows shown`;
    if (this.foot.length) {
      for (let c = 0; c < this.ncols; c++) {
        if (!this.numeric[c]) {
          this.foot[c].textContent = '';
          continue;
        }
        const vals = rows.map((r) => this.nums.get(r)![c]?.v).filter((v): v is number => v !== undefined);
        const sum = vals.reduce((a, b) => a + b, 0);
        const total = this.sums[c] === 'off' ? null : this.sums[c] === 'cog' ? this.weighted(rows, c) : sum;
        const v = this.stat === 'Count' ? vals.length : !vals.length ? null
          : this.stat === 'Sum' ? total : this.stat === 'Mean' ? sum / vals.length
            : this.stat === 'Min' ? Math.min(...vals) : Math.max(...vals);
        this.foot[c].textContent = v === null ? '' : this.format(c, v, this.stat);
      }
      const cog = this.stat === 'Sum' && this.sums.includes('cog') ? ', CoG weighted by mass' : '';
      const why = this.table.dataset.sheetNosumWhy ?? 'aboard in some cases only';
      const out = left ? `, ${left} left out, ${why}` : '';
      if (!this.numeric[0]) this.foot[0].textContent = `${this.stat} of ${picked ? `${picked} selected` : `${rows.length} rows`}${out}${cog}`;
    }
    this.update3d();
  }

  // ------------------------------------------------------------------ copy and CSV
  // The selected rows still shown, or the table as shown (group and total rows included).
  exportRows(): HTMLTableRowElement[] {
    const body = Array.from(this.table.querySelectorAll('tbody tr')) as HTMLTableRowElement[];
    const picked = body.filter((r) => this.sel.has(r) && !r.classList.contains('sheet-out'));
    return picked.length ? picked : body.filter((r) => !r.classList.contains('sheet-out') && !r.classList.contains('sheet-off'));
  }

  grid(): string[][] {
    const line = (cells: (HTMLTableCellElement | null)[]) => {
      const out: string[] = [];
      for (let c = 0; c < this.ncols; c++) out.push(cells[c] ? cellText(cells[c]) : '');
      return out;
    };
    const out = this.head ? [line(this.heads)] : [];
    for (const r of this.exportRows()) out.push(line(this.cols.get(r)!));
    return out;
  }

  say(text: string) {
    this.ui.msg.textContent = text;
    window.setTimeout(() => {
      if (this.ui.msg.textContent === text) this.ui.msg.textContent = '';
    }, 4000);
  }

  async copy() {
    const g = this.grid();
    const text = g.map((r) => r.map((c) => c.replace(/[\t\r\n]+/g, ' ')).join('\t')).join('\n');
    const n = g.length - (this.head ? 1 : 0);
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      const area = document.createElement('textarea');
      area.value = text;
      area.style.position = 'fixed';
      area.style.opacity = '0';
      document.body.append(area);
      area.select();
      document.execCommand('copy');
      area.remove();
    }
    this.say(`Copied ${n} row${n === 1 ? '' : 's'}`);
  }

  csv() {
    const q = (s: string) => (/[",\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s);
    const text = '\uFEFF' + this.grid().map((r) => r.map(q).join(',')).join('\r\n') + '\r\n';
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([text], { type: 'text/csv;charset=utf-8' }));
    a.download = `${this.fileName()}.csv`;
    document.body.append(a);
    a.click();
    a.remove();
    window.setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  }

  // The page and the heading above the table, for example trailer-load-cases.csv.
  fileName(): string {
    const page = slug(location.pathname.split('/').filter(Boolean).pop() ?? 'home');
    let heading = '';
    for (const h of Array.from(document.querySelectorAll('.sl-markdown-content :is(h2, h3)'))) {
      if (h.compareDocumentPosition(this.root) & Node.DOCUMENT_POSITION_FOLLOWING) heading = h.id || norm(h.textContent ?? '');
    }
    return heading ? `${page}-${slug(heading)}` : `${page}-table-${this.index + 1}`;
  }

  // ------------------------------------------------------------------ the 3D model
  keys(r: HTMLTableRowElement): string[] {
    const first = cellText(this.cols.get(r)![0]);
    return [first, first.split(' ')[0]];
  }

  update3d() {
    const b = this.ui?.show3d;
    if (!b) return;
    const has = (r: HTMLTableRowElement) => this.keys(r).some((k) => known.has(k));
    b.hidden = !this.rows.some(has);
    b.disabled = !this.target().some((r) => this.sel.has(r) && has(r));
  }

  show3d() {
    const ids = this.target().filter((r) => this.sel.has(r)).flatMap((r) => this.keys(r));
    const detail = { ids: [...new Set(ids)], count: 0 };
    document.dispatchEvent(new CustomEvent('ct:show-parts', { detail }));
    this.say(detail.count ? `${detail.count} part${detail.count === 1 ? '' : 's'} highlighted in the 3D model`
      : 'None of the selected rows is a part in the 3D model');
  }

  // Select the row for a part and bring it into view. Exact first cells first, then the first word.
  find(ids: string[], exact: boolean): boolean {
    const r = this.rows.find((x) => {
      const [first, word] = this.keys(x);
      return ids.includes(exact ? first : word);
    });
    if (!r) return false;
    if (r.classList.contains('sheet-out')) {
      this.ui.filter.value = '';
      this.applyFilter();
    }
    this.clear();
    this.mark(r, true);
    this.anchor = r;
    this.root.scrollIntoView({ behavior: 'smooth', block: 'start' });
    this.focus(r, true);
    this.refresh();
    return true;
  }
}

// ------------------------------------------------------------------ start
function start() {
  const tables = Array.from(document.querySelectorAll('.sl-markdown-content table')) as HTMLTableElement[];
  for (const t of tables) {
    if (t.closest('.not-content, cad-viewer, .sheet, [data-sheet="off"]')) continue;
    if (!t.tBodies.length || !t.tBodies[0].rows.length) continue;
    sheets.push(new Sheet(t, sheets.length));
  }
  document.querySelectorAll('cad-viewer').forEach((v) => ((v as any).partKeys as string[] | undefined)?.forEach((k) => known.add(k)));
  sheets.forEach((s) => s.update3d());
  document.fonts?.ready.then(() => fit(sheets));
  let t = 0;
  window.addEventListener('resize', () => {
    clearTimeout(t);
    t = window.setTimeout(() => fit(sheets), 150);
  });
}

document.addEventListener('ct:parts-ready', (e) => {
  for (const id of (e as CustomEvent).detail.ids as string[]) known.add(id);
  sheets.forEach((s) => s.update3d());
});
document.addEventListener('ct:find-row', (e) => {
  const d = (e as CustomEvent).detail as { ids: string[]; found: boolean };
  d.found = sheets.some((s) => s.find(d.ids, true)) || sheets.some((s) => s.find(d.ids, false));
});

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
else start();
