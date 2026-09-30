# v2.3 dialogue audit — one-time events in repeatable pools (2026-10-01)

Brief (from the player/designer, 2026-10-01): some NPC dialogue treated one-time life events and milestones as
ordinary repeatable flavour. Example: 小林 said 「我升職那天也是來這裡慶祝的，你還記得嗎？」 many times. Audit every
named regular / NPC pool, classify each line, and fix the classification. Do not solve it with one global cooldown,
and do not rewrite good repeatable dialogue.

Categories used below:

1. **HABIT** — repeatable habit or personality; safe to recur.
2. **CALLBACK** — a real past fact, referenced rarely: only if it really happened in this save, with a long gap, and
   never as if it just happened again.
3. **ONCE** — a one-time life event or story beat: happens once when it happens, then becomes history (a fact).
4. **WORLD MEMORY** — refers to a real past event in this save; does not repeat indefinitely.

## Root cause

A regular's ordering line was `REG_BY[id].l[tier]`, where tier is 0 (visits 0–3), 1 (visits 4–11) or 2 (12+). The
line was said on 35% of orders. The third slot held each regular's "big" line: a milestone, a memory or a
declaration. So every mature regular said only that line, every few visits, for the rest of the game.

## Ordering-line pools (REGS `l`)

| Regular | Line | Was | Category | Now |
|---|---|---|---|---|
| 陳伯伯 | 一份炒飯，謝謝。 | tier 0 | HABIT | unchanged (first visits) |
| 陳伯伯 | Jill，今天還是老樣子。 | tier 1 | HABIT | tier 1 and 2 |
| 陳伯伯 | 我記得你這裡剛開幕的時候只有四張桌子。 | tier 2, 35% of orders | WORLD MEMORY | callback, **once**, only once the shop has grown (level ≥ 2) |
| Mia | 一杯咖啡，謝謝。今天好長。 | tier 0 | HABIT | unchanged |
| Mia | Jill 主廚，今天也拜託你的咖啡續命。 | tier 1 | HABIT | tier 1 and 2 |
| Mia | 每次加班完來這裡，才覺得今天有被好好對待。 | tier 2 | HABIT (a habitual feeling, "every time") | tier 2, alongside the line above |
| 小林 | 哪個最快？我十分鐘後要回公司。 | tier 0 | HABIT | unchanged |
| 小林 | Jill，老樣子，快快快。 | tier 1 | HABIT | tier 1 and 2 |
| 小林 | 我升職那天也是來這裡慶祝的，你還記得嗎？ | tier 2, 35% of orders — **even if the promotion never happened** | CALLBACK | **removed from the pool**. Now a callback, **once**, only if his promotion (「升職了，今天不趕。」) really happened here, at least 10 days later |
| Leo | 請問學生有優惠嗎？沒有也沒關係。 | tier 0 | HABIT | unchanged (first visits) |
| Leo | Jill 姊，我期末考考完了！ | tier 1, 35% of orders | periodic life event | **removed from the pool**. Now a moment `finals`: only while he is a student, at most once in 60 days, not in an exam week |
| Leo | 我畢業了，第一份薪水就是想來這裡吃一頓。 | tier 2, 35% of orders — **before he even looked for a job** | ONCE | **removed from the pool**. Now a once-in-a-life moment `grad`: after his job hunt (「快畢業了，開始找工作。」), at least 10 days later, once; it becomes his record 「畢業了，第一份薪水來這裡吃了一頓。」 |
| Sophie | 讓我看看這家店有什麼本事。 | tier 0 | HABIT (first visits) | unchanged |
| Sophie | Jill，今天的醬汁我想再試一次。 | tier 1 | HABIT | tier 1 and 2 |
| Sophie | 我寫過很多餐廳，但只有這裡，我會想一直回來。 | tier 2, 35% of orders | CALLBACK (a declaration that loses meaning when repeated) | callback, at most once in 30 days, only at tier 2 |
| 王先生 | 靠窗的位子可以嗎？ | tier 0 | HABIT | unchanged |
| 王先生 | Jill，我們又來約會了。 | tier 1 | HABIT (weekly date) | tier 1 and 2 |
| 王先生 | 結婚紀念日每年都在這裡過，這是第幾年了？ | tier 2, 35% of orders — **even before any anniversary here** | CALLBACK | callback, only after their anniversary really happened here (≥ 7 days later); the couple share one gap of 40 days |
| 王太太 | 甜點先看一下菜單，好嗎？ | tier 0 | HABIT | unchanged |
| 王太太 | Jill，今天他又說要提早走，妳別理他。 | tier 1 | HABIT | tier 1 and 2 |
| 王太太 | 每年紀念日都在這裡，妳的店不能關喔。 | tier 2, 35% of orders | CALLBACK | as 王先生's (the same shared gap) |

A callback is at most one in three of the lines a regular says when it is due; otherwise they speak from habit.

## Visit moments (regPlanVisit / regSeatMoment)

| Regular | Moment | Line | Was | Category | Now |
|---|---|---|---|---|---|
| 陳伯伯 | walk | 今天走到河邊…／散步繞遠了一點。／走一走就到了。 | repeatable | HABIT | unchanged |
| 陳伯伯 | oranges (gift) | 鄰居送太多橘子…／橘子，朋友種的… | again 4 days after the last bag | occasional | ≥ 30 days since the last bag |
| 陳伯伯 | veg (gift) | 朋友田裡的菜…／菜園今年收太好… | any visit | occasional | ≥ 21 days apart |
| 陳伯伯 | friend | 今天帶老朋友來。／以前教書的同事，退休了才有空。 | any visit | occasional | ≥ 14 days apart |
| 陳伯伯 | students | 以前的學生昨天來看我，都當爸爸了。 | repeatable | ONCE (specific news) | once |
| Mia | deadline / delivered | 先給我咖啡，稿子還沒交。／稿子交了！… | repeatable | HABIT (her work rhythm) | unchanged |
| Mia | coworker | 同事一直問我都吃哪裡，帶她來了。／今天有伴，不用一個人吃。 | any visit | occasional | ≥ 14 days apart; after the first time, only 「今天有伴，不用一個人吃。」 |
| Mia | drawing (gift) | 幫店裡畫了個小東西… | once (flag) | ONCE | unchanged; the flag now keeps the day |
| Mia | moved | 搬家了，但還是會繞過來。 | **repeatable** | ONCE | once |
| 小林 | late | 今天加班，還好還開著。／趕上了。 | repeatable | HABIT | unchanged |
| 小林 | promo / newjob | 升職了，今天不趕。／換工作了，離這裡遠一點，還是會來。 | once (flags) | ONCE | unchanged; the flags now keep the day |
| Leo | broke | 今天只能點這個。／月底了。 | early visits | HABIT | unchanged |
| Leo | payday | 打工薪水下來了！ | any visit | occasional, student only | ≥ 25 days apart; not after graduating |
| Leo | classmates | 同學說想來看貓。／跟同學一起… | any visit | occasional | ≥ 14 days apart |
| Leo | exam | 期中考週，吃完就回去唸書。／考完再來好好吃。 | any visit | periodic, student only | ≥ 25 days apart; not after graduating |
| Leo | finals (from the old pool) | Jill 姊，我期末考考完了！ | 35% of orders | periodic, student only | ≥ 60 days apart |
| Leo | plant (gift) / jobhunt | 送了一盆多肉…／快畢業了，開始找工作。 | once (flags) | ONCE | unchanged; the flags keep the day |
| Leo | grad (from the old pool) | 我畢業了，第一份薪水就是想來這裡吃一頓。 | 35% of orders | ONCE | after the job hunt, once |
| Sophie | signature / strict | 今天想看看招牌菜。… | repeatable | HABIT | unchanged |
| Sophie | writer | 我帶了一位朋友，她在寫餐廳專欄。 | any visit | occasional | ≥ 30 days apart |
| 王家 | share / alone | （分一份）／先生今天出差，我一個人來。… | repeatable | HABIT | unchanged |
| 王家 | anniv | 今天是我們的結婚紀念日。 | once (flag) | ONCE | unchanged; the flag keeps the day |
| 王家 | flowers (gift) | （自己種的花） | again 6 days after the last flowers | occasional | ≥ 30 days since the last flowers |

## Two regulars who know each other (REG_PAIRS)

| Pair | Lines | Was | Category | Now |
|---|---|---|---|---|
| 陳伯伯 × 王先生 | 王先生，好久不見。／陳老師！ | every 5 days when both are in | ONCE (they find out they know each other) | once; a pair that already met (their record says so) never plays it again |
| Mia × 小林 | 你也在這棟上班？／三樓。你是樓上那間？ | every 5 days | ONCE (a discovery) | once, as above |
| Sophie × Leo | 學生，點那道，不會錯。／好、好，那道。 | every 5 days | HABIT | unchanged |

## Checked, no change needed

- **World memories (WORLD_MEM)**: side hall, terrace, kitchen, glass, ceiling, catwalk, expansion, first special,
  storm, busiest day, husband. Each is read from a real day in the save, surfaces in a window after it, and is said
  once per save.
- **Dylan**: the running act (DYLAN_ACT) is his and Jill's habit by design. The restaurant scenes (DYLAN_SCENES) play
  once each. Valentine's rotates year to year. Regulars noticing him have a 4-day gap. The Jill × Dylan revision is
  in qa4_2026-10-01_dylan_dialogue.txt.
- **Named guests**:
  - 周董: 「隨便」 is his habit; 「那明天再來。」 is capped at 3.
  - Ken × 杜: the argument is their habit; the wine question happens once.
  - Madame Lin: speaks only when something really changed; 「冷氣還沒換啊。」 comes while it is true.
  - The critic and the inspector: event lines.
  - Mr. Hart, 吃貨小琪, 美食部落客 Momo: their posts are chosen per guest.
- **Staff**:
  - A new hire's first-shift question happens once per hire.
  - The veteran's answer is a habit.
  - 晴 × 阿拓 and the Lounge staff lines are contextual habits.
  - The milestone scene plays once.
- **Story events (STORY_EV)**: ambient events are habits with cooldowns; minor and major beats are once or capped.
  The story audit (story page) classifies these separately.

## Older saves (migration `dlgAuditMig`)

For a save from before this audit:

- A regular who had reached tier 2 had been saying their old third line every few visits.
  - A once-callback (陳伯伯's four tables, 小林's promotion) is marked as already said.
  - A rare callback (Sophie's 「只有這裡」, the Wangs' anniversary) starts its gap on the day the save is loaded.
- A moving or former-students moment that the regular's own record shows already happened is not a new event again.

On the player's Day 52 save, 小林 will not bring up the promotion again.

Leo, who has not looked for a job yet in that save, will graduate once, later, after his job hunt.

Test: `regulars_remember_their_life_not_replay_it` (the player's Day 52 save).
