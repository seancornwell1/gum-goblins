// Limited-time special editions. Each has a date window (by night, so a late
// Sunday bedtime still counts) and a parent override in settings:
// 'auto' follows the dates, 'on' forces it (e.g. to preview), 'off' hides it.

import { store, nightKey } from './store.js';

export const EVENTS = {
  halloween: { name: 'Halloween', start: '2026-10-30', end: '2026-11-01', dates: 'Oct 30 – Nov 1' },
};

export function inWindow(id, key = nightKey()) {
  const e = EVENTS[id];
  return key >= e.start && key <= e.end;
}

// The special edition running right now, or null.
export function activeEvent() {
  const mode = store.settings.halloween || 'auto';
  if (mode === 'off') return null;
  if (mode === 'on' || inWindow('halloween')) return 'halloween';
  return null;
}
