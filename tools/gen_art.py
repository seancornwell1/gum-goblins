#!/usr/bin/env python3
"""Generates every picture in the game as SVG files under assets/img/.

The game code never draws art itself; it only places and animates these
files. Re-run this script after changing a design:

    python3 tools/gen_art.py

Any file can be replaced by a hand-made or AI-generated image with the same
name and aspect ratio (the emoji are also rasterised to PNG for the photo
sticker, see the bottom of this file).
"""
import json
import math
import os
import random
import shutil
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "img")

OL = "#2d1b3d"  # outline colour used by every character


def svg(w, h, body, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}"><defs>{defs}</defs>{body}</svg>')


def write(name, content):
    path = os.path.join(OUT, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


def S(w=6):
    return f'stroke="{OL}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"'


# ---------------------------------------------------------------- faces

def eyes(cx, cy, gap, r, mode="open", look=(0, 0), w=5):
    out = []
    for sx in (-1, 1):
        x = cx + sx * gap
        if mode == "closed":
            out.append(f'<path d="M{x-r} {cy} Q{x} {cy+r*0.9} {x+r} {cy}" fill="none" {S(w)}/>')
        elif mode == "dizzy":
            p = f"M{x} {cy}"
            for i in range(1, 22):
                a = i * 0.6
                rr = r * i / 22
                p += f" L{x+math.cos(a)*rr:.1f} {cy+math.sin(a)*rr:.1f}"
            out.append(f'<circle cx="{x}" cy="{cy}" r="{r}" fill="#fff" {S(w)}/>')
            out.append(f'<path d="{p}" fill="none" stroke="{OL}" stroke-width="{w*0.7}" stroke-linecap="round"/>')
        elif mode == "squint":
            out.append(f'<path d="M{x-r} {cy-r*0.4} L{x+r*0.6} {cy} L{x-r} {cy+r*0.4}" fill="none" {S(w)}/>'
                       if sx < 0 else
                       f'<path d="M{x+r} {cy-r*0.4} L{x-r*0.6} {cy} L{x+r} {cy+r*0.4}" fill="none" {S(w)}/>')
        else:
            px, py = look
            out.append(f'<ellipse cx="{x}" cy="{cy}" rx="{r}" ry="{r*1.1}" fill="#fff" {S(w)}/>')
            out.append(f'<circle cx="{x+px*r*0.35}" cy="{cy+py*r*0.35}" r="{r*0.55}" fill="{OL}"/>')
            out.append(f'<circle cx="{x+px*r*0.35-r*0.2}" cy="{cy+py*r*0.35-r*0.25}" r="{r*0.2}" fill="#fff"/>')
    return "".join(out)


def blush(cx, cy, gap, rx, color="#ff8fb8", op=0.7):
    return "".join(f'<ellipse cx="{cx+s*gap}" cy="{cy}" rx="{rx}" ry="{rx*0.6}" fill="{color}" opacity="{op}"/>'
                   for s in (-1, 1))


def smile(cx, cy, w, h=None, sw=5, fill=None):
    h = h if h is not None else w * 0.55
    if fill:
        return (f'<path d="M{cx-w} {cy} Q{cx} {cy+h*2} {cx+w} {cy} Z" fill="{fill}" {S(sw)}/>')
    return f'<path d="M{cx-w} {cy} Q{cx} {cy+h*1.6} {cx+w} {cy}" fill="none" {S(sw)}/>'


def kawaii(cx, cy, s=1.0, mode="open"):
    """Small cute face used on every collectible emoji."""
    return (eyes(cx, cy, 22 * s, 9 * s, mode, w=4 * s)
            + blush(cx, cy + 16 * s, 36 * s, 9 * s)
            + smile(cx, cy + 14 * s, 10 * s, 6 * s, sw=4 * s))


# ---------------------------------------------------------------- goblins
# Purple, round, friendly. Characters are 300x300 and stand on y≈290.

PURPLES = {
    "a": ("#9b5de5", "#c9a7ff", "#7d3fc8"),
    "b": ("#8a4fd8", "#bfa0f5", "#6b2fb5"),
    "c": ("#b07af0", "#dcc4ff", "#8b52d6"),
    "sneaky": ("#7b48c9", "#b294ef", "#5c2ea6"),
    "big": ("#7b3fd1", "#b58ff2", "#5e28ad"),
}


def goblin_a(mode="open"):
    body, belly, dark = PURPLES["a"]
    m = (smile(150, 190, 34, 18, fill="#5a1f4a") +
         '<path d="M162 191 L170 191 L166 204 Z" fill="#fff" stroke="#2d1b3d" stroke-width="3" stroke-linejoin="round"/>'
         if mode != "closed" else smile(150, 196, 16, 6))
    zz = ""
    return svg(300, 300, f'''
<ellipse cx="150" cy="290" rx="90" ry="10" fill="#000" opacity=".15"/>
<path d="M60 130 L8 70 L92 104 Z" fill="{body}" {S()}/>
<path d="M240 130 L292 70 L208 104 Z" fill="{body}" {S()}/>
<path d="M44 92 L80 112" stroke="{belly}" stroke-width="8" stroke-linecap="round"/>
<path d="M256 92 L220 112" stroke="{belly}" stroke-width="8" stroke-linecap="round"/>
<ellipse cx="110" cy="276" rx="26" ry="14" fill="{dark}" {S()}/>
<ellipse cx="190" cy="276" rx="26" ry="14" fill="{dark}" {S()}/>
<ellipse cx="150" cy="170" rx="100" ry="105" fill="{body}" {S()}/>
<ellipse cx="150" cy="215" rx="62" ry="52" fill="{belly}"/>
<circle cx="88" cy="110" r="9" fill="{dark}"/><circle cx="210" cy="96" r="12" fill="{dark}"/>
<circle cx="225" cy="130" r="6" fill="{dark}"/>
<path d="M58 190 Q32 200 40 226" fill="none" {S(10)}/><path d="M58 190 Q32 200 40 226" fill="none" stroke="{body}" stroke-width="5" stroke-linecap="round"/>
<path d="M242 190 Q268 200 260 226" fill="none" {S(10)}/><path d="M242 190 Q268 200 260 226" fill="none" stroke="{body}" stroke-width="5" stroke-linecap="round"/>
{eyes(150, 140, 36, 22, mode, look=(0.3, 0.2))}
{blush(150, 172, 62, 13)}
{m}{zz}''')


def goblin_b(mode="open"):
    body, belly, dark = PURPLES["b"]
    if mode == "closed":
        eye = f'<path d="M122 130 Q150 150 178 130" fill="none" {S(6)}/>'
        mouth = smile(150, 196, 14, 6)
    else:
        eye = (f'<circle cx="150" cy="128" r="36" fill="#fff" {S()}/>'
               f'<circle cx="156" cy="132" r="19" fill="{OL}"/><circle cx="148" cy="122" r="7" fill="#fff"/>')
        mouth = (f'<path d="M118 188 Q150 222 182 188 Z" fill="#5a1f4a" {S(5)}/>'
                 f'<path d="M150 200 Q160 230 172 214 Q170 202 160 199 Z" fill="#ff7aa8" {S(4)}/>')
    return svg(300, 300, f'''
<ellipse cx="150" cy="290" rx="75" ry="9" fill="#000" opacity=".15"/>
<path d="M104 74 Q92 30 70 24 Q96 52 92 84 Z" fill="#e7d9ff" {S(5)}/>
<path d="M196 74 Q208 30 230 24 Q204 52 208 84 Z" fill="#e7d9ff" {S(5)}/>
<ellipse cx="118" cy="280" rx="22" ry="12" fill="{dark}" {S()}/>
<ellipse cx="182" cy="280" rx="22" ry="12" fill="{dark}" {S()}/>
<path d="M150 56 C220 56 236 140 236 200 C236 262 196 278 150 278 C104 278 64 262 64 200 C64 140 80 56 150 56 Z" fill="{body}" {S()}/>
<path d="M150 170 C190 170 206 210 200 240 C194 262 106 262 100 240 C94 210 110 170 150 170 Z" fill="{belly}"/>
<path d="M66 196 L36 176" {S(10)}/><path d="M66 196 L36 176" stroke="{body}" stroke-width="4" stroke-linecap="round"/>
<path d="M234 196 L264 176" {S(10)}/><path d="M234 196 L264 176" stroke="{body}" stroke-width="4" stroke-linecap="round"/>
<circle cx="96" cy="150" r="7" fill="{dark}"/><circle cx="206" cy="232" r="9" fill="{dark}"/>
{eye}{blush(150, 172, 54, 12)}{mouth}''')


def goblin_c(mode="open"):
    body, belly, dark = PURPLES["c"]
    pts = []
    for i in range(36):
        a = i / 36 * math.tau
        r = 108 if i % 2 == 0 else 92
        pts.append(f"{150+math.cos(a)*r:.1f},{165+math.sin(a)*r*0.95:.1f}")
    mouth = (f'<path d="M126 196 Q150 214 174 196" fill="none" {S(5)}/>'
             f'<path d="M136 200 L140 210 L146 202" fill="#fff" stroke="{OL}" stroke-width="3" stroke-linejoin="round"/>'
             f'<path d="M154 202 L160 210 L164 200" fill="#fff" stroke="{OL}" stroke-width="3" stroke-linejoin="round"/>'
             if mode != "closed" else smile(150, 200, 14, 6))
    return svg(300, 300, f'''
<ellipse cx="150" cy="290" rx="80" ry="9" fill="#000" opacity=".15"/>
<path d="M150 70 Q140 40 160 18" fill="none" {S(6)}/>
<circle cx="162" cy="18" r="13" fill="#ff7ac0" {S(5)}/>
<polygon points="{' '.join(pts)}" fill="{body}" {S()}/>
<circle cx="150" cy="168" r="66" fill="{belly}" opacity=".6"/>
<ellipse cx="112" cy="272" rx="20" ry="11" fill="{dark}" {S()}/>
<ellipse cx="188" cy="272" rx="20" ry="11" fill="{dark}" {S()}/>
{eyes(150, 150, 30, 18, mode, look=(-0.3, 0.1))}
{blush(150, 182, 52, 11)}{mouth}''')


def goblin_sneaky(mode="open"):
    body, belly, dark = PURPLES["sneaky"]
    if mode == "closed":
        face = (f'<path d="M80 112 Q150 96 220 112 L216 140 Q150 126 84 140 Z" fill="#3c2357" {S(4)}/>'
                f'<path d="M104 126 Q116 134 128 126" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round"/>'
                f'<path d="M172 126 Q184 134 196 126" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round"/>'
                + smile(150, 176, 12, 5))
    else:
        face = (f'<path d="M80 112 Q150 96 220 112 L216 146 Q150 130 84 146 Z" fill="#3c2357" {S(4)}/>'
                f'<ellipse cx="116" cy="126" rx="15" ry="12" fill="#fff"/><circle cx="122" cy="127" r="7" fill="{OL}"/>'
                f'<ellipse cx="184" cy="126" rx="15" ry="12" fill="#fff"/><circle cx="190" cy="127" r="7" fill="{OL}"/>'
                f'<path d="M124 172 Q150 190 182 166" fill="none" {S(5)}/>')
    return svg(300, 300, f'''
<ellipse cx="150" cy="290" rx="60" ry="8" fill="#000" opacity=".15"/>
<path d="M90 96 L40 60 L100 76 Z" fill="{body}" {S(5)}/>
<path d="M210 96 L260 60 L200 76 Z" fill="{body}" {S(5)}/>
<path d="M126 250 L112 284" {S(9)}/><path d="M174 250 L188 284" {S(9)}/>
<path d="M150 60 C210 60 224 120 220 170 C216 230 190 256 150 256 C110 256 84 230 80 170 C76 120 90 60 150 60 Z" fill="{body}" {S()}/>
<ellipse cx="150" cy="208" rx="40" ry="34" fill="{belly}"/>
<path d="M86 190 Q60 170 70 150" fill="none" {S(8)}/>
<path d="M214 190 Q244 178 238 150" fill="none" {S(8)}/>
<path d="M150 62 Q160 40 176 46" fill="none" {S(5)}/>
{face}''')


def goblin_big(mode="open"):
    body, belly, dark = PURPLES["big"]
    if mode == "closed":
        brows = ""
        mouth = smile(200, 250, 24, 9, sw=7)
    elif mode == "dizzy":
        brows = ""
        mouth = f'<ellipse cx="200" cy="258" rx="26" ry="20" fill="#5a1f4a" {S(6)}/>'
    elif mode == "squint":
        brows = ""
        mouth = (f'<path d="M150 246 Q200 236 250 246 Q244 280 200 282 Q156 280 150 246 Z" fill="#5a1f4a" {S(6)}/>'
                 f'<path d="M160 248 L240 248 L236 260 L164 260 Z" fill="#fff" {S(3)}/>')
    else:
        brows = (f'<path d="M126 130 Q150 116 176 132" fill="none" {S(9)}/>'
                 f'<path d="M224 132 Q250 116 274 130" fill="none" {S(9)}/>')
        mouth = (f'<path d="M136 236 Q200 300 264 236 Q200 256 136 236 Z" fill="#5a1f4a" {S(6)}/>'
                 f'<path d="M168 244 L178 268 L190 248 Z" fill="#fff" stroke="{OL}" stroke-width="4" stroke-linejoin="round"/>'
                 f'<path d="M210 248 L222 268 L232 244 Z" fill="#fff" stroke="{OL}" stroke-width="4" stroke-linejoin="round"/>')
    bubble = ""
    if mode == "open":
        bubble = (f'<circle cx="300" cy="240" r="30" fill="#ff9ccd" {S(5)}/>'
                  f'<ellipse cx="290" cy="228" rx="9" ry="6" fill="#fff" opacity=".8"/>')
    return svg(400, 400, f'''
<ellipse cx="200" cy="388" rx="150" ry="14" fill="#000" opacity=".15"/>
<path d="M120 96 Q96 30 60 20 Q96 64 92 116 Z" fill="#efe2ff" {S()}/>
<path d="M280 96 Q304 30 340 20 Q304 64 308 116 Z" fill="#efe2ff" {S()}/>
<ellipse cx="138" cy="372" rx="44" ry="20" fill="{dark}" {S()}/>
<ellipse cx="262" cy="372" rx="44" ry="20" fill="{dark}" {S()}/>
<path d="M200 70 C300 70 352 150 352 250 C352 340 290 372 200 372 C110 372 48 340 48 250 C48 150 100 70 200 70 Z" fill="{body}" {S(7)}/>
<path d="M200 230 C270 230 300 280 290 320 C280 356 120 356 110 320 C100 280 130 230 200 230 Z" fill="{belly}"/>
<path d="M54 240 Q14 250 22 300 Q30 312 46 300" fill="{body}" {S(7)}/>
<path d="M346 240 Q386 250 378 300 Q370 312 354 300" fill="{body}" {S(7)}/>
<circle cx="110" cy="170" r="12" fill="{dark}"/><circle cx="300" cy="190" r="16" fill="{dark}"/><circle cx="280" cy="140" r="8" fill="{dark}"/>
<path d="M150 82 L160 40 L182 66 L200 30 L218 66 L240 40 L250 82 Z" fill="#ffd23f" {S(6)}/>
<circle cx="200" cy="52" r="7" fill="#ff7ac0" {S(3)}/>
{eyes(200, 170, 50, 30, mode, look=(0, 0.25), w=7)}
{brows}{blush(200, 214, 92, 18)}{mouth}{bubble}''')


# ---------------------------------------------------------------- buddy
# "Sparkle", a little tooth hero with a blue cape and a toothbrush sword.

TOOTH = ("M80 110 C76 56 124 44 150 64 C176 44 224 56 220 110 C220 160 212 196 206 236 "
         "C200 286 186 304 174 304 C160 304 160 268 150 258 C140 268 140 304 126 304 "
         "C114 304 100 286 94 236 C88 196 80 160 80 110 Z")


def toothbrush(x, y, angle, scale=1.0, color="#ff5c8a"):
    return (f'<g transform="translate({x} {y}) rotate({angle}) scale({scale})">'
            f'<rect x="-8" y="-10" width="16" height="120" rx="8" fill="{color}" {S(5)}/>'
            f'<rect x="-11" y="-58" width="22" height="52" rx="6" fill="#fff" {S(5)}/>'
            f'<path d="M-11 -48 L-24 -48 M-11 -36 L-24 -36 M-11 -24 L-24 -24 M-11 -12 L-24 -12" '
            f'stroke="#5ad1ff" stroke-width="7" stroke-linecap="round"/>'
            f'<rect x="-4" y="40" width="8" height="40" rx="4" fill="#fff" opacity=".5"/>'
            f'</g>')


def buddy(pose="ready", cape_color="#3a86ff", brush_color="#ff5c8a", layer=None):
    """Whole buddy, or one layer of it: "cape", "body" (no cape/brush) or "brush"."""
    cape = (f'<path d="M96 120 C60 170 50 250 44 296 Q150 320 256 296 C250 250 240 170 204 120 Z" '
            f'fill="{cape_color}" {S()}/>'
            f'<path d="M120 286 Q150 300 180 286" fill="none" stroke="#ffffff" stroke-opacity=".45" stroke-width="6" stroke-linecap="round"/>')
    brush = ""
    shine = '<path d="M104 92 Q110 70 132 68" fill="none" stroke="#fff" stroke-width="10" stroke-linecap="round" opacity=".9"/>'
    body = f'<path d="{TOOTH}" fill="#fdfbff" {S()}/>' + \
        f'<path d="M96 200 C110 230 190 230 204 200" fill="none" stroke="#e3dcf2" stroke-width="10" stroke-linecap="round"/>'
    scarf = f'<path d="M100 172 Q150 196 200 172 L198 188 Q150 210 102 188 Z" fill="#ff5c8a" {S(5)}/>'
    extra = ""
    if pose == "ready":
        face = eyes(150, 122, 28, 16, look=(0.2, 0)) + blush(150, 150, 46, 11) + smile(150, 146, 18, 10, fill="#ff7aa8")
        arms = (f'<path d="M86 178 Q60 200 52 226" fill="none" {S(12)}/><path d="M86 178 Q60 200 52 226" fill="none" stroke="#fdfbff" stroke-width="6" stroke-linecap="round"/>'
                f'<path d="M214 176 Q240 160 252 136" fill="none" {S(12)}/><path d="M214 176 Q240 160 252 136" fill="none" stroke="#fdfbff" stroke-width="6" stroke-linecap="round"/>')
        brush = toothbrush(256, 136, 20, color=brush_color)
    elif pose == "cheer":
        face = eyes(150, 122, 28, 16, "closed") + blush(150, 148, 46, 12) + smile(150, 142, 22, 13, fill="#ff7aa8")
        arms = (f'<path d="M88 170 Q60 140 56 104" fill="none" {S(12)}/><path d="M88 170 Q60 140 56 104" fill="none" stroke="#fdfbff" stroke-width="6" stroke-linecap="round"/>'
                f'<path d="M212 170 Q240 140 244 104" fill="none" {S(12)}/><path d="M212 170 Q240 140 244 104" fill="none" stroke="#fdfbff" stroke-width="6" stroke-linecap="round"/>')
        brush = toothbrush(246, 104, -10, color=brush_color)
        extra = sparkle_shape(48, 70, 16) + sparkle_shape(268, 60, 12)
    elif pose == "wait":
        face = eyes(150, 122, 28, 16, look=(-0.6, -0.3)) + blush(150, 150, 46, 11) + \
            f'<ellipse cx="150" cy="152" rx="8" ry="7" fill="#ff7aa8" {S(4)}/>'
        arms = (f'<path d="M88 178 Q70 210 80 236" fill="none" {S(12)}/><path d="M88 178 Q70 210 80 236" fill="none" stroke="#fdfbff" stroke-width="6" stroke-linecap="round"/>'
                f'<path d="M212 178 Q230 210 220 236" fill="none" {S(12)}/><path d="M212 178 Q230 210 220 236" fill="none" stroke="#fdfbff" stroke-width="6" stroke-linecap="round"/>')
        brush = toothbrush(234, 250, 160, 0.8, color=brush_color)
    elif pose == "swish":
        face = (eyes(150, 112, 28, 14, "closed") +
                f'<circle cx="104" cy="150" r="30" fill="#fdfbff" {S(5)}/><circle cx="196" cy="150" r="30" fill="#fdfbff" {S(5)}/>'
                + blush(150, 150, 46, 14, op=0.85) +
                f'<ellipse cx="150" cy="156" rx="9" ry="7" fill="#ff7aa8" {S(4)}/>')
        arms = (f'<path d="M88 178 Q64 190 64 214" fill="none" {S(12)}/><path d="M88 178 Q64 190 64 214" fill="none" stroke="#fdfbff" stroke-width="6" stroke-linecap="round"/>'
                f'<path d="M212 178 Q236 190 236 214" fill="none" {S(12)}/><path d="M212 178 Q236 190 236 214" fill="none" stroke="#fdfbff" stroke-width="6" stroke-linecap="round"/>')
        extra = (f'<path d="M30 140 Q20 150 30 160 M18 130 Q4 150 18 170" fill="none" stroke="#5ad1ff" stroke-width="5" stroke-linecap="round"/>'
                 f'<path d="M270 140 Q280 150 270 160 M282 130 Q296 150 282 170" fill="none" stroke="#5ad1ff" stroke-width="5" stroke-linecap="round"/>')
    else:  # sleep
        face = eyes(150, 126, 28, 15, "closed") + blush(150, 150, 46, 11) + smile(150, 152, 8, 4)
        arms = (f'<path d="M88 180 Q72 206 90 226" fill="none" {S(12)}/><path d="M88 180 Q72 206 90 226" fill="none" stroke="#fdfbff" stroke-width="6" stroke-linecap="round"/>'
                f'<path d="M212 180 Q228 206 210 226" fill="none" {S(12)}/><path d="M212 180 Q228 206 210 226" fill="none" stroke="#fdfbff" stroke-width="6" stroke-linecap="round"/>')
        extra = (f'<path d="M84 92 C96 30 180 10 236 56 Q250 86 262 110 Q236 70 216 80 C190 66 120 70 84 92 Z" fill="#3a86ff" {S(5)}/>'
                 f'<path d="M84 92 Q150 60 220 82" fill="none" stroke="#fff" stroke-width="12" stroke-linecap="round"/>'
                 f'<circle cx="266" cy="114" r="14" fill="#fff" {S(4)}/>')
    shadow = '<ellipse cx="150" cy="310" rx="90" ry="9" fill="#000" opacity=".15"/>'
    if layer == "cape":
        return svg(300, 320, shadow + cape)
    if layer == "body":
        return svg(300, 320, f'{arms}{body}{shine}{scarf}{face}{extra}')
    if layer == "brush":
        return svg(300, 320, brush)
    return svg(300, 320, f'{shadow}{cape}{arms}{body}{shine}{scarf}{face}{brush}{extra}')


def sparkle_shape(x, y, r, color="#ffd23f"):
    return (f'<path d="M{x} {y-r} Q{x+r*0.2} {y-r*0.2} {x+r} {y} Q{x+r*0.2} {y+r*0.2} {x} {y+r} '
            f'Q{x-r*0.2} {y+r*0.2} {x-r} {y} Q{x-r*0.2} {y-r*0.2} {x} {y-r} Z" fill="{color}" '
            f'stroke="{OL}" stroke-width="{max(2, r/5):.1f}" stroke-linejoin="round"/>')


# ---------------------------------------------------------------- worlds
# Portrait 900x1600 backgrounds. The middle third is kept calm because the
# mirror sits there; detail lives at the top and bottom.

def grad(id_, stops, vertical=True):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    xy = 'x1="0" y1="0" x2="0" y2="1"' if vertical else 'x1="0" y1="0" x2="1" y2="0"'
    return f'<linearGradient id="{id_}" {xy}>{s}</linearGradient>'


def stars(rng, n, ymax):
    out = []
    for _ in range(n):
        x, y, r = rng.uniform(10, 890), rng.uniform(10, ymax), rng.uniform(2, 5)
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="#fff8d6" opacity="{rng.uniform(.5, 1):.2f}"/>')
    return "".join(out)


def cloud(x, y, s, color="#fff", op=1):
    return (f'<g opacity="{op}" transform="translate({x} {y}) scale({s})">'
            f'<ellipse cx="0" cy="0" rx="70" ry="34" fill="{color}"/><ellipse cx="-50" cy="10" rx="46" ry="26" fill="{color}"/>'
            f'<ellipse cx="54" cy="10" rx="50" ry="28" fill="{color}"/><ellipse cx="10" cy="-24" rx="44" ry="32" fill="{color}"/></g>')


def sky(night, day_stops, night_stops, rng):
    d = grad("sky", night_stops if night else day_stops)
    b = '<rect width="900" height="1600" fill="url(#sky)"/>'
    if night:
        b += stars(rng, 70, 800)
        b += ('<circle cx="720" cy="190" r="74" fill="#fff4c2"/><circle cx="750" cy="168" r="70" fill="url(#sky)"/>'
              '<circle cx="720" cy="190" r="110" fill="#fff4c2" opacity=".08"/>')
    else:
        b += ('<circle cx="720" cy="200" r="130" fill="#fff1a8" opacity=".35"/>'
              '<circle cx="720" cy="200" r="86" fill="#ffe066"/>')
        b += cloud(200, 170, 1.2, op=.9) + cloud(560, 330, 0.8, op=.8) + cloud(120, 520, 0.7, op=.6)
    return d, b


def bg_street(night):
    rng = random.Random(1)
    d, b = sky(night, [(0, "#7cc8ff"), (.55, "#bfe6ff"), (1, "#ffe3b8")],
               [(0, "#141a44"), (.6, "#2c2f6e"), (1, "#4a3d7a")], rng)
    house_cols = ["#ff8fa3", "#ffd166", "#7bdff2", "#b8f2a6", "#cdb4ff", "#ffb4a2"]
    roof_cols = ["#e5487a", "#f08c2b", "#3a86ff", "#2fb36d", "#8f5bd6", "#d9534f"]
    x = -40
    i = 0
    while x < 940:
        w = rng.choice([150, 170, 190])
        h = rng.choice([230, 270, 300])
        base = 1130
        c = house_cols[i % 6]
        r = roof_cols[i % 6]
        if night:
            c = shade(c, 0.45)
            r = shade(r, 0.45)
        b += f'<rect x="{x}" y="{base-h}" width="{w}" height="{h}" fill="{c}" {S(5)}/>'
        b += f'<path d="M{x-14} {base-h} L{x+w/2} {base-h-90} L{x+w+14} {base-h} Z" fill="{r}" {S(5)}/>'
        win = "#ffe27a" if night else "#e8f7ff"
        for wy in (base - h + 40, base - h + 130):
            if wy > base - 90:
                continue
            for wx in (x + 26, x + w - 66):
                b += f'<rect x="{wx}" y="{wy}" width="40" height="46" rx="6" fill="{win}" {S(4)}/>'
        b += f'<rect x="{x+w/2-24}" y="{base-86}" width="48" height="86" rx="18" fill="{shade(r, 0.8)}" {S(4)}/>'
        x += w + 20
        i += 1
    # hedges, sidewalk, road
    hedge = "#2f7d4a" if night else "#5cc46a"
    for hx in range(-20, 940, 110):
        b += f'<ellipse cx="{hx}" cy="1140" rx="70" ry="40" fill="{hedge}" {S(5)}/>'
    b += f'<rect x="0" y="1150" width="900" height="120" fill="{"#6d6a8c" if night else "#d9d4e8"}" {S(5)}/>'
    for sx in range(0, 900, 100):
        b += f'<line x1="{sx}" y1="1150" x2="{sx-30}" y2="1270" stroke="{OL}" stroke-width="3" opacity=".3"/>'
    b += f'<rect x="0" y="1270" width="900" height="330" fill="{"#2e2c45" if night else "#5b5a73"}"/>'
    for sx in range(20, 900, 180):
        b += f'<rect x="{sx}" y="1420" width="100" height="18" rx="9" fill="#ffd23f" opacity="{.5 if night else .9}"/>'
    for lx in (120, 620):
        b += f'<rect x="{lx}" y="840" width="16" height="320" fill="#4b4766" {S(4)}/>'
        b += f'<path d="M{lx-26} 850 Q{lx+8} 800 {lx+42} 850 Z" fill="#4b4766" {S(4)}/>'
        if night:
            b += f'<circle cx="{lx+8}" cy="860" r="80" fill="#ffe27a" opacity=".2"/>'
        b += f'<circle cx="{lx+8}" cy="858" r="14" fill="{"#ffe27a" if night else "#fff6c8"}" {S(3)}/>'
    return svg(900, 1600, b, d)


def bg_forest(night):
    rng = random.Random(2)
    d, b = sky(night, [(0, "#8fd8ff"), (.6, "#d4f3ff"), (1, "#fff0c4")],
               [(0, "#0f1d3a"), (.6, "#1d3a5c"), (1, "#2a4a5a")], rng)
    hills = [("#9be08a", 980, 160), ("#6cc76a", 1060, 140), ("#44a85a", 1150, 120)]
    for col, y, amp in hills:
        c = shade(col, 0.4) if night else col
        p = f"M0 1600 L0 {y}"
        for xx in range(0, 960, 60):
            p += f" L{xx} {y - amp*0.5*math.sin(xx/140 + y) - 30:.0f}"
        p += " L900 1600 Z"
        b += f'<path d="{p}" fill="{c}" {S(5)}/>'
    for i, (tx, ty, s) in enumerate([(70, 1000, 1.1), (210, 960, .8), (780, 990, 1.2), (650, 1010, .9),
                                     (360, 1040, .7), (520, 1050, .75), (880, 1080, 1.0), (20, 1120, .9)]):
        trunk = shade("#8b5a3c", 0.5) if night else "#8b5a3c"
        b += f'<rect x="{tx-12*s}" y="{ty}" width="{24*s}" height="{70*s}" fill="{trunk}" {S(4)}/>'
        for k, (w, h) in enumerate([(120, 110), (100, 100), (76, 90)]):
            col = ["#2e9e5b", "#36b267", "#45c476"][k]
            col = shade(col, 0.45) if night else col
            yy = ty - k * 70 * s
            b += (f'<path d="M{tx-w*s} {yy+10*s} L{tx} {yy-h*s} L{tx+w*s} {yy+10*s} Q{tx} {yy+30*s} {tx-w*s} {yy+10*s} Z" '
                  f'fill="{col}" {S(5)}/>')
    # path and mushrooms
    path_col = "#7a6450" if night else "#e8c99b"
    b += f'<path d="M330 1600 Q420 1400 450 1260 Q470 1200 520 1180 Q500 1260 560 1400 Q620 1520 640 1600 Z" fill="{path_col}" {S(5)}/>'
    for mx, my, s in [(130, 1360, 1), (760, 1330, .8), (230, 1480, .7), (700, 1500, 1.1)]:
        cap = shade("#ff5c5c", 0.5) if night else "#ff5c5c"
        b += f'<rect x="{mx-14*s}" y="{my}" width="{28*s}" height="{40*s}" rx="8" fill="#fff3e0" {S(4)}/>'
        b += f'<path d="M{mx-50*s} {my+4} Q{mx} {my-70*s} {mx+50*s} {my+4} Z" fill="{cap}" {S(5)}/>'
        b += f'<circle cx="{mx-16*s}" cy="{my-20*s}" r="{8*s}" fill="#fff"/><circle cx="{mx+18*s}" cy="{my-14*s}" r="{6*s}" fill="#fff"/>'
    if night:
        for _ in range(26):
            fx, fy = rng.uniform(40, 860), rng.uniform(900, 1550)
            b += f'<circle cx="{fx:.0f}" cy="{fy:.0f}" r="14" fill="#fff59a" opacity=".18"/><circle cx="{fx:.0f}" cy="{fy:.0f}" r="5" fill="#fff59a"/>'
    else:
        for _ in range(14):
            fx, fy = rng.uniform(40, 860), rng.uniform(1250, 1580)
            col = rng.choice(["#ff8fb8", "#ffd23f", "#fff", "#b39bff"])
            b += f'<circle cx="{fx:.0f}" cy="{fy:.0f}" r="9" fill="{col}" {S(3)}/><circle cx="{fx:.0f}" cy="{fy:.0f}" r="3" fill="#ffb703"/>'
    return svg(900, 1600, b, d)


def bg_city(night):
    rng = random.Random(3)
    d, b = sky(night, [(0, "#6fb7ff"), (.6, "#b6dcff"), (1, "#ffd6e8")],
               [(0, "#0d1033"), (.6, "#24245e"), (1, "#3d2f6b")], rng)
    # far skyline
    x = -20
    while x < 920:
        w = rng.choice([70, 90, 110])
        h = rng.randint(320, 560)
        col = "#2d3266" if night else "#a9b8e8"
        b += f'<rect x="{x}" y="{1150-h}" width="{w}" height="{h}" fill="{col}"/>'
        x += w + 6
    # near buildings
    cols = ["#ff8fa3", "#7bdff2", "#ffd166", "#cdb4ff", "#95e1a3", "#ffb4a2"]
    x = -30
    i = 0
    while x < 930:
        w = rng.choice([140, 160, 180])
        h = rng.randint(260, 460)
        c = shade(cols[i % 6], 0.42) if night else cols[i % 6]
        top = 1180 - h
        b += f'<rect x="{x}" y="{top}" width="{w}" height="{h}" fill="{c}" {S(5)}/>'
        if i % 3 == 1:
            b += f'<rect x="{x+w/2-6}" y="{top-60}" width="12" height="60" fill="#4b4766" {S(3)}/>'
            b += f'<circle cx="{x+w/2}" cy="{top-64}" r="10" fill="#ff5c5c" {S(3)}/>'
        for wy in range(top + 30, 1100, 64):
            for wx in range(int(x) + 20, int(x + w) - 30, 44):
                lit = rng.random() < (0.55 if night else 0.0)
                wc = "#ffe27a" if lit else ("#3a3a6a" if night else "#eef8ff")
                b += f'<rect x="{wx}" y="{wy}" width="26" height="34" rx="4" fill="{wc}" stroke="{OL}" stroke-width="3"/>'
        x += w + 14
        i += 1
    # park strip with round trees, road, crossing
    g = "#2f6b48" if night else "#7fd67a"
    b += f'<rect x="0" y="1180" width="900" height="80" fill="{g}" {S(5)}/>'
    for tx in (90, 330, 590, 830):
        b += f'<rect x="{tx-8}" y="1140" width="16" height="60" fill="#8b5a3c" {S(3)}/>'
        b += f'<circle cx="{tx}" cy="1120" r="44" fill="{shade("#3fb56b", .5) if night else "#3fb56b"}" {S(5)}/>'
    b += f'<rect x="0" y="1260" width="900" height="340" fill="{"#262640" if night else "#56557a"}"/>'
    for zx in range(120, 800, 80):
        b += f'<rect x="{zx}" y="1300" width="44" height="140" rx="6" fill="#fff" opacity="{.35 if night else .85}"/>'
    return svg(900, 1600, b, d)


def shade(hex_color, f):
    h = hex_color.lstrip("#")
    r, g, bb = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    r, g, bb = (int(v * f + 30 * (1 - f) * 0.5) for v in (r, g, bb))
    return f"#{min(r,255):02x}{min(g,255):02x}{min(bb,255):02x}"


def bg_home():
    rng = random.Random(4)
    d = grad("sky", [(0, "#b388ff"), (.5, "#ff9ccd"), (1, "#ffd6a5")])
    b = '<rect width="900" height="1600" fill="url(#sky)"/>'
    for _ in range(40):
        x, y = rng.uniform(0, 900), rng.uniform(0, 1600)
        b += sparkle_shape(x, y, rng.uniform(6, 16), "#fff6c8").replace(f'stroke="{OL}"', 'stroke="none"')
    b += cloud(150, 1450, 1.6, "#fff", .7) + cloud(760, 1520, 1.4, "#fff", .7) + cloud(450, 1580, 1.8, "#fff", .8)
    return svg(900, 1600, b, d)


# ---------------------------------------------------------------- mouth guide

MW, MH = 400, 320


def teeth_layout():
    top, bot = [], []
    for i in range(10):
        t = (i - 4.5) / 4.5
        x = 200 + t * 132
        w = 30 - 9 * abs(t)
        h = 50 - 18 * abs(t)
        ty = 70 + 30 * t * t
        top.append((x, ty, w, h))
        by = 252 - 30 * t * t
        bot.append((x, by - h, w, h))
    return top, bot


ZONES = [  # id, row, teeth indexes (screen-left = his left, like a mirror)
    ("top_left", "top", [0, 1, 2]),
    ("top_front", "top", [3, 4, 5, 6]),
    ("top_right", "top", [7, 8, 9]),
    ("bottom_right", "bot", [7, 8, 9]),
    ("bottom_front", "bot", [3, 4, 5, 6]),
    ("bottom_left", "bot", [0, 1, 2]),
]

def _gap_order():
    """All 18 gaps (9 per row), front teeth first, then working outwards."""
    order = [("top", 4), ("bot", 4)]
    for d in range(1, 5):
        for row in ("top", "bot"):
            order += [(row, 4 - d), (row, 4 + d)]
    return [(f"gap_{row}_{i}", row, i) for row, i in order]


GAPS = _gap_order()


def mouth():
    top, bot = teeth_layout()
    b = (f'<path d="M20 160 C20 40 120 18 200 30 C280 18 380 40 380 160 C380 280 280 302 200 296 C120 302 20 280 20 160 Z" fill="#ff6f91" {S(7)}/>'
         f'<path d="M48 160 C48 70 130 52 200 60 C270 52 352 70 352 160 C352 250 270 270 200 266 C130 270 48 250 48 160 Z" fill="#6b1f44" {S(5)}/>'
         f'<path d="M110 240 C120 190 280 190 290 240 C270 262 130 262 110 240 Z" fill="#ff8fab" {S(4)}/>'
         f'<path d="M200 205 L200 238" stroke="#e86a8e" stroke-width="4" stroke-linecap="round"/>'
         f'<path d="M58 120 C70 70 150 56 200 64 C250 56 330 70 342 120 C300 98 100 98 58 120 Z" fill="#ff9db5" {S(4)}/>'
         f'<path d="M58 200 C100 226 300 226 342 200 C330 254 250 268 200 262 C150 268 70 254 58 200 Z" fill="#ff9db5" {S(4)}/>')
    for x, y, w, h in top:
        b += f'<rect x="{x-w/2:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{w*0.35:.1f}" fill="#fffdf6" {S(4)}/>'
    for x, y, w, h in bot:
        b += f'<rect x="{x-w/2:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{w*0.35:.1f}" fill="#fffdf6" {S(4)}/>'
    write("guide/mouth.svg", svg(MW, MH, b))

    layout = {"w": MW, "h": MH, "zones": {}, "gaps": {}}
    for zid, row, idx in ZONES:
        teeth = top if row == "top" else bot
        x0 = min(teeth[i][0] - teeth[i][2] / 2 for i in idx) - 9
        x1 = max(teeth[i][0] + teeth[i][2] / 2 for i in idx) + 9
        y0 = min(teeth[i][1] for i in idx) - 9
        y1 = max(teeth[i][1] + teeth[i][3] for i in idx) + 9
        hl = (f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1-x0:.1f}" height="{y1-y0:.1f}" rx="18" '
              f'fill="#fff06a" fill-opacity=".45" stroke="#ffd23f" stroke-width="9"/>'
              f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1-x0:.1f}" height="{y1-y0:.1f}" rx="18" '
              f'fill="none" stroke="#fff" stroke-width="3" stroke-dasharray="10 12"/>')
        hl += sparkle_shape(x1 - 4, y0 + 2, 12) + sparkle_shape(x0 + 6, y1 - 4, 8)
        write(f"guide/{zid}.svg", svg(MW, MH, hl))
        cy = (y0 + y1) / 2
        layout["zones"][zid] = {"x": (x0 + x1) / 2 / MW, "y": cy / MH,
                                "brushY": (y0 - 26 if row == "top" else y1 + 26) / MH}
    for gid, row, i in GAPS:
        teeth = top if row == "top" else bot
        a, c = teeth[i], teeth[i + 1]
        gx = (a[0] + a[2] / 2 + c[0] - c[2] / 2) / 2
        gy = (a[1] + c[1]) / 2 + (a[3] + c[3]) / 4
        hl = (f'<ellipse cx="{gx:.1f}" cy="{gy:.1f}" rx="15" ry="32" fill="#7cf5ff" fill-opacity=".45" stroke="#2ad1ff" stroke-width="7"/>'
              f'<line x1="{gx:.1f}" y1="{gy-30:.1f}" x2="{gx:.1f}" y2="{gy+30:.1f}" stroke="#fff" stroke-width="4" stroke-dasharray="6 6"/>')
        write(f"guide/{gid}.svg", svg(MW, MH, hl))
        layout["gaps"][gid] = {"x": gx / MW, "y": gy / MH, "row": row}
    layout["gapOrder"] = [g[0] for g in GAPS]
    with open(os.path.join(OUT, "guide", "layout.json"), "w") as f:
        json.dump(layout, f, indent=1)


# ---------------------------------------------------------------- icons (200x200)

def floss_pick(angle=0):
    return (f'<g transform="rotate({angle} 100 100)">'
            f'<path d="M92 92 L108 92 L106 176 Q100 192 94 176 Z" fill="#5ad1ff" {S(6)}/>'
            f'<path d="M58 22 Q52 84 100 100 Q148 84 142 22 L126 22 Q128 70 100 80 Q72 70 74 22 Z" fill="#5ad1ff" {S(6)}/>'
            f'<line x1="66" y1="26" x2="134" y2="26" stroke="#fff" stroke-width="5" stroke-linecap="round"/>'
            f'<path d="M100 110 L100 160" stroke="#fff" stroke-width="5" stroke-linecap="round" opacity=".6"/>'
            f'</g>')


def icon_files():
    I = {}
    I["brush"] = svg(200, 200, toothbrush(100, 110, 35, 1.1))
    I["pick"] = svg(200, 200, floss_pick(0))
    I["floss"] = svg(200, 200,
                     f'<rect x="40" y="70" width="52" height="96" rx="20" fill="#fffdf6" {S(6)}/>'
                     f'<rect x="108" y="70" width="52" height="96" rx="20" fill="#fffdf6" {S(6)}/>'
                     f'<path d="M30 70 Q100 40 170 70" fill="#ff9db5" {S(6)}/>'
                     f'<g transform="translate(50 2) scale(.5)">{floss_pick(0)}</g>'
                     f'<line x1="100" y1="44" x2="100" y2="160" stroke="#2ad1ff" stroke-width="5"/>')
    I["gift"] = svg(200, 200,
                    f'<rect x="34" y="84" width="132" height="94" rx="10" fill="#ff5c8a" {S(6)}/>'
                    f'<rect x="24" y="60" width="152" height="36" rx="10" fill="#ff8fb8" {S(6)}/>'
                    f'<rect x="88" y="60" width="24" height="118" fill="#ffd23f" {S(5)}/>'
                    f'<path d="M100 60 C70 20 40 40 60 60 Z M100 60 C130 20 160 40 140 60 Z" fill="#ffd23f" {S(5)}/>')
    I["moon"] = svg(200, 200,
                    f'<path d="M126 26 A76 76 0 1 0 176 132 A60 60 0 1 1 126 26 Z" fill="#ffe27a" {S(6)}/>'
                    + eyes(96, 110, 18, 8, "closed", w=4) + smile(96, 126, 10, 5, sw=4)
                    + sparkle_shape(160, 40, 12, "#fff6c8"))
    I["cup"] = svg(200, 200,
                   f'<path d="M50 50 L150 50 L136 176 Q100 186 64 176 Z" fill="#c8f1ff" {S(6)}/>'
                   f'<path d="M58 90 L142 90 L134 170 Q100 178 66 170 Z" fill="#5ad1ff"/>'
                   f'<path d="M50 50 L150 50 L136 176 Q100 186 64 176 Z" fill="none" {S(6)}/>'
                   f'<path d="M72 64 L78 150" stroke="#fff" stroke-width="7" stroke-linecap="round" opacity=".8"/>')
    I["swish"] = svg(200, 200,
                     f'<circle cx="100" cy="104" r="70" fill="#fdfbff" {S(6)}/>'
                     f'<circle cx="54" cy="120" r="26" fill="#fdfbff" {S(5)}/><circle cx="146" cy="120" r="26" fill="#fdfbff" {S(5)}/>'
                     + eyes(100, 88, 24, 10, "closed", w=4) + blush(100, 120, 46, 12, op=.9) +
                     f'<ellipse cx="100" cy="128" rx="8" ry="6" fill="#ff7aa8" {S(4)}/>'
                     f'<path d="M16 90 Q6 104 16 118 M184 90 Q194 104 184 118" fill="none" stroke="#2ad1ff" stroke-width="6" stroke-linecap="round"/>')
    I["sink"] = svg(200, 200,
                    f'<rect x="88" y="20" width="24" height="44" rx="6" fill="#c9c6d8" {S(5)}/>'
                    f'<path d="M88 30 L60 30 Q48 30 48 44" fill="none" {S(10)}/><path d="M88 30 L60 30 Q48 30 48 44" fill="none" stroke="#c9c6d8" stroke-width="4"/>'
                    f'<path d="M20 90 L180 90 Q176 170 100 176 Q24 170 20 90 Z" fill="#f2f7ff" {S(6)}/>'
                    f'<ellipse cx="100" cy="104" rx="60" ry="12" fill="#c8f1ff"/>'
                    f'<circle cx="100" cy="132" r="8" fill="{OL}"/>'
                    f'<path d="M48 54 Q42 70 48 74 Q54 70 48 54 Z" fill="#5ad1ff" {S(3)}/>')
    I["star"] = svg(200, 200, star_path(100, 104, 86, 40, "#ffd23f") + eyes(100, 100, 20, 8, "open", w=4)
                    + smile(100, 120, 12, 6, sw=4))
    I["star_small"] = svg(200, 200, star_path(100, 104, 86, 40, "#ffd23f"))
    I["tooth_sticker"] = svg(200, 200,
                             f'<circle cx="100" cy="100" r="92" fill="#c9f2ff" {S(6)}/>'
                             f'<g transform="translate(28 28) scale(.48)"><path d="{TOOTH}" fill="#fdfbff" {S(9)}/></g>'
                             + eyes(100, 86, 14, 7, "closed", w=4) + smile(100, 100, 9, 5, sw=4)
                             + sparkle_shape(160, 46, 14))
    I["gear"] = svg(200, 200, gear())
    I["mystery"] = svg(200, 200,
                       f'<circle cx="100" cy="100" r="84" fill="#e9e1fb" stroke="#b9a8de" stroke-width="6" stroke-dasharray="14 10"/>'
                       f'<path d="M76 78 Q76 50 102 50 Q128 50 128 76 Q128 94 106 102 L104 118" fill="none" stroke="#b9a8de" stroke-width="14" stroke-linecap="round"/>'
                       f'<circle cx="104" cy="146" r="9" fill="#b9a8de"/>')
    I["face_outline"] = svg(300, 380,
                            f'<ellipse cx="150" cy="190" rx="120" ry="160" fill="#ffffff" fill-opacity=".25" '
                            f'stroke="#fff" stroke-width="10" stroke-dasharray="22 16"/>'
                            f'<path d="M100 160 Q112 150 124 160 M176 160 Q188 150 200 160" fill="none" stroke="#fff" stroke-width="8" stroke-linecap="round"/>'
                            f'<path d="M110 250 Q150 280 190 250" fill="none" stroke="#fff" stroke-width="8" stroke-linecap="round"/>')
    I["pop"] = svg(200, 200, burst())
    I["sparkle"] = svg(200, 200, sparkle_shape(100, 100, 80) + sparkle_shape(170, 40, 22, "#fff6c8") + sparkle_shape(36, 160, 16, "#fff6c8"))
    I["zzz"] = svg(200, 200, "".join(
        f'<text x="{x}" y="{y}" font-family="Arial Rounded MT Bold, Arial, sans-serif" font-weight="900" '
        f'font-size="{s}" fill="#e6ddff" stroke="{OL}" stroke-width="4" paint-order="stroke">Z</text>'
        for x, y, s in [(30, 180, 70), (96, 110, 54), (146, 54, 40)]))
    I["wave"] = svg(600, 300,
                    f'<path d="M0 120 Q75 60 150 120 T300 120 T450 120 T600 120 L600 300 L0 300 Z" fill="#5ad1ff" {S(6)}/>'
                    f'<path d="M0 170 Q75 120 150 170 T300 170 T450 170 T600 170 L600 300 L0 300 Z" fill="#2ab0f0" opacity=".9"/>'
                    + "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" opacity=".85"/>'
                              for x, y, r in [(80, 96, 12), (230, 90, 9), (380, 100, 14), (520, 92, 10), (300, 200, 8)]))
    I["book"] = svg(200, 200,
                    f'<path d="M100 50 Q60 30 20 44 L20 170 Q60 156 100 176 Q140 156 180 170 L180 44 Q140 30 100 50 Z" fill="#cdb4ff" {S(6)}/>'
                    f'<path d="M100 50 L100 176" {S(5)}/>'
                    + star_path(58, 104, 26, 12, "#ffd23f") + sparkle_shape(142, 100, 22, "#ff8fb8"))
    I["calendar"] = svg(200, 200,
                        f'<rect x="26" y="40" width="148" height="140" rx="16" fill="#fff" {S(6)}/>'
                        f'<path d="M26 56 Q26 40 42 40 L158 40 Q174 40 174 56 L174 80 L26 80 Z" fill="#ff5c8a" {S(6)}/>'
                        f'<rect x="56" y="22" width="14" height="34" rx="7" fill="#c9c6d8" {S(4)}/>'
                        f'<rect x="130" y="22" width="14" height="34" rx="7" fill="#c9c6d8" {S(4)}/>'
                        + star_path(100, 130, 38, 17, "#ffd23f"))
    I["home"] = svg(200, 200,
                    f'<path d="M30 96 L100 34 L170 96 L150 96 L150 170 L50 170 L50 96 Z" fill="#ffd166" {S(6)}/>'
                    f'<rect x="84" y="118" width="32" height="52" rx="8" fill="#ff8fa3" {S(5)}/>')
    I["play"] = svg(200, 200, f'<circle cx="100" cy="100" r="86" fill="#3a86ff" {S(6)}/><path d="M80 60 L146 100 L80 140 Z" fill="#fff" {S(6)}/>')
    I["camera"] = svg(200, 200,
                      f'<rect x="20" y="60" width="160" height="110" rx="20" fill="#7bdff2" {S(6)}/>'
                      f'<path d="M70 60 L82 38 L118 38 L130 60" fill="#7bdff2" {S(6)}/>'
                      f'<circle cx="100" cy="114" r="34" fill="#fff" {S(6)}/><circle cx="100" cy="114" r="16" fill="{OL}"/>')
    rays = ""
    for i in range(16):
        a0 = i / 16 * math.tau
        a1 = a0 + math.tau / 40
        rays += (f'<path d="M100 100 L{100+math.cos(a0)*98:.1f} {100+math.sin(a0)*98:.1f} '
                 f'L{100+math.cos(a1)*98:.1f} {100+math.sin(a1)*98:.1f} Z" fill="#fff6c8" opacity="{.8 if i % 2 else .5}"/>')
    I["rays"] = svg(200, 200, '<defs><radialGradient id="rg"><stop offset="0" stop-color="#fff8d6"/>'
                    '<stop offset="1" stop-color="#fff8d6" stop-opacity="0"/></radialGradient></defs>'
                    f'<circle cx="100" cy="100" r="98" fill="url(#rg)"/>{rays}'
                    + sparkle_shape(30, 40, 10, "#ffd23f") + sparkle_shape(170, 150, 12, "#ffd23f") + sparkle_shape(160, 36, 8, "#fff"))
    for k, v in I.items():
        write(f"icons/{k}.svg", v)


def star_path(cx, cy, R, r, color):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = R if i % 2 == 0 else r
        pts.append(f"{cx+math.cos(a)*rr:.1f},{cy+math.sin(a)*rr:.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{color}" {S(6)}/>'


def gear():
    p = []
    for i in range(32):
        a = i / 32 * math.tau
        r = 84 if (i // 2) % 2 == 0 else 64
        p.append(f"{100+math.cos(a)*r:.1f},{100+math.sin(a)*r:.1f}")
    return f'<polygon points="{" ".join(p)}" fill="#cfc8e6" {S(6)}/><circle cx="100" cy="100" r="28" fill="#fff" {S(6)}/>'


def burst():
    pts = []
    for i in range(24):
        a = i / 24 * math.tau
        r = 92 if i % 2 == 0 else 54
        pts.append(f"{100+math.cos(a)*r:.1f},{100+math.sin(a)*r:.1f}")
    return (f'<polygon points="{" ".join(pts)}" fill="#ffe66d" {S(5)}/>'
            f'<circle cx="100" cy="100" r="38" fill="#fff" opacity=".9"/>'
            + sparkle_shape(100, 100, 26, "#ff8fb8"))


# ---------------------------------------------------------------- emoji (256x256)
# Original cartoon collectibles, eight per world, each with a little face.

def E(body):
    return svg(256, 256, f'<ellipse cx="128" cy="240" rx="70" ry="8" fill="#000" opacity=".12"/>{body}')


def emoji_street():
    out = {}
    out["hydrant"] = ("Fire Hydrant", E(
        f'<rect x="78" y="206" width="100" height="24" rx="8" fill="#d62f3a" {S()}/>'
        f'<path d="M86 100 Q86 60 128 56 Q170 60 170 100 L170 210 L86 210 Z" fill="#ff4d5a" {S()}/>'
        f'<rect x="72" y="92" width="112" height="20" rx="10" fill="#d62f3a" {S()}/>'
        f'<rect x="48" y="140" width="34" height="34" rx="10" fill="#ffd23f" {S()}/>'
        f'<rect x="174" y="140" width="34" height="34" rx="10" fill="#ffd23f" {S()}/>'
        f'<rect x="116" y="34" width="24" height="24" rx="6" fill="#ffd23f" {S()}/>'
        + kawaii(128, 150, 0.9)))
    out["cone"] = ("Traffic Cone", E(
        f'<rect x="50" y="206" width="156" height="26" rx="8" fill="#ff7b25" {S()}/>'
        f'<path d="M112 30 L144 30 L190 210 L66 210 Z" fill="#ff8a3d" {S()}/>'
        f'<path d="M100 78 L156 78 L166 116 L90 116 Z" fill="#fff" {S(5)}/>'
        + kawaii(128, 160, 0.85)))
    out["skateboard"] = ("Skateboard", E(
        f'<g transform="rotate(-12 128 140)">'
        f'<rect x="24" y="110" width="208" height="46" rx="23" fill="#7b5cff" {S()}/>'
        f'<path d="M40 122 L216 122" stroke="#b6a6ff" stroke-width="8" stroke-linecap="round"/>'
        f'<circle cx="70" cy="178" r="20" fill="#ffd23f" {S()}/><circle cx="186" cy="178" r="20" fill="#ffd23f" {S()}/>'
        f'<rect x="56" y="152" width="28" height="12" fill="#c9c6d8" {S(4)}/><rect x="172" y="152" width="28" height="12" fill="#c9c6d8" {S(4)}/>'
        + kawaii(128, 128, 0.7) + '</g>'))
    out["sneaker"] = ("Sneaker", E(
        f'<path d="M30 180 L36 110 Q60 96 92 104 L120 140 Q160 150 210 160 Q234 168 230 196 L30 196 Z" fill="#3ad2ff" {S()}/>'
        f'<path d="M26 196 L232 196 Q236 216 220 220 L36 220 Q22 216 26 196 Z" fill="#fff" {S()}/>'
        f'<path d="M92 108 L80 150 M106 120 L94 158 M120 136 L110 164" stroke="#fff" stroke-width="7" stroke-linecap="round"/>'
        f'<path d="M150 158 Q180 150 200 170" fill="none" stroke="#ff5c8a" stroke-width="10" stroke-linecap="round"/>'
        + kawaii(60, 150, 0.6)))
    out["icepop"] = ("Ice Pop", E(
        f'<rect x="114" y="170" width="28" height="64" rx="10" fill="#f0c68a" {S()}/>'
        f'<path d="M70 70 Q70 30 128 30 Q186 30 186 70 L186 180 Q128 196 70 180 Z" fill="#ff7ac0" {S()}/>'
        f'<path d="M70 70 Q70 30 128 30 Q186 30 186 70 L186 96 Q128 112 70 96 Z" fill="#ffe066" {S()}/>'
        f'<path d="M90 60 L94 140" stroke="#fff" stroke-width="9" stroke-linecap="round" opacity=".6"/>'
        + kawaii(128, 128, 0.85)))
    out["balloon"] = ("Balloon", E(
        f'<path d="M128 180 Q110 206 132 222 Q150 236 128 250" fill="none" {S(4)}/>'
        f'<ellipse cx="128" cy="100" rx="72" ry="84" fill="#ff5c8a" {S()}/>'
        f'<path d="M118 182 L138 182 L128 168 Z" fill="#ff5c8a" {S(5)}/>'
        f'<ellipse cx="96" cy="64" rx="14" ry="22" fill="#fff" opacity=".6" transform="rotate(-25 96 64)"/>'
        + kawaii(128, 104, 1)))
    out["mailbox"] = ("Mailbox", E(
        f'<rect x="116" y="150" width="24" height="84" fill="#8b5a3c" {S()}/>'
        f'<path d="M50 160 L50 100 Q50 54 102 54 L170 54 Q212 54 212 100 L212 160 Z" fill="#3a86ff" {S()}/>'
        f'<rect x="196" y="58" width="10" height="60" fill="#ff4d5a" {S(4)}/><rect x="196" y="58" width="36" height="22" fill="#ff4d5a" {S(4)}/>'
        f'<path d="M50 100 Q50 54 102 54 Q140 60 140 100 L140 160 L50 160 Z" fill="#5da0ff" {S()}/>'
        + kawaii(95, 110, 0.75)))
    out["bus"] = ("School Bus", E(
        f'<rect x="20" y="70" width="216" height="120" rx="24" fill="#ffc53d" {S()}/>'
        f'<rect x="36" y="86" width="44" height="40" rx="8" fill="#c8f1ff" {S(5)}/>'
        f'<rect x="92" y="86" width="44" height="40" rx="8" fill="#c8f1ff" {S(5)}/>'
        f'<rect x="148" y="86" width="44" height="40" rx="8" fill="#c8f1ff" {S(5)}/>'
        f'<rect x="20" y="140" width="216" height="12" fill="#2d1b3d"/>'
        f'<circle cx="68" cy="196" r="22" fill="#4b4766" {S()}/><circle cx="188" cy="196" r="22" fill="#4b4766" {S()}/>'
        f'<circle cx="68" cy="196" r="8" fill="#c9c6d8"/><circle cx="188" cy="196" r="8" fill="#c9c6d8"/>'
        f'<circle cx="224" cy="168" r="8" fill="#fff59a" {S(3)}/>'
        + kawaii(214, 104, 0.5)))
    return out


def emoji_forest():
    out = {}
    out["mushroom"] = ("Mushroom", E(
        f'<path d="M96 130 L160 130 Q166 200 150 226 L106 226 Q90 200 96 130 Z" fill="#fff3e0" {S()}/>'
        f'<path d="M28 136 Q30 40 128 36 Q226 40 228 136 Q128 158 28 136 Z" fill="#ff5c5c" {S()}/>'
        f'<circle cx="80" cy="96" r="16" fill="#fff"/><circle cx="150" cy="70" r="13" fill="#fff"/><circle cx="190" cy="110" r="11" fill="#fff"/>'
        + kawaii(128, 176, 0.75)))
    out["acorn"] = ("Acorn", E(
        f'<path d="M66 110 Q66 220 128 230 Q190 220 190 110 Z" fill="#d9944a" {S()}/>'
        f'<path d="M50 112 Q54 56 128 54 Q202 56 206 112 Q128 126 50 112 Z" fill="#8b5a3c" {S()}/>'
        f'<path d="M70 92 L186 92 M80 74 L176 74" stroke="#6b4429" stroke-width="5" stroke-linecap="round" opacity=".7"/>'
        f'<path d="M128 54 Q130 30 146 22" fill="none" {S(7)}/>'
        + kawaii(128, 160, 0.9)))
    scales = ""
    for row, (y, n) in enumerate([(200, 3), (172, 4), (144, 5), (116, 4), (88, 3), (62, 2)]):
        for k in range(n):
            x = 128 + (k - (n - 1) / 2) * 30
            scales += f'<path d="M{x-16} {y-10} Q{x} {y+16} {x+16} {y-10}" fill="#a8683a" {S(4)}/>'
    out["pinecone"] = ("Pinecone", E(
        f'<path d="M128 36 Q196 60 198 140 Q196 214 128 226 Q60 214 58 140 Q60 60 128 36 Z" fill="#c98850" {S()}/>'
        + scales
        + f'<path d="M120 40 Q128 18 142 24 Q134 32 136 44" fill="#5cc46a" {S(4)}/>'
        + f'<ellipse cx="128" cy="134" rx="44" ry="30" fill="#e8b27a" {S(4)}/>'
        + kawaii(128, 128, 0.7)))
    out["leaf"] = ("Maple Leaf", E(
        f'<path d="M128 26 L148 74 L196 56 L180 106 L226 118 L184 148 L200 190 L142 170 L136 236 L120 236 L114 170 L56 190 L72 148 L30 118 L76 106 L60 56 L108 74 Z" '
        f'fill="#ff8a3d" {S()}/>'
        f'<path d="M128 80 L128 230" stroke="#d9622a" stroke-width="5" stroke-linecap="round"/>'
        + kawaii(128, 128, 0.85)))
    out["owl"] = ("Owl", E(
        f'<path d="M58 70 L72 40 L96 64 Q128 54 160 64 L184 40 L198 70 Q222 120 206 180 Q190 230 128 230 Q66 230 50 180 Q34 120 58 70 Z" fill="#a47148" {S()}/>'
        f'<ellipse cx="128" cy="176" rx="50" ry="44" fill="#f2d3a8"/>'
        f'<circle cx="96" cy="112" r="30" fill="#fff" {S(5)}/><circle cx="160" cy="112" r="30" fill="#fff" {S(5)}/>'
        f'<circle cx="100" cy="114" r="14" fill="{OL}"/><circle cx="156" cy="114" r="14" fill="{OL}"/>'
        f'<circle cx="95" cy="108" r="5" fill="#fff"/><circle cx="151" cy="108" r="5" fill="#fff"/>'
        f'<path d="M118 136 L138 136 L128 154 Z" fill="#ffb703" {S(4)}/>'
        + blush(128, 146, 56, 10)))
    out["hedgehog"] = ("Hedgehog", E(
        "".join(f'<path d="M{128+math.cos(a)*70:.0f} {150+math.sin(a)*60:.0f} L{128+math.cos(a+0.17)*104:.0f} {150+math.sin(a+0.17)*92:.0f} L{128+math.cos(a+0.34)*70:.0f} {150+math.sin(a+0.34)*60:.0f}" fill="#7a5233" {S(5)}/>'
                for a in [math.pi + i * 0.34 for i in range(10)])
        + f'<ellipse cx="128" cy="160" rx="84" ry="64" fill="#8f6440" {S()}/>'
        f'<path d="M70 200 Q60 150 100 130 Q150 120 200 150 Q214 200 190 214 Q128 230 70 200 Z" fill="#f2d3a8" {S(5)}/>'
        f'<circle cx="206" cy="166" r="9" fill="{OL}"/>'
        + kawaii(150, 172, 0.6)))
    out["campfire"] = ("Campfire", E(
        f'<rect x="44" y="196" width="168" height="24" rx="12" fill="#8b5a3c" {S()}/>'
        f'<rect x="60" y="182" width="136" height="22" rx="11" fill="#a8683a" {S()} transform="rotate(-8 128 192)"/>'
        f'<path d="M128 24 Q190 90 186 150 Q182 196 128 196 Q74 196 70 150 Q66 110 100 74 Q104 110 120 112 Q110 70 128 24 Z" fill="#ff7b25" {S()}/>'
        f'<path d="M128 96 Q164 130 160 160 Q156 186 128 186 Q100 186 98 162 Q96 132 128 96 Z" fill="#ffd23f"/>'
        + kawaii(128, 156, 0.7)))
    out["snail"] = ("Snail", E(
        f'<path d="M20 214 Q30 186 70 190 L196 190 Q214 160 206 120 L222 92 M206 120 L196 92" fill="#ffd6a5" {S()}/>'
        f'<path d="M20 214 L210 214 Q230 210 224 190 Q218 160 206 120" fill="#ffd6a5" {S()}/>'
        f'<circle cx="222" cy="88" r="8" fill="{OL}"/><circle cx="196" cy="88" r="8" fill="{OL}"/>'
        f'<circle cx="112" cy="134" r="72" fill="#b388ff" {S()}/>'
        f'<path d="M112 134 m-48 0 a48 48 0 1 0 96 0 a34 34 0 1 0 -68 0 a22 22 0 1 0 44 0 a10 10 0 1 0 -20 0" fill="none" stroke="#7d5bd6" stroke-width="7" stroke-linecap="round"/>'
        + kawaii(196, 168, 0.5)))
    return out


def emoji_city():
    out = {}
    out["skyscraper"] = ("Skyscraper", E(
        f'<rect x="78" y="40" width="100" height="196" rx="10" fill="#7bdff2" {S()}/>'
        f'<rect x="110" y="16" width="36" height="28" fill="#5da0ff" {S(5)}/>'
        + "".join(f'<rect x="{x}" y="{y}" width="20" height="22" rx="3" fill="#e8f7ff" {S(3)}/>'
                  for y in (56, 88, 186) for x in (92, 118, 144))
        + f'<rect x="112" y="206" width="32" height="30" fill="#5da0ff" {S(4)}/>'
        + kawaii(128, 136, 0.8)))
    out["taxi"] = ("Taxi", E(
        f'<path d="M30 170 L30 140 Q34 120 60 116 L80 80 Q90 66 110 66 L150 66 Q170 66 180 80 L200 116 Q226 120 228 140 L228 170 Z" fill="#ffd23f" {S()}/>'
        f'<path d="M92 110 L104 82 L152 82 L166 110 Z" fill="#c8f1ff" {S(5)}/>'
        f'<rect x="108" y="44" width="42" height="22" rx="6" fill="#fff" {S(5)}/>'
        f'<rect x="30" y="148" width="198" height="12" fill="{OL}" opacity=".9"/>'
        f'<circle cx="74" cy="178" r="22" fill="#4b4766" {S()}/><circle cx="184" cy="178" r="22" fill="#4b4766" {S()}/>'
        f'<circle cx="74" cy="178" r="8" fill="#c9c6d8"/><circle cx="184" cy="178" r="8" fill="#c9c6d8"/>'
        + kawaii(128, 126, 0.55)))
    out["pizza"] = ("Pizza Slice", E(
        f'<path d="M36 50 Q128 10 220 50 L128 236 Z" fill="#ffd166" {S()}/>'
        f'<path d="M36 50 Q128 10 220 50 L210 70 Q128 34 46 70 Z" fill="#e2a04a" {S()}/>'
        f'<circle cx="96" cy="96" r="14" fill="#ff5c5c" {S(4)}/><circle cx="160" cy="92" r="12" fill="#ff5c5c" {S(4)}/>'
        f'<circle cx="128" cy="188" r="10" fill="#ff5c5c" {S(4)}/>'
        + kawaii(128, 128, 0.75)))
    out["donut"] = ("Donut", E(
        f'<circle cx="128" cy="134" r="96" fill="#e2a04a" {S()}/>'
        f'<path d="M40 128 Q36 50 128 44 Q220 50 216 128 Q206 150 190 140 Q170 160 150 146 Q128 166 104 148 Q86 162 68 142 Q50 152 40 128 Z" fill="#ff8fb8" {S(5)}/>'
        f'<circle cx="128" cy="134" r="26" fill="#fff" {S()}/>'
        + "".join(f'<rect x="{x}" y="{y}" width="16" height="6" rx="3" fill="{c}" transform="rotate({r} {x} {y})"/>'
                  for x, y, c, r in [(70, 80, "#3ad2ff", 30), (110, 64, "#ffd23f", -20), (170, 76, "#7bdff2", 50),
                                     (186, 110, "#fff", -30), (60, 116, "#ffd23f", 70)])
        + kawaii(128, 190, 0.6)))
    out["hotdog"] = ("Hot Dog", E(
        f'<path d="M30 150 Q20 110 60 110 L196 110 Q236 110 226 150 Q216 196 128 196 Q40 196 30 150 Z" fill="#f2c27a" {S()}/>'
        f'<rect x="20" y="104" width="216" height="40" rx="20" fill="#e2563c" {S()}/>'
        f'<path d="M40 122 Q60 110 80 124 T120 124 T160 124 T200 124 T224 120" fill="none" stroke="#ffd23f" stroke-width="7" stroke-linecap="round"/>'
        + kawaii(128, 164, 0.7)))
    out["trafficlight"] = ("Traffic Light", E(
        f'<rect x="116" y="196" width="24" height="44" fill="#4b4766" {S()}/>'
        f'<rect x="80" y="20" width="96" height="184" rx="24" fill="#3c3a59" {S()}/>'
        f'<circle cx="128" cy="58" r="22" fill="#ff5c5c" {S(4)}/>'
        f'<circle cx="128" cy="112" r="22" fill="#ffd23f" {S(4)}/>'
        f'<circle cx="128" cy="166" r="22" fill="#5cd67a" {S(4)}/>'
        + eyes(128, 108, 9, 5, "open", w=3) + smile(128, 118, 6, 4, sw=3)))
    out["pigeon"] = ("Pigeon", E(
        f'<path d="M50 160 Q40 100 100 96 Q110 60 150 62 Q180 64 186 96 L214 104 L186 114 Q200 160 170 196 Q120 220 70 200 L30 214 L46 180 Z" fill="#a9b8d8" {S()}/>'
        f'<path d="M120 116 Q150 120 160 156 Q130 170 100 150 Z" fill="#8a9bc4" {S(4)}/>'
        f'<path d="M140 96 Q160 110 180 104 Q176 130 150 130 Z" fill="#7fd6a8" opacity=".8"/>'
        f'<path d="M110 206 L106 230 M150 202 L154 230" {S(6)}/>'
        f'<circle cx="160" cy="84" r="9" fill="{OL}"/><circle cx="157" cy="81" r="3" fill="#fff"/>'
        + blush(160, 104, 0, 9)))
    out["pretzel"] = ("Pretzel", E(
        f'<path d="M128 200 C40 230 20 130 70 90 C110 60 150 120 128 160 C106 120 146 60 186 90 C236 130 216 230 128 200 Z" '
        f'fill="none" stroke="{OL}" stroke-width="40" stroke-linejoin="round"/>'
        f'<path d="M128 200 C40 230 20 130 70 90 C110 60 150 120 128 160 C106 120 146 60 186 90 C236 130 216 230 128 200 Z" '
        f'fill="none" stroke="#c97b35" stroke-width="28" stroke-linejoin="round"/>'
        + "".join(f'<circle cx="{x}" cy="{y}" r="3" fill="#fff"/>' for x, y in [(60, 120), (80, 92), (192, 100), (200, 150), (100, 200), (150, 206)])
        + kawaii(128, 108, 0.55)))
    return out


WORLDS = [
    ("street", "The Street", bg_street, emoji_street),
    ("forest", "The Forest", bg_forest, emoji_forest),
    ("city", "The City", bg_city, emoji_city),
]


def main():
    import art_extra as X
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    for name, fn in [("a", goblin_a), ("b", goblin_b), ("c", goblin_c), ("sneaky", goblin_sneaky)]:
        write(f"goblins/{name}.svg", fn("open"))
        write(f"goblins/{name}_sleep.svg", fn("closed"))
    for mode, suffix in [("open", ""), ("squint", "_hurt"), ("dizzy", "_dizzy"), ("closed", "_sleep")]:
        write(f"goblins/big{suffix}.svg", goblin_big(mode))
    import art_halloween as HW
    hero = X.hero_files(write)
    HW.hero_items(write, hero)
    with open(os.path.join(OUT, "hero", "parts.json"), "w") as f:
        json.dump(hero, f, indent=1)
    write("worlds/home.svg", bg_home())
    catalog = {"worlds": []}
    for wid, title, bg, em in WORLDS + X.MORE_WORLDS:
        write(f"worlds/{wid}.svg", bg(False))
        write(f"worlds/{wid}_night.svg", bg(True))
        designs = dict(em())
        designs.update(X.EXTRA_FOR.get(wid, dict)())
        items = []
        for eid, (label, content) in designs.items():
            write(f"emoji/{wid}/{eid}.svg", content)
            write(f"emoji/{wid}/{eid}_gold.svg", X.sparkly(content))
            items.append({"id": f"{wid}/{eid}", "name": label})
        catalog["worlds"].append({"id": wid, "name": title, "emoji": items})
    # Limited-time event worlds: only played (and their emoji only won) during the event.
    catalog["worlds"].append(HW.halloween_files(write, X.sparkly))
    with open(os.path.join(OUT, "emoji", "catalog.json"), "w") as f:
        json.dump(catalog, f, indent=1)
    mouth()
    icon_files()
    for k, v in X.extra_icons().items():
        write(f"icons/{k}.svg", v)
    if shutil.which("rsvg-convert"):
        app_icon = svg(512, 512, '<rect width="512" height="512" rx="0" fill="#b388ff"/>'
                       '<g transform="translate(56 70) scale(1.33)">' + goblin_a("open").split("</defs>", 1)[1][:-6] + '</g>')
        write("icons/app.svg", app_icon)
        for size in (180, 192, 512):
            subprocess.run(["rsvg-convert", "-w", str(size), "-h", str(size), os.path.join(OUT, "icons", "app.svg"),
                            "-o", os.path.join(OUT, "icons", f"app-{size}.png")], check=True)
    n = sum(len(w["emoji"]) for w in catalog["worlds"])
    print(f"art written to {OUT}: {len(catalog['worlds'])} worlds, {n} emoji (+{n} sparkly)")


if __name__ == "__main__":
    main()
