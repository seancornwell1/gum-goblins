// The player's tooth hero, stacked from generated layers (cape, body, hat,
// brush) so he can dress it up. Code only stacks and animates the images.

import { h, img } from './dom.js';
import { ART, heroParts } from './assets.js';
import { store } from './store.js';

export function heroEl(pose = 'ready', look = store.hero, cls = '') {
  const el = h('div', { class: `hero ${cls}` });
  setPose(el, pose, look);
  return el;
}

export function setPose(el, pose, look = store.hero) {
  const layers = [ART.hero(`cape_${look.cape}`), ART.hero(`body_${pose}`)];
  if (look.hat !== 'none' && pose !== 'sleep') layers.push(ART.hero(`hat_${look.hat}`));
  if (heroParts.brushPoses.includes(pose)) layers.push(ART.hero(`brush_${look.brush}_${pose}`));
  el.replaceChildren(...layers.map(src => img(src)));
  el.dataset.pose = pose;
}
