"""Repro of cooking_the_card_says_who_has_it_and_a_dish_can_be_taken_back up to the failing check, printing the card's
text and Jill's state right after the take-back, then for a few frames.  python3 repro.py ROOT [JK_GAME_JS]"""
import sys, os, json
ROOT = sys.argv[1]; sys.path.insert(0, os.path.join(ROOT, 'tests')); os.chdir(ROOT)
if len(sys.argv) > 2: os.environ['JK_GAME_JS'] = sys.argv[2]
sys.argv = [sys.argv[0]]
import run_tests as rt
import cooking_tests as ct
from playwright.sync_api import sync_playwright
srv, port = rt.start_server()
with sync_playwright() as p:
    b = p.chromium.launch()
    ADE = "{id:'t_ade',role:'chef',name:'阿德師傅',lv:3,duty:'bar',since:1,days:0,pool:'restaurant'}"
    g = ct._day(b, port, 'index', 7140, f"S.level=3;S.eq.bar=1;S.crew.push({ADE})")
    g.ev("window.__patient=1")
    g.ev("window.__hold=true;{const W=wfStaff;wfStaff=function(){if(window.__hold)return;return W.apply(this,arguments)}}")
    print('order', ct._wait_orders(g, 1))
    nid = g.ev("(()=>{wfGather();return wfList()[0].id})()")
    g.ev(f"(()=>{{const n=wfNode({nid});wfSelectItem(n.its[0].tk,n.its[0].it)}})()"); g.ev("__run(1)")
    print('card waiting:', repr(g.ev(ct.GUIDE)))
    g.ev("window.__hold=false")
    print('cook takes it', ct._until(g, f"wfNode({nid}).who==='t_ade'", step=1))
    g.ev("__run(4)")
    print('card on his way:', repr(g.ev(ct.GUIDE)))
    J = "JSON.stringify((()=>{const J=R.jill;return{x:Math.round(J.x),y:Math.round(J.y),room:J.room,troom:J.troom,tx:J.tx,ty:J.ty,cur:J.cur&&J.cur.t,q:J.q.length,petGo:!!J.petGo,pet:!!J.pet,rest:!!J.rest,visit:!!J.visit,kcur:J.kcur||null,hands:(J.hands||[]).length,idle:+(J.idle||0).toFixed(2),calm:+(J.calm||0).toFixed(2),wq:wfJ().wq,wcur:wfJ().cur||null}})())"
    print('Jill before the tap:', g.ev(J))
    ct._tap_slot(g, f"wfNode({nid}).to")
    st = g.ev(f"JSON.stringify((()=>{{const n=wfNode({nid});return{{who:n.who,st:n.st,si:n.si,to:n.to&&n.to.no}}}})())")
    print('after the tap:', st)
    print('card after the tap:', repr(g.ev(ct.GUIDE)))
    print('Jill after the tap:', g.ev(J))
    for k in range(6):
        g.ev("__run(1)")
        print(f'  +{k+1} frame card:', repr(g.ev(ct.GUIDE))[:160], '| Jill', g.ev(J)[:300])
    g.close(); b.close()
srv.shutdown()
