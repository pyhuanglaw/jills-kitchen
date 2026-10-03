"""v2.4 rc4 visual checkpoints at phone size (390x844), from real play: a new game (秀琴阿姨 from Day 1, the coach,
Day 2's news, the Day 4 staff tab, hiring her, 怡君's first visit with her mother at closing) and the player's Day 52
save (the 2.4 note), plus the manual. Writes PNGs to docs/evidence/v24_rc4/ (or the folder given).

  python3 tools/sims/v24_shots.py [out_dir]
"""
import sys, os, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, os.path.join(ROOT, 'tests'))
import run_tests as rt
from playwright.sync_api import sync_playwright

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'docs', 'evidence', 'v24_rc4')
os.makedirs(OUT, exist_ok=True)
SEED = "Math.random=(function(){let a=%d;return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
notes = []

def act(g, a, **kv):
    ds = ''.join(f"el.dataset.{k}='{v}';" for k, v in kv.items())
    g.ev(f"(()=>{{const el=document.createElement('button');el.dataset.act='{a}';{ds}$('#screen').appendChild(el);el.click();el.remove()}})()")

def shot(g, name, what):
    g.page.wait_for_timeout(60)
    g.page.screenshot(path=os.path.join(OUT, name))
    notes.append(f'{name}: {what}')
    print('shot', name, flush=True)

def frames(g, n):
    g.page.evaluate(f'()=>window.__play({n},0)')

def finish_day(g):
    for _ in range(400):
        r = g.page.evaluate('()=>window.__bot(150,1/30)')
        if g.ev("phase") != 'service' or r['ticks'] < 150: break
    if g.ev("phase") == 'service': g.ev("__bot(60000,1/30)")
    g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
    if g.ev("phase") == 'summary': g.click('[data-act=toShop]')

with sync_playwright() as p:
    srv, port = rt.start_server(); b = p.chromium.launch()
    # ---- a new game ----
    g = rt.Game(b, port, 'index', seed=270, manual=True, viewport={'width': 390, 'height': 844})
    rt.install_bot(g)
    g.click('[data-act=open]'); g.page.wait_for_timeout(100)
    rt.start_day(g)
    g.ev("__botUntil('R.t>=R.dur*.915',60000,1/30)")
    for _ in range(40):   # real frames until she is in and has spoken
        frames(g, 15)
        if g.ev("!!(R.xqh&&!R.xqh.arriving)"): break
    frames(g, 50)
    shot(g, 'day1_helper_arrives.png', 'Day 1 of a new game, about 21:15: 秀琴阿姨 has walked in and tidies beside a table nobody is at; her first lines')
    frames(g, 170)
    shot(g, 'day1_coach.png', 'a few seconds later, after her three lines: the coach names her, once')
    g.ev("__botUntil('R.closing!=null',60000,1/30)")
    g.ev("document.querySelectorAll('#toasts>*').forEach(e=>e.remove())")
    for _ in range(6): g.ev("__tick(1000/30)")
    frames(g, 1); g.ev("for(let i=0;i<30*6;i++){update(1/30);updateCats(1/30,0)}"); g.ev("forceDraw=true;__tick(1000/30)")
    shot(g, 'day1_closing_helper.png', 'Day 1, after 21:30: she wipes down by the pickup point while the closing runs; about twenty seconds in she goes home')
    g.ev("finishClosing()"); g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
    if g.ev("phase") == 'summary': g.click('[data-act=toShop]')
    g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(150)
    shot(g, 'day2_news.png', 'Day 2 of a new game: the morning news says who came to help last night')
    for day in range(2, 5):
        if day > 2:
            g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(100)
        g.ev(SEED % (270000 + day)); rt.start_day(g); finish_day(g)
        if day == 3: act(g, 'hire', k='waiter'); g.ev("__tick(30)")
    g.ev("shopTab='staff';showShop()"); g.page.wait_for_timeout(80)
    g.ev("const it=[...document.querySelectorAll('#screen .item')].find(e=>e.innerText.includes('清潔員'));if(it)it.scrollIntoView({block:'center'})")
    shot(g, 'day4_staff_tab.png', 'Day 4, the staff tab opens: the recruit list says the first cleaner is 秀琴阿姨')
    g.ev("S.money=Math.max(S.money,5000)")
    if g.ev("(S.crew||[]).length>=crewCap()"): g.ev("S.level=Math.max(S.level,2)")
    g.ev("window.__noScenes=false")
    act(g, 'hire', k='cleaner'); g.ev("__tick(30)")
    shot(g, 'hire_her_line.png', 'hiring the first cleaner is hiring her: her one line over the shop, 「那以後就天天來了。」')
    g.ev("for(let i=0;i<80&&typeof DLG!=='undefined'&&DLG;i++){__tick(400);dlgNext()}"); g.ev("const c=[...document.querySelectorAll('#screen *')].find(e=>e.children.length===0&&e.textContent.trim()==='今天起正式上班'||e.textContent.includes('今天起正式上班')&&e.children.length===0);if(c)c.scrollIntoView({block:'center'})")
    shot(g, 'hire_her_card.png', 'her card: 清潔員, 「今天起正式上班」 — she was in most evenings before')
    g.ev("window.__noScenes=true")
    g.close()
    # ---- 怡君's first visit in a new game with no cleaner: her mother is the evening helper ----
    g = rt.Game(b, port, 'index', seed=271, manual=True, viewport={'width': 390, 'height': 844})
    rt.install_bot(g)
    g.click('[data-act=open]'); g.page.wait_for_timeout(100); g.ev("window.__fastSay=1")
    got = False
    for day in range(1, 15):
        act(g, 'restock'); g.ev("__tick(200)"); rt.fill_fridge(g); g.ev(SEED % (271000 + day))
        rt.start_day(g)
        if g.ev("due('yj_meet',null,0,'yj')&&R.sched.some(o=>o.name==='怡君')"):
            g.ev("window.__noScenes=false;window.__fastSay=0")
            for _ in range(3000):
                g.page.evaluate('()=>window.__bot(10,1/30)')
                if g.ev("!!DLG") or g.ev("phase") != 'service': break
            if g.ev("!!DLG"):
                g.ev("hud(true);forceDraw=true"); g.ev("__tick(1000/30)")
                shot(g, 'yj_meet_helper_scene.png', f'a new game, Day {g.ev("S.day")}, no cleaner hired: 怡君 came late to eat; her mother, in to help close up, walked over — 「妳怎麼來了？」 with the player\'s yj_intro picture')
                for _ in range(3):
                    g.ev("__tick(400);dlgNext()"); g.page.wait_for_timeout(40)
                shot(g, 'yj_meet_helper_scene_line4.png', 'the same scene, the last line 「不能吃妳工作的喔？」 (怡君, laughing)')
                while g.ev("!!DLG"): g.ev("__tick(400);dlgNext()")
                got = True
            g.ev("window.__noScenes=true;window.__fastSay=1")
        finish_day(g)
        if day == 3: act(g, 'hire', k='waiter'); g.ev("__tick(30)")
        if got: break
        g.click('#screen [data-act=nextDay]'); g.ev("__tick(100)")
    if not got: notes.append('yj_meet_helper_scene.png: NOT TAKEN — 怡君 did not meet her mother within 14 days with this seed')
    g.close()
    # ---- the player's Day 52 save: the 2.4 note ----
    g = rt.Game(b, port, 'index', seed=272, manual=True, viewport={'width': 390, 'height': 844})
    raw = json.load(open(os.path.join(ROOT, 'tests', 'saves', 'player_day52.json'), encoding='utf-8')); raw = raw.get('save', raw)
    g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.page.wait_for_timeout(150)
    g.click('[data-act=openFresh]') if g.page.query_selector('[data-act=openFresh]') else g.click('[data-act=open]'); g.page.wait_for_timeout(150)
    if g.ev("phase") == 'shop':
        g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(200)
    shot(g, 'day52_update_note.png', "the player's Day 52 save, next prep screen: one 2.4 note — staff arriving late, the illustrations, 後場整理區 (systems only)")
    # the manual
    g.ev("showGuide()"); g.page.wait_for_timeout(80)
    g.ev("const d=[...document.querySelectorAll('#screen details.gcard')];d.forEach(x=>x.open=false);const s=d.find(x=>x.querySelector('summary b').textContent.trim()==='Jill 與員工');s.open=true;const p=[...s.querySelectorAll('*')].find(e=>e.children.length===0&&e.textContent.trim()==='秀琴阿姨');(p||s).scrollIntoView({block:'start'})")
    shot(g, 'manual_staff.png', 'the manual, Jill 與員工: 清潔員, 秀琴阿姨 (before and after the first cleaner), 晚點到')
    g.ev("const d=[...document.querySelectorAll('#screen details.gcard')];d.forEach(x=>x.open=false);const s=d.find(x=>x.querySelector('summary b').textContent.trim()==='故事');s.open=true;const p=[...s.querySelectorAll('*')].find(e=>e.children.length===0&&e.textContent.trim()==='插圖');(p||s).scrollIntoView({block:'center'})")
    shot(g, 'manual_story.png', 'the manual, 故事: 插圖 and 店外的生活')
    print('errors', g.errors[:3])
    g.close(); b.close()
open(os.path.join(OUT, 'shots.txt'), 'w', encoding='utf-8').write('\n'.join(notes) + '\n')
print('\n'.join(notes))
