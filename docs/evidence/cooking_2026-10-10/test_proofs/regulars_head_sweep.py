"""The rc7.2 regular's-head check without holding the staff, over seeds: who takes the order in the frame of the tap
(Jill, or a free waiter under the 2026-10-09 #6 rule). JK_GAME_JS picks the build.  python3 reghead_sweep.py SEED..."""
import sys, os, json
ROOT='/home/user/jills-kitchen'; sys.path.insert(0, os.path.join(ROOT,'tests')); os.chdir(ROOT); seeds=[int(x) for x in sys.argv[1:]]; sys.argv=[sys.argv[0]]
import run_tests as rt, v24_tests as v
from playwright.sync_api import sync_playwright
srv, port = rt.start_server()
with sync_playwright() as p:
    b = p.chromium.launch()
    for seed in seeds:
        g = rt.Game(b, port, 'index', seed=seed, manual=True, viewport={'width': 390, 'height': 844})
        v.load_save(g, 'player_day74_1508.json'); v.to_service(g)
        g.ev("__botUntil('R.groups.some(q=>q.reg&&q.reg!==\\'dylan\\'&&q.table!=null&&[\\'reading\\',\\'eat\\'].includes(q.state))',60000,1/30)")
        info = json.loads(g.ev("""JSON.stringify((()=>{const q=R.groups.find(q=>q.reg&&q.reg!=='dylan'&&q.table!=null&&['reading','eat'].includes(q.state));if(!q)return null;window.__rq=q;const t=R.tables[q.table];setRoom(t.room||'main');return{t:t.i,room:t.room||'main',reg:q.reg,rest:R.jill.rest,jroom:R.jill.room}})())"""))
        if not info: print(json.dumps({'seed':seed,'none':1})); g.close(); continue
        g.ev("window.__act=()=>{};__tick(1000/30)")
        head = "JSON.stringify((()=>{const q=__rq;const p=idMemberAt(q,0);const r=sc.getBoundingClientRect();return[r.left+SV.ox+p.x*SV.s,r.top+SV.oy+(p.y-20)*SV.s]})())"
        g.ev("__rq.state='order';R.jill.q.length=0;$('#regcard').hidden=true;document.querySelectorAll('#plines>*,#toasts>*').forEach(e=>e.remove())")
        free = g.ev("(S.crew||[]).filter(m=>m.role==='waiter'&&R.cw&&R.cw[m.id]&&!R.cw[m.id].task&&(R.cw[m.id].cd||0)<=1/30).length")
        xy = json.loads(g.ev(head)); g.page.mouse.click(xy[0], xy[1]); g.ev("__tick(1000/30)")
        st = json.loads(g.ev("JSON.stringify({card:!$('#regcard').hidden,q:R.jill.q.slice(),cur:R.jill.cur?R.jill.cur.t:null,claim:R.tables[%d].claim||null})" % info['t']))
        jill = info['t'] in st['q'] or st['cur'] == info['t']
        print(json.dumps({'seed':seed,'table':info['t'],'room':info['room'],'jill_rest':info['rest'],'jill_room':info['jroom'],'free_waiters':free,'card':st['card'],'jill_goes':jill,'claimed_by_staff':bool(st['claim'] and st['claim']!='jill')}), flush=True)
        g.close()
    b.close()
srv.shutdown()
