"""The booked-out Lounge at 390x844 on the player's Day 74 save: Ken's tasting night and the chef's night (later nights, so
nothing is held), mid-evening. python3 shot_events.py ROOT OUT"""
import sys, os, json, base64
ROOT = sys.argv[1]; OUT = sys.argv[2].rstrip('/') + '/'
sys.path.insert(0, ROOT + '/tests'); os.chdir(ROOT)
import run_tests as rt, v24_tests as v
from playwright.sync_api import sync_playwright
os.makedirs(OUT, exist_ok=True)
srv, port = rt.start_server()
def save_url(url, path): open(path, 'wb').write(base64.b64decode(url.split(',')[1])); print('  saved', os.path.basename(path), flush=True)
def crop(g, name, x, y, w, h, k=3):
    url = g.ev(f"(()=>{{const s=SV.s*DPR;const cv=document.createElement('canvas');cv.width={w}*{k};cv.height={h}*{k};const c=cv.getContext('2d');c.drawImage(sc,(SV.ox+({x})*SV.s)*DPR,(SV.oy+({y})*SV.s)*DPR,{w}*s,{h}*s,0,0,{w}*{k},{h}*{k});return cv.toDataURL('image/png')}})()")
    save_url(url, OUT + name)
def clean(g): g.ev("document.querySelectorAll('#plines>*,#toasts>*').forEach(e=>e.remove())")
with sync_playwright() as p:
    b = p.chromium.launch()
    # Ken's tasting night
    g = rt.Game(b, port, 'index', seed=7621, manual=True, viewport={'width': 390, 'height': 844})
    v.load_save(g, 'player_day74_1508.json')
    g.ev("S.cn=null;kenS().next={d:S.day,n:5};showPrep()"); g.page.wait_for_timeout(150)
    g.ev("(()=>{const e=[...document.querySelectorAll('#screen .event')].find(e=>e.textContent.includes('品酒夜'));if(e)e.scrollIntoView({block:'center'})})()"); clean(g)
    g.page.screenshot(path=OUT + '01_kt_news_tonight.png'); print('  shot 01')
    v.to_service(g); g.ev("window.__act=window.__actLazy")
    g.ev("__botUntil('R.kt&&R.kt.on&&R.kt.said>=1&&R.t>R.kt.t0+R.dur*.08',150000,1/30)")
    g.ev("setRoom('lounge')"); g.ev("for(let i=0;i<8;i++)__tick(1000/30)"); clean(g); g.page.wait_for_timeout(100)
    g.page.screenshot(path=OUT + '02_kt_the_whole_lounge.png'); print('  shot 02', g.ev("JSON.stringify({t:Math.round(R.t/R.dur*100),said:R.kt.said,in:R.groups.filter(q=>q.tasting&&q.table!=null).reduce((a,q)=>a+q.size,0)})"))
    crop(g, '02b_kt_tables_close.png', 40, 220, 200, 150, 3)
    crop(g, '02c_kt_bar_and_L_close.png', 90, 90, 290, 160, 3)
    print('errors', g.errors[:3]); g.close()
    # the chef's night
    g = rt.Game(b, port, 'index', seed=7621, manual=True, viewport={'width': 390, 'height': 844})
    v.load_save(g, 'player_day74_1508.json')
    g.ev("kenS().next=null;S.cn={n:1,last:S.day-9,next:{d:S.day,menu:cnMenu()}};showPrep()"); g.page.wait_for_timeout(150)
    g.ev("(()=>{const e=[...document.querySelectorAll('#screen .event')].find(e=>e.textContent.includes('主廚之夜'));if(e)e.scrollIntoView({block:'center'})})()"); clean(g)
    g.page.screenshot(path=OUT + '03_cn_news_tonight.png'); print('  shot 03')
    v.to_service(g); g.ev("window.__act=window.__actLazy")
    g.ev("__botUntil('R.cn&&R.cn.on&&R.cn.guests.filter(q=>q.ticket&&q.ticket.items.some(i=>i.course===1&&i.st===\"served\")).length>=5',150000,1/30)")
    g.ev("__botUntil('R.cn.guests.some(q=>q.ticket&&q.ticket.items.some(i=>i.cnp&&i.st===\"ready\"&&!i.picked))',30000,1/30)")
    g.ev("setRoom('lounge')"); g.ev("for(let i=0;i<4;i++)__tick(1000/30)"); clean(g); g.page.wait_for_timeout(100)
    g.page.screenshot(path=OUT + '04_cn_the_whole_lounge.png'); print('  shot 04', g.ev("JSON.stringify({t:Math.round(R.t/R.dur*100),in:R.groups.filter(q=>q.cn&&q.table!=null).reduce((a,q)=>a+q.size,0),waiting:R.cn.guests.reduce((a,q)=>a+(q.ticket?q.ticket.items.filter(i=>i.cnp&&i.st==='ready'&&!i.picked).length:0),0)})"))
    crop(g, '04b_cn_L_end_plates_close.png', 90, 120, 130, 140, 4)
    crop(g, '04c_cn_tables_close.png', 40, 220, 330, 200, 2)
    # the ticket rail: courses to come are dashed
    print('errors', g.errors[:3]); g.close(); b.close()
srv.shutdown()
