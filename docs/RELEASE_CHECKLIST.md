# Release checklist — every release

Permanent from v2.3 (2026-10-01). A release is not complete until every item has been done and recorded in the
release report.

## 0. Scope — finish everything the player asked for (2026-10-02, the player)

- Everything the player has asked for gets finished. A release is never a stopping point
  (`docs/v24/rule_finish_everything_0237_2026-10-02.txt`) — and finishing something is never a reason for a release
  (§0a).
- After a release, go straight on to the next part of what was asked (the plan's next release). Stop only when nothing
  that was asked for is left, or for a product decision only the player can make.
- 「中間不用停」 means: do not stop, and do not stop after a release either.
- Report ≠ stop (2026-10-02 06:44, `docs/v24/report_is_not_stop_0644_2026-10-02.txt`): report progress, screenshots
  and questions whenever useful, then carry on with the next defined item. A question never blocks the work that
  does not depend on it (note it as pending; take the safe, reversible default). Stop only when genuinely blocked: two
  confirmed canons contradict each other, irreversible save loss, a major product fork with no safe reversible
  default, or a missing asset with nothing else to do. The player's silence is not a pause. Keeping going never means
  inventing scope. After a release: say 「v2.4-rcN 已發布完成。」 and go straight on to the roadmap's next part.

## 0a. Publish ≠ progress — one consolidated release per batch (permanent)

The player, 2026-10-03 10:16 and 10:34 (`docs/v24/player_messages_0953_1034_2026-10-03.txt`).

- Implementation, tests, regressions, simulations and safe fixes go on autonomously. Finishing a subtask is never a
  reason to publish.
- "Publish" always means ONE consolidated release at the end of the current batch, unless the player explicitly says
  「publish this change now」.
- Publish only when all four hold:
  1. the current requested batch is complete;
  2. the full regression passes on the commit to be published (§5);
  3. migration and save compatibility are verified;
  4. the build is meaningful for the player's normal play on the iPhone.
- During the work: local and internal builds and evidence only. An intermediate version is published only when
  publishing is itself needed to test a problem specific to the host (claude.ai), and the player is told why.
- Small fixes found after a release candidate go into the next one — never one version per fix.
- 「先做不用圖的」「先做這些」「這個先處理」「可以先完成的先做」 and the like set what to implement first. They are never
  permission to publish an intermediate build.
- Why: from 2026-10-02 00:00 to 2026-10-03 09:52 there were ten publishes (v40–v49). rc7.3 + rc7.4 were one batch,
  and so were rc7.5 + rc7.6. Every publish ran the whole release — the regression, the build, the read-back, the live
  check, the report, eleven zips — and used the player's allowance for little.

## 1. Content in the release

- [ ] Release content audit table: FEATURE / FIX | STATUS | SOURCE BRANCH | IN THIS RELEASE? | WHY / WHY NOT.
- [ ] Nothing previously requested silently disappears.
  - READY work on other branches is merged.
  - NOT READY work is listed with what remains and why.
- [ ] Briefs and corrections from the player are filed verbatim under `docs/vNN/`.

## 2. The in-game manual (小小店主手冊) — mandatory, after the final merge

The manual is part of the game. Audit it against the **final** feature set, not an earlier one.

For every section, check:

1. Does the manual already describe this feature?
2. Is that description still accurate?
3. Did the access path change?
4. Did unlock conditions change?
5. Did costs, limits, effects, progression, controls or behaviour change?
6. Is a newly added system important enough that a normal player would expect the manual to explain it?
7. Did any old sentence become misleading because of this update?
8. Does it explain the feature in player language, not implementation terms?
9. Does a sentence about a space (side room, terrace, Lounge, second floor and its rooms) wait for that space? `GUIDE_WHEN` holds those gates; a new or reworded sentence about a space needs its rule.

Update the manual in the same release.

Record in the release report:

- **MANUAL AUDIT**: sections checked, sections changed, new sections added, obsolete wording removed.
- Write "no change required" only when it was actually verified.

Keep `followup_the_manual_describes_the_current_game` in step: new required phrases and stale phrases.

Update the audit stamp on `GUIDE` in `js/game.js` ("last: …").

## 3. Implemented ≠ perceived (I / T / O)

For each player-facing feature, report:

- **I** — implemented: the code is in.
- **T** — targeted test or simulation shows it works.
- **O** — a normal player can notice, understand and retrieve it.

Never promote T to O.

- Mark O as observed only after the player confirms it.
- Phone screenshots are evidence for T, not for O.
- Never claim an iPhone observation.

## 4. Text

- [ ] Traditional Chinese only, in the game, the docs and the report.
  - Scan with ICU's Hans-Hant transform (system libicu, no network): `python3 tools/hans_scan.py js/game.js index.html <new docs>`.
  - Review every hit. Valid Traditional forms such as 沉, 干貝, 宿舍 are expected.
- [ ] Dialogue follows the written rules:
  - `docs/v23/qa4_2026-10-01_dylan_dialogue.txt` for Jill × Dylan;
  - `docs/v23/dialogue_audit_2026-10-01.md` for one-time events vs habits.

## 5. Tests and saves

**Permanent (the player, 2026-10-02 22:20 and 22:22: 「你不可以跳過任何測試，你已經做過一次很危險的事了」「這個不能跳過任何測試的規定應該要永久記憶」):**
never skip a test. Every publish — a release, a hotfix, a one-line fix — runs the full regression (every test) on the
exact commit that will be published, and is published only when all of it passes. A failure is fixed and the whole
suite runs again. Targeted runs are for working, never a substitute for the full run before a publish. (rc7.1 was
published at 21:12 on targeted checks alone, and its backup box froze the player's iPhone.)


How testing runs between releases (the player's 05:42 strategy, `docs/v24/testing_strategy_0542_2026-10-02.txt`):
- After each change, run what it can affect first: its own tests, the tests of what depends on it, the closest real
  save, and the screenshots if the player sees it (`python3 tests/run_tests.py -k name1,name2`). Widen to the
  integration tests when the change is in a shared system (staff pools, the scheduler, the economy, saves).
- A failure: fix it, rerun that test, then its neighbours, then wider if needed — not the whole suite for every fix.
- The player's saves are checkpoints (`tests/saves/README.md` says what each is for), never a save × test matrix.
- The full regression is the release gate (and the gate for big shared-system changes): never skipped because the
  targeted tests passed.
- I / T / O stay apart: a passing test or a scripted run on a real save is TESTED, never OBSERVED.

- [ ] Full regression: `python3 tests/run_tests.py`.
  - It takes about 65 minutes; run it in the background with a log (in a clean worktree of the commit, so the work
    tree can keep moving).
  - Re-record goldens (`--record`) only for a change that legitimately moves them, and say which and why.
- [ ] Mature saves migrate: every fixture in `tests/saves/`, including the player's latest real save.
- [ ] Story progress and history survive save/reload: no beat fabricated, none lost, nothing announced twice.
- [ ] Phone screenshots at 390×844 from realistic saves for every player-visible change.
  - Investigate anything suspicious; do not crop it away.

## 6. Build and publish

- [ ] `python3 tools/build_single.py`.
  - The test `single_file_in_sync` checks that the single file matches.
- [ ] `python3 tools/build_artifact.py` writes the page for the live URL.
- [ ] Tag the release.
- [ ] Publish to the **same live URL** the player uses: https://claude.ai/artifact/ThXBVmarX3k8SK47Hhh8qA.
  - The live URL moved here on 2026-10-03, from v24 rc7.6 on.
    - Releases up to v24 rc7.6 went to https://claude.ai/artifact/2vhURujrtCpQ1P5jnSsjps; the release reports name that URL.
    - Saves from the old URL come over only through the in-game backup (設定・存檔).
  - Saves are kept per URL.
  - Never leave the new build on a different URL while the player's normal one stays old.
- [ ] Check the published page (from v2.4 rc5).
  - Read it back with Artifact's read action, which saves the live HTML.
  - Run `python3 tools/sims/live_check.py LIVE.html <tag> tests/saves/<the player's latest>.json docs/evidence/<release>_release`.
  - Pass: the page built from the tag sits inside the live HTML byte for byte.
  - Pass: one day plays from the player's save, and the page survives a reload with no page errors.
    - A save made during the evening (the backup writes the day's checkpoint) opens with 「繼續營業 · HH:MM」: the check resumes it, and does the restock on the next day's prep instead (from v2.4 rc6).
  - Record the published version in the release report.
- [ ] **No zips for a routine release** (the player, 2026-10-03, permanent): 「Do not generate ZIP packages for routine
  releases. GitHub is the primary source backup and version history. Generate a full offline ZIP only when explicitly
  requested or at major milestone releases.」 Push the branch (and the tag) to GitHub instead.
- [ ] Only when the player asks for it, or at a major milestone: package the release as zips, made from the tag
  (`git archive <tag>`), and send them to the player with the release reply.
  - `python3 tools/make_release_zips.py <tag> <name> <this release's evidence folder>` does all of the below and runs the source check.
  - **source**: everything but the large art, the evidence and the saves. Check it: `tools/build_single.py` and `tools/build_artifact.py` run from the unzipped copy must give files identical to the committed single file and to the published page.
  - **art**: the player's source pictures (`docs/v23` images, `assets/portraits/src`) and the full-size portrait cards (`assets/portraits/*.png`).
  - **evidence**: this release's screenshots and regression logs.
  - **saves**: `tests/saves`.
  - Keep each zip under 25 MB; split a kind into numbered parts when needed. Together the zips hold every file of the tag, except evidence that earlier releases already shipped.
