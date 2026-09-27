# Jill's Kitchen 2.1 — Food & Life: release report (2026-09-27)

## 1. Artifact / release version
- Artifact https://claude.ai/artifact/2vhURujrtCpQ1P5jnSsjps — **Version 29**, label "2.1 Food & Life" (Version 28 = 2.0 final).
- Repo tag **v2.1** on `master`, on top of `v2.0` (`6a757c2`, also `baseline-v2.0`). Zip `jills-kitchen-v2.1.zip` (sent).
- Nothing from 2.0 was restarted, redesigned or replaced: the rooms, the kitchen line, the money ladder, the cats' things and
  the Dylan arc are as shipped. 2.1 is nine commits of content on top.
- The brief arrived truncated after "0. PRODUCT DIRECTION — Jill's Kitchen is being developed toward a future"; this build
  is the reading of the title (food & life), the stated central question, and the two systems 2.0 had deferred (chef
  specials / signature evolution). If the rest of the brief names things not here, they are the next pass.

## 2. What the player sees (by room)
- **菜單研發 (evening)**: a new 特製版 section — eight finer versions of mastered dishes (LV3), 1.8k–7k each, with their own
  icon; below LV3 the shop says what is missing. Researched ones join the menu (or wait for a slot). 招牌菜 page: which
  version the signature is on and how many sold to the next.
- **廚房**: the specials on the line look like their base while cooking and get their finish at the pass (crab, burrata,
  mushroom sauce, truffle, marrow bone, cherries, uni, matcha). Idle cooks wipe, sip, taste, read the rail, chat. The
  pickup side is furnished (shelving, work table with the dish rack, mop) on phone-tall screens.
- **用餐區**: bigger plates; the meal visibly goes down; empty plates until the bill; a party's talk bubble; families with a
  small child; a guest photographing a special; the signature's second/third plating.
- **店門口**: passers-by (some with a dog, umbrellas in the rain), lookers at the window and the door with a thought bubble,
  a scooter or bicycle on the road, and the ones who walk in — from where they stood. The summary counts them.
- **Summary / prep**: 路過進來 n 組; the 2.1 news line once; the signature upgrade news the morning after.

## 3. Save compatibility (result)
- A pre-2.1 save owns no special and loads unchanged (asserted in the specials test on the Day-25 V18.1.1 fixture, which
  is now explicitly built without specials). All new fields are optional (`firstSpecial`, `sigEvoNews`, `news21`,
  `stats.walkins`, `stats.families`, `lastSummary.walkins/families`). The Day-25 migration test and every save test pass.

## 4. Testing result
- `python3 tests/run_tests.py` (index.html): **55 passed, 0 failed** after the goldens were re-recorded (the street draws
  from the shared random stream, so scenario/frames/cat fingerprint moved; each was reviewed). Lint clean.
- New tests: `specials_are_a_finer_version_of_a_mastered_dish`, `the_street_has_passers_by_and_some_walk_in`.
- Real-speed smoke (`playtest21.py`, 3 days, a grown 2.0 restaurant with 18 tables and 10 staff, person-like actor):
  no errors over 3 × ~300 s real time. Day 1: 85 guests / 2 lost / 4 walk-ins / rating 3→4.21, the signature reached its
  second plating (46 sold); the evening researched all eight specials (84k → 50k). Day 2: 97 / 13 lost (the critic buzz
  day) / 6 walk-ins; specials cooked and served (蟹肉蛋炒飯, 布拉塔番茄麵). Day 3: 78 / 17 / 7; the album got 「先拍再吃」;
  the log had 「有人在門口看了一下，走進來了。」「特製版長這樣。」「小朋友：「我要那個！」」. Cooks' idle kinds seen every day:
  chat, rail, sip, taste, wipe. Families seated on every day (15 in three days).
- Pacing check (`pace21.py`, lazy fast-bot, 21 tables, 4 waiters + 2 cleaners + 4 chefs, 3 days): as-is 90/0, 76/29, 76/27
  lost; without families 66/0, 75/20, 53/32; without walk-ins 76/0, 69/37, 73/49. The same probe on the **2.0 baseline**:
  74/2, 86/22, 58/28. So the day-2/3 losses in that scenario are pre-existing (rating-driven demand outgrowing what a
  passive Jill turns over), not a 2.1 regression; walk-ins and families do not add to them. The real-speed run above,
  with a person acting, stayed at 2–17 lost.

## 5. Normal-play observations
- The street is the biggest change to the feel: the restaurant is on a road with people on it, and arrivals now come out of
  that flow. Lookers convert often enough to notice (4–7 a day on a grown restaurant) without changing demand.
- The specials read at the pass and in the ticket strip; at table size (20 px) they read by colour (pink, white, dark).
- Idle cooks chatting at the range is the single most-noticed kitchen change in the looks; the furnished pickup side makes
  the kitchen screenshot hold up.
- Families take four-tops; on the weekend event they double. The child is obviously a child at any size.

## 6. I/T/O per system
| System | Implemented | Tested | Observed |
|---|---|---|---|
| 特製版 | 8 specials, shop section, research, stock/xp, toppings, `baseOf` in every renderer, achievements, moments | specials test (offer, prices, unlock, icons differ, cooked and served by chefs, tickets) | smoke: researched, on the menu, cooked, served, photographed |
| Signature evolution | `sigLv` from lifetime sold, plating v2/v3, price, shop/prep text, achievements, Dylan scene | goldens; probe renders of v1/v2/v3 | smoke: v2 reached on day 1 |
| Table life | plates 20/22 px, meal going down, empty plates, talk bubbles, special reactions, photo | goldens re-recorded; crops reviewed | smoke: quotes in the log |
| Street | walkers, dogs, umbrellas, vehicles, lookers, walk-ins as the next scheduled party, summary, achievement | street test | smoke: 4–7 walk-ins/day, screenshots |
| Kitchen life | idle beats, chat pairs, furnished pickup side, home spots apart | kitchen tests pass; screenshots | smoke: all five idle kinds daily |
| Families | type, looks with a child, weights, four-tops, cat interest, quotes, moment, achievement | — (covered by goldens and the smoke) | smoke: families every day |

## 7. Deferred / known limits
- An umbrella stand inside by the door was built and removed: the HUD chips cover that corner on phones.
- Cats still do not visit the kitchen. Desktop remains the phone column. Ready plates on the pass are still not tappable.
- Walk-ins only replace plain scheduled parties (never a regular, never a signature seeker).
- The rest of the 2.1 brief (not received) — see §1.

## 8. Real-device-only validation still needed
- iPhone: the street's extra draw cost in the rain with five walkers and a scooter; the kitchen fill on the 390×800 class
  (LH 551) vs 390×700 (LH 464, where the fill is skipped by design); the specials section's scroll on the R&D page; the
  service worker with cache `jills-kitchen-v2.1`. Nothing here was verified on a real device in this session.
