"""2026-10-04 (the player: 「請給我『營業中 Staff Room 裡真的有員工』的實際截圖證據」): the player's save at phone size (390×844),
a whole evening played by the lazy bot, photographed as a player would see it — the room tabs during the service, the
second floor (its hall and the Staff Room's door), going in by a tap on the room, the Staff Room with someone of the crew
who went up on their own (the game's own break: nobody is placed there), and the room after they have gone back down.
Every Staff Room entry and exit is logged beside the pictures.

  python3 tools/sims/staff_room_shots.py SAVE SEED OUT_DIR
"""
import sys, os, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, os.path.join(ROOT, 'tests'))
import run_tests as rt, v24_tests as vt
from playwright.sync_api import sync_playwright
SAVE, SEED, OUT = sys.argv[1], int(sys.argv[2]), sys.argv[3]
os.makedirs(OUT, exist_ok=True)
notes = []
def note(s): print(s, flush=True); notes.append(s)

with sync_playwright() as p:
    srv, port = rt.start_server(); b = p.chromium.launch()
    g = rt.Game(b, port, 'index', seed=SEED, manual=True, viewport={'width': 390, 'height': 844})
    vt.load_save(g, os.path.basename(SAVE)); g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}")
    vt.to_service(g)
    def frames(n=12): g.ev(f"for(let i=0;i<{n};i++)__tick(1000/30)"); g.page.wait_for_timeout(60)
    def clean(): g.ev("document.querySelectorAll('#toasts>*,#plines>*,#banner>*').forEach(e=>e.remove())")
    def shot(name, what):
        frames(); clean(); frames(2); g.page.screenshot(path=os.path.join(OUT, name))
        note(f'{name}: {what} | ' + g.ev("JSON.stringify({clock:clockStr(),room,inside:srPeople().map(p=>p.m.name+(p.seated?'（坐著）':p.spotK?'（站著）':'（走進來）'))})"))
    def tab(k): g.ev(f"document.querySelector('#roomTabs [data-room={k}]').click()"); frames()
    def tap_scene(x, y):
        r = json.loads(g.ev(f"JSON.stringify((()=>{{const r=sc.getBoundingClientRect();return{{x:r.left+SV.ox+{x}*SV.s,y:r.top+SV.oy+{y}*SV.s}}}})())"))
        g.page.mouse.click(r['x'], r['y']); frames()
    log = []; state = {}
    def watch():
        s = json.loads(g.ev("JSON.stringify({clock:R?clockStr():'',cw:(S.crew||[]).filter(m=>R&&R.cw&&R.cw[m.id]).map(m=>{const w=R.cw[m.id];return[m.name,w.room,!!(w.task&&w.task.sr),!!(w.task&&w.task.fired)]})})"))
        for n, room, sr, fired in s['cw']:
            o = state.get(n, (False, False)); inn = sr and room == 'staff' and fired
            if sr and not o[0]: log.append(f"{s['clock']} {n} 出發上樓")
            if inn and not o[1]: log.append(f"{s['clock']} {n} 進了休息室")
            if o[0] and not sr: log.append(f"{s['clock']} {n} " + ('離開休息室，回去工作' if o[1] else '半路被叫回去'))
            state[n] = (sr, inn)
    # 1. the tabs during the service
    g.ev("__botUntil('R.t>=R.dur*.06',90000,1/30)"); tab('main'); shot('01_service_tabs.png', '營業中的主廳：上面的房間分頁有「休息室」')
    # 2. the second floor: its hall, the Staff Room's door
    tab('up'); shot('02_second_floor.png', '二樓：走廊、員工休息室的牆和門')
    # 3. in by a tap on the room itself
    sr = json.loads(g.ev("JSON.stringify({x:(UPR.sr.x0+UPR.sr.x1)/2,y:(UPR.sr.y0+UPR.sr.y1)/2})"))
    tap_scene(sr['x'], sr['y']); shot('03_in_from_the_floor.png', '在二樓點員工休息室：進到裡面')
    # 4. wait in the room for someone of the crew to come up by themselves (their break)
    seen = None
    for _ in range(3000):
        g.ev("__botUntil('false',6,1/30)"); watch()
        if g.ev("phase") != 'service' or g.ev("R.closing!=null"): break
        if g.ev("srPeople().some(p=>p.seated)"):
            seen = g.ev("srPeople().find(p=>p.seated).m.name"); break
    if seen:
        tab('staff'); shot('04_crew_inside.png', f'營業中：{seen} 自己上樓休息，坐在休息室裡')
        for _ in range(3000):   # until they go back down
            g.ev("__botUntil('false',6,1/30)"); watch()
            if not g.ev(f"srPeople().some(p=>p.m.name==={json.dumps(seen)})"): break
        tab('staff'); shot('05_after_they_left.png', f'{seen} 回去工作以後的休息室')
        tab('main'); shot('06_back_downstairs.png', '回到主廳')
    else:
        note('nobody of the crew went up during the service')
    for _ in range(4000):
        if g.ev("phase") != 'service' or not g.ev("!!R"): break
        g.ev("__botUntil('false',6,1/30)"); watch()
    stats = g.ev("JSON.stringify(S.lastSummary?{guests:S.lastSummary.guests,rev:S.lastSummary.rev,angry:S.lastSummary.angry,lost:S.lastSummary.lost}:null)")
    note('errors: ' + json.dumps(g.errors[:3]))
    b.close(); srv.shutdown()
note('the evening: ' + stats)
open(os.path.join(OUT, 'staff_room_log.txt'), 'w', encoding='utf-8').write('\n'.join(notes) + '\n\n休息室進出紀錄（營業中與打烊後）：\n' + '\n'.join(log) + '\n')
print('\n'.join(log))
