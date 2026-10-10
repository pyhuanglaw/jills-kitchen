"""怡君 and 《那面牆》 in new games: the day of each beat (new_game_timeline JSON rows[].beats), the gaps, and how crowded
the days around them are (major+v24 beats that day)."""
import json, sys
ORDER=['yj_meet','yj_look','yj_three','yj_chose','yj_move','yj_key','wall_worry','wall_photos','wall_visit','wall_wang','wall_setback','wall_fee','wall_mediation','wall_settle','wall_paper','wall_article','wall_fixed']
for p in sys.argv[1:]:
    d=json.load(open(p)); first={}; dens={}
    for r in d['rows']:
        for b in r.get('beats') or []:
            lane,_,k=b.partition(':')
            if k not in first: first[k]=r['day']
            if lane in ('m','v'): dens[r['day']]=dens.get(r['day'],0)+1
    seq=[(k,first[k]) for k in ORDER if k in first]
    print(p.split('/')[-1], 'days', d['rows'][-1]['day'])
    print('  ', '  '.join(f'{k}:{v}' for k,v in seq))
    if 'yj_meet' in first:
        m=first['yj_meet']; print('   from meeting:', {k:v-m for k,v in seq})
    yjdays=[v for k,v in seq]
    if yjdays:
        lo,hi=min(yjdays),max(yjdays)
        busy=[(dd,dens.get(dd,0)) for dd in range(lo,hi+1)]
        print('   span',lo,'-',hi,'=',hi-lo,'days; beat-days',len(set(yjdays)),'; days with >=3 major/v24 beats in the span',sum(1 for dd,n in busy if n>=3))
