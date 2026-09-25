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
import argparse, functools, http.server, json, os, socketserver, sys, threading, time, traceback

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
// One step of a perfect, deterministic player: seat, serve, cook every step exactly right.
window.__act = function(){
  if (!(phase==='service' && R)) return false;
  if (!R.closed) {
    for (const g of queued()) { if (g.state==='queue') { const t=freeTableFor(g); if (t) seatGroup(g,t); } }
  }
  for (const t of R.tables) { if (tableActionable(t) && !jillTargets(t.i)) tapTable(t); }
  for (const tk of R.tickets) for (const it of tk.items) if (it.st==='pending') startCook(tk,it,true);
  for (const s of R.slots) {
    const j=s.job; if (!j || !j.step) continue; const k=j.step;
    if (chefFor(s.type)) continue;
    if (s.broken) { tapStation(R.slots.indexOf(s)); continue; }
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
const __h = s => { let x=2166136261; for (let i=0;i<s.length;i++){ x^=s.charCodeAt(i); x=Math.imul(x,16777619);} return (x>>>0).toString(16); };
const __px = cv => { if (!cv || !cv.width || !cv.height) return '-'; const d=cv.getContext('2d').getImageData(0,0,cv.width,cv.height).data; const u=new Uint32Array(d.buffer); let x=2166136261; for (let i=0;i<u.length;i++) x=Math.imul(x^u[i],16777619); return (x>>>0).toString(16); };
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
           cats: __h(JSON.stringify((CATS||[]).map(c=>[c.def.id,c.st,c.pose,Math.round(c.x),Math.round(c.y),c.perch,!!c.hidden]))) };
};
window.__digest = function(){
  const cats = (CATS||[]).map(c=>[c.def.id,c.st,c.pose,Math.round(c.x),Math.round(c.y),c.perch,!!c.hidden]);
  const s = S.lastSummary ? {rev:S.lastSummary.rev,cost:S.lastSummary.cost,tips:S.lastSummary.tips,bonus:S.lastSummary.bonus,wages:S.lastSummary.wages,net:S.lastSummary.net,guests:S.lastSummary.guests,lost:S.lastSummary.lost,perfect:S.lastSummary.perfect,plated:S.lastSummary.plated,avg:S.lastSummary.avg,top:S.lastSummary.top,stars:S.lastSummary.stars} : null;
  return {day:S.day, money:S.money, lifetime:S.lifetime, level:S.level, stats:S.stats, xp:S.xp, stock:S.stock, reviews:S.reviews.length,
          reviewHash:__h(JSON.stringify(S.reviews.map(r=>[r.s,r.txt,r.name]))), regulars:S.regulars, summary:s, cats, catHash:__h(JSON.stringify(cats)),
          mem:Object.keys(S.mem||{}).sort().map(k=>k+':'+S.mem[k].day+':'+__h(S.mem[k].img))};
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
        for(const k of['scr','scr2','cave','toy'])own(OCC[k],k);OCC.bed.forEach(c=>own(c,'bed'));
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
        if name.endswith('.json'):
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
    # 1) a guest group arrives -> tap it -> it gets seated
    g.ev("__tick(1000/30)")
    for _ in range(40):
        if g.ev("queued().some(x=>x.state==='queue')"): break
        g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
    gid = g.ev("(()=>{const q=queued().find(x=>x.state==='queue');return q?q.id:null})()")
    check(gid is not None, 'no guests arrived to seat')
    gx, gy = g.ev(f"(()=>{{const q=R.groups.find(x=>x.id==={gid});return[q.x+6,q.y-22]}})()")
    tap(gx, gy)
    check(g.ev(f"R.groups.find(x=>x.id==={gid}).table!=null"), 'tapping the waiting guests did not seat them')
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
    cid = g.ev("(()=>{const c=CATS.find(c=>!c.hidden&&c.def.id!=='mei'&&c.def.id!=='snow'&&c.y<FB-40&&c.perch<0&&!R.groups.some(q=>Math.hypot(q.x-c.x,q.y-c.y)<40)&&!R.tables.some(t=>Math.hypot(t.x-c.x,t.y-c.y)<50));return c?c.def.id:null})()")
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
                if fn in (golden_scenario, golden_frames):
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
