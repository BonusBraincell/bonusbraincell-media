> **Master copy lives in GitHub: BonusBraincell/bonusbraincell-media/templates/.** OneDrive reverted edited templates on Nov 16, so daily runs always pull templates from the repo and push any template change back there. The copy in this folder is a mirror.

# Production templates

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
`pip install kokoro-onnx` and download the two model files into a `tts_dir` (default `/home/claude/tts`):
- `https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx` → `kokoro.onnx`
- `https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin` → `voices.bin`
Also needs ffmpeg, Pillow, numpy and the Inter font (all present in the Claude cloud workspace on 2026-11-15).

## Visual types available in the renderer
`hook` (title + two tags) · `offer` (two boxes → tag) · `rows` (table rows; optional `note`) · `alloc` (tile grid split) · `clock` (clock + order bin) · `auction` (two crossing curves) · `pop` (tag → tag + big %) · `bars` (two stat bars + source) · `payoff` (two-line takeaway) · `cta` (logo + line) · `card` (one big card: header, giant value, sub, optional note) · `mappin` (pipelines converging on a hub pin + tanks; label, sub) · `tiles` (100 tiles, 99 fade, 1 stays; big line, source) · `converge` (two price lines meeting at expiration; l1, l2, end_label, note) · `negative` (price line falling through $0; value, label, source). Added 2026-11-16. New visual types get added to `VISUALS` in `render_episode.py`; keep the navy/yellow palette and the same chrome and caption style.

## House format (every video)
- 1080×1920, 30 fps, H.264 + AAC, loudness −14 LUFS, **65–90 s (must be over 60 s for TikTok Creator Rewards)**. About 175–230 narrated words at the house voice speed.
- Frame 0 = the designed cover (`--cover`).
- Top chrome: progress bar, logo slot, BONUS BRAINCELL, series pill.
- Visual zone y 400–1300. Captions centered at y≈1420, white on dark pill, ≤28 characters per chunk.
- Mark illustrative numbers on screen. One source line on any real statistic.
- End with a repeatable line, then the CTA "Follow for one bonus braincell per scroll."


## Caption chunking (Nov 16)
Burned-in captions follow sentences and clauses, up to two lines (~42 characters, max ~56), never split abbreviations like U.S., never end on a weak word (at, the, of…), and never leave a one-word orphan.

## Voice variation (Script System v2, Nov 16)
The host voice stays `af_heart` (brand recognition). Variety comes from three levers, set per scene in the episode spec:
- `"speed"`: pacing per beat. Hook 1.10–1.12, mechanism 1.04–1.06, example 1.08, payoff line 1.00–1.02 (slower so it lands). Clamped to 0.9–1.2.
- `"voice"`: a second Kokoro voice for a quoted line only (a myth "people say…", a viewer question, a historical quote). Use `am_michael` or `bf_emma`; never more than 2 scenes per episode, and never for the payoff line.
- Sentence rhythm in the script itself: mix one short punch line (≤6 words) into every 2–3 longer lines.
Omit both keys and the scene uses the spec-level `voice`/`speed` as before.
