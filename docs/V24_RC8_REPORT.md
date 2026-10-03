# JILL'S KITCHEN v2.4 rc8 — release report (2026-10-03)

rc8 is built on rc7.6 (the last published version) and holds rc7.7 and the whole rc8 batch: The Lounge as the shop next
door, Madame Lin's line from Day 1 to the opening, the restaurant's three staff lists, 晴 × 阿拓's five after-work scenes,
the player's ten pictures, the cooks taking over Jill's dishes, and the story pacing check. The player's messages of
2026-10-02 19:19 to 2026-10-03.

The batch was started by the original development session (rc7.7, Checkpoints A–B, Checkpoint C's first commit and an
uncommitted working tree it could not finish: usage limit). That workspace was restored from its backup and the batch
finished on top of it (`wip/lin`). The player asked for the release: 「這個處理好就發布遊戲」 (2026-10-03).

**How this report reports** (`docs/RELEASE_CHECKLIST.md` §3):
- **I — IMPLEMENTED**: the code is in the repo, at the tag.
- **T — TESTED**: a test, or a scripted run on the player's own saves, shows it works. Screenshots taken in headless
  Chromium at 390×844 count as T.
- **O — OBSERVED**: only when the player has confirmed it in their own play. Nothing here is O yet, and nothing was
  observed on an iPhone.

**Branch, tag, page**
- Branch `wip/lin` (GitHub `pyhuanglaw/jills-kitchen`), tag `v2.4-rc8`.
- Published to the player's live URL, which moved on 2026-10-03: https://claude.ai/artifact/ThXBVmarX3k8SK47Hhh8qA (§7).
  The old URL (https://claude.ai/artifact/2vhURujrtCpQ1P5jnSsjps) keeps rc7.6; saves come over through 設定・存檔.

## 0. What the player asked for

Filed verbatim under `docs/v24/`: `lounge_origin_madame_lin_2026-10-02_1919.txt` (the Madame Lin line, The Lounge next
door, the staff lists), `art_requests_2026-10-03_1539.md`, `qing_tuo_after_work_brief_2026-10-03.txt` (晴 × 阿拓),
`player_messages_2026-10-03_cooks_pacing.txt` (Jill's rest and the cooks; the scheduler and the pacing), and the
earlier rc7.7 messages (`docs/v24/player_messages_0953_1034_2026-10-03.txt`).

## 1. Commits since rc7.6 (3b075fe, published as version 49)

| Commit | What |
|---|---|
| 27d5631, fc9fdb2 | rc7.7: the 35 portraits the game never shows out of the page again |
| e096fcd | rc7.7: Evan behind the bar from the day The Lounge is built, never hired |
| 2fc4079 | rc7.7: the Lounge's people pour Ken's rounds; Ken's share of a tasting night |
| 4412415 | rc7.7 fixes: the L closes round the bartenders; the summary's notes; Ken's share in Jill's words |
| 66eb6cf, a37c690 | Checkpoint A: The Lounge is the shop next door (the street, the back corridor) |
| 4a1a9b2 | Checkpoint B: the Madame Lin line, stories 1–6 |
| ff05b0a | Checkpoint C (1): the restaurant's three lists — 廚師, 服務生, 清潔員 |
| a95fcd2 | Checkpoint C (2): the signing, the works, the opening; Madame Lin as a guest; mature saves get the line as history; the bell (`docs/V24_RC8_CHECKPOINT_C_REPORT.md`) |
| 0d3ab73, 61a4458 | 晴 × 阿拓 after work, the five scenes (`docs/V24_RC8_QING_TUO_REPORT.md`) |
| 0d3ab73, 2c1d303, 205f9c3, 7206017, a3084b9 | the player's ten pictures |
| ec985d1 | the live URL moves to the new artifact |
| 3b4403f | the cooks take over (Jill's rest; the long-failing jill_rests test closed) |
| 5d21f20 | the scheduler's two majors a day confirmed; 晴 × 阿拓's pacing; a booked-out night's closing |
| (this report's commit) | the release report, the release evidence |

## 2. Release content audit

| Feature / fix | Status | Source branch | In this release? | Why / why not |
|---|---|---|---|---|
| rc7.7 (Evan from the first night, Ken's rounds and share, the L, the page size) | READY | wip/lin | yes | done and tested before the batch went on |
| The Lounge as the shop next door (Checkpoint A) | READY | wip/lin | yes | |
| Madame Lin, Day 1 to her last night (Checkpoint B) | READY | wip/lin | yes | |
| The signing, the works, the opening, Madame Lin as a guest, the bell, mature saves (Checkpoint C) | READY | wip/lin | yes | |
| The restaurant's three lists and The Lounge's own | READY | wip/lin | yes | |
| 晴 × 阿拓 after work, five scenes | READY | wip/lin | yes | |
| The player's ten pictures | READY | wip/lin | yes | all ten asked for are in |
| The cooks take over (a station without its cook; first plates) | READY | wip/lin | yes | the player's rule, 2026-10-03 |
| 晴 × 阿拓 pacing, the booked-night fix | READY | wip/lin | yes | the player chose 「再縮更多」 |
| The live URL move | READY | `claude/jills-kitchen-github-setup-4x7483` (8ca784b), cherry-picked as ec985d1 | yes | |
| The rc7.6 import on `main` (d0947ea) | — | main | no | the twelve rc7.6 zips as one commit, for the GitHub setup; the same game as 3b075fe, superseded by `wip/lin` |

Nothing previously requested is dropped.

## 3. What changed, with I / T / O

| Change | I | T | O |
|---|---|---|---|
| The Lounge next door: its own door on the street, no door from the Main Hall; staff and Jill by the back corridor | I | T (`v24_rc8_the_lounge_is_the_shop_next_door`, Checkpoint A evidence) | — |
| Madame Lin's line (Day 1's bell, the wine, her retirement, 看看, her last night) | I | T (rc8 tests; the Day 30/52 chains, Checkpoint C report §4) | — |
| The signing, the works, the opening; Evan meets Dylan | I | T (`v24_rc8_the_signing_the_work_and_the_opening`, c01–c08) | — |
| Madame Lin as a guest | I | T (`v24_rc8_madame_lin_comes_back_as_a_guest`, c09–c10) | — |
| Mature saves get the line as history (「更早以前」), nothing replayed | I | T (`v24_rc8_mature_saves_get_the_line_as_history`, c11–c12) | — |
| Three restaurant lists; a list over its places keeps everyone | I | T (tests, c12–c14) | — |
| The bell | I | T (`v24_rc8_the_bell_rings_when_the_door_opens`, c15) | — |
| 晴 × 阿拓, five held scenes; who knows what | I | T (`v24_rc8_qing_tuo_after_work_five_scenes`, q1–q6) | — |
| The ten pictures in their scenes and the story pages | I | T (`v24_illustrations_show_with_the_scene_and_reopen`; release screenshots) | — |
| The cooks: a cook from another station covers one with no cook; a dish's first plate is a cook's too; Jill rests when the crew has the work | I | T (`jill_rests_when_staff_cover_the_floor` and the staff tests; 0.91/0.89/0.90 of the service on seeds 7/8/9) | — |
| 晴 × 阿拓 pacing: Day 82 / 84 / 88 / 90 / 95 from the Day 74 save (was 82 / 94 / 99 / 113 / 118) | I | T (`tools/sims/story_per_day.py`, `docs/evidence/v24_rc8/qing_tuo/pacing/`) | — |
| The scenes after closing on a booked-out night too, when their people are in; 《今天喝？》 never on one | I | T (the same sim: 《晚點回去》 after Ken's tasting, Day 84) | — |
| 晴 × 阿拓 starts after Dylan's reveal (its pictures show his face; every scene keeps its picture) | I | T (`v24_rc8_qing_tuo_after_work_five_scenes`) | — |
| Jill hosts the opening (the first tenth of the service) and the end (from 88%) in the Main Hall, rests only in between; a rest still going at 88% ends; at the closing she is always up (「你就設定jill開店和關店都會在主廳歡迎和送客」) | I | T (`jill_rests…`, `v24_rc73_tora_waits_for_jill_after_closing`: 樾樾 comes out, she sees him, they go) | — |

### Jill's rest (the player: 「不要為了讓測試通過直接調高 Jill 的休息機率……讓這個長期 known failure 正式結案」)

- What Checkpoint A changed: nothing in Jill's rest. Her rest code is the same before (rc7.7) and after. On the test's
  day (a stove cook, a bar cook, nobody at the oven or the cold station) every rest ended for an oven or cold-station
  dish only she could cook, and 25–45 s passed before she could sit again. rc7.7 sat 0.46 / 0.44 / 0.12 of the service
  on seeds 7 / 8 / 9, the current build 0.09 / 0.13 / 0.27: the same mechanism, seed by seed — rc7.7's seed 9 failed
  the test's 0.12 bound too. The bisect to 66eb6cf was a seed changing sides, not a regression.
- What the player decided: 「第一次做的菜是她要做，其他時候廚師都可以自己接手」, then 「不管是不是第一次做那道菜，有廚師她就不用做」.
- **Gameplay changed** (`chefCan`, `chefCover`, `crewUpd`): a cook takes a dish Jill has never made (his level's dishes;
  the signature and the signature dessert still LV5); a station with no cook of its own today gets a cook from another
  station, a dish at a time, after his own station's. Jill is not called up for them.
- Found by the full regression on the cooks' rule: with a crew she was resting in her room at the closing on most
  evenings, and the closing kept her on the sofa (a V18 rule from when rests were rare) — so 樾樾's waiting for her at
  the kitchen door (rc7.3) no longer happened. The player: 「你就設定jill開店和關店都會在主廳歡迎和送客」 — she now hosts
  the first tenth of the service and its end (from 88%) in the Main Hall and rests only in between; at the closing she
  is always up. `v24_rc73_tora_waits_for_jill_after_closing` passes again; she still rests most of the service.
- **The test changed to the new rule, not loosened**: the lower bound from 0.12 to 0.5; the 0.75 cap (the old rule:
  oven and cold dishes hers) goes; new: a cook from another station took the oven or cold-station dishes; her own day
  (she never sits) and the tapped table (she is up at once) unchanged. Four other tests that encoded 「第一份永遠由 Jill
  親自做」 now expect the cook (each says why).

### The scheduler (the player: 「一天可以不只一個劇情，不然太慢」 — check it before the release)

- `LANE_CAP` {major 2, minor 3, v24 2} and `LANE_GAP` are rc7's and unchanged on every commit since. From the Day 74
  save over 46 days: two majors on seven days, free major slots on most of the days between 晴 × 阿拓's scenes. No
  regression and no test assumption behind it: the line's own waits (this session's, none from the brief) were the
  limit, and the line's report wrongly said 「one major a day」 — corrected.
- Shortened at the player's choice (「再縮更多」, then 「隔一天也可以」「只要予安有上班就可以吧」「包場夜打烊後店員還是可以留下
  的吧」): two days between the scenes (was five and four), one more drink of Dylan's (was two), 予安 from the day after
  she joins on one of her nights (was ten days), 沈晴 home two days after 《最近比較常》 (was five), and the four scenes
  after closing on a booked-out night too (each checks its own people).

### Two more tests from the full regression

- `cats_use_sofa_by_personality` (failing since Checkpoint B): its 16 evenings are all Day 1, which now opens with Madame
  Lin's held 《隔壁》. With the scene marked as seen the evenings are rc7.7's to the sample; the cats' code is unchanged.
  The test marks Day 1's scene as seen; its thresholds are unchanged.
- `v24_rc6_new_things_are_talked_about`: one evening (seed 331) said two words about The Lounge's new stage. Seeds 331–336
  said 5/5/4/7/5/2 before the cooks' rule and 2/5/5/6/5/4 after — the same spread. The test now plays three evenings and
  asks for three words or more on most of them.

## 4. Manual audit (小小店主手冊)

Checked against the final feature set: every section. Changed in this release:
- 房間, 員工 (the three lists, each with its own places), 調酒師 (Evan from the first night), 怎麼來的 (Madame Lin's bar
  next door, the signing and the works), 配菜的酒, Lounge I／II／III, 安安, 要有調酒師, 客人怎麼用, 晚餐後八折, Bar Food,
  Ken 的品酒夜, 結算, 廚房設備, 私人包廂 — written with rc7.7 and Checkpoints A–C, checked again.
- 做菜, 廚師, 誰來做 and the chef's card — the cooks' new rule (no more 「每道新菜的第一份永遠由 Jill 親自做」).
- Jill 的空檔, Jill 在房間 — she rests most of a staffed evening, and is in the Main Hall at the opening and the end.
- The prep screen's warning for a station with nobody says the other cooks will help.
- No new section: 晴 × 阿拓 and Madame Lin's visits are stories, not systems.
- Audit stamp on `GUIDE` updated (last: v2.4 rc8). `followup_the_manual_describes_the_current_game` passes.

## 5. Text

- `tools/hans_scan.py js/game.js index.html`: three forms, all valid Traditional (干 in 干貝, 沉, 宿舍).
- The new dialogue follows the briefs' lines (Madame Lin, 晴 × 阿拓); the four lines of work talk in 《晚點回去》 are this
  session's and the player's to change (晴 × 阿拓 report §0).

## 6. Full regression

RESULT_PLACEHOLDER

## 7. Build and publish

PUBLISH_PLACEHOLDER

## 8. Evidence (390×844, headless Chromium — T, not O)

- `docs/evidence/v24_rc8/release/` — re-shot on the release build with the player's pictures: `qing_tuo/` (the five
  scenes' key lines, the story page; `log.txt` has every line) and `checkpoint_c/` (the signing, the works, the opening,
  Madame Lin as a guest, the mature saves' pages, the lists, the bell; `log.txt` checks each claim).
- `docs/evidence/v24_rc8/checkpoint_c/`, `docs/evidence/v24_rc8/qing_tuo/` — the checkpoints' own evidence, simulations
  and regression lists; `docs/evidence/v24_rc8/qing_tuo/pacing/` — the scheduler and pacing logs.
- `docs/evidence/v24_rc8_release/` — the live check (§7).

## 9. What only the player can judge (O)

- Whether Jill resting most of a fully staffed evening reads well, and whether the cooks covering every station takes
  something away from hiring.
- 晴 × 阿拓's pace (five scenes in about three weeks of play from a Day 74 save) and the four work-talk lines.
- The ten pictures in their scenes on the phone.
- Madame Lin's line in a new game from Day 1 (the simulations played it from the Day 30 and Day 52 saves).
