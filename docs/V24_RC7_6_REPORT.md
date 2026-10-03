# JILL'S KITCHEN v2.4 rc7.6 — release report (2026-10-03)

rc7.6 is built on rc7.5. It holds the chef's night (主廚之夜), Ken's tasting night over the whole Lounge, the Lounge's bar
turned into a longer L, and Dylan's hood in Jill's room — the player's messages of 2026-10-02 14:49 / 22:11 and of
2026-10-03 07:09–08:00.

**How this report reports** (`docs/RELEASE_CHECKLIST.md` §3):
- **I — IMPLEMENTED**: the code is in the repo, at the tag.
- **T — TESTED**: a test, or a scripted run on the player's own saves, shows it works. Screenshots taken in headless
  Chromium at 390×844 count as T.
- **O — OBSERVED**: only when the player has confirmed it in their own play. Nothing here is O yet, and nothing was
  observed on an iPhone.

**Branch, tag, page**
- Branch `wip/rc7.6-chef` (from rc7.5's candidate; rc7.5 merged in at its release), tag `v2.4-rc7.6`.
- Published to the player's usual URL, https://claude.ai/artifact/2vhURujrtCpQ1P5jnSsjps (§7).

## 0. What the player asked for

Filed verbatim: `docs/v24/player_messages_0709_0716_2026-10-03.txt`, `docs/v24/player_messages_0744_0800_2026-10-03.txt`.

- 2026-10-02 14:49 (events in the Lounge) and 22:11 「而且你不是說酒吧可以辦活動嗎？除了品酒。」 — the chef's night.
- 07:09 「可以 就是只有主廚之夜的來賓可以點餐廳的」 — the first plan approved (the bar's six for the chef's night).
- 07:44 「在房間Dylan就穿帽T一直戴著帽T帽子吧」
- 07:44 「酒吧品酒日不只吧台 整個酒吧都是品酒日的來賓可以嗎」
- 07:44 「吧檯新增L型就能增加位子」, 07:45 「而且可以變長一點」
- 08:00 「主廚之夜就是包場整間辦主廚之夜 就是讓酒吧的客人也能吃到餐廳的厲害的菜，所以整個酒吧的客人平常的酒吧的客人也可以來呀，
  只是他們來的是主廚之夜的活動，那整間都是給主廚之夜辦」 — this replaces the 07:09 plan: the whole Lounge, not the bar's six.

## 1. Commits since rc7.5

(filled at the release)

## 2. Release content audit

| Feature / fix | Status | Branch | In rc7.6? | Why / why not |
|---|---|---|---|---|
| 主廚之夜, booked out (14:49, 22:11, 08:00) | Done | wip/rc7.6-chef | Yes | |
| Ken's tasting night over the whole Lounge (07:44) | Done | wip/rc7.6-chef | Yes | |
| The bar's L, longer, nine seats (07:44–07:45) | Done | wip/rc7.6-chef | Yes | From Lounge II; Lounge I keeps its six |
| Dylan's hood up in Jill's room (07:44) | Done | wip/rc7.6-chef | Yes | |
| The evening's schedule kept in time order | Fixed | wip/rc7.6-chef | Yes | Found while measuring the chef's night: a held visit waited behind walk-ins the 「店裡突然安靜下來了」 moment had pushed back |
| Ken goes home after his night by the evening's clock | Fixed | wip/rc7.6-chef | Yes | Found in the same runs: a night that ended at closing time left him standing behind the bar under the test harness |
| 鋼琴之夜 (paid pianist, 14:49) | Already in | — | — | 予安's nights (rc7) |
| The wife's no-login backup, the picture-dependent stories, the P5 outside cast | Not started | — | No | The backup needs a phone test by the player; the stories wait for the player's pictures |

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

- Whether the L reads as an L at a glance on the phone, and whether two people one behind the other along it look right.
- Whether a booked-out evening feels like an event — the whole room set, Ken's rounds, the chef's courses one after the
  other — and whether 23 seats is the right size for it.
- Whether Dylan with his hood up still has his face (his portrait), and no longer gives the reveal away.

## 10. Text

(filled at the release)
