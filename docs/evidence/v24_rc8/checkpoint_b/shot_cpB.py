"""Checkpoint B (the player's brief of 2026-10-02 19:19 §26): the pieces of the Madame Lin line that are not one scene —
Ken's question, the pairing glasses at the pass and on the tables, guests walking next door after dinner, Madame Lin
coming over from her own door, the news of her last nights, the story page 「隔壁」, her bar after her last night.
Headless Chromium at 390x844 on the player's saves (T, not O).   python3 shot_cpB.py ROOT OUT"""
import sys, os, json, base64
ROOT = sys.argv[1]; OUT = sys.argv[2].rstrip('/') + '/'
sys.path.insert(0, ROOT + '/tests'); os.chdir(ROOT)
import run_tests as rt, v24_tests as v
from playwright.sync_api import sync_playwright
os.makedirs(OUT, exist_ok=True)
srv, port = rt.start_server()
log = []
VP = {'width': 390, 'height': 844}
def clean(g):
    g.ev("try{hud(true)}catch(e){};document.querySelectorAll('#plines>*,#toasts>*,#banner>*').forEach(e=>e.remove())")
def shot(g, name):
    clean(g); g.page.wait_for_timeout(120); g.page.screenshot(path=OUT + name); print('  shot', name, flush=True)
def crop(g, name, x, y, w, h, k=3):
    clean(g)
    url = g.ev(f"(()=>{{const s=SV.s*DPR;const cv=document.createElement('canvas');cv.width={w}*{k};cv.height={h}*{k};const c=cv.getContext('2d');c.drawImage(sc,(SV.ox+({x})*SV.s)*DPR,(SV.oy+({y})*SV.s)*DPR,{w}*s,{h}*s,0,0,{w}*{k},{h}*{k});return cv.toDataURL('image/png')}})()")
    open(OUT + name, 'wb').write(base64.b64decode(url.split(',')[1])); print('  saved', name, flush=True)
def go(g, rm, n=4):
    g.ev(f"setRoom('{rm}')"); g.ev(f"for(let i=0;i<{n};i++)__tick(1000/30)")
def held(g, want, prefix):
    got = []
    for _ in range(40):
        if not g.ev("!!(typeof DLG!=='undefined'&&DLG)"): break
        t = g.ev("(document.querySelector('#dlg .dlg-text')||{}).textContent||''"); n = g.ev("(document.querySelector('#dlg .dlg-name')||{}).textContent||''")
        got.append((n + '：' if n else '') + t)
        if want and want[0] in t: g.ev("__tick(400)"); shot(g, f'{prefix}{len(want)}.png' if False else f'{prefix}_{t[:6]}.png'); want = want[1:]
        g.ev("__tick(400);dlgNext()"); g.ev("for(let j=0;j<2;j++)__tick(1000/30)")
    return got
with sync_playwright() as p:
    b = p.chromium.launch()
    # 1. Ken's question, on the Day 49 save (no question yet): his third paid visit with a main
    g = rt.Game(b, port, 'index', seed=8501, manual=True, viewport=VP)
    v.load_save(g, 'player_day49.json')
    g.ev("story().named['品酒師 Ken']=Object.assign(story().named['品酒師 Ken']||{},{v:3,last:S.day-2,dishes:{steak:2,salmon:1}})")
    v.to_service(g); g.ev("window.__noScenes=false;window.__holds=true")
    g.ev("R.sched=R.sched.filter(o=>o.name!=='品酒師 Ken');R.sched.splice(R.si,0,{t:R.t+3,type:'gourmet',size:1,name:'品酒師 Ken',story:1})")
    g.ev("__botUntil(\"!!(typeof DLG!=='undefined'&&DLG&&DLG.sh&&DLG.sh.k==='ken_wine_q')\",200000,1/30)")
    log.append('1. Ken: ' + ' / '.join(held(g, ['妳真的不賣酒', '隔壁就有', '那是隔壁'], 'b10_ken_asks')))
    g.close()
    # 2. the pairing glasses before the Lounge, and the guests who walk next door after dinner; Madame Lin from her own door
    g = rt.Game(b, port, 'index', seed=8502, manual=True, viewport=VP)
    v.load_save(g, 'player_day52.json')
    g.ev("const st=story();for(const k of ['tasting_night','pairing_wine'])st.facts[k]={d:S.day-2,n:1,l:S.day-2}")
    v.to_service(g)
    g.ev("window.__act=window.__actLazy")
    g.ev("R.sched.splice(R.si,0,{t:R.t+2,type:'vip',size:1,name:'Madame Lin',story:1})")
    got = {}
    for _ in range(4000):
        g.page.evaluate('()=>window.__bot(3,1/30)')
        if 'lin' not in got and g.ev("R.groups.some(q=>namedId(q)==='Madame Lin'&&q.room==='front'&&q.x>250)"):
            go(g, 'front', 2); shot(g, 'b11_street_madame_lin_comes_over_from_her_bar.png'); got['lin'] = 1
        if 'pass' not in got and g.ev("R.tickets.some(tk=>tk.items.some(i=>i.dinw&&i.st==='ready'&&!i.picked))"):
            go(g, 'main', 2); shot(g, 'b12_main_hall_a_pairing_glass_at_the_pass.png'); crop(g, 'b12b_the_glass_at_the_pass.png', 130, 300, 140, 100, 3); got['pass'] = 1
        if 'table' not in got and g.ev("R.groups.some(q=>q.ticket&&q.ticket.items.some(i=>i.dinw&&i.st==='served')&&q.state==='eat'&&q.room==='main')"):
            go(g, 'main', 2); shot(g, 'b13_main_hall_wine_with_dinner.png'); got['table'] = 1
        if 'walk' not in got and g.ev("R.groups.some(q=>q.toBar&&q.room==='front'&&q.x>260&&namedId(q)!=='Madame Lin')"):
            go(g, 'front', 2); shot(g, 'b14_street_after_dinner_next_door.png'); got['walk'] = 1
        if len(got) == 4 or g.ev("phase") != 'service': break
    log.append('2. got: %s; wine served so far: %s' % (sorted(got), g.ev("R.st.wineCost||0")))
    g.ev("__botUntil('phase!==\"service\"',200000,1/30)"); g.page.wait_for_timeout(150)
    g.ev("(()=>{const e=[...document.querySelectorAll('#screen h3')].find(e=>/晚餐桌上|今天賣了/.test(e.textContent))||[...document.querySelectorAll('#screen .ledger div')].find(e=>/酒水成本/.test(e.textContent));if(e)e.scrollIntoView({block:'center'})})()")
    shot(g, 'b15_summary_wine_cost_and_dinner_glasses.png')
    log.append('2. summary: ' + g.ev("JSON.stringify({wine:S.lastSummary.wine,dinWine:S.lastSummary.dinWine})"))
    g.close()
    # 3. the news before her last nights; the street the day after; the story page
    g = rt.Game(b, port, 'index', seed=8503, manual=True, viewport=VP)
    v.load_save(g, 'player_day52.json')
    g.ev("const st=story();for(const k of ['tasting_night','pairing_wine'])st.facts[k]={d:S.day-14,n:1,l:S.day-14};st.facts.lin_retiring={d:S.day-10,n:1,l:S.day-10};linS().last=S.day+1;evState('lin_retire').n=1;evState('lin_retire').d=S.day-10;showPrep()")
    g.page.wait_for_timeout(150); g.ev("(()=>{const e=[...document.querySelectorAll('#screen .event')].find(e=>/隔壁/.test(e.textContent));if(e)e.scrollIntoView({block:'center'})})()")
    shot(g, 'b16_news_her_last_nights.png')
    log.append('3. news: ' + g.ev("(()=>{const e=[...document.querySelectorAll('#screen .event')].find(e=>/隔壁/.test(e.textContent));return e?e.innerText.replace(/\\n/g,' '):''})()"))
    g.ev("factSet('lin_closed');for(const k in BGC)delete BGC[k]"); v.to_service(g); g.ev("window.__act=window.__actLazy")
    g.ev("__botUntil('R.t>=R.dur*.5',200000,1/30)"); go(g, 'front', 3); shot(g, 'b17_street_after_her_last_night.png')
    g.ev("const st=story();for(const k of ['ken_where','jd_want','dylan_book','lin_viewing','lin_take'])st.facts[k]={d:S.day-1,n:1,l:S.day-1};st.facts.lin_hello={d:1,n:1,l:1};for(const k of ['lin_hello','pairing_start','lin_retire','ken_where','jd_want','dylan_book','lin_viewing'])evState(k).n=1")
    g.ev("openStory('nextdoor')"); g.ev("__tick(100)"); g.page.wait_for_timeout(200)
    shot(g, 'b18_story_page_next_door.png')
    log.append('3. page: ' + g.ev("(()=>{const e=document.querySelector('#screen');return e?e.innerText.replace(/\\n+/g,' | ').slice(0,600):''})()"))
    log.append(f'errors: {g.errors[:3]}'); g.close()
    b.close()
srv.shutdown()
open(OUT + 'log.txt', 'w', encoding='utf-8').write('\n'.join(log) + '\n'); print('\n'.join(log))
