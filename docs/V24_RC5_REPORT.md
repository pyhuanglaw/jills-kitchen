# JILL'S KITCHEN v2.4 rc5 — release report (2026-10-01 → 02)

**Legend**
- **I** — implemented: the code is in the repo.
- **T** — tested: an automated test, a seeded simulation, or a screenshot from real play inspected in headless
  Chromium at phone size (390×844).
- **O** — observed by the player on the phone. Nothing in this report is O yet; §12 is what to look at.

**Branch and builds**
- Branch: `master`. Tag: `v2.4-rc5`.
- Published to the player's usual URL, https://claude.ai/artifact/2vhURujrtCpQ1P5jnSsjps (saves live there).

**What the player asked for in this round (filed verbatim, `docs/v24/`)**
- 17:57 「繼續吧」: P2, the Second Floor (the plan: `docs/v24/AUDIT_AND_PLAN.md` §7).
- 17:48 the signature dessert's −/＋ jumps up beside its info line (`next/dessert_stepper_jumps_2026-10-01.txt`, for this version).
- 18:32 「Evan是男的吧」 and 「一堆npc一直重複是為了Jill招牌菜來的」 (`next/evan_and_sig_line_2026-10-01.txt` + the screenshot).
- 19:07–19:16 the staff pool architecture, the Lounge's fixed roster, 許葳's sheet, servers and the kitchen shared
  (`staff_pools_1907_2026-10-01.txt`, `assets/portraits/src/sheet_xuwei_v24.jpg`).
- 19:19 the player's own Day 61 save (`tests/saves/player_day61.json`) — used for the migration tests and the pacing.

## 1. Commits since v2.4-rc4

| Commit | What |
|---|---|
| acd2bb5 | S2: the second floor as a room (vacant and taken), the stair door in the side room, the street's 2F windows; P2 plan in AUDIT_AND_PLAN §7 |
| 63bccc9 | S3: the Second Floor arc; the two staff pools and the Lounge roster; 許葳; staff sprites from their portraits; the signature line |
| b3369b7 | S4: the 樓上 chapter, the manual, the one-time note; the signature steppers; the tests |
| (this) | Small fixes from the evidence pass, the single-file build, this report and the evidence |

## 2. Release content audit

| FEATURE / FIX | STATUS | IN THIS RELEASE? | WHY / NOTES |
|---|---|---|---|
| P2 the Second Floor: the room (vacant / taken), stairs, the street's windows | DONE | Yes | §4, §5 |
| P2 the arc: the regular's question, the crew, the landlord, the missing cats, the pressure, the reminder, the call, the project, the open floor | DONE | Yes | §3, measured §6 |
| 《那面牆》's callback 「先看漏水。」 | DONE | Yes | Only if the wall happened |
| Two staff pools (restaurant / Lounge), capacities never added together; the Lounge's fixed roster of five | DONE | Yes | §7 |
| 許葳 (portrait, four expressions, sprite, Lounge cleaner) | DONE | Yes | §7 |
| Staff sprites match their portraits (Evan was drawn with long hair; every named employee's hair came from a hash of the id) | FIXED | Yes | §8 |
| 「我是專程為了 Jill 的招牌菜來的！」 said by every signature guest | FIXED | Yes | §8 |
| The signature steppers jumping beside the info line | FIXED | Yes | §8 |
| P3 / P4 the Staff Room, the Private Dining Room | NOT STARTED | No | Next. The crew's space moments (`sp_*`) are recorded as their evidence |
| P5 the outside cast and their long arcs (Kevin, 珊珊, 宇翔, 小彤 + parents, 老林, 國雄) | NOT STARTED | No | Later (§9 F) |

## 3. The Second Floor arc (second_floor_and_long_arcs §3–§23; implementation pass I)

**Era.** `up` opens two days after 《那面牆》 settles (as rc4 planned), and its first beat waits for the stairs and a
restaurant that has grown into them: the side room bought, the restaurant at its full size (level 5, JILL), a crew of
five or more (`upCan`). Nothing in it fires on the first day a save plays this version.

| # | Beat | Lane | Who | Waits for | Journal |
|---|---|---|---|---|---|
| U1 | 「樓上也是你們的？」「不是，房東的。」「一直空著？」「好像是。」 | v24 | 陳伯伯 (a regular who walks past every day; else 小林, Leo) | the era | none (§4: building information) |
| U2 | 「樓上真的一直都空著喔？」「嗯。」「上面多大？」「不知道。」「妳沒上去過？」「沒有啊。」 (one person: 「房東還沒租出去？」「好像還沒。」) | v24, at closing | two of the crew who are here (Nina first; a cook from the kitchen) | U1 + 1 day | none |
| U3 | The landlord's afternoon: the fire inspection is coming, he goes up; 「我可以一起上去嗎？」; 「地板是好的，窗戶也是好的。」; he locks the door on the way out. Words only — the floor is not shown | major, start of the day | Jill, the landlord | U2 + 2 days | week timeline; 樓上 (once it exists) |
| U4 | The missing cats (§4 below) | major (claimed at the start of the day) | the cats, Jill, the crew who are really here | U3 + 3 days ("several days") | week timeline (written once they are found); 樓上 |
| — | Customer pressure, one a day, different people and different needs: 「妳們現在人這麼多，沒想過樓上？」「樓上又不是我的。」「租啊。」「你講得很簡單。」 (小林, a busy night) / 「今天又滿了？」「嗯。」「樓上還空著？」「還在。」 (Leo, seated after a wait) / 「妳這間越來越不像以前那麼小了。」「有嗎？」「有啊。」 (王太太) / a family wanting somewhere quieter when the side room is full too | v24 / ambient | different regulars | U4 + 2 (the night is given room) | none |
| — | Crew pressure, one every other day: 《又在找位置》 at the staff meal, said by someone eating standing up (「我們是不是每次都在找地方坐？」「嗯。」); 《箱子》 (「你幹嘛坐那裡？」「這裡可以坐。」「……那是箱子。」); 《東西放哪》 (「這裡早晚會找不到東西。」) | ambient | the people in them | the era | none |
| U5 | 「妳不是看過樓上？」「看過。」「很小？」「……不小。」 (a veteran cook who was not upstairs that night) or 「樓上不是還空著？」「那是房東的。」「我知道啊。」 | v24, closing | one of the crew | U4 + 2, two kinds of crew pressure, two kinds of customer pressure | none |
| U6 | At closing Jill walks to the stair door and stands there; she calls: 「……樓上現在還空著嗎？」「妳真的要租樓上？」「嗯。」「下面不夠用了？」 (she looks back at the restaurant) 「開始有一點。」「整層？」「整層。」 → the project is offered (開始規劃 / 之後再說, as the Lounge was) | major, closing | Jill, the landlord | U5 + 2, and §19's evidence: the question, the inspection, the night, the pressure, a full-size restaurant, $120,000 in the till | week timeline; 樓上 |
| — | 「先看漏水。」 (Mia, after looking up at the ceiling) — Sophie laughs — 秀琴阿姨 「真的，先看。」 — 王先生, only if he is at a table near them: 「……這次跟我沒關係。」 | ambient | Sophie, Mia, 秀琴阿姨 | U6 + 1, until a week after the lease; only if the wall happened | none |
| U7 | 店舖工程 › 二樓（整層） $350,000: basic works (cleaning, floor and walls, power, light, air, the stair rail). The whole floor, no partitions; not a dining room, no seats, no staff places | the player | — | U6 | 樓上 「整層。」 |
| — | The open floor: the furniture comes over the week (the table and odd chairs the next day; the cabinet and coat stand; the lamp and the cats' cushion; the stool and the scratching board), traces after (a bag, a cup, a charger, a coat); one line the second day (「我包包可以放樓上嗎？」「放啊。」); cats go up now and then, one at a time; 柔柔 back at her window sometimes; once, if someone who went up that night sees 柔柔 and 小齁 go up together: 「妳們兩個比我們早用。」「不要提醒我。」 | ambient | — | the lease | none |

**The story page** gets a 餐廳故事 chapter, 「樓上」, only once the night has happened: 房東的二樓 · 柔柔和小齁不見的那一晚
· 「……樓上現在還空著嗎？」 · 「整層。」 (the cats' names as the player has them). No beat says what the floor will become.

## 4. The night of the missing cats (§9–§16, §43; implementation pass I4)

- **The door (I, T).** The day's major is the night's: at the start of the service, 「下午，房東帶冷氣師傅上樓看了一下冷氣。」
  and the landlord, 「好了。門我帶上了。」 — so the door was opened that very day, and shut; three days earlier he locked
  it after the inspection. The door looks shut until about 82% of the service; then it stands a hand open and the
  stairwell light lies on the side room's floor (`u4_side_door_closed.png`, `u4_side_door_ajar.png`).
- **How long (I, T).** 柔柔 goes at 84% of the service (when she is free on the floor: across the dining room to the side
  arch, a moment at the stair door, up), 小齁 after her from 88%. Closing is 21:30-ish; the longest they can be gone is
  about an hour of the game's clock. If either is not on the floor by then (a perch, the sofa), she is up when the
  closing starts — never days.
- **Who (I, T).** At closing the routine stops: the 「結束今天」 pill is hidden and the closing clock waits. The search uses
  only the crew who are here today (a server or a cleaner on the floor; cooks answer from the kitchen; a bartender
  from the Lounge if it is open) — tested by sending Nina home for the day: she is never in it. Someone notices
  (「柔柔呢？」「剛剛不是還在？」「小齁也不在。」); everyone spreads out (Jill to the cat trees, one to the side room, one to the
  Lounge, the rest round the dining room); the other cats are accounted for from where they really are (「包包在這。」,
  「樾樾呢？」「這裡。」); the cook: 「廚房沒有。」 The one in the side room finds the door: 「這個怎麼開著？」 — the view goes
  there; Jill: 「……柔柔？」. Jill and up to two of the crew go up.
- **The floor (I, T).** The first real view of it, at night: dark but for the stairwell and the street through the big
  windows; a second later someone finds the switch. 柔柔 is sitting at the window; 小齁 has been nosing round the
  landlord's boxes and comes to Jill first. 「妳們兩個。」 — then, only then, 「……這裡滿大的欸。」「嗯。」 (and with a
  second person, 「比我想的大。」「先把貓帶下去。」). Down they go, the cats first; the door is shut and latched
  (「扣好了。」); the 二樓 tab disappears again; the closing goes on. No unlock, no project, no "maybe".
- **Cut short (I, T).** If the day ends in the middle of it, the cats are home and the night is not counted; it can come
  another day.
- **Cats (I, T).** 柔柔 and 小齁 by their canon looks (the game's own cats, not the reference picture's), by the names the
  player gave them.

## 5. The space (§24, implementation pass I, J; the player's two reference pictures)

- **Architecture (I, T).** The front view of the reference: the back wall with two big window rows and the pilaster
  between them, the air conditioner, two pendant lamps; a structural column in the middle; the stair opening with its
  railing in the lower right — the far end of the well is the deep end (the railing guards it), the way on and off is at
  the near left where the steps meet the floor. Plank floor.
- **Vacant (the landlord's):** dust, a plant, boxes and a step ladder, a folding table and two folding chairs. Dark at
  night until a lamp is on (`u4_up_dark.png` / `u4_up_found.png`).
- **Taken:** clean, warm, two boxes left from the works; the furniture comes up over the week; no walls.
  `UP_ZONES` (staff room left, private dining along the windows, the stairs, an undecided corner, the middle kept clear)
  is data only — nothing is built on it in P2.
- **Navigation.** The stair door at the side room's near edge; people and cats walk side ↔ up through it; the 二樓 tab
  exists once the floor is Jill's (and during the night). The street shows the second floor above the sign: dark while
  it is the landlord's, warm once it is hers.

## 6. Pacing (T: `tools/sims/v24_pacing.py`, lazy bot, three seeds × two saves, 60 days; `docs/evidence/v24_rc5/sims/`)

| Save | Wall settled | Era opens | U1 | U3 | U4 (night) | U5 | U6 (call) | Bought (sim buys at once) |
|---|---|---|---|---|---|---|---|---|
| Day 52 (seed 7000 / 7100 / 7200) | 83 / 81 / 80 | 85 / 83 / 82 | 85 / 84 / 84 | 90 / 88 / 87 | 93 / 91 / 90 | 97 / 95 / 93 | 99 / 97 / 95 | same day |
| The player's Day 61 (seed 7000 / 7100 / 7200) | 82 / 81 / 81 | 84 / 83 / 83 | 85 / 83 / 85 | 88 / 88 / 88 | 91 / 91 / 91 | 94 / 94 / 94 | 96 / 96 / 96 | same day |

The player's window for the first Second Floor beats was "approximately Day 78–86": U1 comes on Day 83–85. From the
era opening to the call is 13–14 days; the night is 6–8 days after the first question. One major beat a day in every
run, no page errors. The crew's moments start with the era (Day 82–87) and come every other day; the customer moments
two days after the night, one a day.

A fresh game (`tools/sims/v24_fresh.py --plan grow`, 120 days, two seeds, the perfect bot buying whatever it can
afford): the era opens with the wall (Day 48 / 52), the crew's moments start, and the first beat waits for the
restaurant's full size — the bot's restaurant reached level 5 on Day 117 in one run (U1 117, U2 118, U3 120) and never
in the other. The bot's economy is not a player's (it overhires and does not grow its menu); what the run shows is the
gate holding, not the day a person would get there.

## 7. Two staff lists (the player, 19:07–19:16) and 許葳

- **Pools (I, T).** Every employee has `pool` = `restaurant` | `lounge` (old saves: by the Lounge roster's names and roles,
  and any bartender, → `lounge`; everyone else → `restaurant`). Role is a separate field: 安安 is a Lounge waiter, 許葳 a
  Lounge cleaner, 阿拓 a Lounge cook.
- **Capacities (I, T).** `restaurantCap()` = the level + 後場整理區 + 側廳 + 廚房擴建 + 廚房二期 (2 each). `loungeCap()` = the
  roster names the Lounge's works have opened. `crewCap()` (which added the Lounge's +2 and +2 into one number) is
  gone. Tested: 廚房二期 adds two restaurant places and no Lounge place; Lounge III and the second floor add none;
  Lounge I alone gives two Lounge places and the restaurant is unchanged.
- **The Lounge roster (I, T).** Lounge I: Evan 林奕文 (首席調酒師), 沈晴 (調酒師). Lounge II: 阿拓 黃柘 (Bar Food 料理員 — in
  the one kitchen, as in v2.3; the player, 19:11: 「不管你要叫什麼只會找到他們」), 安安 (Lounge 外場), 許葳 (Lounge 清潔). The
  staff page has 「Lounge 名單」: these five by name, with their portraits and jobs, 聘請 or 在店裡; all five = 「Lounge 的人
  都到齊了。」 Nobody else is ever offered; a generic bartender cannot be hired. The restaurant's recruitment shows 廚師 /
  服務生 / 清潔員 only.
- **Work (I, T).** Unchanged and cross-zone (the player, 19:14): servers are shared both ways (a restaurant server on the
  Lounge floor stays restaurant staff; 安安 seats and takes orders anywhere); one kitchen (阿拓 cooks there, quicker on bar
  food; the Lounge's food comes from it); the bartenders keep to the bar. 許葳 starts her evening in the Lounge and clears
  it first, then wherever she is needed.
- **Migration (I, T).** Nobody is fired. A save that used the old shared number can hold more restaurant people than the
  restaurant's own places (tested: 13 of 12): the page says why, everyone stays, the restaurant hires again below its
  number; the Lounge still hires its own. 安安 and 阿拓 hired the old way (as a plain waiter / chef) are the Lounge's.
  The player's Day 61 save: 餐廳員工 12/12, Lounge 員工 2/5 (阿拓, 安安, 許葳 can be hired now).
- **許葳 (I, T).** Her portrait and the four expressions from the player's sheet (工作中, 淺笑, 覺得好笑, 已經處理好了), her
  sprite (dark hair tied low, the dark grey work shirt, a black waist apron), and one moment, once, at a closing a few
  days in: 「Lounge 那幾桌——」 「收好了。」 (the "already done" face).
- **晴 × 阿拓 (T).** Untouched and easier to reach: 阿拓 no longer needs a free restaurant place. In the evidence run the
  line's first beat (「炸雞好了沒？」) came the first evening after he was hired.
- **One-time note** for a save that was already going: the two lists, the Lounge's people, where they work.

## 8. Fixes

- **Staff sprites (I, T).** Evan had hair style 2 (Sophie's long hair). Every named employee's style came from a hash of
  the id — a man could get long hair. All twenty-four named staff now take skin, hair colour, hair, glasses, a
  headscarf from their portraits (`STAFF_FACE`, `LOUNGE_LOOKS`); the role still decides the uniform. Before/after lineup
  checked by eye; Evan in the Lounge shot.
- **The signature line (I, T).** Seven ways of saying it with the dish's name (『Jill's 檸檬奶油干貝』…), at most one every two
  and a half minutes of the service (so one or two an evening), never the same sentence twice running, never a named
  guest (周董 is himself). Picked by a hash, so the evening's random stream is where it was. Tested with fourteen
  signature guests in a row.
- **The steppers (I, T).** The −/＋ of both signature cards is a block of its own under the info line. The test checks
  the position at 9, 16 and 100 份 and the layout itself (it fails on rc4's CSS: on the player's phone font the
  dessert's line was short enough for the stepper to sit beside it).

## 8a. Manual audit (docs/RELEASE_CHECKLIST.md §2)

- **Checked:** every section (開店與料理, 開店前, Jill 與員工, 招待與熟客, 商店, 招牌菜與招牌甜點, Lounge, 五隻店貓, 料理研發,
  餐廳日誌) against the final feature set.
- **Changed:** 開店與料理 › 房間 (二樓 once it is the restaurant's; the stair door in the side room); Jill 與員工 (the summary:
  the Lounge list at the bottom of the page) › 員工 (two lists, places counted apart; the Lounge's five by name; servers
  shared, one kitchen, bartenders at the bar) › 調酒師 (Evan and 沈晴, from the Lounge list); 商店 › 店舖工程 (二樓（整層）
  when the story gets there: not a dining room, no seats, no staff places); Lounge › Lounge I／II／III (II adds 阿拓, 安安,
  許葳 to the list, instead of 「第二位調酒師」); 五隻店貓 › 牠們不出門 (once the floor is the restaurant's, one goes up now
  and then and comes down by herself).
- **Obsolete wording removed:** 「人數上限跟擴建、後場整理區、側廳、廚房擴建、廚房二期、Lounge 有關」, 「有 Lounge 以後才能招募」,
  「第二位調酒師」 — `followup_the_manual_describes_the_current_game` now checks they are gone and that the new phrases are
  there.
- **No change required (verified):** 招牌菜 (「客人會專程為它來」 is still how it works; only the arrival line changed); 餐廳日誌
  (the 故事 page's chapters are described generically; 樓上 appears there like the others).
- Audit stamp: `last: v2.4 rc5`.

## 9. The brief's completion report (second_floor_and_long_arcs §48)

- **A. Current state.** Before: rc4 (P0 + P1). Preserved: everything in rc4, the v2.3 Lounge cast and their stories,
  every save. Changed: the second floor, the staff pools, the fixes above.
- **B. The arc.** §3. Formal project eligibility: U6's evidence list (`upAskReady`). Pacing rules: narrative gaps only
  (1, 2, 3, 2, 2 days), one major a day, no first-day dump.
- **C. The cat event.** §4.
- **D. The space.** §5. The reference pictures are the geometry; the cats in them are not canon.
- **E. Staff Room.** Not built. Its prerequisite is now the second floor (it will grow walls in `UP_ZONES.staff` when its
  story happens). The evidence is kept as facts (`sp_seat`, `sp_box`, `sp_stuff`) and the open floor's traces.
- **F. Character arcs.** 怡君: done in rc4 (introduction 《三個選項》, the move, the spare key, 《那面牆》 with 王先生, the
  settlement, the aftermath). Kevin, 珊珊, 宇翔, 小彤 + parents, 老林, 國雄: not started (P5); nothing in rc5 contradicts
  them — no line yet for any of them.
- **G. Migration.** Old saves start the second floor with nothing set; mature saves get the arc at its own pace
  (§6). The staff pools migrate by name and role, nobody is fired (§7). Save/reload: before the project, after the
  call, after the purchase (tests); the night is not saved half-way — a reload puts the evening back at the last
  checkpoint and the night plays again.

## 10. QA (implementation pass T, the items rc5 touches)

| # | Check | How |
|---|---|---|
| 24 | Second Floor geometry follows the saved references | Screenshots (`u4_*`, `u7_*`, `up_*`) |
| 25 | 柔柔 orange longhair, 小齁 tabby-white | Screenshots |
| 26 | Missing only briefly, indoors | §4; `v24_the_night_of_the_missing_cats` |
| 27 | Only the crew really present | the same test (Nina off: not in the search) |
| 28 | No immediate unlock | the same test; `v24_the_second_floor_is_a_story_before_it_is_a_room` |
| 29 | The whole floor | `v24_jill_calls_the_landlord_and_the_whole_floor_is_hers` |
| 30–32 | Open plan, movable furniture, not a Staff Room | the same test; `up_open_floor_*.png` |
| 36–37 | Stairs clear, windows and column coherent | Screenshots; the party upstairs is routed round the railing |
| 38–39 | Cats upstairs restrained; 柔柔 back at her window | `upCatLife` (one cat at a time, now and then); the pacing runs (`up_late` on Day 100–111) |
| 44 | The restaurant still works | the full regression (§11) |
| 45 | Phone layout | every screenshot is 390×844 |
| 46–47 | Save/reload at each state; story survives | the tests above |
| 48 | No baseline screenshot silently rewritten | §11 (goldens) |

## 11. Tests and regression

- New in rc5 (all in `tests/v24_tests.py`): the pools (two), the signature line, the steppers, the Second Floor (four).
- `docs/evidence/v24_rc5/full_run.log` — the whole suite during the evidence pass: 149 passed, 2 failed — both tests
  behind the new data (twenty-five staff portraits now, not twenty-four; the player's Day 61 save already has v2.4 story
  facts, which the load test took for fabricated). Updated: the portrait count, and the load test now checks that a
  save's v2.4 facts come back exactly as saved (none for a save from before v2.4). `rerun_after_fix.log`: 3 passed.
- `full_run_2.log` — the whole suite after those updates: 151 passed, 0 failed.
- `full_run_final.log` — the whole suite on the release commit (92751b0): **151 passed, 0 failed**.
- Goldens: not re-recorded. `golden_scenario` and `golden_frames` pass unchanged — their two fresh days have no
  employee whose look changed (秀琴阿姨's was already hers) and never reach the second floor or the Lounge.

## 12. For the player to look at (O)

1. Your Day 61 save: the staff page — 餐廳員工 12/12, Lounge 員工 2/5; hire 阿拓, 安安, 許葳 from 「Lounge 名單」; nobody else is offered.
2. Evan in the Lounge (short dark hair now); the other staff look like their portraits.
3. The signature guests: one line now and then, with your dish's name.
4. The signature dessert's −/＋: it stays put while you add stock.
5. Around Day 83–85 (after the wall), a regular asks about upstairs; a few days later the landlord; then, one evening,
   two cats are missing at closing.
6. After the call, 店舖工程 › 二樓（整層）; the floor the same evening, and over the next week.

## 13. Evidence (`docs/evidence/v24_rc5/`)

Screenshots (390×844, real play from the Day 52 and Day 61 saves; T, not O), listed with one line each in
`shots_up.txt`: the landlord's afternoon (`u3_*`), the night (`u4_*`), the call and the project (`u6_*`, `u7_*`), the open
floor (`up_*`), the staff lists and the Lounge at work (`staff_*`). Sims in `sims/`. The full run in `full_run.log`.
