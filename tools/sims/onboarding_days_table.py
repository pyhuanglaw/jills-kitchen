import json, sys
from collections import defaultdict
def load(f):
    return [json.loads(l) for l in open(f)]
for f in sys.argv[1:]:
    rows = load(f)
    print('==', f.split('/')[-1], len(rows), 'evenings')
    agg = defaultdict(list)
    for r in rows:
        agg[(r['player'], r['day'])].append(r)
    print('player day | guests lost | full_s fulls block_s peak | washed(by) | jill dish_s wash_s table_s | xq clear wash | money after stock → end')
    for (who, day), rs in sorted(agg.items(), key=lambda x: (x[0][0], x[0][1])):
        n = len(rs); S = lambda f: sum(f(r) for r in rs) / n
        g = S(lambda r: (r['summary'] or {}).get('guests', 0)); lost = S(lambda r: (r['summary'] or {}).get('lost', 0))
        full = S(lambda r: r['dd'].get('full', 0)); fulls = S(lambda r: r['dd'].get('fulls', 0)); blk = S(lambda r: r['dd'].get('blockT', 0)); peak = S(lambda r: r['dd'].get('peak', 0))
        wash = S(lambda r: r['dd'].get('wash', 0)); by = defaultdict(float)
        for r in rs:
            for k, v in (r['dd'].get('by') or {}).items(): by[k] += v / n
        jd = S(lambda r: r['jill_floor'].get('dish', 0)); jw = S(lambda r: (r['dd'].get('washT') or {}).get('jill', 0)); jt = S(lambda r: r['jill_floor'].get('table', 0))
        xc = S(lambda r: r['xq'].get('clear', 0)); xw = S(lambda r: r['xq'].get('wash', 0))
        m1 = S(lambda r: r['money_after_stock']); me = S(lambda r: r['money_end'])
        lostl = [ (r['summary'] or {}).get('lost', 0) for r in rs]
        print(f"{who:5} D{day} | {g:5.1f} {lost:4.1f} {lostl} | {full:5.1f} {fulls:3.1f} {blk:5.1f} {peak:4.1f} | {wash:4.1f} {dict((k, round(v,1)) for k,v in by.items())} | {jd:5.1f} {jw:5.1f} {jt:5.1f} | {xc:5.1f} {xw:5.1f} | {m1:7.0f} → {me:7.0f}")
