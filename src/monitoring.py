"""
ApexAgent Monitoring and Metrics Module
Production-ready monitoring with Prometheus integration
"""

import time
import psutil
import logging
from functools import wraps
from datetime import datetime, timedelta
from collections import defaultdict, deque
from threading import Lock, Thread
import json
import redis
from flask import request, g
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Prometheus metrics
REQUEST_COUNT = Counter('apexagent_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('apexagent_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
ACTIVE_USERS = Gauge('apexagent_active_users', 'Number of active users')
SYSTEM_CPU = Gauge('apexagent_system_cpu_percent', 'System CPU usage')
SYSTEM_MEMORY = Gauge('apexagent_system_memory_percent', 'System memory usage')
SYSTEM_DISK = Gauge('apexagent_system_disk_percent', 'System disk usage')
API_ERRORS = Counter('apexagent_api_errors_total', 'API errors', ['endpoint', 'error_type'])
CACHE_HITS = Counter('apexagent_cache_hits_total', 'Cache hits', ['cache_type'])
CACHE_MISSES = Counter('apexagent_cache_misses_total', 'Cache misses', ['cache_type'])
SECURITY_EVENTS = Counter('apexagent_security_events_total', 'Security events', ['event_type', 'severity'])
AI_REQUESTS = Counter('apexagent_ai_requests_total', 'AI provider requests', ['provider', 'model'])
AI_RESPONSE_TIME = Histogram('apexagent_ai_response_seconds', 'AI response time', ['provider', 'model'])
HYBRID_PROCESSING = Gauge('apexagent_hybrid_local_percent', 'Percentage of local processing')
COST_SAVINGS = Gauge('apexagent_cost_savings_percent', 'Cost savings percentage')

class PerformanceMonitor:
    """Advanced performance monitoring with real-time analytics"""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        self.metrics_lock = Lock()
        self.request_times = deque(maxlen=1000)
        self.error_counts = defaultdict(int)
        self.endpoint_stats = defaultdict(lambda: {'count': 0, 'total_time': 0, 'errors': 0})
        self.active_sessions = set()
        self.security_events = deque(maxlen=500)
        self.ai_metrics = defaultdict(lambda: {'requests': 0, 'total_time': 0, 'errors': 0})
        
        # Start background monitoring
        self.monitoring_thread = Thread(target=self._background_monitoring, daemon=True)
        self.monitoring_thread.start()
        
        logging.info("Performance monitor initialized")

    def _background_monitoring(self):
        """Background thread for system monitoring"""
        while True:
            try:
                # Update system metrics
                SYSTEM_CPU.set(psutil.cpu_percent())
                SYSTEM_MEMORY.set(psutil.virtual_memory().percent)
                SYSTEM_DISK.set(psutil.disk_usage('/').percent)
                
                # Update active users count
                ACTIVE_USERS.set(len(self.active_sessions))
                
                # Clean old sessions (older than 30 minutes)
                current_time = time.time()
                self.active_sessions = {
                    session for session in self.active_sessions 
                    if current_time - session.get('last_seen', 0) < 1800
                }
                
                # Update hybrid processing metrics
                self._update_hybrid_metrics()
                
                time.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                logging.error(f"Background monitoring error: {e}")
                time.sleep(60)  # Wait longer on error

    def _update_hybrid_metrics(self):
        """Update hybrid processing and cost metrics"""
        try:
            if self.redis_client:
                # Get hybrid processing stats from Redis
                local_requests = int(self.redis_client.get('local_requests') or 0)
                cloud_requests = int(self.redis_client.get('cloud_requests') or 0)
                
                if local_requests + cloud_requests > 0:
                    local_percent = (local_requests / (local_requests + cloud_requests)) * 100
                    HYBRID_PROCESSING.set(local_percent)
                    
                    # Calculate cost savings (local processing is ~60% cheaper)
                    cost_savings = local_percent * 0.6
                    COST_SAVINGS.set(cost_savings)
                    
        except Exception as e:
            logging.error(f"Hybrid metrics update error: {e}")

    def track_request(self, method, endpoint, status_code, duration):
        """Track request metrics"""
        with self.metrics_lock:
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status_code).inc()
            REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
            
            self.request_times.append({
                'timestamp': time.time(),
                'duration': duration,
                'endpoint': endpoint,
                'status': status_code
            })
            
            # Update endpoint statistics
            stats = self.endpoint_stats[endpoint]
            stats['count'] += 1
            stats['total_time'] += duration
            if status_code >= 400:
                stats['errors'] += 1

    def track_error(self, endpoint, error_type, error_message=None):
        """Track API errors"""
        API_ERRORS.labels(endpoint=endpoint, error_type=error_type).inc()
        
        with self.metrics_lock:
            self.error_counts[f"{endpoint}:{error_type}"] += 1
            
        logging.error(f"API Error - Endpoint: {endpoint}, Type: {error_type}, Message: {error_message}")

    def track_cache_operation(self, cache_type, hit=True):
        """Track cache operations"""
        if hit:
            CACHE_HITS.labels(cache_type=cache_type).inc()
        else:
            CACHE_MISSES.labels(cache_type=cache_type).inc()

    def track_security_event(self, event_type, severity, details=None):
        """Track security events"""
        SECURITY_EVENTS.labels(event_type=event_type, severity=severity).inc()
        
        event = {
            'timestamp': time.time(),
            'type': event_type,
            'severity': severity,
            'details': details,
            'ip': request.remote_addr if request else 'unknown'
        }
        
        with self.metrics_lock:
            self.security_events.append(event)
            
        logging.warning(f"Security Event - Type: {event_type}, Severity: {severity}, Details: {details}")

    def track_ai_request(self, provider, model, duration, success=True):
        """Track AI provider requests"""
        AI_REQUESTS.labels(provider=provider, model=model).inc()
        AI_RESPONSE_TIME.labels(provider=provider, model=model).observe(duration)
        
        with self.metrics_lock:
            key = f"{provider}:{model}"
            metrics = self.ai_metrics[key]
            metrics['requests'] += 1
            metrics['total_time'] += duration
            if not success:
                metrics['errors'] += 1

    def add_active_session(self, session_id, user_id=None):
        """Add active session"""
        session_info = {
            'id': session_id,
            'user_id': user_id,
            'start_time': time.time(),
            'last_seen': time.time()
        }
        self.active_sessions.add(session_info)

    def update_session_activity(self, session_id):
        """Update session last seen time"""
        for session in self.active_sessions:
            if session.get('id') == session_id:
                session['last_seen'] = time.time()
                break

    def get_performance_summary(self):
        """Get comprehensive performance summary"""
        with self.metrics_lock:
            current_time = time.time()
            
            # Recent requests (last 5 minutes)
            recent_requests = [
                req for req in self.request_times 
                if current_time - req['timestamp'] < 300
            ]
            
            # Calculate metrics
            avg_response_time = sum(req['duration'] for req in recent_requests) / len(recent_requests) if recent_requests else 0
            error_rate = len([req for req in recent_requests if req['status'] >= 400]) / len(recent_requests) if recent_requests else 0
            
            # Top endpoints by request count
            top_endpoints = sorted(
                self.endpoint_stats.items(),
                key=lambda x: x[1]['count'],
                reverse=True
            )[:10]
            
            # Recent security events
            recent_security = [
                event for event in self.security_events
                if current_time - event['timestamp'] < 3600  # Last hour
            ]
            
            return {
                'timestamp': current_time,
                'system': {
                    'cpu_percent': psutil.cpu_percent(),
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_percent': psutil.disk_usage('/').percent,
                    'active_users': len(self.active_sessions)
                },
                'requests': {
                    'total_recent': len(recent_requests),
                    'avg_response_time': round(avg_response_time, 3),
                    'error_rate': round(error_rate * 100, 2),
                    'requests_per_minute': len(recent_requests) / 5
                },
                'top_endpoints': [
                    {
                        'endpoint': endpoint,
                        'count': stats['count'],
                        'avg_time': round(stats['total_time'] / stats['count'], 3),
                        'error_rate': round((stats['errors'] / stats['count']) * 100, 2)
                    }
                    for endpoint, stats in top_endpoints
                ],
                'security': {
                    'recent_events': len(recent_security),
                    'event_types': list(set(event['type'] for event in recent_security))
                },
                'ai_providers': {
                    provider_model: {
                        'requests': metrics['requests'],
                        'avg_response_time': round(metrics['total_time'] / metrics['requests'], 3) if metrics['requests'] > 0 else 0,
                        'error_rate': round((metrics['errors'] / metrics['requests']) * 100, 2) if metrics['requests'] > 0 else 0
                    }
                    for provider_model, metrics in self.ai_metrics.items()
                }
            }

class HealthChecker:
    """Comprehensive health checking system"""
    
    def __init__(self, redis_client=None, db=None):
        self.redis_client = redis_client
        self.db = db
        self.health_checks = {}
        self.last_check_time = 0
        self.check_interval = 30  # 30 seconds
        
    def register_check(self, name, check_function, critical=True):
        """Register a health check"""
        self.health_checks[name] = {
            'function': check_function,
            'critical': critical,
            'last_result': None,
            'last_check': 0
        }

    def run_health_checks(self, force=False):
        """Run all health checks"""
        current_time = time.time()
        
        if not force and current_time - self.last_check_time < self.check_interval:
            return self._get_cached_results()
            
        results = {}
        overall_status = 'healthy'
        
        for name, check_info in self.health_checks.items():
            try:
                start_time = time.time()
                result = check_info['function']()
                duration = time.time() - start_time
                
                check_result = {
                    'status': 'healthy' if result else 'unhealthy',
                    'duration': round(duration, 3),
                    'timestamp': current_time,
                    'critical': check_info['critical']
                }
                
                if not result and check_info['critical']:
                    overall_status = 'unhealthy'
                elif not result:
                    overall_status = 'degraded' if overall_status == 'healthy' else overall_status
                    
            except Exception as e:
                check_result = {
                    'status': 'error',
                    'error': str(e),
                    'timestamp': current_time,
                    'critical': check_info['critical']
                }
                
                if check_info['critical']:
                    overall_status = 'unhealthy'
                    
            results[name] = check_result
            check_info['last_result'] = check_result
            check_info['last_check'] = current_time
            
        self.last_check_time = current_time
        
        return {
            'status': overall_status,
            'timestamp': current_time,
            'checks': results
        }

    def _get_cached_results(self):
        """Get cached health check results"""
        results = {}
        overall_status = 'healthy'
        
        for name, check_info in self.health_checks.items():
            if check_info['last_result']:
                results[name] = check_info['last_result']
                if check_info['last_result']['status'] != 'healthy' and check_info['critical']:
                    overall_status = 'unhealthy'
                    
        return {
            'status': overall_status,
            'timestamp': self.last_check_time,
            'checks': results,
            'cached': True
        }

    def check_database(self):
        """Check database connectivity"""
        try:
            if self.db:
                # Simple query to test connection
                result = self.db.engine.execute('SELECT 1').fetchone()
                return result is not None
            return False
        except Exception:
            return False

    def check_redis(self):
        """Check Redis connectivity"""
        try:
            if self.redis_client:
                return self.redis_client.ping()
            return False
        except Exception:
            return False

    def check_disk_space(self):
        """Check available disk space"""
        try:
            disk_usage = psutil.disk_usage('/')
            free_percent = (disk_usage.free / disk_usage.total) * 100
            return free_percent > 10  # At least 10% free space
        except Exception:
            return False

    def check_memory_usage(self):
        """Check memory usage"""
        try:
            memory = psutil.virtual_memory()
            return memory.percent < 90  # Less than 90% memory usage
        except Exception:
            return False

def monitor_requests(monitor):
    """Decorator to monitor Flask requests"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            
            try:
                response = f(*args, **kwargs)
                status_code = getattr(response, 'status_code', 200)
                
            except Exception as e:
                status_code = 500
                monitor.track_error(request.endpoint or 'unknown', type(e).__name__, str(e))
                raise
                
            finally:
                duration = time.time() - start_time
                monitor.track_request(
                    request.method,
                    request.endpoint or 'unknown',
                    status_code,
                    duration
                )
                
            return response
        return decorated_function
    return decorator

def setup_monitoring(app, redis_client=None, db=None):
    """Setup monitoring for Flask app"""
    monitor = PerformanceMonitor(redis_client)
    health_checker = HealthChecker(redis_client, db)
    
    # Register health checks
    health_checker.register_check('database', health_checker.check_database, critical=True)
    health_checker.register_check('redis', health_checker.check_redis, critical=True)
    health_checker.register_check('disk_space', health_checker.check_disk_space, critical=True)
    health_checker.register_check('memory_usage', health_checker.check_memory_usage, critical=False)
    
    # Add monitoring routes
    @app.route('/metrics')
    def metrics():
        return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}
    
    @app.route('/health')
    def health():
        health_status = health_checker.run_health_checks()
        status_code = 200 if health_status['status'] == 'healthy' else 503
        return health_status, status_code
    
    @app.route('/api/metrics/performance')
    def performance_metrics():
        return monitor.get_performance_summary()
    
    @app.route('/api/metrics/business')
    def business_metrics():
        return {
            'active_users': len(monitor.active_sessions),
            'total_requests': sum(stats['count'] for stats in monitor.endpoint_stats.values()),
            'avg_response_time': sum(req['duration'] for req in monitor.request_times) / len(monitor.request_times) if monitor.request_times else 0,
            'error_rate': len([req for req in monitor.request_times if req.get('status', 200) >= 400]) / len(monitor.request_times) if monitor.request_times else 0
        }
    
    @app.route('/api/metrics/security')
    def security_metrics():
        recent_events = [
            event for event in monitor.security_events
            if time.time() - event['timestamp'] < 3600
        ]
        
        return {
            'recent_events_count': len(recent_events),
            'event_types': list(set(event['type'] for event in recent_events)),
            'severity_breakdown': {
                severity: len([e for e in recent_events if e['severity'] == severity])
                for severity in ['low', 'medium', 'high', 'critical']
            }
        }
    
    # Request monitoring middleware
    @app.before_request
    def before_request():
        g.start_time = time.time()
        
        # Track session activity
        session_id = request.headers.get('X-Session-ID')
        if session_id:
            monitor.update_session_activity(session_id)
    
    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            monitor.track_request(
                request.method,
                request.endpoint or 'unknown',
                response.status_code,
                duration
            )
        return response
    
    # Store monitor and health checker in app context
    app.monitor = monitor
    app.health_checker = health_checker
    
    logging.info("Monitoring system initialized successfully")
    return monitor, health_checker

