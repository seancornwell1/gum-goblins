// The nightly routines. The steps, their order and their sounds are the same
// every night; only the world (scenery and emoji set) changes.

import { $, h, img, toast } from './dom.js';
import { ART, ZONES, GAPS, SMALL_GOBLINS, catalog, preloadImages } from './assets.js';
import { store } from './store.js';
import { audio } from './audio.js';
import { keepAwake } from './wake.js';
import { Guide } from './guide.js';
import { photoCard } from './photo.js';
import { showCollection, showCalendar } from './books.js';

const BRUSH_STEPS = [['brush', 'Brush'], ['pick', 'Get your floss pick'], ['floss', 'Floss'], ['gift', 'Prize'], ['moon', 'Goodnight']];
const SWISH_STEPS = [['cup', 'Take a sip'], ['swish', 'Swish'], ['sink', 'Spit'], ['star_small', 'Gold star']];

// Where goblins gather around the mirror for each zone (degrees, 0 = right, 90 = down).
const ZONE_ANGLES = {
  top_left: [196, 222, 248], top_front: [242, 270, 298], top_right: [292, 318, 344],
  bottom_right: [16, 42, 68], bottom_front: [66, 90, 114], bottom_left: [112, 138, 164],
};
const GAP_ANGLES = {
  gap_top_mid: 256, gap_bottom_mid: 104, gap_top_left: 204, gap_top_right: 336, gap_bottom_left: 156, gap_bottom_right: 24,
};

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

  show(el) { this.screen.replaceChildren(el); return el; }

  mirrorGeometry() {
    const app = $('#app').getBoundingClientRect();
    const r = $('#mirror').getBoundingClientRect();
    // The mirror animates its scale in; use its final size.
    const size = Math.max(r.width, r.height) / (document.body.classList.contains('cam') ? 1 : 0.6);
    return { cx: r.left + r.width / 2 - app.left, cy: r.top + r.height / 2 - app.top, R: size / 2, W: app.width, H: app.height };
  }

  placeAround(el, deg, radiusFactor = 1.0, halfSize = 50) {
    const g = this.mirrorGeometry();
    const a = deg * Math.PI / 180;
    const x = Math.max(halfSize, Math.min(g.W - halfSize, g.cx + Math.cos(a) * g.R * radiusFactor));
    const y = Math.max(halfSize + 60, Math.min(g.H - halfSize, g.cy + Math.sin(a) * g.R * radiusFactor));
    el.style.left = `${x}px`;
    el.style.top = `${y}px`;
    return { x, y };
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
      if (!st.starting) {
        audio.fx('pause');
        clearTimeout(this.comeBackTimer);
        this.comeBackTimer = setTimeout(() => { if (this.paused && !this.aborted) audio.say('come_back'); }, 1200);
      }
      this.pausedStarting = !!st.starting;
    } else if (should && this.paused && this.pausedStarting && !st.starting) {
      // Camera is ready but he isn't in frame yet.
      this.pausedStarting = false;
      $('#pause .pause-text').textContent = 'Come back to the mirror!';
    } else if (!should && this.paused) {
      this.paused = false;
      this.applyFreeze();
      clearTimeout(this.comeBackTimer);
      $('#pause').hidden = true;
      audio.duck(1);
      if (!this.pausedStarting) { audio.fx('resume'); audio.say('there_you_are'); }
      this.pausedStarting = false;
    }
  }

  clearPause() {
    this.paused = false;
    clearTimeout(this.comeBackTimer);
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
    try {
      if (kind === 'swish') await this.swishRoutine();
      else await this.brushRoutine();
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
    audio.stopVoice();
    audio.stopMusic(1.2);
    this.clearPause();
    document.body.classList.remove('cam');
    this.strip.replaceChildren();
    this.stage.replaceChildren();
    this.onExit?.();
  }

  // ------------------------------------------------------------ brush & floss

  async brushRoutine() {
    const s = store.settings;
    const worlds = catalog.worlds.map(w => w.id);
    const world = store.worldForTonight(worlds);
    this.world = world;
    preloadImages([ART.world(world), ART.world(world, true), ...SMALL_GOBLINS.map(ART.goblin), ART.goblin('big'),
      ART.goblin('big_hurt'), ART.goblin('big_dizzy'), ART.goblin('sneaky'), ART.buddy('cheer'), ART.buddy('sleep')]);

    if (s.camera) this.tracker.start();
    else this.tracker.stop();
    document.body.classList.add('cam');
    const result = await this.brushing(world);
    await this.flossPause();
    await this.flossing();
    await this.reward(result);
    await this.goodnight(world);
  }

  async brushing(world) {
    const s = store.settings;
    this.setStrip(BRUSH_STEPS, 0);
    this.setBg(ART.world(world));
    this.stage.replaceChildren();
    audio.playMusic('music_adventure');
    const zoneDur = (s.brushMinutes * 60) / ZONES.length;
    const guide = new Guide('brush', ZONES.length);
    const buddy = img(ART.buddy('ready'), 'buddy');
    this.show(h('div', {}, guide.el, buddy));
    guide.show(ZONES[0], 0);

    await audio.say('lets_brush');
    this.check();
    await audio.say('world_' + world);
    this.check();

    if (this.tracker.status().noCamera && s.camera) toast('Camera not available — timers run on their own.');

    let clock = 0, moving = 0, skipping = false, photo = null;
    for (let i = 0; i < ZONES.length; i++) {
      const z = ZONES[i];
      const final = i === ZONES.length - 1;
      guide.show(z, i);
      let goblins = [], big = null;
      if (!final) {
        goblins = this.spawnGoblins(z, i);
        if (!skipping) audio.say('zone_' + z);
      } else {
        audio.playMusic('music_boss', 1);
        big = this.spawnBig();
        if (!skipping) {
          audio.say('zone_' + z).then(() => !this.aborted && audio.say(store.bigEscaped ? 'big_back' : 'big_goblin'));
        }
      }
      let lastHit = 0;
      const res = skipping ? { clock: zoneDur, moving: zoneDur, skipped: true } : await this.track(zoneDur, (p, st) => {
        guide.setProgress(p);
        guide.setActive(st.active, st.now);
        if (!final) {
          goblins.forEach((g, k) => { if (!g.popped && p >= ((k + 1) / goblins.length) * 0.9) this.popGoblin(g); });
        } else {
          big.hp.style.transform = `scaleX(${1 - p})`;
          if (p - lastHit >= 0.12 && p < 0.98) { lastHit = p; this.hitBig(big); }
          if (!photo && p > 0.35 && st.faceNow) {
            photo = this.tracker.snapshot();
            if (photo) { const f = $('#flash'); f.classList.remove('go'); void f.offsetWidth; f.classList.add('go'); }
          }
        }
      });
      if (res.skipped) skipping = true;
      clock += res.clock;
      moving += res.moving;
      goblins.forEach(g => { if (!g.popped) this.popGoblin(g); });
      if (!final) audio.fx('chime');
      else this.lastBig = big;
    }
    guide.finish();
    guide.setActive(true);

    const score = skipping ? 1 : clock > 0 ? moving / clock : 1;
    const passed = skipping || score >= s.passMark;
    const big = this.lastBig;
    big.hp.parentElement.remove();
    if (passed) {
      audio.stopMusic(0.8);
      big.body.querySelector('img').src = ART.goblin('big_dizzy');
      big.el.classList.add('beaten');
      audio.fx('defeat');
      buddy.src = ART.buddy('cheer');
      buddy.classList.add('cheer');
      await this.sleep(1500);
      const b = h('div', { class: 'burst', style: { left: '50%', top: big.el.style.top || '60%', width: '60vw', position: 'absolute' } });
      this.stage.append(b);
      audio.fx('pop');
      await audio.say('big_beaten');
      this.check();
      store.bigEscaped = false;
    } else {
      audio.stopMusic(2);
      big.el.classList.add('escape');
      big.el.append(h('div', { class: 'bubble' }, 'I\'ll be back tomorrow!'));
      audio.fx('whoosh');
      audio.fx('giggle');
      await audio.say('big_escaped');
      this.check();
      await this.sleep(2500);
      store.bigEscaped = true;
    }
    this.stage.replaceChildren();
    return { passed, score, photo, world };
  }

  spawnGoblins(zone, zoneIndex) {
    const angles = ZONE_ANGLES[zone];
    return angles.map((deg, k) => {
      const type = SMALL_GOBLINS[(zoneIndex + k) % SMALL_GOBLINS.length];
      const el = h('div', { class: 'sprite goblin enter', style: { animationDelay: `${k * 0.25}s` } }, img(ART.goblin(type)));
      el.querySelector('img').style.animationDelay = `${-k * 0.4}s`;
      this.stage.append(el);
      this.placeAround(el, deg, 1.0, el.offsetWidth / 2 || 50);
      return { el, popped: false };
    });
  }

  popGoblin(g) {
    g.popped = true;
    g.el.classList.add('pop');
    audio.fx('pop', { rate: 0.9 + Math.random() * 0.3 });
    setTimeout(() => g.el.remove(), 600);
  }

  spawnBig() {
    const hp = h('i');
    const body = h('div', { class: 'body' }, img(ART.goblin('big')), img(ART.goblin('big_hurt')));
    const el = h('div', { class: 'big enter' }, h('div', { class: 'bar hp' }, hp), body);
    const g = this.mirrorGeometry();
    el.style.top = `${g.cy + g.R * 0.55}px`;
    if (store.bigEscaped) {
      const bubble = h('div', { class: 'bubble' }, 'I\'m back!');
      el.append(bubble);
      setTimeout(() => bubble.remove(), 3500);
    }
    this.stage.append(el);
    audio.fx('giggle', { rate: 0.7 });
    return { el, body, hp };
  }

  hitBig(big) {
    audio.fx('hit', { gain: 0.8 });
    big.el.classList.remove('flinch');
    void big.el.offsetWidth;
    big.el.classList.add('flinch', 'hurt');
    setTimeout(() => big.el.classList.remove('hurt'), 450);
  }

  async flossPause() {
    this.setStrip(BRUSH_STEPS, 1);
    audio.playMusic('music_calm', 2);
    audio.duck(0.6);
    const btn = h('button', { class: 'btn blue' }, img(ART.icon('pick')), 'I\'m ready!');
    this.show(h('div', { class: 'center-col calm' },
      img(ART.icon('pick'), 'hero-img'),
      h('p', { class: 'big-text' }, 'Get your floss pick'),
      btn));
    audio.say('get_floss');
    await this.waitTap(btn);
    audio.duck(1);
  }

  async flossing() {
    const s = store.settings;
    this.setStrip(BRUSH_STEPS, 2);
    const gaps = GAPS.slice(0, s.flossGaps);
    const guide = new Guide('floss', gaps.length);
    this.show(h('div', {}, guide.el, img(ART.buddy('ready'), 'buddy')));
    guide.show(gaps[0], 0);
    await audio.say('lets_floss');
    this.check();
    let skipping = false;
    for (let i = 0; i < gaps.length; i++) {
      const gap = gaps[i];
      guide.show(gap, i);
      const deg = GAP_ANGLES[gap];
      const el = h('div', { class: 'sprite sneaky goblin enter' }, img(ART.goblin('sneaky')));
      this.stage.append(el);
      const { x } = this.placeAround(el, deg, 0.92, 45);
      if (!skipping) audio.say(gap);
      const res = skipping ? { skipped: true } : await this.track(s.flossSeconds, (p, st) => {
        guide.setProgress(p);
        guide.setActive(st.active, st.now);
      });
      if (res.skipped) skipping = true;
      el.classList.remove('enter');
      el.classList.add('run', x > this.mirrorGeometry().cx ? 'right' : 'left');
      audio.fx('whoosh', { gain: 0.6 });
      audio.fx('giggle');
      audio.fx('chime');
      setTimeout(() => el.remove(), 1500);
      if (!skipping) await this.sleep(700);
    }
    guide.finish();
    await audio.say('floss_done');
    this.check();
    this.stage.replaceChildren();
  }

  async reward({ passed, photo, world }) {
    this.setStrip(BRUSH_STEPS, 3);
    audio.stopMusic(1);
    document.body.classList.remove('cam');
    let emoji = null;
    if (passed) {
      const missing = (w) => catalog.worlds.find(x => x.id === w).emoji.filter(e => !store.collection[e.id]);
      let pool = missing(world);
      if (!pool.length) pool = catalog.worlds.flatMap(w => missing(w.id));
      emoji = pool.length ? pool[Math.floor(Math.random() * pool.length)] : null;
      if (emoji) store.addEmoji(emoji.id);
    }
    store.completeNight({ passed, emoji: emoji?.id || null, world });

    const goodnightBtn = h('button', { class: 'btn' }, img(ART.icon('moon')), 'Goodnight');
    const col = h('div', { class: 'center-col reward' });
    this.show(col);
    if (passed) {
      audio.fx('fanfare');
      audio.fx('sparkle');
      if (emoji) {
        col.append(h('p', { class: 'big-text' }, 'New emoji!'),
          h('div', { class: 'reveal' }, img(ART.emoji(emoji.id))),
          h('div', { class: 'emoji-name' }, emoji.name));
        await audio.say('new_emoji');
      } else {
        col.append(h('p', { class: 'big-text' }, 'You found them all!'), h('div', { class: 'reveal' }, img(ART.icon('star'))));
        await audio.say('all_found');
      }
      this.check();
      if (photo && emoji) {
        const card = photoCard(photo, emoji.id);
        const saveBtn = h('button', { class: 'btn pink small' }, img(ART.icon('camera')), 'Save photo');
        saveBtn.addEventListener('click', async () => {
          audio.fx('tap');
          const ok = await card.save();
          if (ok) { saveBtn.textContent = 'Saved ✓'; saveBtn.disabled = true; }
        });
        col.append(card.el, saveBtn);
        audio.say('photo');
      }
    } else {
      col.append(h('p', { class: 'big-text' }, 'No emoji tonight'),
        h('div', { class: 'reveal' }, img(ART.goblin('big'))),
        h('div', { class: 'emoji-name' }, 'Beat the big goblin tomorrow!'));
      await audio.say('no_emoji');
      this.check();
    }
    col.append(h('div', { class: 'row' },
      h('button', { class: 'btn small blue', onclick: () => { audio.fx('tap'); showCollection(emoji?.id); } }, img(ART.icon('book')), 'Collection'),
      h('button', { class: 'btn small blue', onclick: () => { audio.fx('tap'); showCalendar(); } }, img(ART.icon('calendar')), 'Calendar')),
    goodnightBtn);
    await this.waitTap(goodnightBtn);
    $('#overlay').hidden = true;
  }

  async goodnight(world) {
    this.setStrip(BRUSH_STEPS, 4);
    this.tracker.stop();
    keepAwake(false);
    this.setBg(ART.world(world, true));
    audio.playMusic('music_lullaby', 3);
    const g = this.mirrorGeometry();
    const W = g.W, H = g.H;
    const sleepers = [
      [ART.buddy('sleep'), 0.5, 0.86, Math.min(W * 0.36, 200)],
      [ART.goblin('big_sleep'), 0.2, 0.7, Math.min(W * 0.34, 190)],
      [ART.goblin('a_sleep'), 0.82, 0.68, Math.min(W * 0.22, 120)],
      [ART.goblin('b_sleep'), 0.14, 0.94, Math.min(W * 0.2, 110)],
      [ART.goblin('c_sleep'), 0.86, 0.94, Math.min(W * 0.2, 110)],
      [ART.goblin('sneaky_sleep'), 0.66, 0.78, Math.min(W * 0.15, 80)],
    ];
    const cast = h('div', { class: 'night-cast' });
    sleepers.forEach(([src, x, y, w], i) => {
      const s = img(src, 'sleeper');
      Object.assign(s.style, { left: `${x * W}px`, top: `${y * H}px`, width: `${w}px`, animationDelay: `${-i * 0.7}s` });
      const z = img(ART.icon('zzz'), 'zzz');
      Object.assign(z.style, { left: `${x * W + w * 0.2}px`, top: `${y * H - w * 1.1}px`, animationDelay: `${i * 0.6}s` });
      cast.append(s, z);
    });
    this.stage.replaceChildren(cast);
    const done = h('button', { class: 'btn small', style: { opacity: 0, transition: 'opacity 1s' } }, 'Done');
    this.show(h('div', {},
      h('div', { class: 'goodnight-text' }, h('p', { class: 'big-text' }, 'Goodnight!'),
        h('div', { style: { marginTop: '24px' } }, done))));
    await this.sleep(1500);
    await audio.say('goodnight');
    this.check();
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
    audio.say('take_sip');
    await this.waitTap(ready);

    this.setStrip(SWISH_STEPS, 1);
    const secs = store.settings.swishSeconds;
    const count = h('div', { class: 'count' }, secs);
    this.show(h('div', { class: 'center-col' }, img(ART.buddy('swish'), 'swish-buddy'), count));
    const wave = h('div', { class: 'wave' }, img(ART.icon('wave')));
    const H = this.mirrorGeometry().H;
    const goblins = [0.18, 0.5, 0.82].map((x, i) => {
      const el = h('div', { class: 'sprite goblin' }, img(ART.goblin(SMALL_GOBLINS[i])));
      Object.assign(el.style, { left: `${x * 100}%`, top: `${H * 0.86}px` });
      this.stage.append(el);
      return { el, x, gone: false };
    });
    this.stage.append(wave);
    audio.say('swish');
    audio.fx('wave');
    await new Promise(resolve => {
      const start = performance.now();
      let lastSay = start, lastWave = start, pausedFor = 0, lastNow = start;
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
        if (now - lastSay > 7000 && secs - t > 4) { lastSay = now; audio.say('swish'); }
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
    await audio.say('spit');
    this.check();
    await this.sleep(1200);
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
    const tapped = this.waitTap(home);
    audio.say('swish_done');
    await tapped;
    $('#overlay').hidden = true;
  }
}
