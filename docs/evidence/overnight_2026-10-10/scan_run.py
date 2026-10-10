"""Summarise a new_game_timeline run log: per day, the warnings a player saw (stock, fridge, money, staff, opening), and
anything that looks wrong (a stuck day, a page error, an unexpected screen).
  python3 scan_run.py RUN.txt"""
import sys, re, collections
txt = open(sys.argv[1], encoding='utf-8').read().splitlines()
KEYS = {'沒有備料': '開店：沒有備料', '冰箱滿了': '補貨：冰箱滿了', '錢不夠': '錢不夠', '等太久': '等太久', '生氣地離開': '生氣離開',
        'expected the': '畫面不對', 'did not end': '營業結束不了', 'Traceback': '程式錯誤', 'ERR ': '觀測錯誤'}
per = collections.defaultdict(collections.Counter); days = []
cur = None
for line in txt:
    m = re.match(r'Day\s+(\d+)\s', line)
    if m: cur = int(m.group(1)); days.append(line[:150]); continue
    m = re.search(r'\[Day (\d+)\]', line)
    d = int(m.group(1)) if m else cur
    for k, lab in KEYS.items():
        if k in line: per[d][lab] += 1
tot = collections.Counter()
for d in sorted(x for x in per if x is not None):
    tot.update(per[d]); print(f'Day {d}: ' + ', '.join(f'{k} {n}' for k, n in per[d].most_common()))
print('total:', dict(tot)); print('days played:', len(days))
pe = [l for l in txt if l.startswith('page errors')]; print(pe[-1] if pe else 'page errors: (no line)')
