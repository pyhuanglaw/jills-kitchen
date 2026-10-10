import sys, os, json
sys.path.insert(0, os.path.join(os.getcwd(), 'tests')); sys.argv=[sys.argv[0]]
import run_tests as rt
from playwright.sync_api import sync_playwright
import v24_tests as v
srv, port = rt.start_server()
out=[]
with sync_playwright() as p:
    b = p.chromium.launch()
    for gjs in sys.stdin.read().split():
        os.environ['JK_GAME_JS']=gjs
        for f in ['player_day6_1254.json','player_day30.json','player_day52.json','player_day61.json','player_day89_0448.json','player_day92_2105.json']:
            if not os.path.exists('tests/saves/'+f): continue
            g = rt.Game(b, port, 'index', seed=5, manual=True, viewport={'width':390,'height':844})
            v.load_save(g, f)
            r = g.ev("JSON.stringify({day:S.day,lv:S.level,crew:(S.crew||[]).length,caps:CAP_ROLES.map(r=>`${ROLES[r].n} ${roleCrew(r).length}/${roleCap(r)}`).join('、')})")
            print(os.path.basename(gjs), f, r, flush=True); g.close()
    b.close()
srv.shutdown()
