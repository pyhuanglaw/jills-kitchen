"""The release check on the published page (docs/RELEASE_CHECKLIST.md §6, after the publish).

The page as the artifact service holds it (Artifact read → the saved HTML) is compared with a page built from the tag,
then played at phone size (390×844, touch) with a real save, the way a player would: the title, OPEN, the prep screen,
restock, a day into the evening with the lazy bot (the rooms photographed through their tabs), the summary, the staff
page, the next day, and a reload of the page. T evidence: a Chromium touch viewport on this machine, not a phone, and
not the claude.ai frame the player opens it in.

  python3 tools/sims/live_check.py LIVE.html TAG SAVE.json OUT_DIR
"""
import sys, os, re, json, hashlib, subprocess, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, os.path.join(ROOT, 'tests'))
import run_tests as rt
from playwright.sync_api import sync_playwright

LIVE, TAG, SAVE, OUT = sys.argv[1:5]
os.makedirs(OUT, exist_ok=True)
notes = []

def note(s):
    print(s, flush=True); notes.append(s)

# ---- 1. the page built from the tag sits in the live HTML byte for byte; the host adds only its document skeleton ----
live = open(LIVE, encoding='utf-8').read()
with tempfile.TemporaryDirectory() as d:
    tar = subprocess.run(['git', 'archive', '--format=tar', TAG], cwd=ROOT, capture_output=True, check=True).stdout
    subprocess.run(['tar', '-x', '-C', d], input=tar, check=True)
    subprocess.run([sys.executable, os.path.join(d, 'tools', 'build_artifact.py'), os.path.join(d, 'page.html')], check=True, capture_output=True)
    built = open(os.path.join(d, 'page.html'), encoding='utf-8').read()
    game = open(os.path.join(d, 'js', 'game.js'), encoding='utf-8').read()
at = live.find(built)
assert at >= 0, f'the live page does not carry the page built from {TAG}'
assert live.count(game) == 1, f'the js/game.js of {TAG} is not in the live page exactly once'
host = live[:at] + live[at + len(built):]
note(f'{TAG}: the page built from the tag ({len(built.encode())} bytes, sha256 {hashlib.sha256(built.encode()).hexdigest()[:12]}) '
     f'is inside the live HTML ({len(live.encode())} bytes) byte for byte, js/game.js once; the host adds {len(host.encode())} bytes (its document skeleton)')
KEY = re.search(r"const KEY='([^']+)'", game).group(1)

# ---- 2. played at phone size with the save ----
raw = json.load(open(SAVE)); save = raw.get('save', raw)

class Live(rt.Game):
    """rt.Game, but the page is the live HTML (served on a local origin so the save has somewhere to live)"""
    def __init__(self, browser, port, html, seed, storage):
        self.ctx = browser.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        self.page = self.ctx.new_page(); self.errors = []
        self.page.on('pageerror', lambda e: self.errors.append(str(e)))
        self.page.on('console', lambda m: self.errors.append('console.error: ' + m.text) if m.type == 'error' and 'fonts.g' not in m.text and 'ERR_' not in m.text else None)
        self.page.route('**/live.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=rt.inject(html)))
        self.page.route('https://fonts.googleapis.com/**', lambda r: r.abort())
        self.page.route('https://fonts.gstatic.com/**', lambda r: r.abort())
        self.page.add_init_script(rt.init_script(seed, True, False))
        self.page.add_init_script("(function(){if(!sessionStorage.getItem('__seeded')){localStorage.clear();const d=%s;for(const k in d)localStorage.setItem(k,d[k]);sessionStorage.setItem('__seeded','1')}})();" % json.dumps(storage))
        self.url = f'http://127.0.0.1:{port}/live.html'
        self.page.goto(self.url); self.page.wait_for_function('typeof window.__jk==="function"')

def shot(g, name, what):
    g.ev("forceDraw=true"); g.ev("__tick(1000/30)"); g.page.wait_for_timeout(60)
    g.page.screenshot(path=os.path.join(OUT, name))
    note(f'{name}: {what} | ' + g.ev("JSON.stringify({phase,day:S.day,t:R?Math.round(R.t/R.dur*100)+'%':null,room})"))

def inv(g, where):
    bad = g.ev(rt.INV)
    assert not bad, f'state invariant broken at {where}: {bad}'

def lines(g):
    """__botUntil steps the game without the clock, so lines queued meanwhile (setTimeout) would all come out at the next
    frame: let them come and go before a photograph (one clamped frame), as v24_up_shots does"""
    g.ev("__tick(9000)"); g.ev("document.querySelectorAll('#toasts>*,#plines>*').forEach(e=>e.remove())")

def until(g, cond):
    for _ in range(200):
        if g.ev(f"phase!=='service'||!R||!!({cond})"): break
        g.ev("for(let i=0;i<80&&typeof DLG!=='undefined'&&DLG;i++){__tick(400);dlgNext()}")   # a line on screen: the player taps on
        g.ev(f"__botUntil({json.dumps(cond)},1500,1/30)")
    lines(g)

def room(g, k):
    g.tap(f'#roomTabs [data-room={k}]'); g.ev("for(let i=0;i<20;i++)__tick(1000/30)")

def text(g, sel='#screen'):
    return g.ev(f"(()=>{{const e=document.querySelector('{sel}');return e?e.innerText:''}})()")

with sync_playwright() as p:
    srv, port = rt.start_server(); b = p.chromium.launch()
    g = Live(b, port, live, 6101, {KEY: json.dumps(save, ensure_ascii=False)})
    day0 = save.get('day')
    t = text(g); assert f'DAY {day0}' in t, t[:200]
    cp = save.get('checkpoint')
    resumes = bool(cp and cp.get('day') == day0)   # a save made during the evening: the title offers 繼續營業 · the clock, and OPEN resumes it
    if resumes:
        assert '繼續營業' in t, t[:200]
        shot(g, '01_title.png', f'the title with the save: DAY {day0}, 繼續營業 · {cp.get("clock")} (the save was made during the evening)')
        g.tap('[data-act=open]'); g.page.wait_for_timeout(200)
        assert g.ev("phase") == 'service', g.ev("phase"); inv(g, 'resumed service')
        shot(g, '02_resumed.png', f'繼續營業: the evening resumed where the save stopped ({cp.get("clock")})')
        rt.install_bot(g); g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy")
    else:
        shot(g, '01_title.png', f'the title with the save: DAY {day0}')
        g.tap('[data-act=open]'); g.page.wait_for_timeout(200)
        if g.ev("phase") == 'shop':   # rc8.5: a save made after closing opens on 升級餐廳 — the next day from there, as a player would
            shot(g, '01b_shop.png', 'OPEN: the save was made after closing — 升級餐廳')
            g.tap('#screen [data-act=nextDay]'); g.page.wait_for_timeout(300)
            g.ev("for(let i=0;i<40&&typeof DLG!=='undefined'&&DLG;i++)dlgNext()")
        assert g.ev("phase") == 'prep', g.ev("phase"); inv(g, 'prep')
        day0 = g.ev("S.day")   # the day played (the one after the save's, when it was saved after closing)
        shot(g, '02_prep.png', 'OPEN: the prep screen')
        if g.page.query_selector('[data-act=restock]:not([disabled])'): g.tap('[data-act=restock]'); g.page.wait_for_timeout(120)   # disabled = 已足夠
        rt.start_day(g); rt.install_bot(g); g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy")
    inv(g, 'service')
    walk = [(.30, 'main', 'the dining room' + ('' if resumes else ', early evening')), (.42, 'side', 'the side room (the stair door at the near edge)'),
            (.55, 'front', 'the street'), (.66, 'lounge', 'the Lounge'), (.74, 'kitchen', 'the kitchen'), (.80, 'home', 'Jill\'s room (rc7.3)')]
    for i, (frac, k, what) in enumerate(walk):
        until(g, f'R.t>=R.dur*{frac}')
        if g.ev("phase") != 'service': break
        if g.page.query_selector(f'#roomTabs [data-room={k}]'): room(g, k)
        shot(g, f'0{3 + i}_{k}.png' if i < 5 else f'07b_{k}.png', what)   # (07b: the numbers after it stay what they were)
    for _ in range(1500):
        if g.ev("phase") != 'service': break
        g.ev("for(let i=0;i<80&&typeof DLG!=='undefined'&&DLG;i++){__tick(400);dlgNext()}")
        g.page.evaluate('()=>window.__bot(150,1/30)')
    assert g.ev("phase") == 'summary', g.ev("phase"); inv(g, 'summary')
    g.ev("document.querySelectorAll('#toasts>*').forEach(e=>e.remove())")
    shot(g, '08_summary.png', 'the day\'s summary')
    st = g.ev("(()=>{const e=document.querySelector('#screen .stoday');return e?[...e.querySelectorAll('.st-row')].map(r=>r.innerText.replace(/\\s+/g,' ')).join(' / '):''})()")
    note('the summary\'s 今天的故事: ' + (st or '(none today)'))
    g.tap('[data-act=toShop]'); g.page.wait_for_timeout(150)
    g.tap('[data-act=tab][data-k=staff]'); g.page.wait_for_timeout(150)
    # the Lounge's list is on the page once the Lounge is built or has its people (showShop: loungeLv()||lc.length) — a save from
    # before the Lounge (the user's Day 6 save, 2026-10-10) has the restaurant's list only
    lounge = g.ev("loungeLv()>0||(S.crew||[]).some(m=>crewPool(m)==='lounge')")
    t = text(g); assert '餐廳員工' in t and ('Lounge 員工' in t or not lounge), t[:300]
    note('the staff page: ' + re.search(r'餐廳員工[^\n]*', t).group(0))
    shot(g, '09_staff.png', 'the shop, the staff page: two numbers' if lounge else 'the shop, the staff page (no Lounge yet: the restaurant\'s list only)')
    g.tap('#screen [data-act=nextDay]'); g.page.wait_for_timeout(250)
    g.ev("for(let i=0;i<80&&typeof DLG!=='undefined'&&DLG;i++){__tick(400);dlgNext()}")
    assert g.ev("phase") == 'prep' and g.ev("S.day") == day0 + 1; inv(g, 'next prep')
    shot(g, '10_prep_next_day.png', f'the next day\'s prep (Day {day0 + 1})')
    m1 = None
    if resumes and g.page.query_selector('[data-act=restock]:not([disabled])'):   # the restock the prep path above taps, here on the next day
        m0 = g.ev("S.money"); g.tap('[data-act=restock]'); g.page.wait_for_timeout(120); inv(g, 'restock'); m1 = g.ev("S.money")
        note(f'restock on Day {day0 + 1}: ${m0:,} → ${m1:,}')
    g.reload(); g.page.wait_for_timeout(200)
    if m1 is not None:   # the purchase was saved by the game itself (nothing here saves)
        assert g.ev("S.money") == m1, (g.ev("S.money"), m1); note(f'after the reload the money is still ${m1:,}: the restock was saved')
    t = text(g); assert f'DAY {day0 + 1}' in t, t[:200]
    shot(g, '11_after_reload.png', f'the page reloaded: the title keeps DAY {day0 + 1}')
    assert not g.errors, g.errors
    note(f'page errors: none ({len(g.errors)})')
    g.close(); b.close(); srv.shutdown()

open(os.path.join(OUT, 'live_check.txt'), 'w', encoding='utf-8').write('\n'.join(notes) + '\n')
print('ok')
