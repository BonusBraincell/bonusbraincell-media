"""Custom scenes · Why is it called Black Friday? (v4, MYTH THEN MECHANISM in a MINIATURE WORLD)

A paper-cutout downtown street carries the story. The myth (a shop ledger flipping red to black) is stamped
"came later"; then the street fills with suburban shoppers' cars, an Army-Navy pennant adds the weekend crowd,
the jam locks up, a traffic officer works the corner, and the police nickname is stamped on the street.
Merchants hoist a "BIG FRIDAY" banner that peels off. A two-stop timeline (early 1960s -> late 1980s) shows the
name going national and the red-to-black story arriving last.
Environment: daylight. Yellow = the thing to track (the name / the jam). No real people, logos or artwork:
the officer is a faceless flat figure; the city is generic, labeled as an illustration.
"""
import math, random
from PIL import Image, ImageDraw
import world as WD
import design as DZ

Y = DZ.C["track"]; NAVY = DZ.C["bg"]
INK = (10, 30, 62); MUTED = (74, 96, 117); WHITE = (255, 255, 255)
RED = (214, 64, 58); BLACKINK = (22, 24, 30); GREEN = (39, 150, 90)
ROAD_Y = 1100; ROAD_H = 150
BLD = [(40, 420, (232, 214, 190)), (215, 540, (210, 180, 150)), (385, 470, (236, 226, 208)),
       (560, 600, (196, 170, 140)), (745, 500, (226, 204, 176)), (905, 450, (205, 186, 160))]
CAR_COLS = [(235, 87, 87), (47, 128, 237), (39, 174, 96), (242, 160, 60), (240, 240, 240), (130, 90, 200)]

# ---------------- pieces ----------------
def buildings(img, d, a=1.0, sign=None, sign_a=0.0):
    for k, (x, h, col) in enumerate(BLD):
        w = 165
        WD.shadow(img, lambda m: m.rectangle([x, ROAD_Y - h, x + w, ROAD_Y], fill=255), (8, 10), 10, 70)
    d = ImageDraw.Draw(img)
    for k, (x, h, col) in enumerate(BLD):
        w = 165
        d.rectangle([x, ROAD_Y - h, x + w, ROAD_Y], fill=col)
        for r in range(int((h - 120) / 78)):
            for c in range(3):
                wy = ROAD_Y - h + 30 + r * 78
                d.rectangle([x + 18 + c * 48, wy, x + 48 + c * 48, wy + 40], fill=(126, 150, 180))
        # shop front
        d.rectangle([x + 10, ROAD_Y - 110, x + w - 10, ROAD_Y], fill=WD.lerp(col, (60, 50, 40), 0.35))
        d.rectangle([x + 22, ROAD_Y - 96, x + w - 22, ROAD_Y - 14], fill=(170, 200, 222))
        d.polygon([(x + 4, ROAD_Y - 110), (x + w - 4, ROAD_Y - 110), (x + w - 18, ROAD_Y - 140), (x + 18, ROAD_Y - 140)],
                  fill=[(214, 64, 58), (47, 128, 237), (39, 150, 90)][k % 3])
    return ImageDraw.Draw(img)

def road(d, t=0.0):
    d.rectangle([0, ROAD_Y, 1080, ROAD_Y + ROAD_H], fill=(96, 102, 116))
    d.rectangle([0, ROAD_Y, 1080, ROAD_Y + 10], fill=(150, 156, 168))
    for x in range(-40, 1100, 120):
        d.rectangle([x, ROAD_Y + 80, x + 60, ROAD_Y + 88], fill=(236, 230, 200))

def car(d, x, y, col, s=1.0):
    w, h = 104 * s, 46 * s
    d.rounded_rectangle([x, y, x + w, y + h], radius=int(14 * s), fill=col)
    d.rounded_rectangle([x + 18 * s, y - 24 * s, x + 84 * s, y + 4 * s], radius=int(10 * s), fill=WD.lerp(col, WHITE, 0.45))
    for wx in (x + 22 * s, x + 82 * s):
        d.ellipse([wx - 12 * s, y + h - 12 * s, wx + 12 * s, y + h + 12 * s], fill=(30, 32, 40))

def traffic(d, t, n, jam, seed=3, lanes=(ROAD_Y + 26, ROAD_Y + 104)):
    """n cars per lane; jam 0 = flowing, 1 = bumper to bumper. Positions are deterministic in t."""
    rnd = random.Random(seed)
    for li, ly in enumerate(lanes):
        spacing = WD.lerp(260, 118, jam)
        speed = WD.lerp(180, 8, jam) * (1 if li == 0 else 0.8)
        off = (t * speed + li * 70) % spacing
        for k in range(int(1200 / spacing) + 2):
            x = -140 + k * spacing + off
            if k >= n + 2 and jam < 0.5:
                continue
            col = CAR_COLS[(k * 5 + li * 3 + seed) % len(CAR_COLS)]
            car(d, x, ly, col)

def officer(img, d, cx, base, s=1.0, wave=0.0):
    """Faceless flat traffic officer (cap, coat, white gloves) on a small round platform."""
    d.ellipse([cx - 90 * s, base - 20 * s, cx + 90 * s, base + 20 * s], fill=(236, 200, 70))
    d.rounded_rectangle([cx - 46 * s, base - 210 * s, cx + 46 * s, base - 10 * s], radius=int(26 * s), fill=(28, 44, 86))
    d.ellipse([cx - 36 * s, base - 286 * s, cx + 36 * s, base - 214 * s], fill=(214, 170, 130))
    d.rounded_rectangle([cx - 44 * s, base - 300 * s, cx + 44 * s, base - 262 * s], radius=int(10 * s), fill=(20, 32, 64))
    d.rectangle([cx - 50 * s, base - 268 * s, cx + 50 * s, base - 258 * s], fill=(20, 32, 64))
    d.ellipse([cx - 10 * s, base - 292 * s, cx + 10 * s, base - 274 * s], fill=Y)          # cap badge
    ang = math.radians(-20 - 70 * wave)
    sx, sy = cx + 40 * s, base - 190 * s
    ex, ey = sx + 120 * s * math.cos(ang), sy + 120 * s * math.sin(ang)
    d.line([(sx, sy), (ex, ey)], fill=(28, 44, 86), width=int(30 * s))
    d.ellipse([ex - 20 * s, ey - 20 * s, ex + 20 * s, ey + 20 * s], fill=WHITE)
    d.line([(cx - 40 * s, base - 190 * s), (cx - 70 * s, base - 80 * s)], fill=(28, 44, 86), width=int(30 * s))
    d.ellipse([cx - 90 * s, base - 100 * s, cx - 50 * s, base - 60 * s], fill=WHITE)

def stamp(img, cx, cy, text, col, t, at, rot=-8, size=110, w=None):
    """Rubber-stamp text that slams down at 'at' (scale 1.5 -> 1)."""
    u = WD.seg(t, at, at + 0.18)
    if u <= 0:
        return
    s = 1.5 - 0.5 * WD.ease_out(u)
    f = DZ.F(size, "Black")
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    tw = tmp.textlength(text, font=f)
    bw = int(w or tw + 80); bh = int(size * 1.5)
    lay = Image.new("RGBA", (bw, bh), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.rounded_rectangle([6, 6, bw - 6, bh - 6], radius=18, outline=col + (235,), width=10)
    ld.text((bw / 2, bh / 2), text, font=f, fill=col + (235,), anchor="mm")
    lay = lay.rotate(rot, expand=True, resample=Image.BICUBIC)
    lay = lay.resize((int(lay.width * s), int(lay.height * s)), Image.BICUBIC)
    img.paste(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)), lay)
    DZ.REG["text"].append(dict(box=[cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2], role="label", size=size, text=text[:60]))

def ledger(img, d, x, y, w, h, flip, e, title="STORE LEDGER"):
    """A shop ledger: the balance bar flips from red ink to black ink (the familiar story)."""
    WD.shadow(img, lambda m: m.rounded_rectangle([x, y, x + w, y + h], radius=26, fill=255), (0, 16), 20, 90)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x, y, x + w, y + h], radius=26, fill=(252, 250, 242), outline=(200, 190, 160), width=4)
    for k in range(5):
        d.line([(x + 30, y + 110 + k * 52), (x + w - 30, y + 110 + k * 52)], fill=(214, 226, 236), width=3)
    WD.T(d, (x + 40, y + 56), title, "badge", MUTED, "lm")
    col = WD.lerp(RED, BLACKINK, flip)
    word = "IN THE RED" if flip < 0.5 else "IN THE BLACK"
    d.rounded_rectangle([x + 40, y + h - 150, x + w - 40, y + h - 46], radius=18, fill=col)
    WD.T(d, (x + w / 2, y + h - 98), word, "label", WHITE, "mm", size=54)
    return d

# ---------------- scenes ----------------
def bf_hook(img, d, t, p, ctx):
    """Myth: a shop window ledger flips from red to black, labeled as the story you've heard."""
    e = ctx["env"]
    d = buildings(img, d)
    road(d); traffic(d, t, 2, 0.0)
    flip = 1.0 if ctx.get("cover") else WD.ease_io(WD.seg(t, p.get("flip_at", 2.0), p.get("flip_at", 2.0) + 0.6))
    bob = 0 if ctx.get("cover") else 6 * math.sin(t * 2.2)
    d = ledger(img, d, 190, 520 + bob, 700, 400, flip, e)
    WD.chip(d, (540, 975), "the story you've heard", e, fill=Y, fg=NAVY, role="label")
    return img

def bf_myth(img, d, t, p, ctx):
    """The ledger gets stamped CAME LATER; a police cap badge slides in as the real lead."""
    e = ctx["env"]
    d = buildings(img, d)
    road(d); traffic(d, t + 3, 3, 0.1)
    d = ledger(img, d, 190, 520, 700, 400, 1.0, e)
    stamp(img, 540, 720, "CAME LATER", RED, t, p.get("stamp_at", 0.8), size=96)
    d = ImageDraw.Draw(img)
    u = WD.ease_out(WD.seg(t, p.get("police_at", 2.4), p.get("police_at", 2.4) + 0.5))
    if u > 0.02:
        cx = 1300 - 500 * u
        officer(img, d, cx, ROAD_Y + 60, 1.1, wave=0.5 + 0.5 * math.sin(t * 5))
        WD.label(d, "police", (cx - 30, ROAD_Y - 260), (cx - 190, 980), e, "label", INK, a=u)
    return img

def bf_street(img, d, t, p, ctx):
    """Philadelphia, early 1960s: cars stream in from the suburbs; the street fills."""
    e = ctx["env"]
    d = buildings(img, d)
    road(d)
    jam = 0.55 * WD.ease_io(WD.seg(t, 0.8, p["_dur"]))
    traffic(d, t, 6, jam)
    WD.chip(d, (540, 560), "PHILADELPHIA · EARLY 1960s", e, fill=e["ink"], fg=WHITE, role="label")
    a = WD.ease_out(WD.seg(t, p.get("sub_at", 1.4), p.get("sub_at", 1.4) + 0.4))
    if a > 0.02:
        d.rounded_rectangle([90, 640, 560, 730], radius=18, fill=WD.lerp(e["bottom"], (39, 150, 90), a))
        WD.T(d, (325, 685), "FROM THE SUBURBS  →", "label", WHITE, "mm", size=36)
        WD.label(d, "shoppers + tourists", (700, ROAD_Y + 40), (640, 850), e, "label", INK, a=a)
    WD.T(d, (540, 1268), "Illustration: a generic downtown street", "source", MUTED, "mm")
    return img

def bf_game(img, d, t, p, ctx):
    """An Army-Navy pennant flies over the street; the lanes lock solid (gridlock)."""
    e = ctx["env"]
    d = buildings(img, d)
    road(d)
    g = p.get("grid_at", p["_dur"] * 0.6)
    jam = 0.55 + 0.45 * WD.ease_io(WD.seg(t, g - 0.8, g))
    traffic(d, t, 8, jam)
    u = WD.ease_out(WD.seg(t, 0.2, 0.8)); wav = math.sin(t * 4) * 10
    px, py = 150, 520
    if u > 0.02:
        d.line([(px, py), (px, py + 300)], fill=(90, 70, 50), width=10)
        L = 660 * u
        d.polygon([(px, py), (px + L, py + 70 + wav), (px, py + 150)], fill=(28, 44, 86))
        d.polygon([(px, py + 46), (px + L * 0.72, py + 72 + wav * 0.7), (px, py + 104)], fill=(236, 200, 70))
        if u > 0.9:
            WD.T(d, (px + 40, py + 75), "ARMY–NAVY GAME", "label", (28, 44, 86), "lm", size=34)
    WD.chip(d, (540, 790), "SATURDAY · in some years", e, fill=e["ink"], fg=WHITE, a=u, role="label")
    a = WD.ease_out(WD.seg(t, g, g + 0.3))
    if a > 0.02:
        WD.glow(img, 540, ROAD_Y + 80, 260, Y, int(70 * a))
        d = ImageDraw.Draw(img)
        WD.chip(d, (540, 980), "GRIDLOCK", e, fill=Y, fg=NAVY, a=a, role="label")
    return img

def bf_police(img, d, t, p, ctx):
    """The officer works the jammed corner; three problems pop; a long-shift clock; the nickname is stamped."""
    e = ctx["env"]
    d = buildings(img, d)
    road(d); traffic(d, t, 8, 1.0)
    officer(img, d, 850, ROAD_Y + 70, 1.2, wave=0.5 + 0.5 * math.sin(t * 6))
    items = [("traffic jams", p.get("jam_at", 0.2)), ("accidents", p.get("acc_at", 0.9)), ("shoplifters", p.get("shop_at", 1.6))]
    for k, (s_, at) in enumerate(items):
        a = WD.ease_out(WD.seg(t, at, at + 0.3))
        if a > 0.02:
            WD.chip(d, (300, 560 + k * 92), s_, e, fill=WHITE, fg=INK, role="label", a=a)
    c = WD.ease_out(WD.seg(t, p.get("shift_at", 2.4), p.get("shift_at", 2.4) + 0.4))
    if c > 0.02:
        cx, cy, r = 600, 640, 76
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=WHITE, outline=INK, width=8)
        hand = math.radians(-90 + 360 * WD.seg(t, p.get("shift_at", 2.4), p["_dur"]) * 1.5)
        d.line([(cx, cy), (cx + 60 * math.cos(hand), cy + 60 * math.sin(hand))], fill=RED, width=8)
        d.line([(cx, cy), (cx, cy - 44)], fill=INK, width=8)
        WD.T(d, (cx, cy + r + 40), "longer shifts", "label", INK, "mm", size=36)
    stamp(img, 470, 900, "BLACK FRIDAY", BLACKINK, t, p.get("name_at", p["_dur"] - 1.0), rot=-6, size=100)
    return img

def bf_banner(img, d, t, p, ctx):
    """Merchants hoist a BIG FRIDAY banner across the street; it peels off and drops."""
    e = ctx["env"]
    d = buildings(img, d)
    road(d); traffic(d, t, 8, 1.0)
    up = WD.ease_out(WD.seg(t, p.get("big_at", 1.0) - 0.3, p.get("big_at", 1.0) + 0.3))
    drop = WD.ease_io(WD.seg(t, p.get("fail_at", 3.0), p.get("fail_at", 3.0) + 0.9))
    by = 520 + 140 * up
    d.line([(60, 600), (60, ROAD_Y)], fill=(90, 70, 50), width=10)
    d.line([(1020, 600), (1020, ROAD_Y)], fill=(90, 70, 50), width=10)
    if up > 0.02:
        lay = Image.new("RGBA", (770, 170), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle([0, 0, 769, 169], radius=16, fill=(255, 255, 255, 255), outline=(39, 150, 90, 255), width=10)
        ld.text((385, 85), "BIG FRIDAY", font=DZ.F(104, "Black"), fill=(39, 150, 90, 255), anchor="mm")
        lay = lay.rotate(-28 * drop, expand=True, resample=Image.BICUBIC, center=(0, 0))
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * (1 - drop))))
        img.paste(lay, (140, int(by + 160 * drop ** 2)), lay)
        DZ.REG["text"].append(dict(box=[140, by, 910, by + 170], role="label", size=104, text="BIG FRIDAY"))
        d = ImageDraw.Draw(img)
    WD.chip(d, (540, 560), "the merchants' name", e, fill=e["ink"], fg=WHITE, a=up, role="label")
    a = WD.ease_out(WD.seg(t, p.get("fail_at", 3.0) + 0.5, p.get("fail_at", 3.0) + 0.9))
    if a > 0.02:
        WD.chip(d, (540, 1000), "didn't stick", e, fill=Y, fg=NAVY, a=a, role="label")
    return img

def bf_timeline(img, d, t, p, ctx):
    """Two stops on a track: early 1960s (police slang in Philadelphia) -> late 1980s (national + the red-to-black story)."""
    e = ctx["env"]
    y0 = 790; x0, x1 = 230, 790
    d.rounded_rectangle([x0 - 20, y0 - 10, x1 + 20, y0 + 10], radius=10, fill=WD.lerp(e["bottom"], INK, 0.25))
    prog = WD.ease_io(WD.seg(t, 0.3, p.get("nat_at", 1.5) + 0.3))
    d.rounded_rectangle([x0 - 20, y0 - 10, x0 + (x1 - x0) * prog, y0 + 10], radius=10, fill=Y)
    for x, top, sub, at in ((x0, "EARLY 1960s", "Philadelphia police slang", 0.0), (x1, "LATE 1980s", "used nationwide", p.get("nat_at", 1.5))):
        a = WD.ease_out(WD.seg(t, at, at + 0.35))
        d.ellipse([x - 26, y0 - 26, x + 26, y0 + 26], fill=WD.lerp(e["bottom"], INK, a))
        if a > 0.02:
            WD.T(d, (x, y0 - 140), top, "label", INK, "mm", size=52, maxw=380)
            WD.T(d, (x, y0 + 80), sub, "small", MUTED, "mm", maxw=320)
    # the new backstory arrives last: a small ledger flips red -> black at the late-1980s stop
    s = p.get("story_at", p["_dur"] - 1.6)
    a = WD.ease_out(WD.seg(t, s, s + 0.4))
    if a > 0.02:
        flip = WD.ease_io(WD.seg(t, s + 0.4, s + 1.0))
        d = ledger(img, d, 230, 935, 620, 320, flip, e, title="THE NEW BACKSTORY")
    car(d, x0 + (x1 - x0) * prog - 52, y0 - 76, Y)
    WD.chip(d, (540, 520), "WHERE THE NAME WENT", e, fill=e["ink"], fg=WHITE, role="label")
    return img

def bf_payoff(img, d, t, p, ctx):
    """Back on the street: the gridlocked cars, a yellow ring around the jam, the name on a street sign."""
    e = ctx["env"]
    d = buildings(img, d)
    road(d); traffic(d, t, 8, 1.0)
    z = 1.0 + 0.05 * WD.ease_io(WD.seg(t, 0, p["_dur"]))
    a = WD.ease_out(WD.seg(t, 0.2, 0.6))
    d.rounded_rectangle([40, ROAD_Y - 6, 1040, ROAD_Y + ROAD_H + 6], radius=30, outline=WD.lerp(e["bottom"], Y, a), width=12)
    # street sign
    d.line([(540, 640), (540, 900)], fill=(70, 80, 92), width=14)
    d.rounded_rectangle([230, 560, 850, 680], radius=14, fill=(26, 110, 70), outline=WHITE, width=6)
    WD.T(d, (540, 620), "BLACK FRIDAY", "label", WHITE, "mm", size=72)
    WD.chip(d, (540, 750), "named for a traffic jam", e, fill=Y, fg=NAVY, a=a, role="label")
    return WD.zoom(img, z, 540, 900)

# ---------------- cover ----------------
def bf_cover(img, d, t, p, ctx):
    """Living cover: the gridlocked street + officer + BLACK FRIDAY stamp (scene 5's function as art)."""
    e = ctx["env"]
    d = buildings(img, d)
    road(d); traffic(d, 0.0, 8, 1.0)
    # a second, wider jammed boulevard fills the lower grid crop (cover only)
    d.rectangle([0, ROAD_Y + ROAD_H, 1080, ROAD_Y + ROAD_H + 40], fill=(200, 196, 186))
    y2 = ROAD_Y + ROAD_H + 40
    d.rectangle([0, y2, 1080, y2 + 210], fill=(96, 102, 116))
    d.rectangle([0, y2 + 210, 1080, y2 + 226], fill=(150, 156, 168))
    d.rectangle([0, y2 + 226, 1080, 1920], fill=(232, 228, 218))
    for k, ly in enumerate((y2 + 34, y2 + 124)):
        for j in range(10):
            car(d, -60 + j * 120 + (k % 2) * 50, ly, CAR_COLS[(j * 5 + k * 2) % len(CAR_COLS)], 1.0)
    officer(img, d, 860, ROAD_Y + 70, 1.2, wave=1.0)
    stamp(img, 430, 880, "BLACK FRIDAY", BLACKINK, 1.0, 0.0, rot=-6, size=88)
    return img
