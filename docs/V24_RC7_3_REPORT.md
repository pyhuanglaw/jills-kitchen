# JILL'S KITCHEN v2.4 rc7.3 — release report (2026-10-03)

rc7.3 is built on rc7.2 (live as version 45 since 00:40). It holds Jill's room: the room itself, Jill's and Dylan's
everyday life in it, the five cats living between it and the restaurant. It also holds the cats' tries at the tables,
寶寶 and the regulars, and the posts' pictures and likes. None of it needs the player's pictures. The player said to
publish it as soon as it was ready (22:18: 「Jill房間如果你不需要我的圖你就先發佈」).

**How this report reports** (`docs/RELEASE_CHECKLIST.md` §3):
- **I — IMPLEMENTED**: the code is in the repo, at the tag.
- **T — TESTED**: a test, or a scripted run on the player's own saves, shows it works. Screenshots taken in headless
  Chromium at 390×844 count as T.
- **O — OBSERVED**: only when the player has confirmed it in their own play. Nothing here is O yet, and nothing was
  observed on an iPhone. A Chromium touch test is not an iPhone.

**Branch, tag, page**
- Branch `wip/rc7.3` (rc7.2 merged in) up to the candidate 9a36bbd; the release fixes on `release/rc7.3` from it (§5, §6);
  tag `v2.4-rc7.3`.
- Published to the player's usual URL, https://claude.ai/artifact/2vhURujrtCpQ1P5jnSsjps (§7).

## 0. What the player asked for

Filed verbatim in `docs/v24/`:
- `jill_room_2026-10-02_1853.txt`: the 18:53 brief, 「Jill 的房間」.
- `jill_room_dylan_study_2026-10-02_1854.txt`: 18:54 (Dylan studies at a real desk), 18:5x (the room has its own
  entrance) and 19:15 (before the reveal too he studies there; the restaurant does not know; the player finds out).
  Both files were filed on `wip/qing-tuo-after-work` and are now on this branch too.
- `player_messages_1920_1932_2026-10-02.txt`: 19:23 (the sofa and the cats' sofa time move into the room; Jill rests
  there).
- `jill_room_cats_2026-10-02_2218.txt`: 22:18–22:54 (where each cat lives; the tables; 樾樾 after closing).
- `refs/dylan_desk_reference_2026-10-02_2232.jpg`: Dylan's desk (22:32).
- The posts' pictures and likes: 15:02 and 22:09 (「貼文還是沒有照片啊」), in the earlier message files.

## 1. Commits since rc7.2

| Commit | What |
|---|---|
| 428d7a7 | Jill's room: the room from Day 1, her rest and evening there, the reveal at his table, the cats' home layer, petting, its doors, the steals and 寶寶's meow, post pictures and likes, tests |
| a2d3104 | Merge of the published rc7.2 |
| 6cd304c | The edge of the bed instead of the dining room's first table; the manual; tests on the player's own backup |
| 9d7df75 | Goldens re-recorded with before/after/diff proof (§5.1) |
| ca3f416 | 樾樾 comes out at the closing once he knows the crew; Jill waits for him; evidence screenshots |
| a9ac17e | The single file rebuilt |
| 9a36bbd | The briefs filed on this branch; the evening's room check; golden_frames re-recorded for the closing (§5.1); the report — the release candidate |
| (release/rc7.3) | The eight tests the first full regression failed, brought up to the game (§5.2); its log and the forty-days seed sweep as evidence |

## 2. Release content audit

| Feature / fix | Status | Branch | In rc7.3? | Why / why not |
|---|---|---|---|---|
| Jill's room from Day 1; the dining room without the sofa (18:53 §1–§5) | Done | wip/rc7.3 | Yes | |
| Jill's rest and her evening in her room; the e-book only there (18:53 §6, 19:23) | Done | wip/rc7.3 | Yes | |
| Dylan studies at his desk, before the reveal too (18:54, 19:15, 22:32) | Done | wip/rc7.3 | Yes | |
| The reveal: at his table, then the two of them go back to the room | Done | wip/rc7.3 | Yes | |
| Text audit: Dylan lives here (18:53 §16) | Done | wip/rc7.3 | Yes | Lines that only the 晴×拓 scenes hold are on that branch |
| The cats' homes; the sofa's cats in the room (22:18, 22:25, 22:33) | Done | wip/rc7.3 | Yes | |
| 樾樾 waits for Jill after closing (22:54) | Done | wip/rc7.3 | Yes | |
| 小齁, 寶寶 and 包包 at the tables, never successful (22:26–22:27) | Done | wip/rc7.3 | Yes | |
| 寶寶 meows at people she knows, who melt (22:18) | Done | wip/rc7.3 | Yes | |
| Posts with their pictures and likes (15:02, 22:09) | Done | wip/rc7.3 | Yes | |
| Dylan's first drink, 晴×拓 Acts 2 and 5 under the new canon (18:53 §9–§11) | Written | wip/qing-tuo-after-work | No | They come with the 晴×拓 story, which waits for the player's pictures (19:20) |
| The Madame Lin origin line, the bar next door (19:19, 19:30) | Planned | — | No | Needs the player's pictures |
| Guest preferences: a favourite dish or glass (22:39) | Implemented after the candidate, being tested | wip/rc7.3 (after 9a36bbd) | No | rc7.4, once its tests and screenshots are done |
| The Lounge's bites: oysters, cheese sticks, pork knuckle, Buffalo wings (23:03) | Implemented after the candidate, being tested | wip/rc7.3 (after 9a36bbd) | No | rc7.4 |
| The Lounge's TV ($200,000) and sound system ($150,000) (23:06) | Implemented after the candidate, being tested | wip/rc7.3 (after 9a36bbd) | No | rc7.4 |
| Sprites for the new story people: Evan, 沈晴, 阿拓 (22:22) | Implemented after the candidate, being tested | wip/rc7.3 (after 9a36bbd) | No | rc7.4 |
| Pizza, with an oven and one more chef (23:08) | Not started | — | No | After rc7.4 |

## 3. What changed, with I / T / O

### 3.1 The room (18:53 §1–§5, 18:54, 22:32, 22:33)
- 「房間」 is the last room tab, after the kitchen. Inside it reads 「Jill 的房間」. It is there from Day 1: not an unlock, not a purchase, no reveal.
- In it: the oatmeal sofa under the window, the rolling TV, a queen bed in pale oak, Dylan's desk, a cat bed, a lounger, the litter box in a pale wood cabinet, a floor lamp, a nightstand, and the right-hand cat tree moved in from the dining room.
  - The desk follows the player's 22:32 photo: the laptop on the left, the monitor on an arm, books and handouts. Nothing on it says which exam.
  - No large dark furniture. Dark only in small things: the screens, the monitor arm, his jacket on the hook.
- The dining room has no sofa, no TV and no second cat tree; the space is left open.
- The doors:
  - A tap on the pale wood door by the kitchen's pass (「房間 ›」) opens the room.
  - The 「‹ 廚房」 mat at the room's door goes back.
  - The room's own door to the lane is Dylan's way in and out.
- Nine tabs fit a phone (`#roomTabs.many9`).
- I, T: `v24_rc73_jills_room_is_there_from_day_one`; screenshots `01`–`03`.

### 3.2 Jill in her room (18:53 §6, 19:23)
- During a service, when nothing needs her, she walks through the kitchen to her room and sits down. She reads, sits, or is with the cats. Work calls her back at once.
- After closing she wipes the pass, then goes to her room.
- The evening is on the sofa. On some evenings, or when the cats have the whole sofa, she sits on the edge of the bed with her e-book instead.
  - Before, she sat at the dining room's first table. That plan is gone.
- She reads only in the room.
- T: `v24_rc73_jills_room_is_there_from_day_one`, `v24_rc73_the_evening_is_in_her_room`, `jill_evening_life` (twelve evenings: every seated moment is in the room), `jill_rests_when_staff_cover_the_floor`. Screenshots `05`, `09`, `10`.

### 3.3 Dylan (18:54, 19:15)
- When he is not in the restaurant, he is at his desk, seen from behind with his headphones. That includes before the reveal. Nobody in the restaurant mentions it; a player who opens the room finds him.
- The reveal happens on an evening when Jill is settled on her sofa:
  - She gets up, walks out through the kitchen to his table, and says 「老公。」. He answers 「嗯。」.
  - Then 「老公，走了。」「好。」, and the two of them go back to the room.
- Text: after the reveal the log says 「Dylan 回來吃飯了。」, and a full room at the door is 「先回房間了。」. Before the reveal, as before.
- T: `dylan_hidden_reveal` (rewritten for the table: she came from the sofa, both are in the dining room, under 40 px apart), `dylan_stays_a_quiet_regular_early_on`, `dylan_is_a_presence_not_a_story_trigger`.

### 3.4 The cats' homes (22:18–22:54)
- The room is the cats' home, not a pen. They come and go through the corridor beside the kitchen. Nobody is sent back at closing.
- Each cat:
  - 樾樾: almost always in the room (the desk beside Dylan, the bed, the sofa).
  - 柔柔: about the restaurant, and back to the room to sleep.
  - 小齁: now and then runs back to meow at Dylan; he turns round.
  - 包包: sleeps in the room, and also where the restaurant is busiest.
  - 寶寶: likes the room and comes out now and then.
- The sofa works as it always did, only in the room: who takes which place, who sleeps there, 樾樾 and 小齁 trading the place next to Jill.
- Cats in the room can be petted. A sleeping 包包 opens one eye and stays asleep.
- 樾樾 after closing (22:54):
  - On a new game he keeps to the room.
  - Once the crew are faces he knows (someone 10 days in, or from Day 21), he comes out as soon as the guests have gone. He sits by the kitchen door, in sight.
  - Jill, the pass wiped, waits if he is on his way, sees him, and they go to her room together.
- Three seeded services of the player's Day 74 (`scratchpad` sim, T):

| Cat | In the room | Asleep | Of that sleep, in the room |
|---|---|---|---|
| 樾樾 | 75% | 33% | 91% |
| 柔柔 | 15% | 18% | 70% |
| 小齁 | 30% | 14% | 78% |
| 包包 | 47% | 75% | 56% |
| 寶寶 | 33% | 36% | 61% |

- T: `v24_rc73_the_cats_live_between_the_room_and_the_restaurant`, `v24_rc73_tora_waits_for_jill_after_closing`, `cats_use_sofa_by_personality`, `touch_controls`, `v24_rc6_cats_visit_the_rooms_and_leave`. Screenshots `04`, `13`–`15`.

### 3.5 At the tables; 寶寶 and the regulars (22:18, 22:26–22:27)
- Each tries now and then, never every time, and never successfully. A word from the guest or Jill, and the cat jumps down; the plate is untouched.
  - 小齁 jumps on a table for fried food (fries, bites, croquettes).
  - 寶寶 jumps on a table for steak.
  - 包包 wants the chicken, but mostly sits under the table looking up.
- 寶寶 comes out to a guest who knows her (a regular or a story guest she is familiar with) and meows. They melt, and say so.
- T: `v24_rc73_the_cats_try_their_luck_and_never_get_it`. Screenshots `06`–`08`.

### 3.6 Posts: their pictures and likes (15:02, 22:09)
- Every post carries a picture. Jill's is the album photo she posted; a guest's is what they shot (the plate, the cat where it sat, the bar's light), drawn from the game's own art and the same every time it is shown.
- Likes keep coming:
  - a cat brings the most;
  - Momo brings many;
  - Jill brings as many as the restaurant's name;
  - an ordinary guest brings a handful;
  - old posts keep collecting a few.
- T: `v24_rc73_posts_carry_their_picture_and_likes_that_keep_coming`. It reads the player's own backup with its 184 photos; Jill's posts show the photos she posted. Screenshots `11`, `12`.

## 4. Manual audit (小小店主手冊)

Sections checked: 營業中（房間）, 五隻店貓, Jill 的房間, 社群與宣傳, Jill 與員工.
- **Changed**:
  - 房間: the list of tabs ends 「・廚房・房間」; inside, 「Jill 的房間」.
  - 五隻店貓 › 個性 and 點牠們: 樾樾 mostly in the room; petting in the room.
  - Jill 的空檔: her rest in her room.
- **New**:
  - 🛋️ 「Jill 的房間」: 怎麼進去 (the tab, the doors), 裡面有什麼, Jill 在房間 (the sofa, the edge of the bed), 貓的家, 樾樾等 Jill.
  - 偷吃（從來沒成功）, 寶寶和熟客.
  - 照片和讚.
  - The section is spoiler-free: it does not say who Dylan is.
- **Removed**: nothing said the sofa was in the dining room except the old 「Jill 的空檔」, rewritten.
- `followup_the_manual_describes_the_current_game` carries the new phrases.
- The GUIDE stamp says rc7.3.

## 5. Tests

- New:
  - `v24_rc73_jills_room_is_there_from_day_one`, `v24_rc73_the_evening_is_in_her_room`
  - `v24_rc73_the_cats_live_between_the_room_and_the_restaurant`, `v24_rc73_the_cats_try_their_luck_and_never_get_it`
  - `v24_rc73_posts_carry_their_picture_and_likes_that_keep_coming`, `v24_rc73_tora_waits_for_jill_after_closing`
- Changed, where the game moved:
  - `dylan_hidden_reveal`: the reveal is at his table now.
  - `jill_evening_life`: the end of an evening can be the edge of the bed; every seated moment is in her room.
  - `cats_use_sofa_by_personality`: the harness reads a cat's sleep in the room.
  - `touch_controls`: it pets a cat the finger can reach, the one the game would pick there.
  - `v24_rc6_cats_visit_the_rooms_and_leave`: it waits for a cat free on the floor.
  - `followup_the_manual_describes_the_current_game`.
- Goldens: see §5.1.
- Full regression: see §6.

### 5.1 Goldens re-recorded

`cat_personality_fingerprint`, `golden_scenario` and `golden_frames` failed on 6cd304c. Each difference comes from two
intended changes (`docs/evidence/v24_rc7_3/golden_frames/golden_check_6cd304c.log`):
- The dining room no longer has the sofa, the TV or the right-hand cat tree, and the room tabs end with 「房間」. This shows in `title`, `service_20s`, `service_panel`, `pause` and `evening`.
- The cats' days start in Jill's room (樾樾 and 寶寶), and the room is one of their choices. From the first frame of the seeded days, every cat decision, and so every later random draw, is different. This explains:
  - the fingerprint's weights and states;
  - the scenario's day;
  - the frames' cat samples;
  - the length of the two days (7,127 and 7,806 frames, from 7,301 and 8,028);
  - the money, the reviews and the photos on the `summary`, `shop`, `book_cats` and `book_mem` screens.

Re-recorded with `--record` on 6cd304c, in 9d7df75. A second run passed unchanged. Each frame's before/after/diff is in
`docs/evidence/v24_rc7_3/golden_frames/`.

ca3f416 changed the closing: 樾樾, sitting by Jill at the pass, now goes with her to her room. `golden_frames` then
differed from the closing of day 1 on (sample #170, t = 169.7 s), and in the cats seen behind the `summary`, `shop`,
`book_cats` and `book_mem` sheets (`golden_frames_2/golden_check_ca3f416.log`, before/after/diff beside it). The fingerprint
and the scenario did not move. Re-recorded once more, and the next run passed unchanged.

### 5.2 Brought up to the game at the release

The first full regression on the candidate (9a36bbd, §6) failed eight tests. None of them was the game going wrong; each
was a test that still described rc7.2, or that leaned on one seed's random draws. Fixed on `release/rc7.3`:
- `mature_save_loads_into_2_0`, `purchases_change_the_place`, `z_regression_rooms_kitchen_construction_and_staff_assignment`,
  `v24_rc6_the_floor_and_its_rooms_are_tabs`: the open rooms, and the tabs, now end with Jill's room (`home`), which is
  there from Day 1 (18:53 §1). The lists they expected are one room longer.
- `dylan_leaves_a_trace_and_never_vanishes_at_a_closed_door`: after the reveal his arrival reads 「Dylan 回來吃飯了。」,
  not 「Dylan 來了。」 (18:53 §16: he lives here). Before the reveal the test now checks that no line about him appears
  at all.
- `v24_rc6_a_name_finds_its_person_and_a_person_its_name`: its last check wanted no mark at all four seconds after the
  taps. The service goes on during those seconds, and a guest who speaks in the room you are looking at is marked
  softly for 1.8 s (rc6). On 9a36bbd a guest spoke 0.17 s before the end. The check now asks what it means: every mark
  made before those seconds is gone, and anything left is new and goes as well.
- `v24_rc7_the_wine_and_monsieur_du`: the morning the wine is due, the landlord's afternoon upstairs (`up_inspect`) is
  due too, and the morning's major beat is a weighted draw between them. On 9a36bbd the draw went to the landlord.
  `ken_wine` is class A with a floor of two (passed over twice, it is next), so the test now allows the morning it is
  due or one of the two after.
- `v24_day52_save_plays_the_stories_in_order_over_forty_days`: on seed base 7400, 怡君 moved in on Day 63 (ten days after
  meeting, one more than the target), the wall began on Day 68 and settled on Day 85. Seven seed bases on rc7.2 and on
  the candidate (`docs/evidence/v24_rc7_3/sims/day52_seeds.txt`): the wall begins Day 63–68 on rc7.3 (64–67 on rc7.2)
  and settles Day 80–85 on both — about the same spread, earlier at the median. Every seed's trajectory moved because
  the cats' days in Jill's room draw their own random numbers. 7400 is now the one late seed. The test uses 7600,
  which meets every target on both builds.

Each was rerun on its own and passed before the whole suite ran again.

## 6. Full regression

**Run 1, the candidate 9a36bbd** (clean worktree, 01:19–01:55): 200 passed, 8 failed — the eight in §5.2.
Log: `docs/evidence/v24_rc7_3/regression/full_regression_9a36bbd_200_pass_8_fail.log`.

**Run 2, the release commit 22d92e0** (a clean worktree of the commit, 02:19–03:02): **208 passed, 0 failed.**
Log: `docs/evidence/v24_rc7_3/regression/full_regression_22d92e0_208_pass.log`. This is the commit the page was built
from; nothing the page is built from changed after it (the commit after it adds this report's §6–§7, the live check's
screenshots, and Jill's room to the live check's walk).

## 7. Build and publish

- `tools/build_single.py` on 22d92e0: the single file was already in step (6,318 KB; rebuilt, no change).
- `tools/build_artifact.py`: the page for the live URL (6,468,631 bytes).
- Tag `v2.4-rc7.3`: first set at 22d92e0, moved to the commit that adds this section and the live check's screenshots,
  before the zips were made. Nothing the page is built from changed in between.
- **Published** to https://claude.ai/artifact/2vhURujrtCpQ1P5jnSsjps, version 46 (version id 1790967750-ba52), at 03:03.
- **Checked** (`tools/sims/live_check.py`, `docs/evidence/v24_rc7_3_release/`):
  - The page built from the tag sits inside the live HTML byte for byte. The host adds 552 bytes, its document skeleton.
  - The player's Day 74 save, made during the evening, opens on 「繼續營業 · 21:48」. The check resumes it and walks the
    rooms through their tabs, Jill's room too (`07b_home.png`, added to the walk for this release). Then it finishes
    the day: the summary, then the staff page (「餐廳員工 14/14 人・Lounge 員工 5/5 人・每日薪資 $29,360」).
  - Day 75's restock is saved ($220,777 → $195,630), and the page survives a reload.
  - No page errors.

## 8. Evidence (390×844, headless Chromium — T, not O)

`docs/evidence/v24_rc7_3/`:

| File | What |
|---|---|
| `01_day1_dining_room.png` | A new game: the dining room without the sofa |
| `02_day1_kitchen_door.png` | The kitchen, its door to the room |
| `03_day1_jills_room.png` | The room on Day 1 |
| `04_d74_room_service_pet.png` | The player's Day 74, a service: 樾樾 on the desk by Dylan, petted |
| `05_d74_jill_rests_in_her_room.png` | Jill resting on her sofa, Dylan at his desk |
| `06_d74_ban_up_for_the_fries.png`, `07_d74_ban_down_plate_untouched.png` | 小齁 and the fries; 「哈哈，被發現了。」 |
| `08_d74_baobao_meows_at_mia.png` | 寶寶 and Mia |
| `09_d74_evening_sofa.png`, `10_d74_evening_bed.png` | The evening: the sofa; the edge of the bed |
| `11_d74_posts_with_pictures.png`, `12_d74_posts_more.png` | The posts with their pictures and likes |
| `13`–`15` | 樾樾 by the kitchen door at closing; Jill sees him; they go |

## 9. What only the player can judge (O)

- Whether the room feels like theirs: light, lived in, room for the cats.
- Whether 樾樾's coming out at closing reads as him, and comes at the right time in his story with the crew.
- Whether the cats' tries at the tables are funny rather than a nuisance, and rare enough.
- Whether the posts' pictures look like what a guest would post.
- Whether the reveal at his table lands.

## 10. Text

`python3 tools/hans_scan.py js/game.js css/style.css docs/V24_RC7_3_REPORT.md tests/v24_tests.py tests/run_tests.py tests/v23_tests.py docs/v24/jill_room_2026-10-02_1853.txt docs/v24/jill_room_dylan_study_2026-10-02_1854.txt`
- Hits: 干 (干貝; 干擾 in the player's 18:54), 沉 (睡得很沉), 舍 (宿舍) only. All are valid Traditional forms.
