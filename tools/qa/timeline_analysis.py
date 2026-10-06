"""讀新玩家時間表的結果（QA, 2026-10-06）: the --json files of tools/qa/new_game_timeline.py, turned into the tables a
person asks for — each seed's road to The Lounge (the story, the rating, the money, the people, the signing, the opening,
the cash a week and two weeks on), and the Lounge's first weeks next to the week before it, room by room.

  python3 tools/qa/timeline_analysis.py out300.json out301.json out302.json [--md report.md]

Everything here is the observer's record (part B of tools/qa/sim_player.py): read after the day, never shown to the
simulated player. The player's own decisions are in each file's 'log' (what it saw, why, what it pressed).
"""
import sys, json, argparse, statistics as st


def first(rows, f):
    return next((r for r in rows if f(r)), None)


def day_of(r):
    return r['day'] if r else None


def money_on(rows, d):
    r = next((x for x in rows if x['day'] == d), None)
    return r['money'] if r else None


def hires(log, pred=lambda d: True):
    return [d for d in log if d['kind'] == 'decide' and d['pressed'] and '聘請' in d['pressed'] and d.get('cost') and pred(d)]


WAITS = ('等太久', '沒等到', '生氣離開', '等位', '耐心')


def timeline(o):
    rows, log = o['rows'], o['log']
    beats = {}
    for r in rows:
        for b in r['beats']:
            beats.setdefault(b.split(':', 1)[1], r['day'])
    view = beats.get('lin_viewing')
    opened = first(rows, lambda r: r['lounge'])
    od = day_of(opened)
    side = first(rows, lambda r: any(p[0] == '側廳' for p in (r.get('rentParts') or [])))
    sd = day_of(side)
    crew_on = lambda d: next((x['crew'] for x in rows if x['day'] == d), None)
    # the rating: the first time at 4.0, then the lowest before the Lounge opened, and the day it was back
    r40 = first(rows, lambda r: r['rate1'] >= 4.0)
    span = [r for r in rows if r40 and r['day'] > r40['day'] and (not od or r['day'] < od)]
    low = min(span, key=lambda r: r['rate1']) if span else None
    back = first([r for r in rows if low and r['day'] > low['day']], lambda r: r['rate1'] >= 4.0) if low else None
    why_low = []
    if low:
        for r in rows:
            if low['day'] - 2 <= r['day'] <= low['day']:
                for m in (r.get('seen') or {}).get('minus') or []:
                    why_low.append(f"Day {r['day']} {m['k']}（{m['v']}）")
    first_wait_hire = next(iter(hires(log, lambda d: any(w in (d['why'] or '') for w in WAITS))), None)
    first_hire = next(iter(hires(log)), None)
    m50 = first(rows, lambda r: r['money'] >= 50000)
    all3 = first(rows, lambda r: view and r['day'] >= view and r['rate1'] >= 4.0 and r['money'] >= 50000)
    paid = first(rows, lambda r: (r.get('proj') or {}).get('state') in ('signing', 'reno', 'built'))
    pd = day_of(paid)
    sign_press = next((d for d in log if d['kind'] == 'decide' and d['pressed'] and '簽約' in d['pressed'] and d.get('cost')), None)
    # Madame Lin's last night: signed before it, it is the evening before the signing (the branch's rule, 2026-10-06)
    last_night = beats.get('lin_last') or ((sign_press['day'] - 1) if sign_press else None)
    top = []
    wines = []
    if opened:
        top = sorted(opened.get('menu') or [], key=lambda x: -x[1])[:6]
        for d in log:
            if d['day'] <= od and d['kind'] == 'decide' and d['pressed'] and '研發' in d['pressed'] and '酒' in (d['why'] or '') and d.get('cost'):
                wines.append((d['day'], d['pressed']))
    return {
        'view': view, 'side': sd, 'crew_before_side': crew_on(sd - 1) if sd else None, 'crew_after_side': [crew_on(sd + k) for k in (0, 3, 7)] if sd else None,
        'r40': day_of(r40), 'low': (low['day'], low['rate1']) if low else None, 'why_low': why_low[:6], 'back40': day_of(back),
        'first_hire': (first_hire['day'], first_hire['pressed'], first_hire['why']) if first_hire else None,
        'first_wait_hire': (first_wait_hire['day'], first_wait_hire['pressed'], first_wait_hire['why']) if first_wait_hire else None,
        'm50': day_of(m50), 'all3': day_of(all3), 'sign_press': sign_press['day'] if sign_press else None, 'paid': pd,
        'last_night': last_night, 'lin_sign': beats.get('lin_sign'), 'opened': od,
        'roles_open': opened.get('roles') if opened else None, 'top_dishes': top, 'wines_dev': wines,
        'wines_n_open': opened.get('wines') if opened else None,
        'cash': {k: money_on(rows, od + k) for k in (0, 7, 14)} if od else None,
        'level_open': opened['level'] if opened else None,
    }


def room_week(rows, d0, d1):
    """averages over days d0..d1 (inclusive)"""
    R = [r for r in rows if d0 <= r['day'] <= d1 and r.get('econ')]
    if not R:
        return None
    def avg(f):
        v = [f(r) for r in R]
        v = [x for x in v if x is not None]
        return sum(v) / len(v) if v else None
    E = lambda r, room, k: ((r['econ'].get(room) or {}).get(k) or 0)
    rent_lg = lambda r: sum(p[1] for p in (r.get('rentParts') or []) if p[0] == 'Lounge')
    rent_main = lambda r: sum(p[1] for p in (r.get('rentParts') or []) if p[0] != 'Lounge')
    waits = lambda r: (sum(r['econ']['waits']) / len(r['econ']['waits'])) if r['econ'].get('waits') else None
    return {
        'days': len(R),
        '主廳客人': avg(lambda r: E(r, 'main', 'guests')), 'Lounge 客人': avg(lambda r: E(r, 'lounge', 'guests')),
        '主廳座位利用率': avg(lambda r: r['econ']['occMain'] / r['econ']['capMain'] if r['econ'].get('capMain') else None),
        'Lounge 座位利用率': avg(lambda r: r['econ']['occLg'] / r['econ']['capLg'] if r['econ'].get('capLg') else None),
        '主廳 食物營收': avg(lambda r: E(r, 'main', 'food')), '主廳 飲料營收': avg(lambda r: E(r, 'main', 'drink')), '主廳 酒水營收': avg(lambda r: E(r, 'main', 'wine')),
        'Lounge 食物營收': avg(lambda r: E(r, 'lounge', 'food')), 'Lounge 酒水營收': avg(lambda r: E(r, 'lounge', 'wine') + E(r, 'lounge', 'drink')),
        '小費（主廳）': avg(lambda r: E(r, 'main', 'tips')), '小費（Lounge）': avg(lambda r: E(r, 'lounge', 'tips')),
        '全店營收（含小費、獎金）': avg(lambda r: r['sum']['rev'] + r['sum']['tips'] + (r['sum'].get('bonus') or 0)),
        '食材／補貨成本': avg(lambda r: r['sum']['cost']), '酒水成本': avg(lambda r: r['sum'].get('wine') or 0),
        '餐廳員工薪水': avg(lambda r: (r.get('wagePools') or {}).get('restaurant')), 'Lounge 員工薪水': avg(lambda r: (r.get('wagePools') or {}).get('lounge') or 0),
        '主廳／餐廳租金': avg(rent_main), 'Lounge 租金': avg(rent_lg), 'Ken 的費用': avg(lambda r: r['sum'].get('ken') or 0),
        '每日淨額': avg(lambda r: r['sum']['net']), '每日收店現金': avg(lambda r: r['money']),
        '沒等到的客人': avg(lambda r: r['sum'].get('lost') or 0), '生氣離開（人）': avg(lambda r: (r['econ'].get('left') or {}).get('angry') or 0),
        '出餐數': avg(lambda r: r['econ'].get('served')), '平均等待（秒）': avg(waits),
    }


def fmt(v):
    if v is None:
        return '—'
    if isinstance(v, float) and v < 1.5 and v > 0 and v != int(v):
        return f'{v * 100:.0f}%'
    if isinstance(v, (int, float)):
        return f'{v:,.0f}'
    return str(v)


def report(files):
    out = []
    data = [(f, json.load(open(f, encoding='utf-8'))) for f in files]
    out.append('## 每個 seed 的時間表（觀測器紀錄）\n')
    T = []
    for f, o in data:
        t = timeline(o); T.append(t)
        seed = o['args']['seed']
        out.append(f"### seed {seed}（{o.get('policy')}／{o.get('service')}）")
        L = [('《看看》', t['view']), ('側廳購入', t['side']), ('側廳前一天員工數', t['crew_before_side']), ('側廳當天／3 天後／7 天後員工數', t['crew_after_side']),
             ('第一次評分 ≥4.0', t['r40']), ('之後到 Lounge 前最低評分（Day, 分數）', t['low']), ('最低時的扣分理由', '；'.join(t['why_low']) or '—'),
             ('回到 4.0', t['back40']), ('第一次聘人', t['first_hire'] and f"Day {t['first_hire'][0]} {t['first_hire'][1]}"),
             ('第一次因等待而聘人', t['first_wait_hire'] and f"Day {t['first_wait_hire'][0]} {t['first_wait_hire'][1]}（{t['first_wait_hire'][2][:60]}）"),
             ('第一次自然有 $50,000', t['m50']), ('三個條件同時成立', t['all3']), ('按下 簽約・開工', t['sign_press']), ('Madame Lin 最後一晚', t['last_night']),
             ('《簽約》', t['lin_sign']), ('The Lounge 開幕', t['opened']), ('開幕時餐廳等級', t['level_open']), ('開幕時員工', t['roles_open']),
             ('開幕時最貴的六道菜', '、'.join(f'{d} ${p}' for d, p in t['top_dishes'])), ('開幕前研發的酒', '、'.join(f'Day {d} {p}' for d, p in t['wines_dev']) or '—'),
             ('開幕時酒單支數', t['wines_n_open']), ('開幕當天／7 天後／14 天後收店現金', t['cash'] and ' / '.join(fmt(v) for v in t['cash'].values()))]
        for k, v in L:
            out.append(f'- {k}：{fmt(v) if not isinstance(v, (list, tuple, dict)) else v}')
        out.append('')
    out.append('## Lounge 開幕前 7 天 vs 開幕後 7 天／14 天（每天平均）\n')
    for (f, o), t in zip(data, T):
        if not t['opened']:
            continue
        od = t['opened']; rows = o['rows']
        a, b, c = room_week(rows, od - 7, od - 1), room_week(rows, od, od + 6), room_week(rows, od, od + 13)
        out.append(f"### seed {o['args']['seed']}（開幕 Day {od}）\n")
        out.append('| | 開幕前 7 天 | 開幕後 7 天 | 開幕後 14 天 |')
        out.append('|---|---:|---:|---:|')
        for k in a:
            if k == 'days':
                continue
            out.append(f'| {k} | {fmt(a[k])} | {fmt(b[k]) if b else "—"} | {fmt(c[k]) if c else "—"} |')
        out.append(f"\n（天數：{a['days']} / {b['days'] if b else 0} / {c['days'] if c else 0}）\n")
    return '\n'.join(out)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='+'); ap.add_argument('--md', default=None)
    A = ap.parse_args()
    md = report(A.files)
    print(md)
    if A.md:
        open(A.md, 'w', encoding='utf-8').write(md)
