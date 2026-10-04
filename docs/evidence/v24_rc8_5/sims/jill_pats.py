import sys, os, json
ROOT=sys.argv[1]; sys.path.insert(0, os.path.join(ROOT,'tests'))
import run_tests as rt
from playwright.sync_api import sync_playwright
out=[]
with sync_playwright() as p:
    srv, port = rt.start_server(); b = p.chromium.launch()
    for seed in range(1, 21):
        g = rt.Game(b, port, 'index', seed=seed, manual=True); rt.install_bot(g); g.ev(rt.LAZY_ACTOR); g.click('[data-act=open]')
        rt.start_day(g); g.ev("window.__rs={sit:0,frames:0,pets:0,petN:0,last:false}")
        for _ in range(1500):
            r = g.ev("(()=>{for(let i=0;i<10;i++){if(!(phase==='service'&&R))return 0;if(i===0)__act();__tick(1000/30);const J=R.jill;__rs.frames++;if(J.rest==='sit')__rs.sit++;if(J.pet){__rs.pets++;if(!__rs.last)__rs.petN++}__rs.last=!!J.pet;if(R.closing!=null&&R.closing>2&&!R.ended){finishClosing();return 0}}return 1})()")
            if not r: break
        s = json.loads(g.ev("JSON.stringify(__rs)")); out.append((seed, s['petN'], round(s['sit']/max(1,s['frames']),3)))
        g.close()
    b.close(); srv.shutdown()
print('seed, times she patted a cat, share of the day sitting:', out)
print('days with a pat:', sum(1 for o in out if o[1]>0), 'of', len(out), '; pats in total:', sum(o[1] for o in out))
