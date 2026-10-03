import sys, os, json
ROOT = sys.argv[1]; SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 7611
MODE = sys.argv[3] if len(sys.argv) > 3 else 'cn'
sys.path.insert(0, ROOT + '/tests'); os.chdir(ROOT)
import run_tests as rt, v24_tests as v
from playwright.sync_api import sync_playwright
srv, port = rt.start_server()
with sync_playwright() as p:
    b = p.chromium.launch()
    g = rt.Game(b, port, 'index', seed=SEED, manual=True, viewport={'width': 390, 'height': 844})
    v.load_save(g, 'player_day74_1508.json')
    g.ev("kenS().next=null;S.cn=" + ("{n:1,last:S.day-9,next:{d:S.day,menu:cnMenu()}}" if MODE == 'cn' else "null"))
    v.to_service(g); g.ev("window.__act=window.__actLazy||(()=>{})")
    js = "(()=>{const a=R.sched;let bad=[];for(let i=Math.max(R.si,1);i<a.length;i++)if(a[i].t<a[i-1].t-1e-9)bad.push([i,+(a[i-1].t/R.dur).toFixed(3),a[i-1].name||a[i-1].type,a[i-1].hold?1:0,+(a[i].t/R.dur).toFixed(3),a[i].name||a[i].type,a[i].hold?1:0]);return JSON.stringify({t:+(R.t/R.dur).toFixed(3),si:R.si,bad:bad.slice(0,4)})})()"
    print('start', g.ev(js))
    for f in [x / 100 for x in range(2, 46, 2)]:
        g.ev("__botUntil('R.t>R.dur*%f',150000,1/30)" % f)
        r = json.loads(g.ev(js))
        if r['bad']: print(f, r); break
    g.close(); b.close()
srv.shutdown()
