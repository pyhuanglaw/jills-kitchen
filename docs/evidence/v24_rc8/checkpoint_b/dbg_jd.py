"""Stage check: 《有點想接》 and the book, in Jill's room after closing, on the player's Day 52 save (headless: T, not O).
python3 dbg_jd.py ROOT OUT [reveal=0|1]"""
import sys, os, json, base64
ROOT = sys.argv[1]; OUT = sys.argv[2].rstrip('/') + '/'; REVEAL = len(sys.argv) > 3 and sys.argv[3] == '1'
sys.path.insert(0, ROOT + '/tests'); os.chdir(ROOT)
import run_tests as rt, v24_tests as v
from playwright.sync_api import sync_playwright
os.makedirs(OUT, exist_ok=True)
srv, port = rt.start_server()
log = []
def clean(g):
    g.ev("try{hud(true)}catch(e){};document.querySelectorAll('#plines>*,#toasts>*,#banner>*').forEach(e=>e.remove())")
def shot(g, name):
    clean(g); g.page.wait_for_timeout(120); g.page.screenshot(path=OUT + name); print('  shot', name, flush=True)
def crop(g, name, x, y, w, h, k=3):
    clean(g)
    url = g.ev(f"(()=>{{const s=SV.s*DPR;const cv=document.createElement('canvas');cv.width={w}*{k};cv.height={h}*{k};const c=cv.getContext('2d');c.drawImage(sc,(SV.ox+({x})*SV.s)*DPR,(SV.oy+({y})*SV.s)*DPR,{w}*s,{h}*s,0,0,{w}*{k},{h}*{k});return cv.toDataURL('image/png')}})()")
    open(OUT + name, 'wb').write(base64.b64decode(url.split(',')[1])); print('  saved', name, flush=True)
def run_to_closing(g):
    g.ev("__botUntil('R.closing!=null',200000,1/30)")
    g.ev("lifeEnsureEvening()"); g.ev("for(let i=0;i<3;i++)__tick(1000/30)")
def step(g, want, tag):
    got = []
    for i in range(30):
        if not g.ev("!!DLG"): break
        t = g.ev("(document.querySelector('#dlg .dlg-text')||{}).textContent||''"); n = g.ev("(document.querySelector('#dlg .dlg-name')||{}).textContent||''")
        got.append((n + '：' if n else '') + t)
        for w in want:
            if w in t:
                shot(g, f'{tag}_{len([x for x in got if any(w2 in x for w2 in want)])}.png'); crop(g, f'{tag}_{len([x for x in got if any(w2 in x for w2 in want)])}_room.png', 60, 40, 320, 150, 3)
        g.ev("__tick(400);dlgNext()"); g.ev("for(let j=0;j<2;j++)__tick(1000/30)")
    return got
with sync_playwright() as p:
    b = p.chromium.launch()
    for scene in ('jd_want', 'dylan_book'):
        g = rt.Game(b, port, 'index', seed=8301, manual=True, viewport={'width': 390, 'height': 844})
        v.load_save(g, 'player_day52.json')
        setup = "const st=story();st.facts.pairing_wine={d:S.day-9,n:1,l:S.day-9};st.facts.tasting_night={d:S.day-9,n:1,l:S.day-9};st.facts.lin_retiring={d:S.day-2,n:1,l:S.day-2};linS().last=S.day+10;st.facts.ken_where={d:S.day-1,n:1,l:S.day-1};"
        if scene == 'dylan_book': setup += "st.facts.jd_want={d:S.day-2,n:1,l:S.day-2};evState('jd_want').n=1;"
        if REVEAL: setup += "S.dylan.stage=3;S.dylan.reveal=S.day-5;"
        g.ev(setup); g.ev("S.regulars.dylan=S.regulars.dylan||1")
        v.to_service(g); g.ev("window.__noScenes=false;window.__holds=true;window.__act=window.__actLazy")
        g.ev("buildSchedule&&0"); g.ev("R.sched=R.sched.filter(o=>o.reg!=='dylan')")   # Dylan at his desk tonight, not a guest
        run_to_closing(g)
        log.append(f'{scene}: room {g.ev("room")}, held {g.ev("!!(DLG&&DLG.hold)")}, dylan at desk {g.ev("!!homeDylanAtDesk()")}, jill {g.ev("JSON.stringify({on:LIFE.jill.on,pos:LIFE.jill.pos,room:LIFE.jill.room,x:LIFE.jill.x,y:LIFE.jill.y})")}, book {g.ev("linBookOn()")}')
        got = step(g, ['要退休了', '有點想接', '停下來', '那就先看看'] if scene == 'jd_want' else ['很大的書', '這你的', '看看。'], f'{scene}{"_rev" if REVEAL else ""}')
        log.append(f'{scene} lines: ' + ' / '.join(got))
        log.append(f'{scene} errors: {g.errors[:3]}'); g.close()
    b.close()
srv.shutdown()
open(OUT + 'log.txt', 'w', encoding='utf-8').write('\n'.join(log) + '\n'); print('\n'.join(log))
