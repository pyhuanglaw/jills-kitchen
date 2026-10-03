"""v2.3 Phase 7: N lazy days on the Day 46 save with Lounge I and the Lounge cast hired (as a player who built it would
have) — what the social layer produced on its own: which beats fired on which day, the density per day, the pair facts
of the authored pairs, Story Photos. Usage: python3 tools/sims/social_days.py [days] [seed] [lounge lv]"""
import sys, os, json, time, collections
ROOT='/home/claude/jills-kitchen-project'; sys.path.insert(0, os.path.join(ROOT,'tests'))
import run_tests as rt
from playwright.sync_api import sync_playwright
days=int(sys.argv[1]) if len(sys.argv)>1 else 30; seed=int(sys.argv[2]) if len(sys.argv)>2 else 11; lv=int(sys.argv[3]) if len(sys.argv)>3 else 1
raw=json.load(open(ROOT+'/tests/saves/player_day46.json'))['save']
with sync_playwright() as p:
    srv,port=rt.start_server(); b=p.chromium.launch()
    g=rt.Game(b,port,'index',seed=seed,manual=True,viewport={'width':390,'height':844})
    g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.click('[data-act=openFresh]'); g.page.wait_for_timeout(120)
    g.ev("S.money+=900000;factSet('lounge_project');for(let l=1;l<=%d;l++){buyLounge(l);hideReveal()}S.crew.push({id:'cb1',role:'bartender',name:'Evan',lv:2,duty:'lbar'},{id:'cb2',role:'bartender',name:'沈晴',lv:2,duty:'lbar'},{id:'ct1',role:'chef',name:'阿拓',lv:2,duty:'stove'},{id:'cw9',role:'waiter',name:'安安',lv:2,duty:'both',duties:{seat:true,order:true,serve:true,check:true,clean:false,lounge:true}});for(const m of S.crew.filter(m=>m.role==='waiter').slice(0,1))waiterDuties(m).lounge=true;showPrep()" % lv)
    t0=time.time(); dens=collections.Counter(); perday=[]
    for d in range(days):
        g.ev("if(phase!=='prep'){S.phase='prep';showPrep()}S.money+=30000;autoStock()"); rt.start_day(g); rt.install_bot(g); g.ev(rt.LAZY_ACTOR+"\nwindow.__act=window.__actLazy;")
        rt.play_day(g, max_steps=60000)
        for i in range(400):
            if g.ev("phase")!='service': break
            g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
        st=json.loads(g.ev("JSON.stringify({day:S.day,guests:S.lastSummary&&S.lastSummary.guests,lg:S.lastSummary&&S.lastSummary.lg,trace:story().trace.filter(t=>t.d===S.day).map(t=>t.k+'/'+t.lane[0]),who:R?null:null,vis:{sophie:S.regulars.sophie,mia:S.regulars.mia,ken:(story().named['品酒師 Ken']||{}).v,du:(story().named['Monsieur 杜']||{}).v},photos:Object.keys(story().photos)})"))
        maj=sum(1 for t in st['trace'] if t.endswith('/m') and not t.startswith('recognize')); mi=sum(1 for t in st['trace'] if t.endswith('/i'))
        dens[(sum(1 for t in st['trace'] if '/m' in t and t.split('/')[0] in [e for e in ['sm_c','sm_d','sm_h','kd_photo','qt_3','qt_photo','lin_gift','sophie_mei_4','ken_tasting','lounge_reveal']]))]+=1
        print(f"day {st['day']}: guests {st['guests']} lg {st['lg']} visits {st['vis']} | {st['trace']} | photos {st['photos']}")
        perday.append(st['trace'])
        g.ev("S.phase='prep';S.day++;planToday();showPrep()")
    print('elapsed', round(time.time()-t0), 's')
    for pr in [['sophie','mia'],['n:品酒師 Ken','n:Monsieur 杜'],['s:cb2','s:ct1']]:
        print('pair', pr, g.ev("JSON.stringify(Object.fromEntries(Object.entries(rel(%s,%s)).map(([k,v])=>[k,v.n])))" % (json.dumps(pr[0]),json.dumps(pr[1]))), 'fam', g.ev("famOf(%s,%s)" % (json.dumps(pr[0]),json.dumps(pr[1]))), 'romantic', g.ev("romanticEligible(%s,%s)" % (json.dumps(pr[0]),json.dumps(pr[1]))))
    print('facts', g.ev("JSON.stringify(Object.fromEntries(Object.entries(story().facts).filter(([k])=>!/^first_|^lounge_(direct|wait|after)_|^tasted_|^held_/.test(k)).map(([k,v])=>[k,v.n])))"))
    print('events', g.ev("JSON.stringify(Object.fromEntries(Object.entries(story().ev).filter(([k,v])=>v.n).map(([k,v])=>[k,v.n])))"))
    print('posts', g.ev("JSON.stringify(social().posts.map(p=>p.day+' '+p.who+'['+p.topic+'] '+p.txt))"))
    print('pending photos', g.ev("JSON.stringify(storyPhotoPending())"), 'photos', g.ev("JSON.stringify(story().photos)"))
    print('named visits', g.ev("JSON.stringify(Object.fromEntries(Object.entries(story().named).map(([k,v])=>[k,v.v])))"))
    print('misses', g.ev("JSON.stringify(Object.fromEntries(Object.entries(story().ev).filter(([k,v])=>v.miss>=2).map(([k,v])=>[k,v.miss])))"))
    print('major beats per day histogram (authored majors only)', dict(dens))
    print('errors', g.errors[:3]); g.close(); b.close()
