// Halloween edition check: plays a two-player night on Oct 31 (date faked),
// then checks the game is back to normal a week later.
//   python3 -m http.server 8123 &   (from the repo root)
//   NODE_PATH=$(npm root -g) node tests/halloween.mjs [outdir]
import { createRequire } from 'node:module';
import fs from 'node:fs';
const { chromium } = createRequire(import.meta.url)('playwright');

const OUT = process.argv[2] || 'test-output';
fs.mkdirSync(OUT, { recursive: true });
const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
const p = await (await b.newContext({ viewport: { width: 390, height: 844 } })).newPage();
const errors = [];
p.on('pageerror', e => errors.push(String(e)));
const fail = msg => { throw new Error(msg); };

await p.clock.setFixedTime(new Date('2026-10-31T19:30:00'));
await p.goto('http://localhost:8123/?sim=1&fast=12');
await p.waitForSelector('#go-brush');
if (!(await p.isVisible('.event-tag'))) fail('Halloween tag missing on Oct 31');
await p.screenshot({ path: `${OUT}/hw-home.png` });
await p.click('#go-brush'); await p.click('#who-0-1');
await p.waitForSelector('.big', { timeout: 60000 });
const bossArt = await p.evaluate(() => [...document.querySelectorAll('.big img')].map(i => i.naturalWidth && i.src.includes('big_hw')));
if (!bossArt.every(Boolean)) fail('vampire big goblin art did not load');
await p.waitForSelector('text=Ready!', { timeout: 60000 });
await p.click('text=Ready!');
await p.waitForSelector('.btn:has-text("Goodnight")', { timeout: 90000 });
await p.waitForTimeout(1500);
await p.screenshot({ path: `${OUT}/hw-reward.png` });
const won = await p.evaluate(() => JSON.parse(localStorage.getItem('gumgoblins.v1')).profiles.map(k => Object.keys(k.collection)));
if (!won.every(ids => ids.length === 1 && ids[0].startsWith('halloween/'))) fail('expected one Halloween emoji each: ' + JSON.stringify(won));
await p.click('.btn:has-text("Goodnight")');
await p.waitForTimeout(3000);
const broken = await p.evaluate(() => [...document.querySelectorAll('.night-cast img')].filter(i => !i.naturalWidth).length);
if (broken) fail(`${broken} goodnight images failed to load`);

await p.clock.setFixedTime(new Date('2026-11-07T19:30:00'));
await p.goto('http://localhost:8123/?sim=1&fast=12');
await p.waitForSelector('#go-brush');
if (await p.isVisible('.event-tag')) fail('Halloween still on a week later');
await p.click('#my-hero');
if (!(await p.isVisible('[aria-label="hat pumpkin"]'))) fail('earned pumpkin hat should stay available');
console.log('errors:', errors.length ? errors : 'none');
await b.close();
if (errors.length) process.exit(1);
console.log('halloween ok');
