import sys, os
src = open('/home/user/jills-kitchen/js/game.js', encoding='utf-8').read()
M = {
 'no_patience_protection': ("if(g.pat<=0){if(g.beat){", "if(g.pat<=0){if(false){"),
 'protect_every_story_visit': ("if(g.pat<=0){if(g.beat){", "if(g.pat<=0){if(g.story){"),
 'door_three_tries': ("(o.tries||0)<(o.beat?40:3)", "(o.tries||0)<3"),
 'door_says_her_name': ("if(o.beat){/* v2.5.4: the evening too full", "if(false){/* v2.5.4: the evening too full"),
 'plan_untagged': ("const W=(id,p,g,k)=>out.push({reg:id,p,grp:g,k,beat:1}),Y=(p,g,k)=>out.push(Object.assign({name:YJN,p,type:'regular',size:1,grp:g,k,beat:1}", "const W=(id,p,g,k)=>out.push({reg:id,p,grp:g,k,beat:1}),Y=(p,g,k)=>out.push(Object.assign({name:YJN,p,type:'regular',size:1,grp:g,k}"),
 'familiarity_tagged': ("out.push({reg:'sophie',p:.35},{reg:'mia',p:.35})", "out.push({reg:'sophie',p:.35,beat:1},{reg:'mia',p:.35,beat:1})"),
 'schedule_drops_it': ("name:w.name,story:1},w.beat?{beat:1}:{},w.o||{})", "name:w.name,story:1},w.o||{})"),
 'spawn_drops_it': ("story:!!o.story,beat:!!o.beat,", "story:!!o.story,"),
 'sold_out_only_yj': ("if(!items.length&&(isYJ(g)||g.beat)){", "if(!items.length&&isYJ(g)){"),
 'notice_says_her_name': ("function shownName(g){if(isYJ(g)&&!fact('yj_meet'))", "function shownName(g){if(false)"),
}
for k, (a, b) in M.items():
    assert src.count(a) == 1, (k, src.count(a))
    open(os.path.join(sys.argv[1], k + '.js'), 'w', encoding='utf-8').write(src.replace(a, b))
print(' '.join(M))
