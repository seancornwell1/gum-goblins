// The reward photo: tonight's emoji sits on it as a sticker, he drags it
// where he wants, and it is saved to the phone (share sheet -> Save Image on
// iPhone, or a download elsewhere). The photo never leaves the phone.

import { h, img, toast } from './dom.js';
import { ART } from './assets.js';

export function photoCard(canvas, emojiId) {
  const pic = img(canvas.toDataURL('image/jpeg', 0.9));
  const sticker = img(ART.emoji(emojiId), 'sticker');
  const pos = { x: 0.78, y: 0.24 };
  const place = () => { sticker.style.left = `${pos.x * 100}%`; sticker.style.top = `${pos.y * 100}%`; };
  place();
  const card = h('div', { class: 'photo' }, pic, sticker, h('div', { class: 'drag-hint' }, 'Drag your sticker!'));

  let dragging = false;
  const move = e => {
    if (!dragging) return;
    const r = card.getBoundingClientRect();
    pos.x = Math.max(0.05, Math.min(0.95, (e.clientX - r.left) / r.width));
    pos.y = Math.max(0.05, Math.min(0.95, (e.clientY - r.top) / r.height));
    place();
  };
  card.addEventListener('pointerdown', e => {
    dragging = true;
    card.setPointerCapture(e.pointerId);
    card.querySelector('.drag-hint')?.remove();
    move(e);
  });
  card.addEventListener('pointermove', move);
  card.addEventListener('pointerup', () => { dragging = false; });
  card.addEventListener('pointercancel', () => { dragging = false; });

  async function save() {
    const out = document.createElement('canvas');
    out.width = canvas.width;
    out.height = canvas.height;
    const g = out.getContext('2d');
    g.drawImage(canvas, 0, 0);
    const stickerImg = await loadImage(ART.emojiPng(emojiId));
    const size = out.width * 0.34;
    g.drawImage(stickerImg, pos.x * out.width - size / 2, pos.y * out.height - size / 2, size, size);
    const blob = await new Promise(r => out.toBlob(r, 'image/jpeg', 0.92));
    const name = `gum-goblins-${new Date().toISOString().slice(0, 10)}.jpg`;
    const file = new File([blob], name, { type: 'image/jpeg' });
    try {
      if (navigator.canShare?.({ files: [file] })) {
        await navigator.share({ files: [file] });
        return true;
      }
    } catch (e) {
      if (e.name === 'AbortError') return false;
    }
    const a = h('a', { href: URL.createObjectURL(blob), download: name });
    document.body.append(a);
    a.click();
    a.remove();
    toast('Photo saved');
    return true;
  }

  return { el: card, save };
}

function loadImage(src) {
  return new Promise((res, rej) => {
    const i = new Image();
    i.onload = () => res(i);
    i.onerror = rej;
    i.src = src;
  });
}
