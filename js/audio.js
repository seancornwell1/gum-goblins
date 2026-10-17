// Plays the generated music and effects through Web Audio, with
// separate volume controls. Works with the iPhone ringer switch on silent:
// the audio session is set to "playback" (Safari 16.4+), and on older iOS a
// silent looping <audio> element forces the same media playback category.

const MUSIC = ['music_adventure', 'music_boss', 'music_calm', 'music_lullaby'];
const FX = ['zap', 'pop', 'chime', 'fanfare', 'sparkle', 'whoosh', 'wave', 'tap', 'hit', 'giggle', 'resume', 'pause', 'defeat'];
// Per-track trims so every piece sits at a calm level next to the others.
const MUSIC_TRIM = { music_adventure: 0.8, music_boss: 0.95, music_calm: 0.75, music_lullaby: 0.6 };

class AudioEngine {
  constructor() {
    this.ctx = null;
    this.buffers = new Map();
    this.loading = null;
    this.music = null;       // { name, src, gain }
    this.duckLevel = 1;
    this.loopStart = 1;
    this.loops = {};
  }

  // Must be called from inside a tap handler the first time.
  unlock() {
    if (this.ctx) {
      if (this.ctx.state !== 'running') this.ctx.resume().catch(() => {});
      return this.loading;
    }
    try { if (navigator.audioSession) navigator.audioSession.type = 'playback'; } catch (e) { /* not supported */ }
    if (!navigator.audioSession) {
      const el = document.getElementById('unmute');
      el.play().catch(() => {});
    }
    const AC = window.AudioContext || window.webkitAudioContext;
    this.ctx = new AC();
    // Play one silent sample synchronously inside the gesture (old iOS needs this).
    const b = this.ctx.createBuffer(1, 1, 22050);
    const s = this.ctx.createBufferSource();
    s.buffer = b; s.connect(this.ctx.destination); s.start(0);
    this.ctx.resume().catch(() => {});

    this.master = this.ctx.createGain();
    this.master.connect(this.ctx.destination);
    this.musicBus = this.ctx.createGain();
    this.duckBus = this.ctx.createGain();
    this.musicBus.connect(this.duckBus).connect(this.master);
    this.fxBus = this.ctx.createGain();
    this.fxBus.connect(this.master);
    this.applyVolumes(this.vols || { music: .5, fx: .7 });

    document.addEventListener('visibilitychange', () => {
      if (!document.hidden && this.ctx.state !== 'running') this.ctx.resume().catch(() => {});
    });
    this.loading = this.loadAll().catch(e => { console.warn(e); this.loaded = true; });
    return this.loading;
  }

  async loadAll() {
    const meta = await fetch('assets/audio/music.json').then(r => r.json());
    this.loopStart = meta.loopStart;
    for (const [k, v] of Object.entries(meta.music)) this.loops[k] = v.loop;
    const jobs = [
      ...MUSIC.map(n => [n, `assets/audio/${n}.mp3`]),
      ...FX.map(n => ['fx_' + n, `assets/audio/fx_${n}.mp3`]),
    ];
    // Effects first so taps and pops work straight away.
    jobs.sort((a, b) => (a[0].startsWith('music') ? 1 : 0) - (b[0].startsWith('music') ? 1 : 0));
    await Promise.all(jobs.map(([k, url]) => this.load(k, url)));
    this.loaded = true;
  }

  async load(key, url) {
    try {
      const buf = await fetch(url).then(r => r.arrayBuffer());
      const audio = await new Promise((res, rej) => this.ctx.decodeAudioData(buf, res, rej));
      this.buffers.set(key, audio);
    } catch (e) {
      console.warn('audio load failed', url, e);
    }
  }

  applyVolumes({ music, fx }) {
    this.vols = { music, fx };
    if (!this.ctx) return;
    const t = this.ctx.currentTime;
    this.musicBus.gain.setTargetAtTime(music, t, 0.1);
    this.fxBus.gain.setTargetAtTime(fx, t, 0.1);
  }

  playMusic(name, fade = 1.5) {
    if (!this.ctx) return;
    if (this.music?.name === name) return;
    this.stopMusic(fade);
    const buf = this.buffers.get(name);
    if (!buf) {
      // Not decoded yet: try again shortly.
      this.pendingMusic = name;
      this.loading?.then(() => { if (this.pendingMusic === name) { this.pendingMusic = null; this.playMusic(name, fade); } });
      return;
    }
    this.pendingMusic = null;
    const src = this.ctx.createBufferSource();
    src.buffer = buf;
    src.loop = true;
    src.loopStart = this.loopStart;
    src.loopEnd = this.loopStart + (this.loops[name] || buf.duration - this.loopStart);
    const g = this.ctx.createGain();
    const t = this.ctx.currentTime;
    g.gain.setValueAtTime(0, t);
    g.gain.linearRampToValueAtTime(MUSIC_TRIM[name] ?? 0.8, t + fade);
    src.connect(g).connect(this.musicBus);
    src.start(t, 0.05);
    this.music = { name, src, gain: g };
  }

  stopMusic(fade = 1.5) {
    this.pendingMusic = null;
    if (!this.music) return;
    const { src, gain } = this.music;
    const t = this.ctx.currentTime;
    gain.gain.cancelScheduledValues(t);
    gain.gain.setValueAtTime(gain.gain.value, t);
    gain.gain.linearRampToValueAtTime(0, t + fade);
    try { src.stop(t + fade + 0.05); } catch (e) { /* already stopped */ }
    this.music = null;
  }

  // Softly lowers the music (while paused).
  duck(level, time = 0.6) {
    if (!this.ctx) return;
    this.duckLevel = level;
    this.duckBus.gain.setTargetAtTime(level, this.ctx.currentTime, time / 3);
  }

  fx(name, { rate = 1, gain = 1 } = {}) {
    const buf = this.buffers.get('fx_' + name);
    if (!buf || !this.ctx) return;
    const src = this.ctx.createBufferSource();
    src.buffer = buf;
    src.playbackRate.value = rate;
    const g = this.ctx.createGain();
    g.gain.value = gain;
    src.connect(g).connect(this.fxBus);
    src.start();
    return src;
  }
}

export const audio = new AudioEngine();
