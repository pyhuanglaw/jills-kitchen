"""v2.4 pacing simulation (docs/v24/pacing_correction_2026-10-01.txt): the player's Day 52 save played forward day after
day by the lazy bot (the staff do their jobs; Jill cooks what no chef can), the story arbiter running as in play. Prints
the day each 怡君 / 秀琴阿姨 × Sophie-Mia / 《那面牆》 beat happened, against the player's targets:

  怡君 moved in (the spare key)   ~Day 59–62
  《那面牆》 begins               ~Day 62–66
  《那面牆》 settled               ~Day 75–82
  Second Floor era opens          ~Day 78–86   (two days after the settlement)

  python3 tools/sims/v24_pacing.py [days=36] [seedbase=7000] [save=tests/saves/player_day52.json]
"""
import sys, os, json, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, os.path.join(ROOT, 'tests'))
import run_tests as rt
from playwright.sync_api import sync_playwright

DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 36
SEEDBASE = int(sys.argv[2]) if len(sys.argv) > 2 else 7000
SAVE = sys.argv[3] if len(sys.argv) > 3 else os.path.join(ROOT, 'tests/saves/player_day52.json')
raw = json.load(open(SAVE)); raw = raw.get('save', raw)
SEED = "Math.random=(function(){let a=%d;return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
KEYS = ['yj_meet', 'yj_look', 'yj_three', 'yj_chose', 'yj_move', 'yj_key', 'yj_key_seen', 'xq_oh',
        'wall_worry', 'wall_call', 'wall_photos', 'wall_jill', 'wall_visit', 'wall_wang', 'wall_setback', 'wall_report', 'wall_fee', 'wall_prep',
        'wall_mediation', 'wall_settle', 'wall_paid', 'wall_article', 'wall_paper', 'wall_fixed']

def main():
    t0 = time.time()
    with sync_playwright() as p:
        srv, port = rt.start_server(); b = p.chromium.launch()
        g = rt.Game(b, port, 'index', seed=SEEDBASE, manual=True, viewport={'width': 390, 'height': 844})
        g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.page.wait_for_timeout(150)
        g.click('[data-act=openFresh]') if g.page.query_selector('[data-act=openFresh]') else g.click('[data-act=open]'); g.page.wait_for_timeout(150)
        g.ev("window.__fastSay=1")
        rows = []
        for d in range(DAYS):
            if g.ev("phase") == 'shop':
                g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(120)
            if g.ev("phase") == 'summary':
                g.click('[data-act=toShop]'); g.page.wait_for_timeout(80); g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(120)
            g.ev(SEED % (SEEDBASE + d)); g.ev("S.today.sugKey=null;S.today.sug=null;autoStock()")
            rt.start_day(g); rt.install_bot(g); g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;window.__noScenes=true")
            day = g.ev("S.day"); g.ev("window.__seen=new Set();window.__sm=[]")
            for _ in range(1200):
                r = g.page.evaluate('()=>window.__bot(150,1/30)')
                g.ev("if(R)for(const q of R.groups){for(const id of storyIdsOf(q))__seen.add(id);for(const id of storyIdsOf(q))if(['sophie','mia','wang'].includes(id)&&q.table!=null){const k=id+'@'+(R.tables[q.table].room||'main')+':'+Math.round(R.t/10)*10;if(!__sm.some(x=>x.startsWith(id+'@')))__sm.push(k)}}")
                if g.ev("phase") != 'service' or not g.ev("!!R"): break
                if r['ticks'] < 150: break
            if g.ev("phase") == 'service':
                g.ev("closeShop('x');for(const q of R.groups.slice())leaveGroup(q,'ok')"); g.page.evaluate('()=>window.__bot(400,1/30)')
            if g.ev("phase") == 'service': g.ev("finishClosing()")
            info = json.loads(g.ev("""JSON.stringify({day:S.day,wx:(story().v24&&story().v24.wx||{})[S.day]||null,
              came:Object.keys(story().named||{}).filter(k=>(story().named[k].seen===S.day)),
              sm:window.__sm||[],majors:(story().day&&story().day.d===S.day)?story().day.major:null,
              seen:[...(window.__seen||[])].filter(x=>['sophie','mia','wang','n:怡君'].includes(x)),
              miss:Object.fromEntries(KEYS_JS.filter(k=>story().ev[k]&&story().ev[k].miss).map(k=>[k,story().ev[k].miss])),
              regs:(S.lastSummary&&S.lastSummary.regs)||null,
              fam:[xqKnows('sophie'),xqKnows('mia')],
              eras:{yj:eraOpenDay('yj'),wall:eraOpenDay('wall'),up:eraOpenDay('up')},
              facts:Object.fromEntries(%s.filter(k=>fact(k)&&fact(k).d===S.day).map(k=>[k,1])),
              money:S.money,errors:(window.__errs||[]).length})""".replace("KEYS_JS", json.dumps(KEYS)) % json.dumps(KEYS)))
            rows.append(info)
            print(f"Day {info['day']:3d}  {info['wx'] or '-':6s} fam {info['fam']}  seen {info['seen']} sat {info['sm']} major {info['majors']} miss {info['miss']}  {' '.join(info['facts'].keys())}", flush=True)
        final = json.loads(g.ev("JSON.stringify(Object.fromEntries(%s.map(k=>[k,fact(k)?fact(k).d:null])))" % json.dumps(KEYS)))
        eras = json.loads(g.ev("JSON.stringify({yj:eraOpenDay('yj'),wall:eraOpenDay('wall'),up:eraOpenDay('up'),dorm:story().v24.dorm})"))
        majors = json.loads(g.ev("JSON.stringify(story().trace.filter(t=>t.lane==='major').map(t=>[t.d,t.k]))"))
        print('\nfirst day each beat happened:')
        for k in KEYS:
            print(f'  {k:16s} {final[k]}')
        print('eras open:', eras)
        per = {}
        for dd, k in majors: per.setdefault(dd, []).append(k)
        print('major beats per day (last 40 in the trace):', {k: v for k, v in per.items()})
        print('more than one major in a day:', [dd for dd, v in per.items() if len(v) > 1])
        print('page errors:', g.errors[:5])
        g.close(); b.close()
    print(f'{DAYS} days in {time.time()-t0:.0f}s')

if __name__ == '__main__':
    main()
