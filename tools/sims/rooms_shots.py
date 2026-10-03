"""F: the occupied Day 33 rooms at phone scale (390x844) — main hall and side hall during the rush, plus 打烊後.
Usage: rooms221.py <tag> ; JK_GAME_JS for the v2.2 before."""
import sys, os, json
ROOT='/home/claude/jills-kitchen-project'; sys.path.insert(0, os.path.join(ROOT,'tests'))
from run_tests import Game, start_server, install_bot, start_day, LAZY_ACTOR
from playwright.sync_api import sync_playwright
from PIL import Image
SAVE='/home/claude/jills-kitchen-project/tests/saves/player_day35.json'
raw=json.load(open(SAVE))['save']
tag=sys.argv[1] if len(sys.argv)>1 else 'after'
OUT='/tmp/claude-0/-home-claude/3e92becc-ea59-5b58-92f6-ca1d4bdefb76/scratchpad/rooms221/'; os.makedirs(OUT,exist_ok=True)
with sync_playwright() as p:
    srv, port = start_server(); b = p.chromium.launch()
    g = Game(b, port, 'index', seed=21, manual=True, touch=True, viewport={'width':390,'height':844})
    g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.click('[data-act=openFresh]'); g.page.wait_for_timeout(120)
    install_bot(g); g.ev(LAZY_ACTOR+"\nwindow.__act=window.__actLazy;"); g.ev("autoStock()"); start_day(g)
    g.ev("window.__noScenes=true")
    # play to the rush with the sim, then render a frame
    for i in range(24): g.page.evaluate('()=>window.__bot(150,1/30)')
    g.ev("FLASH=null;document.querySelectorAll('.toast,#toasts>*').forEach(e=>e.remove());setRoom('main');forceDraw=true"); g.page.evaluate('()=>window.__play(3,0)'); g.ev("FLASH=null;MEMQ.length=0;forceDraw=true"); g.page.evaluate('()=>window.__play(1,0)'); g.page.wait_for_timeout(80)
    info=g.ev("JSON.stringify({t:R.t,groups:R.groups.length,seated:R.groups.filter(q=>q.table!=null).length,main:R.tables.filter(t=>(t.room||'main')==='main').length,side:R.tables.filter(t=>t.room==='side').length,front:R.tables.filter(t=>t.room==='front').length,cats:CATS.filter(c=>!c.hidden).length})")
    print(tag, info)
    g.page.screenshot(path=OUT+f'{tag}_main_rush.png')
    g.ev("FLASH=null;document.querySelectorAll('.toast,#toasts>*').forEach(e=>e.remove());setRoom('side');forceDraw=true"); g.page.evaluate('()=>window.__play(3,0)'); g.ev("FLASH=null;MEMQ.length=0;forceDraw=true"); g.page.evaluate('()=>window.__play(1,0)'); g.page.wait_for_timeout(80)
    g.page.screenshot(path=OUT+f'{tag}_side_rush.png')
    # after closing: the empty rooms (the shop's peek), main and side
    g.ev("closeShop('x');for(const q of R.groups.slice())leaveGroup(q,'ok')"); g.page.evaluate('()=>window.__bot(400,1/30)')
    if g.ev("phase")=='service': g.ev("finishClosing()")
    g.page.wait_for_timeout(100); g.ev("document.querySelectorAll('.toast,#toasts>*').forEach(e=>e.remove())")
    print('phase after close', g.ev("phase"))
    if g.ev("document.querySelector('[data-act=peek]')?1:0"): g.click('[data-act=peek]'); g.page.wait_for_timeout(100)
    for rm in ['main','side']:
        g.ev("FLASH=null;MEMQ.length=0;setRoom('%s');forceDraw=true" % rm); g.page.evaluate('()=>window.__play(3,0)'); g.page.wait_for_timeout(80)
        g.page.screenshot(path=OUT+f'{tag}_{rm}_closed.png')
    g.ev("setRoom('main')")
    print('errors', g.errors[:3]); g.close(); b.close()
