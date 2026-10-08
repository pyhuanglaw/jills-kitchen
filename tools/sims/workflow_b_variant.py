"""Workflow B's numbers, the way docs/cooking/WORKFLOW_B.md §9 measured them: a save's next evenings with the player who lets
the staff do their jobs (LAZY_ACTOR), the forty-days test's seeding (Math.random seeded per evening), and a variant patched
in after each day starts (JS run through the game's own eval, e.g. "DD_CAP[0]=20;" or "S.ops.dish=1;"). One JSON line per
evening: guests, lost, revenue, the dirty dishes (R.st.dd), each role's evening (R.st.wl), the pass, the waiters' trips.
  python3 tools/sims/workflow_b_variant.py WORKTREE SAVE SEEDBASE DAYS NAME OUT.jsonl [JS]
  SAVE: a file in tests/saves (player_day52.json, player_day30.json, ...)"""
import sys, os, json
ROOT, SAVE, BASE, DAYS, NAME, OUT = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5], sys.argv[6]
JS = sys.argv[7] if len(sys.argv) > 7 else ''
sys.path.insert(0, os.path.join(ROOT, 'tests')); os.chdir(ROOT)
import run_tests as rt
import v24_tests as vt
from playwright.sync_api import sync_playwright
ST = """JSON.stringify((()=>{const st=R.st||{};return{t:+R.t.toFixed(0),guests:st.guests,lost:st.lost,dd:st.dd||null,wl:st.wl||null,ps:st.ps||null,wb:st.wb||null,
 dirtyNow:R.tables.filter(t=>t.dirty&&!t.group).length}})())"""
SAMPLE = "R.tables.filter(t=>t.dirty&&!t.group).length"
with sync_playwright() as p:
    srv, port = rt.start_server(); b = p.chromium.launch()
    g = rt.Game(b, port, 'index', seed=254 if SAVE == 'player_day52.json' else BASE, manual=True, viewport={'width': 390, 'height': 844})
    vt.load_save(g, SAVE); g.ev("window.__fastSay=1")
    seed = "Math.random=(function(){let a=%d;return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
    for d in range(DAYS):
        if g.ev("phase") == 'summary': g.click('[data-act=toShop]'); g.page.wait_for_timeout(60)
        if g.ev("phase") == 'shop': g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(100)
        g.ev(seed % (BASE + d)); g.ev("S.today.sugKey=null;S.today.sug=null;autoStock()")
        if g.ev("phase") != 'service': rt.start_day(g)
        rt.install_bot(g); g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;window.__noScenes=true")
        if SAVE != 'player_day52.json': g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}")   # as the runs in §9 did
        if JS: g.ev(JS)
        last = None; dsum = 0; n = 0
        for _ in range(1200):
            r = g.page.evaluate('()=>window.__bot(30,1/30)')
            if g.ev("phase") != 'service' or not g.ev("!!R"): break
            last = json.loads(g.ev(ST)); dsum += last['dirtyNow']; n += 1
            if r['ticks'] < 30: break
        if g.ev("phase") == 'service':
            g.ev("closeShop('x');for(const q of R.groups.slice())leaveGroup(q,'ok')"); g.page.evaluate('()=>window.__bot(400,1/30)')
        if g.ev("phase") == 'service': g.ev("finishClosing()")
        summ = json.loads(g.ev("JSON.stringify(S.lastSummary&&{day:S.day,guests:S.lastSummary.guests,lost:S.lastSummary.lost,rev:S.lastSummary.rev})"))
        rec = {'name': NAME, 'base': BASE, 'day': d, 'summary': summ, 'end': last, 'dirtyAvg': round(dsum / max(1, n), 2)}
        open(OUT, 'a').write(json.dumps(rec) + '\n')
        print(NAME, BASE, d, summ, 'dirtyAvg', rec['dirtyAvg'], flush=True)
    g.close(); b.close(); srv.shutdown()
