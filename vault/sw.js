self.addEventListener('install', (e) => {
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', (e) => {
  const fetchOpts = e.request.mode === 'navigate' ? { cache: 'no-cache' } : {};
  e.respondWith(
    fetch(e.request, fetchOpts).catch(() => caches.match(e.request))
  );
});
