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
    # (round 2, 2026-10-10: 秀琴阿姨 is on every game's staff from Day 1 — the service adds her if a crew lacks her. These tests
    #  set the crew they are about, so she has the evening off: the crew stays the one each test sets.)
    g.ev("S.level=2;S.tables=4;S.money=5000;S.crew=[{id:'w1',role:'waiter',name:'小茉',lv:%d,duty:'both',since:1,days:3,pool:'restaurant'}%s];xqCrewMig(S);setCrewAway(xiuqin(),'off');save()" % (lv, crew_extra))
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
      const s=R.slots.find(x=>x.type==='stove');wfAssign(n,'jill',s);n.st='ready';n.si=0;n.slot=s;s.wf=n;n.who=null;n.to=null;wfJ().wq=[];
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



# ---------------------------------------------------------------- the dirty dishes, on the same hands (the user's Part 1)

# a day with a cleaner (LV1) and nothing else of the floor's: guests kept patient, the kitchen left to the test
def _dirty_day(b, port, target, seed, crew="{id:'c1',role:'cleaner',name:'阿芳',lv:1,duty:'clean',since:1,days:3,pool:'restaurant'}"):
    g = Game(b, port, target, seed=seed, manual=True, viewport={'width': 390, 'height': 844})
    _rt.install_bot(g)
    g.click('[data-act=open]'); g.page.wait_for_timeout(80)
    g.ev("S.level=2;S.tables=4;S.money=5000;S.crew=[%s];xqCrewMig(S);setCrewAway(xiuqin(),'off');save();window.__noXQH=1" % crew)   # (round 2: her evening off, as in _floor_day)
    start_day(g)
    g.ev("R.sched=[];R.si=0")   # nobody new comes in: the test sets the tables
    return g


# a table left with plates on it (the guests gone): n of them
DIRTY = "((i,n,d)=>{const t=R.tables[i];t.group=null;t.dirty=true;t.plates=[];for(let k=0;k<n;k++)t.plates.push({d:d||(k%3===2?'coffee':'friedrice'),q:'P',want:0});R.tv++;return t.i})"
TICK = "(n=>{for(let i=0;i<n;i++){for(const q of R.groups)q.pat=1;__tick(1000/30)}})"


@test
def workflow_dirty_dishes_go_back_by_hand_to_the_tub(b, port, target):
    """Part 1 (一、六、七、八、acceptance 1–5, 8–11): a table left with three plates is cleared by the cleaner — the plates leave
    the table into her hands (a stack, not nothing), she walks through the kitchen door to the cart in front of the sink and
    puts them in: 髒餐具 3/10. Tapping the cart sends someone to wash: she walks to the sink, takes two, washes them one by
    one; the count goes 3 → 2 → 1 → 0, one at a time, never all at once."""
    g = _dirty_day(b, port, target, 9201)
    ti = g.ev(DIRTY + "(0,3)")
    seen = {'hands': 0, 'kitchen': False, 'count': []}
    for _ in range(300):
        g.ev(TICK + "(3)")
        st = json.loads(g.ev("JSON.stringify({h:handsN(R.cw.c1||{},'dirty'),room:R.cw.c1&&R.cw.c1.room,n:ddCount(),dirty:R.tables[%d].dirty,left:R.tables[%d].plates.length})" % (ti, ti)))
        seen['hands'] = max(seen['hands'], st['h'])
        if st['h'] and st['room'] == 'kitchen': seen['kitchen'] = True
        if st['n'] == 3 and not st['h']: break
    check(seen['hands'] == 3 and seen['kitchen'], f'the three plates in her hands, carried into the kitchen: {seen}')
    check(g.ev("ddCount()") == 3 and g.ev("ddS().n.length") == 3 and not g.ev("R.tables[%d].dirty" % ti), 'in the tub: 3/10, the table clear')
    check(json.loads(g.ev("JSON.stringify(ddS().n.slice().sort())")) == sorted(['plate', 'plate', 'cup']), 'a cup and two plates, as they were served')
    # washing: the player taps the cart
    g.ev("setRoom('kitchen')")
    C = json.loads(g.ev("JSON.stringify(ddCart())"))
    o = json.loads(g.ev("JSON.stringify((()=>{const r=sc.getBoundingClientRect();return{x:r.left+SV.ox+%f*SV.s,y:r.top+SV.oy+%f*SV.s}})())" % (C['x'], C['y'] - 16)))
    g.page.mouse.click(o['x'], o['y']); g.page.wait_for_timeout(40)
    check(g.ev("ddWasher()") == 'c1', 'the cart tapped: the cleaner is sent to wash')
    counts, at_sink = [], False
    for _ in range(400):
        g.ev(TICK + "(2)")
        n = g.ev("ddCount()"); at_sink = at_sink or g.ev("ddWasherAt()")
        if not counts or counts[-1] != n: counts.append(n)
        if n == 0: break
    check(at_sink and counts == [3, 2, 1, 0], f'at the sink, one at a time: {counts}')
    check(g.ev("(R.st.dd||{}).wash") == 3 and g.ev("(R.st.dd||{}).in") == 3, 'the evening counts three in, three washed')
    check(not g.errors, g.errors[:3]); g.close()


@test
def workflow_a_full_tub_holds_the_table_and_never_the_plating(b, port, target):
    """「10/10 後不能再完成新收桌」 and 「不會因此阻止 Cooking PLATING」 (acceptance 6, 7, 13): with the tub full, a table left with
    plates stays dirty — nobody takes its plates (they never vanish), Jill sent to it comes back without, it cannot be
    seated — while a finished dish can still be plated (no clean-plate count). Washed down to 9, the table is cleared."""
    g = _dirty_day(b, port, target, 9202)
    g.ev("ddS().n=Array(10).fill('plate');ddS().wash={who:'x',ph:'take',t:0,spot:0};ddS().wash2={who:'y',ph:'take',t:0,spot:1};R.tv++")   # full, and the sink taken (nobody can make room yet)
    # (2026-10-09: the sink has two places now — a second cleaner washes beside the first — so both are taken; with only the
    #  first taken, the cleaner here washes beside it and takes two of the ten, which is the new rule, not this test's question)
    ti = g.ev(DIRTY + "(1,2)")
    g.ev(TICK + "(240)")
    st = json.loads(g.ev("JSON.stringify({dirty:R.tables[%d].dirty,left:R.tables[%d].plates.length,n:ddCount(),hands:handsN(R.cw.c1||{},'dirty'),free:ddFree()})" % (ti, ti)))
    check(st['dirty'] and st['left'] == 2 and st['n'] == 10 and st['hands'] == 0, f'eight seconds later: the table still has its two plates, nobody holds any: {st}')
    g.ev("tapTable(R.tables[%d])" % ti)
    check(not g.ev("jillTargets(%d)" % ti), 'Jill is not sent to a table whose dishes have nowhere to go (the toast says the tub is full)')
    check(g.ev("freeTableFor({size:1,state:'queue'})!==R.tables[%d]" % ti), 'it cannot be seated')
    # the plating does not wait for plates: a wok of rice done, plated
    nid = g.ev("""(()=>{const tk={id:999,g:null,items:[{d:'friedrice',st:'cooking',q:null,want:0,picked:false,set:null}],no:1};const n=wfNew('friedrice');n.its.push({tk,it:tk.items[0]});n.n=1;tk.items[0].wf=n.id;wfList().push(n);
      const s=R.slots.find(x=>x.type==='stove');n.st='ready';n.si=0;n.slot=s;s.wf=n;return n.id})()""")
    check(g.ev("wfAssign(wfNode(%d),'jill')" % nid) and g.ev("wfNode(%d).st" % nid) == 'dish', 'a full tub: the plating still starts, plates from the rack')
    g.ev("wfList().splice(wfList().indexOf(wfNode(%d)),1);R.slots.forEach(s=>{if(s.wf&&s.wf.id===%d)s.wf=null})" % (nid, nid))
    # the sink free again: the cleaner washes (the stack is high) and clears the table when there is room
    g.ev("ddS().wash=null;ddS().wash2=null;R.tv++")
    for _ in range(600):
        g.ev(TICK + "(3)")
        if not g.ev("R.tables[%d].dirty" % ti): break
    check(not g.ev("R.tables[%d].dirty" % ti), 'room in the tub: the table is cleared')
    check(not g.errors, g.errors[:3]); g.close()


@test
def workflow_washing_can_stop_halfway_and_the_rest_waits(b, port, target):
    """「洗滌可以中斷… 剩下 6/10 就留在 Dirty Dish Area。之後其他人可以繼續洗。不要重置」 (acceptance 12): washing six, the one
    at the sink is called away after the ones in hand; what is left stays in the tub, counted; the next one to wash goes on
    from there."""
    g = _dirty_day(b, port, target, 9203)
    g.ev("ddS().n=['plate','plate','cup','plate','bowl','glass'];R.tv++;ddTap()")
    for _ in range(600):
        g.ev(TICK + "(2)")
        if g.ev("ddCount()") <= 4: break
    g.ev("ddWashers().forEach(W=>W.stop=1)")   # (2026-10-09: everyone at the sink — the cleaner may be washing beside the one tapped)
    for _ in range(300):
        g.ev(TICK + "(2)")
        if not g.ev("ddWasher()"): break
    left = g.ev("ddCount()")
    check(not g.ev("ddWasher()") and 1 <= left <= 4 and g.ev("ddS().n.length") == left, f'called away: the rest stays in the tub, counted: {left}')
    g.ev(TICK + "(150)")
    check(g.ev("ddCount()") == left, 'and it is still there five seconds later (nothing reset, nothing washed by itself)')
    g.ev("ddTap()")
    for _ in range(600):
        g.ev(TICK + "(2)")
        if g.ev("ddCount()") == 0: break
    check(g.ev("ddCount()") == 0 and g.ev("(R.st.dd||{}).wash") == 6, 'the next washing goes on from there: all six')
    check(not g.errors, g.errors[:3]); g.close()


@test
def workflow_waiters_keep_serving_and_one_at_most_washes(b, port, target):
    """「不要讓 waiter 在有大量菜等著送時，所有人一起跑去洗碗」 (acceptance 14): two waiters and no cleaner, the tub at 9 of 10 and
    plates waiting on the pass — neither goes to wash while there are plates for the guests; with nothing for the guests
    one (never two) washes; Jill and the cooks never wash by themselves."""
    g = _floor_day(b, port, target, 9204, 4, ",{id:'w2',role:'waiter',name:'阿哲',lv:3,duty:'both',since:1,days:3,pool:'restaurant'},{id:'k1',role:'chef',name:'阿德師傅',lv:3,duty:'stove',since:1,days:3,pool:'restaurant'}")
    tks = json.loads(g.ev(READY2))
    check(tks, 'plates on the pass for two tables')
    g.ev("ddS().n=Array(9).fill('plate');R.tv++")
    washed_while_plates = []
    for _ in range(200):
        g.ev("for(const q of R.groups)q.pat=1;__tick(1000/30)")
        w = g.ev("ddWasher()")
        plates = g.ev("R.tickets.some(t=>!t.claim&&t.items.some(i=>i.st==='ready'&&!i.picked))")   # plates nobody is coming for
        if w and plates: washed_while_plates.append(w)
    check(not washed_while_plates, f'no waiter at the sink while plates wait with nobody coming for them: {washed_while_plates[:3]}')
    # nothing for the guests now: one of them washes, the other does not
    g.ev("R.sched=[];R.si=0;for(const q of R.groups.slice())leaveGroup(q,'ok');for(const t of R.tables){t.dirty=false;t.plates=[]}")
    whos = set()
    for _ in range(600):
        g.ev("__tick(1000/30)")
        w = g.ev("ddWasher()")
        if w: whos.add(w)
        n_wash = g.ev("Object.values(R.cw).filter(w=>w.task&&w.task.k==='wash').length")
        check(n_wash <= 1, 'never two at the sink')
        if g.ev("ddCount()") < 8: break
    check(whos and whos <= {'w1', 'w2'}, f'a waiter washes when nothing is waiting for the guests: {whos}')
    check(g.ev("ddWasher()") != 'jill' and not g.ev("(R.jill.hands||[]).some(e=>e.k==='dirty'&&e.w)"), 'Jill never by herself')   # (2026-10-09: the one Jill — what she washes is in R.jill's hands, marked w)
    check(not g.errors, g.errors[:3]); g.close()


@test
def workflow_a_second_cleaner_washes_beside_the_first(b, port, target):
    """The release gate (2026-10-09, 四-1／四-3: a bottleneck a hire or an upgrade can relieve) and the user's #5 (「重要的是玩家
    能透過聘人及設備投資解除瓶頸」): with two cleaners, the stack high and no table to clear, the second washes beside the first —
    each at a place of their own at the sink (behind the counter, the second on the sink's right); a tap on the cart says who
    is washing; saved and read back with two at the sink, both go on and every dish is washed once; a waiter is never the
    second one at the sink; with one at the sink, a tap on the cart sends Jill (no cleaner free) to the other place."""
    C2 = ("{id:'c1',role:'cleaner',name:'阿芳',lv:3,duty:'clean',since:1,days:3,pool:'restaurant'},"
          "{id:'c2',role:'cleaner',name:'小彤',lv:3,duty:'clean',since:1,days:3,pool:'restaurant'}")
    g = _dirty_day(b, port, target, 9331, C2)
    g.ev("ddS().n=Array(9).fill('plate');R.tv++")
    two = None
    for _ in range(400):
        g.ev(TICK + "(2)")
        o = json.loads(g.ev("JSON.stringify({W:ddWashers().map(W=>({who:W.who,spot:W.spot,at:ddWasherAt(W)})),n:ddCount()})"))
        if len(o['W']) == 2 and all(w['at'] for w in o['W']): two = o; break
    check(two and {w['who'] for w in two['W']} == {'c1', 'c2'} and {w['spot'] for w in two['W']} == {0, 1}, f'two cleaners, the stack high: both wash, each at a place of their own: {two}')
    pos = json.loads(g.ev("JSON.stringify([ddSink(),ddSink2(),R.cw.c1&&{x:R.cw.c1.x,y:R.cw.c1.y},R.cw.c2&&{x:R.cw.c2.x,y:R.cw.c2.y}])"))
    check(pos[0]['y'] == pos[1]['y'] and pos[1]['x'] > pos[0]['x'] + 10, f'the second place is beside the first, on its right, behind the counter: {pos}')
    g.ev("toast=(m=>{window.__toast=m})");g.ev("ddTap()")
    lab = g.ev("window.__toast||''")
    check('阿芳' in lab and '小彤' in lab, f'a tap on the cart says who is washing — both: {lab}')
    # saved and read back with two at the sink: both go on, and every dish is washed once
    before = json.loads(g.ev("JSON.stringify({n:ddCount(),W:ddWashers().map(W=>W.who+':'+W.spot).sort()})"))
    check(g.ev("checkpointSave('manual')"), 'the checkpoint is written')
    g.reload(); _rt.install_bot(g)
    g.click('[data-act=open]')
    after = json.loads(g.ev("JSON.stringify({n:ddCount(),W:ddWashers().map(W=>W.who+':'+W.spot).sort()})"))
    check(after == before, f'read back: the same count, the same two at their places: {before} / {after}')
    for _ in range(900):
        g.ev(TICK + "(2)")
        if g.ev("ddCount()") == 0: break
    check(g.ev("ddCount()") == 0 and g.ev("(R.st.dd||{}).wash") == 9, f'all nine washed, each once: {g.ev("JSON.stringify(R.st.dd)")}')
    check(not g.errors, g.errors[:3]); g.close()
    # one cleaner and a waiter: the waiter never joins the one at the sink (a cleaner may join a waiter who is washing)
    g = _dirty_day(b, port, target, 9332, "{id:'c1',role:'cleaner',name:'阿芳',lv:3,duty:'clean',since:1,days:3,pool:'restaurant'},{id:'w1',role:'waiter',name:'小茉',lv:3,duty:'both',since:1,days:3,pool:'restaurant'}")
    g.ev("ddS().n=Array(9).fill('plate');R.tv++")
    seconds = set()
    for _ in range(600):
        g.ev(TICK + "(2)")
        w2 = g.ev("ddS().wash2&&ddS().wash2.who")
        if w2: seconds.add(w2)
        if g.ev("ddCount()") == 0: break
    check('w1' not in seconds and g.ev("ddCount()") == 0, f'one cleaner and a waiter: the waiter is never the second at the sink, and the stack is washed: {seconds}')
    check(not g.errors, g.errors[:3]); g.close()
    # one cleaner washing, the player taps the cart: Jill goes to the other place and washes too; asked for a table, she
    # finishes the plate in hand and goes, the cleaner washing on
    g = _dirty_day(b, port, target, 9333)
    g.ev("ddS().n=Array(10).fill('plate');R.tv++")
    for _ in range(300):
        g.ev(TICK + "(2)")
        if g.ev("ddWasher()==='c1'"): break
    g.ev("toast=(m=>{window.__toast=m})"); g.ev("ddTap()")
    check(g.ev("ddS().wash2&&ddS().wash2.who") == 'jill' and 'Jill' in g.ev("window.__toast||''"), f'a tap with one at the sink sends Jill to the other place: {g.ev("JSON.stringify(ddWashers())")} {g.ev("window.__toast")}')
    at = False
    for _ in range(300):
        g.ev(TICK + "(2)")
        if g.ev("!!ddWashOf('jill')&&ddWasherAt(ddWashOf('jill'))&&(R.jill.hands||[]).some(e=>e.k==='dirty'&&e.w)"): at = True; break
    check(at, 'Jill at the second place with a plate to wash')
    g.ev("ddTap()")
    check('阿芳' in g.ev("window.__toast||''") and 'Jill' in g.ev("window.__toast||''") and '正在洗' in g.ev("window.__toast||''"), f'both places taken: a tap says who is washing: {g.ev("window.__toast")}')
    ti = g.ev(DIRTY + "(0,0)")
    g.ev("tapTable(R.tables[%d])" % ti)
    for _ in range(300):
        g.ev(TICK + "(2)")
        if not g.ev("!!ddWashOf('jill')"): break
    check(not g.ev("!!ddWashOf('jill')") and g.ev("ddWasher()") == 'c1', f'asked for a table, Jill leaves the sink after the plate in hand; the cleaner washes on: {g.ev("JSON.stringify(ddWashers())")}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def workflow_the_dirty_dishes_survive_a_checkpoint(b, port, target):
    """「save/reload dirty dish state 不 duplication / disappearance」 (acceptance 16, 17): mid-evening — dishes in the tub, some
    in the cleaner's hands on the way, two at the sink being washed — the checkpoint brings back the same count, the same
    hands, the same washing; a checkpoint from before the dirty dishes (no tub in it) comes back with an empty tub."""
    g = _dirty_day(b, port, target, 9205)
    g.ev(DIRTY + "(0,3)"); g.ev(DIRTY + "(1,2)")
    for _ in range(400):
        g.ev(TICK + "(2)")
        if g.ev("handsN(R.cw.c1,'dirty')>0&&R.cw.c1.task&&R.cw.c1.task.k==='dump'"): break
    g.ev("ddS().n.push('plate','plate','cup','glass');R.tv++")
    before = json.loads(g.ev("JSON.stringify({n:ddCount(),tub:ddS().n.length,hands:handsN(R.cw.c1,'dirty'),dirty:R.tables.filter(t=>t.dirty).map(t=>[t.i,t.plates.length])})"))
    check(before['hands'] > 0, f'caught on the way: {before}')
    check(g.ev("checkpointSave('manual')"), 'the checkpoint is written')
    g.reload(); _rt.install_bot(g)
    g.click('[data-act=open]')
    after = json.loads(g.ev("JSON.stringify({n:ddCount(),tub:ddS().n.length,hands:handsN(R.cw.c1,'dirty'),dirty:R.tables.filter(t=>t.dirty).map(t=>[t.i,t.plates.length])})"))
    check(after == before, f'the same dishes, in the same places: {before} / {after}')
    # an older checkpoint (no tub in it): an empty tub, and the evening goes on
    g.ev("(()=>{const cp=JSON.parse(JSON.stringify(S.checkpoint));delete cp.snap.misc.dd;restoreService(cp)})()")   # (a reload writes a new checkpoint on the way out: the old one is restored directly)
    check(g.ev("phase") == 'service' and g.ev("ddS().n.length") == 0, 'a checkpoint from before: an empty tub')
    g.ev(TICK + "(60)")
    check(not g.errors, g.errors[:3]); g.close()


@test
def workflow_the_cart_shows_how_full_it_is(b, port, target):
    """「場景 visual 在 0、低、中、高、滿容量有明顯差異」 and 「mobile touch target 好點」 (acceptance 18, 19): the cart drawn at 0,
    2, 5, 8 and 10 is a different picture each time (more of it filled); the place to tap is at least 40 px each way on a phone."""
    g = _dirty_day(b, port, target, 9206)
    g.ev("setRoom('kitchen')")
    C = json.loads(g.ev("JSON.stringify(ddCart())"))
    shots = []
    for n in (0, 2, 5, 8, 10):
        g.ev(f"ddS().n=[];for(let i=0;i<{n};i++)ddS().n.push(['plate','plate','cup','bowl','glass'][i%5]);R.tv++;forceDraw=true;__tick(1000/30)")
        g.page.wait_for_timeout(40)
        r = json.loads(g.ev("JSON.stringify((()=>{const r=sc.getBoundingClientRect();return{x:r.left+SV.ox+%f*SV.s,y:r.top+SV.oy+%f*SV.s,s:SV.s}})())" % (C['x'] - 18, C['y'] - 60)))
        shots.append(g.page.screenshot(clip={'x': r['x'], 'y': r['y'], 'width': 40 * r['s'], 'height': 70 * r['s']}))
    from io import BytesIO
    from PIL import Image, ImageChops
    ims = [Image.open(BytesIO(x)).convert('RGB') for x in shots]
    diffs = [sum(ImageChops.difference(ims[i], ims[i + 1]).convert('L').point(lambda v: 255 if v > 24 else 0).histogram()[255:]) for i in range(4)]
    check(all(d > 40 for d in diffs), f'each step looks different on the cart: {diffs}')
    s = g.ev("SV.s")
    check(40 * s >= 40 and 44 * s >= 40, f'the cart is a big enough place to tap: {40 * s:.0f} × {44 * s:.0f} px')
    check(not g.errors, g.errors[:3]); g.close()


# ---------------------------------------------------------------- the user's decisions of 2026-10-09 (#4, #6, #7)

@test
def workflow_the_dishwasher_washes_and_the_big_cart_is_its_own(b, port, target):
    """The user, 2026-10-09 #4 (docs/v24/cooking_final_decisions_2026-10-09.txt): the 商用洗碗機 washes twice as fast and that
    is all — no bigger cart, no quicker clearing; the bigger cart (10 → 20) is 大髒盤車, a cheap mid-game upgrade ($8,000,
    from Jill's Restaurant) in the shop's 營運升級, bought with the same button as the others. A save from before that has
    the dishwasher keeps its 20 (as 大髒盤車), told once; one without keeps 10."""
    g = _dirty_day(b, port, target, 9311)
    o = json.loads(g.ev("JSON.stringify(OPS.find(o=>o.k==='cart'))"))
    check(o and o['tiers'] == [8000] and o['lv'] == 3, f'大髒盤車: $8,000, from level 3: {o}')
    caps = json.loads(g.ev("(()=>{const r=[];for(const [d,c] of [[0,0],[1,0],[0,1],[1,1]]){S.ops.dish=d;S.ops.cart=c;r.push(ddCap())}S.ops.dish=0;S.ops.cart=0;return JSON.stringify(r)})()"))
    check(caps == [10, 10, 20, 20], f'the cart holds 10, 20 with 大髒盤車, whatever the dishwasher: {caps}')
    w = json.loads(g.ev("(()=>{const m={lv:2};S.ops.dish=0;const a=[washT('c1'),cleanDur(m)];S.ops.dish=1;const b2=[washT('c1'),cleanDur(m)];S.ops.dish=0;return JSON.stringify([a,b2])})()"))
    check(abs(w[1][0] - w[0][0] * .5) < 1e-9 and abs(w[1][1] - w[0][1]) < 1e-9, f'the dishwasher: washing in half the time, clearing as before: {w}')
    texts = json.loads(g.ev("JSON.stringify({dish:OPS.find(o=>o.k==='dish').d(1),cart:OPS.find(o=>o.k==='cart').d(1),guide:JSON.stringify(GUIDE)})"))
    check('洗碗快一倍' in texts['dish'] and '20' not in texts['dish'] and '收桌' not in texts['dish'], f'the dishwasher card says washing only: {texts["dish"]!r}')
    check('20' in texts['cart'] and '大髒盤車 20 個' in texts['guide'], f'the cart card and the manual say 20 with 大髒盤車: {texts["cart"]!r}')
    # bought with the shop's button
    g.ev("R=null;phase='shop';S.day=10;S.level=3;S.money=20000;showShop();shopTab='works';showShop()"); g.page.wait_for_timeout(60)   # (店舖工程 opens on Day 3)
    check(g.ev("!!document.querySelector('[data-act=buyOps][data-k=cart]')"), '大髒盤車 for sale in 店舖工程')
    m0 = g.ev("S.money"); g.click('[data-act=buyOps][data-k=cart]'); g.page.wait_for_timeout(60)
    check(g.ev("opsLv('cart')") == 1 and g.ev("S.money") == m0 - 8000 and g.ev("ddCap()") == 20, 'bought: $8,000, the cart holds 20')
    # a save from before
    olds = json.loads(g.ev("""(()=>{const base=JSON.parse(localStorage.getItem(KEY));const a=Object.assign({},base,{ops:{dish:1},cartMig:undefined,news:[]});delete a.cartMig;
      const b2=Object.assign({},base,{ops:{},news:[]});delete b2.cartMig;const ra=parseSave(JSON.stringify(a)),rb=parseSave(JSON.stringify(b2));
      return JSON.stringify({a:ra.o.ops,an:ra.o.news.filter(x=>x.includes('大髒盤車')).length,b:rb.o.ops,bn:rb.o.news.filter(x=>x.includes('大髒盤車')).length,again:parseSave(JSON.stringify(ra.o)).o.news.filter(x=>x.includes('大髒盤車')).length})})()"""))
    check(olds['a'].get('cart') == 1 and olds['an'] == 1, f'a save with the dishwasher keeps the 20 (大髒盤車), told once: {olds}')
    check(not olds['b'].get('cart') and olds['bn'] == 0, f'a save without keeps 10, nothing said: {olds}')
    check(olds['again'] == 1, f'read again, it is not told twice: {olds}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def workflow_a_table_someone_is_going_to_clear_is_not_given_to_jill_too(b, port, target):
    """The user, 2026-10-09 #6: a dirty table a cleaner (or 秀琴阿姨) is already on her way to — tapped, it says so (「阿芳正在
    過去收拾。再點一次，改由 Jill 收拾。」) and Jill is not sent to race her for it; her trip goes on. Tapped again within a few
    seconds, Jill takes it: the cleaner lets it go (her task and her place in the tub are released) and finds other work —
    never two people on their way to one table."""
    g = _dirty_day(b, port, target, 9321)
    ti = g.ev(DIRTY + "(2,2)")
    ok = False
    for _ in range(60):
        g.ev(TICK + "(1)")
        if g.ev("(()=>{const w=R.cw.c1;return !!(w&&w.task&&w.task.k==='clean'&&w.task.t===R.tables[%d]&&w.moving)})()" % ti): ok = True; break
    check(ok, 'the cleaner is on her way to the table')
    g.ev("tapTable(R.tables[%d])" % ti)
    msg = g.ev("[...document.querySelectorAll('#toasts .toast')].map(e=>e.textContent).join(' ')")
    check('阿芳正在過去收拾' in msg and '改由 Jill 收拾' in msg, f'it says who is on it: {msg!r}')
    check(not g.ev("jillTargets(%d)" % ti) and g.ev("R.cw.c1.task&&R.cw.c1.task.t===R.tables[%d]" % ti), 'Jill is not sent; the cleaner goes on')
    on_way0 = g.ev("ddOnTheWay()")
    g.ev(TICK + "(3)")
    g.ev("tapTable(R.tables[%d])" % ti)
    check(g.ev("jillTargets(%d)" % ti) and g.ev("R.tables[%d].claim" % ti) is None, 'tapped again: Jill has it, the claim let go')
    check(not g.ev("R.cw.c1.task&&R.cw.c1.task.k==='clean'&&R.cw.c1.task.t===R.tables[%d]" % ti), 'the cleaner let it go')
    check(g.ev("ddOnTheWay()") < on_way0, f'her place in the tub released: {on_way0} → {g.ev("ddOnTheWay()")}')
    both = False
    for _ in range(300):
        g.ev(TICK + "(2)")
        w_on = g.ev("(()=>{const w=R.cw.c1;return !!(w&&w.task&&w.task.k==='clean'&&w.task.t===R.tables[%d])})()" % ti)
        if w_on and g.ev("jillTargets(%d)" % ti): both = True
        if not g.ev("R.tables[%d].dirty" % ti): break
    check(not both, 'never two people on their way to it')
    check(not g.ev("R.tables[%d].dirty" % ti), 'Jill cleared it')
    check(not g.errors, g.errors[:3]); g.close()


@test
def workflow_the_inspector_weighs_how_many_how_long_and_who_is_on_them(b, port, target):
    """The user, 2026-10-09 #12: the inspection is no longer 「22 秒內所有髒桌必須清空」 — he weighs how many dirty tables, for
    how long, and whether someone is on them; a table someone is on counts less than one nobody is; and it stays a
    challenge — tables someone is on do not pass by themselves. While he looks round (22 s) each dirty table counts every
    second: 1 when someone is on it (a claim, or Jill's), 2 when nobody is; he passes the place at 30 or less (INSP_OK).
    Burnt food plays no part (nothing burns). His review is tagged, so the summary never counts it as 料理失常 — a line
    the summary and the review digest no longer show (the new kitchen has none)."""
    g = _dirty_day(b, port, target, 9331)
    RUN = """(()=>{const out={};const run=(set,secs)=>{for(const t of R.tables){t.dirty=false;t.claim=null;t.group=null}R.jill.q=[];R.jill.cur=null;set();const I={sc:0,scU:0};for(let i=0;i<(secs||22)*30;i++)inspScore(I,1/30);return [Math.round(I.sc),Math.round(I.scU)]};
      out.none=run(()=>{});
      out.one_nobody=run(()=>{R.tables[0].dirty=true});
      out.one_nobody_15s=run(()=>{R.tables[0].dirty=true},15);
      out.one_cleaner=run(()=>{R.tables[0].dirty=true;R.tables[0].claim='c1'});
      out.one_jill=run(()=>{R.tables[0].dirty=true;R.jill.q=[0]});
      out.two_cleaner=run(()=>{for(const i of [0,1]){R.tables[i].dirty=true;R.tables[i].claim='c1'}});
      out.three_cleaner_10s=run(()=>{for(const i of [0,1,2]){R.tables[i].dirty=true;R.tables[i].claim='c1'}},10);
      out.four_cleaner_10s=run(()=>{for(const i of [0,1,2,3]){R.tables[i].dirty=true;R.tables[i].claim='c1'}},10);
      for(const t of R.tables){t.dirty=false;t.claim=null}R.jill.q=[];return JSON.stringify(out)})()"""
    sc = json.loads(g.ev(RUN))
    ok = g.ev("INSP_OK")
    check(ok == 30, f'he passes at 30 or less: {ok}')
    check(sc['none'] == [0, 0] and sc['one_cleaner'] == [22, 0] and sc['one_jill'] == [22, 0], f'clean, or one table someone is on the whole time: passes: {sc}')
    check(sc['one_nobody'] == [44, 44] and sc['one_nobody_15s'] == [30, 30], f'one table nobody is on counts double — a whole visit fails, 15 s is the line: {sc}')
    check(sc['two_cleaner'][0] > ok and sc['four_cleaner_10s'][0] > ok and sc['three_cleaner_10s'][0] <= ok + 1, f'tables someone is on still count: two the whole time, or four for 10 s, fail: {sc}')
    # the verdict at the end of his 22 s: the money, the review (tagged), the words
    res = []
    for s0, u0 in ((29, 0), (31, 31), (40, 10)):
        res.append(json.loads(g.ev("""(()=>{const m0=S.money,n0=S.reviews.length;R.insp={t:21.99,dur:22,x:224,y:204,tx:224,ty:204,sc:%d,scU:%d,out:false};__tick(1000/30);
          const r=S.reviews[S.reviews.length-1];return JSON.stringify({dm:S.money-m0,n:S.reviews.length-n0,s:r.s,txt:r.txt,tags:r.tags,out:!!(R.insp&&R.insp.out)})})()""" % (s0, u0))))
        g.ev("R.insp=null")
    check(res[0]['dm'] == 300 and res[0]['s'] == 5 and res[0]['tags'] == ['insp'], f'29: passed, +$300: {res[0]}')
    check(res[1]['dm'] == -300 and res[1]['s'] == 2 and '沒人收' in res[1]['txt'] and res[1]['tags'] == ['insp'], f'31, all of it nobody\'s: failed, 「放著沒人收」: {res[1]}')
    check(res[2]['dm'] == -300 and '太多、收得太慢' in res[2]['txt'], f'40, mostly tables someone was on: failed, 「太多、收得太慢」: {res[2]}')
    # in play: a table the cleaner clears while he looks round passes; the ring and the tag over him say how it goes
    g.ev("fireIncident('inspector');R.insp.x=R.insp.tx;R.insp.y=R.insp.ty")
    ti = g.ev(DIRTY + "(1,2)")
    m0 = g.ev("S.money"); seen = set()
    for _ in range(400):
        g.ev(TICK + "(3)")
        if g.ev("R.tables[%d].dirty" % ti): seen.add(g.ev("R.tables[%d].claim" % ti) or 'nobody')
        if not g.ev("!!R.insp") or g.ev("R.insp.out"): break
    check('c1' in seen and g.ev("S.money") - m0 == 300, f'the cleaner on it, cleared while he looked: passed: {seen}, {g.ev("S.money") - m0}')
    # no 「料理失常」: not in the summary's factors (even with an old day's Okay and burnt), not in the digest
    labels = json.loads(g.ev("JSON.stringify(ratingStory({q:{P:2,G:1,O:3,B:2},pats:[.9,.9],lost:0,reviews:[],angry:0,short:{},catJoy:0},8).map(x=>x.label))"))
    check('料理失常' not in labels, f'the summary has no 料理失常: {labels}')
    g.ev("for(let i=0;i<6;i++)S.reviews.push({s:2,txt:'x',name:'y',day:S.day,w:1})")   # untagged low reviews (older saves', the inspector's before)
    check('料理失常' not in g.ev("reviewDigestHTML()"), f'nor the digest: {g.ev("reviewDigestHTML()")}')
    check(not g.errors, g.errors[:3]); g.close()


DISH_COUNT = r"""(()=>{window.__dc={made:0,bad:[],over:[],peak:0};const D=window.__dc;
 const onT=()=>R.tables.reduce((a,t)=>a+(t.plates?t.plates.length:0),0);
 for(const name of ['serveItems','treatArrive']){const f0=eval(name);const wrap=function(){const a=onT();const r=f0.apply(this,arguments);D.made+=Math.max(0,onT()-a);return r};if(name==='serveItems')serveItems=wrap;else treatArrive=wrap}
 window.__dcCheck=function(){const hands=ddCarriers().reduce((a,w)=>a+handsN(w,'dirty'),0);const dyl=R.groups.reduce((a,g)=>a+(g.bus&&Array.isArray(g.dd)?g.dd.length:0),0)+(LIFE.dylan&&LIFE.dylan.carry&&Array.isArray(LIFE.dylan.dd)?LIFE.dylan.dd.length:0);   /* Dylan carrying his own plates to the hatch */
  const washed=(R.st.dd&&R.st.dd.wash)||0;const now=onT()+hands+ddS().n.length+washed+dyl;const c=ddCount();if(c>D.peak)D.peak=c;
  if(now!==D.made&&D.bad.length<5)D.bad.push({t:+R.t.toFixed(1),made:D.made,tables:onT(),hands,cart:ddS().n.length,washed,dyl});
  if(c>ddCap()&&D.over.length<5)D.over.push({t:+R.t.toFixed(1),count:c,cap:ddCap()})}})()"""


@test
def workflow_every_dish_goes_round_and_none_is_lost_or_made(b, port, target):
    """The user's release gate (2026-10-09, 三 C): 客人用餐結束 → 桌面產生髒盤 → 員工收桌 → 髒盤送回 → 洗碗 → 乾淨餐具恢復可用 →
    桌位重新接待客人, 「資源與數量守恆，不得無故複製或消失餐盤」 — with nobody to clear but Jill, one cleaner, two cleaners with the
    dishwasher and the big cart, a cleaner and two seasoned waiters who clear on the way. A busy stretch of each evening, every
    second: every dish set down at a table (served, or a treat) is still on a table, in someone's hands, in the cart, or washed —
    none lost, none made — and the cart never holds more than it can."""
    configs = [
        ('Jill alone', "", "window.__noXQH=1"),
        ('one cleaner', "{id:'c1',role:'cleaner',name:'阿芳',lv:1,duty:'clean',since:1,days:3,pool:'restaurant'}", ""),
        ('two cleaners, dishwasher, big cart', "{id:'c1',role:'cleaner',name:'阿芳',lv:2,duty:'clean',since:1,days:3,pool:'restaurant'},{id:'c2',role:'cleaner',name:'小彤',lv:1,duty:'clean',since:1,days:3,pool:'restaurant'}", "S.ops=S.ops||{};S.ops.dish=1;S.ops.cart=1"),
        ('a cleaner, two waiters on the way', "{id:'c1',role:'cleaner',name:'阿芳',lv:1,duty:'clean',since:1,days:3,pool:'restaurant'},{id:'w1',role:'waiter',name:'小茉',lv:3,duty:'both',since:1,days:3,pool:'restaurant'},{id:'w2',role:'waiter',name:'Kai',lv:2,duty:'both',since:1,days:3,pool:'restaurant'}", "S.ops=S.ops||{};S.ops.cart=1"),
    ]
    for name, crew, extra in configs:
        g = Game(b, port, target, seed=9361, manual=True, viewport={'width': 390, 'height': 844})
        _rt.install_bot(g)
        g.click('[data-act=open]'); g.page.wait_for_timeout(80)
        g.ev("S.day=12;S.level=3;S.tables=6;S.money=20000;S.eq.stove=3;S.eq.prep=1;S.eq.bar=2;S.eq.fridge=3;S.crew=[%s];%s;autoStock();save()" % (crew, extra))
        start_day(g)
        g.ev(_rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;")
        g.ev(DISH_COUNT)
        for _ in range(300):   # five minutes of the evening
            g.ev("for(let i=0;i<30;i++){if(!__act())break;update(1/30);updateCats(1/30,0);if(!R||phase!=='service')break}if(R)__dcCheck()")
            if g.ev("phase") != 'service': break
        r = json.loads(g.ev("JSON.stringify({made:__dc.made,bad:__dc.bad,over:__dc.over,peak:__dc.peak,washed:(R&&R.st.dd&&R.st.dd.wash)||0,cap:R?ddCap():null})"))
        check(r['made'] >= (6 if name == 'Jill alone' else 10), f'{name}: a busy stretch (dishes set down: {r["made"]})')
        check(not r['bad'], f'{name}: every dish accounted for: {r["bad"]}')
        check(not r['over'], f'{name}: the cart never holds more than it can: {r["over"]}')
        check(name == 'Jill alone' or r['washed'] > 0, f'{name}: dishes washed and back in use: {r}')
        check(not g.errors, f'{name}: {g.errors[:3]}'); g.close()
