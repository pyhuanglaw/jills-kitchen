#!/bin/bash
S=/tmp/claude-0/-home-user-jills-kitchen/63b8740a-97ce-5ff7-813a-d847b68fd153/scratchpad
until [ "$(wc -l < $S/r4/fire/rec/out/done.txt 2>/dev/null)" -ge 12 ]; do sleep 20; done
$S/r4/fire/rec/run_early.sh "420:2:human 421:2:human 422:2:human 423:2:human" "424:2:human 425:2:human 426:2:human 427:2:human" "428:2:human 429:2:human 430:2:human 431:2:human" "432:2:perfect 433:2:perfect 434:2:perfect 435:2:perfect"
