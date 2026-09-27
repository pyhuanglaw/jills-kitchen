/* Jill's Kitchen — game logic, rendering, audio, save system */
(()=>{
'use strict';
/* ================= utilities ================= */
const $=s=>document.querySelector(s);
const clamp=(v,a,b)=>v<a?a:v>b?b:v;
const rand=(a,b)=>a+Math.random()*(b-a);
const ri=(a,b)=>Math.floor(a+Math.random()*(b-a+1));
const pick=a=>a[Math.floor(Math.random()*a.length)];
const lerp=(a,b,t)=>a+(b-a)*t;
const fmt=n=>(n<0?'-$':'$')+Math.abs(Math.round(n)).toLocaleString('en-US');
function wpick(arr,wf){let s=0;const w=arr.map(x=>{const v=Math.max(0,wf(x)||0);s+=v;return v});if(s<=0)return null;let r=Math.random()*s;for(let i=0;i<arr.length;i++){r-=w[i];if(r<=0)return arr[i]}return arr[arr.length-1]}
function el(c,x,y,rx,ry){c.beginPath();c.ellipse(x,y,Math.max(.1,rx),Math.max(.1,ry),0,0,Math.PI*2);c.fill()}
function rr(c,x,y,w,h,r){r=Math.max(0,Math.min(r,w/2,h/2));c.beginPath();c.moveTo(x+r,y);c.arcTo(x+w,y,x+w,y+h,r);c.arcTo(x+w,y+h,x,y+h,r);c.arcTo(x,y+h,x,y,r);c.arcTo(x,y,x+w,y,r);c.closePath()}
function circ(c,x,y,r){c.beginPath();c.arc(x,y,Math.max(.1,r),0,Math.PI*2);c.fill()}
function rng(seed){let a=seed>>>0;return()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
function hash(s){let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}return h>>>0}
function mkCanvas(w,h){const c=document.createElement('canvas');c.width=w;c.height=h||w;return c}
/* accepts '#rrggbb' and 'rgb(r,g,b)' (mix() returns the latter, and its result is sometimes mixed again) */
function hex2rgb(h){if(h.charAt(0)!=='#'){const m=h.match(/[\d.]+/g)||[];return[+m[0]||0,+m[1]||0,+m[2]||0]}h=h.replace('#','');return[parseInt(h.slice(0,2),16),parseInt(h.slice(2,4),16),parseInt(h.slice(4,6),16)]}
function mix(a,b,t){const A=hex2rgb(a),B=hex2rgb(b);return`rgb(${Math.round(lerp(A[0],B[0],t))},${Math.round(lerp(A[1],B[1],t))},${Math.round(lerp(A[2],B[2],t))})`}
const FONT='Figtree,"PingFang TC","Noto Sans TC","Microsoft JhengHei",sans-serif';
const DFONT='"Young Serif",Georgia,serif';

/* ================= game data ================= */
function shuffle(a){a=a.slice();for(let i=a.length-1;i>0;i--){const k=Math.floor(Math.random()*(i+1));[a[i],a[k]]=[a[k],a[i]]}return a}
const sA=(items,order,txt)=>({t:'add',items,order:!!order,txt});
const sW=(verb,time,over,anim)=>({t:'wait',verb,time,over:over||0,anim:anim||null});
const sZ=(verb,time,c,w)=>({t:'zone',verb,time,c,w});
const sH=(verb,ing,a,b,rate,unit)=>({t:'hold',verb,ing,a,b,rate,unit});
const sD=(verb,ing,min,max)=>({t:'dose',verb,ing,min,max})
const sK=(verb,time,board)=>({t:'work',verb,time,board:!!board})   /* routine handwork: one decision starts it, Jill does the rest */;
const DISHES={
 friedrice:{n:'黃金蛋炒飯',cat:'main',st:'stove',v:'wok',price:120,cost:35,diff:1,pop:1,lv:1,rd:0,steps:[sA(['egg','rice'],1,'依序下鍋：先雞蛋、再白飯'),sW('翻炒',4.5,5,'stir'),sD('淋醬油','soy',2,3)],fin:['scallion']},
 coffee:{n:'拿鐵咖啡',cat:'drink',st:'bar',v:'cup',price:90,cost:18,diff:1,pop:1,lv:1,rd:0,steps:[sH('磨豆','beans',.6,.8,.55,'研磨度'),sW('萃取濃縮',3.5),sH('蒸奶泡','milk',.7,.85,.5,'溫度')]},
 pasta:{n:'番茄義大利麵',cat:'main',st:'stove',v:'pot',price:160,cost:45,diff:2,pop:1,lv:1,rd:0,steps:[sA(['noodle'],0,'麵條下鍋'),sW('煮麵',6,4.5),sA(['tomato'],0,'瀝乾，加入番茄醬汁'),sK('拌炒',2.4)],fin:['basil','parmesan']},
 salad:{n:'田園沙拉',cat:'starter',st:'prep',v:'bowl',price:110,cost:28,diff:1,pop:.85,lv:1,rd:0,steps:[sK('切菜',2.4,1),sA(['greens','ctomato'],0,'放入生菜、小番茄'),sD('淋油醋醬','dressing',1,2)],fin:['cucumber']},
 burger:{n:'經典牛肉漢堡',cat:'main',st:'stove',v:'griddle',pan:1,price:190,cost:62,diff:2,pop:1.1,lv:1,rd:600,steps:[sA(['patty'],0,'牛肉排下鍋'),sZ('翻面',4.5,.72,.15),sZ('起鍋',4,.78,.14),sA(['cheese','bun'],1,'組裝：起司 → 麵包')],fin:['lettuce']},
 blacktea:{n:'錫蘭檸檬紅茶',cat:'drink',st:'bar',v:'cup',price:70,cost:10,diff:1,pop:.8,lv:1,rd:300,steps:[sA(['tea'],0,'放入紅茶葉'),sW('浸泡',4,4),sA(['lemon'],0,'撈出茶葉，放上檸檬片')]},
 sparkling:{n:'檸檬氣泡水',cat:'drink',st:'bar',v:'glass',price:60,cost:8,diff:1,pop:.7,lv:1,rd:250,steps:[sA(['ice','lemon'],0,'放入冰塊與檸檬'),sH('倒氣泡水','soda',.76,.92,.6,'水位')]},
 soup:{n:'南瓜濃湯',cat:'starter',st:'stove',v:'pot',price:130,cost:30,diff:1,pop:.85,lv:1,rd:700,steps:[sA(['pumpkin','stock'],1,'先放南瓜，再倒高湯'),sW('熬煮',6,0,'stir'),sH('加鮮奶油','cream',.45,.68,.5,'份量')],fin:['seeds']},
 pudding:{n:'焦糖布丁',cat:'dessert',st:'prep',v:'mold',price:120,cost:28,diff:1,pop:.9,lv:1,rd:700,steps:[sH('倒布丁液','custard',.7,.88,.55,'份量'),sW('冷藏',5),sH('淋焦糖','caramel',.35,.6,.6,'份量')]},
 fries:{n:'松露薯條',cat:'starter',st:'oven',v:'tray',price:150,cost:42,truffle:1,diff:2,pop:1,lv:1,rd:900,steps:[sA(['potato'],0,'薯條鋪上烤盤'),sZ('出爐',6,.8,.14),sD('撒鹽','salt',1,2)],fin:['truffle']},
 fruitsoda:{n:'莓果蘇打',cat:'drink',st:'bar',v:'glass',price:120,cost:24,diff:1,pop:.9,lv:2,rd:800,steps:[sA(['fruit','ice'],0,'放入水果片與冰塊'),sH('倒氣泡水','soda',.76,.92,.6,'水位')],fin:['syrup']},
 veg:{n:'香料烤蔬菜',cat:'starter',st:'oven',v:'tray',price:140,cost:32,diff:1,pop:.75,lv:2,rd:900,steps:[sK('切蔬菜',2.4,1),sD('淋橄欖油','oil',1,2),sZ('出爐',7,.8,.14)]},
 tiramisu:{n:'提拉米蘇',cat:'dessert',st:'prep',v:'mold',price:170,cost:45,diff:2,pop:1,lv:2,rd:1400,steps:[sA(['ladyfinger','mascarpone'],1,'依序：手指餅乾 → 馬斯卡彭'),sW('冷藏',6),sD('撒可可粉','cocoa',1,2)],fin:['espresso']},
 chicken:{n:'香草烤雞',cat:'main',st:'oven',v:'tray',price:360,cost:110,diff:2,pop:1,lv:2,rd:2200,steps:[sA(['chicken'],0,'雞腿放上烤盤'),sD('抹香草鹽','herbs',1,2),sZ('出爐',10,.8,.13)],fin:['lemon']},
 steak:{n:'炙烤肋眼牛排',cat:'main',st:'stove',v:'pan',pan:1,price:520,cost:190,diff:3,pop:1.1,lv:2,rd:3200,steps:[sA(['steak'],0,'肋眼下鍋'),sZ('翻面',5,.7,.13),sH('澆淋奶油','butter',.5,.78,.6,'份量'),sZ('起鍋',5,'want',.09)],fin:['salt']},
 basque:{n:'巴斯克乳酪蛋糕',cat:'dessert',st:'prep',v:'mold',price:170,cost:42,diff:2,pop:1,lv:3,rd:2000,steps:[sH('倒入乳酪糊','cheesebatter',.72,.9,.5,'份量'),sW('烘烤定型',5),sA(['berries'],0,'放上莓果')]},
 prosciutto:{n:'生火腿沙拉',cat:'starter',st:'prep',v:'plate',price:220,cost:78,diff:2,pop:.9,lv:3,rd:2400,steps:[sA(['prosciutto','fig'],0,'擺上生火腿與無花果'),sD('淋巴薩米克醋','balsamic',1,2)],fin:['greens','parmesan']},
 salmon:{n:'香烤鮭魚',cat:'main',st:'oven',v:'tray',price:420,cost:140,diff:3,pop:1,lv:3,rd:3600,steps:[sA(['salmon','asparagus'],1,'先放鮭魚，再放蘆筍'),sZ('出爐',9,.8,.12)],fin:['lemon','salt']},
 seafood:{n:'海鮮義大利麵',cat:'main',st:'stove',v:'pot',price:380,cost:130,diff:3,pop:1,lv:3,rd:3800,steps:[sA(['noodle'],0,'麵條下鍋'),sW('煮麵',5,4.5),sA(['garlic','shrimp','mussel'],1,'依序：蒜片 → 鮮蝦 → 淡菜'),sK('拌炒',2.6)],fin:['parsley']},
 duck:{n:'香煎鴨胸',cat:'main',st:'stove',v:'pan',pan:1,price:480,cost:160,diff:3,pop:1.1,lv:3,rd:4500,steps:[sK('鴨皮劃刀',2,1),sA(['duck'],0,'鴨皮朝下下鍋'),sZ('翻面',6,.72,.12),sZ('起鍋',5,.8,.11),sH('淋橙醬','orange',.45,.7,.55,'份量')]},
 risotto:{n:'松露燉飯',cat:'main',st:'stove',v:'pan',truffle:1,price:440,cost:150,diff:3,pop:1,lv:4,rd:5500,steps:[sA(['arborio','wine'],1,'先燉飯米，再倒白酒'),sW('燉煮',7,4,'stir'),sH('加高湯','stock',.55,.78,.5,'份量'),sW('收汁',4,0,'stir')],fin:['truffle','parmesan']},
 souffle:{n:'舒芙蕾',cat:'dessert',st:'oven',v:'ramekin',price:240,cost:60,diff:3,pop:1,lv:4,rd:5000,steps:[sK('打發蛋白',3,1),sH('倒入模具','whites',.7,.86,.55,'份量'),sZ('出爐',7,.8,.1),sD('撒糖粉','sugar',1,2)]},
};
const CAT_N={main:'主餐',starter:'前菜',dessert:'甜點',drink:'飲料'};
/* ---- 2.1: 特製版. A dish Jill has mastered (LV3) can become its own richer version: the same cooking, a finer finish on
   the plate, its own price and stock. Bought on the R&D page; the first plate is Jill's, as with any new dish. ---- */
const SPECIALS={
 friedrice:{id:'friedrice_x',n:'蟹肉蛋炒飯',top:'crab',price:190,cost:62,rd:1800,d:'炒飯上鋪一層新鮮蟹肉，蔥花更多。'},
 pasta:{id:'pasta_x',n:'布拉塔番茄麵',top:'burrata',price:260,cost:82,rd:2400,d:'番茄麵上放一整顆布拉塔起司，切開流出來。'},
 burger:{id:'burger_x',n:'松露蘑菇牛肉堡',top:'porcini',price:290,cost:98,rd:2800,d:'牛肉堡夾松露蘑菇醬。',truffle:1},
 soup:{id:'soup_x',n:'松露南瓜濃湯',top:'truffle',price:210,cost:52,rd:2200,d:'南瓜濃湯上桌前刨黑松露。',truffle:1},
 steak:{id:'steak_x',n:'乾式熟成肋眼',top:'marrow',price:780,cost:290,rd:6500,d:'熟成 28 天的肋眼，配一段烤骨髓。'},
 duck:{id:'duck_x',n:'櫻桃鴨胸',top:'cherry',price:680,cost:230,rd:6000,d:'鴨胸配櫻桃紅酒醬。'},
 risotto:{id:'risotto_x',n:'海膽燉飯',top:'uni',price:640,cost:225,rd:7000,d:'松露燉飯上放兩片海膽。',truffle:1},
 souffle:{id:'souffle_x',n:'抹茶舒芙蕾',top:'matcha',price:340,cost:88,rd:5500,d:'舒芙蕾出爐撒上抹茶粉。'},
};
for(const base in SPECIALS){const sp=SPECIALS[base],B=DISHES[base];DISHES[sp.id]=Object.assign({},B,{n:sp.n,price:sp.price,cost:sp.cost,rd:0,special:base,fin:(B.fin||[]).concat([sp.top]),pop:(B.pop||1)*1.1,lv:Math.max(B.lv,3),truffle:sp.truffle||B.truffle})}
function baseOf(d){const D=DISHES[d];return D&&D.special?D.special:d}
const ST_N={stove:'爐台',oven:'烤箱',bar:'咖啡吧',prep:'冷盤台'};
const ING={egg:{n:'雞蛋',k:'egg'},rice:{n:'白飯',k:'bowl',c:'#FBF6E6'},scallion:{n:'蔥花',k:'bits',c:'#5FA640'},soy:{n:'醬油',k:'bottle',c:'#3A1E10'},
 noodle:{n:'義大利麵',k:'noodle'},tomato:{n:'番茄醬汁',k:'bowl',c:'#C8321E'},basil:{n:'羅勒葉',k:'leaf',c:'#3F8B3A'},parmesan:{n:'起司粉',k:'bowl',c:'#FFF1C2'},
 garlic:{n:'蒜片',k:'bits',c:'#EDE0C0'},shrimp:{n:'鮮蝦',k:'shrimp'},mussel:{n:'淡菜',k:'mussel'},parsley:{n:'巴西里',k:'leaf',c:'#4E9A3A'},
 patty:{n:'牛肉排',k:'patty'},bun:{n:'漢堡麵包',k:'bun'},cheese:{n:'起司片',k:'slice',c:'#F7C548'},lettuce:{n:'生菜',k:'leaf',c:'#7CBF4A'},
 greens:{n:'綜合生菜',k:'leaf',c:'#6FAE45'},ctomato:{n:'小番茄',k:'tomato'},cucumber:{n:'小黃瓜',k:'cuke'},dressing:{n:'油醋醬',k:'bottle',c:'#E2BE5E'},
 beans:{n:'咖啡豆',k:'beans'},milk:{n:'牛奶',k:'carton',c:'#FFFFFF'},tea:{n:'紅茶葉',k:'bits',c:'#5A3218'},lemon:{n:'檸檬片',k:'lemon'},ice:{n:'冰塊',k:'ice'},soda:{n:'氣泡水',k:'bottle',c:'#BFE3F0'},syrup:{n:'莓果糖漿',k:'bottle',c:'#E2566E'},fruit:{n:'水果片',k:'fruit'},
 potato:{n:'薯條',k:'fries'},salt:{n:'鹽與胡椒',k:'shaker',c:'#FFFFFF'},truffle:{n:'黑松露',k:'truffle'},crab:{n:'蟹肉',k:'bits',c:'#F2C6B4'},burrata:{n:'布拉塔起司',k:'bowl',c:'#FFFFFF'},porcini:{n:'松露蘑菇醬',k:'bottle',c:'#4A3A2E'},marrow:{n:'烤骨髓',k:'bits',c:'#E8D7B8'},cherry:{n:'櫻桃紅酒醬',k:'bottle',c:'#7A1C2E'},uni:{n:'海膽',k:'bits',c:'#F0932B'},matcha:{n:'抹茶粉',k:'shaker',c:'#6FA84E'},oil:{n:'橄欖油',k:'bottle',c:'#C9B23A'},
 pumpkin:{n:'南瓜塊',k:'chunk'},stock:{n:'高湯',k:'bottle',c:'#E6C88C'},cream:{n:'鮮奶油',k:'carton',c:'#FFF8E8'},seeds:{n:'南瓜籽',k:'bits',c:'#4F7A35'},
 vegmix:{n:'時蔬',k:'veg'},herbs:{n:'香草鹽',k:'shaker',c:'#8DB05A'},butter:{n:'奶油',k:'slice',c:'#F8E08E'},
 duck:{n:'鴨胸',k:'duck'},orange:{n:'橙醬',k:'bottle',c:'#E8862E'},chicken:{n:'雞腿',k:'chicken'},steak:{n:'肋眼',k:'steak'},salmon:{n:'鮭魚',k:'salmon'},asparagus:{n:'蘆筍',k:'aspar'},
 arborio:{n:'燉飯米',k:'bowl',c:'#F3EAD0'},wine:{n:'白酒',k:'bottle',c:'#E9DF9A'},prosciutto:{n:'生火腿',k:'ham'},fig:{n:'無花果',k:'fig'},balsamic:{n:'巴薩米克醋',k:'bottle',c:'#3A1A1A'},
 custard:{n:'布丁液',k:'carton',c:'#F6D77E'},caramel:{n:'焦糖',k:'bottle',c:'#B8661F'},ladyfinger:{n:'手指餅乾',k:'finger'},espresso:{n:'濃縮咖啡',k:'cup'},mascarpone:{n:'馬斯卡彭',k:'bowl',c:'#F7EEDC'},cocoa:{n:'可可粉',k:'shaker',c:'#6E4226'},
 cheesebatter:{n:'乳酪糊',k:'carton',c:'#F4DFA9'},berries:{n:'莓果',k:'berry'},whites:{n:'蛋白霜',k:'carton',c:'#FFFFFF'},sugar:{n:'糖粉',k:'shaker',c:'#FFFFFF'},
 mash:{n:'奶油薯泥',k:'bowl',c:'#F3E2B6'},bread:{n:'酸種麵包',k:'bread'},scallop:{n:'干貝',k:'scallop'},
 s_redwine:{n:'紅酒醬',k:'bottle',c:'#6E1F2A'},s_lemon:{n:'檸檬奶油醬',k:'bottle',c:'#EFCF73'},s_truffle:{n:'松露醬',k:'bottle',c:'#4A3A2E'},s_yuzu:{n:'柚子胡椒醬',k:'bottle',c:'#D2BA3A'},s_pesto:{n:'青醬',k:'bottle',c:'#4F8A3A'}};
function stepShort(st){return st.t==='add'?st.items.map(i=>ING[i].n).join('、'):st.verb}
function mechN(d){return DISH(d).steps.map(stepShort).join(' → ')}
const SIG={
 base:{rice:{n:'香料米飯',p:40},mash:{n:'奶油薯泥',p:50},pasta:{n:'手工寬麵',p:60},bread:{n:'酸種麵包',p:40}},
 protein:{duck:{n:'鴨胸',p:160},beef:{n:'和牛',p:220},salmon:{n:'鮭魚',p:140},chicken:{n:'雞腿',p:100},scallop:{n:'干貝',p:180}},
 sauce:{redwine:{n:'紅酒醬',p:40,c:'#6E1F2A'},lemon:{n:'檸檬奶油',p:30,c:'#EFCF73'},truffle:{n:'松露醬',p:70,c:'#4A3A2E'},yuzu:{n:'柚子胡椒',p:40,c:'#D2BA3A'},pesto:{n:'青醬',p:30,c:'#4F8A3A'}},
 side:{asparagus:{n:'蘆筍',p:30},veg:{n:'烤蔬菜',p:30},salad:{n:'小沙拉',p:20},fries:{n:'薯條',p:20}},
};
const SIG_CAT_N={base:'主食',protein:'蛋白質',sauce:'醬汁',side:'配菜'};
/* 2.1: the signature grows with the number sold — a second and a third version of the plate, a little dearer */
const SIG_EVO=[0,40,110];function sigSold(){return S.records&&S.records.sig?S.records.sig.v:0}function sigLv(){const v=sigSold();return v>=SIG_EVO[2]?3:v>=SIG_EVO[1]?2:1}
function sigDef(){const s=S.signature;if(!s)return null;const add=SIG.base[s.base].p+SIG.protein[s.protein].p+SIG.sauce[s.sauce].p+SIG.side[s.side].p;const price=320+add+(sigLv()-1)*30;const BASE={rice:'rice',mash:'mash',pasta:'noodle',bread:'bread'},PROT={duck:'duck',beef:'steak',salmon:'salmon',chicken:'chicken',scallop:'scallop'},SIDE={asparagus:'asparagus',veg:'vegmix',salad:'greens',fries:'potato'};
 return{n:s.name,cat:'main',st:'stove',v:'pan',pan:1,price,cost:Math.round(price*.32),diff:3,pop:1,lv:2,truffle:s.sauce==='truffle'?1:0,sig:1,steps:[sA([PROT[s.protein]],0,SIG.protein[s.protein].n+'下鍋'),sZ('翻面',5,.72,.12),sZ('起鍋',4.5,.8,.11),sA([BASE[s.base],SIDE[s.side]],0,'擺上'+SIG.base[s.base].n+'與'+SIG.side[s.side].n),sH('淋'+SIG.sauce[s.sauce].n,'s_'+s.sauce,.45,.7,.55,'份量')]}}
function DISH(d){return d==='signature'?sigDef():DISHES[d]}

const TYPES={
 office:{n:'上班族',pat:.8,eat:.7,tip:.1,sens:.7,qw:.35,budget:1,read:.7,pref:{main:1.2,starter:.6,drink:1.4,dessert:.5},pD:.55,pS:.12},
 student:{n:'學生',pat:1,eat:1,tip:.04,sens:1.4,qw:.4,budget:.55,read:1,pref:{main:1.3,starter:.7,drink:.8,dessert:.8},pD:.3,pS:.2},
 gourmet:{n:'美食家',pat:1.45,eat:1.3,tip:.15,sens:.3,qw:.8,budget:1.6,read:1.4,pref:{main:1.2,starter:1.1,drink:.8,dessert:1},pD:.35,pS:.35},
 couple:{n:'情侶',pat:1.1,eat:1.25,tip:.12,sens:.8,qw:.5,budget:1.15,read:1.2,pref:{main:1,starter:.9,drink:1,dessert:2.2},pD:.45,pS:.6},
 vip:{n:'VIP',pat:.9,eat:1.1,tip:.25,sens:.2,qw:.7,budget:2.2,read:1,pref:{main:1.3},pD:.5,pS:.45},
 critic:{n:'神秘客',pat:1.1,eat:1.2,tip:.1,sens:.4,qw:.85,budget:1.5,read:1.3,pref:{},pD:.4,pS:.4},
 blogger:{n:'部落客',pat:1,eat:1.2,tip:.1,sens:.6,qw:.6,budget:1.2,read:1.2,pref:{dessert:1.6},pD:.6,pS:.5},
 regular:{n:'熟客',pat:1.3,eat:1,tip:.12,sens:.6,qw:.5,budget:1,read:.8,pref:{},pD:.4,pS:.25},
 family:{n:'一家人',pat:.9,eat:1.15,tip:.1,sens:.9,qw:.45,budget:1.05,read:1,pref:{main:1.2,starter:.8,drink:1.1,dessert:1.7},pD:.6,pS:.3},   /* 2.1: two grown-ups and a child; they take a four-top, the child watches the cats */
};
const SKIN=['#F6D3B5','#EDC19C','#E2AE88','#C98E63','#9C6644'];
const HAIR=['#2B1D16','#4A2E1F','#6B4428','#A5652F','#D8B27A','#1E1E24','#7E3B2A'];
const LOOKS={
 office:{top:['#2F3B4C','#46505C','#3E4E66','#5B4B44'],acc:['tie','tie','scarf',null],pants:'#2E2B33'},
 student:{top:['#C75B39','#4F8A6B','#E0A43A','#5B6FB3','#8C5FA8'],acc:['backpack','backpack',null],pants:'#3E4F6E'},
 gourmet:{top:['#6B3E57','#5A4632','#34495E'],acc:['beret','glasses'],pants:'#3A3030'},
 couple:{top:['#B84A5A','#4A6FA5','#E7A6A1','#6F8F5E','#D6A04A'],acc:['bow',null,null],pants:'#3B3542'},
 vip:{top:['#1F1F24','#5E1E2E','#2E2A4A'],acc:['shades'],pants:'#1B1B20'},
 family:{top:['#E0A43A','#4F8A6B','#B84A5A','#5B6FB3','#C75B39','#6F8F5E'],acc:[null,null,'scarf','glasses'],pants:'#3B3542'},
 critic:{top:['#4A4440'],acc:['hat'],pants:'#2A2826'},
 blogger:{top:['#E58FA5','#F2B84B'],acc:['phone'],pants:'#3B3542'},
 regular:{top:['#7B8B6F'],acc:[null],pants:'#3B3542'},
};
const NAMES={
 office:['陳先生','林小姐','張經理','Kevin','Amy','黃先生','吳小姐','Jason','蔡課長','Grace'],
 student:['阿哲','小安','Yuki','佳佳','阿凱','Tina','小宇','Ruby'],
 gourmet:['老饕李先生','Chloe','Emma','Monsieur 杜','品酒師 Ken'],
 couple:['Ryan 與 Ivy','阿傑與小雯','Ben 與 Lily','Sam 與 Nina','小周與阿晴'],
 vip:['周董','Madame Lin','Mr. Hart'],
 family:['王家三口','李家','張媽媽一家','陳家','小周一家','林家三口','Lin family'],
 critic:['戴帽子的客人'],
 blogger:['吃貨小琪','美食部落客 Momo'],
};
const REGS=[
 {id:'chen',n:'陳伯伯',day:2,type:'regular',size:1,fav:['friedrice','risotto'],looks:[{skin:'#EDC19C',hair:'#C9C3BA',hs:5,top:'#7B8B6F',acc:'glasses',pants:'#5A5048'}],
  l:['一份炒飯，謝謝。','Jill，今天還是老樣子。','我記得你這裡剛開幕的時候只有四張桌子。'],who:'住在附近的退休老師，每天散步都會經過。'},
 {id:'mia',n:'Mia',day:3,type:'office',size:1,fav:['coffee','tiramisu'],looks:[{skin:'#F6D3B5',hair:'#2B1D16',hs:1,top:'#3E5A7A',acc:'scarf',pants:'#2E2B33'}],
  l:['一杯咖啡，謝謝。今天好長。','Jill 主廚，今天也拜託你的咖啡續命。','每次加班完來這裡，才覺得今天有被好好對待。'],who:'樓上設計公司的設計師，永遠在趕稿。'},
 {id:'koba',n:'小林',day:4,type:'office',size:1,fav:['burger','pasta'],looks:[{skin:'#E2AE88',hair:'#1E1E24',hs:0,top:'#2F3B4C',acc:'tie',pants:'#2E2B33'}],
  l:['哪個最快？我十分鐘後要回公司。','Jill，老樣子，快快快。','我升職那天也是來這裡慶祝的，你還記得嗎？'],who:'業務員，吃飯永遠像在比賽。'},
 {id:'leo',n:'Leo',day:5,type:'student',size:1,fav:['pasta','friedrice','burger'],looks:[{skin:'#F6D3B5',hair:'#A5652F',hs:3,top:'#C75B39',acc:'backpack',pants:'#3E4F6E'}],
  l:['請問學生有優惠嗎？沒有也沒關係。','Jill 姊，我期末考考完了！','我畢業了，第一份薪水就是想來這裡吃一頓。'],who:'附近大學的學生，錢包很薄但很捧場。'},
 {id:'sophie',n:'Sophie',day:7,type:'gourmet',size:1,fav:['duck','salmon','risotto','chicken'],looks:[{skin:'#EDC19C',hair:'#6B4428',hs:2,top:'#6B3E57',acc:'beret',pants:'#3A3030'}],
  l:['讓我看看這家店有什麼本事。','Jill，今天的醬汁我想再試一次。','我寫過很多餐廳，但只有這裡，我會想一直回來。'],who:'味覺很挑剔的美食家，嘴上嚴格，心很軟。'},
 {id:'wang',n:'王先生與王太太',day:9,type:'couple',size:2,fav:['tiramisu','steak','basque'],looks:[{skin:'#E2AE88',hair:'#4A2E1F',hs:0,top:'#4A6FA5',acc:null,pants:'#2E2B33'},{skin:'#F6D3B5',hair:'#2B1D16',hs:2,top:'#B84A5A',acc:'bow',pants:'#3B3542'}],
  l:['兩位，靠窗的位子可以嗎？','Jill，我們又來約會了。','我們結婚紀念日每年都會來，這是第幾年了呢？'],who:'結婚多年、每週都約會一次的夫妻。'},
];
const REG_BY=Object.fromEntries(REGS.map(r=>[r.id,r]));
const LEVELS=[
 {n:"Jill's Little Kitchen",tables:4,menu:5,q:3},
 {n:"Jill's Bistro",tables:6,menu:7,q:4,cost:5000,rating:0},
 {n:"Jill's Restaurant",tables:8,menu:9,q:5,cost:16000,rating:3.9},
 {n:"Jill's Fine Dining",tables:10,menu:12,q:5,cost:40000,rating:4.3},
 {n:'JILL',tables:12,menu:16,q:5,cost:90000,rating:4.6},
];
const TABLE_COST=[0,0,500,800,1400,2000,2800,3800,5000,6500,8000,10000];
/* Operations: what a restaurant that cannot grow any bigger can still get better at. Each one is a real capacity or
   throughput change, bought once (or in tiers), and none of them needs a next expansion. */
/* the pieces that were bought with the room in mind now live in the projects page too */
const OPS=[
 {k:'flow',n:'動線規劃',tiers:[9000,16000,26000],lv:3,d:t=>`重新安排出菜口與桌子之間的走法：Jill 走路 +${6*t}%，員工 +${8*t}%。`},
 {k:'wait',n:'門口候位區',tiers:[12000],lv:4,d:()=>'門口多一排椅子：客滿時多等 2 組客人，少一點失望離開的人。'},
 {k:'room',n:'後場休息室',tiers:[24000],lv:5,d:()=>'後場隔出一間休息室：可以再聘 2 位員工。'},
 {k:'board',n:'大菜單板',tiers:[15000],lv:5,d:()=>'門口換一塊大菜單板：菜單上限 +2 道。'},
];
function opsLv(k){return(S.ops&&S.ops[k])||0}
/* ---- 2.0: the money ladder. Big projects change the place; street pieces change the front; the cats' things change
   what the cats do. Every entry is data: the shop, the effects and the reveal read it. ---- */
const PROJECTS=[
 {k:'terrace',n:'露天座位',cost:25000,lv:2,ic:'terrace',room:'front',d:'門口人行道上撐起陽傘，最多再放 3 張雙人桌（桌子另外買）。路過的人看得到有人在外面吃飯：客流 +5%。',done:'門口的陽傘撐起來了。',jill:'外面也可以坐了。',unlock:['露天桌位（這一頁）'],react:'小茉：「外面的桌子我來顧。」'},
 {k:'pass',n:'大出菜口',cost:15000,lv:3,ic:'pass',room:'kitchen',d:'出菜口加寬、加保溫燈：可以同時放更多盤，服務生取餐更快（反應 −15%）。',done:'出菜口變寬了，保溫燈亮著。',jill:'好，出菜。',unlock:[],react:'秀琴阿姨：「這樣端菜順多了。」'},
 {k:'cooler',n:'冷藏庫',cost:30000,lv:3,ic:'cooler',room:'kitchen',d:'後場隔出一間冷藏庫：食材容量 +80 份，備料可以一次買夠。',done:'冷藏庫裝好了，門一開一陣白霧。',jill:'終於。',unlock:[],react:'包包在冷藏庫門口坐了很久。'},
 {k:'kext',n:'廚房擴建',cost:45000,lv:3,ic:'kext',room:'kitchen',d:'爐灶換成六口的大爐（第 5、6 口爐可以在「廚房設備」加購），廚房可以再站 2 個人。',done:'新的六口爐灶進來了。',jill:'六口爐。',unlock:['爐灶第 5、6 口（廚房設備）','再聘 2 位員工'],react:'阿德師傅：「這下真的能同時做了。」'},
 {k:'side',n:'側廳',cost:60000,lv:3,ic:'side',room:'side',d:'把隔壁打通：一間有整面大窗的側廳，最多 6 張桌（前 2 張是四人卡座）；可以再聘 2 位員工、菜單上限 +2。酒櫃會搬進去。',done:'牆打通了。側廳有一整面窗，下午的光會照進來。',jill:'……店真的變大了。',unlock:['側廳桌位（這一頁）','再聘 2 位員工——桌子多了要多幾位服務生','窗邊貓架、側廳貓窩（貓的東西）'],react:'柔柔第一個走進去看了一圈。'},
];
const EXTERIOR=[
 {k:'season',n:'季節布置',cost:2000,lv:1,ic:'season',d:'燈籠、三角旗、花環，隨著日子換。'},
 {k:'bench',n:'門口長椅',cost:3000,lv:1,ic:'bench',d:'等位的客人有地方坐：門口最多再等 2 組。'},
 {k:'plants',n:'門口花箱',cost:4000,lv:1,ic:'planter',d:'兩個花箱，門口有了顏色。客流 +2%。'},
 {k:'lights',n:'門口串燈',cost:5000,lv:2,ic:'lights',d:'沿著屋簷掛一排小燈，天黑以後整條街最溫暖的一段。客流 +2%。'},
 {k:'sign',n:'招牌燈',cost:6000,lv:2,ic:'signlamp',d:'招牌上裝一盞燈，天黑以後整條街都看得到。客流 +3%。'},
 {k:'awning',n:'遮雨棚',cost:8000,lv:2,ic:'awning',d:'紅白條紋的遮雨棚。下雨天門口的人比較願意等；客流 +3%。買過之後可以換顏色。',styles:['紅白','綠白','深藍白']},
];
const CATGEAR=[
 {k:'box',n:'紙箱',cost:800,ic:'box',room:'main',x:300,y:204,poses:['sit'],d:'就是一個紙箱，放在桌子之間的走道上。柔柔會躲在裡面，等別的貓經過。',w:{mikan:4,ban:2,mei:.8,tora:.5,snow:.2}},
 {k:'cushion',n:'大睡墊',cost:1200,ic:'cushion',room:'side',need:'side',x:352,y:300,poses:['sleep','loaf','curl'],d:'一塊很厚的睡墊，放在側廳靠窗那一側。包包大概會把它當成正職。',w:{snow:4,tora:1,mikan:1.2,ban:.4,mei:.6}},
 {k:'basket',n:'藤籃',cost:1800,ic:'basket',room:'side',need:'side',x:60,y:418,poses:['curl','loaf'],d:'剛好塞得下一隻貓的藤籃，放在側廳門邊。樾樾的尺寸。',w:{tora:3,mei:1,mikan:1,snow:.6,ban:.5}},
 {k:'tunnel',n:'貓隧道',cost:2500,ic:'tunnel',room:'side',need:'side',x:150,y:420,poses:['loaf'],d:'一條會沙沙響的隧道，放在側廳。小齁會衝進去，再從另一頭衝出來。',w:{ban:4,mikan:1.5,mei:1,tora:.3,snow:.1}},
 {k:'perch',n:'窗邊貓架',cost:3500,ic:'perch',room:'side',need:'side',x:128,y:84,poses:['sit','loaf'],d:'側廳大窗前的一層貓架，看得到整條街。寶寶會在那裡看很久。',w:{mei:4,mikan:2,snow:1,tora:.8,ban:1}},
 {k:'lounge',n:'側廳貓窩',cost:4500,ic:'lounge',room:'side',need:'side',x:352,y:410,poses:['sleep','curl','belly'],d:'側廳角落一張圓圓的軟窩，下午有太陽。',w:{snow:3,tora:2,mikan:1.5,mei:1,ban:.6}},
 {k:'deluxe',n:'三層大跳台',cost:12000,ic:'deluxe',room:'main',lv:4,d:'右邊的貓跳台換成三層的大跳台：高處多 2 個位子，寶寶和包包不用再搶。',w:{}},
];
function gearOn(k){return!!(S.gear&&S.gear[k])}
function projOn(k){return!!(S.rooms&&S.rooms[k])}
function extOn(k){return!!(S.ext&&S.ext[k])}
function tablesTotal(){return S.tables+(projOn('side')?(S.sideTables||0):0)+(projOn('terrace')?(S.frontTables||0):0)}
/* the street's pull on passers-by */
function extAttract(){let m=1;if(extOn('awning'))m+=.03;if(extOn('sign'))m+=.03;if(extOn('lights'))m+=.02;if(extOn('plants'))m+=.02;if(projOn('terrace'))m+=.05;if(EXTERIOR.every(e=>extOn(e.k)))m+=.03;return m}
const SIDE_TABLE_COST=[1500,2200,3000,4000,5200,6500],FRONT_TABLE_COST=[1200,1800,2600];
/* what to save for next: one thing within reach, one a few days away, one to dream about */
function goalLadder(){const out=[];const money=S.money;const add=(n,cost,where)=>{if(cost==null)return;out.push({n,cost,where,left:Math.max(0,cost-money)})};
 for(const P of PROJECTS)if(!projOn(P.k)&&S.level>=P.lv)add(P.n,P.cost,'工程');
 for(const E of EXTERIOR)if(!extOn(E.k)&&S.level>=E.lv)add(E.n,E.cost,'工程');
 for(const G of CATGEAR)if(!gearOn(G.k)&&(!G.need||projOn(G.need))&&S.level>=(G.lv||1))add(G.n,G.cost,'貓的東西');
 const nl=LEVELS[S.level];if(nl)add('擴建：'+nl.n,nl.cost,'桌椅與擴建');
 if(S.tables<tableCap())add('餐桌',TABLE_COST[S.tables],'桌椅與擴建');
 if(projOn('side')&&(S.sideTables||0)<6)add('側廳桌',SIDE_TABLE_COST[S.sideTables||0],'工程');
 for(const E of EQUIP){const lv=S.eq[E.k]||0;if(lv<5)add(E.n+(lv?' LV'+(lv+1):''),E.cost[lv],'廚房設備')}
 for(const o of OPS){const t=opsLv(o.k);if(o.tiers[t]!=null&&S.level>=o.lv)add(o.n,o.tiers[t],'桌椅與擴建')}
 for(const Dc of DECOR){const t=S.decor[Dc.k]||0;if(Dc.tiers[t]!=null&&S.level>=(Dc.tierLv?Dc.tierLv[t]:Dc.lv))add(Dc.n,Dc.tiers[t],'裝潢')}
 out.sort((a,b)=>a.cost-b.cost);const near=out.find(g=>g.left===0)||out[0];const mid=out.find(g=>g.left>0&&g.left<=Math.max(3000,money*.6))||out.find(g=>g.left>0);const far=out.slice().reverse().find(g=>g.left>0&&g!==mid)||null;
 const G=[near,mid,far].filter((g,i,a)=>g&&a.indexOf(g)===i);for(const g of out.slice().reverse()){if(G.length>=3)break;if(!G.includes(g))G.push(g)}return G}
function goalLadderHTML(){const G=goalLadder();if(!G.length)return'';const avg=S.lastSummary?Math.max(1,S.lastSummary.net):1000;
 return`<h3>存錢的目標</h3><div class="card goals">${G.map(g=>{const pct=Math.min(100,Math.round(S.money/g.cost*100));const days=g.left>0?Math.max(1,Math.ceil(g.left/avg)):0;return`<div class="goal"><div class="gt"><span>${g.n}</span><small>${g.where}</small></div><div class="gb"><i style="width:${pct}%"></i></div><div class="gm">${g.left>0?`還差 ${fmt(g.left)}${days<=30?` · 照今天的收入約 ${days} 天`:''}`:'現在就買得起'}</div></div>`}).join('')}</div>`}
function flowMul(who){const t=opsLv('flow');return 1+(who==='jill'?.06:.08)*t}
/* Interior styles: floor, walls, baseboard and counter. Bought once, switched any time, never forced by an expansion
   (the level's own flourishes — the brass trim, the sign — stay as they are). */
const THEMES={classic:{n:'原本的樣子',d:'米色地板、灰牆，開幕那天的樣子。',cost:0,floor:'#E8E1D5',wall0:'#B6B5B0',wall1:'#A3A29D',base:'#ECE9E3',c0:'#F3F0EA',c1:'#DAD5CC',front:'#D6D2CA'},
 wood:{n:'溫暖木頭',d:'橡木地板、米黃的牆，晚上燈一開整間都是暖的。',cost:2500,floor:'#D6B58C',wall0:'#EADFC8',wall1:'#DCCFB3',base:'#C9A46A',c0:'#F1E6D2',c1:'#D9C6A6',front:'#8A6A42'},
 cream:{n:'奶油白',d:'白牆、淺色地板，乾淨明亮。',cost:2500,floor:'#F0EBE2',wall0:'#F5F1E9',wall1:'#ECE6DC',base:'#E2DCD0',c0:'#FBF8F2',c1:'#E6E1D8',front:'#E9E4DC'},
 evening:{n:'夜色',d:'深色木地板、墨綠的牆，適合晚餐時段的安靜。',cost:3500,floor:'#6B564C',wall0:'#3E4A46',wall1:'#33403C',base:'#2E2A2E',c0:'#4A4448',c1:'#3A3538',front:'#2A2528'},
 sage:{n:'淡淡的綠',d:'灰綠的牆，像有植物的房間。',cost:3000,floor:'#E3E6DA',wall0:'#C9D6C4',wall1:'#B9C8B3',base:'#DDE5D6',c0:'#F0F3EA',c1:'#CDD6C6',front:'#8FA38A'},
 modern:{n:'簡單的灰',d:'水泥色的牆、淺灰地板，什麼都不多。',cost:3000,floor:'#D8D8D6',wall0:'#9EA3A8',wall1:'#8E9398',base:'#EDEDEB',c0:'#F4F4F2',c1:'#C9CBCC',front:'#3A3A3C'}};
function TH(){return THEMES[S.theme]||THEMES.classic}
const EQUIP=[
 {k:'stove',n:'爐灶',cost:[0,900,2600,6000,13000],d:lv=>`${stoveSlots(lv)} 口爐・加熱速度 ×${SPD[lv-1].toFixed(2)}${projOn('kext')&&lv>=4?'（擴建後的大爐）':''}`},
 {k:'pan',n:'平底鍋',cost:[0,600,1600,4000,9000],d:lv=>`煎類料理速度 +${(lv-1)*8}%・Perfect 範圍 +${(lv-1)*10}%・炒飯不易焦`},
 {k:'oven',n:'烤箱',cost:[1200,1500,3500,8000,16000],d:lv=>lv?`${lv>=3?'雙門烤箱，2':'1'} 個烤位・速度 ×${SPD[lv-1].toFixed(2)}`:'爐台旁裝一台烤箱，解鎖烤類料理：松露薯條、烤雞、鮭魚…'},
 {k:'bar',n:'咖啡機',cost:[0,700,2000,5000,11000],d:lv=>lv?`${lv>=3?'雙沖煮頭，2':'1'} 個出杯位・速度 ×${SPD[lv-1].toFixed(2)}`:'工作台尾端裝一台咖啡機，解鎖飲料。'},
 {k:'fridge',n:'冰箱',cost:[0,800,2200,5000,12000],d:lv=>`食材容量 ${FRIDGE[lv-1]+(projOn('cooler')?80:0)} 份・冷盤台 ${lv>=3?2:1} 塊砧板・冷藏速度 ×${SPD[lv-1].toFixed(2)}`},
];
const SPD=[1,1.12,1.25,1.4,1.55];
const FRIDGE=[40,60,90,130,180];
const DECOR=[
 {k:'plants',n:'觀葉植物',tiers:[300,900,2000],lv:1,amb:1,d:'角落多一點綠色，客人會待得更舒服。'},
 {k:'lights',n:'暖光吊燈',tiers:[500,1500,4000],lv:1,amb:1,d:'黃銅吊燈與壁燈，晚餐時段整間店都亮起來。'},
 {k:'art',n:'牆上畫作',tiers:[600,2500],lv:1,amb:1,d:'Jill 親自挑的畫。'},
 {k:'chairs',n:'新椅子',tiers:[700,3000],lv:1,amb:1,d:'坐得舒服，客人耐心 +8%。'},
 {k:'rug',n:'手織地毯',tiers:[800],lv:2,amb:1,d:'讓用餐區更有層次。'},
 {k:'ware',n:'高級餐具',tiers:[2500],lv:2,amb:1,d:'金邊餐盤，小費 +15%。'},
 {k:'bar',n:'吧台',tiers:[4000],lv:2,amb:2,d:'酒櫃與高腳椅。飲料速度 +15%，可聘請吧台手。'},
 {k:'sofa',n:'沙發卡座',tiers:[3500,6000,12000],tierLv:[3,3,5],lv:3,amb:1,d:'把兩張桌改成四人卡座，可以接待 3–4 人團體。'},
];
const QV={P:100,G:82,O:58,B:12};
const QN={P:'PERFECT',G:'GOOD',O:'OKAY',B:'BURNT'};
const STEAK_W=['Rare','Medium Rare','Medium','Well Done'];
const STEAK_S=['R','MR','M','WD'];
const WEATHER={sun:{n:'晴朗',m:1,ic:'sun',d:'適合出門吃晚餐的好天氣。'},cloud:{n:'多雲',m:.95,ic:'cloud',d:'不冷不熱，普通的一天。'},rain:{n:'下雨',m:.82,pat:1.1,ic:'rain',d:'客人少一點、耐心多一點；熱湯和熱飲會比較好賣。'},storm:{n:'大雨',m:.66,pat:1.2,ic:'storm',d:'出門的人少，來的人會待久一點；熱的東西最受歡迎。'},hot:{n:'炎熱',m:.95,pat:.93,ic:'hot',d:'冰飲和冰甜點會賣得特別好，熱湯乏人問津。'},cool:{n:'涼爽',m:1.06,ic:'cool',d:'出門吃飯的人多一點，湯也好賣。'}};
const WX_HOT=['coffee','soup','risotto'],WX_COLD=['sparkling','fruitsoda','blacktea','pudding','basque','tiramisu'];
function wxNow(){return R?R.weather:(S.today?S.today.weather:'sun')}
/* how today's weather moves a dish's appeal (modest, legible: hot things on wet days, cold things on hot days) */
function wxDemand(d){const W=wxNow();const D=DISH(d);if(!D)return 1;let w=1;
 if(W==='rain'||W==='storm'){if(WX_HOT.includes(d))w*=W==='storm'?1.6:1.45;if(WX_COLD.includes(d)&&D.cat==='drink')w*=.7}
 if(W==='hot'){if(WX_COLD.includes(d))w*=D.cat==='drink'?1.6:1.25;if(WX_HOT.includes(d))w*=.6}
 if(W==='cool'){if(d==='soup')w*=1.25;if(D.cat==='main')w*=1.05}return w}
/* and today's occasion */
function evDemand(d){const ev=R?R.event:(S.today?S.today.event:'none');const E=EVENTS[ev];const D=DISH(d);if(!E||!D)return 1;let w=1;if(E.dem){if(E.dem[D.cat])w*=E.dem[D.cat];if(E.dem[d])w*=E.dem[d]}if(ev==='valentine'&&D.cat==='dessert')w*=2;return w}
/* dishes worth stocking up on today, for the prep screen: on the menu and clearly more wanted than on a plain day */
function wxHints(){return menuList().filter(d=>stationOk(d)&&wxDemand(d)*evDemand(d)>=1.2)}
const EVENTS={
 none:{n:'平常的一天',d:'沒有特別的事。好好做菜吧。'},
 company:{n:'附近公司聚餐',d:'晚餐客流 +30%，上班族特別多。',m:1.3},
 truffle:{n:'松露價格上漲',d:'松露料理的食材成本 ×1.5。',need:()=>S.unlocked.some(d=>DISH(d)&&DISH(d).truffle)},
 blogger:{n:'美食部落客來訪',d:'服務得好，明天可能會爆紅。'},
 valentine:{n:'今天是情人節',d:'情侶變多，甜點特別受歡迎。',m:1.12},
 concert:{n:'附近演唱會散場',d:'20:30 左右會湧進一波客人。',m:1.08},
 students:{n:'一群學生要來',d:'某個時段會一口氣來很多學生。'},
 vip:{n:'VIP 預約',d:'19:00 有 VIP 貴賓到訪，消費高、要求也高。'},
 weekend:{n:'週末晚餐',d:'出門吃飯的人多，情侶和家庭也多；甜點會比平常好賣。',m:1.15,mix:{couple:1.5,family:2},dem:{dessert:1.25}},
 datenight:{n:'約會之夜',d:'今晚情侶特別多、來得比較晚，甜點和飲料一起點的機率高。',m:1.05,mix:{couple:2.2},dem:{dessert:1.5,drink:1.2},late:true},
 market:{n:'附近的市集',d:'街上有市集，早一點就會有人進來；學生和上班族都多。',m:1.12,mix:{student:1.5,office:1.3},early:true},
 fresh:{n:'漁獲新鮮',d:'今天海鮮進貨便宜又新鮮：海鮮類料理成本 ×0.7，客人也更想點。',costMul:{seafood:.7,salmon:.7},dem:{seafood:1.4,salmon:1.4},need:()=>S.unlocked.includes('seafood')||S.unlocked.includes('salmon')},
 celebrate:{n:'店慶',d:'開店滿十天的日子。熟客都會想來，客人也比平常多一點。',m:1.15,regs:1},
};
const RV={
 5:['Jill 主廚的{d}真的太厲害了。','{d}完美。我要把這家店藏起來不告訴別人。','燈光、音樂、{d}，今晚被 Jill 治癒了。','Chef Jill 是天才，這句不是誇飾。','每一口都像被好好照顧。一定會再來。','我在{d}前安靜了三秒，然後吃光了。'],
 4:['等了一下，但值得。','{d}很好吃，店裡氣氛也很舒服。','Jill 很忙但出餐很穩，推。','小小的店，大大的用心。','{d}有水準，下次想試招牌。'],
 3:['{d}還可以，下次想試別的。','普普通通，但 Jill 主廚的笑容加分。','人有點多，味道中規中矩。','不錯吃，就是等得有點久。'],
 2:['我的{d}差點等到退休。','Jill 本人好像忙到分身乏術。','{d}有點焦，但我相信下次會更好。','價格有點勇敢。'],
 1:['等到我開始懷疑人生。','餓著肚子離開了，Jill 下次見。','今天運氣不好，沒吃到就走了。','在門口的長椅上等到跟隔壁的陌生人變朋友。'],
};
const ACH=[
 {id:'first',n:'First Perfect',d:'做出第一道 Perfect 料理',ic:'star'},
 {id:'rush',n:'Dinner Rush',d:'一天內服務 10 位客人',ic:'flame'},
 {id:'fire',n:"Jill's On Fire",d:'第一次進入 Rush Mode',ic:'flame'},
 {id:'perfectnight',n:'Perfect Night',d:'整晚沒有料理失敗（至少 8 道、無人生氣離開）',ic:'moon',p:1},
 {id:'combo10',n:'Ten in a Row',d:'達成 COMBO ×10',ic:'star',p:1},
 {id:'sig',n:'Signature Born',d:'研發出 Jill 的招牌菜',ic:'plate',p:1},
 {id:'duck',n:"Jill's Signature",d:'香煎鴨胸熟練度滿級',ic:'duck',p:2},
 {id:'oldfriend',n:'Old Friend',d:'有熟客成為 Jill 的老客人',ic:'heart',p:2},
 {id:'loves',n:'Everybody Loves Jill',d:'服務 100 位回頭客',ic:'heart',p:2},
 {id:'critic',n:"Critic's Choice",d:'讓神秘美食評論家給出五星',ic:'pen',p:1},
 {id:'chef',n:'Chef Jill',d:'餐廳評分達到五星（4.75 以上，至少 20 則評論）',ic:'crown',p:2},
 {id:'jill',n:'JILL',d:'餐廳擴建到最高等級',ic:'crown',p:2},
 {id:'million',n:'First Million',d:'累積收入達到 $1,000,000',ic:'coin',p:2},
 /* early */
 {id:'week',n:'One Week',d:'連續營業七天',ic:'moon',p:0},{id:'hire',n:'First Hire',d:'聘請第一位員工',ic:'waiter',p:0},{id:'bistro',n:'Bistro',d:"擴建為 Jill's Bistro",ic:'crown',p:0},{id:'lab',n:'Kitchen Lab',d:'在實驗室試出一道新料理',ic:'plate',p:0},{id:'menu8',n:'Eight Dishes',d:'菜單上同時有 8 道菜',ic:'plate',p:0},{id:'star3',n:'Three Stars',d:'把一道料理升到三星',ic:'star',p:0},{id:'regular4',n:'Familiar Face',d:'第一位客人成為熟客',ic:'heart',p:0},{id:'caught',n:'Not Today',d:'抓到偷食材的小偷',ic:'flame',p:0},{id:'rowdy',n:'Peacemaker',d:'安撫一位鬧事的客人',ic:'heart',p:0},{id:'inspect',n:'Spotless',d:'衛生檢查滿分通過',ic:'star',p:0},
 /* mid */
 {id:'taught',n:'Passed On',d:'把招牌菜交給一位 LV5 廚師',ic:'plate',p:1},{id:'usual',n:'The Usual',d:'Jill 記得一位熟客的老樣子',ic:'heart',p:1},{id:'gift',n:'Something From Home',d:'熟客帶了東西來給店裡',ic:'heart',p:1},{id:'company',n:'Not Alone Today',d:'熟客第一次帶人來',ic:'heart',p:1},{id:'treat',n:'On The House',d:'Jill 請了客人一份',ic:'plate',p:1},{id:'dylan5',n:'Him Again',d:'Dylan 第五次來店',ic:'heart',p:1},{id:'jillrest',n:'A Moment',d:'營業中 Jill 在沙發上坐了一下',ic:'moon',p:1},{id:'everyone',n:'All Five',d:'五隻貓同時出現在一張照片裡',ic:'heart',p:1},{id:'lap',n:'Lap Cat',d:'有貓跳上 Jill 的膝蓋',ic:'heart',p:1},{id:'play',n:'Playtime',d:'小齁跟柔柔玩起來了',ic:'heart',p:1},{id:'photos50',n:'Fifty Photos',d:'相簿累積 50 張照片',ic:'pen',p:1},{id:'rain',n:'Rainy Day Soup',d:'下雨天賣出 6 碗以上的湯',ic:'moon',p:1},{id:'hot',n:'Ice Cold',d:'炎熱的一天賣出 12 杯以上的冰飲',ic:'flame',p:1},{id:'celebrate',n:'Ten Days',d:'過了第一次店慶',ic:'crown',p:1},{id:'datenight',n:'Date Night',d:'約會之夜接待 5 對情侶',ic:'heart',p:1},{id:'rev20k',n:'Twenty Thousand',d:'單日營業額達到 $20,000',ic:'coin',p:1},{id:'noshort',n:'Nothing Missing',d:'一天 30 位客人以上、一次都沒有臨時叫貨',ic:'star',p:1},{id:'rating45',n:'Four and a Half',d:'評分達到 4.5（至少 20 則評論）',ic:'star',p:1},
 /* mature */
 {id:'guests60',n:'Full House',d:'一天接待 60 位客人',ic:'flame',p:2},{id:'calm7',n:'Calm Week',d:'連續七天沒有客人生氣離開',ic:'moon',p:2},{id:'storm',n:'Come Rain Or Shine',d:'大雨天還是接待了 15 位客人',ic:'moon',p:2},{id:'night0',n:'No One Waits',d:'一天 20 位客人以上、沒有人等到不耐煩',ic:'star',p:2},{id:'staff6',n:'Full Crew',d:'同時有 6 位員工',ic:'waiter',p:2},{id:'lv5all',n:'Veterans',d:'三位以上員工全部滿級',ic:'crown',p:2},{id:'ops3',n:'Well Oiled',d:'動線規劃升到最高',ic:'star',p:2},{id:'room',n:'Back Room',d:'蓋了後場休息室',ic:'crown',p:2},{id:'sig100',n:'A Hundred Plates',d:'招牌菜賣出 100 份',ic:'duck',p:2},{id:'keep10',n:'Curator',d:'珍藏 10 張照片',ic:'pen',p:2},
 /* 2.1: the plate */
 {id:'special',n:'The Finer Version',d:'研發第一道特製版',ic:'plate',p:2},{id:'specials4',n:'Chef\'s Table',d:'菜單上有四道特製版',ic:'crown',p:2},{id:'walkin',n:'Passing By',d:'路人在門口看了一下就進來，累計 20 次',ic:'signlamp',p:1},{id:'families',n:'Family Table',d:'招待了 10 組帶小孩來的家庭',ic:'heart',p:1},{id:'sig2',n:'Second Plating',d:'招牌菜賣到第二版',ic:'star',p:2},{id:'sig3',n:'The Signature, Perfected',d:'招牌菜賣到第三版',ic:'crown',p:3},
 /* 2.0: the place grows */
 {id:'project',n:'Under Construction',d:'完成第一個大工程',ic:'expand',p:2},{id:'allprojects',n:'The Whole Block',d:'露天座位、大出菜口、冷藏庫、廚房擴建、側廳——全部完工',ic:'crown',p:2},{id:'storefront',n:'Curb Appeal',d:'門口的每一樣東西都裝好了',ic:'lights',p:2},{id:'catgear',n:'Spoiled',d:'買齊了所有貓的東西',ic:'heart',p:2},{id:'newspot',n:'It Was Their Idea',d:'一隻貓第一次用了你買給牠的東西',ic:'heart',h:1},{id:'sideful',n:'Both Rooms',d:'側廳和用餐區同時坐滿',ic:'flame',p:2},{id:'terrace',n:'Al Fresco',d:'第一組客人坐在陽傘下吃完了一餐',ic:'star',p:2},
 /* hidden: things that happen on their own */
 {id:'anniv',n:'Anniversary',d:'王先生與王太太在店裡過了紀念日',ic:'heart',h:1},{id:'pause',n:'Passing By',d:'Jill 在 Dylan 的桌邊停了一下',ic:'heart',h:1},{id:'husband',n:'All Along',d:'原來一直都認識',ic:'heart',h:1},{id:'dylancat',n:'The Cats Know',d:'貓對 Dylan 的態度不像對陌生人',ic:'heart',h:1},{id:'bagcat',n:'The Bag',d:'包包對袋子比橘子有興趣',ic:'heart',h:1},{id:'neighbors',n:'Small World',d:'兩位熟客在店裡認出了彼此',ic:'heart',h:1},{id:'writer',n:'In Print',d:'寫專欄的朋友給了好評',ic:'pen',h:1},{id:'oddspot',n:'Why There',d:'有貓睡在一個奇怪的地方',ic:'moon',h:1},{id:'sleepgod',n:'Sleeps Through Anything',d:'店裡再吵，包包照睡',ic:'moon',h:1},
];
/* photos the game kept by itself (the first of a kind) do not count towards the player's own curation */
function MEMS_FIRST(p){const A=albumList();return A.find(x=>x.kind===p.kind)===p}
const ACH_BY_MEMO={everyone:'everyone',lap:'lap',play:'play',swat:'play',rest:'jillrest',pause:'pause',dylancat:'dylancat',bagcat:'bagcat',oddspot:'oddspot',sleepgod:'sleepgod',anniversary:'anniv',neighbors:'neighbors',company:'company',gift:'gift'};
const COACH=[
 '客人來了！有空桌的話他們會自己入座；客滿時會先在門口的長椅坐一下，等桌子空出來。',
 '客人在看菜單。等桌上出現「!」，點那張桌子幫他們點餐。',
 '訂單來了！點上方訂單條裡的炒飯（或到廚房點爐台），開始做菜。',
 '照著料理台做：先點「雞蛋」、再點「白飯」下鍋，Jill 會自己翻炒。翻炒完記得回來淋醬油。',
 '炒飯好了，放在出菜口。點那張桌子，Jill 會端過去。',
 '客人開動了。吃完會出現金幣，點桌子收錢。',
 '最後點桌子收拾乾淨，就能接下一組客人。',
 '做得好，Chef Jill！就這樣一路做到打烊吧。',
];

/* ================= save / state ================= */
const KEY='jills-kitchen-save-v1';
function newState(){return{v:1,day:1,phase:'prep',money:500,lifetime:0,level:1,
 eq:{stove:1,oven:0,bar:0,prep:0,fridge:1,pan:1},tables:2,
 decor:{plants:0,lights:0,art:0,chairs:0,rug:0,ware:0,bar:0,sofa:0},staff:{busser:false,bartender:false},mem:{},catFam:{},crew:[],crewMig:1,rstar:{},dylan:{stage:0,stay:0,reveal:0,last:0,clues:{}},life:{sofa:0,tv:0},checkpoint:null,savedAt:0,savedLabel:'',rdProg:{},rdDone:{},labKnown:{},labTried:{},album:null,notes:[],taught:0,ops:{},theme:'classic',themes:{classic:1},sets:{},rooms:{side:0,terrace:0,kext:0,cooler:0,pass:0},sideTables:0,frontTables:0,ext:{awning:0,sign:0,plants:0,lights:0,bench:0,season:0},gear:{},gearUse:{},newRooms:{},reveal:null,rhist:[],records:{},salesHist:{},menuSince:{},regMem:{},props:{},regDay:null,gourmetBoost:0,dayLog:[],dayLogDay:0,
 unlocked:['friedrice'],menu:['friedrice'],price:{},stock:{},xp:{},reviews:[],achievements:{},regulars:{},returning:0,
 signature:null,catNames:{},buzz:1,buzzMsg:'',stats:{guests:0,perfect:0,days:0},tut:0,gate:1,news:[],today:null,todayCost:0,lastSummary:null,sfx:true,music:true}}
let S;
/* How saves stay compatible (details: docs/ARCHITECTURE.md)
   - NEW field: just add it to newState(). load() gives old saves every missing top-level field
     from newState(), and merges eq/decor/staff/stats key by key.
   - CHANGED data (rename a field, convert a format, rename an id): bump SAVE_V and add
     MIGRATE[old version]=o=>{...}. Steps run in order, oldest first, before the defaults are filled.
   - Never rename or delete ids that saves store (dish ids, cat ids, memory ids, crew roles).
   - A save this code cannot read (broken JSON, unknown or newer version) is copied to RESCUE_KEY
     before the game starts fresh, so the next save() can never destroy it. */
const SAVE_V=1;
const MIGRATE={};
const RESCUE_KEY=KEY+'-unreadable';
function rescue(t,why){try{if(!localStorage.getItem(RESCUE_KEY))localStorage.setItem(RESCUE_KEY,t);console.warn(`[save] could not read the save (${why}); a copy was kept in localStorage["${RESCUE_KEY}"]`)}catch(e){}}
function fillDefaults(o){const base=newState();for(const k in base)if(!(k in o))o[k]=base[k];for(const k of['eq','decor','staff','stats','ops','rooms','ext','gear','gearUse','newRooms'])o[k]=Object.assign({},base[k],o[k]);return o}
// Old bartender/busser -> crew. NOTE: fillDefaults() runs first and already sets crewMig from newState(),
// so this conversion never fires. Kept exactly as it was to preserve current behaviour (see docs/REFACTOR_REPORT.md).
function legacyCrew(o){if(!o.crewMig){o.crewMig=1;o.crew=o.crew||[];if(o.staff&&o.staff.busser)o.crew.push({id:'c1',role:'cleaner',name:'秀琴阿姨',lv:1,duty:'clean'});if(o.staff&&o.staff.bartender)o.crew.push({id:'c2',role:'chef',name:'小茉',lv:1,duty:'bar'})}return o}
/* Text -> a playable save, or {err}. Used for the browser's own copy and for backup files alike:
   parse -> is it one of ours -> version -> migrations -> defaults -> sanity checks. Nothing here
   touches S or localStorage. */
const BACKUP_APP='jills-kitchen';
function parseSave(t){let o;try{o=JSON.parse(t)}catch(e){return{err:'notjson'}}
 let photos=null;if(o&&typeof o==='object'&&o.app===BACKUP_APP&&o.save&&typeof o.save==='object'){if(o.photos&&typeof o.photos==='object')photos=o.photos;o=o.save}   /* a backup file wraps the save (and its pictures) */
 else if(o&&typeof o==='object'&&typeof o[KEY]==='string'){try{o=JSON.parse(o[KEY])}catch(e){return{err:'notjson'}}}   /* a raw localStorage dump */
 if(!o||typeof o!=='object'||Array.isArray(o))return{err:'notsave'};
 if(typeof o.v!=='number'||o.v%1)return{err:'notsave'};
 if(!(typeof o.day==='number'&&typeof o.money==='number'&&Array.isArray(o.unlocked)&&Array.isArray(o.menu)))return{err:'notsave'};
 if(o.v<1)return{err:'notsave'};if(o.v>SAVE_V)return{err:'newer',v:o.v};
 try{for(let n=o.v;n<SAVE_V;n++){MIGRATE[n](o);o.v=n+1}o=legacyCrew(fillDefaults(o))}catch(e){return{err:'broken'}}
 if(!(o.day>=1&&isFinite(o.money)&&o.unlocked.every(d=>typeof d==='string')&&o.menu.every(d=>typeof d==='string')&&Array.isArray(o.crew)&&o.dylan&&typeof o.dylan==='object'))return{err:'broken'};
 o.day=Math.max(1,Math.floor(o.day));o.money=Math.round(o.money);return{o,photos}}
function load(){let t=null;try{t=localStorage.getItem(KEY)}catch(e){return null}if(!t)return null;
 const r=parseSave(t);if(r.err){rescue(t,r.err+(r.v?' '+r.v:''));return null}return r.o}
let saveWarned=false;
function backupName(){const d=new Date(),p=n=>String(n).padStart(2,'0');return `JillsKitchen_Save_${d.getFullYear()}-${p(d.getMonth()+1)}-${p(d.getDate())}_${p(d.getHours())}${p(d.getMinutes())}_Day${S.day}.json`}
function backupText(photos){return JSON.stringify({app:BACKUP_APP,kind:'save',v:S.v,exported:new Date().toISOString(),save:S,photos:photos||{}},null,1)}
function exportSave(){if(phase==='service'&&!paused){toast('先暫停再備份');return false}if(phase==='service'&&R&&R.closing==null)checkpointSave('backup');else save();const name=backupName();photoAll().then(ph=>exportWith(name,backupText(ph)));return true}
function exportWith(name,text){
 const direct=()=>{try{const blob=new Blob([text],{type:'application/json'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),4000);toast('已備份存檔：'+name);return true}catch(e){toast('這個瀏覽器無法下載檔案');return false}};
 /* inside the claude.ai viewer a page cannot download by itself; the host saves the file for us */
 const host=window.claude&&typeof window.claude.use==='function';if(!host)return direct();
 toast('準備備份檔…');window.claude.use('downloads').then(d=>{if(!d){direct();return}return d.save({filename:name,data:text}).then(()=>toast('已備份存檔：'+name),e=>{if(e&&e.code==='declined')return;direct()})}).catch(direct);return true}
function copyBackup(){if(phase==='service'&&!paused){toast('先暫停再備份');return}if(phase==='service'&&R&&R.closing==null)checkpointSave('backup');else save();photoAll().then(ph=>copyWith(backupText(ph)))}
function copyWith(text){
 const done=()=>toast('備份文字已複製，貼到備忘錄或訊息裡留著；之後用「貼上備份文字恢復」讀回來');
 const fallback=()=>{try{const ta=document.createElement('textarea');ta.value=text;ta.style.position='fixed';ta.style.opacity='0';document.body.appendChild(ta);ta.focus();ta.select();const ok=document.execCommand&&document.execCommand('copy');ta.remove();if(ok)done();else toast('這個瀏覽器不讓網頁複製文字，請改用「備份到檔案」')}catch(e){toast('這個瀏覽器不讓網頁複製文字，請改用「備份到檔案」')}};
 if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(text).then(done,fallback);else fallback()}
const IMPORT_MSG={notjson:'這不是 Jill\'s Kitchen 的存檔檔案（無法讀取內容）',notsave:'這不是 Jill\'s Kitchen 的存檔檔案',newer:'這個存檔來自比較新的版本，目前的遊戲讀不了',broken:'這個存檔檔案已經損壞，無法讀取'};
let pendingImport=null,pendingPhotos=null;
function importSaveText(t){const r=parseSave(t);if(r.err){pendingImport=null;toast(IMPORT_MSG[r.err]+'。目前的進度沒有改變');if(sub==='settings'||sub==='pause')showSettings();return false}pendingImport=r.o;pendingPhotos=r.photos;if(sub==='pause')sub='settings';showSettings();return true}
function importConfirm(){const o=pendingImport;if(!o)return;const ph=pendingPhotos;pendingImport=null;pendingPhotos=null;if(phase==='service'&&!paused){toast('先暫停再讀取存檔');return}paused=false;
 S=o;PHOTOS.clear();if(ph){for(const p of albumList())if(!p.img&&ph[p.id])p.img=ph[p.id]}photoMigrate();save();R=null;ICACHE.clear();DCACHE.clear();IDLE=null;bg=null;lifeReset();setAudio();sub=null;resetStep=0;toast(`已讀取存檔：DAY ${S.day}`);showTitle()}
function pickImportFile(){if(phase==='service'&&!paused){toast('先暫停再讀取存檔');return}let inp=$('#importFile');
 if(!inp){inp=document.createElement('input');inp.type='file';inp.id='importFile';inp.accept='.json,application/json,text/plain';inp.hidden=true;document.body.appendChild(inp);
  inp.addEventListener('change',()=>{const f=inp.files&&inp.files[0];inp.value='';if(!f)return;if(f.size>40e6){toast(IMPORT_MSG.notsave+'。目前的進度沒有改變');return}const fr=new FileReader();fr.onload=()=>importSaveText(String(fr.result||''));fr.onerror=()=>toast('讀取檔案失敗。目前的進度沒有改變');fr.readAsText(f)})}
 inp.click()}
function save(){try{S.savedAt=Date.now();S.savedLabel=`DAY ${S.day} · ${R&&phase==='service'?clockStr():(phase==='service'?'17:00':'打烊後')}`;localStorage.setItem(KEY,JSON.stringify(S));return true}catch(e){if(!saveWarned){saveWarned=true;console.warn('[save] saving failed',e)}return false}}
function hasSave(){try{return!!localStorage.getItem(KEY)}catch(e){return false}}
S=load()||newState();

/* ================= derived ================= */
const stoveSlots=lv=>[1,2,3,3,4][lv-1]+(projOn('kext')?Math.min(2,Math.max(0,lv-3)):0);   /* the six-burner range of the kitchen expansion: LV4 → 5, LV5 → 6 */
const LV=()=>LEVELS[S.level-1];
const tableCap=()=>LV().tables;
const menuCap=()=>LV().menu+2*opsLv('board')+(projOn('side')?2:0);
const fridgeCap=()=>FRIDGE[S.eq.fridge-1]+(projOn('cooler')?80:0);
function ambience(){let a=0;for(const d of DECOR)a+=(S.decor[d.k]||0)*d.amb;return a+(S.level-1)}
function rating(){const r=S.reviews.slice(-Math.max(40,tablesTotal()*4));let s=3*4,n=4;for(const v of r){const w=v.w||1;s+=v.s*w;n+=w}return s/n}   /* a bigger place is judged over more visits, so one hard evening does not swing it */
function xpLv(x){return x>=55?5:x>=28?4:x>=12?3:x>=4?2:1}
const XP_T=[0,4,12,28,55];
function mLv(d){return xpLv(S.xp[d]||0)}
function priceOf(d){const D=DISH(d);return Math.round(D.price*(1+.15*(starOf(d)-1))*(S.price[d]||1)/5)*5}
function costOf(d){const D=DISH(d);let c=D.cost;if(S.today&&S.today.event==='truffle'&&D.truffle)c*=1.5;const E=S.today&&EVENTS[S.today.event];if(E&&E.costMul&&E.costMul[d])c*=E.costMul[d];return Math.round(c)}
function stockTotal(){let t=0;for(const k in S.stock)t+=S.stock[k]||0;return t}
function stSpeed(type){const lv=type==='stove'?S.eq.stove:type==='oven'?Math.max(1,S.eq.oven):type==='bar'?Math.max(1,S.eq.bar):S.eq.fridge;let v=SPD[clamp(lv,1,5)-1];if(type==='bar'&&S.decor.bar)v*=1.15;if(R&&R.fire>0)v*=1.4;return v}
function dishSpeed(d,type){const D=DISH(d);let v=stSpeed(type);if(D.pan)v*=1+.08*(S.eq.pan-1);return v/(1-.07*(mLv(d)-1))}
function menuList(){const m=S.menu.filter(d=>S.unlocked.includes(d));if(S.signature&&!m.includes('signature'))m.unshift('signature');return m}
function maxSeats(tables){return(tables||buildTables()).reduce((a,t)=>Math.max(a,t.seats),2)}
function dayDur(D){return D===1?150:D===2?170:D===3?190:D<=5?210:D<=9?230:250}
function feat(){const D=S.day;return{prices:D>=2,stock:true,events:D>=3,rush:D>=4}}

/* ================= layout of the room ================= */
const LW=400;let LH=424,DY=0,FB=364,KB=0,FY=0;   /* KB: extra kitchen-band height on tall screens (bigger chefs, taller stations) */let PSC=1.24,CSC=1.32;
const COLS=[110,186,262,338],RSH=[0,-16,0];let ROWS=[162,240,318];
const SPOT_ORDER=[5,6,9,10,1,2,4,7,8,11,0,3];
/* ---- 2.0: rooms. The restaurant is four spaces drawn one at a time; the simulation runs in all of them. Every moving
   thing carries .room, and a target in another room is reached through a doorway (all doorways lead to the dining room). ---- */
const ROOMS={main:{n:'用餐區'},kitchen:{n:'廚房'},side:{n:'側廳'},front:{n:'店門口'}};
let room='main';
const SIDE_L={door:{x:70,y:100},arch:{x:48,y:8,w:44},cols:[104,200,296],rows:[196,318],window:{x:118,y:10,w:180,h:64},cat:{x:352,y:120}};   /* the side dining room: its door is an arch on the back wall, left */
const SIDE_ARCH={x:344,y:12,w:40};   /* the arch to the side room, on the dining room's back wall, right */
const FR={door:{x:200,y:262},walk:300,enter:{x:-24,y:300},exit:{x:424,y:300},cols:[96,304,200],row:352,bench:{x:350,y:262},sun:{x:48,y:266}};   /* the street outside */
const KD={x:64,y:0};   /* the kitchen door in the dining room: at the left end of the counter (y filled from FB) */
const KR={get door(){return{x:200,y:LH-30}},get fridge(){return{x:318,y:LH-112,w:52,h:80}},get cooler(){return{x:44,y:LH-112,w:48,h:80}}};   /* the kitchen: the fridge and the cold room stand on the pickup side, the door to the dining room between them */
function roomOpen(k){return k==='main'||k==='kitchen'||k==='front'||(k==='side'&&!!(S.rooms&&S.rooms.side))}
function doorway(a,b){const kd={x:KD.x,y:FB-8};
 if(a==='main'){if(b==='side')return[[SIDE_ARCH.x+SIDE_ARCH.w/2,100],[SIDE_L.door.x,SIDE_L.door.y]];if(b==='front')return[[DOOR.x,DOOR.y+4],[FR.door.x,FR.door.y]];if(b==='kitchen')return[[kd.x,kd.y],[KR.door.x,KR.door.y]]}
 if(b==='main'){if(a==='side')return[[SIDE_L.door.x,SIDE_L.door.y],[SIDE_ARCH.x+SIDE_ARCH.w/2,100]];if(a==='front')return[[FR.door.x,FR.door.y],[DOOR.x,DOOR.y+4]];if(a==='kitchen')return[[KR.door.x,KR.door.y],[kd.x,kd.y]]}
 return null}
function nextHop(a,b){return(a==='main'||b==='main')?b:'main'}
/* one movement step for anything with x,y,room and a target tx,ty,troom; through doorways when needed. Returns true on arrival. */
function stepTo(e,v){const tr=e.troom||e.room||'main';if(!e.room)e.room='main';let tx=e.tx,ty=e.ty;let hop=null;
 if(tr!==e.room){hop=nextHop(e.room,tr);const dw=doorway(e.room,hop);if(!dw){e.room=tr;return false}tx=dw[0][0];ty=dw[0][1]}
 const dx=tx-e.x,dy=ty-e.y,d=Math.hypot(dx,dy);
 if(d<=v){e.x=tx;e.y=ty;if(hop){const dw=doorway(e.room,hop);e.room=hop;e.x=dw[1][0];e.y=dw[1][1];return false}return true}
 e.x+=dx/d*v;e.y+=dy/d*v;if(Math.abs(dx)>.5)e.face=dx>=0?1:-1;return false}
function sendOut(g){g.troom='front';g.tx=FR.exit.x;g.ty=FR.exit.y}
const DOOR={x:53,y:104};
const PASS={x:200,y:360};
/* Waiting area: a small wooden bench under the door, three places, plus two standing spots beside it
   for bigger parties or when the bench is taken. Cats may use an empty place (one cat at a time,
   never the last free one while someone is waiting), so places are reserved, not indexed. */
const BENCH={x:62,w:28,gx:58,seats:[156,196,236],stand:[{x:100,y:200},{x:100,y:240}]};
function benchFree(i){return !OCC['bench'+i]&&!(R&&R.groups.some(g=>g.spot&&g.spot.k==='seat'&&g.spot.i===i&&(g.state==='queue'||g.state==='arrive')))}
function standFree(i){return !(R&&R.groups.some(g=>g.spot&&g.spot.k==='stand'&&g.spot.i===i&&(g.state==='queue'||g.state==='arrive')))}
function spotPos(sp){return sp.k==='seat'?{x:BENCH.gx,y:BENCH.seats[sp.i]}:BENCH.stand[sp.i]}
function pickSpot(g){if(g.size<=2){for(let i=0;i<3;i++)if(benchFree(i))return{k:'seat',i}}for(let i=0;i<2;i++)if(standFree(i))return{k:'stand',i};if(g.size>2){for(let i=0;i<3;i++)if(benchFree(i))return{k:'seat',i}}return null}
function isSeated(g){return g.state==='queue'&&!g.moving&&!!g.spot&&g.spot.k==='seat'}
function buildTables(){const out=[];const sofa=S.decor.sofa*2;for(let i=0;i<S.tables;i++){const sp=SPOT_ORDER[i];const r=Math.floor(sp/4),c=sp%4;out.push({i,spot:sp,x:COLS[c]+RSH[r],y:ROWS[r],seats:i<sofa?4:2,group:null,dirty:false,plates:[],busT:0,room:'main'})}
 const nS=(S.rooms&&S.rooms.side)?(S.sideTables||0):0;for(let k=0;k<nS;k++){const r=Math.floor(k/3),c=k%3;out.push({i:out.length,spot:100+k,x:SIDE_L.cols[c],y:SIDE_L.rows[r]+(r?DY*.5:0),seats:k<2?4:2,group:null,dirty:false,plates:[],busT:0,room:'side'})}
 const nF=(S.rooms&&S.rooms.terrace)?(S.frontTables||0):0;for(let k=0;k<nF;k++)out.push({i:out.length,spot:200+k,x:FR.cols[k],y:FR.row,seats:2,group:null,dirty:false,plates:[],busT:0,room:'front',out:true});
 return out}
function buildSlots(){const a=[];const add=(t,n)=>{for(let i=0;i<n;i++)a.push({type:t,no:i+1,job:null,fx:null,flash:0})};
 add('stove',stoveSlots(S.eq.stove));if(S.eq.oven)add('oven',S.eq.oven>=3?2:1);if(S.eq.bar)add('bar',S.eq.bar>=3?2:1);if(S.eq.prep)add('prep',S.eq.fridge>=3?2:1);return a}
function seatPos(t){return t.seats===4?[{dx:-14,dy:-15,side:0},{dx:14,dy:-15,side:0},{dx:-36,dy:2,side:-1},{dx:36,dy:2,side:1}]:[{dx:-25,dy:0,side:-1},{dx:25,dy:0,side:1}]}

/* ================= food art ================= */
function leaf(c,x,y,l,w,a,col){c.save();c.translate(x,y);c.rotate(a);c.fillStyle=col;c.beginPath();c.moveTo(-l/2,0);c.quadraticCurveTo(0,-w,l/2,0);c.quadraticCurveTo(0,w,-l/2,0);c.fill();c.strokeStyle='rgba(255,255,255,.28)';c.lineWidth=.6;c.beginPath();c.moveTo(-l/2+1,0);c.lineTo(l/2-1,0);c.stroke();c.restore()}
function stick(c,x,y,l,w,a,col,edge){c.save();c.translate(x,y);c.rotate(a);c.fillStyle=edge||col;rr(c,-l/2,-w/2,l,w,w/2.4);c.fill();c.fillStyle=col;rr(c,-l/2+.7,-w/2+.6,l-1.4,w-1.8,w/3);c.fill();c.restore()}
function gloss(c,x,y,rx,ry,a){c.fillStyle=`rgba(255,255,255,${a||.35})`;el(c,x,y,rx,ry)}
function drawPlate(c,gold,k){k=k||1;c.save();c.scale(k,k*.8);c.fillStyle='rgba(70,40,20,.22)';el(c,2,7,47,46);
 let g=c.createRadialGradient(-12,-14,4,0,0,46);g.addColorStop(0,'#FFFFFF');g.addColorStop(.72,'#F6F1E8');g.addColorStop(1,'#D8CEBE');c.fillStyle=g;el(c,0,0,46,46);
 c.fillStyle='#FBF8F2';el(c,0,1,33,33);c.strokeStyle='rgba(120,90,60,.13)';c.lineWidth=1.2;c.beginPath();c.arc(0,1,33.5,0,7);c.stroke();
 if(gold){c.strokeStyle='#C99A45';c.lineWidth=2;c.beginPath();c.arc(0,0,42.5,0,7);c.stroke()}c.restore()}
function drawBowl(c,gold){c.save();c.scale(1,.8);c.fillStyle='rgba(70,40,20,.22)';el(c,2,8,44,43);let g=c.createRadialGradient(-10,-12,4,0,0,42);g.addColorStop(0,'#FFFFFF');g.addColorStop(1,'#DCD2C2');c.fillStyle=g;el(c,0,0,42,42);c.fillStyle='#E9E1D4';el(c,0,2,34,33);if(gold){c.strokeStyle='#C99A45';c.lineWidth=2;c.beginPath();c.arc(0,0,39,0,7);c.stroke()}c.restore()}
function drawCoaster(c){c.fillStyle='rgba(70,40,20,.22)';el(c,2,40,30,9);c.fillStyle='#B98A5A';el(c,0,38,28,8);c.fillStyle='#CFA170';el(c,0,37,25,6.6)}
function riceMound(c,R,x,y,r){let g=c.createRadialGradient(x-r*.25,y-r*.3,2,x,y,r);g.addColorStop(0,'#FCE7A8');g.addColorStop(1,'#D69D3F');c.fillStyle=g;el(c,x,y,r,r*.95);
 const cols=['#FFF2C9','#F3D07C','#E6B658','#FBE6AE'];for(let i=0;i<r*3.2;i++){const a=R()*6.283,d=Math.sqrt(R())*r*.9;c.save();c.translate(x+Math.cos(a)*d,y+Math.sin(a)*d);c.rotate(R()*3);c.fillStyle=cols[Math.floor(R()*4)];el(c,0,0,r*.11,r*.055);c.restore()}
 for(let i=0;i<10;i++){const a=R()*6.283,d=R()*r*.75;const ex=x+Math.cos(a)*d,ey=y+Math.sin(a)*d;c.fillStyle=R()<.55?'#FFCF3A':'#FFF3D0';el(c,ex,ey,r*.16,r*.11);c.fillStyle='rgba(255,255,255,.45)';el(c,ex-r*.04,ey-r*.03,r*.06,r*.03)}
 for(let i=0;i<7;i++){const a=R()*6.283,d=R()*r*.8;c.fillStyle='#6DAA45';circ(c,x+Math.cos(a)*d,y+Math.sin(a)*d,r*.075)}
 for(let i=0;i<6;i++){const a=R()*6.283,d=R()*r*.8;c.fillStyle='#EE7E3A';c.fillRect(x+Math.cos(a)*d,y+Math.sin(a)*d,r*.1,r*.1)}
 c.strokeStyle='#4D9A3A';c.lineWidth=r*.05;for(let i=0;i<7;i++){const a=R()*6.283,d=R()*r*.8;c.beginPath();c.arc(x+Math.cos(a)*d,y+Math.sin(a)*d,r*.07,0,7);c.stroke()}}
function noodleNest(c,R,x,y,r,cols){c.fillStyle=cols[1];el(c,x,y,r,r*.95);c.lineCap='round';for(let i=0;i<34;i++){c.strokeStyle=cols[Math.floor(R()*cols.length)];c.lineWidth=r*.075;c.beginPath();const r0=r*(.2+R()*.7),a0=R()*6.28;c.arc(x+(R()-.5)*r*.2,y+(R()-.5)*r*.2,r0,a0,a0+1.4+R()*2);c.stroke()}}
function tomatoSauce(c,R,x,y,r){let g=c.createRadialGradient(x-r*.3,y-r*.3,1,x,y,r);g.addColorStop(0,'#EE6A40');g.addColorStop(1,'#B42C1C');c.fillStyle=g;for(let i=0;i<7;i++){const a=R()*6.28,d=R()*r*.45;el(c,x+Math.cos(a)*d,y+Math.sin(a)*d,r*.55,r*.48)}gloss(c,x-r*.3,y-r*.35,r*.25,r*.12,.4)}
function shrimp(c,x,y,s,a){c.save();c.translate(x,y);c.rotate(a);c.lineCap='round';c.strokeStyle='#E46A43';c.lineWidth=6*s;c.beginPath();c.arc(0,0,6*s,.3,3.7);c.stroke();c.strokeStyle='#F8A57E';c.lineWidth=2.6*s;c.beginPath();c.arc(0,0,6*s,.4,3.4);c.stroke();c.strokeStyle='rgba(255,255,255,.7)';c.lineWidth=.8*s;for(let k=0;k<4;k++){const t=.7+k*.7;c.beginPath();c.moveTo(Math.cos(t)*3*s,Math.sin(t)*3*s);c.lineTo(Math.cos(t)*9*s,Math.sin(t)*9*s);c.stroke()}c.fillStyle='#D5492F';c.beginPath();c.moveTo(Math.cos(3.7)*6*s,Math.sin(3.7)*6*s);c.lineTo(Math.cos(3.7)*6*s-5*s,Math.sin(3.7)*6*s+3*s);c.lineTo(Math.cos(3.7)*6*s-2*s,Math.sin(3.7)*6*s+5*s);c.fill();c.restore()}
function mussel(c,x,y,s,a){c.save();c.translate(x,y);c.rotate(a);c.fillStyle='#262A3A';el(c,0,0,8.5*s,5.2*s);c.fillStyle='#F09A5C';el(c,.5*s,0,5.4*s,3.1*s);gloss(c,-3*s,-2.5*s,3*s,1*s,.35);c.restore()}
function greens(c,R,x,y,r,n){const cols=['#6FB33F','#8FCC52','#4F9A3A','#B5DB68','#8B3A55','#7DBE4C','#A8D35A'];for(let i=0;i<n;i++){const a=R()*6.283,d=Math.sqrt(R())*r;leaf(c,x+Math.cos(a)*d,y+Math.sin(a)*d,r*.5+R()*r*.25,r*.24,R()*6.28,cols[Math.floor(R()*cols.length)])}c.fillStyle='rgba(255,255,255,.22)';for(let i=0;i<Math.floor(n/3);i++){const a=R()*6.283,d=Math.sqrt(R())*r*.8;el(c,x+Math.cos(a)*d,y+Math.sin(a)*d,r*.12,r*.06)}}
function cherryTom(c,x,y,r){c.fillStyle='#D8392A';circ(c,x,y,r);c.fillStyle='#F06A4F';circ(c,x-r*.2,y-r*.2,r*.6);gloss(c,x-r*.35,y-r*.4,r*.3,r*.18,.6);c.fillStyle='#3E7D2E';circ(c,x+r*.1,y-r*.8,r*.25)}
function lemonWedge(c,x,y,s,a){c.save();c.translate(x,y);c.rotate(a);c.fillStyle='#F2D23E';c.beginPath();c.arc(0,0,9*s,Math.PI,0);c.closePath();c.fill();c.fillStyle='#FBEFA2';c.beginPath();c.arc(0,-.4*s,7.2*s,Math.PI,0);c.closePath();c.fill();c.strokeStyle='#F2D23E';c.lineWidth=.8*s;for(let k=1;k<5;k++){const t=Math.PI+k*Math.PI/5;c.beginPath();c.moveTo(0,-.4*s);c.lineTo(Math.cos(t)*7*s,Math.sin(t)*7*s-.4*s);c.stroke()}c.restore()}
function herbs(c,R,x,y,r,n,col){for(let i=0;i<n;i++){const a=R()*6.283,d=R()*r;leaf(c,x+Math.cos(a)*d,y+Math.sin(a)*d,4+R()*2,2,R()*6,col||'#4E9A3A')}}
function rosemary(c,x,y,s,a){c.save();c.translate(x,y);c.rotate(a);c.strokeStyle='#5C6E3A';c.lineWidth=1*s;c.beginPath();c.moveTo(-10*s,0);c.lineTo(10*s,0);c.stroke();for(let k=-8;k<=8;k+=2.5){leaf(c,k*s,-2*s,4.5*s,1.2*s,-.9,'#4E7A3A');leaf(c,k*s,2*s,4.5*s,1.2*s,.9,'#5E8C45')}c.restore()}
function truffleShave(c,x,y,r){c.fillStyle='#2F2622';circ(c,x,y,r);c.strokeStyle='rgba(200,180,160,.55)';c.lineWidth=.6;c.beginPath();c.moveTo(x-r*.7,y);c.quadraticCurveTo(x,y-r*.5,x+r*.6,y+r*.2);c.moveTo(x-r*.3,y+r*.5);c.quadraticCurveTo(x,y,x+r*.2,y-r*.6);c.stroke()}
function duckSlices(c,x,y,s){for(let k=0;k<5;k++){c.save();c.translate(x-8*s+k*4.5*s,y+(k-2)*1.2*s);c.rotate(-.55+k*.27);c.fillStyle='#6E3219';rr(c,-13*s,-4.8*s,26*s,9.6*s,4.8*s);c.fill();c.fillStyle='#F1DEC0';rr(c,-12.5*s,-4.8*s,25*s,2.4*s,1.2*s);c.fill();let g=c.createLinearGradient(0,-2*s,0,4*s);g.addColorStop(0,'#E8908A');g.addColorStop(1,'#C85A5A');c.fillStyle=g;rr(c,-11.5*s,-1.8*s,23*s,5.6*s,2.8*s);c.fill();c.restore()}}
const STEAK_COL=['#B8263A','#D2465A','#C96A6A','#8F5E4F'];
function steakSlices(c,x,y,s,w){for(let k=0;k<5;k++){c.save();c.translate(x-10*s+k*5*s,y+(k-2)*.8*s);c.rotate(-.35+k*.16);c.fillStyle='#4A2615';rr(c,-9*s,-12*s,18*s,24*s,4*s);c.fill();let g=c.createRadialGradient(0,0,1,0,0,10*s);g.addColorStop(0,STEAK_COL[w]);g.addColorStop(1,'#8A4A34');c.fillStyle=g;rr(c,-7*s,-10*s,14*s,20*s,3.5*s);c.fill();c.strokeStyle='rgba(40,18,8,.8)';c.lineWidth=1.4*s;if(k===4){for(let m=-6;m<=6;m+=4){c.beginPath();c.moveTo(-8*s,m*s-3*s);c.lineTo(8*s,m*s+3*s);c.stroke()}}c.restore()}}
function salmonFillet(c,x,y,s,a){c.save();c.translate(x,y);c.rotate(a||-.2);c.fillStyle='#B8572B';rr(c,-18*s,-10*s,36*s,21*s,9*s);c.fill();let g=c.createLinearGradient(0,-10*s,0,10*s);g.addColorStop(0,'#F7A67A');g.addColorStop(1,'#E3703F');c.fillStyle=g;rr(c,-17*s,-10*s,34*s,17*s,8*s);c.fill();c.strokeStyle='rgba(255,230,215,.8)';c.lineWidth=1.3*s;for(let k=-3;k<=3;k++){c.beginPath();c.moveTo(k*4.5*s-3*s,-9*s);c.quadraticCurveTo(k*4.5*s+1*s,-2*s,k*4.5*s-2*s,6*s);c.stroke()}gloss(c,-6*s,-6*s,7*s,2*s,.35);c.restore()}
function chickenLeg(c,x,y,s){c.save();c.translate(x,y);c.rotate(-.45);c.fillStyle='#F5EAD6';rr(c,12*s,-3*s,12*s,6*s,3*s);c.fill();circ(c,24*s,-3*s,3.2*s);circ(c,24*s,3*s,3.2*s);let g=c.createRadialGradient(-6*s,-6*s,2,0,0,22*s);g.addColorStop(0,'#EDB463');g.addColorStop(.7,'#C7772F');g.addColorStop(1,'#8E4A1C');c.fillStyle=g;el(c,-2*s,0,19*s,13*s);gloss(c,-8*s,-6*s,7*s,2.5*s,.45);gloss(c,4*s,-4*s,3*s,1.2*s,.3);c.fillStyle='rgba(90,50,20,.35)';for(let k=0;k<6;k++)circ(c,-12*s+k*4*s,(k%2?3:-2)*s,.9*s);c.restore()}
function asparagus(c,x,y,s,n,a){c.save();c.translate(x,y);c.rotate(a||.25);for(let k=0;k<n;k++){c.strokeStyle='#5E8F3A';c.lineCap='round';c.lineWidth=3.4*s;c.beginPath();c.moveTo(-18*s,k*4*s);c.lineTo(14*s,k*4*s-2*s);c.stroke();c.fillStyle='#4C7A2E';el(c,15*s,k*4*s-2*s,4*s,2.2*s);c.strokeStyle='rgba(255,255,255,.25)';c.lineWidth=.8*s;c.beginPath();c.moveTo(-16*s,k*4*s-.8*s);c.lineTo(12*s,k*4*s-2.8*s);c.stroke()}c.restore()}
function friesPile(c,R,x,y,s,n){for(let i=0;i<n;i++){stick(c,x+(R()-.5)*20*s,y+(R()-.5)*14*s,14*s+R()*6*s,3.6*s,R()*3.14,'#F4C650','#D59A2C')}}
function vegPieces(c,R,x,y,r){for(let i=0;i<5;i++){const a=R()*6.28,d=R()*r*.8,px=x+Math.cos(a)*d,py=y+Math.sin(a)*d;c.save();c.translate(px,py);c.rotate(R()*3);c.fillStyle=i%2?'#E8892E':'#C63A3A';rr(c,-5,-3.5,10,7,2);c.fill();c.fillStyle='rgba(60,25,10,.35)';rr(c,-5,1.5,10,2,1);c.fill();c.fillStyle='rgba(255,255,255,.25)';rr(c,-3.5,-2.5,4,1.4,.7);c.fill();c.restore()}
 for(let i=0;i<5;i++){const a=R()*6.28,d=R()*r*.7,px=x+Math.cos(a)*d,py=y+Math.sin(a)*d;c.fillStyle='#4E7F2E';circ(c,px,py,5.5);c.fillStyle='#E7EDB8';circ(c,px,py,4.2);c.fillStyle='rgba(120,70,20,.4)';c.beginPath();c.arc(px,py,4.4,3.5,5.2);c.lineTo(px,py);c.fill();c.strokeStyle='rgba(60,40,20,.55)';c.lineWidth=.9;c.beginPath();c.moveTo(px-3,py-1);c.lineTo(px+3,py-2);c.moveTo(px-3,py+2);c.lineTo(px+3,py+1);c.stroke()}
 for(let i=0;i<4;i++){const a=R()*6.28,d=R()*r*.75;c.save();c.translate(x+Math.cos(a)*d,y+Math.sin(a)*d);c.rotate(R()*6);c.strokeStyle=i%2?'#D6392E':'#F2BE2E';c.lineWidth=4.2;c.lineCap='round';c.beginPath();c.arc(0,0,6,0,2);c.stroke();c.restore()}
 for(let i=0;i<3;i++){const a=R()*6.28,d=R()*r*.7;c.fillStyle='#5B2E5A';el(c,x+Math.cos(a)*d,y+Math.sin(a)*d,6,4.5);c.fillStyle='#EFE2C6';el(c,x+Math.cos(a)*d,y+Math.sin(a)*d,4.5,3.2)}
 cherryTom(c,x+r*.4,y-r*.3,4);cherryTom(c,x-r*.5,y+r*.3,4)}
function scallops(c,x,y,s){for(let k=0;k<3;k++){const px=x+(k-1)*11*s,py=y+(k%2?4:-2)*s;c.fillStyle='#F2E6D0';el(c,px,py+2*s,7*s,5*s);let g=c.createRadialGradient(px,py,1,px,py,7*s);g.addColorStop(0,'#E0A45A');g.addColorStop(1,'#A8632A');c.fillStyle=g;el(c,px,py,6.4*s,4.6*s);gloss(c,px-2*s,py-1.5*s,2.2*s,1*s,.4)}}
function mash(c,x,y,s){c.fillStyle='#F3E2B6';el(c,x,y,16*s,11*s);c.strokeStyle='#E2CB90';c.lineWidth=1.4*s;c.beginPath();c.arc(x,y,9*s,.5,4);c.stroke();c.beginPath();c.arc(x+2*s,y,4*s,1,5);c.stroke();gloss(c,x-5*s,y-4*s,5*s,2*s,.4)}
function bread(c,x,y,s){c.save();c.translate(x,y);c.rotate(-.3);c.fillStyle='#9A5A28';rr(c,-12*s,-8*s,24*s,16*s,6*s);c.fill();c.fillStyle='#F2DDB0';rr(c,-10*s,-6*s,20*s,12*s,5*s);c.fill();c.fillStyle='rgba(180,140,90,.5)';for(let k=0;k<6;k++)circ(c,-6*s+k*2.4*s,(k%2?2:-2)*s,.9*s);c.restore()}

const VESSEL={coffee:'cup',blacktea:'cup',sparkling:'glass',fruitsoda:'glass',soup:'bowl',salad:'bowl',soup_x:'bowl'};
function paintFood(c,id,want){const SP=DISHES[id]&&DISHES[id].special?SPECIALS[DISHES[id].special]:null;if(SP){paintFood(c,DISHES[id].special,want);paintTopping(c,SP.top,rng(hash(id)));return}
 const R=rng(hash(id+'|'+(want||0)+(id==='signature'&&S.signature?JSON.stringify(S.signature):'')));
 const flat=fn=>{c.save();c.scale(1,.8);fn();c.restore()};
 switch(id){
 case 'friedrice':flat(()=>{riceMound(c,R,0,0,28)});break;
 case 'pasta':flat(()=>{noodleNest(c,R,0,0,27,['#F4CB72','#E8B04F','#F7D98E']);tomatoSauce(c,R,0,-2,15);leaf(c,7,-9,12,6,-.6,'#3F8B3A');leaf(c,11,-4,10,5,.4,'#4E9E44');c.fillStyle='#FFF6DC';for(let i=0;i<16;i++)circ(c,(R()-.5)*30,(R()-.5)*28,.9)});break;
 case 'seafood':flat(()=>{noodleNest(c,R,0,0,27,['#F3DB9A','#E9C678','#F7E6B4']);c.fillStyle='rgba(120,160,40,.25)';el(c,0,0,20,18);shrimp(c,-9,-6,1,.4);shrimp(c,9,-8,1,2.2);shrimp(c,2,8,1,-1);mussel(c,-12,8,1,.5);mussel(c,14,5,1,-.7);herbs(c,R,0,0,20,8,'#3E8A36');lemonWedge(c,22,-16,.8,.6)});break;
 case 'burger':flat(()=>{friesPile(c,R,22,8,1,10);c.fillStyle='#7CBF4A';for(let k=0;k<12;k++){const a=k/12*6.28;circ(c,-8+Math.cos(a)*20,Math.sin(a)*19,6)}c.fillStyle='#F7C548';c.beginPath();c.moveTo(-30,-2);c.lineTo(-18,-14);c.lineTo(-14,4);c.fill();c.beginPath();c.moveTo(10,-12);c.lineTo(14,4);c.lineTo(2,-6);c.fill();c.fillStyle='#6A3A20';el(c,-8,2,21,19);let g=c.createRadialGradient(-14,-8,3,-8,0,21);g.addColorStop(0,'#F1B566');g.addColorStop(1,'#B5652A');c.fillStyle=g;el(c,-8,-1,20,18);c.fillStyle='#FFF3D6';for(let i=0;i<16;i++){c.save();c.translate(-8+(R()-.5)*26,-1+(R()-.5)*24);c.rotate(R()*3);el(c,0,0,1.8,.9);c.restore()}gloss(c,-15,-9,6,3,.35)});break;
 case 'salad':flat(()=>{greens(c,R,0,0,24,36);cherryTom(c,-8,-6,4.6);cherryTom(c,9,5,4.6);cherryTom(c,5,-12,4);for(let k=0;k<3;k++){const px=(R()-.5)*30,py=(R()-.5)*26;c.fillStyle='#5A8F3A';circ(c,px,py,5.2);c.fillStyle='#DDEFC2';circ(c,px,py,4.2)}c.fillStyle='#D9A45A';for(let k=0;k<4;k++){c.save();c.translate((R()-.5)*30,(R()-.5)*26);c.rotate(R());c.fillRect(-2.5,-2.5,5,5);c.restore()}c.strokeStyle='rgba(255,250,235,.85)';c.lineWidth=1.3;c.beginPath();c.moveTo(-16,4);c.bezierCurveTo(-6,-10,4,14,16,-4);c.stroke()});break;
 case 'prosciutto':flat(()=>{greens(c,R,0,2,20,20);c.lineCap='round';for(let k=0;k<4;k++){const px=(k-1.5)*11,py=(k%2?-6:5);c.strokeStyle='#D9737A';c.lineWidth=8.5;c.beginPath();c.moveTo(px-8,py);c.bezierCurveTo(px-3,py-9,px+3,py+9,px+8,py);c.stroke();c.strokeStyle='#F3C1C0';c.lineWidth=2;c.beginPath();c.moveTo(px-7,py-2.4);c.bezierCurveTo(px-3,py-10,px+3,py+6,px+7,py-2.4);c.stroke()}c.fillStyle='#FFF4D8';for(let k=0;k<5;k++){c.save();c.translate((R()-.5)*30,(R()-.5)*26);c.rotate(R()*3);c.fillRect(-3,-1,6,2);c.restore()}c.fillStyle='#6B2E4A';circ(c,-18,-10,4.5);c.fillStyle='#E88A9A';circ(c,-18,-10,3);c.fillStyle='#4A1F1F';for(let k=0;k<7;k++)circ(c,(R()-.5)*44,(R()-.5)*40,1)});break;
 case 'coffee':flat(()=>{c.fillStyle='#E9E2D6';rr(c,20,-5,14,10,5);c.fill();c.fillStyle='#FBF8F2';rr(c,22,-3,9,6,3);c.fill();c.fillStyle='rgba(60,30,15,.2)';el(c,1,3,26,26);c.fillStyle='#FFFFFF';circ(c,0,0,25);c.fillStyle='#E7DFD1';circ(c,0,1,22);let g=c.createRadialGradient(-5,-5,2,0,0,21);g.addColorStop(0,'#9A5A30');g.addColorStop(1,'#5B3019');c.fillStyle=g;circ(c,0,1,20);c.fillStyle='#F1DDBB';c.beginPath();c.moveTo(0,12);c.bezierCurveTo(-16,0,-10,-12,0,-5);c.bezierCurveTo(10,-12,16,0,0,12);c.fill();c.strokeStyle='#A8683A';c.lineWidth=1.3;c.beginPath();c.moveTo(0,-3);c.lineTo(0,9);c.stroke();gloss(c,-9,-10,5,2,.25)});break;
 case 'blacktea':flat(()=>{c.fillStyle='#E9E2D6';rr(c,20,-5,14,10,5);c.fill();c.fillStyle='rgba(60,30,15,.2)';el(c,1,3,26,26);c.fillStyle='#FFFFFF';circ(c,0,0,25);let g=c.createRadialGradient(-5,-5,2,0,0,21);g.addColorStop(0,'#E08A3E');g.addColorStop(1,'#9A4416');c.fillStyle=g;circ(c,0,1,21);c.fillStyle='#F2D23E';circ(c,6,-3,7);c.fillStyle='#FBEFA2';circ(c,6,-3,5.6);c.strokeStyle='#F2D23E';c.lineWidth=.7;for(let k=0;k<6;k++){c.beginPath();c.moveTo(6,-3);c.lineTo(6+Math.cos(k)*5.5,-3+Math.sin(k)*5.5);c.stroke()}gloss(c,-9,-9,6,2,.3)});break;
 case 'sparkling':case 'fruitsoda':{drawCoaster(c);const soda=id==='fruitsoda';c.save();c.beginPath();c.moveTo(-17,-38);c.lineTo(17,-38);c.lineTo(14,36);c.lineTo(-14,36);c.closePath();c.clip();let g=c.createLinearGradient(0,-30,0,36);if(soda){g.addColorStop(0,'#FF93A6');g.addColorStop(1,'#FFB35C')}else{g.addColorStop(0,'rgba(200,232,244,.8)');g.addColorStop(1,'rgba(160,210,230,.85)')}c.fillStyle=g;c.fillRect(-20,-28,40,70);c.fillStyle='rgba(255,255,255,.55)';rr(c,-11,-24,10,10,2);c.fill();rr(c,1,-18,10,10,2);c.fill();if(soda){c.fillStyle='#F7931E';circ(c,-4,6,8);c.fillStyle='#FFC46B';circ(c,-4,6,6);c.fillStyle='#E23E57';el(c,6,18,6,5)}else{c.fillStyle='#F2D23E';circ(c,-3,10,7);c.fillStyle='#FBEFA2';circ(c,-3,10,5.5)}c.strokeStyle='rgba(255,255,255,.85)';c.lineWidth=.9;for(let i=0;i<14;i++){c.beginPath();c.arc((R()-.5)*24,-24+R()*56,.8+R()*1.4,0,7);c.stroke()}c.restore();c.strokeStyle='rgba(255,255,255,.9)';c.lineWidth=1.6;c.beginPath();c.moveTo(-17,-38);c.lineTo(-14,36);c.lineTo(14,36);c.lineTo(17,-38);c.stroke();c.fillStyle='rgba(255,255,255,.35)';c.fillRect(-12,-30,3,60);if(soda){c.save();c.translate(8,-38);c.rotate(.35);c.fillStyle='#fff';c.fillRect(-2,-16,4,40);c.fillStyle='#E23E57';for(let k=0;k<5;k++)c.fillRect(-2,-16+k*8,4,4);c.restore();leaf(c,-8,-38,10,4,-.5,'#4E9A3A')}else{lemonWedge(c,12,-38,.9,.5)}break}
 case 'fries':flat(()=>{c.save();c.rotate(.2);c.fillStyle='#F6F0E2';c.fillRect(-24,-22,48,44);c.strokeStyle='rgba(120,90,60,.2)';c.strokeRect(-24,-22,48,44);c.restore();friesPile(c,R,-2,0,1.3,20);for(let k=0;k<6;k++)truffleShave(c,(R()-.5)*30,(R()-.5)*24,3.5);herbs(c,R,0,0,18,8,'#3E8A36');c.fillStyle='#fff';circ(c,22,-18,8);c.fillStyle='#F2E5B8';circ(c,22,-18,6)});break;
 case 'veg':flat(()=>{vegPieces(c,R,0,0,26);rosemary(c,10,14,1,.3)});break;
 case 'soup':flat(()=>{let g=c.createRadialGradient(-6,-6,3,0,0,28);g.addColorStop(0,'#F7B24A');g.addColorStop(1,'#DA7A20');c.fillStyle=g;circ(c,0,2,28);c.strokeStyle='rgba(255,250,240,.9)';c.lineWidth=2.4;c.beginPath();for(let t=0;t<14;t+=.2){const r=t*1.1;c.lineTo(Math.cos(t)*r,2+Math.sin(t)*r)}c.stroke();c.fillStyle='#4F7A35';for(let k=0;k<6;k++){c.save();c.translate((R()-.5)*30,(R()-.5)*30);c.rotate(R()*3);el(c,0,0,3,1.6);c.restore()}c.fillStyle='#D9A45A';c.fillRect(8,-12,5,5);c.fillRect(-14,8,5,5);gloss(c,-10,-10,8,3,.3)});break;
 case 'duck':flat(()=>{c.fillStyle='#C8732A';el(c,2,6,26,14);c.fillStyle='#B25E1E';el(c,6,8,18,9);duckSlices(c,0,-2,1.1);c.fillStyle='#F29A38';el(c,-22,10,5,3);el(c,-18,14,5,3);herbs(c,R,16,-12,6,6,'#5AA048');c.fillStyle='#8A3A1A';for(let k=0;k<5;k++)circ(c,-20+k*10,20,1.6)});break;
 case 'risotto':flat(()=>{let rg=c.createRadialGradient(-6,-6,3,0,0,27);rg.addColorStop(0,'#F6E6B6');rg.addColorStop(1,'#DEBF80');c.fillStyle=rg;el(c,0,0,27,25);c.fillStyle='rgba(255,255,255,.7)';for(let k=0;k<8;k++){c.save();c.translate((R()-.5)*40,(R()-.5)*36);c.rotate(R()*3);c.fillRect(-3,-1,6,2);c.restore()}for(let i=0;i<80;i++){const a=R()*6.28,d=Math.sqrt(R())*24;c.fillStyle=R()<.5?'#F8ECC8':'#E0C78D';c.save();c.translate(Math.cos(a)*d,Math.sin(a)*d);c.rotate(R()*3);el(c,0,0,2.4,1.3);c.restore()}for(let k=0;k<7;k++)truffleShave(c,(R()-.5)*30,(R()-.5)*28,3.6+R()*1.6);c.fillStyle='#4F8A3A';for(let k=0;k<6;k++)circ(c,(R()-.5)*50,(R()-.5)*44,1.3);gloss(c,-9,-10,8,3,.3)});break;
 case 'chicken':flat(()=>{for(let k=0;k<4;k++){const px=-16+k*10,py=16-(k%2)*5;let g=c.createRadialGradient(px-2,py-2,1,px,py,6);g.addColorStop(0,'#F4CE79');g.addColorStop(1,'#C98A34');c.fillStyle=g;el(c,px,py,6,5)}chickenLeg(c,-2,-4,1.05);rosemary(c,18,-14,.9,1.2);lemonWedge(c,-22,-12,.8,-.6)});break;
 case 'steak':flat(()=>{c.fillStyle='rgba(120,40,30,.25)';el(c,0,4,26,14);steakSlices(c,0,-1,1,want||1);c.fillStyle='#F8E08E';rr(c,-22,-18,10,8,2);c.fill();herbs(c,R,-17,-14,3,3,'#4E7A3A');rosemary(c,16,14,.9,-.4);c.fillStyle='#fff';for(let k=0;k<8;k++)circ(c,(R()-.5)*34,(R()-.5)*28,.7)});break;
 case 'salmon':flat(()=>{asparagus(c,-2,-2,1,5,.25);salmonFillet(c,2,-4,1,-.18);lemonWedge(c,20,14,.9,.4);herbs(c,R,-10,-14,5,5,'#6FA84E')});break;
 case 'basque':flat(()=>{c.fillStyle='#EAD29A';c.beginPath();c.moveTo(-26,-2);c.lineTo(24,-14);c.lineTo(24,18);c.lineTo(-26,6);c.closePath();c.fill();c.fillStyle='#F4DFA9';c.beginPath();c.moveTo(-26,-2);c.lineTo(24,4);c.lineTo(24,18);c.lineTo(-26,6);c.closePath();c.fill();let g=c.createLinearGradient(-26,0,24,0);g.addColorStop(0,'#7A4A22');g.addColorStop(1,'#3E2210');c.fillStyle=g;c.beginPath();c.moveTo(-26,-3);c.lineTo(24,-15);c.lineTo(24,4);c.lineTo(-26,-1);c.closePath();c.fill();c.fillStyle='rgba(30,15,5,.55)';for(let k=0;k<7;k++)el(c,-14+k*6,-6+(R()-.5)*4-k*1.4,2.4,1.2);c.fillStyle='#3A2E6A';circ(c,-18,14,3.4);circ(c,-12,17,3);c.fillStyle='#D23A4A';circ(c,-6,15,3.2);gloss(c,-17,13,1.2,.7,.6)});break;
 case 'tiramisu':{drawPlate(c,false,.1);c.fillStyle='rgba(90,50,25,.18)';el(c,0,16,28,8);c.fillStyle='#F4E6CC';c.fillRect(-18,-4,36,20);c.fillStyle='#B77A45';c.fillRect(-18,1,36,4);c.fillRect(-18,10,36,4);c.fillStyle='#6E4226';c.beginPath();c.moveTo(-18,-4);c.lineTo(-10,-14);c.lineTo(26,-14);c.lineTo(18,-4);c.closePath();c.fill();c.fillStyle='#E9DCC2';c.beginPath();c.moveTo(18,-4);c.lineTo(26,-14);c.lineTo(26,6);c.lineTo(18,16);c.closePath();c.fill();c.fillStyle='#A8703E';c.beginPath();c.moveTo(18,1);c.lineTo(26,-9);c.lineTo(26,-5);c.lineTo(18,5);c.fill();c.fillStyle='rgba(60,30,15,.5)';for(let k=0;k<30;k++)circ(c,-12+R()*34,-12+R()*7,.6);leaf(c,4,-14,9,4,-.4,'#4E9A3A');c.fillStyle='rgba(110,66,38,.5)';for(let k=0;k<20;k++)circ(c,(R()-.5)*60,20+R()*8,.6);break}
 case 'pudding':flat(()=>{c.fillStyle='#A85617';el(c,0,4,26,20);gloss(c,-10,-4,6,2,.25)});c.fillStyle='rgba(90,40,10,.25)';el(c,1,12,20,6);{let g=c.createLinearGradient(-17,0,17,0);g.addColorStop(0,'#E7B650');g.addColorStop(.4,'#F7D98A');g.addColorStop(1,'#D9A13E');c.fillStyle=g;c.beginPath();c.moveTo(-17,-10);c.lineTo(17,-10);c.lineTo(19,10);c.quadraticCurveTo(0,16,-19,10);c.closePath();c.fill();c.fillStyle='#B8661F';el(c,0,-10,17,6);c.fillStyle='#8E4712';for(let k=0;k<5;k++){c.beginPath();c.moveTo(-14+k*7,-9);c.quadraticCurveTo(-13+k*7,-3,-12+k*7,-9);c.fill()}gloss(c,-6,-12,6,1.6,.5)}break;
 case 'souffle':c.fillStyle='rgba(90,50,25,.2)';el(c,2,18,26,7);c.fillStyle='#FFFFFF';c.fillRect(-20,-2,40,20);el(c,0,18,20,5);c.strokeStyle='rgba(150,130,110,.25)';c.lineWidth=1;for(let k=-18;k<=18;k+=4){c.beginPath();c.moveTo(k,-1);c.lineTo(k,20);c.stroke()}{let g=c.createRadialGradient(-5,-18,2,0,-8,24);g.addColorStop(0,'#F4CE7A');g.addColorStop(1,'#C98A33');c.fillStyle=g;c.beginPath();c.moveTo(-21,-2);c.bezierCurveTo(-24,-24,24,-24,21,-2);c.closePath();c.fill();c.fillStyle='#fff';el(c,0,-2,21,4);c.fillStyle='#F4CE7A';el(c,0,-3,20,3);c.fillStyle='rgba(255,255,255,.9)';for(let k=0;k<26;k++)circ(c,(R()-.5)*30,-20+R()*14,.8)}c.fillStyle='#D23A4A';circ(c,22,14,3.4);c.fillStyle='#3A2E6A';circ(c,26,17,3);break;
 case 'signature':{const s=S.signature||{base:'mash',protein:'duck',sauce:'redwine',side:'asparagus'};flat(()=>{c.fillStyle=SIG.sauce[s.sauce].c;el(c,2,4,26,15);c.fillStyle='rgba(255,255,255,.2)';el(c,-6,0,8,3);
  if(s.base==='rice')riceMound(c,R,-14,4,11);else if(s.base==='mash')mash(c,-12,4,1);else if(s.base==='pasta')noodleNest(c,R,-13,4,11,['#F3DB9A','#E9C678','#F7E6B4']);else bread(c,-14,4,1);
  if(s.side==='asparagus')asparagus(c,4,14,.7,4,-.1);else if(s.side==='veg'){cherryTom(c,16,14,4);c.fillStyle='#4E7F2E';circ(c,8,16,4.5);c.fillStyle='#E7EDB8';circ(c,8,16,3.3)}else if(s.side==='salad')greens(c,R,16,12,8,10);else friesPile(c,R,16,12,.7,8);
  if(s.protein==='duck')duckSlices(c,6,-4,.85);else if(s.protein==='beef')steakSlices(c,6,-4,.8,1);else if(s.protein==='salmon')salmonFillet(c,6,-6,.75,-.3);else if(s.protein==='chicken')chickenLeg(c,6,-6,.75);else scallops(c,6,-6,1);
  c.fillStyle='#E9C46A';for(let k=0;k<6;k++)c.fillRect(-10+R()*30,-16+R()*16,1.6,1.6);herbs(c,R,10,-14,5,4,'#6FA84E');
  const lv=sigLv();if(lv>=2){/* the second version: a swoosh of the sauce and a tuft of microgreens */c.strokeStyle=shade(SIG.sauce[s.sauce].c,-.25);c.lineWidth=3.2;c.lineCap='round';c.beginPath();c.moveTo(-26,16);c.quadraticCurveTo(-8,26,20,20);c.stroke();c.lineWidth=1.2;c.strokeStyle='rgba(255,255,255,.25)';c.beginPath();c.moveTo(-24,15);c.quadraticCurveTo(-8,23,16,19);c.stroke();for(let k=0;k<7;k++){c.save();c.translate(22+(R()-.5)*8,-12+(R()-.5)*8);c.rotate(R()*3);leaf(c,0,0,5,2.2,0,k%2?'#4E9E44':'#7CBF4A');c.restore()}}
  if(lv>=3){/* the third: an edible flower and a few flakes of gold leaf */c.save();c.translate(-20,-14);for(let k=0;k<6;k++){c.save();c.rotate(k*1.047);c.fillStyle=k%2?'#F4B6C2':'#F7D06B';el(c,3.2,0,3,1.6);c.restore()}c.fillStyle='#F0932B';circ(c,0,0,1.5);c.restore();c.fillStyle='#F1C64B';for(let k=0;k<5;k++){c.save();c.translate(-4+R()*24,-8+R()*18);c.rotate(R()*3);c.fillRect(-1.4,-.9,2.8,1.8);c.restore()}c.fillStyle='rgba(255,255,255,.5)';for(let k=0;k<3;k++)circ(c,-2+R()*20,-6+R()*14,.5)}});break}
 }}
const DCACHE=new Map();
function dishCanvas(id,q,size,gold,want){const key=id+'|'+q+'|'+size+'|'+(gold?1:0)+'|'+(want||0)+(id==='signature'&&S.signature?'|'+S.signature.base+S.signature.protein+S.signature.sauce+S.signature.side+sigLv():'');if(DCACHE.has(key))return DCACHE.get(key);
 const cv=mkCanvas(size),c=cv.getContext('2d');c.translate(size/2,size/2);c.scale(size/100,size/100);const v=VESSEL[id]||'plate';
 if(v==='plate'&&id!=='tiramisu')drawPlate(c,gold);else if(id==='tiramisu')drawPlate(c,gold);else if(v==='bowl')drawBowl(c,gold);else if(v==='cup')drawPlate(c,gold,.92);
 const fl=mkCanvas(size),f=fl.getContext('2d');f.translate(size/2,size/2);const fs=(v==='cup'||v==='glass')?1:1.12;/* 2.1: the food fills more of the plate */f.scale(size/100*fs,size/100*fs);paintFood(f,id,want);
 f.setTransform(1,0,0,1,0,0);f.globalCompositeOperation='source-atop';
 if(q==='B'){f.fillStyle='rgba(38,20,10,.66)';f.fillRect(0,0,size,size)}else if(q==='O'){f.fillStyle='rgba(130,110,90,.2)';f.fillRect(0,0,size,size)}else if(q==='P'){const g=f.createRadialGradient(size*.38,size*.34,1,size*.38,size*.34,size*.45);g.addColorStop(0,'rgba(255,255,255,.3)');g.addColorStop(1,'rgba(255,255,255,0)');f.fillStyle=g;f.fillRect(0,0,size,size)}
 c.setTransform(1,0,0,1,0,0);if(v!=='cup'&&v!=='glass'){/* the food sits on the plate: a soft shadow under it */c.save();c.shadowColor='rgba(60,30,10,.32)';c.shadowBlur=size*.05;c.shadowOffsetY=size*.025;c.drawImage(fl,0,0);c.restore()}else c.drawImage(fl,0,0);
 if(q==='B'){c.fillStyle='rgba(60,60,60,.35)';for(let k=0;k<3;k++){c.beginPath();c.arc(size*(.4+k*.1),size*(.3-k*.06),size*.08,0,7);c.fill()}}
 if(DCACHE.size>600)DCACHE.clear();DCACHE.set(key,cv);return cv}
const ICACHE=new Map();
function dishURL(id,q,want){const k='u'+id+(q||'G')+(want||0)+(id==='signature'&&S.signature?S.signature.base+S.signature.protein+S.signature.sauce+S.signature.side+sigLv():'')+(S.decor.ware?1:0);if(ICACHE.has(k))return ICACHE.get(k);const u=dishCanvas(id,q||'G',112,S.decor.ware>0,want).toDataURL();ICACHE.set(k,u);return u}

/* ================= people art ================= */
/* People. One renderer for guests, staff, Dylan and Jill. Units are the same as before (head r≈9.6,
   torso 17 wide) so nothing that positions or hit-tests people had to move. Options: s/pscale, flip,
   seated, lounge{legs,len}, bob, step, tall, jill, me, hat, hold ('reader'|'phone'), flipPage,
   gaze{x,y} (local, -1..1), mood (happy|ok|sad|angry|eat) + chew, blink, expr (Jill only: smile|focus|
   soft|amused|tired). Look L: skin, hair, hs 0..8, top, acc, pants. */
function drawPerson(c,x,y,L,o){o=o||{};const s=(o.s||1)*(o.pscale===undefined?PSC:o.pscale)*(L.kid?.74:1);c.save();c.translate(x,y);c.scale((o.flip?-1:1)*s,s);
 const seated=o.seated,bob=o.bob||0,step=o.step||0;const OL='rgba(60,34,22,.5)';c.lineJoin='round';c.lineCap='round';
 const pc=L.pants||'#3B3542';const skin=L.skin,hair=L.hair;const hairDk=shade(hair,-.28),hairLt=shade(hair,.3);
 if(!seated){c.fillStyle='rgba(40,25,15,.16)';el(c,0,1,13,4.4);c.fillStyle='rgba(40,25,15,.2)';el(c,0,.6,9,2.8);const LL=o.tall?15:10;const l1=-LL-Math.max(0,step)*1.6,l2=-LL-Math.max(0,-step)*1.6;
  c.fillStyle=pc;c.strokeStyle=OL;c.lineWidth=.6;rr(c,-5.6,l1,4.8,LL,2.2);c.fill();c.stroke();rr(c,.8,l2,4.8,LL,2.2);c.fill();c.stroke();
  c.fillStyle='rgba(255,255,255,.09)';c.fillRect(-4.8,l1+1.5,1.2,LL-4);c.fillRect(1.6,l2+1.5,1.2,LL-4);
  c.fillStyle='#2A2220';el(c,-3.2,l1+LL-.6,3.3,1.8);el(c,3.2,l2+LL-.6,3.3,1.8);c.fillStyle='rgba(255,255,255,.28)';el(c,-4,l1+LL-1.3,1.3,.5);el(c,2.4,l2+LL-1.3,1.3,.5)}
 if(seated&&o.lounge){const lg=o.lounge;c.fillStyle=pc;c.strokeStyle=OL;c.lineWidth=.6;
  if(lg.legs<.3){c.fillStyle=shade(pc,.12);rr(c,-7.2,-6,14.4,8.5,3.2);c.fill();c.stroke();c.fillStyle=pc;rr(c,-6.2,.5,4.8,8.5,2.2);c.fill();c.stroke();rr(c,1.4,.5,4.8,8.5,2.2);c.fill();c.stroke();c.fillStyle='rgba(255,255,255,.1)';rr(c,-6,-4.6,12,1.4,.7);c.fill();c.fillStyle='#2A2220';el(c,-3.8,9.4,3.3,1.8);el(c,3.8,9.4,3.3,1.8);c.fillStyle='rgba(255,255,255,.2)';el(c,-4.4,8.8,1.2,.5);el(c,3.2,8.8,1.2,.5)}
  else{const len=lg.len;c.save();c.translate(3,-4.5);c.rotate(.07);c.fillStyle=shade(pc,.16);rr(c,0,-5.2,len,5,2.5);c.fill();c.stroke();c.fillStyle=shade(pc,.06);rr(c,-1,-1.4,len-1.5,5.2,2.6);c.fill();c.stroke();c.fillStyle='rgba(255,255,255,.14)';rr(c,2,-.6,len-6,1.2,.6);c.fill();c.fillStyle='#2A2220';c.save();c.translate(len+.6,-3.6);c.rotate(-.6);el(c,0,0,3,1.8);c.fillStyle='rgba(255,255,255,.2)';el(c,-.6,-.6,1.4,.6);c.restore();c.save();c.translate(len-.9,.3);c.rotate(-.6);c.fillStyle='#2A2220';el(c,0,0,3,1.8);c.fillStyle='rgba(255,255,255,.2)';el(c,-.6,-.6,1.4,.6);c.restore();c.restore()}}
 const base=seated?-4:(o.tall?-14:-9);const hy=base-25+bob;const top=o.jill?'#FFFFFF':L.top;const by=base-17+bob;
 if(L.acc==='backpack'){c.fillStyle='#4E6B8A';rr(c,-9.5,by,19,14,5);c.fill();c.fillStyle='rgba(0,0,0,.15)';rr(c,-9.5,by+9,19,5,3);c.fill()}
 /* hair behind the head: long styles */
 if(L.hs===1||L.hs===2||L.hs===8){c.fillStyle=hairDk;rr(c,-11,hy-9,22,L.hs===1?20:29,9);c.fill();c.strokeStyle=OL;c.lineWidth=.6;c.stroke();c.fillStyle='rgba(0,0,0,.1)';rr(c,-11,hy+6,22,L.hs===1?5:14,6);c.fill()}
 if(L.hs===7){c.fillStyle=hairDk;el(c,0,hy+1,12.6,10.5);c.strokeStyle=OL;c.lineWidth=.6;c.beginPath();c.ellipse(0,hy+1,12.6,10.5,0,0,7);c.stroke()}
 if(L.hs===4&&o.me){c.fillStyle=hair;c.save();c.translate(7.8,hy-6);c.rotate(.32+Math.sin((o.step||0)*1.6+(o.bob||0))*.1);c.beginPath();c.moveTo(-2.6,0);c.quadraticCurveTo(-4.6,10,-.6,19);c.quadraticCurveTo(4.2,11,2.8,0);c.closePath();c.fill();c.strokeStyle=hairLt;c.lineWidth=.8;c.beginPath();c.moveTo(.2,2);c.quadraticCurveTo(-1.8,10,-.4,16);c.stroke();c.fillStyle='#D4553A';rr(c,-2.8,-1.2,5.6,2.6,1.2);c.fill();c.restore()}
 else if(L.hs===4){c.fillStyle=hair;c.save();c.translate(8.6,hy+3);c.rotate(.35);el(c,0,0,4,9);c.strokeStyle=OL;c.lineWidth=.6;c.stroke();c.strokeStyle=hairLt;c.lineWidth=.9;c.beginPath();c.moveTo(-1,-6);c.quadraticCurveTo(-2,0,-.5,6);c.stroke();c.restore()}
 /* torso */
 let bg=c.createLinearGradient(-9,0,9,0);bg.addColorStop(0,shade(top,.16));bg.addColorStop(.5,top);bg.addColorStop(1,shade(top,o.jill?-.12:-.24));c.fillStyle=bg;c.strokeStyle=OL;c.lineWidth=.6;
 /* arms hang from the shoulders and pose: they swing with the steps, come together in front to carry, one bends up
    to work. o.arms=[left,right] overrides (radians; positive = in across the body, negative = out and away). */
 const armA=(sx)=>{if(o.arms)return o.arms[sx<0?0:1];if(o.carry)return 1.25;if(!seated&&step)return sx*step*.45;return -.06};
 const arm=(sx)=>{const a=armA(sx);c.save();c.translate(sx*8.8,by+3);c.rotate(sx*a);c.fillStyle=bg;c.strokeStyle=OL;c.lineWidth=.6;rr(c,-2.2,-1.2,4.4,11.4,2.2);c.fill();c.stroke();c.fillStyle='rgba(0,0,0,.1)';rr(c,-2.2,7.8,4.4,2.3,1);c.fill();c.fillStyle=skin;circ(c,0,11.4,2.3);c.fillStyle='rgba(0,0,0,.08)';circ(c,0,12.1,1.6);c.restore()};
 const armsFront=!!(o.carry||o.arms);if(!armsFront){arm(-1);arm(1)}
 c.fillStyle=bg;rr(c,-8.6,by,17.2,17.5,6.5);c.fill();c.strokeStyle=OL;c.lineWidth=.7;c.stroke();
 if(L.pat==='stripes'){c.save();c.beginPath();rr(c,-8.6,by,17.2,17.5,6.5);c.clip();c.fillStyle='rgba(255,255,255,.28)';for(let yy=by+3;yy<by+17;yy+=3.6)c.fillRect(-9,yy,18,1.4);c.restore()}
 else if(L.pat==='dots'){c.save();c.beginPath();rr(c,-8.6,by,17.2,17.5,6.5);c.clip();c.fillStyle='rgba(255,255,255,.35)';for(let yy=by+3;yy<by+17;yy+=4)for(let xx=-7;xx<8;xx+=4)circ(c,xx+(Math.round(yy)%2?2:0),yy,.9);c.restore()}
 else if(L.pat==='cardi'){c.fillStyle=shade(L.top2||top,-.18);c.strokeStyle=OL;c.lineWidth=.5;c.beginPath();c.moveTo(-8.6,by+4);c.lineTo(-8.6,by+17);c.quadraticCurveTo(-4,by+17.5,-3.4,by+17);c.lineTo(-3.4,by+4);c.closePath();c.fill();c.stroke();c.beginPath();c.moveTo(8.6,by+4);c.lineTo(8.6,by+17);c.quadraticCurveTo(4,by+17.5,3.4,by+17);c.lineTo(3.4,by+4);c.closePath();c.fill();c.stroke()}
 if(L.chef){/* the double-breasted jacket: two rows of buttons, a coloured neckerchief */c.fillStyle='#C9CED0';for(let k=0;k<3;k++){circ(c,-3,by+5+k*4,.9);circ(c,3,by+5+k*4,.9)}c.strokeStyle='rgba(0,0,0,.1)';c.lineWidth=.6;c.beginPath();c.moveTo(0,by+2);c.lineTo(0,by+17);c.stroke();const nk=L.kerchief||'#B8536A';c.fillStyle=nk;c.beginPath();c.moveTo(-5,hy+8.4);c.lineTo(5,hy+8.4);c.lineTo(0,hy+13.4);c.closePath();c.fill();c.fillStyle='rgba(255,255,255,.3)';c.beginPath();c.moveTo(-4.2,hy+8.9);c.lineTo(-1,hy+9.2);c.lineTo(-2.4,hy+10.8);c.closePath();c.fill()}
 if(L.apron&&!seated){/* the half apron over the pants */c.fillStyle=L.apron;c.strokeStyle=OL;c.lineWidth=.5;rr(c,-8,by+13,16,9,2);c.fill();c.stroke();c.fillStyle='rgba(255,255,255,.12)';c.fillRect(-7,by+14,14,1.2)}
 /* shoulders catch the light; a waist band grounds the shirt */
 c.fillStyle='rgba(255,255,255,.14)';c.beginPath();c.moveTo(-6.8,by+1.2);c.quadraticCurveTo(-3,by-.2,1,by+.4);c.quadraticCurveTo(-2.4,by+2.2,-6.8,by+3.4);c.closePath();c.fill();
 if(!seated&&!o.jill){c.fillStyle='rgba(0,0,0,.1)';rr(c,-8.6,by+13.5,17.2,4,3);c.fill()}
 if(armsFront){arm(-1);arm(1)}
 /* neck and collar */
 c.fillStyle=skin;c.fillRect(-2.3,hy+7,4.6,4.2);c.fillStyle='rgba(0,0,0,.14)';c.fillRect(-2.3,hy+8.6,4.6,2.6);
 if(!o.jill){c.fillStyle=shade(top,.26);c.beginPath();c.moveTo(-4.8,by+.4);c.lineTo(0,by+4.8);c.lineTo(4.8,by+.4);c.closePath();c.fill();c.fillStyle='rgba(0,0,0,.12)';c.beginPath();c.moveTo(-3.2,by+.6);c.lineTo(0,by+3.4);c.lineTo(3.2,by+.6);c.closePath();c.fill()}
 if(o.jill){c.fillStyle='#C99A45';for(let k=0;k<3;k++){circ(c,-3,by+5+k*4,.95);circ(c,3,by+5+k*4,.95)}c.strokeStyle='rgba(0,0,0,.1)';c.lineWidth=.6;c.beginPath();c.moveTo(0,by+2);c.lineTo(0,by+17);c.stroke();c.fillStyle='rgba(0,0,0,.05)';rr(c,-8.6,by+9,17.2,8.5,4);c.fill();
  c.fillStyle='#D4553A';c.beginPath();c.moveTo(-5.2,hy+8.3);c.lineTo(5.2,hy+8.3);c.lineTo(0,hy+14);c.fill();c.fillStyle='#B8432C';c.beginPath();c.moveTo(0,hy+14);c.lineTo(-1.5,hy+17);c.lineTo(1.5,hy+17);c.fill();c.fillStyle='rgba(255,255,255,.35)';c.beginPath();c.moveTo(-4.4,hy+8.8);c.lineTo(-1,hy+9.2);c.lineTo(-2.4,hy+11);c.fill();
  c.fillStyle='#F1ECE3';rr(c,-7,base-2+bob,14,5,2);c.fill();c.fillStyle='rgba(0,0,0,.07)';rr(c,-7,base+1+bob,14,2,1);c.fill();c.fillStyle='#C99A45';c.fillRect(-6,by+3,3,1.6)}
 if(L.acc==='tie'){c.fillStyle='#fff';c.beginPath();c.moveTo(-3.8,hy+8.6);c.lineTo(0,hy+12.5);c.lineTo(3.8,hy+8.6);c.fill();c.fillStyle='#A8323A';c.beginPath();c.moveTo(-1.3,hy+11);c.lineTo(1.3,hy+11);c.lineTo(1.8,hy+20);c.lineTo(0,hy+22);c.lineTo(-1.8,hy+20);c.fill();c.fillStyle='rgba(255,255,255,.25)';c.fillRect(-.9,hy+12,.9,7)}
 if(L.acc==='scarf'){c.fillStyle='#E2B04A';rr(c,-6.5,hy+8,13,4.5,2);c.fill();c.fillRect(2,hy+11,3,7);c.fillStyle='rgba(0,0,0,.12)';c.fillRect(2,hy+16,3,2);c.fillStyle='rgba(255,255,255,.2)';rr(c,-5.5,hy+8.8,6,1.2,.6);c.fill()}
 if(L.acc==='backpack'){c.strokeStyle='#3C5470';c.lineWidth=2;c.beginPath();c.moveTo(-5,by+1);c.lineTo(-5,by+11);c.moveTo(5,by+1);c.lineTo(5,by+11);c.stroke()}
 if(L.acc==='shades'){c.strokeStyle='#E6C27A';c.lineWidth=1;c.beginPath();c.moveTo(-4,hy+9);c.quadraticCurveTo(0,hy+15,4,hy+9);c.stroke()}
 if(L.acc==='phone'){c.fillStyle='#222';rr(c,7,base-10+bob,4.5,7,1);c.fill();c.fillStyle='#8FD3F4';c.fillRect(7.8,base-9+bob,2.9,5)}
 if(o.hold&&o.hold!=='camera'){const ph=o.hold==='phone';const hy2=by+9;c.save();c.translate(0,hy2);c.rotate(-.1);c.fillStyle=ph?'#2A2A2E':'#F2EFE8';rr(c,-4.6,-5,9.2,ph?6.6:8.6,1.2);c.fill();c.strokeStyle=OL;c.lineWidth=.5;c.stroke();c.fillStyle=ph?'#9FD8F5':'#FBFAF6';c.fillRect(-3.7,-4,7.4,ph?4.7:6.6);if(ph){c.fillStyle='rgba(255,255,255,.25)';c.fillRect(-3.7,-4,2.2,4.7)}else{c.fillStyle='rgba(0,0,0,.2)';for(let k=0;k<4;k++)c.fillRect(-2.8,-2.7+k*1.5,5.6-(k===3?2.2:0),.6)}c.restore();
  c.fillStyle=skin;const rh=o.flipPage?-2.4:0;rr(c,-9.4,hy2-1,5,3.4,1.7);c.fill();rr(c,4.4,hy2-1+rh,5,3.4,1.7);c.fill();circ(c,-5.4,hy2+1.4,2.2);circ(c,5.4,hy2+1.4+rh,2.2)}
 /* head */
 c.fillStyle='rgba(0,0,0,.12)';el(c,0,hy+9.4,6.2,1.6);
 let hg=c.createRadialGradient(-3,hy-3,1,0,hy,11);hg.addColorStop(0,shade(skin,.12));hg.addColorStop(1,shade(skin,-.08));c.fillStyle=hg;circ(c,0,hy,9.6);c.strokeStyle=OL;c.lineWidth=.7;c.beginPath();c.arc(0,hy,9.6,0,7);c.stroke();
 c.fillStyle=shade(skin,-.06);circ(c,-9.3,hy+1.6,1.8);circ(c,9.3,hy+1.6,1.8);c.fillStyle='rgba(200,110,90,.35)';circ(c,-9.3,hy+1.7,.8);circ(c,9.3,hy+1.7,.8);
 /* hair on top */
 c.fillStyle=hair;
 if(L.hs===5){c.beginPath();c.arc(0,hy-.5,9.9,Math.PI*1.05,Math.PI*1.95);c.fill();el(c,-9,hy,1.8,4);el(c,9,hy,1.8,4);c.fillStyle='rgba(255,255,255,.2)';el(c,-3,hy-7.4,3,1.2)}
 else{c.beginPath();c.arc(0,hy-.5,10.3,Math.PI*.98,Math.PI*2.02);c.closePath();c.fill();
  if(L.hs===6){for(const [bx,br] of[[-6.2,3.8],[-1,4.6],[4.6,4]]){c.beginPath();c.arc(bx,hy-7.2,br,0,7);c.fill()}c.beginPath();c.moveTo(-9.6,hy-2);c.quadraticCurveTo(-4,hy-1,-1.5,hy+.5);c.quadraticCurveTo(-3,hy-3.6,-7,hy-5);c.fill()}
  else if(L.hs===7){for(const bx of[-8,-3.5,1.5,6.5]){c.beginPath();c.arc(bx,hy-6.4,4.1,0,7);c.fill()}c.beginPath();c.ellipse(-2.5,hy-5.2,8.3,3.9,-.15,0,7);c.fill()}
  else{c.beginPath();c.ellipse(-2.5,hy-5.2,8.3,3.9,-.15,0,7);c.fill()}
  if(L.hs===8){c.beginPath();c.moveTo(-10,hy-1);c.quadraticCurveTo(-2,hy-2,8.5,hy+2.5);c.lineTo(9.8,hy-3);c.quadraticCurveTo(2,hy-7,-9.6,hy-3.5);c.closePath();c.fill()}
  if(L.hs!==0&&L.hs!==6&&L.hs!==8){c.beginPath();c.ellipse(-8.7,hy+1,2.5,6.3,0,0,7);c.fill();c.beginPath();c.ellipse(8.7,hy+1,2.5,6.3,0,0,7);c.fill()}
  /* volume: a darker edge under the fringe, a highlight on top */
  c.strokeStyle=shade(hair,-.22);c.lineWidth=1;c.beginPath();c.arc(0,hy-.5,9.4,Math.PI*1.12,Math.PI*1.88);c.stroke();
  c.strokeStyle=hairLt;c.lineWidth=1.2;c.beginPath();c.arc(-1,hy-3.2,7,Math.PI*1.15,Math.PI*1.45);c.stroke()}
 if(o.me){c.fillStyle=hair;c.beginPath();c.moveTo(-9.4,hy-2.6);c.quadraticCurveTo(-9.2,hy-9.6,0,hy-10);c.quadraticCurveTo(9.2,hy-9.6,9.4,hy-2.6);for(let i=4;i>=-4;i--)c.lineTo(i*2.15+(i>0?.4:-.4),hy-1.6-(Math.abs(i)%2?0:1.1));c.closePath();c.fill();c.strokeStyle=hairLt;c.lineWidth=.7;c.beginPath();c.moveTo(-3,hy-8);c.quadraticCurveTo(-2,hy-5,-2.6,hy-2.6);c.moveTo(2.6,hy-8);c.quadraticCurveTo(3.4,hy-5,3,hy-2.6);c.stroke()}
 if(L.hs===3){c.fillStyle=hair;circ(c,0,hy-11.5,5);c.strokeStyle=hairLt;c.lineWidth=1;c.beginPath();c.arc(-1,hy-12.5,3,Math.PI,Math.PI*1.5);c.stroke()}
 /* face */
 const gz=o.gaze;if(gz){c.save();c.translate(clamp(gz.x||0,-1,1)*1.3,clamp(gz.y||0,-1,1)*.7)}
 const m=o.mood||'ok';const ex=o.me?(o.expr||(m==='happy'?'smile':'focus')):null;const ink='#2A1C16',iris='#3B2416';
 /* both eyes in one path per layer: whites, irises, pupils, highlights, then lids or lash lines */
 const E=[-3.4,3.4];const pair=(f)=>{c.beginPath();for(const sx of E)f(sx);c.fill()};
 const openEyes=(lid)=>{c.fillStyle='#FFFDF9';pair(sx=>c.ellipse(sx,hy+1.4,1.95,2.25,0,0,7));c.fillStyle=iris;pair(sx=>c.ellipse(sx+.25,hy+1.6,1.3,1.6,0,0,7));c.fillStyle=ink;pair(sx=>c.ellipse(sx+.3,hy+1.8,.75,.95,0,0,7));c.fillStyle='#fff';pair(sx=>{c.moveTo(sx+.15,hy+.9);c.arc(sx-.35,hy+.9,.5,0,7)});
   if(lid>0){c.fillStyle=skin;c.beginPath();for(const sx of E)c.rect(sx-2.2,hy-1.2,4.4,2.6*lid);c.fill();c.strokeStyle=ink;c.lineWidth=.7;c.beginPath();for(const sx of E){c.moveTo(sx-1.9,hy-1+2.6*lid);c.lineTo(sx+1.9,hy-1+2.6*lid)}c.stroke()}
   else{c.strokeStyle='rgba(42,28,22,.6)';c.lineWidth=.55;c.beginPath();for(const sx of E){c.moveTo(sx+Math.cos(Math.PI*1.15)*1.95,hy+1.5+Math.sin(Math.PI*1.15)*1.95);c.arc(sx,hy+1.5,1.95,Math.PI*1.15,Math.PI*1.85)}c.stroke()}};
 const brows=(tilt,lift)=>{c.strokeStyle=hairDk;c.globalAlpha*=.7;c.lineWidth=.7;c.beginPath();for(const sg of[-1,1]){c.moveTo(sg*5.2,hy-3.6+lift-tilt*sg*.5);c.quadraticCurveTo(sg*3.2,hy-4.6+lift,sg*1.6,hy-3.8+lift+tilt*sg*.6)}c.stroke();c.globalAlpha/=.7};
 if(ex==='smile'&&!o.blink){c.strokeStyle=ink;c.lineWidth=1.25;c.beginPath();for(const sx of E){c.moveTo(sx+Math.cos(Math.PI*1.1)*1.9,hy+2.4+Math.sin(Math.PI*1.1)*1.9);c.arc(sx,hy+2.4,1.9,Math.PI*1.1,Math.PI*1.9)}c.stroke();brows(0,-.2)}
 else if(ex==='amused'&&!o.blink){openEyes(0);c.strokeStyle=hairDk;c.globalAlpha*=.7;c.lineWidth=.7;c.beginPath();c.moveTo(-5.2,hy-3.4);c.quadraticCurveTo(-3.2,hy-4.2,-1.6,hy-3.6);c.moveTo(1.6,hy-4.8);c.quadraticCurveTo(3.4,hy-5.8,5.4,hy-5);c.stroke();c.globalAlpha/=.7}
 else if((ex==='soft'||ex==='tired')&&!o.blink){openEyes(ex==='tired'?.55:.4);brows(0,ex==='tired'?.3:0)}
 else if(ex==='focus'&&!o.blink){openEyes(.22);brows(.4,.2)}
 else if(m==='angry'){c.fillStyle=ink;c.fillRect(-4.8,hy+.8,3,1.2);c.fillRect(1.8,hy+.8,3,1.2);c.strokeStyle=hairDk;c.lineWidth=1;c.beginPath();c.moveTo(-5.4,hy-3.4);c.lineTo(-1.6,hy-1.4);c.moveTo(5.4,hy-3.4);c.lineTo(1.6,hy-1.4);c.stroke()}
 else if(o.blink){c.strokeStyle=ink;c.lineWidth=.9;c.beginPath();c.moveTo(-5,hy+1.6);c.lineTo(-1.8,hy+1.6);c.moveTo(1.8,hy+1.6);c.lineTo(5,hy+1.6);c.stroke();brows(0,0)}
 else{openEyes(m==='sad'?.3:0);brows(m==='sad'?-.6:0,m==='sad'?.4:m==='happy'?-.3:0)}
 /* nose, cheeks, mouth */
 c.strokeStyle='rgba(120,70,50,.5)';c.lineWidth=.8;c.beginPath();c.moveTo(.9,hy+3);c.lineTo(1.4,hy+4.3);c.lineTo(.4,hy+4.8);c.stroke();
 c.fillStyle=m==='angry'?'rgba(225,70,50,.5)':'rgba(235,120,110,.36)';c.beginPath();c.ellipse(-5.7,hy+4.3,2.2,1.3,0,0,7);c.moveTo(7.9,hy+4.3);c.ellipse(5.7,hy+4.3,2.2,1.3,0,0,7);c.fill();
 c.strokeStyle='#5A2E22';c.lineWidth=1;c.beginPath();
 if(ex==='amused'){c.moveTo(-1.4,hy+6.3);c.quadraticCurveTo(1.4,hy+7.4,3.2,hy+5.6)}
 else if(ex==='focus'||ex==='tired'){c.moveTo(-1.5,hy+6.4);c.lineTo(1.5,hy+6.4)}
 else if(ex==='soft'){c.arc(0,hy+4.8,1.9,.45,Math.PI-.45)}
 else if(m==='happy'||ex==='smile'){c.arc(0,hy+4.3,2.3,.25,Math.PI-.25);c.stroke();c.fillStyle='rgba(180,80,70,.35)';c.beginPath();c.arc(0,hy+4.3,2.2,.35,Math.PI-.35);c.closePath();c.fill();c.beginPath()}
 else if(m==='sad'){c.arc(0,hy+7.6,2,Math.PI+.45,-.45)}
 else if(m==='angry'){c.moveTo(-2,hy+6.2);c.lineTo(2,hy+5.4)}
 else if(m==='eat'){c.stroke();c.fillStyle='#8A3A2A';el(c,0,hy+5.6,1.5,o.chew?1.4:.6);c.beginPath()}
 else{c.moveTo(-1.6,hy+5.7);c.lineTo(1.6,hy+5.7)}c.stroke();
 if(L.acc==='glasses'||L.acc==='hat'){c.strokeStyle='#3A2A22';c.lineWidth=.9;c.beginPath();c.arc(-3.4,hy+1.4,2.7,0,7);c.moveTo(-.7,hy+1.4);c.lineTo(.7,hy+1.4);c.arc(3.4,hy+1.4,2.7,Math.PI,Math.PI*3);c.stroke();c.fillStyle='rgba(255,255,255,.18)';el(c,-3.4,hy+1.4,2.4,2.4);el(c,3.4,hy+1.4,2.4,2.4)}
 if(L.acc==='shades'){c.fillStyle='#161618';rr(c,-6.4,hy-.4,5.4,3.4,1.4);c.fill();rr(c,1,hy-.4,5.4,3.4,1.4);c.fill();c.fillRect(-1,hy+.4,2,.9);c.fillStyle='rgba(255,255,255,.3)';c.fillRect(-5.6,hy,1.4,.8)}
 if(gz)c.restore();
 if(L.acc==='beret'){c.fillStyle='#7A2E3A';c.save();c.translate(-1,hy-8.5);c.rotate(-.2);el(c,0,0,10.5,4);c.fillStyle='rgba(255,255,255,.12)';el(c,-3,-1,5,1.4);c.restore();c.fillRect(-1.5,hy-14,2,3)}
 if(L.acc==='hat'){c.fillStyle='#34302D';el(c,0,hy-6.5,13,3.2);rr(c,-7,hy-15,14,9,3);c.fill();c.fillStyle='#8E6A3A';c.fillRect(-7,hy-8.6,14,2);c.fillStyle='rgba(255,255,255,.08)';rr(c,-6,hy-14,4,7,2);c.fill()}
 if(L.acc==='bow'){c.fillStyle='#E8798A';c.beginPath();c.moveTo(6,hy-8);c.lineTo(11,hy-11);c.lineTo(11,hy-5);c.closePath();c.fill();c.beginPath();c.moveTo(6,hy-8);c.lineTo(1,hy-11);c.lineTo(1,hy-5);c.closePath();c.fill();c.fillStyle='#C4506A';circ(c,6,hy-8,1.6)}
 /* 'camera': the phone raised beside the face, turned sideways, pointed where the gaze goes; drawn over the head */
 if(o.hold==='camera'){const dir=o.gaze?Math.sign(o.gaze.x)||1:1;const px=dir*9.5,py=hy+2;c.save();c.translate(px,py);c.rotate(dir*.25);c.fillStyle='#2A2A2E';rr(c,-2.6,-4.6,5.2,9.2,1.2);c.fill();c.strokeStyle=OL;c.lineWidth=.5;c.stroke();c.fillStyle='#9FD8F5';c.fillRect(-1.9,-3.8,3.8,7.2);c.fillStyle='rgba(255,255,255,.3)';c.fillRect(-1.9,-3.8,1.4,7.2);c.restore();c.fillStyle=skin;circ(c,px-dir*1.5,py+4.6,2.3);circ(c,px+dir*1.2,py-4.4,2)}
 if(o.jill&&o.hat!==false){let tg=c.createLinearGradient(-8,0,8,0);tg.addColorStop(0,'#FFFFFF');tg.addColorStop(1,'#E6E0D6');c.fillStyle=tg;rr(c,-7.6,hy-22,15.2,12,2.5);c.fill();c.fillStyle='#FFFFFF';circ(c,-5.5,hy-22,5.4);circ(c,0,hy-25,6);circ(c,5.5,hy-22,5.4);c.strokeStyle='rgba(120,100,80,.35)';c.lineWidth=.6;c.beginPath();c.arc(-5.5,hy-22,5.4,Math.PI*.9,Math.PI*1.9);c.arc(0,hy-25,6,Math.PI*1.1,Math.PI*1.9);c.arc(5.5,hy-22,5.4,Math.PI*1.1,Math.PI*2.1);c.stroke();c.strokeStyle='rgba(0,0,0,.08)';for(let k=-4;k<=4;k+=4){c.beginPath();c.moveTo(k,hy-19);c.lineTo(k,hy-11);c.stroke()}c.fillStyle='#EDE7DC';c.fillRect(-7.6,hy-12.5,15.2,2.2);c.fillStyle='rgba(0,0,0,.06)';c.fillRect(-7.6,hy-10.6,15.2,.8)}
 c.restore()}

const JILL_LOOK={skin:'#F5D2B8',hair:'#1C1816',hs:4,top:'#fff',pants:'#2E2A28'};
function makeLooks(type,size){const P=LOOKS[type]||LOOKS.office;const out=[];for(let k=0;k<size;k++){const L={skin:pick(SKIN),hair:pick(HAIR),hs:pick([0,0,1,2,3,4,6,6,7,8]),top:pick(P.top),acc:pick(P.acc),pants:P.pants};const pr=Math.random();if(pr<.16)L.pat='stripes';else if(pr<.26)L.pat='dots';else if(pr<.42){L.pat='cardi';L.top2=pick(P.top)}if(type==='couple'&&k===1){L.acc='bow';L.hs=pick([1,2,4,7,8])}if(type==='couple'&&k===0)L.acc=null;if(type==='student'&&k>0)L.acc=pick(['backpack',null]);if(type==='family'&&k===size-1&&size>=3){L.kid=true;L.acc=null;L.hs=pick([0,3,4,6,6]);L.top=pick(['#F4C44E','#E8798A','#7FB3C8','#5E9E3D','#F0932B']);L.pat=Math.random()<.5?'stripes':null;L.top2=null;L.hair=pick(HAIR.slice(0,3))}out.push(L)}return out}
/* the face on a ticket: regulars and Dylan have their own, other guests get one for the day (cleared each night) */
function guestPortrait(g){if(g.reg==='dylan')return portraitURL(DYLAN.looks,'regdylan');if(g.reg&&REG_BY[g.reg])return portraitURL(REG_BY[g.reg].looks,'reg'+g.reg);return portraitURL(g.looks,'g'+S.day+'_'+g.id)}
function portraitURL(looks,key,jill){const k='p'+key;if(ICACHE.has(k))return ICACHE.get(k);const cv=mkCanvas(112),c=cv.getContext('2d');c.fillStyle='#F3E7D2';c.fillRect(0,0,112,112);c.scale(3.2,3.2);
 if(looks.length>1){drawPerson(c,11,50,looks[0],{pscale:1,seated:true,mood:'happy'});drawPerson(c,24,50,looks[1],{pscale:1,seated:true,mood:'happy'})}else drawPerson(c,17.5,jill?53:50,looks[0],{pscale:1,seated:true,mood:'happy',jill,me:jill});const u=cv.toDataURL();ICACHE.set(k,u);return u}

/* ================= icons (shop, achievements) ================= */
function iconURL(kind,lv){const k='i'+kind+(lv||0);if(ICACHE.has(k))return ICACHE.get(k);const cv=mkCanvas(112),c=cv.getContext('2d');c.translate(56,60);c.scale(1.12,1.12);
 const steel=(x,y,w,h,r)=>{let g=c.createLinearGradient(x,y,x,y+h);g.addColorStop(0,'#E4E8EA');g.addColorStop(1,'#9DA7AC');c.fillStyle=g;rr(c,x,y,w,h,r);c.fill()};
 switch(kind){
 case 'stove':steel(-36,-10,72,34,6);c.fillStyle='#2A2A2A';rr(c,-34,-16,68,10,4);c.fill();for(const px of[-18,18]){c.fillStyle='#1B1B1B';el(c,px,-12,14,5);c.strokeStyle='#4A7BD8';c.lineWidth=2;c.beginPath();c.ellipse(px,-12,9,3,0,0,7);c.stroke()}c.fillStyle='#C99A45';for(let i=0;i<4;i++)circ(c,-24+i*16,8,3);break;
 case 'pan':c.fillStyle='#2E2E30';el(c,-6,0,26,14);c.fillStyle='#4A4A4E';el(c,-6,-2,22,11);c.fillStyle='#6B3A22';rr(c,16,-5,26,7,3);c.fill();c.fillStyle='#C99A45';c.fillRect(16,-5,4,7);c.fillStyle='#B2463E';el(c,-8,-3,11,6);gloss(c,-12,-6,5,1.6,.4);break;
 case 'oven':steel(-34,-30,68,58,6);c.fillStyle='#2A2A2A';rr(c,-26,-16,52,34,4);c.fill();c.fillStyle=lv?'#F29A3A':'#554';rr(c,-22,-12,44,26,3);c.fill();if(lv){c.fillStyle='#C7772F';el(c,0,4,14,6)}c.fillStyle='#333';for(let i=0;i<3;i++)circ(c,-16+i*16,-24,3);break;
 case 'bar':{let g=c.createLinearGradient(-26,0,26,0);g.addColorStop(0,'#B7862E');g.addColorStop(.5,'#EBC67A');g.addColorStop(1,'#A37424');c.fillStyle=g;rr(c,-28,-34,56,50,8);c.fill();c.fillStyle='#333';rr(c,-18,-6,36,8,2);c.fill();c.fillStyle='#555';c.fillRect(-4,2,8,6);c.fillStyle='#fff';rr(c,-9,12,18,14,3);c.fill();c.fillStyle='#6B3A1A';el(c,0,13,8,2);c.fillStyle='#2A2A2A';rr(c,-30,26,60,6,2);c.fill();c.fillStyle='#8FD3F4';circ(c,-14,-22,3);circ(c,0,-22,3);break}
 case 'fridge':steel(-26,-38,52,72,6);c.strokeStyle='rgba(0,0,0,.2)';c.lineWidth=1.5;c.beginPath();c.moveTo(-26,-8);c.lineTo(26,-8);c.stroke();c.fillStyle='#777';c.fillRect(16,-30,3,16);c.fillRect(16,0,3,20);c.fillStyle='rgba(160,210,240,.6)';rr(c,-20,-32,28,20,3);c.fill();break;
 case 'ops_flow':{c.strokeStyle='#C99A45';c.lineWidth=4;c.lineCap='round';c.setLineDash([7,6]);c.beginPath();c.moveTo(-34,22);c.lineTo(-10,22);c.lineTo(-10,-10);c.lineTo(20,-10);c.lineTo(20,-26);c.stroke();c.setLineDash([]);c.fillStyle='#2A1C16';c.beginPath();c.moveTo(20,-34);c.lineTo(12,-22);c.lineTo(28,-22);c.closePath();c.fill();c.fillStyle='#5E8F4E';circ(c,-34,22,6);break}
 case 'ops_wait':{c.fillStyle='#6B4428';for(const x of[-30,-10,10,30]){c.fillRect(x-7,-6,14,5);c.fillRect(x-7,-20,3,20);c.fillRect(x+4,-20,3,20);c.fillRect(x-6,-1,2,16);c.fillRect(x+4,-1,2,16)}c.fillStyle='#E6C27A';c.fillRect(-38,-22,76,3);break}
 case 'ops_room':{c.fillStyle='#3B2A22';c.fillRect(-36,-26,72,54);c.fillStyle='#F3E4C8';c.fillRect(-32,-22,64,46);c.fillStyle='#8A6A42';c.fillRect(-24,4,26,14);c.fillStyle='#C9A86A';c.fillRect(-24,0,26,5);c.fillStyle='#5E8FA8';c.fillRect(6,-12,18,22);c.fillStyle='#F4C44E';circ(c,0,-14,4);break}
 case 'ops_board':{c.fillStyle='#2A1C16';c.fillRect(-30,-30,60,50);c.fillStyle='#3A2A22';c.fillRect(-26,-26,52,42);c.strokeStyle='#F7EDDC';c.lineWidth=2.4;c.lineCap='round';for(let i=0;i<4;i++){c.beginPath();c.moveTo(-18,-16+i*10);c.lineTo(-18+(i%2?26:34),-16+i*10);c.stroke()}c.fillStyle='#6B4428';c.fillRect(-4,20,8,12);break}
 case 'table':c.fillStyle='rgba(0,0,0,.15)';el(c,0,24,30,8);c.fillStyle='#6B4428';c.fillRect(-3,-2,6,26);c.fillStyle='#5A3920';el(c,0,-2,30,12);c.fillStyle='#A86E3E';el(c,0,-5,30,12);c.fillStyle='#fff';el(c,-10,-6,7,4);el(c,10,-6,7,4);break;
 case 'expand':{c.fillStyle='#3B2A22';c.fillRect(-36,-26,72,54);c.fillStyle='#F3E4C8';c.fillRect(-32,-22,64,46);c.fillStyle='#C99A45';c.fillRect(-36,-34,72,10);c.fillStyle='#2A1C16';c.font=`700 8px ${FONT}`;c.textAlign='center';c.fillText('LV '+lv,0,-26);c.fillStyle='#F29A3A';rr(c,-24,-12,18,20,2);c.fill();rr(c,6,-12,18,20,2);c.fill();c.fillStyle='#6B4428';c.fillRect(-6,4,12,20);break}
 case 'plants':c.fillStyle='#C06A3E';c.beginPath();c.moveTo(-12,8);c.lineTo(12,8);c.lineTo(9,30);c.lineTo(-9,30);c.fill();for(let i=0;i<7;i++)leaf(c,Math.cos(i)*12,-8-i*3,24,9,-1.6+i*.5,i%2?'#3F7F32':'#5E9E3D');break;
 case 'lights':c.strokeStyle='#5A4632';c.lineWidth=1.5;c.beginPath();c.moveTo(0,-40);c.lineTo(0,-14);c.stroke();{let g=c.createLinearGradient(-18,0,18,0);g.addColorStop(0,'#A77A2A');g.addColorStop(.5,'#EAC274');g.addColorStop(1,'#9A6E22');c.fillStyle=g;c.beginPath();c.moveTo(-6,-16);c.lineTo(6,-16);c.lineTo(20,4);c.lineTo(-20,4);c.closePath();c.fill();let h=c.createRadialGradient(0,10,1,0,10,34);h.addColorStop(0,'rgba(255,220,140,.9)');h.addColorStop(1,'rgba(255,200,120,0)');c.fillStyle=h;el(c,0,14,34,24);c.fillStyle='#FFF1C4';el(c,0,5,6,3)}break;
 case 'art':c.fillStyle='#C99A45';c.fillRect(-28,-28,56,48);c.fillStyle='#F6EEDF';c.fillRect(-23,-23,46,38);c.fillStyle='#E8A15B';circ(c,8,-10,7);c.fillStyle='#6E9A5E';c.beginPath();c.moveTo(-23,15);c.lineTo(-6,-6);c.lineTo(8,8);c.lineTo(16,0);c.lineTo(23,15);c.fill();break;
 case 'chairs':c.fillStyle=lv>=2?'#3F6B55':'#5E3B22';rr(c,-14,-34,28,30,8);c.fill();c.fillStyle=lv>=2?'#4E8068':'#7A4E2C';el(c,0,-2,18,7);c.fillStyle=lv>=2?'#C99A45':'#5E3B22';c.fillRect(-12,2,3,24);c.fillRect(9,2,3,24);break;
 case 'rug':c.save();c.scale(1,.55);c.fillStyle='#8A3A2E';rr(c,-40,-34,80,68,6);c.fill();c.strokeStyle='#E6C27A';c.lineWidth=3;rr(c,-34,-28,68,56,4);c.stroke();c.fillStyle='#2E4A5A';rr(c,-22,-16,44,32,3);c.fill();c.fillStyle='#E6C27A';circ(c,0,0,6);c.restore();break;
 case 'ware':drawPlate(c,true,.5);c.strokeStyle='#C99A45';c.lineWidth=2.4;c.lineCap='round';c.beginPath();c.moveTo(-36,-16);c.lineTo(-36,20);c.moveTo(36,-16);c.lineTo(36,20);c.stroke();break;
 case 'barc':c.fillStyle='#5A3920';c.fillRect(-38,-4,76,30);c.fillStyle='#C99A45';c.fillRect(-40,-8,80,5);c.fillStyle='#3A2A20';c.fillRect(-36,-40,72,26);const bc=['#2E6B4A','#8A2A2A','#C99A45','#3A5A8A','#6B3A5A'];for(let i=0;i<7;i++){c.fillStyle=bc[i%5];rr(c,-32+i*10,-38,6,20,2);c.fill()}break;
 /* 2.0: the projects, the street, the cats' things */
 case 'side':c.fillStyle='#8A6A42';rr(c,-30,-34,60,60,6);c.fill();c.fillStyle='#2A1C16';rr(c,-24,-28,48,52,5);c.fill();let sg=c.createLinearGradient(0,-28,0,24);sg.addColorStop(0,'rgba(255,214,150,.1)');sg.addColorStop(1,'rgba(255,214,150,.6)');c.fillStyle=sg;rr(c,-24,-28,48,52,5);c.fill();c.fillStyle='#9FC1D8';c.fillRect(-14,-20,28,16);c.fillStyle='#F3F1EC';c.fillRect(-1,-20,2,16);c.fillRect(-14,-13,28,2);break;
 case 'terrace':c.fillStyle='#8A6A42';c.fillRect(-1.5,-6,3,34);c.fillStyle='#B8536A';c.beginPath();c.moveTo(-34,-4);c.quadraticCurveTo(0,-38,34,-4);c.closePath();c.fill();c.fillStyle='rgba(255,255,255,.3)';c.beginPath();c.moveTo(-34,-4);c.quadraticCurveTo(-16,-28,0,-34);c.lineTo(0,-4);c.closePath();c.fill();c.fillStyle='#F4F1EA';el(c,0,24,22,7);c.fillStyle='#8A6A42';c.fillRect(-8,26,3,10);c.fillRect(5,26,3,10);break;
 case 'kext':c.fillStyle='#9AA3A6';rr(c,-40,-14,80,40,5);c.fill();c.fillStyle='#2E3134';rr(c,-38,-12,76,30,4);c.fill();for(const [px,py] of[[-24,-4],[0,-4],[24,-4],[-24,10],[0,10],[24,10]]){c.fillStyle='#1B1B1D';el(c,px,py,9,4);c.strokeStyle='#4A7BD8';c.lineWidth=1.6;c.beginPath();c.ellipse(px,py,6,2.4,0,0,7);c.stroke()}c.fillStyle='#C99A45';for(let i=0;i<6;i++)circ(c,-30+i*12,22,2);break;
 case 'cooler':c.fillStyle='#8FA0A8';rr(c,-26,-34,52,66,4);c.fill();c.fillStyle='#E4E6E7';rr(c,-22,-30,44,58,3);c.fill();c.fillStyle='#8FA0A8';rr(c,12,-6,5,18,2);c.fill();c.fillStyle='rgba(140,200,230,.45)';rr(c,-16,-24,26,12,2);c.fill();c.fillStyle='#F4F9FC';for(const [x,y] of[[-30,-40],[30,-36],[-34,20]])circ(c,x,y,3);break;
 case 'pass':c.fillStyle='#2A2A2A';c.fillRect(-36,-30,72,3);for(const x of[-22,0,22]){c.fillRect(x-.8,-27,1.6,8);c.fillStyle='#B8536A';c.beginPath();c.moveTo(x-9,-8);c.lineTo(x+9,-8);c.lineTo(x+5,-19);c.lineTo(x-5,-19);c.closePath();c.fill();c.fillStyle='#FFE6A8';el(c,x,-7.5,6,1.6);c.fillStyle='#2A2A2A'}let pg=c.createLinearGradient(0,0,0,26);pg.addColorStop(0,'#D3D7D9');pg.addColorStop(1,'#AEB5B8');c.fillStyle=pg;rr(c,-40,8,80,18,4);c.fill();c.fillStyle='#F4F1EA';for(const x of[-22,0,22])el(c,x,8,9,4);break;
 case 'season':c.fillStyle='#8A3A2A';c.fillRect(-1,-30,2,10);c.fillStyle='#D8392A';el(c,0,-6,16,20);c.fillStyle='#F4C44E';c.fillRect(-7,-26,14,4);c.fillRect(-7,12,14,4);for(let i=0;i<3;i++){c.fillStyle=['#E8798A','#7FB3C8','#5E9E3D'][i];c.beginPath();c.moveTo(-34+i*12,-34);c.lineTo(-24+i*12,-34);c.lineTo(-29+i*12,-22);c.closePath();c.fill()}break;
 case 'bench':c.fillStyle='#6B4428';rr(c,-36,-14,72,8,3);c.fill();rr(c,-36,2,72,8,3);c.fill();c.fillRect(-33,10,5,18);c.fillRect(28,10,5,18);c.fillStyle='#8A6A42';c.fillRect(-36,-14,72,2);break;
 case 'planter':c.fillStyle='#8A3A2A';rr(c,-28,2,56,26,4);c.fill();c.fillStyle='#A64A36';c.fillRect(-28,2,56,4);for(let k=0;k<8;k++)leaf(c,-24+k*7,-4-Math.abs(k-3.5)*4,16,7,-1.6+(k-3.5)*.35,k%2?'#3F7F32':'#5E9E3D');c.fillStyle='#E8798A';circ(c,-10,-12,3.5);c.fillStyle='#F4C44E';circ(c,10,-14,3.5);break;
 case 'signlamp':c.fillStyle='#2C2C2B';rr(c,-36,-6,72,26,4);c.fill();c.strokeStyle='#E0B863';c.lineWidth=1.5;rr(c,-33,-3,66,20,3);c.stroke();c.fillStyle='#E6C27A';c.font=`400 12px ${DFONT}`;c.textAlign='center';c.textBaseline='middle';c.fillText('JILL',0,7.5);c.textBaseline='alphabetic';c.fillStyle='#8E6422';c.fillRect(-2,-18,4,12);c.fillStyle='#F4C44E';el(c,0,-19,9,3);let lg2=c.createRadialGradient(0,-4,2,0,-4,40);lg2.addColorStop(0,'rgba(255,214,120,.5)');lg2.addColorStop(1,'rgba(255,214,120,0)');c.fillStyle=lg2;c.fillRect(-44,-44,88,60);break;
 case 'awning':c.fillStyle='rgba(0,0,0,.15)';c.fillRect(-40,14,80,6);for(let i=0;i<8;i++){c.fillStyle=i%2?'#F7EDDC':'#B8536A';c.beginPath();c.moveTo(-40+i*10,-14);c.lineTo(-30+i*10,-14);c.lineTo(-26+i*10,12);c.lineTo(-36+i*10,12);c.closePath();c.fill()}c.fillStyle='#B8536A';for(let i=0;i<8;i++){c.beginPath();c.arc(-35+i*10,13,5,0,Math.PI);c.fill()}break;
 case 'box':c.fillStyle='#B8905E';c.beginPath();c.moveTo(-30,-10);c.lineTo(30,-10);c.lineTo(30,26);c.lineTo(-30,26);c.closePath();c.fill();c.fillStyle='#8A6A42';c.fillRect(-30,-10,60,4);c.fillStyle='#C9A26E';c.beginPath();c.moveTo(-30,-10);c.lineTo(-40,-24);c.lineTo(-10,-24);c.lineTo(0,-10);c.closePath();c.fill();c.fillStyle='#2A2A2A';el(c,-8,4,3,3);el(c,8,4,3,3);c.fillStyle='#E6A465';circ(c,0,8,12);c.fillStyle='#F7F3EA';el(c,-5,6,2.4,3);el(c,5,6,2.4,3);c.fillStyle='#2A2A2A';el(c,-5,6.5,1,2);el(c,5,6.5,1,2);break;
 case 'cushion':c.fillStyle='rgba(0,0,0,.14)';el(c,0,20,34,9);c.fillStyle='#B8536A';el(c,0,10,34,16);c.fillStyle='#C9687C';el(c,0,6,30,12);c.fillStyle='rgba(255,255,255,.25)';el(c,-8,2,10,4);c.fillStyle='#F7F6F2';el(c,2,-2,18,11);c.fillStyle='#DEDBD6';el(c,-10,-4,5,4);break;
 case 'basket':c.fillStyle='#B08B5E';c.beginPath();c.moveTo(-32,-6);c.quadraticCurveTo(-30,26,0,26);c.quadraticCurveTo(30,26,32,-6);c.closePath();c.fill();c.strokeStyle='rgba(120,80,40,.4)';c.lineWidth=1.2;for(let y=0;y<22;y+=5){c.beginPath();c.moveTo(-30+y*.6,y);c.lineTo(30-y*.6,y);c.stroke()}c.fillStyle='#D8C4A4';el(c,0,-6,32,8);c.fillStyle='#9A8166';el(c,0,-4,18,9);c.fillStyle='#3B2C20';el(c,-8,-6,3,3);el(c,8,-6,3,3);break;
 case 'tunnel':c.fillStyle='#5E8FA8';rr(c,-40,-14,80,30,14);c.fill();c.fillStyle='#2A3A44';el(c,-36,1,8,14);el(c,36,1,8,14);c.fillStyle='rgba(255,255,255,.15)';c.fillRect(-32,-11,64,4);c.fillStyle='#8C7B66';circ(c,34,-2,8);c.fillStyle='#FFFFFF';el(c,34,2,6,4);c.fillStyle='#352A20';el(c,31,-4,2,2.6);el(c,37,-4,2,2.6);break;
 case 'perch':c.fillStyle='#F3F1EC';c.fillRect(-36,-34,72,44);c.fillStyle='#9FC1D8';c.fillRect(-32,-30,64,36);c.fillStyle='#F3F1EC';c.fillRect(-1,-30,2,36);c.fillStyle='#8A6A42';rr(c,-40,10,80,8,2);c.fill();c.fillRect(-34,18,6,12);c.fillRect(28,18,6,12);c.fillStyle='#DCDDDC';el(c,0,4,16,9);c.fillStyle='#222425';for(let k=0;k<3;k++)c.fillRect(-10+k*8,-2,3,10);break;
 case 'lounge':c.fillStyle='rgba(0,0,0,.14)';el(c,0,20,36,10);c.fillStyle='#8FA893';el(c,0,10,36,18);c.fillStyle='#A9BFAC';el(c,0,8,28,12);c.fillStyle='#F7F6F2';el(c,0,4,16,9);c.fillStyle='#DEDBD6';el(c,-9,1,5,4);c.fillStyle='#F4C44E';for(const [x,y] of[[-30,-24],[32,-20],[26,-30]])circ(c,x,y,2.4);break;
 case 'deluxe':c.fillStyle='#8A6A42';c.fillRect(-3,-34,6,60);c.fillStyle='#B8905E';for(const [y,w] of[[-32,30],[-12,40],[8,50]]){rr(c,-w/2,y,w,7,3);c.fill()}c.fillStyle='#F7F6F2';el(c,-6,-38,12,7);c.fillStyle='#DCDDDC';el(c,12,-18,10,6);c.fillStyle='#E6A465';el(c,-12,2,10,6);break;
 case 'sofa':c.fillStyle='#7A2E3A';rr(c,-38,-28,76,30,10);c.fill();c.fillStyle='#8E3A48';rr(c,-40,-4,80,22,8);c.fill();c.fillStyle='#C99A45';c.fillRect(-34,18,4,10);c.fillRect(30,18,4,10);break;
 case 'busser':case 'bartender':case 'cleaner':case 'waiter':drawPerson(c,0,34,kind==='waiter'||kind==='bartender'?{skin:'#F6D3B5',hair:'#4A2E1F',hs:3,top:'#3F6B55',acc:'tie',pants:'#2E2B33'}:{skin:'#E2AE88',hair:'#2B1D16',hs:0,top:'#8FA3B5',pants:'#2E2B33'},{pscale:1,s:1.9,mood:'happy'});break;
 case 'chef':drawPerson(c,0,40,{skin:'#E2AE88',hair:'#2B1D16',hs:0,top:'#FFFFFF',pants:'#2E2B33'},{pscale:1,s:1.7,mood:'happy',jill:true});break;
 case 'star':case 'flame':case 'moon':case 'heart':case 'crown':case 'coin':case 'duck':case 'plate':case 'pen':{let g=c.createRadialGradient(-8,-10,2,0,0,32);g.addColorStop(0,'#F6D98E');g.addColorStop(1,'#B5832E');c.fillStyle=g;circ(c,0,0,32);c.strokeStyle='#8E6422';c.lineWidth=2.5;c.beginPath();c.arc(0,0,26,0,7);c.stroke();c.fillStyle='#6B4712';c.strokeStyle='#6B4712';c.lineWidth=3;c.lineCap='round';
  if(kind==='star'){c.beginPath();for(let i=0;i<10;i++){const r=i%2?7:16,a=-Math.PI/2+i*Math.PI/5;c.lineTo(Math.cos(a)*r,Math.sin(a)*r)}c.fill()}
  else if(kind==='flame'){c.beginPath();c.moveTo(0,16);c.bezierCurveTo(-14,10,-10,-6,0,-18);c.bezierCurveTo(2,-6,12,-2,10,6);c.bezierCurveTo(10,12,6,16,0,16);c.fill()}
  else if(kind==='moon'){c.beginPath();c.arc(0,0,15,0,7);c.fill();c.fillStyle='#E9C57A';c.beginPath();c.arc(7,-5,13,0,7);c.fill()}
  else if(kind==='heart'){c.beginPath();c.moveTo(0,14);c.bezierCurveTo(-20,0,-12,-18,0,-7);c.bezierCurveTo(12,-18,20,0,0,14);c.fill()}
  else if(kind==='crown'){c.beginPath();c.moveTo(-16,10);c.lineTo(-16,-8);c.lineTo(-8,0);c.lineTo(0,-14);c.lineTo(8,0);c.lineTo(16,-8);c.lineTo(16,10);c.fill()}
  else if(kind==='coin'){c.font=`800 26px ${FONT}`;c.textAlign='center';c.textBaseline='middle';c.fillText('$',0,1)}
  else if(kind==='duck'){el(c,-2,4,14,9);circ(c,8,-6,7);c.beginPath();c.moveTo(14,-7);c.lineTo(21,-5);c.lineTo(14,-3);c.fill()}
  else if(kind==='plate'){c.beginPath();c.arc(0,0,15,0,7);c.stroke();c.beginPath();c.arc(0,0,8,0,7);c.stroke()}
  else if(kind==='pen'){c.beginPath();c.moveTo(-12,12);c.lineTo(10,-10);c.stroke();c.beginPath();c.moveTo(-14,14);c.lineTo(-10,8);c.lineTo(-8,10);c.fill()}
  break}
 }
 const u=cv.toDataURL();ICACHE.set(k,u);return u}

/* ================= audio ================= */
const AU={ctx:null};
function audioResume(){const C=AU.ctx;if(!C||C.state==='running'||C.state==='closed')return;try{const p=C.resume();if(p&&p.catch)p.catch(()=>{})}catch(e){}}
function audioInit(){if(AU.ctx){audioResume();return}
 try{const C=new(window.AudioContext||window.webkitAudioContext)();AU.ctx=C;
  AU.master=C.createGain();AU.master.gain.value=.9;AU.master.connect(C.destination);
  AU.music=C.createGain();AU.music.gain.value=S.music?.16:0;AU.music.connect(AU.master);
  AU.sfx=C.createGain();AU.sfx.gain.value=S.sfx?.55:0;AU.sfx.connect(AU.master);
  const len=C.sampleRate*2,b=C.createBuffer(1,len,C.sampleRate),d=b.getChannelData(0);for(let i=0;i<len;i++)d[i]=Math.random()*2-1;AU.noise=b;
  const n=C.createBufferSource();n.buffer=b;n.loop=true;const hp=C.createBiquadFilter();hp.type='highpass';hp.frequency.value=2800;const g=C.createGain();g.gain.value=0;n.connect(hp);hp.connect(g);g.connect(AU.sfx);n.start();AU.siz=g;
  const n2=C.createBufferSource();n2.buffer=b;n2.loop=true;const bp=C.createBiquadFilter();bp.type='bandpass';bp.frequency.value=520;bp.Q.value=2.2;const g2=C.createGain();g2.gain.value=0;n2.connect(bp);bp.connect(g2);g2.connect(AU.sfx);n2.start(0,.7);AU.chat=g2;AU.chatBp=bp;
  AU.next=C.currentTime+.1;AU.step=0;setInterval(musicTick,40);try{C.onstatechange=()=>{if(!document.hidden&&C.state!=='running')setTimeout(audioResume,300)}}catch(e){}}catch(e){AU.ctx=null}}
function setAudio(){if(!AU.ctx)return;AU.music.gain.setTargetAtTime(S.music?.16:0,AU.ctx.currentTime,.1);AU.sfx.gain.setTargetAtTime(S.sfx?.55:0,AU.ctx.currentTime,.05)}
const mf=m=>440*Math.pow(2,(m-69)/12);
function tone(f,dt,dur,type,vol,slide,dest){const C=AU.ctx;if(!C)return;const t=C.currentTime+(dt||0);const o=C.createOscillator();o.type=type||'sine';o.frequency.setValueAtTime(f,t);if(slide)o.frequency.exponentialRampToValueAtTime(slide,t+dur);const g=C.createGain();g.gain.setValueAtTime(.0001,t);g.gain.exponentialRampToValueAtTime(vol||.2,t+.008);g.gain.exponentialRampToValueAtTime(.0001,t+dur);o.connect(g);g.connect(dest||AU.sfx);o.start(t);o.stop(t+dur+.05)}
function noiseHit(dt,dur,freq,q,vol,type,sweep){const C=AU.ctx;if(!C)return;const t=C.currentTime+(dt||0);const s=C.createBufferSource();s.buffer=AU.noise;const f=C.createBiquadFilter();f.type=type||'bandpass';f.frequency.setValueAtTime(freq,t);if(sweep)f.frequency.exponentialRampToValueAtTime(sweep,t+dur);f.Q.value=q||1;const g=C.createGain();g.gain.setValueAtTime(.0001,t);g.gain.exponentialRampToValueAtTime(vol||.3,t+.005);g.gain.exponentialRampToValueAtTime(.0001,t+dur);s.connect(f);f.connect(g);g.connect(AU.sfx);s.start(t,Math.random());s.stop(t+dur+.05)}
const sfx={
 door(){tone(988,0,.7,'sine',.22);tone(784,.2,1,'sine',.22)},
 chop(){noiseHit(0,.05,2600,1.2,.5);tone(170,0,.08,'sine',.3,90)},
 stir(){noiseHit(0,.07,1800,1.5,.22);tone(300+Math.random()*80,0,.05,'triangle',.05)},
 cash(){tone(1318,0,.3,'triangle',.18);tone(1760,.07,.55,'triangle',.18);noiseHit(0,.06,4200,.7,.2)},
 coffee(){noiseHit(0,1,900,.8,.16,'bandpass',3200);tone(110,0,.9,'sawtooth',.02)},
 perfect(){[784,988,1175,1568].forEach((f,i)=>tone(f,i*.06,.55,'sine',.16));tone(2349,.26,.5,'sine',.06)},
 good(){tone(880,0,.25,'sine',.14);tone(1175,.06,.3,'sine',.11)},
 okay(){tone(520,0,.25,'triangle',.1)},
 serve(){tone(2600,0,.12,'sine',.07);tone(3100,.035,.12,'sine',.05)},
 burnt(){noiseHit(0,.55,420,.8,.3,'lowpass');tone(200,0,.4,'sawtooth',.04,90)},
 angry(){tone(330,0,.25,'square',.04,220);tone(220,.2,.35,'square',.04,150)},
 tap(){tone(1400,0,.04,'sine',.05)},
 bubble(){tone(700,0,.12,'sine',.1,1050)},
 ding(){tone(1568,0,.35,'sine',.1);tone(2093,.04,.3,'sine',.05)},
 ticket(){noiseHit(0,.12,3000,2,.08);tone(1200,0,.06,'square',.02)},
 combo(n){tone(560*Math.pow(1.06,Math.min(n,14)),0,.16,'triangle',.11)},
 fire(){tone(220,0,.6,'sawtooth',.05,880);[523,659,784,1047].forEach((f,i)=>tone(f,.15+i*.07,.4,'triangle',.12))},
 buy(){tone(1046,0,.2,'triangle',.14);tone(1568,.08,.4,'triangle',.14)},
 clear(){noiseHit(0,.15,5000,.6,.08);tone(2400,0,.06,'sine',.04);tone(2800,.06,.06,'sine',.04)},
 crack(){noiseHit(0,.05,3000,1.5,.35);tone(900,0,.04,'square',.03)},
 plop(){tone(320,0,.12,'sine',.12,160)},
 pour(){noiseHit(0,.16,700,1.2,.1,'bandpass',1300)},
 shake(){noiseHit(0,.06,6000,1,.12)},
 flip(){noiseHit(0,.22,3000,.6,.25,'highpass');tone(220,0,.1,'sine',.1,140)},
 whisk(){noiseHit(0,.05,4500,2,.15)},
 grind(){noiseHit(0,.13,1600,4,.1)},
 steam(){noiseHit(0,.13,5000,.7,.08,'highpass')},
 meow(){const C=AU.ctx;if(!C)return;const t=C.currentTime;const o=C.createOscillator();o.type='sawtooth';const f=C.createBiquadFilter();f.type='bandpass';f.Q.value=4;const g=C.createGain();const b=520+Math.random()*260;o.frequency.setValueAtTime(b,t);o.frequency.linearRampToValueAtTime(b*1.45,t+.14);o.frequency.linearRampToValueAtTime(b*.85,t+.46);f.frequency.setValueAtTime(900,t);f.frequency.linearRampToValueAtTime(1700,t+.14);f.frequency.linearRampToValueAtTime(800,t+.46);g.gain.setValueAtTime(.0001,t);g.gain.exponentialRampToValueAtTime(.16,t+.04);g.gain.exponentialRampToValueAtTime(.0001,t+.5);o.connect(f);f.connect(g);g.connect(AU.sfx);o.start(t);o.stop(t+.55);for(let i=0;i<8;i++)noiseHit(.5+i*.07,.05,90,1,.18,'lowpass')},
 scratch(){noiseHit(0,.09,2200,1.2,.08)},
 kibble(){for(let i=0;i<6;i++)tone(1800+Math.random()*900,i*.035,.05,'triangle',.05)},
 fridge(){tone(90,0,.5,'sine',.08);noiseHit(0,.3,600,1,.06,'lowpass')},
 shutter(){noiseHit(0,.04,3200,1,.22);noiseHit(.08,.05,2400,1,.18)},
 catPlay(){tone(900,0,.06,'triangle',.04,1300)},
 sizzleStart(){noiseHit(0,.4,4000,.5,.2,'highpass')},
};
const CHORDS=[[53,57,60,64,41],[53,57,60,64,41],[53,58,62,65,43],[52,58,62,67,36],[55,60,64,67,45],[54,57,60,64,38],[53,58,62,65,43],[52,58,62,67,36]];
function ep(m,t,dur,vol){const C=AU.ctx;const f=mf(m);const o=C.createOscillator();o.type='sine';o.frequency.value=f;const o2=C.createOscillator();o2.type='triangle';o2.frequency.value=f*2.001;const g=C.createGain(),g2=C.createGain();g2.gain.value=.1;g.gain.setValueAtTime(.0001,t);g.gain.exponentialRampToValueAtTime(vol,t+.012);g.gain.exponentialRampToValueAtTime(.0001,t+dur);o.connect(g);o2.connect(g2);g2.connect(g);g.connect(AU.music);o.start(t);o2.start(t);o.stop(t+dur+.05);o2.stop(t+dur+.05)}
function bass(m,t,dur){const C=AU.ctx;const o=C.createOscillator();o.type='triangle';o.frequency.value=mf(m);const g=C.createGain();g.gain.setValueAtTime(.0001,t);g.gain.exponentialRampToValueAtTime(.55,t+.01);g.gain.exponentialRampToValueAtTime(.0001,t+dur);o.connect(g);g.connect(AU.music);o.start(t);o.stop(t+dur+.05)}
function shaker(t,v){const C=AU.ctx;const s=C.createBufferSource();s.buffer=AU.noise;const f=C.createBiquadFilter();f.type='bandpass';f.frequency.value=7500;f.Q.value=1.5;const g=C.createGain();g.gain.setValueAtTime(.0001,t);g.gain.exponentialRampToValueAtTime(v,t+.005);g.gain.exponentialRampToValueAtTime(.0001,t+.06);s.connect(f);f.connect(g);g.connect(AU.music);s.start(t,Math.random());s.stop(t+.08)}
function musicTick(){const C=AU.ctx;if(!C||!S.music)return;if(C.currentTime>AU.next+.5)AU.next=C.currentTime+.05;
 const bpm=evening()?82:R&&R.fire>0?126:(R&&R.rush&&R.t>=R.rushT0&&R.t<=R.rushT1)?114:100;const e=60/bpm/2;
 while(AU.next<C.currentTime+.25){const st=AU.step,bar=Math.floor(st/8)%8,pos=st%8,ch=CHORDS[bar],t=AU.next;
  const hits=(Math.floor(st/8)%2===0)?[0,3,6]:[2,5];if(hits.includes(pos))ch.slice(0,4).forEach((m,i)=>ep(m,t+i*.004,e*2.6,.07));
  if(pos===0)bass(ch[4],t,e*2.8);if(pos===3)bass(ch[4]+7,t,e*1.2);if(pos===4)bass(ch[4]+7,t,e*2.6);if(pos===7)bass(ch[4]+12,t,e*.9);
  shaker(t,pos%2?.05:.028);
  if(Math.random()<.2&&pos%2===0){const scale=[0,2,4,7,9];const note=ch[0]+12+scale[Math.floor(Math.random()*5)];ep(note,t,e*3,.045)}
  AU.next+=e;AU.step++}}

/* ================= DOM refs ================= */
const sc=$('#scene'),sctx=sc.getContext('2d'),tc=$('#tray'),tctx=tc.getContext('2d');
const screenEl=$('#screen'),ticketsEl=$('#tickets');
let DPR=1,SV={w:0,h:0,s:1,ox:0,oy:0},TL={cols:1,rows:1,w:100,h:84,pad:8,gap:6,x0:8},bg=null,bgKey='';
let R=null,IDLE=null,phase='title',paused=false,mainScreen='title',sub=null;

/* ================= planning a day ================= */
function applyGates(){if(S.sigEvoNews&&S.signature){const lv=S.sigEvoNews;S.sigEvoNews=0;S.news.push(`<b>招牌菜升級了。</b>${S.signature.name}賣到 ${lv===3?SIG_EVO[2]:SIG_EVO[1]} 份，Jill 把盤子重新做過：${lv===3?'食用花與金箔':'醬汁畫盤與一撮嫩葉'}，價格高 $${(lv-1)*30}。`)}
 if(!S.news21&&S.day>=3){S.news21=S.day;S.news.push('<b>2.1：食物與日常。</b>做熟的菜（熟練度 LV3）可以在<b>菜單研發</b>研發成<b>特製版</b>；招牌菜賣得多會換盤；街上有人經過、有人在門口看菜單就進來；帶小孩的家庭、雨天的傘、廚房裡的空檔。')}
 if(!S.news20&&S.day>=3){S.news20=S.day;S.news.push('<b>2.0：店可以變大了。</b>用餐區上方可以切到<b>店門口</b>和<b>廚房</b>（廚師真的在裡面煮）。打烊後商店裡多了<b>工程</b>（露天座位、大出菜口、冷藏庫、廚房擴建、側廳）和<b>貓的東西</b>；結算會告訴你下一個存錢的目標。')}
 while(S.gate<S.day){S.gate++;const D=S.gate;
 if(D===2){unlockDish('coffee');S.eq.bar=Math.max(1,S.eq.bar);S.news.push('<b>新料理解鎖：拿鐵咖啡</b>。咖啡吧開張了，客人會加點飲料。')}
 if(D===3){if(S.eq.stove<2){S.eq.stove=2}unlockDish('pasta');S.news.push('<b>第二口爐子到貨！</b>同時可以做兩道熱菜。<br><b>新料理：番茄義大利麵</b>（先煮麵，再加醬）。<br>從今天開始可以自己<b>備料</b>與<b>調整售價</b>。')}
 if(D===4){S.eq.prep=1;unlockDish('salad');S.news.push('<b>冷盤台啟用：田園沙拉</b>（Jill 切菜的時候，可以先去忙別的）。<br>今晚 19:00 會有第一次 <b>Rush Hour</b>，做好準備！')}
 if(D===5)S.news.push('昨晚開始可以<b>裝潢與擴建</b>了。菜單研發也有更多選擇。')
 if(D===6)S.news.push('聽說<b>神秘美食評論家</b>最近會在城裡出沒…')
 if(D===8&&!S.signature)S.news.push('Jill 想做一道只屬於自己的料理。晚上可以在商店研發<b>招牌菜</b>（需要擴建到 Bistro）。')
}}
function unlockDish(d){if(!S.unlocked.includes(d))S.unlocked.push(d);if(!S.menu.includes(d)&&S.menu.length<menuCap()){S.menu.push(d);S.menuSince=S.menuSince||{};S.menuSince[d]=S.day}if(!(d in S.xp))S.xp[d]=0}
function expected(weather,event){const D=S.day;const NT=tablesTotal();let g=(3+NT*2.2)*Math.min(1.35,.85+D*.04);g*=.7+(rating()-3)*.18+.3;g*=WEATHER[weather].m*(EVENTS[event].m||1)*(S.buzz||1)*(S.signature?1.1:1)*extAttract();if(NT>=8)g=Math.min(g,NT*dayDur(D)/75);   /* a grown restaurant: a table turns over three or four times in a service at best, more people than that only queue and leave (the small early days keep their own pace) */g=Math.max(D===1?7:5,Math.round(g));
 const people=Math.round(g*1.45);const items=Math.round(people*(D<=1?1:D<=3?1.4:1.7));return{groups:g,people,items}}
function planToday(){if(S.today&&S.today.day===S.day)return;const F=feat();let weather='sun',event='none';
 if(F.events){const prev=S.wxPrev||'sun';const ww={sun:4,cloud:3,rain:2,storm:.9,hot:1.5,cool:1.6};if(prev==='rain'||prev==='storm'){ww.rain*=1.8;ww.storm*=1.5}if(prev==='hot')ww.hot*=1.8;weather=wpick(Object.keys(ww),k=>ww[k]);S.wxPrev=weather;const evs=Object.keys(EVENTS).filter(k=>!EVENTS[k].need||EVENTS[k].need());const cel=(S.stats.days+1)%10===0&&S.stats.days>0;event=cel?'celebrate':Math.random()<.38?'none':pick(evs.filter(k=>k!=='none'&&k!=='celebrate'&&(k!=='vip'||S.day>=5)))||'none'}
 const ex=expected(weather,event);S.today={day:S.day,weather,event,groups:ex.groups,people:ex.people,items:ex.items,tasks:[],reco:null};S.today.tasks=genTasks(ex);S.todayCost=S.todayCost||0}
function genTasks(ex){const D=S.day;const rw=60+D*25;const avgP=menuList().reduce((a,d)=>a+priceOf(d),0)/Math.max(1,menuList().length);
 const all=[{k:'guests',n:Math.max(3,Math.round(ex.people*.75)),t:n=>`服務 ${n} 位客人`},{k:'perfect',n:Math.max(1,Math.round(ex.items*(D<=2?.25:.3))),t:n=>`Perfect × ${n}`},{k:'revenue',n:Math.max(200,Math.round(ex.items*avgP*.65/50)*50),t:n=>`營業額 ${fmt(n)}`}];
 if(D>=3){all.push({k:'combo',n:Math.min(12,3+Math.floor(D/3)),t:n=>`達成 COMBO ×${n}`});all.push({k:'noangry',n:1,t:()=>'沒有客人生氣離開'})}
 if(D>=4){const m=menuList().filter(d=>DISH(d).cat!=='drink'&&stationOk(d));if(m.length){const exp=expectDemand(ex.groups,60);/* pick among the dishes people actually order, weighted by expected sales; ask for about 70% of that */const d=wpick(m,x=>Math.max(.2,exp[x]||0))||pick(m);const e=exp[d]||1;all.push({k:'dish',d,n:Math.max(2,Math.min(12,Math.round(e*.7))),exp:Math.round(e*10)/10,t:n=>`售出 ${DISH(d).n} × ${n}`})}}
 let chosen=D<=2?all.slice(0,3):[all[0],...all.slice(1).sort(()=>Math.random()-.5).slice(0,2)];return chosen.map(x=>({k:x.k,d:x.d,n:x.n,exp:x.exp,txt:x.t(x.n),reward:rw}))}
function taskProg(t){if(!R)return 0;const st=R.st;switch(t.k){case'guests':return st.guests;case'perfect':return st.perfect;case'revenue':return st.rev;case'combo':return R.maxCombo;case'noangry':return st.angry===0?(R.closed?1:0):0;case'dish':return st.dish[t.d]||0}return 0}
/* Advice, not a rule: what today's guests are likely to order (the ordering model itself, sampled — weather, occasion,
   recommendation and prices included), blended with what actually sold on recent days (sales plus emergency orders,
   so a sold-out day counts as the demand it really had), with a buffer for luck. */
function suggestStock(){const ms=menuList().filter(stationOk);const T=S.today;const exp=expectDemand(T?T.groups:10,80);const hist=S.salesHist||{};const out={};
 for(const d of ms){const e=exp[d]||0;const h=hist[d];const base=h!=null?Math.max(e*.85,h*.55+e*.45):e;out[d]=Math.max(2,Math.ceil(base*1.15+1))}
 let tot=Object.values(out).reduce((a,b)=>a+b,0);const cap=fridgeCap();if(tot>cap){const f=cap/tot;for(const d in out)out[d]=Math.max(1,Math.floor(out[d]*f))}return out}
/* what tomorrow's basic restock would cost right now (menu, stock and today's guest estimate) and how much to keep aside */
function restockEstimate(){const sug=suggestStock();let c=0;for(const d of menuList())c+=Math.max(0,(sug[d]||0)-(S.stock[d]||0))*costOf(d);return Math.round(c)}
function keepAside(){return Math.round(restockEstimate()*1.15+100)}
function shopAfterBuy(){const keep=keepAside();if(S.money<keep)toast(`⚠ 現金 ${fmt(S.money)}，可能不足以完成${S.phase==='prep'?'今天':'明天'}的建議備料（約 ${fmt(restockEstimate())}）`,'warn')}
function buyStock(d,delta){const cur=S.stock[d]||0;if(delta>0){const room=fridgeCap()-stockTotal();delta=Math.min(delta,room);const c=costOf(d);delta=Math.min(delta,Math.floor(S.money/c));if(delta<=0)return false;S.money-=delta*c;S.todayCost+=delta*c;S.stock[d]=cur+delta}else{delta=Math.max(delta,-cur);if(delta===0)return false;S.money+= -delta*costOf(d);S.todayCost-= -delta*costOf(d);S.stock[d]=cur+delta}return true}
function autoStock(){const sug=suggestStock();for(const d in sug){const need=sug[d]-(S.stock[d]||0);if(need>0)buyStock(d,need)}}

/* ================= service ================= */
function startService(){lifeReset();streetReset();dylanStageCheck();bg=null;lastEv=null;
 if(S.money<150&&stockTotal()<5){S.money+=300;toast('Jill 翻出了抽屜裡的應急金 $300')}
 if(S.day<=2)autoStock();S.news=[];
 const T=S.today,dur=dayDur(S.day);
 R={t:0,dur,tables:buildTables(),slots:buildSlots(),groups:[],tickets:[],sched:[],si:0,closed:false,ended:false,
  jill:{x:PASS.x,y:PASS.y,tx:null,ty:null,q:[],cur:null,busy:0,carry:[],idle:0,face:1,step:0,room:'main',troom:'main'},
  combo:0,maxCombo:0,streak:0,fire:0,fireCount:0,floats:[],parts:[],tv:1,gid:1,tkid:1,
  st:{rev:0,tips:0,guests:0,groups:0,perfect:0,q:{P:0,G:0,O:0,B:0},sats:[],dish:{},angry:0,lost:0,reviews:[],critic:null,blogger:null,treats:0},
  rush:feat().rush,rushT0:dur*120/270,rushT1:dur*180/270,rushShown:false,weather:T.weather,event:T.event,coach:(S.day===1&&!S.tut)?0:-1,taskDone:{},lastSpawn:0,idleT:0,focus:0,focusLock:0,holdSlot:null,inc:planIncidents(dur),cw:{},thief:null,insp:null,chaser:null};
 R.sched=buildSchedule(dur);R.log=[];logNew=0;phase='service';paused=false;room='main';hideScreen();layoutAll();renderTickets();renderTasks();hud(true);logChip();stockChip();renderRoomTabs(true);
 if(S.reveal&&S.reveal.day<S.day){const P=PROJECTS.find(x=>x.k===S.reveal.k);S.reveal=null;if(P){setTimeout(()=>{if(R&&phase==='service'){jillSay(P.k==='side'?'今天側廳也開放了。':P.k==='terrace'?'外面的桌子也可以坐。':P.k==='kext'?'廚房變大了，今天可以多做一點。':P.k==='cooler'?'冷藏庫今天開始用。':'出菜口變寬了。');logLine('jill',P.n+'：第一天。')}},2500)}}
 banner("OPEN FOR DINNER",LV().n+' 開始營業','');audioInit();sfx.door();
}
function buildSchedule(dur){const T=S.today,n=T.groups,out=[];
 const E=EVENTS[T.event]||{};const dens=x=>{let v=.55+.9*Math.exp(-Math.pow((x-.5)/.16,2));if(S.day>=4)v+=.9*Math.exp(-Math.pow((x-.55)/.08,2));if(x<.06)v*=.3;if(T.weather==='storm'&&x<.45)v*=.6;if(E.late&&x<.4)v*=.55;if(E.early&&x<.4)v*=1.5;return v};
 if(S.day===1){for(let i=0;i<n;i++)out.push({t:1.5+i*(dur*.8/n)})}else for(let i=0;i<n;i++){let x,guard=0;do{x=rand(.02,.9);guard++}while(Math.random()*2.5>dens(x)&&guard<60);out.push({t:x*dur})}
 out.forEach(o=>Object.assign(o,rollGuest()));
 const ev=T.event;
 if(ev==='vip')out.push({t:dur*120/270,type:'vip',size:2});
 if(ev==='concert')for(let k=0;k<4;k++)out.push({t:dur*(.76+k*.02),type:pick(['student','couple','office']),size:ri(1,2)});
 if(ev==='students'){const t0=rand(.3,.55)*dur;for(let k=0;k<3;k++)out.push({t:t0+k*2,type:'student',size:ri(1,2)})}
 if(ev==='blogger')out.push({t:rand(.3,.7)*dur,type:'blogger',size:1});
 if(S.day>=6&&Math.random()<.2)out.push({t:rand(.25,.8)*dur,type:'critic',size:1});
 for(const r of REGS)if(S.day>=r.day){const met=(S.regulars[r.id]||0)>0;const retry=S.regMiss&&S.regMiss[r.id]===S.day-1;if(Math.random()<(E.regs?.95:retry?.8:met?.55:.45))out.push(regPlanVisit({t:rand(.1,.85)*dur,type:r.type,reg:r.id,size:r.size}))}
 if(S.day>=3){const d=S.dylan;/* a recurring person in Jill's life, not a daily spawn: about every other day, less likely right after a visit */const gap=S.day-(d.last||0);const p=S.day<=5?.5:gap<=1?.4:gap>=3?.92:.68;if(Math.random()<p){const late=Math.random()<(d.stage>=2?.75:d.stage>=1?.6:.35);out.push({t:(late?rand(.6,.86):rand(.1,.55))*dur,type:'regular',reg:'dylan',size:1,tries:0})}}
 return out.sort((a,b)=>a.t-b.t)}
function R_hasFour(){const ts=R?R.tables:buildTables();return ts.some(t=>t.seats>=3)}
function guestWeights(){const D=S.day,ev=S.today?S.today.event:'none',L=S.level;const w={office:30*(ev==='company'?3:1),student:D>=2?22:12,couple:D>=2?14*(ev==='valentine'?3:1):0,gourmet:(D>=3?8+L*3:0)*(S.gourmetBoost===D?1.8:1),vip:D>=6?1.5+L*1.5:0,family:D>=4&&R_hasFour()?4+L*1.5:0};const mixE=EVENTS[ev]&&EVENTS[ev].mix;if(mixE)for(const k in mixE)if(w[k])w[k]*=mixE[k];return w}
/* what a markup does, for today's mix of guests: fewer orders (each type by its price sensitivity) and a satisfaction
   penalty at checkout; a discount brings a few more orders and a small bonus. Read straight from the demand model. */
function priceFeel(d){const m=S.price[d]||1;const w=guestWeights();const D=DISH(d);const peers=menuList().filter(x=>stationOk(x)&&DISH(x).cat===D.cat);let sw=0,dem=0,sat=0;
 const share=()=>{let tot=0;for(const k in w){const T=TYPES[k];if(!T||!w[k])continue;let sum=0,me=0;for(const x of peers){const v=demandW(x,T,{stock:false});sum+=v;if(x===d)me=v}tot+=w[k]*(sum?me/sum:0)}return tot};
 const s1=share();S.price[d]=1;const s0=share();S.price[d]=m;dem=s0>0?s1/s0:1;
 for(const k in w){const T=TYPES[k];if(!T||!w[k])continue;sw+=w[k];sat+=w[k]*(m>1?-(m-1)*80*T.sens:(1-m)*30*T.sens)}sat=sw?sat/sw:0;const lbl=m<=.85?'便宜':m<.99?'略低':m<=1.01?'合理':m<=1.15?'偏高':m<=1.3?'貴':'昂貴';const cls=m<=.85?'cheap':m<.99?'cheap':m<=1.01?'fair':m<=1.15?'high':'steep';return{m,lbl,cls,dem:Math.round((dem-1)*100),sat:Math.round(sat)}}
function priceFeelHTML(d){const f=priceFeel(d);if(f.m===1)return`<small class="pf fair">合理・客人照常點</small>`;return`<small class="pf ${f.cls}">${f.lbl}・點的人約 ${f.dem>0?'+':''}${f.dem}%${f.sat?`、滿意度 ${f.sat>0?'+':''}${f.sat}`:''}${f.m<1?'、小費略少':''}</small>`}
function rollGuest(){const D=S.day;const w=guestWeights();
 const type=wpick(Object.keys(w),k=>w[k]);let size=1;if(type==='couple'||type==='vip')size=2;else if(type==='student')size=Math.random()<.5?1:Math.random()<.65?2:3;else if(type==='office')size=Math.random()<.7?1:2;else if(type==='family')size=3;else size=Math.random()<.6?1:2;
 return{type,size,forSig:!!S.signature&&Math.random()<(recoDish()==='signature'?.12:.05),ret:D>=3&&Math.random()<clamp(.06+(rating()-3)*.1,.03,.3)}}
function queueMax(){return LV().q+2*opsLv('wait')+(extOn('bench')?2:0)+(projOn('terrace')?1:0)}
function queued(){return R.groups.filter(g=>g.state==='arrive'||g.state==='queue').sort((a,b)=>a.id-b.id)}
function requeue(){for(const g of queued()){if(g.state==='arrive'&&!g.landed)continue;
 if(g.spot){const ok=g.spot.k==='seat'?!OCC['bench'+g.spot.i]:true;const upgrade=g.spot.k==='stand'&&g.size<=2&&[0,1,2].some(benchFree);if(ok&&!upgrade)continue;g.spot=null}
 const sp=pickSpot(g);g.spot=sp;const p=sp?spotPos(sp):{x:DOOR.x,y:DOOR.y+22};g.troom='main';g.tx=p.x;g.ty=p.y}}
function spawn(o){if(R.closed)return;const reg=o.reg?REG_BY[o.reg]:null;const size=Math.min(o.size,maxSeats(R.tables));if(o.looks&&o.looks.length>size)o.looks=o.looks.slice(0,size);
 const g={id:R.gid++,type:o.type,size,reg:o.reg||null,forSig:!!o.forSig,ret:!!o.ret,looks:o.looks||(reg?reg.looks:makeLooks(o.type,size)),name:o.name||(reg?reg.n:pick(NAMES[o.type]||NAMES.office)),moment:o.moment||null,comp:o.comp||null,alone:o.alone,
  state:'arrive',table:null,pat:1,room:'front',troom:'main',x:FR.enter.x,y:FR.enter.y,tx:DOOR.x,ty:DOOR.y+22,timer:0,ticket:null,seed:Math.random()*10,mood:'ok'};
 if(reg&&(S.regulars[reg.id]||0)>0)g.ret=true;
 if(queued().length>=queueMax()||(!freeTableFor(g)&&!pickSpot(g))){if(g.reg==='dylan'){if((o.tries||0)<2&&R.t<R.dur*.9){R.sched.splice(R.si+1,0,Object.assign({},o,{t:R.t+rand(24,42),tries:(o.tries||0)+1,back:true}));return}R.st.lost+=size;return}if(g.reg){S.regMiss=S.regMiss||{};S.regMiss[g.reg]=S.day}R.st.lost+=size;R.lostRun=(R.lostRun||0)+1;if(!R.lostToastT||R.t-R.lostToastT>40){const n=R.lostRun;R.lostRun=0;R.lostToastT=R.t;toast(n>1?`${g.name} 和另外 ${n-1} 組看到客滿，失望地走了…`:`${g.name} 看到客滿，失望地走了…`)}return}
 if(o.fromStreet){g.x=o.fromStreet.x;g.y=o.fromStreet.y;g.walkIn=1}R.groups.push(g);R.lastSpawn=R.t;requeue();sfx.door();if(g.reg==='dylan'){S.dylan.last=S.day;if(!S.dylan.first)S.dylan.first=S.day;if(o.back)g.back=true}
 if(g.type==='vip')toast('VIP 貴賓到了！消費高，要求也高。');if(g.type==='family')R.st.families=(R.st.families||0)+1;
 if(g.type==='blogger')toast('美食部落客走進來了，手機已經拿出來了。');
 if(g.forSig)quote(g,'我是專程為了 Jill 的招牌菜來的！');
 coach(0)}
function drainRate(g){const T=TYPES[g.type];const base={queue:1/32,order:1/28,wait:1/80,check:1/26}[g.state]||0;let m=1/(T.pat*(g.reg?1.15:1));if(g.reg==='dylan')m*=.5;if(g.reg&&g.reg!=='dylan'){const tier=regTier(S.regulars[g.reg]||0);if(g.reg==='koba'&&!g.unhurried)m*=tier>=1?1.05:1.3;if(tier>=2)m*=.8;else if(tier>=1)m*=.9}if(g.quick)m*=1.15;if(g.state==='queue'&&g.spot&&g.spot.k==='seat')m*=.7;
 m*=1+Math.min(.35,S.day*.012);m*=1-Math.min(.25,ambience()*.02);m*=1-.08*S.decor.chairs;{const wp=WEATHER[R.weather]&&WEATHER[R.weather].pat;if(wp)m/=wp}if(R.musicT>R.t&&(g.state==='queue'||g.state==='arrive'))m*=.7;if(g.catT&&g.catT>R.t)m*=.6;if(!g.rowdy&&g.table!=null&&R.groups.some(o=>o.rowdy&&o.table!=null&&Math.hypot(R.tables[o.table].x-R.tables[g.table].x,R.tables[o.table].y-R.tables[g.table].y)<140))m*=1.7;if(S.day<=2)m*=.62;else if(S.day<=4)m*=.82;return base*m}
function updGroup(g,dt){
 if(['arrive','queue','toTable','leave'].includes(g.state)){const there=stepTo(g,78*dt);if(!there){g.walk=(g.walk||0)+dt*11;g.moving=true}else{g.moving=false;
  if(g.state==='arrive'){g.landed=true;const t=!R.closed&&freeTableFor(g);if(t&&!t.claim){seatGroup(g,t);return}g.state='queue';requeue()}else if(g.state==='toTable'){g.state='reading';g.timer=rand(2.4,3.8)*(TYPES[g.type].read||1)*(S.day===1?.8:1)*(g.usual?.3:1)*(g.reg==='koba'&&!g.unhurried?.55:1)*(g.rushed?.6:1)}else if(g.state==='leave'){if(g.bus){g.bus=false;sendOut(g);sfx.plop()}else{g.gone=true;return}}}}
 if(g.state==='queue'||g.state==='order'||g.state==='wait'||g.state==='check'||g.state==='arrive'){const dr=drainRate(g.state==='arrive'?{...g,state:'queue'}:g);g.pat-=dt*dr;if(g.pat<=0){g.pat=0;angryLeave(g);return}}
 if(g.state==='queue'&&!g.moving){g.notice=(g.notice??rand(2,4))-dt;if(g.notice<=0){g.notice=rand(1.5,3);if(!R.closed){const t=freeTableFor(g);if(t&&!t.claim&&!queued().some(o=>o!==g&&o.id<g.id&&o.size<=t.seats)){seatGroup(g,t);return}}requeue()}
  /* waiting is mostly just sitting; now and then they look around, check a phone, watch a cat, or chat */
  g.wt=(g.wt??rand(1,4))-dt;if(g.wt<=0){g.wt=rand(4,9);const near=CATS?CATS.find(k=>!k.hidden&&Math.hypot(k.x-g.x,k.y-g.y)<110):null;const r=Math.random();g.wact=near&&r<.35?'cat':r<.55?'phone':r<.72?'look':(g.size>1&&r<.86)?'talk':'idle';g.wcat=g.wact==='cat'?near:null}}
 if(g.reg==='dylan'&&g.table!=null&&['reading','order','wait','eat','check'].includes(g.state))dylanGuestUpd(g,dt);
 if(g.state==='reading'){g.timer-=dt;if(g.timer<=0){g.state='order';sfx.bubble()}}
 if(g.state==='eat'){g.timer-=dt;if(g.timer<=0){g.state='check';g.ate=1;sfx.bubble()}}}
function seatGroup(g,t){t.group=g;t.dirty=false;g.table=t.i;g.state='toTable';g.troom=t.room||'main';g.tx=t.x;g.ty=t.y+8;g.pat=Math.min(1,g.pat+.1);requeue();sfx.tap();jillGreet(g,t);if(projOn('side')&&R.tables.some(q=>q.room==='side')&&R.tables.every(q=>q.room==='front'||q.group))ach('sideful');
 if(g.reg&&g.reg!=='dylan'){const m=regMem(g.reg);m.seats[t.i]=(m.seats[t.i]||0)+1;const v=S.regulars[g.reg]||0;if(usualTable(g.reg)===t.i&&v>=4&&Math.random()<.25&&canChat('seat'+g.reg,300,3))setTimeout(()=>{if(R&&phase==='service'&&R.groups.includes(g))quote(g,pick(['老位子。','還是這裡好。','這個位子看得到貓。']))},500);
  const ud=usualDish(g.reg);if(ud&&v>=4&&!g.moment&&Math.random()<.5)g.usual=ud;regSeatMoment(g,t);regMeet(g)}
 if(!g.reg)seatLine(g);coach(1)}
const SEAT_LINES={side:['這邊是新的？','以前這裡是牆吧。','窗邊的位子不錯。','這一間比較安靜。','側廳耶，第一次坐。'],front:['坐外面好舒服。','外面也可以吃了。','今天天氣好，坐外面。','路過的人都在看我們吃什麼。'],grew:['店變大了。','上次來還沒有這間。','這裡越來越像一間真正的餐廳了。'],any:['聽說 Jill 主廚今天在店裡！','朋友說一定要來吃 Jill 的店。','好香喔，是 Jill 在煎東西嗎？','這間店好溫暖，Jill 很會佈置耶。','終於有位子了。','這裡的貓是不是很有名？','上次路過就想進來了。','同事說這裡的炒飯不錯。'],
 rain:['外面雨好大。','傘都濕透了。','下雨天就想喝點熱的。'],storm:['雨大到不想回家。','外面跟颱風一樣。','等雨小一點再走。'],hot:['熱死了，先來杯冰的。','外面像烤箱。','有冷氣真好。'],cool:['今天天氣真舒服。','終於涼了。'],
 ret:['又來了。','上次那道還有嗎？','這次換點別的。'],decor:['這裡換了燈？','店裡不太一樣了。','牆上那幅是新的？'],crowd:['好多人。','聽說很難等到位子。','早知道早點來。']};
function seatLine(g){const W=R.weather;const pools=[];const t=g.table!=null?R.tables[g.table]:null;if(t&&t.room==='side')pools.push(['side',(S.newRooms&&S.day-(S.newRooms.side||0)<=3)?.9:.35]);if(t&&t.room==='front')pools.push(['front',.6]);if(g.ret&&S.newRooms&&Object.values(S.newRooms).some(d=>d&&S.day-d<=2))pools.push(['grew',.7]);if(g.ret)pools.push(['ret',.5]);if(SEAT_LINES[W])pools.push([W,.45]);if(S.newDecor&&S.day-S.newDecor<=2)pools.push(['decor',.5]);if(queued().length>=3)pools.push(['crowd',.3]);pools.push(['any',.35]);
 const k=wpick(pools,p=>p[1])[0];const p=k==='ret'?.4:k==='any'?.14:.3;if(Math.random()<p&&canChat('seat',18,4))quote(g,pick(SEAT_LINES[k]));
 else if(g.ret&&!g.reg&&Math.random()<.3&&canChat('jillret',60,4)){const J=R.jill;if(!J.cur&&!J.q.length&&!J.rest)jillSay(pick(['又來了，歡迎。','歡迎回來。','今天想吃什麼？']))}}
/* now and then someone in the room says something that fits: about the food at the next table, a new dish, a cat,
   the wait; Jill asks a table how it was when she has a moment. One line at a time, with long gaps. */
function ambientTick(dt){if(!R||R.closing!=null)return;R.ambT=(R.ambT||0)+dt;if(R.ambT<1.2)return;R.ambT=0;const c=[];const add=(k,w,f)=>c.push({k,w,f});const J=R.jill;const free=!J.cur&&!J.q.length&&!J.rest&&!J.visit;
 for(const g of R.groups){if(g.table==null||g.reg==='dylan')continue;const t=R.tables[g.table];
  if(g.state==='reading'&&!g.reg){const nb=R.groups.find(o=>o!==g&&o.table!=null&&o.state==='eat'&&o.ticket&&Math.hypot(R.tables[o.table].x-t.x,R.tables[o.table].y-t.y)<110);
   if(nb&&!g.askedNb)add('nexttable',1,()=>{g.askedNb=1;const it=nb.ticket.items.find(i=>i.st==='served');if(!it)return;quote(g,pick(['隔壁桌那個是什麼？','他們那桌吃的看起來不錯。','那個好像很好吃。']));if(Math.random()<.5)g.wantDish=it.d});
   const nd=menuList().find(d=>S.menuSince&&S.menuSince[d]>=S.day-2&&stationOk(d));if(nd&&!g.askedNew)add('newdish',.8,()=>{g.askedNew=1;quote(g,pick([`${dishName(nd)}是新的？`,'菜單上有新東西。','這道以前沒看過。']));if(Math.random()<.45)g.wantDish=nd})}
  if(['reading','wait'].includes(g.state)&&!g.askedCat&&!g.reg){const k=CATS&&CATS.find(k=>!k.hidden&&Math.hypot(k.x-t.x,k.y-t.y)<90);if(k)add('askcat',.9,()=>{g.askedCat=1;quote(g,pick(['這隻貓叫什麼名字？','牠是店裡的貓嗎？','可以摸嗎？','牠都不怕人耶。']));if(free&&J.calm>1)setTimeout(()=>{if(R&&phase==='service')jillSay(pick([`${catName(k.def)}。`,`叫${catName(k.def)}，不怕人。`,`${catName(k.def)}。牠自己會過去。`]))},1300)})}
  if(g.state==='eat'&&!g.checked&&g.ticket&&free&&Math.hypot(J.x-t.x,J.y-t.y)<70)add('check',1.2,()=>{g.checked=1;jillSay(pick(['還可以嗎？','味道還好嗎？','還合口味嗎？']));const it=g.ticket.items.find(i=>i.st==='served');const q=it&&it.q;setTimeout(()=>{if(R&&phase==='service'&&R.groups.includes(g))quote(g,q==='P'?pick(['很好吃。','太好吃了。','這個我喜歡。']):q==='O'?pick(['還可以。','有一點鹹。','普通。']):q==='B'?pick(['有點焦…','下次再來試試。']):pick(['不錯。','好吃。','嗯，可以。']))},1400)});
  if(g.reg==='chen'&&!g.saidTora){const T2=catBy('tora');if(T2&&!T2.hidden&&familiar(g)&&Math.hypot(T2.x-t.x,T2.y-t.y)<90)add('chentora',1,()=>{g.saidTora=1;quote(g,pick(['那隻虎斑今天沒躲我。','虎斑那隻，以前看到我就走。']))})}
  if(g.reg==='koba'&&!g.saidBan){const H=catBy('ban');if(H&&!H.hidden&&Math.hypot(H.x-t.x,H.y-t.y)<60)add('kobaban',.8,()=>{g.saidBan=1;quote(g,'這隻貓每次都來看我吃飯。')})}}
 if(!c.length)return;const pk=wpick(c,o=>o.w);const gap={nexttable:70,newdish:90,askcat:80,check:50,chentora:400,kobaban:400}[pk.k]||60;if(canChat(pk.k,gap,7))pk.f()}
function freeTableFor(g){const ts=R.tables.filter(t=>!t.group&&!t.dirty&&t.seats>=g.size).sort((a,b)=>a.seats-b.seats);
 if(g.reg&&g.reg!=='dylan'&&ts.length){const u=usualTable(g.reg);const ut=u!=null&&ts.find(t=>t.i===u);if(ut&&(S.regulars[g.reg]||0)>=2)return ut;if(g.reg==='wang'&&u==null){/* by the window, as they always ask */return ts.slice().sort((a,b)=>(a.seats-b.seats)||(a.x-b.x)||(a.y-b.y))[0]}}
 if(g.reg==='dylan'&&ts.length){/* a seat that sees Jill at the pass but is not in her way: the free dining-room table farthest from the kitchen; now and then the side room, once there is one */const sd=ts.filter(t=>t.room==='side');if(sd.length&&(g.wantSide||(g.wantSide==null&&(g.wantSide=Math.random()<.35))))return sd[0];const m=ts.filter(t=>t.room==='main');return (m.length?m:ts).slice().sort((a,b)=>(a.seats-b.seats)||(Math.hypot(b.x-PASS.x,b.y-PASS.y)-Math.hypot(a.x-PASS.x,a.y-PASS.y)))[0]}
 if(ts.length){/* the dining room fills first; outdoor tables only in fair weather */const wx=R.weather;const ok=ts.filter(t=>!t.out||(wx!=='rain'&&wx!=='storm'));const pool=ok.length?ok:ts.filter(t=>!t.out);if(!pool.length)return null;const m=pool.filter(t=>t.room==='main');if(m.length&&Math.random()<.7)return m[0];return pool[0]}
 return ts[0]}
function leaveGroup(g,mood){const t=g.table!=null?R.tables[g.table]:null;if(t&&t.group===g)t.group=null;g.state='leave';g.mood=mood||'ok';sendOut(g);
 if(g.ticket){const tk=g.ticket;for(const s of R.slots)if(s.job&&s.job.tk===tk)s.job=null;for(const it of tk.items)if(it.st==='pending')S.stock[it.d]=(S.stock[it.d]||0)+1;R.tickets=R.tickets.filter(x=>x!==tk);R.jill.carry=R.jill.carry.filter(c=>c.tk!==tk);R.tv++;g.ticket=null}}
function angryLeave(g){if(g.state==='queue'||g.state==='arrive'){R.st.lost+=g.size;toast(`${g.name} 等太久，離開了`);g.state='leave';sendOut(g);g.mood='sad';requeue();if(Math.random()<.35)addReview(g,2,pick(['在門口的長椅上等到跟隔壁的陌生人變朋友。','等到腳痠，下次早點來。','客滿，沒等到位子。']),{wait:true,left:true});return}
 const t=R.tables[g.table];const served=g.ticket?g.ticket.items.some(i=>i.st==='served'):false;R.st.angry++;if(R.combo>=3)toast('COMBO 中斷');R.combo=0;R.streak=0;sfx.angry();
 addFloat(t.x,t.y-50,'生氣離開','#E0654A',1,t.room);toast(`${g.name} 生氣地離開了…`);addReview(g,1,null,{wait:true,left:true});leaveGroup(g,'angry');if(served){t.dirty=true}}
/* ---- the day's talk: every line anyone says is kept, so a bubble missed during the rush can be read later ---- */
let logNew=0;
function dayLog(){if(R)return R.log=R.log||[];S.dayLog=S.dayLog||[];return S.dayLog}
function logLine(who,txt,kind){const L=dayLog();L.push({c:R?clockStr():'打烊後',w:who,t:txt,k:kind||'g'});if(L.length>120)L.splice(0,L.length-120);logNew++;logChip()}
function logChip(){const ch=$('#logChip');if(!ch)return;const show=phase==='service'&&!!R;ch.hidden=!show;if(show)$('#logN').textContent=logNew>99?'99+':String(logNew)}
/* a global pace for ambient talk: one line at a time, and each kind of remark keeps its own distance */
function canChat(key,gap,min){if(!R)return false;R.cds=R.cds||{};const now=R.t;if(now-(R.cds._any||-99)<(min==null?7:min))return false;if(now-(R.cds[key]||-999)<gap)return false;R.cds[key]=now;R.cds._any=now;return true}
function quote(g,txt){logLine(g.name,txt,g.reg==='dylan'?'d':'g');toast(`<b>${g.name}</b>：「${txt}」`,'q')}
function staffSay(m,txt){logLine(m.name,txt,'s');toast(`<b>${m.name}</b>：「${txt}」`,'q')}
function noteLine(txt){logLine('',txt,'e');toast(txt)}
/* a dish needs its station in the kitchen before anyone can order it (a recipe found before the station exists waits) */
function stationOk(d){const D=DISH(d);if(!D)return false;const st=D.st;return st==='stove'||!!(S.eq[st])}
/* How likely a guest of type T is to pick dish d, relative to the other dishes in its category. One
   function for everything that reasons about demand: ordering, the stock suggestion, the day's dish
   mission and the hint on the prep screen. Signature is desirable (×1.35) but no longer swallows the
   service by itself; 今日推薦 is the player's lever (×2.4); stars, price and the guest's budget do the rest. */
function demandW(d,T,ctx){const D=DISH(d);if(!D)return 0;let w=(D.pop||1)*((T.pref||{})[D.cat]||1);
 const m=S.price[d]||1;w*=Math.pow(1/m,1+T.sens*1.8);w*=Math.pow(D.price/220,(T.budget-1)*.9);if(T===TYPES.gourmet&&D.diff>=3)w*=1.7;
 if(d==='signature')w*=1.2;if(recoDish()===d)w*=2.2;w*=wxDemand(d)*evDemand(d);w*=1+.25*(starOf(d)-1);
 if(ctx&&ctx.stock!==false&&(S.stock[d]||0)<=0)w*=.6;return w}
/* Set menus the player chooses to offer: a main with a drink, with a dessert, or both. The add-on is a little cheaper
   and a lot more often ordered; à la carte stays. */
const SETS={drink:{n:'主餐＋飲料',d:'點主餐的客人更常加一杯（飲料 −10%）',off:.9},dessert:{n:'主餐＋甜點',d:'點主餐的客人更常加甜點（甜點 −10%）',off:.9},full:{n:'主餐＋飲料＋甜點',d:'全套：飲料和甜點都更常被加點（各 −15%）',off:.85}};
function setOn(k){return!!(S.sets&&S.sets[k])}
function setFor(cat){if(cat==='drink'&&setOn('full'))return'full';if(cat==='drink'&&setOn('drink'))return'drink';if(cat==='dessert'&&setOn('full'))return'full';if(cat==='dessert'&&setOn('dessert'))return'dessert';return null}
function recoDish(){const r=S.today&&S.today.reco;return r&&S.menu.includes(r)&&S.unlocked.includes(r)?r:(r==='signature'&&S.signature?r:null)}
function orderItems(g){const ms=menuList().filter(stationOk);const T=TYPES[g.type];const W=R?R.weather:(S.today?S.today.weather:'sun');
 const wf=d=>demandW(d,T);const reco=recoDish();
 const foods=()=>ms.filter(d=>DISH(d).cat!=='drink'&&DISH(d).cat!=='dessert');const drinks=()=>ms.filter(d=>DISH(d).cat==='drink');const des=()=>ms.filter(d=>DISH(d).cat==='dessert');
 const items=[];const cap=g.size===1?3:g.size===2?4:5;const reg=g.reg?REG_BY[g.reg]:null;
 for(let k=0;k<g.size;k++){let d=null;
  if(k===0&&g.forSig&&ms.includes('signature'))d='signature';
  else if(k===0&&reg&&g.reg==='dylan'){if(ms.includes('signature')&&Math.random()<.35)d='signature';else if(reco&&ms.includes(reco)&&Math.random()<.5)d=reco}
  else if(k===0&&g.usual&&ms.includes(g.usual))d=g.usual;
  else if(k===0&&g.wantDish&&ms.includes(g.wantDish))d=g.wantDish;
  else if(k===0&&g.wantSig&&ms.includes('signature'))d='signature';
  else if(k===0&&reg&&g.reg==='koba'&&!g.unhurried&&Math.random()<.5){const f=foods();if(f.length)d=f.slice().sort((a,b)=>DISH(a).steps.length-DISH(b).steps.length||DISH(a).price-DISH(b).price)[0]}
  else if(k===0&&reg&&g.broke){const f=foods();if(f.length)d=f.slice().sort((a,b)=>priceOf(a)-priceOf(b))[0]}
  else if(k===0&&reg&&g.celebrate){const f=foods();if(f.length)d=f.slice().sort((a,b)=>priceOf(b)-priceOf(a))[0]}
  else if(k===0&&reg){/* a regular has a favourite, but Jill's recommendation can talk them into something else now and then */
   if(reco&&ms.includes(reco)&&DISH(reco).cat!=='drink'&&DISH(reco).cat!=='dessert'&&Math.random()<.3)d=reco;
   else{d=reg.fav.find(f=>ms.includes(f)&&DISH(f).cat!=='drink'&&DISH(f).cat!=='dessert')||null;if(!d){const f=reg.fav.find(f=>ms.includes(f));if(f){items.push(f);continue}}}}
  if(!d){const f=foods();if(f.length)d=wpick(f,wf)}
  if(d)items.push(d);
  const hasMain=!!d&&DISH(d).cat==='main';const pd=(g.reg==='dylan'?.7:(T.pD||.35))*(W==='hot'?1.5:W==='rain'||W==='storm'?1.2:1)*(reco&&DISH(reco).cat==='drink'?1.25:1)*(hasMain&&setFor('drink')?1.6:1);const dr=drinks();if(dr.length&&(Math.random()<pd||!d))items.push(wpick(dr,wf));
  const ds=des();if(ds.length&&Math.random()<(T.pS||.2)*(reco&&DISH(reco).cat==='dessert'?1.4:1)*(g.celebrate?2.2:1)*(g.broke||g.rushed||g.quick?.2:1)*(hasMain&&setFor('dessert')?1.7:1))items.push(wpick(ds,wf))}
 const out=items.filter(Boolean).slice(0,cap);if(g.share){/* one dessert, two forks */let seen=false;return out.filter(d=>{if(DISH(d).cat!=='dessert')return true;if(seen)return false;seen=true;return true})}return out}
/* expected sales per dish for a day like today: the guest mix and the ordering rules themselves, sampled */
function expectDemand(groups,n){const out={};const G=S.today?S.today.groups:groups||10;const N=n||60;
 for(let i=0;i<N;i++){const o=rollGuest();const g={type:o.type,size:o.size,reg:null,forSig:o.forSig};for(const d of orderItems(g))out[d]=(out[d]||0)+1}
 for(const d in out)out[d]=out[d]*G/N;return out}
function createTicket(g){const items=orderItems(g);const t=R.tables[g.table];
 if(!items.length){leaveGroup(g,'ok');return}
 const hasMain=items.some(d=>DISH(d).cat==='main');const tk={id:R.tkid++,no:t.i+1,g,items:items.map(d=>{const cat=DISH(d).cat;const set=hasMain&&(cat==='drink'||cat==='dessert')&&setFor(cat)||null;return{d,st:'pending',q:null,want:d==='steak'?wpick([0,1,2,3],k=>[.2,.35,.3,.15][k]):0,picked:false,set}}),t0:R.t};
 if(g.reg&&g.reg!=='dylan'){const m=regMem(g.reg);for(const it of tk.items)m.orders[it.d]=(m.orders[it.d]||0)+1;if(g.share&&tk.items.some(i=>DISH(i.d).cat==='dessert')&&Math.random()<.5)setTimeout(()=>{if(R&&phase==='service'&&R.groups.includes(g))quote(g,'一份甜點，兩支叉子。')},800)}
 for(const it of tk.items)takeStock(it);if(tk.items.some(it=>it.st==='order')){toast(`食材不夠！Jill 緊急叫貨中（1.5 倍價），${g.name} 要多等一下`);g.pat=Math.min(1,g.pat+.1)}
 g.ticket=tk;g.state='wait';g.pat=Math.min(1,g.pat+.12);R.tickets.push(tk);R.tv++;sfx.ticket();
 if(g.reg==='dylan'){}else if(g.reg){const v=S.regulars[g.reg]||0;const tier=Math.floor(regTier(v));/* not every visit: a line when they are still new, then only now and then */if(tier===0?Math.random()<.5:Math.random()<.35)quote(g,REG_BY[g.reg].l[tier])}else if(g.type==='vip')quote(g,'把你們最好的端上來吧。');else if(Math.random()<.12)quote(g,pick(['今天想吃點好的。','聽說這裡的東西都是 Jill 親手做的？','有推薦的嗎？算了，都點吧。']));
 coach(2)}
function recipeOf(d){return DISH(d).steps}
function uniq(a){return[...new Set(a)]}
function zoneQ(p,z){if(p>=1.22)return'B';if(p>=1)return'O';const d=Math.abs(p-z.c);return d<=z.w?'P':d<=z.g?'G':'O'}
function decoyFor(d,items){if(S.day<3||Math.random()<.4)return[];const st=DISH(d).st;const pool=new Set();for(const x of S.unlocked.concat(S.signature?['signature']:[])){const D=DISH(x);if(!D||D.st!==st)continue;for(const s2 of D.steps)if(s2.t==='add')s2.items.forEach(i=>pool.add(i))}items.forEach(i=>pool.delete(i));const arr=[...pool];return arr.length?[pick(arr)]:[]}
function enterStep(j,i){const st=recipeOf(j.d)[i];const m=mLv(j.d);const k=Object.assign({},st,{p:0,cnt:0,taps:0,mis:0,t0:R.t,scorch:0,last:R.t,hold:false,level:0,auto:0});
 if(st.t==='add'){k.left=st.items.slice();k.btns=shuffle(st.items.concat(decoyFor(j.d,st.items)))}
 if(st.t==='tap')k.n=Math.max(3,st.n-(m-1));
 const V=stepVar(j,i);
 if(st.t==='zone'){const c=(st.c==='want'?[.52,.66,.8,.93][j.it.want]:st.c)+(st.c==='want'?0:V.shift*.6);let w=st.w*(1+.12*(m-1))*V.width;if(DISH(j.d).pan)w*=1+.1*(S.eq.pan-1);if(st.c==='want')w=Math.min(w,.065);k.z={c,w,g:w+.12}}
 if(st.t==='hold'){const wd=.015*(m-1);const mid=(st.a+st.b)/2+V.shift,half=(st.b-st.a)/2*V.width;k.a=Math.max(.05,mid-half-wd);k.b=Math.min(.97,mid+half+wd);k.rate=st.rate*V.rate}
 if(st.t==='work'){k.n=8;k.taps=0;k.wt=0}
 j.si=i;j.step=k}
/* The target of a hold or a flip moves a little: mostly by the day (today's beans grind coarser, today's cream is
   thicker) and a touch per plate. The band on the tray shows the real target, so the hand learns the recipe and the
   eyes do the last bit. Steak doneness is exact — a customer asked for it. */
function stepVar(j,i){const hd=hash(S.day+'|'+j.d+'|'+i),hj=hash(j.seed+'|'+i);const u=(h,k)=>((h>>>(k*8))&255)/255;
 const shift=(u(hd,0)-.5)*.09+(u(hj,0)-.5)*.03;const width=.85+u(hd,1)*.3;const rate=.9+u(hd,2)*.22;return{shift,width,rate}}
function newJob(tk,it){const j={tk,it,d:it.d,si:0,step:null,scores:[],adds:[],burnt:false,t0:R.t,side:0,sear:[0,0],lastZone:0,mix:0,fill:0,wait:0,overStart:null,overLimit:0,overIdx:-1,overVerb:'',seed:(Math.random()*1e9)|0};enterStep(j,0);return j}
function cookNow(j){return j.step&&j.step.t==='zone'?j.step.p:j.lastZone}
function urgency(j){const k=j.step;if(!k)return 0;if(j.overStart!=null)return 4;if(k.t==='wait'||k.t==='work')return 0;if(k.t==='zone')return k.p>=k.z.c-k.z.g-.12?3:1;if(k.t==='tap'&&k.heat)return 3;return 2}
function advance(s,score){const j=s.job;if(!j)return;j.scores.push(score);const steps=recipeOf(j.d);if(j.si+1<steps.length){enterStep(j,j.si+1);R.tv++}else{const ch=chefHandles(s);if(ch&&!j.plating){/* a chef carries it to the pass and plates it there (finishJob runs when the plate is down) */j.plating={t:0,dur:.7+chefDelay(ch)*.6,x:null};j.step=null;R.tv++}else finishJob(s)}}
function finishJob(s){const j=s.job;if(!j)return;const fin=DISH(j.d).fin;if(fin)for(const f of fin)if(!j.adds.includes(f))j.adds.push(f);const avg=j.scores.length?j.scores.reduce((a,b)=>a+b,0)/j.scores.length:1;const q=j.burnt?'B':avg>=.88?'P':avg>=.68?'G':'O';if(R.holdSlot===s)R.holdSlot=null;plate(s,q)}
function checkOver(j){if(j.overStart==null)return;const over=R.t-j.overStart;if(over>j.overLimit){const bad=over>j.overLimit*2;j.scores[j.overIdx]=bad?.4:.72;toast(`${j.overVerb}${bad?'太久了…':'有點過頭'}`)}j.overStart=null}
function startCook(tk,it,silent){if(!R||it.st!=='pending')return false;const st=DISH(it.d).st;const s=R.slots.find(x=>x.type===st&&!x.job&&!x.broken);if(!s){if(!silent){toast(`${ST_N[st]}都在忙！`);R.slots.filter(x=>x.type===st).forEach(x=>x.flash=1)}return false}
 s.job=newJob(tk,it);it.st='cooking';R.tv++;if(!silent){R.focus=R.slots.indexOf(s);R.focusLock=R.t+1.2;R.panel=true;R.panelT=0;sfx.tap()}coach(3);return true}
function nextPendingFor(type){for(const tk of R.tickets)for(const it of tk.items)if(it.st==='pending'&&DISH(it.d).st===type)return{tk,it};return null}
function ingSfx(id){const k=(ING[id]||{}).k;if(id==='egg')sfx.crack();else if(k==='bottle'||k==='carton')sfx.pour();else if(k==='shaker')sfx.shake();else sfx.plop()}
function actIng(s,id){const j=s.job,k=j&&j.step;if(!k||k.t!=='add'||!k.left.length)return;checkOver(j);const ok=k.order?k.left[0]===id:k.left.includes(id);
 if(ok){k.left.splice(k.left.indexOf(id),1);j.adds.push(id);ingSfx(id);s.pop={id,t:0};if(!k.left.length)advance(s,Math.max(0,1-.3*k.mis))}
 else{k.mis++;s.shake=1;sfx.okay();trayFloat(s,k.order&&k.items.includes(id)?'順序不對':'這道菜不用這個','#FF9A7A')}}
function actDose(s){const j=s.job,k=j&&j.step;if(!k||k.t!=='dose')return;checkOver(j);k.cnt++;j.adds.push(k.ing);ingSfx(k.ing);s.pop={id:k.ing,t:0};if(k.cnt>=k.max+3){trayFloat(s,'太多了！','#FFB27A');advance(s,.3)}}
function actDoseDone(s){const j=s.job,k=j&&j.step;if(!k||k.t!=='dose')return;if(!k.cnt){trayFloat(s,'還沒加喔','#FFD27A');return}const off=k.cnt<k.min?k.min-k.cnt:k.cnt>k.max?k.cnt-k.max:0;trayFloat(s,off===0?'剛剛好':k.cnt<k.min?'少了點':'多了點',off===0?'#9ED08A':'#FFB27A');sfx.tap();advance(s,off===0?1:off===1?.7:.4)}
const CUTADD={veg:'vegmix'};
for(const base in SPECIALS){if(CUTADD[base])CUTADD[SPECIALS[base].id]=CUTADD[base]}
function actTap(s){const j=s.job,k=j&&j.step;if(!k||k.t!=='tap')return;checkOver(j);k.taps++;k.last=R.t;s.shake=1;if(k.heat){sfx.stir();j.mix=Math.max(j.mix,Math.min(1,k.taps/k.n))}else{if(j.d==='souffle')sfx.whisk();else sfx.chop()}
 if(k.taps>=k.n){let sc;if(k.heat)sc=k.scorch<.25?1:k.scorch<.5?.8:.55;else{const e=R.t-k.t0;sc=e<k.n*.45?1:e<k.n*.85?.82:.62;j.cut=true;if(CUTADD[j.d])j.adds.push(CUTADD[j.d])}advance(s,sc)}}
function actZone(s){const j=s.job,k=j&&j.step;if(!k||k.t!=='zone')return;checkOver(j);if(k.p<.25){trayFloat(s,'還太早！','#FFD27A');return}
 j.lastZone=k.p;if(k.p>=1.22){j.burnt=true;trayFloat(s,'焦掉了…','#E0654A');finishJob(s);return}
 const dd=Math.abs(k.p-k.z.c);const sc=k.p>=1?.5:dd<=k.z.w?1:dd<=k.z.g?.8:.5;if(k.verb==='翻面'){j.sear[j.side]=k.p;j.side=1-j.side;j.lastZone=0;s.flipT=.42;sfx.flip()}else sfx.tap();
 trayFloat(s,sc===1?'完美！':sc>=.8?'不錯':k.p<k.z.c?'有點生':'有點過',sc===1?'#FFE38A':sc>=.8?'#9ED08A':'#FFB27A');advance(s,sc)}
function holdStart(s){const j=s.job,k=j&&j.step;if(!k||k.t!=='hold')return;checkOver(j);k.hold=true;k.holdT=0;R.holdSlot=s}
function applyHold(j,k){const v=Math.min(1,k.level);switch(k.ing){case'beans':j.grind=v;break;case'milk':j.foam=v;break;case'soda':case'custard':case'cheesebatter':case'whites':j.fill=v;break;case'caramel':j.car=v;break;case'cream':j.cream=v;break;case'stock':j.stock=v;break;case'butter':j.butter=v;break;default:j.sauce=v;j.sauceC=(ING[k.ing]||{}).c||'#8A4A2A'}if(!j.adds.includes(k.ing))j.adds.push(k.ing)}
function holdEnd(){const s=R&&R.holdSlot;if(!s)return;R.holdSlot=null;const j=s.job,k=j&&j.step;if(!k||k.t!=='hold'||!k.hold)return;k.hold=false;if(k.level<.04)return;let sc;
 if(k.level>=1){sc=.2;trayFloat(s,'溢出來了！','#E0654A')}else if(k.level>=k.a&&k.level<=k.b){sc=1;trayFloat(s,'剛剛好','#9ED08A')}else if(k.level>=k.a-.08&&k.level<=k.b+.08){sc=.75;trayFloat(s,k.level<k.a?'少了一點':'多了一點','#FFD27A')}else{sc=.45;trayFloat(s,k.level<k.a?'太少了':'太多了','#FFB27A')}
 applyHold(j,k);advance(s,sc)}
function updJob(s,dt){const j=s.job,k=j.step;if(!k)return;const sp=dishSpeed(j.d,s.type);
 if(chefAuto(s,dt))return;

 switch(k.t){
 case'wait':k.p+=dt*sp/k.time;j.wait=Math.min(1,k.p);if(k.anim==='stir'){j.mix=Math.max(j.mix,Math.min(1,k.p));k.wt=(k.wt||0)+dt;if(k.wt>.3){k.wt=0;s.shake=.5}}if(k.p>=1){sfx.ding();if(k.over){j.overStart=R.t;j.overLimit=k.over;j.overIdx=j.scores.length;j.overVerb=k.verb}advance(s,1)}break;
 case'zone':k.p+=dt*sp/k.time;if(k.p>=1.5)charcoal(s);break;
 case'work':{if(chefHandles(s)&&!cookPresent(s))break;k.p+=dt*sp/k.time;k.taps=Math.min(k.n,Math.floor(k.p*k.n));k.wt+=dt;if(k.wt>.18){k.wt=0;s.shake=.8;if(Math.random()<.45)(k.board?sfx.chop():sfx.stir())}if(!k.board)j.mix=Math.max(j.mix,Math.min(1,k.p));
  if(k.p>=1){j.cut=true;if(k.board&&CUTADD[j.d]&&!j.adds.includes(CUTADD[j.d]))j.adds.push(CUTADD[j.d]);advance(s,1)}break}
 case'tap':if(k.heat){if(R.t-k.last>.85)k.scorch+=dt*.3/(1+.12*(S.eq.pan-1))*(S.day<=2?.6:1);else k.scorch=Math.max(0,k.scorch-dt*.04);if(k.scorch>=1){j.burnt=true;trayFloat(s,'燒焦了','#E0654A');finishJob(s)}}break;
 case'hold':if(k.hold){k.holdT=(k.holdT||0)+dt;if(k.holdT>1.3/k.rate+1.5){holdEnd();break}k.level+=dt*k.rate;s.ht=(s.ht||0)+dt;if(s.ht>.13){s.ht=0;k.ing==='beans'?sfx.grind():k.ing==='milk'?sfx.steam():sfx.pour()}if(k.level>=1.04)holdEnd()}break}}
function charcoal(s){const j=s.job;s.job=null;if(R.holdSlot===s)R.holdSlot=null;const it=j.it;R.st.q.B++;R.streak=0;sfx.burnt();trayFloat(s,'焦成木炭了','#E0654A');
 it.st='pending';takeStock(it);toast(it.st==='order'?`${DISH(it.d).n} 焦掉了，食材用完，緊急叫貨中…`:`${DISH(it.d).n} 焦掉了，得重做一份`);R.tv++}
function addXP(d,n){const before=mLv(d);S.xp[d]=(S.xp[d]||0)+n;const after=mLv(d);if(after>before){toast(`熟練度提升：${DISH(d).n} LV${after}`);if(d==='duck'&&after>=5)ach('duck')}}
function plate(s,q){const j=s.job;s.job=null;const it=j.it;if(!R.tickets.includes(j.tk))return;it.st='ready';it.q=q;it.byJill=!j.chef;R.tv++;if(DISH(j.d).special&&!S.firstSpecial){S.firstSpecial=S.day;const px=j.plating&&j.plating.x||200;memo('firstspecial',px,KY.passTop+6,{d:dishName(j.d),room:'kitchen'});logLine('',`第一盤${dishName(j.d)}從出菜口出去了。`,'e')}
 addXP(it.d,q==='P'?2:q==='B'?0:1);R.st.q[q]++;trayFloat(s,QN[q],q==='P'?'#FFD95A':q==='G'?'#9ED08A':q==='O'?'#E6D3B0':'#E0654A');
 if(q==='P'){R.st.perfect++;R.streak++;banner('✨ PERFECT! ✨','','perfect');sfx.perfect();burst('tray',s,'#FFE38A');if(!S.achievements.first)ach('first');if(R.streak>=5&&R.fire<=0){R.streak=0;startFire()}}
 else{R.streak=0;if(q==='B'){sfx.burnt();toast('燒焦了…客人不會太開心')}else if(q==='G')sfx.good();else sfx.okay()}
 coach(4)}
function startFire(){R.fire=15;R.fireCount++;banner("JILL'S ON FIRE",'Rush Mode：出菜更快、小費 ×1.5','fire');sfx.fire();ach('fire')}
function checkAllServed(g){if(g.ticket&&g.ticket.items.length&&g.ticket.items.every(it=>it.st==='served')&&g.state==='wait'){g.state='eat';g.timer=rand(7,11)*(TYPES[g.type].eat||1)*(S.day<=2?.8:1)*(R.weather==='storm'?1.2:1)*(g.quick||g.rushed?.7:1)*(g.unhurried?1.3:1);g.eatDur=g.timer}}
function serveItems(g,list){const t=R.tables[g.table];let best=null;
 for(const c of list){const it=c.it;if(it.st!=='ready')continue;it.st='served';t.plates.push({d:it.d,q:it.q,want:it.want});g.pat=Math.min(1,g.pat+.12);
  if(it.q==='P'||it.q==='G'){R.combo++;R.maxCombo=Math.max(R.maxCombo,R.combo);if(R.combo>=2){showCombo();sfx.combo(R.combo)}if(R.combo>=10)ach('combo10')}else{if(R.combo>=3)toast('COMBO 中斷');R.combo=0;hideCombo()}
  R.st.dish[it.d]=(R.st.dish[it.d]||0)+1;if(it.q==='P')best='P'}
 sfx.serve();if(best==='P')burst('scene',{x:t.x,y:t.y-14,room:t.room},'#FFE38A');
 if(list.some(c0=>c0.it.d==='signature')&&Math.random()<.25&&canChat('sig',120,4))quote(g,pick(['這就是招牌菜？','招牌菜長這樣。','終於吃到了。','專程來吃這道的。']));
 else if(list.some(c0=>DISH(c0.it.d)&&DISH(c0.it.d).special)&&Math.random()<.3&&canChat('special',60,4)){const sd=list.find(c0=>DISH(c0.it.d)&&DISH(c0.it.d).special).it.d;const sp=SPECIALS[DISHES[sd].special];quote(g,pick([`${sp.n}，就是這個。`,'特製版長這樣。','這個要拍一下。','比照片還好看。','上面那個是'+ING[sp.top].n+'？','跟一般版差在哪？我看看。']));if(!g.photo&&!g.shot&&Math.random()<.5){g.photo=true;g.shot=true;g.photoT0=R.t+1.2;g.dishShot=sp.n}}
 else if(g.type==='family'&&Math.random()<.3&&canChat('family',60,4))quote(g,pick(['小朋友：「我要那個！」','媽媽：「先吃飯，貓等一下再看。」','小朋友把薯條先搶走了。','爸爸：「這家的貓不怕人。」','小朋友：「牠在看我。」']));
 else if(Math.random()<.12&&canChat('served',25,4))quote(g,pick(['這是 Jill 親手做的嗎？','哇，Jill 主廚的擺盤好美。','聞起來好香…','先拍照，等我一下！','來了來了。','看起來好好吃。','份量剛好。']));
 checkAllServed(g);R.tv++;coach(5)}
/* extra lines a review can draw on when the visit had that in it */
const RVX={cat:{5:['貓來桌邊坐了一下，整晚都值了。','{d}好吃，貓更可愛。'],4:['有貓的餐廳，加分。','貓在腳邊繞，等待都不無聊。'],3:['菜普通，貓很可愛。']},
 wait:{4:['等了一陣子，但{d}值得。'],3:['等得有點久，{d}還可以。','人多，上菜慢了些。'],2:['等太久了，{d}都涼了才想到。','等到快睡著。'],1:['等了半天。']},
 price:{3:['{d}好吃，但價格有點勇敢。'],2:['這個價格，{d}要更好才行。','有點貴。'],1:['貴又慢。']},
 sig:{5:['招牌菜名不虛傳。','為了招牌菜再來一次也願意。'],4:['招牌菜有記憶點。'],3:['招牌菜普通，期待太高了。'],2:['招牌菜今天失常。']},
 treat:{5:['老闆娘請了一杯，人情味滿分。','沒想到會有招待，回家的路上都在笑。'],4:['等久了，老闆娘補了一杯，可以。']},
 decor:{5:['店裡的燈光跟音樂剛剛好。','佈置得像朋友家。'],4:['店裡氣氛很舒服。']},
 wx:{rain:{5:['下雨天躲進來，喝到一碗熱的，幸福。'],4:['雨天的熱湯，剛剛好。'],3:['下雨天人少，服務倒是不慢。']},storm:{5:['外面大雨，裡面暖呼呼。'],4:['雨太大，多坐了一會兒，店家也不趕人。']},hot:{5:['熱到快融化，一杯冰的救回一條命。'],4:['天氣熱，冷飲很及時。'],2:['天氣熱，等得更煩。']},cool:{4:['涼涼的晚上，散步過來吃一頓。']}}};
function reviewText(g,stars,ctx){const pool=RV[stars].slice();const c=ctx||{};const P=(o)=>{if(o&&o[stars])pool.push(...o[stars],...o[stars])};
 if(c.cat)P(RVX.cat);if(c.wait)P(RVX.wait);if(c.price)P(RVX.price);if(c.sig)P(RVX.sig);if(c.treat)P(RVX.treat);if(c.decor)P(RVX.decor);if(c.weather&&RVX.wx[c.weather])P(RVX.wx[c.weather]);return pick(pool)}
function addReview(g,stars,txt,ctx){const top=g.ticket?g.ticket.items.find(i=>i.st==='served')||g.ticket.items[0]:null;const dn=top?DISH(top.d).n:'料理';
 const t=(txt||reviewText(g,stars,ctx)).replace('{d}',dn);const tags=[];const c=ctx||{};if(c.wait)tags.push('wait');if(c.left)tags.push('left');if(c.price)tags.push('price');if(c.q)tags.push('q');if(c.cat)tags.push('cat');if(c.sig)tags.push('sig');if(c.treat)tags.push('treat');
 const r={s:stars,txt:t,name:g.name,day:S.day,w:g.type==='critic'?3:1,critic:g.type==='critic',tags};S.reviews.push(r);if(S.reviews.length>80)S.reviews.shift();R.st.reviews.push(r);return r}
function collect(g){const T=TYPES[g.type];const items=g.ticket.items.filter(i=>i.st==='served');let rev=0,qs=0,pen=0,bon=0;if(g.table!=null&&R.tables[g.table]&&R.tables[g.table].room==='front'&&items.length)ach('terrace');
 for(const it of items){const m=S.price[it.d]||1;rev+=it.set?Math.round(priceOf(it.d)*SETS[it.set].off/5)*5:priceOf(it.d);if(it.set)R.st.sets=(R.st.sets||0)+1;qs+=QV[it.q];pen+=Math.max(0,m-1);bon+=Math.max(0,1-m)}
 const n=Math.max(1,items.length),qa=qs/n;let sat=qa*T.qw+g.pat*100*(1-T.qw);sat-=(pen/n)*80*T.sens;sat+=(bon/n)*30*T.sens;sat+=Math.min(12,ambience()*1.1);sat+=items.reduce((a,it)=>a+starOf(it.d)-1,0)/n*4;if(g.catJoy)sat+=5;if(g.reg)sat+=4;if(g.compl)sat+=g.compl;if(g.strict&&items.some(i=>i.q==='O'||i.q==='B'))sat-=12;if(g.forSig&&items.some(i=>i.d==='signature'))sat+=6;if(items.some(i=>i.d==='signature'&&i.byJill))sat+=3;sat=clamp(sat,0,100);
 let tip=rev*T.tip*Math.pow(sat/80,2)*(R.fire>0?1.5:1)*(1+.04*Math.min(R.combo,10))*(S.decor.ware?1.15:1)*(g.celebrate||g.anniv?1.8:1);if(sat<40)tip=0;if(g.reg==='dylan'&&sat>=40)tip*=1.35;rev=Math.round(rev);tip=Math.round(tip);
 if(g.type==='couple')R.st.couples=(R.st.couples||0)+1;
 S.money+=rev+tip;S.lifetime+=rev+tip;R.st.rev+=rev;R.st.tips+=tip;R.st.guests+=g.size;R.st.groups++;R.st.sats.push(sat);R.st.pats=R.st.pats||[];R.st.pats.push(g.pat);if(pen>0)R.st.pricey=(R.st.pricey||0)+1;if(g.catJoy)R.st.catJoy=(R.st.catJoy||0)+1;if(items.some(i=>i.d==='signature'))R.st.sig=(R.st.sig||0)+items.filter(i=>i.d==='signature').length;
 const t=R.tables[g.table];addFloat(t.x,t.y-42,'+'+fmt(rev),'#FFE38A',1,t.room);if(tip>0)addFloat(t.x+6,t.y-58,'小費 +'+fmt(tip),'#BFE3A8',0,t.room);sfx.cash();burst('coins',{x:t.x,y:t.y-20,room:t.room},'#F4C44E');
 const stars=sat>=86?5:sat>=70?4:sat>=54?3:sat>=36?2:1;
 if(g.type==='critic'){toast('其實剛才那位，是<b>神秘美食評論家</b>！');R.st.critic=sat>=84?'good':sat<55?'bad':'ok';addReview(g,stars,stars>=5?"Jill's Kitchen 是今年最令人驚喜的餐廳。":stars>=4?'Jill 主廚的手藝紮實，值得專程一訪。':'有潛力，但還需要打磨。');if(stars>=5)ach('critic')}
 else if(g.type==='blogger'){R.st.blogger=sat>=78?'good':'ok';addReview(g,stars)}
 else if(g.writer){const r=addReview(g,stars,stars>=5?'朋友帶我來的小店。主廚的菜有自己的個性，會再來。':stars>=4?'朋友推薦的店，水準穩定。':'朋友推薦的店，這次普通。');if(r)r.w=2;if(stars>=4){ach('writer');S.gourmetBoost=S.day+1;S.buzzMsg=S.buzzMsg||'Sophie 的朋友寫了這裡，今天美食家會多一些。'}}
 else if(g.reg==='sophie'&&items.some(i=>i.q==='P')&&(g.wantSig||Math.random()<.3)){const r=addReview(g,Math.max(4,stars),g.wantSig?'招牌菜的醬汁對了。這道可以寫進專欄。':'這家店的水準，是可以寫的。');if(r)r.w=2;quote(g,g.wantSig?'今天的醬汁對了。':'不錯。')}
 else if(g.type==='vip'||(g.reg!=='dylan'&&Math.random()<.55))addReview(g,stars,null,{cat:!!g.catJoy,wait:g.pat<.4,price:pen>0,q:items.some(i=>i.q==='O'||i.q==='B'),sig:items.some(i=>i.d==='signature'),treat:!!g.treated,decor:ambience()>=6,weather:R.weather});
 if(g.reg){S.catFam=S.catFam||{};S.catFam[g.reg]=(S.catFam[g.reg]||0)+1;const before=S.regulars[g.reg]||0;S.regulars[g.reg]=before+1;if(before+1===4){toast(`${g.name} 成為了熟客！`);ach('regular4')}if(g.reg==='dylan'&&before+1>=5)ach('dylan5');if(before+1===12){toast(`${g.name} 成為了 Jill 的老客人！`);ach('oldfriend')}}
 if(g.ret||(g.reg&&(S.regulars[g.reg]||0)>1)){S.returning+=g.size;if(S.returning>=100)ach('loves')}
 if(S.lifetime>=1e6)ach('million');
 if(g.reg!=='dylan'){if(sat>=86&&Math.random()<.22&&canChat('thanks',35,4))quote(g,pick(['很好吃，謝謝。','下次帶朋友來。','老闆娘手藝真好。',g.catJoy?'貓好可愛。':'會再來。','謝謝招待。']));else if(g.pat<.35&&sat>=70&&Math.random()<.3&&canChat('waitok',70,4))quote(g,pick(['等有點久，不過值得。','人真的很多，還好有等。']));else if(sat<45&&Math.random()<.25&&canChat('meh',70,4))quote(g,pick(['等太久了。','有點貴。','普通。','下次再看看。']))}
 leaveGroup(g,sat>=70?'happy':sat>=45?'ok':'sad');t.dirty=true;coach(6);
 if(g.reg==='dylan'){if(dylanStays())dylanLinger(g,t);else{/* he clears his own table: plate to the pass, then out. A habit, not a job. */t.dirty=false;t.plates=[];t.busT=0;g.bus=true;g.troom='main';g.tx=PASS.x+18;g.ty=PASS.y-2;S.dylan.clues.tidy=(S.dylan.clues.tidy||0)+1}}}

/* ---- Jill ---- */
/* Lines for a familiar face. Tier 1 = 熟客 (5+ visits), tier 2 = 老客人 (20+). Short, and never every visit. */
const REG_CHAT={
 chen:[[['陳伯伯，今天散步走遠了嗎？','走到河邊又走回來，肚子餓了。'],['陳伯伯，今天還是老位子。','老位子看得到貓，好。']],[['陳伯伯，今天氣色很好。','有你的菜吃，氣色能不好嗎。'],['陳伯伯來啦。','嗯，來看看我的貓。']]],
 mia:[[['Mia，今天又加班？','別問了，先給我咖啡。'],['Mia，今天早一點喔。','稿子交出去了，來犒賞自己。']],[['Mia，今天想吃什麼？','妳決定，我相信妳。'],['Mia，還撐得住嗎？','有這裡就撐得住。']]],
 koba:[[['小林，今天不趕？','趕！但這裡不能不來。'],['小林，慢慢吃。','我盡量。']],[['小林，今天也很快？','今天…可以慢一點。'],['小林，坐。','老樣子，謝謝。']]],
 leo:[[['Leo，考試還好嗎？','Jill 姊別提了，先吃飯。'],['Leo，今天吃飽一點。','一定！']],[['Leo，上班習慣了嗎？','習慣了，但還是最想念這裡。'],['Leo，今天想吃什麼？','跟以前一樣就好。']]],
 sophie:[[['Sophie，今天想試什麼？','看你今天的手氣。'],['Sophie 來了。','來看看有沒有進步。']],[['Sophie，今天不寫稿？','今天只是想吃飯。'],['Sophie，老位子。','嗯，這裡最舒服。']]],
 wang:[[['兩位，今天也約會？','每週一次，不能少。'],['靠窗的位子留給你們了。','謝謝 Jill。']],[['兩位，今天是第幾年了？','不告訴妳，反正還會再來。'],['王先生、王太太，慢用。','妳的店也要一直開下去喔。']]]};
/* how well the place knows a regular: 0 stranger, .5 眼熟 (2+ visits), 1 熟客 (4+), 2 老客人 (12+) */
function regTier(v){return v>=12?2:v>=4?1:v>=2?.5:0}
/* ---- what the place has learned about a regular: where they sit, what they order, what happened. No meters: this is
   memory, and the game reads it back as habits (a usual table, a usual order) and as a few lines in the journal. ---- */
function regMem(id){S.regMem=S.regMem||{};return S.regMem[id]=S.regMem[id]||{seats:{},orders:{},facts:[],flags:{},last:{}}}
function regFact(id,txt){const m=regMem(id);if(m.facts.some(f=>f.txt===txt))return;m.facts.unshift({day:S.day,txt});if(m.facts.length>6)m.facts.length=6}
function usualTable(id){const m=regMem(id);let best=null,bn=1;for(const k in m.seats)if(m.seats[k]>bn){bn=m.seats[k];best=+k}return best}
function usualDish(id){const m=regMem(id);let best=null,bn=2;for(const k in m.orders)if(m.orders[k]>bn&&menuList().includes(k)&&(S.stock[k]||0)>0){bn=m.orders[k];best=k}return best}
function regGate(id,key,gapDays){const m=regMem(id);if((m.last[key]||-99)>S.day-gapDays)return false;m.last[key]=S.day;return true}
/* how many "something happened" moments the whole cast may have today: one early on, two later */
function momentsLeft(){S.regDay=S.regDay||{};if(S.regDay.d!==S.day){S.regDay={d:S.day,n:0}}return (S.day<8?1:S.day<16?2:3)-S.regDay.n}
function momentUsed(){S.regDay.n++}
/* the room remembers what people brought: a bag of oranges by the counter, a drawing on the wall, a plant on the sill, flowers */
function propOn(k){const p=S.props&&S.props[k];if(!p)return false;const life={oranges:4,flowers:6}[k];return life?S.day-p<life:true}
function propSet(k){S.props=S.props||{};S.props[k]=S.day;bg=null}
/* companions a regular brings: the same friend comes back next time */
function compLooks(id,kind,n){const m=regMem(id);m.comp=m.comp||{};if(!m.comp[kind]||m.comp[kind].length<n){const type=kind==='coworker'?'office':kind==='classmates'?'student':kind==='writer'?'gourmet':kind==='friend'?'regular':'office';m.comp[kind]=makeLooks(type,n)}return m.comp[kind].slice(0,n)}
/* decided when the visit is scheduled: alone or with someone, and which small thing today is about (or nothing at all) */
function regPlanVisit(o){const id=o.reg;if(!id||id==='dylan')return o;const r=REG_BY[id];const v=S.regulars[id]||0;const tier=regTier(v);const m=regMem(id);o.size=r.size;o.looks=r.looks;o.name=r.n;
 if(v<1||momentsLeft()<=0||Math.random()<.3)return o;   /* many visits are just visits */
 const W=[];const add=(k,w)=>{if(w>0)W.push([k,w])};
 if(id==='chen'){add('walk',1);if(tier>=1&&S.day>=8&&!propOn('oranges'))add('oranges',1.2);if(tier>=1&&S.unlocked.includes('salad'))add('veg',.8);if(tier>=1&&S.day>=10)add('friend',1);if(tier>=2)add('students',.8)}
 if(id==='mia'){add('deadline',1.2);if(tier>=.5)add('delivered',1);if(tier>=1&&S.day>=9)add('coworker',1);if(tier>=1&&!m.flags.drawing)add('drawing',.9);if(tier>=2)add('moved',.6)}
 if(id==='koba'){if(tier>=.5)add('late',1);if(tier>=1&&S.day>=12&&!m.flags.promo)add('promo',1.4);if(tier>=2&&!m.flags.newjob)add('newjob',.6)}
 if(id==='leo'){if(tier<1)add('broke',1);if(tier>=.5)add('payday',1);if(tier>=1&&S.day>=8)add('classmates',1.1);add('exam',.7);if(tier>=1&&S.day>=12&&!m.flags.plant)add('plant',.9);if(tier>=2&&!m.flags.jobhunt)add('jobhunt',.6)}
 if(id==='sophie'){if(tier>=.5&&S.signature)add('signature',1);if(tier>=1&&S.day>=10)add('writer',.9);add('strict',.6)}
 if(id==='wang'){add('share',1);if(tier>=.5)add('alone',.7);if(tier>=1&&S.day>=10&&!m.flags.anniv)add('anniv',1.3);if(tier>=1&&!propOn('flowers'))add('flowers',.9)}
 if(!W.length)return o;const k=wpick(W,x=>x[1])[0];if(!regGate(id,'moment',2))return o;momentUsed();o.moment=k;
 switch(k){
 case'friend':o.size=2;o.looks=r.looks.concat(compLooks(id,'friend',1));o.comp='friend';break;
 case'coworker':o.size=2;o.looks=r.looks.concat(compLooks(id,'coworker',1));o.comp='coworker';break;
 case'classmates':{const n=Math.random()<.5?1:2;o.size=1+n;o.looks=r.looks.concat(compLooks(id,'classmates',n));o.comp='classmates';break}
 case'writer':o.size=2;o.looks=r.looks.concat(compLooks(id,'writer',1));o.comp='writer';break;
 case'alone':o.size=1;{const who=Math.random()<.5?0:1;o.looks=[r.looks[who]];o.name=who?'王太太':'王先生';o.alone=who}break;
 case'late':o.t=Math.max(o.t,R?R.dur*.72:o.t);break;
 case'deadline':o.t=Math.max(o.t,R?R.dur*rand(.55,.8):o.t);break}
 return o}
/* the first words of a visit, when they sit down */
function regSeatMoment(g,t){const id=g.reg;if(!id||id==='dylan')return;const k=g.moment;const m=regMem(id);const say=(txt,d)=>setTimeout(()=>{if(R&&phase==='service'&&R.groups.includes(g))quote(g,txt)},d||600);
 if(g.comp==='friend'){say(pick(['今天帶老朋友來。','以前教書的同事，退休了才有空。']));regFact(id,'帶了一位老朋友來。');g.memoAt='seat'}
 if(g.comp==='coworker'){say(pick(['同事一直問我都吃哪裡，帶她來了。','今天有伴，不用一個人吃。']));regFact(id,'帶了同事來。');g.memoAt='seat'}
 if(g.comp==='classmates'){say(pick(['同學說想來看貓。','跟同學一起，今天可以點多一點。']));regFact(id,'帶了同學來看貓。');g.memoAt='seat';for(let i=0;i<g.size;i++)g.wantShot=true}
 if(g.comp==='writer'){say('我帶了一位朋友，她在寫餐廳專欄。');regFact(id,'帶了寫專欄的朋友來。');g.memoAt='seat';g.writer=true;g.treat='drink'}
 if(k==='alone'){say(g.alone?pick(['先生今天出差，我一個人來。','一個人也想來。']):pick(['太太今天加班，我一個人。','她說替她點一份甜點帶回去。']));regFact(id,g.alone?'王太太一個人來過。':'王先生一個人來過。')}
 if(k==='walk')say(pick(['今天走到河邊，回來剛好餓了。','散步繞遠了一點。','走一走就到了。']));
 if(k==='students'){say('以前的學生昨天來看我，都當爸爸了。');regFact(id,'以前的學生來看他，都當爸爸了。')}
 if(k==='deadline'){say(pick(['先給我咖啡，稿子還沒交。','今天不能待太久。']));g.rushed=true}
 if(k==='delivered'){say(pick(['稿子交了！今天要吃好一點。','終於交出去了。']));g.celebrate=true;regFact(id,'趕完稿那天，說要吃好一點。')}
 if(k==='moved'){say('搬家了，但還是會繞過來。');regFact(id,'搬家了，還是會來。')}
 if(k==='late'){say(pick(['今天加班，還好還開著。','趕上了。']))}
 if(k==='promo'){say('升職了，今天不趕。');g.celebrate=true;g.unhurried=true;m.flags.promo=1;regFact(id,'升職那天，難得吃了一頓慢的。')}
 if(k==='newjob'){say('換工作了，離這裡遠一點，還是會來。');m.flags.newjob=1;regFact(id,'換了工作，離得遠了。')}
 if(k==='broke'){say(pick(['今天只能點這個。','月底了。']));g.broke=true}
 if(k==='payday'){say('打工薪水下來了！');g.celebrate=true}
 if(k==='exam'){say(pick(['期中考週，吃完就回去唸書。','考完再來好好吃。']));g.quick=true}
 if(k==='jobhunt'){say('快畢業了，開始找工作。');m.flags.jobhunt=1;regFact(id,'快畢業了，在找工作。')}
 if(k==='signature'){say(pick(['今天想看看招牌菜。','招牌菜，我來評分。']));g.wantSig=true}
 if(k==='strict'){g.strict=true}
 if(k==='share'){g.share=true}
 if(k==='anniv'){say('今天是我們的結婚紀念日。');g.anniv=true;g.treat='dessert';m.flags.anniv=1;regFact(id,'結婚紀念日是在這裡過的。')}
 if(['oranges','veg','drawing','plant','flowers'].includes(k))g.gift=k;
 if(g.memoAt==='seat')setTimeout(()=>{if(R&&phase==='service'&&R.groups.includes(g)&&g.table!=null){const tb=R.tables[g.table];memo('company',tb.x,tb.y-6,{g:g.reg==='wang'?'王先生與王太太':REG_BY[g.reg].n,subj:[{x:tb.x-24,y:tb.y},{x:tb.x+24,y:tb.y}]})}},2500)}
/* the gift is handed over when Jill comes to the table (a waiter taking the order leaves it for the checkout) */
function regGift(g,t){const k=g.gift;if(!k)return;g.gift=null;const id=g.reg;const m=regMem(id);
 const lines={oranges:['鄰居送太多橘子，我一個人吃不完，拿一些來。','橘子，朋友種的，太多了。'],veg:['朋友田裡的菜，太多了，分妳一些。','菜園今年收太好，拿來給店裡。'],drawing:['幫店裡畫了個小東西，貼在牆上好嗎？','畫了一張，放店裡吧。'],plant:['宿舍的多肉長太多，分店裡一盆。','這盆放窗邊剛好。'],flowers:['太太種的花，開太多了。','花園裡剪的，放店裡好看。']};
 quote(g,pick(lines[k]));setTimeout(()=>{if(R&&phase==='service')jillSay(pick(['謝謝，我放這裡。','太好了，謝謝你。','這怎麼好意思。']))},1500);
 if(k==='oranges'){propSet('oranges');regFact(id,'拿了一袋橘子來。')}
 if(k==='veg'){if(S.unlocked.includes('salad')&&stockTotal()+2<=fridgeCap()){S.stock.salad=(S.stock.salad||0)+2;noteLine('田園沙拉的料多了 2 份')}regFact(id,'帶了自己種的菜來。')}
 if(k==='drawing'){propSet('drawing');m.flags.drawing=1;regFact(id,'畫了一張小圖，貼在牆上。')}
 if(k==='plant'){propSet('plant');m.flags.plant=1;regFact(id,'送了一盆多肉，放在窗邊。')}
 if(k==='flowers'){propSet('flowers');regFact(id,'帶了自己種的花來。')}
 memo('gift',t.x,t.y-6,{g:g.name,subj:[{x:R.jill.x,y:R.jill.y}]});ach('gift')}
/* two regulars in the room at once, who happen to know each other. Sparingly: once in a while, one pair at a time. */
const REG_PAIRS=[['chen','wang',['王先生，好久不見。','陳老師！']],['mia','koba',['你也在這棟上班？','三樓。你是樓上那間？']],['sophie','leo',['學生，點那道，不會錯。','好、好，那道。']]];
function regMeet(g){if(!g.reg||g.reg==='dylan')return;for(const [a,b,lines] of REG_PAIRS){if(g.reg!==a&&g.reg!==b)continue;const other=R.groups.find(o=>o!==g&&o.reg===(g.reg===a?b:a)&&o.table!=null&&['reading','order','wait','eat'].includes(o.state));if(!other)continue;
  const va=S.regulars[a]||0,vb=S.regulars[b]||0;if(regTier(va)<.5||regTier(vb)<.5)continue;if(!regGate(a,'meet_'+b,5))continue;if(Math.random()>.7)continue;
  const A=g.reg===a?g:other,B=g.reg===a?other:g;setTimeout(()=>{if(R&&phase==='service'&&R.groups.includes(A))quote(A,lines[0])},900);setTimeout(()=>{if(R&&phase==='service'&&R.groups.includes(B))quote(B,lines[1])},2400);
  if(a==='sophie'&&B.state==='reading')B.wantDish=REG_BY.sophie.fav.find(f=>menuList().includes(f))||null;
  const ta=R.tables[A.table],tb=R.tables[B.table];setTimeout(()=>{if(R&&phase==='service'&&R.groups.includes(A)&&R.groups.includes(B))memo('neighbors',(ta.x+tb.x)/2,(ta.y+tb.y)/2-6,{a:A.name,b:B.name,subj:[ta,tb]})},1200);
  regFact(a,`在店裡遇到${REG_BY[b].n}，原來認識。`);regFact(b,`在店裡遇到${REG_BY[a].n}，原來認識。`);return}}
/* ---- hospitality: something on the house. Not a lever the player pulls; Jill decides, it costs stock, at most twice a day. ---- */
function treatPick(kind){const ms=menuList().filter(d=>stationOk(d)&&(S.stock[d]||0)>0);const want=ms.filter(d=>DISH(d).cat===(kind||'dessert'));const alt=ms.filter(d=>DISH(d).cat===(kind==='drink'?'dessert':'drink'));return want[0]||alt[0]||null}
function treatWanted(g){if(!R||R.st.treats>=2||g.treated||g.table==null)return null;const t=R.tables[g.table];if(!t||t.group!==g)return null;
 if(g.treat)return g.treat;   /* an occasion: anniversary, a special visitor */
 if(g.state==='eat'&&g.pat<.32&&!(R.treatT>R.t)){const tier=g.reg?regTier(S.regulars[g.reg]||0):0;if(Math.random()<(tier>=1?.5:.12))return'drink'}return null}
function treatGo(g,kind){const d=treatPick(kind);if(!d)return false;const J=R.jill;const t=R.tables[g.table];g.treated=true;g.treat=null;R.st.treats=(R.st.treats||0)+1;R.treatT=R.t+120;S.stock[d]--;
 J.visit={g,t0:t,phase:'go',kind:'treat',d};J.troom=t.room||'main';J.tx=t.x+(t.x<200?30:-30);J.ty=t.y+20;J.idle=0;return true}
function treatArrive(V){const g=V.g,t=V.t0;if(!R.groups.includes(g)||t.group!==g)return;t.plates.push({d:V.d,q:'P',want:0,treat:true});g.compl=(g.compl||0)+8;g.pat=Math.min(1,g.pat+.15);sfx.serve();
 const txt=g.anniv?'這個請你們，紀念日快樂。':g.writer?'這杯請你們，慢慢喝。':pick(['今天等有點久，這杯算我的。','這個請你，等久了。']);jillSay(txt);setTimeout(()=>{if(R&&phase==='service'&&R.groups.includes(g))quote(g,pick(['謝謝！','怎麼好意思。','Jill，謝謝。']))},1500);
 memo(g.anniv?'anniversary':'treat',t.x,t.y-6,{g:g.name,d:dishName(V.d),subj:[{x:R.jill.x,y:R.jill.y}]});if(g.reg&&g.reg!=='dylan')regFact(g.reg,g.anniv?'紀念日那天，Jill 請了甜點。':`Jill 請過一杯${dishName(V.d)}。`);ach('treat');logLine('',`Jill 請了 ${g.name} 一份${dishName(V.d)}`,'e')}
/* a trip that gets interrupted before it arrives puts the treat back in the fridge */
function cancelVisit(){const J=R&&R.jill;if(!J||!J.visit)return;const V=J.visit;if(V.kind==='treat'&&V.phase==='go'){S.stock[V.d]=(S.stock[V.d]||0)+1;V.g.treated=false;R.st.treats=Math.max(0,(R.st.treats||0)-1)}J.visit=null}
/* Jill looks for someone to treat when she has a moment */
function treatTick(){if(!R||R.closing!=null)return;const J=R.jill;if(J.visit||J.rest||J.pet||J.cur||J.q.length||jillWorkload()>1||J.idle<.8)return;for(const g of R.groups){if(g.table==null||!['wait','eat'].includes(g.state))continue;const k=treatWanted(g);if(k&&treatGo(g,k))return}}
const TIER_N={0:'陌生人',.5:'有點眼熟',1:'熟客',2:'Jill 的老客人'};
function jillSay(txt){logLine('Jill',txt,'j');toast(`<b>Jill</b>：「${txt}」`,'q')}
function dishName(d){const D=DISH(d);return D?(d==='signature'&&S.signature?S.signature.name:D.n):''}
/* Not every visit, and tied to the visit: the dish and how it came out, a cat that came by or got photographed,
   a long wait, two words with Jill. Newest first in the journal; capped so the save stays small. */
function regularNote(g){if(!R||!g.reg||g.reg==='dylan')return;const v=S.regulars[g.reg]||0;if(v<4||Math.random()>.32)return;S.notes=S.notes||[];if(S.notes.some(n=>n.reg===g.reg&&S.day-n.day<2))return;
 const items=g.ticket?g.ticket.items.filter(i=>i.st==='served'):[];const it=items.length?pick(items):null;const dn=it?dishName(it.d):'';const q=it?it.q:null;const cat=g.lookCat?catName(g.lookCat.def):null;const pool=[];
 if(dn&&(q==='P'||q==='G'))pool.push(`今天的${dn}還是很好吃。`,`${dn}，一如往常。`,`吃了${dn}，今天也算是過去了。`);
 if(dn&&q==='O')pool.push(`${dn}好像跟上次不太一樣，但還是吃完了。`);
 if(dn&&q==='B')pool.push(`今天的${dn}有點失常，下次再給它一次機會。`);
 if(g.photo&&cat)pool.push(`拍到${cat}了，手機裡又多一張。`,`${cat}今天很上相。`);else if(cat&&g.lookCat&&g.lookCat.def.id==='tora')pool.push(`窗邊那隻貓今天終於看我了。`);else if(cat)pool.push(`看了${cat}一會兒，忘了自己在等菜。`);
 if(g.catJoy)pool.push('貓來桌邊繞了一圈，心情好了一半。');if(g.scared)pool.push(`又被${catName(catBy('mikan').def)}嚇到一次。`);
 if(g.pat<.45)pool.push('今天等了比較久，還是值得。');if(g.chat)pool.push('跟 Jill 聊了兩句，回家的路都輕了。');
 if(!pool.length)pool.push('今天也來了。','老位子還在，就好。');
 S.notes.unshift({day:S.day,reg:g.reg,txt:pick(pool)});if(S.notes.length>40)S.notes.length=40}
function jillFarewell(g){if(!R||!g.reg||g.reg==='dylan'||g.chat||(R.chatT||0)>R.t)return;const v=S.regulars[g.reg]||0;const tier=Math.floor(regTier(v));if(!tier||Math.random()>(tier===2?.45:.3))return;
 const items=g.ticket?g.ticket.items.filter(i=>i.st==='served'):[];const it=items.length?pick(items):null;const dn=it?dishName(it.d):'';const good=it&&(it.q==='P'||it.q==='G');
 const gl=dn?(good?pick([`今天的${dn}還是很好吃。`,`${dn}，明天還想吃。`,`${dn}跟上次一樣好。`]):pick([`今天的${dn}，嗯，還可以。`,`${dn}下次再來試一次。`])):pick(['今天也謝謝妳。','明天見。']);
 const jl=tier===2?pick(['慢走，明天見。','路上小心。','下次來，貓會記得你的。']):pick(['謝謝，慢走。','明天見！','謝謝光臨，路上小心。']);
 g.chat=true;R.chatT=R.t+40;quote(g,gl);setTimeout(()=>{if(R&&phase==='service'&&!paused)jillSay(jl)},1400)}
function jillGreet(g,t){if(!R)return;const J=R.jill;if(g.reg==='dylan'){if(!J.cur&&!J.rest&&Math.random()<.7){J.lookAt={x:t.x,y:t.y,t:rand(1.2,2)};if(S.dylan.stage>=1)J.nod=.7}return}const free=!J.cur&&!J.q.length&&!J.rest&&!J.pet&&(J.calm||0)>.8;if(!free)return;
 const v=g.reg?(S.regulars[g.reg]||0):0;const tier=Math.floor(regTier(v));
 /* a look and a nod for everyone she has time for; a word for people she knows */
 if(Math.random()<(g.reg?.9:.45)){J.lookAt={x:t.x,y:t.y,t:rand(1,1.6)};J.nod=.7}
 if(g.reg&&tier>0&&!g.chat&&(R.chatT||0)<R.t&&Math.random()<(tier===2?.55:.4)){const L=REG_CHAT[g.reg];const pr=L&&L[tier-1]?pick(L[tier-1]):null;if(pr){g.chat=true;R.chatT=R.t+40;jillSay(pr[0]);setTimeout(()=>{if(R&&phase==='service'&&!paused&&R.groups.includes(g))quote(g,pr[1])},1500)}}}
function jillTargets(i){const J=R.jill;return J.q.includes(i)||(J.cur&&J.cur.t===i)}
function tableActionable(t){const g=t.group;if(!g)return t.dirty;if(g.rowdy)return true;if(g.state==='order'||g.state==='check')return true;if(g.state==='wait'&&g.ticket&&g.ticket.items.some(it=>it.st==='ready'))return true;return false}
function planAct(){const J=R.jill,t=R.tables[J.cur.t],g=t.group;const need=g&&g.ticket&&g.ticket.items.some(it=>it.st==='ready'&&!it.picked);
 if(need){J.cur.step='pickup';J.troom='main';J.tx=PASS.x+(t.x<200?-14:14);J.ty=PASS.y}else{J.cur.step='table';J.troom=t.room||'main';J.tx=t.x;J.ty=t.y+26}}
function arriveAct(){const J=R.jill;if(J.restTo){J.restTo=false;J.sit=true;J.face=1;return}
 if(J.visit&&J.visit.phase==='go'&&J.visit.kind==='selfie'){const V=J.visit;V.phase='stand';V.t=rand(2,3);const t=V.t0,g=V.g;J.face=t.x>=J.x?1:-1;J.lookAt={x:t.x,y:t.y-8,t:V.t};if(R.groups.includes(g)){jillSay(pick(['好啊。','來。','貓也要一起嗎？']));g.pat=Math.min(1,g.pat+.1);memo('selfie',t.x,t.y-6,{g:g.name,subj:[{x:J.x,y:J.y}]})}return}
 if(J.visit&&J.visit.phase==='go'&&J.visit.kind==='treat'){const V=J.visit;V.phase='stand';V.t=rand(1.4,2.2);const t=V.t0;J.face=t.x>=J.x?1:-1;J.lookAt={x:t.x,y:t.y-8,t:V.t};treatArrive(V);return}
 if(J.visit&&J.visit.phase==='go'){const V=J.visit;V.phase='stand';V.t=rand(2.2,3.6);const t=V.t0,g=V.g;J.face=t.x>=J.x?1:-1;J.lookAt={x:t.x,y:t.y-8,t:V.t};
  if(R.groups.includes(g)){memo('pause',t.x,t.y,{subj:[{x:J.x,y:J.y}]});const st=S.dylan.stage;const r=Math.random();
   if(r<.4&&!g.said){g.said=1;setTimeout(()=>{if(R&&phase==='service')dylanAct(g)},500)}
   else if(r<.75){const pr=st>=3?pick([['吃慢一點。','嗯。'],['今天很多人。','看得出來。'],['貓都在。','我知道。']]):pick([['還可以嗎？','很好吃。'],['今天人很多。','我不急。'],[null,'老闆娘，妳很忙。']]);setTimeout(()=>{if(!R||phase!=='service')return;if(pr[0])jillSay(pr[0]);setTimeout(()=>{if(R&&phase==='service'&&R.groups.includes(g))quote(g,pr[1])},pr[0]?1400:0)},400)}}
  return}
 if(J.rest==='go'){const L=LIFE.jill;if(!L.reserved||!L.pos){J.rest=null;return}J.visit=null;J.rest='sit';J.sofa=true;memo('rest',JPOS[L.pos].x,SOFA.jy,{subj:sofaCats(),rush:!!(R.fireCount&&R.t-(R.fireEnd||-99)<60)});L.x=JPOS[L.pos].x;L.y=SOFA.jy;L.on=true;L.reserved=false;L.act='idle';L.t=rand(4,9);L.last=null;L.sinceSit=0;L.legs=0;L.legTarget=0;L.gazeT=0;L.flip=0;L.settleT=rand(20,40);L.bobT=.5;J.face=L.face;J.x=L.x;J.y=SOFA.front+10;return}
 if(!J.cur)return;const t=R.tables[J.cur.t];
 if(J.cur.step==='pickup'){const g=t.group;if(g&&g.ticket){for(const it of g.ticket.items)if(it.st==='ready'&&!it.picked){it.picked=true;J.carry.push({tk:g.ticket,it})}}J.busy=.22;J.cur.step='table';J.cur.go=true;R.tv++;return}
 let busy=0;const g=t.group;/* what this trip is for is decided before anything changes: a checkout leaves the table dirty,
   and clearing it is the next trip (tap again, or a cleaner) — the same rule whoever takes the money */
 const clearing=!t.group&&t.dirty;
 if(g&&g.rowdy){g.rowdy=0;ach('rowdy');g.pat=Math.min(1,g.pat+.25);busy=1.1;quote(g,'好啦好啦…看在 Jill 的面子上。');addFloat(t.x,t.y-50,'安撫成功','#9ED08A',1,t.room);sfx.good()}
 if(g&&g.state==='order'&&g.usual&&!g.usualSaid){g.usualSaid=1;ach('usual');jillSay('老樣子？');setTimeout(()=>{if(R&&phase==='service'&&R.groups.includes(g))quote(g,pick(['老樣子。','嗯，老樣子。','妳記得。']))},1200);if(g.reg)regFact(g.reg,`常點${dishName(g.usual)}，Jill 記得。`)}
 if(g&&g.state==='order'){createTicket(g);busy=.7}
 if(g&&g.gift&&['order','wait','eat','check'].includes(g.state)&&J.cur.step==='table')regGift(g,t);
 if(g&&g.ticket&&J.carry.length){const mine=J.carry.filter(c=>c.tk===g.ticket);if(mine.length){serveItems(g,mine);J.carry=J.carry.filter(c=>c.tk!==g.ticket);busy=Math.max(busy,.4)}}
 if(g&&g.reg==='dylan'&&!g.said&&(J.cur.step==='table')&&(g.state==='check'||(g.ticket&&g.ticket.items.some(i=>i.st==='served')))&&Math.random()<.6){g.said=1;setTimeout(()=>{if(R&&phase==='service'&&R.groups.includes(g)){if(g.back&&Math.random()<.5)quote(g,'剛才太滿了，繞了一圈再回來。');else if(Math.random()<.55)dylanAct(g);else quote(g,dylanLine())}},600)}
 if(g&&g.state==='check'){if(g.gift)regGift(g,t);jillFarewell(g);regularNote(g);collect(g);busy=Math.max(busy,.5)}
 if(clearing&&!t.group&&t.dirty){t.dirty=false;t.plates=[];t.busT=0;busy=Math.max(busy,.55);sfx.clear();coach(7)}
 J.carry=J.carry.filter(c=>R.tickets.includes(c.tk));J.busy=busy||.08;J.cur.done=true}
/* What still needs Jill herself right now. Staff who cover a job take it off her plate, which is how
   hiring people turns into free time for her — no employee-count bonus anywhere. */
/* a waiter's duties: which of the five front-of-house jobs this person takes. Older saves carry m.duty ('both'|'seat'|'order');
   it is read once into the new form. Serving needs LV2, checkout LV3, whatever the setting. */
function waiterDuties(m){if(!m.duties){const d=m.duty||'both';m.duties={seat:d!=='order',order:d!=='seat',serve:d==='both',check:d==='both',clean:false}}return m.duties}
function waiterDoes(m,k){if(m.role!=='waiter')return false;const d=waiterDuties(m);if(!d[k])return false;if(k==='serve')return m.lv>=2;if(k==='check')return m.lv>=3;return true}
function dutyLabel(m){const d=waiterDuties(m);const on=[['seat','帶位'],['order','點餐'],['serve','上菜'],['check','結帳'],['clean','收桌']].filter(([k])=>d[k]).map(([,n])=>n);return on.length===5?'全部都做':on.length?on.join('＋'):'（沒有職責）'}
function crewCovers(kind){for(const m of S.crew||[]){if(kind==='clean'&&(m.role==='cleaner'||waiterDoes(m,'clean')))return true;if(m.role!=='waiter')continue;if(waiterDoes(m,kind))return true}return false}
function chefCanAny(d){const D=DISH(d);if(!D)return false;const m=chefFor(D.st);return !!m&&chefCan(m,d)}
function jillWorkload(){if(!R||R.closing!=null)return 9;const J=R.jill;let w=0;
 if(J.cur||J.q.length||J.carry.length)w+=3;
 for(const t of R.tables){const g=t.group;if(!g){if(t.dirty&&!crewCovers('clean'))w++;continue}if(g.rowdy)w+=3;if((g.state==='order'||g.state==='reading'||g.state==='toTable')&&!crewCovers('order'))w++;if(g.state==='check'&&!crewCovers('check'))w++;if(g.state==='wait'&&g.ticket&&g.ticket.items.some(i=>i.st==='ready'&&!i.picked)&&!crewCovers('serve'))w++}
 for(const tk of R.tickets)for(const it of tk.items)if(it.st==='pending'&&!chefCanAny(it.d))w++;
 for(const s0 of R.slots){if(s0.broken)w+=2;if(s0.job&&!chefHandles(s0))w++}
 if(R.thief||R.insp)w+=3;return w}
function startRest(pos){const J=R.jill,L=LIFE.jill;J.rest='go';J.restPos=pos;L.pos=pos;L.reserved=true;L.on=false;L.face=JPOS[pos].face;L.legs=0;L.legTarget=0;L.act=null;L.petCat=null;L.hat=true;J.troom='main';J.tx=JPOS[pos].x;J.ty=SOFA.front+10;J.idle=0}
function endRest(){const J=R.jill,L=LIFE.jill;if(!J.rest)return;const was=L.on;const x=L.x;J.rest=null;J.sofa=false;L.on=false;L.reserved=false;L.pos=null;L.act=null;L.petCat=null;L.hat=false;if(was){J.x=x;J.y=SOFA.front+12}J.tx=null;J.ty=null;J.moving=false;J.restCD=R.t+rand(25,45);J.idle=0;J.calm=0;
 for(const c of CATS||[])if(c.sofa&&c.sofa.kind==='lap'&&c.sofaOn)leaveSofa(c)}
function restTick(dt){const J=R.jill,L=LIFE.jill;L.sinceSit+=dt;L.t-=dt;if(L.gazeT>0)L.gazeT-=dt;if(L.flip>0)L.flip-=dt;if(L.bobT>0)L.bobT-=dt;
 if(L.act==='read'){L.flipT-=dt;if(L.flipT<=0){L.flipT=rand(5,13);L.flip=.35}}
 J.restChk=(J.restChk||0)+dt;if(J.restChk>.5){J.restChk=0;if(J.q.length||jillWorkload()>0){endRest();return}}
 if(L.t<=0){const lap=(CATS||[]).find(c=>c.sofa&&c.sofa.kind==='lap'&&c.sofaOn);const near=sofaCats().filter(c=>Math.abs(c.x-L.x)<46);
  const W=[['read',L.last==='read'?1.5:3],['idle',L.last==='idle'?1:2],['look',2]];if(near.length&&L.act!=='pet')W.push(['pet',lap?4:3]);
  const k=wpick(W,o=>o[1])[0];L.last=L.act;L.act=k;
  if(k==='read'){L.t=rand(10,25);L.flipT=rand(4,10)}else if(k==='idle')L.t=rand(5,12);
  else if(k==='look'){L.t=rand(2.5,4);const g=R.groups.find(q=>q.table!=null&&['reading','wait','eat'].includes(q.state));L.gazeT=L.t;L.gazeX=g?R.tables[g.table].x:(L.face>0?L.x+80:L.x-80)}
  else if(k==='pet'){L.petCat=pick(near);L.t=rand(2.5,4.5);L.petCat.hearts.push({x:0,y:-24,t:0});L.petCat.happy=Math.max(L.petCat.happy||0,1.5);L.petCat.quiet=1}}}
function jillUpd(dt){const J=R.jill;const fire=R.fire>0;
 J.calm=(J.calm||0)+dt;J.wlChk=(J.wlChk||0)+dt;if(J.wlChk>.5){J.wlChk=0;if(J.cur||J.q.length||jillWorkload()>0)J.calm=0}
 if(J.rest==='sit'){restTick(dt);if(J.rest==='sit')return}
 if(J.busy>0){J.busy-=dt*(fire?1.5:1);if(J.busy>0)return;J.busy=0;if(J.cur){if(J.cur.go){J.cur.go=false;const t=R.tables[J.cur.t];J.troom=t.room||'main';J.tx=t.x;J.ty=t.y+26}else if(J.cur.done)J.cur=null}}
 if(!J.cur&&J.q.length){J.cur={t:J.q.shift()};planAct();J.idle=0}
 if(J.tx!=null){const v=165*flowMul('jill')*(fire?1.5:1)*dt;if(stepTo(J,v)){J.tx=null;J.moving=false;arriveAct()}else{J.step+=dt*12;J.moving=true}return}
 if(J.room!=='main'){/* away from the dining room with nothing to do: back to the pass */J.troom='main';J.tx=PASS.x;J.ty=PASS.y;return}
 if(J.pet){J.pet.t-=dt;if(J.pet.t<=0){J.pet=null;J.idle=0}else if(J.q.length||jillWorkload()>2)J.pet=null}
 if(!J.cur&&!J.pet&&R.closing==null&&J.idle>1.5&&(J.petCD||0)<R.t&&CATS&&Math.random()<dt*.5){/* a cat wandered close: look down, crouch, one pat */const near=CATS.find(c=>!c.hidden&&c.perch<0&&!c.sofa&&['rest','daze','stare','sleep','side'].includes(c.st)&&Math.hypot(c.x-J.x,c.y-J.y)<42);
  if(near){const id=near.def.id;const p=id==='tora'?.9:id==='ban'?.85:id==='mikan'?.6:id==='mei'?.45:.35;J.petCD=R.t+rand(18,40);if(Math.random()<p){J.pet={cat:near,t:rand(1.6,3),crouch:near.st!=='side'};if(near.st!=='side')memo('pet',near.x,near.y-6,{a:catName(near.def),subj:[{x:J.x,y:J.y}]});J.face=near.x>=J.x?1:-1;if(near.st!=='sleep'){releaseSpots(near);near.st='pet';near.pose=near.st==='sleep'?near.pose:'rub';near.happy=rand(2,3.5);near.quiet=1;near.face=J.x>=near.x?1:-1}near.hearts.push({x:0,y:-26,t:0});if(id==='snow'&&near.st==='sleep')snowNudge(near)}else{J.lookAt={x:near.x,y:near.y,t:rand(1,2),down:true}}}}
 if(J.lookAt){J.lookAt.t-=dt;if(J.lookAt.t<=0)J.lookAt=null}if(J.nod>0)J.nod-=dt;
 if(J.visit){const V=J.visit;if(J.q.length||jillWorkload()>1||!R.groups.includes(V.g)||V.g.table==null){cancelVisit()}else if(V.phase==='stand'){V.t-=dt;J.lookAt={x:V.t0.x,y:V.t0.y-8,t:.3};if(V.t<=0){J.visit=null;J.idle=2.3}return}}
 if(!J.cur&&R.closing==null){J.idle+=dt;treatTick();if(J.visit)return;
  /* Dylan is here and she has a moment: she goes over and stands by his table for a bit. Not a job; once a visit. */
  if(!J.visit&&!J.rest&&!J.pet&&J.idle>1.2&&J.calm>2.5&&(J.visitCD||0)<R.t&&Math.random()<dt*.35&&jillWorkload()<=1){const g=R.groups.find(q=>q.reg==='dylan'&&q.table!=null&&['wait','eat'].includes(q.state)&&!q.paused);if(g){const t=R.tables[g.table];g.paused=true;J.visitCD=R.t+60;J.visit={g,t0:t,phase:'go'};J.troom=t.room||'main';J.tx=t.x+(t.x<200?30:-30);J.ty=t.y+20;S.dylan.clues.pause=(S.dylan.clues.pause||0)+1;return}}
  /* a quiet moment: nothing on the pass, nobody waiting on her -> she may sit down on the sofa for a bit */
  if(!J.rest&&!J.pet&&J.calm>5&&(J.restCD||0)<R.t&&R.t>10&&R.t<R.dur*.92&&Math.random()<dt*.3&&jillWorkload()===0){const pos=freeJillPos();if(pos){startRest(pos);return}J.restCD=R.t+15}
  if(J.idle>2.2&&Math.hypot(J.x-PASS.x,J.y-PASS.y)>3){J.troom='main';J.tx=PASS.x;J.ty=PASS.y}}}
function tapTable(t){const g=t.group;if(R.jill.visit&&!jillTargets(t.i))cancelVisit();if(g&&g.rowdy){if(!jillTargets(t.i)){R.jill.q.push(t.i);if(R.jill.rest)endRest();sfx.tap()}return}
 if(!g&&!t.dirty){const q=queued().filter(x=>x.state==='queue'||x.state==='arrive');const fit=q.find(x=>x.size<=t.seats);if(fit){seatGroup(fit,t);return}if(q.length)toast('這張桌子坐不下這組客人');return}
 if(g&&(g.state==='toTable'||g.state==='reading')){toast('客人還在看菜單');return}
 if(g&&g.state==='eat'){toast('客人正在享用中');return}
 if(g&&g.state==='wait'&&!tableActionable(t)){toast('料理還沒好，先去廚房做菜吧');return}
 if(jillTargets(t.i))return;R.jill.q.push(t.i);if(R.jill.rest)endRest();sfx.tap()}

/* ---- staff ---- */
function staffUpd(dt){crewUpd(dt);incUpd(dt);stockArrive()}

/* ---- main update ---- */
function update(dt){R.t+=dt;
 if(R.fire>0){R.fire-=dt;if(R.fire<=0){R.fire=0;toast('Rush Mode 結束，呼！')}}
 if(!R.closed&&R.t<R.dur*.96){const free=R.tables.some(t=>!t.group&&!t.dirty)&&queued().length===0;const quiet=R.groups.length===0&&!R.slots.some(x=>x.job);R.idleT=quiet?R.idleT+dt:0;const gap=R.t-R.lastSpawn;const maxGap=S.day<=2?9:S.day<=5?7:5.5;
  if(free&&(gap>maxGap||R.idleT>2)){R.idleT=0;if(R.si<R.sched.length)R.sched[R.si].t=R.t;else spawn(Object.assign({t:R.t},rollGuest()))}}
 while(R.si<R.sched.length&&R.sched[R.si].t<=R.t){spawn(R.sched[R.si]);R.si++}
 if(R.rush&&!R.rushShown&&R.t>=R.rushT0){R.rushShown=true;banner('RUSH HOUR','晚餐尖峰時段開始！','fire')}
 if(R.t>=R.dur&&!R.closed)closeShop('21:30 打烊，不再接新客人');
 for(const g of R.groups)updGroup(g,dt);R.groups=R.groups.filter(g=>!g.gone);
 kitchenUpd(dt);streetUpd(dt);
 for(const s of R.slots){if(s.job)updJob(s,dt);if(s.pop)s.pop.t+=dt;if(s.fx){s.fx.t+=dt;if(s.fx.t>1)s.fx=null}if(s.flash>0)s.flash=Math.max(0,s.flash-dt*1.5);if(s.shake>0)s.shake=Math.max(0,s.shake-dt*8);if(s.flipT>0)s.flipT=Math.max(0,s.flipT-dt)}
 staffUpd(dt);ambientTick(dt);if(R.panel){const sl=R.slots[R.focus];const k=sl&&sl.job&&sl.job.step;const done=!sl||!sl.job||!!chefHandles(sl);if(done||(k&&(k.t==='wait'||k.t==='work')&&!R.holdSlot)){R.panelT=(R.panelT||0)+dt;if(R.panelT>(done?.7:.9)){R.panel=false;R.panelT=0}}else R.panelT=0}jillUpd(dt);
 for(const f of R.floats)f.t+=dt;R.floats=R.floats.filter(f=>f.t<f.life);
 for(const p of R.parts){p.t+=dt;p.x+=p.vx*dt;p.y+=p.vy*dt;p.vy+=p.g*dt}R.parts=R.parts.filter(p=>p.t<p.life);
 for(const k in S.stock)if(S.stock[k]<0)S.stock[k]=0;
 if(AU.ctx){const n=R.slots.filter(s=>s.job&&s.type==='stove').length;AU.siz.gain.setTargetAtTime(Math.min(.14,n*.05)*(.7+Math.random()*.6),AU.ctx.currentTime,.05);const seated=R.groups.filter(g=>['reading','order','wait','eat','check'].includes(g.state)).length;AU.chat.gain.setTargetAtTime(Math.min(.09,seated*.018),AU.ctx.currentTime,.3);if(Math.random()<.1)AU.chatBp.frequency.setTargetAtTime(380+Math.random()*500,AU.ctx.currentTime,.08)}
 if(R.closed&&R.groups.length===0&&R.closing==null)startClosing();if(R.closing!=null){R.closing+=dt;if(R.closing>75&&!R.ended){finishClosing();return}}
 R.cpT=(R.cpT||0)+dt;if(R.cpT>20&&R.closing==null){R.cpT=0;checkpointSave('auto')}}
function startClosing(){R.closing=0;hideCombo();const J=R.jill;J.q=[];J.cur=null;J.carry=[];const wasResting=J.rest==='sit';const keep=wasResting?Object.assign({},LIFE.jill):null;if(J.rest&&!wasResting)endRest();lifePlan();
 if(wasResting){LIFE.plan='sofa';const L=LIFE.jill;Object.assign(L,{on:true,reserved:false,pos:keep.pos,x:keep.x,y:SOFA.jy,face:keep.face,legs:0,legTarget:0,act:'settle',t:rand(1,3),sinceSit:0,counted:false,hat:false});J.rest=null;J.sofa=true;J.tx=null;J.ty=null;J.moving=false;J.restTo=false}
 else if(LIFE.plan==='sofa'){J.tx=null;J.ty=null;J.restTo=false;J.moving=false;const L=LIFE.jill;L.x=J.x;L.y=J.y;L.face=J.face;/* first the pass gets wiped down; then the sofa */L.wrapT=rand(4,6.5);if(Math.hypot(J.x-PASS.x,J.y-PASS.y)>4){L.act='standing';jillWalk(L,PASS.x,PASS.y,'wrap')}else L.act='wrap'}
 else{const t=R.tables[0];J.troom='main';J.tx=t.x-25;J.ty=t.y+2;J.restTo=true}$('#closePill').hidden=false;if(CATS)for(const c of CATS){if(c.hidden||['jump','walk','race','dash','bed'].includes(c.st))continue;c.t=Math.min(c.t||0,c.def.id==='tora'?.4:c.def.id==='ban'?rand(1.5,3):rand(2,8))}}
function finishClosing(){if(!R||R.ended)return;R.ended=true;$('#closePill').hidden=true;endDay()}
/* Why the stars went where they went today, in the player's words. Each cause carries a sign and a weight so the
   summary can show the ones that mattered. Computed from what happened, not from the formula's decimals. */
function ratingStory(st,plated){const out=[];const add=(t,s,w)=>out.push({t,s,w});
 const q=st.q||{};const good=(q.P||0)+(q.G||0),bad=(q.O||0)+(q.B||0);if(plated>=4){if(good/plated>=.8)add(`料理品質高（Perfect ${q.P||0}・Good ${q.G||0}）`,1,good/plated);if(bad/plated>=.25)add(`料理失常 ${bad} 道（Okay／燒焦）`,-1,bad/plated*1.5)}
 const pats=st.pats||[];if(pats.length>=4){const p=pats.reduce((a,b)=>a+b,0)/pats.length;if(p<.5)add(`客人等太久（結帳時平均耐心 ${Math.round(p*100)}%）`,-1,(.6-p)*2.5);else if(p>=.78)add('上菜快，客人很少等',1,(p-.6)*1.5)}
 if(st.angry)add(`${st.angry} 組客人生氣離開（每組一顆星）`,-1,st.angry*.5);
 if(st.lost>=6)add(`${st.lost} 位客滿沒等到位子（有些留下兩顆星）`,-1,st.lost*.06);
 if((st.pricey||0)>=3)add(`${st.pricey} 組覺得價格偏高`,-1,st.pricey*.15);
 const short=Object.values(st.short||{}).reduce((a,b)=>a+b,0);if(short>=6)add(`缺貨臨時叫貨 ${short} 次，客人多等`,-1,short*.05);
 if(ambience()>=6)add(`店裡氛圍 +${ambience()}`,1,.3);if((st.catJoy||0)>=3)add(`貓陪了 ${st.catJoy} 桌客人`,1,st.catJoy*.08);if(st.treats)add(`請客 ${st.treats} 次`,1,.25);
 if(st.critic==='good')add('評論家給了好評（權重 ×3）',1,2);if(st.critic==='bad')add('評論家的評價不好（權重 ×3）',-1,2);
 return out.sort((a,b)=>b.w-a.w)}
/* the restaurant's records: fun, legible, with the day they were set */
const REC_N={revDay:'單日最高營業額',guestsDay:'單日最多客人',ratingMax:'最高評分',dishDay:'單日一道菜賣最多',tipsDay:'單日最多小費',perfectDay:'單日最多 Perfect',combo:'最長 COMBO',photosDay:'單日最多照片',calm:'連續沒有客人生氣離開',rain:'下雨天營業額最高',treats:'請客的次數',sig:'招牌菜賣出的份數',regs:'來過最多次的熟客'};
function updRecords(st,plated,D){S.records=S.records||{};const Rc=S.records;const set=(k,v,extra)=>{if(v==null)return;if(!Rc[k]||v>Rc[k].v)Rc[k]=Object.assign({v,d:D},extra||{})};
 set('revDay',st.rev);set('guestsDay',st.guests);set('ratingMax',Math.round(rating()*100)/100);let td=null,tn=0;for(const d in st.dish)if(st.dish[d]>tn){tn=st.dish[d];td=d}if(td)set('dishDay',tn,{dish:td});set('tipsDay',st.tips);set('perfectDay',st.perfect);set('combo',R.maxCombo);set('photosDay',albumList().filter(p=>p.day===D).length);
 Rc.calmRun=st.angry?0:(Rc.calmRun||0)+1;set('calm',Rc.calmRun);if(R.weather==='rain'||R.weather==='storm')set('rain',st.rev);
 Rc.treats={v:(Rc.treats?Rc.treats.v:0)+(st.treats||0),d:D};const sigBefore=sigLv();Rc.sig={v:(Rc.sig?Rc.sig.v:0)+(st.sig||0),d:D};if(S.signature&&sigLv()>sigBefore){S.sigEvoNews=sigLv();DCACHE.clear();ICACHE.clear();if(sigLv()>=2)ach('sig2');if(sigLv()>=3)ach('sig3')}
 let br=null,bn=0;for(const k in S.regulars)if(S.regulars[k]>bn){bn=S.regulars[k];br=k}if(br)Rc.regs={v:bn,d:D,who:br==='dylan'?'Dylan':(REG_BY[br]||{}).n||br};
 return Object.keys(Rc).filter(k=>Rc[k]&&Rc[k].d===D&&['revDay','guestsDay','ratingMax','dishDay','tipsDay','perfectDay','combo','photosDay'].includes(k)&&(D>3))}
function recordsHTML(){const Rc=S.records||{};const rows=Object.keys(REC_N).filter(k=>Rc[k]&&Rc[k].v).map(k=>{const r=Rc[k];const v=k==='revDay'||k==='tipsDay'||k==='rain'?fmt(r.v):k==='ratingMax'?r.v.toFixed(2):k==='dishDay'?`${dishName(r.dish)} × ${r.v}`:k==='regs'?`${r.who} · ${r.v} 次`:k==='calm'?`${r.v} 天`:k==='combo'?`×${r.v}`:String(r.v);return`<div class="rec"><span>${REC_N[k]}</span><b>${v}</b><small>DAY ${r.d}</small></div>`});
 return rows.length?`<div class="card recs">${rows.join('')}</div>`:'<p class="muted">開店幾天後，這裡會留下紀錄。</p>'}
function ratingHistHTML(){const H=(S.rhist||[]).slice(-14);if(!H.length)return'<p class="muted">還沒有紀錄。</p>';const W=300,Hh=70;const xs=i=>10+i*(W-20)/Math.max(1,H.length-1);const ys=r=>Hh-6-(clamp(r,2.5,5)-2.5)/2.5*(Hh-14);
 const path=H.map((h,i)=>(i?'L':'M')+xs(i).toFixed(1)+' '+ys(h.r).toFixed(1)).join(' ');const nl=LEVELS[S.level];
 return`<svg class="spark" viewBox="0 0 ${W} ${Hh}" preserveAspectRatio="none">${[3,4,5].map(v=>`<line x1="0" x2="${W}" y1="${ys(v)}" y2="${ys(v)}" stroke="rgba(46,32,25,.12)"/><text x="2" y="${ys(v)-2}" font-size="8" fill="#9A8574">${v}</text>`).join('')}${nl?`<line x1="0" x2="${W}" y1="${ys(nl.rating)}" y2="${ys(nl.rating)}" stroke="#C99A45" stroke-dasharray="3 3"/>`:''}<path d="${path}" fill="none" stroke="#5E8F4E" stroke-width="2"/>${H.map((h,i)=>`<circle cx="${xs(i)}" cy="${ys(h.r)}" r="2.6" fill="#5E8F4E"/>`).join('')}</svg>
  <div class="card rh">${H.slice().reverse().slice(0,8).map((h,i,arr)=>{const prev=H[H.indexOf(h)-1];const d=prev?h.r-prev.r:0;return`<div class="rrow"><span>DAY ${h.d}</span><b>${h.r.toFixed(2)}</b><em class="${d>0.004?'up':d<-0.004?'dn':''}">${d>0.004?'↑':d<-0.004?'↓':'→'}${prev&&Math.abs(d)>.004?Math.abs(d).toFixed(2):''}</em><small>${h.why&&h.why.length?h.why.join('・'):h.rs!=null?`今日評論平均 ${h.rs} 星`:'沒有新評論'}</small></div>`}).join('')}</div>`}
function achDay(st,plated){if(S.stats.days+1>=7)ach('week');if(st.rev>=20000)ach('rev20k');if(st.guests>=60)ach('guests60');const short=Object.values(st.short||{}).reduce((a,b)=>a+b,0);if(short===0&&st.guests>=30)ach('noshort');
 const Rc=S.records||{};if((Rc.calmRun||0)>=7)ach('calm7');const W=R.weather;if((W==='rain'||W==='storm')&&(st.dish.soup||0)>=6)ach('rain');if(W==='storm'&&st.guests>=15)ach('storm');if(W==='hot'&&WX_COLD.filter(d=>DISH(d).cat==='drink').reduce((a,d)=>a+(st.dish[d]||0),0)>=12)ach('hot');
 if(R.event==='celebrate')ach('celebrate');if(R.event==='datenight'&&(st.couples||0)>=5)ach('datenight');const pats=st.pats||[];if(st.guests>=20&&pats.length>=8&&pats.every(p=>p>=.5))ach('night0');
 if(rating()>=4.5&&S.reviews.length>=20)ach('rating45');if(Rc.sig&&Rc.sig.v>=100)ach('sig100');const crew=S.crew||[];if(crew.length>=6)ach('staff6');if(crew.length>=3&&crew.every(m=>m.lv>=5))ach('lv5all');if(opsLv('flow')>=3)ach('ops3');if(albumList().length>=50)ach('photos50')}
function endDay(){if(!R)return;clearCheckpoint();const st=R.st,D=S.day;const wages=crewWages();let bonus=0;
 const tasks=S.today.tasks.map(t=>{const p=taskProg(t);const done=p>=t.n;if(done)bonus+=t.reward;return{...t,p,done}});
 S.money+=bonus-wages;const avg=st.sats.length?st.sats.reduce((a,b)=>a+b,0)/st.sats.length:0;
 let top=null,topN=0;for(const d in st.dish)if(st.dish[d]>topN){topN=st.dish[d];top=d}
 const dayStars=st.sats.length?clamp(Math.round((avg/100)*5*2)/2,1,5):1;
 let nb=1,msg='';if(st.critic==='good'){nb+=.35;msg="Jill's Kitchen 昨晚突然爆紅！評論家的文章被瘋狂轉發。"}else if(st.critic==='bad'){nb-=.1;msg='評論家的文章不太留情面，今天客人少了一點。'}if(st.blogger==='good'){nb+=.25;msg=msg||'美食部落客的貼文爆了，大家都想來 Jill 的店！'}
 S.buzz=nb;S.buzzMsg=msg;S.stats.days++;S.stats.guests+=st.guests;S.stats.perfect+=st.perfect;S.stats.walkins=(S.stats.walkins||0)+(st.walkins||0);if(S.stats.walkins>=20)ach('walkin');S.stats.families=(S.stats.families||0)+(st.families||0);if(S.stats.families>=10)ach('families');
 const plated=st.q.P+st.q.G+st.q.O+st.q.B;
 if(st.guests>=10)ach('rush');if(plated>=8&&st.q.B===0&&st.q.O===0&&st.angry===0)ach('perfectnight');if(rating()>=4.75&&S.reviews.length>=20)ach('chef');
 const r0=(S.rhist&&S.rhist.length)?S.rhist[S.rhist.length-1].r:3;const story=ratingStory(st,plated);S.rhist=S.rhist||[];S.rhist.push({d:D,r:Math.round(rating()*100)/100,n:st.reviews.length,rs:st.reviews.length?Math.round(st.reviews.reduce((a,r)=>a+r.s,0)/st.reviews.length*10)/10:null,why:story.slice(0,2).map(x=>x.t)});if(S.rhist.length>60)S.rhist.shift();
 const recs=updRecords(st,plated,D);achDay(st,plated);
 S.lastSummary={day:D,rev:st.rev,cost:S.todayCost,wages,tips:st.tips,bonus,net:st.rev+st.tips+bonus-S.todayCost-wages,guests:st.guests,lost:st.lost,walkins:st.walkins||0,families:st.families||0,angry:st.angry,perfect:st.perfect,plated,avg:Math.round(avg),top,stars:dayStars,reviews:st.reviews.slice(-3),tasks,maxCombo:R.maxCombo,reco:recoDish(),recoN:recoDish()?(st.dish[recoDish()]||0):0,photos:albumList().filter(p=>p.day===D).length,r0,r1:Math.round(rating()*100)/100,story,recs,weather:R.weather,event:R.event,treats:st.treats||0,sets:st.sets||0,crew:(S.crew||[]).map(m=>({name:m.name,role:m.role,lv:m.lv,wage:crewWage(m),n:(st.crew||{})[m.id]||{}})),short:Object.values(st.short||{}).reduce((a,b)=>a+b,0),
  sales:menuList().map(d=>({d,n:st.dish[d]||0,rev:(st.dish[d]||0)*priceOf(d),short:(st.short||{})[d]||0,left:S.stock[d]||0})).sort((a,b)=>b.n-a.n)};
 S.dayLog=(R.log||[]).slice(-90);S.dayLogDay=D;S.salesHist=S.salesHist||{};for(const d of menuList()){const v=(st.dish[d]||0)+((st.short||{})[d]||0);const h=S.salesHist[d];S.salesHist[d]=h==null?v:Math.round((h*.5+v*.5)*10)/10}S.phase='shop';S.tut=1;save();
 for(const k of[...ICACHE.keys()])if(k.startsWith('pg'))ICACHE.delete(k);
 R=null;phase='summary';paused=false;if(AU.ctx){AU.siz.gain.setTargetAtTime(0,AU.ctx.currentTime,.1);AU.chat.gain.setTargetAtTime(0,AU.ctx.currentTime,.3)}
 IDLE=null;hideCombo();$('#fire').hidden=true;hideCoach();renderTickets();renderTasks();layoutAll();showSummary()}

/* ================= effects ================= */
function addFloat(x,y,txt,col,big,rm){if(!R)return;R.floats.push({x,y,txt,col,big,t:0,life:1.4,room:rm||'main'})}
function burst(where,s,col){if(!R)return;if(where==='tray'){s.burst={t:0,col};return}const n=where==='coins'?10:14;for(let i=0;i<n;i++){const a=rand(-Math.PI,0),v=rand(40,110);R.parts.push({x:s.x,y:s.y,vx:Math.cos(a)*v,vy:Math.sin(a)*v,g:where==='coins'?260:120,t:0,life:rand(.6,1),col,kind:where==='coins'?'coin':'spark',room:s.room||'main'})}}
function trayFloat(s,txt,col){s.fx={txt,col,t:0}}
function showCombo(){const el=$('#combo');el.hidden=false;el.textContent='COMBO ×'+R.combo;el.classList.remove('bump');void el.offsetWidth;el.classList.add('bump')}
function hideCombo(){$('#combo').hidden=true}
function banner(title,subt,kind){const b=$('#banner');const d=document.createElement('div');d.className='bn '+(kind||'');d.innerHTML=`<b>${title}</b>${subt?`<span>${subt}</span>`:''}`;b.innerHTML='';b.appendChild(d);setTimeout(()=>{if(d.parentNode)d.remove()},1700)}
function toast(html,kind){const box=$('#toasts');const lastT=box.lastElementChild;if(lastT&&lastT.innerHTML===html&&lastT.style.opacity!=='0')return;const d=document.createElement('div');d.className='toast '+(kind||'');d.innerHTML=html;box.appendChild(d);while(box.children.length>2)box.firstChild.remove();setTimeout(()=>{d.style.transition='opacity .4s';d.style.opacity='0';setTimeout(()=>d.remove(),400)},kind==='q'?3600:2800)}
function ach(id){if(S.achievements[id])return;S.achievements[id]=S.day;const a=ACH.find(x=>x.id===id);if(a){setTimeout(()=>banner(a.n,'成就解鎖'),600);sfx.buy()}}
function coach(k){if(!R||R.coach<0)return;if(k===R.coach){showCoach(COACH[k]);R.coach++;if(R.coach>=COACH.length){R.coach=-1;setTimeout(hideCoach,4500)}}}
function showCoach(txt){const c=$('#coach');c.hidden=false;c.innerHTML=`<img alt="" src="${portraitURL([JILL_LOOK],'jill',true)}"><div>${txt}</div>`}
function hideCoach(){$('#coach').hidden=true}

/* ================= HUD & tickets ================= */
let hudCache={};
function clockStr(){if(!R)return phase==='service'?'17:00':'打烊';const m=Math.floor(17*60+Math.min(R.t/R.dur,1.35)*270);const h=Math.floor(m/60),mm=m%60;return`${h}:${String(mm).padStart(2,'0')}`}
function hud(force){const vals={d:S.day,c:R?clockStr():(phase==='prep'?'開店前':phase==='title'?'17:00':'打烊後'),r:rating().toFixed(1),m:fmt(S.money)};
 if(force||vals.d!==hudCache.d)$('#hDay').textContent=vals.d;if(force||vals.c!==hudCache.c)$('#hClock').textContent=vals.c;if(force||vals.r!==hudCache.r)$('#hRate').textContent=vals.r;if(force||vals.m!==hudCache.m)$('#hMoney').textContent=vals.m;hudCache=vals;
 if(R&&R.fire>0){$('#fire').hidden=false;$('#fireBar').style.width=(R.fire/15*100)+'%'}else $('#fire').hidden=true}
let tkVer=-1,tkRefs=[];
/* The order strip on a phone: when the tickets do not fit, the strip scrolls (drag anywhere on it, or tap the
   edge button), tickets drop the guest name and shrink a little, and the edge button says how many are hidden.
   Every order stays reachable; nothing is clipped away silently. */
function ticketsLayout(){const el=ticketsEl;const more=$('#tkMore'),back=$('#tkBack');if(!more)return;const over=el.scrollWidth>el.clientWidth+2;
 el.classList.toggle('scroll',over);el.classList.toggle('compact',over&&R&&R.tickets.length>=4);
 if(!over){more.hidden=true;back.hidden=true;return}
 const right=el.scrollLeft+el.clientWidth;let hidden=0;for(const t of el.querySelectorAll('.tk')){if(t.offsetLeft+t.offsetWidth>right+4)hidden++}
 more.hidden=hidden===0;more.innerHTML=`›<small>+${hidden}</small>`;back.hidden=el.scrollLeft<24}
function renderTickets(){if(!R){ticketsEl.innerHTML=`<div class="tk-empty">${phase==='service'?'':'訂單會出現在這裡。'}</div>`;tkVer=-1;tkRefs=[];ticketsEl.classList.remove('scroll','compact');const m=$('#tkMore');if(m){m.hidden=true;$('#tkBack').hidden=true}return}
 if(R.tv===tkVer)return;tkVer=R.tv;
 if(!R.tickets.length){ticketsEl.innerHTML='<div class="tk-empty">還沒有訂單。點有「!」的桌子幫客人點餐。</div>';tkRefs=[];ticketsLayout();return}
 ticketsEl.innerHTML=R.tickets.map(tk=>{const g=tk.g;return`<div class="tk ${g.reg?(g.reg==='dylan'?'isdylan':'isreg'):g.type==='vip'?'isvip':''}" data-tk="${tk.id}"><div class="tk-h"><b>T${tk.no}</b><em data-w>0:00</em></div><div class="tk-who"><img alt="" src="${guestPortrait(g)}"><span>${g.reg==='dylan'?'Dylan':g.name}</span></div><div class="tk-items">${tk.items.map((it,i)=>`<button class="it ${it.st}" data-tk="${tk.id}" data-i="${i}" aria-label="${DISH(it.d).n}"><img alt="" src="${dishURL(it.d,it.st==='ready'||it.st==='served'?it.q:'G',it.want)}">${it.d==='steak'?`<span class="tag">${STEAK_S[it.want]}</span>`:''}${it.st==='ready'?'<span class="ok">✓</span>':''}${it.st==='order'?'<span class="dl">叫貨中</span>':''}</button>`).join('')}</div><div class="tk-pat"><i data-p></i></div></div>`}).join('');ticketsLayout();
 tkRefs=[...ticketsEl.querySelectorAll('.tk')].map(el=>({el,tk:R.tickets.find(t=>t.id===+el.dataset.tk),w:el.querySelector('[data-w]'),p:el.querySelector('[data-p]')}));updTicketBars()}
function updTicketBars(){if(!R)return;for(const r of tkRefs){if(!r.tk)continue;const e=Math.floor(R.t-r.tk.t0);r.w.textContent=`${Math.floor(e/60)}:${String(e%60).padStart(2,'0')}`;const p=r.tk.g.pat;r.p.style.width=(p*100)+'%';r.p.style.background=p>.55?'#5E8F4E':p>.28?'#E0A43A':'#D4553A';r.el.classList.toggle('urgent',p<.28)}}
/* a long press on a game control (hold-and-release cooking, buttons, the room) must never become a text
   selection, a magnifier or a context menu on iOS; the backup text box keeps its normal behaviour */
const noSelect=e=>{const t=e.target;if(!t||!t.closest)return;if(t.closest('textarea,input'))return;e.preventDefault()};
document.addEventListener('contextmenu',noSelect);document.addEventListener('selectstart',noSelect);
ticketsEl.addEventListener('scroll',()=>ticketsLayout(),{passive:true});
{const rc=$('#regcard');if(rc)rc.addEventListener('click',()=>{rc.hidden=true});const lb=$('#lightbox');if(lb){lb.addEventListener('click',e=>{const b=e.target.closest('[data-lb]');if(!b)return;const a=b.dataset.lb;if(a==='close')closeLightbox();else if(a==='prev')lightboxStep(-1);else if(a==='next')lightboxStep(1);else if(a==='keep'){const p=albumList().find(x=>x.id===lightbox.ids[lightbox.i]);if(p){p.keep=!p.keep;if(albumList().filter(x=>x.keep&&!MEMS_FIRST(x)).length>=10)ach('keep10');save();lightboxRender();if(sub==='book')keepScroll(showBook)}}});
 let sx=null,sy=null;lb.addEventListener('touchstart',e=>{const t=e.touches[0];sx=t.clientX;sy=t.clientY},{passive:true});lb.addEventListener('touchend',e=>{if(sx==null)return;const t=e.changedTouches[0];const dx=t.clientX-sx,dy=t.clientY-sy;sx=null;if(Math.abs(dx)>50&&Math.abs(dx)>Math.abs(dy)*1.5)lightboxStep(dx<0?1:-1)},{passive:true});
 document.addEventListener('keydown',e=>{if(!lightbox)return;if(e.key==='Escape')closeLightbox();else if(e.key==='ArrowLeft')lightboxStep(-1);else if(e.key==='ArrowRight')lightboxStep(1)})}}
$('#tkMore').addEventListener('click',()=>{ticketsEl.scrollBy({left:ticketsEl.clientWidth*.8,behavior:'smooth'});setTimeout(ticketsLayout,400)});
$('#tkBack').addEventListener('click',()=>{ticketsEl.scrollBy({left:-ticketsEl.clientWidth*.8,behavior:'smooth'});setTimeout(ticketsLayout,400)});
ticketsEl.addEventListener('click',e=>{const b=e.target.closest('.it');if(!b||!R)return;const tk=R.tickets.find(t=>t.id===+b.dataset.tk);if(!tk)return;const it=tk.items[+b.dataset.i];if(!it)return;
 if(it.st==='pending')startCook(tk,it);else if(it.st==='ready'){const t=R.tables[tk.g.table];if(t)tapTable(t)}else if(it.st==='order'){toast(`食材運送中，還要 ${Math.max(1,Math.ceil(it.ordT-R.t))} 秒`)}else if(it.st==='cooking'){const i=R.slots.findIndex(x=>x.job&&x.job.it===it);if(i>=0){R.focus=i;R.panel=true;R.panelT=0}}});
function renderTasks(){const chip=$('#taskChip');if(!S.today||phase!=='service'){chip.hidden=true;$('#taskPanel').hidden=true;const lp=$('#logPanel');if(lp)lp.hidden=true;const sp=$('#stockPanel');if(sp)sp.hidden=true;logChip();stockChip();const rt=$('#roomTabs');if(rt)rt.hidden=true;return}chip.hidden=false;const ts=S.today.tasks;$('#taskDots').innerHTML=ts.map(t=>`<i class="${taskProg(t)>=t.n?'on':''}"></i>`).join('');
 if(!$('#taskPanel').hidden)$('#taskPanel').innerHTML=`<h4>今日任務</h4>`+ts.map(t=>{const p=Math.min(t.n,taskProg(t));const done=p>=t.n;return`<div class="task ${done?'done':''}"><span>${t.txt}</span><small>+${fmt(t.reward)}</small><div class="bar"><i style="width:${t.k==='noangry'?(R&&R.st.angry?0:100):p/t.n*100}%"></i></div><small>${t.k==='noangry'?(R&&R.st.angry?'失敗':'維持中'):t.k==='revenue'?fmt(p)+' / '+fmt(t.n):p+' / '+t.n}</small></div>`}).join('')}
$('#taskChip').addEventListener('click',()=>{const p=$('#taskPanel');p.hidden=!p.hidden;$('#logPanel').hidden=true;const sp=$('#stockPanel');if(sp)sp.hidden=true;renderTasks()});
function logHTML(list,n){const L=list.slice(-(n||14)).reverse();if(!L.length)return'<p class="muted" style="margin:4px 0">還沒有人說話。</p>';return L.map(e=>`<div class="ll ${e.k}"><small>${e.c}</small>${e.w?`<b>${e.w}</b>`:''}<span>${e.k==='e'?e.t:'「'+e.t+'」'}</span></div>`).join('')}
/* ---- 庫存: what is in the fridge right now, by dish, and emergency orders at 1.5× with real buttons ---- */
let stockArm=null;
function stockLevel(d){const n=S.stock[d]||0;return n<=0?'out':n<=2?'low':'ok'}
function emergencyCost(d){return Math.round(costOf(d)*1.5)}
function buyEmergency(d,n){const cst=emergencyCost(d);let k=0;while(k<n&&S.money>=cst&&stockTotal()<fridgeCap()){S.money-=cst;S.todayCost+=cst;S.stock[d]=(S.stock[d]||0)+1;k++}
 if(k){R.st.bought=(R.st.bought||0)+k;R.tv++;sfx.buy();toast(`緊急叫貨：${dishName(d)} ×${k}　-${fmt(cst*k)}`);hud()}else toast(S.money<cst?'錢不夠':'冰箱滿了，放不下');return k}
function stockChip(){const ch=$('#stockChip');if(!ch)return;const show=phase==='service'&&!!R;ch.hidden=!show;if(!show)return;const ms=menuList().filter(stationOk);const out=ms.filter(d=>stockLevel(d)==='out').length,low=ms.filter(d=>stockLevel(d)==='low').length;
 ch.classList.toggle('out',out>0);ch.classList.toggle('low',!out&&low>0);$('#stockN').textContent=out?`缺 ${out}`:low?`低 ${low}`:`${stockTotal()}/${fridgeCap()}`}
function openStock(on){const p=$('#stockPanel');if(!p)return;p.hidden=on===false?true:on===true?false:!p.hidden;if(!p.hidden){$('#logPanel').hidden=true;$('#taskPanel').hidden=true;renderStock()}}
function renderStock(){const p=$('#stockPanel');if(!p||p.hidden||!R)return;const ms=menuList().filter(stationOk).slice().sort((a,b)=>(S.stock[a]||0)-(S.stock[b]||0));const tot=stockTotal(),cap=fridgeCap();
 const lowAll=ms.filter(d=>(S.stock[d]||0)<=2);const fillCost=lowAll.reduce((a,d)=>a+emergencyCost(d)*Math.max(0,3-(S.stock[d]||0)),0);
 p.innerHTML=`<div class="sp-h"><h4>冰箱 <span>${tot}/${cap}</span></h4><button class="sp-x" data-stock="close" aria-label="關閉">✕</button></div>
  ${lowAll.length&&fillCost>0?`<button class="btn sm sp-fill" data-stock="fill">${stockArm==='fill'?`確定？低於 3 份的全部補到 3　${fmt(fillCost)}`:`低於 3 份的全部補到 3　${fmt(fillCost)}`}</button>`:''}
  <div class="sp-list">${ms.map(d=>{const n=S.stock[d]||0;const lv=stockLevel(d);const c=emergencyCost(d);const c3=c*3;const arm=stockArm===d+'|3';return`<div class="sp-row ${lv}"><img alt="" src="${dishURL(d,'P')}"><div class="nm">${dishName(d)}<small>${lv==='out'?'賣完了':lv==='low'?'快沒了':'還夠'}・叫貨 ${fmt(c)}/份</small></div><b class="n">${n}</b><button data-stock="buy" data-d="${d}" data-n="1" ${S.money<c||tot>=cap?'disabled':''}>+1 <small>${fmt(c)}</small></button><button data-stock="buy" data-d="${d}" data-n="3" class="${arm?'arm':''}" ${S.money<c||tot>=cap?'disabled':''}>${arm?'確定？':'+3'} <small>${fmt(c3)}</small></button></div>`}).join('')}</div>
  <p class="sp-note">臨時叫貨是平常進貨的 1.5 倍價，5 秒後到貨。餐點缺料時 Jill 也會自動叫貨。</p>`}
{const sp=$('#stockPanel');if(sp){sp.addEventListener('click',e=>{const b=e.target.closest('[data-stock]');if(!b||b.disabled)return;const a=b.dataset.stock;audioInit();
  if(a==='close'){sp.hidden=true;return}
  if(a==='fill'){if(stockArm!=='fill'){stockArm='fill';renderStock();setTimeout(()=>{if(stockArm==='fill'){stockArm=null;renderStock()}},4000);return}stockArm=null;for(const d of menuList().filter(stationOk))if((S.stock[d]||0)<=2)buyEmergency(d,3-(S.stock[d]||0));renderStock();stockChip();return}
  if(a==='buy'){const d=b.dataset.d,n=+b.dataset.n;const cost=emergencyCost(d)*n;if(cost>=600&&stockArm!==d+'|'+n){stockArm=d+'|'+n;renderStock();setTimeout(()=>{if(stockArm===d+'|'+n){stockArm=null;renderStock()}},4000);return}stockArm=null;buyEmergency(d,n);renderStock();stockChip()}});
 $('#stockChip').addEventListener('click',()=>openStock())}}
/* ---- room navigation: tabs with badges (what needs you where), swipe on the scene, keys 1–4 on a keyboard ---- */
const ROOM_ORDER=['front','main','side','kitchen'];
function roomsOpen(){return ROOM_ORDER.filter(roomOpen)}
function setRoom(k){if(!roomOpen(k)||k===room)return;room=k;forceDraw=true;sfx.tap();renderRoomTabs(true)}
function roomAlerts(){const A={};for(const k of ROOM_ORDER)A[k]={n:0,u:0};if(!R||phase!=='service')return A;
 for(const t of R.tables){const k=t.room||'main';const g=t.group;if(!g){if(t.dirty)A[k].n++;continue}if(g.rowdy){A[k].n++;A[k].u++;continue}if(g.state==='order'||g.state==='check'||(g.state==='wait'&&g.ticket&&g.ticket.items.some(i=>i.st==='ready'&&!i.picked))){A[k].n++;if(g.pat<.3)A[k].u++}}
 for(const s0 of R.slots){if(s0.broken){A.kitchen.n++;A.kitchen.u++;continue}const j=s0.job;if(j&&!chefHandles(s0)){const u=urgency(j);if(u>=2){A.kitchen.n++;if(u>=3)A.kitchen.u++}}}
 for(const tk of R.tickets)for(const it of tk.items)if(it.st==='pending'&&!chefCanAny(it.d)){A.kitchen.n++;break}
 const q=queued().length;if(q){A.main.n+=q}return A}
let tabsHTML='';
function roomIsNew(k){const nr=S.newRooms||{};const d=k==='side'?nr.side:k==='kitchen'?Math.max(nr.kext||0,nr.cooler||0,nr.pass||0):k==='front'?Math.max(nr.terrace||0,...EXTERIOR.map(e=>S.ext&&S.ext[e.k]?0:0)):0;return!!d&&S.day-d<=1}
function renderRoomTabs(force){const el=$('#roomTabs');if(!el)return;const show=phase==='service'&&!!R;el.hidden=!show;if(!show)return;const A=roomAlerts();
 const h=roomsOpen().map(k=>`<button data-room="${k}" class="${k===room?'on':''}${A[k].u?' urgent':''}${roomIsNew(k)&&k!==room?' new':''}"><span>${ROOMS[k].n}</span>${A[k].n?`<b>${A[k].n}</b>`:roomIsNew(k)&&k!==room?'<b class="nw">NEW</b>':''}</button>`).join('');
 if(force||h!==tabsHTML){tabsHTML=h;el.innerHTML=h}}
{const rt=$('#roomTabs');if(rt)rt.addEventListener('click',e=>{const b=e.target.closest('[data-room]');if(b)setRoom(b.dataset.room)})}
document.addEventListener('keydown',e=>{if(phase!=='service'||!R||sub)return;const i=['1','2','3','4'].indexOf(e.key);if(i>=0){const list=roomsOpen();if(list[i])setRoom(list[i])}else if(e.key==='ArrowLeft'||e.key==='ArrowRight'){const list=roomsOpen();const i2=list.indexOf(room)+(e.key==='ArrowRight'?1:-1);if(list[i2])setRoom(list[i2])}});
let SW=null;
function swipeEnd(e){if(!SW||!R)return;const dx=e.clientX-SW.x,dy=e.clientY-SW.y,dt=performance.now()-SW.t;const hit=SW.hit,idle=SW.idle;SW=null;const swiped=!R.holdSlot&&dt<=700&&Math.abs(dx)>=70&&Math.abs(dy)<=Math.abs(dx)*.6;if(idle!=null&&!swiped&&Math.hypot(dx,dy)<12){if(!paused&&room==='kitchen')tapStation(idle);return}if(hit||!swiped)return;const list=roomsOpen();const i=list.indexOf(room)+(dx<0?1:-1);if(list[i])setRoom(list[i])}
window.addEventListener('pointerup',swipeEnd);
function renderLog(){const p=$('#logPanel');if(!p||p.hidden)return;p.innerHTML=`<h4>今天大家說了什麼</h4>${logHTML(dayLog(),14)}`}
{const ch=$('#logChip');if(ch){ch.addEventListener('click',()=>{const p=$('#logPanel');p.hidden=!p.hidden;logNew=0;logChip();renderLog();$('#taskPanel').hidden=true;const sp=$('#stockPanel');if(sp)sp.hidden=true});$('#logPanel').addEventListener('click',()=>{$('#logPanel').hidden=true})}}
$('#taskPanel').addEventListener('click',()=>{$('#taskPanel').hidden=true});

/* ================= layout ================= */
function layoutAll(){DPR=Math.min(2,window.devicePixelRatio||1);const r=sc.getBoundingClientRect();if(!R&&r.width>0){const s0=r.width/336;const nd=clamp(Math.floor(r.height/s0-424-96),0,240);if(Math.abs(nd-DY)>2)applyDY(nd)}if(!IDLE)IDLE=makeIdle();sc.width=Math.round(r.width*DPR);sc.height=Math.round(r.height*DPR);SV.w=r.width;SV.h=r.height;SV.s=Math.min(r.width/336,r.height/LH);SV.ox=r.width/2-206*SV.s;SV.oy=Math.max(0,r.height-LH*SV.s);
 const W=Math.max(200,r.width-12);const kTop=SV.oy+FB*SV.s;{const pb=Math.max(18,r.height-kTop+10)+'px';$('#closePill').style.bottom=pb;$('#peekPill').style.bottom=pb}const WS=Math.round(clamp(r.height*.3,160,196));TL={n:0,chipW:0,CH:0,WS,pad:0,gap:0,x0:0,W};tc.style.height=WS+'px';tc.width=Math.round(W*DPR);tc.height=Math.round(WS*DPR);$('#trayWrap').style.top=Math.max(4,SV.oy+134*SV.s-WS)+'px';const tb=Math.max(8,r.height-kTop+8)+'px';$('#toasts').style.bottom=tb;$('#coach').style.bottom=tb;bg=null;forceDraw=true;if(typeof ticketsLayout==='function')ticketsLayout()}
function makeIdle(){const t=buildTables();const ev=['summary','shop'].includes(phase);if(ev)lifeEnsureEvening();const L=LIFE.jill;
 const jill=ev&&LIFE.plan==='sofa'?{x:L.x,y:L.y,sit:L.on,sofa:L.on?L.pos:null,carry:[],q:[],cur:null,face:L.face,step:0}:(ev&&t[0])?{x:t[0].x-25,y:t[0].y+2,sit:true,carry:[],q:[],cur:null,face:1,step:0}:{x:PASS.x,y:PASS.y,carry:[],q:[],cur:null,face:1,step:0};
 return{tables:t,slots:buildSlots(),groups:[],tickets:[],jill,floats:[],parts:[],fire:0}}
window.addEventListener('resize',()=>{layoutAll()});

/* ================= scene render ================= */
/* Soft contact shadow: a wide faint ellipse under a tighter darker one. Everything that stands on the floor uses it. */
function softShadow(c,x,y,rx,ry,a){a=a||.22;c.fillStyle=`rgba(40,25,15,${a*.45})`;el(c,x,y+ry*.15,rx*1.25,ry*1.35);c.fillStyle=`rgba(40,25,15,${a})`;el(c,x,y,rx,ry)}
/* The room's light through the day: clear at opening, warm in the late afternoon, dim and cool by closing */
function tintFor(d){d=clamp(d,0,1);return d<.5?mix('#FFF8EE','#FFE6C4',d/.5):mix('#FFE6C4','#C2B4C0',(d-.5)/.5)}
/* the weather colours the room a little: cooler and dimmer when it rains, warmer on a hot day */
function wxTint(col){const W=wxNow();if(W==='rain')return mix(col,'#C9D3DE',.2);if(W==='storm')return mix(col,'#AEB8C6',.32);if(W==='hot')return mix(col,'#FFD9A8',.16);if(W==='cool')return mix(col,'#E4F0EE',.1);return col}
function duskF(){if(R)return clamp(R.t/R.dur,0,1.2);return phase==='title'?.55:phase==='prep'?.25:.95}
const BGM=80;
/* Mobile browsers (iOS in particular) may throw away an offscreen canvas's pixels when the page sits
   in the background or memory is short. The cached floor/wall would then draw as nothing and the room
   would look dark from that moment on — through the next day as well, because the cache key never
   changes. So: probe a floor pixel of the cache every couple of seconds and after any return to the
   foreground, and rebuild it when it has gone blank. */
let bgProbeT=0;
function bgCheck(now){if(!bg)return;if(now-bgProbeT<2)return;bgProbeT=now;try{const s=SV.s*DPR;const px=Math.floor((BGM+200)*s),py=Math.floor(250*s);const d=bg.getContext('2d').getImageData(px,py,1,1).data;if(d[3]<200)bg=null}catch(e){}}
function makeBg(){const s=SV.s*DPR;const XW=LW+BGM*2,X0=-BGM;const cv=mkCanvas(Math.ceil(XW*s),Math.ceil(LH*s));const c=cv.getContext('2d');c.scale(s,s);c.translate(BGM,0);const L=S.level,rnd=rng(77);
 c.save();c.beginPath();c.rect(X0,90,XW,LH-90);c.clip();c.fillStyle=TH().floor;c.fillRect(X0,90,XW,LH);
 for(let i=0;i<40;i++){c.fillStyle=`rgba(${rnd()<.5?'255,255,255':'170,150,125'},.06)`;el(c,X0+rnd()*XW,95+rnd()*(LH-95),20+rnd()*50,6+rnd()*16)}
 for(let i=0;i<7000;i++){c.fillStyle=rnd()<.55?'rgba(255,255,255,.45)':'rgba(140,120,95,.14)';c.fillRect(X0+rnd()*XW,90+rnd()*(LH-90),.9,.9)}
 c.strokeStyle='rgba(150,130,105,.06)';c.lineWidth=.6;for(let y=96;y<LH;y+=3){c.beginPath();c.moveTo(X0,y);c.lineTo(LW+BGM,y+(rnd()-.5)*1.5);c.stroke()}
 c.strokeStyle='rgba(120,100,80,.035)';c.lineWidth=.5;for(let x=X0;x<LW+BGM;x+=6){c.beginPath();c.moveTo(x,90);c.lineTo(x+22,LH);c.stroke();c.beginPath();c.moveTo(x+22,90);c.lineTo(x,LH);c.stroke()}
 let g=c.createLinearGradient(0,90,0,LH);g.addColorStop(0,'rgba(60,50,40,.26)');g.addColorStop(.12,'rgba(60,50,40,.06)');g.addColorStop(.3,'rgba(60,50,40,0)');g.addColorStop(1,'rgba(60,50,40,.14)');c.fillStyle=g;c.fillRect(X0,90,XW,LH);
 let vg=c.createRadialGradient(200,250,120,200,250,340);vg.addColorStop(0,'rgba(50,40,30,0)');vg.addColorStop(1,'rgba(50,40,30,.16)');c.fillStyle=vg;c.fillRect(X0,90,XW,LH);c.restore();
 if(S.decor.rug){c.save();c.translate(216,244);c.scale(1,.42);c.fillStyle='rgba(0,0,0,.14)';el(c,4,10,176,120);c.fillStyle='#CFC6B8';el(c,0,0,172,116);c.strokeStyle='#8C857A';c.lineWidth=5;c.beginPath();c.ellipse(0,0,156,102,0,0,7);c.stroke();c.fillStyle='#B8AFA2';el(c,0,0,128,80);c.strokeStyle='rgba(255,255,255,.35)';c.lineWidth=2;for(let k=0;k<5;k++){c.beginPath();c.ellipse(0,0,40+k*18,24+k*12,0,0,7);c.stroke()}c.restore()}
 let wg=c.createLinearGradient(0,0,0,92);wg.addColorStop(0,TH().wall0);wg.addColorStop(1,TH().wall1);c.fillStyle=wg;c.fillRect(X0,0,XW,92);
 for(let i=0;i<320;i++){c.fillStyle=`rgba(${rnd()<.5?'255,255,255':'70,70,66'},${.03+rnd()*.05})`;el(c,X0+rnd()*XW,rnd()*88,4+rnd()*16,2+rnd()*8)}
 for(let i=0;i<2600;i++){c.fillStyle=rnd()<.5?'rgba(60,60,58,.18)':'rgba(255,255,255,.2)';c.fillRect(X0+rnd()*XW,rnd()*86,.8,.8)}
 c.strokeStyle='rgba(70,70,66,.32)';c.lineWidth=.7;for(let x=X0+10;x<LW+BGM;x+=92){c.beginPath();c.moveTo(x,0);c.lineTo(x,86);c.stroke()}c.beginPath();c.moveTo(X0,44);c.lineTo(LW+BGM,44);c.stroke();
 for(let x=X0+10;x<LW+BGM;x+=92)for(const dx of[23,69])for(const y of[20,66]){c.fillStyle='#7D7C77';circ(c,x+dx,y,1.5);c.fillStyle='rgba(255,255,255,.35)';circ(c,x+dx+.4,y+.5,.6)}
 c.fillStyle=TH().base;c.fillRect(X0,85,XW,7);c.fillStyle='rgba(0,0,0,.12)';c.fillRect(X0,91.5,XW,1.5);if(L>=4){c.fillStyle='#C99A45';c.fillRect(X0,84.4,XW,1.2)}
 c.save();c.translate(22,0);c.fillStyle='#D9D5CD';c.fillRect(8,20,46,72);c.fillStyle='#F1EEE9';c.fillRect(12,24,38,68);c.strokeStyle='rgba(0,0,0,.08)';c.lineWidth=1;c.strokeRect(15,58,32,30);c.fillStyle='rgba(180,210,225,.5)';rr(c,17,29,28,26,2);c.fill();c.fillStyle='rgba(255,255,255,.45)';c.fillRect(20,31,4,22);c.fillStyle='#2A2A2A';c.fillRect(42,58,2.2,9);c.fillStyle='#F6EEDF';rr(c,19,62,20,10,2);c.fill();c.fillStyle='#2E6B4A';c.font=`800 6px ${FONT}`;c.textAlign='center';c.fillText('OPEN',29,69.5);
 c.fillStyle='#2A2A2A';c.fillRect(22,14,18,2);circ(c,31,19,2.6);c.restore();
 drawBagCabinet(c);
 const signW=L===5?120:136;c.fillStyle='rgba(0,0,0,.18)';rr(c,200-signW/2+2,33,signW,30,4);c.fill();c.fillStyle=L===5?'#14161F':'#2C2C2B';rr(c,200-signW/2,30,signW,30,4);c.fill();c.strokeStyle=L>=4?'#E0B863':'rgba(230,194,122,.7)';c.lineWidth=1.1;rr(c,200-signW/2+2.5,32.5,signW-5,25,3);c.stroke();
 c.fillStyle='#E6C27A';c.textAlign='center';c.textBaseline='middle';if(L===5){c.font=`400 20px ${DFONT}`;c.fillText('J I L L',200,46)}else{c.font=`400 ${L===1?11:12.5}px ${DFONT}`;c.fillText(LV().n,200,45.5)}c.textBaseline='alphabetic';

 if(S.decor.art>=2){for(const [x,col] of[[146,'#6E8A9A'],[228,'#C08A6A']]){c.fillStyle='#2A2A2A';c.fillRect(x,62,26,21);c.fillStyle='#F3F0EA';c.fillRect(x+2.5,64.5,21,16);c.fillStyle=col;circ(c,x+13,72.5,5.5)}}
 if(S.rooms&&S.rooms.side)drawArch(c,SIDE_ARCH.x,SIDE_ARCH.y,SIDE_ARCH.w,80,'側廳 ›');
 if(S.decor.bar&&!(S.rooms&&S.rooms.side)){c.fillStyle='#2A2A28';c.fillRect(342,48,54,22);const bc=['#2E6B4A','#8A2A2A','#C99A45','#3A5A8A','#6B3A5A','#D9C27A'];for(let i=0;i<8;i++){c.fillStyle=bc[i%6];rr(c,345+i*6.4,50-(i%3)*2,4.2,17+(i%3)*2,1.5);c.fill()}c.fillStyle='#8C8A84';c.fillRect(290,86,110+BGM,18);c.fillStyle='#A7A59F';c.fillRect(290,90,110+BGM,14);c.fillStyle='#ECE9E3';c.fillRect(288,84,112+BGM,3);for(const x of[306,336,366]){c.fillStyle='#2A2A2A';c.fillRect(x-.8,108,1.6,10);c.fillStyle='#D9D5CD';el(c,x,107,7,3)}}
 return cv}
function drawProps(c){const [x,y,h]=[88,10,68];
 if(propOn('plant')){c.fillStyle='#8A6A42';rr(c,x+3,y+h-7,9,7,1.5);c.fill();c.fillStyle='#7FA36A';for(let k=0;k<6;k++)el(c,x+7.5+Math.cos(k*1.05)*2.6,y+h-9-Math.sin(k*1.05)*1.6,2.4,1.6);c.fillStyle='#A8C48E';circ(c,x+7.5,y+h-9.5,1.4)}
 if(propOn('flowers')){const fx=x+19;c.fillStyle='#C9D6DE';rr(c,fx-3,y+h-9,6,9,2);c.fill();c.fillStyle='rgba(255,255,255,.5)';c.fillRect(fx-2,y+h-8,1.2,6);c.strokeStyle='#5E8F4E';c.lineWidth=.8;for(const dx of[-2,0,2]){c.beginPath();c.moveTo(fx,y+h-9);c.lineTo(fx+dx*1.4,y+h-16);c.stroke()}for(const [dx,col] of[[-2.8,'#E8798A'],[0,'#F4C44E'],[2.8,'#E8798A']])for(let k=0;k<5;k++){c.fillStyle=col;el(c,fx+dx+Math.cos(k*1.26)*1.7,y+h-16.5+Math.sin(k*1.26)*1.7,1.2,1.2)}c.fillStyle='#F7EDDC';circ(c,fx-2.8,y+h-16.5,.7);circ(c,fx+2.8,y+h-16.5,.7)}
 if(propOn('drawing')){const dx=190,dy=64;c.fillStyle='rgba(0,0,0,.14)';c.fillRect(dx+1,dy+1,20,15);c.fillStyle='#FFFDF7';c.fillRect(dx,dy,20,15);c.fillStyle='#C99A45';c.fillRect(dx+8,dy-2,4,2);c.strokeStyle='#2E2019';c.lineWidth=.6;c.beginPath();c.moveTo(dx+3,dy+11);c.lineTo(dx+7,dy+5);c.lineTo(dx+10,dy+9);c.lineTo(dx+13,dy+4);c.lineTo(dx+17,dy+11);c.stroke();c.fillStyle='#E8798A';circ(c,dx+14.5,dy+9.5,1.3);c.fillStyle='#5E8FA8';el(c,dx+6,dy+12.5,3,1)}}
function drawWindows(c,dusk,now){const wins=[[88,10,42,68]];const d=clamp(dusk,0,1);const W=wxNow();const wet=W==='rain'||W==='storm';
 for(const [x,y,w,h] of wins){let g=c.createLinearGradient(0,y,0,y+h);const top=wet?(W==='storm'?'#8A93A0':'#B9C2CC'):W==='hot'?'#FFEFC8':W==='cool'?'#EAF4F8':'#FFF4DE',bot=wet?(W==='storm'?'#6E7683':'#9AA4B0'):'#FCE4BE';g.addColorStop(0,mix(top,'#3A3E5E',d));g.addColorStop(1,mix(bot,'#4E4666',d));c.fillStyle=g;c.fillRect(x,y,w,h);
  if(wet){/* rain on the glass: streaks that run down, more in a storm; now and then a flash */const n=W==='storm'?14:7;c.strokeStyle=`rgba(230,240,250,${W==='storm'?.55:.4})`;c.lineWidth=.8;for(let k=0;k<n;k++){const ph=((now*(W==='storm'?.9:.5))+k*.37)%1;const rx=x+3+((k*17)%(w-6));const ry=y+ph*h;c.beginPath();c.moveTo(rx,ry);c.lineTo(rx-1,ry+6+(k%3)*3);c.stroke()}if(W==='storm'&&Math.sin(now*.53)*Math.sin(now*2.9)>.985){c.fillStyle='rgba(255,255,255,.55)';c.fillRect(x,y,w,h)}}
  const pw=w/2;for(let p=0;p<2;p++){const px=x+p*pw;c.fillStyle='#F3F1EC';c.fillRect(px+.5,y+.5,pw-1,h-1);
   for(let yy=y+4;yy<y+h-4;yy+=3.3){c.fillStyle='#FCFBF8';c.fillRect(px+3.5,yy,pw-7,2.1);c.fillStyle=d<.55?`rgba(255,214,150,${.55-d*.7})`:`rgba(36,38,62,${.25+(d-.55)*.6})`;c.fillRect(px+3.5,yy+2.1,pw-7,1.2)}
   c.fillStyle='#E4E0D9';c.fillRect(px+pw/2-.6,y+4,1.2,h-8);c.strokeStyle='#E0DCD4';c.lineWidth=1;c.strokeRect(px+1,y+1,pw-2,h-2)}
  c.strokeStyle='#E6E3DC';c.lineWidth=2.2;c.strokeRect(x,y,w,h);c.fillStyle='#EFECE6';c.fillRect(x-3,y+h,w+6,3);
  if(S.decor.plants>=3){c.fillStyle='#C06A3E';rr(c,x+w-16,y+h-8,12,9,2);c.fill();for(let k=0;k<5;k++)leaf(c,x+w-10+Math.cos(k)*4,y+h-11-k,10,4,-1.6+k*.6,k%2?'#3F7F32':'#5E9E3D')}}}
function lightSpots(){const L=S.decor.lights;const a=[{x:53,y:14,r:40,k:.6}];if(L>=1)a.push({x:110,y:58,r:110,k:1},{x:272,y:58,r:110,k:1});if(L>=2)a.push({x:84,y:44,r:60,k:.7});if(L>=3)a.push({x:200,y:22,r:150,k:1});if(S.decor.bar)a.push({x:345,y:80,r:70,k:.7});return a}
function drawLampBodies(c,now){const L=S.decor.lights;const brass=(x,y,w)=>{let g=c.createLinearGradient(x-w,0,x+w,0);g.addColorStop(0,'#9A6E22');g.addColorStop(.5,'#EAC274');g.addColorStop(1,'#8E6422');return g};
 if(L>=1)for(const x of[110,272]){c.strokeStyle='#3A2A20';c.lineWidth=.8;c.beginPath();c.moveTo(x,0);c.lineTo(x,48);c.stroke();c.fillStyle=brass(x,0,12);c.beginPath();c.moveTo(x-4,46);c.lineTo(x+4,46);c.lineTo(x+13,58);c.lineTo(x-13,58);c.closePath();c.fill();c.fillStyle='#FFF1C4';el(c,x,58.5,5,1.8)}
 if(L>=2)for(const x of[84]){c.fillStyle=brass(x,0,5);c.fillRect(x-1,40,2,8);c.fillStyle='#FFE9B8';el(c,x,38,4,5);c.fillStyle=brass(x,0,6);rr(c,x-5,44,10,3,1);c.fill()}
 if(L>=3){c.strokeStyle='#8E6422';c.lineWidth=1;c.beginPath();c.moveTo(200,0);c.lineTo(200,10);c.stroke();c.fillStyle=brass(200,0,26);rr(c,176,10,48,4,2);c.fill();for(let k=0;k<5;k++){const x=180+k*10;c.fillStyle='#FFE9B8';el(c,x,19,2.2,4);c.fillStyle='#C99A45';c.fillRect(x-.6,14,1.2,3)}}}
function drawBench(c){const tier=S.decor.chairs;const wood=tier===0?'#8A5A36':tier===1?'#5E3B22':'#C99A45';const seat=tier===2?'#3F6B55':tier===1?'#7A4E2C':'#A06A3E';const x=BENCH.x,w=BENCH.w,y0=BENCH.seats[0]-16,y1=BENCH.seats[2]+12;
 softShadow(c,x+1,y1+1,w*.75,3.2,.2);
 c.fillStyle=wood;c.fillRect(x-w/2+1,y1-3,3,7);c.fillRect(x+w/2-4,y1-3,3,7);
 c.fillStyle=seat;rr(c,x-w/2,y0,w,y1-y0,3);c.fill();c.strokeStyle='rgba(60,34,22,.45)';c.lineWidth=.7;c.stroke();
 {/* a long cushion, the sofa's cream, so the bench belongs to the same room */let cg=c.createLinearGradient(x-w/2,0,x+w/2,0);cg.addColorStop(0,'#D9C9A9');cg.addColorStop(.45,'#EFE2C8');cg.addColorStop(1,'#CDBB9C');c.fillStyle=cg;rr(c,x-w/2+2.5,y0+2.5,w-5,y1-y0-6,4);c.fill();c.strokeStyle='rgba(90,70,45,.28)';c.lineWidth=.7;c.stroke();c.strokeStyle='rgba(90,70,45,.18)';for(const sy of[BENCH.seats[0]+20,BENCH.seats[1]+20]){c.beginPath();c.moveTo(x-w/2+5,sy);c.lineTo(x+w/2-5,sy);c.stroke()}c.fillStyle='rgba(255,255,255,.3)';rr(c,x-w/2+5,y0+5,3,y1-y0-11,1.5);c.fill()}
 c.fillStyle=wood;rr(c,x-w/2,y1-3,w,3.5,1.5);c.fill();
 c.fillStyle=wood;rr(c,x-w/2-6,y0-10,6,y1-y0+8,2);c.fill();c.strokeStyle='rgba(60,34,22,.45)';c.stroke();c.fillStyle='rgba(255,255,255,.14)';rr(c,x-w/2-5,y0-8,1.6,y1-y0+4,.8);c.fill()}
function drawChair(c,x,y,side,back){const tier=S.decor.chairs;const wood=tier===0?'#8A5A36':tier===1?'#5E3B22':'#C99A45';const seat=tier===2?'#3F6B55':tier===1?'#7A4E2C':'#A06A3E';
 if(back){c.fillStyle=tier===2?'#35604B':wood;rr(c,x-9,y-26,18,16,tier===1?8:3);c.fill();if(tier===1){c.fillStyle='#4E3020';rr(c,x-6,y-23,12,10,5);c.fill()}return}
 const bx=x+side*8;c.fillStyle=wood;c.fillRect(bx-1.5,y-26,3,26);if(tier===2){c.fillStyle='#35604B';rr(c,bx-3,y-26,6,18,3);c.fill()}else if(tier===1){c.strokeStyle=wood;c.lineWidth=2.4;c.beginPath();c.arc(bx,y-20,6,Math.PI*.5+side*.8,Math.PI*1.5+side*.8,side>0);c.stroke()}else{/* a plain wooden back: two slats and a top rail */c.fillStyle=wood;rr(c,bx-3.2,y-26,6.4,3,1.2);c.fill();c.fillStyle=shade(wood,-.12);c.fillRect(bx-3.2,y-22,1.4,14);c.fillRect(bx+1.8,y-22,1.4,14)}
 softShadow(c,x,y+4,9,2.6,.16);c.fillStyle=seat;el(c,x,y-4,9,3.6);c.fillStyle='rgba(255,255,255,.18)';el(c,x-2,y-5,4.5,1.4);c.fillStyle=wood;c.fillRect(x-7,y-3,2,8);c.fillRect(x+5,y-3,2,8)}
function drawTableFull(c,t,now){const g=t.group;const seated=g&&['reading','order','wait','eat','check'].includes(g.state);const seats=seatPos(t);const four=t.seats===4;const L=S.level;
 softShadow(c,t.x,t.y+6,four?40:28,four?12:9,.24);
 if(four){c.fillStyle='#6A2632';rr(c,t.x-34,t.y-40,68,26,9);c.fill();c.fillStyle='#7E2E3C';rr(c,t.x-34,t.y-20,68,10,4);c.fill();c.strokeStyle='rgba(0,0,0,.15)';c.lineWidth=1;for(let k=-2;k<=2;k++){c.beginPath();c.moveTo(t.x+k*13,t.y-38);c.lineTo(t.x+k*13,t.y-22);c.stroke()}c.fillStyle='#C99A45';c.fillRect(t.x-34,t.y-41,68,2)}
 const order=seats.map((sp,k)=>({sp,k})).sort((a,b)=>a.sp.dy-b.sp.dy);
 for(const {sp,k} of order){const x=t.x+sp.dx,y=t.y+sp.dy;if(!four||sp.side!==0)drawChair(c,x,y,sp.side,false);
  if(seated&&k<g.size){const L0=g.looks[k%g.looks.length];const looking=!!(g.lookT&&R&&g.lookT>R.t&&g.lookCat&&!g.lookCat.hidden);const mood=looking?'happy':g.state==='eat'?'eat':g.pat>.6?'happy':g.pat>.3?'ok':'sad';let gaze=null,hold=null;
   if(g.reg==='dylan'&&R&&g.gaze>R.t){const J=R.jill;gaze={x:(J.x>=x?1:-1)*(sp.side>0?-1:1),y:J.y>y?.5:-.3}}
   else if(looking){const cc=g.lookCat;gaze={x:(cc.x>=x?1:-1)*(sp.side>0?-1:1),y:cc.y>y-14?.45:-.25};
    /* the photographer: phone up half a second before the shot, still up for a moment after it */
    if(k===0&&g.photo&&g.photoT0&&R.t>g.photoT0-.9&&R.t<g.photoT0+.7)hold='camera'}
   drawPerson(c,x,y,L0,{seated:true,mood,flip:sp.side>0,bob:g.state==='eat'&&!looking?Math.sin(now*6+k)*.6:Math.sin(now*1.4+g.seed+k*1.7)*.3,chew:g.state==='eat'&&!looking&&Math.sin(now*9+k)>0,blink:Math.sin(now*1.3+g.seed+k*2)>.97,gaze,hold});
   /* a face you have seen before gets its name on the floor, like the staff: 'oh, it is you again' */
   /* 2.1: a party of two or more talks while they wait — a little bubble passes between them */
   if(g.size>=2&&!looking&&['reading','wait','order'].includes(g.state)&&!g.rowdy){const ph=now*.7+g.seed;const who=Math.floor(ph/6.28)%Math.min(g.size,4);if(k===who&&Math.sin(ph)>.35){const f=sp.side>0?-1:1;c.fillStyle='rgba(255,250,240,.92)';const bx=x+f*11,by=y-56;rr(c,bx-6.5,by-4.5,13,9,4);c.fill();c.beginPath();c.moveTo(bx-f*3,by+4);c.lineTo(bx-f*6,by+8);c.lineTo(bx-f*1,by+4.4);c.fill();c.fillStyle='#2E2019';for(let i=-1;i<=1;i++)circ(c,bx+i*2.8,by+.3,.8)}}
   if(k===0&&g.reg&&(S.regulars[g.reg]||0)>=1&&(g.reg!=='dylan'||(S.regulars.dylan||0)>=1))nameTag(c,x,y-50,g.reg==='dylan'?'Dylan':g.name.length>5?g.name.slice(0,5):g.name)}
  else if(LIFE.dylan&&LIFE.dylan.seated&&LIFE.dylan.table===t.i&&LIFE.dylan.seat===k){const D=LIFE.dylan;drawPerson(c,x,y,DYLAN.looks[0],{seated:true,mood:'happy',flip:sp.side>0,bob:Math.sin(now*1.5)*.3,blink:Math.sin(now*1.3+2)>.975,hold:D.phone?'phone':null,gaze:D.phone?{x:0,y:.6}:null})}}
 if(seated&&R&&g.photo&&g.photoT0&&R.t>=g.photoT0&&R.t-g.photoT0<.22){/* the flash: a small white burst at the phone */const sp=seatPos(t)[0];const px=t.x+sp.dx+(sp.side>0?-7:7),py=t.y+sp.dy-30;const a=1-(R.t-g.photoT0)/.22;c.fillStyle=`rgba(255,255,255,${.85*a})`;circ(c,px,py,6+4*(1-a));c.fillStyle=`rgba(255,255,255,${a})`;circ(c,px,py,2.5)}
 const rx=four?34:22,ry=four?12:10.5;const top=L>=4?'#6E4128':L===3?'#8A5836':'#B07744';const edge=L>=4?'#4E2E1C':'#7A4E2C';
 c.fillStyle=edge;c.fillRect(t.x-2.5,t.y-4,5,12);c.fillStyle='#3A2A20';el(c,t.x,t.y+7,8,2.6);
 c.fillStyle=edge;el(c,t.x,t.y-3,rx,ry);c.fillStyle=top;el(c,t.x,t.y-6,rx,ry);
 if(L>=3){c.fillStyle='#F7F2E8';el(c,t.x,t.y-6.5,rx+1,ry+.5);c.fillStyle='#E9E1D2';c.beginPath();c.ellipse(t.x,t.y-6.5,rx+1,ry+.5,0,0,Math.PI);c.lineTo(t.x-rx-1,t.y-2);c.ellipse(t.x,t.y-2,rx+1,ry+.5,0,Math.PI,0,true);c.fill();c.fillStyle='#F7F2E8';el(c,t.x,t.y-7,rx,ry)}
 else{c.strokeStyle='rgba(60,30,10,.14)';c.lineWidth=.6;for(let k=1;k<4;k++){c.beginPath();c.ellipse(t.x+2,t.y-6,rx*k/4,ry*k/4,0,.3,2.8);c.stroke()}c.fillStyle='rgba(255,255,255,.14)';el(c,t.x-rx*.3,t.y-9,rx*.45,ry*.35);c.strokeStyle='rgba(255,255,255,.3)';c.lineWidth=.9;c.beginPath();c.ellipse(t.x,t.y-6,rx-.6,ry-.6,0,Math.PI*1.08,Math.PI*1.6);c.stroke();c.strokeStyle='rgba(40,20,5,.22)';c.beginPath();c.ellipse(t.x,t.y-6,rx-.4,ry-.4,0,.2,Math.PI*.8);c.stroke()}
 const pos=[[-9,-9],[9,-9],[-12,-3],[12,-3],[0,-6]];const n=t.plates.length;
 if(!g&&!t.dirty&&!n){const sp=four?[[-18,-8],[18,-8]]:[[-11,-7],[11,-7]];for(const [dx,dy] of sp){c.fillStyle='rgba(0,0,0,.12)';el(c,t.x+dx+.5,t.y+dy+1,5.4,3);c.fillStyle='#FFFFFF';el(c,t.x+dx,t.y+dy,5.2,2.9);c.fillStyle=L>=4?'#2F4A40':L>=2?'#B84A3A':'#E2D2B4';c.beginPath();c.moveTo(t.x+dx-2,t.y+dy-1.5);c.lineTo(t.x+dx+2.5,t.y+dy-1.5);c.lineTo(t.x+dx,t.y+dy+1.5);c.fill();c.strokeStyle='#B9C1C4';c.lineWidth=.8;c.beginPath();c.moveTo(t.x+dx-7,t.y+dy-2);c.lineTo(t.x+dx-7,t.y+dy+2.5);c.moveTo(t.x+dx+7,t.y+dy-2);c.lineTo(t.x+dx+7,t.y+dy+2.5);c.stroke()}}
 t.plates.slice(0,5).forEach((p,i)=>{const [dx,dy]=four?[pos[i][0]*1.6,pos[i][1]]:pos[i];const q=(t.dirty||(g&&g.ate))?'E':p.q;const pr=g&&g.state==='eat'&&g.eatDur?clamp(1-g.timer/g.eatDur,0,1):0;if(q==='E'){c.fillStyle='#fff';el(c,t.x+dx,t.y+dy,6.5,4.2);c.fillStyle='rgba(180,120,60,.4)';circ(c,t.x+dx+1,t.y+dy,1);circ(c,t.x+dx-2,t.y+dy+1,.8)}else{const cv=dishCanvas(p.d,p.q,64,S.decor.ware>0,p.want);const PS=four?22:20;c.drawImage(cv,t.x+dx-PS/2,t.y+dy-PS/2,PS,PS);if(pr>.12&&!VESSEL[p.d]){/* 2.1: the meal goes down while they eat — the plate shows through from the middle out */const e=clamp((pr-.12)/.8,0,1);c.fillStyle='rgba(255,255,255,.96)';el(c,t.x+dx,t.y+dy+.5,PS*.34*e,PS*.215*e);if(e>.5){c.fillStyle='rgba(180,120,60,.35)';circ(c,t.x+dx+1.5,t.y+dy+.5,.9);circ(c,t.x+dx-2,t.y+dy+1.2,.7)}}const D=DISH(p.d);if(D&&g&&(g.state==='wait'||g.state==='eat')&&pr<.5&&(D.cat==='main'||p.d==='soup'||p.d==='coffee'||p.d==='blacktea')){/* a little steam while it is fresh */for(let w=0;w<2;w++){const ph=(now*.55+w*.5+i*.3)%1;c.globalAlpha=(1-ph)*.28;c.fillStyle='#fff';circ(c,t.x+dx-2+w*4+Math.sin(now*2+w+i)*1.5,t.y+dy-8-ph*10,1.6+ph*1.8)}c.globalAlpha=1}}});
 if(t.dirty&&!n){c.fillStyle='#fff';el(c,t.x-6,t.y-7,6,4);el(c,t.x+6,t.y-6,6,4)}
 if(S.level>=2&&duskF()>.45){/* a tea light once the evening comes */const cx=t.x+(four?22:0),cy=t.y-(four?5:12);const fl=.8+Math.sin(now*11+t.i)*.2;c.fillStyle='rgba(0,0,0,.1)';el(c,cx,cy+2,3,1.3);c.fillStyle='#E8DFCF';rr(c,cx-2.4,cy-2.6,4.8,4,1);c.fill();c.fillStyle='#FFD27A';el(c,cx,cy-3.4,1.1,1.7*fl);c.fillStyle='rgba(255,200,110,.35)';circ(c,cx,cy-3,4.5*fl)}
 if(seated&&['reading','order','wait'].includes(g.state)){for(let k=0;k<Math.min(g.size,2);k++){const gx=t.x+(k?7:-7),gy=t.y-10;c.fillStyle='rgba(215,238,250,.6)';c.fillRect(gx-1.7,gy-5,3.4,5.5);c.fillStyle='rgba(255,255,255,.85)';c.fillRect(gx-1.7,gy-5,.9,5.5)}}
 if(L>=2){c.fillStyle='rgba(255,255,255,.7)';rr(c,t.x-2,t.y-15,4,6,1);c.fill();const fl=.8+Math.sin(now*8+t.i)*.2;c.fillStyle=`rgba(255,200,90,${fl})`;el(c,t.x,t.y-17,1.3,2.2)}
 }
function bubble(c,x,y,kind,pulse,extra){c.save();c.translate(x,y);const s=1+pulse*.08;c.scale(s,s);c.fillStyle='rgba(0,0,0,.2)';rr(c,-11,-10,24,21,8);c.fill();c.fillStyle=kind==='angry'?'#4A3A3A':'#FFFDF7';rr(c,-12,-12,24,21,8);c.fill();c.beginPath();c.moveTo(-3,8);c.lineTo(3,8);c.lineTo(0,13);c.fill();
 c.lineCap='round';
 if(kind==='menu'){c.fillStyle='#7A2E3A';rr(c,-7,-7,14,11,1.5);c.fill();c.fillStyle='#F6EEDF';c.fillRect(-5,-5,4,7);c.fillRect(1,-5,4,7);c.fillStyle='#C99A45';c.fillRect(-.5,-7,1,11)}
 else if(kind==='order'){c.fillStyle='#D4553A';rr(c,-2,-9,4,10,2);c.fill();circ(c,0,4.5,2.2)}
 else if(kind==='wait'){const [a,b]=extra;c.fillStyle='#6B5647';c.font=`800 8.5px ${FONT}`;c.textAlign='center';c.textBaseline='middle';c.fillText(`${a}/${b}`,0,-1.5);c.fillStyle='#C99A45';c.fillRect(-7,4,14*(a/b),2)}
 else if(kind==='ready'){let g=c.createLinearGradient(0,-8,0,4);g.addColorStop(0,'#F4F6F7');g.addColorStop(1,'#A9B4BA');c.fillStyle=g;c.beginPath();c.arc(0,3,8,Math.PI,0);c.fill();c.fillStyle='#8E9AA0';c.fillRect(-10,3,20,2);circ(c,0,-5.5,1.5)}
 else if(kind==='check'){c.fillStyle='#E6C27A';circ(c,0,-1.5,7.5);c.strokeStyle='#8E6422';c.lineWidth=1;c.beginPath();c.arc(0,-1.5,5.6,0,7);c.stroke();c.fillStyle='#6B4712';c.font=`800 9px ${FONT}`;c.textAlign='center';c.textBaseline='middle';c.fillText('$',0,-1)}
 else if(kind==='angry'){c.strokeStyle='#FF6A4A';c.lineWidth=2;c.lineCap='round';for(let q=0;q<4;q++){c.save();c.rotate(q*Math.PI/2+.78);c.beginPath();c.arc(5,5,3.2,Math.PI,Math.PI*1.5);c.stroke();c.restore()}}
 else if(kind==='dirty'){c.strokeStyle='#6E9AB0';c.lineWidth=1.6;for(let k=0;k<3;k++){const a=k*2.1;c.beginPath();c.moveTo(Math.cos(a)*2,Math.sin(a)*2-2);c.lineTo(Math.cos(a)*7,Math.sin(a)*7-2);c.stroke()}c.fillStyle='#8FB8CC';circ(c,0,-2,2)}
 c.restore()}
function patBar(c,x,y,p){c.fillStyle='rgba(20,15,10,.55)';rr(c,x-14,y,28,5,2.5);c.fill();c.fillStyle=p>.55?'#7BC06A':p>.28?'#F0B43A':'#E0543A';rr(c,x-13,y+1,26*p,3,1.5);c.fill()}
function drawPlant(c,x,y,kind){softShadow(c,x,y+2,12,4,.2);c.fillStyle='#B8603A';c.beginPath();c.moveTo(x-10,y-14);c.lineTo(x+10,y-14);c.lineTo(x+7,y+1);c.lineTo(x-7,y+1);c.fill();c.fillStyle='#9A4E2E';c.fillRect(x-10.5,y-16,21,3);
 if(kind==='tall'){for(let i=0;i<9;i++)leaf(c,x+Math.sin(i*1.7)*9,y-26-i*5,20,8,-1.57+Math.sin(i*2.3)*.9,i%2?'#3F7F32':'#5E9E3D')}else{for(let i=0;i<8;i++)leaf(c,x+Math.cos(i*.8)*8,y-20-Math.sin(i)*4,14,6,i*.8,i%2?'#4E8A3A':'#6FAE45')}}
function plantSpots(){const P=S.decor.plants;const a=[];if(P>=1)a.push({x:250,y:106,k:'tall'});if(P>=2)a.push({x:264,y:102,k:'tall'},{x:240,y:104,k:'bush'});if(P>=3)a.push({x:278,y:100,k:'bush'});return a}
function view(){if(R)return R;if(!IDLE)IDLE=makeIdle();return IDLE}
function drawStringLights(c,now,dusk){if(S.level<2)return;const x0=-BGM,x1=LW+BGM;const yAt=x=>{const seg=(((x-x0)%130)+130)%130/130;return 4+Math.sin(seg*Math.PI)*12};c.strokeStyle='rgba(40,30,20,.75)';c.lineWidth=.7;c.beginPath();for(let x=x0;x<=x1;x+=4)c.lineTo(x,yAt(x));c.stroke();
 for(let x=x0+10;x<x1;x+=22){const y=yAt(x)+3;const tw=.75+Math.sin(now*2+x*.3)*.25;c.fillStyle=`rgba(255,${Math.round(205+tw*30)},${Math.round(130+tw*40)},${.65+dusk*.35})`;el(c,x,y,1.8,2.4);if(dusk>.15){let g=c.createRadialGradient(x,y,0,x,y,10);g.addColorStop(0,`rgba(255,200,120,${.4*dusk*tw})`);g.addColorStop(1,'rgba(255,200,120,0)');c.fillStyle=g;c.fillRect(x-10,y-10,20,20)}}}
function drawScene(now){const c=sctx;c.setTransform(1,0,0,1,0,0);c.globalAlpha=1;c.globalCompositeOperation='source-over';if(c.filter!==undefined&&c.filter!=='none')c.filter='none';c.fillStyle='#1E1714';c.fillRect(0,0,sc.width,sc.height);
 bgCheck(now);const s=SV.s*DPR;c.setTransform(s,0,0,s,SV.ox*DPR,SV.oy*DPR);const X0=-BGM,XW=LW+BGM*2;
 const TOP=SV.oy/SV.s,WT=wallTop();
 if(room!=='main'){c.save();c.beginPath();c.rect(X0,-TOP,XW,LH+TOP);c.clip();drawOtherRoom(c,now,duskF(),view(),X0,XW,TOP);c.restore();return}
 if(TOP>1){c.fillStyle=TH().base;c.fillRect(X0,-TOP,XW,TOP);
  if(WT<0){let wg=c.createLinearGradient(0,WT,0,0);wg.addColorStop(0,TH().wall1);wg.addColorStop(1,TH().wall0);c.fillStyle=wg;c.fillRect(X0,WT,XW,-WT);
   c.strokeStyle='rgba(70,70,66,.3)';c.lineWidth=.7;for(let x=X0+10;x<LW+BGM;x+=92){c.beginPath();c.moveTo(x,WT);c.lineTo(x,0);c.stroke()}for(let y=0;y>WT;y-=44){c.beginPath();c.moveTo(X0,y);c.lineTo(LW+BGM,y);c.stroke()}
   for(let x=X0+10;x<LW+BGM;x+=92)for(const dx of[23,69])for(let y=-24;y>WT+3;y-=44){c.fillStyle='#7D7C77';circ(c,x+dx,y,1.5);c.fillStyle='rgba(255,255,255,.35)';circ(c,x+dx+.4,y+.5,.6)}
   c.fillStyle='rgba(255,255,255,.05)';for(let i=0;i<24;i++)el(c,X0+((i*97)%XW),WT+((i*53)%(-WT)),14,5);
   c.fillStyle=TH().base;c.fillRect(X0,WT-7,XW,7);c.fillStyle='rgba(255,220,160,.28)';c.fillRect(X0,WT-2,XW,2);c.fillStyle='rgba(0,0,0,.1)';c.fillRect(X0,WT,XW,2)}
  c.fillStyle='#3A3A3A';rr(c,20,-TOP+Math.max(3,(TOP+WT-7)*.35),150,6,2);c.fill();c.fillStyle='rgba(255,255,255,.12)';for(let x=24;x<168;x+=4)c.fillRect(x,-TOP+Math.max(3,(TOP+WT-7)*.35)+1,1,4);
  if(S.decor.lights){c.strokeStyle='#3A2A20';c.lineWidth=.8;for(const x of[110,272]){c.beginPath();c.moveTo(x,-TOP);c.lineTo(x,0);c.stroke()}}}
 c.save();c.beginPath();c.rect(X0,-TOP,XW,LH+TOP);c.clip();
 const dusk=duskF();const key=S.level+'|'+(S.theme||'')+'|'+JSON.stringify(S.decor)+'|'+JSON.stringify(S.props||{})+'|'+SV.s+'|'+DPR+'|'+S.menu.join(',');if(!bg||bgKey!==key){bg=makeBg();bgKey=key}c.drawImage(bg,X0,0,XW,LH);
 drawWindows(c,dusk,now);drawProps(c);drawLampBodies(c,now);drawBagSparkle(c,now);drawWallRun(c,now);drawStringLights(c,now,clamp(dusk,0,1));
 if(dusk<.85){c.save();c.globalCompositeOperation='lighter';const a=(.85-dusk)*.11;const wins=[[64,58]];if(S.level>=2)wins.push([276,58]);for(const [x,w] of wins){let g=c.createLinearGradient(0,70,0,310);g.addColorStop(0,`rgba(255,196,120,${a})`);g.addColorStop(1,'rgba(255,196,120,0)');c.fillStyle=g;c.beginPath();c.moveTo(x,70);c.lineTo(x+w,70);c.lineTo(x+w+120,310);c.lineTo(x+56,310);c.closePath();c.fill()}c.restore()}
 const V=view();const J=V.jill;const list=[];
 for(const t of V.tables)if((t.room||'main')==='main')list.push({y:t.y,f:()=>drawTableFull(c,t,now)});
 for(const p of plantSpots())list.push({y:p.y,f:()=>drawPlant(c,p.x,p.y,p.k)});
 for(const G of CATGEAR)if(gearOn(G.k)&&G.room==='main'&&G.poses)list.push({y:G.y-6,f:()=>drawGear(c,G,now)});if(gearOn('box')){const bc=CATS&&CATS.find(k=>k.gear==='box'&&k.st==='gear'&&!k.away);if(bc)list.push({y:CATGEAR[0].y+12,f:()=>drawGear(c,CATGEAR[0],now,true)})}
 list.push({y:354+FY,f:()=>drawChalkboard(c,now)});
 list.push({y:352+FY,f:()=>drawCatTree(c,now)},{y:357+FY,f:()=>drawCatTree2(c,now)},{y:355+FY,f:()=>drawStairs(c)},{y:SPOT.scr2.y,f:()=>drawPost(c,now)},{y:BENCH.seats[0]-20,f:()=>drawBench(c)},{y:SOFA.y,f:()=>drawSofaGroup(c,now)},{y:LIFE.tv.y,f:()=>drawTV(c,LIFE.tv,now)});
 {const D=LIFE.dylan;if(D&&!D.seated&&!D.onSofa)list.push({y:D.y,f:()=>drawDylanFree(c,D,now)})}
 if(CATS)for(const k of CATS){if(k.hidden&&k.st==='hide2'&&k.peekT>0){list.push({y:k.y,f:()=>{c.save();c.translate(k.x,k.y);c.scale(CSC,CSC);catHead(c,k.def,0,-7,k.def.fluffy?6:5.4,{},false);c.restore()}});continue}if(k.sofa&&k.sofaOn)continue;if(!k.hidden&&(k.perch<0||k.st==='jump'||TREE.perches[k.perch].t===3))list.push({y:(k.sofa||k.sofaLeaving)?SOFA.front+1:k.y+(k.st==='bed'||k.st==='scr'||k.st==='eat'?2:0),f:()=>drawCat(c,k,now)})}
 list.push({y:SPOT.scr.y,f:()=>drawScratcher(c,now)},{y:SPOT.cave.y,f:()=>drawCave(c,now)},{y:SPOT.bed.y,f:()=>drawBed(c,now)},{y:SPOT.bowl.y,f:()=>drawBowls(c,now)});
 for(const g of V.groups)if(WALK_ST.includes(g.state)&&(g.room||'main')==='main')list.push({y:g.y,f:()=>drawWalkers(c,g,now)});
 if(!J.sofa&&(J.room||'main')==='main')list.push({y:J.y,f:()=>drawJillAt(c,J,V,now)});
 crewDraw(c,now,list,'main');incDraw(c,now,list);
 list.sort((a,b)=>a.y-b.y).forEach(i=>i.f());drawSay(c);
 drawCounter(c,now,V);drawPassStrip(c,now,V);
 c.save();c.globalCompositeOperation='multiply';c.fillStyle=wxTint(tintFor(dusk));c.fillRect(X0,-TOP,XW,LH+TOP);
 if(evening()&&!(R&&R.closing!=null&&R.closing<6)){/* after hours: the light gathers where someone is — the sofa when Jill is there, otherwise the room's middle */const L=LIFE.jill;const cx=L&&(L.on||L.reserved)?(SOFA.x0+SOFA.x1)/2:200,cy=L&&(L.on||L.reserved)?SOFA.seat:250;let eg=c.createRadialGradient(cx,cy,60,cx,cy,330);eg.addColorStop(0,'rgba(255,255,255,1)');eg.addColorStop(1,'rgba(196,186,200,1)');c.fillStyle=eg;c.fillRect(X0,-TOP,XW,LH+TOP)}c.restore();
 c.save();c.globalCompositeOperation='lighter';const lk=.12+clamp(dusk,0,1)*.2;for(const L0 of lightSpots()){let g=c.createRadialGradient(L0.x,L0.y,2,L0.x,L0.y+30,L0.r);g.addColorStop(0,`rgba(255,196,120,${lk*L0.k})`);g.addColorStop(1,'rgba(255,170,90,0)');c.fillStyle=g;c.fillRect(L0.x-L0.r,L0.y-L0.r,L0.r*2,L0.r*2.4)}
 for(const t of V.tables){if(S.level>=2){let g=c.createRadialGradient(t.x,t.y-15,1,t.x,t.y-15,26);g.addColorStop(0,`rgba(255,190,100,${.1+dusk*.12})`);g.addColorStop(1,'rgba(255,190,100,0)');c.fillStyle=g;c.fillRect(t.x-26,t.y-41,52,52)}}
 {let g=c.createRadialGradient(220,380+FY,10,220,380+FY,140);g.addColorStop(0,'rgba(255,170,80,.12)');g.addColorStop(1,'rgba(255,170,80,0)');c.fillStyle=g;c.fillRect(60,260,320,180)}
 if(LIFE.tv.on){const tv=LIFE.tv;let g=c.createRadialGradient(tv.x,tv.y-36,3,tv.x,tv.y-36,26);g.addColorStop(0,'rgba(170,200,255,.5)');g.addColorStop(.45,'rgba(170,200,255,.22)');g.addColorStop(1,'rgba(170,200,255,0)');c.fillStyle=g;c.fillRect(tv.x-28,tv.y-64,56,56)}c.restore();
 if(R){const pulse=(Math.sin(now*6)+1)/2;
  for(const t of R.tables)if((t.room||'main')==='main')drawTableOverlay(c,t,now,pulse);
  queued().forEach(g=>{if(g.state==='queue'&&!g.moving)patBar(c,g.x,g.y-(isSeated(g)?50:56),g.pat)});
  const qs=(J.cur?[J.cur.t]:[]).concat(J.q);qs.forEach((ti,k)=>{const t=R.tables[ti];if((t.room||'main')!=='main')return;c.fillStyle='#2E2019';circ(c,t.x+(t.seats===4?40:30),t.y-22,7);c.fillStyle='#E6C27A';c.font=`800 8px ${FONT}`;c.textAlign='center';c.textBaseline='middle';c.fillText(String(k+1),t.x+(t.seats===4?40:30),t.y-21.5)});
  for(const p of R.parts){if((p.room||'main')!=='main')continue;const a=1-p.t/p.life;if(p.kind==='coin'){c.fillStyle=`rgba(244,196,78,${a})`;el(c,p.x,p.y,3,3.4);c.fillStyle=`rgba(142,100,34,${a})`;el(c,p.x,p.y,1.4,1.8)}else{c.fillStyle=`rgba(255,230,140,${a})`;c.save();c.translate(p.x,p.y);c.rotate(p.t*6);c.fillRect(-2.5,-.6,5,1.2);c.fillRect(-.6,-2.5,1.2,5);c.restore()}}
  for(const f of R.floats){if((f.room||'main')!=='main')continue;const a=1-f.t/f.life;c.globalAlpha=Math.min(1,a*1.5);c.font=`800 ${f.big?12:9.5}px ${FONT}`;c.textAlign='center';c.textBaseline='middle';c.lineWidth=3;c.strokeStyle='rgba(30,20,15,.8)';c.strokeText(f.txt,f.x,f.y-f.t*22);c.fillStyle=f.col;c.fillText(f.txt,f.x,f.y-f.t*22);c.globalAlpha=1}
  if(R.fire>0){const a=.25+Math.sin(now*8)*.08;let g=c.createRadialGradient(200,220,150,200,220,320);g.addColorStop(0,'rgba(255,120,30,0)');g.addColorStop(1,`rgba(255,110,30,${a})`);c.fillStyle=g;c.fillRect(X0,-TOP,XW,LH+TOP)}}
 if(R&&R.blackout>0){R.blackout-=1/60;const a=R.blackout>2.2?.75:R.blackout>.5?.85:(R.blackout/.5)*.85;c.fillStyle=`rgba(8,6,12,${a})`;c.fillRect(X0,-TOP,XW,LH+TOP)}
 if(FLASH){c.fillStyle=`rgba(255,255,255,${(1-FLASH.t/.5)*.55})`;c.fillRect(FLASH.x-78,FLASH.y-82,156,112)}
 let vg=c.createRadialGradient(206,290,210,206,290,400);vg.addColorStop(0,'rgba(0,0,0,0)');vg.addColorStop(1,'rgba(15,8,4,.38)');c.fillStyle=vg;c.fillRect(X0,-TOP,XW,LH+TOP);
 c.restore()}
const WALK_ST=['arrive','queue','toTable','leave'];
function drawWalkers(c,g,now){const n=g.size;const sit=isSeated(g);const wact=g.state==='queue'&&!g.moving?g.wact:null;const mood=g.state==='leave'?(g.mood==='angry'?'angry':g.mood==='sad'?'sad':'happy'):(g.pat>.5?'happy':g.pat>.25?'ok':'sad');
  g.looks.forEach((L0,k)=>{const off=(k-(n-1)/2)*11;const stp=g.moving?Math.sin(g.walk+k):0;let gaze=null,hold=null;
   if(wact==='phone'&&k===0){hold='phone';gaze={x:0,y:.6}}else if(wact==='cat'&&g.wcat&&!g.wcat.hidden){gaze={x:g.wcat.x>=g.x?1:-1,y:g.wcat.y>g.y-20?.5:-.2}}else if(wact==='look'){gaze={x:1,y:-.1}}else if(wact==='talk'&&n>1){gaze={x:k?1:-1,y:.1}}
   if(sit){drawPerson(c,g.x+(n>1?(k%2?6:-6):0),g.y+(n>1?(k%2?3:-3):0)+Math.floor(k/2)*14,L0,{seated:true,lounge:{legs:0},mood,flip:false,hold,gaze,bob:Math.sin(now*1.3+g.seed+k*1.7)*.3,blink:Math.sin(now*1.4+g.seed+k)>.97});return}
   drawPerson(c,g.x+off,g.y+(k%2)*2,L0,{step:stp,bob:g.moving?Math.abs(stp)*-.8:0,mood,flip:g.tx<g.x,hold:g.moving?null:hold,gaze:g.moving?null:gaze,blink:Math.sin(now*1.4+g.seed+k)>.97});if(k===0&&(g.room||'main')==='front'&&streetWet())drawUmbrella(c,g.x+off+(g.tx<g.x?-3:3),g.y-30,UMB_COLS[Math.floor(g.seed*7)%UMB_COLS.length]);if(g.bus&&k===0){const fl=g.tx<g.x?-1:1;const px=g.x+off+fl*7,py=g.y-27;c.fillStyle='#FBFAF6';c.beginPath();c.ellipse(px,py,6.5,2.8,0,0,7);c.fill();c.strokeStyle='rgba(60,45,35,.55)';c.lineWidth=.7;c.stroke();c.fillStyle='rgba(120,90,70,.25)';c.beginPath();c.ellipse(px,py,3.2,1.2,0,0,7);c.fill()}})}
function drawJillAt(c,J,V,now){const moving=J.moving;const stp=moving?Math.sin(J.step):0;
  /* handwork in progress (chopping, stirring) and she is at the pass: show her at it */
  const cooking=!moving&&R&&phase==='service'&&Math.hypot(J.x-PASS.x,J.y-PASS.y)<6&&R.slots.some(s=>s.job&&s.job.step&&!chefHandles(s)&&(s.job.step.t==='work'||(s.job.step.t==='wait'&&s.job.step.anim==='stir')));
  if(V.fire>0){let fg=c.createRadialGradient(J.x,J.y-20,2,J.x,J.y-20,30);fg.addColorStop(0,'rgba(255,150,50,.5)');fg.addColorStop(1,'rgba(255,90,20,0)');c.fillStyle=fg;el(c,J.x,J.y-20,30,34)}
  /* concentrating while she cooks or hurries somewhere with a job; her usual smile otherwise; tired once the closing starts */
  const expr=(R&&R.closing!=null)?'tired':(cooking||(moving&&R&&R.jill.cur))?'focus':'smile';const pet=R&&R.jill.pet;const crouch=!!(pet&&pet.crouch);const look=R&&R.jill.lookAt?R.jill.lookAt:(pet?{x:pet.cat.x,y:pet.cat.y}:null);const gaze=look?{x:((look.x>=J.x?1:-1)*(J.face<0?-1:1)),y:(pet||look.down)?.55:.15}:null;
  const nod=R&&R.jill.nod>0?Math.sin(R.jill.nod*9)*1.4:0;const carrying=!!(J.carry&&J.carry.length);drawPerson(c,J.x,J.y+(crouch?4:0),JILL_LOOK,{jill:true,me:true,tall:!crouch,seated:!!J.sit||crouch,s:crouch?1:1.1,step:stp,carry:carrying,arms:cooking?[.35,1.0+Math.sin(now*9)*.2]:null,bob:(moving?Math.abs(stp)*-1:cooking?Math.abs(Math.sin(now*9))*-1.2:Math.sin(now*2)*.4)+nod,mood:'happy',expr,gaze,flip:J.face<0,blink:Math.sin(now*1.7)>.985,hat:!(evening()&&LIFE.plan==='sofa'&&LIFE.jill.act!=='wrap'&&LIFE.jill.after!=='wrap')});
  if(R&&R.closing!=null&&LIFE.jill.act==='wrap'&&!moving){const wx=J.x+9+Math.sin(now*5.5)*6,wy=J.y-19;c.fillStyle='#BFD9EC';c.save();c.translate(wx,wy);c.rotate(Math.sin(now*5.5)*.3);rr(c,-4,-2.2,8,4.4,1.4);c.fill();c.restore();c.fillStyle=JILL_LOOK.skin;circ(c,wx-2,wy-1,2.3)}
  if(pet&&pet.cat){const p=pet.cat;const hx=p.x+(p.x<J.x?6:-6),hy=p.y-(p.st==='sleep'?6:10);c.fillStyle=JILL_LOOK.skin;circ(c,hx,hy,2.6);c.fillStyle='rgba(60,34,22,.35)';c.beginPath();c.arc(hx,hy,2.6,0,7);c.stroke()}
  if(cooking){const f=J.face<0?-1:1;const a=Math.sin(now*9);c.save();c.translate(J.x+f*4,J.y-29+a*1.6);c.rotate(f*(-.55+a*.3));c.fillStyle='#D9D9DD';rr(c,-1.1,-8,2.4,9.5,1);c.fill();c.strokeStyle='rgba(60,34,22,.4)';c.lineWidth=.5;c.stroke();c.fillStyle='#4A3226';rr(c,-1.4,1.4,3,4.4,1.2);c.fill();c.restore()}
  J.carry.slice(0,3).forEach((cc,i)=>{const cv=dishCanvas(cc.it.d,cc.it.q,64,S.decor.ware>0,cc.it.want);c.drawImage(cv,J.x+(i%2?5:-21),J.y-50-Math.floor(i/2)*8,16,16)})}
function drawTableOverlay(c,t,now,pulse){const g=t.group;const bx=t.x,by=t.y-(t.seats===4?74:68);
   if(g&&!['toTable','leave'].includes(g.state)){let kind=null,extra=null;if(g.state==='reading')kind='menu';else if(g.state==='order')kind='order';else if(g.state==='wait'){const it=g.ticket?g.ticket.items:[];if(it.some(i=>i.st==='ready'&&!i.picked))kind='ready';else kind='wait',extra=[it.filter(i=>i.st==='served').length,it.length]}else if(g.state==='check')kind='check';
    const act=kind==='order'||kind==='ready'||kind==='check';if(act){c.strokeStyle=`rgba(255,215,110,${.35+pulse*.45})`;c.lineWidth=2;c.beginPath();c.ellipse(t.x,t.y-4,(t.seats===4?42:34)+pulse*3,15+pulse*1.5,0,0,7);c.stroke()}
    if(g.rowdy){kind='angry';c.save();c.translate(Math.sin(now*40)*1.2,0)}if(kind)bubble(c,bx,by,kind,g.rowdy?pulse:act?pulse:0,extra);if(g.rowdy)c.restore();if(['order','wait','check'].includes(g.state))patBar(c,bx,by+13,g.pat);if(g.ret||g.reg){c.fillStyle='#E8798A';c.beginPath();const hx=bx+15,hy=by-8;c.moveTo(hx,hy+4);c.bezierCurveTo(hx-6,hy,hx-3,hy-5,hx,hy-2);c.bezierCurveTo(hx+3,hy-5,hx+6,hy,hx,hy+4);c.fill()}
    if(g.type==='vip'){c.fillStyle='#E0B863';c.font=`800 7px ${FONT}`;c.textAlign='center';c.fillText('VIP',bx-17,by-6)}}
   else if(!g&&t.dirty){bubble(c,bx,by+8,'dirty',pulse);c.strokeStyle=`rgba(160,210,235,${.3+pulse*.4})`;c.lineWidth=2;c.beginPath();c.ellipse(t.x,t.y-4,34+pulse*3,15,0,0,7);c.stroke()}
   else if(!g&&!t.dirty&&queued().some(q=>q.size<=t.seats)){c.strokeStyle=`rgba(140,200,120,${.25+pulse*.35})`;c.lineWidth=1.6;c.setLineDash([4,4]);c.beginPath();c.ellipse(t.x,t.y-4,t.seats===4?42:32,14,0,0,7);c.stroke();c.setLineDash([])}}
/* the pass, seen from the dining room: the counter with today's ready plates (drawCounter) plus one status dot per
   station and the way to the kitchen. Tapping the counter goes to the kitchen. */
function drawPassStrip(c,now,V){const y=FB+22;const n=V.slots.length;if(!n)return;const x0=200-(n-1)*7;
 for(let i=0;i<n;i++){const s=V.slots[i];const j=s.job;const auto=j&&chefHandles(s);const u=j?urgency(j):-1;const col=s.broken?'#E0543A':!j?'rgba(60,56,50,.25)':auto?'#8FB07A':u>=3?'#E0543A':u===2?'#E6B04A':'#5E8FA8';c.fillStyle=col;circ(c,x0+i*14,y,3.2);if(j&&!auto&&u>=2){const p=(Math.sin(now*7)+1)/2;c.strokeStyle=`rgba(224,84,58,${.3+p*.5})`;c.lineWidth=1.2;c.beginPath();c.arc(x0+i*14,y,5.5,0,7);c.stroke()}}
 const busy=V.slots.filter(s0=>s0.job).length;c.fillStyle='rgba(60,56,50,.78)';c.font=`800 7px ${FONT}`;c.textAlign='center';c.fillText(busy?`廚房 › ${busy} 道在做`:'廚房 ›',200,y+16);
 const chefs=(S.crew||[]).filter(m=>m.role==='chef').length;if(chefs){c.fillStyle='rgba(60,56,50,.55)';c.font=`700 6px ${FONT}`;c.fillText(`${chefs} 位廚師在裡面`,200,y+25)}}
/* ================= 2.0: the kitchen, the side room and the street ================= */
const BGC={};   /* cached backgrounds of the other rooms, by room */
function roomBg(k,key,TOP,draw){const T2=Math.round(TOP);const kk=key+'|'+T2+'|'+SV.s+'|'+DPR+'|'+FB+'|'+DY;const hit=BGC[k];if(hit&&hit.key===kk)return hit.cv;for(const o in BGC)if(o!==k)delete BGC[o];   /* one room's background at a time: a phone's memory is finite */
 const sc0=SV.s*DPR;const XW=LW+BGM*2;const cv=mkCanvas(Math.ceil(XW*sc0),Math.ceil((LH+T2)*sc0));const c=cv.getContext('2d');c.scale(sc0,sc0);c.translate(BGM,T2);draw(c,-BGM,XW,T2);BGC[k]={key:kk,cv};return cv}
function blitBg(c,cv,X0,XW,TOP){const T2=Math.round(TOP);c.drawImage(cv,X0,-T2,XW,LH+T2)}
/* an open doorway in a back wall: dark inside, warm light, a wooden frame and a sign */
function drawArch(c,x,y,w,h,label){c.fillStyle='#8A6A42';rr(c,x-4,y-4,w+8,h+6,6);c.fill();c.fillStyle='#2A1C16';rr(c,x,y,w,h+2,5);c.fill();let g=c.createLinearGradient(0,y,0,y+h);g.addColorStop(0,'rgba(255,214,150,.08)');g.addColorStop(1,'rgba(255,214,150,.4)');c.fillStyle=g;rr(c,x,y,w,h+2,5);c.fill();
 c.fillStyle='rgba(255,230,180,.22)';c.fillRect(x+6,y+h-14,w-12,14);/* light spilling onto the floor, and a mat with the sign */let fg=c.createLinearGradient(0,y+h,0,y+h+26);fg.addColorStop(0,'rgba(255,214,150,.3)');fg.addColorStop(1,'rgba(255,214,150,0)');c.fillStyle=fg;c.fillRect(x-6,y+h,w+12,26);c.fillStyle='#8A3A2A';rr(c,x-2,y+h+8,w+4,12,3);c.fill();c.fillStyle='rgba(255,255,255,.12)';rr(c,x,y+h+9.5,w,3,1.5);c.fill();c.fillStyle='#F6EEDF';c.font=`800 6.5px ${FONT}`;c.textAlign='center';c.textBaseline='middle';c.fillText(label,x+w/2,y+h+14.4);c.textBaseline='alphabetic'}
function drawOtherRoom(c,now,dusk,V,X0,XW,TOP){const k=room;const J=V.jill;const list=[];
 if(k==='kitchen')drawKitchenRoom(c,now,dusk,V,X0,XW,TOP,list);else if(k==='side')drawSideRoom(c,now,dusk,V,X0,XW,TOP,list);else drawFrontRoom(c,now,dusk,V,X0,XW,TOP,list);
 for(const t of V.tables)if((t.room||'main')===k)list.push({y:t.y,f:()=>drawTableFull(c,t,now)});
 for(const g of V.groups)if(WALK_ST.includes(g.state)&&(g.room||'main')===k)list.push({y:g.y,f:()=>drawWalkers(c,g,now)});
 if(!J.sofa&&(J.room||'main')===k)list.push({y:J.y,f:()=>drawJillAt(c,J,V,now)});
 crewDraw(c,now,list,k);
 if(CATS)for(const cat of CATS){if(cat.away!==k)continue;list.push({y:cat.ay,f:()=>{const sx=cat.x,sy=cat.y,sf=cat.face;cat.x=cat.ax;cat.y=cat.ay;cat.face=cat.aface||1;drawCat(c,cat,now);cat.x=sx;cat.y=sy;cat.face=sf}})}
 for(const G of CATGEAR)if(gearOn(G.k)&&G.room===k&&G.poses)list.push({y:G.y+(G.k==='perch'?-30:G.k==='tunnel'?-8:-6),f:()=>drawGear(c,G,now)});
 if(k==='front'&&R){for(const w of STREET.ppl)list.push({y:w.y,f:()=>drawStreetWalker(c,w,now)});if(STREET.veh)list.push({y:STREET.veh.y,f:()=>drawVehicle(c,STREET.veh)})}
 list.sort((a,b)=>a.y-b.y).forEach(i=>i.f());
 /* the light of the hour, as in the dining room (the street bakes it into its sky) */
 if(k!=='front'){c.save();c.globalCompositeOperation='multiply';c.fillStyle=wxTint(tintFor(dusk));c.fillRect(X0,-TOP,XW,LH+TOP);c.restore();
  /* the room's own lamps come up with the evening */c.save();c.globalCompositeOperation='lighter';const lk=.1+clamp(dusk,0,1)*.22;const spots=k==='side'?[{x:104,y:40,r:90,k:1},{x:296,y:40,r:90,k:1},{x:200,y:150,r:130,k:.8}]:[{x:KX.range.x+KX.range.w/2,y:60,r:120,k:.9,col:'255,236,190'},{x:132,y:KY.rail+20,r:70,k:.9},{x:200,y:KY.rail+20,r:70,k:.9},{x:268,y:KY.rail+20,r:70,k:.9},{x:200,y:LH-60,r:90,k:.5}];
  for(const L0 of spots){let g=c.createRadialGradient(L0.x,L0.y,2,L0.x,L0.y+30,L0.r);g.addColorStop(0,`rgba(${L0.col||'255,196,120'},${lk*L0.k})`);g.addColorStop(1,'rgba(255,170,90,0)');c.fillStyle=g;c.fillRect(L0.x-L0.r,L0.y-L0.r,L0.r*2,L0.r*2.4)}
  if(k==='side')for(const t of V.tables){if(t.room!=='side')continue;let g=c.createRadialGradient(t.x,t.y-15,1,t.x,t.y-15,26);g.addColorStop(0,`rgba(255,190,100,${.1+dusk*.12})`);g.addColorStop(1,'rgba(255,190,100,0)');c.fillStyle=g;c.fillRect(t.x-26,t.y-41,52,52)}c.restore()}
 if(R){const pulse=(Math.sin(now*6)+1)/2;for(const t of R.tables)if((t.room||'main')===k)drawTableOverlay(c,t,now,pulse);
  const qs=(J.cur?[J.cur.t]:[]).concat(J.q);qs.forEach((ti,i)=>{const t=R.tables[ti];if((t.room||'main')!==k)return;c.fillStyle='#2E2019';circ(c,t.x+(t.seats===4?40:30),t.y-22,7);c.fillStyle='#E6C27A';c.font=`800 8px ${FONT}`;c.textAlign='center';c.textBaseline='middle';c.fillText(String(i+1),t.x+(t.seats===4?40:30),t.y-21.5)});
  for(const p of R.parts){if((p.room||'main')!==k)continue;const a=1-p.t/p.life;if(p.kind==='coin'){c.fillStyle=`rgba(244,196,78,${a})`;el(c,p.x,p.y,3,3.4);c.fillStyle=`rgba(142,100,34,${a})`;el(c,p.x,p.y,1.4,1.8)}else{c.fillStyle=`rgba(255,230,140,${a})`;c.save();c.translate(p.x,p.y);c.rotate(p.t*6);c.fillRect(-2.5,-.6,5,1.2);c.fillRect(-.6,-2.5,1.2,5);c.restore()}}
  for(const f of R.floats){if((f.room||'main')!==k)continue;const a=1-f.t/f.life;c.globalAlpha=Math.min(1,a*1.5);c.font=`800 ${f.big?12:9.5}px ${FONT}`;c.textAlign='center';c.textBaseline='middle';c.lineWidth=3;c.strokeStyle='rgba(30,20,15,.8)';c.strokeText(f.txt,f.x,f.y-f.t*22);c.fillStyle=f.col;c.fillText(f.txt,f.x,f.y-f.t*22);c.globalAlpha=1}
  if(R.blackout>0){R.blackout-=1/60;const a=R.blackout>2.2?.75:R.blackout>.5?.85:(R.blackout/.5)*.85;c.fillStyle=`rgba(8,6,12,${a})`;c.fillRect(X0,-TOP,XW,LH+TOP)}}
 let vg=c.createRadialGradient(206,290,210,206,290,400);vg.addColorStop(0,'rgba(0,0,0,0)');vg.addColorStop(1,'rgba(15,8,4,.3)');c.fillStyle=vg;c.fillRect(X0,-TOP,XW,LH+TOP)}
/* ================= 2.0: the kitchen — the line, the pass, the cooks =================
   One long counter along the back wall: the sink, the prep boards, the range with its burners, the oven under the counter,
   the coffee machine at the end. The pass runs across the middle under three heat lamps; plates land there and the front
   of house takes them from the other side. Below the pass is the pickup side with the door to the dining room. Every cook
   is an actor who walks the aisle between the line and the pass; the recipe decides where each step happens and the
   tray's own vessel renderer draws the food on the counter, so what is on the fire is the dish that was ordered. */
const KX_BASE={sink:{x:50,w:26},prep:{x:80,w:64},range:{x:148,w:128},oven:{x:280,w:44},bar:{x:328,w:34}},KX_BIG={sink:{x:36,w:22},prep:{x:62,w:60},range:{x:126,w:160},oven:{x:290,w:44},bar:{x:338,w:34}};
const KX={get sink(){return(projOn('kext')?KX_BIG:KX_BASE).sink},get prep(){return(projOn('kext')?KX_BIG:KX_BASE).prep},get range(){return(projOn('kext')?KX_BIG:KX_BASE).range},get oven(){return(projOn('kext')?KX_BIG:KX_BASE).oven},get bar(){return(projOn('kext')?KX_BIG:KX_BASE).bar}};   /* the six-burner range of the expansion takes the line's middle */
const KY={top:130,h:70,face:20,feet:146,passTop:276,passH:40,passFace:12,passFeet:272,front:362,rail:236};
/* where a slot's vessel normally sits and where its cook stands */
function slotHome(s){const i=s.no-1;switch(s.type){
 case'stove':{const cols=projOn('kext')?3:2;const col=i%cols;const x=KX.range.x+(cols===3?[30,80,130][col]:[32,96][col]);return{x,y:i<cols?186:160,sc:.62,cx:x,place:'range'}}
 case'oven':return{x:KX.oven.x+22,y:170,sc:.36,cx:KX.oven.x+22,place:'oven'};
 case'bar':return{x:KX.bar.x+(i?25:9),y:192,sc:.32,cx:KX.bar.x+17,place:'bar'};
 default:{const x=KX.prep.x+(i?50:20);return{x,y:172,sc:.36,cx:x,place:'prep'}}}}
/* where the current step of a job happens: the board for knife work, the sink to drain, the oven while it bakes,
   the pass once an oven dish is out (and for the plating of every chef's dish) */
function stepSpot(s){const j=s.job;const h=slotHome(s);const out=Object.assign({cy:KY.feet},h);if(!j)return out;
 if(j.plating){const x=j.plating.x||200;return Object.assign(out,{place:'pass',cx:x,cy:KY.passFeet,x,y:KY.passTop+22,sc:.5})}
 const k=j.step;if(!k)return out;const v=k.verb||'';
 if(k.t==='work'&&k.board){const x=s.type==='prep'?h.x:KX.prep.x+35;return Object.assign(out,{place:'prep',x,y:172,cx:x,sc:.4,board:true})}
 if(k.t==='add'&&/瀝乾/.test(v)){const x=KX.sink.x+13;return Object.assign(out,{place:'sink',x,y:158,cx:x,sc:.5})}
 if(s.type==='oven'){const steps=recipeOf(j.d);const zi=steps.findIndex(q=>q.t==='zone');
  if(k.t==='zone')return Object.assign(out,{inOven:true,x:KX.oven.x+(s.no>1?34:12),y:KY.top+KY.h+10,sc:.17,cx:KX.oven.x+22});
  if(zi>=0&&j.si>zi)return Object.assign(out,{place:'pass',cx:200,cy:KY.passFeet,x:200,y:KY.passTop+22,sc:.5})}
 return out}
function platingSpot(){const used=R.slots.filter(s=>s.job&&s.job.plating&&s.job.plating.x).map(s=>s.job.plating.x);return[200,148,252,174,226,122,278].find(x=>!used.includes(x))||200}
function jobChef(s){return s.job?chefHandles(s):null}
/* handwork waits for the cook to be at that spot (the fire does not) */
function cookPresent(s){const id=s.cook;if(!id)return true;const a=R.ck&&R.ck[id];if(!a)return true;const b=a.beat;return !!b&&b.s===s&&!a.moving}
function homeSpot(m,i){const z=m.duty==='oven'?KX.oven:m.duty==='bar'?KX.bar:m.duty==='prep'?KX.prep:KX.range;const off=m.duty==='oven'?-8:m.duty==='bar'?10:0;return{x:z.x+z.w/2+off+(i%2?14:-14),y:KY.feet}}
function chefBeat(m,a,i){const mine=R.slots.filter(s=>s.job&&s.cook===m.id);
 let s=mine.find(s=>s.job.plating);if(s)return{kind:'plate',s,x:s.job.plating.x||200,y:KY.passFeet};
 const hands=mine.filter(s=>{const k=s.job.step;return k&&['add','hold','dose','tap','work'].includes(k.t)}).sort((p,q)=>p.job.t0-q.job.t0);
 if(hands.length){const sp=stepSpot(hands[0]);return{kind:hands[0].job.step.t,s:hands[0],x:sp.cx,y:sp.cy,sp}}
 const zones=mine.filter(s=>s.job.step&&s.job.step.t==='zone').sort((p,q)=>(p.job.step.z.c-p.job.step.p)-(q.job.step.z.c-q.job.step.p));
 if(zones.length){const sp=stepSpot(zones[0]);return{kind:'watch',s:zones[0],x:sp.cx,y:sp.cy,sp}}
 if(mine.length){const sp=stepSpot(mine[0]);const k=mine[0].job.step;return{kind:k&&k.anim==='stir'?'stir':'watch',s:mine[0],x:sp.cx,y:sp.cy,sp}}
 const h=homeSpot(m,i);return{kind:'idle',x:h.x,y:h.y}}
/* the cooks' positions and the plating at the pass; runs every frame of a service, whichever room is on screen */
function kitchenUpd(dt){if(!R)return;R.ck=R.ck||{};
 for(const s of R.slots){const m=jobChef(s);s.cook=m?m.id:null;if(s.job&&s.job.plating&&!s.job.plating.x)s.job.plating.x=platingSpot()}
 let i=0;for(const m of S.crew||[]){if(m.role!=='chef')continue;let a=R.ck[m.id];if(!a){const h=homeSpot(m,i);a=R.ck[m.id]={x:h.x,y:h.y,face:1,step:0,moving:false}}
  const b=a.beat=chefBeat(m,a,i);i++;const v=(200+16*m.lv)*flowMul('crew')*dt;const dx=b.x-a.x,dy=b.y-a.y,d=Math.hypot(dx,dy);
  if(d>v){a.x+=dx/d*v;a.y+=dy/d*v;a.moving=true;a.step+=dt*13;if(Math.abs(dx)>.5)a.face=dx>0?1:-1;a.idle=null}else{a.x=b.x;a.y=b.y;a.moving=false;a.face=a.idle==='chat'&&a.chatFace?a.chatFace:1}
  cookIdleTick(m,a,b,dt);
  if(b.kind==='plate'&&!a.moving){const j=b.s.job;j.plating.t+=dt;if(j.plating.t>=j.plating.dur)finishJob(b.s)}}}
/* 2.1: what a cook does with a quiet minute — wipes the counter, drinks some water, tastes the sauce, reads the rail,
   or turns to the cook next to him for a word. Nothing to manage; it is there when you look. */
function cookIdleTick(m,a,b,dt){if(b.kind!=='idle'||a.moving){a.idle=null;a.idleLeft=0;return}
 if(a.idle){a.idleLeft-=dt;if(a.idleLeft<=0){if(a.idle==='chat'&&a.chatWith){const o=R.ck[a.chatWith];if(o&&o.idle==='chat')o.idle=null}a.idle=null;a.chatWith=null}return}
 a.idleNext=(a.idleNext==null?rand(2,6):a.idleNext)-dt;if(a.idleNext>0)return;a.idleNext=rand(6,14);
 const others=Object.keys(R.ck).filter(id=>id!==m.id&&R.ck[id].beat&&R.ck[id].beat.kind==='idle'&&!R.ck[id].moving&&!R.ck[id].idle&&Math.abs(R.ck[id].x-a.x)<110&&Math.abs(R.ck[id].y-a.y)<30);
 const k=pick(others.length?['wipe','sip','taste','rail','chat','chat']:['wipe','wipe','sip','taste','rail']);a.idle=k;a.idleLeft=k==='chat'?rand(3,5):k==='wipe'?rand(2.5,4):rand(1.6,2.6);
 if(k==='chat'){const oid=pick(others),o=R.ck[oid];a.chatWith=oid;o.idle='chat';o.idleLeft=a.idleLeft;o.chatWith=m.id;a.chatFace=o.x>a.x?1:-1;o.chatFace=-a.chatFace;a.face=a.chatFace;o.face=o.chatFace;a.talker=1;o.talker=0}}
/* 2.1: the pickup side is furnished when the screen is tall enough to leave floor there — wire shelving with the plates,
   the jars and the dry goods on the left, a work table with the dish rack and the glasses by the fridge, the mop and
   bucket by the door. Cached with the room. */
function drawKitchenFill(b,LHk){
 {const top=KY.passTop+124,bot=LHk-70;if(bot-top>=60){const x=16,w=62,h=Math.min(124,bot-top),y=bot-h;b.fillStyle='rgba(0,0,0,.14)';el(b,x+w/2,y+h+2,w*.55,5);
  const tiers=h>=104?3:2,th=h/tiers;b.fillStyle='#7C838A';for(const px of[x,x+w-3])b.fillRect(px,y-4,3,h+6);
  for(let t=0;t<=tiers;t++){const ty=y+t*th;b.fillStyle='#9AA0A6';b.fillRect(x,ty,w,3);b.fillStyle='rgba(255,255,255,.35)';b.fillRect(x,ty,w,1)}
  const stack=(sx,sy,n,rw,col)=>{for(let i=0;i<n;i++){b.fillStyle=col||'#F6F1E6';el(b,sx,sy-i*2.2,rw,2.6);b.fillStyle='rgba(0,0,0,.08)';el(b,sx,sy-i*2.2+.6,rw*.8,1.2)}};
  stack(x+14,y+th-5,6,9);stack(x+34,y+th-5,4,7);stack(x+50,y+th-5,5,5,'#E8E2D6');
  const jy=y+th*(tiers-1);for(const [jx,col] of[[x+10,'#D9A45A'],[x+22,'#8A3A2A'],[x+34,'#5E9E3D']]){b.fillStyle='rgba(255,255,255,.6)';rr(b,jx-5,jy-16,10,14,2);b.fill();b.fillStyle=col;rr(b,jx-4,jy-11,8,8,1.5);b.fill();b.fillStyle='#3A2A22';rr(b,jx-5,jy-18,10,3,1);b.fill()}
  b.fillStyle='#C9A063';rr(b,x+42,jy-15,18,13,1.5);b.fill();b.fillStyle='rgba(0,0,0,.15)';b.fillRect(x+42,jy-9,18,1.2);
  b.fillStyle='#EBE1CC';rr(b,x+6,y+h-21,22,18,5);b.fill();b.fillStyle='#8A6A42';b.fillRect(x+9,y+h-19,16,2);b.fillStyle='#B8536A';b.font=`800 6px ${FONT}`;b.textAlign='center';b.fillText('米',x+17,y+h-8);
  b.fillStyle='#C9A063';rr(b,x+34,y+h-18,24,15,1.5);b.fill();b.fillStyle='rgba(0,0,0,.15)';b.fillRect(x+34,y+h-11,24,1.2);b.fillStyle='#2E2019';b.font=`800 4.5px ${FONT}`;b.fillText('FRAGILE',x+46,y+h-6)}}
 {const x=254,w=58,y=LHk-150;if(y>=KY.passTop+118){b.fillStyle='rgba(0,0,0,.14)';el(b,x+w/2,y+40,w*.55,5);b.fillStyle='#7C838A';b.fillRect(x+3,y+10,3,28);b.fillRect(x+w-6,y+10,3,28);b.fillStyle='#9AA0A6';b.fillRect(x+3,y+24,w-6,2);
  let g=b.createLinearGradient(0,y,0,y+12);g.addColorStop(0,'#D5DADE');g.addColorStop(1,'#A9B0B6');b.fillStyle=g;rr(b,x,y,w,12,2);b.fill();b.fillStyle='rgba(255,255,255,.5)';b.fillRect(x+2,y+1,w-4,1.2);
  b.fillStyle='#8A9096';b.fillRect(x+6,y-11,30,2);for(let i=0;i<6;i++){b.fillStyle='#F6F1E6';rr(b,x+8+i*4.6,y-20,2.6,11,1.2);b.fill();b.fillStyle='rgba(0,0,0,.06)';b.fillRect(x+9.6+i*4.6,y-18,.8,8)}b.fillStyle='#8A9096';b.fillRect(x+6,y-1,30,1.5);
  for(let i=0;i<3;i++){b.fillStyle='rgba(200,220,235,.75)';rr(b,x+39+i*5.8,y-10,4.2,10,1);b.fill();b.fillStyle='rgba(255,255,255,.7)';b.fillRect(x+40+i*5.8,y-9,1,8)}
  b.fillStyle='#B8536A';rr(b,x+w-15,y+7,9,13,1.5);b.fill();b.fillStyle='rgba(255,255,255,.25)';b.fillRect(x+w-15,y+11,9,1.2);b.fillRect(x+w-15,y+15,9,1.2)}}
 {const x=118,y=LHk-12;if(LHk>=520){b.fillStyle='rgba(0,0,0,.14)';el(b,x,y+2,12,3.5);b.fillStyle='#E0A43A';b.beginPath();b.moveTo(x-9,y-15);b.lineTo(x+9,y-15);b.lineTo(x+7,y);b.lineTo(x-7,y);b.closePath();b.fill();b.fillStyle='rgba(0,0,0,.14)';b.fillRect(x-9,y-15,18,2.2);b.fillStyle='rgba(255,255,255,.2)';b.fillRect(x-6,y-11,2,9);
  b.strokeStyle='#8A6A42';b.lineWidth=2.2;b.lineCap='round';b.beginPath();b.moveTo(x+3,y-12);b.lineTo(x+11,y-54);b.stroke();b.fillStyle='#D5DADE';for(let i=0;i<6;i++){b.fillRect(x-3+i*2.2,y-18,1.3,9)}b.fillStyle='#2E2019';b.fillRect(x-4,y-19,14,2)}}}
function hitStation(p){if(!R||room!=='kitchen')return -1;let best=-1,bd=1e9;
 for(let i=0;i<R.slots.length;i++){const s=R.slots[i];const spots=[slotHome(s)];if(s.job)spots.push(stepSpot(s));
  for(const sp of spots){if(sp.place==='pass')continue;const d=Math.hypot(p.x-sp.x,(p.y-(sp.y-8))*1.4);if(d<26&&d<bd){bd=d;best=i}}
  if(s.type==='oven'){const dx=KX.oven.x+2+(s.no-1)*22;if(p.x>=dx-2&&p.x<=dx+22&&p.y>=KY.top+KY.h-2&&p.y<=KY.top+KY.h+KY.face+2)return i}}
 return best}
/* ---- drawing ---- */
function drawKitchenRoom(c,now,dusk,V,X0,XW,TOP,list){const E=S.eq;const LHk=LH;
 const bg=roomBg('kitchen',S.level+'|'+(S.theme||'')+'|'+E.stove+E.oven+E.bar+E.prep+E.fridge+'|'+JSON.stringify(S.rooms||{}),TOP,(b,X0,XW,T2)=>{const r=rng(31);
  /* cream subway tiles, a sage band behind the line */b.fillStyle='#D8D2C4';b.fillRect(X0,-T2,XW,92+T2);for(let y=-T2-(T2%12)-12,k=0;y<64;y+=12,k++){const off=k%2?13:0;for(let x=X0-13+off;x<LW+BGM;x+=26){b.fillStyle=r()<.08?'#E6E0D2':'#EDE8DC';rr(b,x+.6,y+.6,24.8,10.8,1.2);b.fill()}}
  for(let y=64;y<92;y+=7)for(let x=X0;x<LW+BGM;x+=7){b.fillStyle=(Math.floor((x-X0)/7)+Math.floor((y-64)/7))%2?'#A3B9A6':'#95AB99';b.fillRect(x+.4,y+.4,6.2,6.2)}b.fillStyle='rgba(0,0,0,.08)';b.fillRect(X0,63,XW,1.2);
  /* the hood over the range */{const ht=Math.max(-T2+4,-26);let g=b.createLinearGradient(0,ht,0,40);g.addColorStop(0,'#6E767A');g.addColorStop(1,'#4E5559');b.fillStyle=g;b.beginPath();b.moveTo(KX.range.x+6,ht);b.lineTo(KX.range.x+KX.range.w-6,ht);b.lineTo(KX.range.x+KX.range.w+6,40);b.lineTo(KX.range.x-6,40);b.closePath();b.fill();b.fillStyle='#8A9498';b.fillRect(KX.range.x-6,40,KX.range.w+12,4);b.fillStyle='rgba(255,236,190,.9)';for(const x of[KX.range.x+22,KX.range.x+52,KX.range.x+82])el(b,x,45,8,1.8);let lg=b.createLinearGradient(0,46,0,92);lg.addColorStop(0,'rgba(255,230,170,.28)');lg.addColorStop(1,'rgba(255,230,170,0)');b.fillStyle=lg;b.fillRect(KX.range.x-4,46,KX.range.w+8,46)}
  /* the pan rail over the prep boards, shelves with containers over the coffee machine, a clock, the window over the sink */
  b.fillStyle='#3A3A3A';b.fillRect(KX.prep.x+4,22,KX.prep.w-8,2.4);for(let i=0;i<3;i++){const x=KX.prep.x+18+i*22;b.fillStyle='#2A2A2A';b.fillRect(x-.8,24,1.6,6);b.fillStyle=i===1?'#B87333':'#3C3C3C';circ(b,x,38,7.5);b.fillStyle=i===1?'#D08A48':'#585858';circ(b,x,38,5.5);b.fillStyle='#2A2A2A';b.fillRect(x-1,29,2,5)}
  for(const y of[30,54]){b.fillStyle='#8A6A42';b.fillRect(KX.oven.x+4,y,88,3);b.fillStyle='rgba(0,0,0,.1)';b.fillRect(KX.oven.x+4,y+3,88,1.5);for(let i=0;i<6;i++){const x=KX.oven.x+8+i*14;b.fillStyle=['#D8B25A','#C86A3A','#7FA36A','#E8D4B0','#B8536A','#F4F1EA'][(i+(y>40?2:0))%6];rr(b,x,y-10,10,10,1.5);b.fill();b.fillStyle='rgba(255,255,255,.35)';b.fillRect(x+1.2,y-9,2,7);b.fillStyle='#2A2A2A';b.fillRect(x,y-12,10,2.2)}}
  b.fillStyle='#F4F1EA';circ(b,KX.sink.x+17,36,9);b.strokeStyle='#2A2A2A';b.lineWidth=1.2;b.beginPath();b.arc(KX.sink.x+17,36,9,0,7);b.stroke();b.beginPath();b.moveTo(KX.sink.x+17,36);b.lineTo(KX.sink.x+17,30);b.moveTo(KX.sink.x+17,36);b.lineTo(KX.sink.x+21,38);b.stroke();
  /* the floor: terracotta tiles */b.fillStyle='#C2946C';b.fillRect(X0,92,XW,LHk-92);for(let y=92;y<LHk;y+=22)for(let x=X0;x<LW+BGM;x+=22){const k=(Math.floor((x-X0)/22)+Math.floor((y-92)/22))%2;b.fillStyle=k?'#CB9C74':'#BE8E66';b.fillRect(x+.7,y+.7,20.6,20.6);if(r()<.25){b.fillStyle='rgba(255,255,255,.07)';el(b,x+11,y+11,6,3)}}
  let g0=b.createLinearGradient(0,92,0,LHk);g0.addColorStop(0,'rgba(60,40,30,.22)');g0.addColorStop(.1,'rgba(60,40,30,0)');g0.addColorStop(1,'rgba(60,40,30,.18)');b.fillStyle=g0;b.fillRect(X0,92,XW,LHk-92);
  /* the pickup side: a rubber mat in front of the pass, crates, a bin, the way to the dining room */b.fillStyle='rgba(40,30,25,.18)';rr(b,84,KY.passTop+KY.passH+KY.passFace+8,232,26,3);b.fill();
  for(const [cx,cy] of[[70,KY.passTop+70],[70,KY.passTop+100]]){b.fillStyle='rgba(0,0,0,.14)';el(b,cx,cy+14,26,5);b.fillStyle='#B8905E';rr(b,cx-22,cy-8,44,22,2);b.fill();b.fillStyle='#8A6A42';b.fillRect(cx-22,cy-1,44,2);b.fillRect(cx-22,cy+7,44,2);b.fillStyle=cy<KY.passTop+90?'#F0932B':'#5E9E3D';for(let k=0;k<6;k++)circ(b,cx-15+k*6,cy-10+(k%2),3.4)}
  b.fillStyle='rgba(0,0,0,.14)';el(b,332,KY.passTop+108,13,4);b.fillStyle='#4A4A4E';rr(b,320,KY.passTop+72,24,34,3);b.fill();b.fillStyle='#5A5A60';rr(b,318,KY.passTop+68,28,6,2);b.fill();
  drawKitchenFill(b,LHk);
  /* the door to the dining room, bottom centre */{const dx=200,dy=LHk-2;b.fillStyle='#3A2A22';b.fillRect(dx-38,dy-62,76,62);for(const sx of[dx-34,dx+2]){b.fillStyle='#8A6A42';b.fillRect(sx,dy-58,32,58);b.fillStyle='rgba(255,230,180,.5)';circ(b,sx+16,dy-40,7);b.fillStyle='#C9CDD0';b.fillRect(sx+(sx<dx?24:4),dy-26,4,10)}b.fillStyle='rgba(255,214,150,.18)';b.fillRect(dx-38,dy-62,76,62);
   b.fillStyle='#F6EEDF';rr(b,dx-26,dy-14,52,11,2);b.fill();b.fillStyle='#2E2019';b.font=`800 6.5px ${FONT}`;b.textAlign='center';b.textBaseline='middle';b.fillText('‹ 用餐區',dx,dy-8.4);b.textBaseline='alphabetic'}});
 blitBg(c,bg,X0,XW,TOP);
 /* the line, the lamps, the pass, the fridge and the cold room; the cooks; Jill and the waiters on the pickup side */
 list.push({y:KY.top+KY.h+KY.face+1,f:()=>drawLine(c,now,V)});
 list.push({y:KY.rail+23,f:()=>drawHeatLamps(c,now)});
 list.push({y:KY.passTop+KY.passH+KY.passFace+1,f:()=>drawPass(c,now,V)});
 {const {x,y,w,h}=KR.fridge;list.push({y:y+h,f:()=>drawKFridge(c,now,x,y,w,h)});if(S.rooms&&S.rooms.cooler){const k=KR.cooler;list.push({y:k.y+k.h,f:()=>drawCooler(c,now,k)})}}
 if(R&&R.ck)for(const m of S.crew||[]){if(m.role!=='chef')continue;const a=R.ck[m.id];if(!a)continue;list.push({y:a.y,f:()=>drawCook(c,m,a,now)})}
 else{/* before and after service the cooks are at their places, wiping down */let i=0;for(const m of S.crew||[]){if(m.role!=='chef')continue;const h=homeSpot(m,i++);const a={x:h.x,y:h.y,face:1,step:0,moving:false,beat:{kind:'idle',x:h.x,y:h.y}};list.push({y:a.y,f:()=>drawCook(c,m,a,now)})}}
 const J=V.jill;if(R&&(J.room||'main')==='main'&&Math.hypot(J.x-PASS.x,J.y-PASS.y)<30){
  const ms=R.slots.find(s0=>s0.job&&!s0.cook&&s0.job.step&&s0.job.step.t!=='wait');
  if(ms){const sp=stepSpot(ms);const k=ms.job.step;list.push({y:sp.cy,f:()=>{const bob=Math.abs(Math.sin(now*9))*-1.2;drawPerson(c,sp.cx,sp.cy,JILL_LOOK,{jill:true,me:true,tall:true,s:1.1,mood:'happy',expr:'focus',bob,blink:Math.sin(now*1.7)>.985,hat:true});if(k.t==='work'&&k.board)drawHandKnife(c,sp.cx,sp.cy,1,now);nameTag(c,sp.cx,sp.cy-68,'Jill')}})}
  else list.push({y:KY.front,f:()=>{drawPerson(c,200,KY.front,JILL_LOOK,{jill:true,me:true,tall:true,s:1.1,mood:'happy',expr:'smile',bob:Math.sin(now*2)*.4,blink:Math.sin(now*1.7)>.985,hat:true});nameTag(c,200,KY.front-68,'Jill')}})}
 if(R&&R.cw)for(const m of S.crew||[]){if(m.role==='chef')continue;const w=R.cw[m.id];if(!w||(w.room||'main')!=='main'||Math.hypot(w.x-PASS.x,w.y-PASS.y)>40)continue;const x=clamp(w.x,120,280);
  list.push({y:KY.front+4,f:()=>{drawPerson(c,x,KY.front+4,crewLook(m),{s:1,mood:'happy',expr:'smile',bob:Math.sin(now*2+x)*.4,blink:Math.sin(now*1.5+x)>.97});if(w.carry)w.carry.slice(0,3).forEach((it,i)=>{c.drawImage(dishCanvas(it.d,it.q,64,S.decor.ware>0,it.want),x+(i%2?4:-20),KY.front-46-Math.floor(i/2)*8,16,16)});nameTag(c,x,KY.front-52,m.name)}})}
 if(S.decor.plants)list.push({y:112,f:()=>drawPlant(c,KX.bar.x+KX.bar.w+10,110,'bush')})}
/* the line itself: counter top and cabinet face, then each zone's equipment, then the vessels with the food in them */
function drawLine(c,now,V){const E=S.eq;const x0=KX.sink.x-4,x1=KX.bar.x+KX.bar.w+4,y=KY.top,h=KY.h,f=KY.face;
 c.fillStyle='rgba(0,0,0,.18)';rr(c,x0+2,y+5,x1-x0,h+f+6,4);c.fill();
 let g=c.createLinearGradient(0,y,0,y+h);g.addColorStop(0,'#D9B98F');g.addColorStop(1,'#C69C70');c.fillStyle=g;rr(c,x0,y,x1-x0,h,4);c.fill();c.fillStyle='rgba(255,255,255,.35)';rr(c,x0+2,y+1.5,x1-x0-4,3,1.5);c.fill();
 const r=rng(17);c.strokeStyle='rgba(120,80,40,.22)';c.lineWidth=.6;for(let yy=y+10;yy<y+h-4;yy+=7){c.beginPath();c.moveTo(x0+4,yy);c.lineTo(x1-4,yy+(r()-.5)*1.5);c.stroke()}
 /* the face: cream doors and drawers */c.fillStyle='#A47B54';rr(c,x0,y+h-2,x1-x0,f+2,2);c.fill();for(let dx=x0+6;dx<x1-30;dx+=34){if(dx>KX.range.x-8&&dx<KX.range.x+KX.range.w)continue;if(dx>KX.oven.x-8&&dx<KX.oven.x+KX.oven.w-4&&E.oven)continue;c.fillStyle='#EDE6D8';rr(c,dx,y+h+2,30,f-6,1.5);c.fill();c.fillStyle='#8A6A42';c.fillRect(dx+13,y+h+f/2-1,4,1.6)}
 c.fillStyle='rgba(0,0,0,.2)';c.fillRect(x0,y+h+f-2,x1-x0,3);
 /* the sink */{const x=KX.sink.x;c.fillStyle='#8E979B';rr(c,x+1,y+16,24,30,4);c.fill();c.fillStyle='#6F7A7E';rr(c,x+3,y+19,20,24,3);c.fill();c.fillStyle='#A8B3B8';rr(c,x+4,y+20,18,5,2);c.fill();c.strokeStyle='#C9D0D3';c.lineWidth=2.2;c.lineCap='round';c.beginPath();c.moveTo(x+13,y+16);c.lineTo(x+13,y+6);c.quadraticCurveTo(x+13,y,x+19,y+1);c.stroke();c.fillStyle='#C9D0D3';circ(c,x+19,y+2,1.6);
  const drain=R&&R.slots.some(s0=>s0.job&&stepSpot(s0).place==='sink');if(drain){c.strokeStyle='rgba(170,215,240,.9)';c.lineWidth=1.5;c.beginPath();c.moveTo(x+19,y+3);c.lineTo(x+19,y+26);c.stroke();c.fillStyle='rgba(255,255,255,.9)';for(let i=0;i<6;i++){const ph=(now*1.4+i*.17)%1;circ(c,x+6+(i*5)%16,y+30-ph*10,1.2+ph)}}
  /* the dish rack */c.fillStyle='#4A4A4E';c.fillRect(x-1,y+50,3,10);c.fillRect(x+22,y+50,3,10);c.fillStyle='#E8E4DC';for(let i=0;i<3;i++){el(c,x+6+i*6.5,y+56,3.6,7)}}
 /* prep: boards, a knife, greens, salt; a bread basket while there is no cold station yet */{const x=KX.prep.x;const boards=E.prep?(E.fridge>=3?2:1):0;for(let i=0;i<boards;i++){const bx=x+(i?50:20);c.fillStyle='rgba(0,0,0,.14)';el(c,bx+1,y+50,20,4);c.fillStyle='#C8965E';rr(c,bx-19,y+34,38,14,3);c.fill();c.fillStyle='#9A6534';c.fillRect(bx-19,y+46,38,2)}
  if(!E.prep){c.fillStyle='rgba(0,0,0,.12)';el(c,x+32,y+48,18,4);c.fillStyle='#B8905E';c.beginPath();c.moveTo(x+14,y+32);c.lineTo(x+50,y+32);c.lineTo(x+46,y+46);c.lineTo(x+18,y+46);c.closePath();c.fill();c.fillStyle='#D9A066';for(let k=0;k<3;k++)el(c,x+22+k*10,y+31,6,4);c.fillStyle='#F0C892';for(let k=0;k<3;k++)el(c,x+22+k*10,y+30,4,2)}
  c.fillStyle='#F4F1EA';rr(c,x+4,y+8,8,10,2);c.fill();c.fillStyle='#2A2A2A';c.fillRect(x+4,y+6,8,2.5);c.fillStyle='#E8E4DC';el(c,x+54,y+14,7,4);c.fillStyle='#5E9E3D';for(let k=0;k<4;k++)el(c,x+50+k*3,y+11-(k%2)*2,3,2);
  c.save();c.translate(x+32,y+14);c.rotate(-.3);let kg=c.createLinearGradient(0,-3,0,3);kg.addColorStop(0,'#F4F6F7');kg.addColorStop(1,'#9AA4A8');c.fillStyle=kg;c.beginPath();c.moveTo(-9,2);c.lineTo(8,2);c.lineTo(8,-1.5);c.quadraticCurveTo(-3,-5,-9,2);c.fill();c.fillStyle='#3A2A20';rr(c,8,-1.6,8,3.4,1.5);c.fill();c.restore();
  /* the lowboy fridge in the face */c.fillStyle='#C9CDD0';rr(c,x+2,y+h+2,KX.prep.w-4,f-6,1.5);c.fill();c.fillStyle='#9AA3A6';c.fillRect(x+KX.prep.w/2-1,y+h+3,2,f-8);c.fillRect(x+8,y+h+f/2-1,8,1.6);c.fillRect(x+KX.prep.w-16,y+h+f/2-1,8,1.6)}
 /* the range: steel frame, black top, knobs on the face, burners lit while something is on them */{const x=KX.range.x,w=KX.range.w;c.fillStyle='#9AA3A6';rr(c,x-2,y,w+4,h,3);c.fill();c.fillStyle='#2E3134';rr(c,x,y+2,w,h-4,3);c.fill();c.fillStyle='#3A3E41';rr(c,x+2,y+4,w-4,h-8,2);c.fill();c.fillStyle='rgba(255,255,255,.08)';c.fillRect(x+4,y+6,w-8,2);let rg=c.createLinearGradient(0,y,0,y+h);rg.addColorStop(0,'rgba(255,230,170,.16)');rg.addColorStop(1,'rgba(255,230,170,0)');c.fillStyle=rg;rr(c,x+2,y+4,w-4,h-8,2);c.fill();
  c.fillStyle='#2A2C2E';rr(c,x,y+h,w,f-2,1.5);c.fill();const nk=projOn('kext')?6:4;for(let k=0;k<nk;k++){c.fillStyle='#8A9498';circ(c,x+22+k*(nk===6?22:28),y+h+f/2,3.2);c.fillStyle='#2A2C2E';c.fillRect(x+21.4+k*(nk===6?22:28),y+h+f/2-3,1.2,3)}c.fillStyle='#8A9498';c.fillRect(x+w-14,y+h+3,8,f-8);
  const n=stoveSlots(E.stove);for(let i=0;i<n;i++){const s0=V.slots.find(q=>q.type==='stove'&&q.no===i+1);const hm=slotHome(s0||{type:'stove',no:i+1});const lit=!!(s0&&s0.job&&stepSpot(s0).place==='range');drawBurner(c,hm.x,hm.y+8,.62,lit,now)}}
 /* the oven under the counter: door(s) with a window, warm when something bakes; a fruit bowl on the counter until there is one */{const x=KX.oven.x;if(E.oven){const doors=E.oven>=3?2:1;for(let i=0;i<doors;i++){const dx=x+2+i*22;const s0=V.slots.find(q=>q.type==='oven'&&q.no===i+1);const on=!!(s0&&s0.job&&stepSpot(s0).inOven);c.fillStyle='#34302D';rr(c,dx,y+h+1,20,f-4,2);c.fill();let og=c.createLinearGradient(0,y+h,0,y+h+f);og.addColorStop(0,on?'#5A2E18':'#262220');og.addColorStop(1,on?'#8A4418':'#1E1A18');c.fillStyle=og;rr(c,dx+2.5,y+h+4,15,f-9,1.5);c.fill();if(on){c.fillStyle=`rgba(255,${Math.round(150+Math.sin(now*4)*30)},60,.35)`;rr(c,dx+2.5,y+h+4,15,f-9,1.5);c.fill()}c.fillStyle='#9AA3A6';c.fillRect(dx+3,y+h+2,14,1.6)}
   if(doors===1){c.fillStyle='#2A2C2E';rr(c,x+24,y+h+1,18,f-4,2);c.fill();c.fillStyle='#8A9498';c.fillRect(x+28,y+h+f/2-1,10,1.6)}
   /* the landing on top: a trivet */c.fillStyle='rgba(0,0,0,.12)';el(c,x+22,y+44,19,5);c.strokeStyle='#4A4A4E';c.lineWidth=1.2;c.beginPath();c.ellipse(x+22,y+42,16,4.6,0,0,7);c.stroke()}
  else{c.fillStyle='rgba(0,0,0,.12)';el(c,x+22,y+46,16,4);c.fillStyle='#F4F1EA';c.beginPath();c.moveTo(x+6,y+34);c.quadraticCurveTo(x+8,y+46,x+22,y+46);c.quadraticCurveTo(x+36,y+46,x+38,y+34);c.fill();for(const [ox,oy,col] of[[-7,-2,'#F0932B'],[0,-5,'#F0932B'],[7,-2,'#D8392A'],[-3,-8,'#F4C44E']]){c.fillStyle=col;circ(c,x+22+ox,y+34+oy,4.2)}}}
 /* the coffee machine, or a kettle and mugs until there is one */{const x=KX.bar.x;if(E.bar)drawEspresso(c,x+1,y+10,32,E.bar>=3?44:40,now);else{c.fillStyle='rgba(0,0,0,.12)';el(c,x+12,y+46,10,3);c.fillStyle='#B8536A';rr(c,x+4,y+30,16,16,4);c.fill();c.fillStyle='#8A3A4A';c.fillRect(x+4,y+30,16,2.5);c.strokeStyle='#B8536A';c.lineWidth=2;c.beginPath();c.arc(x+22,y+37,4,-1.3,1.3);c.stroke();c.fillStyle='#2A2A2A';c.fillRect(x+10,y+27,4,3);for(const [mx,col] of[[x+27,'#5E8FA8'],[x+30,'#E6C27A']]){c.fillStyle=col;rr(c,mx,y+38,6,8,1.5);c.fill()}}}
 /* what is cooking: every job's vessel where its step happens (a pan left on the fire stays there, empty) */
 const vs=[];for(const s0 of V.slots){if(!s0.job||s0.job.plating)continue;const sp=stepSpot(s0);if(sp.place==='pass')continue;vs.push({s:s0,sp});if(s0.type==='stove'&&sp.place!=='range'){const hm=slotHome(s0);vs.push({s:s0,sp:hm,empty:true})}}
 vs.sort((a,b)=>a.sp.y-b.sp.y);for(const v of vs){if(v.empty){c.save();c.translate(v.sp.x,v.sp.y);c.scale(v.sp.sc,v.sp.sc);drawVesselBack(c,DISH(v.s.job.d).v);drawVesselFront(c,DISH(v.s.job.d).v);c.restore();continue}
  if(v.sp.inOven){c.save();c.translate(v.sp.x,v.sp.y);c.scale(v.sp.sc,v.sp.sc);c.globalAlpha=.9;drawVesselBack(c,DISH(v.s.job.d).v);drawContents(c,v.s.job,DISH(v.s.job.d).v,now);c.restore();continue}
  drawStageFood(c,v.s,v.s.job,v.sp.x,v.sp.y,v.sp.sc,now);
  const k=v.s.job.step;if(k&&k.t==='wait'&&/冷藏/.test(k.verb||'')){c.fillStyle='#F4F9FC';circ(c,v.sp.x+14,v.sp.y-18,6);c.fillStyle='#5E8FA8';c.font=`800 7px ${FONT}`;c.textAlign='center';c.textBaseline='middle';c.fillText('❄',v.sp.x+14,v.sp.y-17.6);c.textBaseline='alphabetic'}
  if(R&&R.panel&&R.slots[R.focus]===v.s){const p=(Math.sin(now*6)+1)/2;c.strokeStyle=`rgba(230,194,122,${.5+p*.4})`;c.lineWidth=1.5;c.beginPath();c.ellipse(v.sp.x,v.sp.y+2,26,13,0,0,7);c.stroke()}}}
function drawBurner(c,cx,gy,sc,active,now){c.fillStyle='#17191A';el(c,cx,gy,22*sc*2,11*sc);c.strokeStyle='#6A6E70';c.lineWidth=2*sc;c.beginPath();c.ellipse(cx,gy,36*sc,9*sc,0,0,7);c.stroke();c.lineWidth=1.2*sc;for(let a=0;a<6;a++){c.beginPath();c.moveTo(cx+Math.cos(a)*14*sc,gy+Math.sin(a)*3.4*sc);c.lineTo(cx+Math.cos(a)*42*sc,gy+Math.sin(a)*10.4*sc);c.stroke()}
 if(active){for(let i=0;i<16;i++){const a=i/16*6.283+now*2.5;const fl=(4+Math.sin(now*22+i*1.7)*1.8)*sc;const px=cx+Math.cos(a)*16*sc,py=gy+Math.sin(a)*4*sc;c.fillStyle=i%3?'rgba(90,140,255,.9)':'rgba(255,180,80,.8)';el(c,px,py-fl*.6,1.7*sc,fl)}let hg=c.createRadialGradient(cx,gy,2,cx,gy,56*sc);hg.addColorStop(0,'rgba(255,140,60,.28)');hg.addColorStop(1,'rgba(255,140,60,0)');c.fillStyle=hg;c.fillRect(cx-56*sc,gy-30*sc,112*sc,60*sc)}}
function drawEspresso(c,x,y,w,h,now){let b2=c.createLinearGradient(x,0,x+w,0);b2.addColorStop(0,'#9E7026');b2.addColorStop(.5,'#EFCB80');b2.addColorStop(1,'#95691F');c.fillStyle='rgba(0,0,0,.16)';rr(c,x+2,y+3,w,h,4);c.fill();c.fillStyle=b2;rr(c,x,y,w,h*.62,5);c.fill();c.fillStyle='#2A2A2A';rr(c,x+3,y+h*.62,w-6,6,2);c.fill();c.fillStyle='#8FD3F4';circ(c,x+8,y+9,2);circ(c,x+w/2,y+9,2);circ(c,x+w-8,y+9,2);c.fillStyle='#555';c.fillRect(x+9,y+h*.62+6,4,6);if(h>36)c.fillRect(x+w-13,y+h*.62+6,4,6);c.fillStyle='#3A3F42';rr(c,x+2,y+h-6,w-4,6,2);c.fill();c.strokeStyle='#C9D0D3';c.lineWidth=1.6;c.beginPath();c.moveTo(x+w-3,y+h*.5);c.lineTo(x+w+4,y+h*.75);c.stroke();
 const on=R&&R.slots.some(s0=>s0.type==='bar'&&s0.job);if(on){c.fillStyle=`rgba(120,255,140,${.6+Math.sin(now*8)*.3})`;circ(c,x+w/2,y+9,2)}}
function drawHeatLamps(c,now){const y=KY.rail;const big=projOn('pass');const x0=big?76:92,x1=big?324:308;c.fillStyle='#2A2A2A';c.fillRect(x0,y,x1-x0,2.6);for(const x of[x0,x1]){c.fillRect(x-1.2,y-20,2.4,20)}
 for(const x of big?[110,170,230,290]:[132,200,268]){c.fillStyle='#2A2A2A';c.fillRect(x-.8,y+2,1.6,8);c.fillStyle='#B8536A';c.beginPath();c.moveTo(x-11,y+22);c.lineTo(x+11,y+22);c.lineTo(x+6,y+10);c.lineTo(x-6,y+10);c.closePath();c.fill();c.fillStyle='#8A3A4A';c.fillRect(x-11,y+21,22,1.5);c.fillStyle=`rgba(255,214,120,${.8+Math.sin(now*3+x)*.1})`;el(c,x,y+22.5,7,1.8);
  let g=c.createLinearGradient(0,y+24,0,KY.passTop+30);g.addColorStop(0,'rgba(255,200,110,.22)');g.addColorStop(1,'rgba(255,200,110,0)');c.fillStyle=g;c.beginPath();c.moveTo(x-9,y+24);c.lineTo(x+9,y+24);c.lineTo(x+30,KY.passTop+30);c.lineTo(x-30,KY.passTop+30);c.closePath();c.fill()}}
/* the pass: steel top, the tickets on the rail along its back edge, the plates being finished and the ones waiting */
function drawPass(c,now,V){const T=TH();const big=projOn('pass');const x0=big?64:80,x1=big?336:320,y=KY.passTop,h=KY.passH,f=KY.passFace;
 c.fillStyle='rgba(0,0,0,.18)';rr(c,x0+2,y+5,x1-x0,h+f+6,4);c.fill();let g=c.createLinearGradient(0,y,0,y+h);g.addColorStop(0,'#D3D7D9');g.addColorStop(1,'#AEB5B8');c.fillStyle=g;rr(c,x0,y,x1-x0,h,4);c.fill();c.fillStyle='rgba(255,255,255,.5)';rr(c,x0+2,y+1.5,x1-x0-4,2.5,1.2);c.fill();
 let fg=c.createLinearGradient(0,y+h,0,y+h+f);fg.addColorStop(0,T.c0);fg.addColorStop(1,T.c1);c.fillStyle=fg;rr(c,x0,y+h-2,x1-x0,f+2,2);c.fill();c.fillStyle='rgba(0,0,0,.2)';c.fillRect(x0,y+h+f-2,x1-x0,3);
 /* the rail with the open tickets */c.fillStyle='#3A3A3A';c.fillRect(x0+8,y-2,x1-x0-16,2);if(V.tickets){const open=V.tickets.filter(tk=>tk.items.some(it=>it.st==='pending'||it.st==='cooking'));
  open.slice(0,9).forEach((tk,i)=>{const x=x0+14+i*22,ty=y-16;c.fillStyle='rgba(0,0,0,.15)';c.fillRect(x+1,ty+1,18,15);c.fillStyle='#FFFDF5';c.fillRect(x,ty,18,15);c.fillStyle='#8A9498';c.fillRect(x+7,ty-2,4,3);c.fillStyle='#2E2019';c.font=`800 6px ${FONT}`;c.textAlign='center';c.textBaseline='middle';c.fillText('T'+tk.no,x+9,ty+5);tk.items.slice(0,4).forEach((it,k)=>{c.fillStyle=it.st==='cooking'?'#E6B04A':it.st==='pending'?'#E0543A':'#8FB07A';circ(c,x+4+k*3.6,ty+11.5,1.3)})});c.textBaseline='alphabetic'}
 /* plates being finished at the pass */for(const s0 of V.slots){const j=s0.job;if(!j||!j.plating)continue;const px=j.plating.x||200,py=y+14;const u=clamp(j.plating.t/j.plating.dur,0,1);const sz=24+u*10;c.globalAlpha=.55+u*.45;c.drawImage(dishCanvas(j.d,'G',64,S.decor.ware>0,j.it.want),px-sz/2,py-sz/2,sz,sz);c.globalAlpha=1;
  if(u>.55){/* the garnish going on */const fin=DISH(j.d).fin;if(fin&&fin.length){const t=(u-.55)/.45;c.globalAlpha=1-t;drawIng(c,fin[0],px+8,py-16-t*10,9);c.globalAlpha=1}}
  for(let k=0;k<3;k++){const ph=(now*1.2+k*.33)%1;c.globalAlpha=(1-ph)*.5;c.fillStyle='#fff';circ(c,px-8+k*8,py-16-ph*14,2+ph*3);c.globalAlpha=1}}
 /* plates waiting under the lamps, ticket number on each */if(V.tickets){const ready=[];for(const tk of V.tickets)for(const it of tk.items)if(it.st==='ready'&&!it.picked)ready.push({tk,it});
  ready.slice(0,big?11:9).forEach((r0,i)=>{const x=x0+18+i*26,py=y+22;c.fillStyle='rgba(0,0,0,.12)';el(c,x,py+14,15,3.5);c.drawImage(dishCanvas(r0.it.d,r0.it.q,64,S.decor.ware>0,r0.it.want),x-17,py-17,34,34);c.fillStyle='#FFF8EC';rr(c,x+6,py-22,14,8,2);c.fill();c.fillStyle='#2E2019';c.font=`800 5.5px ${FONT}`;c.textAlign='center';c.textBaseline='middle';c.fillText('T'+r0.tk.no,x+13,py-18);c.textBaseline='alphabetic';
   c.strokeStyle='rgba(255,255,255,.45)';c.lineWidth=1;for(let k=0;k<2;k++){const ph=(now*.8+i*.37+k*.5)%1;c.globalAlpha=(1-ph)*.6;c.beginPath();c.moveTo(x-4+k*8,py-12-ph*10);c.quadraticCurveTo(x-1+k*8,py-16-ph*10,x-4+k*8,py-20-ph*10);c.stroke();c.globalAlpha=1}})}}
function drawKFridge(c,now,x,y,w,h){const open=(now-FRIDGE_T)<1.8;c.fillStyle='rgba(0,0,0,.16)';rr(c,x+2,y+3,w,h,3);c.fill();c.fillStyle=S.level>=4?'#4A4A4E':'#C9CDD0';rr(c,x,y,w,h,3);c.fill();let fg=c.createLinearGradient(x,0,x+w,0);fg.addColorStop(0,'#E4E6E7');fg.addColorStop(.5,'#F7F8F8');fg.addColorStop(1,'#CDD1D3');c.fillStyle=fg;rr(c,x+2,y+(open?6:2),w-4,h-6,2);c.fill();c.fillStyle='#9AA3A6';rr(c,x+w-14,y+h*.45,8,3,1);c.fill();c.fillStyle='#2A2F33';rr(c,x+w-16,y+8,10,6,1);c.fill();c.fillStyle='#8FD3F4';c.font=`800 4px ${FONT}`;c.textAlign='center';c.fillText('3°C',x+w-11,y+12.4);c.fillStyle='rgba(60,56,50,.75)';c.font=`800 6.5px ${FONT}`;c.fillText('冰箱 · 庫存',x+w/2,y+h+9);
 if(R&&menuList().some(d=>(S.stock[d]||0)<=1)){const p=(Math.sin(now*6)+1)/2;c.fillStyle='#E0543A';circ(c,x+6,y-4-p*1.5,5.5);c.fillStyle='#fff';c.font=`800 7.5px ${FONT}`;c.textAlign='center';c.textBaseline='middle';c.fillText('!',x+6,y-3.6-p*1.5);c.textBaseline='alphabetic'}}
function drawCooler(c,now,k){const {x,y,w,h}=k;c.fillStyle='rgba(0,0,0,.16)';rr(c,x+2,y+3,w,h,3);c.fill();c.fillStyle='#C9CDD0';rr(c,x,y,w,h,3);c.fill();c.fillStyle='#E4E6E7';rr(c,x+3,y+3,w-6,h-6,2);c.fill();c.fillStyle='#8FA0A8';rr(c,x+w-12,y+h/2-8,6,16,2);c.fill();c.fillStyle='rgba(140,200,230,.35)';rr(c,x+6,y+8,w-20,10,2);c.fill();c.fillStyle='#2A2F33';c.font=`800 6.5px ${FONT}`;c.textAlign='center';c.fillText('冷藏庫',x+w/2,y+h+9)}
function drawHandKnife(c,x,y,f,now){const a=Math.sin(now*9);c.save();c.translate(x+f*4,y-26+a*1.6);c.rotate(f*(-.55+a*.3));c.fillStyle='#D9D9DD';rr(c,-1.1,-8,2.4,9.5,1);c.fill();c.strokeStyle='rgba(60,34,22,.4)';c.lineWidth=.5;c.stroke();c.fillStyle='#4A3226';rr(c,-1.4,1.4,3,4.4,1.2);c.fill();c.restore()}
function drawHandSpoon(c,x,y,f,now){const a=now*6;c.save();c.translate(x+f*4+Math.cos(a)*2,y-27+Math.sin(a)*1.2);c.rotate(f*-.5);c.fillStyle='#6B4428';rr(c,-.9,-9,1.8,10,.9);c.fill();c.fillStyle='#8A6A42';el(c,0,1.5,2.4,1.6);c.restore()}
/* a cook: walking the aisle, or at work with the tool of the step; a plate in hand on the way to the pass */
function drawCook(c,m,a,now){const b=a.beat||{kind:'idle'};const k=b.s&&b.s.job&&b.s.job.step;const moving=a.moving;const stp=moving?Math.sin(a.step):0;
 const busy=!moving&&(b.kind!=='idle'&&b.kind!=='watch');const chop=busy&&k&&k.t==='work'&&k.board;const stir=busy&&((k&&k.t==='tap'&&k.heat)||b.kind==='stir'||(k&&k.t==='work'&&!k.board));const plating=b.kind==='plate'&&!moving;
 const idle=b.kind==='idle'&&!moving?a.idle:null;const wiping=idle==='wipe';const bob=moving?Math.abs(stp)*-1:chop?Math.abs(Math.sin(now*9))*-1.2:plating?Math.abs(Math.sin(now*7))*-.9:busy?Math.abs(Math.sin(now*5))*-.6:wiping?Math.abs(Math.sin(now*8))*-.5:Math.sin(now*2+a.x)*.4;
 const sipping=idle==='sip'||idle==='taste';const arms=moving?null:(chop||stir)?[.35,.95+Math.sin(now*(chop?9:6))*.25]:busy&&k&&(k.t==='hold'||k.t==='dose')?[.3,1.1]:plating?[.65+Math.sin(now*7)*.1,.65-Math.sin(now*7)*.1]:b.kind==='watch'||idle==='rail'?[1.05,1.05]:sipping?[.3,1.25]:idle==='chat'?[.4+Math.sin(now*3)*.15,.35]:null;
 drawPerson(c,a.x,a.y,crewLook(m),{s:1.1,mood:'happy',expr:busy||b.kind==='watch'?'focus':'smile',bob,step:stp,flip:a.face<0,blink:Math.sin(now*1.5+a.x)>.97,arms,gaze:idle==='rail'?{x:0,y:.5}:idle==='chat'?{x:1,y:.1}:null});
 if(wiping){const f=a.face<0?-1:1;c.fillStyle='#F4F1EA';el(c,a.x+f*12+Math.sin(now*8)*5,a.y-24,5,3)}
 else if(sipping){const f=a.face<0?-1:1;c.save();c.translate(a.x+f*5,a.y-38);c.rotate(f*.35);if(idle==='sip'){c.fillStyle='#F6F1E6';rr(c,-3.2,-3,6.4,7.5,1.4);c.fill();c.fillStyle='rgba(120,90,60,.35)';el(c,0,-2.6,2.6,.9)}else{c.fillStyle='#C9CDD2';c.fillRect(-.8,-1,1.6,9);el(c,0,-2.4,2.8,1.8);c.fillStyle='#D9A45A';el(c,0,-2.4,1.8,1)}c.restore()}
 else if(idle==='chat'&&a.talker&&Math.sin(now*1.6)>-.2){const f=a.face<0?-1:1;c.fillStyle='rgba(255,250,240,.95)';const bx=a.x+f*14,by=a.y-66;rr(c,bx-7,by-5,14,10,4);c.fill();c.fillStyle='#2E2019';for(let i=-1;i<=1;i++)circ(c,bx+i*3,by+.4,.9)}
 if(chop)drawHandKnife(c,a.x,a.y,a.face<0?-1:1,now);else if(stir)drawHandSpoon(c,a.x,a.y,a.face<0?-1:1,now);
 else if(busy&&k&&(k.t==='hold'||k.t==='dose')){/* a bottle or a shaker, tipped over the vessel */const col=k.ing==='beans'?'#6B3A1A':(ING[k.ing]||{}).c||'#ccc';const f=a.face<0?-1:1;c.save();c.translate(a.x+f*6,a.y-31);c.rotate(f*.9);c.fillStyle=col==='#FFFFFF'?'#F2EEE6':col;rr(c,-2.4,-7,4.8,11,1.6);c.fill();c.fillStyle='#2A2A2A';c.fillRect(-1.4,-9.5,2.8,3);c.restore();if(k.t==='dose'){for(let i=0;i<4;i++){const ph=(now*2+i*.25)%1;c.globalAlpha=1-ph;c.fillStyle=col;circ(c,a.x+f*14+(i-1.5)*2,a.y-26+ph*10,.9);c.globalAlpha=1}}}
 if(b.kind==='plate'&&moving){c.drawImage(dishCanvas(b.s.job.d,'G',64,S.decor.ware>0,b.s.job.it.want),a.x-10,a.y-44,20,20)}
 nameTag(c,a.x,a.y-62,m.name)}
/* ---- the side room: the lounge. An arch back to the dining room on the left of the back wall, a big window with curtains,
   a sideboard with a lamp, the wine bar (once bought), its own tables, a rug ---- */
function drawSideRoom(c,now,dusk,V,X0,XW,TOP,list){const T=TH();const d=clamp(dusk,0,1);
 const bg=roomBg('side',S.level+'|'+(S.theme||'')+'|'+(S.decor.bar?1:0)+'|'+(gearOn('lounge')?1:0)+'|'+(gearOn('perch')?1:0),TOP,(b,X0,XW,T2)=>{const r=rng(53);
  b.fillStyle=T.base;b.fillRect(X0,-T2,XW,T2+92);let wg=b.createLinearGradient(0,-T2,0,92);wg.addColorStop(0,T.wall0);wg.addColorStop(1,T.wall1);b.fillStyle=wg;b.fillRect(X0,-T2,XW,T2+92);
  for(let i=0;i<300;i++){b.fillStyle=`rgba(${r()<.5?'255,255,255':'70,70,66'},${.03+r()*.05})`;el(b,X0+r()*XW,-T2+r()*(T2+88),4+r()*16,2+r()*8)}
  b.strokeStyle='rgba(70,70,66,.3)';b.lineWidth=.7;for(let x=X0+10;x<LW+BGM;x+=92){b.beginPath();b.moveTo(x,-T2);b.lineTo(x,86);b.stroke()}for(let y=44;y>-T2;y-=44){b.beginPath();b.moveTo(X0,y);b.lineTo(LW+BGM,y);b.stroke()}
  b.fillStyle=T.base;b.fillRect(X0,85,XW,7);b.fillStyle='rgba(0,0,0,.12)';b.fillRect(X0,91.5,XW,1.5);if(S.level>=4){b.fillStyle='#C99A45';b.fillRect(X0,84.4,XW,1.2)}
  /* the floor, like the dining room's */b.fillStyle=T.floor;b.fillRect(X0,92,XW,LH-92);for(let i=0;i<5000;i++){b.fillStyle=r()<.55?'rgba(255,255,255,.35)':'rgba(140,120,95,.12)';b.fillRect(X0+r()*XW,92+r()*(LH-92),.9,.9)}
  b.strokeStyle='rgba(150,130,105,.06)';b.lineWidth=.6;for(let y=96;y<LH;y+=3){b.beginPath();b.moveTo(X0,y);b.lineTo(LW+BGM,y+(r()-.5)*1.5);b.stroke()}
  let g=b.createLinearGradient(0,92,0,LH);g.addColorStop(0,'rgba(60,50,40,.24)');g.addColorStop(.12,'rgba(60,50,40,0)');g.addColorStop(1,'rgba(60,50,40,.14)');b.fillStyle=g;b.fillRect(X0,92,XW,LH-92);
  /* a rug between the rows */b.save();b.translate(200,258+DY*.3);b.scale(1,.42);b.fillStyle='rgba(0,0,0,.1)';el(b,3,8,112,84);b.fillStyle='#C4A0A6';el(b,0,0,110,82);b.fillStyle='#D2B2B7';el(b,0,0,92,66);b.strokeStyle='rgba(255,255,255,.35)';b.lineWidth=2.5;for(let k=0;k<3;k++){b.beginPath();b.ellipse(0,0,28+k*22,18+k*16,0,0,7);b.stroke()}b.restore();
  /* the arch back to the dining room */drawArch(b,SIDE_L.arch.x,SIDE_L.arch.y,SIDE_L.arch.w,80,'‹ 用餐區');
  /* two brass sconces */for(const sx of[104,296]){b.fillStyle='#8E6422';b.fillRect(sx-1.5,30,3,10);b.fillStyle='#EAC274';b.beginPath();b.moveTo(sx-7,30);b.lineTo(sx+7,30);b.lineTo(sx+5,22);b.lineTo(sx-5,22);b.closePath();b.fill();b.fillStyle='rgba(255,236,190,.9)';el(b,sx,30.5,5,1.5)}
  /* the big window with curtains */{const {x,y,w,h}=SIDE_L.window;b.fillStyle='#E6E3DC';b.fillRect(x-4,y-4,w+8,h+8);b.fillStyle='#F3F1EC';b.fillRect(x,y,w,h);b.fillStyle='#EFECE6';b.fillRect(x-6,y+h+2,w+12,3);
   b.fillStyle='#8A6A42';b.fillRect(x-22,y-10,w+44,3.5);for(const cx of[x-18,x+w+4]){let cg=b.createLinearGradient(cx,0,cx+14,0);cg.addColorStop(0,'#A64A5E');cg.addColorStop(.5,'#C25E74');cg.addColorStop(1,'#A64A5E');b.fillStyle=cg;b.beginPath();b.moveTo(cx,y-7);b.lineTo(cx+14,y-7);b.lineTo(cx+12,y+h+4);b.lineTo(cx+2,y+h+4);b.closePath();b.fill();b.fillStyle='rgba(0,0,0,.12)';for(let k=0;k<3;k++)b.fillRect(cx+3+k*4,y-6,1,h+9)}
   b.fillStyle='#B8536A';b.fillRect(x-20,y-8,w+40,8);b.fillStyle='rgba(255,255,255,.18)';b.fillRect(x-20,y-8,w+40,2)}
  /* the sideboard under the window: a lamp, a vase, a framed photo */{const sx=150,sy=76,sw=100;b.fillStyle='rgba(0,0,0,.16)';rr(b,sx+2,sy+4,sw,28,3);b.fill();b.fillStyle='#8A6A42';rr(b,sx,sy,sw,26,3);b.fill();b.fillStyle='#A98559';b.fillRect(sx+3,sy+2,sw-6,3);b.fillStyle='#6E4E2E';for(let k=0;k<3;k++){rr(b,sx+6+k*31,sy+8,27,14,1.5);b.fill();b.fillStyle='#C99A45';b.fillRect(sx+17+k*31,sy+14,5,1.6);b.fillStyle='#6E4E2E'}
   b.fillStyle='#2A2A2A';b.fillRect(sx+14,sy-14,2,14);b.fillStyle='#F6EEDF';b.beginPath();b.moveTo(sx+6,sy-14);b.lineTo(sx+24,sy-14);b.lineTo(sx+21,sy-26);b.lineTo(sx+9,sy-26);b.closePath();b.fill();
   b.fillStyle='#5E8FA8';rr(b,sx+50,sy-12,8,12,3);b.fill();b.strokeStyle='#5E9E3D';b.lineWidth=.9;for(const dx of[-2,0,2]){b.beginPath();b.moveTo(sx+54,sy-12);b.lineTo(sx+54+dx*2,sy-22);b.stroke()}b.fillStyle='#E8798A';for(const dx of[-4,0,4])circ(b,sx+54+dx,sy-22,1.6);
   b.fillStyle='#2A2A2A';b.fillRect(sx+74,sy-13,16,13);b.fillStyle='#F3F0EA';b.fillRect(sx+75.5,sy-11.5,13,10);b.fillStyle='#C08A6A';circ(b,sx+82,sy-6.5,3)}
  /* the wine bar moved in here with the side room */if(S.decor.bar){b.fillStyle='#2A2A28';b.fillRect(318,26,60,22);const bc=['#2E6B4A','#8A2A2A','#C99A45','#3A5A8A','#6B3A5A','#D9C27A'];for(let i=0;i<9;i++){b.fillStyle=bc[i%6];rr(b,321+i*6.4,28-(i%3)*2,4.2,17+(i%3)*2,1.5);b.fill()}b.fillStyle='#8C8A84';b.fillRect(306,86,94,18);b.fillStyle='#A7A59F';b.fillRect(306,90,94,14);b.fillStyle='#ECE9E3';b.fillRect(304,84,96,3);for(const x of[322,352]){b.fillStyle='#2A2A2A';b.fillRect(x-.8,108,1.6,10);b.fillStyle='#D9D5CD';el(b,x,107,7,3)}}
  else{/* a bookshelf instead */b.fillStyle='#8A6A42';b.fillRect(330,20,52,72);b.fillStyle='#6E4E2E';b.fillRect(333,23,46,66);const cols=['#B8536A','#5E8FA8','#E6C27A','#2E6B4A','#C08A6A','#F3F0EA'];for(let sh=0;sh<3;sh++){b.fillStyle='#8A6A42';b.fillRect(333,44+sh*22,46,2);let x=335;for(let k=0;k<7&&x<376;k++){const w=4+(k*7)%4;b.fillStyle=cols[(k+sh)%6];b.fillRect(x,26+sh*22-(k%2?2:0),w,18+(k%2?2:0));x+=w+1}}}
  /* the cat lounge in the corner, once bought */if(gearOn('lounge')){b.fillStyle='rgba(0,0,0,.14)';el(b,352,414,20,8);b.fillStyle='#8FA893';el(b,352,410,20,9);b.fillStyle='#A9BFAC';el(b,352,408,15,6)}
  });
 blitBg(c,bg,X0,XW,TOP);
 /* the window glass: sky by the hour and the weather */{const {x,y,w,h}=SIDE_L.window;const W=wxNow();const wet=W==='rain'||W==='storm';let g=c.createLinearGradient(0,y,0,y+h);const top=wet?(W==='storm'?'#8A93A0':'#B9C2CC'):W==='hot'?'#FFEFC8':W==='cool'?'#EAF4F8':'#FFF4DE',bot=wet?(W==='storm'?'#6E7683':'#9AA4B0'):'#FCE4BE';g.addColorStop(0,mix(top,'#3A3E5E',d));g.addColorStop(1,mix(bot,'#4E4666',d));c.fillStyle=g;c.fillRect(x,y,w,h);
  if(wet){const n=W==='storm'?24:12;c.strokeStyle=`rgba(230,240,250,${W==='storm'?.55:.4})`;c.lineWidth=.8;for(let k=0;k<n;k++){const ph=((now*(W==='storm'?.9:.5))+k*.37)%1;const rx=x+3+((k*29)%(w-6));const ry=y+ph*h;c.beginPath();c.moveTo(rx,ry);c.lineTo(rx-1,ry+6+(k%3)*3);c.stroke()}}
  else{c.fillStyle=`rgba(255,255,255,${.25-d*.2})`;el(c,x+40,y+18,22,6);el(c,x+120,y+30,30,7)}
  c.fillStyle='#F3F1EC';c.fillRect(x+w/2-1.5,y,3,h);c.fillRect(x,y+h/2-1,w,2);if(d>.5){let lg=c.createLinearGradient(0,y,0,y+h);lg.addColorStop(0,'rgba(255,214,150,0)');lg.addColorStop(1,`rgba(255,214,150,${(d-.5)*.5})`);c.fillStyle=lg;c.fillRect(x,y,w,h)}}
 list.push({y:112,f:()=>drawPlant(c,104,110,'tall')},{y:112,f:()=>drawPlant(c,296,110,'bush')});
 if(d>.45){/* the lamp on the sideboard is on */let lg=c.createRadialGradient(165,64,2,165,64,40);lg.addColorStop(0,`rgba(255,214,150,${.35*d})`);lg.addColorStop(1,'rgba(255,214,150,0)');c.fillStyle=lg;c.fillRect(125,24,80,80)}}
/* ---- the street: the sky by the hour and the weather, the neighbours, the façade with the sign, the door (OPEN while the
   service runs), the pavement with whatever was bought for it, the tables under umbrellas ---- */
function drawFrontRoom(c,now,dusk,V,X0,XW,TOP,list){const d=clamp(dusk,0,1);const W=wxNow();const wet=W==='rain'||W==='storm';const E=S.ext||{};const dq=Math.round(d*16)/16;
 const bg=roomBg('front',S.level+'|'+W+'|'+dq+'|'+JSON.stringify(E)+'|'+Math.floor(S.day/10)+'|'+(S.rooms&&S.rooms.terrace?S.frontTables:0),TOP,(b,X0,XW,T2)=>{const d=dq;
  /* sky */{let g=b.createLinearGradient(0,-T2,0,130);const top=wet?'#8E97A2':W==='hot'?'#9FC8EC':W==='cool'?'#C9DDEA':'#A9D3F0',bot=wet?'#B7BFC8':'#F2DEC0';g.addColorStop(0,mix(top,'#1E2438',d));g.addColorStop(1,mix(bot,'#5E4666',d));b.fillStyle=g;b.fillRect(X0,-T2,XW,130+T2);
   if(!wet){b.fillStyle=`rgba(255,240,200,${.9-d*.6})`;circ(b,340-d*60,Math.max(-T2+14,20-T2*.4)+d*40,10);if(d>.6){b.fillStyle=`rgba(255,255,255,${(d-.6)*2})`;for(let k=0;k<26;k++)circ(b,X0+((k*67)%XW),-T2+((k*41)%(90+T2)),.9)}}
   b.fillStyle=`rgba(255,255,255,${.35-d*.3})`;for(const [cx,cy,r0] of[[80,-T2+30,14],[104,-T2+26,18],[128,-T2+32,12]])circ(b,cx,cy,r0);
   /* the neighbours: two quiet buildings */b.fillStyle=mix('#D9CFC2','#2A2A38',d);b.fillRect(X0,56,BGM+34,74);b.fillStyle=mix('#CFC2B4','#2A2A38',d);b.fillRect(366,48,XW,82);b.fillStyle=mix('#B8A898','#1E1E2A',d);b.fillRect(X0,56,BGM+34,5);b.fillRect(366,48,XW,5);for(const [x,y] of[[-36,70],[-36,98],[6,70],[6,98],[376,64],[376,94],[406,64],[406,94]]){b.fillStyle=d>.5?'rgba(255,220,150,.8)':'rgba(120,130,150,.6)';b.fillRect(x,y,11,14)}}
  /* the façade */const wall='#EADFC8',trim='#B8536A';b.fillStyle=wall;b.fillRect(X0+34,120,XW-68,170);b.fillStyle='rgba(0,0,0,.08)';for(let y=126;y<286;y+=16)b.fillRect(X0+34,y,XW-68,1);b.fillStyle=trim;b.fillRect(X0+34,120,XW-68,6);b.fillStyle='rgba(0,0,0,.12)';b.fillRect(X0+34,126,XW-68,3);
  /* windows: the dining room, faintly, behind the glass */for(const wx of[78,258]){b.fillStyle='#3A2A22';b.fillRect(wx-3,188,70,62);let g=b.createLinearGradient(0,190,0,248);g.addColorStop(0,d>.45?'#FFE2A8':'#F6EFE0');g.addColorStop(1,d>.45?'#E8B865':'#E4DCCB');b.fillStyle=g;b.fillRect(wx,191,64,56);b.fillStyle='rgba(60,40,30,.22)';el(b,wx+18,236,9,4);el(b,wx+46,236,9,4);b.fillRect(wx+14,224,8,12);b.fillRect(wx+42,224,8,12);b.fillStyle='rgba(255,255,255,.3)';b.fillRect(wx+4,195,14,48);b.fillStyle='#3A2A22';b.fillRect(wx+31,191,2,56);b.fillStyle='#F6EEDF';b.fillRect(wx-6,250,76,3)}
  /* the door */{const x=FR.door.x;b.fillStyle='#3A2A22';b.fillRect(x-24,180,48,82);b.fillStyle='#6B4428';b.fillRect(x-20,184,40,78);b.fillStyle='#C99A45';b.fillRect(x-20,184,40,2);b.fillStyle='rgba(255,230,180,.35)';b.fillRect(x-14,190,28,28);b.fillStyle='#E6C27A';circ(b,x+12,228,2);
   b.fillStyle='#CFC6B8';b.fillRect(x-30,262,60,8);b.fillStyle='rgba(0,0,0,.15)';b.fillRect(x-30,269,60,2)}
  /* the sign */{const L=S.level;const signW=L===5?120:136;b.fillStyle='rgba(0,0,0,.18)';rr(b,200-signW/2+2,143,signW,30,4);b.fill();b.fillStyle=L===5?'#14161F':'#2C2C2B';rr(b,200-signW/2,140,signW,30,4);b.fill();b.strokeStyle=L>=4?'#E0B863':'rgba(230,194,122,.7)';b.lineWidth=1.1;rr(b,200-signW/2+2.5,142.5,signW-5,25,3);b.stroke();
   b.fillStyle='#E6C27A';b.textAlign='center';b.textBaseline='middle';if(L===5){b.font=`400 20px ${DFONT}`;b.fillText('J I L L',200,156)}else{b.font=`400 ${L===1?11:12.5}px ${DFONT}`;b.fillText(LV().n,200,155.5)}b.textBaseline='alphabetic';
   if(E.sign){b.fillStyle='#8E6422';b.fillRect(198,132,4,8);b.fillStyle='#F4C44E';el(b,200,132,7,2.5);if(d>.3){let g=b.createRadialGradient(200,150,4,200,150,70);g.addColorStop(0,`rgba(255,214,120,${.35*d})`);g.addColorStop(1,'rgba(255,214,120,0)');b.fillStyle=g;b.fillRect(120,110,160,80)}}}
  /* the awning */if(E.awning){const cols=E.awning===2?['#2E6B4A','#F7EDDC']:E.awning===3?['#2E3A4B','#F7EDDC']:['#B8536A','#F7EDDC'];b.fillStyle='rgba(0,0,0,.15)';b.fillRect(126,196,148,6);for(let i=0;i<12;i++){b.fillStyle=cols[i%2];b.beginPath();b.moveTo(126+i*12.3,176);b.lineTo(126+(i+1)*12.3,176);b.lineTo(126+(i+1)*12.3+4,196);b.lineTo(126+i*12.3+4,196);b.closePath();b.fill()}b.fillStyle=cols[0];for(let i=0;i<12;i++){b.beginPath();b.arc(132+i*12.3,197,5,0,Math.PI);b.fill()}}
  /* the pavement and the street */b.fillStyle='#CFC9BE';b.fillRect(X0,284,XW,90);b.fillStyle='rgba(0,0,0,.07)';for(let x=X0;x<LW+BGM;x+=40)b.fillRect(x,284,1,90);b.fillRect(X0,328,XW,1);b.fillStyle='#B8B2A6';b.fillRect(X0,372,XW,5);b.fillStyle='#4A4A4E';b.fillRect(X0,377,XW,LH-377);b.fillStyle='rgba(255,255,255,.5)';for(let x=X0;x<LW+BGM;x+=40)b.fillRect(x,400,22,2);
  /* planters, the bench, seasonal things */if(E.plants){for(const px of[150,250]){b.fillStyle='#8A3A2A';rr(b,px-12,266,24,16,2);b.fill();for(let k=0;k<7;k++)leaf(b,px-8+k*2.6,262-Math.abs(k-3)*2,9,3.6,-1.6+(k-3)*.4,k%2?'#3F7F32':'#5E9E3D');b.fillStyle='#E8798A';circ(b,px-4,258,1.6);b.fillStyle='#F4C44E';circ(b,px+3,256,1.6)}}
  if(E.bench){const {x,y}=FR.bench;b.fillStyle='#6B4428';b.fillRect(x-24,y-12,48,5);b.fillRect(x-24,y-2,48,5);b.fillRect(x-22,y+3,3,12);b.fillRect(x+19,y+3,3,12);b.fillStyle='#8A6A42';b.fillRect(x-24,y-12,48,1.5)}
  if(E.season){const k=Math.floor(S.day/10)%3;if(k===0){for(const lx of[60,340]){b.fillStyle='#8A3A2A';b.fillRect(lx-1,160,2,12);b.fillStyle='#D8392A';el(b,lx,182,7,10);b.fillStyle='#F4C44E';b.fillRect(lx-3,171,6,2);b.fillRect(lx-3,192,6,2)}}else if(k===1){for(let i=0;i<8;i++){b.fillStyle=['#E8798A','#F4C44E','#7FB3C8','#5E9E3D'][i%4];b.beginPath();b.moveTo(60+i*40,132);b.lineTo(72+i*40,132);b.lineTo(66+i*40,146);b.closePath();b.fill()}}else{b.fillStyle='#F4C44E';for(const lx of[70,330])for(let i=0;i<5;i++)el(b,lx+Math.cos(i*1.26)*7,178+Math.sin(i*1.26)*7,3,3)}}
  if(wet){b.fillStyle='rgba(120,140,170,.18)';b.fillRect(X0,284,XW,LH-284)}
  /* the street lamp on the corner, a bicycle against the wall */b.fillStyle='#2A2A2E';b.fillRect(366,150,3,134);b.fillStyle='#3A3A3E';rr(b,360,282,15,5,2);b.fill();b.beginPath();b.moveTo(367.5,150);b.quadraticCurveTo(367.5,138,356,138);b.lineTo(356,141);b.quadraticCurveTo(364.5,141,364.5,150);b.closePath();b.fill();b.fillStyle='#F4E2B0';rr(b,349,138,14,9,2);b.fill();b.fillStyle='#2A2A2E';b.fillRect(348,136,16,2.5);
  b.strokeStyle='#2E2B33';b.lineWidth=1.6;for(const wx of[44,66]){b.beginPath();b.arc(wx,276,8,0,7);b.stroke();b.beginPath();b.arc(wx,276,2,0,7);b.stroke()}b.beginPath();b.moveTo(44,276);b.lineTo(53,262);b.lineTo(66,276);b.moveTo(53,262);b.lineTo(58,262);b.lineTo(66,276);b.moveTo(50,258);b.lineTo(56,258);b.stroke();b.fillStyle='#8A6A42';rr(b,55,260,6,2.5,1);b.fill();
  b.fillStyle='rgba(60,56,50,.7)';b.font=`800 7px ${FONT}`;b.textAlign='center';b.fillText('點門口進去',FR.door.x,280)});
 blitBg(c,bg,X0,XW,TOP);
 /* live: rain, the door plate, the string lights, the umbrellas; the lamp and the windows on the wet pavement */
 if(d>.25){c.save();c.globalCompositeOperation='lighter';let g=c.createRadialGradient(356,146,3,356,146,80);g.addColorStop(0,`rgba(255,226,150,${.38*d})`);g.addColorStop(1,'rgba(255,226,150,0)');c.fillStyle=g;c.fillRect(276,66,160,180);c.restore()}
 if(wet){c.save();c.globalCompositeOperation='lighter';for(const wx of[110,290,200]){let g=c.createLinearGradient(0,286,0,360);g.addColorStop(0,`rgba(255,214,140,${.18+d*.14})`);g.addColorStop(1,'rgba(255,214,140,0)');c.fillStyle=g;c.fillRect(wx-30,286,60,74)}c.restore()}
 if(wet){for(let k=0;k<(W==='storm'?40:18);k++){const ph=((now*(W==='storm'?.9:.5))+k*.37)%1;const rx=X0+((k*53)%XW);c.strokeStyle='rgba(230,240,250,.45)';c.lineWidth=.8;c.beginPath();c.moveTo(rx,-TOP+ph*(130+TOP));c.lineTo(rx-1,-TOP+ph*(130+TOP)+9);c.stroke()}}
 {const x=FR.door.x;c.fillStyle='#F6EEDF';rr(c,x-12,224,24,11,2);c.fill();c.fillStyle=R?'#2E6B4A':'#8A3A2A';c.font=`800 6px ${FONT}`;c.textAlign='center';c.fillText(R?'OPEN':'CLOSED',x,232)}
 if(E.lights){c.strokeStyle='rgba(40,30,20,.7)';c.lineWidth=.7;c.beginPath();for(let x=40;x<=360;x+=4)c.lineTo(x,128+Math.sin((x-40)/60*Math.PI)*8);c.stroke();for(let x=48;x<360;x+=16){const y=131+Math.sin((x-40)/60*Math.PI)*8;const tw=.75+Math.sin(now*2+x*.3)*.25;c.fillStyle=`rgba(255,${Math.round(205+tw*30)},${Math.round(130+tw*40)},${.55+d*.45})`;el(c,x,y,1.8,2.4);if(d>.2){let g=c.createRadialGradient(x,y,0,x,y,9);g.addColorStop(0,`rgba(255,200,120,${.35*d*tw})`);g.addColorStop(1,'rgba(255,200,120,0)');c.fillStyle=g;c.fillRect(x-9,y-9,18,18)}}}
 if(S.rooms&&S.rooms.terrace)for(const t of V.tables)if(t.room==='front'){list.push({y:t.y-58,f:()=>{c.fillStyle='#8A6A42';c.fillRect(t.x-1,t.y-62,2,44);c.fillStyle='#B8536A';c.beginPath();c.moveTo(t.x-40,t.y-58);c.quadraticCurveTo(t.x,t.y-88,t.x+40,t.y-58);c.closePath();c.fill();c.fillStyle='rgba(255,255,255,.25)';c.beginPath();c.moveTo(t.x-40,t.y-58);c.quadraticCurveTo(t.x-20,t.y-80,t.x,t.y-84);c.lineTo(t.x,t.y-58);c.closePath();c.fill();c.fillStyle='rgba(0,0,0,.1)';for(let k=-3;k<=3;k++)c.fillRect(t.x+k*13-.5,t.y-58,1,3)}})}}

/* ================= 2.1: the street has a life of its own =================
   While the restaurant is open, people walk the pavement: neighbours, students, a couple, someone with a dog; a scooter
   or a bicycle passes on the road. Some stop at a window or the door and look in (the street pieces make that likelier,
   and the lights in the evening). One who likes what they see becomes the next arrival on the schedule: the same person
   turns and walks in from where they stood, so the guests visibly come from the street. Demand does not change — a
   walk-in takes the place of the party that was about to arrive. */
const STREET={ppl:[],next:0,veh:null,nextVeh:0};
const STREET_TYPES=['office','student','couple','gourmet','office','student','couple'];
const UMB_COLS=['#B8536A','#2E6B4A','#2E3A4B','#E0A43A','#5B6FB3','#F7EDDC'];
function streetReset(){STREET.ppl=[];STREET.next=rand(2,6);STREET.veh=null;STREET.nextVeh=rand(8,26)}
function streetWet(){const W=wxNow();return W==='rain'||W==='storm'}
function streetStopP(){let p=.14;if(extOn('plants'))p+=.05;if(extOn('lights'))p+=.04;if(extOn('sign'))p+=.05;if(extOn('awning'))p+=.05;if(extOn('season'))p+=.03;if(projOn('terrace')&&(S.frontTables||0)>0)p+=.06;if(duskF()>.5&&(extOn('lights')||extOn('sign')))p+=.08;return Math.min(.55,p)}
function streetSpawn(){const dir=Math.random()<.5?1:-1;const type=pick(STREET_TYPES);const n=type==='couple'?2:Math.random()<.22?2:1;const wet=streetWet();
 const w={x:dir>0?-BGM-34:LW+BGM+34,y:rand(336,366),dir,v:rand(24,38)*(wet?1.3:1),looks:makeLooks(type,n),type,n,walk:Math.random()*6,st:'walk',t:0,dur:0,seed:Math.random()*10,dog:n===1&&!wet&&Math.random()<.2,dogCol:pick(['#C9A063','#5A4632','#F2EAD8','#2A2220','#B5652A']),umb:wet&&Math.random()<.9?pick(UMB_COLS):null,stopX:null,bub:0};
 if(w.dog)w.v=Math.min(w.v,30);
 if(!R.closed&&Math.random()<streetStopP()){const spots=[110,290,FR.door.x+(dir>0?-34:34)];if(projOn('terrace')&&(S.frontTables||0)>0)spots.push(FR.cols[0]+(dir>0?-46:46));w.stopX=pick(spots)}
 STREET.ppl.push(w)}
function streetJoin(w){if(R.closed||R.t>R.dur*.9||R.si>=R.sched.length)return false;const o=R.sched[R.si];if(o.reg||o.t-R.t>45||o.forSig)return false;if(queued().length>=queueMax()-1)return false;if(Math.random()>.6)return false;
 const spec=Object.assign({},o,{t:R.t,looks:o.size===w.n?w.looks:null,fromStreet:{x:w.x,y:w.y}});R.si++;spawn(spec);return true}
function streetUpd(dt){if(!R)return;const wet=streetWet();STREET.next-=dt;
 if(STREET.next<=0&&STREET.ppl.length<(wet?3:5)){streetSpawn();STREET.next=rand(5,13)*(wet?1.5:1)*(R.rush?.75:1)*(R.closed?1.6:1)}
 for(const w of STREET.ppl){w.t+=dt;
  if(w.st==='walk'){w.x+=w.dir*w.v*dt;w.walk+=dt*7.5;if(w.stopX!=null&&(w.dir>0?w.x>=w.stopX:w.x<=w.stopX)){w.st='look';w.t=0;w.dur=rand(1.8,3.6);w.stopX=null}
   if(w.dir>0?w.x>LW+BGM+44:w.x<-BGM-44)w.gone=true}
  else if(w.st==='look'&&w.t>=w.dur){if(streetJoin(w)){w.gone=true;R.st.walkins=(R.st.walkins||0)+1;if(!R.walkinNoted&&room!=='front'){R.walkinNoted=1;noteLine('有人在門口看了一下，走進來了。')}}else{w.st='walk';w.t=0;if(Math.random()<.25)w.dir=-w.dir}}}
 STREET.ppl=STREET.ppl.filter(w=>!w.gone);
 STREET.nextVeh-=dt;if(!STREET.veh&&STREET.nextVeh<=0){const dir=Math.random()<.5?1:-1;const scoot=Math.random()<.72;STREET.veh={x:dir>0?-BGM-70:LW+BGM+70,dir,v:scoot?rand(150,215):rand(70,100),kind:scoot?'scooter':'bike',y:rand(390,404),col:pick(['#C9413A','#2E6B4A','#F2EAD8','#3E4E66','#E0A43A']),helm:pick(['#F2EAD8','#2A2A2E','#C9413A','#5B6FB3']),box:scoot&&Math.random()<.5,boxCol:pick(['#2E9E6B','#E86A3A','#F4C44E']),look:makeLooks('office',1)[0],ph:Math.random()*6};STREET.nextVeh=rand(12,40)}
 if(STREET.veh){const v=STREET.veh;v.x+=v.dir*v.v*dt;v.ph+=dt*9;if(v.dir>0?v.x>LW+BGM+80:v.x<-BGM-80)STREET.veh=null}}
function drawUmbrella(c,x,y,col){c.save();c.translate(x,y);c.strokeStyle='#3A2E28';c.lineWidth=1.1;c.beginPath();c.moveTo(0,0);c.lineTo(0,-16);c.stroke();c.fillStyle=col;c.beginPath();c.moveTo(-17,-16);c.quadraticCurveTo(0,-34,17,-16);for(let k=17;k>-17;k-=6.8)c.quadraticCurveTo(k-3.4,-13,k-6.8,-16);c.closePath();c.fill();c.strokeStyle='rgba(60,34,22,.4)';c.lineWidth=.6;c.stroke();c.fillStyle='rgba(255,255,255,.2)';c.beginPath();c.moveTo(-13,-17);c.quadraticCurveTo(-9,-28,0,-31);c.quadraticCurveTo(-7,-26,-8,-17);c.fill();c.fillStyle='#3A2E28';circ(c,0,-33,1.2);c.restore()}
function drawDog(c,x,y,flip,ph,col){c.save();c.translate(x,y);c.scale(flip?-1:1,1);c.fillStyle='rgba(40,25,15,.16)';el(c,1,1,9,2.6);const OL='rgba(60,34,22,.5)';c.strokeStyle=OL;c.lineWidth=.6;
 c.fillStyle=shade(col,-.12);for(const [lx,k] of[[-5.5,0],[-2.5,3.1],[2.5,1.6],[5.5,4.7]]){const lift=Math.max(0,Math.sin(ph+k))*2;rr(c,lx-1.3,-7-lift*.2,2.6,7-lift,1.1);c.fill();c.stroke()}
 c.fillStyle=col;el(c,0,-9,8.6,4.8);c.stroke();circ(c,8.5,-12.5,4.2);c.fillStyle=shade(col,.14);el(c,11.6,-11.4,2.8,1.9);c.fillStyle='#2A2220';circ(c,13.4,-11.8,.9);circ(c,9.6,-13.6,.75);c.fillStyle=shade(col,-.2);c.save();c.translate(6,-15.5);c.rotate(-.5);el(c,0,0,1.9,3.2);c.restore();
 c.strokeStyle=col;c.lineWidth=2.2;c.lineCap='round';c.beginPath();c.moveTo(-8,-10);c.quadraticCurveTo(-12,-15+Math.sin(ph*1.7)*2,-10,-18);c.stroke();c.strokeStyle='#C9413A';c.lineWidth=1.2;c.beginPath();c.moveTo(4.6,-10.2);c.lineTo(5.4,-14.6);c.stroke();c.restore()}
function drawStreetWalker(c,w,now){const f=w.dir;const look=w.st==='look';
 w.looks.forEach((L0,k)=>{const off=(k-(w.n-1)/2)*12*f;drawPerson(c,w.x+off,w.y+(k%2)*2,L0,{step:look?0:Math.sin(w.walk+k),bob:look?0:Math.abs(Math.sin(w.walk+k))*-.8,mood:look?'happy':'ok',flip:f<0,gaze:look?{x:0,y:-.45}:null,blink:Math.sin(now*1.4+w.seed+k)>.97});
  if(w.umb&&k===0)drawUmbrella(c,w.x+off+f*3,w.y-30,w.umb)});
 if(w.dog){const dx=w.x-f*20;c.strokeStyle='rgba(60,45,35,.7)';c.lineWidth=.8;c.beginPath();c.moveTo(w.x-f*7,w.y-24);c.quadraticCurveTo(w.x-f*12,w.y-14,dx+f*4,w.y-13);c.stroke();drawDog(c,dx,w.y+2,f<0,look?0:w.walk*1.1,w.dogCol)}
 if(look){/* a little thought while they read the window */const t=w.t;if(t>.5){c.fillStyle='rgba(255,250,240,.95)';const bx=w.x+f*9,by=w.y-56;circ(c,bx,by,5.6);circ(c,bx-f*4,by+6,1.8);circ(c,bx-f*6.5,by+9.5,1.1);c.fillStyle='#2E2019';if(t>w.dur-.9){c.font=`800 8px ${FONT}`;c.textAlign='center';c.textBaseline='middle';c.fillText('!',bx,by+.5);c.textBaseline='alphabetic'}else{for(let i=-1;i<=1;i++)circ(c,bx+i*2.2,by+.3,.75)}}}}
function drawVehicle(c,v){const f=v.dir;c.save();c.translate(v.x,v.y);c.scale(f,1);c.fillStyle='rgba(20,15,10,.22)';el(c,0,2,22,4);
 if(v.kind==='scooter'){for(const wx of[-14,14]){c.fillStyle='#2A2A2E';circ(c,wx,-4.5,5.4);c.fillStyle='#8A8A90';circ(c,wx,-4.5,2.6);c.fillStyle='#2A2A2E';circ(c,wx,-4.5,1)}
  c.fillStyle=shade(v.col,-.2);c.fillRect(-14,-8,28,3);c.fillStyle=v.col;c.beginPath();c.moveTo(-17,-9);c.quadraticCurveTo(-19,-17,-8,-18);c.lineTo(3,-18);c.lineTo(6,-10);c.lineTo(15,-10);c.lineTo(16,-6);c.lineTo(-15,-6);c.closePath();c.fill();c.fillStyle='rgba(255,255,255,.22)';c.fillRect(-14,-16,12,1.6);
  c.fillStyle=v.col;c.beginPath();c.moveTo(11,-10);c.quadraticCurveTo(17,-20,15,-31);c.lineTo(18,-31);c.quadraticCurveTo(21,-18,14,-9);c.closePath();c.fill();c.strokeStyle='#2A2A2E';c.lineWidth=1.6;c.lineCap='round';c.beginPath();c.moveTo(16,-32);c.lineTo(8,-33);c.stroke();c.fillStyle='#F4E2B0';circ(c,19,-26,2.2);c.fillStyle='#C9413A';circ(c,-18,-12,1.4);
  c.fillStyle='#2A2220';rr(c,-13,-22,15,4.5,2);c.fill();if(v.box){c.fillStyle=v.boxCol;rr(c,-27,-33,15,14,2);c.fill();c.fillStyle='rgba(0,0,0,.12)';c.fillRect(-27,-22,15,3);c.fillStyle='rgba(255,255,255,.4)';c.fillRect(-25,-29,11,1.6)}}
 else{for(const wx of[-13,13]){c.strokeStyle='#2E2B33';c.lineWidth=1.6;c.beginPath();c.arc(wx,-6,7.5,0,7);c.stroke();c.beginPath();c.arc(wx,-6,1.6,0,7);c.stroke();for(let k=0;k<6;k++){c.beginPath();c.moveTo(wx,-6);c.lineTo(wx+Math.cos(k+v.ph*.3)*7,-6+Math.sin(k+v.ph*.3)*7);c.stroke()}}
  c.strokeStyle=v.col;c.lineWidth=2;c.beginPath();c.moveTo(-13,-6);c.lineTo(-3,-19);c.lineTo(11,-19);c.lineTo(13,-6);c.moveTo(-3,-19);c.lineTo(4,-8);c.lineTo(13,-6);c.moveTo(4,-8);c.lineTo(11,-19);c.stroke();c.fillStyle='#2A2220';rr(c,-7,-22,7,2.6,1);c.fill();c.strokeStyle='#2A2A2E';c.lineWidth=1.4;c.beginPath();c.moveTo(11,-19);c.lineTo(12,-26);c.lineTo(16,-27);c.stroke()}
 c.restore();
 const rx=v.x-f*(v.kind==='scooter'?4:2),ry=v.y-(v.kind==='scooter'?17:19);drawPerson(c,rx,ry,v.look,{seated:true,lounge:{legs:0},s:.8,flip:f<0,arms:[.75,.75],mood:'ok'});
 if(v.kind==='scooter'){c.save();c.translate(rx,ry-29*.8*PSC);c.fillStyle=v.helm;c.beginPath();c.arc(0,-.5,10.8,Math.PI,0);c.lineTo(10.8,3);c.lineTo(-10.8,3);c.closePath();c.fill();c.strokeStyle='rgba(60,34,22,.5)';c.lineWidth=.6;c.stroke();c.fillStyle='rgba(255,255,255,.28)';el(c,-4,-6,3.2,1.6);c.fillStyle='rgba(0,0,0,.2)';c.fillRect(-10.8,1.5,21.6,1.5);c.restore()}}
/* ================= kitchen render ================= */
const TRAYHIT={chips:[],ctrls:[],stage:null};
const inR=(h,x,y)=>x>=h.x&&x<=h.x+h.w&&y>=h.y&&y<=h.y+h.h;
function wsRect(){return{x:0,y:0,w:TL.W,h:TL.WS}}
function wsText(c,txt,x,y,font,col,align,base,maxW){c.font=font;c.fillStyle=col;c.textAlign=align||'left';c.textBaseline=base||'alphabetic';txt=String(txt);if(maxW&&c.measureText(txt).width>maxW){while(txt.length>1&&c.measureText(txt+'…').width>maxW)txt=txt.slice(0,-1);txt+='…'}c.fillText(txt,x,y)}
function shade(h,a){return a>0?mix(h,'#FFFFFF',a):mix(h,'#000000',-a)}
function drawTray(now){const c=tctx;const W=tc.width/DPR,H=tc.height/DPR;c.setTransform(DPR,0,0,DPR,0,0);let g=c.createLinearGradient(0,0,0,H);g.addColorStop(0,'#1B2326');g.addColorStop(1,'#12181A');c.fillStyle=g;c.fillRect(0,0,W,H);
 TRAYHIT.chips=[];TRAYHIT.ctrls=[];TRAYHIT.stage=null;const V=view();const n=V.slots.length;const fi=R?clamp(R.focus||0,0,Math.max(0,n-1)):0;
 if(V.slots[fi])drawWorkspace(c,V.slots[fi],wsRect(),now)}
function instrText(j,k){switch(k.t){case'add':return k.txt;case'tap':return`連點「${k.verb}」${k.heat?'，停太久會焦':''}`;case'zone':return`看準時機「${k.verb}」`+(k.c==='want'?`（要 ${STEAK_W[j.it.want]}）`:'');case'hold':return`按住「${k.verb}」，在金色區間放開`;case'dose':return`${k.verb} ${k.min===k.max?k.min:k.min+'–'+k.max} 下，再按完成`;case'wait':return`${k.verb}中…可以先去做別的`;case'work':return`Jill 正在${k.verb}…可以先去做別的`}return''}
function drawWorkspace(c,s,r,now){const j=s.job;const k=j&&j.step;const pulse=(Math.sin(now*7)+1)/2;
 c.save();rr(c,r.x,r.y,r.w,r.h,14);c.clip();const split=r.y+r.h*.52;
 c.fillStyle='#E7DFD0';c.fillRect(r.x,r.y,r.w,split-r.y);c.strokeStyle='rgba(120,100,80,.2)';c.lineWidth=1;for(let yy=r.y+38,row=0;yy<split;yy+=11,row++){c.beginPath();c.moveTo(r.x,yy);c.lineTo(r.x+r.w,yy);c.stroke();for(let xx=r.x+(row%2?11:0);xx<r.x+r.w;xx+=22){c.beginPath();c.moveTo(xx,yy);c.lineTo(xx,Math.min(split,yy+11));c.stroke()}}
 let lg=c.createRadialGradient(r.x+r.w*.25,r.y+40,10,r.x+r.w*.25,r.y+40,r.w*.7);lg.addColorStop(0,'rgba(255,196,120,.32)');lg.addColorStop(1,'rgba(255,196,120,0)');c.fillStyle=lg;c.fillRect(r.x,r.y,r.w,r.h);
 let sg=c.createLinearGradient(0,split,0,r.y+r.h);sg.addColorStop(0,'#C3CACD');sg.addColorStop(.1,'#A2ACB0');sg.addColorStop(1,'#6A7478');c.fillStyle=sg;c.fillRect(r.x,split,r.w,r.y+r.h-split);c.fillStyle='rgba(255,255,255,.55)';c.fillRect(r.x,split,r.w,1.5);c.strokeStyle='rgba(255,255,255,.07)';for(let xx=r.x-40;xx<r.x+r.w;xx+=4){c.beginPath();c.moveTo(xx,split+2);c.lineTo(xx+30,r.y+r.h);c.stroke()}
 let hg=c.createLinearGradient(0,r.y,0,r.y+38);hg.addColorStop(0,'rgba(34,24,18,.97)');hg.addColorStop(1,'rgba(46,32,24,.94)');c.fillStyle=hg;c.fillRect(r.x,r.y,r.w,38);c.fillStyle='#C99A45';c.fillRect(r.x,r.y+38,r.w,1.2);
 const sw=Math.min(180,r.w*.47);const st={x:r.x+2,y:r.y+40,w:sw,h:r.h-42};const ct={x:r.x+sw+8,y:r.y+48,w:r.w-sw-16,h:r.h-56};
 if(!j){wsText(c,`${ST_N[s.type]}${s.type==='stove'||s.no>1?' '+s.no:''}`,r.x+12,r.y+18,`400 14px ${DFONT}`,'#FFF3DA');wsText(c,R?'這個工作台目前空著':'開店後，料理會在這裡一步一步完成',r.x+12,r.y+33,`700 10.5px ${FONT}`,'rgba(247,237,220,.7)','left','alphabetic',r.w-24)}
 else{const D=DISH(j.d);const steps=recipeOf(j.d);c.fillStyle='#FFF8EC';rr(c,r.x+8,r.y+6,24,14,4);c.fill();wsText(c,'T'+j.tk.no,r.x+20,r.y+13.5,`800 9px ${FONT}`,'#2E2019','center','middle');
  wsText(c,D.n,r.x+38,r.y+18,`400 14px ${DFONT}`,'#FFF3DA','left','alphabetic',r.w-70-steps.length*12);
  c.fillStyle='rgba(255,255,255,.14)';circ(c,r.x+r.w-16,r.y+14,10);c.strokeStyle='#FFF3DA';c.lineWidth=1.8;c.beginPath();c.moveTo(r.x+r.w-20,r.y+10);c.lineTo(r.x+r.w-12,r.y+18);c.moveTo(r.x+r.w-12,r.y+10);c.lineTo(r.x+r.w-20,r.y+18);c.stroke();TRAYHIT.ctrls.push({x:r.x+r.w-32,y:r.y,w:32,h:30,act:'close'});
  for(let i=0;i<steps.length;i++){const dx=r.x+r.w-38-(steps.length-1-i)*12;const done=i<j.si,cur=i===j.si;c.fillStyle=done?'#E6C27A':cur?'#FFF3DA':'rgba(255,255,255,.2)';circ(c,dx,r.y+13,cur?3.6:2.8);if(cur){c.strokeStyle='#E6C27A';c.lineWidth=1.2;c.beginPath();c.arc(dx,r.y+13,6,0,7);c.stroke()}}
  const urgent=j.overStart!=null;wsText(c,(urgent?`快！${j.overVerb}過頭中 · `:`${j.si+1}/${steps.length} · `)+instrText(j,k),r.x+12,r.y+33,`700 11px ${FONT}`,urgent?`rgb(255,${Math.round(140+pulse*60)},110)`:'rgba(247,237,220,.9)','left','alphabetic',r.w-24)}
 drawStage(c,s,j,st.x,st.y,st.w,st.h,now);TRAYHIT.stage=st;
 c.fillStyle='rgba(34,26,20,.8)';rr(c,ct.x-5,ct.y-5,ct.w+10,ct.h+10,12);c.fill();
 if(j)drawControls(c,s,j,k,ct,now);else drawIdleControls(c,s,ct,now);
 if(s.fx){const a=1-s.fx.t;c.globalAlpha=Math.max(0,a);c.font=`800 ${s.fx.txt.length>5?13:16}px ${FONT}`;c.textAlign='center';c.textBaseline='middle';c.lineWidth=3.5;c.strokeStyle='rgba(20,15,10,.85)';const fx=st.x+st.w/2,fy=st.y+22-s.fx.t*14;c.strokeText(s.fx.txt,fx,fy);c.fillStyle=s.fx.col;c.fillText(s.fx.txt,fx,fy);c.globalAlpha=1}
 if(s.burst){s.burst.t+=1/60;const t=s.burst.t;if(t>.9)s.burst=null;else{const bx=st.x+st.w/2,by=st.y+st.h*.55;for(let i=0;i<14;i++){const a=i/14*6.28;const d=14+t*70;c.fillStyle=`rgba(255,225,120,${1-t/.9})`;c.save();c.translate(bx+Math.cos(a)*d,by+Math.sin(a)*d*.6);c.rotate(t*5);c.fillRect(-4,-.8,8,1.6);c.fillRect(-.8,-4,1.6,8);c.restore()}}}
 c.restore()}
function paperBtn(c,x,y,w,h,opt){const pulse=(Math.sin(performance.now()/1000*7)+1)/2;const st=opt.style||'paper';
 c.fillStyle='rgba(0,0,0,.35)';rr(c,x,y+2.5,w,h,10);c.fill();
 if(st==='gold'){let g=c.createLinearGradient(0,y,0,y+h);g.addColorStop(0,'#EDC878');g.addColorStop(1,'#BE8A35');c.fillStyle=g}else if(st==='hot'){let g=c.createLinearGradient(0,y,0,y+h);g.addColorStop(0,'#F4946A');g.addColorStop(1,'#C24A2A');c.fillStyle=g}else if(st==='dim')c.fillStyle='rgba(255,248,236,.32)';else c.fillStyle='#FFF8EC';
 rr(c,x,y,w,h,10);c.fill();if(opt.glow){c.strokeStyle=`rgba(255,232,150,${.45+pulse*.55})`;c.lineWidth=2.5;rr(c,x-1.5,y-1.5,w+3,h+3,11.5);c.stroke()}
 c.fillStyle='rgba(255,255,255,.35)';rr(c,x+4,y+2.5,w-8,Math.min(5,h/5),3);c.fill();
 if(opt.hit)TRAYHIT.ctrls.push(Object.assign({x,y,w,h},opt.hit))}
function drawControls(c,s,j,k,r,now){const ink='#2E2019';
 switch(k.t){
 case'add':{const b=k.btns;const n=b.length;const cols=n<=2?1:2;const rows=Math.ceil(n/cols);const gap=6;const bw=(r.w-gap*(cols-1))/cols;const bh=Math.min(54,(r.h-gap*(rows-1))/rows);const y0=r.y+(r.h-(bh*rows+gap*(rows-1)))/2;
  b.forEach((id,i)=>{const col=i%cols,row=Math.floor(i/cols);const x=r.x+col*(bw+gap),y=y0+row*(bh+gap);const done=k.items.includes(id)&&!k.left.includes(id);const hint=S.day<=2&&!done&&(k.order?k.left[0]===id:k.left.includes(id));
   paperBtn(c,x,y,bw,bh,{style:done?'dim':'paper',glow:hint,hit:done?null:{act:'ing',arg:id,s}});const ir=Math.min(15,bh*.33);drawIng(c,id,x+8+ir,y+bh/2+1,ir);wsText(c,ING[id].n,x+16+ir*2,y+bh/2+4.5,`800 ${bw>96?13:11.5}px ${FONT}`,done?'rgba(46,32,25,.45)':ink,'left','alphabetic',bw-ir*2-22);
   if(done){c.fillStyle='#5E8F4E';circ(c,x+bw-10,y+10,6.5);c.strokeStyle='#fff';c.lineWidth=1.6;c.beginPath();c.moveTo(x+bw-13,y+10);c.lineTo(x+bw-10.5,y+12.5);c.lineTo(x+bw-6.5,y+7.5);c.stroke()}});break}
 case'dose':{const bh=Math.min(56,r.h*.44);paperBtn(c,r.x,r.y,r.w,bh,{style:'paper',hit:{act:'dose',s}});drawIng(c,k.ing,r.x+24,r.y+bh/2+1,14);wsText(c,k.verb,r.x+46,r.y+bh/2-1,`800 13.5px ${FONT}`,ink,'left','alphabetic',r.w-90);wsText(c,'點一下加一次',r.x+46,r.y+bh/2+13,`600 10px ${FONT}`,'#8A7462');wsText(c,'×'+k.cnt,r.x+r.w-10,r.y+bh/2+8,`400 22px ${DFONT}`,ink,'right');
  const py=r.y+bh+9;const N=k.max+2;const pw=(r.w-(N-1)*4)/N;for(let i=0;i<N;i++){const inT=i+1>=k.min&&i+1<=k.max;c.fillStyle=i<k.cnt?(inT?'#7DB86A':'#E0A43A'):inT?'rgba(230,194,122,.55)':'rgba(255,255,255,.16)';rr(c,r.x+i*(pw+4),py,pw,8,4);c.fill()}
  const ok=k.cnt>=k.min&&k.cnt<=k.max;const dy=py+15,dh=Math.max(28,r.y+r.h-dy);paperBtn(c,r.x,dy,r.w,dh,{style:ok?'gold':'paper',glow:ok,hit:{act:'doseDone',s}});wsText(c,'完成',r.x+r.w/2,dy+dh/2+5,`800 14px ${FONT}`,ink,'center');break}
 case'tap':{const heat=k.heat;const bh=r.h-(heat?22:14);const idle=heat&&R.t-k.last>.55;paperBtn(c,r.x,r.y,r.w,bh,{style:idle?'hot':'gold',glow:true,hit:{act:'tap',s}});wsText(c,'連點',r.x+r.w/2,r.y+bh/2-7,`700 11px ${FONT}`,'rgba(46,32,25,.7)','center');wsText(c,k.verb+'！',r.x+r.w/2,r.y+bh/2+14,`400 20px ${DFONT}`,ink,'center');
  const py=r.y+bh+6;c.fillStyle='rgba(255,255,255,.12)';rr(c,r.x,py,r.w,6,3);c.fill();c.fillStyle='#F4C44E';rr(c,r.x,py,r.w*k.taps/k.n,6,3);c.fill();if(heat){c.fillStyle='rgba(255,255,255,.12)';rr(c,r.x,py+9,r.w,5,2.5);c.fill();c.fillStyle=k.scorch>.5?'#E0543A':'#E08A3A';rr(c,r.x,py+9,r.w*Math.min(1,k.scorch),5,2.5);c.fill()}break}
 case'zone':{const gy=r.y+2,gh=16;const X=v=>r.x+r.w*clamp(v/1.3,0,1);c.fillStyle='#10171A';rr(c,r.x,gy,r.w,gh,8);c.fill();c.save();rr(c,r.x,gy,r.w,gh,8);c.clip();c.fillStyle='#4E5A60';c.fillRect(X(.3),gy,X(1)-X(.3),gh);c.fillStyle='#6E9A5E';c.fillRect(X(k.z.c-k.z.g),gy,X(k.z.c+k.z.g)-X(k.z.c-k.z.g),gh);c.fillStyle='#F4C44E';c.fillRect(X(k.z.c-k.z.w),gy,X(k.z.c+k.z.w)-X(k.z.c-k.z.w),gh);c.fillStyle='#8A5A3A';c.fillRect(X(1),gy,X(1.22)-X(1),gh);c.fillStyle='#8A2A18';c.fillRect(X(1.22),gy,r.x+r.w-X(1.22),gh);c.restore();
  let lab=0;if(k.c==='want'){lab=12;[.52,.66,.8,.93].forEach((v,i)=>wsText(c,STEAK_S[i],X(v),gy+gh+10,`800 8.5px ${FONT}`,i===j.it.want?'#FFE38A':'rgba(247,237,220,.45)','center'))}
  const px=X(Math.min(k.p,1.3));c.fillStyle='#fff';c.fillRect(px-1.3,gy-3,2.6,gh+6);c.beginPath();c.moveTo(px,gy-3);c.lineTo(px-4.5,gy-8);c.lineTo(px+4.5,gy-8);c.fill();
  const q=zoneQ(k.p,k.z);const ready=q==='P'||q==='G';const by=gy+gh+8+lab,bh=r.y+r.h-by;paperBtn(c,r.x,by,r.w,bh,{style:k.p>=1?'hot':ready?'gold':'paper',glow:ready||k.p>=1,hit:{act:'zone',s}});wsText(c,k.p>=1.22?'快！要焦了':k.p>=1?'有點過了，快起鍋':ready?'就是現在！':k.p<k.z.c-k.z.g?'再等一下…':'',r.x+r.w/2,by+15,`800 10px ${FONT}`,'rgba(46,32,25,.65)','center');wsText(c,k.verb,r.x+r.w/2,by+bh/2+10,`400 21px ${DFONT}`,ink,'center');break}
 case'hold':{const gy=r.y+2,gh=16;const lv=Math.min(1.05,k.level);c.fillStyle='#10171A';rr(c,r.x,gy,r.w,gh,8);c.fill();c.save();rr(c,r.x,gy,r.w,gh,8);c.clip();c.fillStyle='rgba(244,196,78,.3)';c.fillRect(r.x+r.w*k.a,gy,r.w*(k.b-k.a),gh);let col=k.ing==='beans'?'#8A5A30':(ING[k.ing]||{}).c||'#ccc';if(col==='#FFFFFF'||col==='#FFF8E8')col='#EDE7DC';c.fillStyle=col;c.fillRect(r.x,gy+3,r.w*Math.min(1,lv),gh-6);c.restore();c.strokeStyle='#F4C44E';c.lineWidth=1.5;c.strokeRect(r.x+r.w*k.a,gy,r.w*(k.b-k.a),gh);
  const inB=lv>=k.a&&lv<=k.b;wsText(c,k.unit==='溫度'?`${Math.round(lv*80)}°C`:k.unit==='研磨度'?(lv<.05?'':lv<k.a?'還太粗':lv>k.b?'太細了':'剛好'):`${Math.round(lv*100)}%`,r.x+r.w,gy+gh+12,`800 10px ${FONT}`,inB?'#FFE38A':'rgba(247,237,220,.8)','right');
  const by=gy+gh+17,bh=r.y+r.h-by;paperBtn(c,r.x,by,r.w,bh,{style:k.hold?(inB?'gold':k.level>k.b?'hot':'paper'):'paper',glow:k.hold&&inB,hit:{act:'hold',s}});wsText(c,k.hold?(inB?'放開！':k.level>k.b?'快放開！':'按住…'):'按住不放',r.x+r.w/2,by+15,`800 10px ${FONT}`,'rgba(46,32,25,.65)','center');wsText(c,k.verb,r.x+r.w/2,by+bh/2+10,`400 19px ${DFONT}`,ink,'center','alphabetic',r.w-50);drawIng(c,k.ing,r.x+20,by+bh/2+3,11);break}
 case'work':{const cx=r.x+r.w/2,cy=r.y+r.h/2-8;const RR=Math.min(32,r.h/2-14);c.strokeStyle='rgba(255,255,255,.14)';c.lineWidth=6;c.beginPath();c.arc(cx,cy,RR,0,7);c.stroke();c.strokeStyle='#E6C27A';c.lineCap='round';c.beginPath();c.arc(cx,cy,RR,-Math.PI/2,-Math.PI/2+Math.min(1,k.p)*6.283);c.stroke();c.lineCap='butt';
  const a=Math.sin(now*14)*.35;c.save();c.translate(cx,cy+2);c.rotate(k.board?-.5+a:a*.6);c.fillStyle='#E9E6E0';if(k.board){rr(c,-2,-16,4,18,1.5);c.fill();c.fillStyle='#6B4A2E';rr(c,-2.5,2,5,9,1.5);c.fill()}else{c.strokeStyle='#C9CED0';c.lineWidth=2.4;c.beginPath();c.moveTo(0,-14);c.lineTo(0,10);c.stroke();c.fillStyle='#C9CED0';el(c,0,12,6,3)}c.restore();
  wsText(c,'Jill 正在'+k.verb,cx,cy+RR+15,`700 11px ${FONT}`,'rgba(247,237,220,.9)','center');wsText(c,'可以先去做別的',cx,cy+RR+28,`600 9.5px ${FONT}`,'rgba(247,237,220,.6)','center');break}
 case'wait':{const cx=r.x+r.w/2,cy=r.y+r.h/2-8;const RR=Math.min(32,r.h/2-14);c.strokeStyle='rgba(255,255,255,.14)';c.lineWidth=6;c.beginPath();c.arc(cx,cy,RR,0,7);c.stroke();c.strokeStyle='#8FC3DB';c.lineCap='round';c.beginPath();c.arc(cx,cy,RR,-Math.PI/2,-Math.PI/2+Math.min(1,k.p)*6.283);c.stroke();c.lineCap='butt';const left=Math.max(0,(1-k.p)*k.time/dishSpeed(j.d,s.type));wsText(c,left.toFixed(1)+'s',cx,cy+6,`400 17px ${DFONT}`,'#FFF3DA','center');wsText(c,k.verb+'中',cx,cy+RR+15,`700 11px ${FONT}`,'rgba(247,237,220,.9)','center');if(k.over)wsText(c,'好了要記得回來',cx,cy+RR+28,`600 9.5px ${FONT}`,'rgba(255,200,140,.9)','center');break}
 }}
function drawIdleControls(c,s,r,now){const n=R?nextPendingFor(s.type):null;if(n){const bh=Math.min(70,r.h);const y=r.y+(r.h-bh)/2;paperBtn(c,r.x,y,r.w,bh,{style:'gold',glow:true,hit:{act:'start',s}});c.drawImage(dishCanvas(n.it.d,'G',64,false,n.it.want),r.x+6,y+bh/2-22,44,44);wsText(c,'開始製作',r.x+56,y+bh/2-5,`800 10.5px ${FONT}`,'rgba(46,32,25,.7)');wsText(c,DISH(n.it.d).n,r.x+56,y+bh/2+13,`400 14px ${DFONT}`,'#2E2019','left','alphabetic',r.w-62)}
 else{wsText(c,R?'等待訂單':'打烊中',r.x+r.w/2,r.y+r.h/2-4,`400 16px ${DFONT}`,'#FFF3DA','center');wsText(c,R?'點上方訂單的料理開始':'開店後在這裡做菜',r.x+r.w/2,r.y+r.h/2+15,`600 10.5px ${FONT}`,'rgba(247,237,220,.7)','center')}}
function drawStage(c,s,j,x,y,w,h,now){const D=j?DISH(j.d):null;const k=j?j.step:null;const board=k&&((k.t==='tap'&&!k.heat)||(k.t==='work'&&k.board));const cx=x+w/2,cy=y+h*.58;const sc=Math.min(w/118,h/96);const active=!!j;
 if(s.type==='stove'){const gy=cy+16*sc;c.fillStyle='rgba(0,0,0,.35)';el(c,cx,gy+6*sc,50*sc,12*sc);c.fillStyle='#17191A';el(c,cx,gy,46*sc,11.5*sc);c.strokeStyle='#4A4E50';c.lineWidth=2*sc;c.beginPath();c.ellipse(cx,gy,36*sc,9*sc,0,0,7);c.stroke();c.lineWidth=1.2*sc;for(let a=0;a<6;a++){c.beginPath();c.moveTo(cx+Math.cos(a)*14*sc,gy+Math.sin(a)*3.4*sc);c.lineTo(cx+Math.cos(a)*42*sc,gy+Math.sin(a)*10.4*sc);c.stroke()}
  if(active&&!board){for(let i=0;i<16;i++){const a=i/16*6.283+now*2.5;const fl=(4+Math.sin(now*22+i*1.7)*1.8)*sc;const px=cx+Math.cos(a)*16*sc,py=gy+Math.sin(a)*4*sc;c.fillStyle=i%3?'rgba(90,140,255,.9)':'rgba(255,180,80,.8)';el(c,px,py-fl*.6,1.7*sc,fl)}let hg=c.createRadialGradient(cx,gy,2,cx,gy,56*sc);hg.addColorStop(0,'rgba(255,140,60,.28)');hg.addColorStop(1,'rgba(255,140,60,0)');c.fillStyle=hg;c.fillRect(x,y,w,h)}}
 else if(s.type==='oven'){c.fillStyle='#34302D';rr(c,x+6,y+4,w-12,h-8,8);c.fill();let og=c.createLinearGradient(0,y,0,y+h);og.addColorStop(0,active?'#5A2E18':'#262220');og.addColorStop(1,active?'#8A4418':'#1E1A18');c.fillStyle=og;rr(c,x+12,y+10,w-24,h-20,5);c.fill();if(active){c.strokeStyle=`rgba(255,${Math.round(120+Math.sin(now*4)*30)},50,.9)`;c.lineWidth=2;for(const yy of[y+16,y+h-18]){c.beginPath();for(let xx=x+18;xx<x+w-18;xx+=8)c.lineTo(xx,yy+(Math.round(xx/8)%2?2:-2));c.stroke()}}c.strokeStyle='rgba(200,200,200,.35)';c.lineWidth=1.2;c.beginPath();c.moveTo(x+14,cy+16*sc);c.lineTo(x+w-14,cy+16*sc);c.stroke()}
 else if(s.type==='bar'){let b2=c.createLinearGradient(x,0,x+w,0);b2.addColorStop(0,'#9E7026');b2.addColorStop(.5,'#EFCB80');b2.addColorStop(1,'#95691F');c.fillStyle=b2;rr(c,x+w*.16,y+2,w*.68,24,6);c.fill();c.fillStyle='#2A2A2A';rr(c,cx-16,y+24,32,7,2);c.fill();c.fillStyle='#555';c.fillRect(cx-3,y+31,6,5);c.fillStyle='#8FD3F4';circ(c,cx-18,y+13,2.2);circ(c,cx,y+13,2.2);circ(c,cx+18,y+13,2.2);c.fillStyle='#3A3F42';rr(c,x+w*.12,y+h-12,w*.76,8,3);c.fill()}
 else{c.fillStyle='rgba(0,0,0,.25)';el(c,cx,cy+24*sc,54*sc,11*sc);let mg=c.createLinearGradient(0,cy,0,cy+30*sc);mg.addColorStop(0,'#F4F1EC');mg.addColorStop(1,'#D6CFC4');c.fillStyle=mg;el(c,cx,cy+18*sc,52*sc,13*sc);c.strokeStyle='rgba(150,140,130,.35)';c.lineWidth=.8;c.beginPath();c.moveTo(cx-40*sc,cy+14*sc);c.quadraticCurveTo(cx,cy+22*sc,cx+36*sc,cy+12*sc);c.stroke()}
 if(!j)return;
 const vy=s.type==='bar'?y+h-16-24*sc:cy;const vs=s.type==='oven'?sc*.92:D.v==='glass'?sc*.9:sc;drawStageFood(c,s,j,cx,vy,vs,now)}
/* the vessel with whatever is in it right now, at (cx,vy) and scale vs: the board while chopping, the pour of a hold,
   the spit of a sear, the steam, the ingredient that just went in. Used by the tray and by the kitchen. */
function drawStageFood(c,s,j,cx,vy,vs,now){const D=DISH(j.d);const k=j.step;const board=k&&((k.t==='tap'&&!k.heat)||(k.t==='work'&&k.board));
 c.save();c.translate(cx,vy);c.scale(vs,vs);if(s.shake)c.translate(Math.sin(now*70)*s.shake*2,0);
 if(board)drawBoard(c,j,k,now,s);else{drawVesselBack(c,D.v);if(s.flipT>0){/* the flip: contents hop and turn over */const u=1-s.flipT/.42;c.save();c.translate(0,-Math.sin(u*Math.PI)*14);c.scale(1,Math.max(.12,Math.abs(Math.cos(u*Math.PI))));drawContents(c,j,D.v,now);c.restore()}else drawContents(c,j,D.v,now);drawVesselFront(c,D.v);
  if(k&&k.t==='zone'&&D.pan&&k.p>.3){/* fat spitting while it sears */for(let i=0;i<5;i++){const ph=(now*1.5+i*.21)%1;c.globalAlpha=(1-ph)*.85;c.fillStyle=i%2?'#FFF1B0':'#FFD27A';circ(c,-26+i*13+Math.sin(now*9+i*2)*3,-12-ph*24,1.6-ph)}c.globalAlpha=1}}
 if(k&&k.t==='hold'&&k.hold){let col=k.ing==='beans'?'#6B3A1A':(ING[k.ing]||{}).c||'#ccc';if(col==='#FFFFFF')col='#F2EEE6';const bot=D.v==='glass'?29-76*Math.min(1,k.level):D.v==='cup'?-9:D.v==='mold'?17-32*Math.min(1,k.level):D.v==='ramekin'?-10:D.v==='pot'?-16:-2;c.globalAlpha=.9;c.fillStyle=col;const wob=Math.sin(now*30)*.6;rr(c,-2.6+wob,-95,5.2,bot+95,2.6);c.fill();c.globalAlpha=1;if(k.ing==='milk'){for(let i=0;i<3;i++){const ph=(now*1.4+i*.33)%1;c.globalAlpha=(1-ph)*.5;c.fillStyle='#fff';circ(c,-10+i*10,-20-ph*30,4+ph*6)}c.globalAlpha=1}}
 const smoky=(k&&k.t==='tap'&&k.heat&&k.scorch>.45)||(k&&k.t==='zone'&&k.p>1);const steamy=smoky||(s.type==='stove'&&!board)||(k&&k.t==='wait'&&(D.v==='cup'||D.v==='pot'));
 if(steamy){for(let i=0;i<4;i++){const ph=(now*.7+i*.25)%1;c.globalAlpha=(1-ph)*(smoky?.55:.3);c.fillStyle=smoky?'#555':'#fff';circ(c,-18+i*12+Math.sin(now*2+i)*4,-26-ph*40,5+ph*8)}c.globalAlpha=1}
 if(s.pop&&s.pop.t<.5){const t=s.pop.t/.5;c.globalAlpha=1-t;drawIng(c,s.pop.id,0,-50+t*36,12);c.globalAlpha=1}
 c.restore()}
function drawBoard(c,j,k,now,s){c.fillStyle='rgba(0,0,0,.28)';el(c,2,18,54,12);c.fillStyle='#9A6534';rr(c,-52,-8,104,26,7);c.fill();c.fillStyle='#C8965E';rr(c,-52,-14,104,26,7);c.fill();c.strokeStyle='rgba(120,70,30,.25)';c.lineWidth=.8;for(let i=0;i<4;i++){c.beginPath();c.moveTo(-46,-9+i*6);c.quadraticCurveTo(0,-7+i*6,46,-10+i*6);c.stroke()}
 const p=k.taps/k.n;const R0=rng(j.seed);
 const jd=baseOf(j.d);if(jd==='duck'){c.fillStyle='#E39292';el(c,-6,-1,30,12);c.fillStyle='#F3DCC0';el(c,-6,-3,28,9.5);c.strokeStyle='rgba(150,90,60,.85)';c.lineWidth=1.2;for(let i=0;i<k.taps;i++){const off=-20+i*(36/Math.max(1,k.n-1));c.beginPath();c.moveTo(off-5,-11);c.lineTo(off+5,4);c.stroke();c.beginPath();c.moveTo(off+5,-11);c.lineTo(off-5,4);c.stroke()}}
 else if(jd==='souffle'){c.fillStyle='#F4F0EA';c.beginPath();c.moveTo(-26,-10);c.quadraticCurveTo(-24,14,0,14);c.quadraticCurveTo(24,14,26,-10);c.fill();c.fillStyle='#E4DCCF';el(c,0,-10,26,7);c.fillStyle='#FFFFFF';const f=4+p*10;for(let i=0;i<7;i++)circ(c,-16+i*5.4,-11-Math.sin(i*1.3)*f*.35,3.5+f*.3);const a=Math.sin(now*20)*(s.shake||0)*.6;c.save();c.translate(12,-14);c.rotate(-.6+a);c.strokeStyle='#C9CED0';c.lineWidth=1.2;for(let i=-2;i<=2;i++){c.beginPath();c.ellipse(i*1.5,-8,3,9,0,0,7);c.stroke()}c.fillStyle='#8A5A30';c.fillRect(-1.5,-30,3,14);c.restore()}
 else{const cols=jd==='salad'?['#7CBF4A','#D8392A','#9AC66A']:['#4E7F2E','#D6392E','#F2BE2E'];const whole=Math.max(0,3-Math.floor(p*3));for(let i=0;i<whole;i++){c.fillStyle=cols[i];el(c,-36+i*11,-3,7.5,5.5);gloss(c,-38+i*11,-5,2.5,1.2,.4)}const pieces=Math.floor(p*16);for(let i=0;i<pieces;i++){c.fillStyle=cols[i%3];c.save();c.translate(2+R0()*40,-11+R0()*15);c.rotate(R0()*3);c.fillRect(-2.6,-1.8,5.2,3.6);c.restore()}}
 if(jd!=='souffle'){const lift=(s.shake||0)*10;c.save();c.translate(-8,-18-lift);c.rotate(-.12);let kg=c.createLinearGradient(0,-8,0,6);kg.addColorStop(0,'#F4F6F7');kg.addColorStop(1,'#9AA4A8');c.fillStyle=kg;c.beginPath();c.moveTo(-20,4);c.lineTo(18,4);c.lineTo(18,-4);c.quadraticCurveTo(-6,-11,-20,4);c.fill();c.fillStyle='#3A2A20';rr(c,18,-3,17,7,3);c.fill();c.fillStyle='#C99A45';circ(c,23,.5,1);circ(c,30,.5,1);c.restore()}}
function drawVesselBack(c,v){let g;switch(v){
 case'wok':c.fillStyle='rgba(0,0,0,.3)';el(c,0,10,50,16);c.fillStyle='#6B3A22';rr(c,40,-6,34,7,3);c.fill();c.fillStyle='#8A5230';c.fillRect(44,-5,26,2);c.fillStyle='#1E1E20';el(c,0,3,48,23);g=c.createRadialGradient(-10,-6,4,0,0,44);g.addColorStop(0,'#58585F');g.addColorStop(1,'#26262A');c.fillStyle=g;el(c,0,0,44,19);break;
 case'pan':case'griddle':c.fillStyle='rgba(0,0,0,.3)';el(c,0,10,50,15);c.fillStyle='#2A2A2C';rr(c,38,-4,36,7,3.5);c.fill();c.fillStyle='#46464C';c.fillRect(40,-3,30,1.5);c.fillStyle='#1B1B1D';el(c,0,3,46,21);g=c.createRadialGradient(-8,-6,4,0,0,42);g.addColorStop(0,'#4C4C52');g.addColorStop(1,'#2A2A2E');c.fillStyle=g;el(c,0,0,42,18);break;
 case'pot':c.fillStyle='rgba(0,0,0,.3)';el(c,0,28,44,10);g=c.createLinearGradient(-36,0,36,0);g.addColorStop(0,'#8C979C');g.addColorStop(.4,'#E8ECEE');g.addColorStop(1,'#7C878C');c.fillStyle=g;c.beginPath();c.moveTo(-36,-16);c.lineTo(36,-16);c.lineTo(34,24);c.ellipse(0,24,34,8,0,0,Math.PI);c.closePath();c.fill();c.fillStyle='#9AA4A8';rr(c,-49,-13,13,6,3);c.fill();rr(c,36,-13,13,6,3);c.fill();c.fillStyle='#CDD4D7';el(c,0,-16,36,11);c.fillStyle='#6E787C';el(c,0,-16,33,9.5);break;
 case'tray':c.fillStyle='rgba(0,0,0,.35)';el(c,0,16,56,10);c.fillStyle='#7C868A';rr(c,-52,-20,104,40,4);c.fill();c.fillStyle='#B4BCBF';rr(c,-49,-17,98,34,3);c.fill();c.fillStyle='#EFE6D2';rr(c,-45,-15,90,30,2);c.fill();break;
 case'cup':c.fillStyle='rgba(0,0,0,.25)';el(c,0,26,34,8);c.fillStyle='#F4EFE6';el(c,0,22,32,9);c.fillStyle='#FFFFFF';el(c,0,20,28,7);c.strokeStyle='#F1ECE3';c.lineWidth=5;c.beginPath();c.arc(24,4,8,-1.2,1.3);c.stroke();g=c.createLinearGradient(-22,0,22,0);g.addColorStop(0,'#E6DFD3');g.addColorStop(.4,'#FFFFFF');g.addColorStop(1,'#D6CEC0');c.fillStyle=g;c.beginPath();c.moveTo(-22,-10);c.lineTo(22,-10);c.quadraticCurveTo(20,20,0,20);c.quadraticCurveTo(-20,20,-22,-10);c.fill();c.fillStyle='#F7F3EC';el(c,0,-10,22,7);c.fillStyle='#EAE3D6';el(c,0,-9.5,19.5,5.6);break;
 case'glass':c.fillStyle='rgba(0,0,0,.25)';el(c,0,32,24,6);c.fillStyle='rgba(220,235,240,.2)';c.beginPath();c.moveTo(-19,-46);c.lineTo(19,-46);c.lineTo(15,30);c.lineTo(-15,30);c.closePath();c.fill();break;
 case'bowl':c.fillStyle='rgba(0,0,0,.28)';el(c,0,24,40,9);g=c.createLinearGradient(-40,0,40,0);g.addColorStop(0,'#D6CDBE');g.addColorStop(.4,'#FFFFFF');g.addColorStop(1,'#CCC2B2');c.fillStyle=g;c.beginPath();c.moveTo(-42,-8);c.quadraticCurveTo(-38,24,0,24);c.quadraticCurveTo(38,24,42,-8);c.fill();c.fillStyle='#F7F3EC';el(c,0,-8,42,13);c.fillStyle='#E6DED0';el(c,0,-7,38,11);break;
 case'mold':c.fillStyle='rgba(0,0,0,.25)';el(c,0,22,36,7);break;
 case'ramekin':c.fillStyle='rgba(0,0,0,.3)';el(c,0,20,30,7);c.fillStyle='#FFFFFF';c.fillRect(-24,-10,48,28);el(c,0,18,24,5);c.strokeStyle='rgba(150,130,110,.25)';c.lineWidth=1;for(let q=-22;q<=22;q+=4){c.beginPath();c.moveTo(q,-9);c.lineTo(q,20);c.stroke()}c.fillStyle='#F4F0EA';el(c,0,-10,24,6);c.fillStyle='#E4DCCF';el(c,0,-10,21,4.8);break;
 case'plate':c.fillStyle='rgba(0,0,0,.25)';el(c,0,8,52,18);g=c.createRadialGradient(-12,-6,4,0,0,50);g.addColorStop(0,'#FFFFFF');g.addColorStop(1,'#DCD3C4');c.fillStyle=g;el(c,0,0,50,20);c.fillStyle='#FBF8F2';el(c,0,1,38,15);break}}
function drawVesselFront(c,v){switch(v){
 case'wok':c.strokeStyle='rgba(255,255,255,.14)';c.lineWidth=1.5;c.beginPath();c.ellipse(0,0,44,19,0,.2,Math.PI-.2);c.stroke();break;
 case'pan':case'griddle':c.strokeStyle='rgba(255,255,255,.14)';c.lineWidth=1.5;c.beginPath();c.ellipse(0,0,42,18,0,.2,Math.PI-.2);c.stroke();break;
 case'pot':c.strokeStyle='#E8ECEE';c.lineWidth=2;c.beginPath();c.ellipse(0,-16,35,10.5,0,0,Math.PI);c.stroke();c.fillStyle='rgba(255,255,255,.35)';c.fillRect(-26,-6,4,26);break;
 case'glass':c.strokeStyle='rgba(255,255,255,.85)';c.lineWidth=1.6;c.beginPath();c.moveTo(-19,-46);c.lineTo(-15,30);c.lineTo(15,30);c.lineTo(19,-46);c.stroke();c.fillStyle='rgba(255,255,255,.3)';c.fillRect(-14,-40,3,64);c.strokeStyle='rgba(255,255,255,.6)';c.beginPath();c.ellipse(0,-46,19,4,0,0,7);c.stroke();break;
 case'mold':c.fillStyle='rgba(230,240,245,.18)';c.fillRect(-30,-16,60,34);c.strokeStyle='rgba(255,255,255,.8)';c.lineWidth=1.4;c.strokeRect(-30,-16,60,34);c.fillStyle='rgba(255,255,255,.35)';c.fillRect(-27,-13,3,28);break}}
function drawContents(c,j,v,now){const R0=rng(j.seed);
 if(v==='wok'||v==='pan'||v==='griddle'||v==='tray'||v==='plate'||v==='bowl'){c.save();if(v==='tray'){c.beginPath();c.rect(-45,-15,90,30);c.clip();c.scale(1,.62)}else{const rx=v==='bowl'?38:v==='plate'?40:42,ry=v==='bowl'?11:v==='plate'?16:18,oy=v==='bowl'?-7:0;c.beginPath();c.ellipse(0,oy,rx,ry,0,0,7);c.clip();c.translate(0,oy);c.scale(1,ry/rx)}drawTopLayers(c,j,R0,now,v);c.restore()}
 else if(v==='pot')drawPot(c,j,R0,now);else if(v==='cup')drawCupC(c,j,R0,now);else if(v==='glass')drawGlassC(c,j,R0,now);else if(v==='mold')drawMoldC(c,j,R0,now);else if(v==='ramekin')drawRamekinC(c,j,R0,now)}
function drawTopLayers(c,j,R0,now,v){const d=baseOf(j.d);const cnt=id=>j.adds.filter(x=>x===id).length;const k=j.step;
 const mixA=d==='friedrice'||d==='risotto'?j.mix:d==='salad'?Math.min(1,cnt('dressing')*.34):0;
 const P=(n,r,fn)=>{for(let i=0;i<n;i++){const a=R0()*6.283,dd=Math.sqrt(R0())*r;fn(Math.cos(a)*dd,Math.sin(a)*dd,i)}};
 if(v==='wok'||v==='pan'||v==='griddle'){let g=c.createRadialGradient(-10,-8,2,0,0,32);g.addColorStop(0,'rgba(255,220,140,.2)');g.addColorStop(1,'rgba(255,220,140,0)');c.fillStyle=g;circ(c,0,0,32)}
 c.globalAlpha=1-mixA*.9;const side=d==='signature';const ck=clamp(cookNow(j),0,1.3);
 for(const id of uniq(j.adds)){switch(id){
  case'egg':{const age=clamp((R.t-j.t0)/5,0,1);P(7,16,(x,y)=>{c.fillStyle=mix('#FFE680','#F0B83A',age);el(c,x,y,7,5);c.fillStyle='rgba(255,250,235,.85)';el(c,x+2,y+1,3,2)});break}
  case'rice':if(side)riceMound(c,R0,-20,10,11);else P(80,24,(x,y)=>{c.fillStyle=R0()<.5?'#FFFDF4':'#EDE6D2';c.save();c.translate(x,y);c.rotate(R0()*3);el(c,0,0,2.4,1.2);c.restore()});break;
  case'arborio':P(80,24,(x,y)=>{c.fillStyle=R0()<.5?'#F8F2DE':'#E9DFC0';c.save();c.translate(x,y);c.rotate(R0()*3);el(c,0,0,2.6,1.4);c.restore()});break;
  case'wine':c.fillStyle='rgba(240,230,150,.28)';circ(c,0,0,30);break;
  case'stock':{const lv=k&&k.t==='hold'&&k.ing==='stock'?k.level:(j.stock||0);c.fillStyle=`rgba(236,206,140,${.15+lv*.45})`;circ(c,0,0,30);break}
  case'scallion':P(12,24,(x,y)=>{c.strokeStyle='#4D9A3A';c.lineWidth=1.3;c.beginPath();c.arc(x,y,1.9,0,7);c.stroke()});break;
  case'soy':c.fillStyle=`rgba(100,50,15,${Math.min(.35,cnt('soy')*.1)})`;circ(c,0,0,26);break;
  case'patty':case'steak':case'duck':case'chicken':case'salmon':case'scallop':drawProtein(c,id,j,v==='tray');break;
  case'butter':{const b=k&&k.t==='hold'&&k.ing==='butter'?k.level:(j.butter||0);c.fillStyle=`rgba(250,226,140,${.25+b*.45})`;for(let i=0;i<7;i++)circ(c,Math.cos(i+now*.8)*28,Math.sin(i+now*.8)*20,3+b*5);break}
  case'cheese':c.fillStyle='#F7C548';c.save();c.rotate(.5);rr(c,-17,-17,34,34,3);c.fill();c.restore();break;
  case'lettuce':c.fillStyle='#7CBF4A';for(let i=0;i<14;i++){const a=i/14*6.283;circ(c,Math.cos(a)*24,Math.sin(a)*24,6)}break;
  case'bun':{let g=c.createRadialGradient(-6,-8,3,0,0,26);g.addColorStop(0,'#F1B566');g.addColorStop(1,'#B5652A');c.fillStyle=g;circ(c,0,0,25);c.fillStyle='#FFF3D6';for(let i=0;i<16;i++){c.save();c.translate((R0()-.5)*34,(R0()-.5)*34);c.rotate(R0()*3);el(c,0,0,1.8,.9);c.restore()}gloss(c,-8,-9,7,3,.35);break}
  case'potato':P(16,26,(x,y)=>stick(c,x,y,16,4,R0()*3.14,mix('#F6E6B0','#EDB040',clamp(ck,0,1)),mix('#E8D49A','#C07A22',clamp(ck,0,1))));if(ck>1){c.fillStyle=`rgba(40,20,10,${Math.min(.6,(ck-1)*2)})`;circ(c,0,0,30)}break;
  case'vegmix':vegPieces(c,R0,0,0,26);if(ck>0){c.fillStyle=`rgba(90,45,15,${Math.min(.5,ck*.35)})`;P(18,26,(x,y)=>el(c,x,y,3,1))}break;
  case'truffle':P(7,22,(x,y)=>truffleShave(c,x,y,3.6));break;
  case'salt':case'herbs':case'sugar':case'cocoa':{const col=ING[id].c;P(cnt(id)*10,26,(x,y)=>{c.fillStyle=col;circ(c,x,y,.9)});break}
  case'oil':c.fillStyle=`rgba(210,190,60,${Math.min(.3,cnt('oil')*.1)})`;circ(c,0,0,32);break;
  case'balsamic':P(cnt(id)*7,28,(x,y)=>{c.fillStyle='#3A1A1A';circ(c,x,y,1.4)});break;
  case'lemon':lemonWedge(c,24,-12,1.1,.5);break;
  case'asparagus':if(side)asparagus(c,14,12,.6,4,-.1);else asparagus(c,4,12,.9,4,.2);break;
  case'greens':if(side)greens(c,R0,20,10,9,10);else greens(c,R0,0,0,26,28);break;
  case'ctomato':cherryTom(c,-10,-8,5);cherryTom(c,12,6,5);cherryTom(c,2,-14,4.5);break;
  case'cucumber':P(4,22,(x,y)=>{c.fillStyle='#5A8F3A';circ(c,x,y,5);c.fillStyle='#DDEFC2';circ(c,x,y,4)});break;
  case'dressing':P(cnt(id)*5,24,(x,y)=>{c.fillStyle='rgba(230,196,106,.85)';el(c,x,y,3,1.6)});break;
  case'prosciutto':c.lineCap='round';for(let i=0;i<3;i++){const px=(i-1)*14,py=i%2?-6:5;c.strokeStyle='#E48C8F';c.lineWidth=7;c.beginPath();c.moveTo(px-8,py);c.bezierCurveTo(px-3,py-9,px+3,py+9,px+8,py);c.stroke();c.strokeStyle='#F8D4D2';c.lineWidth=1.6;c.beginPath();c.moveTo(px-8,py-2.5);c.bezierCurveTo(px-3,py-11,px+3,py+7,px+8,py-2.5);c.stroke()}break;
  case'fig':c.fillStyle='#6B2E4A';circ(c,-20,-8,5);c.fillStyle='#E88A9A';circ(c,-20,-8,3.6);c.fillStyle='#6B2E4A';circ(c,18,12,5);c.fillStyle='#E88A9A';circ(c,18,12,3.6);break;
  case'parmesan':P(18,24,(x,y)=>{c.fillStyle='#FFF4D8';circ(c,x,y,1.1)});break;
  case'mash':mash(c,-18,10,1);break;
  case'bread':bread(c,-18,10,1);break;
  case'noodle':noodleNest(c,R0,-18,10,12,['#F4CB72','#E8B04F','#F7D98E']);break;
  case'potatoSide':break;
 }}
 const holding=k&&k.t==='hold'&&!['butter','stock','milk','soda','beans','cream','custard','caramel','cheesebatter','whites'].includes(k.ing);
 if(j.sauce||holding){const lv=holding?k.level:j.sauce;const col=holding?(ING[k.ing]||{}).c:j.sauceC;c.fillStyle=col;c.globalAlpha=.88*(1-mixA*.9);for(let i=0;i<5;i++)el(c,Math.cos(i*1.3)*12,Math.sin(i*1.3)*8+2,3+lv*9,2+lv*5)}
 c.globalAlpha=1;if(mixA>0){c.globalAlpha=mixA;c.drawImage(foodCanvas(d,160),-38,-38,76,76);c.globalAlpha=1}}
const PROT={steak:['#C43A4C','#7A3E22'],duck:['#E39292','#8A4A26'],patty:['#C65A5C','#6A3A22'],chicken:['#F4CDB0','#C07A34'],salmon:['#F8A57C','#D0703E'],scallop:['#F6EADA','#C8904A']};
function drawProtein(c,id,j,oven){const rc=PROT[id];const cook=cookNow(j);const flipped=j.side===1;const col=v=>v>1?mix(rc[1],'#2A1A10',Math.min(1,(v-1)*3)):mix(rc[0],rc[1],clamp(v,0,1));
 const top=col(oven?cook:flipped?j.sear[0]:0);const edge=col(Math.min(1.3,cook*1.15));
 const G=r=>{const gr=c.createRadialGradient(-5,-5,2,0,0,r);gr.addColorStop(0,top);gr.addColorStop(.62,top);gr.addColorStop(1,edge);return gr};
 c.fillStyle='rgba(0,0,0,.28)';
 switch(id){
  case'steak':el(c,2,5,31,23);c.fillStyle=G(32);c.beginPath();c.moveTo(-28,-10);c.bezierCurveTo(-24,-24,18,-26,28,-12);c.bezierCurveTo(34,4,24,22,0,22);c.bezierCurveTo(-24,22,-34,6,-28,-10);c.fill();c.fillStyle=flipped?mix('#F3E6D0','#C89A60',clamp(j.sear[0],0,1)):'#F3E6D0';c.beginPath();c.moveTo(-28,-10);c.bezierCurveTo(-24,-24,18,-26,28,-12);c.lineTo(24,-8);c.bezierCurveTo(14,-19,-20,-17,-24,-5);c.closePath();c.fill();
   if(!flipped){c.strokeStyle='rgba(255,255,255,.35)';c.lineWidth=.9;for(let i=0;i<5;i++){c.beginPath();c.moveTo(-18+i*8,-5);c.quadraticCurveTo(-14+i*8,5,-20+i*8,15);c.stroke()}}else if(j.sear[0]>.35){c.strokeStyle='rgba(40,18,8,.65)';c.lineWidth=2.4;for(let i=-2;i<=2;i++){c.beginPath();c.moveTo(-16+i*10,-14);c.lineTo(-4+i*10,18);c.stroke()}}gloss(c,-10,-8,9,3,.22);break;
  case'patty':el(c,2,5,26,20);c.fillStyle=G(26);circ(c,0,0,25);if(flipped&&j.sear[0]>.35){c.strokeStyle='rgba(40,18,8,.6)';c.lineWidth=2.4;for(let i=-2;i<=2;i++){c.beginPath();c.moveTo(-14+i*8,-18);c.lineTo(-4+i*8,18);c.stroke()}}else if(!flipped){c.fillStyle='rgba(255,255,255,.3)';for(let i=0;i<12;i++)circ(c,Math.cos(i)*14,Math.sin(i*1.7)*14,1)}break;
  case'duck':el(c,2,5,31,20);if(flipped){const v=j.sear[0];c.fillStyle=v>1?mix('#C9782E','#2A1A10',Math.min(1,(v-1)*3)):mix('#F3DCC0','#C9782E',clamp(v,0,1));el(c,0,0,30,19);if(j.cut){c.strokeStyle='rgba(90,40,15,.55)';c.lineWidth=1.3;for(let i=-3;i<=3;i++){c.beginPath();c.moveTo(i*7-6,-15);c.lineTo(i*7+6,15);c.stroke();c.beginPath();c.moveTo(i*7+6,-15);c.lineTo(i*7-6,15);c.stroke()}}gloss(c,-8,-8,10,3,.35)}else{c.fillStyle=G(30);el(c,0,0,30,19);c.fillStyle='rgba(255,255,255,.25)';el(c,-6,-6,10,4)}break;
  case'chicken':c.save();c.rotate(-.35);el(c,0,5,28,19);c.fillStyle='#F5EAD6';rr(c,20,-4,14,8,4);c.fill();circ(c,34,-3,4);circ(c,34,3,4);c.fillStyle=G(28);el(c,-2,0,26,18);gloss(c,-10,-7,9,3,.4);c.restore();break;
  case'salmon':c.save();c.rotate(-.15);el(c,2,5,32,18);c.fillStyle=G(32);rr(c,-30,-15,60,30,12);c.fill();c.strokeStyle=`rgba(255,235,220,${.9-Math.min(.6,cook*.5)})`;c.lineWidth=1.4;for(let i=-4;i<=4;i++){c.beginPath();c.moveTo(i*6-3,-14);c.quadraticCurveTo(i*6+2,0,i*6-2,14);c.stroke()}c.restore();break;
  case'scallop':for(let i=0;i<3;i++){const px=(i-1)*16,py=i%2?5:-3;c.fillStyle='rgba(0,0,0,.25)';el(c,px+1,py+3,10,7);c.save();c.translate(px,py);c.fillStyle=G(10);circ(c,0,0,9.5);c.restore()}break}}
function drawPot(c,j,R0,now){const has=id=>j.adds.includes(id);const k=j.step;const d=baseOf(j.d);c.save();c.beginPath();c.ellipse(0,-16,33,9.5,0,0,7);c.clip();c.translate(0,-16);c.scale(1,9.5/33);const boiling=k&&k.t==='wait';
 if(d==='soup'){c.fillStyle=has('stock')?mix('#E6C88C','#EA922E',clamp(j.wait||0,0,1)):'#C9D9DD';circ(c,0,0,34);if(has('pumpkin')&&(j.wait||0)<.9){c.globalAlpha=1-(j.wait||0);for(let i=0;i<8;i++){c.fillStyle=i%2?'#F2A33A':'#E88C2A';c.save();c.translate((R0()-.5)*44,(R0()-.5)*44);c.rotate(R0()*3);c.fillRect(-5,-5,10,10);c.restore()}c.globalAlpha=1}
  const cr=k&&k.t==='hold'&&k.ing==='cream'?k.level:(j.cream||0);if(cr>0){c.strokeStyle=`rgba(255,250,240,${Math.min(1,cr*1.5)})`;c.lineWidth=3;c.beginPath();for(let t=0;t<12;t+=.25){const q=t*1.6*Math.min(1.2,cr*1.6);c.lineTo(Math.cos(t)*q,Math.sin(t)*q)}c.stroke()}
  if(has('seeds')){c.fillStyle='#4F7A35';for(let i=0;i<7;i++){c.save();c.translate((R0()-.5)*36,(R0()-.5)*36);c.rotate(R0()*3);el(c,0,0,3.4,1.8);c.restore()}}}
 else{const drained=has('tomato')||has('garlic');c.fillStyle=drained?'#6E777B':'#BFD6DC';circ(c,0,0,34);
  if(has('noodle')){const w=j.wait||0;if(!drained){if(w<.45){c.lineCap='round';for(let i=0;i<16;i++){const a=i/16*6.283;c.strokeStyle=i%2?'#EFD28A':'#E3C272';c.lineWidth=2.4;c.beginPath();c.moveTo(Math.cos(a)*3,Math.sin(a)*3);c.lineTo(Math.cos(a)*(18+w*30),Math.sin(a)*(18+w*30));c.stroke()}}else noodleNest(c,R0,0,0,26,['#F7E0A0','#EFD08A','#F9E8B8'])}else noodleNest(c,R0,0,0,28,['#F4CB72','#E8B04F','#F7D98E'])}
  if(has('tomato'))tomatoSauce(c,R0,0,0,20);if(has('garlic')){c.fillStyle='#EDE0C0';for(let i=0;i<8;i++)el(c,(R0()-.5)*40,(R0()-.5)*40,3,2.2)}if(has('shrimp')){shrimp(c,-12,-6,1.2,.4);shrimp(c,12,-8,1.2,2.2);shrimp(c,2,12,1.2,-1)}if(has('mussel')){mussel(c,-16,10,1.3,.5);mussel(c,18,8,1.3,-.7)}
  if(j.mix>0){c.globalAlpha=j.mix;c.drawImage(foodCanvas(d,160),-40,-40,80,80);c.globalAlpha=1}
  if(has('basil')){leaf(c,6,-8,14,7,-.6,'#3F8B3A');leaf(c,11,-2,12,6,.4,'#4E9E44')}if(has('parmesan')){c.fillStyle='#FFF4D8';for(let i=0;i<20;i++)circ(c,(R0()-.5)*40,(R0()-.5)*40,1.1)}if(has('parsley'))herbs(c,R0,0,0,24,12,'#3E8A36')}
 if(boiling){c.fillStyle='rgba(255,255,255,.75)';for(let i=0;i<10;i++){const ph=(now*1.6+i*.37)%1;circ(c,Math.cos(i*2.1)*22,Math.sin(i*2.1)*22,1.4+ph*3)}}
 c.restore()}
function drawCupC(c,j,R0,now){const has=id=>j.adds.includes(id);const k=j.step;c.save();c.beginPath();c.ellipse(0,-9.5,19.5,5.6,0,0,7);c.clip();c.translate(0,-9.5);c.scale(1,5.6/19.5);
 if(j.d==='coffee'){const e=j.wait||0;if(e>0){c.fillStyle=mix('#EFE8DC','#5E3219',Math.min(1,e*1.3));circ(c,0,0,20);c.fillStyle=`rgba(196,130,70,${e*.55})`;circ(c,0,0,13)}const fo=k&&k.t==='hold'&&k.ing==='milk'?Math.min(1,k.level):(j.foam||0);if(fo>0){c.fillStyle=mix('#8A5A34','#E9CFA6',fo);circ(c,0,0,20);if(!(k&&k.t==='hold')){c.fillStyle='#F7EAD2';c.beginPath();c.moveTo(0,12);c.bezierCurveTo(-16,0,-10,-12,0,-5);c.bezierCurveTo(10,-12,16,0,0,12);c.fill()}}}
 else{if(has('tea')){c.fillStyle=mix('#E6DCCB','#B5561F',clamp(j.wait||0,0,1));circ(c,0,0,20);if(!has('lemon')){c.fillStyle='#4A2A14';for(let i=0;i<14;i++)el(c,(R0()-.5)*30,(R0()-.5)*30,1.8,1)}}if(has('lemon')){c.fillStyle='#F2D23E';circ(c,5,-3,8);c.fillStyle='#FBEFA2';circ(c,5,-3,6.5)}}
 c.restore()}
function drawGlassC(c,j,R0,now){const k=j.step;const has=id=>j.adds.includes(id);c.save();c.beginPath();c.moveTo(-18,-45);c.lineTo(18,-45);c.lineTo(14.5,29);c.lineTo(-14.5,29);c.closePath();c.clip();
 const lvl=k&&k.t==='hold'&&k.ing==='soda'?Math.min(1.05,k.level):(j.fill||0);
 if(has('syrup')){c.fillStyle='rgba(226,86,110,.85)';c.fillRect(-20,20,40,10)}
 if(lvl>0){const top=29-76*lvl;let g=c.createLinearGradient(0,top,0,29);if(has('syrup')){g.addColorStop(0,'rgba(255,170,180,.75)');g.addColorStop(1,'rgba(226,86,110,.85)')}else{g.addColorStop(0,'rgba(200,232,244,.6)');g.addColorStop(1,'rgba(160,210,230,.75)')}c.fillStyle=g;c.fillRect(-20,top,40,30-top);c.fillStyle='rgba(255,255,255,.6)';c.fillRect(-20,top,40,1.5);c.strokeStyle='rgba(255,255,255,.8)';c.lineWidth=.8;for(let i=0;i<10;i++){const ph=(now*.6+i*.13)%1;const yy=29-ph*(29-top);c.beginPath();c.arc(-10+((i*7)%20),yy,1+(i%3)*.4,0,7);c.stroke()}}
 const surf=lvl>0?29-76*lvl:22;
 if(has('fruit')){c.fillStyle='#F7931E';circ(c,-5,14,8);c.fillStyle='#FFC46B';circ(c,-5,14,6.2);c.fillStyle='#E23E57';el(c,6,22,6,5)}
 if(has('lemon')){const ly=Math.max(surf+6,-30);c.fillStyle='#F2D23E';circ(c,4,ly,8);c.fillStyle='#FBEFA2';circ(c,4,ly,6.4)}
 if(has('ice')){for(let i=0;i<3;i++){const yy=lvl>.2?surf+3+i*9:18-i*9;c.fillStyle='rgba(235,248,255,.75)';rr(c,-12+i*7,yy,10,10,2);c.fill();c.strokeStyle='rgba(150,190,210,.7)';c.lineWidth=.8;rr(c,-12+i*7,yy,10,10,2);c.stroke()}}
 c.restore();if(lvl>1){c.fillStyle='rgba(190,225,240,.6)';el(c,20,-40,4,8)}}
function drawMoldC(c,j,R0,now){const has=id=>j.adds.includes(id);const k=j.step;const d=baseOf(j.d);c.save();c.beginPath();c.rect(-29,-15,58,32);c.clip();const bot=17,H=32;
 if(d==='pudding'){const lv=k&&k.t==='hold'&&k.ing==='custard'?Math.min(1.05,k.level):(j.fill||0);if(lv>0){const top=bot-H*lv;let g=c.createLinearGradient(-29,0,29,0);g.addColorStop(0,'#E9B650');g.addColorStop(.5,'#F9DC8E');g.addColorStop(1,'#DDA640');c.fillStyle=g;c.fillRect(-29,top,58,bot-top);if(j.wait>0){c.fillStyle=`rgba(255,255,255,${j.wait*.3})`;c.fillRect(-29,top,58,2)}const car=k&&k.t==='hold'&&k.ing==='caramel'?Math.min(1,k.level):(j.car||0);if(car>0){c.fillStyle='#A8561A';c.fillRect(-29,top,58,car*10);gloss(c,-10,top+2,10,1.2,.35)}}}
 else if(d==='tiramisu'){if(has('ladyfinger')){c.fillStyle=has('espresso')?'#9A6236':'#E7C07A';c.fillRect(-29,7,58,10);c.fillStyle='rgba(255,255,255,.2)';for(let i=0;i<6;i++)circ(c,-24+i*10,9,1)}if(has('mascarpone')){c.fillStyle='#F7EEDC';c.fillRect(-29,-5,58,12)}const cc=j.adds.filter(x=>x==='cocoa').length;if(cc){c.fillStyle='#6E4226';c.fillRect(-29,-7,58,Math.min(4,cc*1.2));c.fillStyle='rgba(110,66,38,.7)';for(let i=0;i<cc*8;i++)circ(c,(R0()-.5)*56,-8+R0()*3,.7)}}
 else{const lv=k&&k.t==='hold'?Math.min(1.05,k.level):(j.fill||0);if(lv>0){const top=bot-H*lv;c.fillStyle='#F4DFA9';c.fillRect(-29,top,58,bot-top);const w=j.wait||0;if(w>0){let g=c.createLinearGradient(0,top,0,top+9);g.addColorStop(0,mix('#F4DFA9','#4A2A12',w));g.addColorStop(1,'#F4DFA9');c.fillStyle=g;c.fillRect(-29,top,58,9)}}}
 c.restore();if(has('berries')){c.fillStyle='#3A2E6A';circ(c,-8,-17,4);c.fillStyle='#D23A4A';circ(c,2,-18,4.2);c.fillStyle='#3A2E6A';circ(c,10,-16,3.6)}}
function drawRamekinC(c,j,R0,now){const k=j.step;const lv=k&&k.t==='hold'?Math.min(1.05,k.level):(j.fill||0);if(lv<=0)return;const cook=cookNow(j);const rise=4+lv*6+Math.min(1,cook)*12;const col=cook>1?mix('#C98A33','#3A2010',Math.min(1,(cook-1)*3)):mix('#FFFFFF','#D9A04A',clamp(cook,0,1));let g=c.createRadialGradient(-5,-10-rise,2,0,-10,26);g.addColorStop(0,mix(col,'#FFFFFF',.25));g.addColorStop(1,col);c.fillStyle=g;c.beginPath();c.moveTo(-21,-10);c.bezierCurveTo(-24,-10-rise*1.6,24,-10-rise*1.6,21,-10);c.closePath();c.fill();const sug=j.adds.filter(x=>x==='sugar').length;c.fillStyle='rgba(255,255,255,.95)';for(let i=0;i<sug*10;i++)circ(c,(R0()-.5)*30,-12-R0()*rise,.8)}
function foodCanvas(id,size,want){const key='f'+id+size+(want||0)+(id==='signature'&&S.signature?S.signature.base+S.signature.protein+S.signature.sauce+S.signature.side:'');if(DCACHE.has(key))return DCACHE.get(key);const cv=mkCanvas(size),f=cv.getContext('2d');f.translate(size/2,size/2);f.scale(size/100,size/100);paintFood(f,id,want);DCACHE.set(key,cv);return cv}
/* the finish that makes a 特製版 recognisable on the pass */
function paintTopping(c,top,R){c.save();c.scale(1,.8);
 switch(top){
 case'crab':{c.fillStyle='rgba(120,60,30,.14)';el(c,0,3,19,11);for(let i=0;i<14;i++){c.save();const a=R()*6.28,d=Math.sqrt(R())*11;c.translate(Math.cos(a)*d*1.5,Math.sin(a)*d);c.rotate(R()*3);const L=9+R()*5;c.fillStyle=i%3?'#F8E6DA':'#F3D2C2';rr(c,-L/2,-2.4,L,4.8,2.4);c.fill();c.fillStyle='#EF8A70';rr(c,L/2-3.2,-2.4,3.2,4.8,2);c.fill();c.fillStyle='rgba(255,255,255,.6)';rr(c,-L/2+1,-1.6,L*.45,1.4,.7);c.fill();c.restore()}for(let i=0;i<8;i++){const x=(R()-.5)*30,y=(R()-.5)*22;c.fillStyle='#4E9A3A';circ(c,x,y,1.7);c.fillStyle='#BFE39A';circ(c,x,y,.8)}break}
 case'burrata':{c.fillStyle='rgba(0,0,0,.14)';el(c,1,4,12,7);let g=c.createRadialGradient(-3,-4,1,0,0,12);g.addColorStop(0,'#FFFFFF');g.addColorStop(1,'#E9E2D3');c.fillStyle=g;el(c,0,-1,11.5,10);c.fillStyle='#FFFDF6';c.beginPath();c.moveTo(-4,-9);c.quadraticCurveTo(0,-14,4,-9);c.quadraticCurveTo(0,-7,-4,-9);c.fill();c.fillStyle='rgba(255,250,235,.9)';el(c,6,4,6,3);leaf(c,9,-8,10,5,-.5,'#3F8B3A');c.fillStyle='rgba(120,90,40,.35)';for(let i=0;i<5;i++)circ(c,(R()-.5)*16,(R()-.5)*14,.7);break}
 case'porcini':{c.save();c.translate(-8,0);c.fillStyle='rgba(60,35,20,.35)';el(c,0,18,19,4);let g=c.createLinearGradient(0,10,0,20);g.addColorStop(0,'#7A4A2A');g.addColorStop(1,'#4A2C18');c.fillStyle=g;c.beginPath();c.moveTo(-20,11);c.quadraticCurveTo(-10,22,0,21);c.quadraticCurveTo(10,22,20,11);c.quadraticCurveTo(0,17,-20,11);c.fill();for(const [x,y,a] of[[-14,13,-.5],[-5,17,.2],[5,16,-.2],[14,12,.5]]){c.save();c.translate(x,y);c.rotate(a);c.fillStyle='#8F6038';el(c,0,0,5.2,3);c.fillStyle='#C99A62';el(c,-.6,-.9,3.6,1.7);c.fillStyle='rgba(255,255,255,.35)';el(c,-1.5,-1.4,1.5,.6);c.restore()}c.fillStyle='rgba(255,255,255,.22)';el(c,-6,13.5,7,1.4);c.fillStyle='#2A211C';for(const [x,y] of[[-9,9],[2,10],[9,7],[-2,-8],[6,-12]]){c.save();c.translate(x,y);c.rotate(R()*3);c.beginPath();c.moveTo(-2.6,0);c.quadraticCurveTo(0,-2,2.6,0);c.quadraticCurveTo(0,1.3,-2.6,0);c.fill();c.restore()}c.fillStyle='#5FA640';circ(c,-3,14,.9);circ(c,8,15,.8);c.restore();break}
 case'truffle':{c.fillStyle='#2A211C';for(let i=0;i<8;i++){c.save();c.translate((R()-.5)*22,(R()-.5)*16);c.rotate(R()*3);c.beginPath();c.moveTo(-3,0);c.quadraticCurveTo(0,-2.2,3,0);c.quadraticCurveTo(0,1.4,-3,0);c.fill();c.restore()}c.fillStyle='rgba(255,255,255,.35)';el(c,-6,-6,4,2);break}
 case'marrow':{c.save();c.translate(21,-9);c.rotate(-.55);c.fillStyle='rgba(60,30,10,.22)';rr(c,-12,-3,26,10,5);c.fill();c.fillStyle='#EAD9B8';rr(c,-13,-5.5,26,11,5.5);c.fill();c.fillStyle='#D3B78A';rr(c,-13,-5.5,26,3.2,3);c.fill();c.fillStyle='#F4E8CE';rr(c,-12,-4,24,1.6,.8);c.fill();let g=c.createLinearGradient(0,-3,0,4);g.addColorStop(0,'#F0C9A0');g.addColorStop(1,'#C9865A');c.fillStyle=g;el(c,0,.5,8.5,3.2);c.fillStyle='rgba(255,240,220,.7)';el(c,-2,-.6,4,1.2);c.fillStyle='#FFFFFF';for(let i=0;i<5;i++)circ(c,-8+i*4+(R()-.5)*2,.5+(R()-.5)*3,.55);c.fillStyle='#4E9A3A';circ(c,-4,-1,1);circ(c,3,1.5,1);circ(c,7,-1.5,.8);c.restore();break}
 case'cherry':{c.fillStyle='rgba(122,28,46,.55)';el(c,2,6,16,6);for(const [x,y] of[[-6,4],[3,8],[10,2],[-1,-1]]){c.fillStyle='#6E1626';circ(c,x,y,3.6);c.fillStyle='#A02A3E';circ(c,x-.8,y-1,2.6);c.fillStyle='rgba(255,255,255,.55)';circ(c,x-1.6,y-1.8,.9)}c.strokeStyle='#4E3A22';c.lineWidth=.9;c.beginPath();c.moveTo(10,-1);c.quadraticCurveTo(13,-7,17,-9);c.stroke();break}
 case'uni':{for(const [x,y,a] of[[-7,-3,-.35],[6,1,.3],[-1,8,-.05]]){c.save();c.translate(x,y);c.rotate(a);c.fillStyle='rgba(120,60,10,.18)';el(c,1,2,10,4);let g=c.createLinearGradient(0,-4,0,4);g.addColorStop(0,'#F8BC55');g.addColorStop(1,'#E27A1E');c.fillStyle=g;c.beginPath();c.moveTo(-10,0);c.quadraticCurveTo(-8,-5,0,-4.6);c.quadraticCurveTo(8,-5,10,0);c.quadraticCurveTo(8,4.4,0,4.4);c.quadraticCurveTo(-8,4.4,-10,0);c.fill();c.fillStyle='rgba(200,100,20,.35)';for(let k=-7;k<=7;k+=2.3)for(let r=-2;r<=2;r+=2)circ(c,k+(r?1.1:0),r,.7);c.fillStyle='rgba(255,255,255,.4)';el(c,-3,-2.2,3.5,1);c.restore()}c.fillStyle='#3F8B3A';circ(c,14,-8,1.2);circ(c,-13,7,1);break}
 case'matcha':{c.fillStyle='rgba(111,168,78,.55)';el(c,0,-6,16,9);c.fillStyle='#6FA84E';for(let i=0;i<26;i++)circ(c,(R()-.5)*34,-6+(R()-.5)*20,.8+R()*.5);c.fillStyle='rgba(255,255,255,.4)';el(c,-5,-9,4,2);break}}
 c.restore()}
function drawIng(c,id,x,y,r){const I=ING[id]||{k:'bits',c:'#ccc'};c.save();c.translate(x,y);const s=r/16;c.scale(s,s);const sh=()=>{c.fillStyle='rgba(0,0,0,.18)';el(c,1,13,13,3)};
 switch(I.k){
 case'egg':sh();c.fillStyle='#F2E1C8';el(c,0,0,10.5,13.5);c.fillStyle='rgba(160,110,60,.12)';el(c,3,4,6,8);c.fillStyle='#FFF6E8';el(c,-3.5,-5,3.5,4.5);break;
 case'bowl':case'bits':sh();c.fillStyle='#F4F0EA';c.beginPath();c.moveTo(-15,-2);c.quadraticCurveTo(-13,14,0,14);c.quadraticCurveTo(13,14,15,-2);c.fill();c.fillStyle=I.k==='bowl'?I.c:'#E9E1D4';el(c,0,-2,14,5);if(I.k==='bits'){const R0=rng(hash(id));c.fillStyle=I.c;for(let i=0;i<12;i++)el(c,(R0()-.5)*20,-2+(R0()-.5)*6,1.8,1.2)}else{c.fillStyle='rgba(255,255,255,.35)';el(c,-4,-3.5,5,1.4)}c.strokeStyle='rgba(0,0,0,.14)';c.lineWidth=1;c.beginPath();c.ellipse(0,-2,15,5.5,0,0,7);c.stroke();break;
 case'bottle':{sh();const light=['#BFE3F0','#E9DF9A','#E6C88C','#EFCF73'].includes(I.c);const glass='rgba(230,242,246,.92)';c.fillStyle=light?glass:I.c;rr(c,-7,-3,14,17,4);c.fill();if(light){c.fillStyle=I.c;rr(c,-6,2,12,11,3);c.fill()}c.fillStyle=light?glass:I.c;c.fillRect(-3,-11,6,9);c.fillStyle='#2A2A2A';rr(c,-3.6,-15,7.2,4.5,1.2);c.fill();c.fillStyle='#F6EEDF';c.fillRect(-7,3,14,5.5);c.fillStyle='rgba(255,255,255,.4)';c.fillRect(-5,-1,2.2,13);c.strokeStyle='rgba(0,0,0,.15)';c.lineWidth=.8;rr(c,-7,-3,14,17,4);c.stroke();break}
 case'carton':sh();c.fillStyle='#FFFFFF';c.fillRect(-8,-6,16,20);c.fillStyle='#EAE5DC';c.beginPath();c.moveTo(-8,-6);c.lineTo(0,-14);c.lineTo(8,-6);c.fill();c.fillStyle=I.c==='#FFFFFF'||I.c==='#FFF8E8'?'#6FA3D0':I.c;c.fillRect(-8,2,16,7);c.fillStyle='rgba(0,0,0,.08)';c.fillRect(3,-6,5,20);c.strokeStyle='rgba(0,0,0,.15)';c.lineWidth=.8;c.strokeRect(-8,-6,16,20);break;
 case'shaker':sh();c.fillStyle='rgba(235,240,242,.9)';rr(c,-6,-4,12,17,3);c.fill();c.fillStyle=I.c==='#FFFFFF'?'#F4F4F4':I.c;c.fillRect(-5,4,10,8);c.fillStyle='#B9C1C4';rr(c,-7,-10,14,7,3);c.fill();c.fillStyle='#6A7478';for(let i=-1;i<=1;i++)circ(c,i*3.5,-8,.8);c.strokeStyle='rgba(0,0,0,.15)';c.lineWidth=.8;rr(c,-6,-4,12,17,3);c.stroke();break;
 case'leaf':for(let i=0;i<5;i++)leaf(c,Math.cos(i*1.3)*5,Math.sin(i*1.3)*4,15,7,i*1.2,i%2?I.c:mix(I.c,'#FFFFFF',.18));break;
 case'noodle':c.save();c.rotate(-.5);for(let i=-4;i<=4;i++){c.fillStyle=i%2?'#F1D48A':'#E9C878';c.fillRect(i*1.6-.7,-15,1.4,30)}c.fillStyle='#C8963A';c.fillRect(-8,-2,16,4);c.restore();break;
 case'shrimp':shrimp(c,0,0,1.3,.4);break;
 case'mussel':mussel(c,-3,0,1.3,.4);mussel(c,4,4,1.1,-.5);break;
 case'patty':sh();c.fillStyle='#C65A5C';el(c,0,0,14,10);c.fillStyle='rgba(255,255,255,.35)';for(let i=0;i<8;i++)circ(c,(i%4-1.5)*5,i<4?-3:3,.9);break;
 case'bun':sh();{let g=c.createRadialGradient(-4,-6,2,0,0,15);g.addColorStop(0,'#F1B566');g.addColorStop(1,'#B5652A');c.fillStyle=g;c.beginPath();c.arc(0,4,14,Math.PI,0);c.closePath();c.fill();c.fillStyle='#FFF3D6';for(let i=0;i<6;i++)el(c,-8+i*3.4,-2-Math.sin(i)*3,1.2,.7)}break;
 case'slice':c.save();c.rotate(.2);c.fillStyle=I.c;rr(c,-11,-9,22,18,3);c.fill();c.fillStyle='rgba(255,255,255,.3)';rr(c,-9,-7,8,4,2);c.fill();c.restore();break;
 case'tomato':cherryTom(c,-5,2,7);cherryTom(c,6,-1,6);break;
 case'cuke':c.fillStyle='#4E7F2E';circ(c,-4,0,8);c.fillStyle='#DDEFC2';circ(c,-4,0,6.5);c.fillStyle='#4E7F2E';circ(c,6,3,7);c.fillStyle='#DDEFC2';circ(c,6,3,5.6);break;
 case'beans':for(let i=0;i<6;i++){c.save();c.translate(Math.cos(i)*7,Math.sin(i*1.7)*5);c.rotate(i);c.fillStyle='#5A3218';el(c,0,0,4.6,3.2);c.strokeStyle='#2A160A';c.lineWidth=.8;c.beginPath();c.moveTo(-3,0);c.quadraticCurveTo(0,1.4,3,0);c.stroke();c.restore()}break;
 case'lemon':c.fillStyle='#F2D23E';circ(c,0,0,12);c.fillStyle='#FBEFA2';circ(c,0,0,10);c.strokeStyle='#F2D23E';c.lineWidth=1;for(let i=0;i<8;i++){c.beginPath();c.moveTo(0,0);c.lineTo(Math.cos(i*.785)*9.5,Math.sin(i*.785)*9.5);c.stroke()}break;
 case'ice':c.fillStyle='rgba(220,240,250,.9)';rr(c,-11,-6,11,11,2.5);c.fill();rr(c,1,-2,11,11,2.5);c.fill();c.strokeStyle='rgba(120,170,195,.8)';c.lineWidth=1;rr(c,-11,-6,11,11,2.5);c.stroke();rr(c,1,-2,11,11,2.5);c.stroke();break;
 case'fruit':c.fillStyle='#F7931E';circ(c,-4,0,9);c.fillStyle='#FFC46B';circ(c,-4,0,7);c.fillStyle='#E23E57';c.beginPath();c.moveTo(6,-8);c.quadraticCurveTo(14,0,6,10);c.quadraticCurveTo(-1,0,6,-8);c.fill();break;
 case'fries':for(let i=0;i<7;i++)stick(c,-8+i*2.6,0,20,3.6,1.3+Math.sin(i)*.2,'#F4E2A8','#DCC486');break;
 case'truffle':c.fillStyle='#2F2622';circ(c,0,0,11);c.fillStyle='rgba(255,255,255,.14)';for(let i=0;i<8;i++)circ(c,Math.cos(i)*6,Math.sin(i*1.3)*6,1.3);break;
 case'chunk':for(let i=0;i<4;i++){c.save();c.translate((i%2)*9-4,Math.floor(i/2)*8-4);c.rotate(.3*i);c.fillStyle=i%2?'#F2A33A':'#E88C2A';c.fillRect(-4.5,-4.5,9,9);c.fillStyle='#4F7A35';c.fillRect(-4.5,-4.5,9,1.6);c.restore()}break;
 case'veg':c.fillStyle='#4E7F2E';circ(c,-6,-2,6);c.fillStyle='#E7EDB8';circ(c,-6,-2,4.5);c.strokeStyle='#D6392E';c.lineWidth=4;c.lineCap='round';c.beginPath();c.arc(5,4,6,0,2);c.stroke();c.fillStyle='#5B2E5A';el(c,4,-7,5,3.6);break;
 case'duck':sh();c.fillStyle='#E39292';el(c,0,1,14,9);c.fillStyle='#F3DCC0';el(c,0,-2,13,6.5);break;
 case'chicken':sh();c.fillStyle='#F5EAD6';c.fillRect(6,-2,8,4);c.fillStyle='#F4CDB0';el(c,-2,0,12,8.5);break;
 case'steak':sh();c.fillStyle='#C43A4C';el(c,0,1,14,10);c.fillStyle='#F3E6D0';c.beginPath();c.ellipse(0,1,14,10,0,Math.PI*1.1,Math.PI*1.9);c.lineTo(0,-4);c.fill();c.strokeStyle='rgba(255,255,255,.4)';c.lineWidth=.8;for(let i=0;i<3;i++){c.beginPath();c.moveTo(-6+i*5,0);c.quadraticCurveTo(-4+i*5,5,-7+i*5,9);c.stroke()}break;
 case'salmon':sh();c.save();c.rotate(-.2);c.fillStyle='#F8A57C';rr(c,-14,-8,28,16,6);c.fill();c.strokeStyle='rgba(255,235,220,.9)';c.lineWidth=1;for(let i=-2;i<=2;i++){c.beginPath();c.moveTo(i*5-2,-7);c.quadraticCurveTo(i*5+1,0,i*5-1,7);c.stroke()}c.restore();break;
 case'aspar':asparagus(c,0,-4,.6,4,.3);break;
 case'ham':c.lineCap='round';c.strokeStyle='#E48C8F';c.lineWidth=7;c.beginPath();c.moveTo(-10,2);c.bezierCurveTo(-5,-8,4,10,10,-1);c.stroke();c.strokeStyle='#F8D4D2';c.lineWidth=1.8;c.beginPath();c.moveTo(-10,-.5);c.bezierCurveTo(-5,-10,4,8,10,-3.5);c.stroke();break;
 case'fig':c.fillStyle='#6B2E4A';circ(c,-4,0,8);c.fillStyle='#E88A9A';circ(c,-4,0,5.8);c.fillStyle='#FFE3E6';for(let i=0;i<6;i++)circ(c,-4+Math.cos(i)*3,Math.sin(i)*3,.7);c.fillStyle='#6B2E4A';circ(c,7,4,6);break;
 case'finger':for(let i=0;i<3;i++){c.save();c.translate(0,-6+i*6);c.rotate(.2);c.fillStyle='#E7C07A';rr(c,-13,-3,26,6,3);c.fill();c.fillStyle='rgba(255,255,255,.7)';for(let t=-10;t<=10;t+=4)circ(c,t,-1.5,.7);c.restore()}break;
 case'cup':sh();c.fillStyle='#FFFFFF';c.beginPath();c.moveTo(-10,-5);c.lineTo(10,-5);c.quadraticCurveTo(9,11,0,11);c.quadraticCurveTo(-9,11,-10,-5);c.fill();c.fillStyle='#5B3019';el(c,0,-5,9,3);c.strokeStyle='#fff';c.lineWidth=2.5;c.beginPath();c.arc(11,1,4,-1.2,1.3);c.stroke();break;
 case'berry':c.fillStyle='#3A2E6A';circ(c,-5,2,5);circ(c,4,4,4.5);c.fillStyle='#D23A4A';circ(c,1,-5,5.2);c.fillStyle='rgba(255,255,255,.5)';circ(c,-6,0,1.3);circ(c,0,-7,1.3);break;
 case'bread':bread(c,0,0,.9);break;
 case'scallop':scallops(c,0,0,.9);break}
 c.restore()}
/* ================= cats ================= */
const CAT_DEF=[
 {id:'tora',n:'樾樾',b:'tabby',base:'#9A8166',str:'#3B2C20',belly:'#FFFFFF',tint:'#C98E4E',eye:'#A4B25A',nose:'#E3A29A',earIn:'#F0B8B0',white:{belly:1,paws:1,chest:1,muzzle:1},whiteAmt:.22,strDense:1,fluffy:0,like:'jill',sex:'男生',who:'棕色虎斑，臉上的虎斑比較多，白肚子、白襪子。'},
 {id:'ban',n:'小齁',b:'tabby',base:'#8C7B66',str:'#352A20',belly:'#FFFFFF',eye:'#8FAE62',nose:'#EBA2A2',earIn:'#F2BCB6',white:{belly:1,paws:1,chest:1,muzzle:1,blaze:1},whiteAmt:.5,chestBig:1,fluffy:0,like:'play',sex:'女生',who:'虎斑白臉，鼻子上一道白，白胸口、白手套。'},
 {id:'snow',n:'包包',b:'persian',base:'#F7F6F2',shadeC:'#DEDBD6',str:null,belly:'#FFFFFF',eye:'#9EA64E',eyeLine:1,eyeBig:1,nose:'#D69CA4',earIn:'#BDB0BC',white:{},fluffy:1,like:'top',sex:'男生',who:'銀白金吉拉，圓臉大眼，眼線很深。'},
 {id:'mikan',n:'柔柔',b:'persian',base:'#E6A465',str:null,belly:'#FFF7EE',eye:'#D2AE3E',nose:'#EDA59A',earIn:'#F2B8A8',white:{chest:1,paws:1,blaze:1,muzzle:1},fluffy:1,like:'guest',sex:'女生',who:'橘色金吉拉，白圍兜配白手套。'},
 {id:'mei',n:'寶寶',b:'amshort',base:'#DCDDDC',str:'#222425',belly:'#F1F1F0',eye:'#E4B83A',eyeBig:1,roundPupil:1,nose:'#E6A68A',earIn:'#F0C0B8',fold:1,white:{},fluffy:0,like:'wander',sex:'女生',who:'銀色美短，黑色粗條紋、摺耳、圓滾滾的大眼睛。'},
];
const TREE={x:54,perches:[{x:57,y:320,t:1,ax:83},{x:85,y:288,t:1,ax:111},{x:63,y:254,t:1,ax:89},{x:88,y:350,t:1,ax:114},{x:336,y:320,t:2,ax:308},{x:356,y:288,t:2,ax:326},{x:338,y:252,t:2,ax:312}]};
const WALL=[{x:362,y:66},{x:360,y:32},{x:344,y:-2},{x:316,y:-24},{x:276,y:-40},{x:232,y:-50},{x:190,y:-46}];
function wallTop(){const top=SV.oy/SV.s;return top>40?-Math.min(110,top-26):0}
function perchVis(i){const p=TREE.perches[i];if(p.need&&!gearOn(p.need))return false;return p.t!==3||p.y>wallTop()+14}
let CATS=null;const perchOcc=[];
function drawWallRun(c,now){const WT=wallTop();const vis=y=>y>WT+10;
 const bracket=(x,y)=>{c.fillStyle='#6E6E6A';c.fillRect(x-1,y+2,2,6);c.fillRect(x-4,y+7,8,1.4)};
 const step=(x,y,w)=>{c.fillStyle='rgba(0,0,0,.14)';rr(c,x-w/2+1,y+3,w,6,2);c.fill();bracket(x-w/3,y);bracket(x+w/3,y);c.fillStyle='#B08B5E';rr(c,x-w/2,y,w,5,1.5);c.fill();c.fillStyle='#D9B98A';rr(c,x-w/2,y-1.5,w,3,1.5);c.fill();c.fillStyle='#8E8B85';rr(c,x-w/2+2,y-2.4,w-4,2,1);c.fill()};
 WALL.forEach((w,i)=>{if(!vis(w.y))return;
  if(i===4){const x0=w.x-24,x1=w.x+24;c.strokeStyle='#8A7458';c.lineWidth=.9;c.beginPath();c.moveTo(x0,w.y-16);c.quadraticCurveTo(w.x,w.y-4,x1,w.y-16);c.stroke();c.fillStyle='#6E6E6A';c.fillRect(x0-2,w.y-18,4,4);c.fillRect(x1-2,w.y-18,4,4);for(let k=0;k<8;k++){const px=x0+3+k*6,py=w.y+Math.sin((k+.5)/8*Math.PI)*3;c.strokeStyle='#8A7458';c.lineWidth=.6;c.beginPath();c.moveTo(px+2,py);c.lineTo(px+2,w.y-10+Math.sin((k+.5)/8*Math.PI)*5);c.stroke();c.fillStyle=k%2?'#C9A57A':'#D9B98A';rr(c,px,py-1.5,5,3.4,1);c.fill()}}
  else if(i===6){c.fillStyle='rgba(0,0,0,.14)';el(c,w.x+1,w.y+4,16,5);bracket(w.x-8,w.y+2);bracket(w.x+8,w.y+2);c.fillStyle='#E9E3DA';c.beginPath();c.moveTo(w.x-16,w.y-2);c.quadraticCurveTo(w.x,w.y+12,w.x+16,w.y-2);c.closePath();c.fill();fluff(c,'#F3EEE6',w.x,w.y-2,15,2.6,12,1.8)}
  else step(w.x,w.y,i===0?22:26)});
 if(vis(-60)){c.fillStyle='rgba(0,0,0,.14)';c.fillRect(154,-72,28,26);c.fillStyle='#D9C9AE';rr(c,150,-76,28,26,3);c.fill();c.fillStyle='#3A322C';el(c,164,-62,6.5,6.5);c.fillStyle='#C4B294';c.fillRect(150,-52,28,2)}
 if(S.decor.art>=1&&vis(-42)){const ax=100,ay=-44;c.fillStyle='rgba(0,0,0,.18)';c.fillRect(ax+3,ay+3,26,32);c.fillStyle='#F4F2EE';c.fillRect(ax,ay,26,32);c.fillStyle='#FBFAF7';c.fillRect(ax+2.5,ay+2.5,21,27);c.fillStyle='#D9B27A';circ(c,ax+16,ay+10,3);c.fillStyle='#8FA38A';c.beginPath();c.moveTo(ax+2.5,ay+29.5);c.lineTo(ax+10,ay+17);c.lineTo(ax+16,ay+24);c.lineTo(ax+20,ay+20);c.lineTo(ax+23.5,ay+29.5);c.fill()}}
function drawGear(c,G,now,front){const {x,y}=G;
 switch(G.k){
 case'box':{if(front){c.fillStyle='#B8905E';c.fillRect(x-14,y-8,28,16);c.fillStyle='#8A6A42';c.fillRect(x-14,y-8,28,2);c.fillStyle='rgba(0,0,0,.12)';c.fillRect(x-14,y+6,28,2);return}c.fillStyle='rgba(0,0,0,.16)';el(c,x,y+9,17,4);c.fillStyle='#A47B54';c.fillRect(x-14,y-22,28,30);c.fillStyle='#8A6A42';c.fillRect(x-14,y-22,28,2);c.fillStyle='#C9A26E';c.beginPath();c.moveTo(x-14,y-22);c.lineTo(x-20,y-30);c.lineTo(x-2,y-30);c.lineTo(x+2,y-22);c.closePath();c.fill();c.fillStyle='#4A3226';c.font=`800 5px ${FONT}`;c.textAlign='center';c.fillText('FRAGILE',x,y-12);break}
 case'cushion':{c.fillStyle='rgba(0,0,0,.14)';el(c,x,y+6,22,7);c.fillStyle='#B8536A';el(c,x,y,22,10);c.fillStyle='#C9687C';el(c,x,y-2,19,7.5);c.fillStyle='rgba(255,255,255,.22)';el(c,x-5,y-4,7,2.5);break}
 case'basket':{c.fillStyle='rgba(0,0,0,.14)';el(c,x,y+5,20,6);c.fillStyle='#B08B5E';c.beginPath();c.moveTo(x-19,y-8);c.quadraticCurveTo(x-18,y+8,x,y+8);c.quadraticCurveTo(x+18,y+8,x+19,y-8);c.closePath();c.fill();c.strokeStyle='rgba(120,80,40,.4)';c.lineWidth=.8;for(let yy=y-5;yy<y+6;yy+=3){c.beginPath();c.moveTo(x-17+(yy-y)*.4,yy);c.lineTo(x+17-(yy-y)*.4,yy);c.stroke()}c.fillStyle='#D8C4A4';el(c,x,y-8,19,5);c.fillStyle='#A88858';el(c,x,y-7.5,15,3.5);break}
 case'tunnel':{c.fillStyle='rgba(0,0,0,.14)';el(c,x,y+7,36,5);c.fillStyle='#5E8FA8';rr(c,x-36,y-10,72,20,10);c.fill();c.fillStyle='#2A3A44';el(c,x-34,y,6,9);el(c,x+34,y,6,9);c.fillStyle='rgba(255,255,255,.15)';c.fillRect(x-30,y-8,60,3);c.strokeStyle='rgba(0,0,0,.12)';c.lineWidth=1;for(let k=-2;k<=2;k++){c.beginPath();c.moveTo(x+k*12,y-10);c.lineTo(x+k*12,y+10);c.stroke()}break}
 case'perch':{c.fillStyle='rgba(0,0,0,.14)';c.fillRect(x-20,y+3,40,3);c.fillStyle='#8A6A42';rr(c,x-20,y-2,40,5,2);c.fill();c.fillStyle='#A98559';c.fillRect(x-20,y-2,40,1.5);c.fillStyle='#8A6A42';c.fillRect(x-17,y+3,3,14);c.fillRect(x+14,y+3,3,14);c.fillStyle='#EDE6D8';rr(c,x-17,y-6,34,4,2);c.fill();break}
 case'lounge':{c.fillStyle='rgba(0,0,0,.14)';el(c,x,y+4,20,8);c.fillStyle='#8FA893';el(c,x,y,20,9);c.fillStyle='#A9BFAC';el(c,x,y-2,15,6);break}}}
/* the A-frame chalkboard by the counter: today's recommendation, or a word from the kitchen */
function drawChalkboard(c,now){const x=270,y=FB-10;const rd=recoDish();c.fillStyle='rgba(0,0,0,.16)';el(c,x+1,y+2,14,4);c.fillStyle='#8A6A42';c.beginPath();c.moveTo(x-12,y);c.lineTo(x-9,y-32);c.lineTo(x+9,y-32);c.lineTo(x+12,y);c.closePath();c.fill();c.fillStyle='#2C3A34';c.beginPath();c.moveTo(x-9.5,y-3);c.lineTo(x-7.5,y-29);c.lineTo(x+7.5,y-29);c.lineTo(x+9.5,y-3);c.closePath();c.fill();
 c.fillStyle='#F6EEDF';c.font=`800 4.6px ${FONT}`;c.textAlign='center';c.textBaseline='middle';c.fillText(rd?'今日推薦':"Jill's",x,y-24);c.fillStyle='#E6C27A';c.font=`700 4.2px ${FONT}`;const nm=rd?dishName(rd):'歡迎光臨';c.fillText(nm.length>6?nm.slice(0,6):nm,x,y-17);if(rd){c.drawImage(dishCanvas(rd,'P',64,S.decor.ware>0),x-6,y-14,12,12)}else{c.strokeStyle='rgba(255,255,255,.5)';c.lineWidth=.6;c.beginPath();c.moveTo(x-5,y-11);c.quadraticCurveTo(x,y-7,x+5,y-11);c.stroke()}c.textBaseline='alphabetic'}
function drawCatTree2(c,now){c.save();c.translate(-26,DY);const sisal=(x,y0,y1)=>{let g=c.createLinearGradient(x-4,0,x+4,0);g.addColorStop(0,'#B8986A');g.addColorStop(.5,'#E2C898');g.addColorStop(1,'#A88858');c.fillStyle=g;c.fillRect(x-4,y0,8,y1-y0);c.strokeStyle='rgba(110,80,40,.45)';c.lineWidth=.7;for(let y=y0+1;y<y1;y+=2.2){c.beginPath();c.moveTo(x-4,y);c.lineTo(x+4,y+1);c.stroke()}};
 const plat=(x,y,rx,col,top)=>{c.fillStyle='rgba(0,0,0,.18)';el(c,x+2,y+4,rx+1,rx*.34);c.fillStyle=col;el(c,x,y+2.5,rx,rx*.36);c.fillRect(x-rx,y-.5,rx*2,3);c.fillStyle=top;el(c,x,y-.5,rx,rx*.34)};
 c.fillStyle='rgba(0,0,0,.22)';el(c,372,358,30,6.5);c.fillStyle='#8C8F94';rr(c,344,346,58,11,4);c.fill();c.fillStyle='#C9CCD0';el(c,373,346,29,6);
 sisal(362,322,348);sisal(382,290,348);sisal(364,258,320);
 c.fillStyle='#A7AAB0';rr(c,346,300,20,20,4);c.fill();c.fillStyle='#2A2A2C';el(c,356,312,6,6);c.fillStyle='#C9CCD0';rr(c,346,298,20,4,2);c.fill();
 plat(362,320,17,'#8C8F94','#D5D8DC');plat(382,288,15,'#8C8F94','#D5D8DC');
 if(gearOn('deluxe')){sisal(364,200,252);sisal(346,222,258);plat(346,222,15,'#8C8F94','#D5D8DC');plat(372,196,16,'#8C8F94','#D5D8DC');c.fillStyle='#A7AAB0';rr(c,352,168,24,26,5);c.fill();c.fillStyle='#2A2A2C';el(c,364,182,7,7);c.fillStyle='#C9CCD0';rr(c,352,166,24,4,2);c.fill()}
 c.strokeStyle='#8C8F94';c.lineWidth=1.2;c.beginPath();c.moveTo(348,244);c.lineTo(348,256);c.moveTo(380,244);c.lineTo(380,256);c.stroke();c.fillStyle='#E9E3DA';c.beginPath();c.moveTo(346,246);c.quadraticCurveTo(364,262,382,246);c.lineTo(382,250);c.quadraticCurveTo(364,266,346,250);c.closePath();c.fill();fluff(c,'#F2ECE4',364,251,16,3,10,1.6);
 c.restore();const onTree=CATS?CATS.filter(k=>k.perch>=0&&TREE.perches[k.perch].t===2&&k.st!=='jump').sort((a,b)=>a.y-b.y):[];for(const k of onTree)drawCat(c,k,now)}
function drawStairs(c){const x=300,y=356+FY;c.fillStyle='rgba(0,0,0,.2)';el(c,x+2,y+2,16,4);c.fillStyle='#4A4A4C';rr(c,x-15,y-10,30,10,2);c.fill();c.fillStyle='#5E5E61';rr(c,x-15,y-12,30,3,1.5);c.fill();c.fillStyle='#434346';rr(c,x-5,y-21,20,11,2);c.fill();c.fillStyle='#5A5A5D';rr(c,x-5,y-23,20,3,1.5);c.fill();c.fillStyle='rgba(255,255,255,.06)';for(let i=0;i<30;i++)c.fillRect(x-14+(i*7)%28,y-9+(i*3)%8,.8,.8)}
function drawPost(c,now){const {x,y}=SPOT.scr2;c.fillStyle='rgba(0,0,0,.22)';el(c,x+1,y+1.5,12,3.5);c.fillStyle='#D5D0C8';rr(c,x-12,y-5,24,6,2);c.fill();let g=c.createLinearGradient(x-4,0,x+4,0);g.addColorStop(0,'#B8986A');g.addColorStop(.5,'#E2C898');g.addColorStop(1,'#A88858');c.fillStyle=g;c.fillRect(x-4,y-38,8,34);c.strokeStyle='rgba(110,80,40,.45)';c.lineWidth=.7;for(let yy=y-37;yy<y-4;yy+=2.2){c.beginPath();c.moveTo(x-4,yy);c.lineTo(x+4,yy+1);c.stroke()}c.fillStyle='#D5D0C8';el(c,x,y-38,7,2.4);const sw=Math.sin(now*2)*1.5;c.strokeStyle='rgba(60,40,30,.6)';c.lineWidth=.5;c.beginPath();c.moveTo(x,y-40);c.lineTo(x+sw,y-48);c.stroke();c.fillStyle='#8FB6D9';circ(c,x+sw,y-49,2.4)}
function catCheer(g,amt){if(!R||!g)return 0;if(R.t-(g.cwin??-99)>20){g.cwin=R.t;g.cgain=0}const a=Math.max(0,Math.min(amt,.3-g.cgain));if(a>0){g.pat=Math.min(1,g.pat+a);g.cgain+=a;g.catJoy=true}return a}
function catName(C){return(S.catNames&&S.catNames[C.id])||C.n}
WALL.forEach((w,i)=>TREE.perches.push({x:w.x,y:w.y-3,t:3,wi:i,ax:366,ay:114}));
/* 2.0: the two high places of the three-tier tree (only there once it is bought) */
TREE.perches.push({x:320,y:222,t:2,ax:312,need:'deluxe'},{x:346,y:196,t:2,ax:326,need:'deluxe'});
/* ================= five cats: personality AI ================= */
function applyDY(d){DY=d;KB=clamp(Math.round(d*.25),0,30);FY=d-KB;FB=364+d-KB;LH=424+d;ROWS=[162,240+(d-KB)*.5,318+d-KB];PASS.y=360+d-KB;
 TREE.perches.forEach(p=>{if(p.by==null)p.by=p.y;p.y=p.by+(p.t===3?0:d-KB)});
 SPOT.scr.y=358+d-KB;SPOT.bowl.y=360+d-KB;SPOT.toy.y=324+d-KB;
 CATS=null;perchOcc.length=0;OCC.scr=OCC.scr2=OCC.cave=OCC.toy=null;OCC.bed=[];SIDE.R=SIDE.L=null;IDLE=null;bg=null;if(typeof LIFE!=='undefined'&&LIFE.dylan&&LIFE.dylan.seated){LIFE.dylan.seated=false;LIFE.dylan.state='think';LIFE.dylan.t=1}}
const SIDE={R:null,L:null};let RACE_CD=90,BAO_LAST=null;const MEMQ=[];let FLASH=null;
const MEMS={sofa:'今晚的沙發',sofafull:'沙發客滿',husband:'Dylan — Jill 的先生',sides:'Jill 左右各一隻',ambush:'埋伏成功',what:'妳到底在幹嘛',waited:'白等了',race:'突然開賽',sleepgod:'睡神',nearby:'今天也在附近',best:'最佳座位',nap3:'三貓午睡',everyone:'今天大家都在',
 rest:'偷閒',lap:'膝上的重量',photo:'被拍了',pet:'摸一下',dylan:'留下來的人',
 play:'玩起來了',swat:'柔柔的小巴掌',pressed:'靠著柔柔',greeter:'不怕生',cushion:'一起擠軟墊',distracted:'走到一半忘了',guide:'小齁帶路',oldfriends:'又見面了',dylancat:'他們好像認識',quiet:'打烊後',oddspot:'怎麼睡在這',newroom:'新的店',newspot:'牠自己找到的',boxcat:'紙箱裡有東西',window:'窗邊',tunnel:'隧道的另一頭',reading:'各自安靜',pause:'經過的時候',company:'今天不是一個人',gift:'拿來的東西',anniversary:'紀念日',neighbors:'在店裡遇到',treat:'這個請你',bagcat:'比較喜歡袋子',rainday:'下雨天',selfie:'合照',dishphoto:'先拍再吃',firstspecial:'第一道特製版',kidcat:'小朋友與貓'};
/* one line under each photo, written from what was actually in the frame */
const MEM_TXT={newspot:i=>`${i.a}第一次用了${i.g}。`,boxcat:i=>`${i.a}在紙箱裡，只露出頭。`,window:i=>`${i.a}在窗邊看了很久的街。`,tunnel:i=>`${i.a}從隧道另一頭衝出來。`,sofa:i=>`${i.cats||'貓'}陪 Jill 坐了一會兒。`,sofafull:i=>`沙發上擠了 ${i.n||3} 隻貓，Jill 只好縮著坐。`,husband:()=>'原來一直都認識。',sides:i=>`${i.a}跟${i.b}一左一右。`,ambush:i=>`${i.a}從角落跳出來，${i.b}嚇了一跳。`,what:i=>`${i.a}看著${i.b}，看不懂。`,waited:i=>`${i.a}埋伏了半天，什麼都沒等到。`,race:i=>`${i.a}跟${i.b}突然繞著店裡跑起來。`,sleepgod:i=>`店裡再吵，${i.a}都照睡不誤。`,nearby:i=>`${i.a}坐在 Jill 腳邊。`,best:i=>`${i.a}找到了看得見全店的位子。`,nap3:()=>'三隻貓睡成一團。',everyone:()=>'五隻貓難得同時出現在一個畫面裡。',rest:i=>i.rush?'剛忙完一波，Jill 坐下來喘口氣。':'店裡沒事，Jill 在沙發上坐了一下。',lap:i=>`${i.a}跳上了 Jill 的膝蓋。`,photo:i=>`客人拿起手機，拍了${i.a}一張。`,pet:i=>`Jill 蹲下來摸了摸${i.a}。`,dylan:()=>'打烊後，Dylan 還在沙發上。',
 play:i=>`${i.a}跟${i.b}玩起來了。`,swat:i=>`${i.a}玩到一半，輕輕拍了${i.b}一下。`,pressed:i=>`${i.a}靠著${i.b}睡著了。`,greeter:i=>`${i.a}在陌生客人旁邊待得很自在。`,cushion:i=>`${i.a}跟${i.b}擠在同一塊軟墊上。`,distracted:i=>`${i.a}本來要去吃飯，走到一半就忘了。`,guide:i=>`${i.a}回頭等${i.b}，帶他去吃飯。`,oldfriends:i=>`${i.g}跟${i.a}又見面了。`,dylancat:i=>`${i.a}對 Dylan 的態度，不像對陌生人。`,quiet:()=>'店關了，燈還亮著。',oddspot:i=>`${i.a}睡在一個奇怪的地方。`,newroom:()=>'擴建之後的第一個晚上，大家都在。',reading:i=>`Jill 在看書，${i.cats}在旁邊各睡各的。`,pause:()=>'Jill 在 Dylan 的桌邊站了一下。',company:i=>`${i.g}今天帶了人來。`,gift:i=>`${i.g}帶了東西來給店裡。`,anniversary:()=>'王先生與王太太的紀念日，Jill 請了甜點。',neighbors:i=>`${i.a}跟${i.b}在店裡打了招呼，原來認識。`,treat:i=>`Jill 請了${i.g}一份${i.d}。`,bagcat:i=>`橘子沒興趣，${i.a}對袋子比較有興趣。`,rainday:i=>`外面在下雨，${i.a}睡得更沉了。`,selfie:i=>`${i.g}想跟 Jill 合照。`,dishphoto:i=>`${i.d}上桌，客人先拍了一張。`,firstspecial:i=>`第一盤${i.d}從出菜口出去了。`,kidcat:i=>`小朋友盯著${i.a}看了很久，飯都忘了吃。`};
/* Photos are the bulk of the restaurant's history, so they do not live in the save string any more: the save
   keeps the record (kind, day, clock, caption, 珍藏), the picture goes to IndexedDB under the record's id. A
   browser without IndexedDB (or one that refuses it) falls back to keeping the picture inline, with a lower
   cap so localStorage stays safe. Backups always carry the pictures. */
const PHOTOS=new Map();let photoDB=null,photoDBFail=false,photoQueue=Promise.resolve();
function photoOpen(){return new Promise(res=>{if(photoDB)return res(photoDB);if(photoDBFail||!window.indexedDB)return res(null);try{const rq=indexedDB.open('jills-kitchen-photos',1);rq.onupgradeneeded=()=>{rq.result.createObjectStore('photos')};rq.onsuccess=()=>{photoDB=rq.result;photoDB.onclose=()=>{photoDB=null};photoDB.onversionchange=()=>{photoDB.close();photoDB=null};res(photoDB)};rq.onerror=()=>{photoDBFail=true;res(null)};rq.onblocked=()=>res(null)}catch(e){photoDBFail=true;res(null)}})}
function photoPut(id,data){PHOTOS.set(id,data);return photoOpen().then(db=>new Promise(res=>{if(!db)return res(false);try{const tx=db.transaction('photos','readwrite');tx.objectStore('photos').put(data,id);tx.oncomplete=()=>res(true);tx.onerror=()=>res(false);tx.onabort=()=>res(false)}catch(e){res(false)}}))}
function photoGet(id){if(!id)return Promise.resolve(null);if(PHOTOS.has(id))return Promise.resolve(PHOTOS.get(id));return photoOpen().then(db=>new Promise(res=>{if(!db)return res(null);try{const rq=db.transaction('photos').objectStore('photos').get(id);rq.onsuccess=()=>{if(rq.result)PHOTOS.set(id,rq.result);res(rq.result||null)};rq.onerror=()=>res(null)}catch(e){res(null)}}))}
function photoDel(id){PHOTOS.delete(id);photoOpen().then(db=>{if(!db)return;try{db.transaction('photos','readwrite').objectStore('photos').delete(id)}catch(e){}})}
function photoClear(){PHOTOS.clear();photoOpen().then(db=>{if(!db)return;try{db.transaction('photos','readwrite').objectStore('photos').clear()}catch(e){}})}
/* every picture of the album, for a backup: {id: dataURL} */
function photoAll(){const A=albumList();return Promise.all(A.map(p=>p.img?Promise.resolve([p.id,p.img]):photoGet(p.id).then(d=>[p.id,d]))).then(arr=>{const o={};for(const [id,d] of arr)if(id&&d)o[id]=d;return o})}
const PHOTO_BLANK='data:image/svg+xml,'+encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="360" height="270"><rect width="360" height="270" fill="#EFE3CF"/></svg>');
let photoWake=0;
/* what to put in an <img> right now: the picture if we have it, otherwise a blank while it loads (the album re-renders once) */
function photoSrc(p){if(p.img)return p.img;if(PHOTOS.has(p.id))return PHOTOS.get(p.id);photoGet(p.id).then(d=>{if(d&&!photoWake){photoWake=1;Promise.resolve().then(()=>{photoWake=0;if(sub==='book')keepScroll(showBook);if(lightbox)lightboxRender()})}});return PHOTO_BLANK}
/* pictures still inline in the save (older saves, or a failed IndexedDB write) move into the store when it works */
function photoMigrate(){const A=albumList();const inline=A.filter(p=>p.img);if(!inline.length)return;photoQueue=photoQueue.then(()=>photoOpen()).then(db=>{if(!db)return;return Promise.all(inline.map(p=>photoPut(p.id,p.img).then(ok=>{if(ok)delete p.img}))).then(()=>save())})}
function albumCap(){return photoDBFail?60:240}   /* ordinary photos kept; 珍藏 never rotate out */
function albumList(){if(!S.album){S.album=[];/* photos from before the album existed: all 珍藏, no clock */for(const k of Object.keys(S.mem||{}))if(S.mem[k]&&S.mem[k].img)S.album.push({kind:k,day:S.mem[k].day,clock:'',cap:MEMS[k]||k,txt:'',img:S.mem[k].img,keep:true});S.album.sort((a,b)=>a.day-b.day);for(const k in S.mem||{})if(S.mem[k])S.mem[k]={day:S.mem[k].day}/* the picture now lives in the album */}
 for(const p of S.album)if(!p.id)p.id='p'+p.day+'_'+p.kind+'_'+Math.random().toString(36).slice(2,8);return S.album}
function albumAllows(kind){const A=albumList();const today=A.filter(p=>p.day===S.day);if(today.length>=4)return false;const same=A.filter(p=>p.kind===kind);if(!same.length)return true;const last=same[same.length-1];if(S.day-last.day<3)return false;return today.filter(p=>!p.keep).length<2}
function eveningClock(){const m=Math.floor(21*60+30+Math.min(LIFE.t||0,180)*(75/180));const h=Math.floor(m/60),mm=m%60;return`${h}:${String(mm).padStart(2,'0')}`}
function albumAdd(kind,img,info){const A=albumList();if(ACH_BY_MEMO[kind])ach(ACH_BY_MEMO[kind]);if(A.length+1>=50)ach('photos50');const keep=!A.some(p=>p.kind===kind);const clock=R&&R.closing==null?clockStr():evening()?eveningClock():'';let txt='';try{txt=(MEM_TXT[kind]||(()=>''))(info||{})}catch(e){}
 const p={id:'p'+S.day+'_'+kind+'_'+Math.random().toString(36).slice(2,8),kind,day:S.day,clock,cap:MEMS[kind]||kind,txt,keep};A.push(p);
 photoPut(p.id,img).then(ok=>{if(!ok){p.img=img;save()}});   /* no store: the picture stays in the save */
 const ord=A.filter(p=>!p.keep);while(ord.length>albumCap()){const old=ord.shift();A.splice(A.indexOf(old),1);photoDel(old.id)}return p}
function catBy(id){return CATS?CATS.find(c=>c.def.id===id):null}
function evening(){return(R&&R.closing!=null)||['summary','shop'].includes(phase)}
function jillA(){const J=view().jill;const idle=!R||(!J.cur&&!(J.q&&J.q.length)&&!J.moving);if(R&&phase==='service'&&R.closing==null&&J.room&&J.room!=='main')return{x:PASS.x,y:PASS.y,idle:false,sit:false};if(R&&phase==='service'&&R.closing==null&&J.rest){return{x:LIFE.jill.x,y:SOFA.front+10,idle:false,sit:true}}if(R&&phase==='service'&&R.closing==null){const near=Math.hypot(J.x-PASS.x,J.y-PASS.y)<30;return{x:PASS.x,y:PASS.y,idle:idle&&near,sit:false}}return{x:J.x,y:J.y,idle,sit:!!J.sit}}
function slotPos(s){const a=jillA();const y=Math.min(a.y+(a.sit?4:2),FB-6);return s==='R'?{x:a.x+22,y}:s==='L'?{x:a.x-22,y}:s==='R2'?{x:a.x+31,y:y+2}:s==='L2'?{x:a.x-31,y:y+2}:{x:a.x+rand(-10,10),y:y-16}}
function tableClear(x,y){const V=view();for(const t of V.tables){const dx=(x-t.x)/(t.seats===4?50:42),dy=(y-t.y+10)/25;if(dx*dx+dy*dy<1)return false}return true}
function randFloor(){for(let i=0;i<16;i++){const x=rand(96,316),y=rand(140,FB-14);if(tableClear(x,y)&&!(y<SOFA.front+6&&x<SOFA.x1+6))return{x,y}}return{x:rand(96,300),y:FB-12}}
function guestPts(){const out=[];if(!R)return out;for(const g of R.groups){if(g.state==='leave'||(g.room||'main')!=='main')continue;if(g.table!=null&&!['arrive','queue','toTable'].includes(g.state)){const t=R.tables[g.table];out.push({x:t.x,y:t.y,g})}else out.push({x:g.x,y:g.y,g})}return out}
function familiar(g){return g&&g.reg&&(g.reg==='dylan'||(S.catFam&&S.catFam[g.reg]||0)>=4)}
function scorePt(c,p){const id=c.def.id,a=jillA();let s=Math.random()*20;const dj=Math.hypot(p.x-a.x,p.y-a.y);const near=(o,w)=>{if(!o||o.hidden)return 0;return w*Math.max(0,120-Math.hypot(p.x-o.x,p.y-o.y))/120*20};
 if(id==='tora'){s+=Math.max(0,160-dj)/160*30+near(catBy('mikan'),.6);for(const q of guestPts())if(!familiar(q.g))s-=Math.max(0,90-Math.hypot(p.x-q.x,p.y-q.y))/90*25}
 if(id==='ban'){s+=Math.max(0,160-dj)/160*18+near(catBy('tora'),1)+near(catBy('mikan'),.8)+near(catBy('mei'),.5)}
 if(id==='mikan'){s+=near(catBy('ban'),1)+near(catBy('tora'),.8)+near(catBy('mei'),.6)}
 if(id==='mei'){s+=(p.y<170?14:0)+Math.abs(p.x-206)/10}
 if(id==='snow'){s+=Math.max(0,120-Math.hypot(p.x-SPOT.bed.x,p.y-SPOT.bed.y))/120*14}
 return s}
function pickFloor(c){let best=null,bs=-1e9;for(let i=0;i<7;i++){const p=randFloor();const sc=scorePt(c,p);if(sc>bs){bs=sc;best=p}}return best}
function catJump(c,x1,y1,next){c.st='jump';c.jmp={x0:c.x,y0:c.y,x1,y1,t:0,d:c.race?.4:.55,next};c.face=x1>=c.x?1:-1}
function catWalk(c,x,y,after,t){c.st='walk';c.tx=x;c.ty=y;c.after=after;c.afterT=t||rand(3,7);c.stareAt=null;
 /* never walk through the sofa: go round its front */
 const box={a:SOFA.x0-6,b:SOFA.x1+6,t:SOFA.back-8,d:SOFA.front+2};const inside=(px,py)=>px>box.a&&px<box.b&&py>box.t&&py<box.d;
 c.via=(!inside(c.x,c.y)&&!inside(x,y)&&segHitsRect(c.x,c.y,x,y,box))?{x:clamp((c.x+x)/2,box.a,box.b),y:box.d+10}:null}
function freeFloorCat(c){return !c.away&&c.perch<0&&!c.sofa&&['rest','walk','daze','side'].includes(c.st)&&!c.guest&&!c.hidden}
const SPOT={bed:{x:262,y:124},scr:{x:126,y:358},scr2:{x:226,y:114},cave:{x:318,y:126},bowl:{x:164,y:360},toy:{x:100,y:324}};
const OCC={scr:null,scr2:null,cave:null,toy:null,bench0:null,bench1:null,bench2:null,bed:[]};const TOY={amp:1};let FOOD=1;
function spotFree(k){return k==='bed'?OCC.bed.length<2:!OCC[k]}
const GEAR_OCC={};
function releaseSpots(c){for(const k in GEAR_OCC)if(GEAR_OCC[k]===c)GEAR_OCC[k]=null;if(c.st!=='gear'&&!c.away)c.gear=null;for(const k of['scr','scr2','cave','toy','bench0','bench1','bench2'])if(OCC[k]===c)OCC[k]=null;c.benchI=-1;OCC.bed=OCC.bed.filter(x=>x!==c);if(SIDE.R===c)SIDE.R=null;if(SIDE.L===c)SIDE.L=null;c.slot=null;c.hidden=false;c.peekT=0;c.sofa=null;c.sofaOn=false;
 /* a perch reserved for a climb that never happened would stay booked forever */if(c.goPerch>=0&&c.perch!==c.goPerch&&perchOcc[c.goPerch]===c){perchOcc[c.goPerch]=null;c.goPerch=-1}}
function leavePerch(c,then){const p=TREE.perches[c.perch];perchOcc[c.perch]=null;c.perch=-1;if(p.t===3){c.chain=WALL.slice(0,p.wi).reverse().map(w=>({x:w.x,y:w.y-3})).concat([{x:p.ax,y:p.ay}]);c.chainEnd=then||'decide';const n=c.chain.shift();catJump(c,n.x,n.y,c.chain.length?'chain':c.chainEnd)}else catJump(c,p.x+(p.t===2?-1:1)*rand(24,40),rand(338,350)+DY,then||'decide')}
function goPerch(c,i){perchOcc[i]=c;c.goPerch=i;const p=TREE.perches[i];catWalk(c,p.ax,p.ay||350+FY,'climb')}
function catGo(c,what){const s=SPOT;releaseSpots(c);
 if(what==='scr'){OCC.scr=c;catWalk(c,s.scr.x-15,s.scr.y+1,'scr')}
 else if(what==='scr2'){OCC.scr2=c;catWalk(c,s.scr2.x-11,s.scr2.y+1,'scr')}
 else if(what==='cave'){OCC.cave=c;catWalk(c,s.cave.x-20,s.cave.y+6,'cave')}
 else if(what==='bed'){OCC.bed.push(c);const k=OCC.bed.length;catWalk(c,s.bed.x+(k===1?-5:6),s.bed.y+1,'bed')}
 else if(what==='eat'){const i=CATS.filter(o=>o.st==='eat'||o.after==='eat').length;catWalk(c,s.bowl.x+[-14,14,0,-26,26][i%5],s.bowl.y+[0,0,6,4,4][i%5]+1,'eat')}
 else if(what==='toy'){OCC.toy=c;catWalk(c,s.toy.x-6,350+FY,'toy')}}
function freePerches(){return TREE.perches.map((_,i)=>i).filter(i=>!perchOcc[i]&&perchVis(i))}
function sleepHere(c,tmin,tmax){c.st='sleep';c.pose=pick(['curl','loaf','curl',c.def.id==='tora'?'belly':'loaf',c.def.id==='snow'?'belly':'curl']);c.t=rand(tmin||14,tmax||30);c.slept=0}
/* ---- Jill-side seats (樾樾 × 小齁) ---- */
function goJill(c){releaseSpots(c);if(LIFE.jill.pos&&(evening()?LIFE.plan==='sofa':(LIFE.jill.on||LIFE.jill.reserved))){goSofaJill(c);return}const id=c.def.id;const rival=id==='tora'?catBy('ban'):id==='ban'?catBy('tora'):null;let slot=null;
 if(!SIDE.R)slot='R';else if(SIDE.R===rival&&rival){const r=Math.random();
  if(r<.3)slot=SIDE.L?'B':'L';else if(r<.5)slot='R2';else if(r<.65)slot='B';else if(r<.8){const p=pickFloor(c);catWalk(c,p.x,p.y,'rest');return}
  else{slot='R';const o=rival;SIDE.R=null;o.slot=null;if(!SIDE.L){SIDE.L=o;o.slot='L';const q=slotPos('L');o.st='walk';o.tx=q.x;o.ty=q.y;o.after='side'}else{o.st='rest';o.pose='sit';o.t=rand(1,3)}}}
 else slot=SIDE.L?(Math.random()<.5?'L2':'B'):'L';
 if(slot==='R'||slot==='L')SIDE[slot]=c;c.slot=slot;const q=slotPos(slot);c.lag=id==='tora'?rand(2,6):id==='ban'?rand(1,3):rand(1,4);c.lagT=0;catWalk(c,q.x,q.y,'side')}
/* ---- decisions ---- */
/* ---- 2.0: the things bought for the cats. A piece is a spot with poses and a personality weight; the side room's
   pieces are reached by a trip through the arch (the cat is off the dining-room floor while it is there). ---- */
function catGoGear(c,G){if(!G)return;releaseSpots(c);GEAR_OCC[G.k]=c;c.gear=G.k;
 if(G.room==='side'){catWalk(c,SIDE_ARCH.x+SIDE_ARCH.w/2,108,'gearAway');return}
 catWalk(c,G.x+(G.k==='box'?0:0),G.y+(G.k==='box'?2:0),'gear')}
function gearUsed(c,G){S.gearUse=S.gearUse||{};const U=S.gearUse[G.k]=S.gearUse[G.k]||{};const first=!U[c.def.id];U[c.def.id]=S.day;const nm=catName(c.def);
 if(first){ach('newspot');logLine('cat',`${nm}第一次用了${G.n}。`,'cat');if(G.room==='main')memo('newspot',c.x,c.y,{a:nm,g:G.n,subj:[c]});else memo('newspot',G.x,G.y,{a:nm,g:G.n,room:'side',subj:[{x:G.x,y:G.y}]})}
 if(G.k==='box')memo('boxcat',c.x,c.y,{a:nm,subj:[c]});if(G.k==='perch')memo('window',G.x,G.y,{a:nm,room:'side',subj:[{x:G.x,y:G.y}]})}
function gearArrive(c){const G=CATGEAR.find(x=>x.k===c.gear);if(!G||!gearOn(G.k)){c.gear=null;catDecide(c);return}c.st='gear';c.pose=pick(G.poses);c.face=Math.random()<.5?1:-1;c.t=G.k==='box'?rand(20,45):rand(25,60);c.boxSeen={};gearUsed(c,G)}
function gearTick(c,dt){const G=CATGEAR.find(x=>x.k===c.gear);c.moving=false;c.t-=dt;
 if(G&&G.k==='box'&&!c.away){/* the ambush: a cat passing the box gets pounced on, both run */for(const o of CATS){if(o===c||o.hidden||o.perch>=0||o.sofa||!['walk','race','chase'].includes(o.st))continue;const d=Math.hypot(o.x-c.x,o.y-c.y);if(d>44)continue;const key=o.def.id+Math.floor((R?R.t:0)/8);if(c.boxSeen[key])continue;c.boxSeen[key]=1;if(Math.random()<.6){memo('ambush',c.x,c.y,{a:catName(c.def),b:catName(o.def),subj:[c,o]});logLine('cat',`${catName(c.def)}從紙箱裡跳出來，${catName(o.def)}嚇了一跳。`,'cat');GEAR_OCC[G.k]=null;c.gear=null;c.gearCD=60;const p=pickFloor(c);c.run=1;catWalk(c,p.x,p.y,'rest');const q=pickFloor(o);o.run=1;catWalk(o,q.x,q.y,'rest');return}}}
 if(G&&G.k==='tunnel'&&c.away&&c.t<20&&!c.dashed){/* the dash through the tunnel: out the other end */c.dashed=1;c.ax=G.x+(c.aface>0?34:-34);c.aface=c.aface>0?1:-1;c.pose='sit';memo('tunnel',c.ax,c.ay,{a:catName(c.def),room:'side',subj:[{x:c.ax,y:c.ay}]})}
 if(c.t<=0){if(c.away){c.away=null;c.hidden=false;c.x=SIDE_ARCH.x+SIDE_ARCH.w/2;c.y=110;c.face=-1;c.dashed=0}GEAR_OCC[c.gear]=null;c.gear=null;c.gearCD=rand(40,120);c.st='rest';c.pose='stretch';c.t=1.4}}
function catDecide(c){c.guest=null;c.moving=false;c.run=0;const id=c.def.id;const ev=evening();const a=jillA();if(c.gearCD>0)c.gearCD=Math.max(0,c.gearCD-1);
 if(id==='snow'&&c.forgot==='eat'){c.forgot=null;c.distractedOnce=1;if(Math.random()<.4){catWalk(c,SPOT.bowl.x+8,SPOT.bowl.y-2,'eat');return}}
 if(c.sofa){if(c.sofaOn){sofaDecide(c);return}c.sofa=null}
 if(c.perch>=0){const stay=id==='snow'?.8:id==='mei'?.65:.4;if(Math.random()<stay){if(id==='snow'||Math.random()<.3)sleepHere(c,18,45);else{c.st='rest';c.pose=pick(['sit','loaf','groom','sit','yawn']);c.t=rand(6,14)}return}leavePerch(c,'decide');return}
 releaseSpots(c);const fp=freePerches();const near=CATS.filter(o=>o!==c&&freeFloorCat(o)&&Math.hypot(o.x-c.x,o.y-c.y)<100);
 const W=[];const add=(k,w)=>{if(w>0)W.push([k,w])};
 const jillW=(id==='tora'?6:id==='ban'?5:id==='mikan'?(a.idle?4.5:2.2):id==='mei'?(a.idle?2:.6):.5)*(ev?2.6:1);
 add('jill',jillW);add('wander',id==='mikan'?1.6:id==='snow'?.5:1.1);add('rest',id==='tora'?2.2:1.2);
 {const W=wxNow();const wetW=W==='rain'||W==='storm';add('sleep',(id==='snow'?8:id==='tora'?1.4:id==='mei'?1.1:1.2)*(wetW?1.5:W==='hot'?1.35:W==='cool'?.85:1));if(W==='storm'&&id==='tora')add('jill',2)}
 add('perch',fp.length?(id==='mei'?4.5:id==='snow'?1.2:id==='mikan'?.9:1):0);
 add('scr',spotFree('scr')?(id==='tora'?1:.6):0);add('scr2',spotFree('scr2')?.5:0);add('cave',spotFree('cave')?(id==='tora'?.9:.5):0);add('bed',spotFree('bed')?(id==='snow'?3:id==='ban'&&OCC.bed.some(o=>o.def.id==='mei')?2.4:.8):0);
 add('eat',id==='mikan'?1:.5);add('toy',spotFree('toy')?(id==='mikan'?1:.4)*(wxNow()==='cool'?1.4:wxNow()==='hot'?.6:1):0);
 add('sofa',sofaWeight(c));
 for(const G of CATGEAR){if(!gearOn(G.k)||!G.poses||(G.need&&!projOn(G.need)))continue;if(GEAR_OCC[G.k]&&GEAR_OCC[G.k]!==c)continue;const w=(G.w[id]||.3)*(G.room==='side'?(ev?.35:.7):1)*(c.gearCD>0?0:1)*(S.day-(S.gear[G.k]||0)<=1?1.8:1);add('gear:'+G.k,w)}
 {const fs=[0,1,2].filter(benchFree);const standing=R&&R.groups.some(g=>g.state==='queue'&&g.spot&&g.spot.k==='stand');if(fs.length>=2&&!standing&&![0,1,2].some(i=>OCC['bench'+i]))add('bench',id==='mei'?.5:id==='snow'?.15:.25)}
 if(R&&phase==='service'){const dg=R.groups.find(g=>g.reg==='dylan'&&g.table!=null&&['reading','wait','eat','check'].includes(g.state)&&!(g.catT>R.t)&&!CATS.some(o=>o.guest===g));if(dg)add('visitDylan',id==='tora'?2:id==='mikan'?1.4:id==='ban'?.9:id==='mei'?.5:.2)}
 {const D=LIFE.dylan;if(D&&!D.onSofa&&(D.seated||D.state==='stand'||D.state==='crouch'))add('nearDylan',id==='tora'?.9:id==='mikan'?.6:id==='ban'?.4:0)}
 if(id==='ban'){add('nearTora',1.3);add('nearRou',1.1);add('nearBao',.7)}
 if(id==='mikan'){add('nearHou',1.8);add('nearTora',1.4);add('watchBao',1);if(BAO_LAST&&ctime-BAO_LAST.t>6&&ctime-BAO_LAST.t<70)add('imitate',1.4);if(!c.ambCD||ctime>c.ambCD)add('ambush',.7);add('stare',.9)}
 if(id==='mei'){add('watch',2);if(CATS.some(o=>o.st==='hide2'))add('wander',1.5)}
 if(RACE_CD<=0){const o=catBy(id==='tora'?'snow':id==='snow'?'tora':'');const ok=o&&!o.hidden&&o.perch<0&&!o.sofa&&!['jump','race','dash','visit','hide'].includes(o.st)&&Math.hypot(o.x-c.x,o.y-c.y)<260;if(ok&&id==='tora')add('race',1.4);if(ok&&id==='snow'&&!['sleep','bed'].includes(o.st))add('race',.25)}
 if(near.length&&['ban','mikan'].includes(id))add('play',.5);
 if(id==='ban'){const m=catBy('mikan');if(m&&freeFloorCat(m)&&['rest','daze','stare'].includes(m.st)&&Math.hypot(m.x-c.x,m.y-c.y)<230&&!(c.playCD>ctime))add('seekPlay',1.3)}
 if(id==='tora'){const m=catBy('mikan');if(m&&!m.hidden&&m.perch<0&&!m.sofa&&['rest','sleep','bed'].includes(m.st))add('nearRou',1)}
 /* 包包 forgot where he was going: 小齁 notices and brings him along */
 if(id==='ban'){const b=catBy('snow');if(b&&b.forgot==='eat'&&!b.hidden&&Math.hypot(b.x-c.x,b.y-c.y)<220)add('guideBao',3)}
 if(id==='snow'&&propOn('oranges')&&!c.bagDone&&Math.hypot(c.x-46,c.y-(FB-14))>30)add('bag',2.5);
 const ch=wpick(W,o=>o[1])[0];
 switch(ch){
 case'jill':goJill(c);break;
 case'bag':c.bagDone=1;catWalk(c,46,FB-14,'sleep');break;
 case'wander':{let p=pickFloor(c);if(id==='mei'){const h=CATS.find(o=>o.st==='hide2');if(h&&Math.random()<.4)p={x:clamp(h.x+rand(-30,30),96,316),y:clamp(h.y+rand(-16,16),140,FB-10)}}catWalk(c,p.x,p.y,'rest');if(id==='mikan'&&Math.random()<.35)c.stareAt=rand(20,60);break}
 case'rest':c.st='rest';c.pose=pick(id==='tora'?['groom','groom','sit','loaf']:['sit','groom','loaf','yawn']);c.t=rand(4,10);break;
 case'sleep':{if(id==='snow'){const spots=[];if(spotFree('bed'))spots.push('bed');const hi=[6,13,2].filter(i=>fp.includes(i));if(hi.length)spots.push('perch');const ss=sofaSlots(c).some(x=>x.kind==='seat');if(ss)spots.push('sofa');if(Math.random()<.3||!spots.length){sleepHere(c,25,70);break}const s=pick(spots);if(s==='bed'){catGo(c,'bed')}else if(s==='sofa'){const sl=pickSofaSlot(c,false);if(sl){c.wantSleep=1;goSofaSlot(c,sl)}else sleepHere(c,25,70)}else goPerch(c,pick(hi));c.wantSleep=1;break}
  if(id==='tora'&&R){const fg=R.groups.find(g=>g.table!=null&&g.reg&&(g.reg==='dylan'||(S.catFam&&S.catFam[g.reg]||0)>=8)&&['wait','eat','order'].includes(g.state));if(fg&&Math.random()<.3){const t=R.tables[fg.table];catWalk(c,clamp(t.x+pick([-32,32]),96,316),Math.min(FB-10,t.y+18),'sleep');break}}
  if(id==='tora'||id==='ban'){goJill(c);c.wantSleep=1;break}
  const p=pickFloor(c);catWalk(c,p.x,p.y,'sleep');break}
 case'perch':{let i;if(id==='mei'){const best=[6,13,12,2,11].filter(k=>fp.includes(k));i=best.length?best[0]:pick(fp)}else if(id==='tora'){const low=[3,0,1].filter(k=>fp.includes(k));i=low.length?pick(low):pick(fp)}else i=pick(fp);goPerch(c,i);break}
 case'nearTora':case'nearRou':case'nearHou':case'nearBao':case'watchBao':{const o=catBy({nearTora:'tora',nearRou:'mikan',nearHou:'ban',nearBao:'mei',watchBao:'mei'}[ch]);if(!o||o.hidden){const p=pickFloor(c);catWalk(c,p.x,p.y,'rest');break}
  const off=ch==='watchBao'?rand(55,85):rand(18,40);const ang=rand(0,6.28);const x=clamp(o.x+Math.cos(ang)*off,96,316),y=clamp((o.perch>=0?Math.min(o.y+40,FB-14):o.y)+Math.sin(ang)*off*.4,140,FB-10);catWalk(c,x,y,ch==='watchBao'?'watch':(o.st==='sleep'||o.st==='bed')&&Math.random()<.6?'sleep':'rest');c.lookAt=o;break}
 case'imitate':{const b=BAO_LAST;BAO_LAST=null;if(b.perch!=null&&!perchOcc[b.perch]&&perchVis(b.perch))goPerch(c,b.perch);else catWalk(c,clamp(b.x+rand(-24,24),96,316),clamp(b.y+30,140,FB-10),'rest');break}
 case'watch':{const p=Math.random()<.5?{x:rand(104,140),y:rand(118,132)}:pickFloor(c);catWalk(c,p.x,p.y,'watch');break}
 case'stare':c.st='stare';c.t=rand(3,8);c.pose='sit';c.face=Math.random()<.5?1:-1;break;
 case'ambush':startAmbush(c);break;
 case'sofa':{const sl=pickSofaSlot(c,false);if(sl)goSofaSlot(c,sl);else{const p=pickFloor(c);catWalk(c,p.x,p.y,'rest')}break}
 case'bench':{const fs=[0,1,2].filter(benchFree);if(!fs.length){const p=pickFloor(c);catWalk(c,p.x,p.y,'rest');break}const i=pick(fs);releaseSpots(c);OCC['bench'+i]=c;c.benchI=i;catWalk(c,BENCH.x+20,BENCH.seats[i]+8,'benchUp');break}
 case'visitDylan':{const g=R.groups.find(g=>g.reg==='dylan'&&g.table!=null);if(!g){const p=pickFloor(c);catWalk(c,p.x,p.y,'rest');break}releaseSpots(c);const t=R.tables[g.table];c.guest=g;catWalk(c,clamp(t.x+rand(-12,12),96,316),Math.min(FB-8,t.y+20),'visit');S.dylan.clues.pet=(S.dylan.clues.pet||0)+1;break}
 case'nearDylan':{const D=LIFE.dylan;if(!D){const p=pickFloor(c);catWalk(c,p.x,p.y,'rest');break}const off=rand(18,34),ang=rand(0,6.28);catWalk(c,clamp(D.x+Math.cos(ang)*off,96,316),clamp(D.y+(D.seated?rand(14,26):Math.abs(Math.sin(ang))*off*.4+2),140,FB-10),'rest');c.lookAt=D;break}
 case'race':startRace(c);break;
 case'play':{const o=pick(near);startPlay(c,o);break}
 case'seekPlay':{const m=catBy('mikan');c.playCD=ctime+rand(50,110);c.target=m;catWalk(c,clamp(m.x+(c.x<m.x?-22:22),96,316),clamp(m.y+4,140,FB-10),'playWith');break}
 case'guideBao':{const b=catBy('snow');catWalk(c,clamp(b.x+(c.x<b.x?-20:20),96,316),clamp(b.y+2,140,FB-10),'guide');break}
 default:if(ch.startsWith('gear:'))catGoGear(c,CATGEAR.find(G=>G.k===ch.slice(5)));else catGo(c,ch)}}
/* a play bout between two cats; 柔柔 may end it with a mischievous little swat (play, not a fight) */
function startPlay(c,o){releaseSpots(o);releaseSpots(c);const t=rand(2.5,4);c.st='play';c.t=t;c.partner=o;o.st='play';o.t=t;o.partner=c;o.guest=null;c.face=o.x>=c.x?1:-1;o.face=-c.face;sfx.catPlay();
 const rou=c.def.id==='mikan'?c:o.def.id==='mikan'?o:null,hou=c.def.id==='ban'?c:o.def.id==='ban'?o:null;memo('play',(c.x+o.x)/2,(c.y+o.y)/2,{a:catName(c.def),b:catName(o.def),subj:[c,o]});
 if(rou&&hou&&Math.random()<.4){rou.swatT=t*.55;rou.swatAt=hou}}
function catArrive(c){const a=c.after;const id=c.def.id;
 if(a==='playWith'){const m=c.target;c.target=null;if(m&&freeFloorCat(m)&&['rest','daze','stare','sleep'].includes(m.st)&&Math.hypot(m.x-c.x,m.y-c.y)<60){startPlay(c,m);return}c.st='rest';c.pose='sit';c.t=rand(2,4);return}
 if(a==='guide'){const b=catBy('snow');if(b&&b.forgot==='eat'&&Math.hypot(b.x-c.x,b.y-c.y)<60){b.forgot=null;b.st='walk';b.tx=SPOT.bowl.x+8;b.ty=SPOT.bowl.y-2;b.after='eat';b.afterT=0;b.moving=true;b.run=0;memo('guide',(c.x+b.x)/2,(c.y+b.y)/2,{a:catName(c.def),b:catName(b.def),subj:[b]});catWalk(c,SPOT.bowl.x-14,SPOT.bowl.y-4,'rest',rand(3,5));return}c.st='rest';c.pose='sit';c.t=rand(2,4);return}
 if(a==='sofaUp'){const s=c.sofa;if(!s){catDecide(c);return}if(s.kind==='seat'||s.kind==='lap')catJump(c,s.x,s.y,'sofaLand');else{c.chain=[{x:s.x,y:s.y}];c.chainEnd='sofaLand';catJump(c,clamp(s.x,SOFA.seatL+8,SOFA.seatR-8),SOFA.catY,'chain')}return}
 if(a==='climb'){const i=c.goPerch;c.perch=i;const P0=TREE.perches[i];if(P0.t===3){c.chain=WALL.slice(0,P0.wi+1).map(w=>({x:w.x,y:w.y-3}));c.chainEnd='perch';const n=c.chain.shift();catJump(c,n.x,n.y,c.chain.length?'chain':'perch')}else catJump(c,P0.x,P0.y,'perch');return}
 if(a==='visit'){const g=c.guest;if(g&&R&&R.groups.includes(g)&&g.table!=null){c.st='visit';c.pose='sit';c.t=7;g.catT=R.t+7;if(catCheer(g,.08)>0){const tb=R.tables[g.table];if(tb)addFloat(tb.x,tb.y-54,'心情 UP','#F29AAE',0)}c.hearts.push({x:0,y:-26,t:0});if(g.reg&&g.reg!=='dylan'&&(S.catFam&&S.catFam[g.reg]||0)>=4){const tb=R.tables[g.table];memo('oldfriends',c.x,c.y,{g:g.name,a:catName(c.def),subj:[{x:tb.x,y:tb.y-6}]})}}else catDecide(c);return}
 if(a==='side'){c.st='side';c.lagT=0;const J=jillA();c.face=J.x>=c.x?1:-1;c.pose=c.wantSleep?'loaf':pick(['sit','sit','loaf',J.idle?'rub':'sit']);c.t=rand(10,24);c.sleepy=!!c.wantSleep;c.wantSleep=0;return}
 if(a==='sleep'){sleepHere(c,16,36);return}
 if(a==='watch'){c.st='rest';c.pose='sit';c.t=rand(8,16);c.face=c.x<206?1:-1;return}
 if(a==='scr'){c.st='scr';c.pose='scr';c.face=1;c.t=rand(3,5);return}
 if(a==='cave'){c.st='hide';c.hidden=true;c.x=SPOT.cave.x;c.y=SPOT.cave.y;c.t=rand(8,16);return}
 if(a==='bed'){c.st='bed';c.pose=Math.random()<.5?'knead':'curl';c.t=id==='snow'?rand(30,70):rand(10,20);c.kneadT=c.pose==='knead'?2.2:0;return}
 if(a==='eat'){c.st='eat';c.pose='eat';c.face=c.x<SPOT.bowl.x?1:-1;c.t=rand(4,6);return}
 if(a==='toy'){c.st='toy';c.pose='toy';c.face=1;c.t=rand(4,6);TOY.amp=2.5;return}
 if(a==='benchUp'){const i=c.benchI;if(i<0||OCC['bench'+i]!==c){catDecide(c);return}catJump(c,BENCH.x+2,BENCH.seats[i]-3,'benchLand');return}
 if(a==='hide2'){c.st='hide2';c.hidden=true;c.t=rand(15,40);c.seen={};return}
 if(a==='gear'){gearArrive(c);return}
 if(a==='gearAway'){const G=CATGEAR.find(x=>x.k===c.gear);if(!G||!gearOn(G.k)){c.gear=null;catDecide(c);return}c.away='side';c.hidden=true;c.ax=G.x;c.ay=G.y;c.aface=G.k==='perch'?1:(Math.random()<.5?1:-1);c.st='gear';c.pose=pick(G.poses);c.t=rand(28,70);gearUsed(c,G);return}
 if(a==='flee'){c.run=0;if(c.lookBack){c.lookBack=0;c.st='stare';c.t=1.6;c.face=c.x<(catBy('mei')||c).x?1:-1;return}}
 if(a==='raceNext'){raceStep(c);return}
 c.st='rest';c.pose=pick(['sit','groom','loaf','sit']);c.t=c.afterT||rand(3,7)}
/* ---- 柔柔 ambush ---- */
function hideSpots(){const out=[{x:74+14,y:FB-10},{x:318,y:FB-12},{x:SPOT.cave.x+22,y:SPOT.cave.y+2},{x:SPOT.scr2.x+14,y:SPOT.scr2.y+4},{x:LIFE.tv.x-15,y:LIFE.tv.y+3}];if(LIFE.tv.at!=='use')out.push({x:SOFA.x1+9,y:SOFA.front+2});for(const p of plantSpots())out.push({x:p.x+10,y:p.y+4});for(const t of view().tables)if(!t.group)out.push({x:t.x,y:t.y+4});return out}
function startAmbush(c){c.ambCD=ctime+rand(70,140);const b=catBy('mei');const sp=hideSpots();let best=pick(sp);if(b){const ref=b.st==='walk'?{x:b.tx,y:b.ty}:b;best=sp.sort((p,q)=>Math.hypot(p.x-ref.x,p.y-ref.y)-Math.hypot(q.x-ref.x,q.y-ref.y))[Math.floor(Math.random()*2)]||best}c.amb=best;catWalk(c,best.x,best.y,'hide2')}
function ambushTick(c,dt){c.t-=dt;if(c.peekT>0)c.peekT-=dt;
 for(const o of CATS){if(o===c||o.hidden||o.perch>=0)continue;if(!['walk','race','chase'].includes(o.st))continue;const d=Math.hypot(o.x-c.x,o.y-c.y);if(d>46)continue;const key=o.def.id+Math.floor(ctime/6);if(c.seen[key])continue;c.seen[key]=1;
  if(o.def.id==='mei'){if(Math.random()<.55){scare(c,o);return}}else{c.peekT=1.1}}
 if(c.t<=0){c.hidden=false;const r=Math.random();if(r<.45){c.st='daze';c.pose='daze';c.t=rand(2,4);memo('waited',c.x,c.y,{a:catName(c.def)})}else if(r<.75){c.st='rest';c.pose=pick(['sit','loaf']);c.t=rand(6,12)}else catDecide(c)}}
function scare(c,b){c.hidden=false;c.st='dash';c.target=b;c.t=.45;c.run=1;b.stareAt=null;memo('ambush',b.x,b.y,{a:catName(c.def),b:catName(b.def),subj:[c]});if(R)for(const g of R.groups)if(g.table!=null&&Math.hypot(R.tables[g.table].x-b.x,R.tables[g.table].y-b.y)<90)g.scared=true;sfx.catPlay();
 const r=Math.random();b.react=r<.25?'chase':r<.6?'glare':r<.75?'freeze':'ignore'}
function afterScare(c){const b=c.target;c.target=null;const r=b?b.react:'ignore';
 if(b){if(r==='chase'){releaseSpots(b);b.st='chase';b.target=c;b.t=2.2;b.run=1}else if(r==='glare'){releaseSpots(b);b.glareAt=c;catJump(b,b.x,b.y,'glare');b.jmp.d=.3;memo('what',b.x,b.y,{a:catName(b.def),b:catName(c.def),subj:[c]})}else if(r==='freeze'){releaseSpots(b);catJump(b,b.x,b.y,'decide');b.jmp.d=.35}}
 const q=Math.random();if(q<.4){const p=randFloor();c.run=1;catWalk(c,p.x,p.y,'rest')}else if(q<.6){const p=randFloor();c.run=1;c.lookBack=1;catWalk(c,p.x,p.y,'flee')}else if(q<.8){catJump(c,c.x+rand(-6,6),c.y,'decide');c.jmp.d=.3}else{c.run=1;c.circ=[{x:c.x+30,y:c.y-12},{x:c.x+10,y:c.y-30},{x:c.x-20,y:c.y-10}].map(p=>({x:clamp(p.x,96,316),y:clamp(p.y,140,FB-10)}));const n=c.circ.shift();catWalk(c,n.x,n.y,'circ')}}
/* ---- 樾樾 × 包包 race ---- */
function startRace(c){const o=catBy(c.def.id==='tora'?'snow':'tora');if(!o)return catDecide(c);RACE_CD=rand(200,360);const wasAsleep=['sleep','bed'].includes(o.st);releaseSpots(o);o.guest=null;o.wd=wasAsleep?rand(.5,.9):.2;
 const path=[];let lx=Math.random()<.5;for(let i=0;i<4;i++){lx=!lx;path.push({x:lx?rand(96,150):rand(262,316),y:rand(150,FB-14)})}
 const lead=c,fol=o;lead.path=path;lead.run=1;lead.st='walk';lead.after='raceNext';raceStep(lead);fol.st='race';fol.target=lead;fol.t=16;fol.run=1;fol.moving=false;fol.pose='daze';memo('race',c.x,c.y,{a:catName(c.def),b:catName(o.def),subj:[o]})}
function raceStep(c){const n=c.path&&c.path.shift();if(!n){c.run=0;c.path=null;const f=CATS.find(o=>o.st==='race'&&o.target===c);if(f){f.st='rest';f.run=0;f.target=null;finishRace(f)}finishRace(c);return}c.st='walk';c.tx=n.x;c.ty=n.y;c.after='raceNext';c.run=1}
function finishRace(c){c.run=0;if(c.def.id==='snow'){if(spotFree('bed')&&Math.random()<.4)catGo(c,'bed');else sleepHere(c,30,60)}else{c.st='rest';c.pose='groom';c.t=rand(4,8)}}
/* ---- memories ---- */
function memo(id,x,y,info){if(!MEMS[id])return;if(MEMQ.some(m=>m.id===id)||!albumAllows(id))return;MEMQ.push({id,x,y,info,room:(info&&info.room)||'main'})}
/* The frame is built from the subjects of the moment (info.subj: the cats, Jill, the guest…), not from one
   point: a close-up for one subject, wider when there are several, the whole room if that is what it takes.
   Whatever the caption names is inside the picture. */
function memFrame(m){const pts=[{x:m.x,y:m.y}].concat((m.info&&m.info.subj)||[]).filter(p=>p&&isFinite(p.x)&&isFinite(p.y));
 let x0=Math.min(...pts.map(p=>p.x-18)),x1=Math.max(...pts.map(p=>p.x+18)),y0=Math.min(...pts.map(p=>p.y-34)),y1=Math.max(...pts.map(p=>p.y+10));
 let w=Math.max(150,x1-x0),h=Math.max(112,y1-y0);if(w/h>4/3)h=w*3/4;else w=h*4/3;const cx=(x0+x1)/2,cy=(y0+y1)/2-2;
 const W=SV.w/SV.s,H=SV.h/SV.s;w=Math.min(w,W);h=Math.min(h,H);let fx=cx-w/2,fy=cy-h/2;fx=clamp(fx,-SV.ox/SV.s,W-SV.ox/SV.s-w);fy=clamp(fy,-SV.oy/SV.s,H-SV.oy/SV.s-h);return{x:fx,y:fy,w,h}}
function flushMem(){if(!MEMQ.length)return;for(const m of MEMQ.splice(0)){if(m.room!==room)continue;/* the camera only sees the room on screen */try{const f=memFrame(m);const sx=(SV.ox+f.x*SV.s)*DPR,sy=(SV.oy+f.y*SV.s)*DPR,sw=f.w*SV.s*DPR,sh=f.h*SV.s*DPR;const cv=mkCanvas(360,270),c=cv.getContext('2d');c.drawImage(sc,sx,sy,sw,sh,0,0,360,270);albumAdd(m.id,cv.toDataURL('image/jpeg',.68),m.info);S.mem=S.mem||{};if(!S.mem[m.id])S.mem[m.id]={day:S.day};FLASH={x:m.x,y:m.y,t:0};sfx.shutter();save()}catch(e){}}}
function memChecks(){if(!CATS)return;const T=catBy('tora'),H=catBy('ban'),B=catBy('mei'),Bb=catBy('snow');
 const nm=c=>catName(c.def);const atSide=c=>c&&c.st==='side'&&!c.moving&&(c.slot==='L'||c.slot==='R');if(atSide(T)&&atSide(H)&&T.slot!==H.slot){const a=jillA();memo('sides',a.x,a.y,{a:nm(T),b:nm(H),subj:[T,H]})}
 if(T&&T.st==='side'&&T.sleepy&&!T.moving&&T.t<T.t0-4){const a=jillA();memo('nearby',T.x,T.y,{a:nm(T),subj:[{x:a.x,y:a.y}]})}
 if(B&&B.perch>=0&&[6,13,12].includes(B.perch)&&B.st==='rest')memo('best',B.x,B.y+20,{a:nm(B)});
 if(Bb&&(Bb.st==='sleep'||Bb.st==='bed')&&R&&(R.fire>0||R.insp||R.thief||R.groups.length>=6))memo('sleepgod',Bb.x,Bb.y,{a:nm(Bb),subj:R.groups.filter(g=>g.table!=null).slice(0,3).map(g=>R.tables[g.table])});
 const sl=CATS.filter(c=>!c.hidden&&(c.st==='sleep'||c.st==='bed'||(c.st==='side'&&c.sleepy)));if(sl.length>=3){const cx=sl.reduce((a,c)=>a+c.x,0)/sl.length,cy=sl.reduce((a,c)=>a+c.y,0)/sl.length;const trio=sl.filter(c=>Math.hypot(c.x-cx,c.y-cy)<75);if(trio.length>=3)memo('nap3',cx,cy,{subj:trio})}
 {const L=LIFE.jill;const on=sofaCats();if(L.on&&evening()&&L.sinceSit>6){if(on.length>=1)memo('sofa',(SOFA.x0+SOFA.x1)/2,120,{cats:on.map(nm).join('、'),subj:on.concat([{x:L.x,y:SOFA.jy}])});if(on.length>=3)memo('sofafull',(SOFA.x0+SOFA.x1)/2,120,{n:on.length,subj:on.concat([{x:L.x,y:SOFA.jy}])})}
  const lap=on.find(c=>c.sofa.kind==='lap');if(L.on&&lap&&L.sinceSit>3)memo('lap',lap.x,lap.y,{a:nm(lap),subj:[{x:L.x,y:SOFA.jy}]});
  const D=LIFE.dylan;if(D&&D.onSofa&&evening())memo('dylan',D.x,SOFA.jy,{subj:L.on?[{x:L.x,y:SOFA.jy}]:[]})}
 /* 樾樾 pressed against 柔柔; 寶寶 and 小齁 sharing the cushion; 柔柔 relaxed beside a stranger; odd sleeping spots */
 {const M=catBy('mikan');if(T&&M&&T.st==='sleep'&&!T.hidden&&!M.hidden&&['sleep','rest','bed','side'].includes(M.st)&&Math.hypot(T.x-M.x,T.y-M.y)<28)memo('pressed',(T.x+M.x)/2,(T.y+M.y)/2,{a:nm(T),b:nm(M),subj:[T,M]});
  if(B&&H&&OCC.bed.includes(B)&&OCC.bed.includes(H)&&B.st==='bed'&&H.st==='bed')memo('cushion',SPOT.bed.x,SPOT.bed.y,{a:nm(H),b:nm(B),subj:[B,H]});
  if(M&&R&&phase==='service'&&['rest','sleep','daze'].includes(M.st)&&!M.hidden){const g=R.groups.find(g=>g.table!=null&&!g.reg&&['reading','wait','eat'].includes(g.state)&&Math.hypot(R.tables[g.table].x-M.x,R.tables[g.table].y-M.y)<44);M.calmT=g?(M.calmT||0)+1/30:0;if(g&&M.calmT>5)memo('greeter',M.x,M.y,{a:nm(M),subj:[R.tables[g.table]]})}
  for(const c of CATS){if(c.st==='sleep'&&!c.hidden&&c.perch<0&&!c.sofa&&(Math.hypot(c.x-DOOR.x,c.y-DOOR.y)<48||Math.hypot(c.x-PASS.x,c.y-PASS.y)<40))memo('oddspot',c.x,c.y,{a:nm(c)})}
{const W=wxNow();if((W==='rain'||W==='storm')&&R&&phase==='service'&&R.t>20){const c=CATS.find(c=>!c.hidden&&(c.st==='sleep'||c.st==='bed'||(c.st==='side'&&c.sleepy))&&c.y<230);if(c)memo('rainday',c.x,c.y,{a:nm(c),subj:[{x:109,y:44}]})}}
 if(Bb&&propOn('oranges')&&!Bb.hidden&&['sleep','rest'].includes(Bb.st)&&Math.hypot(Bb.x-46,Bb.y-(FB-14))<22)memo('bagcat',40,FB-10,{a:nm(Bb),subj:[Bb]});
  const L=LIFE.jill;if(evening()&&L.on&&L.act==='read'&&L.sinceSit>12){const asleep=CATS.filter(c=>!c.hidden&&(c.st==='sleep'||c.st==='bed'||(c.st==='side'&&c.sleepy)));if(asleep.length>=2)memo('reading',L.x,SOFA.jy,{cats:asleep.slice(0,3).map(nm).join('、'),subj:asleep.slice(0,3)});if(!LIFE.dylan&&asleep.length>=2)memo('quiet',L.x,SOFA.jy,{subj:asleep.slice(0,2)})}
  if(S.newRoom&&S.newRoom<S.day&&evening()&&CATS.filter(c=>!c.hidden).length>=3){const v=CATS.filter(c=>!c.hidden);memo('newroom',v.reduce((a,c)=>a+c.x,0)/v.length,v.reduce((a,c)=>a+c.y,0)/v.length,{subj:v});S.newRoom=0}}
 const vis=CATS.filter(c=>!c.hidden);if(vis.length===5){const cx=vis.reduce((a,c)=>a+c.x,0)/5,cy=vis.reduce((a,c)=>a+c.y,0)/5;if(vis.every(c=>Math.hypot(c.x-cx,c.y-cy)<100))memo('everyone',cx,cy,{subj:vis})}}
/* ---- update ---- */
let ctime=0;
function initCats(){CATS=CAT_DEF.map(d=>({def:d,x:0,y:0,st:'rest',pose:'sit',perch:-1,benchI:-1,t:rand(2,6),face:Math.random()<.5?1:-1,ph:Math.random()*10,cd:0,happy:0,hearts:[],after:null,tx:0,ty:0}));
 const T=catBy('tora'),H=catBy('ban'),B=catBy('mei'),Rr=catBy('mikan'),Bb=catBy('snow');
 T.x=PASS.x-26;T.y=FB-8;T.pose='groom';H.perch=0;perchOcc[0]=H;H.x=TREE.perches[0].x;H.y=TREE.perches[0].y;B.perch=6;perchOcc[6]=B;B.x=TREE.perches[6].x;B.y=TREE.perches[6].y;Rr.x=140;Rr.y=FB-30;Rr.pose='sit';
 OCC.bed.push(Bb);Bb.x=SPOT.bed.x-5;Bb.y=SPOT.bed.y+1;Bb.st='bed';Bb.pose='curl';Bb.t=rand(20,40)}
function updateCats(dt,now){if(!CATS)initCats();ctime+=dt;RACE_CD-=dt;TOY.amp=Math.max(1,TOY.amp-dt*.6);if(FLASH){FLASH.t+=dt;if(FLASH.t>.5)FLASH=null}
 for(const c of CATS){c.ph+=dt*(c.run?2.4:1);c.cd=Math.max(0,c.cd-dt);if(c.wcd>0)c.wcd-=dt;if(c.wakeT>0)c.wakeT-=dt;if(c.flickT>0)c.flickT-=dt;if(c.hopT>0)c.hopT-=dt;if(c.forgot&&c.st!=='daze'&&c.st!=='walk')c.forgot=null;
  if(c.swatT!=null&&c.st==='play'){c.swatT-=dt;if(c.swatT<=0){c.swatT=null;const o=c.swatAt;c.swatAt=null;c.swatShow=.5;if(o&&o.st==='play'){o.hopT=.45;o.hearts.push({x:0,y:-26,t:0});memo('swat',(c.x+o.x)/2,(c.y+o.y)/2,{a:catName(c.def),b:catName(o.def),subj:[c,o]})}}}if(c.swatShow>0)c.swatShow-=dt;if(c.happy>0){c.happy-=dt;if(c.happy<=0){c.quiet=0;if(c.st==='pet')catDecide(c)}}for(const h of c.hearts)h.t+=dt;c.hearts=c.hearts.filter(h=>h.t<1.4);
  switch(c.st){
  case'jump':{const j=c.jmp;j.t+=dt;const u=Math.min(1,j.t/j.d);c.x=lerp(j.x0,j.x1,u);c.y=lerp(j.y0,j.y1,u)-Math.sin(u*Math.PI)*(Math.abs(j.x1-j.x0)+Math.abs(j.y1-j.y0)<4?7:22);if(u>=1){c.x=j.x1;c.y=j.y1;c.sofaLeaving=false;if(j.next==='sofaLand'){c.sofaOn=true;sofaSettle(c,true)}else if(j.next==='benchLand'){c.st='bench';c.pose=pick(['loaf','sit','sit']);c.face=1;c.t=c.def.id==='mei'?rand(20,50):rand(12,40);c.moving=false}else if(j.next==='chain'){const n=c.chain.shift();catJump(c,n.x,n.y,c.chain.length?'chain':c.chainEnd)}else if(j.next==='glare'){c.st='glare';c.pose='glare';c.t=rand(1.8,2.8);c.moving=false}else if(j.next==='perch'){if(c.wantSleep||(c.def.id==='snow'&&Math.random()<.7)){c.wantSleep=0;sleepHere(c,25,60)}else{c.st='rest';c.pose=pick(['sit','loaf','groom']);c.t=c.def.id==='mei'?rand(14,26):rand(6,12)}if(c.def.id==='mei')BAO_LAST={perch:c.perch,x:c.x,y:c.y,t:ctime}}else catDecide(c)}break}
  case'walk':{const spd=c.run?(c.st==='walk'&&c.after==='raceNext'?118:96):c.after==='visit'?60:c.after==='eat'?46:c.def.id==='snow'?28:34;
   if(c.via){const vx=c.via.x-c.x,vy=c.via.y-c.y,vd=Math.hypot(vx,vy),vv=spd*dt;if(vd>vv){c.x+=vx/vd*vv;c.y+=vy/vd*vv;c.face=vx>=0?1:-1;c.moving=true}else{c.x=c.via.x;c.y=c.via.y;c.via=null}break}
   const dx=c.tx-c.x,dy=c.ty-c.y,d=Math.hypot(dx,dy),v=spd*dt;
   /* a cat does not walk into the TV cabinet while someone is rolling it: wait a moment */
   {const tv=LIFE.tv;if(tv&&tv.mover&&d>v){const nx=c.x+dx/d*v,ny=c.y+dy/d*v;if(Math.hypot(nx-tv.x,ny-6-tv.y)<18&&Math.hypot(c.x-tv.x,c.y-6-tv.y)>=Math.hypot(nx-tv.x,ny-6-tv.y)){c.moving=false;break}}}
   if(c.stareAt!=null&&d<c.stareAt){c.stareAt=null;c.resume={tx:c.tx,ty:c.ty,after:c.after};c.st='stare';c.t=rand(2.5,7);c.pose='sit';c.moving=false;break}
   if(c.def.id==='snow'&&c.after==='eat'&&!c.forgot&&!c.distractedOnce&&d>40&&d<110&&Math.random()<dt*.35){c.distractedOnce=1;c.forgot='eat';c.st='daze';c.pose='daze';c.t=rand(4,7);c.moving=false;memo('distracted',c.x,c.y,{a:catName(c.def)});break}
   if(d>v){c.x+=dx/d*v;c.y+=dy/d*v;c.face=dx>=0?1:-1;c.moving=true}else{c.x=c.tx;c.y=c.ty;c.moving=false;if(c.after==='circ'){const n=c.circ&&c.circ.shift();if(n){c.tx=n.x;c.ty=n.y;break}c.run=0}catArrive(c)}break}
  case'rest':c.moving=false;c.t-=dt;if(c.lookAt&&!c.lookAt.hidden)c.face=c.lookAt.x>=c.x?1:-1;if(c.t<=0){c.lookAt=null;catDecide(c)}break;
  case'stare':c.moving=false;c.t-=dt;if(c.t<=0){if(c.resume&&Math.random()<.6){const r0=c.resume;c.resume=null;catWalk(c,r0.tx,r0.ty,r0.after)}else{c.resume=null;catDecide(c)}}break;
  case'daze':c.moving=false;c.t-=dt;if(c.t<=0){if(Math.random()<.5){c.st='rest';c.pose='stretch';c.t=1.5}else catDecide(c)}break;
  case'glare':c.moving=false;c.t-=dt;if(c.glareAt)c.face=c.glareAt.x>=c.x?1:-1;if(c.t<=0){c.glareAt=null;catDecide(c)}break;
  case'sleep':c.moving=false;c.t-=dt;c.slept+=dt;if(c.t<=0){c.st='daze';c.pose='daze';c.t=c.def.id==='snow'?rand(3,6):rand(1.5,3)}break;
  case'side':{const q=slotPos(c.slot||'B');const d=Math.hypot(q.x-c.x,q.y-c.y);c.t-=dt;if(c.t0==null)c.t0=c.t;
   if(d>30){c.lagT+=dt;if(c.lagT>c.lag){c.lagT=0;if(Math.random()<.62){c.lag=c.def.id==='tora'?rand(2,6):rand(1,3);catWalk(c,q.x,q.y,'side')}else{releaseSpots(c);catDecide(c)}}}
   else{const J=jillA();if(c.pose==='rub'&&!J.idle)c.pose='sit';if(c.sleepy)c.pose='loaf'}
   if(c.t<=0){c.t0=null;if(c.sleepy||Math.random()<.35){c.t=rand(10,22);c.sleepy=c.def.id==='tora'&&Math.random()<.5}else{releaseSpots(c);catDecide(c)}}break}
  case'wary':c.moving=false;c.t-=dt;if(c.warnG)c.face=c.warnG.x>=c.x?1:-1;if(c.t<=0){const r=Math.random();const fp=freePerches();if(r<.5)goJill(c);else if(r<.75&&[2,1,0,6].some(k=>fp.includes(k))){goPerch(c,[2,1,0,6].find(k=>fp.includes(k)))}else{let best=null,bs=-1;for(let i=0;i<6;i++){const p=randFloor();const s=Math.min(...guestPts().map(q=>Math.hypot(p.x-q.x,p.y-q.y)),999);if(s>bs){bs=s;best=p}}catWalk(c,best.x,best.y,'watch')}}break;
  case'hide2':ambushTick(c,dt);break;
  case'gear':gearTick(c,dt);break;
  case'dash':{c.t-=dt;const b=c.target;if(b){const dx=b.x-c.x,dy=b.y-c.y,d=Math.hypot(dx,dy);if(d>10){const v=150*dt;c.x+=dx/d*Math.min(v,d);c.y+=dy/d*Math.min(v,d);c.face=dx>=0?1:-1;c.moving=true}}if(c.t<=0){c.moving=false;afterScare(c)}break}
  case'race':{c.t-=dt;if(c.wd>0){c.wd-=dt;c.moving=false;c.pose='daze';if(c.target)c.face=c.target.x>=c.x?1:-1;break}const L=c.target;if(!L||c.t<=0||!L.path){c.st='rest';c.run=0;finishRace(c);break}const tx=L.x-L.face*14,ty=L.y+4;const dx=tx-c.x,dy=ty-c.y,d=Math.hypot(dx,dy);if(d>3){const v=122*dt;c.x+=dx/d*Math.min(v,d);c.y+=dy/d*Math.min(v,d);c.face=dx>=0?1:-1;c.moving=true}break}
  case'scr':c.t-=dt;c.sT=(c.sT||0)+dt;if(c.sT>.35){c.sT=0;if(Math.random()<.5)sfx.scratch()}if(c.t<=0){c.x-=4;catDecide(c)}break;
  case'hide':c.t-=dt;if(c.t<=0){c.hidden=false;c.x=SPOT.cave.x-20;c.y=SPOT.cave.y+6;c.face=-1;c.st='rest';c.pose='stretch';c.t=1.4;OCC.cave=null}break;
  case'bed':c.t-=dt;if(c.kneadT>0){c.kneadT-=dt;if(c.kneadT<=0)c.pose='curl'}if(c.t<=0){OCC.bed=OCC.bed.filter(x=>x!==c);c.st='daze';c.pose='daze';c.t=rand(2,5)}break;
  case'eat':c.t-=dt;if(c.t<=0){c.st='rest';c.pose='groom';c.t=rand(2,4)}break;
  case'toy':c.t-=dt;TOY.amp=Math.max(TOY.amp,2.2);if(c.t<=0){OCC.toy=null;catDecide(c)}break;
  case'bench':{c.t-=dt;const i=c.benchI;if(c.t<=0||i<0){if(i>=0&&OCC['bench'+i]===c)OCC['bench'+i]=null;c.benchI=-1;catJump(c,BENCH.x+22,BENCH.seats[Math.max(0,i)]+10,'decide')}break}
  case'chase':{c.t-=dt;const tg=c.target;if(!tg||c.t<=0){c.run=0;catDecide(c);break}const dx=tg.x-c.x,dy=tg.y-c.y,d=Math.hypot(dx,dy);if(d>12){const v=(c.run?90:72)*dt;c.x+=dx/d*v;c.y+=dy/d*v;c.face=dx>=0?1:-1;c.moving=true}else{c.moving=false;c.run=0;c.st='play';c.t=1.6;if(tg.st!=='hide2'){tg.st='play';tg.t=1.6;tg.partner=c;c.partner=tg;tg.face=-c.face}}break}
  case'visit':c.t-=dt;{const g=c.guest;if(!g||!R||!R.groups.includes(g)||g.state==='leave'||c.t<=0){catDecide(c);break}catCheer(g,dt*.035);if(Math.random()<dt*.5)c.hearts.push({x:0,y:-26,t:0})}break;
  case'play':c.t-=dt;c.moving=false;if(c.t<=0){c.partner=null;catDecide(c)}break;
  case'pet':c.moving=false;break}}
 /* 樾樾 is wary of strangers */
 const T=catBy('tora');if(T&&R&&phase==='service'&&!(T.wcd>0)&&T.perch<0&&!T.sofa&&!T.hidden&&['rest','walk','daze','stare'].includes(T.st)){for(const q of guestPts()){if(familiar(q.g))continue;if(Math.hypot(q.x-T.x,q.y-T.y)<72){releaseSpots(T);T.st='wary';T.t=rand(1.2,2.4);T.warnG=q;T.wcd=12;T.moving=false;const H=catBy('ban');if(H&&freeFloorCat(H)&&H.st!=='side'&&Math.random()<.35){releaseSpots(H);catWalk(H,clamp(T.x+rand(-40,40),96,316),clamp(T.y+rand(-10,14),140,FB-10),'rest')}break}}}
 /* guests needing comfort: friendly cats only */
 if(R&&phase==='service'&&R.closing==null){R.catCheck=(R.catCheck||0)+dt;if(R.catCheck>3){R.catCheck=0;const needy=R.groups.filter(g=>['order','wait','check'].includes(g.state)&&g.pat<.5&&!CATS.some(c=>c.guest===g)).sort((a,b)=>a.pat-b.pat)[0];
  if(needy){const pref={mikan:3,ban:2,snow:.3,mei:0,tora:familiar(needy)?1.5:0};const pool=CATS.filter(c=>pref[c.def.id]>0&&c.perch<0&&!c.hidden&&!c.sofa&&['rest','walk','daze','eat','toy'].includes(c.st)&&!c.guest);const c=wpick(pool,o=>pref[o.def.id]);if(c&&Math.random()<.7){releaseSpots(c);const t=R.tables[needy.table];c.guest=needy;catWalk(c,clamp(t.x+rand(-12,12),96,316),Math.min(FB-8,t.y+20),'visit')}}}
  /* guests notice cats */
  /* guests notice the cats. What draws the eye: 寶寶 sitting pretty (tree, sofa back, window bed), 包包 asleep in a
     silly pose, 柔柔 doing something odd, two cats chasing each other. 樾樾 keeps away from strangers, so he is
     rarely close enough. A look is common; a phone photo happens to some groups, once per visit. Dylan never
     photographs them - he sees these cats every day. */
  R.noticeT=(R.noticeT??rand(4,8))-dt;if(R.noticeT<=0){R.noticeT=rand(4,8);const cands=[];const busyCats=CATS.filter(c=>!c.hidden&&['race','chase','dash','play','wary'].includes(c.st));
   for(const g of R.groups){if(g.table==null||!['reading','wait','eat'].includes(g.state)||g.reg==='dylan'||(g.lookT&&g.lookT>R.t))continue;const t=R.tables[g.table];
    for(const c of CATS){if(c.hidden)continue;const d=Math.hypot(t.x-c.x,t.y-c.y);const lim=busyCats.includes(c)?170:120;if(d>=lim)continue;const id=c.def.id;let w=1;
     if(id==='mei'){w=3;if(c.perch>=0||(c.sofa&&c.sofa.kind==='back')||c.st==='bed')w=4.5}
     else if(id==='snow'){w=c.st==='sleep'&&c.pose==='belly'?2.6:c.st==='sleep'?1.2:.8}
     else if(id==='mikan'){w=['stare','daze','hide','hide2','wary','glare'].includes(c.st)||c.pose==='glare'?2.4:1.2}
     else if(id==='tora'){w=.5}
     if(busyCats.includes(c))w+=2;if(g.type==='family')w*=1.8;cands.push({g,c,w:w*(1-d/(lim+30))})}}
   const pk=wpick(cands,o=>o.w);if(pk){const star=pk.c.def.id==='mei'&&(pk.c.perch>=0||pk.c.st==='rest'||pk.c.sofa);const set=star?cands.filter(o=>o.c===pk.c).slice(0,3):busyCats.includes(pk.c)?cands.filter(o=>busyCats.includes(o.c)).slice(0,3):[pk];
    for(const o of set){const g=o.g,id=o.c.def.id;const dur=rand(2.2,3.8);g.lookT=R.t+dur;g.lookCat=o.c;if(g.wantShot==null)g.wantShot=Math.random()<(g.type==='blogger'?.95:.32);const pPhoto=(g.shot||!g.wantShot)?0:(id==='mei'?.8:id==='snow'?.6:.4);
     if(Math.random()<pPhoto){g.shot=true;g.photo=true;g.photoT0=R.t+.5+rand(.7,1.2);g.lookT=Math.max(g.lookT,g.photoT0+.9)}else g.photo=false;if(g.type==='family'&&g.table!=null&&!o.c.hidden&&Math.random()<.5){const t=R.tables[g.table];memo('kidcat',o.c.x,o.c.y-4,{a:catName(o.c.def),subj:[{x:t.x,y:t.y-6}]})}}}}
  /* Jill notices someone photographing a cat: a glance over, if she is free */
  for(const g of R.groups){if(g.photo&&g.photoT0&&R.t>=g.photoT0&&!g.shotSeen){g.shotSeen=true;if(g.lookCat&&!g.lookCat.hidden&&g.table!=null){const t=R.tables[g.table];memo('photo',g.lookCat.x,g.lookCat.y-4,{a:catName(g.lookCat.def),subj:[{x:t.x,y:t.y-6}]})}else if(g.dishShot&&g.table!=null){const t=R.tables[g.table];memo('dishphoto',t.x,t.y-8,{d:g.dishShot,room:t.room})}const J=R.jill;if(!J.cur&&!J.q.length&&!J.rest&&!J.pet&&Math.random()<.65&&g.table!=null){const t=R.tables[g.table];J.lookAt={x:t.x,y:t.y,t:rand(1,1.8)};J.nod=.7}}}}
 /* 寶寶 walks where 柔柔 might be hiding; nothing else to do */
 memChecks()}
function freeCatNear(x,y){return CATS.filter(c=>c.perch<0&&!c.hidden&&!c.sofa&&!['jump','visit','bed','chase','race','dash','hide2'].includes(c.st)).sort((a,b)=>Math.hypot(a.x-x,a.y-y)-Math.hypot(b.x-x,b.y-y))[0]}
function hitSpot(p){if(p.x>=276&&p.x<=344&&p.y>=8&&p.y<=88)return'bags';const d=(s,r)=>Math.hypot(p.x-s.x,p.y-(s.y-8))<r;if(d(SPOT.bowl,16))return'bowl';if(Math.hypot(p.x-(SPOT.toy.x+Math.sin(performance.now()/1000*2.2)*3),p.y-SPOT.toy.y)<11)return'toy';if(d(SPOT.cave,20))return'cave';if(d(SPOT.bed,20))return'bed';if(d(SPOT.scr,18))return'scr';if(Math.hypot(p.x-SPOT.scr2.x,p.y-(SPOT.scr2.y-20))<16)return'scr2';return null}
function tapSpot(k){audioInit();if(k==='bags'){BAG_T=performance.now()/1000;sfx.ding();toast(pick(['Jill 的包包收藏櫃，每一個都是自己努力賺來的','今天打烊後要背哪一個回家呢？','櫃子的燈一打，每個包都閃閃發亮']));return}
 if(k==='bowl'){sfx.kibble();for(const c of CATS.filter(c=>c.perch<0&&!c.hidden&&['rest','walk','daze','stare'].includes(c.st)&&c.def.id!=='snow').slice(0,2))catGo(c,'eat');return}
 if(k==='cave'){const c=OCC.cave;if(c&&c.st==='hide'){c.t=0;c.happy=1.6;sfx.meow();c.hearts.push({x:0,y:-26,t:0})}else if(!c){const f=freeCatNear(SPOT.cave.x,SPOT.cave.y);if(f)catGo(f,'cave')}return}
 if(k==='bed'){if(OCC.bed.length){for(const c of OCC.bed.slice()){if(c.def.id==='snow'){c.hearts.push({x:0,y:-20,t:0});continue}c.t=0;c.happy=1.2}sfx.meow()}else{const f=freeCatNear(SPOT.bed.x,SPOT.bed.y);if(f)catGo(f,'bed')}return}
 if(k==='scr2'){if(!OCC.scr2){const f=freeCatNear(SPOT.scr2.x,SPOT.scr2.y);if(f)catGo(f,'scr2')}return}
 if(k==='scr'){if(!OCC.scr){const f=freeCatNear(SPOT.scr.x,SPOT.scr.y);if(f)catGo(f,'scr')}return}
 if(k==='toy'){TOY.amp=4;sfx.catPlay();if(!OCC.toy){const f=freeCatNear(SPOT.toy.x,350+FY);if(f)catGo(f,'toy')}}}

/* furniture */
function drawScratcher(c,now){const {x,y}=SPOT.scr;c.fillStyle='rgba(0,0,0,.22)';el(c,x+1,y+2,22,5);c.fillStyle='#A9814F';rr(c,x-20,y-8,40,9,2);c.fill();c.fillStyle='#D9B27A';c.beginPath();c.moveTo(x-20,y-8);c.quadraticCurveTo(x,y-18,x+20,y-8);c.lineTo(x+20,y-6);c.quadraticCurveTo(x,y-15,x-20,y-6);c.closePath();c.fill();c.strokeStyle='rgba(120,85,45,.55)';c.lineWidth=.7;for(let i=-18;i<=18;i+=2.4){const yy=y-8-(1-(i/20)**2)*9;c.beginPath();c.moveTo(x+i,yy+1);c.lineTo(x+i,y+.5);c.stroke()}c.fillStyle='#6FA84E';for(let i=0;i<5;i++)circ(c,x-8+i*4,y-11-Math.sin(i)*1.5,.8);c.fillStyle='rgba(255,255,255,.18)';c.fillRect(x-20,y-8,40,1)}
function drawCave(c,now){const {x,y}=SPOT.cave;const occ=OCC.cave&&OCC.cave.st==='hide'?OCC.cave:null;c.fillStyle='rgba(0,0,0,.25)';el(c,x+2,y+2,22,6);let g=c.createRadialGradient(x-6,y-18,2,x,y-10,24);g.addColorStop(0,'#E4D8C8');g.addColorStop(1,'#B9A690');c.fillStyle=g;c.beginPath();c.moveTo(x-21,y);c.bezierCurveTo(x-23,y-30,x+23,y-30,x+21,y);c.closePath();c.fill();c.fillStyle='rgba(120,100,80,.25)';for(let i=0;i<40;i++){const a=i*2.4,r=(i%7)*2.6;circ(c,x+Math.cos(a)*r,y-10+Math.sin(a)*r*.7,.7)}c.strokeStyle='rgba(255,255,255,.25)';c.lineWidth=1;c.beginPath();c.moveTo(x-18,y-10);c.quadraticCurveTo(x-10,y-22,x+4,y-23);c.stroke();
 const mx=x-8,my=y-7;c.fillStyle='#2A211C';el(c,mx,my,8,7);c.fillStyle='#B9A690';c.fillRect(mx-9,my+5,18,3);c.strokeStyle='#A08C76';c.lineWidth=1.4;c.beginPath();c.ellipse(mx,my,8,7,0,Math.PI,0);c.stroke();
 if(occ){const peek=Math.sin(now*.9+occ.ph)>.7;if(peek){c.save();c.beginPath();c.ellipse(mx,my,8,7.2,0,0,7);c.rect(mx-12,my,24,6);c.clip();catHead(c,occ.def,mx,my+1.5+Math.sin(now*3)*.4,occ.def.fluffy?5.6:5,{},false);c.restore()}else{const bl=Math.sin(now*1.7+occ.ph)>.93;c.fillStyle=occ.def.eye;if(!bl){el(c,mx-2.4,my,1.3,1.1);el(c,mx+2.4,my,1.3,1.1);c.fillStyle='#111';el(c,mx-2.4,my,.4,1);el(c,mx+2.4,my,.4,1)}else{c.fillRect(mx-3.6,my,2.4,.5);c.fillRect(mx+1.2,my,2.4,.5)}}}}
function drawBed(c,now){const {x,y}=SPOT.bed;c.fillStyle='rgba(0,0,0,.24)';el(c,x+1,y+2,24,6);c.fillStyle='#C9A68A';el(c,x,y-2,23,8);fluff(c,'#E9CDB6',x,y-4,21,7,22,2.6);c.fillStyle='#F6E9DC';el(c,x,y-4,16,5);c.fillStyle='rgba(180,140,110,.25)';el(c,x,y-3.4,12,3.4);c.fillStyle='rgba(255,255,255,.35)';el(c,x-8,y-9,6,1.4)}
function drawBowls(c,now){const {x,y}=SPOT.bowl;const bowl=(bx,col,fill,kib)=>{c.fillStyle='rgba(0,0,0,.2)';el(c,bx+1,y+1.5,8.5,2.6);c.fillStyle='#E4E8EA';c.beginPath();c.moveTo(bx-8,y-4);c.quadraticCurveTo(bx-7,y+1,bx,y+1);c.quadraticCurveTo(bx+7,y+1,bx+8,y-4);c.fill();c.fillStyle='#F6F8F9';el(c,bx,y-4,8,2.6);if(fill>0){c.fillStyle=col;el(c,bx,y-4,6.8*Math.max(.35,fill),2*Math.max(.35,fill));if(kib){c.fillStyle='#7A4A26';for(let i=0;i<Math.round(fill*9);i++)circ(c,bx-4+(i*3.1)%8,y-4.6+(i%3)*.7,.8)}}};bowl(x-6,'#B07A46',FOOD,1);bowl(x+9,'rgba(140,200,235,.9)',1,0);c.fillStyle='#C99A45';c.font=`800 4.5px ${FONT}`;c.textAlign='center';c.fillText('CAT',x-6,y+4.4)}
function catShadow(c,w){c.fillStyle='rgba(30,20,10,.13)';el(c,0,.8,w+3,3.2);c.fillStyle='rgba(30,20,10,.2)';el(c,0,.5,w*.8,2.2)}
function catBelly(c,C,ph,o){const W=C.white||{};catShadow(c,15);
 const fk=o.flick>0?Math.sin(o.flick*9)*3*Math.min(1,o.flick):0;c.strokeStyle=shade(C.base,-.05);c.lineWidth=C.fluffy?5:3.2;c.lineCap='round';c.beginPath();c.moveTo(11,-3);c.quadraticCurveTo(18,-2+fk*.5,20+Math.sin(ph*2)*1.5+Math.abs(fk)*.3,-6-fk);c.stroke();
 const legs=[[-5,-.5],[-1,.3],[6,-.2],[9,.6]];const wig=t=>Math.sin(ph*3+t)*1.2;
 for(const [lx,t] of legs){c.save();c.translate(lx,-8);c.rotate(-.35+t*.5+wig(t)*.05);c.fillStyle=C.base;rr(c,-1.4,-8,2.8,8.5,1.3);c.fill();c.fillStyle=W.paws?'#FFFFFF':C.belly;el(c,0,-8,1.9,1.3);c.restore()}
 c.fillStyle=C.base;c.save();c.beginPath();c.ellipse(1,-5,13,5.6,0,0,7);c.fill();c.clip();if(C.str){c.strokeStyle=C.str;c.globalAlpha=.7;c.lineWidth=1.2;for(let i=-3;i<=3;i++){c.beginPath();c.moveTo(i*3.4,1);c.lineTo(i*3.4+1,-3);c.stroke()}c.globalAlpha=1}c.fillStyle=W.belly||C.fluffy?'#FFFFFF':C.belly;el(c,1,-8.4,10,3.6);c.fillStyle='rgba(240,170,170,.35)';el(c,3,-8.4,4,1.8);c.restore();if(C.fluffy)fluff(c,C.base,1,-5,12,5,14,1.8);
 c.save();c.translate(-13,-6);c.rotate(-1.25);catHead(c,C,0,0,C.fluffy?6.2:5.6,{sleep:!o.wake,twitch:o.twitch},false);c.restore()}

function hitRegular(p){if(!R)return null;for(const g of R.groups){if(!g.reg||g.table==null||!['reading','order','wait','eat','check'].includes(g.state))continue;const t=R.tables[g.table];if((t.room||'main')!==room)continue;const sp=seatPos(t)[0];const x=t.x+sp.dx,y=t.y+sp.dy;if(Math.abs(p.x-x)<14&&p.y<y+6&&p.y>y-46)return g}return null}
/* a small card, not a dialogue: name, how well the place knows them, what has been noticed */
let regCardT=0;
function showRegCard(g){const el=$('#regcard');if(!el)return;const v=S.regulars[g.reg]||0;const isD=g.reg==='dylan';const tier=regTier(v);const rv=isD&&S.dylan.stage>=3;
 let who=isD?(rv?DYLAN.who2:DYLAN.who):REG_BY[g.reg].who;const notes=[];if(isD&&!rv){if(S.dylan.stage>=1)notes.push('打烊後偶爾會留下來。');if(S.dylan.clues.knows)notes.push('好像知道東西放在哪。');if(S.dylan.seen&&S.dylan.seen.wang)notes.push('王太太也注意到他了。');if((S.dylan.clues.pet||0)>=1)notes.push('貓對他好像不太怕生。');if((S.dylan.clues.tidy||0)>=1)notes.push('走之前會自己收盤子。');if((S.dylan.clues.pause||0)>=2)notes.push('Jill 經過他那桌的時候，會停一下。')}
 else if(!isD){const cf=(S.catFam&&S.catFam[g.reg])||0;if(cf>=4)notes.push('樾樾不躲他了。');const m=regMem(g.reg);if(m.facts.length)notes.push(m.facts[0].txt);else{const nt=notesFor(g.reg,1);if(nt.length)notes.push(`「${nt[0].txt}」`)}}
 el.innerHTML=`<img alt="" src="${isD?portraitURL(DYLAN.looks,'regdylan'):portraitURL(REG_BY[g.reg].looks,'reg'+g.reg)}"><div><b>${isD?'Dylan':g.name}</b> <span class="tier t${Math.floor(tier)}">${rv?'Jill 的先生':TIER_N[tier]}</span><p>${v?`來店 ${v} 次・`:''}${who}${notes.length?'<br>'+notes.join(' '):''}</p></div>`;
 el.hidden=false;sfx.tap();clearTimeout(regCardT);regCardT=setTimeout(()=>{el.hidden=true},4200)}
function hitCat(p){if(!CATS)return null;let best=null,bd=0;for(const c of CATS){if(c.hidden)continue;const lying=['sleep','bed','loaf','curl','belly'].includes(c.pose)||c.st==='sleep';const r=(c.def.fluffy?27:22)*(lying?1:1);const d=Math.hypot(p.x-c.x,(p.y-(c.y-(lying?8:12)))*(lying?1.4:1));if(d<r&&(best===null||d<bd)){bd=d;best=c}}return best}
/* 包包 knows you are there; he just is not getting up. Eyes open a moment, an ear and the tail flick, a purr. */
function snowNudge(c){c.wakeT=1.5;c.flickT=1.3;tone(190,0,.35,'sine',.045,140);setTimeout(()=>{if(AU.ctx)tone(205,0,.3,'sine',.04,150)},220)}
function tapCat(c){audioInit();const id=c.def.id;
 if(id==='mei'&&Math.random()<.35&&!['sleep','bed'].includes(c.st)){c.face=-c.face;tone(420,0,.12,'sine',.05,300);return}
 if(id==='snow'&&(c.st==='sleep'||c.st==='bed')){c.hearts.push({x:0,y:-20,t:0});snowNudge(c);return}
 sfx.meow();if(c.st==='sleep'){c.st='daze';c.pose='daze';c.t=2.5}if(['scr','toy','eat','stare','daze','wary','rest'].includes(c.st)&&!c.sofa)releaseSpots(c);c.happy=1.8;c.hearts.push({x:0,y:-28,t:0},{x:5,y:-24,t:-.2});
 if(!['jump','visit','side','race','dash','chase','hide2','bed','hide','walk'].includes(c.st)&&c.perch<0&&!c.sofa){c.st='pet';c.pose='happy';c.moving=false}else if(c.perch>=0||c.st==='side'||c.sofa){c.pose='happy';c.t=Math.max(c.t,2.5)}
 if(R&&phase==='service'&&c.cd<=0){c.cd=12;for(const g of R.groups){if(g.table==null||!['reading','order','wait','check'].includes(g.state))continue;const t=R.tables[g.table];if(Math.hypot(t.x-c.x,t.y-c.y)<90&&catCheer(g,.08)>0)addFloat(t.x,t.y-54,'心情 UP','#F29AAE',0)}}}
/* ---- cat drawing ---- */
function catStripesSide(c,C,bw,bh){if(!C.str)return;c.strokeStyle=C.str;c.lineCap='round';if(C.b==='amshort'){c.globalAlpha=.9;c.lineWidth=1.7;for(let i=-3;i<=3;i++){c.beginPath();c.moveTo(i*3.3,-10-bh-1);c.quadraticCurveTo(i*3.3+2,-11,i*3.3-.5,-10+bh*.2);c.stroke()}c.lineWidth=1.3;c.beginPath();c.arc(-1,-9.5,3,0,7);c.stroke()}else{const dense=!!C.strDense;c.globalAlpha=dense?.9:.8;c.lineWidth=dense?1.5:1.3;const n=dense?4:3,sp=dense?2.9:3.4,len=dense?bh*.55:bh*.1;for(let i=-n;i<=n;i++){c.beginPath();c.moveTo(i*sp,-10-bh-1);c.quadraticCurveTo(i*sp+1.8,-10.5,i*sp,-10+len);c.stroke()}}c.globalAlpha=1}
function fluff(c,col,cx,cy,rx,ry,n,r){c.fillStyle=col;c.beginPath();for(let i=0;i<n;i++){const a=i/n*6.283;const x=cx+Math.cos(a)*rx,y=cy+Math.sin(a)*ry;c.moveTo(x+r,y);c.arc(x,y,r,0,7)}c.fill()}
const legCol=(C,far)=>far?shade(C.base,-.14):C.base;
function catHead(c,C,hx,hy,r,o,side){const fl=C.fluffy,W=C.white||{};
 const ear=(ex,dir)=>{if(C.fold){c.fillStyle=C.base;c.beginPath();c.moveTo(ex-2.8,hy-r*.55);c.quadraticCurveTo(ex+dir*.4,hy-r-2.2,ex+2.8,hy-r*.5);c.quadraticCurveTo(ex+dir*1.2,hy-r*.35,ex-2.8,hy-r*.55);c.fill();c.fillStyle=shade(C.base,-.12);c.beginPath();c.moveTo(ex-1.6,hy-r*.62);c.quadraticCurveTo(ex+dir*.4,hy-r-.8,ex+1.6,hy-r*.58);c.fill();return}
  const tw=(o.twitch&&dir>0)?o.twitch:0;c.fillStyle=C.base;c.beginPath();c.moveTo(ex-2.7,hy-r*.55);c.lineTo(ex+dir*.6+tw,hy-r-(fl?2.8:4.4)+Math.abs(tw)*.5);c.lineTo(ex+2.7,hy-r*.45);c.closePath();c.fill();c.fillStyle=C.earIn;c.beginPath();c.moveTo(ex-1.3,hy-r*.6);c.lineTo(ex+dir*.5+tw,hy-r-(fl?1.4:2.8)+Math.abs(tw)*.5);c.lineTo(ex+1.4,hy-r*.55);c.closePath();c.fill()};
 if(side){ear(hx-1.5,1);ear(hx+2.5,1)}else{ear(hx-r*.56,-1);ear(hx+r*.56,1)}
 let g=c.createRadialGradient(hx-2,hy-2,1,hx,hy,r+1);g.addColorStop(0,shade(C.base,.12));g.addColorStop(1,shade(C.base,-.08));c.fillStyle=g;circ(c,hx,hy,r);
 if(fl){fluff(c,C.base,hx,hy+1,r*.95,r*.8,11,1.9);if(C.shadeC){c.fillStyle=C.shadeC;el(c,hx,hy-r*.55,r*.5,r*.25)}}
 if(C.str){c.save();c.beginPath();c.arc(hx,hy,r,0,7);c.clip();c.strokeStyle=C.str;c.globalAlpha=.85;c.lineWidth=C.b==='amshort'?1.2:1;c.lineCap='round';if(!side){for(const dx of[-2,0,2]){c.beginPath();c.moveTo(hx+dx,hy-r+.5);c.lineTo(hx+dx*.6,hy-r+4)}c.stroke();c.beginPath();c.moveTo(hx-r,hy-.5);c.lineTo(hx-r+3.2,hy+.4);c.moveTo(hx+r,hy-.5);c.lineTo(hx+r-3.2,hy+.4);c.moveTo(hx-r+.5,hy+2);c.lineTo(hx-r+2.8,hy+2.4);c.moveTo(hx+r-.5,hy+2);c.lineTo(hx+r-2.8,hy+2.4);c.stroke()}else{c.beginPath();c.moveTo(hx-1,hy-r+.5);c.lineTo(hx-.4,hy-r+4);c.moveTo(hx+1.6,hy-r+.8);c.lineTo(hx+1.6,hy-r+4);c.moveTo(hx-r+.5,hy);c.lineTo(hx-r+3,hy+.8);c.stroke()}c.globalAlpha=1;c.restore()}
 if(W.muzzle){c.fillStyle='#FFFFFF';el(c,hx+(side?r*.55:0),hy+r*.42,side?r*.45:r*.52,r*.36)}
 if(W.blaze&&!side){c.fillStyle='#FFFFFF';c.beginPath();c.moveTo(hx-2.6,hy+2);c.lineTo(hx-.5,hy-r*.8);c.lineTo(hx+.5,hy-r*.8);c.lineTo(hx+2.6,hy+2);c.closePath();c.fill()}
 if(fl&&!side){c.fillStyle=W.chest?'#FFFFFF':C.base;fluff(c,W.chest?'#FFFFFF':shade(C.base,.06),hx,hy+r*.8,r*.7,r*.2,7,1.8)}
 const big=C.eyeBig||fl;const ex=side?[hx+r*.45]:[hx-r*.38,hx+r*.38];const ey=hy+(fl?-.1:-.6);
 if(o.yawn&&!side){c.fillStyle='#B85A66';el(c,hx,hy+r*.5,1.5,2.1);c.fillStyle='#F2A0A8';el(c,hx,hy+r*.62,.9,.9)}
 for(const x of ex){if(o.happy||o.sleep||o.yawn){c.strokeStyle='#3A2A22';c.lineWidth=.9;c.beginPath();if(o.happy)c.arc(x,ey+.8,1.4,Math.PI*1.1,Math.PI*1.9);else c.arc(x,ey-.4,1.4,.2,Math.PI-.2);c.stroke()}
  else if(o.blink){c.fillStyle='#3A2A22';c.fillRect(x-1.5,ey,3,.7)}
  else{const rx=big?2.05:1.55,ry=big?2.1:1.75;c.fillStyle=C.eye;el(c,x,ey,rx,ry);c.fillStyle='#15110E';if(C.roundPupil)circ(c,x,ey+.1,1.35);else el(c,x,ey,big?1.1:.55,big?1.7:1.45);if(C.eyeLine){c.strokeStyle='#2A2220';c.lineWidth=.7;c.beginPath();c.ellipse(x,ey,rx+.2,ry+.2,0,0,7);c.stroke()}c.fillStyle='#fff';circ(c,x-.6,ey-.7,.5);circ(c,x+.5,ey+.6,.22)}}
 const nx=side?hx+r*.88:hx,ny=hy+(fl?1.5:2);if(C.shadeC&&!side){c.fillStyle='rgba(150,145,140,.35)';el(c,nx,ny-1.2,1.8,1)}c.fillStyle=C.nose;c.beginPath();c.moveTo(nx-1.1,ny-.5);c.lineTo(nx+1.1,ny-.5);c.lineTo(nx,ny+.8);c.closePath();c.fill();if(C.eyeLine){c.strokeStyle='rgba(60,40,40,.6)';c.lineWidth=.35;c.stroke()}
 c.strokeStyle='rgba(60,40,30,.55)';c.lineWidth=.6;if(!side){c.beginPath();c.moveTo(nx,ny+.8);c.quadraticCurveTo(nx-.8,ny+1.9,nx-1.6,ny+1.3);c.moveTo(nx,ny+.8);c.quadraticCurveTo(nx+.8,ny+1.9,nx+1.6,ny+1.3);c.stroke()}
 c.strokeStyle='rgba(255,255,255,.75)';c.lineWidth=.35;c.beginPath();for(const s of side?[1]:[-1,1]){c.moveTo(nx+s*1.6,ny+.8);c.lineTo(nx+s*7.5,ny-.2);c.moveTo(nx+s*1.6,ny+1.2);c.lineTo(nx+s*7.5,ny+2.1)}c.stroke()}
function catSide(c,C,ph,moving,o){const fl=C.fluffy,W=C.white||{};const bw=fl?12.5:11.5,bh=fl?7.5:6;
 catShadow(c,13);if(!moving){c.save();c.translate(0,Math.sin(ph*1.7)*.3)}
 const sway=Math.sin(ph*3)*.35;const tail=()=>{c.beginPath();c.moveTo(-bw+2,-10);c.quadraticCurveTo(-bw-8,-12+(o.tailUp?-8:0),-bw-5+sway*6,o.tailUp?-27:-19)};c.strokeStyle=shade(C.base,-.04);c.lineCap='round';c.lineWidth=fl?5.4:3.2;tail();c.stroke();if(C.str){c.strokeStyle=C.str;c.lineWidth=3.4;c.globalAlpha=.75;c.setLineDash([1.6,2.4]);tail();c.stroke();c.setLineDash([]);c.globalAlpha=1}
 const leg=(x,phs,far)=>{let a=moving?Math.sin(ph*13+phs)*2.4:0,lift=moving?Math.max(0,Math.cos(ph*13+phs))*1.4:0;if(o.leap){a=x>0?3:-3;lift=2}const lx=x-1.5+a*.5,ly=-8.5-lift;c.fillStyle=legCol(C,far);rr(c,lx,ly,3,8.5,1.3);c.fill();if(W.paws){c.fillStyle=far?'#E8E6E2':'#FFFFFF';rr(c,lx,ly+4.2,3,4.3,1.3);c.fill()}else if(C.str&&C.b==='amshort'){c.fillStyle=C.str;c.globalAlpha=.7;c.fillRect(lx,ly+2,3,1);c.fillRect(lx,ly+4.5,3,1);c.globalAlpha=1}c.fillStyle=W.paws?(far?'#E8E6E2':'#FFFFFF'):(far?shade(C.belly,-.1):C.belly);el(c,x+a*.5,-.4-lift,1.9,1)};
 leg(-7,0,1);leg(6,Math.PI,1);
 let g=c.createLinearGradient(0,-10-bh,0,-10+bh);g.addColorStop(0,shade(C.base,.1));g.addColorStop(.7,C.base);g.addColorStop(1,shade(C.base,-.05));c.fillStyle=g;c.save();c.beginPath();c.ellipse(0,-10,bw,bh,0,0,7);c.fill();c.clip();catStripesSide(c,C,bw,bh);
 if(C.tint){c.fillStyle=C.tint;c.globalAlpha=.35;el(c,1,-8,5,3.4);c.globalAlpha=1}
 if(W.belly){const amt=C.whiteAmt!=null?C.whiteAmt:.5;/* how much of the flank is white, from the belly up */let wg=c.createLinearGradient(0,-10-bh,0,-10+bh);wg.addColorStop(Math.max(0,1-amt-.14),'rgba(255,255,255,0)');wg.addColorStop(Math.min(1,1-amt+.02),'#FFFFFF');c.fillStyle=wg;c.fillRect(-bw,-10-bh,bw*2,bh*2+1)}
 if(C.shadeC){c.fillStyle=C.shadeC;c.globalAlpha=.6;el(c,-2,-10-bh+1.5,bw*.7,2);c.globalAlpha=1}c.restore();
 if(fl)fluff(c,C.base,0,-10,bw*.95,bh*.9,16,2.2);
 if(W.chest||W.belly||fl){c.fillStyle=W.chest||W.belly?'#FFFFFF':C.belly;const cs=C.chestBig?1.45:1;el(c,bw-4,-8-(cs-1)*2,3.8*cs,4.4*cs);if(fl)fluff(c,W.chest?'#FFFFFF':C.belly,bw-4,-7,3,3,6,1.5)}
 if(o.paw){const a=Math.sin(ph*14)*2.5;c.fillStyle=C.base;rr(c,bw-6,-18+a,3,9,1.3);c.fill();rr(c,bw-3,-17-a,3,9,1.3);c.fill();c.fillStyle=W.paws?'#FFFFFF':C.belly;el(c,bw-4.5,-18+a,1.9,1.2);el(c,bw-1.5,-17-a,1.9,1.2);leg(-5,Math.PI,0)}else{leg(-5,Math.PI,0);leg(o.stretch?11:8,0,0)}
 const hd=o.headDown?Math.sin(ph*8)*.5:0;catHead(c,C,o.headDown?bw+2.5:bw+1,o.headDown?-9+hd:-15.5,fl?6.8:C.eyeBig?6.3:5.9,o,true);if(!moving)c.restore()}
function catSit(c,C,ph,o){const fl=C.fluffy,W=C.white||{};
 catShadow(c,10);c.save();c.translate(0,Math.sin(ph*1.7)*.3);
 const sway=Math.sin(ph*2)*1.4;const tail=()=>{c.beginPath();c.moveTo(5,-1.5);c.quadraticCurveTo(-2,2.5,-10,-1+sway*.3);c.lineTo(-11.5,-3.5+sway)};c.strokeStyle=shade(C.base,-.05);c.lineCap='round';c.lineWidth=fl?5.2:3.2;tail();c.stroke();if(C.str){c.strokeStyle=C.str;c.globalAlpha=.7;c.lineWidth=3.4;c.setLineDash([1.6,2.4]);tail();c.stroke();c.setLineDash([]);c.globalAlpha=1}
 const bw=fl?9.4:7.8,bh=fl?9:8.4;let g=c.createRadialGradient(-2,-12,1,0,-8,bh+2);g.addColorStop(0,shade(C.base,.12));g.addColorStop(1,shade(C.base,-.1));c.fillStyle=g;c.save();c.beginPath();c.ellipse(0,-8,bw,bh,0,0,7);c.fill();c.clip();
 if(C.str){c.strokeStyle=C.str;c.lineCap='round';if(C.b==='amshort'){c.globalAlpha=.9;c.lineWidth=1.6;for(let k=0;k<5;k++){const yy=-15+k*3.2;c.beginPath();c.moveTo(-bw,yy);c.quadraticCurveTo(-bw+3.5,yy+1.6,-bw+5.5,yy-.3);c.moveTo(bw,yy);c.quadraticCurveTo(bw-3.5,yy+1.6,bw-5.5,yy-.3);c.stroke()}c.lineWidth=1.1;for(let k=0;k<3;k++){c.beginPath();c.moveTo(-2.5,-14+k*3);c.quadraticCurveTo(0,-13+k*3,2.5,-14+k*3);c.stroke()}}else{c.globalAlpha=.8;c.lineWidth=1.3;for(let k=0;k<4;k++){const yy=-14+k*3.4;c.beginPath();c.moveTo(-bw,yy);c.quadraticCurveTo(-bw+3,yy+1.4,-bw+4.2,yy-.4);c.moveTo(bw,yy);c.quadraticCurveTo(bw-3,yy+1.4,bw-4.2,yy-.4);c.stroke()}}c.globalAlpha=1}
 if(C.tint){c.fillStyle=C.tint;c.globalAlpha=.3;el(c,-5,-8,3,4);c.globalAlpha=1}
 if(C.shadeC){c.fillStyle=C.shadeC;c.globalAlpha=.55;el(c,-bw+1,-8,2.5,6);el(c,bw-1,-8,2.5,6);c.globalAlpha=1}c.restore();
 if(fl)fluff(c,C.base,0,-8,bw*.95,bh*.9,16,2.2);
 const chestW=W.chest||W.belly;c.fillStyle=chestW?'#FFFFFF':C.belly;el(c,0,-6.5,chestW?(fl?6:3.8):(fl?5.2:4.2),chestW?(fl?7:5.8):(fl?6.2:5.4));if(fl)fluff(c,chestW?'#FFFFFF':C.belly,0,-10,4.4,3.2,8,1.7);
 const pc=W.paws?'#FFFFFF':C.str&&C.b==='amshort'?C.base:C.belly;const pb=o.groom?Math.sin(ph*9)*1.2:0;const kn=o.knead?Math.sin(ph*7)*1.6:0;c.fillStyle=pc;el(c,-3,-.9-Math.max(0,kn),2.5,1.6);if(o.knead){el(c,3,-.9-Math.max(0,-kn),2.5,1.6)}else if(o.groom){rr(c,.8,-17+pb,3,7,1.5);c.fill();el(c,2.3,-17.5+pb,2,1.6)}else el(c,3,-.9,2.5,1.6);
 if(C.b==='amshort'){c.strokeStyle=C.str;c.globalAlpha=.6;c.lineWidth=.6;c.beginPath();c.moveTo(-4.4,-2.2);c.lineTo(-1.8,-2.2);c.moveTo(1.8,-2.2);c.lineTo(4.4,-2.2);c.stroke();c.globalAlpha=1}
 catHead(c,C,0,-18.5,fl?7.5:C.eyeBig?7:6.5,o,false);c.restore()}
function catLoaf(c,C,ph,o){const fl=C.fluffy,W=C.white||{};catShadow(c,12);
 const bw=fl?11.5:10.5,bh=fl?6.6:5.8;let g=c.createLinearGradient(0,-5-bh,0,0);g.addColorStop(0,shade(C.base,.1));g.addColorStop(1,shade(C.base,-.1));c.fillStyle=g;c.save();c.beginPath();c.ellipse(0,-5.5,bw,bh,0,0,7);c.fill();c.clip();
 if(C.str){c.strokeStyle=C.str;c.lineWidth=C.b==='amshort'?1.6:1.3;c.globalAlpha=.85;if(C.b==='amshort'){c.beginPath();c.arc(-3,-6,2.8,0,7);c.stroke()}for(let i=-3;i<=3;i++){c.beginPath();c.moveTo(i*3.2,-5.5-bh);c.quadraticCurveTo(i*3.2+1.5,-6,i*3.2,-3.5);c.stroke()}c.globalAlpha=1}
 if(C.tint){c.fillStyle=C.tint;c.globalAlpha=.3;el(c,3,-5,4,3);c.globalAlpha=1}if(W.belly){c.fillStyle='#FFFFFF';el(c,0,-.5,bw,2.6)}if(C.shadeC){c.fillStyle=C.shadeC;c.globalAlpha=.55;el(c,0,-5.5-bh+1.5,bw*.7,2);c.globalAlpha=1}c.restore();if(fl)fluff(c,C.base,0,-5.5,bw*.95,bh*.85,16,2);
 const fk=o.flick>0?Math.sin(o.flick*9)*3.2*Math.min(1,o.flick):0;const tail=()=>{c.beginPath();c.moveTo(-bw+2,-1.5);c.quadraticCurveTo(-2,2+fk*.6,7+Math.abs(fk)*.4,-.5-fk)};c.strokeStyle=shade(C.base,-.05);c.lineWidth=fl?4.8:3;c.lineCap='round';tail();c.stroke();if(C.str){c.strokeStyle=C.str;c.globalAlpha=.7;c.lineWidth=3.2;c.setLineDash([1.6,2.4]);tail();c.stroke();c.setLineDash([]);c.globalAlpha=1}
 if(W.paws||fl&&W.chest){c.fillStyle='#FFFFFF';el(c,-5,-.8,2.3,1.3);el(c,-1,-.8,2.3,1.3)}
 const breathe=Math.sin(ph*1.8)*.3;catHead(c,C,-bw*.35+2,-9.5+breathe,fl?6.5:C.eyeBig?6.1:5.6,{sleep:o.sleep&&!o.wake,happy:o.happy&&!o.wake,blink:o.blink,twitch:o.twitch},false);
 if(o.sleep&&!o.wake){const t=(ph*.6)%1;c.globalAlpha=1-t;c.fillStyle='#FFF3DA';c.font=`800 ${5+t*3}px ${FONT}`;c.textAlign='center';c.fillText('z',6+t*6,-18-t*10);c.globalAlpha=1}}
function drawCat(c,cat,now){const C=cat.def;c.save();c.translate(cat.x,cat.y);c.scale(CSC,CSC);const flip=cat.face<0;const blink=Math.sin(now*1.1+cat.ph*.1+C.id.length)>.975;const happy=cat.happy>0||cat.pose==='happy'||cat.st==='visit'&&Math.sin(now*1.5)>.6;
 if(cat.st==='jump'){c.scale(flip?-1:1,1);c.rotate((cat.jmp.y1<cat.jmp.y0?-.35:.3));catSide(c,C,cat.ph,false,{leap:true,tailUp:true})}
 else if(cat.st==='play'){c.scale(flip?-1:1,1);const up=cat.hopT>0?Math.sin(cat.hopT/.45*Math.PI):Math.max(0,Math.sin(now*9+C.id.length));c.translate(cat.hopT>0?-up*3:0,-up*(cat.hopT>0?6:3));c.rotate(-up*.35);catSide(c,C,cat.ph,true,{tailUp:true,happy:false,paw:cat.swatShow>0})}
 else if(cat.moving||cat.pose==='walk'){c.scale(flip?-1:1,1);catSide(c,C,cat.ph,true,{tailUp:true,blink})}
 else if(cat.pose==='rub'){c.scale(flip?-1:1,1);c.rotate(Math.sin(now*3)*.06);catSide(c,C,cat.ph,false,{tailUp:true,happy:true})}
 else if(cat.pose==='belly'){c.scale(flip?-1:1,1);catBelly(c,C,cat.ph,{wake:cat.wakeT>0,flick:cat.flickT,twitch:cat.wakeT>0?Math.sin(cat.ph*14)*1.3:0})}
 else if(cat.pose==='curl'){c.scale(flip?-1:1,1);catLoaf(c,C,cat.ph,{sleep:!happy,happy,blink,wake:cat.wakeT>0,flick:cat.flickT,twitch:cat.wakeT>0?Math.sin(cat.ph*14)*1.3:0})}
 else if(cat.pose==='knead'){c.scale(flip?-1:1,1);catSit(c,C,cat.ph,{knead:true,happy:true})}
 else if(cat.pose==='yawn'){c.scale(flip?-1:1,1);const yv=Math.sin(cat.ph*.8)>.55;catSit(c,C,cat.ph,{yawn:yv,blink})}
 else if(cat.pose==='stretch'&&cat.st==='rest'){c.scale(flip?-1:1,1);c.translate(0,0);c.rotate(.2);catSide(c,C,cat.ph,false,{stretch:true,tailUp:true,happy:true})}
 else if(cat.pose==='scr'){c.scale(flip?-1:1,1);c.translate(4,0);c.rotate(-.7);catSide(c,C,cat.ph,false,{paw:true,tailUp:true})}
 else if(cat.pose==='toy'){c.scale(flip?-1:1,1);c.translate(2,0);c.rotate(-1.05);catSide(c,C,cat.ph,false,{paw:true,tailUp:true,look:true})}
 else if(cat.pose==='eat'){c.scale(flip?-1:1,1);catSide(c,C,cat.ph,false,{headDown:true,chew:true})}
 else if(cat.pose==='daze'){c.scale(flip?-1:1,1);catSit(c,C,cat.ph,{blink:true,twitch:Math.sin(now*.9+cat.ph)>.985?1.2:0})}
 else if(cat.pose==='glare'){c.scale(flip?-1:1,1);c.rotate(-.05);catSit(c,C,cat.ph,{blink:true})}
 else if(cat.pose==='loaf'){c.scale(flip?-1:1,1);catLoaf(c,C,cat.ph,{sleep:!happy,happy,blink,wake:cat.wakeT>0,flick:cat.flickT,twitch:cat.wakeT>0?Math.sin(cat.ph*14)*1.3:0})}
 else{c.scale(flip?-1:1,1);catSit(c,C,cat.ph,{groom:cat.pose==='groom'&&!happy,happy,blink,twitch:Math.sin(now*.9+cat.ph)>.985?1.2:0})}
 c.restore();
 for(const h of cat.hearts){if(h.t<0)continue;const a=1-h.t/1.4;c.fillStyle=`rgba(232,110,130,${a})`;const hx=cat.x+h.x+Math.sin(h.t*6)*2,hy=cat.y+h.y*CSC-h.t*16;c.beginPath();c.moveTo(hx,hy+2.6);c.bezierCurveTo(hx-4,hy,hx-2,hy-3.4,hx,hy-1.3);c.bezierCurveTo(hx+2,hy-3.4,hx+4,hy,hx,hy+2.6);c.fill()}
 if(cat.happy>0&&!cat.quiet){const nm=catName(C);c.font=`800 7px ${FONT}`;const w=c.measureText(nm).width+8;c.fillStyle='rgba(255,248,236,.95)';rr(c,cat.x-w/2,cat.y-50,w,11,5);c.fill();c.fillStyle='#2E2019';c.textAlign='center';c.textBaseline='middle';c.fillText(nm,cat.x,cat.y-44.3);c.textBaseline='alphabetic'}}
function drawCatTree(c,now){c.save();c.translate(30,DY);const X=40;const sisal=(x,y0,y1)=>{let g=c.createLinearGradient(x-4,0,x+4,0);g.addColorStop(0,'#B8986A');g.addColorStop(.5,'#E2C898');g.addColorStop(1,'#A88858');c.fillStyle=g;c.fillRect(x-4,y0,8,y1-y0);c.strokeStyle='rgba(110,80,40,.45)';c.lineWidth=.7;for(let y=y0+1;y<y1;y+=2.2){c.beginPath();c.moveTo(x-4,y);c.lineTo(x+4,y+1);c.stroke()}};
 const plat=(x,y,rx,col,top)=>{c.fillStyle='rgba(0,0,0,.18)';el(c,x+2,y+4,rx+1,rx*.34);c.fillStyle=col;el(c,x,y+2.5,rx,rx*.36);c.fillRect(x-rx,y-.5,rx*2,3);c.fillStyle=top;el(c,x,y-.5,rx,rx*.34);c.fillStyle='rgba(255,255,255,.12)';el(c,x-rx*.3,y-1.4,rx*.45,rx*.12)};
 softShadow(c,X+8,358,34,7,.26);c.fillStyle='#A88A66';rr(c,X-24,346,64,11,4);c.fill();c.fillStyle='#D8C09A';el(c,X+8,346,32,6.5);
 sisal(24,322,348);sisal(55,290,348);sisal(33,256,320);
 plat(27,320,17,'#9C7E60','#D9C3A2');plat(55,288,16,'#9C7E60','#D9C3A2');
 c.fillStyle='#7A5A40';c.beginPath();c.ellipse(33,256,18,7,0,0,Math.PI);c.lineTo(15,251);c.ellipse(33,251,18,6.4,0,Math.PI,0);c.closePath();c.fill();c.fillStyle='#EFE3CF';el(c,33,251,15,5);c.fillStyle='rgba(0,0,0,.08)';el(c,33,252,11,3.4);
 const sw=Math.sin(now*(2.2+TOY.amp*.8))*3*TOY.amp;c.strokeStyle='rgba(60,40,30,.6)';c.lineWidth=.6;c.beginPath();c.moveTo(69,290);c.lineTo(70+sw,321);c.stroke();c.fillStyle='#E24A5A';circ(c,70+sw,324,3.2);c.fillStyle='rgba(255,255,255,.5)';circ(c,69+sw,323,1);c.strokeStyle='#F2D23E';c.lineWidth=.8;c.beginPath();c.moveTo(67+sw,322);c.lineTo(73+sw,326);c.stroke();
 c.restore();const onTree=CATS?CATS.filter(k=>k.perch>=0&&TREE.perches[k.perch].t===1&&k.st!=='jump').sort((a,b)=>a.y-b.y):[];for(const k of onTree)drawCat(c,k,now)}
function catPortraitURL(C){const k='cat'+C.id;if(ICACHE.has(k))return ICACHE.get(k);const cv=mkCanvas(112),c=cv.getContext('2d');c.fillStyle='#F3E7D2';c.fillRect(0,0,112,112);c.translate(56,100);c.scale(2.8,2.8);catSit(c,C,0,{});const u=cv.toDataURL();ICACHE.set(k,u);return u}

let FRIDGE_T=-9,SINK_T=-9,KPOP={};
function kitchenItems(){return[{k:'sink',x:40,y:FB+6,w:36,h:32},{k:'knife',x:79,y:FB+8,w:16,h:28},{k:'spice',x:332,y:FB+12,w:40,h:24},{k:'fridge',x:330,y:FB+44,w:44,h:LH-FB-44},{k:'bell',x:84,y:FB-12,w:14,h:12}]}
function bump(k){const p=KPOP[k];if(!p)return 0;const t=performance.now()/1000-p;return t<1?Math.abs(Math.sin(t*20))*(1-t)*2:0}
function drawCounter(c,now,V){const X0=-BGM,XW=LW+BGM*2;
 c.fillStyle='rgba(40,30,20,.14)';c.fillRect(X0,FB-5,XW,5);
 let g=c.createLinearGradient(0,FB,0,FB+44);g.addColorStop(0,TH().c0);g.addColorStop(1,TH().c1);c.fillStyle=g;c.fillRect(X0,FB,XW,44);
 const R0=rng(91);c.fillStyle='rgba(120,110,95,.14)';for(let i=0;i<220;i++)c.fillRect(X0+R0()*XW,FB+2+R0()*41,.9,.9);c.fillStyle='rgba(255,255,255,.35)';for(let i=0;i<60;i++)c.fillRect(X0+R0()*XW,FB+2+R0()*41,1.4,.6);
 c.fillStyle=S.level>=4?'#C99A45':'#BDB6AA';c.fillRect(X0,FB-1,XW,2.2);c.fillStyle='rgba(255,255,255,.7)';c.fillRect(X0,FB+1.2,XW,.8);
 c.fillStyle=S.theme&&S.theme!=='classic'?TH().front:(S.level>=4?'#3A3A3C':'#D6D2CA');c.fillRect(X0,FB+44,XW,LH-FB-44);c.fillStyle='rgba(0,0,0,.12)';c.fillRect(X0,FB+44,XW,1.5);c.fillStyle='rgba(255,255,255,.5)';c.fillRect(X0,FB+45.5,XW,.8);
 for(let x=-70;x<326;x+=46){c.strokeStyle='rgba(0,0,0,.1)';c.lineWidth=1;rr(c,x,FB+48,42,LH-FB-51,2);c.stroke();c.fillStyle='#2A2A2A';rr(c,x+15,FB+51,12,1.8,.9);c.fill()}
 let h=c.createRadialGradient(214,FB+16,6,214,FB+16,170);h.addColorStop(0,'rgba(255,200,130,.16)');h.addColorStop(1,'rgba(255,200,130,0)');c.fillStyle=h;c.fillRect(X0,FB-40,XW,90);
 if(propOn('oranges')){/* the bag of oranges 陳伯伯 brought, on the floor by the counter */const bx=40,by=FB-4;c.fillStyle='rgba(40,25,15,.18)';el(c,bx,by+1,9,3);c.fillStyle='#C8A878';c.beginPath();c.moveTo(bx-7,by);c.lineTo(bx-6,by-14);c.lineTo(bx+6,by-14);c.lineTo(bx+7,by);c.closePath();c.fill();c.fillStyle='#B8936A';c.fillRect(bx-6,by-14,12,2);for(const [ox,oy] of[[-3,-15],[2,-16],[-1,-18]]){c.fillStyle='#F0932B';circ(c,bx+ox,by+oy,2.4);c.fillStyle='#5E8F4E';el(c,bx+ox+.5,by+oy-2.2,1.2,.6)}}
 for(const it of kitchenItems())drawKItem(c,it,now);
 if(V.tickets){const ready=[];for(const tk of V.tickets)for(const it of tk.items)if(it.st==='ready'&&!it.picked)ready.push({tk,it});
  ready.slice(0,10).forEach((r,i)=>{const ps=20+KB*.2;const x=110+i*(ps+1),y=FB-3;c.drawImage(dishCanvas(r.it.d,r.it.q,64,S.decor.ware>0,r.it.want),x-ps/2,y-15-(ps-20)*.5,ps,ps);c.fillStyle='#FFF8EC';rr(c,x+3,y-18,12,7,2);c.fill();c.fillStyle='#2E2019';c.font=`800 5.5px ${FONT}`;c.textAlign='center';c.textBaseline='middle';c.fillText('T'+r.tk.no,x+9,y-14.4);c.textBaseline='alphabetic';
   c.strokeStyle='rgba(255,255,255,.45)';c.lineWidth=1;for(let k=0;k<2;k++){const ph=(now*.8+i*.37+k*.5)%1;c.globalAlpha=(1-ph)*.6;c.beginPath();c.moveTo(x-3+k*5,y-12-ph*14);c.quadraticCurveTo(x+2+k*5,y-16-ph*14,x-2+k*5,y-20-ph*14);c.stroke()}c.globalAlpha=1})}}
function drawKItem(c,it,now){const {x,y,w,h}=it;const b=bump(it.k);c.save();c.translate(0,-b);
 switch(it.k){
 case'sink':{c.fillStyle='#B9C1C4';rr(c,x,y+4,w,24,3);c.fill();c.fillStyle='#7E888C';rr(c,x+3,y+7,w-6,18,3);c.fill();c.fillStyle='#A8B3B8';rr(c,x+4,y+8,w-8,6,2);c.fill();c.strokeStyle='#C9D0D3';c.lineWidth=2;c.lineCap='round';c.beginPath();c.moveTo(x+w/2,y+5);c.lineTo(x+w/2,y-8);c.quadraticCurveTo(x+w/2,y-12,x+w/2+5,y-12);c.lineTo(x+w/2+7,y-9);c.stroke();
  const t=now-SINK_T;if(t<2.2){c.strokeStyle='rgba(170,215,240,.9)';c.lineWidth=1.5;c.beginPath();c.moveTo(x+w/2+7,y-8);c.lineTo(x+w/2+7,y+12);c.stroke();c.fillStyle='rgba(255,255,255,.9)';for(let i=0;i<6;i++){const ph=(t*1.4+i*.17)%1;circ(c,x+7+(i*5)%22,y+16-ph*12,1.2+ph)}}
  c.fillStyle='#FFFFFF';el(c,x+11,y+19,5,2);el(c,x+15,y+18,5,2);break}
 case'knife':{c.fillStyle='#3A2E26';c.beginPath();c.moveTo(x,y+26);c.lineTo(x+3,y+8);c.lineTo(x+16,y+8);c.lineTo(x+16,y+26);c.closePath();c.fill();c.fillStyle='#2A2A2A';for(let i=0;i<3;i++){rr(c,x+5+i*3.6,y-1+i,2.4,10,1.1);c.fill()}c.fillStyle='#E9E6E0';rr(c,x+1,y+14,6,12,2);c.fill();c.strokeStyle='#6B4A2E';c.lineWidth=1.2;c.beginPath();c.moveTo(x+3,y+14);c.lineTo(x+2,y+6);c.moveTo(x+5,y+14);c.lineTo(x+6,y+5);c.stroke();break}
 case'spice':{const cols=['#C8321E','#E8A13A','#6FA84E','#F4F1EA','#3A2A20'];c.fillStyle='#B08B5E';rr(c,x,y+14,w,3,1);c.fill();for(let i=0;i<5;i++){const sx=x+2+i*7.6;c.fillStyle='rgba(230,240,245,.92)';rr(c,sx,y+4,6,10,1.5);c.fill();c.fillStyle=cols[i];c.fillRect(sx+1,y+8,4,5.5);c.fillStyle='#2A2A2A';c.fillRect(sx,y+2,6,2.4)}for(let k=0;k<5;k++)leaf(c,x+34+Math.cos(k*1.3)*3,y+1-Math.sin(k)*2,8,3.2,-1.57+(k-2)*.5,k%2?'#3F7F32':'#5E9E3D');break}
 case'fridge':{const t=now-FRIDGE_T;const open=t<1.8;c.fillStyle=S.level>=4?'#4A4A4E':'#C9CDD0';rr(c,x,y+2,w,h-3,2);c.fill();let fg=c.createLinearGradient(x,0,x+w,0);fg.addColorStop(0,'#E4E6E7');fg.addColorStop(.5,'#F7F8F8');fg.addColorStop(1,'#CDD1D3');c.fillStyle=fg;rr(c,x+1,y+(open?5:2),w-2,h-5,2);c.fill();c.fillStyle='#9AA3A6';rr(c,x+8,y+(open?8:5),w-16,2,1);c.fill();c.fillStyle='#2A2F33';rr(c,x+w-12,y+(open?10:7),9,5,1);c.fill();c.fillStyle='#8FD3F4';c.font=`800 3.8px ${FONT}`;c.textAlign='center';c.fillText('3°C',x+w-7.5,y+(open?13.6:10.6));
  if(open){const a=Math.min(1,t/.2)*(t>1.5?Math.max(0,(1.8-t)/.3):1);c.globalAlpha=a;const ms=menuList().slice(0,6);const bw=ms.length*13+8;const bx=Math.min(x+w-bw,x+w/2-bw/2),by=FB-22;c.fillStyle='rgba(255,255,255,.95)';rr(c,bx,by,bw,16,5);c.fill();ms.forEach((d,i)=>{c.drawImage(dishCanvas(d,'G',64,false),bx+4+i*13,by+2,12,12);const n=S.stock[d]||0;c.fillStyle=n<=1?'#E0543A':'#2E2019';c.font=`800 4.5px ${FONT}`;c.textAlign='center';c.fillText(n,bx+10+i*13,by+15.6)});c.globalAlpha=1}
  if(R&&menuList().some(d=>(S.stock[d]||0)<=1)){const p=(Math.sin(now*6)+1)/2;c.fillStyle='#E0543A';circ(c,x+6,y-4-p*1.5,5.5);c.fillStyle='#fff';c.font=`800 7.5px ${FONT}`;c.textAlign='center';c.textBaseline='middle';c.fillText('!',x+6,y-3.6-p*1.5);c.textBaseline='alphabetic'}break}
 case'bell':{c.fillStyle='#C99A45';c.beginPath();c.arc(x+7,y+10,5.5,Math.PI,0);c.fill();c.fillRect(x,y+10,14,2);circ(c,x+7,y+3.6,1.1);c.fillStyle='rgba(255,255,255,.4)';el(c,x+5,y+7,1.4,2.2);break}}
 c.restore()}
function hitKItem(p){if(room!=='main')return null;for(const it of kitchenItems()){if(p.x>=it.x-3&&p.x<=it.x+it.w+3&&p.y>=it.y-8&&p.y<=it.y+it.h+3)return it.k}return null}
/* a tap in one of the other rooms: stations, the fridge, doorways, tables, regulars */
function roomTap(p,e){e.preventDefault();audioInit();
 if(room==='kitchen'){if(R&&!paused&&phase==='service'){const si=hitStation(p);if(si>=0){const s0=R.slots[si];if(s0.broken||s0.job||nextPendingFor(s0.type)){tapStation(si);return true}SW.idle=si;return false}}const f=KR.fridge;if(p.x>=f.x-4&&p.x<=f.x+f.w+4&&p.y>=f.y-8&&p.y<=f.y+f.h+12){FRIDGE_T=performance.now()/1000;sfx.fridge();if(R&&phase==='service')openStock(true);return true}
  if(S.rooms&&S.rooms.cooler){const k=KR.cooler;if(p.x>=k.x-4&&p.x<=k.x+k.w+4&&p.y>=k.y-8&&p.y<=k.y+k.h+12){if(R&&phase==='service')openStock(true);return true}}
  if(p.y>LH-70&&Math.abs(p.x-200)<60){setRoom('main');return true}return false}
 if(room==='side'){const a=SIDE_L.arch;if(p.x>=a.x-8&&p.x<=a.x+a.w+8&&p.y>=a.y-6&&p.y<=a.y+112){setRoom('main');return true}}
 if(room==='front'){if(Math.abs(p.x-FR.door.x)<30&&p.y>176&&p.y<276){setRoom('main');return true}}
 const rg=hitRegular(p);if(rg&&!paused){showRegCard(rg);return true}
 if(!R||paused||phase!=='service')return false;let best=null,bd=1e9;for(const t of R.tables){if((t.room||'main')!==room)continue;const d=Math.hypot((p.x-t.x)*.85,p.y-(t.y-16));const lim=t.seats===4?46:40;if(d<lim&&d<bd){bd=d;best=t}}
 if(best){tapTable(best);return true}return false}
function tapKItem(k){audioInit();KPOP[k]=performance.now()/1000;const now=performance.now()/1000;
 if(k.startsWith('miss:')){toast(`${k.slice(5)}還沒買，打烊後可以在商店購買`);return}
 switch(k){
 case'fridge':{FRIDGE_T=now;sfx.fridge();if(R&&phase==='service')openStock(true);break}
 case'sink':SINK_T=now;sfx.pour();setTimeout(()=>sfx.pour(),200);if(R&&phase==='service'){const t=R.tables.find(t=>t.dirty&&!t.group&&!jillTargets(t.i));if(t){R.jill.q.push(t.i);toast('Jill 去收盤子回來洗')}}break;
 case'knife':sfx.chop();setTimeout(()=>sfx.chop(),110);break;
 case'spice':sfx.shake();break;
 case'bell':sfx.ding();break}}
function tapStation(i){const s=R.slots[i];if(!s)return;audioInit();if(s.broken){s.fix=(s.fix||0)+1;s.shake=1;sfx.chop();trayFloat(s,'修理 '+s.fix+'/8','#FFD27A');if(s.fix>=8){s.broken=false;toast(`${ST_N[s.type]}修好了！`);sfx.ding()}return}if(s.job){R.focus=i;R.panel=true;sfx.tap();return}const n=nextPendingFor(s.type);if(n){R.focus=i;startCook(n.tk,n.it)}else toast(`${ST_N[s.type]}：目前沒有要做的料理`)}



/* ================= today's checkpoint (continue a service day where it stopped) =================
   R is the live day: guests, tickets, what is on every stove, where Jill and the staff are. The
   checkpoint writes it into the save as plain data (references become indices), and restoreService()
   builds a new R from it. Anything that does not resolve throws, and the caller falls back to
   reopening at the same clock with today's numbers kept — and says so. */
const CP_KEYS=['t','dur','si','closed','log','cds','treatT','musicT','blackout','combo','maxCombo','streak','fire','fireCount','tv','gid','tkid','st','rush','rushT0','rushT1','rushShown','weather','event','coach','taskDone','lastSpawn','idleT','focus','sched','inc','noticeT','catCheck','cpT'];
const G_STATES=['arrive','queue','toTable','reading','order','wait','eat','check','leave'];
function snapshotService(){if(!R||phase!=='service'||R.closing!=null||R.ended)return null;
 const ti=t=>t?R.tickets.indexOf(t):-1;
 const ir=it=>{if(!it)return null;for(let a=0;a<R.tickets.length;a++){const k=R.tickets[a].items.indexOf(it);if(k>=0)return[a,k]}return null};
 const groups=R.groups.filter(g=>!g.gone).map(g=>{const o={};for(const k in g)if(!['ticket','wcat','lookCat','claim','gone'].includes(k))o[k]=g[k];o.ticket=ti(g.ticket);o.claim=g.claim||null;return o});
 const gi2=g=>g?groups.findIndex(o=>o.id===g.id):-1;
 const tickets=R.tickets.map(tk=>{const o={};for(const k in tk)if(k!=='g'&&k!=='items')o[k]=tk[k];o.g=gi2(tk.g);o.items=tk.items.map(i=>Object.assign({},i));o.claim=tk.claim||null;return o});
 const slots=R.slots.map(s0=>{const o={broken:!!s0.broken,fix:s0.fix||0,job:null};if(s0.job){const j=s0.job;const jo={};for(const k in j)if(k!=='tk'&&k!=='it')jo[k]=j[k];jo.tk=ti(j.tk);jo.it=ir(j.it);o.job=jo}return o});
 const J=R.jill;const jill={};for(const k in J)if(!['carry','cur','pet','lookAt','rest','restPos','sofa','visit'].includes(k))jill[k]=J[k];jill.carry=J.carry.map(c=>({tk:ti(c.tk),it:ir(c.it)}));jill.cur=J.cur?Object.assign({},J.cur):null;
 const cw={};for(const id in R.cw||{}){const w=R.cw[id];const o={};for(const k in w)if(k!=='task'&&k!=='carry')o[k]=w[k];o.task=w.task?Object.assign({},w.task,{g:gi2(w.task.g),t:w.task.t?w.task.t.i:-1,tk:ti(w.task.tk)}):null;o.carry=w.carry?w.carry.map(ir):null;cw[id]=o}
 const tables=R.tables.map(t=>({group:gi2(t.group),dirty:!!t.dirty,plates:(t.plates||[]).map(p=>Object.assign({},p)),busT:t.busT||0,claim:t.claim||null}));
 const misc={};for(const k of CP_KEYS)if(k in R)misc[k]=R[k];
 const snap={groups,tickets,slots,jill,cw,tables,misc,tablesN:R.tables.length,slotsN:R.slots.length};
 return JSON.parse(JSON.stringify(snap))}   /* through JSON once: proves it is plain data, drops undefined */
function checkpointSave(why){if(!R||phase!=='service')return false;try{const snap=snapshotService();if(!snap)return false;S.checkpoint={day:S.day,at:R.t,clock:clockStr(),why,snap};save();return true}catch(e){console.warn('[checkpoint] not saved:',e&&e.message);return false}}
function clearCheckpoint(){if(S.checkpoint){S.checkpoint=null}}
function restoreService(cp){const snap=cp.snap;if(!snap||cp.day!==S.day)throw new Error('checkpoint is for another day');
 lifeReset();streetReset();dylanStageCheck();bg=null;lastEv=null;const dur=snap.misc.dur||dayDur(S.day);
 const N={t:0,dur,tables:buildTables(),slots:buildSlots(),groups:[],tickets:[],sched:[],si:0,closed:false,ended:false,
  jill:{x:PASS.x,y:PASS.y,tx:null,ty:null,q:[],cur:null,busy:0,carry:[],idle:0,face:1,step:0,room:'main',troom:'main'},
  combo:0,maxCombo:0,streak:0,fire:0,fireCount:0,floats:[],parts:[],tv:1,gid:1,tkid:1,
  st:{rev:0,tips:0,guests:0,groups:0,perfect:0,q:{P:0,G:0,O:0,B:0},sats:[],dish:{},angry:0,lost:0,reviews:[],critic:null,blogger:null,treats:0},
  rush:feat().rush,rushT0:dur*120/270,rushT1:dur*180/270,rushShown:false,weather:S.today&&S.today.weather,event:S.today&&S.today.event,coach:-1,taskDone:{},lastSpawn:0,idleT:0,focus:0,focusLock:0,holdSlot:null,inc:[],cw:{},thief:null,insp:null,chaser:null};
 if(N.tables.length!==snap.tablesN||N.slots.length!==snap.slotsN)throw new Error('room changed');
 for(const k of CP_KEYS)if(k in snap.misc)N[k]=snap.misc[k];
 N.groups=snap.groups.map(o=>Object.assign({},o,{wcat:null,gone:false}));
 N.tickets=snap.tickets.map(o=>Object.assign({},o,{items:o.items.map(i=>Object.assign({},i))}));
 N.tickets.forEach((tk,i)=>{tk.g=N.groups[snap.tickets[i].g];if(!tk.g)throw new Error('ticket without guests')});
 N.groups.forEach((g,i)=>{const t=snap.groups[i].ticket;g.ticket=t>=0?N.tickets[t]:null;if(t>=0&&!g.ticket)throw new Error('guests without ticket');if(!G_STATES.includes(g.state)||!isFinite(g.x)||!isFinite(g.y)||!Array.isArray(g.looks))throw new Error('bad guest')});
 snap.tables.forEach((o,i)=>{const t=N.tables[i];t.group=o.group>=0?N.groups[o.group]:null;if(o.group>=0&&!t.group)throw new Error('table without guests');t.dirty=o.dirty;t.plates=o.plates||[];t.busT=o.busT||0;t.claim=o.claim||null});
 const item=ref=>{if(!ref)return null;const tk=N.tickets[ref[0]];return tk&&tk.items[ref[1]]||null};
 snap.slots.forEach((o,i)=>{const s0=N.slots[i];s0.broken=!!o.broken;s0.fix=o.fix||0;if(o.job){const j=Object.assign({},o.job);j.tk=N.tickets[o.job.tk];j.it=item(o.job.it);if(!j.tk||!j.it||!DISH(j.d))throw new Error('job without ticket');if(j.step){j.step=Object.assign({},j.step);j.step.hold=false}s0.job=j}});
 Object.assign(N.jill,snap.jill);N.jill.carry=snap.jill.carry.map(c=>({tk:N.tickets[c.tk],it:item(c.it)})).filter(c=>c.tk&&c.it);N.jill.cur=snap.jill.cur?Object.assign({},snap.jill.cur):null;N.jill.q=(snap.jill.q||[]).slice();if(!isFinite(N.jill.x)||!isFinite(N.jill.y))throw new Error('bad jill');N.jill.sofa=false;N.jill.rest=null;N.jill.pet=null;N.jill.lookAt=null;N.jill.nod=0;N.jill.visit=null;
 for(const id in snap.cw){const o=snap.cw[id];const w=Object.assign({},o);if(o.task){w.task=Object.assign({},o.task);w.task.g=o.task.g>=0?N.groups[o.task.g]:null;w.task.t=o.task.t>=0?N.tables[o.task.t]:null;w.task.tk=o.task.tk>=0?N.tickets[o.task.tk]:null;if((o.task.g>=0&&!w.task.g)||(o.task.t>=0&&!w.task.t)||(o.task.tk>=0&&!w.task.tk))w.task=null}w.carry=o.carry?o.carry.map(item).filter(Boolean):null;if(w.carry&&!w.carry.length)w.carry=null;N.cw[id]=w}
 N.holdSlot=null;N.panel=false;N.panelT=0;N.closing=null;
 R=N;phase='service';paused=false;hideScreen();layoutAll();renderTickets();renderTasks();hud(true);audioInit();return true}
function resumeCheckpoint(){const cp=S.checkpoint;if(!cp||cp.day!==S.day){goMain();return}
 applyGates();if(!S.today)planToday();
 try{restoreService(cp);banner('繼續營業',`DAY ${S.day} · ${cp.clock}`,'');toast(`從 ${cp.clock} 繼續今天的營業`)}
 catch(e){console.warn('[checkpoint] could not restore fully:',e&&e.message);
  /* the safe fallback: reopen at the same clock with today's numbers, the room starts empty */
  startService();R.t=cp.at;if(cp.snap&&cp.snap.misc){if(cp.snap.misc.st)R.st=cp.snap.misc.st;if(cp.snap.misc.sched)R.sched=cp.snap.misc.sched;if(cp.snap.misc.si!=null)R.si=cp.snap.misc.si}
  toast(`今天的店內狀況無法完整還原，從 ${cp.clock} 重新開店（今天的營收與客人數都保留，店裡的客人會重新入座）`)}
 clearCheckpoint();save()}
/* ================= life: the sofa, the rolling TV, Jill's evenings, Dylan ================= */
/* Nothing in this section plays a scene. Jill, Dylan, the five cats and the TV each decide for
   themselves from their own state, personality, what is free on the sofa, where the others are,
   cooldowns and chance. Whatever happens on a given evening comes out of those rules. */
const SOFA={x0:88,x1:208,y:100,back:86,seat:112,front:142,arm:12,jy:134,catY:132,backY:90,armY:100};
SOFA.seatL=SOFA.x0+SOFA.arm;SOFA.seatR=SOFA.x1-SOFA.arm;
const JPOS={L:{x:122,face:1},R:{x:174,face:-1},M:{x:148,face:1}};   /* where Jill can sit; L = legs to the right, towards the TV */
const TV_PARK={x:352,y:118};
function tvUsePos(){return LIFE.jill.pos==='R'?{x:SOFA.x0,y:146}:{x:SOFA.x1,y:146}}   /* in front of the arm at Jill's feet */
const DYLAN={id:'dylan',n:'Dylan',type:'regular',size:1,fav:['signature'],looks:[{skin:'#EDC19C',hair:'#2A211C',hs:6,top:'#4E5A6B',acc:null,pants:'#3B3A44'}],
 who:'一個人來，話不多。喜歡坐看得到廚房的位子。',who2:'Jill 的先生。結婚 11 年。打烊以後，有時候會留下來——然後隔天再來追一次。'};
REG_BY.dylan=DYLAN;
const LIFE={day:0,plan:null,t:0,jill:null,tv:null,dylan:null,say:[],revealRoll:0};
function lifeReset(){LIFE.day=0;LIFE.plan=null;LIFE.t=0;LIFE.revealRoll=0;LIFE.say=[];LIFE.dylan=null;
 LIFE.jill={on:false,pos:null,x:PASS.x,y:PASS.y,face:1,step:0,legs:0,legTarget:0,act:null,last:null,t:0,flipT:0,flip:0,gazeT:0,gazeX:0,settleT:32,bobT:0,catNew:0,sinceSit:0,walking:false,tx:0,ty:0,via:null,after:null,sitT:0,petCat:null,counted:false};
 LIFE.tv={x:TV_PARK.x,y:TV_PARK.y,at:'park',on:false,face:0,mover:null,path:null,wait:0,offT:0,tried:0,step:0}}
lifeReset();
function segHitsRect(x0,y0,x1,y1,r){for(let i=0;i<=10;i++){const u=i/10,px=x0+(x1-x0)*u,py=y0+(y1-y0)*u;if(px>r.a&&px<r.b&&py>r.t&&py<r.d)return true}return false}
/* ---- who is where on the seat ---- */
function jillLegs(){const J=LIFE.jill;if(!J.on||(J.legs<.05&&J.legTarget<.05))return null;const len=10+Math.max(J.legs,J.legTarget)*32;return J.face>0?[J.x+3,J.x+3+len]:[J.x-3-len,J.x-3]}
function seatIvs(exclude){const out=[];const J=LIFE.jill,D=LIFE.dylan;if(J.on){out.push({a:J.x-13,b:J.x+13,who:'jill'});const lg=jillLegs();if(lg)out.push({a:lg[0],b:lg[1],who:'legs'})}else if(J.reserved&&J.pos)out.push({a:JPOS[J.pos].x-13,b:JPOS[J.pos].x+13,who:'jill'});
 if(D&&(D.onSofa||D.state==='toSofa'||D.state==='waitSofa'))out.push({a:(D.onSofa?D.x:D.tx)-13,b:(D.onSofa?D.x:D.tx)+13,who:'dylan'});
 if(CATS)for(const c of CATS){if(c===exclude||!c.sofa||c.sofa.kind!=='seat')continue;out.push({a:c.sofa.x-12,b:c.sofa.x+12,who:c})}return out}
function ivFree(a,b,ivs){if(a<SOFA.seatL||b>SOFA.seatR)return false;for(const v of ivs)if(a<v.b+1&&b>v.a-1)return false;return true}
function sofaCats(){return CATS?CATS.filter(c=>c.sofa&&c.sofaOn):[]}
function sofaSlots(c){const J=LIFE.jill,D=LIFE.dylan;const ivs=seatIvs(c);const out=[];const taken=k=>CATS.some(o=>o!==c&&o.sofa&&o.sofa.k===k);
 for(const x of[112,136,160,184])if(ivFree(x-12,x+12,ivs))out.push({k:'seat'+x,x,y:SOFA.catY,kind:'seat'});
 if(J.on&&!taken('lap')){const lg=jillLegs();out.push({k:'lap',x:lg?(lg[0]+lg[1])/2:J.x+J.face*2,y:lg?SOFA.catY:SOFA.jy+4,kind:'lap'})}
 for(const [k,x] of[['armL',SOFA.x0+6],['armR',SOFA.x1-6]])if(!taken(k)&&!(D&&D.onSofa&&Math.abs(D.x-x)<22))out.push({k,x,y:SOFA.armY,kind:'arm'});
 for(const x of[114,140,166,192]){if(J.on&&Math.abs(x-J.x)<22)continue;if(D&&D.onSofa&&Math.abs(x-D.x)<22)continue;if(taken('back'+x))continue;if(CATS.some(o=>o!==c&&o.sofa&&o.sofa.kind==='back'&&Math.abs(o.sofa.x-x)<25))continue;out.push({k:'back'+x,x,y:SOFA.backY,kind:'back'})}
 return out}
/* ---- cats choosing a place on the sofa (personality × occupancy × who is already there) ---- */
function dylanSeatX(){const J=LIFE.jill;if(!(LIFE.dylan&&S.dylan.stage>=3&&(J.on||J.pos)))return null;const face=J.on?J.face:JPOS[J.pos].face;return face>0?184:112}
function pickSofaSlot(c,wantNear){const id=c.def.id;const sl=sofaSlots(c);if(!sl.length)return null;const J=LIFE.jill,D=LIFE.dylan;const dx=dylanSeatX();
 const dJ=s=>J.on?Math.hypot(s.x-J.x,s.y-120):999;const dD=s=>D&&D.onSofa?Math.hypot(s.x-D.x,s.y-120):999;
 const others=sofaCats().filter(o=>o!==c);const crowd=s=>others.reduce((a,o)=>a+Math.max(0,30-Math.hypot(o.sofa.x-s.x,o.sofa.y-s.y)),0);
 const mate=(idl,w,s)=>{const o=catBy(idl);return o&&o.sofa?w*Math.max(0,60-Math.hypot(o.sofa.x-s.x,o.sofa.y-s.y))/60:0};
 return wpick(sl,s=>{let w=1;
  if(id==='snow'){w=s.kind==='seat'?3:s.kind==='lap'?1.2:s.kind==='arm'?.3:.2;if(s.kind==='seat'&&(s.x<=112||s.x>=184))w*=1.4;if(J.on)w*=1+Math.max(0,50-dJ(s))/50;w*=1+Math.max(0,40-dD(s))/40*.5}
  else if(id==='mei'){w=s.kind==='back'?3:s.kind==='arm'?2.2:s.kind==='seat'?.8:.25;w*=1/(1+crowd(s)*.08)}
  else if(id==='tora'||id==='ban'){w=wantNear&&J.on?Math.max(.2,80-dJ(s))/80*3:(s.kind==='seat'?1.2:s.kind==='lap'?(J.on?1.5:0):.7);if(id==='tora')w*=1+Math.max(0,50-dD(s))/50*.6;if(id==='ban')w*=1+mate('tora',.8,s)}
  else{w=s.kind==='seat'?1:s.kind==='arm'?1.1:s.kind==='back'?.9:.6;w*=1+mate('ban',1.2,s)+mate('tora',.9,s)+mate('mei',1,s);if(J.on&&wantNear)w*=1+Math.max(0,80-dJ(s))/80}
  if(dx!=null&&s.kind==='seat'&&s.x===dx)w*=.35; /* his usual place */
  return w})}
function sofaWeight(c){const id=c.def.id;const J=LIFE.jill,D=LIFE.dylan;let w=id==='snow'?2.4:id==='mei'?2.2:id==='mikan'?.9:id==='tora'?.7:.6;
 if(J.on)w*=(id==='tora'||id==='ban')?.5:1.3;
 if(id==='mikan'&&CATS.some(o=>o!==c&&o.sofa&&o.def.id==='mei'))w+=1;
 if(D&&D.onSofa){if(id==='tora')w+=.6;if(id==='snow')w+=.3}
 if(evening())w*=1.3;if(c.sofaCD>ctime)w*=.2;const sl=sofaSlots(c);if(!sl.length)return 0;if(id==='snow'&&!sl.some(s=>s.kind==='seat'||s.kind==='lap'))w*=.25;return w}
function goSofaSlot(c,s){releaseSpots(c);c.sofa={k:s.k,x:s.x,y:s.y,kind:s.kind};c.sofaOn=false;c.guest=null;catWalk(c,clamp(s.x,SOFA.x0-4,SOFA.x1+4),SOFA.front+10,'sofaUp')}
function goSofaJill(c){const id=c.def.id;const J=LIFE.jill;const jx=J.on?J.x:JPOS[J.pos||'L'].x;const rival=id==='tora'?catBy('ban'):id==='ban'?catBy('tora'):null;const sl=sofaSlots(c);
 const floor=()=>{const p={x:clamp(jx+rand(-22,22),96,316),y:SOFA.front+10};catWalk(c,p.x,p.y,'rest')};
 if(!sl.length){floor();return}
 const dJ=s=>Math.hypot(s.x-jx,s.y-120);const best=sl.slice().sort((a,b)=>dJ(a)-dJ(b))[0];
 const rivalCloser=rival&&rival.sofa&&rival.sofa.kind!=='back'&&dJ(rival.sofa)<dJ(best);
 if(rivalCloser){const r=Math.random();if(r<.2){floor();return}if(r<.32){const p=pickFloor(c);catWalk(c,p.x,p.y,'rest');return}}
 const dx=dylanSeatX();const s=(id==='tora'||id==='ban')&&!(rivalCloser&&Math.random()<.5)&&!(best.kind==='seat'&&best.x===dx&&Math.random()<.65)?best:pickSofaSlot(c,true);if(!s){floor();return}goSofaSlot(c,s)}
function sofaSettle(c,fresh){const id=c.def.id;const J=LIFE.jill;const s=c.sofa;c.moving=false;c.run=0;
 const sleepy=(id==='snow'?.8:s.kind==='lap'?.5:.35)*(evening()?1.2:1);
 if(Math.random()<sleepy){sleepHere(c,evening()?30:20,evening()?90:50);if(s.kind!=='seat')c.pose='loaf'}
 else{c.st='rest';c.pose=s.kind==='lap'?pick(['loaf','curl','loaf']):pick(['sit','loaf','groom','loaf']);c.t=rand(8,24)}
 c.face=J.on?(J.x>=c.x?1:-1):(Math.random()<.5?1:-1);
 if(fresh&&J.on&&Math.abs(c.x-J.x)<46){LIFE.jill.gazeT=rand(1.2,2.2);LIFE.jill.gazeX=c.x;LIFE.jill.catNew++}
 if(id==='mei')BAO_LAST={perch:null,x:c.x,y:c.y,t:ctime}}
function moveSofaSlot(c,s){c.sofa={k:s.k,x:s.x,y:s.y,kind:s.kind};c.sofaOn=false;catJump(c,s.x,s.y,'sofaLand')}
function leaveSofa(c,then){c.sofa=null;c.sofaOn=false;c.sofaLeaving=true;c.sofaCD=ctime+rand(20,60);catJump(c,clamp(c.x+rand(-14,14),SOFA.x0-6,SOFA.x1+6),SOFA.front+12,then||'decide')}
function sofaDecide(c){const id=c.def.id;const J=LIFE.jill;
 let stay=id==='snow'?.85:id==='mei'?.6:id==='tora'?(J.on?.78:.4):id==='ban'?(J.on?.72:.4):.45;if(evening())stay+=.08;
 if(Math.random()<stay){
  if(J.on&&(id==='tora'||id==='ban')&&Math.random()<.25){const sl=sofaSlots(c);const dJ=s=>Math.hypot(s.x-J.x,s.y-120);const cur=dJ(c.sofa);const better=sl.filter(s=>dJ(s)<cur-8).sort((a,b)=>dJ(a)-dJ(b))[0];if(better){moveSofaSlot(c,better);return}}
  sofaSettle(c);return}
 leaveSofa(c,'decide')}
/* ---- Jill's evening ---- */
function lifePlan(){if(LIFE.day===S.day&&LIFE.plan)return;LIFE.day=S.day;LIFE.t=0;LIFE.revealRoll=0;LIFE.say=[];
 LIFE.plan=Math.random()<.85?'sofa':'table';const J=LIFE.jill;Object.assign(J,{on:false,reserved:false,pos:null,legs:0,legTarget:0,act:null,last:null,t:0,walking:false,via:null,after:null,sitT:0,catNew:0,sinceSit:0,counted:false,tvFirst:false})}
function freeJillPos(){const ivs=seatIvs(null);const ok=p=>ivFree(JPOS[p].x-13,JPOS[p].x+13,ivs);const clearHead=p=>!sofaCats().some(o=>o.sofa.kind==='back'&&Math.abs(o.sofa.x-JPOS[p].x)<20);
 const order=Math.random()<.7?['L','R','M']:['R','L','M'];return order.find(p=>ok(p)&&clearHead(p))||order.find(ok)||null}
function jillWalk(L,x,y,after){L.tx=x;L.ty=y;L.after=after;L.walking=true;L.via=null;
 if(L.y<148&&y>=148)L.via={x:L.x,y:152};else if(y<148&&L.y>=148)L.via={x,y:152}}
function jillLife(J,L,dt){const tv=LIFE.tv;
 if(L.walking){const tx=L.via?L.via.x:L.tx,ty=L.via?L.via.y:L.ty;const dx=tx-L.x,dy=ty-L.y,d=Math.hypot(dx,dy),v=140*dt;
  if(d<=v){L.x=tx;L.y=ty;if(L.via){L.via=null}else{L.walking=false;const a=L.after;L.after=null;jillArrive(L,a)}}else{L.x+=dx/d*v;L.y+=dy/d*v;L.face=dx>=0?1:-1;L.step+=dt*12}}
 else if(L.sitT>0){L.sitT-=dt;if(L.sitT<=0){L.on=true;L.reserved=false;L.y=SOFA.jy;L.act='settle';L.t=rand(1.5,4);L.sinceSit=0;
   if(!L.counted){L.counted=true;S.life=S.life||{};S.life.sofa=(S.life.sofa||0)+1}
   for(const c of CATS||[]){if(c.st==='side'){releaseSpots(c);c.st='rest';c.pose='sit';c.t=rand(.4,1.8)}else if(c.st==='walk'&&c.after==='side'){releaseSpots(c);c.after='rest';c.afterT=rand(.5,2)}}}}
 else if(L.act==='toSofa'){const pos=L.reserved&&L.pos?L.pos:freeJillPos();if(!pos){lifeNoRoom();return}L.pos=pos;L.reserved=true;L.face=JPOS[pos].face;
  if(!L.tvFirst&&tv.at==='park'&&!tv.mover&&tv.tried<2&&Math.random()<.4){L.tvFirst=true;L.act='standing';jillWalk(L,tv.x+18,tv.y+4,'grabTV');return} /* on her way: bring the TV over first */
  jillWalk(L,JPOS[pos].x,SOFA.front+10,'sit')}
 else if(L.on){L.sinceSit+=dt;L.t-=dt;
  /* legs: stretch out when the seat beside her is free, pull them in when someone needs the room */
  const want=L.legTarget;const room=ivFree(L.face>0?L.x+3:L.x-3-42,L.face>0?L.x+3+42:L.x-3,seatIvs(null).filter(v=>v.who!=='jill'&&v.who!=='legs'));
  if(L.legTarget===0&&room&&['read','idle','tv'].includes(L.act)&&Math.random()<dt*.04)L.legTarget=1;
  const target=(L.act==='fetch'||L.act==='standing')?0:want;if(Math.abs(L.legs-target)>.01){const st=L.legs<target?1.6:2.2;L.legs=L.legs<target?Math.min(target,L.legs+dt*st):Math.max(target,L.legs-dt*st)}
  if(L.gazeT>0)L.gazeT-=dt;if(L.flip>0)L.flip-=dt;if(L.bobT>0)L.bobT-=dt;
  L.settleT-=dt;if(L.settleT<=0){L.settleT=rand(25,50);L.bobT=.5}
  if(L.act==='read'){L.flipT-=dt;if(L.flipT<=0){L.flipT=rand(5,13);L.flip=.35}}
  if(L.act==='settle'&&L.t<=0){L.legTarget=room&&Math.random()<.85?1:0;jillDecide(L)}
  else if(L.act==='wantTV'){if(tv.mover){L.act='waitTV';L.t=30}else if(L.t<=0){if(!CATS.some(c=>c.sofa&&c.sofa.kind==='lap')&&tvUsable()&&tv.tried<2){L.act='fetch';L.fetch='legsIn';L.t=0}else{L.last='tv';L.act=null;jillDecide(L)}}}
  else if(L.act==='waitTV'){if(tv.at==='use'&&!tv.mover){tv.on=true;L.act='tv';L.t=rand(30,90);S.life.tv=(S.life.tv||0)+1}else if(!tv.mover||L.t<=0){L.act=null;L.last='tv';jillDecide(L)}}
  else if(L.act==='fetch'){if(L.fetch==='legsIn'&&L.legs<.05){L.fetch='stand';L.on=false;L.reserved=true;L.y=SOFA.front+10;L.act='standing';jillWalk(L,tv.x+18,tv.y+4,'grabTV')}}
  else if(['read','idle','tv','pet'].includes(L.act)&&L.t<=0){if(L.act==='pet'&&L.petCat)L.petCat=null;jillDecide(L)}
  if(L.act==='tv'&&!(tv.on&&tv.at==='use')){L.act=null;jillDecide(L)}
  if(L.catNew>0&&L.act!=='pet'&&L.act!=='settle'&&Math.random()<dt*.25){const near=sofaCats().filter(c=>Math.abs(c.x-L.x)<46);if(near.length){L.petCat=pick(near);L.act='pet';L.t=rand(2,4);L.petCat.hearts.push({x:0,y:-24,t:0});if(Math.random()<.5)L.petCat.happy=Math.max(L.petCat.happy,1.5),L.petCat.quiet=1}L.catNew=0}}
 else if(L.act==='wrap'){L.face=1;L.wrapT=(L.wrapT||0)-dt;if(L.wrapT<=0)L.act='toSofa'}
 else if(L.act==='standing'&&!L.walking){/* stood up but has nothing to do: sit back down */L.act='toSofa'}
 /* mirror into the view's Jill so everything that reads view().jill sees her where she is */
 J.x=L.x;J.y=L.y;J.face=L.face;J.moving=L.walking||L.act==='pushing';J.step=L.step;J.sit=L.on;J.sofa=L.on?L.pos:null}
function jillArrive(L,a){const tv=LIFE.tv;
 if(a==='sit'){L.sitT=.35;L.face=JPOS[L.pos].face;L.y=SOFA.front+10;L.act='sitting'}
 else if(a==='grabTV'){if(tv.mover||tv.at==='use'){L.act='toSofa';return}tv.mover='jill';tv.path=[{x:tv.x,y:tvUsePos().y},{x:tvUsePos().x,y:tvUsePos().y}];tv.wait=0;L.act='pushing';L.face=-1}
 else if(a==='back'){L.act='toSofa'}
 else if(a==='wrap'){L.act='wrap'}}
function jillDecide(L){const tv=LIFE.tv,D=LIFE.dylan;const W=[];const add=(k,w)=>{if(w>0)W.push([k,w])};
 add('read',L.last==='read'?2:4);add('idle',L.last==='idle'?1.2:2.4);
 const lap=CATS.some(c=>c.sofa&&c.sofa.kind==='lap');const tvOk=tvUsable()&&!(tv.at!=='use'&&lap&&!(D&&!D.onSofa&&S.dylan.stage>=1));
 add('tv',tvOk?(L.last==='tv'?1.2:2.4)*(tv.at==='use'?1.3:1)*(D&&D.onSofa&&S.dylan.stage>=3?1.4:1):0);
 const k=wpick(W,o=>o[1])[0];L.last=k;L.act=k;
 if(k==='read'){L.t=rand(25,75);L.flipT=rand(4,10)}else if(k==='idle')L.t=rand(10,40);
 else if(k==='tv'){if(tv.at==='use'&&!tv.mover){tv.on=true;L.t=rand(30,90);S.life.tv=(S.life.tv||0)+1;tvNoticed()}else{L.act='wantTV';L.t=rand(2,6)}}}
/* ---- the rolling TV ---- */
function tvUsable(){const tv=LIFE.tv;if(tv.at==='use')return Math.abs(tv.x-tvUsePos().x)<3;if(tv.mover)return false;return tv.tried<2&&tv.at==='park'}
function tvNoticed(){for(const c of CATS||[]){if(c.hidden||c.st!=='rest'||Math.random()>.3)continue;const d=Math.hypot(c.x-LIFE.tv.x,c.y-LIFE.tv.y);if(d<130)c.lookAt={x:LIFE.tv.x,y:LIFE.tv.y-20,hidden:false}}}
function tvBlocked(tv,dx,dy){const px=tv.x+dx*26,py=tv.y+dy*24;const who=tv.mover;const near=(x,y,r)=>Math.hypot(x-px,y-py)<r;
 for(const c of CATS||[]){if(c.hidden||c.perch>=0||c.sofa)continue;if(near(c.x,c.y-6,22)||Math.hypot(c.x-tv.x,c.y-6-tv.y)<19)return true}
 if(who!=='jill'&&LIFE.jill.on===false&&near(LIFE.jill.x,LIFE.jill.y-10,22))return true;
 if(who!=='dylan'&&LIFE.dylan&&!LIFE.dylan.onSofa&&!LIFE.dylan.seated&&near(LIFE.dylan.x,LIFE.dylan.y-10,22))return true;return false}
function tvUpd(dt){const tv=LIFE.tv;
 if(tv.mover){const n=tv.path[0];if(!n){tvDone(true);return}const dx=n.x-tv.x,dy=n.y-tv.y,d=Math.hypot(dx,dy);
  if(d<1){tv.path.shift();if(!tv.path.length)tvDone(true);return}
  if(tvBlocked(tv,dx/d,dy/d)){tv.wait+=dt;if(tv.wait>5)tvDone(false);return}
  tv.wait=Math.max(0,tv.wait-dt);const v=Math.min(d,44*dt);tv.x+=dx/d*v;tv.y+=dy/d*v;tv.step+=dt*12;tv.at='moving';
  const m=tv.mover==='jill'?LIFE.jill:LIFE.dylan;if(m){m.x=tv.x+18;m.y=tv.y+3;m.face=-1;m.step=tv.step;m.walking=false;m.moving=true}}
 else if(tv.on){const w=(LIFE.jill.on&&LIFE.jill.act==='tv')||(LIFE.dylan&&LIFE.dylan.onSofa&&LIFE.dylan.act==='tv');tv.offT=w?0:tv.offT+dt;if(tv.offT>25){tv.on=false;tv.offT=0}}}
function tvDone(ok){const tv=LIFE.tv;const who=tv.mover;tv.mover=null;tv.path=null;
 if(ok&&Math.abs(tv.x-tvUsePos().x)<2&&Math.abs(tv.y-tvUsePos().y)<2){tv.at='use';tv.face=LIFE.jill.pos==='R'?1:-1;tv.on=true;tvNoticed();if(who==='dylan'){S.dylan.clues.tv=(S.dylan.clues.tv||0)+1}}
 else{tv.at='stuck';tv.tried++}
 if(who==='jill'){const L=LIFE.jill;L.moving=false;L.act='standing';jillWalk(L,JPOS[L.pos].x,SOFA.front+10,'back');if(ok)L.last='tv-fetched'}
 else if(who==='dylan'&&LIFE.dylan){const D=LIFE.dylan;D.moving=false;D.state='think';D.t=rand(.5,1.5)}}
/* ---- Dylan ---- */
function dylanStays(){const d=S.dylan;if(!d||d.stage<1)return false;if(!R.closed&&R.t<R.dur*.72)return false;return Math.random()<(d.stage>=2?.8:.6)}
function dylanLinger(g,t){g.gone=true;const sp=seatPos(t)[0];LIFE.dylan={x:t.x+sp.dx,y:t.y+sp.dy,face:sp.side>0?-1:1,state:'linger',table:t.i,seat:0,seated:true,onSofa:false,t:rand(3,8),phone:Math.random()<.7,walking:false,step:0,moving:false,carry:false,catCD:0,tidied:false,act:null,talkT:rand(30,70),since:0};
 const d=S.dylan;d.stay=(d.stay||0)+1;d.clues.late=(d.clues.late||0)+1}
function dylanStageCheck(){const d=S.dylan;if(!d)return;const v=S.regulars.dylan||0;const cl=Object.keys(d.clues||{}).filter(k=>d.clues[k]>0).length;
 if(d.stage===0&&v>=3&&S.day>=6)d.stage=1;
 if(d.stage===1&&S.day>=12&&v>=6&&(d.stay||0)>=2&&cl>=3&&(S.life&&S.life.sofa||0)>=3&&((d.clues.pet||0)>=1||(d.clues.tidy||0)>=3||(d.clues.pause||0)>=2))d.stage=2}
function dylanLine(){const st=S.dylan.stage;if(st>=3)return pick(['今天很累了吧。','不急，我等妳。','貓都在。']);return pick(['今天人很多。','貓咪們今天很乖。',R&&R.weather==='rain'?'外面開始下雨了。':'今天天氣很好。'])}
/* The running act: he asks, she brushes him off. Before the reveal it reads as a patient regular
   trying his luck; after it, the same act keeps going — now it's an old joke between the two of
   them. Each entry: what he says, what she answers (null = she doesn't dignify it), what he adds. */
const DYLAN_ACT={
 before:[['老闆娘，今天有空嗎？','沒有。'],['老闆娘，妳有男朋友嗎？','先吃飯。'],['今天的菜好吃到想每天來。','你本來就每天來。'],['老闆娘，可以留個電話嗎？','不行。'],['老闆娘，妳綁馬尾很好看。',null],['我下次帶花來。','帶錢來就好。'],
  ['主廚，請問今日推薦是什麼？','你可以正常講話。','我只是尊重主廚。'],['這道菜，跟昨天一樣好。','你昨天不是才吃過？','昨天跟今天是不同的約會。'],['老闆娘，妳今天有笑。','我每天都有。','沒有，今天比較多。'],['我可以坐這裡看妳做菜嗎？','你已經坐下了。',null],['老闆娘，這隻貓好像認識我。','牠誰都認識。','牠剛剛只來我這桌。'],['老闆娘，打烊後要去哪？','回家。','一個人？','跟貓。']],
 after:[['老闆娘，明天有空嗎？','不行，我老公會生氣。','那確實滿麻煩的。'],['老闆娘，可以留個電話嗎？','你不是有嗎？','再要一次也不行喔？'],['老闆娘，妳一個人住嗎？','跟五隻貓，還有一個很煩的人。','聽起來滿熱鬧的。'],['老闆娘，這道菜是為我做的吧？','是為 {T} 號桌做的。',null],['老闆娘，晚上一起吃飯？','回家吃。','好。'],
  ['老闆娘，今天早點打烊？','看貓答不答應。','牠們一向答應。'],['主廚，今天的菜有進步。','你昨天也這樣講。','昨天也是真的。'],['老闆娘，我可以追妳嗎？','追到了再說。','那就是可以。'],['老闆娘，紀念日想吃什麼？','你記得日期？','我只是問問。','……那天店裡吃。'],['這位子有人坐嗎？','有，一個很煩的人。','那我坐旁邊。'],['老闆娘，我今天可以幫忙嗎？','不用，你是客人。','客人可以每天來嗎？','你不是已經每天來了。']]};
/* Scenes that belong to a moment: the place grew, a cat took something first, a regular noticed. Each plays once. */
const DYLAN_SCENES=[
 {k:'side',when:()=>projOn('side'),lines:[['側廳有位子嗎？','你坐哪都一樣。','不一樣，那邊看得到妳。'],['妳把牆打掉了。','嗯。','以前那面牆我還滿喜歡的。','……你要不要吃飯。']]},
 {k:'kext',when:()=>projOn('kext'),lines:[['廚房變大了。','嗯。','妳更忙了。','你話變多了。']]},
 {k:'terrace',when:()=>projOn('terrace'),lines:[['外面也有位子了。','下次坐外面。','下雨我就進來。']]},
 {k:'pass',when:()=>projOn('pass'),lines:[['出菜口變寬了。','你連這個都注意。','我什麼都注意。']]},
 {k:'cooler',when:()=>projOn('cooler'),lines:[['冷藏庫。','嗯。','好，那我不問了。']]},
 {k:'jill5',when:()=>S.level>=5,lines:[['招牌上只剩一個名字了。','還缺一個嗎？','……不缺。']]},
 {k:'special',when:()=>S.menu.some(d=>DISHES[d]&&DISHES[d].special),lines:[['特製版跟一般的差在哪？','差一百塊。','那我要特製版。'],['我要特製版。','你每次都點最貴的。','我尊重主廚的研發。']]},
 {k:'special4',when:()=>S.menu.filter(d=>DISHES[d]&&DISHES[d].special).length>=4,lines:[['菜單上有四道特製版了。','嗯。','妳以前一道都不肯做。','以前沒有人一直點。']]},
 {k:'sigevo',when:()=>!!S.signature&&sigLv()>=2,lines:[['招牌菜換盤了？','嗯。','我吃得出來。','你根本還沒吃。','我看得出來。']]},
 {k:'gear',when:()=>CATGEAR.some(G=>gearOn(G.k)&&S.day-(S.gear[G.k]||0)<=3&&(S.gearUse[G.k]&&Object.keys(S.gearUse[G.k]).length)),lines:[['牠已經在上面了。','牠比你快。','牠比誰都快。']]},
 {k:'menu',when:()=>S.dylan.stage>=2&&!(S.dylan.clues.knows),clue:'knows',lines:[['菜單我自己拿了。','你知道放哪？','我……猜的。']]},
 {k:'water',when:()=>S.dylan.stage>=2&&(S.dylan.clues.knows||0)>=1&&!(S.dylan.clues.knows2),clue:'knows2',lines:[['水我自己倒了。','杯子呢？','左邊第二個櫃子。','……嗯。']]},
 {k:'wang',when:()=>S.dylan.stage>=1&&(S.regulars.wang||0)>=3&&R.groups.some(q=>q.reg==='wang'&&q.table!=null),note:true,lines:[['王太太：「那位先生每天都來耶。」','嗯。','王太太：「妳不覺得他……」','他吃完就會走了。']]},
];
function dylanScene(g){const seen=S.dylan.seen=S.dylan.seen||{};for(const sc of DYLAN_SCENES){if(seen[sc.k])continue;let ok=false;try{ok=sc.when()}catch(e){ok=false}if(!ok)continue;seen[sc.k]=S.day;if(sc.clue)S.dylan.clues[sc.clue]=(S.dylan.clues[sc.clue]||0)+1;
 const L=pick(sc.lines);const say=(i,txt)=>setTimeout(()=>{if(!R||phase!=='service')return;if(sc.note&&txt.startsWith('王太太：'))noteLine(txt);else if(i%2===0){if(R.groups.includes(g))quote(g,txt)}else jillSay(txt)},600+i*1500);
 L.forEach((txt,i)=>{if(txt)say(i,txt)});logLine('dylan',L.filter(Boolean).join(' / '),'reg');return true}return false}
function dylanAct(g){const st=S.dylan.stage;const pool=st>=3?DYLAN_ACT.after:DYLAN_ACT.before;const line=pick(pool).map(x=>x&&x.replace('{T}',g.table+1));quote(g,line[0]);
 if(line[1])setTimeout(()=>{if(R&&phase==='service')jillSay(line[1])},1500);else setTimeout(()=>{if(R&&phase==='service')noteLine('Jill 看了他一眼，沒有回答。')},1500);
 if(line[2])setTimeout(()=>{if(R&&phase==='service')quote(g,line[2])},3100)}
function dylanGuestUpd(g,dt){const t=R.tables[g.table];const J=R.jill;g.glT=(g.glT??rand(5,12))-dt;
 const jillLooking=Math.hypot(J.x-t.x,J.y-t.y)<80&&((J.face>0)===(t.x>=J.x));
 if(g.gaze>R.t&&jillLooking)g.gaze=0;
 if(g.glT<=0){g.glT=rand(8,20);if(!jillLooking&&Math.random()<.75){g.gaze=R.t+rand(1.2,2.8);S.dylan.clues.look=(S.dylan.clues.look||0)+1}}
 if(!g.said&&['wait','eat'].includes(g.state)&&g.ticket&&R.t-g.ticket.t0>8&&!J.cur&&!J.q.length&&!J.moving&&Math.random()<dt*.08){g.said=1;if(dylanScene(g))return;if(Math.random()<(S.dylan.stage>=3?.4:.5))dylanAct(g);else quote(g,dylanLine())}}
function dylanWalk(D,x,y,after){D.tx=x;D.ty=y;D.after=after;D.walking=true;D.seated=false;D.via=null;if(D.y<148&&y>=148)D.via={x:D.x,y:152};else if(y<148&&D.y>=148)D.via={x,y:152}}
function dylanCanSofa(){const J=LIFE.jill;if(!(J.on||(J.reserved&&J.pos)))return null;const ivs=seatIvs(null);const face=J.on?J.face:JPOS[J.pos].face;
 if(face>0&&ivFree(170,196,ivs))return 183;if(face<0&&ivFree(100,126,ivs))return 113;
 if(S.dylan.stage>=3&&J.on&&J.legs<.3){for(const x of[149,160,136])if(ivFree(x-13,x+13,ivs))return x}return null}
function dylanUpd(dt){const D=LIFE.dylan;if(!D)return;D.t-=dt;D.since+=dt;const st=S.dylan.stage;const J=LIFE.jill;
 if(D.walking){const tx=D.via?D.via.x:D.tx,ty=D.via?D.via.y:D.ty;const dx=tx-D.x,dy=ty-D.y,d=Math.hypot(dx,dy),v=80*dt;
  if(d<=v){D.x=tx;D.y=ty;if(D.via)D.via=null;else{D.walking=false;D.moving=false;dylanArrive(D)}}else{D.x+=dx/d*v;D.y+=dy/d*v;D.face=dx>=0?1:-1;D.step+=dt*11;D.moving=true}return}
 switch(D.state){
 case'linger':{if(!R||R.closing!=null){D.state='think';D.t=rand(.4,1.5);D.since=0;break}
  const t=R&&R.tables[D.table];if(t&&t.group){/* his table is needed again: he gives it up and waits by the door */D.seated=false;dylanWalk(D,rand(66,84),rand(156,186),'stand');break}
  if(D.t<=0){D.t=rand(4,9);if(st>=1&&!D.tidied&&t&&t.dirty&&!t.group&&!jillTargets(t.i)&&Math.random()<.45){D.tidied=true;dylanWalk(D,t.x,t.y+26,'bus')}}break}
 case'think':if(D.t<=0)dylanDecide(D);break;
 case'sitDown':{D.sitT-=dt;if(D.sitT<=0){D.onSofa=true;D.y=SOFA.jy;D.state='sitSofa';D.t=rand(30,90);D.act=(LIFE.tv.on&&LIFE.tv.at==='use'&&Math.random()<.6)?'tv':(Math.random()<.55?'phone':'idle');D.phone=D.act==='phone';
   if(J.on&&J.legTarget>.75&&(J.face>0?D.x>J.x:D.x<J.x))J.legTarget=.75;if(Math.random()<.3){J.gazeT=1.4;J.gazeX=D.x}
   if(D.reveal){D.revealT=2.5}}break}
 case'sitSofa':{if(D.revealT!=null){D.revealT-=dt;if(D.revealT<=0){D.revealT=null;D.reveal=false;doReveal()}}
  if(st>=3&&J.on&&D.onSofa){D.talkT-=dt;if(D.talkT<=0){D.talkT=rand(45,110);if(Math.random()<.5){if(Math.random()<.25){const line=pick(DYLAN_ACT.after);say('d',D.x,SOFA.jy-52,line[0]);if(line[1])say('j',J.x,SOFA.jy-52,line[1],1.5);if(line[2])say('d',D.x,SOFA.jy-52,line[2],3.1)}else{say('d',D.x,SOFA.jy-52,pick(['今天很累了吧。','冷嗎？','明天我早點來。','貓都在。']));if(Math.random()<.55)say('j',J.x,SOFA.jy-52,pick(['嗯。','還好。','好。']),1.3)}}}}
  if(D.act==='tv'&&!(LIFE.tv.on&&LIFE.tv.at==='use'))D.act='idle';
  if(D.t<=0)dylanDecide(D);break}
 case'waitSofa':{if(J.on&&J.sinceSit>2.5){const x=dylanCanSofa();if(x!=null&&Math.abs(x-D.x)<=6){D.state='sitDown';D.sitT=.3;D.face=J.x>=D.x?1:-1;break}}if(D.t<=0||(J.on&&dylanCanSofa()==null)){D.state='think';D.t=1;D.reveal=false}break}
 case'sitTable':case'stand':case'crouch':if(D.t<=0||(st>=3&&D.state!=='crouch'&&(J.on||J.reserved)&&dylanCanSofa()!=null&&Math.random()<dt*.08))dylanDecide(D);break;
 case'pushing':break;
 case'gone':LIFE.dylan=null;break}}
function dylanArrive(D){const a=D.after;D.after=null;const J=LIFE.jill;
 if(a==='bus'){const t=R&&R.tables[D.table];if(t&&t.dirty&&!t.group){t.dirty=false;t.plates=[];t.busT=0;D.carry=true;S.dylan.clues.tidy=(S.dylan.clues.tidy||0)+1;dylanWalk(D,PASS.x+18,PASS.y-2,'pass')}else{D.state='think';D.t=1}}
 else if(a==='pass'){D.carry=false;sfx.clear();D.state='think';D.t=rand(1,3)}
 else if(a==='sitTable'){D.seated=true;D.state='sitTable';D.t=S.dylan.stage>=3?rand(14,40):rand(25,70);D.phone=Math.random()<.65}
 else if(a==='stand'){D.state='stand';D.t=rand(8,20);D.phone=Math.random()<.5}
 else if(a==='cat'){const c=D.cat;D.state='crouch';D.t=rand(6,12);D.face=c&&c.x>=D.x?1:-1;D.catCD=LIFE.t+40;
  if(c&&!c.hidden&&c.perch<0&&!c.sofa&&['rest','daze','stare'].includes(c.st)){const id=c.def.id;const p=id==='tora'?.7:id==='mikan'?.55:id==='ban'?.5:id==='mei'?.25:.1;if(Math.random()<p){releaseSpots(c);c.st='pet';c.pose='rub';c.happy=rand(2.5,4);c.quiet=1;c.face=D.x>=c.x?1:-1;c.hearts.push({x:0,y:-26,t:0});S.dylan.clues.pet=(S.dylan.clues.pet||0)+1;memo('dylancat',c.x,c.y,{a:catName(c.def),subj:[{x:D.x,y:D.y}]})}else if(c.st==='rest')c.face=D.x>=c.x?1:-1}}
 else if(a==='grabTV'){const tv=LIFE.tv;if(tv.mover||tv.at==='use'){D.state='think';D.t=1;return}tv.mover='dylan';tv.path=[{x:tv.x,y:tvUsePos().y},{x:tvUsePos().x,y:tvUsePos().y}];tv.wait=0;D.state='pushing';D.face=-1}
 else if(a==='sofa'){D.state='arrived';const x=dylanCanSofa();if(x==null||Math.abs(x-D.x)>6){D.state='think';D.t=1;return}
  if(!(J.on&&J.sinceSit>2.5)){D.state='waitSofa';D.tx=D.x;D.t=14;return} /* she is still on her way or just sat down: he waits a moment beside the sofa */
  D.state='sitDown';D.sitT=.3;D.face=J.x>=D.x?1:-1;D.seated=false}
 else if(a==='door'){D.state='gone'}
 else{D.state='think';D.t=1}}
function dylanDecide(D){const st=S.dylan.stage;const J=LIFE.jill;const tv=LIFE.tv;const W=[];const add=(k,w)=>{if(w>0)W.push([k,w])};
 const V=view();const near=CATS?CATS.filter(c=>!c.hidden&&c.perch<0&&!c.sofa&&!['jump','walk','race','dash','chase','hide2','visit','play'].includes(c.st)&&Math.hypot(c.x-D.x,c.y-D.y)<150):[];
 const sofaX=dylanCanSofa();const wantsTV=J.on&&(J.act==='wantTV'||J.act==='waitTV')&&tv.at==='park'&&!tv.mover&&tv.tried<2;
 if(st===2&&(J.on||J.reserved)&&!LIFE.revealRoll)LIFE.revealRoll=Math.random()<.75?1:-1;
 const reveal=st===2&&LIFE.revealRoll===1&&sofaX!=null&&(J.reserved||J.on)&&(!J.on||['settle','read','idle','tv','pet','wantTV','waitTV'].includes(J.act));
 add('sitTable',D.state==='sitTable'?.7:1);add('stand',.35);
 if(near.length&&D.catCD<LIFE.t)add('cat',st>=3?.6:.7);
 if(wantsTV)add('tv',1.3);
 if(reveal)add('sofa',3);
 if(st>=3&&sofaX!=null)add('sofa',D.state==='sitSofa'?2.2:(J.on&&J.sinceSit<20)||!J.on?2.6:1.6);
 add('leave',(st>=3?.12:.3)+Math.max(0,(D.since-(st>=3?200:70))/60));
 if(D.state==='sitSofa'&&st>=3&&Math.random()<.75){D.t=rand(25,80);D.act=(tv.on&&tv.at==='use'&&Math.random()<.5)?'tv':(Math.random()<.5?'phone':'idle');D.phone=D.act==='phone';return}
 const k=wpick(W,o=>o[1])[0];
 if(k==='sofa'&&D.onSofa){D.t=rand(25,80);return}
 if(D.onSofa&&k!=='sofa'){D.onSofa=false;D.y=SOFA.front+10;D.seated=false}
 switch(k){
 case'sitTable':{if(D.state==='sitTable'){D.t=rand(20,50);D.phone=Math.random()<.65;return}const tb=V.tables.slice().sort((a,b)=>Math.hypot(a.x-148,a.y-130)-Math.hypot(b.x-148,b.y-130)).find(t=>!t.group);if(!tb){D.state='think';D.t=2;return}const sp=seatPos(tb);const k2=sp[0].dx<0&&tb.x>148?0:1;const s=sp[Math.min(k2,sp.length-1)];D.table=tb.i;D.seat=Math.min(k2,sp.length-1);dylanWalk(D,tb.x+s.dx,tb.y+s.dy,'sitTable');break}
 case'stand':{const p={x:rand(66,84),y:rand(156,186)};dylanWalk(D,p.x,p.y,'stand');break}
 case'cat':{const c=near.sort((a,b)=>Math.hypot(a.x-D.x,a.y-D.y)-Math.hypot(b.x-D.x,b.y-D.y))[0];D.cat=c;dylanWalk(D,clamp(c.x+(c.x<D.x?24:-24),60,340),clamp(c.y+3,150,FB-6),'cat');break}
 case'tv':dylanWalk(D,tv.x+18,tv.y+4,'grabTV');break;
 case'sofa':{if(reveal)D.reveal=true;D.state='toSofa';dylanWalk(D,sofaX,SOFA.front+10,'sofa');break}
 case'leave':dylanWalk(D,DOOR.x,DOOR.y,'door');break;
 default:D.state='think';D.t=2}}
function doReveal(){const d=S.dylan;if(d.stage>=3)return;d.stage=3;d.reveal=S.day;ach('husband');save();const D=LIFE.dylan,J=LIFE.jill;if(D&&J){say('j',J.x,SOFA.jy-52,LIFE.tv.on?'老公，遙控器。':'老公。');say('d',D.x,SOFA.jy-52,LIFE.tv.on?'喔。':'嗯。',1.4)}memo('husband',(SOFA.x0+SOFA.x1)/2,120,{subj:[{x:LIFE.jill.x,y:SOFA.jy},{x:LIFE.dylan?LIFE.dylan.x:LIFE.jill.x,y:SOFA.jy}]})}
function say(who,x,y,txt,delay){LIFE.say.push({who,x,y,txt,t:-(delay||0),life:2.6});logLine(who==='j'?'Jill':'Dylan',txt,who==='j'?'j':'d')}
function lifeEnsureEvening(){if(!evening())return;if(LIFE.day!==S.day||!LIFE.plan)lifePlan();const L=LIFE.jill;
 if(LIFE.plan==='sofa'&&!L.on&&!L.act&&!L.walking){const pos=freeJillPos();if(!pos){lifeNoRoom();return}L.pos=pos;L.reserved=true;L.face=JPOS[pos].face;L.x=JPOS[pos].x;L.y=SOFA.front+10;L.sitT=.01}}
function lifeNoRoom(){/* the cats have the whole sofa: Jill takes her old seat at the first table instead */LIFE.plan='table';const L=LIFE.jill;L.act=null;L.reserved=false;L.pos=null;
 if(R&&R.jill){const J=R.jill,t=R.tables[0];J.troom='main';J.tx=t.x-25;J.ty=t.y+2;J.restTo=true;J.sit=false;J.sofa=null}else IDLE=null}
/* ---- per-frame ---- */
function lifeUpd(dt){if(!evening())return;LIFE.t+=dt;lifeEnsureEvening();
 const V=view();const J=V.jill;const L=LIFE.jill;
 if(LIFE.plan==='sofa')jillLife(J,L,dt);
 tvUpd(dt);dylanUpd(dt);for(const s of LIFE.say)s.t+=dt;LIFE.say=LIFE.say.filter(s=>s.t<s.life)}
/* ---- drawing ---- */
function drawSofaBody(c){const {x0,x1}=SOFA;const w=x1-x0;const y0=SOFA.back,ys=SOFA.seat,yf=SOFA.front,A=SOFA.arm;
 softShadow(c,(x0+x1)/2,yf+2,w/2+2,5,.22);
 let g=c.createLinearGradient(0,y0,0,ys);g.addColorStop(0,'#E4D5BA');g.addColorStop(1,'#CDBB9C');c.fillStyle=g;rr(c,x0+4,y0,w-8,ys-y0+6,9);c.fill();c.strokeStyle='rgba(90,70,45,.25)';c.lineWidth=.8;rr(c,x0+4.5,y0+.5,w-9,ys-y0+5,9);c.stroke();
 for(const k of[0,1]){const cw=(w-2*A)/2-4,cx=x0+A+(w-2*A)*(k?.75:.25);let cg=c.createLinearGradient(0,y0,0,ys);cg.addColorStop(0,'#F1E5CC');cg.addColorStop(1,'#DACAAA');c.fillStyle=cg;rr(c,cx-cw/2,y0+2,cw,ys-y0,7);c.fill();c.strokeStyle='rgba(90,70,45,.2)';c.lineWidth=.7;c.stroke();c.fillStyle='rgba(255,255,255,.4)';rr(c,cx-cw/2+4,y0+4.5,cw-8,3.5,1.8);c.fill();c.fillStyle='rgba(90,70,45,.1)';rr(c,cx-cw/2+2,ys-7,cw-4,4,2);c.fill()}
 /* piping on the back cushions, a throw pillow leaning in the right corner */
 c.strokeStyle='rgba(120,95,60,.22)';c.lineWidth=.6;for(const k of[0,1]){const cw=(w-2*A)/2-4,cx=x0+A+(w-2*A)*(k?.75:.25);rr(c,cx-cw/2+2.5,y0+4.5,cw-5,ys-y0-5,5);c.stroke()}
 {const px=x1-A-13,py=y0+9;c.save();c.translate(px,py);c.rotate(-.18);let pg=c.createLinearGradient(-9,0,9,0);pg.addColorStop(0,'#8FA38A');pg.addColorStop(.5,'#B7C9B0');pg.addColorStop(1,'#88997F');c.fillStyle=pg;rr(c,-9,-8,18,16,4);c.fill();c.strokeStyle='rgba(60,70,55,.35)';c.lineWidth=.7;c.stroke();c.fillStyle='rgba(255,255,255,.25)';rr(c,-6,-5.5,6,3,1.5);c.fill();c.restore()}
 c.fillStyle='#B9C7B3';c.beginPath();c.moveTo(x1-46,y0+1);c.lineTo(x1-20,y0+1);c.lineTo(x1-22,y0+16);c.lineTo(x1-44,y0+16);c.closePath();c.fill();c.strokeStyle='rgba(60,70,55,.3)';c.lineWidth=.6;for(let k=1;k<4;k++){c.beginPath();c.moveTo(x1-45,y0+1+k*4);c.lineTo(x1-21,y0+1+k*4);c.stroke()}
 let sg=c.createLinearGradient(0,ys,0,yf);sg.addColorStop(0,'#EFE2C8');sg.addColorStop(.7,'#E2D2B4');sg.addColorStop(1,'#C9B694');c.fillStyle=sg;rr(c,x0+A-2,ys-2,w-2*A+4,yf-ys+2,5);c.fill();
 c.fillStyle='rgba(90,70,45,.16)';c.fillRect(x0+A-2,ys-2,w-2*A+4,1.2);c.strokeStyle='rgba(90,70,45,.18)';c.lineWidth=.7;c.beginPath();c.moveTo((x0+x1)/2,ys);c.lineTo((x0+x1)/2,yf-3);c.stroke();
 c.fillStyle='rgba(255,255,255,.25)';rr(c,x0+A+3,ys+1,w-2*A-6,3,1.5);c.fill();
 c.fillStyle='#C4AF8C';rr(c,x0+A-2,yf-5,w-2*A+4,5,2);c.fill();
 for(const ax of[x0,x1-A]){let ag=c.createLinearGradient(ax,0,ax+A,0);ag.addColorStop(0,'#D9C8A8');ag.addColorStop(.5,'#EADCC2');ag.addColorStop(1,'#CDBB9C');c.fillStyle=ag;rr(c,ax,SOFA.armY-6,A,yf-SOFA.armY+6,6);c.fill();c.strokeStyle='rgba(90,70,45,.25)';c.lineWidth=.8;c.stroke();c.fillStyle='rgba(255,255,255,.35)';el(c,ax+A/2,SOFA.armY-4,A/2-1.5,2)}
 c.fillStyle='#6E4A2E';for(const fx of[x0+6,x1-9]){rr(c,fx,yf-1,3,4,1);c.fill()}}
function drawSofaGroup(c,now){drawSofaBody(c);const L=LIFE.jill,D=LIFE.dylan;const on=sofaCats();const tv=LIFE.tv;
 const byKind=k=>on.filter(o=>o.sofa.kind===k).sort((a,b)=>a.x-b.x);
 for(const k of byKind('back'))drawCat(c,k,now);
 if(L.on){const flip=L.face<0;const bob=L.bobT>0?Math.sin(L.bobT*6)*.8:Math.sin(now*1.6)*.35;const look=L.gazeT>0?L.gazeX:L.act==='tv'&&tv.on?tv.x:null;
  const gaze=look!=null?{x:(look>=L.x?1:-1)*(flip?-1:1),y:.35}:L.act==='read'?{x:0,y:.6}:null;
  /* her face after hours: amused when he is doing his act, warm when a cat or he has her attention, tired-but-content early in the evening, otherwise soft */
  const expr=LIFE.say.some(q=>q.who==='d'&&q.t>=0&&q.t<q.life)?'amused':(L.gazeT>0||L.act==='pet')?'smile':(LIFE.t<25&&L.sinceSit<25)?'tired':'soft';
  drawPerson(c,L.x,SOFA.jy,JILL_LOOK,{jill:true,me:true,seated:true,s:1.1,bob,mood:'happy',expr,flip,blink:Math.sin(now*1.7)>.985,hat:!!L.hat,lounge:{legs:L.legs,len:(10+L.legs*32)/(1.1*PSC)},hold:L.act==='read'||(L.act==='wantTV'&&L.last==='read')?'reader':null,flipPage:L.flip>0,gaze})}
 if(D&&D.onSofa){const flip=D.face<0;const look=D.act==='tv'&&tv.on?tv.x:(D.gazeT>0?L.x:null);drawPerson(c,D.x,SOFA.jy,DYLAN.looks[0],{seated:true,mood:'happy',flip,blink:Math.sin(now*1.3+2)>.975,lounge:{legs:0},hold:D.phone?'phone':null,gaze:look!=null?{x:(look>=D.x?1:-1)*(flip?-1:1),y:D.act==='phone'?.5:.2}:(D.act==='phone'?{x:0,y:.6}:null)})}
 for(const k of byKind('lap'))drawCat(c,k,now);for(const k of byKind('seat'))drawCat(c,k,now);for(const k of byKind('arm'))drawCat(c,k,now);
 if(L.on&&L.act==='pet'&&L.petCat&&L.petCat.sofa){const p=L.petCat;c.fillStyle=JILL_LOOK.skin;circ(c,p.x+(p.x<L.x?5:-5),p.y-9,2.6);c.fillStyle='rgba(60,34,22,.35)';c.beginPath();c.arc(p.x+(p.x<L.x?5:-5),p.y-9,2.6,0,7);c.stroke()}}
function drawTV(c,tv,now){const {x,y}=tv;const dir=tv.face;const roll=tv.at==='moving'?Math.sin(tv.step)*.6:0;
 softShadow(c,x,y+1.5,12,3.2,.24);
 c.fillStyle='#2A2A2E';for(const wx of[-9,-3,3,9])el(c,x+wx,y+.5,2.2,1.6);c.fillStyle='#3C3C42';rr(c,x-11,y-4,22,4,1.5);c.fill();c.fillStyle='rgba(255,255,255,.15)';c.fillRect(x-10,y-3.6,20,.8);
 c.fillStyle='#4A4A50';c.fillRect(x-1.4,y-24,2.8,20);c.fillStyle='#2E2E33';rr(c,x-2.5,y-26,5,3,1);c.fill();c.fillStyle='#6E6E76';rr(c,x-4,y-10,8,2.2,1);c.fill();
 c.save();c.translate(x+roll,y-36);const sx=dir?.84:1;c.transform(sx,dir*.1,0,1,0,0);
 c.fillStyle='#1E1E22';rr(c,-12,-9,24,17,2);c.fill();
 if(tv.on){const ph=now*.3;const h1=(ph*40)%360,h2=(ph*40+70)%360;let g=c.createLinearGradient(-11,-8,11,7);g.addColorStop(0,`hsl(${h1},42%,${58+Math.sin(now*3)*4}%)`);g.addColorStop(1,`hsl(${h2},38%,42%)`);c.fillStyle=g;c.fillRect(-10.6,-7.6,21.2,14.2);c.fillStyle='rgba(255,255,255,.55)';c.fillRect(-9,4,10+Math.sin(now*.9)*3,1.4);c.fillStyle='rgba(255,255,255,.18)';c.beginPath();c.moveTo(-10.6,-7.6);c.lineTo(2,-7.6);c.lineTo(-10.6,4);c.fill()}
 else{c.fillStyle='#2A2C33';c.fillRect(-10.6,-7.6,21.2,14.2);c.fillStyle='rgba(255,255,255,.08)';c.beginPath();c.moveTo(-10.6,-7.6);c.lineTo(0,-7.6);c.lineTo(-10.6,4);c.fill();c.fillStyle='#E24A5A';circ(c,9,5.5,.7)}
 c.restore();
 if(tv.on){c.save();c.globalCompositeOperation='lighter';let g=c.createRadialGradient(x+dir*22,y-14,4,x+dir*22,y-14,56);g.addColorStop(0,'rgba(150,190,255,.16)');g.addColorStop(1,'rgba(150,190,255,0)');c.fillStyle=g;c.fillRect(x-64,y-72,128,92);c.restore()}}
function drawDylanFree(c,D,now){const stp=D.moving?Math.sin(D.step):0;const crouch=D.state==='crouch';
 drawPerson(c,D.x,D.y,DYLAN.looks[0],{step:stp,bob:D.moving?Math.abs(stp)*-.8:Math.sin(now*1.5)*.3,mood:'happy',flip:D.face<0,seated:crouch,s:crouch?.95:1,hold:!D.moving&&D.phone&&D.state==='stand'?'phone':null,blink:Math.sin(now*1.3+2)>.975,lounge:crouch?{legs:0}:null});
 if(D.carry){c.fillStyle='#fff';el(c,D.x+(D.face<0?-9:9),D.y-34,6.5,4.2);el(c,D.x+(D.face<0?-9:9),D.y-36.5,6.5,4.2)}}
function drawSay(c){for(const s of LIFE.say){if(s.t<0)continue;const a=s.t<.2?s.t/.2:s.t>s.life-.4?(s.life-s.t)/.4:1;c.globalAlpha=Math.max(0,a);c.font=`700 6.5px ${FONT}`;const w=c.measureText(s.txt).width+10;c.fillStyle='#FFFDF7';rr(c,s.x-w/2,s.y-8,w,12,6);c.fill();c.beginPath();c.moveTo(s.x-2.5,s.y+4);c.lineTo(s.x+2.5,s.y+4);c.lineTo(s.x,s.y+7.5);c.fill();c.fillStyle='#2E2019';c.textAlign='center';c.textBaseline='middle';c.fillText(s.txt,s.x,s.y-1.6);c.textBaseline='alphabetic';c.globalAlpha=1}}

/* ================= crew ================= */
const ROLES={
 chef:{n:'廚師',hire:1500,wage:240,up:1200,d:'負責一個工作站。LV1 只做簡單的菜，升級後能處理更多料理；LV3 起也會接手 Jill 做到一半的菜；LV5 連 Jill 的招牌菜都學會了。每道新菜的第一份，永遠由 Jill 親自做。',duties:['stove','oven','prep','bar']},
 waiter:{n:'服務生',hire:1200,wage:200,up:1000,d:'帶位、點餐、收桌；LV2 起會把做好的菜端給客人，LV3 起連結帳都包了。職責可以自己配：今天只收桌，或全部都做。等級越高動作越快。',duties:['both','seat','order']},
 cleaner:{n:'清潔員',hire:900,wage:150,up:800,d:'專職收桌，比服務生收得快，薪水也比較便宜。忙的時候幫服務生分擔最後那一趟。',duties:['clean']},
};
const DUTY_N={stove:'爐台',oven:'烤箱',prep:'冷盤台',bar:'咖啡吧',both:'帶位＋點餐',seat:'只帶位',order:'只點餐',clean:'收桌'};
const CREW_NAMES={chef:['阿德師傅','Marco','小林師傅','阿珠姐','Hugo'],waiter:['小茉','Kai','Nina','阿哲','Momo'],cleaner:['秀琴阿姨','小彤','阿明','Yuki']};
function crewCount(m,k){if(!R)return;R.st.crew=R.st.crew||{};const c=R.st.crew[m.id]=R.st.crew[m.id]||{};c[k]=(c[k]||0)+1}
function crewCap(){return[1,2,3,4,6][S.level-1]+(opsLv('room')?2:0)+(projOn('side')?2:0)+(projOn('kext')?2:0)}
/* a senior employee costs more than a new one by a good margin: LV5 ≈ 2.8× LV1 (chef 240→672, waiter 200→560, cleaner 150→420) */
function crewWage(m){return Math.round(ROLES[m.role].wage*(1+.45*(m.lv-1)))}
function crewWages(){return(S.crew||[]).reduce((a,m)=>a+crewWage(m),0)}
function chefFor(type){let b=null;for(const m of S.crew||[])if(m.role==='chef'&&m.duty===type&&(!b||m.lv>b.lv))b=m;return b}
/* What a chef is trusted with: LV1 simple dishes, LV2 ordinary ones, LV3+ everything up to the hardest recipes and
   dishes Jill started herself. The signature dish and a recipe's very first plate always stay with Jill. */
/* What a chef can cook: dishes up to their level's difficulty (LV3 handles everything ordinary), and only
   dishes Jill has made at least once. The Signature is Jill's own until a chef reaches LV5 — then she has
   taught it. (Jill still makes the first portion of every new dish herself.) */
function chefCan(m,d){const D=DISH(d);if(!D)return false;if(D.sig||d==='signature')return m.lv>=5&&(S.xp.signature||0)>0;if((S.xp[d]||0)<=0)return false;return D.diff<=Math.min(3,m.lv)}
function chefLock(m,d){const D=DISH(d);if(!D)return'';if(D.sig||d==='signature')return m.lv>=5?((S.xp.signature||0)>0?'':'Jill 先做過一次'):'LV5 進階訓練';if((S.xp[d]||0)<=0)return'Jill 先做過一次';return D.diff>Math.min(3,m.lv)?`LV${D.diff}`:''}
function chefHandles(s){const j=s.job;if(!j)return null;if(j.chef){/* 2.0: the cook who started it keeps it — a second cook of the same duty is a real second pair of hands */const own=(S.crew||[]).find(m=>m.id===j.chef&&m.role==='chef');if(own)return own}const ch=chefFor(s.type);if(!ch)return null;return ch.lv>=3&&chefCan(ch,j.d)?ch:null}
function chefDelay(m){return Math.max(.45,1.5-.22*(m.lv-1))}
function chefScore(m){return[.8,.86,.9,.95,1][m.lv-1]}
function waiterDelay(m){return Math.max(.3,2.2-.4*(m.lv-1))*(projOn('pass')?.85:1)}
function cleanDur(m){return Math.max(.3,1.3-.22*(m.lv-1))}
function crewStat(m){return m.role==='chef'?`每步 ${chefDelay(m).toFixed(1)} 秒・品質 ${Math.round(chefScore(m)*100)}`:m.role==='waiter'?`反應 ${waiterDelay(m).toFixed(1)} 秒`:`收桌 ${cleanDur(m).toFixed(1)} 秒`}
/* hash() is unsigned 32-bit: shift with >>> — a signed >> turns half of all ids negative, HAIR[-2] is undefined and the first draw of that employee throws (and with it the whole frame loop) */
function crewLook(m){const h=hash(m.id);const L={skin:SKIN[h%SKIN.length],hair:HAIR[(h>>>3)%HAIR.length],hs:[0,1,2,3,4,6,7][(h>>>6)%7],top:m.role==='waiter'?'#3F6B55':m.role==='cleaner'?'#8FA3B5':'#FFFFFF',acc:m.role==='waiter'?'tie':null,pants:'#2E2B33'};if(m.role==='chef'){L.chef=true;L.kerchief=['#B8536A','#2E6B4A','#3A5A8A','#C99A45','#6B3A5A'][(h>>>9)%5]}else L.apron=m.role==='waiter'?'#2A2220':'#5E6E7A';return L}
function chefAuto(s,dt){const j=s.job,k=j.step;const ch=chefHandles(s);if(!ch||k.t==='wait'||k.t==='work')return false;const sp=dishSpeed(j.d,s.type);
 if(k.t==='zone'){const tgt=k.z.c-k.z.w*.35+(ch.lv<3?(hash(j.seed+''+j.si)%100/100-.5)*.08:0);if(k.p>=tgt){j.overStart=null;actZone(s)}else{k.p+=dt*sp/k.time;if(k.p>=1.5)charcoal(s)}return true}
 if(!cookPresent(s))return true;k.auto+=dt;if(k.auto<chefDelay(ch))return true;
 switch(k.t){case'add':k.left.forEach(i=>j.adds.push(i));k.left=[];s.pop={id:k.items[k.items.length-1],t:0};break;case'hold':k.level=(k.a+k.b)/2;applyHold(j,k);break;case'dose':for(let i=0;i<k.min;i++)j.adds.push(k.ing);k.cnt=k.min;break;case'tap':if(k.heat)j.mix=1;else{j.cut=true;if(CUTADD[j.d])j.adds.push(CUTADD[j.d])}break}
 j.overStart=null;advance(s,chefScore(ch));return true}
function crewUpd(dt){R.cw=R.cw||{};for(const m of S.crew||[]){
 if(m.role==='chef'){const peers=(S.crew||[]).filter(q=>q.role==='chef'&&q.duty===m.duty).length;const share=Math.ceil(R.slots.filter(q=>q.type===m.duty).length/Math.max(1,peers));for(const s of R.slots)if(s.type===m.duty&&!s.job&&!s.broken){if(R.slots.filter(q=>q.job&&q.job.chef===m.id).length>=share)break;let n=null;for(const tk of R.tickets){for(const it of tk.items)if(it.st==='pending'&&DISH(it.d).st===s.type&&chefCan(m,it.d)){n={tk,it};break}if(n)break}if(n&&startCook(n.tk,n.it,true)&&s.job){s.job.chef=m.id;crewCount(m,'cook');if(n.it.d==='signature'&&!S.taught){S.taught=S.day;jillSay('這道也交給你了。');setTimeout(()=>{if(R&&phase==='service')staffSay(m,'交給我。')},1400);ach('taught')}}}continue}
 let w=R.cw[m.id];if(!w)w=R.cw[m.id]={x:m.role==='waiter'?84:362,y:m.role==='waiter'?150:190,task:null,cd:1,face:1,step:0,busy:0,room:'main',troom:'main'};if(!w.room)w.room='main';
 if(w.task){const tk=w.task;let ok=true;
  if(tk.k==='seat')ok=R.groups.includes(tk.g)&&tk.g.state==='queue'&&!tk.t.group&&!tk.t.dirty;
  if(tk.k==='order')ok=tk.t.group===tk.g&&tk.g.state==='order';
  if(tk.k==='clean')ok=tk.t.dirty&&!tk.t.group;
  if(tk.k==='serve')ok=R.tickets.includes(tk.tk)&&tk.g.state==='wait'&&tk.t.group===tk.g&&(tk.phase==='table'||tk.tk.items.some(i=>i.st==='ready'&&!i.picked));
  if(tk.k==='check')ok=tk.t.group===tk.g&&tk.g.state==='check'&&!jillTargets(tk.t.i);
  if(!ok){if(tk.g)tk.g.claim=null;if(tk.t)tk.t.claim=null;if(tk.tk)tk.tk.claim=null;if(w.carry){for(const c0 of w.carry)c0.picked=false;w.carry=null}w.task=null;w.cd=.3;continue}
  const v=(115+15*m.lv)*flowMul('crew')*dt;w.tx=tk.x;w.ty=tk.y;w.troom=tk.room||(tk.t?tk.t.room:'main')||'main';
  if(!stepTo(w,v)){w.step+=dt*12;w.moving=true}
  else{w.moving=false;w.busy+=dt;if(w.busy>=tk.dur){
   if(tk.k==='seat'){seatGroup(tk.g,tk.t);if(Math.random()<.08&&canChat('waiter',60,5))staffSay(m,pick(['這邊請。','兩位這邊。','請坐。']))}
   if(tk.k==='order'&&!jillTargets(tk.t.i))createTicket(tk.g);else if(tk.k==='order'&&tk.g.state==='order')createTicket(tk.g);
   if(tk.k==='clean'){tk.t.dirty=false;tk.t.plates=[];tk.t.busT=0;sfx.clear()}
   if(tk.k==='serve'&&tk.phase==='pickup'){w.carry=tk.tk.items.filter(i=>i.st==='ready'&&!i.picked);for(const i of w.carry)i.picked=true;tk.phase='table';tk.room=tk.t.room||'main';tk.x=tk.t.x+(tk.t.x<200?-26:26);tk.y=tk.t.y+22;w.busy=0;R.tv++;continue}
   if(tk.k==='serve'){serveItems(tk.g,w.carry.map(it=>({it})));w.carry=null;tk.tk.claim=null;if(Math.random()<.08&&canChat('waiter',60,5))staffSay(m,pick(['久等了。','請慢用。','小心燙。']))}
   if(tk.k==='check'&&tk.g.state==='check'){regularNote(tk.g);collect(tk.g)}
   crewCount(m,tk.k);if(tk.g)tk.g.claim=null;if(tk.t)tk.t.claim=null;w.task=null;w.busy=0;w.cd=m.role==='waiter'?waiterDelay(m):.35}}
  continue}
 w.cd-=dt;if(w.cd>0){w.moving=false;continue}
 if(m.role==='waiter'){
  if(waiterDoes(m,'seat')){const g=queued().find(g=>g.state==='queue'&&!g.claim&&freeTableFor(g)&&!freeTableFor(g).claim);if(g){const t=freeTableFor(g);g.claim=m.id;t.claim=m.id;w.task={k:'seat',g,t,x:g.x+22,y:g.y+2,dur:.25,room:'main'};continue}}
  if(waiterDoes(m,'order')){const t=R.tables.find(t=>t.group&&t.group.state==='order'&&!t.claim&&!jillTargets(t.i));if(t){t.claim=m.id;w.task={k:'order',g:t.group,t,x:t.x+(t.x<200?-26:26),y:t.y+22,dur:.5};continue}}
  if(waiterDoes(m,'serve')){const tk=R.tickets.find(t=>t.g.table!=null&&t.g.state==='wait'&&!t.claim&&t.items.some(i=>i.st==='ready'&&!i.picked)&&!jillTargets(t.g.table)&&!R.jill.carry.some(c0=>c0.tk===t));if(tk){tk.claim=m.id;w.task={k:'serve',tk,g:tk.g,t:R.tables[tk.g.table],x:PASS.x+(tk.g.table%2?14:-14),y:PASS.y,dur:.25,phase:'pickup',room:'main'};continue}}
  if(waiterDoes(m,'check')){const t=R.tables.find(t=>t.group&&t.group.state==='check'&&!t.claim&&!jillTargets(t.i));if(t){t.claim=m.id;w.task={k:'check',g:t.group,t,x:t.x+(t.x<200?-26:26),y:t.y+22,dur:.6};continue}}
  if(waiterDoes(m,'clean')){const t=R.tables.find(t=>t.dirty&&!t.group&&!t.claim&&!jillTargets(t.i));if(t){t.claim=m.id;w.task={k:'clean',t,x:t.x+(t.x<200?-24:24),y:t.y+22,dur:cleanDur(m)+.4};continue}}
  w.cd=.4;if(w.room!=='main'||Math.hypot(w.x-84,w.y-150)>4){w.tx=84;w.ty=150;w.troom='main';if(!stepTo(w,80*dt)){w.moving=true;w.step+=dt*12}}}
 else{const t=R.tables.find(t=>t.dirty&&!t.group&&!t.claim&&!jillTargets(t.i));if(t){t.claim=m.id;w.task={k:'clean',t,x:t.x+(t.x<200?-24:24),y:t.y+22,dur:cleanDur(m)};continue}w.cd=.4}}}
function crewDraw(c,now,list,rm){
 if(R&&R.cw)for(const m of S.crew||[]){if(m.role==='chef')continue;const w=R.cw[m.id];if(!w||(w.room||'main')!==(rm||'main'))continue;list.push({y:w.y,f:()=>{const stp=w.moving?Math.sin(w.step):0;drawPerson(c,w.x,w.y,crewLook(m),{step:stp,bob:w.moving?Math.abs(stp)*-.8:0,mood:'happy',flip:w.face<0,carry:!!(w.carry&&w.carry.length),arms:m.role==='cleaner'&&w.task&&w.task.k==='clean'&&!w.moving?[.3,1.0]:null});
  if(w.carry)w.carry.slice(0,3).forEach((it,i)=>{const cv=dishCanvas(it.d,it.q,64,S.decor.ware>0,it.want);c.drawImage(cv,w.x+(i%2?5:-21),w.y-50-Math.floor(i/2)*8,16,16)});
  const hx=w.x+(w.face<0?-12:12);if(m.role==='cleaner'){c.strokeStyle='#8A6A3A';c.lineWidth=1.6;c.beginPath();c.moveTo(hx,w.y-30);c.lineTo(hx+(w.face<0?-4:4),w.y-2);c.stroke();c.fillStyle='#C9A86A';el(c,hx+(w.face<0?-4:4),w.y-1,5,2.4)}else{c.fillStyle='#C9CED0';el(c,hx,w.y-26,7,2)}
  nameTag(c,w.x,w.y-64,m.name)}})}}
function nameTag(c,x,y,n){c.font=`800 6.5px ${FONT}`;const w=c.measureText(n).width+8;c.fillStyle='rgba(42,42,42,.72)';rr(c,x-w/2,y-6,w,10,4);c.fill();c.fillStyle='#FFF8EC';c.textAlign='center';c.textBaseline='middle';c.fillText(n,x,y-1);c.textBaseline='alphabetic'}
/* ================= incidents ================= */
const INC_BAD=['rowdy','broken','thief','inspector'],INC_GOOD=['lucky','delivery','quiet','musician','selfie','power','rainstart','viprush','wave'];
function planIncidents(dur){const D=S.day;if(D<3)return[];const n=D<6?1:D<12?2:3;const pool=[];let bad=0;const cand=shuffle(INC_BAD.concat(INC_GOOD,INC_GOOD));
 for(const k of cand){if(pool.length>=n)break;if(pool.includes(k))continue;const isBad=INC_BAD.includes(k);if(isBad&&bad>=(D<8?1:2))continue;if(k==='rainstart'&&!(S.today.weather==='sun'||S.today.weather==='cloud'))continue;if(isBad)bad++;pool.push(k)}
 return pool.map((k,i)=>({k,t:dur*(.2+.62*(i+Math.random()*.7)/n),tries:0}))}
function fireIncident(k){switch(k){
 case'rowdy':{const cand=R.groups.filter(g=>['order','wait','eat'].includes(g.state)&&g.type!=='vip'&&!g.reg&&g.table!=null);if(!cand.length)return false;const g=pick(cand);g.rowdy=R.t+16;banner('奧客鬧事！',`T${g.table+1} 的客人在大吵大鬧`,'fire');toast('點那張桌子，讓 Jill 過去安撫');sfx.angry();return true}
 case'broken':{const cand=R.slots.filter(s=>!s.job&&!s.broken&&s.type!=='prep');if(!cand.length)return false;const s=pick(cand);s.broken=true;s.fix=0;banner('設備故障！',`${ST_N[s.type]}${s.no} 冒煙了`,'fire');toast('連點那台設備把它修好');sfx.burnt();return true}
 case'thief':{const ds=menuList().filter(d=>(S.stock[d]||0)>=2).sort((a,b)=>S.stock[b]-S.stock[a]);if(!ds.length)return false;const d=ds[0];const n=Math.min(4,S.stock[d]);S.stock[d]-=n;R.thief={x:130,y:FB-12,d,n,caught:false,look:{skin:'#E2AE88',hair:'#1E1E24',hs:0,top:'#2A2A30',acc:'shades',pants:'#1B1B20'}};banner('食材被偷了！','快點那個小偷！','fire');sfx.angry();
  const cat=CATS&&CATS.find(c=>c.perch<0&&!c.hidden&&!['jump','visit'].includes(c.st));if(cat){releaseSpots(cat);cat.guest=null;cat.run=1;catWalk(cat,R.thief.x,R.thief.y,'rest');R.chaser=cat}return true}
 case'inspector':{R.insp={t:0,dur:22,x:DOOR.x,y:DOOR.y+20,tx:224,ty:204,b0:R.st.q.B,out:false};banner('衛生檢查員突襲！','22 秒內把髒桌子收乾淨、別燒焦','fire');sfx.door();return true}
 case'viprush':{for(let i=0;i<3;i++)R.sched.splice(R.si,0,{t:R.t+i*2.5,type:i===1?'gourmet':'vip',size:2});R.sched.sort((a,b)=>a.t-b.t);banner('饕客尖峰時刻！','一群 VIP 饕客湧進來了','fire');return true}
 case'wave':{for(let i=0;i<3;i++)R.sched.splice(R.si,0,Object.assign({t:R.t+i*3},rollGuest()));R.sched.sort((a,b)=>a.t-b.t);noteLine('外面一下子來了一群人');return true}
 case'lucky':{const cand=R.groups.filter(g=>g.table!=null&&['eat','check'].includes(g.state)&&!g.reg);if(!cand.length)return false;const g=pick(cand);const t=R.tables[g.table];const tip=Math.round(80+Math.random()*120);S.money+=tip;S.lifetime+=tip;R.st.tips+=tip;quote(g,pick(['不用找了。','這個給你們，辛苦了。','多的當小費。']));addFloat(t.x,t.y-58,'小費 +'+fmt(tip),'#BFE3A8',1,t.room);sfx.cash();return true}
 case'delivery':{const ms=menuList().filter(d=>stationOk(d)&&(S.stock[d]||0)<=6);if(!ms.length||stockTotal()+2>fridgeCap())return false;const d=pick(ms);S.stock[d]=(S.stock[d]||0)+2;noteLine(`供應商多送了 2 份${dishName(d)}的料，算他們請的`);sfx.ding();R.tv++;return true}
 case'quiet':{let n=0;for(let i=R.si;i<R.sched.length;i++){const o=R.sched[i];if(o.t<R.t+35){o.t+=35;n++}}if(!n&&R.groups.length>2)return false;noteLine('店裡突然安靜下來了');return true}
 case'musician':{R.musicT=R.t+45;noteLine('門口有人在唱歌，等位的客人不那麼急了');const q=queued();if(q.length)quote(q[0],pick(['外面有人在唱歌。','這首我會。']));return true}
 case'selfie':{const cand=R.groups.filter(g=>g.table!=null&&g.state==='eat'&&g.pat>.6&&!g.reg);const J=R.jill;if(!cand.length||J.visit||J.rest||J.cur||J.q.length||jillWorkload()>1)return false;const g=pick(cand);const t=R.tables[g.table];quote(g,pick(['可以跟妳合照嗎？','老闆娘，一起拍一張？']));J.visit={g,t0:t,phase:'go',kind:'selfie'};J.troom=t.room||'main';J.tx=t.x+(t.x<200?30:-30);J.ty=t.y+20;J.idle=0;return true}
 case'power':{R.blackout=2.6;noteLine('跳電了一下');sfx.burnt();if(CATS)for(const c of CATS){if(c.hidden||c.sofa||c.perch>=0||['jump','walk','race','dash','chase','hide2','bed','sleep'].includes(c.st))continue;releaseSpots(c);c.st='daze';c.pose='daze';c.t=rand(2,4);c.moving=false}return true}
 case'rainstart':{if(R.weather!=='sun'&&R.weather!=='cloud')return false;R.weather='rain';S.today.weather='rain';S.wxPrev='rain';noteLine('外面突然下起雨了');const g=R.groups.find(g=>g.table!=null&&['reading','wait','eat'].includes(g.state));if(g)quote(g,pick(['下雨了。','還好進來了。','雨來得真快。']));bg=null;return true}}return false}
function incUpd(dt){for(const e of R.inc||[]){if(!e.done&&R.t>=e.t&&!R.closed){if(fireIncident(e.k))e.done=true;else if(++e.tries>2)e.done=true;else e.t=R.t+8}}
 for(const g of R.groups){if(g.rowdy&&R.t>g.rowdy){g.rowdy=0;quote(g,'什麼爛店，我不吃了！');R.st.angry++;addReview(g,1,'隔壁桌鬧事鬧超久，店家都不管。');const t=R.tables[g.table];const served=g.ticket&&g.ticket.items.some(i=>i.st==='served');leaveGroup(g,'angry');if(t&&served)t.dirty=true;sfx.angry()}}
 const th=R.thief;if(th){const tx=DOOR.x,ty=DOOR.y+6,dx=tx-th.x,dy=ty-th.y,d=Math.hypot(dx,dy),v=(th.caught?95:38)*dt;th.step=(th.step||0)+dt*14;if(d>v){th.x+=dx/d*v;th.y+=dy/d*v;th.face=dx>=0?1:-1}else{if(!th.caught)toast(`小偷帶著 ${DISH(th.d).n}×${th.n} 跑掉了…`);R.thief=null}
  if(R.chaser&&R.chaser.st==='walk'&&R.thief){R.chaser.tx=clamp(th.x-10,80,372);R.chaser.ty=clamp(th.y+4,120,FB-12)}}
 const I=R.insp;if(I){const dx=I.tx-I.x,dy=I.ty-I.y,d=Math.hypot(dx,dy),v=60*dt;if(d>v){I.x+=dx/d*v;I.y+=dy/d*v;I.moving=true;I.step=(I.step||0)+dt*12;I.face=dx>=0?1:-1}else{I.moving=false;if(I.out){R.insp=null;return}}
  if(!I.out&&!I.moving){I.t+=dt;if(I.t>=I.dur){const dirty=R.tables.some(t=>t.dirty);const burnt=R.st.q.B>I.b0;if(!dirty&&!burnt){ach('inspect');S.money+=300;S.reviews.push({s:5,txt:'衛生檢查：桌面乾淨、出餐穩定，滿分通過。',name:'衛生檢查員',day:S.day,w:2});R.st.reviews.push(S.reviews[S.reviews.length-1]);banner('檢查通過！','衛生獎勵 +$300');sfx.perfect()}else{S.money-=300;S.reviews.push({s:2,txt:dirty?'衛生檢查：桌上還堆著髒盤子，需要改進。':'衛生檢查：廚房有燒焦味，需要改進。',name:'衛生檢查員',day:S.day,w:2});banner('檢查沒過…','罰款 -$300','fire');sfx.angry()}I.out=true;I.tx=DOOR.x;I.ty=DOOR.y}}}}
function tapThief(p){const th=R&&R.thief;if(!th||th.caught)return false;if(Math.hypot(p.x-th.x,p.y-(th.y-22))>26)return false;th.caught=true;ach('caught');S.stock[th.d]=(S.stock[th.d]||0)+th.n;toast(`抓到了！搶回 ${DISH(th.d).n}×${th.n}`);addFloat(th.x,th.y-50,'抓到了！','#FFE38A',1);sfx.perfect();R.tv++;if(R.chaser){R.chaser.happy=2;R.chaser.hearts.push({x:0,y:-26,t:0})}return true}
function incDraw(c,now,list){const th=R&&R.thief;if(th)list.push({y:th.y,f:()=>{const stp=Math.sin(th.step||0);drawPerson(c,th.x,th.y,th.look,{step:stp,bob:Math.abs(stp)*-1,mood:th.caught?'sad':'ok',flip:(th.face||-1)<0});if(!th.caught){c.fillStyle='#8A6A42';el(c,th.x+10,th.y-30,8,9);c.fillStyle='#6E5230';c.fillRect(th.x+7,th.y-40,6,3);c.drawImage(dishCanvas(th.d,'G',64,false),th.x-2,th.y-86,24,24);c.fillStyle='#E0543A';c.font=`800 8px ${FONT}`;c.textAlign='center';c.fillText('點我！',th.x+10,th.y-90)}}});
 const I=R&&R.insp;if(I)list.push({y:I.y,f:()=>{const stp=I.moving?Math.sin(I.step):0;drawPerson(c,I.x,I.y,{skin:'#F0C8A8',hair:'#4A4A4A',hs:0,top:'#3A4A5A',acc:'glasses',pants:'#2A2A30'},{step:stp,mood:'ok',flip:(I.face||1)<0});c.fillStyle='#8A6A42';rr(c,I.x+8,I.y-30,8,10,1);c.fill();c.fillStyle='#fff';c.fillRect(I.x+9,I.y-28,6,7);
  if(!I.out){const f=1-I.t/I.dur;c.lineWidth=3;c.strokeStyle='rgba(0,0,0,.25)';c.beginPath();c.arc(I.x,I.y-72,9,0,7);c.stroke();c.strokeStyle=f>.3?'#E6B04A':'#E0543A';c.beginPath();c.arc(I.x,I.y-72,9,-Math.PI/2,-Math.PI/2+f*6.283);c.stroke();c.fillStyle='#2E2019';c.font=`800 7px ${FONT}`;c.textAlign='center';c.textBaseline='middle';c.fillText(Math.ceil(I.dur-I.t),I.x,I.y-71.5);c.textBaseline='alphabetic';const dirty=R.tables.filter(t=>t.dirty).length;if(dirty)nameTag(c,I.x,I.y-88,`髒桌 ${dirty}`)}}})}
/* ================= emergency stock ================= */
function takeStock(it){if((S.stock[it.d]||0)>0){S.stock[it.d]--;return}it.st='order';it.ordT=R.t+5;const c=Math.round(costOf(it.d)*1.5);S.money-=c;S.todayCost+=c;R.st.short=R.st.short||{};R.st.short[it.d]=(R.st.short[it.d]||0)+1}
function stockArrive(){let n=0;for(const tk of R.tickets)for(const it of tk.items)if(it.st==='order'&&R.t>=it.ordT){it.st='pending';n++}if(n){R.tv++;toast('叫的食材送到了！可以開始做了');sfx.ding()}}
function closeShop(msg){if(!R||R.closed)return;R.closed=true;toast(msg);for(const g of R.groups)if(g.state==='arrive'||g.state==='queue'){g.state='leave';sendOut(g)}}
/* ================= stars & lab ================= */
function starOf(d){return(S.rstar&&S.rstar[d])||1}
function starUpCost(d){const D=DISH(d);return Math.round(D.price*(starOf(d)===1?8:16)/50)*50}
const KEY_OVR={veg:['vegmix','oil']};
function dishKeys(d){if(KEY_OVR[d])return KEY_OVR[d];const out=[];for(const st of DISHES[d].steps){const arr=st.t==='add'?st.items:(st.t==='hold'||st.t==='dose')?[st.ing]:[];for(const i of arr)if(!out.includes(i)&&!i.startsWith('s_'))out.push(i)}return out.slice(0,3)}
/* the pantry grows with the restaurant: ingredients of dishes up to one level above the current one */
function pantry(){const set=new Set(['egg','rice','milk','beans','cheese','tomato']);for(const d in DISHES)if(DISHES[d].rd>0&&DISHES[d].lv<=S.level+1)dishKeys(d).forEach(i=>set.add(i));return Object.keys(ING).filter(i=>set.has(i))}
let labSel=[];
/* Every pantry ingredient wears its profile on the card: what role it plays (主體/配料/調味/醬汁/飲品/甜點),
   how it tastes (清爽・濃郁・香氣・口感, 0-3), which world it belongs to (savory / drink / sweet) and a cost tier.
   Everything the player needs to reason about a combination is visible before paying for a trial. */
const LABI={
 egg:{d:'base',t:[1,1,0,1],w:'s',c:1},rice:{d:'base',t:[1,0,0,2],w:'s',c:1},noodle:{d:'base',t:[1,0,0,2],w:'s',c:1},tomato:{d:'sauce',t:[2,1,1,0],w:'s',c:1},garlic:{d:'season',t:[0,1,3,0],w:'s',c:1},shrimp:{d:'side',t:[2,0,1,2],w:'s',c:2},
 patty:{d:'base',t:[0,3,1,2],w:'s',c:2},bun:{d:'side',t:[0,1,0,2],w:'s',c:1},cheese:{d:'side',t:[0,3,1,1],w:'s',c:1},potato:{d:'base',t:[0,1,0,3],w:'s',c:1},salt:{d:'season',t:[0,0,2,0],w:'s',c:1},oil:{d:'season',t:[0,1,2,0],w:'s',c:1},
 pumpkin:{d:'base',t:[1,2,0,1],w:'s',c:1},stock:{d:'sauce',t:[0,2,2,0],w:'s',c:1},cream:{d:'sauce',t:[0,3,0,1],w:'s',c:1},vegmix:{d:'base',t:[2,0,1,2],w:'s',c:1},herbs:{d:'season',t:[1,0,3,0],w:'s',c:1},butter:{d:'sauce',t:[0,3,1,0],w:'s',c:1},
 duck:{d:'base',t:[0,3,1,2],w:'s',c:3},orange:{d:'sauce',t:[2,0,2,0],w:'s',c:2},chicken:{d:'base',t:[0,2,1,2],w:'s',c:2},steak:{d:'base',t:[0,3,1,3],w:'s',c:3},salmon:{d:'base',t:[1,2,1,2],w:'s',c:3},asparagus:{d:'side',t:[2,0,1,2],w:'s',c:2},
 arborio:{d:'base',t:[0,1,0,3],w:'s',c:2},wine:{d:'sauce',t:[1,1,3,0],w:'s',c:2},prosciutto:{d:'base',t:[0,2,2,1],w:'s',c:3},fig:{d:'side',t:[1,1,2,1],w:'s',c:2},balsamic:{d:'sauce',t:[2,0,2,0],w:'s',c:2},
 beans:{d:'drink',t:[0,2,3,0],w:'d',c:1},milk:{d:'mix',t:[1,1,0,1],w:'d',c:1},tea:{d:'drink',t:[2,0,2,0],w:'d',c:1},lemon:{d:'mix',t:[3,0,2,0],w:'d',c:1},ice:{d:'mix',t:[3,0,0,1],w:'d',c:1},soda:{d:'drink',t:[3,0,0,2],w:'d',c:1},fruit:{d:'mix',t:[2,0,2,1],w:'d',c:1},
 custard:{d:'sweet',t:[0,2,1,2],w:'w',c:1},caramel:{d:'top',t:[0,2,2,0],w:'w',c:1},ladyfinger:{d:'sweet',t:[0,1,1,2],w:'w',c:1},mascarpone:{d:'top',t:[0,3,0,2],w:'w',c:2},cocoa:{d:'top',t:[0,1,3,0],w:'w',c:1},cheesebatter:{d:'sweet',t:[0,3,1,2],w:'w',c:2},berries:{d:'top',t:[2,0,2,1],w:'w',c:1},whites:{d:'sweet',t:[1,0,0,3],w:'w',c:1},sugar:{d:'top',t:[0,1,1,0],w:'w',c:1}};
const DIR_N={base:'主體',side:'配料',season:'調味',sauce:'醬汁',drink:'飲品基底',mix:'飲品配料',sweet:'甜點基底',top:'甜點配料'};
const DIR_GROUPS=[['base','主體'],['side','配料'],['season','調味與醬汁'],['sauce',null],['drink','飲品'],['mix',null],['sweet','甜點'],['top',null]];
const TASTE_N=['清爽','濃郁','香氣','口感'];
function labProfile(i){return LABI[i]||{d:'side',t:[1,1,1,1],w:'s',c:1}}
function labDishesWith(i){return Object.keys(DISHES).filter(d=>!DISHES[d].special&&dishKeys(d).includes(i))}
function labRD(){return Object.keys(DISHES).filter(d=>DISHES[d].rd>0&&!S.unlocked.includes(d))}
function tasteStr(t){return TASTE_N.map((n,k)=>t[k]>0?n+'↑'.repeat(Math.min(3,t[k])):null).filter(Boolean).join(' ')||'淡'}
/* 很好 = the two are known to go together: they share a dish already on the menu, or a trial has shown it. Untried pairs are judged from the profiles only. */
function labKnownPair(a,b){return !!((S.labKnown||{})[[a,b].sort().join('|')])}
function labLearn(list){S.labKnown=S.labKnown||{};for(let a=0;a<list.length;a++)for(let b=a+1;b<list.length;b++)S.labKnown[[list[a],list[b]].sort().join('|')]=1}
function labPair(a,b){if(labDishesWith(a).some(d=>S.unlocked.includes(d)&&dishKeys(d).includes(b))||labKnownPair(a,b))return 'great';const A=labProfile(a),B=labProfile(b);if(A.w!==B.w)return 'bad';
 const heavy=['season','sauce'];if(A.d==='base'&&B.d==='base')return 'bad';if(heavy.includes(A.d)&&heavy.includes(B.d))return 'bad';if(A.d==='drink'&&B.d==='drink')return 'bad';if(A.d==='sweet'&&B.d==='sweet')return 'bad';return 'ok'}
const PAIR_N={great:'很好',ok:'可以',bad:'不合'};
function labStations(sel){const n={};for(const i of sel)for(const d of labDishesWith(i))n[DISHES[d].st]=(n[DISHES[d].st]||0)+1;const ks=Object.keys(n).sort((a,b)=>n[b]-n[a]);if(ks.length)return ks.slice(0,2);
 const w=labProfile(sel[0]||'egg').w;return w==='d'?['bar']:w==='w'?['prep','oven']:['stove']}
function labCat(sel){const n={};for(const i of sel)for(const d of labDishesWith(i))n[DISHES[d].cat]=(n[DISHES[d].cat]||0)+1;const ks=Object.keys(n).sort((a,b)=>n[b]-n[a]);return ks[0]||null}
/* what a trial makes of a selection: a dish (exact, or with one ingredient too many), a promising prototype (research
   progress on the dish it resembles), or an ordinary one with the reason spelled out */
function labEval(sel){let best=null;for(const d of labRD()){const K=dishKeys(d);const m=K.filter(i=>sel.includes(i));const extra=sel.filter(i=>!K.includes(i));const sc=m.length/K.length+m.length*.01-extra.length*.001;if(!best||sc>best.sc)best={d,K,m,extra,sc}}
 if(best&&best.m.length===best.K.length)return{kind:best.extra.length?'success':'exact',d:best.d,extra:best.extra};
 if(best){const lead=best.m.find(i=>['base','drink','sweet'].includes(labProfile(i).d));const missing=best.K.filter(i=>!sel.includes(i));const rightKind=missing.some(k=>sel.some(i=>!best.K.includes(i)&&labProfile(i).d===labProfile(k).d));if(best.m.length>=2||(best.m.length===1&&best.K.length===2&&lead&&rightKind))return{kind:'potential',d:best.d,have:best.m,missing}}
 const known=S.unlocked.find(d=>DISHES[d]&&dishKeys(d).every(i=>sel.includes(i)));if(known)return{kind:'known',d:known};
 /* ordinary: say why */
 const P=sel.map(labProfile);const worlds=new Set(P.map(p=>p.w));const bases=sel.filter(i=>['base','drink','sweet'].includes(labProfile(i).d));const heavy=sel.filter(i=>['season','sauce'].includes(labProfile(i).d));let why;
 if(worlds.size>1)why=worlds.has('w')&&(worlds.has('s')||worlds.has('d'))?'甜的跟鹹的混在一起，味道很奇怪。':'飲料的材料跟料理的材料混在一起了。';
 else if(!bases.length)why='缺少主體：沒有一樣能當主角的食材。';
 else if(bases.length>=2)why=`兩種主體打架：${ING[bases[0]].n}跟${ING[bases[1]].n}都想當主角。`;
 else if(heavy.length>=2)why='味道太重：調味太多，蓋過了食材本身。';
 else why='可以吃，但還不像一道能上菜單的料理。';
 let tip='';for(let a=0;a<sel.length;a++)for(let b=a+1;b<sel.length;b++)if(labPair(sel[a],sel[b])==='great')tip=`${ING[sel[a]].n}跟${ING[sel[b]].n}的相性很好，往這個方向再想想。`;
 if(!tip&&bases.length===1){const st=labStations(sel)[0];tip=`${ING[bases[0]].n}比較適合${ST_N[st]}的料理，換一種配料或醬汁試試。`}
 return{kind:'plain',why,tip}}
function labLock(d){const D=DISHES[d];if(S.level<D.lv)return`要擴建到 ${LEVELS[D.lv-1].n} 才能上菜單`;if(!stationOk(d))return`要先買${ST_N[D.st]}才能上菜單`;return null}
function rdFinish(d,how){const lock=labLock(d);const D=DISHES[d];if(lock){S.rdDone[d]=1;toast(`${how}「${D.n}」！${lock}，到時會自動加入。`);return}unlockDish(d);ach('lab');sfx.fire();banner(how,D.n);toast(`新料理：${D.n}${S.menu.includes(d)?'，已加入菜單':''}`)}
function rdAutoUnlock(){for(const d in S.rdDone||{}){if(S.unlocked.includes(d)){delete S.rdDone[d];continue}if(!labLock(d)){delete S.rdDone[d];unlockDish(d);toast(`之前研發好的「${DISHES[d].n}」現在可以上菜單了！`)}}}
function labPreviewHTML(){if(!labSel.length)return'<p class="small" style="margin:6px 0 0">點食材看它的特性；選 2–3 種再試做。主角＋配料或醬汁，是最常見的組合。</p>';
 const rows=labSel.map(i=>{const p=labProfile(i);return`<div class="labrow"><img alt="" src="${ingURL(i)}"><b>${ING[i].n}</b><span class="tag">${DIR_N[p.d]}</span><span class="muted">${tasteStr(p.t)} · ${'$'.repeat(p.c)}</span></div>`}).join('');
 let pairs='';for(let a=0;a<labSel.length;a++)for(let b=a+1;b<labSel.length;b++){const k=labPair(labSel[a],labSel[b]);pairs+=`<span class="pair ${k}">${ING[labSel[a]].n}×${ING[labSel[b]].n} ${PAIR_N[k]}</span>`}
 const sum=[0,0,0,0];for(const i of labSel){const t=labProfile(i).t;for(let k=0;k<4;k++)sum[k]+=t[k]}const ts=TASTE_N.map((n,k)=>sum[k]>0?n+'↑'.repeat(Math.min(3,Math.round(sum[k]/Math.max(1,labSel.length-1))||1)):null).filter(Boolean).join(' ');
 const st=labStations(labSel).map(k=>ST_N[k]).join('／');const cat=labCat(labSel);
 return`<div class="labprev">${rows}${labSel.length>1?`<div class="labline">相性：${pairs}</div>`:''}<div class="labline">整體味道：${ts||'淡'}</div><div class="labline">可能適合：${st}${cat?' · '+CAT_N[cat]:''}</div></div>`}
function labResultHTML(){const r=S.labLast;if(!r)return'';return`<div class="labres ${r.kind}"><b>${r.title}</b><div>${r.text}</div></div>`}
function ingURL(id){const k='ing'+id;if(ICACHE.has(k))return ICACHE.get(k);const cv=mkCanvas(64),c=cv.getContext('2d');drawIng(c,id,32,34,24);const u=cv.toDataURL();ICACHE.set(k,u);return u}
/* ================= Jill's bag cabinet ================= */
let BAG_T=-9;
function drawBagCabinet(c){const x=280,y=12,w=60,h=72;c.fillStyle='rgba(0,0,0,.2)';c.fillRect(x+1,y+2,w+2,h+2);c.fillStyle='#2A2A2A';rr(c,x-2,y-2,w+4,h+4,3);c.fill();let g=c.createLinearGradient(0,y,0,y+h);g.addColorStop(0,'#F7F3EA');g.addColorStop(1,'#E4DDCF');c.fillStyle=g;c.fillRect(x,y,w,h);
 for(const sx of[x+10,x+30,x+50]){let lg=c.createRadialGradient(sx,y+2,1,sx,y+14,20);lg.addColorStop(0,'rgba(255,220,150,.55)');lg.addColorStop(1,'rgba(255,220,150,0)');c.fillStyle=lg;c.fillRect(sx-20,y,40,34);c.fillStyle='#C99A45';el(c,sx,y+1.5,2.5,1)}
 c.fillStyle='#CFC6B6';c.fillRect(x,y+35,w,2.5);c.fillRect(x,y+h-3,w,3);c.fillStyle='rgba(0,0,0,.08)';c.fillRect(x,y+37.5,w,1.5);
 const bag=(cx,by,k,col)=>{c.fillStyle='rgba(0,0,0,.15)';el(c,cx,by,8,1.4);const dk=shade(col,-.2);
  if(k==='top'){c.fillStyle=col;c.beginPath();c.moveTo(cx-8,by);c.lineTo(cx+8,by);c.lineTo(cx+6.5,by-11);c.lineTo(cx-6.5,by-11);c.closePath();c.fill();c.strokeStyle=dk;c.lineWidth=1.4;c.beginPath();c.arc(cx,by-11,4.2,Math.PI,0);c.stroke();c.fillStyle=dk;c.fillRect(cx-6.5,by-8,13,1)}
  else if(k==='bucket'){c.fillStyle=col;rr(c,cx-6,by-12,12,12,3);c.fill();c.strokeStyle=shade(col,.35);c.lineWidth=.7;c.beginPath();c.moveTo(cx-6,by-10);c.quadraticCurveTo(cx,by-8,cx+6,by-10);c.stroke();c.strokeStyle=col;c.lineWidth=1.2;c.beginPath();c.moveTo(cx-4,by-12);c.lineTo(cx,by-19);c.lineTo(cx+4,by-12);c.stroke()}
  else if(k==='mini'){c.strokeStyle='#D6AE5A';c.lineWidth=.8;c.setLineDash([1,1]);c.beginPath();c.moveTo(cx-5,by-8);c.quadraticCurveTo(cx,by-20,cx+5,by-8);c.stroke();c.setLineDash([]);c.fillStyle=col;rr(c,cx-6,by-8,12,8,2);c.fill();c.fillStyle=dk;c.beginPath();c.moveTo(cx-6,by-8);c.lineTo(cx+6,by-8);c.lineTo(cx,by-4);c.closePath();c.fill()}
  else if(k==='tote'){c.fillStyle=col;c.beginPath();c.moveTo(cx-9,by);c.lineTo(cx+9,by);c.lineTo(cx+8,by-12);c.lineTo(cx-8,by-12);c.closePath();c.fill();c.strokeStyle=dk;c.lineWidth=1;c.beginPath();c.moveTo(cx-5,by-12);c.quadraticCurveTo(cx-5,by-19,cx-1,by-12);c.moveTo(cx+1,by-12);c.quadraticCurveTo(cx+5,by-19,cx+5,by-12);c.stroke()}
  else{c.fillStyle=col;c.beginPath();c.moveTo(cx-8,by-6);c.quadraticCurveTo(cx,by+3,cx+8,by-6);c.lineTo(cx+8,by-8);c.quadraticCurveTo(cx,by-10,cx-8,by-8);c.closePath();c.fill();c.strokeStyle=dk;c.lineWidth=1.1;c.beginPath();c.moveTo(cx-7,by-8);c.quadraticCurveTo(cx,by-20,cx+7,by-8);c.stroke()}
  c.fillStyle='rgba(255,255,255,.25)';c.fillRect(cx-4,by-9,2,5)};
 bag(x+11,y+35,'top','#B8793A');bag(x+30,y+35,'bucket','#1E1E20');bag(x+49,y+35,'mini','#E8B4B0');bag(x+17,y+h-3,'tote','#EFE3CC');bag(x+42,y+h-3,'moon','#8FA38A');
 c.strokeStyle='rgba(255,255,255,.55)';c.lineWidth=1.2;c.beginPath();c.moveTo(x+4,y+h-4);c.lineTo(x+22,y+4);c.moveTo(x+12,y+h-4);c.lineTo(x+28,y+10);c.stroke();c.strokeStyle='#2A2A2A';c.lineWidth=1;c.beginPath();c.moveTo(x+w/2,y);c.lineTo(x+w/2,y+h);c.stroke();c.fillStyle='#C99A45';c.fillRect(x+w/2-3.5,y+h/2-1,2,5);c.fillRect(x+w/2+1.5,y+h/2-1,2,5)}
function drawBagSparkle(c,now){const t=now-BAG_T;const base=.35+Math.sin(now*2)*.25;const pts=[[291,22],[318,40],[332,58],[300,70]];pts.forEach((p,i)=>{const a=t<1.6?(1-t/1.6):Math.max(0,Math.sin(now*1.3+i*1.7))*base;if(a<=.02)return;c.fillStyle=`rgba(255,244,200,${a})`;c.save();c.translate(p[0],p[1]);c.rotate(now*2+i);const s=t<1.6?3.5:2.2;c.fillRect(-s,-.5,s*2,1);c.fillRect(-.5,-s,1,s*2);c.restore()})}

/* ================= guide ================= */
/* 小小店主手冊：seven cards, short lines, the same tone as the rest of the game */
const GUIDE=[
 {ic:'🍳',h:'開店與料理',sum:'每天 17:00 開店、21:30 打烊。你是 Chef Jill，點餐廳裡的東西就能指揮她。',pts:[
  ['帶位','有空桌客人會自己坐；客滿時在門口長椅等。想指定順序，點那組客人或點空桌。'],
  ['點餐','桌上出現紅色「!」→ 點桌子，Jill 過去點餐。'],
  ['做菜','點廚房檯面上亮著「+」的設備，照料理台的指示一步一步做。'],
  ['上菜','桌上出現銀色餐蓋 → 點桌子，Jill 去出菜口端菜。'],
  ['收錢・收桌','出現金幣點桌子收錢；客人走後點桌子收乾淨才能接下一組。'],
  ['料理台的幾種步驟','放食材（有些要照順序）／Jill 自己來（切、炒、打發，開始後她會做完）／等一下（時間到再回來）／看準時機（指針到金色區按）／按住放開（在金色區間放開）／撒幾下（數量對了按完成）。'],
  ['把店開得順','這個在等，就先去做那個。連續好評出菜會累積 COMBO，連續 5 道 PERFECT 進入 JILL\'S ON FIRE。'],
  ['食材不夠','客人照樣點，Jill 會自動緊急叫貨（1.5 倍價、等一下）。冰箱上的「!」點一下就補貨。'],
  ['突發事件（第 3 天起）','奧客鬧事點桌子安撫；設備冒煙連點修理；小偷抱著食材跑，快點他；衛生檢查倒數時桌面要乾淨、料理不能燒焦。']]},
 {ic:'👩🏻‍🍳',h:'Jill 與員工',sum:'Jill 一個人做得完的事有限。人請對了，她才有空坐下來。',pts:[
  ['廚師','負責一個工作站。LV1 只做簡單的菜，LV3 起也會接手 Jill 做到一半的菜。招牌菜和每道新菜的第一份，永遠由 Jill 親自做。'],
  ['服務生','帶位、點餐；LV2 起端菜，LV3 起連結帳都包了。'],
  ['清潔員','客人走後自動收桌。'],
  ['Jill 的空檔','沒有急著要做的菜、沒有客人等她的時候，她會去沙發坐一下、看看書、看看店裡、摸摸靠過來的貓。工作一來她馬上起身——你點桌子，她也會立刻過去。'],
  ['她也會打招呼','客人入座時她會抬頭點個頭；熟客來了偶爾聊兩句；有人拍貓的時候她會看一眼。']]},
 {ic:'🐈',h:'五隻店貓',sum:'樾樾、小齁、寶寶、柔柔、包包住在店裡。不用餵、不用照顧，牠們有自己的生活。',pts:[
  ['個性','樾樾黏 Jill、怕生；小齁愛玩也黏人；寶寶天生明星，總坐在好看的位子；柔柔有點傻，愛埋伏寶寶；包包很會睡。'],
  ['點牠們','可以摸，但牠們不一定理你。點睡著的包包，他會睜一下眼、動動耳朵尾巴——然後繼續睡。'],
  ['客人也看貓','客人會轉頭看貓、微笑，有人會拿手機拍一張。等太久的客人，親人的貓有時會去陪一下。'],
  ['名字','在餐廳日誌的「店貓」可以直接改名字。']]},
 {ic:'🪑',h:'餐廳與升級',sum:'打烊後用今天賺的錢，把小店一路擴建成招牌只剩「JILL」的餐廳。',pts:[
  ['桌椅與擴建','加桌子、擴建店面（評分夠高才能擴建）。擴建後菜單上限、等候組數都變多。'],
  ['廚房設備','爐台、烤箱、咖啡吧、冷盤台、冰箱、平底鍋。升級後更快、位子更多。'],
  ['裝潢','植物、燈、畫、椅子、地毯、餐具、卡座。店裡會真的變漂亮，客人也更有耐心。'],
  ['先留一點錢','商店上方會顯示明天的基本備料大約要多少、建議保留多少。買太多不會擋你，但會提醒你。'],
  ['開店前','可以幫每道菜進貨、調整售價；想再買東西，開店前也能回到商店。']]},
 {ic:'🧪',h:'料理研發',sum:'每種食材都寫著它的角色和味道。用看得到的資訊推理，不是猜密碼。',pts:[
  ['怎麼選','先選一個主角（主體／飲品基底／甜點基底），再配配料、調味或醬汁。選好會先看到相性、整體味道、可能適合哪個工作站。'],
  ['試做的結果','大成功＝就是這道菜；成功料理＝多了一種食材也做出來了；有潛力＝方向對了，告訴你哪些是對的、還缺哪一種，累積三次研究進度就完成；普通試作品＝會說為什麼（缺少主體、味道太重、甜鹹混在一起…）。'],
  ['相性','一起出現在菜單上的食材、或試做證明過的組合，會標「很好」。其他依角色判斷「可以」或「不合」。'],
  ['急的話','每道菜也可以直接買食譜；做熟了還能升到 3 星。']]},
 {ic:'📷',h:'生活相簿',sum:'店裡的日常剛好被看到的時候，會留下一張照片。',pts:[
  ['什麼時候會拍','貓睡成一團、Jill 坐下來、有貓跳上膝蓋、客人拍貓、柔柔埋伏成功……同一種畫面隔幾天可能再出現。'],
  ['珍藏','每種畫面的第一張會珍藏起來，不會被換掉；其他的會慢慢換新，最多留 30 張。不用整理。'],
  ['在哪裡看','餐廳日誌 →「相簿」。日誌的總覽也會放最近的兩張。']]},
 {ic:'💾',h:'存檔與備份',sum:'進度都在這台裝置的瀏覽器裡。換手機前，先備份成一個檔案。',pts:[
  ['自動存檔','每天打烊、每次購買，還有營業中每 20 秒、暫停、切到別的 App 時，都會存下當下的店內狀況。下次打開可以從那個時間點繼續。'],
  ['手動存檔','暫停選單和設定裡都有【儲存目前進度】，上面會寫最後儲存的時間。'],
  ['備份到檔案','設定 → 備份到檔案，會下載一個 .json。從備份檔恢復時會先檢查檔案，確認沒問題才覆蓋現在的進度。也可以複製／貼上備份文字。'],
  ['清除瀏覽器資料','會連存檔一起清掉。備份檔留著就不怕。']]}];
function showGuide(){sub='guide';show(`<div class="sheet tall"><div class="sh-top"><div class="ttl"><div class="eyebrow">JILL'S KITCHEN</div><h2>小小店主手冊</h2></div><button class="btn sm" data-act="closeSub">關閉</button></div>
 <p class="muted" style="font-size:12.5px;margin:0 0 10px">點一張卡片展開。</p>
 <div class="guide2">${GUIDE.map((g,i)=>`<details class="gcard" ${i===0?'open':''}><summary><span class="gic">${g.ic}</span><span class="gh"><b>${g.h}</b><small>${g.sum}</small></span><span class="gchev">›</span></summary><div class="gbody">${g.pts.map(([k,t])=>`<div class="gpt"><b>${k}</b><span>${t}</span></div>`).join('')}</div></details>`).join('')}</div>
 <div class="footer"><button class="btn primary big" data-act="closeSub">知道了</button></div></div>`)}

/* ================= input ================= */
function scenePt(e){const r=sc.getBoundingClientRect();return{x:(e.clientX-r.left-SV.ox)/SV.s,y:(e.clientY-r.top-SV.oy)/SV.s}}
sc.addEventListener('pointerdown',e=>{const p=scenePt(e);SW={x:e.clientX,y:e.clientY,t:performance.now(),hit:false};
 if(room!=='main'){if(roomTap(p,e))SW.hit=true;return}
 if(S.rooms&&S.rooms.side&&p.x>=SIDE_ARCH.x-6&&p.x<=SIDE_ARCH.x+SIDE_ARCH.w+6&&p.y>=SIDE_ARCH.y-4&&p.y<=SIDE_ARCH.y+112&&!hitCat(p)){e.preventDefault();SW.hit=true;setRoom('side');return}
 if(R&&!paused&&phase==='service'&&tapThief(p)){e.preventDefault();SW.hit=true;return}const ct=hitCat(p);if(ct&&!paused){e.preventDefault();tapCat(ct);return}const rg=hitRegular(p);if(rg&&!paused){e.preventDefault();showRegCard(rg);return}const hs=hitSpot(p);if(hs&&!paused){e.preventDefault();tapSpot(hs);return}if(!paused&&p.y>FB-16){const ki=hitKItem(p);if(ki){e.preventDefault();SW.hit=true;tapKItem(ki);return}if(R&&phase==='service'&&p.y>FB){e.preventDefault();SW.hit=true;setRoom('kitchen');return}}if(!R||paused||phase!=='service')return;e.preventDefault();audioInit();
 let best=null,bd=1e9;for(const g of queued()){if(g.state!=='queue'&&g.state!=='arrive')continue;const d=Math.hypot(p.x-g.x,p.y-(g.y-22));if(d<26&&d<bd){bd=d;best={g}}}
 for(const t of R.tables){if((t.room||'main')!==room)continue;const d=Math.hypot((p.x-t.x)*.85,p.y-(t.y-16));const lim=t.seats===4?46:40;if(d<lim&&d<bd){bd=d;best={t}}}
 if(!best)return;SW.hit=true;if(best.g){const t=freeTableFor(best.g);if(t)seatGroup(best.g,t);else toast('目前沒有空桌，先收拾一下吧')}else tapTable(best.t)});
function doCtrl(h){const s=h.s;switch(h.act){case'ing':actIng(s,h.arg);break;case'dose':actDose(s);break;case'doseDone':actDoseDone(s);break;case'tap':actTap(s);break;case'zone':actZone(s);break;case'hold':holdStart(s);break;case'close':R.panel=false;break;case'start':{const n=nextPendingFor(s.type);if(n)startCook(n.tk,n.it);break}}}
tc.addEventListener('pointerdown',e=>{if(!R||paused||phase!=='service')return;e.preventDefault();audioInit();const r=tc.getBoundingClientRect();const x=e.clientX-r.left,y=e.clientY-r.top;
 for(const h of TRAYHIT.chips){if(inR(h,x,y)){const s=R.slots[h.i];R.focus=h.i;R.focusLock=R.t+1.6;if(!s.job){const n=nextPendingFor(s.type);if(n)startCook(n.tk,n.it)}else sfx.tap();return}}
 for(const h of TRAYHIT.ctrls){if(inR(h,x,y)){if(h.act==='hold'){R.holdPtr=e.pointerId;try{tc.setPointerCapture(e.pointerId)}catch(e2){}}doCtrl(h);return}}
 if(TRAYHIT.stage&&inR(TRAYHIT.stage,x,y)){const s=R.slots[R.focus];if(s&&s.job&&s.job.step&&s.job.step.t==='tap')actTap(s)}});
window.addEventListener('pointerup',()=>{if(R)holdEnd()});window.addEventListener('pointercancel',()=>{if(R)holdEnd()});
for(const ev of['pointerup','pointercancel','lostpointercapture'])tc.addEventListener(ev,()=>{if(R)holdEnd()});
window.addEventListener('blur',()=>{if(R)holdEnd()});
for(const ev of['touchend','touchcancel'])window.addEventListener(ev,()=>{if(R&&R.holdSlot)holdEnd()},{passive:true});
/* iOS: the text-selection magnifier and the callout come from the touch, not the pointer event, so they are stopped here.
   Only the two game canvases: buttons, sheets, inputs and the order strip keep their normal touch behaviour. */
for(const el of[sc,tc]){el.addEventListener('touchstart',e=>{e.preventDefault()},{passive:false});el.addEventListener('touchmove',e=>{e.preventDefault()},{passive:false})}
tc.addEventListener('contextmenu',e=>e.preventDefault());
$('#closePill').addEventListener('click',()=>finishClosing());$('#peekPill').addEventListener('click',()=>{$('#peekPill').hidden=true;screenEl.hidden=false;if(phase!=='service'){room='main';forceDraw=true}});
$('#hPause').addEventListener('click',()=>{audioInit();if(phase==='service'){paused=true;showPause();checkpointSave('pause')}else if(phase!=='title'){openSub('settings')}});
document.addEventListener('visibilitychange',()=>{if(document.hidden){if(phase==='service'&&!paused){paused=true;showPause()}if(phase==='service'&&R)checkpointSave('hidden')}else{bg=null;DCACHE.clear();audioResume()}});
/* coming back from another app or from the page cache: caches may be blank, the audio context asleep */
window.addEventListener('pageshow',()=>{bg=null;DCACHE.clear();audioResume()});
window.addEventListener('focus',audioResume);
/* iOS only lets audio resume from a user gesture: the very next tap does it */
document.addEventListener('pointerdown',()=>{if(AU.ctx)audioResume()},{capture:true,passive:true});
document.addEventListener('touchend',()=>{if(AU.ctx)audioResume()},{capture:true,passive:true});

/* ================= screens ================= */
const SVG={
 star:(f)=>`<svg viewBox="0 0 24 24"><path fill="${f?'#E0A93A':'#E3D6C0'}" d="M12 2.5l2.9 6 6.6.8-4.9 4.5 1.3 6.5L12 17l-5.9 3.3 1.3-6.5L2.5 9.3l6.6-.8z"/></svg>`,
 half:()=>`<svg viewBox="0 0 24 24"><defs><linearGradient id="hg"><stop offset="50%" stop-color="#E0A93A"/><stop offset="50%" stop-color="#E3D6C0"/></linearGradient></defs><path fill="url(#hg)" d="M12 2.5l2.9 6 6.6.8-4.9 4.5 1.3 6.5L12 17l-5.9 3.3 1.3-6.5L2.5 9.3l6.6-.8z"/></svg>`,
 book:`<svg viewBox="0 0 16 16"><path d="M2 3.2c2-.8 4-.6 6 .8 2-1.4 4-1.6 6-.8v9.4c-2-.8-4-.6-6 .8-2-1.4-4-1.6-6-.8z" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/><path d="M8 4v9.4" stroke="currentColor" stroke-width="1.2"/></svg>`,
 gear:`<svg viewBox="0 0 16 16"><circle cx="8" cy="8" r="2.4" fill="none" stroke="currentColor" stroke-width="1.4"/><path d="M8 1.5v2M8 12.5v2M1.5 8h2M12.5 8h2M3.4 3.4l1.4 1.4M11.2 11.2l1.4 1.4M3.4 12.6l1.4-1.4M11.2 4.8l1.4-1.4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>`,
 sun:`<svg viewBox="0 0 40 40"><circle cx="20" cy="20" r="8" fill="#F2B43A"/><g stroke="#F2B43A" stroke-width="2.6" stroke-linecap="round"><path d="M20 4v5M20 31v5M4 20h5M31 20h5M8.7 8.7l3.5 3.5M27.8 27.8l3.5 3.5M8.7 31.3l3.5-3.5M27.8 12.2l3.5-3.5"/></g></svg>`,
 cloud:`<svg viewBox="0 0 40 40"><circle cx="14" cy="14" r="6" fill="#F2B43A"/><path d="M12 30h17a6 6 0 0 0 0-12 8 8 0 0 0-15 2 5 5 0 0 0-2 10z" fill="#BFC7CE"/></svg>`,
 rain:`<svg viewBox="0 0 40 40"><path d="M10 24h19a6 6 0 0 0 0-12 8 8 0 0 0-15 2 5 5 0 0 0-4 10z" fill="#9FAAB4"/><g stroke="#5E8FA8" stroke-width="2.2" stroke-linecap="round"><path d="M14 28l-2 5M21 28l-2 5M28 28l-2 5"/></g></svg>`,
 storm:`<svg viewBox="0 0 40 40"><path d="M10 22h19a6 6 0 0 0 0-12 8 8 0 0 0-15 2 5 5 0 0 0-4 10z" fill="#6E7683"/><g stroke="#5E8FA8" stroke-width="2.2" stroke-linecap="round"><path d="M12 27l-2 5M20 27l-2 5M28 27l-2 5M16 30l-2 5M24 30l-2 5"/></g><path d="M22 20l-4 7h4l-2 7 6-9h-4l2-5z" fill="#F2B43A"/></svg>`,
 cool:`<svg viewBox="0 0 40 40"><circle cx="22" cy="16" r="7" fill="#F2D77A"/><path d="M6 26c4-5 9-5 13 0s9 5 13 0" fill="none" stroke="#7FB3C8" stroke-width="2.4" stroke-linecap="round"/><path d="M8 32c4-5 9-5 13 0s9 5 13 0" fill="none" stroke="#7FB3C8" stroke-width="2.4" stroke-linecap="round"/></svg>`,
 hot:`<svg viewBox="0 0 40 40"><circle cx="20" cy="18" r="10" fill="#F28A3A"/><path d="M8 32h24" stroke="#F2B43A" stroke-width="2.4" stroke-linecap="round"/><path d="M11 36h18" stroke="#F2B43A" stroke-width="2" stroke-linecap="round" opacity=".6"/></svg>`,
};
function starsHTML(v){let h='';for(let i=1;i<=5;i++)h+=v>=i?SVG.star(1):v>=i-.5?SVG.half():SVG.star(0);return h}
function show(html,cls){screenEl.hidden=false;screenEl.className=cls||'';screenEl.innerHTML=html;$('#taskPanel').hidden=true;renderTasks()}
function hideScreen(){screenEl.hidden=true;screenEl.innerHTML='';sub=null}
function topIcons(){return`<button class="icon-btn" data-act="peek" aria-label="看店裡" style="font-weight:800;font-size:11px;width:auto;padding:0 9px">看店裡</button><button class="icon-btn" data-act="guide" aria-label="店主手冊" style="font-weight:800;font-size:15px">?</button><button class="icon-btn" data-act="book" aria-label="餐廳日誌">${SVG.book}</button><button class="icon-btn" data-act="settings" aria-label="設定">${SVG.gear}</button>`}

function showTitle(){phase='title';mainScreen='title';R=null;IDLE=null;lifeReset();hud(true);renderTickets();const has=hasSave()&&(S.day>1||S.stats.days>0);
 show(`<div class="title"><div class="sub-cn">Jill 主廚的餐廳</div><h1>JILL'S KITCHEN</h1><div class="by">A Restaurant by Chef Jill</div>
  ${S.checkpoint&&S.checkpoint.day===S.day?`<button class="btn primary open" data-act="open">繼續營業 · ${S.checkpoint.clock}</button><div class="cont">DAY ${S.day} · ${fmt(S.money)} · 今天營業到一半存了進度</div><button class="btn sm" style="margin-top:6px" data-act="openFresh">不繼續，從開店前重來</button>`:`<button class="btn primary open" data-act="open">OPEN FOR DINNER</button>
  <div class="cont">${has?`繼續：DAY ${S.day} · ${fmt(S.money)} · ${LV().n}`:'今天，是 Jill 的餐廳開幕的日子。'}</div>`}
  <div class="links"><button class="btn sm" data-act="guide">店主手冊</button><button class="btn sm" data-act="book">餐廳日誌</button><button class="btn sm" data-act="settings">設定・存檔</button></div></div>`)}
function goMain(){if(S.phase==='shop'&&S.lastSummary)showShop();else{applyGates();planToday();showPrep()}}

function showPrep(){phase='prep';mainScreen='prep';R=null;room='main';lifeReset();IDLE=makeIdle();layoutAll();hud(true);renderTickets();planToday();const T=S.today,F=feat();const W=WEATHER[T.weather],E=EVENTS[T.event];
 const ms=menuList();const unlocked=[...S.unlocked];const sug=suggestStock();let restockCost=0;for(const d of ms){const need=Math.max(0,sug[d]-(S.stock[d]||0));restockCost+=need*costOf(d)}
 const cap=fridgeCap(),tot=stockTotal();const menuN=S.menu.filter(d=>S.unlocked.includes(d)).length;
 const rows=unlocked.map(d=>{const D=DISH(d);const on=S.menu.includes(d);const m=S.price[d]||1;const st=S.stock[d]||0;const lv=mLv(d);
  return`<div class="menu-row ${on?'':'off'}"><img alt="" src="${dishURL(d,'P')}"><div class="nm">${D.n}<span class="stars">${'★'.repeat(starOf(d))}</span><small>${CAT_N[D.cat]} · LV${lv}</small></div><button class="tog ${on?'on':''}" data-act="toggle" data-d="${d}" aria-label="${on?'從菜單移除':'加入菜單'}"></button>
  <div class="meta">${fmt(priceOf(d))} · 成本 ${fmt(costOf(d))} · ${D.steps.length} 步驟・${mechN(d)}${stationOk(d)?'':` · <b style="color:var(--tomato)">缺少${ST_N[D.st]}，客人不會點</b>`}</div>
  ${!on&&F.stock&&st>0?`<div class="ctl offstock"><span>冰箱裡還有 ${st} 份，佔著位子</span><button class="btn sm" data-act="stock" data-d="${d}" data-v="-99">退掉（退 ${fmt(st*costOf(d))}）</button></div>`:''}
  ${on&&(F.prices||F.stock)?`<div class="ctl">${F.prices?`<span class="step"><label>售價</label><button data-act="price" data-d="${d}" data-v="-1" aria-label="降價">−</button><span>${fmt(priceOf(d))}${m!==1?` <small>${m>1?'+':''}${Math.round((m-1)*100)}%</small>`:''}</span><button data-act="price" data-d="${d}" data-v="1" aria-label="漲價">＋</button></span>`:''}${F.stock?`<span class="step"><label>庫存</label><button data-act="stock" data-d="${d}" data-v="-2" aria-label="退貨">−</button><span>${st} 份</span><button data-act="stock" data-d="${d}" data-v="2" aria-label="進貨">＋</button></span>`:''}${F.prices?priceFeelHTML(d):''}${F.stock&&st===0?'<span class="warnpill">沒有備料</span>':''}</div>`:''}</div>`}).join('');
 const sig=S.signature?`<div class="sig"><img alt="" src="${dishURL('signature','P')}"><div><div class="st">★ CHEF JILL'S SIGNATURE ★</div><b>${S.signature.name}</b><small>${fmt(priceOf('signature'))} · 庫存 ${S.stock.signature||0} 份 · 永遠在菜單最上方</small>${F.stock?`<div style="margin-top:6px" class="step"><button data-act="stock" data-d="signature" data-v="-2" style="color:var(--cream)">−</button><span style="color:var(--cream)">${S.stock.signature||0} 份</span><button data-act="stock" data-d="signature" data-v="2" style="color:var(--cream)">＋</button></div>`:''}</div></div>`:'';
 show(`<div class="sheet tall"><div class="sh-top"><div class="ttl"><div class="eyebrow">DAY ${S.day} · 開店前</div><h2>${LV().n}</h2></div>${topIcons()}</div>
  <div class="card today"><div class="wx">${SVG[W.ic||T.weather]||SVG.sun}</div><div><b>${W.n} · 預計約 ${T.people} 位客人</b><p>${W.d}${S.buzz>1?' 店裡最近很紅，人潮會多一些。':''}${(()=>{const w=(S.crew||[]).filter(m=>m.role==='waiter').length;const NT=tablesTotal();return NT>w*6+8?`<br><b style="color:#B8432C">⚠ ${NT} 張桌、${w} 位服務生：桌數比服務生顧得來的多，客人會等太久。</b>`:''})()}</p>${(()=>{const h=wxHints();return h.length?`<p class="hint">今天可能要多準備：<b>${h.map(dishName).join('、')}</b></p>`:''})()}</div></div>
  ${(()=>{if(shopDay()<3)return'';const G=goalLadder();const g=G.find(x=>x.left>0)||G[0];if(!g)return'';const avg=S.lastSummary?Math.max(1,S.lastSummary.net):0;const days=g.left>0&&avg?Math.ceil(g.left/avg):0;return`<div class="goalline"><span>存錢目標</span><b>${g.n}</b><small>${g.left>0?`還差 ${fmt(g.left)}${days&&days<=30?` · 約 ${days} 天`:''}`:'今晚就買得起'}</small></div>`})()}
  ${T.event!=='none'?`<div class="event"><b>今日事件：${E.n}</b><br>${E.d}</div>`:''}
  ${S.buzzMsg?`<div class="news">${S.buzzMsg}</div>`:''}
  ${S.news.length?`<div class="news">${S.news.join('<br>')}</div>`:''}
  <h3>今日任務</h3><div class="card tasks">${T.tasks.map(t=>`<div class="task"><span>${t.txt}</span><small>獎勵 +${fmt(t.reward)}</small></div>`).join('')}</div>
  ${(()=>{const reco=recoDish();const dt=T.tasks.find(t=>t.k==='dish');const list=menuList().filter(stationOk);if(!list.length)return'';const exp=expectDemand(T.groups,60);
   return`<h3>⭐ 今日推薦</h3><div class="card reco"><p class="d">客人今天會比較容易點這道菜。想主推哪一道就選它，再多備一點料。</p><div class="opts">${list.map(d=>`<button class="${reco===d?'on':''}" data-act="reco" data-d="${d}">${reco===d?'⭐ ':''}${dishName(d)}</button>`).join('')}</div>
   <p class="small">${reco?`今日推薦：<b>${dishName(reco)}</b>，預估約 ${Math.max(1,Math.round(exp[reco]||0))} 份。`:'還沒選。'}${dt?` 今日任務要賣 ${dt.n} 份${dishName(dt.d)}${reco===dt.d?'，就是這道。':`（預估約 ${Math.max(1,Math.round(exp[dt.d]||0))} 份）——推薦它會比較容易。`}`:''}</p></div>`})()}
  ${F.prices&&menuList().some(d=>DISH(d).cat==='drink'||DISH(d).cat==='dessert')?`<h3>套餐</h3><div class="card sets"><p class="d">要不要推套餐？點主餐的客人會更常加點；加點的那一份便宜一點。單點照常。</p>${Object.keys(SETS).map(k=>`<button class="setb ${setOn(k)?'on':''}" data-act="setT" data-k="${k}"><b>${setOn(k)?'✓ ':''}${SETS[k].n}</b><small>${SETS[k].d}</small></button>`).join('')}</div>`:''}
  <h3>今日菜單 <small>${menuN}/${menuCap()} 道${S.signature?' ＋ 招牌菜':''}</small></h3>
  ${sig}<div class="card">${rows||'<p class="muted">還沒有料理</p>'}</div>
  ${F.stock?`<div class="cap"><span>冰箱</span><div class="capbar"><i style="width:${tot/cap*100}%"></i></div><span>${tot}/${cap}</span></div><button class="btn sm" data-act="restock" ${restockCost>0?'':'disabled'} style="width:100%">一鍵補到建議量 ${restockCost>0?fmt(restockCost):'（已足夠）'}</button>${(()=>{const off=unlocked.filter(d=>!S.menu.includes(d)&&(S.stock[d]||0)>0);if(!off.length)return'';const n=off.reduce((a,d)=>a+S.stock[d],0);return`<button class="btn sm" data-act="${discardArmed?'discardAll':'discardAsk'}" style="width:100%;margin-top:6px">${discardArmed?`確定退掉這 ${n} 份？（再按一次）`:`退掉不在菜單上的庫存（${n} 份）`}</button>`})()}`:`<p class="muted" style="font-size:12.5px;margin:8px 2px 0">前兩天會自動備料。第 3 天開始可以自己進貨、調整售價。</p>`}
  ${S.day>=2?`<button class="btn sm" data-act="backShop" style="width:100%;margin-top:10px">‹ 返回升級餐廳</button>`:''}
  <div class="footer"><div id="startWarn"></div><button class="btn primary big" data-act="start">開始營業</button></div></div>`)}

function showSummary(){phase='summary';mainScreen='summary';const s=S.lastSummary;if(!s){showShop();return}
 const topHTML=s.top?`<img alt="" src="${dishURL(s.top,'P')}" style="width:34px;height:34px;vertical-align:middle;margin-right:4px">${DISH(s.top)?DISH(s.top).n:''}`:'—';
 show(`<div class="sheet tall"><div class="sh-top"><div class="ttl"><div class="eyebrow">今日結算</div><h2>DAY ${s.day}</h2><div class="sum-stars">${starsHTML(s.stars)}</div></div><button class="icon-btn" data-act="peek" style="font-weight:800;font-size:11px;width:auto;padding:0 9px">看店裡</button></div>
  <div class="ledger"><div><span>營業額</span><span>${fmt(s.rev)}</span></div><div class="neg"><span>食材成本</span><span>-${fmt(s.cost)}</span></div>${s.wages?`<div class="neg"><span>薪資</span><span>-${fmt(s.wages)}</span></div>`:''}<div class="pos"><span>小費</span><span>+${fmt(s.tips)}</span></div>${s.bonus?`<div class="pos"><span>任務獎勵</span><span>+${fmt(s.bonus)}</span></div>`:''}<div class="net"><span>今日淨利</span><span style="color:${s.net>=0?'var(--sage)':'#A2412B'}">${s.net>=0?'+':''}${fmt(s.net)}</span></div></div>
  ${(()=>{const W=WEATHER[s.weather]||WEATHER.sun,E=EVENTS[s.event];return`<div class="chips"><span>${W.n}</span>${s.event&&s.event!=='none'&&E?`<span>${E.n}</span>`:''}${s.treats?`<span>請客 ${s.treats} 次</span>`:''}${s.sets?`<span>套餐加點 ${s.sets} 份</span>`:''}${s.short?`<span class="warn">臨時叫貨 ${s.short} 次</span>`:''}</div>`})()}
  ${s.r1!=null?`<div class="card rating"><div class="rl"><span>餐廳評分</span><b>${(s.r0||3).toFixed(2)} → ${s.r1.toFixed(2)}</b><em class="${s.r1>s.r0+.004?'up':s.r1<s.r0-.004?'dn':''}">${s.r1>s.r0+.004?'↑':s.r1<s.r0-.004?'↓':'→'}</em></div>${s.story&&s.story.length?`<ul>${s.story.slice(0,3).map(x=>`<li class="${x.s>0?'up':'dn'}">${x.s>0?'＋':'－'} ${x.t}</li>`).join('')}</ul>`:'<p class="muted" style="margin:4px 0 0">今天沒有明顯影響評分的事。</p>'}${(()=>{const nl=LEVELS[S.level];if(!nl)return'';const ok=s.r1>=nl.rating;return`<small>${ok?`已達擴建到 ${nl.n} 的評分門檻（${nl.rating.toFixed(1)}）`:`擴建到 ${nl.n} 需要 ${nl.rating.toFixed(1)}，還差 ${(nl.rating-s.r1).toFixed(2)}`}</small>`})()}</div>`:''}
  ${s.recs&&s.recs.length?`<div class="news">🏆 今天創了紀錄：${s.recs.map(k=>REC_N[k]).join('、')}</div>`:''}
  <div class="statgrid"><div class="card"><small>客人數</small><b>${s.guests}</b>${s.lost?` <small style="display:inline">（${s.lost} 位沒等到）</small>`:''}${s.walkins?` <small style="display:inline">（${s.walkins} 組路過進來）</small>`:''}</div><div class="card"><small>Perfect 料理</small><b>${s.perfect}</b> <small style="display:inline">/ ${s.plated}</small></div><div class="card"><small>平均滿意度</small><b>${s.avg}%</b></div><div class="card"><small>最受歡迎</small><b style="font-size:13px">${topHTML}</b></div></div>
  ${s.sales&&s.sales.length?`<h3>今天賣了什麼</h3><div class="card sales">${s.sales.map(x=>`<div class="sale ${x.d===s.reco?'reco':''}"><img alt="" src="${dishURL(x.d,'P')}"><span class="nm">${x.d===s.reco?'⭐ ':''}${dishName(x.d)}</span><span class="n">${x.n} 份</span><span class="rev">${fmt(x.rev)}</span><small>${x.short?`臨時叫貨 ${x.short}`:x.left?`剩 ${x.left}`:'賣完'}</small></div>`).join('')}</div>`:''}
  ${s.crew&&s.crew.length?`<h3>員工今天做了什麼</h3><div class="card staffday">${s.crew.map(m=>{const n=m.n||{};const parts=m.role==='chef'?[n.cook?`做了 ${n.cook} 道`:'沒有接到菜']:m.role==='waiter'?[n.seat?`帶位 ${n.seat}`:'',n.order?`點餐 ${n.order}`:'',n.serve?`上菜 ${n.serve}`:'',n.check?`結帳 ${n.check}`:'',n.clean?`收桌 ${n.clean}`:''].filter(Boolean):[n.clean?`收了 ${n.clean} 桌`:'沒有桌子要收'];return`<div class="srow"><b>${m.name}</b><span>${parts.join('・')||'—'}</span><small>日薪 ${fmt(m.wage)}</small></div>`}).join('')}<div class="srow tot"><b>薪資合計</b><span>${fmt(s.wages)}${s.rev?`（營業額的 ${Math.round(s.wages/s.rev*100)}%）`:''}</span></div></div>`:''}
  ${s.photos?`<div class="news">📷 今天留下了 ${s.photos} 張照片 <button class="jmore" data-act="album">看相簿 ›</button></div>`:''}
  <h3>今日任務</h3><div class="card">${s.tasks.map(t=>`<div class="task ${t.done?'done':''}"><span>${t.done?'✓ ':''}${t.txt}</span><small>${t.done?'+'+fmt(t.reward):'未完成'}</small></div>`).join('')}</div>
  ${s.reviews.length?`<h3>今晚的評論</h3><div class="card">${s.reviews.map(r=>`<div class="review"><div class="rs">${starsHTML(r.s)}</div><p>「${r.txt}」</p><small>${r.critic?'神秘美食評論家':r.name}</small></div>`).join('')}</div>`:''}
  ${goalLadderHTML()}
  ${nextDayNote(s.day+1)?`<div class="news" style="margin-top:14px">明天：${nextDayNote(s.day+1)}</div>`:''}
  <div class="footer"><button class="btn primary big" data-act="toShop">晚上升級餐廳</button></div></div>`);if(s.net>0)sfx.cash()}
function nextDayNote(D){return{2:'解鎖 <b>拿鐵咖啡</b>',3:'第二口 <b>爐子</b> 到貨，還有 <b>番茄義大利麵</b>',4:'冷盤台與 <b>田園沙拉</b>，以及第一次 <b>Rush Hour</b>',5:'晚上可以開始 <b>裝潢與擴建</b> 了',6:'可以聘請 <b>員工</b>，評論家也可能出現',8:'可以研發 <b>Jill 的招牌菜</b>'}[D]||''}

let shopTab='kitchen';
/* the shop belongs to the evening: opened again from the next morning's preparation, it still counts as that evening */
function shopDay(){return S.phase==='prep'&&phase==='shop'?S.day-1:S.day}
function shopTabs(){const D=shopDay();return[{k:'tables',n:'桌椅與擴建',on:true},{k:'kitchen',n:'廚房設備',on:D>=2},{k:'menu',n:'菜單研發',on:D>=2},{k:'decor',n:'裝潢',on:D>=4},{k:'projects',n:'工程',on:D>=3},{k:'cats',n:'貓的東西',on:D>=4},{k:'staff',n:'員工',on:D>=4},{k:'sig',n:'招牌菜',on:D>=7}]}
function showShop(){phase='shop';mainScreen='shop';R=null;rdAutoUnlock();IDLE=makeIdle();layoutAll();hud(true);renderTickets();const tabs=shopTabs();if(!tabs.find(t=>t.k===shopTab&&t.on))shopTab='tables';
 let body='';const money=S.money;const btn=(cost,act,extra,label)=>`<button class="btn sm ${money>=cost?'primary':''}" data-act="${act}" ${extra||''} ${money>=cost?'':'disabled'}>${label||'購買'} ${fmt(cost)}</button>`;
 if(shopTab==='tables'){const cap=tableCap();const next=S.tables<cap?TABLE_COST[S.tables]:null;
  body+=`<div class="item"><img alt="" src="${iconURL('table')}"><div class="nm">餐桌 <span class="muted" style="font-weight:600;font-size:12px">${S.tables} / ${cap} 張</span></div><div class="d">多一張桌子，同時就能多接待一組客人。${S.decor.sofa?`其中 ${S.decor.sofa*2} 張是四人卡座。`:''}</div><div class="act">${next!=null?btn(next,'buyTable','','加一張桌子'):LEVELS[S.level]?`<span class="lock">這個規模最多 ${cap} 張，擴建後可以再加</span>`:`<span class="lock">${cap} 張是 JILL 的極限。想接待更多人：沙發卡座、候位區、動線。</span>`}</div></div>`;
  const nl=LEVELS[S.level];if(nl){const ok=rating()>=nl.rating;body+=`<div class="item"><img alt="" src="${iconURL('expand',S.level+1)}"><div class="nm">擴建：${nl.n}</div><div class="d">桌位上限 ${nl.tables} 張、菜單上限 ${nl.menu} 道、門口最多等候 ${nl.q} 組。牆面、地板與招牌全部換新，也會吸引更講究的客人。</div><div class="act">${shopDay()<4&&S.level===1?'<span class="lock">第 4 天打烊後開放擴建</span>':ok?btn(nl.cost,'expand','','擴建'):`<span class="lock">需要餐廳評分 ${nl.rating.toFixed(1)}（目前 ${rating().toFixed(1)}）</span>`}</div></div>`}
  else body+=`<div class="item"><img alt="" src="${iconURL('expand',5)}"><div class="nm">JILL</div><div class="d">門口的招牌上，只剩下一個名字。這就是 Jill 的餐廳——不會再更大了，但還可以更好。</div></div>`;
  const opsList=OPS.filter(o=>S.level>=Math.min(o.lv,3)||opsLv(o.k));if(opsList.length){body+=`<div class="nm" style="font-weight:800;font-size:15px;margin:14px 0 2px">營運升級</div><p class="muted" style="font-size:12px;margin:0 0 6px">不用再擴建也能變強的地方。</p>`+opsList.map(o=>{const t=opsLv(o.k);const max=o.tiers.length;const cost=t<max?o.tiers[t]:null;const lvOk=S.level>=o.lv;return`<div class="item"><img alt="" src="${iconURL('ops_'+o.k,t)}"><div class="nm">${o.n} ${max>1?`<span class="pips">${o.tiers.map((_,i)=>`<i class="${i<t?'on':''}"></i>`).join('')}</span>`:t?'<span class="tier t1">已擁有</span>':''}</div><div class="d">${o.d(Math.max(1,t||1))}${t&&t<max?`<br><b>下一級：</b>${o.d(t+1)}`:''}</div><div class="act">${cost==null?'<span class="muted">已達最高</span>':!lvOk?`<span class="lock">需要擴建到 ${LEVELS[o.lv-1].n}</span>`:btn(cost,'buyOps',`data-k="${o.k}"`,t?'升級':'購買')}</div></div>`}).join('')}}
 if(shopTab==='kitchen'){for(const E of EQUIP){const lv=S.eq[E.k]||0;const max=5;const cost=lv<max?E.cost[lv]:null;const locked=E.k==='oven'&&lv===0&&shopDay()<3;
  body+=`<div class="item"><img alt="" src="${iconURL(E.k==='bar'?'bar':E.k,lv)}"><div class="nm">${E.n} ${lv?`LV${lv}`:'（未購買）'} <span class="pips">${[1,2,3,4,5].map(i=>`<i class="${i<=lv?'on':''}"></i>`).join('')}</span></div><div class="d">${E.d(Math.max(lv,E.k==='oven'&&!lv?0:1))}${lv<max&&lv?`<br><b>下一級：</b>${E.d(lv+1)}`:''}</div><div class="act">${locked?'<span class="lock">第 3 天後開放</span>':cost!=null?btn(cost,'buyEq',`data-k="${E.k}"`,lv?'升級':'購買'):'<span class="muted">已達最高等級</span>'}</div></div>`}}
 if(shopTab==='menu'){const pan=pantry();body+=`<div class="lab"><div class="nm" style="font-weight:800;font-size:15px">料理研發</div><p class="d" style="margin:2px 0 8px;font-size:12.5px;color:var(--ink2)">每種食材都標著它的角色和味道。選 2–3 種試做（每次 $150）：組合對了就是新料理；方向對了會累積研究進度，三次就能完成；不對也會告訴你為什麼。</p>${labResultHTML()}${DIR_GROUPS.map(([dk,title])=>{const items=pan.filter(i=>labProfile(i).d===dk);if(!items.length)return'';return`${title?`<div class="labgrp">${title}</div>`:''}<div class="opts">${items.map(i=>`<button class="${labSel.includes(i)?'on':''}" data-act="labPick" data-k="${i}"><img alt="" src="${ingURL(i)}">${ING[i].n}<small>${'$'.repeat(labProfile(i).c)}</small></button>`).join('')}</div>`}).join('')}${labPreviewHTML()}<div class="act" style="margin-top:8px">${btn(150,'labTry',labSel.length>=2?'':'disabled','試做')}<span class="muted" style="font-size:12px">${labSel.length?`已選 ${labSel.length}/3`:'還沒選'}</span></div></div></div><div class="card" style="margin-top:10px"><div class="nm" style="font-weight:800;font-size:15px;margin-bottom:4px">食譜升級</div><p class="d" style="margin:0 0 4px;font-size:12.5px;color:var(--ink2)">每升一顆星：售價 +15%、客人更想點、滿意度更高。最高 3 星。</p>`+S.unlocked.concat(S.signature?['signature']:[]).map(d=>{const st=starOf(d);return`<div class="item"><img alt="" src="${dishURL(d,'P')}"><div class="nm">${DISH(d).n}<span class="stars">${'★'.repeat(st)}${'<span style="color:#E3D6C0">★</span>'.repeat(3-st)}</span></div><div class="d">目前售價 ${fmt(priceOf(d))}</div><div class="act">${st<3?btn(starUpCost(d),'starUp',`data-d="${d}"`,'升級'):'<span class="muted">已滿星</span>'}</div></div>`}).join('')+`</div><div class="card" style="margin-top:10px"><div class="nm" style="font-weight:800;font-size:15px;margin-bottom:4px">還沒研發的料理</div>`;
  const list=Object.keys(DISHES).filter(d=>DISHES[d].rd>0&&!S.unlocked.includes(d)).sort((a,b)=>DISHES[a].lv-DISHES[b].lv||DISHES[a].rd-DISHES[b].rd);
  body+=list.length?list.map(d=>{const D=DISHES[d];const lvOk=S.level>=D.lv;const ovenOk=stationOk(d);return`<div class="item"><img alt="" src="${dishURL(d,'P')}"><div class="nm">${D.n} <span class="muted" style="font-size:11.5px;font-weight:600">${CAT_N[D.cat]}</span></div><div class="d">售價 ${fmt(D.price)} · 成本 ${fmt(D.cost)} · ${ST_N[D.st]} · 難度 ${'●'.repeat(D.diff)}<br>${(()=>{const pr=(S.rdProg||{})[d]||0;const K=dishKeys(d);const lead=K.find(i=>['base','drink','sweet'].includes(labProfile(i).d))||K[0];return`研究進度 <span class="dots">${'●'.repeat(pr)}${'○'.repeat(Math.max(0,3-pr))}</span> · ${K.length} 種食材，主角是「${ING[lead].n}」${pr>=2?`，另外要配${K.filter(i=>i!==lead).map(i=>DIR_N[labProfile(i).d]).join('和')}`:''}`})()}</div><div class="act">${!lvOk?`<span class="lock">需要擴建到 ${LEVELS[D.lv-1].n}</span>`:!ovenOk?`<span class="lock">需要先購買${ST_N[D.st]}</span>`:btn(D.rd,'rd',`data-d="${d}"`,'直接買食譜')}</div></div>`}).join(''):'<p class="muted">所有料理都研發完成了。</p>';
  body+=`<p class="muted" style="font-size:12px;margin-top:10px">研發後的料理可以在開店前加入菜單。菜單上限：${menuCap()} 道。</p>`;
  {const sps=Object.keys(SPECIALS).filter(b=>S.unlocked.includes(b));if(sps.length){body+=`<div class="nm" style="font-weight:800;font-size:15px;margin:14px 0 2px">特製版</div><p class="muted" style="font-size:12px;margin:0 0 6px">做熟了的菜（熟練度 LV3），可以研發成更講究的版本：一樣的做法，盤子上多一道功夫，價格高一截，食材另外備。原版和特製版可以同時在菜單上。</p>`;
   for(const b of sps){const sp=SPECIALS[b];const on=S.unlocked.includes(sp.id);const ok=mLv(b)>=3;body+=`<div class="item ${on?'done':''}"><img alt="" src="${dishURL(sp.id,'P')}"><div class="nm">${sp.n} <span class="muted" style="font-size:11.5px;font-weight:600">${dishName(b)} 的特製版</span></div><div class="d">${sp.d} 售價 ${fmt(sp.price)} · 成本 ${fmt(sp.cost)}${on?'<br><b>已研發</b>'+(S.menu.includes(sp.id)?'，在菜單上':'，開店前可以加入菜單'):''}</div>${on?'':`<div class="act">${ok?btn(sp.rd,'rdSpecial',`data-d="${b}"`,'研發'):`<span class="muted">先把${dishName(b)}做到熟練度 LV3（現在 LV${mLv(b)}）</span>`}</div>`}</div>`}}}}
 if(shopTab==='decor'){body+=`<div class="nm" style="font-weight:800;font-size:15px;margin:0 0 2px">店裡的樣子</div><p class="muted" style="font-size:12px;margin:0 0 6px">地板、牆和吧台的顏色。買過的隨時可以換回來；擴建不會改變它。</p><div class="themes">${Object.keys(THEMES).map(k=>{const t=THEMES[k];const own=!!(S.themes&&S.themes[k])||k==='classic';const on=(S.theme||'classic')===k;const lvOk=S.level>=2||k==='classic';return`<button class="theme ${on?'on':''}" data-act="theme" data-k="${k}" ${!lvOk?'disabled':''}><i style="background:linear-gradient(${t.wall0} 0 42%,${t.base} 42% 50%,${t.floor} 50% 100%)"><b style="background:${t.c0}"></b></i><span>${t.n}</span><small>${on?'現在':own?'已擁有':!lvOk?'Bistro 起':fmt(t.cost)}</small></button>`}).join('')}</div><div class="nm" style="font-weight:800;font-size:15px;margin:14px 0 2px">裝潢</div>`+DECOR.map(Dc=>{const t=S.decor[Dc.k]||0;const max=Dc.tiers.length;const cost=t<max?Dc.tiers[t]:null;const needLv=Dc.tierLv?Dc.tierLv[Math.min(t,max-1)]:Dc.lv;const lvOk=S.level>=needLv;return`<div class="item"><img alt="" src="${iconURL(Dc.k==='bar'?'barc':Dc.k,t)}"><div class="nm">${Dc.n} ${max>1?`<span class="pips">${Dc.tiers.map((_,i)=>`<i class="${i<t?'on':''}"></i>`).join('')}</span>`:t?'<span class="tier t1">已擁有</span>':''}</div><div class="d">${Dc.d} 氛圍 +${Dc.amb}</div><div class="act">${cost==null?'<span class="muted">已擁有全部</span>':!lvOk?`<span class="lock">需要擴建到 ${LEVELS[needLv-1].n}</span>`:Dc.k==='sofa'&&S.tables<(t+1)*2?`<span class="lock">需要至少 ${(t+1)*2} 張桌子</span>`:btn(cost,'buyDecor',`data-k="${Dc.k}"`)}</div></div>`}).join('');body+=`<p class="muted" style="font-size:12px;margin-top:10px">目前氛圍 ${ambience()}：客人耐心與滿意度都會提升。買完上方就能看到店裡變化。</p>`}
 if(shopTab==='projects'){body+=`<div class="nm" style="font-weight:800;font-size:15px;margin:0 0 2px">大工程</div><p class="muted" style="font-size:12px;margin:0 0 6px">會把店變成另一個樣子的東西。買了以後，第二天開店就看得到。</p>`;
  for(const P of PROJECTS){const on=projOn(P.k);const ok=S.level>=P.lv;const pct=Math.min(100,Math.round(S.money/P.cost*100));
   body+=`<div class="item ${on?'done':''}"><img alt="" src="${iconURL(P.ic)}"><div class="nm">${P.n} ${on?'<span class="tier t1">已完工</span>':''}</div><div class="d">${on?P.done:P.d}</div>${on?'':`<div class="act">${ok?btn(P.cost,'buyProject',`data-k="${P.k}"`,'開工'):`<span class="muted">需要擴建到 ${LEVELS[P.lv-1].n}</span>`}${!on&&ok&&S.money<P.cost?`<span class="muted" style="font-size:11.5px">還差 ${fmt(P.cost-S.money)}</span>`:''}</div>${!on&&ok&&S.money<P.cost?`<div class="gb"><i style="width:${pct}%"></i></div>`:''}`}</div>`}
  if(projOn('side')){const n=S.sideTables||0;const c=n<6?SIDE_TABLE_COST[n]:null;body+=`<div class="item"><img alt="" src="${iconURL('table')}"><div class="nm">側廳的桌子 <span class="muted" style="font-weight:600;font-size:12px">${n} / 6 張</span></div><div class="d">側廳可以放 6 張桌，前 2 張是四人卡座。</div><div class="act">${c!=null?btn(c,'buySideTable','','加一張'):'<span class="muted">側廳已經滿了</span>'}</div></div>`}
  if(projOn('terrace')){const n=S.frontTables||0;const c=n<3?FRONT_TABLE_COST[n]:null;body+=`<div class="item"><img alt="" src="${iconURL('terrace')}"><div class="nm">露天桌 <span class="muted" style="font-weight:600;font-size:12px">${n} / 3 張</span></div><div class="d">陽傘下的雙人桌。下雨的日子沒有人想坐外面。</div><div class="act">${c!=null?btn(c,'buyFrontTable','','加一張'):'<span class="muted">人行道放不下更多了</span>'}</div></div>`}
  body+=`<div class="nm" style="font-weight:800;font-size:15px;margin:14px 0 2px">店門口</div><p class="muted" style="font-size:12px;margin:0 0 6px">從街上看過來的樣子。到「店門口」那一格就看得到。</p>`;
  for(const E of EXTERIOR){const on=extOn(E.k);const ok=S.level>=E.lv;body+=`<div class="item ${on?'done':''}"><img alt="" src="${iconURL(E.ic)}"><div class="nm">${E.n}${on&&E.styles?` <span class="muted" style="font-weight:600;font-size:12px">${E.styles[(S.ext[E.k]||1)-1]}</span>`:''}</div><div class="d">${E.d}</div><div class="act">${on?(E.styles?`<button class="btn sm" data-act="extStyle" data-k="${E.k}">換顏色</button>`:'<span class="tier t1">裝好了</span>'):ok?btn(E.cost,'buyExt',`data-k="${E.k}"`):`<span class="muted">需要擴建到 ${LEVELS[E.lv-1].n}</span>`}</div></div>`}}
 if(shopTab==='cats'){body+=`<div class="nm" style="font-weight:800;font-size:15px;margin:0 0 2px">貓的東西</div><p class="muted" style="font-size:12px;margin:0 0 6px">買給牠們的。誰會用、怎麼用，牠們自己決定。</p>`;
  for(const G of CATGEAR){const on=gearOn(G.k);const okRoom=!G.need||projOn(G.need);const ok=okRoom&&S.level>=(G.lv||1);const used=Object.keys((S.gearUse||{})[G.k]||{});
   body+=`<div class="item ${on?'done':''}"><img alt="" src="${iconURL(G.ic)}"><div class="nm">${G.n} ${on?'<span class="tier t1">已擺好</span>':''}${G.room==='side'?' <span class="muted" style="font-weight:600;font-size:12px">側廳</span>':''}</div><div class="d">${G.d}${on&&used.length?`<br><b>用過的：</b>${used.map(id=>catName(CAT_DEF.find(x=>x.id===id))).join('、')}`:''}</div>${on?'':`<div class="act">${ok?btn(G.cost,'buyGear',`data-k="${G.k}"`):okRoom?`<span class="muted">需要擴建到 ${LEVELS[(G.lv||1)-1].n}</span>`:'<span class="muted">要先有側廳</span>'}</div>`}</div>`}}
 if(shopTab==='staff'){const crew=S.crew||[];const cap=crewCap();
  body+=`<p class="muted" style="font-size:12.5px;margin:0 0 6px">員工 ${crew.length}/${cap} 人・每日薪資 ${fmt(crewWages())}。${LEVELS[S.level]?'擴建餐廳可以聘更多人。':[!opsLv('room')?'「後場休息室」（桌椅與擴建）':'',!projOn('side')?'「側廳」（工程）':'',!projOn('kext')?'「廚房擴建」（工程）':''].filter(Boolean).length?[!opsLv('room')?'「後場休息室」（桌椅與擴建）':'',!projOn('side')?'「側廳」（工程）':'',!projOn('kext')?'「廚房擴建」（工程）':''].filter(Boolean).join('、')+' 各可以再多 2 位。':'這是最多的人數了。'}</p>`;
  body+=crew.map(m=>{const R0=ROLES[m.role];const up=m.lv<5?R0.up*m.lv:null;return`<div class="item"><img alt="" src="${iconURL(m.role)}"><div class="nm">${m.name} <span class="tier t1">${R0.n}</span> <span class="pips">${[1,2,3,4,5].map(i=>`<i class="${i<=m.lv?'on':''}"></i>`).join('')}</span></div><div class="d">職責：<b>${m.role==='waiter'?dutyLabel(m):DUTY_N[m.duty]}</b>・日薪 ${fmt(crewWage(m))}・${crewStat(m)}</div>${m.role==='chef'?`<div class="cap">${(()=>{const list=S.unlocked.filter(d=>DISH(d).st===m.duty).concat(S.signature&&m.duty==='stove'?['signature']:[]);if(!list.length)return`<span class="muted">${ST_N[m.duty]}目前沒有料理</span>`;return list.map(d=>{const lock=chefLock(m,d);return`<span class="${lock?'no':'ok'}">${lock?'🔒':'✓'} ${dishName(d)}${lock?` <small>${lock}</small>`:''}</span>`}).join('')})()}</div>`:m.role==='waiter'?`<div class="cap duties">${[['seat','帶位',1],['order','點餐',1],['serve','上菜',2],['check','結帳',3],['clean','收桌',1]].map(([k,n,lv])=>{const d=waiterDuties(m);const locked=m.lv<lv;return`<button class="dt ${locked?'no':d[k]?'on':''}" data-act="dutyT" data-k="${m.id}" data-d="${k}" ${locked?'disabled':''}>${locked?'🔒':d[k]?'✓':'○'} ${n}${locked?` <small>LV${lv}</small>`:''}</button>`}).join('')}</div>`:`<div class="cap"><span class="ok">✓ 客人走後收桌</span></div>`}<div class="act">${m.role==='chef'&&R0.duties.length>1?`<button class="btn sm" data-act="duty" data-k="${m.id}">換工作站</button>`:''}${up!=null?btn(up,'crewUp',`data-k="${m.id}"`,'訓練升級'):'<span class="muted">已滿級</span>'}<button class="btn sm danger" data-act="crewFire" data-k="${m.id}">解雇</button></div></div>`}).join('');
  body+=`<div class="nm" style="font-weight:800;font-size:15px;margin:14px 0 2px">招募</div>`+Object.keys(ROLES).map(r=>{const R0=ROLES[r];return`<div class="item"><img alt="" src="${iconURL(r)}"><div class="nm">${R0.n}</div><div class="d">${R0.d} 日薪 ${fmt(R0.wage)} 起，LV5 ${fmt(Math.round(R0.wage*2.8))}。</div><div class="act">${crew.length>=cap?`<span class="lock">${LEVELS[S.level]?'人數已滿，擴建後可再聘':opsLv('room')?'人數已滿':'人數已滿，後場休息室可以再多 2 位'}</span>`:btn(R0.hire,'hire',`data-k="${r}"`,'聘請')}</div></div>`}).join('')}
 if(shopTab==='sig'){if(S.signature)body+=`<div class="sig"><img alt="" src="${dishURL('signature','P')}"><div><div class="st">★ CHEF JILL'S SIGNATURE ★</div><b>${S.signature.name}</b><small>${fmt(priceOf('signature'))} · ${Object.keys(SIG).map(k=>SIG[k][S.signature[k]].n).join('・')}</small><small style="display:block;margin-top:3px">${sigLv()>=3?'第三版 · 食用花與金箔':sigLv()===2?`第二版 · 醬汁畫盤與嫩葉 · 賣到 ${SIG_EVO[2]} 份升第三版（目前 ${sigSold()}）`:`第一版 · 賣到 ${SIG_EVO[1]} 份升第二版（目前 ${sigSold()}）`}</small></div></div><p class="muted" style="font-size:12.5px">招牌菜永遠在菜單最上方，有些客人會專程為它而來。賣得夠多，Jill 會把盤子做得更講究、價格也高一點。可以花 $800 重新調整配方。</p>${btn(800,'sigOpen','','重新設計')}`;
  else body+=`<div class="item"><img alt="" src="${dishURL('signature','P')}"><div class="nm">Jill's Signature Dish</div><div class="d">從主食、蛋白質、醬汁、配菜組出一道只屬於 Jill 的料理。會出現在菜單最上方，客人也會專程為它而來（客流 +10%）。</div><div class="act">${S.level<2?'<span class="lock">需要擴建到 Jill\'s Bistro</span>':btn(3000,'sigOpen','','開始研發')}</div></div>`}
 show(`<div class="sheet tall"><div class="sh-top"><div class="ttl"><div class="eyebrow">${S.phase==='prep'?`DAY ${S.day} · 開店前`:`DAY ${S.day} · 打烊後`}</div><h2>升級 Jill 的餐廳</h2></div>${topIcons()}</div>
  <div class="row" style="margin-bottom:6px"><span class="muted" style="font-weight:700">目前現金</span><span class="moneytag">${fmt(S.money)}</span><span style="margin-left:auto" class="muted">評分 ${rating().toFixed(1)}</span></div>
  ${(()=>{const est=restockEstimate(),keep=keepAside();const low=S.money<keep;const when=S.phase==='prep'?'今天':'明日';return`<div class="budget ${low?'low':''}"><span>${when}預估基本備料 約 ${fmt(est)}</span><span>建議保留 約 ${fmt(keep)}</span>${low?`<span class="w">⚠ 現在的現金可能不夠完成建議備料，${when}可以少備一點或臨時叫貨</span>`:''}</div>`})()}
  <div class="tabs">${tabs.map(t=>`<button class="${t.k===shopTab?'on':''}" data-act="tab" data-k="${t.k}" ${t.on?'':'disabled'}>${t.n}</button>`).join('')}</div>
  <div class="card">${body}</div>
  <div class="footer">${S.phase==='prep'?`<button class="btn primary big" data-act="toPrep">回到開店準備 ›</button>`:`<button class="btn primary big" data-act="nextDay">準備 DAY ${S.day+1}</button>`}</div></div>`)}

let sigDraft=null;
function showSig(){sub='sig';const d=sigDraft;const old=S.signature;S.signature=d;const url=dishCanvas('signature','P',220,S.decor.ware>0);S.signature=old;const price=320+Object.keys(SIG).reduce((a,k)=>a+SIG[k][d[k]].p,0);
 show(`<div class="sheet tall"><div class="sh-top"><div class="ttl"><div class="eyebrow">Jill's Signature Dish</div><h2>設計招牌菜</h2></div><button class="btn sm" data-act="closeSub">取消</button></div>
  <div class="sigprev"><canvas id="sigCv" width="220" height="220"></canvas><div><div class="eyebrow">★ CHEF JILL'S SIGNATURE ★</div><div style="font-family:var(--disp);font-size:19px;margin:4px 0">${d.name}</div><div class="muted" style="font-size:12.5px">售價 ${fmt(price)} · 在爐台用平底鍋煎，看準時機起鍋</div></div></div>
  ${Object.keys(SIG).map(cat=>`<h3>${SIG_CAT_N[cat]}</h3><div class="opts">${Object.keys(SIG[cat]).map(k=>`<button class="${d[cat]===k?'on':''}" data-act="sigPick" data-c="${cat}" data-k="${k}">${SIG[cat][k].n}<small>+${SIG[cat][k].p}</small></button>`).join('')}</div>`).join('')}
  <h3>菜名</h3><input class="txt" id="sigName" maxlength="18" value="${d.name.replace(/"/g,'&quot;')}">
  <div class="footer"><button class="btn primary big" data-act="sigMake" ${S.money>=(S.signature?800:3000)?'':'disabled'}>${S.signature?'更新配方 $800':'研發招牌菜 $3,000'}</button></div></div>`);
 const cv=$('#sigCv');cv.getContext('2d').drawImage(url,0,0)}
function sigAutoName(d){return`Jill's ${SIG.sauce[d.sauce].n}${SIG.protein[d.protein].n}`}

let bookTab='reviews';
/* what the last reviews keep saying, in one line the player can act on */
function reviewDigest(n){const rv=S.reviews.slice(-(n||25));const d={n:rv.length,good:0,wait:0,left:0,price:0,q:0,cat:0,sig:0,treat:0};for(const r of rv){if(r.s>=4)d.good++;const tg=r.tags||[];for(const k of tg)if(k in d)d[k]++;if(!r.tags&&r.s<=2)d.q++}return d}
function reviewDigestHTML(){const d=reviewDigest(25);if(d.n<5)return'';const parts=[`好評 ${d.good}`];if(d.wait)parts.push(`等太久 ${d.wait}`);if(d.left)parts.push(`沒等到就走 ${d.left}`);if(d.q)parts.push(`料理失常 ${d.q}`);if(d.price)parts.push(`覺得貴 ${d.price}`);if(d.cat)parts.push(`提到貓 ${d.cat}`);if(d.sig)parts.push(`提到招牌菜 ${d.sig}`);
 const worst=[['wait',d.wait+d.left,'客人最常抱怨等待：多一位服務生或廚師、備料多一點，會有幫助。'],['q',d.q,'料理失常被提到好幾次：注意燒焦與 Okay 的比例。'],['price',d.price,'有人覺得貴：看看哪些菜的售價調高了。']].sort((a,b)=>b[1]-a[1])[0];
 return`<div class="digest"><b>最近 ${d.n} 則在說什麼</b><span>${parts.join('・')}</span>${d.good>=d.n*.8?'<small>大多是好評，繼續保持。</small>':worst&&worst[1]>=3?`<small>${worst[2]}</small>`:''}</div>`}
function notesFor(id,n){return(S.notes||[]).filter(x=>x.reg===id).slice(0,n||2)}
let lightbox=null;   /* {ids:[...], i} while a photo is open */
function openLightbox(id){const A=albumList().slice().reverse();const i=A.findIndex(p=>p.id===id);if(i<0)return;lightbox={ids:A.map(p=>p.id),i};$('#lightbox').hidden=false;lightboxRender();sfx.tap()}
function closeLightbox(){lightbox=null;const el=$('#lightbox');if(el)el.hidden=true}
function lightboxRender(){const el=$('#lightbox');if(!lightbox||!el)return;const p=albumList().find(x=>x.id===lightbox.ids[lightbox.i]);if(!p){closeLightbox();return}
 el.innerHTML=`<div class="lb-bg" data-lb="close"></div><button class="lb-close" data-lb="close" aria-label="關閉">✕</button>
  <figure class="lb-card ${p.keep?'keep':''}"><img alt="" src="${photoSrc(p)}"><figcaption><span class="when">DAY ${p.day}${p.clock?' · '+p.clock:''}</span><b>「${p.cap}」</b>${p.txt?`<span class="txt">${p.txt}</span>`:''}</figcaption>${p.keep?'<span class="pin">珍藏</span>':''}</figure>
  <div class="lb-nav"><button data-lb="prev" ${lightbox.i<=0?'disabled':''} aria-label="上一張">‹</button><span class="lb-count">${lightbox.i+1} / ${lightbox.ids.length}</span><button class="lb-keep ${p.keep?'on':''}" data-lb="keep">${p.keep?'♥ 珍藏中':'♡ 珍藏'}</button><button data-lb="next" ${lightbox.i>=lightbox.ids.length-1?'disabled':''} aria-label="下一張">›</button></div>`}
function lightboxStep(d){if(!lightbox)return;const n=lightbox.i+d;if(n<0||n>=lightbox.ids.length)return;lightbox.i=n;lightboxRender()}
function albumFigure(p,i){return`<figure class="polaroid ${p.keep?'keep':''}" style="--r:${((i%3)-1)*1.5}deg" data-act="photo" data-k="${p.id}"><img alt="" src="${photoSrc(p)}"><figcaption><span class="when">DAY ${p.day}${p.clock?' · '+p.clock:''}</span><b>「${p.cap}」</b>${p.txt?`<span class="txt">${p.txt}</span>`:''}</figcaption>${p.keep?'<span class="pin">珍藏</span>':''}</figure>`}
function showBook(){sub='book';let body='';
 if(bookTab==='front'){const rv=S.reviews.slice(-2).reverse();const notes=(S.notes||[]).slice(0,3);const A=albumList().slice(-2).reverse();const met=REGS.filter(r=>(S.regulars[r.id]||0)>0).length;const nAch=Object.keys(S.achievements).length;
  body=`<div class="jhead"><div class="bigrate"><b>${rating().toFixed(1)}</b><div><div class="sum-stars">${starsHTML(Math.round(rating()*2)/2)}</div><div class="muted" style="font-size:12px">${S.reviews.length} 則評價 · 開業 ${S.stats.days||0} 天 · ${S.stats.guests||0} 位客人</div></div></div></div>
   <div class="jsec"><div class="jt">最近的評價 <button class="jmore" data-act="btab" data-k="reviews">全部 ›</button></div>${rv.length?rv.map(r=>`<div class="review"><div class="rs">${starsHTML(r.s)}</div><p>「${r.txt}」</p><small>${r.name||''}${r.day?` · DAY ${r.day}`:''}</small></div>`).join(''):'<p class="muted">還沒有評價。</p>'}</div>
   <div class="jsec"><div class="jt">熟客留言 <button class="jmore" data-act="btab" data-k="regulars">熟客 ›</button></div>${notes.length?notes.map(n=>`<div class="note"><b>${REG_BY[n.reg]?REG_BY[n.reg].n:n.reg}</b><span>「${n.txt}」</span><small>DAY ${n.day}</small></div>`).join(''):`<p class="muted">${met?'熟客們還沒留下什麼話。':'來過 4 次的客人會成為熟客，偶爾留下幾句話。'}</p>`}</div>
   <div class="jsec"><div class="jt">生活相簿 <button class="jmore" data-act="btab" data-k="mem">相簿 ›</button></div>${A.length?`<div class="album">${A.map(albumFigure).join('')}</div>`:'<p class="muted">店裡的日常會慢慢留下照片。</p>'}</div>
   <div class="jsec"><div class="jt">五隻店貓 <button class="jmore" data-act="btab" data-k="cats">店貓 ›</button></div><div class="catrow">${CAT_DEF.map(C=>`<div><img alt="" src="${catPortraitURL(C)}"><span>${catName(C)}</span></div>`).join('')}</div></div>
   <div class="jsec"><div class="jt">成就 ${nAch} / ${ACH.length} <button class="jmore" data-act="btab" data-k="ach">全部 ›</button></div><div class="achrow">${ACH.filter(a=>S.achievements[a.id]).slice(-4).map(a=>`<span><img alt="" src="${iconURL(a.ic)}">${a.n}</span>`).join('')||'<span class="muted">還沒有成就。</span>'}</div></div>`}
 if(bookTab==='reviews'){const rv=S.reviews.slice().reverse();body=`<div class="bigrate"><b>${rating().toFixed(1)}</b><div><div class="sum-stars">${starsHTML(Math.round(rating()*2)/2)}</div><div class="muted" style="font-size:12px">${S.reviews.length} 則評論 · 最近 40 則計入評分</div></div></div>${reviewDigestHTML()}<div class="card" style="margin-top:12px">${rv.length?rv.slice(0,30).map(r=>`<div class="review"><div class="rs">${starsHTML(r.s)}</div><p>「${r.txt}」</p><small>${r.critic?'神秘美食評論家':r.name} · DAY ${r.day}</small></div>`).join(''):'<p class="muted">還沒有評論。開店吧！</p>'}</div>`}
 if(bookTab==='regulars'){body=`<p class="muted" style="font-size:12.5px;margin:0 0 8px">來過兩次會開始眼熟，4 次成為熟客，12 次成為 Jill 的老客人。回頭客累計：${S.returning} / 100</p><div class="card">`+REGS.map(r=>{const v=S.regulars[r.id]||0;const tier=regTier(v);const met=v>0;const nt=met?notesFor(r.id,2):[];const m=met?regMem(r.id):null;const ut=met?usualTable(r.id):null;const ud=met?(()=>{let b=null,bn=2;for(const k in m.orders)if(m.orders[k]>bn){bn=m.orders[k];b=k}return b})():null;const habits=met?[ut!=null?`老位子 T${ut+1}`:'',ud?`常點${dishName(ud)}`:''].filter(Boolean):[];
   return`<div class="reg ${met?'':'unknown'}"><img alt="" src="${portraitURL(r.looks,'reg'+r.id)}"><div><b>${met?r.n:'？？？'}</b> ${met?`<span class="tier t${Math.floor(tier)}">${TIER_N[tier]}</span>`:''}</div><p>${met?`${r.who}<br>來店 ${v} 次${habits.length?'・'+habits.join('・'):''}・「${r.l[Math.floor(tier)]}」`:`第 ${r.day} 天後可能會出現。`}</p>${met&&m.facts.length?`<div class="facts">${m.facts.slice(0,4).map(f=>`<div class="note"><span>${f.txt}</span><small>DAY ${f.day}</small></div>`).join('')}</div>`:''}${nt.length?`<div class="notes">${nt.map(n=>`<div class="note"><span>「${n.txt}」</span><small>DAY ${n.day}</small></div>`).join('')}</div>`:''}</div>`}).join('')
  +(()=>{const v=S.regulars.dylan||0;if(!v)return'';const rv=S.dylan.stage>=3;const tier=regTier(v);return`<div class="reg"><img alt="" src="${portraitURL(DYLAN.looks,'regdylan')}"><div><b>Dylan</b> <span class="tier ${rv?'t2':'t'+Math.floor(tier)}">${rv?'Jill 的先生':TIER_N[tier]}</span></div><p>${rv?DYLAN.who2:DYLAN.who}<br>來店 ${v} 次${rv?`・DAY ${S.dylan.reveal}`:''}</p></div>`})()+'</div>'}
 if(bookTab==='rest'){const nl=LEVELS[S.level];const wages=crewWages();const last=S.lastSummary;
  body=`<div class="jsec" style="margin-top:0;padding-top:0;border-top:0"><div class="jt">評分走勢 <span class="muted" style="font-weight:600;font-size:12px">最近 14 天</span></div>${ratingHistHTML()}
   <p class="muted" style="font-size:12px;margin:8px 0 0">評分＝最近 40 則評論的平均（評論家 ×3、檢查員 ×2）。客人給幾顆星看四件事：料理品質、等了多久、價格合不合理、店裡的氛圍；生氣離開一律一顆星，客滿沒等到的人有時留兩顆星。${nl?`擴建到 ${nl.n} 需要 ${nl.rating.toFixed(1)}。`:'這已經是最大的規模。'}</p></div>
   <div class="jsec"><div class="jt">餐廳紀錄</div>${recordsHTML()}</div>
   <div class="jsec"><div class="jt">員工與開銷</div><div class="card">${(S.crew||[]).length?(S.crew||[]).map(m=>`<div class="srow"><b>${m.name}</b><span>${ROLES[m.role].n} LV${m.lv}・${DUTY_N[m.duty]||m.duty}</span><small>日薪 ${fmt(crewWage(m))}</small></div>`).join('')+`<div class="srow tot"><b>每日薪資</b><span>${fmt(wages)}${last&&last.rev?`（昨天營業額的 ${Math.round(wages/last.rev*100)}%）`:''}</span></div>`:'<p class="muted" style="margin:0">還沒有員工。</p>'}</div>
   <div class="card" style="margin-top:8px"><div class="srow"><b>開業</b><span>${S.stats.days||0} 天・${S.stats.guests||0} 位客人</span></div><div class="srow"><b>累積收入</b><span>${fmt(S.lifetime||0)}</span></div>${last?`<div class="srow"><b>昨天</b><span>營業額 ${fmt(last.rev)}・食材 ${fmt(last.cost)}・薪資 ${fmt(last.wages)}・淨利 ${fmt(last.net)}</span></div>`:''}</div></div>`}
 if(bookTab==='talk'){const L=(S.dayLog||[]);body=`<p class="muted" style="font-size:12.5px;margin:0 0 8px">${S.dayLogDay?`DAY ${S.dayLogDay} 店裡說過的話`:'今天店裡說過的話'}（最近 ${Math.min(90,L.length)} 句）。營業中按左上角的 💬 也看得到。</p><div class="card">${logHTML(L,90)}</div>`}
 if(bookTab==='cats'){body=`<p class="muted" style="font-size:12.5px;margin:0 0 8px">住在店裡的五隻貓。名字可以直接改。</p><div class="card">`+CAT_DEF.map(C=>`<div class="reg"><img alt="" src="${catPortraitURL(C)}"><div><input class="txt" data-cat="${C.id}" maxlength="8" value="${catName(C).replace(/"/g,'&quot;')}" aria-label="貓咪名字" style="padding:6px 10px;width:auto;max-width:130px"> <span class="tier">${C.sex}</span></div><p>${C.who}</p></div>`).join('')+'</div>'}
 if(bookTab==='mem'){const A=albumList().slice().reverse();body=`<p class="muted" style="font-size:12.5px;margin:0 0 10px">店裡的日常，剛好被看到的時候會留下一張。第一次的畫面會珍藏起來，其他的會慢慢換新。</p>`+(A.length?`<div class="album">${A.map(albumFigure).join('')}</div>`:'<div class="card"><p class="muted" style="margin:0">還沒有留下任何畫面。</p></div>')}
 if(bookTab==='ach'){const n=ACH.filter(a=>S.achievements[a.id]).length;const groups=[['早期',a=>!a.h&&(a.p||0)===0],['中期',a=>!a.h&&a.p===1],['成熟的餐廳',a=>!a.h&&a.p===2],['自己發生的事',a=>a.h]];
  body=`<p class="muted" style="font-size:12.5px;margin:0 0 8px">${n} / ${ACH.length} 已解鎖。有些成就不會先告訴你是什麼。</p>`+groups.map(([title,f])=>{const list=ACH.filter(f);if(!list.length)return'';const got=list.filter(a=>S.achievements[a.id]).length;return`<div class="jt" style="margin-top:12px">${title} <span class="muted" style="font-weight:600;font-size:12px">${got}/${list.length}</span></div><div class="card">`+list.map(a=>{const g0=S.achievements[a.id];const veil=a.h&&!g0;return`<div class="ach ${g0?'':'off'}"><img alt="" src="${iconURL(veil?'moon':a.ic)}"><b>${veil?'？？？':a.n}</b><small>${veil?'……':a.d}${g0?` · DAY ${g0}`:''}</small></div>`}).join('')+'</div>'}).join('')}
 if(bookTab==='mastery'){body=`<p class="muted" style="font-size:12.5px;margin:0 0 8px">Jill 越常做一道菜，就做得越快，Perfect 判定也越寬。</p><div class="card">`+S.unlocked.concat(S.signature?['signature']:[]).map(d=>{const x=S.xp[d]||0,lv=mLv(d);const cur=XP_T[lv-1],nx=XP_T[lv]||cur;const pct=lv>=5?100:(x-cur)/(nx-cur)*100;return`<div class="mast"><img alt="" src="${dishURL(d,'P')}"><b style="font-size:13.5px">${DISH(d).n}</b><span class="tier ${lv>=5?'t2':lv>=3?'t1':''}">LV${lv}</span><div class="bar" style="grid-column:2"><i style="width:${pct}%"></i></div><small class="muted">${DISH(d).steps.length} 步驟</small></div>`}).join('')+'</div>'}
 show(`<div class="sheet tall"><div class="sh-top"><div class="ttl"><div class="eyebrow">JILL'S KITCHEN JOURNAL</div><h2>餐廳日誌</h2></div><button class="btn sm" data-act="closeSub">關閉</button></div>
  <div class="tabs">${[['front','總覽'],['rest','餐廳'],['reviews','評價'],['regulars','熟客'],['talk','話語'],['mem','相簿'],['cats','店貓'],['ach','成就'],['mastery','熟練度']].map(([k,n])=>`<button class="${bookTab===k?'on':''}" data-act="btab" data-k="${k}">${n}</button>`).join('')}</div>${body}</div>`)}
let resetStep=0;
let pasteBox=false;
function importConfirmHTML(){const pi=pendingImport;if(!pi)return '';const when=pi.savedAt?(()=>{const d=new Date(pi.savedAt),p=n=>String(n).padStart(2,'0');return `${d.getFullYear()}/${d.getMonth()+1}/${d.getDate()} ${p(d.getHours())}:${p(d.getMinutes())}`})():'';
 return `<div class="inline-warn" style="margin-top:10px">讀取這個備份？<b>DAY ${pi.day} · ${fmt(pi.money)}</b>${when?`（${when} 存的）`:''}${pi.checkpoint&&pi.checkpoint.day===pi.day?`<br>裡面有營業到一半（${pi.checkpoint.clock}）的進度`:''}<br>目前的進度會被這個備份取代。</div><div class="row"><button class="btn" style="flex:1" data-act="importNo">取消</button><button class="btn primary" style="flex:1" data-act="importYes">讀取這個存檔</button></div>`}
function pasteBoxHTML(){if(!pasteBox)return '';return `<div class="card" style="margin-top:10px"><p class="small" style="margin-top:0">把之前「複製備份文字」貼在這裡，再按恢復。</p><textarea id="pasteArea" class="txt" rows="4" style="width:100%;font-size:11px;font-weight:500;resize:vertical" placeholder="{&quot;app&quot;:&quot;jills-kitchen&quot;…}"></textarea><div class="row" style="margin-top:8px"><button class="btn" style="flex:1" data-act="pasteCancel">取消</button><button class="btn primary" style="flex:1" data-act="pasteGo">從貼上的文字恢復</button></div></div>`}
function showSettings(){sub='settings';show(`<div class="modal"><h2>設定・存檔</h2>
 <div class="card"><div class="setrow"><span>背景音樂</span><button class="tog ${S.music?'on':''}" data-act="music" aria-label="背景音樂"></button></div><div class="setrow"><span>音效</span><button class="tog ${S.sfx?'on':''}" data-act="sfx" aria-label="音效"></button></div></div>
 ${saveCardHTML()}
 <p class="small" style="margin:8px 2px 0">進度存在目前使用的瀏覽器裡：清除網站資料、換瀏覽器或換裝置時不會自動帶過去，要靠上面的備份。</p>
 ${importConfirmHTML()}${pasteBoxHTML()}
 <div class="stack" style="margin-top:14px">${phase!=='service'?'<button class="btn" data-act="load">回到上次存檔</button>':''}
 ${resetStep===0?'<button class="btn danger" data-act="reset1">重置遊戲</button>':`<div class="inline-warn">確定要重置嗎？Day、金錢、升級、熟客、成就都會消失，無法復原。</div><div class="row"><button class="btn" style="flex:1" data-act="resetNo">取消</button><button class="btn danger" style="flex:1" data-act="reset2">我確定，重置</button></div>`}
 <button class="btn dark" data-act="closeSub">關閉</button></div></div>`,'dim')}
function saveCardHTML(){const cp=S.checkpoint&&S.checkpoint.day===S.day?S.checkpoint:null;return `<div class="card" style="margin-top:12px"><div class="setrow"><span>✓ 本機自動儲存</span><span class="muted" style="font-weight:600;font-size:12px">${S.savedLabel?`最後儲存：${S.savedLabel}`:'尚未存檔'}</span></div>
 ${phase==='service'&&R&&R.closing==null?`<p class="small">營業中每 20 秒、暫停時、切到別的 App 時都會存下目前的店內狀況（客人、訂單、爐上的菜、Jill 和員工）。下次開啟可以從這個時間點繼續。</p><button class="btn" style="width:100%;margin-top:8px" data-act="save">儲存目前進度</button>`:`<p class="small">每天打烊、購買升級後都會自動存檔${cp?`；今天營業到一半的進度（${cp.clock}）也還在`:''}。</p><button class="btn" style="width:100%;margin-top:8px" data-act="save">存檔</button>`}</div>
 <div class="card" style="margin-top:10px"><div class="setrow"><span><b>備份與移轉</b></span></div><p class="small">換手機、換瀏覽器、以防萬一：把進度存成一個檔案，之後再讀回來。</p>
 <div class="row" style="margin-top:8px"><button class="btn" style="flex:1" data-act="export">備份到檔案</button><button class="btn" style="flex:1" data-act="import">從備份檔恢復</button></div>
 <div class="row" style="margin-top:8px"><button class="btn sm" style="flex:1" data-act="copyBackup">複製備份文字</button><button class="btn sm" style="flex:1" data-act="pasteBackup">貼上備份文字恢復</button></div></div>`}
function showPause(){sub='pause';show(`<div class="modal"><h2>暫停中</h2><p>DAY ${S.day} · ${clockStr()} · 目前營業額 ${fmt(R?R.st.rev:0)}</p>
 <div class="stack"><button class="btn primary big" data-act="resume">繼續營業</button></div>
 ${saveCardHTML()}
 <div class="card" style="margin-top:10px"><div class="setrow"><span>背景音樂</span><button class="tog ${S.music?'on':''}" data-act="music" aria-label="背景音樂"></button></div><div class="setrow"><span>音效</span><button class="tog ${S.sfx?'on':''}" data-act="sfx" aria-label="音效"></button></div></div>
 <div class="stack" style="margin-top:12px"><button class="btn" data-act="guide">小小店主手冊</button>${R&&!R.closed?'<button class="btn" data-act="closeEarly">提早打烊（等店裡客人吃完）</button><button class="btn danger" data-act="closeNow">馬上結束今天</button>':''}</div></div>`,'dim')}
function openSub(k){if(k==='book')showBook();else if(k==='settings'){resetStep=0;showSettings()}}
function closeSub(){sub=null;if(phase==='service'){if(paused){showPause();return}hideScreen();return}if(mainScreen==='title')showTitle();else if(mainScreen==='prep')showPrep();else if(mainScreen==='shop')showShop();else if(mainScreen==='summary')showSummary()}

let startWarned=false,discardArmed=false;
screenEl.addEventListener('click',e=>{const b=e.target.closest('[data-act]');if(!b||b.disabled)return;audioInit();doAct(b.dataset.act,b.dataset.d,b.dataset.k,b)});
function doAct(a,d,k,b){
 switch(a){
 case'open':sfx.door();if(S.checkpoint&&S.checkpoint.day===S.day)resumeCheckpoint();else goMain();break;
 case'openFresh':sfx.door();clearCheckpoint();save();goMain();break;
 case'discardAsk':discardArmed=true;keepScroll(showPrep);setTimeout(()=>{discardArmed=false;if(phase==='prep'&&!sub)keepScroll(showPrep)},4000);break;
 case'discardAll':{discardArmed=false;for(const x of S.unlocked)if(!S.menu.includes(x)&&(S.stock[x]||0)>0)buyStock(x,-99);sfx.tap();toast('退掉了不在菜單上的庫存');save();keepScroll(showPrep);break}
 case'setT':{S.sets=S.sets||{};S.sets[k]=!S.sets[k];if(k==='full'&&S.sets.full){S.sets.drink=false;S.sets.dessert=false}if((k==='drink'||k==='dessert')&&S.sets[k])S.sets.full=false;sfx.tap();save();keepScroll(showPrep);break}
 case'reco':{if(!S.today)break;S.today.reco=S.today.reco===d?null:d;sfx.tap();save();keepScroll(showPrep);break}
 case'toggle':{const on=S.menu.includes(d);if(on){const rest=S.menu.filter(x=>x!==d&&DISH(x).cat!=='drink'&&DISH(x).cat!=='dessert');if(!rest.length&&!S.signature&&DISH(d).cat!=='drink'&&DISH(d).cat!=='dessert'){toast('菜單至少要有一道主食');break}S.menu=S.menu.filter(x=>x!==d)}else{if(S.menu.filter(x=>S.unlocked.includes(x)).length>=menuCap()){toast(`菜單已滿（上限 ${menuCap()} 道）${LEVELS[S.level]?'，擴建後可以放更多':opsLv('board')?'':'；「大菜單板」可以多放 2 道'}`);break}S.menu.push(d);S.menuSince=S.menuSince||{};if(!S.menuSince[d])S.menuSince[d]=S.day;if(menuList().length>=8)ach('menu8')}sfx.tap();save();showPrep();break}
 case'price':{const steps=[.8,.9,1,1.1,1.2,1.3,1.5];let i=steps.indexOf(S.price[d]||1);if(i<0)i=2;i=clamp(i+(+b.dataset.v),0,steps.length-1);S.price[d]=steps[i];sfx.tap();save();keepScroll(showPrep);break}
 case'stock':{const ok=buyStock(d,+b.dataset.v);if(!ok)toast(+b.dataset.v>0?(stockTotal()>=fridgeCap()?'冰箱滿了，升級冰箱可以放更多':'錢不夠了'):'沒有庫存可以退');else sfx.tap();save();keepScroll(showPrep);break}
 case'restock':{const sug=suggestStock();for(const x in sug){const need=sug[x]-(S.stock[x]||0);if(need>0)buyStock(x,need)}sfx.buy();save();keepScroll(showPrep);break}
 case'start':{const empty=menuList().filter(x=>(S.stock[x]||0)===0);if(feat().stock&&empty.length&&!startWarned){startWarned=true;$('#startWarn').innerHTML=`<div class="inline-warn">${empty.map(x=>DISH(x).n).join('、')} 沒有備料，客人點了要臨時叫貨（1.5 倍價、要等）。再按一次直接開店。</div>`;break}startWarned=false;clearCheckpoint();save();startService();break}
 case'toShop':showShop();break;
 case'backShop':showShop();break;
 case'toPrep':showPrep();break;
 case'tab':shopTab=k;sfx.tap();showShop();break;
 case'buyTable':{const c=TABLE_COST[S.tables];if(S.money>=c&&S.tables<tableCap()){S.money-=c;S.tables++;sfx.buy();toast('新桌子搬進來了！');save();IDLE=null;showShop();shopAfterBuy()}break}
 case'buySideTable':{const n=S.sideTables||0;const c=SIDE_TABLE_COST[n];if(projOn('side')&&c!=null&&S.money>=c){S.money-=c;S.sideTables=n+1;sfx.buy();toast('側廳多了一張桌子');save();IDLE=null;keepScroll(showShop);shopAfterBuy()}break}
 case'buyFrontTable':{const n=S.frontTables||0;const c=FRONT_TABLE_COST[n];if(projOn('terrace')&&c!=null&&S.money>=c){S.money-=c;S.frontTables=n+1;sfx.buy();toast('陽傘下多了一張桌子');save();IDLE=null;keepScroll(showShop);shopAfterBuy()}break}
 case'buyProject':{const P=PROJECTS.find(x=>x.k===k);if(!P||projOn(P.k)||S.money<P.cost||S.level<P.lv)break;S.money-=P.cost;S.rooms[P.k]=1;S.newRooms[P.k]=S.day;S.reveal={k:P.k,day:S.day};if(P.k==='side')S.sideTables=Math.max(S.sideTables||0,2);if(P.k==='terrace')S.frontTables=Math.max(S.frontTables||0,1);ach('project');if(PROJECTS.every(x=>projOn(x.k)))ach('allprojects');save();IDLE=null;bg=null;for(const kk in BGC)delete BGC[kk];projectReveal(P);break}
 case'buyExt':{const E=EXTERIOR.find(x=>x.k===k);if(!E||extOn(E.k)||S.money<E.cost||S.level<E.lv)break;S.money-=E.cost;S.ext[E.k]=1;sfx.buy();toast(`${E.n}：裝好了，到「店門口」看看`);if(EXTERIOR.every(x=>extOn(x.k)))ach('storefront');save();for(const kk in BGC)delete BGC[kk];keepScroll(showShop);shopAfterBuy();break}
 case'extStyle':{const E=EXTERIOR.find(x=>x.k===k);if(!E||!E.styles||!extOn(E.k))break;S.ext[E.k]=(S.ext[E.k]%E.styles.length)+1;sfx.tap();save();for(const kk in BGC)delete BGC[kk];keepScroll(showShop);break}
 case'buyGear':{const G=CATGEAR.find(x=>x.k===k);if(!G||gearOn(G.k)||S.money<G.cost||(G.need&&!projOn(G.need))||S.level<(G.lv||1))break;S.money-=G.cost;S.gear[G.k]=S.day;sfx.buy();toast(`${G.n}：擺好了。看牠們什麼時候發現。`);if(CATGEAR.every(x=>gearOn(x.k)))ach('catgear');save();IDLE=null;bg=null;for(const kk in BGC)delete BGC[kk];keepScroll(showShop);shopAfterBuy();break}
 case'revealPeek':{const P=PROJECTS.find(x=>x.k===k);hideReveal();if(P){room=P.room;forceDraw=true;screenEl.hidden=true;$('#peekPill').hidden=false;banner(P.n,P.done,'gold')}break}
 case'revealClose':hideReveal();showShop();shopAfterBuy();break;
 case'expand':{const nl=LEVELS[S.level];if(nl&&S.money>=nl.cost){S.money-=nl.cost;S.level++;if(S.level===2)ach('bistro');sfx.buy();banner(LV().n,'擴建完成！');if(S.level===5)ach('jill');S.newRoom=S.day;save();bg=null;showShop();shopAfterBuy()}break}
 case'buyEq':{const lv=S.eq[k]||0;const E=EQUIP.find(x=>x.k===k);const c=E.cost[lv];if(lv<5&&S.money>=c){S.money-=c;S.eq[k]=lv+1;sfx.buy();toast(`${E.n} ${lv?'升級':'購買'}完成：LV${lv+1}`);save();IDLE=null;layoutAll();keepScroll(showShop);shopAfterBuy()}break}
 case'rdSpecial':{const sp=SPECIALS[d];if(!sp||S.unlocked.includes(sp.id)||mLv(d)<3||S.money<sp.rd)break;S.money-=sp.rd;unlockDish(sp.id);S.stock[sp.id]=S.stock[sp.id]||0;sfx.buy();toast(`研發成功：${sp.n}！${S.menu.includes(sp.id)?'已加入菜單':'菜單已滿，記得在開店前調整'}`);ach('special');if(Object.keys(SPECIALS).filter(b=>S.unlocked.includes(SPECIALS[b].id)).length>=4)ach('specials4');save();keepScroll(showShop);shopAfterBuy();break}
 case'rd':{const D=DISHES[d];if(S.money>=D.rd){S.money-=D.rd;unlockDish(d);sfx.buy();toast(`研發成功：${D.n}！${S.menu.includes(d)?'已加入菜單':'菜單已滿，記得在開店前調整'}`);save();keepScroll(showShop);shopAfterBuy()}break}
 case'theme':{const t=THEMES[k];if(!t)break;S.themes=S.themes||{classic:1};if(!S.themes[k]){if(S.money<t.cost||S.level<2)break;S.money-=t.cost;S.themes[k]=1;toast(`${t.n}：換好了`);sfx.buy()}else sfx.tap();S.theme=k;save();bg=null;IDLE=null;keepScroll(showShop);break}
 case'buyOps':{const o=OPS.find(x=>x.k===k);if(!o)break;const t=opsLv(k);const c=o.tiers[t];if(c==null||S.money<c||S.level<o.lv)break;S.money-=c;S.ops=S.ops||{};S.ops[k]=t+1;sfx.buy();toast(`${o.n}：完成了`);if(k==='room')ach('room');save();keepScroll(showShop);shopAfterBuy();break}
 case'buyDecor':{const Dc=DECOR.find(x=>x.k===k);const t=S.decor[k]||0;const c=Dc.tiers[t];const needLv=Dc.tierLv?Dc.tierLv[Math.min(t,Dc.tiers.length-1)]:Dc.lv;if(c!=null&&S.money>=c&&S.level>=needLv){S.money-=c;S.decor[k]=t+1;S.newDecor=S.day;sfx.buy();toast(`${Dc.n} 裝好了，看看店裡！`);save();IDLE=null;bg=null;keepScroll(showShop);shopAfterBuy()}break}
 case'hire':{const R0=ROLES[k];S.crew=S.crew||[];if(!R0||S.money<R0.hire||S.crew.length>=crewCap())break;S.money-=R0.hire;const used=S.crew.map(m=>m.name);const name=CREW_NAMES[k].find(n=>!used.includes(n))||R0.n;const duty=k==='chef'?(S.eq.bar&&!chefFor('bar')?'bar':'stove'):R0.duties[0];S.crew.push({id:'c'+Date.now().toString(36)+Math.floor(Math.random()*999),role:k,name,lv:1,duty});ach('hire');sfx.buy();toast(`${name} 加入了 Jill's Kitchen！`);save();keepScroll(showShop);shopAfterBuy();break}
 case'crewFire':S.crew=(S.crew||[]).filter(m=>m.id!==k);save();keepScroll(showShop);break;
 case'crewUp':{const m=(S.crew||[]).find(m=>m.id===k);if(!m||m.lv>=5)break;const c=ROLES[m.role].up*m.lv;if(S.money<c)break;S.money-=c;m.lv++;sfx.buy();toast(`${m.name} 升到 LV${m.lv}！`);save();keepScroll(showShop);shopAfterBuy();break}
 case'duty':{const m=(S.crew||[]).find(m=>m.id===k);if(!m)break;let opts=ROLES[m.role].duties;if(m.role==='chef')opts=opts.filter(d=>d==='stove'||S.eq[d]);const i=opts.indexOf(m.duty);m.duty=opts[(i+1)%opts.length];sfx.tap();save();keepScroll(showShop);break}
 case'dutyT':{const m=(S.crew||[]).find(m=>m.id===k);if(!m||m.role!=='waiter')break;const D0=waiterDuties(m);const key=b.dataset.d;D0[key]=!D0[key];m.duty=D0.seat&&D0.order?'both':D0.seat?'seat':D0.order?'order':'both';sfx.tap();save();keepScroll(showShop);break}
 case'labPick':{const i=labSel.indexOf(k);if(i>=0)labSel.splice(i,1);else if(labSel.length<3)labSel.push(k);else toast('最多選 3 種食材');sfx.tap();keepScroll(showShop);break}
 case'labTry':{if(S.money<150||labSel.length<2)break;S.money-=150;const sel=labSel.slice();const r=labEval(sel);S.rdProg=S.rdProg||{};S.rdDone=S.rdDone||{};
  if(r.kind==='exact'||r.kind==='success'){const D=DISHES[r.d];S.labLast={kind:r.kind,title:r.kind==='exact'?'大成功！':'成功料理',text:r.kind==='exact'?`${sel.map(i=>ING[i].n).join('＋')}，就是「${D.n}」。`:`做出了「${D.n}」。${ING[r.extra[0]].n}其實用不到，下次可以省下來。`};labLearn(dishKeys(r.d));delete S.rdProg[r.d];rdFinish(r.d,r.kind==='exact'?'研發成功！':'研發成功')}
  else if(r.kind==='potential'&&(S.labTried=S.labTried||{})[sel.slice().sort().join('|')]){/* the same combination again: nothing new is learned */const miss=[...new Set(r.missing.map(i=>DIR_N[labProfile(i).d]))];S.labLast={kind:'plain',title:'跟上次一樣',text:`這個組合試過了，沒有新的發現。${r.have.map(i=>ING[i].n).join('、')}留著，換一種${miss.join('或')}試試。`};sfx.okay()}
  else if(r.kind==='potential'){S.labTried[sel.slice().sort().join('|')]=1;const D=DISHES[r.d];const pr=Math.min(3,(S.rdProg[r.d]||0)+1);S.rdProg[r.d]=pr;labLearn(r.have);const miss=r.missing.map(i=>DIR_N[labProfile(i).d]);
   const text=pr>=3?`第三次試作，終於成形了。`:`像是一道${CAT_N[D.cat]}（${ST_N[D.st]}）的雛形。${r.have.map(i=>ING[i].n).join('、')}是對的，還缺${miss.length}種${[...new Set(miss)].join('或')}。研究進度 ${'●'.repeat(pr)}${'○'.repeat(3-pr)}`;
   S.labLast={kind:'potential',title:pr>=3?'研究完成！':'有潛力的試作品',text,have:r.have.slice(),missDirs:[...new Set(r.missing.map(i=>labProfile(i).d))]};if(pr>=3){delete S.rdProg[r.d];rdFinish(r.d,'研究完成！')}else sfx.good()}
  else if(r.kind==='known'){S.labLast={kind:'plain',title:'這道已經會了',text:`這就是「${DISHES[r.d].n}」的做法，已經在菜單上了。`};sfx.okay()}
  else{S.labLast={kind:'plain',title:'普通試作品',text:r.why+(r.tip?' '+r.tip:'')};sfx.okay()}
  labSel=[];save();keepScroll(showShop);break}
 case'starUp':{const c=starUpCost(d);if(S.money<c||starOf(d)>=3)break;S.money-=c;S.rstar=S.rstar||{};S.rstar[d]=starOf(d)+1;if(starOf(d)>=3)ach('star3');sfx.buy();toast(`${DISH(d).n} 升到 ${'★'.repeat(starOf(d))}`);save();keepScroll(showShop);shopAfterBuy();break}
 case'closeEarly':paused=false;hideScreen();closeShop('Jill 提早打烊，等店裡客人吃完就結算');break;
 case'closeNow':paused=false;hideScreen();clearCheckpoint();closeShop('今天到此為止，準備結算');for(const g of R.groups.slice()){if(g.state==='check')collect(g);else if(g.state!=='leave')leaveGroup(g,'ok')}for(const t of R.tables){t.dirty=false;t.plates=[]}break;
 case'nextDay':clearCheckpoint();S.day++;S.today=null;S.todayCost=0;S.lastSummary=null;S.phase='prep';applyGates();planToday();save();showPrep();break;
 case'sigOpen':sigDraft=S.signature?{...S.signature}:{base:'mash',protein:'duck',sauce:'redwine',side:'asparagus',name:''};if(!sigDraft.name)sigDraft.name=sigAutoName(sigDraft);showSig();break;
 case'sigPick':{const auto=sigDraft.name===sigAutoName(sigDraft);const nm=$('#sigName');if(nm&&!auto)sigDraft.name=nm.value;sigDraft[b.dataset.c]=k;if(auto)sigDraft.name=sigAutoName(sigDraft);keepScroll(showSig);break}
 case'sigMake':{const cost=S.signature?800:3000;if(S.money<cost)break;const nm=($('#sigName').value||'').trim()||sigAutoName(sigDraft);S.money-=cost;const first=!S.signature;S.signature={...sigDraft,name:nm.slice(0,18)};if(first){S.xp.signature=0;S.stock.signature=S.stock.signature||0;ach('sig')}ICACHE.clear();DCACHE.clear();sfx.fire();banner("★ SIGNATURE ★",nm);save();sub=null;shopTab='sig';showShop();break}
 case'guide':showGuide();break;
 case'peek':screenEl.hidden=true;$('#peekPill').hidden=false;break;
 case'book':bookTab='front';showBook();break;
 case'photo':openLightbox(k);break;
 case'album':bookTab='mem';showBook();break;
 case'btab':bookTab=k;showBook();break;
 case'settings':resetStep=0;showSettings();break;
 case'closeSub':closeSub();break;
 case'music':S.music=!S.music;setAudio();save();sub==='pause'?showPause():showSettings();break;
 case'sfx':S.sfx=!S.sfx;setAudio();save();sub==='pause'?showPause():showSettings();break;
 case'save':{if(phase==='service'&&R&&R.closing==null){const ok=checkpointSave('manual');toast(ok?`已儲存目前進度（${S.savedLabel}）`:'這個瀏覽器不允許存檔')}else toast(save()?`已存檔（${S.savedLabel}）`:'這個瀏覽器不允許存檔');if(sub==='settings')showSettings();else if(sub==='pause')showPause();break}
 case'copyBackup':copyBackup();break;
 case'pasteBackup':pasteBox=true;if(sub==='pause'){sub='settings'}showSettings();setTimeout(()=>{const a=$('#pasteArea');if(a)a.focus()},50);break;
 case'pasteCancel':pasteBox=false;showSettings();break;
 case'pasteGo':{const a=$('#pasteArea');const t=a?a.value.trim():'';pasteBox=false;if(!t){toast('還沒有貼上任何內容');showSettings();break}importSaveText(t);break}
 case'export':exportSave();break;
 case'import':pickImportFile();break;
 case'importYes':importConfirm();break;
 case'importNo':pendingImport=null;showSettings();break;
 case'load':{if(phase==='service'){toast('營業中不能讀取存檔');break}const o=load();if(o){S=o;ICACHE.clear();DCACHE.clear();IDLE=null;bg=null;toast(`已讀取：DAY ${S.day}`);setAudio();sub=null;showTitle()}else toast('找不到存檔');break}
 case'reset1':resetStep=1;showSettings();break;
 case'resetNo':resetStep=0;showSettings();break;
 case'reset2':{S=newState();photoClear();try{localStorage.removeItem(KEY)}catch(e){}save();R=null;phase='title';ICACHE.clear();DCACHE.clear();IDLE=null;bg=null;resetStep=0;sub=null;toast('已重置，一切重新開始');showTitle();break}
 case'resume':paused=false;hideScreen();break;
 }}
screenEl.addEventListener('input',e=>{if(e.target.dataset&&e.target.dataset.cat){S.catNames=S.catNames||{};S.catNames[e.target.dataset.cat]=e.target.value.trim().slice(0,8);save();return}if(e.target.id==='sigName'&&sigDraft)sigDraft.name=e.target.value});
/* a big purchase is an event: the dust of the work, then the reveal — what changed, what it opens up, who said what */
function projectReveal(P){let el=$('#reveal');if(!el){el=document.createElement('div');el.id='reveal';screenEl.parentNode.appendChild(el)}
 el.hidden=false;el.className='work';el.innerHTML=`<div class="rv"><div class="dust">${Array.from({length:14},(_,i)=>`<i style="left:${8+i*6.5}%;animation-delay:${(i*137%700)/1000}s"></i>`).join('')}</div><b>施工中…</b><span>${P.n}</span></div>`;sfx.buy();
 const T=setTimeout(()=>{if(!$('#reveal')||el.hidden)return;el.className='done';sfx.ding();
  el.innerHTML=`<div class="rv card"><div class="eyebrow">完工</div><h2>${P.n}</h2><p class="done">${P.done}</p><p class="say">Jill：「${P.jill}」</p>${P.react?`<p class="react">${P.react}</p>`:''}${P.unlock&&P.unlock.length?`<div class="unl"><b>現在可以</b>${P.unlock.map(u=>`<span>${u}</span>`).join('')}</div>`:''}<div class="btns"><button class="btn primary" data-act="revealPeek" data-k="${P.k}">去看看 ›</button><button class="btn" data-act="revealClose">繼續買東西</button></div></div>`},1500);
 el.onclick=e=>{const b=e.target.closest('[data-act]');if(!b)return;clearTimeout(T);doAct(b.dataset.act,b.dataset.d,b.dataset.k,b)}}
function hideReveal(){const el=$('#reveal');if(el){el.hidden=true;el.innerHTML=''}}
function keepScroll(fn){const sh=screenEl.querySelector('.sheet');const top=sh?sh.scrollTop:0;fn();const s2=screenEl.querySelector('.sheet');if(s2)s2.scrollTop=top}

/* ================= loop ================= */
let last=performance.now(),tick=0;
let lastEv=null;
let frameN=0,forceDraw=false;
let frameErrs=0,frameErrMsg='',stockT=0;
/* One bad frame must not stop the game: the loop keeps its appointment with the next frame no matter what. The first
   error of a kind is logged; after a burst of them the player is told once (the situation the soufflé bug produced —
   a dead loop with a live Pause button — cannot happen again). */
function frame(now){try{frameBody(now)}catch(e){frameErrs++;const m=e&&e.message||String(e);if(m!==frameErrMsg){frameErrMsg=m;console.error('[frame]',e)}if(frameErrs===40){try{toast('畫面出了點問題，已跳過（遊戲繼續）','warn')}catch(e2){}}}requestAnimationFrame(frame)}
function frameBody(now){frameN++;const covered=phase!=='service'||paused||!!sub;/* the sims always get their time; the expensive part, drawing the room, runs at ~20 fps while a sheet covers it */
 if(AU.ctx&&S.music){const ev=evening();if(ev!==lastEv){lastEv=ev;AU.music.gain.setTargetAtTime(ev?.09:.16,AU.ctx.currentTime,.8)}}const dt=Math.min(.05,(now-last)/1000);last=now;const t=now/1000;
 if(!(phase==='service'&&paused)){updateCats(dt,t);lifeUpd(dt)}
 if(phase==='service'&&R&&!paused){update(dt);tick+=dt;if(tick>.12){tick=0;renderTickets();updTicketBars();renderTasks();hud();stockChip();renderRoomTabs();stockT=(stockT||0)+1;if(stockT%8===0)renderStock()}}
 else if(phase!=='service'&&IDLE){const J=IDLE.jill;if(!(evening()&&LIFE.plan==='sofa'))J.x=PASS.x;}
 if(sc.width>0&&(!covered||frameN%3===0||forceDraw)){forceDraw=false;drawScene(t);flushMem()}{const tw=$('#trayWrap');const want=!!(R&&R.panel&&phase==='service'&&!paused);if(tw.hidden===want)tw.hidden=!want;if(want&&tc.width>0)drawTray(t)}}

/* ================= boot ================= */
function boot(){layoutAll();hud(true);renderTickets();showTitle();requestAnimationFrame(frame);photoOpen().then(()=>photoMigrate());
 if(document.fonts&&document.fonts.ready)document.fonts.ready.then(()=>{bg=null;layoutAll()})}
boot();
})();
