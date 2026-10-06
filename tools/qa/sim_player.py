"""A simulated person playing Jill's Kitchen from Day 1 (QA, 2026-10-06; the user: 「模擬一個真的在玩 Jill's Kitchen 的人」,
「真人玩家 timeline 的決策與操作，原則上只能根據玩家在當下畫面上實際看得到、按得到的資訊進行」).

Three parts, kept apart on purpose (the user asked for them to be listed as A and B):

A. 玩家行為 (the player) — `Screen`, `Hands`, `NormalPlayer`, `BaselinePlayer`.
   Reads only what is drawn on the page and acts only by real taps (a touch at the control's place on screen, after a
   finger-like scroll to it — `tests/player.py`'s reach) on a control that is there, enabled and not covered.
   STRUCTURAL GUARANTEE: this part holds the Playwright `page` only. Everything it reads goes through
   `page.evaluate()` in the page's global scope, where the game's state (S, R, fact(), LOUNGE_PROJ…) does not exist —
   the game is one closure; only the harness hook `window.__jk` (which this part never uses) can see inside. Its
   JavaScript touches the DOM only (checked by `tests/sim_player_tests.py`). Waiting is `__tick` (time passing).
   No state is written: no free stock, no money, no fake buttons, no actions the screen does not offer.

B. 觀測器 (the observer) — `Observer`.
   Reads the game's internal state through the harness hook (`g.ev`): the day's books by room, guests, seats, waits,
   story beats, the Lounge's state, the true rating. For the record and the checks only: the player never receives
   anything from it (the timeline passes it to the report, not to the policy). Its wrappers around game functions only
   count; they draw no random numbers and move no time.

C. 營業中的手 (the hands during a service) — `SERVICE` actors, run by the observer's hook because the service is drawn on
   a canvas, not in buttons. They act on what the room shows (who waits, which table needs Jill, which station needs
   her next step), through the game's own functions:
     'perfect' 完美操作玩家: the test suite's `__act` — every task at once, every frame, every step at the perfect moment.
               Its takings are NOT a normal player's.
     'human'   一般玩家節奏: lets the staff do their jobs (as `LAZY_ACTOR`) and does the rest like a person: notices a task
               ~0.9 s after it appears, one tap every ~0.45 s (quick taps 0.18 s), cooks on at most two stations at a
               time, and hits a timing step's perfect window about three times in four. Assumptions, written down;
               not measured from the user's hands.
     'staff'   讓員工做、Jill 補位: `LAZY_ACTOR` — the staff's jobs left to them, everything else instantly and perfectly.

Every decision the player makes goes into the day's log: what the screen showed → why → the control pressed (its
text, on which tab) → what it cost (the HUD before and after) → what happened.
"""
import json, re

# ======================================================================= A. 玩家行為 (the player)

# The only JavaScript part A runs. DOM only: no game names (tests/sim_player_tests.py checks this list).
_VIS = ("const vis=e=>!!e&&!e.hidden&&e.getClientRects().length>0&&getComputedStyle(e).visibility!=='hidden'"
        "&&(e.offsetParent!==null||getComputedStyle(e).position==='fixed');const clean=s=>String(s||'').replace(/\\s+/g,' ').trim();")
JS_KIND = "(()=>{" + _VIS + r"""const q=s=>document.querySelector(s);
 if(vis(q('#dlg')))return 'dialog';if(vis(q('#reveal')))return 'reveal';
 if(vis(q('#screen [data-act=open]')))return 'title';if(vis(q('#screen [data-act=toShop]')))return 'summary';
 if(vis(q('#screen [data-act=nextDay]')))return 'shop';if(vis(q('#screen [data-act=start]')))return 'prep';
 if(vis(q('#screen .modal')))return 'modal';
 const c=clean((q('#hClock')||{}).textContent);if(/^\d\d:\d\d/.test(c))return 'service';return 'other'})()"""
JS_HUD = "(()=>{" + _VIS + r"""const t=s=>clean((document.querySelector(s)||{}).textContent);
 return {day:parseInt(t('#hDay'))||0,clock:t('#hClock'),rate:parseFloat(t('#hRate')),money:parseInt(t('#hMoney').replace(/[^0-9]/g,''))||0}})()"""
JS_TEXT = "(sel=>{" + _VIS + "const e=document.querySelector(sel);return vis(e)?e.innerText:''})"
JS_BUTTONS = "(scope=>{" + _VIS + r"""const out=[];const all=[...document.querySelectorAll(scope+' [data-act]')].filter(vis);
 all.forEach((e,i)=>{const it=e.closest('.item,.menu-row');const nm=it&&it.querySelector('.nm');const d=it&&it.querySelector('.d');const lk=it&&it.querySelector('.lock,.act .muted');
  const st=nm&&nm.querySelector('.stars');let stars=null;if(st){const grey=[...st.querySelectorAll('span')].reduce((a,s)=>a+(s.textContent.match(/★/g)||[]).length,0);stars=(st.textContent.match(/★/g)||[]).length-grey}
  out.push({act:e.dataset.act,k:e.dataset.k??null,d:e.dataset.d??null,v:e.dataset.v??null,text:clean(e.innerText),dis:!!e.disabled,
   card:it?{nm:clean(nm&&nm.innerText),d:clean(d&&d.innerText),lock:clean(lk&&lk.innerText),stars,done:it.classList.contains('done'),on:it.classList.contains('menu-row')?!it.classList.contains('off'):null}:null})});return out})"""
JS_SUMMARY = "(()=>{" + _VIS + r"""const sc=document.querySelector('#screen');if(!vis(sc))return null;
 const money=s=>parseInt(String(s).replace(/[^0-9]/g,''))||0;const L={};
 for(const r of sc.querySelectorAll('.ledger > div')){const sp=r.querySelectorAll(':scope > span');if(sp.length<2)continue;const k=clean(sp[0].childNodes[0]&&sp[0].childNodes[0].textContent||sp[0].innerText);L[k]=(r.classList.contains('neg')?-1:1)*money(sp[1].innerText)}
 const rows=g=>[...sc.querySelectorAll('.rfg.'+g+' .rf')].map(r=>({k:clean((r.querySelector('.rf-k')||{}).innerText),v:clean((r.querySelector('.rf-v')||{}).innerText),s:clean((r.querySelector('.rf-s')||{}).innerText)}));
 const rl=sc.querySelector('.rating .rl b');const rr=rl?clean(rl.innerText).match(/([\d.]+)\s*→\s*([\d.]+)/):null;const arrow=clean((sc.querySelector('.rating .rl em')||{}).innerText);
 const stat=k=>{const c=[...sc.querySelectorAll('.statgrid .card')].find(c=>clean((c.querySelector('small')||{}).innerText)===k);return c?clean(c.innerText):''};
 const g=stat('客人數');const sales=[...sc.querySelectorAll('.sales:not(.lgsales):not(.dinwine) .sale:not(.set)')].map(s=>({nm:clean((s.querySelector('.nm')||{}).innerText).replace(/^⭐ /,''),n:parseInt(clean((s.querySelector('.n')||{}).innerText))||0,rev:money((s.querySelector('.rev')||{}).innerText),note:clean((s.querySelector('small')||{}).innerText)}));
 const lg=[...sc.querySelectorAll('.lgsales .sale:not(.tot):not(.tip)')].map(s=>({nm:clean((s.querySelector('.nm')||{}).innerText),n:clean((s.querySelector('.n')||{}).innerText),rev:money((s.querySelector('.rev')||{}).innerText)}));
 return {ledger:L,r0:rr?+rr[1]:null,r1:rr?+rr[2]:null,arrow,minus:rows('dn'),plus:rows('up'),
  guests:parseInt((g.match(/客人數\s*(\d+)/)||[])[1])||0,lost:parseInt((g.match(/(\d+) 位沒等到/)||[])[1])||0,walkins:parseInt((g.match(/(\d+) 組路過/)||[])[1])||0,
  perfect:stat('Perfect 料理'),sat:parseInt((stat('平均滿意度').match(/(\d+)%/)||[])[1])||null,sales,lounge:lg,
  staff:[...sc.querySelectorAll('.staffday .srow:not(.tot)')].map(r=>clean(r.innerText)),gate:clean((sc.querySelector('.rating small')||{}).innerText)}})()"""
JS_PREP = "(()=>{" + _VIS + r"""const sc=document.querySelector('#screen');if(!vis(sc))return null;const money=s=>parseInt(String(s).replace(/[^0-9]/g,''))||0;const tx=sc.innerText;
 const rows=[...sc.querySelectorAll('.menu-row:not(.wrow)')].map(r=>{const nm=r.querySelector('.nm');const name=clean(nm&&nm.childNodes[0]&&nm.childNodes[0].textContent);const small=clean((nm&&nm.querySelector('small')||{}).innerText);
   const meta=clean((r.querySelector('.meta')||{}).innerText);const tog=r.querySelector('[data-act=toggle]');const stk=r.querySelector('.stk span:not(.step) , .stk > span');
   return {name,d:tog&&tog.dataset.d,on:!r.classList.contains('off'),cat:small.split(' · ')[0],bar:/不佔名額/.test(small),price:money((meta.match(/^\$[\d,]+/)||['0'])[0]),cost:money((meta.match(/成本 \$[\d,]+/)||['0'])[0]),noStation:/客人不會點/.test(meta),
     stock:(()=>{const m=clean(r.innerText).match(/庫存\s*−?\s*(\d+) 份/);return m?+m[1]:null})()}});
 const cap=tx.match(/今日菜單\s*(\d+)\s*\/\s*(\d+)\s*道/);const fr=tx.match(/冰箱\s*(\d+)\s*\/\s*(\d+)/);const rs=[...sc.querySelectorAll('[data-act=restock]')].filter(vis)[0];
 const warn=clean((document.querySelector('#startWarn')||{}).innerText);const exp=tx.match(/預計約\s*(\d+)\s*位客人/);
 return {rows,menuN:cap?+cap[1]:null,menuCap:cap?+cap[2]:null,fridge:fr?[+fr[1],+fr[2]]:null,restock:rs?{text:clean(rs.innerText),dis:!!rs.disabled,price:money(rs.innerText)}:null,
  warn,expect:exp?+exp[1]:null,tablesWarn:/客人會等太久/.test(tx),notes:[...sc.querySelectorAll('.inline-warn,.warnline,.news li')].map(e=>clean(e.innerText)).slice(0,8)}})()"""
JS_SHOP_TOP = "(()=>{" + _VIS + r"""const sc=document.querySelector('#screen');if(!vis(sc))return null;const tx=sc.innerText;const m=re=>{const x=tx.match(re);return x?parseInt(x[1].replace(/,/g,'')):null};
 return {cash:m(/目前現金\s*\$([\d,]+)/),need:m(/預估基本備料 約 \$([\d,]+)/),keep:m(/建議保留 約 \$([\d,]+)/),low:/現在的現金可能不夠/.test(tx),
  tabs:[...sc.querySelectorAll('[data-act=tab]')].filter(vis).map(e=>({k:e.dataset.k,text:clean(e.innerText),dis:!!e.disabled,on:e.classList.contains('on')}))}})()"""
JS_STAFF = "(()=>{" + _VIS + r"""const sc=document.querySelector('#screen');if(!vis(sc))return null;const money=s=>parseInt(String(s).replace(/[^0-9]/g,''))||0;
 const cl=clean((sc.querySelector('.capline')||{}).innerText);const roles={};for(const x of cl.matchAll(/(廚師|服務生|清潔員|Lounge 員工)\s*(\d+)\/(\d+)/g))roles[x[1]]={n:+x[2],cap:+x[3]};
 const wages=money((cl.match(/每日薪資 \$[\d,]+/)||['0'])[0]);
 const hire=[...sc.querySelectorAll('.item[class*=hire-]')].map(it=>{const r=[...it.classList].find(c=>c.startsWith('hire-')).slice(5);const b=it.querySelector('[data-act=hire]');const d=clean((it.querySelector('.d')||{}).innerText);
   return {role:r,name:clean((it.querySelector('.nm')||{}).innerText),wage:money((d.match(/日薪 \$[\d,]+/)||['0'])[0]),btn:b&&vis(b)?{text:clean(b.innerText),dis:!!b.disabled,price:money(b.innerText)}:null,lock:clean((it.querySelector('.lock')||{}).innerText)}});
 const crew=[...sc.querySelectorAll('.item')].filter(it=>it.querySelector('[data-act=crewUp],[data-act=wineCourse]')||/目前：/.test(it.innerText)).map(it=>{const b=it.querySelector('[data-act=crewUp]');const nm=clean((it.querySelector('.nm')||{}).innerText);
   const lock=[...it.querySelectorAll('.cap .no')].map(x=>clean(x.innerText));const role=clean((it.querySelector('.nm .tier.t1')||{}).innerText);
   return {nm,role,lv:it.querySelectorAll('.pips i.on').length,d:clean((it.querySelector('.d')||{}).innerText),lock,up:b&&vis(b)?{k:b.dataset.k,text:clean(b.innerText),dis:!!b.disabled,price:money(b.innerText)}:null}});
 const lounge=[...sc.querySelectorAll('[data-act=hireLounge]')].filter(vis).map(b=>({k:b.dataset.k,text:clean(b.innerText),dis:!!b.disabled,price:money(b.innerText),card:clean((b.closest('.item')||{}).innerText).slice(0,80)}));
 return {line:cl,roles,wages,hire,crew,lounge}})()"""
JS_PANEL = "(()=>{" + _VIS + r"""const d=document.querySelector('#dlg');if(!vis(d))return null;return {who:clean((d.querySelector('.dlg-name')||{}).innerText),text:clean((d.querySelector('.dlg-text')||{}).innerText),next:clean((d.querySelector('.dlg-next')||{}).innerText)}})()"""
JS_TOASTS = "(()=>{" + _VIS + "return [...document.querySelectorAll('#toasts > *')].filter(vis).map(e=>clean(e.innerText)).slice(-4)})()"
JS_REVEAL = "(()=>{" + _VIS + "const r=document.querySelector('#reveal');if(!vis(r))return null;return {text:clean(r.innerText).slice(0,200),btns:[...r.querySelectorAll('[data-act]')].filter(vis).map(b=>({act:b.dataset.act,text:clean(b.innerText)}))}})()"
# a window that stops the day and asks (試酒的晚上, 新企劃 …): its words and its buttons
JS_MODAL = "(()=>{" + _VIS + r"""const m=document.querySelector('#screen .modal');if(!vis(m))return null;const t=s=>clean((m.querySelector(s)||{}).innerText);
 return {eyebrow:t('.eyebrow'),title:t('h2'),text:t('p'),btns:[...m.querySelectorAll('[data-act]')].filter(vis).map(b=>({act:b.dataset.act,k:b.dataset.k??null,text:clean(b.innerText),primary:b.classList.contains('primary'),dis:!!b.disabled}))}})()"""
PLAYER_JS = [JS_KIND, JS_HUD, JS_TEXT, JS_BUTTONS, JS_SUMMARY, JS_PREP, JS_SHOP_TOP, JS_STAFF, JS_PANEL, JS_TOASTS, JS_REVEAL, JS_MODAL]

SHOP_TABS = {'home': '家具與佈置', 'works': '店舖工程', 'social': '社群與宣傳', 'catlife': '貓咪生活', 'kitchen': '廚房設備', 'menu': '菜單研發', 'staff': '員工', 'sig': '招牌菜'}


def _money(s):
    m = re.search(r'\$([\d,]+)', s or '')
    return int(m.group(1).replace(',', '')) if m else 0


class Screen:
    """what is on the screen — page.evaluate in the page's global scope (the game's closure is out of its reach)"""
    def __init__(self, page):
        self.page = page

    def js(self, code, arg=None):
        return self.page.evaluate(code if arg is None else code, arg) if arg is not None else self.page.evaluate(code)

    def kind(self):
        return self.page.evaluate(JS_KIND)

    def hud(self):
        return self.page.evaluate(JS_HUD)

    def text(self, sel='#screen'):
        return self.page.evaluate(JS_TEXT, sel)

    def buttons(self, scope='#screen'):
        return self.page.evaluate(JS_BUTTONS, scope)

    def summary(self):
        return self.page.evaluate(JS_SUMMARY)

    def prep(self):
        return self.page.evaluate(JS_PREP)

    def shop_top(self):
        return self.page.evaluate(JS_SHOP_TOP)

    def staff(self):
        return self.page.evaluate(JS_STAFF)

    def panel(self):
        return self.page.evaluate(JS_PANEL)

    def toasts(self):
        return self.page.evaluate(JS_TOASTS)

    def reveal(self):
        return self.page.evaluate(JS_REVEAL)

    def modal(self):
        return self.page.evaluate(JS_MODAL)


class Hands:
    """real taps: the control is found on the screen, brought where a finger can reach it (a swipe of the list it is in),
    checked that nothing covers it, and touched at its centre (tests/player.py's reach). Time passes with __tick."""
    def __init__(self, player):
        self.p = player            # tests/player.Player — only its page, reach() and frames() are used
        self.page = player.page

    def wait(self, frames):
        self.p.frames(frames)

    def tap_sel(self, sel, nth=0):
        loc = self.page.locator(sel).nth(nth)
        x, y = self.p.reach(loc)
        if self.p.touch:
            self.page.touchscreen.tap(x, y)
        else:
            self.page.mouse.click(x, y)
        self.wait(6)

    def tap(self, act, k=None, d=None, scope='#screen'):
        sel = f'{scope} [data-act="{act}"]' + (f'[data-k="{k}"]' if k is not None else '') + (f'[data-d="{d}"]' if d is not None else '')
        n = self.page.locator(sel).count()
        for i in range(n):   # the first one a player can see and reach
            if self.page.locator(sel).nth(i).is_visible():
                self.tap_sel(sel, i)
                return True
        raise LookupError(f'no visible control {sel}')


class Log:
    """the decision log: 畫面看到什麼 → 為什麼 → 按了哪個控制項 → 花多少 → 結果"""
    def __init__(self):
        self.rows = []

    def add(self, day, saw, why, pressed=None, cost=None, result=None, kind='decide'):
        self.rows.append({'day': day, 'kind': kind, 'saw': saw, 'why': why, 'pressed': pressed, 'cost': cost, 'result': result})

    def today(self, day):
        return [r for r in self.rows if r['day'] == day]

    @staticmethod
    def line(r):
        s = f"[Day {r['day']}] 看到：{r['saw']} → {r['why']}"
        if r['pressed']:
            s += f" → 按「{r['pressed']}」"
        if r['cost'] is not None:
            s += f"（花 ${r['cost']:,}）"
        if r['result']:
            s += f" → {r['result']}"
        return s


class PlayerBase:
    """what every simulated person does the same way: read the panels, go through the day's screens, restock, open"""
    name, label = 'base', ''

    def __init__(self, screen, hands, log):
        self.s, self.h, self.log = screen, hands, log
        self.day = 0
        self.last_summary = None
        self.unknown = []

    # ---- panels, cards
    def read_panels(self, max_lines=200):
        """a story panel on screen: read and tap it line by line (a moment to read each, as a person does)"""
        lines = []
        for _ in range(max_lines):
            p = self.s.panel()
            if not p:
                break
            lines.append(f"{p['who']}：{p['text']}" if p['who'] else p['text'])
            self.h.wait(12)
            try:
                self.h.tap_sel('#dlg')
            except Exception:
                self.h.wait(30)
            self.h.wait(4)
        return lines

    def close_reveal(self):
        r = self.s.reveal()
        if not r:
            return False
        if not r['btns']:
            self.h.wait(60)   # 施工中…: the card turns into 完工 by itself
            r = self.s.reveal()
            if not r or not r['btns']:
                return False
        keep = [b for b in r['btns'] if b['act'] in ('revealClose', 'revealPrep')] or r['btns']
        b = keep[0]
        self.log.add(self.day, f"完工卡片：{r['text'][:60]}", '看完了，回到原本的畫面', b['text'], kind='screen')
        self.h.tap(b['act'], scope='#reveal')
        return True

    def answer_modal(self):
        """a window that stops the day and asks: read it, answer it from what it says"""
        m = self.s.modal()
        if not m or not m['btns']:
            return False
        saw = f"{m['eyebrow']}《{m['title']}》：{m['text'][:70]}"
        opts = [b for b in m['btns'] if not b['dis']]
        acts = {b['act'] for b in opts}
        if acts & {'roomGo', 'upGo'}:
            # 開始規劃 只是把它列進「店舖工程」，按鈕寫著不花錢；之後再說 也找得到 — a person who wants to see what comes plans it
            b = next((x for x in opts if str(x['k']).endswith('plan')), opts[0])
            why = '按鈕寫著「開始規劃」只是列進店舖工程、現在不花錢，想看看接下來會怎樣'
        elif 'tastingDir' in acts:
            # 「沒有標準答案」: nothing on the screen makes one better; a person tries the other one the next time
            last = getattr(self, 'tasting_last', None)
            b = next((x for x in opts if x['k'] != last), opts[0]) if last else opts[0]
            self.tasting_last = b['k']
            why = '畫面寫著「沒有標準答案」' + ('；上次選了另一個，這次換一個試試' if last else '；第一次，先選第一個')
        else:
            b = next((x for x in opts if x['primary']), opts[0])
            why = '沒處理過的視窗：按主要的那個按鈕'
            self.unknown.append(saw)
        self.log.add(self.day, saw, why, b['text'], kind='screen')
        self.h.tap(b['act'], k=b['k'])
        self.h.wait(6)
        return True

    def settle(self):
        """whatever stands between the player and the screen they were on"""
        for _ in range(12):
            k = self.s.kind()
            if k == 'dialog':
                self.read_panels()
            elif k == 'reveal':
                if not self.close_reveal():
                    break
            elif k == 'modal':
                if not self.answer_modal():
                    break
            else:
                return k
        return self.s.kind()

    def money(self):
        return self.s.hud()['money']

    def press(self, act, k=None, d=None, saw='', why='', label=None, tab=None, scope='#screen'):
        """a tap on a control that is on the screen, with its line in the log (and what it cost, read off the HUD)"""
        m0 = self.money()
        btns = [b for b in self.s.buttons(scope) if b['act'] == act and (k is None or b['k'] == k) and (d is None or b['d'] == d)]
        if not btns or btns[0]['dis']:
            self.log.add(self.day, saw, why + '（但按鈕不在畫面上或按不下去，沒按）', label, kind='skip')
            return False
        text = btns[0]['text'] or label or act
        t0 = self.s.toasts()
        self.h.tap(act, k, d, scope)
        self.settle()
        m1 = self.money()
        new = [t for t in self.s.toasts() if t not in t0]
        spent = m0 - m1
        self.log.add(self.day, saw, why, (f'{SHOP_TABS.get(tab, tab)} › ' if tab else '') + text, spent if spent else None,
                     (f'現金 ${m0:,} → ${m1:,}' if spent else '') + (('；' if spent else '') + f'畫面：{new[-1][:50]}' if new else ''))
        return True

    def open_tab(self, tab):
        top = self.s.shop_top()
        if not top:
            return False
        t = next((x for x in top['tabs'] if x['k'] == tab), None)
        if not t or t['dis']:
            return False
        if not t['on']:
            self.h.tap('tab', tab)
            self.settle()
        return True

    # ---- the day's screens
    def prep(self, day):
        self.day = day
        self.settle()
        self.prep_menu()
        self.prep_asks()
        self.restock()

    def prep_menu(self):
        pass

    def prep_asks(self):
        for b in self.s.buttons():
            if b['act'] == 'ktHold' and not b['dis']:
                self.press('ktHold', saw='開店前：「品酒之夜｜今晚要辦嗎？」', why='故事的活動，辦', label=b['text'])

    def restock(self):
        p = self.s.prep()
        r = p and p['restock']
        if not r:
            self.log.add(self.day, '開店前沒有「一鍵補到建議量」', '跳過補貨', kind='skip')
            return
        hud = self.s.hud()
        self.press('restock', saw=f"開店前：{r['text']}，現金 ${hud['money']:,}，冰箱 {p['fridge']}", why='每天開店前先補到建議量', label=r['text'])

    def open_shop(self):
        """開始營業 — a warning under the button is read; a second press opens anyway (as the warning invites)"""
        self.settle()
        self.press('start', saw='開店前畫面', why='準備好了，開始營業', label='開始營業')
        if self.s.kind() == 'prep':
            w = self.s.prep()['warn']
            self.log.add(self.day, f'開店按鈕下的提醒：「{w[:80]}」', '提醒讀過了；照它說的再按一次開店', kind='screen')
            self.h.tap('start')
        self.settle()

    def summary(self):
        self.settle()
        sm = self.s.summary()
        self.last_summary = sm
        return sm

    def to_shop(self):
        self.settle()
        self.h.tap('toShop')
        self.settle()

    def next_day(self):
        self.settle()
        self.h.tap('nextDay')
        self.h.wait(3)
        self.settle()

    def evening(self, day):
        pass


def _signals(sm):
    """what the summary says about the evening's service, in the words on the card"""
    minus = {r['k']: r for r in (sm or {}).get('minus', [])}
    plus = {r['k']: r for r in (sm or {}).get('plus', [])}
    pat = None
    for r in (sm or {}).get('minus', []) + (sm or {}).get('plus', []):
        m = re.search(r'耐心(?:剩)?\s*(\d+)%', r['v'] + ' ' + r['s'])
        if m:
            pat = int(m.group(1))
    angry = int((re.search(r'(\d+)', minus['生氣離開']['v']) or [0, 0])[1]) if '生氣離開' in minus else 0
    lost = (sm or {}).get('lost', 0)
    unmet = sum(int((re.search(r'少賣 (\d+)', x['note']) or [0, 0])[1]) for x in (sm or {}).get('sales', []) if '少賣' in x['note'])
    waits = '等太久' in minus or angry > 0 or (pat is not None and pat < 70) or lost >= 4
    why = []
    if '等太久' in minus: why.append(f"結算扣分「等太久 {minus['等太久']['v']}」")
    if angry: why.append(f'「生氣離開 {angry} 組」')
    if lost >= 4: why.append(f'「{lost} 位沒等到」')
    if pat is not None and pat < 70 and '等太久' not in minus: why.append(f'平均耐心 {pat}%')
    return {'waits': waits, 'why': '、'.join(why), 'lost': lost, 'angry': angry, 'patience': pat, 'unmet': unmet, 'full': '客滿離開' in minus,
            'down': (sm or {}).get('arrow') == '↓', 'r1': (sm or {}).get('r1'), 'minus': list(minus), 'plus': list(plus)}


class NormalPlayer(PlayerBase):
    """合理玩家模擬 (the user, 2026-10-06): fills staff places when guests wait or the rating falls on service, keeps buying
    what raises the takings (pricier dishes, their stars and special versions, the Lounge's wines), then space and the
    story's works, then the rest — always keeping a few days' running costs in the till (the shop's own 「建議保留」 plus two
    days of the wages and rent it shows). Never sits on money while the summary says guests waited and a place is free.
    Saving for a story's work (its card says how much is missing) holds back only the low-priority things."""
    name, label = 'normal', '合理玩家模擬'

    def __init__(self, screen, hands, log):
        super().__init__(screen, hands, log)
        self.rent = 0
        self.wages = 0
        self.saving_for = None
        self.menu_names = set()

    # ---- the prep screen: tonight's menu, the pricier dishes on it
    def prep_menu(self):
        p = self.s.prep()
        if p:
            self.menu_names = {r['name'] for r in p['rows'] if r['on']}
        if not p or not p['menuCap']:
            return
        rows = [r for r in p['rows'] if r['d'] and not r['noStation']]
        slot = [r for r in rows if not r['bar']]
        for r in [r for r in rows if r['bar'] and not r['on']]:
            self.press('toggle', d=r['d'], saw=f"開店前：酒吧小點「{r['name']}」不在今晚菜單（不佔名額）", why='放上去，多一樣可以賣', label=f"{r['name']} 的開關")
        # a dinner is a dish each, and now and then a drink or a dessert with it: keep the best-priced drink and dessert
        # (they are added to a main, not ordered instead of one), fill the rest with the highest prices
        keep = []
        for cat in ('飲料', '甜點'):
            c = sorted([r for r in slot if r['cat'] == cat], key=lambda r: -r['price'])
            if c:
                keep.append(c[0])
        rest = sorted([r for r in slot if r not in keep], key=lambda r: -r['price'])
        want = (keep + rest)[:p['menuCap']]
        if not any(r['cat'] == '主餐' for r in want):
            mains = sorted([r for r in slot if r['cat'] == '主餐'], key=lambda r: -r['price'])
            if mains:
                want = want[:-1] + mains[:1]
        wd = {r['d'] for r in want}
        off = [r for r in slot if r['on'] and r['d'] not in wd]
        add = [r for r in slot if not r['on'] and r['d'] in wd]
        for a in add:
            if self.s.prep()['menuN'] >= p['menuCap']:
                if not off:
                    break
                o = sorted(off, key=lambda r: r['price'])[0]
                off.remove(o)
                self.press('toggle', d=o['d'], saw=f"開店前：今日菜單 {self.s.prep()['menuN']}/{p['menuCap']} 道已滿；「{o['name']}」${o['price']} 是菜單上最便宜的", why=f"讓位給更貴的「{a['name']}」${a['price']}", label=f"{o['name']} 的開關")
            self.press('toggle', d=a['d'], saw=f"開店前：「{a['name']}」${a['price']} 研發好了但不在今晚菜單", why='售價比較高，放上菜單', label=f"{a['name']} 的開關")

    # ---- the shop, in the order the user plays it
    def evening(self, day):
        self.day = day
        sm = self.last_summary or {}
        sig = _signals(sm)
        self.rent = -(sm.get('ledger', {}).get('租金') or 0)
        top = self.s.shop_top() or {}
        self.reserve_base = max(top.get('keep') or 0, top.get('need') or 0)
        self.sig = sig
        self.staffing(sig)
        self.capacity(sig)
        self.revenue(sig)
        self.space_and_story(sig)
        self.low_priority(sig)

    def reserve(self):
        return self.reserve_base + 2 * (self.wages + self.rent)

    def can(self, price, extra=0):
        return self.money() - price >= self.reserve() + extra

    def staffing(self, sig):
        if not self.open_tab('staff'):
            return
        st = self.s.staff()
        self.wages = st['wages']
        order = ['waiter', 'chef', 'cleaner'] if sig['waits'] else ['chef', 'waiter', 'cleaner']
        names = {'waiter': '服務生', 'chef': '廚師', 'cleaner': '清潔員'}
        for role in order:
            for _ in range(4):
                st = self.s.staff()
                h = next((x for x in st['hire'] if x['role'] == role), None)
                if not h or not h['btn'] or h['btn']['dis']:
                    break
                cap = st['roles'].get(names[role], {})
                runway = 0 if sig['waits'] else 3 * h['wage']
                if not self.can(h['btn']['price'], runway):
                    self.log.add(self.day, f"員工：{names[role]} {cap.get('n')}/{cap.get('cap')}，聘請 ${h['btn']['price']:,}，日薪 ${h['wage']:,} 起；現金 ${self.money():,}",
                                 f"留下 ${self.reserve() + runway:,}（建議保留＋兩天薪資租金{'＋三天新薪水' if runway else ''}）就不夠，先不請", kind='hold')
                    break
                why = (f"{sig['why']} → 聘請{names[role]}" if sig['waits'] else f'{names[role]}還有名額，錢夠付幾天薪水 → 補人')
                if not self.press('hire', k=role, saw=f"員工：{names[role]} {cap.get('n')}/{cap.get('cap')}，{h['btn']['text']}，日薪 ${h['wage']:,} 起", why=why, label=h['btn']['text'], tab='staff'):
                    break
                self.wages = self.s.staff()['wages']
        # the Lounge's own people, when its list has places (they are the Lounge's story, too)
        for _ in range(3):
            st = self.s.staff()
            lg = [x for x in st['lounge'] if not x['dis']]
            if not lg or not self.can(lg[0]['price']):
                break
            if not self.press('hireLounge', k=lg[0]['k'], saw=f"員工 › Lounge 名單：{lg[0]['card'][:40]}", why='Lounge 的名單有空位，錢夠', label=lg[0]['text'], tab='staff'):
                break
        self.training(sig)

    def training(self, sig):
        """訓練升級 on the staff cards: a cook whose card locks a dish that is on tonight's menu (🔒 LV2 — Jill cooks it
        herself); a waiter below LV3 when guests wait (the card: LV2 起會上菜，LV3 起會結帳); anyone when guests wait and
        it is affordable; and, with plenty in the till, everyone towards LV5 (faster, and a cook's dishes Perfect)"""
        rich = self.money() > self.reserve() + 40000
        for _ in range(8):
            st = self.s.staff()
            cand = []
            for c in st['crew']:
                if not c['up'] or c['up']['dis']:
                    continue
                locked = [x for x in c['lock'] if any(n and n in x for n in self.menu_names)]
                if locked:
                    cand.append((0, c, f"員工：{c['nm']}（卡片上今晚菜單的菜鎖著：{'、'.join(locked[:2])}）", '這些菜現在都要 Jill 自己做 → 訓練廚師'))
                elif sig['waits'] and '服務生' in c['role'] and c['lv'] < 3:
                    cand.append((1, c, f"員工：{c['nm']} LV{c['lv']}（卡片寫 LV2 起會上菜，LV3 起會結帳）", f"{sig['why']} → 訓練服務生"))
                elif sig['waits']:
                    cand.append((2, c, f"員工：{c['nm']} LV{c['lv']}，{c['d'][:30]}", f"{sig['why']} → 訓練，動作快一點"))
                elif rich and c['lv'] < 5:
                    cand.append((3, c, f"員工：{c['nm']} LV{c['lv']}，現金 ${self.money():,}", '錢夠多，員工練到滿級'))
            if not cand:
                break
            cand.sort(key=lambda x: (x[0], x[1]['up']['price']))
            _, c, saw, why = cand[0]
            if not self.can(c['up']['price']):
                break
            if not self.press('crewUp', k=c['up']['k'], saw=saw, why=why, label=c['up']['text'], tab='staff'):
                break

    def capacity(self, sig):
        """guests turned away or waiting too long, and no free place left to hire into: more tables (up to the cap the
        card shows), then the expansion or the work whose card says it adds staff places or tables; the stove's next
        burner when the kitchen is the one place left"""
        if not (sig['waits'] or sig['lost'] >= 4 or sig['full']):
            return
        st = self.s.staff() if self.open_tab('staff') else None
        free_place = st and any(h['btn'] and not h['btn']['dis'] for h in st['hire'])
        if (sig['lost'] >= 4 or sig['full']) and self.open_tab('home'):
            for act in ('buyTable', 'buySideTable', 'buyFrontTable', 'buySideBooth'):
                for _ in range(2):
                    b = next((x for x in self.s.buttons() if x['act'] == act and not x['dis']), None)
                    if not b or not self.can(_money(b['text'])):
                        break
                    if not self.press(act, k=b['k'], saw=f"結算：「{sig['lost']} 位沒等到」；家具與佈置：{(b['card'] or {}).get('nm', '')} {b['text']}", why='客人來了沒位子坐，多一張桌子', label=b['text'], tab='home'):
                        break
        if (sig['waits'] or sig['lost'] >= 4) and self.open_tab('home'):
            for _ in range(3):
                pats = sorted([x for x in self.s.buttons() if x['act'] in ('buyDecor', 'buyExt') and not x['dis'] and x['card']
                               and re.search(r'耐心|門口最多再等|等的客人|願意等', x['card']['d'])], key=lambda x: _money(x['text']))
                if not pats or not self.can(_money(pats[0]['text'])):
                    break
                b = pats[0]
                if not self.press(b['act'], k=b['k'], saw=f"{sig['why'] or '客人沒位子'}；家具與佈置：「{b['card']['nm']}」{b['card']['d'][-30:]}", why='卡片寫客人等得住／門口多等幾組', label=b['text'], tab='home'):
                    break
        if free_place or not self.open_tab('works'):
            return
        cand = [x for x in self.s.buttons() if x['act'] in ('expand', 'buyProject', 'buyOps') and not x['dis'] and x['card']
                and re.search(r'服務生|廚師|清潔員|桌位上限|張桌', x['card']['d'])]
        cand.sort(key=lambda x: _money(x['text']))
        for b in cand[:1]:
            price = _money(b['text'])
            if not self.can(price):
                self.log.add(self.day, f"{sig['why'] or '客人沒位子'}；員工沒有空的名額；店舖工程：「{b['card']['nm']}」{b['text']}", f'付了就低於要留的 ${self.reserve():,}，再存', kind='hold')
                continue
            self.press(b['act'], k=b['k'], saw=f"{sig['why'] or '客人沒位子'}；員工沒有空的名額；店舖工程：「{b['card']['nm']}」{b['card']['d'][:60]}", why='工程寫著多員工名額／桌位：先解決人手和位子', label=b['text'], tab='works')

    def revenue(self, sig):
        bought = 0
        # new dishes, the most expensive first; a station a dish needs ("需要先購買烤箱") is part of buying it
        if self.open_tab('menu'):
            for _ in range(6):
                cards = [b for b in self.s.buttons() if b['act'] == 'rd' and b['card']]
                cand = sorted([b for b in cards if not b['dis']], key=lambda b: -_money(b['card']['d']))
                if not cand:
                    break
                b = cand[0]
                price = _money(b['text'])
                if not self.can(price):
                    self.log.add(self.day, f"菜單研發：「{b['card']['nm']}」{b['card']['d'][:30]}，{b['text']}", f'買了就低於要留的 ${self.reserve():,}，先不買', kind='hold')
                    break
                if not self.press('rd', d=b['d'], saw=f"菜單研發：「{b['card']['nm']}」{b['card']['d'][:30]}，{b['text']}", why='售價高的料理先研發', label=b['text'], tab='menu'):
                    break
                bought += 1
            # stars: the dishes that sold the most yesterday
            sold = [x['nm'] for x in sorted((self.last_summary or {}).get('sales', []), key=lambda x: -x['n'])]
            for _ in range(3):
                ups = [b for b in self.s.buttons() if b['act'] == 'starUp' and not b['dis'] and b['card']]
                ups.sort(key=lambda b: (sold.index(b['card']['nm'].split('★')[0].strip()) if b['card']['nm'].split('★')[0].strip() in sold else 99, -_money(b['card']['d'])))
                if not ups or not self.can(_money(ups[0]['text'])):
                    break
                nm = ups[0]['card']['nm'].split('★')[0].strip()
                if not self.press('starUp', d=ups[0]['d'], saw=f"食譜升級：「{nm}」{ups[0]['card']['d']}（卡片：每升一顆星售價 +15%）", why='賣得多的菜先升星' if nm in sold else '升星提高售價', label=ups[0]['text'], tab='menu'):
                    break
            for _ in range(2):
                sp = [b for b in self.s.buttons() if b['act'] == 'rdSpecial' and not b['dis'] and b['card']]
                if not sp or not self.can(_money(sp[0]['text'])):
                    break
                if not self.press('rdSpecial', d=sp[0]['d'], saw=f"特製版：「{sp[0]['card']['nm']}」{sp[0]['card']['d'][-24:]}", why='同一道菜賣更高的價', label=sp[0]['text'], tab='menu'):
                    break
            # the Lounge's wines (the user: 「酒類尤其要納入正常玩家的經濟策略」)
            for _ in range(4):
                wd = sorted([b for b in self.s.buttons() if b['act'] == 'wineDev' and not b['dis'] and b['card']], key=lambda b: -_money(re.sub(r'.*一杯', '', b['card']['d'])))
                if not wd or not self.can(_money(wd[0]['text'])):
                    break
                if not self.press('wineDev', k=wd[0]['k'], saw=f"酒單研發：「{wd[0]['card']['nm']}」{wd[0]['card']['d'][-26:]}", why='Lounge 多一支酒可以賣（卡片：留下來喝的人也會多一點）', label=wd[0]['text'], tab='menu'):
                    break
            # a dish that waits for a station: buy the station
            need = [b for b in self.s.buttons() if b['act'] == 'rd' and b['card'] and '需要先購買' in (b['card']['lock'] or '')]
            locks = [c for c in self.s.text().split('\n') if '需要先購買' in c]
            if locks and self.open_tab('kitchen'):
                for b in [x for x in self.s.buttons() if x['act'] == 'buyEq' and not x['dis'] and x['card'] and '未購買' in x['card']['nm']]:
                    if self.can(_money(b['text'])):
                        self.press('buyEq', k=b['k'], saw=f"菜單研發寫「{locks[0][:20]}」；廚房設備：{b['card']['nm']}", why='買了才能做那些料理', label=b['text'], tab='kitchen')
        # the kitchen keeps up when guests wait: the stove's next level is one more burner (its card says so)
        if sig['waits'] and self.open_tab('kitchen'):
            b = next((x for x in self.s.buttons() if x['act'] == 'buyEq' and x['k'] == 'stove' and not x['dis'] and x['card'] and '口爐' in x['card']['d']), None)
            if b and self.can(_money(b['text'])) and _money(b['text']) <= self.money() // 4:
                self.press('buyEq', k='stove', saw=f"{sig['why']}；廚房設備：{b['card']['nm']}，{b['card']['d'][:40]}", why='多一口爐，同時做的菜多一道', label=b['text'], tab='kitchen')
        if sig['unmet'] >= 6 and self.open_tab('kitchen'):
            b = next((x for x in self.s.buttons() if x['act'] == 'buyEq' and x['k'] == 'fridge' and not x['dis']), None)
            if b and self.can(_money(b['text'])):
                self.press('buyEq', k='fridge', saw=f"結算：賣完、估計少賣 {sig['unmet']} 份；廚房設備：{b['card']['nm']}", why='冰箱大一點，備料夠', label=b['text'], tab='kitchen')

    def space_and_story(self, sig):
        if not self.open_tab('works'):
            return
        btns = self.s.buttons()
        # the story's works: Madame Lin's bar, the Lounge's next steps, the floor upstairs and its rooms
        story_acts = ('linSign', 'buyLounge', 'buyUp', 'buySR', 'buyPD')
        self.saving_for = None
        for b in [x for x in btns if x['act'] in story_acts]:
            price = _money(b['text'])
            nm = (b['card'] or {}).get('nm') or b['text']
            if b['dis']:
                if price:
                    self.saving_for = (nm, price)
                    self.log.add(self.day, f"店舖工程：「{nm}」{b['text']}（按不下去）{(b['card'] or {}).get('lock', '')[:40]}", '這是故事的下一步，先存錢', kind='hold')
                continue
            if self.can(price):
                if self.press(b['act'], k=b['k'], saw=f"店舖工程：「{nm}」{b['text']}", why='故事的下一步，錢夠、留得住建議保留', label=b['text'], tab='works'):
                    btns = self.s.buttons()
            else:
                self.saving_for = (nm, price)
                self.log.add(self.day, f"店舖工程：「{nm}」{b['text']}，現金 ${self.money():,}", f'付了就低於要留的 ${self.reserve():,}，再存幾天', kind='hold')
        # the restaurant itself: the expansion and the works that add places and tables
        for _ in range(3):
            btns = self.s.buttons()
            cand = [x for x in btns if x['act'] in ('expand', 'buyProject', 'buyOps') and not x['dis'] and x['card']]
            if not cand:
                break
            staff_help = [x for x in cand if re.search(r'服務生|廚師|清潔員', x['card']['d'])]
            b = (staff_help if sig['waits'] else cand)[0] if (staff_help if sig['waits'] else cand) else cand[0]
            price = _money(b['text'])
            if self.saving_for and not (sig['waits'] and b in staff_help):
                self.log.add(self.day, f"店舖工程：「{b['card']['nm']}」{b['text']}", f"在存「{self.saving_for[0]}」，空間的工程等故事的工程之後", kind='hold')
                break
            if not self.can(price):
                break
            why = f"{sig['why']}，工程寫著多幾位員工的名額" if sig['waits'] and b in staff_help else '店變大：桌子、菜單、員工名額都多'
            if not self.press(b['act'], k=b['k'], saw=f"店舖工程：「{b['card']['nm']}」{b['card']['d'][:50]}，{b['text']}", why=why, label=b['text'], tab='works'):
                break

    def low_priority(self, sig):
        """the rest of the shop — furniture, the front of the shop, the cats' things, a kitchen station's next level — one
        or two an evening while saving for a story's work, more when the till is full"""
        goal = (self.saving_for[1] if self.saving_for else 0)
        n = 0
        for tab, acts in (('home', ('buyDecor', 'buyExt', 'buyTable', 'buySideTable', 'buyFrontTable', 'buySideBooth')), ('kitchen', ('buyEq',)), ('catlife', ('buyGear',))):
            if not self.open_tab(tab):
                continue
            for _ in range(6):
                cand = sorted([x for x in self.s.buttons() if x['act'] in acts and not x['dis']], key=lambda x: _money(x['text']))
                b = next((x for x in cand if self.money() - _money(x['text']) >= self.reserve() + goal + 2 * _money(x['text'])), None)
                if not b or n >= (2 if self.saving_for else 8):
                    break
                nm = (b['card'] or {}).get('nm', '') or b['text']
                why = '錢有餘，買一樣讓店更好的' + (f"（「{self.saving_for[0]}」的錢留著）" if self.saving_for else '')
                if not self.press(b['act'], k=b['k'], saw=f"{SHOP_TABS[tab]}：「{nm}」{((b['card'] or {}).get('d') or '')[-28:]}，{b['text']}", why=why, label=b['text'], tab=tab):
                    break
                n += 1


class BaselinePlayer(PlayerBase):
    """刻意不投資的 baseline: restocks, reads every panel, takes the story's yes/no, and buys nothing — to compare with,
    never to judge the game by"""
    name, label = 'baseline', '刻意不投資的 baseline'


POLICIES = {'normal': NormalPlayer, 'baseline': BaselinePlayer}


# ======================================================================= C. 營業中的手 (the hands during a service)

# a frame of the game's own loop (frameBody) without the drawing: time passes (the harness's __advance: the virtual
# clock and the game's timers, no requestAnimationFrame), the cats and the evening's life move, the service updates —
# held, as in play, while a story's panel holds it. The hands act first, as a finger between two frames would.
SERVICE_JS = r"""(()=>{if(window.__svc)return 'already';
 window.__svc={n:0};
 window.__frame=function(dt){const sp=phase==='service'&&R&&!paused?simSpeed():1;const sdt=dt*sp;if(R)R.speed=sp;
  if(typeof __advance==='function')__advance(dt*1000);const t=performance.now()/1000;
  if(!(phase==='service'&&(paused||(DLG&&DLG.hold)))){updateCats(sdt,t);lifeUpd(sdt)}
  if(phase==='service'&&R&&!paused&&!(DLG&&DLG.hold)){update(sdt)}
  if((++__svc.n)%4===0){try{if(phase==='service'&&R){renderTickets();hud()}}catch(e){}}};
 window.__runService=function(n,who){const dt=1/30;let i=0;const act=who==='perfect'?window.__act:who==='staff'?window.__actLazy:window.__actHuman;
  for(;i<n;i++){if(phase!=='service'||!R)break;if(DLG||paused)break;if(!R.closed||R.groups.length||R.closing==null){try{act(dt)}catch(e){__svc.err=(__svc.err||0)+1;__svc.last=String(e&&e.stack||e).slice(0,300)}}
   __frame(dt);if(window.__econSample&&__svc.n%30===0)__econSample();if(DLG||paused)break}return {i,phase,dlg:!!DLG,paused:!!paused}};
 return 'installed'})()"""

# 一般玩家節奏: assumptions, written down (see the module docstring)
HUMAN_JS = r"""(()=>{if(window.__actHuman)return 'already';
 const rnd=(()=>{let a=%(seed)d>>>0;return()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}})();
 window.__H={gap:%(gap)s,tap:%(tap)s,react:%(react)s,max:%(max)d,acc:{zone:[%(zp)s,%(zg)s],hold:[%(hp)s,%(hg)s],dose:%(dose)s},t:0,next:0,seen:{},sts:[],acts:0};
 window.__actHuman=function(dt){if(!(phase==='service'&&R))return false;const H=__H;H.t+=dt;if(H.t<H.next)return true;
  const cov=crewCovers;const C=[];const seen=k=>{if(H.seen[k]==null)H.seen[k]=H.t;return H.t-H.seen[k]>=H.react};
  H.sts=H.sts.filter(i=>R.slots[i]&&R.slots[i].job&&!chefHandles(R.slots[i]));
  for(const i of H.sts){const s=R.slots[i];const k=s.job.step;if(!k)continue;
   if(k.t==='add'){const id=k.left[0];if(id)C.push([9,'add'+i+id+k.left.length,()=>actIng(s,id),H.tap])}
   else if(k.t==='tap')C.push([9,'tap'+i+k.taps,()=>actTap(s),H.tap*.8]);
   else if(k.t==='zone'){if(k.tgt==null){const r=rnd(),sg=rnd()<.5?-1:1;k.tgt=r<H.acc.zone[0]?k.z.c:r<H.acc.zone[0]+H.acc.zone[1]?k.z.c+sg*(k.z.w+k.z.g)/2:k.z.c+sg*(k.z.g+.06);k.tgt=Math.max(.26,Math.min(1.12,k.tgt))}if(k.p>=k.tgt)C.push([10,'zone'+i+k.tgt,()=>actZone(s),H.tap])}
   else if(k.t==='hold')C.push([8,'hold'+i,()=>{const r=rnd(),mid=(k.a+k.b)/2;const lv=r<H.acc.hold[0]?mid:r<H.acc.hold[0]+H.acc.hold[1]?(rnd()<.5?k.a-.04:k.b+.04):(rnd()<.5?k.a-.14:k.b+.14);k.hold=true;R.holdSlot=s;k.level=Math.max(.05,Math.min(.99,lv));holdEnd()},H.gap*2]);
   else if(k.t==='dose'){if(k.goal==null)k.goal=rnd()<H.acc.dose?k.min:(rnd()<.5?Math.max(1,k.min-1):k.max+1);C.push([9,'dose'+i+k.cnt,()=>{if(k.cnt<k.goal)actDose(s);else actDoseDone(s)},H.tap])}}
  if(!R.closed&&!cov('seat'))for(const g of queued())if(g.state==='queue'){const t=freeTableFor(g);if(t){C.push([3,'seat'+g.id,()=>seatGroup(g,t),H.gap]);break}}
  for(const t of R.tables){if(!tableActionable(t)||jillTargets(t.i))continue;const g=t.group;
   if(!g){if(!cov('clean'))C.push([1,'clean'+t.i,()=>tapTable(t),H.gap]);continue}
   if(g.rowdy){C.push([6,'rowdy'+t.i,()=>tapTable(t),H.gap]);continue}
   if(g.state==='order'&&!cov('order'))C.push([4,'order'+t.i+g.id,()=>tapTable(t),H.gap]);
   else if(g.state==='check'&&!cov('check'))C.push([2,'check'+t.i+g.id,()=>tapTable(t),H.gap]);
   else if(g.state==='wait'&&!cov('serve'))C.push([5,'serve'+t.i+g.id,()=>tapTable(t),H.gap])}
  if(H.sts.length<H.max){let done=false;for(const tk of R.tickets){if(done)break;for(const it of tk.items)if(it.st==='pending'&&!chefCanAny(it.d)){C.push([4.5,'cook'+tk.id+'_'+tk.items.indexOf(it),()=>{if(startCook(tk,it,true)){const s2=R.slots.findIndex(x=>x.job&&x.job.it===it);if(s2>=0)H.sts.push(s2)}},H.gap]);done=true;break}}}
  for(let i=0;i<R.slots.length;i++)if(R.slots[i].broken)C.push([2.5,'fix'+i+R.slots[i].fix,()=>tapStation(i),H.tap]);
  const ready=C.filter(c=>c[0]>=8||seen(c[1]));if(!ready.length)return true;ready.sort((a,b)=>b[0]-a[0]);const c=ready[0];c[2]();H.acts++;H.next=H.t+c[3];return true};
 return 'installed'})()"""
HUMAN_DEFAULT = dict(gap=.45, tap=.18, react=.9, max=2, zp=.72, zg=.22, hp=.75, hg=.2, dose=.88)

SERVICE_LABELS = {'perfect': '完美操作玩家（每一步都在完美時機、同時做所有事；收入不是一般玩家收入）',
                  'human': '一般玩家節奏（員工做他們的事；Jill 看到事情約 0.9 秒後才動、每 0.45 秒一下、最多同時顧兩個工作站、時機題約四分之三打中 Perfect）',
                  'staff': '讓員工做、Jill 補位（員工的事交給員工，其餘 Jill 立刻、完美地做）'}


# ======================================================================= B. 觀測器 (the observer)

ECON_HOOKS = r"""(()=>{if(window.__econ)return 'already';window.__econ={};
 const D=()=>{const k=S.day;return __econ[k]=__econ[k]||{main:{groups:0,guests:0,food:0,drink:0,wine:0,tips:0},lounge:{groups:0,guests:0,food:0,drink:0,wine:0,tips:0},
   waits:[],served:0,samples:0,occMain:0,capMain:0,occLg:0,capLg:0,queue:0,left:{},arrived:0,turned:0}};
 const kind=d=>{const X=DISH(d)||{};return X.wine?'wine':X.cat==='drink'?'drink':'food'};
 const c0=collect;collect=function(g,o){const day=D();const lg=!!(g&&g.ticket&&g.ticket.lounge);const items=((g&&g.ticket&&g.ticket.items)||[]).filter(i=>i.st==='served');
  const r0=R.st.rev,t0=R.st.tips;const out=c0.apply(this,arguments);const dr=R.st.rev-r0,dt=R.st.tips-t0;
  const w={food:0,drink:0,wine:0};for(const it of items){w[kind(it.d)]+=priceOf(it.d)||0}const W=w.food+w.drink+w.wine;const box=lg?day.lounge:day.main;
  if(W>0)for(const k in w)box[k]+=dr*w[k]/W;else box.food+=dr;box.tips+=dt;
  if(!(o&&o.tab)&&g&&!g.__econCounted){g.__econCounted=1;box.groups++;box.guests+=g.size||1}return out};
 const s0=serveItems;serveItems=function(g,list){const day=D();const tk=g&&g.ticket;const before=tk?tk.items.filter(i=>i.st==='served').length:0;const out=s0.apply(this,arguments);
  if(tk){const after=tk.items.filter(i=>i.st==='served').length;day.served+=after-before;if(before===0&&after>0&&tk.t0!=null)day.waits.push(Math.round(R.t-tk.t0))}return out};
 const l0=leaveGroup;leaveGroup=function(g,why){const day=D();if(g&&!g.__econLeft&&!['paid','done'].includes(why)){g.__econLeft=1;const k=String(why||'?');day.left[k]=(day.left[k]||0)+(g.size||1)}return l0.apply(this,arguments)};
 window.__econSample=function(){if(!(R&&phase==='service'))return;const day=D();day.samples++;for(const t of R.tables){if(t.lounge){day.capLg++;if(t.group)day.occLg++}else{day.capMain++;if(t.group)day.occMain++}}day.queue+=(typeof queued==='function'?queued().length:0)};
 window.__notes=[];const nl=noteLine;noteLine=function(t){__notes.push({d:S.day,t:String(t)});return nl.apply(this,arguments)};
 return 'installed'})()"""

DAY_RECORD = r"""JSON.stringify((()=>{const L=S.lastSummary||{};const e=(window.__econ||{})[S.day]||null;
 const wage=m=>{try{return crewWage(m)}catch(x){return 0}};const pools={restaurant:0,lounge:0};for(const m of (S.crew||[])){const p=crewPool(m)==='lounge'?'lounge':'restaurant';pools[p]+=wage(m)}
 const roles={};for(const m of (S.crew||[])){const k=(crewPool(m)==='lounge'?'lg_':'')+m.role;roles[k]=(roles[k]||0)+1}
 return {day:S.day,money:S.money,level:S.level,rate:+rating().toFixed(2),rate1:+rating().toFixed(1),tables:tablesTotal(),crew:(S.crew||[]).length,roles,wagePools:pools,
  rentParts:L.rentParts||[],sum:{rev:L.rev,tips:L.tips,bonus:L.bonus,cost:L.cost,wages:L.wages,rent:L.rent,wine:L.wine,cfee:L.cfee,piano:L.piano,ken:L.ken,loan:L.loan,net:L.net,guests:L.guests,lost:L.lost,perfect:L.perfect,plated:L.plated,avg:L.avg,
   lg:L.lg?{tabs:L.lg.tabs,rev:L.lg.rev,tip:L.lg.tip}:null,lgSales:L.lgSales||null,dinWine:L.dinWine||null},econ:e,
  beats:(story().trace||[]).filter(t=>t.d===S.day).map(t=>t.lane[0]+':'+t.k),
  lounge:typeof loungeLv==='function'?loungeLv():0,proj:S.loungeProj?{state:S.loungeProj.state||null,open:S.loungeProj.open||null}:null,viewing:!!fact('lin_viewing'),
  linCard:(fact('lounge_project')&&!loungeLv())?{cost:LOUNGE_PROJ[0].cost}:null,up:!!(S.rooms&&S.rooms.up),wines:Object.keys(S.wineDev||{}).length,unlocked:(S.unlocked||[]).length,
  menu:menuList().map(d=>[d,priceOf(d)]),dy:S.dylan?{stage:S.dylan.stage,reveal:S.dylan.reveal||null}:null}})())"""


class Observer:
    """B: the game's state, for the record — never handed to the player"""
    def __init__(self, g):
        self.g = g

    def install(self):
        return self.g.ev(ECON_HOOKS)

    def day(self):
        return json.loads(self.g.ev(DAY_RECORD))

    def notes(self):
        return json.loads(self.g.ev("JSON.stringify(window.__notes||[])"))

    def phase(self):
        return self.g.ev("phase")
