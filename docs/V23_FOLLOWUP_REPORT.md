# JILL'S KITCHEN v2.3 follow-up — release report (2026-10-01)

**Legend**
- **I** — implemented: the code is in the repo.
- **T** — tested: an automated test, a seeded simulation, or a screenshot inspected in headless Chromium at 390×844.
- **O** — observed by the player on the phone. Nothing in this report is O yet; the §11 checklist is what to look at.

**Branch and builds**
- Branch: `master`. Tag: `v2.3-rc2`.
- Published to the player's usual URL, https://claude.ai/artifact/2vhURujrtCpQ1P5jnSsjps. Saves live there.
- The separate RC artifact (`Ax3QGfTwVAhBoqa3jKJXYk`) is not updated; it could not keep saves.

Briefs filed verbatim:

- `docs/v23/qa1_2026-10-01_normal_play.txt`
- `qa2_…_visible_consequences.txt`
- `qa3_…_scope_correction.txt`
- `qa4_…_dylan_dialogue.txt`

## 1. What changed (commits since 06646a0)

| Commit | What |
|---|---|
| cb9eb2c | Campaigns felt in the room; character story progress page; story-update note; the words around a beat kept; every dialogue line kept, × to close; journal reachable during service; manual audited |
| d4667dc | 餐廳故事 restored **verbatim** from 01427bd (wip/qa-normal-play) — no new chapter, ending or main quest |
| 0a26b06 | READY QA items merged from wip/qa-normal-play (room tabs, cushion, chandelier light, social entrances) + fixes found in the phone screenshots |
| 1b78b2d | Dylan × Jill dialogue revision |
| 9cc4ded | Dialogue audit: regulars remember their life, they do not replay it |
| 97cc6ff | Story audit: numbered stages, only real beats, real dates; Story Photo art 情人節 / 今年也在這裡 |
| c764f82 | Manual audit after the final merge; `docs/RELEASE_CHECKLIST.md`; `tools/build_artifact.py`, `tools/hans_scan.py` |
| ff410de | All twenty staff portraits redrawn by the player (the Lounge four kept) |
| f5f248f, 52cf9a3 | Staff meal Story Photo (the player's second version); regulars' habit lines no longer draw a random number when there is no choice |
| e5c6936 | Goldens re-recorded for intended changes (causes proven by elimination); the journal's 社群 page opens on day 6 like the shop |
| f8886df | Sophie's and Mia's portraits from the player's illustrated sheet; the other regulars keep theirs |
| 3512845 | Story Photos from the player's full pictures: 晴 × 阿拓 「多的」「有你在的晚班」, Sophie × Mia 「一起回家」; a Story Photo with art shows the current art, also in a save that took it earlier |
| 2312c8b, 85dbefe | Ken × 杜 「固定的位置」 and 「還是沒有同意」 from the player's full pictures |
| 81296bb | A regular's card says 她 for Sophie and Mia (found in the portrait screenshots) |
| f12b94f | The 熟客 page no longer quotes 「undefined」 (a regression from the dialogue audit, found in the portrait screenshots) |

## 2. Release content audit

| FEATURE / FIX | STATUS | SOURCE BRANCH | IN THIS RELEASE? | WHY / WHY NOT |
|---|---|---|---|---|
| Campaigns felt in the room: 📱 on tickets, guests say why they came (rate-limited), sold-out reactions, cat fans look for real cats, wine → Lounge, summary chip | DONE | master (qa2) | Yes | qa2 goal 1 |
| Jill's answer to a sold-out complaint varies, at most twice a day | DONE | master | Yes | Seen repeating in the campaign sims |
| 故事: 人物／關係支線 with progress, story-update note (deep link), the words of each beat kept | DONE | master (qa2) | Yes | qa2 goal 2 |
| 餐廳故事 (four chapters) | RESTORED | wip/qa-normal-play 01427bd | Yes | Correction §1: restored from the commit, not re-created |
| Numbered stages, 「？？？」 for each unseen one, real stage counts, real dates or 更早以前 | DONE | master | Yes | Correction §2 + the story-audit guardrail |
| Dialogue log keeps the whole day; × to close; logged in the journal's 話語 | DONE | master (qa2) | Yes | Normal-play QA |
| Journal from the pause menu and the summary | DONE | master (qa2) | Yes | Normal-play QA |
| Room tabs under the ticket rail (not over the top row of tables) | READY → merged | wip/qa-normal-play | Yes | READY |
| Two cats on one cushion side by side | READY → merged + fixed | wip/qa-normal-play | Yes | READY. The WIP version still stacked the two cats when one left and another came; fixed and tested |
| Main-hall chandelier light reaches the floor | READY → merged | wip/qa-normal-play | Yes | READY |
| 社群與宣傳 entrances: prep-screen line, shop tab after 店舖工程, journal 社群 page (read-only during service) | READY → merged + gated | wip/qa-normal-play | Yes | READY. The journal page was there from day 1 (a way around the shop's day-6 unlock); it now opens on day 6 |
| Story note sits under the room tabs and hides when any screen opens | DONE | master | Yes | Found in the merge screenshots (it covered the tabs and floated over the journal) |
| Jill's post candidates: photo thumbnails fill in; the line previews the post | DONE | master | Yes | Found in the merge screenshots (blank squares; name shown twice) |
| Dylan × Jill revision (cooler scene deleted; 「不要理他。」; 「你不是在追？」「那我繼續。」; 「誰？」「你。」; the anniversary) | DONE | master | Yes | 2026-10-01 request |
| The running act's fourth line (Jill's) was never said | FIXED | master | Yes | Found while implementing the revision |
| Regulars' dialogue audit (one-time events out of ordinary pools) | DONE | master | Yes | 2026-10-01 request (§5) |
| Story Photo art: 情人節，還在追 / 今年也在這裡 / 開店前 | DONE | master | Yes | Art supplied by the player |
| Story Photo art replaced with the player's full pictures: 多的 / 有你在的晚班 / 一起回家 / 固定的位置 / 還是沒有同意 | DONE | master | Yes | Art supplied by the player (they were small concept-sheet panels, upscaled) |
| A Story Photo taken before its art changed shows the current art | FIXED | master | Yes | Found while integrating the art: the album keeps the picture from the day the photo was taken, so an earlier save would have kept the old panel |
| Staff portraits: 20 redrawn, Evan / 沈晴 / 安安 / 阿拓 kept | DONE | master | Yes | Art supplied by the player |
| Regular portraits: Sophie and Mia from the player's illustrated sheet; 陳伯伯, 王先生, 王太太, 小林, Leo kept | DONE | master | Yes | The player's decision: only Sophie and Mia change |
| A regular's card: 「樾樾不躲他了。」 for Sophie and Mia | FIXED | master | Yes | Found in the portrait screenshots; only 王太太 had 她 |
| The 熟客 page quoted 「undefined」 for six mature regulars | FIXED | master | Yes | Found in the portrait screenshots. Caused by this release's dialogue audit: the page read `l[tier]`, and the audit moved the one-time lines out of `l` |
| Regulars' guest-book notes: 「吃了拿鐵咖啡」 (吃 for a drink), 「香煎鴨胸，一如往常。」 for a dish that is not their usual, 「請了Jill's…」 without a space | FOUND, NOT CHANGED | — | **No** | Text from V18, not from this release. Changing the note pools changes which note a seeded day writes; left for the next release so this one's regression stays valid |
| Manual audit + permanent release checklist | DONE | master | Yes | qa2 goal 3 (§4) |
| Dog types / dog house | NOT READY | wip/qa-normal-play (`docs/v23/wip_dog_types.js`) | **No** | Only a drawing draft (`drawDogT`, five types, `dogTypeOf`). Not wired to the street walkers or the dog that comes along; the nook is not redesigned or moved (still clipped at x 50); no tests, no screenshots |
| Kitchen / fridge depth, money sinks | NOT STARTED | — | **No** | On the normal-play list; never started. Needs design: OPS room tier 2, walk-in, menu board tier 2, side-hall four-tops |
| Side-hall window cat furniture | NOT STARTED | — | **No** | Never started |
| Side-hall seating rule | NOT STARTED | — | **No** | Never started |
| Main story / main quest | NOT DESIGNED (on purpose) | — | **No** | Still being designed (correction §3); nothing invented |

## 3. 故事 — what the page shows

The full audit is in `docs/v23/story_audit_2026-10-01.md`.

**A. 餐廳故事.** Restored verbatim, then changed only as follows:

- the rows are numbered, with 「？？？」;
- real dates where the game kept them;
- a hidden chapter's stage is not announced before the chapter is revealed.

**B. 人物／關係支線.** Only one-time authored moments count. The real number of stages for each line:

| Line | Stages |
|---|---|
| Sophie & Mia | 8 |
| Sophie & 寶寶 | 4 |
| Ken & Monsieur 杜 (友情故事) | 9 |
| 晴 & 阿拓 | 6 |
| Dylan | 16 + the reveal as one 「？？？」; after the reveal, 「不要理他。」 joins |
| 王先生 & 王太太 | 2 |
| 小林 | 3 |
| Leo | 4 |
| the staff-meal pair | 2 |
| 周董 | 3 |
| Madame Lin | 2 |
| 老饕李先生 | up to 3 |
| 戴帽子的客人 | 2 |
| 衛生檢查員 | 2 |

**Removed as stages:**

- a visit count;
- recurring behaviour;
- ambient lines;
- repeats;
- the Wangs' anniversary counted twice;
- the deleted cooler scene.

**Added, because they already existed:**

- Dylan's twelve dated once-only scenes;
- the two second Story Photos (固定的位置, 有你在的晚班);
- 小林's promotion and new job;
- Leo's plant → five cats → job hunt → first salary;
- the staff meal's running joke.

**Not lines, recorded truthfully:**

- Mia (alone), 陳伯伯: small existing threads.
- Evan: in other lines.
- 安安, Hugo, Mr. Hart, 小琪, Momo: ambient character life.

**Rules**
- **Dates.** Only from the game's records. An achievement day shared by four or more achievements is an update catching up, not a date. The first hire is unknown when the crew predates tenure. Anything unknown shows 「更早以前」.
  - On the player's Day 52 save, the first hire shows 更早以前, not DAY 27.
- **Denominators.** A stage that can no longer happen is not counted. 老饕李先生 is 1 / 1 on the Day 52 save: the second signature came first.
- **Updates.** Announced only the day a beat happens. A new definition never announces the past, and nothing is announced on load.

## 4. MANUAL AUDIT (after the final merge)

**Sections checked** — all thirteen:

- 開店與料理
- 開店前：備料與菜單
- Jill 與員工
- 招待與熟客
- 商店：家具、工程、營運
- 招牌菜與招牌甜點
- Lounge：留下來的地方
- 五隻店貓
- 料理研發
- 餐廳日誌
- 故事
- 社群與宣傳
- 存檔與備份

**Sections changed**

- 開店與料理／房間: 「票券列下面的分頁…」 (the tabs moved).
- 招待與熟客／熟客: added 「熟客也有自己的生活——升職、換工作、搬家、畢業這種事只會發生一次，之後記在他們的卡片上；平常點餐時說的是他們的習慣。」
- 餐廳日誌: the summary lists 社群; new entry 社群 (read-only during service). From qa2: 在哪裡, 故事, 話語 (the whole day, ×).
- 故事: rewritten.
  - 兩個部分: 餐廳故事 / 人物／關係支線.
  - 一段一段: every stage numbered, 「？？？」, 更早以前.
  - 故事更新: appears under the room tabs.
- 社群與宣傳／在哪裡: three entrances from day 6; the journal page is read-only during service.
- Earlier in this release (qa2):
  - Jill 與員工: 工作分配; 員工 (tenure); new entries 新來的人, 調酒師.
  - 熟客: named guests.
  - 商店: 店舖工程 (Lounge), 營運升級 (Bar 小廚), new entry 存錢目標.
  - Lounge: 要有調酒師, Bar Food.
  - 五隻店貓: 客人也看貓.
  - 存檔與備份: 手動存檔.

**New sections added in this release** (qa2): 📜 故事, 📣 社群與宣傳.

**Obsolete wording removed**

- 「上方的分頁」
- 「畫面上方會跳一個小通知」
- 「下一段寫著「？？？」」
- 「打烊後或開店前，商店的「社群與宣傳」分頁（第 6 天起）。」
- (qa2) 「暫停選單和設定裡都有【儲存目前進度】」 — the button is only in 設定 during service.
- (qa2) the old Lounge-bartender sentence.

**No change required — verified**

- 開店前：備料與菜單
- Jill 與員工 (this pass)
- 商店 (the 社群 tab order is described in 社群與宣傳)
- 招牌菜與招牌甜點
- Lounge — checked against the restored Lounge chapters.
- 五隻店貓 — the cushion fix is behaviour, not something to explain.
- 料理研發
- 存檔與備份
- 招待與熟客／Dylan — it quotes none of the revised lines.
- Checked again for the last changes (new Story Photo art, 她 on the card, the 熟客 page's quote):
  - 餐廳日誌／相簿 still holds: 「重要的故事真的走到某一步時，會多一張故事照片（標著「故事」），永久保存。」
  - 熟客 does not describe the quote.
  - No change.

**Checks**
- Test: `followup_the_manual_describes_the_current_game` (required phrases and stale phrases).
- The audit stamp on `GUIDE` reads 「last: v2.3 follow-up, 2026-10-01」.
- The audit is now item 2 of the permanent `docs/RELEASE_CHECKLIST.md`.

## 5. Dialogue audit — findings and exact changes

The full table is in `docs/v23/dialogue_audit_2026-10-01.md`.

**Root cause.** A regular's ordering line was `l[tier]`. The third slot held each regular's milestone or memory line. So every mature regular said only that line, on about a third of orders, forever. Examples:

- 小林's promotion, even when no promotion had happened;
- Leo's graduation, before he had looked for a job;
- the Wangs' anniversary, before any anniversary here.

**Ordering lines**

- The pools are habits only.
- **Callbacks** are said only if their history really happened in this save, and only once or with a long gap:
  - 小林 「我升職那天也是來這裡慶祝的，你還記得嗎？」: **removed from his pool**. It is said once, ten or more days after his real promotion.
  - 陳伯伯's four tables: once, after the shop grew.
  - Sophie 「只有這裡」: a 30-day gap.
  - The Wangs' anniversary lines: after it happened here, with a shared 40-day gap.

**Leo**

- 「期末考考完了！」 is a rare student moment (a 60-day gap).
- 「我畢業了，第一份薪水…」 is a **once-in-a-life** moment after his job hunt.
- After graduating, no student moments.

**Moments**

- Happen once: Mia moving; 陳伯伯's former student.
- Come back only after a long gap: oranges (30 days), vegetables (21), flowers (30), the old friend / a coworker / classmates (14), the columnist friend (30), payday (25), exam week (25).
- Mia's coworker: after the first time, only 「今天有伴…」.

**Two regulars who find out they know each other** (陳伯伯 × 王先生, Mia × 小林): once. Sophie × Leo stays a habit.

**Older saves**

- The lines a mature regular already said many times are marked as said.
- On the player's Day 52 save, 小林 will not bring up the promotion again.
- Leo, who has not looked for a job yet, will graduate once, later.

**Checked, no change:** world memories, Dylan's act and scenes, the named guests, the staff, the story events.

**Missed by the audit, fixed later in the release.** The journal's 熟客 page also quoted a regular's line as `l[tier]`.
After the audit, `l` holds habits only. So every mature regular except Mia showed 「undefined」 there. On the Day 52
save, that was 陳伯伯, 小林, Leo, Sophie, 王先生 and 王太太. The page now quotes the newest habit line the tier has
unlocked, which is the pool `regTalk` draws from. Leo, whose student lines became moments, gets no quote. Test:
`journal_pages_never_show_undefined` checks every journal page on three real saves.

## 6. Jill × Dylan revision

As requested; the details are in `docs/v23/qa4_2026-10-01_dylan_dialogue.txt`.

- The cooler scene is deleted.
- 王太太「追到了沒？」 Dylan「還在努力。」 Jill「**不要理他。**」
- 「你不是在追？」「那我繼續。」
- 「誰？」「你。」
- The anniversary: 「你決定。」「我每次決定妳都說不要。」「所以你先想三個。」
- The writing rule is filed.
- Found on the way: the running act never said a fourth line. Fixed.

Listed there, **not changed** (targeted revision only): VAL_LINES.post 「十一年了，還帶。」 — your call.

## 7. Art

**Story Photos — every picture and where it comes from**

| Story Photo | Line | Picture |
|---|---|---|
| 情人節，還在追 | Dylan | The player's picture (new slot, was waiting) |
| 今年也在這裡 | 王先生 & 王太太 | The player's picture (new slot, was waiting) |
| 開店前 | the staff | The player's second version, made to the spec (new slot, was waiting) |
| 多的 | 晴 & 阿拓 | The player's full picture, replacing an upscaled concept-sheet panel |
| 有你在的晚班 | 晴 & 阿拓 | The player's full picture, replacing an upscaled concept-sheet panel |
| 一起回家 | Sophie & Mia | The player's full picture, replacing an upscaled concept-sheet panel; the cat on the counter kept |
| 固定的位置 | Ken & 杜 | The player's full picture, replacing an upscaled concept-sheet panel |
| 還是沒有同意 | Ken & 杜 | The player's full picture, replacing an upscaled concept-sheet panel |
| 今天一起來 | Sophie & Mia | Unchanged: the concept sheet's top banner (enough resolution) |
| 她說只是剛好看到, 好像真的開起來了 | Sophie & 寶寶; the restaurant | Unchanged: drawn by the game |

- Every picture is cut 4:3 by eye, keeping both people whole; the crops are in `docs/evidence/v23/story_art/`.
- Style, as supplied: 今年也在這裡, 固定的位置, 還是沒有同意 and 今天一起來 are photo-realistic; the others are illustrated.
- New slots appear when their moment happens. A slot that was already waiting joins the album dated to the day it happened.

**A photo taken before its picture changed.** The album keeps a copy of the picture from the day a photo was taken. So a
save that earned 「多的」 when it was still the small panel would have kept the small panel. Now a Story Photo that has art
always shows the current art: in the album, the lightbox and the social page. The stored copy stays for export. A photo
drawn by the game keeps the picture it was taken with. Test: `story_photos_show_the_current_art_not_an_old_copy`.

On the Day 52 save:

- The Wang anniversary was before story photos existed (DAY 38), so it will not appear in that save.
- Valentine's comes after Dylan's reveal.
- 開店前 needs four staff with twenty days each, about 17 more days.
- None of the five replaced pictures has been earned yet in that save, so each will first appear with the new art.

**Staff portraits.** Twenty redrawn, cut as cards; the Lounge four kept. 阿勇 and five others had none before.

**Regular portraits.** Only Sophie and Mia change, from the player's illustrated sheet (each one's main panel; Sophie's
name label painted out with the sheet's white). They now match their Story Photos. 陳伯伯, 王先生, 王太太, 小林 and Leo keep
their portraits, as the player decided.

## 8. Tests, saves, goldens

**Full regression:** 118 / 118, then 38 / 38 re-run on the final code. All 120 tests pass on the final code; see §12.

**New tests in this release**

- `followup_*` ×4 (qa2)
- `qa_merged_room_tabs_cushion_light_and_social_entrances`
- `dylan_dialogue_revisions_2026_10_01`
- `regulars_remember_their_life_not_replay_it`
- `story_page_counts_only_real_beats_numbered_with_unseen_stages`
- `every_player_save_migrates_plays_a_day_and_keeps_its_story`
- `journal_social_page_opens_the_same_day_as_the_shops`
- `story_photos_show_the_current_art_not_an_old_copy`
- `regular_card_says_her_for_sophie_and_mia`
- `journal_pages_never_show_undefined`

**Mature saves.** Every save the player sent (Day 30, 33, 35, 39, 42, 44, 46, 48, 49, 50a, 50b, 52, 52a):

- opens on its own day;
- migrates silently (nothing announced);
- shows the 故事 page;
- plays a whole lazy day without an error;
- after save/reload keeps its story record and the page counts exactly — no beat lost, none invented.

**Story save/reload**, on the Day 52 save: Dylan's twelve dated stages survive, plus the one added during the test. What the player has been told survives, and nothing is announced twice.

**Goldens re-recorded.** Each cause was proven by elimination: with the change reverted on a copy, the old golden matched exactly.

- `cats.json`, `scenario.json`: the cushion fix moves cats, which shifts the seeded random stream.
- `frames.json` and the screens: the cushion; the floor light; the tabs under the rail; 餐廳日誌 in the pause menu; the journal's 故事 tab; the shop's tab order.
- `lounge_i_content…`: seed 51 → 52. After the shift, seed 51 became the rare day with no bar food. Measured over seeds 51–60: 2–4 bar-food tabs a day on nine days of ten.

**Tests updated for intended changes**

- Shop tab order.
- Every staff name has a portrait.
- The room tabs sit under the rail on desktop and phone.

**Text**

- Traditional Chinese only. ICU Hans-Hant scan of `js/game.js`, `index.html` and the new docs: no Simplified characters. The only hits are valid forms: 干貝, 睡得很沉, 宿舍.

## 9. Phone screenshots (390×844, headless Chromium — T, not O)

The final set was re-taken on the final code (f12b94f). It is in `docs/evidence/v23_followup/phone/`, with a README
saying what each file shows.

All taken on the player's Day 52 save:

- the story page (both sections, numbered rows, a beat opened to its words);
- the story note under the tabs;
- the room tabs under the ticket rail at dusk;
- two cats on the cushion, before and after a swap;
- the chandelier light;
- the prep-screen 社群與宣傳 line;
- the journal 社群 page during service;
- the staff page and a staff line with the new portraits;
- Sophie's and Mia's cards in service and on the 熟客 page, with their new portraits;
- the journal's 相簿 and the lightbox with the new Story Photos (多的, 有你在的晚班, 一起回家, 固定的位置);
- the manual's 房間 entry.

**Investigated: blank polaroids.** In the first album screenshot, three photos of the Day 52 save were blank squares. Cause:
the test loader puts only the save into the browser, not the pictures that the exported file carries alongside it. With
the game's own import (設定 → 讀取存檔), all 133 pictures show. Not a game fault; the player's import path brings the pictures.

**Investigated and fixed: two text faults on the portrait screenshots.**

- Sophie's and Mia's cards said 「樾樾不躲他了。」.
- On the 熟客 page, six regulars ended with 「undefined」.

Both are fixed (§2, §5), with tests. Seen on the same page and left for the next release (§2): 「吃了拿鐵咖啡」, and
「一如往常」 for a dish that is not the regular's usual.

## 10. I / T / O

| Feature | I | T | O |
|---|---|---|---|
| Campaign felt in the room | ✓ | ✓ test + `tools/sims/campaign_days.py` | — |
| 故事 page (both sections), numbered stages, story note | ✓ | ✓ tests + screenshots | — |
| Beat words kept / retrievable | ✓ | ✓ | — |
| Dialogue log whole day / × | ✓ | ✓ | — |
| Journal from pause / summary | ✓ | ✓ | — |
| Room tabs / cushion / light / social entrances | ✓ | ✓ test + screenshots | — |
| Dylan revision | ✓ | ✓ | — |
| Regulars' dialogue audit | ✓ | ✓ | — |
| Story Photo art, staff portraits | ✓ | ✓ screenshots | — |
| The five replaced Story Photo pictures; an earlier photo shows the current art | ✓ | ✓ test + screenshots | — |
| Sophie's and Mia's portraits | ✓ | ✓ tests (`q_portraits…`, `named_guests…`) + screenshots | — |
| Manual | ✓ | ✓ test | — |

## 11. What to check on the phone (for O)

1. Open the usual URL. The Day 52 save loads (not a new game). The page title is still Jill's Kitchen.
2. 日誌 → 故事:
   - 餐廳故事: CHAPTER 1–3 with numbered rows; CHAPTER 4 「？？？？？」.
   - 人物／關係支線: Dylan 12 / 17 with dates; tap a row to see what was said.
3. In service:
   - the room tabs sit under the tickets, not over the top row of tables;
   - when a story moves, a small note appears under the tabs; tap it to open that story.
4. Start a campaign (e.g. 店貓). Look for:
   - 📱 on some tickets;
   - a few guests saying why they came;
   - the summary chip.
5. Ordinary days:
   - 小林 does not keep bringing up his promotion;
   - Leo does not keep graduating.
6. Staff cards and staff lines show the new portraits.
7. Sophie's and Mia's cards show the new portraits; the other regulars look as before.
8. When a Story Photo arrives (for example 「多的」 or 「固定的位置」), the album shows your full picture, not a small blurry panel.
9. 小小店主手冊: the 故事 and 社群與宣傳 sections describe what you see.

## 12. Final regression

**Full run: 118 / 118 passed.**

- Started on 3512845, about 45 minutes.
- Four commits landed while it ran:
  - 2312c8b and 85dbefe: art data only;
  - 81296bb and f12b94f: the two text fixes.
- Every test that started after f12b94f ran on the final code. That includes `golden_scenario`, `golden_frames`, the portrait tests and `every_player_save_migrates…`.

**Re-run on the final code (f12b94f): 38 / 38 passed.**

- The 36 tests that ran before f12b94f landed, including `single_file_in_sync` and `cat_personality_fingerprint`.
- The two tests added after the full run had started.

So every one of the 120 tests has passed on the final code.

**Goldens.** None re-recorded after e5c6936. The later changes do not reach them: the golden screens start a new game, which has no Story Photos and no regulars yet.

**Text.** The ICU Hans-Hant scan of `js/game.js`, this report, the dialogue audit and the tests finds only the valid forms 沉, 干貝 and 宿舍.
