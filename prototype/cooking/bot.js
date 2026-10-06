/* A play-tester for the cooking prototype: a "decent human" — one action every `react` seconds (no reading two things
   at once), looks after the kitchen in the order a careful player would. It plays through window.__cook (the same
   moves a tap makes), in game time, so a whole night takes a second. Used by playtest.py; not loaded by the page. */
window.__botRun=function(k,opt){
  opt=opt||{};const C=window.__cook;C.pause(true);C.start(k,opt.lines?{seed:opt.seed||7,noTut:opt.noTut,lines:opt.lines,busy:!!opt.busy}:{seed:opt.seed||7,noTut:opt.noTut,line:opt.line||'stove',busy:!!opt.busy});
  if(opt.noCook){C.G.staff=C.G.staff.filter(s=>s.role==='waiter');C.G.staff.forEach(()=>{});document.querySelectorAll('.pp.cook,.pp.barista').forEach(e=>e.remove())}
  const G=()=>C.G,react=opt.react||.8,its=()=>[...G().items.values()];
  let next=0,acts=0;const log=[];
  const free=st=>{const a=G().slots[st];return a?a.indexOf(null):-1};
  function act(){
    const g=G();
    const items=its().filter(it=>!(it.at&&it.at.carry)&&it.ph!=='cook'&&it.ph!=='asm'&&!it.res);
    // 1 burnt → bin
    let it=items.find(i=>i.ph==='burnt');if(it&&C.move({it:it.id},{st:'trash'}))return 'trash';
    // 2 things going off or done, most urgent first: next station, a tray, the shelf
    const ready=items.filter(i=>i.ph==='done'||i.ph==='over'||i.ph==='hold').filter(i=>!(i.at&&i.at.tray)&&!(i.at&&i.at.st==='shelf'&&!C.K[i.k].fin&&free(C.nextStOf(i.k))<0));
    ready.sort((a,b)=>urg(a)-urg(b));
    for(const i of ready){
      const nx=C.nextStOf(i.k);
      if(nx&&C.canGo({it:i.id},{st:nx})){C.move({it:i.id},{st:nx});return 'next:'+i.k}
      if(C.K[i.k].fin){const tk=g.tickets.filter(t=>!t.done&&t.dishes.some((d,j)=>d===i.k&&!t.fill[j])).sort((a,b)=>b.w/b.pat-a.w/a.pat)[0];if(tk&&C.move({it:i.id},{tray:tk.id}))return 'plate:'+i.k}
      if(i.at&&i.at.st&&i.at.st!=='shelf'&&i.at.st!=='chill'&&(i.ph==='over'||i.ph==='done'&&i.pr&&i.pr.safe<1e8&&i.pr.safe-i.dt<2.5)&&C.canGo({it:i.id},{st:'shelf'})){C.move({it:i.id},{st:'shelf'});return 'shelf:'+i.k}
    }
    // 3 start what the tables are waiting for, slowest first
    const want=[];
    for(const tk of g.tickets.filter(t=>!t.done).sort((a,b)=>b.w/b.pat-a.w/a.pat)){
      tk.dishes.forEach((d,j)=>{if(tk.fill[j])return;want.push(d)})
    }
    // what is already on its way, by dish
    const onway={};for(const i of its()){let k=i.k;const e=endOf(k);onway[e]=(onway[e]||0)+1}
    const need={};for(const d of want)need[d]=(need[d]||0)+1;
    const cands=[];
    for(const d in need){const D=C.DISH[d];
      for(const s of D.start){const end=endOf(s);const have=countStart(s);const n=need[d]-have;if(n<=0)continue;const st=Object.keys(C.PR).find(x=>x.startsWith(s+'@')).split('@')[1];if(free(st)<0)continue;cands.push({s,st,len:chainLen(s)})}}
    cands.sort((a,b)=>b.len-a.len);
    if(cands.length){const c=cands[0];C.move({bin:c.s},{st:c.st});return 'start:'+c.s}
    // 4 make puddings ahead when there is room
    if(g.N.st.includes('chill')&&free('chill')>=0&&its().filter(i=>i.k==='custard'||i.k==='pudding').length<2){C.move({bin:'custard'},{st:'chill'});return 'ahead'}
    return null;
  }
  function endOf(k){let cur=k,n=0;while(n++<8){const s=C.nextStOf(cur);if(!s||s==='asm')break;cur=C.PR[cur+'@'+s].o}for(const r in C.ASM)if(C.ASM[r].needs.includes(cur))return r;return cur}
  function countStart(s){const end=endOf(s);let n=0;for(const i of its()){if(i.at&&i.at.tray)continue;const e=endOf(i.k);if(e!==end)continue;
    // for an assembled dish count the component of this start's line only
    if(C.ASM[end]){if(chainKinds(s).includes(i.k)||i.k===end)n++}else n++}return n}
  function chainKinds(s){const out=[s];let cur=s,n=0;while(n++<8){const st=C.nextStOf(cur);if(!st||st==='asm')break;cur=C.PR[cur+'@'+st].o;out.push(cur)}return out}
  function chainLen(s){let t=0,cur=s,n=0;while(n++<8){const st=C.nextStOf(cur);if(!st||st==='asm')break;const p=C.PR[cur+'@'+st];t+=p.t;cur=p.o}return t}
  function urg(i){if(i.ph==='over')return -100+i.ot;if(i.ph==='done'&&i.pr&&i.pr.safe<1e8)return i.pr.safe-i.dt;if(i.ph==='hold')return 30-i.ht;return 50}
  let t=0;const dt=.05;
  while(!G().ended&&t<(opt.stopAt||900)){
    if(t>=next){const a=act();if(a){acts++;log.push([+t.toFixed(1),a]);next=t+react*(.8+.4*Math.random())}else next=t+.2}
    C.step(dt);t+=dt;
  }
  return Object.assign({k,acts,log:log.slice(0,400)},window.__cookLast||{});
};
