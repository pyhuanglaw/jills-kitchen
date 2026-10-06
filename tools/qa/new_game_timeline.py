"""Deep-audit tool (2026-10-06): on which day does a player who starts on Day 1 meet each story?
The user, 2026-10-06: 「我的遊戲是邊玩邊改……如果是第一天玩的人他應該在很前面照他玩的……你就是設某個故事是哪一個故事的條件
這樣玩下去就好了」 — the stories follow each other's conditions; this measures where a new game actually gets to them.

A new game played from Day 1: the fast bot serves; the closing is PLAYED with the evening's life running (Jill's room,
Dylan at his desk, the 'evening' story tick — the fast bot alone skips the closing to the summary, and the stories told at
the closing then never come); the player lingers on the summary and in the shop (Jill's sofa evening goes on behind the
card); the shop is bought the way a person who keeps savings would (RESERVE), and every story offer — Madame Lin's bar,
the Lounge, the second floor, the rooms — is taken when it is offered. Prints each day's beats and Dylan's reveal
conditions; at the end the first day of every beat. Report, not a test: one seed is one possible game.
With the bar next door on the works page, each day also prints what its card says (her last night, the level, the money,
簽約・開工), and at the end the days of 《看看》, her last night, the money for Lounge I, the signing and the opening.

  python3 tools/qa/new_game_timeline.py [--days 100] [--seed 300] [--reserve 80000] [--json out.json] [--what-if JS]

At the end: the Lounge's days (《看看》, the rating 4.0, the first day with the money, paid, 《簽約》, the opening), the seven
days after the opening (the till and the day's money in and out), and the first day of each line that needs The Lounge.
--what-if JS: a balance question asked of the simulation only — the snippet runs in the page before Day 1 (e.g.
"RENT.lounge=1000"); it never changes the game's files. Leave it out for the game as it is.
--lounge-buffer N: another what-if, of the player — Lounge I is signed only with N more than its price in the till
(a player who heeds a warning about the days after). Leave it out for the player of every other run.
"""
import sys, os, json, time, argparse
ROOT = os.environ.get('JK_ROOT') or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'tests'))
import run_tests as rt
from playwright.sync_api import sync_playwright
ap = argparse.ArgumentParser(); ap.add_argument('--days', type=int, default=70); ap.add_argument('--seed', type=int, default=300); ap.add_argument('--json', default=None)
ap.add_argument('--reserve', type=int, default=80000); ap.add_argument('--what-if', dest='what_if', default=''); ap.add_argument('--lounge-buffer', dest='buffer', type=int, default=0)
A = ap.parse_args()
RESERVE = A.reserve
SEED = "Math.random=(function(){let a=%d;return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
EARLY = {1: [('rd', {'d': 'pasta'}), ('buyTable', {})], 2: [('buyEq', {'k': 'bar'}), ('buyTable', {})], 3: [('hire', {'k': 'chef'})],
         5: [('expand', {}), ('buyDecor', {'k': 'plants'})], 8: [('hire', {'k': 'waiter'}), ('buyTable', {})], 11: [('expand', {})], 14: [('hire', {'k': 'cleaner'})]}
GROW = [('expand', {}), ('buyProject', {'k': 'side'}), ('buyProject', {'k': 'kext'}), ('buyOps', {'k': 'room'}), ('hire', {'k': 'waiter'}),
        ('hire', {'k': 'chef'}), ('hire', {'k': 'cleaner'}), ('buyTable', {}), ('buySideTable', {}), ('buyEq', {'k': 'bar'}), ('buyEq', {'k': 'oven'}),
        # the story's offers, taken when there (each a no-op otherwise; 'linTake' is rc8.5's 「接下隔壁」 — since 2026-10-06
        # 《看看》 decides it and the button is gone)
        # Lounge I is 簽約・開工 (linSign): the game has no button 「buyLounge 1」 (pressing one built Lounge I around the story
        # once its level requirement went, 2026-10-06 — the game now refuses it too). 'noop' keeps its place: every press
        # moves the game's clock a little, and the same number of presses keeps a seed's days the same as in the runs before
        ('linTake', {}), ('linSign', {}), ('noop', {}), ('buyLounge', {'k': '2'}), ('buyLounge', {'k': '3'}),
        ('buyUp', {}), ('buySR', {'k': '2'}), ('buySR', {'k': '3'}), ('buyPD', {'k': '1'}), ('buyPD', {'k': '2'}), ('buyPD', {'k': '3'})]
def main():
    t0 = time.time(); rows = []
    with sync_playwright() as p:
        srv, port = rt.start_server(); b = p.chromium.launch()
        g = rt.Game(b, port, 'index', seed=A.seed, manual=True, viewport={'width': 390, 'height': 844})
        rt.install_bot(g)
        def act(a, **kv):
            ds = ''.join(f"el.dataset.{k}='{v}';" for k, v in kv.items())
            g.ev(f"(()=>{{const el=document.createElement('button');el.dataset.act='{a}';{ds}$('#screen').appendChild(el);el.click();el.remove()}})()")
            g.ev("__tick(30);if(typeof hideReveal==='function')try{hideReveal()}catch(e){};for(let i=0;i<80&&typeof DLG!=='undefined'&&DLG;i++){__tick(400);dlgNext()}")
        g.click('[data-act=open]'); g.ev("window.__fastSay=1")
        if A.what_if: g.ev(A.what_if); print('WHAT-IF (the simulation only):', A.what_if, flush=True)
        if A.buffer: print(f'WHAT-IF (the player): Lounge I only with ${A.buffer:,} more than its price', flush=True)
        paid_day = None
        g.ev("window.__notes=[];const __nl=noteLine;noteLine=function(t){__notes.push({d:S.day,t});return __nl.apply(this,arguments)}")
        for day in range(1, A.days + 1):
            g.ev("for(let i=0;i<80&&typeof DLG!=='undefined'&&DLG;i++){__tick(400);dlgNext()}")
            if g.ev("phase") != 'prep':
                print('not at prep on day', day, g.ev("phase")); break
            act('restock'); rt.fill_fridge(g)
            g.ev(SEED % (A.seed * 1000 + day))
            rt.start_day(g)
            # the service by the fast bot up to the closing; the closing itself played with the evening's life running (as
            # in play: the 'evening' story tick, Jill's room, Dylan at his desk) — the fast bot would skip it to the summary
            for _ in range(800):
                g.ev("__botUntil('R.closing!=null',150,1/30)")
                g.ev("for(let i=0;i<80&&typeof DLG!=='undefined'&&DLG;i++){__tick(400);dlgNext()}")
                if g.ev("phase") != 'service' or g.ev("R&&R.closing!=null"): break
            for _ in range(200):
                if g.ev("phase") != 'service': break
                g.ev("__evening(1,1/30)")
                g.ev("for(let i=0;i<80&&typeof DLG!=='undefined'&&DLG;i++){__tick(400);dlgNext()}")
            if g.ev("phase") == 'service': g.ev("__bot(60000,1/30)")
            g.ev("for(let i=0;i<30;i++)__tick(1000/30)")
            info = json.loads(g.ev("""JSON.stringify({day:S.day,money:S.money,lv:S.level,crew:(S.crew||[]).length,
               dy:S.dylan?{stage:S.dylan.stage,reveal:S.dylan.reveal||null,v:S.regulars.dylan||0,stay:S.dylan.stay||0,clues:Object.keys(S.dylan.clues||{}).filter(k=>S.dylan.clues[k]>0).length,sofa:(S.life&&S.life.sofa)||0}:null,
               beats:(story().trace||[]).filter(t=>t.d===S.day).map(t=>t.lane[0]+':'+t.k),
               rate:+rating().toFixed(2),rate1:+rating().toFixed(1),lounge:typeof loungeLv==='function'?loungeLv():0,up:!!(S.rooms&&S.rooms.up),sr:typeof srStage==='function'?srStage():0,pd:typeof pdStage==='function'?pdStage():0,
               sum:(L=>L?{rev:L.rev,tips:L.tips,bonus:L.bonus,cost:L.cost,wages:L.wages,rent:L.rent,wine:L.wine,cfee:L.cfee,loan:L.loan,net:L.net,guests:L.guests,lost:L.lost,lg:L.lg?{tabs:L.lg.tabs,rev:L.lg.rev}:null}:null)(S.lastSummary),
               lin:typeof linWorksCard==='function'&&fact('lounge_project')&&!loungeLv()?{state:(S.loungeProj||{}).state||null,cost:LOUNGE_PROJ[0].cost,
                 card:linWorksCard(S.money,(c,a,e,l)=>(l||'')+' '+fmt(c)+(S.money>=c?'':'（不夠）')).replace(/.*<div class="act">/,'').replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim()}:null})"""))
            rows.append(info)
            sm = info.get('sum') or {}
            day_money = f"淨 {sm.get('net', 0):+} (收 {sm.get('rev', 0)}+{sm.get('tips', 0)}，貨 {sm.get('cost', 0)}，薪 {sm.get('wages', 0)}，租 {sm.get('rent', 0)}，酒 {sm.get('wine', 0)}" + (f"，Lounge {sm['lg']['tabs']} 桌 {sm['lg']['rev']}" if sm.get('lg') else '') + ")"
            print(f"Day {info['day']:3d} lv{info['lv']} ★{info['rate1']} crew {info['crew']:2d} ${info['money']:>8} {day_money} dylan {info['dy']} lounge {info['lounge']} up {int(info['up'])} sr {info['sr']} pd {info['pd']} | {' '.join(info['beats'])}" + (f" | 工程頁：{info['lin']['card']}" if info.get('lin') else ''), flush=True)
            # a person reads the summary and shops for a while: the evening goes on behind the card (Jill's sofa, Dylan)
            g.ev("for(let i=0;i<40*30;i++)__tick(1000/30)")
            if g.ev("phase") == 'summary': g.click('[data-act=toShop]')
            g.ev("for(let i=0;i<30*30;i++)__tick(1000/30)")
            for a, kv in EARLY.get(day, []): act(a, **kv)
            if day >= 15:
                # a person takes what the story offers first, then grows the restaurant only with money to spare
                # …and once the story offers a place (Madame Lin's bar, the second floor), saves up for it first
                saving = g.ev("(fact('lounge_project')&&!loungeLv())||(fact('up_ask')&&!(S.rooms&&S.rooms.up))")
                for a, kv in GROW:
                    if a == 'linSign' and A.buffer and g.ev("S.money") < g.ev("LOUNGE_PROJ[0].cost") + A.buffer: continue
                    story = a in ('linTake', 'linSign', 'buyLounge', 'buyUp', 'buySR', 'buyPD')
                    if story or (not saving and g.ev("S.money") > RESERVE): act(a, **kv)
            if paid_day is None and g.ev("!!S.loungeProj&&S.loungeProj.state==='signing'"): paid_day = day
            g.click('[data-act=nextDay]'); g.ev("__tick(100)")
        first = {}
        for r in rows:
            for bk in r['beats']:
                k = bk.split(':', 1)[1]
                first.setdefault(k, r['day'])
        print('\nFIRST DAY OF EACH BEAT:', json.dumps(first, ensure_ascii=False))
        proj = next((r['day'] for r in rows if r.get('lin')), None)
        cost = next((r['lin']['cost'] for r in rows if r.get('lin')), None)
        rich = next((r['day'] for r in rows if proj and r['day'] >= proj and cost and r['money'] >= cost and not r['lounge']), None)
        opened = next((r['day'] for r in rows if r['lounge']), None)
        lounge = {'看看': first.get('lin_viewing'), '工程頁有 Lounge': proj, '最後一晚': first.get('lin_last'), '等級 4': next((r['day'] for r in rows if r['lv'] >= 4), None),
                  '評分 4.0': next((r['day'] for r in rows if r.get('rate1', 0) >= 4.0), None),
                  f'第一次有 ${cost:,}' if cost else '第一次有': next((r['day'] for r in rows if cost and r['money'] >= cost), None),
                  f'《看看》後第一次有 ${cost:,}' if cost else '存到': rich,
                  '付錢（簽約・開工）': paid_day, '《簽約》': first.get('lin_sign'), 'The Lounge 開幕': opened}
        rate_on = lambda d: next((r['rate1'] for r in rows if r['day'] == d), None)
        span = [r['rate1'] for r in rows if proj and r['day'] >= proj and (not opened or r['day'] <= opened)]
        # the rating moves with the last reviews: the first days' few reviews make Day 1 read high, so what matters is
        # where it is when the money is there
        lounge.update({'《看看》那天評分': rate_on(first.get('lin_viewing')), '付錢那天評分': rate_on(paid_day), '《看看》到開幕最低評分': min(span) if span else None})
        print('THE LOUNGE:', json.dumps(lounge, ensure_ascii=False))
        after = [{'day': r['day'], 'money': r['money'], **{k: (r.get('sum') or {}).get(k) for k in ('net', 'rev', 'tips', 'cost', 'wages', 'rent', 'wine')},
                  'lounge_tabs': ((r.get('sum') or {}).get('lg') or {}).get('tabs'), 'lounge_rev': ((r.get('sum') or {}).get('lg') or {}).get('rev')}
                 for r in rows if opened and opened - 1 <= r['day'] <= opened + 7]
        print('AROUND THE OPENING (the day before, the opening day, seven more):')
        for x in after:
            print(f"  Day {x['day']:3d} ${x['money']:>7}  淨 {x['net'] or 0:+6}  收 {(x['rev'] or 0) + (x['tips'] or 0):>6}（Lounge {x['lounge_tabs'] or 0} 桌 {x['lounge_rev'] or 0}）  貨 {x['cost'] or 0:>5}  薪 {x['wages'] or 0:>5}  租 {x['rent'] or 0:>5}  酒 {x['wine'] or 0:>5}")
        LINES = [('Lounge 第一晚（Ken 和杜）', 'lounge_first_night'), ('Ken 第一次坐進 Lounge', 'ken_lounge'), ('Ken 提議品酒', 'ken_propose'),
                 ('第一次品酒之夜', 'kt_night'), ('Evan 的來歷', 'evan_origin'), ('Ken 和杜：第二個杯墊', 'kd_coaster'), ('Ken 和杜：照片', 'kd_photo'),
                 ('樣酒', 'ken_samples'), ('「晚餐之後」上酒單', 'ken_wine'), ('Ken 和杜：固定的位子', 'kd_usual'), ('Evan：「杜來了嗎？」', 'kd_evan_1'),
                 ('Madame Lin 來當客人', 'lin_guest'), ('晴 × 阿拓 開始', 'qt_1'), ('晴 × 阿拓：今天喝？', 'qt_drink'), ('晴 × 阿拓：講完', 'qt_said'),
                 ('予安 開始', 'ya_1'), ('予安：「星期幾？」', 'ya_join')]
        lines = {n: first.get(k) for n, k in LINES}
        lines.update({'Lounge II': next((r['day'] for r in rows if r['lounge'] >= 2), None), 'Lounge III': next((r['day'] for r in rows if r['lounge'] >= 3), None),
                      '二樓': next((r['day'] for r in rows if r['up']), None)})
        print('THE LINES THAT NEED THE LOUNGE (first day):', json.dumps(lines, ensure_ascii=False))
        notes = [n for n in json.loads(g.ev("JSON.stringify(__notes)")) if any(w in n['t'] for w in ('隔壁', 'Lounge', '簽約'))]
        print('LINES ABOUT IT:', json.dumps(notes, ensure_ascii=False))
        print('page errors:', g.errors[:5])
        if A.json: json.dump({'rows': rows, 'first': first, 'lounge': lounge, 'after': after, 'lines': lines, 'what_if': A.what_if, 'buffer': A.buffer, 'notes': notes, 'errors': g.errors[:20]}, open(A.json, 'w'), ensure_ascii=False, indent=1)
        g.close(); b.close(); srv.shutdown()
    print(f'{A.days} days in {time.time()-t0:.0f}s')
if __name__ == '__main__':
    main()
