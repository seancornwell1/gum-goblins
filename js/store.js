// Everything is kept in this phone's localStorage. Nothing is ever uploaded.

const KEY = 'gumgoblins.v1';

export const DEFAULT_SETTINGS = {
  brushMinutes: 2,
  passMark: 0.3,
  flossGaps: 10,
  flossSeconds: 3,
  swishEnabled: false,
  swishSeconds: 20,
  volMusic: 0.5,
  volFx: 0.7,
  camera: true,
  sensitivity: 'medium',
};

function blank() {
  return {
    settings: { ...DEFAULT_SETTINGS },
    collection: {},   // emoji id -> night it was earned
    nights: {},       // night -> { passed, emoji, world }
    swish: {},        // night -> true (gold star)
    mornings: {},     // night -> true (sun sticker)
    hero: { cape: 'blue', hat: 'none', brush: 'pink' },
    bigEscaped: false,
    worldByNight: {},
    seenUnlocks: null, // hero items already announced
  };
}

let data = load();

function load() {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) {
      const d = { ...blank(), ...JSON.parse(raw) };
      d.settings = { ...DEFAULT_SETTINGS, ...d.settings };
      // Older saves: floss defaults changed to more, quicker gaps.
      if (d.settings.flossGaps < 6) { d.settings.flossGaps = DEFAULT_SETTINGS.flossGaps; d.settings.flossSeconds = DEFAULT_SETTINGS.flossSeconds; }
      return d;
    }
  } catch (e) { /* private mode or corrupted: start fresh */ }
  return blank();
}

function save() {
  try { localStorage.setItem(KEY, JSON.stringify(data)); } catch (e) { /* storage full or blocked */ }
}

// Ask the browser not to evict our data when storage is low.
navigator.storage?.persist?.().catch(() => {});

// A "night" runs from 4am to 4am, so a late bedtime still counts for that evening.
export function nightKey(date = new Date()) {
  const d = new Date(date.getTime() - 4 * 3600 * 1000);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

export const store = {
  get settings() { return data.settings; },
  setSetting(k, v) { data.settings[k] = v; save(); },
  get collection() { return data.collection; },
  get nights() { return data.nights; },
  get swish() { return data.swish; },
  get mornings() { return data.mornings; },
  get hero() { return data.hero; },
  setHero(part, value) { data.hero = { ...data.hero, [part]: value }; save(); },
  get seenUnlocks() { return data.seenUnlocks; },
  set seenUnlocks(v) { data.seenUnlocks = v; save(); },
  get bigEscaped() { return data.bigEscaped; },
  set bigEscaped(v) { data.bigEscaped = v; save(); },

  worldForTonight(worldIds) {
    const k = nightKey();
    if (!data.worldByNight[k] || !worldIds.includes(data.worldByNight[k])) {
      data.worldByNight = { [k]: worldIds[Math.floor(Math.random() * worldIds.length)] };
      save();
    }
    return data.worldByNight[k];
  },

  addEmoji(id) { data.collection[id] = nightKey(); save(); },
  completeNight(info) { data.nights[nightKey()] = { ...(data.nights[nightKey()] || {}), ...info, done: true }; save(); },
  addSwishStar() { data.swish[nightKey()] = true; save(); },
  // Mornings count by calendar date (no 4am shift).
  addMorningSun() { data.mornings[nightKey(new Date(Date.now() + 4 * 3600 * 1000))] = true; save(); },

  resetProgress() {
    const { settings, hero, seenUnlocks } = data;
    data = blank();
    Object.assign(data, { settings, hero, seenUnlocks });
    save();
  },
};
