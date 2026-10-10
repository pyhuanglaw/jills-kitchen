"""The reveal night on seeds (the run_tests scenario, checks off): where she says 「老公」 — how far from him, which act, rooms.
On the build in JK_GAME_JS."""
import sys, os, json
ROOT='/home/user/jills-kitchen'; sys.path.insert(0, os.path.join(ROOT,'tests')); os.chdir(ROOT)
TAG=sys.argv[1]; SEEDS=[int(x) for x in sys.argv[2].split(',')]; sys.argv=[sys.argv[0]]
import run_tests as rt
from playwright.sync_api import sync_playwright
srv, port = rt.start_server()
with sync_playwright() as p:
    b = p.chromium.launch()
    for seed in SEEDS:
        g = rt.Game(b, port, 'index', seed=seed, manual=True)
        try:
            ra, beside, elsewhere = rt.dylan_reveal_scenario(g, checks=False)
            rv = g.page.evaluate('window.__rv||null')
        except Exception as e:
            ra, beside, rv = None, None, {'error': str(e)[:200]}
        print(json.dumps({'tag':TAG,'seed':seed,'revealed_at':ra,'beside':beside,'rv':rv,'errors':g.errors[:2]}, ensure_ascii=False), flush=True)
        g.close()
    b.close()
srv.shutdown()
