"""The card test's scenario (tests/cooking_tests.py cooking_the_card_says_who_has_it_and_a_dish_can_be_taken_back) on many
seeds, up to the take-back and a few frames after: one JSON line a seed — was Jill on a floor trip at the tap, what the card
said at the tap and in the frames after, and whether the take-back itself was right.
python3 sweep.py ROOT GAME_JS SEED0 SEED1"""
import sys, os, json
ROOT, GAME, A, B = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]); sys.path.insert(0, os.path.join(ROOT, 'tests')); os.chdir(ROOT)
os.environ['JK_GAME_JS'] = GAME; sys.argv = [sys.argv[0]]
import run_tests as rt
import cooking_tests as ct
from playwright.sync_api import sync_playwright
srv, port = rt.start_server()
with sync_playwright() as p:
    b = p.chromium.launch()
    for seed in range(A, B + 1):
        out = {'seed': seed}
        try:
            ADE = "{id:'t_ade',role:'chef',name:'阿德師傅',lv:3,duty:'bar',since:1,days:0,pool:'restaurant'}"
            g = ct._day(b, port, 'index', seed, f"S.level=3;S.eq.bar=1;S.crew.push({ADE})")
            g.ev("window.__patient=1")
            g.ev("window.__hold=true;{const W=wfStaff;wfStaff=function(){if(window.__hold)return;return W.apply(this,arguments)}}")
            if not ct._wait_orders(g, 1): out['skip'] = 'no order'; print(json.dumps(out, ensure_ascii=False), flush=True); g.close(); continue
            nid = g.ev("(()=>{wfGather();return wfList()[0].id})()")
            g.ev(f"(()=>{{const n=wfNode({nid});wfSelectItem(n.its[0].tk,n.its[0].it)}})()"); g.ev("__run(1)")
            g.ev("window.__hold=false")
            if not ct._until(g, f"wfNode({nid}).who==='t_ade'", step=1): out['skip'] = 'the cook did not take it'; print(json.dumps(out, ensure_ascii=False), flush=True); g.close(); continue
            g.ev("__run(4)")
            if g.ev(f"wfNode({nid}).st") != 'go': out['skip'] = 'the cook already started'; print(json.dumps(out, ensure_ascii=False), flush=True); g.close(); continue
            out['jill_at_tap'] = json.loads(g.ev("JSON.stringify({cur:R.jill.cur?R.jill.cur.t:null,q:R.jill.q.length,room:R.jill.room||'main'})"))
            ct._tap_slot(g, f"wfNode({nid}).to")
            st = json.loads(g.ev(f"JSON.stringify((()=>{{const n=wfNode({nid});return{{who:n.who,st:n.st,si:n.si,its:n.its.map(o=>o.it.st),cook:(R.wfc||{{}}).t_ade||null,q:wfJ().wq.includes({nid}),ck:(n.ck||[]).length}}}})())"))
            out['taken_back_ok'] = st['who'] == 'jill' and st['st'] == 'go' and st['si'] == 0 and all(x == 'cooking' for x in st['its']) and st['cook'] is None and st['q'] and not st['ck']
            line = lambda: (lambda gt: gt.split('\n')[3] if gt.count('\n') >= 3 else gt)(g.ev(ct.GUIDE))
            cards = [line()]
            first = 0 if 'Jill 前往中' in cards[0] else None
            for k in range(1, 301):
                g.ev("__run(1)"); c = line(); cards.append(c)
                if first is None and 'Jill 前往中' in c: first = k
                if first is not None and k >= first + 3: break
            out['card_at_tap'] = cards[0]; out['first_on_her_way'] = first
            out['kinds'] = sorted(set(c.split('·')[-1].strip() if '·' in c else c for c in cards))
            out['jill_trip'] = g.ev("JSON.stringify(R.jill.cur?{t:R.jill.cur.t}:null)")
            g.close()
        except Exception as e:
            out['error'] = str(e)[:200]
        print(json.dumps(out, ensure_ascii=False), flush=True)
    b.close()
srv.shutdown()
