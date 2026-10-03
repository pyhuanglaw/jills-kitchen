"""The Lounge's bar, every stool taken (the player's Day 74 save), at 390x844. python3 shot_bar.py ROOT OUT TAG"""
import sys, os, json, base64
ROOT = sys.argv[1]; OUT = sys.argv[2].rstrip('/') + '/'; TAG = sys.argv[3]
sys.path.insert(0, ROOT + '/tests'); os.chdir(ROOT)
import run_tests as rt, v24_tests as v
from playwright.sync_api import sync_playwright
os.makedirs(OUT, exist_ok=True)
srv, port = rt.start_server()
def save_url(url, path): open(path, 'wb').write(base64.b64decode(url.split(',')[1])); print('  saved', os.path.basename(path), flush=True)
with sync_playwright() as p:
    b = p.chromium.launch()
    g = rt.Game(b, port, 'index', seed=7603, manual=True, viewport={'width': 390, 'height': 844})
    v.load_save(g, 'player_day74_1508.json')
    v.to_service(g); g.ev("window.__act=()=>{}")
    g.ev("__botUntil('R.t>=R.dur*.5',90000,1/30)")
    n = g.ev("""(()=>{const bars=R.tables.filter(t=>t.room==='lounge'&&t.kind==='bar');for(const t of bars){if(t.group){const q=t.group;leaveGroup(q,'ok');q.gone=true;R.groups=R.groups.filter(x=>x!==q)}t.group=null;t.dirty=false;t.claim=null;t.plates=[]}
      let k=0;for(const t of bars){spawn({t:R.t,type:['office','gourmet','student','couple'][k%4],size:1,lounge:1});const q=R.groups[R.groups.length-1];if(q.table!=null&&R.tables[q.table]!==t){const t0=R.tables[q.table];t0.group=null;q.table=null}if(q.table==null)seatGroup(q,t);q.state='eat';q.timer=999;q.x=t.x;q.y=t.y;k++}return bars.map(t=>t.x)})()""")
    print('stools x', n)
    g.ev("setRoom('lounge')"); g.ev("for(let i=0;i<10;i++)__tick(1000/30)"); g.ev("document.querySelectorAll('#plines>*,#toasts>*').forEach(e=>e.remove())")
    g.page.wait_for_timeout(100); g.page.screenshot(path=OUT + f'{TAG}_lounge_bar_full.png')
    url = g.ev("(()=>{const s=SV.s*DPR;const x=180,y=120,w=200,h=130,sc3=3;const cv=document.createElement('canvas');cv.width=w*sc3;cv.height=h*sc3;const c=cv.getContext('2d');c.drawImage(sc,(SV.ox+x*SV.s)*DPR,(SV.oy+y*SV.s)*DPR,w*s,h*s,0,0,w*sc3,h*sc3);return cv.toDataURL('image/png')})()")
    save_url(url, OUT + f'{TAG}_lounge_bar_close.png')
    print('errors', g.errors[:3]); g.close(); b.close()
srv.shutdown()
