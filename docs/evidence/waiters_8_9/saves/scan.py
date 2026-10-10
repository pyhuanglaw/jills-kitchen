"""Every save in tests/saves/ (the user's own and the fixtures), loaded in this build: the staff before (the file) and after
(the game, once loaded): nobody lost, nobody doubled, every id kept, a name changed only where it was a role's name or a
numbered one (服務生8…), nobody called 服務生N after. The waiters' names in each, and who would be hired next.
  python3 docs/evidence/waiters_8_9/saves/scan.py OUT.txt     (from the repo root)"""
import sys, os, json, glob, re
OUT = sys.argv[1]; ROOT = os.getcwd(); sys.path.insert(0, os.path.join(ROOT, 'tests')); sys.argv = [sys.argv[0]]
import run_tests as rt
from playwright.sync_api import sync_playwright
ROLE_N = {'waiter': '服務生', 'chef': '廚師', 'cleaner': '清潔員'}
def numbered(nm, role):
    b = ROLE_N.get(role); return bool(b) and (nm == b or (nm.startswith(b) and nm[len(b):].isdigit()))
srv, port = rt.start_server(); lines = []; bad = 0
with sync_playwright() as p:
    b = p.chromium.launch()
    for f in sorted(glob.glob(os.path.join(ROOT, 'tests', 'saves', '*.json'))):
        raw = json.load(open(f, encoding='utf-8')); raw = raw.get('save', raw)
        before = [(m.get('id'), m.get('name'), m.get('role')) for m in raw.get('crew', [])]
        g = rt.Game(b, port, 'index', seed=930, manual=True, viewport={'width': 390, 'height': 844})
        g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.page.wait_for_timeout(150)
        g.click('[data-act=openFresh]') if g.page.query_selector('[data-act=openFresh]') else g.click('[data-act=open]'); g.page.wait_for_timeout(150)
        after = json.loads(g.ev("JSON.stringify(S.crew.map(m=>[m.id,m.name,m.role]))"))
        nxt = g.ev("(()=>{const used=S.crew.map(m=>m.name);const ln=LOUNGE_ROSTER.map(r=>r.name);return (CREW_NAMES.waiter||[]).find(n=>!used.includes(n)&&!ln.includes(n))||'(none)'})()")
        cap = g.ev("roleCrew('waiter').length+'/'+roleCap('waiter')")
        ids_b = {i: (n, r) for i, n, r in before}; ids_a = {i: (n, r) for i, n, r in after}
        lost = [i for i in ids_b if i not in ids_a]; added = [i for i in ids_a if i not in ids_b]
        renamed = [(ids_b[i][0], ids_a[i][0]) for i in ids_b if i in ids_a and ids_b[i][0] != ids_a[i][0]]
        bad_rename = [x for x in renamed if not numbered(x[0], ids_b[[i for i in ids_b if ids_b[i][0] == x[0]][0]][1])]
        names = [n for _, n, _ in after]; twice = sorted({n for n in names if names.count(n) > 1})
        num_after = [n for i, n, r in after if numbered(n, r)]
        ok = not lost and not twice and not bad_rename and not num_after and not g.errors
        added_ok = all(ids_a[i][1] == 'cleaner' and ids_a[i][0] == '秀琴阿姨' for i in added)   # 秀琴阿姨 joins old saves on load (xqCrewMig, 2026-10-10)
        ok = ok and added_ok
        bad += not ok
        waiters = [n for i, n, r in after if r == 'waiter']
        lines.append(f"{'OK  ' if ok else 'BAD '} {os.path.basename(f)}: {len(before)} → {len(after)} people"
                     + (f" (+{', '.join(ids_a[i][0] for i in added)})" if added else '')
                     + f"; renamed {renamed or 'nobody'}; waiters {cap} {waiters}; next waiter hired: {nxt}"
                     + (f"; LOST {lost}" if lost else '') + (f"; TWICE {twice}" if twice else '') + (f"; NUMBERED {num_after}" if num_after else '')
                     + (f"; errors {g.errors[:2]}" if g.errors else ''))
        print(lines[-1], flush=True); g.close()
    b.close()
srv.shutdown()
lines.append(f'\n{len(lines)} saves, {bad} not OK')
open(OUT, 'w', encoding='utf-8').write('\n'.join(lines) + '\n'); print(lines[-1])
