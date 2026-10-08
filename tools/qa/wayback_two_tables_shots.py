"""The user's §45 picture in full, one waiter, one trip: plates for two tables from the pass → the second table → on the way
back TWO finished tables cleared → everything into the kitchen at once. The evening is stepped inside the page without
drawing (fast; the clock and the game's timers move with it, so toasts and lines come and go as in play); a frame is drawn only for a picture, with the game's seeded random set aside while it draws (so a picture
does not change what happens next). Day 30 save (the one the private page loads), phone size, 3x.
python3 tools/qa/wayback_two_tables_shots.py WORKTREE OUTDIR SEED...   (seed 4044: the pictures in docs/evidence/cooking_2026-10-08/screens/acceptance/s45_*)"""
import sys, os, json
wt, out = sys.argv[1], sys.argv[2]; SEEDS = [int(s) for s in sys.argv[3:]] or [3033]
os.makedirs(out, exist_ok=True); sys.path.insert(0, os.path.join(wt, 'tests')); os.chdir(wt)
import run_tests as rt, v24_tests as vt
from playwright.sync_api import sync_playwright
WATCH = r"""window.__wbw={};
window.__wbInfo=function(m){const w=R.cw[m.id]||{};const t=w.task;const H=w.hands||[];return{id:m.id,name:m.name,lv:m.lv,x:w.x,y:w.y,room:w.room||'main',k:t?t.k:null,ph:t?t.phase:null,
  stops:t&&t.stops?t.stops.length:0,dish:H.filter(e=>e.k==='dish').length,tabs:new Set(H.filter(e=>e.k==='dish').map(e=>e.tk.no)).size,dirty:H.filter(e=>e.k==='dirty').length,
  ct:t&&t.k==='clean'&&t.t?t.t.i:null,mv:!!w.moving}};
window.__wbStep=function(max){for(let n=0;n<max;n++){if(!(phase==='service'&&R))return{end:1};const r=__bot(1,1/30);__advance(1000/30);if(!r.ticks||!R||phase!=='service')return{end:1};
  for(const m of S.crew||[]){if(m.role!=='waiter'||!crewHere(m)||m.lv<3)continue;const w=__wbInfo(m);const T=__wbw[m.id];const pk=T?T.pk:null;let ev=null;
   if(!T||T.st===0){if(w.k==='serve'&&w.ph==='table'&&w.dish>=2&&w.tabs>=2&&w.mv){__wbw[m.id]={st:1,cl:[],pk:w.k};ev='1_two_tables_in_hand'}else{__wbw[m.id]={st:0,cl:[],pk:w.k}}}
   else if(T.st===1){if(w.k==='serve'&&w.ph==='table'&&w.stops===1&&w.mv){T.st=2;ev='2_on_to_the_second_table'}else if(w.k!=='serve')T.st=0}
   else if(T.st===2){if(pk==='serve'&&w.k==='clean'){T.st=3;T.cl=[w.ct]}else if(w.k!=='serve'||w.ph==='pickup')T.st=0}
   else if(T.st===3){if(w.k==='clean'&&w.ct!=null&&!T.cl.includes(w.ct)){T.cl.push(w.ct);ev='3_a_second_finished_table'}
     else if(w.k==='dump'&&T.cl.length>=2&&!T.d4&&w.room!=='kitchen'&&w.dirty>=2&&w.mv){T.d4=1;ev='4_both_tables_in_hand'}
     else if(w.k==='dump'&&T.cl.length>=2&&w.room==='kitchen'&&w.dirty>=2){T.st=9;ev='5_into_the_kitchen_at_once'}
     else if(w.k!=='clean'&&w.k!=='dump')T.st=0;else if(w.k==='dump'&&T.cl.length<2)T.st=0}
   if(T)T.pk=w.k;
   if(ev)return{ev,w,cl:(__wbw[m.id]||{}).cl,t:+R.t.toFixed(1)}}}
 return{}};
window.__wbDraw=function(rm){const keep=Math.random;Math.random=function(){return .5};const r0=room;try{if(rm!==room)setRoom(rm);drawScene(performance.now()/1000)}finally{Math.random=keep}return r0};
"""
srv, port = rt.start_server()
with sync_playwright() as p:
    b = p.chromium.launch()
    _nc = b.new_context
    b.new_context = lambda **kw: _nc(**dict(kw, device_scale_factor=3))
    done = None
    for SEED in SEEDS:
        g = rt.Game(b, port, 'index', seed=SEED, manual=True, viewport={'width': 390, 'height': 844})
        vt.load_save(g, 'player_day30.json')
        if g.ev("phase") != 'service': rt.start_day(g)
        rt.install_bot(g); g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;window.__noScenes=true")
        g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}")
        g.ev(WATCH)
        shots = {}   # waiter id -> list
        found = None
        for _ in range(4000):
            r = json.loads(g.ev("JSON.stringify(__wbStep(600))"))
            if r.get('end'): break
            if not r.get('ev'): 
                # drop the pictures of trips that did not go on
                for k in list(shots):
                    st = g.ev(f"(__wbw['{k}']||{{}}).st")
                    if st == 0: shots.pop(k)
                continue
            w = r['w']; ev = r['ev']
            if ev.startswith('1_'): shots[w['id']] = []
            r0 = g.ev(f"__wbDraw('{w['room']}')"); g.page.wait_for_timeout(40)
            o = json.loads(g.ev("JSON.stringify((()=>{const r=sc.getBoundingClientRect();return{x:r.left+SV.ox+%f*SV.s,y:r.top+SV.oy+%f*SV.s}})())" % (w['x'], w['y'])))
            cw, ch = 200, 170
            clip = {'x': max(0, min(390 - cw, o['x'] - cw / 2)), 'y': max(0, o['y'] - ch + 40), 'width': cw, 'height': ch}
            img = g.page.screenshot(clip=clip)
            # the same moment with the page's notes (toasts, banners: DOM over the canvas) set aside — kept apart, named _plain
            g.ev("window.__hid=[...document.body.querySelectorAll('*')].filter(e=>e!==sc&&!e.contains(sc)&&getComputedStyle(e).position!=='static'&&e.offsetParent!==null).map(e=>{const v=e.style.visibility;e.style.visibility='hidden';return[e,v]})")
            plain = g.page.screenshot(clip=clip)
            g.ev("for(const [e,v] of window.__hid)e.style.visibility=v")
            g.ev(f"if(room!=='{r0}')setRoom('{r0}')")
            shots.setdefault(w['id'], []).append((ev, img, w, r['t'], r.get('cl'), plain))
            if ev.startswith('5_'):
                found = shots[w['id']]; break
        print('seed', SEED, 'found', bool(found), 'errors', g.errors[:3], flush=True)
        g.close()
        if found:
            done = (SEED, found); break
    if done:
        for ev, img, w, t, cl, plain in done[1]:
            open(os.path.join(out, ev + '.png'), 'wb').write(img)
            open(os.path.join(out, ev + '_plain.png'), 'wb').write(plain)
            print(ev, 't', t, {k: w.get(k) for k in ('name', 'lv', 'room', 'k', 'ph', 'stops', 'dish', 'tabs', 'dirty', 'ct')}, 'cleared', cl, flush=True)
    b.close()
srv.shutdown()
