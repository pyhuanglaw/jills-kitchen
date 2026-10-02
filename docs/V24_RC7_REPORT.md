# JILL'S KITCHEN v2.4 rc7 — release report (2026-10-02)

rc7 has two parts:
- **What the player asked for from 14:39 to 16:59.** This covers the day's money, Ken after the Lounge (his tastings, the wine, 杜), 林予安 the pianist, the landlord, more than one story a day, a line that finds its table, and the story guests' own faces.
- **The manual audit and the release.**

Three things the player decided while rc7 was being finished are *not* in it:
- **沈晴 × 阿拓 after work (18:07, the five acts).** It is built on the branch `wip/qing-tuo-after-work` and goes out in the next version, with the player's pictures (18:12, 18:41).
- **P5, the other Staff Lives arcs.** It is paused (18:38, 18:39). Its plan and the seven portrait cards are kept as backlog (`docs/v24/AUDIT_AND_PLAN.md` §9.7).
- **主廚之夜 (14:49) and the social posts with their pictures and likes (15:02).** Neither is done yet. Both are next.

**How this report reports** (`docs/RELEASE_CHECKLIST.md` §3):
- **I — IMPLEMENTED**: the code is in the repo, at the tag.
- **T — TESTED**: a test, or a seeded simulation, shows it works. Screenshots I took in headless Chromium from the player's own saves at 390×844 count as T.
- **O — OBSERVED**: only when the player has confirmed it in their own play. Nothing here is O yet, and nothing was observed on an iPhone.

**Branch, tag, page**
- Branch `master`, tag `v2.4-rc7`.
- Published to the player's usual URL, https://claude.ai/artifact/2vhURujrtCpQ1P5jnSsjps (§9).

## 0. What the player asked for

Filed in `docs/v24/`.
- **14:39–18:43**: `player_messages_1439_1843_2026-10-02.txt`. It holds the 14:39–15:40 lines verbatim as the commits quoted them, the rest as a summary, marked as such; 15:56 onwards verbatim.
- **15:24**: `ken_lounge_continuity_2026-10-02_1524.txt` and `du_collab_wine_payoff_2026-10-02_1524.txt`.
- **16:42–16:46**: `pianist_yuan_2026-10-02_1642.txt`.
- **18:07, 18:08**: the 沈晴 × 阿拓 texts are filed on the branch that carries them.

## 1. Commits since v2.4-rc6

| Commit | Time | What |
|---|---|---|
| b421041 | 14:31 | The P5 plan (`AUDIT_AND_PLAN` §9). Now paused (§9.7) |
| 1241ee3 | 14:51 | The seven outside-cast portrait cards (packed, unused while P5 is paused) |
| 6dfc442 | 15:32 | The day's money: what the glasses cost, the rent, wages, 秀琴阿姨's loan, no debt; the Lounge's figure; golden_scenario and golden_frames re-recorded with proof (the rent) |
| 2f9be97 | 15:47 | The landlord's afternoon: 「我上去一下，拿個東西。」 |
| 485c87e | 16:10 | More than one story a day |
| 8800715 | 16:13 | A line finds its table |
| 8e8d407 | 17:09 | Ken after the Lounge: his tastings, the wine 「晚餐之後」, 杜 |
| 8a5b1f9 | 17:22 | 林予安, the Lounge's pianist |
| 8e536ae | 18:04 | The story guests' own faces; golden_frames re-recorded with proof (陳伯伯) |
| 7af5df7 | 18:44 | The manual audit |

## 2. Release content audit

| Feature / fix | Status | Branch | In rc7? | Why / why not |
|---|---|---|---|---|
| The day's money (14:39–15:03) | Done | master | Yes | |
| Ken after the Lounge (15:24, 15:33) | Done | master | Yes | |
| 杜 and the wine (15:24) | Done | master | Yes | |
| 林予安 the pianist (16:42–16:46) | Done | master | Yes | |
| The landlord's afternoon (15:40) | Done | master | Yes | |
| More than one story a day (15:39) | Done | master | Yes | |
| A line finds its table (15:37) | Done | master | Yes | |
| The story guests' own faces (15:38) | Done | master | Yes | |
| The player's pictures and sheets (16:12–16:59) | Done | master | Yes | Packed with the Ken, 杜 and 予安 work |
| 沈晴 × 阿拓 after work (18:07, revised Act 5, 18:08) | Built without its pictures | wip/qing-tuo-after-work | No | The player, 18:12 and 18:41: next version, with the pictures |
| P5, the other Staff Lives arcs | Plan and cards only | master | Cards only (unused) | Paused by the player, 18:38 and 18:39; kept as backlog |
| 主廚之夜 (14:49) | Not started | — | No | Next |
| Social posts: the picture and likes (15:02) | Not started | — | No | Next |

Nothing else asked for is outstanding. The branches `hotfix-v18.1.1` and `wip/qa-normal-play` were merged long ago.

## 3. What changed, with I / T / O

### 3.1 The day's money (14:39–15:03)

**What changed**
- Every glass poured, in the Lounge or with dinner, is on a new 酒水成本 line: the wine's own cost, about 30%.
- A rent every day for the space the restaurant takes. The dining room costs $300–2,500 by its level; 側廳 +2,000, 戶外區 +400, 廚房擴建 +800, Lounge +2,500, 二樓 +4,000. It is itemised on the summary.
- Wages are 10% higher and climb more steeply: LV5 is 3.2× the start.
- Nothing is ever owed: the till pays down to $0. In the first ten days, on an evening the till cannot pay its costs and still buy tomorrow's food, 秀琴阿姨 lends $20,000 at closing (a scene, once). She is paid back a week or more later.
- The Lounge figure on the summary is what its tabs paid, and equals its list's total.

**Measured** (`tools/sims/economy_days.py`, logs in `docs/evidence/v24_rc7/sims`)
- Day 71: net about $94k → about $78k a day.
- Day 30: about $47k → about $41k.
- A new game's first days: −$300 a day.

**I / T / O**
- I: in.
- T: `v24_rc7_the_money`; the golden proofs (`golden_scenario_proof.log`, `golden_frames/`).
- T: phone screenshots of the summary from the Day 74 save (`money/`): 酒水成本 −$6,497, 薪資 −$14,679, 租金 −$8,200 itemised (主廳 2,500 · 側廳 2,000 · 戶外區 400 · 廚房擴建 800 · Lounge 2,500), net +$99,612.
- O: not yet.

A note from those screenshots, not a bug: tips on that day were $48,130 on $124,015 of takings (about 39%). That is the existing tip model with 97% satisfaction and long combos. rc7 did not touch it. Whether it is too generous is a balance question for the player.

### 3.2 Ken after the Lounge (15:24, 15:33)

**What changed**
- The finished Lounge begins Ken's next chapter:
  - he comes back and sits in it;
  - he proposes a small tasting at the bar: 「我主持。酒我挑，菜妳配。」 Only Ken holds tastings.
- He hosts three tastings, held scenes:
  - the first with the player's picture;
  - the second with 杜 at the end of the bar;
  - the third ends with 「做一支我們自己的。」
- The samples come after closing. Jill names the wine 「晚餐之後」. It comes onto the Lounge's list for good.
- At least four days later 杜 tastes it: 「太輕。」…「可是它很好。」 (the player's picture).
- After the third tasting, a tasting every week or two, unheld.
- A tasting night:
  - the news says so the day before and on the day;
  - the stools are for the people who came;
  - Ken stands behind the bar with a glass, the glasses are set out on the counter, a small board.
- The player's expression sheets: Ken with his glasses (主持, 乾笑, 品酒) and 杜 (品酒, 不以為然, 真心稱讚).

**Traced** from the player's Day 74 save over 40 days (`tools/sims/ken_chain.py`):
- proposal Day 76;
- tastings Days 79, 84, 89;
- samples Day 93, the wine Day 98, 杜 Day 102;
- the fourth tasting Day 105, with the wine poured.

**I / T / O**
- I: in.
- T: `v24_rc7_ken_comes_back_and_proposes_a_tasting`, `v24_rc7_ken_hosts_his_tasting_nights`, `v24_rc7_the_wine_and_monsieur_du`.
- T: phone screenshots (`ken/`).
- O: not yet.

### 3.3 林予安, the Lounge's pianist (16:42–16:46)

**What changed**
- The piano no longer plays itself. It stays silent until 予安 has come in as a guest a few times:
  - her first evening, she keeps looking at it (the player's picture);
  - 「那台有人彈嗎？」;
  - 「妳們有在找彈琴的人嗎？」…「我。」.
- The trial, on an evening the Wangs are in the Lounge:
  - the scene where she sits down holds the restaurant; the playing does not;
  - the end of the piece is a held scene with the player's picture: a few tables clap, 王太太 says 「彈得真好。」, 予安 says 「謝謝。」;
  - later: 「下週還有空嗎？」「星期幾？」 (the player's picture).
- Then three nights a week:
  - the news says so;
  - she comes early, and the piano draws her in her own looks;
  - more people stay after dinner;
  - now and then a word: 「八點半比較吵。」;
  - her fee, 鋼琴演奏 $2,500, is on the night's accounts.

**Traced** from Day 74 (`tools/sims/yuan_chain.py`): first evening Day 77; the trial and her yes Day 84.

**I / T / O**
- I: in.
- T: `v24_rc7_yuan_comes_to_play_the_piano`.
- T: phone screenshots (`yuan/`).
- O: not yet.

### 3.4 The landlord's afternoon (15:40)

The floor is his, so he asks nobody: 「我上去一下，拿個東西。」 He goes up for the two old fire extinguishers, because the inspection is coming. He asks Jill 「要上來看嗎？」. A story page that kept the old words shows the scene as it is now.

**I / T / O**
- I: in.
- T: `v24_rc7_the_landlord_goes_up`.
- T: phone screenshots of the held scene (`landlord/`).
- O: not yet.

### 3.5 More than one story a day (15:39)

**What changed**
- Two major beats a day (was one), two of the long stories' steps (was one), three minor moments (was two).
- Two beats of one lane on one day are a part of the evening apart, so two stories never land in the same minute.

**Measured** (`tools/sims/story_per_day.py`)
- Two beats due on the same day no longer wait for each other.
- The total is the same: 6–7 major beats in 12 days either way.
- What is due is the limit. More lines running at once is what fills the empty days: Ken's tastings and 予安 now.

**I / T / O**
- I: in.
- T: the lane tests; the forty-days and mature-save tests.
- O: not yet.

### 3.6 A line finds its table (15:37)

**What changed**
- A guest's line with a face, said while walking to a table through another room, now takes the tap to that table's room. The table rings until they reach it.
- A waiter's or the bartender's line finds the table it was said at.
- Jill's line to a guest finds the guest.
- The inspector's line finds her where she walks.

**I / T / O**
- I: in.
- T: `v24_rc7_a_line_finds_its_table`.
- T: phone screenshots (`tap/`): Sophie says 「今天人好多。」 in the dining room; the tap shows 側廳 with T10 ringed, 「Sophie · T10」.
- O: not yet.

### 3.7 The story guests' own faces (15:38)

**What changed**
- Fourteen hair styles that only story guests have, drawn from their portraits.
- Their own glasses, beards, brows, lashes, lips, pearls and earrings, 杜's cravat, Mia's overalls, 小琪's camera.
- The strangers' accessories are the strangers' again.

Before and after, and in-game shots: `cast/`.

**I / T / O**
- I: in.
- T: `v24_rc7_story_guests_have_their_own_faces`.
- T: golden_frames re-recorded with proof (`cast/README.md`).
- O: not yet.

## 4. The manual (小小店主手冊) audit

Every section was checked against the final feature set.

**Changed**
- 商店: the piano. It no longer "plays one night in three"; nobody plays it until 予安, three nights a week.
- 開店與料理 › 誰在哪裡: a line said on the way to a table; a waiter's or the bartender's line.
- 故事 › 店裡暫停中: Ken's stories after the Lounge and 予安's hold the restaurant too.
- 招待與熟客 › 熟客: the story guests look like their portraits; no stranger does.
- 每天的帳 › 結算: 鋼琴演奏.

**Already current** (added with their features in rc7):
- 每天的帳 (酒水成本, 租金, 薪水, 錢不夠的時候);
- Lounge › Ken 的品酒夜, 鋼琴與予安, 晚餐之後.

**No change required, verified**
- 開店前, Jill 與員工, 招牌菜, 二樓, 五隻店貓, 料理研發, 餐廳日誌, 社群與宣傳, 存檔與備份.

**Test**: the audit stamp says rc7, and `followup_the_manual_describes_the_current_game` checks 11 new phrases and the old piano line as stale.

## 5. Text

`tools/hans_scan.py js/game.js index.html`: three distinct hits, all valid Traditional and all present in rc6 too:
- 干貝 (scallops);
- 沉 (睡得很沉 and the like);
- 宿舍.

## 6. Tests

- **Full regression** on a clean worktree of 7af5df7: see §6.1. It takes about 65 minutes.
- **New tests in rc7**: `v24_rc7_the_money`, `v24_rc7_madame_lin_says_which_corner`, `v24_rc7_the_landlord_goes_up`, `v24_rc7_a_line_finds_its_table`, `v24_rc7_ken_comes_back_and_proposes_a_tasting`, `v24_rc7_ken_hosts_his_tasting_nights`, `v24_rc7_the_wine_and_monsieur_du`, `v24_rc7_yuan_comes_to_play_the_piano`, `v24_rc7_story_guests_have_their_own_faces`.
- **Goldens re-recorded, each with proof**:
  - golden_scenario and golden_frames for the rent;
  - golden_frames again for 陳伯伯's new look. With his old look and everything else new, the old baseline passes untouched.

### 6.1 Full regression

(filled in below when the run finishes)

## 7. Saves

- The player's saves are the migration fixtures (`tests/saves/README.md`), including the latest, Day 74 15:08. They load and play in the full regression.
- The simulations above all start from them.
- The player's Day 73 and Day 74 saves were filed in rc7.

## 8. Screenshots (390×844, headless Chromium, the player's saves)

All under `docs/evidence/v24_rc7/`:
- `money/` and `landlord/`: device pixel ratio 2.
- `tap/`.
- `ken/` and `yuan/`.
- `cast/`: device pixel ratio 3.

## 9. Build and publish

(filled in below)

## 10. What only the player can judge (O)

- Whether the money now feels right. Rent and wages bite, the loan comes when it should, and tips may be generous.
- Whether Ken's tastings feel like his and come at a pace that makes the Lounge feel used.
- Whether 予安's arrival reads as someone who chose the place, and her trial as a good piece played in a room that keeps living.
- Whether the story guests are recognisable at a glance on the phone.
- Whether two stories a day feels like more is happening, or only busier.

## 11. Next

1. 沈晴 × 阿拓 after work, with the player's pictures. The code is on its branch.
2. 主廚之夜 and the social posts.
3. Deepening the people the player already knows (18:39):
   - the Lounge's own life;
   - Ken, 杜 and the two of them together;
   - 予安 and Evan;
   - Dylan and the Lounge's people;
   - continuity between characters;
   - what each story leaves behind in normal play.
