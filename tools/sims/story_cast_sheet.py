"""rc7 (the player, 15:38 「有劇情的npc在遊戲裡的臉和髮型可不可以特別一點 不要都跟別人一樣」): every guest with a story — the
regulars, the named guests — their portrait beside the sprite the game draws for them (4× and at a phone's size),
next to a row of generic guests the same day might bring, to see at a glance whether a story character looks like
anyone else.

  python3 tools/sims/story_cast_sheet.py OUT.png [generic|lineup]   # generic: a sheet of 40 generic guests instead;
                                                                     # lineup: the cast side by side at 2× and at a phone's
                                                                     # size, a row of strangers under them
"""
import sys, os, base64
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, os.path.join(ROOT, 'tests'))
import run_tests as rt
from playwright.sync_api import sync_playwright

OUT = sys.argv[1]
WHICH = sys.argv[2] if len(sys.argv) > 2 else 'cast'

JS = r"""((which)=>{
 const P={chen:'chen',mia:'reg23_mia',koba:'xiaolin',leo:'leo',sophie:'reg23_sophie',wang:'mr_wang',wangwife:'mrs_wang'};
 if(which==='lineup'){const cast=REGS.filter(r=>P[r.id]).map(r=>({n:r.n,L:r.looks[0]})).concat(Object.keys(NAMED).map(k=>({n:k.replace(/^(品酒師|美食部落客|吃貨|老饕) ?/,''),L:NAMED[k].looks})));
  const T=['office','student','gourmet','couple','family','vip','blogger'];const gen=[];for(let i=0;i<cast.length;i++){const L=makeLooks(T[i%T.length],1,'main')[0];gen.push(L)}
  const CW=62,W=cast.length*CW+20,H=330;const cv=document.createElement('canvas');cv.width=W;cv.height=H;const c=cv.getContext('2d');c.fillStyle='#EFE6D8';c.fillRect(0,0,W,H);
  c.fillStyle='#2E2019';c.font='700 12px sans-serif';c.fillText('有故事的客人（2×）',8,16);c.fillText('手機實際大小',8,184);c.fillText('一般客人（手機大小）',8,256);
  cast.forEach((r,i)=>{const x=20+CW/2+i*CW;drawPerson(c,x,150,Object.assign({},r.L),{s:2/PSC,mood:'happy'});c.fillStyle='#2E2019';c.font='600 10px sans-serif';const tw=c.measureText(r.n).width;c.fillText(r.n,x-tw/2,166);
   drawPerson(c,x,238,Object.assign({},r.L),{s:.975,mood:'happy'});drawPerson(c,x,316,Object.assign({},gen[i]),{s:.975,mood:'happy'})});
  return Promise.resolve(cv.toDataURL('image/png'))}
 let rows;
 if(which==='generic'){rows=[];const T=['office','student','gourmet','couple','family','vip','blogger'];for(let i=0;i<40;i++){const L=makeLooks(T[i%T.length],1,'main')[0];rows.push({n:T[i%T.length],p:null,L})}}
 else rows=REGS.filter(r=>P[r.id]).map(r=>({n:r.n,p:P[r.id],L:r.looks[0]})).concat(Object.keys(NAMED).map(k=>({n:k,p:NAMED[k].p,L:NAMED[k].looks})));
 const per=which==='generic'?8:1;const RH=which==='generic'?120:170,W=which==='generic'?760:640;const cv=document.createElement('canvas');cv.width=W;cv.height=Math.ceil(rows.length/per)*RH;const c=cv.getContext('2d');
 c.fillStyle='#E9DFCF';c.fillRect(0,0,W,cv.height);
 const imgs=rows.map(r=>{if(!r.p)return null;const s=portraitData(r.p);if(!s)return null;const im=new Image();im.src=s;return im});
 return new Promise(res=>setTimeout(()=>{
  if(which==='generic'){rows.forEach((r,i)=>{const x=50+(i%per)*90,y=Math.floor(i/per)*RH+RH-16;drawPerson(c,x,y,Object.assign({},r.L),{s:2.6/PSC,mood:'happy'})});return res(cv.toDataURL('image/png'))}
  rows.forEach((r,i)=>{const y0=i*RH;c.fillStyle=i%2?'#E4D8C6':'#EFE6D8';c.fillRect(0,y0,W,RH);
   const im=imgs[i];if(im&&im.complete){const h=RH-24,w=im.width*h/im.height;c.drawImage(im,8,y0+6,w,h)}
   c.fillStyle='#2E2019';c.font='700 13px sans-serif';c.fillText(r.n,8,y0+RH-5);
   drawPerson(c,230,y0+RH-12,Object.assign({},r.L),{s:3.6/PSC,mood:'happy'});drawPerson(c,330,y0+RH-36,Object.assign({},r.L),{s:3.6/PSC,seated:true,mood:'happy'});
   for(let j=0;j<3;j++)drawPerson(c,430+j*40,y0+RH-26,Object.assign({},r.L),{s:.975,mood:j===2?'ok':'happy',flip:j===1});
   c.fillStyle='#2E2019';c.font='600 10px sans-serif';c.fillText('phone size',430,y0+RH-6)});res(cv.toDataURL('image/png'))},400))})"""

with sync_playwright() as p:
    srv, port = rt.start_server(); b = p.chromium.launch()
    g = rt.Game(b, port, 'index', seed=1)
    data = g.page.evaluate('([js,w])=>window.__jk(js)(w)', [JS, WHICH])
    open(OUT, 'wb').write(base64.b64decode(data.split(',', 1)[1]))
    print('wrote', OUT)
    g.close(); b.close(); srv.shutdown()
