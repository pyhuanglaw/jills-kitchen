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
| F cat-restaurant reviews grounded in actual events | DONE (test `f_reviews_name_only_the_cats_the_table_actually_met`) | `catEv(g,k,c)` records what a table actually met (a cat asleep, on a perch, walking past, by the table, photographed, a child watching); `reviewText` composes open/detail/cat/close from `RV_*` pools and names that cat doing that thing; no cat line for a table that met none; tag `cat` only when used; cats never serve/accompany anyone (wording rule) |
| G dialogue/review composable variation + duplicate suppression | DONE (test `g_lines_and_reviews_do_not_repeat_themselves`) | `pickT` ring (`SAID.q` 48 in-session + `S.said` 60 across days) picks the least-recently-said line; reviews composed, retried up to 4× against `S.reviews`; weather/room/family/Jill clauses; no runtime LLM |
| H shop taxonomy 家具與佈置 / 店舖工程 / 貓咪生活 | DONE (test `h_i_k_t_shop_rooms_decoration_pass_and_dreams`) | `shopTabs` home/works/catlife + kitchen/menu/staff/sig; `SHOP_TAB_MAP` keeps old deep links; tabs unlock with the day (works ≥ 3, catlife ≥ 4) |
| I decoration much more visible | DONE (same test; checkpoints sent) | art frames under the sign, plant spots inside the visible scene (x 38–374), sconces/floor lamp with light pools, rug, tier-2 chairs, booth material — every bought decor changes the room where the player looks |
| I+ dining-room art direction — quieter, refined luxury (user clarification, 2026-09-29) | DONE — dining room (booths oatmeal/walnut/brass, rug greige, tier-2 chairs charcoal+oatmeal, pots muted; before/after idle + service in `docs/evidence/v22_art/`), storefront in R (taupe cornice, stone band, brass line; before/after), PERFECT banner in S; no gameplay/balance change | reduce large red/burgundy surfaces (sofa booths, banquettes, rugs, repeated upholstery) to a restrained palette (ivory, cream, oatmeal, greige, taupe, natural wood, warm stone, muted brown, a little charcoal/black metal, restrained brass, plants); keep the concrete walls, the warm beige/cream floor and carpet, the warm light, the architecture and the cosy feel; hierarchy space → food & people → cats & details → furniture → small decoration; unify upholstery families, fewer competing silhouettes, breathing room; mature = richer materials + composition, not more objects; before/after at phone scale from the Day 30 room, checkpoints during the pass; no gameplay/balance changes |
| J cat furniture tiers with behaviours, Album | DONE (test `j_cat_furniture_comes_in_tiers_and_the_grass_pot_is_used`) | `GEAR_TIERS` 1–3 in 貓咪生活, the grass pot (nibble → belly-up, album memo `grass`), catwalk perches (t:4) reached by `catwalkHops`; no chores/meters, cats never outside |
| K dining-room cleanup of the old kitchen strip | DONE (same test as H) | `kitchenItems()` = bus tub (sink), bell, stock board (fridge) only; heat-lamp rail on the pass; one status line; clipped tickets kept |
| L lightweight hospitality (常客 / Jill's Card, 招待) | DONE (test `l_m_n_hospitality_set_sales_and_the_weather_suggestion`) | Jill's Card: every 5th visit of a regular is a dessert on the house (`g.card`, `.jcard` dots in the book); player 招待 chip on a ticket (`[data-treat]`, 2 a day, costs one from the fridge, `R.st.treats`); ach `card` |
| M set-menu sales stats | DONE (same test) | `R.st.setN/setRev/dishRev` at the bill, `S.lastSummary.setSales`, `S.setHist` history, shown on the summary and 餐廳 tab |
| N weather recommendation one-tap 加入今日菜單 | DONE (same test) | `wxOffMenu()` + `menuAdd` action: adds only when a slot is free; a full menu is told, nothing removed silently (`.wxadd`) |
| P food/cooking polish (80 % flow / 20 % hand-feel), resume `stash@{0}` choreography | DONE (`ffc8591`, cooking tests) | the 2.1 choreography merged onto the v2.2 hand timing (`hdt`): vessel moves (pot → pan, board → plate), colander drain, pan toss, rest-and-slice, sauce at the pass; timing unchanged |
| Q second-gen character art + Jill recognizable + NPC portrait architecture | DONE (`e17b79a`, test `q_portraits_are_one_system_with_a_fallback_and_fit_a_phone`) | `PORTRAITS` (id → assets, side, tone variants) + `STAFF_PORTRAITS` (by role and hiring order, never by appearance) + `portraitOf` with a plain fallback; `tools/portraits.py` cuts the sheets (alpha kept, interiors made opaque, feathered only where a crop runs through the drawing) → `assets/portraits/*.png`, `web/*.webp`, `js/portraits.js` (802 KB, inlined in the single file); shown at the morning remark, expansion, construction card, the quiet reveal, Dylan/Jill exchanges (cards), regulars' lines (V); container-query sizing on wide stages; the 小林/Sophie sheet-order question is in the report |
| R storefront art pass (rain / evening) | DONE (`2fbf683`; before/after in `docs/evidence/v22_art/storefront_*.png`) | plaster + stone band + brass line façade, windows showing the room (a cat on the sill inside), stone-flag pavement with puddles/splashes in rain, storm rain, window/door light at dusk, doormat; the glass front project is one wide window; street life untouched |
| S UI hierarchy (smaller / shorter PERFECT etc.) | DONE (`e17b79a`) | PERFECT banner 22 px, higher, ~1 s; nothing removed |
| T 100k–300k aspirational projects, three horizons | DONE (test `h_i_k_t_…`) | `DREAMS`: glass front $100k (近, lv 4), wooden ceiling + fans $180k (中, lv 4), catwalk $300k (遠, lv 5) in 店舖工程 with their own section; effects in ambience/attraction/hot-day patience (documented, small) and in the room (`drawCeiling`, `CATWALK` perches); no inflation/taxes |
| U world memory (low-frequency later acknowledgement) | DONE (test `u_v_world_memory_and_regulars_speak_with_their_faces`) | `WORLD_MEM` reads days the save already keeps (rooms/projects `S.newRooms`, expansion `S.grewDay`, first special `S.firstSpecial`, record rainy day / record day `S.records`, the reveal `S.dylan.reveal` at stage ≥ 3); a regular with ≥ 2 visits may bring one up days later (each memory has a window), once ever, at most one a day, chance .35 at seating; the line is logged and kept in that regular's facts; nothing new is recorded |
| V regulars' small histories | DONE (same test) | every regular's line (seat moment, tier line, Jill ↔ regular exchange, world memory) is a portrait card with their supplied face (`quote` → `portraitLine`; the Wangs' lines pick 王先生 or 王太太; the person answered is beside them, dimmed); the 熟客 page shows the faces once known (`regFaceHTML`, sprite fallback); facts/notes/habits from 2.1 kept; Dylan is the husband, no dating progression |
| V+ Dylan presence (user clarifications, 2026-09-29 ×2) — PRESENCE, CLUE/NARRATIVE PROGRESSION and REVEAL are three separate knobs that must not share one rarity | DONE (test `dylan_is_a_presence_not_a_story_trigger`; audit before/after in `docs/evidence/v22_dylan_audit_*.log`: scheduled 12/12 days, entered 12/12, spoke 12/12 after vs 8/6/3 before; stage 2 eligibility untouched, reveal untouched) | (1) presence relatively common: ordinary visits that advance nothing (eats, orders a familiar favourite, Jill already knows his order, short casual exchange, sits quietly when she is busy, cats treat him as family from Day 1, clears his own plate/glass/chair as established, notices a change on a later visit, near closing sometimes, visits with no clue at all); regulars may notice he comes often; Jill teases his charm attempts. (2) audit the compound gates: scheduled-day probability × arrival window × rush timing × queue/full-house × Jill-idle × story eligibility × RNG — decouple where they multiply into disappearance; a visit rejected only because the room is temporarily full gets a natural same-day retry/later arrival (no seat stealing, no queue jumping, not every visit guaranteed). (3) clues accumulate in varied categories (cats-as-family, shorthand, knows where something is, stays near closing, a regular notices, Jill anticipates his order, knows a detail a customer would not), not one fragile sequence and not the same clue repeated to bump a counter; no quests/objectives. (4) the reveal stays special and low-frequency — no Day 30 deadline; the quiet reveal (「老公，走了。」「好。」) and the after-reveal pursuit stay. Not staff, no routine help, no meters/dating. Current state of the Day 30 save: stage 1, 10 visits in 28 days, `seen:{pass}` only — the Jill-idle + RNG gate on his lines and the full-house drop are the compounding gates to fix |
| Q+ Jill/Dylan world-sprite identity (user clarification, 2026-09-29) | DONE (`c43ed2a`, test `q_plus_world_sprites_keep_jill_and_dylan_their_own`; lineup + room before/after in `docs/evidence/v22_art/sprites_*.png`; U/V follow-up: the service call site still forced the toque — now off everywhere, the hair is her silhouette; the hat stays an option in `drawPerson`) | world sprites stay lightweight Canvas (never portrait images) but must visually correspond to the supplied portraits: Jill — dark straight hair, clear fringe silhouette, head shape, chef clothing/apron, body silhouette, a few facial cues; Dylan — short dark hair silhouette, head/face silhouette, stable casual clothing (distinctive jacket/top), not dressed as staff, posture/idle cue if useful. Silhouette test at real phone world-sprite scale (locate Jill quickly; locate Dylan when present; distinguish him from male staff, generic men, named regulars) — no permanent floating name label (a temporary one on interaction is fine). Audit procedural customer looks so the strongest Jill/Dylan combinations (hair + clothing + silhouette) are reserved. Portrait ↔ world connection must read as the same character |
| V++ 王先生 / 王太太 are two characters (user clarification, 2026-09-29 23:00) | DONE (test `wangs_are_two_people_who_usually_come_together`; checkpoint sent) | two `REGS` records (`wang` 王先生, `wangwife` 王太太; `pair`, he `lead`s the shared visit), separate portrait assets (mr_wang / mrs_wang), sprites (his: glasses, brown jacket over light blue; hers: brown bob, pink cardigan — from the portraits), visit counts, `regMem` histories, notes, world memories, tier lines, `REG_CHAT` (couple exchanges name the answerer; solo pools for each), name tags on the floor (one each, stepped apart), the tap card (the person tapped), the 熟客 rows; they usually come together to one table/one bill (`g.regs=['wang','wangwife']`, `pairName`), she is never scheduled alone, the 'alone' moment is one of them by themselves; a couple line shows both faces with the speaker lit (`quote` → `portraitLine(who,{with:other})`); the Dylan/王太太 scene is said by her with her face; a couple's review is signed by one of them; `legacyWang` migrates an old save once (she inherits the shared history; solo-visit facts stay with the right person). Never a combined couple NPC |
| Q+ follow-up: no permanent name label for Dylan | DONE | `floorTag`: Dylan's floor name shows only for ~2.6 s after a tap or a line (`g.tagT`); regulars keep their 2.1 floor tags |
| Q++ character translation (user feedback, 2026-09-30 00:26 and 00:50) — Jill and Dylan recognizable at phone scale from masses, not detail; Jill the owner-host, not staff | DONE (`sprites_q2_*.png`: the real Day 30 room at 390 wide before/after, 2× strips beside the cleaner and the chefs; test `q_plus_…` updated) | Jill: her own cream linen shirt with the sleeves rolled to the elbow (forearms show — hands-on), khaki trousers, a natural-linen half apron with the cat patch tied with a tan band, the long dark ponytail over her shoulder, the straight fringe, earrings, a bright resting face — the light warm figure in a room of darker clothes; no uniform white, no bib, no black trousers, no toque, no name label anywhere (the kitchen view's 'Jill' tag removed). Dylan: a thick tousled crop with real volume (style 9), strong brows, a long dark-navy cardigan with a collar over a white tee, a watch, a cat mug when seated; his floor name only after a tap or a line. Reserved from guests and crew: style 4 (her tail), style 9, white tops, a white tee under a cardigan, her shirt and trousers. Verified in the Day 30 room with 13 parties and staff on the floor and at the pass beside four chefs |
| W Album living history | DONE (test `w_the_album_is_a_living_history`) | the 相簿 reads forward: weeks, and inside each the things that happened to the place that week (only from days written when they happened — rooms/projects `S.newRooms`, the expansion `S.grewDay`, the first special `S.firstSpecial`, the record days, the reveal at stage ≥ 3, the regulars' facts; **the achievements' days are deliberately not used** — a save that came through a version update carries the newer achievements dated the day they were granted, e.g. the Day 30 save has 聘請第一位員工 = DAY 27), then that week's photos; the last week is this one and the page ends with 今天 … 還在繼續; the lightbox walks the same order; no memorial framing (asserted); 珍藏 tag brass, not red |
| X responsive desktop | DONE (test `x_a_desktop_window_is_used_and_the_mouse_and_keyboard_work`; before/after 1440×900 sent) | ≥ 900×560: the column is as wide as the room at that height (`desktopWidth()` = (H − HUD)/424 × (LW + 2·BGM), `html.desk`), so no dark bands and the HUD/tickets/sheets span the room; sheets ≤ 720 px centred, modals ≤ 520; room tabs positioned by scene scale (76 logical px, all sizes); mouse: pointer cursor only over tappable targets (`sceneHot`/`roomHot`, the same targets as the tap); keyboard: Space pause/resume, Escape closes dialogue → lightbox → sheet/pause (or pauses), Enter/Space steps a dialogue, plus the existing 1–4/←→ rooms and [ ] speed; resize mid-service re-lays out (tested 1440 → 1000 → 390); below 900 px the phone layout is untouched; no Steamworks |
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
