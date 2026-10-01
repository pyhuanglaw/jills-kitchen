# v2.4 rc4 — evidence

rc4 = P0 + P1 (`docs/v24/AUDIT_AND_PLAN.md` §6), with the player's fresh-game premise of 15:07
(`docs/v24/xiuqin_from_day1_2026-10-01.txt`) and the 15:08 / 15:11 requirements
(`docs/v24/requests_1508_1511_2026-10-01.txt`). P0's own evidence is in `docs/evidence/v24_p0/`.

## Phone screenshots (390×844, headless Chromium, real play; T, not O)

Made by `tools/sims/v24_shots.py`; the list with one line each is `shots.txt`.

| File | What it shows |
|---|---|
| `day1_helper_arrives.png` | A new game, Day 1, ~21:15: 秀琴阿姨 has walked in and tidies beside a table nobody is at; her first lines |
| `day1_coach.png` | A few seconds later, after her three lines: the coach names her, once |
| `day1_closing_helper.png` | After 21:30: still tidying during the closing (the portrait line on screen is held there because the shot steps the game without its timers); she goes home ~20 s in |
| `day2_news.png` | Day 2's prep screen: the news says who came to help |
| `day4_staff_tab.png` | Day 4, when the staff tab opens: the recruit list says the first cleaner is her (here the crew is full: a waiter was hired on Day 3) |
| `hire_her_line.png` | Hiring the first cleaner is hiring her: her one line over the shop. For this shot the restaurant level was raised to make room (as expanding would) |
| `hire_her_card.png` | Her card: 清潔員, 「今天起正式上班」 |
| `yj_meet_helper_scene.png`, `yj_meet_helper_scene_line4.png` | A new game, Day 8, no cleaner hired: 怡君 came late; her mother, in to help close up, walked over — 「妳怎麼來了？」 … 「不能吃妳工作的喔？」 with the player's `yj_intro` |
| `day52_update_note.png` | The player's Day 52 save, next prep screen: the one 2.4 note (systems only) |
| `manual_staff.png`, `manual_story.png` | The manual: 秀琴阿姨, 晚點到; 插圖, 店外的生活 |

## Simulations (T)

- `sims/pacing_*.log` — `tools/sims/v24_pacing.py 40 SEED`: the player's Day 52 save, forty lazy days, five seeds.
- `sims/fresh_*.log` / `.json` — `tools/sims/v24_fresh.py`: a new game played by the perfect bot with three shop
  plans (the cleaner hired Day 4, Day 14, never), and the control run without her (`--noxqh`).
- `golden_proof.txt` — why `golden_frames` was re-recorded, and the proof that nothing else moved.

## Regression

- `full_run.log` — `python3 tests/run_tests.py`, the whole suite on the release commit.
