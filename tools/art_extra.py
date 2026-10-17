"""More generated art for tools/gen_art.py: extra emoji, five more worlds,
hero customisation parts, sparkly emoji variants and a few icons."""
import math
import random

from gen_art import (OL, S, svg, E, kawaii, eyes, blush, smile, sparkle_shape, star_path, grad, stars,
                     cloud, sky, shade, buddy, TOOTH)


def F(c, w=6):
    return f'fill="{c}" {S(w)}'


# ---------------------------------------------------------------- shared shapes

def animal_head(cx, cy, r, col, ears="round", ear_col=None, snout=None, face_s=1.0):
    ear_col = ear_col or col
    out = ""
    if ears == "round":
        out += f'<circle cx="{cx-r*0.75}" cy="{cy-r*0.7}" r="{r*0.35}" {F(ear_col)}/><circle cx="{cx+r*0.75}" cy="{cy-r*0.7}" r="{r*0.35}" {F(ear_col)}/>'
    elif ears == "pointy":
        out += (f'<path d="M{cx-r*0.9} {cy-r*0.2} L{cx-r*0.75} {cy-r*1.25} L{cx-r*0.2} {cy-r*0.8} Z" {F(ear_col)}/>'
                f'<path d="M{cx+r*0.9} {cy-r*0.2} L{cx+r*0.75} {cy-r*1.25} L{cx+r*0.2} {cy-r*0.8} Z" {F(ear_col)}/>')
    elif ears == "floppy":
        out += (f'<ellipse cx="{cx-r*0.95}" cy="{cy-r*0.05}" rx="{r*0.3}" ry="{r*0.6}" {F(ear_col)} transform="rotate(20 {cx-r*0.95} {cy})"/>'
                f'<ellipse cx="{cx+r*0.95}" cy="{cy-r*0.05}" rx="{r*0.3}" ry="{r*0.6}" {F(ear_col)} transform="rotate(-20 {cx+r*0.95} {cy})"/>')
    elif ears == "side":
        out += (f'<ellipse cx="{cx-r*1.05}" cy="{cy-r*0.25}" rx="{r*0.4}" ry="{r*0.2}" {F(ear_col)}/>'
                f'<ellipse cx="{cx+r*1.05}" cy="{cy-r*0.25}" rx="{r*0.4}" ry="{r*0.2}" {F(ear_col)}/>')
    out += f'<circle cx="{cx}" cy="{cy}" r="{r}" {F(col)}/>'
    if snout:
        out += f'<ellipse cx="{cx}" cy="{cy+r*0.42}" rx="{r*0.45}" ry="{r*0.3}" {F(snout, 5)}/>'
    out += kawaii(cx, cy - r * 0.1, face_s)
    return out


def dino(col, belly, kind="rex"):
    """Cute side-view dinosaur facing right."""
    out = ""
    if kind == "stego":
        for i, (x, y) in enumerate([(66, 86), (98, 62), (132, 56), (166, 70)]):
            out += f'<path d="M{x-22} {y+60} L{x} {y} L{x+22} {y+60} Z" {F("#ff8a3d", 5)}/>'
    if kind == "long":
        neck = f'<path d="M150 150 Q170 70 190 46" fill="none" {S(36)}/><path d="M150 150 Q170 70 190 46" fill="none" stroke="{col}" stroke-width="24" stroke-linecap="round"/>'
    else:
        neck = ""
    out += f'<path d="M30 176 Q10 170 18 150 Q50 160 70 150 Z" {F(col)}/>'  # tail
    out += f'<ellipse cx="116" cy="160" rx="80" ry="54" {F(col)}/>'
    out += f'<ellipse cx="124" cy="176" rx="50" ry="30" fill="{belly}"/>'
    out += f'<rect x="72" y="190" width="26" height="40" rx="10" {F(col)}/><rect x="140" y="190" width="26" height="40" rx="10" {F(col)}/>'
    out += neck
    if kind == "long":
        hx, hy = 196, 50
        out += f'<ellipse cx="{hx}" cy="{hy}" rx="34" ry="24" {F(col)}/>'
        out += f'<circle cx="{hx+6}" cy="{hy-6}" r="6" fill="{OL}"/><circle cx="{hx+4}" cy="{hy-8}" r="2" fill="#fff"/>'
        out += f'<path d="M{hx+12} {hy+10} Q{hx+22} {hy+14} {hx+28} {hy+6}" fill="none" {S(4)}/>'
        out += blush(hx + 10, hy + 6, 0, 6)
        return out
    hx, hy = 186, 104
    out += f'<ellipse cx="{hx}" cy="{hy}" rx="52" ry="42" {F(col)}/>'
    if kind == "tri":
        out += f'<path d="M150 70 Q180 40 226 66 Q200 80 170 96 Z" {F("#ffd6a5", 5)}/>'
        out += f'<path d="M196 66 L208 30 L214 64 Z" {F("#fff6e0", 4)}/><path d="M224 92 L248 82 L232 102 Z" {F("#fff6e0", 4)}/>'
    if kind == "rex":
        out += f'<path d="M100 166 Q86 176 92 188" fill="none" {S(8)}/>'
        out += f'<path d="M206 124 L212 132 L218 124 M222 124 L228 132 L234 124" fill="#fff" stroke="{OL}" stroke-width="3" stroke-linejoin="round"/>'
    out += eyes(hx + 4, hy - 8, 16, 9, w=4) + blush(hx + 2, hy + 12, 24, 8)
    out += f'<path d="M{hx+4} {hy+16} Q{hx+20} {hy+26} {hx+36} {hy+14}" fill="none" {S(4)}/>'
    return out


def wings(cx, cy, col, w=60, h=40):
    return (f'<path d="M{cx} {cy} Q{cx-w} {cy-h*1.6} {cx-w*1.3} {cy} Q{cx-w*0.6} {cy+h*0.4} {cx} {cy} Z" {F(col, 5)}/>'
            f'<path d="M{cx} {cy} Q{cx+w} {cy-h*1.6} {cx+w*1.3} {cy} Q{cx+w*0.6} {cy+h*0.4} {cx} {cy} Z" {F(col, 5)}/>')


# ---------------------------------------------------------------- extra emoji for the first three worlds

def emoji_street_extra():
    return {
        "puppy": ("Puppy", E(animal_head(128, 130, 74, "#f2c27a", "floppy", "#a8683a", "#fff3e0")
                             + f'<ellipse cx="128" cy="160" rx="10" ry="7" fill="{OL}"/>')),
        "kite": ("Kite", E(
            f'<path d="M128 220 Q100 236 120 246 Q140 252 112 252" fill="none" {S(4)}/>'
            f'<path d="M128 24 L200 110 L128 220 L56 110 Z" {F("#ff5c8a")}/>'
            f'<path d="M128 24 L128 220 M56 110 L200 110" {S(4)}/>'
            f'<path d="M128 24 L200 110 L128 110 Z" fill="#ffd23f" opacity=".9"/><path d="M128 110 L56 110 L128 220 Z" fill="#3ad2ff" opacity=".9"/>'
            f'<path d="M128 24 L200 110 L128 220 L56 110 Z" fill="none" {S()}/>'
            + kawaii(128, 104, 0.8))),
        "scooter": ("Scooter", E(
            f'<path d="M60 196 L190 196 L204 60" fill="none" {S(14)}/><path d="M60 196 L190 196 L204 60" fill="none" stroke="#5cd67a" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="M184 56 L226 50" {S(12)}/>'
            f'<circle cx="62" cy="208" r="22" {F("#4b4766")}/><circle cx="196" cy="208" r="22" {F("#4b4766")}/>'
            f'<circle cx="62" cy="208" r="8" fill="#c9c6d8"/><circle cx="196" cy="208" r="8" fill="#c9c6d8"/>'
            + kawaii(130, 176, 0.5))),
        "stopsign": ("Stop Sign", E(
            f'<rect x="118" y="150" width="20" height="86" {F("#c9c6d8")}/>'
            + f'<polygon points="{" ".join(f"{128+math.cos(math.pi/8+i*math.pi/4)*86:.0f},{100+math.sin(math.pi/8+i*math.pi/4)*86:.0f}" for i in range(8))}" {F("#ff4d5a")}/>'
            + f'<polygon points="{" ".join(f"{128+math.cos(math.pi/8+i*math.pi/4)*70:.0f},{100+math.sin(math.pi/8+i*math.pi/4)*70:.0f}" for i in range(8))}" fill="none" stroke="#fff" stroke-width="6"/>'
            + kawaii(128, 96, 1))),
    }


def emoji_forest_extra():
    return {
        "fox": ("Fox", E(
            f'<path d="M48 70 L80 150 L176 150 L208 70 L160 110 L96 110 Z" {F("#ff8a3d")}/>'
            f'<path d="M48 120 Q128 250 208 120 Q200 90 128 92 Q56 90 48 120 Z" {F("#ff8a3d")}/>'
            f'<path d="M78 150 Q128 230 178 150 Q150 170 128 168 Q106 170 78 150 Z" fill="#fff3e0"/>'
            f'<ellipse cx="128" cy="176" rx="11" ry="8" fill="{OL}"/>' + kawaii(128, 138, 0.9))),
        "butterfly": ("Butterfly", E(
            wings(128, 120, "#b388ff", 60, 50) +
            f'<path d="M128 130 Q70 170 80 206 Q110 214 128 140 Q146 214 176 206 Q186 170 128 130 Z" {F("#ff8fb8", 5)}/>'
            f'<ellipse cx="128" cy="140" rx="16" ry="56" {F("#5c3a8a")}/>'
            f'<path d="M120 86 Q110 60 96 56 M136 86 Q146 60 160 56" fill="none" {S(4)}/>'
            + kawaii(128, 116, 0.45))),
        "bee": ("Bee", E(
            wings(128, 90, "#e8f7ff", 40, 34) +
            f'<ellipse cx="128" cy="146" rx="80" ry="64" {F("#ffd23f")}/>'
            f'<path d="M96 88 Q90 146 96 204 M136 84 Q130 146 136 208" fill="none" stroke="{OL}" stroke-width="16"/>'
            f'<ellipse cx="128" cy="146" rx="80" ry="64" fill="none" {S()}/>'
            f'<path d="M208 146 L230 150 L208 156 Z" {F(OL, 3)}/>'
            + kawaii(176, 140, 0.6))),
        "clover": ("Lucky Clover", E(
            f'<path d="M128 140 Q120 200 96 236" fill="none" {S(10)}/><path d="M128 140 Q120 200 96 236" fill="none" stroke="#2fb36d" stroke-width="5"/>'
            + "".join(f'<g transform="rotate({a} 128 120)"><path d="M128 120 C90 100 92 50 128 70 C164 50 166 100 128 120 Z" transform="translate(0 -26)" {F("#5cd67a")}/></g>'
                      for a in (0, 90, 180, 270))
            + f'<circle cx="128" cy="120" r="18" fill="#5cd67a"/>' + kawaii(128, 116, 0.5))),
    }


def emoji_city_extra():
    return {
        "coffee": ("Cocoa Mug", E(
            f'<path d="M180 110 Q226 110 222 150 Q218 186 176 184" fill="none" {S(14)}/><path d="M180 110 Q226 110 222 150 Q218 186 176 184" fill="none" stroke="#5da0ff" stroke-width="6"/>'
            f'<path d="M50 80 L190 80 L180 210 Q120 226 60 210 Z" {F("#5da0ff")}/>'
            f'<ellipse cx="120" cy="80" rx="70" ry="14" {F("#8b5a3c", 5)}/>'
            f'<circle cx="100" cy="72" r="12" fill="#fff" {S(3)}/><circle cx="130" cy="68" r="10" fill="#fff" {S(3)}/>'
            f'<path d="M96 54 Q86 36 100 22 M134 50 Q124 32 138 18" fill="none" stroke="#c9c6d8" stroke-width="6" stroke-linecap="round"/>'
            + kawaii(120, 138, 0.9))),
        "helicopter": ("Helicopter", E(
            f'<path d="M40 50 L216 50" {S(10)}/><rect x="122" y="50" width="12" height="30" {F("#4b4766", 4)}/>'
            f'<path d="M150 140 L230 120 L236 100 L224 104 L210 124 L160 128 Z" {F("#ff7b25", 5)}/>'
            f'<ellipse cx="116" cy="140" rx="74" ry="58" {F("#ff7b25")}/>'
            f'<path d="M60 130 Q60 96 100 92 L110 140 Z" {F("#c8f1ff", 5)}/>'
            f'<path d="M70 214 L170 214 M90 196 L84 214 M150 196 L156 214" {S(7)}/>'
            + kawaii(132, 136, 0.7))),
        "headphones": ("Headphones", E(
            f'<path d="M56 150 Q56 50 128 50 Q200 50 200 150" fill="none" {S(26)}/><path d="M56 150 Q56 50 128 50 Q200 50 200 150" fill="none" stroke="#ff5c8a" stroke-width="14"/>'
            f'<rect x="30" y="130" width="54" height="84" rx="24" {F("#3c3a59")}/><rect x="172" y="130" width="54" height="84" rx="24" {F("#3c3a59")}/>'
            f'<rect x="42" y="142" width="30" height="60" rx="14" fill="#ff8fb8"/><rect x="184" y="142" width="30" height="60" rx="14" fill="#ff8fb8"/>'
            + kawaii(128, 150, 0.7))),
        "camera": ("Camera", E(
            f'<rect x="28" y="80" width="200" height="130" rx="22" {F("#ff8fa3")}/>'
            f'<path d="M84 80 L98 52 L158 52 L172 80" {F("#ff8fa3")}/>'
            f'<circle cx="128" cy="146" r="46" {F("#fff")}/><circle cx="128" cy="146" r="30" {F("#3c3a59", 4)}/>'
            f'<circle cx="118" cy="136" r="8" fill="#fff"/><rect x="184" y="94" width="26" height="16" rx="5" {F("#ffd23f", 4)}/>'
            + kawaii(128, 108, 0.45))),
    }


# ---------------------------------------------------------------- new worlds' emoji

def emoji_ocean():
    o = {}
    o["fish"] = ("Fish", E(
        f'<path d="M190 128 L240 86 L236 170 Z" {F("#ff8a3d")}/>'
        f'<ellipse cx="120" cy="128" rx="90" ry="64" {F("#ffb03a")}/>'
        f'<path d="M110 70 Q130 40 160 72" {F("#ff8a3d", 5)}/>'
        f'<path d="M150 80 Q160 128 150 176" fill="none" stroke="#fff" stroke-width="8" opacity=".7"/>' + kawaii(96, 120, 0.9)))
    o["octopus"] = ("Octopus", E(
        "".join(f'<path d="M{x} 150 Q{x+d} 200 {x+d*2} 226" fill="none" {S(26)}/><path d="M{x} 150 Q{x+d} 200 {x+d*2} 226" fill="none" stroke="#ff7ac0" stroke-width="14" stroke-linecap="round"/>'
                for x, d in [(70, -14), (104, -6), (152, 6), (186, 14)])
        + f'<path d="M48 150 Q40 40 128 36 Q216 40 208 150 Q128 176 48 150 Z" {F("#ff7ac0")}/>' + kawaii(128, 108, 1.1)))
    o["whale"] = ("Whale", E(
        f'<path d="M190 120 Q220 60 246 80 Q226 100 236 120 Q214 112 200 134 Z" {F("#5da0ff")}/>'
        f'<path d="M20 150 Q24 70 110 70 Q200 70 204 140 Q206 200 110 204 Q30 206 20 150 Z" {F("#5da0ff")}/>'
        f'<path d="M24 160 Q110 190 200 150 Q190 200 110 204 Q34 204 24 160 Z" fill="#c8f1ff"/>'
        f'<path d="M96 66 Q86 40 70 34 M96 66 Q100 36 116 26" fill="none" stroke="#5ad1ff" stroke-width="6" stroke-linecap="round"/>' + kawaii(84, 130, 0.9)))
    o["crab"] = ("Crab", E(
        f'<path d="M50 100 Q20 70 40 46 Q60 60 56 80 Q70 64 76 84 Z" {F("#ff5c5c", 5)}/><path d="M206 100 Q236 70 216 46 Q196 60 200 80 Q186 64 180 84 Z" {F("#ff5c5c", 5)}/>'
        f'<path d="M70 170 L40 200 M80 186 L60 220 M186 170 L216 200 M176 186 L196 220" {S(9)}/>'
        f'<ellipse cx="128" cy="150" rx="86" ry="56" {F("#ff5c5c")}/>'
        f'<path d="M106 100 L100 70 M150 100 L156 70" {S(6)}/><circle cx="100" cy="66" r="12" {F("#fff", 4)}/><circle cx="156" cy="66" r="12" {F("#fff", 4)}/>'
        f'<circle cx="102" cy="66" r="6" fill="{OL}"/><circle cx="154" cy="66" r="6" fill="{OL}"/>'
        + blush(128, 160, 40, 10) + smile(128, 156, 14, 8)))
    o["starfish"] = ("Starfish", E(star_path(128, 132, 104, 50, "#ff9f68") + kawaii(128, 128, 0.9)))
    o["jellyfish"] = ("Jellyfish", E(
        "".join(f'<path d="M{x} 130 Q{x+10} 170 {x} 200 Q{x-10} 222 {x+4} 240" fill="none" stroke="#c39bff" stroke-width="7" stroke-linecap="round"/>' for x in (84, 112, 144, 172))
        + f'<path d="M40 140 Q40 40 128 40 Q216 40 216 140 Q192 126 172 142 Q150 126 128 142 Q106 126 84 142 Q64 126 40 140 Z" {F("#e0c3ff")}/>'
        + kawaii(128, 98, 1)))
    o["shell"] = ("Seashell", E(
        f'<path d="M128 220 L40 120 Q60 40 128 34 Q196 40 216 120 Z" {F("#ffc2d4")}/>'
        + "".join(f'<path d="M128 214 L{x} 60" stroke="#ff8fb8" stroke-width="5"/>' for x in (70, 98, 128, 158, 186))
        + f'<path d="M128 220 L40 120 Q60 40 128 34 Q196 40 216 120 Z" fill="none" {S()}/>'
        f'<rect x="110" y="206" width="36" height="22" rx="8" {F("#ffc2d4", 5)}/>' + kawaii(128, 128, 0.7)))
    o["turtle"] = ("Sea Turtle", E(
        f'<ellipse cx="56" cy="190" rx="26" ry="14" {F("#7fd67a")}/><ellipse cx="200" cy="190" rx="26" ry="14" {F("#7fd67a")}/>'
        f'<ellipse cx="60" cy="110" rx="28" ry="14" {F("#7fd67a")} transform="rotate(-30 60 110)"/>'
        f'<circle cx="214" cy="120" r="30" {F("#7fd67a")}/>'
        f'<ellipse cx="128" cy="150" rx="86" ry="62" {F("#3fa85a")}/>'
        f'<path d="M128 96 L160 120 L148 160 L108 160 L96 120 Z" fill="none" stroke="#2a7d44" stroke-width="5"/>'
        + eyes(218, 114, 10, 6, w=3) + smile(220, 128, 8, 4, sw=3)))
    o["puffer"] = ("Pufferfish", E(
        "".join(f'<path d="M{128+math.cos(a)*84:.0f} {128+math.sin(a)*84:.0f} L{128+math.cos(a)*106:.0f} {128+math.sin(a)*106:.0f}" {S(7)}/>' for a in [i * math.tau / 16 for i in range(16)])
        + f'<circle cx="128" cy="128" r="88" {F("#ffd23f")}/><ellipse cx="128" cy="160" rx="60" ry="40" fill="#fff3c0"/>' + kawaii(128, 122, 1.1)))
    o["seahorse"] = ("Seahorse", E(
        f'<path d="M140 60 Q196 70 180 120 Q166 150 176 186 Q186 220 150 234 Q120 240 120 214 Q140 220 146 204 Q150 180 130 160 Q104 130 116 96 Q90 96 76 80 Q100 56 140 60 Z" {F("#ffb03a")}/>'
        f'<path d="M150 70 L170 46 L176 70" {F("#ff8a3d", 4)}/><path d="M176 140 Q206 140 200 170 Q186 156 176 160" {F("#ff8a3d", 4)}/>'
        f'<circle cx="130" cy="82" r="8" fill="{OL}"/><circle cx="127" cy="79" r="3" fill="#fff"/>' + blush(140, 100, 0, 8)))
    o["sailboat"] = ("Sailboat", E(
        f'<path d="M30 170 L226 170 Q210 220 128 222 Q46 220 30 170 Z" {F("#ff5c5c")}/>'
        f'<rect x="122" y="34" width="12" height="138" {F("#8b5a3c", 4)}/>'
        f'<path d="M136 40 L210 150 L136 150 Z" {F("#fff")}/><path d="M120 60 L60 150 L120 150 Z" {F("#ffd23f")}/>'
        + kawaii(128, 192, 0.6)))
    o["coral"] = ("Coral", E(
        f'<path d="M128 230 L128 150 M128 180 Q90 160 80 110 M128 160 Q170 140 176 90 M80 110 Q66 80 76 56 M80 110 Q100 84 96 62 M176 90 Q196 66 186 44 M176 90 Q160 64 166 40 M128 150 Q124 110 132 80" '
        f'fill="none" {S(30)}/>'
        f'<path d="M128 230 L128 150 M128 180 Q90 160 80 110 M128 160 Q170 140 176 90 M80 110 Q66 80 76 56 M80 110 Q100 84 96 62 M176 90 Q196 66 186 44 M176 90 Q160 64 166 40 M128 150 Q124 110 132 80" '
        f'fill="none" stroke="#ff7a9a" stroke-width="18" stroke-linecap="round"/>' + kawaii(128, 196, 0.6)))
    return o


def emoji_space():
    o = {}
    o["rocket"] = ("Rocket", E(
        f'<path d="M100 200 Q128 250 156 200 Z" {F("#ffb03a", 5)}/>'
        f'<path d="M84 150 L52 200 L96 190 Z" {F("#ff5c5c")}/><path d="M172 150 L204 200 L160 190 Z" {F("#ff5c5c")}/>'
        f'<path d="M128 20 Q186 70 172 196 L84 196 Q70 70 128 20 Z" {F("#f2f7ff")}/>'
        f'<path d="M100 50 Q128 16 156 50 Q128 60 100 50 Z" {F("#ff5c5c", 5)}/>'
        f'<circle cx="128" cy="100" r="24" {F("#5ad1ff")}/>' + kawaii(128, 150, 0.6)))
    o["planet"] = ("Ringed Planet", E(
        f'<ellipse cx="128" cy="134" rx="118" ry="34" fill="none" stroke="{OL}" stroke-width="18" transform="rotate(-14 128 134)"/>'
        f'<circle cx="128" cy="128" r="74" {F("#c39bff")}/>'
        f'<path d="M70 100 Q128 116 190 96 M60 150 Q128 166 196 146" fill="none" stroke="#a47be8" stroke-width="10"/>'
        f'<path d="M14 160 Q128 190 242 108" fill="none" stroke="{OL}" stroke-width="18" stroke-linecap="round"/>'
        f'<path d="M14 160 Q128 190 242 108" fill="none" stroke="#ffd166" stroke-width="8" stroke-linecap="round"/>' + kawaii(128, 120, 0.9)))
    o["moon"] = ("Moon", E(
        f'<circle cx="128" cy="128" r="96" {F("#fff1a8")}/>'
        f'<circle cx="80" cy="90" r="16" fill="#f2dd7a"/><circle cx="180" cy="170" r="20" fill="#f2dd7a"/><circle cx="170" cy="76" r="10" fill="#f2dd7a"/>'
        + kawaii(128, 126, 1.1)))
    o["shootingstar"] = ("Shooting Star", E(
        f'<path d="M20 230 L110 140" stroke="#ff8fb8" stroke-width="22" stroke-linecap="round"/><path d="M46 240 L120 166" stroke="#5ad1ff" stroke-width="14" stroke-linecap="round"/>'
        + star_path(150, 108, 88, 40, "#ffd23f") + kawaii(150, 104, 0.8)))
    o["alien"] = ("Alien", E(
        f'<path d="M90 60 Q80 30 64 26 M166 60 Q176 30 192 26" fill="none" {S(6)}/><circle cx="64" cy="26" r="10" {F("#ffd23f", 4)}/><circle cx="192" cy="26" r="10" {F("#ffd23f", 4)}/>'
        f'<path d="M128 46 Q210 46 206 130 Q200 220 128 226 Q56 220 50 130 Q46 46 128 46 Z" {F("#7be07a")}/>'
        f'<ellipse cx="94" cy="124" rx="24" ry="30" fill="{OL}" transform="rotate(20 94 124)"/><ellipse cx="162" cy="124" rx="24" ry="30" fill="{OL}" transform="rotate(-20 162 124)"/>'
        f'<circle cx="88" cy="112" r="8" fill="#fff"/><circle cx="156" cy="112" r="8" fill="#fff"/>' + smile(128, 176, 16, 8)))
    o["ufo"] = ("UFO", E(
        f'<path d="M90 150 L60 230 L196 230 L166 150 Z" fill="#fff59a" opacity=".6"/>'
        f'<path d="M80 110 Q80 50 128 50 Q176 50 176 110 Z" {F("#c8f1ff")}/>'
        f'<ellipse cx="128" cy="130" rx="110" ry="38" {F("#b388ff")}/>'
        + "".join(f'<circle cx="{x}" cy="138" r="8" {F("#ffd23f", 3)}/>' for x in (56, 92, 128, 164, 200)) + kawaii(128, 84, 0.6)))
    o["helmet"] = ("Space Helmet", E(
        f'<rect x="60" y="190" width="136" height="40" rx="14" {F("#c9c6d8")}/>'
        f'<circle cx="128" cy="120" r="96" {F("#f2f7ff")}/><ellipse cx="128" cy="128" rx="68" ry="58" {F("#3c3a6e")}/>'
        f'<path d="M84 104 Q100 82 126 80" fill="none" stroke="#fff" stroke-width="10" stroke-linecap="round" opacity=".8"/>'
        + sparkle_shape(160, 140, 12, "#fff6c8") + kawaii(128, 128, 0.8).replace(OL, "#fff")))
    o["comet"] = ("Comet", E(
        f'<path d="M200 60 Q100 90 40 220 Q120 150 210 110 Z" fill="#7cf5ff" opacity=".8"/>'
        f'<path d="M200 60 Q130 110 90 210 Q150 150 216 100 Z" fill="#fff" opacity=".8"/>'
        f'<circle cx="190" cy="80" r="48" {F("#5ad1ff")}/>' + kawaii(190, 76, 0.7)))
    o["satellite"] = ("Satellite", E(
        f'<rect x="10" y="100" width="70" height="56" rx="6" {F("#5da0ff")}/><rect x="176" y="100" width="70" height="56" rx="6" {F("#5da0ff")}/>'
        f'<path d="M10 128 L80 128 M45 100 L45 156 M176 128 L246 128 M211 100 L211 156" stroke="#2d3266" stroke-width="4"/>'
        f'<rect x="80" y="122" width="96" height="12" fill="#c9c6d8"/>'
        f'<rect x="92" y="84" width="72" height="90" rx="16" {F("#e5e1f0")}/><path d="M128 84 L128 50" {S(6)}/><circle cx="128" cy="44" r="10" {F("#ff5c5c", 4)}/>'
        + kawaii(128, 124, 0.6)))
    o["sun"] = ("Sun", E(
        "".join(f'<path d="M{128+math.cos(a)*80:.0f} {128+math.sin(a)*80:.0f} L{128+math.cos(a+0.2)*112:.0f} {128+math.sin(a+0.2)*112:.0f} L{128+math.cos(a+0.4)*80:.0f} {128+math.sin(a+0.4)*80:.0f} Z" {F("#ffb03a", 4)}/>'
                for a in [i * math.tau / 12 for i in range(12)])
        + f'<circle cx="128" cy="128" r="80" {F("#ffd23f")}/>' + kawaii(128, 124, 1.1)))
    o["asteroid"] = ("Asteroid", E(
        f'<path d="M50 120 Q40 60 100 50 Q150 30 190 70 Q230 110 206 160 Q190 220 120 214 Q50 210 50 120 Z" {F("#b8a8a0")}/>'
        f'<circle cx="90" cy="90" r="14" fill="#9a8a84"/><circle cx="170" cy="170" r="18" fill="#9a8a84"/><circle cx="180" cy="96" r="9" fill="#9a8a84"/>'
        + kawaii(128, 132, 0.9)))
    o["robot"] = ("Robot", E(
        f'<path d="M128 40 L128 20" {S(6)}/><circle cx="128" cy="18" r="10" {F("#ff5c5c", 4)}/>'
        f'<rect x="56" y="40" width="144" height="110" rx="24" {F("#a9c4e8")}/>'
        f'<rect x="72" y="58" width="112" height="72" rx="16" {F("#2d3266", 4)}/>'
        f'<circle cx="104" cy="92" r="12" fill="#7cf5ff"/><circle cx="152" cy="92" r="12" fill="#7cf5ff"/>'
        f'<path d="M110 114 Q128 124 146 114" fill="none" stroke="#7cf5ff" stroke-width="5" stroke-linecap="round"/>'
        f'<rect x="76" y="156" width="104" height="74" rx="18" {F("#a9c4e8")}/>'
        f'<circle cx="128" cy="192" r="14" {F("#ffd23f", 4)}/>'))
    return o


def emoji_farm():
    o = {}
    o["cow"] = ("Cow", E(
        f'<path d="M64 60 Q50 40 60 26 M192 60 Q206 40 196 26" fill="none" stroke="#fff6e0" stroke-width="14" stroke-linecap="round"/>'
        + animal_head(128, 124, 82, "#fff", "side", "#fff")
        + f'<ellipse cx="80" cy="90" rx="24" ry="18" fill="{OL}"/><ellipse cx="178" cy="150" rx="16" ry="12" fill="{OL}"/>'
        f'<ellipse cx="128" cy="170" rx="52" ry="32" {F("#ffb4c8", 5)}/><ellipse cx="110" cy="170" rx="7" ry="9" fill="{OL}"/><ellipse cx="146" cy="170" rx="7" ry="9" fill="{OL}"/>'
        + eyes(128, 110, 26, 10, w=4)))
    o["pig"] = ("Piglet", E(
        animal_head(128, 130, 82, "#ffb4c8", "pointy", "#ff9ab8")
        + f'<ellipse cx="128" cy="160" rx="30" ry="22" {F("#ff9ab8", 5)}/><ellipse cx="118" cy="160" rx="5" ry="8" fill="{OL}"/><ellipse cx="138" cy="160" rx="5" ry="8" fill="{OL}"/>'))
    o["chick"] = ("Chick", E(
        f'<path d="M110 40 Q120 20 128 40 Q136 20 146 40" {F("#ffb03a", 4)}/>'
        f'<circle cx="128" cy="134" r="90" {F("#ffe066")}/><path d="M50 150 Q30 130 44 116 Q62 128 60 150 Z" {F("#ffd23f", 5)}/><path d="M206 150 Q226 130 212 116 Q194 128 196 150 Z" {F("#ffd23f", 5)}/>'
        f'<path d="M114 142 L142 142 L128 160 Z" {F("#ff8a3d", 4)}/>' + eyes(128, 116, 30, 11, w=4) + blush(128, 146, 52, 11)))
    o["sheep"] = ("Sheep", E(
        "".join(f'<circle cx="{128+math.cos(a)*76:.0f}" cy="{128+math.sin(a)*70:.0f}" r="36" {F("#fff")}/>' for a in [i * math.tau / 10 for i in range(10)])
        + f'<circle cx="128" cy="128" r="76" fill="#fff"/>'
        + f'<ellipse cx="128" cy="140" rx="46" ry="52" {F("#5a4a5a")}/>' + kawaii(128, 136, 0.8).replace(OL, "#fff")))
    o["tractor"] = ("Tractor", E(
        f'<rect x="40" y="120" width="140" height="60" rx="10" {F("#ff4d5a")}/>'
        f'<path d="M120 120 L120 56 L190 56 L196 120 Z" {F("#ff4d5a")}/><rect x="132" y="68" width="48" height="40" rx="6" {F("#c8f1ff", 4)}/>'
        f'<rect x="60" y="90" width="12" height="32" {F("#4b4766", 4)}/>'
        f'<circle cx="168" cy="186" r="44" {F("#3c3a59")}/><circle cx="168" cy="186" r="18" {F("#ffd23f", 4)}/>'
        f'<circle cx="64" cy="200" r="28" {F("#3c3a59")}/><circle cx="64" cy="200" r="11" {F("#ffd23f", 4)}/>' + kawaii(90, 150, 0.55)))
    o["barn"] = ("Barn", E(
        f'<path d="M24 110 L128 30 L232 110 L220 110 L220 228 L36 228 L36 110 Z" {F("#e5487a")}/>'
        f'<path d="M24 110 L128 30 L232 110" fill="none" stroke="#fff" stroke-width="12" stroke-linejoin="round"/>'
        f'<rect x="88" y="150" width="80" height="78" {F("#fff", 5)}/><path d="M88 150 L168 228 M168 150 L88 228" stroke="#e5487a" stroke-width="8"/>'
        + kawaii(128, 100, 0.7)))
    o["carrot"] = ("Carrot", E(
        f'<path d="M128 70 Q100 20 92 40 Q110 56 116 72 M128 70 Q128 14 140 20 Q138 48 134 70 M128 70 Q160 30 170 46 Q150 60 140 76" {F("#5cd67a", 5)}/>'
        f'<path d="M84 80 Q128 60 172 80 Q160 160 132 236 Q124 240 120 232 Q96 160 84 80 Z" {F("#ff8a3d")}/>'
        f'<path d="M100 130 L116 128 M146 160 L134 160 M110 180 L122 180" stroke="#d9622a" stroke-width="5" stroke-linecap="round"/>' + kawaii(128, 108, 0.75)))
    o["corn"] = ("Corn", E(
        f'<path d="M128 230 Q60 200 70 110 Q100 170 128 180 Z" {F("#5cd67a")}/><path d="M128 230 Q196 200 186 110 Q156 170 128 180 Z" {F("#5cd67a")}/>'
        f'<ellipse cx="128" cy="116" rx="46" ry="92" {F("#ffd23f")}/>'
        + "".join(f'<circle cx="{x}" cy="{y}" r="7" fill="#ffb703"/>' for y in range(50, 190, 22) for x in (110, 128, 146) if (x - 128) ** 2 / 46 ** 2 + (y - 116) ** 2 / 92 ** 2 < 0.8)
        + kawaii(128, 118, 0.7)))
    o["egg"] = ("Egg", E(
        f'<path d="M128 26 Q200 30 206 140 Q206 230 128 232 Q50 230 50 140 Q56 30 128 26 Z" {F("#fff6e8")}/>'
        f'<path d="M80 100 Q88 70 110 56" fill="none" stroke="#fff" stroke-width="10" stroke-linecap="round"/>' + kawaii(128, 146, 1)))
    o["apple"] = ("Apple", E(
        f'<path d="M128 70 Q130 40 146 26" fill="none" {S(8)}/><path d="M134 56 Q170 30 190 50 Q166 74 134 56 Z" {F("#5cd67a", 5)}/>'
        f'<path d="M128 74 Q70 40 40 110 Q30 200 100 228 Q128 236 156 228 Q226 200 216 110 Q186 40 128 74 Z" {F("#ff4d5a")}/>'
        f'<ellipse cx="76" cy="110" rx="12" ry="22" fill="#fff" opacity=".5" transform="rotate(20 76 110)"/>' + kawaii(128, 146, 1)))
    o["duck"] = ("Duckling", E(
        f'<path d="M40 170 Q30 230 128 230 Q226 230 214 160 Q190 130 150 150 Q130 160 110 150 Q60 130 40 170 Z" {F("#ffe066")}/>'
        f'<circle cx="104" cy="100" r="58" {F("#ffe066")}/><path d="M50 100 Q26 110 32 120 Q46 124 58 114 Z" {F("#ff8a3d", 5)}/>'
        f'<path d="M150 180 Q190 160 200 190 Q180 196 150 180 Z" {F("#ffd23f", 4)}/>' + eyes(108, 92, 18, 8, w=4) + blush(108, 114, 30, 8)))
    o["sunflower"] = ("Sunflower", E(
        f'<path d="M128 150 L128 236" {S(12)}/><path d="M128 150 L128 236" stroke="#5cd67a" stroke-width="6"/>'
        f'<path d="M128 200 Q90 180 80 200 Q100 216 128 206" {F("#5cd67a", 5)}/>'
        + "".join(f'<ellipse cx="{128+math.cos(a)*60:.0f}" cy="{100+math.sin(a)*60:.0f}" rx="24" ry="14" transform="rotate({math.degrees(a):.0f} {128+math.cos(a)*60:.0f} {100+math.sin(a)*60:.0f})" {F("#ffd23f", 5)}/>' for a in [i * math.tau / 12 for i in range(12)])
        + f'<circle cx="128" cy="100" r="44" {F("#8b5a3c")}/>' + kawaii(128, 98, 0.75).replace(OL, "#fff3e0")))
    return o


def emoji_candy():
    o = {}
    o["lollipop"] = ("Lollipop", E(
        f'<rect x="120" y="140" width="16" height="96" rx="6" {F("#fff")}/>'
        f'<circle cx="128" cy="96" r="76" {F("#ff7ac0")}/>'
        f'<path d="M128 96 m-54 0 a54 54 0 0 1 108 0 a40 40 0 0 1 -80 0 a26 26 0 0 1 52 0 a12 12 0 0 1 -24 0" fill="none" stroke="#fff" stroke-width="10" stroke-linecap="round"/>'
        + kawaii(128, 100, 0.6)))
    o["cupcake"] = ("Cupcake", E(
        f'<path d="M60 130 L196 130 L180 228 L76 228 Z" {F("#5ad1ff")}/>'
        + "".join(f'<path d="M{x} 132 L{x+6} 226" stroke="#2ab0f0" stroke-width="5"/>' for x in (86, 112, 138, 162))
        + f'<path d="M50 132 Q40 90 80 86 Q84 46 128 50 Q172 46 176 86 Q216 90 206 132 Z" {F("#ffc2d4")}/>'
        f'<circle cx="128" cy="40" r="16" {F("#ff4d5a", 5)}/>' + kawaii(128, 100, 0.8)))
    o["gumdrop"] = ("Gumdrop", E(
        f'<path d="M40 220 Q40 50 128 46 Q216 50 216 220 Q128 236 40 220 Z" {F("#7be07a")}/>'
        + "".join(f'<circle cx="{x}" cy="{y}" r="4" fill="#fff"/>' for x, y in [(80, 120), (170, 100), (190, 180), (70, 190), (128, 70)])
        + kawaii(128, 150, 1)))
    o["candycane"] = ("Candy Cane", E(
        f'<path d="M110 236 L110 90 Q110 40 152 40 Q196 40 196 90" fill="none" {S(44)}/>'
        f'<path d="M110 236 L110 90 Q110 40 152 40 Q196 40 196 90" fill="none" stroke="#fff" stroke-width="30" stroke-linecap="round"/>'
        f'<path d="M110 236 L110 90 Q110 40 152 40 Q196 40 196 90" fill="none" stroke="#ff4d5a" stroke-width="30" stroke-dasharray="16 16" stroke-linecap="butt"/>'
        + kawaii(110, 150, 0.5)))
    o["icecream"] = ("Ice Cream", E(
        f'<path d="M78 130 L128 240 L178 130 Z" {F("#e2a04a")}/><path d="M96 150 L150 190 M120 140 L164 170 M92 170 L140 210" stroke="#c9852e" stroke-width="4"/>'
        f'<circle cx="128" cy="96" r="58" {F("#ffc2d4")}/><path d="M70 120 Q90 150 104 126 Q120 150 136 126 Q152 150 168 126 Q180 140 186 120" fill="#ffc2d4" {S(5)}/>'
        f'<circle cx="128" cy="40" r="14" {F("#ff4d5a", 5)}/>' + kawaii(128, 96, 0.8)))
    o["wrapped"] = ("Wrapped Candy", E(
        f'<path d="M70 128 L20 90 L30 128 L20 166 Z" {F("#ffd23f")}/><path d="M186 128 L236 90 L226 128 L236 166 Z" {F("#ffd23f")}/>'
        f'<ellipse cx="128" cy="128" rx="68" ry="56" {F("#ff9f68")}/>'
        f'<path d="M96 80 L84 176 M160 80 L172 176" stroke="#fff" stroke-width="10" opacity=".7"/>' + kawaii(128, 124, 0.9)))
    o["chocolate"] = ("Chocolate Bar", E(
        f'<rect x="54" y="40" width="148" height="190" rx="14" {F("#8b5a3c")}/>'
        + "".join(f'<rect x="{x}" y="{y}" width="56" height="40" rx="6" fill="#a8683a" stroke="#6b4429" stroke-width="3"/>' for x in (66, 134) for y in (52, 100))
        + f'<path d="M48 140 L208 140 L208 236 L48 236 Z" {F("#5ad1ff")}/>' + kawaii(128, 180, 0.8)))
    o["cottoncandy"] = ("Cotton Candy", E(
        f'<path d="M110 236 L96 140 L160 140 L146 236 Z" {F("#fff")}/><path d="M104 190 L152 190" stroke="#ff8fb8" stroke-width="8"/>'
        + "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>' for x, y, r, c in [(90, 100, 44, "#ffc2d4"), (160, 96, 46, "#c39bff"), (128, 60, 44, "#ffc2d4"), (128, 120, 48, "#e0c3ff")])
        + kawaii(128, 104, 0.8)))
    o["gummybear"] = ("Gummy Bear", E(
        f'<circle cx="92" cy="44" r="20" {F("#ff4d5a")}/><circle cx="164" cy="44" r="20" {F("#ff4d5a")}/>'
        f'<ellipse cx="80" cy="200" rx="26" ry="30" {F("#ff4d5a")}/><ellipse cx="176" cy="200" rx="26" ry="30" {F("#ff4d5a")}/>'
        f'<ellipse cx="128" cy="166" rx="62" ry="60" {F("#ff4d5a")}/>'
        f'<circle cx="128" cy="88" r="56" {F("#ff4d5a")}/>'
        f'<ellipse cx="104" cy="70" rx="10" ry="16" fill="#fff" opacity=".45"/>' + kawaii(128, 88, 0.8)))
    o["cookie"] = ("Cookie", E(
        f'<circle cx="128" cy="128" r="96" {F("#e2a04a")}/>'
        + "".join(f'<ellipse cx="{x}" cy="{y}" rx="12" ry="9" fill="#6b4429"/>' for x, y in [(80, 80), (176, 90), (70, 160), (186, 170), (130, 200), (120, 60)])
        + kawaii(128, 128, 1)))
    o["jellybean"] = ("Jelly Bean", E(
        f'<path d="M60 150 Q30 80 100 60 Q150 50 160 90 Q170 120 200 110 Q240 120 220 180 Q190 230 120 214 Q70 204 60 150 Z" {F("#b388ff")}/>'
        f'<path d="M84 100 Q96 76 120 74" fill="none" stroke="#fff" stroke-width="10" stroke-linecap="round" opacity=".7"/>' + kawaii(136, 160, 0.8)))
    o["cake"] = ("Cake Slice", E(
        f'<path d="M30 120 L200 70 L226 120 Z" {F("#fff")}/>'
        f'<path d="M30 120 L226 120 L226 220 L30 220 Z" {F("#ffd6a5")}/>'
        f'<path d="M30 160 L226 160" stroke="#ff8fb8" stroke-width="14"/><path d="M30 120 L226 120 L226 220 L30 220 Z" fill="none" {S()}/>'
        f'<circle cx="190" cy="66" r="18" {F("#ff4d5a", 5)}/>' + kawaii(128, 186, 0.7)))
    return o


def emoji_dino():
    o = {}
    o["trex"] = ("T. Rex", E(dino("#5cd67a", "#c8f5b8", "rex")))
    o["stego"] = ("Stegosaurus", E(dino("#7bdff2", "#d4f6ff", "stego")))
    o["brachio"] = ("Long Neck", E(dino("#b388ff", "#e6d9ff", "long")))
    o["tricera"] = ("Triceratops", E(dino("#ff9f68", "#ffe0c8", "tri")))
    o["ptero"] = ("Pterodactyl", E(
        f'<path d="M128 130 Q60 60 10 90 Q50 110 60 150 Q100 130 128 150 Z" {F("#ff8fb8")}/>'
        f'<path d="M128 130 Q196 60 246 90 Q206 110 196 150 Q156 130 128 150 Z" {F("#ff8fb8")}/>'
        f'<ellipse cx="128" cy="150" rx="30" ry="44" {F("#ff7aa8")}/>'
        f'<circle cx="128" cy="96" r="34" {F("#ff7aa8")}/><path d="M150 90 L206 104 L150 112 Z" {F("#ffd23f", 5)}/><path d="M108 70 L80 40 L118 66 Z" {F("#ff7aa8", 5)}/>'
        + eyes(124, 90, 12, 7, w=3) + blush(124, 106, 18, 6)))
    o["dinoegg"] = ("Dino Egg", E(
        f'<path d="M128 26 Q200 30 206 140 Q206 230 128 232 Q50 230 50 140 Q56 30 128 26 Z" {F("#e8f5d0")}/>'
        + "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#9be08a"/>' for x, y, r in [(90, 80, 12), (166, 110, 16), (80, 170, 14), (160, 190, 10), (124, 60, 8)])
        + f'<path d="M58 130 L84 112 L106 134 L128 112 L150 134 L172 112 L198 130" fill="none" {S(5)}/>' + kawaii(128, 160, 0.9)))
    o["volcano"] = ("Volcano", E(
        f'<path d="M100 40 Q90 20 106 10 Q120 24 116 40 M150 44 Q160 20 176 26 Q168 40 156 50" fill="#c9c6d8" {S(4)}/>'
        f'<path d="M20 230 L96 70 L160 70 L236 230 Z" {F("#a8683a")}/>'
        f'<path d="M96 70 L160 70 L150 110 Q140 96 132 120 Q120 96 110 116 Z" {F("#ff7b25", 5)}/>' + kawaii(128, 170, 0.9)))
    o["bone"] = ("Bone", E(
        f'<g transform="rotate(-30 128 128)"><rect x="60" y="108" width="136" height="40" {F("#fff6e8")}/>'
        f'<circle cx="56" cy="104" r="26" {F("#fff6e8")}/><circle cx="56" cy="152" r="26" {F("#fff6e8")}/><circle cx="200" cy="104" r="26" {F("#fff6e8")}/><circle cx="200" cy="152" r="26" {F("#fff6e8")}/>'
        f'<rect x="58" y="112" width="140" height="32" fill="#fff6e8"/>' + kawaii(128, 124, 0.6) + '</g>'))
    o["footprint"] = ("Footprint", E(
        "".join(f'<ellipse cx="{x}" cy="{y}" rx="24" ry="34" transform="rotate({r} {x} {y})" {F("#5cd67a")}/>' for x, y, r in [(70, 92, -25), (128, 64, 0), (186, 92, 25)])
        + f'<path d="M128 234 Q56 232 64 168 Q72 120 128 120 Q184 120 192 168 Q200 232 128 234 Z" {F("#5cd67a")}/>'
        + kawaii(128, 176, 0.8)))
    o["palm"] = ("Palm Tree", E(
        f'<path d="M120 236 Q140 160 128 90" fill="none" {S(26)}/><path d="M120 236 Q140 160 128 90" fill="none" stroke="#a8683a" stroke-width="16"/>'
        + "".join(f'<path d="M128 90 Q{128+dx*0.5} {60+dy*0.5} {128+dx} {90+dy} Q{128+dx*0.6} {80+dy*0.2} 128 96 Z" {F("#3fb56b", 5)}/>' for dx, dy in [(-100, 20), (100, 20), (-70, -50), (70, -50), (0, -70)])
        + f'<circle cx="116" cy="102" r="12" {F("#8b5a3c", 4)}/><circle cx="140" cy="104" r="12" {F("#8b5a3c", 4)}/>' + kawaii(130, 180, 0.5)))
    o["fossil"] = ("Fossil Shell", E(
        f'<circle cx="128" cy="128" r="96" {F("#d9c6a5")}/>'
        f'<path d="M128 128 m-70 0 a70 70 0 1 1 140 0 a54 54 0 1 1 -108 0 a38 38 0 1 1 76 0 a22 22 0 1 1 -44 0" fill="none" stroke="#a8875a" stroke-width="8" stroke-linecap="round"/>'
        + kawaii(128, 150, 0.7)))
    o["fern"] = ("Fern", E(
        f'<path d="M128 236 Q120 140 150 30" fill="none" {S(8)}/>'
        + "".join(f'<ellipse cx="{128+side*28 + (y-236)*-0.1:.0f}" cy="{y}" rx="26" ry="10" transform="rotate({side*-25} {128+side*28 + (y-236)*-0.1:.0f} {y})" {F("#3fb56b", 4)}/>' for y in range(60, 220, 26) for side in (-1, 1))
        + kawaii(130, 140, 0.5)))
    return o


# ---------------------------------------------------------------- sparkly variants

def sparkly(content):
    """Rare gold version of an emoji: same art with a golden glow and sparkles."""
    inner = content.split("</defs>", 1)[1][:-len("</svg>")]
    defs = ('<radialGradient id="gold"><stop offset="0" stop-color="#fff6b0"/><stop offset=".7" stop-color="#ffd23f" stop-opacity=".8"/>'
            '<stop offset="1" stop-color="#ffb703" stop-opacity="0"/></radialGradient>'
            '<filter id="warm"><feColorMatrix type="matrix" values="1 .12 0 0 .04  0 1 0 0 .02  0 0 .8 0 0  0 0 0 1 0"/></filter>')
    body = (f'<circle cx="128" cy="128" r="126" fill="url(#gold)"/>'
            f'<g filter="url(#warm)">{inner}</g>'
            + sparkle_shape(36, 40, 18, "#fff6c8") + sparkle_shape(222, 60, 14, "#ffd23f")
            + sparkle_shape(216, 214, 18, "#fff6c8") + sparkle_shape(40, 200, 10, "#ffd23f"))
    return svg(256, 256, body, defs)


# ---------------------------------------------------------------- new worlds' backgrounds (900x1600)

def bg_ocean(night):
    rng = random.Random(5)
    d = grad("sky", [(0, "#0b2a52"), (.5, "#14457a"), (1, "#1a5a7a")] if night else [(0, "#7fe0ff"), (.5, "#3ab4e8"), (1, "#1f86c4")])
    b = '<rect width="900" height="1600" fill="url(#sky)"/>'
    for i in range(6):
        x = 80 + i * 150
        b += f'<path d="M{x} 0 L{x+60} 0 L{x+200} 1100 L{x+100} 1100 Z" fill="#fff" opacity="{.04 if night else .12}"/>'
    sand = "#7a6a4a" if night else "#ffe0a3"
    b += f'<path d="M0 1240 Q220 1180 450 1230 Q700 1280 900 1220 L900 1600 L0 1600 Z" {F(sand, 5)}/>'
    for x, h, c in [(60, 300, "#3fb56b"), (140, 220, "#5cd67a"), (780, 340, "#3fb56b"), (850, 240, "#5cd67a"), (690, 200, "#2fa060")]:
        c = shade(c, .45) if night else c
        p = f"M{x} 1260"
        for k in range(1, 9):
            p += f" Q{x + (24 if k % 2 else -24)} {1260 - h*(k-.5)/8} {x} {1260 - h*k/8}"
        b += f'<path d="{p}" fill="none" stroke="{OL}" stroke-width="24" stroke-linecap="round"/><path d="{p}" fill="none" stroke="{c}" stroke-width="14" stroke-linecap="round"/>'
    for x, y, r, c in [(300, 1290, 60, "#ff7a9a"), (560, 1300, 50, "#ffb03a"), (420, 1330, 34, "#b388ff")]:
        c = shade(c, .5) if night else c
        b += f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r*0.6}" {F(c, 5)}/>'
    for _ in range(30):
        x, y, r = rng.uniform(20, 880), rng.uniform(100, 1200), rng.uniform(4, 14)
        b += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.0f}" fill="none" stroke="#fff" stroke-width="3" opacity=".5"/>'
    b += f'<path d="M150 1480 l30 -10 l10 -30 l10 30 l30 10 l-30 10 l-10 30 l-10 -30 Z" fill="#ff9f68" {S(4)}/>'
    return svg(900, 1600, b, d)


def bg_space(night):
    rng = random.Random(6)
    d = grad("sky", [(0, "#0a0620"), (.6, "#1d1250"), (1, "#3a1f6e")] if night else [(0, "#1b1050"), (.6, "#3a2390"), (1, "#7a3fc8")])
    b = '<rect width="900" height="1600" fill="url(#sky)"/>' + stars(rng, 140, 1300)
    b += f'<circle cx="720" cy="260" r="110" {F("#ff9f68")}/><path d="M620 230 Q720 260 820 220 M612 290 Q720 320 826 284" fill="none" stroke="#e8784a" stroke-width="14"/>'
    b += f'<ellipse cx="720" cy="270" rx="190" ry="40" fill="none" stroke="#ffd166" stroke-width="12" transform="rotate(-12 720 270)"/>'
    b += f'<circle cx="160" cy="520" r="50" {F("#7bdff2")}/><circle cx="140" cy="505" r="10" fill="#5ab8d0"/>'
    ground = "#4a3f6e" if night else "#8a7ab8"
    b += f'<path d="M0 1220 Q300 1170 600 1210 Q780 1236 900 1200 L900 1600 L0 1600 Z" {F(ground, 5)}/>'
    for x, y, r in [(150, 1330, 50), (520, 1290, 34), (760, 1400, 60), (360, 1470, 40)]:
        b += f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r*.4}" fill="{shade(ground, .75)}" {S(4)}/>'
    b += f'<path d="M640 1210 L640 1080" {S(6)}/><path d="M640 1080 L720 1100 L640 1120 Z" {F("#ff5c5c", 4)}/>'
    return svg(900, 1600, b, d)


def bg_farm(night):
    rng = random.Random(7)
    d, b = sky(night, [(0, "#8fd3ff"), (.6, "#cdeeff"), (1, "#fff0c4")], [(0, "#141a44"), (.6, "#2c2f6e"), (1, "#4a3d7a")], rng)
    for col, y, amp in [("#a8e07a", 1000, 80), ("#7fcf5a", 1080, 60)]:
        c = shade(col, .4) if night else col
        b += f'<path d="M0 1600 L0 {y} Q225 {y-amp} 450 {y} T900 {y} L900 1600 Z" {F(c, 5)}/>'
    barn, roof = ("#e5487a", "#8f2f50") if not night else (shade("#e5487a", .45), shade("#8f2f50", .45))
    b += f'<path d="M560 1060 L560 860 L660 780 L760 860 L760 1060 Z" {F(barn, 5)}/><path d="M540 870 L660 770 L780 870" fill="none" stroke="{roof}" stroke-width="22" stroke-linejoin="round"/>'
    b += f'<rect x="620" y="960" width="80" height="100" {F("#fff6e0" if not night else "#8a8070", 5)}/><path d="M620 960 L700 1060 M700 960 L620 1060" stroke="{barn}" stroke-width="8"/>'
    win = "#ffe27a" if night else "#fff6e0"
    b += f'<circle cx="660" cy="870" r="22" {F(win, 4)}/>'
    fence = "#fff6e0" if not night else "#8a8070"
    b += f'<path d="M0 1150 L900 1150 M0 1190 L900 1190" stroke="{fence}" stroke-width="12"/>'
    for x in range(20, 900, 90):
        b += f'<rect x="{x}" y="1120" width="22" height="100" rx="6" {F(fence, 4)}/>'
    field = "#c98850" if not night else "#5a4a3a"
    b += f'<rect x="0" y="1260" width="900" height="340" fill="{field}"/>'
    for y in range(1290, 1600, 60):
        b += f'<path d="M0 {y} Q450 {y-14} 900 {y}" fill="none" stroke="{shade(field, .8)}" stroke-width="10"/>'
        for x in range(40, 900, 120):
            b += f'<path d="M{x} {y-6} q-10 -30 0 -40 q10 10 0 40" fill="{"#5cd67a" if not night else "#2f6b48"}"/>'
    return svg(900, 1600, b, d)


def bg_candy(night):
    rng = random.Random(8)
    d = grad("sky", [(0, "#2a1d5a"), (.6, "#5a2f7a"), (1, "#8a3f8a")] if night else [(0, "#ffb3e0"), (.6, "#ffd6f0"), (1, "#fff0d6")])
    b = '<rect width="900" height="1600" fill="url(#sky)"/>'
    if night:
        b += stars(rng, 60, 800)
    for x, y, s in [(180, 250, 1.3), (640, 420, 1.0)]:
        b += cloud(x, y, s, "#ffc2e8" if not night else "#7a4a9a", .9)
    for col, y in [("#ffc2d4", 1020), ("#c39bff", 1110), ("#9be0ff", 1200)]:
        c = shade(col, .45) if night else col
        b += f'<path d="M0 1600 L0 {y} Q150 {y-90} 300 {y} T600 {y} T900 {y} L900 1600 Z" {F(c, 5)}/>'
    for x, y, c in [(120, 1000, "#ff4d5a"), (780, 980, "#ffd23f"), (440, 1080, "#5ad1ff")]:
        c2 = shade(c, .5) if night else c
        b += f'<rect x="{x-8}" y="{y}" width="16" height="160" {F("#fff", 4)}/><circle cx="{x}" cy="{y}" r="70" {F(c2)}/>'
        b += f'<path d="M{x} {y} m-40 0 a40 40 0 0 1 80 0 a26 26 0 0 1 -52 0 a12 12 0 0 1 24 0" fill="none" stroke="#fff" stroke-width="10" stroke-linecap="round"/>'
    for x, c in [(260, "#7be07a"), (620, "#ff9f68"), (840, "#b388ff")]:
        c2 = shade(c, .5) if night else c
        b += f'<path d="M{x-60} 1330 Q{x-60} 1220 {x} 1218 Q{x+60} 1220 {x+60} 1330 Z" {F(c2)}/>'
    for _ in range(40):
        x, y = rng.uniform(0, 900), rng.uniform(1260, 1600)
        b += f'<rect x="{x:.0f}" y="{y:.0f}" width="18" height="6" rx="3" fill="{rng.choice(["#fff", "#ffd23f", "#5ad1ff", "#ff7ac0"])}" transform="rotate({rng.randint(0, 180)} {x:.0f} {y:.0f})"/>'
    return svg(900, 1600, b, d)


def bg_dino(night):
    rng = random.Random(9)
    d, b = sky(night, [(0, "#ffb07a"), (.6, "#ffd6a5"), (1, "#fff0c4")], [(0, "#1a1440"), (.6, "#3a2a5a"), (1, "#5a3a5a")], rng)
    vol = "#8b5a3c" if not night else "#4a3a3a"
    b += f'<path d="M380 1000 L520 700 L620 700 L760 1000 Z" {F(vol, 5)}/><path d="M520 700 L620 700 L600 760 Q580 740 570 780 Q556 740 540 770 Z" {F("#ff7b25", 5)}/>'
    b += f'<path d="M560 690 Q520 600 580 560 Q640 520 600 450" fill="none" stroke="#c9c6d8" stroke-width="40" stroke-linecap="round" opacity=".6"/>'
    for col, y in [("#7fcf5a", 1000), ("#4fae5a", 1100)]:
        c = shade(col, .4) if night else col
        b += f'<path d="M0 1600 L0 {y} Q200 {y-60} 450 {y} T900 {y} L900 1600 Z" {F(c, 5)}/>'
    for x, y, s in [(110, 1040, 1.2), (800, 1060, 1.0), (300, 1120, .7)]:
        trunk = "#a8683a" if not night else "#5a4030"
        b += f'<path d="M{x} {y+220*s} Q{x+30*s} {y+100*s} {x} {y}" fill="none" stroke="{OL}" stroke-width="{34*s}" stroke-linecap="round"/><path d="M{x} {y+220*s} Q{x+30*s} {y+100*s} {x} {y}" fill="none" stroke="{trunk}" stroke-width="{22*s}" stroke-linecap="round"/>'
        leaf = "#3fb56b" if not night else "#2f6b48"
        for dx, dy in [(-150, 30), (150, 30), (-100, -70), (100, -70), (0, -100)]:
            b += f'<path d="M{x} {y} Q{x+dx*0.5*s} {y+(dy-40)*0.5*s} {x+dx*s} {y+dy*s} Q{x+dx*0.6*s} {y+(dy-10)*0.3*s} {x} {y+8} Z" {F(leaf, 5)}/>'
    for _ in range(18):
        x, y = rng.uniform(0, 900), rng.uniform(1200, 1580)
        b += f'<path d="M{x:.0f} {y:.0f} q-20 -40 0 -70 q20 30 0 70" fill="{"#5cd67a" if not night else "#2f6b48"}" {S(3)}/>'
    return svg(900, 1600, b, d)


# ---------------------------------------------------------------- hero parts

CAPES = {"blue": "#3a86ff", "red": "#ff4d5a", "green": "#2fb36d", "purple": "#8f5bd6", "orange": "#ff8a3d", "pink": "#ff7ac0"}
BRUSHES = {"pink": "#ff5c8a", "blue": "#3a86ff", "green": "#5cd67a", "yellow": "#ffd23f", "purple": "#b388ff"}
HERO_POSES = ["ready", "cheer", "wait", "swish", "sleep"]
BRUSH_POSES = ["ready", "cheer", "wait"]


def hats():
    h = {}
    h["crown"] = (f'<path d="M100 74 L96 26 L122 50 L150 14 L178 50 L204 26 L200 74 Q150 60 100 74 Z" {F("#ffd23f")}/>'
                  f'<circle cx="150" cy="42" r="8" {F("#ff4d5a", 4)}/><circle cx="116" cy="62" r="5" fill="#5ad1ff"/><circle cx="184" cy="62" r="5" fill="#5cd67a"/>')
    h["cap"] = (f'<path d="M86 84 Q90 30 150 30 Q210 30 214 84 Q150 70 86 84 Z" {F("#ff4d5a")}/>'
                f'<path d="M200 80 Q250 76 262 92 Q236 100 204 92 Z" {F("#ff4d5a")}/>'
                f'<circle cx="150" cy="30" r="8" {F("#ff4d5a", 4)}/><path d="M150 34 L150 76" stroke="#d93a47" stroke-width="5"/>')
    h["wizard"] = (f'<path d="M84 86 Q150 64 216 86 L170 4 Q150 -6 140 10 Z" {F("#8f5bd6")}/>'
                   f'<path d="M80 84 Q150 60 220 84 Q224 96 210 98 Q150 80 90 98 Q76 96 80 84 Z" {F("#b388ff")}/>'
                   + star_path(156, 50, 14, 6, "#ffd23f") + sparkle_shape(128, 70, 6, "#fff6c8"))
    h["headband"] = (f'<path d="M80 92 Q150 70 220 92 L218 110 Q150 90 82 110 Z" {F("#ff5c8a")}/>'
                     f'<path d="M216 96 Q250 100 262 124 Q240 120 222 108 Z" {F("#ff5c8a", 5)}/><path d="M218 104 Q246 120 250 146 Q232 132 220 112 Z" {F("#ff5c8a", 5)}/>'
                     + star_path(150, 92, 12, 5, "#ffd23f"))
    h["bunny"] = (f'<ellipse cx="116" cy="34" rx="18" ry="46" {F("#fff")} transform="rotate(-12 116 34)"/><ellipse cx="116" cy="38" rx="8" ry="30" fill="#ffb4c8" transform="rotate(-12 116 38)"/>'
                  f'<ellipse cx="184" cy="34" rx="18" ry="46" {F("#fff")} transform="rotate(12 184 34)"/><ellipse cx="184" cy="38" rx="8" ry="30" fill="#ffb4c8" transform="rotate(12 184 38)"/>'
                  f'<path d="M94 80 Q150 56 206 80" fill="none" {S(14)}/><path d="M94 80 Q150 56 206 80" fill="none" stroke="#ff7ac0" stroke-width="7"/>')
    h["pirate"] = (f'<path d="M70 82 Q150 10 230 82 Q150 64 70 82 Z" {F("#3c3a59")}/>'
                   f'<path d="M70 82 Q150 64 230 82" fill="none" stroke="#ffd23f" stroke-width="6"/>'
                   f'<circle cx="150" cy="50" r="10" fill="#fff"/><path d="M142 62 L158 62" stroke="#fff" stroke-width="4"/>')
    return h


def hero_files(write):
    for name, col in CAPES.items():
        write(f"hero/cape_{name}.svg", buddy("ready", cape_color=col, layer="cape"))
    for pose in HERO_POSES:
        write(f"hero/body_{pose}.svg", buddy(pose, layer="body"))
    for name, col in BRUSHES.items():
        for pose in BRUSH_POSES:
            write(f"hero/brush_{name}_{pose}.svg", buddy(pose, brush_color=col, layer="brush"))
    for name, body in hats().items():
        write(f"hero/hat_{name}.svg", svg(300, 320, body))
    return {"capes": list(CAPES), "brushes": list(BRUSHES), "hats": ["none", *hats().keys()],
            "poses": HERO_POSES, "brushPoses": BRUSH_POSES}


def extra_icons():
    return {
        "bolt": svg(120, 120,
                    '<defs><radialGradient id="b"><stop offset="0" stop-color="#fff"/><stop offset=".55" stop-color="#9ff7ff"/>'
                    '<stop offset="1" stop-color="#5ad1ff" stop-opacity="0"/></radialGradient></defs>'
                    '<circle cx="60" cy="60" r="58" fill="url(#b)"/>' + sparkle_shape(60, 60, 30, "#ffffff").replace(f'stroke="{OL}"', 'stroke="#2ab0f0"')),
        "sun_sticker": svg(200, 200,
                           "".join(f'<path d="M{100+math.cos(a)*62:.0f} {100+math.sin(a)*62:.0f} L{100+math.cos(a+0.22)*92:.0f} {100+math.sin(a+0.22)*92:.0f} L{100+math.cos(a+0.44)*62:.0f} {100+math.sin(a+0.44)*62:.0f} Z" fill="#ffb03a" {S(4)}/>'
                                   for a in [i * math.tau / 10 for i in range(10)])
                           + f'<circle cx="100" cy="100" r="62" fill="#ffd23f" {S(6)}/>'
                           + eyes(100, 94, 20, 8, "closed", w=4) + smile(100, 112, 14, 7, sw=4)),
        "mystery_gold": svg(200, 200,
                            f'<circle cx="100" cy="100" r="84" fill="#fff6d6" stroke="#f2c84b" stroke-width="6" stroke-dasharray="14 10"/>'
                            f'<path d="M76 78 Q76 50 102 50 Q128 50 128 76 Q128 94 106 102 L104 118" fill="none" stroke="#f2c84b" stroke-width="14" stroke-linecap="round"/>'
                            f'<circle cx="104" cy="146" r="9" fill="#f2c84b"/>' + sparkle_shape(160, 40, 12, "#ffd23f")),
        "plus": svg(100, 100, f'<circle cx="50" cy="50" r="44" fill="#5cd67a" {S(6)}/><path d="M50 28 L50 72 M28 50 L72 50" stroke="#fff" stroke-width="12" stroke-linecap="round"/>'),
    }


MORE_WORLDS = [
    ("ocean", "The Ocean", bg_ocean, emoji_ocean),
    ("space", "Outer Space", bg_space, emoji_space),
    ("farm", "The Farm", bg_farm, emoji_farm),
    ("candy", "Candy Land", bg_candy, emoji_candy),
    ("dino", "Dino Valley", bg_dino, emoji_dino),
]
EXTRA_FOR = {"street": emoji_street_extra, "forest": emoji_forest_extra, "city": emoji_city_extra}
