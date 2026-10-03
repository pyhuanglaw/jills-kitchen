"""The chef's night, group by group: seated, ordered, each course out, paid (Day 74 save). python3 probe_cn_timeline.py ROOT seed"""
import sys, os, json
ROOT = sys.argv[1]; SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 7611
sys.path.insert(0, ROOT + '/tests'); os.chdir(ROOT)
import run_tests as rt, v24_tests as v
from playwright.sync_api import sync_playwright
srv, port = rt.start_server()
with sync_playwright() as p:
    b = p.chromium.launch()
    g = rt.Game(b, port, 'index', seed=SEED, manual=True, viewport={'width': 390, 'height': 844})
    v.load_save(g, 'player_day74_1508.json')
    g.ev("kenS().next=null;S.cn={n:1,last:S.day-9,next:{d:S.day,menu:cnMenu()}}")
    v.to_service(g); g.ev("window.__act=window.__actLazy||(()=>{})")
    g.ev("""window.__tl={};const T=()=>+(R.t/R.dur).toFixed(3);const G=q=>__tl[q.id]=__tl[q.id]||{n:q.name,s:q.size,bar:0};
      const s0=seatGroup;seatGroup=function(q,t){if(q.cn){const o=G(q);o.sat=T();o.bar=t.kind==='bar'?1:0}return s0.apply(this,arguments)};
      const c0=createTicket;createTicket=function(q){const r=c0.apply(this,arguments);if(q.cn)G(q).ord=T();return r};
      const v0=serveItems;serveItems=function(q,list){if(q&&q.cn)for(const x of list)if(x.it.st==='ready'&&!DISH(x.it.d).wine){G(q)['c'+x.it.course]=T()}return v0.apply(this,arguments)};
      const k0=collect;collect=function(q,o){if(q&&q.cn)G(q).paid=T();return k0.apply(this,arguments)};""")
    g.ev("__botUntil('R.cn.end||phase!==\"service\"',150000,1/30)")
    print('end', g.ev("+(R.t/R.dur).toFixed(3)"))
    for o in json.loads(g.ev("JSON.stringify(Object.values(__tl))")): print(o)
    print('lgw', g.ev("JSON.stringify((S.crew||[]).filter(m=>lgServes(m)).map(m=>[m.name,m.lv,crewHere(m)]))"), 'bt', g.ev("JSON.stringify((S.crew||[]).filter(m=>m.role==='bartender').map(m=>[m.name,m.lv,m.duty,crewHere(m)]))"))
    print('errors', g.errors[:3]); g.close(); b.close()
srv.shutdown()
