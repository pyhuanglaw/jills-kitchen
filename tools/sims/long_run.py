"""Long play for the release gate (the user, 2026-10-09: 「Fresh save／中期存檔／後期存檔：連續模擬 30 個遊戲日，至少三組不同種子，
營業途中儲存、關閉、重新載入」). From a new game or one of the user's saves, N days played by the test player who leaves to the staff
what they cover and taps the rest (LAZY_ACTOR), each morning's luck seeded from (seed, day). On the reload days the evening is
saved as the game saves it (checkpointSave), the page is closed and opened again, and 繼續營業 brings it back. One JSON line per day:
the summary (guests, lost, net, money), the reload (groups before and after), page errors, state invariants, a service that had
to be closed by force (stuck), at most one Jill in the rooms at any look, and how many of the stories' beats have happened.
  python3 tools/sims/long_run.py START SEED [DAYS=30] [RELOAD_DAYS=3,12,24]     START: fresh | a file in tests/saves"""
import sys, os, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'tests')); os.chdir(ROOT)
START, SEED = sys.argv[1], int(sys.argv[2]); DAYS = int(sys.argv[3]) if len(sys.argv) > 3 else 30
RELOADS = {int(x) for x in (sys.argv[4] if len(sys.argv) > 4 else '3,12,24').split(',') if x}
sys.argv = [sys.argv[0]]
import run_tests as rt
import v24_tests as v
from playwright.sync_api import sync_playwright
SEEDJS = "Math.random=(function(){let a=%d;return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
def actor(g):
    rt.install_bot(g); g.ev(v.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;window.__noScenes=true")
srv, port = rt.start_server()
with sync_playwright() as p:
    b = p.chromium.launch()
    g = rt.Game(b, port, 'index', seed=SEED, manual=True, viewport={'width': 390, 'height': 844})
    if START == 'fresh':
        g.click('[data-act=open]')
    else:
        v.load_save(g, START)
    g.ev("window.__fastSay=1")
    for d in range(DAYS):
        if g.ev("phase") == 'summary':
            g.click('[data-act=toShop]'); g.page.wait_for_timeout(60)
        if g.ev("phase") == 'shop':
            g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(100)
        for _ in range(30):
            if g.ev("typeof DLG!=='undefined'&&!!DLG"): g.ev("dlgNext()")
        g.ev(SEEDJS % (SEED * 1000 + d)); g.ev("S.today.sugKey=null;S.today.sug=null;autoStock()")
        day = g.ev("S.day"); f0 = g.ev("Object.keys((story()||{}).facts||{}).length")
        rt.start_day(g); actor(g)
        rec = {'start': START, 'seed': SEED, 'day': day, 'reload': None, 'stuck': 0, 'two_jills': 0}
        reloaded = d in RELOADS
        for k in range(1500):
            r = g.page.evaluate('()=>window.__bot(150,1/30)')
            if g.ev("phase") != 'service' or not g.ev("!!R"): break
            if g.ev("!!R.jk"): rec['two_jills'] += 1
            if reloaded and g.ev("R.t>R.dur*.4&&R.closing==null"):
                reloaded = False
                n0 = g.ev("R.groups.length"); ok = g.ev("checkpointSave('test')")
                g.reload(); g.click('[data-act=open]'); g.page.wait_for_timeout(200)
                for _ in range(30):
                    if g.ev("typeof DLG!=='undefined'&&!!DLG"): g.ev("dlgNext()")
                ph = g.ev("phase"); n1 = g.ev("R?R.groups.length:-1")
                rec['reload'] = {'saved': ok, 'phase': ph, 'groups': [n0, n1]}
                if ph != 'service': break
                actor(g)
            if r['ticks'] < 150: break
        if g.ev("phase") == 'service':
            rec['stuck'] = 1
            g.ev("closeShop('x');for(const q of R.groups.slice())leaveGroup(q,'ok')"); g.page.evaluate('()=>window.__bot(400,1/30)')
        if g.ev("phase") == 'service': g.ev("finishClosing()")
        s = json.loads(g.ev("JSON.stringify(S.lastSummary?{guests:S.lastSummary.guests,lost:S.lastSummary.lost,net:S.lastSummary.net,rev:S.lastSummary.rev,day:S.lastSummary.day}:null)"))
        rec.update(summary=s, money=g.ev("S.money"), level=g.ev("S.level"), crew=g.ev("(S.crew||[]).length"),
                   facts=g.ev("Object.keys((story()||{}).facts||{}).length") - f0, errors=g.errors[:2], bad=g.ev(rt.INV))
        g.errors.clear() if hasattr(g.errors, 'clear') else None
        print(json.dumps(rec, ensure_ascii=False), flush=True)
    g.close(); b.close()
srv.shutdown()
