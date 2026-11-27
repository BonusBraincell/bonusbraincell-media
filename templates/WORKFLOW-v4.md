# Bonus Braincell · Production workflow v4 (default from the 2026-11-30 slot; Nov 27–29 stay on v3 so EXP-02/06 finish clean)

v3 made every episode correct and safe to post. v4 makes each one **ours and different**: an editorial contribution we created, a narrative structure chosen for the subject, and at least one custom animated sequence that shows the mechanism. Brand stays recognizable through type, the mark lockup, yellow-as-focus and the caption style, not through one repeated layout.

Files: `check_episode.py` (editorial gate, run before render) · `world.py` (scene kit: environments, illustrated helpers, env-aware chrome) · `sfx.py` (procedural sound effects) · `render_episode.py` (`"workflow": "v4"` path: custom scenes, transitions, sound) · `make_cover.py` (`"v4": true` covers) · `preview_scene.py` (fast stills of custom scenes, no narration) · `../catalog/episodes.json` (our catalog for novelty checks) · worked examples in `../episodes/2026-12-0{2,3,4}_*/`.

## 1 · Why v4 (audit, Nov 26)
Twelve published episodes shared: one cover template (series pill, two-line headline, giant yellow number or two cards, white question pill, lockup) on every grid tile; the same navy dot stage with a small icon or boxes in the middle of empty space; frame 0.7 s repeating the cover headline; a "[do X], and [surprise]" opener in 6 of the last 8; a "doesn't X… it Y" or "So remember…" couplet ending in all 12; the same 6-beat skeleton; no sound design; one 0.15 s fade between every scene. Reach on Instagram fell to 5–9 views on 3 of the last 6 Reels, and YouTube's monetization policy names "content that looks like it's made with a template, with little to no variation across videos."

## 2 · The episode record (required; `spec.json` → `"record"`)
| Field | What it holds |
|---|---|
| `question` | The exact question, as a viewer would ask it |
| `audience_reason` | Why our audience (curious adults outside their own field) would care |
| `editorial_contribution` | `{type, statement}`: the thing we made. Types: concrete example · comparison/calculation from verified inputs · visual model · connection everyday ↔ system · labeled hypothetical · resolved contradiction/misconception · real dataset |
| `narrative_structure` | One of: journey · mystery_resolved_through_evidence · comparison_two_worlds · consequence_unfolding · myth_then_mechanism · countdown_or_timeline · calculation_reveal · build_up_from_parts · question_from_viewer |
| `animation_approach` | One of the eight below (+ optional `secondary_approach`) |
| `custom_scene` | One paragraph: the central sequence built for this explanation |
| `cover_composition` | `{type, layout, environment, text_amount, main_object}` |
| `sources_and_assumptions` | Pointer to the claim ledger + every assumption that affects a result |
| `asset_provenance` | Where every visual/audio element came from (code-drawn, font licenses, Kokoro, sfx.py, any third-party asset + license) |
| `similar_recent_episodes` | From `catalog/episodes.json`, with how this one differs |
| `render_review_status` | draft → rendered → qa_passed → published (+ notes) |

## 3 · Topic selection (both modes)
For every candidate write: exact question · why our audience cares · original contribution · best visual mechanism · sources needed · similar recent episodes (catalog). Reject a candidate if its contribution is only "a number card" or if it repeats a catalog premise with new nouns (e.g. a third IPO-mechanics episode in two weeks). Prefer a candidate whose visual mechanism we haven't used in the last 5 episodes.
- **AUTOPILOT:** news (72 h → 7 d), audience questions (Growth/comments.md), trends (vidIQ outliers as interest signals only; never copy a treatment), evergreen curiosities. Pick the one with the strongest question, two reliable sources and a mechanism we can animate.
- **PICK MODE:** take Rob's topic/question/URL and develop the strongest original treatment; offer 3 angles that differ in contribution and approach.
- **Backlog:** keep 5–7 fully researched episodes (record + ledger + script) so daily publishing never forces a thin one. The weekly review refills it.

## 4 · Animation approaches (choose by what the story needs)
| Approach | Use when | Built-in examples |
|---|---|---|
| SYSTEM_CUTAWAY | the answer is inside an object or system | `c_cabin`, `c_flow` (windows) |
| FOLLOW_THE_JOURNEY | one object/dollar/signal moves through parties or steps | nickel on a production line with a cost meter |
| COUNTERFACTUAL_MODEL | one condition changes (route closes, rate moves, engine stops) | label "illustration, not a prediction" |
| TWO_WORLDS | two scenarios side by side, changes synchronized | atom clock vs Earth clock (leap second) |
| SCALE_REVEAL | familiar ↔ unfamiliar scale, speed, quantity | 0.9 s → 1 hour on a labeled log axis |
| VISUAL_CASE_FILE | a question answered by assembling evidence | Comet case folder, exhibits 1–3 |
| MINIATURE_WORLD | a small illustrated environment carries the logic | paper-cutout street (Black Friday cover) |
| DATA_STORY | a verified dataset or labeled worked example | IERS leap-second staircase; to-scale cost bar |
Keep an approach when it serves a new story; never reuse a previous episode's scene sequence.

## 5 · Scene spec (every scene)
`"explain": {"understand", "objects", "change", "cause", "text"}`: what the viewer must understand · which objects are visible · what changes over time · what causes it · the on-screen text that's necessary. Plus `subject`, `changes` (timed to narration phrases), `environment` (optional per scene), `transition` (cut · dissolve · push_left · push_up · zoom_through; match it to the relationship: cut = same world continues, push = next step/exhibit, dissolve = shift of view, zoom_through = scale change), `sfx` for meaningful events only (stamp, clink, crack, tick, beep, register, paper, swoosh_up…; ≤ ~1 per 3 s).
Motion must show causation, sequence, scale, flow, accumulation, constraints or tradeoffs. Hold a diagram ≥ 1.2 s before changing it. Data graphics and geometry are exact (to-scale bars, real dates, real formulas); anything else that looks quantitative is labeled ILLUSTRATIVE / illustration / simplified model.

## 6 · Custom scenes (how to build)
Write `episodes/<date>_<slug>/scenes.py` with functions `fn(img, d, t, p, ctx)` (t = seconds into the scene, p = params with phrase times resolved, ctx = env colors, durations, `cover` flag). Use `world.py` helpers (`T`, `label`, `chip`, `glow`, `shadow`, `counter`, `seg`, `ease_*`, `zoom`, `path_at`) so text is registered for layout QA. Start from the three demos. Iterate with `python3 preview_scene.py spec.json /tmp/prev` (4 stills per scene, layout warnings) before the full render.
Environments (`design-system.json → environments`): navy_classic · mint_floor · case_file (light) · two_skies · blueprint · dusk_map · daylight (light). Add one when a story needs a new world; keep yellow = focus and the caption box unchanged.

## 6b · Pace, captions, music (v4.1, from the @everytypesorted read, 2026-11-26)
A visual change every 3-4 s (a new object, label, camera move or state), kinetic captions (`"caption_style": "kinetic"`), a procedural music bed (`"music"`) plus sound effects. Frame 0 shows the moving object and the question; a myth or contradiction is a strong opener when the topic has one. Rob approved the short format on 2026-11-26: 35–50 s, two posts a day (~12:30 PM and ~7:15 PM ET), trend-led topics (`Growth/trend-bank.md` in the OneDrive folder).

## 7 · Script and narration
Open on a specific question or situation; start answering by ~6 s. Build one causal explanation to a payoff in the structure chosen. Concrete examples, natural language, varied sentence length. **Retired as defaults** (check_episode warns): the "[do X], and [surprise]" opener, "So remember…", and the "X doesn't… It…" couplet ending. Endings rotate: an image to remember (nickel receipt) · an action for the viewer (trace the window) · a permission/consequence reveal (leap second) · a number to repeat · a question answered. Length: 35–50 s, never over 55 s (Rob, 2026-11-26, for reach; spec "duration_range": [30, 55]). One editorial voice; vary energy with per-scene `speed` and `...` beats. CTA stays "Follow for one bonus braincell per scroll." Banned phrases and no em dashes as before.

## 8 · Covers (v4)
`make_cover.py OUT/cover.png --spec cover.json --preview` with `"v4": true`. **Brand constants:** Inter Black headline with exactly one *yellow* phrase (highlighter band on light environments), the mark + BONUS BRAINCELL lockup bottom-left inside the 3:4 crop, the series name in small caps under it. **Variables:** environment, art (a function in the episode's scenes.py; often scene 1 itself = "living cover"), `layout` top/middle/bottom, `art_dy`, amount of text. Rotate composition types (object_hero · document_still_life · split_two_worlds · map_route · macro_closeup · scale_contrast · diagram_hero · miniature_world) so neighbours on the grid differ. Before posting, rebuild the 9-tile grid preview (last 6 published + next 3) and change any tile that repeats its neighbour's composition or environment.
**Platform controls (checked 2026-11-26):** vidIQ's Instagram Reel publisher and TikTok draft have no cover parameter, so frame 0 stays the cover (`--cover`, 0.5 s hold, then dissolve into scene 1). YouTube: the vidIQ YouTube destination accepts `thumbnailImageId` (verified channels only; a refusal doesn't fail the upload); YouTube's custom Shorts thumbnails rolled out in July 2026 to YPP creators, and custom thumbnails show on channel pages and search, not in the Shorts feed. Upload cover.jpg with `vidiq_upload_image` and pass it; keep frame 0 as the feed thumbnail.

## 9 · Order of work (daily)
1. Topic + record fields + claim ledger (fact-check pass 1). 2. Script (3 hook variants, retention gates). 3. `check_episode.py spec.json` → must PASS (fix FAILs; resolve or justify warnings in the run log). 4. Scenes: reuse/adapt a demo module or write new functions; `preview_scene.py`; fix layout warnings. 5. Cover (+ grid preview). 6. Fact-check pass 2 (fresh agent) on everything on screen. 7. `render_episode.py spec.json OUT --cover OUT/cover.png`. 8. QA (`qa-report.json` pass_, look at qa-sheet, 5 full frames incl. one per transition, listen to the sfx). 9. Package, update `catalog/episodes.json` (one entry), post, record.

## 10 · Platform guidance (official, checked 2026-11-26)
YouTube monetization: the "inauthentic content" policy (renamed from repetitious content on July 15, 2025; clarified July 2026) covers mass-produced, repetitive or template-looking content and "AI-generated content made with generic templates" without the creator's original insight. Our protection is the editorial record and custom scenes, not hiding tools. Monetization eligibility and recommendation performance are separate outcomes; nothing here guarantees either, an originality label, distribution or views.
Disclosure: YouTube requires the altered/synthetic setting for realistic content; our narration is a synthetic voice over non-realistic animation, so we keep the AI label on IG/TikTok and the "synthetic (AI) voice" line in every YouTube description (house rule, stricter than required). Third-party assets need a recorded license; sponsorships need the platforms' paid-partnership tools and "Ad" in captions.
