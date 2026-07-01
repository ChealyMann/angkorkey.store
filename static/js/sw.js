const CACHE_NAME = 'angkorkey-cache-v2';
const ASSETS_TO_CACHE = [
  '/',
  '/home',
  '/products',
  '/promotions',
  '/categories',
  '/cart',
  'https://cdn.tailwindcss.com',
  'https://cdn.jsdelivr.net/npm/lucide@0.469.0/dist/umd/lucide.min.js',
  'https://flagcdn.com/24x18/gb.png',
  'https://flagcdn.com/24x18/kh.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      const localAssets = ASSETS_TO_CACHE.filter(url => !url.startsWith('http') || url.includes(self.location.hostname));
      const crossOriginAssets = ASSETS_TO_CACHE.filter(url => url.startsWith('http') && !url.includes(self.location.hostname));

      return cache.addAll(localAssets).then(() => {
        const promises = crossOriginAssets.map(url => {
          return fetch(new Request(url, { mode: 'no-cors' }))
            .then(response => cache.put(url, response))
            .catch(err => console.warn('Failed to pre-cache cross-origin asset:', url, err));
        });
        return Promise.all(promises);
      });
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);
  if (url.protocol !== 'http:' && url.protocol !== 'https:') return;

  // Cache-first for static assets
  const isStaticAsset = 
    url.origin === self.location.origin && url.pathname.startsWith('/static/') ||
    url.hostname.includes('cdn.tailwindcss.com') ||
    url.hostname.includes('jsdelivr.net') ||
    url.hostname.includes('fonts.gstatic.com') ||
    url.hostname.includes('fonts.googleapis.com') ||
    url.hostname.includes('flagcdn.com');

  if (isStaticAsset) {
    event.respondWith(
      caches.match(event.request).then((cachedResponse) => {
        if (cachedResponse) {
          return cachedResponse;
        }
        return fetch(event.request).then((networkResponse) => {
          if (networkResponse && (networkResponse.status === 200 || networkResponse.status === 0)) {
            const responseToCache = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, responseToCache);
            });
          }
          return networkResponse;
        });
      })
    );
  } else {
    // Network-first with 10-second timeout fallback to cache for dynamic content (F5/refreshes)
    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => reject(new Error('Network timeout')), 10000);
    });

    event.respondWith(
      Promise.race([fetch(event.request), timeoutPromise])
        .then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const responseToCache = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, responseToCache);
            });
          }
          return networkResponse;
        })
        .catch(() => {
          // If network is completely offline OR takes longer than 2 seconds, load instantly from cache
          return caches.match(event.request);
        })
    );
  }
});
