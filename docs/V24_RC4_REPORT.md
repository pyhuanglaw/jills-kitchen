# JILL'S KITCHEN v2.4 rc4 — release report (2026-10-01)

**Legend**
- **I** — implemented: the code is in the repo.
- **T** — tested: an automated test, a seeded simulation, or a screenshot inspected in headless Chromium at phone size.
- **O** — observed by the player on the phone. Nothing in this report is O yet; §10 is what to look at.

**Branch and builds**
- Branch: `master`. Tag: `v2.4-rc4`.
- Published to the player's usual URL, https://claude.ai/artifact/2vhURujrtCpQ1P5jnSsjps (saves live there).

**Briefs filed verbatim (`docs/v24/`)**
- The Staff Lives / 《那面牆》 / Second Floor briefs and pictures (filed before this pass), the implementation brief,
  the visual addendum, the defect-timeline correction.
- Today: the two pacing corrections, the 秀琴阿姨 canon change, the illustration continuity note, the player's four
  illustrations and five portrait sheets, the fresh-game premise (`xiuqin_from_day1_2026-10-01.txt`, 15:07) and the
  two standing requirements of 15:08 and 15:11 (`requests_1508_1511_2026-10-01.txt`).

## 1. Commits since v2.3-rc3

| Commit | What |
|---|---|
| d818ab5, fa348b1, 458ff44, b1e381e, 48002e6 | The player's briefs and corrections, filed verbatim |
| 7e409f6 | `docs/v24/AUDIT_AND_PLAN.md`: canon from the code, conflicts and decisions, architecture, chronology, releases |
| 0bfc482 | P0: 後場整理區, tenure classes, one day's presence, the walk-over, eras and narrative-time pacing, the story illustrations, name pools |
| 2682820 | P1: 怡君 and 《三個選項》, 秀琴阿姨 × Sophie / Mia, 《那面牆》; 秀琴阿姨 from Day 1; the manual, tutorial and news |
| (this) | This report and the evidence |

## 2. Release content audit

| FEATURE / FIX | STATUS | SOURCE | IN THIS RELEASE? | WHY / WHY NOT |
|---|---|---|---|---|
| P0 foundations (後場整理區, tenure, presence, walk-over, eras, illustrations, name pools) | DONE | master | Yes | rc4 = P0 + P1. Evidence in `docs/evidence/v24_p0/` |
| 怡君 and 《三個選項》 (Y1–Y6), with `yj_intro` and `yj_key` | DONE | master | Yes | P1 |
| 秀琴阿姨 × Sophie / Mia familiarity, 「喔～～」 | DONE | master | Yes | P1 (B progression) |
| 《那面牆》 (W1–W10) and the aftermath, with `wall_leak` and `wall_settled` | DONE | master | Yes | P1 |
| The player's expression portraits (秀琴阿姨 ×3, 怡君 ×2 + 2, 王先生 ×2, Mia ×1, the landlord ×3) | DONE | master | Yes (the landlord's are for P2) | Supplied today |
| 秀琴阿姨 from Day 1 (the evening helper); the first cleaner is her | DONE | master | Yes | The player, 15:07 |
| 怡君 not gated on a late day or on Sophie × Mia; A and B progressions meeting in the wall | DONE | master | Yes | The player, 15:07 |
| Manual, opening tutorial, news cover the new content | DONE | master | Yes | The player, 15:11 (§7) |
| Traditional Chinese only | CHECKED | master | Yes | The player, 15:08 (§8) |
| Pacing to the player's windows on the Day 52 save | DONE, measured | master | Yes | §4 |
| A story-update notice never covers a scene | FIXED | master | Yes | Found in the screenshot audit (§3) |
| P2 the Second Floor (room, facade, stairs, the missing cats, the lease) | NOT STARTED | — | No | rc5. The landlord's portraits are in; the era opens in the code (`up`) with nothing in it yet |
| P3 / P4 the Staff Room, the Private Dining Room | NOT STARTED | — | No | rc6 |
| P5 the other Staff Lives arcs and the outside cast (#42) | NOT STARTED | — | No | Later; nothing in rc4 contradicts them (國雄 has no lines yet) |

## 3. What was planned, what the game showed, what changed

| Planned | Observed | Changed to |
|---|---|---|
| The helper wipes at the pass (bottom of the dining room) | At 390×844 the pass is under the portrait lines, the coach and the close pill: she could not be seen | She tidies beside a table nobody is at and that is already clear, in the rows a phone shows, and moves on every 6–10 s |
| The coach names her the moment she walks in | It covered her own first line (both sit at the bottom) | It comes 6.5 s (game time) later, after her three lines |
| Her hire line as a toast | Toasts sit under the shop sheet (z-index 4 vs 20): invisible, for every purchase toast, before this pass too | A one-line scene with her face over the shop |
| A new cleaner's card says 「今天剛來」 | For her it is not true | 「今天起正式上班」 |
| In helper mode 怡君 comes at 90% of the service | A quiet evening pulled her visit forward (to ~55%); a street walker could take her place; late in the evening the fridge was often empty and she left hungry | Her visit keeps its hour (`hold`); she waits for her mother if she has finished; with an empty fridge Jill orders in one portion for her (the opening days' emergency order, 1.5×) |
| Sophie and Mia brought together for a wall beat | One was pulled forward on a quiet evening, or they sat in different rooms (the first took her usual table, the second found no free one there) | Grouped story visits keep their hour; the first of a group sits in a room with a free table for each of them |
| One major beat a day, shared | On the Day 52 save another story's major (e.g. Ken's tasting night at the start of the day) took the day 怡君 came for 《三個選項》, two to four days in a row | The day's major is held for the v2.4 beat its people came for, until it plays or until 85% of the service; the others count a miss (their priority rises) and come another day. A beat that has only that day (floor 0: Dylan on Valentine's) is never held back — an early version of the hold lost it (measured, §4) |
| The leak shows after rain; after a dry week, a night rain | The wall began Day 67–68 in dry runs | A night rain once the move has settled (four days after the key) |
| The wall needs the familiarity exchanges | In a new game that is three short talks: the wall could begin a week after 秀琴阿姨 was hired | It also needs a long acquaintance: Sophie and Mia in 8+ times each, and 秀琴阿姨 on the floor 6+ days |
| — | A story-update notice (「故事更新 怡君 & 秀琴阿姨」) sat on top of the illustration | It waits under the scene and shows when the scene closes |

## 4. Simulations (seeded; T)

**The player's Day 52 save**, forty lazy days per seed (`tools/sims/v24_pacing.py`; logs in `docs/evidence/v24_rc4/sims/`).

| Seed | 怡君 meets her mother | spare key (59–62) | the wall begins (62–66) | mediation (75–82) | Second Floor era opens (78–86) | two majors in a day | page errors |
|---|---|---|---|---|---|---|---|
| 7000 | 54 (Day 53 is Valentine's: Dylan's beat goes first) | 63 | 66 | 81 | 83 | never | 0 |
| 9100 | 53 | 61 | 65 | 81 | 83 | never | 0 |
| 4242 | 53 | 61 | 65 | 81 | 83 | never | 0 |
| 5555 | 53 | 61 | 63 | 79 | 81 | never | 0 |
| 8080 | 53 | 61 | 63 | 79 | 81 | never | 0 |

Nothing fires at the start of Day 53 (the first day played); the first v2.4 beat is 怡君's visit that evening. One
spare key is a day outside the window, because a beat that has only that day (Dylan on Valentine's) is never held
back. (A first version of the hold, without that exception, put 怡君's key on Day 61 in this seed — and Dylan's Valentine
never happened.)

**What holding the day's major costs** (the same seeds with the hold switched off, `*_nohold.log`): without it the key
comes Day 61–63, the wall Day 63–66 and the mediation Day 79–84 (two seeds past 82). The v2.3 majors that share those
days move the other way: Sophie × Mia's 「這邊也可以」 (sm_c) and the bag on the stool (sm_d) — the same people the
wall brings in —

| Seed | sm_c with the hold / without | sm_d with / without |
|---|---|---|
| 7000 | 64 / 64 | 76 / 67 |
| 9100 | 72 / 72 | 90 / 90 |
| 4242 | 72 / 89 | — / — |
| 5555 | 72 / 61 | after Day 92 / 68 |
| 8080 | 71 / 71 | — / — |

So in two of five seeds one of their beats comes 9–11 days later, in one seed 17 days earlier, in two no change. One
major a day is the player's rule; the hold only decides which story goes first on the days 怡君 or the wall's people
come. If Sophie × Mia should go first on shared days, it is a one-line change (§12).

**A new game** (`tools/sims/v24_fresh.py`, the perfect bot, a stocked fridge).

| Shop plan (seed) | 秀琴阿姨's first evening | hired | 怡君's first visit | spare key | the wall begins | where the run ended (Day 40) |
|---|---|---|---|---|---|---|
| the cleaner first, Day 4 (300) | Day 1 | Day 4 | Day 8 | Day 16 | Day 30 | the retainer (W7) |
| a waiter first, the cleaner Day 14 (300) | Day 1 | Day 14 | Day 8 | Day 16 | Day 27 | the letters (W8) |
| never a cleaner (512, 30 days) | Day 1 | — | Day 8 | Day 16 | — (it needs her on the crew) | — |

怡君 never waits on Sophie × Mia: in the third run the pair's own story had not moved at all. The wall waits for B
(Sophie and Mia in 8+ times each, her on the floor 6+ days) and settles about two and a half weeks after it begins
(in earlier runs of the same plans the wall began Day 21–27 and the mediation came on Day 38).

**Not free labour.** The same new game with and without her (`--noxqh`), Days 1–7 (before 怡君 can come): money,
revenue, tips, guests, stars and reviews identical every day, including the four days she came in. In the tests:
Day 1 with and without her — money, lifetime, summary, reviews, stats, regulars and stock identical
(`v24_xiuqin_is_there_from_day_one_and_is_not_free_labour`). `golden_frames`: the day's digest identical; only her
pixels and lines differ (`docs/evidence/v24_rc4/golden_proof.txt`).

## 5. Tests

New in `tests/v24_tests.py` (18 v2.4 tests in all):
- `v24_xiuqin_is_there_from_day_one_and_is_not_free_labour`, `v24_xiuqin_goes_home_a_while_into_the_closing`,
  `v24_the_first_cleaner_hired_is_her_and_keeps_what_she_knows`,
  `v24_yijun_comes_early_in_a_fresh_game_and_meets_her_mother_at_closing`,
  `v24_manual_tutorial_and_news_cover_the_new_content`, `v24_the_day_is_held_for_the_beat_its_people_came_for`;
- the P1 tests (stage gates, 怡君's first visit, the authored text of the wall, forty days of the Day 52 save — now
  checked against the player's windows).

Full regression (`python3 tests/run_tests.py`, 142 tests): 137 passed, 5 failed (`docs/evidence/v24_rc4/full_run.log`).
None of the five was a broken feature; each was traced:
- `purchases_change_the_place` (the terrace never got guests in the first 150 s): fails on P0 too, passes on rc3. P0's
  tenure classes make a legacy cook count as experienced, so 《第二層左邊》 now draws its coin on that save — an
  intended change that moves the day's random stream. The terrace's two-seat tables still fill (first at 181 s of
  250, when a small party comes while the rooms inside are full). The test now watches the whole service.
- `named_guests_keep_one_face_and_the_staff_have_theirs`: 怡君 is an eleventh named guest, with her card, and never in
  the random pool. Updated to say so.
- `phase7_the_arcs_run_on_real_history_and_leave_it_changed`, `phase9_the_restaurant_remembers_milestones_slots_and_small_crossovers`:
  on these saves' first v2.4 day 怡君 is coming, so the day's major is held for her (§3) and the forced v2.3 majors
  waited. The tests' own "a new day" helper now clears that hold too.
- `window_line_cats_stay_inside_and_in_sight` (two window places in one evening, needs three): over twelve seeds one
  evening finds 3–6 places, mean 4.7, the same on P0 and on rc4 (`sims/window_places_p0_vs_rc4.log`); this seed's
  evening found two. The test now watches a second evening when the first found fewer than three.
All five pass after that (`docs/evidence/v24_rc4/rerun_after_fix.log`), and every other test passed in the full run.

Goldens: `golden_frames` re-recorded (her evening on Day 1, Day 2's news line); with her switched off the code
reproduced the P0 baselines exactly; `golden_scenario` and `cat_personality_fingerprint` unchanged.

## 6. Saves

- Every player save in `tests/saves/` (Day 30 … Day 52) loads with its money, upgrades and crew; no v2.4 story fact
  exists until something is played (`v24_saves_load_and_nothing_fires_on_load`).
- The Day 52 save: the first v2.4 day is recorded when it is played; nothing fires at the very start of it; one 2.4
  note on the next prep screen, once.
- A save with no cleaner (the Day 30 save with its cleaners removed): helper mode, and the note says who comes in the
  evenings.
- Hiring the first cleaner in helper mode keeps her id (`xq`), so what she knows carries over; firing her ends the
  evenings too.

## 7. Manual audit (小小店主手冊)

Sections checked: all ten. Changed:
- **Jill 與員工**: 清潔員 (the first one is 秀琴阿姨); new 秀琴阿姨 (before the first cleaner: some evenings near
  closing, helps tidy, no tables, no guests, the game's work is still yours; the first cleaner is her, then an
  ordinary cleaner); new 晚點到 (staff late for their own reasons, said that morning; their jobs undone meanwhile;
  wage paid).
- **故事**: new 插圖 (a picture with some scenes; 「看插圖」 reopens it from the story); new 店外的生活 (family, a move;
  staff walking to a regular's table for a few words; cooks never leave the kitchen).
- **商店 → 營運升級**: 後場整理區 (P0).
- Stale wording removed: none found (「後場休息室」 is gone from the manual since P0; checked).
- Audit stamp on `GUIDE`: 「last: v2.4 rc4 …」.

The opening tutorial: Day 1 — she walks in near closing and says who she is to the place; the coach names her once
(never over the tutorial's own steps). Day 2's news. The staff tab (Day 4) says the first cleaner is her.
A save that was already going gets one 2.4 note (systems only: late arrivals, the illustrations, 後場整理區; who comes in
the evenings when there is no cleaner yet) — nobody's story is told in advance.

## 8. Text

- `python3 tools/hans_scan.py js/game.js index.html docs/v24/AUDIT_AND_PLAN.md …`: only the valid Traditional forms
  (睡得很沉, 干貝, 宿舍).
- English only in names (Sophie, Mia, Jill, Ken …), as the player allows.
- Dialogue: her evening chat is habit lines (repeatable, a small pool); her first evening and the hire line are
  one-time.

## 9. Screenshots

`docs/evidence/v24_rc4/` (README there): Day 1 with her, the coach, the closing, Day 2's news, the Day 4 staff tab, the
hire, 怡君's first visit in a new game with the player's picture, the Day 52 note, the manual.

## 10. What to look at on the phone (for O)

1. Your Day 52 save: the 2.4 note on the next prep screen; 怡君 on Day 53 or so, eating, and 秀琴阿姨 walking over.
2. Over the next week: 《三個選項》, 「她決定了」, the move (she is in late), the spare key.
3. Two to three days after the key: 《那面牆》 — the wiping, the phone call, the photos, the flat, 王先生.
4. A new game (another browser or a backup first): Day 1, near 21:15 — does she read as someone the restaurant
   already knows? Is anything she does mistaken for work you no longer have to do?

## 11. Not in this release

The Second Floor (rc5), the Staff Room and the Private Dining Room (rc6), the other Staff Lives arcs (P5).

## 12. A decision for the player

On a day when someone comes in for a due v2.4 major beat, that beat holds the day's one major slot (until it plays,
or 85% of the service). It keeps 怡君 and the wall on your windows; it can delay a Sophie × Mia beat by about a week
when both stories need the same evening (§4). The alternative is to let a story whose own people are seated go first —
the wall then lands a few days later (mediation up to Day 84 in these seeds). Say which you prefer; the default in rc4
is the hold.

