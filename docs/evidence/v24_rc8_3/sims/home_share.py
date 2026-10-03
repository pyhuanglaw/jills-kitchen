import sys, os, json
ROOT='/home/user/jills-kitchen-lin-restore/project_git'; sys.path.insert(0, os.path.join(ROOT,'tests')); os.chdir(ROOT)
import run_tests as rt
from playwright.sync_api import sync_playwright
run = r"""(n=>{const cnt={};let t=0;for(let i=0;i<n;i++){t+=1/30;updateCats(1/30,t);for(const c of CATS){const k=c.def.id;cnt[k]=cnt[k]||{home:0,all:0,bowl:0};cnt[k].all++;if(c.st==='home')cnt[k].home++;if(c.homeSpot==='bowl'&&c.st==='home')cnt[k].bowl++}}return cnt})"""
tot={}
with sync_playwright() as p:
    srv, port = rt.start_server(); b = p.chromium.launch()
    for seed in range(1,9):
        g = rt.Game(b, port, 'index', seed=31337+seed, manual=True); rt.install_bot(g)
        g.click('[data-act=open]')
        r=g.ev(f"({run})(18000)")
        for k,v in r.items():
            T=tot.setdefault(k,{'home':0,'all':0,'bowl':0})
            for kk in v: T[kk]+=v[kk]
        g.close()
    b.close(); srv.shutdown()
print(sys.argv[1], {k:(round(v['home']/v['all']*100), round(v['bowl']/v['all']*100,1)) for k,v in tot.items()})
