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
import { unlocked, isUnlocked, lockHint, takeNewUnlocks } from './unlocks.js';

const params = new URLSearchParams(location.search);
const tracker = new Tracker($('#cam'));
// Testing aids: ?sim=1 fakes the camera (keys: f = face in view, m = moving),
// ?fast=10 runs timers ten times faster.
if (params.has('sim')) {
  tracker.sim = { inView: true, moving: true };
  window.__sim = tracker.sim;
  addEventListener('keydown', e => {
    if (e.key === 'f') tracker.sim.inView = !tracker.sim.inView;
    if (e.key === 'm') tracker.sim.moving = !tracker.sim.moving;
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

function start(kind) {
  applyVolumes();
  applyTracking();
  audio.unlock();
  audio.fx('tap');
  game.run(kind);
}

function showHome() {
  if (game.running) return;
  $('#bg').src = ART.home;
  $('#bg').classList.remove('fade');
  $('#strip').replaceChildren();
  const tonight = store.nights[nightKey()];
  const buttons = [
    h('button', { class: 'btn', id: 'go-brush', onclick: () => start('brush') },
      img(ART.icon('brush')), 'Brush & Floss', img(ART.icon('pick'))),
    h('button', { class: 'btn small sunny', id: 'go-morning', onclick: () => start('morning') },
      img(ART.icon('sun_sticker')), 'Morning brush'),
  ];
  if (store.settings.swishEnabled) {
    buttons.push(h('button', { class: 'btn small blue', id: 'go-swish', onclick: () => start('swish') }, img(ART.icon('cup')), 'Swish'));
  }
  const tap = fn => () => { audio.unlock(); audio.fx('tap'); fn(); };
  $('#screen').replaceChildren(h('div', { class: 'home' },
    h('div', { class: 'logo' }, h('h1', {}, 'Gum', h('span', {}, 'Goblins'))),
    h('div', { class: 'home-cast' },
      img(ART.goblin('a'), 'g1'),
      h('button', { class: 'bd', id: 'my-hero', 'aria-label': 'Dress up your hero', onclick: tap(showHeroEditor) },
        heroEl('ready'), h('span', { class: 'edit-badge' }, '✎')),
      img(ART.goblin('c'), 'g2')),
    tonight?.done ? h('div', { class: 'tonight' }, img(ART.icon('tooth_sticker')), 'Done tonight!') : null,
    h('div', { class: 'home-buttons' }, buttons),
    h('div', { class: 'home-row' },
      h('button', { class: 'round-btn', 'aria-label': 'Collection', onclick: tap(() => showCollection()) }, img(ART.icon('book'))),
      h('button', { class: 'round-btn', 'aria-label': 'Calendar', onclick: tap(showCalendar) }, img(ART.icon('calendar'))))));
}

// Dress-up: capes, hats and brush colours. Locked ones show how to earn them.
function showHeroEditor() {
  const ov = $('#overlay');
  const preview = h('div', { class: 'hero-preview' });
  const close = () => { ov.hidden = true; ov.replaceChildren(); showHome(); };
  const rows = h('div');
  const hint = h('div', { class: 'lock-hint' });
  const render = () => {
    const have = unlocked();
    preview.replaceChildren(heroEl('cheer'));
    const row = (title, part, options) => h('div', { class: 'hero-row' }, h('h3', {}, title),
      h('div', { class: 'hero-options' }, options.map(opt => {
        const open = isUnlocked(part, opt, have);
        return h('button', {
          class: `hero-opt ${store.hero[part] === opt ? 'on' : ''} ${open ? '' : 'locked'}`, 'aria-label': `${part} ${opt}`,
          onclick: () => {
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
    h('h2', {}, 'My Hero'), preview, hint, rows,
    h('div', { style: { textAlign: 'center', marginTop: '16px' } }, h('button', { class: 'btn', onclick: close }, 'Done'))));
  ov.hidden = false;
  ov.onclick = e => { if (e.target === ov) close(); };
}

async function boot() {
  await loadData();
  takeNewUnlocks(); // first run: everything he starts with counts as already seen
  applyVolumes();
  applyTracking();
  setupGear({
    onSettings: open => game.setSettingsOpen(open),
    trackerStatus: () => (game.running ? tracker.status() : null),
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
