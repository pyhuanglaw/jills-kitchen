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
test, check, setup_check, ROOT, install_bot, LAZY_ACTOR = _rt.test, _rt.check, _rt.setup_check, _rt.ROOT, _rt.install_bot, _rt.LAZY_ACTOR
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
    expect = m0 + s['rev'] + s['tips'] + s['bonus'] + (s.get('insp') or 0) - s['wages'] - s.get('rent', 0) - s.get('wine', 0) - (s.get('cfee') or 0) + (s.get('loan') or 0) - (c1 - c0)
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
  [...document.querySelectorAll('#reveal,#dlg,#upPlanBig,#peekPill')].map(e=>e.hidden?0:1).join('')])"""
SKIP_ACTS = {'tab', 'closeSub', 'nextDay', 'peek', 'guide', 'book', 'settings', 'reset', 'resetNo'}


def _back_to(p, where, k=None):
    """put away whatever a press opened (a story panel, a reveal card, a sub-screen, a peek at the room) and come back to the
    shop (on tab k) or the prep screen — the way the player closes it, done directly so the sweep can go on"""
    p.settle()
    # a question the press asked (換掉哪一道？ / are you sure?): the player answers no
    p.ev("for(const a of ['menuSwapNo','resetNo','importNo','pasteCancel','cnCancel','ktCancel']){const e=[...document.querySelectorAll('[data-act='+a+']')].find(e=>e.offsetParent!==null);if(e)e.click()}")
    p.ev("try{if(typeof hideReveal==='function')hideReveal()}catch(e){};if(sub&&sub!=='pause'){sub=null}")
    # a look at a room (二樓 看看整層) or the floor plan's zoom: the player taps 「回到店舖工程 ›」 / the picture to come back
    p.ev("for(const id of ['upPlanBig','peekPill']){const e=document.getElementById(id);if(e&&!e.hidden)e.click()}")
    if where == 'shop':
        if k:
            p.ev(f"shopTab='{k}'")
        p.ev("if(phase==='shop')showShop()")
    else:
        p.ev("if(phase==='prep')showPrep()")
    p.frames(1)


def _sweep_tab(p, k, dead, tapped):
    _back_to(p, 'shop', k)
    p.ev("if(!window.__toastWrap){window.__toastWrap=1;window.__toastN=0;const t0=toast;toast=function(){__toastN++;return t0.apply(this,arguments)}}")
    seen = set()
    for _ in range(400):
        btns = p.page.evaluate("""skip=>[...document.querySelectorAll('#screen .sheet button, #screen .sheet [data-act]')].filter(e=>e.offsetParent!==null&&!e.disabled&&e.dataset.act&&!skip.includes(e.dataset.act))
            .map((e,i)=>[i,e.dataset.act,e.dataset.k||'',(e.innerText||'').replace(/\\s+/g,' ').trim().slice(0,24)])""", sorted(SKIP_ACTS))
        todo = [x for x in btns if (x[1], x[2]) not in seen]
        if not todo or len(seen) >= 25:
            return
        i, act, kk, txt = todo[0]; seen.add((act, kk))   # its label may change after a press (a price, a count): the same button
        if '使用中' in txt or '現在' in txt:   # the one in use now (a theme, a set): pressing it again is meant to do nothing
            continue
        before = p.ev(FINGERPRINT)
        sel = '#screen .sheet button, #screen .sheet [data-act]'
        loc = p.page.locator(sel).filter(has_text=txt) if txt else None
        try:
            # find this very button again (the sheet may have re-rendered): by its act, key and text
            idx = p.page.evaluate("""([skip,act,k])=>{const all=[...document.querySelectorAll('#screen .sheet button, #screen .sheet [data-act]')];
                return all.findIndex(e=>e.offsetParent!==null&&!e.disabled&&e.dataset.act===act&&(e.dataset.k||'')===k)}""", [sorted(SKIP_ACTS), act, kk])
            if idx < 0:
                continue
            p.tap(sel, nth=idx, settle=False, wait=2)
        except Unreachable as e:
            dead.append(f'{k} › 「{txt}」 {act}:{kk} — cannot be reached: {e}')
            continue
        tapped.append((k, act, kk, txt))
        p.frames(2)
        after = p.ev(FINGERPRINT)
        if after == before:
            dead.append(f'{k} › 「{txt}」 {act}:{kk} — nothing happened')
        # whatever opened (a reveal card, a sub-screen, a story panel): put it away, back on this tab
        _back_to(p, 'shop', k)


def _new_game_shop(b, port, target, days=7):
    """a new game played to the shop after Day `days` (the fast bot serves; a story that holds the service stops the bot,
    so it is read through, as a player would, and the day goes on; the summary's 升級餐廳 by a tap) — a shop with almost
    everything still to buy"""
    p = Player(b, port, target)
    p.tap('[data-act=open]'); p.settle()
    for day in range(1, days + 1):
        p.ev("autoStock()"); p.start_day()
        install_bot(p.g)
        for _ in range(300):
            if p.state()['phase'] != 'service':
                break
            p.settle(); p.ev("__bot(2000,1/30)")
        p.settle()
        setup_check(p.state()['phase'] == 'summary', f'Day {day} did not reach the summary: {p.state()}')
        p.tap('#screen [data-act=toShop]')
        if day < days:
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
            setup_check(p.state()['phase'] == 'shop', f'{where}: not in the shop: {p.state()}')
            p.ev("S.money=Math.max(S.money,5e6)")   # enough to buy anything offered, so a refusal is never the reason
            tabs = p.page.evaluate("()=>[...document.querySelectorAll('#screen .tabs [data-act=tab]')].filter(e=>!e.disabled&&e.getAttribute('aria-disabled')!=='true').map(e=>e.dataset.k)")
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
            todo = [x for x in btns if tuple(x[:4]) not in seen]
            if not todo or len(seen) >= 320:
                break
            act, kk, dd, vv, txt = todo[0]; seen.add((act, kk, dd, vv))   # 「補到建議 25」 becomes 「補到建議 0」: the same button
            sel = f'#screen .sheet [data-act="{act}"]' + (f'[data-k="{kk}"]' if kk else '') + (f'[data-d="{dd}"]' if dd else '') + (f'[data-v="{vv}"]' if vv else '')
            before = p.ev(FINGERPRINT)
            try:
                p.tap(sel, settle=False, wait=2)
            except Unreachable as e:
                dead.append(f'「{txt}」 {act}:{kk}:{dd} — cannot be reached: {e}'); continue
            n += 1; p.frames(2)
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
    「一鍵補到建議量」 cannot buy the dishes still short — and says nothing. A button that cannot do its job says why: after
    the press every dish is at its suggestion, or something on screen (a toast, a line about the fridge) said why not."""
    p = Player(b, port, target, save=LATE)
    try:
        p.tap('#screen [data-act=open]'); p.tap('#screen [data-act=nextDay]'); p.settle()
        p.ev("if(!window.__toastWrap){window.__toastWrap=1;window.__toastN=0;const t0=toast;toast=function(){__toastN++;return t0.apply(this,arguments)}}")
        d = p.ev("([...document.querySelectorAll('#screen [data-act=stockTo][data-k=max]')].find(e=>e.offsetParent!==null&&!e.disabled)||{dataset:{}}).dataset.d")
        setup_check(d, 'no 補滿 button a player can see on the prep screen')
        p.tap(f'#screen [data-act=stockTo][data-k=max][data-d="{d}"]')
        SHORT = "JSON.stringify(Object.entries(suggestStock()).filter(([k,v])=>(S.stock[k]||0)<v).map(([k])=>k))"
        setup_check(p.ev("stockTotal()>=fridgeCap()") and json.loads(p.ev(SHORT)), f'the case: the fridge full after 補滿 {d}, other dishes short of their suggestion')
        t0, txt0 = p.ev("__toastN"), p.text('#screen'); p.tap('#screen [data-act=restock]')
        short, txt1 = json.loads(p.ev(SHORT)), p.text('#screen')
        said = p.ev("__toastN") > t0 or txt1.count('冰箱') > txt0.count('冰箱')
        check(not short or said, f'一鍵補到建議量 with a full fridge: {short} stay short and nothing says why')
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


# the line's state just after 《看看》, set directly (the quick way to that day): Jill has decided, her last night five days on
_AFTER_THE_VIEWING = """const st=story();const d=S.day;const set=(k,dd)=>st.facts[k]={d:dd,n:1,l:dd};
 for(const k of ['tasting_night','pairing_wine'])set(k,d-20);set('lin_retiring',d-6);linS().last=d+5;set('ken_where',d-5);set('jd_want',d-4);set('dylan_book',d-2);set('lin_viewing',d-1);
 for(const k of ['pairing_start','lin_retire','ken_where','jd_want','dylan_book','lin_viewing'])Object.assign(evState(k),{n:1,d:d-1});
 linDecided();showShop()"""


@test
def qa_lounge_one_signs_before_her_last_night(b, port, target):
    """The user, 2026-10-06/07: Lounge I is 《看看》 + $50,000 — her last night is her story, never a wait.
    The Day 52 save (rating 4.3, $173,060), 《看看》 behind it and her last night five days ahead: the player opens 店舖工程,
    taps 簽約・開工 — $50,000 goes and the signing is the next opening; the next morning 《簽約》 is read through and the
    work begins."""
    p = Player(b, port, target, save='player_day52.json')
    try:
        p.tap('#screen [data-act=open]')
        p.ev(_AFTER_THE_VIEWING); p.frames(2)
        setup_check(p.state()['phase'] == 'shop' and p.ev("S.money>=50000&&linLast()>S.day&&!fact('lin_closed')") is True,
                    f'the case: in the shop, $50,000+, her last night ahead: {p.state()}')
        p.tap('#screen [data-act=tab][data-k=works]')
        card = p.text('#screen .lin-card')
        check('最後一晚' not in card and 'Madame Lin 做到' not in card and '簽約・開工 $50,000' in card, f'the card waits for nothing but the money: {card[-80:]!r}')
        m0 = p.state()['money']
        p.tap('#screen .lin-card [data-act=linSign]')
        check(m0 - p.state()['money'] == 50000 and p.ev("S.loungeProj.state") == 'signing', f'簽約・開工 by a tap: {m0} → {p.state()["money"]}')
        p.tap('#screen [data-act=nextDay]'); p.settle(); p.restock(); p.start_day()
        check(any('那就這樣' in l for l in p.read) and p.ev("!!fact('lin_signed')") and p.ev("barState()") == 'reno', f'the next morning 《簽約》, then the work: {p.read[-6:]}')
        check(not p.errors, p.errors[:3])
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
    """WS9-01, W3-06 (fixed 2026-10-06): a story holding the restaurant, the player leaves the app after its first line
    (or Safari drops the tab) and comes back with 繼續營業 — the story is not lost: the lines not yet read are on screen
    again (the restaurant held until they are read) and its page keeps all of its lines. It used to be marked as
    happened with its page keeping only the lines already read."""
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
                held = p.ev("!!DLG&&!!DLG.hold&&phase==='service'")
                again = p.settle()
                return int(p.ev("JSON.stringify(((story().beatLines||{}).qt_1||[]).length)")), held, len(again)
            else:
                p.read_dialog()
            return int(p.ev("JSON.stringify(((story().beatLines||{}).qt_1||[]).length)")), True, 0
        finally:
            p.close()
    whole = run(False)[0]; after, held, again = run(True)
    check(whole >= 3, f'the control run kept {whole} lines')
    check(after >= whole, f'after leaving the app the story keeps {after} of its {whole} lines')
    check(held and again >= whole - 1, f'after 繼續營業 the rest of the story is not on screen again (held {held}, {again} lines read, {whole} in all)')


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
            for k in p.page.evaluate("()=>[...document.querySelectorAll('#screen .tabs [data-act=tab]')].filter(e=>!e.disabled&&e.getAttribute('aria-disabled')!=='true').map(e=>e.dataset.k)"):
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
def qa_the_task_list_opens_under_its_chip_and_any_tap_puts_it_away(b, port, target):
    """今日任務 (the user on the iPhone, 2026-10-10: 「今日任務的按鍵位置擋到冷盤了」「今日任務還沒辦法按掉」): the list opened over its
    own chip — in the kitchen over the sink and the cold station too — and nothing on it said how to close it; a tap
    beside it did not. On each phone width, a new game's first evening, in the kitchen and in the dining room, by finger:
    the list opens under its chip (the chip can still be reached), and the chip, its ×, the list itself and a tap
    anywhere else in the room each put it away."""
    bad = []
    for W in WIDTHS:
        p = Player(b, port, target, W=W)
        try:
            p.tap('[data-act=open]'); p.settle(); p.start_day(); p.settle()
            check(p.state()['phase'] == 'service', f'{W}px: Day 1 did not open')
            for rm in ('kitchen', 'main'):
                p.room_tab(rm)
                for nm, close in (('the chip', lambda: p.tap('#taskChip')), ('its ×', lambda: p.tap('#taskPanel .tpx')),
                                  ('the list', lambda: p.tap('#taskPanel h4')), ('a tap in the room', lambda: p.tap_scene(200, 300))):
                    p.tap('#taskChip')
                    if p.ev("$('#taskPanel').hidden"):
                        bad.append(f'{W}px {rm}: the chip did not open the list'); continue
                    if not p.can_reach('#taskChip'):
                        bad.append(f'{W}px {rm}: the open list covers its chip')
                    close()
                    if not p.ev("$('#taskPanel').hidden"):
                        bad.append(f'{W}px {rm}: {nm} did not put the list away'); p.ev("$('#taskPanel').hidden=true")
            check(not p.errors, p.errors[:3])
        finally:
            p.close()
    check(not bad, ' | '.join(bad[:6]))


@test
def qa_the_kitchen_chips_never_sit_on_the_counters(b, port, target):
    """庫存, 今日任務 and 💬 in the kitchen (the user, 2026-10-10: 「按鈕擋住冷盤台、點不到」, on a computer): they sit at a fixed height,
    and on a short screen — a laptop's window, a phone held sideways — the counters come up under them, so the stations there
    could not be tapped. On a tall phone, a phone sideways, a short laptop window and a desktop window, a new game's first
    evening in the kitchen: no chip lies on what can be tapped there (the counters and their stations, the coffee machine,
    the pizza oven: kitchenTapBoxes), none on the room tabs, and each can be reached by a finger."""
    bad = []
    for W, H in ((390, 844), (375, 667), (844, 390), (1100, 500), (1280, 720)):
        p = Player(b, port, target, W=W, H=H)
        try:
            p.tap('[data-act=open]'); p.settle(); p.start_day(); p.settle()
            p.room_tab('kitchen'); p.frames(10)
            r = json.loads(p.ev("""JSON.stringify((()=>{const s=sc.getBoundingClientRect(),X=x=>s.left+SV.ox+x*SV.s,Y=y=>s.top+SV.oy+y*SV.s;
              const box=e=>{if(!e||e.hidden)return null;const b=e.getBoundingClientRect();return{x0:b.left,x1:b.right,y0:b.top,y1:b.bottom}};
              return{boxes:kitchenTapBoxes().map(b=>({x0:X(b.x0),x1:X(b.x1),y0:Y(b.y0),y1:Y(b.y1)})),
                tabs:box($('#roomTabs')),chips:['stockChip','taskChip','logChip'].map(id=>[id,box($('#'+id))]).filter(c=>c[1])}})())"""))
            hit = lambda a, c: a['x0'] < c['x1'] - 1 and a['x1'] > c['x0'] + 1 and a['y0'] < c['y1'] - 1 and a['y1'] > c['y0'] + 1
            for cid, c in r['chips']:
                if any(hit(c, x) for x in r['boxes']):
                    bad.append(f'{W}×{H}: {cid} on the counters ({c})')
                if r['tabs'] and hit(c, r['tabs']):
                    bad.append(f'{W}×{H}: {cid} on the room tabs')
                if not p.can_reach('#' + cid):
                    bad.append(f'{W}×{H}: {cid} cannot be reached')
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
            for k in p.page.evaluate("()=>[...document.querySelectorAll('#screen .tabs [data-act=tab]')].filter(e=>!e.disabled&&e.getAttribute('aria-disabled')!=='true').map(e=>e.dataset.k)"):
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
    """W3-11 / the user (2026-10-04, 10-06: 「電腦版升級餐廳點不到右邊的項目」— the blocker before testing on a computer):
    under 900×560 a desktop window got the phone's layout, the tab strips had no scrollbar and no arrows, and a mouse
    wheel scrolls the sheet, not the strip — 員工 and 招牌菜 (and the journal's last tabs) could not be reached; the old
    tests scrolled them into view and passed. Now, with a mouse, every tab of the shop and of the journal is on the
    screen (the strip wraps): nothing hidden to the side, each one clicked where it is (no scrolling done for the
    player), the shop or the journal turns to it, and the open tab stays in sight. Common desktop windows, from
    1366×768 down to 800×600 (1024, 900 and just under 900 among them)."""
    bad = []
    for W, H in ((1366, 768), (1280, 540), (1024, 768), (900, 700), (899, 800), (800, 600)):
        p = Player(b, port, target, save=LATE, W=W, H=H, touch=False)
        try:
            p.tap('#screen [data-act=open]')
            for sheet, act, var in (('shop', 'tab', 'shopTab'), ('journal', 'btab', 'bookTab')):
                if sheet == 'journal':
                    p.ev("showShop()"); p.tap('#screen [data-act=book]')
                st = p.strip('#screen .tabs')
                hidden = [x['text'] for x in st['items'] if not x['visible']] if st else ['(no strip)']
                if hidden:
                    bad.append(f'{W}×{H} {sheet}: tabs off the screen with a mouse: {hidden}')
                keys = p.page.evaluate(f"()=>[...document.querySelectorAll('#screen .tabs [data-act={act}]')].filter(e=>!e.disabled&&e.getAttribute('aria-disabled')!=='true').map(e=>e.dataset.k)")
                for k in keys:
                    sel = f'#screen .tabs [data-act={act}][data-k={k}]'
                    try:
                        p.tap(sel)
                    except Exception as e:
                        bad.append(f'{W}×{H} {sheet} › {k}: {e}'); continue
                    if p.ev(var) != k:
                        bad.append(f'{W}×{H} {sheet} › {k}: clicked, but it shows {p.ev(var)}'); continue
                    st = p.strip('#screen .tabs'); on = [x for x in st['items'] if x['on']]
                    if not on or not on[0]['visible']:
                        bad.append(f'{W}×{H} {sheet} › {k}: the open tab is out of sight')
        finally:
            p.close()
    check(not bad, 'with a mouse: ' + '; '.join(bad[:10]))


@test
def qa_the_selected_tab_is_on_screen(b, port, target):
    """W3-11, WS2-06: the shop opens on the tab the player used last — on the late save that is 廚房設備, which sat
    outside the screen; and after a tab further right was chosen, the strip jumped back to the start. On a phone the open
    tab is always in sight (the strip keeps where the finger left it); the strip is still one row a finger swipes
    sideways (the user: 「手機原本的橫向操作不要被修壞」), and where more tabs are off to one side it fades on that side."""
    bad = []
    for W in WIDTHS:
        p = Player(b, port, target, save=LATE, W=W)
        try:
            p.tap('#screen [data-act=open]')
            def look(when):
                st = p.strip('#screen .tabs')
                on = [x for x in st['items'] if x['on']]
                if on and not on[0]['visible']:
                    bad.append(f'{W}px {when}: the open tab 「{on[0]["text"]}」 is off the screen')
                tops = p.page.evaluate("()=>[...document.querySelectorAll('#screen .tabs button')].map(e=>Math.round(e.getBoundingClientRect().top))")
                if len(set(tops)) != 1 or st['scrollWidth'] <= st['clientWidth']:
                    bad.append(f'{W}px {when}: the strip is no longer one sideways row ({len(set(tops))} rows, {st["scrollWidth"]}/{st["clientWidth"]})')
                cls = p.ev("document.querySelector('#screen .tabs').className")
                idx = [i for i, x in enumerate(st['items']) if x['visible']]
                if idx and idx[-1] < len(st['items']) - 1 and 'more-r' not in cls:
                    bad.append(f'{W}px {when}: tabs to the right, no sign of them')
                if idx and idx[0] > 0 and 'more-l' not in cls:
                    bad.append(f'{W}px {when}: tabs to the left, no sign of them')
            look('opening the shop')
            p.tap('#screen .tabs [data-act=tab][data-k=sig]'); look('after 招牌菜')
            p.tap('#screen .tabs [data-act=tab][data-k=home]'); look('after 家具與佈置')
        finally:
            p.close()
    check(not bad, '; '.join(bad[:8]))


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
            # (2026-10-10, round 2: d12a638's run failed with 1 pair — at one look a waiter on his way back to his place, in his
            #  short pause between jobs, was passing over another's place (scratchpad sweep in docs/evidence/cooking_2026-10-10/
            #  test_proofs/waiting_staff.txt: a passing pair on both builds' seeds, never two standing on one place). What the
            #  finding was about is two people *waiting* on one spot: both must be at the place they are going to.)
            n = p.ev("""(()=>{const W=Object.values(R.cw||{}).filter(w=>!w.task&&(w.room||'main')==='main'&&(w.tx==null||Math.hypot(w.x-w.tx,w.y-w.ty)<3));let n=0;
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
        # a heart is the pink shape drawn with curves (the table's bubble heart: two bezier lobes); the pink of a flower on
        # the table, a bow in a guest's hair or the season's decorations is drawn with arcs and lines and is not one
        p.ev("""(()=>{if(window.__hearts!=null)return;window.__hearts=0;const P=CanvasRenderingContext2D.prototype,f0=P.fill,b0=P.beginPath,z0=P.bezierCurveTo;
          P.beginPath=function(){this.__bz=false;return b0.apply(this,arguments)};P.bezierCurveTo=function(){this.__bz=true;return z0.apply(this,arguments)};
          P.fill=function(){if(this.__bz&&String(this.fillStyle).toLowerCase()==='#e8798a'&&this.canvas===sc)window.__hearts++;return f0.apply(this,arguments)}})()""")
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
    """WS1-03, WS7-02, N01 (fixed 2026-10-06): the album's last card 「今天。」 said 「1 隻貓都在」 — it counted the cats in
    the dining room at that moment. The five cats are always there (PROJECT_MEMORY §4): two of them in Jill's room
    while the card is read, it still says five."""
    p = Player(b, port, target, save=LATE)
    try:
        p.tap('#screen [data-act=open]')
        p.ev("for(const id of ['tora','mei'])homeCatIn(catBy(id))")
        p.tap('#screen [data-act=book]'); p.tap('#screen .tabs [data-act=btab][data-k=mem]')
        txt = p.text('#screen')
        m = re.search(r'(\d+) 隻貓都在', txt)
        check(m, 'no 「今天。」 card with the cats')
        check(m.group(1) == '5', f'the album says 「{m.group(0)}」')
    finally:
        p.close()


@test
def qa_photos_of_jills_room_are_taken_in_her_room(b, port, target):
    """WS7-01 (fixed 2026-10-06): 「膝上的重量」 (and the sofa's other pictures) showed the dining room — the photo was
    queued without its room, so the camera took whatever room was on screen. Jill on her sofa with a cat on her lap: the
    sofa's photos belong to Jill's room; Jill reading with two cats asleep in her room: 「各自安靜」 is hers too and names
    those two (not cats asleep in the dining room)."""
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
        rd = json.loads(p.ev("""JSON.stringify((()=>{MEMQ.length=0;const aa=albumAllows;albumAllows=()=>true;const L=LIFE.jill;L.act='read';L.sinceSit=13;
          for(const c of CATS){c.sofa=null;c.sofaOn=false}const two=['ban','snow'].map(catBy);for(const c of two){homeCatIn(c);c.homeSleep=true}
          for(const c of CATS.filter(c=>!two.includes(c))){c.away=null;c.hidden=false;c.homeSleep=false;c.st='sleep'}
          try{memChecks()}finally{albumAllows=aa}return MEMQ.filter(m=>m.id==='reading').map(m=>({room:m.room,cats:m.info.cats}))})())"""))
        check(rd, 'no 「各自安靜」 photo was queued with Jill reading and two cats asleep in her room')
        names = p.ev("JSON.stringify(['ban','snow'].map(id=>catName(CAT_DEF.find(c=>c.id===id))))")
        check(all(x['room'] == 'home' for x in rd), f'「各自安靜」 is queued for {rd}')
        check(all(set(x['cats'].split('、')) == set(json.loads(names)) for x in rd), f'「各自安靜」 names {rd}, not the cats asleep in her room {names}')
        # the player is looking at the dining room when it is taken: the picture is still of her room (drawn for the
        # camera), it is not lost, and the screen stays where the player was
        took = json.loads(p.ev("""JSON.stringify((()=>{room='main';const ds=drawScene;const drawn=[];drawScene=function(t){if(SNAP)drawn.push(room);return ds.apply(this,arguments)};
          const n0=albumList().length;try{flushMem()}finally{drawScene=ds}return{added:albumList().length-n0,drawn,room}})())"""))
        check(took['added'] >= 1 and took['drawn'] and set(took['drawn']) == {'home'} and took['room'] == 'main', f'taken while the dining room was on screen: {took}')
    finally:
        p.close()


# ---------------------------------------------------------------- words (known-open, objective ones only)

@test
def qa_a_favourite_is_missed_only_when_it_is_off_the_menu(b, port, target):
    """N02 (fixed 2026-10-06): a regular whose favourite IS on today's menu and in the fridge said 「香煎鴨胸今天沒有喔？那我
    看看別的。」 because the line looked at the order, not the menu (Sophie, Mia, 小林 in one week; the user, rc8.3:
    「Sophie連續兩天說沒有香煎鴨胸很白癡」) — and in the Lounge, whose list is the bar's, about the dinner dish. Every
    favourite the restaurant has: on the menu (and in the fridge) nobody says it is not on, in the Lounge nobody says it,
    taken off the menu it is said (the line still exists where it is true)."""
    p = Player(b, port, target, save=LATE)
    try:
        _to_service_from_late(p)
        out = json.loads(p.ev("""JSON.stringify((()=>{const out={on:[],off:[],lounge:[]};let cur='on';const q0=quote;quote=function(g,t,o){out[cur].push(t);return true};const r0=Math.random;Math.random=()=>0;
          const menu0=S.menu.slice();const w=Object.keys(WINES)[0];
          try{for(const id of Object.keys(LOVES)){const L=LOVES[id];const d=L.d;if(!S.unlocked.includes(d)||!S.menu.includes(d))continue;
            S.regulars[id]=Math.max(4,S.regulars[id]||0);S.stock[d]=Math.max(5,S.stock[d]||0);const g={reg:id,regs:[id],size:1,name:id};
            const other=menuList().find(x=>x!==d&&baseOf(x)!==d&&DISH(x).cat==='main')||menuList().find(x=>x!==d);
            const ask=(k,tk)=>{cur=k;S.loveMiss={};R.loveSaid=0;loveOrdered(g,tk)};
            ask('on',{items:[{d:other}]});ask('lounge',{lounge:1,items:[{d:w,lbar:1}]});
            S.menu=S.menu.filter(x=>x!==d&&baseOf(x)!==d);ask('off',{items:[{d:other}]});S.menu=menu0.slice()}}
          finally{quote=q0;Math.random=r0;S.menu=menu0}return out})())"""))
        menu_names = p.ev("menuList().map(dishName)")
        wrong = [t for t in out['on'] if '沒有' in t and any(n and n in t for n in menu_names)]
        check(out['off'], 'no favourite was ever missed, even off the menu (the test did not reach the line)')
        check(not wrong, f'said with the dish on the menu and in the fridge: {wrong[:3]}')
        check(not [t for t in out['lounge'] if '沒有' in t], f'said in the Lounge about the dinner dish: {out["lounge"][:3]}')
    finally:
        p.close()


@test
def qa_a_review_talks_about_the_food_not_the_glass(b, port, target):
    """WS6-06 (fixed 2026-10-06): a review named the glass as the dish — 「氣泡酒的火候剛剛好」「黑皮諾好吃，盤子乾淨得像沒用
    過」 (6–10 of the last 100 reviews in the user's Day 86–92 saves; mostly guests who only had a glass in the Lounge).
    A dinner with a glass and a dish: the review speaks of the dish. A Lounge guest with only a glass: no review line
    names the glass as food. The signature named 「Jill's …」 is never 「Jill 主廚的Jill's …」. No bench before it is bought."""
    p = Player(b, port, target, save=LATE)
    try:
        _to_service_from_late(p)
        out = json.loads(p.ev("""JSON.stringify((()=>{const w=Object.keys(WINES)[0];const food=menuList().find(d=>DISH(d)&&DISH(d).cat==='main'&&d!=='signature');const said=[],lg=[],sig=[];const r0=Math.random;
          for(let i=0;i<12;i++){const g={name:'T',size:2,type:'couple',cats:[],ticket:{items:[{d:w,st:'served',lbar:true},{d:food,st:'served'}]},table:null};
            const r=addReview(g,5);if(r)said.push(r.txt)}   /* the journal keeps 80: count what is returned, not the list's length */
          for(let i=0;i<20;i++){const g={name:'L',size:1,type:'couple',cats:[],lg:{why:'direct'},ticket:{lounge:1,items:[{d:w,st:'served',lbar:1}]},table:null};const r=addReview(g,4+(i%2));if(r)lg.push(r.txt)}
          const s0=S.signature;if(s0){for(let i=0;i<30;i++){Math.random=(()=>{let k=i*7+1;return()=>((k=k*48271%2147483647)/2147483647)})();const g={name:'S',size:1,type:'gourmet',cats:[],ticket:{items:[{d:'signature',st:'served'}]},table:null};const r=addReview(g,5);if(r)sig.push(r.txt)}Math.random=r0}
          const bench=extOn('bench');const ext0=S.ext.bench;S.ext.bench=0;const left=[];for(let i=0;i<60;i++){const g={name:'W',size:2,type:'couple',cats:[],ticket:null,table:null};const r=addReview(g,1,null,{left:true,wait:true});if(r)left.push(r.txt)}S.ext.bench=ext0;
          return {wine:dishName(w),food:dishName(food),said,lg,sig,left,signame:s0?dishName('signature'):null}})())"""))
        named = [t for t in out['said'] if out['wine'] in t]
        check(out['said'], 'no review was written')
        check(not named, f'the review names the glass ({out["wine"]}) as the dish: {named[:2]}')
        food_words = re.compile(r'好吃|火候|盤子|吃到最後一口|上桌|熱騰騰|擺盤|份量')
        lg_bad = [t for t in out['lg'] if out['wine'] in t and food_words.search(t)]
        check(not lg_bad, f'a Lounge guest\'s glass reviewed as food: {lg_bad[:2]}')
        check(not [t for t in out['sig'] if 'Jill 主廚的Jill' in t], f'「Jill 主廚的Jill\'s…」: {[t for t in out["sig"] if "Jill 主廚的Jill" in t][:1]}')
        check(not [t for t in out['left'] if '長椅' in t], f'a bench in a review with no bench bought: {[t for t in out["left"] if "長椅" in t][:1]}')
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
def qa_the_first_two_days_say_the_stock_fills_itself(b, port, target):
    """Audit WS5-10: on Day 1 the prep screen said 「沒有備料」 by every dish, the fridge 0/40 and 「一鍵補到建議量 $525」 with $500
    in the till, and 開始營業 stopped once with a red warning — while the first two days fill the stock themselves when the
    shop opens (startService → autoStock). The line that said so had stopped showing (feat().stock is always on). Now Day 1
    and 2 say it, warn about nothing and open on the first tap, the stock filled; from Day 3 an empty dish is warned about
    as before. By taps, on a phone."""
    p = Player(b, port, target)
    try:
        p.tap('[data-act=open]'); p.settle()
        check(p.state()['phase'] == 'prep' and p.ev("S.day") == 1, f'not at the Day 1 prep: {p.state()}')
        txt = p.text('#screen')
        check('前兩天開店時，Jill 會照建議量把每道菜的備料補好' in txt, 'Day 1: the prep screen says the stock fills itself')
        check('沒有備料' not in txt, 'Day 1: no 「沒有備料」 by the dishes')
        check(p.ev("menuList().every(d=>(S.stock[d]||0)===0)"), 'the fridge is empty before opening (the point of the line)')
        warn = p.start_day(confirm=False)
        check(warn is None and p.state()['phase'] == 'service', f'Day 1: 開始營業 opens on the first tap, no warning: {warn}')
        check(p.ev("menuList().every(d=>(S.stock[d]||0)>0)"), f'the stock was filled at opening: {p.ev("JSON.stringify(S.stock)")}')
        # Day 3: the player stocks; an empty dish is still worth one warning
        p.ev("phase='prep';R=null;S.day=3;S.phase='prep';for(const d of menuList())S.stock[d]=0;showPrep()"); p.settle()
        txt = p.text('#screen')
        check('沒有備料' in txt and '前兩天開店時' not in txt, 'Day 3: an empty dish says so, and the first-days line is gone')
        warn = p.start_day(confirm=False)
        check(warn and '沒有備料' in warn and p.state()['phase'] == 'prep', f'Day 3: the first tap warns: {warn}')
        check(not p.errors, p.errors[:3])
    finally:
        p.close()


@test
def qa_the_stock_rule_is_said_the_way_it_works(b, port, target):
    """Audit WS1-05 / README #7 (fixed 2026-10-07): what happens to a dish with nothing in the fridge was said four ways,
    and from Day 3 the start warning said the opposite of the game: 「沒有備料，客人點了要臨時叫貨（1.5 倍價、要等）」 —
    while from Day 3 such a dish cannot be ordered at all and nobody orders it for you (the audit's new player believed
    it, opened with an empty fridge and lost every table). The manual said 「客人點到沒貨的菜，Jill 也會自動叫貨」; the
    fridge said 「店不會自己花錢叫貨」 on Day 1, when Jill does. Day 1 and Day 3, by taps (the stock chip, 開始營業): the
    fridge panel, the start warning, the sold-out notice and the manual say what the game then does."""
    p = Player(b, port, target)
    try:
        p.tap('[data-act=open]'); p.settle()
        p.start_day(confirm=False)
        check(p.state()['phase'] == 'service', f'Day 1 did not open: {p.state()}')
        p.tap('#stockChip'); p.settle()
        note = p.text('#stockPanel')
        check('Jill 會自己臨時叫貨' in note and '店不會自己花錢叫貨' not in note, f'Day 1, the fridge panel: {note[-90:]}')
        d = p.ev("menuList()[0]")
        r = json.loads(p.ev(f"JSON.stringify((()=>{{const m00=S.money;S.stock['{d}']=0;S.money=500;const m0=S.money;const it={{d:'{d}'}};const ok=takeStock(it);const paid=m0-S.money;S.money=0;const it2={{d:'{d}'}};const ok2=takeStock(it2);S.money=m00;return{{ok,st:it.st,paid,ok2,st2:it2.st}}}})())"))
        check(r['ok'] and r['st'] == 'order' and r['paid'] > 0, f'Day 1: a dish with nothing left is ordered on the spot, as the panel says: {r}')
        check(not r['ok2'] and r['st2'] == 'cancel' and '錢夠的話' in note, f'Day 1 with an empty till: not ordered — and the panel says 「錢夠的話」: {r}')
        p.capture_on()
        p.ev("R.stockNote={};stockWatch()")
        sold = [c['t'] for c in p.captured() if c['k'].startswith('toast') and '賣完了' in c['t']]
        check(sold and all('錢夠的話 Jill 會臨時叫貨' in t for t in sold), f'Day 1, the sold-out notice: {sold[:1]}')
        # Day 3, before opening, a dish with nothing in the fridge
        p.ev("phase='prep';R=null;S.day=3;S.phase='prep';unlockDish('pasta');if(!S.menu.includes('pasta'))S.menu.push('pasta');const m=menuList();for(const x of m)S.stock[x]=30;S.stock.friedrice=0;showPrep()"); p.settle()
        warn = p.start_day(confirm=False)
        check(warn and '點不到' in warn and '1.5 倍價' not in warn and '要等' not in warn, f'Day 3, the start warning: {warn}')
        p.tap('[data-act=start]'); p.settle()
        check(p.state()['phase'] == 'service', f'the second tap did not open: {p.state()}')
        r = json.loads(p.ev("""JSON.stringify((()=>{const zero=menuList().filter(x=>(S.stock[x]||0)===0);const asked=new Set();
          const ty=Object.keys(TYPES);for(let i=0;i<80;i++){const g={type:ty[i%ty.length],size:1+i%4,name:'T',cats:[]};for(const x of orderItems(g))asked.add(x)}
          const m0=S.money;const it={d:zero[0]};const ok=takeStock(it);return{zero,asked:[...asked],ok,st:it.st,paid:m0-S.money}})())"""))
        check(r['asked'] and not set(r['asked']) & set(r['zero']), f'Day 3: a dish with nothing in the fridge was ordered: {set(r["asked"]) & set(r["zero"])} (asked {r["asked"][:6]}, empty {r["zero"]})')
        check(not r['ok'] and r['st'] == 'cancel' and r['paid'] == 0, f'Day 3: nobody orders it for you, nothing is paid: {r}')
        p.tap('#stockChip'); p.settle()
        note = p.text('#stockPanel')
        check('賣完的菜客人點不到' in note and 'Jill 會自己臨時叫貨' not in note, f'Day 3, the fridge panel: {note[-90:]}')
        p.ev("__cap.length=0;R.stockNote={};stockWatch()")
        sold = [c['t'] for c in p.captured() if c['k'].startswith('toast') and '賣完了' in c['t']]
        check(sold and all('點不到' in t and 'Jill 會臨時叫貨' not in t for t in sold), f'Day 3, the sold-out notice: {sold[:1]}')
        p.ev("showGuide()"); p.settle()
        p.page.locator('.gcard summary', has_text='營業中').first.click(); p.settle()   # the card a player opens
        guide = p.text('#screen')
        check('Jill 也會自動叫貨' not in guide and '賣完的菜客人點不到' in guide and '只有前兩天，錢夠的話' in guide, 'the manual says the rule as the game plays it')
        check(not p.errors, p.errors[:3])
    finally:
        p.close()


@test
def qa_no_text_copy_backup(b, port, target):
    """Audit WS2-14: 設定・存檔 had 「複製備份文字」, the button the user reported 2026-10-02 (「按複製直接當機 離開瀏覽器前一秒出現字
    再進去黑畫面」「不能用文字方式這樣只會當機」); PROJECT_MEMORY §10: 不要再用「文字框複製」做備份. Settings, opened by a tap:
    the file backup and its restore are there, no copy-text button; a text saved before can still be pasted back; the
    manual does not offer the text either."""
    p = Player(b, port, target)
    try:
        p.tap('[data-act=open]'); p.settle()
        p.tap('#hPause'); p.settle()
        txt = p.text('#screen')
        check(p.ev("sub") == 'settings', f'the settings did not open: {p.ev("sub")}')
        check('備份到檔案' in txt and '從備份檔恢復' in txt, 'the file backup is there')
        check('複製備份文字' not in txt and not p.ev("!!document.querySelector('[data-act=copyBackup]')"), 'no copy-text button')
        check(p.ev("!!document.querySelector('[data-act=pasteBackup]')"), 'a text saved before can still be pasted back')
        check('備份文字' not in p.ev("JSON.stringify(GUIDE)"), 'the manual does not offer a text backup')
    finally:
        p.close()


@test
def qa_the_second_burner_bought_on_day_two_is_paid_back(b, port, target):
    """Audit WS1-08: Day 2's shop sells the 2-burner stove for $900; on Day 3 the game gives every shop its second burner
    and said 「第二口爐子到貨！」 — the $900 was simply lost. Bought by a tap in Day 2's shop, it is paid back on Day 3 and
    the morning says so; a shop that did not buy it gets the burner as before, no money."""
    for buy in (True, False):
        p = Player(b, port, target)
        try:
            p.tap('[data-act=open]'); p.settle()
            p.ev("S.day=2;S.money=5000;S.phase='shop';showShop();shopTab='kitchen';showShop()"); p.settle()
            if buy:
                setup_check(p.ev("!!document.querySelector('#screen [data-act=buyEq][data-k=stove]')"), 'no stove upgrade in the Day 2 shop')
                p.tap('#screen [data-act=buyEq][data-k=stove]'); p.settle()
                check(p.ev("S.eq.stove") == 2 and p.ev("S.money") == 4100, f'bought: {p.ev("S.eq.stove")} {p.ev("S.money")}')
            m0 = p.ev("S.money")
            p.tap('#screen [data-act=nextDay]'); p.settle()
            check(p.ev("S.day") == 3 and p.ev("S.eq.stove") == 2, 'Day 3, two burners')
            news = p.ev("S.news.join(' ')")
            if buy:
                check(p.ev("S.money") == m0 + 900 and '那 $900 退回來了' in news, f'paid back: {p.ev("S.money")} vs {m0}; {news[:120]}')
            else:
                check(p.ev("S.money") == m0 and '退回來' not in news, f'nothing to pay back: {p.ev("S.money")} vs {m0}')
        finally:
            p.close()


@test
def qa_the_signature_editor_shows_the_menus_price(b, port, target):
    """Audit WS2-11: 「重新設計」 opened the editor on the dish as it is and said 「售價 $610」 while the shop and the menu said
    $940 — the editor showed the recipe's base, without its stars and the player's own price. The editor, opened by a tap
    on the player's late save, shows the price the menu charges for the same recipe."""
    p = Player(b, port, target, save=LATE)
    try:
        p.tap('#screen [data-act=open]'); p.settle()
        setup_check(p.ev("!!S.signature"), 'the save has no signature dish')
        if p.ev("phase") != 'shop':
            p.ev("showShop()"); p.settle()
        p.ev("shopTab='sig';showShop()"); p.settle()
        setup_check(p.ev("!!document.querySelector('#screen [data-act=sigOpen]')"), 'no 重新設計 in the shop')
        p.tap('#screen [data-act=sigOpen]'); p.settle()
        menu = p.ev("fmt(priceOf('signature'))")
        txt = p.text('#screen')
        check(f'售價 {menu}' in txt, f'the editor says the menu\'s price {menu}: {txt[:160]!r}')
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


# ---------------------------------------------------------------- the world and its people (audit 2026-10-06: fixed)

@test
def qa_who_is_still_there_at_closing(b, port, target):
    """N06: 「品酒師 Ken 和 Monsieur 杜 一起走了。」 at 21:21, then at closing 「打烊後，Ken 沒有走。…」 — the beat asked only
    whether he came today. Now a closing beat needs the person still there (here, or gone only after the doors closed and
    not with someone); on the samples night Ken stays till the doors close; on 予安's nights she stays till then too."""
    p = Player(b, port, target, save=LATE)
    try:
        _to_service_from_late(p)
        r = json.loads(p.ev("""JSON.stringify((()=>{const E=STORY_EV.find(e=>e.k==='ken_samples');factSet('ken_collab');delete story().facts.ken_samples;kenS().samples=S.day;
          const kq=kenQuiet,kn=kenNightToday;kenQuiet=()=>true;kenNightToday=()=>false;const out={};
          for(const g of R.groups.filter(g=>storyIdsOf(g).includes(KEN_ID)))R.groups.splice(R.groups.indexOf(g),1);
          namedHist(KEN).seen=S.day;R.leftAt={};R.leftAt[KEN_ID]={t:R.t,closed:false,together:true};R.leftTog={};R.leftTog[KEN_ID]=1;out.leftWithDu=E.when({});
          R.leftAt[KEN_ID]={t:R.t,closed:false,together:false};R.leftTog={};out.leftEarly=E.when({});
          R.leftAt[KEN_ID]={t:R.t,closed:true,together:false};out.stayedToClose=E.when({});
          const g={named:KEN,table:0,timer:0,size:1};const c0=R.closed;R.closed=false;out.lingers=storyLinger(g)&&g.timer>0;R.closed=true;out.leavesAtClose=!storyLinger({named:KEN,table:0,timer:0,size:1});R.closed=c0;
          kenQuiet=kq;kenNightToday=kn;
          const Y={g:{named:YA,size:1},on:1,t0:R.t,trial:0,done:0};R.ya=Y;const t0=R.t;R.t=R.dur*.95;R.closed=false;yaUpd(.05);out.yaAt95=!Y.done;R.closed=true;yaUpd(.05);out.yaAtClose=!!Y.done;R.t=t0;R.closed=c0;R.ya=null;
          return out})())"""))
        check(not r['leftWithDu'], 'the samples beat would play after Ken left with 杜')
        check(not r['leftEarly'], 'the samples beat would play after Ken left before closing')
        check(r['stayedToClose'], 'the samples beat would not play with Ken there to the end')
        check(r['lingers'] and r['leavesAtClose'], f'Ken does not stay till the doors close on the samples night: {r}')
        check(r['yaAt95'] and r['yaAtClose'], f'予安 leaves before the doors close on her night: {r}')
    finally:
        p.close()


@test
def qa_named_people_do_not_speak_a_strangers_lines(b, port, target):
    """N03: Dylan after fifteen signature dishes said 「這就是招牌菜？」; 周董 said 「把你們最好的端上來吧。」 a moment before his
    own 「隨便。」; Madame Lin's 「你選。」 was followed by her ordering 「氣泡酒，一杯。」. The serving lines and the VIP's order are
    a stranger's: Dylan, a regular, a named guest never say them; a stranger still does."""
    p = Player(b, port, target, save=LATE)
    try:
        _to_service_from_late(p)
        install_bot(p.g); p.ev(LAZY_ACTOR); p.ev("window.__act=window.__actLazy")
        for _ in range(240):   # until strangers sit with their orders
            if p.ev("R.groups.filter(g=>g.ticket&&g.table!=null&&!g.reg&&!namedId(g)&&g.ticket.items.length).length>=1"):
                break
            p.settle(); p.ev("for(let i=0;i<30;i++){__act();__tick(1000/30)}")
        r = json.loads(p.ev("""JSON.stringify((()=>{const said=[];const q0=quote0;quote0=function(g,t,o){said.push([g.__k,t]);return q0.apply(this,arguments)};const r0=Math.random;Math.random=()=>0;
          const ok=[];try{const base=R.groups.filter(g=>g.ticket&&g.table!=null&&!g.reg&&!namedId(g)&&g.ticket.items.length);if(base.length<1)return {err:'no anonymous seated group'};
           const mk=(k,f)=>{const g0=base[0];const g=Object.assign({},g0,{__k:k,servedTick:1,ticket:Object.assign({},g0.ticket,{items:g0.ticket.items.map(i=>Object.assign({},i,{st:'ready'}))})});f(g);return g};
           for(const [k,f] of [['dylan',g=>{g.reg='dylan'}],['regular',g=>{g.reg='sophie';g.regs=['sophie']}],['named',g=>{g.named='周董';g.type='vip'}],['stranger',g=>{}]]){
            const g=mk(k,f);R.cds={};R.saidT={};R.chatN=0;R.chatAt=null;S.chatSeen={};
            try{serveItems(g,g.ticket.items.map(it=>({it})))}catch(e){said.push([k,'ERR '+e.message])}
            if(k==='named'||k==='stranger'){const v=mk(k+'-order',g=>{f(g);g.type='vip';g.state='order';g.ticket=null});R.cds={};R.saidT={};try{createTicket(v)}catch(e){}}}}
          finally{quote0=q0;Math.random=r0}return {said}})())"""))
        check('err' not in r, r.get('err', ''))
        by = {}
        for k, t in r['said']:
            by.setdefault(k, []).append(t)
        strangers_lines = re.compile(r'這就是招牌菜|招牌菜長這樣|終於吃到了|專程來吃|這是 Jill 親手做的嗎|長這樣|就是這個|這個要拍一下|比照片還好看|跟一般的差在哪|招牌甜點|自己想的|留了肚子|拍一張再吃|我要那個|擺盤好美|把你們最好的|今天有什麼特別的|招牌的都上一份|不用看菜單|今天才有的|來了來了|看起來好好吃|份量剛好|聞起來好香|先拍照')
        for k in ('dylan', 'regular', 'named', 'named-order'):
            bad = [t for t in by.get(k, []) if strangers_lines.search(t)]
            check(not bad, f'{k} said a stranger’s line: {bad[:2]}')
        check(any(strangers_lines.search(t) for t in by.get('stranger', []) + by.get('stranger-order', [])), f'a stranger no longer says them either: {by}')
    finally:
        p.close()


@test
def qa_after_the_reveal_dylan_is_not_a_stranger(b, port, target):
    """N07: Day 95 (26 days after the reveal) Mia: 「那個人跟老闆娘很熟的樣子。」; the user's Day 72 save, 小林: 「那位先生又
    來了。」. After the reveal no regular notices him as a stranger and no clue is counted; before it they still do."""
    p = Player(b, port, target, save=LATE_CP)
    try:
        p.tap('#screen [data-act=open]'); p.frames(10)
        r = json.loads(p.ev("""JSON.stringify((()=>{const said=[];const q0=quote;quote=function(g,t,o){if(g&&g.id===9002)said.push(t);return q0.apply(this,arguments)};const r0=Math.random;Math.random=()=>0;
          const tb=R.tables.find(t=>!t.group)||R.tables[0];const dg={id:9001,reg:'dylan',table:tb.i,state:'eat',size:1,looks:[],x:tb.x,y:tb.y};R.groups.push(dg);
          const reg=Object.keys(S.regulars).find(k=>k!=='dylan'&&!(REG_BY[k]&&REG_BY[k].pair)&&(S.regulars[k]||0)>=4);const g={id:9002,reg,regs:[reg],table:tb.i,size:1,state:'reading'};
          const out={reg};try{for(const stage of [S.dylan.stage,2]){S.dylan.stage=stage;const n0=S.dylan.clues.noticed||0;const s0=said.length;for(let i=0;i<20;i++){S.dylan.noticedDay=-9;regularsNoticeDylan(g);__tick(2500)}out['stage'+stage]={clues:(S.dylan.clues.noticed||0)-n0,lines:said.length-s0}}}
          finally{quote=q0;Math.random=r0;R.groups.splice(R.groups.indexOf(dg),1)}return out})())"""))
        after = [v for k, v in r.items() if k.startswith('stage') and k != 'stage2']
        check(after and after[0]['clues'] == 0 and after[0]['lines'] == 0, f'after the reveal a regular still notices him as a stranger: {r}')
        check(r['stage2']['clues'] > 0, f'before the reveal (control) nobody notices him: {r}')
    finally:
        p.close()


@test
def qa_the_days_text_matches_the_day(b, port, target):
    """N13, WS2-07, N16, WS1-11, WS1-12: Day 90's 「店慶」 said 「開店滿十天的日子」; Valentine's morning said 「今天今天是情人
    節。」; a VIP booking's morning said 「今天沒什麼特別的」; a new game's summary and journal said 「擴建到 Jill's Bistro 的
    門檻 0.0」; the first tutorial card sat guests on a bench Day 1 does not have."""
    p = Player(b, port, target)
    try:
        r = json.loads(p.ev("""JSON.stringify((()=>{const out={};out.cel=EVENTS.celebrate.d;const d0=S.stats.days;S.stats.days=89;out.cel90=EVENTS.celebrate.d;S.stats.days=d0;
          out.names=Object.values(EVENTS).map(E=>E.n);const T0=S.today;const m=[];for(const ev of ['valentine','vip','celebrate']){for(const w of ['cloud','sun']){S.today=Object.assign({},T0||{},{weather:w,event:ev,day:S.day});for(let i=0;i<20;i++)m.push(morningLine())}}S.today=T0;out.morning=m;
          out.coach=(typeof COACH!=='undefined'?COACH:[]).map(c=>typeof c==='string'?c:JSON.stringify(c)).join('|');return out})())"""))
        check('十天' not in r['cel90'] and '90' in r['cel90'], f'Day 90’s anniversary reads: {r["cel90"]}')
        check(not [n for n in r['names'] if n.startswith('今天')], f'an event named 「今天…」: {[n for n in r["names"] if n.startswith("今天")]}')
        check(not [t for t in r['morning'] if '今天今天' in t or '沒什麼特別' in t or '普通的一天' in t], f'mornings with an event: {[t for t in r["morning"] if "今天今天" in t or "沒什麼特別" in t][:2]}')
        check(all(any(n in t for n in ('情人節', 'VIP', '店慶')) for t in r['morning']), 'a morning with an event does not say it')
        check('長椅' not in r['coach'], 'the first tutorial card sits guests on a bench Day 1 does not have')
        p.tap('[data-act=open]'); p.settle(); p.ev("autoStock()"); p.start_day()
        install_bot(p.g); p.ev("__bot(60000,1/30)"); p.ev("while(DLG)dlgNext()")
        check(not re.search(r'(門檻|需要) 0\.0', p.text('#screen')), 'the Day 1 summary shows a 0.0 rating gate')
    finally:
        p.close()


@test
def qa_continuing_the_day_does_not_replay_its_opening(b, port, target):
    """N16 (WS2-01's save): 繼續營業 at 22:08 fell back to reopening the room (the table count had changed) and replayed the
    evening's start — 「那天下午…」, 「OPEN FOR DINNER」 — and then 「RUSH HOUR 晚餐尖峰時段開始！」 at 22:08."""
    p = Player(b, port, target, save='player_day68_1033.json')
    try:
        p.capture_on()
        p.tap('#screen [data-act=open]'); p.frames(60)
        caps = p.captured()
        banners = [c['t'] for c in caps if c['k'] == 'banner']
        check(not [t for t in banners if 'RUSH' in t or 'OPEN FOR DINNER' in t], f'banners after 繼續營業: {banners}')
        check(p.state()['phase'] == 'service', f'not back in the service: {p.state()}')
    finally:
        p.close()


@test
def qa_regulars_do_not_repeat_a_line_within_the_week(b, port, target):
    """N14: 小林's 「今天加班，還好還開著。」 four times in seven days (rc8.5 had promised a regular says the same line at most
    once a week; the rule lived only in the order's line). Every regular's everyday line goes through the same week."""
    p = Player(b, port, target, save=LATE)
    try:
        _to_service_from_late(p)
        r = json.loads(p.ev("""JSON.stringify((()=>{const said=[];const q0=quote;quote=function(g,t,o){said.push([S.day,t]);return true};const d0=S.day;const g=R.groups.find(x=>x.reg)||{reg:'koba',regs:['koba']};
          try{for(const d of [d0,d0+2,d0+4,d0+8]){S.day=d;regSay(g,'今天加班，還好還開著。')}}finally{quote=q0;S.day=d0}return said})())"""))
        days = [d for d, t in r]
        check(len(days) == 2 and days[1] - days[0] >= 7, f'said on days {days} (at most once a week)')
    finally:
        p.close()


@test
def qa_the_summarys_tomorrow_matches_the_shop(b, port, target):
    """WS1-09: the summary's 「明天：…」 said decor and expansion, the staff and the signature dish a day after the shop
    already had them. Each is announced for the evening its tab opens."""
    p = Player(b, port, target)
    try:
        r = json.loads(p.ev("""JSON.stringify((()=>{const out=[];const d0=S.day,p0=S.phase,ph0=phase;try{for(let K=2;K<=9;K++){const note=nextDayNote(K);S.day=K;S.phase='shop';phase='shop';const on=shopTabs().filter(t=>t.on).map(t=>t.k);
          out.push({K,note,on})}}finally{S.day=d0;S.phase=p0;phase=ph0}return out})())"""))
        first = {}
        for x in r:
            for k in x['on']:
                first.setdefault(k, x['K'])
        notes = {x['K']: x['note'] for x in r}
        where = {'員工': 'staff', '招牌菜': 'sig'}
        for word, tab in where.items():
            k = next((K for K, n in notes.items() if word in n), None)
            check(k == first.get(tab), f'「{word}」 is announced for Day {k} but its tab opens on evening {first.get(tab)}')
    finally:
        p.close()


# ---------------------------------------------------------------- one exchange at a time (audit 2026-10-06: fixed)

def _said_order(p, js_setup, seconds=14, read_panels=False):
    """run the setup in a service, let the room go on for a while (reading any panel like a player), and return every
    line shown, in order, with whether a story panel was open at that moment"""
    p.ev("""(()=>{window.__said=[];const l0=logLine;window.__l0=l0;logLine=function(w,t,k){__said.push({t:String(t),dlg:!!DLG});return l0.apply(this,arguments)}})()""")
    p.ev(js_setup)
    for _ in range(int(seconds)):
        if read_panels and p.ev("!!DLG"):
            p.read_dialog()
        p.frames(30)
    out = json.loads(p.ev("JSON.stringify(window.__said)"))
    p.ev("logLine=window.__l0")
    return out


@test
def qa_one_exchange_at_a_time(b, port, target):
    """N04, N16: exchanges overlapped and a question was answered by someone else's line (「Mia，今天想吃什麼？」 →
    「第二層左邊。」); the narration 「阿珠姐 連頭都沒回。」 came before Jill's question. Two exchanges set going at the same
    moment are said one after the other, each question followed by its own answer."""
    p = Player(b, port, target, save=LATE)
    try:
        _to_service_from_late(p)
        p.ev("window.__noScenes=true")   # the room's own lines, no panels in this one
        said = _said_order(p, """(()=>{shStart('t_one',false,null,()=>{JILL_SAY('問一？',400);later(()=>noteLine('答一。'),1600)});
            shStart('t_two',false,null,()=>{JILL_SAY('問二？',300);later(()=>noteLine('答二。'),1500)})})()""")
        seq = [x['t'] for x in said if re.search(r'[問答][一二]', x['t'])]
        check(seq == ['問一？', '答一。', '問二？', '答二。'], f'the two exchanges came out as {seq}')
        said = _said_order(p, """(()=>{const vet=veteranCook();if(!vet){window.__novet=1;return}const E=STORY_EV.find(e=>e.k==='veteran_knows');shStart('veteran_knows',false,null,()=>E.run({}))})()""", seconds=6)
        if not p.ev("!!window.__novet"):
            seq = [x['t'] for x in said]
            q = next((i for i, t in enumerate(seq) if t in ('那個⋯⋯放哪？', '鹽呢？')), None)
            n = next((i for i, t in enumerate(seq) if '連頭都沒回' in t), None)
            check(q is not None and n is not None and n > q, f'the veteran’s narration before the question: {seq}')
    finally:
        p.close()


@test
def qa_room_lines_wait_for_the_story_panel(b, port, target):
    """W3-02: a story's panel holds the restaurant, but the room's lines went on underneath on the wall clock — Ken and 杜's
    「這支太甜了。」 was said under the photo and gone when it closed. The room's exchanges wait with the rest of the room."""
    p = Player(b, port, target, save=LATE)
    try:
        _to_service_from_late(p)
        p.ev("window.__noScenes=false;window.__holds=true")
        said = _said_order(p, """(()=>{shStart('kd_photo',true,null,()=>{noteLine('面板一。');noteLine('面板二。')});
            JILL_SAY('房間裡的話。',700);later(()=>noteLine('房間裡的回答。'),1900)})()""", seconds=8)
        under = [x['t'] for x in said if x['dlg'] and '房間裡' in x['t']]
        check(not under, f'room lines said under the story panel: {under}')
        p.read_dialog(); p.frames(30 * 6)
        after = json.loads(p.ev("JSON.stringify(window.__said?__said.map(x=>x.t):[])"))
        log = p.ev("JSON.stringify((R.log||[]).map(x=>x.t))")
        check('房間裡的話。' in log and '房間裡的回答。' in log, f'the room’s lines were lost, not kept for after the panel: {log[-300:]}')
    finally:
        p.close()


@test
def qa_two_stories_do_not_share_a_panel(b, port, target):
    """N10: two stories due together read as one panel — the second opened in the same tap that closed the first
    (《多的。》's last line, then 「樓上真的一直都空著喔？」). After the first closes the room is seen for a moment."""
    p = Player(b, port, target, save=LATE)
    try:
        _to_service_from_late(p)
        p.ev("window.__noScenes=false;window.__holds=true")
        p.ev("shStart('t_first',true,null,()=>{noteLine('甲一。');noteLine('甲二。')});shStart('t_second',true,null,()=>{noteLine('乙一。')})")
        check(p.ev("!!DLG&&DLG.sh&&DLG.sh.k==='t_first'"), 'the first story is not on screen')
        for _ in range(10):
            if not p.ev("!!DLG&&DLG.sh&&DLG.sh.k==='t_first'"):
                break
            p.frames(12); p.tap('#dlg'); p.frames(1)
        check(not p.ev("!!DLG"), 'the second story opened in the same tap that closed the first')
        p.frames(30 * 3)
        check(p.ev("!!DLG&&DLG.sh&&DLG.sh.k==='t_second'"), 'the second story never came')
    finally:
        p.close()


@test
def qa_a_story_photo_comes_after_its_lines(b, port, target):
    """N10: the album's 「還是沒有同意」 came before the words it records (the photo was taken when the beat began, its lines
    still on their way). PROJECT_MEMORY §9: 事件還沒發生不能先有照片."""
    p = Player(b, port, target, save=LATE)
    try:
        _to_service_from_late(p)
        p.ev("window.__noScenes=false;window.__holds=true")
        key = p.ev("Object.keys(STORY_PHOTOS).find(k=>!story().photos[k]&&(STORY_PHOTOS[k].art||STORY_PHOTOS[k].stage))||''")
        check(key, 'every story photo is already in this album')
        p.ev(f"shStart('kd_photo',true,null,()=>{{JILL_SAY('先說的一句。',700);JILL_SAY('後說的一句。',2200);storyPhoto('{key}',{{}})}})")
        lines = p.read_dialog()
        i_last = next((i for i, l in enumerate(lines) if '後說的一句' in l), None)
        i_photo = next((i for i, l in enumerate(lines) if '相簿' in l), None)
        check(i_last is not None and i_photo is not None, f'the panel read {lines}')
        check(i_photo > i_last, f'the photo came before the lines it records: {lines}')
    finally:
        p.close()


@test
def qa_a_long_scene_is_kept_whole_on_its_page(b, port, target):
    """N08 (fixed 2026-10-06; its test 2026-10-07): a written scene longer than twelve lines lost its end on the story
    page — 《那面牆》's mediation (21 lines) stopped at 「金額的部分呢？」, so 「我接受。」 was never on it. The cap is for the
    chatter a beat's timers bring, not for the scene's own lines. In a service, the mediation read through by taps: every
    line of it is on its page."""
    p = Player(b, port, target, save=MID, checkpoint=False)
    try:
        _to_service_from_late(p)
        p.ev("""(()=>{const st=story();delete st.ev.wall_mediation;if(st.facts)delete st.facts.wall_mediation;if(st.beatLines)delete st.beatLines.wall_mediation;
          const E=STORY_EV.find(e=>e.k==='wall_mediation');shStart('wall_mediation',shAuthored(E),null,()=>E.run({}),true)})()""")
        read = p.read_dialog()
        kept = [x['t'] for x in json.loads(p.ev("JSON.stringify((story().beatLines||{}).wall_mediation||[])"))]
        check(len(read) >= 21, f'the mediation was not shown whole: {len(read)} lines read')
        check(len(kept) >= 21 and '我接受。' in kept and kept[20] == '嗯。剩下的是修牆。', f'its page keeps {len(kept)} lines, the last 「{kept[-1] if kept else ""}」')
        check(not p.errors, p.errors[:3])
    finally:
        p.close()


@test
def qa_a_late_save_reads_true(b, port, target):
    """The user's Day 92 save as a player opens it (2026-10-07; the fixes are of 2026-10-06, the old-page repair of 10-07):
    - N08 / WS9-01: story pages cut part-way through a written scene before the fix are whole again — 《那面牆》's
      mediation (12 of 21 lines, ending 「金額的部分呢？」), the photos of the wall (6 lines, ending 「可以放大嗎？」); a
      second load changes nothing more.
    - N15: no 「Ken 的品酒夜」 / 「品酒夜」 on the pages (the nights are 品酒之夜); 「妳不是在問炸物？」 is credited to the cook
      who said it (阿德師傅), not Hugo.
    - N05: a story notice and the summary's stories name the story (「X 的故事」) and show each beat's title as written:
      not 「Madame Lin「妳真的不賣酒？」」 (Ken's words under her name), not a description put in quotes.
    - W3-16: a week of one day reads 「DAY 92」, not 「DAY 92–92」.
    - WS2-08: the Lounge's snacks news no longer says 「每道新菜的第一份還是 Jill 親自做」 (rc8 retired that rule).
    - W3-13: the next morning's line is filed under the new day, as 開店前 — not in the day before as 打烊後."""
    p = Player(b, port, target, save=LATE)
    try:
        pages = json.loads(p.ev("JSON.stringify(story().beatLines)"))
        med = [x['t'] for x in pages.get('wall_mediation', [])]
        ph = [x['t'] for x in pages.get('wall_photos', [])]
        check(len(med) == 21 and med[11] == '金額的部分呢？' and med[-1] == '嗯。剩下的是修牆。' and '我接受。' in med, f'N08: the mediation page has {len(med)} lines, ending 「{med[-1] if med else ""}」')
        check(len(ph) > 6 and ph[5] == '可以放大嗎？' and '差很多。' in ph, f'N08: the photos of the wall have {len(ph)} lines, ending 「{ph[-1] if ph else ""}」')
        p.reload(background=False)
        again = json.loads(p.ev("JSON.stringify(story().beatLines)"))
        check(again == pages, 'N08: a second load changed the pages again')
        p.tap('#screen [data-act=open]'); p.settle()
        p.ev("showBook()"); p.settle()
        p.tap('[data-act=btab][data-k=story]'); p.settle()
        story_txt = p.ev("storyPageHTML()")
        check('Ken 的品酒夜' not in story_txt and not re.search(r'(?<!之)品酒夜', story_txt), 'N15: the pages still say 「品酒夜」')
        check('阿德師傅：「妳不是在問炸物？」' in story_txt and 'Hugo：「妳不是在問炸物？」' not in story_txt, 'N15: 「妳不是在問炸物？」 is not credited to the cook who said it')
        bad = json.loads(p.ev("""JSON.stringify((()=>{const bad=[];for(const L of STORY_LINES){let P=null;try{if(!L.open())continue;P=lineProgress(L)}catch(e){continue}
            for(const x of P.done.slice(0,3)){storyNoteShow.pending=null;storyNoteShow({k:L.k,who:lineWho(L),t:x.t,n:1,total:2});const el=document.querySelector('#storyNote');
              const b=el.querySelector('b').textContent,s=(el.querySelector('span')||{}).textContent||'';if(!/的故事$/.test(b)||s!==String(x.t))bad.push(b+' | '+s+' | '+x.t)}}
            for(let D=S.day;D>S.day-8;D--){const box=document.createElement('div');box.innerHTML=storyTodayHTML(D);for(const r of box.querySelectorAll('.st-row')){if(String(r.dataset.k).startsWith('ch'))continue;
              const b=r.querySelector('b').textContent;if(!/的故事$/.test(b))bad.push('summary: '+b)}}return bad})())"""))
        check(not bad, f'N05: a story named as its speaker, or a title not as written: {bad[:3]}')
        p.ev("clearTimeout(storyNoteShow.t);document.querySelector('#storyNote').hidden=true")   # the notices this check showed
        p.tap('[data-act=btab][data-k=mem]'); p.settle()
        album = p.text('#screen')
        same = [m.group(0) for m in re.finditer(r'DAY (\d+)–(\d+)', album) if m.group(1) == m.group(2)]
        check('DAY ' in album and not same, f'W3-16: {same[:2]}')
        news = p.ev("(()=>{S.unlocked=S.unlocked.filter(d=>d!==barDishes()[0]);S.news=[];barMenuMig();return S.news.join(' ')})()")
        check('小點' in news and '親自做' not in news, f'WS2-08: {news[:120]}')
        p.ev("S.news=[]")
        p.tap('[data-act=closeSub]'); p.settle()
        # W3-13: to the next day; the morning's line, read like a player, is filed under that day
        n_before = p.ev("(S.dayLog||[]).length")
        p.tap('#screen [data-act=nextDay]')
        morning = p.settle()
        r = json.loads(p.ev("JSON.stringify({day:S.day,n:(S.dayLog||[]).length,pre:S.preLog})"))
        check(morning, 'W3-13: no morning line at the prep (the test did not reach the case)')
        check(r['n'] == n_before, f'W3-13: the morning went into the day before ({r["n"] - n_before} lines)')
        pre = (r['pre'] or {}).get('L') or []
        check(r['pre'] and r['pre']['d'] == r['day'] and pre and all(x['c'] == '開店前' for x in pre), f'W3-13: the morning is not kept as 開店前 of Day {r["day"]}: {r["pre"]}')
        p.restock(); p.start_day()
        first = json.loads(p.ev(f"JSON.stringify(R.log.slice(0,{len(pre)}))"))
        check([x['t'] for x in first] == [x['t'] for x in pre], f'W3-13: the day\'s log does not begin with its morning: {first[:2]}')
        check(not p.errors, p.errors[:3])
    finally:
        p.close()


@test
def qa_a_chapter_is_listed_only_where_it_is_shown(b, port, target):
    """N09 (fixed 2026-10-06; its test 2026-10-07): a new game's Day 5 summary listed 「晚餐之後」 (two lines) while the
    story page did not show that chapter yet, and the page numbered its chapters by their place in the list
    (CHAPTER 2, then CHAPTER 4). One rule now decides whether a chapter is shown, everywhere; chapters are numbered
    as shown. 「晚餐之後」 has no rule of its own any more (the user, 2026-10-07: no hidden level-4 gate), so the case is
    「樓上」: 房東的二樓 (up_inspect) comes before the chapter shows (with the cats upstairs, up_cats). A new game with that
    beat today: the chapter is not in the summary and the numbers have no gap; once it shows it is in both."""
    p = Player(b, port, target)
    try:
        p.tap('[data-act=open]'); p.settle()
        q = """JSON.stringify((()=>{const page=storyPageHTML();return{today:storyToday(S.day).map(x=>x.who),nums:[...page.matchAll(/CHAPTER (\\d+)/g)].map(m=>+m[1]),
          hidden:restChapters().filter(C=>C.showIf&&!C.showIf()).map(C=>C.t),onPage:page.includes('<b>樓上</b>')}})())"""
        p.ev("factSet('up_inspect')")
        r = json.loads(p.ev(q))
        check('樓上' in r['hidden'], f'setup: 樓上 should not be shown before the cats upstairs: {r}')
        check('樓上' not in r['today'] and not r['onPage'], f'the summary lists a chapter the page does not show: {r["today"]}')
        check(r['nums'] == list(range(1, len(r['nums']) + 1)), f'the chapters are numbered with a gap: {r["nums"]}')
        p.ev("factSet('up_cats')")
        r = json.loads(p.ev(q))
        check('樓上' in r['today'] and r['onPage'], f'once 樓上 shows, the chapter is on the page and in the summary: {r}')
        check(r['nums'] == list(range(1, len(r['nums']) + 1)), f'the chapters are numbered with a gap: {r["nums"]}')
        check(not p.errors, p.errors[:3])
    finally:
        p.close()


@test
def qa_lines_with_a_face_do_not_cover_toasts(b, port, target):
    """WS1-10, W3-10: a line with a face covered the toasts — on Day 1's first photo the husband's 「拍妳。」「嗯。」 were
    under Jill's lines; with two toasts the upper one was covered. At 390 and 375, with and without the tutorial card,
    no face line lies on a toast."""
    OVER = """(()=>{const T=[...document.querySelectorAll('#toasts .toast')].filter(e=>e.offsetParent!==null||getComputedStyle(e).position==='fixed').map(e=>e.getBoundingClientRect());
      const P=[...document.querySelectorAll('#plines .pline')].map(e=>e.getBoundingClientRect());return T.length>0&&P.length>0&&T.some(a=>P.some(q=>a.left<q.right&&q.left<a.right&&a.top<q.bottom&&q.top<a.bottom))})()"""
    bad = []
    for W in (390, 375):
        p = Player(b, port, target, save=LATE, W=W)
        try:
            _to_service_from_late(p)
            p.ev("toast('<b>甲</b>：「一句話」','q');toast('<b>乙</b>：「另一句話，長一點的那種」','q');portraitLine('jill','丙。',{})"); p.frames(3)
            if p.ev(OVER):
                bad.append(f'{W}px')
        finally:
            p.close()
        p = Player(b, port, target, W=W)
        try:
            p.tap('[data-act=open]'); p.settle(); p.start_day(); p.frames(30)
            p.ev("toast('<b>Jill 先生</b>：「拍妳。」','q');portraitLine('jill','我根本沒在看。',{})"); p.frames(3)
            if p.ev(OVER):
                coach = 'up' if p.ev("!document.querySelector('#coach').hidden") else 'down'
                bad.append(f'{W}px Day 1 (tutorial card {coach})')
        finally:
            p.close()
    check(not bad, f'a face line lies on a toast at {bad}')


@test
def qa_a_story_waiting_its_turn_is_not_done_yet(b, port, target):
    """N04 follow-up (2026-10-06): a story beat chosen while an exchange is being said waits for its turn — and until it
    has been said it is not done. Before, it was marked done when chosen: Sophie × 寶寶's 「今天那隻呢？」 then counted her
    visits from zero, and the next beat (寶寶 at her table, two visits later) could come the same evening; a beat whose
    turn never came (the app closed) was lost. And a picture taken in the room waits for its beat's lines (N10)."""
    import v23_tests as v23
    g = _rt.Game(b, port, target, seed=39, manual=True, viewport={'width': 390, 'height': 844})
    try:
        v23.load_fixture(g, 'player_day39.json'); g.click('[data-act=openFresh]'); g.page.wait_for_timeout(120)
        g.ev("S.money+=20000;autoStock()"); _rt.start_day(g); g.ev("for(let i=0;i<3;i++)__tick(1000/30)")
        g.ev("Object.assign(evState('sophie_mei_1'),{n:1,d:S.day-6,last:S.day-6,v:(S.regulars.sophie||0)-3})")   # beat 1, three visits ago
        g.ev("R.groups.slice().forEach(q=>leaveGroup(q,'ok'));R.groups.length=0;for(const t of R.tables){t.group=null;t.dirty=false}")
        g.ev("talk(()=>{JILL_SAY('湯好了。',300);JILL_SAY('誰要先？',2600)})")   # an exchange being said when she sits down
        ti = g.ev(v23.SEAT_SOPHIE)
        setup_check(ti is not None, 'Sophie seated')
        st = g.ev("({chosen:story().trace.slice(-1)[0].k,done:evDone('sophie_mei_2'),since:sophieVisitsSince('sophie_mei_2')})")
        setup_check(st['chosen'] == 'sophie_mei_2', f'「今天那隻呢？」 was not chosen: {st}')
        check(not st['done'] and st['since'] == -1, f'「今天那隻呢？」 waits its turn and is not done yet: {st}')
        # 寶寶 comes to her table and looks while it waits: the next beat must not come
        g.ev("(()=>{const c=catBy('mei');const t=R.tables[%d];c.hidden=false;c.perch=-1;c.sofa=null;c.st='rest';c.x=t.x+30;c.y=t.y+14})()" % ti)
        g.ev("catEv(R.groups.find(q=>q.reg==='sophie'),'look',catBy('mei'))")
        check(not g.ev("evDone('sophie_mei_3')"), 'the next beat came while the one before it was still waiting')
        g.ev("__talkFor(12)")
        done = g.ev("({done:evDone('sophie_mei_2'),since:sophieVisitsSince('sophie_mei_2'),said:(R.log||[]).some(l=>/今天那隻呢/.test(l.t))})")
        check(done['done'] and done['since'] == 0 and done['said'], f'after the exchange, her question — and her visits counted from now: {done}')
        g.ev("catEv(R.groups.find(q=>q.reg==='sophie'),'look',catBy('mei'))")
        check(not g.ev("evDone('sophie_mei_3')"), 'the next beat came on the same evening')
        # the app closes while a beat waits its turn: it is not lost
        g.ev("R.groups.slice().forEach(q=>leaveGroup(q,'ok'));R.groups.length=0;for(const t of R.tables){t.group=null;t.dirty=false}")
        g.ev("Object.assign(evState('sophie_mei_2'),{n:0,miss:0});for(const k of ['v','last','d'])delete evState('sophie_mei_2')[k];delete storyDay().seen.sophie_mei_2;storyDay().minor=0;storyDay().lp={};(()=>{const c=catBy('mei');c.x=40;c.y=FB-12})()")
        g.ev("talk(()=>{JILL_SAY('湯好了。',300);JILL_SAY('誰要先？',2600)})"); g.ev(v23.SEAT_SOPHIE)
        setup_check(g.ev("story().trace.slice(-1)[0].k==='sophie_mei_2'&&story().trace.length>1"), 'the beat was not chosen this time: ' + g.ev("JSON.stringify({s2:evState('sophie_mei_2'),day:storyDay(),trace:story().trace.slice(-3)})"))
        g.ev("checkpointSave('hidden')"); g.reload()
        check(g.ev("evState('sophie_mei_2').n") == 0, 'a beat whose turn never came was saved as done (lost)')
        # a picture taken in the room comes after its beat's lines
        g.ev("startService({resume:true})")
        key = g.ev("Object.keys(STORY_PHOTOS).find(k=>!story().photos[k]&&(STORY_PHOTOS[k].art||STORY_PHOTOS[k].stage))||''")
        setup_check(key, 'every story photo is already in this album')
        g.ev("window.__fastSay=0;R.floorUntil=null")
        g.ev(f"shStart('qa_room_photo',false,null,()=>{{JILL_SAY('先說的一句。',700);JILL_SAY('後說的一句。',2200);storyPhoto('{key}',{{}})}})")
        check(not g.ev(f"!!story().photos['{key}']"), 'the picture was taken before its lines were said')
        g.ev("__talkFor(10)")
        check(g.ev(f"!!story().photos['{key}']") and g.ev("(R.log||[]).some(l=>/後說的一句/.test(l.t))"), 'the lines, then the picture')
        check(not g.errors, f'page errors: {g.errors[:3]}')
    finally:
        g.close()


@test
def qa_the_savings_goals_are_in_tonights_shop(b, port, target):
    """WS1-07: the summary's 「存錢的目標」 said 「現在就買得起」 about what the shop did not sell yet — Day 1 the 咖啡機 under
    a grey 廚房設備 tab, Day 2 the 門口花箱 (the street pieces come on Day 3), Day 3 the 擴建 (「第 4 天打烊後開放擴建」).
    For the first nine evenings of a new game, every goal is on a tab that is open that evening, and the tab, opened,
    shows it with a price to press."""
    p = Player(b, port, target)
    try:
        bad = []
        for K in range(1, 10):
            p.ev(f"S.day={K};S.phase='summary';phase='summary';S.money=Math.max(S.money,6000)")
            goals = json.loads(p.ev("JSON.stringify(goalLadder().map(g=>({n:g.n,where:g.where,left:g.left})))"))
            tabs = {t['n']: t for t in json.loads(p.ev("JSON.stringify(shopTabs())"))}
            for gl in goals:
                t = tabs.get(gl['where'])
                if not t or not t['on']:
                    bad.append(f"Day {K}: 「{gl['n']}」 on 「{gl['where']}」, a tab not open that evening"); continue
                p.ev(f"S.phase='shop';phase='shop';shopTab={json.dumps(t['k'])};showShop()")
                name = re.sub(r' LV\d+$', '', gl['n']).split('：')[-1]
                shown = p.ev(f"""(()=>{{const sc=document.querySelector('#screen');for(const it of sc.querySelectorAll('.item')){{const nm=(it.querySelector('.nm')||{{}}).textContent||'';if(nm.includes({json.dumps(name)})&&it.querySelector('[data-act]:not([disabled])'))return true}}return false}})()""")
                if not shown:
                    bad.append(f"Day {K}: 「{gl['n']}」 is not for sale on 「{gl['where']}」 that evening")
                p.ev("S.phase='summary';phase='summary';hideScreen()")
        check(not bad, '; '.join(bad[:8]))
        # and a grey tab, tapped, says when it opens (it did nothing): Day 1's evening, 店舖工程
        p.ev("S.day=1;S.phase='shop';phase='shop';shopTab='home';showShop()")
        p.tap('#screen .tabs [data-act=tab][data-k=works]')
        msg = p.ev("[...document.querySelectorAll('#toasts .toast')].map(e=>e.textContent).join(' ')")
        check('第 3 天' in msg and p.ev("shopTab") == 'home', f'the grey 店舖工程, tapped, said {msg!r} (the shop on {p.ev("shopTab")})')
    finally:
        p.close()


@test
def qa_a_guest_who_moves_to_the_lounge_is_counted_once(b, port, target):
    """Found while reading the Lounge's books (2026-10-06): a party that has dinner and then goes to The Lounge for a
    glass paid twice, as it should (dinner, then the tab) — but was also counted twice as guests, so the summary's
    客人數 (and the lifetime count) grew by every after-dinner move. One visit, one count."""
    p = Player(b, port, target, save=LATE)
    try:
        _to_service_from_late(p)
        setup_check(p.ev("loungeLv()>0&&loungeOpenTonight()"), 'the Lounge is not open tonight on this save')
        install_bot(p.g); p.ev("__botUntil('R.groups.some(q=>q.table!=null&&!R.tables[q.table].lounge&&q.ticket&&q.state!==\\'leave\\'&&!q.reg&&!namedId(q))',30000,1/30)")
        r = json.loads(p.ev("""JSON.stringify((()=>{const g=R.groups.find(q=>q.table!=null&&!R.tables[q.table].lounge&&q.ticket&&q.state!=='leave'&&!q.reg&&!namedId(q));if(!g)return null;
          for(const it of g.ticket.items){it.st='served';it.q=it.q||'G';it.picked=true}g.state='check';const n0=R.st.guests,k0=R.st.groups,m0=S.money;collect(g);const ls=loungeSeatFor(g);if(!ls)return{noSeat:1};moveToLounge(g,ls);
          g.ticket={id:R.tkid++,no:1,g,lounge:1,items:[{d:'w_white',st:'served',q:'G',want:0,picked:true,lbar:1}],t0:R.t};R.tickets.push(g.ticket);g.state='check';const m1=S.money;collect(g,{tab:true});
          return{size:g.size,guests:R.st.guests-n0,groups:R.st.groups-k0,dinner:m1-m0,tab:S.money-m1,m0,m1,m2:S.money,n0,g0:R.st.guests}})())"""))
        setup_check(r and not r.get('noSeat'), f'no dinner party to move: {r}')
        check((r.get('dinner') or 0) > 0 and (r.get('tab') or 0) > 0, f'both bills are paid: {r}')
        check(r['guests'] == r['size'] and r['groups'] == 1, f'one visit counted {r["guests"]} guests / {r["groups"]} groups for a party of {r["size"]}')
    finally:
        p.close()


# ---------------------------------------------------------------- the code itself (guard)

@test
def qa_no_function_is_declared_twice(b, port, target):
    """Found by the lint (tools/lint.mjs, no-redeclare) in the final regression of 2026-10-09: the fifth batch of dishes
    added its own small plate knife as `function chKnife(c,x,y,now)` — the cutting board's knife already had that name.
    Two declarations of one function do not fail anything: the later one silently replaces the earlier everywhere, so
    every earlier dish's cut (the salad, the prosciutto, the tiramisu…) drew the plate knife, at an angle read as a
    time. A top-level function name is declared once."""
    src = open(os.environ.get('JK_GAME_JS') or os.path.join(ROOT, 'js', 'game.js'), encoding='utf-8').read()
    names = re.findall(r'(?m)^(?:async\s+)?function\s*\*?\s*([A-Za-z_$][\w$]*)\s*\(', src)
    check(len(names) > 1000, f'the functions were not found: {len(names)}')
    twice = sorted({n for n in names if names.count(n) > 1})
    check(not twice, f'declared more than once (the last one replaces the others): {twice}')
