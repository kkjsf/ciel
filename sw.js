// Le nom du cache derive du ?v= avec lequel index.html enregistre ce worker (APP_VERSION) :
// une seule source de version pour toute l'app.
const VERSION = new URL(self.location.href).searchParams.get('v') || 'dev';
const PREFIX = 'ciel-';
const CACHE = PREFIX + 'v' + VERSION;
const ASSETS = ['./', './index.html', './manifest.json', './icons/icon.svg', './icons/icon-192.png', './icons/icon-512.png', './icons/icon-maskable-512.png'];

self.addEventListener('install', e => {
  // cache: 'reload' sinon le precache peut reprendre l'ancienne version dans le cache HTTP
  e.waitUntil(caches.open(CACHE).then(c => Promise.all(
    ASSETS.map(u => c.add(new Request(u, { cache: 'reload' })).catch(() => console.warn('[sw] precache ignore', u)))
  )));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  // Ne supprimer que NOS anciens caches : l'origine github.io est partagee avec les autres apps.
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k.startsWith(PREFIX) && k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;
  // Page : reseau d'abord (les mises a jour arrivent tout de suite), cache si hors ligne.
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req, { cache: 'no-cache' }).then(r => {
      if (r.ok) { const copy = r.clone(); caches.open(CACHE).then(c => c.put('./index.html', copy)); }
      return r;
    }).catch(() => caches.match('./index.html', { cacheName: CACHE })));
    return;
  }
  e.respondWith(caches.match(req, { cacheName: CACHE, ignoreSearch: true }).then(hit => hit || fetch(req)));
});
