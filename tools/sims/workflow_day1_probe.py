"""Day 1 the way golden_frames plays it (seed 2024, the perfect bot, the real main loop): when the evening closes, and what
the dirty dishes did on the way. python3 tools/sims/workflow_day1_probe.py WORKTREE"""
import sys, os, json
wt = sys.argv[1]
sys.path.insert(0, os.path.join(wt, 'tests')); os.chdir(wt)
import run_tests as rt
from playwright.sync_api import sync_playwright
LOG = """JSON.stringify({t:+R.t.toFixed(0),q:queued().length,groups:R.groups.length,
 dirty:R.tables.filter(t=>t.dirty&&!t.group).length,free:R.tables.filter(t=>!t.dirty&&!t.group).length,
 dd:typeof ddCount==='function'?ddCount():null,jh:(R.jill.hands||[]).filter(e=>e.k==='dirty').length,
 xq:!!R.xqh,wash:typeof ddS==='function'&&ddS().wash?ddS().wash.who:null,guests:R.st.guests,lost:R.st.lost,closed:!!R.closed})"""
srv, port = rt.start_server()
with sync_playwright() as p:
    b = p.chromium.launch()
    g = rt.Game(b, port, 'index', seed=2024, manual=True)
    rt.install_bot(g)
    g.ev("__tick(500)"); g.click('[data-act=open]'); g.ev("__tick(1000/30)")
    rt.start_day(g)
    g.ev("__play(600, 30)"); g.ev("__play(900, 30, '(R.wf||[]).length>0')")
    for i in range(80):
        r = g.ev("__play(300, 0, 'R.closing!=null&&R.closing>5')")
        if g.ev("phase") != 'service' or not g.ev("!!R"): break
        print(g.ev(LOG), flush=True)
        if g.ev("R.closing!=null&&R.closing>5"): break
    print('END', g.ev("JSON.stringify({t:R.t,dur:R.dur,dd:R.st.dd||null,wb:R.st.wb||null,ps:R.st.ps||null,guests:R.st.guests,lost:R.st.lost})"))
    g.close(); b.close()
srv.shutdown()
