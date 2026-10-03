# V18.2 working plan (living document — updated as systems land)

Base: `baseline-v18.1` (b84440a). Branch of work: main, checkpoints tagged `v18.2-wip-N`.

## Classification (sent to the player 2026-09-27)
MUST: 1 Dylan · 2/13 micro-interactions + 今日留言 · 4/5/6 regulars' lives/gifts/companions · 8/9 weather+special days · 12 rating explain/history · 14 review digest · 17/18 inventory panel + restock UI · 19 records · 20 economy · 21 price labels · 27 stock suggestion · 28 achievements · 30 perf · 34/35 tests+smoke
SHOULD: 3 complimentary · 7 VIP visits · 10 set menus · 11 hold variation · 15 themes · 16 overlap audit · 22 incidents · 25 movement · 26 waiter duties · 29 PWA
PROTOTYPE/DECIDE: 23/24 kitchen view
DEFER: outside brief; themes/set menus slip first

## Status
- [x] 0 baseline measurement — docs/playtest-v18.2/base_s7.json, perfect_s7.json (wages 4–7% of revenue at maturity; stock suggestion 15–56 emergency orders/day; Dylan 8–10 visits by D25)
- [x] 1 Dylan (wip-1) · [x] ticket identity (wip-1) · [x] soufflé hotfix → V18.1.1 published (wip-2)
- [~] 2/13 log done (wip-1); ambient micro-interactions + line variety + review tags: patch C
- [x] 4/5/6 regulars (wip-3) — moments/gifts/companions/pairs/treats/journal facts; lines fire via setTimeout so bot-mode probes under-report; verify in real-time smoke
- [ ] 8/9 weather + days
- [ ] 12/14 rating + reviews
- [ ] 17/18 inventory + restock
- [ ] 19 records
- [ ] 20/21 economy + price labels
- [ ] 27 stock suggestion
- [ ] 28 achievements
- [ ] SHOULD items
- [ ] 23 kitchen prototype decision
- [ ] tests / smoke / docs / ship

## Notes for resuming after context loss
- Patches are applied with python scripts in the scratchpad (`patch_v182*.py`), each asserting exact match counts.
- Tests: `python3 tests/run_tests.py` (39 in V18.1). Single-file: `python3 tools/build_single.py`. Lint: `node tools/lint.mjs`.
- Artifact fragment: scratchpad `mkfrag.py` → /home/claude/jills-kitchen.html → publish to existing URL.

## Added by the player during V18.2
- MUST: ticket identity (done wip-1); max-expansion dead-end audit + late-game operations upgrades (staff room +2, waiting area +2, 動線 tiers, booth tier 3); achievements 35–50 spread early/mid/mature with hidden; soufflé lock (done, V18.1.1).

## 2.0 (autonomous, user asleep) — spatial growth
Rooms: main / kitchen / side / front. Entities carry `.room`; only the viewed room is drawn; routing through doorways.
Purchases: side room 60k (+6 tables via sideTables, +2 staff, +2 menu), kitchen ext 40k/70k (+slots, multi-chef, +2 staff), terrace 25k (+3 outdoor tables, weather-dependent), cooler 30k (+80 fridge), big pass 12k, exterior: awning/sign/planters/lights/bench/seasonal/cat nook.
Status:
- [ ] R1 room architecture (state, routing, draw dispatch, tabs+badges+swipe)
- [ ] R2 kitchen room (layout, big stations, chefs, pass, fridge, Jill at pass)
- [ ] R3 side room (layout, tables, doorway, purchase)
- [ ] R4 front room (layout, street arrivals/departures, upgrades, outdoor tables)
- [ ] R5 capacity model + multi-chef + staff cap + menu cap
- [ ] R6 food: chef specials
- [ ] R7 cats/album/achievements in new spaces
- [ ] R8 migration + tests + smoke + docs + publish
