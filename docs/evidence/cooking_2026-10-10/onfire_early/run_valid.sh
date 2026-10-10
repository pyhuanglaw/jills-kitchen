#!/bin/bash
# ON FIRE in new games with the fire on: GAME_JS TAG then batches of seed:days:service
S=/tmp/claude-0/-home-user-jills-kitchen/63b8740a-97ce-5ff7-813a-d847b68fd153/scratchpad
GJS=$1; TAG=$2; shift 2
OUT=$S/r4/fire/valid/$TAG; mkdir -p $OUT
cd /home/user/jills-kitchen
HOOK="$(cat $S/r4/fire/rec/hook.js);$(cat $S/r4/fire/rec/hook_fire.js)"
run(){ JK_GAME_JS=$GJS timeout 3600 python3 -u tools/qa/new_game_timeline.py --days $2 --seed $1 --service $3 --json $OUT/${3}_$1.json --what-if "$HOOK" --probe $S/r4/fire/rec/probe_fire.json > $OUT/${3}_$1.out 2>&1
  echo "$3 $1 exit=$? $(date -u +%H:%M:%S)" >> $OUT/done.txt; }
for batch in "$@"; do for spec in $batch; do IFS=: read sd dd sv <<< "$spec"; run $sd $dd $sv & done; wait; done
