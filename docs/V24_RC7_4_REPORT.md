# JILL'S KITCHEN v2.4 rc7.4 — release report (2026-10-03)

rc7.4 is built on rc7.3. It holds what the player asked for between 22:22 and 23:08 that needs no pictures: the new
story people's own looks in the game, a favourite dish and glass for the regulars and the named guests, four more bites
for the Lounge, the Lounge's TV and sound system, and the bar pizza with its oven and one more cook.

**How this report reports** (`docs/RELEASE_CHECKLIST.md` §3):
- **I — IMPLEMENTED**: the code is in the repo, at the tag.
- **T — TESTED**: a test, or a scripted run on the player's own saves, shows it works. Screenshots taken in headless
  Chromium at 390×844 count as T.
- **O — OBSERVED**: only when the player has confirmed it in their own play. Nothing here is O yet, and nothing was
  observed on an iPhone. A Chromium touch test is not an iPhone.

**Branch, tag, page**
- Branch `wip/rc7.4` (from the rc7.3 candidate; `release/rc7.3` merged in), tag `v2.4-rc7.4`.
- Published to the player's usual URL, https://claude.ai/artifact/2vhURujrtCpQ1P5jnSsjps (§7).

## 0. What the player asked for

Filed verbatim in `docs/v24/player_messages_2219_2308_2026-10-02.txt`:
- 22:22 「新的劇情有提到的人他們的頭像在遊戲裡的也要特別設計庫這個可以先發佈，就算他們的劇情還沒有發佈」
- 22:39 「……或者可不可以建立客人對某個餐點或某杯酒的特殊喜好……」 (the random menu button and no 解雇 from the same
  message went out in rc7.2)
- 23:03 「酒吧應該新增生蠔、起司條、德國豬腳」「酒吧還要有水牛城雞翅」
- 23:06 「酒吧要新增電視大的電視轉播運動比賽 / 這個就放在家具類，應該要200,000 / 然後電視的音響系統150,000」;
  「就維持酒吧的客人沒辦法點餐餐廳的餐」
- 23:07 「酒吧的菜還是可以給餐廳的廚師煮 / 但是要讓酒吧專屬的服務生去送餐」 (the carrying went out in rc7.2; the new
  bites follow it)
- 23:08 「酒吧應該可以開發披薩吧 但可能要烤爐 所以要再增加一個廚師」

## 1. Commits since rc7.3

(filled at the release)

## 2. Release content audit

| Feature / fix | Status | Branch | In rc7.4? | Why / why not |
|---|---|---|---|---|
| Evan, 沈晴 and 阿拓 look like their portraits in the game (22:22) | Done | wip/rc7.4 | Yes | |
| A favourite dish and glass for each regular and named guest (22:39) | Done | wip/rc7.4 | Yes | |
| Buffalo wings, cheese sticks, oysters, pork knuckle in the Lounge (23:03) | Done | wip/rc7.4 | Yes | |
| The Lounge's guests order only from the Lounge (23:06) | Kept | — | Yes | Unchanged; a test now checks it for the new bites |
| The Lounge's TV ($200,000) and sound system ($150,000) (23:06) | Done | wip/rc7.4 | Yes | |
| The Lounge's bites cooked by the restaurant's cooks, carried by the Lounge's own waiter (23:07) | Done in rc7.2 | — | Yes | The new bites go the same way (tested) |
| Pizza, with an oven and one more cook (23:08) | Done | wip/rc7.5, merged | Yes | Joined this release rather than waiting for its own: one full regression for both |
| Dylan's first drink, 晴×拓 Acts 2 and 5 (18:53 §9–§11) | Written | wip/qing-tuo-after-work | No | Waits for the player's pictures |
| The Madame Lin origin line, the bar next door (19:19, 19:30) | Planned | — | No | Waits for the player's pictures |

## 3. What changed, with I / T / O

### 3.1 The new story people's looks (22:22)

- **Evan**: tousled dark waves with a low, messy fringe and locks over the ears, down to the collar; stubble.
- **沈晴**: dark hair up in a loose knot at the crown, strands falling by her face; small gold hoops.
- **阿拓**: short, textured hair pushed up into points.
- Their colours, clothes and aprons are as before; only the hair, the stubble and the earrings are new.
- They show wherever these three are drawn. Their stories are not out yet.
- I: yes. T: sprite sheet beside their portraits (§8). O: not yet.

### 3.2 Favourites (22:39)

- Each regular and each named guest loves one dish and one glass (a wine, or a drink for those who do not drink wine):
  - 陳伯伯: 黃金蛋炒飯 and 錫蘭檸檬紅茶.
  - Mia: 提拉米蘇 and 拿鐵咖啡.
  - (the full list is `LOVES` in `js/game.js`; every pick is on the game's menu or wine list.)
- Nobody announces it. When a favourite is on, the guest is likely to order it and says so (「今天有蛋炒飯，太好了。」).
  When it is off, they sometimes say that instead (「今天沒有提拉米蘇啊……」).
- Once Jill has heard it:
  - the journal's 熟客 page and 店裡的人 say 「最愛 …」;
  - the menu and the Lounge's wine list mark the row 「♥ name」.
- At the bill, a guest who had their favourite is a little happier (+6).
- They do **not** come more often for it. The branch had that (a regular 20% likelier to come while the favourite is
  on), and the busier evenings held the stories back; it came out before the release (§5.2).
- A demand estimate (the stock suggestion) learns nothing.
- I: yes. T: `v24_rc74_favourites_learned_in_play_and_marked_on_the_menu` and the menu screenshot. O: not yet.

### 3.3 The Lounge's new bites (23:03, 23:06, 23:07)

| Bite | From Lounge | Station | Price |
|---|---|---|---|
| 水牛城雞翅 (wings fried, then tossed in Buffalo sauce; celery and blue cheese) | I | stove | $220 |
| 起司條 (breaded mozzarella, fried; marinara) | I | stove | $170 |
| 生蠔 (on crushed ice, opened, lemon) | II | cold station | $360 |
| 德國豬腳 (roasted to a crisp skin; sauerkraut and mustard) | III | oven | $520 |

- A save that already has the Lounge gets the ones its level allows the next morning, with one line of news, once.
- They take no menu slot, like the other bites.
- The Lounge's guests order them; nothing from the restaurant's menu, as the player kept (23:06).
- The restaurant's cooks make them. As with every new dish, Jill makes the first portion; the news says so.
- The Lounge's own waiter carries them over (23:07, from rc7.2).
- 阿拓 and the Bar 小廚／油炸站 make them faster, as they do every bite.
- I: yes. T: `v24_rc74_the_lounges_new_bites`, `cooking_every_recipe` and the recipe-shape test (every recipe finishes
  PERFECT with perfect play, in 2–5 interactions); the dish sheet (§8). O: not yet.

### 3.4 The Lounge's TV and sound system (23:06)

- In the shop, 店裡的樣子 › 家具與佈置, a new block 「Lounge 的家具」, only when there is a Lounge:
  - Lounge 大電視, $200,000, on the wall between the arch and the bar;
  - 電視音響系統, $150,000, needs the TV — two floor speakers and a sound bar. Its price shows while it waits.
- Each, bought, has its card and a look at the Lounge.
- Game nights come about twice a week (28% of days, fixed per day). On a game night the TV is on during the service:
  - two guests come for the game, three with the sound;
  - more diners stay on in the Lounge after dinner (×1.15, ×1.3 with the sound);
  - the fans order bites more often, and the fried ones (wings, cheese sticks, chicken bites, croquettes);
  - with the sound, a fan orders another glass more often.
- On other nights the sound plays music: a few more diners stay on (×1.08).
- The day's summary says 「有比賽轉播（N 位來看球）」 on the Lounge line.
- I: yes. T: `v24_rc74_the_lounge_tv_and_its_sound` and the screenshots (§8). O: not yet.

### 3.5 The bar pizza, its oven and one more cook (23:08)

- **The oven**: 「披薩烤爐」, a kitchen work (廚房設備 › 後場工程, and 店舖工程), $120,000; it needs the Lounge (without one
  the card says 「要先有 Lounge」). A brick oven built into the kitchen's back wall beside the hood, its mouth glowing,
  the flue up through the ceiling, a peel hanging beside it. Its card and a look at the kitchen when it is built.
- **One more cook**: the restaurant's list grows by one. The kitchen has a new station, 「披薩烤爐」, on the board
  (工作分配), for one cook; the next cook hired goes to it if nobody is there. With nobody at it, Jill bakes.
- **The pizza is researched, not given** (「開發」): before the oven, the recipe waits on the research list 「需要先購買
  披薩烤爐」 and nothing of it is in the lab; with the oven, the lab's pantry has 「披薩麵團」, and dough + 番茄醬汁 +
  起司 is the pizza (or buy the recipe, $3,200). The morning news of the Lounge's bites never hands it out.
- **The dish**: 酒吧披薩, $380 (cost $110), a Lounge bite (no menu slot). The bar pie: a thin crust in a round steel
  pan, the sauce, the cheese to the edge where it goes lacy and dark, pepperoni, cut in small squares (the tavern
  cut), a pinch of oregano. Four steps: the dough into the pan, the sauce (hold), the cheese and the pepperoni, into
  the oven (timing). Dressed on the counter below the oven, baked in its mouth.
- A simple dish (difficulty ●), so the cook hired for the oven (LV1) bakes it once Jill has made the first, as with
  every new dish. The Lounge's own waiter carries it. The Lounge orders it; the fans on a game night like it too.
- Where the oven sits: its glowing mouth stays clear of the HUD's right-hand chips on a phone (今日任務 above it; a
  combo badge only grazes its edge). With the HUD hidden, `21b_d74_the_oven_without_the_hud.png` shows all of it.
- I: yes. T: `v24_rc75_the_pizza_oven_one_more_cook_and_the_bar_pizza`, `cooking_every_recipe` and
  `cooking_flow_families` (the pizza finishes PERFECT with perfect play), the screenshots (§8). O: not yet.

## 4. Manual audit (小小店主手冊)

Checked against the final feature set: 熟客 and 店裡的人, 日誌's 熟客 page, 今天的菜單 and the random menu, the Lounge's
section (Bar Food, the furniture, 晚餐後八折, VIP), 家具與佈置.
- **New**: 「最愛的一道、一杯」 — everyone with a name has a favourite dish and glass; nobody announces it; what a guest
  says when it is on, and sometimes when it is off; once known, 「最愛」 in the journal and ♥ with the name on the menu
  and the wine list; they order it and are a little happier; the random menu leans to the favourites. (The branch's
  「來得勤一點」 came out with the extra visits.)
- **New**: 「電視與音響」 — where the two pieces are (家具與佈置 › Lounge 的家具), the prices, the sound needs the TV,
  about two game nights a week, the fans, staying on, music on the other nights, the summary's 「有比賽轉播」.
- **Changed**: Bar Food lists the new bites and the level each comes with (II: 生蠔; III: 德國豬腳), and points to the
  pizza.
- **New**: 「酒吧披薩」 — the oven (where, the price, the Lounge first), the research (the dough in the lab, or the
  recipe), the dish, the oven's cook on the board (the next one hired goes there), Jill when nobody is there, Jill's
  first.
- **Changed**: 廚房設備 names the pizza oven among the kitchen works; 員工 counts it among what raises the
  restaurant's list; 電視與音響 says the fans order the pizza too.
- **Changed**: the journal's 熟客 page lists 「最愛（知道以後）」.
- **Removed**: the old Bar Food list (`followup_the_manual_describes_the_current_game` keeps it as a stale phrase).
- The three new looks: no change required. The manual says how the story guests look (「有故事的客人在店裡的樣子跟
  頭像一樣」) and names Evan, 沈晴 and 阿拓 with their jobs; it describes no one's looks on the staff, and nothing in it is
  now wrong.
- The audit stamp on `GUIDE` says rc7.4.

## 5. Tests

- New:
  - `v24_rc74_favourites_learned_in_play_and_marked_on_the_menu`
  - `v24_rc74_the_lounges_new_bites`
  - `v24_rc74_the_lounge_tv_and_its_sound`
  - `v24_rc75_the_pizza_oven_one_more_cook_and_the_bar_pizza`
- `cooking_every_recipe`, `cooking_flow_families`: their kitchen now has the pizza oven, so the pizza is cooked with
  every other recipe.
- `followup_the_manual_describes_the_current_game`: the new phrases (favourites, the bites, the TV) and the old Bar Food
  list as a stale phrase.
- The first full run on the branch (1e88ded, stopped at test 32) found a real bug: Ken's favourite is Jill's signature,
  and before there is one his order threw (`loveOrdered` read the name of a dish that does not exist yet). Two story
  tests failed on it. Fixed in ddfe212: a favourite with no name yet is never missed aloud. The favourites test now
  seats Ken with no signature and checks that his order goes through without a word about it.
- The full run on 6e82c77 (the pizza in) failed nine tests (`docs/evidence/v24_rc7_4/regression/full_regression_rc74_6e82c77.log`). Three were the game:
  - **Building the Lounge handed out the pizza.** `buyLounge` unlocked every bar dish of its level, the researched
    pizza too, oven or not. Now it skips a researched dish (9aad866). Found by
    `lounge_i_content_bar_food_in_the_kitchen_wine_at_dinner_the_cast_by_name`; the pizza test now builds Lounge I on
    the Day 52 save and checks the pizza stays locked.
  - **予安's trial without 王太太.** The trial night wants the Wangs in the Lounge a little before her. When they were
    coming that evening anyway, their visit kept its own hour (here 148 s, after the piece ended at 113 s), so nobody
    said 「彈得真好」. Now a story that needs someone at an hour moves their visit to it (9aad866). Found by
    `v24_rc7_yuan_comes_to_play_the_piano`.
  - **A regular the story asked for was lost at the door.** Found tracing the forty days (§5.2): Sophie was in the plan
    for the article with 怡君 and a full room turned her away for the day, because her visit was her own, not the
    story's. Now such a visit is the story's: a full room sends her back a little later, as it does anyone the story
    asked for (57e6f80).
- The other six were tests that described rc7.3 or leaned on one seed's draws:
  - `research_is_solvable_from_visible_info`: its solver now has the Lounge and the oven, and takes a result's hint
    only for its own kind of dish (bb3d6da).
  - `lounge_i_content_…`: Lounge I gives five bites now, not three.
  - `v24_rc7_the_money`: the Day 71 menu has seven bar bites of eight (rc7.4's four came onto it).
  - `v24_rc7_2_vip_cards_and_the_lounge_after_dinner`: at half the evening every main-hall table can be taken; the test
    frees one before it seats Mia and Leo.
  - `v24_the_night_of_the_missing_cats`: back downstairs, 小齁 can go straight into the cave (hidden, in the main hall);
    the test counts that as downstairs.
  - `v24_day52_save_plays_the_stories_in_order_over_forty_days`: see §5.2.
- Goldens: §5.1.

### 5.1 Goldens

All of it is the favourites (`docs/evidence/v24_rc7_4/golden/golden_notes.txt`):
- On the branch, `golden_scenario` and `golden_frames` differed from day 2 on. With `LOVES` emptied (the harness's
  `JK_GAME_JS`), both passed: nothing else in rc7.4 changes a new game's first two days.
- Without the extra visits (the release), `golden_scenario` and the fingerprint pass against rc7.3's own baselines:
  the three days end exactly as before.
- `golden_frames` differs at one sample: day 2, t = 75 s. By the test's own steps (`gf_day2.py`), that frame on rc7.3
  and on the release: the same evening, and 陳伯伯 saying 「還好今天有黃金蛋炒飯。」 — his portrait line, his name, the
  ring at his table (`day2_t75.before/after/diff.png`).
- `tests/golden/frames.json` re-recorded (two lines, day 2's trace); the ten key screens came back byte for byte the
  same; `scenario.json` is rc7.3's. Both pass on a second run.

### 5.2 The forty days from Day 52

`docs/evidence/v24_rc7_4/sims/day52_seeds.txt`: seven seed bases on four builds, with the test's own targets.
- The branch (9aad866), with regulars likelier to come while their favourite is on: settled by Day 82 on three seeds
  of seven (six on rc7.3); the article seven days after the settlement on three (three or four days on every rc7.3
  seed). The full run's failure was one of these.
- The trace of one seed (7100): Sophie, planned with 怡君 for the article, turned away by a full room on two evenings
  — the bug above.
- With that fixed (57e6f80), the article came back to three days; the wall still began late on two seeds (68).
- Without the extra visits (the release): the wall begins Day 63–66 on all seven and settles by Day 82 within 18 days
  of beginning (79–82, median 81; rc7.3 80–85, median 80); the article three days after on all seven. Five seeds of
  seven meet every target, as on rc7.3; the two others miss 怡君's move-in by one day (it moves between seeds on every
  build).
- So the favourites stay — the orders, the lines, the marks, the bill — and the extra visits went.
- 7600 meets every target on rc7.3 and on the release, and the test keeps it.

## 6. Full regression

(filled at the release)

## 7. Build and publish

(filled at the release)

## 8. Evidence (390×844, headless Chromium — T, not O)

`docs/evidence/v24_rc7_4/` (the scripts' own logs: `evidence_log.txt`, `evidence_log_pizza.txt`). Everything from the player's Day 74 save
(`player_day74_1508.json`), saved before rc7.4:

| File | What |
|---|---|
| `01_evan_qing_tuo_beside_their_portraits.png` | Each of the three beside their portrait: the sprite at 4×, then at game size standing and seated |
| `02_d74_lounge_game_night.png`, `02b_d74_lounge_the_tv.png` | A game night: the TV on between the arch and the bar (2:1 on the screen), the speakers either side; Evan behind the bar; 3× close-up of the TV |
| `03_d74_kitchen.png` | The kitchen in service: 阿拓 on the line |
| `04_d74_menu_favourites.png` | The next morning's menu: 「♥ 陳伯伯」 beside 黃金蛋炒飯 |
| `05_d74_journal_favourites.png` | The journal's 熟客: 「最愛 黃金蛋炒飯」, 「最愛 提拉米蘇」 |
| `06_d74_wine_list_favourite.png` | The Lounge's wine list: 「♥ Sophie」 beside 黑皮諾 |
| `07_d74_morning_news_of_the_bites.png` | The morning after the update: 「Lounge 的小點多了：水牛城雞翅、起司條、生蠔、德國豬腳。……」 |
| `08_the_four_bites.png` | The four bites as served, and their pieces |
| `09_d74_lounge_bites_at_a_table.png`, `09b_d74_lounge_bites_close.png` | Wings and oysters on a Lounge table (3× close-up) |
| `10_d74_shop_lounge_furniture.png`, `10b_d74_shop_both_owned.png` | The shop: 「Lounge 的家具」, the sound's price shown while it waits; then both owned |
| `11_d74_tv_bought.png`, `11b_d74_tv_look.png` | The TV's card; the look at the Lounge |
| `13_d74_summary_game_night.png` | The summary: 「有比賽轉播（5 位來看球）」 on the Lounge line |
| `14_the_bar_pizza.png` | The bar pizza as served, and its pieces |
| `15_d74_shop_the_pizza_oven.png` | 廚房設備: the pizza oven's card, $120,000 |
| `16_d74_research_waits_for_the_oven.png` | 菜單研發: 酒吧披薩 waiting for the oven |
| `17_d74_the_oven_built.png` | The oven's card when it is built |
| `18_d74_board_the_oven_and_its_cook.png` | 工作分配: 「披薩烤爐 1/1」 with the cook just hired (老周師傅, LV1) |
| `19_d74_the_lab_finds_it.png` | The lab: 「大成功！披薩麵團＋番茄醬汁＋起司片，就是『酒吧披薩』。」 |
| `20_d74_jills_first_pizza_step1–4.png`, `20_d74_jills_first_pizza_baking.png` | Jill makes the first one: each step in the tray, then the pie in the oven's mouth |
| `21_d74_the_cook_bakes_it.png`, `21b_d74_the_oven_without_the_hud.png` | The oven's cook bakes the next one for the Lounge: the kitchen as a phone shows it, then with the HUD hidden |
| `22_d74_pizza_in_the_lounge.png`, `22b_d74_pizza_close.png` | The pizza on a Lounge table; 安安 serving (3× close-up) |

The game night in 02 and 13 is forced (the test's way: the day's coin held). Which nights are game nights is fixed per
day: from Day 74, 17 in ten weeks (Day 74 is one, then 77, 81, 85, 86, 92, 93, 96 …); over 700 days, 1.85 a week.

## 9. What only the player can judge (O)

- Whether Evan, 沈晴 and 阿拓 read as themselves at the game's size.
- Whether the favourites are noticed, and whether a guest saying so is charming rather than repetitive.
- Whether the bites look like themselves on the plate.
- Whether two game nights a week, and two or three fans, feel right; whether the prices feel right.

## 10. Text

(filled at the release)
