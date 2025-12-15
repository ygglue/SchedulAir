const STATIC_CACHE = 'schedulair-static-v1';
const CDN_CACHE = 'schedulair-cdn-v1';

const PAGES_TO_CACHE = [
    '/home',
    '/editor',
    '/account',
    '/static/css/bootstrap.min.css',
    '/static/css/styles.css',
    '/static/js/bootstrap.bundle.min.js',
    '/static/js/scripts.js',
    '/static/js/account.js',
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(STATIC_CACHE).then(cache =>
            cache.addAll(PAGES_TO_CACHE)
        )
    );
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(
                keys
                    .filter(k => ![STATIC_CACHE, CDN_CACHE].includes(k))
                    .map(k => caches.delete(k))
            )
        )
    );
});

self.addEventListener('fetch', event => {
    const request = event.request;

    // Only GET requests
    if (request.method !== 'GET') return;

    const url = new URL(request.url);

    // 🔹 CDN assets (Bootstrap Icons, fonts, etc.)
    if (url.hostname === 'cdn.jsdelivr.net') {
        event.respondWith(
            caches.open(CDN_CACHE).then(cache =>
                fetch(request)
                    .then(response => {
                        cache.put(request, response.clone());
                        return response;
                    })
                    .catch(() => caches.match(request))
            )
        );
        return;
    }

    // 🔹 HTML pages (network-first)
    if (['/home', '/editor', '/account'].includes(url.pathname)) {
        event.respondWith(
            fetch(request)
                .then(response => {
                    const clone = response.clone();
                    caches.open(STATIC_CACHE).then(cache => cache.put(request, clone));
                    return response;
                })
                .catch(() => caches.match(request))
        );
        return;
    }

    // 🔹 Static CSS/JS (cache-first)
    if (PAGES_TO_CACHE.includes(url.pathname)) {
        event.respondWith(
            caches.match(request).then(response => response || fetch(request))
        );
        return;
    }

    // 🔹 All other requests: fetch normally
});
