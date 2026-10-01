"""v2.3 follow-up (2026-10-01): do the late kitchen works matter in play? The player's Day 52 save, several consecutive
lazy days (the staff work; Jill cooks only what no chef can), the same seed for the same day in every variant:

  base       the save as it is
  walkin     + 走入式冷藏庫 (cold storage 260 -> 400)
  k2         + 廚房二期, the cups only (coffee bar 2 -> 4), nobody hired
  k2h        + 廚房二期 and its two places filled: two LV5 waiters
  all        walkin + k2h

Per day: guests, lost at the door, angry, revenue, net, restock cost, dishes that sold out (and when), drinks served,
how often both coffee cups were busy, drinks waiting, guests queued at the door.

  python3 tools/sims/late_game_days.py [days=3] [variants=base,walkin,k2,k2h,all] [save=tests/saves/player_day52.json]
"""
import sys, os, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, os.path.join(ROOT, 'tests'))
import run_tests as rt
from playwright.sync_api import sync_playwright

DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 3
VARIANTS = (sys.argv[2] if len(sys.argv) > 2 else 'base,walkin,k2,k2h,all').split(',')
SAVE = sys.argv[3] if len(sys.argv) > 3 else os.path.join(ROOT, 'tests/saves/player_day52.json')
raw = json.load(open(SAVE)); raw = raw.get('save', raw)
SEED = "Math.random=(function(){let a=%d;return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
SAMPLE = """JSON.stringify((()=>{const pend={},busy={},cap={};for(const s of R.slots){cap[s.type]=(cap[s.type]||0)+1;if(s.job)busy[s.type]=(busy[s.type]||0)+1}
 for(const tk of R.tickets)for(const it of tk.items)if(it.st==='pending'){const st=DISH(it.d).st;pend[st]=(pend[st]||0)+1}
 return{t:Math.round(R.t),pend,busy,cap,q:R.groups.filter(g=>g.state==='queue').length,z:menuList().filter(d=>stationOk(d)&&(S.stock[d]||0)<=0)}})())"""

def setup(g, v):
    g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.page.wait_for_timeout(150)
    g.click('[data-act=openFresh]') if g.page.query_selector('[data-act=openFresh]') else g.click('[data-act=open]'); g.page.wait_for_timeout(150)
    g.ev("window.__fastSay=1")
    if v in ('walkin', 'all'): g.ev("S.rooms.walkin=1")
    if v in ('k2', 'k2h', 'all'): g.ev("S.rooms.kitchen2=1")
    if v in ('k2h', 'all'):
        g.ev("for(const n of ['阿凱','小芸'])S.crew.push({id:'sim'+n,role:'waiter',name:n,lv:5,duty:'both',since:S.day,days:0,fam:{}})")
    if g.ev("phase") == 'shop': g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(200)

def day(g, d):
    g.ev(SEED % (7000 + d)); g.ev("S.today.sugKey=null;S.today.sug=null")
    m0 = g.ev("S.money"); g.ev("autoStock()"); cost = m0 - g.ev("S.money")
    rt.start_day(g); rt.install_bot(g); g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;")
    samples, zero = [], {}
    for _ in range(900):
        r = g.page.evaluate('()=>window.__bot(150,1/30)')
        if g.ev("phase") != 'service' or not g.ev("!!R"): break
        s = json.loads(g.ev(SAMPLE)); samples.append(s)
        for x in s['z']: zero.setdefault(x, s['t'])
        if r['ticks'] < 150: break
    if g.ev("phase") == 'service': g.ev("closeShop('x');for(const q of R.groups.slice())leaveGroup(q,'ok')"); g.page.evaluate('()=>window.__bot(400,1/30)')
    if g.ev("phase") == 'service': g.ev("finishClosing()")
    sm = json.loads(g.ev("""JSON.stringify({day:S.lastSummary.day,guests:S.lastSummary.guests,lost:S.lastSummary.lost,angry:S.lastSummary.angry,rev:S.lastSummary.rev,net:S.lastSummary.net,wages:S.lastSummary.wages,
      drinks:(S.lastSummary.sales||[]).filter(x=>DISH(x.d)&&DISH(x.d).st==='bar').reduce((a,x)=>a+x.n,0),items:(S.lastSummary.sales||[]).reduce((a,x)=>a+x.n,0),left:(S.lastSummary.sales||[]).reduce((a,x)=>a+(x.left||0),0),money:S.money})"""))
    n = max(1, len(samples))
    bar_full = round(sum(1 for x in samples if x['busy'].get('bar', 0) >= x['cap'].get('bar', 1)) / n, 2)
    bar_wait = round(sum(x['pend'].get('bar', 0) for x in samples) / n, 2)
    queue = round(sum(x['q'] for x in samples) / n, 2)
    sm.update({'restock': cost, 'sold_out': len(zero), 'first_sold_out_t': min(zero.values()) if zero else None, 'bar_full': bar_full, 'drinks_waiting': bar_wait, 'queue': queue, 'cap': g.ev("fridgeCap()"), 'cups': g.ev("barCups(S.eq.bar)")})
    # on to the next day the way the player goes: the summary, the shop, the next day
    if g.page.query_selector('[data-act=toShop]'): g.click('[data-act=toShop]'); g.page.wait_for_timeout(100)
    if g.page.query_selector('#screen [data-act=nextDay]'): g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(150)
    return sm

with sync_playwright() as p:
    srv, port = rt.start_server(); b = p.chromium.launch()
    for v in VARIANTS:
        g = rt.Game(b, port, 'index', seed=7, manual=True, viewport={'width': 390, 'height': 844})
        setup(g, v); rows = []
        for d in range(DAYS):
            rows.append(day(g, d)); print(json.dumps(dict(variant=v, **rows[-1]), ensure_ascii=False), flush=True)
        tot = {k: sum(r[k] for r in rows) for k in ('guests', 'lost', 'angry', 'rev', 'net', 'restock', 'drinks', 'sold_out')}
        tot['bar_full'] = round(sum(r['bar_full'] for r in rows) / len(rows), 2); tot['drinks_waiting'] = round(sum(r['drinks_waiting'] for r in rows) / len(rows), 2)
        print('TOTAL', v, json.dumps(tot, ensure_ascii=False), 'errors', g.errors[:2], flush=True); g.close()
    b.close()
