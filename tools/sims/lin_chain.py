"""The Madame Lin line (the player, 2026-10-02 19:19): a save played forward day by day by the lazy bot. Each day prints
the line's beats that happened, who walked next door after dinner, the pairing glasses poured with dinner, Madame Lin's
and Ken's visits, and the day's major beats. The tasting's choice and the 「隔壁」 decision are answered as a player
might (food; 接下隔壁).

  python3 tools/sims/lin_chain.py SAVE DAYS [SEEDBASE=8200] [SETUP_JS]
  SHOTS=dir: the scenes play (held, as a player sees them) and a screenshot is taken of the lines named in WANT
"""
import sys, os, json, time, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, os.path.join(ROOT, 'tests'))
import run_tests as rt
from playwright.sync_api import sync_playwright

SAVE, DAYS = sys.argv[1], int(sys.argv[2])
SEEDBASE = int(sys.argv[3]) if len(sys.argv) > 3 else 8200
SETUP = sys.argv[4] if len(sys.argv) > 4 else ''
SHOTS = os.environ.get('SHOTS')
WANT = {'pairing_start': ['今晚那幾支', '想喝酒，隔壁就有'], 'lin_retire': ['我做到月底', '還沒有'], 'ken_where': ['她真的不做了', '不然吃完去哪'],
        'jd_want': ['Madame Lin 要退休了', '我有點想接', '那就先看看'], 'dylan_book': ['多了一本很大的書', '這你的', '看看。'],
        'lin_viewing': ['妳那邊有人接了嗎', '磨石子地', '推開後場的門', '妳廚房就在後面', '還有他', '你想留下', '有吧台就行'],
        'lin_sign': ['一起去隔壁', '吧台上放著合約', '那就這樣', '把鑰匙交給她', 'Evan，這', '你好。'], 'lin_guest': ['開門進來', '坐哪', '隨便', '喝什麼', '你選']}
RNG = "Math.random=(function(){let a=%d;return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
KEYS = ['lin_hello', 'ken_wine_q', 'ken_pairing', 'lounge_idea', 'tasting_night', 'pairing_wine', 'lin_retiring', 'ken_where', 'jd_want', 'dylan_book', 'lin_viewing', 'lounge_project', 'lin_take', 'lin_closed', 'lin_signed', 'evan_knows_dylan', 'lounge_built_1', 'lin_guest']
EVS = ['ken_tasting', 'tasting_start', 'pairing_start', 'lin_retire', 'ken_where', 'jd_want', 'dylan_book', 'lin_viewing', 'lin_decide', 'lin_last', 'lin_sign', 'lin_guest']
UNTIL = os.environ.get('UNTIL', 'decide')   # decide (Jill's decision and her last night) | open (the signing, the work, the opening) | guest (Madame Lin at The Lounge)


SEEN = {}
def held(g, day):
    """a held beat on screen: step through it, a screenshot of each wanted line"""
    for _ in range(60):
        if not g.ev("!!(typeof DLG!=='undefined'&&DLG)"): return
        k = g.ev("DLG&&DLG.sh?DLG.sh.k:(DLG&&DLG.lines&&DLG.lines[0]&&DLG.lines[0].k)||''") or 'scene'
        t = g.ev("(document.querySelector('#dlg .dlg-text')||{}).textContent||''")
        for w in WANT.get(k, []):
            if w in t and (k, w) not in SEEN:
                SEEN[(k, w)] = 1; g.ev("__tick(400);try{hud(true)}catch(e){};document.querySelectorAll('#plines>*,#toasts>*,#banner>*').forEach(e=>e.remove())"); g.page.wait_for_timeout(120)
                n = len([x for x in SEEN if x[0] == k])
                g.page.screenshot(path=os.path.join(SHOTS, f'{k}_{n}_day{day}.png')); print(f'   shot {k}_{n}_day{day}.png  「{t[:40]}」', flush=True)
        g.ev("__tick(300);dlgNext()")


def main():
    t0 = time.time()
    raw = json.load(open(SAVE)); save = raw.get('save', raw); save['checkpoint'] = None
    KEY = re.search(r"const KEY='([^']+)'", open(os.path.join(ROOT, 'js', 'game.js'), encoding='utf-8').read()).group(1)
    if SHOTS: os.makedirs(SHOTS, exist_ok=True)
    with sync_playwright() as p:
        srv, port = rt.start_server(); b = p.chromium.launch()
        g = rt.Game(b, port, 'index', seed=SEEDBASE, manual=True, viewport={'width': 390, 'height': 844}, storage={KEY: json.dumps(save, ensure_ascii=False)})
        g.click('[data-act=open]'); g.page.wait_for_timeout(150)
        if SETUP: g.ev(SETUP)
        g.ev("""window.__fastSay=1;window.__tr=[];const __st0=storyTrace;storyTrace=function(o){__tr.push(Object.assign({d:S.day},o));return __st0(o)};
          window.__vis=[];const __sp=spawn;spawn=function(o){const n0=R?R.groups.length:0;const r=__sp.apply(this,arguments);try{if(R&&R.groups.length>n0){const g=R.groups[R.groups.length-1];const nn=g&&namedId(g);if(nn==='Madame Lin'||nn==='品酒師 Ken')__vis.push({d:S.day,n:nn,t:Math.round(R.t/R.dur*100)})}}catch(e){}return r};
          window.__bar=[];const __so=sendOut;sendOut=function(g){if(g&&g.toBar&&barState()==='lin'&&!g.__barCounted){g.__barCounted=1;__bar.push({d:S.day,n:namedId(g)||g.type})}return __so.apply(this,arguments)}""")
        info = json.loads(g.ev("JSON.stringify({day:S.day,lv:S.level,dy:S.dylan.stage,ken:(story().named['品酒師 Ken']||{}).v,lin:(story().named['Madame Lin']||{}).v})"))
        print(f"{os.path.basename(SAVE)} from Day {info['day']} (level {info['lv']}, Dylan stage {info['dy']}, Ken visits {info.get('ken', 0)}, Madame Lin visits {info.get('lin', 0)}), seeds {SEEDBASE}+", flush=True)
        for d in range(DAYS):
            for _ in range(3):
                if g.ev("phase") == 'summary':
                    if not g.page.query_selector('[data-act=toShop]'):
                        print('   (no 「toShop」 on the summary: sub=%s, screen=%r)' % (g.ev("sub"), g.ev("($('#screen').innerText||'').slice(0,160)")), flush=True)
                        g.ev("sub=null;showSummary()"); g.page.wait_for_timeout(100)
                    g.click('[data-act=toShop]'); g.page.wait_for_timeout(80)
                if g.ev("phase") == 'shop':
                    if UNTIL != 'decide' and g.ev("!loungeLv()&&!!fact('lin_take')&&!!fact('lin_closed')&&!fact('lin_signed')&&!(S.loungeProj&&/signing|reno/.test(S.loungeProj.state||''))&&S.level>=LOUNGE_PROJ[0].need&&S.money>=LOUNGE_PROJ[0].cost"):
                        g.ev("shopTab='works';showShop()"); g.page.wait_for_timeout(60); g.click('#screen [data-act=linSign]'); g.page.wait_for_timeout(80)   # 簽約・開工, as a player would
                        print(f"   Day {g.ev('S.day')}: 簽約・開工 paid; state {g.ev('S.loungeProj.state')}", flush=True)
                    g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(120); g.ev("__tick(1200)")
                    if g.ev("!!$('#reveal')&&!$('#reveal').hidden"):
                        rv = g.ev("($('#reveal').innerText||'').replace(/\\n+/g,' | ').slice(0,120)"); print(f"   Day {g.ev('S.day')} morning: {rv}", flush=True)
                        if SHOTS: g.page.screenshot(path=os.path.join(SHOTS, f"lounge_opens_day{g.ev('S.day')}.png"))
                        g.ev("hideReveal()")
            g.ev("for(let i=0;i<80&&typeof DLG!=='undefined'&&DLG;i++){__tick(400);dlgNext()}")
            news = g.ev("(()=>{const h=linNewsHTML();return h?h.replace(/<[^>]+>/g,' ').replace(/\\s+/g,' ').trim():''})()")
            g.ev(RNG % (SEEDBASE + d)); g.ev("autoStock()")
            if SHOTS: g.ev("window.__noScenes=false;window.__holds=true")   # before opening: the day's first scene may come with it
            if g.ev("phase") != 'service': rt.start_day(g)
            rt.install_bot(g); g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;window.__noScenes=true")
            if SHOTS: g.ev("window.__noScenes=false;window.__holds=true")
            day = g.ev("S.day")
            for _ in range(2000):
                if g.ev("sub==='tasting'"): g.ev("tastingDir('food')")
                if g.ev("sub==='loungeproj'"):
                    if SHOTS and ('lin_decide', 'modal') not in SEEN:
                        SEEN[('lin_decide', 'modal')] = 1; g.page.wait_for_timeout(150); g.page.screenshot(path=os.path.join(SHOTS, f'lin_decide_1_day{day}.png')); print(f'   shot lin_decide_1_day{day}.png', flush=True)
                    g.ev("loungeGo('plan')")
                if SHOTS: held(g, day)
                g.ev("for(let i=0;i<20&&typeof DLG!=='undefined'&&DLG;i++){__tick(400);dlgNext()}")
                n = g.ev("__botUntil(\"sub==='loungeproj'||sub==='tasting'||!!(typeof DLG!=='undefined'&&DLG)||(R.closing!=null&&!storyDay().eve)\",150,1/30)")
                if g.ev("!!R&&R.closing!=null&&!storyDay().eve"): g.ev("lifeEnsureEvening()")   # the main loop's evening, which the bot does not run
                if g.ev("phase") != 'service' or not g.ev("!!R"): break
                if n < 150 and not g.ev("paused||sub==='loungeproj'||sub==='tasting'||!!(typeof DLG!=='undefined'&&DLG)"): break
            if g.ev("phase") == 'service': g.ev("__bot(60000,1/30)")
            if g.ev("sub==='loungeproj'"): g.ev("loungeGo('plan')")
            if g.ev("!!(typeof DLG!=='undefined'&&DLG)"):
                if SHOTS: held(g, day)
                g.ev("for(let i=0;i<80&&typeof DLG!=='undefined'&&DLG;i++){__tick(400);dlgNext()}")
            g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
            x = json.loads(g.ev("""JSON.stringify({facts:%s.filter(k=>fact(k)&&(fact(k).l===S.day||fact(k).d===S.day)),evs:%s.filter(k=>evState(k).d===S.day||(evState(k).last===S.day&&evState(k).n)),
              majors:__tr.filter(t=>t.d===S.day&&t.lane==='major').map(t=>t.k),vis:__vis.filter(v=>v.d===S.day).map(v=>v.n.replace('品酒師 ','')+'@'+v.t+'%%'),bar:__bar.filter(v=>v.d===S.day).map(v=>v.n),
              din:S.lastSummary&&S.lastSummary.dinWine?S.lastSummary.dinWine.reduce((a,x)=>a+x.n,0):0,st:barState(),last:linLast()})""" % (json.dumps(KEYS), json.dumps(EVS))))
            print(f"Day {day:3d}  bar {x['st']:6s} {('last '+str(x['last'])) if x['last'] else '':8s} visits {','.join(x['vis']) or '-':22s} next door {len(x['bar'])} {('(Ken)' if 'Ken' in ' '.join(x['bar']) or '品酒師 Ken' in x['bar'] else ''):5s} glasses {x['din']:3d}  facts {' '.join(x['facts']) or '·'}  events {' '.join(x['evs']) or '·'}{'  news: '+news if news else ''}", flush=True)
            if UNTIL == 'decide' and g.ev("!!fact('lounge_project')&&!!fact('lin_closed')"): break
            if UNTIL == 'open' and g.ev("loungeLv()>0"): break
            if UNTIL == 'guest' and g.ev("!!fact('lin_guest')"): break
        F = json.loads(g.ev("JSON.stringify(Object.fromEntries(%s.map(k=>[k,fact(k)?fact(k).d:null])))" % json.dumps(KEYS)))
        E = json.loads(g.ev("JSON.stringify(Object.fromEntries(%s.map(k=>[k,evState(k).d||null])))" % json.dumps(EVS)))
        print('\nthe day of each fact:', F); print('the day of each event:', E)
        print('words kept:', g.ev("JSON.stringify(Object.fromEntries(['lin_retire','ken_where','jd_want','dylan_book','lin_viewing','pairing_start','lin_sign','lin_guest'].map(k=>[k,((story().beatLines||{})[k]||[]).length])))"))
        print('Evan:', g.ev("JSON.stringify((S.crew||[]).filter(m=>m.name==='Evan').map(m=>({role:m.role,pool:m.pool,since:m.since})))"), ' Dylan stage:', g.ev("S.dylan.stage"), ' money:', g.ev("S.money"), ' level:', g.ev("S.level"))
        print('page errors:', g.errors[:5])
        g.close(); b.close(); srv.shutdown()
    print(f'{d + 1} days in {time.time()-t0:.0f}s')


if __name__ == '__main__':
    main()
