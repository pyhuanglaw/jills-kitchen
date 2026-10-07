#!/usr/bin/env python3
"""The story-first waits (the user, 2026-10-07): from new_game_timeline.py runs made with
--probe tools/qa/probes/story_first_waits.json, each important story and space as a timeline, and every wait split
three ways:

  1. the story's own prerequisites hold -> its authored beat happens (days, and what the days in between had);
  2. a project is on offer -> the first evening the player has the money for it;
  3. the first evening with the money -> the evening the player buys it (and what the player said instead).

A probe is read at the summary of day D, so a beat that waits for it can come on D+1 at the earliest; the waits below
are counted from that morning. Usage: story_waits.py out300.json out301.json ... [--md report.md]"""
import sys, json, argparse
from collections import Counter

COSTS = {'lounge1': 50000, 'piano': 100000, 'up': 160000, 'lounge2': 80000, 'lounge3': 150000, 'pdr': 240000}


def first(rows, pred, start=None):
    for r in rows:
        if start is not None and r['day'] < start:
            continue
        try:
            if pred(r):
                return r['day']
        except (KeyError, TypeError):
            pass
    return None


def pr(r, k):
    return (r.get('probe') or {}).get(k)


def gap(a, b):
    return None if a is None or b is None else b - a


def between(rows, a, b, k):
    """how many evenings in [a, b) a probe was true (who came in, how many majors the day had)"""
    if a is None or b is None:
        return None
    return sum(1 for r in rows if a <= r['day'] < b and pr(r, k))


def why_waiting(log, d0, d1, words):
    """the player's own words (the decision log) on the evenings it had the money and did not buy"""
    c = Counter()
    if d0 is None:
        return []
    for e in log:
        if e.get('kind') != 'decide' or not (d0 <= e.get('day', 0) < (d1 if d1 is not None else 10 ** 6)):
            continue
        txt = (e.get('saw') or '') + ' ' + (e.get('why') or '')
        if any(w in txt for w in words):
            c[(e.get('why') or '').strip()[:60]] += 1
    return c.most_common(4)


def spent_on(log, d0, d1):
    """what the money went to instead (the player's purchases between two evenings)"""
    out = []
    if d0 is None:
        return out
    for e in log:
        if e.get('kind') == 'decide' and e.get('pressed') and d0 <= e.get('day', 0) < (d1 if d1 is not None else 10 ** 6):
            p = e['pressed']
            if any(w in p for w in ('開工', '擴建', '簽約', '購買', '升級', '加一張', '換', '聘請', '研發', '直接買')) and (e.get('cost') or 0) >= 5000:
                out.append((e['day'], p[:28], e.get('cost')))
    return out


def analyse(path):
    d = json.load(open(path, encoding='utf-8'))
    rows, log, F, NR = d['rows'], d['log'], d['final']['facts'], d['final'].get('newRooms') or {}
    crew = {n: s for n, role, s in d['final'].get('crew') or []}
    money = {r['day']: r['money'] for r in rows}
    last = rows[-1]['day'] if rows else None
    T, W = {}, []

    def ready(k, start=None):
        return first(rows, lambda r: pr(r, k) is True, start)

    def can_pay(cost, start):
        return None if start is None else first(rows, lambda r: r['money'] >= cost, start)

    # the Lounge's origin
    T['Ken 問酒（ken_wine_q）'] = F.get('ken_wine_q')
    t_ready = ready('tasting_ready'); T['試酒之夜'] = F.get('tasting_night')
    W.append(('試酒之夜', '故事條件成立 → 發生', t_ready, T['試酒之夜'], f"Ken 那幾天來了 {between(rows, t_ready, T['試酒之夜'], 'ken_today')} 晚"))
    r_ready = ready('retire_ready'); T['Madame Lin 退休（lin_retire）'] = F.get('lin_retiring')
    W.append(('Madame Lin 退休', '配菜的酒 7 天後 → 她來店裡那晚', r_ready, T['Madame Lin 退休（lin_retire）'],
              f"她那幾天來了 {between(rows, r_ready, T['Madame Lin 退休（lin_retire）'], 'lin_today')} 晚"))
    for k in ('ken_where', 'jd_want', 'dylan_book'):
        T[k] = F.get(k)
    T['《看看》'] = F.get('lin_viewing')
    W.append(('《看看》', 'Dylan 的設計書 → 隔天起', (F.get('dylan_book') or 0) + 0 if F.get('dylan_book') else None, T['《看看》'], ''))
    proj = F.get('lounge_project')
    pay1 = can_pay(COSTS['lounge1'], proj)
    paid1 = first(rows, lambda r: (r.get('proj') or {}).get('state') in ('signing', 'reno', 'built'))
    T['Lounge I 可以簽（project 出現）'] = proj; T['第一次付得起 $50,000'] = pay1; T['Lounge I 付錢簽約'] = paid1
    T['《簽約》'] = F.get('lin_signed'); T['Lounge 開幕'] = NR.get('lounge') or first(rows, lambda r: r['lounge'])
    W.append(('Lounge I', 'project 出現 → 第一次付得起', proj, pay1, ''))
    W.append(('Lounge I', '付得起 → 實際付', pay1, paid1, why_waiting(log, pay1, paid1, ('Lounge I',))))
    opened = T['Lounge 開幕']
    # 晴 × 阿拓
    T['沈晴 加入'] = crew.get('沈晴'); T['阿拓 加入'] = crew.get('阿拓')
    T['晴 × 阿拓 一起上班第一步（qt_1）'] = F.get('qt_1')
    s1 = ready('scene1_ready'); T['Scene 1《今天喝》'] = F.get('qt_drink')
    W.append(('Scene 1《今天喝》', '條件成立（開幕 10 天、Dylan 已揭曉）→ 發生', s1, T['Scene 1《今天喝》'], ''))
    for k, n in (('qt_late', 'Scene 2《晚點回去》'), ('qt_often', 'Scene 3《最近比較常》'), ('qt_ya', 'Scene 4《你喜歡予安》'), ('qt_said', 'Scene 5《講完》')):
        T[n] = F.get(k)
    # the piano and 予安
    payP = can_pay(COSTS['piano'], opened)
    T['第一次付得起鋼琴 $100,000'] = payP; T['鋼琴'] = NR.get('piano')
    W.append(('鋼琴', 'Lounge 開幕（可以買）→ 第一次付得起', opened, payP, ''))
    W.append(('鋼琴', '付得起 → 實際買', payP, T['鋼琴'], why_waiting(log, payP, T['鋼琴'], ('鋼琴',))))
    y1 = ready('ya1_ready'); T['予安第一次（ya_1）'] = F.get('ya_1')
    W.append(('予安第一次', '鋼琴 3 天後 → 她坐進 Lounge', y1, T['予安第一次（ya_1）'], f"她那幾天來了 {between(rows, y1, T['予安第一次（ya_1）'], 'ya_today')} 晚"))
    T['ya_2'] = F.get('ya_2'); T['ya_3'] = F.get('ya_3')
    tr = ready('trial_ready'); T['予安試彈'] = F.get('ya_trial')
    W.append(('予安試彈', '條件成立 → 發生', tr, T['予安試彈'], ''))
    T['予安加入'] = F.get('ya_join')
    # the floor upstairs
    era = first(rows, lambda r: pr(r, 'up_era') and pr(r, 'up_can'))
    T['二樓故事可以開始'] = era; T['二樓故事開始（up_hint）'] = F.get('up_hint')
    W.append(('二樓故事開始', '條件成立（Lounge 開 2 天、側廳、5 人）→ 第一段', era, T['二樓故事開始（up_hint）'], ''))
    sr = ready('sr_ready'); T['《大家待的地方》'] = F.get('sr_story')
    W.append(('《大家待的地方》', '條件成立 → 發生', sr, T['《大家待的地方》'], ''))
    ak = ready('ask_ready'); T['打給房東（整層。）'] = F.get('up_ask')
    W.append(('打給房東', '條件成立 → 打電話', ak, T['打給房東（整層。）'], ''))
    payU = can_pay(COSTS['up'], T['打給房東（整層。）'])
    T['第一次付得起二樓 $160,000'] = payU; T['二樓＋休息室 I'] = F.get('up_lease') or NR.get('up')
    W.append(('二樓初期工程', 'project 出現 → 第一次付得起', T['打給房東（整層。）'], payU, ''))
    W.append(('二樓初期工程', '付得起 → 實際開工', payU, T['二樓＋休息室 I'], why_waiting(log, payU, T['二樓＋休息室 I'], ('二樓',))))
    # the Lounge's rooms, the Private Dining Room
    pay2 = can_pay(COSTS['lounge2'], opened)
    T['第一次付得起 Lounge II $80,000'] = pay2; T['Lounge II'] = NR.get('lounge2')
    W.append(('Lounge II', '付得起 → 實際買', pay2, T['Lounge II'], why_waiting(log, pay2, T['Lounge II'], ('Lounge II',))))
    pay3 = can_pay(COSTS['lounge3'], T['Lounge II'])
    T['第一次付得起 Lounge III $150,000'] = pay3; T['Lounge III'] = NR.get('lounge3')
    W.append(('Lounge III', '付得起 → 實際買', pay3, T['Lounge III'], why_waiting(log, pay3, T['Lounge III'], ('Lounge III',))))
    T['包廂 era'] = first(rows, lambda r: pr(r, 'pd_era'))
    for k in ('pd_yj', 'pd_other', 'pd_story'):
        T[k] = F.get(k)
    T['包廂蓋好'] = NR.get('pdr') or NR.get('pd')
    T['模擬最後一天'] = last
    # the story budget: on how many of the waiting days two major beats had already happened (the day's cap)
    W = [w + (None if w[2] is None or w[3] is None else sum(1 for r in rows if w[2] < r['day'] < w[3] and (pr(r, 'majors') or 0) >= 2),) for w in W]
    return {'seed': d['args']['seed'], 'T': T, 'W': W, 'money': money, 'rows': rows, 'log': log,
            'spent_lounge': spent_on(log, pay1, paid1), 'spent_piano': spent_on(log, payP, T['鋼琴']), 'spent_up': spent_on(log, payU, T['二樓＋休息室 I'])}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('files', nargs='+'); ap.add_argument('--md', default=None)
    A = ap.parse_args()
    R = [analyse(f) for f in A.files]
    out = []
    keys = list(R[0]['T'].keys())
    out.append('| | ' + ' | '.join(f"seed {r['seed']}" for r in R) + ' |')
    out.append('|---|' + '---|' * len(R))
    for k in keys:
        out.append(f'| {k} | ' + ' | '.join(str(r['T'].get(k) if r['T'].get(k) is not None else '—') for r in R) + ' |')
    out.append('')
    for r in R:
        out.append(f"### seed {r['seed']}：等待")
        for name, kind, a, b, note, *_ in r['W']:
            g = gap(a, b)
            full = _[0] if _ else None
            out.append(f"- {name}｜{kind}：{a} → {b}（{'—' if g is None else str(g) + ' 天'}）{('｜' + str(note)) if note else ''}{('｜那幾天已經滿兩個 major：' + str(full) + ' 天') if full else ''}")
        for lab, sp in (('Lounge I', r['spent_lounge']), ('鋼琴', r['spent_piano']), ('二樓', r['spent_up'])):
            if sp:
                out.append(f"- 付得起 {lab} 到真的買之間，錢花在：" + '；'.join(f"Day {d} {p} ${c:,}" for d, p, c in sp[:8]))
        out.append('')
    txt = '\n'.join(out)
    print(txt)
    if A.md:
        open(A.md, 'w', encoding='utf-8').write(txt + '\n')


if __name__ == '__main__':
    main()
