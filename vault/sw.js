// v9 - Ultra-fast X-Engine direct thumbnail extraction + Pinterest Pidgets API + prevent background rate-limit exhaustion
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
