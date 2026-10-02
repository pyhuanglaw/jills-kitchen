# JILL'S KITCHEN v2.4 rc6 — release report (2026-10-02)

rc6 = P3 the Staff Room + P4 the Private Dining Room, on the second floor that rc5 opened. The plan and its corrections
are `docs/v24/AUDIT_AND_PLAN.md` §8, §8.1 (economy) and §8.2 (the player's corrections of 04:06–04:26).

**How this report reports** (the player's rc6 spec, AY):
- **IMPLEMENTED** — the code is in the repo, at the tag.
- **TESTED** — an automated test or a seeded simulation shows it works.
- **OBSERVED** — seen with my own eyes in screenshots of real play (the player's Day 61 save, headless Chromium,
  390×844 phone size, some at 1280×800). This is *my* observation, not the player's. Nothing here was observed on an
  iPhone.
- **Needs Player Observation** — what only the player can judge, on the phone (§12).

**Branch and builds**
- Branch: `master`. Tag: `v2.4-rc6`.
- Published to the player's usual URL, https://claude.ai/artifact/2vhURujrtCpQ1P5jnSsjps (saves live there). §13 is the
  check of the published page.

**What the player asked for in this round** (filed verbatim, `docs/v24/`)
- 02:31–02:48: finish both rooms; the rule 「以後只要我跟你說過的東西，不管你中間有沒有發佈內容，你就是把它做完」
  (`rule_finish_everything_0237_2026-10-02.txt`, also `docs/RELEASE_CHECKLIST.md` §0).
- 03:00: the RC6 final spec, sections A–AY (`rc6_final_spec_0300_2026-10-02.txt`).
- 04:06: the RC6 final implementation spec, Staff Room + Private Dining + Second Floor integration
  (`rc6_spec_spaces_0406_2026-10-02.txt`; the attachment ends in section 33, filed as received).
- 04:08: 【重要修正｜Second Floor 的空間層級與操作方式】 (`second_floor_architecture_0408_2026-10-02.txt`).
- 04:09: the impact report request; 「關於空間有什麼要問的現在問清楚」; 04:13 「你如果有問問題問我我還沒回答你之前你也是給我我繼續做下去」
  (`impact_report_request_0409_2026-10-02.txt`). The impact report was sent at 04:13 (class A: the rooms' own views were
  already separate scenes; the floor's view and the navigation changed).
- 04:17: the floor's view as a finished floor, real architecture, Restaurant → Second Floor → Room
  (`second_floor_overview_visual_0417_2026-10-02.txt`).
- 04:25–04:26: the Private Dining Room as contemporary Art Deco, the same beautiful room in all three phases, the
  table running down the phone (`private_dining_artdeco_0425_2026-10-02.txt`, the photo
  `refs/private_dining_artdeco_mood_0425_2026-10-02.jpg`).

## 1. Commits since v2.4-rc5

| Commit | What |
|---|---|
| 5bb4806 | The two rooms: Phase I–III, their own views, the stories, the crew using the room, reservations, walk-ins, story bookings, +2 places; the spec and the rule filed; the plan |
| ff05e2d | The long table's way round; a cat now and then in the empty room; the summary line; the manual; three tests |
| ff3f00f | The player's corrections of 04:06–04:26: closed rooms on the floor, the floor recomposed, 二樓 → a room → ‹ 二樓, the Art Deco room with the long table down the screen; the crew go up first; big parties order a dish each; the minimum from what a party orders |
| 822b8ca | The minimum's factors from the simulations; breaks that happen; one of the floor out by the big window at closing; a test |
| 0b8ca7c | Desktop: a lower far wall so the table keeps its length; settings outlined; the plan §8.1–§8.2; the sims |
| 6fad1b4 | The room's order and bill first for the floor crew; its party waits for the bill at ease |
| bd3c4ec | The single-file build |
| (this) | The report and the evidence |

## 2. Release content audit

| FEATURE / FIX | STATUS | IN THIS RELEASE? | WHY / NOTES |
|---|---|---|---|
| Staff Room: the need (《箱子》《又在找位置》《東西放哪》 rc5, 《等一下》), 《大家待的地方》, the project | DONE | Yes | §3 |
| Staff Room Phase I / II / III, built in place | DONE | Yes | §3 |
| Staff Room in use: early arrivals, quiet-moment breaks, closing; Restaurant and Lounge crew; cats | DONE | Yes | §3 |
| Staff Room traces only after their story (延長線, 阿德's towel, 小彤's cup …) | DONE | Yes | §3 |
| Private Dining: 怡君 「有比較安靜的嗎？」, a second table that is not staff family, 《關上門以後》, the project, 「裡面可以嗎？」 | DONE | Yes | §4 |
| Private Dining Phase I / II / III (4–6 / 4–8 / 4–10) | DONE | Yes | §4 |
| Private Dining as contemporary Art Deco from Phase I; the table down the screen | DONE | Yes | The player, 04:25; §4 |
| Reservations: automatic, one per evening, soft pity, guaranteed early, the news card, fixed minimum, the bill's floor | DONE | Yes | §4, §7 |
| Walk-ins on unreserved evenings; story bookings first | DONE | Yes | §4 |
| Second Floor: closed rooms on the floor's view, the floor recomposed, the corner left undecided | DONE | Yes | The player, 04:06–04:17; §5 |
| Navigation: 二樓 → the floor; doors → rooms; ‹ 二樓 | DONE | Yes | §5 |
| Restaurant staff +1 (Private Dining I) +1 (III); Lounge unchanged | DONE | Yes | §6 |
| Economy: prices, the minimum, measured | DONE | Yes | §7, AUDIT_AND_PLAN §8.1 |
| Bug: a booked party could wait upstairs for its bill until it left unpaid | FIXED | Yes | §4 |
| Bug: the minimum was always the bill (a surcharge) | FIXED | Yes | §7 |
| Manual, journal chapters | DONE | Yes | §8 |
| P5 (rc7): the other Staff Lives arcs | NOT STARTED | No | Next, straight after this release (the plan sent to the player at 03:05) |
| The floor's undecided corner | KEPT UNDECIDED | — | The player: do not decide its use |

## 3. The Staff Room

**IMPLEMENTED**
- Story. 《等一下》 (`sp_wait`): 怡君 waiting at closing for her mother, nowhere to sit that is not a guest's seat.
  《大家待的地方》 (`sr_story`, the day's major, after closing; the player's lines) when the floor has been taken a week
  and is in use, the restaurant is at level 5, eight on the restaurant's list with three of them 熟手 or more (tenure
  classes — the legacy crew's two or three counted days never make them new), someone from outside introduced, and two
  kinds of evidence. Then the project is offered (開始規劃 / 之後再說; it stays in 店舖工程 either way).
- Phases (店舖工程 › 二樓的房間): I $160,000 — walls, door, sofa, chairs, a low table, water, a shelf, outlets (the open
  floor's cabinet, floor lamp and coat stand move in); built overnight. II $70,000 (5 days after I) — lockers, a small
  fridge, coffee and tea, an outlet strip, cups. III $90,000 (7 days after II) — a softer sofa, a table to eat round, a
  speaker, more shelves. II and III are the same room the next day; one job on the floor at a time.
- Use, with no story most of the time: 0–2 of the floor sit a moment before the doors open; in a quiet moment one of
  the floor goes up for a few minutes (at most twice an evening; never when the door has a queue); at closing a few
  of the kitchen, the floor and — with the Lounge — the bar go up, sit, hold a cup or a phone, talk, and the day ends.
  First-time moments once each, two days apart: 「插座不夠。」→ (II) 「我就說吧。」, 「家裡多煮的，你們吃。」, Hugo and the
  fridge, 「我充電線呢？」「你外套口袋。」. The first evening: Jill goes up — 「坐啊。」「喔，好。」.
- Lounge crew use it and stay on the Lounge's list; it adds no places (K).
- Cats: on about a quarter of closings one follows the crew in and sleeps on the sofa a while, then goes.
- The journal: the restaurant's story has the chapter 「大家待的地方」.

**TESTED** — `v24_rc6_the_staff_room_comes_from_a_need_and_grows_in_place`, `…_is_used_and_the_pools_stay_apart`,
`…_cats_visit_the_rooms_and_leave`, `…_one_tab_for_the_floor_and_old_saves_get_nothing`. Simulation (§9): the story 7
days after the lease, the room the next day; breaks on 28–34 of 53 evenings; a cat on 12; at closing about six up there
at the most; no second major on any day.

**OBSERVED** (screenshots, §11): Phase I and III at closing — people on the sofa, the chairs, the stool, by the window
and the fridge; 小彤's cup, the towel; the room's frosted window lit on the floor's view while they are in there.

## 4. The Private Dining Room

**IMPLEMENTED**
- Story. 怡君 with three friends: 「要坐裡面一點嗎？」「有比較安靜的嗎？」「……沒有。」 (`pd_yj`, nothing unlocks); days later a
  table that is not staff family with the same need — 周董 with two guests, 「有比較不被打擾的位置嗎？」 (a family at a
  busy hour where the save does not know him) (`pd_other`); then 《關上門以後》 (`pd_story`, major, after closing; the
  player's lines; the Lounge line only when there is a Lounge), when the Staff Room is ten days old with something of
  the people in it. The project is offered. A few days after the room opens, the payoff 「裡面可以嗎？」「可以。」 on a
  story booking (`pd_back`).
- The room (the player's 04:25 brief): contemporary Art Deco with Jill's Kitchen's warmth, already finished and
  beautiful in Phase I — a stone floor in large warm-charcoal slabs, an ivory stone table on walnut and brass running
  from the door (the near end, the bottom of the view) to the window wall (its long axis is the phone's height), deep
  green panelling with brass lines on the far and side walls, upholstered oatmeal chairs on brass feet down both sides,
  a stepped brass pendant, a walnut sideboard under the window, a service console, a plant in a brass pot. Phase II,
  the same room more complete: the table longer (8), sconces, fluted panels, velvet drapes on a brass rod, a framed
  print, a console with its lamp, a coat stand, flowers, water glasses. Phase III: the table at 10, the coffered
  ceiling, the tiered chandelier, a wine cabinet, an arched mirror, the sideboard's stone top and lamp, gold chargers,
  wine glasses, candles. Prices I $240,000, II $120,000 (6 days and 3 uses after I), III $160,000 (8 days and 9 uses).
- Reservations: automatic (no accept / decline), at most one for the evening, made on the prep screen with its date,
  meal period, party size (4 up to the phase's maximum), kind and minimum, and saved; never made twice, never on an
  evening a story holds; the room is kept for them (no walk-in, even before they come). The day's news:
  「今晚｜私人包廂｜已預約」, 「6 位・家庭聚餐・最低消費 $X」. Frequency: a base chance per phase, a quiet rise after each
  evening without one (never shown), the first by the room's second evening.
- The bill: what they ate, or the minimum if that is more; the tip on what they ate; nobody orders to reach it. The
  summary's chip: 「包廂 N 組（預約）・低消補足 $Y」.
- On an evening nobody booked, a party of four or more that fits may sit there (no minimum); regulars and the Lounge's
  guests keep their places.
- The crew see to the room upstairs first: its order and its bill before anything else on their list (when that job is
  theirs), then its plates and its table; the party waits for the bill at ease. (Before this a booked party could wait
  a minute for its bill and leave unpaid — 8 of 24 bookings in the first simulation.)
- Parties of five or more order as people do — a dish each, a drink or a dessert here and there — up to twelve on one
  ticket; the ticket shows them in one row of smaller plates. Three and four order as before.
- Cats: none while a party is in or the room is kept; in an empty room, now and then, one by the window wall; a party
  coming sends her out by the door.
- Story hooks (AA–AC): `pdBook(day, {k, size, who})` keeps an evening for an authored use before any random booking;
  an existing booking is never overwritten.
- The journal: the chapter 「關上門以後」.

**TESTED** — `v24_rc6_private_dining_reservations_follow_the_rules` (3/4/6/7, 4/8/9, 4/10/11; one an evening; the
minimum fixed through price changes, a new phase and a reload; story evenings; walk-ins), `…_bookings_are_seen_and_grow_
with_the_room`, `…_story_needs_two_tables_and_a_lived_in_staff_room`, `…_a_booked_party_comes_eats_and_pays` (the news
card unclipped at 390, the party played through to the summary), `…_the_private_dining_room_minimum_service_and_long_
table` (the minimum grows with the party, sits near what it orders, the same figure on the same evening; a dish each;
6/8/10 places down the room; the crew go up first). Simulations: §9.

**OBSERVED** (screenshots, §11): Phase I set and with six, II with eight, III set and with ten; the three phases side
by side as one room growing; the ticket of a ten; the room at 1280×800.

## 5. The Second Floor

**IMPLEMENTED**
- The floor's view (二樓) is the floor: where the rooms are, never what is inside. Each room is a closed room on it —
  the wall that faces you (the Private Dining Room's in deep green panels and brass with an arched frosted window; the
  Staff Room's in the floor's plaster with a frosted window), the end wall seen a little from the side as the column
  is, the walls' tops, a real door (trim, panels, a frosted light, the lever, the threshold, a mat) with its sign. The
  state shows from outside only: light in the frosted glass and under the door when someone is in there; on the
  Private Dining Room's door a paper card, 已預約 / 用餐中; over its door the same bubble a table shows when the table
  in there needs you.
- The plan (the player's layout): the Private Dining Room against the left window; the Staff Room on the left, a
  wall's height in front of it (a passage between them, so the Private Dining Room's whole front shows); the open
  middle, the right window (柔柔's), the column, the stairs; the corner left of the stairs not decided — the side
  windows' light on the boards and a plant, nothing more. People walk round the rooms and the column. At closing one of
  the floor stays out by the big window with a phone; the cats keep the cushion and the window.
- Navigation: 二樓 opens the floor from anywhere (it no longer goes round three rooms); tapping a room's door or wall
  goes in; inside, the tab reads 「‹ 二樓」 and the room's own door does the same; the arrow keys go over the top-level
  rooms only.

**TESTED** — `v24_rc6_one_tab_for_the_floor_and_old_saves_get_nothing` (the tab, the doors in and out, ‹ 二樓, the keys),
`…_the_open_floor_keeps_its_ways` (stairs, middle, column, right window, entry and corner outside the rooms; walking
stairs → each door → stairs never through a wall), `…_cats_visit_the_rooms_and_leave`.

**OBSERVED** (screenshots): the floor at dusk with a party upstairs (用餐中, the green front warm), at closing (the
Staff Room lit, someone at the window, a cat on the cushion), with a booking not yet come (已預約).

## 6. Restaurant staff

**IMPLEMENTED** — the restaurant's list gets +1 with the Private Dining Room's Phase I and +1 with its Phase III; the
Lounge's list is its fixed five and unchanged; hiring for the new places is the restaurant's hiring; working in the
Staff Room or upstairs never moves anyone between lists.

**TESTED** — `v24_rc6_two_more_restaurant_places_and_the_lounge_unchanged` (+1, +2, two hires from the restaurant's
pool, the Lounge as it was, kept across a reload).

## 7. Economy (AUDIT_AND_PLAN §8.1)

- Prices: Staff Room $160,000 / $70,000 / $90,000; Private Dining Room $240,000 / $120,000 / $160,000. The measured
  late-game day nets about $55–57k, so each first phase is three to four and a half days of takings — felt, never a
  grind after the story.
- The minimum: what a party of that size and kind orders at the day's menu and prices (the ordering rules themselves,
  sampled with a seeded draw — the day's dice untouched), × 0.88 / 0.92 / 0.94 by phase, rounded to $100, at least
  $400, fixed in the booking. It grows with the party. Most parties pass it; a light table is brought up to it.

## 8. Manual (小小店主手冊) and journal — audit (RELEASE_CHECKLIST §2)

Sections checked: all fourteen. Changed:
- **開店與料理 › 房間**: the floor's tab is the floor; the doors; ‹ 二樓; the room's card and bubble on its door.
- **Jill 與員工 › 員工**: the restaurant's number also grows with the Private Dining Room's I and III; the Staff Room
  adds none.
- **商店 › 店舖工程**: 「二樓的房間」 after the floor.
- **New card 二樓：休息室與包廂**: how they come, the Staff Room, who goes up, the Private Dining Room, bookings, the
  minimum, evenings nobody booked.
- **五隻店貓 › 牠們不出門**: a cat in the Staff Room at closing; in the empty Private Dining Room now and then.
- Stale wording removed: the tab that went round three rooms (「輪流切」); the rc5 sentence that gave the restaurant's
  number only from the ground floor. `followup_the_manual_describes_the_current_game` checks both, and the new phrases.
- The audit stamp on `GUIDE`: 「last: v2.4 rc6 …」.
- Journal: the restaurant's chapters 「大家待的地方」 and 「關上門以後」. The opening tutorial and the Day 1–4 guidance are
  unchanged: nothing of rc6 happens before the late game; no one-time note (the rooms come by their stories — nothing
  is told in advance).

## 9. Simulations (TESTED)

FINAL_SIMS

## 10. Tests and saves

FINAL_REGRESSION

- Saves: every fixture in `tests/saves/` (including the player's Day 52 and Day 61) loads with no room, no booking and
  no story fact of rc6; nothing of the staff, their tenure, the second floor's state, the Lounge's list or the
  restaurant's progress is reset. New state is created only when its story happens (`S.up.sr`, `S.up.pd`).
- Text: `python3 tools/hans_scan.py js/game.js index.html css/style.css` — only the valid Traditional forms (沉, 干貝,
  宿舍).

## 11. Evidence

`docs/evidence/v24_rc6/` (README there): the phone screenshots by `tools/sims/v24_rooms_shots.py`, the simulation logs
by `tools/sims/v24_rooms_pacing.py`, the full run's log.

## 12. Needs Player Observation (on the iPhone)

1. **The floor's view** (二樓): does it read as the finished floor above the restaurant — two real rooms, the open part,
   the stairs, the cats — and not a map for choosing rooms? Are the doors easy to find and to tap?
2. **The Private Dining Room**: the Art Deco room on the phone — the green, the stone, the brass, the long table down
   the screen; is Phase I already beautiful enough for its price? Are the three phases clearly one room?
3. **Bookings**: over your evenings, does it feel that people really book the room — not every evening, more with each
   phase? Is the news card readable? Does the minimum feel like a floor (most tables pass it) and not a charge?
4. **The Staff Room**: do you see people use it (early, a short break, after closing) without the floor emptying?
5. **The stories**: 《等一下》, 《大家待的地方》, 怡君's 「有比較安靜的嗎？」, the second table, 《關上門以後》, 「裡面可以嗎？」 —
   the spacing in your own play.
6. **Navigation**: 二樓 → a door → the room → ‹ 二樓 — clear where you are?

## 13. The published page

PUBLISHED_CHECK

## 14. Next

P5 (rc7): the other Staff Lives arcs (國雄, 宇翔, 珊珊, 老林, Kevin, 小彤 and her parents, Kai, the crossovers), as in the
plan sent at 03:05 — straight after this release.
