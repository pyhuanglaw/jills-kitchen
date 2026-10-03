# JILL'S KITCHEN rc8 — Checkpoint C report (2026-10-03)

Checkpoint C of the player's brief of 2026-10-02 19:19 (`docs/v24/lounge_origin_madame_lin_2026-10-02_1919.txt`, §12–§17,
§21–§23, §26): the signing, the work and the opening; Madame Lin as a guest; mature-save migration; the restaurant's three
staff lists and the Lounge's own; the brass bell from her Day 1 visit.

The work was started by the original session (ff05b0a and an uncommitted working tree it could not finish: usage limit).
That workspace was restored from its backup (35 split parts, every file checksummed, the `wip/lin` bundle) and this report
finishes the checkpoint on top of it. Nothing was published.

**How this report reports** (`docs/RELEASE_CHECKLIST.md` §3): **I** implemented, **T** tested (a test or a scripted run on
the player's saves; headless Chromium screenshots at 390×844 count as T), **O** observed by the player in normal play.
Nothing here is O.

## 1. Commits

- ff05b0a — the restaurant's three lists — 廚師, 服務生, 清潔員 — each with its own places (§21–§22).
- this commit — the rest of Checkpoint C (below), the tests brought in line with it, the evidence and this report.

## 2. Implementation (I)

| Brief | What the game does |
|---|---|
| §12–§13 簽約 | After her last night the works page offers 簽約・開工 (the money then); the next opening is 《簽約》 in her bar: the contract, a pen, a ring of keys on the bar top; Jill signs; 「那就這樣。」「嗯。」; Madame Lin hands Jill the keys. Dylan came with her and says one word. |
| §13A Evan meets Dylan | After the reveal: 「Evan，這 Dylan。」「Jill 老公。」「你好。」「你好。」 Before the reveal: 「Evan，這 Jill 老公。」 — his name never on the panel; 「先生」 only as the narration's word and his name tag. Only Evan learns anything (`evan_knows_dylan`); the restaurant's reveal is untouched (§14). |
| §15 the work | Two days, the shopfront papered over (`barState()` 'reno'), then the morning card 「開幕 · The Lounge」. The bar stays where her bar was. |
| §16 Evan | On The Lounge's list from the opening day, never a recruitment card (rc7.7's rule, kept). |
| §17 Madame Lin as a guest | Some days after the opening (five or more), on an ordinary night: 「坐哪？」「隨便。」「喝什麼？」「你選。」, held, in The Lounge; she sits at the bar; after that she comes now and then. Not on a night the whole Lounge is booked (Ken's tasting, the chef's night) — see §4. |
| §21–§22 three lists | ff05b0a: chef / waiter / cleaner each have their own places; every expansion and work names its list; the Lounge's list is separate; a restaurant waiter working the Lounge floor stays a restaurant waiter. |
| §23 mature saves | `linMig`: a save from before the line keeps everything and is given the line as history — facts and beats marked retro, shown as 「更早以前」, never played, never announced. With The Lounge: the whole line to the signing. With the project but no Lounge: up to her last night (簽約・開工 next; a 「再想想」 stays one). After the tasting: the pairing wines. Past Day 1: her visit and the bell. A save made by this version is left alone. |
| §3 the bell | Her Day 1 present stays on the door; it swings and rings when a guest comes in or goes out (one ring for a busy door). |
| wording | Evan's line about Ken names Ken instead of 「他」. |
| pictures | `lin_sign` and `lin_guest` illustration slots with drawn stand-ins until the player's pictures arrive (`docs/v24/art_requests_2026-10-03_1539.md`). |

## 3. Tests (T)

The original session's last background run (71 tests) left no record of which 71. A risk-based set was run instead: the
66 tests whose names touch the Lounge, Madame Lin, staff, pools, capacity, Evan, Ken, tastings, saves and migration, and the
two goldens.

- First run: 61 passed, 5 failed. Each failure was classified before anything was changed:
  - **Real bug (fixed):** `v24_rc7_ken_hosts_his_tasting_nights` — on the Day 74 save Madame Lin's first visit as a guest was
    planned into a tasting night, took the evening's one major story slot, and Ken's first tasting never began. Her Lounge
    visits now skip nights the whole Lounge is booked (`kenNightToday()`, `cnTonight()`); §17 asks for an ordinary night.
  - **Outdated expectation (test updated, its point kept):**
    - `v24_rc8_madame_lin_next_door_on_day_one` (Checkpoint B) expected a Day 74 save to have no `lin_hello` at all;
      Checkpoint C gives it as history. It now checks that her Day 1 is history (retro) and that the scene does not play.
    - `story_state_is_empty_on_old_saves_and_stable_over_reloads` (v2.3) expected the Day 30–39 saves' story to be empty;
      they now carry only Madame Lin's Day 1 as history. It still fails on anything else.
    - `staff_learn_places_coarsely_and_veterans_stay_useful` broke at e096fcd (rc7.7): building the Lounge now puts Evan
      behind the bar, starting that day; the test added a second Evan and expected no start day. It now uses the Evan the
      build adds.
  - **Not Checkpoint C, left as it is:** `jill_rests_when_staff_cover_the_floor` — fails identically on ff05b0a and
    4a1a9b2; bisected to 66eb6cf (Checkpoint A, the Lounge as the shop next door). With a full crew Jill still sits on every
    seed measured, less than before: seed 7 / 8 / 9 → 0.09 / 0.13 / 0.27 now, against 0.46 / 0.44 on rc7.6 (the test's bound
    is 0.12–0.75). No gameplay or threshold was changed for it; whether Jill's quiet moments still read in play is for the
    player's normal play (O).
- After the fix and the updates: the five re-run, 5 passed; the set stands at 65 of 66 (the Jill test above).
- New tests from this checkpoint: `v24_rc8_the_signing_the_work_and_the_opening`, `v24_rc8_madame_lin_comes_back_as_a_guest`,
  `v24_rc8_mature_saves_get_the_line_as_history`, `v24_rc8_the_bell_rings_when_the_door_opens`; with the earlier rc8 tests
  (the shop next door, Day 1, Ken's question to Jill's decision, the staging, mature saves hearing nothing new, the three
  lists) all pass. rc7.7's (Evan from the first night, the Lounge pouring Ken's rounds, Ken's share) and the L bar pass.
- The goldens (`golden_scenario`, `golden_frames`) pass on the baselines the original session re-recorded.
- The full regression (232 tests) has not been run on this commit; it belongs to the release gate.

## 4. Simulations (T) — `docs/evidence/v24_rc8/checkpoint_c/chain/`

`tools/sims/lin_chain.py` (the lazy bot, the player's two answers given) to Madame Lin's first visit as a guest, 0 page errors:

| From | Ken asks | tasting | pairing wine | 「我做到月底」 | Ken: 不然吃完去哪 | 有點想接 | the book | 看看 | last night | 簽約 | opens | as a guest |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Day 30 save (story empty) | 31 | 35 | 36 | 45 | 46 | 47 | 49 | 50 | 57 | 58 | 60 | 66 |
| Day 52 save | (before) | 56 | 57 | 65 | 66 | 67 | 70 | 71 | 77 | 78 | 80 | 85 |

- One step a day; the order is the brief's; Evan on The Lounge's list from the opening day.
- A new game from Day 1 (`fresh_day1.json`, 200 days): her visit on Day 1, Ken's question on Day 5, and then the line waits —
  the bot never expands the restaurant (level 1 all along), so the wine, her retirement and everything after never come
  early. The Day 30 save stands in for the fresh chronology on a restaurant a player actually grew.

## 5. Evidence (T) — `docs/evidence/v24_rc8/checkpoint_c/`

`shot_cpC.py` (written for this checkpoint; the original session's script was not in its backup) checks each claim and logs
it in `log.txt` — 0 FAIL — beside the screenshots:

- c01–c03 the works page: before her last night, 簽約・開工, paid (the signing tomorrow).
- c04 《簽約》 every line, before and after the reveal; c05 the street papered over; c06 the morning card; c07 Evan on The
  Lounge's list (no card to hire him); c08 the street with The Lounge next door.
- c09 Madame Lin as a guest, every line; c10 her at the bar.
- c11 the story page 「隔壁」 on the Day 61 and Day 74 saves — 「更早以前」; c12 their staff pages, three lists and the Lounge's.
  Both saves keep every employee (name, role, start day, level), every story fact (incl. 晴 × 阿拓's), The Lounge, Dylan's
  stage and Ken's wine; a whole day plays with nothing of the line replayed.
- c13 a legacy save over a list (waiters 6/4): everyone stays, the page says so, no waiter can be hired, still all there
  after a day and a reload.
- c14 a new game: the chef's place takes no waiter and no cleaner.
- c15 Day 1: the bell rings at the door; on the Day 74 save it is still on the door after a reload.

## 6. Checklist (the player's message of 2026-10-03)

| Item | |
|---|---|
| Fresh chronology Madame Lin → wine → retirement → 看看 → signing → work → opening | T (§4) |
| Mature / legacy saves: no catch-up dump | T (tests, c11) |
| Old staff identity, tenure, history kept | T (c11–c12) |
| Over a list: grandfathered, nobody fired | T (c13; no automated test yet) |
| Chef / waiter / cleaner places independent | T (tests, c14) |
| The Lounge's list separate from the restaurant's | T (tests, c12) |
| Evan from her bar to The Lounge, never recruited | T (tests, c07) |
| Evan meets Dylan at the signing (「Evan，這 Dylan。」「Jill 老公。」「你好。」「你好。」) | T (c04) |
| The bell from Day 1 stays | T (tests, c15) |
| The Lounge a separate shop, no door from the Main Hall | T (`v24_rc8_the_lounge_is_the_shop_next_door`) |
| The kitchen supports it by the back | T (same test) |
| rc7.7 tasting service / Ken's share / L bar / summary notes | T (their tests) |

## 7. Known limitations / remaining work

- Nothing is O: the player has not played any of this.
- Pictures: `lin_hello`, `dylan_book`, `lin_viewing`, `lin_sign`, `lin_guest` show drawn stand-ins until the player's art arrives.
- `jill_rests_when_staff_cover_the_floor` fails since Checkpoint A (§3); left for normal play to judge.
- The full regression is for the release gate.
- No automated test covers a save over a list yet (the evidence script does).

**Checkpoint C: Done** (I and T as above; O pending; not published).
