#!/usr/bin/env python3
"""Bonus Braincell design system v3: tokens, primitives, chrome, captions and the v3 scene types.

Every value comes from design-system.json (same folder). render_episode.py and make_cover.py import this
module, so Autopilot and Pick Mode always draw with the same rules. Rules: DESIGN.md.

v3 scene types (use these for new episodes):
  hook_object  topic-specific object/action at frame 0, optional short headline, optional result
  compare      labeled numbers side by side: baseline + value + units in one glance, optional bars
  whole        one proportional whole (bar or 100-tile grid) for quantities that coexist
  process      one object/value carried through distinct states (vertical or horizontal)
  cross        an object crosses a boundary and its state readout changes
  diagram      spec-driven schematic (shapes, icons, labels) with timed appear/move/rotate/track changes
  answer       the answer on screen, key words in yellow, optional sign-off

Timing: any param named "at" / ending in "_at" (and diagram "show"/"hide"/"track") may be a number of
seconds from scene start or a phrase from the scene's narration; the renderer converts phrases to seconds.
"""
import json, math, os, re
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
DS = json.load(open(os.path.join(HERE, "design-system.json")))

def hx(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

C = {k: hx(v) for k, v in DS["color"].items() if isinstance(v, str) and v.startswith("#")}
W, H = DS["canvas"]["w"], DS["canvas"]["h"]
L, M, S, T = DS["layout"], DS["motion"], DS["stroke"], DS["type"]
CX = L["center_x"]

# ---------- registry for QA (text boxes, icons used) ----------
REG = {"text": [], "icons": set(), "missing_icons": set(), "fit": []}
def reg_reset():
    REG["text"].clear(); REG["fit"].clear()

# ---------- fonts / easing ----------
_fc = {}
def F(size, weight="Bold"):
    key = (int(size), weight)
    if key not in _fc:
        _fc[key] = ImageFont.truetype(os.path.join(DS["font"]["dir"], f"Inter-{weight}.otf"), int(size))
    return _fc[key]

def ease(u):
    u = max(0.0, min(1.0, u))
    return 1 - (1 - u) ** 3

def inn(t, start, dur=None):
    return ease((t - start) / (dur or M["enter"]))

def blend(c1, c2, a):
    a = max(0.0, min(1.0, a))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * a) for i in range(3))

def col(role, a=1.0):
    """role -> RGB, faded in from bg by a."""
    c = C.get(role, C["ink"])
    return blend(C["bg"], c, a)

# ---------- text ----------
def _plain(s):
    return s.replace("*", "")

def _wrap(d, s, font, maxw):
    words, lines, cur = s.split(), [], ""
    for w_ in words:
        test = (cur + " " + w_).strip()
        if d.textlength(_plain(test), font=font) <= maxw or not cur:
            cur = test
        else:
            lines.append(cur); cur = w_
    if cur:
        lines.append(cur)
    return lines

def fit(d, s, role, maxw, max_lines=None, size=None):
    """Shrink from the role size to its minimum, then wrap up to max_lines. Returns (font, size, lines, ok)."""
    t = T[role]
    ml = max_lines or t.get("max_lines", 1)
    sz = size or t["size"]
    while True:
        font = F(sz, t["weight"])
        lines = _wrap(d, s, font, maxw)
        if len(lines) <= ml and all(d.textlength(_plain(l), font=font) <= maxw for l in lines):
            return font, sz, lines, True
        if sz <= t["min"]:
            return font, sz, lines[:ml], False
        sz -= 2

def txt(d, xy, s, role="label", fill="ink", anchor="mm", maxw=900, a=1.0, hi="track", max_lines=None, size=None):
    """Draw text with auto-fit and *highlight* markup (words between asterisks use the hi color).
    Registers the box for the layout check. Returns (x0, y0, x1, y1)."""
    if s is None or s == "":
        return None
    s = str(s)
    x, y = xy
    if y > L["rail_y"]:  # keep essential text clear of the platforms' right rail
        lo, hi_ = L["content_x"]
        if anchor[0] == "m":
            maxw = min(maxw, 2 * max(60, min(x - lo + 40, hi_ - x)))
        elif anchor[0] == "l":
            maxw = min(maxw, max(60, hi_ - x))
        else:
            maxw = min(maxw, max(60, x - lo + 40))
    font, sz, lines, ok = fit(d, s, role, maxw, max_lines, size)
    if not ok:
        REG["fit"].append(s)
    lh = sz * T[role]["line"]
    n = len(lines)
    if anchor[1] == "m":
        top = y - lh * n / 2
    elif anchor[1] == "s" or anchor[1] == "b":
        top = y - lh * n
    else:
        top = y
    on = False
    x0b, x1b = 1e9, -1e9
    for i, line in enumerate(lines):
        pw = d.textlength(_plain(line), font=font)
        lx = x - pw / 2 if anchor[0] == "m" else (x - pw if anchor[0] == "r" else x)
        ly = top + i * lh + lh / 2
        cx_ = lx
        for k, word in enumerate(line.split(" ")):
            seg = word
            while seg:
                if seg.startswith("*"):
                    on = not on; seg = seg[1:]; continue
                j = seg.find("*")
                part = seg if j < 0 else seg[:j]
                c = col(hi if on else fill, a) if isinstance(fill, str) else blend(C["bg"], fill, a)
                if part:
                    d.text((cx_, ly), part, font=font, fill=c, anchor="lm")
                    cx_ += d.textlength(part, font=font)
                seg = "" if j < 0 else seg[j:]
            if k < len(line.split(" ")) - 1:
                cx_ += d.textlength(" ", font=font)
        x0b, x1b = min(x0b, lx), max(x1b, lx + pw)
    box = (x0b, top, x1b, top + lh * n)
    if a > 0.5:
        REG["text"].append(dict(box=box, role=role, size=sz, text=_plain(s)[:60]))
    return box

def chip(d, xy, s, fill="panel", fg="ink", role="badge", pad=(22, 12), outline=None, a=1.0, anchor="mm"):
    font, sz, lines, _ = fit(d, s, role, 860, 1)
    w_ = d.textlength(_plain(lines[0]), font=font)
    h_ = sz * 1.0
    x, y = xy
    if anchor == "mm":
        x0, y0 = x - w_ / 2 - pad[0], y - h_ / 2 - pad[1]
    else:
        x0, y0 = x, y - h_ / 2 - pad[1]
    box = [x0, y0, x0 + w_ + 2 * pad[0], y0 + h_ + 2 * pad[1]]
    d.rounded_rectangle(box, radius=(h_ + 2 * pad[1]) / 2, fill=col(fill, a) if fill else None,
                        outline=col(outline, a) if outline else None, width=3 if outline else 0)
    txt(d, ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2), lines[0], role, fg, "mm", 2000, a)
    return box

def illustrative(d, y=None, a=1.0):
    chip(d, (CX, y or (L["kicker_y"] + 60)), "ILLUSTRATIVE NUMBERS", fill=None, fg="muted", outline="line", a=a)

def kicker(d, s, a=1.0, y=None):
    if s:
        txt(d, (CX, y or L["kicker_y"]), s, "kicker", "ink", "mm", 900, a)

def source(d, s, a=1.0, y=None):
    if s:
        txt(d, (CX, y or L["source_y"]), s if s.lower().startswith(("source", "illustr", "example")) else "Source: " + s,
            "source", "muted", "mm", 900, a)

# ---------- icons (Lucide, ISC) ----------
_ic = {}
def icon(name, size, role="ink", a=1.0, stroke_px=None):
    key = (name, int(size), role, round(a, 2), stroke_px)
    if key in _ic:
        return _ic[key]
    path = os.path.join(HERE, "icons", f"{name}.svg")
    im = None
    if os.path.exists(path):
        try:
            import cairosvg, io
            c = col(role, a)
            sw = (stroke_px or S["icon_px"]) * 24.0 / size
            svg = open(path).read().replace("currentColor", "#%02x%02x%02x" % c)
            svg = re.sub(r'stroke-width="[\d.]+"', f'stroke-width="{sw:.2f}"', svg)
            png = cairosvg.svg2png(bytestring=svg.encode(), output_width=int(size), output_height=int(size))
            im = Image.open(io.BytesIO(png)).convert("RGBA")
            REG["icons"].add(name)
        except Exception:
            im = None
    if im is None:
        REG["missing_icons"].add(name)
    _ic[key] = im
    return im

def paste_icon(img, d, name, cx, cy, size, role="ink", a=1.0, rot=0, label=None):
    im = icon(name, size, role, a)
    if im is None:  # fallback: labeled box
        d.rounded_rectangle([cx - size / 2, cy - size / 2.6, cx + size / 2, cy + size / 2.6], radius=S["radius"],
                            outline=col(role, a), width=S["outline"])
        txt(d, (cx, cy), label or name.replace("-", " "), "label", role, "mm", size - 30, a)
        return
    if rot:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    img.paste(im, (int(cx - im.width / 2), int(cy - im.height / 2)), im)

def arrow(d, p0, p1, role="ink", width=None, a=1.0, head=None):
    width = width or S["line"]; head = head or S["arrow_head"]
    (x0, y0), (x1, y1) = p0, p1
    ang = math.atan2(y1 - y0, x1 - x0)
    bx, by = x1 - head * 0.8 * math.cos(ang), y1 - head * 0.8 * math.sin(ang)
    d.line([x0, y0, bx, by], fill=col(role, a), width=int(width))
    d.polygon([(x1, y1), (bx + head * 0.5 * math.sin(ang), by - head * 0.5 * math.cos(ang)),
               (bx - head * 0.5 * math.sin(ang), by + head * 0.5 * math.cos(ang))], fill=col(role, a))

# ---------- background, chrome, caption ----------
_bg = None
def background():
    global _bg
    if _bg is None:
        img = Image.new("RGB", (W, H), C["bg"])
        d = ImageDraw.Draw(img)
        for y in range(0, H, 60):
            for x in range(0, W, 60):
                d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=C["bg_dot"])
        _bg = img
    return _bg.copy()

def mark(h, logo_path=None):
    p = logo_path if logo_path and os.path.exists(logo_path) else os.path.join(HERE, "brand", "mark.png")
    im = Image.open(p).convert("RGBA")
    r = h / im.height
    return im.resize((max(1, int(im.width * r)), int(h)), Image.LANCZOS)

def chrome(img, d, series, progress, logo_path=None):
    ph = L["progress_h"]
    d.rectangle([0, 0, W, ph], fill=C["panel"])
    d.rectangle([0, 0, int(W * progress), ph], fill=C["track"])
    lk = L["lockup"]
    mk = mark(lk["mark_h"], logo_path)
    img.paste(mk, (lk["x"], lk["y"] - mk.height // 2), mk)
    x = lk["x"] + mk.width + lk["gap"]
    f = F(T["lockup"]["size"], T["lockup"]["weight"])
    d.text((x, lk["y"]), "BONUS BRAINCELL", font=f, fill=C["ink"], anchor="lm")
    x += d.textlength("BONUS BRAINCELL", font=f) + 18
    d.text((x, lk["y"]), "·  " + series.upper(), font=F(T["lockup"]["size"], "Bold"), fill=C["muted"], anchor="lm")

def caption(img, text, stop_end=()):
    if not text:
        return
    cp = L["caption"]
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    words = text.split()
    size = T["caption"]["size"]
    font = F(size, T["caption"]["weight"])
    if d.textlength(text, font=font) <= cp["max_w"] or len(words) < 2:
        lines = [text]
    else:  # two balanced lines, no weak-word line ends, no one-word lines
        best = None
        for k in range(1, len(words)):
            a_, b_ = " ".join(words[:k]), " ".join(words[k:])
            w_ = max(d.textlength(a_, font=font), d.textlength(b_, font=font))
            if words[k - 1].lower().strip(",.:;\"'") in stop_end:
                w_ += 400
            if k == 1 or k == len(words) - 1:
                w_ += 300
            if best is None or w_ < best[0]:
                best = (w_, [a_, b_])
        lines = best[1]
    while size > T["caption"]["min"] and max(d.textlength(l, font=font) for l in lines) > cp["max_w"]:
        size -= 2; font = F(size, T["caption"]["weight"])
    lh = size * T["caption"]["line"]
    total = lh * len(lines)
    top = cp["center_y"] - total / 2
    maxw = max(d.textlength(l, font=font) for l in lines)
    box = [CX - maxw / 2 - cp["pad_x"], top - cp["pad_y"], CX + maxw / 2 + cp["pad_x"], top + total + cp["pad_y"]]
    d.rounded_rectangle(box, radius=cp["radius"], fill=tuple(DS["color"]["caption_box_rgba"]))
    for i, l in enumerate(lines):
        d.text((CX, top + i * lh + lh / 2 - 3), l, font=font, fill=C["ink"], anchor="mm")
    img.paste(ov, (0, 0), ov)
    REG["text"].append(dict(box=tuple(box), role="caption", size=size, text=text[:60]))

# ---------- v3 scenes ----------
def _motion_xy(motion, t, cx, cy):
    u = ease(t / 0.7)
    rot = 0
    if motion == "slide":
        cx = cx - 240 * (1 - u); cy += 8 * math.sin(t * 3)
    elif motion == "drop":
        cy = cy - 220 * (1 - u)
    elif motion == "rise":
        cy = cy + 220 * (1 - u)
    elif motion == "sway":
        rot = 6 * math.sin(t * 2.2); cy += 6 * math.sin(t * 2.2 + 1)
    elif motion == "spin":
        rot = -360 * ease(t / 1.2)
    elif motion == "pulse":
        pass
    return cx, cy, rot

def s_hook_object(img, d, t, p):
    """headline (optional, *markup*), icon, icon_label, motion, action, result, result_icon, result_at, illustrative."""
    has_head = bool(p.get("headline"))
    if has_head:
        txt(d, (CX, 600), p["headline"], "hook", "ink", "mm", 940)
    res_at = p.get("result_at", 0.9)
    has_res = bool(p.get("result"))
    oy = 1010 if has_head else 900
    ox = 300 if has_res else CX
    size = 300 if has_res else 400
    cx, cy, rot = _motion_xy(p.get("motion", "slide"), t, ox, oy)
    r = inn(t, res_at, M["change"]) if has_res else 0
    obj_role = "track" if r < 0.5 else "ink"
    if p.get("motion") == "pulse":
        size *= 1 + 0.04 * math.sin(t * 5)
    paste_icon(img, d, p.get("icon", "help-circle"), cx, cy, size, obj_role, 1.0, rot, p.get("icon_fallback"))
    if p.get("icon_label"):
        chip(d, (cx, cy + size * 0.55 + 10), p["icon_label"], fill="panel", fg="track" if obj_role == "track" else "ink",
             role="label", pad=(26, 12))
    if has_res:
        a = inn(t, res_at - 0.35, M["change"])
        if a > 0:
            arrow(d, (ox + size / 2 + 20, oy), (ox + size / 2 + 20 + 150 * a, oy), "muted", a=a)
            if p.get("action"):
                txt(d, (ox + size / 2 + 95, oy - 60), p["action"], "small", "muted", "mm", 260, a)
        if r > 0:
            rx = 760
            sc = 0.8 + 0.2 * r
            if p.get("result_icon"):
                paste_icon(img, d, p["result_icon"], rx, oy - 70, int(200 * sc), "track", r)
                txt(d, (rx, oy + 80), p["result"], "label", "track", "mm", 300, r)
            else:
                bw, bh = 300 * sc, 230 * sc
                d.rounded_rectangle([rx - bw / 2, oy - bh / 2, rx + bw / 2, oy + bh / 2], radius=S["radius"], fill=col("track", r))
                txt(d, (rx, oy), p["result"], "label", "on_track", "mm", 260, r)
    if p.get("illustrative"):
        illustrative(d, 1200)

def _value_unit(d, cx, cy, value, unit, role, a, maxw):
    """Value with its unit beside it (same glance). Falls back to unit under value if too wide."""
    vf, vs, _, _ = fit(d, str(value), "value", maxw, 1)
    vw = d.textlength(str(value), font=vf)
    uf = F(T["unit"]["size"], T["unit"]["weight"])
    uw = d.textlength(unit, font=uf) if unit else 0
    if unit and vw + 14 + uw <= maxw:
        x0 = cx - (vw + 14 + uw) / 2
        txt(d, (x0, cy), str(value), "value", role, "lm", maxw, a, size=vs)
        txt(d, (x0 + vw + 14, cy + vs * 0.22), unit, "unit", role, "lm", maxw, a)
    else:
        txt(d, (cx, cy), str(value), "value", role, "mm", maxw, a, size=vs)
        if unit:
            txt(d, (cx, cy + vs * 0.62), unit, "unit", role, "mm", maxw, a)
    return vs

def s_compare(img, d, t, p):
    """kicker, items [{label, value, unit, note, icon, n, track}], vs, bars (bool), illustrative, source."""
    kicker(d, p.get("kicker"))
    items = p["items"]
    k = len(items)
    x0s, x1s = L["content_x"]
    gap = 120 if (p.get("vs") and k == 2) else 0  # reserved middle gap for the relation sign
    cw = (x1s - x0s - gap) / k
    bars = p.get("bars") and all("n" in it for it in items)
    nmax = max((float(it.get("n", 0)) for it in items), default=1) or 1
    for i, it in enumerate(items):
        delay = 0.0 if not it.get("track") else 0.35
        a = inn(t, i * M["stagger"] + delay)
        role = "track" if it.get("track") else "ink"
        cx = x0s + cw * (i + 0.5) + (gap if i >= k / 2 else 0)
        y = 760
        if it.get("icon"):
            paste_icon(img, d, it["icon"], cx, 700, 140, role if it.get("track") else "muted", a)
            y = 880
        vs = _value_unit(d, cx, y, it["value"], it.get("unit", ""), role, a, cw - 20)
        ly = y + vs * 0.62 + (60 if it.get("unit") and False else 50)
        txt(d, (cx, ly + 30), it.get("label", ""), "label", "ink" if it.get("track") else "muted", "mm", cw - 50, a)
        if it.get("note"):
            txt(d, (cx, ly + 110), it["note"], "source", "muted", "mm", cw - 50, a)
        if bars:
            g = ease((t - 0.3 - i * M["stagger"] - delay) / M["change"])
            hmax = 190
            hh = hmax * float(it["n"]) / nmax * g
            d.rounded_rectangle([cx - 70, 1225 - max(hh, 4), cx + 70, 1225], radius=12, fill=col(role if it.get("track") else "line", a))
    if p.get("vs") and k == 2:
        vy = 880 if any(it.get("icon") for it in items) else 760
        txt(d, (CX, vy), p["vs"], "hook", "dim", "mm", 120)
    if p.get("illustrative"):
        illustrative(d)
    source(d, p.get("source"))

def s_whole(img, d, t, p):
    """kicker, total (label of the whole), segments [{label, n, value, track}], shape bar|grid, illustrative, source."""
    kicker(d, p.get("kicker"))
    if p.get("illustrative"):
        illustrative(d)
    segs = p["segments"]
    tot = sum(float(s_["n"]) for s_ in segs) or 1
    g = ease((t - 0.1) / 0.9)
    others = ["panel", "line", "dim"]
    roles = []
    oi = 0
    for s_ in segs:
        if s_.get("track"):
            roles.append("track")
        else:
            roles.append(others[oi % 3]); oi += 1
    if p.get("total"):
        txt(d, (CX, 690), p["total"], "small", "muted", "mm", 880)
    if p.get("shape", "bar") == "grid":
        cell, gap = 52, 8
        gx0 = CX - (10 * cell + 9 * gap) / 2
        gy0 = 740
        counts = [round(100 * float(s_["n"]) / tot) for s_ in segs]
        idx = []
        for r_, c_ in zip(roles, counts):
            idx += [r_] * c_
        idx = (idx + ["panel"] * 100)[:100]
        shown = int(100 * g)
        for n in range(100):
            rr, cc = divmod(n, 10)
            x, y = gx0 + cc * (cell + gap), gy0 + rr * (cell + gap)
            d.rounded_rectangle([x, y, x + cell, y + cell], radius=8, fill=col(idx[n] if n < shown else "bg_dot"))
        ly = gy0 + 10 * (cell + gap) + 30
    else:
        bx0, bx1 = L["content_x"]; by0, by1 = 760, 890
        d.rounded_rectangle([bx0, by0, bx1, by1], radius=20, outline=col("line"), width=3)
        x = bx0
        for s_, r_ in zip(segs, roles):
            w_ = (bx1 - bx0) * float(s_["n"]) / tot * g
            if w_ > 1:
                d.rectangle([x, by0, x + w_, by1], fill=col(r_))
                d.line([x + w_, by0, x + w_, by1], fill=C["bg"], width=4)
            x += w_
        ly = by1 + 70
    # legend: swatch + label + value, values beside their labels
    a = inn(t, 0.6)
    for i, (s_, r_) in enumerate(zip(segs, roles)):
        y = ly + i * 72
        d.rounded_rectangle([140, y - 20, 180, y + 20], radius=8, fill=col(r_, a))
        txt(d, (210, y), s_["label"], "label", "ink" if s_.get("track") else "muted", "lm", 500, a)
        if s_.get("value") is not None:
            txt(d, (L["content_x"][1], y), str(s_["value"]), "label", "track" if s_.get("track") else "ink", "rm", 260, a)
    source(d, p.get("source"), y=max(L["source_y"], ly + len(segs) * 72) if ly + len(segs) * 72 > L["source_y"] else None)

def s_process(img, d, t, p):
    """kicker, states [{label, sub, value}], token {icon, value}, at [seconds or phrases per state], layout v|h, flow, illustrative, source."""
    kicker(d, p.get("kicker"))
    st = p["states"]
    n = len(st)
    dur = p.get("_dur", 6.0)
    ats = p.get("at") or [i * (dur * 0.8) / max(1, n) for i in range(n)]
    ats = [float(x) for x in ats]
    cur = max([i for i, x in enumerate(ats) if t >= x] or [0])
    nxt_u = 0.0
    if cur + 1 < n:
        nxt_u = ease((t - ats[cur + 1] + M["change"]) / M["change"])
    vert = p.get("layout", "v" if n > 3 else "h") == "v"
    if vert:
        y0, y1 = 680, 1200
        pts = [(220, y0 + (y1 - y0) * i / max(1, n - 1)) for i in range(n)]
    else:
        x0, x1 = 220, 760
        pts = [(x0 + (x1 - x0) * i / max(1, n - 1), 960) for i in range(n)]
    for i in range(n - 1):
        role = "ink" if i < cur else "line"
        if p.get("flow"):
            (ax, ay), (bx, by) = pts[i], pts[i + 1]
            if vert:
                arrow(d, (ax, ay + 60), (bx, by - 60), role, 5)
            else:
                arrow(d, (ax + 80, ay), (bx - 80, by), role, 5)
        else:
            d.line([pts[i], pts[i + 1]], fill=col(role), width=5)
    for i, ((x, y), s_) in enumerate(zip(pts, st)):
        role = "track" if i == cur else ("ink" if i < cur else "dim")
        r = 64
        d.ellipse([x - r, y - r, x + r, y + r], fill=C["bg"], outline=col(role), width=S["outline"] + (3 if i == cur else 0))
        txt(d, (x, y), str(i + 1), "label", role, "mm", 80)
        lab_role = "ink" if i <= cur else "dim"
        if vert:
            txt(d, (x + 100, y - (18 if s_.get("sub") else 0)), s_["label"], "label", lab_role, "lm", 560)
            if s_.get("sub"):
                txt(d, (x + 100, y + 32), s_["sub"], "source", "muted" if i <= cur else "dim", "lm", 560)
        else:
            txt(d, (x, y + 125), s_["label"], "label", lab_role, "mm", 260)
            if s_.get("sub"):
                txt(d, (x, y + 205), s_["sub"], "small", "muted" if i <= cur else "dim", "mm", 260)
    # token carried through the states
    tok = p.get("token")
    if tok:
        (ax, ay) = pts[cur]
        (bx, by) = pts[min(cur + 1, n - 1)]
        tx, ty = ax + (bx - ax) * nxt_u, ay + (by - ay) * nxt_u
        val = st[cur].get("value", tok.get("value"))
        if vert:
            tx += 470; tx = min(tx, 800)
        else:
            ty -= 220
        if tok.get("icon"):
            paste_icon(img, d, tok["icon"], tx, ty - (40 if val else 0), 170, "track")
        if val:
            chip(d, (tx, ty + (50 if tok.get("icon") else 0)), str(val), fill="track", fg="on_track", role="label", pad=(24, 12))
    if p.get("illustrative"):
        illustrative(d)
    source(d, p.get("source"))

def s_cross(img, d, t, p):
    """kicker, left, right (region names), boundary (label), icon, before, after (state readouts), at, illustrative, source."""
    kicker(d, p.get("kicker"))
    bx = CX
    d.line([bx, 650, bx, 1170], fill=col("muted"), width=4)
    for yy in range(650, 1170, 40):
        d.line([bx, yy, bx, yy + 20], fill=C["bg"], width=6)
    txt(d, (320, 690), p.get("left", ""), "label", "muted", "mm", 380)
    txt(d, (740, 690), p.get("right", ""), "label", "muted", "mm", 360)
    if p.get("boundary"):
        txt(d, (bx, 1205), p["boundary"], "source", "muted", "mm", 600)
    at = float(p.get("at", 1.6))
    span = 1.8
    u = ease((t - (at - span / 2)) / span) if t > at - span / 2 else 0.0
    ox = 300 + (760 - 300) * u
    oy = 880
    paste_icon(img, d, p.get("icon", "circle"), ox, oy, 220, "track")
    crossed = ox >= bx
    flash = max(0.0, 1 - abs(t - at) / 0.4) if crossed else 0
    state = p.get("after") if crossed else p.get("before")
    if state:
        b = chip(d, (ox, oy + 160), state, fill="track" if flash > 0.2 else "panel", fg="on_track" if flash > 0.2 else "ink",
                 role="label", pad=(26, 14))
    if p.get("illustrative"):
        illustrative(d)
    source(d, p.get("source"))

def _pt(v):
    return (float(v[0]), float(v[1]))

def _rot(pts, deg, o):
    a = math.radians(deg); ox, oy = o
    return [(ox + (x - ox) * math.cos(a) - (y - oy) * math.sin(a), oy + (x - ox) * math.sin(a) + (y - oy) * math.cos(a)) for x, y in pts]

def s_diagram(img, d, t, p):
    """kicker, elements [...], illustrative, source. Element keys: type rect|circle|line|arrow|arc|polygon|text|icon,
    geometry in canvas px (stage y 620-1250), role ink|muted|dim|track|panel|line, fill (bool), width,
    show / hide (time), move {by:[dx,dy], at, dur}, rotate {from, to, at, dur, origin:[x,y]}, track (time it turns yellow),
    label {text, at:[x,y], role}."""
    kicker(d, p.get("kicker"))
    for e in p.get("elements", []):
        show = float(e.get("show", 0)); hide = e.get("hide")
        if t < show or (hide is not None and t >= float(hide)):
            continue
        a = inn(t, show)
        role = e.get("role", "ink")
        if e.get("track") is not None and t >= float(e["track"]):
            role = "track"
        dx = dy = 0.0
        if e.get("move"):
            mv = e["move"]; u = ease((t - float(mv.get("at", 0))) / float(mv.get("dur", M["change"])))
            dx, dy = mv["by"][0] * u, mv["by"][1] * u
        deg = 0.0; org = None
        if e.get("rotate"):
            rt = e["rotate"]; u = ease((t - float(rt.get("at", 0))) / float(rt.get("dur", M["change"])))
            deg = float(rt.get("from", 0)) + (float(rt["to"]) - float(rt.get("from", 0))) * u
            org = _pt(rt.get("origin", (CX, 900)))
        c = col(role, a)
        w_ = int(e.get("width", S["track"] if role == "track" else S["line"]))
        ty = e["type"]
        def tf(pts):
            pts = [(x + dx, y + dy) for x, y in pts]
            return _rot(pts, deg, (org[0] + dx, org[1] + dy)) if org else pts
        if ty == "rect":
            x, y, ww, hh = e["x"], e["y"], e["w"], e["h"]
            pts = tf([(x, y), (x + ww, y), (x + ww, y + hh), (x, y + hh)])
            if e.get("fill"):
                d.polygon(pts, fill=c)
            else:
                d.line(pts + [pts[0]], fill=c, width=w_, joint="curve")
        elif ty == "polygon":
            pts = tf([_pt(q) for q in e["pts"]])
            if e.get("fill"):
                d.polygon(pts, fill=c)
            else:
                d.line(pts + [pts[0]], fill=c, width=w_, joint="curve")
        elif ty == "circle":
            (x, y), = tf([(e["x"], e["y"])]); r = e["r"]
            d.ellipse([x - r, y - r, x + r, y + r], fill=c if e.get("fill") else None, outline=None if e.get("fill") else c, width=w_)
        elif ty == "line":
            d.line(tf([_pt(q) for q in e["pts"]]), fill=c, width=w_, joint="curve")
        elif ty == "arrow":
            p0, p1 = tf([_pt(e["from"]), _pt(e["to"])])
            grow = ease((t - show) / float(e.get("grow", 0.4)))
            p1 = (p0[0] + (p1[0] - p0[0]) * grow, p0[1] + (p1[1] - p0[1]) * grow)
            arrow(d, p0, p1, role, w_, a)
        elif ty == "arc":
            (x, y), = tf([(e["x"], e["y"])]); r = e["r"]
            d.arc([x - r, y - r, x + r, y + r], e.get("start", 0), e.get("end", 360), fill=c, width=w_)
        elif ty == "text":
            (x, y), = tf([(e["x"], e["y"])])
            txt(d, (x, y), e["text"], e.get("text_role", "label"), role, e.get("anchor", "mm"), e.get("maxw", 600), a)
        elif ty == "icon":
            (x, y), = tf([(e["x"], e["y"])])
            paste_icon(img, d, e["name"], x, y, e.get("size", 200), role, a, -deg if e.get("spin_with_rotate") else 0)
        if e.get("label"):
            lb = e["label"]
            (lx, ly), = tf([_pt(lb["at"])])
            txt(d, (lx, ly), lb["text"], lb.get("text_role", "small"), lb.get("role", "ink" if role != "track" else "track"),
                lb.get("anchor", "mm"), lb.get("maxw", 420), a)
    if p.get("illustrative"):
        illustrative(d)
    source(d, p.get("source"))

def s_answer(img, d, t, p, logo_path=None):
    """icon (optional), line (*markup* for the key words), sub, source, signoff (bool)."""
    y = 800
    if p.get("icon"):
        paste_icon(img, d, p["icon"], CX, 700, 200, "track", inn(t, 0))
        y = 930
    txt(d, (CX, y), p["line"], "answer", "ink", "mm", 920, inn(t, 0.05))
    if p.get("sub"):
        txt(d, (CX, y + 190), p["sub"], "label", "muted", "mm", 880, inn(t, 0.5))
    if p.get("signoff"):
        a = inn(t, 0.6)
        mk = mark(70, logo_path)
        if a > 0:
            img.paste(mk, (CX - mk.width // 2, 1120), mk)
        txt(d, (CX, 1225), p.get("signoff_text", "Follow for one bonus braincell per scroll"), "small", "muted", "mm", 880, a)
    else:
        source(d, p.get("source"))

V3 = dict(hook_object=s_hook_object, compare=s_compare, whole=s_whole, process=s_process,
          cross=s_cross, diagram=s_diagram, answer=s_answer)

# ---------- QA: layout check against platform guides ----------
def _hit(b, r):
    return not (b[2] <= r[0] or b[0] >= r[2] or b[3] <= r[1] or b[1] >= r[3])

def layout_issues(boxes):
    g = DS["platform_guides"]
    out = []
    for e in boxes:
        b = e["box"]
        for plat in ("youtube_shorts", "instagram_reels", "tiktok"):
            for zone, r in g[plat].items():
                if _hit(b, r):
                    out.append(f"{e['role']} '{e['text']}' overlaps {plat} {zone} UI")
        if e["role"] != "caption" and _hit(b, g["youtube_native_captions"]):
            out.append(f"{e['role']} '{e['text']}' sits in the YouTube native-caption band")
        if e["role"] not in ("caption", "source", "badge") and b[2] > L["essential_max_x"] and b[3] > 780:
            out.append(f"{e['role']} '{e['text']}' extends past x={L['essential_max_x']} (right-rail risk)")
        if e["size"] < T["source"]["min"]:
            out.append(f"{e['role']} '{e['text']}' is {e['size']}px (< {T['source']['min']}px phone minimum)")
    return sorted(set(out))

def guides_overlay(img):
    """Draw the estimated platform UI zones and the native-caption band (QA previews only, never in the video)."""
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    g = DS["platform_guides"]
    cols = {"youtube_shorts": (255, 60, 60, 60), "instagram_reels": (200, 80, 255, 50), "tiktok": (0, 230, 230, 50)}
    for plat, c in cols.items():
        for r in g[plat].values():
            d.rectangle(r, fill=c, outline=c[:3] + (200,), width=2)
    d.rectangle(g["youtube_native_captions"], outline=(255, 140, 0, 255), width=4)
    d.text((70, g["youtube_native_captions"][1] + 8), "YT native captions (est.)", font=F(26, "Bold"), fill=(255, 140, 0, 255))
    out = img.convert("RGBA"); out.alpha_composite(ov)
    return out.convert("RGB")
