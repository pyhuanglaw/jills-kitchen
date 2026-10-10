#!/bin/bash
# The tests changed or added after the user's iPhone reports (2026-10-10): on the game as it is (they pass), on the game before
# the reports (8ded2e2: the ones about the reports fail), and on broken versions of today's game (each fails its test).
# bash run.sh MUTDIR OLDGAMEJS
M=${1:?mutants dir}; OLD=${2:?8ded2e2 game.js}
cd /home/user/jills-kitchen
F='^(PASS|FAIL|OPEN)|passed|^      '
CH=cooking_jill_and_the_cooks_hand_work_on,cooking_a_cook_on_standby_rests_and_his_card_counts_his_dishes,cooking_plating_happens_where_the_food_is,cooking_a_full_place_is_a_quiet_wait,qa_the_task_list_opens_under_its_chip_and_any_tap_puts_it_away,qa_the_kitchen_chips_never_sit_on_the_counters
echo "== the game as it is ($(git rev-parse --short HEAD); js/game.js as 6bf5002: $(git diff --quiet 6bf5002 -- js/game.js css/style.css && echo yes))  $(date -u +%H:%M:%S)"
timeout 1800 python3 -u tests/run_tests.py -k $CH 2>&1 | grep -E "$F" | cut -c1-400
echo "== the game before the reports (8ded2e2's js/game.js)  $(date -u +%H:%M:%S)"
JK_GAME_JS=$OLD timeout 1800 python3 -u tests/run_tests.py -k $CH 2>&1 | grep -E "$F" | cut -c1-400
run() { echo "-- $1 -> $2  $(date -u +%H:%M:%S)"; JK_GAME_JS=$M/$1.js timeout 900 python3 -u tests/run_tests.py -k $2 2>&1 | grep -E "$F" | cut -c1-400; }
run chips_never_lift qa_the_kitchen_chips_never_sit_on_the_counters
run chips_lift_all_or_none qa_the_kitchen_chips_never_sit_on_the_counters
run task_list_stays qa_the_task_list_opens_under_its_chip_and_any_tap_puts_it_away
run task_list_over_chip qa_the_task_list_opens_under_its_chip_and_any_tap_puts_it_away
run batch_of_three_split cooking_a_full_place_is_a_quiet_wait
run cooks_never_plate cooking_jill_and_the_cooks_hand_work_on
run rack_by_the_wall cooking_plating_happens_where_the_food_is
echo "== done $(date -u +%H:%M:%S)"
