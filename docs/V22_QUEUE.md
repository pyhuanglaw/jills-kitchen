# v2.2 — the cumulative queue and its reconciliation checklist

One queue for the whole v2.2 brief plus every later addition (the four review notes, the three portrait sheets, the cat
wording rule). Later messages are additions, not replacements. Statuses: **DONE** (built, tested), **PARTIAL** (some
of the item is built; what is missing is written next to it), **DEFERRED** (intentionally not built, with the reason),
**BLOCKED** (cannot be built here, with what would unblock it), **NOT STARTED**. Silence never means implemented: every
line below is updated when the item moves, and the final report copies this table.

Baseline: `v2.1` = `da79864`. Checkpoint: `v2.2-ux-stable` (see the bottom of this file for the SHA once tagged).

The player's Day 30 save (`tests/saves/player_day30.json`) is only the mature regression fixture and the smoke test's
starting state. Nothing in v2.2 is keyed to Day 30 or to that save: every fix works for any compatible save on any
day, and the only day gates in the changed code are the game's existing ones (the tutorial's auto-provisioning on
days 1–2 in `startService` → `autoStock()`, which `orderItems`/`takeStock` respect; Dylan and the news from Day 3).

## Working rules added during v2.2

- **Visual checkpoints** (user, 2026-09-29): during long autonomous stretches, capture and inspect the relevant game
  screen whenever a player-visible change is done, when moving to a different UI/room/feature/art pass, and roughly
  every 10–15 minutes otherwise — realistic state (the Day 30 save where it fits), the affected area cropped/zoomed,
  phone + desktop for responsive work, characters at gameplay scale. A suspicious state on a screenshot is
  investigated, never cropped away (the `庫存 621/180` on a probe screenshot was a fixture that wrote the stock past
  the fridge capacity; the harness now checks `stockTotal() <= fridgeCap()` as an invariant and fixtures fill within
  the capacity). No screenshots for their own sake, no re-captures of unchanged screens, no interrupting long runs.
- **Day 30 is only a fixture**: nothing is keyed to that save or day.

## Order

1. A1–A5 (test-first) → 2. B–E → 3. A–E tests + nearby regression + Day 30 loads + normal-speed smoke → 4. tag
`v2.2-ux-stable` → 5. F–Z in the brief's priority order, portraits at Q → 6. QA, smoke, migration, performance, final
report with this checklist reconciled.

## A. Stability (priority 1)

| item | status | where | proof |
|---|---|---|---|
| A1 restock suggestion drift; failed + changes nothing and says why | DONE | `suggestStock` cached per day (`S.today.sugKey/sug`, seeded), `stockQuote`, `buyStock` atomic, `stockFailText` | `a1_failed_restock_changes_nothing_and_the_suggestion_holds_still`; failing on baseline in `docs/evidence/v22_A_tests_on_v21_baseline.log` |
| A2 no auto-buy, never negative | DONE | sold-out dishes not on offer from Day 3 (`orderItems`), `takeStock` returns false, wages `wagesPaid=min(wages,money)` + `S.wageOwed` record only | `a2_the_game_never_buys_stock_for_the_player_and_money_never_goes_negative`; design question (payroll shortfall, days 1–2 provisioning) in the report |
| A3 service → menu softlock on short phones | DONE | `#screen.dim` scrolls, lean pause menu, `.modal{flex:0 0 auto}` | `a3_the_pause_menu_is_reachable_on_a_short_phone_and_every_way_out_works` (375×553, 390×664) |
| A4 journal → album softlock + save safety | DONE | `photoSrc` patches `img[data-pid]` in place (2,509 redraws → 1), `visibilitychange`/`pagehide` checkpoint | `a4_the_album_opens_without_a_render_storm_and_progress_survives_a_kill`, `a4b_a_mid_service_checkpoint_is_consistent_and_the_day_finishes_after_it` |
| A5 side-hall money desync | DONE | `doAct` wrapper refreshes `hud(true)` when money changed; 去看看 pill returns through a real redraw | `a5_money_is_one_number_everywhere_after_the_side_hall` |
| review note 1: no debt/morale system for payroll | DONE (kept) | shortfall recorded in `S.wageOwed` only, no mechanics | report §balance |
| review note 2: speed — decide whether hand timing needs real time | DONE | zones/hold/tap scorch capped at 1.5× real time on Jill's own tray only (`updJob` `hdt`); everything else follows the speed | `d_service_speed_scales_the_whole_simulation_and_keeps_hand_timing_fair`; the exact list of real-time timers is in the report |
| review note 3: RNG tests verified, not re-recorded blindly | DONE | `docs/evidence/v22_rng_invariants.md` (cats' state fractions over 4 seeds, Dylan over 6 seeds, free-to-pet cats over 3 seeds, golden guest count) | goldens re-recorded after the evidence |
| review note 4: explicit checkpoint round trip | DONE | `a4b_…` (service → durable change → hidden → checkpoint → reload → resume → finish → save → reload) | test |

## B–E. Management clarity, pacing, rating (priorities 2–4)

| item | status | where | proof |
|---|---|---|---|
| B staff grouped by job (廚房 / 外場 / 清潔) | DONE | `GROUPS`, `.crewgrp` | `b_staff_are_grouped_by_job` |
| C restock +1 / 建議 / 補滿 respecting capacity and money | DONE | `stock`/`stockTo` actions, service `buyEmergency` +1 / 補滿 with confirm ≥ $600 | `c_restock_shortcuts_respect_both_the_fridge_and_the_money` |
| D service speed 0.75 / 1 / 1.5 / 2× coherent | DONE | `SPEEDS`, `simSpeed`, `setSpeed`, HUD clock chip, pause segment, `[`/`]` | `d_service_speed_scales_the_whole_simulation_and_keeps_hand_timing_fair` |
| E rating card hierarchy + records as chips | DONE | `ratingStory`, `.card.rating`, `.recs .rec` | `e_rating_card_is_structured_and_records_are_chips` |
| O preserve scroll on local edits (moved up because it was cheap) | DONE | anchored `keepScroll` | `o_toggling_a_dish_keeps_the_scroll_position` |

## Checkpoint gate

| step | status |
|---|---|
| A–E tests pass | DONE |
| nearby regression (full suite) | DONE — 64/66 on the first full run (`docs/evidence/v22_suite_gate.log`); the two failures were a stochastic bound (`jill_rests…`, 0.646 vs < 0.6) and raster noise inside album photos (`golden_frames` book_mem, ≤ 12 levels) — both verified against the v2.1 baseline first (`docs/evidence/v22_rng_invariants.md`), then the tests adjusted; 66/66 after |
| Day 30 save loads, opens on prep, checkpoint resumable | DONE (`day30_load.py`, `a4b_…`) |
| short normal-speed smoke on Day 30 (real time, touch, phone viewport) | DONE — 2 days, speeds 0.75/1/1.5/2× cycled, pause menu on screen, no errors (`docs/evidence/v22_smoke_gate.log`); found and fixed: the summary screen's HUD kept the pre-wage money until 去商店 (now `hud(true)` in `showSummary`, asserted in the A5 test) |
| commit + tag `v2.2-ux-stable`, `v2.1` preserved | DONE — `511f237` |

## F–Z (priorities 5–12)

| item | status | notes |
|---|---|---|
| F cat-restaurant reviews grounded in actual events | NOT STARTED | cats are the theme, never "serving" guests (user rule) |
| G dialogue/review composable variation + duplicate suppression | NOT STARTED | no runtime LLM |
| H shop taxonomy 家具與佈置 / 店舖工程 / 貓咪生活 | NOT STARTED | no tiny categories |
| I decoration much more visible | NOT STARTED | |
| I+ dining-room art direction — quieter, refined luxury (user clarification, 2026-09-29) | NOT STARTED | reduce large red/burgundy surfaces (sofa booths, banquettes, rugs, repeated upholstery) to a restrained palette (ivory, cream, oatmeal, greige, taupe, natural wood, warm stone, muted brown, a little charcoal/black metal, restrained brass, plants); keep the concrete walls, the warm beige/cream floor and carpet, the warm light, the architecture and the cosy feel; hierarchy space → food & people → cats & details → furniture → small decoration; unify upholstery families, fewer competing silhouettes, breathing room; mature = richer materials + composition, not more objects; before/after at phone scale from the Day 30 room, checkpoints during the pass; no gameplay/balance changes |
| J cat furniture tiers with behaviours, Album | NOT STARTED | no chores, cats never outside |
| K dining-room cleanup of the old kitchen strip | NOT STARTED | keep the pass / clipped tickets |
| L lightweight hospitality (常客 / Jill's Card, 招待) | NOT STARTED | defer with reasons if it does not fit |
| M set-menu sales stats | NOT STARTED | |
| N weather recommendation one-tap 加入今日菜單 | NOT STARTED | respect slots, no silent removal |
| P food/cooking polish (80 % flow / 20 % hand-feel), resume `stash@{0}` choreography | NOT STARTED | |
| Q second-gen character art + Jill recognizable + NPC portrait architecture | NOT STARTED | assets stored: `assets/portraits/` (Jill ×2, Jill/Dylan sheet ×8, regulars/staff sheet ×13); crop via `tools/portraits.py`; staff mapped to the real roster |
| R storefront art pass (rain / evening) | NOT STARTED | keep the street life, cats never outside |
| S UI hierarchy (smaller / shorter PERFECT etc.) | NOT STARTED | do not remove information |
| T 100k–300k aspirational projects, three horizons | NOT STARTED | no inflation / taxes |
| U world memory (low-frequency later acknowledgement) | NOT STARTED | |
| V regulars' small histories | NOT STARTED | Dylan is the husband; no dating progression |
| V+ Dylan presence (user clarifications, 2026-09-29 ×2) — PRESENCE, CLUE/NARRATIVE PROGRESSION and REVEAL are three separate knobs that must not share one rarity | NOT STARTED | (1) presence relatively common: ordinary visits that advance nothing (eats, orders a familiar favourite, Jill already knows his order, short casual exchange, sits quietly when she is busy, cats treat him as family from Day 1, clears his own plate/glass/chair as established, notices a change on a later visit, near closing sometimes, visits with no clue at all); regulars may notice he comes often; Jill teases his charm attempts. (2) audit the compound gates: scheduled-day probability × arrival window × rush timing × queue/full-house × Jill-idle × story eligibility × RNG — decouple where they multiply into disappearance; a visit rejected only because the room is temporarily full gets a natural same-day retry/later arrival (no seat stealing, no queue jumping, not every visit guaranteed). (3) clues accumulate in varied categories (cats-as-family, shorthand, knows where something is, stays near closing, a regular notices, Jill anticipates his order, knows a detail a customer would not), not one fragile sequence and not the same clue repeated to bump a counter; no quests/objectives. (4) the reveal stays special and low-frequency — no Day 30 deadline; the quiet reveal (「老公，走了。」「好。」) and the after-reveal pursuit stay. Not staff, no routine help, no meters/dating. Current state of the Day 30 save: stage 1, 10 visits in 28 days, `seen:{pass}` only — the Jill-idle + RNG gate on his lines and the full-house drop are the compounding gates to fix |
| Q+ Jill/Dylan world-sprite identity (user clarification, 2026-09-29) | NOT STARTED | world sprites stay lightweight Canvas (never portrait images) but must visually correspond to the supplied portraits: Jill — dark straight hair, clear fringe silhouette, head shape, chef clothing/apron, body silhouette, a few facial cues; Dylan — short dark hair silhouette, head/face silhouette, stable casual clothing (distinctive jacket/top), not dressed as staff, posture/idle cue if useful. Silhouette test at real phone world-sprite scale (locate Jill quickly; locate Dylan when present; distinguish him from male staff, generic men, named regulars) — no permanent floating name label (a temporary one on interaction is fine). Audit procedural customer looks so the strongest Jill/Dylan combinations (hair + clothing + silhouette) are reserved. Portrait ↔ world connection must read as the same character |
| W Album living history | NOT STARTED | no death / memorial framing |
| X responsive desktop | NOT STARTED | no 540 px column; mouse / keyboard / resize; no Steamworks |
| Y save compatibility with the Day 30 save | PARTIAL | loads and plays on v2.2 (A tests, smoke: two full days at normal speed, $70,588 → $207,375); every later section must keep it — re-checked before the final tag |
| Z autonomous bug fixing, no silent rebalancing | ONGOING | balance observations collected in the report, none changed |

## Required regression coverage (24 items)

restock suggestion stability ✔ · atomic restock ✔ · no auto-buy ✔ · money never negative ✔ · service → menu on short
phone ✔ · journal → album ✔ · money display across screens ✔ · staff grouping ✔ · speed coherence ✔ · rating card ✔ ·
scroll preservation ✔ · checkpoint round trip ✔ · Day 30 migration (PARTIAL: loads; final re-check pending) · weather
reco add (pending N) · staff assignment (pending) · set sales (pending M) · review duplicate suppression (pending G) ·
cat-context review (pending F) · room navigation (pending) · kitchen service (pending) · mobile touch ✔ (touch
contexts in the harness; `touch_controls`) · desktop resize (pending X) · album persistence ✔ · construction ownership
(pending).

## Tags

- `v2.1` / `stable-v2.1` = `da79864` (preserved)
- `v2.2-ux-stable` = `511f237` (2026-09-29)
