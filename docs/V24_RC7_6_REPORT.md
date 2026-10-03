# JILL'S KITCHEN v2.4 rc7.6 — release report (2026-10-03)

rc7.6 is built on rc7.5. It holds the chef's night (主廚之夜), Ken's tasting night over the whole Lounge, the Lounge's bar
turned into a longer L, and Dylan's hood in Jill's room — the player's messages of 2026-10-02 14:49 / 22:11 and of
2026-10-03 07:09–08:00.

**How this report reports** (`docs/RELEASE_CHECKLIST.md` §3):
- **I — IMPLEMENTED**: the code is in the repo, at the tag.
- **T — TESTED**: a test, or a scripted run on the player's own saves, shows it works. Screenshots taken in headless
  Chromium at 390×844 count as T.
- **O — OBSERVED**: only when the player has confirmed it in their own play. Nothing here is O yet, and nothing was
  observed on an iPhone.

**Branch, tag, page**
- Branch `wip/rc7.6-chef` (from rc7.5's candidate; rc7.5 merged in at its release), tag `v2.4-rc7.6`.
- Published to the player's usual URL, https://claude.ai/artifact/2vhURujrtCpQ1P5jnSsjps (§7).

## 0. What the player asked for

Filed verbatim: `docs/v24/player_messages_0709_0716_2026-10-03.txt`, `docs/v24/player_messages_0744_0800_2026-10-03.txt`.

- 2026-10-02 14:49 (events in the Lounge) and 22:11 「而且你不是說酒吧可以辦活動嗎？除了品酒。」 — the chef's night.
- 07:09 「可以 就是只有主廚之夜的來賓可以點餐廳的」 — the first plan approved (the bar's six for the chef's night).
- 07:44 「在房間Dylan就穿帽T一直戴著帽T帽子吧」
- 07:44 「酒吧品酒日不只吧台 整個酒吧都是品酒日的來賓可以嗎」
- 07:44 「吧檯新增L型就能增加位子」, 07:45 「而且可以變長一點」
- 08:00 「主廚之夜就是包場整間辦主廚之夜 就是讓酒吧的客人也能吃到餐廳的厲害的菜，所以整個酒吧的客人平常的酒吧的客人也可以來呀，
  只是他們來的是主廚之夜的活動，那整間都是給主廚之夜辦」 — this replaces the 07:09 plan: the whole Lounge, not the bar's six.
- 08:51 (answering: a ticket for the tasting night, or by the glass?) 「少賺沒關係 但是之後聯名酒出了之後開店前可以選擇要不要舉辦品酒夜」
  — by the glass; once the wine is out, the player decides before opening.

## 1. Commits since rc7.5

- e88a89f — 主廚之夜, first build (the 07:09 plan: the bar's six, the kitchen cooking the courses).
- 6a0e326 — its photo taken before the closing scene moves the view, kept whatever else the day kept.
- 4112608 — Dylan's hood up in Jill's room (07:44); the player's messages 07:44–08:00 filed.
- 1d8aa2e — the bar's L from Lounge II; both nights book out the whole Lounge (07:44, 08:00); Ken's rounds; the chef's
  night plated at the bar, course by course, carried in the Lounge; texts and the manual.
- c435d84 — the evening's schedule kept in time order; the chef's night photo while the room is full; tests for all of it.
- 9c83f76 — this report's first draft.
- 84c7899 — after 「晚餐之後」 the tasting night is the player's to hold (08:51); the manual; a test.
- 8514239 — the chef's night's card and note say who makes its courses; Ken's first night begins 「快七點了」.
- 7a69925 — evidence so far (the measurements, Dylan, the L bar).
- 66e50c6 — merge of the released rc7.5 (`v2.4-rc7.5`).
- 3b075fe — the single file rebuilt. **The full regression ran on 3b075fe** (§6).
- (the report's final commit at the release: documents only)

## 2. Release content audit

| Feature / fix | Status | Branch | In rc7.6? | Why / why not |
|---|---|---|---|---|
| 主廚之夜, booked out (14:49, 22:11, 08:00) | Done | wip/rc7.6-chef | Yes | |
| Ken's tasting night over the whole Lounge (07:44) | Done | wip/rc7.6-chef | Yes | |
| The bar's L, longer, nine seats (07:44–07:45) | Done | wip/rc7.6-chef | Yes | From Lounge II; Lounge I keeps its six |
| Dylan's hood up in Jill's room (07:44) | Done | wip/rc7.6-chef | Yes | |
| After 「晚餐之後」: the tasting night is the player's to hold, before opening (08:51) | Done | wip/rc7.6-chef | Yes | At most once a week, never on the chef's night — the two limits were added here and told to the player |
| The evening's schedule kept in time order | Fixed | wip/rc7.6-chef | Yes | Found while measuring the chef's night: a held visit waited behind walk-ins the 「店裡突然安靜下來了」 moment had pushed back |
| Ken goes home after his night by the evening's clock | Fixed | wip/rc7.6-chef | Yes | Found in the same runs: a night that ended at closing time left him standing behind the bar under the test harness |
| 鋼琴之夜 (paid pianist, 14:49) | Already in | — | — | 予安's nights (rc7) |
| The wife's no-login backup, the picture-dependent stories, the P5 outside cast | Not started | — | No | The backup needs a phone test by the player; the stories wait for the player's pictures |

## 3. What changed, with I / T / O

**主廚之夜 — the chef's night, booked out** (14:49, 22:11, 08:00)
- **I** — From Lounge II with a signature dish, planned in the shop's Lounge section for tomorrow (「排在明晚」, cancel
  until the doors open), never on Ken's night, at most once a week. The news the day before and on the day:
  「明晚／今晚｜主廚之夜 · N 席」 — N is the whole Lounge's seats (23 at Lounge III), 「包場」.
- **I** — That night the whole Lounge is the chef's night's (`lgBook`): one at each stool, two at each small table and in
  the corner, four on the sofa. The Lounge's own people who were coming tonight come to it (in the runs: Monsieur 杜
  and Ken sat at the bar and ate the three courses); nobody else is seated in the Lounge while it lasts, nobody moves over
  after dinner, nobody waits at the bar. A guest of the night who finds a table not yet cleared comes back a moment
  later, never to the dining room.
- **I** — Three courses (the best starter on the menu, the signature, the signature dessert or the best dessert), each
  with a glass, one after the other: the second is plated once the first is eaten (`cnCourses`). The portions were
  made in the morning; at night they are plated behind the bar and set at the end of the bar's L — the kitchen's
  stations never cook them (the first build did: 69 plates jammed the kitchen and the dining room lost twice its
  guests). The Lounge's waiter carries them to the tables, the bartenders hand them over at the bar; each course's
  glass goes with its plate. On the tickets a course still to come is dashed.
- **I** — $1,800 a head, wine included, on the summary's Lounge line apart from the Lounge's tabs. The first night: a
  scene at its start and its end (the restaurant held); later nights, a line in the room. The album keeps its picture
  (taken while the room is full and someone is looking at the Lounge, or as it ends).
- **T** — `v24_rc76_the_chefs_night` (on the Day 74 save: 23 people, every course and glass out, the second never
  before the first, never through the stations, nobody else in the Lounge, 杜 and a pair come to it via `lgBook`,
  $41,400 on the summary, the album). The evening measured on the Day 74 save, three seeds (§8 `sims/`): every one of
  the 23 had all three courses, the last out between 20:31 and 20:41; the day's net +$23k / +$2k / +$18k against the
  same day without it; 6–13 more turned away at the dining room's door (the Lounge is not there for them that night).
- **O** — not yet.

**Ken's tasting night over the whole Lounge** (07:44)
- **I** — Every Lounge seat is for the people who came (`lgBook`, as above; twos and fours at the tables and the sofa);
  the news says the whole room's seats. Ken pours tonight's three a round at a time at every seat (`kenRounds`: the
  first as the night opens, the second and the last as he says so); someone who sits down after a round has it poured
  as they sit; the bartenders never pour them. Three glasses set out at every seat of every table too; the small board
  stands at the end of the bar's L. By the glass, as before (08:51: 「少賺沒關係」).
- **I** — After the night Ken goes home by the evening's clock as well as the timer (a night that ended at closing time
  left him standing behind the bar under the test harness).
- **T** — `v24_rc7_ken_hosts_his_tasting_nights` (the whole room, 23, twos and a four; the first round at the tables
  too, never through the bartenders; the Lounge everyone's again after; Ken goes home), `v24_rc7_ken_comes_back_and_proposes_a_tasting`
  (the news, 23 seats). Measured (three seeds): the Lounge took about $16k against $13k on a normal day, but with the
  room booked out the dining room had no bar to send its waiting guests to: 8–10 more turned away, the day's net −$1k /
  −$15k / −$8k. Told to the player at 08:48; the answer (08:51): less is fine.
- **O** — not yet.

**After 「晚餐之後」: the player holds the tasting night** (08:51)
- **I** — Once the wine is out Ken no longer plans his nights. Before opening the news asks 「Ken 的品酒夜｜今晚要辦嗎？」:
  「今晚辦」 makes tonight his, 「這次不辦」 takes it back before the doors open. At most once a week, never on the chef's
  night (both limits added here, told to the player). A later night an older save had planned by itself becomes the
  player's to hold. The story's three nights are unchanged.
- **T** — `v24_rc76_after_the_wine_the_tasting_night_is_the_players`; evidence `kt03`, `kt04`.
- **O** — not yet.

**The bar's L** (07:44–07:45)
- **I** — From Lounge II the counter runs on to the left, in front of the plain wall (the wine wall stays where it was),
  and turns toward the room at its left end. Seven stools along it, two along the L, nine in all, 30 apart as rc7.5
  made them, every one inside a phone's view. The first six keep their places in the seat list (a regular's usual
  stool, the old saves); the three new ones come last. Walkers go round the L and the counter (the obstacle paths the
  second floor already uses). A fourth lamp hangs over the L. Lounge I keeps its six in a row.
- **T** — `v24_rc76_the_bar_turns_into_an_l` (nine, the spacing, the phone's view, the list order, a walk from the arch
  never through the L or the counter, an evening's stools sat on), the Lounge levels test (nine at III); screenshots.
- **O** — not yet.

**Dylan's hood** (07:44)
- **I** — In Jill's room Dylan's hoodie has its hood up: over his hair and ears, his face and glasses in its opening, a
  little fringe under its edge; from behind, a grey hood under the headphones. In the restaurant, the cardigan.
- **T** — `v24_rc76_dylan_at_home_keeps_his_hood_up` (pixels: the crown and the ears are the hood's grey at home, his
  hair out; from behind the hood; at the desk he is drawn in it); screenshots (the sheet, the room at gameplay scale).
- **O** — not yet.

**The evening's schedule kept in time order** (found while measuring)
- **I** — The day's visitors are read in time order; the 「店裡突然安靜下來了」 moment pushed the next half-minute's
  walk-ins back without reordering, so a visit whose hour is held (a tasting's guests, 予安's trial, the chef's night)
  waited behind them — on one seed the chef's night's first guests came 20 seconds late and in a burst. Dylan's later
  try went in unsorted too. Both now put the rest of the evening back in order (`schedTailSort`).
- **T** — the chef's night's timeline on the same seed (the first guests seated on time, the night ending at 20:30
  instead of 21:16); the full regression.

## 4. Manual audit (小小店主手冊)

Audited against the final rc7.6 set (after the merge of rc7.5).
- **Changed — 主廚之夜**: rewritten — 包場, the whole Lounge (N 席), the Lounge's own people come to it, around seven,
  three courses made in the morning and plated at the bar 「一道一道上」, the plates at 「吧台 L 型的那一頭」, the Lounge's
  waiter and the bartenders carry, the glass with its plate, $1,800, the summary. Removed: 「吧台的六個位子留給訂位的客人」,
  「廚房照常做」, 「只有主廚之夜的客人在 Lounge 吃餐廳的菜」 (no one else is in the Lounge that night).
- **Changed — Ken 的品酒夜**: the whole Lounge (N 席), twos and fours, 「一輪一輪倒」, the board at the bar's end, 「每桌一份
  小食」; after 「晚餐之後」 the player holds it before opening (「Ken 的品酒夜｜今晚要辦嗎？」, 「今晚辦」, 「這次不辦」, once a
  week, not on the chef's night); by the glass, and that the day usually takes a little less. Removed: 「提議在吧台辦小型的
  品酒夜」, 「那一晚吧台的位子留給品酒的客人」, 「之後每一兩個禮拜他會再辦一次，不用你安排」.
- **Changed — Lounge I／II／III**: 「II：吧台加長、轉成 L 型，九個位子（一樣坐得開）」. The shop's Lounge II card says the same.
- **Changed — the chef's night's shop card**: the buyout, 23 seats, made in the morning and plated at the bar.
- **No change required — Dylan's hood**: verified, the manual says nothing of what he wears.
- **No change required — the schedule's order**: an internal fix; nothing the manual says changes.
- The GUIDE stamp: `last: v2.4 rc7.6 (主廚之夜, booked out — the whole Lounge, plated at the bar, course by course; Ken's
  tasting night the whole Lounge, poured a round at a time; the bar's L from Lounge II, nine seats)`.
- `followup_the_manual_describes_the_current_game`: the new phrases above required, the removed ones stale.

## 5. Tests

- New: `v24_rc76_the_bar_turns_into_an_l`, `v24_rc76_dylan_at_home_keeps_his_hood_up`,
  `v24_rc76_after_the_wine_the_tasting_night_is_the_players`.
- Rewritten: `v24_rc76_the_chefs_night` (booked out: 23 people with twos and a four; nobody else in the Lounge; the
  Lounge's own come to it (`lgBook`); course by course; never through the kitchen's stations; over by 21:03 (.9 of the
  evening); $41,400; the album).
- Changed: `v24_rc7_ken_hosts_his_tasting_nights` (the whole room, 23, the first round poured at the tables by Ken, Ken
  goes home), `v24_rc7_ken_comes_back_and_proposes_a_tasting` (23 seats in the news), the Lounge levels test (nine
  stools at III, two on the L), the manual test (phrases).
- No golden moved: `golden_scenario` and `golden_frames` pass unchanged (no golden frame shows a Lounge II+ room).

## 6. Full regression

- **3b075fe (the published commit): 218 passed, 0 failed** — `regression/full_regression_3b075fe.log`, a clean worktree
  of the commit, 09:12–09:51. Every test ran; none was skipped or deselected.

## 7. Build and publish

- `tools/build_single.py` on 3b075fe: no change to the committed single file. `tools/build_artifact.py` →
  `jills-kitchen-rc7.6.html` (6,557,802 bytes). Tag `v2.4-rc7.6`.
- Published to https://claude.ai/artifact/2vhURujrtCpQ1P5jnSsjps — **version 49** (id 1790992322-ea10), read back at
  09:52.
- Read back and checked (`tools/sims/live_check.py`, `docs/evidence/v24_rc7_6_release/`): the page built from the tag is
  inside the live HTML byte for byte (sha256 c93dd4db1180; the host adds its 552-byte skeleton); the player's Day 74 save
  opens with 「繼續營業 · 21:48」, the evening resumes, every room photographed (Jill's room too), the summary, the staff
  page, Day 75's prep and restock ($208,704 → $183,573), a reload keeps DAY 75 and the money; no page errors.
- The tag moves to this report's commit (documents only; the game is 3b075fe's).

## 8. Evidence (390×844, headless Chromium — T, not O)

`docs/evidence/v24_rc7_6/`:
- `screens/events/` — taken on 3b075fe (`evidence_rc76.py`, its log `evidence_log.txt`): the chef's night's card,
  planned, the news the day before and on the day, its first night opening (held, 19:08) and ending (held, 20:29), the
  whole Lounge at 19:40 with plates waiting at the L's end, the summary (「主廚之夜 23 位 · $41,400」, the day's net
  $72,347), the album's picture; Ken's night: the news, the whole Lounge at 19:08 with glasses on every table, the bar,
  the L and the board; after the wine: 「今晚要辦嗎？」 and the night held.
- `screens/lbar/` — the L on the phone and on a desktop with every stool taken, close-ups, the room with a coordinate
  grid before (rc7.5) and after.
- `screens/dylan/` — the sheet (the restaurant and the room), Jill's room at gameplay scale (Day 52, Day 74), the desk.
- `sims/` — the measurements and `notes.txt` (how the chef's night got its shape; the three-seed comparison).
- `regression/` — the full regression log (§6).

## 9. What only the player can judge (O)

- Whether the L reads as an L at a glance on the phone, and whether two people one behind the other along it look right.
- Whether a booked-out evening feels like an event — the whole room set, Ken's rounds, the chef's courses one after the
  other — and whether 23 seats is the right size for it.
- Whether Dylan with his hood up still has his face (his portrait), and no longer gives the reveal away.

## 10. Text

`python3 tools/hans_scan.py js/game.js index.html docs/V24_RC7_6_REPORT.md docs/v24/player_messages_0744_0800_2026-10-03.txt docs/evidence/v24_rc7_6/sims/notes.txt`:
three expected hits only — 干 (干貝), 沉 (睡得很沉), 舍 (宿舍).
