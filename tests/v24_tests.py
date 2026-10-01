"""v2.4 tests — Staff Lives foundations (docs/v24/AUDIT_AND_PLAN.md): the back-of-house area, tenure as a class, one
day's story presence, the walk-over, the order of the eras and their dormancy, narrative-time pacing, the story
illustrations, the name pools. Same harness and TESTS list as run_tests.py (imported at the end of that file), so
`python3 tests/run_tests.py -k v24` runs these."""
import json, os, sys, glob
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
    check(g.ev("crewCap()") == 12 and g.ev("S.crew.length") == 12, 'the +2 is kept: the crew of twelve still fits')
    check(g.ev("S.money") == raw['money'], 'nothing refunded or charged')
    d = g.ev("OPS.find(o=>o.k==='room').d(1)")
    check('休息' not in d and '整理區' in d and '2 位員工' in d, f'work storage, +2: {d}')
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
    """B / pacing: 怡君 first; 《那面牆》 opens two days after the spare key; the Second Floor two days after the
    settlement — not walled behind anything else. An era whose people are not on the crew goes dormant once a later
    one could start and has waited 5 days (the next blocked one with it), and never wakes after a later era began.
    Nothing at the very start of the first day; no gap between beats except a stage's own."""
    g = Game(b, port, target, seed=245, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day52.json')
    g.ev("v24()")
    d0 = g.ev("S.day")
    check(g.ev("v24().first") == d0 and g.ev("eraOpen('yj')") and not g.ev("eraOpen('wall')") and not g.ev("eraOpen('up')"), 'only 怡君 at first')
    check(g.ev("v24Fresh('daystart')") and not g.ev("(()=>{S.day++;const r=v24Fresh('daystart');S.day--;return r})()"), 'nothing at the start of the first day only')
    g.ev("factSet('yj_meet');factSet('yj_key')")
    check(not g.ev("eraOpen('wall')") and g.ev("eraOpenDay('wall')") == d0 + 2, 'the wall: two days after the key')
    g.ev("S.day+=2"); check(g.ev("eraOpen('wall')"), 'open on the day')
    g.ev("factSet('wall_worry');factSet('wall_settle')")
    check(g.ev("eraOpenDay('up')") == d0 + 4, 'the floor: two days after the settlement')
    check(g.ev("stageGap('wall_settle',0)") and not g.ev("stageGap('wall_settle',1)"), 'a stage waits only its own gap')
    # dormancy: no 秀琴阿姨, a later era that could start
    g.ev("delete story().facts.yj_meet;delete story().facts.yj_key;delete story().facts.wall_worry;delete story().facts.wall_settle;S.day-=2")
    g.ev("window.__xqm=S.crew.find(m=>m.name==='秀琴阿姨');S.crew=S.crew.filter(m=>m!==__xqm);V24_ERAS[2].__can=V24_ERAS[2].can;V24_ERAS[2].can=()=>true")
    for i in range(4):
        g.ev("S.day++;v24Dormancy()")
    check(g.ev("v24().dorm.yj") is None and not g.ev("eraOpen('up')"), 'four days: still waiting')
    g.ev("S.day++;v24Dormancy()")
    check(g.ev("v24().dorm.yj") is not None and g.ev("v24().dorm.wall") is not None and g.ev("eraOpen('up')"), 'the fifth: 怡君 and the wall dormant, the floor open')
    check(not g.ev("eraOpen('yj')") and not g.ev("eraOpen('wall')"), 'dormant is not done: those eras are closed')
    g.ev("S.crew.push(__xqm);S.day++;v24Dormancy()")
    check(g.ev("v24().dorm.yj") is None, 'she is back before the floor began: 怡君 wakes')
    g.ev("S.crew=S.crew.filter(m=>m!==__xqm);for(let i=0;i<5;i++){S.day++;v24Dormancy()}factSet('up_hint');S.crew.push(__xqm);S.day++;v24Dormancy()")
    check(g.ev("v24().dorm.yj") is not None, 'once the floor began, it does not wake (no reversed chronology)')
    g.ev("V24_ERAS[2].can=V24_ERAS[2].__can")
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
    check(g.ev("['yj_intro','yj_key','wall_leak','wall_settled'].every(k=>!!STORY_ART[k])"), "all four of the player's pictures are in")
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
        check(ok['t'] and not ok['v24'], f'{name}: tenure classes, no story facts: {ok}')
        check(not g.errors, f'{name}: {g.errors[:3]}'); g.close()
    g = Game(b, port, target, seed=249, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day52.json')
    to_service(g)
    d = g.ev("S.day")
    play_day(g, max_steps=60000)
    check(g.ev("story().v24&&story().v24.first") == d, 'the first v2.4 day is recorded when it is played')
    check(not g.errors, g.errors[:3]); g.close()
