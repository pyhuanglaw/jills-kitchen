"""A new game's save on its Day 1 prep screen (before Madame Lin's Day 1 visit), for tools/sims/lin_chain.py to play the
whole Madame Lin line forward from the start.   python3 fresh_save.py ROOT OUT.json"""
import sys, os, json
ROOT = sys.argv[1]; OUT = sys.argv[2]
sys.path.insert(0, ROOT + '/tests'); os.chdir(ROOT)
import run_tests as rt
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    srv, port = rt.start_server(); b = p.chromium.launch()
    g = rt.Game(b, port, 'index', seed=9001, manual=True, viewport={'width': 390, 'height': 844})
    g.click('[data-act=open]'); g.page.wait_for_timeout(150)
    s = json.loads(g.ev("JSON.stringify(S)"))
    assert s['day'] == 1 and s.get('linMig') == 1 and not ((s.get('story') or {}).get('facts') or {}).get('lin_hello'), 'a new game, before Day 1'
    json.dump(s, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False)
    print('Day', s['day'], 'money', s['money'], 'errors', g.errors[:2])
    g.close(); b.close(); srv.shutdown()
