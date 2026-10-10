"""What a normal player ran into, day by day — from the log of tools/qa/new_game_timeline.py (2026-10-10, the overnight QA that
found the one-tap restock leaving the newest dishes with nothing: 「沒有備料」 on every one of twelve days).

The timeline prints, for each day, the summary line and the player's decisions with what the screen said (「畫面：…」,
「開店按鈕下的提醒：…」). This counts, per day, the warnings a player saw and anything that looks wrong:
  開店：沒有備料 — the opening warns a dish of tonight's menu has nothing
  補貨：冰箱滿了 — the one-tap restock could not reach every suggestion
  錢不夠 — a purchase the money did not cover
  等太久 / 生氣離開 — guests leaving (in the decisions the player read)
  畫面不對 / 營業結束不了 / 程式錯誤 / 觀測錯誤 — the run itself went wrong (a day not reaching its prep, a service that did
  not end, a traceback, a probe that threw)
A warning on every day is the thing to look into: something the player cannot get rid of.

  python3 tools/qa/new_game_timeline.py --save player_day6_1254.json --days 14 > run.txt
  python3 tools/qa/scan_timeline_log.py run.txt
"""
import sys, re, collections
KEYS = {'沒有備料': '開店：沒有備料', '冰箱滿了': '補貨：冰箱滿了', '錢不夠': '錢不夠', '等太久': '等太久', '生氣地離開': '生氣離開',
        'expected the': '畫面不對', 'did not end': '營業結束不了', 'Traceback': '程式錯誤', 'ERR ': '觀測錯誤'}


def main(path):
    txt = open(path, encoding='utf-8').read().splitlines()
    per = collections.defaultdict(collections.Counter); days = 0; cur = None
    for line in txt:
        m = re.match(r'Day\s+(\d+)\s', line)
        if m:
            cur = int(m.group(1)); days += 1; continue
        m = re.search(r'\[Day (\d+)\]', line)
        d = int(m.group(1)) if m else cur
        for k, lab in KEYS.items():
            if k in line:
                per[d][lab] += 1
    tot = collections.Counter()
    for d in sorted(x for x in per if x is not None):
        tot.update(per[d]); print(f'Day {d}: ' + ', '.join(f'{k} {n}' for k, n in per[d].most_common()))
    print('total:', dict(tot)); print('days played:', days)
    pe = [l for l in txt if l.startswith('page errors')]
    print(pe[-1] if pe else 'page errors: (no line — the run did not finish)')


if __name__ == '__main__':
    main(sys.argv[1])
