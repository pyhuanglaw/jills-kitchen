# V18.2 working plan (living document — updated as systems land)

Base: `baseline-v18.1` (b84440a). Branch of work: main, checkpoints tagged `v18.2-wip-N`.

## Classification (sent to the player 2026-09-27)
MUST: 1 Dylan · 2/13 micro-interactions + 今日留言 · 4/5/6 regulars' lives/gifts/companions · 8/9 weather+special days · 12 rating explain/history · 14 review digest · 17/18 inventory panel + restock UI · 19 records · 20 economy · 21 price labels · 27 stock suggestion · 28 achievements · 30 perf · 34/35 tests+smoke
SHOULD: 3 complimentary · 7 VIP visits · 10 set menus · 11 hold variation · 15 themes · 16 overlap audit · 22 incidents · 25 movement · 26 waiter duties · 29 PWA
PROTOTYPE/DECIDE: 23/24 kitchen view
DEFER: outside brief; themes/set menus slip first

## Status
- [ ] 0 baseline measurement (economy, Dylan, regulars) — scratchpad/base182.py
- [ ] 1 Dylan
- [ ] 2/13 dialogue + log
- [ ] 4/5/6 regulars
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
