"""Why did the wall's photos / visit wait? The forty-days loop (the Day 52 test's own) for DAYS days with seed base BASE; from day
FROM on, per day: the weather (planned, recorded), Sophie's and Mia's groups as the evening went (state, table, room, smPair, 秀琴
here/free), the story trace of the day, the wall's facts.  python3 wall_diag.py ROOT BASE DAYS FROM"""
import sys, os, json
ROOT = sys.argv[1]; BASE = int(sys.argv[2]); DAYS = int(sys.argv[3]); FROM = int(sys.argv[4]); sys.path.insert(0, os.path.join(ROOT, 'tests')); os.chdir(ROOT); sys.argv = [sys.argv[0]]
import run_tests as rt
import v24_tests as vt
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    srv, port = rt.start_server(); b = p.chromium.launch()
    g = rt.Game(b, port, 'index', seed=254, manual=True, viewport={'width': 390, 'height': 844})
    vt.load_save(g, 'player_day52.json'); g.ev("window.__fastSay=1")
    g.ev("""window.__tr=[];const __st0=storyTrace;storyTrace=function(o){__tr.push(Object.assign({d:S.day,t:R?Math.round(R.t/R.dur*100):-1},o));return __st0(o)};""")
    seed = "Math.random=(function(){let a=%d;return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
    for d in range(DAYS):
        if g.ev("phase") == 'summary': g.click('[data-act=toShop]'); g.page.wait_for_timeout(60)
        if g.ev("phase") == 'shop': g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(100)
        g.ev(seed % (BASE + d)); g.ev("S.today.sugKey=null;S.today.sug=null;autoStock()")
        rt.start_day(g); rt.install_bot(g); g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;window.__noScenes=true")
        day = g.ev("S.day"); watch = day >= FROM
        plan = g.ev("JSON.stringify((R.sched||[]).filter(o=>['sophie','mia'].some(id=>String(o.story||'').includes(id)||o.named==='Sophie'||o.named==='Mia'||o.name==='Sophie'||o.name==='Mia'||(o.ids||[]).includes(id))).map(o=>({t:Math.round(o.t/R.dur*100),story:o.story,name:o.name||o.named,v24grp:o.v24grp})))") if watch else '[]'
        start = g.ev("JSON.stringify({wx:S.today.weather,rec:v24().wx[S.day]||null,recPrev:v24().wx[S.day-1]||null})")
        seen = []; last = None
        for _ in range(1200):
            r = g.page.evaluate('()=>window.__bot(150,1/30)')
            if g.ev("phase") != 'service' or not g.ev("!!R"): break
            if watch:
                s = g.ev("""JSON.stringify(R.groups.filter(q=>storyIdsOf(q).some(id=>id==='sophie'||id==='mia')).map(q=>[storyIdsOf(q).filter(id=>id==='sophie'||id==='mia').join('+'),q.state,q.table,q.table!=null&&R.tables[q.table]?(R.tables[q.table].room||'main'):null]).concat([['pair',!!smPair(),'xqHere',!!xqHere(),'xqFree',!!xqFree()]]))""")
                if s != last: seen.append((g.ev("Math.round(R.t/R.dur*100)"), json.loads(s))); last = s
            if r['ticks'] < 150: break
        if g.ev("phase") == 'service':
            g.ev("closeShop('x');for(const q of R.groups.slice())leaveGroup(q,'ok')"); g.page.evaluate('()=>window.__bot(400,1/30)')
        if g.ev("phase") == 'service': g.ev("finishClosing()")
        facts = json.loads(g.ev("JSON.stringify(Object.fromEntries(['wall_worry','wall_call','wall_photos','wall_visit','wall_wang'].map(k=>[k,fact(k)?fact(k).d:null])))"))
        end = g.ev("JSON.stringify({wx:S.today.weather,rec:v24().wx[S.day]||null})")
        if watch:
            tr = json.loads(g.ev("JSON.stringify(__tr.filter(t=>t.d===S.day&&/wall|sophie|mia|smw/.test(JSON.stringify(t))))"))
            print(json.dumps({'day': day, 'start': json.loads(start), 'end': json.loads(end), 'facts': facts, 'plan': json.loads(plan),
                              'seen (t%, groups[ids,state,table,room], pair/xq)': seen, 'trace': tr}, ensure_ascii=False), flush=True)
        else:
            print(json.dumps({'day': day, 'start': json.loads(start), 'end': json.loads(end), 'facts': facts}, ensure_ascii=False), flush=True)
    g.close(); b.close(); srv.shutdown()
