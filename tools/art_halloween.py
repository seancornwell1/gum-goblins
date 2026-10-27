"""Halloween edition art for tools/gen_art.py: a pumpkin-patch world, goblins
in costumes, a vampire big goblin, 12 limited emoji, hero items and a
Halloween home screen. Spooky-cute, never scary."""
import math
import random

from gen_art import (OL, S, svg, E, kawaii, eyes, blush, smile, sparkle_shape, grad, stars, shade,
                     goblin_a, goblin_b, goblin_c, goblin_sneaky, goblin_big)

ORANGE, DARK, NIGHT_PURPLE = "#ff8a1f", "#3c3459", "#2b1a4f"


def F(c, w=6):
    return f'fill="{c}" {S(w)}'


# ---------------------------------------------------------------- shared shapes

def pumpkin(cx, cy, r, face=True, glow=False, s=1.0):
    out = ""
    if glow:
        out += f'<circle cx="{cx}" cy="{cy}" r="{r*1.7}" fill="#ffb84a" opacity=".25"/>'
    out += f'<path d="M{cx} {cy-r*0.9} Q{cx+r*0.1} {cy-r*1.35} {cx+r*0.3} {cy-r*1.4}" fill="none" stroke="#2f7d4a" stroke-width="{r*0.18:.1f}" stroke-linecap="round"/>'
    for dx, rx in [(-0.45, 0.6), (0.45, 0.6), (0, 0.55)]:
        out += f'<ellipse cx="{cx+dx*r:.1f}" cy="{cy}" rx="{rx*r:.1f}" ry="{r*0.85:.1f}" {F(ORANGE, max(3, r*0.08))}/>'
    if face:
        e = r * 0.22
        out += (f'<path d="M{cx-r*0.45} {cy-r*0.05} l{e} {-e*1.3} l{e} {e*1.3} Z" fill="#5a2a10"/>'
                f'<path d="M{cx+r*0.45} {cy-r*0.05} l{-e} {-e*1.3} l{-e} {e*1.3} Z" fill="#5a2a10"/>'
                f'<path d="M{cx-r*0.45} {cy+r*0.25} Q{cx} {cy+r*0.7} {cx+r*0.45} {cy+r*0.25} Q{cx} {cy+r*0.45} {cx-r*0.45} {cy+r*0.25} Z" fill="#5a2a10"/>')
        if glow:
            out = out.replace('fill="#5a2a10"', 'fill="#ffe27a"')
    return out


def ghost(cx, cy, r, op=1.0):
    return (f'<g opacity="{op}"><path d="M{cx-r} {cy+r} L{cx-r} {cy} Q{cx-r} {cy-r*1.1} {cx} {cy-r*1.1} Q{cx+r} {cy-r*1.1} {cx+r} {cy} '
            f'L{cx+r} {cy+r} Q{cx+r*0.66} {cy+r*0.7} {cx+r*0.33} {cy+r} Q{cx} {cy+r*0.7} {cx-r*0.33} {cy+r} Q{cx-r*0.66} {cy+r*0.7} {cx-r} {cy+r} Z" '
            f'{F("#fbf7ff", max(3, r*0.1))}/>' + kawaii(cx, cy - r * 0.2, r / 70) + '</g>')


def bat(cx, cy, s, col=DARK):
    return (f'<g transform="translate({cx} {cy}) scale({s})">'
            f'<path d="M0 0 Q-20 -24 -48 -16 Q-40 -6 -44 6 Q-30 0 -26 12 Q-14 2 0 8 Q14 2 26 12 Q30 0 44 6 Q40 -6 48 -16 Q20 -24 0 0 Z" fill="{col}"/>'
            f'<circle cx="0" cy="2" r="9" fill="{col}"/><path d="M-6 -6 L-4 -12 L-1 -6 M6 -6 L4 -12 L1 -6" fill="{col}"/>'
            f'<circle cx="-3" cy="1" r="1.8" fill="#ffd23f"/><circle cx="3" cy="1" r="1.8" fill="#ffd23f"/></g>')


def witch_hat(cx, base, w, col="#5a3a8a", band=ORANGE):
    return (f'<ellipse cx="{cx}" cy="{base}" rx="{w}" ry="{w*0.2}" {F(col)}/>'
            f'<path d="M{cx-w*0.5} {base-2} Q{cx-w*0.3} {base-w*0.9} {cx+w*0.1} {base-w*1.3} Q{cx+w*0.45} {base-w*1.4} {cx+w*0.6} {base-w*1.1} '
            f'Q{cx+w*0.3} {base-w*1.0} {cx+w*0.45} {base-2} Z" {F(col)}/>'
            f'<path d="M{cx-w*0.46} {base-w*0.18} Q{cx} {base-w*0.3} {cx+w*0.44} {base-w*0.18} L{cx+w*0.44} {base-w*0.02} Q{cx} {base-w*0.12} {cx-w*0.48} {base-w*0.02} Z" fill="{band}"/>'
            + sparkle_shape(cx + w * 0.15, base - w * 0.6, w * 0.12, "#ffd23f"))


# ---------------------------------------------------------------- goblins in costumes

def dress(content, behind="", front=""):
    return content.replace("</defs>", "</defs>" + behind, 1)[:-len("</svg>")] + front + "</svg>"


def bat_wings(cx, cy, span, col=DARK):
    return (f'<path d="M{cx-span*0.2} {cy} Q{cx-span*0.6} {cy-span*0.6} {cx-span} {cy-span*0.35} Q{cx-span*0.85} {cy-span*0.1} {cx-span*0.92} {cy+span*0.1} '
            f'Q{cx-span*0.7} {cy} {cx-span*0.66} {cy+span*0.2} Q{cx-span*0.45} {cy+span*0.08} {cx-span*0.2} {cy+span*0.25} Z" {F(col)}/>'
            f'<path d="M{cx+span*0.2} {cy} Q{cx+span*0.6} {cy-span*0.6} {cx+span} {cy-span*0.35} Q{cx+span*0.85} {cy-span*0.1} {cx+span*0.92} {cy+span*0.1} '
            f'Q{cx+span*0.7} {cy} {cx+span*0.66} {cy+span*0.2} Q{cx+span*0.45} {cy+span*0.08} {cx+span*0.2} {cy+span*0.25} Z" {F(col)}/>')


def pumpkin_cap(cx, top, w):
    return (f'<path d="M{cx} {top} Q{cx+4} {top-24} {cx+16} {top-30}" fill="none" stroke="#2f7d4a" stroke-width="9" stroke-linecap="round"/>'
            f'<path d="M{cx+4} {top-14} Q{cx+34} {top-34} {cx+46} {top-12} Q{cx+22} {top-4} {cx+4} {top-14} Z" {F("#5cd67a", 4)}/>'
            f'<path d="M{cx-w} {top+w*0.55} Q{cx-w} {top} {cx} {top} Q{cx+w} {top} {cx+w} {top+w*0.55} Q{cx} {top+w*0.35} {cx-w} {top+w*0.55} Z" {F(ORANGE)}/>'
            f'<path d="M{cx-w*0.45} {top+w*0.45} Q{cx-w*0.45} {top+w*0.1} {cx-w*0.2} {top+w*0.04} M{cx+w*0.45} {top+w*0.45} Q{cx+w*0.45} {top+w*0.1} {cx+w*0.2} {top+w*0.04}" '
            f'fill="none" stroke="#d96a10" stroke-width="5" stroke-linecap="round"/>')


def vampire_cape():
    return (f'<path d="M60 190 Q10 290 26 384 L374 384 Q390 290 340 190 Z" {F(DARK, 7)}/>'
            f'<path d="M84 210 Q50 290 60 370 L340 370 Q350 290 316 210 Z" fill="#c2304a"/>'
            f'<path d="M110 150 L30 50 L170 130 Z" {F(DARK, 6)}/><path d="M118 146 L58 74 L160 132 Z" fill="#c2304a"/>'
            f'<path d="M290 150 L370 50 L230 130 Z" {F(DARK, 6)}/><path d="M282 146 L342 74 L240 132 Z" fill="#c2304a"/>')


def costume_goblins(write):
    """Writes goblins/<name>_hw.svg (and _sleep, _hurt, _dizzy) for Halloween."""
    for mode, suf in [("open", ""), ("closed", "_sleep")]:
        write(f"goblins/a_hw{suf}.svg", dress(goblin_a(mode), front=witch_hat(150, 74, 66)))
        write(f"goblins/b_hw{suf}.svg", dress(goblin_b(mode), behind=bat_wings(150, 150, 140)))
        write(f"goblins/c_hw{suf}.svg", dress(goblin_c(mode), front=pumpkin_cap(150, 62, 58)))
        write(f"goblins/sneaky_hw{suf}.svg", dress(goblin_sneaky(mode), front=witch_hat(150, 70, 52, "#2f6b48", "#b388ff")))
    for mode, suf in [("open", ""), ("squint", "_hurt"), ("dizzy", "_dizzy"), ("closed", "_sleep")]:
        write(f"goblins/big_hw{suf}.svg", dress(goblin_big(mode), behind=vampire_cape()))


# ---------------------------------------------------------------- world: Pumpkin Patch (900x1600)

def bg_halloween(night):
    rng = random.Random(31)
    d = grad("sky", [(0, "#0e0a24"), (.5, "#2b1a4f"), (1, "#4a2a5a")] if night
             else [(0, "#2b1a4f"), (.45, "#7a3a8a"), (1, "#ff9a4a")])
    b = '<rect width="900" height="1600" fill="url(#sky)"/>' + stars(rng, 60 if night else 25, 700)
    b += '<circle cx="700" cy="240" r="170" fill="#ffd27a" opacity=".18"/><circle cx="700" cy="240" r="120" fill="#ffe9a8"/>'
    b += '<circle cx="660" cy="210" r="18" fill="#f2d48a"/><circle cx="740" cy="280" r="26" fill="#f2d48a"/><circle cx="720" cy="190" r="10" fill="#f2d48a"/>'
    for x, y, s in [(560, 180, 0.9), (820, 330, 0.7), (250, 320, 1.0), (150, 200, 0.7), (420, 420, 0.6)]:
        b += bat(x, y, s, "#1e1636")
    hill = "#24183f" if night else "#3c2a63"
    b += f'<path d="M0 1080 Q200 900 420 960 Q640 1020 900 900 L900 1600 L0 1600 Z" fill="{hill}"/>'
    # a cute haunted house on the hill
    house, roof = ("#5a3a8a", "#2b1a4f") if not night else ("#3e2a62", "#1a1030")
    win = "#ffd84a"
    b += f'<rect x="560" y="760" width="220" height="200" {F(house, 5)}/>'
    b += f'<path d="M540 770 L670 650 L800 770 Z" {F(roof, 5)}/>'
    b += f'<rect x="590" y="640" width="70" height="150" {F(house, 5)}/><path d="M580 650 L625 570 L670 650 Z" {F(roof, 5)}/>'
    for wx, wy in [(605, 680), (590, 800), (700, 800)]:
        b += f'<rect x="{wx}" y="{wy}" width="40" height="46" rx="8" {F(win, 4)}/><path d="M{wx+20} {wy} L{wx+20} {wy+46} M{wx} {wy+23} L{wx+40} {wy+23}" stroke="{OL}" stroke-width="3"/>'
    b += f'<path d="M650 960 L650 890 Q670 870 690 890 L690 960 Z" {F("#8b5a3c", 4)}/>'
    # bare, curly trees
    for tx, flip in [(120, 1), (420, -1)]:
        b += (f'<path d="M{tx} 1100 Q{tx+10*flip} 980 {tx} 900 Q{tx-30*flip} 860 {tx-60*flip} 870 M{tx} 940 Q{tx+40*flip} 900 {tx+80*flip} 920 '
              f'Q{tx+100*flip} 900 {tx+96*flip} 880" fill="none" stroke="#1e1636" stroke-width="18" stroke-linecap="round"/>')
    ground = "#3a2a2a" if night else "#5a3a3a"
    b += f'<path d="M0 1200 Q450 1150 900 1200 L900 1600 L0 1600 Z" {F(ground, 5)}/>'
    b += '<path d="M0 1260 L900 1260 M0 1300 L900 1300" stroke="#2a1d1d" stroke-width="10"/>'
    for x in range(30, 900, 80):
        b += f'<path d="M{x} 1310 L{x} 1240 L{x+12} 1226 L{x+24} 1240 L{x+24} 1310 Z" fill="#2a1d1d"/>'
    vine = "#2f7d4a"
    b += f'<path d="M0 1420 Q150 1380 300 1430 T600 1420 T900 1440" fill="none" stroke="{vine}" stroke-width="8"/>'
    for x, y, r in [(110, 1430, 60), (330, 1460, 46), (560, 1420, 70), (790, 1470, 52), (220, 1540, 40), (680, 1560, 44)]:
        b += pumpkin(x, y, r, face=True, glow=night)
    for x, y, r in [(260, 640, 46), (840, 760, 34), (140, 520, 30)]:
        b += ghost(x, y, r, 0.9)
    return svg(900, 1600, b, d)


def bg_home_halloween():
    rng = random.Random(32)
    d = grad("sky", [(0, "#3a1f6e"), (.55, "#8a3a9a"), (1, "#ff9a4a")])
    b = '<rect width="900" height="1600" fill="url(#sky)"/>' + stars(rng, 50, 900)
    b += '<circle cx="720" cy="220" r="110" fill="#ffe9a8"/>'
    for x, y, s in [(560, 200, 1.0), (300, 160, 0.8), (160, 380, 0.7), (820, 420, 0.6), (420, 520, 0.5)]:
        b += bat(x, y, s, "#1e1636")
    b += f'<path d="M0 1380 Q450 1300 900 1380 L900 1600 L0 1600 Z" fill="#2b1a4f"/>'
    for x, y, r in [(120, 1430, 70), (360, 1480, 50), (640, 1440, 80), (840, 1500, 48)]:
        b += pumpkin(x, y, r, face=True, glow=True)
    return svg(900, 1600, b, d)


# ---------------------------------------------------------------- 12 limited emoji (256x256)

def emoji_halloween():
    o = {}
    o["jackolantern"] = ("Jack-o'-Lantern", E(pumpkin(128, 140, 92, face=False) + kawaii(128, 136, 1.1)))
    o["ghost"] = ("Little Ghost", E(ghost(128, 128, 88)))
    o["bat"] = ("Bat", E(bat(128, 120, 2.4, "#5a3a8a").replace('r="1.8"', 'r="0"')
                         + eyes(128, 120, 10, 6, w=3) + blush(128, 132, 18, 5) + smile(128, 128, 6, 3, sw=3)))
    o["candycorn"] = ("Candy Corn", E(
        f'<path d="M128 24 Q60 170 44 216 Q128 240 212 216 Q196 170 128 24 Z" {F("#fff")}/>'
        f'<path d="M84 128 Q128 140 172 128 Q196 170 212 216 Q128 240 44 216 Q60 170 84 128 Z" fill="{ORANGE}"/>'
        f'<path d="M58 180 Q128 196 198 180 Q206 200 212 216 Q128 240 44 216 Q50 200 58 180 Z" fill="#ffd23f"/>'
        f'<path d="M128 24 Q60 170 44 216 Q128 240 212 216 Q196 170 128 24 Z" fill="none" {S()}/>' + kawaii(128, 150, 0.8)))
    o["witchhat"] = ("Witch Hat", E(witch_hat(128, 200, 100) + kawaii(128, 150, 0.7).replace(OL, "#fff")))
    o["blackcat"] = ("Black Cat", E(
        f'<path d="M190 200 Q240 180 230 120 Q226 100 214 110 Q222 160 186 176" {F("#3c3459")}/>'
        f'<ellipse cx="128" cy="190" rx="70" ry="44" {F("#3c3459")}/>'
        f'<path d="M66 110 L74 40 L118 82 Z M190 110 L182 40 L138 82 Z" {F("#3c3459")}/>'
        f'<circle cx="128" cy="120" r="64" {F("#3c3459")}/>'
        f'<ellipse cx="104" cy="114" rx="14" ry="17" fill="#c8f56a"/><ellipse cx="152" cy="114" rx="14" ry="17" fill="#c8f56a"/>'
        f'<ellipse cx="104" cy="116" rx="5" ry="12" fill="{OL}"/><ellipse cx="152" cy="116" rx="5" ry="12" fill="{OL}"/>'
        f'<path d="M122 140 L134 140 L128 148 Z" fill="#ff8fb8"/>' + blush(128, 146, 40, 9)
        + f'<path d="M70 146 L40 140 M70 154 L42 160 M186 146 L216 140 M186 154 L214 160" stroke="#c9c6d8" stroke-width="3"/>'))
    o["spider"] = ("Friendly Spider", E(
        f'<path d="M128 10 L128 70" stroke="#c9c6d8" stroke-width="4"/>'
        + "".join(f'<path d="M128 140 Q{128+s*70} {100+k*18} {128+s*104} {150+k*24}" fill="none" {S(8)}/>' for s in (-1, 1) for k in range(4))
        + f'<circle cx="128" cy="140" r="62" {F("#5a3a8a")}/>' + kawaii(128, 136, 1)))
    o["cauldron"] = ("Cauldron", E(
        f'<circle cx="100" cy="56" r="20" {F("#7be07a", 4)}/><circle cx="150" cy="40" r="14" {F("#7be07a", 4)}/><circle cx="168" cy="74" r="10" {F("#7be07a", 4)}/>'
        f'<path d="M40 110 Q30 230 128 232 Q226 230 216 110 Z" {F("#3c3459")}/>'
        f'<ellipse cx="128" cy="110" rx="94" ry="22" {F("#3c3459")}/><ellipse cx="128" cy="110" rx="78" ry="14" fill="#7be07a"/>'
        f'<path d="M70 230 L60 248 M186 230 L196 248" {S(10)}/>' + kawaii(128, 170, 0.9).replace(OL, "#fff")))
    o["pail"] = ("Treat Bucket", E(
        f'<path d="M60 90 Q128 10 196 90" fill="none" {S(10)}/>'
        + pumpkin(128, 160, 80, face=False)
        + f'<ellipse cx="128" cy="92" rx="70" ry="14" {F("#5a2a10", 5)}/>'
        + "".join(f'<rect x="{x}" y="{y}" width="22" height="14" rx="6" fill="{c}" {S(3)} transform="rotate({r} {x} {y})"/>'
                  for x, y, c, r in [(90, 70, "#ff5c8a", -20), (120, 62, "#5ad1ff", 10), (150, 70, "#ffd23f", 30)])
        + kawaii(128, 160, 0.9)))
    o["haunted"] = ("Haunted House", E(
        f'<rect x="54" y="110" width="148" height="120" {F("#7a5ab8")}/>'
        f'<path d="M36 118 L128 40 L220 118 Z" {F("#3c3459")}/>'
        f'<rect x="70" y="130" width="34" height="38" rx="6" {F("#ffd84a", 4)}/><rect x="152" y="130" width="34" height="38" rx="6" {F("#ffd84a", 4)}/>'
        f'<path d="M108 230 L108 186 Q128 168 148 186 L148 230 Z" {F("#8b5a3c", 4)}/>'
        f'<circle cx="90" cy="152" r="8" fill="{OL}"/><circle cx="166" cy="152" r="8" fill="{OL}"/>'
        + blush(128, 176, 52, 9) + bat(186, 54, 0.8)))
    o["broom"] = ("Broomstick", E(
        f'<path d="M40 40 L160 160" stroke="{OL}" stroke-width="20" stroke-linecap="round"/><path d="M40 40 L160 160" stroke="#a8683a" stroke-width="10" stroke-linecap="round"/>'
        f'<path d="M150 140 L236 196 Q230 230 200 236 L140 160 Z" {F("#ffd166")}/>'
        f'<path d="M160 172 L216 222 M176 160 L226 206" stroke="#e2a04a" stroke-width="5"/>'
        f'<path d="M140 150 L170 170" {S(14)}/><path d="M140 150 L170 170" stroke="{ORANGE}" stroke-width="8"/>' + kawaii(196, 196, 0.5)))
    o["mummy"] = ("Mummy", E(
        f'<path d="M60 236 L60 110 Q60 40 128 40 Q196 40 196 110 L196 236 Z" {F("#f2ece0")}/>'
        + "".join(f'<path d="M60 {y} Q128 {y+14} 196 {y-6}" fill="none" stroke="#d9cfba" stroke-width="5"/>' for y in (80, 180, 210))
        + f'<rect x="76" y="100" width="104" height="44" rx="20" fill="#5a4a5a"/>'
        + eyes(128, 122, 24, 11, w=4) + blush(128, 160, 40, 9) + smile(128, 160, 10, 5, sw=4)))
    return o


# ---------------------------------------------------------------- hero items

def bat_cape():
    return (f'<path d="M96 120 C60 170 50 250 44 296 Q70 278 96 300 Q122 278 150 304 Q178 278 204 300 Q230 278 256 296 C250 250 240 170 204 120 Z" {F(DARK)}/>'
            f'<path d="M110 130 C84 180 74 250 70 282 Q96 270 112 286 M190 130 C216 180 226 250 230 282 Q204 270 188 286" fill="none" stroke="{ORANGE}" stroke-width="6" stroke-linecap="round"/>'
            f'<path d="M100 124 L64 70 L118 112 Z" {F(DARK, 5)}/><path d="M200 124 L236 70 L182 112 Z" {F(DARK, 5)}/>'
            f'<path d="M102 118 L78 84 L114 110 Z" fill="{ORANGE}"/><path d="M198 118 L222 84 L186 110 Z" fill="{ORANGE}"/>')


def hero_items(write, hero):
    shadow = '<ellipse cx="150" cy="310" rx="90" ry="9" fill="#000" opacity=".15"/>'
    write("hero/cape_bat.svg", svg(300, 320, shadow + bat_cape()))
    write("hero/hat_pumpkin.svg", svg(300, 320, pumpkin_cap(150, 34, 66)))
    hero["capes"].append("bat")
    hero["hats"].append("pumpkin")


# ---------------------------------------------------------------- everything

def halloween_files(write, sparkly):
    costume_goblins(write)
    write("worlds/halloween.svg", bg_halloween(False))
    write("worlds/halloween_night.svg", bg_halloween(True))
    write("worlds/home_halloween.svg", bg_home_halloween())
    items = []
    for eid, (label, content) in emoji_halloween().items():
        write(f"emoji/halloween/{eid}.svg", content)
        write(f"emoji/halloween/{eid}_gold.svg", sparkly(content))
        items.append({"id": f"halloween/{eid}", "name": label})
    return {"id": "halloween", "name": "Halloween", "event": "halloween", "emoji": items}
