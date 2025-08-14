# Firebase Performance Monitoring Integration for Aideon AI Lite

This document provides comprehensive information about the Firebase Performance Monitoring integration for real-time performance tracking and optimization in Aideon AI Lite.

## Overview

Firebase Performance Monitoring is a service that helps you to gain insight into the performance characteristics of your app. This integration provides comprehensive performance monitoring, system metrics collection, and optimization capabilities for Aideon AI Lite.

## Features

- **Automatic Request Monitoring**: Track all HTTP requests and their performance
- **Custom Performance Traces**: Create custom traces for specific operations
- **System Metrics Collection**: Monitor CPU, memory, disk, and network usage
- **Performance Thresholds**: Automatic detection of slow operations
- **Real-time Analytics**: Live performance monitoring and alerting
- **Background Monitoring**: Continuous system health monitoring
- **Performance Benchmarking**: Built-in performance testing capabilities
- **Health Monitoring**: System health checks and status reporting

## Architecture

### Components

1. **FirebasePerformanceManager**: Core class for performance monitoring
2. **PerformanceTrace**: Individual performance trace tracking
3. **Flask Integration**: Automatic request performance monitoring
4. **API Endpoints**: REST API for performance management
5. **Background Monitoring**: Continuous system metrics collection
6. **Health Monitoring**: System health checks and alerts

### Metric Types

```python
METRIC_TYPES = {
    'HTTP_REQUEST': 'http_request',           # Web request performance
    'DATABASE_QUERY': 'database_query',       # Database operation performance
    'EXTERNAL_API': 'external_api',           # External service calls
    'AI_GENERATION': 'ai_generation',         # AI model operations
    'FILE_OPERATION': 'file_operation',       # File I/O operations
    'AUTHENTICATION': 'authentication',       # Auth operations
    'CUSTOM_TRACE': 'custom_trace',          # Custom application traces
    'SYSTEM_RESOURCE': 'system_resource'      # System resource monitoring
}
```

### Performance Thresholds

```python
PERFORMANCE_THRESHOLDS = {
    'HTTP_REQUEST': {
        'good': 1.0,        # < 1 second
        'acceptable': 3.0,  # 1-3 seconds
        'poor': 5.0         # > 5 seconds
    },
    'DATABASE_QUERY': {
        'good': 0.1,        # < 100ms
        'acceptable': 0.5,  # 100-500ms
        'poor': 1.0         # > 1 second
    },
    'AI_GENERATION': {
        'good': 5.0,        # < 5 seconds
        'acceptable': 15.0, # 5-15 seconds
        'poor': 30.0        # > 30 seconds
    }
}
```

## Installation and Setup

### 1. Initialize Performance Manager

```python
from src.firebase_performance import init_performance_monitoring
from flask import Flask

app = Flask(__name__)

# Initialize Performance Monitoring
performance_manager = init_performance_monitoring(
    app=app,
    credentials_path='/path/to/firebase-credentials.json'
)
```

### 2. Register API Endpoints

```python
from src.api.performance_endpoints import performance_bp

app.register_blueprint(performance_bp)
```

### 3. Environment Configuration

```bash
# Firebase configuration
FIREBASE_PROJECT_ID=aideonlite-ai
FIREBASE_CREDENTIALS_PATH=/path/to/credentials.json

# Performance monitoring configuration
PERFORMANCE_AUTO_COLLECTION=true
PERFORMANCE_BACKGROUND_MONITORING=true
PERFORMANCE_MONITORING_INTERVAL=30
```

## Usage Examples

### Basic Performance Tracing

```python
from src.firebase_performance import get_performance_manager

manager = get_performance_manager()

# Start a custom trace
trace = manager.start_trace(
    name="video_generation",
    trace_type="AI_GENERATION",
    attributes={
        "model": "stable-diffusion",
        "resolution": "1024x1024",
        "user_id": "123"
    }
)

# Perform the operation
result = generate_video()

# Add metrics and attributes
trace.add_metric("frames_generated", 30)
trace.add_attribute("output_format", "mp4")

# Stop the trace
manager.stop_trace(trace)
```

### Using Context Manager

```python
# Using trace as context manager
with manager.start_trace("database_operation", "DATABASE_QUERY") as trace:
    # Perform database operation
    result = db.query("SELECT * FROM users")
    
    # Add metrics
    trace.add_metric("rows_returned", len(result))
    trace.add_attribute("query_type", "SELECT")
    
    # Trace is automatically stopped when exiting context
```

### Using the Decorator

```python
from src.firebase_performance import performance_monitor

@performance_monitor(
    name="ai_text_generation",
    trace_type="AI_GENERATION",
    attributes={"model": "gpt-4"}
)
def generate_text(prompt):
    # Function implementation
    # Performance is automatically tracked
    return ai_model.generate(prompt)
```

### System Metrics Monitoring

```python
# Get current system metrics
stats = manager.get_performance_stats()
system_metrics = stats['system_metrics']

print(f"CPU Usage: {system_metrics['cpu']['percent']}%")
print(f"Memory Usage: {system_metrics['memory']['percent']}%")
print(f"Disk Usage: {system_metrics['disk']['percent']}%")
```

## API Endpoints

### Trace Management

#### Start Custom Trace

```http
POST /api/v1/performance/start-trace
Content-Type: application/json

{
  "name": "custom_operation",
  "trace_type": "CUSTOM_TRACE",
  "attributes": {
    "operation_type": "data_processing",
    "user_id": "user_123"
  }
}
```

**Response:**
```json
{
  "success": true,
  "trace_id": "uuid-trace-id",
  "message": "Trace started successfully"
}
```

#### Stop Custom Trace

```http
POST /api/v1/performance/stop-trace
Content-Type: application/json

{
  "trace_id": "uuid-trace-id",
  "attributes": {
    "result_status": "success",
    "items_processed": 100
  }
}
```

**Response:**
```json
{
  "success": true,
  "trace_id": "uuid-trace-id",
  "duration": 2.345,
  "message": "Trace stopped successfully"
}
```

#### Add Custom Metric

```http
POST /api/v1/performance/add-metric
Content-Type: application/json

{
  "trace_id": "uuid-trace-id",
  "metric_name": "processing_rate",
  "value": 150.5
}
```

### Performance Analytics

#### Get Performance Statistics

```http
GET /api/v1/performance/stats
```

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_traces": 1250,
    "traces_by_type": {
      "HTTP_REQUEST": 800,
      "DATABASE_QUERY": 300,
      "AI_GENERATION": 150
    },
    "average_durations": {
      "HTTP_REQUEST": 1.2,
      "DATABASE_QUERY": 0.3,
      "AI_GENERATION": 8.5
    },
    "active_traces": 5,
    "slow_operations_count": 12,
    "system_metrics": {
      "cpu": {"percent": 45.2},
      "memory": {"percent": 62.8},
      "disk": {"percent": 78.1}
    }
  }
}
```

#### Get Trace Summary

```http
GET /api/v1/performance/trace-summary?trace_type=HTTP_REQUEST
```

**Response:**
```json
{
  "success": true,
  "summary": {
    "count": 800,
    "average_duration": 1.2,
    "min_duration": 0.1,
    "max_duration": 8.5,
    "p95_duration": 3.2,
    "p99_duration": 6.1
  },
  "trace_type": "HTTP_REQUEST"
}
```

### System Monitoring

#### Get System Metrics

```http
GET /api/v1/performance/system-metrics
```

**Response:**
```json
{
  "success": true,
  "metrics": {
    "timestamp": "2024-12-06T14:30:22Z",
    "cpu": {
      "percent": 45.2,
      "count": 8
    },
    "memory": {
      "percent": 62.8,
      "available_bytes": 2147483648,
      "total_bytes": 8589934592
    },
    "disk": {
      "percent": 78.1,
      "free_bytes": 107374182400,
      "total_bytes": 536870912000
    },
    "network": {
      "bytes_sent": 1048576000,
      "bytes_received": 2097152000
    },
    "process": {
      "memory_bytes": 134217728,
      "cpu_percent": 12.5
    }
  }
}
```

#### Get Slow Operations

```http
GET /api/v1/performance/slow-operations?limit=10
```

**Response:**
```json
{
  "success": true,
  "slow_operations": [
    {
      "timestamp": "2024-12-06T14:25:15Z",
      "message": "Slow HTTP_REQUEST operation: POST /api/generate",
      "type": "HTTP_REQUEST",
      "context": {
        "duration": 8.5,
        "threshold": 5.0,
        "attributes": {
          "method": "POST",
          "endpoint": "/api/generate"
        }
      }
    }
  ],
  "total_count": 12
}
```

### Health Monitoring

#### Health Check

```http
GET /api/v1/performance/health
```

**Response:**
```json
{
  "success": true,
  "health": {
    "status": "healthy",
    "issues": [],
    "stats": {...},
    "timestamp": "2024-12-06T14:30:22Z"
  }
}
```

**Warning Status:**
```json
{
  "success": true,
  "health": {
    "status": "warning",
    "issues": [
      "High CPU usage: 85.2%",
      "High number of slow operations: 15"
    ],
    "stats": {...},
    "timestamp": "2024-12-06T14:30:22Z"
  }
}
```

### Configuration

#### Get Metric Types

```http
GET /api/v1/performance/metric-types
```

#### Get Performance Thresholds

```http
GET /api/v1/performance/thresholds
```

### Performance Testing

#### Run Benchmark

```http
POST /api/v1/performance/benchmark
Content-Type: application/json

{
  "test_type": "cpu",
  "duration": 2.0
}
```

**Response:**
```json
{
  "success": true,
  "benchmark": {
    "test_type": "cpu",
    "requested_duration": 2.0,
    "actual_duration": 2.001,
    "result": 15000000
  }
}
```

## Flask Integration

### Automatic Request Monitoring

All HTTP requests are automatically monitored:

```python
@app.before_request
def before_request():
    # Automatically start performance trace for each request
    g.performance_trace = manager.start_trace(
        name=f"{request.method} {request.endpoint}",
        trace_type="HTTP_REQUEST",
        attributes={
            "method": request.method,
            "endpoint": request.endpoint,
            "url": request.url
        }
    )

@app.after_request
def after_request(response):
    # Automatically stop trace and add response metrics
    if hasattr(g, 'performance_trace'):
        g.performance_trace.add_attribute('status_code', response.status_code)
        g.performance_trace.add_attribute('response_size', len(response.get_data()))
        manager.stop_trace(g.performance_trace)
```

### Performance Middleware

Custom middleware for specific monitoring:

```python
def performance_middleware():
    """Custom performance monitoring middleware."""
    
    def middleware(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            with manager.start_trace(f.__name__, "CUSTOM_TRACE") as trace:
                trace.add_attribute("function", f.__name__)
                result = f(*args, **kwargs)
                trace.add_attribute("success", True)
                return result
        return decorated_function
    return middleware
```

## Background Monitoring

### System Metrics Collection

Continuous monitoring of system resources:

```python
def _monitor_system_metrics(self):
    """Monitor system metrics in background."""
    while not self._shutdown_event.is_set():
        try:
            # Collect system metrics
            metrics = self._collect_system_metrics()
            
            # Check for performance issues
            self._check_performance_thresholds(metrics)
            
            # Sleep for monitoring interval
            time.sleep(30)  # Monitor every 30 seconds
            
        except Exception as e:
            logger.error(f"Error in system monitoring: {str(e)}")
```

### Performance Threshold Monitoring

Automatic detection of performance issues:

```python
def _check_performance_thresholds(self, metrics):
    """Check if system metrics exceed performance thresholds."""
    
    # Check CPU usage
    cpu_percent = metrics.get('cpu', {}).get('percent', 0)
    if cpu_percent > 80:
        self._log_performance_issue(
            'High CPU usage detected',
            'SYSTEM_RESOURCE',
            {'cpu_percent': cpu_percent}
        )
    
    # Check memory usage
    memory_percent = metrics.get('memory', {}).get('percent', 0)
    if memory_percent > 85:
        self._log_performance_issue(
            'High memory usage detected',
            'SYSTEM_RESOURCE',
            {'memory_percent': memory_percent}
        )
```

## Performance Optimization

### Best Practices

1. **Use Appropriate Trace Types**: Choose the correct trace type for better categorization
2. **Add Meaningful Attributes**: Include relevant context information
3. **Monitor Critical Operations**: Focus on user-facing and critical operations
4. **Set Realistic Thresholds**: Configure thresholds based on your requirements

### Performance Tuning

1. **Database Optimization**: Monitor and optimize slow database queries
2. **API Response Times**: Track and improve API response times
3. **Resource Usage**: Monitor system resources and optimize usage
4. **Caching**: Implement caching for frequently accessed data

### Alerting and Monitoring

```python
def setup_performance_alerts():
    """Set up performance monitoring alerts."""
    
    def check_performance():
        stats = manager.get_performance_stats()
        
        # Check for high error rates
        slow_ops = stats.get('slow_operations_count', 0)
        if slow_ops > 10:
            send_alert(f"High number of slow operations: {slow_ops}")
        
        # Check system resources
        system_metrics = stats.get('system_metrics', {})
        cpu_percent = system_metrics.get('cpu', {}).get('percent', 0)
        if cpu_percent > 80:
            send_alert(f"High CPU usage: {cpu_percent}%")
    
    # Schedule regular checks
    schedule.every(5).minutes.do(check_performance)
```

## Integration with Monitoring Systems

### Dashboard Integration

Create performance dashboards:

```python
def create_performance_dashboard():
    """Create performance monitoring dashboard."""
    
    # Get performance statistics
    stats = manager.get_performance_stats()
    
    # Create dashboard widgets
    widgets = [
        {
            "type": "metric",
            "title": "Total Traces",
            "value": stats['total_traces']
        },
        {
            "type": "chart",
            "title": "Average Response Times",
            "data": stats['average_durations']
        },
        {
            "type": "gauge",
            "title": "System CPU Usage",
            "value": stats['system_metrics']['cpu']['percent']
        }
    ]
    
    return widgets
```

### Log Integration

Forward performance data to logging systems:

```python
class PerformanceLogHandler(logging.Handler):
    """Custom log handler for performance data."""
    
    def emit(self, record):
        # Forward performance data to external logging system
        if hasattr(record, 'performance_data'):
            external_logger.log_performance(record.performance_data)
```

## Troubleshooting

### Common Issues

#### High CPU Usage

```python
# Monitor CPU-intensive operations
@performance_monitor(trace_type="CUSTOM_TRACE")
def cpu_intensive_operation():
    # Monitor and optimize CPU usage
    pass
```

#### Memory Leaks

```python
# Monitor memory usage patterns
def monitor_memory_usage():
    stats = manager.get_performance_stats()
    memory_percent = stats['system_metrics']['memory']['percent']
    
    if memory_percent > 90:
        # Trigger garbage collection
        import gc
        gc.collect()
```

#### Slow Database Queries

```python
# Monitor database performance
@performance_monitor(trace_type="DATABASE_QUERY")
def database_operation():
    # Monitor and optimize database queries
    pass
```

### Debugging Steps

1. **Check Performance Stats**: Review performance statistics regularly
2. **Monitor System Metrics**: Watch system resource usage
3. **Analyze Slow Operations**: Investigate operations exceeding thresholds
4. **Review Trace Details**: Examine individual trace attributes and metrics
5. **Use Health Endpoints**: Monitor system health status

## Future Enhancements

### Planned Features

1. **Machine Learning Analysis**: Automatic performance pattern detection
2. **Predictive Monitoring**: Predict performance issues before they occur
3. **Advanced Analytics**: More sophisticated performance analysis
4. **Custom Dashboards**: User-configurable performance dashboards
5. **Integration APIs**: Better integration with external monitoring tools

### Scalability Improvements

1. **Distributed Tracing**: Support for distributed system tracing
2. **Data Aggregation**: Efficient aggregation of performance data
3. **Real-time Streaming**: Real-time performance data streaming
4. **Advanced Caching**: Intelligent caching of performance metrics

