"""The user's Day 92 save, Day 93's prep: the swaps the simulated player made (seven cheap dishes off the menu, seven dearer
ones on, by the prep screen's own switches), then 「一鍵補到建議量」: which of tonight's dishes have nothing.
  python3 starve_repro.py OUT.txt   (from the repo root; JK_GAME_JS may name another game.js)"""
import sys, os, json
ROOT = os.getcwd(); sys.path.insert(0, os.path.join(ROOT, 'tests'))
OUT = sys.argv[1]; sys.argv = [sys.argv[0]]
import run_tests as rt
from playwright.sync_api import sync_playwright
OFF = ['檸檬氣泡水', '錫蘭檸檬紅茶', '拿鐵咖啡', '焦糖布丁', '南瓜濃湯', '松露薯條', '巴斯克乳酪蛋糕']
ON = ['番茄義大利麵', '經典牛肉漢堡', '生火腿沙拉', '海鮮義大利麵', '蟹肉蛋炒飯', '布拉塔番茄麵', '松露南瓜濃湯']
lines = []
def note(s): print(s, flush=True); lines.append(s)
srv, port = rt.start_server()
with sync_playwright() as p:
    b = p.chromium.launch()
    g = rt.Game(b, port, 'index', seed=933, manual=True, viewport={'width': 390, 'height': 844})
    raw = json.load(open(os.path.join(ROOT, 'tests', 'saves', 'player_day92_2105.json'), encoding='utf-8')); raw = raw.get('save', raw)
    g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.page.wait_for_timeout(150)
    g.click('[data-act=openFresh]') if g.page.query_selector('[data-act=openFresh]') else g.click('[data-act=open]'); g.page.wait_for_timeout(200)
    if g.ev("phase") == 'shop': g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(200)
    for _ in range(10):
        if g.ev("typeof DLG!=='undefined'&&!!DLG"): g.ev("dlgNext()")
    note(f"Day {g.ev('S.day')} prep; fridge {g.ev('stockTotal()')}/{g.ev('fridgeCap()')}; menu {g.ev('S.menu.length')}")
    for nm in OFF + ON:   # the prep screen's switch for each dish, as the player presses it
        d = g.ev(f"Object.keys(DISHES).concat(Object.values(typeof VARIANTS!=='undefined'?VARIANTS:{{}}).map(v=>v.id)).find(k=>dishName(k)==='{nm}')||null")
        if not d: d = g.ev(f"[...S.unlocked].find(k=>dishName(k)==='{nm}')||null")
        ok = g.ev(f"(()=>{{const b=[...document.querySelectorAll('#screen [data-act=toggle]')].find(x=>x.dataset.d==='{d}');if(!b)return false;b.click();return true}})()")
        g.page.wait_for_timeout(40)
        note(f"  switch {nm} ({d}): {'pressed' if ok else 'NOT FOUND'} -> on the menu: {g.ev(f'S.menu.includes({json.dumps(d)})')}")
    off_left = g.ev("[...S.unlocked].filter(d=>!S.menu.includes(d)&&(S.stock[d]||0)>0).map(d=>dishName(d)+' '+S.stock[d]).join('、')")
    note(f"leftovers of dishes now off the menu: {off_left}")
    sug = g.ev("suggestStock()")
    g.click('[data-act=restock]'); g.page.wait_for_timeout(150)
    rows = g.ev("menuList().map(d=>[dishName(d),S.stock[d]||0])")
    sug_named = g.ev("(()=>{const s=suggestStock();return Object.fromEntries(Object.keys(s).map(d=>[dishName(d),s[d]]))})()")
    empty = [n for n, k in rows if k == 0]
    short = [f"{n} {k}/{sug_named.get(n)}" for n, k in rows if sug_named.get(n) and k < sug_named[n]]
    note(f"after 一鍵補到建議量: fridge {g.ev('stockTotal()')}/{g.ev('fridgeCap()')}; tonight's dishes with nothing: {empty or 'none'}; below their suggestion: {short or 'none'}")
    TOAST = "[...document.querySelectorAll('.toast')].map(t=>t.textContent).filter(t=>/冰箱|錢/.test(t)).join(' | ')"
    note(f"toast: {g.ev(TOAST)}")
    g.click('[data-act=start]'); g.page.wait_for_timeout(150)
    WARN = "(()=>{const e=document.querySelector('.inline-warn');return e?e.textContent:null})()"
    note(f"the opening's warning: {g.ev(WARN)}")
    note(f"page errors: {g.errors[:3]}")
    g.close(); b.close()
srv.shutdown()
open(OUT, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
