"""The Lounge's bar with every stool taken (the player's Day 74 save) at a given viewport, and close crops.
python3 shot_bar2.py ROOT OUT TAG [W H] [--empty]"""
import sys, os, base64
ROOT = sys.argv[1]; OUT = sys.argv[2].rstrip('/') + '/'; TAG = sys.argv[3]
W = int(sys.argv[4]) if len(sys.argv) > 4 else 390; H = int(sys.argv[5]) if len(sys.argv) > 5 else 844
EMPTY = '--empty' in sys.argv
sys.path.insert(0, ROOT + '/tests'); os.chdir(ROOT)
import run_tests as rt, v24_tests as v
from playwright.sync_api import sync_playwright
os.makedirs(OUT, exist_ok=True)
srv, port = rt.start_server()
def save_url(url, path): open(path, 'wb').write(base64.b64decode(url.split(',')[1])); print('  saved', os.path.basename(path), flush=True)
def crop(g, name, x, y, w, h, k=3):
    url = g.ev(f"(()=>{{const s=SV.s*DPR;const cv=document.createElement('canvas');cv.width={w}*{k};cv.height={h}*{k};const c=cv.getContext('2d');c.drawImage(sc,(SV.ox+({x})*SV.s)*DPR,(SV.oy+({y})*SV.s)*DPR,{w}*s,{h}*s,0,0,{w}*{k},{h}*{k});return cv.toDataURL('image/png')}})()")
    save_url(url, OUT + name)
with sync_playwright() as p:
    b = p.chromium.launch()
    g = rt.Game(b, port, 'index', seed=7603, manual=True, viewport={'width': W, 'height': H})
    v.load_save(g, 'player_day74_1508.json')
    v.to_service(g); g.ev("window.__act=()=>{}")
    g.ev("__botUntil('R.t>=R.dur*.5',90000,1/30)")
    g.ev("""(()=>{const bars=R.tables.filter(t=>t.room==='lounge'&&t.kind==='bar');for(const t of bars){if(t.group){const q=t.group;leaveGroup(q,'ok');q.gone=true;R.groups=R.groups.filter(x=>x!==q)}t.group=null;t.dirty=false;t.claim=null;t.plates=[]}})()""")
    if not EMPTY:
        g.ev("""(()=>{const bars=R.tables.filter(t=>t.room==='lounge'&&t.kind==='bar');let k=0;for(const t of bars){spawn({t:R.t,type:['office','gourmet','student','couple'][k%4],size:1,lounge:1});const q=R.groups[R.groups.length-1];if(q.table!=null&&R.tables[q.table]!==t){const t0=R.tables[q.table];t0.group=null;q.table=null}if(q.table==null)seatGroup(q,t);q.state='eat';q.timer=999;q.x=t.x;q.y=t.y+8;k++}})()""")
    g.ev("setRoom('lounge')"); g.ev("for(let i=0;i<10;i++)__tick(1000/30)"); g.ev("document.querySelectorAll('#plines>*,#toasts>*').forEach(e=>e.remove())")
    g.page.wait_for_timeout(100); g.page.screenshot(path=OUT + f'{TAG}_lounge.png')
    crop(g, f'{TAG}_bar_close.png', 90, 110, 290, 140, 3)
    crop(g, f'{TAG}_L_close.png', 90, 110, 110, 140, 4)
    print('errors', g.errors[:3]); g.close(); b.close()
srv.shutdown()
