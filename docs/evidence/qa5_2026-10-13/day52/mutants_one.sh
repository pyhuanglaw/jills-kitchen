#!/bin/bash
# one.sh NAME GAMEJS : the Day 52 test of the working tree (seed base 7000) on a game
M=/tmp/claude-0/-home-user-jills-kitchen/63b8740a-97ce-5ff7-813a-d847b68fd153/scratchpad/q5/d52/mut
cd /home/user/jills-kitchen
JK_GAME_JS=$2 timeout 1500 python3 -u tests/run_tests.py -k v24_day52_save_plays_the_stories_in_order_over_forty_days > $M/$1.txt 2>&1
echo "$1 exit=$? $(date -u +%H:%M:%S)" >> $M/done.txt
