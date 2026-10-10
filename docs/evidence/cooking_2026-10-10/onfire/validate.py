"""ON FIRE on the build in JK_GAME_JS: the user's saves (and staff variants) and a new game's first days, the lazy test player:
did tonight's fire come, when, how many tables had been served. One JSON line per evening."""
import sys, os, json
ROOT='/home/user/jills-kitchen'; sys.path.insert(0, os.path.join(ROOT,'tests')); os.chdir(ROOT)
WHICH=sys.argv[1].split(','); SEEDS=[int(x) for x in sys.argv[2].split(',')]; VARIANT=sys.argv[3] if len(sys.argv)>3 else ''
sys.argv=[sys.argv[0]]
import run_tests as rt
import v24_tests as v
from playwright.sync_api import sync_playwright
SAVES={'day30':'player_day30.json','day52':'player_day52.json','day92':'player_day92_2105.json'}
VAR={'':'','fewer_cooks':"(()=>{const cs=S.crew.filter(m=>m.role==='chef'&&m.pool==='restaurant');for(const m of cs.slice(Math.ceil(cs.length/2)))m.duty=null;return 1})()",
 'no_cooks':"(()=>{for(const m of S.crew)if(m.role==='chef'&&m.pool==='restaurant')m.duty=null;return 1})()"}
STEP=r"""window.__mStep=function(n){let k=0;for(let i=0;i<n;i++){if(!__act())break;update(1/30);updateCats(1/30,0);k++;if(!R||phase!=='service')break;if(R.fire>0&&!window.__fireAt)window.__fireAt=R.t;if(R.closing!=null){if(R.closing>1&&!R.ended){window.__fc=R.fireCount;finishClosing();break}continue}}return k}"""
srv, port = rt.start_server()
with sync_playwright() as p:
    b = p.chromium.launch()
    for which in WHICH:
        for seed in SEEDS:
            g = rt.Game(b, port, 'index', seed=500+seed, manual=True, viewport={'width':390,'height':844})
            if which.startswith('fresh'):
                days = int(which[5:] or 3); rt.install_bot(g); g.click('[data-act=open]')
                for d in range(1, days+1):
                    if d >= 3: g.ev("autoStock()")
                    rt.start_day(g); g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;"); g.ev("window.__fireAt=null;window.__fc=null;"+STEP)
                    for _ in range(4000):
                        if g.ev("phase") != 'service' or not g.ev("!!R"): break
                        if g.page.evaluate('()=>window.__mStep(60)') < 60: break
                    print(json.dumps({'start':'fresh','day':d,'seed':seed,'variant':VARIANT,'fires':g.ev("window.__fc"),'at':g.ev("window.__fireAt"),'guests':g.ev("S.lastSummary&&S.lastSummary.guests"),'errors':g.errors[:2]}), flush=True)
                    if g.ev("phase") == 'summary': g.click('[data-act=toShop]')
                    if d < days: g.click('[data-act=nextDay]')
            else:
                v.load_save(g, SAVES[which]); g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}")
                if VAR.get(VARIANT): g.ev(VAR[VARIANT])
                v.to_service(g, lazy=True); g.ev("window.__fireAt=null;window.__fc=null;"+STEP)
                for _ in range(4000):
                    if g.ev("phase") != 'service' or not g.ev("!!R"): break
                    if g.page.evaluate('()=>window.__mStep(60)') < 60: break
                print(json.dumps({'start':which,'seed':seed,'variant':VARIANT,'fires':g.ev("window.__fc"),'at':g.ev("window.__fireAt"),'guests':g.ev("S.lastSummary&&S.lastSummary.guests"),'level':g.ev("S.level"),'errors':g.errors[:2]}), flush=True)
            g.close()
    b.close()
srv.shutdown()
