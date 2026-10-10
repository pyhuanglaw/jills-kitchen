"""Day 1, Jill alone (the rc8.5 harness's player): where is she when a resting cat is within reach, and what is she doing then?
Encounters (a resting cat comes within R px of her in the main hall) by what she was doing; pats started.  ROOT SEEDS..."""
import sys, os, json
ROOT=sys.argv[1]; seeds=[int(x) for x in sys.argv[2:]]; sys.path.insert(0, os.path.join(ROOT,'tests')); sys.argv=[sys.argv[0]]
import run_tests as rt
from playwright.sync_api import sync_playwright
PROBE=r"""(()=>{window.__np={enc:{},sec:{},pats:0,last:false,near:false};window.__npStep=function(){const J=R.jill;const M=__np;
 if(J.pet&&!M.last)M.pats++;M.last=!!J.pet;
 if((J.room||'main')!=='main'){M.near=false;return}
 const c=CATS.find(c=>!c.hidden&&c.perch<0&&!c.sofa&&['rest','daze','stare','sleep','side'].includes(c.st)&&Math.hypot(c.x-J.x,c.y-J.y)<40);
 const k=J.pet?'pet':J.rest?'rest':(J.busy>0&&J.cur)?'at_table':(J.tx!=null&&J.tx===PASS.x&&J.ty===PASS.y)?'walk_pass':(J.tx!=null&&J.troom==='kitchen')?'walk_kitchen':(J.tx!=null&&J.cur&&J.cur.dump)?'walk_dump':(J.tx!=null)?'walk_other':'idle';
 if(c){M.sec[k]=(M.sec[k]||0)+1/30;if(!M.near)M.enc[k]=(M.enc[k]||0)+1}M.near=!!c}})()"""
out=[]
with sync_playwright() as p:
    srv, port = rt.start_server(); b = p.chromium.launch()
    for seed in seeds:
        g = rt.Game(b, port, 'index', seed=seed, manual=True); rt.install_bot(g); g.ev(rt.LAZY_ACTOR); g.click('[data-act=open]')
        rt.start_day(g); g.ev(PROBE)
        for _ in range(1500):
            r = g.ev("(()=>{for(let i=0;i<10;i++){if(!(phase==='service'&&R))return 0;if(i===0)__act();__tick(1000/30);__npStep();if(R.closing!=null&&R.closing>2&&!R.ended){finishClosing();return 0}}return 1})()")
            if not r: break
        s = json.loads(g.ev("JSON.stringify(__np)")); s['seed']=seed; s['sec']={k:round(v,1) for k,v in s['sec'].items()}; del s['last']; del s['near']
        print(json.dumps(s), flush=True); out.append(s)
        g.close()
    b.close(); srv.shutdown()
tot={}
for s in out:
    for k,v in s['enc'].items(): tot[k]=tot.get(k,0)+v
print('encounters by what she was doing:', tot, 'pats:', sum(s['pats'] for s in out))
