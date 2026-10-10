#!/bin/bash
# one.sh NAME GAMEJS|- : the Day 52 test (the working tree's, each morning's draw seeded) on a game
S=/tmp/claude-0/-home-user-jills-kitchen/63b8740a-97ce-5ff7-813a-d847b68fd153/scratchpad
cd /home/user/jills-kitchen
T=v24_day52_save_plays_the_stories_in_order_over_forty_days
if [ "$2" = "-" ]; then timeout 1500 python3 -u tests/run_tests.py -k $T > $S/r3/d52fix/$1.txt 2>&1; else JK_GAME_JS=$2 timeout 1500 python3 -u tests/run_tests.py -k $T > $S/r3/d52fix/$1.txt 2>&1; fi
echo "$1 exit=$? $(date -u +%H:%M:%S)" >> $S/r3/d52fix/done.txt
