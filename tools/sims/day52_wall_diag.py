"""Why does wall_worry wait? The forty-days loop for DAYS days with seed base BASE; per day: the majors that fired, Sophie's and
Mia's visits, and every time wall_worry's conditions got as far as smPair (and what it returned, with 秀琴 there or not).
python3 day52_diag.py ROOT BASE DAYS"""
import sys, os, json
ROOT = sys.argv[1]; BASE = int(sys.argv[2]); DAYS = int(sys.argv[3]); sys.path.insert(0, os.path.join(ROOT, 'tests')); os.chdir(ROOT)
import run_tests as rt
import v24_tests as vt
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    srv, port = rt.start_server(); b = p.chromium.launch()
    g = rt.Game(b, port, 'index', seed=254, manual=True, viewport={'width': 390, 'height': 844})
    vt.load_save(g, 'player_day52.json'); g.ev("window.__fastSay=1")
    g.ev("""window.__tr=[];const __st0=storyTrace;storyTrace=function(o){__tr.push(Object.assign({d:S.day,t:R?Math.round(R.t/R.dur*100):-1},o));return __st0(o)};
      window.__sp=[];const __sm=smPair;smPair=function(){const r=__sm();__sp.push({d:S.day,t:R?Math.round(R.t/R.dur*100):-1,ok:!!r,xq:!!xqHere(),maj:(storyDay()||{}).major});return r};
      window.__sm0={};""")
    seed = "Math.random=(function(){let a=%d;return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
    for d in range(DAYS):
        if g.ev("phase") == 'summary': g.click('[data-act=toShop]'); g.page.wait_for_timeout(60)
        if g.ev("phase") == 'shop': g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(100)
        g.ev(seed % (BASE + d)); g.ev("S.today.sugKey=null;S.today.sug=null;autoStock()")
        rt.start_day(g); rt.install_bot(g); g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;window.__noScenes=true")
        v0 = json.loads(g.ev("JSON.stringify({s:S.regulars.sophie||0,m:S.regulars.mia||0,w:S.today.weather,sched:R.sched.filter(o=>o.reg==='sophie'||o.reg==='mia'||(o.regs||[]).some(x=>x==='sophie'||x==='mia')).map(o=>[o.reg,(o.regs||[]).join('+'),Math.round(o.t/R.dur*100)])})"))
        for _ in range(1200):
            r = g.page.evaluate('()=>window.__bot(150,1/30)')
            if g.ev("phase") != 'service' or not g.ev("!!R"): break
            if r['ticks'] < 150: break
        if g.ev("phase") == 'service':
            g.ev("closeShop('x');for(const q of R.groups.slice())leaveGroup(q,'ok')"); g.page.evaluate('()=>window.__bot(400,1/30)')
        if g.ev("phase") == 'service': g.ev("finishClosing()")
        x = json.loads(g.ev("JSON.stringify({day:S.day-0,s:S.regulars.sophie||0,m:S.regulars.mia||0,maj:__tr.filter(t=>t.d===S.day&&t.lane==='major').map(t=>t.k+'@'+t.t),sp:__sp.filter(o=>o.d===S.day)})"))
        sp = x['sp']; okn = sum(1 for o in sp if o['ok']); okxq = sum(1 for o in sp if o['ok'] and o['xq'])
        first_ok = next((o for o in sp if o['ok']), None)
        print(f"Day {x['day']} {v0['w']:5s} sophie+{x['s']-v0['s']} mia+{x['m']-v0['m']} sched {v0['sched']}  smPair calls {len(sp)} ok {okn} ok&xq {okxq} first_ok {first_ok}  majors {x['maj']}", flush=True)
    F = json.loads(g.ev("JSON.stringify(Object.fromEntries(%s.map(k=>[k,fact(k)?fact(k).d:null])))" % json.dumps(vt.V24_KEYS)))
    print('yj_key', F['yj_key'], 'wall_worry', F['wall_worry'])
    g.close(); b.close(); srv.shutdown()
