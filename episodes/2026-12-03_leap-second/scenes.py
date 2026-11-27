"""Custom scenes · Why are clocks dropping the leap second? (v4 demo, TWO WORLDS + DATA STORY + SCALE REVEAL)

Two worlds side by side for the whole episode: the ATOM clock (left, cyan) and the EARTH clock (right, a spinning
planet under the sun). Their gap is the through-line. Real data: the IERS leap-second table (via IANA tzdata
leap-seconds.list), 27 insertions 1972-2016. Decision: CGPM Resolution 5 (2026), continuous UTC from 20 May 2027,
|UT1-UTC| allowed up to 3,600 s. Environment: two_skies. Yellow = the gap (the thing to track).
"""
import math, datetime as dt
from PIL import Image, ImageDraw, ImageFont
import world as WD
import design as DZ

NAVY = DZ.C["bg"]; Y = DZ.C["track"]; INK = (244, 246, 251); MUTED = (165, 179, 214)
CYAN = (56, 209, 197); SUN = (255, 181, 71); OCEAN = (40, 96, 170); LAND = (70, 160, 110); RED = (235, 87, 87)
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
def M(sz): return ImageFont.truetype(MONO, sz)

# IERS leap seconds (effective dates; TAI-UTC after each), from /usr/share/zoneinfo/leap-seconds.list
LEAPS = ["1972-07-01", "1973-01-01", "1974-01-01", "1975-01-01", "1976-01-01", "1977-01-01", "1978-01-01", "1979-01-01",
         "1980-01-01", "1981-07-01", "1982-07-01", "1983-07-01", "1985-07-01", "1988-01-01", "1990-01-01", "1991-01-01",
         "1992-07-01", "1993-07-01", "1994-07-01", "1996-01-01", "1997-07-01", "1999-01-01", "2006-01-01", "2009-01-01",
         "2012-07-01", "2015-07-01", "2017-01-01"]

def mono(d, xy, s, sz=40, fill=INK, anchor="mm"):
    d.text(xy, s, font=M(sz), fill=fill, anchor=anchor)
    bb = d.textbbox(xy, s, font=M(sz), anchor=anchor)
    DZ.REG["text"].append(dict(box=bb, role="label", size=sz, text=s[:60]))

def panels(img, d, title_l="ATOM CLOCK", title_r="EARTH CLOCK", y0=560, y1=1060):
    for x0, x1, col, title in ((80, 525, (10, 44, 52), title_l), (555, 1000, (16, 22, 58), title_r)):
        WD.shadow(img, lambda m: m.rounded_rectangle([x0, y0, x1, y1], radius=30, fill=255), (0, 14), 18, 120)
        d.rounded_rectangle([x0, y0, x1, y1], radius=30, fill=col, outline=WD.lerp(col, INK, 0.25), width=3)
        WD.T(d, ((x0 + x1) / 2, y0 + 44), title, "badge", CYAN if "ATOM" in title else SUN, "mm")

def atom(d, cx, cy, t, r=110, col=CYAN):
    d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=col)
    for k in range(3):
        a0 = k * 60
        bb = [cx - r, cy - r * 0.38, cx + r, cy + r * 0.38]
        lay_pts = []
        for j in range(73):
            th = math.radians(j * 5)
            x, y = r * math.cos(th), r * 0.38 * math.sin(th)
            ca, sa = math.cos(math.radians(a0)), math.sin(math.radians(a0))
            lay_pts.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
        d.line(lay_pts, fill=WD.lerp((10, 44, 52), col, 0.6), width=3)
        th = t * 4 + k * 2.1
        x, y = r * math.cos(th), r * 0.38 * math.sin(th)
        ca, sa = math.cos(math.radians(a0)), math.sin(math.radians(a0))
        ex, ey = cx + x * ca - y * sa, cy + x * sa + y * ca
        d.ellipse([ex - 10, ey - 10, ex + 10, ey + 10], fill=INK)

def earth(img, d, cx, cy, R, spin, sun=True):
    """Earth seen from above the North Pole: day side toward the sun (top), a meridian marker that rotates."""
    if sun:
        sy = cy - R - 62
        WD.glow(img, cx, sy, 46, SUN, 140)
        d = ImageDraw.Draw(img)
        d.ellipse([cx - 22, sy - 22, cx + 22, sy + 22], fill=SUN)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=OCEAN)
    for k in range(5):  # continents as blobs around the pole, rotating
        a = spin + k * 1.3
        bx, by = cx + R * 0.55 * math.cos(a), cy + R * 0.55 * math.sin(a)
        d.ellipse([bx - R * 0.22, by - R * 0.16, bx + R * 0.22, by + R * 0.16], fill=LAND)
    night = Image.new("L", img.size, 0); nd = ImageDraw.Draw(night)
    nd.pieslice([cx - R, cy - R, cx + R, cy + R], 0, 180, fill=120)
    img.paste((4, 8, 24), (0, 0), night)
    d = ImageDraw.Draw(img)
    mx, my = cx + R * math.cos(spin), cy + R * math.sin(spin)
    d.line([(cx, cy), (mx, my)], fill=Y, width=6)
    d.ellipse([mx - 10, my - 10, mx + 10, my + 10], fill=Y)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=WD.lerp(OCEAN, INK, 0.4), width=3)
    return d

def gap_bar(d, value, vmax=1.0, y=1150, label=None, unit="s", a=1.0, col=None, show=True):
    """The gap between the two clocks, the episode's through-line (0 to vmax)."""
    x0, x1 = 160, 920
    d.rounded_rectangle([x0, y - 20, x1, y + 20], radius=20, fill=(20, 30, 62))
    w = (x1 - x0) * WD.clamp(abs(value) / vmax)
    if w > 4:
        d.rounded_rectangle([x0, y - 20, x0 + w, y + 20], radius=20, fill=col or Y)
    WD.T(d, (x0, y - 52), label or "GAP BETWEEN THE CLOCKS", "badge", MUTED, "lm")
    if show:
        WD.T(d, (x1, y - 52), f"{value:.2f} {unit}" if vmax <= 10 else f"{value:,.0f} {unit}", "badge", Y, "rm")

# ---------------- scenes ----------------
def l_hook(img, d, t, p, ctx):
    """Two clocks, two worlds: the atom clock ticks; Earth turns under the sun. A small yellow gap opens."""
    panels(img, d)
    atom(d, 302, 760, t)
    secs = int(t) % 60
    mono(d, (302, 960), f"12:00:{secs:02d}", 52, CYAN)
    d = earth(img, d, 778, 850, 125, -math.pi / 2 + 0.03 * t + 0.02)
    mono(d, (778, 1010), "sun overhead?", 30, SUN)
    ga = 1.0 if ctx.get("cover") else WD.ease_out(WD.seg(t, p.get("gap_at", 2.0), p.get("gap_at", 2.0) + 0.8))
    if ga > 0:
        gap_bar(d, 0.42 * ga, show=False)
    return img

def l_wobble(img, d, t, p, ctx):
    """Left: evenly spaced ticks. Right: Earth's day ticks, unevenly spaced, nudged by tides and the interior."""
    panels(img, d, "EVERY SECOND EQUAL", "EVERY DAY A LITTLE DIFFERENT")
    for k in range(9):  # metronome ticks
        x = 130 + k * 45
        on = int(t * 2) % 9 == k
        d.rectangle([x, 760, x + 18, 860], fill=CYAN if on else WD.lerp((10, 44, 52), CYAN, 0.45))
    mono(d, (302, 930), "cesium atoms", 34, CYAN)
    import random
    rnd = random.Random(5)
    x = 560
    for k in range(9):
        x += 40 + rnd.uniform(-12, 12)
        d.rectangle([x, 760, x + 18, 860], fill=WD.lerp((16, 22, 58), SUN, 0.55))
    a1 = WD.ease_out(WD.seg(t, p.get("tides_at", 1.5), p.get("tides_at", 1.5) + 0.4))
    a2 = WD.ease_out(WD.seg(t, p.get("inside_at", 3.0), p.get("inside_at", 3.0) + 0.4))
    if a1 > 0:
        mono(d, (778, 925), "tides: slower", 32, WD.lerp((16, 22, 58), INK, a1))
    if a2 > 0:
        mono(d, (778, 985), "inside: ±", 30, WD.lerp((16, 22, 58), INK, a2))
    return img

def l_calc(img, d, t, p, ctx):
    """Illustrative calculation: if every day ran 2.7 ms long, the gap reaches one full second in ~370 days."""
    dur = p["_dur"]
    WD.chip(d, (540, 560), "ILLUSTRATIVE NUMBERS", WD.env("two_skies"), fill=INK, fg=NAVY)
    WD.T(d, (540, 660), "each day: 86,400.0027 s", "label", INK, "mm")
    WD.T(d, (540, 715), "atom day: 86,400 s", "label", CYAN, "mm")
    days = WD.counter(t, p.get("pile_at", 1.0), max(1.0, dur - 2.0), 0, 370)
    gap = days * 0.0027
    # a calendar strip filling
    cols, rows = 20, 6
    for k in range(cols * rows):
        x = 150 + (k % cols) * 39; y = 790 + (k // cols) * 39
        filled = k < days / 370 * cols * rows
        d.rectangle([x, y, x + 30, y + 30], fill=Y if filled else (30, 44, 84))
    mono(d, (540, 1060), f"day {days:,.0f}", 46, INK)
    gap_bar(d, min(1.0, gap), 1.0, y=1180, label="EARTH BEHIND THE ATOMS")
    return img

def l_patch(img, d, t, p, ctx):
    """The patch: at 0.9 s, a leap second 23:59:60 is inserted and the gap snaps back."""
    dur = p["_dur"]; ins = p.get("insert_at", dur * 0.6)
    panels(img, d, "UTC CLOCK", "THE GAP")
    # digital clock counting into the leap second
    seq = ["23:59:58", "23:59:59", "23:59:60", "00:00:00"]
    k = int(WD.clamp((t - (ins - 1.0)) / 1.0, -1, 3)) if t >= ins - 1.0 else -1
    shown = seq[max(0, min(3, k + 1))] if t >= ins - 2.0 else "23:59:58"
    col = Y if shown == "23:59:60" else CYAN
    mono(d, (302, 790), shown[:6], 64, CYAN)
    mono(d, (302, 880), shown[6:], 120, col)
    if shown == "23:59:60":
        WD.T(d, (302, 990), "one extra second", "small", Y, "mm")
    # gap gauge on the right: climbs toward 0.9, drops by 1 at the insertion
    g = 0.6 + 0.3 * WD.seg(t, 0.2, ins) if t < ins else 0.9 - 1.0 * WD.ease_out(WD.seg(t, ins, ins + 0.4))
    gx, gy0, gy1 = 778, 1000, 650
    def Yg(v): return gy0 - (gy0 - gy1) * (v + 0.2) / 1.2
    d.line([(gx, Yg(-0.2)), (gx, Yg(1.0))], fill=(40, 52, 96), width=26)
    d.line([(gx, Yg(0)), (gx, Yg(g))], fill=Y if g >= 0 else RED, width=26)
    for v in (0.0, 0.9):
        d.line([(gx - 40, Yg(v)), (gx + 40, Yg(v))], fill=INK if v == 0 else RED, width=4)
        mono(d, (gx + 56, Yg(v)), f"{v:.1f} s", 28, INK if v == 0 else RED, "lm")
    return img

def l_data(img, d, t, p, ctx):
    """Real data: TAI-UTC staircase 10 s → 37 s, 1972-2017, with the 1970s highlighted."""
    dur = p["_dur"]
    x0, x1, y0, y1 = 170, 900, 1150, 700
    d1, d2 = dt.date(1972, 1, 1), dt.date(2018, 1, 1)
    def X(dd): return x0 + (x1 - x0) * (dd - d1).days / (d2 - d1).days
    def Yv(v): return y0 - (y0 - y1) * (v - 10) / 28
    d.line([(x0, y0), (x1, y0)], fill=MUTED, width=3)
    for yr in (1972, 1980, 1990, 2000, 2010):
        xx = X(dt.date(yr, 1, 1)); d.line([(xx, y0), (xx, y0 + 12)], fill=MUTED, width=3)
        mono(d, (xx, y0 + 36), str(yr), 26, MUTED)
    u = WD.seg(t, 0.2, dur * 0.65)
    shown = int(len(LEAPS) * u + 0.001)
    hl = WD.ease_out(WD.seg(t, p.get("seventies_at", 3.0), p.get("seventies_at", 3.0) + 0.5))
    if hl > 0:
        d.rectangle([X(dt.date(1972, 1, 1)), y1 - 10, X(dt.date(1980, 1, 2)), y0], fill=WD.lerp((7, 27, 46), (60, 50, 10), hl))
        mono(d, ((X(dt.date(1972, 1, 1)) + X(dt.date(1980, 1, 2))) / 2, y1 + 20), "9 in the 1970s", 28, Y)
    pts = [(X(d1), Yv(10))]; v = 10
    for k in range(shown):
        dd = dt.date.fromisoformat(LEAPS[k]); pts.append((X(dd), Yv(v))); v += 1; pts.append((X(dd), Yv(v)))
    pts.append((X(dt.date.fromisoformat(LEAPS[shown - 1])) if shown else X(d1), Yv(v)))
    if shown == len(LEAPS):
        pts.append((X(d2), Yv(v)))
    d.line(pts, fill=CYAN, width=6)
    WD.T(d, (x0, 600), f"leap seconds added: {shown}", "label", INK, "lm")
    la = WD.ease_out(WD.seg(t, p.get("last_at", dur * 0.8), p.get("last_at", dur * 0.8) + 0.4))
    if la > 0:
        lx = X(dt.date(2017, 1, 1)); ly = Yv(37)
        d.ellipse([lx - 14, ly - 14, lx + 14, ly + 14], fill=Y)
        WD.T(d, (lx - 10, ly - 46), "last one: Dec 31, 2016", "small", Y, "rm")
    WD.T(d, (540, 1262), "Source: IERS leap-second table (via IANA tzdata)", "source", MUTED, "mm")
    return img

def l_faster(img, d, t, p, ctx):
    """Earth speeds up: the gap shrinks toward the other side; a negative leap second (deleting 23:59:59) appears."""
    dur = p["_dur"]; neg = p.get("neg_at", dur * 0.55)
    d = earth(img, d, 540, 840, 190, -math.pi / 2 + t * 0.9)
    for k in range(3):  # speed lines
        a = t * 0.9 + k * 2.1
        d.arc([540 - 230, 840 - 230, 540 + 230, 840 + 230], math.degrees(a), math.degrees(a) + 40, fill=Y, width=6)
    if t > neg:
        a_ = WD.ease_out(WD.seg(t, neg, neg + 0.5))
        mono(d, (340, 1130), "23:59:58", 54, WD.lerp((10, 14, 38), CYAN, a_))
        mono(d, (740, 1130), "00:00:00", 54, WD.lerp((10, 14, 38), CYAN, a_))
        mono(d, (540, 1130), "59", 54, WD.lerp((10, 14, 38), RED, a_))
        d.line([(500, 1110), (580, 1150)], fill=WD.lerp((10, 14, 38), RED, a_), width=8)
        WD.T(d, (540, 1210), "never done before", "small", RED, "mm")
    pa = WD.ease_out(WD.seg(t, p.get("odds_at", dur * 0.8), p.get("odds_at", dur * 0.8) + 0.4))
    if pa > 0:
        WD.chip(d, (540, 1050), "30% CHANCE BY 2035 (CCTF/IERS)", WD.env("two_skies"), a=pa)
    return img

def l_reveal(img, d, t, p, ctx):
    """Scale reveal: the allowed gap zooms out from 0.9 s to 3,600 s (one hour), on a log axis."""
    dur = p["_dur"]; z = p.get("hour_at", dur * 0.55)
    WD.T(d, (540, 580), "from 20 May 2027", "label", INK, "mm")
    WD.T(d, (540, 640), "no more leap seconds", "small", MUTED, "mm")
    # log axis 0.1 s .. 10,000 s
    x0, x1, y = 140, 880, 960
    def X(v): return x0 + (x1 - x0) * (math.log10(v) + 1) / 5
    zoom = WD.ease_io(WD.seg(t, z - 1.8, z + 0.1))  # lands on "an hour", then holds
    d.line([(x0, y), (x1, y)], fill=MUTED, width=4)
    ticks = [(0.9, "0.9 s"), (60, "1 min"), (3600, "1 hour")]
    for v, lab in ticks:
        if v > 1 and zoom < 0.05:
            continue
        xx = X(v); a = 1 if v < 1 else zoom
        d.line([(xx, y - 18), (xx, y + 18)], fill=WD.lerp((10, 14, 38), INK, a), width=4)
        mono(d, (xx, y + 50), lab, 30, WD.lerp((10, 14, 38), INK, a))
    old = X(0.9)
    d.rectangle([x0, y - 60, old, y - 24], fill=CYAN)
    WD.T(d, (x0 + 10, y - 82), "old limit: 0.9 s", "small", CYAN, "lm") if zoom < 0.05 else WD.T(d, (old + 16, y - 42), "old limit", "small", CYAN, "lm")
    if zoom > 0.02:
        new = x0 + (X(3600) - x0) * zoom
        d.rectangle([x0, y - 150, new, y - 100], fill=Y)
        if zoom > 0.9:
            WD.T(d, (x1, y - 190), "new limit: 1 hour", "label", Y, "rm")
    WD.T(d, (540, 1110), "log scale: each step is 10×", "source", MUTED, "mm")
    WD.T(d, (540, 1262), "Source: CGPM Resolution 5 (2026), BIPM", "source", MUTED, "mm")
    return img

def l_payoff(img, d, t, p, ctx):
    """Payoff: phone (atom time) and sun (Earth time) side by side, a thin yellow gap drifting between them."""
    panels(img, d, "YOUR PHONE", "THE SUN")
    d.rounded_rectangle([232, 650, 372, 930], radius=26, outline=CYAN, width=8)
    mono(d, (302, 760), "12:00", 40, CYAN)
    d = earth(img, d, 778, 860, 115, -math.pi / 2 + 0.25 * math.sin(t * 0.6))
    gap_bar(d, 0.15 + 0.1 * math.sin(t * 0.5), 1.0, y=1150, label="ALLOWED TO DRIFT APART", show=False)
    return img

def l_cover(img, d, t, p, ctx):
    """Cover art: the two worlds up top, a giant 23:59:60 (the yellow :60 is the hook) below; headline goes between."""
    panels(img, d, y0=300, y1=760)
    atom(d, 302, 520, 1.3)
    mono(d, (302, 700), "ATOMS", 40, CYAN)
    d = earth(img, d, 778, 560, 120, -math.pi / 2 + 0.3)
    f = M(170)
    s1, s2 = "23:59:", "60"
    w1 = d.textlength(s1, font=f); w2 = d.textlength(s2, font=f)
    x = 540 - (w1 + w2) / 2
    d.text((x, 1340), s1, font=f, fill=INK, anchor="lm")
    d.text((x + w1, 1340), s2, font=f, fill=Y, anchor="lm")
    return img
