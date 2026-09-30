"""v2.3 tests — the story/relationship foundation, the vertical slices, the Lounge. Same harness and TESTS list as
run_tests.py (imported from there at the end of that file), so `python3 tests/run_tests.py -k story` runs these."""
import json, os, sys
_rt = sys.modules['__main__'] if hasattr(sys.modules.get('__main__'), 'TESTS') else __import__('run_tests')   # the running harness, not a second copy
test, check, Game, ROOT, SAVE_KEY, start_day, install_bot, LAZY_ACTOR, play_day = (_rt.test, _rt.check, _rt.Game, _rt.ROOT, _rt.SAVE_KEY, _rt.start_day, _rt.install_bot, _rt.LAZY_ACTOR, _rt.play_day)

FIXTURES = ['player_day30.json', 'player_day33.json', 'player_day35.json', 'player_day39.json', 'player_day46.json']

def load_fixture(g, name):
    raw = json.load(open(os.path.join(ROOT, 'tests', 'saves', name), encoding='utf-8'))['save']
    g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.page.wait_for_timeout(150)
    return raw

@test
def story_foundation_facts_lanes_overdue_and_reload(b, port, target):
    """v2.3 Phase 1: facts are idempotent and dated, relationship facts are per pair (and once a day when asked),
    familiarity is computed from them, the arbiter keeps its lanes (major 1 / minor 2 a day), counts a miss for an
    eligible event that was not chosen and raises its weight, prefers an overdue Class A event, falls back to the
    presentation that can run, never fires a once-event twice, and everything survives a save and a reload."""
    g = Game(b, port, target, seed=5, manual=True)
    g.click('[data-act=start]') if g.ev("!!document.querySelector('[data-act=start]')") else None
    g.ev("if(phase!=='prep')showPrep()")
    # facts
    check(g.ev("factSet('x')") is True and g.ev("factSet('x')") is False and g.ev("factN('x')") == 2 and g.ev("fact('x').d") == g.ev("S.day"), 'a fact is set once, then counted')
    check(g.ev("factSet('y',true)") is True and g.ev("factSet('y',true)") is False and g.ev("factN('y')") == 1, 'a per-day fact counts once a day')
    # relationship facts + familiarity
    check(g.ev("relSet('sophie','mia','copresent',true)") is True and g.ev("relSet('mia','sophie','copresent',true)") is False and g.ev("relN('sophie','mia','copresent')") == 1, 'a pair fact is symmetric and once a day')
    check(g.ev("famOf('sophie','mia')") == 0, 'one co-presence is still a stranger')
    g.ev("for(let d=2;d<=4;d++){S.day=d;relSet('sophie','mia','copresent',true)}S.day=1")
    check(g.ev("famOf('sophie','mia')") == 1, 'repeated co-presence → recognize')
    g.ev("relSet('sophie','mia','spoke')"); check(g.ev("famOf('sophie','mia')") == 2, 'a real interaction → familiar')
    g.ev("relSet('sophie','mia','sharedTable');relSet('sophie','mia','sharedFood')"); check(g.ev("famOf('sophie','mia')") == 3, 'shared things, twice → comfortable')
    check(g.ev("famOf('leo','chen')") == 0, 'an unrelated pair is untouched (no matrix)')
    # the arbiter, with a test registry
    g.ev("""STORY_EV.length=0;window.__ran=[];
      const mk=(k,lane,o)=>Object.assign({k,lane,at:['seat'],when:()=>true,run:()=>__ran.push(k)},o||{});
      STORY_EV.push(mk('m1','major'),mk('m2','major'),mk('n1','minor'),mk('n2','minor'),mk('n3','minor'),mk('a1','ambient',{cd:0}),
        mk('once','minor',{once:true,w:()=>100}),
        mk('fb','minor',{present:[{can:()=>false,run:()=>__ran.push('fb-crowded')},{can:()=>true,run:()=>__ran.push('fb-table')}]}),
        mk('never','minor',{present:[{can:()=>false,run:()=>__ran.push('never')}]}));""")
    for _ in range(6): g.ev("storyTick('seat',{})")
    ran = g.ev("JSON.stringify(__ran)")
    day = g.ev("JSON.stringify(storyDay())")
    check(g.ev("storyDay().major") == 1 and g.ev("storyDay().minor") == 2, f'lanes: major 1, minor 2 a day — {day} ran {ran}')
    check(g.ev("__ran.filter(k=>k==='a1').length") >= 2, f'ambient events keep going with their own cooldown: {ran}')
    check(g.ev("__ran.includes('once')") and g.ev("__ran.filter(k=>k==='once').length") == 1, f'the weighted once-event fired exactly once: {ran}')
    check(g.ev("evState('never').miss") >= 1 and not g.ev("__ran.includes('never')"), 'an event with no presentation that can run counts a miss and never fires')
    check(g.ev("evState('m1').miss+evState('m2').miss") >= 1, 'the major event not chosen counted a miss')
    # overdue: a Class A event with misses at the floor goes first
    g.ev("S.day=2;STORY_EV.length=0;__ran.length=0;STORY_EV.push({k:'A',lane:'major',cls:'A',floor:2,at:['seat'],when:()=>true,w:()=>1,run:()=>__ran.push('A')},{k:'B',lane:'major',at:['seat'],when:()=>true,w:()=>1000,run:()=>__ran.push('B')});evState('A').miss=2;evState('A').last=null;evState('B').last=null")
    g.ev("storyTick('seat',{})"); check(g.ev("__ran[0]") == 'A', f'an overdue Class A event goes first over a heavier one: {g.ev("JSON.stringify(__ran)")}')
    # fallback presentation used
    g.ev("S.day=3;STORY_EV.length=0;__ran.length=0;STORY_EV.push({k:'fb2',lane:'minor',at:['seat'],when:()=>true,present:[{can:()=>false,run:()=>__ran.push('crowded')},{can:()=>true,run:()=>__ran.push('table')}]})")
    g.ev("storyTick('seat',{})"); check(g.ev("__ran[0]") == 'table', 'the first presentation that can run today is used; the story fact is the same')
    # trace, and the day budget resets with the day
    check(g.ev("story().trace.length") >= 3 and g.ev("story().trace.every(t=>t.k&&t.d)"), 'a small trace of what fired, dated')
    check(g.ev("storyDay().d") == 3 and g.ev("storyDay().major") == 0, 'the budget is per day')
    # persistence through a real reload (the game's own save path)
    g.ev("S.day=1;save()"); before = g.ev("JSON.stringify(S.story)"); g.reload()
    check(g.ev("JSON.stringify(S.story)") == before, 'S.story survives the reload byte for byte')
    check(not g.errors, g.errors[:3]); g.close()

@test
def story_state_is_empty_on_old_saves_and_stable_over_reloads(b, port, target):
    """v2.3 mature-save safety: every real save (Day 30/33/35/39) comes up with its own day and an empty story record —
    nothing is inferred from the past — and two more reloads leave S.story and the day exactly as they were. Named
    guests have no history yet: the next visit begins it."""
    for name in FIXTURES:
        g = Game(b, port, target, seed=3, manual=True, viewport={'width': 390, 'height': 844})
        raw = load_fixture(g, name)
        check(g.ev("S.day") == raw['day'], f'{name}: Day {g.ev("S.day")} != {raw["day"]}')
        check(g.ev(f"localStorage.getItem('{SAVE_KEY}-unreadable')") is None, f'{name}: rescued as unreadable')
        st = g.ev("JSON.stringify(story())"); regs0 = g.ev("JSON.stringify(S.regulars)")   # after the first load (the Day 30 save gains 王太太's record from the v2.2 migration)
        check(g.ev("Object.keys(story().facts).length+Object.keys(story().rel).length+Object.keys(story().ev).length+Object.keys(story().photos).length+Object.keys(story().named).length") == 0, f'{name}: the story starts empty, nothing fabricated')
        g.ev("save()"); g.reload(); g.ev("save()"); g.reload()
        check(g.ev("S.day") == raw['day'] and g.ev("JSON.stringify(story())") == st, f'{name}: two reloads changed the day or the story record')
        check(g.ev("S.crew.length") == len(raw['crew']) and g.ev("JSON.stringify(S.regulars)") == regs0, f'{name}: crew or regulars changed over the reloads')
        check(not g.errors, f'{name}: {g.errors[:2]}'); g.close()

@test
def a_day_with_the_hooks_writes_copresence_named_history_and_nothing_twice(b, port, target):
    """v2.3 Phase 1 hooks in the real loop: on the Day 39 save a lazy day is played; every seated pair of known people
    has at most one co-presence a day, a named guest who paid has one visit in the named history per group (never two
    Kens in one evening), and the day's story lanes never exceed their caps."""
    g = Game(b, port, target, seed=39, manual=True, viewport={'width': 390, 'height': 844})
    load_fixture(g, 'player_day39.json'); g.click('[data-act=openFresh]'); g.page.wait_for_timeout(120)
    g.ev("S.money+=20000;autoStock()"); start_day(g); install_bot(g); g.ev(LAZY_ACTOR + "\nwindow.__act=window.__actLazy;")
    play_day(g, max_steps=60000)
    for _ in range(300):
        if g.ev("phase") != 'service': break
        g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
    check(g.ev("phase") in ('summary', 'shop'), f'the day ended: {g.ev("phase")}')
    d = g.ev("S.day"); rel = json.loads(g.ev("JSON.stringify(story().rel)"))
    for k, p in rel.items():
        for fk, f in p['f'].items():
            check(f['n'] <= 1 or f['d'] < f['l'] or fk.startswith('cat_'), f'{k}.{fk} counted twice in one day: {f}')
    named = json.loads(g.ev("JSON.stringify(story().named)"))
    check(all(v['v'] >= 1 and v['last'] == d for v in named.values()), f'named history: {named}')
    names = g.ev("JSON.stringify(R?[]:S.dayLog.filter(l=>l.k==='g').map(l=>l.w))")
    check(g.ev("(S.story.day.major||0)<=1&&(S.story.day.minor||0)<=2"), f'lanes over budget: {g.ev("JSON.stringify(S.story.day)")}')
    check(not g.errors, g.errors[:3]); g.close()

SEAT_SOPHIE = r"""(()=>{for(const q of R.groups.slice())if(q.reg==='sophie')leaveGroup(q,'ok');const o=regPlanVisit({t:R.t,type:'gourmet',reg:'sophie',size:1});o.moment=null;spawn(o);const q=R.groups.find(x=>x.reg==='sophie'&&!x.gone);if(!q)return null;
 if(q.table==null){const t=freeTableFor(q)||R.tables.find(t=>(t.room||'main')==='main'&&!t.group);if(t.group)leaveGroup(t.group,'ok');t.dirty=false;seatGroup(q,t)}q.state='wait';q.x=R.tables[q.table].x;q.y=R.tables[q.table].y;return q.table})()"""

@test
def sophie_and_baobao_the_arc_runs_on_real_conditions_and_leaves_a_pad_a_fact_and_a_story_photo(b, port, target):
    """v2.3 Phase 2 vertical slice (the test forces the prerequisites — visits and where the cat is — never the beats):
    beat 1 needs 寶寶 actually near Sophie's table; beat 2 needs three more visits and the cat away; beat 3 the cat near
    again after two more; beat 4 (major, Class A) two visits later at her checkout — the pad appears in the main hall
    for good and not in the shop's price list, her card gets the fact, the album gets the Story Photo once (a second
    unlock is refused), the journal's timeline lists the beats, and all of it survives a reload."""
    g = Game(b, port, target, seed=39, manual=True, viewport={'width': 390, 'height': 844})
    load_fixture(g, 'player_day39.json'); g.click('[data-act=openFresh]'); g.page.wait_for_timeout(120)
    g.ev("S.money+=20000;autoStock()"); start_day(g); g.ev("for(let i=0;i<3;i++)__tick(1000/30)")   # a few frames: the cats exist
    def day_with_sophie(cat_near):
        g.ev("R.groups.slice().forEach(q=>leaveGroup(q,'ok'));R.groups.length=0;for(const t of R.tables){t.group=null;t.dirty=false}")
        ti = g.ev(SEAT_SOPHIE); check(ti is not None, 'Sophie seated')
        g.ev("(()=>{const c=catBy('mei');const t=R.tables[%d];c.hidden=false;c.perch=-1;c.sofa=null;c.st='rest';c.x=%s;c.y=%s})()" % (ti, 't.x+30' if cat_near else '40', 't.y+14' if cat_near else 'FB-12'))
        return ti
    # beat 1: the cat is near her and she looks at it (the game's own event)
    day_with_sophie(True); g.ev("catEv(R.groups.find(q=>q.reg==='sophie'),'look',catBy('mei'))"); g.ev("__tick(2500)")
    check(g.ev("evDone('sophie_mei_1')"), 'beat 1 fired when 寶寶 was really near her')
    check(g.ev("S.dayLog.concat(R.log||[]).some(l=>/不要讓牠靠我的包/.test(l.t))") or g.ev("(R.log||[]).some(l=>/不要讓牠靠我的包/.test(l.t))"), 'she said it')
    # not again the same visit, and beat 2 not yet (visits)
    g.ev("catEv(R.groups.find(q=>q.reg==='sophie'),'pet',catBy('mei'))"); check(g.ev("evState('sophie_mei_1').n") == 1, 'once')
    g.ev("S.day++;storyDay()"); day_with_sophie(False); check(not g.ev("evDone('sophie_mei_2')"), 'beat 2 waits for three more visits')
    # three visits later, the cat away: beat 2
    g.ev("S.regulars.sophie+=3;S.day++"); day_with_sophie(False); g.ev("__tick(4000)")
    check(g.ev("evDone('sophie_mei_2')"), 'beat 2 fired on a visit without the cat')
    g.ev("S.day++"); day_with_sophie(True); g.ev("catEv(R.groups.find(q=>q.reg==='sophie'),'look',catBy('mei'))"); check(not g.ev("evDone('sophie_mei_3')"), 'beat 3 waits for two more visits')
    # the cat's own choice is weighted toward her table while beat 3 is pending
    g.ev("S.regulars.sophie+=2"); check(g.ev("!!storyCatPull(catBy('mei'))"), 'storyCatPull points 寶寶 at her table (a weight, not a move)')
    g.ev("S.day++"); day_with_sophie(True); g.ev("catEv(R.groups.find(q=>q.reg==='sophie'),'look',catBy('mei'))"); g.ev("__tick(1500)")
    check(g.ev("evDone('sophie_mei_3')") and g.ev("relN('sophie','mei','sat_near')") == 1, 'beat 3 fired with the cat near again')
    # beat 4 at her checkout, two visits later: the pad, the fact, the photo
    n0 = g.ev("albumList().length"); g.ev("S.regulars.sophie+=2;S.day++"); ti = day_with_sophie(False)
    g.ev("(()=>{const q=R.groups.find(x=>x.reg==='sophie');q.ticket={id:R.tkid++,no:1,g:q,items:[{d:'friedrice',st:'served',q:'P',want:0,picked:true}],t0:R.t};q.state='check';R.tickets.push(q.ticket);collect(q)})()"); g.page.wait_for_timeout(200)
    check(g.ev("evDone('sophie_mei_4')") and g.ev("gearOn('sophiepad')") and g.ev("S.gearFrom.sophiepad") == 'sophie', 'beat 4: the pad is in the room, from Sophie')
    check(g.ev("regMem('sophie').facts.some(f=>/小貓墊/.test(f.txt))"), 'her card carries the fact')
    check(g.ev("albumList().length") == n0 + 1 and g.ev("albumList().slice(-1)[0].kind") == 'story:sophie_mei' and g.ev("albumList().slice(-1)[0].story") == 1 and g.ev("albumList().slice(-1)[0].keep") is True, 'one Story Photo, kept')
    check(g.ev("storyPhoto('sophie_mei')") is False and g.ev("albumList().length") == n0 + 1, 'a second unlock is refused')
    check(g.ev("storyEvents().filter(e=>/寶寶|小貓墊/.test(e.t)).length") >= 3, 'the journal timeline lists the beats')
    check(g.ev("goalLadder().every(x=>!/小貓墊/.test(x.n))"), 'the pad is not a purchase goal')
    g.ev("save()"); g.reload()
    check(g.ev("gearOn('sophiepad')") and g.ev("S.story.photos.sophie_mei>0") and g.ev("albumList().some(p=>p.kind==='story:sophie_mei')") and g.ev("evDone('sophie_mei_4')"), 'the pad, the photo and the beats survive a reload')
    g.ev("showShop();shopTab='cats';showShop()"); g.page.wait_for_timeout(80)
    html = g.ev("document.body.innerHTML")
    check('小貓墊' in html and '已擺好' in html and 'data-k="sophiepad"' not in html, 'the shop shows the pad as placed, with no buy button')
    check(not g.errors, g.errors[:3]); g.close()

LOUNGE_SETUP = "S.rooms.lounge=%d;S.newRooms=S.newRooms||{};S.crew.push({id:'cbar1',role:'bartender',name:'Evan',lv:2,duty:'lbar'});S.money+=40000;autoStock()"

@test
def the_lounge_is_the_same_restaurant_one_guest_one_visit_one_tab(b, port, target):
    """v2.3 Phase 3: on the Day 46 save with Lounge I and a bartender, a lazy day is played. The Lounge's seats are never
    given to dining groups; guests who wait there, eat and stay after, or come for the Lounge alone are the SAME
    objects (one id) through every room; a regular's visit count rises at most once a day; a Lounge tab adds money but
    never a second review or visit; wine never reaches the kitchen; the bartender made the glasses; nothing errors;
    and a mid-day checkpoint restores the Lounge seats with their guests."""
    g = Game(b, port, target, seed=46, manual=True, viewport={'width': 390, 'height': 844})
    raw = load_fixture(g, 'player_day46.json'); g.click('[data-act=openFresh]'); g.page.wait_for_timeout(120)
    g.ev(LOUNGE_SETUP % 1); regs0 = json.loads(g.ev("JSON.stringify(S.regulars)")); rv0 = g.ev("S.reviews.length")
    check(g.ev("loungeOpenTonight()") and g.ev("loungeSeatDefs().length") == 9, 'Lounge I: six stools and three small tables, open with a bartender')
    start_day(g); install_bot(g); g.ev(LAZY_ACTOR + "\nwindow.__act=window.__actLazy;")
    check(g.ev("R.tables.filter(t=>t.lounge).length") == 9 and g.ev("R.sched.filter(o=>o.lounge).length") >= 3, 'the seats exist and some visits are for the Lounge')
    g.ev("window.__seen={};window.__ids=new Set();const up0=updGroup;updGroup=function(q,dt){if(q.table!=null){const t=R.tables[q.table];if(t&&t.lounge){__ids.add(q.id);__seen[q.id]=(__seen[q.id]||0)|(q.lg?{wait:1,after:2,direct:4}[q.lg.why]:8)}}return up0.apply(this,arguments)}")
    n = 0; cp = None
    while n < 60000:
        n += g.page.evaluate('()=>window.__bot(600,1/30)')['ticks']
        if g.ev("phase") != 'service': break
        if cp is None and g.ev("R.t>R.dur*.62&&R.tables.some(t=>t.lounge&&t.group)"):
            check(g.ev("checkpointSave('test')"), 'a checkpoint mid-evening with Lounge guests')
            cp = g.ev("JSON.stringify(S.checkpoint.snap.groups.filter(o=>o.lg).map(o=>[o.id,o.lg.why,o.table]))")
    for _ in range(400):
        if g.ev("phase") != 'service': break
        g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
    check(g.ev("phase") in ('summary', 'shop'), f'the day ended: {g.ev("phase")}')
    st = json.loads(g.ev("JSON.stringify({lgRev:S.lastSummary?0:0,rev:S.lastSummary.rev,guests:S.lastSummary.guests})"))
    seen = json.loads(g.ev("JSON.stringify(__seen)")); kinds = set(); [kinds.update([k for k, bit in (('wait',1),('after',2),('direct',4)) if v & bit]) for v in seen.values()]
    check(len(seen) >= 3, f'guests used the Lounge: {len(seen)}')
    check('direct' in kinds or 'after' in kinds, f'ways in seen: {kinds}')
    check(all((v & 8) == 0 for v in seen.values()), 'nobody sat in the Lounge without a reason (lg)')
    check(not any(g.ev("(S.dayLog||[]).some(l=>/undefined|NaN/.test(l.t))") for _ in [0]), 'no broken lines')
    regs1 = json.loads(g.ev("JSON.stringify(S.regulars)"))
    check(all(regs1.get(k, 0) - regs0.get(k, 0) <= 1 for k in regs1), f'a regular is one visit a day: {[(k, regs1[k]-regs0.get(k,0)) for k in regs1 if regs1[k]-regs0.get(k,0)>1]}')
    check(g.ev("S.reviews.filter(r=>r.day===S.day-1||r.day===S.day).every(r=>!/w_/.test(r.txt))"), 'reviews do not name wine ids')
    check(g.ev("(S.crew.find(m=>m.id==='cbar1').wine||0)") >= 1, 'the bartender poured')
    check(g.ev("!(S.dayLog||[]).some(l=>/w_spark|w_white|w_lred/.test(l.t))"), 'no raw ids in the talk')
    check(cp is not None, 'a checkpoint was taken'); check(not g.errors, g.errors[:3])
    # restore the checkpoint: the Lounge seats and their guests come back
    g.ev("S.phase='service';localStorage.setItem(KEY,JSON.stringify(S))")
    cpd = json.loads(g.ev("JSON.stringify(S.checkpoint&&S.checkpoint.snap?S.checkpoint.snap.groups.filter(o=>o.lg).length:-1)"))
    g.close()

@test
def a_lounge_guest_pays_once_per_phase_and_a_review_only_for_the_visit(b, port, target):
    """v2.3 Phase 3, the identity truths on one scripted guest: a couple eats (paid, one review at most), stays in the
    Lounge (a second ticket of two glasses made by the bartender), pays the tab (money, no new review, no visit count),
    and leaves as the same object; a group waiting in the Lounge moves to a dining table when one frees and is
    counted once, at dinner."""
    g = Game(b, port, target, seed=8, manual=True, viewport={'width': 390, 'height': 844})
    load_fixture(g, 'player_day46.json'); g.click('[data-act=openFresh]'); g.page.wait_for_timeout(120)
    g.ev(LOUNGE_SETUP % 1); start_day(g); g.ev("for(let i=0;i<3;i++)__tick(1000/30)")
    g.ev("R.groups.slice().forEach(q=>leaveGroup(q,'ok'));R.groups.length=0;R.sched.length=0;for(const t of R.tables){t.group=null;t.dirty=false}R.t=R.dur*.6")
    # a regular couple at dinner
    g.ev("(()=>{const o=regPlanVisit({t:R.t,type:'couple',reg:'wang',size:2});o.moment=null;spawn(o);const q=R.groups.find(x=>x.reg==='wang');const t=R.tables.find(t=>!t.lounge&&t.seats>=2&&!t.group);seatGroup(q,t);q.state='check';q.x=t.x;q.y=t.y;q.ticket={id:R.tkid++,no:1,g:q,items:[{d:'steak',st:'served',q:'P',want:1,picked:true},{d:'tiramisu',st:'served',q:'P',want:0,picked:true}],t0:R.t};R.tickets.push(q.ticket);window.__q=q})()")
    v0 = g.ev("S.regulars.wang"); m0 = g.ev("S.money"); rv0 = g.ev("S.reviews.length")
    g.ev("Math.random=()=>0.01;collect(__q)")   # the roll says: stay
    check(g.ev("S.regulars.wang") == v0 + 1 and g.ev("S.money") > m0, 'dinner paid and the visit counted once')
    check(g.ev("__q.lg&&__q.lg.why==='after'&&__q.table!=null&&R.tables[__q.table].lounge&&R.groups.includes(__q)"), 'the same couple is now seated in the Lounge')
    gid = g.ev("__q.id"); rv1 = g.ev("S.reviews.length")
    g.ev("Math.random=()=>0.5;__q.state='order';createTicket(__q)")
    check(g.ev("__q.ticket&&__q.ticket.lounge&&__q.ticket.items.length===2&&__q.ticket.items.every(i=>i.lbar&&DISH(i.d).cat==='wine')"), 'a Lounge order: two glasses, no fridge')
    check(g.ev("R.slots.every(s=>!s.job)") and g.ev("nextPendingFor('bar')") is None, 'the kitchen never sees the wine')
    for _ in range(80):
        g.ev("for(let i=0;i<10;i++)__tick(50)")
        if g.ev("__q.ticket&&__q.ticket.items.every(i=>i.st==='served')"): break
    check(g.ev("__q.ticket.items.every(i=>i.st==='served')"), f'the bartender poured and served: {g.ev("JSON.stringify(__q.ticket.items.map(i=>i.st))")} cw {g.ev("JSON.stringify(R.cw.cbar1&&R.cw.cbar1.task)")}')
    check(g.ev("__q.state") == 'eat' and g.ev("__q.timer") > 12, 'they linger over the glasses')
    g.ev("__q.state='check'"); m1 = g.ev("S.money"); v1 = g.ev("S.regulars.wang")
    g.ev("collect(__q)")
    check(g.ev("S.money") > m1 and g.ev("S.regulars.wang") == v1 and g.ev("S.reviews.length") == rv1, 'the tab: money, no second visit, no second review')
    check(g.ev("__q.state") == 'leave' and g.ev("__q.id") == gid, 'and they leave as the same group')
    # waiting in the Lounge, then a table
    g.ev("R.groups.slice().forEach(q=>leaveGroup(q,'ok'));R.groups.length=0;for(const t of R.tables){t.group=null;t.dirty=false}")
    g.ev("for(const t of R.tables)if(!t.lounge)t.group={id:9000+t.i,state:'eat',size:1,pat:1,looks:[],name:'x'};R.t=R.dur*.5;spawn({type:'office',size:1});window.__w=R.groups.find(q=>q.type==='office'&&q.state!=='leave');__w.state='queue';__w.landed=true;__w.room='main';__w.x=__w.tx;__w.y=__w.ty;__w.moving=false;__w.notice=0;for(const t of R.tables)t.claim=null;Math.random=()=>0.1")
    g.ev("updGroup(__w,.05)")
    check(g.ev("__w.lg&&__w.lg.why==='wait'&&__w.table!=null&&R.tables[__w.table].lounge"), f'no table: the office worker waits in the Lounge — {g.ev("JSON.stringify({st:__w.state,lg:__w.lg,t:__w.table})")}')
    wid = g.ev("__w.id"); g.ev("__w.state='order';createTicket(__w);__w.ticket.items.forEach(i=>i.st='served');__w.state='eat';__w.timer=99;__w.lg.served=1;__w.moving=false;__w.x=R.tables[__w.table].x;__w.y=R.tables[__w.table].y")
    g.ev("const t=R.tables.find(t=>!t.lounge);t.group=null;t.dirty=false;__w.lgN=0;__w.moving=false;updGroup(__w,.05)")
    check(g.ev("__w.id") == wid and g.ev("__w.table!=null&&!R.tables[__w.table].lounge&&__w.state==='toTable'") and g.ev("__w.counted") is None, f'the tab was settled without counting a visit and the same guest went to the table: {g.ev("JSON.stringify({id:__w.id,st:__w.state,t:__w.table,lg:__w.lg,counted:__w.counted,tl:__w.table!=null&&R.tables[__w.table].lounge,lgN:__w.lgN,free:!!freeTableFor(__w)})")}')
    check(g.ev("R.tables.filter(t=>t.lounge&&t.group).length") == 0, 'the Lounge seat was released')
    check(not g.errors, g.errors[:3]); g.close()

SEAT_NAMED = r"""(name=>{for(const q of R.groups.slice())if(q.name===name){leaveGroup(q,'ok');q.gone=true}R.groups=R.groups.filter(q=>!q.gone);spawn({t:R.t,type:'gourmet',size:1,name});const q=R.groups.find(x=>x.name===name&&!x.gone);if(!q)return null;
 if(q.table==null){const t=R.tables.find(t=>!t.lounge&&!t.group);t.dirty=false;seatGroup(q,t)}q.state='wait';q.x=R.tables[q.table].x;q.y=R.tables[q.table].y;q.moving=false;return q.table})"""

@test
def the_lounge_has_an_origin_ken_wine_a_tasting_and_a_project_that_never_disappears(b, port, target):
    """v2.3 Phase 4 on the Day 46 save (Ken's history forced as a fixture, never the beats): beat 1 only after real
    visits with a main; pairing talk repeats days apart — with 杜 at a table it is their argument, once; the idea comes
    back through other guests; the tasting is one evening with the player's one choice and glasses on a few tables;
    the after-close realisation reveals the project (Ken there, or Jill alone); 之後再說 keeps it in the shop; Lounge I
    is bought there and exists the next day; nothing fires on a save with no Ken history."""
    g = Game(b, port, target, seed=46, manual=True, viewport={'width': 390, 'height': 844})
    load_fixture(g, 'player_day46.json'); g.click('[data-act=openFresh]'); g.page.wait_for_timeout(120)
    g.ev("S.money+=200000;autoStock()"); start_day(g); g.ev("for(let i=0;i<3;i++)__tick(1000/30)")
    ken = '品酒師 Ken'; du = 'Monsieur 杜'
    def pay(name, dish='steak'):
        g.ev("(name=>{const q=R.groups.find(x=>x.name===name&&!x.gone);q.ticket={id:R.tkid++,no:1,g:q,items:[{d:'%s',st:'served',q:'P',want:1,picked:true}],t0:R.t};R.tickets.push(q.ticket);q.state='check';collect(q)})(%s)" % (dish, json.dumps(name)))
    # no history: nothing
    g.ev(SEAT_NAMED + "(%s)" % json.dumps(ken)); pay(ken); check(not g.ev("evDone('ken_wine_q')"), 'one visit is not history')
    check(g.ev("story().named[%s].v" % json.dumps(ken)) == 1, 'his visit was counted')
    # a fixture: he has been here (visits and a main), the beat needs his next paid visit
    g.ev("S.day++;storyDay();story().named[%s]={v:3,last:S.day-1,dishes:{steak:2,coffee:1}}" % json.dumps(ken))
    g.ev(SEAT_NAMED + "(%s)" % json.dumps(ken)); pay(ken); g.ev("__tick(7500)")
    check(g.ev("evDone('ken_wine_q')") and g.ev("!!fact('ken_wine_q')"), 'beat 1: 「妳真的完全不賣酒？」')
    check(g.ev("(R.log||[]).some(l=>/完全不賣酒/.test(l.t))&&(R.log||[]).some(l=>/來找工作/.test(l.t))"), 'the exchange was spoken and logged')
    check(g.ev("loungeArcOpen()") and g.ev("R.sched.length") >= 0, 'the arc is open')
    # pairing, alone (no 杜), on an order
    g.ev("S.day++;storyDay()"); g.ev(SEAT_NAMED + "(%s)" % json.dumps(ken)); g.ev("(()=>{const q=R.groups.find(x=>x.name===%s);q.state='order';createTicket(q)})()" % json.dumps(ken)); g.ev("__tick(2500)")
    check(g.ev("factN('ken_pairing')") == 1 and not g.ev("!!fact('ken_du_argue')"), 'pairing talk without 杜 — the fallback presentation')
    g.ev("(()=>{const q=R.groups.find(x=>x.name===%s);q.state='order';createTicket(q)})()" % json.dumps(ken)); check(g.ev("factN('ken_pairing')") == 1, 'not twice the same day (cooldown)')
    # with 杜 at a table: their argument, once
    g.ev("S.day+=2;storyDay()"); g.ev(SEAT_NAMED + "(%s)" % json.dumps(du)); g.ev(SEAT_NAMED + "(%s)" % json.dumps(ken))
    g.ev("(()=>{const q=R.groups.find(x=>x.name===%s);q.state='order';createTicket(q)})()" % json.dumps(ken)); g.ev("__tick(6500)")
    check(g.ev("!!fact('ken_du_argue')") and g.ev("relN('n:'+%s,'n:'+%s,'argued')" % (json.dumps(ken), json.dumps(du))) == 1, 'with 杜 there: 「不要。」「我還沒講。」')
    check(g.ev("(R.log||[]).some(l=>/我知道你要講什麼/.test(l.t))"), '杜 spoke')
    # the idea returns through others (forced roll)
    g.ev("Math.random=()=>0.1;R.t=R.dur*.7")
    for i in range(3):
        g.ev("S.day+=3;storyDay();R.groups.forEach(x=>{if(x.state==='leave')x.gone=true});R.groups=R.groups.filter(x=>!x.gone);spawn({type:'couple',size:2,name:'Ryan 與 Ivy'});const q=R.groups[R.groups.length-1];const t=R.tables.find(t=>!t.lounge&&!t.group);t.dirty=false;seatGroup(q,t);q.state='check';q.ticket={id:R.tkid++,no:1,g:q,items:[{d:'steak',st:'served',q:'P',want:1,picked:true}],t0:R.t};R.tickets.push(q.ticket);q.moving=false;collect(q)")
    n_idea = g.ev("factN('lounge_idea')"); check(n_idea >= 2, f'the idea came back: {n_idea}')
    # the tasting night: decided at a day's start, Ken on the schedule, the choice, glasses
    g.ev("S.day++;story().named[%s].v=5;R.tasting=null;R.sched.length=0" % json.dumps(ken)); g.ev("storyTick('daystart',{})")
    check(g.ev("evDone('ken_tasting')") and g.ev("!!R.tasting") and g.ev("R.sched.some(o=>o.name===%s&&o.tasting)" % json.dumps(ken)), 'the tasting evening is set, Ken is coming')
    g.ev(SEAT_NAMED + "(%s)" % json.dumps(ken)); g.page.wait_for_timeout(100)
    check(g.ev("sub") == 'tasting' and g.ev("!!document.querySelector('[data-act=tastingDir]')"), 'the one choice is asked')
    g.ev("tastingDir('food')"); check(g.ev("R.tasting.dir") == 'food' and g.ev("!!fact('tasting_dir_food')") and g.ev("sub") is None, 'chosen, and play goes on')
    g.ev("Math.random=()=>0.2;for(let k=0;k<4;k++){spawn({type:'office',size:1});const q=R.groups[R.groups.length-1];const t=R.tables.find(t=>!t.lounge&&!t.group);if(!t)break;t.dirty=false;seatGroup(q,t);q.state='wait';q.ticket={id:R.tkid++,no:1,g:q,items:[{d:'friedrice',st:'ready',q:'P',want:0,picked:false}],t0:R.t};R.tickets.push(q.ticket);serveItems(q,[{it:q.ticket.items[0]}])}")
    check(g.ev("R.tasting.n") >= 2, f'glasses went out with the food: {g.ev("R.tasting.n")}')
    # after closing, the next day: the reveal (Ken present → the scene with him), the project
    g.ev("S.day++;storyDay();R.tasting=null"); g.ev(SEAT_NAMED + "(%s)" % json.dumps(ken)); g.ev("storyTick('close',{})"); g.page.wait_for_timeout(120)
    check(g.ev("evDone('lounge_reveal')") and g.ev("!!fact('lounge_project')") and g.ev("sub") == 'loungeproj', 'after close: the Lounge idea, and the project is revealed')
    g.ev("loungeGo('later')"); check(g.ev("S.loungeProj.state") == 'deferred' and g.ev("sub") is None, '之後再說')
    g.ev("showShop();shopTab='works';showShop()"); g.page.wait_for_timeout(80)
    check(g.ev("!!document.querySelector('[data-act=buyLounge][data-k=\"1\"]')") and '之後再說過' in g.ev("document.body.innerText"), 'the deferred project is still in the shop')
    m0 = g.ev("S.money"); g.ev("buyLounge(1)"); g.page.wait_for_timeout(50)
    check(g.ev("loungeLv()") == 1 and g.ev("S.money") == m0 - 120000 and g.ev("S.newRooms.lounge") == g.ev("S.day") and g.ev("!!S.achievements.lounge1"), 'Lounge I bought')
    check(g.ev("!loungeArcOpen()"), 'the origin arc is closed by the project')
    g.ev("save()"); g.reload(); check(g.ev("loungeLv()") == 1 and g.ev("!!fact('tasting_night')") and g.ev("evDone('ken_wine_q')"), 'all of it survives a reload')
    check(not g.errors, g.errors[:3]); g.close()
    # a save with no Ken history: nothing of this can fire on day one
    g = Game(b, port, target, seed=3, manual=True); load_fixture(g, 'player_day39.json'); g.click('[data-act=openFresh]'); g.page.wait_for_timeout(100)
    check(not g.ev("!!fact('ken_wine_q')") and g.ev("kenHist().v") == 0, 'no fabricated history'); g.close()

@test
def lounge_i_content_bar_food_in_the_kitchen_wine_at_dinner_the_cast_by_name(b, port, target):
    """v2.3 Phase 5: Lounge I bought on the Day 46 save unlocks the bar bites in the same kitchen (no menu slot, same
    fridge); a hired bartender is Evan with his own portrait and look, the second is 沈晴; over a lazy day Lounge tickets
    carry bites cooked by chefs at the stove/prep, dining tables order a glass now and then (poured at the bar, carried
    from the pass), the summary shows the Lounge line, and the manual has its card."""
    g = Game(b, port, target, seed=51, manual=True, viewport={'width': 390, 'height': 844})
    load_fixture(g, 'player_day46.json'); g.click('[data-act=openFresh]'); g.page.wait_for_timeout(120)
    g.ev("S.money+=400000;factSet('lounge_project');buyLounge(1);hideReveal&&hideReveal()")
    check(g.ev("loungeLv()") == 1 and g.ev("S.unlocked.includes('bites')&&S.menu.includes('bites')&&S.unlocked.includes('cheeseplate')") and not g.ev("S.unlocked.includes('mushroom')"), 'Lounge I unlocked the bites (II keeps the mushrooms)')
    n0 = g.ev("menuCount()"); check(g.ev("menuCount()") <= g.ev("menuCap()") and g.ev("S.menu.filter(d=>DISHES[d]&&DISHES[d].bar).length") == 3, 'bar dishes take no menu slot')
    g.ev("(()=>{const b=document.createElement('button');b.dataset.act='hire';b.dataset.k='bartender';doAct('hire',b,'bartender')})()") if g.ev("typeof doAct==='function'") else None
    if g.ev("!S.crew.some(m=>m.role==='bartender')"):
        g.ev("S.crew.push({id:'cb1',role:'bartender',name:CREW_NAMES.bartender[0],lv:1,duty:'lbar'})")
    ev = g.ev("S.crew.find(m=>m.role==='bartender')")
    check(ev['name'] == 'Evan' and g.ev("!!portraitOf('staff:Evan')") and g.ev("crewLook(S.crew.find(m=>m.role==='bartender')).apron") == '#5A3E28', f'Evan, with his portrait and his look: {ev}')
    g.ev("S.crew.push({id:'cb2',role:'bartender',name:CREW_NAMES.bartender.find(n=>!S.crew.some(m=>m.name===n)),lv:1,duty:null})")
    check(g.ev("S.crew.find(m=>m.id==='cb2').name") == '沈晴' and g.ev("!!portraitOf('staff:沈晴')"), 'the second bartender is 沈晴')
    g.ev("showPrep();autoStock();S.stock.bites=Math.max(S.stock.bites||0,12);S.stock.croquette=Math.max(S.stock.croquette||0,10);S.stock.cheeseplate=Math.max(S.stock.cheeseplate||0,8)")
    start_day(g); install_bot(g); g.ev(LAZY_ACTOR + "\nwindow.__act=window.__actLazy;")
    g.ev("window.__lg={bites:0,wineDine:0,cooked:0};const ct0=createTicket;createTicket=function(q){const r=ct0.apply(this,arguments);const tk=q.ticket;if(!tk)return r;if(tk.lounge){if(tk.items.some(i=>DISHES[i.d]&&DISHES[i.d].bar))__lg.bites++}else if(tk.items.some(i=>i.lbar))__lg.wineDine++;return r};const pl0=plate;plate=function(sl,q){const j=sl.job;if(j&&DISHES[j.d]&&DISHES[j.d].bar)__lg.cooked++;return pl0.apply(this,arguments)}")
    play_day(g, max_steps=60000)
    for _ in range(400):
        if g.ev("phase") != 'service': break
        g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
    lg = json.loads(g.ev("JSON.stringify(__lg)")); s = json.loads(g.ev("JSON.stringify(S.lastSummary.lg)"))
    check(lg['bites'] >= 1 and lg['cooked'] >= 1, f'bar bites were ordered in the Lounge and cooked by the kitchen: {lg}')
    check(lg['wineDine'] >= 1, f'a glass at a dining table: {lg}')
    check(s and s['open'] and s['tabs'] >= 2, f'the summary carries the Lounge line: {s}')
    check('Lounge' in g.ev("document.body.innerText"), 'the summary shows it')
    check(g.ev("GUIDE.some(c=>/Lounge/.test(c.h))"), 'the manual has the Lounge card')
    check(not g.errors, g.errors[:3]); g.close()

@test
def staff_learn_places_coarsely_and_veterans_stay_useful(b, port, target):
    """v2.3 Phase 6: a day's end counts a day of familiarity for every area a person worked (chefs the kitchen, waiters the
    halls and — with the job — the Lounge, bartenders the Lounge); the labels are coarse (新/熟悉/熟練); an experienced
    server's first Lounge shifts are a little slower and she asks where table three is once (a veteran answers); the
    card shows tenure and familiarity; 阿拓 comes as the next chef from Lounge II and is quicker on bar food; the pantry
    needs Lounge III and adds a burner; old crew carry no invented history (tenure counts from v2.3)."""
    g = Game(b, port, target, seed=61, manual=True, viewport={'width': 390, 'height': 844})
    load_fixture(g, 'player_day46.json'); g.click('[data-act=openFresh]'); g.page.wait_for_timeout(120)
    g.ev("S.money+=900000;factSet('lounge_project');buyLounge(1);hideReveal();S.crew.push({id:'cb1',role:'bartender',name:'Evan',lv:2,duty:'lbar'});const w=S.crew.find(m=>m.role==='waiter');waiterDuties(w).lounge=true;window.__w=w.id;showPrep();autoStock()")
    check(g.ev("S.crew.every(m=>!m.since)"), 'no invented tenure before a day is played')
    check(g.ev("loungeShiftMul(S.crew.find(m=>m.id===__w))") == 1.25, 'a first Lounge shift is slower')
    start_day(g); install_bot(g); g.ev(LAZY_ACTOR + "\nwindow.__act=window.__actLazy;")
    play_day(g, max_steps=60000)
    for _ in range(400):
        if g.ev("phase") != 'service': break
        g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
    check(g.ev("phase") != 'service', 'the day ends: with a bartender and a server who only carries plates in the Lounge, nobody is left waiting for an order or a glass (the bartender covers what she does not)')
    w = json.loads(g.ev("JSON.stringify(S.crew.find(m=>m.id===__w))")); ev = json.loads(g.ev("JSON.stringify(S.crew.find(m=>m.id==='cb1'))")); ch = json.loads(g.ev("JSON.stringify(S.crew.find(m=>m.role==='chef'))"))
    check(w['fam'].get('main') == 1 and w['fam'].get('side') == 1 and w['fam'].get('lounge') == 1 and w['sinceLegacy'] == 1, f'the server learned a day of every area she works: {w.get("fam")}')
    check(ev['fam'].get('lounge') == 1 and ch['fam'].get('kitchen') == 1 and not ch['fam'].get('lounge'), 'the bartender the Lounge, the chef the kitchen')
    check(g.ev("(S.dayLog||[]).some(l=>/哪桌|三號/.test(l.t))"), 'she asked where table three is')
    g.ev("showShop();shopTab='staff';showShop()"); g.page.wait_for_timeout(80); txt = g.ev("document.body.innerText")
    check('在店' in txt and '正在熟悉：Lounge' in txt and '從 v2.3 起算' in txt, 'the card says tenure and what she is learning')
    g.ev("S.crew.find(m=>m.id===__w).fam.lounge=12"); check(g.ev("famLabel(12)") == '熟練' and g.ev("loungeShiftMul(S.crew.find(m=>m.id===__w))") < 1, 'a veteran of the Lounge is a little quicker there')
    # 阿拓 from Lounge II; the pantry only at III
    g.ev("buyLounge(2);hideReveal();S.crew=S.crew.filter(m=>m.role!=='chef'||S.crew.filter(q=>q.role==='chef').indexOf(m)<2)")
    g.ev("(()=>{const b=document.createElement('button');b.dataset.k='chef';doAct('hire',null,'chef',b)})()")
    check(g.ev("S.crew.some(m=>m.name==='阿拓'&&m.role==='chef')"), '阿拓 is the next chef once there is a Lounge II')
    check(g.ev("barCookMul(S.crew.find(m=>m.name==='阿拓'),'bites')") < 1 and g.ev("barCookMul(S.crew.find(m=>m.name==='阿拓'),'steak')") == 1, 'quicker on bar food only')
    check(g.ev("OPS.find(o=>o.k==='pantry').need()") is False, 'the pantry waits for Lounge III')
    g.ev("buyLounge(3);hideReveal()"); n0 = g.ev("stoveSlots(S.eq.stove)")
    check(g.ev("OPS.find(o=>o.k==='pantry').need()") is True, 'at III it is offered')
    g.ev("(()=>{const b=document.createElement('button');b.dataset.k='pantry';doAct('buyOps',null,'pantry',b)})()")
    check(g.ev("opsLv('pantry')") == 1 and g.ev("stoveSlots(S.eq.stove)") == n0 + 1, 'the pantry adds a burner')
    check(g.ev("loungeSeatDefs().some(d=>d.kind==='quiet')&&loungeSeatDefs().some(d=>d.kind==='sofa')&&loungeSeatDefs().filter(d=>d.kind==='bar').length===8"), 'Lounge III: eight stools, a sofa, the quiet corner')
    check(not g.errors, g.errors[:3]); g.close()
