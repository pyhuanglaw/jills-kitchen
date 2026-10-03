"""v2.3: play N lazy days on a real save and print what the story layer did — the trace, the facts, the pair facts,
which beats fired. Usage: python3 tools/sims/story_days.py [save.json] [days] [seed]"""
import sys, os, json, time
ROOT='/home/claude/jills-kitchen-project'; sys.path.insert(0, os.path.join(ROOT,'tests'))
import run_tests as rt
from playwright.sync_api import sync_playwright
save=sys.argv[1] if len(sys.argv)>1 else ROOT+'/tests/saves/player_day39.json'; days=int(sys.argv[2]) if len(sys.argv)>2 else 8; seed=int(sys.argv[3]) if len(sys.argv)>3 else 7
raw=json.load(open(save))['save']
with sync_playwright() as p:
    srv,port=rt.start_server(); b=p.chromium.launch()
    g=rt.Game(b,port,'index',seed=seed,manual=True,viewport={'width':390,'height':844})
    g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.click('[data-act=openFresh]'); g.page.wait_for_timeout(120)
    t0=time.time()
    for d in range(days):
        g.ev("if(phase!=='prep'){S.phase='prep';showPrep()}S.money+=30000;autoStock()"); rt.start_day(g); rt.install_bot(g); g.ev(rt.LAZY_ACTOR+"\nwindow.__act=window.__actLazy;")
        rt.play_day(g, max_steps=60000)
        for i in range(400):
            if g.ev("phase")!='service': break
            g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
        day=g.ev("S.day"); st=json.loads(g.ev("JSON.stringify({guests:S.lastSummary.guests,sophie:S.regulars.sophie,ev:Object.keys(story().ev).filter(k=>story().ev[k].n).map(k=>k+':'+story().ev[k].n),trace:story().trace.filter(t=>t.d===S.day).map(t=>t.k)})"))
        print(f"day {day}: guests {st['guests']} sophie visits {st['sophie']} fired today {st['trace']} | done {st['ev']}")
        g.ev("(()=>{const q=document.querySelector('[data-act=next]')||document.querySelector('[data-act=toShop]');})();S.phase='prep';S.day++;planToday();showPrep()")
    print('elapsed', round(time.time()-t0), 's')
    print('facts', g.ev("JSON.stringify(story().facts)"))
    rel=json.loads(g.ev("JSON.stringify(story().rel)")); print('pairs', len(rel))
    for k,v in list(rel.items())[:12]: print('  ',k,{fk:f['n'] for fk,f in v['f'].items()}, 'fam', g.ev("famOf(%s,%s)" % (json.dumps(k.split('|')[0]),json.dumps(k.split('|')[1]))))
    print('named', g.ev("JSON.stringify(story().named)"))
    print('misses', g.ev("JSON.stringify(Object.fromEntries(Object.entries(story().ev).map(([k,v])=>[k,v.miss])))"))
    print('errors', g.errors[:3]); g.close(); b.close()
