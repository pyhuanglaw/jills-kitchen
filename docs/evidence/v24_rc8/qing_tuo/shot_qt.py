"""晴 × 阿拓 after work (the player's brief of 2026-10-03): the five held scenes on the player's Day 74 save, a screenshot
of each scene's key lines at 390x844 (headless Chromium: T, not O). Each scene comes on an evening when the day's story
slot is free, as in play.   python3 shot_qt.py ROOT OUT"""
import sys, os
ROOT = sys.argv[1]; OUT = sys.argv[2].rstrip('/') + '/'
sys.path.insert(0, ROOT + '/tests'); os.chdir(ROOT)
import run_tests as rt, v24_tests as v
from playwright.sync_api import sync_playwright
os.makedirs(OUT, exist_ok=True)
srv, port = rt.start_server()
log = []
SHOTS = {'qt_drink': ['Dylan 在吧台坐下', '稀奇', '……行'],
         'qt_late': ['只剩吧台', '直接把那一支遞給她', '錢壓在杯子底下'],
         'qt_often': ['你們下班都會留下來', '最近比較常', '沈晴抬眼', '阿拓替她倒'],
         'qt_ya': ['你喜歡予安', '是沈晴', '……沈晴？', '鋼琴啊', '沈晴？', '很明顯嗎', '五個音', '記住就好'],
         'qt_said': ['妳過來一下', '一隻手，五個音', '那妳要不要', '在什麼', '……好啊', '啪、啪', '先走了', '安靜很多', '難怪。']}


def held(g, key, n0):
    want = list(SHOTS[key]); got = []
    for _ in range(90):
        if not g.ev("!!(typeof DLG!=='undefined'&&DLG&&DLG.sh&&DLG.sh.k===%r)" % key): break
        t = g.ev("(()=>{const n=document.querySelector('#dlg .dlg-name'),t=document.querySelector('#dlg .dlg-text');return(n&&n.textContent?n.textContent+'：':'')+(t?t.textContent:'')})()")
        got.append(t)
        if want and want[0] in t:
            g.ev("__tick(400);try{hud(true)}catch(e){};document.querySelectorAll('#plines>*,#toasts>*,#banner>*').forEach(e=>e.remove())"); g.page.wait_for_timeout(150)
            name = f'{n0}_{key}_{len(SHOTS[key]) - len(want) + 1:02d}.png'; g.page.screenshot(path=OUT + name); print('  shot', name, flush=True); want.pop(0)
        g.ev("__tick(400);dlgNext()"); g.ev("for(let j=0;j<2;j++)__tick(1000/30)")
    log.append(f'{key} ({len(got)} lines): ' + ' / '.join(got))
    return got


with sync_playwright() as p:
    b = p.chromium.launch()
    g = rt.Game(b, port, 'index', seed=9401, manual=True, viewport={'width': 390, 'height': 844})
    v.load_save(g, 'player_day74_1508.json')
    g.ev("kenS().next=null;cnS().next=null")
    v.to_service(g); g.ev("window.__act=window.__actLazy;window.__noScenes=true;R.sched=R.sched.filter(o=>o.reg!=='dylan'&&!(o.regs||[]).includes('dylan'))")
    g.ev("__botUntil('R.t>=R.dur*.3',200000,1/30)")
    g.ev("R.sched.splice(R.si,0,{t:R.t+2,type:'regular',reg:'dylan',size:1,story:1,lounge:1,lgRetry:1,tries:1});window.__noScenes=false;window.__holds=true")
    v._qt_until(g, 'qt_drink'); held(g, 'qt_drink', 'q1')
    v._qt_next_day(g)
    v._qt_evening(g, 'qt_late', "story().facts.qx_dylan=story().facts.qx_dylan||{d:S.day-3,n:2,l:S.day-1};story().facts.qt_drink.d=Math.min(story().facts.qt_drink.d,S.day-5)"); held(g, 'qt_late', 'q2')
    v._qt_next_day(g)
    ya = "story().facts.ya_join=story().facts.ya_join||{d:S.day-15,n:1,l:S.day-15};story().facts.ya_join.d=Math.min(story().facts.ya_join.d,S.day-10);while(!yaNight())story().facts.ya_join.d--"
    v._qt_evening(g, 'qt_often', ya + ";story().facts.qt_late.d=Math.min(story().facts.qt_late.d,S.day-4)"); held(g, 'qt_often', 'q3')
    v._qt_next_day(g)
    v._qt_evening(g, 'qt_ya', ya + ";story().facts.qt_often.d=Math.min(story().facts.qt_often.d,S.day-5);if(!qaHome()){qaS().home={d:S.day,back:S.day+2}}", 2); held(g, 'qt_ya', 'q4')
    v._qt_next_day(g)
    while g.ev("!!qaHome()"): v._qt_next_day(g)
    v._qt_next_day(g)
    v._qt_evening(g, 'qt_said', ya); held(g, 'qt_said', 'q5')
    v._qt_next_day(g)
    g.ev("openStory('qt')"); g.ev("__tick(100)"); g.page.wait_for_timeout(200)
    g.ev("(()=>{const e=[...document.querySelectorAll('#screen *')].find(e=>/今天喝？/.test(e.textContent)&&e.children.length<3);if(e)e.scrollIntoView({block:'center'})})()")
    g.page.screenshot(path=OUT + 'q6_story_page.png'); print('  shot q6_story_page.png')
    log.append('days: ' + g.ev("JSON.stringify(['qt_drink','qt_late','qt_often','qt_ya','qt_said'].map(k=>[k,fact(k)&&fact(k).d]))"))
    log.append(f'page errors: {g.errors[:3]}')
    g.close(); b.close()
srv.shutdown()
open(OUT + 'log.txt', 'w', encoding='utf-8').write('\n'.join(log) + '\n'); print('\n'.join(log))
