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

**Revised again (15:07–15:11) for the fresh-game premise and two standing requirements:**
- `xiuqin_from_day1_2026-10-01.txt`: 秀琴阿姨 is part of the restaurant from Day 1 / the first days, without giving a
  free full-strength cleaner. 怡君 is not gated on a late day or on Sophie × Mia. Two progressions — A: 秀琴 → 怡君 →
  《三個選項》 → the move; B: Sophie / Mia's long-term visits → familiarity with 秀琴 — meet in 《那面牆》. Validate on
  the Day 52 save and on a fresh save. Not more beats; not more rc4 scope. (§3.9, §4.)
- 15:08: no Simplified Chinese anywhere in the game; names may be English.
- 15:11: 「因為這次新增很多東西 說明書和一開始的教學都要到位」 — the manual and the opening tutorial must cover the new
  content (§6).

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
9. **秀琴阿姨 before she is on the crew** (the fresh-game premise; the smallest safe way, no second staff system).
   - *Helper mode* while no cleaner is on the crew (and she was never let go): she is `XQ_HELPER` (`id 'xq'`), a sprite
     of her own (`R.xqh`) that is not in `S.crew`, draws no wage and claims nothing. Most evenings (always the first,
     and the evenings 怡君 is coming) she walks in at ~92% of the service, tidies beside tables nobody is at that are
     already clear (never a dirty one: clearing is the game's), says a few words with Jill, and goes home about twenty
     seconds into the closing. No random draw anywhere in it, so a day with her and without her is the same day.
   - `xqm()` is "秀琴阿姨, whichever way she is here": the crew member, else the helper. The P1 beats use it. The
     helper's walk-in fires the arbiter's `xqin` context, so 怡君's steps can play when her mother comes in.
   - *Hiring the first cleaner is hiring her* (the pool already puts her first): the new crew member keeps `id 'xq'`,
     so who she has talked to and what she knows carry over; one line over the shop, 「那以後就天天來了。」; her card
     says 「今天起正式上班」. Let go, she does not come back to help in the evenings (`xq_gone`).
   - *A — 怡君*: the era opens on the first v2.4 day, but its first beat waits for its people (`V24_ERAS.can`):
     秀琴阿姨 known for about a week (`xqKnown`: legacy crew always; otherwise 6+ days since she was first around and
     4+ evenings or working days). In helper mode 怡君 comes late (90%, `hold`: a quiet evening does not pull her
     visit earlier) and waits for her mother if she has finished eating; when the fridge is empty Jill orders in one
     portion for her (the opening days' emergency order, 1.5×) rather than sending her away hungry. On moving day the
     helper is helping with the move instead (「晚上不會來幫忙收店」), and Jill asks the next evening.
   - *B — Sophie / Mia*: 《那面牆》's first beat needs the familiarity exchanges (`smFamiliar`) **and** a long
     acquaintance (`smLongTime`): Sophie and Mia have each been in 8+ times, and 秀琴阿姨 has worked the floor 6+ days
     (legacy crew always). The wall needs her on the crew: a helper is only in at closing.
10. **The day's one major, held for the people who came for it** (pacing, measured on the Day 52 save). When the
    schedule brings someone for a due v2.4 major beat (`V24_WANTS … k`), that beat keeps the day's single major slot
    until it plays or until 85% of the service; other stories' major moments that come up meanwhile are counted as
    missed (their priority rises) and come another day — except a beat that has only that day (floor 0: Dylan on
    Valentine's), which is never held back. Grouped story visits keep their hour (`hold`), and the first of a group
    sits in a room with a free table for each of them, so they really are in the same room. The cost is measured in
    `docs/V24_RC4_REPORT.md` §4: the v2.3 majors that share those days (Sophie × Mia's) come some days later.
    **Kept by the player's decision** (17:34, `decision_priority_1734_2026-10-01.txt`): this default stays, date-exclusive
    beats keep their protection, and the Sophie × Mia delay is an rc4 normal-play observation item.

## 4. The chronology and what a Day 52 player meets

Revised for the pacing corrections and the canon change. "Gap" is the stage's own minimum wait in days after the stage
before it, and only where the fiction needs time; 1 means the next day is fine. Major beats also share the one-a-day
cap with every other story. Days are what a Day 52 player should roughly see, not gates.

**Measured** (`tools/sims/v24_pacing.py`, the Day 52 save, lazy bot, 40 days, seeds 7000 / 9100 / 4242 / 5555 /
8080 — after the 15:07 premise): spare key Day 61 in all five (target 59–62); the wall begins Day 63–65 (62–66);
mediation Day 79–81 (75–82); the Second Floor era opens Day 81–83 (78–86); never two major beats in a day; nothing on
the first day's start. **A new game** (`tools/sims/v24_fresh.py`, the perfect bot, three shop plans): 秀琴阿姨 from Day
1; 怡君 first comes Day 8, the spare key Day 16 (with or without a cleaner hired); the wall begins Day 21–27 (it needs her
on the crew and Sophie / Mia's long acquaintance) and settles about two and a half weeks later; Days 1–7 played with
and without her end with the same money, guests, stars, reviews and stock.

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
  - 秀琴阿姨 from Day 1 in a new game (the evening helper, §3.9); the first cleaner is her.
  - The manual (員工: 秀琴阿姨, 晚點到; 故事: 插圖, 店外的生活), the opening tutorial (Day 1: she walks in and says who
    she is to the place, then the coach names her once; Day 2's news; the staff tab's recruit note) and one 2.4 note
    for a save that was already going (systems only: late arrivals, illustrations, 後場整理區; who comes in the
    evenings if there is no cleaner yet) — the player's 15:11 request.
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

## 7. P2 — the Second Floor (rc5), as built

Written when rc5 began (2026-10-01, after the player's 「繼續吧」 at 17:57). Sources: `second_floor_and_long_arcs`
(the canonical direction), `second_floor_visual_reference` and its two pictures (the canonical geometry, Phase 0–1),
`second_floor_phases`, `implementation_pass` §I–K, S, T. The layout sketch's stair corner (bottom left) is superseded
by the picture (bottom right).

**The building.** The internal stairs come up from the side room (the unit next door that was opened up): a plain
wooden stair door at the side room's near edge, centre — there is room for it between the tunnel and the basket, and
it is the one place inside the restaurant the cats can reach without the kitchen. Closed it is a door and a mat; the
night it is not latched, the stairwell light spills through. The street view gets the second floor above the sign:
two big windows, dark while the floor is the landlord's, warm once it is Jill's.

**The room `up` (二樓)**, drawn from the reference in the game's front view: the back wall with the two big window rows
and the pilaster between them, the air conditioner over it, pendant lamps; a structural column in the middle of the
floor; the stair opening with its railing at the lower right (the stairs going down inside it); wooden planks.
- Vacant (the landlord's): boxes and a step ladder in the right corner, a plant in the left one, a folding table with
  two folding chairs along the left wall, dust. Seen first at night, with the cats.
- Taken (whole floor, basic works): clean, warm light, the boxes down to two; then movable furniture arrives over the
  first days — the shared wooden table and mismatched chairs, a plant, a utility cabinet, a coat stand, a floor lamp,
  and restrained cat things (a low cushion, a small stool, a scratching board). No partitions.
- Zones are data for later (`UP_ZONES`): staff room on the left, private dining along the windows, the stairs bottom
  right, an undecided area bottom left, the middle kept for circulation. Nothing is built on them in P2.
- Not a dining room: no guests, no tables to serve. The tab 二樓 appears once the floor is taken; before that the room
  is only seen during the missing-cats night.

**State.** Story facts, as everything else: `up_hint`, `up_staff`, `up_inspect`, `up_cats` (with `up_door`, the day's
unlatched door), customer pressure `up_busy` / `up_full` / `up_small`, staff pressure `sp_box` / `sp_seat` /
`sp_stuff`, `up_remind`, `up_ask`, `up_leak` (the 《那面牆》 callback). `S.up = {offer, lease, furn:{…}, traces:{…}}`;
`S.rooms.up` once taken. Old saves start with none of it.

**The arc** (era `up`: two days after the wall's settlement; needs the side room and a mature restaurant):

| # | Beat | Lane | Who | Gap |
|---|---|---|---|---|
| U1 | 「樓上也是你們的？」「不是，房東的。」「一直空著？」「好像是。」 — no journal | v24 | an established regular (12+ visits, not one of the wall's people) | era open |
| U2 | Staff, at closing: 「樓上真的一直都空著喔？」 / 「上面多大？」「不知道。」「妳沒上去過？」「沒有啊。」 | v24 | two present staff | 1 |
| U3 | The landlord's afternoon visit: he checks the vacant floor; Jill goes up with him; 「地板是好的，窗戶也是好的。」 He locks the door after. Brief, no room view | major | (vignette, the landlord) | 2 |
| U4 | **The missing cats.** That afternoon the landlord brings someone up to look at the air conditioner; the door closes but does not latch. Late in the evening 柔柔, then 小齁, are not in any room. At closing: 「柔柔呢？」「剛剛不是還在？」「小齁也不在。」 — the present staff and Jill search the rooms (the others are counted: 「包包在這。」…), someone finds the stair door: 「這個怎麼開著？」 「……柔柔？」 Upstairs, at night: 柔柔 by the window, 小齁 comes to Jill first. 「妳們兩個。」 Only then: 「……這裡滿大的欸。」「嗯。」 Down, the door latched. No unlock | major | the cats, Jill, the staff really here | 3 |
| — | Customer pressure, different needs: 「妳們現在人這麼多，沒想過樓上？」「樓上又不是我的。」「租啊。」「你講得很簡單。」 / a full night: 「今天又滿了？」「樓上還空著？」「還在。」 / 「妳這間越來越不像以前那麼小了。」 | v24 / ambient | different regulars | after U4 (+2) |
| — | Staff pressure: 《箱子》《又在找位置》《東西放哪》 (also the Staff Room's evidence later) | ambient | the people in them | from the era's opening, days apart |
| U5 | 「樓上不是還空著？」「那是房東的。」「我知道啊。」 or 「妳不是看過樓上？」「看過。」「很小？」「……不小。」 | v24 | a staff member | after U4 (+2), two staff and two customer kinds seen |
| U6 | At closing Jill looks toward the stair door: 「……樓上現在還空著嗎？」 She calls the landlord: 「妳真的要租樓上？」「嗯。」「下面不夠用了？」「開始有一點。」「整層？」「整層。」 The project is offered | major | Jill, the landlord | 2 |
| — | 「先看漏水。」 (Mia), Sophie laughs, 秀琴阿姨: 「真的，先看。」, 王先生 if he is there: 「……這次跟我沒關係。」 — only if the wall happened | ambient | Sophie, Mia, 秀琴阿姨 | after U6 |
| U7 | The project 二樓（整層） in 店舖工程; the reveal; next day the floor is open | (project) | — | the player |

Then open-floor life: the furniture arrives over a week; staff traces (a bag, a charger, a cup) once people start
going up; cats may go up on their own (restrained places); 柔柔 now and then back at her window. Not a Staff Room.

**Pacing target, Day 52 save:** the era opens ~Day 81–83 → U1 ~82–84 → U3 ~85–87 → U4 ~88–91 → U6 ~94–98 → the
project when the player buys it. **Price:** 二樓（整層） $350,000 — the largest building project (Lounge III is
$220,000, the cat walkway $300,000), about a week of a Day 52 restaurant's net; most mature saves have it by then. It
does nothing mechanical yet: it is the floor.

### 7.1 As built (rc5, 2026-10-01/02) — where the build differs from the plan above

- The era's first beat also waits for the restaurant's full size (level 5) and a crew of five; the crew's moments
  (`sp_*`) start with the era itself.
- U4's start of the day is a two-line scene, not a note: 「下午，房東帶冷氣師傅上樓看了一下冷氣。」 / the landlord,
  「好了。門我帶上了。」 — the player is told the door was opened that day, and shut.
- The customer beats have their people: U1 陳伯伯 (else 小林, Leo); 「妳們現在人這麼多…」 小林 on a busy night; 「今天又滿
  了？」 Leo seated after a wait; 「妳這間越來越不像以前那麼小了。」 王太太; a family wanting somewhere quieter only when
  the side room is full too. One customer moment a day.
- 《那面牆》's callback is at Sophie and Mia's table, 秀琴阿姨 walking over (「Jill 要把樓上租下來。」), Mia looking up at
  the ceiling first.
- The night: the unlit floor is dark (the stairwell, the street through the glass) until someone finds the switch; the
  stair well's deep end is the far end, the way on is at the near left; people and cats are routed round the railing.
- The project is offered at the end of the call like the Lounge (開始規劃 / 之後再說); bought, the floor is open the same
  evening (empty, two boxes) and the furniture arrives from the next day.
- The staff pools (the player, 19:07–19:16) and 許葳 came in during rc5: `docs/v24/staff_pools_1907_2026-10-01.txt`,
  `docs/V24_RC5_REPORT.md` §7.

## 8. rc6 — P3 the Staff Room + P4 the Private Dining Room (plan, 2026-10-02 03:00)

The spec is `docs/v24/rc6_final_spec_0300_2026-10-02.txt` (the player, 03:00; it wins over everything earlier where
they differ). With it: `staff_room_brief`, `private_dining_room_brief` (the parts the final spec keeps), the two
reference pictures (`refs/staff_room_stages_reference`, `refs/private_dining_room_reference`), `second_floor_and_long_arcs`
§24–27, `second_floor_visual_reference` §8–16, implementation pass L–N1, the 13:37 canon (秀琴阿姨 is 怡君's mother).
Scope rule from 02:37 (`rule_finish_everything_0237`): rc6 is released and the work goes straight on to P5.

**The floor (B).** The Private Dining Room takes the left window bay (the floor's left window is its window); the Staff
Room is inside, below it on the left, with no window view. Open: the middle, the right window bay (柔柔's window, the
stool, the scratching board, the shared table moved there), the column, the stairs, the corner by them (the third
zone, undecided). Real rooms: cut walls with dark caps in the cutaway view of 二樓 (like the player's second floor
picture), full-height doors with a narrow glass strip and a name plate; each room also has its own view, drawn from its
reference picture. Rooms: `staff` (休息室) and `pdr` (包廂), reached through 二樓 (one tab for the floor; tapping it
again goes through the rooms; the doors on 二樓 open them). Paths on the floor go round the column.

**Staff Room (C–K).**
- Need: 《箱子》 `sp_box`, 《又在找位置》 `sp_seat`, 《東西放哪》 `sp_stuff` (rc5) and 《等一下》 `sp_wait` (new: 怡君 waits
  at closing for her mother; nowhere to sit that is not a guest's seat). 《大家待的地方》 (major, closing, Jill alone,
  the brief's lines) when: the floor taken 7+ days and in use (`up_use`); level 5; 8+ restaurant crew; 3+ of them 熟手
  or more (tenure classes, never the telemetry days); an outside person introduced (`yj_meet`); 2+ kinds of evidence.
  Then the project is offered (開始規劃 / 之後再說), like the floor's.
- Phase I: construction, done the next day (walls, door, sofa, chairs, a table, basic storage, water, outlets; the
  cabinet, the floor lamp, the coat stand and one odd chair come in from the open floor). Phase II (5+ days later):
  lockers, a small fridge, a better sofa, tea and coffee, more storage, cups, coats and bags. Phase III (7+ days after
  II): better furniture, cushions, wear, a dining table. Improvements show the next day. One major construction at a
  time across the floor.
- Use (F, G): everyone on the crew, Restaurant and Lounge, with no story: early arrivals sit a moment at the start of
  the service; quiet moments in the evening (one at a time, short); at closing several go up, sit, drink something,
  talk, and leave. Lines are rare and small. Cats (H): now and then one follows someone in and sleeps on the sofa,
  then leaves; most of the floor's cat life stays outside.
- Traces only after the event (E): 阿珠姐 「插座不夠。」 → (Phase II) 「我就說吧。」; 怡君 brings a power strip her mother
  mentioned; 阿德's seat; 小彤 「坐啊。」「喔，好。」 on the first day, later her cup; Hugo and the fridge; 秀琴阿姨's
  food some days. No capacity (K).

**Private Dining (L–AF).**
- Need: 怡君 with three friends: 「要坐裡面一點嗎？」「有比較安靜的嗎？」「……沒有。」 (`pd_yj`); later a group that is
  not staff family with the same need (`pd_other`): 周董 with two guests, 「有比較不被打擾的位置嗎？」, where the save
  knows him, else a family at a busy hour. Then 《關上門以後》 (major, closing): needs both, 2+ days after the second,
  the Staff Room 10+ days old with traces in it, the room not begun. The project is offered.
- Phases: I 4–6 people (walls, door, the table for six), II 4–8 (the table extended, more chairs, furnishing),
  III 4–10 (the full room). Each raises the reservation demand. II and III open with use and money (II after 6 days
  and 3+ meals in the room; III after 8 more days and 6+ more), no new long arc (AF).
- Reservations (R–Z): automatic, one per evening (the dinner service is the game's one meal period), made at the start
  of the day for that evening with its party size and minimum spend fixed in the save (`S.up.pd.res`). The minimum is
  size × the restaurant's average check per guest (measured, rounded to $100) × a small private factor; never
  recomputed. The group comes, is seated in the room, orders as usual; the bill is the larger of what they ate and
  the minimum. On an evening with no reservation, a walk-in group of 4+ that fits may use it (normal bill); on a
  reserved evening the room waits for its guests. Frequency: a base chance per phase plus a quiet rise after evenings
  without one (soft pity, never shown); the first one within the first few evenings. The day's news says it:
  「今晚｜私人包廂｜已預約　6 位・最低消費 $X」.
- Story hooks (AA–AC): `pdBook(day,{kind:'story',...})` reserves an evening for an authored use first; the scheduler
  never puts a random reservation on an evening a story holds, and a story never takes an evening already booked.
  The payoff 「裡面可以嗎？」「可以。」 (the group that asked) uses it. Cats keep out while a meal is on (AD).
- Staffing (AG–AJ): Restaurant capacity +1 with Phase I, +1 with Phase III; Lounge unchanged.

**Economy (AL).** Prices from the measured late-game day (to be filled in §8.1): the Staff Room cheaper than the Private
Dining Room; Phase I the main cost of each; II and III less.

**Not built (AE, I, AV):** no approval, deposits, no-shows, calendars, packages, meters, chores, or frameworks.

**Tests (AS–AU)**, the saves, the pacing sims (the Day 52 and Day 61 saves with the floor and the rooms bought as soon
as they are offered; reservation frequency per phase), phone screenshots, the full suite.

### 8.1 Economy — what was measured and what was set (2026-10-02)

**The late-game day** (the player's Day 61 save played by the lazy bot, two 60-day runs, seeds 8100 and 9300): about
75 guests, takings about $51–55k, net about $55–57k a day with everything bought along the way (the floor, both rooms,
all their phases). Money goes from about $120k to about $2.6M over the sixty days.

**Prices** (unchanged from the plan; checked against that day):

| | Phase I | Phase II | Phase III | All three |
|---|---|---|---|---|
| Staff Room | $160,000 (≈ 3 days of net) | $70,000 | $90,000 | $320,000 |
| Private Dining Room | $240,000 (≈ 4½ days) | $120,000 | $160,000 | $520,000 |

The Staff Room is the cheaper room; each room's first phase is its main cost (walls, door, the real works); II and III
are improvements. A mature save can pay for each when it is offered, and it is felt (a few days of takings), but nobody
grinds for weeks after the story.

**Minimum spend** (T, U, V, W). The first formula (party × the restaurant's average check per guest × 1.05–1.15) was
wrong in practice: that average includes the Lounge and the small tables' drinks, and a big party ordered at most eight
plates, so every booked party ate about 55–65% of its minimum and every bill was the minimum — a surcharge, not a
floor. Now:
- a party of five or more orders as people do — a dish each, a drink or a dessert here and there — up to twelve on its
  ticket (three and four order as before);
- the minimum is what a party of that size and kind orders at that day's menu and prices (the ordering rules
  themselves, sampled with a seeded draw so the day's dice are not touched), times 0.88 / 0.92 / 0.94 by phase,
  rounded to $100, never below $400; fixed in the booking.

Measured (two runs, before the last small change of the factors from 0.90/0.95/1.0): every booking came and paid;
Phase I minimum ≈ $2,300–2,600 against ≈ $2,100–3,000 eaten; Phase II ≈ $2,900–3,300 against ≈ $3,300–3,700; Phase
III ≈ $3,800–4,000 against ≈ $3,700–3,800, the floor reached by 10–13 of 17–18 parties — which is why III's factor
came down from 1.0 to 0.94. The final runs are in the release report.

**Bookings by phase** (same runs): Phase I about 29% of evenings, Phase II 44–56%, Phase III about 68%; the longest run
of evenings without one is 2–3; the first comes by the second evening (guaranteed). Walk-in parties use the room on
some free evenings (1 / 3–4 / 7 over the phases' evenings).

**What the rooms add.** The Staff Room adds no takings and no places (K). The Private Dining Room's bookings add
roughly a party of 4–10 on most evenings by Phase III — about $3–4k an evening, under a tenth of the day — and two
places on the restaurant's list (AG). Neither changes the shape of the late-game economy.

### 8.2 The player's corrections of 04:06–04:26 (they replace the parts of §8 above that differ)

Filed: `rc6_spec_spaces_0406`, `second_floor_architecture_0408`, `impact_report_request_0409`,
`second_floor_overview_visual_0417`, `private_dining_artdeco_0425` (+ the photo `refs/private_dining_artdeco_mood_0425`).

- **The floor and its rooms are three scenes.** 二樓 is the floor's own view: where the rooms are — their outer walls, their
  doors, the space they take — never what is inside. Each room is its own full view, entered by its door. (The rooms
  were already their own views; what changes is the floor: the cut walls and the small copies of the rooms' insides on
  it are gone.)
- **From the floor the rooms are closed rooms**: the wall that faces you (the Private Dining Room's in its own language —
  deep green panels, brass, an arched frosted window; the Staff Room's in the floor's plaster with a frosted window),
  the end wall seen a little from the side as the column is, the walls' tops, a real door (trim, panels, frosted glass,
  lever, threshold, a mat) with its sign. The state shows only from outside: light in the frosted glass and under the
  door when someone is in there; the Private Dining Room's card on the door (已預約 / 用餐中); over its door, the same
  bubble a table shows when the table in there needs you.
- **The floor recomposed**: the Staff Room is a wall's height in front of the Private Dining Room (a passage between
  them), so the Private Dining Room's whole front shows; the open middle, the right window, the column, the stairs;
  the corner left of the stairs undecided — side-window light on the boards and a plant, no use given to it. At closing
  one of the floor stays out by the big window; the cats keep their cushion and window.
- **Navigation: Restaurant → 二樓 → a room.** The 二樓 tab is the floor, from anywhere (it no longer goes round three
  rooms); inside a room it reads 「‹ 二樓」 and takes you back; the room's door does the same; the arrow keys go over
  the top-level rooms.
- **The Private Dining Room, redone** (the brief overrides the wooden room of `refs/private_dining_room_reference`):
  contemporary Art Deco with Jill's Kitchen's warmth, from Phase I — stone floor in large slabs, an ivory stone table
  running from the door (the near end, the bottom of the view) to the window wall (its long axis the phone's height),
  deep green panelling with brass, upholstered oatmeal chairs on brass feet, a brass pendant, a walnut sideboard under
  the window, a service console, plants in brass pots. Phase II, the same room more complete: the table longer (8),
  sconces, fluting, velvet drapes, a framed print, a console with its lamp, a coat stand, glasses and flowers. Phase
  III: the table at 10, the coffered ceiling, the tiered chandelier, a wine cabinet, an arched mirror, the sideboard's
  stone top and lamp, chargers, wine glasses, candles. The places are down both sides (the game never shows a back);
  the party comes to the table's near end; the crew serve from there.

### 8.3 The player's corrections of 05:19–05:42 (they replace the parts of §8.2 above that differ)

Filed: `staff_room_muji_0519` (+ `refs/staff_room_muji_ref1–3_0519`), `second_floor_navigation_0523`,
`rc6_release_order_0532`, `testing_strategy_0542`.

- **The Staff Room, redone** (05:19; the brief overrides `refs/staff_room_stages_reference`): bright, warm, light,
  MUJI-inspired, from the three pictures — warm white walls, a very pale oak floor, a pale oak ceiling with beams,
  sheer linen over the window; the palette only warm white, ivory, oatmeal, light greige, pale oak and ash (plants
  green; small dark hardware only). Three ways to use it, never labelled: the sofa zone (a wide low oatmeal sofa on a
  pale oak plinth, two oatmeal armchairs, a long low pale oak coffee table, an ivory rug with quiet arcs, a floor lamp,
  plants) — the heart of the room, facing you; the long table under the window with its banquette and two end chairs
  (4–6); the built-ins along the far wall — five pale oak lockers with small round pulls and name cards and an open bay
  with pegs and cubbies on the left, a bench in front; on the right the kitchenette as part of the wall (warm white
  doors, an oak top, a tiled splash, two open shelves with a warm light under them, a rail of mugs, a stool at the
  counter, and the tall pale oak unit with the fridge behind its door). The door is at the near end (the bottom of the
  view), as in the Private Dining Room; a coat stand by it. Phase I is the whole room; II and III are the same room lived
  in (names on the lockers, everyone's own mug, fruit, a knit throw, a basket of throws, notes on the fridge, a row of
  outlets in the banquette; then flowers and a runner, photos on the fridge, a throw over the sofa's back, a pouf, the
  plants grown, a speaker, slippers by the door). The story traces keep their meaning in the new room (小彤's mug on
  the last hook, 阿德's towel on the left armchair, the power strip 怡君 brought on the long table, the one outlet's
  cube adapter by the counter).
- **The far wall comes down** in the Staff Room (y 168 on a phone, 110 on a short desktop screen) so the built-ins sit
  under the ticket rail and the chips, not behind them. The phone shows x ≈ 38–374 of the room (the 336 design width);
  everything that matters is inside it.
- **Standing places are marked** (fridge, coffee, lockers, pegs, window): until this round none was, so srFreeSpot never
  preferred a seat and people could be drawn "seated" at the fridge. People take seats first now.
- **A way round the furniture**: the Staff Room has several things in the way (the table, the sofa, the coffee table,
  the armchairs); a walker goes round the first one its straight line meets, by the corner whose way is clear of the
  others (`obsVia` with several boxes; one box — the Private Dining Room's table — as before).
- **二樓 is not an everyday tab** (05:23). The everyday tabs are the rooms: 店門口・主廳・側廳・休息室・包廂・Lounge・廚房
  (seven fit a phone at a tighter padding). The tab you are in reads the room's whole name — 員工休息室, 私人包廂 — so
  inside a room the location is the room, never 二樓. A room's door goes down the stairs to the side room (as the
  kitchen's door goes to the dining room); never to the floor's view.
- **The open-floor period** (rc5, before any room): the same rule — no 二樓 tab. The player's 05:23 lists the open-floor
  period among the times the floor is worth seeing; it is seen in its stories (the rc5 and rc6 beats), from 店舖工程
  (看看整層, any day), and — a decision taken here, since a daily tab is exactly what 05:23 removes — not as a tab.
- **The floor is shown when it changes**: (1) the stories that happen up there (R.upView, as rc5 built them; 二樓 is a
  tab, lit, only then); (2) 店舖工程 › 二樓 › 看看整層 — the floor as it is now, the rooms closed (walls, doors, signs,
  nothing of the inside, nobody in them), the works if any, and — once a room has been bought — a chalked 「？」 on the
  corner nobody has decided about (two corner marks, a hand-drawn question mark; nothing named, nothing promised);
  while looking, the tabs are the floor and its rooms only; (3) 去看看 after buying a room's Phase I — the works that
  evening; (4) the morning a room is finished, 0.45 s after the prep screen: the floor as it was last night (the works),
  the walls coming up from the floor, the door, the sign last; a card (完工 · 進去看看 / 回到開店準備); inside, the room's
  own view the first time (morning light, nobody yet, a line on the banner); then back to the day. Once per room
  (`rv` in the save); never during a service; if something else is open on the prep screen it waits for it. Phases II
  and III change the inside only, so they have no floor reveal (their purchase card and 去看看 show the room).
- **Order of work** (05:32): rc6 is released on its own, with all of the above; nothing of P5 in it; P5 (rc7) starts
  after the release, its URL and zips are confirmed.
- **Testing** (05:42): targeted tests after each change (risk-based), the player's saves as checkpoints
  (`tests/saves/README.md`), the full regression at the release gate; `docs/RELEASE_CHECKLIST.md` §5.

### 8.4 The player's corrections of 06:36–12:16 (they replace the parts of §8.3 above that differ)

Filed: `second_floor_three_uses_0636`, `staff_room_recreation_pdr_polish_0643`, `pdr_spatial_polish_0657`,
`npc_wardrobe_0705`, `customer_identity_linking_0709`, `npc_wardrobe_references_0812`, `second_floor_plan_0837`,
`player_messages_0933_1216`, `second_floor_prerequisite_1025`, `story_presentation_1032` (+ the audit).

- **二樓 is an everyday tab again** (06:36, replacing 05:23): the simple floor with its closed rooms, the rooms' doors back
  out onto it; 店舖工程 › 二樓 has the floor's plan for good (architecture only, 「？」 where undecided, 「今天完工」, full
  screen on a tap). The reveal walk the morning a room is finished stays.
- **The floor as the player drew it** (08:37): the Private Dining Room top-left over the street windows, the Staff Room
  directly below it to the back wall, the hall an L down the right, both doors onto the hall where the rooms meet; the
  stairs across the bottom-right corner at half the size (09:14); no column.
- **The Staff Room's recreation** (06:43): a pale oak pool table from II, a massage chair and books from III; at closing
  now and then a frame, someone dozing (runtime only). **The Private Dining Room's walkways** (06:57): only the stone
  sideboard serves.
- **The guests** (07:05, 08:12): a wardrobe, then silhouette and layering, from a hash of the day; Q++ kept (no white
  top on a guest — white is the staff's, the waiters' too since 10:15). **Who is where** (07:09).
- **The Second Floor's story begins with the finished Lounge** (10:25): `V24_ERAS.up.open = loungeDoneDay()` (+2 days),
  no longer `prev:'wall'`; 《那面牆》 and the floor are independent chains that share only the day's story budget.
- **Authored beats hold the restaurant** (10:32; the four kinds chosen at 11:06: Sophie and Mia, the leak case, what
  brings the Second Floor about and its rooms, the love stories): the restaurant stops, one line per tap, the service
  resumes exactly; `SH_HOLD`, `shStart`, the story context `SCX`.
- **More to spend on** (10:21, 10:40, 11:49): four dream works, four seasonal sets, three contracts, a wine course, the
  Lounge's people a level a day; wine research priced like a dish's ($2,500–$8,000) with pairings that bring glasses
  and guests. 買下整棟 waits for the player.
- **The day's one major slot is fair** (12:16): a major beat due when the slot is taken counts a missed day; the next
  day the slot is kept for the beat that has waited longest and can happen today (one day; still one major a day; no
  new cooldown). 晴 and 阿拓 count as there only when they came in; 阿拓 takes one day off after 「多的。」; the slow burn
  a little quicker.

## 9. P5 — the other Staff Lives arcs (rc7; plan, 2026-10-02 14:30)

Started after v2.4-rc6 was published (Version 40) and its page and zips were checked. Sources:
- `staff_lives_brief_2026-10-01.txt`, the canonical brief;
- the two outside-cast messages and their pictures. They win where they differ from the brief: 宇翔's first lines, 老林's first lines and his milestone;
- `canon_change_xiuqin_2026-10-01.txt`: 秀琴阿姨 is 國雄's wife and 怡君's mother; 阿珠姐 keeps no family story;
- the PDR brief §15–16 and the rc6 spec's list of later uses ("員工替家人訂位");
- the player's 05:32 list for rc7: 國雄, 宇翔, 珊珊, 老林, Kevin, 小彤 and her parents, Kai, the crossovers, 怡君's boyfriend, a staff family booking the Private Dining Room.

Also read with it: the player's 12:17 and 12:24 (「故事進展真的太慢」, 「每天…還沒有任何故事」). The first meetings must come soon after updating, a few days apart. Each arc must move at a pace the player can see.

### 9.1 Canon found in the code (rc6)

**Staff and saves**
- The staff have names, roles, portraits and sprites, and nothing else: no ages, no families, no lives outside.
- Tenure: `TENURE_CANON` marks 阿珠姐, 秀琴阿姨 and 阿德師傅 as 資深, and 小彤 as 較新 (熟手 after 45 counted days). Everyone else uses the counted days.
- The player's Day 71 crew includes every staff member these arcs need, all legacy: 阿德師傅, Marco, Hugo, 秀琴阿姨, Kai, Nina and 小彤. Momo and 小威 are new (Day 63).
- There are no weekdays anywhere: the 週末 event is a random draw, not a calendar.

**Already done in rc4–rc6, kept as is**
- 怡君: her arc, her wait at closing (`sp_wait`), the Private Dining Room's 「有比較安靜的嗎？」 and its payoff.
- The Staff Room traces:
  - 小彤's 「坐啊。」 on its first evening (`srFirstStart` picks her), then her mug and the stool;
  - 阿德's armchair;
  - Hugo and the fridge;
  - 阿珠姐's 「插座不夠。」/「我就說吧。」;
  - 秀琴阿姨's food from home;
  - Kai's racket bag on some evenings (`kaiBagToday`; an object, no story).
- 《第二層左邊》 stays 阿珠姐's.
- The new hire's first shift (`first_shift`) asks waiters and cooks only. Its cleaner version comes now, with 小彤's arc.

### 9.2 Conflicts and adaptations

| Brief | Decision |
|---|---|
| 《星期三》: Kai asks for no Wednesday evenings, but the game has no weekdays | His request fixes the week. The day after he asks is a Tuesday, so every seventh day from the day after that is "星期三" for him: he is off that day, with a morning note. No weekday appears anywhere else |
| 「下面第二格」 needs a new employee, and the crew is full in a mature save | It waits for a real new hire: the Private Dining Room's +1/+1, or anyone hired after a departure. It is very late by design. The setup comes early: 小彤 asks where the big rubbish bags are, and 秀琴阿姨 answers 「後面櫃子，下面第二格。」 Later 小彤 gives a new hire the same answer |
| Cooks never leave the kitchen during a service (阿德, Marco, Hugo) | Mid-service, a visitor comes to the kitchen door, one step inside, and the cook comes to the door. At closing a cook walks out of the kitchen door and through the dining room to whoever is waiting. Nobody cooks less |
| 「你進去等我」 and the rest need the Staff Room, which the player's save does not have yet | These beats wait for the room. Until then the same people wait by the door, standing, which is the brief's own Staff Room evidence (`sp_wait`, once the floor's story has begun) |
| 怡君's boyfriend: 阿珠姐's lines in the brief | 秀琴阿姨's, by the canon change |
| 國雄 must not act as if he had never heard of 怡君's flat | No line of his contradicts it. Once the wall is settled, one pickup has 國雄：「怡君說牆弄好了。」 秀琴：「我知道，我去看過了。」 |
| The story hold (11:06): only Sophie and Mia, the leak case, the second floor's triggers and the love stories hold | No P5 beat holds the restaurant. A beat at closing hides the 收店 pill for its few seconds, so the closing cannot be skipped in the middle of it. Nothing else waits |

### 9.3 Architecture (on the arbiter, nothing parallel)

- **The outside cast** are `NAMED` entries with `story:1`. Each has a portrait card and two expressions from the player's sheets, and a matching sprite. They are never in a random pool, visit at most once a day, are not staff, and draw no wage.
- **Three ways to be there:**
  1. **As a guest**: sits, orders, eats, pays, through the schedule (`V24_WANTS`).
  2. **Waiting for someone**: walks in near the end of the service, waits by the door, then leaves with their person at closing. Waiting means standing at first, on a chair by the door on the rainy evening Jill asks, or in the Staff Room once someone has said so.
  3. **At the kitchen door**: walks in, steps into the kitchen doorway, and the cook comes to the door when his hands are free.

  A visitor who is not a guest is a sprite of their own (`R.p5v`), drawn in whatever room they are in. They are never seated at a guest's table and never take a guest's place.
- **Their person is really there.** A visitor comes only when their staff member is on the crew and in today. That includes 國雄's evening alone (秀琴 is working) and excludes 老林's day without 阿德: he comes for the restaurant itself, which is the point of that beat.
  - Let the staff member go, and their outside person stops coming. 老林 is the exception once he is 林叔.
  - Hire them back and their arc goes on: facts are kept by beat, not by crew id.
- **The p5 lane.** One P5 beat a day, beside the other lanes: major 1, minor 2, v24 1. It never takes the day's major slot. The later, quieter visits are ambient and have their own cooldowns.
- **Pacing.**
  - Each arc opens on its own day: the first day played with rc7, plus 1–8 days, in a fixed order (§9.4). In a new game the arcs open no earlier than Day 14, and only once their staff member has worked 7 days.
  - Nothing happens on the first day played (no load-time dump).
  - Inside an arc, each beat waits only its own gap in days, and for the visits or tenure its fiction needs.
  - When a beat is due, the schedule brings its visitor that day with a high chance, using its own hash coin; the day's random stream is untouched.
- **Knowledge.**
  - An outside person is introduced by a fact, written the moment the first beat happens.
  - The coworkers in the room then are written as having met them (`relSet('s:'+id, 'n:'+name, 'met')`).
  - A line that names someone checks those facts; nobody knows anyone before they have met.
- **Journal.** One line per arc on 人物／關係支線, holding the meaningful beats only. Ambient visits and the life-progress mentions are not in the count.

### 9.4 The beats

The order in which arcs open after updating (days after the first day played):
1. 小彤 asks;
2. 國雄;
3. Kevin;
4. 珊珊;
5. Kai;
6. 宇翔;
7. 老林;
8. 小彤's parents.

Gaps are in days after the beat before.

**小彤 — 《下面第二格》**

| # | Beat | How | Needs | Gap |
|---|---|---|---|---|
| T1 | 「阿姨，大垃圾袋放哪？」「後面櫃子，下面第二格。」 | During the service; both cleaners. Without 秀琴阿姨, the senior cleaner or Jill answers. In a new game, at her first shift | 小彤 較新 | — |
| T2 | 《你們怎麼來了》: 「你們怎麼來了！」「吃飯啊。」 Her mother: 「妳去忙，不用管我們。」 At the bill: Jill 「小彤很認真喔。」 Mother 「真的？她在家都……」 小彤 「媽！」 | The parents as guests. 小彤 walks over, then glances at their table while she works | 小彤 in, 7+ days on the crew | 3 |
| T3 | 《想很久了》: 「妳換鞋了？」「嗯。想很久了。」 | At the staff meal, before opening | 小彤 30+ counted days, or 熟手 | 6 |
| T4 | 「坐啊。」 | The Staff Room's first evening (rc6) | — | — |
| T5 | 《家人訂位》: 小彤 books the Private Dining Room for her parents' anniversary. 「這是妳訂的？」「嗯。」「很貴吧？」「員工價。」 The bill says 員工家屬 八折 | A story booking (`pdBook`) and the news card | Room built, T3 | 10 |
| T6 | 《第二格》: a new hire asks; 小彤 answers 「下面第二格。」 If she is in, 秀琴阿姨 is there and says nothing | The new hire's first shifts | 小彤 熟手, T1, a hire in their first 3 days | — |

**秀琴阿姨 & 國雄 — 《來接妳》**

| # | Beat | How | Needs | Gap |
|---|---|---|---|---|
| G1 | 《來接妳》: 「先生，我們打烊了喔。」「我等人。」 秀琴 「我先生。」 「好了沒？」「椅子還沒收。」「喔。」 | Waiting by the door at closing | 秀琴阿姨 in | — |
| G2 | 《下雨》: 「下雨耶，進來坐。」「不用，我站這裡就好。」「坐啦。」 He sits on a chair by the door | Waiting, a rainy evening | Rain, no Staff Room | 3 |
| G3 | 「你去裡面等她。」 He waits upstairs | Waiting | The Staff Room, 2+ days old | 2 |
| G4 | His own days: 「你今天又去爬山？」「跟老張他們。」 (and, once the wall is settled, 「怡君說牆弄好了。」) | A pickup, ambient | 4+ pickups | 6 |
| G5 | 《今天不想煮》: 「你不是跟朋友出去？」「回來了。」「那你來幹嘛？」「吃飯。」「家裡不能吃？」「今天不想煮。」 | 國雄 as a guest; 秀琴 walks over | G4 | 12 |

**Marco & Kevin — 《以前一起做事的人》**

| # | Beat | How | Needs | Gap |
|---|---|---|---|---|
| K1 | Kevin orders the hardest dish on the station Marco is cooking. Marco at the ticket: 「……白痴。」 At the bill: 「跟 Marco 說，太慢了。」 | Kevin as a guest | Marco in | — |
| K2 | 「走，喝一杯。」「明天早班。」「你哪次不是早班。」「……一杯。」 Jill 「你們認識很久了？」 Kevin 「以前在飯店，他在我隔壁站。」 Marco 「他切菜很慢。」 Kevin 「是你太快。」 | Waiting at closing; Marco walks out of the kitchen | Kevin 2+ visits | 5 |
| K3 | 《待滿久了》: 「你這裡待滿久了。」「嗯。」「不走了？」「目前沒有。」 | Waiting at closing | Kevin 3+ visits; Marco long there (legacy and 20+ days since P5 began, or 60+ counted days) | 10 |

Between the beats, Kevin comes now and then for dinner, and sometimes orders the same dish again.

**Nina & 珊珊 — 《等妳》**

| # | Beat | How | Needs | Gap |
|---|---|---|---|---|
| N1 | 《等妳》: 「妳朋友？」「高中同學。」「她以前很安靜。」「誰？」「妳可以走了。」 | Waiting at closing | Nina in | — |
| N2 | Nina at 珊珊's table: 「老樣子？」「嗯。」 A note: the two of them hardly speak. A coworker who met her at N1: 「Nina 在那桌好安靜。」 「高中同學。」 | 珊珊 as a guest; Nina walks over | — | 4 |
| N3 | 「上去等吧，樓上有位子。」「可以嗎？」 Nina 「可以啦。」 | Waiting | The Staff Room | 2 |
| N4 | 「Nina，珊珊來了。」 A coworker says her name for the first time | Waiting | 4+ visits; a coworker who has seen her twice | 6 |

**Hugo & 宇翔 — 《我弟》**

| # | Beat | How | Needs | Gap |
|---|---|---|---|---|
| H1 | 《我弟》: 「哥。」「你怎麼來了？」「拿東西給你。」「放著就好。」 A cook beside him: 「你弟？」「嗯。」 | The kitchen door | Hugo in | — |
| H2 | Hugo at the ticket: 「那桌算我的。」 Jill 「哪桌？」 「我弟。」 At the bill: 「你哥付了。」「……喔。」 | 宇翔 as a guest | — | 4 |
| H3 | 「你進去等我。」「可以喔？」「可以。」 | The kitchen door, then he goes up and waits | The Staff Room | 2 |
| H4 | His life, ambient, days apart: 「他實習找到了。」 → 「他下禮拜畢業。」 → 宇翔 in a shirt: 「哥，我第一天上班。」「嗯。吃了沒？」 | The last of the three is a beat | H2 | 12 / 15 / 15 |

**阿德師傅 & 老林 — 《等一下》**

| # | Beat | How | Needs | Gap |
|---|---|---|---|---|
| L1 | 《等一下》: 「阿德還有一下。」「沒事，我等。」 | Waiting at closing; 阿德 walks out | 阿德 in | — |
| L2 | 「明天要不要去？」「幾點？」「四點。」「太早了。」「魚又不等你。」「……三點半出門。」 A coworker: 「阿德師傅今天話好多。」 | Waiting at closing | — | 4 |
| L3 | 「林叔，又來等阿德師傅？」「欸，叫得很順喔。」 From then on the crew call him 林叔 | Waiting, or as a guest | 4+ visits | 5 |
| L4 | 《今天阿德沒上班》: 「林叔今天沒點魚？」「你們阿德今天又沒上班。」 | 阿德's day off (a morning note), 老林 as a guest | L3, 6+ visits | 6 |

He orders the fish when 阿德 is in. After L4 he comes now and then on his own, even if 阿德 has left the restaurant.

**Kai — 《星期三》**

| # | Beat | How | Needs | Gap |
|---|---|---|---|---|
| A1 | 《星期三》: 「Jill，星期三晚上可以不要排我嗎？」「怎麼了？」「打羽球。固定的。」「好啊。」 | At the staff meal. From then on his Wednesdays are off | Kai in | — |
| A2 | 《四個人》: 「你們小聲一點。」「服務態度很差欸。」 At the bill: 「星期三見。」「嗯。」 | Four friends as guests, one with a racket bag | Not his Wednesday | 3 |
| A3 | The result, ambient, the day after some Wednesdays: 「昨天贏了沒？」「贏了。」 or 「……不要問。」 | The staff meal | A1 | — |

**怡君, later**

| # | Beat | How | Needs |
|---|---|---|---|
| Y7 | Nina recognizes her: 「秀琴阿姨的女兒？」「妳怎麼知道？」「妳們笑起來一樣。」 | 怡君 as a guest; Nina serves | Nina on the crew for 2 of 怡君's visits |
| Y8 | Her boyfriend: 「那是怡君男朋友？」「嗯。」「妳看過了？」「看過。」「怎麼樣？」「吃飯。」 | 怡君 and him as guests | Y7; the wall settled 14+ days ago (or her key 30+ days, if the wall is dormant) |
| — | Nina 「怡君她們在裡面。」 秀琴 「嗯。」 (PDR brief §15) | Ambient, once | 怡君's party in the Private Dining Room |

**Crossovers** (once each, sparse):
- 國雄 and 老林 waiting on the same evening: 「你也在等人？」「等我太太。」「我等阿德。」「你釣魚嗎？」「不釣。」「可以學。」
- 小彤 and 宇翔: 「你是 Hugo 的弟弟？」「嗯。」「不太像。」「大家都這樣說。」

### 9.5 Deferred (not in rc7)

- 《休息一下》, the Staff Room's later authored photo. The brief says not to make it yet.
- 阿珠姐's own outside life. The canon change says not to invent a replacement family.
- 小彤's 第二格 in a save that never hires again: the beat simply waits.

### 9.6 Migration and QA

**Migration**
- Old saves start every P5 arc from nothing; nothing is inferred.
- Nothing happens on the first day played. The arcs open over the following eight days, one P5 beat a day at most.

**QA**
- Tests: migration; progression; spacing; presence (nobody comes for someone who is not in); prerequisites; no premature knowledge; letting go and hiring back; dialogue repetition.
- Simulations: 30 and 60 days from the player's Day 71 save, and a new game.
- Phone screenshots of every first meeting.
