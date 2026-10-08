#!/bin/bash
# M10: the same normal player (human service) on two seeds, main against the new kitchen (and option B, faster hands).
SP=/tmp/claude-0/-home-user/64ee893e-2a9e-517e-af2d-4f2493c4fa84/scratchpad
COOK=/tmp/claude-0/-home-user/64ee893e-2a9e-517e-af2d-4f2493c4fa84/scratchpad/wt_cook3; MAIN=$SP/wt_rc88; DAYS=${DAYS:-8}
WI_C="{const _m=wfMax;wfMax=function(d){return Math.max(_m(d),3)}}"
WI_D="{const _cp=chefProf;chefProf=function(m,f){const p=_cp(m,f);return f==='plate'?Math.max(p,1):p}}"
WI_B="{const _wt=wfTimes;wfTimes=function(d,f){const r=_wt(d,f);return{act:r.act*(f==='plate'||f==='hot'?.62:.7),pas:r.pas}}}"
run(){ # name root seed [whatif]
  if [ -n "$4" ]; then JK_ROOT=$2 python3 $2/tools/qa/new_game_timeline.py --days $DAYS --seed $3 --service human --json $SP/m10/$1.json --log $SP/m10/$1_log.txt --what-if "$4" > $SP/m10/$1.out 2>&1
  else JK_ROOT=$2 python3 $2/tools/qa/new_game_timeline.py --days $DAYS --seed $3 --service human --json $SP/m10/$1.json --log $SP/m10/$1_log.txt > $SP/m10/$1.out 2>&1; fi; }
case "$1" in
 1) run main_300 $MAIN 300 & run cook_300 $COOK 300 & run cookB_300 $COOK 300 "$WI_B" & wait;;
 2) run main_301 $MAIN 301 & run cook_301 $COOK 301 & run cookB_301 $COOK 301 "$WI_B" & wait;;
 4) run cookC_300 $COOK 300 "$WI_C" & run cookC_301 $COOK 301 "$WI_C" & wait;;
 3) run cookD_300 $COOK 300 "$WI_D" & run cookD_301 $COOK 301 "$WI_D" & wait;;
esac
date -u +%H:%M:%S
