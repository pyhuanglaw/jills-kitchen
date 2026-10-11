import sys, os
src = open('/home/user/jills-kitchen/js/game.js', encoding='utf-8').read()
M = {
 'no_fresh_name': ("if(!o.name&&!reg&&!NAMED[nm0])nm0=freshName(nm0,o.type);", ""),
 'bookings_not_reserved': ("R.nmUsed=[...new Set(R.sched.filter(o=>o.name).map(o=>o.name).concat(R.groups.map(g=>g.name)).filter(Boolean))]", "R.nmUsed=[]"),
 'not_saved_with_the_evening': ("'cpT','tasting','nmUsed']", "'cpT','tasting']"),
 'renames_everyone': ("if(!o.name&&!reg&&!NAMED[nm0])nm0=freshName(nm0,o.type);", "nm0=freshName(nm0,o.type);"),
 'no_borrowing': ("if(adult)chain.push(NAMES.office.concat(NAMES.gourmet).filter(n=>!NAMED[n]),NAMES_MORE.office.concat(NAMES_MORE.gourmet));", ""),
 'no_another': ("chain.push([sp(nm)],own.map(sp));", ""),
 'no_extra_names': ("const chain=[own,NAMES_MORE[type]||[]];", "const chain=[own];"),
}
for k, (a, b) in M.items():
    assert src.count(a) == 1, (k, src.count(a))
    open(os.path.join(sys.argv[1], k + '.js'), 'w', encoding='utf-8').write(src.replace(a, b))
print(' '.join(M))
