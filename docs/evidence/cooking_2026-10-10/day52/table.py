"""python3 table.py runs [BUILD ...]  (BUILD: the file prefix in runs/, e.g. main_8298e18, final_8ded2e2, 1f7ff75)
The Day 52 sweep's table: per build and seed base, the beats' days, which of the test's targets it meets (as the test checks
them), the evenings; then per build: the mean days, how many meet every target, how many have the key on Day 63 or later."""
import json, sys, glob, os
D = sys.argv[1]; builds = sys.argv[2:] or ['main_8298e18', 'final_8ded2e2']
names = {'main_8298e18': 'main 8298e18', 'final_8ded2e2': 'final 8ded2e2'}
def targets(d):
    F = d['F']; first = d['first']; miss = []
    if any(v is None for v in F.values()): miss.append('a beat missing in forty days: ' + ','.join(k for k, v in F.items() if v is None))
    vals = [v for v in F.values() if v is not None]
    if not (F['yj_key'] is not None and F['yj_key'] - F['yj_meet'] <= 9 and F['yj_key'] <= first + 10): miss.append('the move within ten days')
    if not (F['wall_worry'] is not None and first + 9 <= F['wall_worry'] <= first + 13): miss.append(f'the wall in {first+9}-{first+13}')
    if not (F['wall_settle'] is not None and F['wall_settle'] - F['wall_worry'] <= 18 and F['wall_settle'] <= first + 29): miss.append(f'by {first+29} / within 18 days')
    if F['wall_worry'] is not None and F['yj_key'] is not None and F['wall_worry'] < F['yj_key'] + 2: miss.append('the wall before the move settled')
    return miss
for b in builds:
    rows = []
    for f in sorted(glob.glob(os.path.join(D, f'{b}_*.json'))):
        try: d = json.load(open(f))
        except Exception: continue
        rows.append(d)
    print(f'== {names.get(b, b)}  ({len(rows)} seeds)')
    for d in sorted(rows, key=lambda x: x['base']):
        F = d['F']; m = targets(d); e = d['evenings']
        art = F.get('wall_article')
        print(f"{d['base']}: yj_meet {F['yj_meet']}, yj_key {F['yj_key']}, wall_worry {F['wall_worry']}, wall_settle {F['wall_settle']}"
              f"{'' if F['wall_settle'] is None or F['wall_worry'] is None else ' (%d days)' % (F['wall_settle'] - F['wall_worry'])}, wall_article {art}"
              f"  — {'meets every target' if not m else 'misses: ' + ', '.join(m)}   | evenings {e['g']} guests, {e['l']} lost, {e['a']} angry, satisfaction {e['w']}, ${e['r']:,.0f}")
    if rows:
        mean = lambda k: sum(d['F'][k] for d in rows if d['F'][k] is not None) / max(1, sum(1 for d in rows if d['F'][k] is not None))
        allm = sum(1 for d in rows if not targets(d)); k63 = sum(1 for d in rows if (d['F']['yj_key'] or 99) >= 63)
        ev = lambda k: sum(d['evenings'][k] for d in rows) / len(rows)
        print(f"   mean: yj_key {mean('yj_key'):.2f}, wall_worry {mean('wall_worry'):.2f}, wall_settle {mean('wall_settle'):.2f}, wall_article {mean('wall_article'):.2f}"
              f" | every target: {allm} of {len(rows)} | the key on Day 63 or later: {k63} of {len(rows)}"
              f" | evenings: {ev('g'):.1f} guests, {ev('l'):.1f} lost, {ev('a'):.1f} angry, ${ev('r'):,.0f}")
