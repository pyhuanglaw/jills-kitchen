"""v2.4 fresh-save simulation (docs/v24/xiuqin_from_day1_2026-10-01.txt): a new game played from Day 1 by the
perfect bot, the shop bought the way a person would (a growth plan), the story arbiter running as in play. Checks the
player's fresh-game premise:

  - 秀琴阿姨 is in the restaurant's evenings from Day 1 (she walks in near closing to help tidy up);
  - she is not free labour: until she is hired, a day with her and the same day without her (window.__noXQH) end with
    the same money, guests, stars and reviews — compare two runs with --noxqh;
  - the first cleaner hired is her (the same person: id 'xq', what she knows carries over);
  - 怡君 comes reasonably early, not gated on a late day or on Sophie × Mia.

  python3 tools/sims/v24_fresh.py [--days 24] [--seed 300] [--plan early|late|never] [--noxqh] [--json out.json]
"""
import sys, os, json, time, argparse
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, os.path.join(ROOT, 'tests'))
import run_tests as rt
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument('--days', type=int, default=24)
ap.add_argument('--seed', type=int, default=300)
ap.add_argument('--plan', default='late', choices=['early', 'late', 'never'])
ap.add_argument('--noxqh', action='store_true')
ap.add_argument('--json', default=None)
A = ap.parse_args()

SEED = "Math.random=(function(){let a=%d;return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
KEYS = ['xq_helper', 'xq_hired', 'yj_meet', 'yj_look', 'yj_three', 'yj_chose', 'yj_move', 'yj_move_told', 'yj_key', 'yj_key_seen',
        'wall_worry', 'wall_photos', 'wall_visit', 'wall_wang', 'wall_setback', 'wall_report', 'wall_fee', 'wall_prep', 'wall_mediation', 'wall_settle']
# a person's shop: early = the cleaner is the first hire (Day 4); late = a waiter first, the cleaner once the room is bigger
PLANS = {
    'early': {1: [('rd', {'d': 'pasta'}), ('buyTable', {})], 2: [('buyEq', {'k': 'bar'}), ('buyTable', {})], 4: [('hire', {'k': 'cleaner'})],
              5: [('expand', {}), ('buyDecor', {'k': 'plants'})], 7: [('hire', {'k': 'waiter'}), ('buyTable', {})], 9: [('expand', {})], 10: [('hire', {'k': 'chef'})]},
    'late': {1: [('rd', {'d': 'pasta'}), ('buyTable', {})], 2: [('buyEq', {'k': 'bar'}), ('buyTable', {})], 3: [('hire', {'k': 'waiter'})],
             5: [('expand', {}), ('buyDecor', {'k': 'plants'})], 8: [('hire', {'k': 'chef'}), ('buyTable', {})], 11: [('expand', {})], 14: [('hire', {'k': 'cleaner'})]},
    'never': {1: [('rd', {'d': 'pasta'}), ('buyTable', {})], 2: [('buyEq', {'k': 'bar'}), ('buyTable', {})], 3: [('hire', {'k': 'waiter'})],
              5: [('expand', {}), ('buyDecor', {'k': 'plants'})], 8: [('hire', {'k': 'chef'}), ('buyTable', {})], 11: [('expand', {})]},
}

def main():
    t0 = time.time(); rows = []
    with sync_playwright() as p:
        srv, port = rt.start_server(); b = p.chromium.launch()
        g = rt.Game(b, port, 'index', seed=A.seed, manual=True, viewport={'width': 390, 'height': 844})
        rt.install_bot(g)
        def act(a, **kv):
            ds = ''.join(f"el.dataset.{k}='{v}';" for k, v in kv.items())
            g.ev(f"(()=>{{const el=document.createElement('button');el.dataset.act='{a}';{ds}$('#screen').appendChild(el);el.click();el.remove()}})()")
        g.click('[data-act=open]')
        g.ev("window.__fastSay=1" + (";window.__noXQH=1" if A.noxqh else ""))
        for day in range(1, A.days + 1):
            act('restock'); g.ev("__tick(200)"); rt.fill_fridge(g)   # a stocked fridge: the bot serves everyone, and a sold-out evening is not what this measures
            g.ev(SEED % (A.seed * 1000 + day))
            rt.start_day(g)
            g.ev("window.__yj=0;window.__xqSeen=0")
            for _ in range(400):
                r = g.page.evaluate('()=>window.__bot(150,1/30)')
                g.ev("if(R){if(R.groups.some(q=>isYJ(q)))__yj=1;if(R.xqh&&!R.xqh.arriving)__xqSeen=1}")
                if g.ev("phase") != 'service' or r['ticks'] < 150: break
            if g.ev("phase") == 'service': g.ev("__bot(60000,1/30)")
            g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
            info = json.loads(g.ev("""JSON.stringify({day:S.day,money:S.money,
              sum:S.lastSummary?{rev:S.lastSummary.rev,tips:S.lastSummary.tips,guests:S.lastSummary.guests,lost:S.lastSummary.lost,stars:S.lastSummary.stars,net:S.lastSummary.net}:null,
              reviews:S.reviews.length,xq:window.__xqSeen,yj:window.__yj,mode:xqHelperMode(),known:xqKnown(),
              crew:(S.crew||[]).map(m=>m.name+(m.id==='xq'?'(xq)':'')),
              fired:%s.filter(k=>fact(k)&&fact(k).l===S.day).map(k=>k+(fact(k).d===S.day?'':'·')),
              errors:(window.__errs||[]).length})""" % json.dumps(KEYS)))
            rows.append(info)
            s = info['sum'] or {}
            print(f"Day {info['day']:3d}  ${info['money']:>7}  rev {s.get('rev')}  guests {s.get('guests')}  stars {s.get('stars')}  "
                  f"秀琴 {'在' if info['xq'] else '-'}  怡君 {'來' if info['yj'] else '-'}  mode {'helper' if info['mode'] else 'crew' if any('秀琴' in c for c in info['crew']) else '-'}  "
                  f"known {int(info['known'])}  crew {info['crew']}  {' '.join(info['fired'])}", flush=True)
            if g.ev("phase") == 'summary': g.click('[data-act=toShop]')
            for a, kv in PLANS[A.plan].get(day, []):
                act(a, **kv); g.ev("__tick(30)")
            g.click('[data-act=nextDay]'); g.ev("__tick(100)")
        final = json.loads(g.ev("JSON.stringify(Object.fromEntries(%s.map(k=>[k,fact(k)?fact(k).d:null])))" % json.dumps(KEYS)))
        rel = json.loads(g.ev("JSON.stringify({sophie:xqKnows('sophie'),mia:xqKnows('mia'),xqid:(xqm()||{}).id||null})"))
        print('\nfirst day each:', {k: v for k, v in final.items() if v})
        print('秀琴阿姨 knows Sophie/Mia:', rel)
        print('majors per day > 1:', json.loads(g.ev("JSON.stringify((()=>{const per={};for(const t of story().trace.filter(t=>t.lane==='major'))(per[t.d]=per[t.d]||[]).push(t.k);return Object.entries(per).filter(([d,v])=>v.length>1)})())")))
        print('page errors:', g.errors[:5])
        if A.json:
            json.dump({'rows': rows, 'final': final, 'rel': rel, 'errors': g.errors[:20]}, open(A.json, 'w'), ensure_ascii=False, indent=1)
        g.close(); b.close()
    print(f'{A.days} days in {time.time()-t0:.0f}s')

if __name__ == '__main__':
    main()
