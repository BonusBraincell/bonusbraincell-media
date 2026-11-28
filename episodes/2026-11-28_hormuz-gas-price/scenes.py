"""Custom scenes · Why can one narrow strait move your gas price? (v4, CONSEQUENCE_UNFOLDING / COUNTERFACTUAL_MODEL + DATA_STORY)

A simplified map of the Strait of Hormuz with a tanker lane (yellow tanker = the thing to track) carries the story:
the U.S. barely imports Gulf crude (to-scale 2025 bar) -> ~20 million b/d squeeze through the strait (2024) ->
a labeled what-if: the lane is choked, bypass pipelines carry a sliver (to-scale bar, EIA 2.6 mb/d estimate) ->
Asian buyers bid for barrels elsewhere -> in one global market the price tags rise together, Texas included ->
crude is about half of a gallon's price. Environment: dusk_map. Everything is code-drawn; the map is simplified
(not to scale) and labeled; the market scenes are labeled SIMPLIFIED MODEL / illustration, not a prediction.
"""
import math, random
from PIL import Image, ImageDraw
import world as WD
import design as DZ

Y = DZ.C["track"]; NAVY = DZ.C["bg"]
INK = (244, 246, 251); MUTED = (182, 190, 220); WHITE = (255, 255, 255)
LAND = (84, 96, 140); LAND_D = (64, 74, 112); SEA = (30, 44, 84); SEA_L = (48, 66, 112)
TEAL = (79, 195, 161); ORANGE = (255, 138, 92); BLUE = (127, 178, 255); RED = (235, 87, 87)

# lane through the strait (left = Persian Gulf side, right = Gulf of Oman side), simplified
LANE = [(-80, 1110), (160, 1080), (380, 1030), (560, 972), (700, 950), (860, 900), (1160, 840)]
NARROW = ((590, 905), (575, 1030))   # the two shores at the narrowest point (simplified)

# ---------------- pieces ----------------
def badge(d, xy, s, e, a=1.0):
    return WD.chip(d, xy, s, e, fill=WD.lerp(e["bottom"], (24, 30, 62), a), fg=MUTED, role="badge", a=a)

def strait_map(img, d, e, t=0.0, top=600, bot=1320, label=True):
    """Simplified strait: Iran's coast on top, the Musandam tip of the Arabian Peninsula below, the lane between."""
    WD.shadow(img, lambda m: m.rounded_rectangle([40, top, 1040, bot], radius=40, fill=255), (0, 18), 24, 120)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([40, top, 1040, bot], radius=40, fill=SEA)
    m = Image.new("L", img.size, 0); ImageDraw.Draw(m).rounded_rectangle([40, top, 1040, bot], radius=40, fill=255)
    lay = img.copy(); ld = ImageDraw.Draw(lay)
    # water ripples
    for k in range(14):
        yy = top + 40 + k * 52
        x = (k * 137 + t * 30) % 900 + 60
        ld.arc([x, yy, x + 80, yy + 20], 200, 340, fill=SEA_L, width=3)
    ld.polygon([(0, top), (1080, top), (1080, 790), (900, 820), (760, 850), (650, 860), (590, 905), (520, 900),
                (400, 930), (240, 960), (0, 990)], fill=LAND)
    ld.polygon([(0, bot), (0, 1240), (220, 1220), (420, 1150), (520, 1080), (575, 1030), (640, 1060), (700, 1120),
                (760, 1200), (880, 1150), (1080, 1110), (1080, bot)], fill=LAND)
    for pts in ([(0, 990), (240, 960), (400, 930), (520, 900), (590, 905), (650, 860), (760, 850), (900, 820), (1080, 790)],
                [(0, 1240), (220, 1220), (420, 1150), (520, 1080), (575, 1030), (640, 1060), (700, 1120), (760, 1200), (880, 1150), (1080, 1110)]):
        ld.line(pts, fill=LAND_D, width=6, joint="curve")
    for k in range(len(LANE) - 1):  # dashed lane
        a, b = LANE[k], LANE[k + 1]
        L = math.dist(a, b); n = int(L / 34)
        for j in range(0, n, 2):
            p0 = (a[0] + (b[0] - a[0]) * j / n, a[1] + (b[1] - a[1]) * j / n)
            p1 = (a[0] + (b[0] - a[0]) * (j + 1) / n, a[1] + (b[1] - a[1]) * (j + 1) / n)
            ld.line([p0, p1], fill=WD.lerp(SEA, INK, 0.35), width=4)
    img.paste(lay, (0, 0), m)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([40, top, 1040, bot], radius=40, outline=(86, 103, 154), width=4)
    if label:
        WD.T(d, (150, top + 70), "IRAN", "small", WD.lerp(LAND, INK, 0.7), "lm", size=30)
        WD.T(d, (150, bot - 50), "ARABIAN PENINSULA", "small", WD.lerp(LAND, INK, 0.7), "lm", size=30)
        WD.T(d, (520, bot - 50), "simplified map", "small", MUTED, "lm", size=26)
    return d

def tanker(d, x, y, s=1.0, col=INK, deck=None):
    """Side-view oil tanker pointing right."""
    deck = deck or WD.lerp(col, NAVY, 0.35)
    d.polygon([(x - 60 * s, y - 12 * s), (x + 48 * s, y - 12 * s), (x + 66 * s, y + 2 * s), (x + 46 * s, y + 14 * s),
               (x - 56 * s, y + 14 * s)], fill=col)
    d.rectangle([x - 54 * s, y - 26 * s, x - 30 * s, y - 12 * s], fill=deck)
    d.rectangle([x - 24 * s, y - 17 * s, x + 36 * s, y - 12 * s], fill=deck)

def lane_tankers(img, d, t, speed=0.06, n=6, stop_u=None, s=1.0, hi=2):
    """Tankers moving along LANE; with stop_u they queue up behind that point."""
    out = []
    for k in range(n):
        u = (k / n + t * speed) % 1.0
        if stop_u is not None:
            u = min(u, stop_u - 0.035 * ((n - 1 - k) % n)) if u < stop_u + 0.02 else u
        x, y = WD.path_at(LANE, u)
        if x < 100 or x > 990:
            continue
        if k == hi:
            WD.glow(img, x, y, 46, Y, 60); d = ImageDraw.Draw(img)
        tanker(d, x, y, s, Y if k == hi else INK)
        out.append((x, y))
    return d, out

def barrel(d, x, y, s=1.0, col=INK):
    w, h = 46 * s, 62 * s
    d.rounded_rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2], radius=int(10 * s), fill=col)
    for f in (-0.22, 0.22):
        d.line([(x - w / 2, y + h * f), (x + w / 2, y + h * f)], fill=WD.lerp(col, NAVY, 0.4), width=max(2, int(4 * s)))

def pump(img, d, x, y, s=1.0, sign_a=1.0, arrow=0.0, e=None):
    """Gas pump with a price sign; arrow (0-1) = a yellow up arrow on the sign (no real price shown)."""
    WD.shadow(img, lambda m: m.rounded_rectangle([x - 90 * s, y - 150 * s, x + 90 * s, y + 210 * s], radius=int(24 * s), fill=255), (8, 16), 18, 110)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x - 90 * s, y - 150 * s, x + 90 * s, y + 210 * s], radius=int(24 * s), fill=(214, 72, 72))
    d.rounded_rectangle([x - 62 * s, y - 118 * s, x + 62 * s, y - 20 * s], radius=int(12 * s), fill=(20, 26, 46))
    d.rectangle([x - 100 * s, y + 200 * s, x + 100 * s, y + 230 * s], fill=(70, 78, 104))
    d.line([(x + 90 * s, y + 10 * s), (x + 130 * s, y + 10 * s), (x + 130 * s, y + 140 * s)], fill=(40, 44, 60), width=int(12 * s))
    d.rounded_rectangle([x + 112 * s, y + 130 * s, x + 150 * s, y + 180 * s], radius=int(8 * s), fill=(40, 44, 60))
    if arrow > 0.02:
        ax, ay = x, y - 69 * s
        h = 34 * s * arrow
        d.polygon([(ax, ay - h - 12 * s), (ax - 26 * s, ay - h + 14 * s), (ax + 26 * s, ay - h + 14 * s)], fill=Y)
        d.rectangle([ax - 10 * s, ay - h + 12 * s, ax + 10 * s, ay + 30 * s], fill=Y)
    return d

def hbar(d, x0, x1, y, h, parts, grow=1.0):
    """To-scale stacked horizontal bar: parts = [(value, color), ...]; grow reveals left to right."""
    tot = sum(v for v, _ in parts)
    x = x0
    lim = x0 + (x1 - x0) * grow
    edges = []
    for v, col in parts:
        w = (x1 - x0) * v / tot
        xe = min(x + w, lim)
        if xe > x:
            d.rectangle([x, y, xe, y + h], fill=col)
        edges.append((x, x + w))
        x += w
    d.rounded_rectangle([x0 - 4, y - 4, x1 + 4, y + h + 4], radius=10, outline=(86, 103, 154), width=4)
    return edges

# ---------------- scenes ----------------
def hz_hook(img, d, t, p, ctx):
    """Frame 0: tankers stream through the narrow strait (yellow one to track) and a gas pump sign ticks up."""
    e = ctx["env"]
    z = 1.0 + 0.04 * WD.ease_io(WD.seg(t, 0, p["_dur"]))
    d = strait_map(img, d, e, t)
    d, pos = lane_tankers(img, d, t, 0.07)
    # narrowest point marker
    a = WD.ease_out(WD.seg(t, 0.2, 0.6))
    d.line(NARROW, fill=WD.lerp(SEA, Y, a), width=7)
    WD.label(d, "the narrow part", (600, 900), (700, 700), e, role="label", color=Y, a=a, maxw=300)
    d = pump(img, d, 820, 1120, 0.62, arrow=WD.ease_out(WD.seg(t, p.get("price_at", 2.0), p.get("price_at", 2.0) + 0.5)), e=e)
    badge(d, (540, 560), "STRAIT OF HORMUZ", e)
    return WD.zoom(img, z, 560, 960)

def hz_imports(img, d, t, p, ctx):
    """DATA: U.S. crude oil imports in 2025 (6.2 million b/d) as a to-scale bar; the Gulf region's 8% in yellow."""
    e = ctx["env"]
    badge(d, (540, 560), "U.S. CRUDE IMPORTS · 2025", e)
    x0, x1, y, h = 120, 900, 930, 150
    grow = WD.ease_out(WD.seg(t, 0.2, 1.2))
    edges = hbar(d, x0, x1, y, h, [(8, Y), (92, (96, 112, 160))], grow)
    a = WD.ease_out(WD.seg(t, p.get("gulf_at", 1.6), p.get("gulf_at", 1.6) + 0.4))
    if a > 0.02:
        gx = (edges[0][0] + edges[0][1]) / 2
 
        WD.T(d, (gx + 30, y - 190), "8%", "value", WD.lerp(e["bottom"], Y, a), "lm", size=150)
        WD.label(d, "from the Middle East Gulf: 8%", (gx, y + h + 10), (gx + 40, y + h + 90), e, role="label", color=Y, a=a, maxw=760)
    a2 = WD.ease_out(WD.seg(t, 1.0, 1.4))
    if a2 > 0.02:
        WD.T(d, ((edges[1][0] + edges[1][1]) / 2, y + h / 2), "everywhere else: 92%", "label", WD.lerp((96, 112, 160), INK, a2), "mm", size=40)
        WD.T(d, (540, y - 60), "6.2 million barrels a day, to scale", "small", MUTED, "mm", size=32)
    # little tanker heading off the bar's yellow slice
    if a > 0.3:
        pass
    WD.T(d, (540, 1270), "Source: EIA · Middle East Gulf countries", "small", MUTED, "mm", size=26)
    return img

def hz_flow(img, d, t, p, ctx):
    """The strait again: a counter climbs to 20 million barrels a day (2024); 1 barrel in 5 lights up yellow."""
    e = ctx["env"]
    d = strait_map(img, d, e, t)
    d, _ = lane_tankers(img, d, t, 0.11, n=8, hi=3)
    v = WD.counter(t, 0.3, 1.4, 0, 20)
    d.rounded_rectangle([120, 660, 640, 800], radius=26, fill=(24, 30, 62), outline=(86, 103, 154), width=3)
    WD.T(d, (150, 712), WD.number(v, 0) + " million", "value", Y, "lm", size=62)
    WD.T(d, (150, 768), "barrels a day · 2024", "small", INK, "lm", size=30)
    a = WD.ease_out(WD.seg(t, p.get("fifth_at", 3.0), p.get("fifth_at", 3.0) + 0.5))
    if a > 0.02:
        d.rounded_rectangle([140, 1130, 900, 1290], radius=26, fill=WD.lerp(SEA, (24, 30, 62), a), outline=WD.lerp(SEA, (86, 103, 154), a), width=3)
        for k in range(5):
            barrel(d, 200 + k * 64, 1210, 0.8, Y if k == 0 else WD.lerp(SEA, (150, 160, 190), a))
        WD.T(d, (700, 1190), "about 1 in 5", "label", WD.lerp(SEA, Y, a), "mm", size=42)
        WD.T(d, (700, 1240), "of the world's oil use", "small", WD.lerp(SEA, INK, a), "mm", size=30)
    badge(d, (540, 560), "THROUGH THE STRAIT", e)
    return img

def hz_choke(img, d, t, p, ctx):
    """WHAT-IF: a barrier closes the lane, tankers queue, thin bypass pipelines carry a sliver; to-scale bar."""
    e = ctx["env"]
    close = WD.ease_out(WD.seg(t, p.get("choke_at", 0.8), p.get("choke_at", 0.8) + 0.5))
    d = strait_map(img, d, e, t, label=False)
    # tankers queue behind the narrow point once it closes
    if close < 0.5:
        d, _ = lane_tankers(img, d, t, 0.07, n=6)
    else:
        for k in range(6):
            u = 0.36 - k * 0.07
            x, y = WD.path_at(LANE, u)
            if x > 100:
                tanker(d, x, y, 1.0, Y if k == 0 else INK)
    # barrier
    if close > 0.02:
        (ax, ay), (bx, by) = NARROW
        mx, my = (ax + bx) / 2, (ay + by) / 2
        hl = 62 * close
        d.line([(mx, my - hl), (mx, my + hl)], fill=RED, width=16)
        for k in range(-1, 2):
            d.line([(mx - 14, my + k * 36 - 10), (mx + 14, my + k * 36 + 10)], fill=WHITE, width=5)
    # bypass pipelines over land (top and bottom), small flow dots
    pa = WD.ease_out(WD.seg(t, p.get("pipe_at", 2.2), p.get("pipe_at", 2.2) + 0.5))
    if pa > 0.02:
        for pts in ([(330, 1125), (440, 1205), (700, 1235), (900, 1175)], [(230, 1135), (215, 1310)]):
            d.line(pts, fill=WD.lerp(LAND, TEAL, pa), width=12, joint="curve")
            for j in range(4):
                u = (j / 4 + t * 0.25) % 1
                x, y = WD.path_at(pts, u)
                d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=WD.lerp(LAND, WHITE, pa))
        WD.T(d, (560, 1272), "bypass pipelines", "small", WD.lerp(LAND, TEAL, pa), "mm", size=30)
    # to-scale bar: 20 vs ~2.6 available
    ba = WD.ease_out(WD.seg(t, p.get("pipe_at", 2.2) + 0.3, p.get("pipe_at", 2.2) + 1.0))
    if ba > 0.02:
        x0, x1, y = 120, 900, 650
        edges = hbar(d, x0, x1, y, 56, [(2.6, TEAL), (17.4, (96, 112, 160))], ba)
        WD.T(d, (x0, y + 90), "spare pipelines: ~2.6 of 20 million b/d (EIA est.)", "small", TEAL, "lm", size=30)
    sa = WD.ease_out(WD.seg(t, p.get("stuck_at", 4.0), p.get("stuck_at", 4.0) + 0.3))
    if sa > 0.02:
        WD.chip(d, (330, 880), "THE REST IS STUCK", e, fill=Y, fg=NAVY, a=sa, role="label")
    badge(d, (540, 560), "WHAT IF IT'S CHOKED? · ILLUSTRATION", e)
    return img

NODES = {"ASIA": (300, 760), "EUROPE": (720, 760), "TEXAS": (720, 1140), "AFRICA": (300, 1140)}

def market_world(d, e, bids=0.0, t=0.0, rise=0.0, hi="TEXAS"):
    """Four regions on a simple board: each has barrels and a price meter. bids = Asia's arrows to the others."""
    for name, (x, y) in NODES.items():
        d.rounded_rectangle([x - 170, y - 120, x + 170, y + 120], radius=30, fill=(28, 36, 70), outline=(86, 103, 154), width=3)
        WD.T(d, (x, y - 80), name, "label", Y if (name == hi and rise > 0.05) else INK, "mm", size=38)
        for k in range(3):
            barrel(d, x - 110 + k * 56, y + 30, 0.8, (150, 160, 190))
        # price meter (no real values): rises with 'rise'
        mx, my0, my1 = x + 110, y + 70, y - 40
        d.rounded_rectangle([mx - 16, my1 - 6, mx + 16, my0 + 6], radius=10, fill=(16, 20, 40))
        lvl = 0.3 + 0.6 * rise
        d.rectangle([mx - 10, my0 - (my0 - my1) * lvl, mx + 10, my0], fill=Y if rise > 0.05 else (120, 130, 170))
    if bids > 0.02:
        ax, ay = NODES["ASIA"]
        for name in ("EUROPE", "TEXAS", "AFRICA"):
            bx, by = NODES[name]
            ex, ey = ax + (bx - ax) * bids * 0.62, ay + (by - ay) * bids * 0.62
            d.line([(ax + 40, ay + 20), (ex + 40, ey + 20)], fill=ORANGE, width=8)
            d.ellipse([ex + 26, ey + 6, ex + 54, ey + 34], fill=ORANGE)

def hz_bids(img, d, t, p, ctx):
    """Asia lost most of the strait's oil (84% went there in 2024): its buyers reach for barrels elsewhere."""
    e = ctx["env"]
    badge(d, (540, 560), "ONE OIL MARKET · SIMPLIFIED MODEL", e)
    bids = WD.ease_io(WD.seg(t, p.get("bid_at", 1.8), p.get("bid_at", 1.8) + 1.2))
    market_world(d, e, bids, t)
    a = WD.ease_out(WD.seg(t, 0.3, 0.7))
    if a > 0.02:
        txt = "84% of the strait's crude went to Asia (2024)" if bids < 0.5 else "Asian buyers bid for other barrels"
        WD.chip(d, (540, 950), txt, e, fill=(24, 30, 62), fg=Y if bids < 0.5 else ORANGE, a=a, role="small")
    return img

def hz_together(img, d, t, p, ctx):
    """Same board: a link line joins the meters and every price rises together; Texas lights up yellow."""
    e = ctx["env"]
    badge(d, (540, 560), "ONE OIL MARKET · SIMPLIFIED MODEL", e)
    rise = WD.ease_io(WD.seg(t, p.get("rise_at", 1.6), p.get("rise_at", 1.6) + 1.2))
    market_world(d, e, 1.0, t, rise)
    if rise > 0.02:
        pts = [(x + 110, y - 40) for x, y in NODES.values()]
        for i in range(len(pts)):
            a_, b_ = pts[i], pts[(i + 1) % len(pts)]
            d.line([a_, b_], fill=WD.lerp((28, 36, 70), Y, rise * 0.6), width=3)
    ta = WD.ease_out(WD.seg(t, p.get("texas_at", 3.2), p.get("texas_at", 3.2) + 0.4))
    if ta > 0.02:
        tx, ty = NODES["TEXAS"]
        WD.glow(img, tx, ty, 190, Y, 40); d = ImageDraw.Draw(img)
        d.rounded_rectangle([tx - 176, ty - 126, tx + 176, ty + 126], radius=32, outline=Y, width=6)
    WD.chip(d, (540, 950), "illustration, not a price forecast", e, fill=(24, 30, 62), fg=MUTED, role="small")
    return img

def hz_pump(img, d, t, p, ctx):
    """A gallon of gas split to scale: crude oil about half (2025 average), the rest refining, delivery, taxes."""
    e = ctx["env"]
    badge(d, (540, 560), "WHAT'S IN A GALLON", e)
    d = pump(img, d, 230, 900, 1.0, arrow=WD.ease_out(WD.seg(t, 0.4, 0.9)), e=e)
    # vertical to-scale bar beside the pump: crude 51% at the bottom
    x0, x1, yt, yb = 430, 580, 680, 1180
    g = WD.ease_out(WD.seg(t, 0.3, 1.3))
    h = (yb - yt)
    cut = yb - h * 0.51
    d.rounded_rectangle([x0 - 4, yt - 4, x1 + 4, yb + 4], radius=10, outline=(86, 103, 154), width=4)
    top = yb - h * g
    d.rectangle([x0, max(cut, top), x1, yb], fill=Y)
    if top < cut:
        d.rectangle([x0, top, x1, cut], fill=(96, 112, 160))
    if g > 0.6:
        WD.label(d, "crude oil: about half", (x1, (cut + yb) / 2), (x1 + 40, (cut + yb) / 2), e, role="label", color=Y, maxw=320, dot=False)
        WD.label(d, "refining, delivery, taxes", (x1, (yt + cut) / 2), (x1 + 40, (yt + cut) / 2), e, role="small", color=INK, maxw=320, dot=False)
    WD.T(d, (540, 1250), "Price of a gallon, 2025 avg · Source: EIA", "small", MUTED, "mm", size=26)
    return img

def hz_payoff(img, d, t, p, ctx):
    """Back to the strait: the queue of tankers, and a fuel receipt sliding out of the pump."""
    e = ctx["env"]
    d = strait_map(img, d, e, t, top=600, bot=1180, label=False)
    for k in range(6):
        x, y = WD.path_at(LANE, 0.36 - k * 0.07)
        if x > 100:
            tanker(d, x, y, 1.0, Y if k == 0 else INK)
    (ax, ay), (bx, by) = NARROW
    d.line([((ax + bx) / 2, (ay + by) / 2 - 62), ((ax + bx) / 2, (ay + by) / 2 + 62)], fill=RED, width=16)
    u = WD.ease_out(WD.seg(t, 0.3, 1.4))
    rx, ry = 700, 630
    rh = 60 + 200 * u
    WD.shadow(img, lambda m: m.rectangle([rx, ry, rx + 220, ry + rh], fill=255), (6, 10), 10, 90)
    d = ImageDraw.Draw(img)
    d.rectangle([rx, ry, rx + 220, ry + rh], fill=(248, 248, 244))
    for k in range(int(rh / 40)):
        d.line([(rx + 24, ry + 30 + k * 40), (rx + 196 - (k % 2) * 50, ry + 30 + k * 40)], fill=(170, 170, 176), width=6)
    a = WD.ease_out(WD.seg(t, 0.4, 0.8))
    WD.chip(d, (380, 760), "a traffic jam you'll never see", e, fill=Y, fg=NAVY, a=a, role="label")
    z = 1.0 + 0.05 * WD.ease_io(WD.seg(t, 0, p["_dur"]))
    return WD.zoom(img, z, 540, 960)

# ---------------- cover ----------------
def hz_cover(img, d, t, p, ctx):
    """Living cover: the strait map (scene 1) bigger and lower, tankers in the lane, a pump with a yellow up arrow."""
    e = ctx["env"]
    d = strait_map(img, d, e, 0.0, top=640, bot=1660, label=False)
    for k, u in enumerate((0.22, 0.36, 0.50, 0.66, 0.80)):
        x, y = WD.path_at(LANE, u)
        if k == 2:
            WD.glow(img, x, y, 56, Y, 70); d = ImageDraw.Draw(img)
        tanker(d, x, y, 1.25, Y if k == 2 else INK)
    (ax, ay), (bx, by) = NARROW
    d.line([(ax, ay), (bx, by)], fill=Y, width=8)
    d = pump(img, d, 820, 1330, 0.8, arrow=1.0, e=e)
    WD.T(d, (990, 690), "simplified map", "small", MUTED, "rm", size=26)
    return img
