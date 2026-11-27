#!/usr/bin/env python3
"""Bonus Braincell editorial gate v4 (2026-11-26). Run BEFORE rendering; the daily task stops on FAIL.

Usage: python3 check_episode.py spec.json [--catalog ../catalog/episodes.json] [--out report.json]

Checks the episode record (the fields that make an episode ours), the script against our recurring patterns,
the scene specs against "animation must explain", and novelty against the last episodes in the catalog.
Exit code 0 = PASS (warnings allowed), 1 = FAIL. Writes a JSON report.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REQUIRED = ["question", "audience_reason", "editorial_contribution", "narrative_structure", "animation_approach",
            "custom_scene", "cover_composition", "sources_and_assumptions", "asset_provenance",
            "similar_recent_episodes", "render_review_status"]
CONTRIB_TYPES = ["example", "comparison", "calculation", "visual model", "connection", "hypothetical",
                 "contradiction", "misconception", "dataset", "two-worlds", "journey"]
BANNED = ["welcome back", "in today's video", "let's dive in", "buckle up", "here's the thing", "the craziest part",
          "game-changer", "game changer", "delve", "in today's world", "it's important to note", "at the end of the day",
          "you won't believe", "did you know", "mind-blowing", "let that sink in"]
# recurring patterns found in the Nov 15-26 catalog (audit): flagged so they are used on purpose, not by habit
OPENER_PATTERNS = {
    "everyday_action_and": r"^(paint|stretch|launch|import|tilt|tap|buy|send|put|drop|pour|flip|hold)\b[^.?!]*,\s*and\b",
    "did_you_know": r"^did you know",
}
ENDING_PATTERNS = {
    "so_remember": r"\bso remember\b",
    "contrast_couplet": r"\b(doesn't|isn't|don't|aren't|wasn't)\b[^.?!]{0,60}[.?!]+\s*(it|they|it's|they're)\b",
    "noun_then_noun_couplet": r"^the [a-z ]+ (is|was) [a-z ]+\. the [a-z ]+ (is|was) [a-z ]+\.",
}

def words(s):
    return len(re.findall(r"[A-Za-z0-9'’.,-]+", s))

def main():
    a = sys.argv
    spec_path = a[1]
    cat_path = a[a.index("--catalog") + 1] if "--catalog" in a else os.path.join(HERE, "..", "catalog", "episodes.json")
    out = a[a.index("--out") + 1] if "--out" in a else os.path.join(os.path.dirname(os.path.abspath(spec_path)), "editorial-check.json")
    spec = json.load(open(spec_path))
    cat = json.load(open(cat_path)) if os.path.exists(cat_path) else {"episodes": []}
    fails, warns, notes = [], [], []
    rec = spec.get("record", {})

    # 1) record completeness
    for k in REQUIRED:
        if not rec.get(k):
            fails.append(f"record.{k} is missing")
    ec = rec.get("editorial_contribution") or {}
    if isinstance(ec, dict):
        if len(ec.get("statement", "")) < 120:
            fails.append("editorial_contribution.statement is too thin (< 120 chars): say exactly what we add (example, calculation, model, connection, resolved contradiction)")
        if not any(t in ec.get("type", "").lower() for t in CONTRIB_TYPES):
            warns.append(f"editorial_contribution.type '{ec.get('type')}' is not one of {CONTRIB_TYPES}")
    if rec.get("animation_approach") and rec["animation_approach"] not in cat.get("approaches", [rec["animation_approach"]]):
        fails.append(f"animation_approach '{rec['animation_approach']}' is not in the approach family {cat.get('approaches')}")
    if rec.get("narrative_structure") and rec["narrative_structure"] not in cat.get("structures", [rec["narrative_structure"]]):
        warns.append(f"narrative_structure '{rec['narrative_structure']}' is new; add it to catalog structures if it's intentional")

    # 2) script
    scenes = spec["scenes"]
    tts = [s["tts"] for s in scenes]
    full = " ".join(tts)
    n = words(full)
    notes.append(f"{n} narrated words")
    if n < 175 or n > 240:
        warns.append(f"{n} words: target 175-230 (65-90 s)")
    low = full.lower()
    for b in BANNED:
        if b in low:
            fails.append(f"banned phrase: '{b}'")
    if "—" in full or " -- " in full:
        fails.append("em dash in narration (house style)")
    first = tts[0].strip().lower()
    for name, rx in OPENER_PATTERNS.items():
        if re.search(rx, first):
            warns.append(f"opener uses the recurring '{name}' pattern; vary it unless it is clearly the best opening")
    last = tts[-1].lower()
    payoff = re.split(r"follow for one bonus braincell", last)[0]
    for name, rx in ENDING_PATTERNS.items():
        if re.search(rx, payoff.strip()):
            warns.append(f"payoff uses the recurring '{name}' ending; most recent episodes ended this way")
    if words(tts[0]) > 30:
        warns.append("scene 1 narration is over 30 words; the question/situation should land in ~2 s and the answer start by ~6 s")

    # 3) animation explains: each scene needs explain fields; custom/v3 types only; illustrative labels
    for i, s in enumerate(scenes, 1):
        ex = s.get("explain", {})
        for k in ("understand", "objects", "change", "cause", "text"):
            if not ex.get(k):
                fails.append(f"scene {i}: explain.{k} missing (what the viewer must understand / objects / what changes / why / on-screen text)")
        if s.get("visual") in ("hook", "card", "payoff", "cta"):
            warns.append(f"scene {i}: legacy static visual '{s['visual']}'")
    if not any(s.get("visual") == "custom" for s in scenes):
        fails.append("no custom scene: every episode needs at least one central sequence built for its own explanation")
    if re.search(r"\b(say|imagine|suppose|for example|illustrative)\b", low) and "illustrative" not in json.dumps(scenes).lower() \
            and "hypothetical" not in json.dumps(scenes).lower():
        warns.append("narration uses a hypothetical; make sure the screen labels it ILLUSTRATIVE / hypothetical")

    # 4) novelty vs catalog (last 7 by date, excluding this episode)
    eps = [e for e in cat.get("episodes", []) if e.get("title") != spec.get("title")]
    eps.sort(key=lambda e: e.get("date", ""))
    recent = eps[-7:]
    last2 = eps[-2:]
    for k in ("animation_approach", "narrative_structure", "cover_composition"):
        mine = rec.get(k, {}).get("type") if isinstance(rec.get(k), dict) else rec.get(k)
        if mine and any(e.get(k) == mine for e in last2):
            warns.append(f"{k} '{mine}' repeats one of the last two episodes; keep it only if it clearly serves this story")
    if rec.get("cover_composition"):
        cc = rec["cover_composition"]
        if isinstance(cc, dict) and cc.get("environment") and spec.get("environment") and cc["environment"] != spec["environment"]:
            notes.append("cover environment differs from the episode environment (fine if intentional)")
    prem = set(w.lower() for w in re.findall(r"[a-z]+", spec.get("title", "").lower()) if len(w) > 3)
    sim = []
    for e in recent + eps[:-7]:
        overlap = prem & set(" ".join(e.get("premise", [])).split())
        if len(overlap) >= 1:
            sim.append(f"{e['id']} {e['title']} (shared: {', '.join(sorted(overlap))})")
    if sim:
        notes.append("possible similar episodes: " + "; ".join(sim[:5]))
        if not rec.get("similar_recent_episodes"):
            fails.append("similar episodes exist; list them in record.similar_recent_episodes and say how this one differs")
    series_last3 = [e.get("series") for e in eps[-3:]]
    if series_last3.count(spec.get("series")) >= 3:
        warns.append(f"series '{spec.get('series')}' was used in each of the last 3 episodes")

    rep = dict(spec=os.path.basename(spec_path), title=spec.get("title"), verdict="FAIL" if fails else "PASS",
               fails=fails, warnings=warns, notes=notes)
    json.dump(rep, open(out, "w"), indent=1)
    print(json.dumps(rep, indent=1))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
