# The player's saves — QA checkpoints

Real saves from the player's iPhone, kept unchanged (tests and tools load copies into a fresh page; nothing writes
back here). They are **checkpoints**, not a matrix (the player's 05:42 testing strategy,
`docs/v24/testing_strategy_0542_2026-10-02.txt`): a save is used to reach a state quickly — a late-game feature, a
legacy migration, a bug — and each test picks the one closest to what it checks. No test runs every save through
everything; the one test that loads them all (`v24_rc6_the_floor_and_its_rooms_are_tabs`) only checks
that each loads clean.

When the player sends a new save: add it here with its era, what it is, and what it is a checkpoint for. Do not add it
to every run.

| Save | Era (when it was written) | What it is | Checkpoint for |
|---|---|---|---|
| `player_day30.json` | v2.2, no story state | the mature Day 30 game: 10 on the crew, the side room, the pass | **legacy** loading and migration; the classic mature screenshots |
| `player_day33.json` | v2.2 | 12 crew, terrace, kitchen extension, cooler | demand and stock simulations |
| `player_day35.json` | v2.2 | money $6 | money edge cases (the emergency cash) |
| `player_day39.json` | v2.2 | the side room's glass | story-day simulations (v2.3) |
| `player_day42.json`, `player_day44.json` | v2.2 | the ceiling, $207k / $156k | spare mature checkpoints (not used) |
| `player_day46.json` | v2.2 | the chandelier | social and campaign simulations |
| `player_day48.json`, `player_day49.json`, `player_day50a.json` | v2.2 | late v2.2 states | `player_day48` in one v2.3 test; the others spare |
| `player_day50b.json` | v2.3, story state, the crew counted as 1-day hires | the catwalk | **tenure migration** (legacy crew are classes, not two-day hires) |
| `player_day52.json` | v2.3 | the **mature late-game** save: 12 crew, everything downstairs bought | the long chains (怡君 → the wall → the second floor → the rooms), the economy, the v2.4 pacing simulations |
| `player_day52a.json` | v2.3 | a second Day 52 | spare |
| `player_day61.json` | v2.4 rc5 | the **newest**: the Lounge open, 14 crew, 怡君 met | rc5 / rc6 states — the second floor and the two rooms are reached from it by setting the earlier story facts (`tests/v24_tests.py` `FLOOR_TAKEN`, `PD_OPEN`; `tools/sims/v24_rooms_*.py`) |

A release's full regression covers a few representative ones through the tests that need them — fresh (a new game),
legacy (`player_day30`), mature late (`player_day52`), current (`player_day61`) — never every save × every test.
