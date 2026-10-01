# v2.4 — audit and plan: Staff Lives, 怡君, 《那面牆》, the Second Floor, the Staff Room, the Private Dining Room

Written 2026-10-01 against v2.3-rc3 (tag `v2.3-rc3`, published as version 37). The canonical brief is
`docs/v24/implementation_pass_2026-10-01.txt` (section letters below refer to it).

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
| A2 — tenure since v2.3 only | `tenure(m)` gives a coarse class, never a date. **Legacy staff** (hired before v2.3, `sinceLegacy`): 「熟手」 by default; where the player's canon says more, that wins — 阿珠姐, 秀琴阿姨 and 阿德師傅 are 「資深」 (veteran cook; legacy staff who watched the restaurant grow; quiet stable routines), 小彤 is 「較新」 (early in her working life). **Hired after v2.3**: their counted days (新 under 10, 熟手 from 10, 資深 from 60). Story gates read the class; the staff card keeps showing the counted days ("從 v2.3 起算"). New hires stay new (《第一天》 unchanged) |
| A3 — no schedules | `crewHere(m)`, story-only presence: here / 晚點到 / 今天沒來 / 已經下班. Only an authored beat sets it, for that one day. A staff member who is not here does no work that day; nothing else changes. No rota, no UI, no chores |
| The random office guest 「Kevin」 | Renamed in the random pool, so Kevin is only ever Marco's old colleague (later pass) |
| 小彤 is a cleaner; 《第一天》 only fires for waiters and chefs | Her arc is later (P5); her first-day line will get a cleaner's version then |
| Crew cap 12/12 on Day 52 | 「下面第二格」 needs a new hire; it stays in P5, after the second floor raises the cap |
| A chef never leaves the kitchen on screen, but 阿珠姐 must meet 怡君, Sophie and Mia at a table | A **table visit**: a staff member walks out of the kitchen to a table, stands there for the exchange, walks back. Real presence, a few seconds, no other effect |
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
2. **Pacing.**
   - `v24Pace()`: at most one meaningful v2.4 beat a day.
   - At least 2 days between meaningful beats of different arcs.
   - Each arc's own gaps are 2–7 days.
   - Ambient hints at most one a day.
   - The first v2.4 beat can come no earlier than the second day the new version is played (no load-time dump).
3. **Chronology without brittle coupling** (brief B). Each era opens when the previous one has ended plus breathing room, or after a fallback if the previous one cannot happen in this save:
   - 怡君 era;
   - 《那面牆》 era;
   - Second Floor era;
   - Staff Room;
   - Private Dining.

   For example, the Second Floor opens when 《那面牆》 is done plus 6 days. If 阿珠姐 has not worked here for 20 days, 怡君's arcs are skipped (dormant, not completed) and the floor opens anyway.
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

## 4. The chronology and what a Day 52 player meets (rough, depends on who comes in)

| Era | Stages (meaningful ones in bold) | Rough length |
|---|---|---|
| 怡君 | **《吃飯啊》** → (她在看房子) → **「三個。」** → 「她決定了。」 → 《搬家》 (阿珠姐 晚點到) → **備用鑰匙** | ~20–30 days |
| breathing room | ordinary days; 怡君 sometimes eats here | ≥ 8 days |
| Sophie × Mia × 阿珠姐 | needs Sophie and Mia to have left together (`sm_g`): **「喔～～」** | when it happens |
| 《那面牆》 | 阿珠姐不太對 → 電話 → **漏水** (a rainy day) → **Mia 看照片** → Sophie 排時間 → **王先生「等一下。」** → 問題 → 照片沒那麼有用 → 水不是從那裡來 → **抓漏的報告** → **「就正式委任我。」** → **律師費** → 準備 → **調解** → **和解** → 修 → **Sophie「我想寫這個。」** → **「今天是不是比較多？」** | ~50–70 days |
| breathing room | | ≥ 6 days |
| 二樓 | 「樓上也是你們的？」 → staff mention → Jill 看過樓上 → (days) → **柔柔和小齁不見了** → pressure (staff and customers) → 「樓上不是還空著？」 → **「整層？」「整層。」** → the whole floor | ~25–40 days |
| open floor | people start using it; the cats visit; 柔柔's window | ≥ 10 days |
| 休息室 | 《箱子》《又在找位置》《東西放哪》 (may start earlier) → **《大家待的地方》** → walls and a door → I / II / III | later |
| 包廂 | its own evidence → **《關上門以後》** → walls and a door | later still |

## 5. Illustrations needed from the player

Hooks exist from the start, each with an in-game fallback:

1. `yj_intro`: 怡君 at Jill's Kitchen, 阿珠姐 out of the kitchen at her table.
2. `yj_key`: 怡君's new home, 阿珠姐 visiting, the spare key.
3. `wall_leak` (**required**): the affected wall or ceiling in 怡君's home. Mia examining the repaired patch, Sophie with photos / the timeline, 阿珠姐 there.
4. `wall_settled`: after the mediation — 怡君 and 王先生, restrained.

Later, for the floor:
- `up_cats`: the first view of the empty 2F with 柔柔 and 小齁. It can be drawn in-game from the reference, so a picture is optional.
- The Staff Room and Private Room interiors, when those passes come.

## 6. Releases

- **rc4: P0 + P1.**
  - Foundations: A1–A3, pacing, illustrations, table visits.
  - 怡君 and 《三個選項》.
  - The Sophie / Mia / 阿珠姐 familiarity.
  - 《那面牆》 complete.
  - The Day 52 player starts meeting 怡君 within days and has weeks of story before the floor.
- **rc5: P2.**
  - The 2F room from the reference, its facade, the stairs.
  - The floor's arc with the missing cats, the lease, the open floor.
- **rc6: P3 + P4.** The Staff Room (walls, door, I–III) and the Private Dining Room (walls, door).
- **P5**: the other Staff Lives arcs (Kevin, 珊珊, 宇翔, 小彤, 老林, 國雄) where they do not delay the above. Some first meetings may come earlier if they fit the pacing.

Each release gets:
- its own tests;
- migration on every player save;
- a multi-day pacing simulation on Day 52 / Day 46;
- phone screenshots;
- a full regression.
