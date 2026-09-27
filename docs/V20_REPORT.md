# Jill's Kitchen 2.0 — release report (2026-09-27)

## 1. Artifact / release version
- Artifact https://claude.ai/artifact/2vhURujrtCpQ1P5jnSsjps — **Version 25**, label "2.0 (b)" (Version 24 = first 2.0 publish).
- Repo tag **v2.0** = commit `cb62b68` on `master`. Checkpoints: `v20-wip-1` rooms + kitchen line · `v20-wip-2` money ladder +
  cats' things · `v20-wip-3` Dylan arc + 2.0 tests · `v20-wip-4` pacing/docs/goldens · `v20-wip-5` demand cap scoped to grown
  restaurants. Zip: `jills-kitchen-v2.0.zip` (sent).
- Foundation kept intact: V18.1.1 hotfix (soufflé input hardening, frame loop guard) + all V18.2 systems.

## 2. What is new to play (summary)
- **Four spaces**: 店門口 (the street: façade, sign, weather, arrivals and departures, the terrace), 用餐區 (as before, plus the
  pass strip and the arch to the side room), **側廳** (bought: big window, sideboard, sconces, wine bar moves in, up to 6 tables
  with 2 booths), **廚房** (a real line). Tabs under the order strip with per-room badges (red = urgent, NEW on a new room),
  swipe on the scene, keys 1–4 / ←→, and the doors/arches/counter in the scene. One simulation runs in all rooms.
- **The kitchen**: sink, prep boards, range (up to 6 burners), under-counter oven, coffee machine; the pass under heat lamps with
  the ticket rail; the pickup side with the door. Cooks are actors: they walk between prep, range, oven, sink and the pass; the
  recipe decides where each step happens; handwork waits for the cook to be there; the tray's own vessel renderer draws the
  pasta in the pot, the duck in the pan, the soufflé in the oven; chefs carry the plate to the pass and plate it with the
  garnish. Tap a burner to open Jill's tray from there; the fridge opens the stock panel.
- **The money ladder**: five projects (露天座位 25k, 大出菜口 15k, 冷藏庫 30k, 廚房擴建 45k, 側廳 60k) with real effects; side and
  outdoor tables; six street pieces (2k–8k); seven cats' things (800–12k). Buying a project is an event (construction → reveal
  card → 「去看看」 → NEW tab + Jill's word the next morning). The summary shows 存錢的目標: one within reach, one a few days
  away, one to dream about, with how far and roughly how many days.
- **The cats' things create behaviour**: 柔柔 in the box ambushing passers-by, 寶寶 on the window perch, 包包 on the cushion or the
  lounge, 樾樾 in the basket, 小齁 through the tunnel; first use per cat is a photo (when you're looking), a log line and an
  achievement. The five cats never go outside.
- **Dylan**: twelve more exchanges of the act (before and after the reveal), milestone scenes tied to the growing place, stage-2
  clues (he knows where the menus and the glasses are), 王太太 notices, he sometimes takes the side room, the journal line after
  the reveal is deliberately ordinary.
- **Art**: people pose (arm swing, carrying, chopping/stirring/pouring, crossed arms), chef jackets with neckerchiefs, aprons,
  patterned customer tops; tea lights and room lamps at dusk; sconces; the street lamp, a bicycle, wet reflections; cats' ears
  twitch. Rooms have their own identity (working warmth / quiet lounge / neighbourhood).
- **Grown-restaurant pacing**: demand is capped at what the tables can turn over (grown restaurants only), the rating is judged
  over more visits in a bigger place, full-house departures are toasted once per 40 s with a count, the prep screen warns when
  tables outnumber what the waiters can cover. Guests remark on the new rooms; a one-time 2.0 news item on the prep screen.
- 7 new achievements (67 total), 4 new album moments, new shop icons; an A-frame chalkboard by the counter with today's
  recommendation; the saving goal as one line on the prep screen; the 2.0 news item once.

## 3. What changes for a Day-25 player
- Loads unchanged (money, level, dishes, staff, regulars, photos, achievements). Three tabs appear (店門口 / 用餐區 / 廚房); the
  kitchen already shows your line, your chefs cooking your orders, the pass filling up.
- After the first close: 工程 and 貓的東西 pages in the shop (all five projects affordable to a rich save; the ladder still shows
  three things), the summary's goals, the reveal on the first purchase. The side room and the terrace add capacity and demand;
  the prep screen will tell you when to hire more waiters (crew cap +4 with the side room and the kitchen expansion).
- Expect the first evening after the side room to be harder (more guests than two waiters can seat): hire; the rating is now
  judged over ~80 visits so one hard evening does not swing it.

## 4. Save compatibility (result)
- Test `mature_save_loads_into_2_0`: a V18.1.1-shaped Day-25 save (JILL, 12 tables, LV5 crew, all dishes, regulars, album,
  Dylan stage 3, no 2.0 fields) keeps every counted field, gets `rooms/ext/gear/gearUse/newRooms/sideTables/frontTables`,
  opens three rooms, plays a whole day in every room with the staff on the line, serves ≥20 guests, no errors. Pass.
- Fresh saves, V13/V16/V18 fixtures, backup export/import, checkpoint round trip: all existing tests pass (`v16_save_continues`,
  `save_backup_and_restore`, `world_stays_visible_across_days`, …).

## 5. Testing result
- `python3 tests/run_tests.py` (index.html): **53 passed, 0 failed**. `--target single`: **53 passed, 0 failed** (on the
  v20-wip-5 build; the two last commits touched seat lines and a news item, spot-checked with 4 tests).
- Goldens: scenario/frames/cat fingerprint re-recorded for 2.0 (guests walk in from the street; chefs plate at the pass;
  posed arms). Lint clean.
- Real-speed smoke (`playtest20.py`, 4 days from the Day-25 save, person-like actor, room switching, evening purchases):
  no errors over 4 × ~300 s real time; reveals seen for all five projects; NEW tab and Jill's line the next day; side tables
  used the day after buying; cats used box/perch/lounge; kitchen looks showed cooks in add/plate/hold/watch beats and plates
  at the pass. It also found the pacing problem (64 lost guests on the day after the terrace) that led to the cap, the rating
  window and the staffing warning; re-measured with the cap: 87 guests / 0 lost / rating 3→4.54 on the first expanded day with
  a full crew. A second 2-day smoke on the final build (Day-25 save, terrace then side room): 82 and 76 guests, 0 lost,
  rating 3→4.58→4.87, no errors.
- Performance (headless Chromium 390×800, mature save, rain): ms JS per frame — dining room 12.6 (V18.1.1 baseline 13.8),
  kitchen 4.3, side room 3.1, street 2.5; first frame in a room after a change 100–240 ms (cached background).

## 6. Normal-play observations (from the smoke and probes)
- The kitchen reads as a kitchen at a glance: the range with the wok steaming, the oven door glowing, two chefs plating under
  the lamps, the waiter arriving on the pickup side. Marco (oven) is idle a lot on menus with few baked dishes — true to the
  menu, not a bug.
- With 2 waiters on 21 tables the evening collapses (25 angry leaves in fast-bot mode); with 4 waiters + 2 cleaners it holds.
  The game now says so on the prep screen and in the side room's reveal card.
- Full-house departures were 60+ toasts a day at peak demand; now one toast per 40 s with the count.
- Emergency restocks 13/day at 22 dishes with a 180 fridge — the cold room (+80) is the intended answer.

## 7. I/T/O per major system
| System | Implemented | Tested | Observed |
|---|---|---|---|
| Rooms + navigation | tabs/badges/swipe/keys/doors, routing through doorways, off-screen sim, per-room album camera | rooms in tests (`mature_save…`, `purchases…`), swipe/keys probes, touch test in the kitchen | all rooms drawn at phone and desktop sizes; cats' trips; guests in side/terrace |
| Kitchen line + cooks | geometry, vessel renderer on the line, actors, presence gating, plating phase, taps | `kitchen_cooks_walk_the_line_and_plate` (movement, plating, gating, throughput), touch test | smoke: cooks in every beat, plates at the pass, Jill's tray from the kitchen |
| Money ladder | PROJECTS/EXTERIOR/CATGEAR data, effects, shop pages, reveal, NEW tab, goals | `purchases_change_the_place`, `goal_ladder…` | smoke: all five reveals, goals list, effects in the next day's run state |
| Cats' things | weights, side-room trips, box ambush, tunnel dash, first-use moments, deluxe tree | `cats_use_their_things_and_stay_inside` | smoke: box/perch/lounge used; no cat outside |
| Dylan | acts, milestone scenes, clues, journal | `goal_ladder_and_dylan_scenes` | scenes fire once; the smoke's 4 days did not draw one (low frequency by design) |
| Art | people poses/clothes, evening lights, street details | golden frames re-recorded, screenshots reviewed | phone + desktop screenshots in all rooms at dusk and rain |
| Pacing | demand cap (NT≥8), rating window, toast limit, warning | pacing probes (2 vs 4 waiters) | numbers above |
| Save | new fields with defaults, migration of a mature save | migration test + all save tests | — |

## 8. Deferred (honest list)
- Chef specials / signature evolution (food progression beyond the existing 22 dishes + signature) — not built.
- A second cook of the same duty only helps through the expansion's extra burners (the older shared-line behaviour).
- Cats do not visit the kitchen; the dining room holds one cat piece (the box) and the big tree, the rest live in the side room.
- The dining room's arch to the side room sits at the right end of the back wall (mostly off-screen on phones).
- Desktop is still the phone column (540px); a landscape layout for Steam is future work.
- Ready plates on the pass are not tappable; waiters/Jill collect as before.
- No new incidents/VIP/hospitality content beyond V18.2's.

## 9. Real-device-only validation still needed
- iPhone: swipe vs tap on the burners/stations and cats; the tab strip's touch targets; scrolling of the order strip while
  swiping rooms; frame rate in the kitchen with a full line and in the street in the rain; the reveal overlay over the shop
  sheet; the service worker with the new cache name (`jills-kitchen-v2.0`); PWA install flow.
- Nothing here was verified on a real device in this session.
