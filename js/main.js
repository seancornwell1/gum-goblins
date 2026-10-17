// Boot, home screen and wiring between the parts.

import { $, h, img } from './dom.js';
import { ART, loadData, preloadImages } from './assets.js';
import { store, nightKey } from './store.js';
import { audio } from './audio.js';
import { Tracker } from './tracker.js';
import { Game } from './game.js';
import { setupGear } from './settings.js';
import { showCollection, showCalendar } from './books.js';

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
  audio.applyVolumes({ music: s.volMusic, voice: s.volVoice, fx: s.volFx });
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
  ];
  if (store.settings.swishEnabled) {
    buttons.push(h('button', { class: 'btn blue', id: 'go-swish', onclick: () => start('swish') }, img(ART.icon('cup')), 'Swish'));
  }
  $('#screen').replaceChildren(h('div', { class: 'home' },
    h('div', { class: 'logo' }, h('h1', {}, 'Gum', h('span', {}, 'Goblins'))),
    h('div', { class: 'home-cast' },
      img(ART.goblin('a'), 'g1'), img(ART.buddy('ready'), 'bd'), img(ART.goblin('c'), 'g2')),
    tonight?.done ? h('div', { class: 'tonight' }, img(ART.icon('tooth_sticker')), 'Done tonight!') : null,
    h('div', { class: 'home-buttons' }, buttons),
    h('div', { class: 'home-row' },
      h('button', { class: 'round-btn', 'aria-label': 'Collection', onclick: () => { audio.unlock(); audio.fx('tap'); showCollection(); } }, img(ART.icon('book'))),
      h('button', { class: 'round-btn', 'aria-label': 'Calendar', onclick: () => { audio.unlock(); audio.fx('tap'); showCalendar(); } }, img(ART.icon('calendar'))))));
}

async function boot() {
  await loadData();
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
