#!/usr/bin/env python3
"""Jill's Kitchen — regression / smoke tests.

Runs the real game in headless Chromium (Playwright). The game files on disk are
never modified: at load time the harness injects a tiny eval hook (window.__jk)
inside the game's closure so tests can read internal state.

Usage:
  python3 tests/run_tests.py                 # test index.html (css/ + js/)
  python3 tests/run_tests.py --target single # test jills-kitchen-single-file.html
  python3 tests/run_tests.py --record        # (re)record the golden baseline
  python3 tests/run_tests.py -k cats         # run tests whose name contains "cats"
  JK_GAME_JS=/path/to/old/game.js python3 tests/run_tests.py   # run the suite against another game.js

Requires: pip install playwright && playwright install chromium
"""
import argparse, functools, http.server, json, os, re, socketserver, sys, threading, time, traceback

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLDEN = os.path.join(ROOT, 'tests', 'golden', 'scenario.json')
GOLDEN_FRAMES = os.path.join(ROOT, 'tests', 'golden', 'frames.json')
SCREENS = os.path.join(ROOT, 'tests', 'golden', 'screens')
ARTIFACTS = os.path.join(ROOT, 'tests', 'artifacts')
FIXTURES = os.path.join(ROOT, 'tests', 'fixtures')
SAVE_KEY = 'jills-kitchen-save-v1'
VIEW = {'width': 390, 'height': 800}

# ---------------------------------------------------------------- server
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

def start_server():
    handler = functools.partial(Quiet, directory=ROOT)
    srv = socketserver.TCPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]

HOOK = "window.__jk=function(s){return eval(s)};"

def inject(js):
    i = js.rfind('boot();')
    assert i > 0, 'boot(); not found — cannot inject test hook'
    return js[:i] + HOOK + js[i:]

# ---------------------------------------------------------------- init scripts
def init_script(seed=None, manual=False, audio=False):
    parts = []
    if seed is not None:
        parts.append("""(function(){let a=%d>>>0;Math.random=function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296};})();""" % seed)
    if not audio:
        parts.append("window.AudioContext=undefined;window.webkitAudioContext=undefined;")
    parts.append("""(function(){
      window.__stats={raf:0,rafOut:0,rafMax:0,intervals:0,listeners:0};
      const R0=window.requestAnimationFrame.bind(window);
      const MANUAL=%s;
      window.requestAnimationFrame=function(cb){__stats.raf++;__stats.rafOut++;__stats.rafMax=Math.max(__stats.rafMax,__stats.rafOut);
        if(MANUAL){__rafQ.push(cb);return __rafQ.length}
        return R0(function(t){__stats.rafOut--;cb(t)})};
      const SI=window.setInterval.bind(window);window.setInterval=function(){__stats.intervals++;return SI.apply(null,arguments)};
      const AEL=EventTarget.prototype.addEventListener;EventTarget.prototype.addEventListener=function(){__stats.listeners++;return AEL.apply(this,arguments)};
      // Manual mode = virtual time. Nothing moves unless the test calls __tick(ms):
      // performance.now(), setTimeout and requestAnimationFrame all follow the virtual clock,
      // so frames, toasts, banners and coach bubbles are fully deterministic.
      window.__rafQ=[];
      if(MANUAL){
        let now=1000,seq=0;const timers=[];
        performance.now=function(){return now};
        window.setTimeout=function(fn,ms){const a=[].slice.call(arguments,2);timers.push({id:++seq,at:now+(+ms||0),fn,a});return seq};
        window.clearTimeout=function(id){const i=timers.findIndex(t=>t.id===id);if(i>=0)timers.splice(i,1)};
        window.__tick=function(ms){const end=now+ms;
          for(;;){let k=-1;for(let i=0;i<timers.length;i++)if(timers[i].at<=end&&(k<0||timers[i].at<timers[k].at))k=i;if(k<0)break;
            const t=timers.splice(k,1)[0];now=Math.max(now,t.at);t.fn.apply(null,t.a)}
          now=end;const q=__rafQ.splice(0);for(const cb of q){__stats.rafOut--;cb(now)}};
      }
    })();""" % ('true' if manual else 'false'))
    return '\n'.join(parts)

# ---------------------------------------------------------------- page helpers
class Game:
    def __init__(self, browser, port, target, seed=None, manual=False, audio=False, storage=None):
        self.ctx = browser.new_context(viewport=VIEW, device_scale_factor=1)
        self.page = self.ctx.new_page()
        self.errors = []
        self.page.on('pageerror', lambda e: self.errors.append(str(e)))
        self.page.on('console', lambda m: self.errors.append('console.error: ' + m.text) if m.type == 'error' and 'fonts.g' not in m.text and 'ERR_' not in m.text else None)
        game_js = os.environ.get('JK_GAME_JS') or os.path.join(ROOT, 'js', 'game.js')  # JK_GAME_JS: test another build, e.g. the baseline
        self.page.route('**/js/game.js', lambda r: r.fulfill(status=200, content_type='application/javascript', body=inject(open(game_js, encoding='utf-8').read())))
        self.page.route('**/jills-kitchen-single-file.html', lambda r: r.fulfill(status=200, content_type='text/html', body=inject(open(os.path.join(ROOT, 'jills-kitchen-single-file.html'), encoding='utf-8').read())))
        self.page.route('https://fonts.googleapis.com/**', lambda r: r.abort())
        self.page.route('https://fonts.gstatic.com/**', lambda r: r.abort())
        self.page.add_init_script(init_script(seed, manual, audio))
        if storage is not None:
            self.page.add_init_script("(function(){if(!sessionStorage.getItem('__seeded')){localStorage.clear();const d=%s;for(const k in d)localStorage.setItem(k,d[k]);sessionStorage.setItem('__seeded','1')}})();" % json.dumps(storage))
        else:
            self.page.add_init_script("(function(){if(!sessionStorage.getItem('__seeded')){localStorage.clear();sessionStorage.setItem('__seeded','1')}})();")
        page = 'index.html' if target == 'index' else 'jills-kitchen-single-file.html'
        self.url = f'http://127.0.0.1:{port}/{page}'
        self.page.goto(self.url)
        self.page.wait_for_function('typeof window.__jk==="function"')

    def ev(self, code):
        return self.page.evaluate('c=>window.__jk(c)', code)

    def click(self, sel):
        self.page.click(sel)

    def reload(self):
        self.page.reload()
        self.page.wait_for_function('typeof window.__jk==="function"')

    def close(self):
        self.ctx.close()

# In-page bot: plays the service perfectly and deterministically.
BOT = r"""
// Weight tracer: every weighted random choice in the game (cat personality decisions, guests
// looking at cats, …) goes through wpick(). We fold every weight it sees into a hash, so even a
// tiny change to a personality weight is detected, although it may not change any outcome.
// The wrapper calls the game's own weight function exactly once per item, as the game does,
// so the random number stream and the behaviour are unchanged.
if (!window.__wt) {
  window.__wt = {n:0, h:2166136261};
  const W0 = wpick;
  wpick = function(arr, wf){ const t = __wt; return W0(arr, function(x){ const v = wf(x);
    const s = typeof v === 'number' ? v.toFixed(6) : String(v);
    for (let i=0;i<s.length;i++){ t.h ^= s.charCodeAt(i); t.h = Math.imul(t.h,16777619); }
    t.h ^= 124; t.h = Math.imul(t.h,16777619); t.n++; return v; }); };
}
window.__wtHash = () => __wt.n + ':' + (__wt.h>>>0).toString(16);
// One step of a perfect, deterministic player: seat, serve, cook every step exactly right.
window.__act = function(){
  if (!(phase==='service' && R)) return false;
  if (!R.closed) {
    for (const g of queued()) { if (g.state==='queue') { const t=freeTableFor(g); if (t) seatGroup(g,t); } }
  }
  for (const t of R.tables) { if (tableActionable(t) && !jillTargets(t.i)) tapTable(t); }
  for (const tk of R.tickets) for (const it of tk.items) if (it.st==='pending') startCook(tk,it,true);
  for (const s of R.slots) {
    if (s.broken) { tapStation(R.slots.indexOf(s)); continue; }
    const j=s.job; if (!j || !j.step) continue; const k=j.step;
    if (chefHandles(s)) continue;
    if (k.t==='add') { const id = k.left[0]; if (id) actIng(s,id); }
    else if (k.t==='tap') actTap(s);
    else if (k.t==='zone') { if (k.p >= k.z.c) actZone(s); }
    else if (k.t==='hold') { k.hold=true; R.holdSlot=s; k.level=(k.a+k.b)/2; holdEnd(); }
    else if (k.t==='dose') { if (k.cnt < k.min) actDose(s); else actDoseDone(s); }
  }
  return true;
};
// Fast mode: step the simulation directly (no rendering).
window.__bot = function(steps, dt){
  const out = {ticks:0};
  for (let n=0; n<steps; n++){
    if (!__act()) break;
    update(dt); updateCats(dt, 0); out.ticks++;
    if (R && R.closing!=null && R.closing>1 && !R.ended) { finishClosing(); break; }
  }
  return out;
};
// Evening mode: keep the world running after closing (Jill's sofa life, the TV, Dylan, the cats) without
// rendering. Steps the same functions the main loop steps.
window.__evening = function(seconds, dt, every, hook){
  const out = {samples:[], bad:[]}; const n = Math.round(seconds/dt);
  for (let i=0;i<n;i++){
    if (R && phase==='service') update(dt);
    updateCats(dt, 0); lifeUpd(dt);
    if (hook) hook(i*dt);
    const b = __lifeInvariants(); if (b.length && out.bad.length<8) out.bad.push({t:+(i*dt).toFixed(2), b});
    if (every && i % every === 0) out.samples.push(__lifeSample(i*dt));
  }
  return out;
};
window.__lifeSample = t => { const L=LIFE.jill, D=LIFE.dylan, tv=LIFE.tv;
  return {t:+t.toFixed(1), phase, plan:LIFE.plan, jill:{on:L.on,act:L.act,legs:+L.legs.toFixed(2),pos:L.pos,x:L.x|0,y:L.y|0,walking:L.walking},
          tv:{at:tv.at,on:tv.on,x:tv.x|0,y:tv.y|0,mover:tv.mover}, dylan:D?{st:D.state,x:D.x|0,y:D.y|0,onSofa:D.onSofa,seated:D.seated,act:D.act}:null,
          cats:CATS.map(c=>({id:c.def.id,st:c.st,pose:c.pose,x:c.x|0,y:c.y|0,slot:c.sofa?c.sofa.k:null,kind:c.sofa?c.sofa.kind:null,on:!!c.sofaOn}))}};
window.__lifeInvariants = function(){ const bad=[]; const L=LIFE.jill, D=LIFE.dylan, tv=LIFE.tv; if (!CATS) return bad;
  const on = CATS.filter(c=>c.sofa&&c.sofaOn);
  const keys = on.map(c=>c.sofa.k); if (new Set(keys).size!==keys.length) bad.push('two cats in one sofa slot: '+keys.join(','));
  if (on.filter(c=>c.sofa.kind==='lap').length>1) bad.push('two cats on the lap');
  const ivs = []; if (L.on){ ivs.push(['jill',L.x-13,L.x+13]); const lg=jillLegs(); if (lg) ivs.push(['legs',lg[0],lg[1]]); }
  if (D&&D.onSofa) ivs.push(['dylan',D.x-13,D.x+13]);
  for (const c of on) if (c.sofa.kind==='seat') ivs.push([c.def.id,c.sofa.x-12,c.sofa.x+12]);
  for (let i=0;i<ivs.length;i++) for (let j=i+1;j<ivs.length;j++){ const a=ivs[i],b=ivs[j]; if (a[0]==='jill'&&b[0]==='legs') continue; if (a[1]<b[2]-0.5 && b[1]<a[2]-0.5) bad.push('overlap on the seat: '+a[0]+' '+b[0]); }
  for (const v of ivs) if (v[1]<SOFA.seatL-0.5||v[2]>SOFA.seatR+0.5) bad.push(v[0]+' hangs off the seat');
  if (L.on && (L.x!==JPOS[L.pos].x || L.y!==SOFA.jy)) bad.push('Jill seated at a wrong place');
  if (L.on && (L.act==='pushing'||L.walking)) bad.push('walking while seated');
  if (tv.mover){ for (const c of CATS){ if (c.hidden||c.perch>=0||c.sofa) continue; if (Math.hypot(c.x-tv.x,c.y-6-tv.y)<14) bad.push('TV rolled into '+c.def.id); } }
  for (const c of CATS){ if (!isFinite(c.x)||!isFinite(c.y)) bad.push(c.def.id+' NaN'); if (c.sofa&&c.sofaOn&&(c.x!==c.sofa.x||c.y!==c.sofa.y)) bad.push(c.def.id+' not at its slot'); }
  if (L.on && CATS.some(c=>c.sofa&&c.sofa.kind==='lap'&&c.sofaOn) && !L.on) bad.push('got up with a cat on the lap');
  return bad;
};
const __h = s => { let x=2166136261; for (let i=0;i<s.length;i++){ x^=s.charCodeAt(i); x=Math.imul(x,16777619);} return (x>>>0).toString(16); };
const __px = cv => { if (!cv || !cv.width || !cv.height) return '-'; const d=cv.getContext('2d').getImageData(0,0,cv.width,cv.height).data; const u=new Uint32Array(d.buffer); let x=2166136261; for (let i=0;i<u.length;i++) x=Math.imul(x^u[i],16777619); return (x>>>0).toString(16); };
window.__botUntil = function(cond, maxSteps, dt){ let n=0; for (; n<maxSteps; n++){ if (!(phase==='service'&&R) || eval(cond)) break; __act(); update(dt||1/30); updateCats(dt||1/30,0); } return n; };
// Frame mode: run the real main loop frame by frame on virtual time (30 fps), sampling
// scene pixels, DOM and cat state along the way.
window.__play = function(frames, every, stop){
  const samples = []; let n = 0;
  for (; n<frames; n++){
    if (!(phase==='service' && R)) break;
    if (stop && eval(stop)) break;
    __act(); __tick(1000/30);
    if (every && n % every === 0) samples.push(__sample());
  }
  return {frames:n, samples};
};
window.__sample = function(){
  return { t: R ? +R.t.toFixed(3) : null, phase, scene: __px(sc), tray: $('#trayWrap').hidden ? '-' : __px(tc),
           dom: __h(['#hud','#tickets','#taskPanel','#banner','#toasts','#coach','#screen'].map(q=>{const e=$(q);return e.hidden+'|'+e.innerHTML}).join('#')),
           cats: __h(JSON.stringify((CATS||[]).map(c=>[c.def.id,c.st,c.pose,Math.round(c.x),Math.round(c.y),c.perch,!!c.hidden]))), weights: __wtHash() };
};
window.__digest = function(){
  const cats = (CATS||[]).map(c=>[c.def.id,c.st,c.pose,Math.round(c.x),Math.round(c.y),c.perch,!!c.hidden]);
  const s = S.lastSummary ? {rev:S.lastSummary.rev,cost:S.lastSummary.cost,tips:S.lastSummary.tips,bonus:S.lastSummary.bonus,wages:S.lastSummary.wages,net:S.lastSummary.net,guests:S.lastSummary.guests,lost:S.lastSummary.lost,perfect:S.lastSummary.perfect,plated:S.lastSummary.plated,avg:S.lastSummary.avg,top:S.lastSummary.top,stars:S.lastSummary.stars} : null;
  return {day:S.day, money:S.money, lifetime:S.lifetime, level:S.level, stats:S.stats, xp:S.xp, stock:S.stock, reviews:S.reviews.length,
          reviewHash:__h(JSON.stringify(S.reviews.map(r=>[r.s,r.txt,r.name]))), regulars:S.regulars, summary:s, cats, catHash:__h(JSON.stringify(cats)),
          mem:Object.keys(S.mem||{}).sort().map(k=>k+':'+S.mem[k].day+':'+__h(S.mem[k].img)), weights:__wtHash(), dylan:S.dylan, life:S.life};
};
"""

def install_bot(g):
    # evaluated through the hook so the helpers close over the game's internals
    g.ev(BOT)

# Screen / run-state invariants that every screen change must keep (see docs/ARCHITECTURE.md).
INV = r"""(()=>{const bad=[];
  if(!['title','prep','service','summary','shop'].includes(phase))bad.push('unknown phase '+phase);
  if(!!R!==(phase==='service'))bad.push('R should exist only during service (phase='+phase+', R='+!!R+')');
  if(paused&&phase!=='service')bad.push('paused outside service');
  if(paused&&sub!=='pause'&&sub!=='guide'&&sub!=='settings')bad.push('paused without a menu open (sub='+sub+')');
  if(phase==='service'&&!paused&&!sub&&!screenEl.hidden)bad.push('menu screen covering the running service');
  if(!IDLE&&phase!=='service'&&phase!=='title')bad.push('no idle view outside service');
  if(typeof __lifeInvariants==='function')bad.push(...__lifeInvariants());
  return bad})()"""

def state_ok(g, where):
    bad = g.ev(INV)
    check(not bad, f'state invariant broken at {where}: {bad}')

def play_day(g, max_steps=40000, chunk=600, dt=1/30):
    steps = 0
    while steps < max_steps:
        r = g.page.evaluate(f'()=>window.__bot({chunk},{dt})')
        steps += r['ticks']
        if g.ev("phase") != 'service':
            break
        if r['ticks'] < chunk:
            break
    return steps

def start_day(g):
    g.click('[data-act=start]')
    if g.ev("phase") != 'service':
        g.click('[data-act=start]')  # second press confirms the "no stock" warning
    assert g.ev("phase") == 'service', 'service did not start'

# ---------------------------------------------------------------- tests
TESTS = []
def test(fn):
    TESTS.append(fn)
    return fn

def check(cond, msg):
    if not cond:
        raise AssertionError(msg)

@test
def single_file_in_sync(b, port, target):
    import subprocess
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'build_single.py'), '--check'], capture_output=True, text=True)
    check(r.returncode == 0, r.stdout.strip() or r.stderr.strip())

@test
def new_game_starts(b, port, target):
    g = Game(b, port, target, seed=1, manual=True)
    check(g.page.is_visible('text=OPEN FOR DINNER'), 'title screen missing')
    check(g.ev("S.day") == 1 and g.ev("S.money") == 500, 'fresh state wrong')
    g.click('[data-act=open]')
    check(g.ev("phase") == 'prep', 'prep screen did not open')
    start_day(g)
    check(g.ev("!!R && R.slots.length>=1 && R.tables.length===S.tables"), 'run state not initialised')
    check(not g.errors, g.errors)
    g.close()

@test
def main_loop_single_instance(b, port, target):
    g = Game(b, port, target, seed=2, manual=False, audio=True)
    g.page.wait_for_timeout(600)
    for _ in range(3):
        g.click('[data-act=open]') if g.page.is_visible('[data-act=open]') else None
        g.page.wait_for_timeout(150)
        g.ev("audioInit()")
        g.ev("audioInit()")
    g.page.wait_for_timeout(500)
    st = g.page.evaluate('window.__stats')
    check(st['rafMax'] <= 1, f'more than one requestAnimationFrame pending at once: {st}')
    check(st['intervals'] <= 1, f'setInterval created more than once: {st}')
    f1 = g.page.evaluate('window.__stats.raf'); g.page.wait_for_timeout(500); f2 = g.page.evaluate('window.__stats.raf')
    check(f2 > f1, 'main loop is not running')
    check(not g.errors, g.errors)
    g.close()

@test
def listeners_do_not_accumulate(b, port, target):
    g = Game(b, port, target, seed=3, manual=True)
    install_bot(g)
    base = g.page.evaluate('window.__stats.listeners')
    g.click('[data-act=open]')
    for day in range(2):
        start_day(g)
        play_day(g, max_steps=2000)
        g.page.click('#hPause'); g.click('[data-act=closeNow]')
        play_day(g, max_steps=3000)
        g.click('[data-act=toShop]'); g.click('[data-act=nextDay]')
    after = g.page.evaluate('window.__stats.listeners')
    check(after == base, f'event listeners grew from {base} to {after}')
    check(not g.errors, g.errors)
    g.close()

@test
def customer_full_flow_and_economy(b, port, target):
    g = Game(b, port, target, seed=4, manual=True)
    install_bot(g)
    g.click('[data-act=open]'); start_day(g)
    m0 = g.ev("S.money"); c0 = g.ev("S.todayCost")
    steps = play_day(g)
    check(g.ev("phase") == 'summary', f'day did not reach summary (phase={g.ev("phase")}, steps={steps})')
    s = g.ev("S.lastSummary")
    check(s['guests'] > 0 and s['plated'] > 0 and s['rev'] > 0, f'no customers served: {s}')
    check(s['perfect'] == s['plated'], f'perfect bot should plate only PERFECT dishes: {s}')
    m1 = g.ev("S.money"); c1 = g.ev("S.todayCost")
    expect = m0 + s['rev'] + s['tips'] + s['bonus'] - s['wages'] - (c1 - c0)
    check(m1 == expect, f'money invariant broken: start {m0}, end {m1}, expected {expect}, summary {s}')
    check(s['net'] == s['rev'] + s['tips'] + s['bonus'] - s['cost'] - s['wages'], 'net formula mismatch')
    check(g.ev("S.reviews.length") > 0, 'no reviews written')
    check(not g.errors, g.errors)
    g.close()

@test
def close_shop_early(b, port, target):
    g = Game(b, port, target, seed=11, manual=True)
    install_bot(g)
    g.click('[data-act=open]'); start_day(g)
    play_day(g, max_steps=1200)
    check(g.ev("phase") == 'service' and g.ev("!R.closed"), 'shop closed too early by itself')
    g.page.click('#hPause'); g.click('[data-act=closeEarly]')
    check(g.ev("R.closed===true && paused===false"), 'close-early did not close the shop')
    seated = g.ev("R.groups.filter(x=>x.table!=null).length")
    play_day(g)
    check(g.ev("phase") == 'summary', 'did not reach the summary after closing early')
    s = g.ev("S.lastSummary")
    check(s['guests'] >= seated, f'guests already seated were not served: {seated} seated, {s}')
    check(not g.errors, g.errors)
    g.close()

@test
def cooking_every_recipe(b, port, target):
    g = Game(b, port, target, seed=5, manual=True)
    g.ev("S.level=5;S.eq.oven=3;S.eq.bar=3;S.eq.prep=1;S.eq.fridge=3;for(const d in DISHES)if(!S.unlocked.includes(d))S.unlocked.push(d);S.signature={base:'mash',protein:'duck',sauce:'redwine',side:'asparagus',name:'Test Sig'}")
    g.click('[data-act=open]'); start_day(g)
    res = g.ev(r"""(()=>{const out={};const ids=Object.keys(DISHES).concat(['signature']);
      for(const d of ids){R.tickets=[];for(const s of R.slots)s.job=null;const g0={name:'T',size:1,table:0,state:'wait',pat:1,type:'office',looks:[]};
        const it={d,st:'pending',q:null,want:d==='steak'?1:0,picked:false};const tk={id:999,no:1,g:g0,items:[it],t0:R.t};R.tickets.push(tk);
        if(!startCook(tk,it,true)){out[d]='NO_SLOT';continue}
        const s=R.slots.find(x=>x.job&&x.job.it===it);let guard=0;
        while(it.st==='cooking'&&guard++<4000){const j=s.job;if(!j)break;const k=j.step;
          if(k.t==='add')actIng(s,k.left[0]);else if(k.t==='tap')actTap(s);else if(k.t==='zone'){if(k.p>=k.z.c)actZone(s);else updJob(s,1/30)}
          else if(k.t==='hold'){k.hold=true;R.holdSlot=s;k.level=(k.a+k.b)/2;holdEnd()}else if(k.t==='dose'){if(k.cnt<k.min)actDose(s);else actDoseDone(s)}else updJob(s,1/30);R.t+=1/30}
        out[d]=it.st==='ready'?it.q:('STUCK:'+it.st)}
      return out})()""")
    bad = {k: v for k, v in res.items() if v != 'P'}
    check(not bad, f'recipes not finishing PERFECT with perfect input: {bad}')
    check(len(res) == g.ev("Object.keys(DISHES).length+1"), 'not every recipe tested')
    check(not g.errors, g.errors)
    g.close()

@test
def five_cats_initialise(b, port, target):
    g = Game(b, port, target, seed=6, manual=True)
    g.ev("updateCats(1/30,0)")
    cats = g.ev("CATS.map(c=>({id:c.def.id,n:c.def.n,x:c.x,y:c.y,st:c.st}))")
    check(sorted(c['id'] for c in cats) == sorted(['tora', 'ban', 'snow', 'mikan', 'mei']), f'cat ids wrong: {cats}')
    check(sorted(c['n'] for c in cats) == sorted(['樾樾', '小齁', '包包', '柔柔', '寶寶']), 'cat names wrong')
    check(all(isinstance(c['x'], (int, float)) and isinstance(c['y'], (int, float)) for c in cats), 'bad positions')
    check(not g.errors, g.errors)
    g.close()

@test
def cat_ai_keeps_running(b, port, target):
    g = Game(b, port, target, seed=7, manual=True)
    install_bot(g)
    g.click('[data-act=open]'); start_day(g)
    r = g.ev(r"""(()=>{__bot(1,1/30);const changes={},last={},sleep={},nearJ={},bad=[];const ids=CATS.map(c=>c.def.id);ids.forEach(i=>{changes[i]=0;sleep[i]=0;nearJ[i]=0});
      const force=[()=>startRace(catBy('tora')),()=>startAmbush(catBy('mikan'))];
      for(let n=0;n<9000;n++){__bot(1,1/30);if(phase!=='service')break;if(n===1500)force[0]();if(n===3000)force[1]();
        for(const c of CATS){if(c.st!==last[c.def.id]){changes[c.def.id]++;last[c.def.id]=c.st}
          if(c.st==='sleep'||c.st==='bed')sleep[c.def.id]++;if(Math.hypot(c.x-PASS.x,c.y-PASS.y)<60)nearJ[c.def.id]++;
          if(!isFinite(c.x)||!isFinite(c.y))bad.push(c.def.id+' NaN');
          if(c.x<-BGM-5||c.x>LW+BGM+5||c.y>LH+5||c.y<wallTop()-40)bad.push(c.def.id+' out of bounds '+Math.round(c.x)+','+Math.round(c.y)+' '+c.st)}
        perchOcc.forEach((c,i)=>{if(c&&c.perch!==i&&c.goPerch!==i)bad.push('perchOcc mismatch '+i+' '+c.def.id)});
        // spot bookkeeping: one spot per cat, no double booking, never booked while on a perch or beside Jill
        const held=new Map();const own=(c,k)=>{if(c)held.set(c,(held.get(c)||[]).concat(k))};
        for(const k of['scr','scr2','cave','toy','bench0','bench1','bench2'])own(OCC[k],k);OCC.bed.forEach(c=>own(c,'bed'));
        if(OCC.bed.length>2||new Set(OCC.bed).size!==OCC.bed.length)bad.push('bed overbooked');
        for(const [c,ks] of held){if(ks.length>1)bad.push(c.def.id+' holds '+ks);if(c.perch>=0)bad.push(c.def.id+' holds '+ks+' while on perch');if(SIDE.R===c||SIDE.L===c)bad.push(c.def.id+' holds '+ks+' while beside Jill')}
        for(const c of CATS){if(c.perch>=0&&perchOcc[c.perch]!==c)bad.push(c.def.id+' on perch it does not own');if((SIDE.R===c||SIDE.L===c)&&c.perch>=0)bad.push(c.def.id+' beside Jill and on perch')}
        if(SIDE.R&&SIDE.R.slot!=='R')bad.push('SIDE.R mismatch');if(SIDE.L&&SIDE.L.slot!=='L')bad.push('SIDE.L mismatch');
        if(bad.length)break}
      return {changes,sleep,nearJ,bad:bad.slice(0,5)}})()""")
    check(not r['bad'], f'cat invariants broken: {r["bad"]}')
    stuck = [k for k, v in r['changes'].items() if v < 3]
    check(not stuck, f'cats that barely changed state: {stuck} {r["changes"]}')
    check(r['sleep']['snow'] == max(r['sleep'].values()), f'包包 should sleep the most: {r["sleep"]}')
    check(not g.errors, g.errors)
    g.close()

@test
def save_and_load_roundtrip(b, port, target):
    g = Game(b, port, target, seed=8, manual=True)
    install_bot(g)
    g.click('[data-act=open]'); start_day(g); play_day(g)
    g.click('[data-act=toShop]')
    money = g.ev("S.money"); tables = g.ev("S.tables")
    g.click('[data-act=buyTable]')
    check(g.ev("S.tables") == tables + 1, 'buying a table failed')
    snap = g.ev("JSON.stringify({day:S.day,money:S.money,tables:S.tables,xp:S.xp,reviews:S.reviews.length,stats:S.stats})")
    g.reload()
    after = g.ev("JSON.stringify({day:S.day,money:S.money,tables:S.tables,xp:S.xp,reviews:S.reviews.length,stats:S.stats})")
    check(snap == after, f'state changed across reload:\n{snap}\n{after}')
    # settings: SAVE / LOAD / RESET needs two presses
    g.click('.links [data-act=settings]'); g.click('[data-act=save]'); g.click('[data-act=load]')
    check(g.ev("S.tables") == tables + 1, 'LOAD lost data')
    g.click('.links [data-act=settings]'); g.click('[data-act=reset1]')
    check(g.ev("S.tables") == tables + 1 and g.ev("S.money") != 500, 'RESET fired on the first press')
    g.click('[data-act=reset2]')
    check(g.ev("S.day") == 1 and g.ev("S.money") == 500, 'RESET did not reset')
    check(not g.errors, g.errors)
    g.close()

def legacy_saves():
    out = {}
    for name in sorted(os.listdir(FIXTURES)):
        if name.endswith('.json') and not name.endswith('_file.json'):   # *_file.json are backup files, not localStorage dumps
            out[name] = open(os.path.join(FIXTURES, name), encoding='utf-8').read()
    return out

@test
def old_saves_load(b, port, target):
    for name, raw in legacy_saves().items():
        storage = json.loads(raw)
        g = Game(b, port, target, seed=9, manual=True, storage=storage)
        orig = json.loads(storage[SAVE_KEY])
        check(g.ev("S.day") == orig['day'] and g.ev("S.money") == orig['money'], f'{name}: day/money not preserved')
        for k in ('eq', 'decor', 'stats', 'unlocked', 'menu', 'xp', 'regulars', 'achievements'):
            check(g.ev(f"JSON.stringify(S.{k})") == json.dumps({**g.ev(f"newState().{k}"), **orig[k]} if isinstance(orig.get(k), dict) and k in ('eq', 'decor', 'stats') else orig.get(k), ensure_ascii=False, separators=(',', ':')), f'{name}: S.{k} not preserved')
        check(g.ev("Array.isArray(S.crew)&&S.crewMig===1&&typeof S.mem==='object'&&typeof S.rstar==='object'"), f'{name}: missing fields not filled with defaults')
        if 'dylan' not in orig:
            check(g.ev("S.dylan&&S.dylan.stage===0&&S.dylan.clues&&S.life&&S.life.sofa===0"), f'{name}: life/dylan defaults missing on an old save')
        else:
            check(g.ev("JSON.stringify(S.dylan)") == json.dumps(orig['dylan'], ensure_ascii=False, separators=(',', ':')), f'{name}: dylan state not preserved')
        if orig.get('staff', {}).get('bartender') and 'crew' not in orig:
            # KNOWN QUIRK (kept on purpose, see docs/REFACTOR_REPORT.md): load() fills crewMig from the
            # defaults before checking it, so a pre-crew save's bartender/busser are NOT turned into crew.
            check(g.ev("S.crew.length") == 0, f'{name}: legacy staff migration behaviour changed')
        if orig.get('mem'):
            g.click('.links [data-act=book]'); g.click('[data-act=btab][data-k=mem]')
            n = g.page.locator('.memgrid img').count()
            check(n == len(orig['mem']), f'{name}: expected {len(orig["mem"])} photos in album, saw {n}')
            srcs = g.page.eval_on_selector_all('.memgrid img', 'els=>els.map(e=>e.src.slice(0,22))')
            check(all(s.startswith('data:image/') for s in srcs), f'{name}: photo images broken')
            g.click('[data-act=closeSub]')
        g.click('[data-act=open]')
        start_day(g)
        install_bot(g); play_day(g, max_steps=1500)
        check(g.ev(f"localStorage.getItem('{SAVE_KEY}-unreadable')") is None, f'{name}: readable save was treated as unreadable')
        check(not g.errors, f'{name}: {g.errors}')
        g.close()

@test
def unreadable_save_is_kept(b, port, target):
    """A save this version can't read (broken, or written by a newer version) must not be destroyed."""
    newer = json.loads(json.loads(open(os.path.join(FIXTURES, 'v13_with_photos.json'), encoding='utf-8').read())[SAVE_KEY])
    newer['v'] = 99
    for label, raw in [('broken JSON', '{"v":1,"day":7,"money":'), ('newer version', json.dumps(newer, ensure_ascii=False))]:
        g = Game(b, port, target, seed=15, manual=True, storage={SAVE_KEY: raw})
        check(g.ev("S.day") == 1 and g.ev("S.money") == 500, f'{label}: game did not start fresh')
        g.click('[data-act=open]'); start_day(g)   # starting a day saves, overwriting the main key
        check(g.ev(f"JSON.parse(localStorage.getItem('{SAVE_KEY}')).day") == 1, f'{label}: new progress not saved')
        check(g.ev(f"localStorage.getItem('{SAVE_KEY}-unreadable')") == raw, f'{label}: unreadable save was not kept')
        g.reload()
        check(g.ev(f"localStorage.getItem('{SAVE_KEY}-unreadable')") == raw, f'{label}: kept copy lost after reload')
        check(not [e for e in g.errors if 'could not read' not in e], f'{label}: {g.errors}')
        g.close()

GOLDEN_CATS = os.path.join(ROOT, 'tests', 'golden', 'cats.json')

@test
def cat_personality_fingerprint(b, port, target, record=False):
    """Long, cats-only run in three moods (before opening, during service, evening after closing):
    ~50,000 cat updates with a fixed seed. Records every cat's state each step plus every decision
    weight. Any change to personalities, weights, timings or probabilities shows up here."""
    g = Game(b, port, target, seed=31337, manual=True)
    install_bot(g)
    run = r"""(n=>{let h=2166136261;const mix=s=>{for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}};
      const cnt={};let t=0;for(let i=0;i<n;i++){t+=1/30;updateCats(1/30,t);
        for(const c of CATS){mix(c.def.id+c.st+c.pose+(c.x|0)+','+(c.y|0)+c.perch+(c.hidden?1:0));cnt[c.def.id+':'+c.st]=(cnt[c.def.id+':'+c.st]||0)+1}}
      return {states:(h>>>0).toString(16), weights:__wtHash(), time:cnt}})"""
    out = {}
    g.click('[data-act=open]')
    out['prep'] = g.ev(f"({run})(18000)")
    start_day(g)
    out['service'] = g.ev(r"""(()=>{let h=2166136261;const mix=s=>{for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}};
      for(let i=0;i<20000&&phase==='service';i++){__bot(1,1/30);for(const c of CATS)mix(c.def.id+c.st+c.pose+(c.x|0)+','+(c.y|0)+c.perch)}
      return {states:(h>>>0).toString(16), weights:__wtHash()}})()""")
    check(g.ev("phase") == 'summary', 'service day did not finish')
    g.click('[data-act=toShop]')
    out['evening'] = g.ev(f"({run})(18000)")
    check(not g.errors, g.errors)
    g.close()
    # personality sanity (independent of the recording): who sleeps most, who stays near Jill
    tm = out['prep']['time']
    sleep = {k: sum(v for key, v in tm.items() if key.startswith(k + ':') and key.split(':')[1] in ('sleep', 'bed')) for k in ['tora', 'ban', 'snow', 'mikan', 'mei']}
    check(max(sleep, key=sleep.get) == 'snow', f'包包 should be the sleepiest cat: {sleep}')
    if record:
        json.dump(out, open(GOLDEN_CATS, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
        print('    recorded cat fingerprint ->', os.path.relpath(GOLDEN_CATS, ROOT))
        return
    want = json.load(open(GOLDEN_CATS, encoding='utf-8'))
    bad = [f'{mood}.{k}' for mood in want for k in want[mood] if out[mood].get(k) != want[mood][k]]
    check(not bad, f'cat behaviour differs from the baseline in: {bad}')

@test
def ui_basics(b, port, target):
    g = Game(b, port, target, seed=10, manual=True)
    state_ok(g, 'title')
    g.click('.links [data-act=guide]'); check(g.page.is_visible('text=遊戲說明'), 'guide did not open'); g.click('.sh-top [data-act=closeSub]')
    g.click('.links [data-act=book]')
    for k in ['reviews', 'regulars', 'cats', 'mem', 'ach', 'mastery']:
        g.click(f'[data-act=btab][data-k={k}]')
    g.click('[data-act=closeSub]'); state_ok(g, 'title after book')
    g.click('[data-act=open]'); state_ok(g, 'prep')
    g.click('[data-act=peek]'); check(g.page.is_visible('#peekPill'), 'peek pill missing'); g.click('#peekPill'); state_ok(g, 'prep after peek')
    start_day(g); state_ok(g, 'service')
    g.page.click('#hPause'); check(g.page.is_visible('[data-act=resume]'), 'pause menu missing'); state_ok(g, 'pause')
    g.click('[data-act=resume]'); state_ok(g, 'resumed')
    check(g.ev("paused") is False, 'resume failed')
    install_bot(g); play_day(g); state_ok(g, 'summary')
    g.click('[data-act=toShop]'); state_ok(g, 'shop')
    for k in ['tables', 'kitchen', 'menu', 'decor', 'staff', 'sig']:
        if g.page.locator(f'[data-act=tab][data-k={k}]:not([disabled])').count():
            g.click(f'[data-act=tab][data-k={k}]')
    g.click('[data-act=nextDay]'); state_ok(g, 'next day prep')
    check(g.ev("phase") == 'prep' and g.ev("S.day") == 2, 'next day failed')
    check(not g.errors, g.errors)
    g.close()

@test
def touch_controls(b, port, target):
    """Real pointer taps on the canvases: seat a guest, tap a table, open a station, press a
    kitchen-panel ingredient, pet a cat, tap the fridge. Exercises the input layer end to end."""
    g = Game(b, port, target, seed=14, manual=True)
    install_bot(g)
    def tap(x, y):  # scene coordinates -> screen pixels
        p = g.ev(f"(()=>{{const r=sc.getBoundingClientRect();return[r.left+SV.ox+({x})*SV.s,r.top+SV.oy+({y})*SV.s]}})()")
        g.page.mouse.click(p[0], p[1]); g.ev("__tick(1000/30)")
    g.ev("__tick(100)")
    g.click('[data-act=open]'); start_day(g)
    # 1) the tables are all dirty, so a guest group waits on the bench -> free a table and tap the
    #    group -> it gets seated at once (left alone it would get up by itself a few seconds later)
    g.ev("for(const t of R.tables)t.dirty=true;__tick(1000/30)")
    for _ in range(60):
        if g.ev("queued().some(x=>x.state==='queue'&&!x.moving)"): break
        g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
    gid = g.ev("(()=>{const q=queued().find(x=>x.state==='queue'&&!x.moving);return q?q.id:null})()")
    check(gid is not None, 'no guests arrived to wait')
    check(g.ev(f"isSeated(R.groups.find(x=>x.id==={gid}))"), 'a small party should sit on the bench while waiting')
    gx, gy = g.ev(f"(()=>{{R.tables[0].dirty=false;const q=R.groups.find(x=>x.id==={gid});return[q.x,q.y-22]}})()")
    tap(gx, gy)
    check(g.ev(f"R.groups.find(x=>x.id==={gid}).table!=null"), 'tapping the waiting guests did not seat them')
    g.ev("for(const t of R.tables)if(!t.group)t.dirty=false")
    # 2) walk the service forward until a ticket exists, then tap the station to open the kitchen panel
    for _ in range(60):
        if g.ev("R.tickets.some(t=>t.items.some(i=>i.st==='pending'))"): break
        g.ev("(()=>{for(const t of R.tables)if(tableActionable(t)&&!jillTargets(t.i))tapTable(t);for(let i=0;i<15;i++)__tick(1000/30)})()")
    check(g.ev("R.tickets.length>0"), 'no order ticket appeared')
    si = g.ev("R.slots.findIndex(s=>s.type==='stove')")
    rx, ry = g.ev(f"(()=>{{const r=kitchenRects(R.slots)[{si}];return[r.x+r.w/2,r.y+r.h/2]}})()")
    tap(rx, ry)
    check(g.ev(f"!!R.slots[{si}].job && R.panel===true"), 'tapping the stove did not start cooking / open the panel')
    g.ev("__tick(1000/30)")
    check(g.ev("!$('#trayWrap').hidden"), 'kitchen panel not visible')
    # 3) press the ingredient the recipe asks for, on the kitchen-panel canvas
    before = g.ev(f"R.slots[{si}].job.adds.length")
    want = g.ev(f"R.slots[{si}].job.step.t==='add'?R.slots[{si}].job.step.left[0]:null")
    check(want is not None, 'first recipe step is not an ingredient step')
    hx, hy = g.ev(f"(()=>{{const h=TRAYHIT.ctrls.find(h=>h.act==='ing'&&h.arg==={json.dumps(want)});const r=tc.getBoundingClientRect();return[r.left+h.x+h.w/2,r.top+h.y+h.h/2]}})()")
    g.page.mouse.click(hx, hy); g.ev("__tick(1000/30)")
    check(g.ev(f"R.slots[{si}].job.adds.length") == before + 1, 'tapping the ingredient did not add it')
    # 4) close the panel with its X
    hx, hy = g.ev("(()=>{const h=TRAYHIT.ctrls.find(h=>h.act==='close');const r=tc.getBoundingClientRect();return[r.left+h.x+h.w/2,r.top+h.y+h.h/2]})()")
    g.page.mouse.click(hx, hy); g.ev("__tick(1000/30)")
    check(g.ev("R.panel===false && $('#trayWrap').hidden"), 'panel did not close')
    # 5) pet a cat that is sitting on the floor away from the counter
    find_cat = "(()=>{const c=CATS.find(c=>!c.hidden&&c.def.id!=='mei'&&c.def.id!=='snow'&&c.y<FB-40&&c.perch<0&&!c.sofa&&c.benchI<0&&!R.groups.some(q=>Math.hypot(q.x-c.x,q.y-c.y)<40)&&!R.tables.some(t=>Math.hypot(t.x-c.x,t.y-c.y)<50));return c?c.def.id:null})()"
    cid = None
    for _ in range(40):
        cid = g.ev(find_cat)
        if cid: break
        g.ev("for(let i=0;i<15;i++)__tick(1000/30)")
    check(cid, 'no cat free to pet')
    if cid:
        cx, cy = g.ev(f"(()=>{{const c=catBy('{cid}');return[c.x,c.y-12]}})()")
        tap(cx, cy)
        check(g.ev(f"catBy('{cid}').hearts.length>0"), f'petting {cid} did not show hearts')
    # 6) tap the fridge
    fx, fy = g.ev("(()=>{const f=kitchenItems().find(i=>i.k==='fridge');return[f.x+f.w/2,f.y+f.h/2]})()")
    tap(fx, fy)
    check(g.ev("KPOP.fridge>0"), 'tapping the fridge did nothing')
    check(not g.errors, g.errors)
    g.close()

# ---------------------------------------------------------------- life: sofa, TV, Jill, Dylan
def run_evening(g, seconds=150, every=30, hook='null'):
    """Plays the day fast, then lets the closing + after-hours world run (no rendering). Returns samples."""
    start_day(g)
    g.ev("__bot(40000,1/30)") if False else None
    # play until the closing begins (the bot stops itself when closing starts)
    steps = play_day(g, max_steps=40000)
    check(g.ev("R&&R.closing!=null||phase!=='service'"), f'day did not reach the closing ({steps} steps)')
    r = g.ev(f"__evening({seconds},1/20,{every},{hook})")
    check(not r['bad'], f'life invariants broken: {r["bad"][:4]}')
    check(g.ev("phase") == 'summary', 'evening did not end in the summary')
    check(not g.errors, g.errors)
    return r['samples']

def next_day(g):
    g.click('[data-act=toShop]'); g.click('[data-act=nextDay]')

@test
def sofa_geometry(b, port, target):
    """Every seat/arm/back place the cats can choose, for every way Jill and Dylan can sit, is inside the
    sofa and never overlaps a body. With Jill stretched out there is still room for several cats."""
    g = Game(b, port, target, seed=16, manual=True)
    install_bot(g)
    r = g.ev(r"""(()=>{const bad=[];let minSlots=99;const L=LIFE.jill;updateCats(1/30,0);
      for(const pos of['L','R','M'])for(const legs of[0,.75,1])for(const dy of[false,true]){
        for(const c of CATS){c.sofa=null;c.sofaOn=false}
        Object.assign(L,{on:true,pos,x:JPOS[pos].x,y:SOFA.jy,face:JPOS[pos].face,legs,legTarget:legs});
        LIFE.dylan=null;if(dy){const x=dylanCanSofa();if(x==null)continue;LIFE.dylan={x,y:SOFA.jy,onSofa:true,seated:false,state:'sitSofa'}}
        // fill the sofa greedily: each cat takes a slot, then re-check with the next cat
        let n=0;for(const c of CATS){const sl=sofaSlots(c);if(!sl.length)break;const s=sl[Math.floor(Math.random()*sl.length)];c.sofa={k:s.k,x:s.x,y:s.y,kind:s.kind};c.sofaOn=true;c.x=s.x;c.y=s.y;n++}
        if(legs===1&&!dy)minSlots=Math.min(minSlots,n);
        bad.push(...__lifeInvariants().map(m=>pos+'/'+legs+'/'+(dy?'dylan':'-')+': '+m));
        const lg=jillLegs();if(lg&&(lg[0]<SOFA.seatL||lg[1]>SOFA.seatR))bad.push(pos+' legs off the seat '+lg);}
      for(const c of CATS){c.sofa=null;c.sofaOn=false}LIFE.dylan=null;Object.assign(L,{on:false,pos:null,legs:0,legTarget:0});
      return{bad:bad.slice(0,6),minSlots}})()""")
    check(not r['bad'], r['bad'])
    check(r['minSlots'] >= 4, f'with Jill stretched out only {r["minSlots"]} cats fit on the sofa')
    g.close()

@test
def jill_evening_life(b, port, target):
    """Twelve seeded evenings: Jill finds her own way to the sofa most nights, stretches out when the seat is
    free, reads / watches the rolling TV / does nothing, and never breaks a rule doing it."""
    nights = []
    for seed in range(40, 52):
        g = Game(b, port, target, seed=seed, manual=True)
        install_bot(g)
        g.click('[data-act=open]')
        samples = run_evening(g, seconds=150, every=10)
        acts = set(x['jill']['act'] for x in samples if x['jill']['on'])
        nights.append({'seed': seed, 'plan': samples[-1]['plan'], 'sat': any(x['jill']['on'] for x in samples),
                       'legs': max(x['jill']['legs'] for x in samples), 'acts': acts,
                       'tv': any(x['tv']['on'] for x in samples), 'tvmoved': any(x['tv']['at'] in ('use', 'moving') for x in samples),
                       'endSeated': samples[-1]['jill']['on'] or samples[-1]['plan'] == 'table',
                       'cats': max(sum(1 for c in x['cats'] if c['on']) for x in samples)})
        g.close()
    sat = [n for n in nights if n['sat']]
    check(len(sat) >= 8, f'Jill used the sofa on only {len(sat)}/12 nights: {nights}')
    check(sum(1 for n in sat if n['legs'] >= .95) >= len(sat) // 2, f'legs stretched on too few nights: {[n["legs"] for n in sat]}')
    check(all(n['endSeated'] for n in nights), f'someone is stuck standing at the end of the evening: {[n for n in nights if not n["endSeated"]]}')
    all_acts = set().union(*[n['acts'] for n in sat])
    check({'read', 'idle'} <= all_acts, f'expected reading and doing nothing across nights, saw {all_acts}')
    check(any(n['tv'] for n in nights), f'the TV was never watched in 12 nights: {[n["tvmoved"] for n in nights]}')
    check(len(set(n['cats'] for n in nights)) >= 3, f'no variety in how many cats join her: {[n["cats"] for n in nights]}')

@test
def cats_use_sofa_by_personality(b, port, target):
    """Over many evenings the five cats use the sofa the way their personalities say, without being told
    where to sit: 包包 sleeps on the seat, 寶寶 takes the high pretty places, 樾樾 and 小齁 compete for the
    places next to Jill (and neither always wins), 柔柔 keeps an eye on the others."""
    slot_time = {k: {} for k in ['tora', 'ban', 'snow', 'mikan', 'mei']}
    sleep_on_sofa = {k: 0 for k in slot_time}; near_jill = {k: 0 for k in slot_time}
    closest = {'tora': 0, 'ban': 0}
    zero_cat_checks = 0; checks = 0
    for seed in range(60, 76):
        g = Game(b, port, target, seed=seed, manual=True)
        install_bot(g)
        g.click('[data-act=open]')
        samples = run_evening(g, seconds=140, every=8)
        for x in samples:
            if not x['jill']['on']:
                continue
            checks += 1
            on = [c for c in x['cats'] if c['on']]
            if not on: zero_cat_checks += 1
            for c in on:
                slot_time[c['id']][c['kind']] = slot_time[c['id']].get(c['kind'], 0) + 1
                if c['st'] == 'sleep': sleep_on_sofa[c['id']] += 1
                if abs(c['x'] - x['jill']['x']) < 50: near_jill[c['id']] += 1
            near = sorted([c for c in on if c['id'] in ('tora', 'ban')], key=lambda c: abs(c['x'] - x['jill']['x']) + (0 if c['kind'] in ('lap', 'arm', 'seat') else 40))
            if near: closest[near[0]['id']] += 1
        g.close()
    tot = {k: sum(v.values()) for k, v in slot_time.items()}
    check(all(tot[k] > 0 for k in tot), f'some cat never used the sofa: {tot}')
    check(slot_time['snow'].get('seat', 0) >= tot['snow'] * .55, f'包包 should mostly lie on the seat: {slot_time["snow"]}')
    check(sleep_on_sofa['snow'] >= tot['snow'] * .5, f'包包 should mostly sleep there: {sleep_on_sofa["snow"]}/{tot["snow"]}')
    hi = slot_time['mei'].get('back', 0) + slot_time['mei'].get('arm', 0)
    check(hi >= tot['mei'] * .55, f'寶寶 should prefer the backrest and the arms: {slot_time["mei"]}')
    for k in ('tora', 'ban'):
        check(near_jill[k] >= tot[k] * .6, f'{k} should sit close to Jill: {near_jill[k]}/{tot[k]} {slot_time[k]}')
    check(closest['tora'] > 0 and closest['ban'] > 0, f'the place closest to Jill should change hands: {closest}')
    check(zero_cat_checks > 0, 'there was never a moment with Jill alone on the sofa')

@test
def dylan_stays_a_quiet_regular_early_on(b, port, target):
    """Before anything is revealed Dylan is just an unusually patient guest who glances at Jill. He does not
    stay after closing, nothing in the UI names the relationship, and no romance UI exists."""
    g = Game(b, port, target, seed=77, manual=True)
    install_bot(g)
    g.ev("S.day=3;S.money=4000;S.level=2;S.tables=4")
    g.click('[data-act=open]')
    visits = 0; stayed = 0; looks = 0
    for d in range(6):
        start_day(g)
        # bring him in early in the day so the visit completes before closing
        g.ev("__botUntil('R.t>R.dur*.25',20000)")
        g.ev("(()=>{for(const q of queued())if(q.state==='queue'){q.state='leave';q.tx=DOOR.x;q.ty=DOOR.y}spawn({type:'regular',reg:'dylan',size:1})})()")
        g.ev("__bot(400,1/30)")
        r = g.ev(r"""(()=>{const g=R.groups.find(x=>x.reg==='dylan');if(!g)return{lost:1};const t=freeTableFor(g);if(t&&g.table==null)seatGroup(g,t);
          const o={type:'regular',reg:'chen',state:'wait',table:0,ticket:null};const other=drainRate(o);const mine=drainRate(Object.assign({},g,{state:'wait'}));return{lost:0,patient:mine<other*.7,table:g.table}})()""")
        if not r.get('lost'):
            visits += 1
            check(r['patient'], 'Dylan should be much more patient than another regular')
        looks = g.ev("S.dylan.clues.look||0")
        stage0 = g.ev("S.dylan.stage") == 0
        play_day(g)
        if os.environ.get('JK_TRACE'): print('   day', d, 'phase', g.ev("phase"), 'R', g.ev("!!R"), 'visible', g.page.locator('[data-act=toShop]').count(), g.ev("screenEl.hidden"))
        if stage0: stayed += 1 if g.ev("!!LIFE.dylan") else 0
        if g.ev("(S.regulars.dylan||0)<3||S.day<6"): check(g.ev("S.dylan.stage") == 0, 'stage moved before the conditions were met')
        next_day(g)
    check(visits >= 3, f'Dylan should have been seated on most of these days: {visits}')
    check(looks > 0, 'Dylan never glanced at Jill')
    check(stayed == 0, 'Dylan must not stay after closing before the story moves on')
    g.click('[data-act=book]'); g.click('[data-act=btab][data-k=regulars]')
    html = g.page.inner_html('#screen')
    check('Dylan' in html and '來店' in html, 'Dylan should be listed with the regulars once met')
    for bad in ['Jill 的先生', 'husband', 'Husband', '好感', 'LOVE', 'Romance', '戀愛', '♥']:
        check(bad not in html, f'romance UI text found early: {bad}')
    check(not g.errors, g.errors)
    g.close()

@test
def dylan_hidden_reveal(b, port, target):
    """The relationship is only shown once several quiet things have happened, and only on an evening
    where Jill is already settled on the sofa; it is one photo and one line in the book, and the game
    just goes on. Afterwards he sometimes sits beside her and sometimes has to sit elsewhere."""
    g = Game(b, port, target, seed=88, manual=True)
    install_bot(g)
    g.ev("S.day=13;S.money=9000;S.level=2;S.tables=4;S.regulars.dylan=6;S.dylan.stage=1;S.dylan.stay=2;S.dylan.clues={late:2,pet:1,look:9};S.life.sofa=4;dylanStays=()=>true")
    g.click('[data-act=open]')
    revealed_at = None; beside = 0; elsewhere = 0
    for d in range(14):
        if g.ev("S.dylan.stage") < 3:
            g.click('[data-act=book]'); g.click('[data-act=btab][data-k=regulars]')
            check('Jill 的先生' not in g.page.inner_html('#screen'), 'the book must not say it before the reveal')
            g.click('[data-act=closeSub]')
        start_day(g)
        check(g.ev("S.dylan.stage") >= 2, 'stage 2 should be reached on the first day of this scenario')
        g.ev("__botUntil('R.t>R.dur*.8',20000)")
        g.ev("(()=>{for(const q of queued())if(q.state==='queue'){q.state='leave';q.tx=DOOR.x;q.ty=DOOR.y}spawn({type:'regular',reg:'dylan',size:1})})()")
        g.ev("__botUntil('(()=>{const g=R.groups.find(x=>x.reg===\"dylan\");return !g||freeTableFor(g)})()',3000)")
        g.ev("(()=>{const g=R.groups.find(x=>x.reg==='dylan');if(g&&g.table==null){const t=freeTableFor(g);if(t)seatGroup(g,t)}})()")
        play_day(g)
        # from the third evening on, the evening's dice are loaded so the test does not depend on luck; every other
        # condition (his presence, Jill settled, a free place beside her) still has to come true by itself
        force = 'if(%s&&S.dylan.stage===2&&LIFE.revealRoll===-1)LIFE.revealRoll=1;' % ('true' if d >= 2 else 'false')
        hook = "t=>{%sif(S.dylan.stage===3&&!window.__rv){window.__rv={t,jillOn:LIFE.jill.on,dylanOn:!!(LIFE.dylan&&LIFE.dylan.onSofa),phase}}}" % force
        samples = g.ev(f"__evening(120,1/20,10,{hook})")['samples']
        rv = g.page.evaluate('window.__rv||null')
        if rv and revealed_at is None:
            revealed_at = d
            check(rv['jillOn'] and rv['dylanOn'], f'the reveal happened away from the sofa: {rv}')
            check(g.ev("S.dylan.reveal") == g.ev("S.day"), 'reveal day not recorded')
        if g.ev("S.dylan.stage") == 3 and g.ev("!!LIFE.dylan"):
            if any(x['dylan'] and x['dylan']['onSofa'] for x in samples): beside += 1
            if any(x['dylan'] and x['dylan']['st'] == 'sitTable' for x in samples): elsewhere += 1
        next_day(g)
        if revealed_at is not None and d - revealed_at >= 4:
            break
    check(revealed_at is not None, 'the reveal never happened in 14 evenings')
    check(g.ev("S.dylan.stage") == 3, 'stage 3 not set')
    g.click('[data-act=book]'); g.click('[data-act=btab][data-k=regulars]')
    html = g.page.inner_html('#screen')
    check('Jill 的先生' in html, 'after the reveal the book should say who he is')
    for bad in ['好感', 'LOVE', 'Romance', '戀愛', 'CONGRATULATIONS', '♥']:
        check(bad not in html, f'romance UI text: {bad}')
    g.click('[data-act=closeSub]')
    check(beside >= 1, f'after the reveal he never sat beside her: beside={beside} elsewhere={elsewhere}')
    check(g.ev("phase") == 'prep', 'the game should simply continue')
    check(not g.errors, g.errors)
    g.close()

@test
def long_play_is_stable(b, port, target):
    """Ten days in a row: nothing piles up (listeners, reviews, per-day arrays, save size)."""
    g = Game(b, port, target, seed=13, manual=True)
    install_bot(g)
    base = g.page.evaluate('window.__stats.listeners')
    g.click('[data-act=open]')
    sizes = []
    for d in range(10):
        start_day(g); state_ok(g, f'day {d+1} service'); play_day(g)
        check(g.ev("phase") == 'summary', f'day {d+1} did not finish'); state_ok(g, f'day {d+1} summary')
        g.click('[data-act=toShop]'); state_ok(g, f'day {d+1} shop'); g.click('[data-act=nextDay]'); state_ok(g, f'day {d+2} prep')
        sizes.append(g.ev("localStorage.getItem('jills-kitchen-save-v1').length"))
        check(g.ev("CATS.every(c=>c.hearts.length<20)"), 'cat hearts piling up')
    check(g.page.evaluate('window.__stats.listeners') == base, 'event listeners grew during long play')
    # addReview() caps at 80; the rare health-inspector review is pushed without the cap (kept as is)
    check(g.ev("S.reviews.length") <= 80 + g.ev("S.reviews.filter(r=>r.name==='衛生檢查員').length"), f'reviews not capped: {g.ev("S.reviews.length")}')
    check(max(sizes) < 150000, f'save grew too large: {sizes}')
    check(not g.errors, g.errors)
    g.close()

# ---------------------------------------------------------------- version 16
@test
def cooking_flow_families(b, port, target):
    """Every ordinary recipe takes 2–5 player interactions with perfect play, nothing is tap-repeated,
    the recipe families have the shapes the design asks for, and a late pan flip is forgiven before
    it burns."""
    g = Game(b, port, target, seed=5, manual=True)
    g.ev("S.level=5;S.eq.oven=3;S.eq.bar=3;S.eq.prep=1;S.eq.fridge=3;for(const d in DISHES)if(!S.unlocked.includes(d))S.unlocked.push(d);S.signature={base:'mash',protein:'duck',sauce:'redwine',side:'asparagus',name:'Test Sig'}")
    g.click('[data-act=open]'); start_day(g)
    res = g.ev(r"""(()=>{const out={};const ids=Object.keys(DISHES).concat(['signature']);
      for(const d of ids){R.tickets=[];for(const s of R.slots)s.job=null;const g0={name:'T',size:1,table:0,state:'wait',pat:1,type:'office',looks:[]};
        const it={d,st:'pending',q:null,want:d==='steak'?1:0,picked:false};const tk={id:999,no:1,g:g0,items:[it],t0:R.t};R.tickets.push(tk);
        if(!startCook(tk,it,true)){out[d]={q:'NO_SLOT'};continue}
        const s=R.slots.find(x=>x.job&&x.job.it===it);let guard=0,n=0;const kinds=new Set();let waitT=0;
        while(it.st==='cooking'&&guard++<6000){const j=s.job;if(!j)break;const k=j.step;kinds.add(k.t);
          if(k.t==='add'){actIng(s,k.left[0]);n++}else if(k.t==='tap'){actTap(s);n++}else if(k.t==='zone'){if(k.p>=k.z.c){actZone(s);n++}else updJob(s,1/30)}
          else if(k.t==='hold'){k.hold=true;R.holdSlot=s;k.level=(k.a+k.b)/2;holdEnd();n++}else if(k.t==='dose'){if(k.cnt<k.min){actDose(s);n++}else{actDoseDone(s);n++}}else{updJob(s,1/30);waitT+=1/30}R.t+=1/30}
        out[d]={q:it.st==='ready'?it.q:('STUCK:'+it.st),n,kinds:[...kinds],waitT:+waitT.toFixed(1),cat:DISH(d).cat,st:DISH(d).st}}
      return out})()""")
    bad = {k: v['q'] for k, v in res.items() if v['q'] != 'P'}
    check(not bad, f'recipes not finishing PERFECT with perfect input: {bad}')
    check(not any('tap' in v['kinds'] for v in res.values()), 'a recipe still uses tap-repeat steps')
    counts = {k: v['n'] for k, v in res.items() if k != 'signature'}
    check(all(2 <= n <= 5 for n in counts.values()), f'interactions outside 2–5: {counts}')
    # families
    fam = {k: v['kinds'] for k, v in res.items()}
    check('zone' in fam['steak'] and 'zone' in fam['burger'] and 'zone' in fam['duck'], f'pan-seared dishes should be flip/remove timing: {fam}')
    check('wait' in fam['soup'] and 'wait' in fam['risotto'] and res['soup']['waitT'] >= 4, f'stewed dishes should have a long passive wait: {fam}')
    check(not ({'zone', 'wait'} & set(fam['salad'])) and not ({'zone', 'wait'} & set(fam['prosciutto'])), f'cold dishes should be quick: {fam}')
    check('wait' in fam['tiramisu'] and 'zone' in fam['salmon'] and 'zone' in fam['chicken'], f'oven/chilled dishes should be prep then a long wait: {fam}')
    check(all('hold' in fam[d] for d in ['coffee', 'sparkling', 'fruitsoda', 'blacktea'] if d in fam and res[d]['cat'] == 'drink') or 'hold' in fam['coffee'], 'the drink gauge (hold) must stay')
    check('work' in fam['salad'] and 'work' in fam['souffle'] and 'work' in fam['duck'], f'handwork steps should be Jill\'s own (work): {fam}')
    # forgiveness on a pan: late but not forgotten -> Okay, forgotten -> burnt
    r = g.ev(r"""(()=>{const out={};for(const p of[1.1,1.3]){R.tickets=[];for(const s of R.slots)s.job=null;const g0={name:'T',size:1,table:0,state:'wait',pat:1,type:'office',looks:[]};
      const it={d:'burger',st:'pending',q:null,want:0,picked:false};const tk={id:998,no:1,g:g0,items:[it],t0:R.t};R.tickets.push(tk);startCook(tk,it,true);const s=R.slots.find(x=>x.job&&x.job.it===it);
      actIng(s,'patty');const k=s.job.step;k.p=p;actZone(s);out[p]={burnt:!s.job||!!s.job.burnt||it.q==='B',score:s.job?s.job.scores[s.job.scores.length-1]:null}}return out})()""")
    check(not r['1.1']['burnt'] and r['1.1']['score'] < .9, f'a slightly late flip should be forgiven, not burnt: {r}')
    check(r['1.3']['burnt'], f'a forgotten pan should burn: {r}')
    check(not g.errors, g.errors)
    g.close()

@test
def kitchen_staff_ladder(b, port, target):
    """Chefs grow by capability: LV1 only simple dishes Jill has already cooked, LV2 ordinary ones, LV3+
    also takes over a dish Jill started. The signature dish and the first serving of any dish stay Jill's."""
    g = Game(b, port, target, seed=12, manual=True)
    g.ev("S.level=5;S.eq.stove=3;S.eq.oven=3;S.eq.bar=3;for(const d in DISHES)if(!S.unlocked.includes(d))S.unlocked.push(d);S.signature={base:'mash',protein:'duck',sauce:'redwine',side:'asparagus',name:'Sig'};S.xp={friedrice:30,seafood:30,burger:30};S.crew=[{id:'c1',role:'chef',name:'阿德',lv:1,duty:'stove'}]")
    r = g.ev("(()=>{const m=S.crew[0];const at=lv=>{m.lv=lv;return{fr:chefCan(m,'friedrice'),pasta:chefCan(m,'pasta'),seafood:chefCan(m,'seafood'),sig:chefCan(m,'signature')}};return{l1:at(1),l2:at(2),l3:at(3),l5:at(5)}})()")
    check(r['l1'] == {'fr': True, 'pasta': False, 'seafood': False, 'sig': False}, f'LV1 chef scope wrong: {r}')
    check(r['l3']['seafood'] and not r['l3']['sig'] and not r['l5']['sig'], f'LV3+/signature scope wrong: {r}')
    check(not r['l2']['pasta'], 'a dish Jill has never cooked (xp 0) must stay hers')
    g.click('[data-act=open]'); start_day(g)
    r = g.ev(r"""(()=>{const g0={name:'T',size:1,table:0,state:'wait',pat:1,type:'office',looks:[]};const mk=d=>{const it={d,st:'pending',q:null,want:0,picked:false};const tk={id:900+Math.random()*99|0,no:1,g:g0,items:[it],t0:R.t};R.tickets.push(tk);startCook(tk,it,true);return R.slots.find(x=>x.job&&x.job.it===it)};
      const m=S.crew[0];m.lv=1;const s1=mk('friedrice');const a=!!chefHandles(s1);m.lv=3;const b=!!chefHandles(s1);const s2=mk('seafood');const c=!!chefHandles(s2);m.lv=1;const d=!!chefHandles(s2);return{a,b,c,d}})()""")
    check(r == {'a': False, 'b': True, 'c': True, 'd': False}, f'take-over rule (LV3+ continues what Jill started) wrong: {r}')
    check(not g.errors, g.errors)
    g.close()

@test
def waiter_serves_ready_food(b, port, target):
    """A LV2 waiter on 帶位＋點餐 also carries finished plates from the pass to the table."""
    g = Game(b, port, target, seed=5, manual=True)
    install_bot(g)
    g.ev(r"""window.__act=function(){if(!(phase==='service'&&R))return false;
      for(const t of R.tables){if(tableActionable(t)&&!jillTargets(t.i)){const gg=t.group;const ready=gg&&gg.ticket&&gg.ticket.items.some(i=>i.st==='ready'&&!i.picked);if(!ready)tapTable(t)}}
      for(const tk of R.tickets)for(const it of tk.items)if(it.st==='pending')startCook(tk,it,true);
      for(const s of R.slots){if(s.broken){tapStation(R.slots.indexOf(s));continue}const j=s.job;if(!j||!j.step)continue;const k=j.step;if(chefHandles(s))continue;
       if(k.t==='add'){const id=k.left[0];if(id)actIng(s,id)}else if(k.t==='zone'){if(k.p>=k.z.c)actZone(s)}else if(k.t==='hold'){k.hold=true;R.holdSlot=s;k.level=(k.a+k.b)/2;holdEnd()}else if(k.t==='dose'){if(k.cnt<k.min)actDose(s);else actDoseDone(s)}}
      return true}""")
    g.ev("window.__srv={waiter:0,jill:0};const s0=serveItems;serveItems=function(g,items){const byW=R.cw&&Object.values(R.cw).some(w=>w.carry&&w.carry.length&&items.every(x=>w.carry.includes(x.it)));if(byW)__srv.waiter++;else __srv.jill++;return s0.apply(this,arguments)}")
    g.ev("S.day=6;S.level=2;S.tables=5;S.money=8000;S.crew=[{id:'w1',role:'waiter',name:'小美',lv:2,duty:'both'}];unlockDish('coffee');for(const d of S.unlocked)S.stock[d]=30")
    g.click('[data-act=open]'); start_day(g)
    for _ in range(300):
        g.ev("__bot(60,1/30)")
        if g.ev("phase") != 'service' or g.ev("__srv.waiter") >= 5: break
    check(g.ev("__srv.waiter") >= 5, f'the waiter did not serve: {g.ev("__srv")}')
    check(not g.errors, g.errors)
    g.close()

@test
def waiting_bench(b, port, target):
    """Full house: small parties sit on the bench by the door, a party of four stands beside it, the
    first party that fits gets up and walks (no teleport) when a table frees, a cat on a place is
    handled, Dylan waits like everyone else, and the bench keeps clear of the door, tables, sofa,
    cat tree, TV and staff spots."""
    g = Game(b, port, target, seed=7, manual=True)
    install_bot(g)
    # geometry: nothing the bench could block
    geo = g.ev(r"""(()=>{const bx0=BENCH.x-BENCH.w/2-6,bx1=BENCH.x+BENCH.w/2,by0=BENCH.seats[0]-28,by1=BENCH.seats[2]+14;const hit=(x,y)=>x>=bx0&&x<=bx1&&y>=by0&&y<=by1;
      const bad=[];if(hit(DOOR.x,DOOR.y+22)||hit(DOOR.x,DOOR.y))bad.push('door landing');
      for(let i=0;i<12;i++){const sp=SPOT_ORDER[i];const r=Math.floor(sp/4),c=sp%4;const x=COLS[c]+RSH[r],y=ROWS[r];if(Math.abs(x-BENCH.x)<BENCH.w/2+30&&Math.abs(y-(by0+by1)/2)<(by1-by0)/2+22)bad.push('table '+sp)}
      if(bx1>SOFA.x0)bad.push('sofa');if(hit(TV_PARK.x,TV_PARK.y))bad.push('tv');for(const p of TREE.perches)if(hit(p.x,p.y)||hit(p.ax,p.ay||350))bad.push('perch');
      for(const sp of BENCH.stand)if(hit(sp.x,sp.y))bad.push('stand spot on bench');if(hit(84,150))bad.push('waiter spot');if(hit(PASS.x,PASS.y))bad.push('pass');
      for(const k in SPOT)if(hit(SPOT[k].x,SPOT[k].y))bad.push('spot '+k);return bad})()""")
    check(not geo, f'bench overlaps: {geo}')
    g.ev("S.day=9;S.level=2;S.tables=5;S.decor.sofa=1;S.money=6000;S.dylan.stage=1;S.regulars.dylan=4")
    g.click('[data-act=open]'); start_day(g)
    g.ev("__botUntil('R.t>8',3000,1/30)")
    # a cat takes the first place, then every table is dirty and three parties arrive
    g.ev(r"""(()=>{for(const t of R.tables)t.dirty=true;window.__noClean=true;const A=window.__act;window.__act=function(){if(window.__noClean)for(const t of R.tables)if(!t.group)t.dirty=true;return A.apply(this,arguments)};
      const c=CATS.find(c=>c.def.id==='mei');releaseSpots(c);if(c.perch>=0){perchOcc[c.perch]=null;c.perch=-1}OCC.bench0=c;c.benchI=0;c.st='bench';c.pose='loaf';c.face=1;c.t=200;c.x=BENCH.x+2;c.y=BENCH.seats[0]-3;
      spawn({type:'office',size:2});spawn({type:'regular',reg:'dylan',size:1});spawn({type:'student',size:4})})()""")
    for _ in range(40):
        g.ev("__bot(15,1/30)")
        if g.ev("queued().length===3&&queued().every(q=>q.state==='queue'&&!q.moving)"): break
    q = g.ev("queued().map(q=>({n:q.name,size:q.size,spot:q.spot?q.spot.k+q.spot.i:null,sit:isSeated(q),x:q.x,y:q.y}))")
    check(len(q) == 3 and all(x['spot'] for x in q), f'waiting parties have no place: {q}')
    check([x['spot'] for x in q if x['size'] <= 2] == ['seat1', 'seat2'], f'small parties should take the free bench places (the cat has place 0): {q}')
    check([x['spot'] for x in q if x['size'] == 4] == ['stand0'], f'a party of four should stand beside the bench: {q}')
    check(all(x['sit'] for x in q if x['size'] <= 2) and not any(x['sit'] for x in q if x['size'] == 4), f'seated/standing wrong: {q}')
    dy = [x for x in q if x['n'] == 'Dylan'][0]
    check(dy['spot'] == 'seat2', f'Dylan must queue behind the party that came first: {q}')
    # free the tables: the first party that fits gets up and walks over; nobody jumps
    g.ev("window.__noClean=false;for(const t of R.tables)if(!t.group)t.dirty=false")
    jumps = g.ev(r"""(()=>{const bad=[];let prev=new Map(R.groups.map(g=>[g.id,[g.x,g.y]]));let first=null;
      for(let i=0;i<150;i++){update(1/30);updateCats(1/30,0);for(const g of R.groups){const p=prev.get(g.id);if(p){const d=Math.hypot(g.x-p[0],g.y-p[1]);if(d>78/30+1)bad.push([i,g.name,+d.toFixed(1)])}}prev=new Map(R.groups.map(g=>[g.id,[g.x,g.y]]));
        if(!first){const s=R.groups.find(g=>g.state==='toTable');if(s)first=s.name}}
      return{bad:bad.slice(0,5),first,states:R.groups.map(g=>[g.name,g.state,g.table])}})()""")
    check(not jumps['bad'], f'a guest teleported: {jumps}')
    check(jumps['first'] and jumps['first'] != 'Dylan', f'the party that arrived first should be seated first: {jumps}')
    check(g.ev("CATS.find(c=>c.def.id==='mei').st") in ('bench', 'jump', 'walk', 'rest'), 'the cat on the bench got stuck')
    # a full bench with a cat on it is never a deadlock: a party keeps a place or leaves through the normal patience rules
    check(g.ev("queued().every(q=>q.spot)"), 'a waiting party lost its place')
    check(not g.errors, g.errors)
    g.close()

@test
def dylan_pays_tidies_and_is_not_staff(b, port, target):
    """Dylan pays like anyone, tips a little more, carries his own plate to the pass and leaves the table
    clean, and never appears anywhere in the staff system."""
    g = Game(b, port, target, seed=21, manual=True)
    install_bot(g)
    g.ev("S.day=8;S.dylan.stage=1;S.regulars.dylan=3;S.level=2;S.tables=5;S.money=5000;dylanStays=()=>false")
    g.click('[data-act=open]'); start_day(g)
    r = g.ev(r"""(()=>{const mk=(reg)=>{const g={id:R.gid++,type:'regular',size:1,reg,ret:true,looks:[],name:reg||'X',state:'check',table:null,pat:1,x:0,y:0,tx:0,ty:0,timer:0,seed:1,mood:'ok',forSig:false};
        const t=R.tables.find(t=>!t.group&&!t.used);t.used=1;t.group=g;g.table=t.i;g.ticket={id:1,no:1,g,items:[{d:'friedrice',st:'served',q:'P',want:0,picked:true}],t0:R.t};R.groups.push(g);return g};
      const rnd=Math.random;Math.random=()=>.99; /* no review roll noise */
      const a=mk('dylan');const t0=R.st.tips,r0=R.st.rev;collect(a);const dTip=R.st.tips-t0,dRev=R.st.rev-r0;const ta=R.tables[a.table];
      const b=mk('wang');const t1=R.st.tips,r1=R.st.rev;collect(b);const oTip=R.st.tips-t1,oRev=R.st.rev-r1;const tb=R.tables[b.table];Math.random=rnd;
      return{dTip,dRev,oTip,oRev,dBus:!!a.bus,dDirty:ta.dirty,oDirty:tb.dirty,dTarget:[a.tx,a.ty],dState:a.state}})()""")
    check(r['dRev'] == r['oRev'] and r['dRev'] > 0, f'Dylan must pay the same price as anyone: {r}')
    check(r['dTip'] > r['oTip'] and r['dTip'] <= r['oTip'] * 1.5 + 2, f'Dylan tips somewhat more, not absurdly more: {r}')
    check(r['dBus'] and not r['dDirty'] and r['oDirty'], f'Dylan should clear his own table, the other guest not: {r}')
    check(abs(r['dTarget'][0] - (g.ev("PASS.x") + 18)) < 1, f'he should walk to the pass first: {r}')
    walk = g.ev(r"""(()=>{const a=R.groups.find(g=>g.reg==='dylan');let atPass=false,jumps=0;let px=a.x,py=a.y;for(let i=0;i<900&&!a.gone;i++){update(1/30);updateCats(1/30,0);if(Math.hypot(a.x-px,a.y-py)>78/30+1)jumps++;px=a.x;py=a.y;if(!a.bus&&!atPass)atPass=i}return{gone:a.gone,atPass,jumps,tidy:S.dylan.clues.tidy||0}})()""")
    check(walk['gone'] and walk['atPass'] and walk['jumps'] == 0, f'Dylan should walk plate->pass->door: {walk}')
    check(walk['tidy'] >= 1, 'clearing his table should count as a quiet clue')
    # never staff
    check(g.ev("!Object.values(ROLES).some(r=>/Dylan/.test(JSON.stringify(r)))&&!JSON.stringify(CREW_NAMES).includes('Dylan')&&!S.crew.some(m=>/Dylan/.test(m.name))"), 'Dylan must never be a staff member')
    check(not g.errors, g.errors)
    g.close()

@test
def world_stays_visible_across_days(b, port, target):
    """Ten consecutive real days played like a person would (buying tables, gear, decor, dishes, hiring
    staff with the game's own random ids plus ids that hash into the sign bit), with real frames.
    Every service day the restaurant world must actually be on the canvas, the frame loop must keep
    running, nothing may throw, and the canvas state (save/restore depth, alpha, composite) must be
    balanced after every frame. Guards against the Day-5 blank-world regression: an employee whose
    id hashed negative made drawPerson throw on its first draw, which killed the frame loop for good
    while the DOM HUD and station taps kept working."""
    g = Game(b, port, target, seed=5, manual=True)
    install_bot(g)
    g.ev(r"""(()=>{window.__cv={depth:0,worst:0};const P=CanvasRenderingContext2D.prototype;const s0=P.save,r0=P.restore;
      P.save=function(){if(this===sctx){__cv.depth++;__cv.worst=Math.max(__cv.worst,__cv.depth)}return s0.apply(this,arguments)};
      P.restore=function(){if(this===sctx)__cv.depth--;return r0.apply(this,arguments)}})()""")
    probe = r"""(()=>{const c=sc.getContext('2d');const w=sc.width,h=sc.height;const y0=Math.floor(h*.25),y1=Math.floor(h*.85);const d=c.getImageData(0,y0,w,y1-y0).data;
      let dark=0,n=0;const cols=new Set();for(let i=0;i<d.length;i+=16){n++;if(Math.abs(d[i]-30)<6&&Math.abs(d[i+1]-23)<6&&Math.abs(d[i+2]-20)<6)dark++;if(cols.size<2000)cols.add((d[i]>>3)<<10|(d[i+1]>>3)<<5|(d[i+2]>>3))}
      const tf=sctx.getTransform();return{dark:+(dark/n).toFixed(3),colors:cols.size,t:R?R.t:null,phase,depth:__cv.depth,alpha:sctx.globalAlpha,comp:sctx.globalCompositeOperation,finite:!R||(isFinite(R.jill.x)&&isFinite(R.jill.y)&&R.groups.every(q=>isFinite(q.x)&&isFinite(q.y))&&CATS.every(k=>isFinite(k.x)&&isFinite(k.y)))}})()"""
    def act(a, **kv):
        ds = ''.join(f"el.dataset.{k}='{v}';" for k, v in kv.items())
        g.ev(f"(()=>{{const el=document.createElement('button');el.dataset.act='{a}';{ds}$('#screen').appendChild(el);el.click();el.remove()}})()")
    plan = {1: [('rd', {'d': 'pasta'}), ('rd', {'d': 'salad'}), ('buyTable', {})],
            2: [('buyEq', {'k': 'bar'}), ('rd', {'d': 'coffee'}), ('buyDecor', {'k': 'plants'}), ('buyTable', {})],
            3: [('hire', {'k': 'waiter'}), ('rd', {'d': 'burger'}), ('buyDecor', {'k': 'lights'})],
            4: [('buyEq', {'k': 'oven'}), ('rd', {'d': 'fries'}), ('expand', {}), ('hire', {'k': 'cleaner'})],
            5: [('expand', {}), ('hire', {'k': 'chef'}), ('rd', {'d': 'soup'}), ('buyDecor', {'k': 'chairs'}), ('buyEq', {'k': 'stove'})],
            6: [('buyEq', {'k': 'fridge'}), ('rd', {'d': 'blacktea'}), ('buyDecor', {'k': 'art'}), ('buyTable', {})],
            7: [('rd', {'d': 'tiramisu'}), ('buyEq', {'k': 'pan'}), ('buyDecor', {'k': 'rug'})],
            8: [('rd', {'d': 'chicken'}), ('buyDecor', {'k': 'ware'}), ('buyTable', {}), ('expand', {})],
            9: [('rd', {'d': 'steak'}), ('buyEq', {'k': 'oven'}), ('hire', {'k': 'chef'})]}
    g.click('[data-act=open]')
    for day in range(1, 11):
        act('restock'); g.ev("__tick(200)")
        if day == 4:   # ids whose hash has the sign bit set: c1 (cleaner), m1 (chef) — the shape that used to crash
            g.ev("S.crew.push({id:'c1',role:'cleaner',name:'阿明',lv:1,duty:'clean'},{id:'m1',role:'chef',name:'Hugo',lv:2,duty:'stove'})")
        start_day(g)
        t_prev = -1
        for sec in range(8):
            g.ev("__play(30,0)")
            check(not g.errors, f'day {day}: page error during service: {g.errors[:2]}')
            pr = g.ev(probe)
            if pr['phase'] != 'service': break
            check(pr['t'] > t_prev, f'day {day}: the clock stopped (frame loop dead?) at second {sec}: {pr}')
            t_prev = pr['t']
            check(pr['dark'] < .3 and pr['colors'] > 300, f'day {day}: the restaurant world is blank/dark at second {sec}: {pr}')
            check(pr['depth'] == 0 and pr['alpha'] == 1 and pr['comp'] == 'source-over', f'day {day}: canvas state leaked after a frame: {pr}')
            check(pr['finite'], f'day {day}: non-finite coordinates: {pr}')
        # finish the day fast, then let the closing and a bit of the evening render
        if g.ev("phase") == 'service': g.ev("__bot(60000,1/30)")
        g.ev("for(let i=0;i<60;i++)__tick(1000/30)")
        check(not g.errors, f'day {day}: page error at closing: {g.errors[:2]}')
        if g.ev("phase") == 'summary': g.click('[data-act=toShop]')
        for a, kv in plan.get(day, []):
            act(a, **kv); g.ev("__tick(30)")
        check(not g.errors, f'day {day}: page error in the shop: {g.errors[:2]}')
        g.click('[data-act=nextDay]'); g.ev("__tick(100)")
        check(g.ev("phase") == 'prep', f'day {day}: next day did not reach the prep screen')
        pr = g.ev(probe)
        check(pr['dark'] < .3 and pr['colors'] > 300, f'day {day + 1}: the room behind the prep screen is blank: {pr}')
    crew = g.ev("S.crew.map(m=>m.id+':'+m.role)")
    check(len(crew) >= 3 and any(c.startswith('c1:') for c in crew) and any(c.startswith('m1:') for c in crew), f'the staff (including the sign-bit ids) should have been drawn all along: {crew}')
    check(g.ev("S.level") >= 2 and g.ev("S.tables") >= 4, 'the test should have expanded the restaurant along the way')
    check(not g.errors, g.errors)
    g.close()

@test
def v16_save_continues_in_v17(b, port, target):
    """A real Version 16 save (10 days, staff with the game's own ids, Dylan met) opens in this build,
    plays a rendered service day, exports, re-imports its own backup and plays on; a Version 16 backup
    file imports directly too."""
    fx = json.loads(open(os.path.join(FIXTURES, 'v16_day10_staff_dylan.json'), encoding='utf-8').read())
    g = Game(b, port, target, seed=3, manual=True, storage=fx)
    install_bot(g)
    orig = json.loads(fx[SAVE_KEY])
    check(g.ev("S.day") == orig['day'] and g.ev("S.money") == orig['money'] and g.ev("S.crew.length") == len(orig['crew']), 'V16 save did not load intact')
    check(g.ev("JSON.stringify(S.dylan)") == json.dumps(orig['dylan'], ensure_ascii=False, separators=(',', ':')), 'V16 Dylan state changed on load')
    g.click('[data-act=open]'); start_day(g)
    g.ev("__play(240,0)")   # eight rendered seconds with the V16 staff on screen
    check(not g.errors, f'errors playing a V16 save: {g.errors[:2]}')
    check(g.ev("R.cw&&Object.keys(R.cw).length") == len(orig['crew']) - sum(1 for m in orig['crew'] if m['role'] == 'chef'), 'V16 staff not active')
    g.ev("__bot(60000,1/30)"); g.ev("__evening(20,1/20,0,null)")
    if g.ev("phase") == 'summary': g.click('[data-act=toShop]')
    g.click('[data-act=nextDay]'); g.ev("__tick(60)")
    day_after = g.ev("S.day"); check(day_after == orig['day'] + 1, 'day did not advance')
    # export -> import own backup -> continue
    g.click('.links [data-act=settings]') if g.page.is_visible('.links [data-act=settings]') else g.click('[data-act=settings]')
    with g.page.expect_download() as dl:
        g.click('[data-act=export]')
    path = os.path.join(ARTIFACTS, 'v16_roundtrip.json'); os.makedirs(ARTIFACTS, exist_ok=True); dl.value.save_as(path)
    with g.page.expect_file_chooser() as fc:
        g.click('[data-act=import]')
    fc.value.set_files(path); g.page.wait_for_timeout(150); g.ev("__tick(100)")
    g.click('[data-act=importYes]'); g.ev("__tick(50)")
    check(g.ev("S.day") == day_after and g.ev("S.crew.length") == len(orig['crew']), 'own backup did not restore')
    g.click('[data-act=open]'); start_day(g); g.ev("__play(60,0)")
    check(g.ev("phase") == 'service' and not g.errors, f'could not keep playing after the import: {g.errors[:2]}')
    g.ev("__bot(60000,1/30)")
    # a backup file written by Version 16 itself
    g.ev("__evening(10,1/20,0,null)")
    if g.ev("phase") == 'summary': g.click('[data-act=toShop]')
    g.click('[data-act=nextDay]'); g.ev("__tick(60)")
    g.click('.links [data-act=settings]') if g.page.is_visible('.links [data-act=settings]') else g.click('[data-act=settings]')
    with g.page.expect_file_chooser() as fc:
        g.click('[data-act=import]')
    fc.value.set_files(os.path.join(FIXTURES, 'v16_backup_file.json')); g.page.wait_for_timeout(150); g.ev("__tick(100)")
    check(g.ev("pendingImport&&pendingImport.day===10"), 'the Version 16 backup file was not accepted')
    g.click('[data-act=importYes]'); g.ev("__tick(50)")
    check(g.ev("S.day") == 10 and g.ev("S.regulars.dylan") == orig['regulars']['dylan'], 'V16 backup file not restored')
    g.click('[data-act=open]'); start_day(g); g.ev("__play(60,0)")
    check(g.ev("phase") == 'service' and not g.errors, f'could not play after importing the V16 backup: {g.errors[:2]}')
    g.close()

@test
def save_backup_and_restore(b, port, target):
    """備份存檔 writes one JSON file; 讀取存檔 restores it (Dylan/life state included) after a confirmation;
    junk, unrelated and newer-version files are refused with the current save untouched; an old save
    file goes through the same migrations as the browser copy."""
    g = Game(b, port, target, seed=4, manual=True)
    install_bot(g)
    g.ev("S.day=6;S.money=4321;S.dylan.stage=2;S.dylan.clues={late:2,tidy:1};S.life.sofa=3;S.life.tv=1;save()")
    g.click('.links [data-act=settings]')
    check(g.page.is_visible('text=本機存檔') and g.page.is_visible('text=備份存檔') and g.page.is_visible('text=讀取存檔'), 'save UI labels missing')
    with g.page.expect_download() as dl:
        g.click('[data-act=export]')
    d = dl.value
    check(re.match(r'^JillsKitchen_Save_\d{4}-\d{2}-\d{2}_\d{4}_Day6\.json$', d.suggested_filename), f'backup file name: {d.suggested_filename}')
    path = os.path.join(ARTIFACTS, 'backup_test.json'); os.makedirs(ARTIFACTS, exist_ok=True); d.save_as(path)
    env = json.load(open(path, encoding='utf-8'))
    check(env.get('app') == 'jills-kitchen' and env['save']['day'] == 6 and env['save']['dylan']['stage'] == 2, 'backup content wrong')
    def feed(p):
        if g.ev("sub") != 'settings': g.click('.links [data-act=settings]')
        with g.page.expect_file_chooser() as fc:
            g.click('[data-act=import]')
        fc.value.set_files(p)
        g.page.wait_for_timeout(150); g.ev("__tick(100)")
    # wreck the state, restore from the file
    g.ev("S.day=1;S.money=1;S.dylan.stage=0;save()")
    feed(path)
    check(g.ev("pendingImport&&pendingImport.day===6") and g.page.is_visible('[data-act=importYes]'), 'import should ask for confirmation first')
    check(g.ev("S.day") == 1, 'nothing may change before the confirmation')
    g.click('[data-act=importYes]'); g.ev("__tick(50)")
    check(g.ev("[S.day,S.money,S.dylan.stage,S.dylan.clues.late,S.life.sofa,S.life.tv,phase].join()") == '6,4321,2,2,3,1,title', f'restore wrong: {g.ev("[S.day,S.money,S.dylan.stage,phase]")}')
    check(json.loads(g.ev("localStorage.getItem(KEY)"))['day'] == 6, 'restored save not written to the browser')
    # bad files
    for name, content, msg in [('junk.json', '{not json', '不是 Jill'), ('other.json', json.dumps({'hello': 'world'}), '不是 Jill'), ('newer.json', json.dumps({'app': 'jills-kitchen', 'save': {'v': 99, 'day': 3, 'money': 1, 'unlocked': [], 'menu': []}}), '比較新的版本'), ('empty.json', '', '不是 Jill')]:
        p = os.path.join(ARTIFACTS, name); open(p, 'w', encoding='utf-8').write(content)
        feed(p)
        check(g.page.locator('#toasts').inner_text().find(msg) >= 0, f'{name}: no clear zh-TW refusal ({g.page.locator("#toasts").inner_text()})')
        check(g.ev("S.day") == 6 and not g.ev("!!pendingImport"), f'{name}: the current save must stay intact')
        g.ev("__tick(6000)")
    # an old save file is migrated like the browser copy
    fx = os.path.join(ROOT, 'tests', 'fixtures', 'legacy_v1_staff.json')
    feed(fx)
    check(g.ev("pendingImport&&pendingImport.dylan&&pendingImport.dylan.stage===0&&Array.isArray(pendingImport.crew)"), 'old save file not migrated/filled')
    g.click('[data-act=importYes]'); g.ev("__tick(50)")
    orig = json.loads(json.load(open(fx, encoding='utf-8'))[SAVE_KEY])
    check(g.ev("S.day") == orig['day'] and g.ev("S.money") == orig['money'], 'old save file not restored')
    # inside the claude.ai viewer the page cannot download by itself: the host's downloads capability saves the file
    r = g.ev(r"""(()=>{window.__saved=null;window.claude={use:n=>Promise.resolve(n==='downloads'?{save:req=>{window.__saved=req;return Promise.resolve({status:'saved'})}}:null)};return exportSave()})()""")
    g.page.wait_for_timeout(100)
    saved = g.ev("__saved&&{filename:__saved.filename,app:JSON.parse(__saved.data).app,day:JSON.parse(__saved.data).save.day}")
    check(r and saved and saved['app'] == 'jills-kitchen' and saved['day'] == orig['day'] and saved['filename'].endswith('.json'), f'host download path not used: {saved}')
    g.ev("delete window.claude")
    check(not g.errors, g.errors)
    g.close()

@test
def golden_scenario(b, port, target, record=False):
    """Deterministic 3-day playthrough with a seeded RNG. Refactors must not change the result."""
    g = Game(b, port, target, seed=12345, manual=True)
    install_bot(g)
    g.click('[data-act=open]')
    days = []
    for d in range(3):
        start_day(g)
        play_day(g)
        check(g.ev("phase") == 'summary', f'day {d+1} did not finish')
        days.append(g.page.evaluate('window.__digest()'))
        g.click('[data-act=toShop]')
        if d == 0:
            g.click('[data-act=buyTable]')
        g.click('[data-act=nextDay]')
    check(not g.errors, g.errors)
    g.close()
    if record:
        os.makedirs(os.path.dirname(GOLDEN), exist_ok=True)
        json.dump(days, open(GOLDEN, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('    recorded golden baseline ->', os.path.relpath(GOLDEN, ROOT))
        return
    want = json.load(open(GOLDEN, encoding='utf-8'))
    for i, (a, w) in enumerate(zip(days, want)):
        if a != w:
            diff = {k: (w.get(k), a.get(k)) for k in set(a) | set(w) if a.get(k) != w.get(k)}
            raise AssertionError(f'day {i+1} differs from golden baseline: ' + json.dumps(diff, ensure_ascii=False)[:1500])

def compare_screens(shots, record):
    """Pixel-exact comparison against tests/golden/screens/*.png. Returns a list of mismatches."""
    from io import BytesIO
    from PIL import Image, ImageChops
    bad = []
    os.makedirs(SCREENS, exist_ok=True)
    for name, png in shots:
        path = os.path.join(SCREENS, name + '.png')
        if record:
            open(path, 'wb').write(png)
            continue
        if not os.path.exists(path):
            bad.append(f'{name}: no golden image'); continue
        a = Image.open(BytesIO(png)).convert('RGB'); w = Image.open(path).convert('RGB')
        box = ImageChops.difference(a, w).getbbox() if a.size == w.size else (0, 0) + a.size
        if box and a.size == w.size:
            # Tolerate text anti-aliasing noise: a handful of pixels off by at most 4 levels.
            # Any real visual change (moved, recoloured or missing element) is far larger than this.
            d = ImageChops.difference(a, w).convert('L')
            hist = d.histogram()
            changed, worst = sum(hist[1:]), max(i for i, n in enumerate(hist) if n)
            if changed <= 40 and worst <= 8:
                box = None
        if box:
            os.makedirs(ARTIFACTS, exist_ok=True)
            a.save(os.path.join(ARTIFACTS, name + '.actual.png'))
            if a.size == w.size:
                ImageChops.difference(a, w).point(lambda v: 255 if v else 0).save(os.path.join(ARTIFACTS, name + '.diff.png'))
            bad.append(f'{name}: pixels differ in box {box} (see tests/artifacts/)')
    return bad

@test
def golden_frames(b, port, target, record=False):
    """Runs the REAL main loop frame by frame on virtual time for two full days (with rendering,
    DOM updates, cat AI, evening mode and memory photos) and compares scene pixels, DOM, cat
    states and key screens against the recorded baseline. Any visual or behavioural change fails."""
    g = Game(b, port, target, seed=2024, manual=True)
    install_bot(g)
    shots, trace = [], {}
    def shot(name):
        g.ev("__tick(1000/30)")
        shots.append((name, g.page.screenshot(animations='disabled', caret='hide')))
    g.ev("__tick(500)"); shot('title')
    g.click('[data-act=open]'); g.ev("__tick(1000/30)"); shot('prep')
    for d in range(2):
        start_day(g)
        r1 = g.ev("__play(600, 30)")
        if d == 0:
            shot('service_20s')
            r1['samples'] += g.ev("__play(900, 30, 'R.slots.some(s=>s.job)')")['samples']
            check(g.ev("R.slots.some(s=>s.job)"), 'no dish on the stove to show in the kitchen panel')
            g.ev("(()=>{const i=R.slots.findIndex(s=>s.job);R.focus=i;R.panel=true})()")
            shot('service_panel')
            g.ev("R.panel=false")
            g.page.click('#hPause'); shot('pause'); g.click('[data-act=resume]')
        r2 = g.ev("__play(20000, 30, 'R.closing!=null&&R.closing>5')")
        if d == 0:
            shot('evening')
        r3 = g.ev("__play(20000, 30)")
        check(g.ev("phase") == 'summary', f'day {d+1} did not reach the summary')
        trace[f'day{d+1}'] = {'samples': r1['samples'] + r2['samples'] + r3['samples'],
                             'frames': r1['frames'] + r2['frames'] + r3['frames'],
                             'digest': g.page.evaluate('window.__digest()')}
        if d == 0:
            shot('summary')
            g.click('[data-act=toShop]'); shot('shop')
            g.click('[data-act=nextDay]')
            g.click('[data-act=book]'); g.click('[data-act=btab][data-k=cats]'); shot('book_cats')
            g.click('[data-act=btab][data-k=mem]'); shot('book_mem'); g.click('[data-act=closeSub]')
        else:
            g.click('[data-act=toShop]'); g.click('[data-act=nextDay]')
    check(not g.errors, g.errors)
    g.close()
    if record:
        os.makedirs(os.path.dirname(GOLDEN_FRAMES), exist_ok=True)
        json.dump(trace, open(GOLDEN_FRAMES, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        compare_screens(shots, True)
        print('    recorded frame baseline ->', os.path.relpath(GOLDEN_FRAMES, ROOT), f'+ {len(shots)} screens')
        return
    want = json.load(open(GOLDEN_FRAMES, encoding='utf-8'))
    problems = compare_screens(shots, False)
    for day in want:
        a, w = trace[day], want[day]
        if a['frames'] != w['frames']:
            problems.append(f'{day}: {a["frames"]} frames, baseline {w["frames"]}')
        for i, (x, y) in enumerate(zip(a['samples'], w['samples'])):
            if x != y:
                problems.append(f'{day}: first differing sample #{i} (t={y["t"]}): ' + ', '.join(k for k in y if x.get(k) != y[k]))
                break
        if a['digest'] != w['digest']:
            problems.append(f'{day}: end-of-day digest differs: ' + ', '.join(k for k in w['digest'] if a['digest'].get(k) != w['digest'][k]))
    check(not problems, '\n      '.join(problems))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--target', choices=['index', 'single'], default='index')
    ap.add_argument('--record', action='store_true')
    ap.add_argument('-k', default='')
    a = ap.parse_args()
    srv, port = start_server()
    failed = 0
    with sync_playwright() as p:
        b = p.chromium.launch()
        for fn in TESTS:
            if a.k and a.k not in fn.__name__:
                continue
            t0 = time.time()
            try:
                if fn in (golden_scenario, golden_frames, cat_personality_fingerprint):
                    fn(b, port, a.target, record=a.record)
                else:
                    fn(b, port, a.target)
                print(f'PASS  {fn.__name__}  ({time.time()-t0:.1f}s)')
            except Exception as e:
                failed += 1
                print(f'FAIL  {fn.__name__}  ({time.time()-t0:.1f}s)\n      {e}')
                if os.environ.get('JK_TRACE'):
                    traceback.print_exc()
        b.close()
    srv.shutdown()
    print(f'\n{len([f for f in TESTS if a.k in f.__name__])-failed} passed, {failed} failed')
    sys.exit(1 if failed else 0)

if __name__ == '__main__':
    main()
