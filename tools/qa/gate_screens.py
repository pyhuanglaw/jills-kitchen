"""The release gate's phone screens (the user, 2026-10-09 七、視覺及手機操作驗收): the main screens and rooms at phone sizes, the
kitchen's teaching card and pizza oven, a busy evening, the menus — PNGs, and a contact sheet per size to look through.
Desktop Chromium at phone sizes, not an iPhone.   python3 tools/qa/gate_screens.py OUT"""
import sys, os, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'tests')); os.chdir(ROOT); OUT = sys.argv[1]; sys.argv = [sys.argv[0]]
os.makedirs(OUT, exist_ok=True)
import run_tests as rt
import v24_tests as v
from playwright.sync_api import sync_playwright
from PIL import Image
SIZES = [('390x844', 390, 844), ('375x667', 375, 667), ('430x932', 430, 932), ('844x390', 844, 390)]
def shot(g, name, size):
    for _ in range(3): g.ev("forceDraw=true;__tick(1000/30)")
    g.page.wait_for_timeout(150)
    p = os.path.join(OUT, f'{size}_{name}.png'); g.page.screenshot(path=p); return p
def room(g, rm):
    g.ev(f"setRoom('{rm}')"); g.page.wait_for_timeout(60)
srv, port = rt.start_server()
made = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    for size, w, h in SIZES:
        L = made.setdefault(size, [])
        # a new game: the title, the first morning, the first evening, the kitchen's first dish with its card
        g = rt.Game(b, port, 'index', seed=601, manual=True, viewport={'width': w, 'height': h})
        L.append(shot(g, '01_title', size))
        g.click('[data-act=open]'); g.page.wait_for_timeout(120); L.append(shot(g, '02_prep_day1', size))
        rt.start_day(g); g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}")
        g.ev("window.__f=function(){for(const q of queued())if(q.state==='queue'){const t=freeTableFor(q);if(t)seatGroup(q,t)}for(const t of R.tables){const q=t.group;if(q&&q.state==='order'&&!jillTargets(t.i))tapTable(t)}}")
        nid = None
        for _ in range(900):
            g.ev("__f();for(const q of R.groups)q.pat=1;__tick(1000/30)")
            nid = g.ev("(()=>{const n=(R.wf||[]).find(n=>n.st==='wait');return n?n.id:null})()")
            if nid: break
        L.append(shot(g, '03_main_day1', size))
        if nid:
            g.ev(f"(()=>{{setRoom('kitchen');const n=wfNode({nid});const it=n.its[0];wfSelectItem(it.tk,it.it);renderTickets();wfGuideUpd()}})()")
            L.append(shot(g, '04_kitchen_card_day1', size))
        room(g, 'home'); L.append(shot(g, '05_jills_room', size))
        # round 2 (2026-10-10): the rest of the first evening with 秀琴阿姨 on the staff, the first shop's staff tab (hiring after
        # Day 1: a chef and a waiter at the first level), both hired, and Day 2's morning with its news
        room(g, 'main'); rt.install_bot(g); g.ev(v.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;window.__noScenes=true")
        g.ev("__botUntil('phase!==\"service\"',90000,1/30)")
        if g.ev("phase") == 'summary':
            g.click('[data-act=toShop]'); g.page.wait_for_timeout(100)
            g.ev("shopTab='staff';showShop()"); g.page.wait_for_timeout(100); L.append(shot(g, '11_shop_staff_day1', size))
            for k in ('chef', 'waiter'):
                g.ev(f"(()=>{{const el=document.createElement('button');el.dataset.act='hire';el.dataset.k='{k}';$('#screen').appendChild(el);el.click();el.remove()}})()"); g.page.wait_for_timeout(80)
            g.ev("shopTab='staff';showShop()"); g.page.wait_for_timeout(100); L.append(shot(g, '12_shop_staff_hired', size))
            g.ev("shopTab='home';showShop()"); g.page.wait_for_timeout(60)
            g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(150); L.append(shot(g, '13_prep_day2', size))
        g.close()
        if size not in ('390x844',):
            continue
        # the Day 92 save: a busy evening in every room, the pause menu, the shop
        g = rt.Game(b, port, 'index', seed=602, manual=True, viewport={'width': w, 'height': h})
        v.load_save(g, 'player_day92_2105.json'); g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}")
        L.append(shot(g, '06_prep_day92', size))
        v.to_service(g, lazy=True)
        g.ev("__bot(30*90,1/30)")
        for rm in ('front', 'main', 'side', 'kitchen', 'lounge', 'up', 'staff'):
            if g.ev(f"roomsOpen().includes('{rm}')"):
                room(g, rm); L.append(shot(g, f'07_day92_{rm}', size))
        g.page.click('#hPause'); g.page.wait_for_timeout(100); L.append(shot(g, '08_pause', size))
        g.page.click('[data-act=resume]'); g.page.wait_for_timeout(60)
        g.ev("__bot(30*400,1/30)")
        if g.ev("phase") == 'service': g.ev("__botUntil('phase!==\"service\"',60000,1/30)")
        if g.ev("phase") == 'summary': L.append(shot(g, '09_summary', size)); g.click('[data-act=toShop]'); g.page.wait_for_timeout(100)
        for tab in g.page.evaluate("()=>[...document.querySelectorAll('#screen .tabs [data-act=tab]')].filter(e=>!e.disabled&&e.getAttribute('aria-disabled')!=='true').map(e=>e.dataset.k)"):
            g.page.click(f'#screen .tabs [data-act=tab][data-k={tab}]'); g.page.wait_for_timeout(80); L.append(shot(g, f'10_shop_{tab}', size))
        g.close()
    b.close()
srv.shutdown()
for size, L in made.items():
    ims = [Image.open(x) for x in L if os.path.exists(x)]
    if not ims: continue
    tw = 260; th = int(ims[0].height * tw / ims[0].width); cols = 6; rows = (len(ims) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * tw, rows * th), 'white')
    for i, im in enumerate(ims): sheet.paste(im.convert('RGB').resize((tw, th)), ((i % cols) * tw, (i // cols) * th))
    sheet.save(os.path.join(OUT, f'sheet_{size}.png')); print(size, len(ims), 'screens')
