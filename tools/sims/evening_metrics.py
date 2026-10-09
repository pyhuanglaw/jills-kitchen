"""An evening's numbers for the release gate's balance table (the user, 2026-10-09: 每晚客人數、營收成本淨收益、平均與高百分位數的
等待時間、訂單完成率、工作站利用率、Jill 與員工的忙碌比例、因髒桌／餐具不足／料理瓶頸造成的損失). On the build in JK_GAME_JS
(default js/game.js): a new game's Day 1–3 and the user's Day 30, 52 and 92 saves, three seeds each, played by the test player who
leaves to the staff what they cover and taps the rest. One JSON line per evening:
  guests, lost (left waiting), angry; rev, cost, net (the day's summary);
  wait: seconds from being seated to the last plate of the order — mean and 90th percentile; done: served / (served + lost);
  st: each kind of station, the share of the evening it had work on it; busy: Jill, waiters, cleaners, cooks (share not idle);
  loss: queue-seconds while a dirty table stood, seconds tables waited on a full dish cart, work-seconds waiting in the kitchen.
  python3 tools/sims/evening_metrics.py TAG [fresh,day30,day52,day92]"""
import sys, os, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'tests')); os.chdir(ROOT)
TAG = sys.argv[1]; WHICH = (sys.argv[2] if len(sys.argv) > 2 else 'fresh,day30,day52,day92').split(','); sys.argv = [sys.argv[0]]
import run_tests as rt
import v24_tests as v
from playwright.sync_api import sync_playwright
SAVES = {'day30': 'player_day30.json', 'day52': 'player_day52.json', 'day92': 'player_day92_2105.json'}
HOOK = r"""(()=>{window.__m={waits:[],st:{},stT:0,qDirty:0,kWait:0,ck:{},ckT:0};
 if(!window.__mh){window.__mh=1;const S0=seatGroup;seatGroup=function(g,t){const r=S0.apply(this,arguments);if(g&&g.__seat==null)g.__seat=R.t;return r};
  const C0=checkAllServed;checkAllServed=function(g){const was=g&&g.state;const r=C0.apply(this,arguments);if(g&&was==='wait'&&g.state==='eat'&&g.__seat!=null&&!g.__w){g.__w=1;__m.waits.push(R.t-g.__seat)}return r}}
 window.__mStep=function(n){let k=0;const M=__m;for(let i=0;i<n;i++){if(!__act())break;update(1/30);updateCats(1/30,0);k++;if(!R||phase!=='service')break;if(R.closing!=null){if(R.closing>1&&!R.ended){finishClosing();break}continue}
   const dt=1/30;M.stT+=dt;for(const s of R.slots){if(!['stove','prep','oven','bar','pizza'].includes(s.type))continue;const o=M.st[s.type]||(M.st[s.type]={n:0,busy:0});o.n+=dt;if(s.wf||s.job)o.busy+=dt}
   const q=queued().filter(g=>g.state==='queue').length;if(q&&R.tables.some(t=>t.dirty&&!t.group))M.qDirty+=q*dt;
   M.kWait+=(typeof wfList==='function'?wfList().filter(n=>n.st==='wait'||n.st==='ready').length:R.tickets.reduce((a,tk)=>a+tk.items.filter(i=>i.st==='pending').length,0))*dt;   /* (main, before the cooking system: dishes not started yet) */
   for(const m of S.crew||[]){if(m.role!=='chef'||!R.ck||!R.ck[m.id])continue;const o=M.ck[m.id]||(M.ck[m.id]={t:0,b:0});o.t+=dt;if((R.wfc&&R.wfc[m.id]&&typeof wfNode==='function'&&wfNode(R.wfc[m.id]))||(R.ck[m.id].beat&&R.ck[m.id].beat.kind!=='idle'))o.b+=dt}}return k}})()"""
def busy(wl, role):
    r = (wl or {}).get(role) or {}
    tot = sum(r.values())
    return round(1 - r.get('idle', 0) / tot, 3) if tot else None
def evening(g):
    g.ev(HOOK)
    for _ in range(4000):
        if g.ev("phase") != 'service' or not g.ev("!!R"): break
        if g.page.evaluate('()=>window.__mStep(60)') < 60: break
    m = json.loads(g.ev("JSON.stringify(__m)"))
    end = json.loads(g.ev("JSON.stringify({s:S.lastSummary&&{guests:S.lastSummary.guests,lost:S.lastSummary.lost,angry:S.lastSummary.angry,rev:S.lastSummary.rev,cost:S.lastSummary.cost,wages:S.lastSummary.wages,net:S.lastSummary.net},wl:(S.lastSummary&&S.lastSummary.wl)||null})"))
    return m, end
srv, port = rt.start_server()
with sync_playwright() as p:
    b = p.chromium.launch()
    runs = []
    if 'fresh' in WHICH:
        for seed in (101, 202, 303): runs.append(('fresh', seed))
    for k in ('day30', 'day52', 'day92'):
        if k in WHICH:
            for seed in (1, 2, 3): runs.append((k, seed))
    for which, seed in runs:
        g = rt.Game(b, port, 'index', seed=(seed if which == 'fresh' else 500 + seed), manual=True, viewport={'width': 390, 'height': 844})
        days = (1, 2, 3) if which == 'fresh' else (0,)
        if which == 'fresh':
            rt.install_bot(g); g.click('[data-act=open]')
        else:
            v.load_save(g, SAVES[which]); g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}")
        for day in days:
            if which == 'fresh':
                if day == 3: g.ev("autoStock()")
                rt.start_day(g); g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;")
            else:
                v.to_service(g, lazy=True)
            g.ev("window.__wlKeep=null;{const E=endDay;endDay=function(){try{if(R&&R.st)window.__wlKeep=JSON.parse(JSON.stringify({wl:R.st.wl||null,dd:R.st.dd||null}))}catch(e){}return E.apply(this,arguments)}}")
            m, end = evening(g)
            keep = json.loads(g.ev("JSON.stringify(window.__wlKeep||{})"))
            wl, dd = keep.get('wl') or {}, keep.get('dd') or {}
            w = sorted(m['waits'])
            s = end['s'] or {}
            rec = {'tag': TAG, 'start': which, 'day': day if which == 'fresh' else None, 'seed': seed, **s,
                   'wait_mean': round(sum(w) / len(w), 1) if w else None, 'wait_p90': round(w[int(len(w) * .9) - 1 if len(w) >= 10 else -1], 1) if w else None,
                   'done': round(s.get('guests', 0) / max(1, s.get('guests', 0) + s.get('lost', 0)), 3),
                   'st': {k: round(o['busy'] / o['n'], 3) for k, o in m['st'].items() if o['n']},
                   'busy': {'jill': busy(wl, 'jill'), 'waiter': busy(wl, 'waiter'), 'cleaner': busy(wl, 'cleaner'), 'xq': busy(wl, 'xq'),
                            'cooks': round(sum(o['b'] for o in m['ck'].values()) / max(1e-9, sum(o['t'] for o in m['ck'].values())), 3) if m['ck'] else None},
                   'loss': {'queue_s_dirty_table': round(m['qDirty']), 'cart_full_block_s': round(dd.get('blockT', 0) or 0), 'kitchen_wait_s': round(m['kWait'])},
                   'errors': g.errors[:2]}
            print(json.dumps(rec, ensure_ascii=False), flush=True)
            if which == 'fresh':
                if g.ev("phase") == 'summary': g.click('[data-act=toShop]')
                if day < 3: g.click('[data-act=nextDay]')
        g.close()
    b.close()
srv.shutdown()
