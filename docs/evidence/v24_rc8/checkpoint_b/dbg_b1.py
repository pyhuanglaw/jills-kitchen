"""Checkpoint B smoke: Day 1 《隔壁》 in a new game (held, staged in the hall), the bell; headless (T, not O).
python3 dbg_b1.py ROOT OUT"""
import sys, os, json, base64
ROOT = sys.argv[1]; OUT = sys.argv[2].rstrip('/') + '/'
sys.path.insert(0, ROOT + '/tests'); os.chdir(ROOT)
import run_tests as rt, v24_tests as v
from playwright.sync_api import sync_playwright
os.makedirs(OUT, exist_ok=True)
srv, port = rt.start_server()
log = []
def clean(g):
    g.ev("document.querySelectorAll('#plines>*,#toasts>*,#banner>*').forEach(e=>e.remove())")
def shot(g, name):
    clean(g); g.page.wait_for_timeout(120); g.page.screenshot(path=OUT + name); print('  shot', name, flush=True)
def save_url(url, path): open(path, 'wb').write(base64.b64decode(url.split(',')[1]))
def crop(g, name, x, y, w, h, k=3):
    clean(g)
    url = g.ev(f"(()=>{{const s=SV.s*DPR;const cv=document.createElement('canvas');cv.width={w}*{k};cv.height={h}*{k};const c=cv.getContext('2d');c.drawImage(sc,(SV.ox+({x})*SV.s)*DPR,(SV.oy+({y})*SV.s)*DPR,{w}*s,{h}*s,0,0,{w}*{k},{h}*{k});return cv.toDataURL('image/png')}})()")
    save_url(url, OUT + name); print('  saved', name, flush=True)
def panel(g):
    return g.ev("(()=>{const t=document.querySelector('#dlg .dlg-text');const n=document.querySelector('#dlg .dlg-name');return DLG?((n?n.textContent:'')+'：'+(t?t.textContent:'')):''})()")
with sync_playwright() as p:
    b = p.chromium.launch()
    g = rt.Game(b, port, 'index', seed=9101, manual=True, viewport={'width': 390, 'height': 844})
    g.ev("__tick(500)"); g.click('[data-act=open]'); g.page.wait_for_timeout(150)
    g.ev("window.__noScenes=false;window.__holds=true")
    rt.start_day(g); rt.install_bot(g)
    g.ev("for(let i=0;i<3;i++)__tick(1000/30)")
    log.append('day %s, phase %s, room %s, held %s, fact %s' % (g.ev("S.day"), g.ev("phase"), g.ev("room"), g.ev("!!(DLG&&DLG.hold)"), g.ev("!!fact('lin_hello')")))
    lines = []; k = 0
    for i in range(30):
        if not g.ev("!!DLG"): break
        t = panel(g); lines.append(t)
        if i == 1: shot(g, 'b01_day1_madame_lin_at_the_door.png')
        if '小紙盒' in t: shot(g, 'b02_day1_the_present_illus_slot.png')
        g.ev("__tick(400);dlgNext()"); g.ev("for(let j=0;j<2;j++)__tick(1000/30)")
    log.append('lines: ' + ' / '.join(lines))
    g.ev("for(let i=0;i<6;i++)__tick(1000/30)")
    log.append('after: bell %s, STAGE %s, room %s, jill %s' % (g.ev("propOn('linbell')"), g.ev("STAGE===null"), g.ev("room"), g.ev("JSON.stringify({x:Math.round(R.jill.x),y:Math.round(R.jill.y),room:R.jill.room})")))
    shot(g, 'b03_day1_after_the_scene.png')
    crop(g, 'b04_the_bell_on_the_door.png', 20, 0, 90, 80, 4)
    g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy")
    g.ev("__botUntil('phase!==\"service\"',200000,1/30)")
    log.append('day 1 ends: phase %s, errors %s' % (g.ev("phase"), g.errors[:3]))
    g.close(); b.close()
srv.shutdown()
open(OUT + 'log.txt', 'w', encoding='utf-8').write('\n'.join(log) + '\n'); print('\n'.join(log))
