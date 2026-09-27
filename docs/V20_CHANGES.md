# Jill's Kitchen 2.0 — what changed, and how it was checked

Foundation: V18.1.1 (the published hotfix) + the V18.2 systems (Dylan presence, regulars' lives, weather and special days,
rating story, records, stock panel, ops upgrades, duties, 60 achievements, incidents, themes, set menus, service worker).
Checkpoints on `master`: `v20-wip-1` (rooms + the kitchen line), `v20-wip-2` (money ladder + the cats' things), `v20-wip-3`
(Dylan arc + tests), then the art passes. Every patch was a python script in the scratchpad asserting exact match counts.

## 1. The restaurant is four spaces (one simulation)
- `ROOMS` main / kitchen / side / front. `let room` is the room on screen; only that room is drawn (`drawScene` dispatches
  to `drawOtherRoom`). Everything that moves carries `.room/.troom`; `stepTo()` walks it through the doorways
  (`doorway(a,b)`, every doorway goes through the dining room; `nextHop`). Guests spawn on the street and walk in;
  leaving guests walk out to the street (`sendOut`). Waiters serve the side room and the terrace through the doorways.
- Navigation: the tab strip under the order strip (`#roomTabs`, badges = things that need you there, red = urgent,
  `NEW` on a room's first day), a swipe on the scene (never over a table, a station or a cat: those are taps), keys 1–4 and
  ←/→ on a keyboard, the counter/arches/doors in the scene. `roomAlerts()` counts per room.
- Off-screen rooms keep simulating (guests, waiters, cats' trips, the cooks); nothing depends on being looked at.
- The album camera only takes pictures of the room on screen (`flushMem` skips memos of other rooms).

## 2. The kitchen is a line, and the cooks cook the dish
- Composition (`drawKitchenRoom`): tiled wall with a sage backsplash, the hood, a pan rail and jars; one continuous counter —
  sink, prep boards, the range (2 or 3 burners per row; 6 with the expansion), the under-counter oven (1 or 2 doors), the
  coffee machine; homely fillers (bread basket, fruit bowl, kettle) where equipment is not yet bought. The pass runs across
  the middle under heat lamps with the ticket rail; below it the pickup side: mat, crates, bin, the fridge (= stock), the
  cold room, the swing door to the dining room.
- The food is the tray's own vessel renderer (`drawStageFood`, split out of `drawStage`) drawn on the burner/board/oven/
  machine at 0.32–0.62 scale: the pasta in the pot, the duck in the pan, the soufflé in the oven, the pour of a hold, the
  spit of a sear, steam, the ingredient that just went in (`s.pop` now fades).
- The cooks are actors (`R.ck[id]`, `kitchenUpd`): `chefBeat()` picks what a cook attends (plating first, then the oldest
  handwork, then a sear about to be ready, then watching the pot, else his home spot); they walk the aisle
  (`200+16·lv` u/s). `stepSpot()` decides where a step happens from the recipe: knife work at the board, `瀝乾` at the sink,
  oven dishes at the landing / inside the oven / at the pass afterwards. Handwork (`add/hold/dose/tap/work`) waits for the
  cook to be there (`cookPresent`); passive steps (boiling, searing, baking) do not. A chef's finished dish goes to the pass
  as a `plating` phase (`0.7 + 0.6·chefDelay` s) before `finishJob` — the plate grows in under the lamp with its garnish.
  Jill's own dishes plate at once as before (her tray is the manual moment).
- Taps: a burner/board/door with a job opens its tray; an idle one only answers on release (a swipe from it still works);
  the fridge/cold room open the stock panel; the door returns to the dining room.
- Tools in hand: knife at the board, spoon at the pot, bottle/shaker for pours and doses, the plate carried to the pass.
- Two cooks of one duty: `chefHandles` keeps a dish with the cook who started it; `crewUpd` gives each cook of a duty an
  equal share of the free burners, so a second stove chef works in parallel instead of watching the first.

## 3. The money ladder (data-driven: `PROJECTS`, `EXTERIOR`, `CATGEAR`, `SIDE_TABLE_COST`, `FRONT_TABLE_COST`)
- Large: 露天座位 25k (3 tables, +5% pull, +1 queue), 大出菜口 15k (waiters −15% reaction, wider pass, 11 plates),
  冷藏庫 30k (+80 capacity), 廚房擴建 45k (six-burner range: LV4→5, LV5→6 burners; +2 crew), 側廳 60k (6 tables, 2 booths,
  +2 crew, +2 menu, the wine bar moves in). Effects live in `crewCap/menuCap/fridgeCap/queueMax/waiterDelay/stoveSlots/
  expected()` (`tablesTotal()`, `extAttract()`).
- Street: 季節布置 2k, 門口長椅 3k (+2 queue), 門口花箱 4k, 門口串燈 5k, 招牌燈 6k, 遮雨棚 8k (3 colours) — each drawn on the
  street; all six +3%.
- The cats' things: 紙箱 800 (dining room), 大睡墊 1.2k, 藤籃 1.8k, 貓隧道 2.5k, 窗邊貓架 3.5k, 側廳貓窩 4.5k (side room),
  三層大跳台 12k (two more high perches).
- A purchase is an event: `projectReveal()` — dust and 「施工中」, then the card (what changed, Jill's line, who reacted,
  what it opens), 「去看看」 shows the room from the shop; the next day the tab says NEW and Jill mentions it at the door.
- The summary shows 存錢的目標 (`goalLadder()`): one within reach, one a few days away, one to dream about, with
  「還差 $x · 照今天的收入約 n 天」.

## 4. The cats and their things
- `catDecide` weighs every owned piece by personality (`G.w`), doubled on its first two days; a piece in the side room is a
  trip through the arch (`catGoGear` → `gearAway`; the cat is `away` and hidden from the dining room, drawn in the side
  room at its spot); `gearTick` ends the visit and brings it back. The box: 柔柔 sits inside (only her head shows, the box
  front is drawn over her), pounces on a cat that passes (`ambush` photo, both run). The tunnel: the dash out the other end.
  First use per cat: 「牠自己找到的」 photo (when the room is on screen), a log line, the `newspot` achievement.
- The five cats never leave the building: no cat state routes to `front`; the away trips only go to the side room.

## 5. Dylan
- `DYLAN_ACT` before/after grew by twelve exchanges in the established tone. `DYLAN_SCENES` play once each when their
  condition holds (the side room, the kitchen, the terrace, the pass, the cold room, the JILL sign, a cat on a new thing,
  the stage-2 clues 「菜單我自己拿了」「水我自己倒了」, 王太太 noticing); `dylanScene()` is tried first when he speaks.
  Once the side room exists he sometimes takes a table there. After the reveal the journal says
  「Jill 的先生。結婚 11 年。打烊以後，有時候會留下來——然後隔天再來追一次。」

## 6. Art
- People: arms pose (swing with the steps, together in front to carry, one bent up to chop/stir/pour, crossed while
  watching the pot); chefs in the double-breasted jacket with a coloured neckerchief; waiters and the cleaner with aprons;
  customers with striped, dotted and cardigan tops.
- Evening: tea lights on the tables (level 2+), each room's lamps (`lighter` pools), sconces in the side room, the street
  lamp and the windows on the wet pavement. Cats' ears twitch.

## 7. Save compatibility
- `newState()` gained `gear`, `gearUse`, `newRooms`, `reveal`; `fillDefaults` merges `rooms/ext/gear/gearUse/newRooms`
  key by key, so a V18.1.1 Day-25 save loads with everything it had and opens the street, the dining room and the kitchen
  (the side room is a purchase). `perchOcc` is sparse (the two deluxe perches sit after the wall perches). Checkpoints
  carry `j.plating`; `R.ck` is rebuilt.

## 8. Tests (`tests/run_tests.py`, 53)
- New: `mature_save_loads_into_2_0`, `kitchen_cooks_walk_the_line_and_plate`, `purchases_change_the_place`,
  `cats_use_their_things_and_stay_inside`, `goal_ladder_and_dylan_scenes`.
- Adapted to the room model: `touch_controls` (the burner is tapped in the kitchen room), `waiting_bench` (a party still on
  the street has no place yet), `dylan_pays_tidies_and_is_not_staff` (a doorway is not a teleport).
- Golden scenario / frames / cat fingerprint re-recorded for 2.0 (guests walk in from the street; chefs plate at the pass).

## 9. Performance (headless Chromium, 390×800, mature save, rain)
- ms of JS per frame (update + draw): dining room 12.6 (V18.1.1: 13.8), kitchen 4.3, side room 3.1, street 2.5. The first
  frame of a room after a change rebuilds its cached background (100–240 ms once).

## 10. Known limits / deferred
- Cats do not visit the kitchen. The side-room arch in the dining room sits at the right end
  of the back wall, mostly off-screen on phones (the tab strip is the primary navigation). No real-device (iPhone)
  verification in this session — see the report.
