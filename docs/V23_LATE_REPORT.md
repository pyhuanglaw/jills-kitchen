# JILL'S KITCHEN v2.3 late game — release report (2026-10-01)

**Legend**
- **I** — implemented: the code is in the repo.
- **T** — tested: an automated test, a seeded simulation, or a screenshot inspected in headless Chromium at phone size.
- **O** — observed by the player on the phone. Nothing in this report is O yet; §11 is what to look at.

**Branch and builds**
- Branch: `master`. Tag: `v2.3-rc3`.
- Published to the player's usual URL, https://claude.ai/artifact/2vhURujrtCpQ1P5jnSsjps (saves live there).

**Briefs filed verbatim**
- This round: `docs/v23/qa5_2026-10-01_late_game_upgrades.txt`, with the player's four references in `docs/v23/refs/`.
- Next round, not started: everything in `docs/v24/`.
  - Staff Lives brief, two outside casts with pictures, the Staff Room brief, the Private Dining Room brief and master reference.
  - The Second Floor correction and the long-arc direction that supersedes it, the floor layout sketch, the phases note.

## 1. Commits since v2.3-rc2 (b67dec6)

| Commit | What |
|---|---|
| dcceeff | Sophie × Mia 「今天一起來」 from the player's illustrated picture (was a concept-sheet crop) |
| 8863eab | 後場工程: 走入式冷藏庫 (cold storage 260 → 400) and 廚房二期 (a second coffee machine, two more people) |
| eb8b1f5 | Five kinds of dog, drawn by shape, and the dog's house by the door |
| b11c328 | 側廳卡座; the side room's window line laid out for a phone; guest-book wording (#39); manual audit |
| f6f856d | COMBO pill: two short lines (it covered the window seat on a phone) |
| 10456ea | Window line: a gentler pull, so the dining room keeps its cats |
| 14c2db7 | The window places have a tier like every other cat piece (the one failure of the full run) |
| c515ac7, 2022fcc, ba287ed | docs/v24: the player's briefs and pictures for the next round |
| 4da3ed6, 7dc2d45 | This report, the evidence, `tools/make_release_zips.py` (every zip under 25,000,000 bytes) |

## 2. Release content audit

| FEATURE / FIX | STATUS | SOURCE | IN THIS RELEASE? | WHY / WHY NOT |
|---|---|---|---|---|
| 走入式冷藏庫 ($80,000; +140 portions; walk-in door drawn) | DONE | master | Yes | qa5: cold storage. Sold-out dishes 13 → 1 in the sim |
| 廚房二期 ($150,000; coffee bar 2 → 4 cups; +2 crew; twin machines) | DONE | master | Yes | qa5: kitchen expansion where the Day 52 bottleneck is |
| New oven / cold-station upgrades | DROPPED | — | No | In the sim those stations stood half idle (§3) |
| Five dogs by shape (博美, 臘腸, 米克斯, 垂耳, 黃金獵犬) and the house | DONE | master | Yes | qa5 + the player's references |
| 側廳卡座 (middle row $18,000, front row $24,000) | DONE | master | Yes | qa1 M; the player today: 「底下六個桌子為什麼不能升級」「新增側廳卡座！」 |
| Side room window line, five steps (窗邊貓架 = step 1) | DONE, re-laid | master | Yes | qa5; layout redone after the screenshot audit (§3) |
| COMBO pill compact | DONE | master | Yes | Found in the screenshot audit: it covered the window seat |
| A cat in the 'sleep' pose drawn sitting up, eyes open (大睡墊, 貓窩) | FIXED | master | Yes | Found while measuring cat sizes |
| 沙發卡座 icon still burgundy | FIXED | master | Yes | Found with the side booth card; the rooms draw oatmeal booths |
| Guest book: drinks are 喝, 一如往常 only for the usual dish, CJK–Latin spacing | DONE | master | Yes | #39 from the player's notes |
| Manual (小小店主手冊) audit | DONE | master | Yes | §8 |
| Staff Lives, Second Floor, Staff Room, Private Dining Room | NOT STARTED | — | No | The next round; the player asked for this round first |
| The other cat gear's long cooldown (box, tunnel… once every few days per cat) | FOUND, LEFT | — | No | Pre-existing; changing it moves every golden and all cat behaviour (§10) |

## 3. What was planned, what the game showed, what changed

| Planned | Observed | Changed to |
|---|---|---|
| Kitchen: high-end stove / oven / cold station | Day 52 save, lazy days: 5–7 dishes sold out before closing; both coffee cups busy half the evening, a drink always waiting; oven and cold station half idle | More cold storage (the walk-in) and a second coffee machine (kitchen II); no new oven or cold station |
| The walk-in raises revenue | It ends sell-outs (13 → 1) but net does not rise in a lazy sim: guests substitute dishes, service is the limit | Kept, priced below kitchen II, described as 「放得下」 |
| Window line: ten places across the whole window | At 390×844 the room tabs cover the window's top; the 庫存 and 今日任務 chips cover its upper corners. A cat is 30–40 units tall, so half the places showed a cat's body without a head | Seven places where a phone shows them. Places that overlap on screen are not used together. At most three cats on the window |
| The window line as one more piece of cat gear | The cats almost never went: 0.2 cats on the window on average, most days none. Any gear started a cooldown of 40–120 decisions, which is days | The window is a place to be, like the cat tree: its own short break, in seconds. A gentle pull that grows with the steps, a little more early in the evening (§4) |
| — | The COMBO pill (shown most of a good evening) covered the right half of the window | Same place, two short lines, 64 px instead of 124 |
| Side booths as a revenue upgrade | Net +5% in the sim, within noise. Groups of three or more seated in the side room 3 → 5. The side room was ~44% full: service binds, not seats | Kept as the consistency upgrade the player asked for; priced modestly |

## 4. Simulations (seeded, lazy staff days; T)

**Kitchen works, Day 52 save, 3 days, the same seeds per variant.** Log: `docs/evidence/v23_late/sims/kitchen_works_day52.log`.

| Variant | Guests | Lost | Angry | Net | Drinks | Sold out |
|---|---|---|---|---|---|---|
| as the save is | 194 | 90 | 56 | 137.8k | 169 | 13 |
| + walk-in | 197 | 95 | 62 | 129.2k | 177 | 1 |
| + kitchen II, nobody hired | 241 | 97 | 39 | 190.2k | 197 | 19 |
| + kitchen II, two LV5 waiters in the new places | 308 | 60 | 2 | 274.2k | 196 | 22 |
| + both, the two waiters | 302 | 79 | 5 | 237.2k | 191 | 5 |

**側廳卡座, Day 52, 3 days.** Log: `side_booths_day52.log`.
- As the save is: 205 guests, 94 lost, net 138.8k; the side room 43% full; 3 groups of 3+ seated there.
- Both rows converted: 204 guests, 90 lost, net 145.4k; 45% full; 5 groups of 3+.

**Window line, three days each.** Logs: `window_cats_day52.log`, `window_cats_day46.log`.
- **t1** is the save as it is (the 窗邊貓架 only). **t5** is the whole line.
- Every sample checked the rules: never more than three cats on window places, never two on overlapping places. The clash count was 0 in every sample.

| Save | Variant | Cats on the window (avg per day) | Most at once | Cats in the dining room | Hops between places |
|---|---|---|---|---|---|
| Day 52 | t1 | 0.26, 0, 0 | 1 | 4.55–4.82 | 0 |
| Day 52 | t5 | 1.31, 1.12, 1.80 | 3 | 3.20–3.62 | 4, 2, 6 |
| Day 46 | t1 | 0.12, 0, 0 | 1 | 4.49–5.0 | 0 |
| Day 46 | t5 | 0.76, 0.51, 0.62 | 1 | 3.89–4.46 | 0 |

The first tuning was stronger: about two cats on the window on Day 46, and 2.7–3.2 left in the dining room. It was turned down (10456ea).

The album memos 窗邊的位子 (two or more cats on the window) and 吊床上的午睡 were asked for. A picture is only taken in the room the player is looking at.

## 5. Save migration (T)

- **Nothing to migrate.** Every new piece of state is absent in an old save, and absent means "as before":
  - `S.sideBooths` → the back row only;
  - the window keys in `S.gear` → the step comes from the 窗邊貓架 the save has;
  - `S.rooms.walkin` and `S.rooms.kitchen2` → off;
  - the dog's kind comes from the walker's seed.
  - Per-cat `winCD` lives only at runtime.
- `every_player_save_migrates_plays_a_day_and_keeps_its_story`: all 13 player saves load, play a day and keep their story. That includes the latest real one, `player_day52.json`.
- **The Day 52 save on load:**
  - window at step 1, side booths 0, cold storage 260, coffee bar 2 cups;
  - the money is untouched ($173,060) and no event fires.
- Save/reload is covered in each feature's test: the booths, the window step, the walk-in, kitchen II.

## 6. Regression (T)

- **Full run** (`python3 tests/run_tests.py`, started on 10456ea): **124 passed, 1 failed**. Log: `docs/evidence/v23_late/full_run.log`.
- **The failure**: `j_cat_furniture_comes_in_tiers_and_the_grass_pot_is_used`, "every piece has a tier".
  - Cause: the seven new window places had no `tier` (the shop's tier lists skip them anyway).
  - Fixed in 14c2db7 (`tier:3`, no behaviour change). The fix landed while the run was past that test; the tests after it ran on the fixed code.
- **Re-run on 14c2db7** of every test the fix or the late commits could touch: `single_file_in_sync`, the failed test, `golden_scenario`, `golden_frames`, `cat_personality_fingerprint`, `window_line_cats_stay_inside_and_in_sight`. Log: `docs/evidence/v23_late/rerun_after_fix.log`.
- **No golden was re-recorded.** The 'sleep' pose fix and the COMBO pill change appear in no golden frame or scenario; the goldens pass unchanged.
- **Mature saves**: `every_player_save_migrates_plays_a_day_and_keeps_its_story` passed. All 13 player saves load, play a day and keep their story.

## 7. Screenshot audit (T)

All at 390×844 unless said, on the player's Day 52 save. The list is in `docs/evidence/v23_late/phone/README.md`.

| Looked at | Found | Done |
|---|---|---|
| Window steps 1–5 | Places under the tabs and chips (heads cut off) | Re-laid. A test checks every place against the tabs, the chips and the COMBO pill at 375×667, 390×844 and 430×932 |
| Window, live evening | The COMBO pill over the window seat | Compact pill |
| Window, cats | 'sleep' drawn as an upright, wide-eyed sit | Curled asleep |
| Side booths 0 / 1 / 2 | All nine the same after both rows; booths sit on the middle row's rug | — |
| Booth and window cards, reveals | Readable; the reveals are caught mid fade-in | — |
| Kitchen with both works | Walk-in door and twin machines visible; 庫存 311/400 | — |
| Street | The five kinds read as dogs at phone scale; the house clear of the parasol | — |
| Not hidden | The top bar's clock reads 17:00 in the live shots: the test bot does not redraw it. The story note (7 s) can sit over the window's middle while it shows | Left |

## 8. Manual audit (小小店主手冊)

**Checked, all sections**:
- 開店與料理
- 開店前：備料與菜單
- Jill 與員工
- 招待與熟客
- 商店：家具、工程、營運
- 招牌菜與招牌甜點
- Lounge
- 五隻店貓
- 料理研發
- 餐廳日誌
- 故事

**Changed**:
- 冰箱裝不下: + 走入式冷藏庫.
- 員工 (people cap): + 廚房二期.
- 家具與佈置: + 側廳卡座, one row at a time, the row full first.
- 店舖工程: + 走入式冷藏庫 and 廚房二期, also at the bottom of 廚房設備.
- 貓咪生活: the window items moved to the new line.
- 廚房設備: 後場工程 and what each does.
- 牠們不出門: the five dogs and the house; the cats stay inside, the window included.

**New**:
- 側廳的大窗: the five steps; the cats decide; at most three; the card shows who used it.

**Removed (stale)**:
- 「窗邊（貓架、睡墊）」
- 「牠會在門邊趴著等主人」

**No change required (verified)**:
- 開店與料理 (COMBO is described, not placed)
- 招待與熟客 (the notes are still 留言)
- 招牌菜
- Lounge
- 料理研發
- 餐廳日誌
- 故事

**Stamp**: GUIDE "last: v2.3 late game (rc3)". `followup_the_manual_describes_the_current_game` checks the new phrases and the two stale ones.

## 9. Text

`tools/hans_scan.py js/game.js index.html`: only the known valid forms remain (沉, 干貝, 宿舍).

One new hit was fixed: 各占一層 → 各佔一層, the form the game already uses. The two 占 in the player's own Private Room brief are left verbatim.

New dialogue is short and states no feelings:
- 「三個人來，也有地方坐了。」
- 「早該這樣。」
- 「窗邊沒我們的位子了。」

## 10. Deliberately not done

- **The next round** (`docs/v24/`): Staff Lives; the Second Floor arc and the floor; the Staff Room; the Private Dining Room.
  - Its audit will start from an existing item: 營運升級 already has 「後場休息室」 ($24,000, +2 staff).
  - The Second Floor's layout waits for the player's master reference (§44 of the long-arc brief). The layout sketch is filed.
- **The other cat gear's cooldown.** After any toy (box, tunnel, grass…) a cat skips all gear for 40–120 decisions, about 2–7 evenings.
  - So most toys are used about once every few days.
  - It is pre-existing and touches every golden. The window line no longer depends on it.
  - Whether to shorten it for the toys too is the player's call.
- **Side booths raise revenue very little.** That is reported here, not hidden: service is the limit at Day 52.

## 11. What to watch on the iPhone (O)

1. **側廳卡座**: buy the middle row, then 去看看. Do the nine tables look like one room after both rows?
2. **The window**: early in the evening, open the side room.
   - Do you see cats on the window seat, the steps, the hammock, the round bed?
   - Are they clear of the tabs and the chips?
   - Is the dining room too empty of cats early in the evening? The window pull is a number; it can go either way.
3. **The COMBO pill**: two lines now. Still feels like a combo? Still readable at a glance?
4. **Kitchen**: the walk-in door; two coffee machines with kitchen II; does the coffee bar keep up with four cups?
5. **The street**: can you tell the five dogs apart at phone size? The house by the door.
6. **The guest book (熟客)**: a drink is 喝了 / 好喝; 一如往常 only for the dish they always have.
