"""rc8.5: the cats' personalities, measured — each cat's share of time in each state during a played service and in the
evening after it, over eight seeds (the fingerprint test's three moods, 31338-31345). Run on rc8.4's game.js
(JK_GAME_JS) and on rc8.5's to show the small-talk change moved one trajectory, not who the cats are.
  [JK_GAME_JS=old/game.js] python3 docs/evidence/v24_rc8_5/sims/cat_moods.py LABEL"""
import sys, os, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))); sys.path.insert(0, os.path.join(ROOT, 'tests')); os.chdir(ROOT)
import run_tests as rt
from playwright.sync_api import sync_playwright
CNT = r"""window.__cmAdd=()=>{for(const c of CATS){const k=c.def.id+':'+(c.st==='bed'?'sleep':c.st);__cm[k]=(__cm[k]||0)+1}}"""
tot = {'service': {}, 'evening': {}}
with sync_playwright() as p:
    srv, port = rt.start_server(); b = p.chromium.launch()
    for seed in range(1, 9):
        g = rt.Game(b, port, 'index', seed=31337 + seed, manual=True); rt.install_bot(g)
        g.click('[data-act=open]'); g.ev(CNT); rt.start_day(g)
        g.ev("window.__cm={};for(let i=0;i<20000&&phase==='service';i++){__bot(1,1/30);__cmAdd()}")
        for k, v in json.loads(g.ev("JSON.stringify(__cm)")).items(): tot['service'][k] = tot['service'].get(k, 0) + v
        if g.ev("phase") == 'summary': g.click('[data-act=toShop]')
        g.ev("window.__cm={};let t=0;for(let i=0;i<18000;i++){t+=1/30;updateCats(1/30,t);__cmAdd()}")
        for k, v in json.loads(g.ev("JSON.stringify(__cm)")).items(): tot['evening'][k] = tot['evening'].get(k, 0) + v
        g.close()
    b.close(); srv.shutdown()
for mood, T in tot.items():
    cats = sorted({k.split(':')[0] for k in T})
    line = []
    for c in cats:
        all_ = sum(v for k, v in T.items() if k.startswith(c + ':'))
        top = sorted(((v / all_ * 100, k.split(':')[1]) for k, v in T.items() if k.startswith(c + ':')), reverse=True)[:4]
        line.append(f"{c} " + ' '.join(f'{s} {round(x)}%' for x, s in top))
    print(sys.argv[1], mood, ' | '.join(line))
