import sys, os, json
ROOT=os.environ.get('ROOT','/home/user/jills-kitchen'); sys.path.insert(0, os.path.join(ROOT,'tests')); os.chdir(ROOT); sys.argv=[sys.argv[0]]
import run_tests as rt
from playwright.sync_api import sync_playwright
srv, port = rt.start_server()
with sync_playwright() as p:
    b = p.chromium.launch(); g = rt.Game(b, port, 'index', seed=14, manual=True)
    rt.install_bot(g)
    g.ev("__tick(100)")
    g.click('[data-act=open]'); rt.start_day(g)
    g.ev("for(const t of R.tables)t.dirty=true;__tick(1000/30)")
    for _ in range(60):
        if g.ev("queued().some(x=>x.state==='queue'&&!x.moving)"): break
        g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
    gid = g.ev("(()=>{const q=queued().find(x=>x.state==='queue'&&!x.moving);return q?q.id:null})()")
    print('gid', gid)
    print(g.ev("JSON.stringify(R.tables.map(t=>({i:t.i,room:t.room,dirty:t.dirty,g:t.group?t.group.id:null,claim:t.claim,seats:t.seats})))"))
    print(g.ev("JSON.stringify(queued().map(q=>({id:q.id,st:q.state,mv:q.moving,size:q.size,room:q.room})))"))
    gx, gy = g.ev(f"(()=>{{R.tables[0].dirty=false;const q=R.groups.find(x=>x.id==={gid});return[q.x,q.y-22]}})()")
    g.ev("setRoom('front')"); g.ev("__tick(1000/30)")
    print(g.ev(f"""(()=>{{const q=R.groups.find(x=>x.id==={gid});const t=freeTableFor(q);return JSON.stringify({{paused:typeof paused!=='undefined'?paused:null,dlg:!!DLG,dlgHidden:$('#dlg').hidden,phase,room:typeof room!=='undefined'?room:null,qstate:q.state,qroom:q.room,size:q.size,free:t?t.i:null,t0:{{dirty:R.tables[0].dirty,group:!!R.tables[0].group,claim:R.tables[0].claim,seats:R.tables[0].seats}},hold:typeof R.hold!=='undefined'?R.hold:null,fq:frontQueueAt({{x:q.x,y:q.y-22}})?frontQueueAt({{x:q.x,y:q.y-22}}).id:null}})}})()"""))
    pt = g.ev(f"(()=>{{const r=sc.getBoundingClientRect();return[r.left+SV.ox+({gx})*SV.s,r.top+SV.oy+({gy})*SV.s]}})()")
    print('elem at point', g.ev(f"(()=>{{const e=document.elementFromPoint({pt[0]},{pt[1]});return e?(e.id||e.className||e.tagName):null}})()"))
    g.page.mouse.click(pt[0], pt[1]); g.ev("__tick(1000/30)")
    print(g.ev(f"(()=>{{const q=R.groups.find(x=>x.id==={gid});return JSON.stringify({{table:q.table,state:q.state,toasts:[...document.querySelectorAll('.toast')].map(e=>e.innerText).slice(-3)}})}})()"))
    g.close(); b.close()
srv.shutdown()
