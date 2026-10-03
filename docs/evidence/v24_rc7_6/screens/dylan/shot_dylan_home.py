"""Dylan's home clothes: a sheet (the restaurant look beside the home look, front, seated, from behind at the desk) and
Jill's room at 390x844 on the player's saves. python3 shot_dylan_home.py ROOT OUT"""
import sys, os, json, base64
ROOT = sys.argv[1]; OUT = sys.argv[2].rstrip('/') + '/'
sys.path.insert(0, ROOT + '/tests'); os.chdir(ROOT)
import run_tests as rt, v24_tests as v
from playwright.sync_api import sync_playwright
os.makedirs(OUT, exist_ok=True)
srv, port = rt.start_server()
def save_url(url, path): open(path, 'wb').write(base64.b64decode(url.split(',')[1])); print('  saved', os.path.basename(path), flush=True)
def crop(g, name, x, y, w, h, scale=3):
    url = g.ev(f"(()=>{{const s=SV.s*DPR;const cv=document.createElement('canvas');cv.width={w}*{scale};cv.height={h}*{scale};const c=cv.getContext('2d');c.drawImage(sc,(SV.ox+({x})*SV.s)*DPR,(SV.oy+({y})*SV.s)*DPR,{w}*s,{h}*s,0,0,{w}*{scale},{h}*{scale});return cv.toDataURL('image/png')}})()")
    save_url(url, OUT + name)
with sync_playwright() as p:
    b = p.chromium.launch()
    g = rt.Game(b, port, 'index', seed=7601, manual=True, viewport={'width': 900, 'height': 600})
    url = g.ev(r"""(()=>{const W=720,H=300;const cv=document.createElement('canvas');cv.width=W;cv.height=H;const c=cv.getContext('2d');c.fillStyle='#EFE6D8';c.fillRect(0,0,W,H);
      c.fillStyle='#2E2019';c.font='700 15px sans-serif';c.fillText('店裡（原本）',40,24);c.fillText('房間裡（新）',400,24);
      const put=(x,L,fn)=>{c.save();c.translate(x,0);fn(L);c.restore()};
      for(const [x0,L] of [[0,DYLAN.looks[0]],[360,DYLAN_HOME]]){
        c.save();c.translate(x0+60,250);c.scale(3,3);drawPerson(c,0,0,L,{pscale:1,mood:'happy'});c.restore();
        c.save();c.translate(x0+170,250);c.scale(3,3);drawPerson(c,0,0,L,{pscale:1,seated:true,lounge:{legs:0},mood:'happy',hold:'phone'});c.restore();
        c.save();c.translate(x0+280,250);c.scale(3,3);drawPersonBack(c,0,0,L,{headphones:true,s:1/PSC});c.restore()}
      c.font='600 12px sans-serif';c.fillText('站著',45,285);c.fillText('坐著',155,285);c.fillText('書桌前（背影）',245,285);c.fillText('站著',405,285);c.fillText('坐著',515,285);c.fillText('書桌前（背影）',605,285);
      return cv.toDataURL('image/png')})()""")
    save_url(url, OUT + '01_dylan_restaurant_and_home.png'); print('errors', g.errors[:3]); g.close()
    for name, save in (('d74', 'player_day74_1508.json'), ('d52', 'player_day52.json')):
        g = rt.Game(b, port, 'index', seed=7602, manual=True, viewport={'width': 390, 'height': 844})
        v.load_save(g, save)
        st = g.ev("JSON.stringify({day:S.day,stage:S.dylan.stage,phase})")
        g.ev("setRoom('home')"); g.ev("for(let i=0;i<8;i++)__tick(1000/30)"); g.ev("document.querySelectorAll('#plines>*,#toasts>*').forEach(e=>e.remove())")
        g.page.wait_for_timeout(100); g.page.screenshot(path=OUT + f'02_{name}_jills_room_prep.png'); print('  shot', name, st, 'desk', g.ev("!!homeDylanAtDesk()"))
        ch = json.loads(g.ev("JSON.stringify({x:HM.chair.x,y:HM.chair.y})"))
        crop(g, f'02b_{name}_the_desk_close.png', ch['x'] - 45, ch['y'] - 70, 90, 80, 4)
        print('errors', g.errors[:3]); g.close()
    b.close()
srv.shutdown()
