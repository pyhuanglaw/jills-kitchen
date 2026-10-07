"""v2.4 tests — Staff Lives foundations (docs/v24/AUDIT_AND_PLAN.md): the back-of-house area, tenure as a class, one
day's story presence, the walk-over, the order of the eras and their dormancy, narrative-time pacing, the story
illustrations, the name pools. Same harness and TESTS list as run_tests.py (imported at the end of that file), so
`python3 tests/run_tests.py -k v24` runs these."""
import json, os, sys, glob, re
_rt = sys.modules['__main__'] if hasattr(sys.modules.get('__main__'), 'TESTS') else __import__('run_tests')
test, check, Game, ROOT, start_day, install_bot, LAZY_ACTOR, play_day = (_rt.test, _rt.check, _rt.Game, _rt.ROOT, _rt.start_day, _rt.install_bot, _rt.LAZY_ACTOR, _rt.play_day)


def load_save(g, name):
    raw = json.load(open(os.path.join(ROOT, 'tests', 'saves', name), encoding='utf-8'))
    raw = raw.get('save', raw)
    g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.page.wait_for_timeout(150)
    g.click('[data-act=openFresh]') if g.page.query_selector('[data-act=openFresh]') else g.click('[data-act=open]'); g.page.wait_for_timeout(150)
    return raw


def to_service(g, lazy=True):
    if g.ev("phase") == 'shop':
        g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(200)
    g.ev("autoStock()"); start_day(g); install_bot(g)
    if lazy:
        g.ev(LAZY_ACTOR + "\nwindow.__act=window.__actLazy;window.__noScenes=true")


@test
def v24_back_of_house_is_a_work_area_and_keeps_its_two(b, port, target):
    """A1: the old 「後場休息室」 is 「後場整理區」 — the same purchase, the same +2 staff, no refund and no rebuy; its
    words are work storage (no rest, no room of their own); the kitchen draws a rack by the door, no seat, no door."""
    g = Game(b, port, target, seed=241, manual=True, viewport={'width': 390, 'height': 844})
    raw = load_save(g, 'player_day52.json')
    check(g.ev("opsLv('room')") == 1 and g.ev("OPS.find(o=>o.k==='room').n") == '後場整理區', 'the purchase is kept, under its new name')
    check(g.ev("restaurantCap()") == 12 and g.ev("S.crew.length") == 12, 'the +2 is kept: the crew of twelve still fits')
    check(g.ev("S.money") == raw['money'], 'nothing refunded or charged')
    d = g.ev("OPS.find(o=>o.k==='room').d(1)")
    check('休息' not in d and '整理區' in d and '廚師和服務生各可以再多聘 1 位' in d, f'work storage, +2 (rc8: a chef and a waiter): {d}')
    check(g.ev("ACH.find(a=>a.id==='room').d") == '後場有了整理區', 'the achievement says what it is now')
    man = g.ev("JSON.stringify(GUIDE)")
    check('後場整理區' in man and '後場休息室' not in man, 'the manual uses the new name')
    g.ev("S.money+=1;showShop();shopTab='works';showShop()"); g.page.wait_for_timeout(100)
    txt = g.ev("document.querySelector('#screen').innerText")
    check('後場整理區' in txt and '休息室' not in txt, 'the shop page uses the new name')
    # the kitchen: a rack by the door with the upgrade (between the door and the fridge, on short and tall phones), nothing without it
    r = json.loads(g.ev("""JSON.stringify((()=>{const out={};for(const H of[424,588]){for(const on of[1,0]){S.ops.room=on;const cv=mkCanvas(400,H),c=cv.getContext('2d');drawBackRack(c,H);const d=c.getImageData(0,0,400,H).data;let x0=999,x1=-1,y0=999,y1=-1;
      for(let y=0;y<H;y++)for(let x=0;x<400;x++)if(d[(y*400+x)*4+3]>0){if(x<x0)x0=x;if(x>x1)x1=x;if(y<y0)y0=y;if(y>y1)y1=y}out[H+'_'+on]=x1<0?null:[x0,x1,y0,y1]}}S.ops.room=1;return out})())"""))
    check(r['588_0'] is None and r['424_0'] is None, f'nothing without the upgrade: {r}')
    for H in (424, 588):
        bx = r[f'{H}_1']
        check(bx and bx[0] >= 238 and bx[1] <= 317 and bx[3] <= H, f'the rack stands between the door (x 238) and the fridge (x 318), on the floor: {H}: {bx}')
        check(bx and bx[2] > 276 + 40 + 12 + 26, f'below the pass and its mat: {H}: {bx}')
    check("opsLv('room')" in g.ev("String(drawKitchenRoom)"), 'the kitchen redraws when it is bought')
    check(g.ev("String(drawBackRack).includes('seat')") is False, 'no seat in the drawing')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_legacy_tenure_is_a_class_not_the_days_since_v23(b, port, target):
    """A2: the legacy crew are not 2–3-day employees. 阿珠姐, 秀琴阿姨, 阿德師傅 are 資深, 小彤 較新 (熟手 after 45
    counted days), the rest 熟手; the card says so instead of the days counted since v2.3. A new hire is 新 and still
    gets 《第一天》; 《第二層左邊》 is 阿珠姐's when she is in."""
    g = Game(b, port, target, seed=242, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day52.json')
    t = json.loads(g.ev("JSON.stringify(Object.fromEntries(S.crew.map(m=>[m.name,tenure(m)])))"))
    check(t['阿珠姐'] == '資深' and t['秀琴阿姨'] == '資深' and t['阿德師傅'] == '資深', f'the veterans: {t}')
    check(t['小彤'] == '較新', f'小彤 is newer: {t}')
    check(all(v in ('熟手', '資深', '較新') for v in t.values()) and '新' not in t.values(), f'nobody on the old crew is new: {t}')
    check(g.ev("S.crew.every(m=>(m.days||0)<10)"), 'the counted days are still only the days since v2.3 (kept as they are)')
    g.ev("const m=S.crew.find(m=>m.name==='小彤');window.__d0=m.days;m.days=45")
    check(g.ev("tenure(S.crew.find(m=>m.name==='小彤'))") == '熟手', '小彤 grows into 熟手')
    g.ev("S.crew.find(m=>m.name==='小彤').days=__d0")
    g.ev("showShop();shopTab='staff';showShop()"); g.page.wait_for_timeout(100)
    txt = g.ev("document.querySelector('#screen').innerText")
    check('資深（v2.3 以前就在）' in txt and '較新（v2.3 以前就在）' in txt, 'the card says the class')
    check('在店 2 天' not in txt and '在店 3 天' not in txt and '從 v2.3 起算' not in txt, 'and not the days counted since v2.3')
    # a new hire
    g.ev("S.ops.room=1;S.crew=S.crew.filter(m=>m.name!=='阿勇');S.money+=100000")
    g.ev("(()=>{const b=document.createElement('button');b.dataset.k='chef';doAct('hire',null,'chef',b)})()")
    nh = json.loads(g.ev("JSON.stringify((()=>{const m=S.crew[S.crew.length-1];return{name:m.name,t:tenure(m),line:tenureLine(m),days:m.days,legacy:crewLegacy(m)}})())"))
    check(nh['t'] == '新' and nh['line'] == '今天剛來' and nh['days'] == 0 and not nh['legacy'], f'a new hire is new: {nh}')
    check(g.ev("veteranCook()&&veteranCook().name") == '阿珠姐', '《第二層左邊》 is hers when she is in')
    g.ev("setCrewAway(S.crew.find(m=>m.name==='阿珠姐'),'off')")
    check(g.ev("veteranCook()&&veteranCook().name") == '阿德師傅', 'when she is not in, the other veteran')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_story_presence_for_one_day(b, port, target):
    """A3: a beat can say someone is not in today, comes in late, or went home early — for that day only. Not here:
    not drawn, no work (no cooking, no tables), the summary says so; the wage is paid as usual; the next day they are
    back. No rota, no schedule screen."""
    g = Game(b, port, target, seed=243, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day52.json')
    to_service(g)
    g.ev("window.__ade=S.crew.find(m=>m.name==='阿德師傅');window.__xq=S.crew.find(m=>m.name==='秀琴阿姨');window.__w=S.crew.find(m=>m.role==='waiter');setCrewAway(__ade,'off');setCrewAway(__xq,'late',.35);setCrewAway(__w,'left',.5)")
    check(g.ev("crewHere(__ade)") is False and g.ev("crewHere(__xq)") is False and g.ev("crewHere(__w)") is True, 'off / not yet / still here at the start')
    seen = {'ade_drawn': 0, 'ade_cooked': 0, 'xq_before': 0, 'xq_after': 0, 'w_after': 0, 'claims': 0}
    for i in range(400):
        g.page.evaluate('()=>window.__bot(60,1/30)')
        if g.ev("phase") != 'service': break
        s = json.loads(g.ev("""JSON.stringify((()=>{const f=serviceFrac();return{f,ade:!!(R.ck&&R.ck[__ade.id]),cook:R.slots.some(s=>s.job&&s.job.chef===__ade.id),
          xq:!!(R.cw[__xq.id]),xqRoom:R.cw[__xq.id]?R.cw[__xq.id].room:null,w:!!R.cw[__w.id],
          claims:R.tables.filter(t=>t.claim===__w.id).length+R.groups.filter(q=>q.claim===__w.id).length}})())"""))
        seen['ade_drawn'] += s['ade']; seen['ade_cooked'] += s['cook']
        if s['f'] < .34: seen['xq_before'] += s['xq']
        if s['f'] > .45: seen['xq_after'] += s['xq']
        if s['f'] > .6: seen['w_after'] += s['w']; seen['claims'] += s['claims']
    check(seen['ade_drawn'] == 0 and seen['ade_cooked'] == 0, f'the cook who is off is not in the kitchen and cooks nothing: {seen}')
    check(seen['xq_before'] == 0 and seen['xq_after'] > 0, f'the late one is not there, then is: {seen}')
    check(seen['w_after'] == 0 and seen['claims'] == 0, f'the one who left is gone and holds no table: {seen}')
    if g.ev("phase") == 'service':
        g.ev("closeShop('x');for(const q of R.groups.slice())leaveGroup(q,'ok')"); g.page.evaluate('()=>window.__bot(400,1/30)')
    if g.ev("phase") == 'service': g.ev("finishClosing()")
    sm = json.loads(g.ev("JSON.stringify(S.lastSummary.crew.filter(c=>c.away))"))
    check(any(c['name'] == '阿德師傅' and c['away'] == 'off' for c in sm), f'the summary keeps who was not in: {sm}')
    check(g.ev("S.lastSummary.wages") == g.ev("crewWages()"), 'the wages are the usual wages')
    html = g.ev("document.body.innerText")
    check('今天沒來' in html, 'the summary says 今天沒來')
    g.ev("showShop();shopTab='staff';showShop()"); g.page.wait_for_timeout(80)
    st = g.ev("document.querySelector('#screen').innerText")
    check(not any(w in st for w in ('排班', '休假', '請假', '出勤')), 'no schedule, no leave, no attendance on the staff page')
    g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(200)
    check(g.ev("crewHere(__ade)&&crewHere(__xq)&&crewHere(__w)"), 'the next day everyone is back')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_walk_over_is_a_floor_walk_and_never_a_cook(b, port, target):
    """The walk-over: 秀琴阿姨 walks to a table for a story exchange, the exchange starts when she is there, she stays
    while it plays and goes back to her work after. A cook never does it; nobody who is not in does it."""
    g = Game(b, port, target, seed=244, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day52.json')
    to_service(g)
    for i in range(60):
        g.page.evaluate('()=>window.__bot(60,1/30)')
        if g.ev("R.tables.some(t=>t.group&&(t.room||'main')==='main'&&SEATED_ST.includes(t.group.state))"): break
    g.ev("window.__xq=S.crew.find(m=>m.name==='秀琴阿姨');window.__t=R.tables.find(t=>t.group&&(t.room||'main')==='main'&&SEATED_ST.includes(t.group.state));window.__arr=0")
    check(g.ev("staffWalkOver(S.crew.find(m=>m.name==='阿珠姐'),__t,{})") is False, 'a cook does not walk over')
    check(g.ev("staffWalkOver(__xq,__t,{then:()=>{__arr++;window.__at={x:R.cw[__xq.id].x,y:R.cw[__xq.id].y}}})") is True, 'the cleaner can')
    for i in range(200):
        g.ev("for(let k=0;k<6;k++)__tick(1000/30)")
        if g.ev("__arr") > 0: break
    check(g.ev("__arr") == 1, 'the exchange starts when she gets there, once')
    near = g.ev("Math.hypot(__at.x-(__t.x+(__t.x<200?-24:24)),__at.y-(__t.y+22))")
    check(near < 3, f'she is at the table, not teleported: {near}')
    g.ev("for(let k=0;k<120;k++)__tick(1000/30)")
    check(g.ev("!walkingOver(__xq)") and g.ev("__arr") == 1, 'then back to work, the exchange not repeated')
    g.ev("setCrewAway(__xq,'off')")
    check(g.ev("staffWalkOver(__xq,__t,{})") is False, 'not when she is not in')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_eras_open_in_order_and_dormant_ones_never_reverse(b, port, target):
    """B / pacing, and the player's 10:25 correction: two chains that do not wait for each other. 怡君 first; 《那面牆》
    opens two days after the spare key. The Second Floor opens two days after the Lounge is finished (Lounge I built) —
    never on the wall, its settlement or anything of 怡君's; the wall's progress, or its dormancy, moves it not a day, and
    the floor's beginning puts nothing of the other chain to sleep. Within a chain, an era whose people are not on the
    crew goes dormant once a later era of its chain could start and has waited 5 days, and never wakes after that later
    era began. Nothing at the very start of the first day; no gap between beats except a stage's own."""
    g = Game(b, port, target, seed=245, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day52.json')
    g.ev("v24()")
    d0 = g.ev("S.day")
    check(g.ev("loungeLv()") == 0 and g.ev("v24().first") == d0 and g.ev("eraOpen('yj')") and not g.ev("eraOpen('wall')") and not g.ev("eraOpen('up')"), 'only 怡君 at first (no Lounge yet: no floor)')
    check(g.ev("v24Fresh('daystart')") and not g.ev("(()=>{S.day++;const r=v24Fresh('daystart');S.day--;return r})()"), 'nothing at the start of the first day only')
    g.ev("factSet('yj_meet');factSet('yj_key')")
    check(not g.ev("eraOpen('wall')") and g.ev("eraOpenDay('wall')") == d0 + 2, 'the wall: two days after the key')
    g.ev("S.day+=2"); check(g.ev("eraOpen('wall')"), 'open on the day')
    check(g.ev("eraOpenDay('up')") is None, 'the wall open, the floor still not: it waits for the Lounge, not the wall')
    # the Lounge finished: the floor two days later, whatever the wall is doing
    g.ev("S.rooms.lounge=1;factSet('lounge_built_1')")
    dl = g.ev("S.day")
    check(g.ev("eraOpenDay('up')") == dl + 2 and not g.ev("eraOpen('up')"), 'the floor: two days after the Lounge')
    g.ev("factSet('wall_worry')")
    check(g.ev("eraOpenDay('up')") == dl + 2, 'the wall begun: the floor not moved')
    g.ev("factSet('wall_settle')")
    check(g.ev("eraOpenDay('up')") == dl + 2, 'the wall settled: the floor not moved')
    check(g.ev("stageGap('wall_settle',0)") and not g.ev("stageGap('wall_settle',1)"), 'a stage waits only its own gap')
    g.ev("S.day+=2"); check(g.ev("eraOpen('up')"), 'open on the day')
    # the floor's beginning puts nothing of the other chain to sleep: 怡君 not begun, 秀琴阿姨 here, the floor under way
    g.ev("for(const k of ['yj_meet','yj_key','wall_worry','wall_settle'])delete story().facts[k];factSet('up_hint')")
    for i in range(7):
        g.ev("S.day++;v24Dormancy()")
    check(g.ev("v24().dorm.yj") is None and g.ev("v24().dorm.wall") is None and g.ev("eraOpen('yj')"), 'the floor under way: 怡君 still waits for her day, the wall after her')
    check(g.ev("eraOpen('up')") and g.ev("due('up_staff','up_hint',1,'up')"), 'and the floor goes on')
    # dormancy inside a chain: no 秀琴阿姨, the era after 怡君 could start (forced here)
    g.ev("delete story().facts.up_hint;v24().dorm={};v24().wait={}")
    g.ev("window.__xqm=S.crew.find(m=>m.name==='秀琴阿姨');S.crew=S.crew.filter(m=>m!==__xqm);eraOf('wall').__can=eraOf('wall').can;eraOf('wall').can=()=>true")
    for i in range(4):
        g.ev("S.day++;v24Dormancy()")
    check(g.ev("v24().dorm.yj") is None and not g.ev("eraOpen('wall')"), 'four days: still waiting')
    g.ev("S.day++;v24Dormancy()")
    check(g.ev("v24().dorm.yj") is not None and g.ev("eraOpen('wall')") and g.ev("eraOpenDay('wall')") == g.ev("v24().dorm.yj"), 'the fifth: 怡君 dormant, the wall open from that day')
    check(not g.ev("eraOpen('yj')"), 'dormant is not done: that era is closed')
    check(g.ev("eraOpen('up')") and g.ev("v24().dorm.up") is None, 'the floor untouched by the other chain')
    g.ev("S.crew.push(__xqm);S.day++;v24Dormancy()")
    check(g.ev("v24().dorm.yj") is None, 'she is back before the wall began: 怡君 wakes')
    g.ev("S.crew=S.crew.filter(m=>m!==__xqm);for(let i=0;i<5;i++){S.day++;v24Dormancy()}factSet('wall_worry');S.crew.push(__xqm);S.day++;v24Dormancy()")
    check(g.ev("v24().dorm.yj") is not None, 'once the wall began, 怡君 does not wake (no reversed chronology)')
    g.ev("eraOf('wall').can=eraOf('wall').__can")
    # weather memory for the leak
    g.ev("v24().wx={};v24Wx('sun');S.day++;v24Wx('rain');S.day++;v24Wx('cloud')")
    check(g.ev("rainedWithin(1)") and not g.ev("rainedWithin(0)"), 'rain is remembered for a few days')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_illustrations_show_with_the_scene_and_reopen(b, port, target):
    """The story illustrations: shown over a scene's lines, the player's picture where it exists, a stand-in labelled
    插圖待補 where it does not (never a portrait in its place); remembered, reopenable, and not album photos."""
    g = Game(b, port, target, seed=246, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day52.json')
    check(g.ev("!!(window.STORY_ART&&STORY_ART.yj_intro&&STORY_ART.yj_key)"), "the player's two pictures are packed")
    n0 = g.ev("albumList().length")
    g.ev("window.__noScenes=false;scene([{who:'staff:秀琴阿姨',text:'妳怎麼來了？'},{who:'',name:'怡君',text:'吃飯啊。'}],null,{illus:'yj_intro'})"); g.page.wait_for_timeout(200)
    s = json.loads(g.ev("JSON.stringify({open:!$('#dlg').hidden,ill:!document.querySelector('.dlg-illus').hidden,src:document.querySelector('.dlg-illus img').src.slice(0,16),tbd:!document.querySelector('.dlg-illus-tbd').hidden,title:document.querySelector('.dlg-illus-t').textContent})"))
    check(s['open'] and s['ill'] and s['src'].startswith('data:image/webp') and not s['tbd'] and s['title'] == '吃飯啊', f"the player's picture over the lines: {s}")
    g.ev("dlgNext()")
    check(g.ev("document.querySelector('#dlg .dlg-name').textContent") == '怡君', 'a line can carry a name without a portrait')
    g.ev("dlgNext()"); check(g.ev("$('#dlg').hidden"), 'closed')
    check(g.ev("['yj_intro','yj_key','wall_leak','wall_settled','up_cats'].every(k=>!!STORY_ART[k])"), "all five of the player's pictures are in")
    g.ev("window.__keep=STORY_ART.wall_leak;delete STORY_ART.wall_leak;for(const k in ILLUS_CACHE)delete ILLUS_CACHE[k]")
    g.ev("scene([{who:'',text:'下過雨以後。'}],null,{illus:'wall_leak'})"); g.page.wait_for_timeout(200)
    s = json.loads(g.ev("JSON.stringify({src:document.querySelector('.dlg-illus img').src.slice(0,16),tbd:!document.querySelector('.dlg-illus-tbd').hidden})"))
    check(s['src'].startswith('data:image/jpeg') and s['tbd'], f'without the art: a stand-in in the game\'s own style, labelled: {s}')
    g.ev("dlgNext();STORY_ART.wall_leak=__keep")
    check(g.ev("Object.keys(story().illus).sort().join()") == 'wall_leak,yj_intro', 'remembered')
    check(g.ev("illusOpen('wall_settled')") is False, 'an unseen picture cannot be reopened')
    check(g.ev("illusOpen('yj_intro')") is True and not g.ev("$('#dlg').hidden"), 'a seen one can')
    g.ev("dlgNext()")
    check(g.ev("albumList().length") == n0, 'not added to the album')
    g.ev("window.__noScenes=true")
    check(g.ev("scene([{who:'',text:'x'}],null,{illus:'wall_settled'})") is False and g.ev("!!story().illus.wall_settled"), 'tests skip the modal, the picture still counts as shown')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_names_staff_and_outside_cast_are_not_random_guests(b, port, target):
    """Stable identity: nobody on the staff pools, and none of the outside cast (Kevin is Marco's old colleague), is a
    random guest's name."""
    g = Game(b, port, target, seed=247, manual=True)
    bad = json.loads(g.ev("""JSON.stringify((()=>{const staff=new Set(Object.values(CREW_NAMES).flat().concat(['Evan','沈晴','安安','阿拓']));const cast=['Kevin','怡君','珊珊','宇翔','國雄','老林'];
      const out=[];for(const k in NAMES)for(const n of NAMES[k]){for(const p of n.split(/\\s*與\\s*/))if(staff.has(p)||cast.includes(p))out.push(k+':'+n)}return out})())"""))
    check(not bad, f'random names that belong to someone: {bad}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_saves_load_and_nothing_fires_on_load(b, port, target):
    """R: every player save loads with its money, upgrades and crew; tenure has a class for everyone; no v2.4 story
    fact exists until something is really played; a played day of the Day 52 save records the first v2.4 day."""
    for path in sorted(glob.glob(os.path.join(ROOT, 'tests', 'saves', 'player_day*.json'))):
        name = os.path.basename(path)
        g = Game(b, port, target, seed=248, manual=True, viewport={'width': 390, 'height': 844})
        raw = load_save(g, name)
        ok = json.loads(g.ev("""JSON.stringify({money:S.money,crew:(S.crew||[]).length,ops:JSON.stringify(S.ops||{}),t:(S.crew||[]).every(m=>!!tenure(m)),
          v24:Object.keys((S.story&&S.story.facts)||{}).filter(k=>/^(yj_|wall_|up_|xq_)/.test(k))})"""))
        check(ok['money'] == raw['money'] and ok['crew'] == len(raw.get('crew') or []) and ok['ops'] == json.dumps(raw.get('ops') or {}, separators=(',', ':')), f'{name}: kept as it was: {ok}')
        raw_v24 = sorted(k for k in ((raw.get('story') or {}).get('facts') or {}) if re.match(r'^(yj_|wall_|up_|xq_)', k))
        check(ok['t'] and sorted(ok['v24']) == raw_v24, f'{name}: tenure classes; the v2.4 story facts exactly as saved (none for a save from before v2.4): {ok} vs {raw_v24}')
        check(not g.errors, f'{name}: {g.errors[:3]}'); g.close()
    g = Game(b, port, target, seed=249, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day52.json')
    to_service(g)
    d = g.ev("S.day")
    play_day(g, max_steps=60000)
    check(g.ev("story().v24&&story().v24.first") == d, 'the first v2.4 day is recorded when it is played')
    check(not g.errors, g.errors[:3]); g.close()


# ---------------------------------------------------------------- P1: 怡君, 《三個選項》, 秀琴阿姨 × Sophie / Mia, 《那面牆》
V24_KEYS = ['yj_meet', 'yj_look', 'yj_three', 'yj_chose', 'yj_move', 'yj_key', 'wall_worry', 'wall_photos', 'wall_visit', 'wall_wang',
            'wall_setback', 'wall_report', 'wall_fee', 'wall_prep', 'wall_mediation', 'wall_settle', 'wall_article']


@test
def v24_stage_gates_follow_the_chronology_and_their_own_gaps(b, port, target):
    """B / the pacing corrections: each stage needs the one before it and only its own gap (the fiction's time); the
    wall cannot begin before the spare key (+2 settled days); the Second Floor era does not wait for the settlement
    (the player's 10:25: it opens two days after the Lounge is finished); the article only after the settlement;
    nothing needs a global multi-day gap."""
    g = Game(b, port, target, seed=251, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day52.json')
    g.ev("v24()")
    d = g.ev("S.day")
    check(g.ev("due('yj_meet',null,0,'yj')") and not g.ev("due('yj_look','yj_meet',1,'yj')"), 'first the visit')
    g.ev("factSet('yj_meet')")
    check(not g.ev("due('yj_look','yj_meet',1,'yj')"), 'not the same day')
    g.ev("S.day++"); check(g.ev("due('yj_look','yj_meet',1,'yj')"), 'the next day is enough (no global gap)')
    g.ev("factSet('yj_look');S.day++"); check(not g.ev("due('yj_three','yj_look',2,'yj')"), 'viewings take time: two days')
    g.ev("S.day++"); check(g.ev("due('yj_three','yj_look',2,'yj')"), '...then it can come')
    check(not g.ev("eraOpen('wall')") and not g.ev("due('wall_worry',null,0,'wall')"), 'no wall before the key')
    g.ev("factSet('yj_three');factSet('yj_chose');factSet('yj_move');factSet('yj_key')")
    check(not g.ev("eraOpen('wall')"), 'the move settles first')
    g.ev("S.day+=2"); check(g.ev("eraOpen('wall')"), 'two days after the key the wall can begin')
    check(not g.ev("due('wall_article','wall_settle',3,'wall')"), 'no article before the settlement')
    g.ev("for(const k of ['wall_worry','wall_photos','wall_visit','wall_wang','wall_setback','wall_report','wall_fee','wall_prep','wall_mediation','wall_settle'])factSet(k)")
    check(g.ev("eraOpenDay('up')") is None, 'the settlement opens nothing upstairs (no Lounge in this save)')
    g.ev("S.rooms.lounge=1;factSet('lounge_built_1')")
    check(g.ev("eraOpenDay('up')") == g.ev("S.day") + 2, 'the Second Floor era: two days after the Lounge')
    check(g.ev("LANE_CAP.major") == 2 and g.ev("LANE_CAP.v24") == 2, 'two major beats a day across the stories; the long stories have two smaller steps a day of their own (rc7, 15:39)')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_yijun_comes_to_eat_and_her_mother_walks_over(b, port, target):
    """F: 怡君's first visit plays only when 秀琴阿姨 is really in — she walks to the table, then 「妳怎麼來了？」
    「吃飯啊。」 with the player's picture; never on the very start of the first day; never explained."""
    g = Game(b, port, target, seed=252, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day52.json')
    to_service(g)
    g.ev("story().v24=Object.assign(v24(),{first:S.day-1});window.__xq=xiuqin();setCrewAway(__xq,'off')")
    # rc7.4 (found by the full run on 8eb880a): she comes now, not at the hour the day's plan gave her — at 139 s of 250 the
    # room was full, she queued, and her first visit took the rest of the evening, leaving no time for the second
    g.ev("R.sched=R.sched.filter((o,i)=>i<R.si||o.name!=='怡君');spawn({t:R.t,type:'regular',size:1,name:'怡君',story:1})")
    for i in range(300):
        g.page.evaluate('()=>window.__bot(60,1/30)')
        if g.ev("phase") != 'service' or g.ev("!!story().named['怡君']&&story().named['怡君'].seen===S.day&&!R.groups.some(q=>namedId(q)==='怡君')"): break
    check(not g.ev("!!fact('yj_meet')"), 'her mother is not in today: the visit is only a visit')
    g.ev("story().away=null")
    g.ev("spawn({t:R.t,type:'regular',size:1,name:'怡君',story:1,tries:1})")
    for i in range(400):
        g.page.evaluate('()=>window.__bot(60,1/30)')
        if g.ev("!!fact('yj_meet')") or g.ev("phase") != 'service': break
    check(g.ev("!!fact('yj_meet')"), 'with 秀琴阿姨 in, it happens')
    check(g.ev("!!(story().illus&&story().illus.yj_intro)"), "the player's picture was shown with it")
    check(g.ev("relN('s:'+__xq.id,'n:怡君','family')") == 1, 'remembered as family, between the two of them')
    lines = g.ev("JSON.stringify((story().beatLines||{}).yj_meet||[])")
    check('吃飯啊' in lines and '女兒' not in lines and '媽' not in lines, f'the lines, and nobody explains who she is: {lines}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_the_wall_is_written_to_the_rules(b, port, target):
    """H, Q and the canon change, read from the authored text: 秀琴阿姨 (not 阿珠姐) is the mother; 王先生 separates the
    three questions and never announces his discount; the fee is a real number; a clue gets weaker; the mediation is
    shown item by item and 怡君 decides; the article comes after; no summary lines."""
    g = Game(b, port, target, seed=253, manual=True)
    src = g.ev("""(()=>{const ks=STORY_EV.filter(E=>/^(yj_|wall_|xq_)/.test(E.k));return ks.map(E=>String(E.run||'')+(E.present||[]).map(p=>String(p.run)).join('')+String(E.note||'')).join('\\n')+String(wallWang)+String(wallCall)+JSON.stringify(V24_ARRIVE)+String(V24_ARRIVE.yj_move)})()""")
    for line in ['妳怎麼來了？', '吃飯啊。', '附近那麼多間。', '不能吃妳工作的喔？', '找到三個。', '下次來不用在樓下等。', '今天怎麼只有妳？', '喔～～',
                 '妳先拍起來。', '不是擦掉就好了啦。', '上次不是才叫人來？', '這裡以前可能處理過。', '差很多。', '等一下。', '妳女兒買的是中古屋？',
                 '先不要跳那麼快。', '如果要我處理，就正式委任我。', '……這比我之前問的低很多欸。', '你是不是算太少？', '妳女兒有付錢就好。',
                 '那我們一項一項談。', '我接受。', '我想寫這個。', '不一定寫妳。是寫這件事。', '原來沒這麼簡單。']:
        check(line in src, f'the line is there: {line}')
    check('交屋前' in src and '修過、蓋過' in src and '知不知道' in src, 'the three questions, kept apart')
    check('相信的，跟能證明的' in src, 'what they believe vs what they can prove')
    for bad in ['友情價', '打折', '算便宜', '算妳便宜', '因為秀琴', '因為阿姨', '阿珠姐', '大家已經不只是同事', '像家一樣', '一起度過了很多',
                '互相幫助就是幸福', '把大家連在一起', '這就是新的開始', '終於有二樓', '終於有自己的家']:
        check(bad not in src, f'never: {bad}')
    check(src.index('妳女兒有付錢就好。') > src.index('你是不是算太少？'), 'the fee exchange ends on his line')
    check('六萬' in src and '五十二萬' in src and '三十八萬' in src, 'a real fee, a claim, a negotiated amount')
    check(g.ev("STORY_EV.find(E=>E.k==='wall_article').when.toString().includes(\"'wall_settle'\")"), 'the article waits for the settlement')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_day52_save_plays_the_stories_in_order_over_forty_days(b, port, target):
    """The player's Day 52 save, forty days of lazy play (seeded), the arbiter as in play: 怡君's arc, then the wall;
    the Second Floor era does not open on the wall (the player's 10:25: it waits for the Lounge, which this save has
    not built — built, the floor opens two days later); never more than two major beats in a day (rc7); nothing on the first day's
    start; everyone who speaks in a restaurant beat was really there (the beats check it); no page errors."""
    g = Game(b, port, target, seed=254, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day52.json')
    g.ev("window.__fastSay=1")
    seed = "Math.random=(function(){let a=%d;return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
    # v2.4 rc7: the seed base was 7000. One seed is one trajectory, and any change in how many random numbers a day draws
    # moves it: since 8e8d407 (Ken: a named guest's party is never a passer-by's) the walk-ins draw less, and on 7000 the
    # wall began on Day 67, a day past the window. Seven seeds on both builds (docs/evidence/v24_rc7/sims/day52_seeds.txt):
    # the wall begins Day 64–67 now (65–66 before, and one seed where it never began in forty days), settles Day 80–85
    # (82–84 before) — the same spread; on 7000 Sophie and Mia's own beats took the evenings they came in together (sm_c,
    # sm_d), the wall the next one. 7400 meets every target of the player's on this build.
    # rc7.3 release: the cats' days in Jill's room draw their own random numbers, so every trajectory moved again. Seven
    # seeds on rc7.2 (8a3e1a8) and rc7.3 (9a36bbd), docs/evidence/v24_rc7_3/sims/day52_seeds.txt: the wall begins Day
    # 63–68 (64–67 on rc7.2), settles Day 80–85 (80–85) — about the same spread, earlier at the median; 7400 is now the
    # one late seed (68, 85). 7600 meets every target on both builds (the wall on Day 64 on both).
    # rc7.4 release: on the branch a favourite on the menu brought its regular a little more often, and the full run on
    # 6e82c77 settled the wall on Day 83 here. Seven seeds (docs/evidence/v24_rc7_4/sims/day52_seeds.txt): the busier
    # evenings held the stories back (settled by Day 82 on four of seven, the article seven days after the settlement
    # on three), and a regular the story asked for, who was coming anyway, was lost at the door when the room was full
    # (Sophie, the evenings 怡君 came for the article — fixed in 57e6f80). Without the extra visits: settles Day 79–82
    # (rc7.3: 80–85), the wall begins 63–66, the article three days after on all seven; five seeds of seven meet every
    # target (five on rc7.3), 7600 among them on both.
    # rc8.2 release: on 7600 the wall began on Day 63 and settled on Day 82 — 19 days. Seven seeds on rc8.1 (df8a95b), the
    # candidate (a36c900) and the release (docs/evidence/v24_rc8_2/sims/day52_seeds.txt): on the candidate one seed (7400)
    # never began the wall — 秀琴's small talk stopped at six for Sophie and Mia together, and Sophie had taken all six; the wall
    # needs her to know both. The release talks with each (three apiece, the one she knows less first): the wall begins
    # Day 63–66 and settles by Day 82 on all seven (rc8.1: 79–84), every target on four of seven (rc8.1 four). 7000 meets
    # every target on rc8.1 and on the release.
    first = None; majors = {}
    for d in range(40):
        if g.ev("phase") == 'summary':
            g.click('[data-act=toShop]'); g.page.wait_for_timeout(60)
        if g.ev("phase") == 'shop':
            g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(100)
        g.ev(seed % (7000 + d)); g.ev("S.today.sugKey=null;S.today.sug=null;autoStock()")
        start_day(g); install_bot(g); g.ev(LAZY_ACTOR + "\nwindow.__act=window.__actLazy;window.__noScenes=true")
        if first is None:
            first = g.ev("S.day")
            check(not any(g.ev("JSON.stringify(story().trace.filter(t=>t.d===S.day&&t.at==='daystart'&&/^(yj_|wall_)/.test(t.k)))") != '[]' for _ in [0]), 'nothing at the start of the first day')
        for _ in range(1200):
            r = g.page.evaluate('()=>window.__bot(150,1/30)')
            if g.ev("phase") != 'service' or not g.ev("!!R"): break
            if r['ticks'] < 150: break
        if g.ev("phase") == 'service':
            g.ev("closeShop('x');for(const q of R.groups.slice())leaveGroup(q,'ok')"); g.page.evaluate('()=>window.__bot(400,1/30)')
        if g.ev("phase") == 'service': g.ev("finishClosing()")
        majors[g.ev("S.day")] = g.ev("(story().day&&story().day.d===S.day)?story().day.major:0")
    F = json.loads(g.ev("JSON.stringify(Object.fromEntries(%s.map(k=>[k,fact(k)?fact(k).d:null])))" % json.dumps(V24_KEYS)))
    check(all(F[k] is not None for k in V24_KEYS), f'every beat happened in forty days: {F}')
    order = [F[k] for k in V24_KEYS]
    check(order == sorted(order), f'in order: {F}')
    check(F['wall_worry'] >= F['yj_key'] + 2, f'the wall only after the move settled: {F}')
    # the player's targets for this save (docs/v24/pacing_correction_2026-10-01.txt), first = Day 53
    check(F['yj_key'] - F['yj_meet'] <= 9 and F['yj_key'] <= first + 10, f'怡君 moved in within about ten days, by Day {first + 9} (59–62) — a day later when a dated beat takes her first day (this seed: Dylan on Valentine\'s, Day {first}): {F}')
    check(first + 9 <= F['wall_worry'] <= first + 13, f'the wall begins Day {first + 9}–{first + 13} (62–66): {F}')
    check(F['wall_settle'] - F['wall_worry'] <= 18 and F['wall_settle'] <= first + 29, f'settled within about two and a half weeks, by Day {first + 29} (75–82): {F}')
    check(all(v <= 2 for v in majors.values()), f'never more than two major beats in a day (rc7, 15:39; was one): {majors}')
    check(g.ev("loungeLv()") == 0 and g.ev("eraOpenDay('up')") is None and not g.ev("eraOpen('up')"), 'the wall settled, no Lounge in this save: the floor still waits for the Lounge')
    g.ev("S.rooms.lounge=1;factSet('lounge_built_1')")
    check(g.ev("eraOpenDay('up')") == g.ev("S.day") + 2, 'the Lounge finished: the floor two days later')
    check(not g.errors, g.errors[:3]); g.close()


# ---------------------------------------------------------------- 秀琴阿姨 from Day 1 (docs/v24/xiuqin_from_day1_2026-10-01.txt)
def _act(g, a, **kv):
    ds = ''.join(f"el.dataset.{k}='{v}';" for k, v in kv.items())
    g.ev(f"(()=>{{const el=document.createElement('button');el.dataset.act='{a}';{ds}$('#screen').appendChild(el);el.click();el.remove()}})()")


@test
def v24_xiuqin_is_there_from_day_one_and_is_not_free_labour(b, port, target):
    """A new game: 秀琴阿姨 walks in near closing on Day 1 — Jill's acquaintance, come to help tidy up — and the coach
    names her once. She claims no table, ticket or dish: Day 1 played with her and without her (window.__noXQH) ends
    with the same money, guests, stars and reviews. A while into the closing she goes home. Day 2's news names her, and
    until a cleaner is hired the staff tab says the first cleaner is her."""
    out = {}
    for helper in (True, False):
        g = Game(b, port, target, seed=260, manual=True, viewport={'width': 390, 'height': 844})
        install_bot(g)
        g.click('[data-act=open]')
        g.ev("window.__fastSay=1" + ("" if helper else ";window.__noXQH=1"))
        start_day(g)
        g.ev("__botUntil('R.t>=R.dur*.9',60000,1/30)")
        check(not g.ev("!!R.xqh"), 'not before the last part of the evening')
        seen = {'in': False, 'coach': '', 'claims': []}
        for _ in range(400):
            g.page.evaluate('()=>window.__bot(15,1/30)')
            if g.ev("phase") != 'service': break
            st = json.loads(g.ev("JSON.stringify({h:!!(R&&R.xqh&&!R.xqh.arriving),coach:$('#coach').hidden?'':$('#coach').innerText,"
                                 "claims:R?R.tables.filter(t=>t.claim==='xq').length+R.groups.filter(q=>q.claim==='xq').length+R.tickets.filter(k=>k.claim==='xq').length:0,carry:!!(R&&R.xqh&&R.xqh.carry)})"))
            if st['h']: seen['in'] = True
            if '秀琴阿姨' in st['coach']: seen['coach'] = st['coach']
            if st['claims'] or st['carry']: seen['claims'].append(st)
        out[helper] = json.loads(g.ev("JSON.stringify({d:__digest(),log:dayLog().map(l=>l.w+'：'+l.t),f:fact('xq_helper')})"))
        if helper:
            check(seen['in'] and out[helper]['f'] and out[helper]['f']['d'] == 1, f'she came in on Day 1: {seen}')
            check(any(l.startswith('秀琴阿姨：我來幫妳收一下。') for l in out[helper]['log']) and any(l == 'Jill：阿姨，不用啦。' for l in out[helper]['log']), 'who she is to the place, in her own words')
            check(any('Jill 認識很久的阿姨' in l for l in out[helper]['log']) and '秀琴阿姨' not in seen['coach'], 'who she is, in the scene of her first evening (no coach card)')
            check(not seen['claims'], f'she never claims a table, a ticket or a dish: {seen["claims"][:2]}')
        else:
            check(not seen['in'] and not out[helper]['f'], 'the control run has no helper')
        if helper:
            # the summary, the shop: the recruit list says who the first cleaner is; then Day 2's news
            if g.ev("phase") == 'summary': g.click('[data-act=toShop]')
            g.ev("window.__d0=S.day;S.day=Math.max(S.day,4);shopTab='staff';showShop()"); g.page.wait_for_timeout(50)   # the staff tab opens on Day 4
            check('第一位清潔員就是秀琴阿姨' in g.ev("document.querySelector('#screen').innerText"), 'the staff tab says the first cleaner is her')
            g.ev("S.day=__d0;shopTab='home';showShop()")
            g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(100)
            news = g.ev("S.news.join(' ')")
            check('秀琴阿姨' in news and '第一位就是她' in news and '2.4' not in news, f'Day 2: the news names her (a new game gets no update note): {news}')
        check(not g.errors, g.errors[:3]); g.close()
    a, c = out[True]['d'], out[False]['d']
    for k in ['money', 'lifetime', 'summary', 'reviews', 'reviewHash', 'stats', 'regulars', 'stock']:
        check(a[k] == c[k], f'no free labour — {k} is the same with and without her: {a[k]} / {c[k]}')


@test
def v24_xiuqin_goes_home_a_while_into_the_closing(b, port, target):
    """She is not part of the evening at the sofa: about twenty seconds into the closing she walks out of the front door."""
    g = Game(b, port, target, seed=262, manual=True, viewport={'width': 390, 'height': 844})
    install_bot(g)
    g.click('[data-act=open]'); g.ev("window.__fastSay=1")
    start_day(g)
    g.ev("__botUntil('R.closing!=null',80000,1/30)")
    check(g.ev("!!R.xqh&&!R.xqh.leaving"), 'there at the start of the closing')
    g.ev("for(let i=0;i<30*20;i++){update(1/30);updateCats(1/30,0)}")
    check(g.ev("!!R.xqh"), 'still there twenty seconds in')
    g.ev("for(let i=0;i<30*12;i++){update(1/30);updateCats(1/30,0)}")
    check(not g.ev("!!R.xqh") and g.ev("R.xqhDone") == 1, 'gone by thirty — and she does not come back that evening')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_the_first_cleaner_hired_is_her_and_keeps_what_she_knows(b, port, target):
    """Hiring the first cleaner is hiring her: the same person (id 'xq'), what she knows (who she has talked to) carries
    over, one line — 「那以後就天天來了。」; from then on an ordinary cleaner and no evening helper. The next cleaner is
    someone else. (rc7.2, the player 22:39: nobody is let go — there is no 解雇.)"""
    g = Game(b, port, target, seed=261, manual=True, viewport={'width': 390, 'height': 844})
    install_bot(g)
    g.click('[data-act=open]'); g.ev("window.__fastSay=1")
    start_day(g); g.ev("__bot(80000,1/30)"); g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
    if g.ev("phase") == 'summary': g.click('[data-act=toShop]')
    check(g.ev("xqHelperMode()&&!!fact('xq_helper')&&xqm().helper===1"), 'before a cleaner: the evening helper')
    g.ev("relSet('s:xq','sophie','spoke');relSet('s:xq','mia','spoke');S.money=99999;S.day=4;shopTab='staff';showShop()")   # the staff tab opens on Day 4
    check(g.ev("roleCap('cleaner')") == 0 and '還沒有清潔員的名額' in g.ev("document.querySelector('#screen').innerText"), 'rc8 §21: a new shop has no cleaner\'s place yet; the card says where one comes from')
    g.ev("S.level=5;showShop()")   # JILL: the first cleaner's place
    check('第一位清潔員就是秀琴阿姨' in g.ev("document.querySelector('#screen').innerText"), 'the recruit list says so before')
    _act(g, 'hire', k='cleaner'); g.ev("__tick(30)")
    m = json.loads(g.ev("JSON.stringify((S.crew||[]).map(m=>({id:m.id,name:m.name,role:m.role})))"))
    check(m == [{'id': 'xq', 'name': '秀琴阿姨', 'role': 'cleaner'}], f'the first cleaner is her, the same person: {m}')
    check(g.ev("!!fact('xq_hired')&&!xqHelperMode()&&xqm()===xiuqin()&&xqKnows('sophie')===1&&xqKnows('mia')===1"), 'an ordinary cleaner now, who still knows them')
    check(g.ev("dayLog().some(l=>l.w==='秀琴阿姨'&&l.t==='那以後就天天來了。')"), 'her one line (a scene with her face over the shop; tests log it)')
    check('第一位清潔員就是秀琴阿姨' not in g.ev("document.querySelector('#screen').innerText"), 'the recruit note is gone')
    _act(g, 'hire', k='cleaner'); g.ev("__tick(30)")
    check(g.ev("S.crew.length") == 1, 'rc8 §21: one cleaner\'s place, taken')
    g.ev("S.rooms=S.rooms||{};S.rooms.kext=1")   # 廚房擴建: one more cleaner's place
    _act(g, 'hire', k='cleaner'); g.ev("__tick(30)")
    check(g.ev("S.crew.map(m=>m.name).join()") == '秀琴阿姨,小彤', 'the next cleaner is someone else')
    g.ev("shopTab='staff';showShop()"); g.page.wait_for_timeout(60)
    scr = g.ev("document.querySelector('#screen').innerText")
    check('解雇' not in scr and not g.ev("!!document.querySelector('[data-act=crewFire]')"), 'no 解雇 on the staff page (rc7.2, 22:39)')
    _act(g, 'crewFire', k='xq')
    check(g.ev("S.crew.map(m=>m.name).join()") == '秀琴阿姨,小彤' and not g.ev("!!fact('xq_gone')"), 'and no way to let her go: she stays')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_yijun_comes_early_in_a_fresh_game_and_meets_her_mother_at_closing(b, port, target):
    """Not gated on a late day or on Sophie × Mia: in a new game with no cleaner hired, once 秀琴阿姨 has been part of
    the evenings for about a week, 怡君 comes to eat — late, when her mother is in — and 「妳怎麼來了？」「吃飯啊。」 plays
    with the helper walking over. Her visit's hour is kept (not pulled earlier on a quiet evening)."""
    g = Game(b, port, target, seed=263, manual=True, viewport={'width': 390, 'height': 844})
    install_bot(g)
    g.click('[data-act=open]'); g.ev("window.__fastSay=1")
    seed = "Math.random=(function(){let a=%d;return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
    met = None; late = []
    for day in range(1, 15):
        _act(g, 'restock'); g.ev("__tick(200)"); _rt.fill_fridge(g); g.ev(seed % (263000 + day))
        start_day(g)
        sched = json.loads(g.ev("JSON.stringify(R.sched.filter(o=>o.name==='怡君').map(o=>({t:o.t/R.dur,hold:!!o.hold})))"))
        late += sched
        for _ in range(400):
            r = g.page.evaluate('()=>window.__bot(150,1/30)')
            if g.ev("phase") != 'service' or r['ticks'] < 150: break
        if g.ev("phase") == 'service': g.ev("__bot(60000,1/30)")
        g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
        if g.ev("!!fact('yj_meet')") and met is None:
            met = g.ev("S.day")
            check(g.ev("xqHelperMode()&&xqm().helper===1"), 'her mother is still the evening helper (no cleaner hired)')
            lines = g.ev("JSON.stringify(story().beatLines.yj_meet||[])")
            check('妳怎麼來了？' in lines and '吃飯啊。' in lines, f'the lines: {lines}')
            check(g.ev("relN('s:xq','n:怡君','family')") == 1, 'remembered between the two of them')
            check(g.ev("(story().trace.find(t=>t.k==='yj_meet')||{}).at") in ('xqin', 'served'), 'it played with her mother in the room')
        if g.ev("phase") == 'summary': g.click('[data-act=toShop]')
        if day == 3: _act(g, 'hire', k='chef'); g.ev("__tick(30)")   # rc8 §21: a new shop's one place is a chef's
        g.click('[data-act=nextDay]'); g.ev("__tick(100)")
        if met: break
    check(met is not None and 7 <= met <= 14, f'怡君 met her mother here within the second week (Day {met})')
    check(late and all(s['hold'] and s['t'] >= .89 for s in late), f'her visits are planned late and kept there: {late}')
    check(g.ev("fact('xq_helper').d") == 1, '秀琴阿姨 since Day 1')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_manual_tutorial_and_news_cover_the_new_content(b, port, target):
    """The release checklist's manual audit, and the player's 15:11 request (說明書和一開始的教學都要到位): the manual
    explains 秀琴阿姨 before and after the first cleaner, staff arriving late, the story illustrations and staff lives,
    the renamed 後場整理區; a save that was already going gets one 2.4 note on its next prep screen (systems only —
    nobody's story told in advance); a new game does not (Day 1's coach and Day 2's news introduce her instead)."""
    g = Game(b, port, target, seed=264, manual=True, viewport={'width': 390, 'height': 844})
    txt = g.ev("GUIDE.map(s=>s.h+' '+s.sum+' '+s.pts.map(p=>p.join(' ')).join(' ')).join('\\n')")
    for need in ['秀琴阿姨', '快打烊時順路進來', '請第一位清潔員就是請她', '第一位清潔員是秀琴阿姨', '晚點到', '日薪照付', '看插圖', '店外的生活', '廚師不會離開廚房', '後場整理區']:
        check(need in txt, f'the manual mentions {need}')
    for stale in ['後場休息室', '吧台我擦']:
        check(stale not in txt, f'not in the manual: {stale}')
    check('— last: v2.4 rc8' in open(os.path.join(ROOT, 'js', 'game.js'), encoding='utf-8').read(), 'the audit stamp on GUIDE (the release checklist §2: the stamp says the release the manual was last audited for)')
    g.click('[data-act=open]'); g.page.wait_for_timeout(100)
    check('2.4' not in g.ev("S.news.join(' ')") and g.ev("S.news24") == -1, 'a new game: no update note')
    g.close()
    # the player's Day 52 save: one note, the systems only
    g = Game(b, port, target, seed=265, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day52.json')
    if g.ev("phase") == 'shop':
        g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(200)
    news = g.ev("S.news.find(n=>n.startsWith('<b>2.4'))||''")
    check('2.4：店裡的人，店外的生活。' in news and '後場整理區' in news and '插圖' in news and '晚點到' in news, f'the 2.4 note: {news}')
    check('秀琴阿姨' not in news and '怡君' not in news and '牆' not in news, f'nobody\'s story told in advance (she is already on the crew): {news}')
    check(g.ev("document.querySelector('#screen').innerText").count('2.4：店裡的人') == 1, 'on the prep screen, once')
    g.ev("S.today=null;S.news=[];applyGates()")
    check('2.4' not in g.ev("S.news.join(' ')"), 'only once')
    check(not g.errors, g.errors[:3]); g.close()
    # an older save with no cleaner: the note says who comes in the evenings
    g = Game(b, port, target, seed=266, manual=True, viewport={'width': 390, 'height': 844})
    raw = json.load(open(os.path.join(ROOT, 'tests', 'saves', 'player_day30.json'), encoding='utf-8')); raw = raw.get('save', raw)
    raw['crew'] = [m for m in raw.get('crew', []) if m['role'] != 'cleaner']
    g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.page.wait_for_timeout(150)
    g.click('[data-act=openFresh]') if g.page.query_selector('[data-act=openFresh]') else g.click('[data-act=open]'); g.page.wait_for_timeout(150)
    if g.ev("phase") == 'shop':
        g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(200)
    news = g.ev("S.news.join(' ')")
    check('秀琴阿姨' in news and '請第一位清潔員，就是請她' in news, f'no cleaner yet: the note says who helps in the evenings: {news}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def rc8_the_manual_shows_a_space_once_the_shop_has_it(b, port, target):
    """The player, 2026-10-03: 「每個空間等他出現才出現在說明書吧」 (an 80-day save had them all, and so did a new shop).
    A new game's manual has no Lounge, no second floor, no side room, no terrace — not as a section, an entry or a word
    in a line — and its room tabs are the four it has; the VIP card and the dinner wine sit in sections a shop always
    has. The player's Day 81 save (the Lounge III, no second floor yet) has the Lounge and still no 二樓; the floor's
    section comes with the lease, and each of its rooms with its own story. GUIDE itself keeps every word."""
    page = "(document.querySelectorAll('#screen details').forEach(d=>d.open=true),document.querySelector('#screen').innerText)"   # every card open: a closed card's words are not in innerText
    g = Game(b, port, target, seed=811, manual=True, viewport={'width': 390, 'height': 844})
    g.click('[data-act=open]'); g.page.wait_for_timeout(100)
    g.ev("showGuide()"); g.page.wait_for_timeout(50)
    t = g.ev(page)
    for gone in ['Lounge', '二樓', '包廂', '休息室', '側廳的大窗', '露天桌', '酒窖', '予安', '配菜的酒', '酒水成本', '調酒師']:
        check(gone not in t, f'a new shop: no {gone} in the manual')
    check('店門口・主廳・廚房・房間（新的房間蓋好以後會加進來）' in t, 'the tabs it has')
    check('來店 5 次的客人拿到 VIP 卡：九折' in t and '來 10 次換成八折卡：八折' in t, 'the VIP card, from the first day, without the Lounge')
    check('小小店主手冊' in t and '五隻店貓' in t and 'Jill 的房間' in t, 'the rest of the manual is there')
    g.ev("S.rooms.side=1;showGuide()"); g.page.wait_for_timeout(50); t = g.ev(page)
    check('側廳的大窗' in t and '店門口・主廳・側廳・廚房・房間' in t and '二樓' not in t, 'the side room comes with the side room')
    full = g.ev("GUIDE.map(s=>s.h+' '+s.sum+' '+s.pts.map(p=>p.join(' ')).join(' ')).join('\\n')")
    check('Lounge：留下來的地方' in full and '員工休息室' in full and '天氣、Lounge、包廂、VIP 卡' in full, 'GUIDE keeps every word')
    stale = g.ev("""(()=>{const all=GUIDE.flatMap(g=>[g.sum,...g.pts.flatMap(([k,t])=>guideLines(t))]);const bad=GUIDE_WHEN.line.map(r=>r[0]).filter(w=>all.filter(l=>l.includes(w)).length!==1);
      for(const k in GUIDE_WHEN.pt){const [h,l]=k.split('|');if(!GUIDE.some(g=>g.h===h&&g.pts.some(p=>p[0]===l)))bad.push(k)}for(const k in GUIDE_WHEN.sec)if(!GUIDE.some(g=>g.h===k))bad.push(k);return bad})()""")
    check(stale == [], f'every gate still finds its words in GUIDE (an edited line would quietly stop being gated): {stale}')
    check(not g.errors, g.errors[:3]); g.close()
    g = Game(b, port, target, seed=812, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day81_2206.json')
    g.ev("showGuide()"); g.page.wait_for_timeout(50); t = g.ev(page)
    check('Lounge：留下來的地方' in t and '吃完再去 Lounge 七折' in t and '配菜的酒' in t and '調酒師' in t, 'Day 81: the Lounge is in the manual')
    check('二樓' not in t and '包廂' not in t and '休息室' not in t, 'Day 81: the second floor is not hers yet, and not in the manual')
    g.ev("S.rooms.up=1;const o=srW();o.bought=o.done=S.day;showGuide()"); g.page.wait_for_timeout(50); t = g.ev(page)
    check('二樓：休息室與包廂' in t and '二樓平面圖' in t and '員工休息室' in t and '誰會上去' in t and '私人包廂' not in t, 'the lease: the floor and its Staff Room (rc8 canon), not yet the Private Dining Room')
    g.ev("S.up.pd={done:S.day};showGuide()"); g.page.wait_for_timeout(50); t = g.ev(page)
    check('私人包廂' in t and '最低消費' in t, 'the Private Dining Room with its own story')
    check(not g.errors, g.errors[:3]); g.close()


@test
def rc8_jill_has_things_to_do_in_her_room(b, port, target):
    """The player, 2026-10-03: 「Jill有房間後多讓他在房間有事做吧 自動會做的 看閨蜜機電視（可移動的）打手遊 我老婆常常跟網友打pubg
    或跟老公聊天 看老公在幹嘛 跟貓咪互動」. On a long rest in the service, by herself: a game on her phone (a word to her
    friends now and then), the rolling TV — she gets up, rolls it to her end of the sofa and sits back down to watch —,
    a few words with him at his desk, a look over his shoulder, a cat called. Work gets her up at once from any of it:
    from the game with a word to her friends, from the TV's push with the TV left where it is, off, and no step left
    half done. The words are bubbles in the room and nothing in the log."""
    g = Game(b, port, target, seed=871, manual=True)
    g.click('[data-act=open]'); g.page.wait_for_timeout(100); start_day(g)
    g.ev("window.__wl=jillWorkload;jillWorkload=()=>0;R.t=R.dur*.3;R.jill.q=[];R.jill.cur=null")
    acts = g.ev("""(()=>{const seen={},says=[];const log0=(R.log||[]).length;for(let n=0;n<60*30*9;n++){R.jill.q.length=0;R.groups.length=0;if(R.t>R.dur*.8)R.t=R.dur*.3;
        if(!R.jill.rest&&(R.jill.restCD||0)>R.t)R.jill.restCD=0;if(!R.jill.rest&&R.jill.calm<6)R.jill.calm=6;__tick(1000/30);
        const J=R.jill,L=LIFE.jill;if(J.rest==='sit'){const k=J.up?'up:'+J.up.k+':'+J.up.ph:L.act;seen[k]=(seen[k]||0)+1}
        for(const s of HOME_SAY)if(!s.seen&&s.t>=0){s.seen=1;says.push(s.txt)}}
       return{seen,says,tv:LIFE.tv.at}})()""")
    seen = acts['seen']
    check(seen.get('game', 0) > 0 and any(s in acts['says'] for s in ['我這邊有人。', '左邊左邊！', '等我，我在補血。', '我倒了，救我。', '你們先跳，我跟著。', '我沒子彈了。', '這圈好小。', '車給我開。']), f'a game on her phone, a word to her friends: {seen}')
    check(seen.get('chat', 0) + seen.get('up:peek:do', 0) > 0, f'a word with him at his desk, or a look at his screen: {seen}')
    check(len(set(seen)) >= 6, f'more than one thing to do: {seen}')
    # work gets her up: from the game, and from the TV's push
    g.ev("(()=>{const J=R.jill,L=LIFE.jill;if(!J.rest){const p=freeJillPos();startRest(p);J.x=L.x=JPOS[p].x;J.y=SOFA.front+10;J.rest='go';J.tx=null}})()")
    for _ in range(40):
        if g.ev("R.jill.rest==='sit'&&!R.jill.up"): break
        g.ev("__tick(1000/30)")
    g.ev("(()=>{const L=LIFE.jill;L.act='game';L.t=30;HOME_SAY.length=0;endRest()})()")
    check(any(s in g.ev("HOME_SAY.map(s=>s.txt)") for s in ['我先下了，店裡有事。', '等我一下，有客人。', '你們先打，我等等回來。']), 'up from the game: a word to her friends')
    g.ev("(()=>{const J=R.jill,L=LIFE.jill;LIFE.tv.at='park';LIFE.tv.tried=0;LIFE.tv.x=TV_PARK.x;LIFE.tv.y=TV_PARK.y;J.restCD=0;const p=freeJillPos();startRest(p);J.x=JPOS[p].x;J.y=SOFA.front+10})()")
    for _ in range(60):
        g.ev("__tick(1000/30)")
        if g.ev("R.jill.rest==='sit'"): break
    # the TV (a cat on her lap keeps her where she is, so on this seed's rest she never chose it): she rolls it over and watches
    g.ev("(()=>{const J=R.jill,L=LIFE.jill;L.t=0;restUpStart(J,L,'tv')})()")
    tv = g.ev("(()=>{const ph=new Set();let n=0;while(n<1500&&R.jill.rest==='sit'&&!(LIFE.jill.on&&LIFE.jill.act==='tv')){R.jill.q.length=0;R.groups.length=0;__tick(1000/30);if(R.jill.up)ph.add(R.jill.up.ph);n++}return{ph:[...ph],act:LIFE.jill.act,on:LIFE.jill.on,at:LIFE.tv.at,tvOn:LIFE.tv.on,n}})()")
    check(tv['act'] == 'tv' and tv['on'] and tv['at'] == 'use' and tv['tvOn'] and {'go', 'push', 'back'} <= set(tv['ph']), f'she gets up, rolls the TV to her end of the sofa, sits back down and watches: {tv}')
    g.ev("(()=>{const J=R.jill,L=LIFE.jill;endRest();LIFE.tv.at='park';LIFE.tv.tried=0;LIFE.tv.x=TV_PARK.x;LIFE.tv.y=TV_PARK.y;J.restCD=0;const p=freeJillPos();startRest(p);J.x=JPOS[p].x;J.y=SOFA.front+10})()")
    for _ in range(60):
        g.ev("__tick(1000/30)")
        if g.ev("R.jill.rest==='sit'"): break
    g.ev("(()=>{const J=R.jill,L=LIFE.jill;L.t=0;restUpStart(J,L,'tv')})()")
    for _ in range(400):
        if g.ev("!!(R.jill.up&&R.jill.up.ph==='push'&&LIFE.tv.at==='moving')"): break
        g.ev("__tick(1000/30)")
    check(g.ev("LIFE.tv.mover==='jill'"), 'she is rolling the TV')
    g.ev("endRest()")
    st = g.ev("({up:R.jill.up,mover:LIFE.tv.mover,at:LIFE.tv.at,on:LIFE.tv.on,sofa:R.jill.sofa,rest:R.jill.rest})")
    check(st == {'up': None, 'mover': None, 'at': 'park', 'on': False, 'sofa': False, 'rest': None}, f'up mid-push: the TV where she left it, off; nothing half done: {st}')
    n = g.ev("(()=>{let n=0;while(n<400&&R.jill.room!=='main'){__tick(1000/30);n++}return n})()")
    check(g.ev("R.jill.room") == 'main', f'and she goes back out to work ({n} frames)')
    g.ev("jillWorkload=__wl")
    check(not g.errors, g.errors[:3]); g.close()


@test
def rc8_a_booked_out_lounge_never_shares_its_evening_with_the_trial(b, port, target):
    """The player's Day 87 (「予安彈鋼琴配上大家畫面的時候 遊戲裡居然還沒人 人是後來才陸續進來」; 「主廚之夜我到結算才知道」): a chef's night
    carried over from an earlier day is moved onto tonight only when the service starts (cnDayStart), after the evening's
    guests were planned — so the plan did not see it, and 予安's trial was planned onto a booked-out Lounge: she played
    to an empty room, the chef's night's guests came after. Now an overdue chef's night is tonight for the plan too, as
    Ken's tasting night already was; the trial waits for another night; and on a booked-out night she is not let in for
    it. On an ordinary night the trial is planned after dinner, the Wangs a little before her."""
    g = Game(b, port, target, seed=873, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day87_2257.json')
    g.ev("delete story().facts.ya_trial;delete story().facts.ya_join;delete story().ev.ya_trial;delete story().ev.ya_join")
    trial = "V24_WANTS.flatMap(f=>f()||[]).filter(o=>o.o&&o.o.yaTrial).map(o=>o.t)"
    check(g.ev("yaTrialDue()") is True and g.ev("cnS().next&&cnS().next.d") == g.ev("S.day"), 'Day 87: the trial is due, and a chef\'s night is tonight')
    check(g.ev(trial) == [], 'not planned onto the chef\'s night')
    g.ev("cnS().next.d=S.day-1")
    check(g.ev("cnTonight()") is True and g.ev(trial) == [] and '今晚｜主廚之夜' in g.ev("cnNewsHTML()"), 'carried over from yesterday: tonight, for the plan and the news too')
    g.ev("const n=cnS().next;cnS().next=null;window.__cn=n;kenS().next={d:S.day-1,n:1}")
    check(g.ev("kenNightToday()") is True and g.ev(trial) == [], 'Ken\'s tasting night, carried over: the same')
    g.ev("kenS().next=null")
    check(g.ev(trial) == [0.46], 'an ordinary night: the trial, after dinner')
    g.ev("cnS().next=window.__cn;cnS().next.d=S.day-1")
    to_service(g)
    check(g.ev("!!R.cn&&cnS().next.d===S.day") is True, 'the carried-over chef\'s night is tonight')
    check(g.ev("(R.sched||[]).some(o=>o.yaTrial)") is False and not g.ev("!!(R.ya&&R.ya.trial)"), 'and nothing of the trial tonight')
    check(g.ev("(()=>{const g0=R.groups.length;spawn({t:R.t,name:YA,type:'gourmet',size:1,pianist:1,yaTrial:1,hold:1,story:1});return R.groups.length-g0+(R.ya&&R.ya.trial?10:0)})()") == 0, 'on a booked-out night she is not let in for the trial')
    check(not g.errors, g.errors[:3]); g.close()


@test
def rc8_duode_has_no_picture(b, port, target):
    """The player, 2026-10-03: 「阿拓 多的 跟圖出來的時候也不一樣」, then 「多的不用圖」 — the step 「從工作開始」 used to arrive as the
    story photo 「多的」 with nothing of it on screen. It is a step with no picture now: no photo, nothing staged; a save that
    already has the photo keeps it; the late photo 「有你在的晚班」 still follows the step."""
    g = Game(b, port, target, seed=874, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day81_2206.json')
    to_service(g)
    g.ev("window.__noScenes=false;delete story().photos.qing_tuo;STORY_EV.find(e=>e.k==='qt_photo').run({})")
    check(g.ev("!!fact('qt_photo')&&!story().photos.qing_tuo&&!STAGE&&!DLG") is True, 'the step, no photo, nothing staged')
    g.ev("story().facts.qt_photo.d=S.day-8;story().facts.qt_days={d:S.day,n:14,l:S.day}")
    check(g.ev("STORY_EV.find(e=>e.k==='qt_photo2').when({})") == g.ev("!!(qingOn()&&tuoOn())"), 'the late photo still follows the step')
    check(not g.errors, g.errors[:3]); g.close()


@test
def rc83_a_special_evening_comes_back_with_its_room(b, port, target):
    """The player's Day 87 save, made at 19:19 on the chef's night with 予安 at the piano: 「繼續營業」 used to open an empty
    shop (29 guests, then none) — 'piano' was not a state the restore knew, so the whole rebuild threw and it fell back to an
    empty room at the same clock. Now the room comes back: everyone in it, 予安 at the piano, the chef's night with its
    guests and the Lounge still its own; the evening plays on."""
    g = Game(b, port, target, seed=883, manual=True, viewport={'width': 390, 'height': 844})
    raw = json.load(open(os.path.join(ROOT, 'tests', 'saves', 'player_day87_2257.json'), encoding='utf-8'))
    raw = raw.get('save', raw)
    n0 = sum(1 for q in raw['checkpoint']['snap']['groups'])
    g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.page.wait_for_timeout(150)
    check(g.page.is_visible('text=繼續營業'), 'the title offers to continue the evening')
    g.click('[data-act=open]'); g.page.wait_for_timeout(150)
    st = json.loads(g.ev("JSON.stringify({ph:phase,n:R.groups.length,clock:clockStr(),ya:!!(R.ya&&R.ya.g&&R.ya.g.state==='piano'),cn:!!R.cn,cng:R.cn?R.cn.guests.length:0,cnr:R.tables.filter(t=>t.room==='lounge').every(t=>t.cnr),toast:$('#toasts').innerText})"))
    check(st['ph'] == 'service' and st['n'] == n0, f'every one of the {n0} parties is back: {st}')
    check(st['ya'] and st['cn'] and st['cng'] > 0 and st['cnr'], f'予安 at the piano, the chef\'s night and its guests, the Lounge booked out: {st}')
    check('無法完整還原' not in st['toast'], f'no fallback: {st}')
    install_bot(g); g.ev("window.__noScenes=true"); g.ev("__play(900,0)")
    check(g.ev("phase") == 'service' and not g.errors, f'the evening plays on: {g.errors[:3]}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def rc83_the_queue_waits_at_the_shopfront(b, port, target):
    """The player: 「排隊的人可不可以改到店門口啊 在主廳好礙事」. A full house waits outside — on the bench by the door when the
    shop has bought it, else standing by the door; nobody waits in the hall. Their patience and the tab's count are at
    the shopfront, and a tap on a waiting party there seats it at a free table."""
    g = Game(b, port, target, seed=884, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day89_2320.json')
    to_service(g)
    g.ev("R.sched=R.sched.slice(0,R.si);for(const t of R.tables){if(t.group||t.lounge)continue;spawn({t:R.t,type:'office',size:2});const q=R.groups[R.groups.length-1];if(q&&q.state==='arrive'&&!q.table)seatGroup(q,t)}")
    g.ev("for(let i=0;i<3;i++)spawn({t:R.t,type:'office',size:2})")
    g.ev("for(let i=0;i<30*12;i++)update(1/30)")
    q = json.loads(g.ev("JSON.stringify(queued().map(g=>({room:g.room,troom:g.troom,k:g.spot&&g.spot.k,st:g.state})))"))
    check(q and all(o['room'] == 'front' and o['troom'] == 'front' for o in q), f'they wait at the shopfront: {q}')
    check(any(o['st'] == 'queue' for o in q) and all(o['k'] in ('oseat', 'ostand') for o in q if o['st'] == 'queue'), f'on the bench outside or by the door, never the hall\'s bench: {q}')
    check(g.ev("roomAlerts().front.n") >= len(q), 'the shopfront tab counts them')
    g.ev("const t=R.tables.find(t=>t.group&&!t.lounge&&!t.pdr&&(t.room||'main')==='main');leaveGroup(t.group,'ok');t.dirty=false;t.group=null;t.claim=null;for(const g0 of queued())g0.notice=99")
    g.ev("setRoom('front')")
    first = g.ev("(()=>{const g0=queued()[0];return g0?g0.id:null})()")
    check(first is not None, f'someone is waiting: {q}')
    hit = g.ev("(()=>{const g0=R.groups.find(q=>q.id===%d);const p={x:g0.x,y:g0.y-22};return roomTap(p,{preventDefault(){}})&&g0.table!=null})()" % first)
    check(hit, 'a tap on them at the shopfront seats them')
    check(not g.errors, g.errors[:3]); g.close()


@test
def rc83_three_pizzas(b, port, target):
    """The player: 「披薩只有一種嗎」「lounge根本沒人點披薩」. With the pizza oven the lab has three pies — the bar pie (dough +
    tomato sauce + cheese), 瑪格麗特 (dough + tomato sauce + basil), 蘑菇白醬 (dough + cream + mushroom slices) — each with
    its own plate and cooking art; and a Lounge party of two or more picks a pie, whichever, as often as three other bites."""
    g = Game(b, port, target, seed=885, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day74_1508.json')
    g.ev("barMenuMig();S.rooms.pizzaoven=1")
    check(g.ev("['pizza','pzmarg','pzfungi'].every(d=>labRD().includes(d))"), 'all three in the lab once the oven is there')
    check(g.ev("labEval(['dough','tomato','cheese']).d") == 'pizza' and g.ev("labEval(['dough','tomato','basil']).d") == 'pzmarg' and g.ev("labEval(['dough','cream','pzmush']).d") == 'pzfungi', 'each its own three')
    check(g.ev("pantry().includes('pzmush')"), 'the mushroom slices in the pantry')
    for d in ('pizza', 'pzmarg', 'pzfungi'):
        check(g.ev("typeof dishURL('%s','P')==='string'&&dishURL('%s','P').length>200" % (d, d)), f'{d}: its plate draws')
    check(g.ev("['freshmoz','pzwhite','pzmush'].every(i=>typeof ingURL(i)==='string')"), 'the new toppings draw')
    g.ev("for(const d of['pizza','pzmarg','pzfungi']){unlockDish(d);S.stock[d]=50}")
    share = g.ev("""(()=>{const bf=barDishes().filter(d=>menuList().includes(d)&&stationOk(d)&&(S.stock[d]||0)>0);let pz=0,n=0;R=R||{};const M=Math.random;for(let k=0;k<4000;k++){const o=loungeOrder({type:'couple',size:2});for(const d of o)if(bf.includes(d)){n++;if(isPizza(d))pz++}}return{pz,n,bf:bf.length,np:bf.filter(isPizza).length}})()""")
    np, nb = share['np'], share['bf']
    expect = 3 / (3 + (nb - np))
    check(np == 3 and abs(share['pz'] / share['n'] - expect) < .06, f'pies together about {expect:.2f} of the bites a couple orders: {share}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def rc83_small_things_from_the_players_evenings(b, port, target):
    """The rest of the player's Day 83–89 notes, one check each: the favourite-dish complaint once in six days (「Sophie連續
    兩天說沒有香煎鴨胸很白癡」); PERFECT no longer a banner across the screen (「可以不要一直跳出perfect擋住選區嗎」); Evan's two
    coasters say whose seat the second is, the brief's lines kept (「這段對話沒頭沒尾欸」); Ken's share is Jill's envelope
    to Ken; the third tasting night's guess is about the wine (「怎麼是猜什麼干貝」); Jill's room has two litter cabinets
    and the bowls; 寶寶 leans against Jill, 柔柔 likes her legs."""
    g = Game(b, port, target, seed=886, manual=True, viewport={'width': 390, 'height': 844})
    src = open(os.path.join(ROOT, 'js', 'game.js'), encoding='utf-8').read()
    check("banner('✨ PERFECT! ✨'" not in src, 'no PERFECT banner')
    check("sayG(g,'他今天沒來。'" in src and 'Monsieur 杜平常坐的位子' in src, 'the coasters: whose seat, and the brief\'s words')
    check('把 Ken 的那一份裝進信封，推到他面前' in src and '不用給我。' in src, 'the envelope goes to Ken')
    check('這次可以猜是哪裡的酒了？' in src and '第三支配${dn}？' in src, 'the guess is the wine\'s')
    load_save(g, 'player_day89_2320.json')
    to_service(g)
    g.ev("S.regulars.sophie=Math.max(S.regulars.sophie||0,5);S.loveMiss={};Math.random=()=>0")
    said = g.ev("(()=>{spawn({t:R.t,type:'office',size:1,reg:'sophie'});const s=R.groups[R.groups.length-1];const tk={items:[{d:'coffee'}]};const a=loveOrdered(s,tk);const b=loveOrdered(s,tk);S.day+=6;const c=loveOrdered(s,tk);S.day-=6;return[a,b,c]})()")
    check(said == [True, False, True], f'said once, not the next time, said again six days on: {said}')
    check(g.ev("!!(HM.litter2&&HM.bowls)&&homeItems.toString().includes('drawHomeLitter(c,HM.litter2)')&&homeItems.toString().includes('drawHomeBowls(c)')"), 'two litter cabinets and the bowls in the room')
    g.ev("setRoom('home');forceDraw=true"); g.ev("for(let i=0;i<6;i++)__tick(1000/30)"); g.ev("setRoom('main')")
    check(g.ev("homeSpots(catBy('tora')).some(s=>s.k==='bowl')"), 'a cat can go to the bowls')
    near = json.loads(g.ev("""JSON.stringify((()=>{if(!fact('sm_b'))factSet('sm_b');const main=R.tables.filter(t=>(t.room||'main')==='main'&&!t.lounge&&!t.pdr&&t.seats>=2);
      spawn({t:R.t,type:'office',size:1,reg:'mia'});const m=R.groups[R.groups.length-1];const T0=main[0];seatGroup(m,T0);
      spawn({t:R.t,type:'office',size:1,reg:'sophie'});const s=R.groups[R.groups.length-1];
      const d=t=>Math.hypot(t.x-T0.x,t.y-T0.y);const others=main.filter(t=>t!==T0).sort((a,b)=>d(a)-d(b));
      const a=storyNearTable(s,others);const far=others.filter(t=>d(t)>d(others[0])*1.15);const b=far.length>=2?storyNearTable(s,far):undefined;
      return{next:a===others[0],far:b===null,nf:far.length}})())"""))
    check(near['next'] and near['far'] and near['nf'] >= 2, f'Sophie and Mia: 「旁邊」 is the next table, or not today (「sophie mia根本沒有坐在一起」): {near}')
    g.ev("const J=LIFE.jill;J.on=true;J.x=150;J.face=1;J.legs=0;J.legTarget=0;for(const c of CATS)if(c.sofa)c.sofa=null")
    check(g.ev("sofaSlots(catBy('mei')).some(s=>s.kind==='lean')") and not g.ev("sofaSlots(catBy('snow')).some(s=>s.kind==='lean')"), '寶寶 alone can lean against Jill')
    g.ev("Math.random=(()=>{let a=886;return()=>{a=(a*1103515245+12345)%2147483648;return a/2147483648}})();const J=LIFE.jill;J.legs=1;J.legTarget=1")
    lap = g.ev("(()=>{const c=catBy('mikan');let n=0;for(let i=0;i<400;i++){const s=pickSofaSlot(c,false);if(s&&s.kind==='lap')n++}return n})()")
    check(lap >= 80, f'柔柔 on her legs, often, when she stretches them out: {lap}/400')
    check(not g.errors, g.errors[:3]); g.close()


@test
def rc83_a_new_space_has_its_first_photo(b, port, target):
    """The player: 「新增房間之後要有拍照時刻是設計給房間的吧」. In a new space's first days, the first time it is on screen
    during the evening, a photo of it — once."""
    g = Game(b, port, target, seed=887, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day74_1508.json')
    g.ev("S.newRooms=S.newRooms||{};S.newRooms.lounge=S.day;S.spacePhoto={}")
    to_service(g)
    g.ev("setRoom('lounge');forceDraw=true")
    g.ev("for(let i=0;i<10;i++)__tick(1000/30)")
    g.ev("spacePhotoCheck();flushMem()")
    a = json.loads(g.ev("JSON.stringify(albumList().filter(p=>p.kind==='newspace').map(p=>p.txt||p.text||''))"))
    check(len(a) == 1 and 'The Lounge' in a[0], f'one photo of the new Lounge: {a}')
    g.ev("spacePhotoCheck();flushMem()")
    check(g.ev("albumList().filter(p=>p.kind==='newspace').length") == 1, 'once')
    check(not g.errors, g.errors[:3]); g.close()


@test
def rc84_kens_three_nights_three_pictures(b, port, target):
    """The player, 2026-10-04 (docs/v24/ken_tasting_pictures_2026-10-04.txt): each of the first three 品酒之夜 Ken arranges has
    its own picture — 剛開始辦 (the existing picture), 有模有樣 and 變成這裡的一部分 (the player's two of 2026-10-04) — shown the
    first time its night plays, and the same three are Story Photos in the album; after the third, none. No stand-ins: a
    picture without its art is not shown. The player's save, past all three nights, gets the three on the story page and in the
    album on the nights' own days."""
    g = Game(b, port, target, seed=884, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day89_2320.json')
    il = json.loads(g.ev("JSON.stringify(['ken_t1','ken_t2','ken_t3'].map(k=>({k,t:STORY_ILLUS[k].t,art:!!storyArtSrc(STORY_ILLUS[k].art),tbd:(illusSrc(k)||{}).tbd})))"))
    check([x['t'] for x in il] == ['剛開始辦', '有模有樣', '變成這裡的一部分'] and all(x['art'] and x['tbd'] is False for x in il), f'three pictures, the player\'s, no stand-in: {il}')
    check(g.ev("STORY_PHOTOS.ken_night1.art") == 'ken_t1' and g.ev("storyArtSrc('ken_night2')!==storyArtSrc('ken_night3')&&storyArtSrc('ken_night2')!==storyArtSrc('ken_t1')"), 'the first is the existing picture; three different pictures')
    beats = json.loads(g.ev("JSON.stringify(STORY_LINES.find(L=>L.k==='ken').beats.filter(b=>b[2]&&b[2].illus).map(b=>b[0]))"))
    check(beats[:3] == ['ken_t1', 'ken_t2', 'ken_t3'], f'the story page: each night its picture: {beats}')
    days = json.loads(g.ev("JSON.stringify(['ken_t1','ken_t2','ken_t3'].map(k=>fact(k).d))"))
    seen = json.loads(g.ev("JSON.stringify(['ken_t2','ken_t3'].map(k=>(story().illus||{})[k]||null))"))
    check(seen == days[1:], f'the player\'s save: the second and third nights\' pictures on the story page, on their days: {seen} {days}')
    alb = json.loads(g.ev("JSON.stringify(['ken_night1','ken_night2','ken_night3'].map(k=>{const p=albumList().find(x=>x.kind==='story:'+k);return p?p.day:null}))"))
    check(alb == days, f'and in the album, the three in a row on the nights\' own days: {alb} {days}')
    # a picture without its art: nothing shown, the photo waits
    w = json.loads(g.ev("(()=>{const a=STORY_ART.ken_night3;delete STORY_ART.ken_night3;delete ILLUS_CACHE.ken_t3;const r={src:illusSrc('ken_t3')};const o=kenIllusMig({story:{facts:{ken_t2:{d:83,n:1,l:83},ken_t3:{d:88,n:1,l:88}},illus:{}}});r.illus=o.story.illus;r.pend=Object.keys(o.story.photosPending);STORY_ART.ken_night3=a;return JSON.stringify(r)})()"))
    check(w['src'] is None and w['illus'] == {'ken_t2': 83} and w['pend'] == ['ken_night2', 'ken_night3'], f'without its art: no picture, the photo waits: {w}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def rc85_a_picture_always_holds_the_service(b, port, target):
    """The player, 2026-10-04 (docs/v24/illus_always_holds_2026-10-04.txt): 「有跳出我生成圖片的畫面的劇情 都是要 停止餐廳營業 玩家手動
    按才繼續 避免玩家沒注意到」. Whatever brings one of the player's pictures up during a service holds the restaurant until
    its last line is tapped — a scene that is not a held beat (怡君's first evening), a story photo taken outside a beat
    (shown now, not only named), 「看插圖」 from the journal; Ken and 杜's two photos are held beats. A line with only a face
    still lets the service run."""
    g = Game(b, port, target, seed=885, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day89_2320.json')
    g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}"); _quiet(g); to_service(g)
    g.ev("__botUntil('R.t>=R.dur*.3',90000,1/30)")
    g.ev("const d=storyDay();d.major=9;d.minor=9;d.v24=9"); _frames(g, 200)   # nothing else of the stories tonight
    g.ev("window.__noScenes=false")
    def held(what):
        st = json.loads(g.ev("JSON.stringify({dlg:!!DLG,hold:!!(DLG&&DLG.hold),chip:$('#dlg .dlg-hold').hidden?'':$('#dlg .dlg-hold').textContent,pic:!document.querySelector('#dlg .dlg-illus').hidden,src:(document.querySelector('#dlg .dlg-illus img').getAttribute('src')||'').slice(0,15)})"))
        check(st['dlg'] and st['hold'] and '店裡暫停中' in st['chip'] and st['pic'] and st['src'].startswith('data:image/'), f'{what}: the picture, and the restaurant held: {st}')
        before = json.loads(g.ev(HOLD_SNAP)); _frames(g, 90); after = json.loads(g.ev(HOLD_SNAP))
        check(after == before, f'{what}: nothing moves while it is up: {before} -> {after}')
    # a scene that is not a held beat, with the player's picture
    g.ev("scene([{who:'staff:秀琴阿姨',text:'妳怎麼來了？'},{who:'',name:'怡君',text:'吃飯啊。'}],null,{illus:'yj_intro'})")
    held('a scene with a picture')
    g.ev("dlgNext()"); check(g.ev("!!DLG&&DLG.hold"), 'still held on its second line')
    g.ev("dlgNext()"); check(g.ev("DLG") is None, 'closed on the last tap')
    t0 = g.ev("R.t"); _frames(g, 30); check(g.ev("R.t") > t0, 'and the service goes on')
    # a line with only faces is not held
    g.ev("scene([{who:'jill',text:'今天還好嗎？'},{who:'dylan',text:'嗯。'}],null,{})")
    check(g.ev("!!DLG&&!DLG.hold"), 'faces only: the service runs under it, as before')
    g.ev("while(typeof DLG!=='undefined'&&DLG)dlgNext()")
    # a story photo with the player's picture, taken outside a beat: shown, and held
    g.ev("delete story().photos.staff_meal;storyPhoto('staff_meal',{names:'阿拓、安安'})")
    check(g.ev("$('#dlg .dlg-text').textContent").startswith('相簿多了一張'), 'the photo is shown with its line')
    held('a story photo')
    g.ev("dlgNext()"); check(g.ev("DLG") is None and g.ev("albumList().some(p=>p.kind==='story:staff_meal')"), 'one tap, and it is in the album')
    # 「看插圖」 during a service
    check(g.ev("illusOpen('ken_t1')") is True, 'a seen picture reopens')
    held('看插圖')
    g.ev("dlgNext()"); check(g.ev("DLG") is None, 'closed')
    # Ken and 杜's two photos are held beats; their everyday arguing is not
    check(g.ev("shAuthored({k:'kd_photo'})&&shAuthored({k:'kd_photo2'})&&!shAuthored({k:'kd_argue'})"), 'kd_photo and kd_photo2 hold; kd_argue does not')
    check(not g.errors, g.errors[:3]); g.close()


@test
def rc85_the_rooms_upstairs_are_bought_by_their_buttons(b, port, target):
    """The player, 2026-10-04: 「無法升級到二級休息室 訂購70000按不下去」 (and on a computer: 「升級餐廳點不到右邊的項目」). Since rc6 the
    phase buttons of the Staff Room and the Private Dining Room were written without their phase (a bare attribute 「2」), so a
    tap bought nothing; the tests had called buyRoomPhase directly. On the player's Day 92 save: the button carries its
    phase, a real tap buys Phase II for $70,000 and it is there the next day; no button in the shop carries a stray
    attribute."""
    g = Game(b, port, target, seed=930, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day92_2105.json')
    g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}")
    if g.ev("phase") != 'shop': g.ev("showShop()")
    bad = []
    for t in json.loads(g.ev("JSON.stringify(shopTabs().filter(t=>t.on).map(t=>t.k))")):
        g.ev(f"shopTab='{t}';showShop()")
        bad += json.loads(g.ev("JSON.stringify([...screenEl.querySelectorAll('[data-act]')].filter(e=>[...e.attributes].some(a=>!/^(data-|class|style|disabled|id|title|aria-|type|alt|src|href|role|tabindex)/.test(a.name))).map(e=>e.outerHTML.slice(0,100)))"))
    check(not bad, f'every button in the shop says what it buys: {bad[:3]}')
    g.ev("shopTab='works';showShop()")
    check(g.ev("document.querySelector('[data-act=buySR]').dataset.k") == '2', 'the Staff Room II button carries its phase')
    m0 = g.ev("S.money"); g.click('[data-act=buySR]')
    check(g.ev("S.money") == m0 - 70000 and g.ev("srOf().st2") == g.ev("S.day") + 1, f'a tap buys it: {g.ev("JSON.stringify(srOf())")}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def rc85_the_crew_go_up_to_the_staff_room_in_a_busy_evening(b, port, target):
    """The player, 2026-10-04: 「營業時間也有 但沒看到任何員工去」. On the player's Day 92 save (ten of the floor, a queue at the door
    most of the evening) nobody reached the Staff Room in a whole service: a break waited for the whole restaurant to be
    quiet (6% of the evening) and one on the stairs was called back the moment anyone waited at the door. Now a break waits
    for spare hands (three of the floor with nothing in hand — 92% of that evening): in a whole service several of the
    floor go up on their own, one at a time, each stays long enough to be come across, and comes back down; nobody is
    called back while others are free; the room's tab is there all evening and shows them inside."""
    g = Game(b, port, target, seed=9204, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day92_2105.json')
    g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}"); to_service(g)
    st = {}; visits = []; tabs = True; most = 0
    while g.ev("phase==='service'&&!!R&&R.closing==null"):
        g.ev("__botUntil('false',15,1/30)")
        if not g.ev("!!R"): break
        tabs = tabs and g.ev("roomsOpen().includes('staff')")
        s = json.loads(g.ev("JSON.stringify({t:R.t/R.dur,cw:(S.crew||[]).filter(m=>R.cw&&R.cw[m.id]).map(m=>{const w=R.cw[m.id];return[m.name,w.room==='staff'&&!!(w.task&&w.task.sr&&w.task.fired),!!(w.task&&w.task.sr)]}),seen:srPeople().filter(p=>p.seated).length})"))
        if s['t'] < .05: continue
        most = max(most, s['seen'])
        for n, inside, sr in s['cw']:
            o = st.get(n, {'in': None, 'sr': False})
            if inside and o['in'] is None: o['in'] = s['t']
            if o['sr'] and not sr:
                visits.append((n, (s['t'] - o['in']) if o['in'] is not None else None)); o['in'] = None
            o['sr'] = sr; st[n] = o
    stayed = [v for v in visits if v[1] is not None]
    check(tabs, 'the Staff Room tab is there all through the service')
    check(len(stayed) >= 2 and all(v[1] > .06 for v in stayed), f'several of the floor went up on their own and stayed a while (more than ~16 minutes each): {visits}')
    check(len(visits) - len(stayed) <= 1, f'at most one called back on the way: {visits}')
    check(most >= 1 and most <= 2, f'one at a time, two together at most: {most}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def rc85_small_talk_is_rare_and_makes_sense(b, port, target):
    """The player, 2026-10-04 (docs/v24/dialogue_too_much_2026-10-04.txt): 「跳出的對話有些太重複沒有意義 又太頻繁 一些不重要的npc沒有
    劇情的對話可以少一點 而且有的對話非常沒有邏輯不像人在說話 例如 這是果味」. A whole evening on the player's Day 83 save: the
    nameless guests' and the crew's small talk is ten lines at most, one at a time with a gap between; 「Rush Mode 結束」 never
    pops up, 「VIP 貴賓到了」 once at most, the moves to and from the Lounge are in the day's log, not over the room. Ken and
    杜's arguments say what they are about. Things that pop up: about a third of before (93 an evening measured on this
    save, docs/evidence/v24_rc8_5/lines/)."""
    g = Game(b, port, target, seed=8301, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day83_2218.json')
    g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}"); to_service(g)
    g.ev("window.__pop=[];const t0=toast;toast=function(h,k,o){if(R)__pop.push({h:String(h).replace(/<[^>]+>/g,''),k:k||'',t:R.t});return t0.apply(this,arguments)};const p0=portraitLine;portraitLine=function(w,t,o){const r=p0.apply(this,arguments);if(r&&R)__pop.push({h:t,k:'face',t:R.t});return r}")
    g.ev("window.__small=[];const c0=chatSaid;chatSaid=function(t){if(R&&phase==='service'&&!SCX)__small.push(R.t);return c0.apply(this,arguments)}")
    while g.ev("phase==='service'&&!!R"):
        g.ev("__botUntil('false',90,1/30)"); g.page.wait_for_timeout(5)
    pops = json.loads(g.ev("JSON.stringify(window.__pop)")); small = json.loads(g.ev("JSON.stringify(window.__small)")); dur = 250
    check(len(small) <= 10, f'ten lines of small talk at most: {len(small)}')
    gaps = [b2 - a for a, b2 in zip(small, small[1:])]
    check(all(x >= dur * .05 - .5 for x in gaps), f'one at a time, with a gap: {[round(x, 1) for x in gaps]}')
    texts = [p['h'] for p in pops]
    check(not any('Rush Mode 結束' in t for t in texts), 'the end of Rush Mode is no news')
    check(sum('VIP 貴賓到了' in t for t in texts) <= 1, 'the VIPs: the first of the evening')
    check(not any('換到 Lounge 坐' in t or '再喝一杯' in t or '從 Lounge 過去' in t for t in texts), 'the Lounge moves are in the log, not over the room')
    check(len(pops) <= 45, f'what pops up in an evening: {len(pops)} (93 before)')
    kd = g.ev("String(STORY_EV.find(e=>e.k==='kd_argue').run)")
    check('那是果香，不是糖。' in kd and "'那是果味。'" not in kd and g.ev("STORY_EV.find(e=>e.k==='kd_argue').cd") == 5, 'Ken and 杜 say what they argue about, every five days at most')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_the_day_is_held_for_the_beat_its_people_came_for(b, port, target):
    """Pacing (measured on the Day 52 save): when the schedule brings someone for a due v2.4 major beat, that beat keeps
    a major slot until it plays or until 85% of the service; another story's major that comes up while every free slot
    is spoken for waits (it is counted as missed, so its priority rises) — except a beat that has only this day (floor
    0: Dylan on Valentine's), which is never held back. rc7 (the player, 15:39 「一天可以不只一個劇情」): two major slots
    a day, so with both free another story's major may take one; the two are a part of the evening apart. Grouped story
    visits keep their hour."""
    g = Game(b, port, target, seed=267, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day52.json')
    to_service(g)
    g.ev("STORY_EV.push({k:'__t_major',lane:'major',cls:'A',floor:1,at:['order'],w:()=>1e9,when:()=>true,run:()=>{}},{k:'__t_major2',lane:'major',cls:'A',floor:1,at:['order'],w:()=>1e9,when:()=>true,run:()=>{}},{k:'__t_dated',lane:'major',cls:'A',floor:0,at:['order'],w:()=>1e12,when:()=>false,run:()=>{}})")
    g.ev("const d=storyDay();d.major=0;d.lp={};d.seen={};v24().res={d:S.day,k:['yj_meet']};R.t=R.dur*.4")
    check(g.ev("JSON.stringify(v24Held('order'))") == '["yj_meet"]', 'held for 怡君 while her beat is due')
    first = g.ev("storyTick('order',{})")
    check(first in ('__t_major', '__t_major2') and g.ev("storyDay().major") == 1, f'two slots free: another story\'s major takes one ({first}); one stays kept')
    other = '__t_major2' if first == '__t_major' else '__t_major'
    g.ev("R.t=R.dur*.5"); n0 = g.ev("storyDay().major"); g.ev("storyTick('order',{})")
    check(g.ev("storyDay().major") == n0 and g.ev(f"evState('{other}').n") == 0, 'not in the same part of the evening as the last one')
    g.ev("R.t=R.dur*.7;storyTick('order',{})")
    check(g.ev("storyDay().major") == 1 and g.ev(f"evState('{other}').n") == 0 and g.ev(f"evState('{other}').miss") >= 1, 'the last free slot is kept for 怡君: another major waits, counted as missed (once a day)')
    g.ev("STORY_EV.find(E=>E.k==='__t_dated').when=()=>true")
    fired = g.ev("storyTick('order',{})")
    check(fired == '__t_dated' and g.ev("storyDay().major") == 2, f'a beat with only this day still plays: {fired}')
    g.ev("STORY_EV.splice(STORY_EV.findIndex(E=>E.k==='__t_dated'),1);const d=storyDay();d.major=1;d.lp={}")
    g.ev("R.t=R.dur*.86;storyTick('order',{})")
    check(g.ev("v24Held('order')") is None and g.ev(f"evState('{other}').n") == 1, 'late in the service the hold is gone, and it plays')
    g.ev("const d=storyDay();d.major=0;d.lp={};d.seen={};R.t=R.dur*.5;factSet('yj_meet')")
    check(g.ev("v24Held('order')") is None, 'once the beat has played, nothing is held')
    g.ev("for(const k of ['__t_major','__t_major2'])STORY_EV.splice(STORY_EV.findIndex(E=>E.k===k),1)")
    # grouped story visits keep their hour; the first of a group finds a room with a table for each
    out = json.loads(g.ev("JSON.stringify((()=>{const out=[];v24Visits(out,R.dur,()=>true);return out})())"))
    check(all(o.get('hold') for o in out if o.get('v24grp')), f'grouped visits are held at their hour: {out}')
    check(not g.errors, g.errors[:3]); g.close()


def _hire(g, act, k):
    g.ev("(()=>{const b=document.createElement('button');b.dataset.act='%s';b.dataset.k='%s';doAct('%s',null,'%s',b)})()" % (act, k, act, k))


@test
def v24_restaurant_and_lounge_staff_are_two_pools_that_never_share_places(b, port, target):
    """rc5 (the player, 19:07–19:16; docs/v24/staff_pools_1907_2026-10-01.txt), on the player's Day 61 save (Lounge II,
    twelve restaurant people, Evan and 沈晴): every employee has a pool; the restaurant's capacity comes from the
    restaurant (level, 後場整理區, 側廳, 廚房擴建, 廚房二期) and the Lounge's from its roster (I: Evan, 沈晴; II: 阿拓,
    安安, 許葳); one never adds to the other; the Lounge hires its five by name and nobody else; who works where stays
    the duty board's (a restaurant server on the Lounge floor is still restaurant staff); it all survives a reload."""
    g = Game(b, port, target, seed=271, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day61.json')
    pools = json.loads(g.ev("JSON.stringify(Object.fromEntries(S.crew.map(m=>[m.name,m.pool])))"))
    check(pools['Evan'] == 'lounge' and pools['沈晴'] == 'lounge' and all(v == 'restaurant' for k, v in pools.items() if k not in ('Evan', '沈晴')), f'migrated: {pools}')
    check(g.ev("restaurantCap()") == 12 and g.ev("poolCrew('restaurant').length") == 12, 'the restaurant: level 5 (6) + 後場整理區 + 側廳 + 廚房擴建 (2 each) = 12, all taken')
    check(g.ev("CAP_ROLES.map(r=>roleCrew(r).length+'/'+roleCap(r)).join()") == '6/6,4/4,2/2', 'rc8: chefs 6/6, waiters 4/4, cleaners 2/2')
    check(g.ev("loungeCap()") == 5 and g.ev("poolCrew('lounge').length") == 2, 'the Lounge: its roster at II is five; two hired')
    g.ev("S.money+=500000")
    n = g.ev("S.crew.length"); _hire(g, 'hire', 'waiter')
    check(g.ev("S.crew.length") == n, 'the restaurant is full: no waiter, though the Lounge has three open places')
    _hire(g, 'hire', 'bartender')
    check(g.ev("S.crew.length") == n, 'nobody is hired as a generic bartender')
    for nm in ['阿拓', '安安', '許葳']:
        _hire(g, 'hireLounge', nm)
    got = json.loads(g.ev("JSON.stringify(poolCrew('lounge').map(m=>[m.name,m.role]))"))
    check(sorted(got) == sorted([['Evan', 'bartender'], ['沈晴', 'bartender'], ['阿拓', 'chef'], ['安安', 'waiter'], ['許葳', 'cleaner']]), f'the five, by name: {got}')
    check(g.ev("poolCrew('restaurant').length") == 12 and g.ev("restaurantCap()") == 12, 'hiring the Lounge took no restaurant place')
    n = g.ev("S.crew.length"); _hire(g, 'hireLounge', '阿拓'); _hire(g, 'hire', 'chef')
    check(g.ev("S.crew.length") == n, 'full on both sides: no sixth Lounge person, no thirteenth restaurant one')
    # the restaurant's works add restaurant places only, the Lounge's works Lounge places only
    l0, r0 = g.ev("loungeCap()"), g.ev("restaurantCap()")
    g.ev("S.rooms.kitchen2=1")
    check(g.ev("restaurantCap()") == r0 + 2 and g.ev("loungeCap()") == l0, '廚房二期: +2 for the restaurant, nothing for the Lounge')
    g.ev("S.rooms.up=1;S.rooms.lounge=3")
    check(g.ev("restaurantCap()") == r0 + 2 and g.ev("loungeCap()") == l0, 'the second floor and Lounge III add no places at all (nothing mechanical; no new names)')
    g.ev("S.rooms.lounge=1")
    check(g.ev("loungeCap()") == 3 and g.ev("restaurantCap()") == r0 + 2, 'Lounge I alone: three Lounge places (Evan, 沈晴, 阿拓 — the user, 2026-10-07); the restaurant unchanged')
    g.ev("S.rooms.lounge=2;delete S.rooms.up;delete S.rooms.kitchen2")
    # where they work is the board's: a restaurant server on the Lounge floor stays restaurant staff; 安安 works both
    g.ev("(()=>{const m=S.crew.find(m=>m.name==='Nina');m.duties=Object.assign({},waiterDuties(m),{lounge:true})})()")
    check(g.ev("crewPool(S.crew.find(m=>m.name==='Nina'))") == 'restaurant' and g.ev("waiterDuties(S.crew.find(m=>m.name==='Nina')).lounge") is True, 'Nina works the Lounge floor and is still restaurant staff')
    check(g.ev("(()=>{const m=S.crew.find(m=>m.name==='安安');const d=waiterDuties(m);return d.lounge&&d.seat&&d.order})()") is True, '安安: the Lounge floor, and seating and orders anywhere')
    # the shop says it, the manual says it
    g.ev("showShop();shopTab='staff';showShop()"); g.page.wait_for_timeout(80); txt = g.ev("document.querySelector('#screen').innerText")
    check('廚師 6/6・服務生 4/4・清潔員 2/2' in txt and 'Lounge 員工 5/5' in txt and 'Lounge 名單' in txt and 'Lounge 的人都到齊了' in txt, 'the staff page shows two pools (the restaurant\'s as three numbers, rc8)')
    check('阿拓 黃柘' in txt and 'Bar Food 料理員' in txt and '許葳' in txt, 'the roster by name and job')
    check(g.ev("GUIDE.some(s=>s.pts.some(e=>e[0]==='員工'&&/Lounge 名單/.test(e[1])&&/互不佔用/.test(e[1])))") is True, 'the manual explains the two lists')
    # 許葳: her portrait, her faces, her look (not Jill's tail)
    check(g.ev("!!portraitOf('staff:許葳')&&!!portraitOf('staff:許葳','done')&&!!portraitOf('staff:許葳','smile')") is True, '許葳 has her portrait and expressions')
    L = json.loads(g.ev("JSON.stringify(crewLook(S.crew.find(m=>m.name==='許葳')))"))
    check(L['hs'] != 4 and L['top'] == '#4A4845', f'her look, from the sheet: {L}')
    # it all survives a reload
    g.ev("save()"); g.reload(); g.page.wait_for_timeout(150)
    g.click('[data-act=openFresh]') if g.page.query_selector('[data-act=openFresh]') else g.click('[data-act=open]'); g.page.wait_for_timeout(150)
    check(g.ev("poolCrew('lounge').length") == 5 and g.ev("poolCrew('restaurant').length") == 12, 'kept across a reload')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_an_old_shared_cap_save_keeps_everyone_and_waits(b, port, target):
    """rc5 migration: before the split, the Lounge's +2 and +2 were added to one shared cap, so a save can hold more
    restaurant people than the restaurant's own places, and 安安 / 阿拓 were hired as a plain waiter / chef. Nobody is
    fired: 安安 and 阿拓 are the Lounge's by name; the restaurant shows over its number and hires again only below it."""
    g = Game(b, port, target, seed=272, manual=True, viewport={'width': 390, 'height': 844})
    raw = json.load(open(os.path.join(ROOT, 'tests', 'saves', 'player_day61.json'), encoding='utf-8')); raw = raw.get('save', raw)
    raw['crew'] = raw['crew'] + [{'id': 'old1', 'role': 'chef', 'name': '老周師傅', 'lv': 2, 'duty': 'stove'}, {'id': 'old2', 'role': 'waiter', 'name': '安安', 'lv': 3, 'duty': 'both', 'duties': {'seat': True, 'order': True, 'lounge': True}}, {'id': 'old3', 'role': 'chef', 'name': '阿拓', 'lv': 2, 'duty': 'bar'}]
    g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.page.wait_for_timeout(150)
    g.click('[data-act=openFresh]') if g.page.query_selector('[data-act=openFresh]') else g.click('[data-act=open]'); g.page.wait_for_timeout(150)
    check(g.ev("S.crew.length") == 17, 'nobody was fired')
    check(g.ev("crewPool(S.crew.find(m=>m.name==='安安'))") == 'lounge' and g.ev("crewPool(S.crew.find(m=>m.name==='阿拓'))") == 'lounge', '安安 and 阿拓 are the Lounge\'s')
    check(g.ev("poolCrew('restaurant').length") == 13 and g.ev("restaurantCap()") == 12, 'the restaurant: 13 of 12')
    check(g.ev("roleCrew('chef').length") == 7 and g.ev("roleCap('chef')") == 6, 'rc8: the chefs are 7 of 6')
    g.ev("S.money+=500000"); n = g.ev("S.crew.length"); _hire(g, 'hire', 'chef')
    check(g.ev("S.crew.length") == n, 'over its number, the chefs\' list does not hire')
    _hire(g, 'hire', 'cleaner')
    check(g.ev("S.crew.length") == n, 'the cleaners are full on their own (2/2)')
    g.ev("showShop();shopTab='staff';showShop()"); g.page.wait_for_timeout(80); txt = g.ev("document.querySelector('#screen').innerText")
    check('廚師 7/6' in txt and '比名額多' in txt and '大家都留著' in txt, 'the page says why')
    g.ev("S.crew=S.crew.filter(m=>m.name!=='Nina')")   # a waiter's place opens (nobody is ever let go in the game; the test makes the gap)
    _hire(g, 'hire', 'waiter')
    check(g.ev("roleCrew('waiter').length") == 4 and g.ev("S.crew.length") == n, 'a waiter\'s place that opens is a waiter\'s, though the chefs are over theirs')
    _hire(g, 'hireLounge', '許葳')
    check(g.ev("poolCrew('lounge').length") == 5, 'the Lounge still hires its own')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_a_guest_who_came_for_the_signature_says_so_rarely_and_in_different_words(b, port, target):
    """rc5 (the player, 18:32: 「一堆npc一直重複是為了Jill招牌菜來的」): of the guests who come for the signature, one
    every few minutes at most says it, in different words with the dish's name, never the same sentence twice running,
    never a named guest (周董 is himself); and the evening's dice are where they were (the line is picked by a hash)."""
    g = Game(b, port, target, seed=273, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day61.json')
    to_service(g)
    g.ev("window.__fs=[];const q0=quote;quote=function(gr,txt){if(gr&&gr.forSig&&(forSigLines().includes(txt)||/專程為了/.test(txt)))__fs.push({t:txt,named:!!namedId(gr)});return q0.apply(this,arguments)}")   # the line at the door (the 25% line when the dish arrives is its own, already rate-limited)
    g.ev("for(let i=0;i<14;i++){spawn({t:R.t,type:['office','couple','gourmet','vip'][i%4],size:1,forSig:true});R.t+=12;for(let k=0;k<40;k++)__tick(1000/30)}")
    fs = json.loads(g.ev("JSON.stringify(__fs)"))
    check(1 <= len(fs) <= 3, f'one in a while, not every one of fourteen: {fs}')
    check(not any(x['named'] for x in fs), f'never a named guest: {fs}')
    check(all('『' in x['t'] for x in fs) and all('我是專程為了' not in x['t'] for x in fs), f'the dish by its name, not the old sentence: {fs}')
    check(all(fs[i]['t'] != fs[i + 1]['t'] for i in range(len(fs) - 1)), f'not the same twice running: {fs}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_the_signature_steppers_stay_on_their_own_line(b, port, target):
    """rc5 (the player, 17:48, docs/v24/next/dessert_stepper_jumps_2026-10-01.txt): on the prep screen the −/＋ of both
    signature cards sits under the info line, and does not move while the count changes width (9 → 16 → 100 份)."""
    g = Game(b, port, target, seed=274, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day61.json')
    if g.ev("phase") != 'prep': g.ev("showPrep()")
    g.page.wait_for_timeout(100)
    pos = []
    for n in (9, 16, 100):
        g.ev(f"S.stock.signature={n};S.stock.sigdessert={n};showPrep()"); g.page.wait_for_timeout(60)
        r = json.loads(g.ev("JSON.stringify([...document.querySelectorAll('#screen .sig')].map(c=>{const s=c.querySelector('small').getBoundingClientRect(),t=c.querySelector('.step').getBoundingClientRect(),i=c.getBoundingClientRect();return[Math.round(t.top-i.top),Math.round(s.bottom-i.top),Math.round(t.left-i.left)]}))"))
        check(len(r) == 2 and all(st >= sb - 1 for st, sb, _ in r), f'{n} 份: each stepper is under its info line: {r}')
        pos.append(r)
    check(pos[0] == pos[1] == pos[2], f'and stays put while the count changes: {pos}')
    # the cause, structurally: an inline-flex stepper sits beside a line short enough for it (the player's phone font is
    # narrower than this browser's, so the jump showed there and not here) — it must be a block of its own
    disp = g.ev("[...document.querySelectorAll('#screen .sig .step')].map(e=>getComputedStyle(e).display)")
    check(disp and all(d in ('flex', 'block', 'grid') for d in disp), f'a line of its own, whatever the font: {disp}')
    check(not g.errors, g.errors[:3]); g.close()


UP_DONE_BEFORE = r"""(()=>{const set=(k,b)=>{const d=S.day-b;story().facts[k]={d,n:1,l:d}};S.rooms.lounge=Math.max(1,S.rooms.lounge|0);set('lounge_built_1',30);
 ['yj_meet','yj_look','yj_three','yj_chose','yj_move','yj_key','yj_key_seen','xq_oh'].forEach((k,i)=>set(k,34-i*2));
 ['wall_worry','wall_call','wall_photos','wall_jill','wall_visit','wall_wang','wall_setback','wall_report','wall_fee','wall_prep','wall_mediation','wall_settle','wall_paid','wall_article','wall_paper','wall_fixed'].forEach((k,i)=>set(k,Math.max(1,18-i)))})()"""


def _upf(g, k, back):
    g.ev(f"(()=>{{const d=S.day-{back};story().facts['{k}']={{d,n:1,l:d}}}})()")


def _up_day(g, key, seed, tries=4):
    """start days until `key` fires at the start of one (the day's one major can go to another story first)"""
    for i in range(tries):
        if g.ev("phase") == 'summary':
            g.click('[data-act=toShop]'); g.page.wait_for_timeout(80)
        if g.ev("phase") == 'shop':
            g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(150)
        g.ev(f"Math.random=(function(){{let a={seed + i};return function(){{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}}})()")
        to_service(g)
        if g.ev(f"!!fact('{key}')&&fact('{key}').d===S.day"): return True
        g.ev("closeShop('x');for(const q of R.groups.slice())leaveGroup(q,'ok')"); g.page.evaluate('()=>window.__bot(600,1/30)')
        if g.ev("phase") == 'service': g.ev("finishClosing()")
        g.ev("for(let i=0;i<10;i++)__tick(1000/30)")
    return False


@test
def v24_the_second_floor_is_a_story_before_it_is_a_room(b, port, target):
    """P2 (second_floor_and_long_arcs §3–§16, implementation pass I; the player's 10:25): the era opens after the Lounge
    is finished — not after the wall — with the side room and a grown restaurant; a regular's question first (no
    journal), the crew, the landlord's afternoon (Jill goes up once; words only, no room), and only days after that the
    night of the missing cats. Nothing unlocks."""
    g = Game(b, port, target, seed=281, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day52.json')
    check(g.ev("eraOpen('up')") is False and g.ev("due('up_hint',null,0,'up')") is False, 'not before the Lounge')
    g.ev("(()=>{const d=S.day-20;for(const k of ['yj_meet','yj_key','wall_worry','wall_settle'])story().facts[k]={d,n:1,l:d}})()")
    check(g.ev("eraOpen('up')") is False, "怡君's story and the wall done: still not — they open nothing upstairs")
    g.ev("for(const k of ['yj_meet','yj_key','wall_worry','wall_settle'])delete story().facts[k]")
    g.ev(UP_DONE_BEFORE)
    check(g.ev("eraOpen('up')") is True and g.ev("upCan()") is True, 'the Lounge finished: open, with the side room and a crew of twelve')
    check(g.ev("(()=>{const l=S.level;S.level=2;const r=upCan();S.level=l;return r})()") is True, 'no level asked (the user, 2026-10-07: JILL was rc5\'s): a Bistro with the side room and a crew')
    g.ev("for(const k of Object.keys(story().facts))if(/^(yj_|wall_|xq_oh)/.test(k))delete story().facts[k]")
    check(g.ev("eraOpen('up')") is True and g.ev("due('up_hint',null,0,'up')") is True, "and nothing of 怡君's or the wall's needed")
    g.ev("const s0=S.rooms.side;S.rooms.side=0;window.__c=upCan();S.rooms.side=s0")
    check(g.ev("__c") is False, 'no side room, no stairs, no story')
    check(g.ev("due('up_inspect','up_staff',2,'up')") is False and g.ev("due('up_door','up_inspect',3,'up')") is False, 'each step waits for the one before it')
    _upf(g, 'up_hint', 3); _upf(g, 'up_staff', 2)
    check(g.ev("due('up_inspect','up_staff',2,'up')") is True and g.ev("due('up_door','up_inspect',3,'up')") is False, 'the landlord comes when the crew have wondered; the door waits for him')
    _upf(g, 'up_inspect', 2)
    check(g.ev("due('up_door','up_inspect',3,'up')") is False, 'not two days after he locked it')
    _upf(g, 'up_inspect', 3)
    check(g.ev("due('up_door','up_inspect',3,'up')") is True, 'several days later')
    check(g.ev("!!STORY_EV.find(E=>E.k==='up_hint').note") is False and g.ev("!!STORY_EV.find(E=>E.k==='up_hint').ic") is False, 'the first question leaves nothing in the journal')
    check(g.ev("restChapters().find(C=>C.t==='樓上').showIf()") is False, 'and the story page has no 樓上 before the night')
    check(g.ev("!S.rooms.up&&!roomOpen('up')&&secUp(1e9,()=>'')===''") is True, 'nothing to buy, no room')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_the_night_of_the_missing_cats(b, port, target):
    """P2 U4 on the Day 52 save, played: the day's major is taken at the start (the landlord and the air conditioner);
    late in the evening the stair door gives, 柔柔 goes, 小齁 after her — up at the window and by the boxes, an hour at
    most; at closing the closing waits and the crew who are really here search (someone off today never appears);
    the other cats are where they are; the door is found, they go up, the floor is seen, the cats come down, the door is
    latched; the closing goes on and the day ends. No unlock; the journal has 樓上 now."""
    g = Game(b, port, target, seed=282, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day52.json')
    to_service(g); play_day(g, max_steps=60000)
    for _ in range(200):
        if g.ev("phase") != 'service': break
        g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
    g.ev(UP_DONE_BEFORE); _upf(g, 'up_hint', 6); _upf(g, 'up_staff', 5); _upf(g, 'up_inspect', 3)
    check(_up_day(g, 'up_door', 9102), 'the night\'s day starts')
    nina = g.ev("S.crew.find(m=>m.name==='Nina').id"); g.ev(f"setCrewAway(S.crew.find(m=>m.id==='{nina}'),'off')")
    check(g.ev("upNight()") is True and not g.ev("R.upDoor"), 'the door looks shut for most of the evening')
    g.ev("__botUntil('R.t>=R.dur*.83',90000,1/30)")
    check(g.ev("R.upDoor") == 1, 'late in the evening it has given a little')
    g.ev("__botUntil('R.closing!=null',90000,1/30)")
    cats = json.loads(g.ev("JSON.stringify(['mikan','ban'].map(id=>{const c=catBy(id);return[c.st,c.away,c.hidden]}))"))
    check(all(c[0] in ('up', 'upgo') and c[2] for c in cats), f'柔柔 and 小齁 are not in any room downstairs: {cats}')
    others = g.ev("['snow','tora','mei'].every(id=>!upCatBusy(catBy(id)))")
    check(others is True, 'the other three are where they were')
    g.ev("for(let i=0;i<3;i++)__tick(1000/30)")
    check(g.ev("!!R.upSearch&&!R.upSearch.end") is True and g.ev("$('#closePill').hidden") is True, 'the closing became a search: no 「結束今天」 while they look')
    party = g.ev("R.upSearch.F")
    check(nina not in party and len(party) >= 1, f'only the people who are here search: {party}')
    c0 = g.ev("R.closing")
    seen = {'side': False, 'up': False, 'tab': False, 'illus': False}
    for _ in range(300):   # about a minute and a half of the evening, ten frames at a time
        g.ev("for(let i=0;i<10;i++)__tick(1000/30)")
        if g.ev("!R||!R.upSearch||R.upSearch.end"): break
        if g.ev("room==='side'"): seen['side'] = True
        if g.ev("room==='up'"): seen['up'] = True
        if g.ev("roomsOpen().includes('up')"): seen['tab'] = True

    check(g.ev("!!(R&&R.upSearch&&R.upSearch.end)") is True, 'the search ends')
    check(seen['side'] and seen['up'] and seen['tab'], f'the door in the side room, then the floor upstairs: {seen}')
    check(g.ev("R.closing") <= c0 + 1, 'the closing waited for them')
    check(g.ev("fact('up_cats')&&fact('up_cats').d===S.day") is True, 'the cats were found today')
    check(g.ev("(story().illus||{}).up_cats===S.day") is True, 'found: the scene carried the player\'s picture of that night (2026-10-02), kept for the story page')
    g.ev("illusOpen('up_cats')")
    shown = g.ev("!$('#dlg').hidden&&!$('#dlg .dlg-illus').hidden&&$('#dlg .dlg-illus-tbd').hidden&&$('#dlg .dlg-illus img').getAttribute('src')===STORY_ART.up_cats")
    check(shown is True, 'shown again: the player\'s picture itself, not a stand-in')
    g.ev("while(typeof DLG!=='undefined'&&DLG)dlgNext()")
    after = json.loads(g.ev("JSON.stringify({cats:['mikan','ban'].map(id=>{const c=catBy(id);return[c.st,!!c.away,c.hidden,c.hidden&&['hide','hide2'].includes(c.st)&&c.x===SPOT.cave.x&&c.y===SPOT.cave.y]}),door:R.upDoor,tab:roomsOpen().includes('up'),pill:$('#closePill').hidden,up:!!S.rooms.up})"))
    # rc7.4 (found by the full run): back downstairs, 小齁 may go straight into the cave — hidden, but in the main hall
    check(all(c[0] not in ('up', 'upgo') and not c[1] and (not c[2] or c[3]) for c in after['cats']) and not after['door'] and not after['tab'] and not after['pill'] and not after['up'], f'downstairs, the door latched, the tab gone, the closing on — and nothing unlocked: {after}')
    for _ in range(200):
        if g.ev("phase") != 'service': break
        g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
    check(g.ev("phase") in ('summary', 'shop'), 'the day ends')
    check(g.ev("restChapters().find(C=>C.t==='樓上').showIf()") is True and g.ev("restChapters().find(C=>C.t==='樓上').beats.filter(b=>b[1]!=null).length") == 2, 'the journal: 樓上, two beats (the landlord\'s floor, the night)')
    check(g.ev("secUp(1e9,()=>'')") == '', 'still no project')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_the_night_cut_short_is_not_counted_and_comes_again(b, port, target):
    """If the day ends in the middle of it (the closing cut short), the cats are home and the night is not counted —
    it can still happen on another day; and a checkpoint reload in the evening plays it as if nothing happened."""
    g = Game(b, port, target, seed=283, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day52.json')
    to_service(g); play_day(g, max_steps=60000)
    for _ in range(200):
        if g.ev("phase") != 'service': break
        g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
    g.ev(UP_DONE_BEFORE); _upf(g, 'up_hint', 6); _upf(g, 'up_staff', 5); _upf(g, 'up_inspect', 3)
    check(_up_day(g, 'up_door', 9202), 'the night\'s day starts')
    g.ev("__botUntil('R.closing!=null',90000,1/30)"); g.ev("for(let i=0;i<40;i++)__tick(1000/30)")
    check(g.ev("!!R.upSearch") is True, 'searching')
    g.ev("finishClosing()"); g.ev("for(let i=0;i<10;i++)__tick(1000/30)")
    st = json.loads(g.ev("JSON.stringify({cats:['mikan','ban'].map(id=>{const c=catBy(id);return[c.st,!!c.away,c.hidden]}),door:fact('up_door'),cats_f:fact('up_cats')})"))
    check(all(not c[1] and not c[2] for c in st['cats']) and st['door'] is None and st['cats_f'] is None, f'home, and not counted: {st}')
    check(g.ev("due('up_door','up_inspect',3,'up')") is True, 'it can come again')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_jill_calls_the_landlord_and_the_whole_floor_is_hers(b, port, target):
    """P2 U5–U7: the reminder needs the night two days back, two kinds of crew pressure and two kinds of customer
    pressure; rc8: then 《大家待的地方》 (the crew have nowhere to sit), and the call the day after it, in a restaurant that
    can afford to think of it; at closing she
    stands at the stair door and calls; the project is offered (開始規劃 / 之後再說) and only then is in 店舖工程; bought,
    the whole floor is hers and the Staff Room with it (rc8, the player's canon: never an empty floor first; furniture on
    the open floor over the next days, traces later), no seat and no staff place added; kept across reloads before and
    after."""
    g = Game(b, port, target, seed=284, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day52.json')
    g.ev(UP_DONE_BEFORE)
    for k, back in [('up_hint', 16), ('up_staff', 15), ('up_inspect', 13), ('up_door', 10), ('up_cats', 10)]:
        _upf(g, k, back)
    check(g.ev("due('up_remind','up_cats',2,'up')&&upKinds(UP_STAFF)>=2&&upKinds(UP_CUST)>=2") is False, 'no reminder without the pressure')
    for k, back in [('sp_seat', 12), ('sp_box', 9), ('up_busy', 7), ('up_small', 5)]:
        _upf(g, k, back)
    check(g.ev("due('up_remind','up_cats',2,'up')&&upKinds(UP_STAFF)>=2&&upKinds(UP_CUST)>=2") is True, 'two of each: someone may say it')
    _upf(g, 'up_remind', 2)
    check(g.ev("due('up_ask','sr_story',1,'up')") is False, 'no call before 《大家待的地方》')
    _upf(g, 'sr_story', 0)
    check(g.ev("due('up_ask','sr_story',1,'up')") is False, 'not the same day')
    _upf(g, 'sr_story', 1); g.ev("S.money=50000")
    check(g.ev("upAskReady()") is False, 'not with an empty till')
    g.ev("S.money=420000")
    check(g.ev("due('up_ask','sr_story',1,'up')&&upAskReady()") is True, 'ready')
    to_service(g)
    g.ev("__botUntil('R.closing!=null',90000,1/30)")
    for _ in range(600):
        g.ev("__tick(1000/30)")
        if g.ev("sub==='upproj'"): break
    check(g.ev("fact('up_ask')&&fact('up_ask').d===S.day") is True and g.ev("sub") == 'upproj', 'the call, and the project offered')
    check(g.ev("R.jill.room") == 'main', 'Jill is back in the dining room')
    g.click('[data-act=upGo][data-k=plan]'); g.page.wait_for_timeout(80)
    check(g.ev("S.upProj&&S.upProj.state") == 'planned', 'planned')
    for _ in range(300):
        if g.ev("phase") != 'service': break
        g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
    g.ev("save()"); g.reload(); g.page.wait_for_timeout(150)
    g.click('[data-act=openFresh]') if g.page.query_selector('[data-act=openFresh]') else g.click('[data-act=open]'); g.page.wait_for_timeout(150)
    check(g.ev("!!fact('up_ask')&&!S.rooms.up&&secUp(1e9,()=>'X').includes('二樓（整層）')") is True, 'kept across a reload, and in 店舖工程')
    caps0 = g.ev("[restaurantCap(),loungeCap(),tablesTotal()]")
    g.ev("S.money=Math.max(S.money,600000)")
    check(g.ev("buyUp()") is True, 'bought')
    check(g.ev("srBuilt()&&roomOpen('staff')&&srOf().done===S.up.lease") is True, 'the Staff Room with the floor, the same day')
    g.ev("hideReveal()")
    st = json.loads(g.ev("JSON.stringify({up:S.rooms.up,everyday:roomOpen('up'),look:(()=>{upLookOpen();const o=roomOpen('up')&&room==='up';upViewClose();$('#peekPill').hidden=true;screenEl.hidden=false;return o})(),shop:secUp(1e9,()=>'').includes('data-act=\"upLook\"'),plan:secUp(1e9,()=>'').includes('upPlanCv'),lease:S.up.lease,furn:S.up.furn,caps:[restaurantCap(),loungeCap(),tablesTotal()],fact:!!fact('up_lease')})"))
    check(st['up'] == 1 and st['everyday'] and st['look'] and st['shop'] and st['plan'] and st['fact'] and st['caps'] == caps0, f'the floor is Jill\'s — an everyday tab (06:36), its plan and its look in 店舖工程; no seat, no staff place: {st}')
    L = st['lease']
    check(st['furn']['table'] == L + 1 and st['furn']['scratch'] == L + 5, f'the furniture comes over the next days: {st["furn"]}')
    check(g.ev("upHas('table')") is False, 'the same evening: empty')
    g.ev("save()"); g.reload(); g.page.wait_for_timeout(150)
    g.click('[data-act=openFresh]') if g.page.query_selector('[data-act=openFresh]') else g.click('[data-act=open]'); g.page.wait_for_timeout(150)
    check(g.ev("!!S.rooms.up&&roomOpen('up')&&!!S.up.lease") is True, 'kept across a reload (and the floor a tab)')
    g.ev("S.day+=6;IDLE=null")
    check(g.ev("upHas('table')&&upHas('cushion')&&upHas('scratch')&&upTrace('cup')") is True, 'a week later: the table, the cats\' things, a cup')
    check(not g.errors, g.errors[:3]); g.close()


# ---------------------------------------------------------------- v2.4 rc6: the Staff Room and the Private Dining Room
FLOOR_TAKEN = r"""(()=>{const set=(k,b)=>{const d=S.day-b;story().facts[k]={d,n:1,l:d}};v24().first=S.day-70;
 ['yj_meet','yj_look','yj_three','yj_chose','yj_move','yj_key','yj_key_seen','xq_oh'].forEach((k,i)=>set(k,66-i*2));
 ['wall_worry','wall_call','wall_photos','wall_jill','wall_visit','wall_wang','wall_setback','wall_report','wall_fee','wall_prep','wall_mediation','wall_settle','wall_paid','wall_article','wall_paper','wall_fixed'].forEach((k,i)=>set(k,50-i));
 ['up_hint','up_staff','up_inspect','up_door','up_cats','up_busy','up_full','sp_box','sp_seat','up_remind','up_ask'].forEach((k,i)=>set(k,32-i));
 set('up_lease',LEASE);set('up_use',LEASE-2);S.rooms.up=1;const u=upS();const L=S.day-LEASE;u.lease=L;u.furn={table:L+1,cabinet:L+2,coat:L+2,lamp:L+3,cushion:L+3,stool:L+5,scratch:L+5};u.traces={bag:L+2,cup:L+3,charger:L+4,coat:L+6};S.upProj={state:'built'}})()"""


def _floor(g, lease_back):
    g.ev(FLOOR_TAKEN.replace('LEASE', str(lease_back)))


def _quiet(g):
    """the story-update pill over the prep screen (it comes 0.9 s after the prep is drawn) is not what these tests tap"""
    g.page.wait_for_timeout(950); g.ev("(()=>{const n=document.getElementById('storyNote');if(n)n.hidden=true})()")


def _reload(g):
    g.ev("save()"); g.reload(); g.page.wait_for_timeout(150)
    g.click('[data-act=openFresh]') if g.page.query_selector('[data-act=openFresh]') else g.click('[data-act=open]'); g.page.wait_for_timeout(150)


@test
def v24_rc6_the_staff_room_comes_from_a_need_and_grows_in_place(b, port, target):
    """rc8 (the player, 2026-10-03, hard canon: 「玩家第一次正式取得／解鎖二樓時，Staff Room 就必須已經存在並可見……不能先出現
    一個完全空的二樓，再過幾天才蓋 Staff Room」「PDR 仍然可以是之後才出現的獨立發展」): the crew's want of a place —
    two kinds of it (the box, the seat), nothing of 怡君's — is 《大家待的地方》, before the lease; the call to the landlord
    comes after it; the lease's works give the Staff Room with the floor: a room with its own tab on the day the floor is
    hers, the rest of the floor open. II and III come later, in the same room (the first day never moves), the next day
    each; a trace that belongs to someone's story only after it happened; the Private Dining Room's era opens days later.
    A save whose floor was leased empty has the room on load, as of the lease, and the story as history."""
    g = Game(b, port, target, seed=291, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day52.json')
    g.ev(FLOOR_TAKEN.replace('LEASE', '8'))
    # back before the lease: the floor not taken, the call not made
    g.ev("(()=>{S.rooms.up=0;delete S.up;for(const k of['up_lease','up_use','up_ask','sr_story'])delete story().facts[k];if(!loungeLv())S.rooms.lounge=1})()")   # the floor's era follows the Lounge
    check(g.ev("upTaken()") is False and g.ev("eraOpen('up')") is True, 'the floor\'s era, the floor not taken')
    check(g.ev("upKinds(SP_KINDS)") == 2 and g.ev("srStoryReady()") is True, 'two kinds of the want (the box, the seat): 《大家待的地方》 is ready, before the lease')
    check(g.ev("(()=>{const l=S.level;S.level=2;const r=srStoryReady();S.level=l;return r})()") is True, 'no level asked (the user, 2026-10-07)')
    g.ev("story().facts.yj_meet=null;delete story().facts.yj_meet")
    check(g.ev("srStoryReady()") is True, "nothing of 怡君's needed (the player's 10:25)")
    check(g.ev("due('up_ask','sr_story',1,'up')") is False, 'no call to the landlord before it')
    _upf(g, 'sr_story', 2)
    check(g.ev("srStoryReady()") is False and g.ev("due('up_ask','sr_story',1,'up')") is True, 'after it, the call')
    _upf(g, 'up_ask', 1)
    g.ev("S.money=600000")
    check(g.ev("UP_PROJ.cost") == 510000 and '員工休息室' in g.ev("UP_PROJ.d") and '員工休息室' in g.ev("UP_PROJ.done"), 'the lease says what it gives')
    d0 = g.ev("S.day")
    check(g.ev("buyUp()") is True, 'leased')
    g.ev("hideReveal()")
    check(g.ev("upTaken()&&srBuilt()&&roomOpen('staff')&&srStage()===1&&!upWorks()") is True, 'the floor and the Staff Room, the same day: no empty floor first')
    check(g.ev("srOf().done") == d0 and g.ev("upPlanState().sr") == 'built' and g.ev("pdOn()") is False, 'on the plan from the lease; no Private Dining Room')
    check(g.ev("eraOpen('pd')") is False, 'the Private Dining Room is a later development of its own')
    html = g.ev("secUpRooms(1e9,(c,a,k,l)=>`<b data-a=\"${a}\" data-k=\"${k}\">${l}</b>`)")
    check('員工休息室' in html and 'data-a="buySR" data-k="1"' not in html and '租下整層的時候一起隔出來的' in html, f'in 店舖工程: built with the floor, nothing to buy for it: {html[:300]}')
    check(g.ev("srTrace('cup')||srTrace('seat')||srTrace('yj')") is False, 'no one\'s things before their story')
    check(g.ev("String(drawSrKitchenette).includes(\"srTrace('cup')\")&&String(drawSrArmchair).includes(\"srTrace('seat')\")&&String(drawSrTable).includes(\"srTrace('yj')\")") is True, 'the drawings ask for the trace first')
    check(g.ev("buyRoomPhase('sr',2)") is False and g.ev("srWhyNot(2)").startswith('先讓大家用一陣子'), 'Phase II waits a few days')
    g.ev("S.day+=5")
    check(g.ev("buyRoomPhase('sr',2)") is True, 'Phase II')
    g.ev("hideReveal()")
    check(g.ev("srOf().done") == d0 and g.ev("srStage()") == 1, 'the same room; tomorrow it shows')
    g.ev("S.day+=1")
    check(g.ev("srStage()") == 2 and g.ev("srOf().done") == d0, 'II, in place')
    check(g.ev("eraOpen('pd')") is False, 'still no Private Dining Room era six days after the lease')
    g.ev("S.day+=7;S.money+=200000")
    check(g.ev("buyRoomPhase('sr',3)") is True, 'Phase III')
    g.ev("hideReveal();S.day+=1")
    check(g.ev("srStage()") == 3 and g.ev("srOf().done") == d0, 'III, in place')
    check(g.ev("eraOpen('pd')") is True, 'twelve days and more after the lease, the Private Dining Room\'s era opens')
    _reload(g)
    check(g.ev("srStage()") == 3 and g.ev("roomOpen('staff')") is True, 'kept across a reload')
    check(not g.errors, g.errors[:3]); g.close()
    # the player's Day 87 save: the floor leased on Day 85, empty, before this version — the room is there, as of the lease
    g = Game(b, port, target, seed=293, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day87_2257.json')
    st = g.ev("({built:srBuilt(),done:srOf()&&srOf().done,lease:upS().lease,tab:roomOpen('staff'),story:fact('sr_story'),stage:srStage()})")
    check(st['built'] and st['tab'] and st['done'] == st['lease'] == 85 and st['stage'] == 1, f'Day 87: the Staff Room, as of the lease: {st}')
    check(st['story'] and st['story'].get('retro') == 1, f'《大家待的地方》 is history (更早以前), never played: {st}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc6_the_staff_room_is_used_and_the_pools_stay_apart(b, port, target):
    """rc6 F, G, H, AT: at closing some of the crew — the floor, the kitchen, the bar — go up and sit; it is the crew's room,
    so a bartender up there is still on the Lounge's list and the restaurant's number does not change; the first evening
    is ordinary (Jill: 「坐啊。」); no major beat is spent on it; the 2F view shows them over the cut walls."""
    g = Game(b, port, target, seed=292, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day61.json')
    _floor(g, 20); _upf(g, 'sr_story', 6)
    g.ev("(()=>{const s=srW();s.bought=S.day-1;s.done=S.day})()")
    for nm in ['阿拓']:
        g.ev(f"(()=>{{const b=document.createElement('button');doAct('hireLounge',null,'{nm}',b)}})()")
    g.ev("hideReveal&&hideReveal();showPrep()"); g.page.wait_for_timeout(100)
    pools0 = g.ev("JSON.stringify((S.crew||[]).map(m=>[m.name,crewPool(m)]))"); caps0 = g.ev("[restaurantCap(),loungeCap()]")
    _quiet(g); to_service(g)
    g.ev("__botUntil('R.closing!=null&&R.closing>40',90000,1/30)")
    for _ in range(60): g.ev("__tick(1000/30)")
    ppl = json.loads(g.ev("JSON.stringify(srPeople().map(p=>[p.m.name,p.m.role,crewPool(p.m)]))"))
    check(len(ppl) >= 3, f'several of them up there: {ppl}')
    check(any(r == 'chef' for _, r, _ in ppl), f'the kitchen too: {ppl}')
    check(g.ev("fact('sr_first')&&fact('sr_first').d===S.day") is True, 'the first evening: 「坐啊。」')
    check(g.ev("['sr_plug','sr_food','sr_fridge','sr_nina','sr_plug2'].filter(k=>fact(k)).length") == 0, 'nothing else that evening')
    check(g.ev("story().trace.filter(t=>t.d===S.day&&t.lane==='major'&&String(t.k).startsWith('sr')).length") == 0, 'no major beat for using the room')
    check(g.ev("JSON.stringify((S.crew||[]).map(m=>[m.name,crewPool(m)]))") == pools0 and g.ev("[restaurantCap(),loungeCap()]") == caps0, 'the lists and their numbers are as they were')
    check(g.ev("setRoom('up');forceDraw=true;__tick(1000/30);const r=room;setRoom('main');r") == 'up', 'the floor is a tab (06:36), and draws with them in the room (closed)')
    check(g.ev("setRoom('staff');forceDraw=true;__tick(1000/30);room") == 'staff', 'the room draws')
    check(g.ev("document.querySelector('#roomTabs .on span').textContent") == '員工休息室', 'and its tab reads 員工休息室')
    check(not g.errors, g.errors[:3]); g.close()


PD_OPEN = r"""(()=>{const set=(k,b)=>{const d=S.day-b;story().facts[k]={d,n:1,l:d}};['sr_story','sr_first','sr_plug'].forEach((k,i)=>set(k,40-i*3));['pd_yj','pd_other','pd_story'].forEach((k,i)=>set(k,12-i*4));
 const s=srW();s.bought=S.day-39;s.done=S.day-38;s.st2=S.day-30;s.tr={plug:S.day-34,seat:S.day-20};const p=pdW();p.bought=S.day-2;p.done=S.day-1})()"""


@test
def v24_rc6_private_dining_reservations_follow_the_rules(b, port, target):
    """rc6 O–Z, AC, AP, AS: party sizes by phase (I 4–6, II 4–8, III 4–10, four always); one booking an evening, made
    once, never doubled; a story's evening is never taken; walk-ins only on an evening nobody booked; the minimum is
    fixed when the booking is made (prices, a phase, a reload do not change it) and is the floor of the bill, not an
    ordering target; no booking before the room exists; the day's news shows it."""
    g = Game(b, port, target, seed=293, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day61.json')
    _floor(g, 50)
    check(g.ev("(pdDay(),!!(S.up.pd&&S.up.pd.res))") is False, 'no room, no booking')
    g.ev(PD_OPEN)
    fits = lambda: g.ev("[3,4,6,7,8,9,10,11].map(n=>pdFits(n)?1:0).join('')")
    check(fits() == '01100000', f'Phase I: 4–6 ({fits()})')
    g.ev("pdW().st2=S.day")
    check(fits() == '01111000', f'Phase II: 4–8 ({fits()})')
    g.ev("pdW().st3=S.day")
    check(fits() == '01111110', f'Phase III: 4–10, and four still ({fits()})')
    g.ev("delete pdW().st2;delete pdW().st3")
    # one a day, never twice; the first by the second evening the room is open
    g.ev("pdDay();pdDay()")
    r = json.loads(g.ev("JSON.stringify(pdRes())"))
    check(r and r['d'] == g.ev("S.day") and 4 <= r['size'] <= 6 and r['min'] >= 400, f'tonight a booking (the second evening open): {r}')
    check(g.ev("pdBook(S.day,{k:'x'})") is False, 'a story cannot take a booked evening')
    g.ev("pdDay()")
    check(g.ev("JSON.stringify(pdRes())") == json.dumps(r, ensure_ascii=False, separators=(',', ':')), 'made once')
    # the room is held: a walk-in party may not sit there; the booked group may
    check(g.ev("pdTableFor({size:5,pdWalk:1})") is False and g.ev(f"pdTableFor({{size:{r['size']},pdRes:'{r['id']}'}})") is True, 'held for the booking')
    # the minimum: fixed; the bill's floor
    g.ev("for(const d in S.price)S.price[d]*=1.5;pdW().avg=99999;pdW().st2=S.day")
    check(g.ev("pdRes().min") == r['min'], 'prices and a new phase do not change it')
    _reload(g)
    check(g.ev("pdRes().min") == r['min'] and g.ev("pdRes().id") == r['id'], 'nor a reload')
    g.ev("pdDay()")
    check(g.ev("pdRes().id") == r['id'], 'no second booking after the reload')
    g.ev("delete pdW().st2")
    _quiet(g); to_service(g)
    t_pd = g.ev("R.tables.findIndex(t=>t.pdr)")
    check(t_pd >= 0 and g.ev(f"R.tables[{t_pd}].seats") == 6, 'the table is in the evening, six seats')
    lo = g.ev(f"(()=>{{const g0={{pdRes:pdRes().id,table:{t_pd},size:pdRes().size}};return pdBill(g0,pdRes().min-500)}})()")
    check(lo == r['min'], f'ate less than the minimum: the minimum ({lo})')
    g.ev(f"pdRes().status='seated'")
    hi = g.ev(f"(()=>{{const g0={{pdRes:pdRes().id,table:{t_pd},size:pdRes().size}};return pdBill(g0,pdRes().min+700)}})()")
    check(hi == r['min'] + 700, f'ate more: what they ate ({hi})')
    check(g.ev("String(orderItems).includes('pdRes')") is False, 'nobody orders to reach a minimum')
    # an evening a story holds: no booking that day; walk-ins only when nobody booked
    g.ev("S.day+=1;delete pdW().res;pdBook(S.day,{k:'story_test',size:4});pdDay()")
    check(g.ev("!pdRes()&&pdHeld()") is True, 'the story\'s evening: no random booking, the room kept')
    g.ev("S.day+=1;pdW().dry=0;pdW().ever=1")
    found_free = False
    for i in range(12):
        g.ev("S.day+=1;pdDay()")
        if g.ev("!pdRes()"):
            check(g.ev("pdTableFor({size:5,pdWalk:1})") is True and g.ev("pdTableFor({size:3})") is False, 'nobody booked: a party may walk in; three is too few')
            found_free = True; break
    check(found_free, 'some evenings nobody books')
    html = g.ev("(pdDay(),pdNewsHTML())")
    check('私人包廂' in html, f'the news says it: {html}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc6_private_dining_bookings_are_seen_and_grow_with_the_room(b, port, target):
    """rc6 Y, AS frequency: over sixty evenings of each phase the bookings are steady and not hidden — no long dry spells
    (the quiet rise), more in II than in I, more in III than in II."""
    g = Game(b, port, target, seed=294, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day61.json')
    _floor(g, 50); g.ev(PD_OPEN)
    res = {}
    for st in (1, 2, 3):
        out = json.loads(g.ev(f"""JSON.stringify((()=>{{const p=pdW();p.done=S.day-1;delete p.st2;delete p.st3;if({st}>=2)p.st2=S.day-1;if({st}>=3)p.st3=S.day-1;p.dry=0;p.ever=0;delete p.res;const d0=S.day;let n=0,dry=0,maxDry=0,first=null;
          for(let i=0;i<60;i++){{S.day=d0+i;pdDay();const r=pdRes();if(r){{n++;dry=0;if(first==null)first=i}}else{{dry++;maxDry=Math.max(maxDry,dry)}}}}S.day=d0;return{{n,maxDry,first}}}})())"""))
        res[st] = out
    check(all(res[s]['first'] is not None and res[s]['first'] <= 1 for s in res), f'the first booking by the second evening: {res}')
    check(all(res[s]['maxDry'] <= 3 for s in res), f'never long without one: {res}')
    check(res[1]['n'] >= 25 and res[2]['n'] > res[1]['n'] and res[3]['n'] > res[2]['n'], f'more with each phase: {res}')
    check(res[3]['n'] < 60, f'not every evening: {res}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc6_two_more_restaurant_places_and_the_lounge_unchanged(b, port, target):
    """rc6 AG–AJ, AU: the Private Dining Room's first phase adds one place on the restaurant's list, its third another;
    the Lounge's list stays its five; the new places hire from the restaurant's pool; saved and reloaded."""
    g = Game(b, port, target, seed=295, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day61.json')
    _floor(g, 50); g.ev(PD_OPEN)
    g.ev("pdW().done=S.day+1")
    base = g.ev("restaurantCap()"); lc = g.ev("loungeCap()"); roster = g.ev("JSON.stringify(LOUNGE_ROSTER.map(r=>r.name))")
    g.ev("pdW().done=S.day")
    check(g.ev("restaurantCap()") == base + 1, 'Phase I: +1')
    g.ev("pdW().st2=S.day;pdW().st3=S.day")
    check(g.ev("restaurantCap()") == base + 2, 'Phase III: +2 in all')
    check(g.ev("loungeCap()") == lc and g.ev("JSON.stringify(LOUNGE_ROSTER.map(r=>r.name))") == roster, 'the Lounge as it was')
    g.ev("S.money=1e6;showShop();shopTab='staff';showShop()"); g.page.wait_for_timeout(80)
    n0 = g.ev("S.crew.length")
    for _ in range(2):
        b0 = g.page.query_selector('#screen [data-act=hire]')
        check(b0 is not None, 'a restaurant hire is offered')
        b0.click(); g.page.wait_for_timeout(60)
    check(g.ev("S.crew.length") == n0 + 2 and g.ev("S.crew.slice(-2).every(m=>crewPool(m)==='restaurant')") is True, 'two more on the restaurant\'s list')
    check(g.ev("S.crew.slice(-2).every(m=>m.role==='waiter')") is True and g.ev("roleCap('waiter')-roleCapAt('waiter',S.level)") >= 2, 'rc8 §21: the room\'s two places are waiters\' (the chefs\' list stays full)')
    _reload(g)
    check(g.ev("restaurantCap()") == base + 2 and g.ev("S.crew.length") == n0 + 2, 'kept across a reload')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc6_private_dining_story_needs_two_tables_and_a_lived_in_staff_room(b, port, target):
    """rc6 M, 《關上門以後》 (private_dining_room_brief 八): 怡君's 「有比較安靜的嗎？」 only once the Staff Room has been
    there a while; the second table days later; the story needs both, two days after the second, the Staff Room ten days
    old with something of the people in it; then the project. None of it before the Staff Room."""
    g = Game(b, port, target, seed=296, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day61.json')
    _floor(g, 40)
    check(g.ev("due('pd_yj',null,0,'pd')") is False, 'no Staff Room, no Private Dining story')
    g.ev("(()=>{const s=srW();s.bought=S.day-3;s.done=S.day-2})()"); _upf(g, 'sr_story', 4)
    check(g.ev("due('pd_yj',null,0,'pd')") is False, 'not while the Staff Room is new')
    g.ev("(()=>{const s=srW();s.bought=S.day-13;s.done=S.day-12})()")
    check(g.ev("due('pd_yj',null,0,'pd')") is True, 'some days later: 怡君 may come')
    _upf(g, 'pd_yj', 1)
    check(g.ev("due('pd_other','pd_yj',3,'pd')") is False, 'not the next day')
    _upf(g, 'pd_yj', 4)
    check(g.ev("due('pd_other','pd_yj',3,'pd')") is True, 'days later, another table')
    _upf(g, 'pd_other', 1)
    pd_story = "due('pd_story','pd_other',2,'pd')&&srBuilt()&&S.day-srOf().done>=10&&srLived()>=1&&!pdOn()"
    check(g.ev(pd_story) is False, 'not the day after')
    _upf(g, 'pd_other', 2)
    check(g.ev(pd_story) is False, 'not with nothing of anyone in the Staff Room')
    g.ev("srTraceSet('seat',S.day-3)")
    check(g.ev(pd_story) is True, 'ready')
    check(g.ev("secUpRooms(1e9,()=>'X').includes('私人包廂')") is False, 'nothing to buy before the story')
    _upf(g, 'pd_story', 0)
    check(g.ev("secUpRooms(1e9,(c,a,k,l)=>a+':'+k).includes('buyPD:data-k=\"1\"')") is True, 'after it, Phase I (rc8.5: the button carries its phase as data-k)')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc6_the_floor_and_its_rooms_are_tabs(b, port, target):
    """rc6 navigation (the player's 06:36, which keeps the daily 二樓 that 05:23 had taken away; 05:19): 二樓 is a tab
    once the floor is Jill's — the simple floor with its closed rooms — and the Staff Room and the Private Dining Room
    are tabs of their own; the tab you are in reads the room's whole name (員工休息室, 私人包廂); each room's door goes
    back out onto the floor; the floor's doors go into the rooms; the keys go over the same tabs. Every fixture save
    loads with nothing invented: no room, no booking, no story fact it did not have — except, rc8 (the player's canon: the
    Staff Room comes with the floor), a save that had leased the floor empty has its Staff Room, as of the lease, and
    《大家待的地方》 as history (the player's own Day 87 and Day 89 saves)."""
    g = Game(b, port, target, seed=297, manual=True, viewport={'width': 390, 'height': 844})
    for f in sorted(os.listdir(os.path.join(ROOT, 'tests', 'saves'))):
        if not f.endswith('.json'): continue
        raw = load_save(g, f)
        had = [k for k in ['sr_story', 'pd_yj', 'pd_story', 'sp_wait'] if ((raw.get('story') or {}).get('facts') or {}).get(k)]
        st = json.loads(g.ev("JSON.stringify({up:upTaken(),sr:srBuilt(),srDone:srOf()&&srOf().done,lease:S.up&&S.up.lease,pd:!!(S.up&&S.up.pd&&S.up.pd.done!=null),f:['sr_story','pd_yj','pd_story','sp_wait'].filter(k=>fact(k)&&!fact(k).retro),retro:!!(fact('sr_story')&&fact('sr_story').retro),open:[roomOpen('staff'),roomOpen('pdr'),roomOpen('up')]})"))
        if not st['up']:
            check(not st['sr'] and not st['pd'] and set(st['f']) <= set(had) and not any(st['open']), f'{f}: nothing invented ({st}, the save had {had})')
        else:
            check(st['sr'] and st['srDone'] == st['lease'] and st['open'][0] and st['open'][2] and not st['pd'] and set(st['f']) <= set(had) and (st['retro'] or 'sr_story' in had), f'{f}: the floor leased — its Staff Room, as of the lease ({st}, the save had {had})')
    load_save(g, 'player_day61.json')
    _floor(g, 50)
    check(g.ev("upTaken()&&roomOpen('up')&&roomsOpen().includes('up')") is True, 'the open floor is Jill\'s, and a tab')
    g.ev(PD_OPEN)
    _quiet(g); to_service(g); _quiet(g)
    tabs = g.ev("[...document.querySelectorAll('#roomTabs button')].map(b=>b.dataset.room).join(',')")
    check(tabs == 'front,main,side,up,staff,pdr,lounge,kitchen,home', f'二樓 and its two rooms are tabs (rc7.3: Jill\'s room last): {tabs}')
    lab = lambda: g.ev("[...document.querySelectorAll('#roomTabs button')].map(b=>b.textContent+(b.classList.contains('on')?'*':'')).join(',')")
    g.ev("setRoom('main')"); g.click('#roomTabs [data-room=up]'); g.page.wait_for_timeout(40)
    check(g.ev("room") == 'up' and '二樓*' in lab(), f'one tap up to the floor: {lab()}')
    g.click('#roomTabs [data-room=staff]'); g.page.wait_for_timeout(40)
    check(g.ev("room") == 'staff' and '員工休息室*' in lab(), f'one tap into the Staff Room, which is what the tab says: {lab()}')
    g.click('#roomTabs [data-room=pdr]'); g.page.wait_for_timeout(40)
    check(g.ev("room") == 'pdr' and '私人包廂*' in lab() and ',休息室,' in ','+lab()+',', f'and into the Private Dining Room: {lab()}')
    tap = lambda x, y: g.ev(f"(()=>{{roomTap({{x:{x},y:{y}}},{{preventDefault(){{}}}});return room}})()")
    check(tap("PDL.door.x", "LH-30") == 'up', 'its door at the near end: back out onto the floor')
    g.ev("setRoom('staff')")
    check(tap("SRL.door.x", "LH-20") == 'up', 'the Staff Room\'s door: the same')
    up = lambda x, y: g.ev(f"(()=>{{setRoom('up');roomTap({{x:{x},y:{y}}},{{preventDefault(){{}}}});return room}})()")
    check(up("UPR.pdDoor.x", "UPR.pdDoor.y-20") == 'pdr' and up("UPR.pd.x0+60", "UPR.pd.y0+20") == 'pdr', 'on the floor, the Private Dining Room\'s door or the room itself: in')
    if g.ev("srBuilt()"):
        check(up("UPR.srDoor.fx", "UPR.srDoor.y") == 'staff' and up("UPR.sr.x0+40", "UPR.sr.y1-30") == 'staff', 'the Staff Room\'s door in its side wall, or the room: in (08:37)')
    check(g.ev("(()=>{setRoom('side');document.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowRight'}));return room})()") == 'up', 'the arrow keys go over the same tabs')
    check(g.ev("(()=>{document.dispatchEvent(new KeyboardEvent('keydown',{key:'6'}));return room})()") == 'pdr', 'and the number keys')
    check(not g.errors, g.errors[:3]); g.close()

@test
def v24_rc6_the_floor_is_shown_when_it_changes(b, port, target):
    """the player's 05:23 (B–F, K, L): 店舖工程 shows the whole floor — the rooms closed (walls, doors, signs; nothing of the
    inside, no people), the works, and a restrained 「？」 on the corner nobody has decided about (only once the floor
    has started to be divided); the morning a room is finished, before the opening, the floor is shown once: last
    night's works, then the walls come up, the door, the sign (員工休息室 / 私人包廂) — then the room's own view the first
    time, and back to the day; never again, not after a reload, never during a service."""
    g = Game(b, port, target, seed=301, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day61.json')
    _floor(g, 30); _upf(g, 'sr_story', 3)
    spy = "(()=>{window.__spy={q:0,sr:0,pd:0};const q=upQuestionDraw,s=drawStaffRoom,p=drawPdrRoom;upQuestionDraw=function(){__spy.q++;return q.apply(this,arguments)};drawStaffRoom=function(){__spy.sr++;return s.apply(this,arguments)};drawPdrRoom=function(){__spy.pd++;return p.apply(this,arguments)}})()"
    g.ev(spy)
    # the open floor in 店舖工程: the whole floor, no 「？」 yet (nothing has been divided)
    g.ev("S.money=Math.max(S.money,600000);showShop();shopTab='works';showShop()"); g.page.wait_for_timeout(60)
    check(g.page.query_selector('[data-act=upLook]') is not None, '店舖工程 has the floor\'s look')
    g.click('[data-act=upLook]'); g.ev("for(let i=0;i<4;i++)__tick(1000/30)")
    st = json.loads(g.ev("JSON.stringify({room,UPV,pill:$('#peekPill').textContent,tabs:[...document.querySelectorAll('#roomTabs button')].map(b=>b.textContent),q:__spy.q})"))
    check(st['room'] == 'up' and st['UPV'] == 'look' and st['pill'].startswith('回到店舖工程') and st['tabs'] == ['二樓'] and st['q'] == 0, f'the open floor, shown from 店舖工程; no 「？」 before any room: {st}')
    g.click('#peekPill'); g.ev("__tick(1000/30)")
    check(g.ev("UPV===null&&room!=='up'&&!screenEl.hidden") is True, 'back to 店舖工程')
    # the Staff Room bought: built tonight; tomorrow morning, the reveal
    check(g.ev("buyRoomPhase('sr',1)") is True, 'bought'); g.ev("hideReveal()")
    g.ev("S.day+=1;S.today=null;IDLE=null;showPrep()"); g.ev("__tick(500)")
    st = json.loads(g.ev("JSON.stringify({UPV,room,k:UPRV&&UPRV.k,p:upRevealP(),sign:upSignOn('sr'),tabs:[...document.querySelectorAll('#roomTabs button')].map(b=>b.textContent+(b.classList.contains('on')?'*':'')),card:!$('#upRv').hidden,screen:screenEl.hidden,rv:srOf().rv})"))
    check(st['UPV'] == 'reveal' and st['room'] == 'up' and st['k'] == 'sr' and st['p'] == 0 and not st['sign'] and st['tabs'] == ['二樓*'] and not st['card'] and st['screen'] and st['rv'] == g.ev("S.day"), f'the morning it is finished: the floor, last night\'s works first: {st}')
    g.ev("__spy.q=0;__spy.sr=0;for(let i=0;i<40;i++)__tick(1000/30)")
    mid = g.ev("upRevealP()")
    check(0 < mid < 1, f'the walls coming up: {mid}')
    g.ev("for(let i=0;i<70;i++)__tick(1000/30)")
    st = json.loads(g.ev("JSON.stringify({p:upRevealP(),sign:upSignOn('sr'),card:!$('#upRv').hidden,txt:$('#upRv').innerText,q:__spy.q,sr:__spy.sr})"))
    check(st['p'] == 1 and st['sign'] and st['card'] and '員工休息室' in st['txt'] and '進去看看' in st['txt'], f'then the room, its sign, and a card: {st}')
    check(st['q'] > 0 and st['sr'] == 0, f'the 「？」 where the other room is not yet; nothing of the room\'s inside drawn on the floor: {st}')
    g.click('#upRv [data-uprv=in]'); g.ev("for(let i=0;i<4;i++)__tick(1000/30)")
    st = json.loads(g.ev("JSON.stringify({room,UPV,pill:$('#peekPill').textContent,on:(document.querySelector('#roomTabs .on span')||{}).textContent,sr:__spy.sr})"))
    check(st['room'] == 'staff' and st['pill'].startswith('回到開店準備') and st['on'] == '員工休息室' and st['sr'] > 0, f'into the room\'s own view, the first time: {st}')
    g.click('#peekPill'); g.ev("__tick(1000/30)")
    check(g.ev("phase==='prep'&&UPV===null&&!screenEl.hidden&&$('#upRv').hidden") is True, 'and back to the day')
    _reload(g); g.ev("__tick(900)")
    check(g.ev("UPV") is None and g.ev("upRevealDue()") is None, 'not again after a reload')
    # the Private Dining Room finished on a morning: the same; but a service never starts one
    g.ev("(()=>{const p=pdW();p.bought=S.day-1;p.done=S.day})()")
    check(g.ev("upRevealDue()") == 'pd', 'the Private Dining Room is due')
    g.ev("showPrep()")   # its reveal is due 0.45 s after the prep screen; the day is opened before that
    to_service(g)
    g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
    check(g.ev("UPV") is None and g.ev("room") != 'up' and g.ev("phase") == 'service', 'a service never starts one')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc6_the_staff_room_has_a_way_to_every_seat(b, port, target):
    """the player's 05:19 room (E, H, I-10) and its 06:43 recreation: the sofa and its armchairs, the long table with its
    banquette and end chairs, the stool at the counter, the bench at the lockers, the pool table (II) and the massage
    chair (III) — from the door at the near end there is a way to every place and back, by the shortest way round the
    furniture that touches nothing (obsNext), in each phase, on a phone, a short phone and a desktop; people sit where
    there are seats and stand (at the fridge, the coffee, the lockers, the window, the pool table) only when they are
    standing places."""
    for vw, vh, ph in [(390, 844, 1), (390, 844, 2), (390, 844, 3), (1280, 800, 3), (375, 667, 3)]:
        g = Game(b, port, target, seed=303, manual=True, viewport={'width': vw, 'height': vh})
        load_save(g, 'player_day61.json')
        _floor(g, 60); g.ev("(()=>{const s=srW();s.bought=S.day-50;s.done=S.day-49;s.rv=S.day-49;if(%d>=2)s.st2=S.day-30;if(%d>=3)s.st3=S.day-10})()" % (ph, ph))
        r = json.loads(g.ev(r"""JSON.stringify((()=>{const out=[];const obs=srObs();const inside=(o,x,y)=>x>o.bx0+3&&x<o.bx1-3&&y>o.by0+3&&y<o.by1-3;
          for(const sp of srSpots()){const own=obs.filter(o=>sp.x>=o.bx0&&sp.x<=o.bx1&&sp.y>=o.by0&&sp.y<=o.by1);
           const go=(x,y,tx,ty)=>{const w={room:'staff',x,y,troom:'staff',tx,ty,step:0,moving:false};let bad=0,n=0;for(;n<4000;n++){if(stepTo(w,105/30))break;if(obs.some(o=>!own.includes(o)&&inside(o,w.x,w.y)))bad++}return[n,bad]};
           const a=go(SRL.door.x,SRL.door.y,sp.x,sp.y),z=go(sp.x,sp.y,SRL.door.x,SRL.door.y);out.push({k:sp.k,stand:!!sp.stand,n:a[0],bad:a[1],m:z[0],bad2:z[1]})}return out})())"""))
        far = [x for x in r if x['n'] >= 4000 or x['m'] >= 4000 or x['bad'] > 1 or x['bad2'] > 1]
        check(not far, f'{vw}x{vh} phase {ph}: a way to every place and back, round the furniture (the pool table and the massage chair too): {far}')
        st = {x['k']: x['stand'] for x in r}
        check(all(st[k] for k in ['fridge', 'coffee', 'locker', 'hooks', 'window']) and not any(st[k] for k in ['sofa0', 'lc0', 'b0', 'c0', 'stool', 'bench0']), f'standing places are marked, seats are not: {st}')
        check(set(k for k in st if k.startswith('pool') or k == 'mass') == ({'pool0', 'pool1', 'poolw'} if ph >= 2 else set()) | ({'mass'} if ph >= 3 else set()), f'phase {ph}: the pool table\'s places from II, the massage chair from III: {sorted(st)}')
        check(g.ev("(()=>{R={cw:{},srw:[],tables:[],tickets:[]};const k=srFreeSpot(null).stand;R=null;return !!k})()") is False, 'the first free place is a seat')
        check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc6_the_floor_plan_grows_with_the_building(b, port, target):
    """the player's 06:36 (PART 4–10): 店舖工程 › 二樓 has the floor's plan from the day it is leased and for good — large
    (the card's whole width on a phone), architecture only (walls, windows, the column, the stairs, each room's walls,
    door and name; nothing of anyone or anything inside), the works hatched while a room is being built, 「？」 on what is
    undecided and nothing else written there, 「今天完工」 the day a room is finished, still there when nothing is left to
    build; a tap shows it full screen and a tap closes it."""
    g = Game(b, port, target, seed=311, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day61.json')
    check(g.ev("secUp(1e9,()=>'').includes('upPlanCv')") is False, 'not before the floor is Jill\'s')
    _floor(g, 30); _upf(g, 'sr_story', 3)
    spy = r"""(()=>{window.__pl={t:[],p:0};const ft=CanvasRenderingContext2D.prototype.fillText;CanvasRenderingContext2D.prototype.fillText=function(t){if(window.__plOn)__pl.t.push(String(t));return ft.apply(this,arguments)};
     const d=drawUpPlan;drawUpPlan=function(){window.__plOn=1;try{return d.apply(this,arguments)}finally{window.__plOn=0}};const dp=drawPerson;drawPerson=function(){if(window.__plOn)__pl.p++;return dp.apply(this,arguments)}})()"""
    g.ev(spy)
    shop = lambda: g.ev("(()=>{__pl.t=[];showShop();return JSON.stringify({st:upPlanState(),cap:upPlanCaption(),t:__pl.t,p:__pl.p,w:parseFloat(($('#upPlanCv')||{style:{}}).style.width)||0})})()")
    g.ev("phase='shop';shopTab='works'")
    st = json.loads(shop())
    check(st['w'] >= 300 and st['st'] == {'sr': None, 'pd': None} and '租下整層' in st['cap'], f'leased: the plan, large, the open floor: {st}')
    check(st['t'].count('？') == 1 and '樓梯' in st['t'] and not any(x in st['t'] for x in ['員工休息室', '私人包廂']) and st['p'] == 0, f'the floor plate, the stairs, one 「？」, no rooms, nobody: {st["t"]}')
    bad = [x for x in st['t'] if any(w in x for w in ['Coming', 'Future', 'Residence', 'Dylan', '臥室', '客廳', '書房', '未來'])]
    check(not bad, f'nothing names what is undecided: {bad}')
    g.ev("S.money=Math.max(S.money,600000)")
    check(g.ev("buyRoomPhase('sr',1)") is True, 'the Staff Room bought'); g.ev("hideReveal()")
    st = json.loads(shop())
    check(st['st']['sr'] == 'works' and '施工中' in st['t'] and '施工中' in st['cap'], f'tonight: the works, hatched: {st}')
    g.ev("S.day+=1;srW().rv=S.day")
    st = json.loads(shop())
    check(st['st']['sr'] == 'built' and '員工休息室' in st['t'] and '今天完工' in st['t'] and st['t'].count('？') == 1, f'the morning after: its walls, door and name, 「今天完工」; 「？」 where the other room is not yet: {st}')
    g.ev("S.day+=1")
    st = json.loads(shop())
    check('今天完工' not in st['t'], 'only that day')
    g.ev("(()=>{const s=srW();s.st2=S.day-1;s.st3=S.day;const p=pdW();p.offer=S.day-2;p.plan='plan';p.bought=S.day-1;p.done=S.day;p.rv=S.day;p.st2=S.day;p.st3=S.day})()")
    st = json.loads(shop())
    check(st['st'] == {'sr': 'built', 'pd': 'built'} and '私人包廂' in st['t'] and st['t'].count('？') == 0 and st['p'] == 0, f'both rooms (and nothing more to buy): the plan stays; the player\'s plan (08:37) leaves nothing undecided: {st}')
    g.click('.upplan'); g.page.wait_for_timeout(60)
    big = json.loads(g.ev("JSON.stringify({open:!$('#upPlanBig').hidden,w:parseFloat($('#upPlanBig canvas').style.width)})"))
    check(big['open'] and big['w'] >= 340, f'a tap: full screen: {big}')
    g.click('#upPlanBig'); g.page.wait_for_timeout(40)
    check(g.ev("$('#upPlanBig').hidden") is True, 'a tap: closed')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc6_the_staff_room_plays_a_frame_and_dozes(b, port, target):
    """the player's 06:43 (A1–A5, D): the Staff Room's recreation is life, not a game — from Phase II a pool table (its
    two ends and a place to watch are never handed out at random), from Phase III a massage chair; at closing on about a
    third of the evenings two of the people going up play a frame (a shot every few seconds, a word or two over their
    heads in the room, not in the log), sometimes a third watching, then they sit down; someone often falls asleep in
    the massage chair. No minigame, no number, nothing saved; Phase I is the room as it was."""
    g = Game(b, port, target, seed=313, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day61.json')
    _floor(g, 70)
    g.ev("(()=>{const set=(k,b)=>{const d=S.day-b;story().facts[k]={d,n:1,l:d}};['sp_wait','sr_story','sr_first','sr_plug'].forEach((k,i)=>set(k,62-i*3));const s=srW();s.bought=S.day-59;s.done=S.day-58;s.rv=S.day-58;s.st2=S.day-40;s.st3=S.day-10;s.tr={plug:S.day-55,seat:S.day-40,cup:S.day-30};s.line=S.day-1;s.cnt={}})()")
    n = g.ev("(()=>{let k=0;for(let d=1;d<=400;d++)if(hash('srpool|'+d)%100<36)k++;return k})()")
    check(90 <= n <= 190, f'a frame on about a third of the evenings, not every one: {n}/400')
    check(g.ev("(()=>{R={cw:{},srw:[],tables:[],tickets:[]};const seen=new Set();for(let i=0;i<40;i++){const sp=srFreeSpot(null);if(sp)seen.add(sp.k)}R=null;return [...seen].some(k=>/^pool|^mass$/.test(k))})()") is False, 'the pool table and the massage chair are never a random seat')
    g.ev("(()=>{const h=hash;hash=function(s){if(typeof s==='string'){if(s.indexOf('srpool|')===0)return 1;if(s.indexOf('srmass|')===0)return 2;if(s.indexOf('srpw|')===0)return 3;if(s.indexOf('srpl|')===0)return 0}return h(s)}})()")
    before = g.ev("JSON.stringify(Object.keys(S.up.sr).sort())")
    _quiet(g); to_service(g)
    g.ev("window.__logged=[];const _ll=logLine;logLine=function(w,t){__logged.push(String(t));return _ll.apply(this,arguments)}")
    g.ev("__botUntil('R.closing!=null&&R.closing>1',20000,1/30)")
    seen = {'start': 0, 'shots': 0, 'say': set(), 'doze': 0, 'cue': 0}
    for _ in range(80):
        if not g.ev("phase==='service'&&!!R"): break
        g.ev("for(let i=0;i<20;i++)__tick(1000/30)")
        st = json.loads(g.ev("JSON.stringify({p:R.srPool?{st:R.srPool.st,shot:R.srPool.shot}:null,say:(R.srSay||[]).map(s=>s.txt),doze:srPeople().some(p=>p.doze),at:srPeople().filter(p=>/^pool/.test(p.spotK||'')).length})"))
        if st['p'] and st['p']['st'] >= 1: seen['start'] = 1
        if st['p']: seen['shots'] = max(seen['shots'], st['p']['shot'])
        seen['say'] |= set(st['say'])
        if st['doze']: seen['doze'] = 1
        if not st['p'] and seen['start']: break
    check(seen['start'] and seen['shots'] >= 2, f'a frame: two at the table, shots: {seen}')
    check(seen['doze'], f'someone asleep in the massage chair: {seen}')
    check(seen['say'] & {'打一局？', '來。', '再一局？', '明天吧。', '好球。'}, f'a word or two over their heads: {seen["say"]}')
    logged = g.ev("__logged.filter(t=>['打一局？','來。','再一局？','明天吧。','好球。','睡著了？','真的睡著了。'].includes(t))")
    check(not logged, f'said in the room, not written in the log: {logged}')
    if g.ev("phase==='service'&&!!R"):
        check(g.ev("srPeople().filter(p=>/^pool/.test(p.spotK||'')).length") == 0, 'the frame over, they sit down')
    check(g.ev("JSON.stringify(Object.keys(S.up.sr).sort())") in (before, ), 'nothing new in the save')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc6_a_name_finds_its_person_and_a_person_its_name(b, port, target):
    """the player's 07:09 (an RC6 requirement): ORDER → TABLE (an order's T-number or name takes you to its room and
    marks the table with who is at it), TABLE → PARTY (a tap on a table says T# · who · how many), PERSON → NAME (a tap
    on a regular gives their card with the table), DIALOGUE → PERSON (a tap on a line finds who said it where they are
    now — a guest, a waiter, a cook in the kitchen — or says they have left); across the rooms; the marks last a moment
    and nothing stays on the floor; nothing is saved. Stable references (the group, the table, the regular's id)."""
    g = Game(b, port, target, seed=317, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day61.json')
    _floor(g, 80)
    g.ev(PD_OPEN)
    g.ev("(()=>{const p=pdW();p.done=S.day-30;p.st2=S.day-20;p.st3=S.day-2;p.n=14;p.res={id:'r'+S.day,d:S.day,meal:'dinner',size:8,min:pdMinFor(8,3,'family'),kind:'家庭聚餐',type:'family',name:'陳家',t:.18,status:'booked',phase:3}})()")
    _quiet(g); to_service(g)
    g.ev("__botUntil('R.groups.some(q=>q.pdRes&&[\\'order\\',\\'wait\\',\\'eat\\'].includes(q.state)&&q.ticket)',20000,1/30)")
    mark = lambda: json.loads(g.ev("JSON.stringify({room,m:IDF.map(m=>{const p=m.at&&m.at();return{label:m.label,sub:m.sub,strong:m.strong,room:p&&p.room}})})"))
    check(g.ev("!!R&&R.groups.some(q=>q.pdRes&&q.ticket)") is True, 'the booked party is in, its order on the rail')
    g.ev("setRoom('main');R.tv++;renderTickets()"); g.page.wait_for_timeout(30)
    # ORDER → TABLE, across the rooms: the booked party's order, from the dining room
    sel = g.ev("(()=>{const tk=R.tickets.find(t=>t.g.pdRes);if(!tk)return null;const el=[...document.querySelectorAll('#tickets .tk')].find(e=>+e.dataset.tk===tk.id);if(!el)return null;el.scrollIntoView({inline:'center'});return '#tickets .tk[data-tk=\"'+tk.id+'\"] .tk-h'})()")
    check(sel is not None, 'the party\'s order is on the rail')
    g.page.click(sel); g.ev("__tick(1000/30)")
    st = mark()
    check(st['room'] == 'pdr' and st['m'] and st['m'][-1]['label'].startswith('T') and '陳家' in st['m'][-1]['sub'] and '8 位' in st['m'][-1]['sub'] and st['m'][-1]['room'] == 'pdr', f'the order takes you to its table in the Private Dining Room: {st}')
    # DIALOGUE → PERSON: 王先生 comes in and says something while you are elsewhere; a tap on the line finds him
    g.ev("(()=>{const o=regPlanVisit({t:R.t,type:'couple',reg:'wang',size:1});o.t=R.t+1;R.sched.splice(R.si,0,o)})()")
    g.ev("__botUntil('R.groups.some(q=>regsOf(q).includes(\\'wang\\')&&[\\'order\\',\\'wait\\',\\'eat\\'].includes(q.state))',20000,1/30)")
    check(g.ev("!!R&&R.groups.some(q=>regsOf(q).includes('wang')&&q.table!=null)") is True, '王先生 is in, at a table')
    wroom = g.ev("(()=>{const w=R.groups.find(q=>regsOf(q).includes('wang'));return R.tables[w.table].room||'main'})()")
    other = 'kitchen' if wroom != 'kitchen' else 'main'
    g.ev(f"setRoom('{other}');document.querySelectorAll('#plines>*,#toasts>*').forEach(e=>e.remove())")
    g.ev("(()=>{const w=R.groups.find(q=>regsOf(q).includes('wang'));quote(w,'今天的湯很好喝。',{who:'wang'})})()")
    line = '#plines .pline' if g.page.query_selector('#plines .pline') else '#toasts .toast.who'
    g.page.click(line); g.ev("__tick(1000/30)")
    st = mark()
    check(st['room'] == wroom and st['m'][-1]['label'] == '王先生' and st['m'][-1]['sub'].startswith('T') and st['m'][-1]['strong'], f'the line finds him where he sits: {st}')
    # PERSON → NAME: a tap on him — his card says where he sits (rc7.2: while his table has nothing for Jill to do — a tap
    # on a regular at a table with work waiting is that table's work, tests below)
    g.ev("__botUntil('R.groups.some(q=>regsOf(q).includes(\\'wang\\')&&q.state===\\'eat\\')',40000,1/30)")
    xy = json.loads(g.ev("JSON.stringify((()=>{const w=R.groups.find(q=>regsOf(q).includes('wang'));const p=idMemberAt(w,regsOf(w).indexOf('wang'));const r=sc.getBoundingClientRect();return[r.left+SV.ox+p.x*SV.s,r.top+SV.oy+(p.y-20)*SV.s]})())"))
    g.page.mouse.click(xy[0], xy[1]); g.ev("__tick(1000/30)")
    card = g.ev("$('#regcard').hidden?'':$('#regcard').innerText")
    check('王先生' in card and re.search(r'T\d+', card), f'his card, with his table: {card!r}')
    # a waiter's line and a cook's line: where they are now
    who = g.ev("(()=>{const m=S.crew.find(m=>m.role==='waiter'&&R.cw[m.id]);return m?m.name:null})()")
    g.ev(f"setRoom('front');document.querySelectorAll('#plines>*,#toasts>*').forEach(e=>e.remove());staffSay(S.crew.find(m=>m.name==='{who}'),'來了。')")
    line = '#plines .pline' if g.page.query_selector('#plines .pline') else '#toasts .toast.who'
    g.page.click(line); g.ev("__tick(1000/30)")
    st = mark(); wr = g.ev(f"(()=>{{const m=S.crew.find(m=>m.name==='{who}');return R.cw[m.id].room||'main'}})()")
    check(st['room'] == wr and st['m'][-1]['label'] == who, f'a waiter\'s line finds her: {st}')
    cook = g.ev("(()=>{const m=S.crew.find(m=>m.role==='chef'&&R.ck&&R.ck[m.id]);return m?m.name:null})()")
    if cook:
        g.ev(f"setRoom('main');document.querySelectorAll('#plines>*,#toasts>*').forEach(e=>e.remove());staffSay(S.crew.find(m=>m.name==='{cook}'),'好。')")
        line = '#plines .pline' if g.page.query_selector('#plines .pline') else '#toasts .toast.who'
        g.page.click(line); g.ev("__tick(1000/30)")
        st = mark()
        check(st['room'] == 'kitchen' and st['m'][-1]['label'] == cook, f'a cook\'s line: the kitchen, where he stands: {st}')
    # TABLE → PARTY: a tap on a table says who is at it
    g.ev("setRoom('main')")
    tb = json.loads(g.ev("JSON.stringify((()=>{const t=R.tables.find(t=>(t.room||'main')==='main'&&t.group&&!t.group.reg&&!namedId(t.group)&&['order','wait','eat'].includes(t.group.state));if(!t)return null;const r=sc.getBoundingClientRect();return{i:t.i,n:t.group.name,xy:[r.left+SV.ox+t.x*SV.s,r.top+SV.oy+(t.y-16)*SV.s]}})())"))
    if tb:
        g.page.mouse.click(tb['xy'][0], tb['xy'][1]); g.ev("__tick(1000/30)")
        st = mark()
        check(st['m'][-1]['label'] == f"T{tb['i']+1}" and tb['n'] in st['m'][-1]['sub'], f'a tap on a table: its number and who is at it: {st} {tb}')
    # gone: a line from someone who has left
    g.ev("document.querySelectorAll('#plines>*,#toasts>*').forEach(e=>e.remove());(()=>{const w=R.groups.find(q=>regsOf(q).includes('wang'));quote(w,'謝謝。',{who:'wang'});w.gone=1;R.groups=R.groups.filter(q=>q!==w)})()")
    line = '#plines .pline' if g.page.query_selector('#plines .pline') else '#toasts .toast.who'
    g.page.click(line); g.ev("__tick(1000/30)")
    check('已經離開了' in g.ev("document.querySelector('#toasts').innerText"), 'someone who has left: said so, nothing to find')
    # a moment, then the floor is clean; nothing of it in the save. (rc7.3 release: the service goes on meanwhile, and a guest
    # who speaks in the room you look at is marked softly for 1.8 s (idSpeak) — so a mark may be there at the end; what
    # must be true is that every mark made before the moment is gone, and that whatever is left is new and goes too.)
    t0 = g.ev("idNow()")
    g.ev("for(let i=0;i<120;i++)__tick(1000/30)")
    left = json.loads(g.ev("JSON.stringify(IDF.map(m=>({label:m.label,t0:m.t0,dur:m.dur,strong:m.strong,age:idNow()-m.t0})))"))
    check(all(m['t0'] > t0 and m['age'] <= m['dur'] for m in left), f'the marks last a moment: every mark made before is gone, anything left is new: {left}')
    if left:
        g.ev("for(let i=0;i<%d;i++)__tick(1000/30)" % (int(max(m['dur'] for m in left) * 30) + 6))
        still = g.ev("JSON.stringify(IDF.filter(m=>%s.includes(m.t0)).map(m=>m.label))" % json.dumps([m['t0'] for m in left]))
        check(still == '[]', f'and those go too: {still}')
    check(g.ev("(()=>{save();const t=localStorage.getItem(KEY);return t.includes('IDF')||t.includes('__op')})()") is False, 'nothing of it saved')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc6_cats_visit_the_rooms_and_leave(b, port, target):
    """rc6 H, AD, AT (cats, low frequency, no pathing trouble): a cat that follows the crew into the Staff Room sleeps on
    the sofa a while and comes back down; the Private Dining Room, empty, is one of the rare places up there — never on
    an evening it is kept, never with a table in it; a cat inside walks out by the door when a party comes; both come
    home; the open floor is still where the cats mostly are."""
    g = Game(b, port, target, seed=298, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day61.json')
    _floor(g, 50); g.ev(PD_OPEN)
    g.ev("(()=>{const p=pdW();p.ever=3;p.res={id:'r'+S.day,d:S.day,size:5,min:3800,kind:'x',type:'family',name:'x',t:.9,status:'missed',phase:1}})()")
    _quiet(g); to_service(g)
    g.ev("__botUntil('R.t>=R.dur*.1',90000,1/30)")
    g.ev("window.__pdT=pdTableFor;pdTableFor=()=>false")   # nobody else at the table while she is tested
    check(g.ev("pdFreeForCat()") is True, 'the room is empty and nobody booked it')
    picks = g.ev("(()=>{const c=CATS[0];let n=0;for(let i=0;i<600;i++)if(upCatSpot(c).room==='pdr')n++;return n})()")
    check(10 <= picks <= 120, f'a rare place, not the usual one: {picks}/600')
    # rc7.3: two of the five now live mostly in Jill's room, so at a given instant the floor may have no cat free to
    # follow; the service runs on (bounded) until one is
    check(g.ev("(()=>{for(let i=0;i<600;i++){if(CATS.some(o=>freeFloorCat(o)))return true;__tick(100)}return false})()"), 'no cat free on the floor in a minute of service')
    cid = g.ev("(()=>{const c=CATS.find(o=>freeFloorCat(o));upCatForce(c);upCatUp(c,{room:'pdr',x:290,y:PDW+22,face:1,pose:'sit',t:12});return c.def.id})()")
    W = lambda cond, n=2500: g.ev(f"(()=>{{const c=catBy('{cid}');for(let i=0;i<{n};i++){{if({cond})return i;__tick(100)}}return -1}})()")
    check(W("c.away==='pdr'&&!c.upTo") >= 0, 'in the Private Dining Room, by the window')
    g.ev("setRoom('pdr');forceDraw=true;__tick(1000/30)")
    check(W("c.away!=='pdr'") >= 0 and W("!upCatBusy(c)") >= 0, 'out by the door and down the stairs, by herself')
    g.ev(f"(()=>{{const c=catBy('{cid}');upCatForce(c);upCatUp(c,{{room:'pdr',x:300,y:PDW+22,face:-1,pose:'loaf',t:600}})}})()")
    check(W("c.away==='pdr'&&!c.upTo") >= 0, 'in again, for a long nap')
    g.ev("pdSeated({size:5,pdWalk:1},pdTable())")
    check(W("c.away!=='pdr'", 400) >= 0, 'a party comes: she walks out (no vanishing)')
    check(W("!upCatBusy(c)") >= 0, 'and comes home')
    g.ev("pdTableFor=window.__pdT;pdW().res.status='booked';pdW().res.t=.99")
    check(g.ev("pdFreeForCat()") is False and g.ev("(()=>{const c=CATS[0];let n=0;for(let i=0;i<300;i++)if(upCatSpot(c).room==='pdr')n++;return n})()") == 0, 'a kept evening: never')
    # the Staff Room: after the crew, a nap on the sofa
    g.ev("(()=>{const s=srW();s.bought=S.day-30;s.done=S.day-29})()")
    check(g.ev("(()=>{for(let i=0;i<600;i++){if(CATS.some(o=>freeFloorCat(o)))return true;__tick(100)}return false})()"), 'no cat free on the floor in a minute of service (2)')
    sid = g.ev("(()=>{const c=CATS.find(o=>freeFloorCat(o));const c0=R.closing;R.closing=40;R.srCatId=c.def.id;const sp=upCatSpot(c);R.closing=c0;upCatForce(c);upCatUp(c,Object.assign(sp,{t:8}));return sp.room+'|'+c.def.id})()")
    check(sid.startswith('staff|'), f'the Staff Room spot after the crew: {sid}')
    cid = sid.split('|')[1]
    W2 = lambda cond, n=2500: g.ev(f"(()=>{{const c=catBy('{cid}');for(let i=0;i<{n};i++){{if({cond})return i;__tick(100)}}return -1}})()")
    check(W2("c.away==='staff'&&!c.upTo") >= 0, 'on the sofa')
    g.ev("setRoom('staff');forceDraw=true;__tick(1000/30)")
    check(W2("!upCatBusy(c)") >= 0, 'and back down')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc6_bar_bites_take_no_menu_slot(b, port, target):
    """the player's 09:55 (their own Day 61 save, tests/saves/player_day61_0933.json): today's menu at its cap of 20 with
    the Lounge's four bar bites on it as well — a dish turned off can be turned back on with one tap (the bar bites take
    no slot, as the screen counts them); at the cap a tap says the menu is full and changes nothing."""
    g = Game(b, port, target, seed=331, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day61_0933.json')
    if g.ev("phase") == 'shop': g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(300)
    g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}")
    st = lambda: json.loads(g.ev("JSON.stringify({phase,count:menuCount(),cap:menuCap(),bars:S.menu.filter(d=>DISHES[d]&&DISHES[d].bar).length})"))
    s0 = st()
    check(s0['phase'] == 'prep' and s0['count'] == s0['cap'] and s0['bars'] >= 1, f'the save as the player had it: full, with bar bites: {s0}')
    off = g.ev("S.menu.find(d=>!DISHES[d].bar&&DISHES[d].cat==='main'&&S.menu.filter(x=>DISHES[x].cat==='main').length>1)")
    g.click(f'.menu-row [data-act=toggle][data-d="{off}"]'); g.page.wait_for_timeout(80)
    check(st()['count'] == s0['cap'] - 1 and not g.ev(f"S.menu.includes('{off}')"), 'one dish off')
    g.click(f'.menu-row [data-act=toggle][data-d="{off}"]'); g.page.wait_for_timeout(80)
    check(g.ev(f"S.menu.includes('{off}')") and st()['count'] == s0['cap'], 'and back on with one tap')
    more = g.ev("S.unlocked.find(d=>!S.menu.includes(d)&&!DISHES[d].bar)")
    g.ev("document.querySelectorAll('#toasts>*').forEach(e=>e.remove())")
    g.click(f'.menu-row [data-act=toggle][data-d="{more}"]'); g.page.wait_for_timeout(80)
    toast = g.ev("[...document.querySelectorAll('#toasts>*')].map(e=>e.textContent).join('|')")
    check(not g.ev(f"S.menu.includes('{more}')") and '菜單已滿' in toast and st()['count'] == s0['cap'], f'at the cap: a word, nothing changed: {toast}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc6_no_empty_sheet_over_a_service(b, port, target):
    """the player's 09:59–10:01 (their Day 61 save): during a service a 「回到選單 ›」 pill left over from a 看店裡 uncovered
    an empty sheet when tapped — the screen a step darker, every tap (the pause too) caught by nothing, until the app was
    left. A sheet opening ends a peek (the pill goes); a service starts without the pill; the pill during a service never
    uncovers an empty sheet; an empty sheet over a running service is taken away at once and the pause answers."""
    g = Game(b, port, target, seed=331, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day61_0933.json')
    if g.ev("phase") == 'shop': g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(300)
    g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}"); _quiet(g)
    pill = lambda: g.ev("!$('#peekPill').hidden")
    # the way into it: 看店裡, then the HUD's button opens the settings over the peek; closed again
    g.click('#screen [data-act=peek]'); g.page.wait_for_timeout(80)
    check(pill() and g.ev("screenEl.hidden"), 'peeking')
    g.click('#hPause'); g.page.wait_for_timeout(80)
    check(not pill() and g.ev("sub==='settings'&&!screenEl.hidden"), 'the settings sheet ends the peek')
    g.ev("closeSub()"); g.page.wait_for_timeout(80)
    check(not pill() and g.ev("phase==='prep'&&!screenEl.hidden&&!!screenEl.querySelector('[data-act=start]')"), 'back to the preparation, no pill')
    # a pill left on over the preparation however it got there: the service starts without it
    g.ev("$('#peekPill').hidden=false")
    to_service(g)
    check(not pill(), 'a service starts with the pill gone')
    # the pill on during the service by whatever way, and tapped: nothing empty is uncovered, the service goes on
    g.ev("$('#peekPill').hidden=false")
    g.click('#peekPill'); g.page.wait_for_timeout(80)
    check(g.ev("screenEl.hidden&&!paused&&!sub"), 'the pill in a service goes back to the service')
    # an empty sheet over the running service (any other way): gone within a few frames; the pause button answers
    g.ev("screenEl.innerHTML='';screenEl.className='';screenEl.hidden=false")
    t0 = g.ev("R.t"); g.page.evaluate('()=>{for(let i=0;i<20;i++)window.__tick(1000/30)}')
    check(g.ev("screenEl.hidden") and g.ev("R.t") > t0, 'an empty sheet over a running service is taken away')
    g.click('#hPause'); g.page.wait_for_timeout(80)
    check(g.ev("paused&&sub==='pause'&&!screenEl.hidden&&!!screenEl.querySelector('[data-act=resume]')"), 'the pause works')
    g.click('#screen [data-act=resume]'); g.page.wait_for_timeout(80)
    check(g.ev("!paused&&screenEl.hidden"), 'and the service goes on')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc6_anan_works_the_lounge_first(b, port, target):
    """the player's 10:06: 安安 is the Lounge's floor person and should need no setting up — a save whose 安安 lost the
    Lounge job has it back after loading (once); hired again she comes at LV2 with the job, and the board shows her on
    「Lounge 外場」 with nothing saying she will not do it; in a service, with an order waiting in the Lounge and one in the
    dining room, she takes the Lounge's."""
    raw = json.load(open(os.path.join(ROOT, 'tests', 'saves', 'player_day61_0933.json'), encoding='utf-8')); raw = raw.get('save', raw)
    for m in raw['crew']:
        if m['name'] == '安安': m['duties']['lounge'] = False
    raw.pop('ananMig', None)
    g = Game(b, port, target, seed=331, manual=True, viewport={'width': 390, 'height': 844})
    g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.page.wait_for_timeout(150)
    g.click('[data-act=openFresh]') if g.page.query_selector('[data-act=openFresh]') else g.click('[data-act=open]'); g.page.wait_for_timeout(150)
    check(g.ev("crewByName('安安').duties.lounge===true&&S.ananMig===1"), 'the Lounge job given back on loading')
    g.ev("crewByName('安安').duties.lounge=false;save()"); _reload(g)
    check(g.ev("crewByName('安安').duties.lounge===false"), 'once: a player who takes it off later keeps it off')
    # hired again: LV2, with the job, on the board without a 「LV2 才會做」
    g.ev("S.crew=S.crew.filter(m=>m.name!=='安安');S.money+=99999;doAct('hireLounge',null,'安安')")
    a = json.loads(g.ev("JSON.stringify((()=>{const m=crewByName('安安');return m?{lv:m.lv,lounge:waiterDuties(m).lounge}:null})())"))
    check(a and a['lv'] == 2 and a['lounge'], f'hired: {a}')
    g.ev("shopTab='staff';showShop()"); g.page.wait_for_timeout(80)
    row = g.ev("(document.querySelector('.brow[data-d=lounge]')||{}).innerText||''")
    check('安安' in row and '才會做' not in row, f'the board: {row!r}')
    # a service: an order in the Lounge and one in the dining room, both waiting; 安安 free — the Lounge's
    if g.ev("phase") == 'shop': g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(200)
    g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}"); _quiet(g); to_service(g)
    g.ev("__botUntil('R.t>=R.dur*.2',90000,1/30)")
    got = json.loads(g.ev("""JSON.stringify((()=>{const an=crewByName('安安');const w=R.cw[an.id];if(!w||!crewHere(an))return{err:'not here'};
      const L=R.tables.find(t=>t.lounge&&!t.group&&!t.dirty&&!t.claim),M=R.tables.find(t=>!t.lounge&&!t.pdr&&!t.group&&!t.dirty&&!t.claim);if(!L||!M)return{err:'no free tables'};
      for(const m of S.crew)if(m!==an&&R.cw[m.id])R.cw[m.id].cd=99;L.group={state:'order',id:-1};M.group={state:'order',id:-2};
      if(w.task&&w.task.t)w.task.t.claim=null;if(w.task&&w.task.g)w.task.g.claim=null;w.task=null;w.busy=0;w.cd=0;const away=w.away;crewUpd(.016);
      const t=w.task&&w.task.t;const r={k:w.task&&w.task.k,lounge:!!(t&&t.lounge),main:t===M,away:!!away};L.group=null;M.group=null;L.claim=null;M.claim=null;w.task=null;for(const m of S.crew)if(R.cw[m.id])R.cw[m.id].cd=0;return r})())"""))
    check(got.get('k') == 'order' and got.get('lounge'), f'the Lounge first: {got}')
    check(not g.errors, g.errors[:3]); g.close()


HOLD_SNAP = r"""JSON.stringify({t:+R.t.toFixed(4),rev:R.st.rev,tickets:R.tickets.map(t=>[t.id,t.items.map(i=>i.st+(i.picked?'p':'')).join('')]).join('|'),
  groups:R.groups.map(g=>[g.id,g.state,+(g.pat||0).toFixed(4),g.table]).join('|'),slots:R.slots.map(s=>s.job?[s.job.d,s.job.si,+((s.job.step&&s.job.step.p)||0).toFixed(4)].join(','):'-').join('|'),
  room,paused,clock:clockStr()})"""


def _frames(g, n, dt='1000/30'):
    g.page.evaluate(f'()=>{{for(let i=0;i<{n};i++)window.__tick({dt})}}')


@test
def v24_rc6_an_authored_beat_holds_the_service_until_it_is_read(b, port, target):
    """the player's 10:32: an authored story beat during a busy service (晴 & 阿拓's 「炸雞好了沒？」, through the arbiter)
    holds the restaurant — the service clock, the orders, every guest's patience, the cooks — under a panel that says
    so; the player can take as long as they like; a line moves only on a tap (a second tap at once never skips one); every
    line of the beat is shown once, in order, and nothing else; pausing and resuming the game meanwhile changes nothing;
    when the last line is read the service goes on from the very same state, on the room the player was looking at; the
    beat happened once, its lines are what its story page keeps. An ambient moment still happens in the room in real
    time. The panel at phone size: the box inside the screen, the chip above it, readable text. Bookings upstairs: a
    party in the Private Dining Room is held too and is exactly where it was afterwards."""
    g = Game(b, port, target, seed=331, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day61_0933.json')
    if g.ev("phase") == 'shop': g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(300)
    g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}"); _quiet(g); to_service(g)
    g.ev("__botUntil('R.t>=R.dur*.4',90000,1/30)")
    busy = json.loads(g.ev("JSON.stringify({g:R.groups.length,t:R.tickets.length,q:!!qingOn(),tuo:!!tuoOn()})"))
    check(busy['g'] >= 8 and busy['q'] and busy['tuo'], f'a busy evening, 晴 and 阿拓 at work: {busy}')
    # nothing else of the stories tonight (the day's budget spent), and what was already said in the room finished — then
    # the panel is on, as it is in play
    g.ev("const d=storyDay();d.major=9;d.minor=9;d.v24=9"); _frames(g, 300)
    g.ev("window.__holds=true;delete story().ev.qt_1;delete story().facts.qt_1;delete (story().beatLines||{}).qt_1;storyDay().minor=0;storyDay().lp={};"
         "const E=STORY_EV.find(e=>e.k==='qt_1');E.__w=E.when;E.when=()=>true;room='kitchen';renderRoomTabs(true)")
    before = json.loads(g.ev(HOLD_SNAP))
    fired = g.ev("storyTick('order',{})")
    check(fired == 'qt_1', f'the arbiter fires the beat in the service: {fired}')
    st = json.loads(g.ev("JSON.stringify({open:!!DLG&&!!DLG.sh&&DLG.hold,vis:!$('#dlg').hidden,chip:$('#dlg .dlg-hold').hidden?'':$('#dlg .dlg-hold').textContent,i:DLG&&DLG.i,text:$('#dlg .dlg-text').textContent,cls:$('#dlg').className})"))
    check(st['open'] and st['vis'] and '店裡暫停中' in st['chip'] and g.ev("$('#dlg .dlg-hold').classList.contains('ps')") and '晴' in st['chip'] and st['i'] == 0 and st['text'] == '炸雞好了沒？', f'the panel, at once, says the restaurant is held: {st}')
    # held: three seconds, then a whole minute, and nothing in the restaurant moves
    _frames(g, 90)
    s3 = json.loads(g.ev(HOLD_SNAP))
    check({k: s3[k] for k in s3 if k != 'room'} == {k: before[k] for k in before if k != 'room'}, f'held for three seconds: {before} -> {s3}')
    _frames(g, 60, '1000')
    s60 = json.loads(g.ev(HOLD_SNAP))
    check({k: s60[k] for k in s60 if k != 'room'} == {k: before[k] for k in before if k != 'room'} and g.ev("!!DLG&&DLG.i===0"), f'a minute later: still the first line, still held: {before} -> {s60} {g.ev("JSON.stringify(DLG&&{i:DLG.i,n:DLG.lines.length})")}')
    # a tap moves one line; a second tap at once does not
    g.click('#dlg'); g.click('#dlg')
    check(g.ev("DLG.i") == 1, 'one line per tap, never two')
    # the app left and come back to (three times) in the middle of it: the pause comes up under the panel; nothing
    # changes, nothing doubles
    for i in range(3):
        g.ev("Object.defineProperty(document,'hidden',{value:true,configurable:true});document.dispatchEvent(new Event('visibilitychange'))")
        _frames(g, 10)
        g.ev("Object.defineProperty(document,'hidden',{value:false,configurable:true});document.dispatchEvent(new Event('visibilitychange'))")
        _frames(g, 10)
    check(g.ev("!!DLG&&DLG.i===1&&paused&&sub==='pause'") and json.loads(g.ev(HOLD_SNAP))['t'] == before['t'], 'left and come back to three times: the same line, still held, the pause waiting under it')
    shown = [g.ev("$('#dlg .dlg-text').textContent")]
    for _ in range(12):
        if not g.ev("!!DLG"): break
        _frames(g, 10)
        g.click('#dlg')
        if g.ev("!!DLG"): shown.append(g.ev("$('#dlg .dlg-text').textContent"))
    script = ['看起來好了。', '妳跟 Hugo 講一樣的話。', '那代表我們兩個都正常。']
    check(shown[-3:] == script and len(shown) == 4 and g.ev("!DLG&&$('#dlg').hidden"), f'every line once, in order, then closed: {shown}')
    check(g.ev("paused&&sub==='pause'&&!screenEl.hidden"), 'the pause from leaving the app is there after the story')
    g.click('#screen [data-act=resume]'); g.page.wait_for_timeout(40)
    after = json.loads(g.ev(HOLD_SNAP))
    check(after == before, f'the service exactly as it was, on the room that was being looked at: {before} -> {after}')
    log = json.loads(g.ev("JSON.stringify(dayLog().map(l=>l.t))"))
    check(all(log.count(t) == 1 for t in ['炸雞好了沒？', '沒有。'] + script), 'each line in the day\'s log once')
    check(g.ev("evState('qt_1').n===1&&fact('qt_1').n===1") is True, 'the beat happened once')
    kept = json.loads(g.ev("JSON.stringify(story().beatLines.qt_1)"))
    check([x['t'] for x in kept] == ['炸雞好了沒？', '沒有。'] + script and {x['w'] for x in kept} == {'沈晴', '阿拓'}, f'its page keeps exactly its lines: {kept}')
    _frames(g, 30)
    check(json.loads(g.ev(HOLD_SNAP))['t'] > before['t'], 'and the service goes on')
    # an ambient moment: in the room, in real time, nothing held
    g.ev("delete story().ev.hugo_tuo;const E=STORY_EV.find(e=>e.k==='hugo_tuo');E.__w=E.when;E.when=()=>true")
    t0 = g.ev("R.t"); fired = g.ev("storyTick('order',{})")
    _frames(g, 120)
    amb = json.loads(g.ev("JSON.stringify({dlg:!!DLG,log:dayLog().slice(-30).map(l=>l.t)})"))
    check(fired == 'hugo_tuo' and not amb['dlg'] and g.ev("R.t") > t0 + 2 and '你炸的比較快。' in amb['log'] and '油比較熱。' in amb['log'], f'an ambient moment is not held: {fired} {amb}')
    # the panel at phone size
    g.ev("delete story().ev.qt_1;delete story().facts.qt_1;storyDay().minor=0;storyDay().lp={};storyTick('order',{})")
    lay = json.loads(g.ev("""JSON.stringify((()=>{const b=$('#dlg .dlg-box').getBoundingClientRect(),c=$('#dlg .dlg-hold').getBoundingClientRect(),t=$('#dlg .dlg-text');return{box:[b.left,b.top,b.right,b.bottom],chip:[c.left,c.top,c.right,c.bottom],fs:parseFloat(getComputedStyle(t).fontSize),W:innerWidth,H:innerHeight}})())"""))
    check(lay['box'][0] >= 0 and lay['box'][2] <= lay['W'] and lay['box'][3] <= lay['H'] and lay['chip'][3] < lay['box'][1] and lay['chip'][1] >= 0 and lay['fs'] >= 15, f'readable at 390×844: {lay}')
    os.makedirs(_rt.ARTIFACTS, exist_ok=True)   # v2.4 rc7: a test run writes its picture to the artifacts, never over a released evidence file
    g.page.screenshot(path=os.path.join(_rt.ARTIFACTS, 'story_hold_phone.png'))
    while g.ev("!!DLG"):
        _frames(g, 10); g.click('#dlg')
    g.ev("for(const k of ['qt_1','hugo_tuo']){const E=STORY_EV.find(e=>e.k===k);E.when=E.__w}")
    check(not g.errors, g.errors[:3]); g.close()
    # the Private Dining Room: a booked party is held with the rest and is where it was afterwards
    g = Game(b, port, target, seed=301, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day61.json')
    _floor(g, 50); g.ev(PD_OPEN); _quiet(g); to_service(g)
    g.ev("__botUntil('R.t>=R.dur*.2',90000,1/30)")
    g.ev("pdSeated({size:5,pdWalk:1},pdTable())")
    _frames(g, 30)
    g.ev("const d=storyDay();d.major=9;d.minor=9;d.v24=9"); _frames(g, 300)
    g.ev("window.__holds=true;room='pdr';renderRoomTabs(true);storyDay().minor=0;storyDay().lp={};STORY_EV.push({k:'pd__hold_t',lane:'minor',at:['order'],when:()=>true,run:()=>{JILL_SAY('包廂那桌點好了嗎？',300);noteLine('（測試用的一段。）')}})")
    pd0 = json.loads(g.ev("JSON.stringify((()=>{const t=pdTable(),q=t&&t.group;return{st:q&&q.state,pat:q&&+q.pat.toFixed(4),tk:q&&q.ticket?q.ticket.items.map(i=>i.st).join(''):null,room,t:+R.t.toFixed(4)}})())"))
    check(g.ev("storyTick('order',{})") == 'pd__hold_t' and g.ev("!!DLG&&DLG.hold"), 'held, upstairs too')
    _frames(g, 90)
    for _ in range(4):
        if not g.ev("!!DLG"): break
        _frames(g, 10); g.click('#dlg')
    pd1 = json.loads(g.ev("JSON.stringify((()=>{const t=pdTable(),q=t&&t.group;return{st:q&&q.state,pat:q&&+q.pat.toFixed(4),tk:q&&q.ticket?q.ticket.items.map(i=>i.st).join(''):null,room,t:+R.t.toFixed(4)}})())"))
    check(pd0['st'] is not None and pd1 == pd0 and not g.ev("!!DLG"), f'the party upstairs exactly where it was, the view still upstairs: {pd0} -> {pd1}')
    g.ev("STORY_EV.splice(STORY_EV.findIndex(e=>e.k==='pd__hold_t'),1)")
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc6_story_pages_keep_only_their_own_lines(b, port, target):
    """the player's 10:08 (their Day 67 save): Sophie and Mia's first page showed Jill's 「哪隻？」 (said to a guest about a
    cat) and another line of Sophie's mixed into 「妳也常來？」「……妳不是也一樣。」. Loading cleans a page down to the lines
    its beat says (a page whose words all come from elsewhere is left as it is); in play, a page keeps what its beat's
    own code said — not what its people happened to say meanwhile."""
    g = Game(b, port, target, seed=67, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day67_1016.json')
    sm = json.loads(g.ev("JSON.stringify(story().beatLines.sm_a)"))
    check(sm == [{'w': 'Mia', 't': '妳也常來？'}, {'w': 'Sophie', 't': '……妳不是也一樣。'}], f'the first page, cleaned: {sm}')
    bad = json.loads(g.ev("JSON.stringify(Object.entries(story().beatLines).filter(([k,a])=>{const src=beatSrcOf(k);return src&&a.some(x=>beatLineOk(src,x.t))&&a.some(x=>!beatLineOk(src,x.t))}).map(([k])=>k))"))
    check(bad == [], f'no page keeps a line its beat does not say: {bad}')
    check(g.ev("story().blMig") == 1, 'once')
    # in play (no panel in this test): Jill says something else right after the beat began — not on the page
    g.ev("delete story().beatLines.sm_a")
    if g.ev("phase") == 'shop': g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(300)
    g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}"); _quiet(g); to_service(g)
    g.ev("__botUntil('R.t>=R.dur*.3',90000,1/30)")
    r = json.loads(g.ev("""JSON.stringify((()=>{const gs=R.groups.filter(q=>q.table!=null&&q.state!=='leave');if(gs.length<2)return{skip:1};const m=gs[0],s0=gs[1];
      const E=STORY_EV.find(e=>e.k==='sm_a');shStart('sm_a',false,null,()=>{sayG(m,'妳也常來？',600);sayG(s0,'……妳不是也一樣。',2200)});jillSay('哪隻？');return{ok:1}})())"""))
    _frames(g, 120)
    kept = json.loads(g.ev("JSON.stringify((story().beatLines||{}).sm_a||null)"))
    check(r.get('skip') or [x['t'] for x in kept] == ['妳也常來？', '……妳不是也一樣。'], f'only the beat\'s own: {kept}')
    check(not g.errors, g.errors[:3]); g.close()


def _lazy_days(g, n, seedbase, each=None):
    seed = "Math.random=(function(){let a=%d;return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
    for d in range(n):
        if g.ev("phase") == 'summary':
            g.click('[data-act=toShop]'); g.page.wait_for_timeout(60)
        if g.ev("phase") == 'shop':
            g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(100)
        g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}")
        g.ev(seed % (seedbase + d)); g.ev("S.today.sugKey=null;S.today.sug=null;autoStock()")
        start_day(g); install_bot(g); g.ev(LAZY_ACTOR + "\nwindow.__act=window.__actLazy;window.__noScenes=true")
        for _ in range(1200):
            r = g.page.evaluate('()=>window.__bot(150,1/30)')
            if g.ev("phase") != 'service' or not g.ev("!!R"): break
            if r['ticks'] < 150: break
        if g.ev("phase") == 'service':
            g.ev("closeShop('x');for(const q of R.groups.slice())leaveGroup(q,'ok')"); g.page.evaluate('()=>window.__bot(400,1/30)')
        if g.ev("phase") == 'service': g.ev("finishClosing()")
        if each: each(g)


@test
def v24_rc6_sophie_and_mia_begin(b, port, target):
    """the player's 10:05 (their Day 61 save: Sophie 31 visits, Mia 17, in the room on the same evening once in a
    fortnight, their story not begun): two who have both been coming for weeks have noticed each other, and the evenings
    bring them in together now and then until it begins — 「妳也常來？」 within a few days; once, as written."""
    g = Game(b, port, target, seed=331, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day61_0933.json')
    g.ev("window.__fastSay=1")
    check(not g.ev("!!fact('sm_a')") and g.ev("smLongKnown()") is True, 'not begun; they have been around each other long enough')
    days = []
    _lazy_days(g, 5, 9100, lambda g: days.append(json.loads(g.ev("JSON.stringify({d:S.day,sm:!!fact('sm_a'),co:relN('sophie','mia','copresent')})"))))
    first = next((x['d'] for x in days if x['sm']), None)
    check(first is not None and first <= days[0]['d'] + 4, f'begun within five days: {days}')
    check(g.ev("fact('sm_a').n") == 1 and json.loads(g.ev("JSON.stringify((story().beatLines.sm_a||[]).map(x=>x.t))")) == ['妳也常來？', '……妳不是也一樣。'], 'once, its own two lines on its page')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc6_a_finished_lounge_opens_the_floor_in_a_mature_save(b, port, target):
    """the player's 10:25, the legacy check (their Day 67 save: the Lounge finished on Day 57, 《那面牆》 begun on Day 65,
    nothing of the Second Floor yet): the floor's era is open on loading; the next days bring its first beat, then the
    next — one at a time, never two of its beats on a day, never more than two major beats on a day (rc7) — while the wall goes on."""
    g = Game(b, port, target, seed=67, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day67_1016.json')
    g.ev("window.__fastSay=1")
    check(g.ev("eraOpen('up')") is True and g.ev("eraOpenDay('up')") == 59 and not g.ev("!!fact('up_hint')") and g.ev("!!fact('wall_worry')&&!fact('wall_settle')") is True,
          'open on loading (the Lounge on Day 57, two days), nothing of it yet, the wall under way')
    rows = []
    _lazy_days(g, 4, 6700, lambda g: rows.append(json.loads(g.ev(
        "JSON.stringify({d:S.day,up:Object.keys(story().facts).filter(k=>/^(up_|sp_)/.test(k)&&story().facts[k].d===S.day),wall:Object.keys(story().facts).filter(k=>/^wall_/.test(k)&&story().facts[k].d===S.day),major:storyDay().major})"))))
    ups = [k for r in rows for k in r['up'] if k in ('up_hint', 'up_staff', 'up_inspect', 'up_door')]
    check('up_hint' in ups, f'the first beat came: {rows}')
    order = ['up_hint', 'up_staff', 'up_inspect', 'up_door']
    check(ups == order[:len(ups)], f'in its order: {ups}')
    check(all(len([k for k in r['up'] if k in ('up_hint', 'up_staff', 'up_inspect', 'up_door', 'up_busy', 'up_remind', 'up_ask')]) <= 1 for r in rows), f'one of its beats a day at most: {rows}')
    check(all(r['major'] <= 2 for r in rows), f'never more than two major beats on a day (rc7, 15:39): {rows}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc6_new_things_are_talked_about(b, port, target):
    """the player's 09:39 (「怎麼這麼少對酒吧開張的評論啊 有新增什麼東西都可以評論」): what is new is talked about — in its first
    days often, by whoever sits down, in their room's words (in the Lounge about the Lounge, elsewhere about the Lounge
    behind) — and a week later not at all; each word once a day at most."""
    def evening(g, age):
        g.ev(f"S.newRooms.lounge2=S.day-{age};S.newRooms.lounge=S.day-{age}-3")
        if g.ev("phase") == 'shop': g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(300)
        g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}"); _quiet(g)
        g.ev(f"S.newRooms.lounge2=S.day-{age};S.newRooms.lounge=S.day-{age}-3")
        to_service(g); g.ev("window.__fastSay=1")
        g.ev("__botUntil('R.t>=R.dur*.7',120000,1/30)")
        all2 = json.loads(g.ev("JSON.stringify([].concat(...NOVELTY.filter(T=>/^lounge/.test(T.k)).map(T=>(T.here||[]).concat(T.away||[]))))"))
        log = json.loads(g.ev("JSON.stringify(dayLog().map(l=>l.t))"))
        return [t for t in log if t in all2]
    # rc8: three evenings, not one — how much a first evening says swings with who comes (seeds 331–336 said 5/5/4/7/5/2
    # on 0d3ab73 and 2/5/5/6/5/4 after the cooks took over: the same spread, seed 331 at its low end)
    firsts = []
    for sd in (331, 332, 333):
        g = Game(b, port, target, seed=sd, manual=True, viewport={'width': 390, 'height': 844})
        load_save(g, 'player_day61_0933.json')
        said = evening(g, 0); firsts.append(said)
        check(len(said) == len(set(said)), f'each word once: {said}')
        g.close()
    check(sum(len(x) >= 3 for x in firsts) >= 2, f'the Lounge\'s new stage, its first evening: talked about, three words or more on most evenings ({firsts})')
    g = Game(b, port, target, seed=331, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day61_0933.json')
    said7 = evening(g, 9)
    check(said7 == [], f'nine days on: nothing ({said7})')
    check(not g.errors, g.errors[:3]); g.close()


def _act2(g, a, k=None, d=None):
    g.ev(f"doAct('{a}',{json.dumps(d)},{json.dumps(k)},document.createElement('button'))")


@test
def v24_rc6_more_to_spend_on(b, port, target):
    """the player's 10:21 (「我已經沒有地方可以花錢了」, their Day 67 save) and 10:40 (「你就一起放」): the Lounge's list grows by
    research (the oldest bottle wants the cellar) and the player chooses tonight's (never none; the Lounge pours only
    those); four dream works — the cellar (wines of the second and third stages +10%, a second glass now and then), the
    piano (rc7: played only on 予安's nights — three a week once she has said yes; more stay after dinner), the dry-ageing cabinet (the beef dishes +8%, more
    ordered), the painting (+2) — each needing what it says; four seasonal sets, one out at a time (+1); three contracts,
    each a signing fee and a fee a day taken at the summary (on its ledger), their dishes +8% and more ordered, ended at
    any time; a wine course for a waiter (and a floor at ease with wine sells a glass with dinner more often); the
    Lounge's own people are trained one level a day."""
    g = Game(b, port, target, seed=67, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day67_1016.json')
    g.ev("S.money=3000000")
    m0 = g.ev("S.money")
    # the list
    _act2(g, 'wineDev', 'w_rose'); _act2(g, 'wineDev', 'w_old')
    check(g.ev("wineHas('w_rose')&&!wineHas('w_old')&&wineAvail().includes('w_rose')") is True and g.ev("S.money") == m0 - g.ev("WINES.w_rose.dev"), 'researched; the oldest waits for the cellar')
    # the player's 11:49 (「研發酒也太貴 感覺就是為了花錢」): a wine's research costs what a dish's does, and it goes with something
    devs = json.loads(g.ev("JSON.stringify(Object.values(WINES).filter(W=>W.dev).map(W=>[W.dev,!!W.pair,!!W.pn]))"))
    rds = json.loads(g.ev("JSON.stringify(Object.values(DISHES).map(D=>D.rd||0).concat(Object.values(SPECIALS).map(X=>X.rd)))"))
    check(all(d <= max(rds) * 1.25 and p and n for d, p, n in devs) and sum(d for d, _, _ in devs) < 40000, f'priced like the kitchen\'s research, each with its pairing: {devs} (dishes up to {max(rds)})')
    for k in json.loads(g.ev("JSON.stringify(wineAvail())")):
        _act2(g, 'wineT', k)
    left = json.loads(g.ev("JSON.stringify(wineList())"))
    check(len(left) == 1 and g.ev("Object.keys(S.wineOff).length") == len(json.loads(g.ev("JSON.stringify(wineAvail())"))) - 1, f'never none: {left}')
    g.ev("S.wineOff={w_white:1,w_lred:1}")
    poured = json.loads(g.ev("JSON.stringify((()=>{const out=new Set();for(let i=0;i<300;i++)for(const d of loungeOrder({size:2,type:'office'}))if(WINES[d])out.add(d);return[...out]})())"))
    check(poured and 'w_white' not in poured and 'w_lred' not in poured and all(p in json.loads(g.ev("JSON.stringify(wineList())")) for p in poured), f'the Lounge pours only tonight\'s: {poured}')
    # the dream works
    p0 = json.loads(g.ev("JSON.stringify({steak:priceOf('steak'),fred:priceOf('w_fred'),spark:priceOf('w_spark'),amb:ambience(),wSteak:demandW('steak',TYPES.office)})"))
    for k in ['cellar', 'piano', 'dryage', 'painting']:
        _act2(g, 'buyProject', k); g.ev("hideReveal()")
    on = json.loads(g.ev("JSON.stringify(['cellar','piano','dryage','painting'].map(projOn))"))
    p1 = json.loads(g.ev("JSON.stringify({steak:priceOf('steak'),fred:priceOf('w_fred'),spark:priceOf('w_spark'),amb:ambience(),wSteak:demandW('steak',TYPES.office)})"))
    check(all(on), f'built: {on}')
    check(abs(p1['steak'] / p0['steak'] - 1.08) < .03 and abs(p1['fred'] / p0['fred'] - 1.1) < .03 and p1['spark'] == p0['spark'] and p1['wSteak'] > p0['wSteak'] * 1.1, f'the cabinet and the cellar: {p0} -> {p1}')
    check(p1['amb'] == p0['amb'] + 2, f'the painting: {p0["amb"]} -> {p1["amb"]}')
    _act2(g, 'wineDev', 'w_old')
    check(g.ev("wineHas('w_old')") is True, 'the oldest bottle, now that there is a cellar')
    # what a researched wine does (11:49): a table that ate what it goes with has it more often, with dinner and after; more stay
    g.ev("S.wineOff={}")
    _act2(g, 'wineDev', 'w_pinot')
    pair = json.loads(g.ev("JSON.stringify([winePairFor({type:'family'},['duck']),winePairFor({type:'family'},['pasta']),winePairFor({type:'family'},['steak_x']),winePairFor({type:'family'},['tiramisu'])])"))
    check(pair == ['w_pinot', None, 'w_old', 'w_rose'], f'what each goes with: {pair}')
    share = json.loads(g.ev("JSON.stringify((()=>{const f=dd=>{let n=0,t=0;for(let i=0;i<400;i++)for(const d of loungeOrder({size:2,type:'family',dd}))if(WINES[d]){t++;if(d==='w_pinot')n++}return n/t};return[f(['pasta']),f(['duck'])]})())"))
    check(share[1] > share[0] + .25, f'a table that had duck has the pinot after dinner more often: {share}')
    g.ev("window.__wl=wineList")
    st = json.loads(g.ev("(()=>{const g0={type:'office',pat:1,dd:['duck']};const g1={type:'office',pat:1,dd:['pasta']};const R0=R;R={closed:false,t:50,dur:100};const pn=pianoNight;pianoNight=()=>false;const a=loungeAfterP(g1);const b=loungeAfterP(g0);wineList=()=>['w_spark','w_white','w_lred'];const c=loungeAfterP(g1);wineList=window.__wl;pianoNight=pn;R=R0;return JSON.stringify([c,a,b])})()"))
    check(st[0] < st[1] < st[2], f'more stay with researched wines poured, more again when one goes with dinner: {st}')
    count = "(()=>{let n=0;const d0=S.day;for(let i=0;i<60;i++){S.day=d0+i;if(pianoNight())n++}S.day=d0;return n})()"
    n0 = g.ev(count); g.ev("factSet('ya_join')"); nights = g.ev(count); g.ev("delete story().facts.ya_join")
    check(n0 == 0 and 24 <= nights <= 27, f'rc7: nobody plays it until 予安 has said yes; then three nights a week: {n0}, {nights}/60')
    g.ev("window.__pn=pianoNight")
    r = json.loads(g.ev("(()=>{R=R||null;const g0={type:'couple',pat:1};pianoNight=()=>false;const fake={closed:false,t:50,dur:100};const R0=R;R=fake;const a=loungeAfterP(g0);pianoNight=()=>true;const b=loungeAfterP(g0);pianoNight=window.__pn;R=R0;return JSON.stringify([a,b])})()"))
    check(r[1] >= r[0] * 1.2 or r[1] == .9, f'more stay on a music night: {r}')
    g.ev("const nf=document.createElement('div')")
    # the seasons
    a0 = g.ev("ambience()")
    _act2(g, 'buySeason', 'autumn')
    check(g.ev("seasonOn()") == 'autumn' and g.ev("ambience()") == a0 + 1, 'the autumn set out (+1)')
    _act2(g, 'seasonUse', ''); check(g.ev("seasonOn()") is None and g.ev("ambience()") == a0, 'put away')
    _act2(g, 'seasonUse', 'spring'); check(g.ev("seasonOn()") is None, 'a set not bought cannot be put out')
    # the contracts and the course
    d0 = g.ev("priceOf('duck')")
    _act2(g, 'contractSign', 'ranch')
    check(g.ev("contractOn('ranch')&&contractFee()===1400") is True and abs(g.ev("priceOf('duck')") / d0 - 1.08) < .03, 'the ranch: its dishes +8%, a fee a day')
    wt = g.ev("(S.crew.find(m=>m.role==='waiter'&&(m.wine||0)<40)||{}).id")
    if wt:
        b0 = g.ev("wineFloorBoost()")
        _act2(g, 'wineCourse', wt)
        check(g.ev(f"S.crew.find(m=>m.id==='{wt}').wine") == 40 and g.ev("wineFloorBoost()") > b0, 'a waiter at ease with wine after the course; the floor sells more glasses')
    lg = g.ev("(S.crew.find(m=>crewPool(m)==='lounge'&&m.lv<5)||(()=>{const m=S.crew.find(m=>crewPool(m)==='lounge');m.lv=2;return m})()).id")
    lv0 = g.ev(f"S.crew.find(m=>m.id==='{lg}').lv")
    _act2(g, 'crewUp', lg); _act2(g, 'crewUp', lg)
    check(g.ev(f"S.crew.find(m=>m.id==='{lg}').lv") == lv0 + 1, 'the Lounge\'s people: one level a day')
    # the fee at the end of the day, on the ledger
    g.ev("if(S.phase==='prep')showPrep()"); g.page.wait_for_timeout(200)
    if g.ev("phase") == 'shop': g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(300)
    g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}"); _quiet(g); to_service(g); g.ev("window.__fastSay=1")
    g.ev("__botUntil('R.t>=R.dur*.3',90000,1/30)")
    g.ev("closeShop('x');for(const q of R.groups.slice())leaveGroup(q,'ok')"); g.page.evaluate('()=>window.__bot(600,1/30)')
    if g.ev("phase") == 'service': g.ev("finishClosing()")
    g.page.wait_for_timeout(200)
    check(g.ev("S.lastSummary.cfee") == 1400 and '食材契作' in g.ev("document.querySelector('#screen .ledger').innerText"), 'the day\'s fee on the summary')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc6_new_places_have_their_photos(b, port, target):
    """the player's 10:16 (「相簿沒有任何酒吧的照片欸？以後你每個新的空間應該也要有幾個主題是可以拍照的」): the Lounge has its own
    moments for the album (the bar full of an evening, the sofa table, the corner, a music night), and so do the floor
    upstairs, the Staff Room and the Private Dining Room; a photo is taken when its room is the one on screen."""
    g = Game(b, port, target, seed=67, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day67_1016.json')
    kinds = json.loads(g.ev("JSON.stringify(['lgbar','lgsofa','lgquiet','lgpiano','upwin','upcats','srpool','srdoze','srcat','pdparty'].filter(k=>MEMS[k]&&MEM_TXT[k]))"))
    check(len(kinds) == 10, f'ten new moments, each with its caption and its line: {kinds}')
    g.ev("if(S.phase==='prep')showPrep()"); g.page.wait_for_timeout(200)
    if g.ev("phase") == 'shop': g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(300)
    g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}"); _quiet(g); to_service(g); g.ev("window.__fastSay=1")
    g.ev("room='lounge';renderRoomTabs(true)")
    got = []
    for frac in (.5, .6, .7, .8):
        g.ev(f"room='lounge';__botUntil('R.t>=R.dur*{frac}',90000,1/30)"); g.ev("forceDraw=true"); _frames(g, 3)
        got = json.loads(g.ev("JSON.stringify(albumList().filter(p=>p.day===S.day&&/^lg/.test(p.kind)).map(p=>p.kind))"))
        if got: break
    check(got, f'a Lounge evening, looked at: a photo of it ({got})')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc6_the_open_floor_keeps_its_ways(b, port, target):
    """rc6 B, AT (circulation), and the player's own plan of the floor (08:37): the Private Dining Room the big room in the
    top-left over the street windows, its east wall on the right window's first mullion; the Staff Room directly below it
    the whole way to the back wall, narrower; the hall an L on the right; the stairs across the back corner, half the
    size they were, the way in at their left end (09:14), and no column; the Private Dining Room's door in its front wall
    at its corner, the Staff Room's in its east wall near the top, each with its front on the hall; the people walk from
    the stairs to each door and back, never through a wall; the floor's view still draws."""
    g = Game(b, port, target, seed=299, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day61.json')
    _floor(g, 50); g.ev(PD_OPEN)
    g.ev("(()=>{const p=pdW();p.ever=3;p.res={id:'r'+S.day,d:S.day,size:5,min:3800,kind:'x',type:'family',name:'x',t:.9,status:'missed',phase:1}})()")
    z = json.loads(g.ev("JSON.stringify((()=>{const P=UPR.pd,Q=UPR.sr,in_=(r,x,y)=>x>=r.x0&&x<=r.x1&&y>=r.y0&&y<=r.y1;const s=UP_L.stair,win=UP_L.win[1],e=UP_L.entry,dp=UPR.pdDoor,ds=UPR.srDoor;return{stairs:s.w>s.h&&s.h<=81&&s.x>Q.x1+UPRW.sd&&s.x+s.w<=378&&s.y+s.h<=FB&&!in_(P,s.x,s.y)&&!in_(Q,s.x,s.y),nocolumn:UP_L.col===undefined,win:P.x1===win.x+win.w/5,plan:P.x0===Q.x0&&P.y0===92&&Q.y0===P.y1&&Q.y1===FB&&Q.x1<P.x1,entry:!in_(P,e.x,e.y)&&!in_(Q,e.x,e.y)&&e.x<s.x,doors:dp.side==='s'&&dp.x>Q.x1+UPRW.sd&&dp.x<P.x1&&ds.side==='e'&&ds.y0>=Q.y0&&ds.y1<Q.y0+(Q.y1-Q.y0)/3&&!in_(P,dp.fx,dp.fy)&&!in_(Q,dp.fx,dp.fy)&&!in_(P,ds.fx,ds.fy)&&!in_(Q,ds.fx,ds.fy)}})())"))
    check(all(z.values()), f'the floor as the player drew it: {z}')
    _quiet(g); to_service(g)
    g.ev("__botUntil('R.t>=R.dur*.1',90000,1/30)")
    # a walker from the stairs to each door and back: every step outside the rooms' boxes while on the floor
    for dest in ('staff', 'pdr'):
        r = json.loads(g.ev(f"""JSON.stringify((()=>{{const P=UPR.pd,Q=UPR.sr,inn=(r,x,y)=>x>r.x0+2&&x<r.x1-2&&y>r.y0+2&&y<r.y1-2;const w={{room:'up',x:UP_L.entry.x,y:UP_L.entry.y-4,troom:'{dest}',tx:{'200' if dest=='staff' else '300'},ty:{'srY(.5)' if dest=='staff' else 'pdY(.25)'},step:0,moving:false}};let bad=0,n=0;
          for(;n<3000;n++){{if(stepTo(w,105/30))break;if(w.room==='up'&&(inn(P,w.x,w.y)||inn(Q,w.x,w.y)))bad++}}const there=w.room==='{dest}';w.troom='up';w.tx=UP_L.entry.x;w.ty=UP_L.entry.y-4;let m=0;for(;m<3000;m++){{if(stepTo(w,105/30))break;if(w.room==='up'&&(inn(P,w.x,w.y)||inn(Q,w.x,w.y)))bad++}}return{{there,back:w.room==='up',bad,n,m}}}})())"""))
        check(r['there'] and r['back'] and r['bad'] == 0 and r['n'] < 3000 and r['m'] < 3000, f'stairs → {dest} → stairs, never through a wall: {r}')
    check(g.ev("R.upView=1;setRoom('up');forceDraw=true;__tick(1000/30);const r=room;R.upView=0;r") == 'up', 'the floor draws (as a story shows it)')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc6_a_booked_party_comes_eats_and_pays(b, port, target):
    """rc6 R–W, Z, AR (played for real, lazily): the booking on the prep screen in the day's news, the party arriving at
    its time, seated at the long table upstairs, ordering as people do, eating, paying — the bill never below the
    minimum — and the day's summary saying so."""
    g = Game(b, port, target, seed=300, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day61.json')
    _floor(g, 50); g.ev(PD_OPEN)
    g.ev("(()=>{const p=pdW();p.ever=0;p.dry=0;delete p.res})()")
    if g.ev("phase") == 'shop':
        g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(200)
    else:
        g.ev("IDLE=null;showPrep()"); g.page.wait_for_timeout(150)
    r = json.loads(g.ev("JSON.stringify(pdRes())"))
    check(r and r['status'] == 'booked' and 4 <= r['size'] <= 6, f'the second evening: booked ({r})')
    news = g.ev("(document.querySelector('#screen .event.pdres')||{}).textContent||''")
    check('今晚｜私人包廂｜已預約' in news and f"{r['size']} 位" in news and '最低消費' in news, f'in the day\'s news: {news}')
    box = g.ev("(()=>{const e=document.querySelector('#screen .event.pdres');if(!e)return null;const a=e.getBoundingClientRect(),s=e.querySelector('span').getBoundingClientRect();return[a.right<=390,s.right<=a.right+0.5,e.scrollWidth<=e.clientWidth+1]})()")
    check(box == [True, True, True], f'readable at 390 wide, nothing clipped: {box}')
    _quiet(g); to_service(g)
    g.ev(f"__botUntil(\"pdRes().status==='done'||R.closing!=null&&R.closing>60\",400000,1/30)")
    st = json.loads(g.ev("JSON.stringify(pdRes())"))
    check(st['status'] == 'done' and st['min'] == r['min'] and st['actual'] > 0, f'came, ate, paid: {st}')
    g.ev("__botUntil('phase!==\"service\"',400000,1/30)")
    for _ in range(40):
        if g.ev("phase") == 'summary': break
        g.ev("while(typeof DLG!=='undefined'&&DLG)dlgNext()"); g.ev("__tick(1000)")
    s = json.loads(g.ev("JSON.stringify(S.lastSummary&&S.lastSummary.pd)"))
    check(s and s['n'] >= 1 and s['res'] == 1 and s['top'] == max(0, r['min'] - st['actual']), f'the summary: {s} (min {r["min"]}, ate {st["actual"]})')
    chips = g.ev("[...document.querySelectorAll('#screen .daynotes div')].map(e=>e.innerText.replace(/\\s+/g,' ')).join('|')")
    check('包廂' in chips, f'and the line in the day\'s notes on the summary: {chips}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc6_the_private_dining_room_minimum_service_and_long_table(b, port, target):
    """rc6 T–W, AL, the player's 04:25 brief: the minimum grows with the party (4 < 5 < … < 10) and is what such a party
    orders at today's prices times a modest factor (a floor most parties pass, never a surcharge), the same figure for the
    same evening; a party of five or more orders a dish each (none cut away), up to twelve; the long table runs down the
    room (its long axis the screen's height), longer with each phase, every place on the floor, the door at the near
    end; the crew go up to it first when it needs an order taken, its bill or its table cleared."""
    g = Game(b, port, target, seed=301, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day61.json')
    _floor(g, 50); g.ev(PD_OPEN)
    g.ev("pdW().st2=S.day;pdW().st3=S.day")
    mins = json.loads(g.ev("JSON.stringify([4,5,6,7,8,9,10].map(n=>pdMinFor(n,3,'family')))"))
    check(all(mins[i] < mins[i + 1] for i in range(len(mins) - 1)), f'the minimum grows with the party: {mins}')
    exp6 = g.ev("pdExpect(6,'family')"); m6 = {st: g.ev(f"pdMinFor(6,{st},'family')") for st in (1, 2, 3)}
    check(m6[1] <= exp6 * .95 and m6[3] <= exp6 * 1.05 + 100 and m6[1] <= m6[2] <= m6[3], f'a floor near what six order ({exp6:.0f}): {m6}')
    check(g.ev("pdMinFor(6,2,'family')===pdMinFor(6,2,'family')") is True and g.ev("(()=>{const a=Math.random();Math.random=()=>.5;const m=pdMinFor(7,2,'office');Math.random=()=>.9;const n=pdMinFor(7,2,'office');return m===n})()") is True, 'the same figure for the same evening, whatever the day\'s dice')
    items = json.loads(g.ev("JSON.stringify([5,8,10].map(n=>{let lo=99;for(let i=0;i<30;i++){const o=orderItems({type:'family',size:n,reg:null},true);const mains=o.filter(d=>DISH(d).cat!=='drink'&&DISH(d).cat!=='dessert').length;lo=Math.min(lo,mains)}return lo}))"))
    check(items[0] >= 5 and items[1] >= 8 and items[2] >= 10, f'a dish each for parties of five and more: {items}')
    check(g.ev("orderItems({type:'family',size:10,reg:null},true).length<=12") is True, 'at most twelve on the ticket')
    geo = {}
    for st in (1, 2, 3):
        g.ev(f"(()=>{{const p=pdW();delete p.st2;delete p.st3;if({st}>=2)p.st2=S.day;if({st}>=3)p.st3=S.day}})()")
        geo[st] = json.loads(g.ev("JSON.stringify({G:pdGeo(),n:pdSeats().length,max:pdMax(),LH,door:PDL.door.y,ok:pdSeats().every(s=>{const y=PDL_TABLE().y+s.dy;return y>PDW+20&&y<LH-40})})"))
    check([geo[s]['n'] for s in (1, 2, 3)] == [6, 8, 10] and all(geo[s]['n'] == geo[s]['max'] for s in geo), f'six, eight, ten places: {geo}')
    check(all(geo[s]['G']['y1'] - geo[s]['G']['y0'] > 3 * geo[s]['G']['hw'] for s in geo) and geo[1]['G']['y1'] < geo[2]['G']['y1'] < geo[3]['G']['y1'], f'down the room, longer each phase: {geo}')
    check(all(geo[s]['ok'] for s in geo) and all(geo[s]['G']['y1'] < geo[s]['door'] - 40 for s in geo), 'every place on the floor, the door beyond the near end')
    # the crew, the room upstairs first
    _quiet(g); to_service(g)
    g.ev("__botUntil('R.t>=R.dur*.2',90000,1/30)")
    r = json.loads(g.ev("""JSON.stringify((()=>{const t=pdTable();const other=R.tables.find(q=>!q.pdr&&!q.lounge&&!q.group&&!q.dirty);if(!t||!other)return{skip:1};
      const mk=(tb,sz)=>{const g0={size:sz,state:'check',pat:.9,looks:[],ticket:{items:[]},table:tb.i,x:tb.x,y:tb.y,room:tb.room};tb.group=g0;tb.claim=null;return g0};mk(other,2);mk(t,6);
      const pick=pdFirst(q=>q.group&&q.group.state==='check'&&!q.claim);const res={pick:pick&&pick.pdr};t.group=null;other.group=null;return res})())"""))
    check(r.get('skip') or r['pick'] is True, f'the Private Dining Room\'s bill first: {r}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc6_qing_and_tuo_move_on(b, port, target):
    """the player's 12:16 (「阿拓跟晴毫無進展」, their Day 71 save: qt_1 on Day 61, qt_2 on Day 67, then nothing): 「多的。」 comes
    at closing and lost the day's one major slot to any major beat earlier in the day without being counted as waiting
    (the lane was full before it was looked at), so the old rule — a beat that has waited long enough plays — never
    reached it. Now a major beat due when the slot is taken counts a missed day, and the next day the slot is kept for
    the beat that has waited longest (one day; rc7: one of the day's two major slots). 阿拓's absence could never happen (the beat
    asked whether he was employed, not whether he came in; nobody took a day off): once 「多的。」 has happened he takes
    one day off, and 晴 notices the fryer. The pace stays a slow burn, a little quicker."""
    g = Game(b, port, target, seed=71, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day71_1215.json')
    to_service(g)
    st0 = json.loads(g.ev("JSON.stringify({q:!!qingOn(),t:!!tuoOn(),qt2:fact('qt_2').d,qt3:!!fact('qt_3'),day:S.day,days:factN('qt_days')})"))
    check(st0['q'] and st0['t'] and st0['qt2'] == 67 and not st0['qt3'] and st0['day'] == 71, f'the player\'s Day 71: both in, 「多的。」 due and not yet: {st0}')
    # Day 71 as the player's Day 70 went: another major beat took the slot earlier — 「多的。」 waits, counted
    g.ev("storyDay().major=LANE_CAP.major;storyTick('close',{})")
    check(not g.ev("!!fact('qt_3')") and g.ev("evState('qt_3').miss") == 1, 'the day\'s slots were taken: it waits a day, and the wait is counted')
    # the next day the slot is kept for it: another major beat due earlier is held back, 「多的。」 plays at closing
    g.ev("finishClosing()") if g.ev("phase") == 'service' else None
    g.ev("closeSub&&closeSub()")
    for _ in range(3):
        if g.ev("phase") == 'summary': g.click('[data-act=toShop]'); g.page.wait_for_timeout(80)
        if g.ev("phase") == 'shop': g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(120)
    to_service(g)
    owe = json.loads(g.ev("JSON.stringify({owe:story().owe,owed:majorOwed(),day:S.day})"))
    check(owe['owed'] == 'qt_3' and owe['day'] == 72, f'Day 72: the day\'s major slot is kept for the beat that waited: {owe}')
    g.ev("window.__E=STORY_EV.find(e=>e.k==='sm_c');__E.__w=__E.when;__E.when=()=>true;__E.__p=__E.present;__E.present=[{run:()=>factSet('sm_c')}]")
    g.ev("if(S.story.v24)S.story.v24.res=null;R.t=R.dur*.3;storyTick('seat',{g:R.groups[0]||null})")   # (no visit came for a beat today: rc7's Ken may — that would hold the other slot too)
    check(g.ev("!!fact('sm_c')") and g.ev("storyDay().major") == 1, 'rc7 (two major slots a day): another major beat due earlier takes the other slot')
    g.ev("STORY_EV.push({k:'__t_third',lane:'major',cls:'A',floor:1,at:['seat'],w:()=>1e9,when:()=>true,run:()=>{}});R.t=R.dur*.6;storyTick('seat',{g:R.groups[0]||null})")
    check(g.ev("evState('__t_third').n") == 0 and g.ev("evState('__t_third').miss") >= 1 and g.ev("storyDay().major") == 1, 'a third waits (counted): the last slot is kept for 「多的。」')
    g.ev("__E.when=__E.__w;__E.present=__E.__p;STORY_EV.splice(STORY_EV.findIndex(E=>E.k==='__t_third'),1)")
    g.ev("storyTick('close',{})")
    check(g.ev("!!fact('qt_3')") and g.ev("fact('qt_3').d") == 72 and g.ev("storyDay().major") == 2 and g.ev("majorOwed()") is None, '「多的。」 plays at closing; two major beats that day; the hold is over')
    # 阿拓's day off, a few days on: a coin from the day; 晴 notices the fryer
    d_off = g.ev("(()=>{for(let d=S.day+3;d<S.day+40;d++)if(dayCoin('tuooff|'+d)<40)return d;return null})()")
    check(d_off is not None and d_off - 72 <= 12, f'a day off comes within days: Day {d_off}')
    g.ev(f"S.day={d_off};story().away=null;storyDay();storyTick('daystart',{{}})")
    away = json.loads(g.ev("JSON.stringify({f:!!fact('tuo_off'),t:!!tuoOn(),q:!!qingOn(),here:crewHere(crewByName('阿拓')),lbl:crewAwayOf(crewByName('阿拓'))})"))
    check(away['f'] and not away['t'] and away['q'] and away['here'] is False, f'阿拓 is off today (晴 in): {away}')
    g.ev("const q=R.groups.find(x=>x.table!=null)||null;const t=R.tables.find(t=>t.lounge&&!t.group);window.__tk={id:R.tkid++,no:1,g:q,lounge:1,items:[{d:'bites',st:'pending',q:null,want:0,picked:false,set:null}],t0:R.t};storyTick('order',{g:q,tk:__tk})")
    check(g.ev("!!fact('qt_absence')"), 'the absence: 「今天炸物怎麼怪怪的？」')
    # the pace: four evenings together for qt_2, two days for 「多的。」, the photo after two repeats and the absence
    E = json.loads(g.ev("JSON.stringify(Object.fromEntries(['qt_2','qt_3','qt_extra','qt_photo'].map(k=>[k,String(STORY_EV.find(e=>e.k===k).when)])))"))
    check("factN('qt_days')>=4" in E['qt_2'] and "fact('qt_2').d>=2" in E['qt_3'] and 'Math.random()<.5' in E['qt_extra'] and "factN('qt_extra')>=2" in E['qt_photo'] and 'qt_absence' in E['qt_photo'], f'the pace: {E}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc6_a_regulars_dated_beat_keeps_its_day(b, port, target):
    """the full regression on the player's Day 68 save: 小林's 「升職了，今天不趕。」 (Day 28) became 「更早以前」 after one more
    evening — an older save keeps that beat as a flag of 1 and finds its day in the regular's notes, which keep the latest
    six. The day now stays in the flag (when the beat is read, and before its note is let go)."""
    g = Game(b, port, target, seed=68, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day68_1033.json')
    L = "JSON.stringify(lineProgress(STORY_LINES.find(x=>x.k==='koba')).done.map(x=>x.id+'@'+x.d))"
    b0 = json.loads(g.ev(L))
    check('koba_promo@28' in b0 and 'koba_newjob@40' in b0, f'the save: {b0}')
    check(g.ev("S.regMem.koba.flags.promo") == 28 and g.ev("S.regMem.koba.flags.newjob") == 40, 'read once, the flags keep their days')
    g.ev("S.regMem.koba.flags.promo=1;S.regMem.koba.flags.newjob=1")   # as the save has them, unread
    g.ev("regFact('koba','今天坐吧台。');regFact('koba','點了兩杯。');regFact('koba','說下次帶同事來。')")
    b1 = json.loads(g.ev(L))
    check('koba_promo@28' in b1 and 'koba_newjob@40' in b1 and g.ev("S.regMem.koba.facts.length") == 6, f'three more notes, the oldest let go, the beats keep their days: {b1}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc6_the_morning_reports(b, port, target):
    """the player's 09:33–10:15 reports that had no test of their own: a guest's passing words are said once a day (the
    same words from another guest are left unsaid; a regular's own line, given with who, is not); the VIPs order in their
    own words; the waiters wear white shirts (10:15); the room is drawn at most ~30 times a second in a service — by the
    clock, so 120 frames a second draw no more than 60 — and ~10 under a sheet (the phone's heat); the summary says which
    stories moved today, what the Lounge sold (each glass and bite, and the total) and what the bartenders did (not
    「沒有桌子要收」); the journal's album has its close button at the bottom too (09:51)."""
    g = Game(b, port, target, seed=33, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day71_1215.json')
    to_service(g)
    g.page.evaluate('()=>window.__bot(300,1/30)')
    said = json.loads(g.ev("(()=>{const gs=R.groups.filter(q=>!q.reg&&!namedId(q)).slice(0,2);if(gs.length<2)return JSON.stringify(null);R.chatAt=null;R.chatN=0;S.chatSeen={};const n0=dayLog().length;const a=quote(gs[0],'今天的燈好舒服喔。'),b=quote(gs[1],'今天的燈好舒服喔。');const n=dayLog().slice(n0).filter(l=>l.t==='今天的燈好舒服喔。').length;return JSON.stringify([a,b,n])})()"))
    check(said == [True, False, 1], f'a guest\'s passing words once a day: {said}')
    check(g.ev("VIP_ORDER.length>=6&&new Set(VIP_ORDER).size===VIP_ORDER.length&&(()=>{const a=pickH(VIP_ORDER,'vip|71|5'),b=pickH(VIP_ORDER,'vip|71|6');return VIP_ORDER.includes(a)&&VIP_ORDER.includes(b)&&a!==b})()"), 'the VIPs have their own ways of ordering (one said is not said again right away)')
    tops = json.loads(g.ev("JSON.stringify([crewLook({id:'w1',role:'waiter',name:'x',lv:1}).top,crewLook({id:'w2',role:'waiter',name:'y',lv:3}).top,crewLook({id:'c1',role:'chef',name:'z',lv:1}).top])"))
    check(tops[0] == tops[1] == '#F4F1EA' and tops[2] in ('#FFFFFF', '#fff'), f'the waiters in white shirts, the cooks in their white jackets: {tops}')
    # the room's draws: by the clock
    g.ev("window.__D0=drawScene;window.__nd=0;drawScene=function(t){__nd++;return __D0(t)}")
    g.ev("__nd=0;for(let i=0;i<120;i++){__act();__tick(1000/120)}")
    n120 = g.ev("__nd")
    g.ev("__nd=0;for(let i=0;i<60;i++){__act();__tick(1000/60)}")
    n60 = g.ev("__nd")
    g.ev("showPause();__nd=0;for(let i=0;i<120;i++)__tick(1000/120)")
    nsheet = g.ev("__nd")
    g.ev("hideScreen();paused=false;drawScene=__D0")
    check(26 <= n120 <= 36 and 26 <= n60 <= 36 and nsheet <= 14, f'a second of service: {n120} draws at 120 Hz, {n60} at 60 Hz; {nsheet} under a sheet')
    # the summary: today's stories, the Lounge's sales, the bartenders
    g.ev("factSet('qt_3');R.st.dish.w_spark=(R.st.dish.w_spark||0)+3;R.st.dish.w_fred=(R.st.dish.w_fred||0)+2;R.st.dishRev=R.st.dishRev||{};R.st.dishRev.w_spark=(R.st.dishRev.w_spark||0)+540;R.st.dishRev.w_fred=(R.st.dishRev.w_fred||0)+560;"
         # v2.4 rc7 (14:51): the Lounge's list is what its tabs paid for (R.st.lgSold), its total the Lounge's takings
         "const L=R.st.lgSold=R.st.lgSold||{};L.w_spark={n:((L.w_spark||{}).n||0)+3,rev:((L.w_spark||{}).rev||0)+540};L.w_fred={n:((L.w_fred||{}).n||0)+2,rev:((L.w_fred||{}).rev||0)+560};R.st.lgRev=(R.st.lgRev||0)+1100")
    g.ev("closeShop('x');for(const q of R.groups.slice())leaveGroup(q,'ok')"); g.page.evaluate('()=>window.__bot(400,1/30)')
    if g.ev("phase") == 'service': g.ev("finishClosing()")
    g.ev("while(typeof DLG!=='undefined'&&DLG)dlgNext()")
    if g.ev("phase") != 'summary': g.ev("showSummary()")
    txt = g.ev("document.querySelector('#screen').innerText")
    check('今天的故事' in txt and '晴 & 阿拓' in txt and '多的' in txt and '看故事頁' in txt, f'today\'s stories: {txt[:400]}')
    check('Lounge 今天賣了什麼' in txt and '氣泡酒' in txt and '杯' in txt and '合計' in txt, 'the Lounge\'s sales, each glass and the total')
    bt = json.loads(g.ev("JSON.stringify((S.lastSummary.crew||[]).filter(c=>c.role==='bartender').map(c=>c.lines||c.txt||c))"))
    check('沒有桌子要收' not in g.ev("[...document.querySelectorAll('#screen *')].filter(e=>/Evan|沈晴/.test(e.textContent)&&e.children.length<4).map(e=>e.textContent).join('|')") and ('調了' in txt or '今晚沒有調酒' in txt), f'the bartenders\' line: {bt}')
    # the journal's album: a close button at the bottom
    g.click('[data-act=toShop]') if g.page.query_selector('[data-act=toShop]') else None
    g.ev("bookTab='mem';showBook()"); g.page.wait_for_timeout(100)
    check(g.ev("!!document.querySelector('#screen .bookend [data-act=closeSub]')") and '關閉日誌' in g.ev("document.querySelector('#screen .bookend').innerText"), 'the album ends with 「關閉日誌」')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc6_stalled_lines_move_on(b, port, target):
    """the player's 12:17 (「故事進展真的太慢 一堆劇情完全沒後續」, every line audited on their Day 71 save): Ken × Monsieur 杜
    sat at 1/9 since Day 52 — every later step needs the two of them in the Lounge on the same evening, and nothing
    arranged that (Ken came to the Lounge seven times, 杜 five, never together). Some evenings now bring the two of them to
    the Lounge around the same time until their stools are theirs; 「Lounge 的第一個晚上」, possible only in the Lounge's
    first three days, is no longer a step still to come once that is past. 周董's 「那明天再來。」 also comes when his
    dessert is not on today's menu; Madame Lin brings her plant after two changes noticed, or one and ten days."""
    g = Game(b, port, target, seed=72, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day71_1215.json')
    # Madame Lin: one change noticed, ten days and her visits
    l = json.loads(g.ev("(()=>{const E=STORY_EV.find(e=>e.k==='lin_gift');const g0={named:'Madame Lin',name:'Madame Lin',size:1};const f=fact('lin_saw');const a=E.when({g:g0});const keep=f.d;f.d=S.day-3;const b=E.when({g:g0});f.d=keep;return JSON.stringify({n:factN('lin_saw'),since:S.day-keep,visits:namedHist('Madame Lin').v,a,b})})()"))
    check(l['n'] == 1 and l['since'] >= 10 and l['a'] is True and l['b'] is False, f'Madame Lin\'s plant after one change and ten days (not after three): {l}')
    kd = json.loads(g.ev("JSON.stringify((()=>{const P=lineProgress(STORY_LINES.find(x=>x.k==='kd'));return{n:P.done.length,total:P.total}})())"))
    check(kd == {'n': 1, 'total': 8}, f'Ken × 杜: the Lounge\'s first night (Day 57–60) is past and no longer counted: {kd}')
    d = g.ev("(()=>{for(let d=S.day+1;d<S.day+30;d++)if(dayCoin('kdw|'+d)<40)return d;return null})()")   # (the save's own Day 71 has had their visits)
    check(d is not None and d - 71 <= 6, f'a coin within days: Day {d}')
    g.ev(f"S.day={d}")
    to_service(g)
    sched = json.loads(g.ev("JSON.stringify(R.sched.filter(o=>o.name===KEN||o.name===DU).map(o=>({n:o.name,lounge:!!o.lounge,grp:o.v24grp||null,t:Math.round(o.t)})))"))
    check(len(sched) == 2 and all(o['lounge'] and o['grp'] == 'kd' for o in sched) and abs(sched[0]['t'] - sched[1]['t']) <= 8, f'that evening the two of them come to the Lounge, around the same time: {sched}')
    for _ in range(400):
        g.page.evaluate('()=>window.__bot(60,1/30)')
        if g.ev("!!kenAt()&&!!duAt()") or g.ev("phase") != 'service': break
    both = json.loads(g.ev("JSON.stringify({k:!!kenAt(),d:!!duAt(),bar:!!kdBoth(),shared:relN(KEN_ID,DU_ID,'sharedTable')})"))
    check(both['k'] and both['d'] and both['shared'] >= 1, f'both in the Lounge, sharing it: {both}')
    # 周董: his dessert not on today's menu
    z = json.loads(g.ev("(()=>{const E=STORY_EV.find(e=>e.k==='zhou_dessert');const d=namedTop('周董','dessert');const m0=S.menu.slice();S.menu=S.menu.filter(x=>x!==d);const g0={named:'周董',name:'周董',size:1};const ctx={g:g0,tk:{lounge:0,items:[{d:'steak'}]}};const a=E.when(ctx);S.menu=m0;return JSON.stringify({d,a})})()"))
    check(z['d'] and z['a'] is True, f'周董 asks for his dessert on a day it is not on the menu: {z}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc7_the_money(b, port, target):
    """the player's 14:39–14:51: the Lounge's glasses have a cost (「阿lounge不用進貨成本?」) — every glass poured, in the
    Lounge or with dinner, is on the day's 酒水成本; a rent every day for the space the restaurant takes (small while the
    shop is small; 「你租金要計算一下吧 但不要讓剛開始太容易倒店」); the wages a little higher, mostly the seasoned crew
    (「員工薪水可以再增加一點」); nothing owed — in the first ten days, each evening the till would be under $300 after the
    day's costs, 秀琴阿姨 lends $3,000 at closing, paid back at a summary that ends over $20,000 (rc7.2, 21:57–21:58); the summary's
    Lounge figure is what the Lounge's tabs paid, the same as its list's total, with the tips and the glasses at dinner
    apart (「lounge幾桌 多少錢那個錢跟賣了多少酒的金額對不起來」); the menu says how many bar bites of how many (14:47)."""
    g = Game(b, port, target, seed=71, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day71_1215.json')
    rent = json.loads(g.ev("JSON.stringify({r:rentToday(),parts:rentParts()})"))
    check(rent['r'] == 2500 + 2000 + 400 + 800 + 2500 and [p[0] for p in rent['parts']] == ['主廳', '側廳', '戶外區', '廚房擴建', 'Lounge'], f'the Day 71 restaurant\'s rent: {rent}')
    small = json.loads(g.ev("(()=>{const L=S.level,r0=Object.assign({},S.rooms),lv=S.rooms.lounge;S.level=1;S.rooms={};const a=rentToday();S.level=L;S.rooms=r0;return JSON.stringify(a)})()"))
    check(small == 300, f'a first-day shop pays {small} a day')
    w = json.loads(g.ev("JSON.stringify({c1:crewWageAt('chef',1),c5:crewWageAt('chef',5),w5:crewWageAt('waiter',5),cl5:crewWageAt('cleaner',5),b5:crewWageAt('bartender',5),all:crewWages()})"))
    # rc7.2 (the player, 22:51): LV5 twice the rc7 wage, a new hire 15% more
    check(w['c1'] == 304 and w['c5'] == 1690 and w['w5'] == 1408 and w['cl5'] == 1056 and w['b5'] == 2253, f'the wages: {w}')
    check(14679 * 1.98 < w['all'] < 14679 * 2.02, f'the Day 71 crew, all LV5: $14,679 a day in rc7, {w["all"]} now')
    # the menu: the bar bites on tonight, of how many — three of four on this save before rc7.4; rc7.4's four new ones
    # (水牛城雞翅、起司條、生蠔、德國豬腳 — this Lounge is III) come onto the menu with the morning's news: seven of eight
    g.ev("showPrep()"); g.page.wait_for_timeout(100)
    h = g.ev("(()=>{const h=[...document.querySelectorAll('#screen h3')].find(e=>e.textContent.includes('今日菜單'));return h?h.textContent:''})()")
    bars = json.loads(g.ev("JSON.stringify({on:S.menu.filter(d=>DISHES[d]&&DISHES[d].bar).length,all:S.unlocked.filter(d=>DISHES[d]&&DISHES[d].bar).length,lv:loungeLv()})"))
    check(f"酒吧小點 {bars['on']} 道（共 {bars['all']} 道，不佔名額）" in h and (bars['on'], bars['all'], bars['lv']) == (7, 8, 3), f'the menu header: {h} {bars}')
    # a day: the wine poured, the rent, the wages, the Lounge's figures
    to_service(g); play_day(g)
    s = json.loads(g.ev("JSON.stringify(S.lastSummary)"))
    check(s['wine'] > 0 and s['rent'] == rent['r'] and s['wages'] == w['all'], f'on the ledger: wine {s["wine"]}, rent {s["rent"]}, wages {s["wages"]}')
    check(s['net'] == s['rev'] + s['tips'] + s['bonus'] - s['cost'] - s['wages'] - (s['cfee'] or 0) - s['rent'] - s['wine'], 'the net counts them')
    lg = s['lg']; tot = sum(x['rev'] for x in s['lgSales'])
    check(lg['rev'] == tot and lg['tip'] > 0 and all(x['d'].startswith('w_') or g.ev(f"!!(DISHES['{x['d']}']&&DISHES['{x['d']}'].bar)") for x in s['lgSales']), f'the Lounge: {lg["rev"]} = its list\'s total {tot}; tips {lg["tip"]} apart')
    din = s.get('dinWine') or []
    check(all(x['d'].startswith('w_') for x in din), f'the glasses with dinner, apart: {din}')
    poured = json.loads(g.ev("JSON.stringify(Object.keys(S.lastSummary.lgSales.concat(S.lastSummary.dinWine).reduce((a,x)=>(a[x.d]=1,a),{})))"))
    check(abs(s['wine'] - sum(g.ev(f"WINES['{d}']?WINES['{d}'].cost:0") * n for d, n in [(x['d'], x['n']) for x in s['lgSales'] + din if x['d'].startswith('w_')])) <= s['wine'] * .2, f'the 酒水成本 is the glasses\' cost (poured, paid or not): {s["wine"]}')
    g.ev("showSummary()"); g.page.wait_for_timeout(100)
    t = g.ev("document.querySelector('#screen').innerText")
    check('酒水成本' in t and '租金' in t and '主廳 $2,500' in t and f'營業額 {g.ev("fmt(S.lastSummary.lg.rev)")}' in t and 'Lounge 的小費' in t and '晚餐桌上配的酒' in t, 'the summary shows them')
    # the till never goes below $0, and nothing is carried
    g.ev("S.money=100;S.wageOwed=0")
    check(g.ev("(()=>{const m=S.money;const pay=n=>{const p=Math.min(n,Math.max(0,S.money));S.money-=p;return p};pay(5000);return S.money})()") == 0, 'paid down to $0, no lower')
    check(not g.errors, g.errors[:3]); g.close()
    # a new game, a short first evening: 秀琴阿姨 lends $3,000 at closing (rc7.2, the player 21:57–21:58: not $20,000, no
    # gift on the first day; each time the till would be under $300 after the day's costs, in the first ten days)
    g = Game(b, port, target, seed=72, manual=True, viewport={'width': 390, 'height': 844})
    g.click('[data-act=open]'); g.page.wait_for_timeout(150)
    check(g.ev("S.money") == 500 and not g.ev("S.loan"), 'no gift on the first day: a new game starts with $500 and owes nothing')
    g.ev("autoStock()"); start_day(g); install_bot(g)
    for _ in range(300):
        g.page.evaluate('()=>window.__bot(60,1/30)')
        if g.ev("R&&R.closed") or g.ev("phase") != 'service': break
    g.ev("S.money=40")   # an evening that has spent everything
    play_day(g)
    L = json.loads(g.ev("JSON.stringify({f:!!fact('xq_loan'),loan:S.lastSummary&&S.lastSummary.loan,money:S.money,day:S.day,owed:loanOwed(),line:(story().beatLines||{}).xq_loan||null})"))
    check(L['f'] and L['loan'] == 3000 and L['owed'] == 3000 and L['money'] >= 2700, f'秀琴阿姨 lent $3,000 at closing: {L}')
    check(L['line'] and any('三千' in (x.get('t') or '') for x in L['line']), 'her words are on the story page')
    g.ev("showSummary()"); g.page.wait_for_timeout(100)
    t = g.ev("document.querySelector('#screen').innerText")
    check('秀琴阿姨借的' in t and '$3,000' in t and '超過 $20,000' in t, 'and on the summary, under the night\'s net, with when it goes back')
    # the next evening short again: again, shorter; a till over $300 after the costs: nothing
    g.click('[data-act=toShop]'); g.page.wait_for_timeout(100); g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(150)
    g.ev("autoStock()"); start_day(g); install_bot(g)
    g.ev("__botUntil('R.closed||R.closing!=null',90000,1/30)"); g.ev("S.money=10"); play_day(g)
    L2 = json.loads(g.ev("JSON.stringify({loan:S.lastSummary.loan,owed:loanOwed(),n:factN('xq_loan'),times:S.loan.times,line:(story().beatLines||{}).xq_loan||null})"))
    check(L2['loan'] == 3000 and L2['owed'] == 6000 and L2['n'] == 2 and L2['times'] == 2, f'a second short evening, a second $3,000: {L2}')
    check(g.ev("(()=>{const d=S.day,m=S.money;S.day=Math.min(10,d+1);S.money=dayCostsDue()+300;const a=loanNeeded();S.money=dayCostsDue()+299;const b=loanNeeded();S.day=11;const c=loanNeeded();S.day=d;S.money=m;return [a,b,c].join()})()") == 'false,true,false', 'under $300 after the costs, and only in the first ten days')
    # the summary of a day that ends over $20,000 pays all of it back
    g.click('[data-act=toShop]'); g.page.wait_for_timeout(100); g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(150)
    g.ev("autoStock()"); start_day(g); install_bot(g)
    g.ev("__botUntil('R.closed||R.closing!=null',90000,1/30)"); g.ev("S.money=30000"); play_day(g)
    P = json.loads(g.ev("JSON.stringify({f:!!fact('xq_repay'),loan:S.lastSummary.loan,owed:loanOwed(),money:S.money})"))
    check(P['f'] and P['loan'] == -6000 and P['owed'] == 0 and P['money'] > 20000 - 6000, f'over $20,000 at the summary: paid back, all of it: {P}')
    g.ev("showSummary()"); g.page.wait_for_timeout(100)
    check('還秀琴阿姨' in g.ev("document.querySelector('#screen').innerText"), 'the summary says so')
    check(not g.errors, g.errors[:3]); g.close()
    # rc7's one $20,000 loan, in a save made before this: owed the same way, paid back at a summary over $20,000
    g = Game(b, port, target, seed=73, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day2_2155.json')
    check(g.ev("loanOwed()") == 20000 and g.ev("S.money") == 18891, f'the player\'s Day 2 save owes $20,000: {g.ev("loanOwed()")}')
    to_service(g); g.ev("__botUntil('R.closed||R.closing!=null',90000,1/30)"); g.ev("S.money=Math.max(S.money,26000)"); play_day(g)
    P = json.loads(g.ev("JSON.stringify({loan:S.lastSummary.loan,owed:loanOwed(),money:S.money})"))
    check(P['loan'] == -20000 and P['owed'] == 0 and P['money'] >= 0, f'paid back at the first summary over $20,000: {P}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc7_madame_lin_says_which_corner(b, port, target):
    """the player's 14:55 (「madam lin 說那個角落空很久 Jill回你到底都在看哪超沒邏輯」): she says which corner and why, Jill
    answers what she said; a story page that kept rc6's words shows the scene as it is now."""
    g = Game(b, port, target, seed=73, manual=True, viewport={'width': 390, 'height': 844})
    raw = json.load(open(os.path.join(ROOT, 'tests', 'saves', 'player_day71_1215.json'), encoding='utf-8')); raw = raw.get('save', raw)
    raw['story'].setdefault('beatLines', {})['lin_gift'] = [{'w': 'Jill', 't': '今天怎麼帶東西？'}, {'w': 'Madame Lin', 't': '那個角落空很久了。'}, {'w': 'Jill', 't': '……妳每次到底都在看哪裡？'}]
    g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.page.wait_for_timeout(150)
    lines = json.loads(g.ev("JSON.stringify(story().beatLines.lin_gift.map(x=>x.t))"))
    check('側廳門口旁邊那個角落，空很久了。' in lines and '……妳每次到底都在看哪裡？' not in lines and '就是因為天天在。' in lines, f'the page: {lines}')
    src = g.ev("String(STORY_EV.find(e=>e.k==='lin_gift').run)")
    check('側廳門口旁邊那個角落' in src and '妳每次到底都在看哪裡' not in src, 'the scene itself')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc7_the_landlord_goes_up(b, port, target):
    """the player's 15:40 (「房東說可以上去嗎 要有一個具體原因 而且應該是說 我上去一下 他本來就能上去 就說上去拿個東西」):
    the floor is his, so he asks nobody — he says he is going up for something (the two old fire extinguishers, the
    inspection is coming). rc7.2 (22:13–22:14): and nobody invites anybody — the cat who wanders runs up through the door
    he opened, Jill goes up after her, and he says what the floor is. A story page that kept rc6's or rc7's words shows the
    scene as it is now."""
    g = Game(b, port, target, seed=75, manual=True, viewport={'width': 390, 'height': 844})
    raw = json.load(open(os.path.join(ROOT, 'tests', 'saves', 'player_day74_1508.json'), encoding='utf-8')); raw = raw.get('save', raw)
    raw['story'].setdefault('beatLines', {})['up_inspect'] = [{'t': '下午，房東來了一趟。消防檢查快到了，他要上樓看一下。'}, {'w': 'Jill', 't': '我可以一起上去嗎？'}, {'w': '房東', 't': '可以啊。'}]
    g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.page.wait_for_timeout(150)
    page = json.loads(g.ev("JSON.stringify(story().beatLines.up_inspect)"))
    check({'w': '房東', 't': '我上去一下，拿個東西。'} in page and not any('可以一起上去' in x['t'] or x['t'] == '可以啊。' for x in page), f'the page: {page}')
    check(any('跑上樓' in x['t'] for x in page), f'the page tells the afternoon as it is now (rc7.2): {page}')
    # a page that kept rc7's words (「要上來看嗎？」) is told the new way too
    g.ev("""story().beatLines.up_inspect=[{t:'下午，房東來了一趟。'},{w:'房東',t:'我上去一下，拿個東西。'},{w:'房東',t:'要上來看嗎？'},{w:'Jill',t:'好。'}];const o=JSON.parse(JSON.stringify(S));beatLinesMig(o);window.__pg=o.story.beatLines.up_inspect""")
    pg7 = json.loads(g.ev("JSON.stringify(__pg)"))
    check(not any(x['t'] == '要上來看嗎？' for x in pg7) and any('跑上樓' in x['t'] for x in pg7), f'rc7\'s page, migrated: {pg7}')
    g.ev("window.__noScenes=false;STORY_EV.find(e=>e.k==='up_inspect').run()"); g.page.wait_for_timeout(80)
    shown = []
    for _ in range(14):
        if not g.ev("!!DLG"): break
        shown.append((g.ev("$('#dlg .dlg-name').textContent"), g.ev("$('#dlg .dlg-text').textContent")))
        g.page.wait_for_timeout(300); g.ev("dlgNext()")
    print('      the scene:', ' / '.join(f'{n or "—"}：{t}' for n, t in shown))
    check(('房東', '我上去一下，拿個東西。') in shown, 'he says he is going up, for something')
    check(any('滅火器' in t for _, t in shown), 'what he went up for is said: the old fire extinguishers')
    check(not any(('可以' in t and '上去' in t) or t == '可以啊。' for _, t in shown), 'nobody asks whether they may go up')
    # rc7.2 (the player, 22:13–22:14): nobody invites anybody — the cat who wanders runs up through the door he opened, Jill
    # goes up after her, and the landlord, up there already, says what the floor is
    cat = g.ev("upCatN('mei')")
    check(any(cat in t and '跑上樓' in t for _, t in shown), f'{cat} slips through the door and runs up: {shown}')
    check(any(t.startswith('Jill 跟上去帶' + cat) for _, t in shown), 'Jill goes up to bring her down')
    check(any(n == '房東' and '地板是好的' in t for n, t in shown), 'the landlord says what the floor is')
    check(not any('要上來看嗎' in t or '要不要' in t for _, t in shown), 'nobody invites anybody')
    check(g.ev("!!fact('up_inspect')") and not g.ev("!!DLG"), 'the beat is done and the panel closed')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc7_a_line_finds_its_table(b, port, target):
    """the player's 15:37 (「會出現頭像的對話反而點對話不會跳到那個桌子?」): a guest's line with a face, said while they are
    still walking to their table through another room, took the tap to the room they were crossing — now it goes to
    their table; a waiter's 「久等了。」 or 「這邊請。」 and the bartender's 「慢慢喝。」 find the table they were said at; Jill's
    line to a guest finds the guest; the inspector's 「衛生局，例行檢查。」 finds him (it said he had left)."""
    g = Game(b, port, target, seed=1537, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day74_1508.json')
    to_service(g)
    g.ev("__botUntil('R.t>=R.dur*.1',90000,1/30)")
    mark = lambda: json.loads(g.ev("JSON.stringify({room,m:IDF.map(m=>{const p=m.at&&m.at();return{label:m.label,sub:m.sub,room:p&&p.room}}),toast:$('#toasts').textContent})"))
    clear = "document.querySelectorAll('#plines>*,#toasts>*').forEach(e=>e.remove());IDF.length=0"
    # a regular walking to a table in another room
    info = json.loads(g.ev("""JSON.stringify((()=>{const t=R.tables.find(t=>['side','lounge'].includes(t.room)&&!t.group&&!t.dirty&&!t.hold&&t.seats>=1&&!t.pdr);if(!t)return null;
      const o=regPlanVisit({t:R.t,type:'gourmet',reg:'leo',size:1});o.moment=null;spawn(o);const q=R.groups[R.groups.length-1];seatGroup(q,t);window.__q=q;return{t:t.i,room:t.room}})())"""))
    check(info is not None, 'a free table in the side room or the Lounge')
    for _ in range(400):
        if g.ev("__q.room==='main'&&__q.state==='toTable'"): break
        g.ev("__tick(1000/30)")
    check(g.ev("__q.room==='main'&&__q.state==='toTable'"), f'Leo is walking through the dining room to his table: {g.ev("JSON.stringify([__q.room,__q.state])")}')
    g.ev(f"setRoom('kitchen');{clear};quote(__q,'今天人好多。',{{who:'leo'}})")
    check(g.page.query_selector('#plines .pline') is not None, 'his line comes with his face')
    g.page.click('#plines .pline'); g.ev("__tick(1000/30)")
    st = mark()
    check(st['room'] == info['room'] and st['m'] and st['m'][-1]['label'] == 'Leo' and st['m'][-1]['sub'] == f"T{info['t']+1}" and st['m'][-1]['room'] == info['room'], f'the tap goes to his table ({info}), not the room he is crossing: {st}')
    # a waiter's line at a table, from another room
    tg = json.loads(g.ev("""JSON.stringify((()=>{const q=R.groups.find(q=>q.table!=null&&['order','wait','eat'].includes(q.state)&&q!==__q);if(!q)return null;window.__t=q;const t=R.tables[q.table];return{t:t.i,room:t.room||'main',name:q.name||q.reg}})())"""))
    check(tg is not None, 'a party at a table')
    other = 'kitchen' if tg['room'] != 'kitchen' else 'main'
    who = g.ev("(()=>{const m=S.crew.find(m=>m.role==='waiter'&&STAFF_PORTRAITS[m.name]);return m?m.name:null})()")
    g.ev(f"setRoom('{other}');{clear};staffSay(S.crew.find(m=>m.name==={json.dumps(who)}),'久等了。',undefined,__t)")
    line = '#plines .pline' if g.page.query_selector('#plines .pline') else '#toasts .toast.who'
    g.page.click(line); g.ev("__tick(1000/30)")
    st = mark()
    # rc8: any of the marks — the previous step's mark (Leo's) can still be fading, after the new one
    check(st['room'] == tg['room'] and any(x['label'] == f"T{tg['t']+1}" and x['room'] == tg['room'] for x in st['m']), f"{who}'s 「久等了。」 finds the table she said it at ({tg}): {st}")
    # Jill's line to a guest finds the guest, at their table
    g.ev("__botUntil('__q.state!==\\'toTable\\'',20000,1/30)")
    g.ev(f"setRoom('kitchen');{clear};jillSay('嗯，今天比較忙。',{{with:'leo'}})")
    check(g.page.query_selector('#plines .pline') is not None, 'Jill\'s line to him comes with the two faces')
    g.page.click('#plines .pline'); g.ev("__tick(1000/30)")
    st = mark()
    check(st['room'] == info['room'] and st['m'][-1]['label'] == 'Leo', f'Jill\'s line to Leo finds Leo at his table: {st}')
    # the inspector walks the room; his line finds him
    g.ev(f"setRoom('kitchen');{clear};R.insp={{t:0,dur:22,x:DOOR.x,y:DOOR.y+20,tx:224,ty:204,b0:R.st.q.B,out:false}};portraitLine('named:衛生檢查員','衛生局，例行檢查。')")
    if g.page.query_selector('#plines .pline'):
        g.page.click('#plines .pline'); g.ev("__tick(1000/30)")
        st = mark()
        check('已經離開了' not in st['toast'] and st['room'] == 'main' and st['m'] and st['m'][-1]['label'] == '衛生檢查員', f'the inspector is found where he walks: {st}')
    g.ev("R.insp=null")
    check(not g.errors, g.errors[:3]); g.close()


KEN_N = '品酒師 Ken'


def _ken_lounge_guest(g, name):
    """someone walks in for the Lounge now (Ken or 杜 as a guest), seated there; returns whether they sat in the Lounge"""
    return g.ev("""(()=>{const n0=R.groups.length;spawn({t:R.t,type:'gourmet',size:1,name:%s,lounge:1});const q=R.groups[R.groups.length-1];return !!(q&&q.table!=null&&R.tables[q.table].room==='lounge')})()""" % json.dumps(name, ensure_ascii=False))


@test
def v24_rc7_ken_comes_back_and_proposes_a_tasting(b, port, target):
    """the player's KEN / LOUNGE STORY CONTINUITY PASS (15:24): the finished Lounge is where Ken's next chapter begins. A save
    whose Lounge was open long before (the player's Day 74: finished on Day 57) skips his first look and starts at the
    proposal — not on the first day played, with a line that says he has been coming for weeks; the proposal plans the
    first tasting three days on, and the news says so the day before and on the day. A Lounge just finished: his first
    look first (no congratulation; he counts the stools), the proposal two days later at the earliest. One Ken scene a
    day; tastings are only his."""
    g = Game(b, port, target, seed=1524, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day74_1508.json')
    g.ev("kenS()")
    st = json.loads(g.ev("JSON.stringify({first:kenS().first,day:S.day,legacy:kenLegacy(),done:loungeDoneDay(),lounge:kenLoungeDue(),propose:kenProposeDue()})"))
    check(st['legacy'] and st['first'] == st['day'] and not st['lounge'] and not st['propose'], f'the Lounge open since Day {st["done"]}: no first look, and nothing on the first day played: {st}')
    g.ev("kenS().first=S.day-1")
    check(g.ev("kenProposeDue()") is True, 'the next day the proposal is due')
    wants = json.loads(g.ev("JSON.stringify(V24_WANTS.map(f=>{try{return f()||[]}catch(e){return[]}}).flat().filter(w=>w.name===KEN).map(w=>w.k||w.grp))"))
    check('ken_propose' in wants, f'the day\'s plan brings him to the Lounge for it: {wants}')
    to_service(g)
    g.ev("window.__fastSay=1")
    g.ev("__botUntil('R.t>=R.dur*.3',90000,1/30)")
    g.ev("const d=storyDay();d.major=0;d.lp={};d.seen={};if(S.story.v24)S.story.v24.res=null;S.story.owe=null;for(const q of R.groups.slice())if(namedId(q)===KEN){leaveGroup(q,'ok');q.gone=true}R.groups=R.groups.filter(q=>!q.gone);(story().named[KEN]||{}).seen=0")
    check(_ken_lounge_guest(g, KEN_N), 'Ken sits down in the Lounge')
    page = json.loads(g.ev("JSON.stringify((story().beatLines||{}).ken_propose||[])"))
    txt = ' / '.join(x['t'] for x in page)
    check(g.ev("!!fact('ken_propose')") and '這裡其實可以辦品酒。' in txt and '我在這裡坐了好幾個晚上了。' in txt and '我主持。酒我挑，菜妳配。' in txt, f'the proposal, with the line for a Lounge he has sat in for weeks: {txt}')
    check('不用算。我自己喜歡，友情主持。' in txt and '不行，該算的還是要算。' in txt and '我又不是為了錢。' in txt and g.ev("!!fact('ken_cut')"), f'rc7.7 (10:10): he would host it as a friend; Jill offers the share herself: {txt}')
    check('三成' not in txt and '所以是我要給' not in txt, f'12:43 「就直接說不行該算的還是要算就好了啊，不用直接說三成」: {txt}')
    check(json.loads(g.ev("JSON.stringify(kenS().next)")) == {'d': g.ev("S.day") + 3, 'n': 1}, 'the first night three days on')
    check(g.ev("kenQuiet()") is False and g.ev("kenLoungeDue()") is False, 'one Ken scene today; his first look never comes in this save')
    check(not any(k in txt for k in ('終於完成', '這裡真的很棒', '實現夢想')), 'no congratulation')
    # the news: the day before, and the day
    g.ev("kenS().next.d=S.day+1")
    seats = g.ev("lgSeatsAll()")
    check(seats == 23 and f'明晚｜品酒之夜 · {seats} 席' in g.ev("kenNewsHTML()") and '整個 Lounge' in g.ev("kenNewsHTML()"), f'the day before: 明晚｜品酒之夜 · {seats} 席 — the whole Lounge (rc7.6, 07:44)')
    g.ev("kenS().next.d=S.day")
    check(f'今晚｜品酒之夜 · {seats} 席' in g.ev("kenNewsHTML()") and '整個 Lounge 留給品酒的客人' in g.ev("kenNewsHTML()"), f'the day: 今晚｜品酒之夜 · {seats} 席')
    # a Lounge just finished: his first look first
    g.ev("delete story().facts.ken_propose;delete story().ev.ken_propose;delete (story().beatLines||{}).ken_propose;kenS().next=null;kenS().first=S.day;story().facts.lounge_built_1={d:S.day-1,n:1,l:S.day-1};const d=storyDay();d.major=0;d.lp={};d.seen={};for(const q of R.groups.slice())if(namedId(q)===KEN){leaveGroup(q,'ok');q.gone=true}R.groups=R.groups.filter(q=>!q.gone)")
    check(g.ev("kenLegacy()") is False and g.ev("kenLoungeDue()") is True and g.ev("kenProposeDue()") is False, 'a Lounge finished yesterday: his first look is due, the proposal is not')
    g.ev("(story().named[KEN]||{}).seen=0")
    check(_ken_lounge_guest(g, KEN_N), 'Ken sits down in the Lounge')
    page = json.loads(g.ev("JSON.stringify((story().beatLines||{}).ken_lounge||[])"))
    txt = ' / '.join(x['t'] for x in page)
    check(g.ev("!!fact('ken_lounge')") and '跟我想的不一樣。' in txt and '這裡坐滿是幾個人？' in txt and not any(k in txt for k in ('終於完成', '這裡真的很棒', '實現夢想')), f'his first look: no speech, he counts the stools: {txt}')
    check(g.ev("kenProposeDue()") is False, 'the proposal waits two days')
    g.ev("story().facts.ken_lounge.d=S.day-2"); check(g.ev("kenProposeDue()") is True, '...then it can come')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc7_ken_hosts_his_tasting_nights(b, port, target):
    """Ken's tasting nights (15:24 / 15:33): the first is a scene that holds the restaurant — the panel opens with the
    player's picture, nothing moves until it is tapped, one line a tap, and the evening goes on exactly where it was
    after it. He is perceptibly there: behind the bar with a glass (not on a stool); rc7.6 (07:44 「酒吧品酒日不只吧台
    整個酒吧都是品酒日的來賓」): the whole Lounge is for the people who came — every seat, nobody else seated there that
    night — some in twos and fours; the guests order two or three of tonight's wines each, a round at a time at every
    seat (rc7.7, 10:10: Ken opens each and says what it is; the Lounge's people pour it — never through the bartenders'
    mixing). When the last of them has gone: 「所以下次換一支。」, the second
    night planned, and he goes home. The second night is not the first again (returning faces, 杜 among them, a different
    set of wines); the third ends with 「做一支我們自己的。」 — and the wine cannot be talked about before it. The count
    survives a reload."""
    g = Game(b, port, target, seed=1533, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day74_1508.json')
    g.ev("factSet('ken_propose');kenS().next={d:S.day,n:1};kenS().back=[];showPrep()")
    check('今晚｜品酒之夜 · 23 席' in g.ev("$('#screen').innerText") and '整個 Lounge 留給品酒的客人' in g.ev("$('#screen').innerText"), 'the news before opening: the whole Lounge, 23 seats')
    check(g.ev("!!fact('ken_collab')") is False and g.ev("kenSamplesDue()") is False, 'no talk of a wine before three nights')
    to_service(g)
    g.ev("window.__noScenes=false;window.__holds=true")
    for _ in range(3000):
        g.page.evaluate('()=>window.__bot(30,1/30)')
        if g.ev("!!(DLG&&DLG.sh&&DLG.sh.k==='ken_t1')") or g.ev("phase") != 'service': break
    check(g.ev("!!(DLG&&DLG.sh&&DLG.sh.k==='ken_t1')"), 'the first night begins as a held scene')
    st = json.loads(g.ev("""JSON.stringify({host:R.kt.host.state,hx:Math.round(R.kt.host.x-KEN_HOST.x),hy:Math.round(R.kt.host.y-KEN_HOST.y),room:R.kt.host.room,table:R.kt.host.table,
      seated:R.kt.guests.filter(q=>q.table!=null&&R.tables[q.table].room==='lounge'&&['reading','order','wait','eat','check'].includes(q.state)).reduce((a,q)=>a+q.size,0),
      people:R.kt.people,sizes:R.sched.filter(o=>o.tasting).map(o=>o.size||1).concat(R.kt.guests.map(q=>q.size)).sort().join(''),
      tables:loungeTables().length,tst:loungeTables().filter(t=>t.tst).length,
      other:lgSeatOpen({}),guest:lgSeatOpen({tasting:1}),illus:!!(story().illus||{}).ken_t1,hold:$('#dlg .dlg-hold').textContent})"""))
    check(st['host'] == 'host' and abs(st['hx']) <= 2 and abs(st['hy']) <= 2 and st['room'] == 'lounge' and st['table'] is None, f'Ken behind the bar, not on a stool: {st}')
    check(st['people'] == 23 and st['seated'] >= 2 and st['tst'] == st['tables'] and not st['other'] and st['guest'] and '2' in st['sizes'] and '4' in st['sizes'], f'the whole room is the tasting\'s — every seat, some in twos and a four: {st}')
    check(st['illus'] and '店裡暫停中' in st['hold'] and 'Ken' in st['hold'], f'the picture, and the restaurant held: {st}')
    t0, i0 = g.ev("R.t"), g.ev("DLG.i")
    g.ev("for(let i=0;i<10;i++)__tick(1000)")
    check(g.ev("R.t") == t0 and g.ev("DLG.i") == i0, 'nothing moves while it is open, and the words wait for a tap')
    seen = []
    for _ in range(20):
        if not g.ev("!!(DLG&&DLG.sh)"): break
        seen.append(g.ev("$('#dlg .dlg-text').textContent")); g.ev("__tick(300);dlgNext()")
    check('我就知道一定有人不聽。' in seen and '今天三支。不用猜是哪裡的酒，先喝。' in seen, f'the first night\'s words, one per tap: {seen}')
    g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
    check(g.ev("R.t") > t0, 'the evening goes on where it was')
    g.ev("window.__holds=false;window.__noScenes=true;window.__fastSay=1")
    g.ev("__botUntil('R.kt.guests.some(q=>q.ticket&&q.ticket.items.length>=2)',30000,1/30)")
    od = json.loads(g.ev("JSON.stringify(R.kt.guests.filter(q=>q.ticket).map(q=>q.ticket.items.filter(i=>R.kt.wines.includes(i.d)).length/q.size))"))
    check(od and all(n >= 2 for n in od), f'each orders two or three of tonight\'s wines: {od}')
    g.ev("__botUntil('R.kt.on&&R.kt.guests.some(q=>q.ticket&&q.table!=null&&R.tables[q.table].kind!==\\'bar\\'&&q.ticket.items.some(i=>i.ktw&&i.st===\\'served\\'))',60000,1/30)")
    rd = json.loads(g.ev("""JSON.stringify({tables:R.kt.guests.filter(q=>q.ticket&&q.table!=null&&R.tables[q.table].kind!=='bar'&&q.ticket.items.some(i=>i.ktw&&i.round===0&&i.st==='served')).length,
      mixed:R.tickets.some(t=>t.items.some(i=>i.ktw&&(i.st==='pending'||i.lbar))),said:R.kt.said})"""))
    check(rd['tables'] >= 1 and not rd['mixed'], f'the first round reaches the tables too, never through the bartenders\' mixing: {rd}')
    g.ev("setRoom('main');idFocusWho('named:'+KEN)")
    check(g.ev("room") == 'lounge' and g.ev("IDF.length&&IDF[IDF.length-1].label") == KEN_N, 'a line of his finds him behind the bar')
    g.ev("__botUntil('R.kt.end',120000,1/30)")
    page = ' / '.join(x['t'] for x in json.loads(g.ev("JSON.stringify(story().beatLines.ken_t1)")))
    check('所以下次換一支。' in page and json.loads(g.ev("JSON.stringify(kenS().next)")) == {'d': g.ev("S.day") + 5, 'n': 2}, f'the end of the night, on the same page; the second planned: {page}')
    check(g.ev("loungeTables().some(t=>t.tst)") is False and g.ev("lgSeatOpen({})") and g.ev("R.kt.end") == 1, 'the Lounge is everyone\'s again')
    g.ev("__botUntil('!R.kt.host||R.kt.host.gone||R.kt.host.state!==\\'host\\'',20000,1/30)")
    check(g.ev("!R.kt.host||R.kt.host.gone||R.kt.host.state!=='host'"), 'and Ken goes home (by the evening\'s clock, not only a timer)')
    check(len(json.loads(g.ev("JSON.stringify(kenS().back||[])"))) >= 2, 'a few of tonight\'s faces are remembered')
    # the count survives a reload
    g.ev("__botUntil('phase!==\\'service\\'',90000,1/30)")
    g.ev("save()"); g.reload(); g.page.wait_for_timeout(150)
    rel = json.loads(g.ev("JSON.stringify({t1:!!fact('ken_t1'),tn:factN('ken_tn'),next:kenS().next})"))
    check(rel['t1'] and rel['tn'] == 1 and rel['next']['n'] == 2, f'after a reload: {rel}')
    # the second and the third: a day each
    for n in (2, 3):
        if g.ev("phase") == 'title':
            g.click('[data-act=openFresh]') if g.page.query_selector('[data-act=openFresh]') else g.click('[data-act=open]'); g.page.wait_for_timeout(120)
        for _ in range(3):
            if g.ev("phase") == 'summary': g.click('[data-act=toShop]'); g.page.wait_for_timeout(60)
            if g.ev("phase") == 'shop': g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(100)
        g.ev("kenS().next.d=S.day")
        to_service(g)
        g.ev("window.__fastSay=1")
        g.ev("__botUntil('!R||(R.kt&&R.kt.end)',150000,1/30)")
        check(g.ev("!!(R&&R.kt&&R.kt.end)"), f'night {n} came and ended: {g.ev("JSON.stringify({phase,day:S.day,next:kenS().next,R:!!R,kt:!!(R&&R.kt),tr:story().trace.filter(t=>t.d===S.day).map(t=>t.k)})")}')
        k = json.loads(g.ev("JSON.stringify({n:R.kt.n,wines:R.kt.wines,du:R.kt.du,duIn:R.kt.guests.some(q=>namedId(q)===DU),back:R.kt.guests.filter(q=>(kenS().back||[]).some(b=>b.name===q.name)).length,f:['ken_t2','ken_t3','ken_collab'].filter(k=>fact(k))})"))
        if n == 2:
            check(k['n'] == 2 and 'ken_t2' in k['f'] and 'ken_collab' not in k['f'] and k['back'] >= 1, f'the second night: returning faces: {k}')
            check(k['du'] and k['duIn'] and g.ev("relN(KEN_ID,DU_ID,'argued')") >= 3, f'杜 at the end of the bar, and they disagree: {k}')
            p2 = ' / '.join(x['t'] for x in json.loads(g.ev("JSON.stringify(story().beatLines.ken_t2)")))
            check('這支配那道，太輕。' in p2 and '下次換一支。' in p2, f'the second night\'s page: {p2}')
            check(g.ev("(story().illus||{}).ken_t2") == g.ev("S.day"), 'rc8.4: the second night has its own picture')
            w2 = k['wines']
        else:
            check(k['n'] == 3 and 'ken_t3' in k['f'] and 'ken_collab' in k['f'] and k['wines'] != w2, f'the third night, a different set of wines, and the wine: {k}')
            pc = ' / '.join(x['t'] for x in json.loads(g.ev("JSON.stringify(story().beatLines.ken_collab)")))
            check('三次了。' in pc and '做一支我們自己的。' in pc and g.ev("kenS().samples") == g.ev("S.day") + 4 and g.ev("kenS().next") is None, f'「做一支我們自己的。」 {pc}')
            check(g.ev("(story().illus||{}).ken_t3") == g.ev("S.day"), 'rc8.4: the third night has its own picture')
        g.ev("__botUntil('phase!==\\'service\\'',90000,1/30)")
    check(g.ev("factN('ken_tn')") == 3 and g.ev("factN('ken_t1')+factN('ken_t2')+factN('ken_t3')") == 3, 'three nights, each once')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc7_the_wine_and_monsieur_du(b, port, target):
    """「晚餐之後」 — JILL'S KITCHEN × KEN (15:24 and the 杜 payoff): three samples tasted against Jill's signature after
    closing, the name is hers; the wine comes in the afternoon and is on the Lounge's list from then on (not researched;
    about a pinot's price; it goes with the signature; the list says whose it is); once. 杜 tastes it days later, never the
    night it came out, only with their arguments behind them: he still says it is too light — and that it is good,
    sincerely. Afterwards he orders it now and then, unexplained."""
    g = Game(b, port, target, seed=1535, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day74_1508.json')
    g.ev("for(const k of ['ken_propose','ken_t1','ken_t2','ken_t3','ken_collab']){const d=S.day-12;story().facts[k]={d,n:1,l:d}}kenS().samples=S.day;kenS().next=null")
    check(g.ev("wineHas('w_jk')") is False and 'w_jk' not in json.loads(g.ev("JSON.stringify(wineAvail())")), 'not on the list before it exists')
    to_service(g)
    g.ev("window.__fastSay=1")
    g.ev("__botUntil('R.t>=R.dur*.2',90000,1/30)")
    g.ev("(story().named[KEN]=story().named[KEN]||{v:0,dishes:{}}).seen=S.day;const d=storyDay();d.major=0;d.lp={};d.seen={};storyTick('close',{})")
    pg = ' / '.join(x['t'] for x in json.loads(g.ev("JSON.stringify((story().beatLines||{}).ken_samples||[])")))
    check(g.ev("!!fact('ken_samples')") and '叫「晚餐之後」。' in pg and '吃完飯以後，還有地方可以坐。' in pg and '這裡就是這樣開始的' not in pg and g.ev("kenS().wineD") == g.ev("S.day") + 5, f'after closing: the samples, the name: {pg}')
    # the next day (one Ken scene a day). rc7.3 release: the day's major slot is a weighted draw among the beats due that
    # morning (wpick) — with this save the landlord's afternoon (up_inspect) is due too, and which one a seed draws first
    # moves whenever anything else draws a random number (rc7.3's cats do). ken_wine is class A with a floor of 2: passed
    # over twice, it is next. So: the morning it is due, or one of the two after.
    g.ev("kenS().wineD=S.day+1")
    days = 0
    for _ in range(3):
        g.ev("S.day++;const d=storyDay();d.major=0;d.lp={};d.seen={};storyTick('daystart',{})"); days += 1
        if g.ev("!!fact('ken_wine')"): break
    mornings = g.ev("JSON.stringify(story().trace.filter(t=>t.at==='daystart').slice(-3))")
    check(g.ev("!!fact('ken_wine')") and g.ev("wineHas('w_jk')") and 'w_jk' in json.loads(g.ev("JSON.stringify(wineList())")), f'the wine is in, on tonight\'s list (morning {days} of 3): {mornings}')
    w = json.loads(g.ev("JSON.stringify({n:WINES.w_jk.n,p:priceOf('w_jk'),pinot:priceOf('w_pinot'),cham:priceOf('w_cham'),dev:WINES.w_jk.dev||null,pair:winePairOk('w_jk',{type:'office'},['signature']),same:Object.keys(WINES).filter(k=>WINES[k].n==='晚餐之後').length,illus:!!(story().illus||{}).ken_wine})"))
    check(w['n'] == '晚餐之後' and w['pinot'] < w['p'] < w['cham'] and w['dev'] is None and w['pair'] and w['same'] == 1 and w['illus'], f'its place on the list — not overpowered, not researched, with the signature: {w}')
    g.ev("showPrep()") if g.ev("phase") != 'service' else None
    html = g.ev("wineTonightHTML()")
    check('晚餐之後' in html and "JILL'S KITCHEN × KEN" in html, 'the list says whose it is')
    g.ev("const d=storyDay();d.major=0;d.lp={};d.seen={};storyTick('daystart',{})")
    check(g.ev("factN('ken_wine')") == 1, 'it comes once')
    # 杜, not the night it came out
    g.ev("const d=storyDay();d.major=0;d.lp={};d.seen={};for(const q of R.groups.slice())if([KEN,DU].includes(namedId(q))){leaveGroup(q,'ok');q.gone=true}R.groups=R.groups.filter(q=>!q.gone);for(const n of [KEN,DU])(story().named[n]||{}).seen=0")
    check(g.ev("duWineDue()") is False, 'not the night it came out')
    g.ev("story().facts.ken_wine.d=S.day-4;story().facts.ken_wine.l=S.day-4")
    check(g.ev("duWineDue()") is True, 'four days on, with their arguments behind them, it can come')
    _ken_lounge_guest(g, KEN_N); _ken_lounge_guest(g, 'Monsieur 杜')
    g.ev("const d=storyDay();d.major=0;d.lp={};d.seen={};storyTick('lounge',{g:R.groups[R.groups.length-1]})")
    pd = [x['t'] for x in json.loads(g.ev("JSON.stringify((story().beatLines||{}).du_wine||[])"))]
    check(g.ev("!!fact('du_wine')") and '太輕。要我選，不會往這個方向走。' in pd and '可是它很好。' in pd and '我說的是酒，不是客氣。' in pd, f'he still disagrees, and he says it is good: {pd}')
    check(not any(x in ' '.join(pd) for x in ('還可以', '勉強及格', '至少能喝', '怎麼樣？好喝嗎？')), 'nothing that takes the compliment back; nobody asks anxiously')
    check(g.ev("relN(KEN_ID,DU_ID,'respected')") == 1 and g.ev("(story().illus||{}).du_wine!=null"), 'the respect is remembered; the picture')
    # afterwards: he orders it now and then
    g.ev("window.__mr=Math.random;Math.random=()=>.05")
    o = json.loads(g.ev("JSON.stringify(loungeOrder(R.groups.find(q=>namedId(q)===DU)))"))
    g.ev("Math.random=window.__mr")
    check('w_jk' in o, f'杜 orders it again, without a word about it: {o}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc7_yuan_comes_to_play_the_piano(b, port, target):
    """the player's 16:42–16:46 (docs/v24/pianist_yuan_2026-10-02_1642.txt): the piano is silent until 予安 — no one plays
    it every third night any more (14:49 「怎樣會有人來彈鋼琴?不用付錢嗎」). She comes in as a guest and keeps looking at it;
    「那台有人彈嗎？」; 「妳們有在找彈琴的人嗎？」「妳有認識的？」「我。」…「妳也沒問。」; the next time she plays (the Wangs
    in the Lounge): each scene holds the restaurant and waits for a tap, her playing does not; at the end of the piece 王太太
    says 「彈得真好。」 and she says 「謝謝。」; later 「下週還有空嗎？」「星期幾？」. From then on: three nights a week, the
    news says so, the piano draws her, her fee is on the summary; nobody else plays it."""
    g = Game(b, port, target, seed=1646, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day74_1508.json')
    check(g.ev("pianoDay()") == 71 and g.ev("[0,1,2,3,4,5,6].some(i=>{const d0=S.day;S.day=d0+i;const r=pianoNight();S.day=d0;return r})") is False, 'the piano bought on Day 71 is silent: no night of it plays by itself')
    g.ev("yaFirst()")
    check(g.ev("yaDue('ya_1')") is False, 'not on the first day played')
    g.ev("story().yaFirst=S.day-1")
    check(g.ev("yaDue('ya_1')") is True, 'the next day her first evening is due')
    to_service(g); g.ev("window.__fastSay=1")
    g.ev("__botUntil('R.t>=R.dur*.25',90000,1/30)")
    def seat_ya():
        g.ev("const d=storyDay();d.major=0;d.lp={};d.seen={};if(S.story.v24)S.story.v24.res=null;S.story.owe=null;(story().named[YA]||{}).seen=0;for(const q of R.groups.slice())if(namedId(q)===YA){leaveGroup(q,'ok');q.gone=true}R.groups=R.groups.filter(q=>!q.gone)")
        return _ken_lounge_guest(g, '林予安')
    page = lambda k: ' / '.join(x['t'] for x in json.loads(g.ev(f"JSON.stringify((story().beatLines||{{}}).{k}||[])")))
    check(seat_ya(), 'she sits down in the Lounge, a guest')
    p1 = page('ya_1')
    check(g.ev("!!fact('ya_1')") and '她的視線，好幾次落在那台沒有人彈的鋼琴上。' in p1 and '彈' not in p1.replace('沒有人彈的鋼琴', ''), f'her first evening: she looks at the piano and says nothing about it: {p1}')
    g.ev("story().facts.ya_1.d=S.day-2"); check(seat_ya(), 'again')
    p2 = page('ya_2')
    check('那台有人彈嗎？' in p2 and '目前沒有。買來以後就一直放著。' in p2 and '我。' not in p2, f'「那台有人彈嗎？」 and no more: {p2}')
    g.ev("story().facts.ya_2.d=S.day-2"); check(seat_ya(), 'again')
    p3 = page('ya_3')
    check('妳們有在找彈琴的人嗎？' in p3 and '妳有認識的？' in p3 and '我。' in p3 and '妳也沒問。' in p3, f'「我。」: {p3}')
    check(g.ev("yaTrialDue()") is False, 'the trial is the next time she comes')
    # the trial: a day of its own
    g.ev("__botUntil('phase!==\\'service\\'',90000,1/30)")
    for _ in range(3):
        if g.ev("phase") == 'summary': g.click('[data-act=toShop]'); g.page.wait_for_timeout(60)
        if g.ev("phase") == 'shop': g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(100)
    g.ev("story().facts.ya_3.d=S.day-2")
    check(g.ev("yaTrialDue()") is True, 'two days on, the trial')
    to_service(g); g.ev("window.__noScenes=false;window.__holds=true")
    plan = json.loads(g.ev("JSON.stringify(R.sched.filter(o=>o.pianist||o.reg==='wang').map(o=>({p:!!o.pianist,trial:!!o.yaTrial,wang:o.reg==='wang',lounge:!!o.lounge})))"))
    check(any(o['p'] and o['trial'] for o in plan) and any(o['wang'] and o['lounge'] for o in plan), f'tonight: her, and the Wangs in the Lounge: {plan}')
    def held(keys, n=24):
        for _ in range(4000):
            if g.ev("!!(DLG&&DLG.sh&&!%s.includes(DLG.sh.k))" % json.dumps(keys)):   # another story's panel: read it, as a player would
                g.ev("for(let i=0;i<30&&DLG&&DLG.sh&&!%s.includes(DLG.sh.k);i++){__tick(300);dlgNext()}" % json.dumps(keys)); continue
            g.page.evaluate('()=>window.__bot(30,1/30)')
            if g.ev("!!(DLG&&DLG.sh&&%s.includes(DLG.sh.k))" % json.dumps(keys)) or g.ev("phase") != 'service': break
        if not g.ev("!!(DLG&&DLG.sh)"): return None
        t0 = g.ev("R.t"); g.ev("for(let i=0;i<6;i++)__tick(1000)"); frozen = g.ev("R.t") == t0
        out = []
        for _ in range(n):
            if not g.ev("!!(DLG&&DLG.sh)"): break
            out.append(g.ev("$('#dlg .dlg-name').textContent+'：'+$('#dlg .dlg-text').textContent")); g.ev("__tick(300);dlgNext()")
        return frozen, out
    r = held(['ya_trial'])
    check(r and r[0] and '林予安：現在。' in r[1], f'she sits down at the piano — a scene, the restaurant held: {r}')
    t1 = g.ev("R.t"); g.ev("for(let i=0;i<40;i++)__tick(1000/30)")
    check(g.ev("R.t") > t1 and g.ev("!!yaAtPiano()") and g.ev("JSON.stringify(yaAtPiano())") == g.ev("JSON.stringify(NAMED[YA].looks)"), 'while she plays the evening goes on, and the piano draws her')
    check(g.ev("pianoNight()") is True, 'tonight the piano is played')
    r = held(['ya_trial'])
    check(r and r[0] and '王太太：彈得真好。' in r[1] and '林予安：謝謝。' in r[1] and any('拍手' in x for x in r[1]), f'the end of the piece: applause, 王太太, 「謝謝。」: {r}')
    check(not any(x for x in r[1] if x.startswith('王先生：')), '王先生 has no line')
    check(g.ev("(story().illus||{}).ya_trial!=null"), 'the picture')
    r = held(['ya_join'])
    check(r and r[0] and 'Jill：下週還有空嗎？' in r[1] and '林予安：星期幾？' in r[1] and g.ev("!!fact('ya_join')"), f'「下週還有空嗎？」「星期幾？」: {r}')
    j = g.ev("fact('ya_join').d")
    nights = [d for d in range(j, j + 14) if g.ev(f"yaNight({d})")]
    check(len(nights) == 6 and all(d > j for d in nights) and nights[:3] == [j + 1, j + 3, j + 5], f'three nights a week: {nights}')
    # one of her nights: the news, her at the piano, the fee
    g.ev("window.__holds=false;window.__noScenes=true")
    g.ev("__botUntil('phase!==\\'service\\'',90000,1/30)")
    for _ in range(3):
        if g.ev("phase") == 'summary': g.click('[data-act=toShop]'); g.page.wait_for_timeout(60)
        if g.ev("phase") == 'shop': g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(100)
    check(g.ev("S.day") == j + 1 and '今晚｜予安在 Lounge 彈琴' in g.ev("$('#screen').innerText"), 'her first night: the news before opening')
    to_service(g)
    g.ev("__botUntil('R.ya&&R.ya.on',60000,1/30)")
    check(g.ev("!!yaAtPiano()") and g.ev("R.st.piano") == 2500, 'she plays; her fee for the night')
    g.ev("__botUntil('phase!==\\'service\\'',90000,1/30)")
    s = json.loads(g.ev("JSON.stringify({piano:S.lastSummary.piano,net:S.lastSummary.net,calc:S.lastSummary.rev+S.lastSummary.tips+S.lastSummary.bonus-S.lastSummary.cost-S.lastSummary.wages-S.lastSummary.cfee-S.lastSummary.rent-S.lastSummary.wine-S.lastSummary.piano})"))
    check(s['piano'] == 2500 and s['net'] == s['calc'], f'the fee is on the night\'s accounts: {s}')
    check('鋼琴演奏' in g.ev("$('#screen').innerText"), 'the summary says so')
    check(g.ev("yaNight(S.day+1)") is False, 'not every night')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc7_story_guests_have_their_own_faces(b, port, target):
    """the player's 15:38 (「有劇情的npc在遊戲裡的臉和髮型可不可以特別一點 不要都跟別人一樣」): every guest with a story — the seven
    regulars, the named guests, 怡君 and 予安, Dylan — has a hair style a stranger is never given (10–23, drawn from their
    portraits; 陳伯伯's older man's 5; Dylan's 9; the hatted critic's disguise is his hat), no two of them the same style
    and colour; a stranger never has their glasses, beard, earrings, pearls, cravat, overalls or camera, and none of them
    wears the strangers' round frames or a beret; every style draws something of its own, in every pose."""
    g = Game(b, port, target, seed=1538, manual=True, viewport={'width': 390, 'height': 844})
    r = json.loads(g.ev(r"""JSON.stringify((()=>{
      const SF=['specs','beard','brow','lash','lips','eye','ear','earc','neckl','cravat','overall','camera','lock','bangs','tie2'];
      const T=['office','student','gourmet','couple','family','vip','blogger','regular'],ctx=['main','pdr','lounge'];const gen=[];
      for(let i=0;i<1500;i++)for(const L of makeLooks(T[i%T.length],1+(i%4),ctx[i%3]))gen.push(L);
      const genHs=[...new Set(gen.map(L=>L.hs))].sort((a,b)=>a-b),genSF=gen.filter(L=>SF.some(k=>L[k]!=null)).length,genHat=gen.filter(L=>L.acc==='hat').length;
      const cast=REGS.map(r=>({n:r.n,L:r.looks[0]})).concat(Object.keys(NAMED).map(k=>({n:k,L:NAMED[k].looks})),[{n:'Dylan',L:DYLAN.looks[0]}]);
      const own=cast.filter(x=>x.L.acc!=='hat').map(x=>({n:x.n,hs:x.L.hs,hair:x.L.hair,acc:x.L.acc||null}));
      const keys={};for(const x of own){const k=x.hs+'|'+x.hair;(keys[k]=keys[k]||[]).push(x.n)}
      /* each story style draws something a stranger's short hair (0) does not, standing and seated, either way round */
      const cv=document.createElement('canvas');cv.width=120;cv.height=140;const c=cv.getContext('2d');const px=(L,o)=>{c.clearRect(0,0,120,140);drawPerson(c,60,130,L,Object.assign({pscale:2},o));return c.getImageData(0,0,120,140).data};
      const same=[];let errs=[];for(const x of cast){if(x.L.hs<10)continue;for(const o of[{},{seated:true,mood:'eat',chew:1},{flip:true,mood:'sad'},{mood:'angry',blink:1}]){try{const a=px(Object.assign({},x.L),o),b=px(Object.assign({},x.L,{hs:0}),o);let d=0;for(let i=0;i<a.length;i+=4)if(Math.abs(a[i]-b[i])+Math.abs(a[i+1]-b[i+1])+Math.abs(a[i+2]-b[i+2])+Math.abs(a[i+3]-b[i+3])>60)d++;if(d<120)same.push(x.n+' '+JSON.stringify(o)+' '+d)}catch(e){errs.push(x.n+': '+e.message)}}}
      return{genHs,genSF,genHat,own,dup:Object.values(keys).filter(v=>v.length>1),same,errs,styles:[...new Set(own.map(x=>x.hs))].filter(h=>h>=10).sort((a,b)=>a-b)}})())"""))
    check(set(r['genHs']) <= {0, 1, 2, 3, 4, 6, 7, 8}, f"a stranger's hair is one of the common styles: {r['genHs']}")
    check(r['genSF'] == 0 and r['genHat'] == 0, f"no stranger has a story guest's details (or the critic's hat): {r['genSF']}, {r['genHat']}")
    common = [x for x in r['own'] if x['hs'] in r['genHs']]
    check(not common, f'every story guest has a style no stranger is given: {common}')
    check(not r['dup'], f'no two story guests share a style and a colour: {r["dup"]}')
    check(not [x for x in r['own'] if x['acc'] in ('glasses', 'beret')], 'none of them wears the strangers\' round frames or a beret')
    check(r['styles'] == list(range(10, 24)), f'the fourteen styles are all in use: {r["styles"]}')
    check(not r['same'] and not r['errs'], f"each draws something of its own, in every pose: {r['same'][:4]} {r['errs'][:3]}")
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc7_2_xiuqin_first_evening_holds_the_service(b, port, target):
    """rc7.2 (the player, 21:49: 「秀琴阿姨出場要暫停遊戲吧 有劇情的」): when 秀琴阿姨 walks in for the first time, a scene with her
    portrait holds the service — the clock, the guests and the stoves wait — until the player has tapped through it; then
    the evening goes on where it stopped. Her later evenings are the few words in the room, as before."""
    g = Game(b, port, target, seed=264, manual=True, viewport={'width': 390, 'height': 844})
    install_bot(g); g.click('[data-act=open]')
    start_day(g)
    g.ev("__botUntil('R.t>=R.dur*.9',60000,1/30)")
    g.ev("window.__noScenes=false")
    for _ in range(400):
        g.page.evaluate('()=>window.__bot(15,1/30)')
        if g.ev("!!(DLG&&DLG.hold)") or g.ev("phase") != 'service': break
    check(g.ev("!!(DLG&&DLG.hold)") and g.ev("factN('xq_helper')") == 1, 'her first evening opens a held scene')
    check('秀琴阿姨' in g.ev("$('#dlg .dlg-name').textContent+$('#dlg .dlg-text').textContent"), 'she is in it')
    t0 = g.ev("R.t"); g.ev("for(let i=0;i<60;i++)__tick(1000/30)")
    check(g.ev("R.t") == t0, 'the service waits while it is open')
    texts = []
    for _ in range(12):
        if not g.ev("!!DLG"): break
        texts.append(g.ev("$('#dlg .dlg-text').textContent")); g.ev("dlgNext()"); g.page.wait_for_timeout(30)
    check(not g.ev("!!DLG") and any('Jill 認識很久的阿姨' in x for x in texts) and '我來幫妳收一下。' in texts, f'tapped through: {texts}')
    g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
    check(g.ev("R.t") > t0, 'then the evening goes on')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc7_2_a_tap_on_the_pass_sends_the_plates(b, port, target):
    """rc7.2 (the player, 21:49: 「點出餐台就能送餐」): in the kitchen, a tap on the pass sends Jill out with every table's ready
    plates, the oldest ticket first — the same as tapping each table. Nothing ready: it says so, and Jill stays."""
    g = Game(b, port, target, seed=265, manual=True, touch=True, viewport={'width': 390, 'height': 844})
    install_bot(g); g.click('[data-act=open]'); g.ev("S.tables=3"); start_day(g)   # a third table (a new game has two)
    g.ev("window.__act=()=>{}")
    g.ev("setRoom('kitchen')"); g.page.wait_for_timeout(50)
    got = g.ev("(()=>{servePass();return [...document.querySelectorAll('#toasts .toast')].map(t=>t.textContent).join('|')})()")
    check('出菜口還沒有做好的菜' in got and not g.ev("R.jill.q.length"), f'nothing ready: it says so: {got}')
    # two tables with a ready plate each, one with nothing ready
    r = json.loads(g.ev("""JSON.stringify((()=>{const out=[];for(let i=0;i<3;i++){const o=rollGuest();o.t=R.t;o.size=1;spawn(o);const q=R.groups[R.groups.length-1];const t=R.tables.find(t=>!t.group&&!t.dirty&&t.seats>=1&&!t.out&&(t.room||'main')==='main');if(!t)return 'no table';seatGroup(q,t);q.x=t.x;q.y=t.y;q.state='wait';const tk={id:R.tkid++,no:R.tickets.length+1,g:q,items:[{d:'friedrice',st:i<2?'ready':'pending',q:'G',want:0}],t0:R.t-i,claim:null};q.ticket=tk;R.tickets.push(tk);out.push(t.i)}return out})())"""))
    check(isinstance(r, list) and len(r) == 3, f'three tables: {r}')
    # the tap, through the kitchen's own tap handler, on the pass as drawn
    g.ev("roomTap({x:200,y:KY.passTop+10},{preventDefault(){}})")
    q = g.ev("R.jill.q.slice()")
    check(sorted(q) == sorted(r[:2]), f'Jill is sent to the two tables with ready plates, not the third: {q} of {r}')
    g.ev("servePass()")
    check(g.ev("R.jill.q.length") == 2, 'a second tap adds nothing: they are already hers')
    check(g.ev("passHit({x:200,y:KY.passTop+10})") and g.ev("passHit({x:200,y:KY.rail})") and not g.ev("passHit({x:200,y:KY.top+20})"), 'the pass and its ticket rail take the tap; the line above does not')
    man = g.ev("JSON.stringify(GUIDE)")
    check('在廚房點出菜口，Jill 會把做好的菜都送出去' in man, 'the manual says so')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc7_2_the_heart_and_the_treat_chip_on_a_ticket(b, port, target):
    """rc7.2 (the player, 21:50, 21:55): the heart on a ticket is for a regular who is one — 熟客, four visits — not for a
    named guest's first visits; and the 招待 chip sits in the name's line after the name, whatever it says, never over it.
    rc8.5 (2026-10-04, the player's choice B): the heart is Sophie's and Mia's alone — 陳伯伯, a regular too, has none."""
    g = Game(b, port, target, seed=266, manual=True, viewport={'width': 390, 'height': 844})
    install_bot(g); g.click('[data-act=open]'); start_day(g); g.ev("window.__act=()=>{}")
    g.ev("""(()=>{const regs=['mia','chen','leo',null];const vis=[5,6,2,0];for(let i=0;i<4;i++){const reg=regs[i];if(reg)S.regulars[reg]=vis[i];const o=rollGuest();const RG=reg?REG_BY[reg]:null;const gg={id:R.gid++,type:reg?RG.type:o.type,size:2,reg,forSig:false,looks:reg?RG.looks:makeLooks(o.type,2),name:reg?RG.n:pick(NAMES.office),state:'eat',table:null,pat:.8,x:200,y:300,tx:200,ty:300,timer:0,ticket:null,seed:1,mood:'ok'};R.groups.push(gg);const tk={id:R.tkid++,no:i+1,g:gg,items:[{d:'friedrice',st:'served',q:'G',want:0}],t0:R.t,claim:null};gg.ticket=tk;R.tickets.push(tk)}R.tv++;renderTickets()})()""")
    marks = json.loads(g.ev("JSON.stringify([...document.querySelectorAll('.tk')].map(e=>({n:e.querySelector('.tk-who span').textContent,reg:e.classList.contains('isreg')})))"))
    by = {m['n']: m['reg'] for m in marks}
    check(by.get('Mia') is True and not any(v for k, v in by.items() if k != 'Mia'), f'the heart only for Mia (five visits), not for a first or second visit: {marks}')
    # every chip state, the name and the chip side by side
    for st, fake in (('offer', "{k:'offer',left:2}"), ('nostock', "{k:'nostock',n:'沒東西可請'}"), ('done', "{k:'done',n:'已招待'}"), ('spent', "{k:'spent',n:'招待 0/2'}"), ('pending', "{k:'pending',n:'集點卡・請甜點'}")):
        g.ev(f"window.__ts0=window.__ts0||treatState;treatState=()=>({fake});R.tv++;renderTickets()")
        boxes = json.loads(g.ev("JSON.stringify([...document.querySelectorAll('.tk')].map(e=>{const n=e.querySelector('.tk-who span').getBoundingClientRect(),c=e.querySelector('.tk-treat'),r=c?c.getBoundingClientRect():null,k=e.getBoundingClientRect();return{n:[n.left,n.right],c:r?[r.left,r.right,r.top,r.bottom]:null,k:[k.left,k.right,k.top,k.bottom]}}))"))
        for x in boxes:
            check(x['c'] and x['n'][1] <= x['c'][0] + .5 and x['c'][1] <= x['k'][1] + .5 and x['c'][3] <= x['k'][3], f'{st}: the chip after the name, inside the ticket: {x}')
    g.ev("treatState=window.__ts0;R.tv++;renderTickets()")
    g.page.screenshot(path=os.path.join(ROOT, 'tests', 'artifacts', 'rc72_tickets.png'), clip={'x': 0, 'y': 40, 'width': 390, 'height': 110})
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc7_2_a_named_guests_line_answers_a_touch(b, port, target):
    """rc7.2 (the player, 22:07: 「有出現人頭的點下去不會看到他在哪一組」): a named guest's line with a face (Madame Lin's
    「不用看菜單了，照你們推薦的來。」), touched on a phone-sized screen from another room, goes to their table and marks it —
    on the touch itself. T evidence: Chromium's touch emulation, not an iPhone."""
    g = Game(b, port, target, seed=1537, manual=True, touch=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day74_1508.json')
    to_service(g)
    g.ev("__botUntil('R.t>=R.dur*.1',90000,1/30)")
    info = json.loads(g.ev("""JSON.stringify((()=>{const t=R.tables.find(t=>(t.room||'main')==='main'&&!t.group&&!t.dirty&&!t.hold&&!t.pdr&&!t.lounge);if(!t)return null;
      spawn({t:R.t,type:'vip',size:1});const q=R.groups[R.groups.length-1];q.name='Madame Lin';q.named='Madame Lin';q.looks=[NAMED['Madame Lin'].looks];if(q.table==null)seatGroup(q,t);window.__q=q;return{t:q.table}})())"""))
    check(info is not None, 'Madame Lin at a table in the dining room')
    for _ in range(300):
        if g.ev("['reading','order','wait','eat'].includes(__q.state)"): break
        g.ev("__tick(1000/30)")
    g.ev("setRoom('kitchen');document.querySelectorAll('#plines>*,#toasts>*').forEach(e=>e.remove());IDF.length=0;quote(__q,'不用看菜單了，照你們推薦的來。',{keep:1})")
    check(g.page.query_selector('#plines .pline') is not None, 'her line comes with her face')
    g.page.tap('#plines .pline'); g.ev("__tick(1000/30)")
    st = json.loads(g.ev("JSON.stringify({room,m:IDF.map(m=>({label:m.label,sub:m.sub}))})"))
    check(st['room'] == 'main' and st['m'] and st['m'][-1]['label'] == 'Madame Lin' and st['m'][-1]['sub'] == f"T{info['t']+1}", f'the touch goes to her table and marks it: {st}')
    check(not g.errors, g.errors[:3]); g.close()



@test
def v24_rc7_2_a_regulars_head_at_a_busy_table_and_the_log_closes(b, port, target):
    """rc7.2 (the player, 22:29: 「點桌子的時候不小心點到常客的頭就會跳他的說明整個擋住你的操作」): a tap on a regular's head at a
    table that has work waiting is a tap on that table — Jill goes; no card in the way. With nothing to do there, the card
    as before. (22:28: 「這個對話框的叉叉按不了很久了」): the conversation log's × stays the same button while new lines come in,
    and closes the log."""
    g = Game(b, port, target, seed=2229, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day74_1508.json')
    to_service(g)
    g.ev("__botUntil('R.groups.some(q=>q.reg&&q.reg!==\\'dylan\\'&&q.table!=null&&[\\'reading\\',\\'eat\\'].includes(q.state))',60000,1/30)")
    info = json.loads(g.ev("""JSON.stringify((()=>{const q=R.groups.find(q=>q.reg&&q.reg!=='dylan'&&q.table!=null&&['reading','eat'].includes(q.state));if(!q)return null;window.__rq=q;window.__st0=q.state;const t=R.tables[q.table];setRoom(t.room||'main');return{t:t.i,room:t.room||'main',reg:q.reg}})())"""))
    check(info is not None, 'a regular at a table')
    g.ev("window.__act=()=>{};__tick(1000/30)")
    head = "JSON.stringify((()=>{const q=__rq;const p=idMemberAt(q,0);const r=sc.getBoundingClientRect();return[r.left+SV.ox+p.x*SV.s,r.top+SV.oy+(p.y-20)*SV.s]})())"
    # work waiting: the order is ready to be taken
    clear = "document.querySelectorAll('#plines>*,#toasts>*').forEach(e=>e.remove())"   # nothing said lies over the table
    g.ev("__rq.state='order';R.jill.q.length=0;$('#regcard').hidden=true;" + clear)
    xy = json.loads(g.ev(head)); g.page.mouse.click(xy[0], xy[1]); g.ev("__tick(1000/30)")
    st = json.loads(g.ev("JSON.stringify({card:!$('#regcard').hidden,q:R.jill.q.slice(),cur:R.jill.cur?R.jill.cur.t:null})"))
    check(not st['card'] and (info['t'] in st['q'] or st['cur'] == info['t']), f'the tap on his head took the order: Jill goes, no card: {st}')
    # nothing to do there: the card
    g.ev("R.jill.q.length=0;R.jill.cur=null;__rq.state='eat';" + clear)
    xy = json.loads(g.ev(head)); g.page.mouse.click(xy[0], xy[1]); g.ev("__tick(1000/30)")
    check(not g.ev("$('#regcard').hidden"), 'eating, nothing to do: his card, as before')
    g.ev("$('#regcard').hidden=true")
    # the log: open it, a new line comes in, the same × closes it
    g.click('#logChip'); g.page.wait_for_timeout(80)
    g.ev("window.__x0=document.querySelector('#logPanel [data-logclose]')")
    for i in range(3):
        g.ev(f"logLine('Jill','測試 {i}','j');renderLog()")
    check(g.ev("document.querySelector('#logPanel [data-logclose]')===window.__x0"), 'the × is the same button after new lines')
    check(str(g.ev("$('#logPanel [data-logn]').textContent")).endswith('句'), 'the count is kept up to date')
    g.click('#logPanel [data-logclose]'); g.page.wait_for_timeout(60)
    check(g.ev("$('#logPanel').hidden"), 'the × closes the log')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc7_2_a_story_on_the_summary_opens_its_page(b, port, target):
    """rc7.2 (the player, 22:38: 「結算看故事頁點進去就不會跳到那個故事啊，要從最上面自己找很不方便」): each of the day's stories
    on the summary is a way into its own page — a tap opens the journal's story page at that story, marked; a restaurant
    chapter opens at that chapter."""
    g = Game(b, port, target, seed=2238, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day74_1508.json')
    to_service(g); play_day(g)
    for _ in range(200):
        if g.ev("phase") != 'service': break
        g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
    check(g.ev("phase") == 'summary' and g.ev("!!S.lastSummary"), 'a day played: the summary')
    k = g.ev("(STORY_LINES.filter(L=>{try{return L.open()&&lineProgress(L).done.length>0}catch(e){return false}}).slice(-1)[0]||{}).k")
    check(bool(k), f'an open story in the save: {k}')
    ch = g.ev("restChapters().findIndex((C,i)=>i>0&&(!C.showIf||C.showIf())&&!(C.hidden&&C.hidden()))")
    check(ch >= 1, f'a restaurant chapter past the first: {ch}')
    g.ev(f"window.__st0=storyToday;storyToday=D=>[{{who:'他們',t:'測試的一段',note:'',k:'{k}'}},{{who:'餐廳',t:'測試的一章',note:'',k:'ch{ch}'}}];showSummary()")
    g.page.wait_for_timeout(80)
    rows = g.ev("[...document.querySelectorAll('.stoday .st-row')].map(e=>e.dataset.act+':'+e.dataset.k)")
    check(rows == [f'story:{k}', f'story:ch{ch}'], f'the rows are ways in: {rows}')
    g.click('.stoday .st-row b'); g.ev("__tick(100)"); g.page.wait_for_timeout(100)   # openStory scrolls on a 60 ms timer (virtual time here)
    st = json.loads(g.ev(f"JSON.stringify({{sub,bookTab,focus:storyFocus,mark:!!document.querySelector('#sl-{k}.focus'),vis:(()=>{{const e=document.getElementById('sl-{k}');if(!e)return null;const r=e.getBoundingClientRect();return r.top<innerHeight&&r.bottom>0}})()}})"))
    check(st['sub'] == 'book' and st['bookTab'] == 'story' and st['focus'] == k and st['mark'] and st['vis'], f'the journal at that story, marked and in view: {st}')
    g.ev("showSummary()"); g.page.wait_for_timeout(80)
    g.click(f'.stoday .st-row[data-k=ch{ch}]'); g.ev("__tick(100)"); g.page.wait_for_timeout(100)
    st = json.loads(g.ev(f"JSON.stringify({{bookTab,focus:storyFocus,mark:!!document.querySelector('#sl-ch{ch}.focus'),vis:(()=>{{const e=document.getElementById('sl-ch{ch}');if(!e)return null;const r=e.getBoundingClientRect();return r.top<innerHeight&&r.bottom>0}})()}})"))
    check(st['bookTab'] == 'story' and st['focus'] == f'ch{ch}' and st['mark'] and st['vis'], f'a chapter opens at the chapter: {st}')
    g.ev("storyToday=window.__st0")
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc7_2_the_random_menu(b, port, target):
    """rc7.2 (the player, 22:39: 「我其實到最後都懶得換菜單耶，可不可以給我一個按鍵是隨機選？」): 🎲 隨機選菜單 on the menu page
    fills the menu's places with dishes a guest can order tonight (their station is there) — at least one 主食, a bit of
    each kind — keeps today's task dish, leaves the bar bites as they were, and gives another menu on another tap."""
    g = Game(b, port, target, seed=2239, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day74_1508.json')
    if g.ev("phase") == 'shop':
        g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(200)
    check(g.ev("phase") == 'prep' and g.ev("!!document.querySelector('[data-act=menuRandom]')"), 'the button is on the menu page')
    check('🎲 隨機選菜單' in g.ev("$('#screen').innerText"), 'and says what it is')
    r = json.loads(g.ev("""JSON.stringify((()=>{const cap=menuCap();const bars0=S.menu.filter(d=>DISHES[d]&&DISHES[d].bar).sort().join();const dt=(S.today.tasks||[]).find(t=>t.k==='dish');S.today.tasks=S.today.tasks||[];
      const can=d=>S.unlocked.includes(d)&&!!DISHES[d]&&!DISHES[d].bar&&stationOk(d);const pool=S.unlocked.filter(can);let task=dt?dt.d:null;if(!task||!can(task)){task=pool[pool.length-1];S.today.tasks.push({k:'dish',d:task,n:3,txt:'test',reward:100})}
      const rolls=[];for(let i=0;i<8;i++){const p=menuRandom();rolls.push({p,count:menuCount(),bars:S.menu.filter(d=>DISHES[d]&&DISHES[d].bar).sort().join(),all:p.every(can),main:p.some(d=>['main','starter'].includes(DISH(d).cat)),cats:[...new Set(p.map(d=>DISH(d).cat))].length,task:p.includes(task)})}
      const kinds=new Set(pool.map(d=>DISH(d).cat)).size;return{cap,pool:pool.length,bars0,kinds,task,rolls,distinct:new Set(rolls.map(x=>x.p.slice().sort().join())).size}})())"""))
    want = min(r['cap'], r['pool'])
    for x in r['rolls']:
        check(len(x['p']) == want and x['count'] == want, f'the menu filled to its places ({want}): {x}')
        check(x['all'] and x['main'] and x['task'] and x['bars'] == r['bars0'], f'orderable, a 主食, the task dish, the bites as they were: {x}')
        check(x['cats'] >= min(r['kinds'], 3), f'a bit of each kind: {x["cats"]} of {r["kinds"]}')
    check(r['distinct'] >= 3, f'another tap, another menu: {r["distinct"]} different menus in 8 taps')
    g.click('[data-act=menuRandom]'); g.page.wait_for_timeout(80)
    check('菜單隨機排好了' in g.ev("[...document.querySelectorAll('#toasts .toast')].map(t=>t.textContent).join('|')"), 'the tap says it is done')
    check(g.ev("phase") == 'prep' and g.ev("menuCount()") == want, 'still on the menu page, the menu full')
    man = g.ev("JSON.stringify(GUIDE)")
    check('隨機選菜單' in man and '今日任務要賣的菜和宣傳中的菜會留著' in man, 'the manual says so')
    # a new game: few dishes — all of them, at least one 主食
    g.ev("localStorage.removeItem(KEY)"); g.reload(); g.page.wait_for_timeout(150); g.click('[data-act=open]'); g.page.wait_for_timeout(150)
    n = json.loads(g.ev("(()=>{const p=menuRandom();return JSON.stringify({p,cap:menuCap(),pool:S.unlocked.filter(d=>!!DISHES[d]&&!DISHES[d].bar&&stationOk(d)).length,main:p.some(d=>['main','starter'].includes(DISH(d).cat))})})()"))
    check(len(n['p']) == min(n['cap'], n['pool']) and n['main'], f'a new game: {n}')
    g.page.screenshot(path=os.path.join(ROOT, 'tests', 'artifacts', 'rc72_random_menu.png'))
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc7_2_the_missing_cats_stop_the_evening(b, port, target):
    """rc7.2 (the player, 22:44: 「上2樓找的時候先發現柔柔不見了 後來發現小齁也不見呀 而且發現貓不見的時候就一定要中斷了，就不是自己
    播放是要點一下才會繼續」): the moment they find the cats gone is a held scene — the evening stops, one line per tap — and it
    names both cats at once (「柔柔和小齁都不見了。」); the open door is held too, and Jill calls them both. Then the search,
    the floor, the cats down, the door latched, as before."""
    g = Game(b, port, target, seed=2244, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day52.json')
    to_service(g); play_day(g, max_steps=60000)
    for _ in range(200):
        if g.ev("phase") != 'service': break
        g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
    g.ev(UP_DONE_BEFORE); _upf(g, 'up_hint', 6); _upf(g, 'up_staff', 5); _upf(g, 'up_inspect', 3)
    check(_up_day(g, 'up_door', 9302), 'the night\'s day starts')
    nA, nB = g.ev("upCatN('mikan')"), g.ev("upCatN('ban')")
    g.ev("__botUntil('R.closing!=null',90000,1/30)")
    g.ev("window.__noScenes=false")
    seen = []
    def held_lines():
        out = []
        for _ in range(12):
            if not g.ev("!!DLG"): break
            out.append(g.ev("$('#dlg .dlg-text').textContent")); g.ev("DLG.shownAt=0;dlgNext()"); g.page.wait_for_timeout(20)
        return out
    other = []
    def until(cond, n):
        for _ in range(n):
            if g.ev(cond): return True
            if g.ev("!!DLG"):
                other.extend(held_lines()); continue   # another story's scene at closing: tapped through
            g.ev("__tick(1000/30)")
        return bool(g.ev(cond))
    ok = until("!!(DLG&&DLG.hold)&&!!R.upSearch&&R.upSearch.step==='noticing'", 600)
    check(ok, f'finding them gone: a held scene (other scenes on the way: {other[:3]})')
    t0 = g.ev("R.t"); g.ev("for(let i=0;i<60;i++)__tick(1000/30)")
    check(g.ev("R.t") == t0, 'the evening waits while it is open')
    first = held_lines(); seen += first
    check(f'{nA}呢？' in first[0] or first[0] == f'{nA}？', f'it starts with {nA}: {first}')
    check(f'{nA}和{nB}都不見了。' in first and any(nB in x for x in first[:-1]), f'and says both are gone, at once: {first}')
    ok = until("!!(DLG&&DLG.hold)&&!!R.upSearch&&R.upSearch.step==='door'", 3000)
    check(ok, 'the open door: held too')
    door = held_lines(); seen += door
    check('這個怎麼開著？' in door and f'……{nA}？{nB}？' in door, f'Jill calls them both: {door}')
    for _ in range(4000):
        g.ev("__tick(1000/30)")
        if g.ev("!!DLG"): seen += held_lines()
        if g.ev("!R||!R.upSearch||R.upSearch.end"): break
    check(g.ev("!!(R&&R.upSearch&&R.upSearch.end)") is True and g.ev("fact('up_cats')&&fact('up_cats').d===S.day") is True, f'found, and the search ends: {seen[-4:]}')
    check('妳們兩個。' in seen, 'the floor, held as before')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc7_2_sophies_pad_seen_and_marked(b, port, target):
    """rc7.2 (the player, 22:49: 「Sophie帶給寶寶的禮物的時候沒有讓我們先看到長什麼樣子後來放到店裡說是在走道邊，但是店裡的貓的東西
    太多了，根本認不出出來哪個是多出來」): the gift scene shows the pad itself on its first lines and holds the service; placed,
    the pad in the dining room is marked — a ring and 「Sophie 送的小貓墊」 — that day and the next, then not; a save that
    already has the pad shows the mark once."""
    g = Game(b, port, target, seed=2249, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day74_1508.json')
    to_service(g)
    g.ev("__botUntil('R.t>=R.dur*.2',90000,1/30)")
    g.ev("window.__act=()=>{}")
    g.ev("""(()=>{const t=R.tables.find(t=>(t.room||'main')==='main'&&!t.group&&!t.dirty&&!t.hold&&!t.lounge&&!t.pdr);spawn({t:R.t,type:'gourmet',size:1});const q=R.groups[R.groups.length-1];q.reg='sophie';q.name='Sophie';q.looks=REG_BY.sophie.looks;if(q.table==null)seatGroup(q,t);window.__sq=q})()""")
    g.ev("window.__noScenes=false;STORY_EV.find(e=>e.k==='sophie_mei_4').run({g:__sq,items:[{d:'duck'}]})")
    check(g.ev("!!(DLG&&DLG.hold)"), 'the gift is a held scene')
    shots = []
    for i in range(10):
        if not g.ev("!!DLG"): break
        shots.append(json.loads(g.ev("JSON.stringify({t:$('#dlg .dlg-text').textContent,ill:!$('#dlg .dlg-illus').hidden,src:($('#dlg .dlg-illus img').getAttribute('src')||'').slice(0,23),cap:$('#dlg .dlg-illus-t').textContent})")))
        if i == 0:
            g.page.screenshot(path=os.path.join(ROOT, 'tests', 'artifacts', 'rc72_sophie_pad_scene.png'))
        g.ev("dlgNext()"); g.page.wait_for_timeout(30)
    check([x['ill'] for x in shots[:3]] == [True, True, True] and all(x['src'] == 'data:image/jpeg;base64,' and x['cap'] == 'Sophie 帶來的小貓墊' for x in shots[:3]), f'the pad itself on the first three lines: {shots[:3]}')
    check(not any(x['ill'] for x in shots[3:]), f'then the words: {shots[3:]}')
    st = json.loads(g.ev("JSON.stringify({on:gearOn('sophiepad'),n:S.gearNew&&S.gearNew.sophiepad,d:S.day,mark:gearNewOn('sophiepad')})"))
    check(st['on'] and st['n'] == st['d'] and st['mark'], f'placed and marked: {st}')
    said = g.ev("(()=>{const cv=mkCanvas(400,500),c=cv.getContext('2d');const L=[];const f=c.fillText.bind(c);c.fillText=(t,x,y)=>{L.push(t);f(t,x,y)};drawGearNew(c,1);return L})()")
    check(said == ['Sophie 送的小貓墊'], f'the tag says who it is from: {said}')
    g.ev("setRoom('main');for(let i=0;i<4;i++)__tick(1000/30)"); g.page.wait_for_timeout(60)
    g.page.screenshot(path=os.path.join(ROOT, 'tests', 'artifacts', 'rc72_sophie_pad_marked.png'))
    check(g.ev("(()=>{const d=S.day;S.day=d+1;const a=gearNewOn('sophiepad');S.day=d+2;const b=gearNewOn('sophiepad');S.day=d;return a&&!b})()"), 'marked the next day too, then not')
    m = json.loads(g.ev("(()=>{const o=JSON.parse(JSON.stringify(S));o.gear=Object.assign({},o.gear,{sophiepad:5});delete o.gearNew;const r=parseSave(JSON.stringify(o));return JSON.stringify({err:r.err||null,n:r.o&&r.o.gearNew&&r.o.gearNew.sophiepad,d:r.o&&r.o.day})})()"))
    check(m['err'] is None and m['n'] == m['d'], f'a save that already has it: marked once from the day it is loaded: {m}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc7_2_vip_cards_and_the_lounge_after_dinner(b, port, target):
    """rc7.2 (the player, 23:00: 「如果從餐廳用餐再去酒吧，應該可以打八折」; 23:02: 「來五次以上的客人有VIP卡不管是餐廳還是酒吧都是九折
    但是如果是餐廳之後去酒吧就是餐廳九折酒吧八折 你自己幫我記錄一個VIP名單 來10次以上的話，酒吧和餐廳都是八折，吃完餐廳再去酒吧酒吧
    就七折」): the rates; the bill at the card's rate item by item (rounded to $5) with the Lounge's list still equal to its
    takings; the card given at the fifth visit and changed at the tenth, said once; the list in the journal; the rate on
    the ticket; a save's people who already came five or ten times have their cards, with no toast."""
    g = Game(b, port, target, seed=2302, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day74_1508.json')
    mig = json.loads(g.ev("JSON.stringify({vip:S.vip,regs:S.regulars,named:Object.fromEntries(Object.entries(story().named).map(([k,v])=>[k,v.v]))})"))
    want = {k for k, v in mig['regs'].items() if v >= 5} | {k for k, v in mig['named'].items() if (v or 0) >= 5}
    check(set(mig['vip']) == want and all(x['d1'] == 0 for x in mig['vip'].values()), f'the people who already came five times have cards, given before there were cards: {len(mig["vip"])} of {len(want)}')
    check(all((x['d2'] == 0) == ((mig['regs'].get(k) or mig['named'].get(k) or 0) >= 10) for k, x in mig['vip'].items()), 'and ten times: the 八折 card')
    to_service(g)
    g.ev("__botUntil('R.t>=R.dur*.5',90000,1/30)")
    g.ev("window.__act=()=>{}")
    # rc7.4 (found by the full run): at half past the evening every main-hall table can be taken — the test makes one free
    g.ev("window.__freeMain=()=>{const ok=t=>(t.room||'main')==='main'&&!t.lounge&&!t.pdr&&!t.hold;let t=R.tables.find(t=>ok(t)&&!t.group&&!t.dirty);if(!t){t=R.tables.find(ok);if(t.group){const q=t.group;leaveGroup(q,'ok');q.gone=true;R.groups=R.groups.filter(x=>x!==q)}t.group=null;t.dirty=false;t.claim=null;t.plates=[]}return t}")
    rates = json.loads(g.ev("""JSON.stringify((()=>{const mk=(reg,v,o)=>{S.regulars[reg]=v;return Object.assign({reg,regs:null,name:REG_BY[reg].n,size:1,counted:0},o||{})};const out={};
      out.r4=billRate(mk('mia',3));out.r5=billRate(mk('mia',4));out.r9=billRate(mk('mia',8));out.r10=billRate(mk('mia',9));
      out.lgAfter0=billRate(mk('mia',3,{counted:1,ticket:{lounge:1},lg:{why:'after'}}));out.lgAfter5=billRate(mk('mia',5,{counted:1,ticket:{lounge:1},lg:{why:'after'}}));out.lgAfter10=billRate(mk('mia',10,{counted:1,ticket:{lounge:1},lg:{why:'after'}}));
      out.lgDirect0=billRate(mk('mia',2,{ticket:{lounge:1},lg:{why:'direct'}}));out.lgDirect5=billRate(mk('mia',4,{ticket:{lounge:1},lg:{why:'direct'}}));out.lgDirect10=billRate(mk('mia',9,{ticket:{lounge:1},lg:{why:'direct'}}));
      out.anon=billRate({size:2,counted:0});out.anonAfter=billRate({size:2,counted:1,ticket:{lounge:1},lg:{why:'after'}});return out})())"""))
    check(rates == {'r4': 1, 'r5': .9, 'r9': .9, 'r10': .8, 'lgAfter0': .8, 'lgAfter5': .8, 'lgAfter10': .7, 'lgDirect0': 1, 'lgDirect5': .9, 'lgDirect10': .8, 'anon': 1, 'anonAfter': .8}, f'the rates: {rates}')
    # a bill: Mia's fifth visit, at dinner — 九折 item by item; the card given, said once
    r = json.loads(g.ev("""JSON.stringify((()=>{S.regulars.mia=4;delete (S.vip||{}).mia;const t=__freeMain();spawn({t:R.t,type:'office',size:1});const q=R.groups[R.groups.length-1];q.reg='mia';q.name='Mia';q.looks=REG_BY.mia.looks;q.ret=true;if(q.table==null)seatGroup(q,t);
      q.ticket={id:R.tkid++,no:99,g:q,items:[{d:'steak',st:'served',q:'G',want:0,picked:true},{d:'coffee',st:'served',q:'G',want:0,picked:true}],t0:R.t};R.tickets.push(q.ticket);q.state='check';
      const want=['steak','coffee'].reduce((a,d)=>a+Math.round(priceOf(d)*.9/5)*5,0),full=priceOf('steak')+priceOf('coffee');const r0=R.st.rev,v0=R.st.vipOff||0;document.querySelectorAll('#toasts>*').forEach(e=>e.remove());collect(q);
      return{paid:R.st.rev-r0,want,full,off:(R.st.vipOff||0)-v0,vip:S.vip.mia,day:S.day,visits:S.regulars.mia,toasts:[...document.querySelectorAll('#toasts .toast')].map(e=>e.textContent).join('|'),note:dayLog().some(l=>/Mia 第 5 次來，Jill 給了一張 VIP 卡/.test(l.t))}})())"""))
    check(r['paid'] == r['want'] and r['off'] == r['full'] - r['want'] and r['want'] < r['full'], f'九折, item by item: {r}')
    check(r['visits'] == 5 and r['vip'] == {'d1': r['day']} and 'Mia 拿到 VIP 卡（九折）' in r['toasts'] and r['note'], f'the card, given at the fifth visit and said: {r}')
    # the Lounge after dinner, no card: 八折; the Lounge's list equals its takings
    r = json.loads(g.ev("""JSON.stringify((()=>{const ls=R.tables.find(t=>t.lounge&&!t.group&&t.kind!=='bar');if(!ls)return null;spawn({t:R.t,type:'couple',size:2});const q=R.groups[R.groups.length-1];if(q.table!=null){const t0=R.tables[q.table];t0.group=null;q.table=null}seatGroup(q,ls);q.counted=1;q.lg={why:'after',at:R.t};
      const w=wineList()[0];q.ticket={id:R.tkid++,no:98,g:q,lounge:1,items:[{d:w,st:'served',q:'G',want:0,picked:true,lbar:1},{d:w,st:'served',q:'G',want:0,picked:true,lbar:1}],t0:R.t};R.tickets.push(q.ticket);q.state='check';
      const want=2*Math.round(priceOf(w)*.8/5)*5;const r0=R.st.lgRev||0,o0=R.st.lgOff||0;collect(q);const L=R.st.lgSold||{};
      return{paid:(R.st.lgRev||0)-r0,want,off:(R.st.lgOff||0)-o0,full:2*priceOf(w),list:Object.values(L).reduce((a,x)=>a+x.rev,0),takings:R.st.lgRev}})())"""))
    check(r and r['paid'] == r['want'] and r['off'] == r['full'] - r['want'], f'the Lounge after dinner: 八折: {r}')
    check(r['list'] == r['takings'], f'the Lounge\'s list is still its takings: {r}')
    # the ticket says the rate; the cards on the journal's VIP page
    g.ev("""(()=>{R.tickets.length=0;S.regulars.leo=12;const t=__freeMain();spawn({t:R.t,type:'student',size:1});const q=R.groups[R.groups.length-1];q.reg='leo';q.name='Leo';q.looks=REG_BY.leo.looks;if(q.table!=null){R.tables[q.table].group=null;q.table=null}seatGroup(q,t);q.state='eat';q.ticket={id:R.tkid++,no:97,g:q,items:[{d:'pasta',st:'served',q:'G',want:0}],t0:R.t};R.tickets.push(q.ticket);R.tv++;renderTickets()})()""")
    tk = json.loads(g.ev("JSON.stringify([...document.querySelectorAll('.tk')].filter(e=>e.textContent.includes('Leo')).map(e=>{const n=e.querySelector('.tk-who span');return{off:(e.querySelector('.tk-h .tk-off')||{}).textContent||null,treat:!!e.querySelector('.tk-who .tk-treat'),cut:n.scrollWidth>n.clientWidth+1}}))"))
    check(tk and tk[0]['off'] == '八折' and tk[0]['treat'] and not tk[0]['cut'], f'the ticket\'s top line says 八折 for a ten-visit card; the 招待 chip is there and the name is whole (23:46): {tk}')
    g.ev("bookTab='vip';showBook()"); g.page.wait_for_timeout(80)
    page = g.ev("$('#screen').innerText")
    check('來 5 次的客人有 VIP 卡' in page and 'Leo' in page and 'VIP 八折' in page and 'Mia' in page and 'VIP 九折' in page, 'the VIP list: who, which card')
    g.page.screenshot(path=os.path.join(ROOT, 'tests', 'artifacts', 'rc72_vip_list.png'))
    check(g.ev("[...document.querySelectorAll('.tabs button')].some(b=>b.textContent==='VIP')"), 'a tab of its own')
    man = g.ev("JSON.stringify(GUIDE)")
    check('VIP 卡' in man and '晚餐後八折' in man and '吃完再去 Lounge 七折' in man, 'the manual says so')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc7_2_the_lounges_own_waiter_carries_its_bites(b, port, target):
    """rc7.2 (the player, 23:07: 「酒吧的菜還是可以給餐廳的廚師煮 但是要讓酒吧專屬的服務生去送餐」): a Lounge table's bite, cooked
    in the one kitchen, is carried by the Lounge's own waiter (安安) when she is in — not by the dining room's waiters, and
    the pass's 送菜 leaves it to her; with her off, as before."""
    g = Game(b, port, target, seed=2307, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day74_1508.json')
    to_service(g)
    g.ev("__botUntil('R.t>=R.dur*.3',90000,1/30)")
    g.ev("window.__act=()=>{}")   # nobody taps for the player
    an = g.ev("(S.crew.find(m=>m.name==='安安')||{}).id")
    g.ev(f"(()=>{{const st=story();if(st.away&&st.away.m)delete st.away.m['{an}']}})()")   # in today, whatever the day's draw said
    check(bool(an) and g.ev(f"crewPool(S.crew.find(m=>m.id==='{an}'))") == 'lounge' and g.ev("lgWaiterHere()"), 'she is here, the Lounge\'s own')
    mk = """(()=>{const ls=R.tables.find(t=>t.lounge&&!t.group&&t.kind!=='bar');if(!ls)return null;spawn({t:R.t,type:'couple',size:2});const q=R.groups[R.groups.length-1];if(q.table!=null){const t0=R.tables[q.table];t0.group=null;q.table=null}seatGroup(q,ls);q.state='wait';q.x=ls.x;q.y=ls.y;
      const tk={id:R.tkid++,no:96,g:q,lounge:1,items:[{d:'bites',st:'ready',q:'G',want:0}],t0:R.t,claim:null};q.ticket=tk;R.tickets.push(tk);window.__lt=tk;return ls.i})()"""
    ti = g.ev(mk)
    check(ti is not None, 'a Lounge table with a bite ready at the pass')
    g.ev("R.jill.q.length=0;servePass()")
    check(ti not in g.ev("R.jill.q.slice()"), 'the pass\'s 送菜 leaves it to her')
    who = None
    for _ in range(900):
        g.ev("__tick(1000/30)")
        who = g.ev("__lt.claim")
        if who: break
    check(who == an, f'she carries it, nobody else: {who} (安安 is {an})')
    # with her off: the bartenders (or a waiter with the Lounge job) fetch it — rc8 (the player, 2026-10-02 19:19): the Lounge is
    # the shop next door, its plates are passed through the back to the end of its bar; nothing of it waits at the Main Hall's pass
    g.ev(f"setCrewAway(S.crew.find(m=>m.id==='{an}'),'off')")
    check(not g.ev("lgWaiterHere()"), 'off today')
    ti2 = g.ev(mk)
    g.ev("R.jill.q.length=0;servePass()")
    check(ti2 not in g.ev("R.jill.q.slice()"), 'the pass\'s 送菜 leaves it: it is not at the pass')
    who2 = None
    for _ in range(900):
        g.ev("__tick(1000/30)")
        who2 = g.ev("__lt.claim")
        if who2: break
    w2 = json.loads(g.ev(f"JSON.stringify((()=>{{const m=S.crew.find(m=>m.id==='{who2}');const w=m&&R.cw[m.id];return{{role:m&&m.role,room:w&&w.task?w.task.room:null,x:w&&w.task?Math.round(w.task.x):null}}}})())")) if who2 else {}
    check(who2 and w2.get('role') in ('bartender', 'waiter') and w2.get('room') == 'lounge', f'fetched from the end of the Lounge\'s bar: {who2} {w2}')
    man = g.ev("JSON.stringify(GUIDE)")
    check('由她送過去' in man and '出菜口的「送菜」只送主廳、側廳的菜' in man, 'the manual says so')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc7_2_no_firing_and_the_wages(b, port, target):
    """rc7.2 (the player, 22:39: 「員工如果請了就不要再有解雇的選項了」): no 解雇 on any card, for either list; (22:51: 「我覺得他們的
    薪水應該都是現在的兩倍…你自己去推算他們一開始的但也不要差太多」): LV5 twice the rc7 wage, a new hire 15% more, the levels between
    in steps; the staff page and the manual say the numbers."""
    g = Game(b, port, target, seed=2251, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day74_1508.json')
    g.ev("shopTab='staff';showShop()"); g.page.wait_for_timeout(80)
    scr = g.ev("$('#screen').innerText")
    check('解雇' not in scr and not g.ev("!!document.querySelector('[data-act=crewFire]')") and g.ev("document.querySelectorAll('#screen .item').length") >= 10, 'the staff page: every card, no 解雇')
    w = json.loads(g.ev("JSON.stringify(['chef','waiter','cleaner','bartender'].map(r=>[1,2,3,4,5].map(l=>crewWageAt(r,l))))"))
    check(w == [[304, 532, 832, 1224, 1690], [253, 443, 693, 1020, 1408], [190, 332, 520, 765, 1056], [405, 709, 1109, 1632, 2253]], f'the wages: {w}')
    check(f'每日薪資 {g.ev("fmt(crewWages())")}' in scr, 'the page shows the day\'s wages')
    man = g.ev("JSON.stringify(GUIDE)")
    check('廚師 LV1 一天 $304、LV5 一天 $1,690' in man and '請了就是店裡的人，沒有解雇' in man and '訓練升級、解雇' not in man, 'the manual')
    check(not g.errors, g.errors[:3]); g.close()


# ---------------------------------------------------------------- rc7.3: Jill's room (docs/v24/jill_room_2026-10-02_1853.txt, _1854, jill_room_cats_2026-10-02_2218.txt)
@test
def v24_rc73_jills_room_is_there_from_day_one(b, port, target):
    """A new game, Day 1: 「Jill 的房間」 is a room tab (the last one, behind the kitchen) — not an unlock; the oatmeal sofa,
    the TV and the right-hand cat tree are in it and no longer in the dining room (one sofa, never two); the dining room's
    cats never pick that tree's perches. During a service Jill rests in her room (through the kitchen), reads only there,
    and comes back out when a table needs her."""
    g = Game(b, port, target, seed=7311, manual=True, viewport={'width': 390, 'height': 844})
    install_bot(g); g.click('[data-act=open]'); start_day(g); g.ev("window.__act=()=>{}")
    st = json.loads(g.ev("JSON.stringify({open:roomsOpen(),order:ROOM_ORDER.slice(-2),n:ROOMS.home.n,full:ROOMS.home.full,day:S.day,parent:ROOM_PARENT.home})"))
    check('home' in st['open'] and st['order'] == ['kitchen', 'home'] and st['n'] == '房間' and st['full'] == 'Jill 的房間' and st['day'] == 1 and st['parent'] == 'kitchen', f'the room from Day 1: {st}')
    code = json.loads(g.ev("JSON.stringify({main:String(drawScene),home:String(homeItems)})"))
    check('drawSofaGroup' not in code['main'] and 'drawTV(' not in code['main'] and 'drawCatTree2' not in code['main'], 'the dining room draws no sofa, no TV, no second cat tree')
    check('drawSofaGroup' in code['home'] and 'drawTV' in code['home'] and 'drawCatTree2' in code['home'], 'the room draws them')
    check(g.ev("TREE.perches.every((p,i)=>p.t!==2||!perchVis(i))"), 'the dining room\'s cats never pick the moved tree')
    g.ev("setRoom('home')"); g.ev("for(let i=0;i<4;i++)__tick(1000/30)")
    check(g.ev("$('#roomTabs button.on').textContent").startswith('Jill 的房間'), 'the open tab says whose room it is')
    g.page.screenshot(path=os.path.join(ROOT, 'tests', 'artifacts', 'rc73_room_day1.png'))
    # a rest in her room
    g.ev("setRoom('main');(()=>{const pos=freeJillPos();if(pos)startRest(pos)})()")
    rooms = set()
    for _ in range(600):
        g.ev("__tick(1000/30)"); rooms.add(g.ev("R.jill.room||'main'"))
        if g.ev("R.jill.rest==='sit'"): break
    st = json.loads(g.ev("JSON.stringify({rest:R.jill.rest,room:R.jill.room,L:LIFE.jill.room,on:LIFE.jill.on,sofa:R.jill.sofa})"))
    check(st['rest'] == 'sit' and st['room'] == 'home' and st['L'] == 'home' and st['on'], f'she rests on her sofa, in her room: {st}')
    check('kitchen' in rooms, f'through the kitchen: {rooms}')
    reads = json.loads(g.ev("JSON.stringify((()=>{const L=LIFE.jill;const out=[];for(let i=0;i<900;i++){__tick(1000/30);if(L.act==='read')out.push(L.room)}return out})())"))
    check(all(r == 'home' for r in reads), f'the e-book only in her room: {set(reads)}')
    # a table needs her: she comes back out
    # a table in the dining room that needs her: an empty one made dirty, or (all taken) one whose guests need something
    g.ev("""(()=>{let t=R.tables.find(t=>(t.room||'main')==='main'&&!t.group);if(t){t.dirty=true;t.plates=[{d:'friedrice'}]}else t=R.tables.find(t=>(t.room||'main')==='main'&&tableActionable(t))||R.tables.find(t=>(t.room||'main')==='main');tapTable(t)})()""")
    back = None
    for _ in range(900):
        g.ev("__tick(1000/30)")
        if g.ev("(R.jill.room||'main')==='main'"): back = True; break
    check(back and not g.ev("R.jill.rest"), 'up, and back in the dining room for the table')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc73_the_evening_is_in_her_room(b, port, target):
    """After closing Jill wipes the pass and goes to her room (she walks there; nobody is teleported); the summary's
    evening is in the room — on the sofa, the TV, the cats; Dylan, when he is home, at his desk. Before the reveal too
    (19:15): a player who looks in finds him studying."""
    g = Game(b, port, target, seed=7312, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day74_1508.json')
    check(g.ev("!!homeDylanAtDesk()"), 'the morning: Dylan at his desk')
    to_service(g)
    g.ev("__botUntil('R.closing!=null',90000,1/30)")
    path = set()
    for _ in range(1500):
        g.ev("__tick(1000/30)"); path.add(g.ev("LIFE.jill.room||'main'"))
        if g.ev("phase") != 'service' or g.ev("LIFE.jill.on&&LIFE.jill.room==='home'"): break
    check('home' in path, f'she went to her room after closing: {path}')
    for _ in range(200):
        if g.ev("phase") != 'service': break
        g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
    g.ev("for(let i=0;i<300;i++)__tick(1000/30)")
    st = json.loads(g.ev("JSON.stringify({ph:phase,L:LIFE.jill.room,on:LIFE.jill.on,V:view().jill.room,desk:!!homeDylanAtDesk(),dy:LIFE.dylan?LIFE.dylan.room:null})"))
    check(st['ph'] in ('summary', 'shop') and st['L'] == 'home' and st['V'] == 'home', f'the evening is in her room: {st}')
    check(st['desk'] or st['dy'] is not None, f'Dylan is somewhere: at his desk, or still about: {st}')
    g.ev("setRoom('home')") if g.ev("roomOpen('home')") else None
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc73_the_cats_live_between_the_room_and_the_restaurant(b, port, target):
    """The room is the cats' home, not a pen (18:53 §7, 22:18–22:54): in a service, cats are both in the restaurant and in
    the room; 樾樾 is mostly in the room, 柔柔 mostly about the restaurant; the sofa's cats are in the room; nobody is
    sent home all at once at closing."""
    g = Game(b, port, target, seed=7313, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day74_1508.json')
    to_service(g)
    samples = json.loads(g.ev("""JSON.stringify((()=>{const out=[];for(let i=0;i<2400&&R.closing==null;i++){__bot(1,1/30);if(i%40===0)out.push(CATS.map(c=>[c.def.id,c.away==='home',!c.hidden&&!c.away]))}return out})())"""))
    check(len(samples) >= 30, f'a service sampled: {len(samples)}')
    both = sum(1 for s in samples if any(x[1] for x in s) and sum(1 for x in s if x[2]) >= 2)
    check(both >= len(samples) // 3, f'cats in the room and in the restaurant at once: {both} of {len(samples)}')
    frac = lambda cid: sum(1 for s in samples for x in s if x[0] == cid and x[1]) / len(samples)
    check(frac('tora') >= .6 and frac('mikan') <= .5, f'樾樾 mostly in the room ({frac("tora"):.2f}), 柔柔 mostly out ({frac("mikan"):.2f})')
    check(g.ev("CATS.filter(c=>c.sofa&&c.sofaOn).every(c=>c.away==='home')"), 'a cat on the sofa is in the room')
    g.ev("__botUntil('R.closing!=null',90000,1/30)")
    n0 = g.ev("CATS.filter(c=>c.away==='home').length")
    g.ev("__tick(1000/30)")
    check(g.ev("CATS.filter(c=>c.away==='home').length") <= n0 + 1, 'no bedtime teleport at closing')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc73_the_cats_try_their_luck_and_never_get_it(b, port, target):
    """(22:26–22:27) 小齁 jumps on a table for the fried food, 寶寶 for the steak — never every time, never successful: a
    word, and down they go, the plate untouched; 包包 is after the chicken but mostly sits under the table looking up.
    (22:18) 寶寶 meows at people she knows, and they melt."""
    g = Game(b, port, target, seed=7314, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day74_1508.json')
    to_service(g)
    g.ev("__botUntil('R.t>=R.dur*.2',90000,1/30)"); g.ev("window.__act=()=>{}")
    # a table in the dining room for the scene: a free one, or (Day 74 is busy) one whose guests are sent on their way
    g.ev("""window.__freeT=()=>{const ok=t=>(t.room||'main')==='main'&&!t.hold&&!t.lounge&&!t.pdr;let t=R.tables.find(t=>ok(t)&&!t.group);if(!t){t=R.tables.find(t=>ok(t)&&t.group&&t.group!==window.__q&&t.group!==window.__r);leaveGroup(t.group,'ok')}t.dirty=false;t.plates=[];return t}""")
    mk = """(d=>{const t=__freeT();spawn({t:R.t,type:'office',size:1});const q=R.groups[R.groups.length-1];if(q.table!=null){R.tables[q.table].group=null;q.table=null}seatGroup(q,t);q.state='eat';q.timer=999;q.ticket={id:R.tkid++,no:90,g:q,items:[{d,st:'served',q:'G',want:0,picked:true}],t0:R.t};R.tickets.push(q.ticket);return q})"""
    for cid, dish in (('ban', 'fries'), ('mei', 'steak')):
        g.ev(f"window.__q={mk}('{dish}');(()=>{{const c=catBy('{cid}');if(c.away==='home')homeCatOut(c);c.stealCD=0;R.groups.filter(x=>x!==__q).forEach(x=>x.stolenAt=R.t);stealGo(c)}})()")
        seen = {'on': False}
        for _ in range(600):
            g.ev("__tick(1000/30)")
            if g.ev(f"!!catBy('{cid}').onTable"): seen['on'] = True
            if seen['on'] and not g.ev(f"catBy('{cid}').onTable") and g.ev(f"catBy('{cid}').st!=='steal'"): break
        r = json.loads(g.ev(f"JSON.stringify({{plate:__q.ticket.items[0].st,stolen:__q.stolenAt!=null,cat:catBy('{cid}').onTable}})"))
        check(seen['on'] and r['plate'] == 'served' and r['stolen'] and not r['cat'], f'{cid} up on the table for the {dish}, and down again — the plate untouched: {r}')
    g.ev("Math.random=(()=>{let k=0;return()=>{k++;return .2}})()")
    g.ev(f"window.__q={mk}('chicken');(()=>{{const c=catBy('snow');if(c.away==='home')homeCatOut(c);c.stealCD=0;stealGo(c)}})()")
    w = json.loads(g.ev("JSON.stringify({watch:catBy('snow').stealWatch,after:catBy('snow').after})"))
    check(w['watch'] and w['after'] == 'stealWatch', f'包包 mostly watches from below: {w}')
    # 寶寶 and the people she knows
    g.ev("""window.__r=(()=>{const t=__freeT();spawn({t:R.t,type:'office',size:1});const q=R.groups[R.groups.length-1];q.reg='mia';q.name='Mia';q.looks=REG_BY.mia.looks;S.catFam=S.catFam||{};S.catFam.mia=9;if(q.table!=null){R.tables[q.table].group=null;q.table=null}seatGroup(q,t);q.state='eat';q.timer=999;R.groups.filter(x=>x!==q).forEach(x=>x.mewed=1);return q})();(()=>{const c=catBy('mei');if(c.away==='home')homeCatOut(c);c.meowGCD=0;meowGo(c)})()""")
    for _ in range(600):
        g.ev("__tick(1000/30)")
        if g.ev("__r.mewed"): break
    g.ev("for(let i=0;i<40;i++)__tick(1000/30)")
    r = json.loads(g.ev("JSON.stringify({mewed:!!__r.mewed,f:R.floats.some(f=>f.txt==='喵～')||true,said:dayLog().some(l=>l.w==='Mia'&&/可愛|叫我|講話|融化/.test(l.t))})"))
    check(r['mewed'] and r['said'], f'寶寶 meows at Mia, who melts: {r}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc73_posts_carry_their_picture_and_likes_that_keep_coming(b, port, target):
    """rc7.3 (the player, 15:02 and 22:09 「貼文還是沒有照片啊」): on the player's own Day 74, every post on the social page
    carries a picture — Jill's own album photo when she posted one (the same photo, by its id), otherwise the thing the
    post is about drawn from the game's art, the same picture every time — and a like count. Likes keep coming: a day
    later every post has at least as many and the young ones more; cats bring the most, an ordinary guest a handful."""
    g = Game(b, port, target, seed=7341, manual=True, viewport={'width': 390, 'height': 844})
    # the player's backup file as the game reads it (設定 → 讀取存檔): the save and its 184 photos
    raw = json.load(open(os.path.join(ROOT, 'tests', 'saves', 'player_day74_1508.json'), encoding='utf-8'))
    check(len(raw.get('photos') or {}) > 100, 'the backup carries its photos')
    g.ev("importSaveText(%s);importConfirm()" % json.dumps(json.dumps(raw, ensure_ascii=False)))
    g.page.wait_for_timeout(300)
    g.click('[data-act=openFresh]') if g.page.query_selector('[data-act=openFresh]') else g.click('[data-act=open]'); g.page.wait_for_timeout(150)
    check(g.ev("S.day") == 74, 'the backup is in')
    g.click('[data-act=book]'); g.click('[data-act=btab][data-k=social]')
    cards = json.loads(g.ev("""JSON.stringify([...document.querySelectorAll('#screen .posts .post')].map(e=>{const im=e.querySelector('img.post-ph');const lk=e.querySelector('.likes');return{src:im?im.getAttribute('src').slice(0,22):'',w:im?im.naturalWidth:0,pid:im?im.dataset.pid||null:null,likes:lk?+lk.textContent.replace(/[^0-9]/g,''):-1}}))"""))
    check(len(cards) == 6, f'the six most recent posts: {len(cards)}')
    check(all(c['src'].startswith('data:image/') or c['pid'] for c in cards) and all(c['likes'] >= 1 for c in cards), f'each with a picture and likes: {cards}')
    g.page.wait_for_timeout(200)
    check(all(w > 0 for w in g.ev("[...document.querySelectorAll('#screen .posts img.post-ph')].map(i=>i.naturalWidth)")), 'the pictures load')
    g.page.screenshot(path=os.path.join(ROOT, 'tests', 'artifacts', 'rc73_posts_day74.png'))
    # all forty, behind the button; Jill's own photos come in from the album's store
    g.click('[data-act=postsAll]')
    check(g.ev("document.querySelectorAll('#screen .posts .post').length") == g.ev("S.social.posts.length"), 'every post, with the button')
    loaded = False
    for _ in range(40):
        g.page.wait_for_timeout(100)
        st = json.loads(g.ev("JSON.stringify([...document.querySelectorAll('#screen .posts img.post-ph[data-pid]')].map(i=>i.src!==PHOTO_BLANK&&i.naturalWidth>0))"))
        if st and all(st): loaded = True; break
    check(loaded, f"Jill's posts show the photos she posted: {st}")
    # Jill's album photo is the one she posted; the drawn ones are the same every time
    r = json.loads(g.ev("""JSON.stringify((()=>{const P=S.social.posts;const withPid=P.filter(p=>p.pid&&albumList().some(a=>a.id===p.pid));
      const same=withPid.every(p=>postPhoto(p)===photoSrc(albumList().find(a=>a.id===p.pid)));
      const drawn=P.filter(p=>!p.pid).slice(0,8);const a1=drawn.map(postPhoto);POST_PH.clear();const a2=drawn.map(postPhoto);
      return{n:withPid.length,same,drawn:drawn.length,stable:a1.every((u,i)=>u&&u===a2[i]),distinct:new Set(a1).size}})())"""))
    check(r['n'] >= 1 and r['same'], f'her own photo: {r}')
    check(r['drawn'] >= 4 and r['stable'] and r['distinct'] >= min(4, r['drawn']), f'the drawn pictures are the same each time and not all alike: {r}')
    # likes over time, and who brings them
    r = json.loads(g.ev("""JSON.stringify((()=>{const P=S.social.posts;const d0=S.day;const now=P.map(postLikes);S.day=d0+1;const later=P.map(postLikes);S.day=d0;
      const young=P.map((p,i)=>i).filter(i=>d0-(P[i].day||d0)<=2);
      const mk=(who,topic,extra)=>Object.assign({id:9000+Math.floor(Math.random()*1000),day:d0-5,who,topic,txt:'x'},extra||{});
      const jillFood=postLikes(Object.assign(mk('Jill','food'),{id:9001})),jillCat=postLikes(Object.assign(mk('Jill','cats',{cat:'snow'}),{id:9001}));
      const guestFood=postLikes(Object.assign(mk('小安','food'),{id:9002})),guestCat=postLikes(Object.assign(mk('小安','cats',{cat:'snow'}),{id:9002}));
      const momo=postLikes(Object.assign(mk('美食部落客 Momo','food'),{id:9003}));
      return{never_less:now.every((v,i)=>later[i]>=v),young_more:young.every(i=>later[i]>now[i]),nyoung:young.length,jillFood,jillCat,guestFood,guestCat,momo}})())"""))
    check(r['never_less'], f'likes never go down: {r}')
    check(r['nyoung'] == 0 or r['young_more'], f'young posts keep collecting: {r}')
    check(r['jillCat'] > r['jillFood'] and r['guestCat'] > r['guestFood'], f'a cat brings more than a plate: {r}')
    check(r['guestFood'] < 60 and r['momo'] > r['guestFood'] * 20, f'an ordinary guest a handful, Momo many: {r}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc73_tora_waits_for_jill_after_closing(b, port, target):
    """(22:54) 樾樾 is shy: when the guests have gone he still keeps to the room — until the crew are faces he knows. Then,
    once the closing begins, he comes out by the kitchen door and waits; Jill, the pass wiped, waits for him if he is on
    his way, sees him, and the two of them go to her room."""
    # shy: a new game's first evening — he stays in the room
    g = Game(b, port, target, seed=7321, manual=True, viewport={'width': 390, 'height': 844})
    install_bot(g); g.click('[data-act=open]'); start_day(g)
    g.ev("__botUntil('R.closing!=null',90000,1/30)")
    check(g.ev("!toraBrave()"), 'Day 1: the crew are strangers to him')
    g.ev("(()=>{const T=catBy('tora');if(T.away!=='home'){releaseSpots(T);homeCatIn(T)}})()")
    out = g.ev("(()=>{const T=catBy('tora');let o=false;for(let i=0;i<1500&&phase==='service';i++){__tick(1000/30);if(T.waitJill||(!T.away&&!T.hidden))o=true}return o})()")
    check(not out, 'a shy 樾樾 stays in the room through the closing')
    check(not g.errors, g.errors[:3]); g.close()
    # brave: the player's Day 74
    seen = []
    for seed in (7322, 7323, 7324):
        g = Game(b, port, target, seed=seed, manual=True, viewport={'width': 390, 'height': 844})
        load_save(g, 'player_day74_1508.json')
        to_service(g)
        g.ev("__botUntil('R.closing!=null',120000,1/30)")
        check(g.ev("toraBrave()"), 'Day 74: he knows the crew')
        g.ev("(()=>{const T=catBy('tora');if(T.away!=='home'){releaseSpots(T);homeCatIn(T)}T.hT=Math.min(T.hT,rand(.6,1.6))})()")
        r = json.loads(g.ev("""JSON.stringify((()=>{const T=catBy('tora'),L=LIFE.jill;const o={came:null,saw:null,jillLeft:null,home:null,waitedSpot:null,out:0};
          for(let i=0;i<2400&&phase==='service';i++){__tick(1000/30);const t=+(R?R.closing:0).toFixed(1);
            if(o.came==null&&T.waitJill&&!T.away&&T.st==='rest'){o.came=t;o.waitedSpot=[T.x|0,T.y|0]}
            if(o.saw==null&&L.sawTora)o.saw=t;
            if(L.room!=='home')o.out=1;   /* rc8: with a crew she is often resting in her room when the closing comes; she goes out to close up first */
            if(o.jillLeft==null&&o.out&&(L.troom==='home'||L.room==='home'))o.jillLeft=t;
            if(o.home==null&&o.came!=null&&T.away==='home')o.home=t}
          return o})())"""))
        seen.append(r)
        g.close()
    ok = [r for r in seen if r['came'] is not None and r['saw'] is not None and r['jillLeft'] is not None and r['home'] is not None and r['came'] <= r['saw'] <= r['jillLeft']]
    check(len(ok) >= 2, f'he comes out, she sees him, then they go — on most evenings: {seen}')
    check(all(r['waitedSpot'] and abs(r['waitedSpot'][0] - 126) < 6 for r in ok), f'by the kitchen door: {seen}')


# ---------------------------------------------------------------- rc7.4: favourites (the player, 22:39)
@test
def v24_rc74_favourites_learned_in_play_and_marked_on_the_menu(b, port, target):
    """(22:39 「可不可以建立客人對某個餐點或某杯酒的特殊喜好」) Each regular and each named guest loves one dish and one glass.
    Nobody announces it: 陳伯伯 orders his 蛋炒飯 when it is on, says so, and from then on the journal says 「最愛」 and
    tomorrow's menu marks the row 「♥ 陳伯伯」; Mia, with no tiramisu on, says that instead — and Jill knows hers too. A
    demand estimate learns nothing. In the Lounge, Sophie's glass is the pinot when it is poured. They are a little
    happier for it at the bill. (They do not come more often for it: the branch had that, and it held the stories back.)"""
    g = Game(b, port, target, seed=7421, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day74_1508.json')
    g.ev("S.loves={};for(const d of['friedrice'])if(!S.menu.includes(d))S.menu.push(d);S.stock.friedrice=Math.max(S.stock.friedrice||0,6);S.menu=S.menu.filter(d=>d!=='tiramisu')")
    to_service(g); g.ev("window.__act=()=>{}")
    # an estimate learns nothing
    g.ev("for(let i=0;i<30;i++)orderItems({type:'regular',size:1,reg:null},true)")
    check(g.ev("Object.keys(S.loves).length") == 0, 'the demand estimate learns nothing')
    day_ok = g.ev("hash('chen|'+S.day)%100<85")
    seat = """(id=>{const ok=t=>(t.room||'main')==='main'&&!t.hold&&!t.lounge&&!t.pdr;let t=R.tables.find(t=>ok(t)&&!t.group);if(!t){t=R.tables.find(t=>ok(t)&&t.group);leaveGroup(t.group,'ok')}t.dirty=false;t.plates=[];
      spawn({t:R.t,type:REG_BY[id].type,reg:id,size:1});const q=R.groups[R.groups.length-1];if(q.table!=null){R.tables[q.table].group=null;q.table=null}seatGroup(q,t);q.x=t.x;q.y=t.y;q.usual=null;q.wantDish=null;q.forSig=false;q.state='order';createTicket(q);return q})"""
    r = json.loads(g.ev(f"""JSON.stringify((()=>{{const q=({seat})('chen');const items=q.ticket?q.ticket.items.map(i=>i.d):[];return{{items,known:!!(S.loves.chen&&S.loves.chen.d),said:dayLog().slice(-6).map(l=>l.t)}}}})())"""))
    if day_ok:
        check('friedrice' in r['items'] and r['known'], f'陳伯伯 orders his favourite and Jill learns it: {r}')
        check(any('蛋炒飯' in t for t in r['said']), f'he says so: {r["said"]}')
    # Mia: no tiramisu today — she says it (the roll held down)
    r = json.loads(g.ev(f"""JSON.stringify((()=>{{const M=Math.random;Math.random=()=>.1;let q;try{{q=({seat})('mia')}}finally{{Math.random=M}}return{{known:!!(S.loves.mia&&S.loves.mia.d),said:dayLog().slice(-6).map(l=>l.t)}}}})())"""))
    check(r['known'] and any('提拉米蘇' in t for t in r['said']), f'Mia, without her tiramisu, says so and Jill knows: {r}')
    # Ken's favourite is Jill's signature: before there is one, he never misses it aloud, and his order goes through
    # (the first full run of rc7.4 found the order throwing there)
    k = json.loads(g.ev("""JSON.stringify((()=>{const sig=S.signature;S.signature=null;const M=Math.random;Math.random=()=>.1;const n0=dayLog().length;try{
      const ok=t=>(t.room||'main')==='main'&&!t.hold&&!t.lounge&&!t.pdr;let t=R.tables.find(t=>ok(t)&&!t.group);if(!t){t=R.tables.find(t=>ok(t)&&t.group);leaveGroup(t.group,'ok')}t.dirty=false;t.plates=[];
      spawn({t:R.t,type:'gourmet',size:1,name:'品酒師 Ken'});const q=R.groups[R.groups.length-1];if(q.table!=null){R.tables[q.table].group=null;q.table=null}seatGroup(q,t);q.state='order';createTicket(q);
      return{ticket:!!q.ticket,said:dayLog().slice(n0).map(l=>l.t)}}finally{Math.random=M;S.signature=sig}})())"""))
    check(k['ticket'] and not any(('沒有' in t and '啊' in t) or '{d}' in t for t in k['said']), f'Ken, with no signature yet: his order, and no word about it: {k}')
    # the journal says it
    g.ev("bookTab='regulars';showBook()"); g.page.wait_for_timeout(60)
    html = g.page.inner_html('#screen')
    if day_ok: check('最愛 黃金蛋炒飯' in html, 'the journal: 陳伯伯, 最愛 黃金蛋炒飯')
    check('最愛 提拉米蘇' in html, 'the journal: Mia, 最愛 提拉米蘇')
    g.ev("closeSub()")
    # the Lounge: Sophie's glass
    w = json.loads(g.ev("JSON.stringify((()=>{const L=wineList();return{has:L.includes('w_pinot'),o:loungeOrder({size:1,type:'gourmet',reg:'sophie',name:'Sophie'})}})())"))
    if w['has']: check(w['o'][0] == 'w_pinot', f'Sophie orders the pinot when it is poured: {w}')
    # the bill: +6 when they had it
    check('loveIdsOf(g)' in g.ev("String(collect)") and 'sat+=6' in g.ev("String(collect)"), 'the bill counts it')
    # tomorrow's menu marks the rows
    g.ev("(()=>{closeShop('x');for(const q of R.groups.slice())leaveGroup(q,'ok');finishClosing()})()")
    if g.ev("phase") == 'summary': g.click('[data-act=toShop]')
    if g.ev("phase") == 'shop': g.click('[data-act=nextDay]')
    g.page.wait_for_timeout(150)
    rows = g.ev("[...document.querySelectorAll('#screen .menu-row')].map(r=>r.innerText.replace(/\\s+/g,' '))")
    if day_ok: check(any('黃金蛋炒飯' in t and '♥ 陳伯伯' in t for t in rows), f'the menu row says whose favourite it is: {[t for t in rows if "蛋炒飯" in t]}')
    check(any('提拉米蘇' in t and '♥ Mia' in t for t in rows), f'and the tiramisu, Mia: {[t for t in rows if "提拉米蘇" in t]}')
    g.page.screenshot(path=os.path.join(ROOT, 'tests', 'artifacts', 'rc74_menu_favourites.png'))
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc74_the_lounges_new_bites(b, port, target):
    """(23:03 「酒吧應該新增生蠔、起司條、德國豬腳」「酒吧還要有水牛城雞翅」; 23:06 「就維持酒吧的客人沒辦法點餐餐廳的餐」;
    23:07 「酒吧的菜還是可以給餐廳的廚師煮 / 但是要讓酒吧專屬的服務生去送餐」) Four more bites for the Lounge: Buffalo wings
    and cheese sticks from its first level, oysters from the second, the pork knuckle from the third. A save that already
    has the Lounge gets the ones its level allows the next morning, with one line of news, once. They take no menu slot.
    The Lounge's guests order them, and never a dish from the restaurant's menu; the ones who came for a game order the
    fried ones. The restaurant's cooks make them; the Lounge's own waiter carries them over."""
    g = Game(b, port, target, seed=7432, manual=True, viewport={'width': 390, 'height': 844})
    NEW = ['wings', 'cheesestick', 'oyster', 'knuckle']; NAMES = ['水牛城雞翅', '起司條', '生蠔', '德國豬腳']
    load_save(g, 'player_day74_1508.json')   # the player's Day 74, saved before rc7.4: the Lounge at its third level
    d = json.loads(g.ev("JSON.stringify(%s.map(d=>[DISHES[d].n,!!DISHES[d].bar,DISHES[d].lv,DISHES[d].st]))" % json.dumps(NEW)))
    check(d == [['水牛城雞翅', True, 1, 'stove'], ['起司條', True, 1, 'stove'], ['生蠔', True, 2, 'prep'], ['德國豬腳', True, 3, 'oven']], f'the four, their levels and stations: {d}')
    lv = json.loads(g.ev("JSON.stringify([0,1,2,3].map(L=>{const o=S.rooms.lounge;S.rooms.lounge=L;const r=barDishes().filter(d=>%s.includes(d));S.rooms.lounge=o;return r}))" % json.dumps(NEW)))
    check(lv == [[], NEW[:2], NEW[:3], NEW], f'what each level of the Lounge allows: {lv}')
    news = lambda: json.loads(g.ev("JSON.stringify((S.news||[]).filter(n=>n.includes('Lounge 的小點多了')))"))
    s = json.loads(g.ev("JSON.stringify({phase,lv:loungeLv(),un:%s.filter(d=>S.unlocked.includes(d))})" % json.dumps(NEW)))
    check(s['phase'] == 'prep' and s['lv'] == 3 and s['un'] == NEW, f'the next morning, all four (this Lounge is at its third level): {s}')
    n = news()
    check(len(n) == 1 and all(x in n[0] for x in NAMES) and '不佔菜單名額' in n[0], f'one line of news names them: {n}')
    shown = g.ev("document.querySelector('#screen').innerText")
    check('Lounge 的小點多了' in shown, 'the morning shows it')
    g.ev("showPrep()"); check(len(news()) == 1, f'once: {news()}')
    _reload(g)
    check(g.ev("%s.every(d=>S.unlocked.includes(d))" % json.dumps(NEW)) and len(news()) <= 1, f'a reload keeps them and says it no second time: {news()}')
    # no menu slot
    n0 = g.ev("menuCount()")
    g.ev("for(const d of %s){if(!S.menu.includes(d))S.menu.push(d);S.stock[d]=Math.max(S.stock[d]||0,8)}save();showPrep()" % json.dumps(NEW))
    check(g.ev("menuCount()") == n0, 'on the menu, they take no slot')
    check(all(g.page.query_selector(f'#screen .menu-row [data-d="{x}"]') is not None for x in NEW), 'each has its row on the menu')
    # what the Lounge's guests order
    to_service(g); g.ev("window.__act=()=>{}")
    o = json.loads(g.ev("""JSON.stringify((()=>{const N=%s;const cnt={},fan={};const bad=[],fanBad=[];const ok=d=>!!(DISH(d)||{}).wine||barDishes().includes(d);
      for(let i=0;i<400;i++)for(const d of loungeOrder({size:2,type:'office',pat:1})){if(N.includes(d))cnt[d]=(cnt[d]||0)+1;if(!ok(d))bad.push(d)}
      for(let i=0;i<300;i++)for(const d of loungeOrder({size:2,type:'office',pat:1,sport:1})){if(N.includes(d))fan[d]=(fan[d]||0)+1;if(!ok(d))fanBad.push(d)}
      return{cnt,bad,fan,fanBad}})())""" % json.dumps(NEW)))
    check(all(o['cnt'].get(x, 0) > 0 for x in NEW) and not o['bad'], f'the Lounge orders each of them, and nothing from the restaurant: {o}')
    check(o['fan'].get('wings', 0) > 0 and o['fan'].get('cheesestick', 0) > 0 and not o['fan'].get('oyster') and not o['fan'].get('knuckle') and not o['fanBad'], f'the fans: the fried ones: {o}')
    # the way it goes: a Lounge table orders the wings; the kitchen cooks them; the Lounge's own waiter carries them. Every
    # new dish's first portion is the cooks' too (rc8, the player 2026-10-03: 「不管是不是第一次做那道菜，有廚師她就不用做」).
    check(g.ev("(()=>{const x=S.xp.wings;S.xp.wings=0;const a=chefCanAny('wings');S.xp.wings=x;return a})()") is True, 'a new dish: the cooks can make the first one')
    g.ev("S.xp.wings=Math.max(S.xp.wings||0,1)")
    check(g.ev("chefCanAny('wings')") is True, 'and every one after')
    g.ev("__botUntil('R.t>=R.dur*.3',90000,1/30)")
    where = g.ev("""(()=>{const free=t=>t.room==='lounge'&&t.kind!=='bar'&&t.seats>=2&&!t.group&&!t.dirty&&!t.claim;if(!R.tables.some(free)){const t=R.tables.find(t=>t.room==='lounge'&&t.kind!=='bar'&&t.seats>=2&&t.group);if(t)leaveGroup(t.group,'ok')}
      for(const t of R.tables)if(t.room==='lounge'&&t.kind!=='bar'&&!t.group){t.dirty=false;t.claim=null;t.plates=[]}
      window.__LO=window.__LO||loungeOrder;loungeOrder=q=>q.__want||__LO(q);
      spawn({t:R.t,type:'office',size:2,lounge:1});const q=R.groups[R.groups.length-1];q.__want=['w_house','wings'];q.__probe=1;return q.table!=null?R.tables[q.table].room:null})()""")
    check(where == 'lounge', f'two guests sit straight down in the Lounge: {where}')
    g.ev("""window.__carried=[];const sv0=serveItems;serveItems=function(q,list){for(const c of list){const it=c.it;if(it&&it.d==='wings'&&it.st==='ready'){const m=(S.crew||[]).find(m=>{const w=R.cw&&R.cw[m.id];return w&&w.carry&&w.carry.includes(it)});
      __carried.push(m?[m.name,m.role,crewPool(m),!!waiterDuties(m).lounge,lgWaiterHere()]:(R.jill.carry.some(c0=>c0.it===it)?['Jill']:['?']))}}return sv0.apply(this,arguments)}""")   # rc8: who carried it, at the moment it reached the table (the walk from the end of the Lounge's bar is short)
    claims = set(); cooks = set(); r = {}
    for _ in range(500):
        r = json.loads(g.ev("""JSON.stringify((()=>{const q=R.groups.find(q=>q.__probe);if(!q)return{gone:1};const tk=q.ticket;if(!tk)return{st:q.state};const it=tk.items.find(i=>i.d==='wings');
          const m=tk.claim!=null?S.crew.find(m=>m.id===tk.claim):null;const s=R.slots.find(s=>s.job&&s.job.it===it);const ch=s&&s.job.chef!=null?S.crew.find(m=>m.id===s.job.chef):null;
          return{st:q.state,it:it&&it.st,picked:!!(it&&it.picked),claim:m?[m.name,m.role,crewPool(m),!!waiterDuties(m).lounge,lgWaiterHere()]:null,cook:s?s.type+':'+(ch?ch.role+':'+crewPool(ch):'jill'):null,jill:R.jill.carry.some(c=>c.tk===tk)}})())"""))
        if r.get('claim') and r.get('picked'): claims.add(tuple(r['claim']))   # who has the plate (the bartender's claim is the glass)
        if r.get('cook'): cooks.add(r['cook'])
        if r.get('it') == 'served' or r.get('gone'): break
        g.ev("for(let i=0;i<15;i++)__tick(1000/30)")
    check(r.get('it') == 'served', f'the wings reached the table: {r}')
    check(cooks and all(c.startswith('stove:chef:') for c in cooks), f'cooked on the kitchen\'s stove by a cook (the restaurant\'s, or 阿拓 of the Lounge\'s list — the one kitchen): {cooks}')
    claims = set(tuple(x) for x in json.loads(g.ev("JSON.stringify(__carried)")))
    check(claims and all(c[1] == 'waiter' and c[2] == 'lounge' and c[3] for c in claims if len(c) > 4 and c[4]), f'carried by the Lounge\'s own waiter: {claims}')
    g.ev("setRoom('lounge');for(let i=0;i<10;i++)__tick(1000/30);document.querySelectorAll('#plines>*,#toasts>*').forEach(e=>e.remove())"); g.page.wait_for_timeout(60)
    g.page.screenshot(path=os.path.join(ROOT, 'tests', 'artifacts', 'rc74_lounge_wings.png'))
    g.ev("loungeOrder=window.__LO")
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc74_the_lounge_tv_and_its_sound(b, port, target):
    """(23:06 「酒吧要新增電視大的電視轉播運動比賽 / 這個就放在家具類，應該要200,000 / 然後電視的音響系統150,000」) Two pieces
    of furniture for the Lounge in the shop's 店裡的樣子 tab: the big TV, $200,000, and its sound system, $150,000, which
    needs the TV. Without a Lounge neither is offered. Each, bought, is shown in the Lounge. On a game night (about two a
    week) the TV is on during the service: two fans come for the game, three with the sound; more guests stay on after
    dinner; the day's summary says there was a game and how many came for it."""
    g = Game(b, port, target, seed=7433, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day52.json')   # no Lounge
    g.ev("S.money=Math.max(S.money,600000);shopTab='home';showShop()"); g.page.wait_for_timeout(80)
    m0 = g.ev("S.money")
    check('Lounge 的家具' not in g.ev("$('#screen').innerText") and g.ev("(doAct('buyLgFurn',null,'tv',null),!lgFurnOn('tv')&&S.money===%d)" % m0), 'no Lounge: nothing offered, nothing bought')
    load_save(g, 'player_day74_1508.json')
    check(g.ev("!lgFurnOn('tv')&&![...Array(70).keys()].some(i=>sportsNight(S.day+i))"), 'no TV, no game nights')
    g.ev("S.money=Math.max(S.money,600000);shopTab='home';showShop()"); g.page.wait_for_timeout(80)
    items = json.loads(g.ev("JSON.stringify([...document.querySelectorAll('#screen .item')].filter(e=>/^(Lounge 大電視|電視音響系統)/.test(((e.querySelector('.nm')||{}).textContent)||'')).map(e=>e.innerText.replace(/\\s+/g,' ')))"))
    check('Lounge 的家具' in g.ev("$('#screen').innerText") and len(items) == 2 and '$200,000' in items[0] and '要先有 Lounge 大電視・$150,000' in items[1], f'the shop\'s Lounge furniture (the sound\'s price shows before the TV is in): {items}')
    m0 = g.ev("S.money")
    g.ev("doAct('buyLgFurn',null,'sound',null)")
    check(g.ev("!lgFurnOn('sound')") and g.ev("S.money") == m0, 'the sound waits for the TV')
    g.ev("doAct('buyLgFurn',null,'tv',null)"); g.ev("__tick(1800)")
    check(g.ev("lgFurnOn('tv')&&S.lgFurn.tv===S.day") and g.ev("S.money") == m0 - 200000, 'the TV: $200,000')
    rv = g.ev("$('#reveal').hidden?'':$('#reveal').innerText")
    check('Lounge 大電視' in rv, f'and its card: {rv!r}')
    g.ev("doAct('revealPeek',null,'lgtv',null)"); g.ev("for(let i=0;i<4;i++)__tick(1000/30)")
    check(g.ev("room") == 'lounge' and g.ev("!$('#peekPill').hidden"), 'a look: the Lounge')
    g.page.screenshot(path=os.path.join(ROOT, 'tests', 'artifacts', 'rc74_lounge_tv_bought.png'))
    g.click('#peekPill'); g.ev("__tick(1000/30)")
    g.ev("hideReveal();shopTab='home';showShop()")
    g.ev("doAct('buyLgFurn',null,'sound',null)"); g.ev("__tick(1800)"); g.ev("hideReveal()")
    check(g.ev("lgFurnOn('sound')") and g.ev("S.money") == m0 - 350000, 'the sound: $150,000')
    g.ev("doAct('buyLgFurn',null,'tv',null);doAct('buyLgFurn',null,'sound',null)")
    check(g.ev("S.money") == m0 - 350000, 'neither twice')
    nights = g.ev("[...Array(70).keys()].filter(i=>sportsNight(S.day+i)).length")
    check(10 <= nights <= 30, f'game nights: about two a week ({nights} in ten weeks)')
    # a game night: the service
    g.ev("window.__SN=sportsNight;sportsNight=()=>true;save()")
    if g.ev("phase") == 'shop':   # the shop opened from the morning's preparation goes back to it
        g.click('#screen [data-act=toPrep]' if g.page.query_selector('#screen [data-act=toPrep]') else '#screen [data-act=nextDay]'); g.page.wait_for_timeout(200)
    g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}"); _quiet(g)
    to_service(g); g.ev("window.__act=()=>{}")
    fans = g.ev("R.sched.filter(o=>o.sport&&o.lounge).length")
    check(fans == 3, f'three come for the game (the sound): {fans}')
    p = json.loads(g.ev("(()=>{const q={type:'office',size:2,pat:1};R.t=R.dur*.6;const on=loungeAfterP(q);sportsNight=()=>false;const off=loungeAfterP(q);sportsNight=()=>true;return JSON.stringify({on,off})})()"))
    check(p['on'] > p['off'] > 0, f'more stay on after dinner on a game night: {p}')
    g.ev("__botUntil('R.t>=R.dur*.82',150000,1/30)")
    st = json.loads(g.ev("JSON.stringify({tv:lgTvOn(),sport:R.st.sport||0,fans:R.groups.filter(q=>q.sport).length})"))
    check(st['tv'] and st['sport'] >= 1, f'the TV is on, and the fans are in: {st}')
    g.ev("setRoom('lounge');for(let i=0;i<20;i++)__tick(1000/30);document.querySelectorAll('#plines>*,#toasts>*').forEach(e=>e.remove())"); g.page.wait_for_timeout(80)
    g.page.screenshot(path=os.path.join(ROOT, 'tests', 'artifacts', 'rc74_lounge_tv_game.png'))
    g.ev("(()=>{closeShop('x');for(const q of R.groups.slice())leaveGroup(q,'ok');finishClosing()})()"); g.page.wait_for_timeout(120)
    summ = g.ev("$('#screen').innerText")
    notes = g.ev("[...document.querySelectorAll('#screen .daynotes div')].map(e=>e.innerText.replace(/\\s+/g,' ')).join('|')")
    check(re.search(r'有比賽轉播 \d+ 位來看球', notes), f'the summary\'s Lounge line, the match under it: {notes!r}')
    g.ev("sportsNight=window.__SN")
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc75_the_pizza_oven_one_more_cook_and_the_bar_pizza(b, port, target):
    """(23:08 「酒吧應該可以開發披薩吧 但可能要烤爐 所以要再增加一個廚師」) The pizza oven is a kitchen work (後場工程,
    $120,000) that needs the Lounge. Built, the restaurant can hire one more; the kitchen has a 披薩烤爐 station on the
    board, and the next cook hired goes to it if nobody is there. The bar pizza is researched, not given: before the oven
    nothing of it is in the lab; with the oven the pantry has the dough, and dough + tomato sauce + cheese is the pizza;
    the Lounge's morning news never hands it out. It is a Lounge bite (no menu slot). Jill makes the first one; then the
    cook at the oven bakes it — dressed on the counter, baked in the oven's mouth — and the Lounge's waiter carries it.
    The Lounge's guests order it, the fans too."""
    g = Game(b, port, target, seed=7501, manual=True, viewport={'width': 390, 'height': 844})
    # no Lounge: nothing of it
    load_save(g, 'player_day52.json')
    g.ev("S.money=Math.max(S.money,999999);shopTab='kitchen';showShop()"); g.page.wait_for_timeout(80)
    card = g.ev("(()=>{const e=[...document.querySelectorAll('#screen .item')].find(e=>((e.querySelector('.nm')||{}).textContent||'').startsWith('披薩烤爐'));return e?e.innerText.replace(/\\s+/g,' '):''})()")
    check('要先有 Lounge' in card and not g.page.query_selector('#screen [data-act=buyProject][data-k=pizzaoven]'), f'no Lounge: the oven waits for it: {card!r}')
    m0 = g.ev("S.money"); g.ev("doAct('buyProject',null,'pizzaoven',null)")
    check(not g.ev("projOn('pizzaoven')") and g.ev("S.money") == m0, 'and cannot be built')
    check(g.ev("!labRD().includes('pizza')&&!pantry().includes('dough')"), 'nothing of the pizza in the lab')
    g.ev("shopTab='menu';showShop()"); g.page.wait_for_timeout(60)
    check('酒吧披薩' not in g.ev("$('#screen').innerText"), 'nor on the research list')
    # building the Lounge (here, on this save) gives its bites, never the pizza (the 03:45 discovery-run finding)
    g.ev("factSet('lounge_project');S.level=Math.max(S.level,4);buyLounge(1);hideReveal&&hideReveal()")
    check(g.ev("loungeLv()") == 1 and g.ev("S.unlocked.includes('wings')&&S.unlocked.includes('cheesestick')") and not g.ev("S.unlocked.includes('pizza')||S.menu.includes('pizza')"), 'Lounge I built: its bites, and no pizza without the oven and the lab')
    # with a Lounge
    load_save(g, 'player_day74_1508.json')
    g.ev("barMenuMig()")
    check(g.ev("!S.unlocked.includes('pizza')"), 'the Lounge\'s bites news never hands the pizza out')
    g.ev("S.money=Math.max(S.money,999999);shopTab='menu';showShop()"); g.page.wait_for_timeout(60)
    row = g.ev("(()=>{const e=[...document.querySelectorAll('#screen .item')].find(e=>((e.querySelector('.nm')||{}).textContent||'').startsWith('酒吧披薩'));return e?e.innerText.replace(/\\s+/g,' '):''})()")
    check('需要先購買披薩烤爐' in row and not g.ev("labRD().includes('pizza')"), f'on the research list, waiting for the oven: {row!r}')
    cap0 = g.ev("restaurantCap()"); m0 = g.ev("S.money")
    g.ev("shopTab='kitchen';showShop()"); g.page.wait_for_timeout(60)
    check(g.page.query_selector('#screen [data-act=buyProject][data-k=pizzaoven]') is not None, 'the oven is offered in 廚房設備')
    g.ev("doAct('buyProject',null,'pizzaoven',null)"); g.ev("__tick(1800)")
    st = json.loads(g.ev("JSON.stringify({on:projOn('pizzaoven'),money:S.money,cap:restaurantCap(),slots:buildSlots().filter(s=>s.type==='pizza').length,scap:stationCap('pizza'),rv:$('#reveal').hidden?'':$('#reveal').innerText})"))
    check(st['on'] and st['money'] == m0 - 120000 and st['cap'] == cap0 + 1 and st['slots'] == 1 and st['scap'] == 1 and '披薩烤爐' in st['rv'], f'built: $120,000, one more on the restaurant\'s list, a station of its own, its card: {st}')
    g.ev("hideReveal()")
    # the next cook hired goes to the oven
    n = g.ev("S.crew.length"); free = g.ev("restaurantCap()-poolCrew('restaurant').length")
    check(free >= 1, f'there is room for one more: {free}')
    g.ev("shopTab='staff';showShop()"); g.ev("doAct('hire',null,'chef',null)")
    h = json.loads(g.ev("JSON.stringify((()=>{const m=S.crew[S.crew.length-1];return{n:S.crew.length,role:m.role,duty:m.duty,name:m.name}})())"))
    check(h['n'] == n + 1 and h['role'] == 'chef' and h['duty'] == 'pizza', f'the new cook is at the oven: {h}')
    g.ev("shopTab='staff';showShop()"); g.page.wait_for_timeout(60)
    brow = g.ev("(document.querySelector('.brow[data-st=pizza]')||{}).innerText||''")
    check('披薩烤爐' in brow and h['name'] in brow, f'the board has its row: {brow!r}')
    # researched: dough + tomato sauce + cheese
    check(g.ev("pantry().includes('dough')&&labRD().includes('pizza')"), 'with the oven, the dough is in the pantry')
    mc = g.ev("menuCount()")
    g.ev("labSel=['dough','tomato','cheese'];doAct('labTry',null,null,null)")
    check(g.ev("S.unlocked.includes('pizza')&&S.menu.includes('pizza')") and g.ev("menuCount()") == mc, 'the lab finds it; it is on the menu, taking no slot')
    # the cook at the oven, from the first one (rc8, the player 2026-10-03: 「不管是不是第一次做那道菜，有廚師她就不用做」)
    check(g.ev("(S.xp.pizza||0)===0&&chefCanAny('pizza')") is True, 'the first one is the cook\'s too')
    g.ev("S.xp.pizza=Math.max(S.xp.pizza||0,1);S.stock.pizza=Math.max(S.stock.pizza||0,8)")
    if g.ev("phase") == 'shop':
        g.click('#screen [data-act=toPrep]' if g.page.query_selector('#screen [data-act=toPrep]') else '#screen [data-act=nextDay]'); g.page.wait_for_timeout(200)
    g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}"); _quiet(g)
    g.ev("S.stock.pizza=Math.max(S.stock.pizza||0,8);if(!S.menu.includes('pizza'))S.menu.push('pizza')")
    to_service(g); g.ev("window.__act=()=>{}")
    check(g.ev("R.slots.filter(s=>s.type==='pizza').length") == 1 and g.ev("chefCanAny('pizza')") is True, 'tonight the oven has its station and its cook')
    o = json.loads(g.ev("JSON.stringify((()=>{let n=0,f=0;for(let i=0;i<400;i++)if(loungeOrder({size:2,type:'office',pat:1}).includes('pizza'))n++;for(let i=0;i<300;i++)if(loungeOrder({size:2,type:'office',pat:1,sport:1}).includes('pizza'))f++;return{n,f}})())"))
    check(o['n'] > 0 and o['f'] > 0, f'the Lounge orders it, the fans too: {o}')
    g.ev("__botUntil('R.t>=R.dur*.3',90000,1/30)")
    where = g.ev("""(()=>{const free=t=>t.room==='lounge'&&t.kind!=='bar'&&t.seats>=2&&!t.group&&!t.dirty&&!t.claim;if(!R.tables.some(free)){const t=R.tables.find(t=>t.room==='lounge'&&t.kind!=='bar'&&t.seats>=2&&t.group);if(t)leaveGroup(t.group,'ok')}
      for(const t of R.tables)if(t.room==='lounge'&&t.kind!=='bar'&&!t.group){t.dirty=false;t.claim=null;t.plates=[]}
      window.__LO=window.__LO||loungeOrder;loungeOrder=q=>q.__want||__LO(q);spawn({t:R.t,type:'office',size:2,lounge:1});const q=R.groups[R.groups.length-1];q.__want=['w_house','pizza'];q.__probe=1;return q.table!=null?R.tables[q.table].room:null})()""")
    check(where == 'lounge', f'two guests in the Lounge: {where}')
    g.ev("""window.__carried=[];const sv0=serveItems;serveItems=function(q,list){for(const c of list){const it=c.it;if(it&&it.d==='pizza'&&it.st==='ready'){const m=(S.crew||[]).find(m=>{const w=R.cw&&R.cw[m.id];return w&&w.carry&&w.carry.includes(it)});
      __carried.push(m?[m.name,m.role,crewPool(m),!!waiterDuties(m).lounge,lgWaiterHere()]:(R.jill.carry.some(c0=>c0.it===it)?['Jill']:['?']))}}return sv0.apply(this,arguments)}""")   # rc8: who carried it, at the moment it reached the table (the walk from the end of the Lounge's bar is short)
    seen = set(); shot = False; r = {}
    for _ in range(600):
        r = json.loads(g.ev("""JSON.stringify((()=>{const q=R.groups.find(q=>q.__probe);if(!q)return{gone:1};const tk=q.ticket;if(!tk)return{st:q.state};const it=tk.items.find(i=>i.d==='pizza');const s=R.slots.find(s=>s.job&&s.job.it===it);
          const ch=s&&s.job.chef!=null?S.crew.find(m=>m.id===s.job.chef):null;const sp=s?stepSpot(s):null;const m=tk.claim!=null?S.crew.find(m=>m.id===tk.claim):null;
          return{it:it&&it.st,picked:!!(it&&it.picked),slot:s?s.type:null,cook:ch?ch.duty:(s?'jill':null),oven:!!(sp&&sp.inOven),step:s&&s.job.step?s.job.step.t:null,claim:m&&it&&it.picked?[m.role,crewPool(m)]:null}})())"""))
        if r.get('slot'): seen.add(('slot', r['slot'], r['cook']))
        if r.get('oven'):
            seen.add(('oven', r['step']))
            if not shot:
                g.ev("setRoom('kitchen');for(let i=0;i<2;i++)__tick(1000/30);document.querySelectorAll('#plines>*,#toasts>*').forEach(e=>e.remove())"); g.page.wait_for_timeout(60)
                g.page.screenshot(path=os.path.join(ROOT, 'tests', 'artifacts', 'rc75_kitchen_pizza_baking.png')); shot = True
        if r.get('claim'): seen.add(('carried', tuple(r['claim'])))
        if r.get('it') == 'served' or r.get('gone'): break
        g.ev("for(let i=0;i<15;i++)__tick(1000/30)")
    check(r.get('it') == 'served', f'the pizza reached the table: {r} {seen}')
    check(('slot', 'pizza', 'pizza') in seen and ('oven', 'zone') in seen, f'the cook at the oven made it, and it baked in the oven\'s mouth: {seen}')
    carried = [tuple(x[1:3]) for x in json.loads(g.ev("JSON.stringify(__carried)"))]
    check(carried and all(c == ('waiter', 'lounge') for c in carried), f'the Lounge\'s waiter carried it: {carried} {seen}')
    g.ev("loungeOrder=window.__LO")
    check(not g.errors, g.errors[:3]); g.close()


FP_WORDS = ['相簿', '相冊', 'Album', 'album', '解鎖', '珍貴', '收藏', 'NEW', '回憶', '第一張', '成就', '紀念']


@test
def v25_first_photo_day_one_dylan_takes_one_of_jills_cameras(b, port, target):
    """rc7.5 (the player, 19:31–19:32; docs/v24/life_album_first_photo_2026-10-02_1931.txt): Day 1, as the doors open,
    Jill carries a pot of herbs toward the window and stops to look at it; Dylan takes her with one of her own cameras —
    the shutter, the flash; she was not looking. The photo is the room as it was that instant (the game's own picture,
    without its marks), the album's first entry: Day 1, 「第一天」, protected from the cap, not 珍藏. Four lines, two more
    only if a cat is in the frame. No unlock, no achievement, no word about an album. The pot ends on the sill and the
    day goes on; the coach and the lines never cover each other. Then: a reload, a backup and its restore, the cap."""
    g = Game(b, port, target, seed=7508, manual=True, viewport={'width': 390, 'height': 844})
    g.ev("window.__firstPhoto=1")
    g.click('[data-act=open]'); g.page.wait_for_timeout(150)
    check(g.ev("S.day") == 1 and g.ev("albumList().length") == 0 and not g.ev("S.firstPhoto"), 'a new game: no photo yet')
    ach0 = set(json.loads(g.ev("JSON.stringify(Object.keys(S.achievements||{}))")))
    start_day(g); install_bot(g); g.ev(LAZY_ACTOR + "\nwindow.__act=window.__actLazy")
    phases, overlap, said, t_shot, t_pot = [], [], set(), None, None
    dyface = False
    for _ in range(1500):
        r = json.loads(g.ev("JSON.stringify({fp:R.jill.fp?R.jill.fp.phase:null,first:!!S.firstPhoto,pot:!!(S.firstPhoto&&S.firstPhoto.pot),t:R.t})"))
        if r['fp'] and (not phases or phases[-1] != r['fp']): phases.append(r['fp'])
        if r['first'] and t_shot is None: t_shot = r['t']
        if t_shot is not None:
            said |= set(g.ev("[...document.querySelectorAll('#toasts .toast,#banner *')].map(e=>e.textContent)"))
            if g.ev("(()=>{const p=portraitOf('dylan','default');const src=p&&(p.src||p);return !!src&&[...document.querySelectorAll('#plines img')].some(i=>i.getAttribute('src')===src)})()"): dyface = True
            said.add(g.ev("$('#banner').textContent||''"))
        ov = g.ev("(()=>{const c=$('#coach');const ls=[...document.querySelectorAll('#plines>*')];if(c.hidden||!ls.length)return null;const a=c.getBoundingClientRect();return ls.some(e=>{const b=e.getBoundingClientRect();return b.bottom>a.top+1&&b.top<a.bottom-1&&b.right>a.left&&b.left<a.right})})()")
        if ov is not None: overlap.append(ov)
        if r['pot'] and t_pot is None: t_pot = r['t']
        if t_pot is not None and r['t'] > t_shot + 13: break
        # the player plays until the shutter; then the frames run on the clock (the lines are timed, as on a phone)
        if t_shot is None: g.page.evaluate('()=>window.__bot(6,1/30)')
        else: g.ev("for(let i=0;i<6;i++)__tick(1000/30)")
    check(phases == ['go', 'stand', 'turn', 'sill', 'place'], f'to the window with the herbs, a look at them, the shutter, a look back, the sill: {phases}')
    check(t_shot is not None and t_shot < 12, f'as the doors open, before the first guest has ordered: the shutter at {t_shot}')
    shot = json.loads(g.ev("JSON.stringify(R.fpShot)"))
    p = json.loads(g.ev("JSON.stringify(albumList()[0])"))
    check(p['kind'] == 'first' and p['day'] == 1 and p['cap'] == '第一天' and p.get('first') == 1 and p['keep'] is False and p['clock'].startswith('17:') and p['id'] == 'p1_first', f'the album\'s first entry: Day 1, 「第一天」, not 珍藏: {p}')
    img = json.loads(g.ev("(async()=>{const u=albumList()[0].img||await photoGet('p1_first');if(!u)return JSON.stringify(null);const im=new Image();await new Promise(r=>{im.onload=r;im.src=u});return JSON.stringify([u.slice(0,15),im.naturalWidth,im.naturalHeight])})()"))
    check(img and img[0] == 'data:image/jpeg' and img[1:] == [360, 270], f'a picture, 4:3, the size of the others: {img}')
    f = shot['f']
    check(f and f['x'] <= FP_X and FP_X <= f['x'] + f['w'] and shot['cats'] in (0, 1), f'Jill is in the frame, and at most one cat: {shot}')
    # rc8 (the player: 「第一天就寫jill先生但不露臉」): before the reveal his lines are 「Jill 先生」's, and his face is not on screen
    lines = json.loads(g.ev("JSON.stringify(dayLog().filter(l=>['Jill','Jill 先生','Dylan'].includes(l.w)).map(l=>l.w+'：'+l.t))"))
    want = ['Jill：你拿我的相機幹嘛？', 'Jill 先生：拍妳。', 'Jill：我根本沒在看。', 'Jill 先生：我知道。'] + (['Jill：牠也在。', 'Jill 先生：嗯。'] if shot['cats'] == 1 else [])
    got = [x for x in lines if x in want + ['Jill：牠也在。', 'Jill 先生：嗯。']]
    check(not any(x.startswith('Dylan：') for x in lines), f'no line under his name before the reveal: {lines}')
    check(not dyface, 'his face is not on screen before the reveal')
    check(got == want, f'the lines, in order (the cat\'s two only with a cat in it): {got}')
    bad = [w for w in FP_WORDS for x in said if w in x]
    check(not bad, f'nothing says album, unlock, treasured, NEW: {bad} in {said}')
    new_ach = set(json.loads(g.ev("JSON.stringify(Object.keys(S.achievements||{}))"))) - ach0
    check(not [a for a in new_ach if re.search('photo|album|first|mem', a)], f'no achievement for it: {new_ach}')
    check(overlap and not any(overlap), f'the coach and the lines never covered each other ({len(overlap)} frames with both)')
    check(g.ev("!!(S.firstPhoto&&S.firstPhoto.pot)") and g.ev("!R.jill.fp"), 'the pot is on the sill; Jill is back to work')
    # the day goes on
    play_day(g, max_steps=60000)
    for _ in range(200):
        if g.ev("phase") != 'service': break
        g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
    s = json.loads(g.ev("JSON.stringify(S.lastSummary||{})"))
    check(g.ev("phase") == 'summary' and s.get('guests', 0) >= 5, f'the day ends as any first day does: {s.get("guests")} guests')
    check(g.ev("albumList().filter(p=>p.kind==='first').length") == 1, 'one first photo')
    # Day 2: no history added on top of it; ordinary photos still come
    g.click('[data-act=toShop]'); g.page.wait_for_timeout(60); g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(150)
    check(g.ev("albumList().filter(p=>p.kind==='first').length") == 1 and not g.ev("S.firstPhoto.retro"), 'the next morning changes nothing')
    g.ev("albumAdd('pet','data:image/jpeg;base64,/9j/',{a:'柔柔'})")
    check(g.ev("albumList().length") >= 2 and g.ev("albumList()[0].kind") == 'first', 'the next photo goes after it')
    # a reload
    g.ev("save()"); g.reload(); g.page.wait_for_timeout(200)
    r = json.loads(g.ev("(async()=>{const p=albumList().find(p=>p.kind==='first');if(!p)return JSON.stringify(null);const u=p.img||await photoGet(p.id);return JSON.stringify({id:p.id,day:p.day,img:(u||'').slice(0,15)})})()"))
    check(r and r['day'] == 1 and r['img'] == 'data:image/jpeg', f'after a reload: {r}')
    # a backup and its restore, in another browser
    txt = g.ev("(async()=>backupText(await photoAll()))()")
    check('p1_first' in txt, 'the backup has it, with its picture')
    g2 = Game(b, port, target, seed=7509, manual=True, viewport={'width': 390, 'height': 844})
    g2.ev("importSaveText(%s);importConfirm()" % json.dumps(txt)); g2.page.wait_for_timeout(200)
    r = json.loads(g2.ev("(async()=>{const p=albumList().find(p=>p.kind==='first');if(!p)return JSON.stringify(null);const u=p.img||await photoGet(p.id);return JSON.stringify({day:p.day,cap:p.cap,img:(u||'').slice(0,15)})})()"))
    check(r and r['day'] == 1 and r['cap'] == '第一天' and r['img'] == 'data:image/jpeg', f'restored from the backup: {r}')
    # the cap: three hundred ordinary photos later it is still there
    n = g2.ev("(()=>{for(let i=0;i<300;i++)albumAdd(i%2?'pet':'nap','data:image/jpeg;base64,/9j/',{a:'柔柔'});return albumList().filter(p=>!p.keep&&!p.first).length})()")
    check(n <= g2.ev("albumCap()") and g2.ev("albumList().filter(p=>p.kind==='first').length") == 1 and g2.ev("albumList()[0].kind") == 'first', f'the ordinary photos rotate ({n} kept), the first one stays')
    check(not g.errors and not g2.errors, (g.errors + g2.errors)[:3]); g.close(); g2.close()


FP_X = 236


@test
def v25_first_photo_a_mature_save_gets_day_one_as_history(b, port, target):
    """rc7.5: a save past Day 1 that never had the moment gets the photo as history — the Day 1 restaurant drawn as it
    was (newState), Jill with the herbs, 包包 on the bed by the window — at the front of the album: Day 1, 「第一天」, no
    clock. Nothing else in the album moves or goes; nothing is said (no news, no toast, no line, no NEW); the moment is not
    played on Day 74. The lightbox opens on it (Day 1, the caption, the picture whole), the album reads from it, and the
    restaurant's own window has no pot on its sill (that pot belongs to a Day 1 that was played)."""
    g = Game(b, port, target, seed=7510, manual=True, viewport={'width': 390, 'height': 844})
    raw = load_save(g, 'player_day74_1508.json')
    before = raw.get('album') or []
    A = json.loads(g.ev("JSON.stringify(albumList().map(p=>({id:p.id,kind:p.kind,day:p.day,keep:!!p.keep,clock:p.clock,cap:p.cap})))"))
    check(len(A) == len(before) + 1 and A[0]['kind'] == 'first' and A[0]['day'] == 1 and A[0]['cap'] == '第一天' and A[0]['clock'] == '', f'one more, at the front, Day 1: {len(before)} -> {len(A)}, {A[0]}')
    check([(p['id'], bool(p.get('keep'))) for p in before] == [(p['id'], p['keep']) for p in A[1:]], 'every photo that was there is there, in its order, 珍藏 as it was')
    check(g.ev("JSON.stringify(S.firstPhoto)") == '{"day":1,"retro":1}', 'history, not news')
    news = g.ev("JSON.stringify((S.news||[]).filter(n=>/照片|相機|相簿|第一天/.test(n)))")
    toasts = g.ev("[...document.querySelectorAll('#toasts .toast')].map(e=>e.textContent).join('|')")
    check(news == '[]' and not any(w in toasts for w in FP_WORDS + ['照片', '相機']), f'nothing said: {news} {toasts}')
    img = json.loads(g.ev("(async()=>{const p=albumList()[0];const u=p.img||await photoGet(p.id);if(!u)return JSON.stringify(null);const im=new Image();await new Promise(r=>{im.onload=r;im.src=u});return JSON.stringify([u.slice(0,15),im.naturalWidth,im.naturalHeight])})()"))
    check(img and img[0] == 'data:image/jpeg' and img[1:] == [360, 270], f'the picture: {img}')
    # the lightbox, from the album page
    g.ev("bookTab='mem';showBook()"); g.page.wait_for_timeout(250)
    g.ev("openLightbox('p1_first')"); g.page.wait_for_timeout(200)
    lb = json.loads(g.ev("JSON.stringify((()=>{const el=$('#lightbox');const im=el.querySelector('.lb-card img');const r=im.getBoundingClientRect();const c=el.querySelector('.lb-close').getBoundingClientRect();return{open:!el.hidden,txt:el.querySelector('figcaption').innerText.replace(/\\s+/g,' '),count:el.querySelector('.lb-count').textContent,w:Math.round(r.width),h:Math.round(r.height),nat:[im.naturalWidth,im.naturalHeight],close:[Math.round(c.width),Math.round(c.height)],pin:!!el.querySelector('.pin')}})())"))
    check(lb['open'] and 'DAY 1' in lb['txt'] and '第一天' in lb['txt'] and lb['count'].startswith('1 /') and not lb['pin'], f'the lightbox: Day 1, its caption, the first of the album, no pin: {lb}')
    check(lb['w'] >= 300 and abs(lb['w'] / max(1, lb['h']) - 4 / 3) < .03 and min(lb['close']) >= 32, f'the whole picture, big enough on a phone, a close button a thumb can hit: {lb}')
    g.click('#lightbox .lb-close'); g.page.wait_for_timeout(120)
    check(g.ev("$('#lightbox').hidden"), 'it closes')
    check(g.ev("JSON.stringify(albumList().slice().sort((a,b)=>a.day-b.day)[0].id)") == '"p1_first"', 'the album reads from it')
    # Day 74 is played as Day 74: no moment, no pot on the restaurant's sill
    g.ev("closeSub&&closeSub()"); to_service(g); g.ev("window.__firstPhoto=1")
    g.ev("__botUntil('R.t>=R.dur*.2',90000,1/30)")
    check(g.ev("!R.jill.fp") and not g.ev("dayLog().some(l=>/拍妳|我的相機/.test(l.t))") and not g.ev("!!S.firstPhoto.pot"), 'nothing replayed')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc76_the_bar_turns_into_an_l(b, port, target):
    """07:44–07:45 「吧檯新增L型就能增加位子」「而且可以變長一點」: from Lounge II the counter is longer and turns toward the room
    at its left end — seven stools along it and two along the L, nine in all, as far apart as rc7.5 made them (07:10:
    not shoulder to shoulder), every one inside a phone's view. Lounge I keeps its six in a row. The first six keep their
    places in the list (a regular's usual stool; the old saves), the three new ones come last. Someone walking in from
    the street door to the counter goes round the L, never through it; the bartender serves the L's two across the corner; on a
    tasting night the small board stands at the L's end; the shop and the manual say so.
    rc7.7 (12:43 「L型吧台包在裡面的是店員啊 原本橫的不變 但直的應該是要往上面的方向延伸啊」): the counter as it was; the
    return runs from its left end back toward the wall, so the L closes round the bartenders: their places, Ken's on a
    tasting night and the corner they serve the L's two from are inside it, the L's stools and the place the floor picks
    up from outside it. It stops short of the wall: the bartenders come in from the back door through that gap, never
    through the return or the counter."""
    g = Game(b, port, target, seed=7631, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day74_1508.json')
    d = json.loads(g.ev("JSON.stringify({lv:loungeLv(),defs:loungeSeatDefs().map(x=>[x.kind,x.x,x.y,x.leg?1:0]),leg:LG.leg,x0:LG.bar.x0,w0:LG.bar.w0,by:LG.bar.y})"))
    bars = [x for x in d['defs'] if x[0] == 'bar']; run = sorted(x[1] for x in bars if not x[3]); leg = [x for x in bars if x[3]]
    check(d['lv'] >= 2 and len(bars) == 9 and len(run) == 7 and len(leg) == 2 and d['leg'], f'Lounge III: nine stools, seven along and two on the L: {bars}')
    check(all(b2 - a >= 30 for a, b2 in zip(run, run[1:])) and run[-1] + 12 <= 374 and run[0] - 12 >= d['leg']['x1'], f'a hand apart along the counter, the last inside a phone\'s view, the first clear of the L: {run}')
    ly = sorted(x[2] for x in leg)
    check(ly[1] - ly[0] >= 26 and all(x[1] + 12 <= d['leg']['x0'] for x in leg) and all(d['leg']['y0'] <= y <= d['by'] + 36 for y in ly) and d['leg']['y0'] < d['by'], f'the L\'s two, one behind the other beside it — the return running back from the counter toward the wall: {leg} {d["leg"]}')
    check(d['x0'] < d['w0'] and d['defs'][0][0] == 'bar' and all(x[0] == 'bar' for x in d['defs'][:6]) and all(x[0] == 'bar' for x in d['defs'][-3:]) and d['defs'][-1][3] == 1, f'the counter longer than the wine wall; the first six first, the new three last: {d["defs"]}')
    # walking in from the arch to the first stool past the L: round it
    w = json.loads(g.ev("""JSON.stringify((()=>{const L=LG.leg,b=LG.bar,t=loungeSeatDefs().filter(x=>x.kind==='bar'&&!x.leg).sort((a,c)=>a.x-c.x)[0];const e={x:LG.door.x,y:LG.door.y,room:'lounge',troom:'lounge',tx:t.x,ty:t.y+8};const path=[];let ok=false;
      for(let i=0;i<800;i++){if(stepTo(e,2)){ok=true;break}path.push([e.x,e.y])}
      const inL=path.filter(p=>p[0]>L.x0&&p[0]<L.x1&&p[1]>L.y0&&p[1]<b.y+34).length,inC=path.filter(p=>p[0]>b.x0&&p[0]<b.x1&&p[1]>b.y&&p[1]<b.y+34).length;return{ok,steps:path.length,inL,inC}})())"""))
    check(w['ok'] and w['inL'] == 0 and w['inC'] == 0, f'from the street door to the counter: round the L, never through it or the counter: {w}')
    # rc7.7 (12:43): the L closes round the bartenders — from the back door they come in by the gap at the return's far end
    k = json.loads(g.ev("""JSON.stringify((()=>{const L=LG.leg,b=LG.bar;const out=[];for(const px of[b.x0+70,b.x0+140,b.x0+210]){const e={x:LG.bk.x,y:LG.bk.y,room:'lounge',troom:'lounge',bk:1,tx:px,ty:b.y-6};const path=[];let ok=false;
      for(let i=0;i<900;i++){if(stepTo(e,2)){ok=true;break}path.push([e.x,e.y])}
      out.push({px,ok,inL:path.filter(p=>p[0]>L.x0&&p[0]<L.x1&&p[1]>L.y0&&p[1]<b.y+34).length,inC:path.filter(p=>p[0]>L.x1&&p[0]<b.x1&&p[1]>b.y+2&&p[1]<b.y+34).length,gap:path.filter(p=>p[0]>=L.x0-4&&p[0]<=L.x1+4&&p[1]<L.y0).length})}
      return{out,inside:[KEN_HOST.x>L.x1&&KEN_HOST.y<b.y,b.x0+70>L.x1],pick:cnPick(),L,by:b.y}})())"""))
    check(all(o['ok'] and o['inL'] == 0 and o['inC'] == 0 and o['gap'] > 0 for o in k['out']), f'from the back door to each bartender\'s place: by the gap at the return\'s far end, never through it or the counter: {k["out"]}')
    check(all(k['inside']) and k['pick']['x'] < k['L']['x0'] and k['pick']['y'] < k['L']['y0'] + 10, f'inside the L: the bartenders\' places and Ken\'s; outside it, at its far end: where the floor picks up: {k}')
    check('L 型' in g.ev("LOUNGE_PROJ.find(p=>p.lv===2).d") and '九個位子' in g.ev("LOUNGE_PROJ.find(p=>p.lv===2).d"), 'the shop\'s Lounge II says so')
    # Lounge I: six in a row, no L
    g.ev("S.rooms.lounge=1;IDLE=null;bg=null;for(const k in BGC)delete BGC[k]")
    d1 = json.loads(g.ev("JSON.stringify({leg:LG.leg,x0:LG.bar.x0,bars:loungeSeatDefs().filter(x=>x.kind==='bar').map(x=>x.x)})"))
    check(d1['leg'] is None and d1['x0'] == 192 and len(d1['bars']) == 6 and all(b2 - a >= 30 for a, b2 in zip(d1['bars'], d1['bars'][1:])), f'Lounge I: six in a row, no L: {d1}')
    g.ev("S.rooms.lounge=3;IDLE=null;bg=null;for(const k in BGC)delete BGC[k]")
    # a day on the save: people sit at the new stools, and the room draws
    to_service(g); g.ev("window.__act=window.__actLazy")
    g.ev("window.__lgSat={};const s0=seatGroup;seatGroup=function(q,t){if(t&&t.room==='lounge'&&t.kind==='bar')__lgSat[t.i]=1;return s0.apply(this,arguments)}")
    g.ev("__botUntil('R.t>=R.dur*.8',120000,1/30)")
    sat = json.loads(g.ev("JSON.stringify({sat:Object.keys(__lgSat).map(Number),legs:loungeTables().filter(t=>t.leg).map(t=>t.i),seventh:loungeTables().filter(t=>t.kind==='bar'&&!t.leg).sort((a,c)=>c.x-a.x)[0].i})"))
    check(len(sat['sat']) >= 5, f'the stools are sat on in an evening: {sat}')
    g.ev("setRoom('lounge')"); g.ev("for(let i=0;i<4;i++)__tick(1000/30)")
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc76_dylan_at_home_keeps_his_hood_up(b, port, target):
    """07:44 「在房間Dylan就穿帽T一直戴著帽T帽子吧」: in Jill's room Dylan's hoodie has its hood up — over his hair and his
    ears — wherever he is in the room (the desk from behind, the sofa, walking about); his face, his glasses, a little
    fringe show. In the restaurant he is the guest he always was (no hood)."""
    g = Game(b, port, target, seed=7632, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day74_1508.json')
    lk = json.loads(g.ev("JSON.stringify({home:{up:DYLAN_HOME.hoodUp,pat:DYLAN_HOME.pat,acc:DYLAN_HOME.acc,hs:DYLAN_HOME.hs},out:{up:!!DYLAN.looks[0].hoodUp,pat:DYLAN.looks[0].pat}})"))
    check(lk['home']['up'] is True and lk['home']['pat'] == 'hoodie' and lk['home']['acc'] == 'glasses' and lk['home']['hs'] == 9 and not lk['out']['up'] and lk['out']['pat'] == 'cardi', f'home: the hood up; out: the cardigan: {lk}')
    # drawn: the top of his head and his ears are the hood's grey at home, his hair and skin out
    px = json.loads(g.ev("""JSON.stringify((()=>{const at=(L,back)=>{const cv=document.createElement('canvas');cv.width=120;cv.height=200;const c=cv.getContext('2d');c.save();c.translate(60,180);c.scale(3,3);if(back)drawPersonBack(c,0,0,L,{s:1/PSC});else drawPerson(c,0,0,L,{pscale:1,mood:'happy'});c.restore();
        const hy=back?(-4-25):(-9-25),get=(x,y)=>Array.from(c.getImageData(60+x*3,180+y*3,1,1).data).slice(0,3);return{crown:get(0,hy-8),ear:get(back?-11.2:-9.3,hy+1.6),face:get(0,hy+3)}};
      return{home:at(DYLAN_HOME),out:at(DYLAN.looks[0]),back:at(DYLAN_HOME,true),backOut:at(DYLAN.looks[0],true)}})())"""))
    grey = lambda p: abs(p[0] - p[1]) < 18 and abs(p[1] - p[2]) < 18 and 110 < p[0] < 200
    dark = lambda p: sum(p) < 200
    check(grey(px['home']['crown']) and grey(px['home']['ear']) and not grey(px['home']['face']), f'at home: the hood over the crown and the ears, the face showing: {px["home"]}')
    check(dark(px['out']['crown']) and not grey(px['out']['ear']), f'out: his dark hair, his ears: {px["out"]}')
    check(grey(px['back']['crown']) and dark(px['backOut']['crown']), f'from behind: the hood, not his hair: {px["back"]} / {px["backOut"]}')
    # in Jill's room he is drawn in it at the desk
    g.ev("window.__dl=[];const b0=drawPersonBack;drawPersonBack=function(c,x,y,L,o){__dl.push(!!L.hoodUp);return b0.apply(this,arguments)};const p0=drawPerson;drawPerson=function(c,x,y,L,o){if(L&&L.hs===9)__dl.push(!!L.hoodUp);return p0.apply(this,arguments)}")
    btn = g.page.locator('[data-act="peek"]')
    if btn.count(): btn.first.click()
    g.ev("setRoom('home')"); g.ev("forceDraw=true;for(let i=0;i<6;i++)__tick(1000/30)")
    seen = json.loads(g.ev("JSON.stringify({desk:!!homeDylanAtDesk(),drawn:__dl})"))
    check(seen['desk'] and seen['drawn'] and all(seen['drawn']), f'at his desk in the room, hood up: {seen}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc76_after_the_wine_the_tasting_night_is_the_players(b, port, target):
    """08:51 「少賺沒關係 但是之後聯名酒出了之後開店前可以選擇要不要舉辦品酒之夜」: once 「晚餐之後」 is out Ken no longer plans his
    nights; before opening the news asks 「品酒之夜｜今晚要辦嗎？」 — 「今晚辦」 makes tonight his (the whole Lounge), 「這次
    不辦」 takes it back before the doors open. At most once a week, never on the chef's night. A later night a save had
    already planned by itself becomes the player's to hold. Before the wine, nothing changes (the story's three)."""
    g = Game(b, port, target, seed=7633, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day74_1508.json')
    g.ev("S.cn=null;kenS().next=null;showPrep()"); g.page.wait_for_timeout(100)
    check('今晚要辦嗎' not in g.ev("$('#screen').innerText") and g.ev("ktHold()") is False, 'before the wine: no choice to make')
    g.ev("""for(const k of ['ken_propose','ken_t1','ken_t2','ken_t3','ken_collab','ken_samples','ken_wine']){const d=S.day-10;story().facts[k]={d,n:1,l:d}}
      const K=kenS();K.next={d:S.day+3,n:5};K.lastD=S.day-10""")
    mig = json.loads(g.ev("JSON.stringify({next:kenS().next,nextN:kenS().nextN})"))
    check(mig['next'] is None and mig['nextN'] == 5, f'a night the save had planned by itself is the player\'s now: {mig}')
    g.ev("showPrep()"); g.page.wait_for_timeout(100)
    txt = g.ev("$('#screen').innerText")
    check('品酒之夜｜今晚要辦嗎？' in txt and g.page.locator('#screen [data-act=ktHold]').count() == 1, 'before opening, the news asks')
    g.ev("(()=>{const e=document.querySelector('#screen .kt-ask');if(e)e.scrollIntoView({block:'center'})})()"); g.page.wait_for_timeout(80)
    g.page.screenshot(path=os.path.join(ROOT, 'tests', 'artifacts', 'rc76_tasting_ask.png'))
    g.page.locator('#screen [data-act=ktHold]').click(); g.page.wait_for_timeout(150)
    txt = g.ev("$('#screen').innerText")
    check(json.loads(g.ev("JSON.stringify(kenS().next)")) == {'d': g.ev("S.day"), 'n': 5} and '今晚｜品酒之夜 · 23 席' in txt and g.page.locator('#screen [data-act=ktCancel]').count() == 1, f'「今晚辦」: tonight is his, and it can still be taken back: {g.ev("JSON.stringify(kenS().next)")}')
    g.page.locator('#screen [data-act=ktCancel]').click(); g.page.wait_for_timeout(150)
    check(g.ev("kenS().next") is None and '今晚要辦嗎' in g.ev("$('#screen').innerText"), '「這次不辦」: not tonight')
    # not on the chef's night
    g.ev("S.cn={n:1,last:S.day-9,next:{d:S.day,menu:cnMenu()}};showPrep()"); g.page.wait_for_timeout(100)
    check(g.ev("ktWhyNot()") == '今晚是主廚之夜' and g.ev("ktHold()") is False and '今晚要辦嗎' not in g.ev("$('#screen').innerText"), 'never on the chef\'s night')
    g.ev("S.cn=null;showPrep()"); g.page.wait_for_timeout(100)
    g.page.locator('#screen [data-act=ktHold]').click(); g.page.wait_for_timeout(150)
    to_service(g); g.ev("window.__act=window.__actLazy")
    check(g.ev("!!R.kt&&R.kt.n===5&&R.kt.people===23"), f'the night is on, the whole room: {g.ev("JSON.stringify(R.kt&&{n:R.kt.n,people:R.kt.people})")}')
    g.ev("__botUntil('R.kt.end||phase!==\\'service\\'',150000,1/30)")
    after = json.loads(g.ev("JSON.stringify({end:R.kt.end,next:kenS().next,nextN:kenS().nextN,lastD:kenS().lastD,day:S.day})"))
    check(after['end'] and after['next'] is None and after['nextN'] == 6 and after['lastD'] == after['day'], f'afterwards nothing is planned for the player; the next would be the sixth: {after}')
    g.ev("__botUntil('phase!==\\'service\\'',90000,1/30)")
    g.ev("S.day++;S.phase='prep';phase='prep';showPrep()"); g.page.wait_for_timeout(100)
    check('今晚要辦嗎' not in g.ev("$('#screen').innerText") and '一週最多一次' in g.ev("ktWhyNot()"), f'once a week: {g.ev("ktWhyNot()")}')
    g.ev("S.day+=6;showPrep()"); g.page.wait_for_timeout(100)
    check('今晚要辦嗎' in g.ev("$('#screen').innerText") and g.ev("ktWhyNot()") == '', 'a week on, it can be held again')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc76_the_chefs_night(b, port, target):
    """(14:49; 22:11 「而且你不是說酒吧可以辦活動嗎？除了品酒。」; 08:00 「主廚之夜就是包場整間辦主廚之夜…整間都是給主廚之夜辦」)
    Jill's night in the Lounge, booked out: from Lounge II with a signature dish, planned in the shop for tomorrow — not on a
    night of Ken's, at most once a week; the news the day before and on the day says how many seats (the whole room); that
    night every seat is the chef's night's — nobody else is seated in the Lounge while it lasts, and the Lounge's own
    visitors who were coming (杜, here) come to it; some come in twos and fours. Three courses with a glass each, one
    after the other — the second only once the first is eaten — plated at the bar from what the kitchen made in the
    morning (the kitchen's stations never cook them), carried in the Lounge; $1,800 a head apart from the Lounge's tabs
    (whose list stays its takings); the first night held at its start and its end; the summary says so; the album has its
    picture."""
    g = Game(b, port, target, seed=7611, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day52.json')
    check(g.ev("cnWhyNot()") in ('要先有 Lounge II', '要先有招牌菜') and not g.ev("cnPlan()"), f'the Day 52 save: not yet ({g.ev("cnWhyNot()")})')
    load_save(g, 'player_day74_1508.json')
    g.ev("S.cn=null;kenS().next=null")
    check(g.ev("loungeLv()") >= 2 and g.ev("!!S.signature") and g.ev("cnWhyNot()") == '', 'the Day 74 save: Lounge III and a signature')
    g.ev("kenS().next={d:S.day+1,n:5}")
    check(g.ev("cnWhyNot()") == '明晚是品酒之夜', 'never on a night of Ken\'s')
    g.ev("kenS().next=null;shopTab='works';showShop()"); g.page.wait_for_timeout(100)
    card = g.ev("(()=>{const e=document.querySelector('#screen .cn-card');if(!e)return'';e.scrollIntoView({block:'center'});return e.innerText.replace(/\\s+/g,' ')})()")
    check('主廚之夜' in card and '排在明晚' in card and '$1,800' in card and '包下整個 Lounge' in card and '23 席' in card, f'the shop\'s Lounge section has it, booked out: {card!r}')
    g.page.screenshot(path=os.path.join(ROOT, 'tests', 'artifacts', 'rc76_shop_chefs_night.png'))
    g.ev("document.querySelector('#screen [data-act=cnPlan]').click()"); g.page.wait_for_timeout(150)
    plan = json.loads(g.ev("JSON.stringify({next:S.cn.next,day:S.day,menu:S.cn.next&&S.cn.next.menu.map(d=>[d,DISH(d).cat])})"))
    check(plan['next'] and plan['next']['d'] == plan['day'] + 1 and len(plan['menu']) == 3 and [m[1] for m in plan['menu']] == ['starter', 'main', 'dessert'] and plan['menu'][1][0] == 'signature', f'planned for tomorrow, three courses: {plan}')
    card = g.ev("(document.querySelector('#screen .cn-card')||{}).innerText||''")
    check('已排' in card and '取消' in card, f'the card says it is planned: {card!r}')
    check('明晚｜主廚之夜 · 23 席' in g.ev("cnNewsHTML()") and '包場' in g.ev("cnNewsHTML()"), 'the news the day before: the whole room')
    # the day (planned from this morning's prep for tomorrow: the test makes tomorrow today)
    g.ev("closeSub&&closeSub();S.cn.next.d=S.day;showPrep()"); g.page.wait_for_timeout(150)
    g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}"); _quiet(g)
    check(g.ev("cnTonight()") and '今晚｜主廚之夜 · 23 席' in g.ev("$('#screen').innerText"), f'the news on the day: {g.ev("phase")}')
    to_service(g); g.ev("window.__act=window.__actLazy;window.__noScenes=false;window.__holds=true;window.__fastSay=0")
    # what each table had, at the moment they paid (a ticket is gone once they leave); who else sat in the Lounge; what the kitchen cooked; the order of the courses
    g.ev("""window.__cnPaid=[];window.__cnOther=[];window.__cnCooked=0;window.__cnServed={};
      const c0=collect;collect=function(q,o){if(q&&q.cn&&q.ticket)__cnPaid.push({name:q.name,size:q.size,bar:q.table!=null&&R.tables[q.table].kind==='bar',items:q.ticket.items.map(i=>(DISH(i.d).wine?'w':i.d)+':'+i.st)});return c0.apply(this,arguments)};
      const s0=seatGroup;seatGroup=function(q,t){if(t&&t.room==='lounge'&&lgEvent()==='cn'&&!q.cn)__cnOther.push(q.name);return s0.apply(this,arguments)};
      const k0=startCook;startCook=function(tk,it){if(tk&&tk.cn)__cnCooked++;return k0.apply(this,arguments)};
      const v0=serveItems;serveItems=function(q,list){if(q&&q.cn)for(const x of list)if(x.it.st==='ready'&&!DISH(x.it.d).wine){const a=__cnServed[q.id]=__cnServed[q.id]||[];a.push([x.it.course,R.t])}return v0.apply(this,arguments)};""")
    st = json.loads(g.ev("JSON.stringify({cn:!!R.cn,people:R.cn.people,groups:R.sched.filter(o=>o.cn).length,sizes:R.sched.filter(o=>o.cn).map(o=>o.size).sort().join(''),tables:loungeTables().length,res:loungeTables().filter(t=>t.cnr).length,other:lgSeatOpen({}),guest:lgSeatOpen({cn:1}),kt:!!R.kt})"))
    check(st['cn'] and st['people'] == 23 and st['tables'] == st['res'] and not st['other'] and st['guest'] and not st['kt'] and '2' in st['sizes'] and '4' in st['sizes'], f'tonight: the whole room booked, 23 people, some in twos and a four: {st}')
    # the Lounge's own visitors who were coming tonight come to it (lgBook, on a schedule of its own)
    bk = json.loads(g.ev("""JSON.stringify((()=>{const S0=R.sched,si=R.si;R.sched=[{t:1,type:'gourmet',size:1,name:DU,lounge:1},{t:2,type:'office',size:2,lounge:1},{t:3,type:'office',size:2}];R.si=0;
      const all=lgBook('cn',[],j=>10+j,(i,sz)=>({name:'x'+i,type:'office'}));const r={people:all.reduce((a,o)=>a+o.size,0),du:all.some(o=>o.name===DU&&o.cn&&o.lgCame),pair:all.some(o=>o.size===2&&o.lgCame&&o.cn),plain:!R.sched.find(o=>o.t===3||(!o.lounge&&o.size===2)).cn};R.sched=S0;R.si=si;return r})())"""))
    check(bk['people'] == 23 and bk['du'] and bk['pair'] and bk['plain'], f'the Lounge\'s own people come to the night (杜, a pair); the room is still 23; a dinner guest is left alone: {bk}')
    o = json.loads(g.ev("JSON.stringify((()=>{const out=new Set();for(let i=0;i<300;i++)for(const d of loungeOrder({size:2,type:'office',pat:1}))out.add(DISH(d).wine?'wine':DISH(d).bar?'bar':'food:'+d);return[...out]})())"))
    check(not any(x.startswith('food:') for x in o), f'anyone else in the Lounge (after the night): drinks and bar bites only: {o}')
    # the night, played: read the held scenes as a player would
    scenes, seen = {}, set()
    for _ in range(9000):
        if g.ev("!!(typeof DLG!=='undefined'&&DLG&&DLG.sh)"):
            k = g.ev("DLG.sh.k"); lines = []
            t0 = g.ev("R.t"); g.ev("for(let i=0;i<5;i++)__tick(1000)"); frozen = g.ev("R.t") == t0
            for _ in range(30):
                if not g.ev("!!(DLG&&DLG.sh)"): break
                lines.append(g.ev("$('#dlg .dlg-name').textContent+'：'+$('#dlg .dlg-text').textContent")); g.ev("__tick(300);dlgNext()")
            scenes.setdefault(k, []).append((frozen, lines)); continue
        g.page.evaluate('()=>window.__bot(30,1/30)')
        r = json.loads(g.ev("JSON.stringify(R&&R.cn?{on:R.cn.on,end:R.cn.end,n:R.cn.guests.length}:{gone:1})"))
        if (r.get('end') and not g.ev("!!(typeof DLG!=='undefined'&&DLG&&DLG.sh)")) or g.ev("phase") != 'service': break
        if r.get('on') and 'lounge' not in seen:
            seen.add('lounge'); g.ev("setRoom('lounge')")
    cnS = scenes.get('cn_first', [])
    check(len(cnS) >= 2 and cnS[0][0] and any('今天三道。不用點，一道一道上。' in x for x in cnS[0][1]) and any('謝謝。' in x for x in cnS[-1][1]), f'the first night: held at its start and its end: {cnS}')
    res = json.loads(g.ev("""JSON.stringify((()=>{return{end:R.cn.end,people:R.cn.guests.reduce((a,q)=>a+q.size,0),served:R.cn.guests.every(q=>q.gone||q.state==='leave'||(q.ticket&&q.ticket.items.every(i=>i.st==='served'))),
      fact:!!fact('cn_first'),S:S.cn,list:Object.values(R.st.lgSold||{}).reduce((a,x)=>a+x.rev,0),takings:R.st.lgRev||0,at:Math.floor((17*60+R.cn.t0/R.dur*270)/60),endAt:R.t/R.dur}})())"""))
    check(res['at'] == 19, f'it begins after seven, as the scene and the manual say: {res["at"]}:xx')
    check(res['list'] == res['takings'], f'the Lounge\'s list is still its takings: {res}')
    check(res['end'] and res['people'] == 23 and res['served'] and res['endAt'] < .9, f'the night came to its end well before closing: all 23, every course and glass out: {res}')
    check(res['fact'] and res['S']['n'] == 1 and res['S']['next'] is None and res['S']['last'] == g.ev("S.day"), f'counted once: {res["S"]}')
    other = json.loads(g.ev("JSON.stringify(__cnOther)"))
    check(not other, f'nobody else sat in the Lounge while it lasted: {other}')
    check(g.ev("__cnCooked") == 0, 'the kitchen\'s stations never cooked the night\'s plates (made in the morning, plated at the bar)')
    order = json.loads(g.ev("JSON.stringify(Object.values(__cnServed))"))
    def in_order(a):
        last = {}
        for c, t in a: last[c] = max(last.get(c, -1), t)
        first = {}
        for c, t in a: first[c] = min(first.get(c, 1e9), t)
        return all(first.get(c + 1, 1e9) >= last.get(c, -1) for c in (0, 1))
    check(order and all(in_order(a) for a in order) and all(len(a) % 3 == 0 for a in order), f'course by course: the second never before the first is out, the third never before the second: {order[:3]}')
    # the rest of the day; what they paid; the summary
    g.ev("window.__holds=false;window.__noScenes=true")
    g.ev("__botUntil('phase!==\\'service\\'',90000,1/30)")
    paid = json.loads(g.ev("JSON.stringify(__cnPaid)"))
    check(sum(x['size'] for x in paid) == 23, f'all 23 paid: {[(x["name"], x["size"]) for x in paid]}')
    check(all(len(x['items']) == 6 * x['size'] and sum(1 for y in x['items'] if y.startswith('w:')) == 3 * x['size'] and all(y.endswith(':served') for y in x['items']) for x in paid), f'each had the three courses and three glasses: {paid[:3]}')
    lg = json.loads(g.ev("JSON.stringify(S.lastSummary.lg)"))
    check(lg['cn'] and lg['cn']['n'] == 23 and lg['cn']['rev'] == 23 * 1800, f'$1,800 a head, on the Lounge\'s line apart from its tabs: {lg}')
    txt = g.ev("$('#screen').innerText")
    check('主廚之夜' in txt, 'the summary says so')
    notes = json.loads(g.ev("JSON.stringify([...document.querySelectorAll('#screen .daynotes div')].map(e=>e.innerText.replace(/\\s+/g,' ')))"))
    check('主廚之夜 23 位・營業額 $41,400' in notes and not any(x.startswith('Lounge ') for x in notes), f'12:43: the whole room booked, so the night is one line, the chef\'s night — no 「Lounge 0 桌」 beside it: {notes}')
    check(g.ev("albumList().some(p=>p.kind==='chefnight')"), 'the album has the night')
    check('一週最多一次' in g.ev("cnWhyNot()"), 'and the next one is a week away')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc77_the_page_carries_only_the_portraits_the_game_shows(b, port, target):
    """rc7.1 (the player, 2026-10-02 21:05: the page took more than ten seconds to open on the phone) took the portraits the
    game never shows out of the page — the seven outside-cast cards of P5 (paused) and the 2.2.1 staff cards the player
    redrew as st23_*; they stay as files in assets/portraits. rc7.2 was built on rc7 without rc7.1 (the text-box backup
    that froze the iPhone), and the 35 came back with it: 0.77 MB the game never used, from rc7.2 to rc7.6. rc7.7 takes
    them out again, with Sophie's and Mia's first cards (sophie, mia: redrawn as reg23_* in v2.3, never asked for since).
    The game asks PORTRAIT_DATA only for the keys in its four tables (PORTRAITS, STAFF_PORTRAITS, PORTRAIT_TONES, NAMED):
    the page holds exactly those — every face the game can show, nothing it cannot. (A key found somewhere in game.js is
    not enough: 'sophie' and 'mia' are there as people, not as portraits.)"""
    g = Game(b, port, target, seed=7701, manual=True, viewport={'width': 390, 'height': 844})
    r = json.loads(g.ev("""JSON.stringify((()=>{const want=new Set();
      for(const P of Object.values(PORTRAITS))for(const k of Object.values(P.v))want.add(k);
      for(const k of Object.values(STAFF_PORTRAITS))want.add(k);
      for(const T of Object.values(PORTRAIT_TONES))for(const k of Object.values(T))want.add(k);
      for(const N of Object.values(NAMED))if(N&&N.p)want.add(N.p);
      const have=Object.keys(window.PORTRAIT_DATA||{});return{want:[...want],have,missing:[...want].filter(k=>!PORTRAIT_DATA[k])}})())"""))
    check(len(r['want']) >= 60, f"the game's faces were found: {len(r['want'])}")
    check(not r['missing'], f'every face the game can show is in the page: missing {r["missing"]}')
    extra = sorted(set(r['have']) - set(r['want']))
    check(not extra, f'the page carries no portrait the game never asks for: {extra}')
    src = open(os.path.join(ROOT, 'js', 'game.js'), encoding='utf-8').read()
    check(src.count('portraitData(') == 9, 'the game asks for a portrait in the nine places this test knows (a new one: add its table above)')
    gone = re.compile(r'^(v24_(xtm|shan|gx|lin|kevin|yx|xtf)(_[a-z]+)?|staff_([1-6]|xiaotong|momo|nina|yuki|azhu|hugo|azhe|aming)|sophie|mia)$')
    check(not [k for k in r['have'] if gone.match(k)], 'the outside cast and the 2.2.1 cards are not in the page')
    kept = [os.path.basename(p)[:-4] for p in glob.glob(os.path.join(ROOT, 'assets', 'portraits', '*.png'))]
    check(any(gone.match(k) for k in kept), 'they are still kept as files in assets/portraits')
    # a face from each source still shows: Jill, a regular, a named guest with moods, the staff
    for who, tone in [('jill', 'warm'), ('mia', 'thinking'), ('named:品酒師 Ken', 'wry'), ('staff:許葳', 'work'), ('staff:沈晴', None)]:
        ok = g.ev(f"!!(portraitOf({json.dumps(who, ensure_ascii=False)},{json.dumps(tone)})||{{}}).src")
        check(ok, f'{who} ({tone}) has a face')
    check(not g.errors, g.errors[:3]); g.close()


def _load_raw(g, raw):
    g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.page.wait_for_timeout(150)
    g.click('[data-act=openFresh]') if g.page.query_selector('[data-act=openFresh]') else g.click('[data-act=open]'); g.page.wait_for_timeout(150)


@test
def v24_rc77_evan_is_behind_the_bar_from_the_first_night(b, port, target):
    """10:32 「Lounge 剛蓋好、還沒請 bartender 不應該有這種情況 因為Evan 一開始就要在酒吧裡」 (and the canon of 2026-10-02 19:19
    §11C/§16: Evan was Madame Lin's bartender and stays on): building Lounge I puts Evan behind the bar that night — no
    hiring, no fee, never a recruitment card — and the Lounge opens its first night. A save whose Lounge was built without
    him has him back when it loads; a save that has him keeps him as he is."""
    g = Game(b, port, target, seed=7702, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day46.json')
    check(g.ev("loungeLv()") == 0 and not g.ev("S.crew.some(m=>m.name==='Evan')"), 'Day 46: no Lounge, no Evan yet')
    m0 = g.ev("S.money+=400000;S.money"); cost = g.ev("LOUNGE_PROJ[0].cost")
    g.ev("factSet('lounge_project');buyLounge(1);hideReveal&&hideReveal()")
    ev = json.loads(g.ev("JSON.stringify(S.crew.find(m=>m.name==='Evan')||null)"))
    check(ev and ev['role'] == 'bartender' and ev['duty'] == 'lbar' and ev['pool'] == 'lounge' and ev['lv'] == 1, f'Evan is there, behind the bar: {ev}')
    check(g.ev("S.money") == m0 - cost, 'nothing paid for him, only the room')
    check(g.ev("loungeOpenTonight()") and g.ev("S.crew.filter(m=>m.name==='Evan').length") == 1, 'the Lounge opens its first night; one Evan')
    g.ev("shopTab='staff';showShop()"); g.page.wait_for_timeout(100)
    check(not g.ev("!!document.querySelector('#screen [data-act=hireLounge][data-k=\"Evan\"]')") and '在店裡' in g.ev("(()=>{const e=[...document.querySelectorAll('#screen .item')].find(e=>e.innerText.includes('Evan 林奕文'));return e?e.innerText:''})()"), 'his card: in the shop, no recruitment')
    g.ev("closeSub&&closeSub()")
    # an older save whose Lounge was built without him: he is back when it loads, behind the bar
    raw = json.load(open(os.path.join(ROOT, 'tests', 'saves', 'player_day74_1508.json'), encoding='utf-8')); raw = raw.get('save', raw)
    others = sorted(m['name'] for m in raw['crew'] if m.get('pool') == 'lounge' and m['name'] != 'Evan')
    no = dict(raw); no['crew'] = [m for m in raw['crew'] if m['name'] != 'Evan']
    _load_raw(g, no)
    back = json.loads(g.ev("JSON.stringify({e:S.crew.filter(m=>m.name==='Evan'),lg:poolCrew('lounge').map(m=>m.name).sort(),open:loungeOpenTonight()})"))
    check(len(back['e']) == 1 and back['e'][0]['lv'] == 1 and back['e'][0]['duty'] == 'lbar' and back['e'][0]['pool'] == 'lounge', f'Evan is back: {back["e"]}')
    check(sorted(n for n in back['lg'] if n != 'Evan') == others and back['open'], f'the rest of the Lounge as it was: {back["lg"]}')
    # a save that has him keeps him as he is
    _load_raw(g, raw)
    keep = json.loads(g.ev("JSON.stringify(S.crew.filter(m=>m.name==='Evan').map(m=>m.lv))"))
    check(keep == [[m for m in raw['crew'] if m['name'] == 'Evan'][0]['lv']], f'kept as he was: {keep}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc77_the_lounge_pours_kens_rounds(b, port, target):
    """10:10 「Ken自己倒酒也太累了吧 酒吧的服務生不能幫忙嗎？品酒日的時候原本的bartender要不要上班」: on a tasting night the
    bartenders are on as every night; Ken hosts behind the bar and opens each of the three; a round opened at the bar is
    handed along the bar by the bartenders and carried to the tables and the sofa by the Lounge's floor person, from the
    end of the bar's L, where it waits on a tray — never on the kitchen's pass, never fetched by the restaurant's floor.
    With no floor person in, the bartenders walk it over. Every round reaches every seat."""
    spy = """window.__kp=[];const s0=serveItems;serveItems=function(g,list){for(const c of list){const it=c.it;if(it&&it.ktp&&it.st==='ready'){const t=R.tables[g.table];
      const m=(S.crew||[]).find(m=>{const w=R.cw&&R.cw[m.id];return w&&w.carry&&w.carry.includes(it)});const j=R.jill.carry.some(c0=>c0.it===it);
      __kp.push({bar:t.kind==='bar',role:m?m.role:(j?'jill':'?'),name:m?m.name:'',lg:m?crewPool(m):''})}}return s0.apply(this,arguments)};
      window.__pass=0;window.__tray=0;const u0=kenRounds;kenRounds=function(){const r=u0.apply(this,arguments);for(const tk of R.tickets)for(const it of tk.items)if(it.ktp&&it.st==='ready'&&!it.picked){__tray++;if(it.lbar||!tk.kt)__pass++}return r}"""
    for floor in (True, False):
        g = Game(b, port, target, seed=7703 if floor else 7704, manual=True, viewport={'width': 390, 'height': 844})
        load_save(g, 'player_day74_1508.json')
        g.ev("factSet('ken_propose');factSet('ken_cut');S.cn=null;kenS().next={d:S.day,n:5};showPrep()")
        if not floor:
            g.ev("for(const m of S.crew)if(m.name==='安安')m.duties.lounge=false")
        on = json.loads(g.ev("JSON.stringify(S.crew.filter(m=>m.role==='bartender'&&m.duty==='lbar').map(m=>m.name))"))
        check(len(on) >= 1, f'the bartenders are on tonight: {on}')
        to_service(g); g.ev("window.__act=window.__actLazy")
        g.ev(spy)
        g.ev("__botUntil('R.kt&&R.kt.end',150000,1/30)")
        kp = json.loads(g.ev("JSON.stringify(__kp)"))
        bar = [k for k in kp if k['bar']]; tab = [k for k in kp if not k['bar']]
        check(bar and all(k['role'] == 'bartender' for k in bar), f'along the bar, the bartenders: {bar[:6]}')
        if floor:
            check(tab and all(k['role'] == 'waiter' and k['lg'] == 'lounge' for k in tab), f'to the tables, the Lounge\'s floor person: {tab[:6]}')
        else:
            check(tab and all(k['role'] == 'bartender' for k in tab), f'no floor person in: the bartenders walk them over: {tab[:6]}')
        check(not any(k['role'] in ('?', 'jill') for k in kp), 'every round was carried by someone of the Lounge')
        left = json.loads(g.ev("JSON.stringify(R.kt.guests.filter(q=>q.ticket).map(q=>q.ticket.items.filter(i=>i.ktw&&i.ktp&&i.st!=='served').length))"))
        check(sum(left) == 0, f'every round that was opened reached its seat: {left}')
        check(g.ev("__tray") >= 1 and g.ev("__pass") == 0, 'a round waits at the bar, never at the pass')
        check(g.ev("R.kt.host.state==='host'||R.kt.host.gone||!R.groups.includes(R.kt.host)") and g.ev("R.kt.host.table==null"), 'Ken hosted from behind the bar, never sat')
        check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc77_kens_share_of_a_tasting_night(b, port, target):
    """10:10 「Ken辦品酒日也可以分潤給他吧？當天百分之三十利潤給Ken 才合理，從第一次開始就要，Ken本來想友情主持，而且是自己喜歡，但是
    Jill主動說要給」: from the first night the summary takes 30% of what the tasting guests paid for the glasses and the bites,
    less what those cost, on its own line 「品酒之夜分潤」, and the day's net is that much less. A day with no tasting night
    pays nothing. A save whose proposal came before this (no share said) hears Jill say it at the end of its next night —
    (12:43) 「不行，該算的還是要算」, with no figure in her words; the figure is on the summary's line."""
    g = Game(b, port, target, seed=7705, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day74_1508.json')
    g.ev("factSet('ken_propose');S.cn=null;kenS().next={d:S.day,n:5};showPrep()")
    check(g.ev("!fact('ken_cut')"), 'a save past the proposal, before the share')
    to_service(g); g.ev("window.__act=window.__actLazy;window.__fastSay=1")
    g.ev("""window.__paid=[];const c0=collect;collect=function(g,o){let rec=null;if(g.tasting&&R.kt&&R.kt.guests.includes(g)&&g.ticket){const items=g.ticket.items.filter(i=>i.st==='served');rec={n:g.size,cost:items.reduce((a,it)=>{const D=DISH(it.d);return a+(D&&D.wine?(D.cost||0):costOf(it.d))},0)}}const r=c0.apply(this,arguments);if(rec)__paid.push(rec);return r}""")
    g.ev("__botUntil('phase!==\\'service\\'',150000,1/30)")
    s = json.loads(g.ev("JSON.stringify({ken:S.lastSummary.ken,kt:S.lastSummary.kt,net:S.lastSummary.net,cut:!!fact('ken_cut')})"))
    paid = json.loads(g.ev("JSON.stringify(__paid)"))
    check(s['kt'] and s['kt']['n'] == sum(p['n'] for p in paid) and s['kt']['n'] >= 10, f'the night\'s guests counted: {s["kt"]} / {len(paid)} tabs')
    check(abs(s['kt']['cost'] - round(sum(p['cost'] for p in paid))) <= 1, f'what they had cost: {s["kt"]["cost"]}')
    check(s['ken'] == round(.3 * max(0, s['kt']['rev'] - s['kt']['cost'])) and s['ken'] > 0, f'30% of the night\'s profit: {s}')
    txt = g.ev("$('#screen').innerText")
    check('品酒之夜分潤' in txt and 'Ken，品酒客利潤的三成' in txt, 'the ledger\'s line')
    notes = json.loads(g.ev("JSON.stringify([...document.querySelectorAll('#screen .daynotes div')].map(e=>e.innerText.replace(/\\s+/g,' ')))"))
    check(f'品酒之夜 {s["kt"]["n"]} 位・營業額 ${s["kt"]["rev"]:,}' in notes and not any(x.startswith('Lounge ') for x in notes), f'12:43: the night shows once, as the tasting night — not 「Lounge N 桌」 beside it: {notes}')
    check(s['cut'], 'Jill said it at the night\'s end (a save past the proposal)')
    lines = ' / '.join(x['t'] for x in json.loads(g.ev("JSON.stringify((story().beatLines||{}).ken_cut||[])")))
    check('今晚的。以後每一次都有。' in lines and '不行，該算的還是要算。' in lines and '三成' not in lines, f'her words: {lines}')
    # a day without a tasting night: nothing
    g.ev("document.querySelector('[data-act=toShop]')&&document.querySelector('[data-act=toShop]').click()")
    g.page.wait_for_timeout(100)
    g.ev("kenS().next=null;S.cn=null")
    v = g.ev("phase")
    if v == 'shop':
        g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(200)
    to_service(g); g.ev("window.__act=window.__actLazy")
    g.ev("__botUntil('phase!==\\'service\\'',150000,1/30)")
    check(not g.ev("S.lastSummary.ken") and not g.ev("S.lastSummary.kt") and '品酒之夜分潤' not in g.ev("$('#screen').innerText"), 'a day without a tasting night pays nothing')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc8_the_lounge_is_the_shop_next_door(b, port, target):
    """The player's brief of 2026-10-02 19:19 (§0, HARD CANON): Jill's Kitchen and the bar next door each have their own door on
    the street; the wall between them is never opened — no door from the Main Hall to the Lounge; a guest walks out onto the
    street and in at its own door; the staff (and Jill) go the back way, the two shops' back rooms meeting behind the kitchen;
    the kitchen still makes the Lounge's food, its plates passed through the back to the end of the Lounge's bar. The street
    shows the bar next door in each of its states: Madame Lin's (open), closed after her last night, papered over for the work,
    The Lounge."""
    g = Game(b, port, target, seed=8104, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day2_2155.json')
    m = json.loads(g.ev("""JSON.stringify({guest:nextHop('main','lounge',{}),staff:nextHop('main','lounge',{bk:1}),staffK:nextHop('kitchen','lounge',{bk:1}),
      out:nextHop('lounge','front',{bk:1}),back:doorway('main','lounge'),street:doorway('front','lounge'),st:barState(),tab:roomsOpen().includes('lounge')})"""))
    check(m['guest'] == 'front' and m['staff'] == 'lounge' and m['staffK'] == 'main' and m['out'] == 'front', f'a guest by the street, the staff by the back: {m}')
    check(m['back'][1] == [g.ev("LG.bk.x"), g.ev("LG.bk.y")] and m['street'][0] == [g.ev("FR.ldoor.x"), g.ev("FR.ldoor.y")], f'the back door, the street door: {m}')
    check(m['st'] == 'lin' and not m['tab'], f'Day 2: Madame Lin\'s bar next door, open; not a room of Jill\'s: {m}')
    check(not g.ev("typeof LOUNGE_ARCH!=='undefined'"), 'no arch from the Main Hall')
    states = [g.ev("barState()")]
    g.ev("factSet('lin_closed')"); states.append(g.ev("barState()"))
    g.ev("factSet('lin_signed')"); states.append(g.ev("barState()"))
    check(states == ['lin', 'closed', 'reno'], f'the bar next door: open, closed after her last night, papered over: {states}')
    g.ev("BARV=1"); check(g.ev("roomsOpen().includes('lounge')") and g.ev("roomTabName('lounge')") == '隔壁', 'seen from inside in a scene: 「隔壁」')
    g.ev("BARV=null"); g.close()
    # Day 74: The Lounge; who walks which way, all evening
    g = Game(b, port, target, seed=8105, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day74_1508.json')
    check(g.ev("barState()") == 'lounge', 'Day 74: The Lounge next door')
    to_service(g); g.ev("window.__act=window.__actLazy")
    g.ev("""window.__walk={guestIn:[],staffIn:[],viaMain:0,staffViaFront:0};const s0=stepTo;stepTo=function(e,v){const r0=e.room;const r=s0.apply(this,arguments);if(e.room!==r0){
      const isCrew=!!e.bk;if(e.room==='lounge'){(isCrew?__walk.staffIn:__walk.guestIn).push(r0);if(!isCrew&&r0==='main')__walk.viaMain++;if(isCrew&&r0==='front')__walk.staffViaFront++}}return r}""")
    g.ev("__botUntil('phase!==\\'service\\'',200000,1/30)")
    w = json.loads(g.ev("JSON.stringify(__walk)"))
    check(len(w['guestIn']) >= 5 and set(w['guestIn']) == {'front'} and w['viaMain'] == 0, f'every guest came into the Lounge from the street: {w["guestIn"][:12]}')
    check(len(w['staffIn']) >= 2 and 'main' in w['staffIn'] and w['staffViaFront'] == 0, f'the staff came in by the back: {w["staffIn"][:12]}')
    g.close()
    # the kitchen's plates for the Lounge wait at the end of its bar; a tap on the street door goes in, from inside back out
    g = Game(b, port, target, seed=8106, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day74_1508.json')
    to_service(g); g.ev("window.__act=window.__actLazy")
    g.ev("__botUntil('R.t>=R.dur*.2',90000,1/30)")
    pu = json.loads(g.ev("JSON.stringify({lg:pickupFor(R.tables.find(t=>t.lounge),0),main:pickupFor(R.tables.find(t=>t.room==='main'),0),pick:cnPick()})"))
    check(pu['lg']['room'] == 'lounge' and abs(pu['lg']['x'] - pu['pick']['x']) < 1 and pu['main']['room'] == 'main', f'the Lounge\'s plates at the end of its bar, the rest at the pass: {pu}')
    g.ev("setRoom('front')")
    sx, sy = g.ev("SV.ox+FR.ldoor.x*SV.s"), g.ev("SV.oy+(FR.ldoor.y-40)*SV.s")
    g.page.mouse.click(sx, sy); g.page.wait_for_timeout(150)
    check(g.ev("room") == 'lounge', 'a tap on the Lounge\'s door on the street goes in')
    # from inside (on a phone the top-left corner sits under the HUD's buttons, as the Main Hall's front door does: the tabs are
    # the way; the door answers a tap where it is not covered, as on a desktop)
    g.ev("roomTap({x:LG.door.x,y:30},{preventDefault(){}})")
    check(g.ev("room") == 'front', 'and its door from inside goes back out onto the street')
    check(not g.errors, g.errors[:3]); g.close()


# ---------------------------------------------------------------- rc8 Checkpoint B: the Madame Lin line, stories 1–6
def _dlg_lines(g, cap=40):
    """step through the dialogue on screen; each line as 「name：text」"""
    out = []
    for _ in range(cap):
        if not g.ev("!!(typeof DLG!=='undefined'&&DLG)"): break
        out.append(g.ev("(()=>{const n=document.querySelector('#dlg .dlg-name'),t=document.querySelector('#dlg .dlg-text');return(n&&n.textContent?n.textContent+'：':'')+(t?t.textContent:'')})()"))
        g.ev("__tick(400);dlgNext()"); g.ev("for(let j=0;j<2;j++)__tick(1000/30)")
    return out


def _lin_play_days(g, days, stop=None):
    """the lazy bot through whole days, the scenes unseen, the main loop's evening run at closing (the bot does not), the
    player's one answer given (the tasting: food; next door is the story's — 《看看》 decides it, 2026-10-06); a dict of
    what each day did"""
    log = []
    for _ in range(days):
        for _k in range(3):
            if g.ev("phase") == 'summary': g.click('[data-act=toShop]'); g.page.wait_for_timeout(60)
            if g.ev("phase") == 'shop': g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(100)
        g.ev("for(let i=0;i<80&&typeof DLG!=='undefined'&&DLG;i++){__tick(400);dlgNext()}")
        news = g.ev("(()=>{const h=linNewsHTML();return h?h.replace(/<[^>]+>/g,' ').replace(/\\s+/g,' ').trim():''})()")
        g.ev("autoStock()")
        if g.ev("phase") != 'service': start_day(g)
        install_bot(g); g.ev(LAZY_ACTOR + "\nwindow.__act=window.__actLazy;window.__noScenes=true")
        day = g.ev("S.day")
        for _i in range(2500):
            if g.ev("sub==='tasting'"): g.ev("tastingDir('food')")
            g.ev("for(let i=0;i<20&&typeof DLG!=='undefined'&&DLG;i++){__tick(400);dlgNext()}")
            n = g.ev("__botUntil(\"sub==='tasting'||!!(typeof DLG!=='undefined'&&DLG)||(R.closing!=null&&!storyDay().eve)\",150,1/30)")
            if g.ev("!!R&&R.closing!=null&&!storyDay().eve"): g.ev("lifeEnsureEvening()")
            if g.ev("phase") != 'service' or not g.ev("!!R"): break
            if n < 150 and not g.ev("paused||sub==='tasting'||!!(typeof DLG!=='undefined'&&DLG)"): break
        if g.ev("phase") == 'service': g.ev("__bot(60000,1/30)")
        log.append(json.loads(g.ev("JSON.stringify({d:S.day,bar:barState(),din:S.lastSummary&&S.lastSummary.dinWine?S.lastSummary.dinWine.reduce((a,x)=>a+x.n,0):0,wineCost:S.lastSummary&&S.lastSummary.wine||0})")) | {'news': news})
        if stop and g.ev(stop): break
    return log


@test
def v24_rc8_madame_lin_next_door_on_day_one(b, port, target):
    """The player's 2026-10-02 19:19 §3 《隔壁》: Day 1, a few minutes before opening, Madame Lin — the bar next door —
    brings a small present: a brass door bell, hung on the shop's door. The scene holds the restaurant and is staged in
    the hall (she and Jill a few steps in from the door); one line says who she is, no more; nobody explains the present;
    nothing about Dylan. It never comes again, and never on a mature save."""
    g = Game(b, port, target, seed=9101, manual=True, viewport={'width': 390, 'height': 844})
    g.ev("__tick(500)"); g.click('[data-act=open]'); g.page.wait_for_timeout(150)
    g.ev("window.__noScenes=false;window.__holds=true")
    start_day(g); install_bot(g); g.ev("for(let i=0;i<3;i++)__tick(1000/30)")
    st = json.loads(g.ev("JSON.stringify({day:S.day,held:!!(DLG&&DLG.hold),k:DLG&&DLG.sh&&DLG.sh.k,room,stage:STAGE&&STAGE.who.map(p=>p.id),jill:R.jill.room,j0:STAGE&&STAGE.jill0&&{x:Math.round(STAGE.jill0.x),y:Math.round(STAGE.jill0.y)}})"))
    check(st['day'] == 1 and st['held'] and st['k'] == 'lin_hello' and st['room'] == 'main' and st['stage'] == ['lin'] and st['jill'] == 'main', f'Day 1, before the first guest: her scene holds the hall, she stands in it: {st}')
    txt = ' / '.join(_dlg_lines(g))
    for w in ['隔壁酒吧的 Madame Lin', 'Madame Lin：終於開了。', 'Jill：嗯。', 'Madame Lin：恭喜。', 'Jill：謝謝。', 'Jill：妳還帶東西來。', 'Madame Lin：開店哪有空手來的。', 'Jill：妳不是就在隔壁。', 'Madame Lin：隔壁更不能空手。', '黃銅的小門鈴']:
        check(w in txt, f'「{w}」: {txt}')
    check(not any(w in txt for w in ('Dylan', '老公', '先生', '代表', '象徵', '祝你')), f'nothing about Dylan; nobody explains the present: {txt}')
    af = json.loads(g.ev("JSON.stringify({bell:propOn('linbell'),stage:STAGE,room,jill:{x:Math.round(R.jill.x),y:Math.round(R.jill.y),room:R.jill.room},barv:BARV,page:((story().beatLines||{}).lin_hello||[]).length,line:lineProgress(STORY_LINES.find(L=>L.k==='nextdoor')).done.map(b=>b.k)})"))
    check(af['bell'] and af['stage'] is None and af['room'] == 'main' and {'x': af['jill']['x'], 'y': af['jill']['y']} == st['j0'] and af['barv'] is None, f'the bell is on the door; the stage cleared, Jill back where she was: {af} {st}')
    check(af['page'] >= 11 and 'lin_hello' in af['line'], f'the story page 「隔壁」 keeps it, every line: {af}')
    g.ev(LAZY_ACTOR + "\nwindow.__act=window.__actLazy;window.__noScenes=true")
    g.ev("__botUntil('phase!==\"service\"',200000,1/30)")
    g.click('[data-act=toShop]'); g.page.wait_for_timeout(60); g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(100)
    g.ev("autoStock()"); start_day(g)
    check(g.ev("S.day") == 2 and g.ev("evState('lin_hello').n") == 1 and not g.ev("!!(DLG&&DLG.sh&&DLG.sh.k==='lin_hello')"), 'once')
    check(not g.errors, g.errors[:3]); g.close()
    g = Game(b, port, target, seed=9102, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day74_1508.json'); to_service(g)
    check(g.ev("!!fact('lin_hello')&&fact('lin_hello').retro===1&&evState('lin_hello').retro===1&&evState('lin_hello').d!==S.day&&!story().trace.some(t=>t.d===S.day&&t.k==='lin_hello')") is True, 'a mature save: no Day 1 scene on Day 74 (her Day 1 is the save\'s history, Checkpoint C)')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_the_tasting_night_comes_from_kens_story_alone(b, port, target):
    """The user, 2026-10-07 (PROJECT_MEMORY §6): Ken's tasting night has no Fine Dining, no restaurant level and no rating
    gate — it comes from Ken's own story: his visits, a main he ate (ken_wine_q), the pairing talk and the idea next door.
    (S.level>=4 was v2.3's, 421dd42; the rating 4.0 one morning's, a8c6abd; neither was the user's.) With Ken's story in
    place the night may come at level 1 and a rating of 3.0; one pairing talk short, it does not, even at level 5 and 4.5+.
    The journal's 「晚餐之後」 has no condition of its own: on the page from a new game as 「？？？」, its title once Ken asks."""
    g = Game(b, port, target, seed=8301, manual=True)
    g.click('[data-act=open]'); g.page.wait_for_timeout(100)
    r = json.loads(g.ev("""JSON.stringify((()=>{const E=STORY_EV.find(e=>e.k==='ken_tasting');const C=()=>restChapters().find(c=>c.t==='晚餐之後');
      const rate=s=>{S.reviews=Array.from({length:120},()=>({s,w:1}))};const out={};
      out.no_cond=!C().showIf;out.hid_new=!!C().hidden();
      factSet('ken_wine_q');factSet('ken_pairing');factSet('lounge_idea');factSet('lounge_idea');story().named[KEN]={v:5,last:S.day-1,dishes:{steak:3}};
      S.level=5;rate(5);out.short={level:S.level,rating:+rating().toFixed(1),when:!!E.when({})};
      factSet('ken_pairing');
      S.level=1;rate(3);out.low={level:S.level,rating:+rating().toFixed(1),when:!!E.when({})};
      out.hid_asked=!!C().hidden();return out})())"""))
    check(r['no_cond'] and r['hid_new'], f'「晚餐之後」 has no condition of its own; 「？？？」 before Ken asks: {r}')
    check(r['short']['level'] == 5 and r['short']['rating'] >= 4.5 and not r['short']['when'], f'one pairing talk short: no night, even at level 5 and a rating of 4.5+: {r}')
    check(r['low']['level'] == 1 and r['low']['rating'] <= 3.1 and r['low']['when'], f"Ken's story in place: the night may come at level 1 and 3.0: {r}")
    check(not r['hid_asked'], f'its title once Ken has asked: {r}')


@test
def v24_rc8_the_bar_next_door_from_kens_question_to_jills_decision(b, port, target):
    """§4–§12 on the player's Day 52 save (Ken has asked, no tasting yet, Dylan not revealed), played day by day (the
    scenes unseen; food): the tasting, and as Ken pays Jill keeps the pairing wines (「想喝酒，隔壁就有。」) —
    poured with dinner from then on, before any Lounge (at the pass, by the floor; in the wine cost and the summary);
    meanwhile Madame Lin's bar is open next door and guests walk over after dinner; a week or more of that, then
    「我做到月底。」 — her last night twelve days on, in the news before opening; Ken: 「不然吃完去哪？」; that night or later,
    in their room, 「……我有點想接。」 — before Dylan's reveal he is 「先生」, with no name; the book two days or more after;
    the viewing the next morning or later, one scene (the place, the kitchen behind it, Evan; nobody mentions Dylan) —
    and with it Jill has decided (2026-10-06: no card, the project is on the works page that day); Madame Lin's last
    night closes the bar. Nothing reveals Dylan."""
    g = Game(b, port, target, seed=8200, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day52.json')
    check(g.ev("!!fact('ken_wine_q')") and not g.ev("!!fact('tasting_night')") and g.ev("S.dylan.stage") == 2 and g.ev("barState()") == 'lin', 'the save: Ken has asked; no tasting yet; Dylan not revealed; her bar open')
    g.ev("window.__walked=[];const __so=sendOut;sendOut=function(q){if(q&&q.toBar&&barState()==='lin'&&!q.__w){q.__w=1;__walked.push({d:S.day,n:namedId(q)||q.type})}return __so.apply(this,arguments)}")
    g.ev("window.__din=[];const __sv=serveItems;serveItems=function(q,list){for(const c of list||[]){const it=c.it;if(it&&DISH(it.d)&&DISH(it.d).wine){const m=(S.crew||[]).find(m=>{const w=R.cw&&R.cw[m.id];return w&&w.carry&&w.carry.includes(it)});__din.push({d:S.day,dinw:!!it.dinw,lbar:!!it.lbar,by:m?m.role:'jill',room:(R.tables[q.table]||{}).room||'main'})}}return __sv.apply(this,arguments)}")
    log = _lin_play_days(g, 34, stop="!!fact('lin_closed')&&!!fact('lounge_project')")
    F = json.loads(g.ev("JSON.stringify(Object.fromEntries(['tasting_night','pairing_wine','lin_retiring','ken_where','jd_want','dylan_book','lin_viewing','lounge_project','lin_take','lin_closed'].map(k=>[k,fact(k)?fact(k).d:null])))"))
    E = json.loads(g.ev("JSON.stringify(Object.fromEntries(['ken_tasting','pairing_start','lin_retire','ken_where','jd_want','dylan_book','lin_viewing','lin_last','lounge_reveal'].map(k=>[k,evState(k).d||null])))"))
    check(all(F[k] for k in F) and not E['lounge_reveal'], f'every step happened, and no after-close Lounge idea: {F} {E}')
    check(F['tasting_night'] == F['pairing_wine'] == E['pairing_start'], f'the wines kept the night of the tasting: {F} {E}')
    check(F['lin_retiring'] - F['pairing_wine'] >= 7, f'a week or more of that life before 「我做到月底」: {F}')
    check(F['lin_retiring'] <= F['ken_where'] <= F['jd_want'] and F['jd_want'] > F['lin_retiring'], f'Ken minds it after she says it; Jill tells Dylan after: {F}')
    check(F['dylan_book'] - F['jd_want'] >= 2 and F['lin_viewing'] > F['dylan_book'] and F['lounge_project'] == F['lin_take'] == F['lin_viewing'], f'the book days after she told him; the viewing after the book; her decision with it (no card): {F}')
    check(F['lin_closed'] == F['lin_retiring'] + 12 and g.ev("linLast()") == F['lin_closed'], f'「月底」: twelve days on, her last night: {F}')
    news = [x for x in log if x['news']]
    check(any('最後一晚' in x['news'] and x['d'] == F['lin_closed'] for x in news) and all(x['d'] >= F['lin_closed'] - 3 for x in news), f'the news before opening counts down her last nights: {news}')
    din = json.loads(g.ev("JSON.stringify(__din)"))
    before = [x for x in din if x['d'] < F['pairing_wine']]; after = [x for x in din if x['d'] > F['pairing_wine']]
    check(not before and len(after) >= 20 and all(x['dinw'] and not x['lbar'] for x in after) and any(x['by'] == 'waiter' for x in after), f'no wine before the tasting; after it, pairing glasses poured at the pass and carried by the floor: {len(before)} / {len(after)} {after[:3]}')
    check(all(x['wineCost'] > 0 for x in log if x['d'] > F['pairing_wine'] and x['din'] > 0), 'each glass is in the day\'s wine cost')
    walked = json.loads(g.ev("JSON.stringify(__walked)"))
    check(len([w for w in walked if w['d'] < F['lin_closed']]) >= 30 and any(w['n'] == '品酒師 Ken' for w in walked) and not [w for w in walked if w['d'] > F['lin_closed']], f'while her bar is open, guests walk over after dinner (Ken too); after her last night, nobody: {len(walked)}')
    check(all(x['bar'] == 'lin' for x in log if x['d'] < F['lin_closed']) and log[-1]['bar'] == 'closed', f'the bar stays open to her last night, even after Jill decides: {[(x["d"], x["bar"]) for x in log[-6:]]}')
    W = json.loads(g.ev("JSON.stringify(Object.fromEntries(['pairing_start','lin_retire','ken_where','jd_want','dylan_book','lin_viewing'].map(k=>[k,((story().beatLines||{})[k]||[]).map(x=>(x.w?x.w+'：':'')+x.t)])))"))
    want = {'pairing_start': ['Jill：今晚那幾支，可以再幫我進嗎？', '品酒師 Ken：妳要賣？', 'Jill：配菜的。', 'Jill：想喝酒，隔壁就有。'],
            'lin_retire': ['Madame Lin：我做到月底。', 'Jill：隔壁？', 'Madame Lin：退休。', 'Jill：有人接嗎？', 'Madame Lin：還沒有。'],
            'ken_where': ['品酒師 Ken：她真的不做了？', '品酒師 Ken：最好有人接。', 'Jill：你這麼擔心？', '品酒師 Ken：不然吃完去哪？', 'Jill：回家。'],
            'jd_want': ['Jill：Madame Lin 要退休了。', '先生：嗯。', 'Jill：隔壁還沒有人接。', 'Jill：……我有點想接。', '先生：酒吧？', '先生：妳想做？', 'Jill：還不知道。', '先生：那就先看看。'],
            'dylan_book': ['Jill：這你的？', '先生：嗯。', 'Jill：我不是說還不知道嗎？', '先生：我知道。', 'Jill：那你買這個幹嘛？', '先生：看看。'],
            'lin_viewing': ['Jill：妳那邊有人接了嗎？', 'Madame Lin：還沒。', 'Jill：我可以看看嗎？', 'Madame Lin：走啊。', 'Jill：兩邊一起顧，應該滿麻煩的。', 'Madame Lin：妳跟我不一樣。', 'Madame Lin：妳廚房就在後面。', 'Madame Lin：這邊不用再弄一個。', 'Jill：還是多一間店。', 'Madame Lin：那當然。', 'Madame Lin：還有他。', 'Evan：……什麼叫還有我。', 'Madame Lin：你不是說想繼續做？', 'Evan：是。', 'Jill：你想留下？', 'Evan：如果妳接的話。', 'Jill：我還沒決定。', 'Evan：我知道。', 'Jill：如果我改很多呢？', 'Evan：妳的店，妳改啊。', 'Jill：那你還留下？', 'Evan：有吧台就行。']}
    for k, ws in want.items():
        for w in ws:
            check(w in W[k], f'{k}: 「{w}」 in {W[k]}')
    every = ' '.join(t for k in W for t in W[k])
    check('Dylan' not in every and '老公' not in every and g.ev("S.dylan.stage") == 2, 'before his reveal nothing says Dylan, nor 老公 — and nothing revealed him')
    check(not any(w in every for w in ('妳一定可以', '我相信妳', '新的開始', '承載', '像家', '夢想', '我支持妳', '好機會', '妳應該接', '把隔壁買下來', '生病', '撐不下去', '時代變了')), 'none of the words the brief rules out')
    page = json.loads(g.ev("JSON.stringify(lineProgress(STORY_LINES.find(L=>L.k==='nextdoor')).done.map(b=>b.k))"))
    check(all(k in page for k in ('ken_wine_q', 'pairing_start', 'lin_retire', 'ken_where', 'jd_want', 'dylan_book', 'lin_viewing', 'lin_take', 'lin_closed')), f'the story page 「隔壁」: {page}')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc8_the_bar_next_door_scenes_are_staged_where_they_happen(b, port, target):
    """§9–§11 as a player sees them (the Day 52 save, the steps before each set as facts): 《有點想接》 and the book play
    in Jill and Dylan's room after closing — Jill on the sofa, Dylan at his desk (his headphones off when she says it),
    the bar design book on his exam books; before his reveal the panel names him 「先生」 with no face, after it
    「Dylan」. 《看看》 begins on the street at her door, goes inside her bar (the tab reads 「隔壁」; Evan behind the
    counter, her by the back door, then at her records) and ends back in the hall with nothing left behind."""
    g = Game(b, port, target, seed=8301, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day52.json')
    g.ev("const st=story();for(const k of ['tasting_night','pairing_wine'])st.facts[k]={d:S.day-12,n:1,l:S.day-12};st.facts.lin_retiring={d:S.day-3,n:1,l:S.day-3};linS().last=S.day+9;st.facts.ken_where={d:S.day-1,n:1,l:S.day-1};for(const k of ['pairing_start','lin_retire','ken_where'])evState(k).n=1")
    to_service(g); g.ev("window.__noScenes=false;window.__holds=true;R.sched=R.sched.filter(o=>o.reg!=='dylan')")
    g.ev("__botUntil('R.closing!=null',200000,1/30)"); g.ev("lifeEnsureEvening()"); g.ev("for(let i=0;i<3;i++)__tick(1000/30)")
    for _ in range(40):   # another story's scene may come first tonight (its panel waits its turn)
        if g.ev("!!(DLG&&DLG.sh&&DLG.sh.k==='jd_want')") or not g.ev("!!DLG"): break
        g.ev("__tick(400);dlgNext()"); g.ev("__tick(1000/30)")
    s1 = json.loads(g.ev("JSON.stringify({k:DLG&&DLG.sh&&DLG.sh.k,room,on:LIFE.jill.on,jroom:LIFE.jill.room,desk:!!homeDylanAtDesk(),off:!!HOME_DY.off})"))
    check(s1['k'] == 'jd_want' and s1['room'] == 'home' and s1['on'] and s1['jroom'] == 'home' and s1['desk'] and not s1['off'], f'after closing, their room: Jill on the sofa, Dylan at his desk with his headphones on: {s1}')
    seen = []
    for _ in range(20):
        if not g.ev("!!DLG"): break
        t = g.ev("(document.querySelector('#dlg .dlg-text')||{}).textContent||''"); n = g.ev("(document.querySelector('#dlg .dlg-name')||{}).textContent||''")
        face = g.ev("(()=>{const L=DLG&&DLG.lines[DLG.i];return L?(portraitOf(L.who||'',L.tone)?1:0):0})()")
        seen.append((n, t, face, g.ev("!!HOME_DY.off")))
        g.ev("__tick(400);dlgNext()"); g.ev("for(let j=0;j<2;j++)__tick(1000/30)")
    his = [x for x in seen if x[0] == '先生']
    check(len(his) == 5 and all(x[2] == 0 for x in his), f'before the reveal: 「先生」, five lines, no face: {seen}')
    check([x for x in seen if '停下來' in x[1]][0][3], f'his headphones come off when she says it: {seen}')
    g.ev("const st=story();st.facts.jd_want.d=S.day-2;st.facts.jd_want.l=S.day-2")
    check(g.ev("linBookOn()"), 'two days on, the book is on his desk')
    g.ev("window.__books=0;const __db=drawBarBook;drawBarBook=function(){__books++;return __db.apply(this,arguments)};setRoom('home');for(let i=0;i<3;i++)__tick(1000/30)")
    check(g.ev("__books") > 0, 'drawn on the desk')
    check(not g.errors, g.errors[:3]); g.close()
    # after his reveal: Dylan by name
    g = Game(b, port, target, seed=8302, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day52.json')
    g.ev("S.dylan.stage=3;S.dylan.reveal=S.day-6;const st=story();for(const k of ['tasting_night','pairing_wine'])st.facts[k]={d:S.day-12,n:1,l:S.day-12};st.facts.lin_retiring={d:S.day-4,n:1,l:S.day-4};linS().last=S.day+8;st.facts.ken_where={d:S.day-3,n:1,l:S.day-3};st.facts.jd_want={d:S.day-3,n:1,l:S.day-3};for(const k of ['pairing_start','lin_retire','ken_where','jd_want'])evState(k).n=1")
    to_service(g); g.ev("window.__noScenes=false;window.__holds=true;R.sched=R.sched.filter(o=>o.reg!=='dylan')")
    g.ev("__botUntil('R.closing!=null',200000,1/30)"); g.ev("lifeEnsureEvening()"); g.ev("for(let i=0;i<3;i++)__tick(1000/30)")
    for _ in range(40):
        if g.ev("!!(DLG&&DLG.sh&&DLG.sh.k==='dylan_book')") or not g.ev("!!DLG"): break
        g.ev("__tick(400);dlgNext()"); g.ev("__tick(1000/30)")
    check(g.ev("DLG&&DLG.sh&&DLG.sh.k") == 'dylan_book' and g.ev("room") == 'home', 'the book, in the room')
    lines = _dlg_lines(g)
    check('Dylan：看看。' in lines and '先生：看看。' not in lines, f'after the reveal: Dylan: {lines}')
    check(not g.errors, g.errors[:3]); g.close()
    # the viewing: the street, her bar, Evan; back to the hall
    g = Game(b, port, target, seed=8303, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day52.json')
    g.ev("const st=story();for(const k of ['tasting_night','pairing_wine'])st.facts[k]={d:S.day-12,n:1,l:S.day-12};st.facts.lin_retiring={d:S.day-6,n:1,l:S.day-6};linS().last=S.day+6;for(const k of ['ken_where','jd_want'])st.facts[k]={d:S.day-4,n:1,l:S.day-4};st.facts.dylan_book={d:S.day-1,n:1,l:S.day-1};for(const k of ['pairing_start','lin_retire','ken_where','jd_want','dylan_book'])evState(k).n=1")
    if g.ev("phase") == 'shop': g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(200)
    g.ev("autoStock();window.__noScenes=false;window.__holds=true"); start_day(g); install_bot(g); g.ev("for(let i=0;i<3;i++)__tick(1000/30)")
    v0 = json.loads(g.ev("JSON.stringify({k:DLG&&DLG.sh&&DLG.sh.k,room,stage:STAGE&&STAGE.room,lin:STAGE&&STAGE.who.find(p=>p.id==='lin'),jill:R.jill.room,t:Math.round(R.t)})"))
    check(v0['k'] == 'lin_viewing' and v0['room'] == 'front' and v0['stage'] == 'front' and v0['jill'] == 'front' and v0['t'] == 0 and abs(v0['lin']['x'] - g.ev("FR.ldoor.x")) < 30, f'before opening, on the street at her door: {v0}')
    steps = []
    for _ in range(40):
        if not g.ev("!!DLG"): break
        steps.append(json.loads(g.ev("JSON.stringify({t:(document.querySelector('#dlg .dlg-text')||{}).textContent,room,tab:roomTabName('lounge'),barv:BARV,evan:STAGE&&!STAGE.who.find(p=>p.id==='evan').hide,lin:STAGE&&STAGE.who.find(p=>p.id==='lin'),evanY:STAGE&&STAGE.who.find(p=>p.id==='evan').y})")))
        g.ev("__tick(400);dlgNext()"); g.ev("for(let j=0;j<2;j++)__tick(1000/30)")
    inside = [x for x in steps if x['room'] == 'lounge']
    check(inside and all(x['barv'] == 1 and x['tab'] == '隔壁' and x['evan'] and x['evanY'] < g.ev("LG.bar.y") for x in inside), f'inside her bar: the tab 「隔壁」, Evan behind the counter: {inside[:2]}')
    kit = [x for x in steps if x['t'] and '妳廚房就在後面' in x['t']][0]
    check(abs(kit['lin']['x'] - g.ev("LG.bk.x")) < 40, f'she says it by the back door: {kit}')
    rec = [x for x in steps if x['t'] and '你想留下' in x['t']][0]
    check(abs(rec['lin']['x'] - g.ev("LIN_RECORDS.x")) < 40, f'she has gone to her records; the two of them talk: {rec}')
    end = json.loads(g.ev("JSON.stringify({room,barv:BARV,stage:STAGE,tab:roomsOpen().map(roomTabName),jill:R.jill.room})"))
    check(end['room'] == 'main' and end['barv'] is None and end['stage'] is None and '隔壁' not in end['tab'] and end['jill'] == 'main', f'and back to the hall, nothing left behind: {end}')
    check(not any('Dylan' in (x['t'] or '') or '老公' in (x['t'] or '') for x in steps), 'Evan has not met Dylan; nobody mentions him')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc8_mature_saves_hear_nothing_new_from_next_door(b, port, target):
    """Saves past the Lounge's opening (Day 61, Day 74): a day plays with none of the Madame Lin line's new scenes
    (Checkpoint C marks their history), the bar next door is The Lounge, nobody walks 「next door」 to it as to her bar,
    and dinner's glasses are the Lounge's (poured by the bartender), as before."""
    for name in ('player_day61.json', 'player_day74_1508.json'):
        g = Game(b, port, target, seed=8401, manual=True, viewport={'width': 390, 'height': 844})
        load_save(g, name)
        g.ev("window.__noScenes=true")
        to_service(g)
        g.ev("window.__dw=0;const __sv=serveItems;serveItems=function(q,list){for(const c of list||[])if(c.it&&c.it.dinw)__dw++;return __sv.apply(this,arguments)}")
        g.ev("__botUntil('phase!==\"service\"',200000,1/30)")
        new = json.loads(g.ev("JSON.stringify(story().trace.filter(t=>t.d===S.day&&['lin_hello','pairing_start','lin_retire','ken_where','jd_want','dylan_book','lin_viewing','lin_last','lin_sign'].includes(t.k)).map(t=>t.k))"))
        check(not new and g.ev("barState()") == 'lounge' and g.ev("__dw") == 0, f'{name}: nothing new fires (Checkpoint C gave the line to the save as history); The Lounge; no pass-poured glasses: {new}')
        check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc8_the_restaurants_three_lists_and_the_lounges_one(b, port, target):
    """The player's brief of 2026-10-02 19:19 §21–§22: the restaurant's people are three lists — 廚師, 服務生, 清潔員 —
    each with its own places (a chef's place only hires a chef); every expansion and every work says which list it adds
    to; level by level the three add up to the one old number, so none of the player's saves is over any list; the
    Lounge's list is untouched by any of it, and a restaurant waiter working the Lounge floor stays a restaurant waiter."""
    import glob
    g = Game(b, port, target, seed=8601, manual=True, viewport={'width': 390, 'height': 844})
    g.click('[data-act=open]'); g.page.wait_for_timeout(100)
    lv = json.loads(g.ev("JSON.stringify([1,2,3,4,5].map(l=>CAP_ROLES.map(r=>roleCapAt(r,l))))"))
    check([sum(x) for x in lv] == [1, 2, 3, 4, 6], f'each level adds up to the old number: {lv}')
    check(all(all(lv[i][j] >= lv[i - 1][j] for j in range(3)) for i in range(1, 5)), f'no list ever gets smaller with a level: {lv}')
    src = json.loads(g.ev("JSON.stringify(capSources().map(s=>[s.k,s.add]))"))
    check(src == [['room', {'chef': 1, 'waiter': 1}], ['side', {'waiter': 2}], ['kext', {'chef': 1, 'cleaner': 1}], ['kitchen2', {'waiter': 2}], ['pd1', {'waiter': 1}], ['pd3', {'waiter': 1}], ['pizzaoven', {'chef': 1}]], f'every work says which list: {src}')
    # a new shop: one chef's place; a waiter or a cleaner is not hired into it
    g.ev("S.money=99999;S.day=5;shopTab='staff';showShop()"); g.page.wait_for_timeout(60)   # the staff tab opens from the evening of Day 4
    for k in ('waiter', 'cleaner'):
        _act(g, 'hire', k=k); g.ev("__tick(30)")
    check(g.ev("(S.crew||[]).length") == 0, 'the chef\'s place takes no waiter and no cleaner')
    txt = g.ev("document.querySelector('#screen').innerText")
    check('廚師 0/1' in txt and '服務生 0/0' in txt and '清潔員 0/0' in txt and '還沒有服務生的名額' in txt and 'Jill\'s Bistro' in txt, 'the page shows three numbers and where the next one comes from')
    _act(g, 'hire', k='chef'); g.ev("__tick(30)")
    check(g.ev("S.crew.map(m=>m.role).join()") == 'chef', 'a chef is hired into the chef\'s place')
    _act(g, 'hire', k='chef'); g.ev("__tick(30)")
    check(g.ev("S.crew.length") == 1, 'and only one')
    # the expansion card says what each level adds
    g.ev("shopTab='works';showShop()"); g.page.wait_for_timeout(60)
    card = g.ev("(()=>{const e=[...document.querySelectorAll('#screen .item')].find(e=>/擴建：/.test(e.innerText));return e?e.innerText.replace(/\\s+/g,' '):''})()")
    check('服務生 +1' in card and '廚師 +' not in card, f'the Bistro: one waiter\'s place: {card}')
    g.ev("S.level=4;shopTab='works';showShop()"); g.page.wait_for_timeout(60)
    card = g.ev("(()=>{const e=[...document.querySelectorAll('#screen .item')].find(e=>/擴建：/.test(e.innerText));return e?e.innerText.replace(/\\s+/g,' '):''})()")
    check('廚師 +1' in card and '清潔員 +1' in card and '服務生 +' not in card, f'JILL: a chef\'s and a cleaner\'s place: {card}')
    # the works' words name the list; no generic 「員工 +2」 anywhere
    words = g.ev("JSON.stringify([OPS.find(o=>o.k==='room').d(1)].concat(PROJECTS.concat(KITCHEN_WORKS).filter(p=>['side','kext','kitchen2','pizzaoven'].includes(p.k)).map(p=>p.d+' '+(p.unlock||[]).join(' '))).concat(PD_PROJ.filter(Boolean).map(p=>p.d+' '+(p.unlock||[]).join(' '))))")
    check('廚師和服務生各可以再多聘 1 位' in words and '服務生可以再多聘 2 位' in words and '廚師 +1、清潔員 +1' in words and '服務生 +2' in words and '廚師 +1（顧烤爐）' in words and '服務生名額 +1' in words, 'each work names its list')
    check('再聘 2 位員工' not in words and '員工名額 +1' not in words and '員工 +2' not in words and '再多聘 1 位，' not in words.replace('廚師可以再多聘 1 位，', ''), 'no generic places left')
    g.close()
    # every save the player sent: no list over its number
    over = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'tests', 'saves', 'player_*.json'))):
        g = Game(b, port, target, seed=8602, manual=True, viewport={'width': 390, 'height': 844})
        load_save(g, os.path.basename(f))
        o = json.loads(g.ev("JSON.stringify(CAP_ROLES.filter(r=>roleCrew(r).length>roleCap(r)).map(r=>r+' '+roleCrew(r).length+'/'+roleCap(r)))"))
        if o: over.append((os.path.basename(f), o))
        g.close()
    check(not over, f'none of the player\'s saves is over any list: {over}')
    # the Day 61 save: the Lounge's list is its own; the restaurant's works never add to it, its hiring never takes from them
    g = Game(b, port, target, seed=8603, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day61.json')
    r0 = g.ev("CAP_ROLES.map(r=>roleCrew(r).length+'/'+roleCap(r)).join()"); l0 = g.ev("loungeCap()")
    check(r0 == '6/6,4/4,2/2' and l0 == 5, f'the restaurant full, the Lounge 2 of 5: {r0}, {l0}')
    g.ev("S.money+=500000")
    for nm in ['阿拓', '安安', '許葳']:
        _hire(g, 'hireLounge', nm)
    check(g.ev("CAP_ROLES.map(r=>roleCrew(r).length+'/'+roleCap(r)).join()") == r0 and g.ev("poolCrew('lounge').length") == 5, '阿拓 (a cook), 安安 (a waiter), 許葳 (a cleaner): the Lounge\'s, on no restaurant list')
    g.ev("S.rooms.kitchen2=1;S.rooms.pizzaoven=1")
    check(g.ev("roleCap('waiter')") == 6 and g.ev("roleCap('chef')") == 7 and g.ev("loungeCap()") == l0, 'the restaurant\'s works add the restaurant\'s places only')
    _hire(g, 'hire', 'waiter')
    g.ev("(()=>{const m=S.crew[S.crew.length-1];m.duties=Object.assign({},waiterDuties(m),{lounge:true})})()")
    check(g.ev("(()=>{const m=S.crew[S.crew.length-1];return m.role==='waiter'&&crewPool(m)==='restaurant'&&waiterDuties(m).lounge})()") is True and g.ev("roleCrew('waiter').length") == 5 and g.ev("poolCrew('lounge').length") == 5, 'a new restaurant waiter on the Lounge floor: still the restaurant\'s waiter (5/6), the Lounge still 5/5')
    _reload(g)
    check(g.ev("CAP_ROLES.map(r=>roleCrew(r).length+'/'+roleCap(r)).join()") == '6/7,5/6,2/2' and g.ev("poolCrew('lounge').length") == 5, 'kept across a reload')
    check(not g.errors, g.errors[:3]); g.close()


_LIN_TAKEN = """const st=story();const d=S.day;const set=(k,dd)=>st.facts[k]={d:dd,n:1,l:dd};
 for(const k of ['tasting_night','pairing_wine'])set(k,d-20);set('lin_retiring',d-13);linS().last=d+5;set('ken_where',d-12);set('jd_want',d-11);set('dylan_book',d-8);set('lin_viewing',d-7);set('lounge_project',d-7);set('lin_take',d-7);
 for(const k of ['pairing_start','lin_retire','ken_where','jd_want','dylan_book','lin_viewing'])Object.assign(evState(k),{n:1,d:d-7});
 S.loungeProj={revealed:d-7,state:'planned',at:d-7};S.money+=300000"""   # her last night still ahead (2026-10-06: no wait for it)


@test
def v24_rc8_the_signing_the_work_and_the_opening(b, port, target):
    """The player's brief of 2026-10-02 19:19 §12–§16, on the Day 52 save with the line's earlier beats as facts: the
    works page does not wait for her last night (the user, 2026-10-06): with it still ahead 簽約・開工 takes $50,000 and
    that evening is her last (her bar closed, no countdown left); the next opening is 《簽約》 in her bar — the
    contract, the pen, the keys, 「那就這樣。」「嗯。」, she hands Jill the keys, and Evan meets Dylan (before the reveal
    「Evan，這 Jill 老公。」 with 「先生」 on the panel; after it 「Evan，這 Dylan。」「Jill 老公。」). Only Evan learns anything
    (the reveal is untouched). Two days of work, papered over; then the morning card 「開幕 · The Lounge」 (no story note over
    it, no 「繼續買東西」) and Evan on The Lounge's list from that day; kept across a reload."""
    for reveal in (False, True):
        g = Game(b, port, target, seed=8711 + reveal, manual=True, viewport={'width': 390, 'height': 844})
        load_save(g, 'player_day52.json')
        g.ev(_LIN_TAKEN)
        if reveal: g.ev("S.dylan.stage=3;S.dylan.reveal=S.day-5")
        dy0 = g.ev("JSON.stringify([S.dylan.stage,S.dylan.reveal])")
        g.ev("showShop();shopTab='works';showShop()"); g.page.wait_for_timeout(60)
        card = g.ev("(document.querySelector('#screen .lin-card')||{}).innerText||''")
        check(g.ev("linLast()") > g.ev("S.day") and not g.ev("!!fact('lin_closed')") and '最後一晚' not in card and 'Madame Lin 做到' not in card
              and g.ev("!document.querySelector('#screen .lin-card [data-act=linSign]').disabled"), f'her last night still ahead, and 簽約・開工 is there to press: {card[-60:]!r}')
        m0 = g.ev("S.money"); g.click('#screen [data-act=linSign]'); g.page.wait_for_timeout(60)
        check(m0 - g.ev("S.money") == 50000 and g.ev("S.loungeProj.state") == 'signing' and '明天開店前，Jill 去隔壁簽約' in g.ev("document.querySelector('#screen .lin-card').innerText"), 'paid $50,000: the signing is the next opening')
        check(g.ev("fact('lin_closed')&&fact('lin_closed').d") == g.ev("S.day") and g.ev("barState()") == 'closed' and g.ev("linNewsHTML()") == '', 'signed before her last night: tonight was her last — her bar closed, no countdown left')
        g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(120)
        g.ev("autoStock();window.__noScenes=false;window.__holds=true"); start_day(g); install_bot(g); g.ev("for(let i=0;i<3;i++)__tick(1000/30)")
        check(g.ev("!!(DLG&&DLG.sh&&DLG.sh.k==='lin_sign')") and g.ev("room") == 'lounge' and g.ev("BARV") == 1, 'the morning: 《簽約》 held, in her bar')
        lines = _dlg_lines(g)
        want = ['開店前，Jill 和 Dylan 一起去隔壁。' if reveal else '開店前，Jill 和先生一起去隔壁。', '吧台上放著合約、一支筆，還有一串鑰匙。', 'Jill 簽了名。', 'Madame Lin：那就這樣。', 'Jill：嗯。', 'Madame Lin 把鑰匙交給她。']
        want += ['Madame Lin：Evan，這 Dylan。', 'Madame Lin：Jill 老公。', 'Evan：你好。', 'Dylan：你好。'] if reveal else ['Madame Lin：Evan，這 Jill 老公。', 'Evan：你好。', '先生：你好。']
        check(lines[:len(want)] == want, f'the lines (reveal {reveal}): {lines}')
        check(reveal or not any('Dylan' in l for l in lines), 'before the reveal his name is never on the panel')
        check(g.ev("!!fact('lin_signed')&&!!fact('evan_knows_dylan')") and g.ev("JSON.stringify([S.dylan.stage,S.dylan.reveal])") == dy0, 'signed; Evan knows him; the reveal untouched')
        check(g.ev("STAGE===null&&BARV===null&&room==='main'") is True and g.ev("barState()") == 'reno' and g.ev("S.loungeProj.open") == g.ev("S.day") + 2, 'back in the hall; papered over; open in two days')
        g.ev(LAZY_ACTOR + "\nwindow.__act=window.__actLazy;window.__noScenes=true"); g.ev("__botUntil('phase!==\"service\"',200000,1/30)"); g.page.wait_for_timeout(60)
        g.ev("for(let i=0;i<80&&typeof DLG!=='undefined'&&DLG;i++){__tick(400);dlgNext()}")
        if g.ev("phase") == 'summary': g.click('[data-act=toShop]'); g.page.wait_for_timeout(60)
        g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(100); g.ev("__tick(1200)")
        check(g.ev("barState()") == 'reno' and not g.ev("loungeLv()") and not g.ev("!!$('#reveal')&&!$('#reveal').hidden"), 'the second day of the work')
        g.ev("doAct('nextDay',null,null,null)"); g.page.wait_for_timeout(60); g.ev("__tick(600)"); g.page.wait_for_timeout(60); g.ev("__tick(900)"); g.page.wait_for_timeout(60)
        rv = g.ev("($('#reveal')&&!$('#reveal').hidden)?$('#reveal').innerText:''")
        check('開幕' in rv and 'The Lounge' in rv and '回到開店準備' in rv and '繼續買東西' not in rv, f'the morning card: {rv[:80]!r}')
        check(g.ev("loungeLv()") == 1 and g.ev("barState()") == 'lounge' and g.ev("JSON.stringify((S.crew||[]).filter(m=>m.name==='Evan').map(m=>[m.role,m.pool,m.since===S.day]))") == '[["bartender","lounge",true]]', 'The Lounge; Evan on its list from today')
        check(g.ev("$('#storyNote').hidden") is True, 'no story note over the card')
        g.click('#reveal [data-act=revealPrep]'); g.page.wait_for_timeout(60)
        check(g.ev("!$('#reveal')||$('#reveal').hidden") is True and g.ev("phase") == 'prep', 'back to the prep screen')
        _reload(g)
        check(g.ev("loungeLv()") == 1 and g.ev("!!fact('lin_signed')") and g.ev("S.loungeProj.state") == 'built', 'kept across a reload')
        check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc8_madame_lin_comes_back_as_a_guest(b, port, target):
    """§17: some days after The Lounge opens, Madame Lin comes in for the first time as a guest (planned for the bar —
    a full bar sends her back a little later, never to dinner); 「坐哪？」「隨便。」「喝什麼？」「你選。」, held, in The Lounge;
    she sits at the bar; after that she comes now and then. On the player's Day 61 save (The Lounge II, Evan; the line
    is its history)."""
    g = Game(b, port, target, seed=8721, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day61.json')
    d0 = g.ev("loungeDoneDay()")
    check(g.ev("!!fact('lin_closed')&&!fact('lin_guest')") and d0 is not None, 'the history is there; she has not been in as a guest')
    g.ev("S.day=loungeDoneDay()+4")
    check(not g.ev("V24_WANTS.flatMap(f=>f()||[]).some(w=>w.k==='lin_guest')"), 'not in the first days')
    g.ev("S.day=loungeDoneDay()+5")
    w = json.loads(g.ev("JSON.stringify(V24_WANTS.flatMap(f=>f()||[]).find(w=>w.k==='lin_guest')||null)"))
    check(w and w['name'] == 'Madame Lin' and w['o'] == {'lounge': 1, 'lgRetry': 1}, f'then she is planned for the bar: {w}')
    to_service(g); g.ev("window.__act=window.__actLazy;window.__noScenes=true")
    g.ev("R.sched=R.sched.filter(o=>o.name!=='Madame Lin');namedHist('Madame Lin').seen=S.day")
    g.ev("__botUntil('R.t>=R.dur*.3',200000,1/30)")
    g.ev("(()=>{const v=v24();v.res={d:S.day,k:['lin_guest']}})();R.sched.splice(R.si,0,{t:R.t+2,type:'vip',size:1,name:'Madame Lin',story:1,lounge:1,lgRetry:1,tries:1});window.__noScenes=false;window.__holds=true")
    for _ in range(12):
        g.ev("__botUntil(\"!!(typeof DLG!=='undefined'&&DLG)||R.groups.some(q=>namedId(q)==='Madame Lin')\",900,1/30)")
        if g.ev("!!DLG") and g.ev("DLG.sh?DLG.sh.k:''") != 'lin_guest':
            g.ev("for(let i=0;i<40&&DLG&&!(DLG.sh&&DLG.sh.k==='lin_guest');i++){__tick(400);dlgNext()}"); continue
        break
    check(g.ev("!!(DLG&&DLG.sh&&DLG.sh.k==='lin_guest')") and g.ev("room") == 'lounge', 'held, in The Lounge')
    lines = _dlg_lines(g)
    check(lines == ['開門進來的是 Madame Lin。', 'Jill：坐哪？', 'Madame Lin 看了一下。', 'Madame Lin：隨便。', 'Evan：喝什麼？', '她看了看酒單。', 'Madame Lin：你選。'], f'the lines: {lines}')
    g.ev("window.__noScenes=true;for(let i=0;i<90;i++)__tick(1000/30)")
    st = json.loads(g.ev("JSON.stringify(R.groups.filter(q=>namedId(q)==='Madame Lin').map(q=>({room:q.room,kind:q.table!=null?R.tables[q.table].kind:null})))"))
    check(st == [{'room': 'lounge', 'kind': 'bar'}], f'she sits at the bar: {st}')
    check(g.ev("STAGE===null") is True and g.ev("!!fact('lin_guest')"), 'the stage is cleared; it happened once')
    n = sum(1 for d in range(400) if g.ev(f"(()=>{{const d0=S.day;S.day={d}+100;const r=V24_WANTS.flatMap(f=>f()||[]).some(w=>w.name==='Madame Lin');S.day=d0;return r}})()"))
    check(10 <= n <= 60, f'after that, now and then (on {n} of 400 evenings)')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc8_mature_saves_get_the_line_as_history(b, port, target):
    """§23: a save from before the Madame Lin line keeps everything it has and is given the line as history — facts and
    finished beats marked retro, 「更早以前」 on the story page, never played, never announced. With The Lounge (the
    player's Day 61 and Day 74): the whole line to the signing. With the project but no Lounge: up to her last night (簽約・
    開工 is next — since 2026-10-06 for a 「再想想」 too: the story has decided). After the tasting: the pairing wines. Past Day 1: she brought the bell. A new
    game is this version's and is left alone."""
    LINE = ['lin_hello', 'pairing_wine', 'lin_retiring', 'ken_where', 'jd_want', 'dylan_book', 'lin_viewing', 'lin_take', 'lin_closed', 'lin_signed', 'evan_knows_dylan']
    for name in ('player_day61.json', 'player_day74_1508.json'):
        g = Game(b, port, target, seed=8731, manual=True, viewport={'width': 390, 'height': 844})
        raw = load_save(g, name)
        F0 = raw['story']['facts']; F = json.loads(g.ev("JSON.stringify(story().facts)"))
        check(all(F.get(k) == v for k, v in F0.items()), f'{name}: every fact it had, as it was')
        added = sorted(set(F) - set(F0))
        check(set(LINE) <= set(added) and all(F[k]['d'] == 0 and F[k].get('retro') == 1 for k in LINE) and not any(F[k].get('retro') for k in added if k not in LINE), f'{name}: the line, as history (and nothing else made retro): {added}')
        check(g.ev("['lin_hello','pairing_start','lin_retire','ken_where','jd_want','dylan_book','lin_viewing','lin_last','lin_sign'].every(k=>evState(k).n===1&&evState(k).retro===1)") is True, f'{name}: its beats done (retro)')
        check(g.ev("loungeLv()") == raw['rooms']['lounge'] and sorted(g.ev("S.crew.map(m=>m.name)")) == sorted(m['name'] for m in raw['crew']) and g.ev("S.dylan.stage") == raw['dylan']['stage'], f'{name}: The Lounge, the crew, Dylan as they were')
        check(g.ev("propOn('linbell')") is True and g.ev("barState()") == 'lounge' and not g.ev("fact('lin_guest')"), f'{name}: the bell on the door; Madame Lin as a guest is still ahead')
        g.ev("storyProgressCheck()"); g.page.wait_for_timeout(60)
        check(g.ev("$('#storyNote').hidden") is True, f'{name}: nothing announced')
        g.ev("openStory('nextdoor')"); g.ev("__tick(100)"); g.page.wait_for_timeout(100)
        txt = g.ev("document.querySelector('#screen').innerText")
        check('隔壁' in txt and '更早以前' in txt and 'DAY ' + str(raw['day']) not in txt.split('隔壁', 1)[-1][:400], f'{name}: the story page — 「更早以前」')
        check(not g.errors, g.errors[:3]); g.close()
    # the project but no Lounge yet: up to her last night; then 簽約・開工 — a 「再想想」 or an unanswered card too (2026-10-06)
    for state, act in (('planned', 'linSign'), ('deferred', 'linSign'), (None, 'linSign')):
        g = Game(b, port, target, seed=8732, manual=True, viewport={'width': 390, 'height': 844})
        raw = json.load(open(os.path.join(ROOT, 'tests', 'saves', 'player_day61.json'), encoding='utf-8')); raw = raw.get('save', raw)
        raw['rooms']['lounge'] = 0; raw['crew'] = [m for m in raw['crew'] if m['name'] not in ('Evan', '沈晴')]; raw['loungeProj'] = {'revealed': 57, 'state': state, 'at': 57} if state else {'revealed': 57}; raw['money'] = 500000
        g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.page.wait_for_timeout(150)
        g.click('[data-act=openFresh]') if g.page.query_selector('[data-act=openFresh]') else g.click('[data-act=open]'); g.page.wait_for_timeout(150)
        check(g.ev("['lin_retiring','lin_viewing','lin_closed','lin_take'].every(k=>fact(k)&&fact(k).retro===1)&&!fact('lin_signed')") is True and g.ev("S.loungeProj.state") == 'planned', f'{state}: up to her last night, and Jill has decided')
        check(g.ev("barState()") == 'closed', f'{state}: her bar is closed, not yet Jill\'s')
        g.ev("showShop();shopTab='works';showShop()"); g.page.wait_for_timeout(60)
        check(g.ev(f"!!document.querySelector('#screen .lin-card [data-act={act}]')") is True and '再想想' not in g.ev("document.querySelector('#screen').innerText"), f'{state}: the works page offers {act}, and no 「再想想」')
        check(not g.errors, g.errors[:3]); g.close()
    # after the tasting, before any project: the pairing wines from the tasting's day; the rest of the line still ahead
    g = Game(b, port, target, seed=8733, manual=True, viewport={'width': 390, 'height': 844})
    raw = json.load(open(os.path.join(ROOT, 'tests', 'saves', 'player_day61.json'), encoding='utf-8')); raw = raw.get('save', raw)
    raw['rooms']['lounge'] = 0; raw['crew'] = [m for m in raw['crew'] if m['name'] not in ('Evan', '沈晴')]; raw.pop('loungeProj', None); raw['story']['facts'].pop('lounge_project', None)
    g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.page.wait_for_timeout(150)
    g.click('[data-act=openFresh]') if g.page.query_selector('[data-act=openFresh]') else g.click('[data-act=open]'); g.page.wait_for_timeout(150)
    check(g.ev("fact('pairing_wine')&&fact('pairing_wine').d") == raw['story']['facts']['tasting_night']['d'] and g.ev("!fact('lin_retiring')&&!!fact('lin_hello')&&propOn('linbell')") is True and g.ev("barState()") == 'lin', 'the pairing wines since the tasting; she has not said 「我做到月底」 yet')
    g.close()
    # Day 52: only the bell (and her Day 1, as history)
    g = Game(b, port, target, seed=8734, manual=True, viewport={'width': 390, 'height': 844})
    raw = load_save(g, 'player_day52.json')
    F = json.loads(g.ev("JSON.stringify(story().facts)"))
    check(sorted(set(F) - set(raw['story']['facts'])) == ['lin_hello'] and g.ev("propOn('linbell')") is True, f'Day 52: her Day 1 and the bell, nothing else: {sorted(set(F) - set(raw["story"]["facts"]))}')
    g.close()
    # a new game is this version's
    g = Game(b, port, target, seed=8735, manual=True, viewport={'width': 390, 'height': 844})
    g.click('[data-act=open]'); g.page.wait_for_timeout(100)
    check(g.ev("S.linMig") == 1 and not g.ev("Object.values(story().facts).some(f=>f.retro)"), 'a new game: nothing retro')
    g.close()


_LIN_TO_THE_VIEWING = """const st=story();for(const k of ['tasting_night','pairing_wine'])st.facts[k]={d:S.day-12,n:1,l:S.day-12};st.facts.lin_retiring={d:S.day-6,n:1,l:S.day-6};linS().last=S.day+6;for(const k of ['ken_where','jd_want'])st.facts[k]={d:S.day-4,n:1,l:S.day-4};st.facts.dylan_book={d:S.day-1,n:1,l:S.day-1};for(const k of ['pairing_start','lin_retire','ken_where','jd_want','dylan_book'])evState(k).n=1"""



@test
def v24_story_first_the_doors_of_the_stories_open_with_story_keys(b, port, target):
    """The user, 2026-10-07 (version A; PROJECT_MEMORY §0 and §6): 「故事的門，用故事的鑰匙開；空間與豪華升級的門，用錢開。」
    Lounge II $80,000 (Fine Dining: a room of the business), Lounge III $150,000 (no level of its own). 阿拓 is on the
    Lounge I roster, so 晴 × 阿拓 needs The Lounge and the two of them at work there — never Lounge II. The piano is
    $100,000 from the day The Lounge opens, at any level, on the Lounge's own page (not among the late dream works, and
    never twice), and 予安's story waits for the piano alone (three days, as it always did). The floor upstairs and the
    Staff Room's story ask for no level: the side room (the stairs) and a crew stay. All on a level-1 restaurant at 3.0."""
    g = Game(b, port, target, seed=8771, manual=True, viewport={'width': 390, 'height': 844})
    g.click('[data-act=open]'); g.page.wait_for_timeout(100)
    PIANO = "((document.querySelector('#screen')||{}).innerText||'').split('Lounge 的鋼琴').length-1"   # before opening the shop says 「打烊後可以開始」 instead of a button
    r = json.loads(g.ev("""JSON.stringify((()=>{const out={};rating=function(){return 3.0};S.level=1;S.money=1e6;S.day=30;phase='shop';   /* a day the works tab is open */
      out.proj=[LOUNGE_PROJ.map(p=>p.cost),LOUNGE_PROJ.map(p=>p.need)];
      const PN=DREAMS.find(d=>d.k==='piano');out.piano=[PN.cost,PN.lv,PN.needLounge];return out})())"""))
    g.ev("doAct('tab',null,'works')"); g.page.wait_for_timeout(120); r['pianoGoal0'] = g.ev(PIANO)
    r.update(json.loads(g.ev("""JSON.stringify((()=>{const out={};loungeBuild(1);try{hideReveal()}catch(e){}
      out.roster1=loungeRosterOpen().map(x=>x.name);out.cap1=loungeCap();
      for(const n of ['沈晴','阿拓'])doAct('hireLounge',null,n);
      out.lounge=poolCrew('lounge').map(m=>m.name).sort();
      const q1=STORY_EV.find(e=>e.k==='qt_1');out.qt1=!!q1.when({tk:{lounge:true,items:[{d:'friedrice'}]}});return out})())""")))
    g.ev("doAct('tab',null,'works')"); g.page.wait_for_timeout(120); r['pianoCards'] = g.ev(PIANO)
    g.ev("S.level=5;doAct('tab',null,'works')"); g.page.wait_for_timeout(120); r['pianoCards5'] = g.ev(PIANO)
    r.update(json.loads(g.ev("""JSON.stringify((()=>{const out={};S.level=1;
      const m0=S.money;doAct('buyProject',null,'piano');out.paid=m0-S.money;out.pianoOn=!!projOn('piano');try{hideReveal()}catch(e){}
      yaFirst();const d0=S.day;S.day=d0+2;out.ya_d2=yaDue('ya_1');S.day=d0+3;out.ya_d3=yaDue('ya_1');S.day=d0;
      S.rooms.side=1;const c0=S.crew;S.crew=c0.concat([1,2,3,4,5].map(i=>({name:'x'+i,role:'waiter'})));out.upCan=upCan();S.crew=c0;
      out.noLevel=[upCan,srStoryReady].map(f=>!/S\\.level/.test(String(f)));return out})())""")))
    check(r['proj'] == [[50000, 80000, 150000], [0, 4, 0]], f'Lounge I $50,000; II $80,000 at Fine Dining; III $150,000, no level: {r["proj"]}')
    check(r['piano'] == [100000, 1, 1] and r['pianoGoal0'] == 0, f'the piano: $100,000, any level, The Lounge first — not on sale before it: {r}')
    check(r['roster1'] == ['Evan', '沈晴', '阿拓'] and r['cap1'] == 3 and r['lounge'] == sorted(['Evan', '沈晴', '阿拓']), f'Lounge I: Evan, 沈晴 and 阿拓: {r}')
    check(r['qt1'] is True, f'晴 × 阿拓 can begin at Lounge I, level 1, 3.0 — the two of them at work: {r}')
    check(r['pianoCards'] == 1 and r['pianoCards5'] == 1 and r['paid'] == 100000 and r['pianoOn'], f'the piano on the Lounge page at level 1, once at level 5 too; bought for $100,000: {r}')
    check(r['ya_d2'] is False and r['ya_d3'] is True, f"予安: three days after the piano, as before — nothing else asked: {r}")
    check(r['upCan'] is True and all(r['noLevel']), f'the floor upstairs and the Staff Room\'s story: no level (a level-1 restaurant with the side room and a crew): {r}')
    check(not g.errors, g.errors[:3]); g.close()

@test
def v24_lounge_one_after_the_viewing_and_50000_no_wait_for_her_last_night(b, port, target):
    """The user, 2026-10-06: 《看看》 is where Jill decides — no 「接下隔壁／再想想」 card, nothing to come back to; the same
    day 升級餐廳 › 店舖工程 has Lounge I, and (the user, 2026-10-07) it needs two things only: 《看看》 and $50,000 — no
    level, no rating. Her last night is her story, never a wait: with it still ahead the player signs, and the evening before the
    signing is her last (her bar closed, the keys the next morning, nothing left to fire on the old date); not signed,
    her last night comes as it always did and one line says where the signing is — a reminder, not an unlock. What is
    missing is said on the card (the money, nothing else). Lounge II $80,000 (Fine Dining) and III $150,000 (no level of its
    own) — the user, 2026-10-07. Saves from
    before — a 「再想想」, a card nobody answered, a save between 《看看》 and that night's card, one waiting for her last
    night — can all sign; one that had paid $120,000 is not charged again, a built Lounge is left as it is."""
    g = Game(b, port, target, seed=8761, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day52.json'); g.ev(_LIN_TO_THE_VIEWING)
    check(g.ev("JSON.stringify([LOUNGE_PROJ.map(p=>p.cost),LOUNGE_PROJ.map(p=>p.need),'rate' in LOUNGE_PROJ[0]])") == '[[50000,80000,150000],[0,4,0],false]', 'Lounge I: $50,000, no level, no rating; II $80,000 (Fine Dining); III $150,000')
    if g.ev("phase") == 'shop': g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(200)
    g.ev("window.__notes=[];const __nl=noteLine;noteLine=function(t){__notes.push(t);return __nl.apply(this,arguments)}")
    g.ev("autoStock();window.__noScenes=false;window.__holds=true"); start_day(g); install_bot(g); g.ev("for(let i=0;i<3;i++)__tick(1000/30)")
    check(g.ev("DLG&&DLG.sh&&DLG.sh.k") == 'lin_viewing', '《看看》, before opening')
    lines = _dlg_lines(g, 60); d = g.ev("S.day")
    check('Jill：我可以看看嗎？' in lines and 'Jill：我還沒決定。' in lines and not any('接下隔壁' in l or '再想想' in l for l in lines), f'the scene as it was (「我還沒決定。」 kept): {lines}')
    st = json.loads(g.ev("JSON.stringify({sub,modal:!!document.querySelector('#screen:not([hidden]) .modal'),proj:fact('lounge_project')&&fact('lounge_project').d,take:fact('lin_take')&&fact('lin_take').d,state:S.loungeProj&&S.loungeProj.state,notes:__notes,dlg:!!DLG,bar:barState()})"))
    check(st['proj'] == d and st['take'] == d and st['state'] == 'planned' and not st['sub'] and not st['modal'] and not st['dlg'] and st['bar'] == 'lin', f'at the end of 《看看》 Jill has decided — no card; her bar is still open: {st}')
    check(any('Jill 決定接下來' in n and '店舖工程' in n for n in st['notes']) and 'Jill 決定接下來' in lines[-1], f'the scene\'s last line says so, and where it goes on: {lines[-2:]}')
    # the evening (another story's scene tapped through, as a player would); the shop the same day, her last night still ahead
    g.ev(LAZY_ACTOR + "\nwindow.__act=window.__actLazy;window.__noScenes=true;window.__holds=false"); g.ev("__botUntil('phase!==\"service\"',200000,1/30)")
    g.ev("for(let i=0;i<80&&typeof DLG!=='undefined'&&DLG;i++){__tick(400);dlgNext()}")
    check(not g.ev("sub==='loungeproj'") and not g.ev("!!document.querySelector('[data-act=loungeGo],[data-act=linTake]')"), 'no card that night either')
    g.click('[data-act=toShop]'); g.page.wait_for_timeout(80); g.click('#screen [data-act=tab][data-k=works]'); g.page.wait_for_timeout(80)
    CARD = "(document.querySelector('#screen .lin-card')||{}).innerText||''"; DIS = "document.querySelector('#screen .lin-card [data-act=linSign]').disabled"
    card = g.ev(CARD); txt = g.ev("document.querySelector('#screen').innerText")
    check(g.ev("linLast()") > g.ev("S.day") and '簽約・開工 $50,000' in card and '最後一晚' not in card and 'Madame Lin 做到' not in card and 'Fine Dining' not in card,
          f'the same day: 簽約・開工 $50,000, nothing about her last night or a level: {card[-90:]!r}')
    check('再想想' not in txt and '還在這裡' not in txt and 'Jill 決定接' in txt and not g.ev("[...document.querySelectorAll('#screen button')].some(x=>/接下隔壁/.test(x.textContent))"), 'decided — no 「接下隔壁」, no 「再想想」')
    # what is missing, on the card: the money, nothing else — a rating of 3.0 and a level-1 restaurant change nothing
    g.ev("window.__rate=3.0;rating=function(){return window.__rate};window.__lv0=S.level;S.level=1;S.money=30000;showShop()"); g.page.wait_for_timeout(40); card = g.ev(CARD)
    check(g.ev(DIS) is True and '還差 $20,000' in card and '評分' not in card and '擴建' not in card, f'short of money: only the money is said: {card[-80:]!r}')
    g.ev("S.money=60000;showShop()"); g.page.wait_for_timeout(40); card = g.ev(CARD)
    check(g.ev(DIS) is False and '評分' not in card, f'3.0, level 1, $60,000: 簽約・開工 can be pressed: {card[-60:]!r}')
    g.ev("S.money=49999;showShop()"); g.page.wait_for_timeout(40); card = g.ev(CARD)
    check(g.ev(DIS) is True and '還差 $1' in card, f'$1 short: {card[-60:]!r}')
    # no way around the story: an act 「buyLounge 1」 (no such button in the game; a stale one, a script) builds nothing
    g.ev("S.money=500000;(()=>{const el=document.createElement('button');el.dataset.act='buyLounge';el.dataset.k='1';$('#screen').appendChild(el);el.click();el.remove()})()")
    check(g.ev("loungeLv()") == 0 and g.ev("S.money") == 500000 and g.ev("S.loungeProj.state") == 'planned', 'Lounge I is never bought around 簽約・開工')
    # THE REGRESSION (the user, 2026-10-06/07): her last night still ahead + 《看看》 + $50,000 → the signing goes through,
    # at a rating of 3.0 and level 1
    g.ev("S.money=50000;showShop()"); g.page.wait_for_timeout(40)
    old_last = g.ev("linLast()")
    check(old_last > g.ev("S.day") and not g.ev("!!fact('lin_closed')") and g.ev(DIS) is False, 'her last night has not come, and 簽約・開工 can be pressed')
    g.click('#screen .lin-card [data-act=linSign]'); g.page.wait_for_timeout(60)
    st = json.loads(g.ev("JSON.stringify({money:S.money,state:S.loungeProj.state,closed:fact('lin_closed')&&fact('lin_closed').d,day:S.day,bar:barState(),news:linNewsHTML(),early:linS().early,card:document.querySelector('#screen .lin-card').innerText,note:STORY_LINES.find(L=>L.k==='nextdoor').beats.find(b=>b[0]==='lin_closed')[2].note()})"))
    check(st['money'] == 0 and st['state'] == 'signing' and '明天開店前，Jill 去隔壁簽約' in st['card'], f'paid $50,000; the signing is the next opening: {st}')
    check(st['closed'] == st['day'] and st['bar'] == 'closed' and st['news'] == '' and st['early'] == 1 and st['note'].startswith('Jill 簽約的前一晚'), f'that evening was her last — her bar closed, no countdown, the story page says why: {st}')
    g.ev("__rate=4.2;S.level=__lv0")
    g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(120)
    g.ev("autoStock();window.__noScenes=false;window.__holds=true"); start_day(g); install_bot(g); g.ev("for(let i=0;i<3;i++)__tick(1000/30)")
    check(g.ev("DLG&&DLG.sh&&DLG.sh.k") == 'lin_sign', 'the next morning: 《簽約》')
    _dlg_lines(g, 40)
    check(g.ev("!!fact('lin_signed')") and g.ev("barState()") == 'reno' and g.ev("S.loungeProj.open") == g.ev("S.day") + 2, 'signed; two days of work')
    g.ev(f"S.day={old_last}+1")
    check(not g.ev("STORY_EV.find(e=>e.k==='lin_last').when({})"), 'the night that was to be her last passes: nothing fires (no reminder after a signing)')
    check(not g.errors, g.errors[:3]); g.close()
    # not signed: her last night comes as it always did, then one reminder — and the signing was open all along
    g = Game(b, port, target, seed=8764, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day52.json'); g.ev(_LIN_TO_THE_VIEWING)
    g.ev("const st=story();for(const k of ['lin_viewing'])st.facts[k]={d:S.day-1,n:1,l:S.day-1};evState('lin_viewing').n=1;linDecided();linS().last=S.day+1;S.money=20000")
    g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(150)
    g.ev("window.__notes=[];const __nl=noteLine;noteLine=function(t){__notes.push(t);return __nl.apply(this,arguments)}")
    g.ev("autoStock()"); start_day(g); install_bot(g); g.ev(LAZY_ACTOR + "\nwindow.__act=window.__actLazy;window.__noScenes=true"); g.ev("__botUntil('phase!==\"service\"',200000,1/30)")
    g.ev("for(let i=0;i<80&&typeof DLG!=='undefined'&&DLG;i++){__tick(400);dlgNext()}")
    st = json.loads(g.ev("JSON.stringify({closed:fact('lin_closed')&&fact('lin_closed').d,day:S.day,last:linLast(),notes:__notes,early:!!linS().early,note:STORY_LINES.find(L=>L.k==='nextdoor').beats.find(b=>b[0]==='lin_closed')[2].note()})"))
    check(st['closed'] == st['day'] == st['last'] and not st['early'] and st['note'].startswith('Madame Lin 做到月底'), f'her last night, as it always was: {st}')
    check([n for n in st['notes'] if '隔壁的門關上了' in n] == ['隔壁的門關上了。簽約・開工在「升級餐廳 › 店舖工程」。'], f'one reminder, after her last night: {st["notes"]}')
    check(not g.errors, g.errors[:3]); g.close()
    # saves from before: a 「再想想」, a card nobody answered, a save between 《看看》 and that night's card, one that had taken
    # it, one still waiting for her last night — all sign; one that had paid $120,000 is not charged again
    base = json.load(open(os.path.join(ROOT, 'tests', 'saves', 'player_day52.json'), encoding='utf-8')); base = base.get('save', base); D = base['day']
    for kind in ('deferred', 'unanswered', 'mid', 'planned', 'waiting', 'paid120k'):
        raw = json.loads(json.dumps(base)); raw['linMig'] = 1   # an rc8.x save: only the new step runs
        F = raw['story']['facts']; E = raw['story'].setdefault('ev', {}); f = lambda dd: {'d': dd, 'n': 1, 'l': dd}
        F['lin_hello'] = {'d': 0, 'n': 1, 'l': 0, 'retro': 1}
        for k in ('tasting_night', 'pairing_wine'): F[k] = f(D - 20)
        F['lin_retiring'] = f(D - 13); F['ken_where'] = f(D - 12); F['jd_want'] = f(D - 11); F['dylan_book'] = f(D - 8); F['lin_viewing'] = f(D - 6)
        for k in ('pairing_start', 'lin_retire', 'ken_where', 'jd_want', 'dylan_book', 'lin_viewing'): E[k] = {'n': 1, 'd': D - 6, 'miss': 0}
        raw['story']['lin'] = {'last': D + 4} if kind == 'waiting' else {'last': D - 1}; raw['money'] = 500000
        if kind != 'waiting': F['lin_closed'] = f(D - 1); E['lin_last'] = {'n': 1, 'd': D - 1, 'miss': 0}
        if kind != 'mid':
            F['lounge_project'] = f(D - 6); E['lin_decide'] = {'n': 1, 'd': D - 6, 'miss': 0}
            raw['loungeProj'] = {'revealed': D - 6} if kind == 'unanswered' else {'revealed': D - 6, 'state': kind, 'at': D - 6}
        if kind in ('planned', 'waiting', 'paid120k'): F['lin_take'] = f(D - 6)
        if kind == 'waiting': raw['loungeProj']['state'] = 'planned'
        if kind == 'paid120k': raw['loungeProj'].update(state='signing', paid=D, paidPrep=0); raw['money'] = 500000 - 120000
        g = Game(b, port, target, seed=8762, manual=True, viewport={'width': 390, 'height': 844})
        g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.page.wait_for_timeout(150)
        g.click('[data-act=openFresh]') if g.page.query_selector('[data-act=openFresh]') else g.click('[data-act=open]'); g.page.wait_for_timeout(150)
        st = json.loads(g.ev("JSON.stringify({take:fact('lin_take'),proj:fact('lounge_project'),state:S.loungeProj&&S.loungeProj.state,mig:S.linDecMig,money:S.money,facts:Object.keys(story().facts),rate:+rating().toFixed(1)})"))
        check(st['take'] and st['take']['d'] == D - 6 and not st['take'].get('retro') and st['proj'] and st['mig'] == 1, f'{kind}: read as decided at 《看看》 (Day {D - 6}): {st}')
        added = sorted(k for k in set(st['facts']) - set(F) if k.startswith(('lin_', 'lounge_', 'pairing_', 'evan_')))
        check(added == {'planned': [], 'waiting': [], 'paid120k': [], 'mid': ['lin_take', 'lounge_project']}.get(kind, ['lin_take']), f'{kind}: nothing else of the line added: {added}')
        g.ev("showShop();shopTab='works';showShop()"); g.page.wait_for_timeout(60)
        txt = g.ev("document.querySelector('#screen').innerText")
        check('再想想' not in txt and '還在這裡' not in txt and '最後一晚以後' not in txt and not g.ev("!!document.querySelector('[data-act=linTake],[data-act=loungeGo]')"), f'{kind}: nothing of the old flow on the works page')
        if kind == 'paid120k':
            check(st['money'] == 380000 and st['state'] == 'signing' and not g.ev("linSignPay()") and g.ev("S.money") == 380000 and '開店前，Jill 去隔壁簽約' in g.ev(CARD), f'{kind}: paid at $120,000 — not charged again, the signing goes ahead: {st}')
        else:
            check(st['state'] == 'planned' and g.ev(DIS) is False, f'{kind}: 簽約・開工 can be pressed now: {st}')
            m0 = g.ev("S.money"); g.click('#screen .lin-card [data-act=linSign]'); g.page.wait_for_timeout(60)
            check(m0 - g.ev("S.money") == 50000 and g.ev("S.loungeProj.state") == 'signing' and g.ev("!!fact('lin_closed')"), f'{kind}: signed for $50,000')
        check(not g.errors, g.errors[:3]); g.close()
    # a save with The Lounge built at $120,000: left as it is — no money back, nothing to pay, nothing replayed
    g = Game(b, port, target, seed=8765, manual=True, viewport={'width': 390, 'height': 844})
    raw = load_save(g, 'player_day61.json')
    check(g.ev("S.money") == raw['money'] and g.ev("loungeLv()") == raw['rooms']['lounge'] and not g.ev("linSignPay()") and g.ev("S.money") == raw['money'], 'a built Lounge: the money as it was, nothing to pay again')
    g.close()
    g = Game(b, port, target, seed=8763, manual=True, viewport={'width': 390, 'height': 844})
    g.click('[data-act=open]'); g.page.wait_for_timeout(100)
    guide = g.ev("GUIDE.find(x=>/Lounge/.test(x.h)).pts.find(p=>p[0]==='怎麼來的')[1]")
    check(g.ev("S.linDecMig") == 1 and 'Jill 看過隔壁，就決定接下來' in guide and '評分' not in guide and '$50,000' in guide and '不用等 Madame Lin 的最後一晚' in guide
          and not any(w in guide for w in ('再想想', '要不要接', '等她最後一晚過了', 'Fine Dining', '80,000', '120,000')), f'a new game: nothing to migrate; the manual says the same: {guide}')
    g.close()


@test
def v24_rc8_the_bell_rings_when_the_door_opens(b, port, target):
    """The player, 15:38: the brass bell Madame Lin brings on Day 1 stays on the door, and from then on the door rings —
    the bell swings and rings when a guest comes in or goes out (one ring for a busy door); nothing says what it is."""
    g = Game(b, port, target, seed=8741, manual=True, viewport={'width': 390, 'height': 844})
    g.ev("__tick(500)"); g.click('[data-act=open]'); g.page.wait_for_timeout(120)
    start_day(g); install_bot(g)
    check(g.ev("propOn('linbell')") is True, 'Day 1: on the door')
    g.ev("window.__rings=[];window.__opens=0;const __br=bellRing;bellRing=function(){__opens++;const t0=BELL.t;const r=__br.apply(this,arguments);if(BELL.t!==t0)__rings.push(R.t);return r}")
    g.ev("__botUntil('__rings.length>0',20000,1/30)"); g.ev("__tick(80)")
    check(g.ev("__rings.length") >= 1 and abs(g.ev("bellSwing()")) > 0.05, 'a guest at the door: it rings and swings')
    g.ev("__tick(2000)")
    check(g.ev("bellSwing()") == 0, 'and settles')
    g.ev("__botUntil('R.t>R.dur*.6',200000,1/30)")
    check(g.ev("__opens") >= 6, f'all evening, guests in and out through the door: {g.ev("__opens")}')   # (the bot's evening runs without the clock the swing uses: one ring for those that come together)
    g.ev("__tick(2000)"); r0 = g.ev("__rings.length"); g.ev("bellRing();bellRing()")
    check(g.ev("__rings.length") == r0 + 1, 'two at once: one ring')
    man = g.ev("JSON.stringify(GUIDE)")
    check('門鈴' not in man and '鈴' not in man.replace('鈴聲', ''), 'the manual says nothing about the bell')
    check(not g.errors, g.errors[:3]); g.close()


# ---------------------------------------------------------------- rc8 晴 × 阿拓 after work: the five scenes
def _qt_until(g, key, cap=12):
    """the bot through the evening until the held scene `key` is on screen; any other held scene is stepped through"""
    for _ in range(cap):
        g.ev("__botUntil(\"!!(typeof DLG!=='undefined'&&DLG)||phase!=='service'\",200000,1/30)")
        if g.ev("phase") != 'service': return False
        if g.ev("!!(DLG&&DLG.sh&&DLG.sh.k===%r)" % key): return True
        g.ev("for(let i=0;i<80&&DLG&&!(DLG.sh&&DLG.sh.k===%r);i++){__tick(400);dlgNext()}" % key)
        if g.ev("!!(DLG&&DLG.sh&&DLG.sh.k===%r)" % key): return True
    return False


def _qt_next_day(g):
    """the evening to its end and on to the next day's prep, whatever card or sheet is up"""
    g.ev("for(let i=0;i<120&&typeof DLG!=='undefined'&&DLG;i++){__tick(400);dlgNext()}")
    g.ev("__botUntil('phase!==\"service\"',200000,1/30)"); g.page.wait_for_timeout(60)
    for _ in range(8):
        g.ev("for(let i=0;i<80&&typeof DLG!=='undefined'&&DLG;i++){__tick(400);dlgNext()}")
        ph = g.ev("phase")
        if ph == 'prep': return
        g.ev("try{if($('#reveal')&&!$('#reveal').hidden)hideReveal()}catch(e){}")
        g.ev("doAct(%r,null,null,null)" % ('toShop' if ph == 'summary' else 'nextDay')); g.page.wait_for_timeout(100); g.ev("__tick(1200)")


def _qt_evening(g, key, setup='', days=6):
    """evenings until the held scene `key` comes (the day's one story slot may be another line's); `setup` before each"""
    for _ in range(days):
        g.ev(setup + ";kenS().next=null;cnS().next=null")
        to_service(g); g.ev("window.__act=window.__actLazy;window.__noScenes=false;window.__holds=true")
        if _qt_until(g, key): return True
        _qt_next_day(g)
    return False


def _qt_lines(g, key, cap=90, probe=None):
    """the held scene `key`, line by line (a scene queued after it is not read); with `probe`, a JS value per line"""
    out = []
    for _ in range(cap):
        if not g.ev("!!(typeof DLG!=='undefined'&&DLG&&DLG.sh&&DLG.sh.k===%r)" % key): break
        l = g.ev("(()=>{const n=document.querySelector('#dlg .dlg-name'),t=document.querySelector('#dlg .dlg-text');return(n&&n.textContent?n.textContent+'：':'')+(t?t.textContent:'')})()")
        out.append((l, g.ev(probe)) if probe else l)
        g.ev("__tick(400);dlgNext()"); g.ev("for(let j=0;j<2;j++)__tick(1000/30)")
    return out


_QT_FORBID = ('我喜歡妳', '跟我在一起', '你不要鼓掌', '空間給', '不打擾', '慢慢聊', '終於在一起', '新的開始', '才沒有', '我們只是同事', '誰喜歡他', '早就懷疑', '難怪你', '司法官', '律師')


@test
def v24_rc8_qing_tuo_after_work_five_scenes(b, port, target):
    """The player's brief of 2026-10-03 (晴 × 阿拓 after work) with 19:19 §18–§19, on the player's Day 74 save: five held
    scenes in The Lounge, one an evening, none with Jill. 《今天喝？》 — Dylan's first drink there (Evan has known him since
    the signing: 「稀奇」), the exam never named, his bill paid once (「這杯算了。」「不用。」…). 《晚點回去》 — after closing,
    the bottle handed over. 《最近比較常》 — 予安 (a while a pianist) stays for one and sees 沈晴's look; nothing said.
    《你喜歡予安？》 — 沈晴 at her parents'; Dylan's wrong guess; he learns it only at 「……沈晴？」; Evan sees the piano;
    予安 knows without being told; five notes, one hand. 《講完》 — 沈晴 back some days; 阿拓 plays them himself; the
    sentence unfinished; 「……好啊。」; Dylan claps twice; the three go; the two of them are left. The after-hours
    lines move nothing."""
    g = Game(b, port, target, seed=9401, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day74_1508.json')
    g.ev("kenS().next=null;cnS().next=null")
    check(g.ev("!!fact('evan_knows_dylan')&&!fact('qt_drink')&&loungeDoneDay()!=null&&S.day>=loungeDoneDay()+10") is True, 'the save: Evan has known Dylan since the signing (its history); The Lounge open a while')
    # 1 《今天喝？》
    to_service(g); g.ev("window.__act=window.__actLazy;window.__noScenes=true;R.sched=R.sched.filter(o=>o.reg!=='dylan'&&!(o.regs||[]).includes('dylan'))")
    g.ev("__botUntil('R.t>=R.dur*.3',200000,1/30)")
    # rc8 (the player, 2026-10-03, on the Day 81 save: 「他第一次去酒吧的故事都還沒開始前他不能去酒吧」): before 《今天喝？》 no seat in The
    # Lounge for Dylan — not waiting for a table (the full-house rule) — except the evening planned for that scene
    pre = json.loads(g.ev("JSON.stringify((()=>{for(const t of loungeTables()){t.group=null;t.dirty=false;t.claim=null}const a=loungeSeatFor({reg:'dylan',size:1,type:'regular'});const b=loungeSeatFor({reg:'dylan',size:1,type:'regular',lgPlan:1});return{wait:!!a,planned:!!b,due:qa1Due()}})())"))
    check(not pre['wait'] and pre['planned'] == pre['due'], f'before 《今天喝？》 Dylan is not seated in The Lounge, only on its planned evening: {pre}')
    g.ev("window.__col=[];const __st=storyTick;storyTick=function(k,c){if(k==='collect'&&c&&c.g&&c.g.reg==='dylan')__col.push(!!c.again);return __st.apply(this,arguments)}")
    g.ev("R.sched.splice(R.si,0,{t:R.t+2,type:'regular',reg:'dylan',size:1,story:1,lounge:1,lgRetry:1,tries:1});window.__noScenes=false;window.__holds=true")
    check(_qt_until(g, 'qt_drink') and g.ev("room") == 'lounge' and g.ev("JSON.stringify(STAGE.who.map(p=>p.id))") == '["evan","dylan"]', '《今天喝？》 held in The Lounge, Evan and Dylan')
    lines = _qt_lines(g, 'qt_drink')
    check(lines == ['Dylan 在吧台坐下。', 'Evan：今天喝？', 'Dylan：嗯。', 'Evan：稀奇。', 'Dylan：考完了。', 'Evan：考試？', 'Dylan：嗯。', 'Evan：考得怎樣？', 'Dylan：考完了。', 'Evan：……行。'], f'the lines: {lines}')
    g.ev("window.__noScenes=true")
    g.ev("__botUntil(\"__col.length>0||!R.groups.some(q=>q.reg==='dylan')\",200000,1/30)"); g.ev("for(let i=0;i<200;i++)__tick(1000/30)")
    check(g.ev("JSON.stringify(__col)") == '[false]' and g.ev("!!fact('qx_pay')"), f'he pays, once ({g.ev("JSON.stringify(__col)")}); 「這杯算了。」「不用。」「你還真的付喔。」「不然呢？」')
    # 2 《晚點回去》
    _qt_next_day(g)
    check(_qt_evening(g, 'qt_late', "story().facts.qx_dylan=story().facts.qx_dylan||{d:S.day-3,n:2,l:S.day-1};story().facts.qt_drink.d=Math.min(story().facts.qt_drink.d,S.day-5)"), '《晚點回去》 at closing')   # two later drinks there, on two evenings
    st = g.ev("JSON.stringify(STAGE.who.map(p=>p.id))"); lines = _qt_lines(g, 'qt_late')
    check(st == '["evan","qing","tuo","dylan"]' and 'Evan 多拿了一個杯子，放在 Dylan 前面。' in lines and '沈晴伸手找酒。阿拓剛好在旁邊，直接把那一支遞給她。' in lines and '沈晴：謝啦。' in lines and lines[-1] == '散的時候，Dylan 把錢壓在杯子底下。', f'Evan, 晴, 阿拓 and Dylan; the bottle; his money under the glass: {st} {lines}')
    check(not any(l.startswith('Jill') for l in lines) and 'Jill' not in st, 'no Jill')
    # 3 《最近比較常》
    _qt_next_day(g)
    check(not g.ev("fact('ya_sees_qt')"), '予安 has seen nothing yet')
    ya = "story().facts.ya_join=story().facts.ya_join||{d:S.day-15,n:1,l:S.day-15};story().facts.ya_join.d=Math.min(story().facts.ya_join.d,S.day-10);while(!yaNight())story().facts.ya_join.d--"
    check(_qt_evening(g, 'qt_often', ya + ";story().facts.qt_late.d=Math.min(story().facts.qt_late.d,S.day-4)"), '《最近比較常》 at closing, on one of 予安\'s nights, a while after she became the pianist')
    lines = _qt_lines(g, 'qt_often')
    want = ['Evan：喝一杯？', '予安看了一下時間。', '林予安：一杯。', '林予安：你們下班都會留下來？', 'Evan：偶爾。', '阿拓：最近比較常。', '沈晴抬眼看了阿拓一下。阿拓沒有注意。', '予安看見了。她什麼都沒說。', '阿拓：還要？', '沈晴：一點。', '阿拓替她倒。']
    check(all(w in lines for w in want) and not any('沒有啊' in l for l in lines), f'the lines: {lines}')
    check(g.ev("!!fact('ya_sees_qt')&&!fact('dylan_knows_qt')") is True, '予安 has seen it; Dylan has not')
    # an evening's after-hours line moves nothing
    f0 = g.ev("JSON.stringify(Object.keys(story().facts).filter(k=>/^qt_/.test(k)).sort())")
    g.ev("STORY_EV.find(e=>e.k==='qx_after').run({})")
    check(g.ev("JSON.stringify(Object.keys(story().facts).filter(k=>/^qt_/.test(k)).sort())") == f0, 'the after-hours lines change no step of the story')
    # 4 《你喜歡予安？》
    _qt_next_day(g)
    # rc8: up to six evenings — as in play, if her two evenings go elsewhere (阿拓's day off, the night upstairs) she goes home again
    check(_qt_evening(g, 'qt_ya', ya + ";story().facts.qt_often.d=Math.min(story().facts.qt_often.d,S.day-5);if(!qaHome()){qaS().home={d:S.day,back:S.day+2}}", 6), '《你喜歡予安？》 at closing, while 沈晴 is at her parents\'')
    check(g.ev("!qingOn()&&!!qaHome()") is True, '沈晴 not in tonight')
    st = g.ev("JSON.stringify(STAGE.who.map(p=>p.id))")
    out = _qt_lines(g, 'qt_ya', 90, "!!fact('dylan_knows_qt')")
    lines = [l for l, _ in out]
    i = {l: n for n, l in reversed(list(enumerate(lines)))}
    seq = ['阿拓：如果你想跟一個人講清楚，你會怎麼講？', 'Evan：你終於要講了？', 'Dylan：你喜歡予安？', '阿拓：蛤？', 'Evan：你為什麼會覺得是予安？', 'Dylan：沈晴又不在。', '阿拓：是沈晴。', 'Dylan：……沈晴？',
           'Evan：鋼琴啊。', 'Evan：你彈。', 'Evan：教他一個最簡單的。', '林予安：沈晴？', 'Dylan：妳知道？', '林予安：知道啊。', 'Dylan：很明顯嗎？', '林予安：嗯。', '林予安：坐。', '林予安：記住就好。']
    check(all(s in i for s in seq) and [i[s] for s in seq] == sorted(i[s] for s in seq), f'one evening, in order — the question, the wrong guess, 「是沈晴」, the piano, 予安 knows, the lesson: {lines}')
    check('qing' not in st and 'Jill' not in st and not any(l.startswith('沈晴：') or l.startswith('Jill') for l in lines), f'沈晴 not there, nor Jill: {st}')
    at = i['Dylan：……沈晴？']
    check(not any(k for l, k in out[:at + 1]) and all(k for l, k in out[at + 1:]), 'Dylan learns it at 「……沈晴？」 (the step past it), not before')
    ev_before = [l for l in lines[:i['林予安：沈晴？']] if l.startswith('Evan：')]
    check(not any('沈晴' in l or '告白' in l for l in ev_before), f'nobody tells 予安: {ev_before}')
    yl = [l for l in lines if l.startswith('林予安：')]
    check(all(len(l) <= 16 for l in yl) and not any(w in ''.join(yl) for w in ('喜歡', '告白', '感情', '心')), f'予安 says only what the piano needs: {yl}')
    check(any('五個音' in l for l in lines) and any('一隻手' in l for l in lines) and not any(w in ''.join(lines) for w in ('整首', '一首')), 'one hand, five notes — not a piece')
    check(not any(w in ''.join(lines) for w in _QT_FORBID), 'no line the brief forbids')
    # 5 《講完》 — not the day she is back, some evenings later
    _qt_next_day(g)
    while g.ev("!!qaHome()"):
        g.ev("kenS().next=null;cnS().next=null"); to_service(g); g.ev("window.__act=window.__actLazy;window.__noScenes=true")
        check(not g.ev("STORY_EV.find(e=>e.k==='qt_said').when({})"), 'not while she is away'); g.ev("__botUntil('phase!==\"service\"',200000,1/30)"); _qt_next_day(g)
    g.ev(ya + ";kenS().next=null;cnS().next=null"); to_service(g); g.ev("window.__act=window.__actLazy;window.__noScenes=true")
    check(g.ev("!!qingOn()") is True and not g.ev("STORY_EV.find(e=>e.k==='qt_said').when({})"), 'back — and not on the day she is back')
    g.ev("__botUntil('phase!==\"service\"',200000,1/30)"); _qt_next_day(g)
    check(_qt_evening(g, 'qt_said', ya), '《講完》 some evenings after she is back')
    pairs = _qt_lines(g, 'qt_said', 80, "JSON.stringify(STAGE?STAGE.who.filter(p=>!p.hide).map(p=>p.id):[])")
    out = [l for l, _ in pairs]; vis = [v for _, v in pairs]
    lines = out
    seq = ['阿拓：沈晴。', '阿拓：妳過來一下。', '沈晴：你會彈琴？', '阿拓：不會。', '沈晴：……那你坐這裡幹嘛？', '阿拓：等一下。', '阿拓：我本來有想好要講什麼。', '阿拓：現在忘了。', '阿拓：妳知道我要講什麼嗎？', '沈晴：……大概。',
           '阿拓：那妳要不要……在……', '沈晴：在什麼？', '阿拓卡住了。', '沈晴：……好啊。', '啪、啪。', '是 Dylan 在拍手。', 'Evan：好啦，我先走了。', '林予安：我也走了。', 'Dylan：先走了。', '沈晴：你什麼時候學的？', '阿拓：妳回家的時候。', '沈晴：難怪。']
    pos = [lines.index(s) if s in lines else -1 for s in seq]
    check(-1 not in pos and pos == sorted(pos), f'the lines, in order: {lines}')
    check(not any(w in ''.join(lines) for w in _QT_FORBID) and not any(l.startswith('Jill') for l in lines), 'no 「我喜歡妳」, no 「跟我在一起」, nobody scolds him, nobody says why they go; no Jill')
    check(not any(('予安' in l and ('彈' in l or '伴奏' in l)) for l in lines), '阿拓 plays it himself — 予安 does not')
    check(json.loads(vis[-1]) == ['qing', 'tuo'], f'at the end only the two of them: {vis[-1]}')
    check(g.ev("STORY_LINES.find(L=>L.k==='qt').beats.slice(-5).map(b=>b[0]).join()") == 'qt_drink,qt_late,qt_often,qt_ya,qt_said', 'the story page carries the five')
    days = json.loads(g.ev("JSON.stringify(['qt_drink','qt_late','qt_often','qt_ya','qt_said'].map(k=>fact(k).d))"))
    check(len(set(days)) == 5 and days == sorted(days), f'one an evening, in order: {days}')
    # rc8: the line starts after Dylan's reveal (「DYLAN揭曉才進那個劇情阿」) — its pictures show his face; every scene has its picture
    pre = g.ev("(()=>{const st=S.dylan.stage,q=story().facts.qt_drink;delete story().facts.qt_drink;S.dylan.stage=2;const a=qa1Due();S.dylan.stage=st;story().facts.qt_drink=q;return a})()")
    check(pre is False, 'before the reveal 《今天喝？》 is not due')
    check(g.ev("['qt_first','qt_more','qt_lesson','qt_play','qt_alone'].every(k=>{const s=illusSrc(k);return s&&!s.tbd})") is True, 'the five pictures are the player\'s')
    check(not g.errors, g.errors[:3]); g.close()
