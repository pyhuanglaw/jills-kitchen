"""rc8.4 extra live check: the player's Day 89 save on the published page — the album's three 品酒之夜 photos and the
story page's 「看插圖」 for the second and third nights.  python3 live_album_check.py LIVE.html SAVE.json OUT_DIR"""
import sys, os, json
ROOT = '/home/user/jills-kitchen-lin-restore/project_git'; sys.path.insert(0, os.path.join(ROOT, 'tests'))
import run_tests as rt
from playwright.sync_api import sync_playwright

LIVE, SAVE, OUT = sys.argv[1:4]
os.makedirs(OUT, exist_ok=True)
html = open(LIVE, encoding='utf-8').read()
raw = json.load(open(SAVE)); save = raw.get('save', raw)
notes = []
def note(s): print(s, flush=True); notes.append(s)

srv, port = rt.start_server()
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
    page = ctx.new_page(); errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.route('**/live.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=rt.inject(html)))
    page.route('https://fonts.googleapis.com/**', lambda r: r.abort())
    page.route('https://fonts.gstatic.com/**', lambda r: r.abort())
    page.add_init_script("(function(){if(!sessionStorage.getItem('__seeded')){localStorage.clear();localStorage.setItem(%s,%s);sessionStorage.setItem('__seeded','1')}})();"
                         % (json.dumps(rt.SAVE_KEY), json.dumps(json.dumps(save, ensure_ascii=False))))
    page.goto(f'http://127.0.0.1:{port}/live.html'); page.wait_for_function('typeof window.__jk==="function"'); page.wait_for_timeout(1500)
    ev = lambda js: page.evaluate('c=>window.__jk(c)', js)
    note('the title: ' + ev("JSON.stringify({phase,day:S.day})"))
    days = ev("JSON.stringify(['ken_t1','ken_t2','ken_t3'].map(k=>fact(k).d))")
    alb = ev("JSON.stringify(['ken_night1','ken_night2','ken_night3'].map(k=>{const p=albumList().find(x=>x.kind==='story:'+k);return p?{day:p.day,cap:p.cap}:null}))")
    ill = ev("JSON.stringify(['ken_t2','ken_t3'].map(k=>(story().illus||{})[k]||null))")
    note(f'the nights: Day {days}; the album at the title: {alb}; the story page\'s pictures seen on: {ill}')
    # 「不繼續，從開店前重來」: the prep screen, where a waiting story photo joins the album
    page.click('[data-act=openFresh]') if page.query_selector('[data-act=openFresh]') else page.click('[data-act=open]'); page.wait_for_timeout(800)
    alb = ev("JSON.stringify(['ken_night1','ken_night2','ken_night3'].map(k=>{const p=albumList().find(x=>x.kind==='story:'+k);return p?{day:p.day,cap:p.cap}:null}))")
    note('the prep screen (' + ev("JSON.stringify({phase,day:S.day})") + f'): the album: {alb}')
    # the album, at the first of the three
    ev("bookTab='mem';showBook()"); page.wait_for_timeout(600)
    pid = ev("(albumList().find(x=>x.kind==='story:ken_night1')||{}).id")
    ev(f"(()=>{{const sh=screenEl.querySelector('.sheet'),el=screenEl.querySelector('.polaroid[data-k=\"{pid}\"]');if(sh&&el)sh.scrollTop=Math.max(0,el.getBoundingClientRect().top-sh.getBoundingClientRect().top+sh.scrollTop-72)}})()")
    page.wait_for_timeout(800); page.screenshot(path=os.path.join(OUT, 'album_night1.png')); note('album_night1.png: the album at Day 78 (剛開始辦)')
    for k, n in (('ken_night2', 'album_night2.png'), ('ken_night3', 'album_night3.png')):
        pid = ev(f"(albumList().find(x=>x.kind==='story:{k}')||{{}}).id")
        ev(f"(()=>{{const sh=screenEl.querySelector('.sheet'),el=screenEl.querySelector('.polaroid[data-k=\"{pid}\"]');if(sh&&el)sh.scrollTop=Math.max(0,el.getBoundingClientRect().top-sh.getBoundingClientRect().top+sh.scrollTop-72)}})()")
        page.wait_for_timeout(800); page.screenshot(path=os.path.join(OUT, n)); note(f'{n}: the album at the {k} photo')
    # the story page: Ken's line, then the second night's picture again
    ev("closeSub&&closeSub()"); page.wait_for_timeout(200)
    ev("illusOpen('ken_t2')"); page.wait_for_timeout(900); page.screenshot(path=os.path.join(OUT, 'illus_again_t2.png')); note('illus_again_t2.png: 「看插圖」 — the second night')
    b.close()
srv.shutdown()
note(f'page errors: {len(errors)} {errors[:3]}')
open(os.path.join(OUT, 'album_check.txt'), 'w', encoding='utf-8').write('\n'.join(notes) + '\n')
