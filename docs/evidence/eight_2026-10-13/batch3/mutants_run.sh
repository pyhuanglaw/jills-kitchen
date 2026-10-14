#!/bin/bash
M=/tmp/claude-0/-home-user-jills-kitchen/63b8740a-97ce-5ff7-813a-d847b68fd153/scratchpad/b3mut
cd /home/user/jills-kitchen
run(){ echo "== $1 (test: $2)"; JK_GAME_JS=$M/$1.js timeout 900 python3 tests/run_tests.py -k $2 2>&1 | grep -E "^(PASS|FAIL)|^      " | head -2; }
T1=kitchen_two_has_a_third_board_at_the_pass; T2=without_kitchen_two_the_cold_counter_keeps_two; T3=the_cold_room_is_the_last_cold_step; T4=the_forecast_counts_the_evening_that_comes
for t in $T1 $T2 $T3 $T4; do run current $t; done
for m in board_on_cold_counter no_third_board plates_on_the_board cook_inside_the_pass pass_loses_a_spot third_board_never_used charged_for_the_board board_news_every_time; do run $m $T1; done
run old_checkpoint_counts_the_board $T2; run no_third_board $T2
for m in cold_room_adds_100 cold_room_costs_50000 cold_room_without_walkin cold_room_not_a_cold_step; do run $m $T3; done
for m in forecast_as_before forecast_never_learns task_follows_the_forecast arrivals_uncapped; do run $m $T4; done
