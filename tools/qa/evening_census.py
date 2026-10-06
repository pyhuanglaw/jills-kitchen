"""Deep-audit tool (2026-10-06): everything that pops up over a player's evenings, counted — for the narrative audit's
numbers (the user, 2026-10-04: 「跳出的對話有些太重複沒有意義 又太頻繁」). It counts; it does not judge: whether a line
sounds like a person is for the reader (docs/audit/PLAYBOOK.md, the narrative workstream).

A save played forward N days the way a daily player does (tests/player.py: real taps for 準備、補貨、開店, the crew work, the
story panels ON and read through). Writes a transcript (clock · kind · text) and prints per evening: popups by kind
(toast / a line with a face / story panel / banner), the speaker categories, and the most repeated lines of the run.

  python3 tools/qa/evening_census.py SAVE DAYS OUT_DIR [--seed 1]
  python3 tools/qa/evening_census.py player_day92_2105.json 3 /tmp/census
"""
import sys, os, json, re, argparse, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'tests'))
import run_tests as rt
from player import Player
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser(); ap.add_argument('save'); ap.add_argument('days', type=int); ap.add_argument('out'); ap.add_argument('--seed', type=int, default=1)
A = ap.parse_args()
os.makedirs(A.out, exist_ok=True)
SYSTEM = re.compile(r'賣完了|只剩 \d+ 份|打烊|RUSH|ON FIRE|OPEN FOR|成就|檢查|奧客|故障|小偷|VIP 貴賓|熟練度|門口有人|走進來了|想點的都賣完了')


def category(k, t):
    if k.startswith('banner') or (k.startswith('toast') and not k.startswith('toast:q') and SYSTEM.search(t)):
        return 'system'
    if k.startswith('panel'):
        return 'story panel'
    if k.startswith('face:named'):
        return 'named guest'
    if k.startswith('face:staff'):
        return 'staff'
    if k.startswith('face:'):
        return 'face (Jill / Dylan / a regular)'
    if k.startswith('toast:q'):
        return 'a guest\'s line'
    return 'other toast'


def main():
    rows = []
    with sync_playwright() as pw:
        srv, port = rt.start_server(); b = pw.chromium.launch()
        p = Player(b, port, 'index', save=A.save, seed=A.seed, checkpoint=False)
        try:
            p.tap('#screen [data-act=open]'); p.settle()
            p.capture_on()
            for _ in range(A.days):
                if p.state()['phase'] == 'shop':
                    p.tap('#screen [data-act=nextDay]'); p.settle()
                if p.state()['phase'] == 'summary':
                    p.tap('#screen [data-act=toShop]'); p.tap('#screen [data-act=nextDay]'); p.settle()
                day = p.state()['day']
                p.restock(); p.start_day(); p.play_evening()
                ev = [x for x in p.captured() if x['d'] == day]
                rows.extend(ev)
                kinds = collections.Counter(x['k'].split(':')[0] + (':held' if x['k'] == 'panel:held' else '') for x in ev)
                cats = collections.Counter(category(x['k'], x['t']) for x in ev)
                print(f'Day {day}: {len(ev)} popups — ' + ', '.join(f'{k} {n}' for k, n in kinds.most_common()) + ' | ' + ', '.join(f'{k} {n}' for k, n in cats.most_common()), flush=True)
                if p.state()['phase'] == 'summary':
                    p.tap('#screen [data-act=toShop]')
            print('page errors:', p.errors[:3])
        finally:
            p.close(); b.close(); srv.shutdown()
    with open(os.path.join(A.out, 'transcript.txt'), 'w', encoding='utf-8') as f:
        for x in rows:
            f.write(f"D{x['d']} {x['c']}  {x['k']:<22} {x['t']}\n")
    rep = collections.Counter(re.sub(r'\d+', '#', x['t']) for x in rows)
    print('\nthe most repeated (numbers as #):')
    for t, n in rep.most_common(15):
        print(f'  ×{n}  {t[:70]}')
    json.dump(rows, open(os.path.join(A.out, 'popups.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)


if __name__ == '__main__':
    main()
