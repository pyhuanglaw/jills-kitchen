"""ON FIRE per evening (the user's #15C, 2026-10-09): fresh Day 1–3 (lazy/every, two seeds) and the user's Day 30/52/92 saves
(lazy, three seeds), on the build in JK_GAME_JS (default js/game.js). One JSON line per evening: fires, Perfect/plated, seconds
under ON FIRE, the evening's seconds.
  JK_GAME_JS=/path/to/game.js python3 tools/sims/onfire_rate.py TAG"""
import sys, os, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'tests')); os.chdir(ROOT); tag = sys.argv[1]; sys.argv = [sys.argv[0]]
import run_tests as rt
import v24_tests as v
from playwright.sync_api import sync_playwright
STEP = "window.__fs=function(n){let k=0;for(let i=0;i<n;i++){if(!__act())break;update(1/30);updateCats(1/30,0);k++;if(R&&R.fire>0)__fireT+=1/30;if(R)__evT+=1/30;if(R&&R.closing!=null&&R.closing>1&&!R.ended){__fc=R.fireCount;__q=JSON.stringify(R.st.q);finishClosing();break}if(!R||phase!=='service')break;__fc=R.fireCount;__q=JSON.stringify(R.st.q)}return k}"
def evening(g):
    g.ev("window.__fireT=0;window.__evT=0;window.__fc=0;window.__q='{}';" + STEP)
    for _ in range(3000):
        if g.ev("phase") != 'service' or not g.ev("!!R"): break
        if g.page.evaluate('()=>window.__fs(60)') < 60: break
    return json.loads(g.ev("JSON.stringify({fires:__fc,q:JSON.parse(__q),fireT:Math.round(__fireT),evT:Math.round(__evT)})"))
srv, port = rt.start_server()
with sync_playwright() as p:
    b = p.chromium.launch()
    for seed in (101, 202):
        for who in ('lazy', 'every'):
            g = rt.Game(b, port, 'index', seed=seed, manual=True, viewport={'width': 390, 'height': 844})
            rt.install_bot(g); g.click('[data-act=open]')
            for day in (1, 2, 3):
                if day == 3: g.ev("autoStock()")
                rt.start_day(g)
                if who == 'lazy': g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;")
                r = evening(g); r.update(tag=tag, save='fresh', day=day, who=who, seed=seed); print(json.dumps(r), flush=True)
                if g.ev("phase") == 'summary': g.click('[data-act=toShop]')
                if day < 3: g.click('[data-act=nextDay]')
            g.close()
    for save in ('player_day30.json', 'player_day52.json', 'player_day92_2105.json'):
        for seed in (1, 2, 3):
            g = rt.Game(b, port, 'index', seed=500 + seed, manual=True, viewport={'width': 390, 'height': 844})
            v.load_save(g, save)
            g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}"); v.to_service(g, lazy=True)
            r = evening(g); r.update(tag=tag, save=save[7:12], who='lazy', seed=seed); print(json.dumps(r), flush=True)
            g.close()
    b.close()
srv.shutdown()
