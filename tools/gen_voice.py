#!/usr/bin/env python3
"""Generates the narration clips into assets/audio/voice/.

Uses the Kokoro neural text-to-speech model (runs offline):

    pip install kokoro-onnx soundfile
    # download kokoro-v1.0.int8.onnx and voices-v1.0.bin from
    # https://github.com/thewh1teagle/kokoro-onnx/releases (model-files-v1.0)
    python3 tools/gen_voice.py path/to/kokoro.onnx path/to/voices.bin

The lines never change from night to night, so each is a fixed file. The ids
must match LINES in js/narration.js.
"""
import json
import os
import subprocess
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "audio", "voice")
VOICE = "af_heart"
SPEED = 0.92

LINES = {
    # brushing
    "lets_brush": "Let's brush! Gum Goblins are coming!",
    "world_street": "Tonight, we're on the street!",
    "world_forest": "Tonight, we're in the forest!",
    "world_city": "Tonight, we're in the city!",
    "zone_top_left": "Top teeth, left side.",
    "zone_top_front": "Top teeth, front.",
    "zone_top_right": "Top teeth, right side.",
    "zone_bottom_right": "Bottom teeth, right side.",
    "zone_bottom_front": "Bottom teeth, front.",
    "zone_bottom_left": "Bottom teeth, left side.",
    "big_goblin": "Here comes the big goblin! Keep brushing!",
    "big_back": "The big goblin is back for another try!",
    "big_beaten": "You beat the big goblin! Hooray!",
    "big_escaped": "Oh no, the big goblin got away. We'll get him tomorrow!",
    # pause / resume
    "come_back": "Come back to the mirror, so I can see you.",
    "there_you_are": "There you are!",
    # flossing
    "get_floss": "Get your floss pick. Tap when you're ready.",
    "lets_floss": "Let's find the sneaky goblins!",
    "gap_top_mid": "Top front teeth, in the middle.",
    "gap_bottom_mid": "Bottom front teeth, in the middle.",
    "gap_top_left": "Top teeth, next gap to the left.",
    "gap_top_right": "Top teeth, next gap to the right.",
    "gap_bottom_left": "Bottom teeth, next gap to the left.",
    "gap_bottom_right": "Bottom teeth, next gap to the right.",
    "floss_done": "Great flossing!",
    # reward / goodnight
    "new_emoji": "You found a new emoji!",
    "all_found": "You found every emoji! Amazing!",
    "no_emoji": "No new emoji tonight. Beat the big goblin tomorrow to win one!",
    "photo": "Put your sticker anywhere you like.",
    "goodnight": "Goodnight, Oliver. Sleep tight.",
    # swish
    "take_sip": "Take a sip. Tap when it's in your mouth.",
    "swish": "Swish, swish, swish!",
    "spit": "Spit!",
    "swish_done": "Great job! You earned a gold star!",
}


def main():
    model, voices = sys.argv[1], sys.argv[2]
    from kokoro_onnx import Kokoro
    k = Kokoro(model, voices)
    os.makedirs(OUT, exist_ok=True)
    durations = {}
    for key, text in LINES.items():
        samples, sr = k.create(text, voice=VOICE, speed=SPEED, lang="en-us")
        x = np.asarray(samples, dtype=np.float32)
        x = x / (np.max(np.abs(x)) + 1e-9) * 0.85
        pad = np.zeros(int(0.08 * sr), dtype=np.float32)
        x = np.concatenate([pad, x, pad])
        pcm = (np.clip(x, -1, 1) * 32767).astype("<i2").tobytes()
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "s16le", "-ar", str(sr), "-ac", "1", "-i", "-",
                        "-c:a", "libmp3lame", "-b:a", "64k", os.path.join(OUT, key + ".mp3")], input=pcm, check=True)
        durations[key] = round(len(x) / sr, 2)
        print(f"{key}: {text}")
    with open(os.path.join(OUT, "lines.json"), "w") as f:
        json.dump({"voice": VOICE, "lines": LINES, "durations": durations}, f, indent=1)


if __name__ == "__main__":
    main()
