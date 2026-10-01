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
    check('— last: v2.4 rc5' in open(os.path.join(ROOT, 'js', 'game.js'), encoding='utf-8').read(), 'the audit stamp on GUIDE')
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
    check(g.ev("loungeCap()") == 2 and g.ev("restaurantCap()") == r0 + 2, 'Lounge I alone: two Lounge places; the restaurant unchanged')
    g.ev("S.rooms.lounge=2;delete S.rooms.up;delete S.rooms.kitchen2")
    # where they work is the board's: a restaurant server on the Lounge floor stays restaurant staff; 安安 works both
    g.ev("(()=>{const m=S.crew.find(m=>m.name==='Nina');m.duties=Object.assign({},waiterDuties(m),{lounge:true})})()")
    check(g.ev("crewPool(S.crew.find(m=>m.name==='Nina'))") == 'restaurant' and g.ev("waiterDuties(S.crew.find(m=>m.name==='Nina')).lounge") is True, 'Nina works the Lounge floor and is still restaurant staff')
    check(g.ev("(()=>{const m=S.crew.find(m=>m.name==='安安');const d=waiterDuties(m);return d.lounge&&d.seat&&d.order})()") is True, '安安: the Lounge floor, and seating and orders anywhere')
    # the shop says it, the manual says it
    g.ev("showShop();shopTab='staff';showShop()"); g.page.wait_for_timeout(80); txt = g.ev("document.querySelector('#screen').innerText")
    check('餐廳員工 12/12' in txt and 'Lounge 員工 5/5' in txt and 'Lounge 名單' in txt and 'Lounge 的人都到齊了' in txt, 'the staff page shows two pools')
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
    g.ev("S.money+=500000"); n = g.ev("S.crew.length"); _hire(g, 'hire', 'cleaner')
    check(g.ev("S.crew.length") == n, 'over its number, the restaurant does not hire')
    g.ev("showShop();shopTab='staff';showShop()"); g.page.wait_for_timeout(80); txt = g.ev("document.querySelector('#screen').innerText")
    check('餐廳員工 13/12' in txt and '比上限多' in txt and '大家都留著' in txt, 'the page says why')
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


UP_DONE_BEFORE = r"""(()=>{const set=(k,b)=>{const d=S.day-b;story().facts[k]={d,n:1,l:d}};
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
    """P2 (second_floor_and_long_arcs §3–§16, implementation pass I): the era opens only after the wall, with the side
    room and a grown restaurant; a regular's question first (no journal), the crew, the landlord's afternoon (Jill goes
    up once; words only, no room), and only days after that the night of the missing cats. Nothing unlocks."""
    g = Game(b, port, target, seed=281, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day52.json')
    check(g.ev("eraOpen('up')") is False and g.ev("due('up_hint',null,0,'up')") is False, 'not before 怡君 and the wall')
    g.ev(UP_DONE_BEFORE)
    check(g.ev("eraOpen('up')") is True and g.ev("upCan()") is True, 'two days after the wall settled, with the side room and a crew of twelve')
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
    seen = {'side': False, 'up': False, 'tab': False}
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
    after = json.loads(g.ev("JSON.stringify({cats:['mikan','ban'].map(id=>{const c=catBy(id);return[c.st,!!c.away,c.hidden]}),door:R.upDoor,tab:roomsOpen().includes('up'),pill:$('#closePill').hidden,up:!!S.rooms.up})"))
    check(all(not c[1] and not c[2] for c in after['cats']) and not after['door'] and not after['tab'] and not after['pill'] and not after['up'], f'downstairs, the door latched, the tab gone, the closing on — and nothing unlocked: {after}')
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
    pressure; the call needs the reminder two days back and a restaurant that can afford to think of it; at closing she
    stands at the stair door and calls; the project is offered (開始規劃 / 之後再說) and only then is in 店舖工程; bought,
    the whole floor is a room (furniture over the next days, traces later), the street's windows warm, no seat and no
    staff place added; kept across reloads before and after."""
    g = Game(b, port, target, seed=284, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day52.json')
    g.ev(UP_DONE_BEFORE)
    for k, back in [('up_hint', 16), ('up_staff', 15), ('up_inspect', 13), ('up_door', 10), ('up_cats', 10)]:
        _upf(g, k, back)
    check(g.ev("due('up_remind','up_cats',2,'up')&&upKinds(UP_STAFF)>=2&&upKinds(UP_CUST)>=2") is False, 'no reminder without the pressure')
    for k, back in [('sp_seat', 12), ('sp_box', 9), ('up_busy', 7), ('up_small', 5)]:
        _upf(g, k, back)
    check(g.ev("due('up_remind','up_cats',2,'up')&&upKinds(UP_STAFF)>=2&&upKinds(UP_CUST)>=2") is True, 'two of each: someone may say it')
    _upf(g, 'up_remind', 1)
    check(g.ev("due('up_ask','up_remind',2,'up')") is False, 'not the next day')
    _upf(g, 'up_remind', 2); g.ev("S.money=50000")
    check(g.ev("upAskReady()") is False, 'not with an empty till')
    g.ev("S.money=420000")
    check(g.ev("due('up_ask','up_remind',2,'up')&&upAskReady()") is True, 'ready')
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
    g.ev("S.money=Math.max(S.money,400000)")
    check(g.ev("buyUp()") is True, 'bought')
    g.ev("hideReveal()")
    st = json.loads(g.ev("JSON.stringify({up:S.rooms.up,open:roomOpen('up'),lease:S.up.lease,furn:S.up.furn,caps:[restaurantCap(),loungeCap(),tablesTotal()],fact:!!fact('up_lease')})"))
    check(st['up'] == 1 and st['open'] and st['fact'] and st['caps'] == caps0, f'the floor is a room; no seat, no staff place: {st}')
    L = st['lease']
    check(st['furn']['table'] == L + 1 and st['furn']['scratch'] == L + 5, f'the furniture comes over the next days: {st["furn"]}')
    check(g.ev("upHas('table')") is False, 'the same evening: empty')
    g.ev("save()"); g.reload(); g.page.wait_for_timeout(150)
    g.click('[data-act=openFresh]') if g.page.query_selector('[data-act=openFresh]') else g.click('[data-act=open]'); g.page.wait_for_timeout(150)
    check(g.ev("!!S.rooms.up&&roomOpen('up')&&S.up.lease") is not None, 'kept across a reload')
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
    """rc6 C–E, AQ, AK, AT: not before the open floor has been lived on a while; 《大家待的地方》 needs the restaurant's
    people (eight on its list, three of them 熟手 or more — by tenure class, so the legacy crew's two or three counted
    days do not make them new), someone from outside introduced, two kinds of evidence. The project is offered after it,
    Phase I is built by the next opening (walls and a door on the floor, the room's own view from then), save/reload
    while building keeps it; II and III come later, in the same room (the first day never moves), the next day each;
    a trace that belongs to someone's story only after it happened; one big job on the floor at a time."""
    g = Game(b, port, target, seed=291, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day52.json')
    check(g.ev("eraOpen('sr')") is False and g.ev("srStoryReady()") is False, 'nothing before the floor is taken')
    _floor(g, 3)
    check(g.ev("eraOpen('sr')") is False, 'the open floor first: not three days after the lease')
    _floor(g, 8)
    check(g.ev("eraOpen('sr')") is True, 'a week after the lease the era is open')
    check(g.ev("srCrewOK()") is True and g.ev("(S.crew||[]).filter(m=>crewLegacy(m)&&(m.days||0)<=3).length") >= 8, 'the legacy crew count as the people they are, not as two-day hires')
    check(g.ev("upKinds(SP_KINDS)") == 2 and g.ev("srStoryReady()") is True, 'two kinds of evidence (the box, the seat): ready')
    g.ev("story().facts.yj_meet=null;delete story().facts.yj_meet")
    check(g.ev("srStoryReady()") is False, 'no one from outside introduced: not yet')
    _floor(g, 8)
    check(g.ev("secUpRooms(1e9,()=>'')") == '', 'nothing in 店舖工程 before the story')
    _upf(g, 'sr_story', 0)
    g.ev("S.money=600000")
    html = g.ev("secUpRooms(1e9,(c,a,k,l)=>`<b data-a=\"${a}\" data-k=\"${k}\">${l}</b>`)")
    check('員工休息室' in html and 'data-a="buySR" data-k="1"' in html and 'data-k="2"' not in html, f'Phase I offered, not II: {html[:300]}')
    d0 = g.ev("S.day")
    check(g.ev("buyRoomPhase('sr',1)") is True, 'bought')
    g.ev("hideReveal()")
    check(g.ev("srBuilding()&&!srBuilt()&&!roomOpen('staff')&&upWorks()==='sr'") is True, 'being built tonight; no room yet')
    check(g.ev("buyRoomPhase('sr',2)") is False, 'one thing at a time')
    _reload(g)
    check(g.ev("srOf().done") == d0 + 1 and g.ev("srBuilding()") is True, 'a reload keeps the works')
    g.ev("S.day+=1;IDLE=null")
    check(g.ev("srBuilt()&&roomOpen('staff')&&srStage()===1&&!upWorks()") is True, 'the next day: the room')
    check(g.ev("srTrace('cup')||srTrace('seat')||srTrace('yj')") is False, 'no one\'s things before their story')
    check(g.ev("String(drawSrShelf).includes(\"srTrace('cup')\")&&String(drawSrChair).includes(\"srTrace('seat')\")") is True, 'the drawings ask for the trace first')
    check(g.ev("buyRoomPhase('sr',2)") is False and g.ev("srWhyNot(2)").startswith('先讓大家用一陣子'), 'Phase II waits a few days')
    g.ev("S.day+=5")
    check(g.ev("buyRoomPhase('sr',2)") is True, 'Phase II')
    g.ev("hideReveal()")
    check(g.ev("srOf().done") == d0 + 1 and g.ev("srStage()") == 1, 'the same room; tomorrow it shows')
    g.ev("S.day+=1")
    check(g.ev("srStage()") == 2 and g.ev("srOf().done") == d0 + 1, 'II, in place')
    g.ev("S.day+=7")
    check(g.ev("buyRoomPhase('sr',3)") is True, 'Phase III')
    g.ev("hideReveal();S.day+=1")
    check(g.ev("srStage()") == 3 and g.ev("srOf().done") == d0 + 1, 'III, in place')
    _reload(g)
    check(g.ev("srStage()") == 3 and g.ev("roomOpen('staff')") is True, 'kept across a reload')
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
    check(g.ev("setRoom('up');forceDraw=true;__tick(1000/30);room") == 'up', 'the floor draws with them in it')
    check(g.ev("setRoom('staff');forceDraw=true;__tick(1000/30);room") == 'staff', 'the room draws')
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
    check(g.ev("secUpRooms(1e9,(c,a,k,l)=>a+':'+k).includes('buyPD:1')") is True, 'after it, Phase I')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc6_one_tab_for_the_floor_and_old_saves_get_nothing(b, port, target):
    """rc6 navigation and AP: with rooms on the floor the tabs keep one 二樓 (its label the room you are in; tapping it
    goes round the floor's rooms); every fixture save loads with no room, no booking, no story fact of these."""
    g = Game(b, port, target, seed=297, manual=True, viewport={'width': 390, 'height': 844})
    for f in sorted(os.listdir(os.path.join(ROOT, 'tests', 'saves'))):
        if not f.endswith('.json'): continue
        load_save(g, f)
        st = json.loads(g.ev("JSON.stringify({sr:!!(S.up&&S.up.sr),pd:!!(S.up&&S.up.pd),f:['sr_story','pd_yj','pd_story','sp_wait'].filter(k=>fact(k)),open:roomOpen('staff')||roomOpen('pdr')})"))
        check(not st['sr'] and not st['pd'] and not st['f'] and not st['open'], f'{f}: nothing of rc6 ({st})')
    load_save(g, 'player_day61.json')
    _floor(g, 50); g.ev(PD_OPEN)
    _quiet(g); to_service(g); _quiet(g)
    tabs = g.ev("[...document.querySelectorAll('#roomTabs button')].map(b=>b.dataset.room).join(',')")
    check('upgrp' in tabs and 'staff' not in tabs and 'pdr' not in tabs, f'one tab for the floor: {tabs}')
    # the player's 04:17 correction: Restaurant → 二樓 → a room; the tab is the floor, the rooms are behind their doors
    g.ev("setRoom('main')"); g.click('#roomTabs [data-room=upgrp]'); g.page.wait_for_timeout(40)
    check(g.ev("room") == 'up', 'the tab opens the floor')
    g.click('#roomTabs [data-room=upgrp]'); g.page.wait_for_timeout(40)
    check(g.ev("room") == 'up', 'and stays on the floor (no going round three rooms)')
    lab = lambda: g.ev("document.querySelector('#roomTabs [data-room=upgrp] span').textContent")
    check(lab() == '二樓', f'labelled 二樓 on the floor: {lab()}')
    tap = lambda x, y: g.ev(f"(()=>{{roomTap({{x:{x},y:{y}}},{{preventDefault(){{}}}});return room}})()")
    check(tap("UPR.pd.x0+60", "UPR.pd.y1-30") == 'pdr', 'the Private Dining Room\'s wall or door on the floor: in')
    check(lab() == '‹ 二樓', f'inside, the tab reads ‹ 二樓: {lab()}')
    check(tap("PDL.door.x", "LH-30") == 'up', 'its door at the near end: back to the floor')
    check(tap("UPR.srDoor.x", "UPR.sr.y1-30") == 'staff', 'the Staff Room\'s door: in')
    g.click('#roomTabs [data-room=upgrp]'); g.page.wait_for_timeout(40)
    check(g.ev("room") == 'up', 'the tab from inside a room: back to the floor')
    check(g.ev("(()=>{room='up';const k=new KeyboardEvent('keydown',{key:'ArrowRight'});document.dispatchEvent(k);return room})()") not in ('staff', 'pdr'), 'the arrow keys go over the top-level rooms only')
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
    sid = g.ev("(()=>{const c=CATS.find(o=>freeFloorCat(o));const c0=R.closing;R.closing=40;R.srCatId=c.def.id;const sp=upCatSpot(c);R.closing=c0;upCatForce(c);upCatUp(c,Object.assign(sp,{t:8}));return sp.room+'|'+c.def.id})()")
    check(sid.startswith('staff|'), f'the Staff Room spot after the crew: {sid}')
    cid = sid.split('|')[1]
    W2 = lambda cond, n=2500: g.ev(f"(()=>{{const c=catBy('{cid}');for(let i=0;i<{n};i++){{if({cond})return i;__tick(100)}}return -1}})()")
    check(W2("c.away==='staff'&&!c.upTo") >= 0, 'on the sofa')
    g.ev("setRoom('staff');forceDraw=true;__tick(1000/30)")
    check(W2("!upCatBusy(c)") >= 0, 'and back down')
    check(not g.errors, g.errors[:3]); g.close()


@test
def v24_rc6_the_open_floor_keeps_its_ways(b, port, target):
    """rc6 B, AT (circulation): with both rooms the open floor keeps the stairs, the middle, the column, the right window
    and the corner nobody has decided; the people walk from the stairs to each door and back round the column, never
    through a wall; the floor's view still draws its furniture and the cut walls."""
    g = Game(b, port, target, seed=299, manual=True, viewport={'width': 390, 'height': 844})
    load_save(g, 'player_day61.json')
    _floor(g, 50); g.ev(PD_OPEN)
    g.ev("(()=>{const p=pdW();p.ever=3;p.res={id:'r'+S.day,d:S.day,size:5,min:3800,kind:'x',type:'family',name:'x',t:.9,status:'missed',phase:1}})()")
    z = json.loads(g.ev("JSON.stringify((()=>{const P=UPR.pd,Q=UPR.sr,in_=(r,x,y)=>x>=r.x0&&x<=r.x1&&y>=r.y0&&y<=r.y1;const s=UP_L.stair,col=UP_L.col,win=UP_L.win[1],e=UP_L.entry;return{stairs:!in_(P,s.x,s.y)&&!in_(Q,s.x,s.y)&&!in_(P,s.x+s.w,s.y+s.h),col:!in_(P,col.x,col.base)&&!in_(Q,col.x,col.base),win:win.x>P.x1,entry:!in_(P,e.x,e.y)&&!in_(Q,e.x,e.y),corner:!in_(Q,UP_ZONES.undecided.x+UP_ZONES.undecided.w,UP_ZONES.undecided.y+UP_ZONES.undecided.h-1)||Q.y1<UP_ZONES.undecided.y+UP_ZONES.undecided.h}})())"))
    check(all(z.values()), f'the open floor keeps its parts: {z}')
    _quiet(g); to_service(g)
    g.ev("__botUntil('R.t>=R.dur*.1',90000,1/30)")
    # a walker from the stairs to each door and back: every step outside the rooms' boxes while on the floor
    for dest in ('staff', 'pdr'):
        r = json.loads(g.ev(f"""JSON.stringify((()=>{{const P=UPR.pd,Q=UPR.sr,inn=(r,x,y)=>x>r.x0+2&&x<r.x1-2&&y>r.y0+2&&y<r.y1-2;const w={{room:'up',x:UP_L.entry.x,y:UP_L.entry.y-4,troom:'{dest}',tx:{'200' if dest=='staff' else '300'},ty:{'srY(.5)' if dest=='staff' else 'pdY(.25)'},step:0,moving:false}};let bad=0,n=0;
          for(;n<3000;n++){{if(stepTo(w,105/30))break;if(w.room==='up'&&(inn(P,w.x,w.y)||inn(Q,w.x,w.y)))bad++}}const there=w.room==='{dest}';w.troom='up';w.tx=UP_L.entry.x;w.ty=UP_L.entry.y-4;let m=0;for(;m<3000;m++){{if(stepTo(w,105/30))break;if(w.room==='up'&&(inn(P,w.x,w.y)||inn(Q,w.x,w.y)))bad++}}return{{there,back:w.room==='up',bad,n,m}}}})())"""))
        check(r['there'] and r['back'] and r['bad'] == 0 and r['n'] < 3000 and r['m'] < 3000, f'stairs → {dest} → stairs, never through a wall: {r}')
    check(g.ev("setRoom('up');forceDraw=true;__tick(1000/30);room") == 'up', 'the floor draws')
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
    chips = g.ev("[...document.querySelectorAll('#screen .chips span')].map(e=>e.textContent).join('|')")
    check('包廂' in chips, f'and the chip on the summary: {chips}')
    check(not g.errors, g.errors[:3]); g.close()
