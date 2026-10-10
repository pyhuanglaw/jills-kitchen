"""Why did 《三個選項》 (yj_three) wait? The forty-days loop (the Day 52 test's own) for DAYS days with seed base BASE; per day:
怡君's visits as the evening went (her group's state, table, 秀琴 there/free), every story trace entry of the day, the majors.
python3 yj_diag.py ROOT BASE DAYS"""
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
      window.__yj=[];const __lv=leaveGroup;leaveGroup=function(q,how){if(q&&namedId(q)==='怡君')__yj.push({d:S.day,t:R?Math.round(R.t/R.dur*100):-1,ev:'leave',how,st:q.state,table:q.table});return __lv.apply(this,arguments)};""")
    seed = "Math.random=(function(){let a=%d;return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
    for d in range(DAYS):
        if g.ev("phase") == 'summary': g.click('[data-act=toShop]'); g.page.wait_for_timeout(60)
        if g.ev("phase") == 'shop': g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(100)
        g.ev(seed % (BASE + d)); g.ev("S.today.sugKey=null;S.today.sug=null;autoStock()")
        rt.start_day(g); rt.install_bot(g); g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;window.__noScenes=true")
        plan = g.ev("JSON.stringify((R.sched||[]).filter(o=>o.name==='怡君'||o.named==='怡君').map(o=>({t:Math.round(o.t/R.dur*100),story:o.story,hold:o.hold})))")
        seen = []
        for _ in range(1200):
            r = g.page.evaluate('()=>window.__bot(150,1/30)')
            if g.ev("phase") != 'service' or not g.ev("!!R"): break
            s = g.ev("JSON.stringify(R.groups.filter(q=>namedId(q)==='怡君').map(q=>({t:Math.round(R.t/R.dur*100),st:q.state,table:q.table,xq:!!xqHere(),xqFree:!!xqFree(),maj:(storyDay()||{}).major||0})))")
            if s != '[]' and (not seen or seen[-1][1] != json.loads(s)[0]['st']): seen.append((json.loads(s)[0]['t'], json.loads(s)[0]['st'], json.loads(s)[0]['table'], json.loads(s)[0]['xq'], json.loads(s)[0]['xqFree'], json.loads(s)[0]['maj']))
            if r['ticks'] < 150: break
        if g.ev("phase") == 'service':
            g.ev("closeShop('x');for(const q of R.groups.slice())leaveGroup(q,'ok')"); g.page.evaluate('()=>window.__bot(400,1/30)')
        if g.ev("phase") == 'service': g.ev("finishClosing()")
        day = g.ev("S.day")
        tr = json.loads(g.ev("JSON.stringify(__tr.filter(t=>t.d===S.day))"))
        yl = json.loads(g.ev("JSON.stringify(__yj.filter(t=>t.d===S.day))"))
        facts = json.loads(g.ev("JSON.stringify(Object.fromEntries(['yj_meet','yj_look','yj_three','yj_chose','yj_move','yj_key'].map(k=>[k,fact(k)?fact(k).d:null])))"))
        print(json.dumps({'day': day, 'plan': json.loads(plan), 'yj_seen (t%,state,table,xqHere,xqFree,majors)': seen, 'yj_leave': yl,
                          'trace': [(t.get('t'), t.get('k'), t.get('at'), t.get('lane')) for t in tr], 'facts': facts}, ensure_ascii=False), flush=True)
    g.close(); b.close(); srv.shutdown()
