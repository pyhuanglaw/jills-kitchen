# The player's saves — QA checkpoints

Real saves from the player's iPhone, kept unchanged (tests and tools load copies into a fresh page; nothing writes
back here). They are **checkpoints**, not a matrix (the player's 05:42 testing strategy,
`docs/v24/testing_strategy_0542_2026-10-02.txt`): a save is used to reach a state quickly — a late-game feature, a
legacy migration, a bug — and each test picks the one closest to what it checks. No test runs every save through
everything; the one test that loads them all (`v24_rc6_the_floor_and_its_rooms_are_tabs`) only checks
that each loads clean.

When the player sends a new save: add it here with its era, what it is, and what it is a checkpoint for. Do not add it
to every run.

| Save | Era (when it was written) | What it is | Checkpoint for |
|---|---|---|---|
| `player_day30.json` | v2.2, no story state | the mature Day 30 game: 10 on the crew, the side room, the pass | **legacy** loading and migration; the classic mature screenshots |
| `player_day33.json` | v2.2 | 12 crew, terrace, kitchen extension, cooler | demand and stock simulations |
| `player_day35.json` | v2.2 | money $6 | money edge cases (the emergency cash) |
| `player_day39.json` | v2.2 | the side room's glass | story-day simulations (v2.3) |
| `player_day42.json`, `player_day44.json` | v2.2 | the ceiling, $207k / $156k | spare mature checkpoints (not used) |
| `player_day46.json` | v2.2 | the chandelier | social and campaign simulations |
| `player_day48.json`, `player_day49.json`, `player_day50a.json` | v2.2 | late v2.2 states | `player_day48` in one v2.3 test; the others spare |
| `player_day50b.json` | v2.3, story state, the crew counted as 1-day hires | the catwalk | **tenure migration** (legacy crew are classes, not two-day hires) |
| `player_day52.json` | v2.3 | the **mature late-game** save: 12 crew, everything downstairs bought | the long chains (怡君 → the wall → the second floor → the rooms), the economy, the v2.4 pacing simulations |
| `player_day52a.json` | v2.3 | a second Day 52 | spare |
| `player_day61.json` | v2.4 rc5 | the **newest**: the Lounge open, 14 crew, 怡君 met | rc5 / rc6 states — the second floor and the two rooms are reached from it by setting the earlier story facts (`tests/v24_tests.py` `FLOOR_TAKEN`, `PD_OPEN`; `tools/sims/v24_rooms_*.py`) |
| `player_day61_0933.json` | v2.4 rc5 (the player's own, 2026-10-02 09:33) | Day 61 evening: Lounge I and II, the four bar bites on today's menu, the menu at its cap of 20, 17 crew (Evan, 沈晴, 阿拓, 安安, 許葳 among them) | the menu-cap bug of 09:55 (`v24_rc6_bar_bites_take_no_menu_slot`); the player's reports of 09:33–09:59 (阿拓's face, repeated lines, the Lounge's comments, the summary) |
| `player_day65_1004.json` | v2.4 rc5 (the player's own, 2026-10-02 10:04) | Day 65 morning: Lounge III, 《那面牆》 just begun, Sophie and Mia in the same room once in a fortnight, their story not begun | the 10:05 report (`v24_rc6_sophie_and_mia_begin` uses its Day 61 sibling) |
| `player_day67_1016.json` | v2.4 rc5 (the player's own, 2026-10-02 10:16) | Day 67: everything bought (nothing left to spend $202,255 on), the Lounge finished on Day 57, the wall under way, nothing of the second floor; Sophie and Mia's first page with lines that were not theirs | the 10:21 report (`v24_rc6_more_to_spend_on`), the 10:25 legacy check (`v24_rc6_a_finished_lounge_opens_the_floor_in_a_mature_save`), the 10:08 page (`v24_rc6_story_pages_keep_only_their_own_lines`), the summary and the new places' photos |
| `player_day68_1033.json` | v2.4 rc5 (the player's own, 2026-10-02 10:33, sent at 11:59) | Day 68 mid-service (a checkpoint at 22:08, rain, the truffle day): $425,697 with everything downstairs bought, Lounge III (finished Day 57), 19 crew all LV5, 《那面牆》 and Sophie and Mia under way, nothing of the second floor | the 10:25 legacy check from a later day, the new places to spend on (the wine research priced like a dish's after the 11:49 report) |
| `player_day71_1215.json` | v2.4 rc5 (the player's own, 2026-10-02 12:15, sent at 12:16) | Day 71 mid-service (a checkpoint at 20:00, made by the backup: the title offers 繼續營業 · 20:00): $647,890, 晴 × 阿拓 stalled (qt_1 Day 61, qt_2 Day 67, 「多的。」 due since Day 70 and lost to 《那面牆》's major beat that day), 《那面牆》 at 王先生, Sophie and Mia at their second beat, nothing of the second floor | the **latest real save** for rc6 (the release check on the published page); the 12:16 report (`v24_rc6_qing_and_tuo_move_on`); the arcs played forward from it |
| `player_day73_1452.json` | v2.4 rc6 (the player's own, 2026-10-02 14:52, sent at 15:15) | Day 73 mid-service (a checkpoint at 17:04): $165,028, 19 crew, Lounge III (finished Day 57), the piano bought on Day 71, 「多的。」 done, the second floor's first word (up_hint) | the 15:15 report 「我又玩了幾天都沒什麼劇情」 (what was stalled and why) |
| `player_day74_1508.json` | v2.4 rc6 (the player's own, 2026-10-02 15:08, sent at 15:15) | Day 74 mid-service (a checkpoint at 21:48; the tests clear it and start at the prep): $244,744, the crew's word on the floor upstairs (up_staff), Ken and 杜 visiting every evening, nothing of Ken's chapter after the Lounge | the **latest real save** for rc7: Ken's legacy entry and his tastings (`v24_rc7_ken_*`, `tools/sims/ken_chain.py`), the landlord's afternoon, a line finds its table, the story pacing (`tools/sims/story_per_day.py`), 予安 (the piano bought on Day 71) |
| `player_day92_2105.json` | v2.4 rc8.4 (the player's own, 2026-10-04 21:05) | Day 92 after closing (the shop): $1.18M, 20 crew (ten of the floor), the second floor leased on Day 85 with the Staff Room at Phase I (given with the lease, rc8.2), no Private Dining Room yet, Ken's collaboration under way | the 2026-10-04 reports: the Staff Room never used in a service (`rc85_the_crew_go_up_to_the_staff_room_in_a_busy_evening`, `tools/sims/staff_room_day.py`), the Phase II button (`rc85_the_rooms_upstairs_are_bought_by_their_buttons`) |
| `player_day89_0448.json` | v2.4 rc8.5 (the player's own, 2026-10-05 04:48 — another game than the Day 92 one) | Day 89 mid-service (a checkpoint at 18:59: the title offers 繼續營業), Dylan out since Day 69 | the 2026-10-05 report 「Dylan已經揭露但在房間還是沒寫Dylan」 (`rc86_dylan_is_named_in_their_room`, `tools/sims/dylan_room_shots.py`) |
| `cooking_day3_0156.json` | v2.5 cooking branch, private test page Version 10 (the user's own, 2026-10-09 01:56, sent with the 「拿鐵咖啡做好無法出杯」 report) | Day 3 mid-service (a checkpoint at 18:33): a new game's third evening, $2,172, no crew; a latte made at 17:2x and still waiting at the coffee machine, nothing lit, no tap taking it out | the 送飲料 fix (`cooking_the_users_day3_latte_goes_out_by_a_tap`). Named `cooking_…`, not `player_…`, so the tests that load every mature save leave it alone |
| `player_day6_1254.json` | v2.5 private test page Version 22 = 8ded2e2, round 2 (the user's own, 2026-10-10 12:54, sent with 「從第二天都沒有」 「他有煮 但都沒有裝盤」) | Day 6 prep, $1,035, level 1: 秀琴阿姨 (cleaner LV2), 阿德師傅 (chef LV1, the range), 小茉 (waiter LV2); the first three days' lessons done (S.jillMade); a mid-service checkpoint left from an earlier day | the early game with the first hires (Day 2 hiring); the cooks taking any step (a LV1 cook plates); the plates at the rack; the 今日任務 list and the kitchen's chips; the release's live check (the user's latest real save) |

A release's full regression covers a few representative ones through the tests that need them — fresh (a new game),
legacy (`player_day30`), mature late (`player_day52`), current (`player_day61`) — never every save × every test.
