"""golden_frames evidence (rc7): the DOM pieces the frame samples hash, on DAY 2 (the first 12 samples) — the day whose
samples all differ — from a given worktree, to diff the old build against the current one. Day 1 is played the way
golden_frames plays it (to the summary, the shop, the next day). usage: dom_dump_day2.py ROOT OUT.json"""
import sys, os, json
ROOT = sys.argv[1]; sys.path.insert(0, os.path.join(ROOT, 'tests'))
import run_tests as rt
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    srv, port = rt.start_server(); b = p.chromium.launch()
    g = rt.Game(b, port, 'index', seed=2024, manual=True)
    rt.install_bot(g)
    g.ev("__tick(500)"); g.ev("__tick(1000/30)")
    g.click('[data-act=open]'); g.ev("__tick(1000/30)")
    rt.start_day(g); g.ev("__play(20000, 30)")
    g.click('[data-act=toShop]'); g.click('[data-act=nextDay]')
    rt.start_day(g)
    out = []
    for i in range(12):
        g.ev("__play(30, 0)")
        out.append(json.loads(g.ev("JSON.stringify(['#hud','#tickets','#taskPanel','#banner','#toasts','#coach','#screen'].map(q=>{const e=$(q);return[q,e.hidden,e.innerHTML.replace(/data:image\\/png;base64,[A-Za-z0-9+\\/=]+/g,'DATAURL')]}))")))
    json.dump(out, open(sys.argv[2], 'w'), ensure_ascii=False, indent=0)
    g.close(); b.close(); srv.shutdown()
print('ok')
