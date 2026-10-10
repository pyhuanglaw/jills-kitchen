import sys, os, json
ROOT=os.environ.get('ROOT','/home/user/jills-kitchen'); sys.path.insert(0, os.path.join(ROOT,'tests')); os.chdir(ROOT); sys.argv=[sys.argv[0]]
import run_tests as rt, v24_tests as v
from playwright.sync_api import sync_playwright
srv, port = rt.start_server()
with sync_playwright() as p:
    b = p.chromium.launch(); g = rt.Game(b, port, 'index', seed=2229, manual=True, viewport={'width': 390, 'height': 844})
    v.load_save(g, 'player_day74_1508.json'); v.to_service(g)
    g.ev("__botUntil('R.groups.some(q=>q.reg&&q.reg!==\\'dylan\\'&&q.table!=null&&[\\'reading\\',\\'eat\\'].includes(q.state))',60000,1/30)")
    info = json.loads(g.ev("""JSON.stringify((()=>{const q=R.groups.find(q=>q.reg&&q.reg!=='dylan'&&q.table!=null&&['reading','eat'].includes(q.state));if(!q)return null;window.__rq=q;window.__st0=q.state;const t=R.tables[q.table];setRoom(t.room||'main');return{t:t.i,room:t.room||'main',reg:q.reg,rt:R.t}})())"""))
    print('info', info)
    g.ev("window.__act=()=>{};__tick(1000/30)")
    head = "JSON.stringify((()=>{const q=__rq;const p=idMemberAt(q,0);const r=sc.getBoundingClientRect();return[r.left+SV.ox+p.x*SV.s,r.top+SV.oy+(p.y-20)*SV.s,p.x,p.y-20]})())"
    clear = "document.querySelectorAll('#plines>*,#toasts>*').forEach(e=>e.remove())"
    g.ev("__rq.state='order';R.jill.q.length=0;$('#regcard').hidden=true;" + clear)
    xy = json.loads(g.ev(head)); print('xy', xy)
    print('up0', g.ev("JSON.stringify({up:upSearching(),srFirst:!!(R&&R.srFirst),plan:LIFE.plan,act:LIFE.jill&&LIFE.jill.act})"))
    print('before', g.ev("""JSON.stringify((()=>{const J=R.jill;const t=R.tables[__rq.table];return{room:J.room,troom:J.troom,cur:J.cur,q:J.q,pet:J.pet,visit:!!J.visit,rest:J.rest,claim:t.claim,going:jillGoing(t.i),act:tableActionable(t),cats:CATS.filter(c=>!c.hidden&&Math.hypot(c.x-%f,c.y-%f)<40).map(c=>c.def.id),paused,DLG:!!DLG,phase,curRoom:typeof room!=='undefined'?room:null}})())""" % (xy[2], xy[3]+20)))
    print('elem', g.ev(f"(()=>{{const e=document.elementFromPoint({xy[0]},{xy[1]});return e?(e.id||e.className||e.tagName):null}})()"))
    g.ev("window.__log=[];{const T0=tapTable;tapTable=function(t){__log.push('tapTable '+t.i+' claim='+t.claim+' st='+(t.group&&t.group.state));return T0.apply(this,arguments)}}{const A0=jillAsk;jillAsk=function(i){__log.push('jillAsk '+i);const r=A0.apply(this,arguments);__log.push('q after ask '+JSON.stringify(R.jill.q));return r}}{const T1=toast;toast=function(m){__log.push('toast '+m);return T1.apply(this,arguments)}}")
    g.page.mouse.click(xy[0], xy[1]); print('log after click', g.ev("JSON.stringify(__log)")); g.ev("__tick(1000/30)"); print('log after tick', g.ev("JSON.stringify(__log)")); print('up', g.ev("JSON.stringify({up:upSearching(),srFirst:!!(R&&R.srFirst),plan:LIFE.plan,act:LIFE.jill&&LIFE.jill.act,rest:R.jill.rest,room:R.jill.room,fact:Object.keys(story().facts).filter(k=>/^up_|^sr_/.test(k)).slice(-8)})"))
    print('after', g.ev("""JSON.stringify((()=>{const J=R.jill;const t=R.tables[__rq.table];return{card:!$('#regcard').hidden,q:J.q,cur:J.cur?J.cur.t:null,claim:t.claim,toasts:[...document.querySelectorAll('#toasts>*')].map(e=>e.innerText),pl:[...document.querySelectorAll('#plines>*')].map(e=>e.innerText),hearts:CATS.filter(c=>c.hearts&&c.hearts.length).map(c=>c.def.id)}})())"""))
    g.close(); b.close()
srv.shutdown()
