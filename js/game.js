// The routines. The steps, their order and their sounds are the same every
// time; only the world (scenery and emoji set) changes. No narration: just
// short on-screen text.
//
// A routine is played by one kid or by two side by side. With two, each has
// their own hero, their bolts follow their own brushing, and each earns their
// own emoji from their own score; the goblins and the big goblin are shared.

import { $, h, img, toast } from './dom.js';
import { ART, ZONES, SMALL_GOBLINS, layout, catalog, allEmoji, preloadImages } from './assets.js';
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

// Where goblins gather around the heroes for each zone (degrees, 0 = right, 90 = down).
const ZONE_ANGLES = {
  top_left: [200, 226, 252], top_front: [244, 270, 296], top_right: [288, 314, 340],
  bottom_right: [10, 34, 58], bottom_front: [64, 90, 116], bottom_left: [122, 146, 170],
};
const MIN_SHOT_MS = 1000;  // fastest a hero fires (fast brushing)
const MAX_SHOT_MS = 4000;  // slowest a hero fires (slow brushing)
const SPAWN_MS = 3000;     // a new goblin arrives this often (per player)
const MAX_GOBLINS = 10;    // per player
const RING = [210, 240, 270, 300, 330, 20, 50, 130, 160];
const OUTER = [225, 270, 315, 30, 150];
// Two players: goblin spots on the left hero's outer side (mirrored for the right hero).
const DUO_SIDE = [[180, 1], [208, 1], [152, 1], [234, 1], [128, 1],
  [194, 1.55], [166, 1.55], [222, 1.55], [140, 1.55], [248, 1.4]];
const GOLD_WEIGHT = 0.35;  // sparkly emoji are rarer than regular ones

// Floss gaps: the whole top row, then the bottom row, each swept left to right.
// Fewer gaps than the 9 per row keeps the ones nearest the front.
function flossOrder(count) {
  const row = (name, k) => [...Array(9).keys()].sort((a, b) => Math.abs(a - 4) - Math.abs(b - 4)).slice(0, k)
    .sort((a, b) => a - b).map(i => `gap_${name}_${i}`).filter(id => layout.gaps[id]);
  const top = Math.ceil(count / 2);
  return [...row('top', top), ...row('bot', count - top)];
}

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
    this.players = [0];
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

  get duo() { return this.players.length > 1; }
  look(p) { return store.profile(this.players[p]).hero; }
  nameOf(p) { return store.profile(this.players[p]).name; }

  // The hero (or both heroes, side by side) in the middle of the screen.
  makeHeroes(pose = 'ready') {
    this.heroes = this.players.map((_, p) => {
      const el = heroEl(pose, this.look(p), `center ${this.duo ? (p ? 'right' : 'left') : ''}`);
      if (this.duo) { el.dataset.name = this.nameOf(p); setPose(el, pose, this.look(p)); }
      return el;
    });
    this.stage.replaceChildren(...this.heroes);
  }

  // The area the goblins circle: around one hero, or around both together.
  ring() {
    const cs = this.heroes.map(el => this.centerOf(el));
    const x0 = Math.min(...cs.map(c => c.x - c.w / 2)), x1 = Math.max(...cs.map(c => c.x + c.w / 2));
    return { x: (x0 + x1) / 2, y: cs[0].y, w: x1 - x0, h: cs[0].h };
  }

  // around: a hero index to circle just that hero (two-player games).
  placeAround(el, deg, radiusFactor = 1.0, halfSize = 50, around = null) {
    const a = this.appRect();
    const c = around === null ? this.ring() : this.centerOf(this.heroes[around]);
    const rad = deg * Math.PI / 180;
    const rx = Math.max(c.w, c.h) * 0.62 * radiusFactor, ry = c.h * 0.62 * radiusFactor;
    const x = Math.max(halfSize, Math.min(a.width - halfSize, c.x + Math.cos(rad) * rx));
    const y = Math.max(halfSize + 70, Math.min(a.height - halfSize, c.y + Math.sin(rad) * ry));
    el.style.left = `${x}px`;
    el.style.top = `${y}px`;
    return { x, y };
  }

  // A hero swings its brush and a toothpaste bolt flies at the target.
  shoot(p, target, onHit, duration = 260) {
    const hero = this.heroes[p];
    if (!target?.isConnected || !hero) return;
    const from = this.centerOf(hero, 0.86, 0.3);
    const to = this.centerOf(target, 0.5, 0.5);
    const bolt = img(ART.icon('bolt'), 'bolt');
    Object.assign(bolt.style, { left: `${from.x}px`, top: `${from.y}px` });
    this.stage.append(bolt);
    hero.classList.remove('attack');
    void hero.offsetWidth;
    hero.classList.add('attack');
    audio.fx('zap', { rate: 0.9 + Math.random() * 0.25 + p * 0.15 });
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

  // The core timed step used by both brushing zones and floss gaps. Time
  // advances while everyone is in view and at least one of them is brushing;
  // each player's score counts only their own movement.
  track(duration, onTick) {
    const n = this.players.length;
    return new Promise(resolve => {
      let clock = 0;
      const moving = new Array(n).fill(0);
      let last = performance.now();
      const frame = now => {
        if (this.aborted) return resolve({ aborted: true, clock, moving });
        const dt = Math.min(0.1, (now - last) / 1000) * this.speed;
        last = now;
        if (this.skip) {
          this.skip = false;
          return resolve({ clock: duration, moving: moving.map(() => duration), skipped: true });
        }
        const sts = this.players.map((_, p) => this.tracker.status(now, p));
        this.updatePause(sts);
        let active = false;
        if (!this.paused && !this.settingsOpen) {
          active = sts.some(st => st.brushing);
          if (active) {
            clock += dt;
            sts.forEach((st, p) => { if (st.movingNow) moving[p] += dt; });
          }
        }
        onTick(Math.min(1, clock / duration), sts.map(st => ({ ...st, active: active && st.brushing, now })), { active, now });
        if (clock >= duration) return resolve({ clock, moving });
        requestAnimationFrame(frame);
      };
      requestAnimationFrame(frame);
    }).then(r => { this.check(); return r; });
  }

  updatePause(sts) {
    const missing = sts.map((st, p) => (st.inView ? -1 : p)).filter(p => p >= 0);
    const starting = sts.some(st => st.starting);
    const should = missing.length > 0;
    const key = starting ? 'starting' : missing.join(',');
    if (should && (!this.paused || this.pauseKey !== key)) {
      if (!this.paused) {
        this.paused = true;
        this.applyFreeze();
        audio.duck(0.3);
        if (!starting) audio.fx('pause');
      }
      this.pauseKey = key;
      const who = this.duo && !starting ? missing.map(p => this.nameOf(p)).join(' and ') : '';
      $('#pause .pause-text').textContent = starting ? 'Getting the mirror ready…'
        : who ? `Come back to the mirror, ${who}!` : 'Come back to the mirror!';
      $('#pause .pause-art').replaceChildren(
        ...(starting ? [0] : missing).map(p => heroEl('wait', this.look(p), 'pause-hero')),
        img(ART.icon('face_outline'), 'pause-face'));
      $('#pause').hidden = false;
      this.pausedStarting = starting;
    } else if (!should && this.paused) {
      this.paused = false;
      this.pauseKey = null;
      this.applyFreeze();
      $('#pause').hidden = true;
      audio.duck(1);
      if (!this.pausedStarting) audio.fx('resume');
      this.pausedStarting = false;
    }
  }

  clearPause() {
    this.paused = false;
    this.pauseKey = null;
    $('#pause').hidden = true;
    audio.duck(1);
    this.applyFreeze();
  }

  // ------------------------------------------------------------ routine wrapper

  // players: profile indexes, e.g. [0] for Oliver alone or [0, 1] for both.
  async run(kind, players = [0]) {
    if (this.running) return;
    this.reset();
    this.players = players;
    this.running = true;
    keepAwake(true);
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
    document.body.classList.remove('cam', 'duo');
    document.querySelectorAll('.banner').forEach(b => b.remove());
    this.strip.replaceChildren();
    this.stage.replaceChildren();
    store.use(0);
    this.onExit?.();
  }

  startCamera() {
    if (store.settings.camera) this.tracker.start(this.players.length);
    else this.tracker.stop();
    document.body.classList.add('cam');
    document.body.classList.toggle('duo', this.duo);
  }

  preload(world) {
    preloadImages([ART.world(world), ART.world(world, true), ...SMALL_GOBLINS.map(ART.goblin), ART.goblin('big'),
      ART.goblin('big_hurt'), ART.goblin('big_dizzy'), ART.goblin('sneaky'), ART.icon('bolt')]);
  }

  // Runs fn for each player with their profile active.
  forEachKid(fn) {
    return this.players.map((profile, p) => { store.use(profile); return fn(p, profile); });
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
    audio.fx('fanfare');
    audio.fx('sparkle');
    const cards = this.forEachKid(p => {
      store.addMorningSun();
      return h('div', { class: 'kid-col' },
        this.duo ? h('div', { class: 'kid-name' }, this.nameOf(p)) : null,
        heroEl('cheer', this.look(p), 'hero-small'),
        this.unlockCard(p));
    });
    const done = h('button', { class: 'btn' }, img(ART.icon('home')), 'All done');
    this.stage.replaceChildren();
    this.show(h('div', { class: 'center-col reward' },
      h('p', { class: 'big-text' }, 'Good morning!'),
      h('div', { class: 'reveal' }, img(ART.icon('sun_sticker'))),
      h('div', { class: 'kids' }, cards),
      h('div', { class: 'row' },
        h('button', { class: 'btn small blue', onclick: () => { audio.fx('tap'); showCalendar(this.players[0]); } }, img(ART.icon('calendar')), 'Calendar')),
      done));
    await this.waitTap(done);
    $('#overlay').hidden = true;
  }

  // ------------------------------------------------------------ brushing

  async brushing(world, steps) {
    const s = store.settings;
    const n = this.players.length;
    this.setStrip(steps, 0);
    this.setBg(ART.world(world));
    audio.playMusic('music_adventure');
    const zoneDur = (s.brushMinutes * 60) / ZONES.length;
    const guide = new Guide('brush', ZONES.length);
    this.makeHeroes('ready');
    this.show(h('div', {}, guide.el));
    guide.show(ZONES[0], 0);
    this.banner(catalog.worlds.find(w => w.id === world).name + '!');
    await this.sleep(1400);
    await this.countdown(5);

    if (this.tracker.status().noCamera && s.camera) toast('Camera not available — timers run on their own.');

    const wasEscaped = this.forEachKid(() => store.bigEscaped).some(Boolean);
    this.horde = [];
    let clock = 0, skipping = false, photo = null, big = null;
    const moving = new Array(n).fill(0);
    for (let i = 0; i < ZONES.length; i++) {
      const z = ZONES[i];
      const final = i === ZONES.length - 1;
      guide.show(z, i);
      if (!final) {
        for (let k = 0; k < n; k++) while (this.alive(this.duo ? k : null).length < 3) this.spawnGoblin(z, this.duo ? k : null);
      } else {
        audio.playMusic('music_boss', 0.8);
        big = this.spawnBig();
        this.banner(wasEscaped ? 'He’s back!' : 'Big Goblin!');
      }
      const lastShot = new Array(n).fill(performance.now());
      let lastHit = 0, spawnClock = 0, lastNow = performance.now();
      const res = skipping ? { clock: zoneDur, moving: moving.map(() => zoneDur), skipped: true } : await this.track(zoneDur, (p, sts, all) => {
        const dt = all.now - lastNow;
        lastNow = all.now;
        guide.setProgress(p);
        guide.setActive(all.active);
        // New goblins keep arriving; brushing too slowly lets them pile up.
        if (!this.paused && !this.settingsOpen) {
          spawnClock += dt * this.speed * n;
          if (spawnClock >= SPAWN_MS) {
            spawnClock = 0;
            // With two players, the new goblin goes to whoever has fewer.
            const owner = this.duo ? (this.alive(0).length <= this.alive(1).length ? 0 : 1) : null;
            if (this.alive(owner).length < MAX_GOBLINS) this.spawnGoblin(z, owner);
          }
        }
        if (final) big.hp.style.transform = `scaleX(${1 - p})`;
        sts.forEach((st, k) => {
          this.heroes[k].classList.toggle('idle', !st.active);
          if (!st.active || !this.readyToShoot(st, lastShot[k])) return;
          lastShot[k] = st.now;
          const target = this.alive(this.duo ? k : null)[0];
          if (target) {
            target.targeted = true;
            this.shoot(k, target.el, () => this.popGoblin(target));
          } else if (final) {
            this.shoot(k, big.body, () => {
              if (p - lastHit >= 0.05) { lastHit = p; big.el.classList.add('hurt'); setTimeout(() => big.el.classList.remove('hurt'), 350); }
            });
          }
        });
        if (final && !photo && p > 0.35 && sts.every(st => st.faceNow)) {
          photo = this.tracker.snapshot();
          if (photo) { const f = $('#flash'); f.classList.remove('go'); void f.offsetWidth; f.classList.add('go'); }
        }
      });
      if (res.skipped) skipping = true;
      clock += res.clock;
      res.moving.forEach((m, k) => { moving[k] += m; });
      if (!final) audio.fx('chime');
    }
    guide.finish();
    guide.setActive(true);
    this.heroes.forEach(el => el.classList.remove('idle'));

    // Each kid's own score decides their own emoji; the big goblin is beaten
    // if anyone brushed well enough.
    const scores = moving.map(m => (skipping ? 1 : clock > 0 ? m / clock : 1));
    const passed = scores.map(sc => skipping || sc >= s.passMark);
    const beaten = passed.some(Boolean);
    big.hp.parentElement.remove();
    if (beaten) {
      audio.stopMusic(0.8);
      this.alive().forEach((g, k) => setTimeout(() => this.popGoblin(g), k * 120));
      big.body.querySelector('img').src = ART.goblin('big_dizzy');
      big.el.classList.add('beaten');
      audio.fx('defeat');
      this.heroes.forEach(el => { setPose(el, 'cheer', this.look(this.heroes.indexOf(el))); el.classList.add('cheer'); });
      await this.sleep(1500);
      this.stage.append(h('div', { class: 'burst', style: { left: big.el.style.left || '50%', top: big.el.style.top, width: '60vw', position: 'absolute' } }));
      audio.fx('pop');
      this.banner('You beat him!', 1800);
      await this.sleep(1800);
    } else {
      audio.stopMusic(2);
      this.alive().forEach(g => { g.popped = true; g.el.classList.remove('enter'); g.el.classList.add('flee'); });
      big.el.classList.add('escape');
      big.el.append(h('div', { class: 'bubble' }, 'I\'ll be back tomorrow!'));
      audio.fx('whoosh');
      audio.fx('giggle');
      await this.sleep(5000);
    }
    this.forEachKid(() => { store.bigEscaped = !beaten; });
    this.stage.replaceChildren();
    return { passed, scores, photo, world };
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

  // Bolts follow each kid's brushing: about one a second when brushing fast,
  // up to one every four seconds when slow, timed to land on a brush stroke.
  readyToShoot(st, lastShot) {
    const rate = Math.max(0.01, st.strokeRate || 0);
    const interval = Math.min(MAX_SHOT_MS, Math.max(MIN_SHOT_MS, 4000 / rate)) / this.speed;
    const since = st.now - lastShot;
    if (since < interval) return false;
    const freshStroke = st.lastStroke && st.now - st.lastStroke < 200 && st.lastStroke > lastShot;
    return freshStroke || since > interval + 600 / this.speed;
  }

  // Goblins still to be zapped; with two players, owner picks one hero's goblins.
  alive(owner = null) {
    return this.horde.filter(g => !g.popped && !g.targeted && (owner === null || g.owner === owner));
  }

  // Spots for a goblin. Alone: around the hero, the current zone's side first.
  // Two players: each hero has its own goblins on its own outer side, so no
  // bolt ever flies across the other hero.
  goblinSlots(zone, owner) {
    if (owner === null) {
      return [...ZONE_ANGLES[zone].map(a => [a, 1]), ...RING.map(a => [a, 1]), ...OUTER.map(a => [a, 1.45]),
        ...RING.map(a => [a + 15, 1.3])];
    }
    return DUO_SIDE.map(([a, r]) => [owner ? (540 - a) % 360 : a, r]);
  }

  spawnGoblin(zone, owner = null) {
    const taken = this.horde.filter(g => !g.popped && g.owner === owner).map(g => g.slot);
    const slot = this.goblinSlots(zone, owner)
      .find(([a, r]) => !taken.some(t => t[0] === a && t[1] === r)) || [owner === 1 ? 0 : 180, 1.7];
    const type = SMALL_GOBLINS[this.horde.length % SMALL_GOBLINS.length];
    const el = h('div', { class: 'sprite goblin enter' }, img(ART.goblin(type)));
    el.querySelector('img').style.animationDelay = `${-Math.random()}s`;
    this.stage.append(el);
    this.placeAround(el, slot[0], slot[1], el.offsetWidth / 2 || 50, owner);
    const g = { el, slot, owner, popped: false, targeted: false };
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
    // Stand just above the heroes, clear of the step strip.
    const c = this.ring();
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
      h('p', { class: 'big-text' }, this.duo ? 'Get your floss picks' : 'Get your floss pick'),
      btn));
    await this.waitTap(btn);
    audio.duck(1);
  }

  async flossing() {
    const s = store.settings;
    this.setStrip(NIGHT_STEPS, 2);
    const gaps = flossOrder(s.flossGaps);
    const guide = new Guide('floss', gaps.length);
    guide.el.classList.add('floss');
    this.makeHeroes('ready');
    this.show(h('div', {}, guide.el));
    guide.show(gaps[0], 0);
    this.banner('Floss time!', 1000);
    await this.sleep(1100);
    await this.countdown(3);
    let skipping = false;
    for (let i = 0; i < gaps.length; i++) {
      const gap = gaps[i];
      guide.show(gap, i);
      // A sneaky goblin peeks out somewhere around the heroes, never the same side
      // twice. With two players they take turns, each zapping on their own side.
      const shooter = i % this.players.length;
      const el = h('div', { class: 'sprite sneaky goblin enter' }, img(ART.goblin('sneaky')));
      this.stage.append(el);
      const { x } = this.duo
        ? this.placeAround(el, this.goblinSlots(null, shooter)[Math.floor(i / 2) % 5][0], 0.95, 45, shooter)
        : this.placeAround(el, (i * 137 + 200) % 360, 0.95, 45);
      const res = skipping ? { skipped: true } : await this.track(s.flossSeconds, (p, sts, all) => {
        guide.setProgress(p);
        guide.setActive(all.active);
        sts.forEach((st, k) => this.heroes[k].classList.toggle('idle', !st.active));
      });
      if (res.skipped) skipping = true;
      const runAway = () => {
        el.classList.remove('enter');
        el.classList.add('run', x > this.ring().x ? 'right' : 'left');
        audio.fx('whoosh', { gain: 0.5 });
        audio.fx('chime', { gain: 0.6 });
        setTimeout(() => el.remove(), 800);
      };
      if (skipping) runAway();
      else { this.shoot(shooter, el, runAway, 130); await this.sleep(150); }
    }
    guide.finish();
    this.heroes.forEach((el, p) => setPose(el, 'cheer', this.look(p)));
    this.banner('Great flossing!', 1200);
    await this.sleep(1200);
    this.stage.replaceChildren();
  }

  // ------------------------------------------------------------ reward

  // A card showing any hero items the active kid just earned, or nothing.
  unlockCard(p) {
    const fresh = takeNewUnlocks();
    if (!fresh.length) return null;
    audio.fx('sparkle');
    const look = this.look(p);
    return h('div', { class: 'unlock-card card' },
      h('div', { class: 'unlock-title' }, fresh.length > 1 ? 'New hero items!' : 'New hero item!'),
      h('div', { class: 'unlock-items' }, fresh.map(({ part, value }) =>
        heroEl('cheer', { ...look, [part]: value }, 'unlock-hero'))),
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
    // Pick and save each kid's prize.
    const results = this.forEachKid((p) => {
      const emoji = passed[p] ? this.pickEmoji(world) : null;
      if (emoji) store.addEmoji(emoji.id);
      store.completeNight({ passed: passed[p], emoji: emoji?.id || null, world });
      return { p, emoji, passed: passed[p], owned: { ...store.collection } };
    });

    const goodnightBtn = h('button', { class: 'btn' }, img(ART.icon('moon')), 'Goodnight');
    const col = h('div', { class: 'center-col reward' });
    this.show(col);
    if (passed.some(Boolean)) { audio.fx('fanfare'); audio.fx('sparkle'); }
    const prize = r => {
      if (!r.passed) {
        return [h('div', { class: 'reveal small' }, img(ART.goblin('big'))),
          h('div', { class: 'emoji-name' }, this.duo ? 'No emoji tonight' : 'Beat the big goblin tomorrow!')];
      }
      if (!r.emoji) return [h('div', { class: 'reveal small' }, img(ART.icon('star'))), h('div', { class: 'emoji-name' }, 'Found them all!')];
      return [h('div', { class: `reveal ${r.emoji.gold ? 'gold' : ''} ${this.duo ? 'small' : ''}` }, img(ART.emoji(r.emoji.id))),
        h('div', { class: 'emoji-name' }, r.emoji.name)];
    };
    if (!this.duo) {
      const r = results[0];
      col.append(h('p', { class: 'big-text' },
        !r.passed ? 'No emoji tonight' : !r.emoji ? 'You found them all!' : r.emoji.gold ? 'Sparkly emoji!' : 'New emoji!'), ...prize(r));
    } else {
      col.append(h('p', { class: 'big-text' }, passed.some(Boolean) ? 'New emoji!' : 'No emoji tonight'),
        h('div', { class: 'kids' }, results.map(r => h('div', { class: 'kid-col' },
          h('div', { class: 'kid-name' }, this.nameOf(r.p)), ...prize(r)))));
    }
    await this.sleep(1200);
    const won = results.filter(r => r.emoji);
    if (photo && won.length) {
      // Tonight's emoji first, then everything either kid has won, newest first.
      const owned = Object.entries(Object.assign({}, ...results.map(r => r.owned)))
        .sort((a, b) => (a[1] < b[1] ? 1 : -1)).map(([id]) => id);
      const fresh = won.map(r => r.emoji.id);
      const editor = photoEditor(photo, fresh, [...fresh, ...owned.filter(id => !fresh.includes(id))]);
      const saveBtn = h('button', { class: 'btn pink small' }, img(ART.icon('camera')), 'Save photo');
      saveBtn.addEventListener('click', async () => {
        audio.fx('tap');
        const ok = await editor.save();
        if (ok) { saveBtn.textContent = 'Saved ✓'; }
      });
      col.append(editor.el, saveBtn);
    }
    this.forEachKid(p => {
      const card = this.unlockCard(p);
      if (card) {
        if (this.duo) card.prepend(h('div', { class: 'kid-name' }, this.nameOf(p)));
        col.append(card);
      }
    });
    col.append(h('div', { class: 'row' },
      h('button', { class: 'btn small blue', onclick: () => { audio.fx('tap'); showCollection(results[0].emoji?.id, this.players[0]); } }, img(ART.icon('book')), 'Collection'),
      h('button', { class: 'btn small blue', onclick: () => { audio.fx('tap'); showCalendar(this.players[0]); } }, img(ART.icon('calendar')), 'Calendar')),
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
    const hw = Math.min(W * (this.duo ? 0.3 : 0.38), 210);
    this.players.forEach((_, p) => {
      const x = this.duo ? (p ? 0.64 : 0.36) : 0.5;
      const hero = heroEl('sleep', this.look(p), 'sleeper');
      Object.assign(hero.style, { left: `${x * W}px`, top: `${0.88 * H}px`, width: `${hw}px`, animationDelay: `${-p * 1.3}s` });
      cast.append(hero, zzz(x, 0.88, hw, 5 + p));
    });
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
    this.show(h('div', { class: 'center-col' },
      h('div', { class: 'kids' }, this.players.map((_, p) => heroEl('swish', this.look(p), 'swish-buddy'))), count));
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
    this.forEachKid(() => store.addSwishStar());
    audio.fx('fanfare');
    audio.fx('sparkle');
    const home = h('button', { class: 'btn' }, img(ART.icon('home')), 'All done');
    this.show(h('div', { class: 'center-col reward' },
      h('p', { class: 'big-text' }, this.duo ? 'Gold stars!' : 'Gold star!'),
      h('div', { class: 'reveal' }, img(ART.icon('star'))),
      h('div', { class: 'row' },
        h('button', { class: 'btn small blue', onclick: () => { audio.fx('tap'); showCalendar(this.players[0]); } }, img(ART.icon('calendar')), 'Calendar')),
      home));
    await this.waitTap(home);
    $('#overlay').hidden = true;
  }
}
