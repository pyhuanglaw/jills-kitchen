import json, os
SRC='/home/user/jills-kitchen/js/game.js'; OUT=os.path.dirname(os.path.abspath(__file__))
src=open(SRC,encoding='utf-8').read()
def js(name, pairs):
    s=src
    for a,b in pairs:
        assert s.count(a)==1, (name, a[:80], s.count(a))
        s=s.replace(a,b)
    open(f'{OUT}/{name}.js','w',encoding='utf-8').write(s)
open(f'{OUT}/current.js','w',encoding='utf-8').write(src)
# 六
js('board_on_cold_counter',[("if(isPrepExt(s)){const x=prepExtX();return{x,y:KY.passTop+17,sc:.28,cx:x,cy:KY.passFeet,place:'prep',ext:1}}","if(isPrepExt(s)){const x=KX.prep.x+28;return{x,y:172,sc:.36,cx:x,place:'prep'}}")])
js('no_third_board',[("function prepExtOn(){return projOn('kitchen2')&&S.eq.prep>0}","function prepExtOn(){return false}")])
js('plates_on_the_board',[("span=(E.x1-(prepExtOn()?PREPX_W+10:17))-(PASS_GAP.x1+17)","span=(E.x1-17)-(PASS_GAP.x1+17)")])
js('cook_inside_the_pass',[("return{x,y:KY.passTop+17,sc:.28,cx:x,cy:KY.passFeet,place:'prep',ext:1}","return{x,y:KY.passTop+17,sc:.28,cx:x,cy:KY.passFeet+12,place:'prep',ext:1}")])
js('pass_loses_a_spot',[("function wfRowN(){return projOn('pass')?11:9}","function wfRowN(){return (projOn('pass')?11:9)-(prepExtOn()?1:0)}")])
js('third_board_never_used',[("function wfSlots(f){const t=WF_ST[f]&&WF_ST[f].slot;if(!t)return[];if(t==='pass')return wfPassSlots();return R.slots.filter(s=>s.type===t)}","function wfSlots(f){const t=WF_ST[f]&&WF_ST[f].slot;if(!t)return[];if(t==='pass')return wfPassSlots();return R.slots.filter(s=>s.type===t&&!isPrepExt(s))}")])
js('old_checkpoint_counts_the_board',[("(projOn('kitchen2')?2:0):0,true))for(let i=0;i<k;i++)kinds.push(t)}","(projOn('kitchen2')?2:0):0))for(let i=0;i<k;i++)kinds.push(t)}")])
js('charged_for_the_board',[("function prepExtMig(){if(!prepExtOn()||S.prepExtNews)return;S.prepExtNews=1;","function prepExtMig(){if(!prepExtOn()||S.prepExtNews)return;S.prepExtNews=1;S.money-=5000;")])
js('board_news_every_time',[("function prepExtMig(){if(!prepExtOn()||S.prepExtNews)return;S.prepExtNews=1;","function prepExtMig(){if(!prepExtOn())return;")])
# 七 cold room
js('cold_room_adds_100',[("+(projOn('coldroom')?150:0)","+(projOn('coldroom')?100:0)")])
js('cold_room_costs_50000',[("{k:'coldroom',n:'冷藏室擴建',cost:60000,","{k:'coldroom',n:'冷藏室擴建',cost:50000,")])
js('cold_room_without_walkin',[("{k:'coldroom',n:'冷藏室擴建',cost:60000,lv:5,need:'walkin',","{k:'coldroom',n:'冷藏室擴建',cost:60000,lv:5,need:'cooler',")])
js('cold_room_not_a_cold_step',[("const COLD_PROJ=['cooler','walkin','coldroom'];","const COLD_PROJ=['cooler','walkin'];")])
# 七 forecast
js('forecast_as_before',[("預計約 ${T.flow||T.people} 位客人","預計約 ${T.people} 位客人")])
js('forecast_never_learns',[("function flowLearn(st){const T=S.today;","function flowLearn(st){return;const T=S.today;")])
js('task_follows_the_forecast',[("S.today.tasks=genTasks(ex);S.todayCost=S.todayCost||0;","S.today.tasks=genTasks(Object.assign({},ex,{people:Math.round(ex.groups*meanGroupSize())}));S.todayCost=S.todayCost||0;")])
js('arrivals_uncapped',[("if(NT>=8)g=Math.min(g,NT*dayDur(D)/75);","if(NT>=8)g=Math.min(g,NT*dayDur(D)/40);")])
print(sorted(f for f in os.listdir(OUT) if f.endswith('.js')))
