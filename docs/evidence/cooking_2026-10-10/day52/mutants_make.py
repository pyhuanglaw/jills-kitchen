"""Three slowed-down versions of js/game.js for the Day 52 test (each is a pacing problem the test is there to catch).
python3 mutants_make.py OUTDIR   (run from the repo root, on the game being checked)"""
import sys
D = sys.argv[1] + '/'
src = open('js/game.js', encoding='utf-8').read()
def mut(name, pairs):
    s = src
    for a, b in pairs:
        assert s.count(a) == 1, (name, a[:80], s.count(a)); s = s.replace(a, b, 1)
    open(D + name + '.js', 'w', encoding='utf-8').write(s); print(name, 'ok')
# the move two days later: 怡君's arc slower than the user's targets
mut('yj_slow', [("due('yj_move','yj_chose',2,'yj')", "due('yj_move','yj_chose',4,'yj')")])
# the mediation six days later: the wall settles too late
mut('wall_slow', [("due('wall_mediation','wall_prep',3,'wall')", "due('wall_mediation','wall_prep',9,'wall')")])
# the Second Floor opens on the wall, not on the Lounge (the player's 10:25)
mut('up_on_wall', [("{k:'up',n:'二樓',open:()=>loungeDoneDay(),", "{k:'up',n:'二樓',open:()=>{const f=fact('wall_settle');return f?f.d:null},")])
