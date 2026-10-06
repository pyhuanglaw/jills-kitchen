"""A simulated player for the new-game timeline (QA; the user, 2026-10-06: 「模擬「一個真的在玩 Jill's Kitchen 的人」」).

Three things here, used by tools/qa/new_game_timeline.py and by the simulator's own tests:

- UI: every action is a press on a button that is on the screen right now (the shop's tab is opened first, as a player
  would). Nothing is bought through a button the game does not draw — the old tool once built Lounge I through a
  「buyLounge 1」 that no screen shows. Restocking is the prep screen's 「一鍵補到建議量」, paid like every other purchase
  (the old tool also filled the fridge for free each morning).
- observe(): what a player can read before deciding — the HUD (cash, ★), the end-of-day summary (guests, the lost and
  the cross, what moved the rating), the staff tab (people per list against its places), the price on each card. It is
  read from the game's state, but only the values those screens show.
- The policies. `normal` (合理玩家模擬) plays like the user (2026-10-06): fills staff places when guests wait or the
  rating falls on service and the till can carry the wages, puts spare money into what raises the takings (pricier
  dishes, drinks and wine), then space and the story's works, keeping a few days' running costs in the till; it never
  saves for a far-off work while the restaurant is short of hands. `baseline` (刻意不投資的 baseline) is the old tool's
  player — upgrades only with more than $80,000 in the till, saves for the story's next place — kept to compare with,
  never to judge the game by.

Every decision goes into the day's log with its reason (「因等待過久／評分下降 → 聘請服務生」, 「保留現金 → 暫緩 …」).
"""
import json

SHOP_TABS = ['works', 'staff', 'menu', 'kitchen', 'home', 'social', 'sig', 'catlife']
# where a player finds each action first (the others are looked through if it is not there)
TAB_OF = {'expand': 'works', 'buyProject': 'works', 'buyOps': 'works', 'linSign': 'works', 'buyLounge': 'works', 'buyUp': 'works',
          'buySR': 'works', 'buyPD': 'works', 'hire': 'staff', 'hireLounge': 'staff', 'crewUp': 'staff', 'wineCourse': 'staff',
          'rd': 'menu', 'rdSpecial': 'menu', 'starUp': 'menu', 'labPick': 'menu', 'labTry': 'menu', 'buyEq': 'kitchen',
          'buyTable': 'home', 'buySideTable': 'home', 'buyFrontTable': 'home', 'buySideBooth': 'home', 'buyDecor': 'home',
          'buyLgFurn': 'home', 'campaign': 'social', 'sigOpen': 'sig', 'buyGear': 'catlife'}
SETTLE = ("__tick(30);for(const a of ['menuSwapNo','resetNo','importNo','pasteCancel','cnCancel','ktCancel']){const e=[...document.querySelectorAll('[data-act='+a+']')]"
          ".find(e=>e.offsetParent!==null);if(e)e.click()}if(typeof hideReveal==='function')try{hideReveal()}catch(e){};"
          "for(let i=0;i<80&&typeof DLG!=='undefined'&&DLG;i++){__tick(400);dlgNext()}")


def _sel(act, k=None, d=None):
    s = f'#screen [data-act="{act}"]'
    if k is not None: s += f'[data-k="{k}"]'
    if d is not None: s += f'[data-d="{d}"]'
    return s


class UI:
    """presses what is on the screen; returns False (and changes nothing) when the button is not there or is disabled"""
    def __init__(self, g):
        self.g = g

    def ev(self, js):
        return self.g.ev(js)

    def phase(self):
        return self.ev("phase")

    def visible(self, act, k=None, d=None):
        """the buttons of this kind on the screen now: [{k,d,text,disabled}]"""
        return self.ev("JSON.stringify([...document.querySelectorAll(%s)].filter(e=>e.offsetParent!==null).map(e=>({k:e.dataset.k??null,d:e.dataset.d??null,"
                       "text:(e.innerText||'').replace(/\\s+/g,' ').trim().slice(0,60),disabled:!!e.disabled})))" % json.dumps(_sel(act, k, d)))

    def buttons(self, act, k=None, d=None):
        return json.loads(self.visible(act, k, d))

    def open_tab(self, tab):
        if self.phase() != 'shop': return False
        if self.ev("typeof shopTab!=='undefined'?shopTab:''") == tab and self.ev("!!document.querySelector('#screen .tabs')"): return True
        ok = self.ev("(()=>{const e=document.querySelector('#screen [data-act=tab][data-k=%s]');if(!e||e.disabled)return false;e.click();return true})()" % json.dumps(tab))
        self.ev("__tick(30)")
        return bool(ok)

    def press(self, act, k=None, d=None):
        """the first enabled button of this kind on the current screen (or, in the shop, its usual tab, then the others)"""
        tabs = [None]
        if self.phase() == 'shop':
            first = TAB_OF.get(act)
            tabs = ([first] if first else []) + [t for t in SHOP_TABS if t != first]
        for tab in tabs:
            if tab is not None and not self.open_tab(tab): continue
            ok = self.ev("(()=>{const e=[...document.querySelectorAll(%s)].find(e=>e.offsetParent!==null&&!e.disabled);if(!e)return false;e.click();return true})()" % json.dumps(_sel(act, k, d)))
            if ok:
                self.ev(SETTLE)
                if self.phase() == 'shop': self.ev("if(!document.querySelector('#screen .tabs'))showShop()")   # back on the shop after a card the press opened
                return True
        return False


OBSERVE = r"""JSON.stringify((()=>{const L=S.lastSummary||{};const roles=(typeof CAP_ROLES!=='undefined'?CAP_ROLES:[]).map(r=>({r,n:roleCrew(r).length,cap:roleCap(r),hire:ROLES[r]&&ROLES[r].hire}));
 return {day:S.day,phase,money:S.money,rate:+rating().toFixed(1),level:S.level,tables:tablesTotal(),crew:(S.crew||[]).length,roles,
  lounge:loungeLv(),loungeCrew:typeof poolCrew==='function'?poolCrew('lounge').length:0,loungeCap:typeof loungeCap==='function'&&loungeLv()?loungeCap():0,
  sum:{guests:L.guests||0,lost:L.lost||0,angry:L.angry||0,walkins:L.walkins||0,rev:L.rev||0,tips:L.tips||0,cost:L.cost||0,wages:L.wages||0,rent:L.rent||0,wine:L.wine||0,net:L.net||0,
       why:(L.story||[]).map(x=>x.t||String(x)).slice(0,6)},
  viewing:!!fact('lin_viewing'),lin:!!fact('lounge_project')&&!loungeLv()?{state:(S.loungeProj||{}).state||null,cost:LOUNGE_PROJ[0].cost}:null}})())"""


def observe(ui):
    return json.loads(ui.ev(OBSERVE))


class Log:
    def __init__(self):
        self.rows = []

    def add(self, day, what, why):
        self.rows.append({'day': day, 'what': what, 'why': why})

    def today(self, day):
        return [r for r in self.rows if r['day'] == day]


# ---- the day's money and people, room by room (read-only: wrappers record, never change what the game does; no
# random numbers drawn, no time moved) ----
ECON_HOOKS = r"""(()=>{if(window.__econ)return 'already';window.__econ={};
 const D=()=>{const k=S.day;return __econ[k]=__econ[k]||{main:{groups:0,guests:0,food:0,drink:0,wine:0,tips:0},lounge:{groups:0,guests:0,food:0,drink:0,wine:0,tips:0},
   waits:[],served:0,samples:0,occMain:0,capMain:0,occLg:0,capLg:0,queue:0,left:{}}};
 const kind=d=>{const X=DISH(d)||{};return X.wine?'wine':X.cat==='drink'?'drink':'food'};
 const c0=collect;collect=function(g,o){const day=D();const lg=!!(g&&g.ticket&&g.ticket.lounge);const items=((g&&g.ticket&&g.ticket.items)||[]).filter(i=>i.st==='served');
  const r0=R.st.rev,t0=R.st.tips;const out=c0.apply(this,arguments);const dr=R.st.rev-r0,dt=R.st.tips-t0;
  const w={food:0,drink:0,wine:0};for(const it of items){w[kind(it.d)]+=priceOf(it.d)||0}const W=w.food+w.drink+w.wine;const box=lg?day.lounge:day.main;
  if(W>0)for(const k in w)box[k]+=dr*w[k]/W;else box.food+=dr;box.tips+=dt;
  if(!(o&&o.tab)&&!g.__econCounted){g.__econCounted=1;box.groups++;box.guests+=g.size||1}return out};
 const s0=serveItems;serveItems=function(g,list){const day=D();const tk=g&&g.ticket;const before=tk?tk.items.filter(i=>i.st==='served').length:0;const out=s0.apply(this,arguments);
  if(tk){const after=tk.items.filter(i=>i.st==='served').length;day.served+=after-before;if(before===0&&after>0&&tk.t0!=null)day.waits.push(Math.round(R.t-tk.t0))}return out};
 const l0=typeof leaveGroup==='function'?leaveGroup:null;if(l0)leaveGroup=function(g,why){const day=D();if(g&&!g.__econLeft&&g.state!=='leave'){g.__econLeft=1;day.left[why||'?']=(day.left[why||'?']||0)+(g.size||1)}return l0.apply(this,arguments)};
 window.__econSample=function(){if(!(R&&phase==='service'))return;const day=D();day.samples++;for(const t of R.tables){if(t.lounge){day.capLg++;if(t.group)day.occLg++}else if(t.room!=='front'||projOn('terrace')){day.capMain++;if(t.group)day.occMain++}}day.queue+=(typeof queued==='function'?queued().length:0)};
 return 'installed'})()"""

ECON_DAY = r"""JSON.stringify((()=>{const e=(window.__econ||{})[S.day]||null;const L=S.lastSummary||{};const parts=typeof rentParts==='function'?rentParts():[];
 const wage=m=>{try{return typeof crewWage==='function'?crewWage(m):0}catch(x){return 0}};const pools={restaurant:0,lounge:0};for(const m of (S.crew||[]))pools[typeof crewPool==='function'?crewPool(m):'restaurant']=(pools[typeof crewPool==='function'?crewPool(m):'restaurant']||0)+wage(m);
 return {e,rentParts:parts,wagePools:pools,sum:{guests:L.guests,lost:L.lost,angry:L.angry,rev:L.rev,tips:L.tips,cost:L.cost,wine:L.wine,wages:L.wages,rent:L.rent,net:L.net,lg:L.lg||null},money:S.money}})())"""
