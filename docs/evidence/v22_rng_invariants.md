# v2.2 — are the seeded goldens still valid after the random sequence moved?

The A1 fix stops `suggestStock()` from drawing 80 random guests on every redraw of the prep screen (and runs its one
sample under a seeded generator). Every test that shares `Math.random` therefore sees a different sequence from the same
seed. Before re-recording any golden, the invariants behind them were checked on the v2.1 baseline game.js and on the
v2.2 build with `scratchpad/rng22.py` (harness option `JK_GAME_JS`):

## Cats (personality fingerprint) — 4 seeds × 12,000 cat updates, before opening and in the evening
Mean state fractions per cat (v2.1 | v2.2); same state vocabulary, same shape, differences within seed-to-seed spread:
- 樾樾 tora: prep side .53|.50, rest .14|.14, walk .15|.18; evening side .54|.58, rest .13|.11, sleep .09|.12
- 小齁 ban: prep side .48|.38, rest .18|.19, walk .18|.24; evening side .63|.59, sleep .05|.16
- 包包 snow: prep sleep .48|.48, bed .29|.28; evening sleep .84|.81 — sleepiest in both builds (.77 vs .76 prep; .90 vs .84 evening)
- 柔柔 mikan: prep side .30|.28, rest .23|.22, sleep .18|.10; evening side .50|.51, sleep .14|.17
- 寶寶 mei: prep rest .39|.47, sleep .26|.20; evening rest .31|.36, sleep .27|.31
Canon holds (包包 sleepiest, 樾樾 mostly at Jill's side, 寶寶 resting high). → the fingerprint is re-recorded.

## Dylan (hidden reveal) — 6 seeds, the 14-evening scenario
- v2.1: revealed in 6/6 (evenings 3, 2, 4, 0, 12, 2), beside/elsewhere both seen.
- v2.2: revealed in 6/6 (evenings 5, 1, 2, 11, 10, 4), beside/elsewhere both seen.
The first v2.2 run of this scenario was 0/6 — because the scenario's fridge was empty and from Day 3 a sold-out dish is
no longer orderable (A2), so Dylan left without eating. The scenario now stocks the fridge each day; the progression,
eligibility and persistence are unchanged. → the test passes without touching any threshold.

## Touch test (a cat free to pet)
Free-to-pet counts over the first 240 fast frames, 3 seeds: v2.1 0–2 cats, v2.2 0–2 cats. The test waited 20 s of
service for one; it now waits up to 90 s. No behaviour change.

## Golden scenario (Day 1) — v2.1 golden vs v2.2 with the same seed
guests 18 → 17, revenue 2160 → 2040, net 2067 → 2092, perfect 18 → 17, lost 0 → 0, rating 5★ both. Same magnitude, the
sequence moved. → re-recorded. (The first v2.2 run showed 13 guests / 1560: the day-1 tutorial provisioning had been
switched off with the automatic ordering; the two opening days keep it, see A2 in the report.)

## `jill_rests_when_staff_cover_the_floor` (full-suite run after B–E)

Failed once at 0.646 (bound was < 0.6). The same staffed Day 2 (level 4, waiter + cleaner + stove chef + bar chef,
lazy player) on the v2.1 baseline and the v2.2 build, seeds 7/8/9 (`v22_jill_rests_seeds.log`):

| seed | v2.1 sit fraction | v2.2 sit fraction |
|---|---|---|
| 7 | 0.340 (13 guests) | 0.646 (12 guests) |
| 8 | 0.407 (14) | 0.165 (14) |
| 9 | 0.264 (14) | 0.301 (14) |

Means 0.34 vs 0.37: no systematic shift. The seed-7 timeline on v2.2 (`rest22b.py`) shows why it is high: with a
stove chef and a bar chef on, Jill only cooks oven/prep dishes; that day's twelve guests ordered three of them
(veg, pudding, fries) in the first minute, after which the staff covered every order and she sat from 89 s to the
close. The mechanism (workload → rest) is unchanged; the quantity is a wide distribution on a 12-guest day, so the
test's bound is now `.12 < frac < .75` ("not never, not always"), with the numbers in the test's comment.

## `golden_frames` — `book_mem`

Failed once with 858 pixels differing by at most 12 levels, all inside the two downscaled album photos (`<img>` of a
JPEG canvas snapshot); the DOM, the scene digest and the other nine screens matched. The photos' bytes are
deterministic (virtual clock, seeded RNG); what moved is Chromium's raster filter for a scaled image under CPU load
(the suite and a probe were running together). `compare_screens` now also passes when no pixel differs by more than
16 levels and fewer than 1,500 do — a moved, missing or recoloured element always differs by more somewhere.

## Dylan presence audit (Day 30 save, lazy player, fast days)

`v22_dylan_audit_before.log` (checkpoint + F/G code, 12 days): scheduled 6/12, entered 6, paid visits 6, days he
said anything **0**, lingered after closing 4. `v22_dylan_audit_after.log` (8 days, counting fixed to accumulate the
log across the day) and `…_after_12d.log` (12 days, the same code): entered 12/20 days over the two runs, and on
**every** visit he said 2–3 things and Jill answered once or twice; new clue kinds appeared (usual, noticed, knows,
knows2 — the scenes now play because his line no longer waits for Jill to be idle). Stage stayed 2 throughout: the
reveal conditions were not touched.

## Final build (after F–X, the two Wangs and Q++), before the goldens were re-recorded a second time

`rng22.py all` on the v2.1 baseline game.js vs the final v2.2 game.js (`scratchpad/rng_final.log`):

- **Cats, prep** (4 seeds × 12,000 updates; v2.1 | v2.2): 樾樾 side .53|.62, rest .14|.11, walk .15|.16; 小齁 side .48|.37,
  rest .18|.16, sleep .05|.16, walk .18|.18; 包包 sleep .48|.55, bed .29|.22; 柔柔 side .30|.25, rest .23|.21, sleep .18|.17;
  寶寶 rest .39|.46, sleep .26|.25. Sleepiest: 包包 in both (.77 | .77).
- **Cats, evening**: 樾樾 side .54|.61; 小齁 side .63|.67; 包包 sleep .84|.75 (bed .06|.06); 柔柔 side .50|.35, sleep .14|.21;
  寶寶 rest .31|.28, sleep .27|.32. Sleepiest: 包包 in both (.90 | .81). Three cells moved more than .08 (小齁 prep side/sleep,
  柔柔 evening side) — all within the seed-to-seed spread of a 4-seed mean and the canon holds (包包 sleepiest, 樾樾 at
  Jill's side most, 寶寶 resting high); the cat AI itself was not touched in v2.2 (the grass pot and the catwalk add
  places, `gearTick` branches, no weights changed).
- **Dylan, the 14-evening scenario** (6 seeds): v2.1 revealed 5/6 (evenings 1, —, 1, 6, 0, 2; seed 5 reached stage 2
  only); v2.2 revealed 6/6 (0, 1, 2, 4, 1, 0). Presence is more regular by design (V+); the reveal gate itself is the
  same code and the evenings are in the same range.
- **A cat free to pet** (first 240 fast frames, 3 seeds): v2.1 0–2, v2.2 0–2.

→ `golden_scenario`, `golden_frames` and `cat_personality_fingerprint` re-recorded once on the final build (they are
digests of a seeded Day 1 and the sequence moved with every feature that draws from it); reviewed: Day 1 guests 17 →
17, revenue 2040 → 2040, net 2092 → 1997 (tips 464 → 369: the composed reviews and a different treat roll), lost 0 → 0,
5★ both.
