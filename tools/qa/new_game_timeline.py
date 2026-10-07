"""新玩家時間表 — 真人玩家版 (QA, 2026-10-06). On which day does a person who starts on Day 1 meet each story, and what does
the money do along the way?

The user, 2026-10-06: 「真人玩家 timeline 的決策與操作，原則上只能根據玩家在當下畫面上實際看得到、按得到的資訊進行」. So the
day is played the way a person plays it, with the three parts of tools/qa/sim_player.py kept apart:

  A. 玩家行為 — the prep screen (tonight's menu, 「一鍵補到建議量」 paid like any purchase, 開始營業), the story panels read
     line by line, the summary read and lingered on, the shop's tabs opened and bought from — every decision from what
     the screen shows, every action a real tap on a control that is there. Policies: normal (合理玩家模擬, default),
     baseline (刻意不投資的 baseline).
  C. 營業中的手 — the service: --service human (一般玩家節奏, default), perfect (完美操作玩家), staff (讓員工做、Jill 補位).
     The closing is played to its end with the evening's life running (the stories told then come).
  B. 觀測器 — the game's own state, read after each day for this report (the books room by room, the true rating, the
     story's beats, the Lounge). Never handed to the player.

What it no longer does (the old tool did, until 2026-10-06): fill the fridge for free each morning; buy through buttons
it made itself (that built Lounge I through a 「buyLounge 1」 no screen shows, and bought on Day 1 a recipe whose tab
opens on Day 2, hired on Day 3 a cook whose tab opens on Day 4); follow a fixed build order (EARLY / GROW); press a
no-op to keep an old seed's days; decide when to save from fact()/S/LOUNGE_PROJ.

  python3 tools/qa/new_game_timeline.py [--days 110] [--seed 300] [--policy normal] [--service human]
                                        [--after-opening 32] [--json out.json] [--log out_log.txt] [--what-if JS]

--save FILE: start from a save (one of tests/saves, the user's own, or one this tool wrote) instead of Day 1.
--dump-save-at N --dump-save FILE: write the game's save at the end of Day N's evening (to start what-if runs there).
--what-if JS: a balance question asked of the simulation only (the snippet runs in the game before Day 1, e.g.
"RENT.lounge=1000"); never the game's files. It changes the game, not the player.
The environment: each morning Math.random is seeded from (seed, day) so a day's luck does not depend on how many taps
the day before took; the virtual clock moves 1/30 s a frame.
"""
import sys, os, json, time, argparse
ROOT = os.environ.get('JK_ROOT') or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'tests')); sys.path.insert(0, os.path.join(ROOT, 'tools', 'qa'))
import run_tests as rt
from player import Player, SAVE_KEY
import sim_player as sp
from playwright.sync_api import sync_playwright

SEED_JS = "Math.random=(function(){let a=%d;return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
LINES = [('Lounge 第一晚（Ken 和杜）', 'lounge_first_night'), ('Ken 第一次坐進 Lounge', 'ken_lounge'), ('Ken 提議品酒', 'ken_propose'),
         ('第一次品酒之夜', 'kt_night'), ('Evan 的來歷', 'evan_origin'), ('Ken 和杜：第二個杯墊', 'kd_coaster'), ('Ken 和杜：照片', 'kd_photo'),
         ('樣酒', 'ken_samples'), ('「晚餐之後」上酒單', 'ken_wine'), ('Madame Lin 來當客人', 'lin_guest'), ('晴 × 阿拓 開始', 'qt_1'),
         ('晴 × 阿拓：今天喝？', 'qt_drink'), ('予安 開始', 'ya_1')]


def run(A):
    t0 = time.time()
    rows, out = [], {'args': vars(A), 'policy': sp.POLICIES[A.policy].label, 'service': sp.SERVICE_LABELS[A.service]}
    with sync_playwright() as pw:
        srv, port = rt.start_server(); b = pw.chromium.launch()
        p = Player(b, port, 'index', save=A.save, W=A.width, H=844, seed=A.seed, touch=True, scenes=True)
        g = p.g
        screen, hands, log = sp.Screen(p.page), sp.Hands(p), sp.Log()
        player = sp.POLICIES[A.policy](screen, hands, log)
        obs = sp.Observer(g)
        # C: the hands for the service; B: the observer's counters
        rt.install_bot(g); g.ev(rt.LAZY_ACTOR)
        g.ev(sp.HUMAN_JS % dict(sp.HUMAN_DEFAULT, seed=A.seed * 7919 + 1)); g.ev(sp.SERVICE_JS); obs.install()
        g.ev("window.__fastSay=0")
        if A.what_if:
            g.ev(A.what_if); print('WHAT-IF (the game, in this simulation only):', A.what_if, flush=True)
        print(f'PLAYER: {player.label}  |  SERVICE: {sp.SERVICE_LABELS[A.service]}', flush=True)
        player.settle(); hands.tap('open'); k0 = player.settle()
        if k0 == 'summary':      # a save made at the summary or in the shop: that evening is over, the next day is played
            player.to_shop(); k0 = player.settle()
        if k0 == 'shop':
            player.next_day(); player.settle()
        day0 = screen.hud()['day'] if A.save else 1
        if A.save:
            print(f'FROM SAVE {A.save}: Day {day0}', flush=True)
        opened_at = None
        for day in range(day0, day0 + A.days):
            p.page.evaluate(SEED_JS % (A.seed * 1000 + day))
            k = player.settle()
            if k != 'prep':
                print(f'Day {day}: expected the prep screen, the screen is {k!r}: {screen.buttons()[:6]}', flush=True); break
            player.prep(day)
            player.open_shop()
            # the service, then the closing played to its end
            for _ in range(600):
                if obs.phase() != 'service':
                    break
                r = g.ev(f"__runService(300,'{A.service}')")
                if r['dlg'] or r.get('paused'):
                    player.settle()      # a story's panel, or a window that stops the day and asks (試酒的晚上, 新企劃)
            else:
                diag = g.ev("""JSON.stringify({phase,paused,sub,dlg:typeof DLG!=='undefined'&&DLG?{hold:!!DLG.hold,sh:DLG.sh?DLG.sh.k:null,i:DLG.i,n:DLG.lines&&DLG.lines.length,line:DLG.lines&&DLG.lines[DLG.i]&&DLG.lines[DLG.i].text}:null,
                  dlgEl:(()=>{const e=document.querySelector('#dlg');return e?{hidden:e.hidden,cls:e.className}:null})(),R:R?{t:+R.t.toFixed(1),dur:R.dur,closed:R.closed,closing:R.closing,ended:R.ended,groups:R.groups.length,states:R.groups.map(g=>g.state).slice(0,12)}:null,
                  wait:(typeof SH_WAIT!=='undefined')?SH_WAIT.length:null,svc:window.__svc||null})""")
                print(f'Day {day}: the service did not end — {diag}', flush=True); out['stuck'] = {'day': day, 'diag': diag}; break
            k = player.settle()
            if k != 'summary':
                print(f'Day {day}: expected the summary, the screen is {k!r}', flush=True); break
            sm = player.summary()
            rec = obs.day(); rec['hud'] = screen.hud(); rec['seen'] = {k2: sm.get(k2) for k2 in ('r0', 'r1', 'arrow', 'minus', 'plus', 'guests', 'lost', 'sat')}
            rows.append(rec)
            hands.wait(40 * 30); player.settle()     # reads the summary for a while; the evening goes on behind the card
            player.to_shop()
            hands.wait(30 * 30); player.settle()     # looks around the shop
            player.evening(day)
            rec['decisions'] = log.today(day)
            s = rec['sum']
            lg = f" Lounge {s['lg']['tabs']} 桌 ${s['lg']['rev']}" if s.get('lg') else ''
            rec['svc'] = g.ev("JSON.stringify({err:__svc.err||0,last:__svc.last||null,acts:window.__H?__H.acts:null})")
            print(f"Day {day:3d} lv{rec['level']} ★{rec['hud']['rate']}({rec['rate']}) 員工 {rec['crew']:2d} ${rec['money']:>8,} | 客 {s.get('guests')} 沒等到 {s.get('lost')} Perfect {s.get('perfect')}/{s.get('plated')} | 淨 {s.get('net', 0):+,}"
                  f"（收 {s.get('rev', 0):,}+{s.get('tips', 0):,} 貨 {s.get('cost', 0):,} 薪 {s.get('wages', 0):,} 租 {s.get('rent', 0):,} 酒 {s.get('wine') or 0:,}{lg}）"
                  f" | lounge {rec['lounge']} | {' '.join(rec['beats'])}", flush=True)
            for d in rec['decisions']:
                if d['kind'] in ('decide', 'hold', 'screen'):
                    print('   ' + sp.Log.line(d), flush=True)
            if rec['lounge'] and opened_at is None:
                opened_at = day
            if A.dump_save and (A.dump_at == day or (A.dump_when and g.ev(A.dump_when))):   # the game's own save at the end of this evening (harness: not the player)
                raw = p.page.evaluate("k=>localStorage.getItem(k)", SAVE_KEY)
                open(A.dump_save, 'w', encoding='utf-8').write(raw or '')
                print(f'SAVE after Day {day} -> {A.dump_save}', flush=True)
            if opened_at and day >= opened_at + A.after_opening:
                break
            player.next_day()
        out['rows'] = rows; out['log'] = log.rows; out['notes'] = obs.notes(); out['errors'] = g.errors[:30]
        report(out)
        if A.json:
            json.dump(out, open(A.json, 'w'), ensure_ascii=False, indent=1)
        if A.log:
            with open(A.log, 'w', encoding='utf-8') as f:
                f.write(f"{out['policy']} / {out['service']} / seed {A.seed}\n")
                for r in log.rows:
                    f.write(sp.Log.line(r) + '\n')
        print('page errors:', g.errors[:5])
        g.close(); b.close(); srv.shutdown()
    print(f'{len(rows)} days in {time.time()-t0:.0f}s')
    return out


def first(rows, f):
    return next((r['day'] for r in rows if f(r)), None)


def report(out):
    rows = out['rows']
    beats = {}
    for r in rows:
        for bk in r['beats']:
            beats.setdefault(bk.split(':', 1)[1], r['day'])
    cost = next((r['linCard']['cost'] for r in rows if r.get('linCard')), 50000)
    view = beats.get('lin_viewing')
    paid = first(rows, lambda r: (r.get('proj') or {}).get('state') in ('signing', 'reno', 'built'))
    opened = first(rows, lambda r: r['lounge'])
    L = {'《看看》': view,
         f'第一次自然有 ${cost:,}': first(rows, lambda r: r['money'] >= cost),
         f'兩個條件同時成立（《看看》、${cost:,}）': first(rows, lambda r: view and r['day'] >= view and r['money'] >= cost),
         '付錢（簽約・開工）': paid, 'Madame Lin 最後一晚': beats.get('lin_last'), '《簽約》': beats.get('lin_sign'), 'The Lounge 開幕': opened}
    print('\nTHE LOUNGE:', json.dumps(L, ensure_ascii=False))
    print('FIRST DAY OF EACH BEAT:', json.dumps(beats, ensure_ascii=False))
    print('THE LINES THAT NEED THE LOUNGE:', json.dumps({n: beats.get(k) for n, k in LINES}, ensure_ascii=False))
    hires = [(d['day'], d['pressed'], d['why']) for d in out['log'] if d['kind'] == 'decide' and d['pressed'] and ('聘請' in d['pressed'] or '訓練' in d['pressed'])]
    print('STAFF DECISIONS:', json.dumps(hires, ensure_ascii=False))
    buys = [(d['day'], d['pressed'], d['cost']) for d in out['log'] if d['kind'] == 'decide' and d['pressed'] and any(w in d['pressed'] for w in ('食譜', '研發', '升級', '開工', '擴建', '簽約', '購買'))]
    print('INVESTMENTS:', json.dumps(buys, ensure_ascii=False))
    out['lounge'] = L; out['first'] = beats


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--days', type=int, default=110); ap.add_argument('--seed', type=int, default=300)
    ap.add_argument('--policy', default='normal', choices=sorted(sp.POLICIES)); ap.add_argument('--service', default='human', choices=sorted(sp.SERVICE_LABELS))
    ap.add_argument('--after-opening', dest='after_opening', type=int, default=32); ap.add_argument('--width', type=int, default=390)
    ap.add_argument('--json', default=None); ap.add_argument('--log', default=None); ap.add_argument('--what-if', dest='what_if', default='')
    ap.add_argument('--save', default=None, help='start from a save (a file in tests/saves, or a path) instead of a new game; --days counts from its next day')
    ap.add_argument('--dump-save-at', dest='dump_at', type=int, default=None); ap.add_argument('--dump-save', dest='dump_save', default=None)
    ap.add_argument('--dump-when', dest='dump_when', default=None, help="JS read in the game each evening; true: write the save (e.g. the evening before the Lounge opens)")
    run(ap.parse_args())
