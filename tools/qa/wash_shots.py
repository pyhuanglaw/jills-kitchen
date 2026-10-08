"""Acceptance 8–12 on a phone: six dirty dishes on the cart, the player taps the cart, someone walks to it, washes at the sink
one by one (the number goes down), is called away halfway, the rest stays. Kitchen, 390 wide, 3x.
python3 wash_shots.py WORKTREE OUT"""
import sys, os, json
wt, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True); sys.path.insert(0, os.path.join(wt, 'tests')); os.chdir(wt)
import run_tests as rt
from playwright.sync_api import sync_playwright
srv, port = rt.start_server()
with sync_playwright() as p:
    b = p.chromium.launch()
    _nc = b.new_context
    b.new_context = lambda **kw: _nc(**dict(kw, device_scale_factor=3))
    g = rt.Game(b, port, 'index', seed=3032, manual=True, viewport={'width': 390, 'height': 844})
    g.click('[data-act=open]'); g.page.wait_for_timeout(150)
    g.ev("S.day=6;S.level=2;S.tables=4;save()"); rt.start_day(g)
    g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}")
    g.ev("R.sched=[];R.si=0;setRoom('kitchen')")
    g.ev("for(let i=0;i<60;i++)__tick(1000/30)")
    g.ev("ddS().n=['plate','cup','plate','bowl','glass','plate'];R.tv++")
    C = json.loads(g.ev("JSON.stringify({c:ddCart(),s:ddSink()})"))
    def shot(name):
        g.ev("forceDraw=true;__tick(1000/30)"); g.page.wait_for_timeout(60)
        cx = (C['c']['x'] + C['s']['x']) / 2 + 20; cy = (C['c']['y'] + C['s']['y']) / 2
        r = json.loads(g.ev("JSON.stringify((()=>{const r=sc.getBoundingClientRect();return{x:r.left+SV.ox+%f*SV.s,y:r.top+SV.oy+%f*SV.s}})())" % (cx, cy)))
        g.page.screenshot(path=os.path.join(out, name + '.png'), clip={'x': max(0, r['x'] - 120), 'y': max(0, r['y'] - 130), 'width': 240, 'height': 230})
        st = json.loads(g.ev("JSON.stringify({n:ddCount(),cart:ddS().n.length,wash:ddS().wash&&ddS().wash.who,ph:ddS().wash&&ddS().wash.ph})"))
        print(name, st, flush=True)
    shot('w0_six_on_the_cart')
    g.ev("ddTap()")   # the player's tap: Jill (no cleaner here) goes to wash
    for _ in range(12): g.ev("__tick(1000/30)")
    shot('w1_on_the_way')
    for i in range(200):
        g.ev("__tick(1000/30)")
        if g.ev("ddS().wash&&ddS().wash.ph==='sink'&&ddWasherAt()"): break
    for _ in range(8): g.ev("__tick(1000/30)")
    shot('w2_washing_at_the_sink')
    for i in range(400):
        g.ev("__tick(1000/30)")
        if g.ev("ddCount()<=3"): break
    shot('w3_three_left')
    # called away: the player sends Jill to the stove — she finishes the one in hand and goes; the rest waits on the cart
    g.ev("ddS().wash&&(ddS().wash.stop=1)")
    for i in range(300):
        g.ev("__tick(1000/30)")
        if not g.ev("!!ddS().wash"): break
    for _ in range(20): g.ev("__tick(1000/30)")
    shot('w4_left_halfway_the_rest_waits')
    print('errors', g.errors[:3])
    g.close(); b.close()
srv.shutdown()
