# JILL'S KITCHEN v2.4 rc6 — release report (2026-10-02)

rc6 has two parts:
- **P3 and P4 of the plan**: the Staff Room and the Private Dining Room, on the second floor that rc5 opened.
- **Everything the player asked for before release**, from 02:31 to 12:16. That covers the second floor's layout and navigation, the guests' clothes, who is where, and the morning's reports (09:33–12:16). The morning's reports are: what is talked about, the summary, the Lounge's list, the freeze, the phone's heat, Sophie and Mia, 安安, the white uniforms, the album, more to spend on, the second floor's prerequisite, stories that hold the restaurant, and 晴 × 阿拓.

The plan is `docs/v24/AUDIT_AND_PLAN.md` §8. Its corrections are in §8.1 (economy), §8.2 (the player's 04:06–04:26) and §8.4 (this morning).

**How this report reports** (the player's rc6 spec, AY; `docs/RELEASE_CHECKLIST.md` §3):
- **I — IMPLEMENTED**: the code is in the repo, at the tag.
- **T — TESTED**: an automated test, or a seeded simulation, shows it works.
  - Screenshots taken by me in headless Chromium from the player's own saves, at 390×844, count as T. They are evidence that I looked.
- **O — OBSERVED**: only when the player has confirmed it in their own play. Nothing in this report is O yet.
  - Nothing was observed on an iPhone. §19 lists what only the player can judge.

**Branch, tag, page**
- Branch `master`, tag `v2.4-rc6`.
- Published to the player's usual URL, https://claude.ai/artifact/2vhURujrtCpQ1P5jnSsjps (the saves live there).
- §20 is the check of the published page.

## 0. What the player asked for (filed verbatim in `docs/v24/`)

| When | What | File |
|---|---|---|
| 02:31–02:48 | Finish both rooms. Rule: 「以後只要我跟你說過的東西…你就是把它做完」 | `rule_finish_everything_0237_2026-10-02.txt` |
| 03:00 | The RC6 final spec, A–AY | `rc6_final_spec_0300_2026-10-02.txt` |
| 04:06–04:26 | The rooms and the floor: the spec; the floor's spatial hierarchy; the impact report; the floor as a finished floor; the Private Dining Room as contemporary Art Deco | `rc6_spec_spaces_0406…`, `second_floor_architecture_0408…`, `impact_report_request_0409…`, `second_floor_overview_visual_0417…`, `private_dining_artdeco_0425…` |
| 05:19, 05:23 | The Staff Room redrawn bright and warm (MUJI); the floor's navigation | `staff_room_muji_0519…`, `second_floor_navigation_0523…` |
| 05:32, 05:42 | The release order; testing strategy (saves as checkpoints, risk-led tests, the full regression as the gate) | `rc6_release_order_0532…`, `testing_strategy_0542…` |
| 06:36, 06:43, 06:57 | 二樓 an everyday tab again; the floor's plan in 店舖工程 for good; the Staff Room's pool table, massage chair, books, games; the Private Dining Room's walkways empty | `second_floor_three_uses_0636…`, `staff_room_recreation_pdr_polish_0643…`, `pdr_spatial_polish_0657…` |
| 06:44 | Report ≠ stop | `report_is_not_stop_0644…` |
| 07:05, 08:12 | The generic guests dressed, not coloured at random; then silhouette and layering | `npc_wardrobe_0705…`, `npc_wardrobe_references_0812…` |
| 07:09 | Who is where: an order ↔ its table ↔ its people ↔ their words | `customer_identity_linking_0709…` |
| 08:37–09:21 | The second floor as the player drew it; the night of the cats' new picture; the stair door | `second_floor_plan_0837…` |
| 09:33–12:16 | The morning's reports, with four saves: Day 61, 67, 68 and 71 | `player_messages_0933_1216_2026-10-02.txt` |
| 10:25 | The Second Floor no longer waits for 《那面牆》 | `second_floor_prerequisite_1025_2026-10-02.txt` |
| 10:32 | Authored story beats hold the restaurant. The audit is `story_presentation_audit_2026-10-02.md`; the player chose what holds at 11:06 | `story_presentation_1032_2026-10-02.txt` |

## 1. Commits since v2.4-rc5

| Commit | Time | What |
|---|---|---|
| 5bb4806 | 03:35 | The two rooms: Phase I–III, their views, stories, the crew, bookings, walk-ins, +2 places |
| ff05e2d | 03:55 | The long table's way round; a cat in the empty room; the summary line; the manual |
| ff3f00f | 04:45 | The player's 04:06–04:26: closed rooms on the floor, the floor recomposed, Art Deco, the long table down the screen |
| 822b8ca | 04:53 | The minimum from what a party orders (I .88, II .92, III .94); a dish each for a big table |
| 0b8ca7c | 05:04 | Desktop's lower far wall; the place settings; §8.1 |
| 6fad1b4 | 05:07 | The room's order and bill first for the floor crew; the party waits for the bill at ease |
| bd3c4ec | 05:07 | The single file |
| 96b883b | 06:30 | The player's 05:19, 05:23: the Staff Room redrawn (MUJI); the rooms and the floor as tabs; the reveal walk |
| 7ce4ece | 07:41 | The player's 06:36, 06:43, 06:57: 二樓 everyday; the floor's plan for good; pool table, massage chair, games and books; the Private Dining Room's walkways |
| 1feb309 | 07:59 | The player's 07:05: the guests' wardrobe |
| 7a060d7 | 08:24 | The player's 07:09: who is where; the night of the cats' picture (08:15) |
| a66d046 | 09:30 | The player's 08:12, 08:37–09:21: silhouette and layering; the floor as the player drew it; the cats' new picture; the stair door |
| 1d91b6e | 11:44 | The player's 09:33–11:06 (§9–§12) |
| 693f8f3 | 11:48 | The catwalk card's own words |
| ea4b5e4 | 12:01 | The player's 11:49: wine research priced like a dish's, each wine doing something; golden_scenario re-recorded with proof; the Day 68 save |
| d958da5 | 12:27 | The player's 12:16: 晴 × 阿拓 and the day's major slot; what the full regression found; golden_frames re-recorded with proof; the Day 71 save |
| 6aa7652 | 12:34 | A regular's dated beat keeps its day; the researched wines without a plate |
| (release) | — | The manual audit, the report, the evidence, the sims, a test for the morning's reports |

## 2. Release content audit

| FEATURE / FIX | STATUS | IN THIS RELEASE? | WHERE |
|---|---|---|---|
| Staff Room: the need, the story 《大家待的地方》, the project, Phase I–III built in place, in use, traces | DONE | Yes | §3 |
| Staff Room redrawn bright and warm; pool table (II), massage chair and books (III), a frame at closing, someone dozing | DONE | Yes | §3 (05:19, 06:43) |
| Private Dining Room: the stories, the project, Phase I–III, contemporary Art Deco, the long table down the screen | DONE | Yes | §4 |
| Private Dining Room's walkways empty: wine cabinet, consoles and coat stand gone | DONE | Yes | §4 (06:57) |
| Bookings (automatic, one an evening, the news card, a fixed minimum just under what they order), walk-ins | DONE | Yes | §4 |
| The second floor as the player drew it (08:37); the stairs (09:14); no column | DONE | Yes | §5 |
| 二樓 an everyday tab; the rooms as tabs; the floor's plan in 店舖工程 for good; the reveal walk | DONE | Yes | §5 (05:23, 06:36) |
| The night of the cats: the player's picture (08:41); the stair door downstairs did not latch (08:44) | DONE | Yes | §5 |
| Restaurant staff +1 (Private Dining I) +1 (III); the Lounge's list unchanged | DONE | Yes | §6 |
| The guests' wardrobe (07:05, 08:12); a guest never in a white top (Q++) | DONE | Yes | §8 |
| Who is where (07:09) | DONE | Yes | §8 |
| 阿拓's portrait from the Lounge cast sheet; every portrait cut clean; 許葳's whole face | DONE | Yes | §9 |
| A guest's passing words once a day; the VIPs' and the named guests' own lines | DONE | Yes | §9 |
| What is new is talked about | DONE | Yes | §9 (09:39) |
| The summary: today's stories, the Lounge's sales, the bartenders' glasses | DONE | Yes | §9 |
| The album's 關閉 at the bottom too | DONE | Yes | §9 (09:51) |
| The Lounge's list on the menu page; tonight's list chosen before opening; bar bites take no menu slot | DONE | Yes | §9 (09:51–10:10) |
| Bug: the menu at its cap with the bar bites on it | FIXED | Yes | §9 (09:55) |
| Bug: the screen dimmed and froze in a service | FIXED | Yes | §9 (09:59–10:01) |
| The phone's heat: the room drawn at most ~30/s in a service, ~10 under a sheet | DONE | Yes | §9 |
| Sophie and Mia begin in a long-running save | FIXED | Yes | §9 (10:05) |
| 安安 at LV2, the Lounge's tables first | DONE | Yes | §9 (10:06) |
| A story page keeps only its beat's own lines | FIXED | Yes | §9 (10:08) |
| The waiters in white shirts | DONE | Yes | §9 (10:15) |
| Photos for the Lounge, the floor upstairs, the Staff Room, the Private Dining Room | DONE | Yes | §9 (10:16) |
| More to spend on: four dream works, four seasonal sets, three contracts, a wine course, wine research, Lounge training a level a day | DONE | Yes | §10 (10:21, 10:40) |
| Wine research priced like a dish's, each wine with a pairing that brings glasses and guests | DONE | Yes | §10 (11:49) |
| 買下整棟 (buy the whole building) | NOT STARTED | No | Asked of the player at 10:40; waiting for their decision |
| The Second Floor's story begins with the finished Lounge, not 《那面牆》 | DONE | Yes | §11 (10:25) |
| Authored beats hold the restaurant, line by line, then resume exactly — for the player's four kinds | DONE | Yes | §12 (10:32, 11:06) |
| 晴 × 阿拓 move on: the day's major slot no longer starves a closing beat; 阿拓's day off; the pace | DONE | Yes | §13 (12:16) |
| Bugs found by the full regression: a non-held beat's scene words; a regular's dated beat losing its day; the catwalk card's text; the researched wines' plate | FIXED | Yes | §14 |
| P5 (rc7): the other Staff Lives arcs | NOT STARTED | No | Next, straight after this release |

## 3. The Staff Room

**I**
- **Story.**
  - 《等一下》: 怡君 waits at closing for her mother, with nowhere to sit that is not a guest's seat.
  - 《大家待的地方》 (the day's major beat, after closing) comes when the floor has been taken a week and is in use, and the crew is big and settled enough.
  - Then the project is offered (開始規劃 / 之後再說; it stays in 店舖工程 either way).
- **The room** (the player's 05:19):
  - Pale oak floor and warm white walls.
  - A low oatmeal sofa and two armchairs round a light wood table, on an ivory rug.
  - A long table for four to six under the sheer-curtained window, with its banquette.
  - A wall of light wood lockers with name cards, and a coat rail.
  - A kitchenette built into the wall: a fridge behind a wood door, a coffee machine, water, cups and open shelves.
  - The furniture is a light natural oak over a paler floor.
- **Phases.** Each is the same room, more lived in; one job on the floor at a time.
  - **I** ($160,000) is already a whole room.
  - **II** ($70,000, five days after I) adds:
    - a pale oak pool table with mushroom felt;
    - lockers with names, each person's own cup;
    - a blanket, a note on the fridge, an outlet strip;
    - board games and cards.
  - **III** ($90,000, seven days after II) adds a light stone massage chair and a table of books in the corner by the door, and photos, plants, flowers and slippers (06:43).
- **In use**, with no story most of the time:
  - Early arrivals sit a moment before opening.
  - A quiet-moment break: at most twice an evening, never with a queue.
  - At closing a few of the crew go up. Now and then two of them play a frame, with a word or two, and sometimes a third watches. From III, someone dozes in the chair. These are runtime only; nothing is saved.
- Walkers go the shortest way round the furniture. Lounge crew use it and stay on the Lounge's list; the room adds no places.

**T**
- `v24_rc6_the_staff_room_comes_from_a_need_and_grows_in_place`
- `…_is_used_and_the_pools_stay_apart`
- `v24_rc6_the_staff_room_has_a_way_to_every_seat`
- `v24_rc6_the_staff_room_plays_a_frame_and_dozes`
- `v24_rc6_cats_visit_the_rooms_and_leave`
- Phone screenshots of Phase I/II/III, set and at closing (`docs/evidence/v24_rc6/`).

## 4. The Private Dining Room

**I**
- **Story.**
  - 怡君 with three friends: 「有比較安靜的嗎？」「……沒有。」
  - Days later, a second table that is not staff family (周董 and two guests).
  - Then 《關上門以後》 (major, after closing), and the project.
  - The payoff 「裡面可以嗎？」「可以。」 comes a few days after the room opens.
- **The room**: contemporary Art Deco from Phase I.
  - A stone floor and an ivory stone table on walnut and brass, running from the door to the window wall down the phone's height.
  - Deep green panelling with brass, oatmeal chairs on brass feet, a stepped brass pendant.
  - II adds sconces, fluted panels, velvet drapes, a print and flowers; the table seats 8.
  - III adds the coffered ceiling, the tiered chandelier, an arched mirror, gold chargers and candles; the table seats 10.
  - The walkways are kept empty (06:57): the ivory stone sideboard is the one service piece.
  - Prices: I $240,000; II $120,000; III $160,000.
- **Bookings.**
  - Automatic: at most one an evening, never twice, never on an evening a story holds.
  - The news card 「今晚｜私人包廂｜已預約」 gives the party size, the kind of meal and the minimum.
  - The room is kept for the party.
- **The minimum.**
  - It is what a party of that size and kind orders at the day's menu and prices, × 0.88 / 0.92 / 0.94 by phase, fixed in the booking.
  - Nobody orders just to reach it.
- **Walk-ins.** On unbooked evenings, a party of four or more that fits may sit there.
- **The crew** see to the room's order and bill first. A party of five or more orders a dish each.

**T**
- `v24_rc6_private_dining_reservations_follow_the_rules`
- `…_bookings_are_seen_and_grow_with_the_room`
- `…_story_needs_two_tables_and_a_lived_in_staff_room`
- `v24_rc6_a_booked_party_comes_eats_and_pays`
- `v24_rc6_the_private_dining_room_minimum_service_and_long_table`
- Simulations (§16). Phone screenshots of the three phases.

## 5. The second floor

**I**
- **The plan, as the player drew it (08:37):**
  - The Private Dining Room is the big room in the top-left, over the street windows.
  - The Staff Room is directly below it, to the back wall.
  - The hall is an L down the right.
  - Both doors open onto the hall where the rooms meet: the Private Dining Room's in its front wall at its corner, the Staff Room's in its east wall near the top.
  - The stairs run across the bottom-right corner at half the size, the way in at their left end. No column (09:14).
- **Navigation (05:23, 06:36).**
  - 二樓 is an everyday tab: the simple floor with its closed rooms.
  - The rooms are tabs of their own (休息室・包廂), each tab reading the room's full name.
  - A room's door goes out onto the floor.
  - The morning a room is finished, Jill takes you upstairs before opening (the reveal).
- **店舖工程 › 二樓** has the floor's plan for good:
  - architecture only;
  - 「？」 where a room is undecided;
  - 「今天完工」 on the day a room is finished;
  - full screen on a tap.
- **The night of the cats**:
  - The player's new picture (08:41) is the illustration.
  - The stair door is downstairs in the side room and did not latch (08:44).

**T**
- `v24_rc6_the_floor_and_its_rooms_are_tabs`
- `v24_rc6_the_floor_is_shown_when_it_changes`
- `v24_rc6_the_floor_plan_grows_with_the_building`
- `v24_rc6_the_open_floor_keeps_its_ways`
- The second floor's story tests

## 6. Restaurant staff

**I**
- The restaurant's list gets +1 with the Private Dining Room's I and +1 with its III. The Lounge's five are unchanged.
- 安安 now joins at LV2 (§9).

**T** — `v24_rc6_two_more_restaurant_places_and_the_lounge_unchanged`.

## 7. Economy (AUDIT_AND_PLAN §8.1)

- The rooms' prices are three to four and a half days of a late-game day's net (about $55–57k).
- The minimum's factors were measured over two 60-day runs: every booking paid, and most parties went past the minimum.
- The things to spend on (§10) add about $1.1M of sinks with their own returns:
  - four dream works ($630,000);
  - seasonal sets ($120,000);
  - contracts (signing fees plus a fee a day);
  - wine research ($29,200);
  - a wine course for each waiter ($12,000).

## 8. The guests' clothes, and who is where

**I — the guests' clothes (07:05, 08:12).**
- Generic guests are dressed from a wardrobe, not coloured at random: muted neutrals, blues, greens, warm reds, and a few brights kept rare.
- Silhouette and layering instead of more prints:
  - a knit with its shirt collar;
  - a cardigan over a shirt or a striped tee;
  - a sweater vest;
  - a knit over the shoulders;
  - a blazer over a shirt;
  - an overshirt, a polo, a rugby, a mock neck, a dress or a skirt.
- Now and then a coloured blazer, a patterned yoke or a tweed. No small florals or dots.
- A table is mostly quiet, with one or two stronger pieces.
- Clothes are chosen from a hash of the day, never Math.random.
- Named people, regulars, the staff and Jill keep their own looks.
- Found by the full regression and kept — the Q++ rule: a guest never wears a white top or a white tee under a cardigan.
  - White is the staff's (the waiters' since 10:15, the cooks' jackets); the cream shirt is Jill's; the navy cardigan over a white tee is Dylan's.
  - The wardrobe's palest shirts are worn a shade deeper: a pale grey-blue, an oat, a blush.

**I — who is where (07:09).**
- An order's T-number or name takes you to its table in whatever room it is, with a ring and 「T35 · 陳家 · 8 位」.
- A tap on a table says who is there; a tap on a regular gives their card.
- A tap on a line someone said finds them, or says they have left.
- A guest who speaks in the room you are looking at is marked for a moment.

**T**
- `q_plus_world_sprites_keep_jill_and_dylan_their_own`
- `v24_rc6_a_name_finds_its_person_and_a_person_its_name`
- golden_frames' re-record (§17): the screens differ only by the clothes, the toast's `who` and the journal's sheet.

## 9. The morning's reports (09:33–10:16)

**I**
- **Portraits (09:33–09:53).**
  - 阿拓 is the cook of the Lounge cast sheet, in his white jacket.
  - Every staff portrait is cut clean of its neighbours; 許葳 shows her whole face.
- **A guest's passing words, once a day (09:39).**
  - The same words from a second guest are left unsaid.
  - A regular's own line, or a story's line, is always said.
  - The VIPs have eight ways of ordering; a named guest who has been before does not talk like a first-timer.
- **What is new is talked about (09:39).**
  - New things are talked about by guests most in their first days, in their own room: the Lounge (I/II/III), the floor upstairs, the rooms, kitchen works, the glass front, the chandelier, the ceiling, the catwalk, cat furniture, decor, the cellar, the piano, the painting and the season's set.
- **The summary (09:44–09:52).**
  - 「今天的故事」: each story page's step dated today, with its title and what happened, and 「看故事頁 ›」.
  - 「Lounge 今天賣了什麼」: each wine and bar bite, how many and for how much, then the total.
  - The bartenders' line: 「調了 N 杯」, not 「沒有桌子要收」.
- **The journal (09:51).** The tall sheet keeps its title and 關閉 at the top, and the album ends with 「關閉日誌」.
- **The menu page (09:51–10:10).**
  - The Lounge's list, with tonight's wines chosen before opening (never none).
  - The bar bites take no menu slot: 「＋ 酒吧小點 幾道（不佔名額）」. This fixes the cap bug of 09:55.
- **The freeze (09:59–10:01).**
  - A 「回到選單」 pill left over from a 看店裡 could outlive its sheet and reach a service, leaving an empty dim sheet.
  - Fix: the pill is hidden with any sheet and at every service start, and an empty sheet over a running service is taken away at once. The bug was reproduced on the committed code before the fix.
- **The phone's heat (09:59).**
  - Drawing the room is nearly all of a frame's cost. It is now drawn at most ~30 times a second in a service, ~10 under a sheet and ~20 while peeking.
  - The cap is by the clock, so a 120 Hz screen does no more than a 60 Hz one.
  - The simulation, the taps and Jill's tray keep every frame.
- **Sophie and Mia (10:05).**
  - Two long-time regulars who have shared the room are noticed by each other.
  - Some evenings bring the two of them in around the same time (a coin from the day) until their story has begun.
- **安安 (10:06).**
  - She joins at LV2 with the Lounge job and sees to the Lounge's tables first.
  - A save whose 安安 lost the job gets it back.
- **A story page keeps only its beat's own lines (10:08).** Jill's 「哪隻？」 is cleaned from the save at boot.
- **The waiters in white shirts (10:15).** Waiters wear #F4F1EA with their dark aprons; the shop's icon is the same.
- **Photos for the new places (10:16).** Ten new album moments:
  - the Lounge's bar full, the sofa table, the quiet corner, a piano night;
  - a cat at the upstairs window, two cats upstairs;
  - a frame of pool, someone dozing, a cat in the Staff Room;
  - the Private Dining Room's closed door and long table.

**T**
- `v24_rc6_the_morning_reports` (added for the release; these had no test of their own):
  - the words once a day;
  - the VIPs' lines;
  - the white shirts;
  - draws per second by the clock: 120 frames → ~30 draws, 60 → ~30, under a sheet ≤ 14;
  - the summary's three parts on the player's Day 71 save;
  - the album's 「關閉日誌」.
- `v24_rc6_new_things_are_talked_about`
- `v24_rc6_bar_bites_take_no_menu_slot`
- `v24_rc6_no_empty_sheet_over_a_service`
- `v24_rc6_sophie_and_mia_begin`
- `v24_rc6_anan_works_the_lounge_first`
- `v24_rc6_story_pages_keep_only_their_own_lines`
- `v24_rc6_new_places_have_their_photos`
- Screenshots sent to the player during the work.

## 10. More to spend on (10:21, 10:40, 11:49)

**I**
- **Dream works.**
  - A commissioned painting: $90,000, ambience +2.
  - A dry-ageing cabinet in the kitchen: $140,000; the beef dishes +8% and ordered more.
  - The Lounge's cellar: $160,000, needs Lounge II; the second and third stages' wines +10%, a second glass now and then, and 老藤卡本內 can be researched.
  - The Lounge's piano: $240,000, needs Lounge II; a music night about one in three, when more stay after dinner.
- **Seasonal sets** ($30,000 each, one out at a time, ambience +1). A change is talked about.
- **Sourcing contracts** (three): a signing fee, then a fee a day taken at the summary and shown on its ledger. Their dishes are +8% and ordered more; end them at any time.
- **A wine course for a waiter** ($12,000). A floor at ease with wine sells a glass with dinner more often.
- **The Lounge's people** are trained one level a day.
- **Wine research (11:49, 「研發酒也太貴 感覺就是為了花錢」).** Each research now costs what a dish's does:
  - $2,500–$8,000; the six together $29,200 (was $376,000).
  - Each wine goes with something:
    - 粉紅氣泡酒: desserts;
    - 橘酒: the roast vegetables, the prosciutto salad and the cheese plate;
    - 黑皮諾: duck and salmon;
    - 老藤卡本內: steak;
    - 香檳: a celebration or a couple;
    - 「晚安」: office workers, students and bloggers.
  - A table that ordered the pairing has a glass of it with dinner more often (×1.4, mostly that one), and stays for one after more often.
  - Every researched wine poured tonight brings a few more people to the Lounge after dinner, up to +15%.
  - The cards and tonight's list say what each wine goes with. Nothing changes before a wine is researched (no extra random draw).
  - The researched wines are drawn like the others: a glass on its coaster, with no plate.

**T**
- `v24_rc6_more_to_spend_on`:
  - every sink and its effect;
  - the research priced within the dishes' range;
  - the pairings;
  - a table that ate duck has the pinot after dinner far more often;
  - more stay with researched wines poured, and more again when one goes with dinner.
- `h_i_k_t_shop_rooms_decoration_pass_and_dreams` (the eight dream works).
- Screenshots: the research cards and tonight's list from the player's Day 71 save (sent 12:28).

**Not in this release**: 買下整棟 (buy the whole building), item 6 of 10:40. It is a product decision only the player can make. I recommended not this version, and it waits for their answer.

## 11. The Second Floor's prerequisite (10:25)

**I**
- The Second Floor's story begins two days after the Lounge is finished. It no longer waits for 《那面牆》 or anything of 怡君's.
- The two chains share only the day's story budget: one major beat a day. There is no new cooldown.
- The floor's own content and order are unchanged:
  - 柔柔 first, 小齁 following;
  - finding the cats does not unlock the rental;
  - the whole floor is rented once;
  - the open-floor period is still there.
- A save with a finished Lounge enters the next valid beat, one at a time.

**T**
- `v24_rc6_a_finished_lounge_opens_the_floor_in_a_mature_save`, on the player's Day 67 save.
- The era, stage-gate, forty-day and second-floor story tests, updated.
- Pacing from the player's Day 67 (`docs/evidence/v24_rc6/sims/pacing_from_day67_lounge_gate.log`) and Day 71 (§16).

## 12. Authored story presentation (10:32, 11:06)

**I**
- **What holds** (the player's choice at 11:06):
  - Sophie and Mia;
  - the leak case (《那面牆》);
  - what brings the Second Floor about, and its rooms' stories;
  - the love stories (晴 × 阿拓, Dylan and Jill, 王先生 and 王太太).
  - 「其他不用」: everything else plays in the room as before.
- **The hold.** When such a beat happens in a service:
  - the restaurant stops: the clock, the orders, patience, the cooks, Jill's tray and the cats;
  - a panel says 「店裡暫停中・…」;
  - the beat moves one line per tap (280 ms debounce, never on its own), with the speaker's portrait;
  - then the service resumes exactly where it stopped, in the room you were looking at.
- Ambient life outside the beat goes on in real time. A beat is never shown twice across a pause and resume.
- The story page records every beat's words, held or not (§14 for the scene path).
- Audit of every story event: 57 of 118 hold (`docs/v24/story_presentation_audit_2026-10-02.md`). 12:16 added a 119th, 阿拓's day off (`tuo_off`, a note at the start of the day), which does not hold.

**T**
- `v24_rc6_an_authored_beat_holds_the_service_until_it_is_read`, the brief's ten points:
  - the busy trigger;
  - the freeze;
  - unlimited reading time;
  - input-only advance;
  - no skipped lines;
  - the exact resume;
  - ambient life unpaused;
  - no duplication across a pause and resume;
  - room / Lounge / Private Dining Room safety;
  - the phone layout.
- Phone screenshot `docs/evidence/v24_rc6/story_hold_phone.png`.
- 晴 × 阿拓's 「多的。」 as the panel, from the player's Day 71 save (sent 12:33).

## 13. 晴 × 阿拓, and the day's major slot (12:16)

The player's Day 71 save had qt_1 on Day 61 and qt_2 on Day 67, then nothing. There were three causes.

**I**
1. **The major slot.**
   - The cause: 「多的。」 comes at closing. It lost the day's one major slot to any major beat earlier in the day, and it was not even counted as waiting, because the lane was full before it was looked at. So the old rule (a class-A beat that has waited long enough plays) never reached it. The player's Day 70 went to 《那面牆》.
   - Now: a major beat that is due when the slot is taken counts a missed day.
   - The next day, the slot is kept for the beat that has waited longest and can happen today (its people in). This lasts one day; if that beat still does not come, the others go first the day after.
   - Still one major beat a day; no new cooldown.
2. **阿拓's absence** (the brief's 「今天炸物怎麼怪怪的？」) could never happen.
   - The cause: the beat asked whether he was employed, not whether he came in, and nobody ever took a day off.
   - Now: 晴 and 阿拓 count as there only when they came in today.
   - Once 「多的。」 has happened, 阿拓 takes one day off (a coin from the day). 晴 and a cook are in, so the absence is noticed.
3. **The pace, still a slow burn** (the brief: 「OPTIONAL STAFF SLOW-BURN」, 「Repeat variations rarely」):
   - qt_2 after four evenings together (was six);
   - 「多的。」 two days later (was three);
   - its repeats every four days or more, at one in two (was six days, two in five);
   - the photo after two repeats and the absence, or two weeks.

**T**
- `v24_rc6_qing_and_tuo_move_on`, on the player's Day 71 save:
  - the slot taken → a counted wait;
  - the next day the slot is kept, another major beat waits, and 「多的。」 plays at closing;
  - one major beat that day;
  - the day off and the absence;
  - the pace.
- `phase7_the_arcs_run_on_real_history_and_leave_it_changed`: the arc with the absence before the photo; firing 阿拓 still ends it cleanly.
- Simulation from the player's Day 71 save (§16), with the beats per day:
  - 「多的。」 on Day 71;
  - the absence on Day 76;
  - the photo on Day 82;
  - the late photo on Day 90;
  - Sophie and Mia, 《那面牆》, the floor and Sophie × 寶寶 going on beside it, never two major beats in a day.

## 14. Found by the full regression (on 693f8f3)

| Finding | Cause | Fix | Test |
|---|---|---|---|
| 怡君's 「吃飯啊。」 not on her story page | After 11:06 her beat does not hold; `scene()` kept a beat's words only on the held path | A beat's scene words are kept whether held or not | `v24_yijun_comes_to_eat…`, `v24_yijun_comes_early…` |
| A guest in a white shirt / a white tee under a cardigan | The wardrobe passes brought the palest shirts; the Q++ rule keeps white for the staff, the cream for Jill, the cardigan over white for Dylan | Those shirts a shade deeper (§8) | `q_plus_world_sprites_keep_jill_and_dylan_their_own` |
| 小林's 「升職了，今天不趕。」 (Day 28) became 「更早以前」 after one more evening (the player's Day 68 save) | An older save dates that beat by a note, and only the latest six notes are kept | The day kept in the flag when read, and before its note goes | `v24_rc6_a_regulars_dated_beat_keeps_its_day`, `every_player_save_migrates_plays_a_day_and_keeps_its_story` |
| 貓的空中走道's card read the wooden ceiling's words | `DREAMS[2]` (already wrong before rc6) | The catwalk's own text | — |
| The researched wines drawn on a plate | Not in the vessel table | A glass on its coaster | Screenshot |
| Test updates for intended changes | The eight dream works; a held story arrival at the head of the schedule (Sophie and Mia's, 10:05); a new day's own beat on opening (the staff meal's joke) | Tests in step | `h_i_k_t…`, `outdoor_area…`, `every_player_save…` |

## 15. Manual (小小店主手冊) — audit (RELEASE_CHECKLIST §2)

All fourteen sections checked against the final feature set.

**Changed for the rooms and the floor (earlier in rc6):**
- 開店與料理 › 房間;
- Jill 與員工 › 員工;
- 商店 › 店舖工程 (二樓的房間, the floor's plan);
- the new card 二樓：休息室與包廂;
- 五隻店貓.

**Changed for 07:09 and 09:33–12:16:**
- 開店與料理 › 誰在哪裡.
- 故事:
  - 店裡暫停中: which stories hold and how;
  - 今天的故事;
  - 忙的時候錯過了: only the beat's own words.
- Lounge:
  - 安安 (new: LV2, the Lounge's tables first);
  - 酒單研發: the price range, the pairings, +15%;
  - 今晚倒哪幾種;
  - 品酒課;
  - Lounge 的人怎麼升級;
  - 帳: the Lounge's sales, the bartenders' glasses.
- 商店:
  - 夢想工程: the four new works;
  - 季節佈置, 食材契作;
  - 店舖工程: the floor's story begins once the Lounge is built, beside 《那面牆》.
- Jill 與員工 › 晚點到: someone may take a day off.
- 餐廳日誌 › 相簿: the new places' photos.

**Stale wording removed:** none was found for this batch. Nothing in the manual tied the floor to 《那面牆》.

**The test.** `followup_the_manual_describes_the_current_game` now requires 21 more phrases for this batch.

**The stamp** on `GUIDE`: 「last: v2.4 rc6 (… the stories that hold the restaurant, the day's stories on the summary, the Lounge's list and sales, the things to spend on, the Second Floor after the Lounge, the new places' photos, a day off)」.

## 16. Simulations (TESTED)

«SIMS»

## 17. Tests, goldens, saves

«FULL_RUN»

**golden_scenario** was re-recorded with proof (`docs/evidence/v24_rc6/golden_scenario_proof.log`).
- The method: take the current code and put back only the 09:39 dialogue changes and the novelty seat pools.
- The result: the old baseline passes. So nothing else in rc6 moved it.
- Without the put-back, day 1 is the same and day 2 differs: a line said once a day draws fewer random numbers.

**golden_frames** was re-recorded with proof (`docs/evidence/v24_rc6/golden_frames/README.md`). With only the dialogue put back:
- Behaviour is identical on both days: the frames, every sample's time, the cats, the weights, the tray, and the end-of-day digests.
- The only DOM difference is the speaking toast's `who` (07:09).
- The screens differ only by the guests' clothes and the journal's tall sheet with its close button.
- Side-by-side images are in the folder.

**Saves.** `every_player_save_migrates_plays_a_day_and_keeps_its_story` runs every save the player has sent, Day 30 to Day 71. For each one it checks:
- it opens silently on its own day;
- its story page shows;
- it plays a day with the lazy bot;
- it keeps its story record and page counts through a save/reload, with no beat lost.

The player's four saves of this morning are filed with their purposes in `tests/saves/README.md`. The latest, `player_day71_1215.json`, is the release check's save.

**Text.** `python3 tools/hans_scan.py js/game.js index.html css/style.css` plus this report and the new docs: only the valid Traditional forms (沉, 干貝, 宿舍).

## 18. Evidence

`docs/evidence/v24_rc6/` (README there):
- the rooms' phone screenshots;
- the story-hold screenshot;
- the golden proofs (`golden_scenario_proof.log`, `golden_frames/`);
- the simulations' logs (`sims/`);
- the full run's logs.

## 19. Needs Player Observation (on the iPhone)

1. **The floor and its rooms.** Does the floor read as the finished floor above the restaurant? Are the doors and tabs clear? Is the Private Dining Room beautiful enough in Phase I for its price?
2. **Bookings and the minimum.** Over your evenings, do bookings feel real, and does the minimum feel like a floor and not a charge?
3. **The Staff Room in use.** Early arrivals, breaks, a frame of pool at closing.
4. **The hold.** Is 「店裡暫停中」 unmistakable? Does one line per tap feel right? Does the service resume where it was? Are the four kinds the right ones?
5. **晴 × 阿拓.** In your own evenings, does their story now move, slowly but visibly?
6. **The wine research.** At $2,500–$8,000, does it feel worth it — glasses with dinner, more people staying?
7. **The heat.** Does the phone stay cooler in a long service?
8. **The guests' clothes.** Do the shirts read as clothes, and the waiters as the staff in white?
9. **The summary.** Is 今天的故事 / Lounge 今天賣了什麼 useful?

## 20. The published page

«PUBLISHED»

## 21. Next

- **P5 (rc7)**: the other Staff Lives arcs (國雄, 宇翔, 珊珊, 老林, Kevin, 小彤 and her parents, Kai, the crossovers), as in the plan sent at 03:05. It starts straight after this release.
- **Waiting for the player**: 買下整棟.
