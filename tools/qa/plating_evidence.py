"""The user's plating evidence (2026-10-09): for a dish, by the player's taps, on a phone-size page (390 wide, 3x):
A the step before done, the food still at its place; B Jill with plates, walking to it; C at it — only now does plating
start; D the plated dish in her hands, walking to the pass; E on the pass. Checked as it goes: no plating before she is
there, the food leaves its vessel only while she is at it, the hands within reach of it.
python3 tools/qa/plating_evidence.py WORKTREE OUT DISH   (friedrice / salad / fries: docs/evidence/cooking_2026-10-08/screens/iphone_fixes/)"""
import sys, os, json
wt, out, DISH = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out, exist_ok=True); sys.path.insert(0, os.path.join(wt, 'tests')); os.chdir(wt)
import run_tests as rt
from playwright.sync_api import sync_playwright
SETUP = {'friedrice': (1, ""), 'salad': (3, ""), 'fries': (3, "S.eq.oven=1;if(!S.unlocked.includes('fries'))S.unlocked.push('fries');if(!S.menu.includes('fries'))S.menu.push('fries');S.stock.fries=12;")}
day, extra = SETUP[DISH]
FLOOR = "window.__f=function(){for(const q of queued())if(q.state==='queue'){const t=freeTableFor(q);if(t)seatGroup(q,t)}for(const t of R.tables){const q=t.group;if(q&&q.state==='order'&&!jillTargets(t.i))tapTable(t)}}"
srv, port = rt.start_server()
with sync_playwright() as p:
    b = p.chromium.launch()
    _nc = b.new_context
    b.new_context = lambda **kw: _nc(**dict(kw, device_scale_factor=3))
    g = rt.Game(b, port, 'index', seed=880 + day, manual=True, viewport={'width': 390, 'height': 844})
    g.click('[data-act=open]'); g.page.wait_for_timeout(80)
    if day > 1: g.ev(f"S.day={day};S.gate=1;applyGates();for(const d of menuList())S.stock[d]=12;S.tables=2;" + extra + "save()")
    rt.start_day(g); g.ev(FLOOR)
    g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}")
    tick = lambda n=1: g.ev(f"(n=>{{for(let i=0;i<n;i++){{for(const q of R.groups)q.pat=1;__tick(1000/30)}}}})({n})")
    def xy(x, y): return json.loads(g.ev("JSON.stringify((()=>{const r=sc.getBoundingClientRect();return{x:r.left+SV.ox+%f*SV.s,y:r.top+SV.oy+%f*SV.s}})())" % (x, y)))
    def tap(x, y): o = xy(x, y); g.page.mouse.click(o['x'], o['y']); g.page.wait_for_timeout(30); tick()
    tk = None
    for _ in range(1500):
        g.ev("__f();for(const q of R.groups)q.pat=1;__tick(1000/30)")
        tk = g.ev("(()=>{const t=R.tickets.find(t=>t.items.some(i=>i.st==='pending'));return t?t.id:null})()")
        if tk: break
    if not g.ev(f"R.tickets.find(t=>t.id==={tk}).items.some(i=>i.d==='{DISH}')"):
        g.ev(f"(()=>{{const t=R.tickets.find(t=>t.id==={tk});t.items.push({{d:'{DISH}',st:'pending',q:null,want:0,picked:false,set:null}});R.tv++}})()")   # (an order of it, for the evidence)
    idx = g.ev(f"R.tickets.find(t=>t.id==={tk}).items.findIndex(i=>i.d==='{DISH}'&&i.st==='pending')")
    g.ev("setRoom('kitchen');renderTickets()"); g.page.click(f'#tickets [data-tk="{tk}"][data-i="{idx}"]'); g.page.wait_for_timeout(30); tick()
    nid = g.ev("R.wsel")
    while True:   # each step before the plating, by taps on its lit place
        if g.ev(f"wfNext(wfNode({nid}))") == 'plate': break
        if g.ev(f"wfOpen(wfNode({nid}))"):
            c = json.loads(g.ev(f"JSON.stringify((()=>{{const n=wfNode({nid});const s=wfBestSlot(n,wfCueSlots(n));return s?wfSlotCenter(s):null}})())"))
            if g.ev("R.wsel") != nid: g.page.click(f'#tickets [data-tk="{tk}"][data-i="{idx}"]'); g.page.wait_for_timeout(30)
            tap(c['x'], c['y'])
        for _ in range(900):
            if g.ev(f"(n=>n.st==='ready'||wfOpen(n))(wfNode({nid}))"): break
            tick(3)
    food = json.loads(g.ev(f"JSON.stringify((()=>{{const n=wfNode({nid});const s=wfFoodSpot(n,n.slot);return{{x:s.x,y:s.y,slot:n.slot.type+n.slot.no,inOven:!!s.inOven}}}})())"))
    reach = json.loads(g.ev(f"JSON.stringify(wfReach(wfNode({nid})))"))
    def shot(name, cx, cy, w=230, h=200):
        g.ev("forceDraw=true;__tick(1000/30)"); g.page.wait_for_timeout(50)
        o = xy(cx, cy)
        g.page.screenshot(path=os.path.join(out, f'{DISH}_{name}.png'), clip={'x': max(0, min(390 - w, o['x'] - w / 2)), 'y': max(0, o['y'] - h * .62), 'width': w, 'height': h})
    STATE = f"JSON.stringify((()=>{{const n=wfNode({nid});const J=wfJ();if(!n)return{{gone:1,J:[J.x,J.y]}};const c=chState(n,'plate');return{{st:n.st,f:n.f,dishes:!!n.dishes,carry:!!n.carry,u:+wfHands(n).toFixed(2),out:c?+c.st.out.toFixed(2):null,J:[Math.round(J.x),Math.round(J.y)],moving:J.moving}}}})())"
    log = []
    g.ev(f"R.wsel={nid}"); shot('A_done_at_its_place', food['x'], food['y'])
    log.append(('A', json.loads(g.ev(STATE))))
    tap(food['x'], food['y'] - 6)                                   # the player taps the finished food
    got = set(); bad = []; first_work = None
    for i in range(1500):
        s = json.loads(g.ev(STATE))
        if s.get('gone'): break
        if s['st'] == 'tofood' and s['moving'] and s['dishes'] and 'B' not in got:
            got.add('B'); shot('B_plates_in_hand_walking_to_it', (s['J'][0] + food['x']) / 2, (s['J'][1] + food['y']) / 2); log.append(('B', s))
        if s['st'] in ('dish', 'tofood') and s['out'] not in (None, 0): bad.append(('plated before she was there', s))
        if s['st'] == 'work' and s['f'] == 'plate':
            if first_work is None:
                first_work = s; got.add('C'); shot('C_there_plating_starts', food['x'], food['y']); log.append(('C', s))
                if abs(s['J'][0] - reach['x']) > 3 or abs(s['J'][1] - reach['y']) > 3: bad.append(('plating started away from the food', s, reach))
            if 'C2' not in got and s['u'] >= .5:
                got.add('C2'); shot('C2_plating_half_way', food['x'], food['y']); log.append(('C2', s))
        if s['st'] == 'topass' and s['moving'] and 'D' not in got:
            got.add('D'); shot('D_plated_in_hand_to_the_pass', s['J'][0], s['J'][1] - 10); log.append(('D', s))
        tick(1)
    it = json.loads(g.ev(f"JSON.stringify((it=>({{st:it.st,pi:it.pi}}))(R.tickets.find(t=>t.id==={tk}).items[{idx}]))"))
    px = g.ev(f"wfRowX({it['pi']})") if it['pi'] is not None else 200
    shot('E_on_the_pass', px, 290); log.append(('E', it))
    hands = ((reach['x'] - food['x']) ** 2 + (reach['y'] - 33 - food['y']) ** 2) ** .5
    print(json.dumps({'dish': DISH, 'food': food, 'reach': reach, 'hands_to_food': round(hands), 'shots': sorted(got) + ['A', 'E'], 'bad': bad, 'errors': g.errors[:3]}, ensure_ascii=False))
    for l in log: print(l)
    g.close(); b.close()
srv.shutdown()
