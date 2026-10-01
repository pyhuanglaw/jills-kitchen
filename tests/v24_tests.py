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


# ---------------------------------------------------------------- P1: 怡君, 《三個選項》, 秀琴阿姨 × Sophie / Mia, 《那面牆》
V24_KEYS = ['yj_meet', 'yj_look', 'yj_three', 'yj_chose', 'yj_move', 'yj_key', 'wall_worry', 'wall_photos', 'wall_visit', 'wall_wang',
            'wall_setback', 'wall_report', 'wall_fee', 'wall_prep', 'wall_mediation', 'wall_settle', 'wall_article']


@test
def v24_stage_gates_follow_the_chronology_and_their_own_gaps(b, port, target):
    """B / the pacing corrections: each stage needs the one before it and only its own gap (the fiction's time); the
    wall cannot begin before the spare key (+2 settled days); the Second Floor era opens two days after the settlement;
    the article only after the settlement; nothing needs a global multi-day gap."""
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
    check(g.ev("eraOpenDay('up')") == g.ev("S.day") + 2, 'the Second Floor era: two days after the settlement')
    check(g.ev("LANE_CAP.major") == 1 and g.ev("LANE_CAP.v24") == 1, 'one major beat a day for every story; the long stories have one smaller step a day of their own')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_yijun_comes_to_eat_and_her_mother_walks_over(b, port, target):
    """F: 怡君's first visit plays only when 秀琴阿姨 is really in — she walks to the table, then 「妳怎麼來了？」
    「吃飯啊。」 with the player's picture; never on the very start of the first day; never explained."""
    g = Game(b, port, target, seed=252, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day52.json')
    to_service(g)
    g.ev("story().v24=Object.assign(v24(),{first:S.day-1});window.__xq=xiuqin();setCrewAway(__xq,'off')")
    g.ev("if(!R.sched.slice(R.si).some(o=>o.name==='怡君'))spawn({t:R.t,type:'regular',size:1,name:'怡君',story:1})")
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
    """The player's Day 52 save, forty days of lazy play (seeded), the arbiter as in play: 怡君's arc, then the wall,
    then the Second Floor era opens; never two major beats in a day; nothing on the first day's start; everyone who
    speaks in a restaurant beat was really there (the beats check it); no page errors."""
    g = Game(b, port, target, seed=254, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day52.json')
    g.ev("window.__fastSay=1")
    seed = "Math.random=(function(){let a=%d;return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
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
    up = g.ev("eraOpenDay('up')")
    check(up is not None and up <= first + 33, f'the Second Floor era opens by Day {first + 33} (78–86): {up}')
    check(all(v <= 1 for v in majors.values()), f'never two major beats in a day: {majors}')
    check(g.ev("eraOpen('up')"), 'the Second Floor era is open after the settlement')
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
            check('Jill 認識很久的阿姨' in seen['coach'], f"the coach names her once: {seen['coach']!r}")
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
    someone else. Let her go and she does not come back to help in the evenings."""
    g = Game(b, port, target, seed=261, manual=True, viewport={'width': 390, 'height': 844})
    install_bot(g)
    g.click('[data-act=open]'); g.ev("window.__fastSay=1")
    start_day(g); g.ev("__bot(80000,1/30)"); g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
    if g.ev("phase") == 'summary': g.click('[data-act=toShop]')
    check(g.ev("xqHelperMode()&&!!fact('xq_helper')&&xqm().helper===1"), 'before a cleaner: the evening helper')
    g.ev("relSet('s:xq','sophie','spoke');relSet('s:xq','mia','spoke');S.money=99999;S.day=4;shopTab='staff';showShop()")   # the staff tab opens on Day 4
    check('第一位清潔員就是秀琴阿姨' in g.ev("document.querySelector('#screen').innerText"), 'the recruit list says so before')
    _act(g, 'hire', k='cleaner'); g.ev("__tick(30)")
    m = json.loads(g.ev("JSON.stringify((S.crew||[]).map(m=>({id:m.id,name:m.name,role:m.role})))"))
    check(m == [{'id': 'xq', 'name': '秀琴阿姨', 'role': 'cleaner'}], f'the first cleaner is her, the same person: {m}')
    check(g.ev("!!fact('xq_hired')&&!xqHelperMode()&&xqm()===xiuqin()&&xqKnows('sophie')===1&&xqKnows('mia')===1"), 'an ordinary cleaner now, who still knows them')
    check(g.ev("dayLog().some(l=>l.w==='秀琴阿姨'&&l.t==='那以後就天天來了。')"), 'her one line (a scene with her face over the shop; tests log it)')
    check('第一位清潔員就是秀琴阿姨' not in g.ev("document.querySelector('#screen').innerText"), 'the recruit note is gone')
    g.ev("S.level=Math.max(S.level,3)")
    _act(g, 'hire', k='cleaner'); g.ev("__tick(30)")
    check(g.ev("S.crew.map(m=>m.name).join()") == '秀琴阿姨,小彤', 'the next cleaner is someone else')
    _act(g, 'crewFire', k='xq'); _act(g, 'crewFire', k=g.ev("S.crew[0].id"))
    check(g.ev("!!fact('xq_gone')&&!xqHelperMode()&&!xqm()"), 'let go: no evening helper after that')
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
        if day == 3: _act(g, 'hire', k='waiter'); g.ev("__tick(30)")
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
    check('— last: v2.4 rc4' in open(os.path.join(ROOT, 'js', 'game.js'), encoding='utf-8').read(), 'the audit stamp on GUIDE')
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
def v24_the_day_is_held_for_the_beat_its_people_came_for(b, port, target):
    """Pacing (measured on the Day 52 save): when the schedule brings someone for a due v2.4 major beat, that beat keeps
    the day's one major slot until it plays or until 85% of the service; another story's major that comes up meanwhile
    waits (it is counted as missed, so its priority rises) — except a beat that has only this day (floor 0: Dylan on
    Valentine's), which is never held back. Grouped story visits keep their hour."""
    g = Game(b, port, target, seed=267, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day52.json')
    to_service(g)
    g.ev("STORY_EV.push({k:'__t_major',lane:'major',cls:'A',floor:1,at:['order'],when:()=>true,run:()=>{}},{k:'__t_dated',lane:'major',cls:'A',floor:0,at:['order'],when:()=>true,run:()=>{}})")
    g.ev("const d=storyDay();d.major=0;d.seen={};v24().res={d:S.day,k:['yj_meet']};R.t=R.dur*.5")
    check(g.ev("JSON.stringify(v24Held('order'))") == '["yj_meet"]', 'held for 怡君 while her beat is due')
    fired = g.ev("storyTick('order',{})")
    check(fired == '__t_dated', f'a beat with only this day still plays: {fired}')
    g.ev("const d=storyDay();d.major=0;d.seen={};STORY_EV.splice(STORY_EV.findIndex(E=>E.k==='__t_dated'),1)")
    m0 = g.ev("evState('__t_major').miss")
    g.ev("storyTick('order',{})")
    check(g.ev("storyDay().major") == 0 and g.ev("evState('__t_major').n") == 0 and g.ev("evState('__t_major').miss") == m0 + 1, 'another major waits, counted as missed')
    g.ev("R.t=R.dur*.86;storyTick('order',{})")
    check(g.ev("v24Held('order')") is None and g.ev("evState('__t_major').n") == 1, 'late in the service the hold is gone, and it plays')
    g.ev("const d=storyDay();d.major=0;d.seen={};R.t=R.dur*.5;factSet('yj_meet')")
    check(g.ev("v24Held('order')") is None, 'once the beat has played, nothing is held')
    g.ev("STORY_EV.splice(STORY_EV.findIndex(E=>E.k==='__t_major'),1)")
    # grouped story visits keep their hour; the first of a group finds a room with a table for each
    out = json.loads(g.ev("JSON.stringify((()=>{const out=[];v24Visits(out,R.dur,()=>true);return out})())"))
    check(all(o.get('hold') for o in out if o.get('v24grp')), f'grouped visits are held at their hour: {out}')
    check(not g.errors, g.errors[:3]); g.close()
