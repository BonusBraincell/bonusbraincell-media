# Scene plan · Why are clocks dropping the leap second?

Total 44.7 s · opening motion · design system v4.0

## Episode record (v4)
- **Question:** Why did the world's timekeepers vote to stop adding leap seconds, and what happens instead?
- **Editorial contribution:** {"type": "two-worlds comparison + calculation + real dataset", "statement": "We run atom time and Earth time side by side for the whole episode, show with a labeled calculation how milliseconds per day become a second in about a year, animate the real 27-step IERS leap-second record (9 in the 1970s, none since 2016), explain why a speeding-up Earth made a first-ever negative leap second a risk, and reveal the new limit (0.9 s to 1 hour) on a labeled log scale."}
- **Narrative structure:** comparison_two_worlds
- **Animation approach:** TWO_WORLDS
- **Custom scene:** Split panels for the whole episode: a cesium atom and digital clock (left), Earth from above the pole turning under the sun (right), with a yellow gap bar as the through-line; a 2.7 ms/day calendar fill; a clock ticking into 23:59:60 while the gap gauge snaps back; the real TAI-UTC staircase 1972-2017; a negative leap second skipping :59; the allowed gap zooming from 0.9 s to one hour on a log axis.
- **Cover composition:** {"type": "split_two_worlds", "layout": "middle", "environment": "two_skies", "text_amount": "one line + the yellow 23:59:60", "main_object": "atom panel and Earth panel with a gap between them"}
- **Similar recent episodes:** ["BB-20261118-004 Why does the U.S. have time zones? (timekeeping; this is its planned Part 2)", "BB-20261126-012 Why is Thanksgiving on the fourth Thursday? (calendar rule; different mechanism)"]

**0.00–0.50 s · cover** (frame 0 = thumbnail)

## Beat 1 · 0.50–6.43 s · custom
- **Main visual subject:** two panels: atom clock ticking; Earth turning under the sun; a yellow gap opens between them
- **Narration:** Your phone keeps time with atoms. The sun keeps time with a spinning planet. They don't agree.
- **Caption chunks:** [0.7–2.6] Your phone keeps time with atoms. / [2.6–5.1] The sun keeps time with a spinning planet. / [5.1–6.1] They don't agree.
- **Labels, values, units, sources:** none
- **What changes and when:** atom electrons orbit, seconds tick; Earth turns; gap bar grows on 'don't agree'; 4.9s: gap_at
- **Assets:** drawn in renderer (no external asset)
- **Viewer must understand:** there are two kinds of time and they differ
- **Visible objects:** atom; digital clock; Earth; sun; gap bar
- **What changes over time:** gap opens
- **What causes the change:** the two clocks run at different rates
- **Necessary on-screen text:** ATOM CLOCK; EARTH CLOCK; GAP BETWEEN THE CLOCKS
- **Environment / transition in / sound:** two_skies / dissolve / tick, tock

## Beat 2 · 6.43–16.03 s · custom
- **Main visual subject:** UTC clock counts 23:59:58 → 23:59:60 → 00:00:00; gap gauge climbs to 0.9 s and snaps back
- **Narration:** Earth's spin wobbles, so a gap grows. Near nine-tenths of a second, timekeepers added a leap second. The clock read 23:59:60.
- **Caption chunks:** [6.6–9.3] Earth's spin wobbles, so a gap grows. / [9.3–11.5] Near nine-tenths of a second, / [11.5–13.9] timekeepers added a leap second. / [13.9–15.7] The clock read 23:59:60.
- **Labels, values, units, sources:** none
- **What changes and when:** gauge climbs toward the 0.9 s line; clock shows a yellow :60 on '23:59:60'; gauge drops by one second; 8.6s: insert_at
- **Assets:** drawn in renderer (no external asset)
- **Viewer must understand:** a leap second resets the gap
- **Visible objects:** digital clock; gap gauge with 0 and 0.9 s lines
- **What changes over time:** an extra second is shown and the gap falls
- **What causes the change:** the inserted second lets Earth catch up
- **Necessary on-screen text:** UTC CLOCK; THE GAP; 0.9 s; one extra second
- **Environment / transition in / sound:** two_skies / push_left / beep

## Beat 3 · 16.03–23.37 s · custom
- **Main visual subject:** real IERS data: TAI-UTC staircase from 10 s to 37 s, 1972-2017; 1970s highlighted
- **Narration:** They did it 27 times since 1972. The last one: New Year's Eve, 2016.
- **Caption chunks:** [16.2–19.5] They did it 27 times since 1972. / [19.5–23.1] The last one: New Year's Eve, 2016.
- **Labels, values, units, sources:** none
- **What changes and when:** staircase draws step by step; 1970s band on 'Nine'; last step marked on 'New Year's Eve'; 1.2s: seventies_at; 3.5s: last_at
- **Assets:** drawn in renderer (no external asset)
- **Viewer must understand:** 27 leap seconds, front-loaded, none since 2016
- **Visible objects:** time axis; staircase line; 1970s band; last-step marker
- **What changes over time:** steps accumulate
- **What causes the change:** each insertion adds one second
- **Necessary on-screen text:** leap seconds added: N; 9 in the 1970s; last one: Dec 31, 2016; source line
- **Environment / transition in / sound:** two_skies / dissolve / none

## Beat 4 · 23.37–30.17 s · custom
- **Main visual subject:** Earth spinning faster with yellow speed arcs; a negative leap second deleting :59; 30% odds chip
- **Narration:** Then Earth sped up, and a first-ever negative leap second started to look possible: deleting a second.
- **Caption chunks:** [23.5–24.7] Then Earth sped up, / [24.7–27.1] and a first-ever negative leap second / [27.1–28.6] started to look possible: / [28.6–29.8] deleting a second.
- **Labels, values, units, sources:** none
- **What changes and when:** Earth spins faster; 23:59:58 → 00:00:00 with :59 struck out on 'deleting'; odds chip on 'thirty percent'; 2.0s: odds_at; 5.3s: neg_at
- **Assets:** drawn in renderer (no external asset)
- **Viewer must understand:** a faster Earth raised the odds of the first negative leap second
- **Visible objects:** Earth; speed arcs; clock digits; odds chip
- **What changes over time:** a second is removed
- **What causes the change:** shorter days reverse the gap
- **Necessary on-screen text:** 23:59:58 59 00:00:00; never done before; 30% CHANCE BY 2035 (CCTF/IERS)
- **Environment / transition in / sound:** two_skies / zoom_through / none

## Beat 5 · 30.17–38.37 s · custom
- **Main visual subject:** scale reveal: the allowed gap zooms out from 0.9 s to one hour on a log axis
- **Narration:** So in October, timekeepers voted: from May 2027, no more leap seconds. The gap can grow to an hour.
- **Caption chunks:** [30.3–32.9] So in October, timekeepers voted: / [32.9–35.8] from May 2027, no more leap seconds. / [35.8–38.0] The gap can grow to an hour.
- **Labels, values, units, sources:** none
- **What changes and when:** old 0.9 s bar; axis zooms out and the yellow bar runs to 1 hour on 'an hour'; 7.2s: hour_at
- **Assets:** drawn in renderer (no external asset)
- **Viewer must understand:** the new rule allows a gap 4,000 times larger, so no patch for centuries
- **Visible objects:** log axis; old limit bar; new limit bar
- **What changes over time:** limit extends
- **What causes the change:** CGPM Resolution 5
- **Necessary on-screen text:** from 20 May 2027; no more leap seconds; old limit; new limit: 1 hour; log scale
- **Environment / transition in / sound:** two_skies / push_up / swoosh_up

## Beat 6 · 38.37–44.73 s · custom
- **Main visual subject:** phone and sun panels side by side, a thin gap allowed to drift
- **Narration:** Your phone and the sun are now allowed to disagree. Follow for one bonus braincell per scroll.
- **Caption chunks:** [38.5–39.9] Your phone and the sun / [39.9–41.7] are now allowed to disagree. / [41.7–44.3] Follow for one bonus braincell per scroll.
- **Labels, values, units, sources:** none
- **What changes and when:** gap bar breathes slowly
- **Assets:** drawn in renderer (no external asset)
- **Viewer must understand:** the repeatable takeaway
- **Visible objects:** phone; Earth and sun; gap bar
- **What changes over time:** gap drifts
- **What causes the change:** payoff
- **Necessary on-screen text:** YOUR PHONE; THE SUN; ALLOWED TO DRIFT APART
- **Environment / transition in / sound:** two_skies / dissolve / none
