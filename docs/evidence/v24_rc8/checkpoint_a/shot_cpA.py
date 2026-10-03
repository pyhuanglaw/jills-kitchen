"""Checkpoint A (the player's brief of 2026-10-02 19:19 §26): the bar next door and the street, at 390x844 and on a desktop,
from the player's saves (headless Chromium: T, not O).
python3 shot_cpA.py ROOT OUT"""
import sys, os, json, base64
ROOT = sys.argv[1]; OUT = sys.argv[2].rstrip('/') + '/'
sys.path.insert(0, ROOT + '/tests'); os.chdir(ROOT)
import run_tests as rt, v24_tests as v
from playwright.sync_api import sync_playwright
os.makedirs(OUT, exist_ok=True)
srv, port = rt.start_server()
log = []
def shot(g, name):
    g.ev("try{if(typeof hud==='function')hud(true)}catch(e){}")
    g.ev("document.querySelectorAll('#plines>*,#toasts>*').forEach(e=>e.remove())")
    g.page.wait_for_timeout(150); g.page.screenshot(path=OUT + name); print('  shot', name, flush=True)
def go(g, rm, n=6):
    g.ev(f"setRoom('{rm}')"); g.ev(f"for(let i=0;i<{n};i++)__tick(1000/30)")
def at(g, frac):
    g.ev(f"__botUntil('R.t>=R.dur*{frac}||phase!==\"service\"',150000,1/30)")
with sync_playwright() as p:
    b = p.chromium.launch()
    for vp, tag in (({'width': 390, 'height': 844}, 'phone'), ({'width': 1280, 'height': 800}, 'desk')):
        # Day 2 (no Lounge): Madame Lin's bar next door, open — the afternoon and the night
        g = rt.Game(b, port, 'index', seed=8101, manual=True, viewport=vp)
        v.load_save(g, 'player_day2_2155.json')
        log.append(f'{tag} Day 2: barState=' + g.ev("barState()") + ' loungeLv=' + str(g.ev("loungeLv()")) + ' tabs=' + g.ev("JSON.stringify(roomsOpen().map(roomTabName))"))
        v.to_service(g); g.ev("window.__act=window.__actLazy")
        at(g, .06); go(g, 'front'); shot(g, f'a01_{tag}_day2_street_afternoon_madame_lins_bar.png')
        at(g, .85); go(g, 'front'); shot(g, f'a02_{tag}_day2_street_night_the_bar_lit.png')
        go(g, 'main'); shot(g, f'a03_{tag}_day2_main_hall_no_door_to_it.png')
        # inside, before it is Jill's (a scene will show it: the viewing, the signing)
        g.ev("BARV=1;renderRoomTabs(true)"); go(g, 'lounge', 8); shot(g, f'a04_{tag}_inside_madame_lins_bar.png')
        log.append(f'{tag} inside: tab=' + g.ev("roomTabName('lounge')"))
        g.ev("BARV=null;setRoom('main');renderRoomTabs(true)")
        # closed after her last night; papered over after the signing
        g.ev("factSet('lin_closed')"); go(g, 'front'); shot(g, f'a05_{tag}_street_closed_after_her_last_night.png')
        g.ev("factSet('lin_signed')"); g.ev("try{for(const k in BGC)delete BGC[k]}catch(e){}"); go(g, 'front'); shot(g, f'a06_{tag}_street_papered_over_for_the_work.png')
        log.append(f'{tag} errors: {g.errors[:3]}'); g.close()
        # Day 74 (Lounge III): The Lounge next door; inside, its own street door and the staff's back door
        g = rt.Game(b, port, 'index', seed=8102, manual=True, viewport=vp)
        v.load_save(g, 'player_day74_1508.json')
        v.to_service(g); g.ev("window.__act=window.__actLazy")
        at(g, .1); go(g, 'front'); shot(g, f'a07_{tag}_day74_street_the_lounge.png')
        at(g, .55); go(g, 'front'); shot(g, f'a08_{tag}_day74_street_night.png')
        go(g, 'lounge'); shot(g, f'a09_{tag}_day74_the_lounge_doors.png')
        go(g, 'main'); shot(g, f'a10_{tag}_day74_main_hall_no_arch.png')
        log.append(f'{tag} errors: {g.errors[:3]}'); g.close()
    b.close()
srv.shutdown()
open(OUT + 'log.txt', 'w', encoding='utf-8').write('\n'.join(log) + '\n'); print('\n'.join(log))
