"""Every dish's plating drawn at three points of each of its plating beats (30 / 60 / 90%), with a hand there (so what the
hand carries to the plate, pours or cuts over it is drawn), for one portion (top row) and for two (bottom row): one grid per
dish. How the rule of docs/cooking/CHOREOGRAPHY.md 「裝盤時手上端的東西」 is checked — a whole piece is never in two places at
once (in the pan, in the air, on the plate) and never nowhere.
  python3 tools/qa/plating_sheet.py OUT DISH [DISH ...]"""
import sys, os, json, base64
wt = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); out = sys.argv[1]; DISHES = sys.argv[2:]
sys.path.insert(0, os.path.join(wt, 'tests')); os.chdir(wt)
import run_tests as rt
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont
os.makedirs(out, exist_ok=True)
JS = r"""(([d,M,pts])=>{const fl=wfFlow(d);const si=fl.indexOf('plate');const prev=fl[si-1];const slot=R.slots.find(s=>s.type===WF_ST[prev].slot);
 const H0=wfHandsAt;window.__hk=window.__hk||0;
 const cv=document.createElement('canvas');cv.width=360;cv.height=270;const c=cv.getContext('2d');const res=[];
 for(const h of pts){const its=[];for(let i=0;i<M;i++)its.push({it:{want:0,d}});
  const n={id:-7,d,n:M,its,seed:7,st:'work',f:'plate',si,act0:1,act:1-h,pas0:1,pas:0,dur:2,slot,who:'jill'};
  const sp=wfFoodSpot(n,slot);wfHandsAt=function(x){return x===n?{x:sp.x+18,y:sp.y+22,f:-1}:H0(x)};
  c.setTransform(1,0,0,1,0,0);c.fillStyle='#C9965F';c.fillRect(0,0,360,270);c.setTransform(3,0,0,3,0,0);c.translate(60-sp.x,58-sp.y);
  try{chDrawFood(c,n,slot,sp,(h*7)%10,true)}catch(e){res.push('ERR '+e.message);continue}finally{wfHandsAt=H0}
  res.push(cv.toDataURL('image/png'))}
 return JSON.stringify(res)})"""
srv, port = rt.start_server()
with sync_playwright() as p:
    b = p.chromium.launch()
    g = rt.Game(b, port, 'index', seed=9101, manual=True, viewport={'width': 390, 'height': 844})
    g.click('[data-act=open]'); g.page.wait_for_timeout(100)
    g.ev("S.eq.stove=2;S.eq.bar=Math.max(S.eq.bar,1);S.eq.prep=Math.max(S.eq.prep,1);S.eq.oven=Math.max(S.eq.oven,1);")
    rt.start_day(g); g.ev("setRoom('kitchen')")
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14) if os.path.exists('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf') else None
    for d in DISHES:
        beats = json.loads(g.ev(f"JSON.stringify((CH['{d}']&&CH['{d}'].plate?CH['{d}'].plate.hands:[]).map(b=>({{to:b.to,g:b.g,say:b.say}})))"))
        pts, labels = [], []; a = 0
        for bi, bt in enumerate(beats):
            for u in (.3, .6, .9):
                pts.append(a + u * (bt['to'] - a)); labels.append(f"b{bi+1} {bt['g']} {int(u*100)}%")
            a = bt['to']
        rows = []
        for M in (1, 2):
            imgs = json.loads(g.ev("(" + JS + ")(" + json.dumps([d, M, pts]) + ")"))
            rows.append(imgs)
        W, H = 360, 270; cols = len(pts)
        sheet = Image.new('RGB', (W * cols, (H + 20) * 2), 'white'); dr = ImageDraw.Draw(sheet)
        for r, imgs in enumerate(rows):
            for i, u in enumerate(imgs):
                x, y = i * W, r * (H + 20)
                if u.startswith('ERR'):
                    dr.text((x + 4, y + 30), u[:60], fill='red'); continue
                im = Image.open(__import__('io').BytesIO(base64.b64decode(u.split(',')[1])))
                sheet.paste(im, (x, y + 20)); dr.text((x + 4, y + 3), f"{d} x{r+1} {labels[i]}", fill='black')
        sheet.save(os.path.join(out, f'{d}_plating.png'))
        print(d, len(pts), 'points', [l for l in labels][:3], g.errors[:2])
    b.close()
