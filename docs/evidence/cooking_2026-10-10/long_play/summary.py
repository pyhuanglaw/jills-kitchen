"""The long play's summary: per run, the days, stuck services, two Jills, page errors, broken invariants, the money, the
reloads mid-service, guests and lost per day; and whether the money moved by exactly the day's net every day."""
import json, sys, glob, os
D = sys.argv[1]
for f in sorted(glob.glob(os.path.join(D, '*.jsonl'))):
    rows = [json.loads(l) for l in open(f) if l.startswith('{')]
    if not rows: print(os.path.basename(f), 'no rows'); continue
    st = sum(r['stuck'] for r in rows); tj = sum(r['two_jills'] for r in rows); er = sum(1 for r in rows if r['errors']); bad = sum(1 for r in rows if r['bad'])
    days = [r['day'] for r in rows]
    print(f"{os.path.basename(f)} days {len(rows)} D{days[0]}-D{days[-1]} stuck {st} two_jills {tj} errors {er} bad {bad} money {rows[0]['money']-(rows[0]['summary'] or {}).get('net',0)} -> {rows[-1]['money']} crew {rows[-1]['crew']} level {rows[-1]['level']} facts {sum(r['facts'] for r in rows)}")
    for r in rows:
        if r.get('reload'): print(f"   reload day {r['day']} {r['reload']}")
    print('   guests', [(r['summary'] or {}).get('guests') for r in rows])
    print('   lost  ', [(r['summary'] or {}).get('lost') for r in rows])
    if er or bad: print('   problems', [(r['day'], r['errors'], r['bad']) for r in rows if r['errors'] or r['bad']][:5])
for f in sorted(glob.glob(os.path.join(D, '*.jsonl'))):
    rows = [json.loads(l) for l in open(f) if l.startswith('{')]
    if len(rows) < 2: continue
    off = [(b['day'], b['money'] - a['money'], (b['summary'] or {}).get('net')) for a, b in zip(rows, rows[1:]) if b['money'] - a['money'] != (b['summary'] or {}).get('net')]
    print(os.path.basename(f), "money change = the day's net on every day:", not off, off[:5])
