> **Master copy lives in GitHub: BonusBraincell/bonusbraincell-media/templates/.** OneDrive reverted edited templates on Nov 16, so daily runs always pull templates from the repo and push any template change back there. The copy in this folder is a mirror.

# Production templates

> **Design system v3 is the default from 2026-11-21 (Autopilot and Pick Mode).** Read `DESIGN.md` first. It holds the rules, the v3 scene types (`hook_object`, `compare`, `whole`, `process`, `cross`, `diagram`, `answer`), the fallbacks and the final checks. All values live in `design-system.json`, the code in `design.py`, the logo in `brand/mark.png` (used automatically; `--logo` is optional) and the icons in `icons/` (Lucide, ISC). Working example: `episode-spec-EXAMPLE-v3-flags.json` + `cover-spec-EXAMPLE-v3-flags.json`. Every render also writes `scene-plan.md/.json`, `qa-report.json` and `qa-sheet.png`; a package is ready only when `qa-report.json` shows `"pass_": true`.

| File | Use |
|---|---|
| `render_episode.py` | **Make the cover first, then pass `--cover OUT/cover.png`** so the cover is the video's first frame (0.5 s); Instagram and TikTok use frame 0 as the thumbnail. Renders a finished episode from a spec: Kokoro narration, 1080×1920 30 fps frames, burned-in captions, `video.mp4`, `captions.srt`, `images/` keyframes. Run: `python3 render_episode.py spec.json OUT_DIR --logo ../../Settings/brand/logo.png` |
| `make_cover.py` | **Cover v2 (thumbnail).** Fills the 3:4 grid crop: big headline, one big visual, kicker pill, brand row. Run: `python3 make_cover.py OUT/cover.png --spec cover.json --logo ../../Settings/brand/logo.png --preview`. Example specs: `cover-spec-EXAMPLE-BB-20261116-001.json` (tags), `cover-spec-EXAMPLE-BB-20261116-002.json` (big number); preview: `cover-v2-preview.png` |
| `episode-spec-EXAMPLE-BB-20261116-001.json` | Working example spec (Episode 1) |
| `episode-spec-template.json` | Blank spec to copy |
| `script-template.md` | Editorial template: question, payoff, beats, sources |
| `post-copy-template.md` | Caption / title / description template |
| `sources-and-rights-template.md` | Claims table + asset rights |
| `post-schema.json` | Shape of `post.json` handoff |

## Renderer requirements (one-time, in the cloud workspace)
`pip install kokoro-onnx cairosvg` and download the two model files into a `tts_dir` (default `/home/claude/tts`):
- `https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx` → `kokoro.onnx`
- `https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin` → `voices.bin`
Also needs ffmpeg, Pillow, numpy and the Inter font (all present in the Claude cloud workspace on 2026-11-15).

## Visual types available in the renderer
**v3 (use these):** see `DESIGN.md` §3. **Legacy (still render, now in v3 colors and lockup; use only when the best topic-specific mechanism):**
`hook` (title + two tags) · `offer` (two boxes → tag) · `rows` (table rows; optional `note`) · `alloc` (tile grid split) · `clock` (clock + order bin) · `auction` (two crossing curves) · `pop` (tag → tag + big %) · `bars` (two stat bars + source) · `payoff` (two-line takeaway) · `cta` (logo + line) · `card` (one big card: header, giant value, sub, optional note) · `mappin` (pipelines converging on a hub pin + tanks; label, sub) · `tiles` (100 tiles, 99 fade, 1 stays; big line, source) · `converge` (two price lines meeting at expiration; l1, l2, end_label, note) · `negative` (price line falling through $0; value, label, source). Added 2026-11-16. `relay` (a message/packet travelling down a chain of boxes, optionally coming back: kicker, nodes, packet, back, highlight, note; added 2026-11-17). `sunpath` (sun crossing a row of towns, each town's noon lighting up: kicker, towns, label, note) · `zones` (vertical bands snapping into place: kicker, bands, big, note) · `noonclock` (clock reaches 12, is set back, reaches 12 again: kicker, first, back, second, t1-t3, note); `hook` takes an optional `note`. Added 2026-11-18. `orbit` (Earth diagrams: mode `station` = station circling with sideways + gravity arrows, drawn from frame 0; `cannon` = Newton's cannon with `shots` speed fractions (1.0 = orbit) and `drawn` already-complete shots; `together` = station and astronaut falling in sync; `drag` = orbit sinks then a reboost lifts it, `drag_label`/`boost_label`; all take kicker, label, note). Added 2026-11-20. `card` takes optional `sub_size` (default 46) for long sub lines (2026-11-21). `build` (action-first build-up hook for EXP-06: an object box already sliding in at frame 0, an action arrow, the result popping in by ~1.2 s: kicker, obj, action, result, note; added 2026-11-20). New visual types get added to `VISUALS` in `render_episode.py`; keep the navy/yellow palette and the same chrome and caption style.

## House format (every video)
- 1080×1920, 30 fps, H.264 + AAC, loudness −14 LUFS, **65–90 s (must be over 60 s for TikTok Creator Rewards)**. About 175–230 narrated words at the house voice speed.
- Frame 0 = the designed cover (`--cover`), held 0.5 s.
- `"opening"` (spec top level, EXP-06): `"static"` (default) = cover, then scene 1 as drawn. `"motion"` = cover, then scene 1 opens with a 0.9 s push-in and must use a moving visual (`build`, `orbit`, `relay`, `sunpath`…), never the static `hook` card. Which one to use each day is set in Calendar/content-log.csv notes ("EXP-06 opening: motion/static").
- Top chrome (v3): progress bar + one compact row at top left (mark, BONUS BRAINCELL, series in muted text). No series pill.
- Stage y 620–1250, kicker y 540, captions centered at y 1385 (max width 700). Essential text below y 760 stays inside x 120–920. Exact values: `design-system.json`.
- Mark illustrative numbers on screen. One source line on any real statistic.
- End with a repeatable line, then the CTA "Follow for one bonus braincell per scroll."


## Caption chunking (Nov 16)
Burned-in captions follow sentences and clauses, up to two lines (~42 characters, max ~56), never split abbreviations like U.S., never end on a weak word (at, the, of, you, than, what…) or a possessive ("store's"), and never leave a one-word orphan. Nov 20: a `|` in a scene's caption forces a chunk break there (never shown), and the two-line balancer avoids a top line ending on a weak word and one-word lines.

## Voice variation (Script System v2, Nov 16)
The host voice stays `af_heart` (brand recognition). Variety comes from three levers, set per scene in the episode spec:
- `"speed"`: pacing per beat. Hook 1.10–1.12, mechanism 1.04–1.06, example 1.08, payoff line 1.00–1.02 (slower so it lands). Clamped to 0.9–1.2.
- `"voice"`: a second Kokoro voice for a quoted line only (a myth "people say…", a viewer question, a historical quote). Use `am_michael` or `bf_emma`; never more than 2 scenes per episode, and never for the payoff line.
- Sentence rhythm in the script itself: mix one short punch line (≤6 words) into every 2–3 longer lines.
Omit both keys and the scene uses the spec-level `voice`/`speed` as before.

## Cover card fit (Nov 21)
make_cover.py now fits each tag card's value to the card width minus 150 px, so long words no longer touch the between-circle.
