const CACHE_NAME = 'niro-cache-v13-FIX-CRITICAL-FORCE-NETWORK';
const urlsToCache = [
  '/manifest.json',
  '/Niro_original.png',
  'https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css',
  'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Outfit:wght@500;700;800&display=swap'
];

self.addEventListener('install', event => {
  self.skipWaiting(); // Forzar activación inmediata
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim()) // Tomar control de inmediato
  );
});

self.addEventListener('fetch', event => {
  // ESTRATEGIA: NETWORK FIRST para HTML y navegación
  if (event.request.mode === 'navigate' || event.request.destination === 'document') {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          return response;
        })
        .catch(() => {
          return caches.match(event.request);
        })
    );
    return;
  }

  // ESTRATEGIA: CACHE FIRST para recursos estáticos
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});