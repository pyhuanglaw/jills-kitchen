// Static analysis of js/game.js: sections, top-level declarations, duplicates, unused names,
// shared mutable state and timer/listener call sites. Dev tool only.
const path=require('path');
const NP=[path.join(__dirname,'..','node_modules'),'/opt/node-tools/node_modules','/opt/node22/lib/node_modules'];
const req=m=>{for(const p of NP){try{return require(path.join(p,m))}catch(e){}}return require(m)};
const acorn=req('acorn'),walk=req('acorn-walk');
const fs=require('fs');
const file=process.argv[2]||path.join(__dirname,'..','js','game.js');
const src=fs.readFileSync(file,'utf8');
const ast=acorn.parse(src,{ecmaVersion:'latest',locations:true});
// find IIFE body
let body=ast.body;
for(const st of ast.body){if(st.type==='ExpressionStatement'&&st.expression.type==='CallExpression'){const cal=st.expression.callee;const fn=cal.type==='FunctionExpression'||cal.type==='ArrowFunctionExpression'?cal:null;if(fn)body=fn.body.body}}
// sections
const sections=[];const re=/\/\* =+ ([^=]+?) =+ \*\//g;let m;while((m=re.exec(src)))sections.push({name:m[1].trim(),pos:m.index});
sections.forEach((s,i)=>s.size=((sections[i+1]||{pos:src.length}).pos)-s.pos);
const secOf=pos=>{let n='(preamble)';for(const s of sections)if(s.pos<=pos)n=s.name;return n};
// declarations
const decl={};const add=(name,kind,node)=>{(decl[name]=decl[name]||[]).push({kind,line:node.loc.start.line,sec:secOf(node.start),node})};
for(const st of body){if(st.type==='FunctionDeclaration')add(st.id.name,'function',st);else if(st.type==='VariableDeclaration')for(const d of st.declarations){if(d.id.type==='Identifier')add(d.id.name,st.kind,d)}}
// references
const refs={};const assigns={};
walk.fullAncestor(ast,(node,state,anc)=>{if(node.type!=='Identifier')return;const p=anc[anc.length-2];if(!p)return;
 if((p.type==='FunctionDeclaration'||p.type==='FunctionExpression')&&p.id===node)return;
 if(p.type==='VariableDeclarator'&&p.id===node)return;
 if(p.type==='MemberExpression'&&p.property===node&&!p.computed)return;
 if(p.type==='Property'&&p.key===node&&!p.computed&&!p.shorthand)return;
 refs[node.name]=(refs[node.name]||0)+1;
 if(p.type==='AssignmentExpression'&&p.left===node||p.type==='UpdateExpression'&&p.argument===node){let fn='(top)';for(let i=anc.length-1;i>=0;i--){const a=anc[i];if(a.type==='FunctionDeclaration'){fn=a.id.name;break}}(assigns[node.name]=assigns[node.name]||new Set()).add(fn)}});
const dup=Object.entries(decl).filter(([k,v])=>v.length>1);
const unused=Object.entries(decl).filter(([k,v])=>!(refs[k]>0));
const lets=Object.entries(decl).filter(([k,v])=>v[0].kind==='let');
// call sites of interest
const sites={setInterval:[],setTimeout:[],requestAnimationFrame:[],addEventListener:[],localStorage:[]};
walk.full(ast,n=>{if(n.type==='CallExpression'){const c=n.callee;const name=c.type==='Identifier'?c.name:c.type==='MemberExpression'&&!c.computed?c.property.name:null;if(name&&Object.hasOwn(sites,name))sites[name].push(`${n.loc.start.line} [${secOf(n.start)}]`);if(c.type==='MemberExpression'&&c.object.name==='localStorage')sites.localStorage.push(`${n.loc.start.line} ${c.property.name}`)}});
// per-frame reachability (static call graph from frame)
const fnNodes={};for(const [k,v] of Object.entries(decl))for(const d of v)if(d.kind==='function')fnNodes[k]=d.node;
const calls={};for(const [k,n] of Object.entries(fnNodes)){const s=new Set();walk.full(n.body,x=>{if(x.type==='CallExpression'&&x.callee.type==='Identifier'&&fnNodes[x.callee.name])s.add(x.callee.name)});calls[k]=s}
const reach=new Set();const stack=['frame'];while(stack.length){const f=stack.pop();if(reach.has(f)||!calls[f])continue;reach.add(f);for(const g of calls[f])stack.push(g)}
const out={file,lines:src.split('\n').length,bytes:src.length,
 sections:sections.map(s=>`${s.name}: ${(s.size/1024).toFixed(1)} KB`),
 topLevel:{functions:Object.values(decl).flat().filter(d=>d.kind==='function').length,const:Object.values(decl).flat().filter(d=>d.kind==='const').length,let:lets.length},
 duplicates:dup.map(([k,v])=>`${k}: ${v.map(d=>d.kind+'@'+d.line+'['+d.sec+']').join(', ')}`),
 unused:unused.map(([k,v])=>`${k} (${v[0].kind}@${v[0].line} [${v[0].sec}])`),
 sharedMutable:lets.map(([k,v])=>`${k}: written by ${assigns[k]?[...assigns[k]].length:0} fn(s)${assigns[k]?' — '+[...assigns[k]].slice(0,8).join(', '):''}`),
 mostWrittenGlobals:Object.entries(assigns).filter(([k])=>decl[k]).map(([k,s])=>[k,s.size]).sort((a,b)=>b[1]-a[1]).slice(0,12),
 reachableFromFrame:reach.size,
 callSites:sites};
console.log(JSON.stringify(out,null,1));
