"""Workflow B's numbers (the user's stress tests A-D): per evening — guests, lost; the waiters' trips (plates per trip,
multi-table); the pass (average, peak, seconds full); the dirty dishes (average, peak, fills, seconds full, table-seconds
waiting for room, washed by whom, seconds of washing by role); the staff's time by job.
  python3 tools/sims/workflow_b_stress.py WORKTREE OUT.json [scenario ...]   scenarios: A (Day 1 new game) B (Days 2-3) C (Day 30 save, a player
  who leaves the staff their jobs) D (Day 92 save, nobody touches anything) D2 (Day 92, the player relieves bottlenecks)"""
import sys, os, json
wt, outp = sys.argv[1], sys.argv[2]
want = sys.argv[3:] or ['A', 'B', 'C', 'D', 'D2']
sys.path.insert(0, os.path.join(wt, 'tests')); os.chdir(wt)
import run_tests as rt, v24_tests as vt
from playwright.sync_api import sync_playwright
NUM = """JSON.stringify((()=>{const st=R.st||{};const ps=st.ps||{},dd=st.dd||{},wb=st.wb||{};return{t:+R.t.toFixed(1),guests:st.guests,lost:st.lost,
  wb,pass:{avg:ps.t?+(ps.occ/ps.t).toFixed(2):0,peak:ps.peak||0,full:+(ps.full||0).toFixed(1),wait:+(ps.wait||0).toFixed(1),noW:+(ps.noW||0).toFixed(1)},
  dd:{avg:dd.t?+(dd.occ/dd.t).toFixed(2):0,peak:dd.peak||0,fulls:dd.fulls||0,full:+(dd.full||0).toFixed(1),block:+(dd.blockT||0).toFixed(1),in:dd.in||0,wash:dd.wash||0,by:dd.by||{},washT:dd.washT||{},starts:dd.starts||0,startAvg:dd.starts?+(dd.startN/dd.starts).toFixed(1):0},wl:st.wl||{},
  dirtyNow:R.tables.filter(t=>t.dirty&&!t.group).length}})())"""
def evening(g, actor, until_summary=True, cap=20000):
    last = None
    for i in range(cap):
        r = g.page.evaluate('()=>window.__bot(30,1/30)')
        if g.ev("phase") != 'service' or not g.ev("!!R"): break
        last = json.loads(g.ev(NUM))
    return last
res = {}
srv, port = rt.start_server()
with sync_playwright() as p:
    b = p.chromium.launch()
    if 'A' in want or 'B' in want:
        for who in ('perfect', 'lazy'):
            g = rt.Game(b, port, 'index', seed=12345, manual=True)
            rt.install_bot(g); g.click('[data-act=open]')
            for d in range(3):
                rt.start_day(g)
                if who == 'lazy': g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;")
                n = evening(g, who)
                s = json.loads(g.ev("JSON.stringify(S.lastSummary&&{guests:S.lastSummary.guests,lost:S.lastSummary.lost,rev:S.lastSummary.rev})"))
                res[f'{who}_day{d+1}'] = {'end': n, 'summary': s}
                print(who, d + 1, s, n and n['dd'], flush=True)
                g.click('[data-act=toShop]')
                if d == 0: g.click('[data-act=buyTable]')
                g.click('[data-act=nextDay]')
            g.close()
    for sc, save, act in (('C', 'player_day30.json', 'lazy'), ('D', 'player_day92_2105.json', 'none'), ('D2', 'player_day92_2105.json', 'relieve')):
        if sc not in want: continue
        if not os.path.exists(os.path.join(wt, 'tests', 'saves', save)): print('no save', save); continue
        g = rt.Game(b, port, 'index', seed=3033, manual=True, viewport={'width': 390, 'height': 844})
        vt.load_save(g, save)
        if g.ev("phase") == 'summary': g.click('[data-act=toShop]'); g.page.wait_for_timeout(60)
        if g.ev("phase") == 'shop': g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(100)
        rt.start_day(g); rt.install_bot(g)
        g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}")
        g.ev("window.__noScenes=true")
        if act == 'lazy': g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;")
        elif act == 'none': g.ev("window.__act=function(){if(!(phase==='service'&&R))return false;for(const g of queued()){if(g.state==='queue'&&!(S.crew||[]).some(m=>m.role==='waiter'&&waiterDoes(m,'seat'))){const t=freeTableFor(g);if(t)seatGroup(g,t)}}return true}")
        else: g.ev(rt.LAZY_ACTOR + "\nwindow.__act=function(){const r=window.__actLazy();if(R&&typeof ddTap==='function'&&!ddS().wash&&ddCount()>=8)ddTap();return r};")
        n = evening(g, act)
        s = json.loads(g.ev("JSON.stringify(S.lastSummary&&{guests:S.lastSummary.guests,lost:S.lastSummary.lost,rev:S.lastSummary.rev})"))
        res[sc] = {'end': n, 'summary': s, 'errors': g.errors[:3]}
        print(sc, s, n and n['dd'], n and n['wb'], n and n['pass'], flush=True)
        g.close()
    b.close()
srv.shutdown()
json.dump(res, open(outp, 'w'), ensure_ascii=False, indent=1)
