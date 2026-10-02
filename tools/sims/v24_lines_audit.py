"""v2.4 rc6 (the player's 12:17, 「故事進展真的太慢 一堆劇情完全沒後續」): every story line on a real save — its progress, the
last day it moved, the next step and what that step waits for (its condition, from the code); then DAYS lazy days played
(the staff do their jobs, the story arbiter as in play) and the same again. A line that was open, unfinished and did not
move is marked STALLED.

  python3 tools/sims/v24_lines_audit.py SAVE DAYS SEED
  e.g. python3 tools/sims/v24_lines_audit.py tests/saves/player_day71_1215.json 30 7100
"""
import sys, os, json
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, os.path.join(ROOT,'tests'))
import run_tests as rt
from playwright.sync_api import sync_playwright
SAVE=sys.argv[1]; DAYS=int(sys.argv[2]); SEED0=int(sys.argv[3])
raw=json.load(open(SAVE)); raw=raw.get('save',raw)
SEED = "Math.random=(function(){let a=%d;return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
SNAP = r"""JSON.stringify(STORY_LINES.map(L=>{let P=null;try{P=lineProgress(L)}catch(e){return{k:L.k,err:String(e)}}
  let open=false;try{open=!!L.open()}catch(e){}
  const done=P.done.map(b=>({id:b.id,d:b.d,t:b.t}));const last=done.reduce((m,b)=>Math.max(m,b.d||0),0);
  const nxt=(L.beats||[]).map(b=>{const key=typeof b[0]==='string'?b[0]:(b[2]&&b[2].key)||null;return{key,t:b[1]}}).filter(b=>b.key&&!done.some(x=>x.id===b.key))[0]||null;
  let src=null;if(nxt){const E=STORY_EV.find(e=>e.k===nxt.key);if(E)src=String(E.when).slice(0,260)}
  let who='';try{who=typeof L.who==='function'?L.who():L.who}catch(e){}
  return{k:L.k,who,open,n:done.length,total:P.total,last,next:nxt,src}}))"""
with sync_playwright() as p:
    srv, port = rt.start_server(); b = p.chromium.launch()
    g = rt.Game(b, port, 'index', seed=SEED0, manual=True, viewport={'width':390,'height':844})
    g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.page.wait_for_timeout(150)
    g.click('[data-act=openFresh]') if g.page.query_selector('[data-act=openFresh]') else g.click('[data-act=open]'); g.page.wait_for_timeout(150)
    g.ev("window.__fastSay=1")
    s0=json.loads(g.ev(SNAP)); day0=g.ev("S.day")
    for d in range(DAYS):
        if g.ev("phase") == 'service':
            g.ev("closeShop('x');for(const q of R.groups.slice())leaveGroup(q,'ok')"); g.page.evaluate('()=>window.__bot(400,1/30)')
            if g.ev("phase") == 'service': g.ev("finishClosing()")
        if g.ev("phase") == 'summary': g.click('[data-act=toShop]'); g.page.wait_for_timeout(80)
        if g.ev("phase") == 'shop': g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(120)
        g.ev(SEED % (SEED0 + d)); g.ev("S.today.sugKey=null;S.today.sug=null;autoStock()")
        rt.start_day(g); rt.install_bot(g); g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;window.__noScenes=true")
        for _ in range(1200):
            r = g.page.evaluate('()=>window.__bot(150,1/30)')
            if g.ev("phase") != 'service' or not g.ev("!!R"): break
            if r['ticks'] < 150: break
        if g.ev("phase") == 'service':
            g.ev("closeShop('x');for(const q of R.groups.slice())leaveGroup(q,'ok')"); g.page.evaluate('()=>window.__bot(400,1/30)')
        if g.ev("phase") == 'service': g.ev("finishClosing()")
    s1=json.loads(g.ev(SNAP)); day1=g.ev("S.day")
    rest0=json.loads(g.ev("JSON.stringify(restDone().map(x=>x.id+'@'+x.d))"))
    print(f'Day {day0} → Day {day1}')
    print(f"{'line':12s} {'who':22s} {'open':5s} {'@'+str(day0):>8s} {'last':>5s} {'@'+str(day1):>8s} {'last':>5s}  next (what it waits for)")
    for a,b2 in zip(s0,s1):
        if 'err' in a: print(a['k'],'ERR',a['err']); continue
        mark = '' if b2['n']>a['n'] else ('  STALLED' if a['open'] and a['n']<a['total'] else '')
        print(f"{a['k']:12s} {str(a['who'])[:22]:22s} {str(a['open']):5s} {str(a['n'])+'/'+str(a['total']):>8s} {a['last']:>5d} {str(b2['n'])+'/'+str(b2['total']):>8s} {b2['last']:>5d}{mark}  {b2['next']['key'] if b2['next'] else '-'}: {(b2['src'] or '')[:200]}")
    print('page errors', g.errors[:3])
    g.close(); b.close(); srv.shutdown()
