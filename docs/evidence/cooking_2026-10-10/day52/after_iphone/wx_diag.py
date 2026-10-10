"""The forty-days loop (the Day 52 test's own) for DAYS days: each day's weather as planned (S.today.weather), what the story
recorded (v24().wx), and the wall's facts.  python3 wx_diag.py ROOT BASE DAYS"""
import sys, os, json
ROOT = sys.argv[1]; BASE = int(sys.argv[2]); DAYS = int(sys.argv[3]); sys.path.insert(0, os.path.join(ROOT, 'tests')); os.chdir(ROOT); sys.argv = [sys.argv[0]]
import run_tests as rt
import v24_tests as vt
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    srv, port = rt.start_server(); b = p.chromium.launch()
    g = rt.Game(b, port, 'index', seed=254, manual=True, viewport={'width': 390, 'height': 844})
    vt.load_save(g, 'player_day52.json'); g.ev("window.__fastSay=1")
    seed = "Math.random=(function(){let a=%d;return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
    for d in range(DAYS):
        if g.ev("phase") == 'summary': g.click('[data-act=toShop]'); g.page.wait_for_timeout(60)
        planned_before = g.ev("S.today?S.today.weather:null")
        if g.ev("phase") == 'shop': g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(100)
        planned = g.ev("S.today?S.today.weather:null")
        g.ev(seed % (BASE + d)); g.ev("S.today.sugKey=null;S.today.sug=null;autoStock()")
        rt.start_day(g); rt.install_bot(g); g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;window.__noScenes=true")
        at_start = g.ev("JSON.stringify({day:S.day,wx:S.today.weather,R:R&&R.weather,rec:v24().wx[S.day]||null})")
        for _ in range(1200):
            r = g.page.evaluate('()=>window.__bot(150,1/30)')
            if g.ev("phase") != 'service' or not g.ev("!!R"): break
            if r['ticks'] < 150: break
        if g.ev("phase") == 'service':
            g.ev("closeShop('x');for(const q of R.groups.slice())leaveGroup(q,'ok')"); g.page.evaluate('()=>window.__bot(400,1/30)')
        if g.ev("phase") == 'service': g.ev("finishClosing()")
        end = g.ev("JSON.stringify({rec:v24().wx[S.day]||null,photos:fact('wall_photos')?fact('wall_photos').d:null,visit:fact('wall_visit')?fact('wall_visit').d:null})")
        print(json.dumps({'planned_at_nextDay': planned, 'start': json.loads(at_start), 'end': json.loads(end)}, ensure_ascii=False), flush=True)
    g.close(); b.close(); srv.shutdown()
