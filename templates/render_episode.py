#!/usr/bin/env python3
"""Bonus Braincell episode renderer.

Usage: python3 render_episode.py episode.json OUTPUT_DIR [--cover OUT/cover.png] [--logo path/to/logo.png]

Reads an episode spec (scenes with narration, captions and a visual type),
generates narration with Kokoro TTS (Apache-2.0), draws 1080x1920 frames with
Pillow, encodes one file per scene, joins them, muxes audio, and writes
video.mp4, captions.srt, cover.png and images/ (one keyframe per scene).
"""
import json, math, os, subprocess, sys, wave, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
NAVY = (11, 31, 75)
NAVY2 = (18, 44, 102)
YELLOW = (255, 214, 10)
WHITE = (245, 247, 255)
MUTED = (150, 166, 205)
FONT_DIR = "/usr/share/fonts/opentype/inter/"

_fc = {}
def F(size, weight="Bold"):
    key = (size, weight)
    if key not in _fc:
        _fc[key] = ImageFont.truetype(f"{FONT_DIR}Inter-{weight}.otf", size)
    return _fc[key]

def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3

def appear(t, start, dur=0.45):
    return ease((t - start) / dur)

def text_center(d, xy, s, font, fill, anchor="mm"):
    d.text(xy, s, font=font, fill=fill, anchor=anchor)

def wrap(d, s, font, maxw):
    words, lines, cur = s.split(), [], ""
    for w_ in words:
        test = (cur + " " + w_).strip()
        if d.textlength(test, font=font) <= maxw:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines

def blend(c1, c2, a):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * a) for i in range(3))

# ---------- shared chrome ----------
_bg = None
def background():
    global _bg
    if _bg is None:
        img = Image.new("RGB", (W, H), NAVY)
        d = ImageDraw.Draw(img)
        for y in range(0, H, 60):
            for x in range(0, W, 60):
                d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=NAVY2)
        _bg = img
    return _bg.copy()

_logo = None
def logo_img(size, logo_path):
    global _logo
    if logo_path and os.path.exists(logo_path):
        im = Image.open(logo_path).convert("RGBA")
        im.thumbnail((size, size))
        return im
    # placeholder mark (replace by dropping logo.png into Settings/brand/)
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, size - 1, size - 1], fill=YELLOW)
    d.text((size / 2, size / 2), "BB", font=F(int(size * 0.42), "ExtraBold"), fill=NAVY, anchor="mm")
    return im

def chrome(img, d, series, progress, logo_path):
    d.rectangle([0, 0, W, 10], fill=NAVY2)
    d.rectangle([0, 0, int(W * progress), 10], fill=YELLOW)
    lg = logo_img(72, logo_path)
    img.paste(lg, (90, 196), lg)
    d.text((180, 232), "BONUS BRAINCELL", font=F(34, "ExtraBold"), fill=WHITE, anchor="lm")
    tw = d.textlength(series.upper(), font=F(26, "Bold"))
    d.rounded_rectangle([180, 262, 180 + tw + 32, 304], radius=21, fill=YELLOW)
    d.text((196, 283), series.upper(), font=F(26, "Bold"), fill=NAVY, anchor="lm")

def caption(img, text):
    if not text:
        return
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    font = F(54, "Bold")
    words = text.split()
    if d.textlength(text, font=font) <= 860 or len(words) < 2:
        lines = [text]
    else:  # two balanced lines: pick the break that minimizes the longer line
        best = None
        for k in range(1, len(words)):
            a, b = " ".join(words[:k]), " ".join(words[k:])
            w_ = max(d.textlength(a, font=font), d.textlength(b, font=font))
            if best is None or w_ < best[0]:
                best = (w_, [a, b])
        lines = best[1]
    lh = 70
    total = lh * len(lines)
    top = 1420 - total / 2
    maxw = max(d.textlength(l, font=font) for l in lines)
    d.rounded_rectangle([540 - maxw / 2 - 30, top - 22, 540 + maxw / 2 + 30, top + total + 14], radius=24, fill=(0, 0, 0, 120))
    for i, l in enumerate(lines):
        d.text((540, top + i * lh + lh / 2 - 4), l, font=font, fill=WHITE, anchor="mm")
    img.paste(ov, (0, 0), ov)

def tag(d, cx, cy, label, value, a=1.0, hl=True, w=360):
    col = YELLOW if hl else WHITE
    bg = blend(NAVY, col, a)
    d.rounded_rectangle([cx - w / 2, cy - 110, cx + w / 2, cy + 110], radius=34, fill=bg)
    d.ellipse([cx - w / 2 + 26, cy - 14, cx - w / 2 + 54, cy + 14], fill=NAVY)
    d.text((cx + 14, cy - 34), value, font=F(96, "ExtraBold"), fill=blend(bg, NAVY, a), anchor="mm")
    d.text((cx + 14, cy + 58), label, font=F(30, "Bold"), fill=blend(bg, NAVY, a), anchor="mm")

def note(d, s, y=1235):
    d.text((540, y), s, font=F(28, "Medium"), fill=MUTED, anchor="mm")

# ---------- scene visuals ----------
def v_hook(img, d, t, p):
    a1, a2 = 1.0, 1.0  # fully drawn from the first frame: no empty screen after the cover
    d.text((540, 470), p["title1"], font=F(92, "ExtraBold"), fill=WHITE, anchor="mm")
    d.text((540, 575), p["title2"], font=F(92, "ExtraBold"), fill=YELLOW, anchor="mm")
    tag(d, 300, 900, p["l1"], p["v1"], a1, True, 380)
    tag(d, 780, 900, p["l2"], p["v2"], a2, False, 380)
    if p.get("between", "≠"):
        d.text((540, 900), p.get("between", "≠"), font=F(120, "ExtraBold"), fill=YELLOW, anchor="mm")
    if p.get("note"):
        note(d, p["note"], 1120)

def v_offer(img, d, t, p):
    d.text((540, 430), p["kicker"], font=F(40, "Bold"), fill=YELLOW, anchor="mm")
    # moon
    d.ellipse([480, 480, 600, 600], fill=YELLOW)
    d.ellipse([515, 465, 635, 585], fill=NAVY)
    a1, a2, a3 = appear(t, 0.2), appear(t, 0.6), appear(t, 1.2)
    for i, (lab, x) in enumerate([(p["a"], 280), (p["b"], 800)]):
        a = [a1, a2][i]
        d.rounded_rectangle([x - 190, 680, x + 190, 820], radius=28, outline=blend(NAVY, WHITE, a), width=6)
        d.text((x, 750), lab, font=F(46, "Bold"), fill=blend(NAVY, WHITE, a), anchor="mm")
    d.text((540, 750), "+", font=F(80, "ExtraBold"), fill=blend(NAVY, YELLOW, a2), anchor="mm")
    d.line([540, 850, 540, 900 + 30 * a3], fill=blend(NAVY, YELLOW, a3), width=8)
    tag(d, 540, 1060, p["tag_label"], p["tag_value"], a3, True, 460)
    note(d, "Illustrative numbers", 1215)

def v_rows(img, d, t, p):
    d.text((540, 430), p["kicker"], font=F(40, "Bold"), fill=YELLOW, anchor="mm")
    hdr = p["header"]
    xs = [140, 560, 940]
    for x, h, an in zip(xs, hdr, ["lm", "mm", "rm"]):
        d.text((x, 520), h, font=F(30, "Bold"), fill=MUTED, anchor=an)
    for i, row in enumerate(p["rows"]):
        a = appear(t, 0.25 + i * 0.45)
        y = 600 + i * 120
        d.rounded_rectangle([110, y, 970, y + 96], radius=22, fill=blend(NAVY, NAVY2, a))
        for x, c, an in zip(xs, row, ["lm", "mm", "rm"]):
            d.text((x + (10 if an == "lm" else -10 if an == "rm" else 0), y + 48), c, font=F(42, "Bold"),
                   fill=blend(NAVY, YELLOW if an == "rm" else WHITE, a), anchor=an)
    note(d, p.get("note", "Illustrative numbers"), 1235)

def v_alloc(img, d, t, p):
    d.text((540, 430), p["kicker"], font=F(40, "Bold"), fill=YELLOW, anchor="mm")
    n, cols = 40, 8
    big = int(n * p["share_big"])
    a_split = appear(t, 1.0, 0.8)
    for i in range(n):
        r, c = divmod(i, cols)
        x0, y0 = 220 + c * 82, 520 + r * 82
        if i < big:
            dx, dy = -60 * a_split, 0
            col = YELLOW
        else:
            dx, dy = 60 * a_split, 60 * a_split
            col = blend(YELLOW, WHITE, a_split)
        a = appear(t, 0.05 + i * 0.015, 0.3)
        d.rounded_rectangle([x0 + dx, y0 + dy, x0 + dx + 66, y0 + dy + 66], radius=12, fill=blend(NAVY, col, a))
    a2 = appear(t, 1.6)
    d.text((300, 1020), p["big_label"], font=F(40, "ExtraBold"), fill=blend(NAVY, YELLOW, a2), anchor="mm")
    d.text((800, 1080), p["small_label"], font=F(40, "ExtraBold"), fill=blend(NAVY, WHITE, a2), anchor="mm")
    d.text((800, 1130), p["small_sub"], font=F(30, "Medium"), fill=blend(NAVY, MUTED, a2), anchor="mm")

def v_clock(img, d, t, p):
    d.text((540, 430), p["kicker"], font=F(40, "Bold"), fill=YELLOW, anchor="mm")
    cx, cy, r = 300, 760, 190
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=WHITE, width=10)
    for k in range(12):
        ang = math.radians(k * 30)
        d.line([cx + (r - 30) * math.sin(ang), cy - (r - 30) * math.cos(ang), cx + (r - 12) * math.sin(ang), cy - (r - 12) * math.cos(ang)], fill=WHITE, width=6)
    # 9:30
    d.line([cx, cy, cx, cy + 140], fill=YELLOW, width=12)
    ha = math.radians(9.5 * 30)
    d.line([cx, cy, cx + 95 * math.sin(ha), cy - 95 * math.cos(ha)], fill=WHITE, width=14)
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=YELLOW)
    a = appear(t, 0.6)
    d.text((cx, cy + r + 70), p["clock_label"], font=F(44, "ExtraBold"), fill=blend(NAVY, YELLOW, a), anchor="mm")
    # bin with flowing orders
    bx0, by0, bx1, by1 = 600, 620, 960, 1000
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=30, outline=WHITE, width=8)
    d.text(((bx0 + bx1) / 2, by1 + 70), p["bin_label"], font=F(36, "Bold"), fill=WHITE, anchor="mm")
    nshow = int(max(0, t - 0.8) * 4)
    for k in range(min(nshow, 12)):
        lab = "BUY" if k % 2 == 0 else "SELL"
        col = YELLOW if lab == "BUY" else WHITE
        rr, cc = divmod(k, 2)
        x = bx0 + 30 + cc * 160
        y = by1 - 70 - rr * 56
        d.rounded_rectangle([x, y, x + 140, y + 46], radius=12, fill=col)
        d.text((x + 70, y + 23), lab, font=F(26, "ExtraBold"), fill=NAVY, anchor="mm")

def v_auction(img, d, t, p):
    d.text((540, 430), p["kicker"], font=F(40, "Bold"), fill=YELLOW, anchor="mm")
    x0, y0, x1, y1 = 170, 570, 930, 1160
    d.line([x0, y1, x1, y1], fill=MUTED, width=4)
    d.line([x0, y0, x0, y1], fill=MUTED, width=4)
    d.text((x1, y1 + 36), "shares", font=F(28, "Medium"), fill=MUTED, anchor="rm")
    d.text((x0 - 20, y0 - 10), "price", font=F(28, "Medium"), fill=MUTED, anchor="rm")
    prog = appear(t, 0.2, 1.6)
    # demand: high price -> few shares (down-right); supply: up-right
    def pt(u, kind):
        x = x0 + 40 + u * (x1 - x0 - 80)
        if kind == "buy":
            y = y0 + 40 + (u ** 0.8) * (y1 - y0 - 80)
        else:
            y = y1 - 40 - (u ** 0.8) * (y1 - y0 - 80)
        return x, y
    n = 60
    for kind, col in [("buy", YELLOW), ("sell", WHITE)]:
        pts = [pt(i / n, kind) for i in range(int(n * prog) + 1)]
        if len(pts) > 1:
            d.line(pts, fill=col, width=10, joint="curve")
    d.line([250, 505, 310, 505], fill=YELLOW, width=10)
    d.text((325, 505), "BUY orders", font=F(32, "Bold"), fill=YELLOW, anchor="lm")
    d.line([600, 505, 660, 505], fill=WHITE, width=10)
    d.text((675, 505), "SELL orders", font=F(32, "Bold"), fill=WHITE, anchor="lm")
    a = appear(t, 2.0)
    cx, cy = pt(0.5 ** 1.25, "buy")  # where the two curves cross
    if a > 0:
        rr = 26 * a
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=YELLOW, outline=NAVY, width=6)
        d.line([x0, cy, cx, cy], fill=blend(NAVY, YELLOW, a), width=4)
        d.text((x0 - 14, cy), p.get("axis", "$28"), font=F(34, "ExtraBold"), fill=blend(NAVY, YELLOW, a), anchor="rm")
        d.rounded_rectangle([290, 1200, 790, 1270], radius=24, fill=blend(NAVY, YELLOW, a))
        d.text((540, 1235), p["label"], font=F(40, "ExtraBold"), fill=NAVY, anchor="mm")
    note(d, "Illustrative curves", 1300)

def v_pop(img, d, t, p):
    a1, a2, a3 = appear(t, 0.1), appear(t, 0.7), appear(t, 1.3)
    tag(d, 270, 820, p["l1"], p["v1"], a1, False, 360)
    tag(d, 810, 820, p["l2"], p["v2"], a2, True, 360)
    d.line([460, 820, 460 + 135 * a2, 820], fill=YELLOW, width=12)
    if a2 > 0.9:
        d.polygon([(590, 792), (590, 848), (622, 820)], fill=YELLOW)
    d.text((540, 1060), p["big"], font=F(130, "ExtraBold"), fill=blend(NAVY, YELLOW, a3), anchor="mm")
    d.text((540, 520), p["kicker"], font=F(60, "ExtraBold"), fill=WHITE, anchor="mm")
    note(d, "Illustrative numbers", 1235)

def v_bars(img, d, t, p):
    d.text((540, 440), p["kicker"], font=F(44, "ExtraBold"), fill=WHITE, anchor="mm")
    d.text((540, 500), p["sub"], font=F(32, "Medium"), fill=MUTED, anchor="mm")
    base = 1100
    scale = 22
    for i, (lab, val) in enumerate(p["bars"]):
        a = appear(t, 0.3 + i * 0.6, 0.9)
        x = 330 + i * 420
        h = val * scale * a
        d.rounded_rectangle([x - 110, base - h, x + 110, base], radius=18, fill=YELLOW if i == 0 else WHITE)
        d.text((x, base - h - 50), f"+{val * a:.0f}%", font=F(64, "ExtraBold"), fill=YELLOW if i == 0 else WHITE, anchor="mm")
        d.text((x, base + 50), lab, font=F(38, "Bold"), fill=WHITE, anchor="mm")
    d.text((540, 1215), p["source"], font=F(26, "Medium"), fill=MUTED, anchor="mm")

def v_payoff(img, d, t, p):
    a1, a2 = appear(t, 0.1), appear(t, 0.9)
    for i, (k, v, a) in enumerate([(p["k1"], p["v1"], a1), (p["k2"], p["v2"], a2)]):
        y = 650 + i * 300
        d.text((540, y - 60), k, font=F(56, "Bold"), fill=blend(NAVY, WHITE, a), anchor="mm")
        d.text((540, y + 30), v, font=F(104, "ExtraBold"), fill=blend(NAVY, YELLOW, a), anchor="mm")

def v_cta(img, d, t, p, logo_path=None):
    a = appear(t, 0.1)
    lg = logo_img(260, logo_path)
    img.paste(lg, (540 - lg.width // 2, 560), lg)
    d.text((540, 920), p["line1"], font=F(64, "ExtraBold"), fill=blend(NAVY, WHITE, a), anchor="mm")
    d.text((540, 1010), p["line2"], font=F(64, "ExtraBold"), fill=blend(NAVY, YELLOW, a), anchor="mm")
    d.text((540, 1110), p.get("handle", "@bonusbraincell"), font=F(40, "Bold"), fill=blend(NAVY, MUTED, a), anchor="mm")

def v_card(img, d, t, p):
    """One big contract/rule card: header, giant value, sub line."""
    d.text((540, 430), p["kicker"], font=F(40, "Bold"), fill=YELLOW, anchor="mm")
    a1, a2 = appear(t, 0.15), appear(t, 0.8)
    x0, y0, x1, y1 = 170, 540, 910, 1110
    d.rounded_rectangle([x0, y0, x1, y1], radius=40, fill=blend(NAVY, NAVY2, a1), outline=blend(NAVY, WHITE, a1), width=6)
    d.text((540, y0 + 80), p["header"], font=F(40, "Bold"), fill=blend(NAVY, MUTED, a1), anchor="mm")
    d.text((540, 820), p["value"], font=F(170, "ExtraBold"), fill=blend(NAVY, YELLOW, a2), anchor="mm")
    d.text((540, 970), p["sub"], font=F(46, "Bold"), fill=blend(NAVY, WHITE, a2), anchor="mm")
    if p.get("note"):
        note(d, p["note"], 1200)

def v_mappin(img, d, t, p):
    """Pipelines converging on one hub pin, with storage tanks."""
    d.text((540, 430), p["kicker"], font=F(40, "Bold"), fill=YELLOW, anchor="mm")
    cx, cy = 540, 820
    prog = appear(t, 0.1, 1.4)
    starts = [(120, 560), (120, 1000), (960, 560), (960, 1040), (540, 520), (300, 1160), (800, 1170)]
    for sx, sy in starts:
        ex, ey = sx + (cx - sx) * prog, sy + (cy - sy) * prog
        d.line([sx, sy, ex, ey], fill=MUTED, width=12)
    a = appear(t, 1.2)
    for k, (tx, ty) in enumerate([(330, 700), (750, 700), (330, 960), (750, 960)]):
        ak = appear(t, 1.2 + 0.15 * k)
        d.ellipse([tx - 62, ty - 62, tx + 62, ty + 62], fill=blend(NAVY, WHITE, ak), outline=NAVY, width=6)
        d.line([tx - 40, ty, tx + 40, ty], fill=blend(NAVY, NAVY2, ak), width=6)
    pr = 70
    d.ellipse([cx - pr, cy - pr - 50, cx + pr, cy + pr - 50], fill=blend(NAVY, YELLOW, a))
    d.polygon([(cx - 52, cy - 10), (cx + 52, cy - 10), (cx, cy + 80)], fill=blend(NAVY, YELLOW, a))
    d.ellipse([cx - 26, cy - 76, cx + 26, cy - 24], fill=NAVY)
    d.text((540, 1215), p["label"], font=F(52, "ExtraBold"), fill=blend(NAVY, WHITE, a), anchor="mm")
    if p.get("sub"):
        d.text((540, 1280), p["sub"], font=F(30, "Medium"), fill=blend(NAVY, MUTED, a), anchor="mm")

def v_tiles(img, d, t, p):
    """100 tiles; 99 fade, 1 stays: 'about 1%'."""
    d.text((540, 430), p["kicker"], font=F(40, "Bold"), fill=YELLOW, anchor="mm")
    fade = appear(t, 1.3, 1.0)
    keep = 67
    for i in range(100):
        r, c = divmod(i, 10)
        x0, y0 = 215 + c * 66, 500 + r * 66
        a = appear(t, 0.05 + i * 0.008, 0.3)
        col = YELLOW if i == keep else blend(WHITE, NAVY2, fade)
        d.rounded_rectangle([x0, y0, x0 + 54, y0 + 54], radius=10, fill=blend(NAVY, col, a))
    a2 = appear(t, 1.9)
    d.text((540, 1215), p["big"], font=F(72, "ExtraBold"), fill=blend(NAVY, YELLOW, a2), anchor="mm")
    if p.get("source"):
        note(d, p["source"], 1285)

def v_converge(img, d, t, p):
    """Two price lines that meet at expiration."""
    d.text((540, 430), p["kicker"], font=F(40, "Bold"), fill=YELLOW, anchor="mm")
    x0, x1, ymid = 150, 900, 830
    prog = appear(t, 0.2, 1.8)
    n = 60
    for kind, col, amp in [("fut", YELLOW, -200), ("phys", WHITE, 170)]:
        pts = []
        for i in range(int(n * prog) + 1):
            u = i / n
            wob = 22 * math.sin(u * 11 + (0 if kind == "fut" else 2))
            pts.append((x0 + u * (x1 - x0), ymid + (amp + wob) * (1 - u) ** 1.4))
        if len(pts) > 1:
            d.line(pts, fill=col, width=10, joint="curve")
    d.line([x1, 540, x1, 1120], fill=MUTED, width=3)
    d.text((x1, 1160), p["end_label"], font=F(30, "Bold"), fill=MUTED, anchor="mm")
    d.line([170, 1240, 230, 1240], fill=YELLOW, width=10)
    d.text((245, 1240), p["l1"], font=F(34, "Bold"), fill=YELLOW, anchor="lm")
    d.line([600, 1240, 660, 1240], fill=WHITE, width=10)
    d.text((675, 1240), p["l2"], font=F(34, "Bold"), fill=WHITE, anchor="lm")
    a = appear(t, 2.0)
    if a > 0:
        rr = 24 * a
        d.ellipse([x1 - rr, ymid - rr, x1 + rr, ymid + rr], fill=YELLOW, outline=NAVY, width=6)
    if p.get("note"):
        note(d, p["note"], 1295)

def v_negative(img, d, t, p):
    """A price line that falls through zero."""
    d.text((540, 430), p["kicker"], font=F(40, "Bold"), fill=YELLOW, anchor="mm")
    x0, x1, y_top, y_zero, y_bot = 170, 920, 560, 860, 1120
    d.line([x0, y_zero, x1, y_zero], fill=MUTED, width=4)
    d.text((x0 - 16, y_zero), "$0", font=F(34, "Bold"), fill=MUTED, anchor="rm")
    prog = appear(t, 0.2, 2.0)
    vals = [18, 17, 19, 16, 15, 16, 13, 12, 14, 11, 10, 8, 6, 2, -12, -37.6]
    def y(v):
        return y_zero - v * (y_zero - y_top) / 20 if v >= 0 else y_zero - v * (y_bot - y_zero) / 40
    pts = [(x0 + i * (x1 - x0) / (len(vals) - 1), y(v)) for i, v in enumerate(vals)]
    m = prog * (len(pts) - 1)
    k = int(m)
    draw = pts[:k + 1]
    if k < len(pts) - 1:
        f = m - k
        draw.append((pts[k][0] + (pts[k + 1][0] - pts[k][0]) * f, pts[k][1] + (pts[k + 1][1] - pts[k][1]) * f))
    if len(draw) > 1:
        d.line(draw, fill=YELLOW, width=10, joint="curve")
    a = appear(t, 2.2)
    if a > 0:
        ex, ey = pts[-1]
        d.ellipse([ex - 22, ey - 22, ex + 22, ey + 22], fill=YELLOW)
        d.text((ex - 40, ey + 2), p["value"], font=F(64, "ExtraBold"), fill=blend(NAVY, YELLOW, a), anchor="rm")
        d.text((540, 1210), p["label"], font=F(42, "ExtraBold"), fill=blend(NAVY, WHITE, a), anchor="mm")
    if p.get("source"):
        note(d, p["source"], 1275)

def v_relay(img, d, t, p):
    """Message relay down a chain of boxes (e.g. store -> network -> bank). A packet travels
    down (and optionally back up). params: kicker, nodes [labels], packet, back (label or null), note."""
    d.text((540, 430), p["kicker"], font=F(40, "Bold"), fill=YELLOW, anchor="mm")
    nodes = p["nodes"]; n = len(nodes)
    top, gap, bh = 510, 22, 120
    step = bh + gap
    ys = [top + k * step for k in range(n)]
    hl = p.get("highlight", [])
    for k, (lab, y) in enumerate(zip(nodes, ys)):
        a = appear(t, 0.05 + k * 0.25)
        on = k in hl
        fill = blend(NAVY, YELLOW if on else NAVY2, a)
        d.rounded_rectangle([300, y, 900, y + bh], radius=26, fill=fill, outline=blend(NAVY, WHITE, a * (0 if on else 0.6)), width=3)
        d.text((600, y + bh / 2), lab, font=F(44, "Bold"), fill=blend(fill, NAVY if on else WHITE, a), anchor="mm")
        if k < n - 1:
            d.line([190, y + bh / 2 + 18, 190, ys[k + 1] + bh / 2 - 18], fill=blend(NAVY, MUTED, a), width=5)
    # packet position: down during first leg, back up during second leg
    travel = 0.9 * (n - 1) * 0.55
    t1 = max(0.0, t - 0.6)
    yc0, yc1 = ys[0] + bh / 2, ys[-1] + bh / 2
    if t1 <= travel:
        y = yc0 + (yc1 - yc0) * ease(min(1, t1 / travel)); lab = p["packet"]; col = YELLOW
    elif p.get("back") and t1 > travel + 0.5:
        u = min(1, (t1 - travel - 0.5) / travel)
        y = yc1 + (yc0 - yc1) * ease(u); lab = p["back"]; col = WHITE
    else:
        y = yc1; lab = p["packet"]; col = YELLOW
    w = min(200, max(110, int(d.textlength(lab, font=F(30, "ExtraBold"))) + 36))
    d.rounded_rectangle([190 - w / 2, y - 32, 190 + w / 2, y + 32], radius=32, fill=col)
    d.text((190, y), lab, font=F(30, "ExtraBold"), fill=NAVY, anchor="mm")
    if p.get("note"):
        note(d, p["note"], 1250)

def v_sunpath(img, d, t, p):
    """Sun crosses a row of towns; each town's own noon lights up as the sun passes overhead.
    params: kicker, towns [labels], label (under the row), note."""
    d.text((540, 430), p["kicker"], font=F(40, "Bold"), fill=YELLOW, anchor="mm")
    towns = p["towns"]; n = len(towns)
    xs = [200 + k * (680 / max(1, n - 1)) for k in range(n)]
    base = 1010
    d.arc([120, 560, 960, 1400], 180, 360, fill=MUTED, width=4)
    u = (t * 0.32) % 1.0
    sx = 150 + 780 * u
    sy = 980 - 400 * math.sin(math.pi * u)
    d.ellipse([sx - 58, sy - 58, sx + 58, sy + 58], fill=YELLOW)
    d.line([110, base, 970, base], fill=WHITE, width=5)
    for x, lab in zip(xs, towns):
        on = abs(sx - x) < 90
        col = YELLOW if on else WHITE
        d.rectangle([x - 46, base - 80, x + 46, base], fill=col)
        d.polygon([(x - 60, base - 80), (x, base - 134), (x + 60, base - 80)], fill=col)
        d.text((x, base + 44), lab, font=F(34, "Bold"), fill=WHITE, anchor="mm")
        d.text((x, base + 96), "NOON" if on else " ", font=F(38, "ExtraBold"), fill=YELLOW, anchor="mm")
    if p.get("label"):
        d.text((540, 1200), p["label"], font=F(46, "Bold"), fill=WHITE, anchor="mm")
    if p.get("note"):
        note(d, p["note"], 1262)

def v_zones(img, d, t, p):
    """Vertical bands snapping into place, west to east. params: kicker, bands [labels], big, note."""
    d.text((540, 430), p["kicker"], font=F(40, "Bold"), fill=YELLOW, anchor="mm")
    bands = p["bands"]; n = len(bands)
    x0, x1, y0, y1 = 110, 970, 540, 1050
    bw = (x1 - x0) / n
    for k, lab in enumerate(bands):
        a = appear(t, 0.2 + k * 0.4, 0.35)
        drop = (1 - a) * 90
        col = YELLOW if k % 2 else NAVY2
        tc = NAVY if k % 2 else WHITE
        fill = blend(NAVY, col, a)
        d.rectangle([x0 + k * bw + 5, y0 - drop, x0 + (k + 1) * bw - 5, y1 - drop], fill=fill, outline=blend(NAVY, WHITE, a * 0.5), width=2)
        fs = 30
        while d.textlength(lab, font=F(fs, "ExtraBold")) > bw - 18 and fs > 20:
            fs -= 1
        d.text((x0 + (k + .5) * bw, (y0 + y1) / 2 - drop), lab, font=F(fs, "ExtraBold"), fill=blend(fill, tc, a), anchor="mm")
    a = appear(t, 0.3 + n * 0.4)
    d.text((540, 1140), p["big"], font=F(64, "ExtraBold"), fill=blend(NAVY, YELLOW, a), anchor="mm")
    if p.get("note"):
        note(d, p["note"], 1235)

def v_noonclock(img, d, t, p):
    """Clock reaches 12, is set back, and reaches 12 again. params: kicker, first, back, second, note."""
    d.text((540, 430), p["kicker"], font=F(40, "Bold"), fill=YELLOW, anchor="mm")
    cx, cy, r = 540, 810, 270
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=NAVY2, outline=WHITE, width=10)
    for k in range(12):
        ang = math.radians(k * 30)
        d.line([cx + (r - 38) * math.sin(ang), cy - (r - 38) * math.cos(ang), cx + (r - 14) * math.sin(ang), cy - (r - 14) * math.cos(ang)], fill=WHITE, width=7)
    d1, d2, d3 = float(p.get("t1", 2.2)), float(p.get("t2", 1.1)), float(p.get("t3", 2.2))
    back = 40.0  # drawn offset in degrees of the minute hand, schematic only
    if t < d1:
        m = -back * (1 - ease(t / d1)); lab = p["first"]
    elif t < d1 + d2:
        m = -back * ease((t - d1) / d2); lab = p["back"]
    elif t < d1 + d2 + d3:
        m = -back * (1 - ease((t - d1 - d2) / d3)); lab = p["back"]
    else:
        m = 0.0; lab = p["second"]
    ma = math.radians(m); ha = math.radians(m / 12)
    d.line([cx, cy, cx + 150 * math.sin(ha), cy - 150 * math.cos(ha)], fill=WHITE, width=16)
    d.line([cx, cy, cx + 225 * math.sin(ma), cy - 225 * math.cos(ma)], fill=YELLOW, width=10)
    d.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=YELLOW)
    d.text((540, 1160), lab, font=F(58, "ExtraBold"), fill=YELLOW, anchor="mm")
    if p.get("note"):
        note(d, p["note"], 1240)

VISUALS = dict(hook=v_hook, offer=v_offer, rows=v_rows, alloc=v_alloc, clock=v_clock,
               auction=v_auction, pop=v_pop, bars=v_bars, payoff=v_payoff, cta=v_cta,
               card=v_card, mappin=v_mappin, tiles=v_tiles, converge=v_converge, negative=v_negative, relay=v_relay,
               sunpath=v_sunpath, zones=v_zones, noonclock=v_noonclock)

# ---------- audio ----------
def tts_scene(text, voice, speed, path, kokoro):
    s, sr = kokoro.create(text, voice=voice, speed=speed, lang="en-us")
    s = np.clip(s, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((s * 32767).astype("int16").tobytes())
    return len(s) / sr, sr

STOP_END = {"a", "an", "the", "at", "of", "to", "in", "on", "for", "and", "or", "but", "by", "with",
            "from", "per", "as", "is", "are", "was", "that", "this", "its", "your", "their", "into", "who",
            "have", "has", "had", "be", "can", "will", "would", "were", "my", "our",
            "you", "what", "than", "when", "where", "if", "so", "it", "they", "we",
            "could", "should", "did", "does", "do", "about"}

def chunk_caption(text, maxc=42):
    """Caption chunks follow sentences and clauses (up to two lines on screen).
    Never splits abbreviations like U.S., never ends a chunk on a weak word, never leaves a tiny orphan."""
    import re
    abbrev = re.compile(r"^(?:[A-Z]\.)+$|^(?:Mr|Mrs|Dr|St|vs|etc|Jan|Feb|Aug|Sept|Oct|Nov|Dec)\.$")
    words = text.split()
    chunks, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        if i + 1 == len(words):
            break
        length = len(" ".join(cur))
        end_sent = w.endswith((".", "?", "!")) and not abbrev.match(w.strip("\"'()"))
        end_clause = w.endswith((",", ";", ":"))
        if end_clause and re.fullmatch(r"\d{1,2},", w) and re.match(r"\d{4}\b", words[i + 1]):
            end_clause = False  # keep dates like "November 18, 1883" together
        if end_sent and length >= 12:
            chunks.append(" ".join(cur)); cur = []
        elif end_clause and length >= 22:
            chunks.append(" ".join(cur)); cur = []
        elif len(" ".join(cur + [words[i + 1]])) > maxc:
            rest = []
            for w2 in words[i + 1:]:
                rest.append(w2)
                if w2.endswith((".", "?", "!", ",", ";", ":")) and not abbrev.match(w2.strip("\"'()")):
                    break
            if len(" ".join(rest)) < 12 and len(" ".join(cur + rest)) <= maxc + 10:
                continue  # finish the short clause on this chunk instead of orphaning it
            moved = []
            while len(cur) > 1 and (cur[-1].lower().strip(",.") in STOP_END or cur[-1].lower().endswith("'s")
                                    or (cur[-1][0].isupper() and cur[-1].isalpha() and (moved or words[i + 1])[0][0].isupper())):
                moved.insert(0, cur.pop())  # also keeps names like "Western Union" on one line
            chunks.append(" ".join(cur)); cur = moved
    if cur:
        chunks.append(" ".join(cur))
    merged = []
    for c in chunks:
        if (merged and (len(c) < 12 or len(merged[-1]) < 12) and len(merged[-1]) + 1 + len(c) <= maxc + 14
                and not merged[-1].endswith((".", "?", "!"))):
            merged[-1] = merged[-1] + " " + c
        else:
            merged.append(c)
    return merged

def srt_time(x):
    ms = int(round(x * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def main():
    spec_path, out = sys.argv[1], sys.argv[2]
    logo_path = None
    if "--logo" in sys.argv:
        logo_path = sys.argv[sys.argv.index("--logo") + 1]
    cover_path = sys.argv[sys.argv.index("--cover") + 1] if "--cover" in sys.argv else None
    cover_hold = 0.5 if cover_path else 0.0
    spec = json.load(open(spec_path))
    os.makedirs(out, exist_ok=True)
    work = os.path.join(out, "_work"); os.makedirs(work, exist_ok=True)
    os.makedirs(os.path.join(out, "images"), exist_ok=True)
    from kokoro_onnx import Kokoro
    tts_dir = spec.get("tts_dir", "/home/claude/tts")
    kokoro = Kokoro(os.path.join(tts_dir, "kokoro.onnx"), os.path.join(tts_dir, "voices.bin"))
    voice, speed = spec.get("voice", "af_heart"), spec.get("speed", 1.08)
    lead, tail = 0.15, 0.35

    # 1) narration per scene -> durations
    timeline, t0 = [], cover_hold
    for i, sc in enumerate(spec["scenes"]):
        wav = os.path.join(work, f"a{i:02}.wav")
        # Per-scene overrides (Script System v2): "voice" for a second character
        # (quoted myth, viewer question), "speed" for pacing (0.98-1.14 range).
        sv = sc.get("voice", voice)
        ss = max(0.9, min(1.2, float(sc.get("speed", speed))))
        dur, sr = tts_scene(sc["tts"], sv, ss, wav, kokoro)
        sdur = round((lead + dur + tail) * FPS) / FPS
        timeline.append(dict(i=i, start=t0, dur=sdur, speech=dur, wav=wav))
        t0 += sdur
    total = t0

    # 2) captions timed across each scene's speech, proportional to characters
    cues = []
    for sc, tl in zip(spec["scenes"], timeline):
        parts = chunk_caption(sc["caption"])
        n = sum(len(p) for p in parts)
        cur = tl["start"] + lead
        for p in parts:
            d_ = tl["speech"] * len(p) / n
            cues.append(dict(start=cur, end=cur + d_, text=p, scene=tl["i"]))
            cur += d_
    with open(os.path.join(out, "captions.srt"), "w") as f:
        for k, c in enumerate(cues, 1):
            f.write(f"{k}\n{srt_time(c['start'])} --> {srt_time(c['end'])}\n{c['text']}\n\n")

    # 3) frames -> one encoded file per scene (cover first: frame 0 = thumbnail)
    seglist = []
    if cover_path:
        cimg = Image.open(cover_path).convert("RGB").resize((W, H))
        cseg = os.path.join(work, "s_cover.mp4")
        proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                                 "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                                 "-pix_fmt", "yuv420p", "-r", str(FPS), cseg], stdin=subprocess.PIPE)
        for _ in range(int(round(cover_hold * FPS))):
            proc.stdin.write(cimg.tobytes())
        proc.stdin.close(); proc.wait()
        seglist.append(cseg)
    for sc, tl in zip(spec["scenes"], timeline):
        nfr = int(round(tl["dur"] * FPS))
        tmp = os.path.join(work, f"s{tl['i']:02}.tmp.mp4")
        fin = os.path.join(work, f"s{tl['i']:02}.mp4")
        proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                                 "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                                 "-pix_fmt", "yuv420p", "-r", str(FPS), tmp], stdin=subprocess.PIPE)
        fn = VISUALS[sc["visual"]]
        keyframe = None
        for fr in range(nfr):
            t = fr / FPS
            gt = tl["start"] + t
            img = background(); d = ImageDraw.Draw(img)
            chrome(img, d, spec["series"], gt / total, logo_path)
            if sc["visual"] == "cta":
                fn(img, d, t, sc["params"], logo_path)
            else:
                fn(img, d, t, sc["params"])
            ctext = next((c["text"] for c in cues if c["start"] <= gt < c["end"]), None)
            caption(img, ctext)
            # gentle fade at scene start
            if t < 0.2 and tl["i"] > 0:
                img = Image.blend(Image.new("RGB", (W, H), NAVY), img, 0.4 + 3 * t)
            proc.stdin.write(img.tobytes())
            if fr == int(nfr * 0.85):
                keyframe = img
        proc.stdin.close(); proc.wait()
        if proc.returncode != 0:
            sys.exit(f"scene {tl['i']} failed")
        os.replace(tmp, fin)
        keyframe.save(os.path.join(out, "images", f"scene{tl['i'] + 1:02}_{sc['visual']}.png"))
        seglist.append(fin)

    # 4) join, then audio
    with open(os.path.join(work, "list.txt"), "w") as f:
        for s in seglist:
            f.write(f"file '{os.path.abspath(s)}'\n")
    silent = os.path.join(work, "video_silent.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", os.path.join(work, "list.txt"), "-c", "copy", silent], check=True)
    # build narration track with exact offsets
    sr = 24000
    track = np.zeros(int(total * sr) + sr, dtype=np.float32)
    for tl in timeline:
        with wave.open(tl["wav"]) as w:
            a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32767
        st = int((tl["start"] + lead) * sr)
        track[st:st + len(a)] += a
    peak = np.max(np.abs(track)) or 1
    track = track / peak * 0.89
    nar = os.path.join(work, "narration.wav")
    with wave.open(nar, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((track[: int(total * sr)] * 32767).astype("int16").tobytes())
    tmpv = os.path.join(out, "video.tmp.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", nar, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-shortest",
                    "-movflags", "+faststart", tmpv], check=True)
    os.replace(tmpv, os.path.join(out, "video.mp4"))
    json.dump(dict(total=total, scenes=timeline, cues=cues), open(os.path.join(work, "timeline.json"), "w"), indent=1)
    print(f"rendered {total:.2f}s, {len(cues)} captions")
    if total <= 61:
        print(f"WARNING: video is {total:.2f}s; it must be longer than 61 s (target 65-90). Lengthen the script and re-render.")
    if total > 90:
        print(f"WARNING: video is {total:.2f}s; keep it at or under 90 s.")

if __name__ == "__main__":
    main()
