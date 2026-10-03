"""Ken's tasting night with the whole Lounge (later nights, unheld) on the Day 74 save: the night's people, when they sat,
were served, paid; the bartenders; the money. python3 sim_kt.py ROOT seed"""
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
    g.ev("S.cn=null;kenS().next={d:S.day,n:5}")
    v.to_service(g); g.ev("window.__act=window.__actLazy||(()=>{})")
    g.ev("""window.__kt={};const _sg=seatGroup;seatGroup=function(q,t){if(q.tasting)(__kt[q.id]=__kt[q.id]||{n:q.name,s:q.size}).sat=+(R.t/R.dur).toFixed(3);return _sg.apply(this,arguments)};
      const _co=collect;collect=function(q){if(q&&q.tasting)(__kt[q.id]=__kt[q.id]||{n:q.name,s:q.size}).paid=+(R.t/R.dur).toFixed(3);return _co.apply(this,arguments)};
      const _ae=checkAllServed;checkAllServed=function(q){const was=q.state;const r=_ae.apply(this,arguments);if(q.tasting&&was==='wait'&&q.state==='eat')(__kt[q.id]=__kt[q.id]||{n:q.name,s:q.size}).served=+(R.t/R.dur).toFixed(3);return r};""")
    for f in [x / 20 for x in range(4, 21)]:
        g.ev("__botUntil('R.t>=R.dur*%f||phase!==\"service\"',120000,1/30)" % f)
        if g.ev("phase") != 'service': break
        print(f, g.ev("""JSON.stringify({kt:R.kt?{on:R.kt.on,end:R.kt.end}:null,lgIn:R.groups.filter(q=>!q.gone&&q.table!=null&&R.tables[q.table]&&R.tables[q.table].room==='lounge').map(q=>q.state[0]).join(''),glasses:R.tickets.filter(t=>t.lounge).reduce((a,t)=>a+t.items.filter(i=>i.lbar&&i.st==='pending').length,0),bt:(S.crew||[]).filter(m=>m.role==='bartender'&&m.duty==='lbar'&&crewHere(m)).map(m=>m.name+':'+(R.cw[m.id]&&R.cw[m.id].task?R.cw[m.id].task.k:'-')).join(',')})"""))
    g.ev("__botUntil('phase!==\"service\"',120000,1/30)")
    print('per group', g.ev("JSON.stringify(Object.values(__kt))"))
    print('summary', g.ev("JSON.stringify(S.lastSummary?{rev:S.lastSummary.rev,net:S.lastSummary.net,guests:S.lastSummary.guests,lost:S.lastSummary.lost,angry:S.lastSummary.angry,lg:S.lastSummary.lg}:null)"))
    print('errors', g.errors[:3]); g.close(); b.close()
srv.shutdown()
