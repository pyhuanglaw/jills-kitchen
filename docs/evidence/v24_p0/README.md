# v2.4 P0 — evidence

The foundations of the implementation pass (`docs/v24/implementation_pass_2026-10-01.txt` §A, §B, §C, §U P0), as
revised by the two pacing corrections and the 秀琴阿姨 canon change (`docs/v24/AUDIT_AND_PLAN.md`).

What P0 is:
- **A1 後場整理區.** The old 營運升級 「後場休息室」 is renamed, with the same purchase and the same +2 staff. Its
  text is work storage. In the kitchen it is a wire rack by the door: aprons, towels, bins, supplies, hooks with
  aprons, a clipboard. There is no seat and no door.
  - `kitchen_rack_phone.png` and `kitchen_rack_zoom.png` show it in the Day 52 save at 390×844.
- **A2 tenure.** `tenure(m)` is a class, never a date. The legacy crew are 熟手, except:
  - 阿珠姐, 秀琴阿姨 and 阿德師傅 are 資深;
  - 小彤 is 較新, and 熟手 after 45 counted days.

  New hires are 新, 熟手 from 10 days and 資深 from 60. A legacy card reads 「資深（v2.3 以前就在）」 instead of
  「在店 3 天」. 《第二層左邊》 goes to 阿珠姐 when she is in.
- **A3 presence.** `setCrewAway(m, off|late|left)` is for one day, set only by an authored beat. Someone not here is
  not drawn and does no work. A late arrival walks in from the street; a leaver walks out. The summary says
  「今天沒來」. Wages are unchanged. There is no rota and no UI.
- **The walk-over.** `staffWalkOver(m, table)` moves a cleaner or server to a table for an exchange, then back to
  work. A cook never does this. It replaces the planned chef table visit, which the canon change made unnecessary.
- **Eras and pacing.**
  - `V24_ERAS` runs 怡君 → 《那面牆》 (2 days after the spare key) → 二樓 (2 days after the settlement).
  - Dormancy: an era whose people are absent stops waiting after 5 days. It never wakes once a later era has begun.
  - There are no global gaps. A stage waits only for its own `gap`. Major beats stay capped at one a day by the
    arbiter.
  - Nothing fires at the very start of the first day played.
  - `v24Visits` brings the people a due beat needs.
  - A weather memory tracks the rain.
- **Story illustrations.**
  - `STORY_ILLUS`: `scene(lines, done, {illus})` shows the picture over the lines.
  - A line can carry a name without a portrait.
  - A journal beat can reopen its picture (看插圖).
  - Pictures are not album photos.
  - All four are the player's pictures (`docs/v24/art/`, packed by `tools/story_art.py`). The game-style stand-ins
    (`drawFlat`, laid out like the player's flat, `drawIllusIntro`, `drawIllusSettled`) show only if a picture is
    missing, labelled 插圖待補.
  - `scenes_three_phone.png` shows three of them in the scene at 390×844. The lines in it are test lines.
- **Names.** No staff name and none of the outside cast is a random guest any more:
  - Kevin → Eric;
  - the student 阿哲 → 阿彥, Yuki → Mina;
  - the couple Sam 與 Nina → Sam 與 Lena.
- 秀琴阿姨's sprite looks like her portrait: a lavender headscarf, a dark top and a lavender apron.

## Tests

`tests/v24_tests.py` has 8 tests, all passing:
- the area and its +2;
- tenure classes;
- one day's presence;
- the walk-over;
- eras and dormancy;
- illustrations;
- name pools;
- every player save loads with nothing fired.

The related older tests pass. `staff_learn_places…` was updated for A2: the legacy card shows the class, not the days
since v2.3. `economy_ops_duties…` was updated for the new name.

## The two goldens: re-recorded, with proof (`golden_proof.txt`)

Both golden runs are new games, so no legacy crew and no v2.4 story is involved. Both changed only because of the
renamed random guest names.

- With the **old** name pool put back, the current code reproduces both recorded baselines **exactly**:
  - `golden_scenario`: all three day digests;
  - `golden_frames`: every sample, both day digests, the eight screens.
- With the **new** pool, `golden_scenario` differs only in `reviewHash` on days 2–3. The three differing reviews
  are identical except for the reviewer's name (Yuki→Mina, Kevin→Eric, 阿哲→阿彥).
- `golden_frames` differs first at day 1, t=37.1, in the DOM: the ticket rail reads 「阿彥」 where it read 「阿哲」.
  The text is otherwise identical.

Only then were the two baselines re-recorded.
