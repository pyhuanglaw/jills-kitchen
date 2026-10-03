"""Checkpoint C (the player's brief of 2026-10-02 19:19 §26): the signing, the work and the opening; Madame Lin as a guest;
mature-save migration; Evan's continuity; the restaurant's three lists and the Lounge's own; a legacy save over a list;
the bell on the door. Headless Chromium at 390x844 on the player's saves (T, not O). Each claim is checked and logged
as OK / FAIL in log.txt beside the screenshots.   python3 shot_cpC.py ROOT OUT"""
import sys, os, json, copy
ROOT = sys.argv[1]; OUT = sys.argv[2].rstrip('/') + '/'
sys.path.insert(0, ROOT + '/tests'); os.chdir(ROOT)
import run_tests as rt, v24_tests as v
from playwright.sync_api import sync_playwright
os.makedirs(OUT, exist_ok=True)
srv, port = rt.start_server()
log = []
VP = {'width': 390, 'height': 844}
fails = 0


def ok(cond, what):
    global fails
    if not cond: fails += 1
    log.append(('OK    ' if cond else 'FAIL  ') + what); print(log[-1], flush=True)


def clean(g):
    g.ev("try{hud(true)}catch(e){};document.querySelectorAll('#plines>*,#toasts>*,#banner>*').forEach(e=>e.remove())")


def shot(g, name):
    clean(g); g.page.wait_for_timeout(120); g.page.screenshot(path=OUT + name); print('  shot', name, flush=True)


def go(g, rm, n=4):
    g.ev(f"setRoom('{rm}')"); g.ev(f"for(let i=0;i<{n};i++)__tick(1000/30)")


def held(g, prefix, cap=40):
    """step through the held scene on screen, a screenshot of every line; the lines as 「name：text」"""
    out = []
    for i in range(cap):
        if not g.ev("!!(typeof DLG!=='undefined'&&DLG)"): break
        line = g.ev("(()=>{const n=document.querySelector('#dlg .dlg-name'),t=document.querySelector('#dlg .dlg-text');return(n&&n.textContent?n.textContent+'：':'')+(t?t.textContent:'')})()")
        out.append(line); g.ev("__tick(400)"); shot(g, f'{prefix}_{i + 1:02d}.png')
        g.ev("__tick(400);dlgNext()"); g.ev("for(let j=0;j<2;j++)__tick(1000/30)")
    return out


def staff_tab(g, name):
    g.ev("showShop();shopTab='staff';showShop()"); g.page.wait_for_timeout(100)
    g.ev("(()=>{const e=document.querySelector('#screen .capline');if(e)e.scrollIntoView({block:'start'})})()")
    shot(g, name)
    return g.ev("(document.querySelector('#screen .capline')||{}).innerText||''")


def crew_of(g):
    return json.loads(g.ev("JSON.stringify((S.crew||[]).map(m=>({id:m.id,name:m.name,role:m.role,pool:crewPool(m),lv:m.lv,since:m.since,days:m.days})))"))


with sync_playwright() as p:
    b = p.chromium.launch()

    # 1. 《簽約》, the work, the opening — before and after the reveal (the Day 52 save with the line's earlier beats as facts)
    for reveal in (False, True):
        tag = 'after_reveal' if reveal else 'before_reveal'
        g = rt.Game(b, port, 'index', seed=8711 + reveal, manual=True, viewport=VP)
        v.load_save(g, 'player_day52.json'); g.ev(v._LIN_TAKEN)
        if reveal: g.ev("S.dylan.stage=3;S.dylan.reveal=S.day-5")
        g.ev("showShop();shopTab='works';showShop()"); g.page.wait_for_timeout(80)
        g.ev("(()=>{const e=document.querySelector('#screen .lin-card');if(e)e.scrollIntoView({block:'center'})})()")
        if not reveal: shot(g, 'c01_works_before_her_last_night.png')
        g.ev("factSet('lin_closed');showShop()"); g.page.wait_for_timeout(80)
        g.ev("(()=>{const e=document.querySelector('#screen .lin-card');if(e)e.scrollIntoView({block:'center'})})()")
        if not reveal: shot(g, 'c02_works_sign_and_start.png')
        g.click('#screen [data-act=linSign]'); g.page.wait_for_timeout(80)
        g.ev("(()=>{const e=document.querySelector('#screen .lin-card');if(e)e.scrollIntoView({block:'center'})})()")
        if not reveal: shot(g, 'c03_works_paid_the_signing_tomorrow.png')
        g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(120)
        g.ev("autoStock();window.__noScenes=false;window.__holds=true"); rt.start_day(g); rt.install_bot(g); g.ev("for(let i=0;i<3;i++)__tick(1000/30)")
        ok(g.ev("!!(DLG&&DLG.sh&&DLG.sh.k==='lin_sign')") and g.ev("room") == 'lounge', f'{tag}: 《簽約》 held at the opening, in her bar')
        lines = held(g, f'c04_signing_{tag}')
        log.append(f'      {tag} lines: ' + ' / '.join(lines)); print(log[-1], flush=True)
        intro = ['Madame Lin：Evan，這 Dylan。', 'Madame Lin：Jill 老公。', 'Evan：你好。', 'Dylan：你好。'] if reveal else ['Madame Lin：Evan，這 Jill 老公。', 'Evan：你好。', '先生：你好。']
        at = next((i for i in range(len(lines)) if lines[i:i + len(intro)] == intro), -1)
        ok(at >= 0 and lines.index('Madame Lin 把鑰匙交給她。') < at, f'{tag}: after the keys, Evan meets Dylan — {" ".join(intro)}')
        ok(g.ev("!!fact('evan_knows_dylan')") and (reveal or g.ev("S.dylan.stage") < 3), f'{tag}: Evan knows Dylan now; the restaurant\'s reveal untouched (stage {g.ev("S.dylan.stage")})')
        go(g, 'front', 3); shot(g, f'c05_street_papered_over_{tag}.png')
        ok(g.ev("barState()") == 'reno' and g.ev("S.loungeProj.open") == g.ev("S.day") + 2, f'{tag}: papered over, two days of work')
        g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;window.__noScenes=true"); g.ev("__botUntil('phase!==\"service\"',200000,1/30)"); g.page.wait_for_timeout(60)
        g.ev("for(let i=0;i<80&&typeof DLG!=='undefined'&&DLG;i++){__tick(400);dlgNext()}")
        if g.ev("phase") == 'summary': g.click('[data-act=toShop]'); g.page.wait_for_timeout(60)
        g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(100); g.ev("__tick(1200)")
        g.ev("doAct('nextDay',null,null,null)"); g.page.wait_for_timeout(60); g.ev("__tick(600)"); g.page.wait_for_timeout(60); g.ev("__tick(900)"); g.page.wait_for_timeout(60)
        rv = g.ev("($('#reveal')&&!$('#reveal').hidden)?$('#reveal').innerText:''")
        if not reveal: shot(g, 'c06_morning_card_the_lounge_opens.png')
        ok('開幕' in rv and 'The Lounge' in rv, f'{tag}: the morning card 「開幕 · The Lounge」')
        ev = json.loads(g.ev("JSON.stringify((S.crew||[]).filter(m=>m.name==='Evan').map(m=>({role:m.role,pool:crewPool(m),since:m.since,day:S.day})))"))
        ok(len(ev) == 1 and ev[0]['role'] == 'bartender' and ev[0]['pool'] == 'lounge' and ev[0]['since'] == ev[0]['day'], f'{tag}: Evan on The Lounge\'s list from the opening day, never hired: {ev}')
        g.click('#reveal [data-act=revealPrep]'); g.page.wait_for_timeout(60)
        if not reveal:
            hires = g.ev("JSON.stringify([...document.querySelectorAll('[data-act=hireLounge]')].map(e=>e.dataset.k))")
            line = staff_tab(g, 'c07_staff_tab_evan_on_the_lounge_list.png')
            ok('Evan' not in json.loads(g.ev("JSON.stringify([...document.querySelectorAll('#screen [data-act=hireLounge]')].map(e=>e.dataset.k))")), 'no recruitment card for Evan on the Lounge\'s list')
            log.append('      staff line: ' + line.replace('\n', ' ')[:300])
            go(g, 'front', 3); shot(g, 'c08_street_the_lounge_next_door.png')
        ok(not g.errors, f'{tag}: no page errors {g.errors[:2]}'); g.close()

    # 2. Madame Lin as a guest at The Lounge (the player's Day 61 save)
    g = rt.Game(b, port, 'index', seed=8721, manual=True, viewport=VP)
    v.load_save(g, 'player_day61.json'); g.ev("S.day=loungeDoneDay()+5")
    v.to_service(g); g.ev("window.__act=window.__actLazy;window.__noScenes=true")
    g.ev("R.sched=R.sched.filter(o=>o.name!=='Madame Lin');namedHist('Madame Lin').seen=S.day")
    g.ev("__botUntil('R.t>=R.dur*.3',200000,1/30)")
    g.ev("(()=>{const v=v24();v.res={d:S.day,k:['lin_guest']}})();R.sched.splice(R.si,0,{t:R.t+2,type:'vip',size:1,name:'Madame Lin',story:1,lounge:1,lgRetry:1,tries:1});window.__noScenes=false;window.__holds=true")
    for _ in range(12):
        g.ev("__botUntil(\"!!(typeof DLG!=='undefined'&&DLG)||R.groups.some(q=>namedId(q)==='Madame Lin')\",900,1/30)")
        if g.ev("!!DLG") and g.ev("DLG.sh?DLG.sh.k:''") != 'lin_guest':
            g.ev("for(let i=0;i<40&&DLG&&!(DLG.sh&&DLG.sh.k==='lin_guest');i++){__tick(400);dlgNext()}"); continue
        break
    lines = held(g, 'c09_lin_guest')
    log.append('      lin_guest lines: ' + ' / '.join(lines)); print(log[-1], flush=True)
    ok(lines == ['開門進來的是 Madame Lin。', 'Jill：坐哪？', 'Madame Lin 看了一下。', 'Madame Lin：隨便。', 'Evan：喝什麼？', '她看了看酒單。', 'Madame Lin：你選。'], 'Madame Lin, retired, comes in as a guest: 「坐哪？」「隨便。」「喝什麼？」「你選。」')
    g.ev("window.__noScenes=true;for(let i=0;i<90;i++)__tick(1000/30)"); go(g, 'lounge', 3); shot(g, 'c10_lounge_madame_lin_at_the_bar.png')
    ok(not g.errors, f'lin_guest: no page errors {g.errors[:2]}'); g.close()

    # 3. mature saves: everything kept, the line as history, nothing played (Day 61, Day 74)
    for name in ('player_day61.json', 'player_day74_1508.json'):
        d = name.split('_')[1].split('.')[0]
        g = rt.Game(b, port, 'index', seed=8731, manual=True, viewport=VP)
        raw = v.load_save(g, name)
        c1 = crew_of(g)
        ok(sorted((m['name'], m['role'], m['since'], m['lv']) for m in c1) == sorted((m['name'], m['role'], m.get('since'), m.get('lv')) for m in raw['crew']), f'{name}: every employee kept with name, role, since (tenure) and level ({len(c1)})')
        F0 = raw['story']['facts']; F = json.loads(g.ev("JSON.stringify(story().facts)"))
        ok(all(F.get(k) == val for k, val in F0.items()), f'{name}: every story fact it had, unchanged ({len(F0)}), incl. 晴×阿拓 {sorted(k for k in F0 if k.startswith("qt_"))}')
        ok(g.ev("loungeLv()") == raw['rooms']['lounge'] and g.ev("S.dylan.stage") == raw['dylan']['stage'] and g.ev("!!fact('tasting_night')") == ('tasting_night' in F0), f'{name}: The Lounge {raw["rooms"]["lounge"]}, Dylan stage {raw["dylan"]["stage"]}, Ken\'s wine as it was')
        added = sorted(set(F) - set(F0))
        ok(all(F[k].get('retro') == 1 for k in added if k.startswith('lin_') or k in ('pairing_wine', 'ken_where', 'jd_want', 'dylan_book', 'evan_knows_dylan')), f'{name}: the Madame Lin line given as history (retro): {added}')
        v.to_service(g); g.ev("__botUntil('phase!==\"service\"',200000,1/30)")
        new = json.loads(g.ev("JSON.stringify(story().trace.filter(t=>t.d===S.day&&['lin_hello','pairing_start','lin_retire','ken_where','jd_want','dylan_book','lin_viewing','lin_decide','lin_last','lin_sign'].includes(t.k)).map(t=>t.k))"))
        ok(not new, f'{name}: a whole day played — no catch-up of the line: {new}')
        g.ev("for(let i=0;i<80&&typeof DLG!=='undefined'&&DLG;i++){__tick(400);dlgNext()}")
        g.ev("openStory('nextdoor')"); g.ev("__tick(100)"); g.page.wait_for_timeout(150); shot(g, f'c11_story_page_next_door_{d}.png')
        ok('更早以前' in g.ev("document.querySelector('#screen').innerText"), f'{name}: the story page 「隔壁」 says 「更早以前」')
        g.ev("hideScreen&&hideScreen();sub=null")
        line = staff_tab(g, f'c12_staff_tab_three_lists_{d}.png'); log.append(f'      {name} staff line: ' + line.replace('\n', ' ')[:300])
        ok(not g.errors, f'{name}: no page errors {g.errors[:2]}'); g.close()

    # 4. a legacy save over a list (the old shared number): nobody leaves; that list waits; the others hire as before
    raw = json.load(open(os.path.join(ROOT, 'tests', 'saves', 'player_day61.json'), encoding='utf-8')); raw = raw.get('save', raw)
    over = copy.deepcopy(raw)
    ws = [m for m in over['crew'] if m['role'] == 'waiter']
    for i, nm in enumerate(['小茉', 'Kai']):
        if any(m['name'] == nm for m in over['crew']): nm = nm + '2'
        m = copy.deepcopy(ws[0]); m['id'] = 'cover%d' % i; m['name'] = nm; m['since'] = 3 + i; over['crew'].append(m)
    g = rt.Game(b, port, 'index', seed=8751, manual=True, viewport=VP)
    g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(over, ensure_ascii=False)); g.reload(); g.page.wait_for_timeout(150)
    g.click('[data-act=openFresh]') if g.page.query_selector('[data-act=openFresh]') else g.click('[data-act=open]'); g.page.wait_for_timeout(150)
    n0 = len(over['crew']); wn, wc = g.ev("roleCrew('waiter').length"), g.ev("roleCap('waiter')")
    ok(g.ev("S.crew.length") == n0 and wn > wc, f'over the waiters\' number ({wn}/{wc}): all {n0} kept on load')
    line = staff_tab(g, 'c13_staff_tab_over_a_list_everyone_stays.png'); log.append('      over-list staff line: ' + line.replace('\n', ' ')[:300])
    ok('大家都留著' in line, 'the staff page says everyone stays')
    g.ev("S.money+=500000"); v._hire(g, 'hire', 'waiter'); g.ev("__tick(30)")
    ok(g.ev("roleCrew('waiter').length") == wn, 'no waiter is hired while the list is over its number')
    v._reload(g); v.to_service(g); g.ev("__botUntil('phase!==\"service\"',200000,1/30)")
    v._reload(g)
    ok(g.ev("S.crew.length") == n0 and g.ev("roleCrew('waiter').length") == wn, f'after a day and a reload: still all {n0}, nobody fired')
    ok(not g.errors, f'over-list: no page errors {g.errors[:2]}'); g.close()

    # 5. a new game: three lists from Day 1, a chef's place takes no waiter; the bell on the door from Madame Lin's visit on
    g = rt.Game(b, port, 'index', seed=8601, manual=True, viewport=VP)
    g.click('[data-act=open]'); g.page.wait_for_timeout(100)
    g.ev("S.money=99999;S.day=5;shopTab='staff';showShop()"); g.page.wait_for_timeout(80)
    for k in ('waiter', 'cleaner'):
        v._act(g, 'hire', k=k); g.ev("__tick(30)")
    ok(g.ev("(S.crew||[]).length") == 0, 'a new game: the chef\'s place takes no waiter and no cleaner')
    line = staff_tab(g, 'c14_staff_tab_new_game_three_lists.png'); log.append('      new game staff line: ' + line.replace('\n', ' ')[:300])
    g.close()
    g = rt.Game(b, port, 'index', seed=8741, manual=True, viewport=VP)
    g.ev("__tick(500)"); g.click('[data-act=open]'); g.page.wait_for_timeout(120)
    rt.start_day(g); rt.install_bot(g)
    ok(g.ev("propOn('linbell')") is True, 'Day 1: the bell is on the door')
    g.ev("window.__r=0;const __br=bellRing;bellRing=function(){const t0=BELL.t;const r=__br.apply(this,arguments);if(BELL.t!==t0)__r++;return r}")
    g.ev("__botUntil('__r>0',20000,1/30)"); g.ev("__tick(60)"); go(g, 'main', 1); shot(g, 'c15_day1_the_bell_rings_at_the_door.png')
    g.close()
    g = rt.Game(b, port, 'index', seed=8742, manual=True, viewport=VP)
    v.load_save(g, 'player_day74_1508.json'); ok(g.ev("propOn('linbell')") is True, 'Day 74 save (The Lounge III): the bell still on the door')
    v._reload(g); ok(g.ev("propOn('linbell')") is True, 'and after a reload')
    g.close()
    b.close()
srv.shutdown()
log.append(f'\n{fails} FAIL')
open(OUT + 'log.txt', 'w', encoding='utf-8').write('\n'.join(log) + '\n'); print(f'{fails} FAIL')
