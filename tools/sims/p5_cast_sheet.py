"""v2.4 P5: the outside cast's sprites beside their portraits, to match one to the other by eye.

Each row: the portrait card (the player's sheet), the sprite drawn by the game's own drawPerson at 4× (the detail) and
at the size a phone shows it (the dining room's scale on a 390-wide screen), standing and seated.

  python3 tools/sims/p5_cast_sheet.py OUT.png [which]   # which: 'cast' (the P5 people, default) or 'hs' (every hair style)
"""
import sys, os, json, base64
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, os.path.join(ROOT, 'tests'))
import run_tests as rt
from playwright.sync_api import sync_playwright

OUT = sys.argv[1]
WHICH = sys.argv[2] if len(sys.argv) > 2 else 'cast'

JS = r"""((which)=>{
 const rows=which==='hs'?[0,1,2,3,4,5,6,7,8,9].map(h=>({n:'hs '+h,p:null,L:{skin:'#EDC19C',hair:'#4A2E1F',hs:h,top:'#7B8B6F',pants:'#3B3542'}}))
  :P5_CAST.map(k=>({n:k,p:NAMED[k]&&NAMED[k].p,L:NAMED[k].looks}));
 const RH=190,W=760;const cv=document.createElement('canvas');cv.width=W;cv.height=rows.length*RH;const c=cv.getContext('2d');
 c.fillStyle='#E9DFCF';c.fillRect(0,0,W,cv.height);
 const imgs=rows.map(r=>{if(!r.p)return null;const s=portraitData(r.p);if(!s)return null;const im=new Image();im.src=s;return im});
 return new Promise(res=>setTimeout(()=>{rows.forEach((r,i)=>{const y0=i*RH;c.fillStyle=i%2?'#E4D8C6':'#EFE6D8';c.fillRect(0,y0,W,RH);
   const im=imgs[i];if(im&&im.complete){const h=RH-14,w=im.width*h/im.height;c.drawImage(im,8,y0+7,w,h)}
   c.fillStyle='#2E2019';c.font='700 13px sans-serif';c.fillText(r.n,8,y0+RH-4);
   /* 4x standing, 4x seated */drawPerson(c,250,y0+RH-12,Object.assign({},r.L),{s:4/PSC*1,mood:'happy'});drawPerson(c,370,y0+RH-40,Object.assign({},r.L),{s:4/PSC,seated:true,mood:'happy'});
   /* the phone's size: the scene is drawn at about 390/400 of its units */const k=.975;for(let j=0;j<3;j++)drawPerson(c,470+j*40,y0+RH-30,Object.assign({},r.L),{s:k,mood:'happy',flip:j===1});
   c.fillStyle='#2E2019';c.font='600 10px sans-serif';c.fillText('phone size',470,y0+RH-8)});res(cv.toDataURL('image/png'))},300))})"""

with sync_playwright() as p:
    srv, port = rt.start_server(); b = p.chromium.launch()
    g = rt.Game(b, port, 'index', seed=1)
    data = g.page.evaluate('([js,w])=>window.__jk(js)(w)', [JS, WHICH])
    open(OUT, 'wb').write(base64.b64decode(data.split(',', 1)[1]))
    print('wrote', OUT)
    g.close(); b.close(); srv.shutdown()
