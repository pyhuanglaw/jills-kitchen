"""rc7 (the player, 2026-10-02 15:39: 「一天可以不只一個劇情不然太慢」). A save played forward day by day by the lazy bot
(the crew do their jobs; Jill does what nobody else can), the story arbiter running as in play. Prints every story beat
each day by lane — major, the long stories' steps (v24), the older stories' minor moments; ambient lines counted — and
marks the ones that hold the restaurant (★). CAPS=old plays the same days with rc6's caps (major 1, minor 2, v24 1,
no gap between two beats of a lane), for a before/after on the same seeds.

  python3 tools/sims/story_per_day.py SAVE DAYS [SEEDBASE=7400]
  CAPS=old python3 tools/sims/story_per_day.py SAVE DAYS [SEEDBASE]
"""
import sys, os, json, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, os.path.join(ROOT, 'tests'))
import run_tests as rt
from playwright.sync_api import sync_playwright

SAVE, DAYS = sys.argv[1], int(sys.argv[2])
SEEDBASE = int(sys.argv[3]) if len(sys.argv) > 3 else 7400
OLD = os.environ.get('CAPS') == 'old'
RNG = "Math.random=(function(){let a=%d;return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"


def main():
    t0 = time.time()
    raw = json.load(open(SAVE)); save = raw.get('save', raw); save['checkpoint'] = None
    KEY = __import__('re').search(r"const KEY='([^']+)'", open(os.path.join(ROOT, 'js', 'game.js'), encoding='utf-8').read()).group(1)
    with sync_playwright() as p:
        srv, port = rt.start_server(); b = p.chromium.launch()
        g = rt.Game(b, port, 'index', seed=SEEDBASE, manual=True, viewport={'width': 390, 'height': 844}, storage={KEY: json.dumps(save, ensure_ascii=False)})
        g.click('[data-act=open]'); g.page.wait_for_timeout(150)
        g.ev("window.__fastSay=1;window.__tr=[];const __st0=storyTrace;storyTrace=function(o){__tr.push(Object.assign({d:S.day,t:R&&R.dur?Math.round(R.t/R.dur*100)/100:null},o));return __st0(o)}")
        if OLD:
            g.ev("LANE_CAP.major=1;LANE_CAP.minor=2;LANE_CAP.v24=1;LANE_GAP.major=0;LANE_GAP.minor=0;LANE_GAP.v24=0")
        print(f"{'(rc6 caps)' if OLD else '(rc7 caps)'} {os.path.basename(SAVE)} from Day {g.ev('S.day')}, seeds {SEEDBASE}+", flush=True)
        tot = {'major': 0, 'v24': 0, 'minor': 0, 'ambient': 0, 'held': 0}
        for d in range(DAYS):
            for _ in range(3):
                if g.ev("phase") == 'summary': g.click('[data-act=toShop]'); g.page.wait_for_timeout(80)
                if g.ev("phase") == 'shop': g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(120)
            g.ev("for(let i=0;i<80&&typeof DLG!=='undefined'&&DLG;i++){__tick(400);dlgNext()}")
            g.ev(RNG % (SEEDBASE + d)); g.ev("autoStock()")
            if g.ev("phase") != 'service':
                rt.start_day(g)
            rt.install_bot(g); g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;window.__noScenes=true")
            day = g.ev("S.day")
            for _ in range(1200):
                r = g.page.evaluate('()=>window.__bot(150,1/30)')
                g.ev("for(let i=0;i<80&&typeof DLG!=='undefined'&&DLG;i++){__tick(400);dlgNext()}")
                if g.ev("phase") != 'service' or not g.ev("!!R") or r['ticks'] < 150: break
            if g.ev("phase") == 'service':
                g.ev("__bot(60000,1/30)")
            g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
            rows = json.loads(g.ev("JSON.stringify(__tr.filter(x=>x.d===%d).map(x=>({k:x.k,lane:x.lane,at:x.at,t:x.t,held:typeof SH_HOLD!=='undefined'&&SH_HOLD.test(x.k)})))" % day))
            by = {'major': [], 'v24': [], 'minor': []}; amb = 0
            for x in rows:
                if x['lane'] == 'ambient': amb += 1; continue
                if x['lane'] in by: by[x['lane']].append(f"{'★' if x['held'] else ''}{x['k']}@{x['at']}{'' if x['t'] is None else ' ' + str(x['t'])}")
                if x['held']: tot['held'] += 1
            for k in by: tot[k] += len(by[k])
            tot['ambient'] += amb
            print(f"Day {day:3d}  major {len(by['major'])} {by['major']}  v24 {len(by['v24'])} {by['v24']}  minor {len(by['minor'])} {by['minor']}  ambient {amb}", flush=True)
        print(f"\n{DAYS} days: major {tot['major']}, v24 {tot['v24']}, minor {tot['minor']}, ambient {tot['ambient']}; held the restaurant {tot['held']}")
        print('page errors:', g.errors[:5])
        g.close(); b.close(); srv.shutdown()
    print(f'{DAYS} days in {time.time()-t0:.0f}s')


if __name__ == '__main__':
    main()
