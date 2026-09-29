# Jill's Kitchen 2.2.1 — real-device QA patch: release report (2026-09-30)

## 1. Versions
- Artifact https://claude.ai/artifact/2vhURujrtCpQ1P5jnSsjps — **Version 33**, label "2.2.1". Single file
  `jills-kitchen-single-file.html` (1,866 KB; the 41 portraits inlined as WebP, ~1,023 KB).
- Repo: **`v2.2.1` (annotated tag) = `7dbcaff`**, the QA commit (code, goldens, single file, this report; §14). Rollback
  points preserved and untouched: `v2.2` = `962b494` (Version 32), `v2.2-ux-stable` = `511f237`, `v2.1` /
  `stable-v2.1` = `da79864`.
- Commits after `v2.2`, in order: A `e43da98`, H `17e462b`, B2+I-12 `407cc48`, H2 assets `fc12c2d`, C `8d0cc07`, D+E
  `46ea177`, F+G+I-13 `9a65fec`, F'+C' `a8401ba`, J+K+M `049d1eb`, B1 `dbe4a3c`, #16 `641dbc0`, H2 `d19a768`, #18
  `d3adc10`, docs `0805810`, QA (goldens, single file, this report) `7dbcaff` = the tag; this SHA pin is a docs-only
  commit after the tag.
- Not started, filed for after this release as instructed: `docs/V23_BRIEF.md` (the v2.3 development brief) and
  `docs/V23_STORIES_BRIEF.md` (the stories design).

## 2. Verification labels
**I** = implemented. **T** = targeted verification in the harness (Playwright/Chromium, a 390×844 touch viewport, the
player's real Day 30 / 33 / 35 saves, seeded simulation). **O** = observed in normal real play. Nothing in this report
is marked O: I have not played it on an iPhone; every "real device" item below is I + T and waits for your check (§16).

## 3. The two bugs that were not on the list
- **A migration threw before `load()` and turned a real save into Day 1.** `mainHallMig` (12→9 tables) read `MAIN_MAX`,
  declared as a `const` below `S=load()`; inside `parseSave`'s try/catch the TDZ error became "broken", the save was
  rescued and a fresh game started. Caught with the Day 35 save on the first render; the same trap would have hit
  `crewNameFix` (ROLES/CREW_NAMES). Both constants now live above `load()`, and
  `the_players_saves_load_through_a_real_reload` loads the Day 30, 33 and 35 saves through a page reload and checks the
  day, the money, the crew, the caps, the prep screen and the staff board. (I/T)
- **A sixth chef was called just 廚師** (the name pool had five). The pools are longer than the crew cap; a role-named
  crew member is renamed on load, once. (I/T)

## 4. Fixes grouped by root cause

**Layout: one grid for both halls; nothing of the kitchen in the main hall** (#6, #7, #8, #19; your Day 30/34/35 screenshots)
- Root cause: the main hall grew to 12 tables in four rows over a v2.1 counter band (dots strip, stairs, bus tub, stock
  board, bell), while the side hall had two table sizes with no order and a pink oval in the middle; the kitchen — a
  room of its own since 2.0 with its own pass — was drawn a second time as a band at the bottom of the main hall.
- Fix: `MAIN_MAX` 9 (three rows of three, booths on the back rows), `SIDE_MAX` 9 (a back row of four-tops, then
  two-tops), the same columns and row rhythm in both; the counter band, the hatch and the swing door are gone — the floor
  runs to a skirting line (`FB = LH − 16`) and the three rows share the whole height (`ROWS = 168 / 268+d·.5 / 368+d`);
  the cat trees, the scratcher, the bowl, the pickup point and the chalkboard moved down with it; the tap zone for the
  band is gone (the tab bar, ←→ and 1–4 are the way to the kitchen). The two-top grew a little (rx 25, chairs ±28) to
  hold its own beside the booths. Side hall: an ivory rug with a brass border under the middle row (the
  department-store kind you asked for, not pink), linen curtains on a wooden pelmet, the cat things in two zones (the
  window: perch + cushion; the far wall: tunnel, basket, lounge, moving with DY like the third row); the bush stepped
  right. Kitchen: the stainless prep table in the foreground is gone. Saves with more than nine main tables are migrated
  once: extras move to the side hall when there is room, otherwise they are refunded at their price, with a news line
  (your Day 35: 12+6 → 9+9, nothing refunded; Day 30: 12+2 → 9+5).
- Room tabs during 看店裡 from the shop and the prep screen; the shop remembers the room you were looking at.
- Evidence: `docs/evidence/v221_rooms/F_before_after.png` (v2.2 vs v2.2.1, both halls, Day 35 rush, 390×844),
  `F2_no_band_and_rug.png`, `after_desk_contact.png`, `peek_contact.png`.
- Tests: `main_and_side_hall_are_one_layout_system`; `mature_save_loads_into_2_0`, `touch_controls`,
  `h_i_k_t…`, `z_regression…`, `old_saves_load` follow. (I/T)

**Staff assignment: a board, not a per-person cycle** (#3; your two messages)
- Root cause: 換工作站 cycled a chef's station blindly; then the chooser I built was still per person.
- Fix: the 員工 tab is two lists. 工作分配 — one row per bought station (n/cap, cap = its cooking slots, today's dish
  count) and per floor job (帶位/點餐/上菜/結帳/收桌), the people on it as chips; × takes someone off (a chef goes to a
  待命 row), ＋ lists who can be added with where they come from and one tap adds them; a full station says 已滿; a LV1
  waiter cannot be put on 結帳. Then 員工 — level, wage, training, firing — and 招募. The prep screen warns when a
  station the menu needs has nobody. A chef on standby does nothing and breaks nothing.
- Evidence: `docs/evidence/v221_rooms/staff_board.png`. Tests: `workstation_assignment_is_explicit_with_capacities_and_swaps`,
  `b_staff_are_grouped_by_job`, `economy_ops…`. (I/T)

**Hospitality: one shared counter hid the action from regulars** (#13, Day 35 #1)
- Root cause (traced, §8): Jill's Card, anniversaries, the writer's friend, Jill's own patience treats and the player's
  招待 all drew from one `R.st.treats` (2/day), and a pending occasion (`g.treat`) hid the button. Regulars were the
  first to lose it: every fifth visit is a card visit, and they get Jill's own patience treat at 50% vs 12%.
- Fix: three budgets; the ticket chip always says where a table stands. Tests:
  `hospitality_stays_with_a_guest_from_stranger_to_regular` (stranger → returning → regular all offerable; the card
  visit shows what is coming; the spent budget says 0/2; an interrupted walk gives the use back). (I/T)

**Restocking during service asked twice** (#2)
- Root cause: a `cost ≥ 600` confirm with a 4-second arm keyed by the quantity, which the periodic redraw changed.
- Fix: one tap, immediate feedback (the cost, the cash), 補滿 per row and for all. Test:
  `restock_during_service_is_one_tap_with_immediate_feedback`. (I/T)

**The stock suggestion vs a mature menu** (#1) — §7 and `docs/evidence/v221_stock.md`. (I/T)

**The speech log** (#20)
- Root cause: `scene()` logged the whole script joined with ' / ' under the internal id `dylan` and kind `reg`, and each
  line again as it was spoken.
- Fix: each spoken line once, under the player-facing name, chronological. Test:
  `speech_log_logs_each_spoken_line_once` (Dylan's multi-line scenes and every other scripted conversation). (I/T)

**Records unreadable** (#12): the journal reused the summary's dark chip styles inside a paper card. Fix: rows with ink
labels and gold values. Test: `restaurant_records_are_readable_in_the_journal`. (I/T)

**Portraits** (#11, the swap, Day 35 #4/#5)
- Root cause: figures overlap on the supplied sheets, so a rectangular crop leaked a neighbour; 小林/Sophie were mapped
  to each other's assets.
- Fix: separator polylines along the seams, pinhole filling, the swap. Ten named guests and eight more staff from the
  card sheet (a simple card crop, no keying, as you asked). Tests: `portrait_crops_isolate_each_figure`,
  `q_portraits…`, `named_guests_keep_one_face_and_the_staff_have_theirs`. (I/T)

**Album deep link** (#4), **weather dish on a full menu** (#5), **outdoor project vs furniture** (#9), **the dog's
corner** (#10), **infrastructure and money sinks** (#14, #15, Day 35 #2/#3), **Dylan** (#17), **a second signature** (#16),
**the manual** (#18): §§9–13. (I/T)

## 5. The real-device issues, one by one

| # | Issue | Reproduced? | Root cause found? | Fix | Regression test | Label |
|---|---|---|---|---|---|---|
| 1 | Stock suggestion vs mature consumption | Yes — Day 33 save, 8 seeds: 5.0 dishes/day sold out, first at 162 min | Yes (§7: flat buffer, the cap, and a vicious circle in the history) | per-dish √ buffer, buffers give first, fridge used to the last portion, unmet demand counted and shown | `stock_suggestion_follows_each_dish_and_counts_the_demand_it_missed` | I/T |
| 2 | Restock asked twice | Yes | Yes | one tap | `restock_during_service_is_one_tap…` | I/T |
| 3 | Station assignment unclear | Yes | Yes | the board | `workstation_assignment…` | I/T |
| 4 | Album entry from the summary | Yes | Yes | 看今天的照片 lands on today | `album_has_two_entries…` | I/T |
| 5 | Weather dish on a full menu | Yes | Yes | a swap chooser, nothing silent | `weather_dish_replaces_a_chosen_dish…` | I/T |
| 6 | 用餐區 → 主廳 | — | — | renamed, no save keys | in the layout test | I/T |
| 7 | Main/side hall balance | Yes (screenshots) | Yes | one grid, 9+9, no band | `main_and_side_hall_are_one_layout_system` | I/T |
| 8 | Room navigation in the shop | Yes | Yes | tabs during 看店裡, room remembered | in the layout test | I/T |
| 9 | Outdoor project vs tables | Yes | Yes | project + furniture, the completion text | `outdoor_area_is_a_project…` | I/T |
| 10 | Dog nook | — (new) | — | the corner, rest behaviour, never inside | same test | I/T |
| 11 | Jill's portrait leaks a neighbour | Yes | Yes | separators; 小林/Sophie swapped | `portrait_crops_isolate_each_figure` | I/T |
| 12 | Records too faint | Yes | Yes | readable rows | `restaurant_records_are_readable…` | I/T |
| 13 | Hospitality rules | Yes (regulars lost it) | Yes | three budgets, the chip says why | `hospitality_stays_with_a_guest…` | I/T |
| 14 | Late-game kitchen purchases | Yes (Day 35: only dreams left) | — | 電力 ×2, 洗碗機 (+ 空調 ×3, 主燈) | `infrastructure_you_can_see…` | I/T |
| 15 | Power outages | Yes | — | electrical line; no same incident two days running | same test | I/T |
| 16 | Signature progression | Yes (one dish, v3 at Day 35) | — | a signature dessert with its own progression | `a_second_signature_the_dessert…` | I/T |
| 17 | Dylan presence | Yes (§6) | Yes (partly) | retry never past closing; a trace; the card's dots; a log line | `dylan_leaves_a_trace…` | I/T |
| 18 | Manual | — | — | rewritten | `ui_basics` opens it | I |
| 19 | Kitchen prep table | Yes | Yes | removed | `kitchen_cooks…` runs the room | I/T |
| 20 | Speech log duplicates | Yes | Yes | each line once | `speech_log_logs_each_spoken_line_once` | I/T |

## 6. Dylan: why v2.2 said 12/12 and Days 31–32 showed none
- The v2.2 audit ran a lazy bot on a full fridge at seed 50: the room was never full, so every scheduled visit got in, and
  "spoke 12/12" counted the aggregate `reg` log line that #20 removed — a line that existed whether or not he had said
  anything the player could see.
- Traced on the Day 30 save (seeds 1–3, active and lazy play, Days 30–32): scheduled 12/18 days (p = .55 the day after
  a visit, .85/.97 otherwise), entered 12/12 when scheduled, spoke 5/12 visits, sat in the side hall 2/12, arrived at
  185–200 of 250 minutes on most visits (stage 2: late 75% of the time).
- Your saves: Day 30 last visit 30; Day 33 visits 10, last 33 — so no paid visit on 31 and 32. Two consecutive misses
  from the schedule alone are ~7% ((1−.55)·(1−.85)); on top of that, a full house at a late arrival scheduled a retry
  28–55 minutes later, and a retry landing after closing reached a closed door and **vanished with no note** (the
  silent-drop path); and 35% of visits sit in the side hall, out of the main-hall view, at a time the player is busy.
  Presence ≠ clues ≠ reveal: none of the three story knobs moved.
- What changed: a retry that would land after closing is not scheduled (he looks in at the door now, with the note);
  every day leaves a trace in the save (`S.dylan.trace`: p, planned, planned time, came, when, room, back, door, lines
  — the last 12 days) so "he was not here" can be checked against what the game did; after the reveal his card shows
  the last days as ●◐○ and his arrival is a quiet line in the log. The schedule (.6/.55/.85/.97), the arrival window
  and the four-try retry are unchanged — reported here, not rebalanced.

## 7. The stock recommendation (before/after)
Full write-up: `docs/evidence/v221_stock.md`. In short: the order model agrees with what sells per dish; the fridge (260)
is the binding constraint on an 18-dish menu that sells ~190; v2.2 recorded "sold 12" for a dish that ran out wanting 18,
so it was recommended lower the next day. Now: `ceil(mean + 1.2·√mean + 1)` per dish, the buffers give first under the
cap, the fridge is filled to the last portion, the screen says when it could not hold the day, unmet demand is counted
(`R.st.unmet`), shown ("賣完・估計少賣 N") and blended into the history. Day 33 save, 8 seeds each, a lazy day:
sold-out dishes per day **5.0 → 3.6**, first sell-out **162 → 175 min**, portions sold 193 → 188, left 67 → 71, guests
lost to a sell-out 0 → 0. Demand, prices and customer counts untouched; the fridge cap untouched (a second cold room
would be the honest lever — deferred, it is capacity).

## 8. Hospitality — the actual rules (traced, then changed)
v2.2: `treatWanted/treatGo/treatArrive`, one `R.st.treats` counter, cap 2/day, shared by (1) Jill's Card — every fifth
visit of a regular (`(v+1)%5===0`) sets `g.treat='dessert', g.card` at seating, (2) the anniversary (`g.anniv`) and the
columnist's friend, (3) Jill's own patience treat (eating, patience < .32, 2-minute gap, 12% / 50% for regulars), (4) the
player's 招待 (`treatOfferable`: seated, wait/eat, not treated, **no pending `g.treat`**, `treats < 2`, not Dylan, a drink
in stock). So a card visit hid the button, a treated table hid it, and two automatic treats spent the day's two before
the player could act — regulars first.

v2.2.1: occasions (card, anniversary, writer) are a promise, never capped; Jill's own patience treats keep 2/day
(`st.jtreats`); the player's 招待 has its own 2/day (`st.ptreats`); `st.treats` counts them all for the summary and the
records. The ticket chip: `招待 n` (offerable, uses left) · `集點卡・請甜點` / `紀念日・請甜點` / `請一杯` (pending) ·
`已招待` · `招待 0/2` · `沒東西可請`; Dylan shows nothing (family, not a table). An interrupted walk returns the use
and the item. The manual carries these rules.

## 9. Infrastructure and money sinks (Day 35 #2/#3, #14, #15)
- After Day 35 the player had left: 木樑天花板 180k, 貓的空中走道 300k, 7 recipes to research, and (new) 門口狗狗休息角.
  Everything else was MAX.
- Air conditioning existed only as flavour text ("有冷氣真好" with no unit anywhere; the ceiling fans dream removed the
  hot-day patience cost). Now 空調 14k/38k/95k: a wall unit, a quiet commercial unit, a linear diffuser in both halls;
  hot-day patience cost ×.6 / ×.3 / none; +1 / +3 ambience; guests and reviews praise the cooling only once there is
  some (and say the room is stuffy when there is none). 電力設施 18k/48k: a panel in the kitchen, then a UPS box; power
  cuts halve then stop; breakdowns −25% then −50%. 商用洗碗機 32k in the back: clearing 30% quicker. 主廳主燈 120k among the
  dreams: brass and glass above the sign, the room warms at dusk, +3 ambience. The same incident is never planned two
  days running. 365k of new purchases on top of the 480k of dreams; no taxes, inflation, maintenance or consumables.

## 10. The signature audit and the dessert (#16)
Audit: one signature (`S.signature`, four parts, stove), three versions by portions sold (40 / 110), redesign $800; the
Day 35 player was at v3 with nothing further. Added, contained: Jill's Signature Dessert — a base, a cream, a fruit and a
finish from their own tables (`SIGD`), plated cold at the 冷盤台 in four steps, second on the menu, taken for dessert by
most guests who came for the signature, its own counter (`records.sigd`) and versions (30 / 80: a coulis stroke and mint,
then a spun-sugar cage and gold), its own news line and designer ($4,000 / $800; needs the main signature, Jill's
Kitchen and a 冷盤台), Sweet Signature. Chefs take it at LV5 after Jill's first plate. No recipe-system change; saves
without it are untouched. Evidence: `docs/evidence/v221_rooms/signature_dessert_ui.png`, `signature_dessert_plates.png`.

## 11. Portrait coverage (Day 35 #4/#5)
- A — core regulars with persistent histories (`REGS`): 陳伯伯, Mia, 小林, Leo, Sophie, 王先生, 王太太 — portraits from v2.2
  (小林/Sophie swapped as you confirmed), untouched. Jill and Dylan untouched.
- B — recurring named guests (`NAMES`): VIP 周董 / Madame Lin / Mr. Hart; gourmet 老饕李先生 / Monsieur 杜 / 品酒師 Ken
  (Chloe, Emma stay generic); blogger 吃貨小琪 / 美食部落客 Momo; the mystery critic 戴帽子的客人; the 衛生檢查員. All ten
  lacked identity in v2.2 (a random sprite per visit, a face for the day). Now each keeps one sprite and the card
  portrait on the ticket, in their lines, at the critic's reveal, the blogger's hello, the inspector's arrival, beside
  their reviews.
- C — generic guests: a face for the day, as before.
- Assets used (18, from the card sheet, cut by card boundary with clean margins, no labels): the ten above and eight
  staff (阿珠姐, Hugo, Nina, 阿哲, Momo, 小彤, 阿明, Yuki). Rejected/deferred: 老周師傅 and 阿勇 (only on the checkerboard
  sheet; keying produced remnants and you asked me to stop — they use the plain presentation until cleaner assets);
  the later crew names 小魏/小威/阿芳/阿桂 have no art yet. Contact sheets: `docs/evidence/v221_art/portraits_named18_extracted.png`
  (shown before integration), `named_guests_in_game.png`.

## 12. Save compatibility
Loads and plays: fresh, the five fixtures (v1 staff, v13 photos, v16 backup, v16 staff/Dylan, v18 album), the Day 30 /
33 / 35 real saves (through a real reload, a day, a save and a reload), the pre-2.0 mature synthetic. No renamed keys.
New fields all default: `hallMig`, `st.jtreats/ptreats`, `S.ops.ac/power/dish`, `S.rooms.chandelier`, `S.incLast`,
`S.dylan.trace`, `S.sigDessert`, `records.sigd`, `S.ext.dognook`, `R.dogOut.nook`. The 12→9 migration runs once and
is idempotent (`hallMig`). `mainHallMig` and `crewNameFix` are declared above `load()` (§3).

## 13. Tests
95 tests (`python3 tests/run_tests.py`), all passing at the tag — the final run is `docs/evidence/v221_suite_final.log`
(95 passed, 0 failed, on the exact tree that was tagged and built). New in v2.2.1 (17): speech_log_logs_each_spoken_line_once,
portrait_crops_isolate_each_figure, restock_during_service_is_one_tap_with_immediate_feedback,
restaurant_records_are_readable_in_the_journal, workstation_assignment_is_explicit_with_capacities_and_swaps,
album_has_two_entries_history_from_the_start_and_todays_photos_from_the_summary,
weather_dish_replaces_a_chosen_dish_when_the_menu_is_full, main_and_side_hall_are_one_layout_system,
outdoor_area_is_a_project_and_its_tables_are_furniture_and_the_dog_rests_outside,
hospitality_stays_with_a_guest_from_stranger_to_regular, the_players_saves_load_through_a_real_reload,
infrastructure_you_can_see_and_a_calmer_incident_calendar, dylan_leaves_a_trace_and_never_vanishes_at_a_closed_door,
stock_suggestion_follows_each_dish_and_counts_the_demand_it_missed, a_second_signature_the_dessert_with_its_own_progression,
named_guests_keep_one_face_and_the_staff_have_theirs. Updated to the new behaviour: mature_save_loads_into_2_0 (9 tables,
the refund), touch_controls (the fridge is in the kitchen), goal_ladder (log names), b_staff / economy_ops / z_regression
(the board), h_i_k_t (no band; four dreams), q_portraits (fourteen staff), cats_use_sofa_by_personality (seat share 80% →
55% of a 45% bigger total because 包包 reaches the sofa earlier with the new layout; threshold 50%, measured against v2.2).
Goldens re-recorded for the layout (scenario, frames, the cat fingerprint) with the invariants rechecked (money ≥ 0,
guests served, lost ≤ guests, net = rev + tips + bonus − cost − wages on every golden day; the frames inspected).
Day 35 smoke: one whole lazy day on the real save — 72 guests, the summary, the shop and the board, a save, a reload
(Day 35 kept), no errors. Sims kept in `tools/sims/`.
Release check on the **published** page: Version 33's live HTML was read back from the artifact service (it carries the
tagged `js/game.js` byte for byte), loaded at 390×844 with the Day 35 save, played into the evening with the lazy bot,
saved and reloaded (Day 35 kept, no page errors); the screenshots of that run — title, prep, the four rooms, after the
reload — are `docs/evidence/v221_release/` (T: a Chromium touch viewport, not a phone).

## 14. QA commit
The `v2.2.1` tag points at `7dbcaff`, the commit that adds the re-recorded goldens, the single file and this report
(the tag message repeats the SHA; `git describe` on it prints `v2.2.1`). Everything else in this report refers to the
commits in §1; the only commit after the tag is this SHA pin (docs only).

## 15. Deferred (not done, on purpose)
- A second cold room / a bigger fridge for 18-dish menus (§7): capacity is economy; listed, not added.
- 老周師傅 / 阿勇 portraits (cleaner assets needed); art for the later crew names.
- The photo-wall dream I considered (album photos on the wall): no wall space in the main hall without moving the sign
  or the cabinet; not added.
- Dylan's schedule numbers: measured and reported (§6), not changed.
- The v2.3 briefs: not started.

## 16. Still needs your iPhone
Everything marked T above, in particular: the two halls at your phone's exact viewport (the HUD covers the top ~120 px of
each room; the third row and the bottom edge), the staff board's chip × and ＋ under a finger, the ticket chip states in
a full ticket strip, one-tap restocking mid-rush, the 看店裡 room tabs from the shop, the dog's corner at the street's
left edge, the dessert designer and its four rows, the manual's readability, and whether Dylan's presence reads as
present over a week of your own play (his card's ●◐○ is the check).
