#!/bin/bash
# What moved the golden baselines (8ded2e2's): 6bf5002's game with only the rack put back by the wall (rack_by_the_wall, made by
# test_proofs/iphone_fixes/mutants_make.py), run against the baselines as they were — in a worktree of 6bf5002 (its tests/golden/).
S=/tmp/claude-0/-home-user-jills-kitchen/63b8740a-97ce-5ff7-813a-d847b68fd153/scratchpad
cd $S/wt_r3b   # 6bf5002
JK_GAME_JS=$S/r3/mut2/rack_by_the_wall.js python3 -u tests/run_tests.py -k golden_scenario,cat_personality_fingerprint,golden_frames
