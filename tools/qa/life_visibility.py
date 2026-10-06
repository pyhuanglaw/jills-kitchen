"""Deep-audit tool (2026-10-06): the life that exists but where — and how often a normal player would see it.
The user asks it as 「為什麼我從來沒看到這個」; the audit's question is 「正常玩家大概多久會注意到一次？」. This measures
the first half (where and how often each piece of life happens) and models the second; whether something SHOULD be more
visible is the user's decision, never this tool's.

A save played N evenings by a daily player (tests/player.py: real taps, the crew work, panels read). Every second of game
time it reads (only reads) where the life is: Jill resting in her room, people in the Staff Room, cats upstairs or in
Jill's room, Dylan at his desk or at a table (which room), 予安 at the piano. Then it models a player who watches the main
dining room and looks at one other tab, chosen at random, once or twice an evening for 10 seconds:
  seen-per-evening ≈ (1 − share of the evening it is in the main room) × P(a glance hits it) + its share in the main room.

  python3 tools/qa/life_visibility.py SAVE EVENINGS [--seed 1] [--json out.json]
"""
import sys, os, json, argparse, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'tests'))
import run_tests as rt
from player import Player
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser(); ap.add_argument('save'); ap.add_argument('evenings', type=int); ap.add_argument('--seed', type=int, default=1); ap.add_argument('--json')
A = ap.parse_args()

SAMPLE = r"""JSON.stringify((()=>{const T=(f,d)=>{try{return f()}catch(e){return d}};const o={};
  o.jill_resting_in_her_room=T(()=>!!(R.jill.rest&&(R.jill.room||'main')==='home'),false);
  o.staff_room_people=T(()=>srPeople().length,0);
  o.cats_upstairs=T(()=>CATS.filter(c=>c.away==='up').length,0);
  o.cats_in_jills_room=T(()=>CATS.filter(c=>c.away==='home').length,0);
  o.cats_in_main=T(()=>CATS.filter(c=>!c.hidden&&!c.away).length,0);
  o.dylan_room=T(()=>{const g=R.groups.find(g=>g.reg==='dylan'&&!g.gone);if(g)return g.room||'main';const D=LIFE.dylan;return D?(D.room||'main'):'home'},null);
  o.piano=T(()=>!!(R.ya&&R.ya.playing),false);
  o.tabs=T(()=>[...document.querySelectorAll('#roomTabs [data-room]')].map(e=>e.dataset.room),[]);
  return o})())"""

FEATURES = {   # what, which tab it is on, when it counts as "there"
    'Jill 營業中在房間休息': ('home', lambda s: s['jill_resting_in_her_room']),
    '休息室有人': ('staff', lambda s: s['staff_room_people'] > 0),
    '貓在二樓': ('up', lambda s: s['cats_upstairs'] > 0),
    '貓在 Jill 的房間': ('home', lambda s: s['cats_in_jills_room'] > 0),
    'Dylan 在主廳吃飯': ('main', lambda s: s['dylan_room'] == 'main'),
    'Dylan 在書桌前': ('home', lambda s: s['dylan_room'] == 'home'),
    '予安在彈琴': ('lounge', lambda s: s['piano']),
}


def main():
    per_evening = []
    with sync_playwright() as pw:
        srv, port = rt.start_server(); b = pw.chromium.launch()
        p = Player(b, port, 'index', save=A.save, seed=A.seed, checkpoint=False)
        try:
            p.tap('#screen [data-act=open]'); p.settle()
            for _ in range(A.evenings):
                if p.state()['phase'] == 'summary':
                    p.tap('#screen [data-act=toShop]')
                if p.state()['phase'] == 'shop':
                    p.tap('#screen [data-act=nextDay]'); p.settle()
                day = p.state()['day']
                p.restock(); p.start_day()
                rt.install_bot(p.g); p.ev(rt.LAZY_ACTOR); p.ev("window.__act=window.__actLazy")
                samples = []
                while p.ev("phase") == 'service':
                    p.settle()
                    p.ev("for(let i=0;i<30;i++){__act();__tick(1000/30)}")
                    samples.append(json.loads(p.ev(SAMPLE)))
                tabs = max((s['tabs'] for s in samples), key=len, default=['main'])
                row = {'day': day, 'seconds': len(samples), 'tabs': tabs}
                for name, (tab, there) in FEATURES.items():
                    share = sum(1 for s in samples if there(s)) / max(1, len(samples))
                    row[name] = round(share, 3)
                per_evening.append(row)
                print(f"Day {day}: {len(samples)} s, tabs {tabs} — " + ', '.join(f"{k} {row[k]:.0%}" for k in FEATURES), flush=True)
            print('page errors:', p.errors[:3])
        finally:
            p.close(); b.close(); srv.shutdown()
    print('\nA player who watches the main room and glances at one other tab (at random) for 10 s, 1–2 times an evening:')
    for name, (tab, _) in FEATURES.items():
        share = sum(r[name] for r in per_evening) / max(1, len(per_evening))
        evenings_with = sum(1 for r in per_evening if r[name] > 0)
        if tab == 'main':
            p_see = min(1.0, share * 3) if share else 0.0
        else:
            n_tabs = max(1, len(per_evening[-1]['tabs']) - 1)
            p_glance = 1 - (1 - 1 / n_tabs) ** 1.5      # 1–2 glances, one tab each
            p_see = p_glance * share
        every = f'every ~{1 / p_see:.0f} evenings' if p_see > 0 else 'practically never'
        print(f"  {name:<14} on 「{tab}」: there {share:.0%} of the service, on {evenings_with}/{len(per_evening)} evenings → seen {every}")
    if A.json:
        json.dump(per_evening, open(A.json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
