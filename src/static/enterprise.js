// ApexAgent Enterprise Features - Production Ready
class EnterpriseFeatures {
    constructor() {
        this.analytics = new AdvancedAnalytics();
        this.dashboard = new ExecutiveDashboard();
        this.security = new SecurityMonitor();
        this.collaboration = new TeamCollaboration();
        this.init();
    }

    init() {
        this.setupEnterpriseAuth();
        this.setupAdvancedFeatures();
        this.setupRealTimeUpdates();
    }

    setupEnterpriseAuth() {
        // Multi-factor authentication UI
        const mfaModal = document.createElement('div');
        mfaModal.id = 'mfa-modal';
        mfaModal.className = 'modal hidden';
        mfaModal.innerHTML = `
            <div class="modal-content">
                <h3>Multi-Factor Authentication</h3>
                <div class="mfa-methods">
                    <button class="mfa-method" data-method="totp">
                        <span class="icon">📱</span>
                        Authenticator App
                    </button>
                    <button class="mfa-method" data-method="sms">
                        <span class="icon">💬</span>
                        SMS Code
                    </button>
                    <button class="mfa-method" data-method="webauthn">
                        <span class="icon">🔐</span>
                        Security Key
                    </button>
                </div>
                <div class="mfa-input hidden">
                    <input type="text" id="mfa-code" placeholder="Enter verification code">
                    <button id="verify-mfa">Verify</button>
                </div>
            </div>
        `;
        document.body.appendChild(mfaModal);

        // SSO integration
        this.setupSSO();
    }

    setupSSO() {
        const ssoProviders = ['google', 'microsoft', 'github', 'okta'];
        const ssoContainer = document.createElement('div');
        ssoContainer.className = 'sso-providers';
        
        ssoProviders.forEach(provider => {
            const button = document.createElement('button');
            button.className = `sso-button sso-${provider}`;
            button.innerHTML = `
                <img src="/icons/${provider}.svg" alt="${provider}">
                Continue with ${provider.charAt(0).toUpperCase() + provider.slice(1)}
            `;
            button.onclick = () => this.initiateSSOLogin(provider);
            ssoContainer.appendChild(button);
        });

        const loginForm = document.querySelector('.login-form');
        if (loginForm) {
            loginForm.appendChild(ssoContainer);
        }
    }

    async initiateSSOLogin(provider) {
        try {
            const response = await fetch(`/api/auth/sso/${provider}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();
            
            if (data.redirectUrl) {
                window.location.href = data.redirectUrl;
            }
        } catch (error) {
            console.error('SSO login failed:', error);
            this.showNotification('SSO login failed. Please try again.', 'error');
        }
    }

    setupAdvancedFeatures() {
        this.createAdvancedSearch();
        this.createBulkOperations();
        this.createCustomReports();
        this.createAPIKeyManager();
    }

    createAdvancedSearch() {
        const searchContainer = document.createElement('div');
        searchContainer.className = 'advanced-search';
        searchContainer.innerHTML = `
            <div class="search-header">
                <input type="text" id="global-search" placeholder="Search across all modules...">
                <button id="search-filters">🔍 Filters</button>
            </div>
            <div class="search-filters hidden">
                <div class="filter-group">
                    <label>Module:</label>
                    <select id="module-filter">
                        <option value="">All Modules</option>
                        <option value="projects">Projects</option>
                        <option value="agents">Agents</option>
                        <option value="security">Security</option>
                        <option value="analytics">Analytics</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Date Range:</label>
                    <input type="date" id="date-from">
                    <input type="date" id="date-to">
                </div>
                <div class="filter-group">
                    <label>Status:</label>
                    <select id="status-filter">
                        <option value="">All Status</option>
                        <option value="active">Active</option>
                        <option value="completed">Completed</option>
                        <option value="pending">Pending</option>
                    </select>
                </div>
            </div>
            <div class="search-results"></div>
        `;

        document.querySelector('.header-content').appendChild(searchContainer);
        this.setupSearchFunctionality();
    }

    setupSearchFunctionality() {
        const searchInput = document.getElementById('global-search');
        const searchResults = document.querySelector('.search-results');
        let searchTimeout;

        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.performSearch(e.target.value);
            }, 300);
        });

        document.getElementById('search-filters').addEventListener('click', () => {
            document.querySelector('.search-filters').classList.toggle('hidden');
        });
    }

    async performSearch(query) {
        if (query.length < 2) return;

        try {
            const filters = {
                module: document.getElementById('module-filter').value,
                dateFrom: document.getElementById('date-from').value,
                dateTo: document.getElementById('date-to').value,
                status: document.getElementById('status-filter').value
            };

            const response = await fetch('/api/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, filters })
            });

            const results = await response.json();
            this.displaySearchResults(results);
        } catch (error) {
            console.error('Search failed:', error);
        }
    }

    displaySearchResults(results) {
        const container = document.querySelector('.search-results');
        container.innerHTML = '';

        if (results.length === 0) {
            container.innerHTML = '<div class="no-results">No results found</div>';
            return;
        }

        results.forEach(result => {
            const item = document.createElement('div');
            item.className = 'search-result-item';
            item.innerHTML = `
                <div class="result-header">
                    <span class="result-type">${result.type}</span>
                    <span class="result-title">${result.title}</span>
                </div>
                <div class="result-content">${result.excerpt}</div>
                <div class="result-meta">
                    <span class="result-date">${new Date(result.date).toLocaleDateString()}</span>
                    <span class="result-module">${result.module}</span>
                </div>
            `;
            item.onclick = () => this.navigateToResult(result);
            container.appendChild(item);
        });
    }

    createBulkOperations() {
        const bulkToolbar = document.createElement('div');
        bulkToolbar.className = 'bulk-operations hidden';
        bulkToolbar.innerHTML = `
            <div class="bulk-info">
                <span id="selected-count">0</span> items selected
            </div>
            <div class="bulk-actions">
                <button id="bulk-export">📤 Export</button>
                <button id="bulk-archive">📦 Archive</button>
                <button id="bulk-delete">🗑️ Delete</button>
                <button id="bulk-assign">👥 Assign</button>
            </div>
        `;

        document.body.appendChild(bulkToolbar);
        this.setupBulkOperations();
    }

    setupBulkOperations() {
        let selectedItems = new Set();

        document.addEventListener('change', (e) => {
            if (e.target.type === 'checkbox' && e.target.classList.contains('item-select')) {
                if (e.target.checked) {
                    selectedItems.add(e.target.value);
                } else {
                    selectedItems.delete(e.target.value);
                }
                this.updateBulkToolbar(selectedItems.size);
            }
        });

        document.getElementById('bulk-export').addEventListener('click', () => {
            this.exportItems(Array.from(selectedItems));
        });

        document.getElementById('bulk-delete').addEventListener('click', () => {
            this.deleteItems(Array.from(selectedItems));
        });
    }

    updateBulkToolbar(count) {
        const toolbar = document.querySelector('.bulk-operations');
        const countElement = document.getElementById('selected-count');
        
        if (count > 0) {
            toolbar.classList.remove('hidden');
            countElement.textContent = count;
        } else {
            toolbar.classList.add('hidden');
        }
    }

    createCustomReports() {
        const reportBuilder = document.createElement('div');
        reportBuilder.id = 'report-builder';
        reportBuilder.className = 'modal hidden';
        reportBuilder.innerHTML = `
            <div class="modal-content large">
                <div class="modal-header">
                    <h3>Custom Report Builder</h3>
                    <button class="close-modal">×</button>
                </div>
                <div class="report-builder-content">
                    <div class="report-config">
                        <div class="config-section">
                            <h4>Data Source</h4>
                            <select id="report-source">
                                <option value="projects">Projects</option>
                                <option value="agents">Agents</option>
                                <option value="security">Security Events</option>
                                <option value="performance">Performance Metrics</option>
                            </select>
                        </div>
                        <div class="config-section">
                            <h4>Metrics</h4>
                            <div class="metric-checkboxes">
                                <label><input type="checkbox" value="count"> Count</label>
                                <label><input type="checkbox" value="avg"> Average</label>
                                <label><input type="checkbox" value="sum"> Sum</label>
                                <label><input type="checkbox" value="trend"> Trend</label>
                            </div>
                        </div>
                        <div class="config-section">
                            <h4>Time Range</h4>
                            <select id="report-timerange">
                                <option value="24h">Last 24 Hours</option>
                                <option value="7d">Last 7 Days</option>
                                <option value="30d">Last 30 Days</option>
                                <option value="90d">Last 90 Days</option>
                                <option value="custom">Custom Range</option>
                            </select>
                        </div>
                        <div class="config-section">
                            <h4>Visualization</h4>
                            <select id="report-chart">
                                <option value="line">Line Chart</option>
                                <option value="bar">Bar Chart</option>
                                <option value="pie">Pie Chart</option>
                                <option value="table">Data Table</option>
                            </select>
                        </div>
                    </div>
                    <div class="report-preview">
                        <div id="chart-container"></div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button id="generate-report">Generate Report</button>
                    <button id="save-report">Save Template</button>
                    <button id="schedule-report">Schedule</button>
                </div>
            </div>
        `;

        document.body.appendChild(reportBuilder);
        this.setupReportBuilder();
    }

    setupReportBuilder() {
        document.getElementById('generate-report').addEventListener('click', () => {
            this.generateCustomReport();
        });

        document.getElementById('save-report').addEventListener('click', () => {
            this.saveReportTemplate();
        });

        document.getElementById('schedule-report').addEventListener('click', () => {
            this.scheduleReport();
        });
    }

    async generateCustomReport() {
        const config = {
            source: document.getElementById('report-source').value,
            metrics: Array.from(document.querySelectorAll('.metric-checkboxes input:checked')).map(cb => cb.value),
            timeRange: document.getElementById('report-timerange').value,
            chartType: document.getElementById('report-chart').value
        };

        try {
            const response = await fetch('/api/reports/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });

            const reportData = await response.json();
            this.renderReport(reportData, config.chartType);
        } catch (error) {
            console.error('Report generation failed:', error);
            this.showNotification('Report generation failed', 'error');
        }
    }

    renderReport(data, chartType) {
        const container = document.getElementById('chart-container');
        container.innerHTML = '';

        switch (chartType) {
            case 'line':
                this.renderLineChart(container, data);
                break;
            case 'bar':
                this.renderBarChart(container, data);
                break;
            case 'pie':
                this.renderPieChart(container, data);
                break;
            case 'table':
                this.renderDataTable(container, data);
                break;
        }
    }

    renderLineChart(container, data) {
        const canvas = document.createElement('canvas');
        container.appendChild(canvas);
        
        // Simple line chart implementation
        const ctx = canvas.getContext('2d');
        const width = canvas.width = container.clientWidth;
        const height = canvas.height = 400;
        
        const maxValue = Math.max(...data.values);
        const stepX = width / (data.labels.length - 1);
        const stepY = height / maxValue;
        
        ctx.strokeStyle = '#6B73FF';
        ctx.lineWidth = 2;
        ctx.beginPath();
        
        data.values.forEach((value, index) => {
            const x = index * stepX;
            const y = height - (value * stepY);
            
            if (index === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });
        
        ctx.stroke();
    }

    createAPIKeyManager() {
        const apiManager = document.createElement('div');
        apiManager.id = 'api-key-manager';
        apiManager.className = 'settings-section';
        apiManager.innerHTML = `
            <h3>API Key Management</h3>
            <div class="api-keys-list">
                <div class="api-key-item">
                    <div class="key-info">
                        <span class="key-name">Production API Key</span>
                        <span class="key-permissions">Full Access</span>
                    </div>
                    <div class="key-actions">
                        <button class="regenerate-key">🔄 Regenerate</button>
                        <button class="revoke-key">🚫 Revoke</button>
                    </div>
                </div>
            </div>
            <button id="create-api-key">+ Create New API Key</button>
        `;

        const settingsContent = document.querySelector('#settings .tab-content');
        if (settingsContent) {
            settingsContent.appendChild(apiManager);
        }

        this.setupAPIKeyManager();
    }

    setupAPIKeyManager() {
        document.getElementById('create-api-key').addEventListener('click', () => {
            this.showAPIKeyCreationModal();
        });
    }

    showAPIKeyCreationModal() {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <h3>Create API Key</h3>
                <form id="api-key-form">
                    <div class="form-group">
                        <label>Key Name:</label>
                        <input type="text" id="key-name" required>
                    </div>
                    <div class="form-group">
                        <label>Permissions:</label>
                        <div class="permission-checkboxes">
                            <label><input type="checkbox" value="read"> Read</label>
                            <label><input type="checkbox" value="write"> Write</label>
                            <label><input type="checkbox" value="admin"> Admin</label>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Expiration:</label>
                        <select id="key-expiration">
                            <option value="30">30 days</option>
                            <option value="90">90 days</option>
                            <option value="365">1 year</option>
                            <option value="never">Never</option>
                        </select>
                    </div>
                    <div class="modal-actions">
                        <button type="submit">Create Key</button>
                        <button type="button" class="cancel">Cancel</button>
                    </div>
                </form>
            </div>
        `;

        document.body.appendChild(modal);

        modal.querySelector('.cancel').onclick = () => modal.remove();
        modal.querySelector('#api-key-form').onsubmit = (e) => {
            e.preventDefault();
            this.createAPIKey(modal);
        };
    }

    async createAPIKey(modal) {
        const formData = new FormData(modal.querySelector('#api-key-form'));
        const permissions = Array.from(modal.querySelectorAll('.permission-checkboxes input:checked')).map(cb => cb.value);
        
        const keyData = {
            name: formData.get('key-name'),
            permissions: permissions,
            expiration: formData.get('key-expiration')
        };

        try {
            const response = await fetch('/api/keys/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(keyData)
            });

            const result = await response.json();
            
            if (result.success) {
                this.showNotification('API key created successfully', 'success');
                this.displayNewAPIKey(result.key);
                modal.remove();
            } else {
                this.showNotification('Failed to create API key', 'error');
            }
        } catch (error) {
            console.error('API key creation failed:', error);
            this.showNotification('API key creation failed', 'error');
        }
    }

    setupRealTimeUpdates() {
        // Real-time notifications
        this.setupNotificationSystem();
        
        // Live data updates
        this.setupLiveDataUpdates();
    }

    setupNotificationSystem() {
        const notificationContainer = document.createElement('div');
        notificationContainer.id = 'notification-container';
        notificationContainer.className = 'notification-container';
        document.body.appendChild(notificationContainer);
    }

    showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">${this.getNotificationIcon(type)}</span>
                <span class="notification-message">${message}</span>
                <button class="notification-close">×</button>
            </div>
        `;

        const container = document.getElementById('notification-container');
        container.appendChild(notification);

        notification.querySelector('.notification-close').onclick = () => {
            notification.remove();
        };

        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, duration);
        }
    }

    getNotificationIcon(type) {
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        return icons[type] || icons.info;
    }

    setupLiveDataUpdates() {
        // Subscribe to real-time updates
        if (window.realTimeManager) {
            window.realTimeManager.subscribe('security', (data) => {
                this.updateSecurityStatus(data);
            });

            window.realTimeManager.subscribe('system', (data) => {
                this.updateSystemMetrics(data);
            });

            window.realTimeManager.subscribe('alerts', (data) => {
                this.showNotification(data.message, data.type);
            });
        }
    }

    updateSecurityStatus(data) {
        const securityElements = document.querySelectorAll('[data-security-metric]');
        securityElements.forEach(element => {
            const metric = element.dataset.securityMetric;
            if (data[metric] !== undefined) {
                element.textContent = data[metric];
            }
        });
    }

    updateSystemMetrics(data) {
        const systemElements = document.querySelectorAll('[data-system-metric]');
        systemElements.forEach(element => {
            const metric = element.dataset.systemMetric;
            if (data[metric] !== undefined) {
                element.textContent = data[metric];
            }
        });
    }
}

// Advanced Analytics Module
class AdvancedAnalytics {
    constructor() {
        this.charts = new Map();
        this.metrics = new Map();
        this.init();
    }

    init() {
        this.setupPredictiveAnalytics();
        this.setupPerformanceTracking();
        this.setupCostOptimization();
    }

    setupPredictiveAnalytics() {
        // Implementation for predictive analytics
        this.createPredictiveModels();
    }

    createPredictiveModels() {
        const models = {
            usage: this.createUsagePredictionModel(),
            performance: this.createPerformancePredictionModel(),
            cost: this.createCostPredictionModel()
        };

        this.models = models;
    }

    createUsagePredictionModel() {
        return {
            predict: (historicalData) => {
                // Simple linear regression for usage prediction
                const trend = this.calculateTrend(historicalData);
                const nextPeriod = historicalData[historicalData.length - 1] + trend;
                return Math.max(0, nextPeriod);
            }
        };
    }

    calculateTrend(data) {
        if (data.length < 2) return 0;
        
        const n = data.length;
        const sumX = (n * (n - 1)) / 2;
        const sumY = data.reduce((sum, val) => sum + val, 0);
        const sumXY = data.reduce((sum, val, index) => sum + (index * val), 0);
        const sumX2 = (n * (n - 1) * (2 * n - 1)) / 6;
        
        return (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
    }
}

// Executive Dashboard Module
class ExecutiveDashboard {
    constructor() {
        this.kpis = new Map();
        this.reports = new Map();
        this.init();
    }

    init() {
        this.setupKPITracking();
        this.setupExecutiveReports();
        this.setupRealTimeMetrics();
    }

    setupKPITracking() {
        const kpis = [
            { id: 'revenue', name: 'Total Revenue', target: 1000000 },
            { id: 'users', name: 'Active Users', target: 10000 },
            { id: 'performance', name: 'System Performance', target: 99.9 },
            { id: 'satisfaction', name: 'Customer Satisfaction', target: 4.5 }
        ];

        kpis.forEach(kpi => {
            this.kpis.set(kpi.id, kpi);
        });
    }

    async updateKPI(id, value) {
        const kpi = this.kpis.get(id);
        if (kpi) {
            kpi.current = value;
            kpi.progress = (value / kpi.target) * 100;
            this.renderKPI(kpi);
        }
    }

    renderKPI(kpi) {
        const element = document.querySelector(`[data-kpi="${kpi.id}"]`);
        if (element) {
            element.querySelector('.kpi-value').textContent = kpi.current;
            element.querySelector('.kpi-progress').style.width = `${Math.min(100, kpi.progress)}%`;
        }
    }
}

// Initialize Enterprise Features
document.addEventListener('DOMContentLoaded', () => {
    window.enterpriseFeatures = new EnterpriseFeatures();
    console.log('Enterprise features initialized');
});

console.log('ApexAgent Enterprise module loaded successfully');

