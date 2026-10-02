# JILL'S KITCHEN v2.4 rc7.4 — release report (2026-10-03)

rc7.4 is built on rc7.3. It holds what the player asked for between 22:22 and 23:06 that needs no pictures: the new
story people's own looks in the game, a favourite dish and glass for the regulars and the named guests, four more bites
for the Lounge, and the Lounge's TV and sound system.

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
| Pizza, with an oven and one more cook (23:08) | Not started | — | No | Next (rc7.5) |
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
- At the bill, a guest who had their favourite is a little happier (+6). They come a little more often while it is on
  the menu.
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

## 4. Manual audit (小小店主手冊)

(filled at the release)

## 5. Tests

- New:
  - `v24_rc74_favourites_learned_in_play_and_marked_on_the_menu`
  - `v24_rc74_the_lounges_new_bites`
  - `v24_rc74_the_lounge_tv_and_its_sound`
- `followup_the_manual_describes_the_current_game`: the new phrases (favourites, the bites, the TV) and the old Bar Food
  list as a stale phrase.

(the rest filled at the release)

## 6. Full regression

(filled at the release)

## 7. Build and publish

(filled at the release)

## 8. Evidence (390×844, headless Chromium — T, not O)

(filled at the release)

## 9. What only the player can judge (O)

- Whether Evan, 沈晴 and 阿拓 read as themselves at the game's size.
- Whether the favourites are noticed, and whether a guest saying so is charming rather than repetitive.
- Whether the bites look like themselves on the plate.
- Whether two game nights a week, and two or three fans, feel right; whether the prices feel right.

## 10. Text

(filled at the release)
