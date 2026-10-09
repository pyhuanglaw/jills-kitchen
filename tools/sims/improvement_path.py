"""Does a reasonable hire or the matching upgrade relieve the bottleneck? (the user's release gate, 2026-10-09, 四-3:
「合理增加人力或購買對應設備後，應能實際改善目標瓶頸」.) Two places, three seeds each, on the build in JK_GAME_JS:
  early — a new game's Day 4 kitchen with the Bistro's six tables, Jill alone / + the first cook / + a waiter / + a cleaner;
  Day 30 — the user's Day 30 save as it is (one cleaner, no dishwasher) / + a second cleaner / + the dishwasher and 大髒盤車.
One JSON line per evening: guests, lost, net, the wait (mean, 90th percentile), the share served, Jill's busy share, the
cart's blocking seconds.   python3 tools/sims/improvement_path.py TAG [all|day30]
day30: only the Day 30 save, each way out on its own and together (a second cleaner at LV1 or LV3, the dishwasher, 大髒盤車)."""
import sys, os, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'tests')); sys.path.insert(0, os.path.join(ROOT, 'tools', 'sims')); os.chdir(ROOT)
TAG = sys.argv[1]; PART = sys.argv[2] if len(sys.argv) > 2 else 'all'; sys.argv = [sys.argv[0]]
import run_tests as rt
import v24_tests as v
from playwright.sync_api import sync_playwright
HOOK = r"""(()=>{window.__m={waits:[]};if(!window.__mh){window.__mh=1;const S0=seatGroup;seatGroup=function(g,t){const r=S0.apply(this,arguments);if(g&&g.__seat==null)g.__seat=R.t;return r};
  const C0=checkAllServed;checkAllServed=function(g){const was=g&&g.state;const r=C0.apply(this,arguments);if(g&&was==='wait'&&g.state==='eat'&&g.__seat!=null&&!g.__w){g.__w=1;__m.waits.push(R.t-g.__seat)}return r}}
  window.__keep=null;{const E=endDay;endDay=function(){try{if(R&&R.st)window.__keep=JSON.parse(JSON.stringify({wl:R.st.wl||null,dd:R.st.dd||null}))}catch(e){}return E.apply(this,arguments)}}})()"""
CREW = {'cook': "{id:'k1',role:'chef',name:'阿德師傅',lv:1,duty:'stove',since:1,days:1,pool:'restaurant'}",
        'waiter': "{id:'w1',role:'waiter',name:'小茉',lv:1,duty:'both',since:1,days:1,pool:'restaurant'}",
        'cleaner': "{id:'c1',role:'cleaner',name:'阿芳',lv:1,duty:'clean',since:1,days:1,pool:'restaurant'}",
        'cleaner2': "{id:'c2x',role:'cleaner',name:'小彤',lv:1,duty:'clean',since:1,days:1,pool:'restaurant'}",
        'cleaner3': "{id:'c2x',role:'cleaner',name:'小彤',lv:3,duty:'clean',since:1,days:1,pool:'restaurant'}"}
DAY30 = [('as saved', ''), ('+ a cleaner', "S.crew.push(%s)" % CREW['cleaner2']), ('+ dishwasher, 大髒盤車', "S.ops=S.ops||{};S.ops.dish=1;S.ops.cart=1")]
if PART == 'day30':
    DAY30 = [('as saved', ''), ('+ a cleaner (LV1)', "S.crew.push(%s)" % CREW['cleaner2']), ('+ a cleaner (LV3)', "S.crew.push(%s)" % CREW['cleaner3']),
             ('+ dishwasher', "S.ops=S.ops||{};S.ops.dish=1"), ('+ 大髒盤車', "S.ops=S.ops||{};S.ops.cart=1"),
             ('+ dishwasher, 大髒盤車', "S.ops=S.ops||{};S.ops.dish=1;S.ops.cart=1"),
             ('+ dishwasher, 大髒盤車, a cleaner (LV3)', "S.ops=S.ops||{};S.ops.dish=1;S.ops.cart=1;S.crew.push(%s)" % CREW['cleaner3'])]
def run(g):
    g.ev(HOOK)
    for _ in range(4000):
        if g.ev("phase") != 'service' or not g.ev("!!R"): break
        r = g.page.evaluate('()=>window.__bot(60,1/30)')
        if r['ticks'] < 60: break
    m = json.loads(g.ev("JSON.stringify({w:__m.waits,k:window.__keep||{},s:S.lastSummary&&{guests:S.lastSummary.guests,lost:S.lastSummary.lost,net:S.lastSummary.net}})"))
    w = sorted(m['w']); wl = (m['k'].get('wl') or {}).get('jill') or {}; tot = sum(wl.values())
    return dict(**(m['s'] or {}), wait_mean=round(sum(w) / len(w), 1) if w else None, wait_p90=round(w[max(0, int(len(w) * .9) - 1)], 1) if w else None,
                jill_busy=round(1 - wl.get('idle', 0) / tot, 3) if tot else None, cart_block_s=round(((m['k'].get('dd') or {}).get('blockT')) or 0))
srv, port = rt.start_server()
with sync_playwright() as p:
    b = p.chromium.launch()
    for seed in (1, 2, 3):
        for name, crew in (('Jill alone', []), ('+ cook', ['cook']), ('+ cook, waiter', ['cook', 'waiter']), ('+ cook, waiter, cleaner', ['cook', 'waiter', 'cleaner'])) if PART == 'all' else ():
            g = rt.Game(b, port, 'index', seed=700 + seed, manual=True, viewport={'width': 390, 'height': 844})
            rt.install_bot(g); g.click('[data-act=open]'); g.page.wait_for_timeout(80)
            g.ev("S.day=4;S.level=2;S.tables=6;S.money=20000;S.eq.stove=2;S.eq.prep=1;S.eq.bar=1;S.eq.fridge=3;for(const d of ['friedrice','coffee','salad','burger'])if(!S.unlocked.includes(d))S.unlocked.push(d);S.menu=['friedrice','coffee','salad','burger'];S.crew=[%s];window.__noXQH=1;autoStock();save()" % ','.join(CREW[c] for c in crew))
            rt.start_day(g); g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;")
            print(json.dumps({'tag': TAG, 'where': 'early Day 4', 'config': name, 'seed': seed, **run(g), 'errors': g.errors[:1]}, ensure_ascii=False), flush=True); g.close()
        for name, js in DAY30:
            g = rt.Game(b, port, 'index', seed=800 + seed, manual=True, viewport={'width': 390, 'height': 844})
            v.load_save(g, 'player_day30.json'); g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}")
            if js: g.ev(js + ";save()")
            v.to_service(g, lazy=True)
            print(json.dumps({'tag': TAG, 'where': 'Day 30 save', 'config': name, 'seed': seed, **run(g), 'errors': g.errors[:1]}, ensure_ascii=False), flush=True); g.close()
    b.close()
srv.shutdown()
