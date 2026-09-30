# v2.3 story audit — what the 故事 page counts (2026-10-01)

This is a discovery, classification and presentation pass over content that already exists. No beat, arc, romance,
friendship, life event, gift, conflict or reveal was invented to fill the page. The rule for the page is:

- **Show** how far a story has gone.
- **Do not show** how to force the next beat.

## What counts as a stage

A stage is a **one-time authored moment**. That means one of:

- a `once` story event;
- a v2.2 once-flag (promotion, moving, graduation…);
- one of Dylan's once-only scenes;
- a dated record;
- the **first** time of an authored minor or major story event.

These never count:

- ambient or habitual lines;
- a repeat of a beat ("the third time");
- a visit count;
- recurring behaviour (the cats going to Dylan, him clearing his plate);
- routine visit variations;
- occasional gifts.

**Denominator rules**
- A stage that can no longer happen in this save is not counted: 老饕李先生's first two beats once the second
  signature exists, 「還在追喔？」 after Dylan's reveal, the staff meal's second box when one of the two has left.
- A stage that still can happen is shown as 「？？？」.
- Dylan's reveal is counted as one 「？？？」 before it happens. The one beat that only exists after it
  (「不要理他。」) joins then. The reveal is not the end.

**Dates**
- A date is shown only when the game itself recorded it: facts, event states, Dylan's scene days, v2.3 once-flags
  (which now keep the day), and the regular's own memory lines.
- An achievement day is not used when four or more achievements share it. That is an update catching up on what had
  already happened, not the day it happened.
- The first hire is unknown when someone on the crew predates tenure records.
- Anything not known is shown as **更早以前**.

**Order and notes**
- Seen stages are listed in the order they happened. An undated one keeps its place in the story.
- Each seen stage opens to what happened. For v2.3 events this is the words captured at the moment. For older ones
  it is the game's own record, or the exact exchange when a scene has only one version. Nothing is paraphrased as
  if it were a quote.

## A. 餐廳故事 — restored verbatim from 01427bd

Four chapters, restored from the wip/qa-normal-play commit (not re-created). Nothing was added to them.

| Chapter | Stages |
|---|---|
| CHAPTER 1 小小的餐廳 | 開店, 第一位員工, 第一次擴建, 有了熟客 |
| CHAPTER 2 店開始有自己的樣子 | 招牌菜, 側廳, 第二道招牌, Jill's Kitchen — JILL |
| CHAPTER 3 晚餐之後 | Ken's wine question → Lounge 開了 (6 stages) |
| CHAPTER 4 Jill's Kitchen — The Lounge | 5 stages |

- Chapter 3 is hidden as 「店裡好像還少了什麼。」 until Ken's question.
- Chapter 4 is hidden as 「？？？？？」 until the Lounge project.

Changes since the restore:

- The rows are numbered, with 「？？？」 for unseen stages.
- Real dates are used where the game kept them (see Dates above).
- 「早期」 now reads 「更早以前」, the same as everywhere else on the page.
- A hidden chapter's stage is not announced before the chapter is revealed. In the player's Day 52 save,
  「好像真的開起來了」 has happened, but chapter 4 is still hidden.

## B. 人物／關係支線 — shown, with their real number of stages

| Line | Stages | Notes |
|---|---|---|
| Sophie & Mia | 8 | sm_a…sm_h, all once. Not stages: sm_after, sm_pad, recognize (ambient). |
| Sophie & 寶寶 | 4 | sophie_mei_1…4. Not a stage: the glance (ambient). |
| Ken & Monsieur 杜 (友情故事) | 9 | first argument; Lounge's first night; 固定的位子; 「杜來了嗎？」; 「他有說幾點嗎？」; the first absence; 第二個杯墊; 還是沒有同意; **固定的位置** (added: a once event with its own Story Photo). Not stages: the arguing and ordering habits, 安安's lines. |
| 晴 & 阿拓 | 6 | qt_1, qt_2, qt_3, the absence, 從工作開始, **有你在的晚班** (added: once, own Story Photo). Not stages: the daily count, 「多的」 repeats, Hugo's line. |
| Dylan → Jill & Dylan | 17 before the reveal (16 + the reveal as one 「？？？」); after it, the reveal and 「不要理他。」 are in, and 「還在追喔？」 stays only if it happened before | 打烊後還在; his 12 once-only scenes (出菜口, 側廳, 廚房, 外面的位子, 招牌上只剩一個名字, 特製版, 四道特製版, 招牌菜換盤, 牠已經在上面了, 菜單我自己拿了, 水我自己倒了, 王太太「那位先生每天都來耶。」); 「還在追喔？」 (before the reveal only); 情人節 (the first); 「不要管人家。」; the reveal; 「不要理他。」 (after). See the Dylan notes below. |
| 王先生 & 王太太 | 2 | the anniversary (once), 「我也是經過。」. The anniversary photo is the same day, not a second stage (it had been counted twice). Not stages: coming alone (routine), sharing, the flowers (occasional gift). |
| 小林 | 3 | 升職 (v2.2 once), 「你哪次不是這個？」, 換了工作 (v2.2 once). Not a stage: 「今天不要那個。」 (ambient, repeatable). |
| Leo | 4 | 一盆多肉 (once), 五隻都在 (the first), 「快畢業了，開始找工作。」 (once), 第一份薪水 (once, after the job hunt). 第一份薪水 is the line that was in his ordinary pool — see dialogue_audit_2026-10-01.md. |
| 員工 (a waiter & a chef) | 2 | the staff meal's running joke, then the second box. One per restaurant; the second only while both still work here. |
| 周董 | 3 | 第一次坐到側廳, 「那明天再來。」 (the first), 「牠在睡。」 (with 包包). Not a stage: 「隨便」 (his habit). |
| Madame Lin | 2 | 一坐下就看出來了 (the first), 「那個角落空很久了。」. Not a stage: 「又看出來了」 (a repeat). |
| 老饕李先生 | up to 3 | 「靠這一道走天下？」, Sophie's 「甜點還沒有。」 — both only while the second signature does not exist — and 「現在可以了。」. |
| 戴帽子的客人 | 2 | the first review (its day when known), 「今天還戴帽子？」. |
| 衛生檢查員 | 2 | the first inspection, 「我今天只是來吃飯。」. Not a stage: 「又來了」 (a repeat). |

**Dylan notes**

- Removed: the cooler scene (deleted from the game, 2026-10-01); 「又來了」 (a visit count);
  「五隻貓好像很熟悉他」 and 「走之前會自己收盤子」 (recurring behaviour — clues, not moments).
- 情人節 and 「不要管人家。」 both happen before the reveal too, so they no longer wait for it.
- Before the reveal the line is 「那位常來的客人」 with only his face, and nothing on it says he is Jill's husband.
  Afterwards it is 「結婚十一年，還在追」 and the same history goes on.
- His one story photo is 情人節; the milestone photo is the restaurant's.

A line is on the page from its first stage. Until then it is one of the 「還有 N 段故事還沒開始」.

## C. Not a line — recorded truthfully

| Character | How it is recorded |
|---|---|
| Mia (alone) | A small existing thread: the drawing (once), moving (now once), 「我以前來的時候這邊還沒有側廳。」 (a one-off memory, only if she came before the side hall). Her story is Sophie & Mia. Not yet a multi-beat arc. |
| 陳伯伯 | A small existing thread: 樾樾 comes close (once), a former student's news (once). The oranges, vegetables and old friend are occasional. Not yet a multi-beat arc; everything is on his regular card. |
| Sophie (alone) | Her arcs are with Mia and 寶寶; her line about the second signature is in 老饕李先生's. |
| Evan | Part of Ken & 杜 (「杜來了嗎？」, 第二個杯墊) and of the restaurant story (「聽說這裡是你害的。」). No separate thread. |
| 安安, Hugo | Ambient character life. |
| Mr. Hart, 吃貨小琪, 美食部落客 Momo | Ambient character life (visits, posts). |
| The cats | Their authored moments are in Sophie & 寶寶, 周董 (包包), Leo (五隻) and 陳伯伯 (樾樾). Cat-to-cat moments are album memories (behaviour). |
| The staff (other) | The first-shift question and veterans' answers are character life. The team photo 「開店前」 is in the album. |

Tests:

- `story_page_counts_only_real_beats_numbered_with_unseen_stages` — the player's Day 52 save.
- `followup_story_progress_is_visible_retrievable_and_honest`.
- `phase9_the_restaurant_remembers_milestones_slots_and_small_crossovers`.
