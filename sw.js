// Le nom du cache derive du ?v= avec lequel index.html enregistre ce worker (APP_VERSION) :
// une seule source de version pour toute l'app.
const VERSION = new URL(self.location.href).searchParams.get('v') || 'dev';
const PREFIX = 'ciel-';
const CACHE = PREFIX + 'v' + VERSION;
const SETTINGS = PREFIX + 'reglages';
const ASSETS = ['./', './index.html', './manifest.json', './icons/icon.svg', './icons/icon-192.png', './icons/icon-512.png', './icons/icon-maskable-512.png'];

self.addEventListener('install', e => {
  // cache: 'reload' sinon le precache peut reprendre l'ancienne version dans le cache HTTP
  e.waitUntil(caches.open(CACHE).then(c => Promise.all(
    ASSETS.map(u => c.add(new Request(u, { cache: 'reload' })).catch(() => console.warn('[sw] precache ignore', u)))
  )));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  // Ne supprimer que NOS anciens caches (l'origine github.io est partagee), et jamais les reglages.
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k.startsWith(PREFIX) && k !== CACHE && k !== SETTINGS).map(k => caches.delete(k))))
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

/* ---------- alerte gel ---------- */
// Le worker n'a pas acces au localStorage : le lieu surveille vit dans un cache a part.
const KEY = './reglages.json';
async function readSettings() {
  const r = await (await caches.open(SETTINGS)).match(KEY);
  return r ? r.json() : {};
}
async function writeSettings(s) {
  await (await caches.open(SETTINGS)).put(KEY, new Response(JSON.stringify(s), { headers: { 'Content-Type': 'application/json' } }));
}
const fKey = new Intl.DateTimeFormat('en-CA', { timeZone: 'Europe/Paris', year: 'numeric', month: '2-digit', day: '2-digit' });
const fHour = new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/Paris', hour: 'numeric', hourCycle: 'h23' });
const fWd = new Intl.DateTimeFormat('fr-FR', { timeZone: 'Europe/Paris', weekday: 'long' });
const hourOf = t => +fHour.format(t);
const deg = v => `${Math.round(v) + 0}°`.replace('-', '−');

// La nuit qui compte : celle qui finit le matin du jour (now + 18 h), de 18 h la veille a 10 h.
// Memes seuils que la carte Gel de l'app, sans la probabilite ensemble (une seule requete legere ici).
async function frostCheck(test) {
  const s = await readSettings(), p = s.alert;
  if (!p) return;
  const url = `https://api.open-meteo.com/v1/forecast?latitude=${p.lat}&longitude=${p.lon}&timezone=Europe%2FParis&timeformat=unixtime`
    + '&forecast_days=3&hourly=temperature_2m,cloud_cover,wind_speed_10m&models=meteofrance_seamless';
  const h = (await (await fetch(url)).json()).hourly, now = Date.now(), morning = fKey.format(now + 18 * 3600e3);
  const night = h.time.map((x, i) => [x * 1000, i]).filter(([t]) => {
    const k = fKey.format(t), hr = hourOf(t);
    return t >= now - 3600e3 && ((k === morning && hr <= 10) || (k === fKey.format(Date.parse(morning + 'T12:00:00Z') - 864e5) && hr >= 18));
  }).map(([, i]) => i).filter(i => h.temperature_2m[i] != null);
  if (!night.length) return;
  const tmin = Math.min(...night.map(i => h.temperature_2m[i]));
  const core = night.filter(i => { const hr = hourOf(h.time[i] * 1000); return hr >= 22 || hr <= 7; });
  const avg = a => a.reduce((x, y) => x + y, 0) / a.length;
  const clearCalm = core.length > 0 && avg(core.map(i => h.cloud_cover[i] ?? 100)) < 40 && avg(core.map(i => h.wind_speed_10m[i] ?? 99)) < 10;
  const level = tmin <= -5 ? 'Gel fort' : tmin <= 0 ? 'Gel' : tmin <= 3 && clearCalm ? 'Gelée blanche possible' : null;
  const coldest = night.reduce((a, i) => h.temperature_2m[i] < h.temperature_2m[a] ? i : a);
  const when = `${hourOf(h.time[coldest] * 1000)}h`;
  const nightName = `la nuit de ${fWd.format(Date.parse(morning + 'T12:00:00Z') - 864e5)} à ${fWd.format(Date.parse(morning + 'T12:00:00Z'))}`;
  if (!test && (!level || s.notified === morning + p.name)) return;
  const title = level ? `${level} ${nightName}` : `Test : pas de gel ${nightName}`;
  const body = `${p.name} : ${deg(tmin)} vers ${when}${clearCalm ? ', nuit claire et calme' : ''}.${level && tmin > 0 ? ' Le sol peut descendre sous zéro.' : ''}`;
  await self.registration.showNotification(title, {
    body, icon: 'icons/icon-192.png', badge: 'icons/icon-192.png', tag: 'gel-' + morning, lang: 'fr',
    data: { url: `./#l=${p.lat.toFixed(4)},${p.lon.toFixed(4)}&n=${encodeURIComponent(p.name)}` },
  });
  if (!test) await writeSettings({ ...s, notified: morning + p.name });
}

self.addEventListener('periodicsync', e => { if (e.tag === 'gel') e.waitUntil(frostCheck(false)); });
self.addEventListener('message', e => {
  const m = e.data || {};
  if (m.type === 'gel-config') e.waitUntil(readSettings().then(s => writeSettings({ ...s, alert: m.alert, notified: null })));
  if (m.type === 'gel-test') e.waitUntil(frostCheck(true));
});
self.addEventListener('notificationclick', e => {
  e.notification.close();
  e.waitUntil(self.clients.openWindow(e.notification.data.url));
});
