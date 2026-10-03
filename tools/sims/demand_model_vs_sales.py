"""B1: orders vs served on the Day 33 save, lazy player (staff do the work, as the real player), autoStock; also the
model's mean for the same day. Prints per dish: model mean, ordered, served, cancelled/left over."""
import sys, os, json
ROOT='/home/claude/jills-kitchen-project'; sys.path.insert(0, os.path.join(ROOT,'tests'))
import run_tests as T
from run_tests import Game, start_server, install_bot, start_day, LAZY_ACTOR
from playwright.sync_api import sync_playwright
SAVE='/home/claude/jills-kitchen-project/tests/saves/player_day33.json'
raw=json.load(open(SAVE))['save']
HOOK=r"""(()=>{window.__ord={};window.__types={};const C0=createTicket;createTicket=function(g){const n=R.tickets.length;const r=C0(g);if(R.tickets.length>n){const tk=R.tickets[R.tickets.length-1];for(const it of tk.items)__ord[it.d]=(__ord[it.d]||0)+1;__types[g.type]=(__types[g.type]||0)+1}return r};return 1})()"""
with sync_playwright() as p:
    srv, port = start_server(); b = p.chromium.launch()
    g = Game(b, port, 'index', seed=7, manual=True)
    tot={}
    for seed in range(3):
        g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.click('[data-act=openFresh]'); g.page.wait_for_timeout(100)
        install_bot(g); g.ev(LAZY_ACTOR+"\nwindow.__act=window.__actLazy;")
        g.ev("Math.random=(function(){let a=%d;return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()" % (2000+seed))
        model=json.loads(g.ev("JSON.stringify(expectDemand(S.today.groups,1500,true))"))
        g.ev("autoStock()"); start_day(g); g.ev(HOOK)
        for i in range(700):
            r=g.page.evaluate('()=>window.__bot(150,1/30)')
            if g.ev("phase")!='service' or r['ticks']<150: break
        if g.ev("phase")=='service': g.ev("closeShop('x');for(const q of R.groups.slice())leaveGroup(q,'ok')"); g.page.evaluate('()=>window.__bot(400,1/30)')
        if g.ev("phase")=='service': g.ev("finishClosing()")
        s=json.loads(g.ev("JSON.stringify({sales:S.lastSummary.sales,guests:S.lastSummary.guests,lost:S.lastSummary.lost,angry:S.lastSummary.angry||0,ord:window.__ord,types:window.__types})"))
        print('seed',seed,'guests',s['guests'],'lost',s['lost'],'angry',s['angry'],'ordered',sum(s['ord'].values()),'served',sum(x['n'] for x in s['sales']),'types',s['types'],flush=True)
        for d,v in model.items(): tot.setdefault(d,{'model':[], 'ord':[], 'served':[]})['model'].append(round(v,1))
        for d in tot: tot[d]['ord'].append(s['ord'].get(d,0)); tot[d]['served'].append(next((x['n'] for x in s['sales'] if x['d']==d),0))
    print(f"{'dish':12}{'model':>22}{'ordered':>16}{'served':>16}")
    for d,r in sorted(tot.items(), key=lambda kv:-sum(kv[1]['model'])): print(f"{d:12}{str(r['model']):>22}{str(r['ord']):>16}{str(r['served']):>16}")
    g.close(); b.close()
