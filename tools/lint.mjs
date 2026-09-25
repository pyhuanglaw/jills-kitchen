// ESLint pass with correctness rules only (no style rules). Dev tool.
import {createRequire} from 'module';
const require=createRequire(import.meta.url);
const tryReq=m=>{for(const p of ['/opt/node22/lib/node_modules/','/opt/node-tools/node_modules/','']){try{return require(p+m)}catch(e){}}throw new Error('missing '+m)};
const {Linter}=tryReq('eslint');
import fs from 'fs';
const file=process.argv[2]||new URL('../js/game.js',import.meta.url).pathname;
const code=fs.readFileSync(file,'utf8');
const browser=['window','document','localStorage','performance','requestAnimationFrame','setTimeout','setInterval','clearTimeout','clearInterval','console','navigator','location','AudioContext','Math','JSON','Date','Object','Array','Set','Map','Number','String','Boolean','Error','Promise','Symbol','parseInt','parseFloat','isNaN','Infinity','NaN','undefined','Image','HTMLCanvasElement','CanvasRenderingContext2D','Intl','structuredClone','getComputedStyle','matchMedia','EventTarget'];
const globals=Object.fromEntries(browser.map(g=>[g,'readonly']));
const linter=new Linter({configType:'flat'});
const msgs=linter.verify(code,[{languageOptions:{ecmaVersion:'latest',sourceType:'script',globals},rules:{
 'no-undef':'error','no-unused-vars':['warn',{vars:'all',args:'none',caughtErrors:'none'}],'no-redeclare':'error','no-dupe-keys':'error','no-duplicate-case':'error','no-self-assign':'error','no-unreachable':'error','no-func-assign':'error','no-const-assign':'error','no-dupe-else-if':'error','no-constant-condition':['warn',{checkLoops:false}],'no-shadow-restricted-names':'error','no-use-before-define':'off','no-fallthrough':'warn','no-empty':'off','no-cond-assign':'warn','no-unsafe-finally':'error','no-sparse-arrays':'warn','use-isnan':'error','valid-typeof':'error'}}]);
const by={};for(const m of msgs){(by[m.ruleId]=by[m.ruleId]||[]).push(`${m.line}:${m.column} ${m.message}`)}
for(const [r,l] of Object.entries(by)){console.log(`== ${r} (${l.length})`);for(const x of l.slice(0,60))console.log('  '+x)}
console.log('TOTAL',msgs.length,'errors',msgs.filter(m=>m.severity===2).length);
