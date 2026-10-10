"""v2.5.1's phone screenshots (390×844), from the user's own Day 6 save (tests/saves/player_day6_1254.json: level 1, 阿德師傅 on the
burners, a waiter, coffee and salad on the menu — the evening the old prep screen warned 「咖啡吧目前無人」「冷盤台目前無人」):
the prep screen without the warning; the staff board's header; the Bistro card in 店舖工程 with 廚師 +1、服務生 +1; the staff page
after the Bistro (廚師 1/2、服務生 1/2, the hiring buttons, the day's wages).
python3 docs/evidence/v251_release/screens/shots.py OUTDIR   (from the repo root)"""
import sys, os, json
OUT = sys.argv[1]; ROOT = os.getcwd(); sys.path.insert(0, os.path.join(ROOT, 'tests')); sys.argv = [sys.argv[0]]
os.makedirs(OUT, exist_ok=True)
import run_tests as rt
from playwright.sync_api import sync_playwright
raw = json.load(open('tests/saves/player_day6_1254.json', encoding='utf-8')); raw = raw.get('save', raw)
srv, port = rt.start_server()
log = []
def note(s): print(s, flush=True); log.append(s)
def day6(b, w=390, h=844, seed=606):
    g = rt.Game(b, port, 'index', seed=seed, manual=True, viewport={'width': w, 'height': h})
    g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.page.wait_for_timeout(150)
    g.click('[data-act=openFresh]') if g.page.query_selector('[data-act=openFresh]') else g.click('[data-act=open]'); g.page.wait_for_timeout(200)
    for _ in range(20):
        if g.ev("typeof DLG!=='undefined'&&!!DLG"): g.ev("dlgNext()")
    return g
with sync_playwright() as p:
    b = p.chromium.launch()
    # 1. the prep screen: no 「目前無人」, no 安排員工
    g = day6(b)
    g.ev("showPrep()"); g.page.wait_for_timeout(250)
    t = g.ev("$('#screen').innerText")
    need = g.ev("JSON.stringify([...new Set(menuList().map(d=>DISH(d).st))].map(st=>[st,chefsAt(st).length]))")
    note(f"01 prep: stations tonight and their cooks {need}; '目前無人' in the text {'目前無人' in t}, '安排員工' {'安排員工' in t}, a .stwarn {g.ev('!!$(\".stwarn\")')}")
    g.page.screenshot(path=os.path.join(OUT, '01_390x844_prep_no_station_warning.png'))
    g.close()
    # 2. the staff board: its header, no red rows
    g = day6(b)
    g.ev("shopTab='staff';showShop()"); g.page.wait_for_timeout(250)
    el = g.page.query_selector('.board'); el and el.scroll_into_view_if_needed(); g.page.wait_for_timeout(120)
    note(f"02 board: header {g.ev('$(\".board .bd-h\").innerText')!r}; rows marked none {g.ev('document.querySelectorAll(\".brow.none\").length')}")
    g.page.screenshot(path=os.path.join(OUT, '02_390x844_staff_board.png'))
    g.close()
    # 3. the Bistro card (店舖工程)
    g = day6(b)
    g.ev("shopTab='works';showShop()"); g.page.wait_for_timeout(250)
    card = g.page.query_selector("text=擴建：Jill's Bistro")
    if card: card.scroll_into_view_if_needed(); g.page.wait_for_timeout(120)
    txt = g.ev("(()=>{const e=[...document.querySelectorAll('#screen .nm')].find(x=>x.textContent.includes('擴建'));return e?e.parentElement.innerText:null})()")
    note(f"03 the Bistro card: {txt!r}")
    g.page.screenshot(path=os.path.join(OUT, '03_390x844_bistro_card.png'))
    # 4. after the Bistro: the staff page
    g.ev("S.money+=20000;S.level=2;save()"); g.ev("shopTab='staff';showShop()"); g.page.wait_for_timeout(250)
    el = g.page.query_selector("text=廚師、服務生、清潔員各算各的名額")
    if el: el.scroll_into_view_if_needed(); g.page.wait_for_timeout(120)
    caps = g.ev("CAP_ROLES.map(r=>`${ROLES[r].n} ${roleCrew(r).length}/${roleCap(r)}`).join('、')")
    hire = g.ev("JSON.stringify([...document.querySelectorAll('#screen [data-act=hire]')].map(x=>x.dataset.k+':'+x.innerText.replace(/\\s+/g,' ')))")
    note(f"04 Bistro staff: {caps}; hire buttons {hire}; wages a day {g.ev('fmt(crewWages())')}; hire fees chef {g.ev('fmt(hireFee(\"chef\"))')} waiter {g.ev('fmt(hireFee(\"waiter\"))')}")
    g.page.screenshot(path=os.path.join(OUT, '04_390x844_bistro_staff.png'))
    g.close()
    b.close()
srv.shutdown()
open(os.path.join(OUT, 'shots.txt'), 'w', encoding='utf-8').write('\n'.join(log) + '\n')
