"""The Lounge booked out, measured on the player's Day 74 save: the same day (same seed) with no event, with the chef's
night, and with Ken's tasting night (later nights: unheld). The kitchen's load, the dining room's lost guests, the
night's people and money. python3 sim_events.py ROOT OUT.jsonl seed1 [seed2 ...]"""
import sys, os, json
ROOT = sys.argv[1]; OUTF = sys.argv[2]; SEEDS = [int(x) for x in sys.argv[3:]] or [7621]
sys.path.insert(0, ROOT + '/tests'); os.chdir(ROOT)
import run_tests as rt, v24_tests as v
from playwright.sync_api import sync_playwright
srv, port = rt.start_server()
SETUP = {
    'none': "S.cn=null;kenS().next=null",
    'cn': "kenS().next=null;S.cn={n:1,last:S.day-9,next:{d:S.day,menu:cnMenu()}}",
    'kt': "S.cn=null;kenS().next={d:S.day,n:5}",
}
rows = []
with sync_playwright() as p:
    b = p.chromium.launch()
    for seed in SEEDS:
        for mode in ('none', 'cn', 'kt'):
            g = rt.Game(b, port, 'index', seed=seed, manual=True, viewport={'width': 390, 'height': 844})
            v.load_save(g, 'player_day74_1508.json')
            g.ev(SETUP[mode])
            v.to_service(g); g.ev("window.__act=window.__actLazy||(()=>{})")
            g.ev("""window.__ev={first:null,last:null,cnServed:0,cnItems:0,lgBlocked:0,maxBack:0};
              const _sv=serveItems;serveItems=function(gq,list){try{if(gq&&gq.cn&&R&&R.cn){for(const x of list){const D=DISH(x.it.d);if(D&&!D.wine){__ev.cnServed++;if(__ev.first==null)__ev.first=R.t/R.dur;__ev.last=R.t/R.dur}}}}catch(e){}return _sv.apply(this,arguments)};""")
            info0 = g.ev("JSON.stringify({ev:lgEvent(),seats:lgSeatsAll(),people:R.cn?R.cn.people:R.kt?R.kt.people:0,dur:R.dur})")
            samples = []
            for k in range(1, 41):
                g.ev("__botUntil('R.t>=R.dur*%f||phase!==\"service\"',120000,1/30)" % (k / 40))
                if g.ev("phase") != 'service': break
                samples.append(json.loads(g.ev("""JSON.stringify({t:+(R.t/R.dur).toFixed(3),ev:lgEvent(),
                  back:R.tickets.filter(tk=>!tk.lounge).reduce((a,tk)=>a+tk.items.filter(i=>i.st==='pending'||i.st==='cooking').length,0),
                  cnBack:R.tickets.filter(tk=>tk.cn).reduce((a,tk)=>a+tk.items.filter(i=>!DISH(i.d).wine&&i.st!=='served'&&i.st!=='cancel').length,0),
                  lgIn:R.groups.filter(q=>!q.gone&&q.table!=null&&R.tables[q.table]&&R.tables[q.table].room==='lounge').reduce((a,q)=>a+q.size,0)})""")))
            end = json.loads(g.ev("""JSON.stringify({cn:R.cn?{on:R.cn.on,end:R.cn.end,people:R.cn.people,guests:R.cn.guests.length,paid:R.cn.guests.filter(q=>q.paid||q.state==='leave').length}:null,
              kt:R.kt?{on:R.kt.on,end:R.kt.end,people:R.kt.people,guests:R.kt.guests.length}:null,ev:__ev})"""))
            g.ev("__botUntil('phase!==\"service\"',120000,1/30)")
            summ = json.loads(g.ev("JSON.stringify(S.lastSummary?{rev:S.lastSummary.rev,net:S.lastSummary.net,guests:S.lastSummary.guests,lost:S.lastSummary.lost,angry:S.lastSummary.angry,lg:S.lastSummary.lg,cost:S.lastSummary.cost,stars:S.lastSummary.stars}:null)"))
            row = {'seed': seed, 'mode': mode, 'info': json.loads(info0), 'end': end, 'summary': summ,
                   'maxBack': max([s['back'] for s in samples] or [0]), 'maxCnBack': max([s['cnBack'] for s in samples] or [0]),
                   'trace': [(s['t'], s['ev'], s['back'], s['cnBack'], s['lgIn']) for s in samples], 'errors': g.errors[:3]}
            rows.append(row)
            print(json.dumps({k: row[k] for k in ('seed', 'mode', 'info', 'end', 'summary', 'maxBack', 'maxCnBack', 'errors')}, ensure_ascii=False), flush=True)
            g.close()
    b.close()
srv.shutdown()
with open(OUTF, 'w', encoding='utf-8') as f:
    for r in rows: f.write(json.dumps(r, ensure_ascii=False) + '\n')
