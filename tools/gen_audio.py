#!/usr/bin/env python3
"""Generates the game's music loops and sound effects into assets/audio/.

    python3 tools/gen_audio.py

Everything is synthesised offline with numpy and encoded with ffmpeg; the game
only plays the resulting files. Levels are kept gentle on purpose: no sudden
loud sounds, soft attacks, peaks well below full scale.

Music loops are written as one full loop followed by a little more of the same
(periodic) material. The game loops between LOOP_START and LOOP_START + length
seconds, so encoder padding at the start of an MP3 never causes a gap.
"""
import json
import os
import subprocess
import tempfile

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "audio")
SR = 44100
LOOP_START = 1.0  # seconds; must stay inside the periodic region
TAIL = 3.0  # extra seconds rendered after one loop


def midi(n):
    names = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    if isinstance(n, (int, float)):
        return n
    base = names[n[0]]
    rest = n[1:]
    if rest.startswith("#"):
        base += 1
        rest = rest[1:]
    elif rest.startswith("b"):
        base -= 1
        rest = rest[1:]
    return base + 12 * (int(rest) + 1)


def hz(n):
    return 440.0 * 2 ** ((midi(n) - 69) / 12)


def env(n, a=0.005, d=0.1, s=0.6, r=0.1, hold=None):
    """ADSR envelope of n samples. hold = samples before release starts."""
    hold = n if hold is None else hold
    t = np.arange(n) / SR
    e = np.ones(n) * s
    ai = int(a * SR)
    di = int(d * SR)
    e[:ai] = np.linspace(0, 1, ai, endpoint=False) if ai else e[:ai]
    if di:
        seg = np.linspace(1, s, di, endpoint=False)
        e[ai:ai + di] = seg[:max(0, min(di, n - ai))]
    if hold < n:
        rel = np.exp(-(t[hold:] - t[hold]) / max(r, 1e-3) * 4)
        e[hold:] = e[hold - 1 if hold else 0] * rel
    return e


def osc(kind, f, n, phase=0.0):
    t = np.arange(n) / SR
    ph = 2 * np.pi * f * t + phase
    if kind == "sine":
        return np.sin(ph)
    if kind == "tri":
        return 2 / np.pi * np.arcsin(np.sin(ph))
    if kind == "square":  # band-limited-ish soft square
        return sum(np.sin(ph * k) / k for k in (1, 3, 5, 7, 9)) * 0.9
    if kind == "saw":
        return sum(np.sin(ph * k) / k * (-1) ** (k + 1) for k in range(1, 10)) * 0.6
    raise ValueError(kind)


# ---------------------------------------------------------------- instruments

def inst_pluck(f, dur, vel):
    n = int((dur + 0.4) * SR)
    x = osc("square", f, n) * 0.5 + osc("tri", f, n) * 0.5
    e = env(n, a=0.004, d=0.18, s=0.35, r=0.12, hold=int(dur * SR))
    return x * e * vel


def inst_lead(f, dur, vel):
    n = int((dur + 0.3) * SR)
    t = np.arange(n) / SR
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.5 * t) * np.clip(t * 3, 0, 1)
    ph = 2 * np.pi * f * np.cumsum(vib) / SR
    x = np.sin(ph) * 0.6 + np.sin(2 * ph) * 0.25 + np.sin(3 * ph) * 0.12
    e = env(n, a=0.012, d=0.12, s=0.7, r=0.15, hold=int(dur * SR))
    return x * e * vel


def inst_bass(f, dur, vel):
    n = int((dur + 0.2) * SR)
    x = osc("tri", f, n) * 0.8 + osc("sine", f / 2, n) * 0.3
    e = env(n, a=0.006, d=0.12, s=0.6, r=0.08, hold=int(dur * SR))
    return x * e * vel


def inst_pad(f, dur, vel):
    n = int((dur + 0.8) * SR)
    x = sum(osc("saw", f * d, n) for d in (0.997, 1.0, 1.003)) / 3
    x = lp_np(x, 900)
    e = env(n, a=0.35, d=0.3, s=0.8, r=0.6, hold=int(dur * SR))
    return x * e * vel


def inst_marimba(f, dur, vel):
    n = int(1.2 * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * t) * np.exp(-t * 5) + 0.35 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 18)
    x[:int(0.003 * SR)] *= np.linspace(0, 1, int(0.003 * SR))
    return x * vel


def inst_musicbox(f, dur, vel):
    n = int(2.0 * SR)
    t = np.arange(n) / SR
    x = (np.sin(2 * np.pi * f * t) * np.exp(-t * 2.2)
         + 0.4 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t * 4)
         + 0.15 * np.sin(2 * np.pi * f * 5.04 * t) * np.exp(-t * 9))
    x[:int(0.004 * SR)] *= np.linspace(0, 1, int(0.004 * SR))
    return x * vel


def inst_kick(f, dur, vel):
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    freq = 50 + 90 * np.exp(-t * 30)
    x = np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-t * 9)
    return x * vel


def inst_snare(f, dur, vel):
    n = int(0.25 * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(7)
    x = rng.uniform(-1, 1, n)
    x = x - lp_np(x, 1200)
    x = x * np.exp(-t * 20) * 0.6 + np.sin(2 * np.pi * 190 * t) * np.exp(-t * 25) * 0.4
    return x * vel


def inst_shaker(f, dur, vel):
    n = int(0.08 * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(11)
    x = rng.uniform(-1, 1, n)
    x = x - lp_np(x, 5000)
    return x * np.exp(-t * 60) * vel


def inst_crash(f, dur, vel):
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(21)
    x = rng.uniform(-1, 1, n)
    x = x - lp_np(x, 4000)
    return x * np.exp(-t * 2.5) * vel


def inst_tom(f, dur, vel):
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    freq = f * (1 + 0.5 * np.exp(-t * 20))
    x = np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-t * 7)
    return x * vel


def lp_np(x, cutoff):
    """Vectorised 2-pole low-pass using FFT (fine for offline rendering)."""
    X = np.fft.rfft(x)
    fr = np.fft.rfftfreq(len(x), 1 / SR)
    H = 1 / (1 + (fr / cutoff) ** 4) ** 0.5
    return np.fft.irfft(X * H, len(x))


INSTR = {"crash": inst_crash, "brass": lambda f, d, v: inst_brass(f, d, v), "pluck": inst_pluck, "lead": inst_lead, "bass": inst_bass, "pad": inst_pad,
         "marimba": inst_marimba, "musicbox": inst_musicbox, "kick": inst_kick,
         "snare": inst_snare, "shaker": inst_shaker, "tom": inst_tom}


def reverb(x, secs=1.6, mix=0.18, seed=3):
    rng = np.random.default_rng(seed)
    n = int(secs * SR)
    t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t * 4.5 / secs)
    ir = lp_np(ir, 5000)
    ir /= np.sqrt(np.sum(ir ** 2))
    m = len(x) + n
    size = 1 << (m - 1).bit_length()
    wet = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[:len(x)]
    return x * (1 - mix) + wet * mix * 0.6


# ---------------------------------------------------------------- song rendering

def render_song(bpm, beats, events, rev=0.2):
    """events: (beat, dur_beats, note, vel, instrument). Returns periodic audio."""
    spb = 60 / bpm
    loop = beats * spb
    total = 2 * loop + 4
    buf = np.zeros(int(total * SR) + SR)
    for beat, dur, note, vel, ins in events:
        f = hz(note) if note is not None else 0
        x = INSTR[ins](f, dur * spb, vel)
        for rep in range(2):  # place twice so the tail is periodic
            st = int((beat * spb + rep * loop) * SR)
            if st >= len(buf):
                continue
            e = min(len(buf), st + len(x))
            buf[st:e] += x[:e - st]
    # One period, including ring-out carried over from the previous repeat.
    L = int(loop * SR)
    period = buf[L:2 * L]
    tiled = reverb(np.tile(period, 3), mix=rev)
    seg = tiled[L:2 * L + int(TAIL * SR)]
    return seg, loop


def chord_notes(root, kind):
    r = midi(root)
    return [r, r + (3 if kind == "m" else 4), r + 7]


def song_adventure():
    bpm, ev = 118, []
    chords = [("C3", ""), ("G2", ""), ("A2", "m"), ("F2", ""), ("C3", ""), ("G2", ""), ("F2", ""), ("G2", "")]
    for bar, (root, kind) in enumerate(chords):
        b0 = bar * 4
        r = midi(root)
        for off in (0, 1.5, 2, 3, 3.5):
            ev.append((b0 + off, 0.4, r, 0.42, "bass"))
        for off in (0.5, 1.5, 2.5, 3.5):
            for n in chord_notes(r + 12, kind):
                ev.append((b0 + off, 0.25, n + 12, 0.07, "pluck"))
        ev.append((b0, 4, r + 24, 0.05, "pad"))
        ev += [(b0 + 0, 0.2, None, 0.55, "kick"), (b0 + 2, 0.2, None, 0.5, "kick"),
               (b0 + 1, 0.2, None, 0.22, "snare"), (b0 + 3, 0.2, None, 0.22, "snare")]
        ev += [(b0 + k * 0.5, 0.1, None, 0.06 if k % 2 else 0.1, "shaker") for k in range(8)]
    mel = [["E5", "-", "G5", "-", "A5", "G5", "E5", "-"], ["D5", "-", "G5", "-", "B5", "A5", "G5", "-"],
           ["C5", "E5", "A5", "-", "G5", "-", "E5", "-"], ["F5", "-", "A5", "-", "G5", "F5", "E5", "D5"],
           ["E5", "G5", "C6", "-", "B5", "-", "G5", "-"], ["D5", "G5", "B5", "-", "D6", "-", "B5", "-"],
           ["C6", "-", "A5", "-", "F5", "-", "A5", "-"], ["G5", "-", "F5", "-", "E5", "-", "D5", "-"]]
    ev += melody(mel, 0.5, 0.2, "lead")
    return bpm, 32, ev


def song_boss():
    """Big-goblin battle: fast, heroic and bright, building to a climax."""
    bpm, ev = 152, []
    # D major hero theme with a lift in the second half.
    chords = [("B2", "m"), ("G2", ""), ("D3", ""), ("A2", ""), ("B2", "m"), ("G2", ""), ("A2", ""), ("A2", ""),
              ("G2", ""), ("A2", ""), ("F#2", "m"), ("B2", "m"), ("G2", ""), ("A2", ""), ("D3", ""), ("A2", "")]
    for bar, (root, kind) in enumerate(chords):
        b0 = bar * 4
        r = midi(root)
        for k in range(8):  # galloping octave bass
            ev.append((b0 + k * 0.5, 0.35, r + (12 if k % 2 else 0), 0.4, "bass"))
        for k in range(16):  # sixteenth-note string ostinato
            n = chord_notes(r + 24, kind)[[0, 1, 2, 1][k % 4]]
            ev.append((b0 + k * 0.25, 0.2, n, 0.06 + (0.03 if k % 4 == 0 else 0), "pluck"))
        for n in chord_notes(r + 12, kind):  # brass stabs
            ev.append((b0, 0.6, n, 0.12, "brass"))
            ev.append((b0 + 2.5, 0.4, n, 0.09, "brass"))
        ev.append((b0, 4, r + 24, 0.05, "pad"))
        ev += [(b0 + k, 0.2, None, 0.5, "kick") for k in range(4)]
        ev += [(b0 + 1, 0.2, None, 0.3, "snare"), (b0 + 3, 0.2, None, 0.3, "snare")]
        ev += [(b0 + k * 0.5 + 0.25, 0.1, None, 0.07, "shaker") for k in range(8)]
        if bar % 4 == 0:
            ev.append((b0, 1, None, 0.22, "crash"))
        if bar % 4 == 3:  # drum fill into the next phrase
            ev += [(b0 + 3 + k * 0.25, 0.2, ["A2", "F2", "D2", "A1"][k], 0.32, "tom") for k in range(4)]
    mel = [  # soaring brass melody
        ["F#5", "-", "-", "D5", "B4", "-", "D5", "F#5"], ["G5", "-", "-", "-", "B5", "-", "A5", "G5"],
        ["F#5", "-", "A5", "-", "D6", "-", "-", "-"], ["C#6", "-", "B5", "-", "A5", "-", "-", "-"],
        ["F#5", "-", "-", "D5", "B4", "-", "D5", "F#5"], ["G5", "-", "-", "-", "B5", "-", "D6", "-"],
        ["E6", "-", "-", "-", "C#6", "-", "A5", "-"], ["A5", "-", "B5", "-", "C#6", "-", "E6", "-"],
        ["D6", "-", "-", "-", "B5", "-", "G5", "-"], ["C#6", "-", "-", "-", "A5", "-", "E5", "-"],
        ["F#5", "-", "A5", "-", "C#6", "-", "F#6", "-"], ["F#6", "-", "-", "E6", "D6", "-", "B5", "-"],
        ["G5", "-", "B5", "-", "D6", "-", "G6", "-"], ["E6", "-", "F#6", "-", "G6", "-", "E6", "-"],
        ["F#6", "-", "-", "-", "D6", "-", "A5", "-"], ["A5", "-", "C#6", "-", "E6", "-", "A6", "-"]]
    ev += melody(mel, 0.5, 0.2, "brass")
    ev += melody(mel, 0.5, 0.08, "lead")
    return bpm, 64, ev


def song_calm():
    bpm, ev = 88, []
    chords = [("F3", ""), ("C3", ""), ("D3", "m"), ("Bb2", ""), ("F3", ""), ("C3", ""), ("Bb2", ""), ("C3", "")]
    for bar, (root, kind) in enumerate(chords):
        b0 = bar * 4
        r = midi(root)
        notes = chord_notes(r + 12, kind)
        arp = [notes[0], notes[1], notes[2], notes[0] + 12, notes[2], notes[1], notes[2], notes[0] + 12]
        for k, n in enumerate(arp):
            ev.append((b0 + k * 0.5, 0.5, n, 0.22 if k % 2 == 0 else 0.16, "marimba"))
        ev.append((b0, 4, r, 0.28, "bass"))
        ev.append((b0, 4, r + 24, 0.05, "pad"))
        ev.append((b0, 4, r + 28 if kind != "m" else r + 27, 0.04, "pad"))
    mel = [["A5", "-", "-", "-", "C6", "-", "A5", "-"], ["G5", "-", "-", "-", "E5", "-", "-", "-"],
           ["F5", "-", "A5", "-", "D6", "-", "-", "-"], ["D6", "-", "C6", "-", "Bb5", "-", "-", "-"],
           ["A5", "-", "-", "-", "C6", "-", "F6", "-"], ["E6", "-", "-", "-", "C6", "-", "-", "-"],
           ["D6", "-", "C6", "-", "Bb5", "-", "A5", "-"], ["G5", "-", "-", "-", "-", "-", "-", "-"]]
    ev += melody(mel, 0.5, 0.1, "lead")
    return bpm, 32, ev


def song_lullaby():
    bpm, ev = 72, []
    chords = [("C3", ""), ("A2", "m"), ("F2", ""), ("G2", ""), ("C3", ""), ("A2", "m"), ("F2", ""), ("G2", "")]
    for bar, (root, kind) in enumerate(chords):
        b0 = bar * 3
        r = midi(root)
        ev.append((b0, 3, r + 12, 0.05, "pad"))
        ev.append((b0, 3, r + 16 if kind != "m" else r + 15, 0.035, "pad"))
        ev.append((b0, 3, r, 0.18, "bass"))
    mel = [["E5", "G5", "E5"], ["D5", "C5", "D5"], ["E5", "E5", "G5"], ["A5", "-", "-"],
           ["G5", "E5", "C5"], ["D5", "E5", "D5"], ["C5", "D5", "B4"], ["C5", "-", "-"]]
    ev += melody(mel, 1, 0.22, "musicbox")
    return bpm, 24, ev


def melody(bars, step, vel, ins):
    ev, beat = [], 0.0
    cur = None
    for bar in bars:
        for n in bar:
            if n == "-":
                if cur:
                    cur[1] += step
            else:
                if cur:
                    ev.append(tuple(cur))
                cur = [beat, step, n, vel, ins]
            beat += step
    if cur:
        ev.append(tuple(cur))
    return ev


# ---------------------------------------------------------------- sound effects

def fx_pop():
    n = int(0.28 * SR)
    t = np.arange(n) / SR
    f = 380 + 900 * (1 - np.exp(-t * 26))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 16)
    x += 0.25 * np.sin(2 * np.pi * np.cumsum(f * 2) / SR) * np.exp(-t * 26)
    return soft_start(x) * 0.55


def fx_chime():
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for i, note in enumerate(["E6", "B6"]):
        st = int(i * 0.09 * SR)
        f = hz(note)
        tt = t[:n - st]
        x[st:] += (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * f * 2.76 * tt) * np.exp(-tt * 6)) * np.exp(-tt * 3)
    return reverb(soft_start(x), 1.2, 0.25) * 0.3


def fx_fanfare():
    seq = [("C5", 0, .18), ("E5", .18, .18), ("G5", .36, .18), ("C6", .54, 1.2)]
    n = int(2.6 * SR)
    x = np.zeros(n)
    for note, st, dur in seq:
        for mult, v in ((1, 1), (0.5, 0.4)):
            y = inst_brass(hz(note) * mult, dur, v)
            s = int(st * SR)
            e = min(n, s + len(y))
            x[s:e] += y[:e - s]
    for note in ("C4", "E4", "G4"):
        y = inst_pad(hz(note), 1.4, 0.25)
        s = int(0.54 * SR)
        e = min(n, s + len(y))
        x[s:e] += y[:e - s]
    x += sparkle_layer(n, 0.6)
    return reverb(soft_start(x), 1.6, 0.25) * 0.32


def inst_brass(f, dur, vel):
    n = int((dur + 0.3) * SR)
    x = osc("saw", f, n)
    x = lp_np(x, min(2400, f * 5))
    e = env(n, a=0.03, d=0.1, s=0.8, r=0.2, hold=int(dur * SR))
    return x * e * vel


def sparkle_layer(n, start):
    x = np.zeros(n)
    rng = np.random.default_rng(5)
    for k in range(10):
        f = hz(int(rng.choice([84, 88, 91, 96, 100])))
        st = int((start + k * 0.08) * SR)
        m = int(0.5 * SR)
        if st + m > n:
            break
        t = np.arange(m) / SR
        x[st:st + m] += np.sin(2 * np.pi * f * t) * np.exp(-t * 9) * 0.12
    return x


def fx_sparkle():
    n = int(1.6 * SR)
    x = sparkle_layer(n, 0.0) * 3
    return reverb(soft_start(x), 1.4, 0.35) * 0.4


def fx_whoosh():
    n = int(1.2 * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(9)
    noise = rng.uniform(-1, 1, n)
    lo = lp_np(noise, 700)
    hi = lp_np(noise, 2500)
    sweep = np.sin(np.pi * t / t[-1]) ** 2
    x = (lo * (1 - t / t[-1]) + hi * (t / t[-1])) * sweep
    return x / np.max(np.abs(x)) * 0.3


def fx_wave():
    n = int(3.0 * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(13)
    noise = lp_np(rng.uniform(-1, 1, n), 1200)
    shape = np.sin(np.pi * t / t[-1]) ** 1.5 * (0.7 + 0.3 * np.sin(2 * np.pi * 1.3 * t))
    x = noise * shape
    return x / np.max(np.abs(x)) * 0.3


def fx_tap():
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * 880 * t) * np.exp(-t * 45) + 0.4 * np.sin(2 * np.pi * 1320 * t) * np.exp(-t * 60)
    return soft_start(x) * 0.25


def fx_zap():
    """Toothpaste bolt: a quick bright upward sparkle."""
    n = int(0.22 * SR)
    t = np.arange(n) / SR
    f = 900 + 1800 * (t / t[-1])
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 18)
    x += 0.3 * np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR) * np.exp(-t * 26)
    return soft_start(x) * 0.22


def fx_hit():
    n = int(0.4 * SR)
    t = np.arange(n) / SR
    f = 220 * np.exp(-t * 4) + 90
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 10)
    rng = np.random.default_rng(1)
    x += lp_np(rng.uniform(-1, 1, n), 2000) * np.exp(-t * 30) * 0.3
    return soft_start(x) * 0.4


def fx_giggle():
    n = int(0.7 * SR)
    x = np.zeros(n)
    for k in range(4):
        st = int(k * 0.14 * SR)
        m = int(0.11 * SR)
        t = np.arange(m) / SR
        f = 700 + 300 * np.sin(np.pi * t / t[-1]) + k * 40
        x[st:st + m] += np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / t[-1]) ** 2
    return x * 0.18


def two_tone(a, b, vel=0.25):
    n = int(0.7 * SR)
    x = np.zeros(n)
    for i, note in enumerate((a, b)):
        y = inst_marimba(hz(note), 0.3, 1)
        s = int(i * 0.16 * SR)
        e = min(n, s + len(y))
        x[s:e] += y[:e - s]
    return reverb(x, 0.8, 0.2) * vel


def fx_defeat():
    """Big goblin beaten: tumbling down-glide plus a soft sparkle."""
    n = int(2.0 * SR)
    t = np.arange(n) / SR
    f = 700 * np.exp(-t * 1.5) + 120
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.8) * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * t))
    x = x * 0.3 + sparkle_layer(n, 0.9) * 1.5
    return reverb(soft_start(x), 1.2, 0.25) * 0.5


def soft_start(x, ms=3):
    k = int(ms / 1000 * SR)
    x = x.copy()
    x[:k] *= np.linspace(0, 1, k)
    fade = min(len(x), int(0.02 * SR))
    x[-fade:] *= np.linspace(1, 0, fade)
    return x


# ---------------------------------------------------------------- output

def encode(name, x, bitrate="96k"):
    x = np.clip(x, -1, 1)
    pcm = (x * 32767).astype("<i2").tobytes()
    path = os.path.join(OUT, name)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "s16le", "-ar", str(SR), "-ac", "1",
                    "-i", "-", "-c:a", "libmp3lame", "-b:a", bitrate, path], input=pcm, check=True)


def normalize(x, peak):
    return x / (np.max(np.abs(x)) + 1e-9) * peak


def main():
    os.makedirs(OUT, exist_ok=True)
    meta = {"loopStart": LOOP_START, "music": {}}
    for name, fn in [("music_adventure", song_adventure), ("music_boss", song_boss),
                     ("music_calm", song_calm), ("music_lullaby", song_lullaby)]:
        bpm, beats, ev = fn()
        x, loop = render_song(bpm, beats, ev)
        x = normalize(x, 0.5)
        encode(name + ".mp3", x, "112k")
        meta["music"][name] = {"loop": loop}
        print(name, f"{loop:.2f}s loop")
    fx = {"zap": fx_zap(), "pop": fx_pop(), "chime": fx_chime(), "fanfare": fx_fanfare(), "sparkle": fx_sparkle(),
          "whoosh": fx_whoosh(), "wave": fx_wave(), "tap": fx_tap(), "hit": fx_hit(),
          "giggle": fx_giggle(), "resume": two_tone("C5", "G5"), "pause": two_tone("G4", "C4", 0.2),
          "defeat": fx_defeat()}
    for k, v in fx.items():
        encode(f"fx_{k}.mp3", np.clip(v, -0.7, 0.7))
    encode("silence.mp3", np.zeros(SR), "32k")
    with open(os.path.join(OUT, "music.json"), "w") as f:
        json.dump(meta, f, indent=1)
    # Tiny silent looping video: fallback that keeps the screen awake on
    # browsers without the Wake Lock API.
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "color=c=black:s=16x16:r=1:d=4",
                        "-f", "lavfi", "-i", "anullsrc=r=22050:cl=mono", "-t", "4", "-shortest",
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "16k",
                        "-movflags", "+faststart", os.path.join(OUT, "keepawake.mp4")], check=True)
    print("audio written to", OUT)


if __name__ == "__main__":
    main()
