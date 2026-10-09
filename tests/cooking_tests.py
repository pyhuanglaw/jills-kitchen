"""The working kitchen (v2.5; the user's spec of 2026-10-07 — docs/v24/cooking_*.txt, docs/cooking/ARCHITECTURE.md).

Every dish is a short workflow over the kitchen's own places (備料, 熱區, 烤箱, 飲料, 披薩烤爐, and 裝盤 — done where the food
is, then carried to the pass: the user, 2026-10-08, docs/v24/cooking_choreography_2026-10-08.txt); a batch of
the same dish is one piece of work and takes one place; Jill and the cooks share the same work. These tests hold the
user's acceptance list: the player always sees where a dish is and where it goes next, a full place means a quiet wait
(never a failure), a batch of three takes one burner, and the four hand-offs (Jill only, the cooks only, Jill then a cook,
a cook then Jill) are one state machine. `python3 tests/run_tests.py -k cooking` runs them.
"""
import json, sys
_rt = sys.modules['__main__'] if hasattr(sys.modules.get('__main__'), 'TESTS') else __import__('run_tests')
test, check, Game, start_day = _rt.test, _rt.check, _rt.Game, _rt.start_day

# the floor, as a player who does nothing in the kitchen: seat, take orders, serve what is ready, take the bill, clear
FLOOR = """window.__floor=function(){if(!(phase==='service'&&R))return;for(const g of queued()){if(g.state==='queue'){const t=freeTableFor(g);if(t)seatGroup(g,t)}}
 for(const t of R.tables){const g=t.group;if(jillTargets(t.i))continue;if(!g){if(t.dirty)tapTable(t);continue}if(g.state==='order'||g.state==='check'||(g.state==='wait'&&g.ticket&&g.ticket.items.some(i=>i.st==='ready'&&!i.picked)))tapTable(t)}}
window.__run=function(n){for(let i=0;i<n;i++){if(window.__patient)for(const q of R.groups)q.pat=1;__floor();__tick(1000/30)}}
/* more of a dish on a ticket that is already there (a kitchen test needs a number of portions at once) */
window.__addOrders=function(n,d){const tk=R.tickets[R.tickets.length-1];for(let i=0;i<n;i++)tk.items.push({d:d||'friedrice',st:'pending',q:null,want:0,picked:false,set:null});R.tv++}
/* who took which step of which work, as it happens */
window.__who={};{const A0=wfAssign;wfAssign=function(n,who,slot){const st=n&&(n.st==='ready'?n.si+1:n.si);const id=n&&n.id;const r=A0(n,who,slot);if(r)(__who[id]||(__who[id]=[])).push(who+'@'+st);return r}}"""
WF = "JSON.stringify((R.wf||[]).map(n=>({id:n.id,d:n.d,n:n.n,st:n.st,si:n.si,who:n.who,slot:n.slot&&n.slot.type,to:n.to&&n.to.type})))"
GUIDE = "((document.querySelector('#wfGuide')||{}).innerText||'')"


def _day(b, port, target, seed, setup=''):
    """Day 1 of a new game with the kitchen as the test needs it (two burners, a level, cooks), the floor run by __floor"""
    g = Game(b, port, target, seed=seed, manual=True, viewport={'width': 390, 'height': 844})
    g.ev(FLOOR)
    g.click('[data-act=open]'); g.page.wait_for_timeout(80)
    g.ev("S.eq.stove=2;" + setup)
    start_day(g)
    g.ev("setRoom('kitchen')")
    return g


def _wait_orders(g, n, d='friedrice', cap=400):
    for _ in range(cap):
        if g.ev(f"R.tickets.reduce((a,tk)=>a+tk.items.filter(it=>it.d==='{d}'&&it.st==='pending').length,0)") >= n:
            return True
        g.ev("__run(15)")
    return False


def _tap_scene(g, x, y):
    p = json.loads(g.ev(f"JSON.stringify((()=>{{const r=sc.getBoundingClientRect();return{{x:r.left+SV.ox+{x}*SV.s,y:r.top+SV.oy+{y}*SV.s}}}})())"))
    g.page.mouse.click(p['x'], p['y']); g.page.wait_for_timeout(40)


def _tap_slot(g, js_slot):
    o = json.loads(g.ev(f"JSON.stringify(wfSlotCenter({js_slot}))"))
    _tap_scene(g, o['x'], o['y'])


def _until(g, cond, cap=600, step=10):
    for _ in range(cap):
        if g.ev(cond):
            return True
        g.ev(f"__run({step})")
    return False


@test
def cooking_the_bar_takes_a_waiting_coffee_while_the_fried_rice_is_selected(b, port, target):
    """The user, 2026-10-09 (real play, Day 2): 「有時候在等炒飯 有咖啡訂單卻顯示現在沒有訂單不能做」. The fried rice picked on
    the ticket and sent to the burner stays selected while it cooks (and while it waits to be plated); a tap on the free
    coffee bar then fell through to the old kitchen's 「咖啡吧：目前沒有要做的料理」 although a coffee was waiting — a free
    place took its own waiting work only when nothing at all was selected. Now a free place takes its oldest waiting work
    whatever else is selected (a selected dish that goes to that place still goes first)."""
    g = _day(b, port, target, 7105, "S.eq.bar=Math.max(1,S.eq.bar);if(!S.unlocked.includes('coffee'))S.unlocked.push('coffee');")
    g.ev("window.__toasts=[];{const T0=toast;toast=function(m){__toasts.push(String(m));return T0.apply(this,arguments)}}")
    check(_wait_orders(g, 1), 'a table orders fried rice')
    # the fried rice's ticket item tapped (what the ticket's tap calls), then the burner
    check(g.ev("(()=>{for(const tk of R.tickets)for(const it of tk.items)if(it.d==='friedrice'&&it.st==='pending')return wfSelectItem(tk,it);return false})()"), 'the fried rice picked on its ticket')
    g.ev("__tick(1000/30)")
    fr = g.ev("R.wsel")
    _tap_slot(g, "R.slots.find(s=>s.type==='stove'&&s.no===1)")
    check(_until(g, "(()=>{const n=wfNode(R.wsel);return n&&(n.st==='work'||n.st==='cook')})()", step=3), 'the fried rice is on the fire')
    g.ev("__addOrders(1,'coffee');wfGather()")
    co = json.loads(g.ev("JSON.stringify((R.wf||[]).filter(n=>n.d==='coffee').map(n=>({id:n.id,st:n.st,who:n.who})))"))
    check(len(co) == 1 and co[0]['st'] == 'wait' and not co[0]['who'] and g.ev("R.wsel") == fr, f'a coffee waits; the fried rice is still the one selected: {co}')
    _tap_slot(g, "R.slots.find(s=>s.type==='bar')")
    st = json.loads(g.ev(f"JSON.stringify((()=>{{const n=wfNode({co[0]['id']});return{{st:n.st,who:n.who,to:n.to&&n.to.type}}}})())"))
    check(st['who'] == 'jill' and st['to'] == 'bar', f'the bar tapped: Jill takes the waiting coffee to it: {st}')
    check(not any('目前沒有要做的料理' in t for t in g.ev("__toasts")), f'no 「目前沒有要做的料理」: {g.ev("__toasts")}')
    check(_until(g, f"(()=>{{const n=wfNode({co[0]['id']});return n&&(n.st==='work'||n.st==='ready')}})()", step=3), 'she makes it')


@test
def cooking_every_drink_is_its_own_cup(b, port, target):
    """The user, 2026-10-09: 「飯可以一次炒多份 但咖啡不能一次兩杯吧」, then 「每一杯都要是獨立 work item、獨立杯子、獨立完成與
    出杯」 — 「可以同時做多杯，不是一次動作批量生出多杯」, the latte, the tea, the sparkling water and the berry soda alike.
    Drinks ordered together are as many pieces of work, one cup each (never one cup marked ×2, as before, when drinks were
    batched like the fried rice). The bar holds as many cups at once as it has places: a tap on the machine while a cup is
    being made there starts the next drink at a free place; with every place taken the next one waits (等空位). Each cup is
    done on its own and taken out on its own — Jill carries that one glass, the others stay at the bar — to its own spot
    on the pass, and the place it leaves takes the drink that was waiting."""
    g = _day(b, port, target, 7130, "S.level=5;S.eq.bar=3;for(const d of ['coffee','blacktea'])if(!S.unlocked.includes(d))S.unlocked.push(d);S.menu=['friedrice'];")   # the guests order fried rice; the drinks are the test's
    g.ev("window.__k=function(n){for(let i=0;i<n;i++){for(const q of R.groups)q.pat=1;__tick(1000/30)}}")
    places = g.ev("R.slots.filter(s=>s.type==='bar').length")
    check(places >= 2 and places == g.ev("barCups(S.eq.bar)"), f'the bar has its places: {places}')
    check(_wait_orders(g, 1), 'a table is in')
    # one more drink than the bar has places: lattes and a tea
    kinds = ['coffee' if i % 2 == 0 else 'blacktea' for i in range(places + 1)]
    g.ev("(()=>{" + "".join(f"__addOrders(1,'{d}');" for d in kinds) + "wfGather()})()")
    DR = "wfList().filter(n=>WF_DISH[baseOf(n.d)]==='drink2')"
    dr = json.loads(g.ev(f"JSON.stringify({DR}.map(n=>({{id:n.id,d:n.d,n:n.n,its:n.its.length}})))"))
    check(len(dr) == places + 1 and all(x['n'] == 1 and x['its'] == 1 for x in dr), f'{places + 1} drinks, {places + 1} pieces of work, one cup each: {dr}')
    ids = []
    for k in range(places):   # the machine tapped once for each place: each tap starts the next waiting drink at a free place
        _tap_slot(g, "R.slots.find(s=>s.type==='bar')")
        mine = json.loads(g.ev(f"JSON.stringify({DR}.filter(n=>n.who==='jill'||n.lastBy==='jill'||n.st==='ready').map(n=>n.id))"))
        new = [i for i in mine if i not in ids]
        check(len(new) == 1, f'tap {k + 1} on the machine: one more drink is Jill\'s: {mine} (had {ids})')
        ids += new
        g.ev("__k(4)")
    at = json.loads(g.ev(f"JSON.stringify({ids}.map(i=>{{const n=wfNode(i);const s=n.slot||n.to;return s&&s.type==='bar'?s.no:null}}))"))
    check(None not in at and len(set(at)) == places, f'each at its own place at the bar: {at}')
    last = next(x['id'] for x in dr if x['id'] not in ids)
    _tap_slot(g, "R.slots.find(s=>s.type==='bar')")
    check(not g.ev(f"wfNode({last}).who") and '等空位' in g.ev(f"wfState(wfNode({last}))"), f'every place taken: the last drink waits — {g.ev(f"wfState(wfNode({last}))")}')
    # done on its own: the first cup is ready while another is still being made
    check(_until(g, f"wfNode({ids[0]}).st==='ready'", step=2), 'the first cup is done')
    check(any(g.ev(f"wfNode({i}).st") != 'ready' for i in ids[1:]), 'the others are not done with it: ' + g.ev(f"JSON.stringify({ids}.map(i=>wfNode(i).st))"))
    # taken out on its own: a tap on that cup
    fs = json.loads(g.ev(f"JSON.stringify((()=>{{const n=wfNode({ids[0]});return wfFoodSpot(n,n.slot)}})())"))
    _tap_scene(g, fs['x'], fs['y'] - 6)
    if g.ev(f"wfNode({ids[0]}).who") != 'jill':   # a finished cup not selected yet: the first tap picks it out, the next sends Jill
        _tap_scene(g, fs['x'], fs['y'] - 6)
    check(g.ev(f"wfNode({ids[0]}).who") == 'jill' and g.ev(f"wfNode({ids[0]}).st") in ('fetch', 'go'), f'the cup tapped: Jill takes it out — {g.ev(f"wfNode({ids[0]}).st")}')
    check(_until(g, f"!wfNode({ids[0]})", step=2), 'set down on the pass')
    rest = json.loads(g.ev(f"JSON.stringify({ids[1:]}.map(i=>{{const n=wfNode(i);return n&&{{st:n.st,carry:!!n.carry,slot:n.slot&&n.slot.type}}}}))"))
    check(all(r and not r['carry'] for r in rest), f'the other cups were not carried with it: {rest}')
    pi = json.loads(g.ev("JSON.stringify(R.tickets.flatMap(t=>t.items).filter(i=>(i.d==='coffee'||i.d==='blacktea')&&i.st==='ready').map(i=>i.pi))"))
    check(len(pi) == 1 and pi[0] is not None, f'one glass on the pass, at its own spot: {pi}')
    # the place it left takes the drink that waited
    _tap_slot(g, "R.slots.find(s=>s.type==='bar')")
    check(g.ev(f"wfNode({last}).who") == 'jill', f'the freed place takes the waiting drink: {g.ev(f"wfState(wfNode({last}))")}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def cooking_the_bar_holds_one_cup_two_with_the_double_group_head_four_with_kitchen_ii(b, port, target):
    """How many cups at once is the coffee machine's (the user, 2026-10-09, choosing 「方案 2，讓料理與飲料設備的升級有真正的
    經營意義」 — the 2026-10-07 capacity rule's DRINK 1 → 2 → 4, 「不要改成 3」): Day 2's machine holds one cup, so a second
    latte waits (等空位) until the first is taken off the machine; the double group head (LV3) holds two; kitchen II's second
    machine two more. The shop says it the same way — 同時 N 杯, never 「一次 N 杯」, which reads as one press making N cups."""
    g = _day(b, port, target, 7132, "S.eq.bar=1;if(!S.unlocked.includes('coffee'))S.unlocked.push('coffee');S.menu=['friedrice'];")
    g.ev("window.__k=function(n){for(let i=0;i<n;i++){for(const q of R.groups)q.pat=1;__tick(1000/30)}}")
    cups = json.loads(g.ev("JSON.stringify((()=>{const k2=S.rooms.kitchen2;const out=[];for(const k of [0,1]){S.rooms.kitchen2=k;out.push([1,2,3,5].map(barCups))}S.rooms.kitchen2=k2;return out})())"))
    check(cups == [[1, 1, 2, 2], [3, 3, 4, 4]], f'the bar: 1, 2 with the double group head, 2 more with kitchen II: {cups}')
    shop = json.loads(g.ev("JSON.stringify([1,3].map(l=>EQUIP.find(e=>e.k==='bar').d(l)))"))
    check('同時 1 杯' in shop[0] and '雙沖煮頭，同時 2 杯' in shop[1] and not any('一次' in t for t in shop), f'the shop says how many at the same time: {shop}')
    k2 = g.ev("JSON.stringify(PROJECTS.concat(KITCHEN_WORKS).find(p=>p.k==='kitchen2'))")
    check('一次' not in k2 and '最多同時 4 杯' in k2, f'kitchen II says it the same way: {k2[:160]}')
    check(g.ev("R.slots.filter(s=>s.type==='bar').length") == 1, 'Day 2\'s machine: one place')
    check(_wait_orders(g, 1), 'a table is in')
    g.ev("__addOrders(2,'coffee');wfGather()")
    ids = json.loads(g.ev("JSON.stringify(wfList().filter(n=>n.d==='coffee').map(n=>n.id))"))
    check(len(ids) == 2, f'two lattes, two pieces of work: {ids}')
    _tap_slot(g, "R.slots.find(s=>s.type==='bar')")
    a = next(i for i in ids if g.ev(f"wfNode({i}).who") == 'jill'); bb = next(i for i in ids if i != a)
    g.ev("__k(6)")
    _tap_slot(g, "R.slots.find(s=>s.type==='bar')")
    check(not g.ev(f"wfNode({bb}).who") and '等空位' in g.ev(f"wfState(wfNode({bb}))"), f'the second latte waits for the place: {g.ev(f"wfState(wfNode({bb}))")}')
    check(_until(g, f"wfNode({a}).st==='ready'", step=2), 'the first latte is done')
    check(not g.ev(f"wfNode({bb}).who") and g.ev(f"wfNode({bb}).st") == 'wait', 'the second has not started: the cup is still on the machine')
    g.ev(f"wfAssign(wfNode({a}),'jill')")   # 送飲料: Jill takes it off the machine
    check(_until(g, f"(()=>{{const n=wfNode({a});return !n||n.carry}})()", step=1), 'the first latte is off the machine')
    _tap_slot(g, "R.slots.find(s=>s.type==='bar')")
    check(g.ev(f"wfNode({bb}).who") == 'jill', f'now the second one is made: {g.ev(f"wfState(wfNode({bb}))")}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def cooking_a_drink_batch_from_an_older_checkpoint_becomes_its_cups(b, port, target):
    """A service saved before every cup was its own (2026-10-09) can hold a batch of drinks: one nobody has started comes
    back as its cups, one under way finishes as it is (nothing made twice, nothing lost). And a checkpoint from a kitchen
    whose coffee bar had fewer places — before the places' kinds were kept in it — comes back with every piece of work at
    the same place, not as an empty shop."""
    g = _day(b, port, target, 7131, "S.eq.bar=3;for(const d of ['coffee','blacktea'])if(!S.unlocked.includes(d))S.unlocked.push(d);S.menu=['friedrice'];")
    check(_wait_orders(g, 1), 'a table is in')
    # two batches the old way: lattes nobody has started, teas on the machine
    g.ev("(()=>{const M0=wfMax;wfMax=d=>2;__addOrders(2,'blacktea');wfGather();__addOrders(2,'coffee');wfGather();wfMax=M0})()")
    tea = g.ev("wfList().find(n=>n.d==='blacktea').id")
    check(g.ev(f"wfNode({tea}).n") == 2 and g.ev("wfList().find(n=>n.d==='coffee').n") == 2, 'two batches of two, the old way')
    g.ev(f"wfAssign(wfNode({tea}),'jill',R.slots.find(s=>s.type==='bar'&&s.no===1))")
    check(_until(g, f"wfNode({tea}).st==='cook'", step=2), 'the teas on the machine')
    snap = json.loads(g.ev("JSON.stringify(snapshotService())"))
    # as an older version wrote it: no kinds, and the bar with its old count of places (the extra ones at its end removed)
    kinds = snap.pop('slotsK')
    old = g.ev("(S.eq.bar>=3?2:1)+(projOn('kitchen2')?2:0)")
    bars = [i for i, k in enumerate(kinds) if k == 'bar']
    drop = bars[old:]
    check(all(not snap['slots'][i]['job'] for i in drop), 'nothing at the places the older kitchen did not have')
    keep = [i for i in range(len(kinds)) if i not in drop]
    remap = {o: n for n, o in enumerate(keep)}
    snap['slots'] = [snap['slots'][i] for i in keep]; snap['slotsN'] = len(keep)
    for n in snap['wfx']['wf']:
        for k in ('slot', 'to'):
            if n.get(k) and n[k][0] == 's':
                check(n[k][1] in remap, f'work at a place the older kitchen had: {n[k]}'); n[k] = ['s', remap[n[k][1]]]
    ok = g.ev(f"(()=>{{try{{restoreService({{day:S.day,snap:{json.dumps(snap, ensure_ascii=False)}}});return true}}catch(e){{return String(e)}}}})()")
    check(ok is True, f'the older checkpoint restores: {ok}')
    after = json.loads(g.ev("JSON.stringify(wfList().filter(n=>n.d!=='friedrice').map(n=>({id:n.id,d:n.d,n:n.n,st:n.st,slot:n.slot&&[n.slot.type,n.slot.no],ok:n.its.every(o=>o.it.wf===n.id)})))"))
    cof = [x for x in after if x['d'] == 'coffee']; tw = [x for x in after if x['d'] == 'blacktea']
    check(len(cof) == 2 and all(x['n'] == 1 and x['st'] == 'wait' and x['ok'] for x in cof), f'the lattes nobody had started: two cups, two pieces of work: {cof}')
    check(len(tw) == 1 and tw[0]['n'] == 2 and tw[0]['st'] == 'cook' and tw[0]['slot'] == ['bar', 1], f'the teas on the machine stay there, a batch to the end: {tw}')
    check(g.ev("R.slots.filter(s=>s.type==='bar').length") == g.ev("barCups(S.eq.bar)"), 'the bar as it is now')
    check(_until(g, f"(()=>{{const n=wfNode({tea});if(n&&wfOpen(n))wfAssign(n,'jill');return !n}})()", step=3), 'the teas finish')
    tr = json.loads(g.ev("JSON.stringify(R.tickets.flatMap(t=>t.items).filter(i=>i.d==='blacktea').map(i=>i.st))"))
    check(len(tr) == 2 and all(x in ('ready', 'served') for x in tr), f'both teas made, once: {tr}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def cooking_fried_rice_goes_hot_then_plating_by_taps(b, port, target):
    """The first dish of the new kitchen, by real taps (the user's prototype list, J1–J15): the ticket item selects its
    work (the card says ● 熱區 → ○ 裝盤, 下一步：熱區; the burner is lit); a tap on the burner sends Jill, who walks there; the
    rice is in the wok and cooks by itself, no tap in between; done, it waits on the fire (✓ 熱區 → ● 裝盤, 下一步：裝盤)
    for as long as it takes — nothing spoils. 2026-10-08 (the user: 「PLATING 不是食物自己移動到某個 plating station」):
    what is lit for 裝盤 is the wok itself, never the pass; a tap on the wok sends Jill for plates, she plates it at the
    wok, carries the plate to the pass; then the plate goes the old way (ready at the pass, carried, paid), with its XP.
    (Changed 2026-10-08: it used to light the pass and plate there — the old acceptance the user named as wrong.)"""
    g = _day(b, port, target, 7101)
    check(_wait_orders(g, 1), 'a table orders fried rice')
    xp0 = g.ev("S.xp.friedrice||0")
    g.click('#tickets .it.pending'); g.page.wait_for_timeout(60); g.ev("__tick(1000/30)")
    n = json.loads(g.ev(WF))
    check(len(n) >= 1 and g.ev("R.wsel") == n[0]['id'] and g.ev("room") == 'kitchen', f'the ticket item selects its work, in the kitchen: {n}')
    gt = g.ev(GUIDE)
    check('黃金蛋炒飯' in gt and '● 熱區' in gt and '○ 裝盤' in gt and '第一步：熱區 · 等待處理' in gt, f'the card: the dish, its workflow, its first step, nobody on it yet: {gt!r}')
    check(g.ev("!!document.querySelector('#tickets .it.wsel .wf b')") and g.ev("document.querySelector('#tickets .it.wsel .wf b').textContent") == '熱',
          'the ticket item is picked out and its mark says 熱 now')
    check(g.ev("wfCueSlots(wfNode(R.wsel)).free.length") == 2, 'both free burners are cued')
    _tap_slot(g, "R.slots.find(s=>s.type==='stove'&&s.no===1)")
    st = json.loads(g.ev("JSON.stringify((()=>{const n=wfNode(R.wsel);return{st:n.st,who:n.who,to:n.to&&n.to.no,items:n.its.map(o=>o.it.st)}})())"))
    check(st['st'] == 'go' and st['who'] == 'jill' and st['to'] == 1 and all(x == 'cooking' for x in st['items']), f'the burner tapped: Jill is sent, the burner held: {st}')
    check(_until(g, "(()=>{const n=wfNode(R.wsel);return n&&(n.st==='work'||n.st==='cook')})()", step=3), 'she gets there and starts')
    check(_until(g, "(()=>{const n=wfNode(R.wsel);return n&&n.st==='ready'})()"), 'the rice is done by itself, with no tap in between')
    gt = g.ev(GUIDE)
    check('✓ 熱區' in gt and '● 裝盤' in gt and '下一步：裝盤' in gt, f'done: the card says where it goes next: {gt!r}')
    cue = json.loads(g.ev("JSON.stringify((()=>{const n=wfNode(R.wsel);const c=wfCueSlots(n);return{f:c.f,food:!!c.food,free:c.free.map(s=>s.type+s.no),at:n.slot.type+n.slot.no}})())"))
    check(cue['f'] == 'plate' and cue['food'] and cue['free'] == [cue['at']], f'the wok itself is cued for 裝盤, not the pass: {cue}')
    g.ev("__run(600)")   # twenty seconds of nothing
    st = json.loads(g.ev("JSON.stringify((()=>{const n=wfNode(R.wsel);return{st:n.st,sc:n.sc,slot:n.slot&&n.slot.type}})())"))
    check(st['st'] == 'ready' and st['slot'] == 'stove' and st['sc'] == [1], f'twenty seconds later it is still waiting on the fire, nothing lost: {st}')
    check(not any(w in g.ev(GUIDE) for w in ('秒', '%', '焦', '快')), 'the card has no timer, no score, no hurry')
    pp = json.loads(g.ev("JSON.stringify(wfSpot(wfPassSlots()[0]))"))
    _tap_scene(g, pp['x'], pp['y'] - 2)
    check(g.ev("wfNode(R.wsel)&&wfNode(R.wsel).st") == 'ready', 'a tap on the pass does not plate it (the pass is where plated food waits)')
    _tap_slot(g, "wfNode(R.wsel).slot")
    check(g.ev("wfNode(R.wsel)&&wfNode(R.wsel).st") == 'dish' and g.ev("wfNode(R.wsel).slot.type") == 'stove', 'the wok tapped: Jill goes for plates, the rice stays in the wok')
    gt = g.ev(GUIDE)
    check('下一步：裝盤 · Jill 前往中' in gt, f'on her way the card names the step she takes it to, not the one it left: {gt!r}')
    its = g.ev("wfNode(R.wsel).its.length")
    check(_until(g, "!R.wsel||!wfNode(R.wsel)"), 'she plates it')
    rd = json.loads(g.ev("JSON.stringify(R.tickets.flatMap(tk=>tk.items.filter(it=>it.d==='friedrice'&&(it.st==='ready'||it.st==='served')).map(it=>it.q)))"))
    check(len(rd) >= its and all(q == 'P' for q in rd), f'plated: ready (or already carried), Jill\'s — Perfect: {rd}')
    check(g.ev("S.xp.friedrice||0") >= xp0 + 2 * its, 'the XP of every portion')
    check(_until(g, "R.st.rev>0", cap=900), 'carried to the table and paid, the old way')
    check(not g.errors, g.errors[:3]); g.close()


@test
def cooking_a_full_place_is_a_quiet_wait(b, port, target):
    """The capacity rule's cases A–F on 熱區 2 and 裝盤 1: two batches cook at once (A); a third is told 「第一步：熱區 · 等空位」
    (2026-10-08: the user's 「第一步」 for a dish not started yet; was 「下一步：熱區 · 目前忙碌」), never an error, and cannot be
    put on a burner that is taken (B); when a burner is free it is 「等待處理」 again but does not start by itself (C); a batch of three takes one burner (D); two batches done at once and one plating place:
    one is plated, the other waits on its burner with its quality untouched (E); a cook who can plate takes the waiting one
    when the pass is free (F). D runs last, on the burner F's plating leaves."""
    g = _day(b, port, target, 7102, "S.level=1")
    g.ev("window.__patient=1")
    check(_wait_orders(g, 1), 'a table orders fried rice')
    g.ev("__addOrders(5)")
    check(_wait_orders(g, 6, cap=5), 'six portions of fried rice ordered')
    g.ev("__run(2)")   # the kitchen gathers new orders into work on its next frame
    ns = json.loads(g.ev(WF))
    check(len(ns) >= 3 and all(x['n'] <= 2 for x in ns), f'at level 1 a batch is up to two: {ns}')
    a, b2, c = ns[0]['id'], ns[1]['id'], ns[2]['id']
    ok = g.ev(f"wfAssign(wfNode({a}),'jill')&&wfAssign(wfNode({b2}),'jill')")
    check(ok, 'A: both burners take a batch')
    g.ev(f"R.wsel={c};__tick(1000/30)")
    gt = g.ev(GUIDE)
    check('第一步：熱區 · 等空位' in gt, f'B: the third is told the fire is busy — a wait, not an error: {gt!r}')
    check(g.ev(f"wfAssign(wfNode({c}),'jill',R.slots.find(s=>s.type==='stove'&&s.no===1))") is False and g.ev(f"wfNode({c}).st") == 'wait', 'B: it cannot be put on a burner that is taken; it stays as it was')
    check(_until(g, f"wfNode({a}).st==='ready'&&wfNode({b2}).st==='ready'", cap=900), 'A: both cook to done')
    # E: one plating place, two batches done
    check(g.ev(f"wfAssign(wfNode({a}),'jill')") is True and g.ev(f"wfAssign(wfNode({b2}),'jill')") is False, 'E: the pass holds one; the other cannot go too')
    q0 = g.ev(f"JSON.stringify(wfNode({b2}).sc)")
    check(_until(g, f"!wfNode({a})"), 'E: the first is plated')
    check(g.ev(f"wfNode({b2}).st") == 'ready' and g.ev(f"wfNode({b2}).slot.type") == 'stove' and g.ev(f"JSON.stringify(wfNode({b2}).sc)") == q0, 'E: the other waited on its burner, nothing lost')
    # C: a burner free again: the third may go, and does not go by itself
    gt = g.ev(GUIDE)
    check('等空位' not in gt and '第一步：熱區 · 等待處理' in gt, f'C: a burner is free: the third waits for someone again: {gt!r}')
    g.ev("__run(150)")
    check(g.ev(f"wfNode({c}).st") == 'wait', 'C: and it waits for someone to start it (no cook here can)')
    g.ev(f"wfAssign(wfNode({c}),'jill')")   # Jill puts it on the free burner: both burners are taken again
    # F: a cook who plates takes the waiting batch once the pass is free
    g.ev("S.crew.push({id:'t_kobayashi',role:'chef',name:'小林師傅',lv:1,duty:'stove',since:1,days:0,pool:'restaurant'})")
    check(_until(g, f"!wfNode({b2})", cap=900), 'F: 小林師傅 (plating is his) plates the batch that waited')
    # D: a batch of three is one burner (level 3) — the burner the plated batch left
    g.ev("S.level=3;__addOrders(3)")
    big = g.ev("(()=>{wfGather();const n=wfList().find(n=>n.st==='wait'&&n.n===3);return n?n.id:0})()")
    check(big, f'D: three portions gathered as one batch at level 3: {g.ev(WF)}')
    if big:
        used0 = g.ev("R.slots.filter(s=>s.type==='stove'&&s.wf).length")
        check(used0 < 2, f'D: a burner is free before it: {g.ev(WF)}')
        check(g.ev(f"wfAssign(wfNode({big}),'jill')") is True and g.ev("R.slots.filter(s=>s.type==='stove'&&s.wf).length") == used0 + 1, 'D: the batch of three takes one burner')
    check(not g.errors, g.errors[:3]); g.close()


@test
def cooking_jill_and_the_cooks_hand_work_on(b, port, target):
    """The four hand-offs, one state machine (spec §35): A Jill from start to end; B the cooks from start to end with no
    tap; C Jill on the fire, a cook plates; D a cook on the fire, Jill plates. A cook only takes what he can do: 阿德師傅
    at LV1 has the fire and not the pass (the proposal in CHEF_SKILL), 小林師傅 the pass."""
    ADE = "{id:'t_ade',role:'chef',name:'阿德師傅',lv:1,duty:'stove',since:1,days:0,pool:'restaurant'}"
    LIN = "{id:'t_lin',role:'chef',name:'小林師傅',lv:1,duty:'stove',since:1,days:0,pool:'restaurant'}"
    out = {}
    for case, crew in (('A', ''), ('B', f"S.crew.push({ADE},{LIN})"), ('C', f"S.crew.push({LIN})"), ('D', f"S.crew.push({ADE})")):
        g = _day(b, port, target, 7110 + ord(case), crew)
        g.ev("window.__patient=1")
        if case in ('A', 'C'):
            check(_wait_orders(g, 1), f'{case}: an order')
            nid = g.ev("(()=>{wfGather();return wfList()[0].id})()")
            check(g.ev(f"wfAssign(wfNode({nid}),'jill')") is True, f'{case}: Jill takes the fire')
        else:
            check(_until(g, "(R.wf||[]).length>0", step=5), f'{case}: an order')
            nid = g.ev("wfList()[0].id")
        check(_until(g, f"(()=>{{const n=wfNode({nid});return !n||n.st==='ready'}})()", cap=900, step=2), f'{case}: on the fire, then done')
        if case in ('A', 'D'):
            check(g.ev(f"wfNode({nid})&&wfNode({nid}).st") == 'ready', f'{case}: it waits at the fire for Jill')
            check(g.ev(f"wfAssign(wfNode({nid}),'jill')") is True, f'{case}: Jill takes the plating')
        check(_until(g, f"!wfNode({nid})", cap=900, step=2), f'{case}: plated')
        out[case] = json.loads(g.ev(f"JSON.stringify(__who[{nid}]||[])"))
        check(not g.errors, g.errors[:3]); g.close()
    check(out['A'] == ['jill@0', 'jill@1'], f"A: Jill, then Jill: {out['A']}")
    check(out['B'] == ['t_ade@0', 't_lin@1'], f"B: 阿德師傅 on the fire, 小林師傅 at the pass, no tap: {out['B']}")
    check(out['C'] == ['jill@0', 't_lin@1'], f"C: Jill on the fire, 小林師傅 plates: {out['C']}")
    check(out['D'] == ['t_ade@0', 'jill@1'], f"D: 阿德師傅 on the fire, Jill plates: {out['D']}")


@test
def cooking_the_card_says_who_has_it_and_a_dish_can_be_taken_back(b, port, target):
    """The user's hand-off canon (2026-10-08 §B, §D, §E, §F): a dish waiting says so (「第一步：熱區 · 等待處理」, no name on
    the ticket); a cook who decides to take it is seen deciding before he starts (「阿德師傅前往中」, his name outlined on the
    ticket); at work it is his (「● 熱區 · 阿德師傅」, his name filled). Focusing a dish never takes it (focus ≠ claim). While
    he is still on his way the player takes it back with a tap on the place it is headed for: Jill has it, nothing reset,
    the cook lets it go and takes other work; once he has started, a tap there only shows it — he finishes the step."""
    ADE = "{id:'t_ade',role:'chef',name:'阿德師傅',lv:3,duty:'bar',since:1,days:0,pool:'restaurant'}"   # posted at the coffee machine: a walk to the burners
    g = _day(b, port, target, 7140, f"S.level=3;S.eq.bar=1;S.crew.push({ADE})")
    g.ev("window.__patient=1")
    g.ev("window.__hold=true;{const W=wfStaff;wfStaff=function(){if(window.__hold)return;return W.apply(this,arguments)}}")   # the cook waits until the dish has been seen waiting
    check(_wait_orders(g, 1), 'an order')
    nid = g.ev("(()=>{wfGather();return wfList()[0].id})()")
    g.ev(f"(()=>{{const n=wfNode({nid});wfSelectItem(n.its[0].tk,n.its[0].it)}})()"); g.ev("__run(1)")
    gt = g.ev(GUIDE)
    check('第一步：熱區 · 等待處理' in gt, f'waiting: {gt!r}')
    check(not g.ev("!!document.querySelector('#tickets .it.wsel .wh')"), 'no name on the ticket while it waits')
    check(g.ev(f"wfNode({nid}).who") is None, 'focus is not a claim')
    g.ev("window.__hold=false")
    check(_until(g, f"wfNode({nid}).who==='t_ade'", step=1), 'the cook takes it')
    g.ev("__run(4)")   # the strip is redrawn a few times a second
    gt = g.ev(GUIDE)
    check('第一步：熱區 · 阿德師傅前往中' in gt and g.ev(f"wfNode({nid}).st") == 'go', f'on his way, said before he starts: {gt!r}')
    check(g.ev("(()=>{const e=document.querySelector('#tickets .it.wsel .wh');return !!e&&e.classList.contains('go')&&e.textContent==='阿德'})()"), 'his name on the ticket, outlined while on the way')
    # the player takes it back: a tap on the burner held for it
    to = g.ev(f"wfNode({nid}).to.no")
    _tap_slot(g, f"wfNode({nid}).to")
    st = json.loads(g.ev(f"JSON.stringify((()=>{{const n=wfNode({nid});return{{who:n.who,st:n.st,si:n.si,to:n.to&&n.to.no,its:n.its.map(o=>o.it.st),cook:(R.wfc||{{}}).t_ade||null,q:wfJ().wq,ck:n.ck||[]}}}})())"))
    check(st['who'] == 'jill' and st['st'] == 'go' and st['si'] == 0 and st['to'] == to and all(x == 'cooking' for x in st['its']) and st['cook'] is None and nid in st['q'] and not st['ck'],
          f'taken back: Jill has it, nothing reset, the cook let it go (and is not counted for it): {st}')
    check('第一步：熱區 · Jill 前往中' in g.ev(GUIDE), 'the card says Jill is on her way')
    # the cook goes on to other work: a second dish ordered is his
    g.ev("__addOrders(1,'pasta')"); g.ev("__run(2)")
    n2 = g.ev("(()=>{wfGather();const n=wfList().find(n=>n.d==='pasta');return n?n.id:0})()")
    check(n2 and _until(g, f"wfNode({n2})&&wfNode({n2}).who==='t_ade'", step=2), 'the cook finds other work')
    # once he has started, a tap on his place only shows it: he finishes the step
    check(_until(g, f"wfNode({n2}).st==='work'", step=1), 'he starts the pasta')
    _tap_slot(g, f"wfNode({n2}).slot"); g.ev("__run(4)")
    check(g.ev("R.wsel") == n2 and g.ev(f"wfNode({n2}).who") == 't_ade', 'a tap on the place he is working at shows it, and it stays his')
    gt = g.ev(GUIDE)
    check('● 熱區 · 阿德師傅' in gt, f'at work: {gt!r}')
    check(g.ev("(()=>{const e=document.querySelector('#tickets .it.wsel .wh');return !!e&&!e.classList.contains('go')})()"), 'his name filled on the ticket at work')
    check(not g.errors, g.errors[:3]); g.close()


@test
def cooking_any_dish_answers_the_five_questions(b, port, target):
    """The user's UX test (2026-10-08 §G): with dishes at different phases, a tap on any one of them answers at once — how
    far it is (the marks), where it goes next (第一步／下一步, or the place it is at now), where that is in the kitchen (a lit
    place, the place held for it, or the place it is at), whether someone has it (等待處理, 等空位, X 前往中, X, 正在煮／烤),
    and whether Jill can step in (a free place lit for her; the place held for a cook still on his way; not while a cook
    is at work on it)."""
    CREW = ("S.crew.push({id:'t_ade',role:'chef',name:'阿德師傅',lv:3,duty:'stove',since:1,days:0,pool:'restaurant'},"
            "{id:'t_marco',role:'chef',name:'Marco',lv:3,duty:'oven',since:1,days:0,pool:'restaurant'})")
    g = _day(b, port, target, 7150, "S.level=4;S.eq.stove=3;S.eq.oven=1;S.eq.bar=1;S.eq.prep=1;S.eq.fridge=2;" + CREW)
    g.ev("window.__patient=1")
    check(_until(g, "R.tickets.length>0"), 'an order')
    for d in ('friedrice', 'steak', 'salad', 'coffee', 'chicken', 'fries', 'pasta'):
        g.ev(f"__addOrders(1,'{d}')")
    g.ev("__run(2)"); g.ev("(()=>{wfGather();const n=wfList().find(n=>n.d==='steak');if(n)wfAssign(n,'jill')})()")
    g.ev("__run(70)")
    # Jill sent to two places in a row: the second says she does it next, not that she is on her way
    two = json.loads(g.ev(r"""JSON.stringify((()=>{const L=wfList().filter(n=>wfOpen(n)&&WF_ST[wfNext(n)].slot&&wfFreeSlot(wfNext(n)));const out=[];
      for(const n of L){if(out.length>=2)break;if(out.some(o=>wfNext(o)===wfNext(n)&&!wfSlots(wfNext(n)).filter(wfSlotFree).length))continue;if(wfAssign(n,'jill'))out.push(n)}
      return out.map(n=>wfState(n))})())"""))
    if len(two) == 2:
        check('接著做' in two[1] and '接著做' not in two[0], f'Jill\'s second job reads 「Jill 接著做」, the first 「Jill 前往中」: {two}')
    nodes = json.loads(g.ev("JSON.stringify(wfList().map(n=>n.id))"))
    phases = set(g.ev("wfList().map(n=>n.st+(n.who?'*':''))"))
    check(len(nodes) >= 4 and len(phases) >= 3, f'dishes at several phases: {phases}')
    bad = []
    for nid in nodes:
        g.ev(f"(()=>{{const n=wfNode({nid});R.wsel=null;wfSelectItem(n.its[0].tk,n.its[0].it)}})()")
        r = json.loads(g.ev(f"""JSON.stringify((()=>{{const n=wfNode({nid});const e=document.querySelector('#wfGuide');const cue=wfCueSlots(n);
          return{{d:n.d,st:n.st,who:n.who,card:e&&!e.hidden?e.innerText:'',marks:(e&&e.querySelector('.wfl')||{{}}).innerText||'',line:(e&&e.querySelector('.wfn')||{{}}).innerText||'',
            lit:cue.free.length,held:!!cue.held,at:!!n.slot,open:wfOpen(n),free:!!(wfNext(n)&&(!WF_ST[wfNext(n)].slot||wfFreeSlot(wfNext(n))))}}}})())"""))
        how_far = '●' in r['marks']
        where_next = any(w in r['line'] for w in ('第一步：', '下一步：', '● '))
        where = r['lit'] > 0 or r['held'] or r['at'] or not r['free']
        who = any(w in r['line'] for w in ('等待處理', '等空位', '前往中', '接著做', '正在煮', '正在烤', '快好了', 'Jill', '阿德師傅', 'Marco'))
        step_in = (r['open'] and (r['lit'] > 0 or not r['free'])) or (r['who'] and r['who'] != 'jill' and r['st'] in ('go', 'fetch') and r['held']) or r['st'] in ('work', 'cook') or r['who'] == 'jill' or (r['st'] in ('go', 'fetch'))
        if not (how_far and where_next and where and who and step_in):
            bad.append(r)
    check(not bad, f'dishes whose card leaves a question open: {bad}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def cooking_a_cook_on_standby_rests_and_his_card_counts_his_dishes(b, port, target):
    """The duty board in the new kitchen (ARCHITECTURE.md, decision 8): a cook taken off the board (「待命中」) does not take
    work, as the board says; put back on it, he does. A cook hired from now on is posted at his own place (阿德師傅 the
    range), never the coffee machine just because it was free. His staff card counts the restaurant's recipes that have a
    step he can take, and lists the ones his level does not allow yet."""
    ADE = "{id:'t_ade',role:'chef',name:'阿德師傅',lv:3,duty:null,since:1,days:0,pool:'restaurant'}"
    g = _day(b, port, target, 7160, f"S.level=3;S.crew.push({ADE})")
    g.ev("window.__patient=1")
    check(_until(g, "R.tickets.length>0"), 'an order')
    g.ev("__run(150)")
    check(not g.ev("wfList().some(n=>n.who==='t_ade'||(n.ck||[]).includes('t_ade'))"), f'a cook on standby rests: {g.ev(WF)}')
    g.ev("S.crew.find(m=>m.id==='t_ade').duty='stove'")
    check(_until(g, "wfList().some(n=>n.who==='t_ade')||R.tickets.some(tk=>tk.items.some(it=>it.st==='ready'))", step=3), 'back on the board, he takes work')
    check(g.ev("chefHomeDuty('阿德師傅')") == 'stove' and g.ev("(S.eq.oven=1,chefHomeDuty('Marco'))") == 'oven', 'a new cook is posted at his own place, not the coffee machine')
    card = g.ev("(()=>{const m={id:'t_k',role:'chef',name:'阿德師傅',lv:1,duty:'stove'};for(const d of ['friedrice','steak','salad'])if(!S.unlocked.includes(d))S.unlocked.push(d);return wfChefDishesHTML(m)})()")
    check('有他會的步驟：' in card and '🔒' in card and '炙烤肋眼牛排' in card, f'his card counts what he can do and shows what his level cannot yet: {card}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def cooking_the_work_survives_a_checkpoint(b, port, target):
    """A service saved in the middle of the new kitchen's work comes back with it: the batch on the fire is still on the
    fire, held by the same place. A checkpoint from before this version, with fried rice on an old-style station job, does
    not throw the evening away: that portion goes back to be made again (its stock was taken when it was ordered)."""
    g = _day(b, port, target, 7120)
    check(_wait_orders(g, 2), 'orders')
    g.ev("(()=>{wfGather();const n=wfList()[0];wfAssign(n,'jill')})()")
    check(_until(g, "(()=>{const n=wfList()[0];return n&&n.st==='cook'})()", step=3), 'on the fire, cooking by itself')
    before = json.loads(g.ev(WF))
    snap = g.ev("JSON.stringify(snapshotService())")
    g.ev(f"(()=>{{const cp={{day:S.day,snap:JSON.parse({json.dumps(snap)})}};restoreService(cp)}})()")
    after = json.loads(g.ev(WF))
    check([(x['d'], x['n'], x['st'], x['si'], x['slot']) for x in after] == [(x['d'], x['n'], x['st'], x['si'], x['slot']) for x in before], f'the same work, at the same place: {before} → {after}')
    check(_until(g, "(()=>{const n=wfList()[0];return n&&n.st==='ready'})()"), 'and it finishes after the reload')
    # an old-style job of fried rice in a checkpoint (as the player's saves from before have)
    s2 = json.loads(g.ev("JSON.stringify(snapshotService())"))
    tki = next(i for i, tk in enumerate(s2['tickets']) if any(it['d'] == 'friedrice' for it in tk['items']))
    iti = next(i for i, it in enumerate(s2['tickets'][tki]['items']) if it['d'] == 'friedrice')
    s2['tickets'][tki]['items'][iti]['st'] = 'cooking'; s2['tickets'][tki]['items'][iti].pop('wf', None)
    s2['wfx'] = None
    si = next(i for i, s in enumerate(s2['slots']) if not s['job'])
    s2['slots'][si]['job'] = {'d': 'friedrice', 'tk': tki, 'it': [tki, iti], 'si': 1, 'step': {'t': 'wait', 'p': .4}, 'scores': [1], 'adds': ['egg', 'rice'], 't0': 0}
    ok = g.ev(f"(()=>{{try{{restoreService({{day:S.day,snap:{json.dumps(s2, ensure_ascii=False)}}});return true}}catch(e){{return String(e)}}}})()")
    check(ok is True, f'the old checkpoint restores: {ok}')
    st = g.ev(f"R.tickets[{tki}].items[{iti}].st")
    check(st in ('pending', 'cooking') and not g.ev("R.slots.some(s=>s.job&&s.job.d==='friedrice')"), f'its fried rice is back to be made again, not on an old job: {st}')
    check(not g.errors, g.errors[:3]); g.close()


# every place in the kitchen: the oven, the coffee machine, the prep boards, the pizza oven, the signature dishes
ALL_PLACES = ("S.level=5;S.eq.stove=3;S.eq.oven=3;S.eq.bar=3;S.eq.prep=1;S.eq.fridge=3;S.rooms=S.rooms||{};S.rooms.pizzaoven=1;"
              "for(const d in DISHES)if(!S.unlocked.includes(d))S.unlocked.push(d);"
              "S.signature={base:'mash',protein:'duck',sauce:'redwine',side:'asparagus',name:'Test Sig'};"
              "S.sigDessert={base:'pannacotta',cream:'mascarpone',fruit:'berries',finish:'caramel',name:'試作'};")
# one dish through its workflow, Jill on every step: the places it used, in order, and how it ended
WALK = r"""(d=>{R.tickets=R.tickets.filter(t=>t.id!==997);const g0={id:'t997',name:'T',size:1,table:0,state:'wait',pat:1,type:'office',looks:makeLooks('office',1)};
  const it={d,st:'pending',q:null,want:d==='steak'?1:0,picked:false};const tk={id:997,no:1,g:g0,items:[it],t0:R.t};R.tickets.push(tk);
  wfGather();const n=wfOf(it);if(!n)return{d,err:'no work'};const places=[],seen=[];let guard=0;
  while(wfNode(n.id)&&guard++<6000){if(wfOpen(n)){if(!wfAssign(n,'jill'))return{d,err:'no place for '+wfNext(n),places}}
   const k=n.si+'|'+n.st;if(n.slot&&!seen.includes(n.si)&&(n.st==='work'||n.st==='cook')){seen.push(n.si);places.push(n.slot.type)}
   if(n.st==='work'&&!n.slot&&!seen.includes(n.si)){seen.push(n.si);places.push('pick')}
   for(const q of R.groups)q.pat=1;__tick(1000/30)}
  R.tickets=R.tickets.filter(t=>t!==tk);return{d,places,q:it.q,st:it.st,flow:wfFlow(d)}})"""


@test
def cooking_every_family_goes_its_own_way(b, port, target):
    """The user's workflow table (cooking_workflow_canon_2026-10-07.txt), family by family: each dish of the new kitchen
    goes through exactly the places of its own workflow, in order — 備料 at a prep board, 熱區 on a burner, 烤箱 in the oven,
    飲料 at the coffee machine, 披薩烤爐 in the pizza oven, 裝盤 where the food already is (changed 2026-10-08, the user's
    PLATING correction: it was 「裝盤 at the pass」 — the wok's rice is plated at the wok, the salad at its board, the baked
    dish at the oven), 送飲料: set down for the floor — and, made by Jill, it is Perfect. A special goes its base dish's way."""
    g = _day(b, port, target, 7130, ALL_PLACES)
    ids = g.ev("Object.keys(DISHES).concat(['signature','sigdessert']).filter(isWF)")
    want_slot = {'prep': 'prep', 'hot': 'stove', 'oven': 'oven', 'drink': 'bar', 'pizza': 'pizza', 'serve': 'pick'}   # 'plate': the place before it
    bad, seen_fams = {}, set()
    for d in ids:
        r = json.loads(g.ev(f"JSON.stringify(({WALK})({json.dumps(d)}))"))
        fl = r.get('flow') or []
        exp = [want_slot[fl[i - 1]] if f == 'plate' and i else want_slot[f] for i, f in enumerate(fl)]
        if r.get('err') or r.get('places') != exp or r.get('q') != 'P':
            bad[d] = r
        seen_fams.add(tuple(r.get('flow') or []))
    check(not bad, f'dishes off their workflow, or not Perfect from Jill: {bad}')
    check(len(seen_fams) == 7, f'all seven workflows are on the new kitchen: {sorted(seen_fams)}')
    sp = g.ev("Object.keys(SPECIALS).filter(b=>isWF(b)).every(b=>JSON.stringify(wfFlow(SPECIALS[b].id))===JSON.stringify(wfFlow(b)))")
    check(sp, 'a special goes its base dish\'s way')
    check(not g.errors, g.errors[:3]); g.close()


# where a person is: Jill in the kitchen, or a cook
POS = "(w=>{if(w==='jill'){const J=wfJ();return{x:J.x,y:J.y}}const a=R.ck&&R.ck[w];return a?{x:a.x,y:a.y}:null})"


@test
def cooking_plating_happens_where_the_food_is(b, port, target):
    """The user's PLATING correction (2026-10-08, docs/v24/cooking_choreography_2026-10-08.txt): 「食物不會自己去下一個
    地方。人去拿它、處理它、搬它。」 Its twelve checks: (1) done on the fire, the food stays in its pan on its burner;
    (2) claiming 裝盤 does not move it; (3) whoever plates first takes clean plates from the rack; (4) then walks to the
    food; (5) plates it there, beside the pan; (6) the pan empties as the plates fill; (7) only then carries the plates to
    the pass; (8) only once they are set down can the floor take them; (9) one work node all the way; (10) a cook plates
    the same way; (11) a batch of three gives three plates, still one work node; (12) a checkpoint in the middle of it
    comes back, a cook on his way to plate can be taken back, and the pass's places (1 at level 1) still hold one plating
    at a time."""
    # 1–9: Jill, one portion
    g = _day(b, port, target, 7170)
    g.ev("window.__patient=1")
    check(_wait_orders(g, 1), 'an order')
    nid = g.ev("(()=>{wfGather();const n=wfList()[0];wfAssign(n,'jill');return n.id})()")
    check(_until(g, f"wfNode({nid}).st==='ready'", step=3), 'on the fire, then done')
    at = json.loads(g.ev(f"JSON.stringify((()=>{{const n=wfNode({nid});const sp=wfFoodSpot(n,n.slot),h=slotHome(n.slot);return{{type:n.slot.type,no:n.slot.no,held:n.slot.wf===n,x:sp.x,y:sp.y,hx:h.x,hy:h.y}}}})())"))
    check(at['type'] == 'stove' and at['held'] and abs(at['x'] - at['hx']) < 1 and abs(at['y'] - at['hy']) < 1, f'(1) done, the rice is in its wok on its burner: {at}')
    trail = []
    g.ev(f"window.__trail=[];window.__nid={nid}")
    g.ev(f"(()=>{{const n=wfNode({nid});R.wsel=n.id}})()")
    _tap_slot(g, f"wfNode({nid}).slot")
    s0 = json.loads(g.ev(f"JSON.stringify((()=>{{const n=wfNode({nid});return{{st:n.st,who:n.who,slot:n.slot&&(n.slot.type+n.slot.no),held:!!n.slot&&n.slot.wf===n,tok:!!n.to&&n.to.type==='pass'&&n.to.wf===n,its:n.its.map(o=>o.it.st)}}}})())"))
    check(s0['st'] == 'dish' and s0['who'] == 'jill' and s0['slot'] == f"stove{at['no']}" and s0['held'] and s0['tok'] and all(x == 'cooking' for x in s0['its']),
          f'(2) 裝盤 claimed by a tap on the wok: the rice has not moved, its burner is still its, one of the pass\'s places is held: {s0}')
    rack = json.loads(g.ev("JSON.stringify(wfRack())"))
    seen = {'rack': False, 'food': False, 'work_at_food': False, 'out': [], 'topass_pi': None, 'ready_while_carried': False, 'ids': set()}
    for _ in range(900):
        r = json.loads(g.ev(f"""JSON.stringify((()=>{{const n=wfNode({nid});const p={POS}('jill');if(!n)return{{gone:true,p}};
          const o={{st:n.st,id:n.id,dishes:!!n.dishes,slot:n.slot&&(n.slot.type+n.slot.no),p,its:n.its.map(x=>x.it.st),pi:n.pi||null}};
          if(n.st==='work'&&n.f==='plate'){{const c=chState(n,'plate');o.out=c?c.st.out:null;const sp=wfFoodSpot(n,n.slot);o.plate=wfPlateAt(n,sp,0);o.food={{x:sp.x,y:sp.y}};const t=wfReach(n);o.spot={{x:t.x,y:t.y}}}}
          if(n.st==='tofood'){{const t=wfReach(n);o.spot={{x:t.x,y:t.y}}}}return o}})())"""))
        if r.get('gone'):
            break
        seen['ids'].add(r['id'])
        if r['st'] == 'tofood' and r['dishes']:
            if abs(r['p']['x'] - rack['x']) < 2 and abs(r['p']['y'] - rack['y']) < 2:
                seen['rack'] = True   # she has just taken the plates at the rack
        if r['st'] == 'work' and r.get('out') is not None:
            # (the user, 2026-10-08 evening: 「裝盤的時候人沒有真的到料理旁邊」 — standing behind the counter her hands were some 70
            # px from a front burner's wok: now she comes round to it, and her hands (33 px above her feet) are within reach of it)
            seen['work_at_food'] = seen['work_at_food'] or (r['slot'] == f"stove{at['no']}" and abs(r['p']['x'] - r['spot']['x']) < 3 and abs(r['p']['y'] - r['spot']['y']) < 3
                                                             and ((r['p']['x'] - r['food']['x']) ** 2 + (r['p']['y'] - 33 - r['food']['y']) ** 2) ** .5 < 50
                                                             and abs(r['plate']['x'] - r['food']['x']) < 60 and abs(r['plate']['y'] - r['food']['y']) < 20)
            seen['out'].append(r['out'])
        if r['st'] == 'topass':
            seen['topass_pi'] = r['pi']
            seen['ready_while_carried'] = seen['ready_while_carried'] or any(x == 'ready' for x in r['its'])
            seen['carry_slot'] = r['slot']
        g.ev("__run(1)")
    check(seen['rack'], f'(3) she took clean plates at the rack (wfRack {rack})')
    check(seen['work_at_food'], '(4)(5) she walked back to the wok and plated it there — beside it, her hands within reach of it — the plate beside the wok')
    outs = seen['out']
    check(len(outs) >= 3 and outs[0] < .5 and outs[-1] > .9 and all(b2 >= a for a, b2 in zip(outs, outs[1:])), f'(6) the rice leaves the wok for the plate as she goes: {outs[:3]}…{outs[-3:]}')
    check(seen['topass_pi'] is not None and seen.get('carry_slot') is None and not seen['ready_while_carried'],
          f'(7)(8) plated, the plate is carried to the pass (its spot held: {seen["topass_pi"]}) and nobody can take it until it is set down')
    check(seen['ids'] == {nid}, f'(9) one work node all the way: {seen["ids"]}')
    pl = json.loads(g.ev("JSON.stringify(R.tickets.flatMap(tk=>tk.items.filter(it=>it.d==='friedrice'&&it.st==='ready').map(it=>it.pi)))"))
    jx = json.loads(g.ev(f"JSON.stringify({POS}('jill'))"))
    mid = sum(g.ev(f"wfRowX({i})") for i in seen['topass_pi']) / len(seen['topass_pi'])
    check(pl and sorted(pl) == sorted(seen['topass_pi']) and abs(mid - jx['x']) < 2, f'(8) set down on the pass at the spots held for them, under her hands: {pl} at x={jx}')
    left = g.ev(f"(()=>{{const s=R.slots.find(s=>s.type==='stove'&&s.no==={at['no']});return s.left&&s.left.v}})()")
    check(left == 'wok', f'the empty wok stays on its burner: {left}')
    check(g.ev(f"JSON.stringify(__who[{nid}])") == '["jill@0","jill@1"]', 'Jill on the fire, Jill plating')
    check(not g.errors, g.errors[:3]); g.close()

    # 10–12: a cook plates the same way; a batch of three; a checkpoint mid-plating; taking it back; one plating at a time
    LIN = "{id:'t_lin',role:'chef',name:'小林師傅',lv:1,duty:'stove',since:1,days:0,pool:'restaurant'}"
    g = _day(b, port, target, 7171, f"S.level=3;S.crew.push({LIN})")
    g.ev("window.__patient=1")
    g.ev("window.__hold=true;{const W=wfStaff;wfStaff=function(){if(window.__hold)return;return W.apply(this,arguments)}}")
    check(_wait_orders(g, 1), 'an order')
    g.ev("__addOrders(2)"); g.ev("__run(2)")
    nid = g.ev("(()=>{wfGather();const n=wfList().find(n=>n.n===3);return n?n.id:0})()")
    check(nid, f'(11) three portions, one batch: {g.ev(WF)}')
    g.ev(f"wfAssign(wfNode({nid}),'jill')")
    check(_until(g, f"wfNode({nid}).st==='ready'", step=3), 'the batch done on the fire')
    g.ev("window.__hold=false")
    check(_until(g, f"wfNode({nid}).who==='t_lin'&&wfNode({nid}).st==='dish'", step=1), '(10) 小林師傅 (plating is his) sets off for the plates')
    # (12) the pass's one place at level 3? — level 3 still has one unless the wide pass is built: a second plating waits
    check(g.ev("passCap()") == 1 and not g.ev("!!wfFreeSlot('plate')"), '(12) one plating at a time: the pass\'s one place is held')
    # (12) take it back while he is on his way: the dish focused, then a tap on the wok it is in
    g.ev(f"(()=>{{const n=wfNode({nid});R.wsel=null;wfSelectItem(n.its[0].tk,n.its[0].it)}})()")
    _tap_slot(g, f"wfNode({nid}).slot")
    tb = json.loads(g.ev(f"JSON.stringify((()=>{{const n=wfNode({nid});return{{who:n.who,st:n.st,cook:(R.wfc||{{}}).t_lin||null,slot:n.slot&&n.slot.type}}}})())"))
    check(tb['who'] == 'jill' and tb['st'] == 'dish' and tb['cook'] is None and tb['slot'] == 'stove', f'(12) taken back: Jill goes for the plates instead, the rice still in the wok: {tb}')
    # hand it back to him: Jill lets go (a fresh claim by the cook)
    g.ev(f"(()=>{{const n=wfNode({nid});wfUnhand(n);if(n.to){{n.to.wf=null;n.to=null}}n.st='ready';n.adv=false;n.dishes=false}})()")
    check(_until(g, f"wfNode({nid}).who==='t_lin'&&wfNode({nid}).st==='tofood'", step=1), '(10) 小林師傅 has the plates and walks to the wok')
    # (12) a checkpoint now: it comes back mid-way and finishes
    snap = g.ev("JSON.stringify(snapshotService())")
    g.ev(f"(()=>{{const cp={{day:S.day,snap:JSON.parse({json.dumps(snap)})}};restoreService(cp)}})()")
    back = json.loads(g.ev(f"JSON.stringify((()=>{{const n=wfNode({nid});return n?{{st:n.st,who:n.who,slot:n.slot&&n.slot.type,held:!!n.slot&&n.slot.wf===n,tok:!!n.to&&n.to.wf===n}}:null}})())"))
    check(back and back['st'] == 'tofood' and back['who'] == 't_lin' and back['slot'] == 'stove' and back['held'] and back['tok'], f'(12) after a checkpoint: the same work, the same place: {back}')
    seen = {'work': False, 'plates': None}
    for _ in range(900):
        r = json.loads(g.ev(f"""JSON.stringify((()=>{{const n=wfNode({nid});if(!n)return{{gone:true}};const a=R.ck&&R.ck.t_lin;const t=n.slot&&n.slot.type!=='pass'?wfReach(n):null;
           return{{st:n.st,f:n.f,at:a&&t?Math.hypot(a.x-t.x,a.y-t.y):null,pi:n.pi||null}}}})())"""))
        if r.get('gone'):
            break
        if r['st'] == 'work' and r['f'] == 'plate' and r['at'] is not None and r['at'] < 3:
            seen['work'] = True
        if r['st'] == 'topass':
            seen['plates'] = r['pi']
        g.ev("__run(1)")
    check(seen['work'], '(10) he plated it at the wok, standing where the food is')
    check(seen['plates'] and len(seen['plates']) == 3 and len(set(seen['plates'])) == 3, f'(11) three plates carried, three spots on the pass: {seen["plates"]}')
    rd = json.loads(g.ev("JSON.stringify(R.tickets.flatMap(tk=>tk.items.filter(it=>it.d==='friedrice'&&it.st==='ready').map(it=>it.pi)))"))
    check(len(rd) >= 3 and len(set(rd)) == len(rd), f'(11) three plates waiting, each at its own spot: {rd}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def cooking_baked_food_waits_in_the_oven_and_a_glass_goes_to_its_spot(b, port, target):
    """The same rule at the other places (2026-10-08): a dish done in the oven stays in the oven until whoever plates it
    pulls it out — it does not jump onto the counter by itself; a drink is carried from the machine to its own spot on the
    pass and set down there, where it waits."""
    g = _day(b, port, target, 7172, "S.level=3;S.eq.oven=1;S.eq.bar=1;S.eq.fridge=2")
    g.ev("window.__patient=1")
    check(_until(g, "R.tickets.length>0"), 'an order')
    g.ev("__addOrders(1,'fries');__addOrders(1,'coffee')"); g.ev("__run(2)")
    fid = g.ev("(()=>{wfGather();const n=wfList().find(n=>n.d==='fries');wfAssign(n,'jill');return n.id})()")
    check(_until(g, f"wfNode({fid}).st==='ready'", step=3), 'the fries bake, then are done')
    sp = json.loads(g.ev(f"JSON.stringify((()=>{{const n=wfNode({fid});return wfFoodSpot(n,n.slot)}})())"))
    check(sp.get('inOven'), f'done, the fries are still in the oven: {sp}')
    g.ev(f"wfAssign(wfNode({fid}),'jill')")
    check(_until(g, f"wfNode({fid}).st==='work'", step=1), 'Jill has plates and is at the oven')
    early = json.loads(g.ev(f"JSON.stringify((()=>{{const n=wfNode({fid});return wfFoodSpot(n,n.slot)}})())"))
    check(early.get('inOven'), f'as she starts, the tray is still in the oven (her hands pull it out): {early}')
    check(_until(g, f"(()=>{{const n=wfNode({fid});return n&&n.st==='work'&&wfHands(n)>.3}})()", step=1), 'plating goes on')
    out = json.loads(g.ev(f"JSON.stringify((()=>{{const n=wfNode({fid});return wfFoodSpot(n,n.slot)}})())"))
    check(not out.get('inOven'), f'then it is out on the counter beside the plate: {out}')
    check(_until(g, f"!wfNode({fid})", step=2), 'plated and set down')
    cid = g.ev("(()=>{const n=wfList().find(n=>n.d==='coffee');return n?n.id:0})()")
    check(cid and _until(g, f"(()=>{{const n=wfNode({cid});if(n&&wfOpen(n))wfAssign(n,'jill');return n&&n.st==='go'&&n.carry}})()", step=1), 'the coffee made, carried')
    pi = json.loads(g.ev(f"JSON.stringify(wfNode({cid}).pi)"))
    check(pi and pi[0] is not None, f'the glass has its own spot on the pass while it is carried: {pi}')
    check(_until(g, f"!wfNode({cid})", step=2), 'set down')
    it = json.loads(g.ev("JSON.stringify(R.tickets.flatMap(tk=>tk.items.filter(it=>it.d==='coffee'&&it.st==='ready').map(it=>it.pi)))"))
    check(it == pi, f'it waits on the spot it was carried to: {it} vs {pi}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def cooking_the_first_three_days_teach_three_kinds_of_work(b, port, target):
    """The user's onboarding (2026-10-08, docs/v24/cooking_onboarding_2026-10-08.txt): 「第一天學做菜，第二天發現飲料也是工作，
    第三天開始真的覺得這是一間有不同工作區的廚房」. A fresh game, three evenings played by the test's player (it taps what
    needs tapping; on Day 3, the first day the player stocks, it takes the suggestion):
    - Day 1: only the fried rice, and it goes HOT → PLATING; 秀琴阿姨 really clears (dishes she carried in reach the cart);
    - Day 2: the latte comes with the day and so does the coffee machine — nobody pays for it — and a coffee goes DRINK → SERVE;
    - Day 3: a dish made another way — the salad, PREP → PLATING, on the cold station the day brings;
    - the money: a new game starts with START_MONEY ($1,200), and Jill's own Day 1 stocking leaves more than $500."""
    g = Game(b, port, target, seed=313, manual=True, viewport={'width': 390, 'height': 844})
    _rt.install_bot(g); g.click('[data-act=open]')
    check(g.ev("S.money") == 1200 and g.ev("START_MONEY") == 1200, f'a new game starts with $1,200: {g.ev("S.money")}')
    # what each piece of work went through, and what 秀琴阿姨 carried into the tub
    g.ev("""window.__steps={};window.__xqIn=0;{const D0=ddDeposit;ddDeposit=function(w){if(R&&w===R.xqh)__xqIn+=(w.hands||[]).filter(e=>e.k==='dirty'&&!e.w).length;return D0(w)}}
     window.__look=function(){if(!R)return;for(const n of R.wf||[])if(n.f)(__steps[n.d]||(__steps[n.d]=[])).includes(n.f)||__steps[n.d].push(n.f)}
     {const A0=wfArrive;wfArrive=function(n){const r=A0.apply(this,arguments);__look();return r}}   /* each step seen as it starts: 送飲料 is 0.7 s, shorter than the test's 1-second look (it was missed when the walk to the cups changed, 2026-10-08 evening) */""")
    seen = {}
    for day in (1, 2, 3):
        if day == 3:
            g.ev("autoStock()")   # the player presses the suggested stocking (from Day 3 Jill no longer stocks by herself)
        m_prep = g.ev("S.money")
        start_day(g)
        g.ev(_rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;")   # a player who leaves to 秀琴阿姨 what she covers
        info = json.loads(g.ev("JSON.stringify({day:S.day,money:S.money,menu:menuList(),bar:S.eq.bar,prep:S.eq.prep})"))
        if day == 1:
            check(info['menu'] == ['friedrice'], f'Day 1 is the fried rice alone: {info["menu"]}')
            check(info['money'] >= 500, f'after Jill stocks Day 1 there is still a cushion: ${info["money"]}')
        if day == 2:
            check('coffee' in info['menu'] and info['bar'] >= 1 and bar_day1 == 0, f'Day 2 brings the latte and the machine: {info}, Day 1 {bar_day1}')
            check(m_prep >= m_shop1, f'nobody paid for the machine: ${m_shop1} after Day 1, ${m_prep} on Day 2 before stocking')
        if day == 3:
            check('salad' in info['menu'] and info['prep'] >= 1 and 'pasta' not in info['menu'], f'Day 3 brings the salad and the cold station: {info}')
        g.ev("window.__steps={}")
        for _ in range(1500):
            r = g.page.evaluate('()=>{const r=window.__bot(30,1/30);window.__look();return r}')
            if g.ev("phase") != 'service' or not g.ev("!!R"): break
            if r['ticks'] < 30: break
        seen[day] = json.loads(g.ev("JSON.stringify(__steps)"))
        if g.ev("phase") == 'summary': g.click('[data-act=toShop]')
        if day == 1: bar_day1 = g.ev("S.eq.bar||0"); m_shop1 = g.ev("S.money")
        if day < 3: g.click('[data-act=nextDay]')
    check(seen[1].get('friedrice') == ['hot', 'plate'], f'Day 1: the fried rice goes HOT → PLATING: {seen[1]}')
    check(g.ev("__xqIn") >= 2, f'秀琴阿姨 carried dishes into the tub on Day 1: {g.ev("__xqIn")}')
    check(seen[2].get('coffee') == ['drink', 'serve'], f'Day 2: a coffee goes DRINK → SERVE: {seen[2]}')
    check(seen[3].get('salad') == ['prep', 'plate'], f'Day 3: the salad goes PREP → PLATING: {seen[3]}')
    grammars = {tuple(seen[1]['friedrice']), tuple(seen[2]['coffee']), tuple(seen[3]['salad'])}
    check(len(grammars) == 3, f'three days, three ways of working: {grammars}')
    check(not g.errors, g.errors)
    g.close()


@test
def cooking_a_save_past_day_three_before_the_onboarding_change_gets_its_cold_station_on_day_four(b, port, target):
    """The onboarding change moved the salad and the cold station from Day 4 to Day 3 and the pasta from Day 3 to Day 4.
    A save that passed Day 3 before it (the pasta, no cold station) gets the cold station and the salad on Day 4 with the
    pasta it already has — nothing is lost and nothing is unlocked twice; a new game's Day 4 adds only the pasta."""
    g = Game(b, port, target, seed=314, manual=True)
    g.click('[data-act=open]')
    old = json.loads(g.ev("""JSON.stringify((()=>{S.day=4;S.gate=3;S.unlocked=['friedrice','coffee','pasta'];S.menu=['friedrice','coffee','pasta'];
      S.eq.prep=0;S.eq.bar=1;S.eq.stove=2;S.news=[];applyGates();return{prep:S.eq.prep,unl:S.unlocked.slice(),news:S.news.join(' ')}})())"""))
    check(old['prep'] == 1 and 'salad' in old['unl'] and old['unl'].count('pasta') == 1 and '冷盤台啟用' in old['news'] and '番茄義大利麵' in old['news'],
          f'the old save catches up on Day 4: {old}')
    new = json.loads(g.ev("""JSON.stringify((()=>{S.day=4;S.gate=3;S.unlocked=['friedrice','coffee','salad'];S.menu=['friedrice','coffee','salad'];
      S.eq.prep=1;S.eq.bar=1;S.eq.stove=2;S.news=[];applyGates();return{prep:S.eq.prep,unl:S.unlocked.slice(),news:S.news.join(' ')}})())"""))
    check(new['unl'] == ['friedrice', 'coffee', 'salad', 'pasta'] and '冷盤台啟用' not in new['news'] and '番茄義大利麵' in new['news'],
          f"a new game's Day 4 adds the pasta only: {new}")
    check(not g.errors, g.errors)
    g.close()


@test
def cooking_day_two_a_latte_from_the_order_to_the_guest_by_taps(b, port, target):
    """The user's Day 2 acceptance (2026-10-08 evening, on the iPhone: 「拿鐵咖啡做好無法出杯」; 「請新增一個真正從 Day 2 玩家
    操作開始的 acceptance test，不要只直接改內部 state」; 「Day 2 新遊戲能不能從點拿鐵一路完整做到客人收到」). A new game, Day 1
    played by the test's bot; then Day 2 as the player plays it, every step a tap where the player taps it on a phone, table
    after table until a latte has reached its guest: the table with a 「!」 for the order; the 廚房 tab; each dish on the
    ticket chosen on the ticket, then its lit place (the stove, the coffee machine), and when it is done its lit place again
    (the wok to plate it, the machine to 送飲料 — the user's word since 「出杯這個用語太怪了吧」); the 主廳 tab; the table for its
    plates. On the way: made, the coffee machine is the lit place and the guide says 送飲料 (before the fix nothing was lit
    and no tap did anything); whoever takes a finished dish or the cups stands beside it, within reach; each waits on the
    pass at its own spot; and the guest has the latte."""
    g = Game(b, port, target, seed=7175, manual=True, viewport={'width': 390, 'height': 844})
    _rt.install_bot(g); g.click('[data-act=open]'); g.page.wait_for_timeout(80)
    start_day(g); _rt.play_day(g)                                   # Day 1, the bot
    if g.ev("phase") == 'summary': g.click('[data-act=toShop]')
    g.click('[data-act=nextDay]'); g.page.wait_for_timeout(80)
    check(g.ev("S.day") == 2 and 'coffee' in g.ev("menuList()") and g.ev("S.eq.bar") >= 1, f'Day 2: the latte and the coffee machine: {g.ev("menuList()")}')
    start_day(g)                                                    # from here on, only the player's taps and the clock
    tick = lambda n=1: g.ev(f"(n=>{{for(let i=0;i<n;i++)__tick(1000/30)}})({n})")
    def tap_scene(x, y):
        o = json.loads(g.ev(f"JSON.stringify((()=>{{const r=sc.getBoundingClientRect();return{{x:r.left+SV.ox+{x}*SV.s,y:r.top+SV.oy+{y}*SV.s}}}})())"))
        g.page.mouse.click(o['x'], o['y']); g.page.wait_for_timeout(30); tick()
    def to_room(k):
        if g.ev("room") == k: return
        g.ev("renderRoomTabs(true)"); g.page.click(f'#roomTabs [data-room="{k}"]'); g.page.wait_for_timeout(30); tick()
        check(g.ev("room") == k, f'the {k} tab')
    def tap_table(t):
        to_room('main')
        xy = json.loads(g.ev(f"JSON.stringify((t=>({{x:t.x,y:t.y}}))(R.tables[{t}]))"))
        tap_scene(xy['x'], xy['y'])
    def choose(tid, idx):
        g.ev("renderTickets()"); g.page.click(f'#tickets [data-tk="{tid}"][data-i="{idx}"]'); g.page.wait_for_timeout(30); tick()
    seen = {'coffee_lit': False, 'reach': []}
    def cook(tid):
        """every dish of a ticket, by taps, until it waits on the pass"""
        to_room('kitchen')
        for idx in range(g.ev(f"R.tickets.find(t=>t.id==={tid}).items.length")):
            it = json.loads(g.ev(f"JSON.stringify((it=>({{d:it.d,st:it.st,wf:it.wf||null}}))(R.tickets.find(t=>t.id==={tid}).items[{idx}]))"))
            if it['st'] != 'pending': continue
            d = it['d']
            choose(tid, idx)
            nid = g.ev("R.wsel")
            check(nid and g.ev(f"wfNode({nid}).d") == d, f'{d}: chosen on its ticket')
            first = json.loads(g.ev(f"JSON.stringify((()=>{{const n=wfNode({nid});const s=wfBestSlot(n,wfCueSlots(n));return s?wfSlotCenter(s):null}})())"))
            check(first, f'{d}: its first place is lit')
            tap_scene(first['x'], first['y'])
            check(g.ev(f"wfNode({nid}).who==='jill'"), f'{d}: the lit place tapped, Jill goes')
            for _ in range(900):
                if g.ev(f"(n=>!n||n.st==='ready')(wfNode({nid}))"): break
                tick(3)
            check(g.ev(f"wfNode({nid})&&wfNode({nid}).st==='ready'"), f'{d}: made, it waits where it was made')
            if g.ev("R.wsel") != nid: choose(tid, idx)
            nxt = g.ev(f"wfNext(wfNode({nid}))")
            cue = json.loads(g.ev(f"JSON.stringify((c=>c.free.map(s=>s.type))(wfCueSlots(wfNode({nid}))))"))
            if d == 'coffee':
                check(nxt == 'serve' and cue == ['bar'] and '送飲料' in g.ev(GUIDE) and '出杯' not in g.ev(GUIDE),
                      f'the latte made: the machine is the lit place and the guide says 送飲料: {nxt} {cue} / {g.ev(GUIDE)}')
                seen['coffee_lit'] = True
            sp = json.loads(g.ev(f"JSON.stringify((()=>{{const n=wfNode({nid});const s=wfFoodSpot(n,n.slot);return{{x:s.x,y:s.y}}}})())"))
            tap_scene(sp['x'], sp['y'] - 6)                        # the finished food / the cups, where they are
            check(g.ev(f"wfNode({nid}).who==='jill'"), f'{d}: tapped where it is: Jill goes for it ({nxt})')
            reach = json.loads(g.ev(f"JSON.stringify((()=>{{const r=wfReach(wfNode({nid}));return{{x:r.x,y:r.y}}}})())"))
            near = False
            for _ in range(900):
                if not g.ev(f"!!wfNode({nid})"): break
                p = json.loads(g.ev("JSON.stringify((J=>({x:J.x,y:J.y}))(wfJ()))"))
                if abs(p['x'] - reach['x']) < 3 and abs(p['y'] - reach['y']) < 3: near = True
                tick(2)
            hands = ((reach['x'] - sp['x']) ** 2 + (reach['y'] - 33 - sp['y']) ** 2) ** .5
            seen['reach'].append((d, round(hands)))
            check(near and hands < 50, f'{d}: she went to it and stood within reach of it ({hands:.0f} px from her hands)')
            st = json.loads(g.ev(f"JSON.stringify((it=>({{st:it.st,pi:it.pi}}))(R.tickets.find(t=>t.id==={tid}).items[{idx}]))"))
            check(st['st'] in ('ready', 'served') and (st['st'] == 'served' or st['pi'] is not None), f'{d}: on the pass at its own spot for the floor: {st}')
    served_latte = False
    done = set()
    to_room('main')
    for _ in range(1200):
        if not g.ev("phase==='service'&&!!R"): break
        t = g.ev("(()=>{const t=R.tables.find(t=>t.group&&t.group.state==='order'&&!jillTargets(t.i));return t?t.i:null})()")
        if t is not None: tap_table(t)                              # the 「!」: the order
        tid = g.ev("(()=>{const tk=R.tickets.find(tk=>!tk.lounge&&tk.items.some(i=>i.st==='pending'));return tk?tk.id:null})()")
        if tid and tid not in done:
            has_latte = g.ev(f"R.tickets.find(t=>t.id==={tid}).items.some(i=>i.d==='coffee')")
            table = g.ev(f"R.tickets.find(t=>t.id==={tid}).g.table")
            cook(tid); done.add(tid)
            tap_table(table)                                        # the plates to the table
            for _ in range(600):
                if g.ev(f"!R.tickets.find(t=>t.id==={tid})||R.tickets.find(t=>t.id==={tid}).items.every(i=>i.st==='served')"): break
                tick(3)
            got = json.loads(g.ev(f"JSON.stringify((()=>{{const tk=R.tickets.find(t=>t.id==={tid});return tk?tk.items.map(i=>[i.d,i.st]):'done'}})())"))
            check(got == 'done' or all(st == 'served' for d, st in got), f'the table has its order: {got}')
            if has_latte:
                served_latte = True; break
        tick(3)
    check(served_latte and seen['coffee_lit'], f'a latte made, taken out with a tap and brought to its guest: {seen}')
    check(g.ev("(R&&R.st.dish||{}).coffee>0"), 'the evening counts the latte as served')
    check(not g.errors, g.errors[:3]); g.close()


@test
def cooking_the_users_day3_latte_goes_out_by_a_tap(b, port, target):
    """The user's own save (tests/saves/cooking_day3_0156.json, private test page Version 10, sent with 「拿鐵咖啡做好無法
    出杯」): Day 3, 18:33, a latte made at the coffee machine and waiting there — nothing lit, no tap taking it out. Resumed
    the way the title's OPEN resumes it: now the machine is lit and the guide says 送飲料; a tap on the cups sends Jill to
    them; they go to the pass; a tap on the table, and 林小姐 has her latte."""
    import os
    raw = json.load(open(os.path.join(_rt.ROOT, 'tests', 'saves', 'cooking_day3_0156.json'), encoding='utf-8'))['save']
    g = Game(b, port, target, seed=1, manual=True, viewport={'width': 390, 'height': 844})
    g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.page.wait_for_timeout(150)
    g.click('[data-act=open]'); g.page.wait_for_timeout(150)
    for _ in range(30):
        if g.ev("typeof DLG!=='undefined'&&!!DLG"): g.ev("dlgNext()")
    tick = lambda n=1: g.ev(f"(n=>{{for(let i=0;i<n;i++){{for(const q of R.groups)q.pat=1;__tick(1000/30)}}}})({n})")
    check(g.ev("phase") == 'service' and g.ev("S.day") == 3, 'the evening resumed at 18:33')
    n = json.loads(g.ev("JSON.stringify((n=>n&&{st:n.st,d:n.d,next:wfNext(n),slot:n.slot&&n.slot.type})(wfNode(8)))"))
    check(n == {'st': 'ready', 'd': 'coffee', 'next': 'serve', 'slot': 'bar'}, f'the latte as it was: made, at the machine, its next step 送飲料: {n}')
    g.ev("setRoom('kitchen');R.wsel=8;renderTickets();wfGuideUpd();__tick(1000/30)")
    check(json.loads(g.ev("JSON.stringify(wfCueSlots(wfNode(8)).free.map(s=>s.type))")) == ['bar'] and '送飲料' in g.ev(GUIDE), f'the machine is lit, the guide says 送飲料: {g.ev(GUIDE)}')
    sp = json.loads(g.ev("JSON.stringify((n=>{const s=wfFoodSpot(n,n.slot);return{x:s.x,y:s.y}})(wfNode(8)))"))
    _tap_scene(g, sp['x'], sp['y'] - 6)
    check(g.ev("wfNode(8).who==='jill'&&wfNode(8).st==='fetch'"), 'a tap on the cups: Jill goes for them')
    for _ in range(600):
        if not g.ev("!!wfNode(8)"): break
        tick(2)
    it = json.loads(g.ev("JSON.stringify(R.tickets.flatMap(t=>t.items).filter(i=>i.d==='coffee').map(i=>[i.st,i.pi]))"))
    check(it and it[0][0] == 'ready' and it[0][1] is not None, f'the latte on the pass at its own spot: {it}')
    table = g.ev("R.tickets.find(t=>t.items.some(i=>i.d==='coffee'&&i.st==='ready')).g.table")
    g.ev("setRoom('main');__tick(1000/30)")
    xy = json.loads(g.ev(f"JSON.stringify((t=>({{x:t.x,y:t.y}}))(R.tables[{table}]))"))
    _tap_scene(g, xy['x'], xy['y'])
    for _ in range(600):
        if g.ev("(R.st.dish||{}).coffee>0"): break
        tick(3)
    check(g.ev("(R.st.dish||{}).coffee>0"), f'林小姐 has her latte: {g.ev("JSON.stringify(R.tickets.flatMap(t=>t.items).map(i=>[i.d,i.st]))")}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def cooking_each_dish_with_its_own_beats_starts_raw_and_changes_by_hand(b, port, target):
    """The choreography (the user's spec, docs/v24/cooking_choreography_2026-10-08.txt, HARD RULES 1–4), for every dish with
    its own beats so far (docs/cooking/CHOREOGRAPHY.md: the fried rice; batch 1, batch 2 …): what goes
    in goes in by a hand — a beat that adds something is the hands', never the heat's, and every beat of the hands has its
    gesture; at the start of each place the dish is its raw look (nothing of the place done), the beats in order bring it to
    the place's finished look; and drawn in the kitchen it looks different at the start, when the hands are done (half way
    through them where nothing cooks by itself) and at the end of each place, and while it is plated — never one finished picture from the first moment."""
    g = _day(b, port, target, 9101, "S.eq.bar=Math.max(S.eq.bar,1);S.eq.prep=Math.max(S.eq.prep,1);S.eq.oven=Math.max(S.eq.oven,1);S.rooms=S.rooms||{};S.rooms.pizzaoven=1;"
           "S.signature={base:'mash',protein:'duck',sauce:'redwine',side:'asparagus',name:'Test Sig'};S.sigDessert={base:'pannacotta',cream:'mascarpone',fruit:'berries',finish:'caramel',name:'試作'};")   # (the pizza oven: the fifth batch's pizzas are drawn in its mouth; Jill's own two exist only once she has made them)
    beats = json.loads(g.ev(r"""JSON.stringify((()=>{const out={};for(const d of Object.keys(CH))for(const f of Object.keys(CH[d])){const c=CH[d][f];const bad=[];
      for(const x of c.hands||[])if(!x.g)bad.push('hands without a gesture: '+x.say);
      for(const x of c.heat||[])if(x.ing)bad.push('added by the heat: '+x.say);
      const s0=Object.assign({},c.from);chRun(s0,c.hands,0);const raw=Object.keys(c.from).every(k=>s0[k]===c.from[k]);
      const s1=Object.assign({},c.from);chRun(s1,c.hands,1);if(c.heat)chRun(s1,c.heat,1);const last={};for(const x of(c.hands||[]).concat(c.heat||[]))Object.assign(last,x.set);
      out[d+'.'+f]={bad,raw,done:Object.keys(last).every(k=>Math.abs(s1[k]-last[k])<1e-9),n:(c.hands||[]).length+(c.heat||[]).length}}return out})())"""))
    for want in ('friedrice.hot', 'friedrice.plate', 'coffee.drink', 'blacktea.drink', 'sparkling.drink', 'salad.prep', 'salad.plate', 'pasta.hot', 'pasta.plate', 'soup.hot', 'soup.plate',
                 'burger.prep', 'burger.hot', 'burger.plate', 'pudding.prep', 'pudding.plate', 'fries.oven', 'fries.plate', 'fruitsoda.drink', 'veg.prep', 'veg.oven', 'veg.plate',
                 'tiramisu.prep', 'tiramisu.plate', 'chicken.prep', 'chicken.oven', 'chicken.plate', 'steak.prep', 'steak.hot', 'steak.plate', 'basque.prep', 'basque.oven', 'basque.plate', 'prosciutto.prep', 'prosciutto.plate',
                 'salmon.prep', 'salmon.oven', 'salmon.plate', 'seafood.prep', 'seafood.hot', 'seafood.plate', 'duck.prep', 'duck.hot', 'duck.plate', 'risotto.hot', 'risotto.plate', 'souffle.prep', 'souffle.oven', 'souffle.plate',
                 'bites.hot', 'bites.plate', 'croquette.prep', 'croquette.hot', 'croquette.plate', 'cheeseplate.prep', 'cheeseplate.plate', 'mushroom.hot', 'mushroom.plate',
                 'wings.hot', 'wings.plate', 'cheesestick.hot', 'cheesestick.plate', 'oyster.prep', 'oyster.plate', 'knuckle.prep', 'knuckle.oven', 'knuckle.plate',
                 'pizza.prep', 'pizza.pizza', 'pizza.plate', 'pzmarg.prep', 'pzmarg.pizza', 'pzmarg.plate', 'pzfungi.prep', 'pzfungi.pizza', 'pzfungi.plate',
                 'signature.prep', 'signature.hot', 'signature.plate', 'sigdessert.prep', 'sigdessert.plate'):
        check(want in beats, f'{want} has its own beats: {sorted(beats)}')
    for k, v in beats.items():
        check(not v['bad'] and v['raw'] and v['done'] and v['n'] >= 2, f'{k}: by hand, from raw to done in its beats: {v}')
    # drawn: each place at its start, when the hands are done, at its end; the plates at their start, half way, done
    looks = json.loads(g.ev(r"""JSON.stringify((()=>{const cv=document.createElement('canvas');cv.width=240;cv.height=200;const c=cv.getContext('2d');const out={};
      const hashOf=()=>{const px=c.getImageData(0,0,240,200).data;let h=2166136261;for(let i=0;i<px.length;i+=4){h^=px[i]+px[i+1]*3+px[i+2]*7+px[i+3]*11;h=Math.imul(h,16777619)}return(h>>>0).toString(16)};
      for(const d of Object.keys(CH)){const fl=wfFlow(d);if(!fl)continue;fl.forEach((f,si)=>{if(!CH[d][f])return;const plating=f==='plate';const ty=WF_ST[plating?fl[si-1]:f].slot;const slot=R.slots.find(s=>s.type===ty);if(!slot)return;
        const at=(st,act,pas)=>{const n={id:-7,d,n:1,its:[{it:{want:0}}],seed:7,st,f,si,act0:1,act,pas0:1,pas,dur:2,slot,who:null};const sp=wfFoodSpot(n,slot);c.setTransform(1,0,0,1,0,0);c.clearRect(0,0,240,200);c.translate(120-sp.x,130-sp.y);chDrawFood(c,n,slot,sp,0,plating);return hashOf()};
        out[d+'.'+f]=plating?[at('work',1,0),at('work',.5,0),at('work',0,0)]:[at('work',1,1),CH[d][f].heat?at('cook',0,1):at('work',.5,1),at('ready',0,0)]})}return out})())"""))   # (a place without heat — the salad's board — is all hands: its middle is half way through them)
    for k, (h0, h1, h2) in looks.items():
        check(len({h0, h1, h2}) == 3, f'{k}: drawn differently at its start, when the hands are done and at its end: {[h0, h1, h2]}')
    check(set(looks) == set(beats), f'every place with its own beats was drawn: {sorted(set(beats) - set(looks))} missing')
    check(not g.errors, g.errors[:3]); g.close()


# ---------------------------------------------------------------- the one Jill (the user, 2026-10-09 #8)
# docs/v24/cooking_final_decisions_2026-10-09.txt: 「Jill 是一個人，不是外場一個 Jill、廚房另一個 Jill」 — 「驗收標準：在正常遊戲的任何時間點，
# 不可能存在兩個 Jill 同時工作。不要用單純隱藏其中一個角色的畫面來掩蓋問題，底層工作狀態也必須一致。」 Two checks run all through:
# every room drawn at once counts Jill (at most once, and only in the room she is in), and every frame a step of hers at a
# station may move on only while she is in the kitchen (her hands are where she is).
ONE_JILL = r"""window.__oj={bad:[],samples:0,cnt:0,rooms:{}};
{const DP=drawPerson;drawPerson=function(c,x,y,L,o){if(L===JILL_LOOK&&window.__ojOn)__oj.cnt++;return DP.apply(this,arguments)}}
{const U=update;update=function(dt){const before=R?wfList().filter(n=>n.who==='jill'&&n.st==='work').map(n=>[n,n.act]):[];U(dt);if(!R)return;const J=R.jill;
  for(const [n,a] of before)if(n.act<a-1e-9&&(J.room||'main')!=='kitchen')__oj.bad.push('her hands moved '+n.d+' on while she was in '+J.room+' (t='+R.t.toFixed(1)+')');
  if(R.jk)__oj.bad.push('a second Jill (R.jk)');__oj.rooms[J.room||'main']=1}}
window.__ojLook=function(){if(!R)return 0;const keep=room;const rooms=[...new Set(['main','kitchen',...roomsOpen()])];let tot=0;const where=[];
  for(const k of rooms){room=k;__oj.cnt=0;window.__ojOn=1;try{drawScene(performance.now()/1000)}finally{window.__ojOn=0}if(__oj.cnt){tot+=__oj.cnt;where.push(k+':'+__oj.cnt)}}
  room=keep;forceDraw=true;__oj.samples++;const J=R.jill;const at=J.rest==='sit'?'home':(J.room||'main');
  if(tot>1)__oj.bad.push('Jill drawn '+tot+' times at once: '+where.join(' ')+' (she is in '+at+', t='+R.t.toFixed(1)+')');
  if(tot===1&&!where[0].startsWith(at+':'))__oj.bad.push('Jill drawn in '+where[0]+' while she is in '+at+' (t='+R.t.toFixed(1)+')');
  return tot};
window.__ojRun=function(n,look){for(let i=0;i<n;i++){for(const q of R.groups)q.pat=1;__tick(1000/30);if(look&&i%look===0)__ojLook()}}"""


@test
def cooking_one_jill_finishes_her_step_then_goes_and_nothing_of_hers_moves_on_while_she_is_away(b, port, target):
    """The one Jill, step by step (the user, 2026-10-09 #8): sent to a dirty table while her hands are on the wok, she finishes
    that step first (「需要跨房間工作時，先妥善處理目前工作」), then walks out of the kitchen by its door; while she is out the
    rice goes on cooking by itself (「烤箱烘烤、燉煮等工作可以依原有規則繼續計時」) and the plating she is given waits for her
    — nothing of hers is done by an unseen second Jill; she takes the plates from the table to the tub, comes back and plates
    it. Saved and read back while she is out, it all comes back and ends the same. Drawn once, in the room she is in."""
    g = _day(b, port, target, 7131)
    check(_wait_orders(g, 1), 'a table orders fried rice')
    g.ev(ONE_JILL)
    check(_until(g, "!R.jill.cur&&!R.jill.q.length", step=3), 'her table work done first')
    nid = g.ev("(()=>{wfGather();const n=wfList().find(n=>n.d==='friedrice'&&wfOpen(n));if(!n)return null;R.wsel=n.id;return wfAssign(n,'jill',R.slots.find(s=>s.type==='stove'&&s.no===1))?n.id:null})()")
    check(nid, 'the fried rice given to Jill at the first burner')
    N = f"wfNode({nid})"
    rooms = []
    for _ in range(900):
        g.ev("__ojRun(1,1)")
        r = g.ev("R.jill.room||'main'")
        if not rooms or rooms[-1] != r: rooms.append(r)
        if g.ev(f"(()=>{{const n={N};return n.st==='work'&&wfHere(n)}})()"): break
    check(rooms[-1] == 'kitchen' and 'main' in rooms, f'she walked in by the door from the dining room: {rooms}')
    act0 = g.ev(f"{N}.act")
    check(act0 > 0.2, f'her hands on it: {act0}')
    g.ev("(()=>{let t=R.tables.find(t=>!t.group);if(!t){const q=R.groups.find(q=>q.table!=null&&!(q.ticket&&q.ticket.items.some(it=>it.d==='friedrice')));t=R.tables[q.table];leaveGroup(q,'ok')}t.dirty=true;t.plates=['plate','cup'];window.__ojT=t.i;tapTable(t)})()")
    check(g.ev("R.jill.q.includes(window.__ojT)"), 'sent to a dirty table while she works the wok')
    left_at = None
    for _ in range(600):
        g.ev("__ojRun(1,2)")
        st, room_ = g.ev(f"{N}.st"), g.ev("R.jill.room||'main'")
        if room_ != 'kitchen':
            left_at = st; break
    check(left_at == 'cook', f'she left only once the hands of the step were done (the rice cooking by itself): {left_at}')
    pas0 = g.ev(f"{N}.pas")
    g.ev("__ojRun(20,5)")
    check(g.ev("R.jill.room||'main'") != 'kitchen' and g.ev(f"{N}.pas") < pas0, 'out of the kitchen, the rice goes on cooking')
    check(_until(g, f"{N}.st==='ready'", step=3), 'done on the fire, waiting')
    g.ev(f"wfAssign({N},'jill')")
    check(g.ev(f"{N}.who") == 'jill' and g.ev(f"wfState({N})").find('接著做') >= 0 or g.ev("R.jill.room") == 'kitchen', f'plating given to her while she is out: 「接著做」 on the card: {g.ev(f"wfState({N})")!r}')
    # saved and read back while she is out
    snap = g.ev("JSON.stringify(snapshotService())")
    g.ev(f"(()=>{{restoreService({{day:S.day,snap:JSON.parse({json.dumps(snap)})}})}})()")   # (the counting wraps the game's functions, not R: it carries on over the reload)
    check(g.ev(f"R.jill.wq.includes({nid})") and g.ev(f"{N}.who") == 'jill', 'read back: the plating is still hers, in her queue')
    for _ in range(1500):
        g.ev("__ojRun(3,5)")
        if g.ev(f"!{N}"): break
    check(g.ev(f"!{N}"), 'she came back and plated it')
    rd = g.ev("R.tickets.flatMap(tk=>tk.items).filter(it=>it.d==='friedrice'&&(it.st==='ready'||it.st==='served')).length")
    check(rd >= 1, f'the plate is on the pass (or out): {rd}')
    check(g.ev("ddS().n.length+(ddS().wash?1:0)+(ddS().done||0)") >= 0 and not g.ev("R.tables[window.__ojT].dirty"), 'the dirty table was cleared, its plates taken to the tub')
    bad = g.ev("__oj.bad.slice(0,6)"); n = g.ev("__oj.samples")
    check(not bad and n >= 40, f'drawn once, in her room, and nothing of hers moved on away from her ({n} looks): {bad}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def cooking_one_jill_through_whole_evenings_early_middle_late(b, port, target):
    """The one Jill over whole evenings played by the test player (the kitchen and the floor both asking for her): a new game's
    first day, the player's Day 30 save (five cooks, the cold station, the oven) and the Day 92 save (the whole crew, the
    Lounge, the second floor). Every look at every room at once finds one Jill at most, in the room she is in; no step of hers
    moves on while she is away from it; no second Jill exists; and each evening closes (nobody stuck)."""
    import v24_tests as v
    for name, save in (('day 1', None), ('day 30', 'player_day30.json'), ('day 92', 'player_day92_2105.json')):
        g = Game(b, port, target, seed=7140, manual=True, viewport={'width': 390, 'height': 844})
        if save:
            v.load_save(g, save)
            g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}"); v.to_service(g, lazy=False)
        else:
            g.click('[data-act=open]'); g.page.wait_for_timeout(80); start_day(g); _rt.install_bot(g)
        g.ev(ONE_JILL)
        for _ in range(400):
            r = json.loads(g.ev("(()=>{const o=__bot(45,1/30);if(R&&phase==='service')__ojLook();return JSON.stringify(o)})()"))
            if g.ev("phase") != 'service' or r['ticks'] < 45: break
        bad = g.ev("__oj.bad.slice(0,6)"); n = g.ev("__oj.samples"); rooms = g.ev("Object.keys(__oj.rooms)")
        check(g.ev("phase") != 'service', f'{name}: the evening closed')
        check(not bad and n >= 50, f'{name}: one Jill, in her room, her hands only where she is ({n} looks, rooms {rooms}): {bad}')
        check('kitchen' in rooms and 'main' in rooms, f'{name}: she was in the kitchen and in the dining room: {rooms}')
        check(not g.errors, f'{name}: {g.errors[:3]}'); g.close()


@test
def cooking_the_teaching_card_is_quiet(b, port, target):
    """The user, 2026-10-09 #1 (docs/v24/cooking_final_decisions_2026-10-09.txt): the white card no longer comes up on every
    tap of an order. The first time a dish is picked it comes once (with how to send Jill), and goes by itself after about
    four seconds; its × puts it away at once; picked again, the dish brings no card (what was taught is kept with the save,
    not reset by a day); the 說明 chip brings it whenever the player asks; two taps in a row that do nothing with the picked
    dish bring it back for a moment. Neither the card nor the chip is over a station, nor over the fridge."""
    g = _day(b, port, target, 7151, "S.menu=['friedrice'];S.eq.bar=1;")
    check(_wait_orders(g, 1), 'a fried rice ordered')
    vis = "(()=>{const e=document.querySelector('#wfGuide');return !!e&&!e.hidden})()"
    chip = "(()=>{const e=document.querySelector('#wfHelp');return !!e&&!e.hidden})()"
    g.click('#tickets .it.pending'); g.page.wait_for_timeout(60); g.ev("__tick(1000/30)")
    check(g.ev(vis) and 'Jill 就走過去做' in g.ev(GUIDE), f'the first time the dish is picked: the card, with how to send Jill: {g.ev(GUIDE)!r}')
    check(g.ev("S.wfTaught&&S.wfTaught.friedrice") == 1, 'taught: kept in the save')
    for _ in range(140): g.ev("for(const q of R.groups)q.pat=1;__tick(1000/30)")
    check(not g.ev(vis) and g.ev(chip), 'after about four seconds it goes by itself; the 說明 chip is there')
    g.click('#tickets .it.wsel'); g.ev("__tick(1000/30)")
    check(not g.ev(vis) and not g.ev(chip) and g.ev("R.wsel") is None, 'unpicked: no card, no chip')
    g.click('#tickets .it.pending'); g.page.wait_for_timeout(60); g.ev("__tick(1000/30)")
    check(not g.ev(vis) and g.ev(chip), 'picked again: no card (taught), only the chip')
    g.click('#wfHelp'); g.ev("__tick(1000/30)")
    check(g.ev(vis), 'the chip brings the card')
    g.click('#wfGuide .wgx'); g.ev("__tick(1000/30)")
    check(not g.ev(vis), 'its × puts it away at once')
    # two taps in a row on a place this dish cannot go (the coffee machine): the card again
    check(g.ev("R.slots.some(s=>s.type==='bar')"), 'a coffee machine to tap by mistake')
    if True:
        _tap_slot(g, "R.slots.find(s=>s.type==='bar')"); g.ev("__tick(1000/30)")
        check(not g.ev(vis), 'one tap that does nothing: no card yet')
        _tap_slot(g, "R.slots.find(s=>s.type==='bar')"); g.ev("__tick(1000/30)")
        check(g.ev(vis), 'the second in a row: the card comes back for a moment')
    # where they are: never over a station, nor over the fridge
    g.ev("wfGuideShow(wfNode(R.wsel),'ask')"); g.ev("__tick(1000/30)")
    over = json.loads(g.ev("""JSON.stringify((()=>{const out=[];const box=q=>{const e=document.querySelector(q);if(!e||e.hidden)return null;return e.getBoundingClientRect()};
      const B=[box('#wfGuide'),box('#wfHelp')].filter(Boolean);const cr=sc.getBoundingClientRect();
      const pts=R.slots.map(s=>{const o=wfSlotCenter(s);return{k:s.type+s.no,x:o.x,y:o.y}});const F=KR.fridge;pts.push({k:'fridge',x:F.x+F.w/2,y:F.y+F.h/2});
      for(const p of pts){const x=cr.left+SV.ox+p.x*SV.s,y=cr.top+SV.oy+p.y*SV.s;for(const b of B)if(x>=b.left&&x<=b.right&&y>=b.top&&y<=b.bottom)out.push(p.k)}return out})())"""))
    check(not over, f'the card and the chip are over no station and not over the fridge: {over}')
    # kept with the save: a new day does not teach the fried rice again
    g.ev("save()")
    check(json.loads(g.ev("localStorage.getItem(KEY)")).get('wfTaught', {}).get('friedrice') == 1, 'what was taught is in the saved game')
    check(not g.errors, g.errors[:3]); g.close()


@test
def cooking_the_pizza_oven_is_clear_of_the_buttons(b, port, target):
    """The user, 2026-10-09 #14: the pizza oven on the kitchen's back wall was covered on a phone by the room tabs (房間, over
    its dome) and by 今日任務 (over the dome, just above the mouth). On the three phone sizes measured, with the evening's
    buttons all showing, the oven — dome, mouth, the shelf it stands on — is clear of every one of them; 今日任務 in the
    kitchen sits beside 庫存, and back on the right in the dining room."""
    import v24_tests as v
    for vw, vh in ((375, 667), (390, 844), (430, 932)):   # a page of its own for each size: the scene's scale is set when the page is laid out
        g = Game(b, port, target, seed=7161, manual=True, viewport={'width': vw, 'height': vh})
        v.load_save(g, 'player_day92_2105.json')
        g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}"); v.to_service(g)
        g.ev("S.rooms=S.rooms||{};S.rooms.pizzaoven=1;__botUntil('false',60,1/30)")
        g.ev("setRoom('kitchen');renderTasks();renderRoomTabs(true);forceDraw=true;__tick(1000/30)"); g.page.wait_for_timeout(60)
        r = json.loads(g.ev("""JSON.stringify((()=>{const P=pizzaOvenRect();const cv=sc.getBoundingClientRect();const o={x0:cv.left+SV.ox+(P.x-4)*SV.s,x1:cv.left+SV.ox+(P.x+P.w+4)*SV.s,y0:cv.top+SV.oy+P.y*SV.s,y1:cv.top+SV.oy+(P.my+6)*SV.s,shown:[],bad:[]};
          for(const id of['roomTabs','stockChip','taskChip','logChip']){const e=document.getElementById(id);if(!e||e.hidden)continue;const r=e.getBoundingClientRect();if(!r.width)continue;o.shown.push(id);
           const ox=Math.min(o.x1,r.right)-Math.max(o.x0,r.left),oy=Math.min(o.y1,r.bottom)-Math.max(o.y0,r.top);if(ox>1&&oy>1)o.bad.push([id,Math.round(ox),Math.round(oy)])}return o})())"""))
        check(set(r['shown']) >= {'roomTabs', 'stockChip', 'taskChip'}, f'{vw}×{vh}: the buttons are there to be checked: {r["shown"]}')
        check(r['y0'] < 260 and r['y1'] > r['y0'], f'{vw}×{vh}: the oven is near the top of the screen, where the buttons are: {r}')
        check(not r['bad'], f'{vw}×{vh}: the pizza oven under a button: {r["bad"]}')
        tl = g.ev("(()=>{const t=document.getElementById('taskChip').getBoundingClientRect(),s=document.getElementById('stockChip').getBoundingClientRect();return t.left>s.right&&Math.abs(t.top-s.top)<2})()")
        check(tl, f'{vw}×{vh}: in the kitchen 今日任務 sits beside 庫存')
        g.ev("setRoom('main');renderRoomTabs(true);__tick(1000/30)")
        check(g.ev("(()=>{const t=document.getElementById('taskChip').getBoundingClientRect();return t.right>=innerWidth-12})()"), f'{vw}×{vh}: in the dining room it is back on the right')
        check(not g.errors, g.errors[:3]); g.close()


@test
def cooking_the_bar_kitchens_burner_has_a_place_of_its_own(b, port, target):
    """The user, 2026-10-09 #15B: the Bar 小廚's burner, which really heats food, is one of the hot zone's places, with the same
    rules as the others — and counted once. It was counted once in the number (stoveSlots: one more) but not in the room:
    its slot sat on another burner's spot (the fifth on the third, the seventh on the fourth), two pans on one fire and one cook
    in the other's place. Now every burner has its own spot (one more across the front row, a little smaller), on the range
    as it is and on the expanded range; without the Bar 小廚 nothing moved. A dish on its burner cooks like on any other."""
    g = _day(b, port, target, 7341)
    out = json.loads(g.ev("""(()=>{const r=[];const S0=JSON.stringify({eq:S.eq,ops:S.ops,rooms:S.rooms,level:S.level});
      for(const kext of [0,1])for(const pantry of [0,1])for(const lv of [1,2,3,4,5]){S.level=5;S.eq.stove=lv;S.ops=S.ops||{};S.ops.pantry=pantry;S.rooms=S.rooms||{};S.rooms.kext=kext;
        const n=stoveSlots(lv);const pos=[];for(let i=1;i<=n;i++){const h=slotHome({type:'stove',no:i});pos.push([h.x,h.y,h.sc])}r.push({kext,pantry,lv,n,pos})}
      const o=JSON.parse(S0);Object.assign(S,{eq:o.eq,ops:o.ops,rooms:o.rooms,level:o.level});return JSON.stringify(r)})()"""))
    for c in out:
        keys = {(p[0], p[1]) for p in c['pos']}
        check(len(keys) == c['n'], f'every burner its own spot: {c}')
        xs = sorted(p[0] for p in c['pos'] if p[1] == 186)
        check(all(b2 - a2 >= 38 for a2, b2 in zip(xs, xs[1:])), f'the front row is not crowded on top of itself: {c}')
    plain = {(c['kext'], c['lv']): c['pos'] for c in out if not c['pantry']}
    rx = g.ev("KX_BASE.range.x")   # (2026-10-09: the range moved right for the walkway through the line — the burners keep their places on it)
    old = {(0, lv): [[rx + [32, 96][i % 2], 186 if i < 2 else 160, .62] for i in range(n)] for lv, n in ((1, 1), (2, 2), (3, 3), (4, 3), (5, 4))}
    check(all(plain[k] == v for k, v in old.items()), f'without the Bar 小廚 the range is as it was: {plain}')
    # a dish on the Bar 小廚's burner (the last one) cooks like on any other
    g.ev("S.level=5;S.eq.stove=5;S.ops=S.ops||{};S.ops.pantry=1;R=null;phase='prep'")
    g.close()
    g = _day(b, port, target, 7342, "S.level=5;S.eq.stove=5;S.ops=S.ops||{};S.ops.pantry=1;S.menu=['friedrice'];")
    check(g.ev("R.slots.filter(s=>s.type==='stove').length") == 5, 'five burners: four and the Bar 小廚\'s')
    check(_wait_orders(g, 1), 'a table orders fried rice')
    g.ev("for(const s of R.slots)if(s.type==='stove'&&s.no<5)s.broken=true")   # (the other four out of use: the fifth is the one free)
    g.ev("wfGather()")
    nid = g.ev("(wfList().find(n=>n.d==='friedrice')||{}).id")
    ok = g.ev(f"wfAssign(wfNode({nid}),'jill',R.slots.find(s=>s.type==='stove'&&s.no===5))")
    check(ok is True and g.ev(f"(wfNode({nid}).slot||wfNode({nid}).to).no") == 5, f'Jill puts it on the fifth burner: {ok}')
    at5 = False
    for _ in range(600):
        g.ev("__run(3)")
        if g.ev(f"!!wfNode({nid})&&!!wfNode({nid}).slot&&wfNode({nid}).slot.no===5&&wfNode({nid}).st==='cook'"): at5 = True
        if g.ev(f"!wfNode({nid})||wfNode({nid}).si>0||wfNode({nid}).st==='ready'"): break
    check(at5 and g.ev(f"!wfNode({nid})||wfNode({nid}).si>0||wfNode({nid}).st==='ready'"), f'it cooked there: {at5}, {g.ev(f"JSON.stringify(wfNode({nid})&&wfState(wfNode({nid})))")}')
    check(not g.errors, g.errors[:3]); g.close()


WALKS = r"""(()=>{const boxes=kitchenObs(),hard=boxes.slice(0,2);   /* the line and the pass: nobody's feet ever inside them */
 const inside=(o,x,y,m)=>x>o.bx0+m&&x<o.bx1-m&&y>o.by0+m&&y<o.by1-m;
 const walk=(a,b)=>{const e={x:a[0],y:a[1],room:'kitchen'};let len=0,bad=null;for(let i=0;i<3000;i++){const w=obsNext(e,'kitchen',b[0],b[1]);const tx=w?w.x:b[0],ty=w?w.y:b[1];const dx=tx-e.x,dy=ty-e.y,d=Math.hypot(dx,dy),v=3;
   if(d<=v){e.x=tx;e.y=ty;len+=d}else{e.x+=dx/d*v;e.y+=dy/d*v;len+=v}
   for(const o of hard)if(!inside(o,a[0],a[1],-1)&&!inside(o,b[0],b[1],-1)&&inside(o,e.x,e.y,1)&&!bad)bad=[Math.round(e.x),Math.round(e.y)];
   if(Math.abs(e.x-b[0])<.01&&Math.abs(e.y-b[1])<.01)return{ok:1,len,bad}}return{ok:0,len,bad}};
 const P={door:[KR.door.x,KR.door.y],room:[homeKDoor().x,homeKDoor().y],drop:[ddDrop().x,ddDrop().y],take:[ddTake().x,ddTake().y],sink:[ddSink().x,ddSink().y],rack:[wfRack().x,wfRack().y],pick:[WF_PICK.x,WF_PICK.y]};
 WF_PASS_X.forEach((x,i)=>P['pass'+i]=[x,KY.passFeet]);
 for(const s of R.slots){const sp=wfSpot(s);P[s.type+s.no]=[sp.cx,sp.cy];const h=slotHome(s);if(h.y>=165)P[s.type+s.no+'f']=[h.x-44,KY.top+KY.h+KY.face+4]}
 const K=Object.keys(P),out={n:0,stuck:[],through:[],worst:0,worstK:''};
 for(const a of K)for(const b of K){if(a===b)continue;const r=walk(P[a],P[b]);out.n++;if(!r.ok)out.stuck.push(a+'→'+b);if(r.bad)out.through.push(a+'→'+b+' at '+r.bad);
   const st=Math.hypot(P[b][0]-P[a][0],P[b][1]-P[a][1]);const extra=r.len-st;if(extra>out.worst){out.worst=Math.round(extra);out.worstK=a+'→'+b}}
 return JSON.stringify(out)})()"""


@test
def cooking_people_walk_round_the_counters(b, port, target):
    """The user, 2026-10-09 #13: 「角色不能直接穿越流理台、工作檯、爐具等實體設備。優先使用既有路徑或加入必要的簡單轉折點，使人物
    自然繞過設備。不需要重建大型尋路系統。同時確認修改不會使員工被卡住、繞遠路過度增加出餐時間，或無法到達工作站。」 The kitchen has a
    floor plan for the Staff Room's rounding (kitchenObs → obsNext): the line (its cooks behind it), the pass, the cart, the crates
    and the bin, the fridge and the cold room. On every kitchen the game builds (Day 1, the middle game, the expanded range, the
    longer pass, kitchen II, the pizza oven, the Bar 小廚): from every place people stand to every other (the door, the door to
    Jill's room, each station from behind and from the front, the pass, the cart, the sink, the rack) the walk gets there, never
    with its feet inside the line or the pass, and never more than a counter's length out of its way. In play (the user's Day 52
    save, a whole evening): nobody's feet inside the line or the pass, Jill's, the cooks', the cleaners' and the waiters'."""
    layouts = [('Day 1', ''),
               ('middle', "S.level=3;S.eq.stove=3;S.eq.prep=1;S.eq.oven=1;S.eq.bar=2;"),
               ('expanded range, longer pass, walk-in', "S.level=5;S.eq.stove=5;S.eq.prep=2;S.eq.oven=3;S.eq.bar=3;S.rooms=S.rooms||{};S.rooms.kext=1;S.rooms.pass=1;S.rooms.cooler=1;S.rooms.walkin=1;"),
               ('kitchen II, pizza oven, Bar 小廚', "S.level=5;S.eq.stove=5;S.eq.prep=2;S.eq.oven=3;S.eq.bar=3;S.rooms=S.rooms||{};S.rooms.kext=1;S.rooms.kitchen2=1;S.rooms.pizzaoven=1;S.rooms.lounge=3;S.ops=S.ops||{};S.ops.pantry=1;")]
    for name, setup in layouts:
        g = _day(b, port, target, 7351, setup)
        r = json.loads(g.ev(WALKS))
        check(r['n'] > 100 and not r['stuck'], f'{name}: every place reaches every other: {r["stuck"][:5]} of {r["n"]}')
        check(not r['through'], f'{name}: no walk through the line or the pass: {r["through"][:5]}')
        check(r['worst'] <= 420, f'{name}: never more than a counter\'s length out of the way: {r["worst"]} ({r["worstK"]})')
        check(not g.errors, g.errors[:3]); g.close()
    # in play
    import v24_tests as v
    g = Game(b, port, target, seed=7352, manual=True, viewport={'width': 390, 'height': 844})
    v.load_save(g, 'player_day52.json')
    g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}"); v.to_service(g, lazy=True)
    g.ev("""window.__in=[];window.__inStep=function(n){const H=()=>kitchenObs().slice(0,2);const ins=(o,x,y)=>x>o.bx0+1&&x<o.bx1-1&&y>o.by0+1&&y<o.by1-1;let k=0;
      for(let i=0;i<n;i++){if(!__act())break;update(1/30);updateCats(1/30,0);k++;if(!R||phase!=='service')break;const hb=H();const who=[];const J=R.jill;if((J.room||'main')==='kitchen')who.push(['jill',J]);for(const id in R.ck||{})who.push(['cook '+id,R.ck[id]]);for(const id in R.cw||{}){const w=R.cw[id];if(w&&w.room==='kitchen')who.push([id,w])}if(R.xqh&&R.xqh.room==='kitchen')who.push(['xq',R.xqh]);
        for(const [nm,e] of who)for(const o of hb)if(ins(o,e.x,e.y)&&__in.length<20)__in.push([nm,Math.round(e.x),Math.round(e.y),Math.round(R.t)])}return k}""")
    for _ in range(3000):
        if g.ev("phase") != 'service' or not g.ev("!!R"): break
        if g.page.evaluate('()=>window.__inStep(60)') < 60: break
    check(g.ev("__in.length") == 0, f'in play nobody stands in the line or the pass: {g.ev("JSON.stringify(__in)")}')
    check(not g.errors, g.errors[:3]); g.close()
