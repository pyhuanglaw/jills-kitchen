"""python3 cmp.py DIR (here: python3 cmp.py .) — the controlled-weather sweep: per seed base, main and new side by side (the beats, targets met, whether
the planned weather was the same), then the means and the pre-declared rule's numbers."""
import json, sys, glob, os, statistics as st
D = sys.argv[1]
def targets(d):
    F = d['F']; first = d['first']; miss = []
    if any(v is None for v in F.values()): miss.append('missing:' + ','.join(k for k, v in F.items() if v is None))
    if not (F['yj_key'] is not None and F['yj_key'] - F['yj_meet'] <= 9 and F['yj_key'] <= first + 10): miss.append('move')
    if not (F['wall_worry'] is not None and first + 9 <= F['wall_worry'] <= first + 13): miss.append('wall62-66')
    if not (F['wall_settle'] is not None and F['wall_settle'] - F['wall_worry'] <= 18 and F['wall_settle'] <= first + 29): miss.append('settle')
    if F['wall_worry'] is not None and F['yj_key'] is not None and F['wall_worry'] < F['yj_key'] + 2: miss.append('order')
    return miss
rows = {}
for f in sorted(glob.glob(os.path.join(D, '*_*.json'))):
    tag, base = os.path.basename(f)[:-5].rsplit('_', 1); tag = tag.split('_')[0]   # main_8298e18_7000 -> main, 7000
    try: rows.setdefault(tag, {})[int(base)] = json.load(open(f))
    except Exception: pass
K = ['yj_key', 'wall_worry', 'wall_photos', 'wall_visit', 'wall_settle', 'wall_article']
bases = sorted(set(rows.get('main', {})) & set(rows.get('new', {})))
for b in bases:
    m, n = rows['main'][b], rows['new'][b]
    same = sum(1 for x, y in zip(m['wx'], n['wx']) if x[1] == y[1]); tot = min(len(m['wx']), len(n['wx']))
    fmt = lambda d: '/'.join(str(d['F'][k]) for k in K)
    print(f"{b}: main {fmt(m)} {'ALL' if not targets(m) else 'miss ' + ','.join(targets(m))}  |  new {fmt(n)} {'ALL' if not targets(n) else 'miss ' + ','.join(targets(n))}  |  same planned weather {same}/{tot}"
          f"  | evenings main {m['evenings']['g']}/{m['evenings']['l']}/{m['evenings']['a']} new {n['evenings']['g']}/{n['evenings']['l']}/{n['evenings']['a']}")
print('(key/worry/photos/visit/settle/article)')
for tag in ['main', 'new']:
    R = [rows[tag][b] for b in bases]
    if not R: continue
    mean = lambda k: st.mean(r['F'][k] for r in R if r['F'][k] is not None)
    gap = lambda a, z: st.mean(r['F'][z] - r['F'][a] for r in R)
    ev = lambda k: st.mean(r['evenings'][k] for r in R)
    print(f"{tag} ({len(R)}): key {mean('yj_key'):.2f}, worry {mean('wall_worry'):.2f}, settle {mean('wall_settle'):.2f}, article {mean('wall_article'):.2f}"
          f" | photos-worry {gap('wall_worry','wall_photos'):.2f}, visit-photos {gap('wall_photos','wall_visit'):.2f}"
          f" | every target {sum(1 for r in R if not targets(r))} of {len(R)} | evenings {ev('g'):.1f} guests, {ev('l'):.1f} lost, {ev('a'):.1f} angry, ${ev('r'):,.0f}")
both = [b for b in bases if not targets(rows['main'][b]) and not targets(rows['new'][b])]
print('every target on both:', both)
