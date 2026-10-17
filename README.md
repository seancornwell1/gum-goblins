# Gum Goblins

A bedtime tooth-care game for Oliver, played on a phone at the sink. Purple Gum
Goblins invade; brushing pops the little ones and beats the big one, flossing
flushes out the sneaky ones between teeth, and every win earns a new emoji.

It's an installable web app (PWA): plain HTML, CSS and JavaScript with no build
step. It runs fully offline once installed, and the camera and photos never
leave the phone.

## Putting it on the phone

The camera only works over HTTPS, so the game has to be hosted. GitHub Pages is
the easiest option:

1. In this repo on GitHub, go to **Settings → Pages**, set **Source** to
   *Deploy from a branch*, then pick branch `main` and folder `/ (root)`.
2. After a minute it's live at `https://seancornwell1.github.io/gum-goblins/`.
3. On the iPhone, open that address in **Safari**, tap **Share → Add to Home
   Screen**, and launch it from the new icon.
4. Open it once while online and wait a few seconds. That downloads everything
   (about 30 MB, mostly the face detector) for offline use.
5. On the first routine, allow camera access.

If the address shows GitHub's 404 page, check the repo's **Actions** tab (top of
the repo page) for a "pages build and deployment" run. Pages only builds on a
push made after it was switched on, and the address must end in
`/gum-goblins/`.

### Setup at the sink

- Stand or mount the phone facing him, with his whole face in the frame.
- The screen stays on during a routine (Wake Lock, with a fallback for older phones).
- The camera view is mirrored, like a real mirror.
- **Sound with the ringer switch on silent:** open the settings (below), tap
  **Test sound** with the switch on, then again with it off. It should play both
  times. This relies on Safari 16.4+ (`navigator.audioSession`), with an older
  silent-audio trick as a fallback. I couldn't test this on a real iPhone, so
  please check it.
- The camera view is a small round mirror in the top-left corner, so you can
  check he's in frame. His hero stands in the middle of the screen.

## How it plays

**Brush & Floss** (every night): brushing → "Get your floss pick" → flossing →
reward → goodnight. The picture strip at the top lights up the current step.

**Morning brush** (the smaller button): brushing only, then a sun sticker on the
calendar. No flossing, and no emoji (those stay the nightly prize).

**His hero:** a tooth hero he dresses up from the home screen (tap it). There
are 6 capes, 6 hats (or none) and 5 brush colours. The hero stands in the middle
of the screen and fires toothpaste bolts at the goblins while he brushes. When
he stops brushing, it stops firing.

There's no narration, just a few short words on screen ("Big Goblin!", "Floss
time!") and the zone name in the guide.

- **Brushing:** six zones, always in this order: top left, top front, top right,
  bottom right, bottom front, bottom left. A mouth diagram in the corner lights
  the zone, with a fill bar and the zone name. A zone's timer
  only runs while his face is in view and there's movement at his mouth (brief
  pauses up to 2 s are allowed). Small goblins gather around the hero and pop as
  each zone fills. The big goblin takes the last zone, to faster battle music.
- **Score:** the share of brushing time that had real movement. At or above the
  pass mark, the big goblin is beaten. Below it, he waddles off saying "I'll be
  back tomorrow!", there's no emoji that night, and he comes back the next night.
  Flossing still happens either way.
- **Pause:** if the camera loses his face for about 1.5 s, everything freezes and
  a calm screen shows the buddy next to a face outline. When it has seen him again
  for about 1 s, the game picks up where it stopped. There's no penalty.
- **Flossing:** quick and long, with 10 gaps of 3 seconds by default (up to 18
  gaps, 9 top and 9 bottom). Front teeth first, then working outwards. A sneaky
  goblin pops up at each gap; when the gap fills, the hero zaps it and it runs
  off. Flossing can't be failed.
- **Reward:** a random emoji he doesn't have yet, picked from tonight's world.
  Once he has an emoji, its rarer **sparkly** version can turn up too.
- **Photo:** the game takes one automatically during the big-goblin fight.
  Tonight's emoji starts on it as a sticker. He can drag stickers, resize them
  (corner handle or two-finger pinch), remove them (×), and add any emoji he's
  ever won from the tray below, as many copies as he likes. **Save photo** opens
  the share sheet on iPhone, where **Save Image** puts it in the camera roll.
- **Collection:** grouped by world, with blank spaces for ones still to find.
- **Calendar:** a tooth sticker for each completed night, a sun for mornings and
  a gold star for Swish.
- **Goodnight:** the world goes dark, and the goblins and the buddy fall asleep
  to a lullaby.

**Swish** (hidden until you turn it on): take a sip → swish countdown → "Spit!"
→ gold star on the calendar.

Worlds: street, forest, city, ocean, outer space, farm, candy land and dino
valley, one picked at random each night. Each has 12 emoji plus their 12
sparkly versions, so 192 to collect.

## Parent settings

**Press and hold the gear (top right) for 1.5 seconds.** Settings:

- Brushing length: 1, 2 or 3 min
- Pass mark: 20–80%, default 30%
- Floss gaps: 6–18, default 10
- Seconds per gap: 2–8, default 3
- Swish on/off and countdown length
- Music and effects volume
- Camera on/off (with it off, the timers just run)
- Movement sensitivity, with a live check that shows whether the camera sees his
  face and movement
- During a routine: **Next step** (finishes the current step as if it went well,
  for when the camera struggles) and **End and go home**
- Reset collection & calendar

## Art and sound

All art and audio are generated files. The game code only places and animates
them.

| What | Generated by | Output |
| --- | --- | --- |
| Characters, hero parts, worlds, emoji, mouth guide, icons | `tools/gen_art.py` + `tools/art_extra.py` (SVG) | `assets/img/` |
| Music loops and sound effects | `tools/gen_audio.py` (numpy synthesis → MP3) | `assets/audio/` |

To swap in different art (for example AI-generated images), drop a replacement
file in with the same name and aspect ratio. After changing any file, run
`python3 tools/build_sw.py` so installed phones pick up the update.

Regenerating:

```sh
pip install numpy           # plus ffmpeg and rsvg-convert
python3 tools/gen_art.py
python3 tools/gen_audio.py
python3 tools/build_sw.py
```

## Development

```sh
python3 -m http.server 8123          # then open http://localhost:8123/
```

Testing aids: `?sim=1` fakes the camera (press `f` to toggle face in view, `m`
to toggle movement) and `?fast=10` runs the timers 10× faster. To run the
end-to-end test (needs Playwright):

```sh
NODE_PATH=$(npm root -g) node tests/flow.mjs
```

Face detection uses MediaPipe's on-device BlazeFace model, which is vendored in
`vendor/` so it works offline.

## Privacy

Camera frames are analysed in memory on the phone and thrown away. The one photo
per night exists only on the reward screen until he saves it to the phone.
Progress lives in the browser's local storage. Nothing is uploaded, and the app
makes no requests to any other server.
