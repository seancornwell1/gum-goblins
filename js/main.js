// Boot, home screen and wiring between the parts.

import { $, h, img } from './dom.js';
import { ART, loadData, preloadImages, heroParts } from './assets.js';
import { store, nightKey } from './store.js';
import { audio } from './audio.js';
import { Tracker } from './tracker.js';
import { Game } from './game.js';
import { setupGear } from './settings.js';
import { showCollection, showCalendar } from './books.js';
import { heroEl } from './hero.js';
import { unlocked, isUnlocked, lockHint, takeNewUnlocks, isEventItem } from './unlocks.js';
import { activeEvent } from './events.js';

const params = new URLSearchParams(location.search);
const tracker = new Tracker($('#cam'));
// Testing aids: ?sim=1 fakes the camera (keys: f / g = player 1 / 2 in view,
// m / n = player 1 / 2 moving), ?fast=10 runs timers ten times faster.
if (params.has('sim')) {
  tracker.sim = [{ inView: true, moving: true }, { inView: true, moving: true }];
  window.__sim = tracker.sim;
  addEventListener('keydown', e => {
    const [p, key] = { f: [0, 'inView'], g: [1, 'inView'], m: [0, 'moving'], n: [1, 'moving'] }[e.key] || [];
    if (key) tracker.sim[p][key] = !tracker.sim[p][key];
  });
}
const game = new Game({ tracker, speed: Math.max(1, +params.get('fast') || 1), onExit: () => showHome() });
window.__game = game;

function applyVolumes() {
  const s = store.settings;
  audio.applyVolumes({ music: s.volMusic, fx: s.volFx });
}

function applyTracking() {
  tracker.sensitivity = store.settings.sensitivity;
}

function start(kind, players) {
  applyVolumes();
  applyTracking();
  audio.unlock();
  audio.fx('tap');
  $('#overlay').hidden = true;
  game.run(kind, players);
}

// With two kids set up, ask who's playing; otherwise just go.
function choosePlayers(kind) {
  audio.unlock();
  if (store.players.length < 2) { start(kind, [0]); return; }
  audio.fx('tap');
  const ov = $('#overlay');
  const pick = (label, players, content) => h('button', {
    class: 'who', id: `who-${players.join('-')}`, onclick: () => start(kind, players),
  }, content, h('span', {}, label));
  ov.replaceChildren(h('div', { class: 'sheet who-sheet' },
    h('button', { class: 'close', onclick: () => { ov.hidden = true; }, 'aria-label': 'Close' }, '×'),
    h('h2', {}, 'Who’s brushing?'),
    h('div', { class: 'who-row' },
      ...store.players.map(i => pick(store.profile(i).name, [i], heroEl('ready', store.profile(i).hero))),
      pick('Both!', store.players, h('div', { class: 'who-both' },
        ...store.players.map(i => heroEl('cheer', store.profile(i).hero)))))));
  ov.hidden = false;
  ov.onclick = e => { if (e.target === ov) ov.hidden = true; };
}

function showHome() {
  if (game.running) return;
  store.use(0);
  $('#bg').src = ART.home();
  document.body.classList.toggle('halloween', activeEvent() === 'halloween');
  $('#bg').classList.remove('fade');
  $('#strip').replaceChildren();
  const tonight = store.players.some(i => store.profile(i).nights[nightKey()]?.done);
  const buttons = [
    h('button', { class: 'btn', id: 'go-brush', onclick: () => choosePlayers('brush') },
      img(ART.icon('brush')), 'Brush & Floss', img(ART.icon('pick'))),
    h('button', { class: 'btn small sunny', id: 'go-morning', onclick: () => choosePlayers('morning') },
      img(ART.icon('sun_sticker')), 'Morning brush'),
  ];
  if (store.settings.swishEnabled) {
    buttons.push(h('button', { class: 'btn small blue', id: 'go-swish', onclick: () => choosePlayers('swish') }, img(ART.icon('cup')), 'Swish'));
  }
  const tap = fn => () => { audio.unlock(); audio.fx('tap'); fn(); };
  const duo = store.players.length > 1;
  const heroButton = i => h('button', { class: 'bd', id: i ? 'my-hero-2' : 'my-hero', 'aria-label': `Dress up ${store.profile(i).name}'s hero`, onclick: tap(() => showHeroEditor(i)) },
    heroEl('ready', store.profile(i).hero), h('span', { class: 'edit-badge' }, '✎'),
    duo ? h('span', { class: 'hero-name' }, store.profile(i).name) : null);
  $('#screen').replaceChildren(h('div', { class: 'home' },
    h('div', { class: 'logo' }, h('h1', {}, 'Gum', h('span', {}, 'Goblins')),
      activeEvent() === 'halloween' ? h('div', { class: 'event-tag' }, '🎃 Halloween Edition 🎃') : null),
    h('div', { class: `home-cast ${duo ? 'duo' : ''}` },
      img(ART.goblin('a'), 'g1'), ...store.players.map(heroButton), img(ART.goblin('c'), 'g2')),
    tonight ? h('div', { class: 'tonight' }, img(ART.icon('tooth_sticker')), 'Done tonight!') : null,
    h('div', { class: 'home-buttons' }, buttons),
    h('div', { class: 'home-row' },
      h('button', { class: 'round-btn', 'aria-label': 'Collection', onclick: tap(() => showCollection()) }, img(ART.icon('book'))),
      h('button', { class: 'round-btn', 'aria-label': 'Calendar', onclick: tap(() => showCalendar()) }, img(ART.icon('calendar'))))));
}

// Dress-up for one kid: capes, hats and brush colours. Locked ones show how to earn them.
function showHeroEditor(profile) {
  store.use(profile);
  const ov = $('#overlay');
  const preview = h('div', { class: 'hero-preview' });
  const close = () => { ov.hidden = true; ov.replaceChildren(); showHome(); };
  const rows = h('div');
  const hint = h('div', { class: 'lock-hint' });
  const render = () => {
    store.use(profile);
    const have = unlocked();
    preview.replaceChildren(heroEl('cheer', store.hero));
    const row = (title, part, options) => h('div', { class: 'hero-row' }, h('h3', {}, title),
      h('div', { class: 'hero-options' }, options.filter(opt => isUnlocked(part, opt, have) || !isEventItem(part, opt) || activeEvent()).map(opt => {
        const open = isUnlocked(part, opt, have);
        return h('button', {
          class: `hero-opt ${store.hero[part] === opt ? 'on' : ''} ${open ? '' : 'locked'}`, 'aria-label': `${part} ${opt}`,
          onclick: () => {
            store.use(profile);
            if (!open) { audio.fx('tap'); hint.textContent = `🔒 ${lockHint(part, opt)} to unlock this!`; return; }
            audio.fx('pop', { gain: 0.5 }); store.setHero(part, opt); hint.textContent = ''; render();
          },
        }, heroEl('ready', { ...store.hero, [part]: opt }), open ? null : img(ART.icon('lock'), 'lock'));
      })));
    rows.replaceChildren(
      row('Cape', 'cape', heroParts.capes),
      row('Hat', 'hat', heroParts.hats),
      row('Brush', 'brush', heroParts.brushes));
  };
  render();
  ov.replaceChildren(h('div', { class: 'sheet' },
    h('button', { class: 'close', onclick: close, 'aria-label': 'Close' }, '×'),
    h('h2', {}, store.players.length > 1 ? `${store.profile(profile).name}’s Hero` : 'My Hero'), preview, hint, rows,
    h('div', { style: { textAlign: 'center', marginTop: '16px' } }, h('button', { class: 'btn', onclick: close }, 'Done'))));
  ov.hidden = false;
  ov.onclick = e => { if (e.target === ov) close(); };
}

async function boot() {
  await loadData();
  // First run: everything each kid starts with counts as already seen.
  [0, 1].forEach(i => { store.use(i); takeNewUnlocks(); });
  store.use(0);
  applyVolumes();
  applyTracking();
  setupGear({
    onSettings: open => game.setSettingsOpen(open),
    trackerStatus: () => (game.running ? game.players.map((_, p) => tracker.status(performance.now(), p)) : null),
    playerNames: () => game.players.map(i => store.profile(i).name),
    routineRunning: () => game.running,
    nextStep: () => game.nextStep(),
    endRoutine: () => game.endRoutine(),
    applyVolumes,
    applyTracking,
    refreshHome: () => showHome(),
  });
  showHome();
  preloadImages(['a', 'b', 'c', 'big', 'sneaky'].map(ART.goblin));

  if ('serviceWorker' in navigator && (location.protocol === 'https:' || location.hostname === 'localhost')) {
    navigator.serviceWorker.register('sw.js').catch(e => console.warn('offline cache unavailable', e));
  }
}

boot();
