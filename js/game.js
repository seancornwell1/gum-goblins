// The routines. The steps, their order and their sounds are the same every
// time; only the world (scenery and emoji set) changes. No narration: just
// short on-screen text.

import { $, h, img, toast } from './dom.js';
import { ART, ZONES, GAPS, SMALL_GOBLINS, catalog, allEmoji, preloadImages } from './assets.js';
import { store } from './store.js';
import { audio } from './audio.js';
import { keepAwake } from './wake.js';
import { Guide } from './guide.js';
import { heroEl, setPose } from './hero.js';
import { photoEditor } from './photo.js';
import { showCollection, showCalendar } from './books.js';
import { takeNewUnlocks } from './unlocks.js';

const NIGHT_STEPS = [['brush', 'Brush'], ['pick', 'Get your floss pick'], ['floss', 'Floss'], ['gift', 'Prize'], ['moon', 'Goodnight']];
const MORNING_STEPS = [['brush', 'Brush'], ['sun_sticker', 'Sun sticker']];
const SWISH_STEPS = [['cup', 'Take a sip'], ['swish', 'Swish'], ['sink', 'Spit'], ['star_small', 'Gold star']];

// Where goblins gather around the hero for each zone (degrees, 0 = right, 90 = down).
const ZONE_ANGLES = {
  top_left: [200, 226, 252], top_front: [244, 270, 296], top_right: [288, 314, 340],
  bottom_right: [10, 34, 58], bottom_front: [64, 90, 116], bottom_left: [122, 146, 170],
};
const MIN_SHOT_MS = 1000;  // fastest the hero fires (fast brushing)
const MAX_SHOT_MS = 4000;  // slowest the hero fires (slow brushing)
const SPAWN_MS = 3000;     // a new goblin arrives this often
const MAX_GOBLINS = 10;
const RING = [210, 240, 270, 300, 330, 20, 50, 130, 160];
const OUTER = [225, 270, 315, 30, 150];
const GOLD_WEIGHT = 0.35; // sparkly emoji are rarer than regular ones

class Abort extends Error {}

export class Game {
  constructor({ tracker, speed = 1, onExit }) {
    this.tracker = tracker;
    this.speed = speed;
    this.onExit = onExit;
    this.stage = $('#stage');
    this.screen = $('#screen');
    this.strip = $('#strip');
    this.running = false;
    this.settingsOpen = false;
  }

  // ------------------------------------------------------------ plumbing

  reset() {
    this.aborted = false;
    this.skip = false;
    this.paused = false;
    this.pendingTap = null;
    this.sleeps = new Set();
  }

  check() { if (this.aborted) throw new Abort(); }

  sleep(ms) {
    return new Promise(res => {
      const t = setTimeout(() => { this.sleeps.delete(done); res(); }, ms / this.speed);
      const done = () => { clearTimeout(t); res(); };
      this.sleeps.add(done);
    }).then(() => this.check());
  }

  waitTap(el) {
    if (this.skip) { this.skip = false; return Promise.resolve('skip'); }
    return new Promise(res => {
      this.pendingTap = res;
      el.addEventListener('click', () => { audio.fx('tap'); res('tap'); }, { once: true });
    }).then(v => { this.pendingTap = null; this.check(); return v; });
  }

  nextStep() {
    if (!this.running) return;
    if (this.pendingTap) { this.pendingTap('skip'); return; }
    this.skip = true;
  }

  endRoutine() {
    if (!this.running) return;
    this.aborted = true;
    this.pendingTap?.('abort');
    this.sleeps.forEach(f => f());
  }

  setSettingsOpen(open) {
    this.settingsOpen = open;
    this.applyFreeze();
  }

  applyFreeze() {
    document.body.classList.toggle('frozen', !!(this.paused || this.settingsOpen));
  }

  setStrip(steps, index) {
    this.strip.replaceChildren(...steps.map(([icon, label], i) =>
      h('div', { class: `step ${i < index ? 'done' : i === index ? 'now' : ''}`, title: label, 'aria-label': label },
        img(ART.icon(icon)))));
  }

  setBg(src) {
    const bg = $('#bg');
    if (bg.getAttribute('src') === src) return;
    bg.classList.add('fade');
    setTimeout(() => { bg.src = src; bg.onload = () => bg.classList.remove('fade'); }, 500);
  }

  show(el) {
    document.querySelectorAll('.banner').forEach(b => b.remove());
    this.screen.replaceChildren(el);
    return el;
  }

  // A short line of big text instead of narration.
  banner(text, ms = 1600) {
    const b = h('div', { class: 'banner' }, text);
    $('#app').append(b);
    setTimeout(() => b.remove(), ms);
  }

  appRect() { return $('#app').getBoundingClientRect(); }

  // Center of an element in stage coordinates.
  centerOf(el, fx = 0.5, fy = 0.5) {
    const a = this.appRect(), r = el.getBoundingClientRect();
    return { x: r.left - a.left + r.width * fx, y: r.top - a.top + r.height * fy, w: r.width, h: r.height };
  }

  placeAround(el, deg, radiusFactor = 1.0, halfSize = 50) {
    const a = this.appRect();
    const c = this.centerOf(this.hero, 0.5, 0.5);
    const R = Math.max(c.w, c.h) * 0.62 * radiusFactor;
    const rad = deg * Math.PI / 180;
    const x = Math.max(halfSize, Math.min(a.width - halfSize, c.x + Math.cos(rad) * R));
    const y = Math.max(halfSize + 70, Math.min(a.height - halfSize, c.y + Math.sin(rad) * R));
    el.style.left = `${x}px`;
    el.style.top = `${y}px`;
    return { x, y };
  }

  // The hero swings its brush and a toothpaste bolt flies at the target.
  shoot(target, onHit, duration = 260) {
    if (!target?.isConnected) return;
    const from = this.centerOf(this.hero, 0.86, 0.3);
    const to = this.centerOf(target, 0.5, 0.5);
    const bolt = img(ART.icon('bolt'), 'bolt');
    Object.assign(bolt.style, { left: `${from.x}px`, top: `${from.y}px` });
    this.stage.append(bolt);
    this.hero.classList.remove('attack');
    void this.hero.offsetWidth;
    this.hero.classList.add('attack');
    audio.fx('zap', { rate: 0.9 + Math.random() * 0.25 });
    const anim = bolt.animate([
      { transform: 'translate(-50%, -50%) scale(.5)' },
      { transform: `translate(calc(-50% + ${to.x - from.x}px), calc(-50% + ${to.y - from.y}px)) scale(1.1)` },
    ], { duration, easing: 'ease-in' });
    anim.onfinish = () => {
      bolt.remove();
      if (!target.isConnected) return;
      target.classList.remove('hit');
      void target.offsetWidth;
      target.classList.add('hit');
      onHit?.();
    };
  }

  // The core timed step used by both brushing zones and floss gaps. Time only
  // advances while he is in view and moving at his mouth.
  track(duration, onTick) {
    return new Promise(resolve => {
      let clock = 0, moving = 0;
      let last = performance.now();
      const frame = now => {
        if (this.aborted) return resolve({ aborted: true, clock, moving });
        const dt = Math.min(0.1, (now - last) / 1000) * this.speed;
        last = now;
        if (this.skip) {
          this.skip = false;
          return resolve({ clock: duration, moving: duration, skipped: true });
        }
        const st = this.tracker.status(now);
        this.updatePause(st);
        let active = false;
        if (!this.paused && !this.settingsOpen) {
          active = st.brushing;
          if (active) {
            clock += dt;
            if (st.movingNow) moving += dt;
          }
        }
        onTick(Math.min(1, clock / duration), { ...st, active, now });
        if (clock >= duration) return resolve({ clock, moving });
        requestAnimationFrame(frame);
      };
      requestAnimationFrame(frame);
    }).then(r => { this.check(); return r; });
  }

  updatePause(st) {
    const should = !st.inView;
    if (should && !this.paused) {
      this.paused = true;
      this.applyFreeze();
      const p = $('#pause');
      p.querySelector('.pause-text').textContent = st.starting ? 'Getting the mirror ready…' : 'Come back to the mirror!';
      p.hidden = false;
      audio.duck(0.3);
      if (!st.starting) audio.fx('pause');
      this.pausedStarting = !!st.starting;
    } else if (should && this.paused && this.pausedStarting && !st.starting) {
      this.pausedStarting = false;
      $('#pause .pause-text').textContent = 'Come back to the mirror!';
    } else if (!should && this.paused) {
      this.paused = false;
      this.applyFreeze();
      $('#pause').hidden = true;
      audio.duck(1);
      if (!this.pausedStarting) audio.fx('resume');
      this.pausedStarting = false;
    }
  }

  clearPause() {
    this.paused = false;
    $('#pause').hidden = true;
    audio.duck(1);
    this.applyFreeze();
  }

  // ------------------------------------------------------------ routine wrapper

  async run(kind) {
    if (this.running) return;
    this.reset();
    this.running = true;
    keepAwake(true);
    $('#pause .pause-art').replaceChildren(heroEl('wait', store.hero, 'pause-hero'), img(ART.icon('face_outline'), 'pause-face'));
    try {
      if (kind === 'swish') await this.swishRoutine();
      else if (kind === 'morning') await this.morningRoutine();
      else await this.nightRoutine();
    } catch (e) {
      if (!(e instanceof Abort)) { console.error(e); toast('Something went wrong — back to the start.'); }
    } finally {
      this.cleanup();
    }
  }

  cleanup() {
    this.running = false;
    this.tracker.stop();
    keepAwake(false);
    audio.stopMusic(1.2);
    this.clearPause();
    document.body.classList.remove('cam');
    document.querySelectorAll('.banner').forEach(b => b.remove());
    this.strip.replaceChildren();
    this.stage.replaceChildren();
    this.onExit?.();
  }

  startCamera() {
    if (store.settings.camera) this.tracker.start();
    else this.tracker.stop();
    document.body.classList.add('cam');
  }

  preload(world) {
    preloadImages([ART.world(world), ART.world(world, true), ...SMALL_GOBLINS.map(ART.goblin), ART.goblin('big'),
      ART.goblin('big_hurt'), ART.goblin('big_dizzy'), ART.goblin('sneaky'), ART.icon('bolt')]);
  }

  // ------------------------------------------------------------ night: brush & floss

  async nightRoutine() {
    const world = store.worldForTonight(catalog.worlds.map(w => w.id));
    this.preload(world);
    this.startCamera();
    const result = await this.brushing(world, NIGHT_STEPS);
    await this.flossPause();
    await this.flossing();
    await this.reward(result);
    await this.goodnight(world);
  }

  // ------------------------------------------------------------ morning: brush only

  async morningRoutine() {
    const worlds = catalog.worlds.map(w => w.id);
    const world = worlds[Math.floor(Math.random() * worlds.length)];
    this.preload(world);
    this.startCamera();
    await this.brushing(world, MORNING_STEPS);
    this.tracker.stop();
    document.body.classList.remove('cam');
    this.setStrip(MORNING_STEPS, 1);
    store.addMorningSun();
    audio.fx('fanfare');
    audio.fx('sparkle');
    const done = h('button', { class: 'btn' }, img(ART.icon('home')), 'All done');
    this.stage.replaceChildren();
    this.show(h('div', { class: 'center-col reward' },
      h('p', { class: 'big-text' }, 'Good morning!'),
      h('div', { class: 'reveal' }, img(ART.icon('sun_sticker'))),
      heroEl('cheer', store.hero, 'hero-small'),
      this.unlockCard(),
      h('div', { class: 'row' },
        h('button', { class: 'btn small blue', onclick: () => { audio.fx('tap'); showCalendar(); } }, img(ART.icon('calendar')), 'Calendar')),
      done));
    await this.waitTap(done);
    $('#overlay').hidden = true;
  }

  // ------------------------------------------------------------ brushing

  async brushing(world, steps) {
    const s = store.settings;
    this.setStrip(steps, 0);
    this.setBg(ART.world(world));
    audio.playMusic('music_adventure');
    const zoneDur = (s.brushMinutes * 60) / ZONES.length;
    const guide = new Guide('brush', ZONES.length);
    this.hero = heroEl('ready', store.hero, 'center');
    this.stage.replaceChildren(this.hero);
    this.show(h('div', {}, guide.el));
    guide.show(ZONES[0], 0);
    this.banner(catalog.worlds.find(w => w.id === world).name + '!');
    await this.sleep(1400);
    await this.countdown(5);

    if (this.tracker.status().noCamera && s.camera) toast('Camera not available — timers run on their own.');

    this.horde = [];
    let clock = 0, moving = 0, skipping = false, photo = null, big = null;
    for (let i = 0; i < ZONES.length; i++) {
      const z = ZONES[i];
      const final = i === ZONES.length - 1;
      guide.show(z, i);
      if (!final) {
        while (this.alive().length < 3) this.spawnGoblin(z);
      } else {
        audio.playMusic('music_boss', 0.8);
        big = this.spawnBig();
        this.banner(store.bigEscaped ? 'He’s back!' : 'Big Goblin!');
      }
      let lastShot = performance.now(), lastHit = 0, spawnClock = 0, lastNow = performance.now();
      const res = skipping ? { clock: zoneDur, moving: zoneDur, skipped: true } : await this.track(zoneDur, (p, st) => {
        const dt = st.now - lastNow;
        lastNow = st.now;
        guide.setProgress(p);
        guide.setActive(st.active);
        this.hero.classList.toggle('idle', !st.active);
        // New goblins keep arriving; brushing too slowly lets them pile up.
        if (!this.paused && !this.settingsOpen) {
          spawnClock += dt * this.speed;
          if (spawnClock >= SPAWN_MS) { spawnClock = 0; if (this.alive().length < MAX_GOBLINS) this.spawnGoblin(z); }
        }
        if (final) big.hp.style.transform = `scaleX(${1 - p})`;
        if (st.active && this.readyToShoot(st, lastShot)) {
          lastShot = st.now;
          const target = this.alive()[0];
          if (target) {
            target.targeted = true;
            this.shoot(target.el, () => this.popGoblin(target));
          } else if (final) {
            this.shoot(big.body, () => {
              if (p - lastHit >= 0.05) { lastHit = p; big.el.classList.add('hurt'); setTimeout(() => big.el.classList.remove('hurt'), 350); }
            });
          }
        }
        if (final && !photo && p > 0.35 && st.faceNow) {
          photo = this.tracker.snapshot();
          if (photo) { const f = $('#flash'); f.classList.remove('go'); void f.offsetWidth; f.classList.add('go'); }
        }
      });
      if (res.skipped) skipping = true;
      clock += res.clock;
      moving += res.moving;
      if (!final) audio.fx('chime');
    }
    guide.finish();
    guide.setActive(true);
    this.hero.classList.remove('idle');

    const score = skipping ? 1 : clock > 0 ? moving / clock : 1;
    const passed = skipping || score >= s.passMark;
    big.hp.parentElement.remove();
    if (passed) {
      audio.stopMusic(0.8);
      this.alive().forEach((g, k) => setTimeout(() => this.popGoblin(g), k * 120));
      big.body.querySelector('img').src = ART.goblin('big_dizzy');
      big.el.classList.add('beaten');
      audio.fx('defeat');
      setPose(this.hero, 'cheer');
      this.hero.classList.add('cheer');
      await this.sleep(1500);
      this.stage.append(h('div', { class: 'burst', style: { left: big.el.style.left || '50%', top: big.el.style.top, width: '60vw', position: 'absolute' } }));
      audio.fx('pop');
      this.banner('You beat him!', 1800);
      await this.sleep(1800);
      store.bigEscaped = false;
    } else {
      audio.stopMusic(2);
      this.alive().forEach(g => { g.popped = true; g.el.classList.remove('enter'); g.el.classList.add('flee'); });
      big.el.classList.add('escape');
      big.el.append(h('div', { class: 'bubble' }, 'I\'ll be back tomorrow!'));
      audio.fx('whoosh');
      audio.fx('giggle');
      await this.sleep(5000);
      store.bigEscaped = true;
    }
    this.stage.replaceChildren();
    return { passed, score, photo, world };
  }

  // 5-4-3-2-1 before brushing starts.
  async countdown(n) {
    for (let k = n; k > 0; k--) {
      const c = h('div', { class: 'countdown' }, k);
      $('#app').append(c);
      audio.fx('tap', { rate: 0.8 });
      await this.sleep(1000).finally(() => c.remove());
    }
    this.banner('Go!', 900);
    audio.fx('chime');
  }

  // Bolts follow his brushing: about one a second when he brushes fast, up to
  // one every four seconds when slow, timed to land on a brush stroke.
  readyToShoot(st, lastShot) {
    const rate = Math.max(0.01, st.strokeRate || 0);
    const interval = Math.min(MAX_SHOT_MS, Math.max(MIN_SHOT_MS, 4000 / rate)) / this.speed;
    const since = st.now - lastShot;
    if (since < interval) return false;
    const freshStroke = st.lastStroke && st.now - st.lastStroke < 200 && st.lastStroke > lastShot;
    return freshStroke || since > interval + 600 / this.speed;
  }

  alive() { return this.horde.filter(g => !g.popped && !g.targeted); }

  spawnGoblin(zone) {
    const taken = this.horde.filter(g => !g.popped).map(g => g.slot);
    const preferred = ZONE_ANGLES[zone];
    // Fill the current zone's spots first, then the rest of the ring, then an outer ring.
    const slot = [...preferred.map(a => [a, 1]), ...RING.map(a => [a, 1]), ...OUTER.map(a => [a, 1.45])]
      .find(([a, r]) => !taken.some(t => t[0] === a && t[1] === r)) || [Math.random() * 360, 1.6];
    const type = SMALL_GOBLINS[this.horde.length % SMALL_GOBLINS.length];
    const el = h('div', { class: 'sprite goblin enter' }, img(ART.goblin(type)));
    el.querySelector('img').style.animationDelay = `${-Math.random()}s`;
    this.stage.append(el);
    this.placeAround(el, slot[0], slot[1], el.offsetWidth / 2 || 50);
    const g = { el, slot, popped: false, targeted: false };
    this.horde.push(g);
    if (this.horde.length > 3) audio.fx('giggle', { gain: 0.4, rate: 1.2 });
    return g;
  }

  popGoblin(g) {
    if (g.popped) return;
    g.popped = true;
    g.el.classList.add('pop');
    audio.fx('pop', { rate: 0.9 + Math.random() * 0.3 });
    setTimeout(() => g.el.remove(), 600);
  }

  spawnBig() {
    const hp = h('i');
    const body = h('div', { class: 'body' }, img(ART.goblin('big')), img(ART.goblin('big_hurt')));
    const el = h('div', { class: 'big enter' }, h('div', { class: 'bar hp' }, hp), body);
    this.stage.append(el);
    // Stand just above the hero, clear of the step strip.
    const c = this.centerOf(this.hero);
    const height = el.offsetWidth + 26; // square art plus the health bar; images may not be laid out yet
    el.style.top = `${Math.max(76, c.y - c.h * 0.5 - height + 20)}px`;
    audio.fx('giggle', { rate: 0.7 });
    return { el, body, hp };
  }

  // ------------------------------------------------------------ flossing

  async flossPause() {
    this.setStrip(NIGHT_STEPS, 1);
    audio.playMusic('music_calm', 2);
    audio.duck(0.6);
    const btn = h('button', { class: 'btn blue' }, img(ART.icon('pick')), 'Ready!');
    this.show(h('div', { class: 'center-col calm' },
      img(ART.icon('pick'), 'hero-img'),
      h('p', { class: 'big-text' }, 'Get your floss pick'),
      btn));
    await this.waitTap(btn);
    audio.duck(1);
  }

  async flossing() {
    const s = store.settings;
    this.setStrip(NIGHT_STEPS, 2);
    const gaps = GAPS.slice(0, s.flossGaps);
    const guide = new Guide('floss', gaps.length);
    guide.el.classList.add('floss');
    this.hero = heroEl('ready', store.hero, 'center');
    this.stage.replaceChildren(this.hero);
    this.show(h('div', {}, guide.el));
    guide.show(gaps[0], 0);
    this.banner('Floss time!', 1000);
    await this.sleep(600);
    let skipping = false;
    for (let i = 0; i < gaps.length; i++) {
      const gap = gaps[i];
      guide.show(gap, i);
      // A sneaky goblin peeks out somewhere around the hero, never the same side twice.
      const deg = (i * 137 + 200) % 360;
      const el = h('div', { class: 'sprite sneaky goblin enter' }, img(ART.goblin('sneaky')));
      this.stage.append(el);
      const { x } = this.placeAround(el, deg, 0.95, 45);
      const res = skipping ? { skipped: true } : await this.track(s.flossSeconds, (p, st) => {
        guide.setProgress(p);
        guide.setActive(st.active);
        this.hero.classList.toggle('idle', !st.active);
      });
      if (res.skipped) skipping = true;
      const runAway = () => {
        el.classList.remove('enter');
        el.classList.add('run', x > this.centerOf(this.hero).x ? 'right' : 'left');
        audio.fx('whoosh', { gain: 0.5 });
        audio.fx('chime', { gain: 0.6 });
        setTimeout(() => el.remove(), 800);
      };
      if (skipping) runAway();
      else { this.shoot(el, runAway, 130); await this.sleep(150); }
    }
    guide.finish();
    setPose(this.hero, 'cheer');
    this.banner('Great flossing!', 1200);
    await this.sleep(1200);
    this.stage.replaceChildren();
  }

  // ------------------------------------------------------------ reward

  // A card showing any hero items he just earned, or nothing.
  unlockCard() {
    const fresh = takeNewUnlocks();
    if (!fresh.length) return null;
    audio.fx('sparkle');
    return h('div', { class: 'unlock-card card' },
      h('div', { class: 'unlock-title' }, fresh.length > 1 ? 'New hero items!' : 'New hero item!'),
      h('div', { class: 'unlock-items' }, fresh.map(({ part, value }) =>
        heroEl('cheer', { ...store.hero, [part]: value }, 'unlock-hero'))),
      h('div', { class: 'unlock-sub' }, 'Tap your hero on the home screen to try it on.'));
  }

  pickEmoji(world) {
    const owned = store.collection;
    const pool = [];
    const consider = w => allEmoji().filter(e => e.world === w && !owned[e.id])
      // A sparkly version can only turn up once its regular version is found.
      .forEach(e => { if (!e.gold) pool.push([e, 1]); else if (owned[e.base]) pool.push([e, GOLD_WEIGHT]); });
    consider(world);
    if (!pool.length) catalog.worlds.forEach(w => consider(w.id));
    if (!pool.length) return null;
    let r = Math.random() * pool.reduce((t, [, wt]) => t + wt, 0);
    for (const [e, wt] of pool) { if ((r -= wt) <= 0) return e; }
    return pool[pool.length - 1][0];
  }

  async reward({ passed, photo, world }) {
    this.setStrip(NIGHT_STEPS, 3);
    audio.stopMusic(1);
    this.tracker.stop();
    document.body.classList.remove('cam');
    const emoji = passed ? this.pickEmoji(world) : null;
    if (emoji) store.addEmoji(emoji.id);
    store.completeNight({ passed, emoji: emoji?.id || null, world });

    const goodnightBtn = h('button', { class: 'btn' }, img(ART.icon('moon')), 'Goodnight');
    const col = h('div', { class: 'center-col reward' });
    this.show(col);
    if (passed) {
      audio.fx('fanfare');
      audio.fx('sparkle');
      if (emoji) {
        col.append(h('p', { class: 'big-text' }, emoji.gold ? 'Sparkly emoji!' : 'New emoji!'),
          h('div', { class: `reveal ${emoji.gold ? 'gold' : ''}` }, img(ART.emoji(emoji.id))),
          h('div', { class: 'emoji-name' }, emoji.name));
      } else {
        col.append(h('p', { class: 'big-text' }, 'You found them all!'), h('div', { class: 'reveal' }, img(ART.icon('star'))));
      }
      await this.sleep(1200);
      if (photo) {
        const owned = Object.entries(store.collection).sort((a, b) => (a[1] < b[1] ? 1 : -1)).map(([id]) => id);
        const tray = emoji ? [emoji.id, ...owned.filter(id => id !== emoji.id)] : owned;
        const editor = photoEditor(photo, emoji ? [emoji.id] : [], tray);
        const saveBtn = h('button', { class: 'btn pink small' }, img(ART.icon('camera')), 'Save photo');
        saveBtn.addEventListener('click', async () => {
          audio.fx('tap');
          const ok = await editor.save();
          if (ok) { saveBtn.textContent = 'Saved ✓'; }
        });
        col.append(editor.el, saveBtn);
      }
    } else {
      col.append(h('p', { class: 'big-text' }, 'No emoji tonight'),
        h('div', { class: 'reveal' }, img(ART.goblin('big'))),
        h('div', { class: 'emoji-name' }, 'Beat the big goblin tomorrow!'));
    }
    const card = this.unlockCard();
    if (card) col.append(card);
    col.append(h('div', { class: 'row' },
      h('button', { class: 'btn small blue', onclick: () => { audio.fx('tap'); showCollection(emoji?.id); } }, img(ART.icon('book')), 'Collection'),
      h('button', { class: 'btn small blue', onclick: () => { audio.fx('tap'); showCalendar(); } }, img(ART.icon('calendar')), 'Calendar')),
    goodnightBtn);
    await this.waitTap(goodnightBtn);
    $('#overlay').hidden = true;
  }

  // ------------------------------------------------------------ goodnight

  async goodnight(world) {
    this.setStrip(NIGHT_STEPS, 4);
    keepAwake(false);
    this.setBg(ART.world(world, true));
    audio.playMusic('music_lullaby', 3);
    const a = this.appRect();
    const W = a.width, H = a.height;
    const sleepers = [
      [ART.goblin('big_sleep'), 0.2, 0.7, Math.min(W * 0.34, 190)],
      [ART.goblin('a_sleep'), 0.82, 0.68, Math.min(W * 0.22, 120)],
      [ART.goblin('b_sleep'), 0.14, 0.94, Math.min(W * 0.2, 110)],
      [ART.goblin('c_sleep'), 0.86, 0.94, Math.min(W * 0.2, 110)],
      [ART.goblin('sneaky_sleep'), 0.66, 0.78, Math.min(W * 0.15, 80)],
    ];
    const cast = h('div', { class: 'night-cast' });
    const zzz = (x, y, w, i) => {
      const z = img(ART.icon('zzz'), 'zzz');
      Object.assign(z.style, { left: `${x * W + w * 0.2}px`, top: `${y * H - w * 1.1}px`, animationDelay: `${i * 0.6}s` });
      return z;
    };
    sleepers.forEach(([src, x, y, w], i) => {
      const s = img(src, 'sleeper');
      Object.assign(s.style, { left: `${x * W}px`, top: `${y * H}px`, width: `${w}px`, animationDelay: `${-i * 0.7}s` });
      cast.append(s, zzz(x, y, w, i));
    });
    const hw = Math.min(W * 0.38, 210);
    const hero = heroEl('sleep', store.hero, 'sleeper');
    Object.assign(hero.style, { left: `${0.5 * W}px`, top: `${0.88 * H}px`, width: `${hw}px` });
    cast.append(hero, zzz(0.5, 0.88, hw, 5));
    this.stage.replaceChildren(cast);
    const done = h('button', { class: 'btn small', style: { opacity: 0, transition: 'opacity 1s' } }, 'Done');
    this.show(h('div', {},
      h('div', { class: 'goodnight-text' }, h('p', { class: 'big-text' }, 'Goodnight!'),
        h('div', { style: { marginTop: '24px' } }, done))));
    await this.sleep(3000);
    done.style.opacity = 1;
    // Let the lullaby play softly for a while, then fade out.
    const fade = setTimeout(() => audio.stopMusic(8), 60000);
    await this.waitTap(done);
    clearTimeout(fade);
  }

  // ------------------------------------------------------------ swish

  async swishRoutine() {
    this.setBg(ART.home);
    this.setStrip(SWISH_STEPS, 0);
    audio.playMusic('music_calm', 1.5);
    const ready = h('button', { class: 'btn blue' }, img(ART.icon('cup')), 'Ready!');
    this.show(h('div', { class: 'center-col calm' },
      img(ART.icon('cup'), 'hero-img'), h('p', { class: 'big-text' }, 'Take a sip'), ready));
    await this.waitTap(ready);

    this.setStrip(SWISH_STEPS, 1);
    const secs = store.settings.swishSeconds;
    const count = h('div', { class: 'count' }, secs);
    this.show(h('div', { class: 'center-col' }, heroEl('swish', store.hero, 'swish-buddy'), count));
    const wave = h('div', { class: 'wave' }, img(ART.icon('wave')));
    const H = this.appRect().height;
    const goblins = [0.18, 0.5, 0.82].map((x, i) => {
      const el = h('div', { class: 'sprite goblin' }, img(ART.goblin(SMALL_GOBLINS[i])));
      Object.assign(el.style, { left: `${x * 100}%`, top: `${H * 0.86}px` });
      this.stage.append(el);
      return { el, x, gone: false };
    });
    this.stage.append(wave);
    audio.fx('wave');
    await new Promise(resolve => {
      const start = performance.now();
      let lastWave = start, pausedFor = 0, lastNow = start;
      const frame = now => {
        if (this.aborted) return resolve();
        if (this.skip) { this.skip = false; return resolve(); }
        if (this.settingsOpen) pausedFor += now - lastNow;
        lastNow = now;
        const t = ((now - start - pausedFor) / 1000) * this.speed;
        const p = Math.min(1, t / secs);
        count.textContent = Math.max(0, Math.ceil(secs - t));
        wave.style.transform = `translateX(${p * 100}vw)`;
        goblins.forEach(g => {
          if (!g.gone && p >= g.x * 0.95) { g.gone = true; g.el.classList.add('washed'); audio.fx('pop', { gain: 0.6 }); }
        });
        if (now - lastWave > 3000) { lastWave = now; audio.fx('wave', { gain: 0.8 }); }
        if (p >= 1) return resolve();
        requestAnimationFrame(frame);
      };
      requestAnimationFrame(frame);
    });
    this.check();
    this.stage.replaceChildren();

    this.setStrip(SWISH_STEPS, 2);
    audio.stopMusic(0.5);
    const spitDone = h('button', { class: 'btn', style: { visibility: 'hidden' } }, 'Done!');
    this.show(h('div', { class: 'center-col' },
      h('p', { class: 'big-text spit-text' }, 'Spit!'), img(ART.icon('sink'), 'hero-img'), spitDone));
    audio.fx('chime');
    await this.sleep(1500);
    spitDone.style.visibility = 'visible';
    await this.waitTap(spitDone);

    this.setStrip(SWISH_STEPS, 3);
    store.addSwishStar();
    audio.fx('fanfare');
    audio.fx('sparkle');
    const home = h('button', { class: 'btn' }, img(ART.icon('home')), 'All done');
    this.show(h('div', { class: 'center-col reward' },
      h('p', { class: 'big-text' }, 'Gold star!'),
      h('div', { class: 'reveal' }, img(ART.icon('star'))),
      h('div', { class: 'row' },
        h('button', { class: 'btn small blue', onclick: () => { audio.fx('tap'); showCalendar(); } }, img(ART.icon('calendar')), 'Calendar')),
      home));
    await this.waitTap(home);
    $('#overlay').hidden = true;
  }
}
