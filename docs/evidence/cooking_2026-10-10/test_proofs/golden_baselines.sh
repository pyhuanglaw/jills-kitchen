#!/bin/bash
# The golden baselines (tests/golden/, recorded on 6834a6d's game — the walkway through the line) and round 2 (the user's
# decisions of 2026-10-10): what moves them, the re-recording, and that they still catch a change.
# Only js/game.js differs between 6834a6d and round 2 (git diff --stat 6834a6d -- index.html css/ js/).
S=/tmp/claude-0/-home-user-jills-kitchen/63b8740a-97ce-5ff7-813a-d847b68fd153/scratchpad
G=golden_frames,golden_scenario,cat_personality_fingerprint
F='^(PASS|FAIL)|passed|^      '
cd /home/user/jills-kitchen
echo "== 0. what differs in the game: files and lines"
git diff --stat 6834a6d -- js/ index.html css/ | tail -3
echo "== 1. 6834a6d's game (the baselines were recorded on it), the baselines as they are"
git show 6834a6d:js/game.js > $S/r2/game_6834a6d.js
JK_GAME_JS=$S/r2/game_6834a6d.js python3 -u tests/run_tests.py -k $G 2>&1 | grep -E "$F" | cut -c1-260
echo "== 2. round 2's game, the baselines as they are"
python3 -u tests/run_tests.py -k $G 2>&1 | grep -E "$F" | cut -c1-1200
echo "== 3. re-recorded on round 2's game"
python3 -u tests/run_tests.py --record -k $G 2>&1 | grep -E "$F|recorded" | cut -c1-200
python3 -u tests/run_tests.py -k $G 2>&1 | grep -E "$F" | cut -c1-200
echo "== 4. still caught: four small changes, one at a time"
mkdir -p $S/r2/mutg
python3 - <<'PY'
s=open('js/game.js',encoding='utf-8').read()
M='/tmp/claude-0/-home-user-jills-kitchen/63b8740a-97ce-5ff7-813a-d847b68fd153/scratchpad/r2/mutg/'
a="friedrice:{n:"
i=s.index(a); j=s.index('price:',i); k=s.index(',',j); price=s[j+6:k]
open(M+'g_price.js','w',encoding='utf-8').write(s[:j+6]+str(int(price)+5)+s[k:])
a2="const JILL_LOOK={"; i=s.index(a2); j=s.index("hair:'",i); k=s.index("'",j+6)
open(M+'g_hair.js','w',encoding='utf-8').write(s[:j+6]+'#FF00FF'+s[k:])
a3="const ww={sun:4,cloud:3,"; assert s.count(a3)==1
open(M+'g_weight.js','w',encoding='utf-8').write(s.replace(a3,"const ww={sun:4.01,cloud:3,"))
a4="const PASS_GAP={x0:188,x1:212};"; assert s.count(a4)==1
open(M+'g_passgap.js','w',encoding='utf-8').write(s.replace(a4,"const PASS_GAP={x0:186,x1:212};"))
print('price',price,'hair',s[j+6:k])
PY
for m in g_price g_hair g_weight g_passgap; do echo "-- $m"; JK_GAME_JS=$S/r2/mutg/$m.js python3 -u tests/run_tests.py -k $G 2>&1 | grep -E "^(PASS|FAIL)|passed" | cut -c1-160; done
echo "== done"
