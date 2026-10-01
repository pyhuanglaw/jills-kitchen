# v2.4 — audit and plan: Staff Lives, 怡君, 《那面牆》, the Second Floor, the Staff Room, the Private Dining Room

Written 2026-10-01 against v2.3-rc3 (tag `v2.3-rc3`, published as version 37). The canonical brief is
`docs/v24/implementation_pass_2026-10-01.txt` (section letters below refer to it).

**Revised the same day (13:30–13:37) for three corrections from the player, which win where they differ:**
- `pacing_correction_2026-10-01.txt`: much shorter arcs. 怡君 ~7–10 days, 2–4 settled days, 《那面牆》 ~12–18 days in
  8–10 beats, 2–4 days before the Second Floor's first hints.
- `pacing_rule_correction_2026-10-01.txt`: no global gaps or cooldowns between beats or stories. At most one major
  beat a day; waits only where the fiction needs time.
- `canon_change_xiuqin_2026-10-01.txt`: **秀琴阿姨** (cleaner, late 50s, 國雄's wife) is 怡君's mother, the one who
  knows Sophie and Mia, and the family at the centre of 《那面牆》. 阿珠姐 stays a senior kitchen veteran and never has
  to leave the kitchen for these stories. §2–§5 below are written to the corrected canon.

Read with it:
- the visual addendum (`visual_addendum_yijun_wall_2026-10-01.txt`);
- the Second Floor visual reference (`second_floor_visual_reference_2026-10-01.txt`, the two pictures in `refs/`);
- the long-arc direction (`second_floor_and_long_arcs_2026-10-01.txt`);
- 《那面牆》 (`arc_that_wall_2026-10-01.txt`);
- the outside casts (two files and pictures).

## 1. What exists today (canon from the code)

**Staff**
- 20 named staff in role pools (`CREW_NAMES`, game.js 222), plus the Lounge four (Evan, 沈晴, 安安, 阿拓).
- Hire order inside a role is fixed by the pool:
  - chefs: 阿德師傅, Marco, 小林師傅, 阿珠姐, Hugo, …
  - waiters: 小茉, Kai, Nina, …
  - cleaners: 秀琴阿姨, 小彤, …
- No ages, no backstories, no family anywhere in the code. Portraits for all 20 come from the player's v2.3 sheets.
- The player's Day 52 crew, in hire order: 阿德師傅, 小茉, Marco, 小林師傅, 秀琴阿姨, 阿珠姐, Kai, Nina, Hugo, 阿哲, 小彤, 阿勇. All LV5. All "legacy": tracking began at v2.3, so `days` is 2–3.

**Regulars used by this pass**
- **Sophie**: 「味覺很挑剔的美食家，嘴上嚴格，心很軟。」 Jill asks her 「今天不寫稿？」, and she says 「我寫過很多餐廳……」. She writes, so magazine / editorial work fits.
- **Mia**: 「樓上設計公司的設計師，永遠在趕稿。」 小林 works on 3F and asks her 「你是樓上那間？」, so her firm is above 3F and the second floor can be vacant. Interior design fits.
- **王先生**: 「結婚多年，每週帶太太來約會一次；報紙看到一半就會被叫去點餐。」 No occupation yet, so lawyer contradicts nothing. He usually comes with 王太太, sometimes alone (`wang_solo`).
- **Sophie × Mia** (`sm_a` … `sm_h`): story state began empty at v2.3. The Day 52 save has none of these beats yet, so they are not "together" there yet.

**Story architecture, reused as is**
- `story()` facts and pair relations.
- The arbiter `STORY_EV` / `storyTick`: lanes, cooldowns, misses, Class A floors.
- Presence helpers (`presentId`, `seatedId`).
- Presentation:
  - `scene()`: the modal dialogue with portraits; lines without a portrait show the name;
  - `portraitLine`, `sayS`, `sayG`, `noteLine`.
- Journal:
  - 人物／關係支線 = `STORY_LINES` (beats keyed by facts);
  - 餐廳故事 = `restChapters()` (hidden chapters with a tease).
- Story Photos: `STORY_PHOTOS` with `art` or a drawn `stage`.
- Visitors are scheduled with the schedule's own hash coins (`storySchedule`), so the day's random stream is left alone.

**Rooms**
- `ROOMS` main / kitchen / side / front / lounge.
- `doorway(a,b)`: every door leads to main. `nextHop` and `stepTo` move people between rooms.
- The Lounge shows what adding a room touches: layout constants, a drawing function through `roomBg`, tables in `buildTables`, tabs, doorway, staff duty, the project and its reveal.

**Cats**
- 柔柔 = `mikan`, 女生, 「橘色金吉拉，白圍兜配白手套」.
- 小齁 = `ban`, 女生, 「虎斑白臉，鼻子上一道白，白胸口、白手套」.
- Cats never enter the kitchen or the Lounge. The side room uses `away='side'` + `hidden` — a precedent for "not here".
- Names can be changed, so story text uses `catName()`.

**Save**
- One save (`jills-kitchen-save-v1`). `fillDefaults` deep-merges a few objects; `story` is created lazily.
- Old saves start story state empty; nothing is inferred.

## 2. Conflicts and what this pass does about them

| Conflict | Decision |
|---|---|
| A1 — 營運升級 「後場休息室」 (bought around Day 27 in the player's save; +2 staff; nothing drawn) | Renamed **後場整理區** with new text: shelves, a rack, a place to change and drop things. The +2 staff and the achievement stay; no refund, no rebuy. Drawn small in the kitchen (shelves, a few hooks), never with a seat or a door. It does not answer the Staff Room's need — it is part of the evidence |
| A2 — tenure since v2.3 only | `tenure(m)` gives a coarse class, never a date. **Legacy staff** (hired before v2.3, `sinceLegacy`): 「熟手」 by default; where the player's canon says more, that wins — 阿珠姐, 秀琴阿姨 and 阿德師傅 are 「資深」 (veteran cook; legacy staff who watched the restaurant grow; quiet stable routines), 小彤 is 「較新」 (early in her working life; 「熟手」 after 45 counted days). **Hired after v2.3**: their counted days (新 under 10, 熟手 from 10, 資深 from 60). Story gates read the class; the staff card keeps showing the counted days ("從 v2.3 起算"). New hires stay new (《第一天》 unchanged). 《第二層左邊》 (`veteran_knows`) goes to 阿珠姐 when she is in, else the most senior cook by class |
| A3 — no schedules | `crewHere(m)`, story-only presence: here / 晚點到 / 今天沒來 / 已經下班. Only an authored beat sets it, for that one day. A staff member who is not here does no work that day; nothing else changes. No rota, no UI, no chores |
| The random office guest 「Kevin」 | Renamed in the random pool, so Kevin is only ever Marco's old colleague (later pass) |
| 小彤 is a cleaner; 《第一天》 only fires for waiters and chefs | Her arc is later (P5); her first-day line will get a cleaner's version then |
| Crew cap 12/12 on Day 52 | 「下面第二格」 needs a new hire; it stays in P5, after the second floor raises the cap |
| ~~A chef never leaves the kitchen on screen, but 阿珠姐 must meet 怡君, Sophie and Mia at a table~~ | Resolved by the canon change: the mother is **秀琴阿姨**, a cleaner, already a walking sprite in the dining rooms. A beat that needs her at a table gives her a **walk-over** task (she walks to that table, stands for the exchange, goes back to work) — the same movement as clearing a table. No cook ever leaves the kitchen for these stories |
| Where the stairs to 2F are | The internal staircase comes down in the **side room** (the unit next door that was opened up): a door in the side room's near wall, bottom edge, beside the cats' bowls. That is how the cats get up without ever leaving the building. The second floor's own reference puts the stair opening at its lower right, above that corner |
| The building's other floors | 3F and above are offices (小林, Mia's firm). 2F is the landlord's, vacant. The street view gets the 2F facade above the sign: dark windows, which light up after the lease |

## 3. Architecture (nothing parallel to what exists)

1. **Arcs on the existing arbiter.**
   - An arc is an ordered list of stages. Each stage is a `STORY_EV` entry with `once`, a `when` that requires:
     - the previous stage;
     - at least *gap* days since it;
     - the people really present, through a `present` check.
   - A run writes its fact.
   - The arc's Journal line is a `STORY_LINES` entry listing only the meaningful stages; ambient steps write facts but are not in the denominator.
2. **Pacing** (revised by the two pacing corrections: narrative time, not cooldowns).
   - **At most one major beat a day**, across every story. The arbiter already does this (`LANE_CAP.major` 1 a day,
     shared with the v2.3 stories); v2.4's major beats go through it, including the away-from-the-restaurant
     vignettes.
   - **No global gaps.** Nothing like "2 days between stories" or "a cooldown after every beat". A beat may come the
     day after the one before it when the people it needs are really there.
   - **Waits only where the fiction needs time.** Each stage has its own minimum `gap` in days after the stage before
     it — 1 for most (the next day is fine), longer only for viewings, a handover, settling in after the move, rain, a
     professional inspection, collecting documents, a formal retainer, scheduling the mediation, repairs.
   - **Presence.** A beat needs the people it shows. When a beat is due, the visit schedule brings those regulars that
     day with a high chance (the schedule's own hash coins, so the day's random stream is untouched). The arc does not
     stall waiting for a lucky visit.
   - **No load-time dump.** The first v2.4 beat cannot come before the second day the new version is played.
   - Ambient life (cats, regulars, staff chatter, v2.3 stories) carries on as before, beside and between beats.
3. **Chronology without brittle coupling** (brief B). Eras in order, each with its own entry condition:
   - 怡君 era;
   - 《那面牆》 era: opens 2 days after the spare key (the move has settled), and its first beat needs rain;
   - Second Floor era: opens 2 days after the settlement. It is not walled behind the aftermath, and its own stages
     carry its own pacing (awareness → inspection → later the missing cats → pressure → asking → the lease → the open
     floor);
   - Staff Room;
   - Private Dining.

   **Fallback (dormancy).** An era whose people cannot be there in this save (怡君's needs 秀琴阿姨 on the crew) does
   not hold the next era forever. Once the next era could start and has waited 5 days, the blocked era becomes
   *dormant*: skipped, not completed, never shown as done. A dormant era does not wake up after a later era has had
   its first beat, so the chronology is never reversed.
4. **Knowledge.**
   - An outside character is "introduced" by a fact when the first beat really happens.
   - Lines that name someone check that the speaker was present then (`relSet(…,'introduced')`) or that the fact exists.
   - No epistemology engine.
5. **Outside characters.**
   - `NAMED` entries with `story:1`: a portrait, a matching sprite, never in a random pool, one visit a day.
   - Scheduled by `storySchedule` only when a beat or a later ambient visit wants them.
   - Not staff.
6. **Story illustrations** (visual addendum).
   - `STORY_ILLUS`: an id, a title, a caption and the art key.
   - `storyIllus(id, then)` shows the picture full-screen before or after the scene's lines.
   - The Journal's beat entry can reopen it. Not in the Life Album.
   - Until the player's art is supplied, a fallback **drawn in the game's own style** (the room, the wall, the people as sprites) with a small 「插圖待補」 label — never a portrait standing in.
7. **Second Floor state**:
   - `S.up`: `{seen, cats, ask, lease, built, open}`, plus the construction state for 休息室 and 包廂 (zone, stage).
   - A new room `up` (二樓), drawn from the reference: the window row along the back wall, a column in it and one in the floor, the stair opening with its railing at the lower right.
   - Zones are data, so the Staff Room's and the Private Room's walls grow inside the floor later without redrawing it.
   - The tab and the doorway exist only when the floor is in play.
8. **Missing cats.**
   - That afternoon a mundane access (the landlord's water-meter check) leaves the stair door unlatched.
   - From late in the evening 柔柔, then 小齁, are `away='up'`: really not in any room you can see.
   - At closing, the present staff and Jill notice. Short search lines, rooms shown one after another. 「這個怎麼開著？」 Up the stairs: the first full view of 2F, the two cats where they went. 「妳們兩個。」
   - Then down, and the door locked. At most about an hour of game time missing.

## 4. The chronology and what a Day 52 player meets

Revised for the pacing corrections and the canon change. "Gap" is the stage's own minimum wait in days after the stage
before it, and only where the fiction needs time; 1 means the next day is fine. Major beats also share the one-a-day
cap with every other story. Days are what a Day 52 player should roughly see, not gates.

**怡君 (target ~7–10 days; Day 52 save: from Day 53, moved in by ~Day 61)**

| # | Beat | Lane | Who has to be there | Gap |
|---|---|---|---|---|
| Y1 | 《吃飯啊》 — 怡君 eats here; 秀琴阿姨 walks over: 「妳怎麼來了？」「吃飯啊。」 Illustration `yj_intro` | major | 怡君, 秀琴阿姨 | era open (the second day played) |
| Y2 | listings: 怡君 scrolling flats at her table; 秀琴阿姨 glances over | minor | 怡君, 秀琴阿姨 | 1 |
| Y3 | 「找到？」「找到三個。」 — three ordinary options and their tradeoffs | major | 怡君, 秀琴阿姨 | 2 (viewings) |
| Y4 | 「她決定了。」 — the smaller one, closer, fits her life; a reasonable choice with what she could see | minor | 秀琴阿姨 (tells Jill) | 1 |
| Y5 | 《搬家》 — 秀琴阿姨 晚點到 (she helped with the move); one line when she comes in | minor | 秀琴阿姨, late | 2 (the handover) |
| Y6 | 備用鑰匙 — morning vignette at 怡君's new home; the wall is in the room and looks normal. Illustration `yj_key`. In service Jill notices the new key on 秀琴阿姨's ring | major | (away scene) | 2 (settling in) |

**Sophie × Mia × 秀琴阿姨 (before the wall)**
- Ambient, while she clears or wipes near their table: two or three short exchanges. They build the pair's familiarity
  (`spoke`). 《那面牆》's first beat needs `famOf` ≥ 2 with both of them.
- 「今天怎麼只有妳？」「她加班。」「喔～～」 (minor): once Sophie and Mia come together (`sm_h`) and Sophie comes alone.
  It happens whenever that is true, before or during the wall.

**《那面牆》 (target ~12–18 days, ten beats; Day 52 save: begins ~Day 63–65, settled ~Day 78–80)**

| # | Beat | Lane | Who | Gap |
|---|---|---|---|---|
| W1 | 秀琴阿姨不太對 — wipes the same table twice; Sophie and Mia ask; 「沒事。」 Later, her phone call by the side door: 「妳先拍起來。」「不是擦掉就好了啦。」「上次不是才叫人來？」「……好啦，妳先不要弄。」 | major | Sophie, Mia, 秀琴阿姨 | era open + rain in the last 3 days (after 5 days without, a night rain the game did not show) |
| W2 | They learn what it is: 怡君's flat leaks when it rains. Photos on 秀琴阿姨's phone; Mia: 「這裡以前可能處理過。」「所以他們本來就知道？」「不是。這只能說可能處理過。」「差在哪？」「差很多。」 Sophie starts asking for the listing, the viewing photos, the messages, the disclosure, the dates | major | Sophie, Mia, 秀琴阿姨 | 1 |
| W3 | First working theory: the seller's side says they never had a leak; the disclosure form says 無滲漏水; the listing photo shows that wall freshly painted. "Water comes in at the window and they painted over it." | minor | 怡君 (with her folder) or 秀琴阿姨 + Sophie | 2 (documents) |
| W4 | 王先生 at the next table: 「等一下。」「妳女兒買的是中古屋？」 He separates the three questions: (1) was the defect there before the handover, (2) was that spot repaired or covered before, (3) did the seller know of this leak and not disclose it. Suspicion, physical evidence, legal relevance, what can be proven. Casual advice: keep this, do not say that, find these | major | 王先生, Sophie, Mia, 秀琴阿姨 | 1 |
| W5 | Setback: a water test on the window frame — nothing comes in. The window was not it. And the "fresh paint" listing photo has no reliable date. 「喔，原來沒這麼簡單。」 | minor | 秀琴阿姨 + Sophie or Mia | 2 (the test) |
| W6 | The leak-detection report: water through a crack in the outer wall behind the patch; old water damage and an old repair under the paint. (1) and (2) now have evidence; (3) does not yet. 「如果要我處理，就正式委任我。」 怡君 retains him. The fee: 「……這比我之前問的低很多欸。」「你是不是算太少？」「沒有。」「真的？」「妳女兒有付錢就好。」 | major | 怡君, 王先生, 秀琴阿姨 | 3 (the inspection) |
| W7 | Preparation: his letter; the seller's lawyer: "never knew"; then the building's repair record shows a worker for that wall before the sale. Mediation is applied for | minor | 王先生 or 秀琴阿姨 | 2 (documents) |
| W8 | 調解 — away scene in the mediation room: 「那我們一項一項談。」 The evidence item by item; the other side concedes the old repair and disputes the knowledge; a proposal; 怡君 decides to accept a negotiated amount | major | (away scene) | 3 (scheduling) |
| W9 | 和解 — compensation recorded as a fact; repairs to start. Illustration `wall_settled` | minor | 怡君 or 秀琴阿姨 | 1 |
| W10 | Sophie: 「我想寫這個。」「寫我的？」「不一定寫妳。是寫這件事。」 怡君 keeps control of her part | minor | Sophie, 怡君 | 3 (only once the matter is closed) |
| — | Aftermath (ambient): before 王先生 sits, 秀琴阿姨 has wiped his table and put the day's paper there; two lines. Later 「牆弄好了。」 | ambient | 王先生, 秀琴阿姨 | 2 / 5 |

**After that**

| Era | Stages | Day 52 save |
|---|---|---|
| 二樓 | opens 2 days after W9 → 「樓上也是你們的？」 → staff mention → Jill 看過樓上 → (days) → **柔柔和小齁不見了** → pressure (staff and customers) → 「樓上不是還空著？」 → **「整層？」「整層。」** → the whole floor | first hints ~Day 80–86 |
| open floor | people start using it; the cats visit; 柔柔's window | a real stretch, not one day |
| 休息室 | 《箱子》《又在找位置》《東西放哪》 (may start earlier) → **《大家待的地方》** → walls and a door → I / II / III. 秀琴阿姨 may add evidence (國雄 waiting for her, 怡君 waiting) but it is everyone's room | later |
| 包廂 | its own evidence → **《關上門以後》** → walls and a door | later still |

國雄's own arc 《今天不回去吃》 (P5) does not depend on the wall, but he is 怡君's father: nothing he says may sound as if
he had never heard of her flat.

## 5. Illustrations needed from the player

Hooks exist from the start, each with an in-game fallback (asked for on 2026-10-01, corrected for the canon change).
**All four were supplied the same afternoon** (`docs/v24/art/illus_*.png`, packed by `tools/story_art.py`; the flat in
② and ③ is one room, checked side by side; ③ is the player's second version, with Sophie as she looks). The
stand-ins only show if a picture is missing. Asked for next (optional, they make the scenes better, nothing waits on
them): expression portraits — 秀琴阿姨 worried / on the phone / 姨母笑, 怡君 tired / relieved, 王先生 lawyer mode / a dry
smile, Mia thinking; for P2 the landlord, and `up_cats`.

1. `yj_intro`: 怡君 at Jill's Kitchen; 秀琴阿姨 in her cleaner's clothes at her table.
2. `yj_key`: 怡君's new home, 秀琴阿姨 visiting, the spare key. The wall is in view and looks normal; any old repair
   is barely visible.
3. `wall_leak` (**required**): the same room and wall after the rain. Mia at the repaired patch, Sophie with photos and
   the timeline, 秀琴阿姨 there, 怡君 possibly.
4. `wall_settled`: after the mediation — 怡君 and 王先生, restrained.

Later, for the floor:
- `up_cats`: the first view of the empty 2F with 柔柔 and 小齁. It can be drawn in-game from the reference, so a picture is optional.
- The Staff Room and Private Room interiors, when those passes come.

## 6. Releases

- **rc4: P0 + P1.**
  - Foundations: A1–A3, pacing, illustrations, the walk-over.
  - 怡君 and 《三個選項》.
  - The Sophie / Mia / 秀琴阿姨 familiarity.
  - 《那面牆》 complete.
  - The Day 52 player meets 怡君 the day after updating and sees the wall settled around Day 80.
- **rc5: P2.**
  - The 2F room from the reference, its facade, the stairs.
  - The floor's arc with the missing cats, the lease, the open floor.
- **rc6: P3 + P4.** The Staff Room (walls, door, I–III) and the Private Dining Room (walls, door).
- **P5**: the other Staff Lives arcs (Kevin, 珊珊, 宇翔, 小彤, 老林, 國雄) where they do not delay the above. Some first meetings may come earlier if they fit the pacing.

Each release gets:
- its own tests;
- migration on every player save;
- a multi-day pacing simulation on Day 52 / Day 46, checked against the targets above;
- phone screenshots;
- a full regression.
