"""rc7.6 evidence at 390x844 on the player's saves (headless Chromium: T, not O): the chef's night booked out (its first
night, held), Ken's tasting night over the whole Lounge, the choice before opening after the wine, the bar's L.
python3 evidence_rc76.py ROOT OUT"""
import sys, os, json, base64
ROOT = sys.argv[1]; OUT = sys.argv[2].rstrip('/') + '/'
sys.path.insert(0, ROOT + '/tests'); os.chdir(ROOT)
import run_tests as rt, v24_tests as v
from playwright.sync_api import sync_playwright
os.makedirs(OUT, exist_ok=True)
srv, port = rt.start_server()
log = []
def shot(g, name):
    g.ev("try{if(typeof hud==='function')hud(true)}catch(e){}")   # the bot does not draw the HUD: its clock would be the morning's
    g.page.wait_for_timeout(100); g.page.screenshot(path=OUT + name); print('  shot', name, flush=True)
def save_url(url, path): open(path, 'wb').write(base64.b64decode(url.split(',')[1])); print('  saved', os.path.basename(path), flush=True)
def crop(g, name, x, y, w, h, k=3):
    url = g.ev(f"(()=>{{const s=SV.s*DPR;const cv=document.createElement('canvas');cv.width={w}*{k};cv.height={h}*{k};const c=cv.getContext('2d');c.drawImage(sc,(SV.ox+({x})*SV.s)*DPR,(SV.oy+({y})*SV.s)*DPR,{w}*s,{h}*s,0,0,{w}*{k},{h}*{k});return cv.toDataURL('image/png')}})()")
    save_url(url, OUT + name)
def clean(g): g.ev("document.querySelectorAll('#plines>*,#toasts>*').forEach(e=>e.remove())")
def center(g, sel, text=None):
    if text: g.ev(f"(()=>{{const e=[...document.querySelectorAll('{sel}')].find(e=>e.textContent.includes({json.dumps(text)}));if(e)e.scrollIntoView({{block:'center'}})}})()")
    else: g.ev(f"(()=>{{const e=document.querySelector('{sel}');if(e)e.scrollIntoView({{block:'center'}})}})()")
with sync_playwright() as p:
    b = p.chromium.launch()
    # ---- the chef's night, its first night (held), booked out
    g = rt.Game(b, port, 'index', seed=7612, manual=True, viewport={'width': 390, 'height': 844})
    v.load_save(g, 'player_day74_1508.json')
    g.ev("S.cn=null;kenS().next=null;shopTab='works';showShop()"); g.page.wait_for_timeout(150)
    center(g, '#screen .cn-card'); clean(g); shot(g, 'cn01_shop_the_chefs_night.png')
    log.append('the card: ' + g.ev("(document.querySelector('#screen .cn-card')||{}).innerText||''").replace('\n', ' '))
    g.ev("document.querySelector('#screen [data-act=cnPlan]').click()"); g.page.wait_for_timeout(150)
    center(g, '#screen .cn-card'); clean(g); shot(g, 'cn02_planned.png')
    g.ev("closeSub&&closeSub();showPrep()"); g.page.wait_for_timeout(150)
    center(g, '#screen .event', '主廚之夜'); clean(g); shot(g, 'cn03_news_tomorrow.png')
    g.ev("S.cn.next.d=S.day;showPrep()"); g.page.wait_for_timeout(150)
    center(g, '#screen .event', '主廚之夜'); clean(g); shot(g, 'cn04_news_tonight.png')
    v.to_service(g); g.ev("window.__act=window.__actLazy;window.__noScenes=false;window.__holds=true;window.__fastSay=0")
    n_open = n_end = 0; mid = False
    for _ in range(9000):
        if g.ev("!!(typeof DLG!=='undefined'&&DLG&&DLG.sh)"):
            k = g.ev("DLG.sh.k"); idx = 0
            for _ in range(30):
                if not g.ev("!!(DLG&&DLG.sh)"): break
                idx += 1
                if k == 'cn_first' and n_end == 0 and n_open < 2 and idx in (1, 3):
                    g.ev("__tick(400)"); shot(g, f'cn05_first_night_opens_{idx}.png'); n_open += 1
                elif k == 'cn_first' and n_open >= 2 and idx == 2 and n_end == 0:
                    g.ev("__tick(400)"); shot(g, 'cn07_first_night_ends.png'); n_end += 1
                g.ev("__tick(300);dlgNext()")
            continue
        g.page.evaluate('()=>window.__bot(30,1/30)')
        r = json.loads(g.ev("JSON.stringify(R&&R.cn?{on:R.cn.on,end:R.cn.end,c1:R.cn.guests.filter(q=>q.ticket&&q.ticket.items.some(i=>i.course===1&&i.st==='served')).length,up:R.cn.guests.reduce((a,q)=>a+(q.ticket?q.ticket.items.filter(i=>i.cnp&&i.st==='ready'&&!i.picked).length:0),0)}:{})"))
        if r.get('on') and not mid and r.get('c1', 0) >= 5 and r.get('up', 0) >= 2:
            g.ev("setRoom('lounge')"); g.ev("for(let i=0;i<4;i++)__tick(1000/30)"); clean(g); shot(g, 'cn06_the_whole_lounge.png')
            crop(g, 'cn06b_the_L_end_plates.png', 90, 120, 130, 140, 4); crop(g, 'cn06c_the_tables.png', 40, 220, 330, 200, 2)
            log.append('mid-night: ' + g.ev("JSON.stringify({clock:clockStr(),in:R.groups.filter(q=>q.cn&&q.table!=null).reduce((a,q)=>a+q.size,0),up:" + str(r.get('up')) + "})")); mid = True
        if (r.get('end') and not g.ev("!!(typeof DLG!=='undefined'&&DLG&&DLG.sh)")) or g.ev("phase") != 'service': break
    log.append('the night: ' + g.ev("JSON.stringify({end:R.cn.end,people:R.cn.people,S:S.cn,endClock:clockStr()})"))
    g.ev("window.__holds=false;window.__noScenes=true")
    g.ev("__botUntil('phase!==\\'service\\'',90000,1/30)"); g.page.wait_for_timeout(150)
    g.ev("document.querySelectorAll('#toasts>*').forEach(e=>e.remove())"); center(g, '#screen .chips span', '主廚之夜'); shot(g, 'cn08_summary.png')
    log.append('summary lg: ' + g.ev("JSON.stringify(S.lastSummary.lg)") + ' net ' + str(g.ev("S.lastSummary.net")))
    url = g.ev("(async()=>{const p=albumList().find(p=>p.kind==='chefnight');return p?(p.img||await photoGet(p.id)):null})()")
    if url: save_url(url, OUT + 'cn09_the_album_photo.jpg')
    log.append('photo: ' + g.ev("JSON.stringify((albumList().find(p=>p.kind==='chefnight')||{}).cap||null)"))
    log.append('errors (chef\'s night): %s' % g.errors[:3]); g.close()
    # ---- Ken's tasting night, the whole Lounge (a later night, unheld)
    g = rt.Game(b, port, 'index', seed=7621, manual=True, viewport={'width': 390, 'height': 844})
    v.load_save(g, 'player_day74_1508.json')
    g.ev("S.cn=null;kenS().next={d:S.day,n:5};showPrep()"); g.page.wait_for_timeout(150)
    center(g, '#screen .event', '品酒夜'); clean(g); shot(g, 'kt01_news_tonight.png')
    v.to_service(g); g.ev("window.__act=window.__actLazy")
    g.ev("__botUntil('R.kt&&R.kt.on&&R.kt.said>=1&&R.t>R.kt.t0+R.dur*.08',150000,1/30)")
    g.ev("setRoom('lounge')"); g.ev("for(let i=0;i<8;i++)__tick(1000/30)"); clean(g); shot(g, 'kt02_the_whole_lounge.png')
    crop(g, 'kt02b_tables_with_glasses.png', 40, 220, 200, 150, 3); crop(g, 'kt02c_the_bar_the_L_and_the_board.png', 90, 90, 290, 160, 3)
    log.append('tasting: ' + g.ev("JSON.stringify({clock:clockStr(),said:R.kt.said,in:R.groups.filter(q=>q.tasting&&q.table!=null).reduce((a,q)=>a+q.size,0)})"))
    g.ev("__botUntil('phase!==\\'service\\'',150000,1/30)")
    log.append('tasting summary lg: ' + g.ev("JSON.stringify(S.lastSummary&&S.lastSummary.lg)"))
    log.append('errors (tasting): %s' % g.errors[:3]); g.close()
    # ---- after the wine: the choice before opening
    g = rt.Game(b, port, 'index', seed=7633, manual=True, viewport={'width': 390, 'height': 844})
    v.load_save(g, 'player_day74_1508.json')
    g.ev("for(const k of ['ken_propose','ken_t1','ken_t2','ken_t3','ken_collab','ken_samples','ken_wine']){const d=S.day-10;story().facts[k]={d,n:1,l:d}}const K=kenS();K.next=null;K.nextN=4;K.lastD=S.day-10;S.cn=null;showPrep()")
    g.page.wait_for_timeout(150); center(g, '#screen .kt-ask'); clean(g); shot(g, 'kt03_after_the_wine_the_question.png')
    g.ev("document.querySelector('#screen [data-act=ktHold]').click()"); g.page.wait_for_timeout(150); center(g, '#screen .kt-ask'); clean(g); shot(g, 'kt04_tonight_held.png')
    log.append('errors (choice): %s' % g.errors[:3]); g.close()
    b.close()
srv.shutdown()
open(OUT + 'evidence_log.txt', 'w', encoding='utf-8').write('\n'.join(log) + '\n'); print('\n'.join(log))
