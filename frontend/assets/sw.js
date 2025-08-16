// ApexAgent Service Worker - Production Ready
const CACHE_NAME = 'apexagent-v1.0.0';
const STATIC_CACHE = 'apexagent-static-v1.0.0';
const API_CACHE = 'apexagent-api-v1.0.0';

const STATIC_ASSETS = [
    '/',
    '/index.html',
    '/optimized.js',
    '/enterprise.js'
];

const API_ENDPOINTS = [
    '/api/auth/status',
    '/api/system/status',
    '/api/dashboard/metrics',
    '/api/security/status',
    '/api/projects'
];

// Install event
self.addEventListener('install', event => {
    event.waitUntil(
        Promise.all([
            caches.open(STATIC_CACHE).then(cache => {
                return cache.addAll(STATIC_ASSETS);
            }),
            caches.open(API_CACHE)
        ]).then(() => {
            console.log('Service Worker installed and caches created');
            return self.skipWaiting();
        })
    );
});

// Activate event
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== STATIC_CACHE && cacheName !== API_CACHE) {
                        console.log('Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => {
            console.log('Service Worker activated');
            return self.clients.claim();
        })
    );
});

// Fetch event
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);

    // Handle API requests
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(handleAPIRequest(request));
        return;
    }

    // Handle static assets
    if (request.method === 'GET') {
        event.respondWith(handleStaticRequest(request));
        return;
    }
});

// Handle API requests with caching strategy
async function handleAPIRequest(request) {
    const url = new URL(request.url);
    const cache = await caches.open(API_CACHE);
    
    // For GET requests, try cache first
    if (request.method === 'GET') {
        const cachedResponse = await cache.match(request);
        
        if (cachedResponse) {
            const cacheTime = new Date(cachedResponse.headers.get('sw-cache-time'));
            const now = new Date();
            const maxAge = getMaxAge(url.pathname);
            
            if (now - cacheTime < maxAge) {
                console.log('Serving from API cache:', url.pathname);
                return cachedResponse;
            }
        }
    }

    try {
        const response = await fetch(request);
        
        if (response.ok && request.method === 'GET') {
            const responseClone = response.clone();
            const headers = new Headers(responseClone.headers);
            headers.set('sw-cache-time', new Date().toISOString());
            
            const cachedResponse = new Response(await responseClone.blob(), {
                status: responseClone.status,
                statusText: responseClone.statusText,
                headers: headers
            });
            
            cache.put(request, cachedResponse);
            console.log('Cached API response:', url.pathname);
        }
        
        return response;
    } catch (error) {
        console.error('API request failed:', error);
        
        // Return cached version if available
        const cachedResponse = await cache.match(request);
        if (cachedResponse) {
            console.log('Serving stale cache due to network error:', url.pathname);
            return cachedResponse;
        }
        
        throw error;
    }
}

// Handle static asset requests
async function handleStaticRequest(request) {
    const cache = await caches.open(STATIC_CACHE);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
        console.log('Serving from static cache:', request.url);
        return cachedResponse;
    }
    
    try {
        const response = await fetch(request);
        
        if (response.ok) {
            cache.put(request, response.clone());
            console.log('Cached static asset:', request.url);
        }
        
        return response;
    } catch (error) {
        console.error('Static request failed:', error);
        throw error;
    }
}

// Get cache max age for different endpoints
function getMaxAge(pathname) {
    const cacheConfig = {
        '/api/auth/status': 5 * 60 * 1000,      // 5 minutes
        '/api/system/status': 30 * 1000,        // 30 seconds
        '/api/dashboard/metrics': 60 * 1000,    // 1 minute
        '/api/security/status': 15 * 1000,      // 15 seconds
        '/api/projects': 5 * 60 * 1000,         // 5 minutes
        'default': 60 * 1000                    // 1 minute default
    };
    
    return cacheConfig[pathname] || cacheConfig.default;
}

// Background sync for offline actions
self.addEventListener('sync', event => {
    if (event.tag === 'background-sync') {
        event.waitUntil(doBackgroundSync());
    }
});

async function doBackgroundSync() {
    try {
        const cache = await caches.open(API_CACHE);
        const requests = await cache.keys();
        
        for (const request of requests) {
            try {
                const response = await fetch(request);
                if (response.ok) {
                    await cache.put(request, response);
                }
            } catch (error) {
                console.warn('Background sync failed for:', request.url);
            }
        }
        
        console.log('Background sync completed');
    } catch (error) {
        console.error('Background sync error:', error);
    }
}

// Push notifications
self.addEventListener('push', event => {
    if (event.data) {
        const data = event.data.json();
        const options = {
            body: data.body,
            icon: '/icon-192x192.png',
            badge: '/badge-72x72.png',
            tag: data.tag || 'apexagent-notification',
            requireInteraction: data.requireInteraction || false,
            actions: data.actions || []
        };
        
        event.waitUntil(
            self.registration.showNotification(data.title, options)
        );
    }
});

// Notification click handling
self.addEventListener('notificationclick', event => {
    event.notification.close();
    
    if (event.action === 'open-dashboard') {
        event.waitUntil(
            clients.openWindow('/?tab=dashboard')
        );
    } else if (event.action === 'open-security') {
        event.waitUntil(
            clients.openWindow('/?tab=security')
        );
    } else {
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

// Performance monitoring
self.addEventListener('message', event => {
    if (event.data && event.data.type === 'PERFORMANCE_REPORT') {
        console.log('Performance metrics:', event.data.metrics);
        
        // Send to analytics endpoint
        fetch('/api/analytics/performance', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(event.data.metrics)
        }).catch(error => {
            console.warn('Performance reporting failed:', error);
        });
    }
});

console.log('ApexAgent Service Worker loaded successfully');

