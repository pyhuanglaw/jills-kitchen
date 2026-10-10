"""v2.5 (fb86e3a) vs v2.5.1 (2e67df3): the normal player's new games (tools/qa/new_game_timeline.py, --days 50, seeds 300-302).
  python3 compare.py BASE_DIR NEW_DIR   (each with normal_300.json, normal_301.json, normal_302.json)"""
import json, sys, os
BASE, NEW = sys.argv[1], sys.argv[2]
RANGES = ((1, 3), (4, 7), (8, 14), (15, 24), (25, 34), (35, 50))
YJ = ['yj_meet', 'yj_key', 'wall_worry', 'wall_mediation', 'wall_article']
def load(d, sd): return json.load(open(os.path.join(d, f'normal_{sd}.json')))['rows']
def first(rows, k):
    for r in rows:
        for b in r.get('beats') or []:
            if b.split(':', 1)[-1] == k: return r['day']
    return None
for sd in (300, 301, 302):
    A, B = load(BASE, sd), load(NEW, sd)
    print(f'== seed {sd}')
    for tag, R in (('v2.5  ', A), ('v2.5.1', B)):
        lv = {}
        for r in R: lv.setdefault(r['level'], r['day'])
        crew = {d: next((r['crew'] for r in R if r['day'] == d), None) for d in (10, 25, 30, 40, 50)}
        ff = next((r['firstFire'] for r in R if r.get('firstFire')), None)
        print(f"  {tag} level first day {lv}  crew on day 10/25/30/40/50 {list(crew.values())}  first ON FIRE day {ff}  money day 30 ${next(r['money'] for r in R if r['day']==30):,} day 50 ${R[-1]['money']:,}  rating day 50 {R[-1]['rate']}")
        print('         怡君／那面牆', {k: first(R, k) for k in YJ})
    print('  days    |  guests  |  沒等到  |  tips   |  net    (v2.5 → v2.5.1)')
    for a, b in RANGES:
        def avg(R, k): s = [r['sum'][k] for r in R if a <= r['day'] <= b]; return sum(s) / len(s) if s else 0
        print(f'  {a:>2}-{b:<2}   | {avg(A,"guests"):5.1f} → {avg(B,"guests"):5.1f} | {avg(A,"lost"):4.1f} → {avg(B,"lost"):4.1f} | {avg(A,"tips"):6.0f} → {avg(B,"tips"):6.0f} | {avg(A,"net"):6.0f} → {avg(B,"net"):6.0f}')
