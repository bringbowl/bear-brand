// v6 - Network-first with cache cleanup & fast non-blocking save
self.addEventListener('install', (e) => {
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.map((k) => caches.delete(k)))).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const fetchOpts = e.request.mode === 'navigate' ? { cache: 'no-cache' } : {};
  e.respondWith(
    fetch(e.request, fetchOpts).catch(() => caches.match(e.request))
  );
});
