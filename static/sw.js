// Service Worker для PWA и офлайн режима
const CACHE_NAME = 'sportbash-v1';
const RUNTIME_CACHE = 'sportbash-runtime-v1';

// Ресурсы для кэширования при установке
const PRECACHE_URLS = [
    '/',
    '/static/css/main.css',
    '/static/js/main.js',
    '/static/js/toast.js',
    '/static/js/form-validation.js',
    '/offline/'
];

// Установка Service Worker
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                return cache.addAll(PRECACHE_URLS);
            })
            .then(() => {
                return self.skipWaiting();
            })
    );
});

// Активация Service Worker
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME && cacheName !== RUNTIME_CACHE) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
            .then(() => {
                return self.clients.claim();
            })
    );
});

// Перехват запросов
self.addEventListener('fetch', (event) => {
    // Пропускаем не-GET запросы
    if (event.request.method !== 'GET') {
        return;
    }
    
    // Пропускаем запросы к API (кроме публичных)
    if (event.request.url.includes('/api/') && 
        !event.request.url.includes('/api/organizations/') &&
        !event.request.url.includes('/api/events/') &&
        !event.request.url.includes('/api/core/')) {
        return;
    }
    
    event.respondWith(
        caches.match(event.request)
            .then((cachedResponse) => {
                // Возвращаем из кэша, если есть
                if (cachedResponse) {
                    return cachedResponse;
                }
                
                // Загружаем из сети
                return fetch(event.request)
                    .then((response) => {
                        // Клонируем ответ для кэширования
                        const responseToCache = response.clone();
                        
                        // Кэшируем успешные ответы
                        if (response.status === 200) {
                            caches.open(RUNTIME_CACHE)
                                .then((cache) => {
                                    cache.put(event.request, responseToCache);
                                });
                        }
                        
                        return response;
                    })
                    .catch(() => {
                        // Офлайн режим - возвращаем офлайн страницу
                        if (event.request.destination === 'document') {
                            return caches.match('/offline/');
                        }
                        
                        // Для других ресурсов возвращаем пустой ответ
                        return new Response('Офлайн', {
                            status: 503,
                            statusText: 'Service Unavailable'
                        });
                    });
            })
    );
});

// Фоновая синхронизация (если поддерживается)
self.addEventListener('sync', (event) => {
    if (event.tag === 'sync-favorites') {
        event.waitUntil(syncFavorites());
    }
});

function syncFavorites() {
    // Синхронизация избранного при восстановлении соединения
    return Promise.resolve();
}
