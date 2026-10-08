"""The first three days on a phone: Day 1 the fried rice's first place (the stove), Day 2 a latte's (the coffee machine),
Day 3 a salad's (the cutting board) — the card and the lit place, the way the player sees them. python3 tools/qa/onboarding_shots.py WORKTREE OUT"""
import sys, os, json
wt, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True); sys.path.insert(0, os.path.join(wt, 'tests')); os.chdir(wt)
import run_tests as rt
from playwright.sync_api import sync_playwright
srv, port = rt.start_server()
with sync_playwright() as p:
    b = p.chromium.launch()
    for day, dish in ((1, 'friedrice'), (2, 'coffee'), (3, 'salad')):
        g = rt.Game(b, port, 'index', seed=500 + day, manual=True, viewport={'width': 390, 'height': 844})
        g.click('[data-act=open]'); g.page.wait_for_timeout(80)
        if day > 1:
            g.ev(f"S.day={day};S.gate=1;applyGates();for(const d of menuList())S.stock[d]=12;S.tables=3;save()")
            g.ev("phase='prep';showPrep&&showPrep()")
        rt.start_day(g)
        g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}")
        # the floor by itself: seat and take orders, nothing in the kitchen
        g.ev("window.__f=function(){for(const q of queued())if(q.state==='queue'){const t=freeTableFor(q);if(t)seatGroup(q,t)}for(const t of R.tables){const q=t.group;if(q&&q.state==='order'&&!jillTargets(t.i))tapTable(t)}}")
        found = None
        for _ in range(900):
            g.ev("__f();for(const q of R.groups)q.pat=1;__tick(1000/30)")
            found = g.ev(f"(()=>{{const n=(R.wf||[]).find(n=>n.d==='{dish}'&&n.st==='wait');return n?n.id:null}})()")
            if found: break
        if not found: print(day, dish, 'no order'); g.close(); continue
        g.ev(f"(()=>{{R.wsel={found};setRoom('kitchen');renderTickets();wfGuideUpd()}})()")
        for _ in range(3): g.ev("forceDraw=true;__tick(1000/30)")
        g.page.wait_for_timeout(120)
        g.page.screenshot(path=os.path.join(out, f'day{day}_{dish}_first_place.png'))
        guide = g.ev("((document.querySelector('#wfGuide')||{}).innerText||'').replace(/\\n/g,' / ')")
        print(day, dish, 'guide:', guide, 'errors', g.errors[:2], flush=True)
        g.close()
    b.close()
srv.shutdown()
