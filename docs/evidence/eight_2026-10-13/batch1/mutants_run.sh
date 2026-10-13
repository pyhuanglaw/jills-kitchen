#!/bin/bash
M=/tmp/claude-0/-home-user-jills-kitchen/63b8740a-97ce-5ff7-813a-d847b68fd153/scratchpad/b1mut
cd /home/user/jills-kitchen
run(){ echo "== $1 (test: $2)"; JK_GAME_JS=$M/$1.js timeout 900 python3 tests/run_tests.py -k $2 2>&1 | grep -E "^(PASS|FAIL)|^      " | head -2; }
T1=dylan_takes_what_is_left_and_never_storms_off; T2=important_people_complain_in_their_own_words; T3=madame_lin_comes_as_herself_not_as_a_drawn_stranger; T4=a_passing_family_is_not_the_wangs
for t in $T1 $T2 $T3 $T4; do run before $t; done
for m in dylan_no_substitute dylan_leaves_like_a_stranger dylan_reviews dylan_storms_off; do run $m $T1; done
for m in no_voice_reviews no_stranger_filter no_spoken_line yijun_named_before_met yijun_voice_before_met; do run $m $T2; done
for m in lin_ungated lin_in_the_rush lin_announced_as_vip lin_on_her_last_night; do run $m $T3; done
run wang_family_back $T4
