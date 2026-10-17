// Keeps the screen on for the whole routine. Uses the Screen Wake Lock API,
// and falls back to a tiny silent looping video on browsers without it.

let lock = null;
let wanted = false;
const video = () => document.getElementById('keepawake');

async function acquire() {
  if (!wanted) return;
  try {
    if ('wakeLock' in navigator) {
      lock = await navigator.wakeLock.request('screen');
      lock.addEventListener('release', () => { lock = null; });
      return;
    }
  } catch (e) { /* denied (e.g. low power mode): use the video fallback */ }
  video().play().catch(() => {});
}

// Call keepAwake(true) from a tap handler.
export function keepAwake(on) {
  wanted = on;
  if (on) {
    // Start the fallback synchronously inside the gesture as well; it is
    // harmless when the wake lock works.
    video().play().catch(() => {});
    acquire();
  } else {
    lock?.release().catch(() => {});
    lock = null;
    video().pause();
  }
}

document.addEventListener('visibilitychange', () => {
  if (!document.hidden && wanted && !lock) acquire();
});
