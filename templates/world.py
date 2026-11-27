#!/usr/bin/env python3
"""Bonus Braincell scene kit v4 (2026-11-26): illustrated, topic-specific scenes on top of design system v3.

v3 gave every episode the same navy stage and infographic primitives. v4 keeps the brand anchors (Inter type,
yellow = the thing to track, the mark lockup, the caption box) and lets each episode build its own world:
an environment (palette + texture), illustrated objects, labels with leader lines, counters, camera moves.

Episode-specific scene code lives next to the episode spec (scenes.py) and is called by render_episode.py through
the "custom" visual: {"visual": "custom", "params": {"fn": "s_hook", ...}}. Every drawing helper here registers its
text with design.REG so the layout QA still checks it against the platform guides.

Main helpers
  env(name) -> dict of RGB colors          background(name) -> Image        chrome(img, d, series, progress, env)
  lerp / clamp / ease_out / ease_io / back / seg(t, a, b)                 path_at(points, u)
  shadow(img, draw_fn, offset, blur, alpha)  glow(img, cx, cy, r, color, alpha)  rrect(d, box, r, fill, outline, w)
  label(d, text, at, to, env, role, color, a, side)  -> leader line + text, registered for QA
  number(v, decimals, prefix, suffix)       counter(t, start, dur, v0, v1)   zoom(img, z, cx, cy)
  T(d, xy, s, role, color, anchor, maxw, a) -> design.txt with an RGB color (works on light environments)
"""
import math, os, json, random
from PIL import Image, ImageDraw, ImageFilter
import design as DZ

W, H = DZ.W, DZ.H
ENVS = {k: v for k, v in DZ.DS.get("environments", {}).items() if not k.startswith("_")}
TRACK = DZ.C["track"]
NAVY = DZ.C["bg"]

def hx(h):
    return DZ.hx(h) if isinstance(h, str) else tuple(h)

def env(name=None):
    e = ENVS.get(name or "navy_classic", ENVS.get("navy_classic"))
    out = {k: hx(v) for k, v in e.items() if isinstance(v, str) and v.startswith("#")}
    out["support"] = [hx(c) for c in e.get("support", [])]
    out["light"] = bool(e.get("light"))
    out["texture"] = e.get("texture", "none")
    out["name"] = name or "navy_classic"
    out["accent"] = TRACK
    return out

# ---------- math / easing ----------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def lerp(a, b, u):
    if isinstance(a, (tuple, list)):
        return tuple(int(round(a[i] + (b[i] - a[i]) * clamp(u))) for i in range(len(a)))
    return a + (b - a) * u

def ease_out(u):
    u = clamp(u); return 1 - (1 - u) ** 3

def ease_io(u):
    u = clamp(u); return 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2

def back(u, s=1.6):
    u = clamp(u) - 1; return 1 + (s + 1) * u ** 3 + s * u ** 2

def seg(t, a, b):
    """0 before a, 1 after b, linear in between."""
    if b <= a:
        return 1.0 if t >= a else 0.0
    return clamp((t - a) / (b - a))

def path_at(pts, u):
    """Point at fraction u along a polyline (by length)."""
    u = clamp(u)
    L = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    tot = sum(L) or 1
    s = u * tot
    for i, l in enumerate(L):
        if s <= l or i == len(L) - 1:
            k = 0 if l == 0 else s / l
            return (pts[i][0] + (pts[i + 1][0] - pts[i][0]) * k, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * k)
        s -= l
    return pts[-1]

def number(v, decimals=0, prefix="", suffix=""):
    s = f"{abs(v):,.{decimals}f}"
    return ("-" if v < 0 else "") + prefix + s + suffix

def counter(t, start, dur, v0, v1):
    return v0 + (v1 - v0) * ease_out(seg(t, start, start + dur))

# ---------- backgrounds ----------
_bg = {}
def background(name=None, seed=7):
    e = env(name)
    key = e["name"]
    if key in _bg:
        return _bg[key].copy()
    img = Image.new("RGB", (W, H), e["top"])
    d = ImageDraw.Draw(img)
    for y in range(H):  # vertical gradient
        d.line([(0, y), (W, y)], fill=lerp(e["top"], e["bottom"], y / H))
    rnd = random.Random(seed)
    tex = e["texture"]
    if tex == "dots":
        for y in range(0, H, 60):
            for x in range(0, W, 60):
                d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=lerp(e["top"], e["ink"], 0.05))
    elif tex == "grid":
        for x in range(0, W, 54):
            d.line([(x, 0), (x, H)], fill=lerp(e["top"], e["ink"], 0.07 if x % 270 else 0.14), width=1 if x % 270 else 2)
        for y in range(0, H, 54):
            d.line([(0, y), (W, y)], fill=lerp(e["top"], e["ink"], 0.07 if y % 270 else 0.14), width=1 if y % 270 else 2)
    elif tex == "paper":
        noise = Image.effect_noise((W // 2, H // 2), 22).resize((W, H)).filter(ImageFilter.GaussianBlur(1.2))
        img = Image.composite(img, Image.new("RGB", (W, H), lerp(e["top"], (120, 100, 70), 0.10)), noise.point(lambda v: 200 + v // 5))
        d = ImageDraw.Draw(img)
        for _ in range(140):  # fibres
            x, y = rnd.randrange(W), rnd.randrange(H)
            ang = rnd.uniform(0, math.pi)
            l = rnd.uniform(8, 26)
            d.line([(x, y), (x + l * math.cos(ang), y + l * math.sin(ang))], fill=lerp(e["top"], (90, 70, 40), 0.12), width=1)
    elif tex == "stars":
        for _ in range(260):
            x, y = rnd.randrange(W), rnd.randrange(H)
            r = rnd.choice([1, 1, 1, 2, 2, 3])
            c = lerp(e["top"], (255, 255, 255), rnd.uniform(0.25, 0.8))
            d.ellipse([x - r, y - r, x + r, y + r], fill=c)
    elif tex == "floor":
        horizon = int(H * 0.57)
        for k in range(1, 22):  # perspective floor lines
            y = horizon + (H - horizon) * (k / 22) ** 1.7
            d.line([(0, y), (W, y)], fill=lerp(e["bottom"], e["ink"], 0.06), width=2)
        for k in range(-12, 13):
            d.line([(W / 2 + k * 30, horizon), (W / 2 + k * 260, H)], fill=lerp(e["bottom"], e["ink"], 0.05), width=2)
        # soft overhead lights
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
        for cx in (200, 540, 880):
            gd.ellipse([cx - 260, -200, cx + 260, 260], fill=(255, 196, 140, 26))
        g = g.filter(ImageFilter.GaussianBlur(70)); img.paste(g, (0, 0), g)
    # vignette
    v = Image.new("L", (W, H), 0); vd = ImageDraw.Draw(v)
    vd.ellipse([-W * 0.35, -H * 0.15, W * 1.35, H * 1.15], fill=255)
    v = v.filter(ImageFilter.GaussianBlur(160))
    dark = Image.new("RGB", (W, H), lerp(e["bottom"], (0, 0, 0), 0.35))
    img = Image.composite(img, dark, v)
    _bg[key] = img
    return img.copy()

# ---------- drawing helpers ----------
def rrect(d, box, r=24, fill=None, outline=None, width=0):
    d.rounded_rectangle([min(box[0], box[2]), min(box[1], box[3]), max(box[0], box[2]), max(box[1], box[3])],
                        radius=r, fill=fill, outline=outline, width=width)

def shadow(img, draw_fn, offset=(0, 18), blur=22, alpha=110):
    """draw_fn(mask_draw) draws the silhouette in white; a blurred dark copy is laid under it."""
    m = Image.new("L", (W, H), 0)
    draw_fn(ImageDraw.Draw(m))
    m = m.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: v * alpha // 255)
    sh = Image.new("RGB", (W, H), (0, 0, 0))
    img.paste(sh, offset, m)

def glow(img, cx, cy, r, color=None, alpha=80):
    color = color or TRACK
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse([cx - r, cy - r, cx + r, cy + r], fill=tuple(color) + (alpha,))
    g = g.filter(ImageFilter.GaussianBlur(r * 0.45))
    img.paste(g, (0, 0), g)

def T(d, xy, s, role="label", color=(244, 246, 251), anchor="mm", maxw=860, a=1.0, max_lines=None, size=None, hi="track"):
    """Text with an explicit RGB color (fades from the frame color under it is not attempted: a<1 dims toward navy)."""
    col = tuple(color)
    if a < 1:
        col = lerp(NAVY, col, a)
    return DZ.txt(d, xy, s, role, col, anchor, maxw, 1.0 if a > 0.5 else a, hi, max_lines, size)

def label(d, text, at, to, e, role="small", color=None, a=1.0, dot=True, line_w=4, maxw=420):
    """Leader-line label: a dot on the object (at) and text at 'to'. Text anchor side follows the line direction."""
    if a <= 0.02:
        return None
    color = color or e["ink"]
    lc = lerp(e["bottom"], color, 0.75 * a)
    d.line([at, to], fill=lc, width=line_w)
    if dot:
        d.ellipse([at[0] - 9, at[1] - 9, at[0] + 9, at[1] + 9], fill=lerp(e["bottom"], color, a))
    anchor = "lm" if to[0] >= at[0] else "rm"
    x = to[0] + (14 if anchor == "lm" else -14)
    return T(d, (x, to[1]), text, role, lerp(e["bottom"], color, a) if a < 1 else color, anchor, maxw)

def chip(d, xy, s, e, fill=None, fg=None, role="badge", a=1.0):
    fill = fill or (TRACK if not e["light"] else e["ink"])
    fg = fg or (NAVY if not e["light"] else e["top"])
    font, sz, lines, _ = DZ.fit(d, s, role, 860, 1)
    tw = d.textlength(DZ._plain(lines[0]), font=font)
    x, y = xy
    box = [x - tw / 2 - 22, y - sz / 2 - 12, x + tw / 2 + 22, y + sz / 2 + 12]
    d.rounded_rectangle(box, radius=(box[3] - box[1]) / 2, fill=lerp(e["bottom"], fill, a))
    T(d, (x, y), lines[0], role, lerp(fill, fg, a), "mm", 2000)
    return box

def zoom(img, z, cx=W / 2, cy=H / 2):
    """Camera push: scale the frame by z around (cx, cy). z=1 -> unchanged."""
    if abs(z - 1) < 1e-3:
        return img
    zw, zh = W / z, H / z
    l = clamp(cx - zw / 2, 0, W - zw); tp = clamp(cy - zh / 2, 0, H - zh)
    return img.crop((int(l), int(tp), int(l + zw), int(tp + zh))).resize((W, H), Image.BICUBIC)

def poly_round(cx, cy, w, h, r, n=10):
    """Points of a rounded rectangle (for polygons that need rotation or warping)."""
    pts = []
    for (qx, qy, a0) in ((cx + w / 2 - r, cy - h / 2 + r, -90), (cx + w / 2 - r, cy + h / 2 - r, 0),
                         (cx - w / 2 + r, cy + h / 2 - r, 90), (cx - w / 2 + r, cy - h / 2 + r, 180)):
        for k in range(n + 1):
            ang = math.radians(a0 + 90 * k / n)
            pts.append((qx + r * math.cos(ang), qy + r * math.sin(ang)))
    return pts

# ---------- chrome for any environment ----------
def chrome(img, d, series, progress, e, logo_path=None):
    lk = DZ.L["lockup"]; ph = DZ.L["progress_h"]
    ink = e["ink"]; muted = e["muted"]
    # soft scrim so the lockup reads on busy art
    sc = Image.new("RGBA", (W, 260), (0, 0, 0, 0)); sd = ImageDraw.Draw(sc)
    base = e["top"]
    for y in range(260):
        sd.line([(0, y), (W, y)], fill=tuple(base) + (int(150 * (1 - y / 260) ** 1.6),))
    img.paste(sc, (0, 0), sc)
    d.rectangle([0, 0, W, ph], fill=lerp(base, ink, 0.18))
    d.rectangle([0, 0, int(W * progress), ph], fill=TRACK)
    mk = DZ.mark(lk["mark_h"], logo_path)
    img.paste(mk, (lk["x"], lk["y"] - mk.height // 2), mk)
    x = lk["x"] + mk.width + lk["gap"]
    f = DZ.F(DZ.T["lockup"]["size"], DZ.T["lockup"]["weight"])
    d.text((x, lk["y"]), "BONUS BRAINCELL", font=f, fill=ink, anchor="lm")
    x += d.textlength("BONUS BRAINCELL", font=f) + 18
    d.text((x, lk["y"]), "·  " + series.upper(), font=DZ.F(DZ.T["lockup"]["size"], "Bold"), fill=muted, anchor="lm")


def kinetic_caption(img, text, age, e):
    """v4.1 kinetic caption: 1-3 words, Inter Black 84 px, white with a dark outline, numbers in yellow,
    centred at the caption line (y 1385), 0.12 s pop-in. Registered for layout QA."""
    if not text:
        return
    d = ImageDraw.Draw(img)
    size = 84
    f = DZ.F(size, "Black")
    nw = len(text.split())
    while d.textlength(text, font=f) + (nw - 1) * 16 > 660 and size > 52:
        size -= 4; f = DZ.F(size, "Black")
    s = 1.0 + 0.10 * (1 - ease_out(age / 0.12))
    words = text.split()
    gap = d.textlength(" ", font=f) + 16   # extra space so the outline doesn't fuse words
    widths = [d.textlength(w_, font=f) + gap for w_ in words]
    x = 540 - (sum(widths) - gap) / 2
    y = DZ.L["caption"]["center_y"]
    lay = Image.new("RGBA", (W, 260), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    for w_, ww in zip(words, widths):
        hot = any(ch.isdigit() for ch in w_) or any(ch in w_ for ch in "$¢%")
        ld.text((x, 130), w_, font=f, fill=TRACK if hot else (255, 255, 255), anchor="lm",
                stroke_width=7, stroke_fill=(6, 12, 28))
        x += ww
    if abs(s - 1) > 0.005:
        lay = lay.resize((int(W * s), int(260 * s)), Image.BICUBIC)
    img.paste(lay, (int(540 - lay.width / 2), int(y - lay.height / 2)), lay)
    tw = sum(widths) - gap
    DZ.REG["text"].append(dict(box=(540 - tw / 2, y - size * 0.6, 540 + tw / 2, y + size * 0.6), role="caption", size=size, text=text[:60]))
