# Sources and rights · BB-20261127-014 · Why does airport security swab your hands?

All sources opened in this run (2026-11-27). Quotes ≤15 words.

## Claim ledger
| # | Claim (as used) | Where used | Source 1 | Source 2 / cross-check |
|---|---|---|---|---|
| C1 | Anyone who handles explosives can leave invisible traces on what they touch (NIST: the premise of IMS trace detection) | narration S2, label "invisible traces" | NIST IR 7240 (Verkouteren et al., Sept 2005), https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7240.pdf: "anyone handling explosives (or narcotics) will leave microscopic, invisible traces on anything they touch." | National Academies, *Opportunities to Improve Airport Passenger Screening with Mass Spectrometry* (2004), ch. 2, https://www.nationalacademies.org/read/10996/chapter/4: "the presence of threat substance residues on his or her hands" |
| C2 | The swab wipes hands/belongings to collect the traces | narration S1-S2, scene 1-2 | DHS S&T, "The Next Generation of Explosives Trace Detection is Here" (Oct 6, 2022; updated 04/10/2025), https://dhs.gov/group/13025/news/2022/10/06/feature-article-next-generation-explosives-trace-detection-here: "wiping the individual's hands, clothes, or belongings with a swab" | NIST IR 7240: "a cloth or paper of some type that is swiped over a surface" |
| C3 | The machine is an ion mobility spectrometer (generic, simplified) | badge "TRACE DETECTOR · SIMPLIFIED", whole sequence | DHS S&T 2022: "all deployed NextGen ETD contact sampling devices are based on ion mobility spectrometry" | NIST IR 7240: "The TSA has deployed thousands of IMS desktop instruments."; Talanta review (INL, OSTI 912136): IMS "has become the most successful and widely used technology" |
| C4 | The swab is heated and the residue turns to vapor | narration S3, HEATER / DESORBER / heating / vapor | NIST IR 7240: "heated with an internal heater, called a desorber, to produce the gases" | ASU chemistry course notes (IMS page), https://www.asu.edu/courses/chm233/notes/spectroscopy/spectroscopyRL2/ims.html: "The swipe sample is first heated to vaporize any organic compounds."; DHS 2022: "it is vaporized and ionized" |
| C5 | Usually a small radioactive source gives the molecules an electric charge (nickel-63) | narration S4, label "ion source (usually nickel-63)" | NIST IR 7240: "normally ionized with a radioactive material, usually nickel-63." | ASU notes: "an ionizing source, usually a radioactive nickel element"; Sandia SAND 2009-1553W, https://www.sandia.gov/app/uploads/sites/145/2021/11/2IMS.pdf: "either be a radioactive source or other means such as a corona discharge" (why we say "usually") |
| C6 | An electric field pulls the ions down a tube against a flow of gas | narration S5, "electric field pulls →", "← gas pushes back" | NIST IR 7240: "drift through an electric field at atmospheric pressure" ... "against a countervailing flow of gas." | Sandia: "known tube length (L) with a known electric field (E)"; ASU: "they suffer collisions with the gases in the tube" |
| C7 | Each kind of molecule crosses at its own speed | narration S5 | DHS 2022: "Each type of molecule travels at a different speed when it is ionized." | ASU: "Different organic ions have different drift times down the tube." |
| C8 | The race lasts milliseconds; drift time commonly under 15 ms | narration S6, "drift time · commonly under 15 ms", axis 0-15 ms | NIST IR 7240: "Drift times are commonly less than 15 milliseconds" | Talanta review abstract (OSTI 912136): "ion drift times from 5–20 ms" (consistent: milliseconds); DHS 2022: "down to the millisecond!" |
| C9 | Arrival time identifies the substance ("fingerprint") | narration S6, chip | DHS 2022: "reveals the type of molecules present" (from speed measured in the tube) | ASU: "When the machine detects a compound with one of these calibrated drift times" |
| C10 | Library of explosives; a strong match alarms, no match no alarm (simplified: NIST alarms above a threshold; badge says SIMPLIFIED, threshold detail deliberately omitted) | narration S7, scene 7 | NIST IR 7240: "All IMS instruments must have a library (spectral database) of peaks"; "will generate a positive alarm for peaks that are intense enough" | DHS 2022: "allows us to match explosives with a newly expanded library" |
| C11 | Knowledge pearl: different molecules can share similar drift times; experts have long looked to mass spectrometry to improve trace detection | captions, X thread | National Academies 2004: "Since different molecules may have similar drift times"; "Mass spectrometry (MS) is an obvious candidate to consider for improving" IMS systems | DHS 2022: "The NextGen Mass Spectrometry ETD addresses and meets the challenge" |
| H1 | "If you fly home this Sunday" (scenario only, no factual claim). Context, not on screen: TSA names Sunday Nov 29, 2026 the busiest day of Thanksgiving weekend | run log / audience reason only | Time Out (Nov 18, 2026), https://www.timeout.com/usa/news/this-is-the-worst-day-to-travel-for-thanksgiving-weekend-according-to-the-tsa-111826 | KSL/Reuters (Dec 1, 2025), https://www.ksl.com/article/51412679: record "3.13 million airline passengers on Sunday" (2025) |

**Illustrative (labeled on screen):** the three peaks and their positions ("ILLUSTRATIVE PEAKS"), the magnified fingertip ("MAGNIFIED · ILLUSTRATION"), the detector layout ("TRACE DETECTOR · SIMPLIFIED"), ion speeds in the tube animation.
**Cut in fact-check pass 1:** "heated to about 200 °C" / "180–230 °C" (only NIST IR 7240 gave a desorber range; the NIST/RSC 2012 desorption study gives a lab range of 60–280 °C, not a commercial spec, so no second source). "Swabs are random" and "lotions cause false alarms" (only a secondary legal blog, FindLaw 2022). "Small ions move faster" (not stated in sources opened). Nothing about who is swabbed, how often, or how to avoid an alarm (mechanism only).

## Fact-check
- Pass 1 (self, core claim before scripting): PASS after the cuts above.
- Pass 2 (independent agent): see post.json qa.fact_check.

## Asset provenance
- Visuals: all drawn in code for this episode (Pillow, `episodes/2026-11-27_airport-swab/scenes.py`, `templates/world.py`): generic flat hand, generic swab, generic detector cutaway. No photos, logos, uniforms, real people or real product designs.
- Fonts: Inter (SIL Open Font License).
- Mark: Bonus Braincell logo (own).
- Narration: Kokoro am_eric, Apache-2.0 (synthetic AI voice).
- Sound effects: synthesized (templates/sfx.py). Music bed: synthesized (templates/sfx.py music_bed), no samples.
