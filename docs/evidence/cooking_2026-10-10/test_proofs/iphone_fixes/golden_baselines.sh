#!/bin/bash
# The golden baselines (tests/golden/, recorded on 8ded2e2's game — round 2) and the iPhone fixes after the merge (the user's
# reports of 2026-10-10: every cook takes any step, the plates fetched at the rack, the task list and the kitchen chips): what moves them, the re-recording, and that they still catch a change.
# js/game.js and css/style.css differ between 8ded2e2 and these fixes (git diff --stat 8ded2e2 -- index.html css/ js/).
S=/tmp/claude-0/-home-user-jills-kitchen/63b8740a-97ce-5ff7-813a-d847b68fd153/scratchpad
G=golden_frames,golden_scenario,cat_personality_fingerprint
F='^(PASS|FAIL)|passed|^      '
cd /home/user/jills-kitchen
echo "== 0. what differs in the game: files and lines"
git diff --stat 8ded2e2 -- js/ index.html css/ | tail -3
echo "== 1. 8ded2e2's game (the baselines were recorded on it), the baselines as they are"
git show 8ded2e2:js/game.js > $S/r3/golden/game_8ded2e2.js
JK_GAME_JS=$S/r3/golden/game_8ded2e2.js python3 -u tests/run_tests.py -k $G 2>&1 | grep -E "$F" | cut -c1-260
echo "== 2. the fixed game, the baselines as they are"
python3 -u tests/run_tests.py -k $G 2>&1 | grep -E "$F" | cut -c1-1200
echo "== 3. re-recorded on the fixed game"
python3 -u tests/run_tests.py --record -k $G 2>&1 | grep -E "$F|recorded" | cut -c1-200
python3 -u tests/run_tests.py -k $G 2>&1 | grep -E "$F" | cut -c1-200
echo "== 4. still caught: four small changes, one at a time"
mkdir -p $S/r3/golden/mutg
python3 - <<'PY'
s=open('js/game.js',encoding='utf-8').read()
M='/tmp/claude-0/-home-user-jills-kitchen/63b8740a-97ce-5ff7-813a-d847b68fd153/scratchpad/r3/golden/mutg/'
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
for m in g_price g_hair g_weight g_passgap; do echo "-- $m"; JK_GAME_JS=$S/r3/golden/mutg/$m.js python3 -u tests/run_tests.py -k $G 2>&1 | grep -E "^(PASS|FAIL)|passed" | cut -c1-160; done
echo "== done"
