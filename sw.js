const CACHE = 'facharzt-krk-v7';
const ASSETS = ['./', './index.html', './manifest.webmanifest', './icon.svg', './data/questions.json', './data/meta.json', './data/taxonomie.json'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);
  // network-first für die App-HTML, Navigation und alle Daten -> Updates erscheinen
  // sofort beim Reload (online). Offline: Fallback auf den Cache.
  const networkFirst =
    e.request.mode === 'navigate' ||
    url.pathname.endsWith('/') ||
    url.pathname.endsWith('/index.html') ||
    url.pathname.endsWith('.json');
  if (networkFirst) {
    e.respondWith(
      fetch(e.request).then((res) => {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(e.request, copy));
        return res;
      }).catch(() => caches.match(e.request).then((h) => h || caches.match('./index.html')))
    );
    return;
  }
  // statische Assets (Icon, Manifest): cache-first
  e.respondWith(caches.match(e.request).then((hit) => hit || fetch(e.request)));
});
