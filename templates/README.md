> **Master copy lives in GitHub: BonusBraincell/bonusbraincell-media/templates/.** OneDrive reverted edited templates on Nov 16, so daily runs always pull templates from the repo and push any template change back there. The copy in this folder is a mirror.

# Production templates

> **Workflow v4 is the default from the 2026-11-30 slot (Autopilot and Pick Mode).** Read `WORKFLOW-v4.md` first: episode record, narrative structures, the eight animation approaches, custom scenes (`world.py`, episode `scenes.py`), v4 covers, the editorial gate (`check_episode.py`) and platform guidance. Worked examples: `../episodes/`. v3 below still applies inside v4.

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

## Voice variation (rotating narrator from 2026-11-23)
Each episode gets a different narrator from the 21 Kokoro voices in `voices.json` (Rob, Nov 22): index = days since `start_date` mod 21, from the spec's `slot_date` (or the post_id date). Repeats every 21 days. Leave spec-level `"voice"` out (or `"rotation"`); an explicit voice name overrides. The narrator is recorded in `qa-report.json` → `audio.narrator`; copy it into `post.json` as `narrator`.
- `"speed"` per scene: pacing per beat. Hook 1.10–1.12, mechanism 1.04–1.06, example 1.08, payoff line 1.00–1.02. Clamped to 0.9–1.2. Voices differ in natural rate (~3.8–4.8 s for the same line), so check the length warning and add or trim a line rather than pushing speed.
- Scene `"voice": "quote"`: a quoted line only (myth, viewer question, historical quote) is read by `audio.quote_voice` (next voice of the opposite gender). Max 2 scenes; never the payoff line.
- Sentence rhythm in the script itself: mix one short punch line (≤6 words) into every 2–3 longer lines.
Every voice is still synthetic: AI label and the "synthetic (AI) voice" description line stay on. Voice sampler: `Production/pilots/2026-11-22_audio-v1/narrator-sampler.mp3` (all 21, in rotation order).

## Cover card fit (Nov 21)
make_cover.py now fits each tag card's value to the card width minus 150 px, so long words no longer touch the between-circle.

## wing scene type (2026-11-22)
v3 `wing` (design.py `s_wing`): NACA-style wing cross-section in dashed moving air; yellow = lift. Modes board, aoa, deflect, inverted, symmetric, camber, myth, fact. Cover `visual.type: "wing"` draws two symmetric sections (both tilted) with lift arrows. First used in BB-20261122-008.

## Audio direction v1 (2026-11-22)
Goal: narration that sounds recorded, not pasted. All of it is subtle; the AI label and the AI-voice line stay on every post.
- **Varied pauses (automatic):** each sentence is synthesized separately and the gap after it depends on its ending: `.` 0.20–0.38 s, `?` 0.36–0.46 s, `...` 0.45–0.60 s, `!` 0.24–0.32 s, plus 0.06 s after a short punch line (≤6 words). Scene tails vary 0.28–0.46 s, 0.55 s before a `payoff`/`answer` scene. Seeded by `post_id`, so re-renders match. Per-scene override: `"pause_after": 0.5`.
- **Room-tone bed (automatic):** a synthesized quiet-room floor (pink noise, no hiss, slow drift; no downloaded audio, so no license to track) under the whole video at `"room_tone_db": -50` (dBFS RMS). `null` turns it off. Pauses never hit digital zero.
- **Breaths (opt-in, max 2):** `[inhale]` in a scene's `tts` inserts a soft 0.34 s inhale ~23 dB under the speech peak. Put it only before the longest sentence of the script. Markers are stripped from captions and timing phrases.
- **Script punctuation is direction:** `...` = a held beat before a reveal, `?` = a real question pause, short sentences = punch. Use line-level variety, not uniform periods.
- **Voice blend (available, off):** spec `"voice": {"af_heart": 0.8, "af_bella": 0.2}` blends Kokoro styles. Not used; the narrator rotates instead. No pitch or tempo shifting on top of the house speed.
- **QA:** `qa-report.json` → `audio` block: `longest_digital_zero_s` (should be 0), `floor_dbfs_p5` (≈ −50), breaths, per-scene gaps and tails. A zero run over 0.05 s with room tone on is a warning.


## Workflow v4 additions (2026-11-26)
- `"workflow": "v4"` in a spec turns on: `"visual": "custom"` scenes from the episode's `scenes.py` (`params.fn`), per-scene `"environment"`, `"transition"` (cut, dissolve, push_left, push_up, zoom_through; scene 1 may dissolve from the cover), `"sfx"` cues (`sfx.py`), `"explain"` fields in scene-plan.md, and the `"record"` block in scene-plan.md / qa-report.json.
- `"caption_style": "kinetic"`: burned-in captions as 1-3 word chunks (84 px Inter Black, numbers in yellow, 0.12 s pop-in); captions.srt keeps full phrases.
- `"music": {"mood": "curious|tense|bright", "bpm": 96, "peak_db": -30}`: procedural music bed (no samples, no license) under narration.
- Narration cache in `OUT/_work/tts_*.wav`: re-renders after visual fixes don't re-synthesize.
- `make_cover.py` with `"v4": true`: episode art + fixed brand layer (see WORKFLOW-v4 §8).
- `check_episode.py spec.json` before every render; `preview_scene.py spec.json /tmp/prev` while building scenes.
