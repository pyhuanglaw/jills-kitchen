"""2026-10-04 (the player: 「正常營業觀察了一段時間，完全沒有看到任何員工進 Staff Room」「用我的成熟存檔跑完整營業日，記錄每一次 Staff Room
entry / exit」): one whole evening on a real save, lazy bot (the staff do the work, as the player plays), with every Staff
Room movement logged — a break sent, called back on the way, arrived, left; who was inside at closing — and the
evening's service numbers, so a change to the breaks can be checked against the restaurant downstairs.

  python3 tools/sims/staff_room_day.py SAVE SEED [ROOT]     (ROOT: another checkout, to run the same evening on older code)
"""
import sys, os, json
SAVE, SEED = sys.argv[1], int(sys.argv[2]); ROOT = sys.argv[3] if len(sys.argv) > 3 else os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'tests'))
import run_tests as rt, v24_tests as vt
from playwright.sync_api import sync_playwright

SNAP = r"""JSON.stringify({t:R.t,dur:R.dur,clock:clockStr(),closing:R.closing,
 cw:(S.crew||[]).filter(m=>R.cw&&R.cw[m.id]).map(m=>{const w=R.cw[m.id];return[m.name,m.role,w.room,!!(w.task&&w.task.sr),!!(w.task&&w.task.fired),w.task&&w.task.sr?w.task.dur:null]}),
 walkers:(R.srw||[]).map(w=>[w.m.name,w.room,!!w.arr]),inside:srPeople().map(p=>p.m.name),brk:R.srBreaks||0})"""
with sync_playwright() as p:
    srv, port = rt.start_server(); b = p.chromium.launch()
    g = rt.Game(b, port, 'index', seed=SEED, manual=True, viewport={'width': 390, 'height': 844})
    vt.load_save(g, os.path.basename(SAVE)); g.ev("for(let i=0;i<30;i++){if(typeof DLG!=='undefined'&&DLG)dlgNext()}")
    vt.to_service(g)
    g.ev("window.__srSent=[];const __s0=srSend;srSend=function(m,dur,spot){const r=__s0.apply(this,arguments);if(r)window.__srSent.push([clockStr(),m.name,dur>1e6?'closing':Math.round(dur)]);return r}")
    st = {}; log = []; dur = g.ev("R.dur"); prev_inside = set()
    def ev(c, who, what): log.append(f'{c}  {who}  {what}')
    for _ in range(20000):
        g.ev("__botUntil('false',6,1/30)")
        if g.ev("phase") != 'service' or not g.ev("!!R"): break
        s = json.loads(g.ev(SNAP)); c = s['clock'] + (' (打烊後)' if s.get('closing') is not None else '')
        for name, role, room, sr, fired, d in s['cw']:
            o = st.get(name, {'sr': False, 'in': False, 'since': None})
            if sr and not o['sr']: ev(c, name, f'出發去休息室（{role}）')
            if sr and room == 'staff' and fired and not o['in']: ev(c, name, '到了，在休息室裡'); o['since'] = s['t']
            if o['sr'] and not sr:
                if o['in']: ev(c, name, f'離開休息室（待了 {round((s["t"]-o["since"])/dur*270)} 分鐘）')
                else: ev(c, name, '半路被叫回去工作')
            o['sr'] = sr; o['in'] = sr and room == 'staff' and fired; st[name] = o
        ins = set(s['inside']) | {w[0] for w in s['walkers'] if w[2]}
        for n in sorted(ins - prev_inside):
            if not any(n == x[0] for x in s['cw']): ev(c, n, '（廚房／吧台的人）走上來，在休息室裡')
        prev_inside = ins
    stats = json.loads(g.ev("JSON.stringify(S.lastSummary?{guests:S.lastSummary.guests,rev:S.lastSummary.rev,angry:S.lastSummary.angry,lost:S.lastSummary.lost,lg:S.lastSummary.lg}:null)"))
    sent = json.loads(g.ev("JSON.stringify(window.__srSent)"))
    b.close(); srv.shutdown()
print('\n'.join(log)); print('srSend calls:', sent); print('the evening:', stats)
