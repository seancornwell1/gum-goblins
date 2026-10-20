// End-to-end smoke test in headless Chromium with a simulated camera.
//   python3 -m http.server 8123 &   (from the repo root)
//   NODE_PATH=$(npm root -g) node tests/flow.mjs [outdir]
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
import fs from 'node:fs';

const OUT = process.argv[2] || 'test-output';
fs.mkdirSync(OUT, { recursive: true });
const BASE = 'http://localhost:8123/';
const errors = [];

const browser = await chromium.launch({
  executablePath: process.env.CHROMIUM || undefined,
  args: ['--autoplay-policy=no-user-gesture-required'],
});
const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, hasTouch: true });
const page = await ctx.newPage();
page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
page.on('pageerror', e => errors.push(String(e)));
const shot = n => page.screenshot({ path: `${OUT}/${n}.png` });
const until = async (fn, ms = 60000) => {
  const t = Date.now();
  while (Date.now() - t < ms) { if (await page.evaluate(fn)) return; await page.waitForTimeout(200); }
  throw new Error('timeout waiting for ' + fn);
};
const hasText = t => `document.body.innerText.includes(${JSON.stringify(t)})`;

await page.goto(BASE + '?sim=1&fast=12');
await page.waitForSelector('#go-brush');
await page.waitForTimeout(800);
await shot('01-home');

// ---- brush & floss, passing
await page.click('#go-brush');
await page.click('#who-0');
await page.waitForTimeout(4500);
await shot('02-brushing');
await page.evaluate(() => { window.__sim[0].inView = false; });
await page.waitForTimeout(600);
if (await page.isHidden('#pause')) throw new Error('pause overlay did not appear');
await shot('03-paused');
await page.evaluate(() => { window.__sim[0].inView = true; });
await page.waitForTimeout(400);
if (!(await page.isHidden('#pause'))) throw new Error('pause overlay did not clear');
await page.waitForTimeout(1500);
await shot('03b-bolts');
await until(() => !!document.querySelector('.big'));
await page.waitForTimeout(800);
await shot('04-big-goblin');
await until(new Function('return ' + hasText('Get your floss pick')));
await page.waitForTimeout(500);
await shot('05-floss-pause');
await page.click('text=Ready!');
await page.waitForTimeout(2600);
await shot('06-flossing');
await until(new Function('return ' + hasText('Goodnight')), 90000);
await page.waitForTimeout(2500);
await shot('07-reward');
const owned = await page.evaluate(() => Object.keys(JSON.parse(localStorage.getItem('gumgoblins.v1')).profiles[0].collection).length);
if (owned !== 1) throw new Error('expected 1 emoji, got ' + owned);
await page.click('text=Collection');
await page.waitForTimeout(700);
await shot('08-collection');
await page.click('#overlay .close');
await page.click('.btn:has-text("Goodnight")');
await page.waitForTimeout(4000);
await shot('09-goodnight');
await until(() => document.querySelector('.goodnight-text .btn')?.style.opacity === '1', 30000);
await page.click('.goodnight-text .btn');
await page.waitForSelector('#go-brush');

// ---- hero dress-up
await page.click('#my-hero');
await page.waitForTimeout(500);
await page.click('[aria-label="hat pirate"]');   // locked: shows how to earn it
await page.waitForSelector('text=Find 25 emoji to unlock this!');
await page.click('[aria-label="hat cap"]');
await page.click('[aria-label="cape red"]');
await shot('09b-hero-editor');
await page.click('#overlay .btn:has-text("Done")');
const look = await page.evaluate(() => JSON.parse(localStorage.getItem('gumgoblins.v1')).profiles[0].hero);
if (look.hat !== 'cap' || look.cape !== 'red') throw new Error('hero look not saved');

// ---- morning brush (no flossing)
await page.click('#go-morning');
await page.click('#who-0');
await until(new Function('return ' + hasText('Good morning!')), 90000);
await page.waitForTimeout(1200);
if (!(await page.evaluate(new Function('return ' + hasText('New hero item!'))))) throw new Error('morning unlock not shown');
await shot('09c-morning');
const sun = await page.evaluate(() => Object.keys(JSON.parse(localStorage.getItem('gumgoblins.v1')).profiles[0].mornings).length);
if (sun !== 1) throw new Error('morning sun not recorded');
await page.click('text=All done');
await page.waitForSelector('#go-brush');

// ---- settings via long press; turn on swish
const g = await page.locator('#gear').boundingBox();
await page.mouse.move(g.x + 20, g.y + 20);
await page.mouse.down();
await page.waitForTimeout(1700);
await page.mouse.up();
if (await page.isHidden('#settings')) throw new Error('settings did not open');
await page.click('#settings .set:has-text("Swish mode") button:has-text("On")');
await shot('10-settings');
await page.click('#settings .close');
await page.waitForSelector('#go-swish');
await shot('11-home-swish');

// ---- swish
await page.click('#go-swish');
await page.click('#who-0');
await page.waitForTimeout(800);
await shot('12-sip');
await page.click('text=Ready!');
await page.waitForTimeout(900);
await shot('13-swish');
await until(new Function('return ' + hasText('Spit!')), 30000);
await shot('14-spit');
await until(() => document.querySelector('.btn')?.style.visibility === 'visible', 15000);
await page.click('text=Done!');
await page.waitForTimeout(1500);
await shot('15-star');
await page.click('text=All done');
await page.waitForSelector('#go-brush');

// ---- brush with too little movement: big goblin escapes
await page.evaluate(() => { window.__sim[0].lazy = true; });
await page.click('#go-brush');
await page.click('#who-0');
await page.waitForTimeout(9000);
const crowd = await page.evaluate(() => document.querySelectorAll('.goblin:not(.pop)').length);
console.log('goblins on screen while brushing slowly:', crowd);
await shot('15b-pileup');
await until(new Function('return ' + hasText("I'll be back tomorrow")), 90000);
await page.waitForTimeout(1200);
await shot('16-escape');
const esc = await page.evaluate(() => JSON.parse(localStorage.getItem('gumgoblins.v1')).profiles[0].bigEscaped);
if (!esc) throw new Error('big goblin should have escaped');
// Parent "next step" from settings skips the pause screen.
await until(new Function('return ' + hasText('Get your floss pick')));
await page.evaluate(() => window.__game.nextStep());
await until(new Function('return ' + hasText('No emoji tonight')), 60000);
await page.waitForTimeout(1500);
await shot('17-no-emoji');
await page.click('text=Calendar');
await page.waitForTimeout(600);
await shot('18-calendar');

await page.click('#overlay .close');
await page.click('.btn:has-text("Goodnight")');
await until(() => document.querySelector('.goodnight-text .btn')?.style.opacity === '1', 30000);
await page.click('.goodnight-text .btn');
await page.waitForSelector('#go-brush');

// ---- two players: both brush, player 2 steps away once, player 2 brushes lazily
await page.evaluate(() => { window.__sim[0].lazy = false; window.__sim[1].lazy = true; });
await page.click('#go-brush');
await page.waitForSelector('#who-0-1');
await shot('19-who');
await page.click('#who-0-1');
await page.waitForTimeout(4500);
const heroes = await page.evaluate(() => document.querySelectorAll('#stage .hero.center').length);
if (heroes !== 2) throw new Error('expected two heroes, got ' + heroes);
await shot('20-duo-brushing');
await page.evaluate(() => { window.__sim[1].inView = false; });
await page.waitForTimeout(600);
const pauseText = await page.textContent('#pause .pause-text');
if (!pauseText.includes('Juniper')) throw new Error('pause should name Juniper: ' + pauseText);
await shot('21-duo-paused');
await page.evaluate(() => { window.__sim[1].inView = true; });
await until(new Function('return ' + hasText('Get your floss picks')), 90000);
await page.click('text=Ready!');
await until(new Function('return ' + hasText('Goodnight')), 90000);
await page.waitForTimeout(2000);
await shot('22-duo-reward');
const counts = await page.evaluate(() => JSON.parse(localStorage.getItem('gumgoblins.v1')).profiles.map(p => Object.keys(p.collection).length));
console.log('emoji per kid after duo night:', counts);
if (counts[1] !== 0) throw new Error('lazy player 2 should not earn an emoji');
const beat = await page.evaluate(() => JSON.parse(localStorage.getItem('gumgoblins.v1')).profiles.map(p => p.bigEscaped));
if (beat.some(Boolean)) throw new Error('team should have beaten the big goblin');
await page.click('.btn:has-text("Goodnight")');
await page.waitForTimeout(3500);
await shot('23-duo-goodnight');

console.log('errors:', errors.length ? errors : 'none');
await browser.close();
if (errors.length) process.exit(1);
console.log('flow ok');
