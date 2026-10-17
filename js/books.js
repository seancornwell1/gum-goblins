// The emoji collection (grouped by world, blanks for ones still to find) and
// the sticker calendar.

import { $, h, img } from './dom.js';
import { ART, catalog } from './assets.js';
import { store, nightKey } from './store.js';
import { audio } from './audio.js';

function openSheet(...content) {
  const ov = $('#overlay');
  const close = () => { ov.hidden = true; ov.replaceChildren(); audio.fx('tap'); };
  const sheet = h('div', { class: 'sheet' }, h('button', { class: 'close', onclick: close, 'aria-label': 'Close' }, '×'), ...content);
  ov.replaceChildren(sheet);
  ov.hidden = false;
  ov.onclick = e => { if (e.target === ov) close(); };
  return close;
}

export function showCollection(highlight = null) {
  const owned = store.collection;
  const total = catalog.worlds.reduce((n, w) => n + w.emoji.length, 0);
  const have = Object.keys(owned).length;
  const sections = catalog.worlds.map(w => {
    const got = w.emoji.filter(e => owned[e.id]).length;
    return [
      h('h3', {}, h('span', {}, w.name), h('span', {}, `${got} / ${w.emoji.length}`)),
      h('div', { class: 'grid' }, w.emoji.map(e => owned[e.id]
        ? h('div', { class: `slot ${e.id === highlight ? 'new' : ''}` }, img(ART.emoji(e.id)), h('span', {}, e.name))
        : h('div', { class: 'slot missing' }, img(ART.icon('mystery')), h('span', {}, '?')))),
    ];
  });
  openSheet(h('h2', {}, img(ART.icon('book')), 'My Collection'), h('div', {}, `${have} of ${total} found`), ...sections);
}

export function showCalendar() {
  let view = new Date();
  view.setDate(1);
  const body = h('div');
  const render = () => {
    const y = view.getFullYear(), m = view.getMonth();
    const first = new Date(y, m, 1).getDay();
    const days = new Date(y, m + 1, 0).getDate();
    const today = nightKey();
    const cells = ['S', 'M', 'T', 'W', 'T', 'F', 'S'].map(d => h('div', { class: 'dow' }, d));
    for (let i = 0; i < first; i++) cells.push(h('div'));
    for (let d = 1; d <= days; d++) {
      const key = `${y}-${String(m + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
      const night = store.nights[key];
      cells.push(h('div', { class: `day ${key === today ? 'today' : ''}` },
        h('span', { class: 'n' }, d),
        night?.done ? img(ART.icon('tooth_sticker'), 's') : null,
        store.swish[key] ? img(ART.icon('star_small'), 'g') : null));
    }
    const label = view.toLocaleDateString(undefined, { month: 'long', year: 'numeric' });
    body.replaceChildren(
      h('div', { class: 'cal-head' },
        h('button', { class: 'btn small', onclick: () => { view.setMonth(m - 1); render(); } }, '‹'),
        h('b', {}, label),
        h('button', { class: 'btn small', onclick: () => { view.setMonth(m + 1); render(); } }, '›')),
      h('div', { class: 'cal-grid' }, cells));
  };
  render();
  openSheet(h('h2', {}, img(ART.icon('calendar')), 'My Calendar'), body);
}
