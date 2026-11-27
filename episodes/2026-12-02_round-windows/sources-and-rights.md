# Sources and rights · Why are airplane windows rounded? (v4 demo, slot 2026-12-02)
Checked 2026-11-26. Re-open every source on the day (fact-check pass 2, fresh agent) before posting.

## Claim ledger
| # | Claim (where) | Source | Support |
|---|---|---|---|
| 1 | Two Comets broke apart in flight in 1954, three months apart: 10 Jan 1954 off Elba (G-ALYP), 8 Apr 1954 near Naples (G-ALYY) (s1) | Report of the Court of Inquiry, C.A.P. 127 (HMSO, 1955), title page; FAA Lessons Learned, Comet 1 https://www.faa.gov/lessons_learned/transport_airplane/accidents/G-ALYV | dates and aircraft in the report title |
| 1b | second source | Time, "The Fate of Yoke Peter" (1954); Aerossurance "Common Comet Misconceptions" | Elba Jan 10, Naples Apr 8 |
| 2 | Cabin pressure differential about 8.25 psi (s2: "about eight pounds per square inch") | FAA Lessons Learned, Comet 1 | "P was about 8.25 psi" |
| 3 | Whole fuselage (G-ALYU) tested in a water tank at Farnborough, repeatedly pressurized (s3) | FAA Lessons Learned; Time (1954): steel tank built around Yoke Uncle at Farnborough | |
| 4 | Failed at about 3,060 cycles counting real flights: 1,230 flights + 1,830 tank cycles (s3 VO "about three thousand"; counter; label) | FAA Lessons Learned | "1,230 pressurized flights before testing and 1,830 tank 'flights'… about 3,060" |
| 4b | second source | Aerossurance (quoting FAA, 3,060 pressure cycles); other accounts give 3,057 (1,221 + 1,836); we say "about three thousand" and show FAA's split |
| 5 | Failure started at the corner of an escape-hatch window (s3) | FAA Lessons Learned: "at a corner of the squarish forward escape hatch window"; British Pathé/Ministry of Supply commentary (1954): failure at the corner of an escape hatch | |
| 6 | Elba wreckage: failure in the region of the roof ADF window, by fatigue (s4) | FAA Lessons Learned quoting the Elba report: "in the region of the A.D.F. window, brought about by fatigue" | |
| 6b | second source | Migflug (2025): crack began near the rear ADF aerial window | |
| 7 | Stress concentrates at a hole; tighter radius → higher peak (s5, s6) | TU Delft AE1102 lecture slides (notch disturbs the stress flow; Kt = 1 + 2a/b = 1 + 2√(a/r)); fracturemechanics.org (Inglis 1913: σmax = σ(1 + 2√(a/ρ)), circle = 3σ) | model labeled on screen as simplified |
| 8 | "A test report lists three-inch corner radii"; window 16.6 × 14 in (s7, drawn to scale) | RAE report on fatigue tests of Comet G-ALYR (FAA library) https://www.faa.gov/sites/faa.gov/files/2022-10/G-ALYR_Report_0.pdf | "Window: 16.6 in. wide x 14 in. high, corner radii 3 in." |
| 9 | Stress near the corners ran much higher than originally calculated (s7) | FAA Lessons Learned: original calculations put average stress near the corners at less than half the ultimate strength; later testing found it "significantly higher" | on screen: "calc: under ½ strength", "tests: much higher" |
| 10 | Later Comets got oval windows; today's oval shape (s8) | FAA Lessons Learned: Comet 1XB window shape changed "from squarish to the now-conventional oval shape" | |

## Assumptions and simplifications
- Force-flow lines are an illustration (labeled). The Inglis chart uses a hole half-length of 8 in for shape only; labeled "Shape only, not the Comet's numbers."
- Aircraft drawings are generic early-jetliner silhouettes, not technical drawings.

## Asset rights
All visuals drawn in code (templates/world.py + scenes.py); no archive photos or footage. Inter (OFL); DejaVu Sans Mono (Bitstream Vera). Narration Kokoro rotation voice for 2026-12-02 (Apache-2.0), disclosed as synthetic. Sound effects synthesized (templates/sfx.py).
