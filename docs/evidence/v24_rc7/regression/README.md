# rc7 full regression (190 tests) and its re-runs

- `full_regression_part1_54_tests.log`: the run on a clean worktree of 7af5df7, started 19:04; the container restarted at
  about 19:13 with 54 tests done (all passed), so the log has no summary line.
- `full_regression_part2a.log`, `full_regression_part2b.log`: the other 136, in two halves at 19:17 (same worktree).
  Together: 186 passed, 4 failed (the report's §6.1).
- `rerun_fixed_tests.log`: the three test fixes re-run on master (f84ce13).
- `bisect_day52_at_*.log`: the forty-days test at rc7's commits — caps 485c87e and tap 8800715 pass; ken 8e8d407 and
  ya 8a5b1f9 fail like 7af5df7.
- `rerun_day52_seed7400.log`: the re-seeded test on master (3836908). The seven-seed sweep on both builds is in
  `../sims/day52_seeds.txt`.
