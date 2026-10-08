"""How often the §45 picture happens on its own: every time a waiter puts dirty dishes into the cart, was the clearing started
on the way back from serving, and how many tables went into that one carry. python3 tools/sims/wayback_count.py WORKTREE SAVE SEED...   (a save that opens straight into its evening: player_day30.json)"""
import sys, os, json
wt, save = sys.argv[1], sys.argv[2]; SEEDS = [int(s) for s in sys.argv[3:]]
sys.path.insert(0, os.path.join(wt, 'tests')); os.chdir(wt)
import run_tests as rt, v24_tests as vt
from playwright.sync_api import sync_playwright
HOOK = r"""window.__wb=[];
{const C0=ddCleanTask;ddCleanTask=function(me,w,t){const r=C0.apply(this,arguments);if(r&&me&&me.role==='waiter'&&w){if(!w.__cl||!w.__cl.length)w.__wbStart=!!(w.task&&w.task.k==='serve');(w.__cl||(w.__cl=[])).includes(t.i)||w.__cl.push(t.i)}return r}}
{const D0=ddDeposit;ddDeposit=function(w){let me=null;for(const m of S.crew||[])if(R.cw&&R.cw[m.id]===w)me=m;
  if(me&&me.role==='waiter'){const n=(w.hands||[]).filter(e=>e.k==='dirty'&&!e.w).length;if(n)__wb.push({id:me.id,lv:me.lv,wb:!!w.__wbStart,tables:(w.__cl||[]).length,n})}
  if(w){w.__cl=[];w.__wbStart=false}return D0.apply(this,arguments)}}"""
srv, port = rt.start_server()
with sync_playwright() as p:
    b = p.chromium.launch()
    for seed in SEEDS:
        g = rt.Game(b, port, 'index', seed=seed, manual=True)
        vt.load_save(g, save)
        if g.ev("phase") != 'service': rt.start_day(g)
        rt.install_bot(g); g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;window.__noScenes=true")
        g.ev(HOOK)
        for _ in range(3000):
            r = g.page.evaluate('()=>window.__bot(150,1/30)')
            if g.ev("phase") != 'service' or not g.ev("!!R"): break
            if r['ticks'] < 150: break
        wb = json.loads(g.ev("JSON.stringify(window.__wb||[])"))
        way = [x for x in wb if x['wb']]
        print(json.dumps({'save': save, 'seed': seed, 'waiter_carries': len(wb), 'on_the_way_back': len(way),
                          'way_back_tables': {k: sum(1 for x in way if x['tables'] == k) for k in (1, 2, 3)},
                          'way_back_dishes_avg': round(sum(x['n'] for x in way) / max(1, len(way)), 2),
                          'by_lv': {lv: sum(1 for x in way if x['lv'] == lv) for lv in (3, 4, 5)}}), flush=True)
        g.close()
    b.close()
srv.shutdown()
