"""ON FIRE for Jill's kitchen of one (2026-10-10, after v2.5): replay the recorded tables (tables_fire_off_2baa9d4.jsonl, new games
on 2baa9d4 with the fire off, the normal player's own shop decisions) under candidate windows. A row of a table is
[t, wait from sitting down to the whole order served, all Perfect, any of Jill's, busy share, tables, cooks at work, waiters at work,
dishes, level]; a walkout is [t, -1, 0, 0, 0]. The run rule is the game's (fireTable): not all Perfect or slower than SLOW ends the
run; slower than FAST does not count; a quiet floor (busy < .5) does not count; Jill's table 1.5, else 1; 4 lights it.
  python3 calibrate_solo.py tables_fire_off_2baa9d4.jsonl"""
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1] if len(sys.argv) > 1 else 'tables_fire_off_2baa9d4.jsonl')]
def fires(tab, FAST, SLOW, RUN=4, BUSY=.5):
    run = 0
    for row in tab:
        if row[1] < 0: run = 0; continue
        t, w, allp, jill, busy = row[:5]
        if not allp or w > SLOW: run = 0; continue
        if w > FAST or busy < BUSY: continue
        run += 1.5 if jill else 1
        if run >= RUN: return t
    return None
def solo(r): return all(x[6] == 0 for x in r['tab'] if x[1] >= 0)   # no cook at work all evening
for svc in ('human', 'perfect'):
    E = [r for r in rows if r['service'] == svc]
    S = [r for r in E if solo(r)]; C = [r for r in E if not solo(r)]
    print(f"{svc}: {len(E)} evenings ({len({r['seed'] for r in E})} new games); Jill cooking alone {len(S)}, with a cook {len(C)}")
    print(f"  with a cook, 30/36 (unchanged): {sum(fires(r['tab'],30,36) is not None for r in C)}/{len(C)}")
    print(f"  Jill alone, 30/36 (before):     {sum(fires(r['tab'],30,36) is not None for r in S)}/{len(S)}")
    for F in (32, 33, 34, 35, 36):
        print(f"  Jill alone, FAST {F}, SLOW 38/39/40/42/44:", '  '.join(f"{sum(fires(r['tab'],F,Sl) is not None for r in S)}/{len(S)}" for Sl in (38, 39, 40, 42, 44)))
    by = {}
    for r in S:
        k = r['day'] if r['day'] <= 2 else '3+'
        o = by.setdefault(k, [0, 0]); o[0] += 1; o[1] += fires(r['tab'], 33, 40) is not None
    print('  33/40 by day (Jill alone):', {k: f'{v[1]}/{v[0]}' for k, v in by.items()})
