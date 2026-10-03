"""rc7: Ken after the Lounge (the player's KEN / LOUNGE STORY CONTINUITY PASS, 2026-10-02 15:24). A save played forward day by
day by the lazy bot, the story arbiter as in play; prints each day what Ken's chapter did — his beats (ken_lounge,
ken_propose, the three nights, ken_collab, ken_samples, ken_wine, du_wine), the tasting nights (how many seats, how many
of the guests came and sat at the bar, Ken behind it, the wines, what the bar sold), the next night planned, and the day's
other major beats; with SHOTS=dir, a phone screenshot of the Lounge on each tasting night once it has begun.

  python3 tools/sims/ken_chain.py SAVE DAYS [SEEDBASE=7600]
  SHOTS=docs/evidence/v24_rc7/ken python3 tools/sims/ken_chain.py tests/saves/player_day74_1508.json 40
"""
import sys, os, json, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, os.path.join(ROOT, 'tests'))
import run_tests as rt
from playwright.sync_api import sync_playwright

SAVE, DAYS = sys.argv[1], int(sys.argv[2])
SEEDBASE = int(sys.argv[3]) if len(sys.argv) > 3 else 7600
SHOTS = os.environ.get('SHOTS')
RNG = "Math.random=(function(){let a=%d;return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
KEYS = ['ken_lounge', 'ken_propose', 'ken_t1', 'ken_t2', 'ken_t3', 'ken_collab', 'ken_samples', 'ken_wine', 'du_wine']


def main():
    t0 = time.time()
    raw = json.load(open(SAVE)); save = raw.get('save', raw); save['checkpoint'] = None
    KEY = __import__('re').search(r"const KEY='([^']+)'", open(os.path.join(ROOT, 'js', 'game.js'), encoding='utf-8').read()).group(1)
    if SHOTS: os.makedirs(SHOTS, exist_ok=True)
    with sync_playwright() as p:
        srv, port = rt.start_server(); b = p.chromium.launch()
        g = rt.Game(b, port, 'index', seed=SEEDBASE, manual=True, viewport={'width': 390, 'height': 844}, storage={KEY: json.dumps(save, ensure_ascii=False)})
        g.click('[data-act=open]'); g.page.wait_for_timeout(150)
        g.ev("window.__fastSay=1;window.__tr=[];const __st0=storyTrace;storyTrace=function(o){__tr.push(Object.assign({d:S.day},o));return __st0(o)}")
        print(f"{os.path.basename(SAVE)} from Day {g.ev('S.day')}, seeds {SEEDBASE}+; Lounge LV{g.ev('loungeLv()')}, finished Day {g.ev('loungeDoneDay()')}; Ken×杜 argued {g.ev('relN(KEN_ID,DU_ID,`argued`)')}", flush=True)
        for d in range(DAYS):
            for _ in range(3):
                if g.ev("phase") == 'summary': g.click('[data-act=toShop]'); g.page.wait_for_timeout(80)
                if g.ev("phase") == 'shop': g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(120)
            g.ev("for(let i=0;i<80&&typeof DLG!=='undefined'&&DLG;i++){__tick(400);dlgNext()}")
            news = g.ev("(()=>{const h=kenNewsHTML();return h?h.replace(/<[^>]+>/g,' ').replace(/\\s+/g,' ').trim():''})()")
            g.ev(RNG % (SEEDBASE + d)); g.ev("autoStock()")
            if g.ev("phase") != 'service': rt.start_day(g)
            rt.install_bot(g); g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;window.__noScenes=true")
            day = g.ev("S.day"); shot = False; peak = None
            for _ in range(1200):
                r = g.page.evaluate('()=>window.__bot(150,1/30)')
                g.ev("for(let i=0;i<80&&typeof DLG!=='undefined'&&DLG;i++){__tick(400);dlgNext()}")
                k = json.loads(g.ev("JSON.stringify(R&&R.kt?{n:R.kt.n,seats:R.kt.seats,on:R.kt.on,end:R.kt.end,host:R.kt.host?R.kt.host.state:null,hx:R.kt.host?[Math.round(R.kt.host.x),Math.round(R.kt.host.y),R.kt.host.room]:null,came:R.kt.guests.length,bar:R.kt.guests.filter(q=>q.table!=null&&R.tables[q.table]&&R.tables[q.table].kind==='bar'&&R.tables[q.table].room==='lounge').length,wines:R.kt.wines,t:Math.round(R.t/R.dur*100)}:null)"))
                if k and (peak is None or k['bar'] >= peak.get('bar', 0)): peak = k
                if SHOTS and k and k['on'] and not k['end'] and not shot:
                    g.ev("setRoom('lounge');for(let i=0;i<3;i++)__tick(1000/30)"); g.page.wait_for_timeout(150)
                    g.page.screenshot(path=os.path.join(SHOTS, f'tasting_day{day}_n{k["n"]}.png')); shot = True
                if g.ev("phase") != 'service' or not g.ev("!!R") or r['ticks'] < 150: break
            if g.ev("phase") == 'service': g.ev("__bot(60000,1/30)")
            g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
            x = json.loads(g.ev("""JSON.stringify({ken:%s.filter(k=>fact(k)&&fact(k).d===S.day),next:kenS().next,first:kenS().first,legacy:kenLegacy(),
              majors:__tr.filter(t=>t.d===S.day&&t.lane==='major').map(t=>t.k),seen:(story().named['品酒師 Ken']||{}).seen===S.day,du:(story().named['Monsieur 杜']||{}).seen===S.day,
              jk:(S.lastSummary&&S.lastSummary.lgSales||[]).filter(o=>o.d==='w_jk').map(o=>o.n)[0]||0,lg:S.lastSummary&&S.lastSummary.lg?S.lastSummary.lg.rev:0})""" % json.dumps(KEYS)))
            kt = '' if not peak else f" | tasting #{peak['n']} {peak['seats']} seats: came {peak['came']}, at the bar {peak['bar']}, Ken {peak['host']} at {peak['hx']}, wines {peak['wines']}"
            print(f"Day {day:3d}  Ken in:{'Y' if x['seen'] else '-'} 杜:{'Y' if x['du'] else '-'}  {' '.join(x['ken']) or '·'}{kt}  next {x.get('next')}  majors {x['majors']}  Lounge ${x['lg']}{' · 晚餐之後 x'+str(x['jk']) if x['jk'] else ''}{'  news: '+news if news else ''}", flush=True)
        F = json.loads(g.ev("JSON.stringify(Object.fromEntries(%s.map(k=>[k,fact(k)?fact(k).d:null])))" % json.dumps(KEYS)))
        print('\nthe day each happened:', F)
        print('tasting nights hosted:', g.ev("factN('ken_tn')"), '| on the list:', g.ev("wineList().includes('w_jk')"))
        print('page errors:', g.errors[:5])
        g.close(); b.close(); srv.shutdown()
    print(f'{DAYS} days in {time.time()-t0:.0f}s')


if __name__ == '__main__':
    main()
