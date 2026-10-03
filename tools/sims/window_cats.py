"""v2.3 late game (2026-10-01): do the cats use the side room's window line, and does the dining room keep its cats?

The player's Day 52 save, lazy days (the staff work), the same seed per day in every variant:

  t1   the save as it is (the window has the 窗邊貓架 only)
  t5   the whole window line (軟墊窗台, 多層窗邊步道, 窗邊吊床, 多貓觀景平台)

Sampled every second of the evening: how many cats are on window places, which places, how many in the dining room
(visible there), how many anywhere in the side room; hops from one window place to another; album memos the window
asked for (吊床上的午睡, 窗邊的位子 — asked, not taken: a picture is only taken in the room the player is looking at);
and two rules checked at every sample — never more than three cats on window places,
never two cats on places that overlap on screen (winClash).

  python3 tools/sims/window_cats.py [days=2] [variants=t1,t5] [save=tests/saves/player_day52.json]
"""
import sys, os, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, os.path.join(ROOT, 'tests'))
import run_tests as rt
from playwright.sync_api import sync_playwright

DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 2
VARIANTS = (sys.argv[2] if len(sys.argv) > 2 else 't1,t5').split(',')
SAVE = sys.argv[3] if len(sys.argv) > 3 else os.path.join(ROOT, 'tests/saves/player_day52.json')
raw = json.load(open(SAVE)); raw = raw.get('save', raw)
SEED = "Math.random=(function(){let a=%d;return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
SAMPLE = """JSON.stringify((()=>{const win=CATS.filter(c=>c.away==='side'&&c.gear&&((CATGEAR.find(x=>x.k===c.gear)||{}).line==='win'||c.gear==='perch'));
 const occ=Object.keys(GEAR_OCC).filter(k=>GEAR_OCC[k]&&(k==='perch'||(CATGEAR.find(x=>x.k===k)||{}).line==='win'));let clash=0;
 for(const k of occ){const G=CATGEAR.find(x=>x.k===k);if(winClash(G,GEAR_OCC[k]))clash++}
 return{t:Math.round(R.t),win:win.map(c=>c.gear),main:CATS.filter(c=>!c.hidden).length,side:CATS.filter(c=>c.away==='side').length,
  winLine:win.filter(c=>c.gear!=='perch').length,clash,hop:CATS.filter(c=>c.hop).length}})())"""

def setup(g, v):
    g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.page.wait_for_timeout(150)
    g.click('[data-act=openFresh]') if g.page.query_selector('[data-act=openFresh]') else g.click('[data-act=open]'); g.page.wait_for_timeout(150)
    g.ev("window.__fastSay=1")
    if v == 't5': g.ev("for(const T of WIN_TIERS)for(const k of T.keys)S.gear[k]=S.gear[k]||(S.day-3)")
    if g.ev("phase") == 'shop': g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(200)

def day(g, d):
    g.ev(SEED % (9100 + d)); g.ev("S.today.sugKey=null;S.today.sug=null")
    g.ev("autoStock()"); rt.start_day(g); rt.install_bot(g); g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;")
    g.ev("window.__memoCount={}")
    samples, hops, prev = [], 0, {}
    for _ in range(900):
        r = g.page.evaluate('()=>window.__bot(30,1/30)')
        if g.ev("phase") != 'service' or not g.ev("!!R"): break
        s = json.loads(g.ev(SAMPLE)); samples.append(s)
        cur = {}
        for k in s['win']: cur[k] = cur.get(k, 0) + 1
        if r['ticks'] < 30: break
    hops = g.ev("window.__winHops||0")
    if g.ev("phase") == 'service': g.ev("closeShop('x');for(const q of R.groups.slice())leaveGroup(q,'ok')"); g.page.evaluate('()=>window.__bot(400,1/30)')
    if g.ev("phase") == 'service': g.ev("finishClosing()")
    memos = json.loads(g.ev("JSON.stringify(window.__memoCount||{})"))
    n = max(1, len(samples))
    spots = {}
    for s in samples:
        for k in s['win']: spots[k] = spots.get(k, 0) + 1
    out = {'samples': len(samples), 'win_avg': round(sum(len(s['win']) for s in samples) / n, 2),
           'winline_max': max((s['winLine'] for s in samples), default=0), 'clash_samples': sum(1 for s in samples if s['clash']),
           'main_avg': round(sum(s['main'] for s in samples) / n, 2), 'side_avg': round(sum(s['side'] for s in samples) / n, 2),
           'spot_share': {k: round(v / n, 2) for k, v in sorted(spots.items(), key=lambda x: -x[1])},
           'hops': hops, 'memos': memos}
    if g.page.query_selector('[data-act=toShop]'): g.click('[data-act=toShop]'); g.page.wait_for_timeout(100)
    if g.page.query_selector('#screen [data-act=nextDay]'): g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(150)
    return out

with sync_playwright() as p:
    srv, port = rt.start_server(); b = p.chromium.launch()
    for v in VARIANTS:
        g = rt.Game(b, port, 'index', seed=7, manual=True, viewport={'width': 390, 'height': 844})
        setup(g, v)
        # count hops between window places (no new random draws: a wrapper around the existing function)
        g.ev("(()=>{const f=winHop;window.__winHops=0;winHop=function(c,x0,y0,G){if(c.away==='side'&&c.gear&&y0<100)window.__winHops++;return f.apply(this,arguments)}})()")
        g.ev("(()=>{const m=memo;memo=function(id){if(['hammock','windowcats','window','newspot'].includes(id))window.__memoCount[id]=(window.__memoCount[id]||0)+1;return m.apply(this,arguments)}})()")
        for d in range(DAYS):
            g.ev("window.__winHops=0")
            print(json.dumps(dict(variant=v, day=d, **day(g, d)), ensure_ascii=False), flush=True)
        print('errors', v, g.errors[:3], flush=True); g.close()
    b.close()
