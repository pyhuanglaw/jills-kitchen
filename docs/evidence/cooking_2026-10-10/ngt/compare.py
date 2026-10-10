"""Side by side: two builds' normal-player runs (hires as pressed, the day of the Bistro, money on Days 10/20/30, guests and lost a night
in Days 1-10, 11-20, 21-30, the net a night, the first day of the stories' main beats, the first ON FIRE). python3 compare.py BEFORE_DIR FINAL_DIR"""
import json, sys, glob, os
for tag, D in [('before', sys.argv[1]), ('final', sys.argv[2])]:
    print('==', tag, D)
    for f in sorted(glob.glob(os.path.join(D, 'normal_*.json'))):
        x = json.load(open(f, encoding='utf-8')); rows = x['rows']; fi = x.get('first') or {}
        hires = [(r['day'], d.get('pressed')) for r in rows for d in (r.get('decisions') or []) if d.get('kind') == 'decide' and '聘請' in (d.get('pressed') or '')]
        lv2 = next((r['day'] for r in rows if r['level'] >= 2), None)
        m = {r['day']: r['money'] for r in rows}
        L = lambda a, b: sum((r['sum'] or {}).get('lost', 0) for r in rows if a <= r['day'] <= b) / (b - a + 1)
        G = lambda a, b: sum((r['sum'] or {}).get('guests', 0) for r in rows if a <= r['day'] <= b) / (b - a + 1)
        N = lambda a, b: sum((r['sum'] or {}).get('net', 0) for r in rows if a <= r['day'] <= b) / (b - a + 1)
        print(f"{os.path.basename(f)} hires {hires} | lv2 D{lv2} | money D10 {m.get(10)} D20 {m.get(20)} D30 {m.get(30)} | tables30 {rows[-1]['tables']} crew30 {rows[-1]['crew']}"
              f" | guests/lost a night D1-10 {G(1,10):.1f}/{L(1,10):.1f} D11-20 {G(11,20):.1f}/{L(11,20):.1f} D21-30 {G(21,30):.1f}/{L(21,30):.1f} | net a night D1-10 {N(1,10):.0f} D21-30 {N(21,30):.0f}"
              f" | yj_meet {fi.get('yj_meet')} yj_key {fi.get('yj_key')} wall {fi.get('wall_worry')} tasting {fi.get('tasting_start')} first_shift {fi.get('first_shift')} | fire {rows[-1].get('firstFire', 'n/a')} | errors {len(x.get('errors') or [])}")
