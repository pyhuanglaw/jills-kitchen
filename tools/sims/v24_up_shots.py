"""v2.4 rc5 visual checkpoints for the Second Floor, at phone size (390x844), from the player's Day 52 save played for
real: the story facts before each beat are set as if the earlier beats had happened (the dates moved so the beat is
due), then the day is played by the bot and the moment is photographed as it happens. Writes PNGs and shots.txt to
docs/evidence/v24_rc5/ (or the folder given).

  python3 tools/sims/v24_up_shots.py [out_dir] [part=all|night|ask|floor]
"""
import sys, os, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, os.path.join(ROOT, 'tests'))
import run_tests as rt
from playwright.sync_api import sync_playwright

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'docs', 'evidence', 'v24_rc5')
PART = sys.argv[2] if len(sys.argv) > 2 else 'all'
os.makedirs(OUT, exist_ok=True)
SAVE = os.path.join(ROOT, 'tests/saves/player_day52.json')
raw = json.load(open(SAVE)); raw = raw.get('save', raw)
SEED = "Math.random=(function(){let a=%d;return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
notes = []

def shot(g, name, what):
    g.ev("forceDraw=true"); g.ev("__tick(1000/30)")
    g.page.wait_for_timeout(60)
    g.page.screenshot(path=os.path.join(OUT, name))
    notes.append(f'{name}: {what}')
    print('shot', name, '|', g.ev("JSON.stringify({day:S.day,t:R?Math.round(R.t):null,closing:R&&R.closing!=null?Math.round(R.closing):null,room,step:R&&R.upSearch?R.upSearch.step:null})"), flush=True)

def frames(g, n, stop=None):
    return g.page.evaluate(f'()=>window.__play({n},0,{json.dumps(stop) if stop else "null"})')

def flush(g):
    """__botUntil steps the simulation without the clock: lines queued meanwhile (setTimeout) would all come out at the
    next real frame — show them and let them go before a photograph (the game advances one clamped frame)"""
    g.ev("__tick(9000)"); clear_toasts(g)

def clear_toasts(g):
    g.ev("document.querySelectorAll('#toasts>*,#plines>*').forEach(e=>e.remove())")

def setf(g, k, back):
    g.ev(f"(()=>{{const d=S.day-{back};story().facts['{k}']={{d,n:1,l:d}}}})()")

def load(b, seed):
    g = rt.Game(b, port, 'index', seed=seed, manual=True, viewport={'width': 390, 'height': 844})
    g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.page.wait_for_timeout(150)
    g.click('[data-act=openFresh]') if g.page.query_selector('[data-act=openFresh]') else g.click('[data-act=open]'); g.page.wait_for_timeout(150)
    # the first day this version is played starts quiet (nothing fires at its start: no load-time dump) — play it through
    begin(g, seed * 7, scenes=False); finish(g)
    return g

def to_prep(g):
    if g.ev("phase") == 'summary':
        g.click('[data-act=toShop]'); g.page.wait_for_timeout(80)
    if g.ev("phase") == 'shop':
        g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(150)

def begin(g, d_seed, scenes=True):
    to_prep(g)
    g.ev(SEED % d_seed); g.ev("S.today.sugKey=null;S.today.sug=null;autoStock()")
    rt.fill_fridge(g)
    g.ev("window.__noScenes=%s" % ('false' if scenes else 'true'))   # before the start: the day's first beat plays at it
    rt.start_day(g); rt.install_bot(g); g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy")

def finish(g):
    g.ev("window.__noScenes=true")
    for _ in range(400):
        r = g.page.evaluate('()=>window.__bot(150,1/30)')
        if g.ev("phase") != 'service' or r['ticks'] < 150: break
    if g.ev("phase") == 'service': g.ev("finishClosing()")
    g.ev("for(let i=0;i<20;i++)__tick(1000/30)")

def begin_until(g, key, d_seed, scenes=True, tries=4):
    """start days until the beat `key` has fired at the start of one (the day's one major can go to another story's
    beat first — that one is then missed, not lost, and the next day it comes first)"""
    for i in range(tries):
        begin(g, d_seed + i, scenes)
        if g.ev(f"!!fact('{key}')&&fact('{key}').d===S.day"): return True
        print(f'  ({key} waited: Day', g.ev("S.day"), 'went to', g.ev("JSON.stringify(story().trace.filter(t=>t.d===S.day&&t.lane==='major').map(t=>t.k))"), ')', flush=True)
        g.ev("window.__noScenes=true;if(DLG){while(DLG)dlgNext()}"); finish(g)
    raise SystemExit(f'{key} never fired')

def story_ready(g):
    """the long stories before the second floor, as if they had happened (怡君 moved in, the wall settled)"""
    for i, k in enumerate(['yj_meet', 'yj_look', 'yj_three', 'yj_chose', 'yj_move', 'yj_key', 'yj_key_seen', 'xq_oh']):
        setf(g, k, 34 - i * 2)
    for i, k in enumerate(['wall_worry', 'wall_call', 'wall_photos', 'wall_jill', 'wall_visit', 'wall_wang', 'wall_setback', 'wall_report', 'wall_fee', 'wall_prep', 'wall_mediation', 'wall_settle', 'wall_paid', 'wall_article', 'wall_paper', 'wall_fixed']):
        setf(g, k, max(1, 18 - i))

def dlg_text(g):
    return g.ev("(()=>{const e=$('#dlg');return e&&!e.hidden?($('#dlg .dlg-name').textContent+'：'+$('#dlg .dlg-text').textContent):null})()")

with sync_playwright() as p:
    srv, port = rt.start_server(); b = p.chromium.launch()
    if PART in ('all', 'night'):
        g = load(b, 501)
        story_ready(g); setf(g, 'up_hint', 6); setf(g, 'up_staff', 5)
        # ---- U3: the landlord, the afternoon (the day's major, at the start of the service) ----
        begin_until(g, 'up_inspect', 9101)
        frames(g, 3)
        shot(g, 'u3_inspect_1.png', 'U3, the start of the service: the landlord came that afternoon (the fire inspection); Jill asks to go up with him')
        for i in range(3): g.ev("dlgNext()")
        shot(g, 'u3_inspect_2.png', 'U3: 「地板是好的，窗戶也是好的。」 — words only; the floor is not shown yet')
        for i in range(5): g.ev("dlgNext()")
        finish(g); to_prep(g)
        setf(g, 'up_inspect', 3)   # three days later (the gap the fiction needs: "several days")
        # ---- U4: the night ----
        begin_until(g, 'up_door', 9102)
        frames(g, 3)
        g.ev("dlgNext()")
        shot(g, 'u4_start.png', 'U4, the start of the service (the day\'s major is this one): the landlord brought someone up to look at the air conditioner — 「好了。門我帶上了。」')
        g.ev("while(DLG)dlgNext()")
        g.ev("__botUntil('R.t>=R.dur*.75',90000,1/30)"); flush(g)
        g.ev("setRoom('side')"); clear_toasts(g)
        shot(g, 'u4_side_door_closed.png', '21:00-ish: the side room; the stair door at the near edge is shut')
        g.ev("__botUntil('R.t>=R.dur*.86',90000,1/30)"); flush(g)
        g.ev("setRoom('side')"); frames(g, 40); clear_toasts(g)
        shot(g, 'u4_side_door_ajar.png', 'later: the door has given a hand\'s width; the stairwell light lies on the floor; a cat by it')
        g.ev("setRoom('main')")
        g.ev("__botUntil('R.closing!=null',90000,1/30)"); flush(g)
        clear_toasts(g)
        frames(g, 100)
        shot(g, 'u4_notice.png', 'closing: 「柔柔呢？」「剛剛不是還在？」「小齁也不在。」')
        frames(g, 130)
        shot(g, 'u4_search.png', 'everyone looks: Jill at the cat trees, the crew in the rooms; the other cats accounted for')
        for _ in range(60):
            frames(g, 15)
            if g.ev("R.upSearch&&R.upSearch.saidDoor"): break
        frames(g, 20)
        shot(g, 'u4_door_found.png', 'the side room: 「這個怎麼開著？」')
        for _ in range(60):
            frames(g, 10)
            if g.ev("R.jill.room==='up'"): break
        frames(g, 8)
        shot(g, 'u4_up_dark.png', 'up the stairs: the landlord\'s empty floor at night, before the light')
        for _ in range(80):
            frames(g, 10)
            if g.ev("!!(R.upSearch&&R.upSearch.seenAt)"): break
        frames(g, 30)
        shot(g, 'u4_up_found.png', 'the light on: 柔柔 at the window, 小齁 comes to Jill first')
        for _ in range(60):
            frames(g, 10)
            if dlg_text(g): break
        shot(g, 'u4_scene_1.png', '「妳們兩個。」')
        g.ev("dlgNext()"); shot(g, 'u4_scene_2.png', 'only after the cats: 「……這裡滿大的欸。」')
        for _ in range(8):
            if not dlg_text(g): break
            g.ev("dlgNext()")
        frames(g, 60)
        shot(g, 'u4_down.png', 'down they go — the cats first')
        for _ in range(80):
            frames(g, 10)
            if g.ev("!!(R.upSearch&&R.upSearch.latched)"): break
        frames(g, 25)
        shot(g, 'u4_latched.png', 'the door shut and latched: 「扣好了。」 — no unlock, no project')
        for _ in range(80):
            frames(g, 10)
            if g.ev("!R||!R.upSearch||R.upSearch.end"): break
        frames(g, 90)
        shot(g, 'u4_after.png', 'the closing goes on; the 二樓 tab is gone again')
        info = g.ev("JSON.stringify({cats:fact('up_cats'),door:fact('up_door'),tabs:roomsOpen(),party:v24().upParty,errors:window.__errs||[]})")
        print('night:', info, 'page errors:', g.errors[:5])
        notes.append('night state: ' + info)
        g.close()
    if PART in ('all', 'ask'):
        g = load(b, 502)
        story_ready(g)
        for k, back in [('up_hint', 16), ('up_staff', 15), ('up_inspect', 13), ('up_door', 10), ('up_cats', 10), ('sp_seat', 12), ('sp_box', 9), ('up_busy', 7), ('up_small', 5), ('up_remind', 2)]:
            setf(g, k, back)
        g.ev("S.money=Math.max(S.money,420000)")
        begin(g, 9201)
        g.ev("__botUntil('R.closing!=null',90000,1/30)"); flush(g)
        clear_toasts(g)
        for _ in range(60):
            frames(g, 10)
            if dlg_text(g): break
        shot(g, 'u6_ask_1.png', 'U6, closing: Jill at the stair door, the phone — 「……樓上現在還空著嗎？」')
        for i in range(7): g.ev("dlgNext()")
        shot(g, 'u6_ask_2.png', '「整層？」')
        g.ev("dlgNext()"); shot(g, 'u6_ask_3.png', '「整層。」')
        g.ev("dlgNext()")
        for _ in range(60):
            frames(g, 10)
            if g.ev("sub==='upproj'"): break
        shot(g, 'u6_project.png', 'the project, offered the way the Lounge was: 開始規劃 / 之後再說')
        g.click('[data-act=upGo][data-k=plan]'); g.page.wait_for_timeout(100)
        finish(g)
        if g.ev("phase") == 'summary':
            g.click('[data-act=toShop]'); g.page.wait_for_timeout(100)
        g.ev("shopTab='works';showShop()"); g.page.wait_for_timeout(100)
        g.ev("(()=>{const e=[...document.querySelectorAll('#screen .nm')].find(x=>x.textContent.trim()==='二樓');if(e)e.scrollIntoView({block:'start'})})()")
        g.page.wait_for_timeout(60)
        shot(g, 'u7_shop_card.png', 'the shop, 店舖工程: 二樓（整層） $350,000')
        g.click('[data-act=buyUp]'); g.page.wait_for_timeout(100); g.ev("__tick(1700)"); g.page.wait_for_timeout(60)
        shot(g, 'u7_reveal.png', 'bought: the works done — 「先這樣。」')
        g.click('[data-act=revealPeek]'); g.page.wait_for_timeout(120)
        shot(g, 'u7_floor_day0.png', 'the same evening: the whole floor, clean and lit, empty but for two boxes')
        g.ev("setRoom('front')"); g.page.wait_for_timeout(80)
        shot(g, 'u7_street.png', 'the street that evening: the windows upstairs are warm now')
        g.close()
    if PART in ('all', 'floor'):
        g = load(b, 503)
        story_ready(g)
        for k, back in [('up_hint', 26), ('up_staff', 25), ('up_inspect', 23), ('up_door', 20), ('up_cats', 20), ('up_ask', 7)]:
            setf(g, k, back)
        g.ev("S.rooms.up=1;S.newRooms=S.newRooms||{};S.newRooms.up=S.day-6;(()=>{const u=upS(),L=S.day-6;u.lease=L;u.furn={table:L+1,cabinet:L+2,coat:L+2,lamp:L+3,cushion:L+3,stool:L+5,scratch:L+5};u.traces={bag:L+2,cup:L+3,charger:L+4,coat:L+6};story().facts.up_lease={d:L,n:1,l:L}})()")
        begin(g, 9301, scenes=False)
        g.ev("__botUntil('R.t>=R.dur*.4',90000,1/30)"); flush(g)
        g.ev("(()=>{const A=catBy('mikan');upCatForce(A);upCatUp(A,{x:UP_L.sill.x,y:UP_L.sill.y-10,face:1,pose:'sit',t:90,win:1});const M=catBy('mei');upCatForce(M);upCatUp(M,{x:250,y:UP_L.col.base+13,face:-1,pose:'loaf',t:90})})()")
        g.ev("setRoom('up')"); frames(g, 20); clear_toasts(g)
        shot(g, 'up_open_floor_day6.png', 'six days after the lease, mid-service: the shared table and odd chairs, the cabinet, the coat stand, the lamp, the cats\' cushion, stool and board; a bag, a cup, a charger; 柔柔 back at her window, 寶寶 on the cushion')
        g.ev("__botUntil('R.t>=R.dur*.97',90000,1/30)"); flush(g); g.ev("setRoom('up')"); frames(g, 20); clear_toasts(g)
        shot(g, 'up_open_floor_night.png', 'the same floor at the end of the evening, the lamps on')
        g.close()
    with open(os.path.join(OUT, 'shots_up.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(notes) + '\n')
    b.close()
