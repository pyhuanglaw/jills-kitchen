"""qa_waiting_staff_do_not_stand_on_one_spot's own loop (Day 92 → the next service, the lazy player, a look a second for 60 s), over
Player seeds: at each look, pairs of staff with no task within 6 px — all of them (the test's count), and those where both are
standing at the place they are going to (waiting there, not walking past).  JK_GAME_JS picks the build.  python3 sweep.py SEED..."""
import sys, os, json
ROOT='/home/user/jills-kitchen'; sys.path.insert(0, os.path.join(ROOT,'tests')); os.chdir(ROOT); seeds=[int(x) for x in sys.argv[1:]]; sys.argv=[sys.argv[0]]
import run_tests as rt, qa_tests as q
from player import Player
from playwright.sync_api import sync_playwright
srv, port = rt.start_server()
with sync_playwright() as pw:
    b = pw.chromium.launch()
    for seed in seeds:
        p = Player(b, port, 'index', save=q.LATE, seed=seed)
        q._to_service_from_late(p)
        rt.install_bot(p.g); p.ev(rt.LAZY_ACTOR); p.ev("window.__act=window.__actLazy")
        anyp, still, ex = 0, 0, []
        for k in range(60):
            p.settle(); p.ev("for(let i=0;i<30;i++){__act();__tick(1000/30)}")
            r = json.loads(p.ev("""JSON.stringify((()=>{const W=Object.entries(R.cw||{}).filter(([id,w])=>!w.task&&(w.room||'main')==='main');let n=0,s=0;const ex=[];
              const at=w=>w.tx==null||Math.hypot(w.x-w.tx,w.y-w.ty)<3;
              for(let i=0;i<W.length;i++)for(let j=i+1;j<W.length;j++){const a=W[i][1],c=W[j][1];if(Math.hypot(a.x-c.x,a.y-c.y)<6){n++;if(at(a)&&at(c))s++;ex.push([W[i][0],W[j][0],at(a),at(c)])}}return{n,s,ex}})())"""))
            anyp += r['n']; still += r['s']
            if r['ex']: ex.append([k] + r['ex'])
        print(json.dumps({'seed': seed, 'looks_with_a_pair': sum(1 for e in ex), 'pairs_any': anyp, 'pairs_both_waiting_at_their_place': still, 'examples': ex[:4]}), flush=True)
        p.close()
    b.close()
srv.shutdown()
