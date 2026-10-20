// Everything is kept in this phone's localStorage. Nothing is ever uploaded.
//
// Settings and tonight's world are shared. Each kid has a profile with their
// own hero, emoji collection, calendar and unlocks. Most of the game reads and
// writes the active profile; store.use(i) switches it.

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
  secondPlayer: true,
};

const KID_FIELDS = ['collection', 'nights', 'swish', 'mornings', 'hero', 'bigEscaped', 'seenUnlocks'];

function blankKid(name, cape) {
  return {
    name,
    collection: {},   // emoji id -> night it was earned
    nights: {},       // night -> { passed, emoji, world }
    swish: {},        // night -> true (gold star)
    mornings: {},     // day -> true (sun sticker)
    hero: { cape, hat: 'none', brush: 'pink' },
    bigEscaped: false,
    seenUnlocks: null, // hero items already announced
  };
}

function blank() {
  return {
    settings: { ...DEFAULT_SETTINGS },
    worldByNight: {},
    profiles: [blankKid('Oliver', 'blue'), blankKid('Juniper', 'red')],
  };
}

let data = load();
let active = 0;

function load() {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) {
      const d = { ...blank(), ...JSON.parse(raw) };
      d.settings = { ...DEFAULT_SETTINGS, ...d.settings };
      // Older saves: floss defaults changed to more, quicker gaps.
      if (d.settings.flossGaps < 6) { d.settings.flossGaps = DEFAULT_SETTINGS.flossGaps; d.settings.flossSeconds = DEFAULT_SETTINGS.flossSeconds; }
      // Older saves kept one kid's progress at the top level: it becomes Oliver's profile.
      if (!JSON.parse(raw).profiles) {
        const kid = blankKid('Oliver', 'blue');
        for (const f of KID_FIELDS) if (d[f] !== undefined) { kid[f] = d[f]; delete d[f]; }
        d.profiles = [kid, blankKid('Juniper', 'red')];
      }
      if (d.profiles[1].name === 'Player 2') d.profiles[1].name = 'Juniper';
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

const kid = () => data.profiles[active];

export const store = {
  get settings() { return data.settings; },
  setSetting(k, v) { data.settings[k] = v; save(); },

  // ---- profiles
  get active() { return active; },
  use(i) { active = i; },
  // Profiles that can play: just Oliver, or both when the second player is on.
  get players() { return data.settings.secondPlayer ? [0, 1] : [0]; },
  profile(i) { return data.profiles[i]; },
  setName(i, name) { data.profiles[i].name = name.trim() || data.profiles[i].name; save(); },

  // ---- the active kid
  get name() { return kid().name; },
  get collection() { return kid().collection; },
  get nights() { return kid().nights; },
  get swish() { return kid().swish; },
  get mornings() { return kid().mornings; },
  get hero() { return kid().hero; },
  setHero(part, value) { kid().hero = { ...kid().hero, [part]: value }; save(); },
  get seenUnlocks() { return kid().seenUnlocks; },
  set seenUnlocks(v) { kid().seenUnlocks = v; save(); },
  get bigEscaped() { return kid().bigEscaped; },
  set bigEscaped(v) { kid().bigEscaped = v; save(); },

  worldForTonight(worldIds) {
    const k = nightKey();
    if (!data.worldByNight[k] || !worldIds.includes(data.worldByNight[k])) {
      data.worldByNight = { [k]: worldIds[Math.floor(Math.random() * worldIds.length)] };
      save();
    }
    return data.worldByNight[k];
  },

  addEmoji(id) { kid().collection[id] = nightKey(); save(); },
  completeNight(info) { kid().nights[nightKey()] = { ...(kid().nights[nightKey()] || {}), ...info, done: true }; save(); },
  addSwishStar() { kid().swish[nightKey()] = true; save(); },
  // Mornings count by calendar date (no 4am shift).
  addMorningSun() { kid().mornings[nightKey(new Date(Date.now() + 4 * 3600 * 1000))] = true; save(); },

  // Clears every kid's collection and calendar; keeps names, heroes and settings.
  resetProgress() {
    data.profiles = data.profiles.map((p, i) => {
      const fresh = blankKid(p.name, i ? 'red' : 'blue');
      return { ...fresh, hero: p.hero, seenUnlocks: p.seenUnlocks };
    });
    save();
  },
};
