"""The Day 52 test's loop (tools/sims/day52_seeds.py) with one change: each morning's draw (the day's weather, its event, its
tasks — planToday at nextDay) comes from its own seeded stream (BASE+500000+d) instead of whatever the evening before left in
the random state. So two builds get the same weather on the same seed (unless a sudden shower, rainstart, changes the next
morning's odds). Also prints each day's weather (planned at nextDay, recorded by the story at the day's end).
python3 day52_wxseed.py ROOT SEEDBASE"""
import sys, os, json
ROOT = sys.argv[1]; BASE = int(sys.argv[2]); sys.path.insert(0, os.path.join(ROOT, 'tests')); os.chdir(ROOT); sys.argv = [sys.argv[0]]
import run_tests as rt
import v24_tests as vt
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    srv, port = rt.start_server(); b = p.chromium.launch()
    g = rt.Game(b, port, 'index', seed=254, manual=True, viewport={'width': 390, 'height': 844})
    vt.load_save(g, 'player_day52.json'); g.ev("window.__fastSay=1")
    seed = "Math.random=(function(){let a=%d;return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
    g.ev("window.__wxSeed=null;const __pt0=planToday;planToday=function(){if(window.__wxSeed!=null){" + (seed % 0).replace('let a=0','let a=window.__wxSeed') + "}return __pt0.apply(this,arguments)}")
    first = None; days = []; wx = []
    for d in range(40):
        if g.ev("phase") == 'summary': g.click('[data-act=toShop]'); g.page.wait_for_timeout(60)
        g.ev("window.__wxSeed=%d" % (BASE + 500000 + d))
        if g.ev("phase") == 'shop': g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(100)
        planned = g.ev("S.today?S.today.weather:null"); g.ev("window.__wxSeed=null")
        g.ev(seed % (BASE + d)); g.ev("S.today.sugKey=null;S.today.sug=null;autoStock()")
        rt.start_day(g); rt.install_bot(g); g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;window.__noScenes=true")
        if first is None: first = g.ev("S.day")
        for _ in range(1200):
            r = g.page.evaluate('()=>window.__bot(150,1/30)')
            if g.ev("phase") != 'service' or not g.ev("!!R"): break
            if r['ticks'] < 150: break
        if g.ev("phase") == 'service':
            g.ev("closeShop('x');for(const q of R.groups.slice())leaveGroup(q,'ok')"); g.page.evaluate('()=>window.__bot(400,1/30)')
        if g.ev("phase") == 'service': g.ev("finishClosing()")
        wx.append([g.ev("S.day"), planned, g.ev("v24().wx[S.day]||null")])
        ev = g.ev("JSON.stringify(S.lastSummary?{d:S.lastSummary.day,g:S.lastSummary.guests,l:S.lastSummary.lost,a:S.lastSummary.angry,w:S.lastSummary.avg,r:S.lastSummary.rev}:null)")
        if ev and ev != 'null': days.append(json.loads(ev))
    F = json.loads(g.ev("JSON.stringify(Object.fromEntries(%s.map(k=>[k,fact(k)?fact(k).d:null])))" % json.dumps(vt.V24_KEYS)))
    print(json.dumps({'base': BASE, 'first': first, 'yj_key': F.get('yj_key'), 'wall_worry': F.get('wall_worry'), 'wall_settle': F.get('wall_settle'), 'F': F,
                      'evenings': {k: round(sum(x[k] or 0 for x in days) / max(1, len(days)), 1) for k in 'glawr'}, 'days': days, 'wx': wx}, ensure_ascii=False), flush=True)
    g.close(); b.close(); srv.shutdown()
