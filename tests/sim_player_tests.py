"""The simulated player's own tests (tools/qa/sim_player.py, tools/qa/new_game_timeline.py; QA 2026-10-06).

The user, 2026-10-06: 「真人玩家 timeline 的決策與操作，原則上只能根據玩家在當下畫面上實際看得到、按得到的資訊進行」 — and the
simulator's past bugs (it skipped the closing; it built Lounge I through a button no screen shows; it filled the fridge
for free; it sat on $200k–300k with two employees while guests waited). These tests keep it honest:

- the player part reads the screen only and cannot reach the game's state (structure + the page's global scope);
- its decisions: guests waited and a place is free → it hires; it keeps the reserve the shop suggests;
- three days by taps: paid restock, the closing played, the summary read, every press a control that was there.

`python3 tests/run_tests.py -k sim_player` runs them (the full regression too).
"""
import json, os, re, sys
_rt = sys.modules['__main__'] if hasattr(sys.modules.get('__main__'), 'TESTS') else __import__('run_tests')
test, check, ROOT = _rt.test, _rt.check, _rt.ROOT
sys.path.insert(0, os.path.join(ROOT, 'tools', 'qa'))
import sim_player as sp
from player import Player


def _part_a_source():
    src = open(os.path.join(ROOT, 'tools', 'qa', 'sim_player.py'), encoding='utf-8').read()
    a = src.index('# ======================================================================= A.')
    c = src.index('# ======================================================================= C.')
    return src[a:c]


@test
def sim_player_reads_only_the_screen(b, port, target):
    """Part A (the player) holds the page only: no harness hook (`.ev(`, `__jk`), no observer; its JavaScript names no
    window property, no harness global (`__…`), no eval. In the page's global scope the game's state does not exist
    (the game is one closure), so a player script that tried to read it would fail, not cheat."""
    a = _part_a_source()
    for bad in ('.ev(', '__jk', 'Observer', 'g.ev', 'fill_fridge', 'FILL_FRIDGE', 'createElement', 'dispatchEvent', '.click()'):
        check(bad not in a, f'the player part uses {bad!r}')
    for js in sp.PLAYER_JS:
        body = re.sub(r"'[^']*'", "''", js)
        hit = re.findall(r'\bwindow\b|\bglobalThis\b|__\w+|\beval\b|\bFunction\(', body)
        check(not hit, f'player JS reaches outside the DOM: {hit[:3]} in {js[:80]}…')
    p = Player(b, port, target)
    try:
        for name in ('S', 'R', 'fact', 'story', 'rating', 'LOUNGE_PROJ', 'phase', 'DLG', 'menuList'):
            check(p.page.evaluate(f'typeof {name}') == 'undefined', f'the game\'s {name} is reachable from the page\'s global scope')
        scr = sp.Screen(p.page)
        check(scr.kind() == 'title', f'the title screen reads as {scr.kind()!r}')
        for js in sp.PLAYER_JS:   # every script runs in the page (DOM only) without an error
            p.page.evaluate(js, '#screen') if js.startswith('(sel') or js.startswith('(scope') else p.page.evaluate(js)
    finally:
        p.close()


class _FakeScreen:
    def __init__(self, money, staff, top):
        self.m, self.st, self.top, self.pressed = money, staff, top, []

    def hud(self):
        return {'money': self.m, 'day': 9, 'rate': 3.9, 'clock': '打烊後'}

    def shop_top(self):
        return self.top

    def staff(self):
        return self.st

    def buttons(self, scope='#screen'):
        out = []
        for h in self.st['hire']:
            if h['btn']:
                out.append({'act': 'hire', 'k': h['role'], 'd': None, 'text': h['btn']['text'], 'dis': h['btn']['dis'], 'card': None})
        return out

    def toasts(self):
        return []

    def kind(self):
        return 'shop'

    def panel(self):
        return None

    def reveal(self):
        return None


class _FakeHands:
    def __init__(self, scr):
        self.scr = scr

    def tap(self, act, k=None, d=None, scope='#screen'):
        self.scr.pressed.append((act, k))
        if act == 'hire':
            h = next(x for x in self.scr.st['hire'] if x['role'] == k)
            self.scr.m -= h['btn']['price']; h['btn'] = None

    def wait(self, n):
        pass


def _staff(waiter_free=True):
    return {'line': '', 'roles': {'廚師': {'n': 1, 'cap': 1}, '服務生': {'n': 0, 'cap': 1 if waiter_free else 0}}, 'wages': 304,
            'hire': [{'role': 'waiter', 'name': '服務生 0/1', 'wage': 253, 'btn': {'text': '聘請 $1,200', 'dis': False, 'price': 1200} if waiter_free else None, 'lock': ''},
                     {'role': 'chef', 'name': '廚師 1/1', 'wage': 304, 'btn': None, 'lock': '廚師名額已滿'}], 'crew': [], 'lounge': []}


@test
def sim_player_hires_when_guests_wait_and_keeps_the_reserve(b, port, target):
    """The normal player, on the summary's words: 「等太久」 and a free waiter's place → it hires (and says why); the same
    with too little money above the shop's 「建議保留」 → it does not, and the log says it held back."""
    top = {'cash': 0, 'need': 900, 'keep': 1100, 'low': False, 'tabs': [{'k': 'staff', 'text': '員工', 'dis': False, 'on': True}]}
    waited = {'minus': [{'k': '等太久', 'v': '平均耐心剩 41%', 's': '結帳時'}], 'plus': [], 'lost': 2, 'sales': [], 'ledger': {'租金': -300}, 'arrow': '↓', 'r1': 3.9}
    scr = _FakeScreen(20000, _staff(), top); log = sp.Log()
    pl = sp.NormalPlayer(scr, _FakeHands(scr), log); pl.last_summary = waited; pl.day = 9
    pl.reserve_base = 1100; pl.rent = 300; pl.staffing(sp._signals(waited))
    check(('hire', 'waiter') in scr.pressed, f'guests waited, a waiter\'s place was free, $20,000 in the till: pressed {scr.pressed}')
    row = next((r for r in log.rows if r['pressed'] and '聘請' in r['pressed']), None)
    check(row and '等太久' in row['why'], f'the log does not say why: {log.rows}')
    scr2 = _FakeScreen(1900, _staff(), top); log2 = sp.Log()
    pl2 = sp.NormalPlayer(scr2, _FakeHands(scr2), log2); pl2.last_summary = waited; pl2.day = 9
    pl2.reserve_base = 1100; pl2.rent = 300; pl2.staffing(sp._signals(waited))
    check(not scr2.pressed, f'with $1,900 (reserve $1,100 + two days of rent and wages) it should hold back: pressed {scr2.pressed}')
    check(any(r['kind'] == 'hold' for r in log2.rows), f'no 「先不請」 line: {log2.rows}')


@test
def sim_player_plays_three_days_by_taps(b, port, target):
    """A new game, three days, the normal player with the 一般玩家節奏 hands: each morning's restock is paid (the HUD
    drops by what the button says), the closing is played to its end, the summary is read, and every press in the log
    is a control the screen showed."""
    p = Player(b, port, target, save=None, W=390, seed=300, touch=True, scenes=True)
    try:
        g = p.g
        scr, hands, log = sp.Screen(p.page), sp.Hands(p), sp.Log()
        pl = sp.NormalPlayer(scr, hands, log); obs = sp.Observer(g)
        _rt.install_bot(g); g.ev(_rt.LAZY_ACTOR); g.ev(sp.HUMAN_JS % dict(sp.HUMAN_DEFAULT, seed=1)); g.ev(sp.SERVICE_JS); obs.install()
        g.ev("window.__closings=0;const fc0=finishClosing;finishClosing=function(){if(R&&R.closing!=null)__closings++;return fc0.apply(this,arguments)}")
        pl.settle(); hands.tap('open'); pl.settle()
        for day in (1, 2, 3):
            check(pl.settle() == 'prep', f'Day {day}: not at the prep screen')
            pl.prep(day); pl.open_shop()
            for _ in range(600):
                if obs.phase() != 'service':
                    break
                r = g.ev("__runService(300,'human')")
                if r['dlg'] or r['paused']:
                    pl.settle()
            check(pl.settle() == 'summary', f'Day {day}: the service did not end at the summary')
            sm = pl.summary()
            check(sm and sm['guests'] > 0 and sm['r1'] is not None, f'Day {day}: the summary was not read: {sm}')
            pl.to_shop(); pl.evening(day); pl.next_day()
        rs = [r for r in log.rows if r['pressed'] and '一鍵補到建議量' in r['pressed']]
        check(len(rs) == 3 and all(r['cost'] for r in rs), f'the restock was not paid each morning: {rs}')
        check(g.ev("__closings") == 3, f'the closing was skipped: {g.ev("__closings")} of 3 played to their end')
        check(not [r for r in log.rows if r['kind'] == 'skip' and '按不下去' in r['why'] and r['pressed'] and '補到建議量' in r['pressed']], 'a restock press found no button')
        check(not g.errors, f'page errors: {g.errors[:3]}')
        check(g.ev("__svc.err||0") == 0, f'the service hands threw: {g.ev("__svc.last")}')
    finally:
        p.close()


@test
def sim_player_answers_a_window_that_stops_the_day(b, port, target):
    """A window that stops the service and asks (試酒的晚上: 跟著菜走／跟著人走; 新企劃: 開始規劃／之後再說) is read and
    answered by a tap on one of its buttons, and the day goes on. (Until 2026-10-06 the simulator only read story panels:
    seed 301 stood forever on Day 52's tasting night, the service paused under 「今晚的酒要往哪邊走？」.)"""
    p = Player(b, port, target, save=None, W=390, seed=301, touch=True, scenes=True)
    try:
        g = p.g
        scr, hands, log = sp.Screen(p.page), sp.Hands(p), sp.Log()
        pl = sp.NormalPlayer(scr, hands, log)
        _rt.install_bot(g); g.ev(_rt.LAZY_ACTOR); g.ev(sp.HUMAN_JS % dict(sp.HUMAN_DEFAULT, seed=1)); g.ev(sp.SERVICE_JS)
        pl.settle(); hands.tap('open'); pl.settle()
        pl.prep(1); pl.open_shop()
        g.ev("__runService(90,'human')"); pl.settle()
        for setup, act in (("R.tasting=R.tasting||{n:0};tastingChoice()", 'tastingDir'), ("roomOffer('sr')", 'roomGo')):
            g.ev(setup)   # the test puts the window up (setup); the player only sees and taps
            r = g.ev("__runService(30,'human')")
            check(r['paused'] and r['i'] == 0, f'{act}: the service did not stop under the window: {r}')
            check(scr.kind() == 'modal', f'{act}: the player does not see the window: {scr.kind()}')
            check(pl.settle() == 'service', f'{act}: after answering, the screen is {scr.kind()}')
            row = log.rows[-1]
            check(row['kind'] == 'screen' and row['pressed'] and row['why'], f'{act}: no log line for the answer: {row}')
            r = g.ev("__runService(30,'human')")
            check(not r['paused'] and r['i'] == 30, f'{act}: the day did not go on: {r}')
        check(g.ev("R.tasting.dir") == 'food', 'the tasting night: the first answer is the first button (跟著菜走)')
        check(g.ev("S.sr&&S.sr.plan||(typeof srW==='function'&&srW().plan)") == 'plan', 'the new room was not planned')
        check(not pl.unknown, f'a window the player did not know: {pl.unknown}')
        check(not g.errors, f'page errors: {g.errors[:3]}')
    finally:
        p.close()
