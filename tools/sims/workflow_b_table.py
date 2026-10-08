"""Averages per variant from tools/sims/workflow_b_variant.py output: python3 tools/sims/workflow_b_table.py FILE.jsonl..."""
import json, sys
from collections import defaultdict
agg = defaultdict(lambda: defaultdict(float)); order = []
for f in sys.argv[1:]:
    for l in open(f):
        r = json.loads(l); k = r['name']
        if k not in order: order.append(k)
        a = agg[k]; s = r['summary'] or {}; e = r['end'] or {}
        a['n'] += 1; a['g'] += s.get('guests', 0); a['l'] += s.get('lost', 0); a['rev'] += s.get('rev', 0); a['dirty'] += r['dirtyAvg']
        dd = e.get('dd') or {}; a['block'] += dd.get('blockT', 0) or 0; a['wash'] += dd.get('wash', 0) or 0; a['full'] += dd.get('full', 0) or 0
        a['starts'] += dd.get('starts', 0) or 0; a['startN'] += dd.get('startN', 0) or 0
        for role in ('cleaner', 'waiter'):
            wl = (e.get('wl') or {}).get(role) or {}
            a[role + 'T'] += sum(v for kk, v in wl.items() if kk != 'dist')
            for kk in ('idle', 'wash', 'clear', 'serve', 'guest'): a[role + kk] += wl.get(kk, 0)
print(f"{'variant':16s} {'n':>2s} {'guests':>6s} {'lost':>5s} {'revenue':>8s} {'dirtyT':>6s} {'blockT':>6s} {'fullS':>5s} {'washed':>6s} {'wash@':>5s} | cleaner idle/clear/wash | waiter idle/serve/clear/wash")
for k in order:
    a = agg[k]; n = a['n']; cT = max(1, a['cleanerT']); wT = max(1, a['waiterT'])
    print(f"{k:16s} {int(n):2d} {a['g']/n:6.1f} {a['l']/n:5.1f} {a['rev']/n:8.0f} {a['dirty']/n:6.2f} {a['block']/n:6.0f} {a['full']/n:5.0f} {a['wash']/n:6.1f} {a['startN']/max(1,a['starts']):5.1f} | "
          f"{100*a['cleaneridle']/cT:3.0f}% {100*a['cleanerclear']/cT:3.0f}% {100*a['cleanerwash']/cT:3.0f}% | {100*a['waiteridle']/wT:3.0f}% {100*a['waiterserve']/wT:3.0f}% {100*a['waiterclear']/wT:3.0f}% {100*a['waiterwash']/wT:3.0f}%")
