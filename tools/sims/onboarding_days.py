"""The user's Day 1–3 acceptance (docs/v24/cooking_onboarding_2026-10-08.txt, 「Day 1–3 驗收」) on a fresh game, three
evenings each, two players: one who leaves to the staff (秀琴阿姨) what they cover and taps the rest ('lazy', the tests'
LAZY_ACTOR), and one who taps everything she can ('every', the tests' perfect bot). For each evening: what each dish went
through, the guests, the money (before and after stocking, at the end), what the dirty dishes did (in, washed and by whom,
the most at once, time full, tables waiting on a full cart), and the evening's time of 秀琴阿姨 and of Jill on the floor.
  python3 tools/sims/onboarding_days.py WORKTREE [SEED ...] [--js CODE]   → one JSON line per evening
  (--js: a variant, evaluated in the game after each evening starts, e.g. "DD_CAP[0]=999" for a cart that never fills)"""
import sys, os, json
args = sys.argv[1:]
JS = None
if '--js' in args:
    i = args.index('--js'); JS = args[i + 1]; del args[i:i + 2]
wt = args[0]; SEEDS = [int(s) for s in args[1:]] or [101, 202, 303]
sys.path.insert(0, os.path.join(wt, 'tests')); os.chdir(wt)
import run_tests as rt
from playwright.sync_api import sync_playwright
LOOK = """window.__steps={};window.__look=function(){if(!R)return;for(const n of R.wf||[])if(n.f)(__steps[n.d]||(__steps[n.d]=[])).includes(n.f)||__steps[n.d].push(n.f)}"""
END = """JSON.stringify({t:+R.t.toFixed(0),dd:R.st.dd||null,wl:R.st.wl||null})"""
SUMM = """JSON.stringify(S.lastSummary&&{guests:S.lastSummary.guests,lost:S.lastSummary.lost,rev:S.lastSummary.rev,cost:S.lastSummary.cost,wages:S.lastSummary.wages,net:S.lastSummary.net})"""
r1 = lambda v: round(v, 1) if isinstance(v, (int, float)) else v
srv, port = rt.start_server()
with sync_playwright() as p:
    b = p.chromium.launch()
    for seed in SEEDS:
        for who in ('lazy', 'every'):
            g = rt.Game(b, port, 'index', seed=seed, manual=True, viewport={'width': 390, 'height': 844})
            rt.install_bot(g); g.click('[data-act=open]')
            for day in (1, 2, 3):
                if day == 3:
                    g.ev("autoStock()")   # from Day 3 the player presses the suggested stocking
                m0 = g.ev("S.money")
                rt.start_day(g)
                m1 = g.ev("S.money")
                if JS: g.ev(JS)
                if who == 'lazy':
                    g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;")
                g.ev(LOOK)
                end = None
                for _ in range(2000):
                    r = g.page.evaluate('()=>{const r=window.__bot(30,1/30);window.__look();return r}')
                    if g.ev("phase") != 'service' or not g.ev("!!R"): break
                    end = g.ev(END)
                    if r['ticks'] < 30: break
                e = json.loads(end) if end else {}
                dd = e.get('dd') or {}; wl = e.get('wl') or {}
                rec = {'seed': seed, 'player': who, 'day': day, 'variant': JS, 'menu_steps': json.loads(g.ev("JSON.stringify(__steps)")),
                       'money_before_stock': m0, 'money_after_stock': m1, 'summary': json.loads(g.ev(SUMM)), 'money_end': g.ev("S.money"),
                       'dd': {k: (r1(v) if not isinstance(v, dict) else {kk: r1(vv) for kk, vv in v.items()}) for k, v in dd.items() if k in ('in', 'wash', 'by', 'peak', 'full', 'fulls', 'blockT', 'washT')},
                       'xq': {k: r1(v) for k, v in (wl.get('xq') or {}).items()}, 'jill_floor': {k: r1(v) for k, v in (wl.get('jill') or {}).items()},
                       'evening_s': e.get('t')}
                print(json.dumps(rec, ensure_ascii=False), flush=True)
                if g.ev("phase") == 'summary': g.click('[data-act=toShop]')
                if day < 3: g.click('[data-act=nextDay]')
            g.close()
    b.close()
srv.shutdown()
