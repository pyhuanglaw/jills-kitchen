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

## 1. Commits since rc7.4

(filled at the release)

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
| 主廚之夜 (14:49, 22:11) | Proposed | — | No | Next; the proposal went to the player with this release |

## 3. What changed, with I / T / O

(written at the release)

## 4. Manual audit (小小店主手冊)

(written at the release)

## 5. Tests

(written at the release)

## 6. Full regression

(filled at the release)

## 7. Build and publish

(filled at the release)

## 8. Evidence (390×844, headless Chromium — T, not O)

(filled at the release)

## 9. What only the player can judge (O)

- Whether Jill reads as busy and not posing; whether the photo looks like a snapshot and not key art.
- Whether the moment is noticed at all on Day 1 (the brief: at most 「喔，好可愛。」), and whether that is right.
- Whether the history photo on a mature save looks like the restaurant they remember opening.

## 10. Text

(filled at the release)
