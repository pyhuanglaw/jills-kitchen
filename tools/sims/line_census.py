"""2026-10-04 (the player: 「跳出的對話有些太重複沒有意義 又太頻繁 一些不重要的npc沒有劇情的對話可以少一點」): every line that pops up
during one evening on a real save — the toasts with a name, the lines with a face (#plines), the room's notes — where it
came from (a story beat and its lane, or the restaurant's own talk and which function), when, and how often the same
words came back. Lazy bot, no held scenes (a held beat's lines are counted as its beat).

  python3 tools/sims/line_census.py SAVE SEED [DAYS] [OUT.json]
  e.g. python3 tools/sims/line_census.py tests/saves/player_day89_2320.json 8900 3
"""
import sys, os, json, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, os.path.join(ROOT, 'tests'))
import run_tests as rt
from playwright.sync_api import sync_playwright
SAVE, SEED = sys.argv[1], int(sys.argv[2]); DAYS = int(sys.argv[3]) if len(sys.argv) > 3 else 1; OUT = sys.argv[4] if len(sys.argv) > 4 else None
raw = json.load(open(SAVE)); raw = raw.get('save', raw)

HOOK = r"""(()=>{window.__lines=[];
 const fnames=()=>{const s=new Error().stack.split('\n').slice(2).map(l=>(l.match(/at (?:Object\.)?([\w$.]+) /)||[])[1]).filter(Boolean);return s.filter(n=>!/^(rec|toast|portraitLine|noteRaw|noteLine|quote0?|staffSay|jillSay|logLine|eval|later|shRun|shFire|shStart|Array|window|setTimeout)/.test(n)).slice(0,6)};
 const lane=k=>{const E=STORY_EV.find(e=>e.k===k);return E?E.lane:'?'};
 const rec=(how,txt)=>{const t=String(txt).replace(/<[^>]+>/g,'');const cx=SCX;window.__lines.push({how,t,day:S.day,at:R?Math.round(R.t/R.dur*1000)/10:null,clock:R?clockStr():null,room,beat:cx?cx.k:null,lane:cx?lane(cx.k):null,src:fnames()})};
 const t0=toast;toast=function(html,kind,o){if(kind==='q'||!kind)rec('toast:'+(kind||'plain'),html);return t0.apply(this,arguments)};
 const p0=portraitLine;portraitLine=function(who,txt,o){const r=p0.apply(this,arguments);if(r)rec('face:'+who,txt);return r};
})()"""

with sync_playwright() as p:
    srv, port = rt.start_server(); b = p.chromium.launch()
    g = rt.Game(b, port, 'index', seed=SEED, manual=True, viewport={'width': 390, 'height': 844})
    g.ev("phase='title';R=null;localStorage.setItem(KEY,JSON.stringify(%s))" % json.dumps(raw, ensure_ascii=False)); g.reload(); g.page.wait_for_timeout(150)
    g.click('[data-act=openFresh]') if g.page.query_selector('[data-act=openFresh]') else g.click('[data-act=open]'); g.page.wait_for_timeout(150)
    g.ev(HOOK); trace = {}
    for d in range(DAYS):
        if d:
            if g.ev("phase") == 'summary': g.click('[data-act=toShop]'); g.page.wait_for_timeout(80)
            if g.ev("phase") == 'shop': g.click('#screen [data-act=nextDay]'); g.page.wait_for_timeout(150)
            g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}")
        g.ev("autoStock()"); rt.start_day(g); rt.install_bot(g); g.ev(rt.LAZY_ACTOR + "\nwindow.__act=window.__actLazy;window.__noScenes=true")
        for _ in range(3000):
            g.ev("__botUntil('false',90,1/30)"); g.page.wait_for_timeout(5)   # real time for the lines a timer brings
            if g.ev("phase") != 'service' or not g.ev("!!R"): break
        g.page.wait_for_timeout(2500)
        day = g.ev("S.day"); trace[day] = json.loads(g.ev("JSON.stringify(story().trace.filter(t=>t.d===S.day).map(t=>t.k+'/'+t.lane))"))
    L = json.loads(g.ev("JSON.stringify(window.__lines)"))
    b.close(); srv.shutdown()

def kind(x):
    if x['beat']: return f"story/{x['lane']}"
    return 'other/' + (x['src'][0] if x['src'] else '?')
c = collections.Counter(kind(x) for x in L)
print(f'seed {SEED}, {DAYS} evening(s) from Day {L[0]["day"] if L else "?"}: {len(L)} lines popped up'); print('per day:', dict(collections.Counter(x["day"] for x in L))); print('story trace:', trace)
for k, n in c.most_common(): print(f'  {n:4d}  {k}')
words = collections.Counter(x['t'] for x in L)
print('the same words more than once:')
for t, n in words.most_common():
    if n < 2: break
    print(f'  {n}×  {t[:70]}')
by_beat = collections.Counter(x['beat'] for x in L if x['beat'])
print('story beats (lines):', dict(by_beat.most_common()))
if OUT:
    json.dump(L, open(OUT, 'w'), ensure_ascii=False, indent=0)
