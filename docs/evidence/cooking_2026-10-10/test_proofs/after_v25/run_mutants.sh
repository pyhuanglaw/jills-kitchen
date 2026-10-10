#!/bin/bash
S=/tmp/claude-0/-home-user-jills-kitchen/63b8740a-97ce-5ff7-813a-d847b68fd153/scratchpad
cd $S/wt_g1
FIRE=cooking_on_fire_can_come_on_the_first_day
CAPS=v24_rc8_the_restaurants_three_lists_and_the_lounges_one,v24_restaurant_and_lounge_staff_are_two_pools_that_never_share_places,v24_an_old_shared_cap_save_keeps_everyone_and_waits
for m in fire_day_gate:$FIRE fire_solo_is_mature:$FIRE fire_waiter_is_a_cook:$FIRE fire_standby_counts:$FIRE bistro_no_more_places:$CAPS bistro_waiter_only:$CAPS; do
  k=${m%%:*}; t=${m#*:}
  echo "== mutant $k" >> $S/r5/proofs/mutants.txt
  JK_GAME_JS=$S/r5/proofs/mut_$k.js timeout 1500 python3 -u tests/run_tests.py -k $t 2>&1 | grep -E "^(PASS|FAIL)|^      |passed" | cut -c1-400 >> $S/r5/proofs/mutants.txt
done
echo "done $(date -u +%H:%M:%S)" >> $S/r5/proofs/mutants.txt
