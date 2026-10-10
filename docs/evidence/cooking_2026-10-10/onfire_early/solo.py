import json,glob,sys
from analyze import fires
ev=[]
for p in sorted(glob.glob(sys.argv[1] if len(sys.argv)>1 else 'out/*.json')):
    d=json.load(open(p))
    for r in d['rows']:
        fe=r['probe']['fe']; combos=sorted(set((x[6],x[7]) for x in fe if x[1]>=0))
        ev.append((p.split('/')[-1][:-5],r['day'],combos[0] if len(combos)==1 else tuple(combos),fe))
def kind(e):
    c=e[2]
    if c in ((0,0),(0,1)): return 'solo'
    if isinstance(c[0],tuple): return 'mixed'
    return 'cook'
for svc in ('human','perfect'):
    E=[e for e in ev if e[0].startswith(svc)]
    if not E: continue
    solo=[e for e in E if kind(e)=='solo']; cook=[e for e in E if kind(e)=='cook']
    print(svc,'evenings',len(E),'solo',len(solo),'with a cook',len(cook),'mixed',len(E)-len(solo)-len(cook))
    print('  with a cook, 30/36:',sum(1 for e in cook if fires(e[3],lambda r:(30,36)) is not None),'/',len(cook))
    for F in (32,33,34,35,36):
        row=[]
        for Sl in (38,39,40,42,44):
            n=sum(1 for e in solo if fires(e[3],lambda r:(F,Sl)) is not None); row.append(f'{n}/{len(solo)}'.rjust(6))
        print('  solo FAST',F,'SLOW 38/39/40/42/44',' '.join(row))
