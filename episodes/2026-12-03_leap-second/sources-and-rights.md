# Sources and rights · Why are clocks dropping the leap second? (v4 demo, slot 2026-12-03)
Checked 2026-11-26. Re-open every source on the day before posting.

## Claim ledger
| # | Claim (where) | Source | Support |
|---|---|---|---|
| 1 | Atomic seconds are constant; Earth's rotation varies: tides slow it, changes inside Earth (core) speed it up or slow it (s2) | National Geographic (Jul 24, 2025, quoting Agnew, Scripps): Moon's tidal influence slows rotation; core slowed and the rest of Earth sped up; Discover (2025) | |
| 2 | 2.7 ms/day × ~370 days ≈ 1 s (s3) | Our calculation; labeled ILLUSTRATIVE NUMBERS on screen; not a measured average | 0.0027 × 370 = 0.999 |
| 3 | A leap second was applied when UT1−UTC approached 0.9 s; 23:59:60 (s4) | BIPM, Resolution 4 of the 27th CGPM (2022) https://www.bipm.org/en/cgpm-2022/resolution-4 | "predicted to approach 0.9 seconds, a leap second is applied" |
| 4 | 27 leap seconds since 1972; 9 in the 1970s; last on Dec 31, 2016 (s5, chart) | IERS Bulletin C leap-second table as distributed in IANA tzdata leap-seconds.list (file "updated through IERS Bulletin C", expires 28 June 2027) | 28 entries: TAI−UTC 10 s (1 Jan 1972) → 37 s (1 Jan 2017); insertions effective 1 Jul 1972 … 1 Jan 1980 = 9 in the 1970s |
| 4b | second source | Euronews (Oct 16, 2026): 27 leap seconds since 1972, most recent end of 2016; CTV News (2025): nine in the 1970s, none since 2016 | |
| 5 | Recent years had the shortest days measured since atomic timekeeping began (s6) | National Geographic (Jul 2025): "the shortest days since atomic timekeeping began in 1955"; Discover: July 5, 2024 shortest day on record | |
| 6 | A negative leap second (deleting a second) has never been applied; seen as high risk (s6) | BIPM, CGPM 2026 Resolution 5 https://www.bipm.org/en/cgpm-2026/resolution-5 | "has never been applied… high risk of causing anomalies and disruption to critical infrastructures" |
| 7 | Odds of a negative leap second ~30% by 2035 (s6 VO "timekeepers put the odds at thirty percent by 2035"; chip "CCTF/IERS") | Resolution 5 noting clause: March 2025 CCTF/IERS workshop estimate "reaching a 30 % probability by 2035" | |
| 8 | In October (15 Oct 2026, 28th CGPM) timekeepers voted for continuous UTC from 20 May 2027 with |UT1−UTC| up to 3,600 s (s7, cover) | BIPM Resolution 5 (2026): "continuous UTC will become effective on 20 May 2027"; "maximum value… 3 600 seconds (1 hour)" | |
| 8b | second source | Euronews (Oct 16, 2026); xenospectrum (adopted Oct 15, 2026) | |
| 9 | Cover: "Why minutes will stop getting 61 seconds" | follows from 3 and 8 (a leap second makes a 61-second minute; continuous UTC has none) | |

## Assumptions and simplifications
- Earth panels are schematic (view from above the pole; continents are blobs). The log axis is labeled. The staircase is drawn from the exact table dates.
- "Your phone keeps atom time" is a simplification: phones sync to UTC, which is atomic time with leap seconds; phrased as "counts atoms" in the payoff.

## Asset rights
All visuals drawn in code; leap-second dates from IANA tzdata (public domain data from IERS Bulletin C). Inter (OFL); DejaVu Sans Mono. Narration Kokoro rotation voice for 2026-12-03 (Apache-2.0), disclosed as synthetic. Sound effects synthesized.
