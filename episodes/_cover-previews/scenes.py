"""Cover art for the upcoming slots that are not demo episodes (Nov 27 - Dec 5), for the nine-cover grid preview.
Each uses a different composition and environment; numbers shown are from the content-log verification notes
(core verified 2026-11-23) and must be re-checked by the daily fact-check before the episode is made.
"""
import math, random
from PIL import Image, ImageDraw, ImageFont
import world as WD
import design as DZ

Y = DZ.C["track"]; NAVY = DZ.C["bg"]; INK = (244, 246, 251)
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

def blackfriday(img, d, t, p, ctx):
    """MINIATURE WORLD: a paper-cutout Philadelphia street jammed with shoppers' cars, a traffic officer's whistle."""
    e = ctx["env"]
    for k, (x, h) in enumerate([(60, 520), (230, 640), (400, 560), (580, 700), (760, 600), (900, 540)]):
        col = [(232, 214, 190), (210, 180, 150), (236, 226, 208), (196, 170, 140), (226, 204, 176), (205, 186, 160)][k]
        WD.shadow(img, lambda m: m.rectangle([x, 1300 - h, x + 170, 1300], fill=255), (8, 10), 10, 80)
        d.rectangle([x, 1300 - h, x + 170, 1300], fill=col)
        for r in range(int(h / 80)):
            for c in range(3):
                d.rectangle([x + 20 + c * 50, 1300 - h + 30 + r * 80, x + 50 + c * 50, 1300 - h + 70 + r * 80], fill=(120, 140, 170))
    d.rectangle([0, 1300, 1080, 1500], fill=(90, 96, 110))
    rnd = random.Random(2)
    for k in range(9):  # gridlocked cars
        x = 40 + k * 118; y = 1340 + (k % 2) * 70
        c = rnd.choice([(235, 87, 87), (47, 128, 237), (39, 174, 96), (242, 201, 76), (230, 230, 230)])
        d.rounded_rectangle([x, y, x + 100, y + 48], radius=14, fill=c)
        d.rounded_rectangle([x + 18, y - 22, x + 82, y + 4], radius=10, fill=WD.lerp(c, (255, 255, 255), 0.4))
    # traffic officer's whistle, big
    cx, cy = 760, 1030
    d.ellipse([cx - 120, cy - 120, cx + 120, cy + 120], fill=(200, 205, 212), outline=(120, 128, 140), width=8)
    d.rounded_rectangle([cx - 300, cy - 70, cx - 60, cy + 30], radius=30, fill=(200, 205, 212), outline=(120, 128, 140), width=8)
    for k in range(3):
        d.arc([cx - 300 - 60 * k - 80, cy - 140 - 40 * k, cx - 300 - 60 * k + 40, cy + 40 + 40 * k], 150, 210, fill=NAVY, width=10)
    return img

def hormuz(img, d, t, p, ctx):
    """MAP ROUTE: a simplified strait with a tanker lane squeezing through; the narrowest point marked."""
    land = (78, 92, 128); sea = (34, 48, 86)
    d.rectangle([0, 600, 1080, 1500], fill=sea)
    d.polygon([(0, 600), (1080, 600), (1080, 760), (760, 820), (600, 960), (420, 900), (0, 940)], fill=land)
    d.polygon([(0, 1500), (0, 1180), (380, 1120), (560, 1010), (700, 1060), (1080, 1000), (1080, 1500)], fill=land)
    lane = [(40, 1060), (300, 1030), (520, 990), (640, 1000), (820, 960), (1060, 900)]
    for k in range(len(lane) - 1):
        d.line([lane[k], lane[k + 1]], fill=WD.lerp(sea, INK, 0.45), width=6)
    for k, u in enumerate((0.15, 0.45, 0.75)):
        x, y = WD.path_at(lane, u)
        d.polygon([(x - 50, y - 14), (x + 40, y - 14), (x + 56, y), (x + 40, y + 14), (x - 50, y + 14)], fill=Y if k == 1 else INK)
    d.line([(600, 960), (560, 1010)], fill=Y, width=8)
    d.ellipse([570, 975, 590, 995], fill=Y)
    d.text((960, 1440), "simplified map", font=ImageFont.truetype(MONO, 26), fill=(170, 180, 205), anchor="rm")
    return img

def cardnumber(img, d, t, p, ctx):
    """MACRO CLOSE-UP: a sample card's number, masked, with the final check digit circled in yellow."""
    WD.shadow(img, lambda m: m.rounded_rectangle([90, 820, 990, 1390], radius=44, fill=255), (0, 24), 26, 150)
    d.rounded_rectangle([90, 820, 990, 1390], radius=44, fill=(28, 70, 140))
    d.rounded_rectangle([170, 920, 300, 1010], radius=14, fill=(214, 178, 96))
    f = ImageFont.truetype(MONO, 70)
    d.text((150, 1160), "•••• •••• •••• ••• ", font=f, fill=INK, anchor="lm")
    x = 150 + d.textlength("•••• •••• •••• ••• ", font=f)
    d.text((x - 6, 1160), "7", font=f, fill=Y, anchor="lm")
    d.ellipse([x - 46, 1100, x + 76, 1222], outline=Y, width=8)
    d.text((150, 1300), "SAMPLE ONLY", font=ImageFont.truetype(MONO, 30), fill=(170, 190, 225), anchor="lm")
    return img

def cybermonday(img, d, t, p, ctx):
    """OBJECT HERO (desk scale): an office laptop with a shipping box; a 2005 press-release card behind it."""
    d.rounded_rectangle([170, 760, 910, 1210], radius=22, fill=(255, 255, 255), outline=(156, 195, 218), width=6)
    d.rounded_rectangle([210, 800, 870, 1170], radius=10, fill=(47, 128, 237))
    d.text((540, 985), "CART (1)", font=DZ.F(70, "Black"), fill=(255, 255, 255), anchor="mm")
    d.polygon([(120, 1210), (960, 1210), (1010, 1260), (70, 1260)], fill=(205, 214, 224))
    d.rectangle([660, 1080, 960, 1300], fill=(196, 150, 100)); d.rectangle([660, 1080, 960, 1120], fill=(176, 130, 82))
    d.rectangle([790, 1080, 830, 1300], fill=(225, 205, 150))
    return img

def miles(img, d, t, p, ctx):
    """SCALE CONTRAST: a credit card larger than the airliner flying past it (the card earns more than you'd think)."""
    WD.shadow(img, lambda m: m.rounded_rectangle([140, 760, 940, 1260], radius=40, fill=255), (0, 24), 26, 150)
    d.rounded_rectangle([140, 760, 940, 1260], radius=40, fill=(18, 40, 86))
    d.rounded_rectangle([210, 850, 330, 930], radius=12, fill=(214, 178, 96))
    d.text((210, 1160), "MILES CARD", font=ImageFont.truetype(MONO, 46), fill=INK, anchor="lm")
    # small airliner crossing in front
    cx, cy, L = 640, 1000, 420
    h = L * 0.11
    d.rounded_rectangle([cx - L / 2, cy - h / 2, cx + L / 2, cy + h / 2], radius=int(h / 2), fill=(240, 244, 250))
    d.polygon([(cx - 60, cy), (cx + 80, cy), (cx - 20, cy + 120), (cx - 110, cy + 120)], fill=(210, 218, 230))
    d.polygon([(cx + L / 2 - 70, cy - h / 2), (cx + L / 2 - 10, cy - 110), (cx + L / 2 + 10, cy - 110), (cx + L / 2, cy - h / 2)], fill=(210, 218, 230))
    return img

def greenland(img, d, t, p, ctx):
    """DIAGRAM HERO, areas to scale: Africa vs Greenland as circles of true relative area (30.4 vs 2.17 million km2)."""
    A, G = 30.37, 2.166
    ra = 330; rg = ra * math.sqrt(G / A)
    d.ellipse([400 - ra, 1000 - ra, 400 + ra, 1000 + ra], fill=(39, 174, 96))
    d.ellipse([850 - rg, 1000 - rg, 850 + rg, 1000 + rg], fill=(255, 255, 255), outline=(47, 128, 237), width=6)
    d.text((400, 1000), "AFRICA", font=DZ.F(60, "Black"), fill=(255, 255, 255), anchor="mm")
    d.text((850, 1000 + rg + 50), "GREENLAND", font=DZ.F(40, "Black"), fill=NAVY, anchor="mm")
    d.text((540, 1430), "true areas, to scale", font=ImageFont.truetype(MONO, 28), fill=(74, 96, 117), anchor="mm")
    return img
