// Parent settings. Opened by pressing and holding the gear for 1.5 seconds so
// little fingers can't change anything by accident.

import { $, h, toast } from './dom.js';
import { store } from './store.js';
import { audio } from './audio.js';

const HOLD_MS = 1500;

export function setupGear(ctx) {
  const gear = $('#gear');
  let timer = null;
  const cancel = () => { clearTimeout(timer); timer = null; gear.classList.remove('holding'); };
  gear.addEventListener('pointerdown', e => {
    e.preventDefault();
    gear.classList.add('holding');
    timer = setTimeout(() => { cancel(); openSettings(ctx); }, HOLD_MS);
  });
  ['pointerup', 'pointerleave', 'pointercancel'].forEach(ev => gear.addEventListener(ev, cancel));
  gear.addEventListener('contextmenu', e => e.preventDefault());
}

function seg(key, options, fmt = v => v, after) {
  const wrap = h('div', { class: 'seg' });
  const render = () => wrap.replaceChildren(...options.map(v => h('button', {
    class: store.settings[key] === v ? 'on' : '',
    onclick: () => { store.setSetting(key, v); render(); after?.(v); },
  }, fmt(v))));
  render();
  return wrap;
}

function vol(label, key, ctx) {
  const out = h('span', {}, Math.round(store.settings[key] * 100));
  const input = h('input', {
    type: 'range', min: 0, max: 1, step: 0.05, value: store.settings[key],
    oninput: e => { store.setSetting(key, +e.target.value); out.textContent = Math.round(e.target.value * 100); ctx.applyVolumes(); },
    onchange: () => audio.fx(key === 'volMusic' ? 'chime' : 'pop'),
  });
  return h('div', { class: 'vol' }, h('span', {}, label), input, out);
}

export function openSettings(ctx) {
  const panel = $('#settings');
  ctx.onSettings(true);
  const statusLine = h('div', { class: 'status-line' });
  const close = () => {
    clearInterval(statusTimer);
    panel.hidden = true;
    panel.replaceChildren();
    ctx.onSettings(false);
  };
  const updateStatus = () => {
    const all = ctx.trackerStatus();
    if (!all) { statusLine.replaceChildren(h('span', {}, 'Camera check runs during a routine.')); return; }
    if (all[0].noCamera) { statusLine.replaceChildren(h('b', { class: 'no' }, 'Camera off — timers run on their own.')); return; }
    const names = ctx.playerNames();
    const mark = (ok, yes, no) => h('b', { class: ok ? 'ok' : 'no' }, ok ? yes : no);
    statusLine.replaceChildren(...all.map((s, p) => h('div', { class: 'status-line' },
      all.length > 1 ? h('span', {}, `${names[p]}:`) : null,
      mark(s.faceNow, '✓ Face found', '✗ No face'),
      mark(s.inView, '✓ In view', '✗ Out of view'),
      mark(s.movingNow, '✓ Movement', '✗ Still'))));
  };
  const statusTimer = setInterval(updateStatus, 250);
  updateStatus();

  let resetArmed = false;
  const resetBtn = h('button', {
    class: 'danger', onclick: () => {
      if (!resetArmed) { resetArmed = true; resetBtn.textContent = 'Tap again to erase everything'; return; }
      store.resetProgress();
      resetBtn.textContent = 'Collection and calendar cleared';
    },
  }, 'Reset collection & calendar');

  const running = ctx.routineRunning();
  const sheet = h('div', { class: 'sheet' },
    h('button', { class: 'close', onclick: close, 'aria-label': 'Close' }, '×'),
    h('h2', {}, 'Parent settings'),
    running ? h('div', { class: 'set' },
      h('span', { class: 't' }, 'Routine'),
      h('div', { class: 'actions' },
        h('button', { class: 'primary', onclick: () => { close(); ctx.nextStep(); } }, 'Next step ⏭'),
        h('button', { onclick: () => { close(); ctx.endRoutine(); } }, 'End and go home')),
      h('small', {}, '“Next step” finishes the current step as if it went well — use it when the camera struggles.')) : null,
    h('div', { class: 'set' }, h('span', { class: 't' }, 'Players'),
      h('div', { class: 'names' }, [0, 1].map(i => h('input', {
        type: 'text', value: store.profile(i).name, maxlength: 14, 'aria-label': `Player ${i + 1} name`,
        onchange: e => { store.setName(i, e.target.value); ctx.refreshHome(); },
      }))),
      h('span', { class: 't', style: { marginTop: '10px' } }, 'Second player'),
      seg('secondPlayer', [true, false], v => (v ? 'On' : 'Off'), () => ctx.refreshHome()),
      h('small', {}, 'With two players, each has their own hero, collection and calendar. To brush together, stand side by side: player 1 on the left of the mirror, player 2 on the right.')),
    h('div', { class: 'set' }, h('span', { class: 't' }, 'Brushing length'),
      seg('brushMinutes', [1, 2, 3], v => `${v} min`),
      h('small', {}, 'Six zones, always in the same order; each zone gets an equal share.')),
    h('div', { class: 'set' }, h('span', { class: 't' }, 'Brushing pass mark'),
      seg('passMark', [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8], v => `${Math.round(v * 100)}%`),
      h('small', {}, 'How much of the brushing time needs real movement to beat the big goblin. Start easy and raise it over time.')),
    h('div', { class: 'set' }, h('span', { class: 't' }, 'Floss gaps'),
      seg('flossGaps', [6, 8, 10, 12, 14, 16, 18]),
      h('span', { class: 't', style: { marginTop: '10px' } }, 'Seconds per gap'),
      seg('flossSeconds', [2, 3, 4, 5, 8], v => `${v}s`),
      h('small', {}, 'Front teeth first, always in the same order.')),
    h('div', { class: 'set' }, h('span', { class: 't' }, 'Swish mode'),
      seg('swishEnabled', [false, true], v => v ? 'On' : 'Off', () => ctx.refreshHome()),
      h('span', { class: 't', style: { marginTop: '10px' } }, 'Swish countdown'),
      seg('swishSeconds', [10, 15, 20, 30, 45, 60], v => `${v}s`),
      h('small', {}, 'Practise with plain water first. Ask his dentist which rinse to use and when.')),
    h('div', { class: 'set' }, h('span', { class: 't' }, 'Volume'),
      vol('Music', 'volMusic', ctx), vol('Effects', 'volFx', ctx),
      h('div', { class: 'actions', style: { marginTop: '8px' } },
        h('button', { onclick: () => { audio.unlock(); audio.fx('chime'); audio.fx('fanfare'); } }, '🔊 Test sound')),
      h('small', {}, 'Test with the ringer switch both on and off: sound should play either way.')),
    h('div', { class: 'set' }, h('span', { class: 't' }, 'Camera tracking'),
      seg('camera', [true, false], v => v ? 'On' : 'Off', v => { if (!v) toast('Timers will run without the camera'); }),
      h('span', { class: 't', style: { marginTop: '10px' } }, 'Movement sensitivity'),
      seg('sensitivity', ['low', 'medium', 'high'], v => v[0].toUpperCase() + v.slice(1), () => ctx.applyTracking()),
      h('div', { style: { marginTop: '10px' } }, statusLine),
      h('small', {}, 'Stand the phone facing him at the sink with his face in frame. The camera only checks that he is in view and moving at his mouth.')),
    h('div', { class: 'set' }, h('span', { class: 't' }, 'Progress'),
      h('div', { class: 'actions' }, resetBtn)),
    h('div', { class: 'set', style: { borderBottom: 0 } },
      h('small', {}, 'Privacy: the camera and photos never leave this phone. Nothing is uploaded or stored anywhere else. Works offline once installed.')));
  panel.replaceChildren(sheet);
  panel.hidden = false;
  panel.onclick = e => { if (e.target === panel) close(); };
}
