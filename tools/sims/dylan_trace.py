"""v2.2.1 #17: Dylan on the real Day 30 save, Days 31-33, the way a player would play: restock to the suggestion (not a
full fridge), the active player (taps everything) or the lazy one (staff do the work), several seeds. Per day: scheduled
(when), every arrival attempt (queue / free tables per room at that moment, entered or rejected), where he sat, how long,
what he said, whether the player looking at the main hall could have seen him, clue/stage deltas.
Usage: dylan221.py <seed> <active|lazy> <days>"""
import sys, os, json
ROOT='/home/claude/jills-kitchen-project'; sys.path.insert(0, os.path.join(ROOT,'tests'))
import run_tests as T
from run_tests import Game, start_server, install_bot, start_day, player30, LAZY_ACTOR
from playwright.sync_api import sync_playwright
seed=int(sys.argv[1]); mode=sys.argv[2]; days=int(sys.argv[3]) if len(sys.argv)>3 else 3
HOOKS=r"""(()=>{window.__dy=[];const S0=spawn;spawn=function(o){let rec=null;if(o.reg==='dylan'){const free=r=>R.tables.filter(t=>!t.group&&!t.dirty&&(t.room||'main')===r).length;rec={t:+R.t.toFixed(1),tries:o.tries||0,back:!!o.back,queued:queued().length,qmax:queueMax(),freeMain:free('main'),freeSide:free('side'),freeFront:free('front'),rush:!!(R.rush&&R.t>=R.rushT0&&R.t<=R.rushT1),closed:R.closed};__dy.push(rec)}const n=R.groups.length;const r=S0(o);if(rec)rec.entered=R.groups.length>n;return r};return 1})()"""
POLL=r"""(()=>{const q=R?R.groups.find(x=>x.reg==='dylan'):null;const t=q&&q.table!=null?R.tables[q.table]:null;return {t:R?+R.t.toFixed(1):0,ph:phase,in:!!q,st:q?q.state:null,room:t?(t.room||'main'):(q?q.room:null),said:!!(q&&q.said),quiet:!!(q&&q.quiet),lines:R?R.log.filter(l=>l.k==='d').map(l=>l.t):[],v:S.regulars.dylan||0,lost:R?R.st.lost:0}})()"""
with sync_playwright() as p:
    srv, port = start_server(); b = p.chromium.launch()
    g = Game(b, port, 'index', seed=seed, manual=True)
    player30(g); install_bot(g)
    if mode=='lazy': g.ev(LAZY_ACTOR+"\nwindow.__act=window.__actLazy;")
    for d in range(days):
        if g.ev("phase")!='prep':
            if g.ev("phase")=='summary': g.click('[data-act=toShop]')
            if g.ev("phase")=='shop': g.click('[data-act=nextDay]')
        g.ev("autoStock()")   # 一鍵補到建議量, as the player did
        before=json.loads(g.ev("JSON.stringify({stage:S.dylan.stage,clues:S.dylan.clues,v:S.regulars.dylan||0,last:S.dylan.last,stock:stockTotal(),cap:fridgeCap()})"))
        start_day(g); g.ev(HOOKS)
        sched=json.loads(g.ev("JSON.stringify(R.sched.filter(o=>o.reg==='dylan').map(o=>({t:+o.t.toFixed(1),dur:R.dur})))"))
        first=None; last=None; rooms=set(); states=[]; lines=set(); seated_t=None; left_t=None; mainSeen=0; polls=0
        for i in range(600):
            r=g.page.evaluate('()=>window.__bot(150,1/30)')
            info=json.loads(g.ev("JSON.stringify("+POLL+")"))
            if info['in']:
                if first is None: first=info['t']
                last=info['t']; rooms.add(info['room']); 
                if not states or states[-1]!=info['st']: states.append(info['st'])
                if info['st'] not in ('arrive','queue','toTable','leave') and seated_t is None: seated_t=info['t']
                if info['st']=='leave' and left_t is None: left_t=info['t']
                if info['room']=='main' and info['st'] not in ('arrive','leave'): mainSeen+=1
                polls+=1
            lines|=set(info['lines'])
            if info['ph']!='service' or r['ticks']<150: break
        if g.ev("phase")=='service': g.ev("closeShop('x');for(const q of R.groups.slice())leaveGroup(q,'ok')"); g.page.evaluate('()=>window.__bot(400,1/30)')
        if g.ev("phase")=='service': g.ev("finishClosing()")
        attempts=json.loads(g.ev("JSON.stringify(window.__dy||[])"))
        after=json.loads(g.ev("JSON.stringify({stage:S.dylan.stage,clues:S.dylan.clues,v:S.regulars.dylan||0,last:S.dylan.last,doorDays:S.dylan.doorDays||0,guests:S.lastSummary?S.lastSummary.guests:0,lost:S.lastSummary?S.lastSummary.lost:0})"))
        dclues={k:after['clues'].get(k,0)-before['clues'].get(k,0) for k in set(after['clues'])|set(before['clues']) if after['clues'].get(k,0)!=before['clues'].get(k,0)}
        row={'seed':seed,'mode':mode,'day':g.ev("S.day"),'stock_before':f"{before['stock']}/{before['cap']}",'scheduled':sched,'attempts':attempts,'entered_at':first,'seated_at':seated_t,'left_at':left_t,'last_seen':last,'rooms':sorted(r for r in rooms if r),'states':states,'lines':sorted(lines),'main_polls':mainSeen,'polls_in':polls,'paid_visit':after['v']-before['v'],'clues+':dclues,'stage':after['stage'],'doorDays':after['doorDays'],'guests':after['guests'],'lost':after['lost'],'errors':g.errors[:2]}
        print(json.dumps(row,ensure_ascii=False),flush=True)
    g.close(); b.close()
