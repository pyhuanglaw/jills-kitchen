"""rc8.8 (the player, 2026-10-05: 「Dylan已經揭露但在房間還是沒寫Dylan」): their room on the player's Day 89 save (he is out since
Day 69) — the tab's full name, his name over him at his desk and on the sofa, the hood up — and, for the other side of
the reveal, a fresh game's room (「先生」, the hood up).   python3 tools/sims/dylan_room_shots.py OUT_DIR"""
import sys, os, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, os.path.join(ROOT, 'tests'))
import run_tests as rt
from playwright.sync_api import sync_playwright
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True); notes = []
def note(s): print(s, flush=True); notes.append(s)
raw = json.load(open(os.path.join(ROOT, 'tests/saves/player_day89_0448.json'))); raw = raw.get('save', raw)
with sync_playwright() as p:
    srv, port = rt.start_server(); b = p.chromium.launch()
    def look(g, name, what):
        g.ev("for(let i=0;i<8;i++)__tick(1000/30)"); g.ev("document.querySelectorAll('#toasts>*,#plines>*,#banner>*').forEach(e=>e.remove())"); g.ev("for(let i=0;i<2;i++)__tick(1000/30)")
        g.page.screenshot(path=os.path.join(OUT, name))
        note(f"{name}: {what} | " + g.ev("JSON.stringify({day:S.day,phase,out:dylanOut(),tab:(document.querySelector('#roomTabs .on')||{}).textContent||null,desk:!!homeDylanAtDesk(),sofa:!!(LIFE.dylan&&LIFE.dylan.onSofa)})"))
    g = rt.Game(b, port, 'index', seed=8950, manual=True, viewport={'width': 390, 'height': 844})
    g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.page.wait_for_timeout(300)
    g.click('[data-act=openFresh]') if g.page.query_selector('[data-act=openFresh]') else g.click('[data-act=open]'); g.page.wait_for_timeout(300)
    g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}")
    rt.start_day(g); g.ev("for(let i=0;i<5;i++)__tick(1000/30);setRoom('home')")
    # at his desk early in the evening (before he comes to eat)
    for _ in range(60):
        if g.ev("!!homeDylanAtDesk()"): break
        g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
    look(g, '01_out_desk.png', '揭曉後：書桌前的 Dylan，分頁「Jill 和 Dylan 的房間」')
    # after closing: their evening — him on the sofa if he sits
    g.ev("closeShop('x');for(const q of R.groups.slice())leaveGroup(q,'ok')"); g.page.evaluate('()=>window.__bot&&window.__bot(400,1/30)')
    if g.ev("phase") == 'service': g.ev("finishClosing()")
    g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}")
    g.ev("const pb=document.querySelector('[data-act=peek]');if(pb)pb.click()"); g.page.wait_for_timeout(200)
    g.ev("try{setRoom('home')}catch(e){room='home'}")
    for _ in range(120):   # their evening, as it goes
        if g.ev("!!(LIFE.dylan&&LIFE.dylan.onSofa)") or g.ev("!!homeDylanAtDesk()"): break
        g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
    note('after closing: ' + g.ev("JSON.stringify({phase,room,dy:LIFE.dylan&&{room:LIFE.dylan.room,onSofa:LIFE.dylan.onSofa}})"))
    look(g, '02_out_evening.png', '揭曉後：打烊後他們的房間（「看店裡」）')
    g.close()
    # a fresh game: before the reveal
    g = rt.Game(b, port, 'index', seed=8951, manual=True, viewport={'width': 390, 'height': 844}); rt.install_bot(g); g.click('[data-act=open]'); rt.start_day(g)
    g.ev("for(let i=0;i<5;i++)__tick(1000/30);setRoom('home')")
    for _ in range(80):
        if g.ev("!!homeDylanAtDesk()"): break
        g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
    look(g, '03_before_desk.png', '揭曉前（新遊戲）：書桌前的「先生」，帽子戴著，分頁「Jill 的房間」')
    note('errors: ' + json.dumps(g.errors[:3])); g.close()
    b.close(); srv.shutdown()
open(os.path.join(OUT, 'dylan_room.txt'), 'w', encoding='utf-8').write('\n'.join(notes) + '\n')
