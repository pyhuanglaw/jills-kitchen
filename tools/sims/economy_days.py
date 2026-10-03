"""The money, day by day (the player, 2026-10-02 14:39: 「阿lounge不用進貨成本?」「你租金要計算一下吧 但不要讓剛開始太
容易倒店 員工薪水可以再增加一點」). Plays days with the lazy bot (the crew work; Jill does what nobody else can) and
prints each day's summary: takings, tips, food cost, the Lounge's glasses and their cost, wages, rent, the bonus, the
net and the money after it — plus the level, the crew and the rooms, so the costs can be read against the restaurant's
size.

  python3 tools/sims/economy_days.py fresh DAYS SEED [plan]       # a new game; plan: grow (default) or none
  python3 tools/sims/economy_days.py SAVE.json DAYS SEED          # a save, as it is (nothing bought)
  BOT=perfect python3 tools/sims/economy_days.py …                # the perfect bot instead of the lazy one

The fresh game restocks every morning with the prep screen's own button (paid for), and buys the way a growing
restaurant would once it can (the next expansion, the side room, the kitchen, staff, tables) — each a no-op when
the till cannot pay.
"""
import sys, os, json, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, os.path.join(ROOT, 'tests'))
import run_tests as rt
from playwright.sync_api import sync_playwright

SRC, DAYS, SEED = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
PLAN = sys.argv[4] if len(sys.argv) > 4 else 'grow'
RNG = "Math.random=(function(){let a=%d;return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
EARLY = {1: [('rd', {'d': 'pasta'}), ('buyTable', {})], 2: [('buyEq', {'k': 'bar'}), ('buyTable', {})], 3: [('hire', {'k': 'chef'})],   # rc8 §21: the first place is a chef's,
         5: [('expand', {}), ('buyDecor', {'k': 'plants'})], 8: [('hire', {'k': 'waiter'}), ('buyTable', {})], 11: [('expand', {})]}   # the Bistro's a waiter's
GROW = [('expand', {}), ('buyProject', {'k': 'side'}), ('buyProject', {'k': 'kext'}), ('buyOps', {'k': 'room'}), ('hire', {'k': 'waiter'}),
        ('hire', {'k': 'chef'}), ('hire', {'k': 'cleaner'}), ('buyTable', {}), ('buySideTable', {})]
INFO = """JSON.stringify((()=>{const s=S.lastSummary||{};return{day:S.day,money:S.money,lv:S.level,crew:(S.crew||[]).length,
 side:!!(S.rooms&&S.rooms.side),lounge:(S.rooms&&S.rooms.lounge)||0,up:!!(S.rooms&&S.rooms.up),
 rev:s.rev,tips:s.tips,cost:s.cost,wine:s.wine||0,wages:s.wages,rent:s.rent||0,cfee:s.cfee||0,bonus:s.bonus,net:s.net,guests:s.guests,
 lg:s.lg?s.lg.rev:0,owed:(S.wageOwed||0)+(S.rentOwed||0)}})())"""


def main():
    t0 = time.time()
    with sync_playwright() as p:
        srv, port = rt.start_server(); b = p.chromium.launch()
        if SRC == 'fresh':
            g = rt.Game(b, port, 'index', seed=SEED, manual=True, viewport={'width': 390, 'height': 844})
        else:
            raw = json.load(open(SRC)); save = raw.get('save', raw); save['checkpoint'] = None
            KEY = __import__('re').search(r"const KEY='([^']+)'", open(os.path.join(ROOT, 'js', 'game.js'), encoding='utf-8').read()).group(1)
            g = rt.Game(b, port, 'index', seed=SEED, manual=True, viewport={'width': 390, 'height': 844}, storage={KEY: json.dumps(save, ensure_ascii=False)})
        rt.install_bot(g)
        if os.environ.get('BOT', 'lazy') == 'lazy': g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy")   # BOT=perfect: the perfect bot (an engaged player)

        def act(a, **kv):
            ds = ''.join(f"el.dataset.{k}='{v}';" for k, v in kv.items())
            g.ev(f"(()=>{{const el=document.createElement('button');el.dataset.act='{a}';{ds}$('#screen').appendChild(el);el.click();el.remove()}})()")
        g.click('[data-act=open]'); g.ev("window.__fastSay=1"); g.ev("__tick(200)")
        if g.ev("phase") == 'service':   # a save made during the evening: play it out first
            g.ev("__bot(60000,1/30)")
        tot = {}
        print(f"{'day':>4} {'lv':>2} {'crew':>4} {'rooms':<7} {'guests':>6} {'takings':>8} {'tips':>7} {'food':>7} {'wine':>6} {'wages':>7} {'rent':>6} {'bonus':>6} {'net':>8} {'money':>9} {'lounge':>7}")
        for _ in range(DAYS):
            if g.ev("phase") == 'summary': g.click('[data-act=toShop]'); g.ev("__tick(50)")
            if g.ev("phase") == 'shop': g.click('[data-act=nextDay]'); g.ev("__tick(100)")
            for i in range(80):
                if not g.ev("typeof DLG!=='undefined'&&!!DLG"): break
                g.ev("__tick(400);dlgNext()")
            act('restock'); g.ev("__tick(200)")
            g.ev(RNG % (SEED * 1000 + g.ev("S.day")))
            rt.start_day(g)
            for _ in range(600):
                r = g.page.evaluate('()=>window.__bot(150,1/30)')
                g.ev("for(let i=0;i<80&&typeof DLG!=='undefined'&&DLG;i++){__tick(400);dlgNext()}")
                if g.ev("phase") != 'service' or r['ticks'] < 150: break
            if g.ev("phase") == 'service': g.ev("__bot(60000,1/30)")
            g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
            x = json.loads(g.ev(INFO))
            rooms = ('S' if x['side'] else '-') + (f"L{x['lounge']}" if x['lounge'] else '--') + ('U' if x['up'] else '-')
            print(f"{x['day']:>4} {x['lv']:>2} {x['crew']:>4} {rooms:<7} {x['guests'] or 0:>6} {x['rev'] or 0:>8} {x['tips'] or 0:>7} {x['cost'] or 0:>7} {x['wine']:>6} {x['wages'] or 0:>7} {x['rent']:>6} {x['bonus'] or 0:>6} {x['net'] or 0:>8} {x['money']:>9} {x['lg']:>7}"
                  + (f"  owed {x['owed']}" if x['owed'] else ''), flush=True)
            if SRC == 'fresh' and PLAN == 'grow':
                if g.ev("phase") == 'summary': g.click('[data-act=toShop]'); g.ev("__tick(50)")
                for a, kv in EARLY.get(x['day'], []):
                    act(a, **kv); g.ev("__tick(30)")
                if x['day'] >= 15:
                    for a, kv in GROW:
                        act(a, **kv); g.ev("__tick(30);if(typeof hideReveal==='function')hideReveal();for(let i=0;i<80&&typeof DLG!=='undefined'&&DLG;i++){__tick(400);dlgNext()}")
        print('page errors:', g.errors[:5])
        g.close(); b.close(); srv.shutdown()
    print(f'{DAYS} days in {time.time()-t0:.0f}s')


if __name__ == '__main__':
    main()
