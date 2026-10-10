"""v2.5's phone screenshots of the user's iPhone fixes (2026-10-10), from the user's own Day 6 save (tests/saves/player_day6_1254.json):
the task list open under its chip with its ×; the first cook (阿德師傅, LV1) plating beside the food; his staff card; the kitchen on
a phone held sideways (844×390) with the chips beside the tabs. And Jill at the rack (a Day 1 kitchen, the cooking tests' _day).
python3 docs/evidence/v25_release/screens/shots.py OUTDIR   (from the repo root)"""
import sys, os, json
OUT = sys.argv[1]; ROOT = os.getcwd(); sys.path.insert(0, os.path.join(ROOT, 'tests')); sys.argv = [sys.argv[0]]
os.makedirs(OUT, exist_ok=True)
import run_tests as rt
import cooking_tests as ct
from playwright.sync_api import sync_playwright
raw = json.load(open('tests/saves/player_day6_1254.json', encoding='utf-8')); raw = raw.get('save', raw)
srv, port = rt.start_server()
log = []
def note(s): print(s, flush=True); log.append(s)
def day6(b, w, h, seed=606):
    g = rt.Game(b, port, 'index', seed=seed, manual=True, viewport={'width': w, 'height': h})
    g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.page.wait_for_timeout(150)
    g.click('[data-act=openFresh]') if g.page.query_selector('[data-act=openFresh]') else g.click('[data-act=open]'); g.page.wait_for_timeout(200)
    for _ in range(20):
        if g.ev("typeof DLG!=='undefined'&&!!DLG"): g.ev("dlgNext()")
    return g
def draw(g):
    # the opening banner leaves after 1.7 s (a setTimeout) and the clock follows the frames in the real game; the test page's
    # manual clock keeps the first and freezes the second, so the banner is taken down and the top bar redrawn
    g.ev("(()=>{const b=$('#banner');if(b)b.innerHTML='';try{hud(true)}catch(e){}})()")
    for _ in range(3): g.ev("forceDraw=true;__tick(1000/30)")
    g.page.wait_for_timeout(150)
with sync_playwright() as p:
    b = p.chromium.launch()
    # 1. 今日任務 open in the kitchen (390×844)
    g = day6(b, 390, 844)
    rt.start_day(g); g.ev("__tick(1000/30)"); g.ev("setRoom('kitchen')"); g.page.wait_for_timeout(100)
    for _ in range(200): g.ev("__tick(1000/30)")   # past the opening banner
    c = json.loads(g.ev("JSON.stringify((()=>{const b=$('#taskChip').getBoundingClientRect();return{x:b.left+b.width/2,y:b.top+b.height/2}})())"))
    g.page.mouse.click(c['x'], c['y']); g.page.wait_for_timeout(150); draw(g)
    note(f"01 the task list: open {g.ev('!$(\"#taskPanel\").hidden')}, its × {g.ev('!!$(\"#taskPanel .tpx\")')}, the chip uncovered {g.ev(f'document.elementFromPoint({c[chr(120)]},{c[chr(121)]}).closest(\"#taskChip\")!==null')}")
    g.page.screenshot(path=os.path.join(OUT, '01_390x844_task_list_open.png'))
    g.page.mouse.click(390 * .6, 844 * .62); g.page.wait_for_timeout(150)
    note(f"   a tap in the kitchen puts it away: {g.ev('$(\"#taskPanel\").hidden')}")
    g.close()
    # 2. the first cook plating beside the food (390×844): the evening played until 阿德師傅 is at the pass step of a dish
    g = day6(b, 390, 844)
    rt.start_day(g); rt.install_bot(g); g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;window.__noScenes=true")
    ade = g.ev("(S.crew.find(m=>m.name==='阿德師傅')||{}).id")
    got = None
    for _ in range(900):
        g.page.evaluate('()=>window.__bot(10,1/30)')
        got = g.ev(f"(()=>{{if(R.t<8)return null;const n=(R.wf||[]).find(n=>n.who==='{ade}'&&(wfFlow(n.d)||[])[n.si]==='plate'&&n.st==='work');return n?JSON.stringify({{d:n.d,n:n.n,t:Math.round(R.t)}}):null}})()")
        if got: break
    g.ev("setRoom('kitchen')"); draw(g)
    note(f"02 阿德師傅 (LV{g.ev(f'S.crew.find(m=>m.id===\"{ade}\").lv')}) plating: {got}")
    g.page.screenshot(path=os.path.join(OUT, '02_390x844_first_cook_plates.png'))
    # 3. his staff card (the shop's 員工)
    card = g.ev(f"wfPlacesHTML(S.crew.find(m=>m.id==='{ade}'))+' | '+wfChefDishesHTML(S.crew.find(m=>m.id==='{ade}'))")
    note(f"03 his staff card: {card}")
    g.close()
    g = day6(b, 390, 844)
    g.ev("shopTab='staff';showShop()"); g.page.wait_for_timeout(250)
    el = g.page.query_selector("text=其他步驟都會做")
    if el: el.scroll_into_view_if_needed(); g.page.wait_for_timeout(120)
    note(f"   the staff page shows 其他步驟都會做: {bool(el)}")
    g.page.screenshot(path=os.path.join(OUT, '03_390x844_staff_card.png'))
    g.close()
    # 4. a phone held sideways: the kitchen's chips beside the tabs, off the counters
    g = day6(b, 844, 390)
    rt.start_day(g); g.ev("__tick(1000/30)"); g.ev("setRoom('kitchen')"); g.page.wait_for_timeout(100)
    for _ in range(10): g.ev("__tick(1000/30)")
    draw(g)
    note(f"04 844×390: the chips lifted {g.ev('JSON.stringify(chipsUp)')}")
    g.page.screenshot(path=os.path.join(OUT, '04_844x390_chips_beside_the_tabs.png'))
    g.close()
    # 5. Jill at the rack (Day 1, no cook)
    g = ct._day(b, port, 'index', 7170)
    g.ev("window.__patient=1"); ct._wait_orders(g, 1)
    nid = g.ev("(()=>{wfGather();const n=wfList()[0];wfAssign(n,'jill');return n.id})()")
    ct._until(g, f"wfNode({nid}).st==='ready'", step=3)
    g.ev(f"R.wsel={nid}"); ct._tap_slot(g, f"wfNode({nid}).slot")
    rack = json.loads(g.ev("JSON.stringify(wfRack())"))
    for _ in range(600):
        p0 = json.loads(g.ev("JSON.stringify({x:R.jill.x,y:R.jill.y})"))
        if abs(p0['x'] - rack['x']) < 2 and abs(p0['y'] - rack['y']) < 2: break
        g.ev("__run(1)")
    draw(g)
    note(f"05 Jill at the rack: rack {rack}, Jill {p0}")
    g.page.screenshot(path=os.path.join(OUT, '05_390x844_jill_at_the_rack.png'))
    g.close()
    b.close()
srv.shutdown()
open(os.path.join(OUT, 'shots.txt'), 'w', encoding='utf-8').write('\n'.join(log) + '\n')
