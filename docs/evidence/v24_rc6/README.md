# v2.4 rc6 — evidence

rc6 = P3 the Staff Room + P4 the Private Dining Room (`docs/v24/AUDIT_AND_PLAN.md` §8, §8.1–§8.3), with the player's
corrections of 04:06–04:26 (the floor's view, the Art Deco room with the long table) and of 05:19–05:23 (the Staff
Room redrawn bright and warm; 二樓 no longer an everyday tab, the floor shown when it changes). The report is
`docs/V24_RC6_REPORT.md`.

## Phone screenshots (390×844, headless Chromium, real play — OBSERVED by me, not by the player)

Made by `tools/sims/v24_rooms_shots.py docs/evidence/v24_rc6 all`; one line each in `shots.txt`. The player's Day 61
save, with the story facts before each state set as if the earlier beats had happened (the floor leased days before,
its furniture in); the day itself is played by the bot and photographed as it happens. The harness's clock is virtual:
the reveal on the prep screen moves when the tool ticks it.

| File | What it shows |
|---|---|
| `reveal_sr_1_works.png` … `reveal_sr_4_first_entry.png` | The morning the Staff Room is finished: the floor as it was last night (the works), the walls coming up, the room's door and sign 員工休息室 with the card, then inside the first time (the tab reads 員工休息室) |
| `sr1_room_evening.png`, `sr1_room_closing.png` | That evening inside (nobody up yet), and its closing — the crew in different places |
| `sr_phase1_day.png` … `sr_phase3_closing.png` | The Staff Room in its three phases, in the afternoon light and at closing: the same room, more lived in |
| `shop_rooms_offer.png`, `shop_rooms_bought.png`, `works_floor.png` | 店舖工程 › 二樓的房間: Phase I and its price; 動工; 去看看 — the works on the floor, shown from 店舖工程 |
| `look_open_floor.png` | 店舖工程 › 二樓 › 看看整層 on the open floor (no room yet, no 「？」) |
| `look_shop_entry.png`, `look_both_rooms.png`, `look_into_room.png` | The same with both rooms: closed rooms, their signs, nothing of the inside; the chalked 「？」 on the undecided corner; a door tapped — the room's own view |
| `pd1_prep_news.png`, `pd1_room_meal.png`, `pd1_summary.png` | The Private Dining Room's second evening: the booking in the news; the party at the long table (the tab reads 私人包廂); the summary's chip |
| `pd3_prep_news.png`, `pd3_room_meal.png` | Phase III: nine booked, at the table |
| `phase1_room_set.png` … `phase3_room_meal.png` | The Private Dining Room in its three phases, set at dusk for the evening's booking, then with 6 / 8 / 10 at the table |
| `tabs_from_main.png`, `tabs_in_room.png` | The tabs from the dining room (休息室 and 包廂 among the rooms, no 二樓) and inside the Private Dining Room (私人包廂 lit; the door reads ‹ 側廳) |
| `staff_closing.png` | The Staff Room in Phase III at closing, with both rooms built |
| `reveal_pd_1_works.png` … `reveal_pd_4_first_entry.png` | The morning the Private Dining Room is finished: the same reveal — the green front and 私人包廂 |
| `story_sr_1.png`, `story_sr_2.png`, `story_sr_offer.png` | 《大家待的地方》 and the project offered |
| `story_pd_yj.png`, `story_pd_yj_log.png` | 怡君: 「有比較安靜的嗎？」「……沒有。」, and the evening's log |
| `story_night_floor.png` | rc5's night of the missing cats on the current build: the floor is shown while the story happens up there, 二樓 a tab only then (`tools/sims/v24_up_shots.py … night`) |

## Simulations (TESTED)

- `sims/rooms_pacing_8100.log`, `sims/rooms_pacing_9300.log` — `tools/sims/v24_rooms_pacing.py 60 SEED 1`: the player's
  Day 61 save with the floor leased the day before, sixty lazy days; the player says 開始規劃 to each offer and buys each
  phase the first evening it is open. Per day: the beats, the phases, the Staff Room's use, the Private Dining Room's
  evening (booking, minimum, what was eaten, walk-ins), the money; then the summary by phase.
- `sims/chain_from_day52_7700.log` — `tools/sims/v24_rooms_pacing.py 100 7700 -1 tests/saves/player_day52.json`: the Day
  52 save as it is, a hundred days — 《那面牆》, the second floor's arc, the floor bought when it is offered, then the
  two rooms.
- `sims/rooms_pacing_*.json` — the per-day rows.

## Regression

- `full_run.log` — the whole suite on the release commit.
