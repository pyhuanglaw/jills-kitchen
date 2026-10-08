"""The user's onboarding question (docs/v24/cooking_onboarding_2026-10-08.txt, 「初始資金增加」): a fresh game's first three days,
the money at each moment that matters — the starting cash, what the day's stocking costs and what is left after it, the
evening's takings and costs, the lowest point. Two players: the one who takes the suggested stock (Jill stocks Days 1–2 by
herself, from Day 3 the player presses the suggestion) and one who stocks generously (one and a half times the suggestion).
  python3 tools/sims/onboarding_cash.py WORKTREE [SEED ...] [--start N]   (--start: try another starting cash)"""
import sys, os, json
args = sys.argv[1:]
START = None
if '--start' in args:
    i = args.index('--start'); START = int(args[i + 1]); del args[i:i + 2]
wt = args[0]; SEEDS = [int(s) for s in args[1:]] or [101, 202, 303]
sys.path.insert(0, os.path.join(wt, 'tests')); os.chdir(wt)
import run_tests as rt
from playwright.sync_api import sync_playwright
MONEY = "JSON.stringify({day:S.day,phase:phase,money:S.money,stock:Object.assign({},S.stock),todayCost:S.todayCost||0,menu:menuList(),sug:suggestStock(),est:restockEstimate()})"
out = []
srv, port = rt.start_server()
with sync_playwright() as p:
    b = p.chromium.launch()
    for seed in SEEDS:
        for who, mult in (('suggested', 1.0), ('generous', 1.5)):
            g = rt.Game(b, port, 'index', seed=seed, manual=True)
            rt.install_bot(g); g.click('[data-act=open]')
            if START is not None: g.ev(f"S.money={START};save()")
            low = None; days = []
            for d in range(3):
                before = json.loads(g.ev(MONEY))
                if d >= 2 or mult != 1.0:   # Days 1–2 Jill stocks by herself at the start of service; the generous player tops it up
                    g.ev(f"(()=>{{const s=suggestStock();for(const k in s){{const need=Math.ceil(s[k]*{mult})-(S.stock[k]||0);if(need>0)buyStock(k,need)}}}})()")
                rt.start_day(g)
                after = json.loads(g.ev(MONEY))
                low = after['money'] if low is None else min(low, after['money'])
                for _ in range(1200):
                    r = g.page.evaluate('()=>window.__bot(150,1/30)')
                    if g.ev("phase") != 'service' or not g.ev("!!R"): break
                    if r['ticks'] < 150: break
                summ = json.loads(g.ev("JSON.stringify(S.lastSummary&&{guests:S.lastSummary.guests,lost:S.lastSummary.lost,rev:S.lastSummary.rev,cost:S.lastSummary.cost,tips:S.lastSummary.tips,bonus:S.lastSummary.bonus,wages:S.lastSummary.wages,net:S.lastSummary.net})"))
                end = g.ev("S.money")
                days.append({'day': d + 1, 'money_before_stock': before['money'], 'stock_cost': before['money'] - after['money'],
                             'money_after_stock': after['money'], 'menu': after['menu'], 'summary': summ, 'money_end': end, 'next_restock_est': after['est']})
                low = min(low, end)
                g.click('[data-act=toShop]'); g.click('[data-act=nextDay]')
            rec = {'seed': seed, 'player': who, 'start': START, 'lowest': low, 'days': days}
            out.append(rec)
            print(json.dumps(rec, ensure_ascii=False), flush=True)
            g.close()
    b.close()
srv.shutdown()
