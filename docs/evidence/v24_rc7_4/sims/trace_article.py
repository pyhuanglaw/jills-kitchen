"""day52_seeds' loop with a trace of the days after the wall settles: who was planned, who sat, whether 怡君 and Sophie
were seated together, and why the article waited. python3 trace_article.py ROOT BASE"""
import sys, os, json
ROOT = sys.argv[1]; BASE = int(sys.argv[2]); sys.path.insert(0, os.path.join(ROOT, 'tests')); os.chdir(ROOT)
import run_tests as rt
import v24_tests as vt
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    srv, port = rt.start_server(); b = p.chromium.launch()
    g = rt.Game(b, port, 'index', seed=254, manual=True, viewport={'width': 390, 'height': 844})
    vt.load_save(g, 'player_day52.json'); g.ev("window.__fastSay=1")
    seed = "Math.random=(function(){let a=%d;return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
    for d in range(40):
        if g.ev("phase") == 'summary': g.click('[data-act=toShop]'); g.page.wait_for_timeout(60)
        if g.ev("phase") == 'shop': g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(100)
        g.ev(seed % (BASE + d)); g.ev("S.today.sugKey=null;S.today.sug=null;autoStock()")
        rt.start_day(g); rt.install_bot(g); g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;window.__noScenes=true")
        settled = g.ev("!!fact('wall_settle')&&!fact('wall_article')")
        if settled:
            plan = g.ev("JSON.stringify(R.sched.filter(o=>o.reg==='sophie'||o.name===YJN||(o.regs||[]).includes('sophie')).map(o=>({who:o.reg||o.name,regs:o.regs,t:+o.t.toFixed(1),grp:o.v24grp||null,hold:!!o.hold})))")
            due = g.ev("due('wall_article','wall_settle',3,'wall')")
            g.ev("window.__tr={both:0,sophie:0,yj:0,first:null,st:[]};")
        for _ in range(1200):
            r = g.page.evaluate('()=>window.__bot(150,1/30)')
            if settled:
                g.ev("(()=>{if(!R)return;const s=!!seatedId('sophie'),y=!!seatedId(YJID);if(s)__tr.sophie++;if(y)__tr.yj++;if(s&&y){__tr.both++;if(__tr.first==null)__tr.first=+R.t.toFixed(1)}const q=R.groups.find(q=>storyIdsOf(q).includes('sophie'));const k=q?(q.state+(q.table!=null?'@'+R.tables[q.table].room:'')+(q.lg?'/lg':'')):'-';const L=__tr.st;if(!L.length||L[L.length-1][1]!==k)L.push([+R.t.toFixed(0),k,R.groups.filter(g=>g.state==='queue').length,R.tables.filter(t=>!t.group&&!t.dirty&&(t.room||'main')!=='lounge').length])})()")
            if g.ev("phase") != 'service' or not g.ev("!!R"): break
            if r['ticks'] < 150: break
        if g.ev("phase") == 'service':
            g.ev("closeShop('x');for(const q of R.groups.slice())leaveGroup(q,'ok')"); g.page.evaluate('()=>window.__bot(400,1/30)')
        if g.ev("phase") == 'service': g.ev("finishClosing()")
        if settled:
            tr = g.ev("JSON.stringify(__tr)")
            print("day", g.ev("S.day-1"), "regMiss.sophie", g.ev("JSON.stringify((S.regMiss||{}).sophie)"), "due", due, 'plan', plan, 'seated', tr, 'article', g.ev("JSON.stringify(fact('wall_article'))"), flush=True)
        if g.ev("!!fact('wall_article')"): break
    g.close(); b.close(); srv.shutdown()
