# Bonus Braincell · Design system v3 (default from 2026-11-21)

**This is the one shared design source for Autopilot and Pick Mode.** Values live in `design-system.json`; code in `design.py`; `render_episode.py` and `make_cover.py` read both. Change a value in the JSON, never in a visual. Repo `templates/` is the master; the OneDrive `Production/templates/` folder is a mirror.

Tagline: "Learning Beyond Your Day Job." Look: clean editorial, deep navy, electric yellow, bold Inter, the butterfly/brain/lightning mark.

## 1 · Rules every episode follows
1. **Yellow means "track this."** Use it only for the active step, the moving object or the newly revealed value. Everything else is white (ink), muted grey-blue or panel navy. One yellow focus at a time. A group can share yellow only if it's one idea (for example, the top 3 registries).
2. **Each story gets its own subject.** Scene 1 shows the episode's object or action (ship, card, plane, barrel), not a generic title card. The series stays recognizable through type, color and motion, not through a repeated layout.
3. **Units and qualifiers sit beside the thing they describe.** Write "~90 %" next to its baseline "0". Use "17.4 %" on its own legend row, not in a footnote. "Illustrative numbers" goes on screen as a badge whenever a number is an example.
4. **Captions carry the narration, labels name the parts, motion shows what changed.** If a label repeats the caption sentence, cut the label.
5. **Arrows only for real movement, sequence or flow.** Don't draw an arrow from "90 locked" to "10 for sale": those coexist, so show one proportional whole (`whole`). A later change gets its own `process` timeline.
6. **One meaningful change at a time.** Hold each important state at least `motion.hold_min` (1.2 s) before the next change.
7. **Compact brand.** One row at top left: mark + BONUS BRAINCELL + series in muted text. No pill, and nothing essential in the YouTube native-caption band (y 236–480).

## 2 · Exact settings (from design-system.json v3.0)
| Token | Value |
|---|---|
| Canvas | 1080 × 1920, 30 fps; cover held 0.5 s as frame 0 |
| bg / panel / line | #0A1E3E / #132C5A / #2B4475 (bg sampled from the logo) |
| track (yellow) / on_track | #F8D607 (sampled from the logo) / #0A1E3E |
| ink / muted / dim | #F4F6FB / #9AA8CC / #5F709B |
| cobalt | #0020D1 (from the swipe banner; brand accents only, never data) |
| Caption box | rgba(4, 10, 24, 0.70), radius 22, pad 30 × 16 |
| Type (Inter) | hook 92 ExtraBold, line height 1.06, min 64, 2 lines · kicker 48 ExtraBold · value 150 ExtraBold (min 80) · unit 44 Bold · label 40 Bold (min 34, 2 lines) · small 34 SemiBold · caption 56 Bold, line height 1.22, min 48, 2 lines · source 28 Medium (min 26) · badge 26 Bold · lockup 26 ExtraBold · answer 84 ExtraBold (min 58, 3 lines) |
| Layout | margins 72 · lockup y 172 (mark 46 px) · kicker y 540 · stage y 620–1250 (tall 500–1270) · source y 1268 · captions centered at y 1385, max width 700 (box stays inside y ~1290–1480) · essential text below y 760 stays inside x 120–920 |
| Strokes | line 6 · tracked 10 · outline 5 · arrow head 30 · radius 28 · icon stroke 22 px |
| Motion | ease cubic-out · enter 0.35 s · state change 0.5 s · hold ≥ 1.2 s · stagger 0.15 s · scene fade 0.15 s · motion opening push-in 0.9 s from 110 % |

**Platform guides (estimated, not verified against live previews):** Shorts top 0–160, bottom 1500+, right rail x 930+ / y 860–1620. Reels top 0–150, bottom 1530+, right x 950+ / y 1080–1680. TikTok top 0–180, bottom 1490+, right x 920+ / y 780–1560. YouTube native captions are estimated at y 236–480; the old series pill sat there and was overlapped on the satellites Short. Update `platform_guides` when a live preview is checked.

## 3 · Scene types (v3)
Pick by what the story needs. The IPO clock-and-order-book is the model: a graphic that changes as the process changes.

| Type | Use for | Key params |
|---|---|---|
| `hook_object` | Scene 1. The topic's object or action, readable with the sound off | `headline` (≤ 2 lines, `*yellow*` markup), `icon` (Lucide name), `icon_label`, `motion` slide/drop/rise/sway/spin/pulse/none, optional `action`, `result`, `result_icon`, `result_at` |
| `compare` | A number with its baseline, or two things side by side | `items` [{label, value, unit, note, icon, n, track}], `vs`, `bars`, `illustrative`, `source` |
| `whole` | Quantities that coexist (shares of one total) | `total`, `segments` [{label, n, value, track}], `shape` bar/grid, `illustrative`, `source` |
| `process` | One object or value carried through states (tap to pay: the same $6 through each step) | `states` [{label, sub, value}], `token` {icon, value}, `at` (one per state: seconds or a narration phrase), `layout` v/h, `flow` |
| `cross` | Boundaries: an object crosses and its state visibly changes (train + clock for time zones) | `left`, `right`, `boundary`, `icon`, `before`, `after`, `at` |
| `diagram` | Physical mechanism: what moves or changes | `elements` [{type rect/circle/line/arrow/arc/polygon/text/icon, role, fill, width, show, hide, track, move {by, at, dur}, rotate {from, to, at, dur, origin} (degrees, **positive = clockwise on screen**), label {text, at}}] in canvas px |
| `answer` | The payoff on screen; optional sign-off | `line` (`*yellow*`), `icon`, `sub`, `source`, `signoff` |
| `wing` | Aerodynamics: a wing cross-section in moving air, yellow lift arrow (added 2026-11-22) | `mode` board/aoa/deflect/inverted/symmetric/camber/myth/fact, `kicker`, `label`, `source`, timing `flip_at`, `grow_at`, `lift_at`, `roll_at`, `tilt_at`, `level_at`, `retilt_at` (phrases OK). Cover: `visual.type` "wing" with two items [label, flip, track] |

**Timing:** any `at`, `*_at`, `show`, `hide` or `track` value can be a phrase from that scene's narration ("rules go"); the renderer converts it to seconds. Prefer phrases, so changes land on the words.

**Icons:** `templates/icons/<name>.svg`: Lucide, 2,410 icons, ISC license (no attribution needed; note "Lucide icon" in sources-and-rights.md). Browse names at lucide.dev. Needs `pip install cairosvg`.

**Legacy visuals** (`clock`, `orbit`, `relay`, `sunpath`, `noonclock`, `tiles`, `converge`, `negative`, `mappin`, `build`, `hook`, `card`, `bars`, …) still render in the new colors and lockup, and the renderer warns when one is used. Use one only when it is the best topic-specific mechanism (for example, `clock` for an order book, `orbit` for orbits). Never use `hook` (static title card) for scene 1 on a motion-opening day.

## 4 · Fallbacks
- **Long labels:** text shrinks to its role minimum, then wraps to the role's max lines. If it still doesn't fit, it's cut and QA fails ("text shrunk to minimum and cut"). Shorten the label.
- **No icon for the subject:** pick the closest Lucide icon. A missing name draws a labeled outline box and fails QA (`missing_icons`).
- **Footage or imagery:** only rights-cleared images (public domain, CC with attribution recorded in sources-and-rights.md, or your own). Put labels on a panel, never directly over a busy image. No photos of real people.
- **Diagram needs more space:** drop the kicker and use the tall stage (y 500–1270), or split it into two scenes with one change each.
- **Busy beat:** if a beat needs more than ~3 labels, split it.

## 5 · Required output per episode (both modes)
`render_episode.py spec.json OUT --cover OUT/cover.png` always writes:
- `video.mp4`, `captions.srt`, `images/`
- **`scene-plan.md` + `scene-plan.json`**: per beat: start/end, narration, timed caption chunks, scene type, main visual subject, labels/values/units/sources, what changes and when, asset source, layout-check notes. Every scene in the spec must have `subject` and `changes` (the renderer warns if not).
- **`qa-report.json`**: duration, cover-first, layout issues against all three platforms' guides and the native-caption band, phone-minimum type sizes, missing icons, warnings, `pass_`.
- **`qa-sheet.png`**: phone-size frames (cover, 0.6 s, each beat) with the platform guides drawn on.

## 6 · Final checks before a package is marked ready (both modes)
1. `qa-report.json` → `pass_: true` (a duration over 61 s and at most 90 s, cover first, 0 layout issues, 0 missing icons). Fix and re-render otherwise.
2. Open `qa-sheet.png` and confirm: hook object identifiable with the sound off; captions and essential labels legible at phone size; yellow marks the one thing to track; the main graphic shows the mechanism (not just a number card); nothing important under the guides.
3. Open the cover crops (`cover_crops.png`): headline whole in the 3:4 crop, one big visual, no dead space.
4. Every on-screen number, label and source note is in the claim ledger (sources-and-rights.md).
5. Copy `scene-plan.md`, `qa-report.json` and `qa-sheet.png` into the package.
