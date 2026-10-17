// The reward photo editor. Tonight's emoji starts on the photo as a sticker;
// he can add any emoji he has won (as many copies as he likes), drag them
// around, resize them (corner handle or two-finger pinch) and remove them.
// Saving opens the share sheet (Save Image -> camera roll on iPhone), or
// downloads elsewhere. The photo never leaves the phone.

import { h, img, toast } from './dom.js';
import { ART } from './assets.js';
import { audio } from './audio.js';

const MIN = 0.08, MAX = 0.9;
const MAX_STICKERS = 40;

export function photoEditor(canvas, startIds, trayIds) {
  const pic = img(canvas.toDataURL('image/jpeg', 0.9));
  const layer = h('div', { class: 'stickers' });
  const photo = h('div', { class: 'photo' }, pic, layer);
  const stickers = [];
  let selected = null;

  const place = st => {
    Object.assign(st.el.style, { left: `${st.x * 100}%`, top: `${st.y * 100}%`, width: `${st.s * 100}%` });
  };
  const select = st => {
    selected = st;
    stickers.forEach(o => o.el.classList.toggle('sel', o === st));
    if (st) layer.append(st.el); // bring to front
  };
  const add = (id, x = 0.5, y = 0.5, s = 0.3) => {
    if (stickers.length >= MAX_STICKERS) { toast('That’s a lot of stickers!'); return; }
    const st = { id, x, y, s };
    st.el = h('div', { class: 'sticker' },
      img(ART.emoji(id)),
      h('button', { class: 'del', 'aria-label': 'Remove sticker' }, '×'),
      h('span', { class: 'grow', 'aria-label': 'Resize sticker' }));
    st.el._st = st;
    stickers.push(st);
    layer.append(st.el);
    place(st);
    select(st);
  };
  startIds.forEach((id, i) => add(id, 0.75 - i * 0.1, 0.25 + i * 0.1));

  // ---- touch handling: drag, handle-resize and pinch-resize
  const pointers = new Map();
  let mode = null, start = null;
  const rel = e => {
    const r = photo.getBoundingClientRect();
    return { x: (e.clientX - r.left) / r.width, y: (e.clientY - r.top) / r.height, w: r.width, h: r.height };
  };
  const dist = (a, b) => Math.hypot((a.x - b.x) * a.w, (a.y - b.y) * a.h);

  photo.addEventListener('pointerdown', e => {
    e.preventDefault();
    photo.setPointerCapture(e.pointerId);
    const p = rel(e);
    pointers.set(e.pointerId, p);
    const stEl = e.target.closest('.sticker');
    if (pointers.size === 2 && selected) {
      const [a, b] = [...pointers.values()];
      mode = 'pinch';
      start = { d: dist(a, b), s: selected.s };
      return;
    }
    if (!stEl) { select(null); mode = null; return; }
    const st = stEl._st;
    if (e.target.closest('.del')) {
      stickers.splice(stickers.indexOf(st), 1);
      st.el.remove();
      select(null);
      audio.fx('tap');
      mode = null;
      return;
    }
    select(st);
    if (e.target.closest('.grow')) {
      mode = 'grow';
      start = { d: dist(p, { ...p, x: st.x, y: st.y }), s: st.s };
    } else {
      mode = 'drag';
      start = { dx: p.x - st.x, dy: p.y - st.y };
    }
  });
  photo.addEventListener('pointermove', e => {
    if (!pointers.has(e.pointerId)) return;
    const p = rel(e);
    pointers.set(e.pointerId, p);
    if (!selected) return;
    if (mode === 'pinch' && pointers.size >= 2) {
      const [a, b] = [...pointers.values()];
      selected.s = clamp(start.s * dist(a, b) / Math.max(10, start.d));
    } else if (mode === 'grow') {
      selected.s = clamp(start.s * dist(p, { ...p, x: selected.x, y: selected.y }) / Math.max(10, start.d));
    } else if (mode === 'drag') {
      selected.x = Math.max(0, Math.min(1, p.x - start.dx));
      selected.y = Math.max(0, Math.min(1, p.y - start.dy));
    }
    place(selected);
  });
  const up = e => {
    pointers.delete(e.pointerId);
    if (pointers.size < 2 && mode === 'pinch') mode = null;
    if (!pointers.size) mode = null;
  };
  photo.addEventListener('pointerup', up);
  photo.addEventListener('pointercancel', up);

  // ---- sticker tray: every emoji he owns, tap to add another copy
  const tray = h('div', { class: 'tray' }, trayIds.map(id =>
    h('button', { class: 'tray-item', 'aria-label': 'Add sticker', onclick: () => {
      audio.fx('pop', { gain: 0.5 });
      add(id, 0.35 + Math.random() * 0.3, 0.35 + Math.random() * 0.3);
    } }, img(ART.emoji(id)))));

  const el = h('div', { class: 'editor' }, photo, h('div', { class: 'tray-wrap' }, tray));

  async function save() {
    select(null);
    const out = document.createElement('canvas');
    out.width = canvas.width;
    out.height = canvas.height;
    const g = out.getContext('2d');
    g.drawImage(canvas, 0, 0);
    for (const st of stickers) {
      const size = Math.round(st.s * out.width);
      try {
        const im = await sharpImage(ART.emoji(st.id), size);
        g.drawImage(im, st.x * out.width - size / 2, st.y * out.height - size / 2, size, size);
      } catch (e) { console.warn('sticker skipped', st.id); }
    }
    const blob = await new Promise(r => out.toBlob(r, 'image/jpeg', 0.92));
    const name = `gum-goblins-${new Date().toISOString().slice(0, 10)}.jpg`;
    const file = new File([blob], name, { type: 'image/jpeg' });
    try {
      if (navigator.canShare?.({ files: [file] })) {
        await navigator.share({ files: [file] });
        return true;
      }
    } catch (e) {
      if (e.name === 'AbortError') return false;
    }
    const a = h('a', { href: URL.createObjectURL(blob), download: name });
    document.body.append(a);
    a.click();
    a.remove();
    toast('Photo saved');
    return true;
  }

  return { el, save };
}

function clamp(s) { return Math.max(MIN, Math.min(MAX, s)); }

// Loads an SVG emoji rasterised at exactly the size it will be drawn, so big
// stickers stay crisp on the saved photo.
async function sharpImage(url, size) {
  const text = await fetch(url).then(r => r.text());
  const sized = text.replace(/width="\d+" height="\d+"/, `width="${size}" height="${size}"`);
  const src = URL.createObjectURL(new Blob([sized], { type: 'image/svg+xml' }));
  try {
    return await new Promise((res, rej) => {
      const i = new Image();
      i.onload = () => res(i);
      i.onerror = rej;
      i.src = src;
    });
  } finally {
    setTimeout(() => URL.revokeObjectURL(src), 1000);
  }
}
