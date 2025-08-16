// ApexAgent Frontend Optimization Module - Production Ready
class ApexAgentOptimizer {
    constructor() {
        this.cache = new Map();
        this.apiCache = new Map();
        this.observers = new Map();
        this.performanceMetrics = {
            loadTime: 0,
            apiCalls: 0,
            cacheHits: 0,
            renderTime: 0
        };
        this.init();
    }

    init() {
        this.setupServiceWorker();
        this.setupLazyLoading();
        this.setupAPIOptimization();
        this.setupPerformanceMonitoring();
        this.setupPreloading();
    }

    // Service Worker for Caching
    setupServiceWorker() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js').then(registration => {
                console.log('ServiceWorker registered:', registration);
            }).catch(error => {
                console.log('ServiceWorker registration failed:', error);
            });
        }
    }

    // Lazy Loading Implementation
    setupLazyLoading() {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    observer.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });

        // Lazy load tab content
        const tabObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const tabId = entry.target.dataset.tab;
                    if (tabId && !this.cache.has(tabId)) {
                        this.preloadTabContent(tabId);
                    }
                }
            });
        });

        document.querySelectorAll('[data-tab]').forEach(tab => {
            tabObserver.observe(tab);
        });
    }

    // API Optimization with Caching
    setupAPIOptimization() {
        this.originalFetch = window.fetch;
        window.fetch = this.optimizedFetch.bind(this);
    }

    async optimizedFetch(url, options = {}) {
        const cacheKey = `${url}_${JSON.stringify(options)}`;
        const cached = this.apiCache.get(cacheKey);
        
        if (cached && Date.now() - cached.timestamp < 60000) {
            this.performanceMetrics.cacheHits++;
            return Promise.resolve(new Response(JSON.stringify(cached.data), {
                status: 200,
                headers: { 'Content-Type': 'application/json' }
            }));
        }

        try {
            const response = await this.originalFetch(url, options);
            const data = await response.clone().json();
            
            this.apiCache.set(cacheKey, {
                data: data,
                timestamp: Date.now()
            });
            
            this.performanceMetrics.apiCalls++;
            return response;
        } catch (error) {
            console.error('API call failed:', error);
            throw error;
        }
    }

    // Performance Monitoring
    setupPerformanceMonitoring() {
        // Monitor page load time
        window.addEventListener('load', () => {
            this.performanceMetrics.loadTime = performance.now();
            this.reportPerformance();
        });

        // Monitor render time
        const renderObserver = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                if (entry.entryType === 'measure') {
                    this.performanceMetrics.renderTime = entry.duration;
                }
            }
        });
        renderObserver.observe({ entryTypes: ['measure'] });
    }

    // Preloading Critical Resources
    setupPreloading() {
        const criticalResources = [
            '/api/auth/status',
            '/api/system/status',
            '/api/dashboard/metrics'
        ];

        criticalResources.forEach(url => {
            this.preloadResource(url);
        });
    }

    async preloadResource(url) {
        try {
            const response = await fetch(url);
            const data = await response.json();
            this.apiCache.set(url, {
                data: data,
                timestamp: Date.now()
            });
        } catch (error) {
            console.warn('Preload failed for:', url);
        }
    }

    // Tab Content Preloading
    preloadTabContent(tabId) {
        const endpoints = {
            'dashboard': ['/api/dashboard/metrics', '/api/dashboard/activity'],
            'security': ['/api/security/status', '/api/security/logs'],
            'projects': ['/api/projects'],
            'analytics': ['/api/analytics/metrics']
        };

        if (endpoints[tabId]) {
            endpoints[tabId].forEach(url => this.preloadResource(url));
        }
    }

    // Bundle Optimization
    loadModuleAsync(moduleName) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = `/modules/${moduleName}.js`;
            script.onload = () => resolve();
            script.onerror = () => reject(new Error(`Failed to load ${moduleName}`));
            document.head.appendChild(script);
        });
    }

    // Performance Reporting
    reportPerformance() {
        const metrics = {
            ...this.performanceMetrics,
            timestamp: Date.now(),
            userAgent: navigator.userAgent,
            connection: navigator.connection?.effectiveType || 'unknown'
        };

        fetch('/api/performance/metrics', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(metrics)
        }).catch(error => console.warn('Performance reporting failed:', error));
    }

    // Memory Management
    clearCache() {
        this.apiCache.clear();
        this.cache.clear();
        console.log('Cache cleared');
    }

    // Get Performance Stats
    getStats() {
        return {
            ...this.performanceMetrics,
            cacheSize: this.apiCache.size,
            memoryUsage: performance.memory ? {
                used: performance.memory.usedJSHeapSize,
                total: performance.memory.totalJSHeapSize,
                limit: performance.memory.jsHeapSizeLimit
            } : null
        };
    }
}

// Real-time Data Manager
class RealTimeDataManager {
    constructor() {
        this.connections = new Map();
        this.updateIntervals = new Map();
        this.subscribers = new Map();
        this.init();
    }

    init() {
        this.setupPolling();
        this.setupWebSocket();
    }

    setupPolling() {
        const endpoints = [
            { url: '/api/system/status', interval: 30000, key: 'system' },
            { url: '/api/security/status', interval: 15000, key: 'security' },
            { url: '/api/dashboard/metrics', interval: 60000, key: 'dashboard' }
        ];

        endpoints.forEach(({ url, interval, key }) => {
            const intervalId = setInterval(async () => {
                try {
                    const response = await fetch(url);
                    const data = await response.json();
                    this.notifySubscribers(key, data);
                } catch (error) {
                    console.error(`Polling failed for ${key}:`, error);
                }
            }, interval);
            
            this.updateIntervals.set(key, intervalId);
        });
    }

    setupWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        try {
            const ws = new WebSocket(wsUrl);
            
            ws.onopen = () => {
                console.log('WebSocket connected');
                this.connections.set('main', ws);
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.notifySubscribers(data.type, data.payload);
            };
            
            ws.onclose = () => {
                console.log('WebSocket disconnected, attempting reconnect...');
                setTimeout(() => this.setupWebSocket(), 5000);
            };
        } catch (error) {
            console.warn('WebSocket not available, using polling only');
        }
    }

    subscribe(key, callback) {
        if (!this.subscribers.has(key)) {
            this.subscribers.set(key, new Set());
        }
        this.subscribers.get(key).add(callback);
    }

    unsubscribe(key, callback) {
        if (this.subscribers.has(key)) {
            this.subscribers.get(key).delete(callback);
        }
    }

    notifySubscribers(key, data) {
        if (this.subscribers.has(key)) {
            this.subscribers.get(key).forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error('Subscriber callback failed:', error);
                }
            });
        }
    }

    destroy() {
        this.updateIntervals.forEach(intervalId => clearInterval(intervalId));
        this.connections.forEach(ws => ws.close());
        this.updateIntervals.clear();
        this.connections.clear();
        this.subscribers.clear();
    }
}

// Enterprise UI Components
class EnterpriseUIManager {
    constructor() {
        this.components = new Map();
        this.themes = {
            dark: {
                primary: '#6B73FF',
                secondary: '#4A90E2',
                background: '#0A0E27',
                surface: '#1A1F3A',
                text: '#FFFFFF',
                textSecondary: '#B0BEC5'
            },
            light: {
                primary: '#6B73FF',
                secondary: '#4A90E2',
                background: '#FFFFFF',
                surface: '#F5F7FA',
                text: '#2C3E50',
                textSecondary: '#7F8C8D'
            }
        };
        this.currentTheme = 'dark';
        this.init();
    }

    init() {
        this.createExecutiveDashboard();
        this.createAdvancedAnalytics();
        this.setupThemeToggle();
        this.setupAccessibility();
    }

    createExecutiveDashboard() {
        const dashboard = document.createElement('div');
        dashboard.id = 'executive-dashboard';
        dashboard.className = 'executive-dashboard hidden';
        dashboard.innerHTML = `
            <div class="executive-header">
                <h2>Executive Dashboard</h2>
                <div class="time-range-selector">
                    <select id="timeRange">
                        <option value="24h">Last 24 Hours</option>
                        <option value="7d">Last 7 Days</option>
                        <option value="30d">Last 30 Days</option>
                        <option value="90d">Last 90 Days</option>
                    </select>
                </div>
            </div>
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-icon">📊</div>
                    <div class="kpi-content">
                        <h3>Total Revenue</h3>


