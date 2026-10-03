# JILL'S KITCHEN v2.4 rc7.5 — release report (2026-10-03)

rc7.5 is built on rc7.4. It holds the Life Album's first photo: the player's brief of 19:31 and 「你畫吧 你有遊戲的畫面」
(19:32).

**How this report reports** (`docs/RELEASE_CHECKLIST.md` §3):
- **I — IMPLEMENTED**: the code is in the repo, at the tag.
- **T — TESTED**: a test, or a scripted run on the player's own saves, shows it works. Screenshots taken in headless
  Chromium at 390×844 count as T.
- **O — OBSERVED**: only when the player has confirmed it in their own play. Nothing here is O yet, and nothing was
  observed on an iPhone.

**Branch, tag, page**
- Branch `wip/rc7.5-album` (from rc7.4's candidate; `wip/rc7.4` merged in), tag `v2.4-rc7.5`.
- Published to the player's usual URL, https://claude.ai/artifact/2vhURujrtCpQ1P5jnSsjps (§7).

## 0. What the player asked for

- 19:31, the Life Album's origin, filed verbatim: `docs/v24/life_album_first_photo_2026-10-02_1931.txt`. In short:
  Day 1, Dylan picks up one of Jill's own instant cameras and takes her while she is busy; nobody thinks it matters;
  it is kept, protected, the album's earliest entry; a mature save gets it as history, never as news.
- 19:32 「你畫吧 你有遊戲的畫面」 — drawn with the game's own renderer, not a picture from the player.
- 07:10 「然後我一直覺得吧台人坐的太擠」 — the Lounge's bar.
- 07:13 「Dylan在書房的時候有辦法讓玩家看不出來他是Dylan嗎？就比較宅的樣子頭像一樣穿搭不同？不然揭曉前就知道了」 — Dylan in
  Jill's room. (07:09–07:16 filed verbatim: `docs/v24/player_messages_0709_0716_2026-10-03.txt`.)

## 1. Commits since rc7.4

- 9a81828 — the first photo: Day 1 as the doors open, Jill carries a pot of herbs to the window, Dylan takes her with
  one of her cameras; a mature save gets Day 1 as history; the coach and the lines never cover each other; tests.
- 18a7451, 6bdb72e — merges of `wip/rc7.4` (the released rc7.4).
- 3fff97d — the manual: the album starts on the opening day, and its limit is 240 (it said 30); the album tests read the
  history photo first; goldens re-recorded (evidence: `golden/`); this report's first draft.
- 0796082 — Dylan's home clothes in Jill's room (07:13); the bar's six stools at every level (07:10); the player's
  messages filed; the old-save and album-cap tests count the first photo apart.
- bcbe631 — the tasting test: the first night opens with half of the six stools taken, not four of eight (found by the
  full regression on 0796082: 213 passed, this one failed).
- (the report's final commit at the release)

## 2. Release content audit

| Feature / fix | Status | Branch | In rc7.5? | Why / why not |
|---|---|---|---|---|
| The first photo on Day 1 (§5–§13 of the brief) | Done | wip/rc7.5-album | Yes | |
| A mature save gets Day 1 as history (§25–§26) | Done | wip/rc7.5-album | Yes | |
| Kept for good: never rotated out by the album's limit (§16) | Done | wip/rc7.5-album | Yes | |
| The lightbox, on a phone (§19) | Checked | — | Yes | It was there; the first photo opens in it like any other (tested at 390×844) |
| One of Jill's cameras in her room (§2–§3) | Done | wip/rc7.5-album | Yes | One camera on her room's sill; the photo leans on it once there is one |
| The coach and the lines people say, at the bottom of the screen | Fixed | wip/rc7.5-album | Yes | Found at the checkpoint: on Day 1 they covered each other |
| Different film sizes (§20, optional) | Not done | — | No | Optional in the brief; every album frame is one size, and a second size means a new layout on the phone. The canon stands: Jill has several cameras |
| Madame Lin's Day 1 visit (§5, §27) | Not in the game yet | — | No | It is the Madame Lin origin, which waits for the player's pictures. The photo is its own short moment as the doors open, so the visit can come before it later |
| Dylan's home clothes (07:13) | Done | wip/rc7.5-album | Yes | The hood comes up in rc7.6 (07:44) |
| The bar: six stools at every level, a hand apart (07:10) | Done | wip/rc7.5-album | Yes | rc7.6 turns it into a longer L from Lounge II (07:44–07:45) |
| 主廚之夜 (14:49, 22:11) | Next | wip/rc7.6-chef | No | Built since; the player made it a whole-Lounge buyout at 08:00; it ships in rc7.6 |

## 3. What changed, with I / T / O

**The Life Album's first photo** (19:31, 19:32)
- **I** — On Day 1, as the doors open (Jill free, half an hour in), Jill carries a small pot of herbs to the dining
  room's window; Dylan takes her with one of her own instant cameras. The photo is the room as it was at that instant,
  drawn by the game itself without its marks (no bubbles, no name tags, no coach). Four lines — 「你拿我的相機幹嘛？」
  「拍妳。」「我根本沒在看。」「我知道。」 — and two more only when a cat is in the picture: 「牠也在。」「嗯。」 Her eyes
  are on the pot (the 'down' look), not on the camera. The pot ends on the sill and stays there. The photo is kept for
  good (`p1_first`, never rotated out by the album's limit) and is the album's first page.
- **I** — A mature save (the player's Day 74) gets Day 1 as history: the opening-day room, 包包 asleep on the bed by the
  window, Jill with the pot; at the start of the album, no news, nothing replayed.
- **I** — One of Jill's cameras on her room's sill; the photo leans on it.
- **T** — `v25_first_photo_day_one_dylan_takes_one_of_jills_cameras`, `v25_first_photo_a_mature_save_gets_day_one_as_history`;
  the album tests count it apart (`album_notes_and_journal`, `old_saves_load`, `album_store_and_viewer_v181`);
  screens 01–17 (§8).
- **O** — not yet.

**The coach and the lines at the bottom** (found at the checkpoint)
- **I** — On Day 1 the coach and the lines people say covered each other; the lines now sit above the coach.
- **T** — screen 05 (the lines at y 601–759, the coach at 768–817).

**Dylan's home clothes** (07:13)
- **I** — In Jill's room (the desk, the sofa, walking about) Dylan wears a soft grey hoodie, grey sweatpants and his
  reading glasses — the same face and hair as his portrait; in the dining room he is in the navy cardigan the restaurant
  knows. (rc7.6 puts the hood up, 07:44.)
- **T** — `screens/dylan/` (the sheet; Jill's room on the Day 52 and Day 74 saves; the desk).
- **O** — not yet.

**The Lounge's bar** (07:10)
- **I** — Six stools at every level, 30 apart (Lounge II had squeezed eight onto the same counter, shoulder to
  shoulder), the last inside a phone's view; Ken's tasting nights: six seats.
- **T** — the Lounge levels test (six stools at Lounge III); `v24_rc7_ken_hosts_his_tasting_nights` (the first night
  opens with half of the six seated); `screens/bar/` before and after.
- **O** — not yet.

## 4. Manual audit (小小店主手冊)

Audited against the final rc7.5 set.
- **Changed — 相簿**: 「每種畫面的第一張會珍藏，其他最多留 240 張（手機存不下照片時 60 張），舊的慢慢換新。相簿從開店那天開始，
  一直翻得回去。」 (it said 30; the album's real limit is 240).
- **Changed — Lounge I／II／III**: 「I：吧台六個位子（坐得開，不會肩碰肩）…II：多一張小桌、四人沙發…」.
- **Changed — Ken 的品酒夜**: 「· 6 席」.
- **No change required — Dylan's clothes**: verified, the manual says nothing of what he wears.
- **No change required — the first photo**: it is a moment, not a system; the album's own section covers where it is.
- The GUIDE stamp: `last: v2.4 rc7.5 (the album starts on the opening day; its limit said right: 240, not 30)`.
- `followup_the_manual_describes_the_current_game`: required 相簿從開店那天開始, 最多留 240 張; stale 其他最多留 30 張.

## 5. Tests

- New: `v25_first_photo_day_one_dylan_takes_one_of_jills_cameras`, `v25_first_photo_a_mature_save_gets_day_one_as_history`.
- Changed: `album_notes_and_journal` (the history photo first), `old_saves_load` (the first polaroid is 第一天),
  `album_store_and_viewer_v181` (the ordinary count leaves `first` apart), the manual test (phrases above), the Lounge
  levels test (six stools), `v24_rc7_ken_hosts_his_tasting_nights` (half of six), Ken's news (「· 6 席」).
- Goldens re-recorded for the history photo on day 2: `tests/golden/scenario.json`, `frames.json`,
  `screens/book_mem.png` — before, after and diff in `golden/` with `golden_notes.txt`.

## 6. Full regression

- **bcbe631 (the published commit): 214 passed, 0 failed** — `regression/full_regression_bcbe631.log`, a clean worktree
  of the commit, 08:28–09:09.
- 0796082: 213 passed, 1 failed — `v24_rc7_ken_hosts_his_tasting_nights` expected the first tasting night to open with
  four on the bar's stools; with six stools (07:10) it opens with half of them, three. The test was corrected (bcbe631)
  and the whole suite run again on bcbe631 — `regression/full_regression_0796082.log`.
- 3fff97d: stopped by its own processes once it had found `old_saves_load` and `album_store_and_viewer_v181` (both fixed
  in 0796082) — `regression/full_regression_rc75_3fff97d.stopped.log`.

## 7. Build and publish

- `tools/build_single.py` on bcbe631: no change to the committed single file. `tools/build_artifact.py` →
  `jills-kitchen-rc7.5.html` (6,523,267 bytes). Tag `v2.4-rc7.5`.
- Published to https://claude.ai/artifact/2vhURujrtCpQ1P5jnSsjps — **version 48** (id 1790989790-9553), 09:10.
- Read back and checked (`tools/sims/live_check.py`, `docs/evidence/v24_rc7_5_release/`): the page built from the tag is
  inside the live HTML byte for byte (the host adds its 552-byte skeleton); the player's Day 74 save opens with
  「繼續營業 · 21:48」, the evening resumes, every room photographed, the summary, the staff page, Day 75's prep and
  restock, a reload keeps DAY 75 and the money; no page errors.
- The tag moves to this report's commit (documents only; the game is bcbe631's).

## 8. Evidence (390×844, headless Chromium — T, not O)

`docs/evidence/v24_rc7_5/`:
- `screens/` 01–17 — the first photo on Day 1 (taken on the release commit, `evidence_fp.py`, its log
  `evidence_log.txt`), the history photo on Day 74, the lightbox, the camera in Jill's room; `screens/bar/` — the bar
  before and after (`shot_bar.py`); `screens/dylan/` — Dylan's home clothes (`shot_dylan_home.py`).
- `golden/` — the re-recorded golden, before/after/diff.
- `regression/` — the full regression logs (§6).

## 9. What only the player can judge (O)

- Whether Jill reads as busy and not posing; whether the photo looks like a snapshot and not key art.
- Whether the moment is noticed at all on Day 1 (the brief: at most 「喔，好可愛。」), and whether that is right.
- Whether the history photo on a mature save looks like the restaurant they remember opening.

## 10. Text

`python3 tools/hans_scan.py js/game.js index.html docs/V24_RC7_5_REPORT.md docs/v24/player_messages_0709_0716_2026-10-03.txt`:
three expected hits only — 干 (干貝), 沉 (睡得很沉), 舍 (宿舍).
