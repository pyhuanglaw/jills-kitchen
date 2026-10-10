"""Early ON FIRE: offline replay of recorded tables (new_game_timeline --probe fe) under candidate windows.
Row: [t, w, allP, jill, busyShare, nTables, chefs, waiters, nItems, level] or [t,-1,0,0,0] for an angry walkout."""
import json, sys, glob, statistics, itertools
def load(paths):
    ev=[]
    for p in paths:
        d=json.load(open(p))
        rows=d['days'] if isinstance(d,dict) and 'days' in d else d.get('rows') if isinstance(d,dict) else d
        for r in rows:
            pr=r.get('probe') or {}
            fe=pr.get('fe') or []
            ev.append({'src':p.split('/')[-1],'day':r.get('day'),'lv':pr.get('lv'),'crew':pr.get('crew'),'tab':fe})
    return ev
def hands(row): return 1+(row[6] if len(row)>6 else 0)+(row[7] if len(row)>7 else 0)
def fires(tab, win, RUN=4, BUSY=.5):
    run=0
    for row in tab:
        if row[1]<0: run=0; continue
        t,w,allp,jill,busy=row[:5]
        FAST,SLOW=win(row)
        if not allp or w>SLOW: run=0; continue
        if w>FAST: continue
        if busy<BUSY: continue
        run+=1.5 if jill else 1
        if run>=RUN: return t
    return None
if __name__=='__main__':
    ev=load(sys.argv[1:])
    print('evenings',len(ev))
    by={}
    for e in ev:
        for row in e['tab']:
            if row[1]>=0: by.setdefault((hands(row)),[]).append(row[1])
    for h in sorted(by): 
        ws=sorted(by[h]); print('hands',h,'tables',len(ws),'p10 %.1f p25 %.1f median %.1f p75 %.1f'%(ws[len(ws)//10],ws[len(ws)//4],statistics.median(ws),ws[3*len(ws)//4]))
