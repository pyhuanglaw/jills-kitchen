"""The user's own save (Day 3, 18:33, a latte made and waiting at the coffee machine since 18:2x): resumed as the title's
OPEN does, on a given build; then the player's taps on the machine. python3 tools/qa/user_save_latte.py WORKTREE SAVE OUT"""
import sys, os, json
wt, savef, out = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out, exist_ok=True); sys.path.insert(0, os.path.join(wt, 'tests')); os.chdir(wt)
import run_tests as rt
from playwright.sync_api import sync_playwright
raw = json.load(open(savef, encoding='utf-8')); raw = raw.get('save', raw)
NODE = "JSON.stringify((()=>{const n=(R.wf||[]).find(n=>n.id===8);if(!n){const it=R.tickets.flatMap(t=>t.items).filter(i=>i.d==='coffee');return{gone:1,items:it.map(i=>[i.st,i.pi])}}const J=wfJ();return{st:n.st,f:n.f,next:wfNext(n),who:n.who,slot:n.slot&&n.slot.type,J:[Math.round(J.x),Math.round(J.y)],cue:wfCueSlots(n).free.map(s=>s.type),guide:((document.querySelector('#wfGuide')||{}).innerText||'').replace(/\\n/g,' / ')}})())"
srv, port = rt.start_server()
with sync_playwright() as p:
    b = p.chromium.launch()
    _nc = b.new_context
    b.new_context = lambda **kw: _nc(**dict(kw, device_scale_factor=3))
    g = rt.Game(b, port, 'index', seed=1, manual=True, viewport={'width': 390, 'height': 844})
    g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.page.wait_for_timeout(200)
    print('title:', g.ev("(document.querySelector('#screen .title .cont')||{}).textContent||''"))
    g.click('[data-act=open]'); g.page.wait_for_timeout(200)
    for _ in range(30):
        if g.ev("typeof DLG!=='undefined'&&!!DLG"): g.ev("dlgNext()")
    print('phase', g.ev("phase"), 'clock', g.ev("R&&clockStr?clockStr():''") if g.ev("typeof clockStr==='function'") else '')
    g.ev("setRoom('kitchen');R.wsel=8;renderTickets();wfGuideUpd();forceDraw=true;__tick(1000/30)"); g.page.wait_for_timeout(80)
    print('resumed:', g.ev(NODE))
    g.page.screenshot(path=os.path.join(out, 'U1_resumed_latte_waiting.png'))
    food = json.loads(g.ev("JSON.stringify((()=>{const n=wfNode(8);return wfFoodSpot(n,n.slot)})())"))
    o = json.loads(g.ev("JSON.stringify((()=>{const r=sc.getBoundingClientRect();return{x:r.left+SV.ox+%f*SV.s,y:r.top+SV.oy+%f*SV.s}})())" % (food['x'], food['y'] - 6)))
    g.page.mouse.click(o['x'], o['y']); g.page.wait_for_timeout(40)
    g.ev("for(let i=0;i<2;i++){for(const q of R.groups)q.pat=1;__tick(1000/30)}")
    print('after the tap:', g.ev(NODE))
    states = []
    for _ in range(600):
        g.ev("for(const q of R.groups)q.pat=1;__tick(1000/30)")
        s = json.loads(g.ev(NODE)); k = s.get('st') or 'gone'
        if not states or states[-1] != k:
            states.append(k)
            g.ev("forceDraw=true;__tick(1000/30)"); g.page.wait_for_timeout(40)
            g.page.screenshot(path=os.path.join(out, 'U_%d_%s.png' % (len(states), k)))
        if s.get('gone'): print('done:', s); break
    print('states:', states)
    # the floor: the player taps the table whose latte it is (Jill serves it)
    tk = g.ev("(()=>{const tk=R.tickets.find(t=>t.items.some(i=>i.d==='coffee'&&i.st==='ready'));return tk?tk.g&&tk.g.table:null})()")
    print('table waiting for the latte:', tk)
    if tk is not None:
        g.ev("setRoom('main');forceDraw=true;__tick(1000/30)"); g.page.wait_for_timeout(60)
        t = json.loads(g.ev("JSON.stringify((t=>({x:t.x,y:t.y}))(R.tables[%d]))" % tk))
        o = json.loads(g.ev("JSON.stringify((()=>{const r=sc.getBoundingClientRect();return{x:r.left+SV.ox+%f*SV.s,y:r.top+SV.oy+%f*SV.s}})())" % (t['x'], t['y'])))
        g.page.mouse.click(o['x'], o['y']); g.page.wait_for_timeout(40)
        for _ in range(900):
            g.ev("for(const q of R.groups)q.pat=1;__tick(1000/30)")
            if g.ev("R.tickets.flatMap(t=>t.items).filter(i=>i.d==='coffee'&&i.st==='served').length>0") or g.ev("!R.tickets.some(t=>t.items.some(i=>i.d==='coffee'&&i.wf===8))&&R.st.dish&&R.st.dish.coffee>0"): break
        print('served to the guest:', g.ev("JSON.stringify({coffee:(R.st.dish||{}).coffee||0,items:R.tickets.flatMap(t=>t.items).filter(i=>i.d==='coffee').map(i=>i.st)})"))
        g.ev("forceDraw=true;__tick(1000/30)"); g.page.wait_for_timeout(60)
        g.page.screenshot(path=os.path.join(out, 'U9_served.png'))
    print('errors', g.errors[:3]); g.close(); b.close()
srv.shutdown()
