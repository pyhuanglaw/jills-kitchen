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


# ---------------------------------------------------------------- the floor's carrying (the user's order of the work: one
# carry model first — Pass + the waiter's several plates — then the dirty dishes on the same model)

# a day with one waiter, the kitchen left alone (the plates are made ready by the test, as the kitchen would set them down)
def _floor_day(b, port, target, seed, lv, crew_extra=''):
    g = Game(b, port, target, seed=seed, manual=True, viewport={'width': 390, 'height': 844})
    _rt.install_bot(g)
    g.click('[data-act=open]'); g.page.wait_for_timeout(80)
    g.ev("S.level=2;S.tables=4;S.money=5000;S.crew=[{id:'w1',role:'waiter',name:'小茉',lv:%d,duty:'both',since:1,days:3,pool:'restaurant'}%s];save()" % (lv, crew_extra))
    start_day(g)
    g.ev("for(const q of R.groups)q.pat=1")
    return g


# two tickets at two tables, every plate made and set down on the pass in a row (no work left for the kitchen)
READY2 = """(()=>{for(let i=0;i<4000&&R.tickets.filter(t=>t.g&&t.g.table!=null&&t.g.state==='wait').length<2;i++){for(const q of R.groups)q.pat=1;__tick(1000/30)}
 const tks=R.tickets.filter(t=>t.g&&t.g.table!=null&&t.g.state==='wait').slice(0,2);if(tks.length<2)return 'null';
 for(const tk of tks){R.wf=(R.wf||[]).filter(n=>!n.its.some(o=>o.tk===tk));for(const it of tk.items){it.wf=null;it.st='ready';it.q='P';it.picked=false;it.pi=null}}
 let k=0;for(const tk of tks)for(const it of tk.items)it.pi=k++;R.tv++;
 return JSON.stringify(tks.map(t=>({id:t.id,table:t.g.table,n:t.items.length})))})()"""

# every plate put down at a table, by whom and with how many still in hand afterwards
SERVED = """window.__sv=[];{const s0=serveItems;serveItems=function(q,items){const w=R.cw&&R.cw.w1;const by=w&&items.length&&items.every(x=>(w.__h0||[]).includes(x.it))?'w1':'other';__sv.push({t:q.table,n:items.length,by,left:w&&w.hands?w.hands.filter(e=>!items.some(x=>x.it===e.it)).length:0,clock:+R.t.toFixed(2)});return s0.apply(this,arguments)}}
 {const p0=servePickup;servePickup=function(m,w,tk,dt){const r=p0.apply(this,arguments);w.__h0=(w.hands||[]).map(e=>e.it);if(tk.phase==='table'&&!tk.__seen){tk.__seen=1;(window.__trips||(window.__trips=[])).push({hand:(w.hands||[]).length,stops:(tk.stops||[]).map(T=>T.g.table)})}return r}}"""


@test
def workflow_a_waiter_has_two_hands_from_the_first_day(b, port, target):
    """「Waiter 不能被設計成一次只能拿一盤」: a LV2 waiter (the first level that serves) carries two plates at once — a table
    with two plates ready gets both in one trip, never two trips of one; a new waiter does not yet put two tables into one
    trip (WAITER_WAYS: tables 1), so two tables are two trips, each with that table's plates. carryCap is 2/2/3/4/4 for the
    five levels, never 1."""
    g = _floor_day(b, port, target, 9101, 2)
    caps = json.loads(g.ev("JSON.stringify([1,2,3,4,5].map(l=>carryCap({role:'waiter',lv:l})))"))
    check(caps == [2, 2, 3, 4, 4] and min(caps) >= 2, f'a waiter carries 2/2/3/4/4: {caps}')
    tks = json.loads(g.ev(READY2))
    check(tks and all(t['n'] >= 1 for t in tks), f'two tables with their plates on the pass: {tks}')
    g.ev(SERVED)
    for _ in range(60):
        g.ev("for(let i=0;i<15;i++){for(const q of R.groups)q.pat=1;__tick(1000/30)}")
        if all(g.ev("(()=>{const tk=R.tickets.find(t=>t.id===%d);return !tk||tk.items.every(i=>i.st==='served')})()" % t['id']) for t in tks):
            break
    trips = json.loads(g.ev("JSON.stringify(window.__trips||[])"))
    sv = json.loads(g.ev("JSON.stringify(__sv)"))
    check(trips and all(len(t['stops']) == 1 for t in trips), f'a new waiter: one table a trip: {trips}')
    two = [t for t in tks if t['n'] >= 2]
    for t in two:
        mine = [x for x in sv if x['t'] == t['table'] and x['by'] == 'w1']
        check(mine and mine[0]['n'] >= 2, f'T{t["table"]+1}: its plates came together in two hands, not one by one: {sv}')
    check(all(t['hand'] <= 2 for t in trips) and any(t['hand'] == 2 for t in trips) or not two, f'never more than two in hand at LV2, and two when two were there: {trips}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def workflow_a_seasoned_waiter_serves_two_tables_in_one_trip(b, port, target):
    """「Pass 拿 2–N 份 → 一趟送多桌」: a LV4 waiter (carries 4, up to three tables a trip, nearest first) with two tables'
    plates waiting takes them in one trip from the pass, puts each table's plates down at its table — they leave his hands
    there, the rest stay in them — and goes on to the next table without going back to the pass. The evening's numbers
    (R.st.wb) count the trip, its plates and that it served two tables."""
    g = _floor_day(b, port, target, 9102, 4)
    tks = json.loads(g.ev(READY2))
    check(tks, 'two tables with their plates on the pass')
    total = sum(min(t['n'], 4) for t in tks)
    g.ev(SERVED)
    for _ in range(60):
        g.ev("for(let i=0;i<15;i++){for(const q of R.groups)q.pat=1;__tick(1000/30)}")
        if all(g.ev("(()=>{const tk=R.tickets.find(t=>t.id===%d);return !tk||tk.items.every(i=>i.st==='served')})()" % t['id']) for t in tks):
            break
    trips = json.loads(g.ev("JSON.stringify(window.__trips||[])"))
    sv = [x for x in json.loads(g.ev("JSON.stringify(__sv)")) if x['by'] == 'w1']
    check(trips and len(trips[0]['stops']) == 2 and trips[0]['hand'] == min(4, total), f'one trip, both tables, {min(4, total)} plates in hand: {trips}')
    check(len(sv) >= 2 and sv[0]['t'] != sv[1]['t'] and sv[0]['left'] == trips[0]['hand'] - sv[0]['n'], f'the first table\'s plates left his hands there, the second table\'s stayed in them: {sv}')
    wb = json.loads(g.ev("JSON.stringify(R.st.wb||null)"))
    check(wb and wb['trips'] >= 1 and wb['multi'] >= 1 and wb['max'] == trips[0]['hand'], f'the evening counts it: {wb}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def workflow_the_pass_is_a_buffer_and_a_full_pass_is_a_quiet_wait(b, port, target):
    """「Pass 正式變成 Finished Food Buffer… 要有真正容量」, from the pass as it is drawn (「先依現在實際 Pass visual 與現有 upgrade
    決定」): its row holds 9 plates, 11 with the bigger pass. Full, a finished dish's plating cannot be started — not by Jill
    (the wok is not lit for it, a tap does nothing), not by a cook — and its card says 出菜口滿了; nothing burns, the
    quality stays, there is no countdown. When the floor takes plates away, the plating can start."""
    g = Game(b, port, target, seed=9103, manual=True, viewport={'width': 390, 'height': 844})
    g.click('[data-act=open]'); g.page.wait_for_timeout(80)
    g.ev("S.eq.stove=2"); start_day(g); g.ev("setRoom('kitchen')")
    check(g.ev("wfRowN()") == 9 and g.ev("(()=>{const r=S.rooms.pass;S.rooms.pass=1;const n=wfRowN();S.rooms.pass=r;return n})()") in (9, 11), 'the row')
    # a finished wok of fried rice waiting for 裝盤, and the pass filled with plates nobody has taken yet
    nid = g.ev("""(()=>{for(let i=0;i<3000&&!R.tickets.length;i++){for(const q of R.groups)q.pat=1;for(const t of R.tables){const q=t.group;if(q&&q.state==='order'&&!jillTargets(t.i))tapTable(t)}__tick(1000/30)}wfGather();const n=wfList()[0];if(!n)return null;
      const s=R.slots.find(x=>x.type==='stove');wfAssign(n,'jill',s);n.st='ready';n.si=0;n.slot=s;s.wf=n;n.who=null;n.to=null;wfJ().q=[];
      const tk=R.tickets[0];for(let k=0;k<wfRowN();k++){tk.items.push({d:'friedrice',st:'ready',q:'P',want:0,picked:false,set:null,pi:k})}R.tv++;return n.id})()""")
    check(nid, 'a wok of rice done, waiting to be plated')
    st = json.loads(g.ev("JSON.stringify({free:wfRowFree(),ok:wfRowOK(wfNode(%d)),line:wfState(wfNode(%d)),cue:wfCueSlots(wfNode(%d)).free.length,assign:wfAssign(wfNode(%d),'jill')})" % (nid, nid, nid, nid)))
    check(st['free'] <= 0 and not st['ok'] and not st['assign'] and st['cue'] == 0 and '出菜口滿了' in st['line'], f'the pass full: plating waits, the card says so: {st}')
    q0 = g.ev("JSON.stringify(wfNode(%d).its.map(o=>o.it.st))" % nid)
    g.ev("for(let i=0;i<300;i++){for(const q of R.groups)q.pat=1;__tick(1000/30)}")
    check(g.ev("wfNode(%d).st" % nid) == 'ready' and g.ev("JSON.stringify(wfNode(%d).its.map(o=>o.it.st))" % nid) == q0, 'ten seconds later it is still waiting, unchanged — nothing burns, nothing is lost')
    # the floor takes two plates: room for the rice
    g.ev("(()=>{const tk=R.tickets[0];let n=0;for(const it of tk.items){if(n<2&&it.st==='ready'&&it.pi!=null){it.st='served';it.pi=null;n++}}R.tv++})()")
    check(g.ev("wfRowOK(wfNode(%d))" % nid) and g.ev("wfAssign(wfNode(%d),'jill')" % nid), 'room on the pass: the plating starts')
    check(not g.errors, g.errors[:3]); g.close()

