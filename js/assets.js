// Paths to the generated art, plus the emoji catalogue and mouth-guide layout
// written by tools/gen_art.py.

const I = 'assets/img/';

export const ART = {
  icon: n => `${I}icons/${n}.svg`,
  goblin: n => `${I}goblins/${n}.svg`,
  buddy: pose => `${I}buddy/${pose}.svg`,
  world: (id, night = false) => `${I}worlds/${id}${night ? '_night' : ''}.svg`,
  home: `${I}worlds/home.svg`,
  emoji: id => `${I}emoji/${id}.svg`,
  emojiPng: id => `${I}emoji/${id}.png`,
  guide: n => `${I}guide/${n}.svg`,
};

export const SMALL_GOBLINS = ['a', 'b', 'c'];

export const ZONES = ['top_left', 'top_front', 'top_right', 'bottom_right', 'bottom_front', 'bottom_left'];
export const ZONE_LABELS = {
  top_left: 'Top teeth, left side', top_front: 'Top teeth, front', top_right: 'Top teeth, right side',
  bottom_right: 'Bottom teeth, right side', bottom_front: 'Bottom teeth, front', bottom_left: 'Bottom teeth, left side',
};
export const GAPS = ['gap_top_mid', 'gap_bottom_mid', 'gap_top_left', 'gap_top_right', 'gap_bottom_left', 'gap_bottom_right'];
export const GAP_LABELS = {
  gap_top_mid: 'Top front teeth, middle', gap_bottom_mid: 'Bottom front teeth, middle',
  gap_top_left: 'Top teeth, next gap left', gap_top_right: 'Top teeth, next gap right',
  gap_bottom_left: 'Bottom teeth, next gap left', gap_bottom_right: 'Bottom teeth, next gap right',
};

export let catalog = null;
export let layout = null;

export async function loadData() {
  [catalog, layout] = await Promise.all([
    fetch(`${I}emoji/catalog.json`).then(r => r.json()),
    fetch(`${I}guide/layout.json`).then(r => r.json()),
  ]);
}

export function allEmoji() {
  return catalog.worlds.flatMap(w => w.emoji.map(e => ({ ...e, world: w.id })));
}

export function worldName(id) {
  return catalog.worlds.find(w => w.id === id)?.name || id;
}

// Warm the browser cache so images appear instantly when a scene needs them.
export function preloadImages(urls) {
  for (const u of urls) { const i = new Image(); i.src = u; }
}
