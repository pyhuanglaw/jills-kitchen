"""One dish through its whole workflow on a phone-size page (390 wide, 3x), Jill alone: at each place, the moment work
begins (what it starts from) and the middle of each of the dish's own beats (CH: the hands' beats, then the heat's) — or,
for a dish without its own beats yet, 10 / 40 / 70 / 95% of the step; done and waiting where it was made; plating the same
way (each beat, or 30 / 70 / 98%); carried; on the pass. Each frame a crop around the food, labelled with the place and
the beat in words. One strip per dish (laid out by the browser, in the game's font): how the user's choreography spec
(docs/v24/cooking_choreography_2026-10-08.txt) is checked, dish by dish.
  python3 tools/qa/dish_frames.py WORKTREE OUT DISH [DISH ...]"""
import sys, os, json, html as H
wt, out = sys.argv[1], sys.argv[2]; DISHES = sys.argv[3:]
os.makedirs(out, exist_ok=True); sys.path.insert(0, os.path.join(wt, 'tests')); os.chdir(wt)
import run_tests as rt
from playwright.sync_api import sync_playwright
MK = r"""window.__mk=(ti,items)=>{const t=R.tables[ti];const o=rollGuest();const gg={id:R.gid++,type:o.type,size:1,reg:null,forSig:false,looks:makeLooks(o.type,1),name:pick(NAMES.office),state:'wait',table:ti,pat:.9,room:'main',troom:'main',x:t.x,y:t.y+8,tx:t.x,ty:t.y+8,timer:0,ticket:null,seed:ti+1,mood:'ok'};R.groups.push(gg);t.group=gg;
  const tk={id:R.tkid++,no:R.tickets.length+1,g:gg,items:items.map(d=>({d,st:'pending',q:null,want:0,picked:false})),t0:R.t};gg.ticket=tk;R.tickets.push(tk);R.tv++;renderTickets();return tk}"""
SETUP = """S.level=5;S.eq.stove=4;S.eq.oven=2;S.eq.bar=3;S.eq.prep=2;S.eq.fridge=4;for(const k of ['oven','prep','bar'])S.eq[k]=Math.max(S.eq[k],2);
 S.rooms=S.rooms||{};if(!S.unlocked.includes('%(d)s'))S.unlocked.push('%(d)s');if(!S.menu.includes('%(d)s'))S.menu.push('%(d)s');S.stock['%(d)s']=20;S.tut=1;%(extra)ssave()"""
EXTRA = {'pizza': "S.projs=S.projs||{};", 'pzmarg': "", 'pzfungi': ""}
STATE = "JSON.stringify((()=>{const n=wfList()[0];if(!n)return null;const lf=wfLookF(n);const s=chOf(n.d,lf)?chState(n,lf):null;const p=n.st==='work'&&n.f==='plate'&&chOf(n.d,'plate')?chState(n,'plate'):null;return{st:n.st,f:n.f,lf,prog:+wfProg(n).toFixed(2),hands:+wfHands(n).toFixed(2),beat:s&&s.beat?s.beat.say:null,plate:p&&p.beat?p.beat.say:null,slot:n.slot&&n.slot.type}})())"
# how far into a place's beats the work is: the beat's index plus its share done (-1 before the place's work begins, 999 once its beats are all done)
BEAT = "(()=>{const n=wfList()[0];const f='%s';if(!n||!(n.st==='work'||n.st==='cook')||n.f!==f)return n&&n.st==='ready'?999:-1;const s=chState(n,f);if(!s)return -1;if(!s.beat)return 999;const L=(s.spec.hands||[]).concat(s.spec.heat||[]);return L.indexOf(s.beat)+s.t})()"
NB = "(()=>{const c=chOf('%s','%s');return c?(c.hands||[]).length+(c.heat||[]).length:0})()"
def tick(g, n): g.ev(f"for(let i=0;i<{n};i++){{for(const q of R.groups)q.pat=1;__tick(1000/30)}}")
srv, port = rt.start_server()
with sync_playwright() as p:
    b = p.chromium.launch()
    _nc = b.new_context
    b.new_context = lambda **kw: _nc(**dict(kw, device_scale_factor=3))
    for d in DISHES:
        g = rt.Game(b, port, 'index', seed=4040, manual=True, viewport={'width': 390, 'height': 844})
        g.click('[data-act=open]'); g.page.wait_for_timeout(150)
        g.ev(SETUP % {'d': d, 'extra': EXTRA.get(d, '')})
        if d in ('pizza', 'pzmarg', 'pzfungi'): g.ev("if(typeof projBuild==='function'){}S.projDone=S.projDone||{};S.projDone.pizzaoven=1;save()")
        rt.start_day(g)
        g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}")
        g.ev(MK); g.ev("R.sched=[];R.si=0;for(const q of R.groups.slice())leaveGroup(q,'ok');R.tickets=[];setRoom('kitchen')")
        tick(g, 60)
        if not g.ev(f"isWF('{d}')"):
            print(d, 'not on the new kitchen'); g.close(); continue
        g.ev(f"__mk(0,['{d}'])"); tick(g, 3)
        shots = []
        def shot(name, label):
            g.ev("forceDraw=true;__tick(1000/30)"); g.page.wait_for_timeout(50)
            sp = json.loads(g.ev("JSON.stringify((()=>{const n=wfList()[0];if(!n)return null;if(n.slot)return wfFoodSpot(n,n.slot);const J=wfJ();return{x:J.x,y:J.y-20}})())") or 'null')
            if not sp: return
            o = json.loads(g.ev("JSON.stringify((()=>{const r=sc.getBoundingClientRect();return{x:r.left+SV.ox+%f*SV.s,y:r.top+SV.oy+%f*SV.s,s:SV.s}})())" % (sp['x'], sp['y'])))
            w, h = 120 * o['s'], 110 * o['s']
            fn = os.path.join(out, f'{d}_{name}.png')
            g.page.screenshot(path=fn, clip={'x': max(0, min(390 - w, o['x'] - w / 2)), 'y': max(0, o['y'] - h * .62), 'width': w, 'height': h})
            st = json.loads(g.ev(STATE) or 'null')
            words = (st or {}).get('plate') or (st or {}).get('beat') or ''
            shots.append((fn, label + (f'｜{words}' if words else '')))
        fl = json.loads(g.ev(f"JSON.stringify(wfFlow('{d}'))"))
        for si, f in enumerate(fl):
            if f == 'plate' or f == 'serve': break
            g.ev("(()=>{const n=wfList()[0];if(wfOpen(n))wfAssign(n,'jill')})()")
            nb = g.ev(NB % (d, f))
            if nb:
                for i in range(-1, nb):   # -1: the moment the work begins
                    for _ in range(1500):
                        tick(g, 1)
                        if g.ev(BEAT % f) >= i + .5: break
                    shot(f'{si}{f}b{i+1}', f'{f} 開始' if i < 0 else f'{f} 第{i+1}拍')
            else:
                for frac in (.1, .4, .7, .95):
                    for _ in range(1500):
                        tick(g, 1)
                        if g.ev(f"(()=>{{const n=wfList()[0];return n&&(n.st==='work'||n.st==='cook')&&n.f==='{f}'&&wfProg(n)>={frac}}})()"): break
                    shot(f'{si}{f}{int(frac*100):02d}', f'{f} {int(frac*100)}%')
            for _ in range(1500):
                tick(g, 1)
                if g.ev("(()=>{const n=wfList()[0];return !n||n.st==='ready'})()"): break
        shot('ready', '做好了，在原處等')
        last = fl[-1]
        g.ev("(()=>{const n=wfList()[0];if(n&&wfOpen(n))wfAssign(n,'jill')})()")
        nbp = g.ev(NB % (d, 'plate')) if last == 'plate' else 0
        if nbp:
            for i in range(nbp):
                for _ in range(1500):
                    tick(g, 1)
                    if g.ev(BEAT % 'plate') >= i + .5: break
                shot(f'plateb{i+1}', f'裝盤 第{i+1}拍')
            for _ in range(1500):
                tick(g, 1)
                if g.ev("(()=>{const n=wfList()[0];return !n||n.st!=='work'||wfHands(n)>=.99})()"): break
            shot('plated', '裝盤完成')
        elif last == 'plate':
            for frac in (.3, .7, .98):
                for _ in range(1500):
                    tick(g, 1)
                    if g.ev(f"(()=>{{const n=wfList()[0];return n&&n.st==='work'&&n.f==='plate'&&wfHands(n)>={frac}}})()"): break
                shot(f'plate{int(frac*100):02d}', f'裝盤 {int(frac*100)}%')
        for _ in range(1500):
            tick(g, 1)
            if g.ev("(()=>{const n=wfList()[0];return !n||n.st==='topass'||(n.st==='go'&&n.carry)})()"): break
        tick(g, 4); shot('carried', '端走')
        for _ in range(1500):
            tick(g, 1)
            if g.ev("!wfList().length"): break
        print(d, len(shots), 'frames', 'errors', g.errors[:2], flush=True)
        g.close()
        cells = ''.join(f'<figure><figcaption>{H.escape(l)}</figcaption><img src="file://{fn}"></figure>' for fn, l in shots)
        name = g.ev if False else None
        page = f"""<!doctype html><meta charset=utf-8><style>body{{margin:0;background:#FAF6EE;font-family:'Noto Sans TC','PingFang TC',sans-serif;color:#2E2019}}
h1{{font-size:24px;margin:12px 16px 6px}}.row{{display:flex;gap:8px;padding:0 16px 16px}}figure{{margin:0;width:200px}}figcaption{{font-size:15px;font-weight:700;color:#7A5226;margin:2px 2px 4px;height:40px;overflow:hidden}}img{{display:block;width:200px;border-radius:8px}}</style>
<h1>{H.escape(d)}</h1><div class=row>{cells}</div>"""
        hp = os.path.join(out, f'{d}_strip.html'); open(hp, 'w', encoding='utf-8').write(page)
        b2 = p.chromium.launch(); pg = b2.new_page(viewport={'width': 2600, 'height': 400}, device_scale_factor=1); pg.goto('file://' + hp); pg.wait_for_timeout(200)
        wpx = pg.evaluate("Math.max(...[...document.querySelectorAll('.row')].map(e=>e.scrollWidth))+20")
        pg.set_viewport_size({'width': int(wpx), 'height': 400}); pg.screenshot(path=os.path.join(out, f'{d}_strip.png'), full_page=True); b2.close()
    b.close()
srv.shutdown()
