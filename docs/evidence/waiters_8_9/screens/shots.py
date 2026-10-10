"""The eighth and ninth waiters (2026-10-10, after v2.5.1), at phone size (390×844), from the user's Day 92 save
(tests/saves/player_day92_2105.json: six restaurant waiters and 安安, seven places): the Private Dining Room's phases I and III
built the way the tests set them up (v24_tests.PD_OPEN; +1 waiter each) so there are nine places, the waiters hired
from the shop the way a player does (阿芳, then the new ones), their cards on the staff page, and the next evening with
them at work (each one found in the rooms and photographed close). Also the figures side by side, drawn large.
python3 docs/evidence/waiters_8_9/screens/shots.py OUTDIR NAME[,NAME]   (from the repo root)"""
import sys, os, json, base64
OUT = sys.argv[1]; NEW = sys.argv[2].split(','); ROOT = os.getcwd(); sys.path.insert(0, os.path.join(ROOT, 'tests')); sys.argv = [sys.argv[0]]
os.makedirs(OUT, exist_ok=True)
import run_tests as rt
import v24_tests as v
from playwright.sync_api import sync_playwright
raw = json.load(open('tests/saves/player_day92_2105.json', encoding='utf-8')); raw = raw.get('save', raw)
srv, port = rt.start_server()
log = []
def note(s): print(s, flush=True); log.append(s)
with sync_playwright() as p:
    b = p.chromium.launch()
    g = rt.Game(b, port, 'index', seed=920, manual=True, viewport={'width': 390, 'height': 844})
    g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.page.wait_for_timeout(150)
    g.click('[data-act=openFresh]') if g.page.query_selector('[data-act=openFresh]') else g.click('[data-act=open]'); g.page.wait_for_timeout(200)
    for _ in range(20):
        if g.ev("typeof DLG!=='undefined'&&!!DLG"): g.ev("dlgNext()")
    g.ev("S.money+=400000"); g.ev(v.PD_OPEN); g.ev("pdW().st2=S.day;pdW().st3=S.day;save()")
    note(f"waiters before: {g.ev('roleCrew(\"waiter\").map(m=>m.name).join(\"、\")')} ({g.ev('roleCrew(\"waiter\").length')}/{g.ev('roleCap(\"waiter\")')})")
    g.ev("shopTab='staff';showShop()"); g.page.wait_for_timeout(200)
    hired = []
    for _ in range(1 + len(NEW)):
        btn = g.page.query_selector('#screen [data-act=hire][data-k=waiter]')
        if not btn: break
        btn.scroll_into_view_if_needed(); btn.click(); g.page.wait_for_timeout(150)
        hired.append(g.ev("S.crew[S.crew.length-1].name"))
    note(f"hired from the shop, in order: {hired}; the toast: {g.ev('[...document.querySelectorAll(\".toast\")].map(t=>t.textContent).join(\" | \")')}")
    note(f"waiters after: {g.ev('roleCrew(\"waiter\").map(m=>m.name).join(\"、\")')} ({g.ev('roleCrew(\"waiter\").length')}/{g.ev('roleCap(\"waiter\")')})")
    for i, nm in enumerate(NEW):
        g.ev("shopTab='staff';showShop()"); g.page.wait_for_timeout(200)
        el = g.page.query_selector(f"#screen .item:has-text('{nm}')")
        if el: el.scroll_into_view_if_needed(); g.page.wait_for_timeout(150)
        card = g.ev(f"(()=>{{const it=[...document.querySelectorAll('#screen .item')].find(x=>x.querySelector('.nm')&&x.querySelector('.nm').textContent.includes('{nm}'));return it?{{img:!!it.querySelector('img.face'),src:(it.querySelector('img.face')||{{}}).src===(portraitOf('staff:{nm}')||{{}}).src,text:it.innerText.replace(/\\s+/g,' ').slice(0,120)}}:null}})()")
        note(f"the staff page, {nm}'s card: {card}")
        g.page.screenshot(path=os.path.join(OUT, f'0{i+1}_390x844_staff_card_{i+8}.png'))
    # the reload keeps them
    g.ev("save()"); g.reload(); g.page.wait_for_timeout(150)
    g.click('[data-act=openFresh]') if g.page.query_selector('[data-act=openFresh]') else g.click('[data-act=open]'); g.page.wait_for_timeout(200)
    note(f"after a reload: {g.ev('roleCrew(\"waiter\").map(m=>m.name+\" LV\"+m.lv).join(\"、\")')}")
    # the next evening, with them at work
    for _ in range(20):
        if g.ev("typeof DLG!=='undefined'&&!!DLG"): g.ev("dlgNext()")
    if g.ev("phase") == 'shop': g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(200)
    g.ev("autoStock()"); rt.start_day(g); rt.install_bot(g); g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;window.__noScenes=true")
    shot = {}
    for _ in range(900):
        g.page.evaluate('()=>window.__bot(15,1/30)')
        for nm in NEW:
            if nm in shot: continue
            pos = g.ev(f"(()=>{{const m=S.crew.find(m=>m.name==='{nm}');const w=m&&R&&R.cw&&R.cw[m.id];return w&&w.x!=null?{{x:w.x,y:w.y,room:w.room||'main',task:w.task?w.task.k:null}}:null}})()")
            if pos and pos['room'] in ('main', 'side') and pos['task']:
                g.ev(f"room='{pos['room']}';renderRoomTabs(true);forceDraw=true;drawScene(performance.now())"); g.page.wait_for_timeout(120)   # draw only: the clock does not move, the view stays here
                pos = g.ev(f"(()=>{{const m=S.crew.find(m=>m.name==='{nm}');const w=R.cw[m.id];return{{x:w.x,y:w.y,room:w.room||'main',task:w.task?w.task.k:null}}}})()")
                pp = json.loads(g.ev(f"JSON.stringify((()=>{{const r=sc.getBoundingClientRect();return{{x:r.left+SV.ox+{pos['x']}*SV.s,y:r.top+SV.oy+{pos['y']}*SV.s}}}})())"))
                shot[nm] = (pos, pp)
                g.page.screenshot(path=os.path.join(OUT, f'0{3+NEW.index(nm)}_390x844_at_work_{nm}.png'))
                g.page.screenshot(path=os.path.join(OUT, f'0{3+NEW.index(nm)}b_close_{nm}.png'), clip={'x': max(0, pp['x'] - 70), 'y': max(0, pp['y'] - 110), 'width': 140, 'height': 140})
                note(f"{nm} at work in the {pos['room']} ({pos['task']}), at {round(pos['x'])},{round(pos['y'])}")
        if len(shot) == len(NEW) or g.ev("phase") != 'service': break
    note(f"page errors: {g.errors[:3]}")
    # the figures side by side, drawn large (the waiters, the new ones last)
    names = ['小茉', 'Kai', 'Nina', '阿哲', 'Momo', '小威', '阿芳'] + NEW
    url = g.ev("""(()=>{const names=%s;const W=110;const cv=document.createElement('canvas');cv.width=W*names.length;cv.height=380;const c=cv.getContext('2d');
      c.fillStyle='#EFE5D3';c.fillRect(0,0,cv.width,cv.height);
      names.forEach((n,i)=>{const L=crewLook({id:'pv'+i,name:n,role:'waiter'});c.save();c.translate(W*i+W/2,300);c.scale(4,4);drawPerson(c,0,0,L,{});c.restore();
        c.fillStyle='#2E2019';c.font='bold 16px sans-serif';c.textAlign='center';c.fillText(n,W*i+W/2,360)});return cv.toDataURL()})()""" % json.dumps(names, ensure_ascii=False))
    open(os.path.join(OUT, '09_the_waiters_drawn_4x.png'), 'wb').write(base64.b64decode(url.split(',')[1]))
    g.close(); b.close()
srv.shutdown()
open(os.path.join(OUT, 'shots.txt'), 'w', encoding='utf-8').write('\n'.join(log) + '\n')
