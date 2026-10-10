"""The normal player's first thirty days (tools/qa/new_game_timeline.py --days 30 --seed N, policy 'normal': taps the screen,
decides from what the screen shows), one block per run: the day's money, staff, level, tables, guests, lost, net, the guests' average
satisfaction (the summary's avg, 0-100); the first evening ever ON FIRE (S.achievements.fire); the hires and the expansions as the player pressed them; the first day of the stories' main beats.
  python3 summary.py DIR [DIR ...]   (each DIR holds normal_<seed>.json from one build)"""
import json, sys, glob, os
BEATS = ['first_shift', 'yj_meet', 'yj_three', 'yj_key', 'wall_worry', 'wall_settle', 'tasting_start', 'dylan_valentine', 'critic_back', 'sm_a', 'lounge_idea']
for D in sys.argv[1:]:
    print(f'==== {D}')
    for f in sorted(glob.glob(os.path.join(D, 'normal_*.json'))):
        x = json.load(open(f, encoding='utf-8')); rows = x['rows']
        print(f"-- {os.path.basename(f)}  days {len(rows)}  page errors {len(x.get('errors') or [])}")
        print('   day  money    staff (roles)                lvl tbl guests lost   net   sat')
        for r in rows:
            s = r.get('sum') or {}; roles = ','.join(f'{k}{v}' for k, v in sorted((r.get('roles') or {}).items()))
            print(f"   {r['day']:>3} {r['money']:>7} {r['crew']:>2} ({roles:<24}) {r['level']:>3} {r['tables']:>3} {s.get('guests', 0):>6} {s.get('lost', 0):>4} {s.get('net', 0):>6} {s.get('avg', 0):>4}")
        acts = [(r['day'], d.get('pressed') or '') for r in rows for d in (r.get('decisions') or []) if d.get('kind') == 'decide' and any(w in (d.get('pressed') or '') for w in ('聘請', '擴建', '訓練', '加一張桌子'))]
        print('   hires / training / expansions / tables:', acts)
        fi = x.get('first') or {}
        print('   first day of:', {k: fi.get(k) for k in BEATS})
        print('   the first evening ever ON FIRE:', ('Day %s' % rows[-1]['firstFire']) if rows[-1].get('firstFire') else ('none in these days' if 'firstFire' in rows[-1] else 'not recorded by this build\'s simulation'))
