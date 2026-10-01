# v2.4 rc5 — evidence

rc5 = P2 the Second Floor (`docs/v24/AUDIT_AND_PLAN.md` §7, §7.1), the two staff lists and 許葳 (the player, 19:07–19:16,
`docs/v24/staff_pools_1907_2026-10-01.txt`), and the fixes the player reported at 17:48 and 18:32
(`docs/v24/next/`). The report is `docs/V24_RC5_REPORT.md`.

## Phone screenshots (390×844, headless Chromium, real play; T, not O)

Made by `tools/sims/v24_up_shots.py docs/evidence/v24_rc5 all`; one line each in `shots_up.txt`. The Day 52 save is
played with the story facts before each beat set as if the earlier beats had happened (the dates moved so the beat is
due); the day itself is played by the bot and photographed as it happens.

| File | What it shows |
|---|---|
| `u3_inspect_1.png`, `u3_inspect_2.png` | The landlord's afternoon (the day's major, at the start of the service): Jill asks to go up; 「地板是好的，窗戶也是好的。」 — words only |
| `u4_start.png` | The night's day starts: the landlord and the air conditioner, 「好了。門我帶上了。」 |
| `u4_side_door_closed.png`, `u4_side_door_ajar.png` | The side room in the evening: the stair door shut; later a hand open, the stairwell light on the floor |
| `u4_notice.png`, `u4_search.png` | Closing: 「柔柔呢？」…; everyone looks |
| `u4_door_found.png` | 「這個怎麼開著？」 |
| `u4_up_dark.png`, `u4_up_found.png` | Upstairs before the light and after: 柔柔 at the window, 小齁 comes to Jill first |
| `u4_scene_1.png`, `u4_scene_2.png` | 「妳們兩個。」, then 「……這裡滿大的欸。」 |
| `u4_down.png`, `u4_latched.png`, `u4_after.png` | Down, the cats first; the door latched (「扣好了。」); the closing goes on, no 二樓 tab |
| `u6_ask_1.png` – `u6_ask_3.png`, `u6_project.png` | The call at the stair door: 「……樓上現在還空著嗎？」 … 「整層？」「整層。」; the project offered |
| `u7_shop_card.png`, `u7_reveal.png`, `u7_floor_day0.png`, `u7_street.png` | 店舖工程 › 二樓（整層）; bought; the floor that evening (empty, two boxes); the street, the windows warm |
| `up_open_floor_day6.png`, `up_open_floor_night.png` | Six days on: the furniture, the cats' things, the crew's traces; 柔柔 back at her window |
| `staff_two_pools_top.png`, `staff_lounge_roster.png`, `staff_lounge_full.png` | The player's Day 61 save: 餐廳員工 12/12 · Lounge 員工 2/5 → 5/5; the Lounge list by name |
| `staff_lounge_at_work.png` | The Lounge that evening: Evan's new look, 安安, the line 晴 × 阿拓 starting the first evening he is there |

## Simulations (T)

- `sims/pace52_*.log`, `sims/pace61_*.log` — `JK_BUY_UP=1 tools/sims/v24_pacing.py 60 SEED [save]`: the Day 52 save and the
  player's Day 61 save, sixty lazy days, three seeds each; the simulation buys the second floor the first evening it
  can.
- `sims/fresh_grow_*.log` / `.json` — `tools/sims/v24_fresh.py --days 120 --plan grow`: a new game that keeps buying
  what it can afford; the Second Floor's first beat waits for the restaurant's full size.

## Regression

- `full_run.log` — the whole suite during the evidence pass (650e841's tests minus two updates): 149 passed, 2 failed
  (both tests not yet in step with the new data: twenty-five staff portraits now; the player's Day 61 save already
  has v2.4 story facts).
- `rerun_after_fix.log` — those two and the manual test after the update: 3 passed.
- `full_run_2.log` — the whole suite after those updates: 151 passed, 0 failed.
- `full_run_final.log` — the whole suite on the release commit (92751b0): 151 passed, 0 failed.
