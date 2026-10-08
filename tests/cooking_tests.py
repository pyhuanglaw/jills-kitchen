"""The working kitchen (v2.5; the user's spec of 2026-10-07 — docs/v24/cooking_*.txt, docs/cooking/ARCHITECTURE.md).

Every dish is a short workflow over the kitchen's own places (備料, 熱區, 烤箱, 飲料, 披薩烤爐, 裝盤 at the pass); a batch of
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
def cooking_fried_rice_goes_hot_then_plating_by_taps(b, port, target):
    """The first dish of the new kitchen, by real taps (the user's prototype list, J1–J15): the ticket item selects its
    work (the card says ● 熱區 → ○ 裝盤, 下一步：熱區; the burner is lit); a tap on the burner sends Jill, who walks there; the
    rice is in the wok and cooks by itself, no tap in between; done, it waits on the fire (✓ 熱區 → ● 裝盤, 下一步：裝盤,
    the pass lit) for as long as it takes — nothing spoils; a tap on the pass and Jill plates it; the plate goes the old
    way (ready at the pass, carried, paid), with its XP."""
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
    check(g.ev("wfCueSlots(wfNode(R.wsel)).f") == 'plate' and g.ev("wfCueSlots(wfNode(R.wsel)).free.length") == 1, 'the pass is cued')
    g.ev("__run(600)")   # twenty seconds of nothing
    st = json.loads(g.ev("JSON.stringify((()=>{const n=wfNode(R.wsel);return{st:n.st,sc:n.sc,slot:n.slot&&n.slot.type}})())"))
    check(st['st'] == 'ready' and st['slot'] == 'stove' and st['sc'] == [1], f'twenty seconds later it is still waiting on the fire, nothing lost: {st}')
    check(not any(w in g.ev(GUIDE) for w in ('秒', '%', '焦', '快')), 'the card has no timer, no score, no hurry')
    pp = json.loads(g.ev("JSON.stringify(wfSpot(wfPassSlots()[0]))"))
    _tap_scene(g, pp['x'], pp['y'] - 2)
    check(g.ev("wfNode(R.wsel)&&wfNode(R.wsel).st") in ('fetch', 'go'), 'the pass tapped: Jill goes to fetch it')
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
    st = json.loads(g.ev(f"JSON.stringify((()=>{{const n=wfNode({nid});return{{who:n.who,st:n.st,si:n.si,to:n.to&&n.to.no,its:n.its.map(o=>o.it.st),cook:(R.wfc||{{}}).t_ade||null,q:wfJ().q,ck:n.ck||[]}}}})())"))
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
    飲料 at the coffee machine, 披薩烤爐 in the pizza oven, 裝盤 at the pass, 出杯 set down for the floor — and, made by
    Jill, it is Perfect. A special goes its base dish's way."""
    g = _day(b, port, target, 7130, ALL_PLACES)
    ids = g.ev("Object.keys(DISHES).concat(['signature','sigdessert']).filter(isWF)")
    want_slot = {'prep': 'prep', 'hot': 'stove', 'oven': 'oven', 'drink': 'bar', 'pizza': 'pizza', 'plate': 'pass', 'serve': 'pick'}
    bad, seen_fams = {}, set()
    for d in ids:
        r = json.loads(g.ev(f"JSON.stringify(({WALK})({json.dumps(d)}))"))
        exp = [want_slot[f] for f in (r.get('flow') or [])]
        if r.get('err') or r.get('places') != exp or r.get('q') != 'P':
            bad[d] = r
        seen_fams.add(tuple(r.get('flow') or []))
    check(not bad, f'dishes off their workflow, or not Perfect from Jill: {bad}')
    check(len(seen_fams) == 7, f'all seven workflows are on the new kitchen: {sorted(seen_fams)}')
    sp = g.ev("Object.keys(SPECIALS).filter(b=>isWF(b)).every(b=>JSON.stringify(wfFlow(SPECIALS[b].id))===JSON.stringify(wfFlow(b)))")
    check(sp, 'a special goes its base dish\'s way')
    check(not g.errors, g.errors[:3]); g.close()
