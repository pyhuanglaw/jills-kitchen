#!/bin/bash
# The golden baselines (tests/golden/, recorded on 8298e18's game) and the walkway through the line: what moves them, the
# re-recording, and that they still catch a change. The only difference in the game between 8298e18 and this build is the
# walkway (git diff 8298e18 -- js/game.js).
S=/tmp/claude-0/-home-user-jills-kitchen/63b8740a-97ce-5ff7-813a-d847b68fd153/scratchpad
G=golden_frames,golden_scenario,cat_personality_fingerprint
F='^(PASS|FAIL)|passed|^      '
cd /home/user/jills-kitchen
echo "== 0. what differs in the game: files and lines"
git diff --stat 8298e18 -- js/ index.html css/ 2>/dev/null | tail -3
echo "== 1. 8298e18's game, the baselines as they are"
JK_GAME_JS=$S/game_8298e18.js python3 -u tests/run_tests.py -k $G 2>&1 | grep -E "$F" | cut -c1-260
echo "== 2. the walkway build, the baselines as they are"
python3 -u tests/run_tests.py -k $G 2>&1 | grep -E "$F" | cut -c1-400
echo "== 3. re-recorded on the walkway build"
python3 -u tests/run_tests.py --record -k $G 2>&1 | grep -E "$F|recorded" | cut -c1-200
python3 -u tests/run_tests.py -k $G 2>&1 | grep -E "$F" | cut -c1-200
echo "== 4. still caught: three small changes, one at a time"
mkdir -p $S/mutw
python3 - <<'PY'
s=open('js/game.js',encoding='utf-8').read()
M='/tmp/claude-0/-home-user-jills-kitchen/63b8740a-97ce-5ff7-813a-d847b68fd153/scratchpad/mutw/'
a="friedrice:{n:"
i=s.index(a); j=s.index('price:',i); k=s.index(',',j); price=s[j+6:k]
open(M+'g_price.js','w',encoding='utf-8').write(s[:j+6]+str(int(price)+5)+s[k:])
a2="const JILL_LOOK={"; i=s.index(a2); j=s.index("hair:'",i); k=s.index("'",j+6)
open(M+'g_hair.js','w',encoding='utf-8').write(s[:j+6]+'#FF00FF'+s[k:])
a3="const ww={sun:4,cloud:3,"; assert s.count(a3)==1
open(M+'g_weight.js','w',encoding='utf-8').write(s.replace(a3,"const ww={sun:4.01,cloud:3,"))
a4="get gap(){const L=KXL();return{x0:L.prep.x+L.prep.w+2,x1:L.range.x-2}}"; assert s.count(a4)==1
open(M+'g_gap.js','w',encoding='utf-8').write(s.replace(a4,"get gap(){const L=KXL();return{x0:L.prep.x+L.prep.w+4,x1:L.range.x-2}}"))
print('price',price,'hair',s[j+6:k])
PY
for m in g_price g_hair g_weight g_gap; do echo "-- $m"; JK_GAME_JS=$S/mutw/$m.js python3 -u tests/run_tests.py -k $G 2>&1 | grep -E "^(PASS|FAIL)|passed" | cut -c1-160; done
echo "== done"
