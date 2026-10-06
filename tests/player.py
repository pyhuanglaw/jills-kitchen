"""The player's hands (QA, 2026-10-06): drive the game the way a person does — a phone-sized touch screen or a desktop
mouse, the story panels ON (the harness turns them off by default), taps on what is actually on screen — on top of the
same harness as every other test (`run_tests.Game`, its virtual time, its bot). Used by `tests/qa_tests.py` (the
routine QA) and by the deep audit's tools (`docs/audit/PLAYBOOK.md`).

The one rule that made it worth writing: a tap is a real input event at the element's place on screen, and it first
checks that a player could reach the element there.
  - a finger may swipe any scrolling list (vertical sheets and the sideways strips alike);
  - a mouse may only roll its wheel (vertical scrolling). A sideways strip with no scrollbar and no arrows cannot be
    scrolled by a mouse — exactly the desktop bug of 2026-10-04 ("電腦版升級餐廳點不到右邊的項目") that an ordinary
    element.click() hid, because it scrolls the element into view by itself.
  - the element's centre must be the element (nothing covering it) — the rc8.5 「II」 button that a sheet covered.

    from player import Player
    p = Player(b, port, target, save='player_day92_2105.json', W=390)     # or save=None: a new game; touch=False: a mouse
    p.tap_text('OPEN FOR DINNER'); p.tap('#screen [data-act=nextDay]'); p.settle()
    p.restock(); p.start_day(); p.play_evening()
"""
import json, os, re, sys

_rt = sys.modules['__main__'] if hasattr(sys.modules.get('__main__'), 'TESTS') else __import__('run_tests')
Game, ROOT, install_bot, LAZY_ACTOR, check = _rt.Game, _rt.ROOT, _rt.install_bot, _rt.LAZY_ACTOR, _rt.check
SAVES_DIR = os.path.join(ROOT, 'tests', 'saves')
SAVE_KEY = re.search(r"const KEY='([^']+)'", open(os.path.join(ROOT, 'js', 'game.js'), encoding='utf-8').read()).group(1)

# text that should never reach the player's eyes
BROKEN_TEXT = re.compile(r'undefined|NaN|\[object |\bnull\b')


class Unreachable(AssertionError):
    pass


class Player:
    def __init__(self, browser, port, target='index', save=None, W=390, H=844, seed=1, touch=True, scenes=True, checkpoint=True):
        """save: a file name in tests/saves (or a path, or a save dict). checkpoint=False drops a mid-service checkpoint,
        so the title offers only OPEN FOR DINNER."""
        storage = None
        if save is not None:
            raw = save if isinstance(save, dict) else json.load(open(save if os.path.isabs(save) else os.path.join(SAVES_DIR, save), encoding='utf-8'))
            raw = raw.get('save', raw)
            if not checkpoint:
                raw = dict(raw); raw['checkpoint'] = None
            storage = {SAVE_KEY: json.dumps(raw, ensure_ascii=False)}
        self.W, self.H, self.touch, self.scenes = W, H, touch, scenes
        self.g = Game(browser, port, target, seed=seed, manual=True, storage=storage, touch=touch, viewport={'width': W, 'height': H})
        self.page = self.g.page
        self.read = []          # every story line read through, in order
        if scenes:
            self.g.ev("window.__noScenes=false")
        self.frames(10)

    # ---- time (virtual: nothing moves unless it is advanced) ----
    def frames(self, n=1):
        n = int(n)
        while n > 0:
            k = min(n, 300); self.g.ev(f"for(let i=0;i<{k};i++)__tick(1000/30)"); n -= k

    def adv(self, seconds):
        self.frames(seconds * 30)

    # ---- looking ----
    def ev(self, js):
        return self.g.ev(js)

    @property
    def errors(self):
        return self.g.errors

    def state(self):
        return json.loads(self.g.ev("""JSON.stringify({phase,day:S.day,money:S.money,room:typeof room!=='undefined'?room:null,
          clock:(typeof R!=='undefined'&&R)?clockStr():null,dialog:(typeof DLG!=='undefined'&&DLG)?{line:$('#dlg .dlg-text').textContent,who:$('#dlg .dlg-name').textContent,held:!!DLG.hold}:null})"""))

    def text(self, sel='#screen'):
        return self.page.evaluate("s=>{const e=document.querySelector(s);return e&&!e.hidden?e.innerText:''}", sel)

    def visible_text(self):
        """everything written on the page that a player can see right now (sheets, toasts, faces, banner, panel, HUD)"""
        return self.page.evaluate("""()=>[...document.querySelectorAll('#screen,#toasts,#plines,#banner,#dlg,#hud,#coach,#storyNote,#tickets')]
            .filter(e=>!e.hidden&&e.offsetParent!==null).map(e=>e.innerText).join('\\n')""")

    def broken_text(self, extra=''):
        """'undefined', 'NaN', '[object …' or a bare 'null' in what the player can see (or in `extra`)"""
        return sorted(set(m.group(0) for m in BROKEN_TEXT.finditer(self.visible_text() + '\n' + extra)))

    def shot(self, path, full=False):
        self.frames(2)
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        self.page.screenshot(path=path, full_page=full)
        return path

    def overflow(self, within='body', allow=('#tickets', '.tabs', '#roomTabs')):
        """visible elements that stick out of the screen sideways or whose text is cut, except inside the scrolling strips
        that are meant to scroll sideways (`allow`)"""
        return self.page.evaluate("""([s,allow])=>{const W=innerWidth,out=[];for(const e of document.querySelectorAll(s+' *')){if(e.offsetParent===null)continue;
          if(allow.some(a=>e.closest(a)))continue;const r=e.getBoundingClientRect();if(r.width<2||r.height<2)continue;
          const txt=(e.innerText||'').replace(/\\s+/g,' ').trim().slice(0,40);const cs=getComputedStyle(e);
          if(r.right>W+1||r.left<-1)out.push(['offscreen',e.tagName+(e.id?'#'+e.id:''),Math.round(r.left),Math.round(r.right),txt]);
          else if(e.scrollWidth>e.clientWidth+2&&!['auto','scroll'].includes(cs.overflowX)&&cs.textOverflow!=='ellipsis'&&e.children.length===0)out.push(['cut',e.tagName,e.scrollWidth,e.clientWidth,txt])}return out.slice(0,40)}""", [within, list(allow)])

    def strip(self, sel):
        """a sideways-scrolling strip (the shop's tabs, the journal's tabs, the tickets): which of its items a player can
        see, and whether anything tells them there is more"""
        return self.page.evaluate("""s=>{const el=document.querySelector(s);if(!el||el.offsetParent===null)return null;const r=el.getBoundingClientRect();const cs=getComputedStyle(el);
          const items=[...el.children].filter(b=>b.offsetParent!==null).map(b=>{const q=b.getBoundingClientRect();
            return {text:(b.innerText||'').trim(),on:b.classList.contains('on'),visible:q.left>=Math.max(0,r.left)-1&&q.right<=Math.min(innerWidth,r.right)+1}});
          return {left:r.left,right:r.right,top:r.top,height:r.height,scrollLeft:el.scrollLeft,scrollWidth:el.scrollWidth,clientWidth:el.clientWidth,
            scrollbar:el.offsetHeight-el.clientHeight>2&&cs.scrollbarWidth!=='none',items}}""", sel)

    # ---- reaching and tapping, like a person ----
    def _locate(self, sel, nth=0, text=None):
        loc = self.page.locator(sel)
        if text is not None:
            loc = loc.filter(has_text=text)
        if loc.count() <= nth:
            raise Unreachable(f'nothing on the page matches {sel!r}' + (f' with 「{text}」' if text else ''))
        return loc.nth(nth)

    def reach(self, loc):
        """bring the element where the player can tap it, the way the player would, then return its centre on screen.
        A finger swipes any scrolling list; a mouse wheel only scrolls up and down."""
        h = loc.element_handle()
        info = self.page.evaluate("""([e,touch])=>{if(e.offsetParent===null&&getComputedStyle(e).position!=='fixed')return {err:'hidden'};
          if(e.disabled)return {err:'disabled'};
          for(let a=e.parentElement;a;a=a.parentElement){const cs=getComputedStyle(a);const r=a.getBoundingClientRect(),q=e.getBoundingClientRect();
            if(['auto','scroll'].includes(cs.overflowY)&&a.scrollHeight>a.clientHeight+1){if(q.top<r.top||q.bottom>r.bottom)a.scrollTop+=((q.top+q.bottom)/2-(r.top+r.bottom)/2)}
            if(['auto','scroll'].includes(cs.overflowX)&&a.scrollWidth>a.clientWidth+1&&(q.left<r.left||q.right>r.right)){
              const bar=a.offsetHeight-a.clientHeight>2&&cs.scrollbarWidth!=='none';
              if(touch||bar)a.scrollLeft+=((q.left+q.right)/2-(r.left+r.right)/2);else return {err:'sideways: a mouse cannot scroll this strip (no scrollbar, no arrows)'}}}
          const q=e.getBoundingClientRect();if(q.bottom<=0||q.top>=innerHeight||q.right<=0||q.left>=innerWidth)return {err:'off the screen'};
          const x=Math.min(innerWidth-1,Math.max(0,(q.left+q.right)/2)),y=Math.min(innerHeight-1,Math.max(0,(q.top+q.bottom)/2));
          const top=document.elementFromPoint(x,y);if(!top||!(top===e||e.contains(top)))return {err:'covered by '+(top?(top.id?'#'+top.id:top.tagName+'.'+String(top.className).split(' ')[0]):'nothing')};
          return {x,y}}""", [h, self.touch])
        if 'err' in info:
            raise Unreachable(info['err'])
        return info['x'], info['y']

    def tap(self, sel, nth=0, text=None, settle=True):
        """a real tap (finger) or click (mouse) on what the selector finds — only if a player could reach it"""
        if settle and sel != '#dlg':
            self.settle()
        x, y = self.reach(self._locate(sel, nth, text))
        if self.touch:
            self.page.touchscreen.tap(x, y)
        else:
            self.page.mouse.move(x, y); self.page.mouse.down(); self.page.mouse.up()
        self.frames(6)

    def tap_text(self, text, within='body'):
        """the first button (or [data-act] element) whose visible text contains `text`"""
        self.settle()
        sel = f"{within} button, {within} [data-act], {within} [data-room]"
        loc = self.page.locator(sel).filter(has_text=text)
        if loc.count() == 0:
            raise Unreachable(f'no button with 「{text}」')
        for i in range(loc.count()):
            if loc.nth(i).is_visible():
                return self.tap(sel, text=text, nth=i, settle=False)
        return self.tap(sel, text=text, settle=False)

    def can_reach(self, sel, nth=0, text=None):
        try:
            self.reach(self._locate(sel, nth, text)); return True
        except Unreachable:
            return False

    def tap_scene(self, x, y):
        """the room drawing, at the game's own coordinates (R.tables[i].x/.y, PASS, …)"""
        p = json.loads(self.g.ev(f"JSON.stringify((()=>{{const r=sc.getBoundingClientRect();return{{x:r.left+SV.ox+{x}*SV.s,y:r.top+SV.oy+{y}*SV.s}}}})())"))
        if self.touch:
            self.page.touchscreen.tap(p['x'], p['y'])
        else:
            self.page.mouse.click(p['x'], p['y'])
        self.frames(6)

    def room_tab(self, k):
        self.tap(f'#roomTabs [data-room={k}]')

    def resize(self, W, H=None):
        self.W, self.H = W, H or self.H
        self.page.set_viewport_size({'width': self.W, 'height': self.H}); self.page.wait_for_timeout(120); self.frames(4)

    def reload(self, background=True):
        """the phone leaves the app (pagehide / hidden — the game writes its checkpoint then) and comes back to a fresh page"""
        if background:
            self.g.ev("document.dispatchEvent(new Event('visibilitychange'));window.dispatchEvent(new Event('pagehide'))")
        self.g.reload(); self.page.wait_for_timeout(200)
        if self.scenes:
            self.g.ev("window.__noScenes=false")   # every load turns the harness's default (panels off) back on
        self.frames(10)

    # ---- the story panels ----
    def read_dialog(self, max_lines=120):
        """a story panel on screen: tap it line by line like a player; the lines read are returned (and kept in .read)"""
        lines = []
        for _ in range(max_lines):
            st = self.state()
            if not st['dialog']:
                break
            lines.append(f"{st['dialog']['who']}：{st['dialog']['line']}")
            self.frames(12)   # a moment to read (an instant second tap is ignored by design)
            try:
                loc = self.page.locator('#dlg')
                (loc.tap if self.touch else loc.click)(timeout=2000)
            except Exception:
                self.g.ev("dlgNext()")
            self.frames(4)
        self.read.extend(lines)
        return lines

    def settle(self):
        """a panel in the way is read through first, as a player must"""
        if self.g.ev("typeof DLG!=='undefined'&&!!DLG"):
            return self.read_dialog()
        return []

    # ---- a day ----
    def restock(self):
        """the prep screen's 「一鍵補到建議量」, by a tap (it is at the bottom of a long page: the player scrolls)"""
        m0 = self.state()['money']
        self.tap('#screen [data-act=restock]')
        return m0 - self.state()['money']

    def start_day(self, confirm=True):
        """開店. Returns the empty-fridge warning when the game shows one (confirm=True presses again, as it invites)"""
        self.tap('[data-act=start]')
        warn = None
        if self.g.ev("phase") != 'service':
            warn = self.text('#startWarn') or None
            if confirm and self.page.locator('[data-act=start]').count():
                self.tap('[data-act=start]')
        self.settle()
        return warn

    def capture_on(self):
        """record everything that pops up from now on (toasts, lines with a face, story lines, banners) with the clock"""
        self.g.ev(r"""(()=>{if(window.__cap)return;window.__cap=[];const rec=(k,t)=>__cap.push({k,t:String(t).replace(/<[^>]+>/g,''),c:(typeof R!=='undefined'&&R)?clockStr():phase,d:S.day});
          const t0=toast;toast=function(h,kind,o){rec('toast'+(kind?':'+kind:''),h);return t0.apply(this,arguments)};
          const p0=portraitLine;portraitLine=function(w,t,o){const r=p0.apply(this,arguments);if(r)rec('face:'+w,t);return r};
          const d0=dlgShow;dlgShow=function(){const L=DLG&&DLG.lines[DLG.i];if(L)rec('panel'+(DLG.hold?':held':''),(L.name||L.who||'')+'：'+L.text);return d0.apply(this,arguments)};
          const b0=banner;banner=function(a,b,c){rec('banner',a+' '+(b||''));return b0.apply(this,arguments)}})()""")

    def captured(self):
        return json.loads(self.g.ev("JSON.stringify(window.__cap||[])"))

    def play_evening(self, staff_do_it=True, max_seconds=1500):
        """the rest of the service played by the test bot (staff_do_it: the crew work and Jill does what nobody else can;
        False: the perfect player), the story panels read through like a player. Returns the seconds played."""
        install_bot(self.g)
        self.g.ev(LAZY_ACTOR)
        self.g.ev("window.__act=" + ("window.__actLazy" if staff_do_it else "window.__act"))
        t = 0
        while t < max_seconds and self.g.ev("phase") == 'service':
            if self.g.ev("typeof DLG!=='undefined'&&!!DLG"):
                self.read_dialog()
            self.g.ev("for(let i=0;i<30;i++){__act();__tick(1000/30)}")
            t += 1
        return t

    def close(self):
        try:
            self.g.close()
        except Exception:
            pass
