/* Jill's Kitchen service worker.
   Shell files are fetched from the network first (so an update is never missed while online) and answered from
   the cache only when the network fails or stalls (so the home-screen app still opens offline). Everything that
   is not part of the shell is passed through. Saves live in localStorage/IndexedDB and are never touched here.
   Bump CACHE when shipping a new build; old caches are deleted on activate. */
const CACHE='jills-kitchen-v2.0';
const SHELL=['./','./index.html','./css/style.css','./js/game.js','./manifest.webmanifest','./icons/icon-192.png','./icons/icon-512.png','./icons/apple-touch-icon.png'];
const NET_TIMEOUT=4000;
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener('message',e=>{if(e.data==='skipWaiting')self.skipWaiting()});
function withTimeout(p,ms){return new Promise((res,rej)=>{const t=setTimeout(()=>rej(new Error('timeout')),ms);p.then(v=>{clearTimeout(t);res(v)},e=>{clearTimeout(t);rej(e)})})}
self.addEventListener('fetch',e=>{const u=new URL(e.request.url);if(e.request.method!=='GET'||u.origin!==location.origin)return;
 const isShell=e.request.mode==='navigate'||SHELL.some(p=>u.pathname.endsWith(p.replace('./','/'))||u.pathname.endsWith(p.slice(2)));
 if(!isShell)return;
 e.respondWith(withTimeout(fetch(e.request),NET_TIMEOUT).then(res=>{if(res&&res.ok){const copy=res.clone();caches.open(CACHE).then(c=>c.put(e.request,copy))}return res})
  .catch(()=>caches.match(e.request,{ignoreSearch:true}).then(hit=>hit||(e.request.mode==='navigate'?caches.match('./index.html'):undefined))))});
