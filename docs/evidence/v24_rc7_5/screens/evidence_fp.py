"""rc7.5 first photo — the mid-build visual checkpoint (brief §31), headless Chromium at 390x844 (T, not O).
python3 evidence_fp.py ROOT OUTDIR [seed]"""
import sys, os, json, base64
ROOT = sys.argv[1]; OUT = sys.argv[2].rstrip('/') + '/'; SEED = int(sys.argv[3]) if len(sys.argv) > 3 else 7508
sys.path.insert(0, ROOT + '/tests'); os.chdir(ROOT)
import run_tests as rt, v24_tests as v
from playwright.sync_api import sync_playwright
os.makedirs(OUT, exist_ok=True)
srv, port = rt.start_server()
VP = {'width': 390, 'height': 844}
log = []
def save_url(url, path):
    open(path, 'wb').write(base64.b64decode(url.split(',')[1])); print('  saved', os.path.basename(path), flush=True)
def shot(g, name):
    g.page.wait_for_timeout(80); g.page.screenshot(path=OUT + name); print('  shot', name, flush=True)
def crop(g, name, x, y, w, h, scale=3):
    url = g.ev(f"(()=>{{const s=SV.s*DPR;const cv=document.createElement('canvas');cv.width={w}*{scale};cv.height={h}*{scale};const c=cv.getContext('2d');c.imageSmoothingEnabled=true;c.drawImage(sc,(SV.ox+({x})*SV.s)*DPR,(SV.oy+({y})*SV.s)*DPR,{w}*s,{h}*s,0,0,{w}*{scale},{h}*{scale});return cv.toDataURL('image/png')}})()")
    save_url(url, OUT + name)
with sync_playwright() as p:
    b = p.chromium.launch()
    # a new game, Day 1, played: the moment as it happens
    g = rt.Game(b, port, 'index', seed=SEED, manual=True, viewport=VP)
    g.ev("window.__firstPhoto=1")
    g.click('[data-act=open]'); g.page.wait_for_timeout(150)
    rt.start_day(g); rt.install_bot(g); g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy")
    done = set(); t_shot = None
    for i in range(1500):
        r = json.loads(g.ev("JSON.stringify({fp:R.jill.fp?R.jill.fp.phase:null,first:!!S.firstPhoto,pot:!!(S.firstPhoto&&S.firstPhoto.pot),t:+R.t.toFixed(2),x:R.jill.x,y:R.jill.y,lines:[...document.querySelectorAll('#plines>*')].length})"))
        if r['fp'] == 'go' and 'go' not in done and r['y'] < 330:
            done.add('go'); g.ev("__tick(1000/30)"); shot(g, '01_d1_jill_carries_the_herbs.png'); log.append(f"01 t={r['t']} going to the window, Jill at ({r['x']:.0f},{r['y']:.0f})")
        if r['fp'] == 'stand' and 'stand' not in done:
            done.add('stand'); g.ev("__tick(1000/30)"); shot(g, '02_d1_she_looks_at_them.png'); crop(g, '02b_d1_she_looks_at_them_close.png', 150, 60, 150, 112)
            log.append(f"02 t={r['t']} stopped, looking at the pot")
        if r['first'] and t_shot is None:
            t_shot = r['t']; g.ev("__tick(1000/30)"); shot(g, '03_d1_the_shutter.png'); log.append(f"03 t={r['t']} the shutter (the flash)")
            fs = json.loads(g.ev("JSON.stringify(R.fpShot)")); log.append(f"   the frame {fs['f']}, cats in it: {fs['cats']}")
        if t_shot is not None and 'l1' not in done and r['lines'] >= 1:
            done.add('l1'); shot(g, '04_d1_first_line.png')
        if t_shot is not None and 'l4' not in done and r['t'] > t_shot + 5.6:
            done.add('l4'); shot(g, '05_d1_four_lines_over_the_coach.png')
            ov = g.ev("(()=>{const c=$('#coach');const ls=[...document.querySelectorAll('#plines>*')];if(c.hidden)return 'coach hidden';const a=c.getBoundingClientRect();return ls.map(e=>{const b=e.getBoundingClientRect();return Math.round(b.top)+'-'+Math.round(b.bottom)}).join(',')+' / coach '+Math.round(a.top)+'-'+Math.round(a.bottom)})()")
            log.append(f"05 t={r['t']} lines vs coach (y ranges): {ov}")
        if r['fp'] == 'place' and 'place' not in done:
            done.add('place'); g.ev("__tick(1000/30)"); crop(g, '06_d1_onto_the_sill_close.png', 60, 0, 120, 112)
        if r['pot'] and 'pot' not in done:
            done.add('pot'); g.ev("for(let i=0;i<3;i++)__tick(1000/30)"); crop(g, '07_d1_the_pot_on_the_sill_close.png', 60, 0, 120, 112)
        if t_shot is not None and r['t'] > t_shot + 11.5 and 'l6' not in done:
            done.add('l6'); shot(g, '08_d1_all_the_lines.png')
        if 'l6' in done and 'pot' in done: break
        if t_shot is None: g.page.evaluate('()=>window.__bot(6,1/30)')
        else: g.ev("for(let i=0;i<6;i++)__tick(1000/30)")
    lines = g.ev("JSON.stringify(dayLog().filter(l=>['Jill','Dylan'].includes(l.w)).map(l=>l.c+' '+l.w+'：'+l.t))")
    log.append('the log: ' + lines)
    url = g.ev("(async()=>{const p=albumList().find(p=>p.kind==='first');return p?(p.img||await photoGet(p.id)):null})()")
    if url: save_url(url, OUT + '09_d1_the_photo.jpg')
    log.append('album[0]: ' + g.ev("JSON.stringify((({id,kind,day,clock,cap,keep,first})=>({id,kind,day,clock,cap,keep,first}))(albumList()[0]))"))
    # the rest of the day; the summary
    rt.play_day(g, max_steps=60000)
    for _ in range(200):
        if g.ev("phase") != 'service': break
        g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
    log.append('the day: phase %s, guests %s' % (g.ev("phase"), g.ev("(S.lastSummary||{}).guests")))
    g.ev("document.querySelectorAll('#toasts>*').forEach(e=>e.remove())"); shot(g, '10_d1_summary.png')
    # Jill's room that evening: the camera on the sill, the photo leaning on it
    if g.ev("phase") == 'summary': g.click('[data-act=toShop]'); g.page.wait_for_timeout(100)
    g.ev("hideScreen&&hideScreen();setRoom('home')"); g.ev("for(let i=0;i<6;i++)__tick(1000/30)")
    g.ev("document.querySelectorAll('#plines>*,#toasts>*').forEach(e=>e.remove())"); shot(g, '11_d1_evening_jills_room.png')
    hw = json.loads(g.ev("JSON.stringify({x0:HM.win.x0,y1:HM.win.y1})"))
    crop(g, '11b_d1_the_camera_and_the_photo_close.png', hw['x0'] - 10, hw['y1'] - 40, 90, 60, 4)
    log.append('errors: %s' % g.errors[:3]); g.close()

    # the player's Day 74 save: the photo as history
    g = rt.Game(b, port, 'index', seed=7510, manual=True, viewport=VP)
    raw = v.load_save(g, 'player_day74_1508.json')
    log.append('Day 74: album %d -> %d, S.firstPhoto %s' % (len(raw.get('album') or []), g.ev("albumList().length"), g.ev("JSON.stringify(S.firstPhoto)")))
    url = g.ev("(async()=>{const p=albumList().find(p=>p.kind==='first');return p?(p.img||await photoGet(p.id)):null})()")
    if url: save_url(url, OUT + '12_d74_the_photo_as_history.jpg')
    g.ev("bookTab='mem';showBook()"); g.page.wait_for_timeout(300); shot(g, '13_d74_album_top.png')
    g.ev("openLightbox('p1_first')"); g.page.wait_for_timeout(250); shot(g, '14_d74_lightbox.png')
    g.ev("lightboxStep(1)"); g.page.wait_for_timeout(200); shot(g, '15_d74_lightbox_next.png')
    g.ev("$('#lightbox').hidden=true;lightbox=null;closeSub&&closeSub()"); g.page.wait_for_timeout(100)
    g.ev("setRoom('home')"); g.ev("for(let i=0;i<6;i++)__tick(1000/30)"); g.ev("document.querySelectorAll('#plines>*,#toasts>*').forEach(e=>e.remove())")
    shot(g, '16_d74_jills_room.png')
    hw = json.loads(g.ev("JSON.stringify({x0:HM.win.x0,y1:HM.win.y1})"))
    crop(g, '16b_d74_the_camera_and_the_photo_close.png', hw['x0'] - 10, hw['y1'] - 40, 90, 60, 4)
    g.ev("setRoom('main')"); g.ev("for(let i=0;i<4;i++)__tick(1000/30)"); crop(g, '17_d74_main_window_no_pot_close.png', 60, 0, 120, 112)
    log.append('errors: %s' % g.errors[:3]); g.close()
    b.close()
srv.shutdown()
open(OUT + 'evidence_log.txt', 'w', encoding='utf-8').write('\n'.join(log) + '\n')
print('\n'.join(log))
