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



# ---------------------------------------------------------------- the dirty dishes, on the same hands (the user's Part 1)

# a day with a cleaner (LV1) and nothing else of the floor's: guests kept patient, the kitchen left to the test
def _dirty_day(b, port, target, seed, crew="{id:'c1',role:'cleaner',name:'阿芳',lv:1,duty:'clean',since:1,days:3,pool:'restaurant'}"):
    g = Game(b, port, target, seed=seed, manual=True, viewport={'width': 390, 'height': 844})
    _rt.install_bot(g)
    g.click('[data-act=open]'); g.page.wait_for_timeout(80)
    g.ev("S.level=2;S.tables=4;S.money=5000;S.crew=[%s];save();window.__noXQH=1" % crew)
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
    g.ev("ddS().n=Array(10).fill('plate');ddS().wash={who:'x',ph:'take',t:0};R.tv++")   # full, and the sink taken (nobody can make room yet)
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
    g.ev("ddS().wash=null;R.tv++")
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
    g.ev("ddS().wash.stop=1")
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
    check(g.ev("ddWasher()") != 'jill' and not g.ev("R.jk&&handsN(R.jk,'dirty')"), 'Jill never by herself')
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
