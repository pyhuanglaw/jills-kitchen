#!/bin/bash
M=/tmp/claude-0/-home-user-jills-kitchen/63b8740a-97ce-5ff7-813a-d847b68fd153/scratchpad/b2mut
cd /home/user/jills-kitchen
run(){ echo "== $1 (test: $2)"; JK_GAME_JS=$M/$1.js timeout 900 python3 tests/run_tests.py -k $2 2>&1 | grep -E "^(PASS|FAIL)|^      " | head -2; }
TA=qa_restock_sits_under_todays_weather; TB=qa_the_prep_screens_44_reach_by_real_taps; TC=qa_the_staff_x_takes_a_finger; TD=qa_the_summary_says_when_the_fridge_was_short; TE=qa_the_prep_screens_small_buttons_take_a_finger
for t in $TA $TB $TC $TD $TE; do run current $t; done
for m in restock_at_the_foot shortfall_written_in shortfall_small estimate_from_deficits own_algorithm; do run $m $TA; done
for m in always_upgrade summary_any_night summary_upgrade_always summary_no_line; do run $m $TD; done
for m in reach_v255 reach_overlaps mini_under_the_note rows_taller tog_even_in_rows; do run $m $TB; run $m $TE; done
for m in x_24 x_rows_close; do run $m $TC; done
