#!/bin/bash
# the Day 52 test on its new seed base (7000): the final game as it is, then three slowed-down versions (a FAIL is the proof)
M=${1:?the mutants directory}
cd /home/user/jills-kitchen
T=v24_day52_save_plays_the_stories_in_order_over_forty_days
echo "== the test on seed base 7000, the game of 8ded2e2 ($(git rev-parse --short HEAD) + the test's new seed; js/game.js $(git diff --quiet 8ded2e2 -- js/game.js && echo unchanged))  $(date -u +%H:%M:%S)"
timeout 1500 python3 -u tests/run_tests.py -k $T 2>&1 | grep -E "^(PASS|FAIL|OPEN)|passed|^      " | cut -c1-600
for m in yj_slow wall_slow up_on_wall; do
  echo "-- mutant $m  $(date -u +%H:%M:%S)"
  JK_GAME_JS=$M/$m.js timeout 1500 python3 -u tests/run_tests.py -k $T 2>&1 | grep -E "^(PASS|FAIL|OPEN)|passed|^      " | cut -c1-600
done
echo "== done $(date -u +%H:%M:%S)"
