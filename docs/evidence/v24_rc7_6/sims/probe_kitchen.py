"""Where the chef's night waits in the kitchen: pending items by station over the evening (Day 74 save). python3 probe_kitchen.py ROOT seed"""
import sys, os, json
ROOT = sys.argv[1]; SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 7621
sys.path.insert(0, ROOT + '/tests'); os.chdir(ROOT)
import run_tests as rt, v24_tests as v
from playwright.sync_api import sync_playwright
srv, port = rt.start_server()
with sync_playwright() as p:
    b = p.chromium.launch()
    g = rt.Game(b, port, 'index', seed=SEED, manual=True, viewport={'width': 390, 'height': 844})
    v.load_save(g, 'player_day74_1508.json')
    g.ev("kenS().next=null;S.cn={n:1,last:S.day-9,next:{d:S.day,menu:cnMenu()}}")
    print('menu', g.ev("JSON.stringify(S.cn.next.menu.map(d=>[d,DISH(d).st]))"))
    v.to_service(g); g.ev("window.__act=window.__actLazy||(()=>{})")
    print('slots', g.ev("JSON.stringify(R.slots.reduce((a,s)=>{a[s.type]=(a[s.type]||0)+1;return a},{}))"), 'chefs', g.ev("JSON.stringify((S.crew||[]).filter(m=>m.role==='chef'&&crewHere(m)).map(m=>[m.name,m.duty,m.lv]))"))
    for k in range(8, 41, 2):
        g.ev("__botUntil('R.t>=R.dur*%f||phase!==\"service\"',120000,1/30)" % (k / 40))
        if g.ev("phase") != 'service': break
        print(k / 40, g.ev("""JSON.stringify((()=>{const o={cn:{},main:{},lg:{}};for(const tk of R.tickets)for(const it of tk.items){const D=DISH(it.d);if(it.st==='served'||it.st==='cancel')continue;if(D.wine){if(tk.cn){o.w=o.w||{};o.w[it.st]=(o.w[it.st]||0)+1}continue}const b=tk.cn?o.cn:tk.lounge?o.lg:o.main;const key=it.st==='ready'?'R':it.st==='later'?'L':D.st;b[key]=(b[key]||0)+1}o.bt=(S.crew||[]).filter(m=>m.role==='bartender'&&m.duty==='lbar'&&crewHere(m)).map(m=>{const w=R.cw[m.id];return m.name+':'+(w&&w.task?w.task.k:'-')}).join(',');o.busy=R.slots.filter(s=>s.job).map(s=>s.type[0]+(s.job.tk.cn?'*':'')).join('');return o})())"""))
    print('errors', g.errors[:3]); g.close(); b.close()
srv.shutdown()
