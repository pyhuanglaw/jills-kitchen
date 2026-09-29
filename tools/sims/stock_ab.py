"""B1 before/after: the Day 33 save, restock to the suggestion, a lazy day (staff work); per seed: suggested total and
cost, dishes that hit 0 before closing (and when), guests who left because their dish was gone, leftover at closing.
Run with JK_GAME_JS=<v2.2 game.js> for the before."""
import sys, os, json
ROOT='/home/claude/jills-kitchen-project'; sys.path.insert(0, os.path.join(ROOT,'tests'))
from run_tests import Game, start_server, install_bot, start_day, LAZY_ACTOR
from playwright.sync_api import sync_playwright
SAVE='/home/claude/jills-kitchen-project/tests/saves/player_day33.json'
raw=json.load(open(SAVE))['save']
label=sys.argv[1] if len(sys.argv)>1 else 'after'
with sync_playwright() as p:
    srv, port = start_server(); b = p.chromium.launch()
    g = Game(b, port, 'index', seed=7, manual=True)
    for seed in range(int(sys.argv[2]) if len(sys.argv)>2 else 3):
        g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.click('[data-act=openFresh]'); g.page.wait_for_timeout(100)
        install_bot(g); g.ev(LAZY_ACTOR+"\nwindow.__act=window.__actLazy;")
        g.ev("Math.random=(function(){let a=%d;return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()" % (3000+seed))
        sug=json.loads(g.ev("S.today.sugKey=null;S.today.sug=null;JSON.stringify(suggestStock())")); m0=g.ev("S.money"); g.ev("autoStock()"); cost=m0-g.ev("S.money")
        start_day(g); out={}
        for i in range(700):
            r=g.page.evaluate('()=>window.__bot(150,1/30)')
            st=json.loads(g.ev("JSON.stringify({t:R?R.t:0,z:menuList().filter(d=>stationOk(d)&&(S.stock[d]||0)<=0)})"))
            for d in st['z']:
                if d not in out: out[d]=round(st['t'])
            if g.ev("phase")!='service' or r['ticks']<150: break
        if g.ev("phase")=='service': g.ev("closeShop('x');for(const q of R.groups.slice())leaveGroup(q,'ok')"); g.page.evaluate('()=>window.__bot(400,1/30)')
        if g.ev("phase")=='service': g.ev("finishClosing()")
        s=json.loads(g.ev("JSON.stringify({guests:S.lastSummary.guests,lost:S.lastSummary.lost,items:S.lastSummary.sales.reduce((a,x)=>a+x.n,0),left:S.lastSummary.sales.reduce((a,x)=>a+x.left,0),soldOutLeft:S.lastSummary.soldOutLeft||0,net:S.lastSummary.net})"))
        print(json.dumps({'label':label,'seed':seed,'sug_total':sum(sug.values()),'sug_cost':cost,'guests':s['guests'],'items':s['items'],'sold_out':out,'n_sold_out':len(out),'left_at_close':s['left'],'left_for_soldout':s['soldOutLeft'],'net':s['net']},ensure_ascii=False),flush=True)
    g.close(); b.close()
