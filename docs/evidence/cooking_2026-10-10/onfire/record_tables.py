"""ON FIRE calibration: the user's Day 30/52/92 saves (and staff variants), the lazy test player, fires off (FIRE_RUN=1e9 build in
JK_GAME_JS). Every table served: when, its wait from sitting down to the last plate, all Perfect, any of Jill's, how busy the room
was; every seated walkout. One JSON line per evening."""
import sys, os, json
ROOT='/home/user/jills-kitchen'; sys.path.insert(0, os.path.join(ROOT,'tests')); os.chdir(ROOT)
WHICH=sys.argv[1].split(','); SEEDS=[int(x) for x in sys.argv[2].split(',')]; VARIANT=sys.argv[3] if len(sys.argv)>3 else ''
sys.argv=[sys.argv[0]]
import run_tests as rt
import v24_tests as v
from playwright.sync_api import sync_playwright
SAVES={'day30':'player_day30.json','day52':'player_day52.json','day92':'player_day92_2105.json'}
VAR={'':'',
 'fewer_cooks':"(()=>{const cs=S.crew.filter(m=>m.role==='chef'&&m.pool==='restaurant');for(const m of cs.slice(Math.ceil(cs.length/2)))m.duty=null;return 1})()",
 'no_cooks':"(()=>{for(const m of S.crew)if(m.role==='chef'&&m.pool==='restaurant')m.duty=null;return 1})()"}
HOOK=r"""(()=>{window.__fe={tab:[],walk:0};if(!window.__fh){window.__fh=1;const F0=fireTable;fireTable=function(g){try{if(R&&g&&!g.__fr&&g.seatAt!=null){const its=(g.ticket&&g.ticket.items)||[];const ts=R.tables.filter(t=>!t.lounge);__fe.tab.push([+R.t.toFixed(1),+(R.t-g.seatAt).toFixed(1),its.every(it=>!it.q||it.q==='P')?1:0,its.some(it=>it.byJill)?1:0,+(ts.filter(t=>t.group).length/Math.max(1,ts.length)).toFixed(2)])}}catch(e){}return F0.apply(this,arguments)};
 const A0=angryLeave;angryLeave=function(g){try{if(g&&g.state!=='queue'&&g.state!=='arrive')__fe.tab.push([+R.t.toFixed(1),-1,0,0,0])}catch(e){}return A0.apply(this,arguments)}}
 window.__mStep=function(n){let k=0;for(let i=0;i<n;i++){if(!__act())break;update(1/30);updateCats(1/30,0);k++;if(!R||phase!=='service')break;if(R.closing!=null){if(R.closing>1&&!R.ended){finishClosing();break}continue}}return k}})()"""
srv, port = rt.start_server()
with sync_playwright() as p:
    b = p.chromium.launch()
    for which in WHICH:
        for seed in SEEDS:
            g = rt.Game(b, port, 'index', seed=500+seed, manual=True, viewport={'width':390,'height':844})
            v.load_save(g, SAVES[which]); g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}")
            if VAR.get(VARIANT): g.ev(VAR[VARIANT])
            v.to_service(g, lazy=True); g.ev(HOOK)
            for _ in range(4000):
                if g.ev("phase") != 'service' or not g.ev("!!R"): break
                if g.page.evaluate('()=>window.__mStep(60)') < 60: break
            fe = json.loads(g.ev("JSON.stringify(__fe)"))
            lv = g.ev("S.level"); ntab = g.ev("(S.tables||0)")
            print(json.dumps({'start':which,'variant':VARIANT,'seed':seed,'level':lv,'tab':fe['tab'],'guests':g.ev("S.lastSummary&&S.lastSummary.guests"),'errors':g.errors[:2]}), flush=True)
            g.close()
    b.close()
srv.shutdown()
