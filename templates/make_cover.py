#!/usr/bin/env python3
"""Bonus Braincell cover template v2 (thumbnail = video frame 0).

Usage: python3 make_cover.py OUT/cover.png --spec cover.json [--logo logo.png] [--preview]

Fills the 3:4 grid crop (y 240-1680) with no dead space:
series pill -> big two-line headline (white + yellow) -> one big visual on a yellow glow
-> white kicker pill -> logo + BONUS BRAINCELL.

cover.json:
  {"series": "Follow the Money", "l1": "The IPO price", "l2": "isn't your price",
   "kicker": "So who sets the first trade?",
   "visual": {"type": "tags", "items": [["OFFER PRICE", "$20", true], ["WHAT YOU PAY", "?", false]], "between": "≠"}}
  or "visual": {"type": "big", "text": "1%", "sub": "of oil futures end in a real barrel"}
  or "visual": {"type": "icon", "name": "ship", "label": "MONROVIA", "sub": "optional line"}   (v3: topic object, Lucide icon)
Design system v3: colors, fonts and the logo come from design-system.json / design.py (shared with the renderer).
--preview writes OUT/cover_crops.png: full frame, 3:4 grid crop, 1:1 crop side by side.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_episode import background, F, wrap, logo_img, NAVY, YELLOW, WHITE, MUTED, W, H
import design as DZ
from PIL import Image, ImageDraw, ImageFilter


def fit_font(d, lines, maxw, start=150, weight="ExtraBold", floor=96):
    size = start
    while size > floor and any(d.textlength(l, font=F(size, weight)) > maxw for l in lines):
        size -= 4
    return F(size, weight), size


def glow(img, cx, cy, r):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    gd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=DZ.C["track"] + (70,))
    g = g.filter(ImageFilter.GaussianBlur(r * 0.45))
    img.paste(g, (0, 0), g)


def card(d, x0, y0, x1, y1, label, value, hl):
    bg, fg = (YELLOW, NAVY) if hl else (WHITE, NAVY)
    d.rounded_rectangle([x0, y0, x1, y1], radius=36, fill=bg)
    d.ellipse([x0 + 22, (y0 + y1) / 2 - 14, x0 + 50, (y0 + y1) / 2 + 14], fill=NAVY)
    cx = (x0 + x1) / 2 + 12
    vf, _ = fit_font(d, [value], x1 - x0 - 150, 150, floor=60)  # leave room for the between-circle and dot
    d.text((cx, y0 + (y1 - y0) * 0.42), value, font=vf, fill=fg, anchor="mm")
    d.text((cx, y0 + (y1 - y0) * 0.80), label, font=F(34, "Bold"), fill=fg, anchor="mm")


def make(out, spec, logo=None, preview=None):
    img = background()
    d = ImageDraw.Draw(img)
    series = spec["series"].upper()
    # series pill (top of the 3:4 crop)
    tw = d.textlength(series, font=F(38, "Bold"))
    d.rounded_rectangle([540 - tw / 2 - 32, 300, 540 + tw / 2 + 32, 366], radius=33, fill=YELLOW)
    d.text((540, 333), series, font=F(38, "Bold"), fill=NAVY, anchor="mm")
    # headline
    hf, hs = fit_font(d, [spec["l1"], spec["l2"]], 1000)
    y = 400 + hs * 0.55
    for txt, col in [(spec["l1"], WHITE), (spec["l2"], YELLOW)]:
        d.text((540, y), txt, font=hf, fill=col, anchor="mm")
        y += hs * 1.08
    # visual zone centre
    vis = spec["visual"]
    vy = 1010
    glow(img, 540, vy, 430)
    d = ImageDraw.Draw(img)
    if vis["type"] == "tags":
        (l1, v1, h1), (l2, v2, h2) = vis["items"]
        card(d, 60, vy - 175, 520, vy + 175, l1, v1, h1)
        card(d, 560, vy - 175, 1020, vy + 175, l2, v2, h2)
        if vis.get("between"):
            d.ellipse([540 - 62, vy - 62, 540 + 62, vy + 62], fill=NAVY)
            d.text((540, vy - 4), vis["between"], font=F(96, "ExtraBold"), fill=YELLOW, anchor="mm")
    elif vis["type"] == "icon":  # v3: the episode's own object
        DZ.paste_icon(img, d, vis["name"], 540, vy - 40, 460, "track")
        d = ImageDraw.Draw(img)
        if vis.get("label"):
            DZ.chip(d, (540, vy + 230), vis["label"], fill="panel", fg="track", role="label", pad=(30, 14))
        if vis.get("sub"):
            sf, _ = fit_font(d, [vis["sub"]], 960, 46, "Bold", floor=34)
            d.text((540, vy + 300), vis["sub"], font=sf, fill=WHITE, anchor="mm")
    elif vis["type"] == "wing":  # two symmetric wing sections, both tilted, each with a lift arrow (2026-11-22)
        for k, (lab, flip, hl) in enumerate(vis["items"]):
            x0 = 60 + k * 500
            d.rounded_rectangle([x0, vy - 200, x0 + 460, vy + 200], radius=DZ.S["radius"], fill=DZ.col("panel"),
                                outline=DZ.col("track" if hl else "ink"), width=DZ.S["outline"])
            fx, fy = x0 + 230, vy + 50
            DZ.draw_foil(d, fx, fy, 300, 9, camber=vis.get("camber", 0.0), thick=0.14, flip=flip, fill="ink", outline="ink")
            DZ.arrow(d, (fx, fy - 30), (fx, fy - 190), "track", DZ.S["track"] + 4)
            d.text((fx, vy + 150), lab, font=F(38, "ExtraBold"), fill=DZ.col("track" if hl else "ink"), anchor="mm")
        if vis.get("between"):
            d.ellipse([540 - 62, vy - 62, 540 + 62, vy + 62], fill=DZ.col("bg"))
            d.text((540, vy - 4), vis["between"], font=F(96, "ExtraBold"), fill=DZ.col("track"), anchor="mm")
    else:  # big number / word
        bf, bs = fit_font(d, [vis["text"]], 900, 400, floor=160)
        d.text((540, vy - 40), vis["text"], font=bf, fill=YELLOW, anchor="mm")
        if vis.get("sub"):
            sf, _ = fit_font(d, [vis["sub"]], 960, 52, "Bold", floor=34)
            d.text((540, vy + bs * 0.5 + 10), vis["sub"], font=sf, fill=WHITE, anchor="mm")
    # kicker pill
    kf, _ = fit_font(d, [spec["kicker"]], 900, 52, "ExtraBold", floor=36)
    kw = d.textlength(spec["kicker"], font=kf)
    d.rounded_rectangle([540 - kw / 2 - 40, 1340, 540 + kw / 2 + 40, 1440], radius=50, fill=WHITE)
    d.text((540, 1390), spec["kicker"], font=kf, fill=NAVY, anchor="mm")
    # brand row (bottom of the 3:4 crop)
    lg = logo_img(110, logo)
    bw = d.textlength("BONUS BRAINCELL", font=F(44, "ExtraBold"))
    x = 540 - (lg.width + 22 + bw) / 2
    img.paste(lg, (int(x), 1480), lg)
    d.text((x + lg.width + 22, 1480 + lg.height / 2), "BONUS BRAINCELL", font=F(44, "ExtraBold"), fill=WHITE, anchor="lm")
    img.save(out)
    if preview:
        full = img.resize((270, 480))
        g = img.crop((0, 240, 1080, 1680)).resize((360, 480))
        s = img.crop((0, 420, 1080, 1500)).resize((480, 480))
        sheet = Image.new("RGB", (1170, 520), (20, 20, 24))
        sheet.paste(full, (20, 20)); sheet.paste(g, (310, 20)); sheet.paste(s, (690, 20))
        sheet.save(preview)


if __name__ == "__main__":
    a = sys.argv
    logo = a[a.index("--logo") + 1] if "--logo" in a else None
    if "--spec" not in a:
        sys.exit(__doc__)
    spec = json.load(open(a[a.index("--spec") + 1]))
    make(a[1], spec, logo, a[1].replace(".png", "_crops.png") if "--preview" in a else None)
