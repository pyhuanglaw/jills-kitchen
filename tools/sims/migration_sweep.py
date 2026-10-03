"""v2.3 Phase 10: every real save fixture — load, reload three times, play one lazy day, reload again. Prints the day,
the money, whether the story state started empty, the new keys, and any page error. Usage: python3 tools/sims/migration_sweep.py"""
import sys, os, json, glob
ROOT='/home/claude/jills-kitchen-project'; sys.path.insert(0, os.path.join(ROOT,'tests'))
import run_tests as rt
from playwright.sync_api import sync_playwright
saves=sorted(glob.glob(ROOT+'/tests/saves/*.json'))
with sync_playwright() as p:
    srv,port=rt.start_server(); b=p.chromium.launch()
    for f in saves:
        raw=json.load(open(f))['save']
        g=rt.Game(b,port,'index',seed=5,manual=True,viewport={'width':390,'height':844})
        g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.page.wait_for_timeout(120)
        d0=raw.get('day'); m0=raw.get('money')
        st=[]
        def open_(): 
            g.page.wait_for_timeout(150)
            if g.page.query_selector('[data-act=openFresh]'): g.click('[data-act=openFresh]')
            else: g.click('[data-act=open]')
            g.page.wait_for_timeout(80)
        for i in range(3):
            if i: g.reload()
            open_()
            st.append(g.ev("JSON.stringify({day:S.day,money:S.money,lv:S.level,story:!!S.story,ev:S.story?Object.keys(S.story.ev||{}).length:0,social:!!S.social,lounge:S.rooms&&S.rooms.lounge||0,crew:(S.crew||[]).length})"))
        ok=len(set(st))==1
        g.ev("if(phase!=='prep'){S.phase='prep';showPrep()}S.money+=30000;autoStock()"); rt.start_day(g); rt.install_bot(g); g.ev(rt.LAZY_ACTOR+"\nwindow.__act=window.__actLazy;")
        rt.play_day(g, max_steps=60000)
        for i in range(400):
            if g.ev("phase")!='service': break
            g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
        after=g.ev("JSON.stringify({phase,day:S.day,guests:S.lastSummary&&S.lastSummary.guests,rev:S.lastSummary&&S.lastSummary.rev,trace:story().trace.filter(t=>t.d===S.day).map(t=>t.k)})")
        g.ev("save()"); g.reload(); open_()
        again=g.ev("JSON.stringify({day:S.day,ev:Object.keys(story().ev).length,facts:Object.keys(story().facts).length})")
        print(os.path.basename(f), 'fixture day',d0,'| loads stable',ok, st[0], '| played', after, '| reloaded', again, '| errors', g.errors[:2])
        g.close()
    b.close()
