#!/usr/bin/env python3
"""Preview custom v4 scenes without narration: renders chosen times of each scene to PNGs (fast iteration).
Usage: python3 preview_scene.py spec.json OUT_DIR [scene_index ...]  (times: 0, 25%, 50%, 85% of an estimated duration)
"""
import sys, os, json, importlib.util
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design as DZ, world as WD
from PIL import Image, ImageDraw
spec_path, out = sys.argv[1], sys.argv[2]
spec = json.load(open(spec_path)); os.makedirs(out, exist_ok=True)
mp = os.path.join(os.path.dirname(os.path.abspath(spec_path)), spec.get("scene_module", "scenes.py"))
ms = importlib.util.spec_from_file_location("episode_scenes", mp); mod = importlib.util.module_from_spec(ms); ms.loader.exec_module(mod)
idx = [int(x) for x in sys.argv[3:]] or range(len(spec["scenes"]))
for i in idx:
    sc = spec["scenes"][i]
    words = len(sc["tts"].split()); dur = words / 2.7 + 0.6
    p = dict(sc.get("params", {})); p["_dur"] = dur
    # crude phrase timing: proportional to characters
    def conv(v):
        if isinstance(v, str):
            k = sc["tts"].lower().find(v.lower()); return 0.15 + (dur - 0.6) * max(0, k) / max(1, len(sc["tts"]))
        return v
    for k in list(p):
        if k.endswith("_at") or k == "at":
            p[k] = [conv(x) for x in p[k]] if isinstance(p[k], list) else conv(p[k])
    envname = sc.get("environment", spec.get("environment")); E = WD.env(envname)
    frames = []
    for u in (0.02, 0.3, 0.6, 0.95):
        t = u * dur
        DZ.reg_reset()
        img = WD.background(envname); d = ImageDraw.Draw(img)
        r = getattr(mod, p["fn"])(img, d, t, p, dict(env=E, dur=dur, gt=t, total=80, scene=i, fps=30, spec=spec))
        if isinstance(r, Image.Image): img = r; d = ImageDraw.Draw(img)
        WD.chrome(img, d, spec["series"], 0.4, E)
        DZ.caption(img, "Sample caption sits here for layout", ())
        issues = DZ.layout_issues(DZ.REG["text"])
        if issues: print(f"scene {i+1} t={t:.1f}:", issues[:4])
        frames.append(img.resize((360, 640)))
    sheet = Image.new("RGB", (360 * 4 + 50, 660), (20, 20, 24))
    for k, f in enumerate(frames): sheet.paste(f, (10 + k * 370, 10))
    sheet.save(os.path.join(out, f"scene{i+1:02}_{p['fn']}.png"))
print("ok")
