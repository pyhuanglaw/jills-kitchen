"""What the player was told and who walked in, day by day — from the --json of tools/qa/new_game_timeline.py (2026-10-11, the
checks of v2.5.4's three decisions, docs/v24/three_decisions_2026-10-11.txt, over long normal-player runs).

The observer (tools/qa/sim_player.py ECON_HOOKS) keeps, per day, every notice (toast) with its moment of the evening and every
group's name with what kind of guest it was. This counts per day:
  補貨：冰箱滿了 / 已退回下架 — what 「一鍵補到建議量」 said (decision 一: no fridge-full notice every morning because of the
    dishes taken off the menu; 退掉不在菜單上的庫存 never asked for any more)
  離開（有名字）— 「X 等太久，離開了」「X 生氣地離開了…」「X 看到客滿，失望地走了…」 with X a story's beat visitor that evening
    (decision 二: never), or 怡君 before 秀琴阿姨 has gone over to her (yj_meet)
  一般客人重名 — a name of a guest with no name of their own (not a regular, a named person, a booking's or a story's) walking
    in more than once in one evening (decision 三: only when every name of the kind, its extra ones and 「另一位」 are used)

  python3 tools/qa/new_game_timeline.py --save player_day92_2105.json --days 12 --json run92.json > run92.txt
  python3 tools/qa/scan_timeline_json.py run92.json
"""
import sys, re, json, collections

LEAVE = re.compile(r'^(.+?) (?:等太久，離開了|生氣地離開了…|看到客滿，失望地走了…|和另外 \d+ 組看到客滿，失望地走了…)$')


def main(path):
    out = json.load(open(path, encoding='utf-8'))
    rows = out.get('rows') or []
    yj_meet = ((out.get('final') or {}).get('facts') or {}).get('yj_meet')
    tot = collections.Counter(); days = 0
    for r in rows:
        e = r.get('econ') or {}
        T = [t for _, t in (e.get('toasts') or [])]
        N = e.get('names') or []
        days += 1
        c = collections.Counter()
        for t in T:
            if '冰箱滿了' in t: c['補貨：冰箱滿了'] += 1
            if '已退回' in t and '下架菜品' in t: c['補貨：已退回下架'] += 1
            if '退掉不在菜單上的庫存' in t: c['提示叫玩家去按「退掉不在菜單上的庫存」'] += 1
            if '錢不夠：' in t: c['補貨：錢不夠'] += 1
        beat = {n[0] for n in N if len(n) > 4 and n[4]}
        for t in T:
            m = LEAVE.match(t)
            if not m: continue
            who = m.group(1)
            c['離開的提示'] += 1
            if who in beat: c['離開（故事那一幕的人）'] += 1
            if '怡君' in who and (yj_meet is None or r['day'] < yj_meet): c['離開（還不認識的怡君）'] += 1
        if yj_meet is None or r['day'] < yj_meet:
            c['提示裡出現「怡君」（還不認識）'] += sum(1 for t in T if '怡君' in t)
        plain = [n[0] for n in N if not (n[1] or n[2] or n[3])]
        dup = {n for n in plain if plain.count(n) > 1}
        c['客人組數'] += len(N); c['一般客人'] += len(plain)
        if dup: c['一般客人重名（名字數）'] += len(dup)
        tot.update(c)
        show = {k: v for k, v in c.items() if v and k not in ('客人組數', '一般客人', '離開的提示')}
        print(f"Day {r['day']:3d}  客人 {c['客人組數']:3d} 組（一般 {c['一般客人']:3d}）  離開提示 {c['離開的提示']:2d}  " + ('  '.join(f'{k} {v}' for k, v in show.items()) or '—')
              + (f"  重名：{'、'.join(sorted(dup))}" if dup else ''))
    print('total:', dict(tot)); print('days:', days, ' 怡君 yj_meet:', yj_meet, ' page errors:', len(out.get('errors') or []))


if __name__ == '__main__':
    main(sys.argv[1])
