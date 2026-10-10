"""Broken versions of js/game.js for the tests changed or added after the user's iPhone reports (2026-10-10). Each one is
a problem one of those tests is there to catch. python3 mutants_make.py OUTDIR   (from the repo root, on the game being checked)"""
import sys
D = sys.argv[1] + '/'
src = open('js/game.js', encoding='utf-8').read()
def mut(name, pairs):
    s = src
    for a, b in pairs:
        assert s.count(a) == 1, (name, a[:60], s.count(a)); s = s.replace(a, b, 1)
    open(D + name + '.js', 'w', encoding='utf-8').write(s); print(name, 'ok')
# the kitchen's chips never go up out of the way (the user: 「按鈕擋住冷盤台、點不到」)
mut('chips_never_lift', [("function chipsWhere(){const sc0=$('#stockChip')", "function chipsWhere(){return null;const sc0=$('#stockChip')")])
# all of them go up or none (the first version of this: at 1100x500 none moved, the three did not fit beside the tabs)
mut('chips_lift_all_or_none', [("const over=at.filter(c=>boxes.some(b=>c.x0<b.x1&&c.x0+c.w>b.x0&&c.y0<b.y1&&c.y0+h>b.y0));", "const over=at.some(c=>boxes.some(b=>c.x0<b.x1&&c.x0+c.w>b.x0&&c.y0<b.y1&&c.y0+h>b.y0))?at:[];")])
# a tap beside the task list leaves it open (the user: 「今日任務還沒辦法按掉」)
mut('task_list_stays', [("document.addEventListener('pointerdown',e=>{const p=$('#taskPanel');if(p&&!p.hidden&&!p.contains(e.target)&&!$('#taskChip').contains(e.target))p.hidden=true},{capture:true,passive:true});", "")])
# the list opens over its own chip again (the user: 「今日任務的按鍵位置擋到冷盤了」)
mut('task_list_over_chip', [("function taskPanelPlace(){const tc=$('#taskChip'),tp=$('#taskPanel');if(!tc||!tp||tc.hidden)return;", "function taskPanelPlace(){return;const tc=$('#taskChip'),tp=$('#taskPanel');if(!tc||!tp||tc.hidden)return;")])
# a batch of three fried rice at level 3 is split in two (cooking_a_full_place_is_a_quiet_wait, case D, after its change)
mut('batch_of_three_split', [("if(WF_BIG.has(b))return L>=5?4:L>=3?3:2;", "if(WF_BIG.has(b))return L>=5?4:2;")])
# a cook at LV1 never plates (the old CHEF_SKILL ladder, in one line: his places are his line's first two)
mut('cooks_never_plate', [("function chefProf(m,f){const fam=f==='pizza'?'oven':f;return fam===chefCore(m)?3:2}", "function chefProf(m,f){const fam=f==='pizza'?'oven':f;if(fam==='plate')return 0;return fam===chefCore(m)?3:2}")])
# the plates are fetched behind the counter by the wall again (the user: 「裝盤為什麼走到左上角？那裏又沒有盤子」)
mut('rack_by_the_wall', [("function wfRack(){return{x:KX.sink.x+12,y:KY.top+KY.h+KY.face+4}}", "function wfRack(){return{x:KX.sink.x+12,y:KY.feet}}")])
