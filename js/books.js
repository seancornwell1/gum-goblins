// The emoji collection (grouped by world, blanks for ones still to find) and
// the sticker calendar. With two kids, tabs switch between their books.

import { $, h, img } from './dom.js';
import { ART, catalog, allEmoji } from './assets.js';
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

// Renders a kid's page with their profile active, plus name tabs when there are two kids.
function withTabs(profile, renderPage) {
  const body = h('div');
  const draw = i => {
    const prev = store.active;
    store.use(i);
    const page = renderPage(i);
    store.use(prev);
    const tabs = store.players.length > 1 ? h('div', { class: 'tabs' }, store.players.map(k =>
      h('button', { class: `tab ${k === i ? 'on' : ''}`, onclick: () => { audio.fx('tap'); draw(k); } }, store.profile(k).name))) : null;
    body.replaceChildren(...[tabs, page].filter(Boolean));
  };
  draw(profile);
  return body;
}

export function showCollection(highlight = null, profile = 0) {
  openSheet(h('h2', {}, img(ART.icon('book')), 'Collection'), withTabs(profile, () => {
    const owned = store.collection;
    const all = allEmoji();
    const have = all.filter(e => owned[e.id]).length;
    const slot = e => owned[e.id]
      ? h('div', { class: `slot ${e.gold ? 'gold' : ''} ${e.id === highlight ? 'new' : ''}` }, img(ART.emoji(e.id)), h('span', {}, e.name))
      : h('div', { class: `slot missing ${e.gold ? 'gold' : ''}` }, img(ART.icon(e.gold ? 'mystery_gold' : 'mystery')), h('span', {}, '?'));
    const sections = catalog.worlds.map(w => {
      const items = all.filter(e => e.world === w.id);
      const got = items.filter(e => owned[e.id]).length;
      return [
        h('h3', {}, h('span', {}, w.name), h('span', {}, `${got} / ${items.length}`)),
        h('div', { class: 'grid' }, items.filter(e => !e.gold).map(slot)),
        h('div', { class: 'grid sparkly' }, items.filter(e => e.gold).map(slot)),
      ];
    });
    return h('div', {}, h('div', {}, `${have} of ${all.length} found · sparkly ones are extra rare!`), ...sections.flat());
  }));
}

export function showCalendar(profile = 0) {
  const view = new Date();
  view.setDate(1);
  let tabsBody = null;
  let current = profile;
  const page = i => {
    current = i;
    const y = view.getFullYear(), m = view.getMonth();
    const first = new Date(y, m, 1).getDay();
    const days = new Date(y, m + 1, 0).getDate();
    const today = nightKey();
    const cells = ['S', 'M', 'T', 'W', 'T', 'F', 'S'].map(d => h('div', { class: 'dow' }, d));
    for (let k = 0; k < first; k++) cells.push(h('div'));
    for (let d = 1; d <= days; d++) {
      const key = `${y}-${String(m + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
      const night = store.nights[key];
      cells.push(h('div', { class: `day ${key === today ? 'today' : ''}` },
        h('span', { class: 'n' }, d),
        night?.done ? img(ART.icon('tooth_sticker'), 's') : null,
        store.mornings[key] ? img(ART.icon('sun_sticker'), 'm') : null,
        store.swish[key] ? img(ART.icon('star_small'), 'g') : null));
    }
    const label = view.toLocaleDateString(undefined, { month: 'long', year: 'numeric' });
    const flip = d => { view.setMonth(m + d); redraw(); };
    return h('div', {},
      h('div', { class: 'cal-head' },
        h('button', { class: 'btn small', onclick: () => flip(-1) }, '‹'),
        h('b', {}, label),
        h('button', { class: 'btn small', onclick: () => flip(1) }, '›')),
      h('div', { class: 'cal-grid' }, cells));
  };
  const holder = h('div');
  const redraw = () => { tabsBody = withTabs(current, page); holder.replaceChildren(tabsBody); };
  redraw();
  openSheet(h('h2', {}, img(ART.icon('calendar')), 'Calendar'), holder);
}
