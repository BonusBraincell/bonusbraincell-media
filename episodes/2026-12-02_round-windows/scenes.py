"""Custom scenes · Why are airplane windows rounded? (v4 demo, VISUAL CASE FILE + SYSTEM CUTAWAY)

A small mystery resolved through evidence: two Comet break-ups in 1954, three exhibits (pressurized cabin, the
Farnborough water-tank test, the Elba wreckage), then the mechanism (force in the skin detours around a cut-out
and piles up where the edge turns tightest) and a labeled simplified model (Inglis: peak = 1 + 2*sqrt(a/rho)).
Environment: case_file (paper desk). Yellow highlighter = the thing to track; red pencil = evidence marks.
"""
import math
from PIL import Image, ImageDraw, ImageFont
import world as WD
import design as DZ

NAVY = DZ.C["bg"]; Y = DZ.C["track"]; RED = (192, 57, 43); MANILA = (217, 183, 122); MANILA_D = (186, 150, 92)
PAPER = (247, 241, 227); GREY = (91, 90, 85); WATER = (120, 170, 205); BLUE = (47, 93, 138)
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
def M(sz): return ImageFont.truetype(MONO, sz)

def mono(d, xy, s, sz=34, fill=NAVY, anchor="lm"):
    d.text(xy, s, font=M(sz), fill=fill, anchor=anchor)
    bb = d.textbbox(xy, s, font=M(sz), anchor=anchor)
    DZ.REG["text"].append(dict(box=bb, role="label", size=sz, text=s[:60]))

def stamp(img, cx, cy, s, a=1.0, rot=-8, col=RED, sz=46):
    if a <= 0.02:
        return
    f = M(sz); tw = int(ImageDraw.Draw(img).textlength(s, font=f))
    lay = Image.new("RGBA", (tw + 60, sz + 50), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.rounded_rectangle([4, 4, tw + 56, sz + 46], radius=10, outline=col + (int(230 * a),), width=6)
    ld.text((30, (sz + 50) / 2), s, font=f, fill=col + (int(230 * a),), anchor="lm")
    sc = 1 + 0.5 * (1 - a)
    lay = lay.resize((int(lay.width * sc), int(lay.height * sc))).rotate(rot, expand=True, resample=Image.BICUBIC)
    img.paste(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)), lay)
    DZ.REG["text"].append(dict(box=(cx - lay.width / 2, cy - lay.height / 2, cx + lay.width / 2, cy + lay.height / 2), role="label", size=sz, text=s))

def card(img, box, rot=0, fill=PAPER, tab=None):
    WD.shadow(img, lambda m: m.rectangle(box, fill=255), (6, 14), 16, 90)
    d = ImageDraw.Draw(img)
    d.rectangle(box, fill=fill, outline=(205, 192, 160), width=2)
    if tab:
        d.rectangle([box[0], box[1] - 44, box[0] + 260, box[1]], fill=fill)
        mono(d, (box[0] + 20, box[1] - 22), tab, 26, GREY)
    return d

def plane(d, cx, cy, L=560, col=NAVY, win=True, wincol=PAPER, square=True):
    """Side view of an early jetliner: tube fuselage, swept fin, a row of squarish windows."""
    h = L * 0.11
    d.rounded_rectangle([cx - L / 2, cy - h / 2, cx + L / 2 - h * 0.2, cy + h / 2], radius=int(h / 2), fill=col)
    d.polygon([(cx + L / 2 - h * 1.6, cy - h / 2), (cx + L / 2 - h * 0.1, cy - h * 1.9), (cx + L / 2 + h * 0.15, cy - h * 1.9), (cx + L / 2, cy - h / 2)], fill=col)
    d.polygon([(cx - L * 0.06, cy + h * 0.2), (cx + L * 0.16, cy + h * 0.2), (cx + L * 0.26, cy + h * 1.1), (cx + L * 0.12, cy + h * 1.1)], fill=WD.lerp(col, (0, 0, 0), 0.2))
    if win:
        n = 11; ws = h * 0.32
        for k in range(n):
            x = cx - L * 0.32 + k * L * 0.05
            r = 3 if square else ws / 2
            d.rounded_rectangle([x - ws / 2, cy - h * 0.22 - ws / 2, x + ws / 2, cy - h * 0.22 + ws / 2], radius=r, fill=wincol)

def crack(d, x0, y0, u, ang=-35, L=150, col=RED, w=6, seed=3):
    import random
    rnd = random.Random(seed); pts = [(x0, y0)]; n = 9
    for k in range(1, int(n * WD.clamp(u)) + 1):
        a_ = math.radians(ang + rnd.uniform(-25, 25))
        pts.append((pts[-1][0] + L / n * math.cos(a_), pts[-1][1] + L / n * math.sin(a_)))
    if len(pts) > 1:
        d.line(pts, fill=col, width=w, joint="curve")

# ---------------- scenes ----------------
def c_hook(img, d, t, p, ctx):
    """Case folder on the desk: two flights, two dates, a red circle on a window corner."""
    d = card(img, [90, 520, 990, 1250], fill=MANILA, tab="CASE FILE")
    d.rectangle([90, 520, 990, 560], fill=MANILA_D)
    mono(d, (130, 610), "DE HAVILLAND COMET · 1954", 34, NAVY)
    a1 = 1.0 if ctx.get("cover") else WD.ease_out(WD.seg(t, 0.0, 0.4))
    a2 = 1.0 if ctx.get("cover") else WD.ease_out(WD.seg(t, p.get("two_at", 1.0), p.get("two_at", 1.0) + 0.4))
    for k, (date, where, a) in enumerate((("10 JAN 1954", "off Elba", a1), ("8 APR 1954", "near Naples", a2))):
        y = 740 + k * 190
        if a > 0.02:
            plane(d, 400, y, 520, WD.lerp(MANILA, NAVY, a), wincol=MANILA)
            mono(d, (690, y - 20), date, 32, WD.lerp(MANILA, NAVY, a))
            mono(d, (690, y + 22), where, 30, WD.lerp(MANILA, GREY, a))
    ca = 1.0 if ctx.get("cover") else WD.ease_out(WD.seg(t, p.get("clue_at", 3.0), p.get("clue_at", 3.0) + 0.5))
    if ca > 0:  # magnified window corner with the red pencil ring
        cx, cy, r = 760, 1120, 80
        # inside the lens (clipped): the top-left corner of a window frame, a hairline crack leaving the corner
        lens = Image.new("RGB", (2 * r, 2 * r), PAPER); ld = ImageDraw.Draw(lens)
        ld.rounded_rectangle([r - 30, r - 30, r + 200, r + 200], radius=30, fill=(206, 222, 235), outline=NAVY, width=12)
        crack(ld, r - 24, r - 24, ca, -135, 70, RED, 5, seed=5)
        m = Image.new("L", (2 * r, 2 * r), 0); ImageDraw.Draw(m).ellipse([0, 0, 2 * r - 1, 2 * r - 1], fill=255)
        img.paste(lens, (cx - r, cy - r), m)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=NAVY, width=5)
        d.arc([cx - r - 18, cy - r - 18, cx + r + 18, cy + r + 18], -200, -200 + 360 * ca, fill=RED, width=8)
        d.line([(cx + r * 0.7, cy + r * 0.7), (cx + r * 1.3, cy + r * 1.3)], fill=NAVY, width=12)
    stamp(img, 780, 610, "UNSOLVED", 1.0 if ctx.get("cover") else WD.ease_out(WD.seg(t, 0.2, 0.6)), rot=-6, sz=40)
    return img

def c_cabin(img, d, t, p, ctx):
    """Exhibit 1: the cabin cross-section breathes out on every flight (pressure arrows), then relaxes."""
    d = card(img, [110, 560, 970, 1240], tab="EXHIBIT 1")
    mono(d, (150, 620), "PRESSURIZED CABIN", 34)
    cyc = 0.5 - 0.5 * math.cos(2 * math.pi * t / 3.2)
    cx, cy, R = 540, 905, 190 + 14 * cyc
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=NAVY, width=14)
    for k in range(12):
        a_ = 2 * math.pi * k / 12
        r0, r1 = R - 120, R - 30 + 40 * cyc
        DZ.arrow(d, (cx + r0 * math.cos(a_), cy + r0 * math.sin(a_)), (cx + r1 * math.cos(a_), cy + r1 * math.sin(a_)), "bg", 7, 0.25 + 0.75 * cyc, 24)
    d.rectangle([cx + R - 20, cy - 34, cx + R + 6, cy + 34], fill=Y)
    WD.label(d, "window cut-out", (cx + R - 8, cy - 30), (cx + R - 60, cy - 230), WD.env("case_file"), "small", NAVY, 1.0)
    ga = WD.ease_out(WD.seg(t, p.get("psi_at", 1.5), p.get("psi_at", 1.5) + 0.4))
    if ga > 0:
        WD.T(d, (540, 1180), "≈ 8.25 psi more inside than out", "label", NAVY, "mm")
    return img

def c_tank(img, d, t, p, ctx):
    """Exhibit 2: the whole fuselage in a water tank, pumped up and down; cycle counter; crack at a hatch corner."""
    dur = p["_dur"]; split = p.get("split_at", dur * 0.7)
    d = card(img, [90, 560, 990, 1250], tab="EXHIBIT 2")
    mono(d, (130, 615), "WATER TANK · FARNBOROUGH", 32)
    # tank
    d.rectangle([140, 700, 940, 1010], fill=WD.lerp(PAPER, WATER, 0.55), outline=BLUE, width=6)
    for k in range(6):
        y = 720 + k * 50 + 6 * math.sin(t * 2 + k)
        d.line([(160, y), (920, y)], fill=WD.lerp(PAPER, WATER, 0.75), width=3)
    cyc = 0.5 - 0.5 * math.cos(2 * math.pi * t / 0.9)
    plane(d, 520, 860, 700 + 6 * cyc, NAVY, wincol=WD.lerp(PAPER, WATER, 0.4))
    # counter: real flights already flown + tank cycles
    n = int(WD.counter(t, 0.3, max(0.5, split - 0.3), 1230, 3060))
    WD.T(d, (540, 1075), f"{n:,} cycles", "value", NAVY, "mm", size=72)
    WD.T(d, (540, 1140), "1,230 real flights + 1,830 in the tank", "small", GREY, "mm", size=30)
    ca = WD.seg(t, split, split + 0.8)
    if ca > 0:
        hx, hy = 330, 845  # forward escape-hatch window corner
        d.rounded_rectangle([hx - 26, hy - 26, hx + 26, hy + 26], radius=6, outline=Y, width=8)
        crack(d, hx + 26, hy - 26, ca, -50, 140)
        crack(d, hx - 26, hy + 26, ca, 140, 120, seed=8)
        stamp(img, 560, 1222, "FAILED AT A CORNER", WD.ease_out(WD.seg(t, split + 0.4, split + 0.8)), rot=-3, sz=32)
    return img

def c_wreck(img, d, t, p, ctx):
    """Exhibit 3: a recovered roof panel from the Elba wreck with a window cut-out and fatigue marks."""
    d = card(img, [130, 560, 950, 1240], tab="EXHIBIT 3", fill=(240, 236, 228))
    mono(d, (170, 615), "ELBA WRECKAGE · ROOF PANEL", 32)
    # torn panel
    pts = [(220, 700), (520, 680), (760, 720), (860, 820), (830, 1060), (600, 1110), (300, 1090), (200, 960)]
    d.polygon(pts, fill=(176, 184, 194), outline=(110, 118, 130))
    for k in range(9):  # rivet rows
        d.ellipse([260 + k * 64, 760, 270 + k * 64, 770], fill=(120, 128, 140))
        d.ellipse([260 + k * 64, 1030, 270 + k * 64, 1040], fill=(120, 128, 140))
    wx, wy = 520, 900
    d.rounded_rectangle([wx - 110, wy - 70, wx + 110, wy + 70], radius=18, fill=(70, 78, 92))
    a = WD.ease_out(WD.seg(t, p.get("mark_at", 1.5), p.get("mark_at", 1.5) + 0.6))
    if a > 0:  # beach marks: concentric arcs = fatigue fingerprint
        for k in range(6):  # concentric "beach marks" spreading from the window corner
            r = 22 + k * 20
            d.arc([wx + 110 - r, wy - 70 - r, wx + 110 + r, wy - 70 + r], 180, 360, fill=WD.lerp((176, 184, 194), (120, 60, 50), a), width=5)
        d.ellipse([wx + 110 - 160, wy - 70 - 160, wx + 110 + 160, wy - 70 + 160], outline=WD.lerp((176, 184, 194), RED, a), width=8)
        WD.label(d, "fatigue marks", (wx + 140, wy - 100), (700, 1160), WD.env("case_file"), "small", RED, a)
    return img

def _flow_y(x, y0, hx, hw, hh, sharp):
    """Illustrative stress-flow line: lines detour around the cut-out and crowd at its edges."""
    s = 1 if y0 >= 0 else -1
    k = math.exp(-((x - hx) / (hw * 0.95)) ** (6 if sharp else 2))
    push = (hh + 8) * k * math.exp(-abs(y0) / (hh * 2.2))
    return y0 + s * push

def c_flow(img, d, t, p, ctx):
    """Mechanism: force lines in a stretched skin detour around a window and bunch at its corners."""
    cx, cy = 540, 890
    hw, hh = 150, 120
    d.rectangle([110, 600, 970, 1190], fill=(250, 247, 240), outline=(185, 170, 140), width=3)
    mono(d, (110, 565), "FORCE IN THE SKIN  (illustration)", 28, GREY)
    lines = [-240, -195, -160, -128, -100, -78, -58, 58, 78, 100, 128, 160, 195, 240]
    for y0 in lines:
        pts = [(x, cy + _flow_y(x, y0 * 1.0, cx, hw, hh, True)) for x in range(130, 960, 10)]
        d.line(pts, fill=BLUE, width=4)
        # traffic: dots moving along the line, slowing where lines crowd
        for j in range(3):
            u = ((t * 0.18 + j / 3 + abs(y0) / 997) % 1.0)
            x = 130 + 820 * u
            y = cy + _flow_y(x, y0, cx, hw, hh, True)
            d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=NAVY)
    d.rounded_rectangle([cx - hw, cy - hh * 0.62, cx + hw, cy + hh * 0.62], radius=14, fill=(70, 78, 92))
    ha = WD.ease_out(WD.seg(t, p.get("pile_at", 2.0), p.get("pile_at", 2.0) + 0.6))
    if ha > 0:
        for sx in (-1, 1):
            for sy in (-1, 1):
                WD.glow(img, cx + sx * hw, cy + sy * hh * 0.62, 70, Y, int(190 * ha))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([cx - hw, cy - hh * 0.62, cx + hw, cy + hh * 0.62], radius=14, fill=(70, 78, 92))
        WD.T(d, (540, 1228), "Force piles up where the edge turns", "label", NAVY, "mm")
    return img

def c_model(img, d, t, p, ctx):
    """Simplified model (Inglis, 1913): peak stress factor = 1 + 2*sqrt(a/rho). Hole tip sharpens; marker climbs the curve."""
    dur = p["_dur"]
    d.rectangle([110, 580, 970, 1250], fill=(250, 247, 240), outline=(185, 170, 140), width=3)
    mono(d, (140, 620), "SIMPLIFIED MODEL · Inglis (1913)", 28, GREY)
    a_in = 8.0  # half-length of the hole, inches (illustrative)
    rho_min, rho_max = 0.5, 8.0
    u = WD.ease_io(WD.seg(t, p.get("squeeze_at", 1.0), dur - 0.8))
    rho = rho_max * (rho_min / rho_max) ** u
    k = 1 + 2 * math.sqrt(a_in / rho)
    # chart: x = tip radius (log, 8 → 0.5 in), y = stress factor 0..10
    gx0, gx1, gy0, gy1 = 200, 900, 1140, 770
    d.line([(gx0, gy0), (gx1, gy0)], fill=NAVY, width=4); d.line([(gx0, gy0), (gx0, gy1)], fill=NAVY, width=4)
    def X(r): return gx0 + (gx1 - gx0) * math.log(rho_max / r) / math.log(rho_max / rho_min)
    def Yv(v): return gy0 - (gy0 - gy1) * v / 10
    for v in (1, 3, 5, 7, 9):
        d.line([(gx0 - 10, Yv(v)), (gx0, Yv(v))], fill=NAVY, width=3)
        mono(d, (gx0 - 18, Yv(v)), f"{v}×", 26, GREY, "rm")
    curve = [(X(rho_max * (rho_min / rho_max) ** (j / 60)), Yv(1 + 2 * math.sqrt(a_in / (rho_max * (rho_min / rho_max) ** (j / 60))))) for j in range(61)]
    d.line(curve, fill=BLUE, width=5)
    d.line([(gx0, Yv(1)), (gx1, Yv(1))], fill=(185, 170, 140), width=2)
    mono(d, (gx1, Yv(1) - 22), "no hole = 1×", 26, GREY, "rm")
    mx, my = X(rho), Yv(k)
    d.ellipse([mx - 16, my - 16, mx + 16, my + 16], fill=Y, outline=NAVY, width=4)
    WD.T(d, (150, 690), f"peak ≈ {k:.1f}× average", "label", NAVY, "lm")
    mono(d, ((gx0 + gx1) / 2, gy0 + 38), "tip radius →  tighter", 26, GREY, "mm")
    # the hole itself, morphing from circle-like to slot (ellipse with same length, shrinking tip radius)
    b = math.sqrt(rho * a_in)
    sc = 6.0
    ex, ey = 820, 690
    d.ellipse([ex - a_in * sc, ey - b * sc, ex + a_in * sc, ey + b * sc], fill=(70, 78, 92))
    d.ellipse([ex + a_in * sc - 14, ey - 14, ex + a_in * sc + 14, ey + 14], fill=Y)
    WD.T(d, (540, 1232), "Model: elliptical hole in a flat, stretched plate. Shape only, not the Comet's numbers.", "source", GREY, "mm")
    return img

def c_twist(img, d, t, p, ctx):
    """The part retellings skip: the windows had 3-inch corner radii (to scale), but stress ran higher than calculated."""
    d = card(img, [110, 560, 970, 1250], tab="TEST REPORT")
    mono(d, (150, 615), "COMET 1 CABIN WINDOW", 32)
    s = 26.0  # px per inch
    W_, H_, R_ = 16.6 * s, 14 * s, 3 * s
    cx, cy = 540, 840
    d.rounded_rectangle([cx - W_ / 2, cy - H_ / 2, cx + W_ / 2, cy + H_ / 2], radius=int(R_), outline=NAVY, width=8, fill=(225, 232, 238))
    # dimensions
    d.line([(cx - W_ / 2, cy + H_ / 2 + 40), (cx + W_ / 2, cy + H_ / 2 + 40)], fill=GREY, width=3)
    mono(d, (cx, cy + H_ / 2 + 70), "16.6 in", 28, GREY, "mm")
    d.line([(cx + W_ / 2 + 30, cy - H_ / 2), (cx + W_ / 2 + 30, cy + H_ / 2)], fill=GREY, width=3)
    mono(d, (cx + W_ / 2 + 44, cy), "14 in", 28, GREY, "lm")
    ra = WD.ease_out(WD.seg(t, p.get("radius_at", 1.0), p.get("radius_at", 1.0) + 0.5))
    if ra > 0:
        qx, qy = cx - W_ / 2 + R_, cy - H_ / 2 + R_
        d.arc([qx - R_, qy - R_, qx + R_, qy + R_], 180, 270, fill=Y, width=14)
        WD.label(d, "r = 3 in", (qx - R_ * 0.7, qy - R_ * 0.7), (300, 1200), WD.env("case_file"), "small", NAVY, ra)
    ha = WD.ease_out(WD.seg(t, p.get("higher_at", 3.0), p.get("higher_at", 3.0) + 0.5))
    if ha > 0:
        mono(d, (540, 1175), "calc: under ½ strength", 26, WD.lerp(PAPER, GREY, ha))
        mono(d, (540, 1220), "tests: much higher", 30, WD.lerp(PAPER, RED, ha))
        d.line([(540, 1175), (850, 1175)], fill=WD.lerp(PAPER, RED, ha), width=4)
    return img

def c_trace(img, d, t, p, ctx):
    """Resolution: squarish window morphs into today's oval; a yellow highlighter traces the edge with no corner."""
    dur = p["_dur"]
    m = WD.ease_io(WD.seg(t, 0.3, 1.6))
    cx, cy = 540, 880
    w, h = 380, 500
    r = int(30 + (150 - 30) * m)
    d.rounded_rectangle([cx - w / 2 - 40, cy - h / 2 - 40, cx + w / 2 + 40, cy + h / 2 + 40], radius=r + 40, fill=(218, 222, 228))
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=r, fill=(150, 196, 230), outline=NAVY, width=8)
    for k in range(3):  # clouds
        ox = (t * 40 + k * 140) % (w + 120) - 60
        d.ellipse([cx - w / 2 + ox - 40, cy - 80 + k * 90, cx - w / 2 + ox + 50, cy - 40 + k * 90], fill=(240, 246, 250))
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=r, outline=NAVY, width=8)
    tu = WD.seg(t, p.get("trace_at", 2.5), p.get("trace_at", 2.5) + 2.0)
    if tu > 0:
        pts = WD.poly_round(cx, cy, w + 20, h + 20, r + 10, 16)
        n = max(2, int(len(pts) * tu))
        d.line(pts[:n], fill=Y, width=16, joint="curve")
        x, y = pts[n - 1]
        d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=NAVY)
    lab = "Comet 1: squarish" if m < 0.5 else "Today: no corners"
    WD.T(d, (540, 1230), lab, "label", NAVY, "mm")
    return img

def c_cover(img, d, t, p, ctx):
    """Cover art: the case folder (c_hook, fully revealed) moved up to leave room for a bottom headline."""
    tmp = WD.background("case_file")
    c_hook(tmp, ImageDraw.Draw(tmp), 9.0, dict(p, two_at=0, clue_at=0), dict(ctx, cover=True))
    img.paste(tmp.crop((0, 470, WD.W, 1270)), (0, 290))
    return img
