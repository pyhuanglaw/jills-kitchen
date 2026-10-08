"""The restaurant around the kitchen (the user, 2026-10-08, docs/v24/restaurant_workflow_b_2026-10-08.txt): wages, and —
as they are built — the dirty dishes and the washing, the pass as the finished food's buffer, the floor's carrying.
`python3 tests/run_tests.py -k workflow` runs them.
"""
import json, sys
_rt = sys.modules['__main__'] if hasattr(sys.modules.get('__main__'), 'TESTS') else __import__('run_tests')
test, check, Game, start_day = _rt.test, _rt.check, _rt.Game, _rt.start_day

# the wage curve as it was on the morning of 2026-10-08 (rc7.2's), before the user's ×0.8
WAGES_BEFORE = {'chef': [304, 532, 832, 1224, 1690], 'waiter': [253, 443, 693, 1020, 1408], 'cleaner': [190, 332, 520, 765, 1056], 'bartender': [405, 709, 1109, 1632, 2253]}


@test
def workflow_wages_are_four_fifths_of_what_they_were(b, port, target):
    """The user's Part 2: every existing wage — each role, each level — is the morning's wage × 0.8, rounded to the dollar;
    the day's wage bill, the summary's 薪 and the money that leaves the till at closing are the same number."""
    g = Game(b, port, target, seed=8801, manual=True)
    _rt.install_bot(g)
    g.click('[data-act=open]'); g.page.wait_for_timeout(80)
    now = json.loads(g.ev("JSON.stringify(Object.fromEntries(['chef','waiter','cleaner','bartender'].map(r=>[r,[1,2,3,4,5].map(l=>crewWageAt(r,l))])))"))
    exp = {r: [round(w * 0.8 + 1e-9) for w in ws] for r, ws in WAGES_BEFORE.items()}
    check(now == exp, f'wages × 0.8: {now} vs {exp}')
    g.ev("S.crew=[{id:'w1',role:'waiter',name:'小茉',lv:2,duty:'both',since:1,days:3,pool:'restaurant'},{id:'c1',role:'cleaner',name:'秀琴阿姨',lv:1,duty:'clean',since:1,days:3,pool:'restaurant'},{id:'k1',role:'chef',name:'阿德師傅',lv:3,duty:'stove',since:1,days:3,pool:'restaurant'}];S.money=5000;save()")
    bill = g.ev("crewWages()")
    check(bill == exp['waiter'][1] + exp['cleaner'][0] + exp['chef'][2], f'the day\'s wage bill: {bill}')
    start_day(g)
    _rt.play_day(g, max_steps=600)
    g.page.click('#hPause'); g.click('[data-act=closeNow]')
    _rt.play_day(g, max_steps=3000)
    s = json.loads(g.ev("JSON.stringify(S.lastSummary||null)"))
    check(s and s['wages'] == bill, f'the summary pays the same wages: {s and s.get("wages")} vs {bill}')
    check(not g.errors, g.errors[:3]); g.close()
