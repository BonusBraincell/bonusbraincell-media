#!/usr/bin/env python3
"""Bonus Braincell episode renderer.

Usage: python3 render_episode.py episode.json OUTPUT_DIR [--cover OUT/cover.png] [--logo path/to/logo.png]

Design system v3 (2026-11-20): every color, size, position and timing comes from design-system.json via
design.py; rules in DESIGN.md. Also writes scene-plan.md/.json, qa-report.json and qa-sheet.png.

Reads an episode spec (scenes with narration, captions and a visual type),
generates narration with Kokoro TTS (Apache-2.0), draws 1080x1920 frames with
Pillow, encodes one file per scene, joins them, muxes audio, and writes
video.mp4, captions.srt, cover.png and images/ (one keyframe per scene).
"""
import json, math, os, re, subprocess, sys, wave, shutil, zlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design as DZ
import world as WD   # v4 scene kit (environments, illustrated custom scenes, env-aware chrome)
import sfx as SFX    # v4 procedural sound effects
import importlib.util

W, H, FPS = DZ.W, DZ.H, DZ.DS["canvas"]["fps"]
NAVY = DZ.C["bg"]
NAVY2 = DZ.C["panel"]
YELLOW = DZ.C["track"]
WHITE = DZ.C["ink"]
MUTED = DZ.C["muted"]
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

# ---------- shared chrome (design system v3) ----------
def background():
    return DZ.background()

def logo_img(size, logo_path):
    return DZ.mark(size, logo_path)

def chrome(img, d, series, progress, logo_path):
    DZ.chrome(img, d, series, progress, logo_path)

def caption(img, text):
    DZ.caption(img, text, STOP_END)

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
    d.text((540, 970), p["sub"], font=F(int(p.get("sub_size", 46)), "Bold"), fill=blend(NAVY, WHITE, a2), anchor="mm")
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

# ---------- orbit (added 2026-11-20) ----------
_orb_cache = {}
def _cannon_path(frac, r0, R):
    """Projectile fired horizontally from radius r0 around a point mass, speed = frac * circular speed.
    Returns list of (x, y) offsets from Earth's centre until it hits radius R or completes one lap."""
    key = (round(frac, 3), r0, R)
    if key in _orb_cache:
        return _orb_cache[key]
    GM = 1.0
    x, y = 0.0, -r0
    vx, vy = frac * math.sqrt(GM / r0), 0.0
    pts, ang, dt = [(x, y)], 0.0, 0.002 * r0 ** 1.5
    for _ in range(20000):
        r = math.hypot(x, y)
        ax, ay = -GM * x / r ** 3, -GM * y / r ** 3
        vx += ax * dt; vy += ay * dt
        x2, y2 = x + vx * dt, y + vy * dt
        ang += abs(math.atan2(x * y2 - y * x2, x * x2 + y * y2))
        x, y = x2, y2
        pts.append((x, y))
        if math.hypot(x, y) <= R or ang >= 2 * math.pi:
            break
    _orb_cache[key] = pts
    return pts

def _earth(d, cx, cy, R):
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=NAVY2, outline=WHITE, width=6)
    for k in (-0.5, 0.0, 0.5):
        h = R * math.sqrt(1 - k * k)
        d.arc([cx - h, cy + k * R - R * 0.18, cx + h, cy + k * R + R * 0.18], 0, 180, fill=MUTED, width=3)

def _station(d, x, y, s=1.0, col=YELLOW):
    d.rectangle([x - 16 * s, y - 12 * s, x + 16 * s, y + 12 * s], fill=col)
    for sx in (-1, 1):
        d.rectangle([x + sx * 22 * s - 14 * s, y - 26 * s, x + sx * 22 * s + 14 * s, y + 26 * s], fill=WHITE)
        d.line([x + sx * 16 * s, y, x + sx * 8 * s + sx * 0, y], fill=col, width=int(4 * s))

def _arrow(d, x0, y0, x1, y1, col, w=8):
    d.line([x0, y0, x1, y1], fill=col, width=w)
    a = math.atan2(y1 - y0, x1 - x0)
    L = 26
    d.polygon([(x1, y1), (x1 - L * math.cos(a - 0.45), y1 - L * math.sin(a - 0.45)),
               (x1 - L * math.cos(a + 0.45), y1 - L * math.sin(a + 0.45))], fill=col)

def v_orbit(img, d, t, p):
    """Orbit diagrams. mode 'station': station circling Earth with a sideways arrow and a gravity arrow
    (fully drawn from frame 0). mode 'cannon': Newton's cannon on a mountain; 'shots' = list of speed fractions
    (1.0 = orbit); the first 'drawn' shots are shown complete, the rest are animated. mode 'together': station
    and astronaut dropping in sync. mode 'drag': orbit slowly sinks, then a reboost lifts it.
    params: kicker, mode, label, note."""
    if p.get("kicker"):
        d.text((540, 430), p["kicker"], font=F(44, "ExtraBold") if p.get("big_kicker") else F(40, "Bold"), fill=YELLOW, anchor="mm")
    mode = p.get("mode", "station")
    cx, cy = 540, 860
    if mode == "station":
        R, ro = 220, 330
        _earth(d, cx, cy, R)
        n = 60
        for k in range(n):
            if k % 2 == 0:
                a0, a1 = 360 * k / n, 360 * (k + 1) / n
                d.arc([cx - ro, cy - ro, cx + ro, cy + ro], a0, a1, fill=MUTED, width=4)
        ang = -math.pi / 2 + 0.55 * t
        sx, sy = cx + ro * math.cos(ang), cy + ro * math.sin(ang)
        tx, ty = -math.sin(ang), math.cos(ang)
        _arrow(d, sx, sy, sx + 150 * tx, sy + 150 * ty, WHITE)
        _arrow(d, sx, sy, sx + (cx - sx) * 0.48, sy + (cy - sy) * 0.48, YELLOW)
        _station(d, sx, sy, 1.3)
        if p.get("tlabel"):
            d.text((sx + 150 * tx + 20 * tx, sy + 150 * ty - 40), p["tlabel"], font=F(34, "Bold"), fill=WHITE, anchor="mm")
    elif mode == "cannon":
        R = 210
        cy = 860
        _earth(d, cx, cy, R)
        top = cy - R - 80
        d.polygon([(cx - 105, cy - R + 22), (cx, top), (cx + 105, cy - R + 22)], fill=WHITE)
        d.rectangle([cx - 8, top - 22, cx + 46, top - 2], fill=YELLOW)
        r0 = R + 80 + 12
        shots = p.get("shots", [])
        drawn = p.get("drawn", 0)
        cols = [MUTED, WHITE, YELLOW]
        for i, fr in enumerate(shots):
            pts = _cannon_path(fr, r0, R)
            if i < drawn:
                u = 1.0
            else:
                u = ease((t - 0.3 - 1.4 * (i - drawn)) / (2.2 if fr >= 0.99 else 1.1))
            m = max(2, int(len(pts) * u))
            seg = [(cx + x, cy + y) for x, y in pts[:m]]
            if u > 0:
                d.line(seg, fill=cols[min(i, 2)] if fr < 0.99 else YELLOW, width=7, joint="curve")
                bx, by = seg[-1]
                d.ellipse([bx - 14, by - 14, bx + 14, by + 14], fill=YELLOW if fr >= 0.99 else WHITE)
    elif mode == "together":
        drop = (t * 120) % 240
        x0, y0 = 540, 560 + drop
        d.rounded_rectangle([x0 - 230, y0, x0 + 230, y0 + 300], radius=40, outline=YELLOW, width=8, fill=NAVY2)
        ax, ay = x0, y0 + 150
        d.ellipse([ax - 28, ay - 92, ax + 28, ay - 36], fill=WHITE)
        d.line([ax, ay - 36, ax, ay + 40], fill=WHITE, width=12)
        d.line([ax - 60, ay - 20, ax + 60, ay - 10], fill=WHITE, width=10)
        d.line([ax, ay + 40, ax - 40, ay + 95], fill=WHITE, width=10)
        d.line([ax, ay + 40, ax + 45, ay + 90], fill=WHITE, width=10)
        for k, xx in enumerate((300, 780)):
            _arrow(d, xx, 600 + drop, xx, 760 + drop, YELLOW, 8)
    elif mode == "drag":
        R, cy = 200, 800
        _earth(d, cx, cy, R)
        cyc = 5.0
        u = (t % cyc) / cyc
        if u < 0.7:
            ro = 340 - 45 * (u / 0.7); boost = False
        else:
            ro = 295 + 45 * ease((u - 0.7) / 0.15); boost = True
        d.arc([cx - 340, cy - 340, cx + 340, cy + 340], 0, 360, fill=NAVY2, width=3)
        d.arc([cx - ro, cy - ro, cx + ro, cy + ro], 0, 360, fill=MUTED, width=4)
        ang = -math.pi / 2 + 0.5 * t
        sx, sy = cx + ro * math.cos(ang), cy + ro * math.sin(ang)
        if boost:
            tx, ty = -math.sin(ang), math.cos(ang)
            _arrow(d, sx - 40 * tx, sy - 40 * ty, sx - 140 * tx, sy - 140 * ty, YELLOW, 10)
        _station(d, sx, sy, 1.2)
        lab = p.get("boost_label", "REBOOST") if boost else p.get("drag_label", "DRAG")
        d.text((540, 1215), lab, font=F(52, "ExtraBold"), fill=YELLOW if boost else WHITE, anchor="mm")
    if p.get("label"):
        d.text((540, 1215), p["label"], font=F(46, "Bold"), fill=WHITE, anchor="mm")
    if p.get("note"):
        note(d, p["note"], 1262)

def v_build(img, d, t, p):
    """Action-first 'build-up' hook (EXP-06): an object is already moving at frame 0,
    an action arrow draws, and the result pops in by ~1.2 s. Params: kicker, obj, action, result, note."""
    if p.get("kicker"):
        d.text((540, 380), p["kicker"], font=F(58, "ExtraBold"), fill=WHITE, anchor="mm")
    # object slides in (already on screen at t=0), then bobs gently so the frame never freezes
    u = ease(t / 0.7)
    ox = 150 + 150 * u
    oy = 820 + 10 * math.sin(t * 3.0)
    d.rounded_rectangle([ox - 140, oy - 110, ox + 140, oy + 110], radius=36, fill=NAVY2, outline=WHITE, width=6)
    for k, line in enumerate(wrap(d, p["obj"], F(46, "ExtraBold"), 250)[:3]):
        d.text((ox, oy - 30 * (len(wrap(d, p["obj"], F(46, "ExtraBold"), 250)[:3]) - 1) + 60 * k), line,
               font=F(46, "ExtraBold"), fill=WHITE, anchor="mm")
    for k in range(3):  # motion lines behind the object while it moves
        if u < 0.98:
            yy = oy - 60 + 60 * k
            d.line([ox - 240 + 30 * k, yy, ox - 165, yy], fill=MUTED, width=6)
    # action arrow draws toward the result
    a = ease((t - 0.3) / 0.6)
    if a > 0:
        x0, x1 = 460, 460 + 160 * a
        pulse = 2 * math.sin(t * 6) if a >= 1 else 0
        d.line([x0, 820, x1, 820], fill=YELLOW, width=int(12 + pulse))
        if a > 0.6:
            d.polygon([(x1 + 30, 820), (x1 - 8, 795), (x1 - 8, 845)], fill=YELLOW)
        if p.get("action"):
            d.text((540, 665), p["action"], font=F(36, "Bold"), fill=YELLOW, anchor="mm")
    # result pops in
    r = ease((t - 0.8) / 0.4)
    if r > 0:
        sc = 0.7 + 0.3 * r
        cx, cy, hw, hh = 830, 820, 150 * sc, 115 * sc
        d.rounded_rectangle([cx - hw, cy - hh, cx + hw, cy + hh], radius=36, fill=blend(NAVY, YELLOW, r))
        for k, line in enumerate(wrap(d, p["result"], F(44, "ExtraBold"), 260)[:3]):
            n = len(wrap(d, p["result"], F(44, "ExtraBold"), 260)[:3])
            d.text((cx, cy - 28 * (n - 1) + 56 * k), line, font=F(int(44 * sc), "ExtraBold"), fill=NAVY, anchor="mm")
    if p.get("note"):
        note(d, p["note"], 1120)

VISUALS = dict(hook=v_hook, offer=v_offer, rows=v_rows, alloc=v_alloc, clock=v_clock,
               auction=v_auction, pop=v_pop, bars=v_bars, payoff=v_payoff, cta=v_cta,
               card=v_card, mappin=v_mappin, tiles=v_tiles, converge=v_converge, negative=v_negative, relay=v_relay,
               sunpath=v_sunpath, zones=v_zones, noonclock=v_noonclock, orbit=v_orbit, build=v_build)
VISUALS.update(DZ.V3)  # v3 scene types: hook_object, compare, whole, process, cross, diagram, answer
LEGACY = set(VISUALS) - set(DZ.V3)

def resolve_times(obj, tts, lead, speech, warn):
    """Convert narration phrases in timing fields to seconds from scene start (proportional to characters)."""
    keys = ("at", "show", "hide", "track", "result_at")
    def conv(v):
        if isinstance(v, str):
            i = tts.lower().find(v.lower())
            if i < 0:
                warn.append(f"timing phrase not found in narration: '{v}'"); return 0.0
            return round(lead + speech * i / max(1, len(tts)), 2)
        return v
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k in keys or k.endswith("_at"):
                out[k] = [conv(x) for x in v] if isinstance(v, list) else conv(v)
            else:
                out[k] = resolve_times(v, tts, lead, speech, warn)
        return out
    if isinstance(obj, list):
        return [resolve_times(x, tts, lead, speech, warn) for x in obj]
    return obj

# ---------- audio ----------
# Audio direction v1 (2026-11-22). Three subtle, always-on polish steps plus one opt-in:
#  1) Varied pauses: each sentence is synthesized on its own (Kokoro's fixed 0.25 s sentence_pause is off)
#     and the gap after it depends on how it ends: "." 0.20-0.38 s, "?" 0.36-0.46 s, "..." 0.45-0.60 s,
#     "!" 0.24-0.32 s, +0.06 s after a short punch line (<= 6 words). Clause pauses vary 0.07-0.13 s.
#     Seeded by post_id + scene, so a re-render sounds identical.
#  2) Scene tails vary 0.28-0.46 s (0.55 s before a payoff/answer scene) instead of a flat 0.35 s.
#  3) Room-tone bed: a synthesized quiet-room floor (pink noise, no hiss, slow drift) mixed under the
#     whole video at spec "room_tone_db" (default -50 dBFS RMS; null = off). Pauses never drop to digital zero.
#  4) Opt-in breaths: "[inhale]" in a scene's "tts" inserts a soft 0.34 s synthetic inhale there.
#     Max 2 per episode, only before the longest sentence. Markers are stripped from captions/timing.
#  Optional: spec "voice" may be a blend, e.g. {"af_heart": 0.8, "af_bella": 0.2} (off by default; af_heart is the brand voice).
BREATH_RE = re.compile(r"\[(?:inhale|breath)[^\]]*\]", re.I)
SR_TTS = 24000

def clean_tts(text):
    return re.sub(r"\s{2,}", " ", BREATH_RE.sub(" ", text)).strip()

VOICES_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voices.json")

def narrator_for(spec):
    """Rotation narrator for this episode's slot date (spec "slot_date" YYYY-MM-DD, else from post_id BB-YYYYMMDD-NNN)."""
    import datetime as _dt
    cfg = json.load(open(VOICES_JSON))
    d = spec.get("slot_date")
    if not d and str(spec.get("post_id", "")).startswith("BB-"):
        x = spec["post_id"].split("-")[1]; d = f"{x[:4]}-{x[4:6]}-{x[6:8]}"
    if not d:
        return cfg["fallback"], None
    vs = cfg["voices"]
    i = (_dt.date.fromisoformat(d) - _dt.date.fromisoformat(cfg["start_date"])).days % len(vs)
    nar = vs[i]
    female = nar[:2] in ("af", "bf")
    quote = next(vs[(i + k) % len(vs)] for k in range(1, len(vs)) if (vs[(i + k) % len(vs)][:2] in ("af", "bf")) != female)
    return nar, quote

def resolve_voice(v, kokoro):
    if isinstance(v, dict):
        tot = sum(v.values())
        return sum(kokoro.get_voice_style(k) * (w / tot) for k, w in v.items())
    return v

def breath_sound(sr, rng, dur=0.34):
    n = int(dur * sr)
    F = np.fft.rfft(rng.standard_normal(n)); f = np.fft.rfftfreq(n, 1 / sr)
    shape = ((f > 250) & (f < 3500)) / (1 + f / 1400)
    x = np.fft.irfft(F * shape, n)
    t = np.linspace(0, 1, n)
    env = np.where(t < 0.72, (t / 0.72) ** 1.6, (1 - t) / 0.28)  # slow draw in, quick release
    x = x * env
    return (x / (np.max(np.abs(x)) or 1)).astype(np.float32)

def sentence_gap(sent, rng):
    s = sent.rstrip()
    if s.endswith("...") or s.endswith("\u2026"):
        g = rng.uniform(0.45, 0.60)
    elif s.endswith("?"):
        g = rng.uniform(0.36, 0.46)
    elif s.endswith("!"):
        g = rng.uniform(0.24, 0.32)
    else:
        g = rng.uniform(0.20, 0.38)
    if len(s.split()) <= 6:
        g += 0.06
    return g

def tts_scene(text, voice, speed, path, kokoro, rng=None, info=None):
    rng = rng or np.random.default_rng(0)
    items = []
    for pc in re.split(r"(\[(?:inhale|breath)[^\]]*\])", text, flags=re.I):
        if not pc.strip():
            continue
        if BREATH_RE.fullmatch(pc.strip()):
            items.append(("breath", None)); continue
        for snt in re.split(r"(?<=[.!?\u2026])\s+", pc.strip()):
            if snt.strip():
                items.append(("say", snt.strip()))
    chunks, gaps, breaths = [], [], 0
    for k, (kind, snt) in enumerate(items):
        nxt = items[k + 1] if k + 1 < len(items) else None
        if kind == "breath":
            chunks += [np.zeros(int(0.06 * SR_TTS), np.float32), ("breath", breath_sound(SR_TTS, rng)),
                       np.zeros(int(0.07 * SR_TTS), np.float32)]
            breaths += 1
            continue
        a, _ = kokoro.create(snt, voice=voice, speed=speed, lang="en-us",
                             sentence_pause=0.0, clause_pause=float(rng.uniform(0.07, 0.13)))
        chunks.append(np.asarray(a, np.float32))
        if nxt is not None and nxt[0] == "say":
            g = sentence_gap(snt, rng); gaps.append(round(g, 3))
            chunks.append(np.zeros(int(g * SR_TTS), np.float32))
    # breaths sit ~23 dB under the speech peak of this scene (Kokoro's output level varies by voice/text)
    speech_peak = max([float(np.max(np.abs(c))) for c in chunks if not isinstance(c, tuple) and len(c)] or [1.0])
    chunks = [c[1] * 0.07 * speech_peak if isinstance(c, tuple) else c for c in chunks]
    s = np.clip(np.concatenate(chunks), -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR_TTS)
        w.writeframes((s * 32767).astype("int16").tobytes())
    if info is not None:
        info["gaps"] = gaps; info["breaths"] = breaths
    return len(s) / SR_TTS, SR_TTS

def room_tone(n, sr, db, seed):
    """Quiet-room floor: pink noise, highs rolled off (no hiss), nothing under 40 Hz, slow +/-1 dB drift."""
    rng = np.random.default_rng(seed)
    F = np.fft.rfft(rng.standard_normal(n)); f = np.fft.rfftfreq(n, 1 / sr); f[0] = 1.0
    shape = (1 / np.sqrt(f)) / (1 + (f / 3500) ** 2)
    shape[f < 40] = 0
    x = np.fft.irfft(F * shape, n)
    t = np.arange(n) / sr
    x *= 10 ** ((0.7 * np.sin(2 * np.pi * t / 7.3) + 0.35 * np.sin(2 * np.pi * t / 2.9 + 1.0)) / 20)
    x = x / np.sqrt(np.mean(x ** 2)) * 10 ** (db / 20)
    return x.astype(np.float32)

def audio_stats(video_path):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", video_path, "-vn", "-ac", "1", "-ar", "48000",
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, dtype=np.float32)
    z = (a == 0).astype(np.int8)
    longest = 0
    if z.any():
        d = np.diff(np.concatenate([[0], z, [0]]))
        longest = int(np.max(np.flatnonzero(d == -1) - np.flatnonzero(d == 1)))
    w = 2400  # 50 ms windows
    rms = np.sqrt(np.mean(a[: len(a) // w * w].reshape(-1, w) ** 2, axis=1) + 1e-20)
    return dict(longest_digital_zero_s=round(longest / 48000, 3),
                floor_dbfs_p5=round(float(20 * np.log10(np.percentile(rms, 5))), 1))

STOP_END = {"a", "an", "the", "at", "of", "to", "in", "on", "for", "and", "or", "but", "by", "with",
            "from", "per", "as", "is", "are", "was", "that", "this", "its", "your", "their", "into", "who",
            "have", "has", "had", "be", "can", "will", "would", "were", "my", "our",
            "you", "what", "than", "when", "where", "if", "so", "it", "they", "we",
            "could", "should", "did", "does", "do", "about", "why", "how"}

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
    cover_hold = DZ.M["cover_hold"] if cover_path else 0.0
    spec = json.load(open(spec_path))
    # ---- v4 (2026-11-26): custom illustrated scenes, environments, transitions, sound effects ----
    v4 = spec.get("workflow") == "v4"
    scene_mod = None
    if v4 or any(sc.get("visual") == "custom" for sc in spec["scenes"]):
        mp = os.path.join(os.path.dirname(os.path.abspath(spec_path)), spec.get("scene_module", "scenes.py"))
        if os.path.exists(mp):
            ms = importlib.util.spec_from_file_location("episode_scenes", mp)
            scene_mod = importlib.util.module_from_spec(ms); ms.loader.exec_module(scene_mod)
    # EXP-06: "opening": "motion" = after the 0.5 s cover, the first scene opens with a push-in and a moving visual.
    # "static" (default) = the current behaviour. The daily task alternates these by date (see Growth/experiment-log.md).
    opening = spec.get("opening", "static")
    if opening == "motion" and spec["scenes"][0]["visual"] == "hook":
        print("WARNING: opening=motion but scene 1 uses the static 'hook' card; use 'build' or another animated visual.")
    os.makedirs(out, exist_ok=True)
    work = os.path.join(out, "_work"); os.makedirs(work, exist_ok=True)
    os.makedirs(os.path.join(out, "images"), exist_ok=True)
    from kokoro_onnx import Kokoro
    tts_dir = spec.get("tts_dir", "/home/claude/tts")
    kokoro = Kokoro(os.path.join(tts_dir, "kokoro.onnx"), os.path.join(tts_dir, "voices.bin"))
    voice, speed = spec.get("voice", "rotation"), spec.get("speed", 1.08)
    quote_voice = None
    if voice == "rotation":  # default since 2026-11-23: a different narrator each episode (templates/voices.json)
        voice, quote_voice = narrator_for(spec)
    lead, tail = 0.15, 0.35
    seed = zlib.crc32(str(spec.get("post_id", spec_path)).encode())
    room_db = spec.get("room_tone_db", -50)
    audio_info = dict(room_tone_db=room_db, narrator=voice, quote_voice=quote_voice, scenes=[])
    nbreath = 0
    for sc in spec["scenes"]:
        sc["_tts_raw"] = sc["tts"]
        nbreath += len(BREATH_RE.findall(sc["tts"]))
        sc["tts"] = clean_tts(sc["tts"])

    # 1) narration per scene -> durations
    timeline, t0 = [], cover_hold
    for i, sc in enumerate(spec["scenes"]):
        wav = os.path.join(work, f"a{i:02}.wav")
        # Per-scene overrides (Script System v2): "voice" for a second character
        # (quoted myth, viewer question), "speed" for pacing (0.98-1.14 range).
        sv0 = sc.get("voice", voice)
        if sv0 == "quote":
            sv0 = quote_voice or "am_michael"
        sv = resolve_voice(sv0, kokoro)
        ss = max(0.9, min(1.2, float(sc.get("speed", speed))))
        rng = np.random.default_rng([seed, i])
        info = {}
        # TTS cache (v4): identical text + voice + speed + seed reuses the previous take, so re-renders after
        # visual fixes don't re-synthesize narration (and sound identical).
        ck = zlib.crc32(json.dumps([sc["_tts_raw"], str(sv0), ss, int(seed), i]).encode())
        cwav, cinfo = os.path.join(work, f"tts_{ck:08x}.wav"), os.path.join(work, f"tts_{ck:08x}.json")
        if os.path.exists(cwav) and os.path.exists(cinfo):
            shutil.copy(cwav, wav); c_ = json.load(open(cinfo)); dur, sr = c_["dur"], c_["sr"]; info.update(c_["info"])
        else:
            dur, sr = tts_scene(sc["_tts_raw"], sv, ss, wav, kokoro, rng, info)
            shutil.copy(wav, cwav); json.dump(dict(dur=dur, sr=sr, info=info), open(cinfo, "w"))
        nxt_vis = spec["scenes"][i + 1]["visual"] if i + 1 < len(spec["scenes"]) else None
        if "pause_after" in sc:
            stail = float(sc["pause_after"])
        elif nxt_vis in ("payoff", "answer"):
            stail = 0.55
        elif nxt_vis is None:
            stail = tail
        else:
            stail = float(rng.uniform(0.28, 0.46))
        info["tail"] = round(stail, 3)
        audio_info["scenes"].append(info)
        sdur = round((lead + dur + stail) * FPS) / FPS
        timeline.append(dict(i=i, start=t0, dur=sdur, speech=dur, wav=wav))
        t0 += sdur
    total = t0
    warns = []
    if nbreath > 2:
        warns.append(f"{nbreath} [inhale] markers; keep it to 2 per episode, before the longest sentences")
    for sc, tl in zip(spec["scenes"], timeline):
        sc["_p"] = resolve_times(sc.get("params", {}), sc["tts"], lead, tl["speech"], warns)
        sc["_p"]["_dur"] = tl["dur"]
        sc["_sfx"] = resolve_times(sc.get("sfx", []), sc["tts"], lead, tl["speech"], warns)
        if sc["visual"] == "custom" and (scene_mod is None or not hasattr(scene_mod, sc.get("params", {}).get("fn", ""))):
            sys.exit(f"scene {tl['i'] + 1}: custom visual needs params.fn defined in the episode's scenes.py")
        if sc["visual"] in LEGACY:
            warns.append(f"scene {tl['i'] + 1} uses legacy visual '{sc['visual']}' (allowed; v3 types preferred, see DESIGN.md)")
        for k in ("subject", "changes"):
            if k not in sc:
                warns.append(f"scene {tl['i'] + 1} has no '{k}' (needed for the scene plan)")

    # 2) captions timed across each scene's speech, proportional to characters
    cues = []
    for sc, tl in zip(spec["scenes"], timeline):
        # optional manual breaks: "|" in a caption forces a new chunk there (never shown on screen)
        parts = [c for seg in sc["caption"].split("|") if seg.strip() for c in chunk_caption(seg.strip())]
        n = sum(len(p) for p in parts)
        cur = tl["start"] + lead
        for p in parts:
            d_ = tl["speech"] * len(p) / n
            cues.append(dict(start=cur, end=cur + d_, text=p, scene=tl["i"]))
            cur += d_
    with open(os.path.join(out, "captions.srt"), "w") as f:
        for k, c in enumerate(cues, 1):
            f.write(f"{k}\n{srt_time(c['start'])} --> {srt_time(c['end'])}\n{c['text']}\n\n")
    # v4.1 "kinetic" burned-in captions: 1-3 word chunks, big, centred (captions.srt keeps full phrases)
    burn = cues
    if spec.get("caption_style") == "kinetic":
        burn = []
        for c in cues:
            ws = c["text"].split()
            groups, cur = [], []
            for w_ in ws:
                cur.append(w_)
                brk = len(cur) >= 3 or w_[-1:] in ",.:;?!" or (len(cur) >= 2 and len(" ".join(cur)) > 14)
                if brk and w_.lower().strip(",.:;?!\"'") in STOP_END and len(cur) < 4 and w_[-1:] not in ",.:;?!":
                    brk = False   # never end a chunk on a weak word ("in", "the", "of"...)
                if brk:
                    groups.append(cur); cur = []
            if cur:
                if groups and len(cur) == 1 and len(" ".join(groups[-1] + cur)) <= 18:
                    groups[-1] += cur
                else:
                    groups.append(cur)
            tot = sum(len(" ".join(g)) + 2 for g in groups)
            st = c["start"]
            for g in groups:
                d_ = (c["end"] - c["start"]) * (len(" ".join(g)) + 2) / tot
                burn.append(dict(start=st, end=st + d_, text=" ".join(g), scene=c["scene"]))
                st += d_

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
    prev_clean = None
    if v4 and cover_path:
        prev_clean = Image.open(cover_path).convert("RGB").resize((W, H))
    for sc, tl in zip(spec["scenes"], timeline):
        nfr = int(round(tl["dur"] * FPS))
        tmp = os.path.join(work, f"s{tl['i']:02}.tmp.mp4")
        fin = os.path.join(work, f"s{tl['i']:02}.mp4")
        proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                                 "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                                 "-pix_fmt", "yuv420p", "-r", str(FPS), tmp], stdin=subprocess.PIPE)
        fn = VISUALS.get(sc["visual"]) if sc["visual"] != "custom" else getattr(scene_mod, sc["_p"]["fn"])
        envname = sc.get("environment", spec.get("environment"))
        ENV = WD.env(envname) if (v4 or envname) else None
        trans = sc.get("transition", "fade" if not v4 else "dissolve") if tl["i"] > 0 else sc.get("transition", "none")
        tdur = float(sc.get("transition_dur", {"cut": 0, "none": 0, "fade": DZ.M["scene_fade"]}.get(trans, 0.4)))
        keyframe = None
        probe = {int(round(min(tl["dur"] - 0.1, 1.2) * FPS)), int(nfr * 0.85)}
        sc["_qa"] = set()
        for fr in range(nfr):
            t = fr / FPS
            gt = tl["start"] + t
            if v4:
                DZ.reg_reset()
                img = WD.background(envname); d = ImageDraw.Draw(img)
                if sc["visual"] == "custom":
                    ctx = dict(env=ENV, dur=tl["dur"], gt=gt, total=total, scene=tl["i"], fps=FPS, spec=spec)
                    r_ = fn(img, d, t, sc["_p"], ctx)
                    if isinstance(r_, Image.Image):
                        img = r_; d = ImageDraw.Draw(img)
                elif sc["visual"] in ("cta", "answer"):
                    fn(img, d, t, sc["_p"], logo_path)
                else:
                    fn(img, d, t, sc["_p"])
                clean = img
                if t < tdur and prev_clean is not None:  # transition from the previous scene's last clean frame
                    u = WD.ease_io(t / tdur)
                    if trans in ("dissolve", "fade"):
                        img = Image.blend(prev_clean, img, u)
                    elif trans in ("push_left", "push_up"):
                        fr_ = Image.new("RGB", (W, H))
                        if trans == "push_left":
                            off = int(W * u); fr_.paste(prev_clean, (-off, 0)); fr_.paste(img, (W - off, 0))
                        else:
                            off = int(H * u); fr_.paste(prev_clean, (0, -off)); fr_.paste(img, (0, H - off))
                        img = fr_
                    elif trans == "zoom_through":
                        img = Image.blend(WD.zoom(prev_clean, 1 + 0.6 * u), img, u)
                    d = ImageDraw.Draw(img)
                WD.chrome(img, d, spec["series"], gt / total, ENV, logo_path)
            else:
                img = background(); d = ImageDraw.Draw(img)
                chrome(img, d, spec["series"], gt / total, logo_path)
                DZ.reg_reset()
                if sc["visual"] in ("cta", "answer"):
                    fn(img, d, t, sc["_p"], logo_path)
                else:
                    fn(img, d, t, sc["_p"])
            if opening == "motion" and tl["i"] == 0 and t < 0.9:
                z = 1.10 - 0.10 * ease(t / 0.9)  # push-in: starts 10% zoomed, settles by 0.9 s
                zw, zh = int(W / z), int(H / z)
                l, tp = (W - zw) // 2, (H - zh) // 2
                img = img.crop((l, tp, l + zw, tp + zh)).resize((W, H), Image.BICUBIC)
                d = ImageDraw.Draw(img)
            cc = next((c for c in burn if c["start"] <= gt < c["end"]), None)
            if spec.get("caption_style") == "kinetic":
                WD.kinetic_caption(img, cc["text"] if cc else None, gt - cc["start"] if cc else 0, ENV or WD.env())
            else:
                caption(img, cc["text"] if cc else None)
            if fr in probe:
                sc["_qa"].update(DZ.layout_issues(DZ.REG["text"]))
                sc["_qa"].update(f"text shrunk to minimum and cut: '{x[:50]}'" for x in DZ.REG["fit"])
            if v4 and fr == nfr - 1:
                prev_clean = clean
            # gentle fade at scene start
            if not v4 and t < 0.2 and tl["i"] > 0:
                img = Image.blend(Image.new("RGB", (W, H), NAVY), img, min(1.0, 0.4 + 0.6 * t / DZ.M["scene_fade"]))
            proc.stdin.write(img.tobytes())
            if fr == int(nfr * 0.85):
                keyframe = img
        proc.stdin.close(); proc.wait()
        if proc.returncode != 0:
            sys.exit(f"scene {tl['i']} failed")
        os.replace(tmp, fin)
        keyframe.save(os.path.join(out, "images", f"scene{tl['i'] + 1:02}_{sc['_p'].get('fn', sc['visual']) if sc['visual'] == 'custom' else sc['visual']}.png"))
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
    sfx_cues = []
    for sc, tl in zip(spec["scenes"], timeline):
        for c in sc.get("_sfx", []):
            sfx_cues.append(dict(t=tl["start"] + float(c.get("at", 0)), sound=c["sound"], gain_db=c.get("gain_db", 0), scene=tl["i"] + 1))
    audio_info["sfx"] = [dict(t=round(c["t"], 2), sound=c["sound"], scene=c["scene"]) for c in sfx_cues]
    music = spec.get("music")
    audio_info["music"] = music
    if sfx_cues or music:
        sfx_wav = os.path.join(work, "sfx.wav")
        tr = SFX.build_track(sfx_cues, total, DZ.DS.get("sfx", {}).get("default_peak_db", -19))
        if music:
            mb = SFX.music_bed(total, seed, float(music.get("peak_db", -30)), int(music.get("bpm", 96)), music.get("mood", "curious"))
            tr[: len(mb)] += mb[: len(tr)]
        if room_db is not None:
            tr = tr + room_tone(len(tr), 48000, float(room_db), seed)
        with wave.open(sfx_wav, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(48000)
            w.writeframes((np.clip(tr, -1, 1) * 32767).astype("int16").tobytes())
        fc = ("[1:a]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[n];[2:a]aresample=48000[b];"
              "[n][b]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89[a]")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", nar, "-i", sfx_wav, "-filter_complex", fc,
                        "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                        "-shortest", "-movflags", "+faststart", tmpv], check=True)
    elif room_db is None:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", nar, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-shortest",
                        "-movflags", "+faststart", tmpv], check=True)
    else:
        # narration is loudness-normalized first, then the room-tone bed is added at its exact level
        bed = os.path.join(work, "roomtone.wav")
        b = room_tone(int(total * 48000), 48000, float(room_db), seed)
        with wave.open(bed, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(48000)
            w.writeframes((np.clip(b, -1, 1) * 32767).astype("int16").tobytes())
        fc = ("[1:a]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[n];[2:a]aresample=48000[b];"
              "[n][b]amix=inputs=2:normalize=0:duration=first[a]")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", nar, "-i", bed, "-filter_complex", fc,
                        "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                        "-shortest", "-movflags", "+faststart", tmpv], check=True)
    os.replace(tmpv, os.path.join(out, "video.mp4"))
    audio_info.update(audio_stats(os.path.join(out, "video.mp4")), breaths=nbreath)
    if room_db is not None and audio_info["longest_digital_zero_s"] > 0.05:
        warns.append(f"audio drops to digital zero for {audio_info['longest_digital_zero_s']} s despite room tone")
    json.dump(dict(total=total, scenes=timeline, cues=cues), open(os.path.join(work, "timeline.json"), "w"), indent=1)
    print(f"rendered {total:.2f}s, {len(cues)} captions")
    write_plan_and_qa(spec, timeline, cues, out, total, warns, cover_path)
    qp = os.path.join(out, "qa-report.json")
    if os.path.exists(qp):
        q = json.load(open(qp)); q["audio"] = audio_info
        if v4:
            q["workflow"] = "v4"
            q["editorial"] = {k: spec.get("record", {}).get(k) for k in
                              ("editorial_contribution", "narrative_structure", "animation_approach", "cover_composition")}
            q["transitions"] = [sc.get("transition", "dissolve") for sc in spec["scenes"][1:]]
            q["environments"] = sorted({sc.get("environment", spec.get("environment")) or "navy_classic" for sc in spec["scenes"]})
        json.dump(q, open(qp, "w"), indent=1)
    print("audio:", {k: v for k, v in audio_info.items() if k != "scenes"})
    if total <= 61:
        print(f"WARNING: video is {total:.2f}s; it must be longer than 61 s (target 65-90). Lengthen the script and re-render.")
    if total > 90:
        print(f"WARNING: video is {total:.2f}s; keep it at or under 90 s.")

def _facts(p, acc):
    if isinstance(p, dict):
        for k, v in p.items():
            if k.startswith("_"):
                continue
            if k in ("label", "value", "unit", "source", "note", "text", "kicker", "headline", "line", "sub", "total",
                     "before", "after", "left", "right", "boundary", "icon_label", "result", "action", "vs"):
                if isinstance(v, (str, int, float)):
                    acc.append(f"{k}: {v}")
            if k == "illustrative" and v:
                acc.append("ILLUSTRATIVE NUMBERS badge")
            _facts(v, acc)
    elif isinstance(p, list):
        for x in p:
            _facts(x, acc)
    return acc

def _assets(p, acc):
    if isinstance(p, dict):
        for k, v in p.items():
            if k in ("icon", "result_icon", "name") and isinstance(v, str):
                acc.add(f"Lucide icon '{v}' (ISC, templates/icons)")
            if k == "image" and isinstance(v, str):
                acc.add(f"image {v} (rights in sources-and-rights.md)")
            _assets(v, acc)
    elif isinstance(p, list):
        for x in p:
            _assets(x, acc)
    return acc

def write_plan_and_qa(spec, timeline, cues, out, total, warns, cover_path):
    """scene-plan.md/.json (production-ready plan per beat) + qa-report.json + qa-sheet.png."""
    plan = []
    for sc, tl in zip(spec["scenes"], timeline):
        p = sc["_p"]
        changes = sc.get("changes") or []
        auto = []
        for k, v in p.items():
            if k == "at" and isinstance(v, list):
                auto += [f"{v_:.1f}s: state {i + 1}" for i, v_ in enumerate(v)]
            elif (k.endswith("_at") or k == "at") and isinstance(v, (int, float)):
                auto.append(f"{v:.1f}s: {k}")
        for e in p.get("elements", []) if isinstance(p.get("elements"), list) else []:
            for k in ("show", "hide", "track"):
                if e.get(k):
                    auto.append(f"{float(e[k]):.1f}s: {e.get('type')} {e.get('name', e.get('text', ''))[:30]} {k}")
            for k in ("move", "rotate"):
                if e.get(k):
                    auto.append(f"{float(e[k].get('at', 0)):.1f}s: {e.get('type')} {k}")
        plan.append(dict(
            beat=tl["i"] + 1, start=round(tl["start"], 2), end=round(tl["start"] + tl["dur"], 2),
            narration=sc["tts"],
            captions=[dict(start=round(c["start"], 2), end=round(c["end"], 2), text=c["text"]) for c in cues if c["scene"] == tl["i"]],
            scene_type=sc["visual"], subject=sc.get("subject", ""),
            labels_values_units_sources=_facts(p, []),
            changes=changes, changes_auto=sorted(set(auto), key=lambda x: float(x.split("s:")[0])),
            assets=sorted(_assets(p, set())) or ["drawn in renderer (no external asset)"],
            explain=sc.get("explain"), environment=sc.get("environment", spec.get("environment")),
            transition=sc.get("transition"), sfx=[c.get("sound") for c in sc.get("_sfx", [])],
            qa=sorted(sc.get("_qa", set()))))
    json.dump(dict(total=round(total, 2), cover=bool(cover_path), opening=spec.get("opening", "static"), beats=plan),
              open(os.path.join(out, "scene-plan.json"), "w"), indent=1)
    with open(os.path.join(out, "scene-plan.md"), "w") as f:
        f.write(f"# Scene plan · {spec.get('title', spec.get('series', ''))}\n\nTotal {total:.1f} s · opening {spec.get('opening', 'static')} · design system v{DZ.DS['version']}\n")
        rec = spec.get("record")
        if rec:
            f.write("\n## Episode record (v4)\n")
            for k in ("question", "editorial_contribution", "narrative_structure", "animation_approach", "custom_scene",
                      "cover_composition", "similar_recent_episodes"):
                v_ = rec.get(k)
                if v_:
                    f.write(f"- **{k.replace('_', ' ').capitalize()}:** {json.dumps(v_, ensure_ascii=False) if not isinstance(v_, str) else v_}\n")
        if cover_path:
            f.write(f"\n**0.00–{DZ.M['cover_hold']:.2f} s · cover** (frame 0 = thumbnail)\n")
        for b in plan:
            f.write(f"\n## Beat {b['beat']} · {b['start']:.2f}–{b['end']:.2f} s · {b['scene_type']}\n")
            f.write(f"- **Main visual subject:** {b['subject'] or '(missing)'}\n- **Narration:** {b['narration']}\n")
            f.write("- **Caption chunks:** " + " / ".join(f"[{c['start']:.1f}–{c['end']:.1f}] {c['text']}" for c in b["captions"]) + "\n")
            f.write("- **Labels, values, units, sources:** " + ("; ".join(b["labels_values_units_sources"]) or "none") + "\n")
            f.write("- **What changes and when:** " + ("; ".join(b["changes"] + b["changes_auto"]) or "static hold") + "\n")
            f.write("- **Assets:** " + "; ".join(b["assets"]) + "\n")
            if b.get("explain"):
                ex = b["explain"]
                for k in ("understand", "objects", "change", "cause", "text"):
                    if ex.get(k):
                        f.write(f"- **{ {'understand': 'Viewer must understand', 'objects': 'Visible objects', 'change': 'What changes over time', 'cause': 'What causes the change', 'text': 'Necessary on-screen text'}[k] }:** {ex[k] if isinstance(ex[k], str) else '; '.join(ex[k])}\n")
            if b.get("environment") or b.get("transition") or b.get("sfx"):
                f.write(f"- **Environment / transition in / sound:** {b.get('environment') or 'navy_classic'} / {b.get('transition') or 'default'} / {', '.join(b['sfx']) or 'none'}\n")
            if b["qa"]:
                f.write("- **Layout check:** " + "; ".join(b["qa"]) + "\n")
    issues = sorted({q for b in plan for q in b["qa"]})
    missing = sorted(DZ.REG["missing_icons"])
    rep_ = dict(design_version=DZ.DS["version"], duration=round(total, 2),
                duration_ok=61 < total <= 90, cover_first_frame=bool(cover_path),
                layout_issues=issues, missing_icons=missing, warnings=warns,
                guides_status=DZ.DS["platform_guides"]["_status"],
                pass_=bool(61 < total <= 90 and cover_path and not issues and not missing))
    json.dump(rep_, open(os.path.join(out, "qa-report.json"), "w"), indent=1)
    # phone-size contact sheet with guides: cover, 0.6 s, each scene keyframe
    try:
        vid = os.path.join(out, "video.mp4")
        times = [0.1, 0.6] + [b["start"] + min(1.2, (b["end"] - b["start"]) * 0.5) for b in plan]
        thumbs = []
        for k, tm in enumerate(times):
            fp = os.path.join(out, "_work", f"qa_{k:02}.png")
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{tm:.2f}", "-i", vid, "-frames:v", "1", fp], check=True)
            thumbs.append(DZ.guides_overlay(Image.open(fp).convert("RGB")).resize((270, 480)))
        cols = 6
        rows = (len(thumbs) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * 280 + 10, rows * 490 + 10), (24, 24, 28))
        for k, th in enumerate(thumbs):
            sheet.paste(th, (10 + (k % cols) * 280, 10 + (k // cols) * 490))
        sheet.save(os.path.join(out, "qa-sheet.png"))
    except Exception as ex:
        warns.append(f"qa-sheet not made: {ex}")
    print("QA:", "PASS" if rep_["pass_"] else "CHECK", f"| layout issues {len(issues)} | missing icons {len(missing)} | warnings {len(warns)}")
    for x in issues[:12] + missing + warns[:12]:
        print("  -", x)

if __name__ == "__main__":
    main()
