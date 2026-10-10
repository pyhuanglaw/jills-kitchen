"""Two wrong versions of js/game.js for the card test (each is what the card check is there to catch).
python3 mutants_make.py OUTDIR   (run from the repo root, on the game being checked)"""
import sys
D = sys.argv[1] + '/'
src = open('js/game.js', encoding='utf-8').read()
def mut(name, pairs):
    s = src
    for a, b in pairs:
        assert s.count(a) == 1, (name, a[:80], s.count(a)); s = s.replace(a, b, 1)
    open(D + name + '.js', 'w', encoding='utf-8').write(s); print(name, 'ok')
# the card never says Jill is on her way (stays 「接著做」 after she sets off)
mut('card_never_on_way', [("function jillOnIt(n){const J=R.jill;if(!n||n.who!=='jill')return false;", "function jillOnIt(n){return false;const J=R.jill;if(!n||n.who!=='jill')return false;")])
# the card does not name Jill when the dish is hers (it reads as waiting)
mut('card_no_jill', [("function wfWho(n){if(!n||!n.who)return null;if(n.who==='jill')return'Jill';", "function wfWho(n){if(!n||!n.who)return null;if(n.who==='jill')return null;")])
