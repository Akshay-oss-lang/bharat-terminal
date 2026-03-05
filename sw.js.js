// ════════════════════════════════════════════════════════════
//  BHARAT TERMINAL PRO — SERVICE WORKER
//  Enables: offline use, fast loading, background updates
//  Version: bump CACHE_VERSION to force update all users
// ════════════════════════════════════════════════════════════

const CACHE_VERSION = 'bharat-v1.0.0';
const STATIC_CACHE  = `${CACHE_VERSION}-static`;
const DATA_CACHE    = `${CACHE_VERSION}-data`;

// Files to cache on install (app shell)
const STATIC_FILES = [
  '/',
  '/index.html',
  '/manifest.json',
  '/icons/icon-192.png',
  '/icons/icon-512.png',
  // Google Fonts — cache for offline use
  'https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700;800&family=Barlow+Condensed:wght@300;400;500;600;700;800&display=swap'
];

// ── INSTALL: Cache static assets ──
self.addEventListener('install', event => {
  console.log('[SW] Installing BharatTerminal PWA...');
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => {
        console.log('[SW] Caching static shell');
        // Cache files individually so one failure doesn't break all
        return Promise.allSettled(
          STATIC_FILES.map(url => cache.add(url).catch(e => console.warn('[SW] Failed to cache:', url, e)))
        );
      })
      .then(() => self.skipWaiting()) // Activate immediately
  );
});

// ── ACTIVATE: Clean old caches ──
self.addEventListener('activate', event => {
  console.log('[SW] Activating new service worker...');
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys.filter(k => !k.startsWith(CACHE_VERSION))
            .map(k => { console.log('[SW] Deleting old cache:', k); return caches.delete(k); })
      ))
      .then(() => self.clients.claim()) // Take control of all tabs
  );
});

// ── FETCH: Network-first for API, Cache-first for assets ──
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // Skip chrome-extension and non-http requests
  if (!event.request.url.startsWith('http')) return;

  // Anthropic API — always network, never cache (security)
  if (url.hostname === 'api.anthropic.com') {
    event.respondWith(fetch(event.request));
    return;
  }

  // External data APIs (Yahoo Finance, NSE, etc.) — network first, cache fallback
  if (url.hostname.includes('yahoo') ||
      url.hostname.includes('nseindia') ||
      url.hostname.includes('bseindia') ||
      url.hostname.includes('stooq') ||
      url.hostname.includes('alphavantage')) {
    event.respondWith(
      fetch(event.request)
        .then(res => {
          // Clone and cache successful responses
          if (res.ok) {
            const clone = res.clone();
            caches.open(DATA_CACHE).then(cache => cache.put(event.request, clone));
          }
          return res;
        })
        .catch(() => {
          // Offline — serve cached data
          return caches.match(event.request)
            .then(cached => cached || new Response(
              JSON.stringify({ error: 'offline', message: 'No cached data available' }),
              { headers: { 'Content-Type': 'application/json' } }
            ));
        })
    );
    return;
  }

  // App shell (HTML, CSS, fonts, icons) — cache first, network fallback
  event.respondWith(
    caches.match(event.request)
      .then(cached => {
        if (cached) return cached;
        return fetch(event.request)
          .then(res => {
            if (res.ok && event.request.method === 'GET') {
              const clone = res.clone();
              caches.open(STATIC_CACHE).then(cache => cache.put(event.request, clone));
            }
            return res;
          })
          .catch(() => {
            // Return offline page for navigation requests
            if (event.request.mode === 'navigate') {
              return caches.match('/index.html');
            }
          });
      })
  );
});

// ── BACKGROUND SYNC: Queue AI queries when offline ──
self.addEventListener('sync', event => {
  if (event.tag === 'sync-market-data') {
    console.log('[SW] Background sync: market data');
    event.waitUntil(syncMarketData());
  }
});

async function syncMarketData() {
  // When back online, notify the app to refresh
  const clients = await self.clients.matchAll();
  clients.forEach(client => {
    client.postMessage({ type: 'MARKET_SYNC', timestamp: Date.now() });
  });
}

// ── PUSH NOTIFICATIONS: Market alerts ──
self.addEventListener('push', event => {
  if (!event.data) return;
  const data = event.data.json();
  const options = {
    body: data.body || 'New market alert',
    icon: '/icons/icon-192.png',
    badge: '/icons/icon-72.png',
    tag: data.tag || 'market-alert',
    renotify: true,
    vibrate: [200, 100, 200],
    data: { url: data.url || '/', timestamp: Date.now() },
    actions: [
      { action: 'view',    title: '📈 View', icon: '/icons/icon-72.png' },
      { action: 'dismiss', title: '✕ Dismiss' }
    ]
  };
  event.waitUntil(
    self.registration.showNotification(data.title || 'BharatTerminal Alert', options)
  );
});

// Handle notification click
self.addEventListener('notificationclick', event => {
  event.notification.close();
  if (event.action === 'view' || !event.action) {
    event.waitUntil(
      self.clients.matchAll({ type: 'window' }).then(clients => {
        if (clients.length > 0) {
          clients[0].focus();
          clients[0].navigate(event.notification.data.url);
        } else {
          self.clients.openWindow(event.notification.data.url);
        }
      })
    );
  }
});

// ── MESSAGE HANDLER: From main app ──
self.addEventListener('message', event => {
  if (event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  if (event.data.type === 'GET_VERSION') {
    event.ports[0].postMessage({ version: CACHE_VERSION });
  }
});

console.log('[SW] BharatTerminal PRO Service Worker loaded. Version:', CACHE_VERSION);
