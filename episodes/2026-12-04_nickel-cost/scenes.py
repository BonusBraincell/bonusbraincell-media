"""Custom scenes · Why does a nickel cost 13 cents to make? (v4 demo, FOLLOW THE JOURNEY + DATA STORY)

One nickel rides a production line left to right. A cost meter above it climbs with each stage, using the Mint's
FY2025 unit-cost breakdown (cost of goods sold 10.97¢, SG&A 2.24¢, distribution 0.10¢ = 13.31¢). Then the coin is
sold to the Federal Reserve at face value (5¢), and the gap is scaled up to the year's 615 million nickels.
Environment: mint_floor. Yellow = the coin being followed and the running cost.
"""
import math
from PIL import Image, ImageDraw
import world as WD
import design as DZ

SILVER = (198, 204, 211); SILVER_D = (132, 141, 152); SILVER_L = (232, 236, 240)
COPPER = (200, 121, 74); COPPER_L = (232, 162, 115); RED = (217, 74, 61)
INK = (244, 246, 251); MUTED = (169, 182, 200); STEEL = (36, 56, 79); STEEL_L = (58, 81, 112)
Y = DZ.C["track"]; NAVY = DZ.C["bg"]
BELT_Y = 1110

COSTS = [("Metal + making", 10.97, COPPER), ("Admin + overhead", 2.24, (143, 163, 184)), ("Shipping", 0.10, Y)]

def coin(img, d, cx, cy, r, sy=1.0, face=True, a=1.0, glow=False):
    """A cupronickel 5-cent coin (no portrait: brand rule, no real people). sy squashes it into perspective."""
    if glow:
        WD.glow(img, cx, cy, r * 1.25, Y, 55)
        d = ImageDraw.Draw(img)
    th = max(6, r * 0.12) * (1 - sy) + 4
    ry = r * max(0.08, sy)
    d.ellipse([cx - r, cy - ry + th, cx + r, cy + ry + th], fill=SILVER_D)          # edge
    d.rectangle([cx - r, cy, cx + r, cy + th], fill=SILVER_D)
    d.ellipse([cx - r, cy - ry, cx + r, cy + ry], fill=SILVER, outline=SILVER_D, width=max(2, int(r * 0.03)))
    d.ellipse([cx - r * 0.86, cy - ry * 0.86, cx + r * 0.86, cy + ry * 0.86], outline=SILVER_L, width=max(2, int(r * 0.025)))
    if face and sy > 0.55:
        f = DZ.F(int(r * 0.78 * 1.0), "Black")
        txt = "5¢"
        tw = d.textlength(txt, font=f)
        lay = Image.new("RGBA", (int(tw) + 20, int(r * 1.1)), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        ld.text((10 + 3, int(r * 0.55) + 3), txt, font=f, fill=SILVER_D + (255,), anchor="lm")
        ld.text((10, int(r * 0.55)), txt, font=f, fill=SILVER_L + (255,), anchor="lm")
        lay = lay.resize((lay.width, max(1, int(lay.height * sy))))
        img.paste(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2 - r * 0.08 * sy)), lay)
        small = DZ.F(max(14, int(r * 0.13)), "ExtraBold")
        d.text((cx, cy + ry * 0.55), "FIVE CENTS", font=small, fill=SILVER_D, anchor="mm")

def belt(img, d, t, speed=60, y=BELT_Y, x0=-20, x1=1100):
    WD.shadow(img, lambda m: m.rectangle([x0, y + 10, x1, y + 70], fill=255), (0, 22), 18, 120)
    d.rectangle([x0, y, x1, y + 56], fill=(30, 44, 62))
    d.rectangle([x0, y, x1, y + 8], fill=(74, 96, 124))
    off = (t * speed) % 60
    for x in range(int(x0 - 60 + off), x1, 60):
        d.line([(x, y + 14), (x + 26, y + 50)], fill=(46, 64, 88), width=6)
    for x in range(x0 + 40, x1, 180):  # rollers / legs
        d.rectangle([x, y + 56, x + 16, y + 190], fill=(24, 36, 52))

def meter(img, d, value, a=1.0, label="COST SO FAR", note=None, flash=0.0):
    """Running cost meter (y 540-680), the episode's through-line."""
    if a <= 0.02:
        return
    box = [190, 520, 890, 690]
    WD.shadow(img, lambda m: m.rounded_rectangle(box, radius=30, fill=255), (0, 16), 20, 140)
    d.rounded_rectangle(box, radius=30, fill=WD.lerp((14, 24, 38), (40, 52, 30), flash), outline=WD.lerp(STEEL_L, Y, 0.35 + 0.65 * flash), width=4)
    WD.T(d, (230, 568), label, "badge", MUTED, "lm")
    WD.T(d, (850, 608), f"{value:.2f}¢", "value", Y, "rm", size=96)
    if note:
        WD.T(d, (230, 640), note, "small", INK, "lm", maxw=360, size=30)

def tag(d, cx, cy, top, value, col, fg=NAVY, w=330, a=1.0):
    box = [cx - w / 2, cy - 92, cx + w / 2, cy + 92]
    d.rounded_rectangle(box, radius=28, fill=WD.lerp((11, 20, 34), col, a))
    WD.T(d, (cx, cy - 40), top, "badge", WD.lerp((11, 20, 34), fg, a), "mm")
    WD.T(d, (cx, cy + 22), value, "value", WD.lerp((11, 20, 34), fg, a), "mm", size=84)

# ---------------- scenes ----------------
def n_hook(img, d, t, p, ctx):
    """Worth 5¢ vs cost 13.31¢: the coin and two tags, fully drawn from frame 0."""
    spin = 0.82 + 0.18 * math.cos(t * 1.6)
    coin(img, d, 540, 840, 250, spin, glow=True)
    d = ImageDraw.Draw(img)
    # both tags are on from frame 0 (matches the cover); the cost tag pulses when the narration names it
    ca = p.get("cost_at", 1.5)
    pulse = 0 if ctx.get("cover") else math.sin(math.pi * WD.seg(t, ca, ca + 0.5))
    tag(d, 300, 1185, "WORTH", "5¢", INK)
    tag(d, 780, 1185 - 14 * pulse, "COST TO MAKE", "13.31¢", Y, w=330 + 24 * pulse)
    return img

def n_strip(img, d, t, p, ctx):
    """Metal strip slides in, the press punches a blank and stamps it; meter climbs to 10.97¢."""
    dur = p["_dur"]; punch = p.get("punch_at", dur * 0.55); law = p.get("law_at", dur * 0.25)
    belt(img, d, t, 40)
    # strip of cupronickel
    sx = -700 + 760 * WD.ease_out(WD.seg(t, 0, 1.0))
    d.rectangle([sx, BELT_Y - 60, sx + 640, BELT_Y], fill=(181, 170, 158), outline=SILVER_D, width=3)
    d.rectangle([sx, BELT_Y - 60, sx + 640, BELT_Y - 50], fill=(214, 206, 196))
    # recipe card: 3 parts copper : 1 part nickel (to scale)
    ra = WD.ease_out(WD.seg(t, 0.3, 0.9)) * (1 - WD.ease_out(WD.seg(t, punch - 0.9, punch - 0.4)))
    bx, by = 150, 740
    if ra > 0.02:
        d.rounded_rectangle([bx, by, bx + 780, by + 170], radius=26, fill=WD.lerp((14, 24, 38), (16, 28, 44), ra), outline=WD.lerp((14, 24, 38), STEEL_L, ra), width=3)
    if ra > 0.02:
        WD.T(d, (bx + 30, by + 40), "THE RECIPE", "badge", WD.lerp((14, 24, 38), MUTED, ra), "lm")
    if ra > 0.02:
        d.rounded_rectangle([bx + 30, by + 70, bx + 30 + 540 * ra, by + 145], radius=12, fill=COPPER)
        d.rounded_rectangle([bx + 570, by + 70, bx + 570 + 180 * ra, by + 145], radius=12, fill=SILVER)
    if ra > 0.6:
        WD.T(d, (bx + 300, by + 108), "75% copper", "label", NAVY, "mm", size=40)
        WD.T(d, (bx + 660, by + 108), "25% nickel", "small", NAVY, "mm", size=32)
    la = WD.ease_out(WD.seg(t, law, law + 0.4))
    la *= (1 - WD.ease_out(WD.seg(t, punch - 0.9, punch - 0.4)))
    if la > 0.02:
        WD.chip(d, (540, 940), "SET BY FEDERAL LAW · 31 U.S.C. § 5112", WD.env("mint_floor"), fill=Y, a=la)
    # press
    drop = WD.seg(t, punch - 0.25, punch) * (1 - WD.seg(t, punch + 0.1, punch + 0.5))
    px, py = 640, BELT_Y - 46 - 250 + 210 * drop
    pa_ = WD.ease_out(WD.seg(t, punch - 0.7, punch - 0.3))
    if pa_ <= 0.02:
        v = WD.counter(t, 0.4, max(1.0, punch + 0.4), 0.0, 10.97)
        meter(img, d, v, note="metal + making")
        WD.T(d, (540, 1270), "Source: U.S. Mint FY2025 unit cost (Treasury OIG audit)", "source", MUTED, "mm")
        return img
    py = py - 300 * (1 - pa_)
    if py > 722:
        d.rectangle([px - 80, 720, px + 80, py], fill=(52, 70, 95))   # ram
    d.rounded_rectangle([px - 190, py - 40, px + 190, py + 20], radius=12, fill=(70, 92, 122))
    d.rectangle([px - 95, py + 20, px + 95, py + 46], fill=SILVER_D)
    WD.T(d, (px - 210, py - 10), "press", "small", MUTED, "rm", size=32)
    # blank / coin after punch
    if t > punch:
        u = WD.ease_out(WD.seg(t, punch, punch + 0.7))
        cx = px + 200 * u; cy = BELT_Y - 40 - 120 * math.sin(math.pi * u)
        coin(img, d, cx, cy, 100, 0.45 + 0.4 * u, face=t > punch + 0.5, glow=True)
        d = ImageDraw.Draw(img)
    v = WD.counter(t, 0.4, max(1.0, punch + 0.4), 0.0, 10.97)
    meter(img, d, v, note="metal + making", flash=WD.seg(t, punch + 0.3, punch + 0.4) * (1 - WD.seg(t, punch + 0.6, punch + 1.0)))
    WD.T(d, (540, 1270), "Source: U.S. Mint FY2025 unit cost (Treasury OIG audit)", "source", MUTED, "mm")
    return img

def _stack(d, y, parts, a=1.0, scale=55.0, x0=150, face_line=True):
    """Receipt bar drawn to scale: 1 cent = scale px."""
    x = x0
    for name, v, col in parts:
        w = v * scale
        d.rectangle([x, y, x + w, y + 56], fill=col)
        x += w
    if face_line:
        fx = x0 + 5 * scale
        d.line([(fx, y - 30), (fx, y + 86)], fill=INK, width=5)
        WD.T(d, (fx, y + 112), "face value 5¢", "small", INK, "mm", size=30)
    return x

def n_overhead(img, d, t, p, ctx):
    """Coin moves on; admin overhead adds 2.24¢; the to-scale receipt bar appears under the line."""
    belt(img, d, t, 60)
    u = WD.ease_io(WD.seg(t, 0.2, p["_dur"] * 0.7))
    cx = 230 + 250 * u
    # admin block: an office desk with paper stacks
    ox = 740
    d.rounded_rectangle([ox - 170, 780, ox + 170, BELT_Y - 10], radius=20, fill=(30, 46, 66), outline=STEEL_L, width=3)
    for k in range(3):
        d.rectangle([ox - 130 + k * 90, 830 - k * 20, ox - 60 + k * 90, 950], fill=(210, 214, 220))
        for j in range(5):
            d.line([(ox - 122 + k * 90, 852 - k * 20 + j * 18), (ox - 68 + k * 90, 852 - k * 20 + j * 18)], fill=(150, 160, 172), width=4)
    WD.T(d, (ox, 1010), "admin + overhead", "label", INK, "mm", size=38)
    coin(img, d, cx, BELT_Y - 48, 100, 0.5, glow=True)
    d = ImageDraw.Draw(img)
    add = WD.seg(t, p.get("add_at", 1.0), p.get("add_at", 1.0) + 0.8)
    meter(img, d, round(10.97 + 2.24 * (1.0 if add >= 1 else WD.ease_out(add)), 2), note="+ 2.24¢ overhead")
    return img

def n_ship(img, d, t, p, ctx):
    """Coin drops into a bag, the truck leaves for the Federal Reserve: +0.10¢ = 13.31¢. Receipt bar to scale."""
    dur = p["_dur"]; tot = p.get("total_at", dur * 0.55)
    # Federal Reserve building (right)
    bx = 770
    d.polygon([(bx - 190, 960), (bx, 890), (bx + 190, 960)], fill=(52, 70, 95))
    d.rectangle([bx - 175, 960, bx + 175, 1090], fill=(44, 62, 86))
    for k in range(6):
        d.rectangle([bx - 150 + k * 56, 980, bx - 126 + k * 56, 1080], fill=(150, 165, 186))
    WD.T(d, (bx, 1130), "FEDERAL RESERVE", "small", INK, "mm", size=32)
    # truck travelling
    u = WD.ease_io(WD.seg(t, 0.3, tot))
    tx = 170 + 330 * u
    d.rounded_rectangle([tx - 110, 960, tx + 60, 1060], radius=12, fill=(214, 220, 228))
    d.rounded_rectangle([tx + 60, 990, tx + 130, 1060], radius=10, fill=(170, 182, 198))
    for wx in (tx - 70, tx + 90):
        d.ellipse([wx - 22, 1046, wx + 22, 1090], fill=(20, 28, 40))
    coin(img, d, tx - 25, 1010, 34, 0.9, face=False, glow=True)
    d = ImageDraw.Draw(img)
    v = 13.21 + 0.10 * WD.seg(t, tot - 0.3, tot)
    meter(img, d, v, label="TOTAL COST" if t >= tot else "COST SO FAR", note="+ 0.10¢ shipping" if t < tot else "per nickel, FY2025",
          flash=WD.seg(t, tot, tot + 0.1) * (1 - WD.seg(t, tot + 0.3, tot + 0.9)))
    # to-scale receipt: 1¢ = 52 px
    sa = WD.ease_out(WD.seg(t, tot, tot + 0.6))
    if sa > 0:
        parts = [(n, v_ * sa, c) for n, v_, c in COSTS]
        _stack(d, 750, parts, scale=52.0, x0=150)
        WD.T(d, (150, 718), "DRAWN TO SCALE", "badge", MUTED, "lm")
    WD.T(d, (540, 1270), "Source: U.S. Mint FY2025 unit cost (Treasury OIG audit)", "source", MUTED, "mm")
    return img

def n_sale(img, d, t, p, ctx):
    """Sold at face value: the coin goes to the Fed, 5¢ comes back, 8.31¢ is left uncovered."""
    dur = p["_dur"]; back = p.get("back_at", dur * 0.4); gap = p.get("gap_at", dur * 0.7)
    # two parties
    WD.rrect(d, [110, 620, 420, 840], 26, (24, 38, 56), STEEL_L, 3)
    WD.T(d, (265, 690), "U.S. MINT", "label", INK, "mm")
    WD.T(d, (265, 760), "spent 13.31¢", "small", MUTED, "mm", size=32)
    WD.rrect(d, [660, 620, 970, 840], 26, (24, 38, 56), STEEL_L, 3)
    WD.T(d, (815, 690), "FEDERAL", "label", INK, "mm"); WD.T(d, (815, 745), "RESERVE", "label", INK, "mm")
    # coin goes right along the upper lane
    u = WD.ease_io(WD.seg(t, 0.2, back - 0.2))
    coin(img, d, 470 + 180 * u, 700, 40, 0.9, face=False, glow=True)
    d = ImageDraw.Draw(img)
    if t > back - 0.3:
        u2 = WD.ease_io(WD.seg(t, back - 0.3, back + 0.5))
        x = 650 - 220 * u2
        d.rounded_rectangle([x - 60, 776, x + 60, 836], radius=16, fill=INK)
        WD.T(d, (x, 806), "5¢", "label", NAVY, "mm")
    # the money bar: cost 13.31 vs recovered 5
    ga = WD.ease_out(WD.seg(t, back, back + 0.6))
    if ga > 0:
        sc_ = 52.0; x0 = 150; y0 = 960
        d.rectangle([x0, y0, x0 + 13.31 * sc_, y0 + 70], outline=INK, width=3)
        d.rectangle([x0, y0, x0 + 5 * sc_ * ga, y0 + 70], fill=INK)
        WD.T(d, (x0 + 5 * sc_ / 2, y0 + 35), "5¢ back", "small", NAVY, "mm", size=30)
        ra = WD.ease_out(WD.seg(t, gap, gap + 0.5))
        if ra > 0:
            d.rectangle([x0 + 5 * sc_, y0, x0 + 13.31 * sc_, y0 + 70], fill=WD.lerp((14, 24, 38), RED, ra))
            WD.T(d, (x0 + 9.15 * sc_, y0 + 35), "−8.31¢", "label", INK, "mm")
            WD.T(d, (540, 1110), "uncovered on every new nickel", "small", MUTED, "mm", size=32)
    WD.T(d, (540, 1270), "Mint sells circulating coins to the Fed at face value (Treasury OIG)", "source", MUTED, "mm")
    return img

def n_scale(img, d, t, p, ctx):
    """615 million nickels shipped: a pile grows, the year's shortfall counts to $50.9 million."""
    dur = p["_dur"]; per = p.get("per_at", dur * 0.6)
    import random
    rnd = random.Random(3)
    n = int(160 * WD.ease_out(WD.seg(t, 0, dur * 0.6)))
    pts = []
    for k in range(160):  # deterministic pile positions (a mound)
        ang = rnd.uniform(0, math.pi)
        rad = rnd.uniform(0, 1) ** 0.6
        x = 540 + math.cos(ang) * rad * 380
        y = 1150 - math.sin(ang) * rad * 230 * (1 - abs(math.cos(ang)) * 0.5)
        pts.append((x, y))
    for k in range(n):
        x, y = pts[k]
        coin(img, d, x, y, 40, 0.42, face=False)
    d = ImageDraw.Draw(img)
    c = WD.counter(t, 0.1, dur * 0.6, 0, 615)
    WD.T(d, (540, 560), f"{c:,.0f} million", "value", INK, "mm", size=110)
    WD.T(d, (540, 650), "nickels shipped in fiscal 2025", "small", MUTED, "mm")
    l = WD.counter(t, 0.4, dur * 0.6, 0, 50.9)
    WD.T(d, (540, 760), f"−${l:.1f} million", "value", RED if l > 1 else INK, "mm", size=92)
    WD.T(d, (540, 835), "seigniorage: face value minus cost", "small", MUTED, "mm", size=30)
    pa = WD.ease_out(WD.seg(t, per, per + 0.5))
    if pa > 0:
        WD.chip(d, (540, 1235), "≈ −$1.64 for every $1 of nickels", WD.env("mint_floor"), fill=Y, a=pa)
    WD.T(d, (540, 1272 + 0), "", "source", MUTED)
    return img

def n_law(img, d, t, p, ctx):
    """Why not switch metals? Today's solid alloy vs the bill's zinc core with a nickel outer layer (cross-sections)."""
    dur = p["_dur"]; bill = p.get("bill_at", dur * 0.5)
    # penny row: production ended
    pa = 1 - WD.ease_out(WD.seg(t, bill - 0.2, bill + 0.3))
    if pa > 0.02:
        cx, cy = 300, 690
        d.ellipse([cx - 80, cy - 80, cx + 80, cy + 80], fill=WD.lerp((14, 24, 38), COPPER, pa * 0.6))
        d.line([(cx - 100, cy + 100), (cx + 100, cy - 100)], fill=WD.lerp((14, 24, 38), RED, pa), width=12)
        WD.T(d, (440, 660), "Penny: production", "label", WD.lerp((14, 24, 38), INK, pa), "lm")
        WD.T(d, (440, 715), "stopped in 2025", "label", WD.lerp((14, 24, 38), INK, pa), "lm")
    # cross sections
    def section(cx, cy, w, layers, title, a):
        y = cy
        for name, frac, col in layers:
            h = 200 * frac
            d.rectangle([cx - w / 2, y, cx + w / 2, y + h], fill=WD.lerp((14, 24, 38), col, a))
            y += h
        WD.T(d, (cx, cy - 40), title, "badge", WD.lerp((14, 24, 38), INK, a), "mm")
    a1 = WD.ease_out(WD.seg(t, 0.2, 0.7))
    section(300, 900, 300, [("alloy", 1.0, (181, 170, 158))], "TODAY: SOLID ALLOY", a1)
    WD.T(d, (300, 1000), "copper-nickel", "label", WD.lerp((14, 24, 38), NAVY, a1), "mm")
    WD.T(d, (300, 1140), "75% copper · 25% nickel", "small", WD.lerp((14, 24, 38), INK, a1), "mm", size=30)
    a2 = WD.ease_out(WD.seg(t, bill, bill + 0.5))
    if a2 > 0:
        section(740, 900, 300, [("ni", 0.14, SILVER_L), ("zn", 0.72, (150, 158, 170)), ("ni", 0.14, SILVER_L)], "BILL: ZINC CORE", a2)
        WD.T(d, (740, 1000), "zinc", "label", NAVY, "mm")
        d.line([(740, 1086), (740, 1122)], fill=Y, width=4)
        WD.T(d, (740, 1150), "nickel outer layer", "small", Y, "mm")
        WD.T(d, (540, 1270), "Common Cents Act, passed by Congress Sept. 2026: lets Treasury test it", "source", MUTED, "mm")
    return img

def n_receipt(img, d, t, p, ctx):
    """Payoff: the invisible receipt prints line by line."""
    u = WD.ease_out(WD.seg(t, 0.0, 1.2))
    top = 540; h = 120 + 560 * u
    WD.shadow(img, lambda m: m.rectangle([270, top, 810, top + h], fill=255), (0, 18), 22, 150)
    d.rectangle([270, top, 810, top + h], fill=(246, 243, 236))
    for x in range(270, 810, 30):  # torn edge
        d.polygon([(x, top + h), (x + 15, top + h + 14), (x + 30, top + h)], fill=(246, 243, 236))
    mono = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
    from PIL import ImageFont
    f1 = ImageFont.truetype(mono, 38); f2 = ImageFont.truetype(mono, 30)
    rows = [("ONE NICKEL", "", f1), ("", "", f2), ("face value", "5¢", f1), ("cost to make", "13.31¢", f1), ("", "", f2), ("Mint FY2025", "", f2)]
    for k, (l, r, f) in enumerate(rows):
        y = top + 70 + k * 78
        if y > top + h - 40:
            break
        d.text((310, y), l, font=f, fill=NAVY, anchor="lm")
        if r:
            d.text((770, y), r, font=f, fill=(170, 40, 30) if "13" in r else NAVY, anchor="rm")
            DZ.REG["text"].append(dict(box=(310, y - 20, 770, y + 20), role="label", size=38, text=l))
    if u > 0.9:
        d.rectangle([310, top + 70 + 3 * 78 + 28, 770, top + 70 + 3 * 78 + 34], fill=Y)
    return img
