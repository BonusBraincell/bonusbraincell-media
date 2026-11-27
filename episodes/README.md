# Workflow v4 pilot · audit, changes, demo episodes (2026-11-26)

## 1 · Audit (what I inspected and what it shows)
**Inspected:** all 12 published videos and covers in `posts/` (frames at 0.7, 3, 15, 30, 50 s, and the 12 covers as one grid), the repo templates (render_episode.py, make_cover.py, design.py, design-system.json, DESIGN.md, README.md, voices.json), the OneDrive workflow docs (START HERE, PROJECT INSTRUCTIONS, Strategy/04 and 08, Automation/recurring-tasks.md, Calendar/content-log.csv, Growth/experiment-log.md, post-metrics.csv), all 12 published caption files (full narration), the live daily scheduled task, and current analytics (vidIQ: Instagram owner insights for 12 Reels, YouTube Shorts list, TikTok public counts).
**Watched vs inferred:** I did not play the YouTube channel page in a browser; I inspected our own rendered video files frame by frame and read every narration track (captions.srt), so the visual and script findings come from the actual published files. Platform-side behaviour (how the feed crops or ranks) is inferred from metrics and official help pages.

**Sources of repetition found**
| Where | What repeats | Evidence |
|---|---|---|
| Covers | One layout on every tile: yellow series pill, 2-line white/yellow headline, giant yellow number *or* two cards, white question pill, lockup, navy glow | 12/12 covers; 7 are big-number cards, 4 two-card |
| Opening frame | Frame 0.7 s repeats the cover headline as text over the same navy | 12/12 |
| Stage | Navy dot background, small Lucide icon or rounded boxes floating in empty space, kicker text above, caption box below | every scene of every episode |
| Visual vocabulary | Infographic primitives (process lists, compare cards, tag cards), not the object or system itself; the IPO clock and the wing were the exceptions | scene keyframes |
| Narration opener | "[Do X], and [surprise]" (Paint…/Stretch…/Launch…/Import…/Tilt…/Tap…) | 6 of the last 8 |
| Narration ending | "X doesn't… It…" / "The A is… The B is…" couplet, "So remember…" | 12/12 endings, 2 with "So remember" |
| Structure | The same 6-beat skeleton (hook, problem, 3 ideas, line, CTA) for every subject | Strategy/04, all scripts |
| Loop lines | "So how/what…?" rhetorical questions | most episodes |
| Transitions / sound | One 0.15 s fade between all scenes; no sound design | renderer |
| Topics | Two IPO-mechanics episodes in 5 days; oil/tariff/strait and ships twice in the plan | content-log |

**What the numbers say (measured):** IG median 3-s skip ≈ 82.5%, median watched ≈ 8%, 0 shares/saves on 906 views; three Reels stalled under 20 views (the trigger to check IG Account Status). TikTok flat at 74–112 views each, zero interactions. YouTube 5–181 views, top three are aviation/engineering. **Hypothesis (not proven):** the grid and first seconds read as one repeated template, which fits both the skip rate and YouTube's "inauthentic content" wording.

## 2 · What changed (implemented)
- `templates/WORKFLOW-v4.md`: the rules (record fields, 9 structures, 8 animation approaches, scene spec, covers, platform guidance).
- `templates/world.py`: scene kit: 7 environments (navy_classic, mint_floor, case_file, two_skies, blueprint, dusk_map, daylight), env-aware chrome, labels with leader lines registered for QA, shadows, glows, counters, camera zoom, path motion.
- `templates/sfx.py`: 15 synthesized sound effects (no samples/licenses), mixed under narration.
- `templates/render_episode.py`: `"workflow": "v4"` path: custom illustrated scenes from the episode's scenes.py, per-scene environments, transitions (cut, dissolve, push_left, push_up, zoom_through, cover→scene dissolve), sound cues timed to narration phrases, narration cache (re-renders after visual fixes skip TTS), v4 record and "explain" fields in scene-plan.md and qa-report.json. v3 specs render exactly as before.
- `templates/make_cover.py`: `"v4": true` covers: episode art (often scene 1 itself) + fixed brand layer; layouts top/middle/bottom; `art_dy`.
- `templates/check_episode.py`: editorial gate (record completeness, contribution strength, banned phrases, retired opener/ending patterns, explain fields, at least one custom scene, novelty vs catalog).
- `templates/preview_scene.py`: 4 stills per custom scene with layout warnings, no narration (fast iteration).
- `catalog/episodes.json`: all 12 published episodes retro-tagged (premise, structure, approach, cover composition, opener/ending pattern, environment) + the 3 demos.
- Daily scheduled task prompt rewritten for v4 (from the Nov 30 slot; Nov 27–29 stay v3 so EXP-02/06 finish clean). Strategy/04 and Growth/experiment-log.md updated.

## 3 · Demo episodes (rendered, QA pass)
| Slot | Episode | Structure | Approach | Environment | Narrator | Length |
|---|---|---|---|---|---|---|
| Dec 2 | Why are airplane windows rounded? | mystery resolved through evidence | VISUAL_CASE_FILE + SYSTEM_CUTAWAY | case_file (paper desk) | bm_fable | ~86 s |
| Dec 3 | Why are clocks dropping the leap second? | two worlds | TWO_WORLDS + DATA_STORY + SCALE_REVEAL | two_skies | af_kore | ~88 s |
| Dec 4 | Why does a nickel cost 13 cents to make? | journey | FOLLOW_THE_JOURNEY + DATA_STORY | mint_floor | am_onyx | ~85 s |
Each folder: spec.json (record + scenes), scenes.py, cover.json, sources-and-rights.md (claim ledger), post-copy.md. Rendered packages (video, cover, captions, scene plan, QA) are in OneDrive `Production/pilots/2026-11-26_workflow-v4/`. Status: `render_review_status: qa_passed (pending day-of fact-check)`; the daily task re-runs fact-check pass 2 on its slot before posting.

## 4 · Nine-cover grid
`_cover-previews/` holds concept covers for Nov 27–Dec 1 and Dec 5; with the three demos they make the 9-tile preview (`grid-next9.png`, `before-after.png`). The six non-demo covers are concepts: their final art comes from each episode's own scenes.py when it's made.
