import json, os
SRC='/home/user/jills-kitchen/js/game.js'; OUT=os.path.dirname(os.path.abspath(__file__))
src=open(SRC,encoding='utf-8').read()
def js(name, pairs):
    s=src
    for a,b in pairs:
        assert s.count(a)==1, (name, a[:80], s.count(a))
        s=s.replace(a,b)
    open(f'{OUT}/{name}.js','w',encoding='utf-8').write(s)
def css(name, rules):
    s=src+"\n;(function(){const st=document.createElement('style');st.textContent=%s;(document.head||document.documentElement).appendChild(st)})();\n" % json.dumps(rules)
    open(f'{OUT}/{name}.js','w',encoding='utf-8').write(s)
open(f'{OUT}/current.js','w',encoding='utf-8').write(src)
# 四: the card back at the foot of the page
js('restock_at_the_foot',[("  ${prepRestockHTML()}\n",""),("  ${wineTonightHTML()}\n","  ${wineTonightHTML()}\n  ${prepRestockHTML()}\n")])
# 五: numbers written in
js('shortfall_written_in',[("<b>預估需求 ${capd} 份｜冰箱容量 ${cap} 份</b>","<b>預估需求 118 份｜冰箱容量 60 份</b>")])
# 五: small type
css('shortfall_small','.rs-short{font-size:11px}.rs-short b{font-size:11.5px}')
# 四: the estimate from the deficits (the old label), not the plan
js('estimate_from_deficits',[("let n=0,c=0;for(const d in plan){n+=plan[d];c+=plan[d]*costOf(d)}","let n=0,c=0;{const sg=suggestStock();for(const d in sg){const k=Math.max(0,sg[d]-(S.stock[d]||0));n+=k;c+=k*costOf(d)}}")])
# 四: a second, own restock algorithm (fills every dish to its suggestion in menu order, no fair share, no sending back)
js('own_algorithm',[("case'restock':{const m0=S.money;const back=returnOffMenu();const sug=suggestStock(),plan=restockPlan();for(const x in plan)buyStock(x,plan[x])",
                     "case'restock':{const m0=S.money;const back={n:0,rf:0};const sug=suggestStock(),plan={};for(const x in sug){const n=sug[x]-(S.stock[x]||0);if(n>0)buyStock(x,n)}")])
# 五: always 「可升級」
js('always_upgrade',[("${fridgeCanGrow()?'可升級冰箱增加容量':'冰箱和冷藏庫都已經是最大'}","可升級冰箱增加容量")])
# 五 summary: the line on any night with sell-outs
js('summary_any_night',[("function fridgeShortSum(st){const fr=st&&st.fr;if(!fr)return null;","function fridgeShortSum(st){const fr=(st&&st.fr)||{need:0,cap:fridgeCap(),open:stockTotal()};")])
js('summary_upgrade_always',[("（照售價約 ${fmt(s.fr.rev)}）。${fridgeCanGrow()?'升級冰箱可以多放。':''}","（照售價約 ${fmt(s.fr.rev)}）。升級冰箱可以多放。")])
js('summary_no_line',[("${s.fr?`<div class=\"sum-fridge\">","${0?`<div class=\"sum-fridge\">")])
# 八: the reach
css('reach_v255','.tog::before{display:none}.tog{width:54px;height:36px;border-radius:18px;border:4px solid transparent;background:#D9CDB8;background-clip:padding-box;margin:-4px}.tog.on{background:var(--sage);background-clip:padding-box}.menu-row .tog{margin:-4px}.tog::after,.menu-row .tog::after{top:3px;left:3px}.step button{height:38px;margin:-4px -6px}.menu-row .ctl>.step:not(.stk) button{margin:-4px -6px;padding:1px 6px}.sig .step button{height:42px;margin:-4px -6px}.stkq .mini::before{display:none}.stkq .mini{height:36px;padding:0 9px;border:solid transparent;border-width:4px 2px;border-radius:11px/13px;margin:-4px -2px;background:var(--paper2);background-clip:padding-box;box-shadow:inset 0 0 0 1px var(--line);position:static}')
css('reach_overlaps','.menu-row .ctl>.step:not(.stk) button{margin:-7px -6px;padding:0}.stkq .mini{margin:-7px -2px -9px;padding:0 11px 8px}.stkq .mini::before{top:7px}')
css('mini_under_the_note','.stkq .mini{position:static;z-index:auto}')
css('rows_taller','.menu-row .ctl{gap:14px 8px}')
css('tog_even_in_rows','.menu-row .tog{margin:-8px -4px}.menu-row .tog::before{top:8px}.menu-row .tog::after{top:11px}')
css('x_24','.bchip .x{width:24px;height:24px;margin:0;padding:0;border-radius:50%;background:rgba(46,32,25,.08)}')
css('x_rows_close','.bp{gap:6px}')
print(sorted(f for f in os.listdir(OUT) if f.endswith('.js')))
# qa_restock_says_why_it_cannot (adapted 2026-10-13): a greyed button that does not say why; a live one that buys nothing and says nothing
js('greyed_silent',[("pv.short>0?'（冰箱已滿）':'（已足夠）'","'（已足夠）'"),("pv.short>0?'冰箱滿了，放不下更多。':'今晚的菜都補到建議量了。'","'今晚的菜都補到建議量了。'")])
js('live_silent',[("${pv.n>0||pv.offN?'':'disabled'}","${pv.n>0||pv.offN||pv.short>0?'':'disabled'}"),("pv.short>0?'冰箱滿了，放不下更多。':'今晚的菜都補到建議量了。'","'今晚的菜都補到建議量了。'"),("pv.short>0?'（冰箱已滿）':'（已足夠）'","''"),("else if(much.length){const over=","else if(0&&much.length){const over=")])
