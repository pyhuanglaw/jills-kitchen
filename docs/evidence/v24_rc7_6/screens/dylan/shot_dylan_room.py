"""Jill's room at gameplay scale (390x844), the prep sheet put away ("看店裡"), Dylan at his desk. python3 shot_dylan_room.py ROOT OUT"""
import sys, os
ROOT = sys.argv[1]; OUT = sys.argv[2].rstrip('/') + '/'
sys.path.insert(0, ROOT + '/tests'); os.chdir(ROOT)
import run_tests as rt, v24_tests as v
from playwright.sync_api import sync_playwright
os.makedirs(OUT, exist_ok=True)
srv, port = rt.start_server()
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, save in (('d74', 'player_day74_1508.json'), ('d52', 'player_day52.json')):
        g = rt.Game(b, port, 'index', seed=7602, manual=True, viewport={'width': 390, 'height': 844})
        v.load_save(g, save)
        btn = g.page.locator('[data-act="peek"]')
        print(name, 'peek buttons', btn.count())
        if btn.count(): btn.first.click()
        g.ev("setRoom('home')"); g.ev("for(let i=0;i<8;i++)__tick(1000/30)"); g.ev("document.querySelectorAll('#plines>*,#toasts>*').forEach(e=>e.remove())")
        g.page.wait_for_timeout(150); g.page.screenshot(path=OUT + f'03_{name}_room_gameplay_scale.png')
        print('errors', g.errors[:3]); g.close()
    b.close()
srv.shutdown()
