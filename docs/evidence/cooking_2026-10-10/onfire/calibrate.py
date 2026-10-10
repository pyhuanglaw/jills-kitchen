import json,sys,itertools,statistics
S='/tmp/claude-0/-home-user-jills-kitchen/63b8740a-97ce-5ff7-813a-d847b68fd153/scratchpad'
rows=[json.loads(l) for f in sys.argv[1:] for l in open(f) if l.startswith('{')]
def fires(tab,FAST,SLOW,BUSY,RUN):
    run=0
    for t,w,allp,jill,busy in tab:
        if w<0: run=0; continue          # a seated walkout
        if not allp or w>SLOW: run=0; continue
        if w>FAST: continue
        if busy<BUSY: continue
        run+=1.5 if jill else 1
        if run>=RUN: return True
    return False
def maxrun(tab,FAST,SLOW,BUSY):
    run=0;m=0
    for t,w,allp,jill,busy in tab:
        if w<0: run=0; continue
        if not allp or w>SLOW: run=0; continue
        if w>FAST or busy<BUSY: continue
        run+=1.5 if jill else 1; m=max(m,run)
    return m
print('evenings',len(rows), {k:sum(1 for r in rows if r['start']==k) for k in ('day30','day52','day92')})
waits=[w for r in rows for (_,w,_,_,_) in r['tab'] if w>=0]
print('table waits: n',len(waits),'p25',sorted(waits)[len(waits)//4],'median',statistics.median(waits),'p75',sorted(waits)[3*len(waits)//4])
for r in rows:
    print(r['start'],r['seed'],'L',r['level'],'tables',len(r['tab']),'maxrun(26,44,.6)',maxrun(r['tab'],26,44,.6),'maxrun(24,40,.6)',maxrun(r['tab'],24,40,.6),'maxrun(30,48,.5)',maxrun(r['tab'],30,48,.5))
best=[]
for FAST,SLOW,BUSY,RUN in itertools.product([20,22,24,26,28,30],[36,40,44,48,52],[.5,.6,.7],[4,5,6,7,8,9,10,12,14,16]):
    if SLOW<=FAST: continue
    per={k:[fires(r['tab'],FAST,SLOW,BUSY,RUN) for r in rows if r['start']==k] for k in ('day30','day52','day92')}
    tot=sum(sum(v) for v in per.values())/len(rows)
    spread=max(sum(v)/len(v) for v in per.values())-min(sum(v)/len(v) for v in per.values())
    best.append((abs(tot-.30)+.5*spread,tot,{k:round(sum(v)/len(v),2) for k,v in per.items()},FAST,SLOW,BUSY,RUN))
best.sort(key=lambda x:x[0])
for b in best[:15]: print(b)
