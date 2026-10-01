# Release checklist — every release

Permanent from v2.3 (2026-10-01). A release is not complete until every item has been done and recorded in the
release report.

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

- [ ] Full regression: `python3 tests/run_tests.py`.
  - It takes about 40 minutes; run it in the background with a log.
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
- [ ] Publish to the **same live URL** the player uses: https://claude.ai/artifact/2vhURujrtCpQ1P5jnSsjps.
  - Saves are kept per URL.
  - Never leave the new build on a different URL while the player's normal one stays old.
