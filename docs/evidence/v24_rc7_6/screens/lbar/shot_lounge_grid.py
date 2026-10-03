"""The Lounge on the player's Day 74 save, with a logical-coordinate grid drawn over it (design aid, never shipped).
python3 shot_lounge_grid.py ROOT OUT TAG [W H]"""
import sys, os
ROOT = sys.argv[1]; OUT = sys.argv[2].rstrip('/') + '/'; TAG = sys.argv[3]
W = int(sys.argv[4]) if len(sys.argv) > 4 else 390; H = int(sys.argv[5]) if len(sys.argv) > 5 else 844
sys.path.insert(0, ROOT + '/tests'); os.chdir(ROOT)
import run_tests as rt, v24_tests as v
from playwright.sync_api import sync_playwright
os.makedirs(OUT, exist_ok=True)
srv, port = rt.start_server()
with sync_playwright() as p:
    b = p.chromium.launch()
    g = rt.Game(b, port, 'index', seed=7603, manual=True, viewport={'width': W, 'height': H})
    v.load_save(g, 'player_day74_1508.json')
    v.to_service(g); g.ev("window.__act=()=>{}")
    g.ev("__botUntil('R.t>=R.dur*.5',90000,1/30)")
    g.ev("setRoom('lounge')"); g.ev("for(let i=0;i<10;i++)__tick(1000/30)")
    g.ev("document.querySelectorAll('#plines>*,#toasts>*,#tickets>*').forEach(e=>e.remove())")
    print('DY', g.ev('DY'), 'LH', g.ev('LH'), 'SV', g.ev('JSON.stringify(SV)'), 'lv', g.ev('loungeLv()'), 'tv', g.ev("lgFurnOn('tv')"))
    print('lounge tables', g.ev("JSON.stringify(R.tables.filter(t=>t.room==='lounge').map(t=>[t.kind,Math.round(t.x),Math.round(t.y),t.seats]))"))
    g.page.wait_for_timeout(100)
    g.page.screenshot(path=OUT + f'{TAG}_plain.png')
    g.ev("""(()=>{window.__grid=1;const c=sc.getContext('2d');c.save();c.setTransform(DPR,0,0,DPR,0,0);c.font='9px sans-serif';
      for(let x=0;x<=400;x+=20){const X=SV.ox+x*SV.s;c.strokeStyle=x%100===0?'rgba(255,60,60,.8)':'rgba(255,255,255,.25)';c.lineWidth=x%100===0?1.2:.6;c.beginPath();c.moveTo(X,0);c.lineTo(X,SV.h);c.stroke();if(x%40===0){c.fillStyle='#ff0';c.fillText(String(x),X+1,SV.h-4)}}
      for(let y=0;y<=LH;y+=20){const Y=SV.oy+y*SV.s;c.strokeStyle=y%100===0?'rgba(60,160,255,.9)':'rgba(255,255,255,.25)';c.lineWidth=y%100===0?1.2:.6;c.beginPath();c.moveTo(0,Y);c.lineTo(SV.w,Y);c.stroke();if(y%40===0){c.fillStyle='#0ff';c.fillText(String(y),2,Y-1)}}
      c.restore()})()""")
    g.page.screenshot(path=OUT + f'{TAG}_grid.png')
    print('errors', g.errors[:3]); g.close(); b.close()
srv.shutdown()
