"""The new pat check (her first breather on the busy floor, a cat beside her, the roll held low for one update) on seeds
1-12 of Day 1 alone: does the breather come, and does she pat? On the build in JK_GAME_JS. Same loop and probe as
tests/run_tests.py jill_rests_when_staff_cover_the_floor."""
import sys, os, json
ROOT = '/home/user/jills-kitchen'
sys.path.insert(0, os.path.join(ROOT, 'tests')); os.chdir(ROOT); TAG = sys.argv[1]; sys.argv = [sys.argv[0]]
import run_tests as rt
from playwright.sync_api import sync_playwright
PROBE = "if(__rs.probe===null&&!J.cur&&!J.pet&&!J.rest&&J.tx==null&&(J.room||'main')==='main'&&J.idle>1.5&&R.closing==null&&R.groups.filter(q=>q.table!=null).length>=2){const wl=jillWorkload();if(wl<=2){const c=CATS.find(k=>k.def.id==='tora');releaseSpots(c);Object.assign(c,{x:J.x+(J.x<200?20:-20),y:J.y+4,st:'rest',pose:'sit',t:12,perch:-1,sofa:null,hidden:false,moving:false});J.petCD=0;const r0=Math.random;Math.random=()=>.01;try{jillUpd(1/30)}finally{Math.random=r0}__rs.probe={t:+R.t.toFixed(1),wl,tables:R.groups.filter(q=>q.table!=null).length,pet:J.pet?J.pet.cat.def.id:null}}}"
srv, port = rt.start_server(); out = []
with sync_playwright() as p:
    b = p.chromium.launch()
    for seed in range(1, 13):
        g = rt.Game(b, port, 'index', seed=seed, manual=True)
        rt.install_bot(g); g.ev(rt.LAZY_ACTOR); g.click('[data-act=open]'); rt.start_day(g)
        g.ev("window.__rs={sit:0,frames:0,pets:0,probe:null}")
        for _ in range(1500):
            r = g.ev("(()=>{for(let i=0;i<10;i++){if(!(phase==='service'&&R))return 0;if(i===0)__act();__tick(1000/30);const J=R.jill;__rs.frames++;if(J.rest==='sit')__rs.sit++;if(J.pet)__rs.pets++;%s;if(R.closing!=null&&R.closing>2&&!R.ended){finishClosing();return 0}}return 1})()" % PROBE)
            if not r: break
        st = json.loads(g.ev("JSON.stringify(__rs)")); out.append((seed, st['probe'], round(st['sit'] / max(1, st['frames']), 3))); g.close()
    b.close()
srv.shutdown()
print(TAG, '(seed, the probe, share sitting):', out)
print(TAG, 'she patted at the probe on', sum(1 for s in out if isinstance(s[1], dict) and s[1]['pet']), 'of', len(out), 'days')
