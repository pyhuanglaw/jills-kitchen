"""golden_frames re-record evidence: run the same two days, compare EVERY sample key by key with the recorded baseline
(not only the first differing one), the frames and the end-of-day digests; save the three differing screens (golden,
actual, a difference image) for inspection. usage: gf_verify.py OUTDIR"""
import sys, os, json
ROOT = os.environ.get('GF_ROOT', '/home/claude/jills-kitchen-project'); sys.path.insert(0, os.path.join(ROOT, 'tests'))
import run_tests as rt
from playwright.sync_api import sync_playwright
from io import BytesIO
from PIL import Image, ImageChops
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
with sync_playwright() as p:
    srv, port = rt.start_server(); b = p.chromium.launch()
    g = rt.Game(b, port, 'index', seed=2024, manual=True)
    rt.install_bot(g)
    shots, trace = [], {}
    def shot(name):
        g.ev("__tick(1000/30)"); shots.append((name, g.page.screenshot(animations='disabled', caret='hide')))
    g.ev("__tick(500)"); shot('title')
    g.click('[data-act=open]'); g.ev("__tick(1000/30)"); shot('prep')
    for d in range(2):
        rt.start_day(g)
        r1 = g.ev("__play(600, 30)")
        if d == 0:
            shot('service_20s')
            r1['samples'] += g.ev("__play(900, 30, 'R.slots.some(s=>s.job)')")['samples']
            g.ev("(()=>{const i=R.slots.findIndex(s=>s.job);R.focus=i;R.panel=true})()"); shot('service_panel'); g.ev("R.panel=false")
            g.page.click('#hPause'); shot('pause'); g.click('[data-act=resume]')
        r2 = g.ev("__play(20000, 30, 'R.closing!=null&&R.closing>5')")
        if d == 0: shot('evening')
        r3 = g.ev("__play(20000, 30)")
        trace[f'day{d+1}'] = {'samples': r1['samples'] + r2['samples'] + r3['samples'], 'frames': r1['frames'] + r2['frames'] + r3['frames'], 'digest': g.page.evaluate('window.__digest()')}
        if d == 0:
            shot('summary'); g.click('[data-act=toShop]'); shot('shop'); g.click('[data-act=nextDay]')
            g.click('[data-act=book]'); g.click('[data-act=btab][data-k=cats]'); shot('book_cats')
            g.click('[data-act=btab][data-k=mem]'); shot('book_mem'); g.click('[data-act=closeSub]')
        else:
            g.click('[data-act=toShop]'); g.click('[data-act=nextDay]')
    errs = g.errors[:]
    g.close(); b.close(); srv.shutdown()
want = json.load(open(rt.GOLDEN_FRAMES, encoding='utf-8'))
rep = {'errors': errs, 'days': {}}
for day in want:
    a, w = trace[day], want[day]
    keys = {}
    for i, (x, y) in enumerate(zip(a['samples'], w['samples'])):
        for k in y:
            if x.get(k) != y[k]: keys.setdefault(k, []).append(i)
    rep['days'][day] = {'frames': [a['frames'], w['frames']], 'samples': [len(a['samples']), len(w['samples'])],
                        'differing_keys': {k: {'count': len(v), 'first': v[0]} for k, v in keys.items()},
                        'digest_differs': [k for k in w['digest'] if a['digest'].get(k) != w['digest'][k]]}
screens = {}
for name, png in shots:
    path = os.path.join(rt.SCREENS, name + '.png')
    A = Image.open(BytesIO(png)).convert('RGB'); W = Image.open(path).convert('RGB')
    box = ImageChops.difference(A, W).getbbox() if A.size == W.size else None
    screens[name] = box
    if box:
        A.save(os.path.join(OUT, f'{name}.actual.png')); W.save(os.path.join(OUT, f'{name}.golden.png'))
        D = ImageChops.difference(A, W).convert('L').point(lambda v: 255 if v > 8 else 0)
        Image.composite(Image.new('RGB', A.size, '#E0303A'), A.point(lambda v: v // 3 + 140), D).save(os.path.join(OUT, f'{name}.diff.png'))
rep['screens'] = screens
json.dump(rep, open(os.path.join(OUT, 'report.json'), 'w'), indent=1)
print(json.dumps(rep, indent=1))
