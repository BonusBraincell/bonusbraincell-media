"""Custom scenes · Why does airport security swab your hands? (v4, JOURNEY / FOLLOW_THE_JOURNEY + SYSTEM_CUTAWAY)

One invisible speck of residue (yellow, the thing to track) rides from a hand into a trace detector:
swab -> heated desorber (vapor) -> ion source (charge) -> drift tube race against a gas headwind ->
arrival time on a millisecond trace -> library check (alarm / no alarm). Environment: blueprint (engineering
cutaway). Everything is code-drawn; the machine is a generic, simplified ion mobility spectrometer (labeled),
the hand is a generic flat hand, and the peaks are labeled ILLUSTRATIVE.
"""
import math, random
from PIL import Image, ImageDraw
import world as WD
import design as DZ

Y = DZ.C["track"]; NAVY = DZ.C["bg"]
INK = (244, 246, 251); MUTED = (184, 205, 235); WHITE = (255, 255, 255)
SKIN = (236, 199, 168); SKIN_D = (205, 160, 128); SLEEVE = (40, 70, 120)
STEEL = (22, 52, 98); STEEL_L = (70, 120, 190); HOT = (255, 140, 60); CYAN = (127, 211, 255); GREEN = (60, 200, 120)
RED = (235, 87, 87)

# ---------------- pieces ----------------
def hand(img, d, cx, cy, s=1.0):
    """Generic flat open hand, palm to camera, fingers up. (cx, cy) = palm centre."""
    fingers = [(-105, 205, 60), (-36, 245, 64), (34, 235, 64), (102, 190, 58)]
    def sil(m):
        m.rounded_rectangle([cx - 150 * s, cy - 130 * s, cx + 150 * s, cy + 170 * s], radius=int(90 * s), fill=255)
        for dx, h, w in fingers:
            m.rounded_rectangle([cx + (dx - w / 2) * s, cy - (130 + h) * s, cx + (dx + w / 2) * s, cy - 60 * s], radius=int(w / 2 * s), fill=255)
        m.line([(cx - 120 * s, cy + 90 * s), (cx - 235 * s, cy - 40 * s)], fill=255, width=int(76 * s))
        m.rectangle([cx - 110 * s, cy + 150 * s, cx + 110 * s, 1920], fill=255)
    WD.shadow(img, sil, (10, 22), 24, 110)
    d = ImageDraw.Draw(img)
    d.rectangle([cx - 112 * s, cy + 150 * s, cx + 112 * s, cy + 420 * s], fill=SKIN)
    d.rectangle([cx - 132 * s, cy + 300 * s, cx + 132 * s, 1920], fill=SLEEVE)
    d.line([(cx - 120 * s, cy + 90 * s), (cx - 235 * s, cy - 40 * s)], fill=SKIN, width=int(76 * s))
    d.ellipse([cx - 273 * s, cy - 78 * s, cx - 197 * s, cy - 2 * s], fill=SKIN)
    for dx, h, w in fingers:
        d.rounded_rectangle([cx + (dx - w / 2) * s, cy - (130 + h) * s, cx + (dx + w / 2) * s, cy - 60 * s], radius=int(w / 2 * s), fill=SKIN)
        for k in (0.33, 0.62):  # knuckle creases
            yy = cy - 130 * s - h * s * (1 - k)
            d.line([(cx + (dx - w * 0.28) * s, yy), (cx + (dx + w * 0.28) * s, yy)], fill=SKIN_D, width=max(2, int(4 * s)))
    d.rounded_rectangle([cx - 150 * s, cy - 130 * s, cx + 150 * s, cy + 170 * s], radius=int(90 * s), fill=SKIN)
    d.arc([cx - 120 * s, cy - 60 * s, cx + 160 * s, cy + 200 * s], 200, 290, fill=SKIN_D, width=max(2, int(5 * s)))
    d.arc([cx - 130 * s, cy - 120 * s, cx + 130 * s, cy + 40 * s], 20, 160, fill=SKIN_D, width=max(2, int(5 * s)))
    return d

def swab(img, d, x, y, s=1.0, specks=0, a=1.0):
    """Swab on a wand: white pad (x, y = pad centre) with a grey holder and handle going up-right."""
    WD.shadow(img, lambda m: m.rounded_rectangle([x - 95 * s, y - 60 * s, x + 95 * s, y + 60 * s], radius=int(18 * s), fill=255), (8, 14), 14, 100)
    d = ImageDraw.Draw(img)
    d.line([(x + 40 * s, y - 60 * s), (x + 190 * s, y - 250 * s)], fill=(120, 130, 146), width=int(30 * s))
    d.rounded_rectangle([x - 100 * s, y - 72 * s, x + 100 * s, y - 44 * s], radius=int(10 * s), fill=(150, 160, 176))
    d.rounded_rectangle([x - 95 * s, y - 56 * s, x + 95 * s, y + 60 * s], radius=int(18 * s), fill=(250, 250, 252), outline=(205, 212, 222), width=max(2, int(4 * s)))
    for k in range(4):
        yy = y - 30 * s + k * 24 * s
        d.line([(x - 75 * s, yy), (x + 75 * s, yy)], fill=(228, 232, 238), width=max(1, int(3 * s)))
    rnd = random.Random(5)
    for k in range(specks):
        sx, sy = x + rnd.uniform(-70, 70) * s, y + rnd.uniform(-35, 45) * s
        speck(img, sx, sy, 7 * s, glow=(k == 0))
    return ImageDraw.Draw(img)

def speck(img, x, y, r=8, glow=True, col=None):
    if glow:
        WD.glow(img, x, y, r * 3.2, Y, 120)
    d = ImageDraw.Draw(img)
    d.ellipse([x - r, y - r, x + r, y + r], fill=col or Y)

def mol(d, x, y, r, col, charged=0.0):
    d.ellipse([x - r, y - r, x + r, y + r], fill=col)
    if charged > 0.02:
        rr = r + 8 + 4 * charged
        d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=WD.lerp(STEEL, WHITE, charged), width=4)

def badge(d, xy, s, e, a=1.0):
    return WD.chip(d, xy, s, e, fill=WD.lerp(e["bottom"], (8, 30, 64), a), fg=MUTED, role="badge", a=a)

def tube(d, x0, x1, yc, h, gate=0.0, e=None):
    """Drift tube cutaway: outer wall, ring electrodes, a gate at the left, the detector plate on the right."""
    d.rounded_rectangle([x0 - 16, yc - h / 2 - 16, x1 + 16, yc + h / 2 + 16], radius=28, fill=STEEL, outline=STEEL_L, width=5)
    d.rectangle([x0, yc - h / 2, x1, yc + h / 2], fill=(10, 36, 74))
    for x in range(int(x0 + 60), int(x1 - 30), 70):
        d.rectangle([x, yc - h / 2 - 10, x + 10, yc - h / 2 + 8], fill=STEEL_L)
        d.rectangle([x, yc + h / 2 - 8, x + 10, yc + h / 2 + 10], fill=STEEL_L)
    # gate (shutter): closed = vertical bars, opening = bars slide apart
    g = 36 * gate
    d.rectangle([x0 + 20, yc - h / 2, x0 + 30, yc - g], fill=INK)
    d.rectangle([x0 + 20, yc + g, x0 + 30, yc + h / 2], fill=INK)
    d.rectangle([x1 - 18, yc - h / 2 + 10, x1 - 4, yc + h / 2 - 10], fill=Y)

def headwind(d, x0, x1, yc, h, t):
    for row in (-0.30, 0.0, 0.30):
        for k in range(9):
            x = x1 - ((t * 260 + k * 100 + row * 77) % (x1 - x0 - 60)) - 30
            yy = yc + row * h
            d.line([(x, yy), (x + 34, yy)], fill=(70, 110, 170), width=4)

def trace_axes(d, box, e, ms_max=15, lab=True):
    x0, y0, x1, y1 = box
    d.rounded_rectangle([x0 - 30, y0 - 30, x1 + 30, y1 + 70], radius=26, fill=(8, 34, 72), outline=STEEL_L, width=3)
    d.line([(x0, y1), (x1, y1)], fill=MUTED, width=4)
    d.line([(x0, y0), (x0, y1)], fill=MUTED, width=4)
    if lab:
        WD.T(d, (x0, y1 + 36), "0 ms", "small", MUTED, "mm", size=30)
        WD.T(d, (x1, y1 + 36), f"{ms_max} ms", "small", MUTED, "mm", size=30)

def peak_curve(x0, x1, y1, height, peaks, upto=1.0):
    pts = []
    n = 160
    for k in range(int(n * upto) + 1):
        u = k / n
        v = sum(hh * math.exp(-((u - pu) / 0.022) ** 2) for pu, hh, _ in peaks)
        pts.append((x0 + (x1 - x0) * u, y1 - 6 - v * height))
    return pts

# ---------------- scenes ----------------
def sw_hook(img, d, t, p, ctx):
    """Frame 0: an open hand with a swab already wiping across the palm; specks transfer to the pad."""
    e = ctx["env"]
    cx, cy = 540, 1000
    d = hand(img, d, cx, cy, 1.0)
    wipe = 0.5 + 0.5 * math.sin(t * 3.2 - 1.2)
    sx = cx - 120 + 240 * wipe
    n = min(5, int(1 + t * 1.4))
    rnd = random.Random(2)
    for k in range(5):  # specks still on the palm (fade once the pad has passed)
        px, py = cx + rnd.uniform(-120, 120), cy + rnd.uniform(-40, 120)
        if k >= n:
            speck(img, px, py, 7, glow=False)
    d = swab(img, d, sx, cy + 30, 1.05, specks=n)
    badge(d, (540, 560), "AIRPORT CHECKPOINT", e)
    a = WD.ease_out(WD.seg(t, 0.3, 0.7))
    WD.label(d, "swab", (sx - 90, cy + 70), (230, 1180), e, role="label", color=INK, a=a)
    return img

def sw_trace(img, d, t, p, ctx):
    """Magnified fingertip: ridges + yellow residue specks; the swab sweeps through and lifts them."""
    e = ctx["env"]
    cx, cy, r = 540, 900, 300
    WD.shadow(img, lambda m: m.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255), (0, 18), 26, 130)
    d = ImageDraw.Draw(img)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SKIN)
    for k in range(1, 15):  # fingerprint ridges
        rr = k * 26
        d.arc([cx - rr * 1.1, cy - rr + 60, cx + rr * 1.1, cy + rr + 60], 180, 360, fill=SKIN_D, width=6)
        d.arc([cx - rr * 1.1, cy - rr + 60, cx + rr * 1.1, cy + rr + 60], 0, 180, fill=WD.lerp(SKIN, SKIN_D, 0.6), width=5)
    # mask outside the lens
    m = Image.new("L", img.size, 0); ImageDraw.Draw(m).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    bg = WD.background(ctx["spec"].get("environment"))
    img.paste(bg, (0, 0), Image.eval(m, lambda v: 255 - v))
    d = ImageDraw.Draw(img)
    d.ellipse([cx - r - 14, cy - r - 14, cx + r + 14, cy + r + 14], outline=INK, width=16)
    d.line([(cx + r * 0.72, cy + r * 0.72), (cx + r * 1.05, cy + r * 1.12)], fill=INK, width=34)
    hunt = p.get("hunt_at", 3.5)
    sweep = WD.ease_io(WD.seg(t, hunt - 0.2, hunt + 1.0))
    sx = cx - 420 + 840 * sweep
    rnd = random.Random(9)
    spots = [(cx + rnd.uniform(-200, 200), cy + rnd.uniform(-160, 200)) for _ in range(9)]
    for k, (x, y) in enumerate(spots):
        lifted = sweep > 0 and x < sx
        if lifted:
            continue
        a = WD.ease_out(WD.seg(t, 0.4 + k * 0.08, 0.7 + k * 0.08))
        if a > 0.02:
            speck(img, x, y, 11 * a, glow=(k == 0))
    d = ImageDraw.Draw(img)
    if 0 < sweep < 1:
        d = swab(img, d, sx, cy + 20, 1.5, specks=sum(1 for x, _ in spots if x < sx))
    a = WD.ease_out(WD.seg(t, 0.8, 1.2))
    if a > 0.02:
        WD.label(d, "invisible traces", (spots[0][0], spots[0][1]), (600, 1250), e, role="label", color=Y, a=a, maxw=320)
    badge(d, (540, 540), "MAGNIFIED · ILLUSTRATION", e)
    return img

def machine_shell(img, d, e, x0=110, x1=970, y0=620, y1=1240):
    WD.shadow(img, lambda m: m.rounded_rectangle([x0, y0, x1, y1], radius=40, fill=255), (0, 20), 24, 130)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x0, y0, x1, y1], radius=40, fill=(14, 44, 90), outline=STEEL_L, width=6)
    return d

def sw_heat(img, d, t, p, ctx):
    """Cutaway: the swab drops into the slot, the desorber glows, the speck lifts off as vapor to the right."""
    e = ctx["env"]
    d = machine_shell(img, d, e)
    slide = p.get("slide_at", 0.8); heat = p.get("heat_at", 2.5); vap = p.get("vapor_at", 4.5)
    # desorber block (left) and outlet pipe (right)
    hx0, hx1, hy0, hy1 = 170, 560, 880, 1170
    h = WD.ease_out(WD.seg(t, heat, heat + 1.4))
    if h > 0.02:
        WD.glow(img, (hx0 + hx1) / 2, 1100, 260, HOT, int(90 * h))
        d = ImageDraw.Draw(img)
    d.rounded_rectangle([hx0, hy0, hx1, hy1], radius=26, outline=STEEL_L, width=5, fill=(10, 36, 74))
    for k in range(7):  # heater coils
        x = hx0 + 40 + k * 52
        d.arc([x - 22, 1110, x + 22, 1150], 180, 360, fill=WD.lerp(STEEL_L, HOT, h), width=9)
    d.rectangle([560, 960, 920, 1010], fill=(10, 36, 74), outline=STEEL_L, width=4)
    d.rectangle([300, 600, 430, 640], fill=(4, 18, 40))  # slot
    # swab goes in from the top
    u = WD.ease_io(WD.seg(t, 0, slide + 0.4))
    sy = 680 + (1000 - 680) * u
    sp = WD.ease_out(WD.seg(t, vap, vap + 2.2))
    d = swab(img, d, 365, sy, 1.0, specks=0)
    # the tracked speck: on the pad, then rises and drifts out as vapor
    if sp < 0.05:
        speck(img, 365, sy + 10, 9)
    else:
        rnd = random.Random(4)
        for k in range(10):
            uu = WD.clamp(sp * 1.25 - k * 0.04)
            x, y = WD.path_at([(365, 990), (470, 930), (620, 985), (900, 985)], uu)
            y += 10 * math.sin(t * 6 + k)
            WD.glow(img, x, y, 22, Y, 50)
            d = ImageDraw.Draw(img)
            d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=Y)
    d = ImageDraw.Draw(img)
    WD.T(d, (365, 840), "HEATER", "badge", MUTED, "mm")
    a = WD.ease_out(WD.seg(t, heat, heat + 0.4))
    if a > 0.02:
        lvl = WD.ease_out(WD.seg(t, heat, heat + 1.4))
        d.rounded_rectangle([600, 680, 920, 900], radius=24, fill=(8, 30, 64), outline=WD.lerp(STEEL_L, Y, a), width=4)
        WD.T(d, (760, 728), "DESORBER", "badge", MUTED, "mm")
        d.rounded_rectangle([640, 790, 880, 830], radius=20, outline=STEEL_L, width=4)
        d.rounded_rectangle([646, 796, 646 + 228 * lvl, 824], radius=14, fill=WD.lerp(HOT, Y, lvl))
        WD.T(d, (760, 866), "heating", "small", Y, "mm", size=30)
    va = WD.ease_out(WD.seg(t, vap, vap + 0.4))
    if va > 0.02:
        WD.chip(d, (740, 1100), "vapor", e, fill=Y, fg=NAVY, a=va, role="label")
    badge(d, (540, 1268), "TRACE DETECTOR · SIMPLIFIED", e)
    return img

def sw_charge(img, d, t, p, ctx):
    """Vapor molecules pass a small ion source and come out charged (a ring = charge)."""
    e = ctx["env"]
    d = machine_shell(img, d, e, y0=660, y1=1220)
    d.rectangle([110, 900, 970, 1000], fill=(10, 36, 74))
    src_x = 520
    d.rounded_rectangle([src_x - 90, 740, src_x + 90, 880], radius=20, fill=(30, 70, 130), outline=STEEL_L, width=4)
    # small trefoil
    cx, cy = src_x, 810
    for k in range(3):
        a0 = -90 + k * 120
        d.pieslice([cx - 46, cy - 46, cx + 46, cy + 46], a0 - 30, a0 + 30, fill=Y)
    d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=(30, 70, 130)); d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=Y)
    ch = p.get("charge_at", 2.0)
    glowa = 0.5 + 0.5 * math.sin(t * 5)
    for k in range(4):
        d.line([(src_x - 50 + k * 34, 885), (src_x - 50 + k * 34, 900)], fill=WD.lerp(STEEL_L, Y, glowa), width=4)
    rnd = random.Random(12)
    for k in range(11):
        x = 140 + ((t * 120 + k * 80) % 820)
        y = 950 + 26 * math.sin(k * 1.7 + t * 2)
        tracked = (k == 3)
        charged = WD.ease_out(WD.seg(x, src_x - 20, src_x + 40)) * WD.ease_out(WD.seg(t, ch - 0.6, ch))
        col = Y if tracked else (CYAN if k % 3 == 0 else (200, 210, 230))
        if tracked:
            WD.glow(img, x, y, 30, Y, 60); d = ImageDraw.Draw(img)
        mol(d, x, y, 13 if tracked else 10, col, charged)
    WD.T(d, (540, 705), "ion source (usually nickel-63)", "small", INK, "mm", maxw=800)
    a = WD.ease_out(WD.seg(t, ch, ch + 0.4))
    if a > 0.02:
        WD.chip(d, (740, 1090), "charged", e, fill=Y, fg=NAVY, a=a, role="label")
    badge(d, (540, 560), "STEP 2 · GIVE IT A CHARGE", e)
    return img

ION_SPEED = [(0.50, CYAN), (0.34, Y), (0.23, (220, 226, 240))]   # fraction of the tube per second (illustrative)

def sw_race(img, d, t, p, ctx):
    """The drift tube: the gate opens, three kinds of ions race to the detector against a gas headwind."""
    e = ctx["env"]
    x0, x1, yc, h = 140, 930, 960, 210
    go = p.get("race_at", 0.6)
    gate = WD.ease_out(WD.seg(t, go, go + 0.3))
    tube(d, x0, x1, yc, h, gate, e)
    headwind(d, x0 + 40, x1 - 20, yc, h, t)
    tt = max(0.0, t - go - 0.3)
    for k, (v, col) in enumerate(ION_SPEED):
        u = WD.clamp(tt * v * 0.62)
        x = x0 + 50 + (x1 - x0 - 90) * u
        y = yc - 50 + k * 50
        if col == Y:
            WD.glow(img, x, y, 36, Y, 70); d = ImageDraw.Draw(img)
        mol(d, x, y, 16 if col == Y else 13, col, 1.0)
    # field arrow above, gas arrow below
    d.line([(260, 800), (820, 800)], fill=INK, width=6)
    d.polygon([(820, 784), (850, 800), (820, 816)], fill=INK)
    WD.T(d, (540, 760), "electric field pulls →", "small", INK, "mm")
    a = WD.ease_out(WD.seg(t, p.get("wind_at", 2.5), p.get("wind_at", 2.5) + 0.4))
    d.line([(290, 1120), (820, 1120)], fill=WD.lerp(e["bottom"], (110, 160, 220), a), width=6)
    d.polygon([(290, 1104), (260, 1120), (290, 1136)], fill=WD.lerp(e["bottom"], (110, 160, 220), a))
    if a > 0.02:
        WD.T(d, (540, 1165), "← gas pushes back", "small", WD.lerp(e["bottom"], MUTED, a), "mm")
    WD.T(d, (x1 - 10, 1210), "detector", "small", Y, "rm", size=30)
    badge(d, (540, 560), "STEP 3 · THE DRIFT TUBE", e)
    return img

PEAKS = [(0.27, 0.55, CYAN), (0.47, 1.0, Y), (0.73, 0.70, (220, 226, 240))]   # illustrative arrival times (fraction of 15 ms)

def sw_clock(img, d, t, p, ctx):
    """Arrival-time trace: a cursor sweeps 0-15 ms and peaks appear as each kind of ion lands."""
    e = ctx["env"]
    box = (190, 700, 870, 1110)
    trace_axes(d, box, e)
    x0, y0, x1, y1 = box
    sweep = WD.ease_io(WD.seg(t, 0.2, max(1.6, p.get("finger_at", 2.6) - 0.2)))
    pts = peak_curve(x0, x1, y1, 330, PEAKS, sweep)
    if len(pts) > 1:
        d.line(pts, fill=INK, width=6, joint="curve")
    for pu, hh, col in PEAKS:
        if sweep >= pu:
            px = x0 + (x1 - x0) * pu
            d.ellipse([px - 13, y1 - 6 - hh * 330 - 13, px + 13, y1 - 6 - hh * 330 + 13], fill=col)
    cxp = x0 + (x1 - x0) * sweep
    d.line([(cxp, y0), (cxp, y1)], fill=WD.lerp(e["bottom"], Y, 0.6), width=3)
    WD.T(d, (540, 1236), "drift time · commonly under 15 ms", "small", MUTED, "mm")
    fa = WD.ease_out(WD.seg(t, p.get("finger_at", 2.6), p.get("finger_at", 2.6) + 0.4))
    if fa > 0.02:
        px = x0 + (x1 - x0) * 0.47
        d.line([(px, y1 - 340), (px, y0 - 6)], fill=Y, width=4)
        WD.chip(d, (px, y0 - 40), "arrival time = fingerprint", e, fill=Y, fg=NAVY, a=fa, role="label")
    badge(d, (540, 560), "ILLUSTRATIVE PEAKS", e)
    return img

def mini_trace(img, d, box, e, peak_u, lib_us, state, a=1.0):
    x0, y0, x1, y1 = box
    d.rounded_rectangle([x0 - 24, y0 - 24, x1 + 24, y1 + 24], radius=24, fill=(8, 34, 72), outline=STEEL_L, width=3)
    for lu in lib_us:  # library reference lines
        lx = x0 + (x1 - x0) * lu
        for yy in range(int(y0), int(y1), 22):
            d.line([(lx, yy), (lx, yy + 11)], fill=(110, 150, 210), width=4)
    pts = peak_curve(x0, x1, y1, (y1 - y0) * 0.85, [(peak_u, 1.0, Y)])
    d.line(pts, fill=Y, width=6, joint="curve")
    lx, ly = (x0 + x1) / 2, y1 + 92
    if state:
        col = RED if state == "alarm" else GREEN
        WD.glow(img, lx, ly, 70, col, int(110 * a)); d = ImageDraw.Draw(img)
        d.ellipse([lx - 34, ly - 34, lx + 34, ly + 34], fill=WD.lerp(STEEL, col, a))
    else:
        d.ellipse([lx - 34, ly - 34, lx + 34, ly + 34], fill=STEEL)
    return ImageDraw.Draw(img)

def sw_library(img, d, t, p, ctx):
    """Library check: left, the peak sits on a library line -> alarm; right, it sits on none -> no alarm."""
    e = ctx["env"]
    al = p.get("alarm_at", 1.2); no = p.get("nomatch_at", 3.0)
    lib = [0.30, 0.55, 0.80]
    a1 = WD.ease_out(WD.seg(t, al, al + 0.4)); a2 = WD.ease_out(WD.seg(t, no, no + 0.4))
    d = mini_trace(img, d, (150, 720, 510, 1010), e, 0.55, lib, "alarm" if a1 > 0.02 else None, a1)
    WD.T(d, (330, 1190), "MATCH", "label", INK if a1 > 0.02 else MUTED, "mm", size=44)
    if a1 > 0.02:
        WD.T(d, (330, 1240), "alarm", "small", RED, "mm")
    pa = WD.ease_out(WD.seg(t, no - 0.6, no))
    if pa > 0.02:
        d = mini_trace(img, d, (590, 720, 930 - 20, 1010), e, 0.43, lib, "clear" if a2 > 0.02 else None, a2)
        WD.T(d, (740, 1190), "NO MATCH", "label", INK if a2 > 0.02 else MUTED, "mm", size=44, maxw=300)
        if a2 > 0.02:
            WD.T(d, (740, 1240), "no alarm", "small", GREEN, "mm")
    WD.T(d, (540, 650), "- - -  library of explosives", "small", (150, 185, 235), "mm")
    badge(d, (540, 560), "STEP 4 · LIBRARY CHECK (SIMPLIFIED)", e)
    return img

def sw_payoff(img, d, t, p, ctx):
    """Back to the hand and swab; a small drift tube beside it with the yellow ion winning the race."""
    e = ctx["env"]
    d = hand(img, d, 330, 1000, 0.8)
    d = swab(img, d, 360, 1010, 0.8, specks=3)
    x0, x1, yc, h = 600, 920, 930, 110
    tube(d, x0, x1, yc, h, 1.0, e)
    u = (t * 0.45) % 1.0
    x = x0 + 30 + (x1 - x0 - 60) * u
    WD.glow(img, x, yc, 26, Y, 70); d = ImageDraw.Draw(img)
    mol(d, x, yc, 12, Y, 1.0)
    a = WD.ease_out(WD.seg(t, 0.2, 0.6))
    WD.chip(d, (540, 660), "a race timed in milliseconds", e, fill=Y, fg=NAVY, a=a, role="label")
    z = 1.0 + 0.05 * WD.ease_io(WD.seg(t, 0, p["_dur"]))
    return WD.zoom(img, z, 540, 960)

# ---------------- cover ----------------
def sw_cover(img, d, t, p, ctx):
    """Living cover: big hand mid-wipe with glowing specks + a magnifier on the residue (scene 1-2 as art)."""
    e = ctx["env"]
    cx, cy = 770, 1190
    d = hand(img, d, cx, cy, 1.45)
    d = swab(img, d, cx + 50, cy + 70, 1.3, specks=4)
    rnd = random.Random(3)
    for k in range(4):
        speck(img, cx - 150 + rnd.uniform(-40, 40), cy + rnd.uniform(-60, 120), 10, glow=True)
    lx, ly, r = 300, 900, 175
    WD.shadow(img, lambda m: m.ellipse([lx - r, ly - r, lx + r, ly + r], fill=255), (0, 14), 20, 120)
    d = ImageDraw.Draw(img)
    d.ellipse([lx - r, ly - r, lx + r, ly + r], fill=SKIN)
    m = Image.new("L", img.size, 0); ImageDraw.Draw(m).ellipse([lx - r, ly - r, lx + r, ly + r], fill=255)
    lay = img.copy(); ld = ImageDraw.Draw(lay)
    for k in range(1, 12):
        rr = k * 24
        ld.arc([lx - rr * 1.1, ly - rr + 40, lx + rr * 1.1, ly + rr + 40], 180, 360, fill=SKIN_D, width=6)
    img.paste(lay, (0, 0), m)
    for (sx, sy) in ((lx - 60, ly - 30), (lx + 50, ly + 20), (lx - 5, ly + 80), (lx + 70, ly - 80)):
        speck(img, sx, sy, 14, glow=True)
    d = ImageDraw.Draw(img)
    d.ellipse([lx - r - 12, ly - r - 12, lx + r + 12, ly + r + 12], outline=INK, width=14)
    d.line([(lx + r * 0.72, ly + r * 0.72), (lx + r * 1.1, ly + r * 1.12)], fill=INK, width=30)
    return img
