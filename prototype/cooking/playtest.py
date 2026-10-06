"""Play-test the cooking prototype with the bot (bot.js): every night, a few seeds, with and without the staff.
  python3 prototype/cooking/playtest.py [--react 0.8] [--seeds 3] [--json out.json]
Prints, per night: tables served / left, burnt, quality, the player's moves a minute, how often the next move was
from the same place, how many things were cooking at once, and what the staff carried."""
import argparse, json, os, statistics as stt
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument('--react', type=float, default=.8); ap.add_argument('--seeds', type=int, default=3)
ap.add_argument('--json', default=None); ap.add_argument('--nights', default='1,2,3,4'); ap.add_argument('--nocook', action='store_true'); ap.add_argument('--line', default='stove')
A = ap.parse_args()
bot = open(os.path.join(HERE, 'bot.js'), encoding='utf-8').read()
rows = []
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 390, 'height': 844})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + os.path.join(HERE, 'index.html')); pg.wait_for_timeout(300); pg.add_script_tag(content=bot)
    for k in [int(x) for x in A.nights.split(',')]:
        for variant in ([False, True] if (A.nocook and k >= 3) else [False]):
            res = []
            for s in range(A.seeds):
                r = pg.evaluate(f"__botRun({k},{{seed:{s+1},noTut:true,react:{A.react},noCook:{'true' if variant else 'false'},line:'{A.line}'}})")
                res.append(r)
            def m(f): return stt.mean(f(r) for r in res)
            row = {'night': k, 'nocook': variant, 'served': m(lambda r: r['served']), 'left': m(lambda r: r['left']), 'burnt': m(lambda r: r['burnt']),
                   'q': m(lambda r: r['q']), 'stars': m(lambda r: r['stars']), 'money': m(lambda r: r['rev'] + r['tips']),
                   'moves_min': m(lambda r: r['moves'] / max(.1, r['mins'])), 'same': m(lambda r: r['same'] / max(1, r['moves'])),
                   'conc': m(lambda r: r['conc'] / max(1, r['concT'])), 'staff': m(lambda r: r['staff']), 'mins': m(lambda r: r['mins'])}
            rows.append(row)
            print(f"night {k}{' (no staff)' if variant else ''}: served {row['served']:.1f} left {row['left']:.1f} burnt {row['burnt']:.1f} q {row['q']:.0f} ★{row['stars']:.1f} ${row['money']:.0f} | moves/min {row['moves_min']:.1f} same-place {row['same']*100:.0f}% cooking-at-once {row['conc']:.1f} staff-carried {row['staff']:.0f} ({row['mins']:.1f} min)")
    print('errors', errs[:3])
    b.close()
if A.json:
    json.dump(rows, open(A.json, 'w'), ensure_ascii=False, indent=1)
