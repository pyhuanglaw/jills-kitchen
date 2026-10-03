"""The player's 12:43: the L's return runs back toward the wall (the bartenders inside it); the summary's notes as an item
of their own, the Lounge on one line. Headless Chromium on the player's Day 74 save (T, not O).
python3 shot_lbar.py ROOT OUT"""
import sys, os, json, base64
ROOT = sys.argv[1]; OUT = sys.argv[2].rstrip('/') + '/'
sys.path.insert(0, ROOT + '/tests'); os.chdir(ROOT)
import run_tests as rt, v24_tests as v
from playwright.sync_api import sync_playwright
os.makedirs(OUT, exist_ok=True)
srv, port = rt.start_server()
log = []
def clean(g):
    g.ev("try{if(typeof hud==='function')hud(true)}catch(e){}")
    g.ev("document.querySelectorAll('#plines>*,#toasts>*,#banner>*').forEach(e=>e.remove())")
def shot(g, name):
    clean(g); g.page.wait_for_timeout(120); g.page.screenshot(path=OUT + name); print('  shot', name, flush=True)
def save_url(url, path): open(path, 'wb').write(base64.b64decode(url.split(',')[1])); print('  saved', os.path.basename(path), flush=True)
def crop(g, name, x, y, w, h, k=3):
    clean(g)
    url = g.ev(f"(()=>{{const s=SV.s*DPR;const cv=document.createElement('canvas');cv.width={w}*{k};cv.height={h}*{k};const c=cv.getContext('2d');c.drawImage(sc,(SV.ox+({x})*SV.s)*DPR,(SV.oy+({y})*SV.s)*DPR,{w}*s,{h}*s,0,0,{w}*{k},{h}*{k});return cv.toDataURL('image/png')}})()")
    save_url(url, OUT + name)
def center(g, sel, text=None):
    g.ev(f"(()=>{{const e=[...document.querySelectorAll('{sel}')].find(e=>!{json.dumps(text)}||e.textContent.includes({json.dumps(text)}));if(e)e.scrollIntoView({{block:'center'}})}})()")
def go(g, rm, n=4):
    g.ev(f"setRoom('{rm}')"); g.ev(f"for(let i=0;i<{n};i++)__tick(1000/30)")
GEO = "JSON.stringify({leg:LG.leg,bar:{x0:LG.bar.x0,x1:LG.bar.x1,y:LG.bar.y},bk:LG.bk,pick:cnPick(),host:{x:KEN_HOST.x,y:KEN_HOST.y},legSeats:loungeSeatDefs().filter(d=>d.leg).map(d=>[d.x,d.y])})"
with sync_playwright() as p:
    b = p.chromium.launch()
    for vp, tag in (({'width': 390, 'height': 844}, 'phone'), ({'width': 1280, 'height': 800}, 'desk')):
        # an ordinary night: the L, the bartenders coming in from the back door by the gap at its far end
        g = rt.Game(b, port, 'index', seed=7731, manual=True, viewport=vp)
        v.load_save(g, 'player_day74_1508.json')
        g.ev("S.cn=null;kenS().next=null")
        if tag == 'phone': log.append('geometry: ' + g.ev(GEO))
        v.to_service(g); g.ev("window.__act=window.__actLazy")
        g.ev("""window.__trail={};const u0=crewUpd;crewUpd=function(dt){const r=u0.apply(this,arguments);for(const m of S.crew||[]){if(crewPool(m)!=='lounge')continue;const w=R.cw&&R.cw[m.id];if(w&&w.room==='lounge'){(__trail[m.name]=__trail[m.name]||[]).push([Math.round(w.x),Math.round(w.y)])}}return r}""")
        g.ev("__botUntil('R.t>=R.dur*.12||phase!==\"service\"',60000,1/30)")
        tr = json.loads(g.ev("JSON.stringify(__trail)"))
        L = json.loads(g.ev(GEO))
        lg, bar = L['leg'], L['bar']
        def through(pts):
            inL = [q for q in pts if lg['x0'] + 1 < q[0] < lg['x1'] - 1 and lg['y0'] + 2 < q[1] < bar['y'] + 30]
            inC = [q for q in pts if lg['x1'] < q[0] < bar['x1'] and bar['y'] + 4 < q[1] < bar['y'] + 30]
            return len(inL), len(inC)
        if tag == 'phone':
            for nm, pts in tr.items():
                gap = [q for q in pts if lg['x0'] - 4 <= q[0] <= lg['x1'] + 4 and q[1] < lg['y0']]
                log.append(f'{nm}: {len(pts)} steps in the Lounge, through the return / the counter: {through(pts)}, by the gap at its far end: {len(gap)}; first {pts[:1]}, last {pts[-1:]}')
        g.ev("__botUntil('R.t>=R.dur*.5||phase!==\"service\"',150000,1/30)")
        go(g, 'lounge'); shot(g, f'l01_{tag}_the_lounge_the_L_turns_back_to_the_wall.png')
        if tag == 'phone':
            crop(g, 'l02_the_L_close.png', 70, 60, 200, 190, 3)
            log.append('bartenders now: ' + g.ev("JSON.stringify((S.crew||[]).filter(m=>m.role==='bartender').map(m=>{const w=R.cw[m.id];return{n:m.name,x:Math.round(w.x),y:Math.round(w.y),room:w.room}}))"))
        g.ev("__botUntil('phase!==\"service\"',150000,1/30)"); g.page.wait_for_timeout(150)
        center(g, '#screen h3', '今天的店'); shot(g, f'l03_{tag}_summary_an_ordinary_night.png')
        if tag == 'phone': log.append('summary, an ordinary night: ' + g.ev("[...document.querySelectorAll('#screen .daynotes div')].map(e=>e.innerText.replace(/\\s+/g,' ')).join(' | ')"))
        log.append(f'{tag} errors: {g.errors[:3]}'); g.close()
        # a tasting night: the tray at the return's far end, the board by the corner, Ken inside the L
        g = rt.Game(b, port, 'index', seed=7621, manual=True, viewport=vp)
        v.load_save(g, 'player_day74_1508.json')
        g.ev("factSet('ken_propose');factSet('ken_cut');S.cn=null;kenS().next={d:S.day,n:5};showPrep()"); g.page.wait_for_timeout(150)
        v.to_service(g); g.ev("window.__act=window.__actLazy")
        cond = """(()=>{if(!R||!R.kt||!R.kt.on)return false;return R.kt.guests.some(q=>q.ticket&&q.table!=null&&R.tables[q.table].kind!=='bar'&&q.ticket.items.some(i=>i.ktp&&i.st==='ready'&&!i.picked))})()"""
        got = False
        for _ in range(3000):
            g.page.evaluate('()=>window.__bot(4,1/30)')
            if g.ev(cond):
                go(g, 'lounge', 3); shot(g, f'l04_{tag}_tasting_night_the_tray_at_the_far_end.png')
                if tag == 'phone':
                    crop(g, 'l05_tasting_night_close.png', 70, 60, 200, 200, 3)
                    log.append('tasting night: ' + g.ev("JSON.stringify({clock:clockStr(),host:R.kt.host?{x:Math.round(R.kt.host.x),y:Math.round(R.kt.host.y),st:R.kt.host.state}:null,floor:(S.crew||[]).filter(m=>m.role==='waiter'&&crewPool(m)==='lounge').map(m=>{const w=R.cw[m.id];return{n:m.name,x:Math.round(w.x),y:Math.round(w.y),k:w.task&&w.task.k}})})"))
                got = True; break
            if g.ev("phase") != 'service': break
        if not got: log.append(f'{tag}: no moment with a round waiting on the tray')
        g.ev("__botUntil('phase!==\"service\"',150000,1/30)"); g.page.wait_for_timeout(150)
        center(g, '#screen h3', '今天的店'); shot(g, f'l06_{tag}_summary_tasting_night.png')
        if tag == 'phone': log.append('summary, the tasting night: ' + g.ev("[...document.querySelectorAll('#screen .daynotes div')].map(e=>e.innerText.replace(/\\s+/g,' ')).join(' | ')"))
        log.append(f'{tag} errors: {g.errors[:3]}'); g.close()
    b.close()
srv.shutdown()
open(OUT + 'log.txt', 'w', encoding='utf-8').write('\n'.join(log) + '\n'); print('\n'.join(log))
