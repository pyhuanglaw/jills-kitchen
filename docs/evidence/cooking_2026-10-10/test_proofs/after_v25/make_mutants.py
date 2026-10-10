"""The mutants behind mutants.txt (2026-10-10, after v2.5): each one breaks one thing the new or changed tests guard; the test must
fail on it. Written from js/game.js at 2e67df3. python3 make_mutants.py OUTDIR"""
import sys, os
src = open(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'js', 'game.js'), encoding='utf-8').read()
M = {
 'fire_day_gate': ("function fireTable(g){if(!R||g.__fr||g.seatAt==null)return;", "function fireTable(g){if(!R||g.__fr||g.seatAt==null||S.day<=3)return;"),
 'fire_solo_is_mature': ("const FIRE_SOLO=[33,40];", "const FIRE_SOLO=[30,36];"),
 # the first version kept the place check (stationCap of a waiter's 'both' is 0), so it never counted a waiter: an equivalent mutant
 'fire_waiter_is_a_cook': ("function fireCooks(){return(S.crew||[]).filter(m=>m.role==='chef'&&crewPool(m)==='restaurant'&&!!m.duty&&stationCap(m.duty)>0&&crewHere(m)).length}",
                           "function fireCooks(){return(S.crew||[]).filter(m=>(m.role==='waiter'||m.role==='chef'&&!!m.duty&&stationCap(m.duty)>0)&&crewPool(m)==='restaurant'&&crewHere(m)).length}"),
 'fire_standby_counts': ("&&!!m.duty&&stationCap(m.duty)>0&&crewHere(m)).length}", "&&crewHere(m)).length}"),
 'bistro_no_more_places': ("const CAP_LEVEL=[{chef:1,waiter:1,cleaner:0},{chef:2,waiter:2,cleaner:0},{chef:3,waiter:2,cleaner:0},{chef:4,waiter:2,cleaner:0},{chef:5,waiter:2,cleaner:1}];",
                           "const CAP_LEVEL=[{chef:1,waiter:1,cleaner:0},{chef:1,waiter:1,cleaner:0},{chef:2,waiter:1,cleaner:0},{chef:3,waiter:1,cleaner:0},{chef:4,waiter:1,cleaner:1}];"),
 'bistro_waiter_only': ("const CAP_LEVEL=[{chef:1,waiter:1,cleaner:0},{chef:2,waiter:2,cleaner:0},", "const CAP_LEVEL=[{chef:1,waiter:1,cleaner:0},{chef:1,waiter:2,cleaner:0},"),
 # for the three tests the full regression found with the old numbers (mutants_staff_numbers.txt)
 'room_adds_nothing': ("{k:'room',n:'後場整理區',w:'營運升級',on:opsLv('room')>0,add:{chef:1,waiter:1}}", "{k:'room',n:'後場整理區',w:'營運升級',on:opsLv('room')>0,add:{}}"),
 'kitchen2_adds_nothing': ("{k:'kitchen2',n:'廚房二期',w:'後場工程',on:projOn('kitchen2'),add:{waiter:2}}", "{k:'kitchen2',n:'廚房二期',w:'後場工程',on:projOn('kitchen2'),add:{}}"),
 'pd_places_are_chefs': ("{k:'pd1',n:'私人包廂 I',w:'二樓',on:pdStage()>=1,add:{waiter:1}},\n {k:'pd3',n:'私人包廂 III',w:'二樓',on:pdStage()>=3,add:{waiter:1}}",
                         "{k:'pd1',n:'私人包廂 I',w:'二樓',on:pdStage()>=1,add:{chef:1}},\n {k:'pd3',n:'私人包廂 III',w:'二樓',on:pdStage()>=3,add:{chef:1}}"),
}
os.makedirs(sys.argv[1], exist_ok=True)
for k, (a, b) in M.items():
    assert src.count(a) == 1, k
    open(os.path.join(sys.argv[1], f'mut_{k}.js'), 'w', encoding='utf-8').write(src.replace(a, b, 1))
print(len(M), 'mutants')
