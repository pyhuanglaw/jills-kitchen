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

  python3 tools/qa/new_game_timeline.py [--days 100] [--seed 300] [--reserve 80000] [--json out.json]
"""
import sys, os, json, time, argparse
ROOT = os.environ.get('JK_ROOT') or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'tests'))
import run_tests as rt
from playwright.sync_api import sync_playwright
ap = argparse.ArgumentParser(); ap.add_argument('--days', type=int, default=70); ap.add_argument('--seed', type=int, default=300); ap.add_argument('--json', default=None)
ap.add_argument('--reserve', type=int, default=80000)
A = ap.parse_args()
RESERVE = A.reserve
SEED = "Math.random=(function(){let a=%d;return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
EARLY = {1: [('rd', {'d': 'pasta'}), ('buyTable', {})], 2: [('buyEq', {'k': 'bar'}), ('buyTable', {})], 3: [('hire', {'k': 'chef'})],
         5: [('expand', {}), ('buyDecor', {'k': 'plants'})], 8: [('hire', {'k': 'waiter'}), ('buyTable', {})], 11: [('expand', {})], 14: [('hire', {'k': 'cleaner'})]}
GROW = [('expand', {}), ('buyProject', {'k': 'side'}), ('buyProject', {'k': 'kext'}), ('buyOps', {'k': 'room'}), ('hire', {'k': 'waiter'}),
        ('hire', {'k': 'chef'}), ('hire', {'k': 'cleaner'}), ('buyTable', {}), ('buySideTable', {}), ('buyEq', {'k': 'bar'}), ('buyEq', {'k': 'oven'}),
        # the story's offers, taken when there (each a no-op otherwise; 'linTake' is rc8.5's 「接下隔壁」 — since 2026-10-06
        # 《看看》 decides it and the button is gone)
        ('linTake', {}), ('linSign', {}), ('buyLounge', {'k': '1'}), ('buyLounge', {'k': '2'}), ('buyLounge', {'k': '3'}),
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
               lounge:typeof loungeLv==='function'?loungeLv():0,up:!!(S.rooms&&S.rooms.up),sr:typeof srStage==='function'?srStage():0,pd:typeof pdStage==='function'?pdStage():0,
               sum:(L=>L?{rev:L.rev,tips:L.tips,bonus:L.bonus,cost:L.cost,wages:L.wages,rent:L.rent,wine:L.wine,cfee:L.cfee,loan:L.loan,net:L.net,guests:L.guests,lost:L.lost,lg:L.lg?{tabs:L.lg.tabs,rev:L.lg.rev}:null}:null)(S.lastSummary),
               lin:typeof linWorksCard==='function'&&fact('lounge_project')&&!loungeLv()?{state:(S.loungeProj||{}).state||null,cost:LOUNGE_PROJ[0].cost,
                 card:linWorksCard(S.money,(c,a,e,l)=>(l||'')+' '+fmt(c)+(S.money>=c?'':'（不夠）')).replace(/.*<div class="act">/,'').replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim()}:null})"""))
            rows.append(info)
            sm = info.get('sum') or {}
            day_money = f"淨 {sm.get('net', 0):+} (收 {sm.get('rev', 0)}+{sm.get('tips', 0)}，貨 {sm.get('cost', 0)}，薪 {sm.get('wages', 0)}，租 {sm.get('rent', 0)}，酒 {sm.get('wine', 0)}" + (f"，Lounge {sm['lg']['tabs']} 桌 {sm['lg']['rev']}" if sm.get('lg') else '') + ")"
            print(f"Day {info['day']:3d} lv{info['lv']} crew {info['crew']:2d} ${info['money']:>8} {day_money} dylan {info['dy']} lounge {info['lounge']} up {int(info['up'])} sr {info['sr']} pd {info['pd']} | {' '.join(info['beats'])}" + (f" | 工程頁：{info['lin']['card']}" if info.get('lin') else ''), flush=True)
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
                    story = a in ('linTake', 'linSign', 'buyLounge', 'buyUp', 'buySR', 'buyPD')
                    if story or (not saving and g.ev("S.money") > RESERVE): act(a, **kv)
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
        lounge = {'看看': first.get('lin_viewing'), '工程頁有 Lounge': proj, '最後一晚': first.get('lin_last'), '等級 4': next((r['day'] for r in rows if r['lv'] >= 4), None),
                  f'存到 ${cost:,}' if cost else '存到': rich,   # paid in the shop that evening; 《簽約》 is the next opening
                  '《簽約》': first.get('lin_sign'), 'The Lounge 開幕': next((r['day'] for r in rows if r['lounge']), None)}
        print('THE LOUNGE:', json.dumps(lounge, ensure_ascii=False))
        notes = [n for n in json.loads(g.ev("JSON.stringify(__notes)")) if any(w in n['t'] for w in ('隔壁', 'Lounge', '簽約'))]
        print('LINES ABOUT IT:', json.dumps(notes, ensure_ascii=False))
        print('page errors:', g.errors[:5])
        if A.json: json.dump({'rows': rows, 'first': first, 'lounge': lounge, 'notes': notes, 'errors': g.errors[:20]}, open(A.json, 'w'), ensure_ascii=False, indent=1)
        g.close(); b.close(); srv.shutdown()
    print(f'{A.days} days in {time.time()-t0:.0f}s')
if __name__ == '__main__':
    main()
