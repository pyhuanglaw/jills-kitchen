"""The census flow (tools/qa/evening_census.py, seed 1) on the user's Day 6 save, with a log of 怡君: every spawn attempt,
her group's state, the door's give-up, the beat."""
import sys, os, json
ROOT = sys.argv[1]
sys.path.insert(0, os.path.join(ROOT, 'tests'))
import run_tests as rt
from player import Player
from playwright.sync_api import sync_playwright
HOOK = r"""(()=>{if(window.__yjh)return;window.__yjh=1;window.__yl=[];const L=(m)=>__yl.push([S.day,R?clockStr():'-',m]);
 const s0=spawn;spawn=function(o){const isY=o&&o.name==='怡君';const n=R.gid;const r=s0.apply(this,arguments);if(isY){const g=R.groups.find(x=>x.id>=n&&x.name==='怡君');L('spawn tries='+(o.tries||0)+' beat='+!!o.beat+' -> '+(g?'in ('+g.state+')':'not in; queue '+queued().length+'/'+queueMax()+(R.sched.some(q=>q.name==='怡君'&&(q.tries||0)>(o.tries||0))?' — back later':' — no retry')))}return r};
 const st0=storyTrace;storyTrace=function(x){if(x&&(x.beat==='怡君'||JSON.stringify(x).includes('yj')))L('trace '+JSON.stringify(x));return st0.apply(this,arguments)};
 const ss0=shStart;shStart=function(k,a,g,fn,now){if(k==='yj_meet')L('shStart floorBusy='+floorBusy()+' closing='+R.closing+' closed='+R.closed+' phase='+phase+' talk='+!!TALK+' fast='+!!window.__fastSay+' floorUntil='+(R.floorUntil!=null?(R.floorUntil-R.t).toFixed(1):null));const fn2=k==='yj_meet'?function(){L('the beat runs (callback)');const r=fn.apply(this,arguments);L('after run: yj_meet='+JSON.stringify(fact('yj_meet')));return r}:fn;return ss0.call(this,k,a,g,fn2,now)};
 const sn0=shStartNow;shStartNow=function(cx,fn,now){if(cx&&cx.k==='yj_meet')L('shStartNow authored='+cx.authored+' shOn='+shOn()+' phase='+phase+' DLG='+!!DLG);return sn0.apply(this,arguments)};
 const xt0=xqTo;xqTo=function(g,then,o){const r=xt0.apply(this,arguments);L('xqTo('+(g&&g.name)+') -> '+r);return r};
 setInterval(()=>{if(!R||phase!=='service')return;const y=R.groups.find(x=>x.name==='怡君'&&!x.gone);if(!y||!['eat','check','wait','leave'].includes(y.state))return;const m=xqm();const w=m&&crewSprite(m);const k=w?('task '+(w.task?w.task.k+(w.task.k==='visit'?(w.task.g===y?'(her)':'(other)'):''):'-')+' next '+(w.next?w.next.k:'-')+' q '+((w.nextQ||[]).length)+' busy '+(w.busy||0).toFixed(1)+' here '+!!xqHere()):'no sprite';if(k!==window.__xk){window.__xk=k;L('秀琴 '+k)}},250);
 const ff0=floorFlush;floorFlush=function(){L('floorFlush (the evening ends) talkq='+(R&&R.talkq?R.talkq.length:0));return ff0.apply(this,arguments)};
 setInterval(()=>{if(!R||phase!=='service')return;const g=R.groups.find(x=>x.name==='怡君'&&!x.gone);const k=g?g.state+(g.table!=null?' T'+(g.table+1):'')+' pat '+g.pat.toFixed(2):'—';if(k!==window.__yk){window.__yk=k;L('state '+k)}},500)})()"""
with sync_playwright() as pw:
    srv, port = rt.start_server(); b = pw.chromium.launch()
    p = Player(b, port, 'index', save='player_day6_1254.json', seed=1, checkpoint=False)
    p.tap('#screen [data-act=open]'); p.settle(); p.g.ev(HOOK)
    for _ in range(3):
        if p.state()['phase'] == 'shop':
            p.tap('#screen [data-act=nextDay]'); p.settle()
        if p.state()['phase'] == 'summary':
            p.tap('#screen [data-act=toShop]'); p.tap('#screen [data-act=nextDay]'); p.settle()
        day = p.state()['day']
        p.g.ev(HOOK)
        sched = p.g.ev("JSON.stringify((S.today&&S.today.v24)||null)")
        p.restock(); p.start_day()
        print('Day', day, 'scheduled 怡君:', p.g.ev("JSON.stringify(R.sched.filter(o=>o.name==='怡君').map(o=>({t:Math.round(o.t),beat:!!o.beat,tries:o.tries||0})))"), flush=True)
        p.play_evening()
        print('  yj_meet:', p.g.ev("JSON.stringify(fact('yj_meet'))"), flush=True)
        if p.state()['phase'] == 'summary':
            p.tap('#screen [data-act=toShop]')
    for x in json.loads(p.g.ev("JSON.stringify(__yl)")): print(' ', x)
    print('errors', p.errors[:3])
    p.close(); b.close(); srv.shutdown()
