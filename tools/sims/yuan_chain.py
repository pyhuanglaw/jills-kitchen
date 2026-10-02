"""rc7: 林予安, the Lounge's pianist (the player, 2026-10-02 16:42–16:46). A save played forward day by day by the lazy
bot; prints each day what her story did (ya_1 … ya_join), whether she played that night (her nights only), her fee,
the Wangs, the news, and the day's other major beats.

  python3 tools/sims/yuan_chain.py SAVE DAYS [SEEDBASE=7700]
"""
import sys, os, json, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, os.path.join(ROOT, 'tests'))
import run_tests as rt
from playwright.sync_api import sync_playwright

SAVE, DAYS = sys.argv[1], int(sys.argv[2])
SEEDBASE = int(sys.argv[3]) if len(sys.argv) > 3 else 7700
SHOTS = os.environ.get('SHOTS')
RNG = "Math.random=(function(){let a=%d;return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
KEYS = ['ya_1', 'ya_2', 'ya_3', 'ya_trial', 'ya_join']


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
        print(f"{os.path.basename(SAVE)} from Day {g.ev('S.day')}, seeds {SEEDBASE}+; piano bought Day {g.ev('pianoDay()')}", flush=True)
        for d in range(DAYS):
            for _ in range(3):
                if g.ev("phase") == 'summary': g.click('[data-act=toShop]'); g.page.wait_for_timeout(80)
                if g.ev("phase") == 'shop': g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(120)
            g.ev("for(let i=0;i<80&&typeof DLG!=='undefined'&&DLG;i++){__tick(400);dlgNext()}")
            news = g.ev("(()=>{const h=yaNewsHTML();return h?h.replace(/<[^>]+>/g,' ').replace(/\\s+/g,' ').trim():''})()")
            g.ev(RNG % (SEEDBASE + d)); g.ev("autoStock()")
            if g.ev("phase") != 'service': rt.start_day(g)
            rt.install_bot(g); g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;window.__noScenes=true")
            day = g.ev("S.day"); shot = False; peak = None
            for _ in range(1200):
                r = g.page.evaluate('()=>window.__bot(150,1/30)')
                g.ev("for(let i=0;i<80&&typeof DLG!=='undefined'&&DLG;i++){__tick(400);dlgNext()}")
                k = json.loads(g.ev("JSON.stringify(R&&R.ya&&R.ya.g?{trial:!!R.ya.trial,st:R.ya.g.state,on:R.ya.on,clap:!!R.ya.clap,ask:!!R.ya.ask,done:!!R.ya.done,t:Math.round(R.t/R.dur*100),wang:!!wangsHere()}:null)"))
                if k: peak = k
                if SHOTS and k and k['st'] == 'piano' and not shot:
                    g.ev("setRoom('lounge');for(let i=0;i<3;i++)__tick(1000/30)"); g.page.wait_for_timeout(150)
                    g.page.screenshot(path=os.path.join(SHOTS, f'piano_day{day}.png')); shot = True
                if g.ev("phase") != 'service' or not g.ev("!!R") or r['ticks'] < 150: break
            if g.ev("phase") == 'service': g.ev("__bot(60000,1/30)")
            g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
            x = json.loads(g.ev("""JSON.stringify({ya:%s.filter(k=>fact(k)&&fact(k).d===S.day),seen:(story().named['林予安']||{}).seen===S.day,
              majors:__tr.filter(t=>t.d===S.day&&t.lane==='major').map(t=>t.k),fee:S.lastSummary&&S.lastSummary.piano||0,night:yaNight(S.day),lg:S.lastSummary&&S.lastSummary.lg?S.lastSummary.lg.rev:0})""" % json.dumps(KEYS)))
            kt = '' if not peak else f" | at the piano: {peak}"
            print(f"Day {day:3d}  予安 in:{'Y' if x['seen'] else '-'}  {' '.join(x['ya']) or '·'}{kt}  fee {x['fee']}  majors {x['majors']}  Lounge ${x['lg']}{'  news: '+news if news else ''}", flush=True)
        F = json.loads(g.ev("JSON.stringify(Object.fromEntries(%s.map(k=>[k,fact(k)?fact(k).d:null])))" % json.dumps(KEYS)))
        print('\nthe day each happened:', F)
        print('her nights in the next two weeks:', [d for d in range(g.ev('S.day'), g.ev('S.day')+14) if g.ev(f'yaNight({d})')])
        print('page errors:', g.errors[:5])
        g.close(); b.close(); srv.shutdown()
    print(f'{DAYS} days in {time.time()-t0:.0f}s')


if __name__ == '__main__':
    main()
