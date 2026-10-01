"""v2.4 rc6 visual checkpoints: the Staff Room and the Private Dining Room, at phone size (390x844), from the player's
Day 61 save played for real. The story facts before each state are set as if the earlier beats had happened (the
floor leased days ago, its furniture arrived); then the day is played by the bot and photographed as it happens.

  python3 tools/sims/v24_rooms_shots.py [out_dir] [part=all|sr|pd|works|shop|story]
"""
import sys, os, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, os.path.join(ROOT, 'tests'))
import run_tests as rt
from playwright.sync_api import sync_playwright

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'docs', 'evidence', 'v24_rc6')
PART = sys.argv[2] if len(sys.argv) > 2 else 'all'
os.makedirs(OUT, exist_ok=True)
SAVE = os.path.join(ROOT, 'tests/saves/player_day61.json')
raw = json.load(open(SAVE)); raw = raw.get('save', raw)
SEED = "Math.random=(function(){let a=%d;return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
notes = []

def shot(g, name, what):
    g.ev("forceDraw=true"); g.ev("__tick(1000/30)")
    g.page.wait_for_timeout(60)
    g.page.screenshot(path=os.path.join(OUT, name))
    notes.append(f'{name}: {what}')
    print('shot', name, '|', g.ev("JSON.stringify({day:S.day,phase,t:R?Math.round(R.t/R.dur*100)+'%':null,closing:R&&R.closing!=null?Math.round(R.closing):null,room})"), '| errors', g.errors[:2], flush=True)

def flush(g):
    g.ev("__tick(9000)"); clear_toasts(g)

def clear_toasts(g):
    g.ev("document.querySelectorAll('#toasts>*,#plines>*').forEach(e=>e.remove())")

def setf(g, k, back):
    g.ev(f"(()=>{{const d=S.day-{back};story().facts['{k}']={{d,n:1,l:d}}}})()")

def floor_ready(g, lease_back=14):
    """the stories before the rooms, as if they had happened: 怡君 and the wall settled, the floor's whole arc, the floor
    leased lease_back days ago and its furniture in"""
    g.ev("(()=>{const v=v24();v.first=S.day-60})()")
    for i, k in enumerate(['yj_meet', 'yj_look', 'yj_three', 'yj_chose', 'yj_move', 'yj_key', 'yj_key_seen', 'xq_oh']):
        setf(g, k, 60 - i * 2)
    for i, k in enumerate(['wall_worry', 'wall_call', 'wall_photos', 'wall_jill', 'wall_visit', 'wall_wang', 'wall_setback', 'wall_report', 'wall_fee', 'wall_prep', 'wall_mediation', 'wall_settle', 'wall_paid', 'wall_article', 'wall_paper', 'wall_fixed']):
        setf(g, k, 44 - i)
    for i, k in enumerate(['up_hint', 'up_staff', 'up_inspect', 'up_door', 'up_cats', 'up_busy', 'up_full', 'sp_box', 'sp_seat', 'sp_stuff', 'up_remind', 'up_ask', 'up_leak']):
        setf(g, k, 26 - i)
    setf(g, 'up_lease', lease_back); setf(g, 'up_use', lease_back - 2)
    g.ev(f"(()=>{{S.rooms.up=1;const u=upS();const L=S.day-{lease_back};u.lease=L;u.furn={{table:L+1,cabinet:L+2,coat:L+2,lamp:L+3,cushion:L+3,stool:L+5,scratch:L+5}};u.traces={{bag:L+2,cup:L+3,charger:L+4,coat:L+6}};S.upProj={{state:'built'}};S.newRooms=S.newRooms||{{}};S.newRooms.up=L}})()")

def load(b, seed, prep=True):
    g = rt.Game(b, port, 'index', seed=seed, manual=True, viewport={'width': 390, 'height': 844})
    g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.page.wait_for_timeout(150)
    g.click('[data-act=openFresh]') if g.page.query_selector('[data-act=openFresh]') else g.click('[data-act=open]'); g.page.wait_for_timeout(150)
    return g

def to_prep(g):
    if g.ev("phase") == 'summary':
        g.click('[data-act=toShop]'); g.page.wait_for_timeout(80)
    if g.ev("phase") == 'shop':
        g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(150)
    g.ev("while(typeof DLG!=='undefined'&&DLG)dlgNext()")

def reprep(g):
    """after changing the state on the prep screen: draw it again (the day's booking is made here)"""
    g.ev("IDLE=null;bg=null;for(const k in BGC)delete BGC[k];showPrep()"); g.page.wait_for_timeout(120)

def begin(g, d_seed, scenes=False):
    to_prep(g)
    g.ev(SEED % d_seed); g.ev("S.today.sugKey=null;S.today.sug=null;autoStock()")
    rt.fill_fridge(g)
    g.ev("window.__noScenes=%s" % ('false' if scenes else 'true'))
    rt.start_day(g); rt.install_bot(g); g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy")

def until(g, cond, maxn=400):
    for _ in range(maxn):
        if g.ev(f"phase!=='service'||!R||!!({cond})"): break
        g.ev("while(typeof DLG!=='undefined'&&DLG)dlgNext()")
        g.ev(f"__botUntil({json.dumps(cond)},1500,1/30)")
    flush(g)

def finish(g):
    g.ev("window.__noScenes=true")
    for _ in range(600):
        if g.ev("phase") != 'service': break
        g.ev("while(typeof DLG!=='undefined'&&DLG)dlgNext()")
        g.page.evaluate('()=>window.__bot(150,1/30)')
    if g.ev("phase") == 'service': g.ev("finishClosing()")
    g.ev("for(let i=0;i<20;i++)__tick(1000/30)")

def frames(g, n):
    for _ in range(n): g.ev("__tick(1000/30)")

with sync_playwright() as p:
    srv, port = rt.start_server(); b = p.chromium.launch()
    if PART in ('all', 'sr'):
        g = load(b, 611)
        floor_ready(g, 16)
        setf(g, 'sp_wait', 9); setf(g, 'sr_story', 3)
        g.ev("(()=>{const s=srW();s.offer=S.day-3;s.plan='plan';s.bought=S.day-1;s.done=S.day})()")
        reprep(g)
        begin(g, 6101)
        until(g, 'R.t>=R.dur*.45')
        g.ev("setRoom('up')"); frames(g, 10); clear_toasts(g)
        shot(g, 'sr1_floor_evening.png', 'Staff Room I, its first evening: the floor in the 二樓 view — the new walls and the door with its plate, the shared table moved to the right window, the open middle and the stairs')
        g.ev("setRoom('staff')"); frames(g, 10); clear_toasts(g)
        shot(g, 'sr1_room_evening.png', 'inside 休息室 (Phase I): green sofa, low table, the chairs (one from the open floor), water, the shelf and its lamp, the cabinet, the floor lamp and the coat stand from the open floor')
        until(g, 'R.closing!=null&&R.closing>34')
        g.ev("setRoom('staff')"); frames(g, 30); clear_toasts(g)
        shot(g, 'sr1_room_closing.png', 'closing, the first evening: some of the crew up in the room; Jill came up to see it')
        g.ev("setRoom('up')"); frames(g, 10); clear_toasts(g)
        shot(g, 'sr1_floor_closing.png', 'closing on the floor: people in the room seen over the cut walls, the door, the lamp')
        g.close()
    if PART in ('all', 'pd'):
        g = load(b, 612)
        floor_ready(g, 40)
        setf(g, 'sp_wait', 33); setf(g, 'sr_story', 30); setf(g, 'sr_first', 27); setf(g, 'sr_plug', 25)
        for k, back in [('pd_yj', 12), ('pd_other', 8), ('pd_story', 4)]: setf(g, k, back)
        g.ev("(()=>{const s=srW();s.offer=S.day-30;s.bought=S.day-29;s.done=S.day-28;s.b2=S.day-20;s.st2=S.day-19;s.tr={plug:S.day-25,seat:S.day-15,cup:S.day-12};const p=pdW();p.offer=S.day-4;p.bought=S.day-2;p.done=S.day-1;p.ever=0})()")
        reprep(g)
        shot(g, 'pd1_prep_news.png', 'the prep screen the day after the Private Dining Room opened: 今晚｜私人包廂｜已預約 — party size and the minimum spend')
        begin(g, 6201)
        until(g, "(()=>{const t=R.tables.find(q=>q.pdr);return !!(t&&t.group&&t.group.state==='eat')})()", 600)
        g.ev("setRoom('pdr')"); frames(g, 10); clear_toasts(g)
        shot(g, 'pd1_room_meal.png', 'inside 包廂 (Phase I): the booked party at the long table, the pendant lamp, the window, the sideboard')
        g.ev("setRoom('up')"); frames(g, 10); clear_toasts(g)
        shot(g, 'pd1_floor_meal.png', 'the floor while they eat: the Private Dining Room door shut, the party seen over the cut wall; the Staff Room (Phase II) below it; the open middle')
        finish(g)
        shot(g, 'pd1_summary.png', 'the summary of that evening')
        g.close()
    print('\n'.join(notes))
    open(os.path.join(OUT, 'shots.txt'), 'a', encoding='utf-8').write('\n'.join(notes) + '\n')
    b.close(); srv.shutdown()
