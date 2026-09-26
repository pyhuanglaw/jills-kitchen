/* Jill's Kitchen service worker: the app shell is cached on install so the home-screen app opens offline;
   requests for the shell are answered from the cache first and refreshed in the background. Saves live in
   localStorage/IndexedDB and are not touched here. Bump CACHE when shipping a new build. */
const CACHE='jills-kitchen-v18.1';
const SHELL=['./','./index.html','./css/style.css','./js/game.js','./manifest.webmanifest','./icons/icon-192.png','./icons/icon-512.png','./icons/apple-touch-icon.png'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{const u=new URL(e.request.url);if(e.request.method!=='GET'||u.origin!==location.origin)return;
 e.respondWith(caches.match(e.request,{ignoreSearch:true}).then(hit=>{const net=fetch(e.request).then(res=>{if(res&&res.ok){const copy=res.clone();caches.open(CACHE).then(c=>c.put(e.request,copy))}return res}).catch(()=>hit);return hit||net}))});
