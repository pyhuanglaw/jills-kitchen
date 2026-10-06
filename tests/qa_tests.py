"""The routine QA (docs/QA.md) — what the deep audit of 2026-10-06 (docs/audit/2026-10-06/) found by playing, kept as
tests so it is never found by hand again. Every test here plays through `tests/player.py`: real taps on what is on
screen, a phone's touch screen (or a desktop mouse where that is the point), the story panels ON.

Same TESTS list as run_tests.py (imported at its end): `python3 tests/run_tests.py --qa` runs only these, and the full
regression runs them too. A test for a bug that is found but not fixed yet is listed in tests/qa_known_open.json: its
failure prints OPEN and does not fail the run; when it passes, the run fails until the entry is removed (from then on
it is that fix's regression test).

What is NOT here, on purpose: whether a line sounds like a person, whether a story is good, whether Day 90 is boring,
whether a feature is noticed — those need eyes (the deep audit, docs/audit/PLAYBOOK.md).
"""
import json, os, re, sys
_rt = sys.modules['__main__'] if hasattr(sys.modules.get('__main__'), 'TESTS') else __import__('run_tests')
test, check, ROOT, install_bot, LAZY_ACTOR = _rt.test, _rt.check, _rt.ROOT, _rt.install_bot, _rt.LAZY_ACTOR
from player import Player, Unreachable, BROKEN_TEXT, SAVES_DIR, SAVE_KEY

LATE = 'player_day92_2105.json'      # Day 92 after closing: $1.18M, 20 crew, the second floor (the late game)
LATE_CP = 'player_day89_0448.json'   # Day 89 with a mid-service checkpoint (18:59), Dylan revealed
MID = 'player_day61_0933.json'       # Day 61: the Lounge, 晴 × 阿拓 under way (the mid game)
WIDTHS = (375, 390, 430)


def _saved(name):
    raw = json.load(open(os.path.join(SAVES_DIR, name), encoding='utf-8'))
    return raw.get('save', raw)


def _to_service_from_late(p):
    """Day 92 (after closing) → the next day's service, by taps"""
    p.tap('#screen [data-act=open]')
    if p.state()['phase'] == 'shop':
        p.tap('#screen [data-act=nextDay]')
    p.settle()
    check(p.state()['phase'] == 'prep', f'not at the prep screen: {p.state()}')
    p.restock()
    p.start_day()
    check(p.state()['phase'] == 'service', f'the service did not start: {p.state()}')


def _till_vs_summary(p, m0, c0):
    """the money the till gained over a day against what the summary says the day made"""
    s = p.ev("S.lastSummary"); m1 = p.ev("S.money"); c1 = p.ev("S.todayCost")
    expect = m0 + s['rev'] + s['tips'] + s['bonus'] - s['wages'] - s.get('rent', 0) - s.get('wine', 0) - (s.get('cfee') or 0) + (s.get('loan') or 0) - (c1 - c0)
    return m1, expect, s


# ---------------------------------------------------------------- whole days by taps (guards)

@test
def qa_a_late_day_by_taps_from_prep_to_the_next_prep(b, port, target):
    """A day of the late game, every step a real tap (390×844 touch, the story panels read through): OPEN →
    準備 DAY 93 → 一鍵補到建議量 (at the bottom of a page of ten thousand pixels: the finger scrolls there) → 開店 → the
    evening (the crew work) → the summary → 升級餐廳 → 準備 DAY 94. Nothing the player sees reads 'undefined' or 'NaN'."""
    p = Player(b, port, target, save=LATE)
    try:
        _to_service_from_late(p)
        p.capture_on()
        p.play_evening()
        check(p.state()['phase'] == 'summary', f'the evening did not reach the summary: {p.state()}')
        seen = '\n'.join(x['t'] for x in p.captured()) + '\n'.join(p.read)
        check(not p.broken_text(seen), f'broken words on screen or in the evening: {p.broken_text(seen)}')
        p.tap('#screen [data-act=toShop]')
        check(p.state()['phase'] == 'shop', 'the summary\'s 升級餐廳 did not open the shop')
        check(not p.broken_text(), f'broken words in the shop: {p.broken_text()}')
        p.tap('#screen [data-act=nextDay]'); p.settle()
        st = p.state()
        check(st['phase'] == 'prep' and st['day'] == 94, f'準備 DAY 94 did not lead to the next prep: {st}')
        check(not p.errors, p.errors[:3])
    finally:
        p.close()


@test
def qa_a_new_game_first_day_by_taps(b, port, target):
    """A first-time player's Day 1 (390×844 touch, panels on): the title, Jill's morning line, 開店, the opening story
    (it holds the service until it is read), the tutorial's tips, the evening, the summary, the shop, Day 2's prep."""
    p = Player(b, port, target)
    try:
        p.tap('[data-act=open]'); p.settle()
        check(p.state()['phase'] == 'prep', f'OPEN FOR DINNER did not open the prep screen: {p.state()}')
        p.capture_on()
        p.start_day()
        check(p.state()['phase'] == 'service', 'Day 1 did not open')
        held = [x for x in p.captured() if x['k'] == 'panel:held']
        check(held, 'the opening story did not hold the service')
        coach = set()
        install_bot(p.g)
        for _ in range(1200):   # up to twenty game minutes, a second at a time
            if p.state()['phase'] != 'service':
                break
            c = p.page.evaluate("()=>{const e=document.querySelector('#coach');return e&&!e.hidden?e.innerText:''}")
            if c:
                coach.add(c)
            p.settle()
            p.ev("__bot(30,1/30)")
        check(len(coach) >= 4, f'the tutorial showed only {len(coach)} tips: {sorted(coach)[:3]}')
        check(p.state()['phase'] == 'summary', f'Day 1 did not reach the summary: {p.state()}')
        seen = '\n'.join(x['t'] for x in p.captured()) + '\n'.join(p.read)
        check(not p.broken_text(seen), f'broken words: {p.broken_text(seen)}')
        p.tap('#screen [data-act=toShop]'); p.tap('#screen [data-act=nextDay]'); p.settle()
        st = p.state()
        check(st['phase'] == 'prep' and st['day'] == 2, f'not at Day 2\'s prep: {st}')
        check(not p.errors, p.errors[:3])
    finally:
        p.close()


# ---------------------------------------------------------------- every button does something (guard)

# what a press can change, seen by the player or kept in the save — not the save's own time stamp (every save() writes one)
FINGERPRINT = """JSON.stringify([S.money,phase,sub||'',typeof shopTab!=='undefined'?shopTab:'',window.__toastN||0,
  (()=>{let h=0;const s=JSON.stringify(S,(k,v)=>k==='savedAt'||k==='savedLabel'?undefined:v);for(let i=0;i<s.length;i++)h=(h*31+s.charCodeAt(i))|0;return h})(),
  (()=>{const e=document.querySelector('#screen');return e?e.innerHTML.length:0})(),
  [...document.querySelectorAll('#reveal,#dlg')].map(e=>e.hidden?0:1).join('')])"""
SKIP_ACTS = {'tab', 'closeSub', 'nextDay', 'peek', 'guide', 'book', 'settings', 'reset', 'resetNo'}


def _back_to(p, where, k=None):
    """put away whatever a press opened (a story panel, a reveal card, a sub-screen, a peek at the room) and come back to the
    shop (on tab k) or the prep screen — the way the player closes it, done directly so the sweep can go on"""
    p.settle()
    # a question the press asked (換掉哪一道？ / are you sure?): the player answers no
    p.ev("for(const a of ['menuSwapNo','resetNo','importNo','pasteCancel','cnCancel','ktCancel']){const e=[...document.querySelectorAll('[data-act='+a+']')].find(e=>e.offsetParent!==null);if(e)e.click()}")
    p.ev("try{if(typeof hideReveal==='function')hideReveal()}catch(e){};if(sub&&sub!=='pause'){sub=null}")
    if where == 'shop':
        if k:
            p.ev(f"shopTab='{k}'")
        p.ev("if(phase==='shop')showShop()")
    else:
        p.ev("if(phase==='prep')showPrep()")
    p.frames(4)


def _sweep_tab(p, k, dead, tapped):
    _back_to(p, 'shop', k)
    p.ev("if(!window.__toastWrap){window.__toastWrap=1;window.__toastN=0;const t0=toast;toast=function(){__toastN++;return t0.apply(this,arguments)}}")
    seen = set()
    for _ in range(400):
        btns = p.page.evaluate("""skip=>[...document.querySelectorAll('#screen .sheet button, #screen .sheet [data-act]')].filter(e=>e.offsetParent!==null&&!e.disabled&&e.dataset.act&&!skip.includes(e.dataset.act))
            .map((e,i)=>[i,e.dataset.act,e.dataset.k||'',(e.innerText||'').replace(/\\s+/g,' ').trim().slice(0,24)])""", sorted(SKIP_ACTS))
        todo = [x for x in btns if (x[1], x[2], x[3]) not in seen]
        if not todo:
            return
        i, act, kk, txt = todo[0]; seen.add((act, kk, txt))
        if '使用中' in txt:
            continue
        before = p.ev(FINGERPRINT)
        sel = '#screen .sheet button, #screen .sheet [data-act]'
        loc = p.page.locator(sel).filter(has_text=txt) if txt else None
        try:
            # find this very button again (the sheet may have re-rendered): by its act, key and text
            idx = p.page.evaluate("""([skip,act,k,txt])=>{const all=[...document.querySelectorAll('#screen .sheet button, #screen .sheet [data-act]')];
                return all.findIndex(e=>e.offsetParent!==null&&!e.disabled&&e.dataset.act===act&&(e.dataset.k||'')===k&&(e.innerText||'').replace(/\\s+/g,' ').trim().slice(0,24)===txt)}""", [sorted(SKIP_ACTS), act, kk, txt])
            if idx < 0:
                continue
            p.tap(sel, nth=idx, settle=False)
        except Unreachable as e:
            dead.append(f'{k} › 「{txt}」 {act}:{kk} — cannot be reached: {e}')
            continue
        tapped.append((k, act, kk, txt))
        p.frames(10)
        after = p.ev(FINGERPRINT)
        if after == before:
            dead.append(f'{k} › 「{txt}」 {act}:{kk} — nothing happened')
        # whatever opened (a reveal card, a sub-screen, a story panel): put it away, back on this tab
        _back_to(p, 'shop', k)


def _new_game_shop(b, port, target, days=7):
    """a new game played quickly to the shop after Day `days` (the fast bot serves; the fridge stocked as the game does on
    Days 1–2) — a shop with almost everything still to buy"""
    p = Player(b, port, target)
    p.tap('[data-act=open]'); p.settle()
    for _ in range(days):
        p.ev("autoStock()"); p.start_day()
        install_bot(p.g); p.ev("__bot(60000,1/30)"); p.ev("while(typeof DLG!=='undefined'&&DLG)dlgNext()")
        p.ev("if(phase==='summary')showShop()")
        if p.state()['day'] < days:
            p.tap('#screen [data-act=nextDay]'); p.settle()
    return p


@test
def qa_every_button_in_the_shop_does_something(b, port, target):
    """The rc6–rc8.5 lesson: the upstairs rooms' 訂購／動工 did nothing for months because every test called the purchase
    function instead of pressing the button. Every enabled button in every tab of the shop is pressed by a finger, and
    something must happen (the money, the save, the sheet, a toast or a card) — in a young restaurant's shop (Day 7: almost
    everything still to buy) and in the late save's (Day 92: the rooms upstairs, the Lounge's furniture)."""
    dead, tapped = [], []
    for where in ('day7', 'day92'):
        p = _new_game_shop(b, port, target) if where == 'day7' else Player(b, port, target, save=LATE)
        try:
            if where == 'day92':
                p.tap('#screen [data-act=open]')
            check(p.state()['phase'] == 'shop', f'{where}: not in the shop: {p.state()}')
            p.ev("S.money=Math.max(S.money,5e6)")   # enough to buy anything offered, so a refusal is never the reason
            tabs = p.page.evaluate("()=>[...document.querySelectorAll('#screen .tabs [data-act=tab]')].filter(e=>!e.disabled).map(e=>e.dataset.k)")
            n0, d0 = len(tapped), len(dead)
            for k in tabs:
                _sweep_tab(p, k, dead, tapped)
            dead[d0:] = [f'{where} › {x}' for x in dead[d0:]]
            check(len(tapped) - n0 >= 15, f'{where}: only {len(tapped) - n0} buttons were pressed — the sweep did not see the shop')
            check(not p.errors, p.errors[:3])
        finally:
            p.close()
    check(not dead, f'{len(dead)} of {len(tapped)} buttons: ' + ' / '.join(dead[:8]))


PREP_SKIP = SKIP_ACTS | {'start', 'toShop', 'discardAll', 'discardAsk', 'restock'}   # restock: pressed first, on its own


@test
def qa_every_button_on_the_prep_screen_does_something(b, port, target):
    """The prep screen (the page a daily player uses most: the menu, the fridge, 補到建議量, the prices) on the late save:
    every enabled button pressed once by a finger has a visible effect. 一鍵補到建議量 first, while the fridge has room."""
    p = Player(b, port, target, save=LATE)
    dead = []
    try:
        p.tap('#screen [data-act=open]'); p.tap('#screen [data-act=nextDay]'); p.settle()
        check(p.state()['phase'] == 'prep', f'not at the prep screen: {p.state()}')
        p.ev("if(!window.__toastWrap){window.__toastWrap=1;window.__toastN=0;const t0=toast;toast=function(){__toastN++;return t0.apply(this,arguments)}}")
        before = p.ev(FINGERPRINT); p.restock()
        if p.ev(FINGERPRINT) == before:
            dead.append('一鍵補到建議量 — nothing happened')
        seen, n = set(), 0
        for _ in range(500):
            btns = p.page.evaluate("""skip=>[...document.querySelectorAll('#screen .sheet button, #screen .sheet [data-act]')].filter(e=>e.offsetParent!==null&&!e.disabled&&e.dataset.act&&!skip.includes(e.dataset.act))
                .map(e=>[e.dataset.act,e.dataset.k||'',e.dataset.d||'',e.dataset.v||'',(e.innerText||'').replace(/\\s+/g,' ').trim().slice(0,24)])""", sorted(PREP_SKIP))
            todo = [x for x in btns if tuple(x) not in seen]
            if not todo:
                break
            act, kk, dd, vv, txt = todo[0]; seen.add((act, kk, dd, vv, txt))
            sel = f'#screen .sheet [data-act="{act}"]' + (f'[data-k="{kk}"]' if kk else '') + (f'[data-d="{dd}"]' if dd else '') + (f'[data-v="{vv}"]' if vv else '')
            before = p.ev(FINGERPRINT)
            try:
                p.tap(sel, settle=False)
            except Unreachable as e:
                dead.append(f'「{txt}」 {act}:{kk}:{dd} — cannot be reached: {e}'); continue
            n += 1; p.frames(6)
            if p.ev(FINGERPRINT) == before:
                dead.append(f'「{txt}」 {act}:{kk}:{dd} — nothing happened')
            _back_to(p, 'prep')
        check(not dead, f'{len(dead)} of {n + len(dead)}: ' + ' / '.join(dead[:8]))
        check(n >= 20, f'only {n} buttons were pressed on the prep screen')
        check(not p.errors, p.errors[:3])
    finally:
        p.close()


@test
def qa_restock_says_why_it_cannot(b, port, target):
    """Known-open (WS2-04): 「補滿」 beside one dish fills the whole fridge with it (拿鐵 2→243, 400/400); then
    「一鍵補到建議量」 does nothing at all — no money, no toast, no change. A button that cannot do its job says why."""
    p = Player(b, port, target, save=LATE)
    try:
        p.tap('#screen [data-act=open]'); p.tap('#screen [data-act=nextDay]'); p.settle()
        p.ev("if(!window.__toastWrap){window.__toastWrap=1;window.__toastN=0;const t0=toast;toast=function(){__toastN++;return t0.apply(this,arguments)}}")
        d = p.ev("(document.querySelector('#screen [data-act=stockTo][data-k=max]')||{dataset:{}}).dataset.d")
        check(d, 'no 補滿 button on the prep screen')
        p.tap(f'#screen [data-act=stockTo][data-k=max][data-d="{d}"]')
        check(p.ev("stockTotal()>=fridgeCap()"), 'the fridge is not full after 補滿')
        before = p.ev(FINGERPRINT); p.tap('#screen [data-act=restock]')
        check(p.ev(FINGERPRINT) != before, '一鍵補到建議量 with a full fridge: nothing happens and nothing says why')
    finally:
        p.close()


@test
def qa_the_private_dining_room_is_bought_by_a_tap(b, port, target):
    """The Private Dining Room's 動工 by a finger (its story is opened ahead of the save's, to reach the state); the
    Staff Room's 訂購 is pressed in rc85_the_rooms_upstairs_are_bought_by_their_buttons."""
    p = Player(b, port, target, save=LATE)
    try:
        p.tap('#screen [data-act=open]')
        p.ev("factSet('pd_story');shopTab='works';showShop()"); p.frames(4)
        m0 = p.ev("S.money")
        p.tap('#screen [data-act=buyPD][data-k="1"]')
        p.settle(); p.ev("try{hideReveal()}catch(e){}")
        check(p.ev("S.money") < m0, f'the money did not move: {m0} → {p.ev("S.money")}')
        check(p.ev("!!(pdOf()&&pdOf().bought===S.day)"), f'no Private Dining Room on order: {p.ev("JSON.stringify(pdOf())")}')
    finally:
        p.close()


# ---------------------------------------------------------------- 繼續營業 (guard + known-open)

RESUMES = ['player_day2_2155.json', 'player_day30.json', 'player_day46.json', 'player_day81_2206.json', 'player_day83_2218.json',
           'player_day89_2320.json', LATE_CP]


def _resume(p):
    p.capture_on()
    p.tap('#screen [data-act=open]'); p.frames(10)
    fell = [x['t'] for x in p.captured() if '無法完整還原' in x['t']]
    return fell


@test
def qa_the_players_checkpoints_resume(b, port, target):
    """「繼續營業」 on the player's own mid-service saves from v2.2 to rc8.5: the evening comes back as it was (its
    guests at their tables), not 「今天的店內狀況無法完整還原」, and it plays on."""
    bad = []
    for name in RESUMES:
        raw = _saved(name); n = len(raw['checkpoint']['snap'].get('groups', []))
        p = Player(b, port, target, save=name)
        try:
            fell = _resume(p)
            got = p.ev("R?R.groups.length:-1")
            if p.state()['phase'] != 'service' or fell or (n >= 3 and got < n * 0.8):
                bad.append(f'{name}: phase {p.state()["phase"]}, {got}/{n} groups, {fell[:1]}')
                continue
            p.play_evening(max_seconds=20)
            if p.errors:
                bad.append(f'{name}: {p.errors[:2]}')
        finally:
            p.close()
    check(not bad, ' | '.join(bad))


@test
def qa_a_checkpoint_survives_a_new_table_count(b, port, target):
    """Known-open (WS2-01): the rc5–rc6 saves' checkpoints (Day 71 at 20:00, 31 groups) come back as an empty shop since
    a later version added a table (35 → 36): every version that changes the tables empties the evening a player left
    mid-service. And the explaining toast is pushed off at once."""
    name = 'player_day71_1215.json'
    n = len(_saved(name)['checkpoint']['snap']['groups'])
    p = Player(b, port, target, save=name)
    try:
        fell = _resume(p)
        got = p.ev("R?R.groups.length:-1")
        check(not fell and got >= n * 0.8, f'{got}/{n} groups after 繼續營業; {fell[:1]}')
    finally:
        p.close()


@test
def qa_a_held_story_survives_leaving_the_app(b, port, target):
    """Known-open (WS9-01, W3-06): a story holding the restaurant, the player leaves the app after its first line (or
    Safari drops the tab) and comes back with 繼續營業 — the story must not be lost: it plays again, or the journal keeps
    all of its lines. Today it is marked as happened and its page keeps the lines already read."""
    def run(leave):
        p = Player(b, port, target, save=MID, checkpoint=False)
        try:
            p.tap('#screen [data-act=open]'); p.settle()
            if p.state()['phase'] == 'shop':
                p.tap('#screen [data-act=nextDay]'); p.settle()
            p.restock(); p.start_day()
            install_bot(p.g); p.ev(LAZY_ACTOR); p.ev("window.__act=window.__actLazy")
            for _ in range(200):
                if p.ev("R.t>=R.dur*.35") or p.state()['phase'] != 'service':
                    break
                p.settle(); p.ev("for(let i=0;i<30;i++){__act();__tick(1000/30)}")
            # 晴 × 阿拓's first beat made due now (the way the suite's own hold tests reach a beat)
            p.ev("delete story().ev.qt_1;delete story().facts.qt_1;if(story().beatLines)delete story().beatLines.qt_1;storyDay().minor=0;storyDay().lp={};const E=STORY_EV.find(e=>e.k==='qt_1');E.when=()=>true")
            p.ev("storyTick('order',{})")
            check(p.ev("!!DLG&&DLG.hold"), 'the beat did not hold the service')
            if leave:
                p.frames(12); p.tap('#dlg'); p.frames(4)
                p.ev("Object.defineProperty(document,'hidden',{value:true,configurable:true});document.dispatchEvent(new Event('visibilitychange'))")
                p.reload(background=False)
                p.tap('#screen [data-act=open]'); p.frames(30)
                p.settle()
            else:
                p.read_dialog()
            return p.ev("JSON.stringify(((story().beatLines||{}).qt_1||[]).length)")
        finally:
            p.close()
    whole = int(run(False)); after = int(run(True))
    check(whole >= 3, f'the control run kept {whole} lines')
    check(after >= whole, f'after leaving the app the story keeps {after} of its {whole} lines and does not play again')


@test
def qa_leaving_while_closing_after_a_resume_keeps_the_day(b, port, target):
    """Known-open (W3-01): 繼續營業 near the end of an evening, the shop starts closing, the player leaves the app again —
    the day must still be there (the closing resumes, or the summary comes). Today the title offers OPEN FOR DINNER and
    the same day's prep: the evening's takings are kept, the summary, wages and rent never happen."""
    p = Player(b, port, target, save=LATE_CP)
    try:
        p.tap('#screen [data-act=open]'); p.frames(10)
        day = p.ev("S.day")
        install_bot(p.g); p.ev(LAZY_ACTOR); p.ev("window.__act=window.__actLazy")
        for _ in range(6000):
            if p.ev("phase") != 'service' or p.ev("R&&R.closed&&R.closing==null&&R.groups.length<=1"):
                break
            p.settle(); p.ev("for(let i=0;i<10;i++){__act();__tick(1000/30);if(DLG)break}")
        p.reload(); p.tap('#screen [data-act=open]'); p.frames(10)
        install_bot(p.g); p.ev(LAZY_ACTOR); p.ev("window.__act=window.__actLazy")
        for _ in range(3000):
            if p.ev("phase") != 'service' or p.ev("R&&R.closing!=null"):
                break
            p.settle(); p.ev("for(let i=0;i<10;i++){__act();__tick(1000/30);if(DLG)break}")
        p.adv(5); p.settle()
        p.reload()
        cp = p.ev("!!(S.checkpoint&&S.checkpoint.day===S.day)")
        check(cp or p.ev("S.day") > day or p.ev("!!S.lastSummary&&S.lastSummary.day===%d" % day),
              f'the day is gone: day {p.ev("S.day")}, no checkpoint, the title offers {p.text("#screen")[:80]!r}')
    finally:
        p.close()


# ---------------------------------------------------------------- screens on the three phones (guard)

def _overflow_everywhere(p, where, bad):
    o = p.overflow()
    if o:
        bad.append(f'{p.W}px {where}: {o[:2]}')


@test
def qa_the_screens_fit_375_390_430(b, port, target):
    """The title, the prep screen, the service, the shop's every tab, the journal's every tab and the settings at the
    three phone widths: nothing sticks out of the screen and no word is cut (the scrolling strips aside)."""
    bad = []
    for W in WIDTHS:
        p = Player(b, port, target, save=LATE, W=W)
        try:
            _overflow_everywhere(p, 'title', bad)
            p.tap('#screen [data-act=open]')
            for k in p.page.evaluate("()=>[...document.querySelectorAll('#screen .tabs [data-act=tab]')].filter(e=>!e.disabled).map(e=>e.dataset.k)"):
                p.tap(f'#screen .tabs [data-act=tab][data-k={k}]'); _overflow_everywhere(p, f'shop › {k}', bad)
            p.tap('#screen [data-act=book]')
            for k in p.page.evaluate("()=>[...document.querySelectorAll('#screen .tabs [data-act=btab]')].map(e=>e.dataset.k)"):
                p.tap(f'#screen .tabs [data-act=btab][data-k={k}]'); _overflow_everywhere(p, f'journal › {k}', bad)
            p.tap('#screen [data-act=closeSub]')
            p.tap('#screen [data-act=settings]'); _overflow_everywhere(p, 'settings', bad); p.tap('[data-act=closeSub]')
            p.tap('#screen [data-act=nextDay]'); p.settle(); _overflow_everywhere(p, 'prep', bad)
            p.restock(); p.start_day(); p.play_evening(max_seconds=40); p.settle()
            _overflow_everywhere(p, 'service', bad)
            check(not p.errors, p.errors[:3])
        finally:
            p.close()
    check(not bad, ' | '.join(bad[:6]))


@test
def qa_every_tab_reaches_by_finger(b, port, target):
    """The shop's and the journal's tab strips scroll sideways: on each phone width every tab can be swiped to and
    tapped, and the tap opens it."""
    bad = []
    for W in WIDTHS:
        p = Player(b, port, target, save=LATE, W=W)
        try:
            p.tap('#screen [data-act=open]')
            for k in p.page.evaluate("()=>[...document.querySelectorAll('#screen .tabs [data-act=tab]')].filter(e=>!e.disabled).map(e=>e.dataset.k)"):
                try:
                    p.tap(f'#screen .tabs [data-act=tab][data-k={k}]')
                    if p.ev("shopTab") != k:
                        bad.append(f'{W}px shop › {k}: the tap did not open it')
                except Unreachable as e:
                    bad.append(f'{W}px shop › {k}: {e}')
            p.tap('#screen [data-act=book]')
            for k in p.page.evaluate("()=>[...document.querySelectorAll('#screen .tabs [data-act=btab]')].map(e=>e.dataset.k)"):
                try:
                    p.tap(f'#screen .tabs [data-act=btab][data-k={k}]')
                except Unreachable as e:
                    bad.append(f'{W}px journal › {k}: {e}')
        finally:
            p.close()
    check(not bad, ' | '.join(bad[:6]))


@test
def qa_every_tab_reaches_by_mouse_in_a_small_window(b, port, target):
    """Known-open (the user, 2026-10-04 and 10-06: 「電腦版升級餐廳點不到右邊的項目」): a desktop window under 900×560 gets
    the phone's layout, and its tab strips have no scrollbar and no arrows — a mouse wheel scrolls the sheet, not the
    strip, so 員工 and 招牌菜 (and the journal's last tabs) cannot be reached."""
    bad = []
    for W, H in ((899, 800), (1280, 540)):
        p = Player(b, port, target, save=LATE, W=W, H=H, touch=False)
        try:
            p.tap('#screen [data-act=open]')
            for k in p.page.evaluate("()=>[...document.querySelectorAll('#screen .tabs [data-act=tab]')].filter(e=>!e.disabled).map(e=>e.dataset.k)"):
                if not p.can_reach(f'#screen .tabs [data-act=tab][data-k={k}]'):
                    bad.append(f'{W}×{H} shop › {k}')
            p.ev("showShop()"); p.tap('#screen [data-act=book]')
            for k in p.page.evaluate("()=>[...document.querySelectorAll('#screen .tabs [data-act=btab]')].map(e=>e.dataset.k)"):
                if not p.can_reach(f'#screen .tabs [data-act=btab][data-k={k}]'):
                    bad.append(f'{W}×{H} journal › {k}')
        finally:
            p.close()
    check(not bad, 'a mouse cannot reach: ' + ', '.join(bad))


@test
def qa_the_selected_tab_is_on_screen(b, port, target):
    """Known-open (W3-11, WS2-06): the shop opens on the tab the player used last — on the late save that is 廚房設備,
    which sits outside the screen; and after a tab further right is chosen, the strip jumps back to the start. The tab
    that is open must be one the player can see."""
    bad = []
    for W in WIDTHS:
        p = Player(b, port, target, save=LATE, W=W)
        try:
            p.tap('#screen [data-act=open]')
            st = p.strip('#screen .tabs')
            on = [x for x in st['items'] if x['on']]
            if on and not on[0]['visible']:
                bad.append(f'{W}px: the shop opens on 「{on[0]["text"]}」 off the screen')
            p.tap('#screen .tabs [data-act=tab][data-k=sig]')
            st = p.strip('#screen .tabs'); on = [x for x in st['items'] if x['on']]
            if on and not on[0]['visible']:
                bad.append(f'{W}px: after choosing 「{on[0]["text"]}」 the strip hides it')
        finally:
            p.close()
    check(not bad, ' | '.join(bad))


@test
def qa_the_pause_button_works_outside_the_service(b, port, target):
    """Known-open (WS2-03): on the prep screen and in the shop the HUD's 「II」 is drawn but a sheet covers it, so a tap
    never reaches it (it is meant to open 設定・存檔 there)."""
    p = Player(b, port, target, save=LATE)
    bad = []
    try:
        p.tap('#screen [data-act=open]')
        for where in ('shop', 'prep'):
            if where == 'prep':
                p.tap('#screen [data-act=nextDay]'); p.settle()
            try:
                p.tap('#hPause', settle=False)
                if p.ev("sub") != 'settings':
                    bad.append(f'{where}: the tap did not open the settings')
                p.ev("if(sub){sub=null;%s}" % ('showShop()' if where == 'shop' else 'showPrep()'))
            except Unreachable as e:
                bad.append(f'{where}: {e}')
    finally:
        p.close()
    check(not bad, ' | '.join(bad))


# ---------------------------------------------------------------- what the evening shows (known-open)

@test
def qa_a_drink_on_a_ticket_reads_right(b, port, target):
    """Known-open (W3-04): a drink not yet poured, tapped on its order ticket, says 「undefined都在忙！」 (the Lounge bar is
    missing from the stations' names). Drinks waiting on the tickets are tapped like the player did; nothing says 'undefined'."""
    p = Player(b, port, target, save=LATE)
    try:
        _to_service_from_late(p)
        p.capture_on()
        install_bot(p.g); p.ev(LAZY_ACTOR); p.ev("window.__act=window.__actLazy")
        tapped = 0
        for _ in range(240):   # until a few drinks still waiting to be poured have been tapped on their tickets
            p.settle(); p.ev("for(let i=0;i<30;i++){__act();__tick(1000/30)}")
            spots = p.ev("""JSON.stringify(R.tickets.flatMap(tk=>tk.items.map((it,i)=>({tk:tk.id,i,d:it.d,st:it.st}))).filter(x=>x.st==='pending'&&wineDish(x.d)).slice(0,2))""")
            for x in json.loads(spots):
                try:
                    p.tap(f'#tickets .it[data-tk="{x["tk"]}"][data-i="{x["i"]}"]', settle=False); tapped += 1
                except Unreachable:
                    pass
            if tapped >= 3:
                break
        bad = [x['t'] for x in p.captured() if BROKEN_TEXT.search(x['t'])]
        check(tapped >= 1, 'no drink waiting on a ticket could be tapped this evening')
        check(not bad, f'{bad[:3]}')
    finally:
        p.close()


@test
def qa_waiting_staff_do_not_stand_on_one_spot(b, port, target):
    """Known-open (W3-05, WS2-02): the waiters with nothing to do all stand on the same point by the door (6–7 people
    on one spot, one name tag on top), the cleaners on another. Two people waiting may not stand on each other."""
    p = Player(b, port, target, save=LATE)
    try:
        _to_service_from_late(p)
        install_bot(p.g); p.ev(LAZY_ACTOR); p.ev("window.__act=window.__actLazy")
        worst = 0
        for _ in range(60):
            p.settle(); p.ev("for(let i=0;i<30;i++){__act();__tick(1000/30)}")
            n = p.ev("""(()=>{const W=Object.values(R.cw||{}).filter(w=>!w.task&&(w.room||'main')==='main');let n=0;
              for(let i=0;i<W.length;i++)for(let j=i+1;j<W.length;j++)if(Math.hypot(W[i].x-W[j].x,W[i].y-W[j].y)<6)n++;return n})()""")
            worst = max(worst, n)
        check(worst == 0, f'{worst} pairs of idle staff on the same spot')
    finally:
        p.close()


@test
def qa_the_inspection_money_is_in_the_summary(b, port, target):
    """Known-open (WS1-02): the health inspector's +$300 / −$300 goes into the till but not into the summary, so 今日淨利
    is $300 off the money. With an inspection that evening, the till must match the summary."""
    p = Player(b, port, target, save=LATE)
    try:
        _to_service_from_late(p)
        m0 = p.ev("S.money") ; c0 = p.ev("S.todayCost")
        p.ev("R.inc=(R.inc||[]).filter(x=>x.k!=='inspector');R.inc.push({k:'inspector',t:R.t+5,tries:0})")
        p.play_evening()
        check(p.ev("(S.reviews||[]).some(r=>r.name==='衛生檢查員'&&r.day===S.day)"), 'no inspection happened')
        m1, expect, s = _till_vs_summary(p, m0, c0)
        check(m1 == expect, f'the till {m1} and the summary {expect} differ by {m1 - expect}')
    finally:
        p.close()


@test
def qa_table_hearts_only_for_sophie_and_mia(b, port, target):
    """Known-open (WS1-04): the user chose (2026-10-04) 「B. 愛心只給 Sophie 和 Mia；熟客不再有任何記號。」 rc8.5 changed the
    order ticket; the pink heart beside a table's bubble still comes for every returning guest and regular. Counted on
    the drawing itself: no pink heart over the room while Sophie and Mia are not there."""
    p = Player(b, port, target, save=LATE)
    try:
        _to_service_from_late(p)
        install_bot(p.g); p.ev(LAZY_ACTOR); p.ev("window.__act=window.__actLazy")
        p.ev("""(()=>{if(window.__hearts!=null)return;window.__hearts=0;const P=CanvasRenderingContext2D.prototype,f0=P.fill;
          P.fill=function(){if(String(this.fillStyle).toLowerCase()==='#e8798a'&&this.canvas===sc)window.__hearts++;return f0.apply(this,arguments)}})()""")
        bad = 0
        for _ in range(80):
            p.settle(); p.ev("window.__hearts=0;for(let i=0;i<30;i++){__act();__tick(1000/30)}")
            sm = p.ev("R.groups.some(g=>smHeart(g))")
            ret = p.ev("R.groups.some(g=>(g.ret||g.reg)&&g.table!=null&&!smHeart(g))")
            if ret and not sm and p.ev("window.__hearts") > 0:
                bad += 1
        check(bad == 0, f'{bad} seconds with pink hearts over the room and neither Sophie nor Mia there')
    finally:
        p.close()


# ---------------------------------------------------------------- the album (known-open)

@test
def qa_the_album_counts_all_five_cats(b, port, target):
    """Known-open (WS1-03, WS7-02, N01): the album's last card 「今天。」 says 「1 隻貓都在」 — it counts the cats in the
    dining room at that moment. The five cats are always there (PROJECT_MEMORY §4)."""
    p = Player(b, port, target, save=LATE)
    try:
        p.tap('#screen [data-act=open]'); p.tap('#screen [data-act=book]'); p.tap('#screen .tabs [data-act=btab][data-k=mem]')
        txt = p.text('#screen')
        m = re.search(r'(\d+) 隻貓都在', txt)
        check(m, 'no 「今天。」 card with the cats')
        check(m.group(1) == '5', f'the album says 「{m.group(0)}」')
    finally:
        p.close()


@test
def qa_photos_of_jills_room_are_taken_in_her_room(b, port, target):
    """Known-open (WS7-01): 「膝上的重量」 (and the sofa's other pictures) show the dining room — the photo is queued
    without its room, so the camera takes whatever room is on screen, and the true picture can never be taken. Jill on
    her sofa with a cat on her lap, the dining room on screen: the lap photo must belong to Jill's room."""
    p = Player(b, port, target, save=LATE)
    try:
        p.tap('#screen [data-act=open]')
        p.ev("""(()=>{window.__mq=[];const m0=memo;memo=function(id,x,y,info){const n=MEMQ.length;const r=m0.apply(this,arguments);if(MEMQ.length>n)__mq.push({id,room:MEMQ[MEMQ.length-1].room});return r};
          const aa=albumAllows;albumAllows=()=>true;/* the album's own pacing (a kind every three days) is not what this checks */const L=LIFE.jill;L.on=true;L.sinceSit=10;L.x=(SOFA.x0+SOFA.x1)/2;
          const c=CATS.find(c=>c.def.id==='tora')||CATS[0];c.sofa={kind:'lap',x:L.x,y:SOFA.catY};c.sofaOn=true;c.x=L.x;c.y=SOFA.catY;try{memChecks()}finally{albumAllows=aa}})()""")
        q = p.ev("JSON.stringify(window.__mq)")
        rows = [x for x in json.loads(q) if x['id'] in ('lap', 'sofa', 'sofafull', 'dylan')]
        check(rows, f'no sofa photo was queued: {q}')
        check(all(x['room'] == 'home' for x in rows), f'the sofa photos are queued for {rows}')
    finally:
        p.close()


# ---------------------------------------------------------------- words (known-open, objective ones only)

@test
def qa_a_favourite_is_missed_only_when_it_is_off_the_menu(b, port, target):
    """Known-open (N02): a regular whose favourite IS on today's menu and in the fridge says 「香煎鴨胸今天沒有喔？那我看看
    別的。」 because the line looks at the order, not the menu (Sophie, Mia, 小林 in one week; the user, rc8.3:
    「Sophie連續兩天說沒有香煎鴨胸很白癡」)."""
    p = Player(b, port, target, save=LATE)
    try:
        _to_service_from_late(p)
        said = p.ev("""(()=>{const out=[];const q0=quote;quote=function(g,t,o){out.push(t);return true};const r0=Math.random;Math.random=()=>0;
          try{for(const id of Object.keys(LOVES)){const L=LOVES[id];const d=L.d;if(!menuList().includes(d))continue;S.stock[d]=Math.max(5,S.stock[d]||0);
            S.regulars[id]=Math.max(4,S.regulars[id]||0);S.loveMiss={};R.loveSaid=0;const other=menuList().find(x=>x!==d&&DISH(x).cat==='main')||menuList().find(x=>x!==d);
            loveOrdered({reg:id,regs:[id],size:1,name:id},{items:[{d:other}]})}}finally{quote=q0;Math.random=r0}return out})()""")
        menu_names = p.ev("menuList().map(dishName)")
        wrong = [t for t in said if any(n and n in t for n in menu_names) and ('沒有' in t)]
        check(said, 'no favourite line was tried (no regular has a favourite on this menu)')
        check(not wrong, f'said with the dish on the menu and in the fridge: {wrong[:3]}')
    finally:
        p.close()


@test
def qa_a_review_talks_about_the_food_not_the_glass(b, port, target):
    """Known-open (WS6-06): a review names the first thing served — often the glass of wine poured with the dinner — as
    the dish: 「氣泡酒的火候剛剛好」「黑皮諾好吃，盤子乾淨得像沒用過」 (6–10 of the last 100 reviews in the user's Day 86–92
    saves). A dinner with a glass first and a dish after: the review speaks of the dish."""
    p = Player(b, port, target, save=LATE)
    try:
        _to_service_from_late(p)
        out = json.loads(p.ev("""JSON.stringify((()=>{const w=Object.keys(WINES)[0];const food=menuList().find(d=>DISH(d)&&DISH(d).cat==='main');const said=[];
          for(let i=0;i<12;i++){const g={name:'T',size:2,type:'couple',cats:[],ticket:{items:[{d:w,st:'served',lbar:true},{d:food,st:'served'}]},table:null};
            const r=addReview(g,5);if(r)said.push(r.txt)}   /* the journal keeps 80: count what is returned, not the list's length */
          return {wine:dishName(w),food:dishName(food),said}})())"""))
        named = [t for t in out['said'] if out['wine'] in t]
        check(out['said'], 'no review was written')
        check(not named, f'the review names the glass ({out["wine"]}) as the dish: {named[:2]}')
    finally:
        p.close()


@test
def qa_a_new_game_gets_no_old_version_notes(b, port, target):
    """Known-open (WS1-06): on Day 3 a new game's prep screen shows the notes written for v2.0/v2.1 saves (「2.1：食物與
    日常。…」「2.0：店可以變大了。…」), which are not true for a new restaurant."""
    p = Player(b, port, target)
    try:
        p.tap('[data-act=open]'); p.settle()
        for day in (1, 2):
            p.ev("autoStock()"); p.start_day()
            install_bot(p.g); p.ev("__bot(60000,1/30)"); p.ev("while(DLG)dlgNext()")
            p.ev("if(phase==='summary')showShop()"); p.tap('#screen [data-act=nextDay]'); p.settle()
        check(p.state()['day'] == 3, f'not at Day 3: {p.state()}')
        txt = p.text('#screen')
        check('2.0：' not in txt and '2.1：' not in txt, 'the Day 3 prep shows the version notes for old saves')
    finally:
        p.close()


@test
def qa_every_level_named_in_the_text_exists(b, port, target):
    """Known-open (WS5-04): the signature dessert's lock and the manual say 「需要擴建到 Jill's Kitchen」 — there is no such
    level (Little Kitchen → Bistro → Restaurant → Fine Dining → JILL); the dessert needs Jill's Restaurant. Every
    「擴建到 …」 written for the player names a real level."""
    src = open(os.path.join(ROOT, 'js', 'game.js'), encoding='utf-8').read()
    levels = [a or b for a, b in re.findall(r'\{n:"([^"]+)",tables:|\{n:\'([^\']+)\',tables:', src)]
    check(len(levels) >= 5, f'the levels were not found: {levels}')
    named = set(m.group(1).strip() for m in re.finditer(r"擴建到 (Jill(?:\\'|')s [A-Za-z ]+?|JILL)(?=[，、。<`\)\s]|$)", src))
    named = {x.replace("\\'", "'") for x in named}
    wrong = sorted(x for x in named if x not in levels and not any(x == l.split(' ')[0] for l in levels))
    check(not wrong, f'the text names levels that do not exist: {wrong} (the levels: {levels})')


# ---------------------------------------------------------------- the stories (guard)

@test
def qa_stories_wait_for_stories_not_for_dates(b, port, target):
    """The user, 2026-10-06: 「你不要固定某個故事是某一天……你就是設某個故事是哪一個故事的條件這樣玩下去就好了」. A story beat
    follows the stories before it and its own conditions; an absolute day in a beat's condition (S.day>=N) is allowed
    only where it is the point of the beat (the opening day's visit). A new one here fails until it is looked at."""
    allowed = {'lin_hello'}   # 《隔壁》: the opening day itself
    p = Player(b, port, target)
    try:
        rows = p.ev(r"""JSON.stringify(STORY_EV.map(E=>({k:E.k,w:String(E.when||'')})).filter(x=>/(?:S\.day|shopDay\(\))\s*(?:>=|>|<=|<|===)\s*\d/.test(x.w)).map(x=>x.k))""")
        found = set(json.loads(rows))
        check(not (found - allowed), f'story beats waiting for a calendar day: {sorted(found - allowed)}')
    finally:
        p.close()
