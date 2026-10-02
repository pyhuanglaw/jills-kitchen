"""golden_frames' own steps up to day 2, t = 75 s (sample #75), then a screenshot and the scene's canvas. JK_GAME_JS picks
the build. python3 gf_day2.py ROOT OUT.png"""
import sys, os, json, base64
ROOT = sys.argv[1]; OUT = sys.argv[2]
sys.path.insert(0, ROOT + '/tests'); os.chdir(ROOT)
import run_tests as rt
from playwright.sync_api import sync_playwright
srv, port = rt.start_server()
with sync_playwright() as p:
    b = p.chromium.launch()
    g = rt.Game(b, port, 'index', seed=2024, manual=True)
    rt.install_bot(g)
    def shot(name):
        g.ev("__tick(1000/30)"); g.page.screenshot(animations='disabled', caret='hide')
    g.ev("__tick(500)"); shot('title')
    g.click('[data-act=open]'); g.ev("__tick(1000/30)"); shot('prep')
    for d in range(2):
        rt.start_day(g)
        if d == 1:
            r = g.ev("__play(%d, 30)" % (75 * 30 + 1))
            s = r['samples'][-1]
            print('t', s.get('t'), 'keys', list(s.keys())[:12])
            g.page.screenshot(path=OUT, animations='disabled', caret='hide')
            print('log', g.ev("JSON.stringify(dayLog().slice(-6).map(l=>l.c+' '+l.w+'：'+l.t))"))
            break
        r1 = g.ev("__play(600, 30)")
        shot('service_20s')
        g.ev("__play(900, 30, 'R.slots.some(s=>s.job)')")
        g.ev("(()=>{const i=R.slots.findIndex(s=>s.job);R.focus=i;R.panel=true})()"); shot('service_panel'); g.ev("R.panel=false")
        g.page.click('#hPause'); shot('pause'); g.click('[data-act=resume]')
        g.ev("__play(20000, 30, 'R.closing!=null&&R.closing>5')"); shot('evening')
        g.ev("__play(20000, 30)")
        shot('summary'); g.click('[data-act=toShop]'); shot('shop'); g.click('[data-act=nextDay]')
        g.click('[data-act=book]'); g.click('[data-act=btab][data-k=cats]'); shot('book_cats')
        g.click('[data-act=btab][data-k=mem]'); shot('book_mem'); g.click('[data-act=closeSub]')
    g.close(); b.close()
srv.shutdown()
