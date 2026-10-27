// Paths to the generated art, plus the emoji catalogue, mouth-guide layout and
// hero parts written by tools/gen_art.py.

import { activeEvent } from './events.js';

const I = 'assets/img/';

export const ART = {
  icon: n => `${I}icons/${n}.svg`,
  // During Halloween the goblins wear costumes (a.svg -> a_hw.svg, big_hurt.svg -> big_hw_hurt.svg).
  goblin: n => `${I}goblins/${activeEvent() === 'halloween' ? n.replace(/^(big|sneaky|a|b|c)(?=_|$)/, '$1_hw') : n}.svg`,
  hero: n => `${I}hero/${n}.svg`,
  world: (id, night = false) => `${I}worlds/${id}${night ? '_night' : ''}.svg`,
  home: () => `${I}worlds/home${activeEvent() === 'halloween' ? '_halloween' : ''}.svg`,
  emoji: id => `${I}emoji/${id}.svg`,
  guide: n => `${I}guide/${n}.svg`,
};

export const SMALL_GOBLINS = ['a', 'b', 'c'];

export const ZONES = ['top_left', 'top_front', 'top_right', 'bottom_right', 'bottom_front', 'bottom_left'];
export const ZONE_LABELS = {
  top_left: 'Top teeth, left side', top_front: 'Top teeth, front', top_right: 'Top teeth, right side',
  bottom_right: 'Bottom teeth, right side', bottom_front: 'Bottom teeth, front', bottom_left: 'Bottom teeth, left side',
};

export let catalog = null;
export let layout = null;
export let heroParts = null;
export let GAPS = [];

export async function loadData() {
  [catalog, layout, heroParts] = await Promise.all([
    fetch(`${I}emoji/catalog.json`).then(r => r.json()),
    fetch(`${I}guide/layout.json`).then(r => r.json()),
    fetch(`${I}hero/parts.json`).then(r => r.json()),
  ]);
  GAPS = layout.gapOrder;
}

// Every collectible: each base emoji plus its rare sparkly (gold) version.
export function allEmoji() {
  return catalog.worlds.flatMap(w => w.emoji.flatMap(e => [
    { id: e.id, name: e.name, world: w.id, gold: false },
    { id: `${e.id}_gold`, name: `Sparkly ${e.name}`, world: w.id, gold: true, base: e.id },
  ]));
}

export function emojiInfo(id) {
  return allEmoji().find(e => e.id === id);
}

// Worlds that can come up on an ordinary night (not limited-time event worlds).
export function everydayWorlds() {
  return catalog.worlds.filter(w => !w.event).map(w => w.id);
}

export function worldName(id) {
  return catalog.worlds.find(w => w.id === id)?.name || id;
}

// Warm the browser cache so images appear instantly when a scene needs them.
export function preloadImages(urls) {
  for (const u of urls) { const i = new Image(); i.src = u; }
}
