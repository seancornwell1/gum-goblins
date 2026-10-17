// The on-screen guide: a cartoon mouth with one zone (or floss gap) lit, a
// little tool showing where to work, a label and a fill bar for time left.

import { h, img } from './dom.js';
import { ART, layout, ZONE_LABELS, GAP_LABELS } from './assets.js';

export class Guide {
  constructor(kind, total) {
    this.kind = kind;
    this.hl = img('', 'hl');
    this.tool = img(ART.icon(kind === 'brush' ? 'brush' : 'pick'), `tool ${kind === 'brush' ? 'brush' : 'pick'}`);
    this.label = h('div', { class: 'label' });
    this.fill = h('i');
    this.hint = h('div', { class: 'hint' }, kind === 'brush' ? 'Brush to beat them!' : 'Floss here!');
    this.dots = h('div', { class: 'dots' }, Array.from({ length: total }, () => h('b')));
    this.el = h('div', { class: 'guide card idle' },
      this.hint,
      h('div', { class: 'mouth' }, img(ART.guide('mouth')), this.hl, this.tool),
      this.label,
      h('div', { class: `bar ${kind === 'floss' ? 'floss' : ''}` }, this.fill),
      this.dots);
    this.idleSince = performance.now();
  }

  show(id, index) {
    const spot = this.kind === 'brush' ? layout.zones[id] : layout.gaps[id];
    this.hl.src = ART.guide(id);
    this.label.textContent = (this.kind === 'brush' ? ZONE_LABELS : GAP_LABELS)[id];
    this.tool.style.left = `${spot.x * 100}%`;
    this.tool.style.top = `${spot.y * 100}%`;
    [...this.dots.children].forEach((d, i) => {
      d.className = i < index ? 'done' : i === index ? 'on' : '';
    });
    this.setProgress(0);
  }

  setProgress(p) {
    this.fill.style.transform = `scaleX(${Math.max(0, Math.min(1, p))})`;
  }

  setActive(active, now = performance.now()) {
    if (active) this.idleSince = now;
    this.el.classList.toggle('idle', !active);
    // Only nudge after a few seconds without movement.
    this.hint.classList.toggle('show', !active && now - this.idleSince > 3000);
  }

  finish() {
    [...this.dots.children].forEach(d => { d.className = 'done'; });
    this.setProgress(1);
  }
}
