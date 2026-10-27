// Hero dress-up items are earned: a few to start, one more for each morning
// brush, and the rest from achievements. Everything is worked out from the
// saved progress, so nothing extra needs storing except which items were
// already announced.

import { store } from './store.js';
import { allEmoji } from './assets.js';
import { EVENTS, inWindow } from './events.js';

const FREE = ['cape:blue', 'cape:red', 'hat:none', 'hat:cap', 'brush:pink'];
// The n-th morning brush unlocks the n-th item.
const MORNING = ['brush:blue', 'cape:green', 'hat:bunny', 'brush:green', 'cape:pink', 'brush:purple'];
const ACHIEVEMENTS = [
  { item: 'hat:crown', label: 'Beat the big goblin', done: s => s.wins >= 1 },
  { item: 'cape:purple', label: 'Brush 5 nights', done: s => s.nights >= 5 },
  { item: 'hat:headband', label: 'Brush 3 nights in a row', done: s => s.streak >= 3 },
  { item: 'hat:wizard', label: 'Find 10 emoji', done: s => s.emoji >= 10 },
  { item: 'brush:yellow', label: 'Find a sparkly emoji', done: s => s.sparkly >= 1 },
  { item: 'hat:pirate', label: 'Find 25 emoji', done: s => s.emoji >= 25 },
  { item: 'cape:orange', label: 'Brush 7 nights in a row', done: s => s.streak >= 7 },
];

// Limited-time items: earned by brushing (night or morning) during the event, kept forever.
const EVENT_ITEMS = [
  { item: 'cape:bat', event: 'halloween' },
  { item: 'hat:pumpkin', event: 'halloween' },
];

export function isEventItem(part, value) {
  return EVENT_ITEMS.some(e => e.item === `${part}:${value}`);
}

function stats() {
  const nights = Object.entries(store.nights).filter(([, n]) => n.done).map(([k]) => k).sort();
  let streak = 0, run = 0, prev = null;
  for (const k of nights) {
    const d = new Date(k + 'T12:00:00');
    run = prev && Math.round((d - prev) / 86400000) === 1 ? run + 1 : 1;
    streak = Math.max(streak, run);
    prev = d;
  }
  const owned = Object.keys(store.collection);
  const gold = new Set(allEmoji().filter(e => e.gold).map(e => e.id));
  return {
    nights: nights.length,
    wins: Object.values(store.nights).filter(n => n.passed).length,
    streak,
    emoji: owned.length,
    sparkly: owned.filter(id => gold.has(id)).length,
    mornings: Object.keys(store.mornings).length,
    // Events brushed in: any night or morning inside the event's dates.
    events: new Set(Object.keys(EVENTS).filter(id => [...nights, ...Object.keys(store.mornings)].some(k => inWindow(id, k)))),
  };
}

export function unlocked() {
  const s = stats();
  return new Set([...FREE, ...MORNING.slice(0, s.mornings), ...ACHIEVEMENTS.filter(a => a.done(s)).map(a => a.item),
    ...EVENT_ITEMS.filter(e => s.events.has(e.event)).map(e => e.item)]);
}

export function isUnlocked(part, value, set = unlocked()) {
  return set.has(`${part}:${value}`) || store.hero[part] === value;
}

// What he needs to do to earn an item.
export function lockHint(part, value) {
  const item = `${part}:${value}`;
  const a = ACHIEVEMENTS.find(x => x.item === item);
  if (a) return a.label;
  const ev = EVENT_ITEMS.find(x => x.item === item);
  if (ev) return `Brush on ${EVENTS[ev.event].name} weekend`;
  const n = MORNING.indexOf(item) + 1 - stats().mornings;
  return n === 1 ? 'Do one more morning brush' : `Do ${n} more morning brushes`;
}

// Items earned since last time, announced once.
export function takeNewUnlocks() {
  const now = unlocked();
  if (store.seenUnlocks === null) { store.seenUnlocks = [...now]; return []; }
  const seen = new Set(store.seenUnlocks);
  const fresh = [...now].filter(i => !seen.has(i));
  if (fresh.length) store.seenUnlocks = [...now];
  return fresh.map(i => { const [part, value] = i.split(':'); return { part, value }; });
}
