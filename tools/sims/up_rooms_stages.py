"""2026-10-04 (the player: 「PDR 的入口」「PDR 現有 Stage 狀態與室內畫面」「Staff Room Stage I / II / III 現有狀態」): the second
floor's two rooms at each of their phases, from a COPY of the player's Day 92 save — bought through the shop's own
buttons where the story allows (the Staff Room's Phase II), the rest opened ahead of the save's story (the Private
Dining Room needs 《關上門以後》 first; Phase III needs days of use) to show what each phase looks like. Nothing is saved.

  python3 tools/sims/up_rooms_stages.py SAVE OUT_DIR
"""
import sys, os, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, os.path.join(ROOT, 'tests'))
import run_tests as rt
from playwright.sync_api import sync_playwright
SAVE, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
notes = []
def note(s): print(s, flush=True); notes.append(s)
raw = json.load(open(SAVE)); raw = raw.get('save', raw)
with sync_playwright() as p:
    srv, port = rt.start_server(); b = p.chromium.launch()
    g = rt.Game(b, port, 'index', seed=9400, manual=True, viewport={'width': 390, 'height': 844})
    g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.page.wait_for_timeout(200)
    g.click('[data-act=open]'); g.page.wait_for_timeout(300); g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}")
    if g.ev("phase") != 'shop': g.ev("showShop()")
    def frames(n=12): g.ev(f"for(let i=0;i<{n};i++)__tick(1000/30)"); g.page.wait_for_timeout(60)
    def clean(): g.ev("document.querySelectorAll('#toasts>*,#plines>*,#banner>*').forEach(e=>e.remove());const c=$('#coach');if(c)c.hidden=true")
    def shot(name, what):
        frames(); clean(); frames(2); g.page.screenshot(path=os.path.join(OUT, name)); note(f'{name}: {what} | ' + g.ev("JSON.stringify({day:S.day,clock:R?clockStr():phase,room,sr:srStage(),pd:pdStage()})"))
    def redraw(): g.ev("IDLE=null;bg=null;for(const kk in BGC)delete BGC[kk];forceDraw=true")
    # the shop: 《關上門以後》 opened ahead of the save's story; the Private Dining Room's Phase I bought by its button (one
    # works upstairs at a time, so the Staff Room's Phase II — its button tested in rc85_the_rooms_upstairs_are_bought_by_their_buttons — is set for the same day)
    g.ev("factSet('pd_story');shopTab='works';showShop()"); g.page.wait_for_timeout(150)
    g.ev("document.querySelector('[data-act=buyPD]').scrollIntoView({block:'center'})"); g.page.wait_for_timeout(100)
    g.page.screenshot(path=os.path.join(OUT, '00_shop_rooms_upstairs.png')); note('00_shop_rooms_upstairs.png: 店舖工程 › 二樓的房間：員工休息室 II 的「訂購」、私人包廂 I 的「動工」（《關上門以後》提前打開）')
    g.click('[data-act=buyPD]'); g.page.wait_for_timeout(200); g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}")
    g.page.wait_for_timeout(300); g.page.screenshot(path=os.path.join(OUT, '00b_pdr_works_card.png')); note('00b_pdr_works_card.png: 按下「動工」以後的卡片')
    g.ev("try{hideReveal()}catch(e){}")
    note('the Private Dining Room Phase I bought by its button: ' + g.ev("JSON.stringify(pdOf())"))
    g.ev("const s=srW();s.b2=S.day;s.st2=S.day+1"); note('the Staff Room Phase II set for tomorrow: ' + g.ev("JSON.stringify(srOf())"))
    # the next day, in the service
    g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}")
    if g.ev("phase") == 'shop': g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(300)
    g.ev("for(let i=0;i<40;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}")
    g.ev("UPV=null;autoStock()"); rt.start_day(g); rt.install_bot(g); g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;window.__noScenes=true")
    g.ev("for(let i=0;i<40;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}"); g.ev("__botUntil('R.t>=R.dur*.1',90000,1/30)")
    tab = lambda k: g.ev(f"document.querySelector('#roomTabs [data-room={k}]').click()")
    tab('up'); shot('01_floor_both_doors.png', '二樓：走廊、員工休息室和包廂的牆與門')
    tab('staff'); shot('02_staff_room_phase2.png', '員工休息室 II（直接打開；它的訂購按鈕另有測試）')
    tab('pdr'); shot('03_pdr_phase1.png', '私人包廂 I')
    g.ev("const s=srW();s.st3=S.day;const p=pdW();p.st2=S.day"); redraw()
    tab('staff'); shot('04_staff_room_phase3.png', '員工休息室 III（提前打開）')
    tab('pdr'); shot('05_pdr_phase2.png', '私人包廂 II（提前打開）')
    g.ev("pdW().st3=S.day"); redraw()
    tab('pdr'); shot('06_pdr_phase3.png', '私人包廂 III（提前打開）')
    g.ev("const s=srW();delete s.st2;delete s.st3"); redraw()
    tab('staff'); shot('07_staff_room_phase1.png', '員工休息室 I（你存檔現在的樣子）')
    note('errors: ' + json.dumps(g.errors[:3]))
    b.close(); srv.shutdown()
open(os.path.join(OUT, 'stages.txt'), 'w', encoding='utf-8').write('\n'.join(notes) + '\n')
