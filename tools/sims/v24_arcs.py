"""v2.4 rc6 (the player's 12:16, 「阿拓跟晴毫無進展」): a real save played forward day after day by the lazy bot (the staff do
their jobs), the story arbiter running as in play; prints, day by day, every story beat that fired — major, minor and
the long chains' (v24) steps, and the 晴 × 阿拓 ambient ones — with whether 沈晴 and 阿拓 came in, their evenings together
and the state of 「多的。」. One major beat a day at most; a beat that waited takes the next day's slot.

  python3 tools/sims/v24_arcs.py SAVE DAYS SEEDBASE [ROOT]
  e.g. python3 tools/sims/v24_arcs.py tests/saves/player_day71_1215.json 20 7100
"""
import sys, os, json, time
SAVE = sys.argv[1]; DAYS = int(sys.argv[2]); SEEDBASE = int(sys.argv[3])
ROOT = sys.argv[4] if len(sys.argv) > 4 else os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'tests'))
import run_tests as rt
from playwright.sync_api import sync_playwright
raw = json.load(open(SAVE)); raw = raw.get('save', raw)
SEED = "Math.random=(function(){let a=%d;return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
t0 = time.time()
with sync_playwright() as p:
    srv, port = rt.start_server(); b = p.chromium.launch()
    g = rt.Game(b, port, 'index', seed=SEEDBASE, manual=True, viewport={'width': 390, 'height': 844})
    g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.page.wait_for_timeout(150)
    g.click('[data-act=openFresh]') if g.page.query_selector('[data-act=openFresh]') else g.click('[data-act=open]'); g.page.wait_for_timeout(150)
    g.ev("window.__fastSay=1")
    allfired = []
    for d in range(DAYS):
        if g.ev("phase") == 'service':
            g.ev("closeShop('x');for(const q of R.groups.slice())leaveGroup(q,'ok')"); g.page.evaluate('()=>window.__bot(400,1/30)')
            if g.ev("phase") == 'service': g.ev("finishClosing()")
        if g.ev("phase") == 'summary':
            g.click('[data-act=toShop]'); g.page.wait_for_timeout(80)
        if g.ev("phase") == 'shop':
            g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(120)
        g.ev(SEED % (SEEDBASE + d)); g.ev("S.today.sugKey=null;S.today.sug=null;autoStock()")
        rt.start_day(g); rt.install_bot(g); g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;window.__noScenes=true")
        g.ev("window.__fired=[];if(!window.__wrapped){window.__wrapped=1;const T0=storyTrace;storyTrace=function(x){window.__fired&&__fired.push(x.lane+':'+x.k+'@'+x.at);return T0(x)}}")
        for _ in range(1200):
            r = g.page.evaluate('()=>window.__bot(150,1/30)')
            if g.ev("phase") != 'service' or not g.ev("!!R"): break
            if r['ticks'] < 150: break
        if g.ev("phase") == 'service':
            g.ev("closeShop('x');for(const q of R.groups.slice())leaveGroup(q,'ok')"); g.page.evaluate('()=>window.__bot(400,1/30)')
        if g.ev("phase") == 'service': g.ev("finishClosing()")
        info = json.loads(g.ev("""JSON.stringify({day:S.day,fired:(window.__fired||[]).filter(x=>!x.startsWith('ambient:')||/qt_/.test(x)),
          qt:{q:!!(S.crew||[]).find(m=>m.name==='沈晴'&&crewHere(m)),t:!!(S.crew||[]).find(m=>m.name==='阿拓'&&crewHere(m)),days:factN('qt_days'),ev3:story().ev.qt_3||null,owe:story().owe||null}})"""))
        allfired.append(info)
        print(f"Day {info['day']:3d}  晴{'+' if info['qt']['q'] else '-'} 拓{'+' if info['qt']['t'] else '-'} qt_days {info['qt']['days']:2d} qt_3 {json.dumps(info['qt']['ev3'])}  {' '.join(info['fired'])}", flush=True)
    print('page errors:', g.errors[:5])
    g.close(); b.close(); srv.shutdown()
print(f'{DAYS} days in {time.time()-t0:.0f}s')
