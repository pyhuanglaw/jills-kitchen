# JILL'S KITCHEN v2.4 rc7.2 — release report (2026-10-02)

rc7.2 is built on rc7 (live as version 44 since 21:44). It holds what the player asked for while playing rc7 on the
phone this evening, from 21:49 to 23:07. rc7.1 (the text-box backup that froze the iPhone) is not in it.

**How this report reports** (`docs/RELEASE_CHECKLIST.md` §3):
- **I — IMPLEMENTED**: the code is in the repo, at the tag.
- **T — TESTED**: a test, or a scripted run on the player's own saves, shows it works. Screenshots taken in headless
  Chromium at 390×844 count as T.
- **O — OBSERVED**: only when the player has confirmed it in their own play. Nothing here is O yet, and nothing was
  observed on an iPhone. A Chromium touch test is not an iPhone.

**Branch, tag, page**
- Branch `hotfix/rc7.2`, tag `v2.4-rc7.2`.
- Published to the player's usual URL, https://claude.ai/artifact/2vhURujrtCpQ1P5jnSsjps (§7).

## 0. What the player asked for

Filed verbatim in `docs/v24/`:
- `player_messages_2049_2214_2026-10-02.txt` — 20:47–22:14 (the iPhone backup incident and the evening on rc7).
- `player_messages_2219_2308_2026-10-02.txt` — 22:19–23:08.
- `jill_room_cats_2026-10-02_2218.txt` — Jill's room and the cats (22:18–22:54), for the next version.
- `refs/dylan_desk_reference_2026-10-02_2232.jpg` — Dylan's desk (22:32), for the next version.

## 1. Commits since rc7

| Commit | What |
|---|---|
| e4e2b07 | 21:49–22:14: 秀琴阿姨's first evening held; $3,000 loans; the pass takes a tap; the heart for a real regular; the 招待 chip beside the name; a line with a face answers a touch; the landlord's afternoon with the cat |
| 809465b | A portrait line's touch handler is a property, not one more listener per line (long_play_is_stable); the release checklist's permanent rule: never skip a test |
| 5e25fa1 | 22:28 the conversation log's ×; 22:29 a tap on a regular's head at a table with work waiting is that table's work |
| e6076cf | 22:38–23:07: the summary's stories open their pages; no 解雇; 🎲 隨機選菜單; the wages; the missing cats held; Sophie's pad; 晚餐後 Lounge 八折 and the VIP cards; 安安 carries the Lounge's bites |
| (see §5) | golden_frames re-recorded, the report |

## 2. Release content audit

| Feature / fix | Status | Branch | In rc7.2? | Why / why not |
|---|---|---|---|---|
| 秀琴阿姨's first evening holds the service (21:49) | Done | hotfix/rc7.2 | Yes | |
| A tap on the pass sends the plates (21:49) | Done | hotfix/rc7.2 | Yes | |
| The 招待 chip no longer over the name (21:50) | Done | hotfix/rc7.2 | Yes | |
| $3,000 loans when under $300 in the first ten days, repaid over $20,000 (21:52–21:58) | Done | hotfix/rc7.2 | Yes | |
| The heart only for a real regular (21:55) | Done | hotfix/rc7.2 | Yes | |
| A named guest's line with a face finds the table on a touch (22:07) | Done | hotfix/rc7.2 | Yes | T is Chromium touch emulation |
| The landlord's second visit: the cat runs up, Jill follows (22:13–22:14) | Done | hotfix/rc7.2 | Yes | |
| The log's × (22:28) | Done | hotfix/rc7.2 | Yes | |
| A regular's head at a busy table (22:29) | Done | hotfix/rc7.2 | Yes | |
| A story on the summary opens its page (22:38) | Done | hotfix/rc7.2 | Yes | |
| 🎲 隨機選菜單 (22:39) | Done | hotfix/rc7.2 | Yes | |
| No 解雇 (22:39) | Done | hotfix/rc7.2 | Yes | |
| The missing cats: held, both named (22:44) | Done | hotfix/rc7.2 | Yes | |
| Sophie's gift seen, and marked in the room (22:49) | Done | hotfix/rc7.2 | Yes | |
| Wages: LV5 twice (22:51) | Done | hotfix/rc7.2 | Yes | |
| 晚餐後 Lounge 八折 (23:00) | Done | hotfix/rc7.2 | Yes | |
| VIP cards and the VIP list (23:02) | Done | hotfix/rc7.2 | Yes | |
| 安安 carries the Lounge's bites (23:07) | Done | hotfix/rc7.2 | Yes | |
| Guests' favourite dish or drink (22:39) | Not started | — | No | Next version (a design of its own: who, how it shows, what it changes) |
| New Lounge bites: 生蠔、起司條、德國豬腳、水牛城雞翅 (23:03) | Not started | — | No | Next version: each needs its drawing and its cooking steps |
| Pizza by research, an oven and one more cook (23:08) | Not started | — | No | Next version, with the bites |
| The Lounge's big TV for sports ($200,000) and its sound ($150,000) (23:06) | Not started | — | No | Next version |
| Lounge guests do not order the restaurant's dishes (23:06) | Decided | — | Unchanged | The player: keep it as it is |
| Jill's room, the cats' homes, Dylan's desk (18:53–22:54) | Audited, not built | wip/room | No | Next version (no pictures needed) |
| New story people's own looks in the game (22:22) | Not started | — | No | Next version, may go before their stories |
| The Madame Lin takeover story; 沈晴 × 阿拓 (22:19) | Built in part | wip/rc8, wip/qing-tuo-after-work | No | Waits for the player's pictures (tomorrow) |
| Social posts with pictures and likes (15:02, 22:09) | Not started | — | No | Next |
| Lounge events: 鋼琴夜, 品酒會, 主廚之夜 (14:49, 22:11) | Not started | — | No | Next |
| A backup for the player's wife without a sign-in | Not solved | wip/rc7.2-newtab | No | Needs a phone test by the player; rc7's 備份到檔案 is unchanged |

## 3. What changed, with I / T / O

(Filled in below; every item: I in, T named, O not yet.)

### 3.1 秀琴阿姨's money (21:52–21:58)
- In the first ten days, whenever the day's costs would leave the till under $300, 秀琴阿姨 lends $3,000 at closing — every time. The first time is the full scene, later times a short one.
- At a summary that ends over $20,000, everything owed is paid back. No first-day gift.
- T: `v24_rc7_the_money`.

### 3.2 The service (21:49–22:29)
- Her first evening is a held scene (the service waits). T: `v24_rc7_2_xiuqin_first_evening_holds_the_service`.
- In the kitchen, a tap on the pass sends Jill out with every ready plate, oldest ticket first. T: `v24_rc7_2_a_tap_on_the_pass_sends_the_plates`.
- The ticket's heart is for a real regular (four visits); the 招待 chip sits after the name in every state. T: `v24_rc7_2_the_heart_and_the_treat_chip_on_a_ticket`.
- A named guest's line with a face, touched, goes to the table. T: `v24_rc7_2_a_named_guests_line_answers_a_touch` (Chromium touch emulation).
- The conversation log's × closes it while lines come in; a tap on a regular's head at a table with work waiting is the table's work. T: `v24_rc7_2_a_regulars_head_at_a_busy_table_and_the_log_closes`.

### 3.3 The landlord's afternoon (22:13–22:14)
- 房東 goes up for something; 寶寶 slips past his feet and runs up; Jill follows to bring her down and sees the floor. T: `v24_rc7_the_landlord_goes_up`.

### 3.4 The summary's stories (22:38)
- Each row of 今天的故事 opens the story page at that story, marked; a restaurant chapter opens at the chapter. T: `v24_rc7_2_a_story_on_the_summary_opens_its_page`.

### 3.5 The menu and the staff (22:39, 22:51)
- 🎲 隨機選菜單 above today's menu. T: `v24_rc7_2_the_random_menu`.
- No 解雇 anywhere. T: `v24_rc7_2_no_firing_and_the_wages`, `v24_the_first_cleaner_hired_is_her_and_keeps_what_she_knows`.
- Wages by level, ×1.15 / ×1.3 / ×1.5 / ×1.75 / ×2 of rc7. LV5 is twice rc7; a new hire costs 15% more.

  | Role | LV1 | LV2 | LV3 | LV4 | LV5 |
  |---|---|---|---|---|---|
  | 廚師 | 304 | 532 | 832 | 1,224 | 1,690 |
  | 服務生 | 253 | 443 | 693 | 1,020 | 1,408 |
  | 清潔員 | 190 | 332 | 520 | 765 | 1,056 |
  | 調酒師 | 405 | 709 | 1,109 | 1,632 | 2,253 |

  The Day 71 crew (nineteen, all LV5): $14,679 a day in rc7, $29,360 now. On rc7's Day 74 summary the net was +$99,612 with $14,679 of wages, so about +$85,000 with these.

### 3.6 The night of the missing cats (22:44)
- Finding 柔柔 and 小齁 gone is a held scene that ends 「柔柔和小齁都不見了。」; the open stair door is held too, and Jill calls both. T: `v24_rc7_2_the_missing_cats_stop_the_evening`.

### 3.7 Sophie's gift (22:49)
- The scene shows the pad itself on its first three lines and holds the service.
- In the dining room the pad is ringed and tagged 「Sophie 送的小貓墊」 that day and the next. A save that already has the pad shows it once from the day it is loaded.
- T: `v24_rc7_2_sophies_pad_seen_and_marked`; screenshots `sophie_pad_marked_390.png`, `sophie_pad_marked_zoom.png`.

### 3.8 Discounts and the VIP list (23:00, 23:02)

| | Restaurant | Lounge | Lounge after dinner |
|---|---|---|---|
| No card | full price | full price | 八折 |
| VIP (5 visits) | 九折 | 九折 | 八折 |
| VIP (10 visits) | 八折 | 八折 | 七折 |

- Each item is discounted and rounded to $5. A table pays at the best card at it.
- The ticket shows the rate beside the name. The summary has a VIP chip; the Lounge line gives the after-dinner discount.
- The card is given at the fifth visit and changed at the tenth, each said once.
- The journal has a VIP tab: who, which card, the day it was given, and who is one visit away.
- Saves: people who already have 5 or 10 visits have their cards ("before there were cards"), with no toast.
- With the discount known, the chance that diners stay on for the Lounge is ×1.2.
- T: `v24_rc7_2_vip_cards_and_the_lounge_after_dinner`.

### 3.9 The Lounge's bites (23:07)
- Cooked in the one kitchen. 安安, when she is in on the Lounge job, carries them. The other waiters, the bartender and the pass's 送菜 leave them to her; with her off, as before.
- T: `v24_rc7_2_the_lounges_own_waiter_carries_its_bites`.

## 4. Manual audit (小小店主手冊)

Sections checked: 營業中（上菜）, 開店前：備料與菜單, Jill 與員工, 錢不夠的時候, Lounge：留下來的地方.
- **Changed**:
  - 上菜: the pass.
  - 員工: no 解雇.
  - 薪水: the new numbers.
  - 錢不夠的時候: $3,000 each time, repaid over $20,000.
  - 安安: she carries the Lounge's bites.
- **New**: 隨機選菜單, 晚餐後八折, VIP 卡.
- **Removed**: 「訓練升級、解雇」, 「LV5 大約是剛來時的三倍」, 「秀琴阿姨會借你兩萬」, 「店站穩了，Jill 會還她」.
- `followup_the_manual_describes_the_current_game` carries the new phrases and the stale ones.
- The GUIDE stamp says rc7.2.

## 5. Tests

- New: the eleven `v24_rc7_2_*` tests above.
- Changed: `v24_rc7_the_money` (loans, wages), `v24_rc7_the_landlord_goes_up`, `v24_the_first_cleaner_hired_is_her_and_keeps_what_she_knows`, `followup_the_manual_describes_the_current_game`, and the rc7.2 test fixes from e4e2b07.
- Goldens: see §5.1.
- Full regression: see §6.

### 5.1 Goldens re-recorded

(filled at the release)

## 6. Full regression

(filled at the release)

## 7. Build and publish

(filled at the release)

## 8. Text

`python3 tools/hans_scan.py js/game.js css/style.css docs/v24/player_messages_2219_2308_2026-10-02.txt docs/v24/jill_room_cats_2026-10-02_2218.txt tests/v24_tests.py`
- Hits: 干 (干貝), 沉, 舍 (宿舍) only. All are valid Traditional forms.
