# v2.4 rc6 — evidence

rc6 has two parts:
- P3, the Staff Room, and P4, the Private Dining Room (`docs/v24/AUDIT_AND_PLAN.md` §8–§8.4);
- everything the player asked for from 02:31 to 12:16.

The report is `docs/V24_RC6_REPORT.md`.

Everything here is **TESTED** evidence: screenshots I took in headless Chromium from the player's own saves, at 390×844, and seeded simulations. None of it is the player's observation, and nothing was observed on an iPhone.

## Phone screenshots of the rooms

Made by `tools/sims/v24_rooms_shots.py docs/evidence/v24_rc6 all` on the release build, after the floor's re-layout (08:37), 二樓 becoming an everyday tab again (06:36) and the Private Dining Room's walkways (06:57). There is one line each in `shots.txt`.

The setup:
- The save is the player's Day 61 save.
- The story facts before each state are set as if the earlier beats had happened: the floor leased days before, its furniture in.
- The day itself is played by the bot and photographed as it happens.
- The harness's clock is virtual: a reveal on the prep screen moves when the tool ticks it.

| File | What it shows |
|---|---|
| `reveal_sr_1_works.png` … `reveal_sr_4_first_entry.png` | The morning the Staff Room is finished: last night's works, the walls coming up, the door and its sign 員工休息室, then inside for the first time |
| `sr1_room_evening.png`, `sr1_room_closing.png` | That evening inside, then at closing: the crew in different places |
| `sr_phase1_day.png` … `sr_phase3_closing.png` | The Staff Room in its three phases, afternoon and closing: the pool table (II), the massage chair and the books (III), a frame of pool at closing |
| `shop_rooms_offer.png`, `shop_rooms_bought.png`, `works_floor.png` | 店舖工程 › 二樓的房間: the offer, 動工, 去看看 |
| `look_open_floor.png`, `look_shop_entry.png`, `look_both_rooms.png`, `look_into_room.png` | 店舖工程 › 二樓 › 看看整層: the open floor; then with both rooms as the player drew them (the Private Dining Room top-left, the Staff Room below it, the hall down the right, the stairs bottom-right); a door tapped |
| `pd1_prep_news.png`, `pd1_room_meal.png`, `pd1_summary.png` | The Private Dining Room's second evening: the booking in the news, the party at the long table, the summary |
| `pd3_prep_news.png`, `pd3_room_meal.png` | Phase III: nine booked, at the table |
| `phase1_room_set.png` … `phase3_room_meal.png` | The Private Dining Room in its three phases, set, then with 6 / 8 / 10 at the table |
| `tabs_from_main.png`, `tabs_in_room.png` | The tabs: 二樓 among the rooms; inside the Private Dining Room the tab reads 私人包廂, and the door reads ‹ 二樓 |
| `staff_closing.png` | The Staff Room in Phase III at closing, with both rooms built |
| `reveal_pd_1_works.png` … `reveal_pd_4_first_entry.png` | The morning the Private Dining Room is finished |
| `story_sr_1.png`, `story_sr_2.png`, `story_sr_offer.png` | 《大家待的地方》 as a held panel at closing (「店裡暫停中」, one line per tap), then the project offered |
| `story_pd_yj.png`, `story_pd_yj_log.png` | 怡君: 「有比較安靜的嗎？」「……沒有。」 and the evening's log |
| `story_night_floor.png` | rc5's night of the missing cats on the current build: the floor shown while the story happens up there (`tools/sims/v24_up_shots.py … night`; that Day 52 save is given a finished Lounge, since the floor's story now follows the Lounge, 10:25) |
| `story_hold_phone.png` | An authored beat holding a busy service at phone size (10:32) |

## The morning's reports, at phone size (`morning/`)

Screenshots sent to the player while the work was done, from their own saves:

| File | What it shows |
|---|---|
| `wine_sheet.png` | The wine research at $2,500–$8,000, each card saying what the wine goes with; tonight's list after three researched (the player's Day 71 save, 11:49) |
| `qt3_sheet.png` | 晴 × 阿拓's 「多的。」 as the held panel (Day 71). Triggered mid-service for the picture; in play it comes at closing |
| `main_guests.png` | The dining room on Day 71: the guests' clothes after the no-white-top rule, the waiters in white |

## Simulations (TESTED; `sims/`)

| File | What it is |
|---|---|
| `arcs_from_day71_7100.log` | `tools/sims/v24_arcs.py tests/saves/player_day71_1215.json 20 7100`: the player's Day 71 save, 20 lazy days. Every beat per day, and 晴 × 阿拓's state |
| `pacing_from_day71_7100.log` | `tools/sims/v24_pacing.py 30 7100 tests/saves/player_day71_1215.json`: the long chains from Day 71 — 《那面牆》 and the second floor side by side; the first day of each beat; no two major beats in a day |
| `pacing_from_day67_lounge_gate.log` | The same from the player's Day 67 save, after the 10:25 gate |
| `rooms_pacing_8100.log`, `rooms_pacing_9300.log` | `tools/sims/v24_rooms_pacing.py 60 SEED 1`: the Day 61 save with the floor leased the day before, 60 lazy days, each room's phase bought when open. Shows the beats, the phases, the Staff Room's use, the Private Dining Room's evenings by phase, the money |
| `chain_from_day71_7700.log` | `tools/sims/v24_rooms_pacing.py 100 7700 -1 tests/saves/player_day71_1215.json`: the player's Day 71 save as it is, 100 days, the floor bought when offered — 《那面牆》, the floor, both rooms and their phases |
| `chain_from_day52_7700.log` | The same from the Day 52 save, which has no Lounge (nobody builds one): 《那面牆》 settles; the floor's story does not begin, as the 10:25 rule says |
| `lines_audit_day71_before.log`, `lines_audit_day71_after.log` | `tools/sims/v24_lines_audit.py tests/saves/player_day71_1215.json 30 7100`: every story line before and after 30 days, with what its next step waits for — before and after the 12:17 fixes |
| `fresh_300.log` | `tools/sims/v24_fresh.py --days 24 --seed 300`: a new game's first 24 days (秀琴阿姨 from Day 1, 怡君 early) |

## Golden re-records (with proof)

- `golden_scenario_proof.log` and `golden_scenario_proof_revert.py`.
- `golden_frames/`: the key-by-key report, the DOM diff and the side-by-side screens.

## Regression

- `full_run_s0.log`, `full_run_s1.log` — the whole suite (181 tests) in two shards on 0767ac5, the release's game and tests.
