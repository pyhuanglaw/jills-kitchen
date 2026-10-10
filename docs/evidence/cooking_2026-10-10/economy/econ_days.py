"""Days 1-6 of a new game, the lazy test player: hire on Day 1's evening (policy) under a set of economy numbers (params),
then play on (stocking from Day 3 as the onboarding asks). One JSON line per day."""
import sys, os, json
ROOT='/home/user/jills-kitchen'; sys.path.insert(0, os.path.join(ROOT,'tests')); os.chdir(ROOT)
TAG=sys.argv[1]; PARAMS=json.loads(sys.argv[2]); POLICY=sys.argv[3]; SEEDS=[int(x) for x in sys.argv[4].split(',')]; DAYS=int(sys.argv[5]) if len(sys.argv)>5 else 6
sys.argv=[sys.argv[0]]
import run_tests as rt
from playwright.sync_api import sync_playwright
HOOK = r"""(()=>{window.__m={waits:[]};
 if(!window.__mh){window.__mh=1;const S0=seatGroup;seatGroup=function(g,t){const r=S0.apply(this,arguments);if(g&&g.__seat==null)g.__seat=R.t;return r};
  const C0=checkAllServed;checkAllServed=function(g){const was=g&&g.state;const r=C0.apply(this,arguments);if(g&&was==='wait'&&g.state==='eat'&&g.__seat!=null&&!g.__w){g.__w=1;__m.waits.push(R.t-g.__seat)}return r}}
 window.__mStep=function(n){let k=0;for(let i=0;i<n;i++){if(!__act())break;update(1/30);updateCats(1/30,0);k++;if(!R||phase!=='service')break;if(R.closing!=null){if(R.closing>1&&!R.ended){finishClosing();break}continue}}return k}})()"""
srv, port = rt.start_server()
with sync_playwright() as p:
    b = p.chromium.launch()
    for seed in SEEDS:
        g = rt.Game(b, port, 'index', seed=seed, manual=True, viewport={'width':390,'height':844})
        g.ev("(()=>{const P=%s;if(P.money!=null)S.money=P.money;for(const k of ['chef','waiter','cleaner'])if(P['hire_'+k]!=null)ROLES[k].hire=P['hire_'+k];window.__P=P;return 1})()" % json.dumps(PARAMS))
        rt.install_bot(g); g.click('[data-act=open]')
        hired = []
        for day in range(1, DAYS+1):
            if day >= 3: g.ev("autoStock()")
            rt.start_day(g); g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;"); g.ev(HOOK)
            m0 = g.ev("S.money")
            for _ in range(4000):
                if g.ev("phase") != 'service' or not g.ev("!!R"): break
                if g.page.evaluate('()=>window.__mStep(60)') < 60: break
            w = sorted(json.loads(g.ev("JSON.stringify(__m.waits)")))
            s = json.loads(g.ev("JSON.stringify(S.lastSummary&&{guests:S.lastSummary.guests,lost:S.lastSummary.lost,rev:S.lastSummary.rev,cost:S.lastSummary.cost,wages:S.lastSummary.wages,rent:S.lastSummary.rent,net:S.lastSummary.net,loan:S.lastSummary.loan,r1:S.lastSummary.r1})") or 'null') or {}
            loan = json.loads(g.ev("JSON.stringify(S.loan||null)"))
            rec = {'tag':TAG,'policy':POLICY,'seed':seed,'day':day,'money_start':m0,'money_end':g.ev("S.money"),**s,'wait':round(sum(w)/len(w),1) if w else None,'crew':g.ev("(S.crew||[]).map(m=>m.role[0]).join('')"),'owed':(loan or {}).get('owed',0),'errors':g.errors[:2]}
            if g.ev("phase") == 'summary': g.click('[data-act=toShop]')
            if day == 1 and POLICY != 'none':
                g.ev("shopTab='staff';showShop()"); g.page.wait_for_timeout(60)
                for k in (['waiter','chef'] if POLICY=='both' else [POLICY]):
                    sel = f'[data-act=hire][data-k={k}]'
                    if g.page.query_selector(sel) and g.ev(f"!document.querySelector('{sel}').disabled"):
                        g.click(sel); g.page.wait_for_timeout(60); hired.append(k)
                rec['hired'] = hired[:]; rec['money_after_hire'] = g.ev("S.money")
            print(json.dumps(rec, ensure_ascii=False), flush=True)
            if day < DAYS: g.click('[data-act=nextDay]')
        g.close()
    b.close()
srv.shutdown()
