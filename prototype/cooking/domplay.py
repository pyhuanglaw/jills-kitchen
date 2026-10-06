"""Play the prototype with real clicks (and some drags): the same decisions as bot.js, but every move is a mouse click
on what the player sees — the bin, the station, the thing, the tray. Catches what the logical bot cannot: a target
covered by another, a tap that selects instead of placing, a drag that drops nowhere.
  python3 prototype/cooking/domplay.py NIGHT SECONDS [--speed 2] [--w 390 --h 844] [--shots DIR]"""
import argparse, json, os, time, random
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument('night', type=int); ap.add_argument('secs', type=float)
ap.add_argument('--speed', type=float, default=2); ap.add_argument('--w', type=int, default=390); ap.add_argument('--h', type=int, default=844)
ap.add_argument('--shots', default=None); ap.add_argument('--drag', type=float, default=.3); ap.add_argument('--tut', action='store_true')
A = ap.parse_args()
PLAN = r"""(()=>{const C=__cook,G=C.G;const its=[...G.items.values()].filter(i=>!(i.at&&i.at.carry)&&i.ph!=='cook'&&i.ph!=='asm'&&!i.res);
 const free=st=>{const a=G.slots[st];return a?a.indexOf(null):-1};
 let i=its.find(x=>x.ph==='burnt');if(i)return{src:{it:i.id},dest:{st:'trash'}};
 const urg=x=>x.ph==='over'?-100:x.ph==='done'&&x.pr&&x.pr.safe<1e8?x.pr.safe-x.dt:x.ph==='hold'?30-x.ht:50;
 const ready=its.filter(x=>['done','over','hold'].includes(x.ph)&&!(x.at&&x.at.tray)).sort((a,b)=>urg(a)-urg(b));
 for(const x of ready){const nx=C.nextStOf(x.k);if(nx&&!(x.at&&x.at.st===nx)&&C.canGo({it:x.id},{st:nx}))return{src:{it:x.id},dest:{st:nx}};
  if(C.K[x.k].fin){const tk=G.tickets.filter(t=>!t.done&&t.dishes.some((d,j)=>d===x.k&&!t.fill[j])).sort((a,b)=>b.w/b.pat-a.w/a.pat)[0];if(tk)return{src:{it:x.id},dest:{tray:tk.id}}}}
 const need={};for(const tk of G.tickets)if(!tk.done)tk.dishes.forEach((d,j)=>{if(!tk.fill[j])need[d]=(need[d]||0)+1});
 const endOf=k=>{let c=k,n=0;while(n++<8){const s=C.nextStOf(c);if(!s||s==='asm')break;c=C.PR[c+'@'+s].o}for(const r in C.ASM)if(C.ASM[r].needs.includes(c))return r;return c};
 const line=s=>{const o=[s];let c=s,n=0;while(n++<8){const st=C.nextStOf(c);if(!st||st==='asm')break;c=C.PR[c+'@'+st].o;o.push(c)}return o};
 const cands=[];for(const d in need)for(const s of C.DISH[d].start){const have=[...G.items.values()].filter(x=>!(x.at&&x.at.tray)&&(line(s).includes(x.k)||x.k===d)).length;if(need[d]-have<=0)continue;const st=Object.keys(C.PR).find(x=>x.startsWith(s+'@')).split('@')[1];if(free(st)<0)continue;cands.push({s,st,len:line(s).length})}
 cands.sort((a,b)=>b.len-a.len);if(cands.length)return{src:{bin:cands[0].s},dest:{st:cands[0].st}};
 if(G.N.st.includes('chill')&&free('chill')>=0&&[...G.items.values()].filter(x=>x.k==='custard'||x.k==='pudding').length<2)return{src:{bin:'custard'},dest:{st:'chill'}};
 return null})()"""
def center(pg, sel):
    bb = pg.locator(sel).first.bounding_box()
    return None if not bb else (bb['x'] + bb['width'] / 2, bb['y'] + bb['height'] / 2)
def sel_of(x):
    if 'bin' in x: return f'[data-bin="{x["bin"]}"]'
    if 'it' in x: return f'[data-it="{x["it"]}"]'
    if 'tray' in x: return f'[data-tray="{x["tray"]}"]'
    return f'[data-st="{x["st"]}"]'
with sync_playwright() as pw:
    b = pw.chromium.launch(); ctx = b.new_context(viewport={'width': A.w, 'height': A.h}, device_scale_factor=1)
    pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + os.path.join(HERE, 'index.html')); pg.wait_for_timeout(300)
    if not A.tut: pg.evaluate("try{localStorage.setItem('jkcook.seen',JSON.stringify(['take','wait','serve','out','two','two2','fill','together','free','over','burnt','oven','asm','cook','ahead','pizza','barista']))}catch(e){}")
    pg.click(f'[data-go="{A.night}"]'); pg.wait_for_timeout(200)
    pg.evaluate(f"__cook.setSpeed({A.speed})")
    t0 = time.time(); moves = fails = drags = 0; log = []; shot_i = 0
    rnd = random.Random(3)
    while time.time() - t0 < A.secs and not pg.evaluate("__cook.G.ended"):
        plan = pg.evaluate(PLAN)
        if not plan:
            pg.wait_for_timeout(150); continue
        before = pg.evaluate("__cook.G.st.moves")
        a, d = center(pg, sel_of(plan['src'])), center(pg, sel_of(plan['dest']))
        if not a or not d:
            fails += 1; log.append(['noel', plan]); pg.wait_for_timeout(100); continue
        if rnd.random() < A.drag:
            pg.mouse.move(*a); pg.mouse.down(); pg.mouse.move((a[0] + d[0]) / 2, (a[1] + d[1]) / 2, steps=4); pg.mouse.move(*d, steps=4); pg.mouse.up(); drags += 1
        else:
            pg.mouse.click(*a); pg.wait_for_timeout(60); pg.mouse.click(*d)
        pg.wait_for_timeout(80)
        after = pg.evaluate("__cook.G.st.moves")
        if after > before: moves += 1
        else:
            fails += 1; hit = pg.evaluate(f"(()=>{{const e=document.elementFromPoint({d[0]},{d[1]});return e?(e.className||e.tagName)+' '+(e.closest('[data-st],[data-tray],[data-it],[data-bin]')||{{outerHTML:''}}).outerHTML.slice(0,80):null}})()")
            log.append(['miss', plan, hit, pg.evaluate("__cook.G.sel")]); pg.mouse.click(5, 5)
        if A.shots and moves and moves % 15 == 0:
            pg.screenshot(path=os.path.join(A.shots, f'dom_n{A.night}_{shot_i:02d}.png')); shot_i += 1
        pg.wait_for_timeout(int(500 / A.speed))
    st = pg.evaluate("JSON.stringify(__cook.G.st)")
    print(f'night {A.night}: {moves} moves by clicks ({drags} drags), {fails} misses; state {st}')
    for l in log[:8]: print('  ', json.dumps(l, ensure_ascii=False)[:300])
    print('errors', errs[:3])
    b.close()
