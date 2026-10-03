import sys, os, json
ROOT='/home/user/jills-kitchen-lin-restore/project_git'; sys.path.insert(0, os.path.join(ROOT,'tests')); os.chdir(ROOT)
import run_tests as rt, v23_tests as v3
from playwright.sync_api import sync_playwright
out=[]
with sync_playwright() as p:
    srv, port = rt.start_server(); b = p.chromium.launch()
    for seed in [51,52,53,54,55,56]:
        g = rt.Game(b, port, 'index', seed=seed, manual=True, viewport={'width': 390, 'height': 844})
        v3.load_fixture(g, 'player_day46.json'); g.click('[data-act=openFresh]'); g.page.wait_for_timeout(120)
        g.ev("S.money+=400000;factSet('lounge_project');buyLounge(1);hideReveal&&hideReveal()")
        g.ev("(()=>{const b=document.createElement('button');b.dataset.act='hireLounge';b.dataset.k='Evan';doAct('hireLounge',null,'Evan',b)})()")
        if g.ev("!S.crew.some(m=>m.role==='bartender')"): g.ev("S.crew.push({id:'cb1',role:'bartender',name:CREW_NAMES.bartender[0],lv:1,duty:'lbar'})")
        g.ev("S.crew.push({id:'cb2',role:'bartender',name:CREW_NAMES.bartender.find(n=>!S.crew.some(m=>m.name===n)),lv:1,duty:null})")
        g.ev("showPrep();autoStock();S.stock.bites=Math.max(S.stock.bites||0,12);S.stock.croquette=Math.max(S.stock.croquette||0,10);S.stock.cheeseplate=Math.max(S.stock.cheeseplate||0,8)")
        rt.start_day(g); rt.install_bot(g); g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;")
        g.ev("window.__lg={bites:0,lt:0,wineDine:0,cooked:0,lw:0};const ct0=createTicket;createTicket=function(q){const r=ct0.apply(this,arguments);const tk=q.ticket;if(!tk)return r;if(tk.lounge){__lg.lt++;if(q.lg&&q.lg.why==='wait')__lg.lw++;if(tk.items.some(i=>DISHES[i.d]&&DISHES[i.d].bar))__lg.bites++}else if(tk.items.some(i=>i.lbar))__lg.wineDine++;return r};const pl0=plate;plate=function(sl,q){const j=sl.job;if(j&&DISHES[j.d]&&DISHES[j.d].bar)__lg.cooked++;return pl0.apply(this,arguments)}")
        rt.play_day(g, max_steps=60000)
        for _ in range(400):
            if g.ev("phase") != 'service': break
            g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
        out.append((seed, json.loads(g.ev("JSON.stringify(__lg)"))))
        g.close()
    b.close(); srv.shutdown()
print(sys.argv[1], out)
