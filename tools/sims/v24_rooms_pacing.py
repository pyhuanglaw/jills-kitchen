"""v2.4 rc6 pacing and economy simulation: the Staff Room and the Private Dining Room, played day after day by the lazy
bot from the player's Day 61 save (the staff do their jobs; Jill cooks what no chef can), the story arbiter running as
in play. The floor's own arc is set as if it had happened (the lease LEASE_BACK days ago, its furniture arriving); from
then on nothing is set by hand: the beats come when their conditions hold, and the player — an eager one — says
「開始規劃」 to each offer and buys each phase the first evening it is open and affordable.

Prints per day: the beats, the phases, what was bought, the Staff Room's people (most at once, breaks, a cat), the
Private Dining Room's evening (the booking and its bill, the walk-ins, other parties), the day's money; then the first
day of each beat, the bookings by phase, the minimum against what was eaten, the days without a booking in a row, the
rooms' share of the takings, majors per day, page errors.

  python3 tools/sims/v24_rooms_pacing.py [days=60] [seedbase=8100] [lease_back=1] [save=tests/saves/player_day61.json]
  JK_ROOMS_BUY=0 to leave the shop alone (the offers are still answered 「開始規劃」)
"""
import sys, os, json, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, os.path.join(ROOT, 'tests'))
import run_tests as rt
from playwright.sync_api import sync_playwright

DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 60
SEEDBASE = int(sys.argv[2]) if len(sys.argv) > 2 else 8100
LEASE_BACK = int(sys.argv[3]) if len(sys.argv) > 3 else 1
SAVE = sys.argv[4] if len(sys.argv) > 4 else os.path.join(ROOT, 'tests/saves/player_day61.json')
BUY = os.environ.get('JK_ROOMS_BUY', '1') != '0'
raw = json.load(open(SAVE)); raw = raw.get('save', raw)
SEED = "Math.random=(function(){let a=%d;return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})()"
KEYS = ['wall_settle', 'up_hint', 'up_inspect', 'up_cats', 'up_ask', 'up_lease', 'up_use', 'sp_wait', 'sr_story', 'sr_build', 'sr_first', 'sr_plug', 'sr_plug2', 'sr_food', 'sr_fridge', 'sr_nina',
        'pd_yj', 'pd_other', 'pd_story', 'pd_build', 'pd_back']


def setf(g, k, back):
    g.ev(f"(()=>{{const d=S.day-{back};story().facts['{k}']={{d,n:1,l:d}}}})()")


def floor_taken(g, lease_back):
    """the stories before the rooms, as if they had happened (as tools/sims/v24_rooms_shots.py): 怡君 and the wall
    settled, the floor's whole arc, the floor leased lease_back days ago, its furniture arriving over the next days"""
    g.ev("(()=>{const v=v24();v.first=S.day-60})()")
    for i, k in enumerate(['yj_meet', 'yj_look', 'yj_three', 'yj_chose', 'yj_move', 'yj_key', 'yj_key_seen', 'xq_oh']):
        setf(g, k, 60 - i * 2)
    for i, k in enumerate(['wall_worry', 'wall_call', 'wall_photos', 'wall_jill', 'wall_visit', 'wall_wang', 'wall_setback', 'wall_report', 'wall_fee', 'wall_prep', 'wall_mediation', 'wall_settle', 'wall_paid', 'wall_article', 'wall_paper', 'wall_fixed']):
        setf(g, k, 44 - i)
    for i, k in enumerate(['up_hint', 'up_staff', 'up_inspect', 'up_door', 'up_cats', 'up_busy', 'up_full', 'sp_box', 'sp_seat', 'up_remind', 'up_ask']):
        setf(g, k, max(lease_back + 1, 24 - i))
    setf(g, 'up_lease', lease_back)
    g.ev(f"(()=>{{S.rooms.up=1;const u=upS();const L=S.day-{lease_back};u.lease=L;u.furn={{table:L+1,cabinet:L+2,coat:L+2,lamp:L+3,cushion:L+3,stool:L+5,scratch:L+5}};u.traces={{bag:L+2,cup:L+3,charger:L+4,coat:L+6}};S.upProj={{state:'built'}};S.newRooms=S.newRooms||{{}};S.newRooms.up=L}})()")


SIM_DAY = r"""window.__simDay=function(steps,dt){let n=0;for(;n<steps;n++){if(!(phase==='service'&&R))break;
 if(sub==='roomoffer'){const b=document.querySelector('#screen [data-act=roomGo]');const k=b?b.dataset.k.split('|')[0]:'?';__rm.offers.push(k);if(b)roomGo(k+'|plan');else{hideScreen();paused=false}}
 if(sub==='upproj'){__rm.offers.push('up');upGo('plan')}if(!__rm.offers.includes('lounge')&&fact('lounge_project')&&fact('lounge_project').d===S.day)__rm.offers.push('lounge')   /* 2026-10-06: no card — 《看看》 decides it, that day */
 if(typeof DLG!=='undefined'&&DLG)dlgNext();
 __act();update(dt);updateCats(dt,0);if(!R)break;
 const m=srPeople().length;if(m>__rm.most)__rm.most=m;__rm.brk=R.srBreaks||0;__rm.cat=R.srCat?1:0;__rm.early=R.srEarly?1:0;
 if(n%15===0)for(const q of R.groups){if(q.table!=null&&R.tables[q.table]&&R.tables[q.table].pdr&&!__rm.seen.has(q)){__rm.seen.add(q);if(q.pdWalk)__rm.walk++;else if(!q.pdRes&&!q.pdStory)__rm.other++}}}
 return n}"""

DAY_JS = r"""JSON.stringify((()=>{const p=pdOf()||{};const r=p.res&&p.res.d===S.day?p.res:null;const L=S.lastSummary||{};
 return{day:S.day,money:S.money,rev:L.rev||0,net:L.net||0,guests:L.guests||0,sr:srStage(),pd:pdStage(),srOn:srOn(),pdOn:pdOn(),
  res:r?{size:r.size,min:r.min,actual:r.actual||0,status:r.status,kind:r.kind}:null,book:(p.book&&p.book[S.day])?{k:p.book[S.day].k,status:p.book[S.day].status}:null,
  pdN:(L.pd&&L.pd.n)||0,pdTop:(L.pd&&L.pd.top)||0,dry:p.dry||0,n:p.n||0,avg:p.avg||0,
  facts:Object.fromEntries(KEYS.filter(k=>fact(k)&&fact(k).d===S.day).map(k=>[k,1])),
  majors:(story().day&&story().day.d===S.day)?story().day.major:null,errors:(window.__errs||[]).length}})())"""


def main():
    t0 = time.time()
    with sync_playwright() as p:
        srv, port = rt.start_server(); b = p.chromium.launch()
        g = rt.Game(b, port, 'index', seed=SEEDBASE, manual=True, viewport={'width': 390, 'height': 844})
        g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.page.wait_for_timeout(150)
        g.click('[data-act=openFresh]') if g.page.query_selector('[data-act=openFresh]') else g.click('[data-act=open]'); g.page.wait_for_timeout(150)
        if LEASE_BACK >= 0: floor_taken(g, LEASE_BACK)
        g.ev("window.__fastSay=1")
        rows = []; buys = []
        for d in range(DAYS):
            bought = []
            if g.ev("phase") == 'summary':
                g.click('[data-act=toShop]'); g.page.wait_for_timeout(80)
            if BUY and g.ev("phase") == 'shop' and g.ev("!!fact('up_ask')&&!upTaken()&&S.money>=UP_PROJ.cost"):
                if g.ev("buyUp()"):
                    g.ev("hideReveal&&hideReveal()"); bought.append('up'); buys.append((g.ev('S.day'), 'up'))
            if BUY and g.ev("phase") == 'shop':
                for kind, L in (('sr', 'SR_PROJ'), ('pd', 'PD_PROJ')):
                    n = g.ev(f"{kind}Next()")
                    if n and not g.ev(f"{kind}WhyNot({n})") and g.ev(f"S.money>={L}[{n}].cost"):
                        if g.ev(f"buyRoomPhase('{kind}',{n})"):
                            g.ev("hideReveal&&hideReveal()"); bought.append(f'{kind}{n}'); buys.append((g.ev('S.day'), f'{kind}{n}'))
            if g.ev("phase") == 'shop':
                g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(120)
            g.ev("for(let i=0;i<80&&typeof DLG!=='undefined'&&DLG;i++){__tick(400);dlgNext()}")
            g.ev(SEED % (SEEDBASE + d)); g.ev("S.today.sugKey=null;S.today.sug=null;autoStock()")
            rt.start_day(g); rt.install_bot(g); g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;window.__noScenes=true")
            g.ev("window.__rm={most:0,brk:0,cat:0,early:0,walk:0,other:0,seen:new Set(),offers:[]}")
            g.ev(SIM_DAY)
            for _ in range(400):
                r = g.page.evaluate('()=>window.__simDay(400,1/30)')
                if g.ev("phase") != 'service' or not g.ev("!!R"): break
            if g.ev("phase") == 'service':
                g.ev("closeShop('x');for(const q of R.groups.slice())leaveGroup(q,'ok')"); g.page.evaluate('()=>window.__simDay(4000,1/30)')
            offers = g.ev("__rm.offers")
            if g.ev("phase") == 'service': g.ev("finishClosing()")
            info = json.loads(g.ev(DAY_JS.replace('KEYS', json.dumps(KEYS))))
            info['rm'] = json.loads(g.ev("JSON.stringify({most:__rm.most,brk:__rm.brk,cat:__rm.cat,walk:__rm.walk,other:__rm.other})"))
            info['bought'] = bought; info['offers'] = offers
            rows.append(info)
            res = info['res']
            rs = f"res {res['size']}p min {res['min']} ate {res['actual']} {res['status']}" if res else ('story ' + json.dumps(info['book'], ensure_ascii=False) if info['book'] else '-')
            print(f"Day {info['day']:3d} sr{info['sr']} pd{info['pd']} {' '.join(bought) or '':6s} | staff most {info['rm']['most']} brk {info['rm']['brk']} cat {info['rm']['cat']} | pd {rs} walk {info['rm']['walk']} other {info['rm']['other']} n {info['n']} | net {info['net']:,} money {info['money']:,} | {' '.join(info['facts'].keys())} {'offer:' + ','.join(offers) if offers else ''}", flush=True)
        final = json.loads(g.ev("JSON.stringify(Object.fromEntries(%s.map(k=>[k,fact(k)?fact(k).d:null])))" % json.dumps(KEYS)))
        majors = json.loads(g.ev("JSON.stringify(story().trace.filter(t=>t.lane==='major').map(t=>[t.d,t.k]))"))
        lease = g.ev("upS().lease")
        print(f'\nthe floor leased on Day {lease}; first day of each beat (days after the lease):')
        for k in KEYS:
            print(f'  {k:10s} {final[k]}' + (f'  (+{final[k]-lease})' if final[k] is not None and lease is not None else ''))
        print('bought:', buys)
        # the bookings by phase
        by = {}
        for r in rows:
            if r['pd'] >= 1:
                s = by.setdefault(r['pd'], {'evenings': 0, 'booked': 0, 'done': 0, 'topped': 0, 'top': 0, 'walk': 0, 'other': 0, 'story': 0, 'maxdry': 0, 'dry': 0, 'min': [], 'ate': []})
                s['evenings'] += 1; s['walk'] += r['rm']['walk']; s['other'] += r['rm']['other']
                if r['book']: s['story'] += 1
                if r['res']:
                    s['booked'] += 1; s['dry'] = 0
                    if r['res']['status'] == 'done':
                        s['done'] += 1; s['min'].append(r['res']['min']); s['ate'].append(r['res']['actual'])
                        if r['res']['actual'] < r['res']['min']: s['topped'] += 1; s['top'] += r['res']['min'] - r['res']['actual']
                elif not r['book']:
                    s['dry'] += 1; s['maxdry'] = max(s['maxdry'], s['dry'])
        print('\nthe Private Dining Room by phase:')
        for ph, s in sorted(by.items()):
            mn = sum(s['min']) / len(s['min']) if s['min'] else 0; at = sum(s['ate']) / len(s['ate']) if s['ate'] else 0
            print(f"  phase {ph}: {s['evenings']} evenings, booked {s['booked']} ({s['booked']/max(1,s['evenings'])*100:.0f}%), paid {s['done']}, story evenings {s['story']}, longest run without a booking {s['maxdry']}; "
                  f"minimum avg ${mn:,.0f} vs eaten avg ${at:,.0f}; topped up {s['topped']}× (${s['top']:,}); walk-in parties {s['walk']}, other parties of 4+ {s['other']}")
        per = {}
        for dd, k in majors: per.setdefault(dd, []).append(k)
        print('more than one major in a day:', [dd for dd, v in per.items() if len(v) > 1])
        sr_days = [r for r in rows if r['sr'] >= 1]
        if sr_days:
            print(f"the Staff Room: {len(sr_days)} evenings; people up there at once avg {sum(r['rm']['most'] for r in sr_days)/len(sr_days):.1f}, "
                  f"evenings with a break {sum(1 for r in sr_days if r['rm']['brk'])}, with a cat {sum(r['rm']['cat'] for r in sr_days)}")
        nets = [r['net'] for r in rows]
        print(f"net per day avg ${sum(nets)/len(nets):,.0f}; money {rows[0]['money']:,} → {rows[-1]['money']:,}")
        print('page errors:', g.errors[:5])
        json.dump(rows, open(os.path.join(os.environ.get('JK_OUT', '.'), f'rooms_pacing_{SEEDBASE}.json'), 'w'), ensure_ascii=False)
        g.close(); b.close()
    print(f'{DAYS} days in {time.time()-t0:.0f}s')


if __name__ == '__main__':
    main()
