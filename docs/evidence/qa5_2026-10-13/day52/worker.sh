#!/bin/bash
# a worker: takes the next unclaimed job (mkdir is the claim), runs the Day 52 loop with each morning's weather on its own seed
S=/tmp/claude-0/-home-user-jills-kitchen/63b8740a-97ce-5ff7-813a-d847b68fd153/scratchpad/q5
JOBS="main:f8d9b87:7600 new:86820a6:7600 rev:24c04ec:7600"
for b in 7000 7100 7200 7300 7400 7500 7700 7800 7900 8000 8100 8200 8300; do JOBS="$JOBS main:f8d9b87:$b new:86820a6:$b"; done
for j in $JOBS; do IFS=: read tag c base <<< "$j"
  mkdir $S/d52/claims/${tag}_${base} 2>/dev/null || continue
  python3 -u $S/d52/day52_wxseed.py $S/wt_$c $base > $S/d52/runs/${tag}_${c}_${base}.json.tmp 2> $S/d52/runs/${tag}_${c}_${base}.err && mv $S/d52/runs/${tag}_${c}_${base}.json.tmp $S/d52/runs/${tag}_${c}_${base}.json
  echo "done ${tag}_${base} $(date -u +%H:%M)"
done
echo "worker finished"
