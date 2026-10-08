The first three days (2026-10-08 evening). docs/cooking/WORKFLOW_B_ACCEPTANCE.md 「Day 1–3 驗收」 reads these.

cash_500.jsonl, cash_1200.jsonl — tools/sims/onboarding_cash.py: the money at each moment of Days 1–3 with $500 and $1,200
  at the start (two seeds; a player who takes the suggested stock and one who buys half again as much).

days_1_3*.jsonl — tools/sims/onboarding_days.py: a fresh game, Days 1–3, seeds 101/202/303, two players: 'lazy' (leaves to
  the staff and 秀琴阿姨 what they cover, taps the rest: the tests' LAZY_ACTOR) and 'every' (taps everything: the tests'
  perfect bot). One line per evening: what each dish went through (menu_steps), the guests, the money, the dirty dishes
  (in, washed and by whom, the most at once, seconds full, times full, table-seconds waiting on a full cart, seconds
  washing), 秀琴阿姨's evening (idle / clear / walk / wash seconds) and Jill on the floor (idle / table / dish seconds).
  - days_1_3.jsonl            8ef21cf + (the onboarding: Day 3 the salad, $1,200)
  - days_1_3_cap999.jsonl     the same with a cart that never fills (--js "DD_CAP[0]=999")
  - days_1_3_d4bbb4b.jsonl    before the onboarding change (Day 3 the pasta, $500), with the dirty dishes
  - days_1_3_b8d0256.jsonl    before the dirty dishes (Day 3 the pasta, $500): clearing a table makes its plates vanish
  The table: python3 tools/sims/onboarding_days_table.py FILE...
