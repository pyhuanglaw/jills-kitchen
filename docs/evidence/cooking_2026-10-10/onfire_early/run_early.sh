#!/bin/bash
# early ON FIRE recordings: new games on the fire-off copy of 2baa9d4, the normal player; per-table rows via the probe
S=/tmp/claude-0/-home-user-jills-kitchen/63b8740a-97ce-5ff7-813a-d847b68fd153/scratchpad
OUT=$S/r4/fire/rec/out; mkdir -p $OUT
cd /home/user/jills-kitchen
HOOK="$(cat $S/r4/fire/rec/hook.js)"
run(){ # seed days service
  JK_GAME_JS=$S/r4/fire/game_fireoff_2baa9d4.js timeout 3600 python3 -u tools/qa/new_game_timeline.py --days $2 --seed $1 --service $3 --json $OUT/${3}_$1.json --what-if "$HOOK" --probe $S/r4/fire/rec/probe.json > $OUT/${3}_$1.out 2>&1
  echo "$3 $1 exit=$? $(date -u +%H:%M:%S)" >> $OUT/done.txt
}
for batch in "$@"; do
  for spec in $batch; do IFS=: read sd dd sv <<< "$spec"; run $sd $dd $sv & done; wait
done
