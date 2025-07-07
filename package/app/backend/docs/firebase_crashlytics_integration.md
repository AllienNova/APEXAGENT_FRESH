# Firebase Crashlytics Integration for Aideon AI Lite

This document provides comprehensive information about the Firebase Crashlytics integration for error reporting and crash analytics in Aideon AI Lite.

## Overview

Firebase Crashlytics is a lightweight, realtime crash reporter that helps you track, prioritize, and fix stability issues that erode your app quality. This integration provides comprehensive error monitoring, crash analytics, and debugging capabilities for Aideon AI Lite.

## Features

- **Automatic Crash Detection**: Captures unhandled exceptions and crashes
- **Custom Error Logging**: Log custom errors with context and metadata
- **Real-time Monitoring**: Real-time error tracking and alerting
- **Error Categorization**: Organize errors by severity and category
- **User Tracking**: Associate errors with specific users
- **Breadcrumb Logging**: Track user actions leading to crashes
- **Performance Monitoring**: Detect slow requests and performance issues
- **Health Monitoring**: System health checks and status reporting

## Architecture

### Components

1. **FirebaseCrashlyticsManager**: Core class for error reporting and analytics
2. **Flask Integration**: Automatic error handlers and middleware
3. **API Endpoints**: REST API for error reporting and monitoring
4. **Background Processing**: Asynchronous error processing
5. **Health Monitoring**: System health checks and alerts

### Error Categories

```python
ERROR_CATEGORIES = {
    'API_ERROR': 'api_error',
    'DATABASE_ERROR': 'database_error',
    'AUTHENTICATION_ERROR': 'auth_error',
    'VALIDATION_ERROR': 'validation_error',
    'EXTERNAL_SERVICE_ERROR': 'external_service_error',
    'SYSTEM_ERROR': 'system_error',
    'USER_ERROR': 'user_error',
    'PERFORMANCE_ERROR': 'performance_error',
    'SECURITY_ERROR': 'security_error',
    'INTEGRATION_ERROR': 'integration_error'
}
```

### Severity Levels

```python
SEVERITY_LEVELS = {
    'FATAL': 'fatal',      # Critical errors that crash the application
    'ERROR': 'error',      # Errors that affect functionality
    'WARNING': 'warning',  # Potential issues that should be monitored
    'INFO': 'info',        # Informational messages
    'DEBUG': 'debug'       # Debug information
}
```

## Installation and Setup

### 1. Initialize Crashlytics Manager

```python
from src.firebase_crashlytics import init_crashlytics
from flask import Flask

app = Flask(__name__)

# Initialize Crashlytics
crashlytics_manager = init_crashlytics(
    app=app,
    credentials_path='/path/to/firebase-credentials.json'
)
```

### 2. Register API Endpoints

```python
from src.api.crashlytics_endpoints import crashlytics_bp

app.register_blueprint(crashlytics_bp)
```

### 3. Environment Configuration

```bash
# Firebase configuration
FIREBASE_PROJECT_ID=aideonlite-ai
FIREBASE_CREDENTIALS_PATH=/path/to/credentials.json

# Crashlytics configuration
CRASHLYTICS_AUTO_COLLECTION=true
CRASHLYTICS_BACKGROUND_PROCESSING=true
```

## Usage Examples

### Basic Error Logging

```python
from src.firebase_crashlytics import get_crashlytics_manager

manager = get_crashlytics_manager()

# Log a custom error
error_id = manager.log_error(
    message="User authentication failed",
    severity="ERROR",
    category="AUTHENTICATION_ERROR",
    context={
        "user_id": "123",
        "login_method": "oauth",
        "ip_address": "192.168.1.1"
    },
    user_id="123"
)
```

### Exception Logging

```python
try:
    # Some operation that might fail
    result = risky_operation()
except Exception as e:
    error_id = manager.log_exception(
        exception=e,
        severity="FATAL",
        category="SYSTEM_ERROR",
        context={
            "operation": "risky_operation",
            "parameters": {"param1": "value1"}
        }
    )
    raise  # Re-raise the exception
```

### Using the Decorator

```python
from src.firebase_crashlytics import crashlytics_monitor

@crashlytics_monitor(severity='ERROR', category='API_ERROR')
def api_endpoint():
    # Function implementation
    # Any exceptions will be automatically logged
    return {"status": "success"}
```

### User Tracking

```python
# Set user identifier for crash reports
manager.set_user_identifier(
    user_id="user_123",
    user_email="user@example.com",
    user_name="John Doe"
)

# Set custom keys for additional context
manager.set_custom_key("subscription_tier", "premium")
manager.set_custom_key("feature_flags", "ai_enabled,video_enabled")
```

### Breadcrumb Logging

```python
# Log breadcrumbs for debugging context
manager.log_breadcrumb(
    message="User started video generation",
    category="user_action",
    level="info",
    data={
        "video_type": "ai_generated",
        "duration": 30,
        "quality": "hd"
    }
)
```

## API Endpoints

### Error Reporting

#### Report Custom Error

```http
POST /api/v1/crashlytics/report-error
Content-Type: application/json

{
  "message": "Custom error message",
  "severity": "ERROR",
  "category": "API_ERROR",
  "context": {
    "additional": "context"
  },
  "user_id": "user_123"
}
```

**Response:**
```json
{
  "success": true,
  "error_id": "uuid-error-id",
  "message": "Error reported successfully"
}
```

#### Report Exception

```http
POST /api/v1/crashlytics/report-exception
Content-Type: application/json

{
  "exception_type": "ValueError",
  "exception_message": "Invalid input provided",
  "stack_trace": ["line 1", "line 2", "line 3"],
  "severity": "FATAL",
  "category": "VALIDATION_ERROR",
  "context": {
    "input_data": "invalid_value"
  }
}
```

### User Management

#### Set User Identifier

```http
POST /api/v1/crashlytics/set-user
Content-Type: application/json

{
  "user_id": "user_123",
  "user_email": "user@example.com",
  "user_name": "John Doe"
}
```

#### Set Custom Key

```http
POST /api/v1/crashlytics/set-custom-key
Content-Type: application/json

{
  "key": "subscription_tier",
  "value": "premium"
}
```

### Debugging

#### Log Breadcrumb

```http
POST /api/v1/crashlytics/breadcrumb
Content-Type: application/json

{
  "message": "User action performed",
  "category": "user_action",
  "level": "info",
  "data": {
    "action": "button_click",
    "element": "generate_video"
  }
}
```

### Monitoring

#### Get Error Statistics

```http
GET /api/v1/crashlytics/stats
```

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_errors": 150,
    "errors_by_severity": {
      "FATAL": 5,
      "ERROR": 45,
      "WARNING": 100
    },
    "errors_by_category": {
      "API_ERROR": 60,
      "SYSTEM_ERROR": 40,
      "USER_ERROR": 50
    },
    "last_error_time": "2024-12-06T14:30:22Z",
    "queue_size": 0,
    "background_thread_alive": true
  }
}
```

#### Health Check

```http
GET /api/v1/crashlytics/health
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

#### Test Crash

```http
POST /api/v1/crashlytics/test-crash
Content-Type: application/json

{
  "message": "Test crash for debugging"
}
```

### Configuration

#### Get Severity Levels

```http
GET /api/v1/crashlytics/severity-levels
```

#### Get Error Categories

```http
GET /api/v1/crashlytics/error-categories
```

## Flask Integration

### Automatic Error Handling

The Crashlytics manager automatically registers Flask error handlers:

```python
@app.errorhandler(Exception)
def handle_exception(error):
    # Automatically logs all unhandled exceptions
    crashlytics_manager.log_exception(error, ...)
    return error_response

@app.errorhandler(404)
def handle_not_found(error):
    # Logs 404 errors for monitoring
    crashlytics_manager.log_error("404 Not Found", ...)
    return not_found_response
```

### Request Context

Automatic request context tracking:

```python
@app.before_request
def before_request():
    # Sets up request ID and timing
    g.request_id = str(uuid.uuid4())
    g.request_start_time = time.time()

@app.after_request
def after_request(response):
    # Logs slow requests as performance errors
    if request_duration > 5.0:
        crashlytics_manager.log_error("Slow request", ...)
```

## Background Processing

### Asynchronous Error Processing

Errors are processed asynchronously to avoid blocking the main application:

```python
# Enable background processing
manager = FirebaseCrashlyticsManager(enable_auto_collection=True)

# Errors are queued and processed in background thread
manager.log_error("Error message")  # Returns immediately
```

### Queue Management

- **Queue Size Monitoring**: Track queue size to detect backups
- **Automatic Retry**: Failed error submissions are retried
- **Graceful Shutdown**: Ensures all queued errors are processed on shutdown

## Error Analysis and Monitoring

### Error Patterns

Monitor common error patterns:

```python
# Get error statistics
stats = manager.get_error_stats()

# Analyze error trends
if stats['errors_by_severity']['FATAL'] > threshold:
    send_alert("High number of fatal errors detected")

# Monitor specific categories
api_errors = stats['errors_by_category'].get('API_ERROR', 0)
if api_errors > api_error_threshold:
    investigate_api_issues()
```

### Performance Monitoring

Automatic performance issue detection:

- **Slow Requests**: Requests taking longer than 5 seconds
- **High Error Rates**: Unusual spikes in error frequency
- **Queue Backups**: Error processing queue backing up

### Health Monitoring

System health status determination:

- **Healthy**: Normal operation, low error rates
- **Warning**: Elevated error rates or queue backups
- **Error**: Critical issues like background thread failure

## Security Considerations

### Data Privacy

- **User Data Protection**: User identifiers are hashed before transmission
- **Context Sanitization**: Sensitive data is filtered from error context
- **Access Control**: API endpoints require proper authentication

### Error Data Handling

- **Data Retention**: Error data is retained according to privacy policies
- **Anonymization**: Personal data is anonymized in error reports
- **Secure Transmission**: All error data is transmitted over HTTPS

## Best Practices

### Error Logging

1. **Use Appropriate Severity Levels**: Choose severity based on impact
2. **Provide Context**: Include relevant context information
3. **Avoid Sensitive Data**: Don't log passwords or personal information
4. **Use Categories**: Categorize errors for better organization

### Performance

1. **Enable Background Processing**: Use async processing for production
2. **Monitor Queue Size**: Watch for queue backups
3. **Set Reasonable Thresholds**: Configure appropriate error thresholds
4. **Regular Health Checks**: Monitor system health regularly

### Debugging

1. **Use Breadcrumbs**: Log user actions leading to errors
2. **Set Custom Keys**: Add relevant metadata to crash reports
3. **User Identification**: Associate errors with users when possible
4. **Test Crash Functionality**: Regularly test crash reporting

## Troubleshooting

### Common Issues

#### Background Thread Not Running

```python
# Check thread status
stats = manager.get_error_stats()
if not stats['background_thread_alive']:
    # Restart background processing
    manager._start_background_processing()
```

#### High Queue Size

```python
# Monitor queue size
if stats['queue_size'] > 50:
    # Investigate processing delays
    # Consider increasing processing capacity
```

#### Firebase Connection Issues

```python
# Check Firebase initialization
if not manager._initialized:
    # Reinitialize Firebase
    manager._initialize_firebase()
```

### Debugging Steps

1. **Check Error Logs**: Review application logs for Crashlytics errors
2. **Verify Configuration**: Ensure Firebase credentials are correct
3. **Test Connectivity**: Verify network connectivity to Firebase
4. **Monitor Health Endpoint**: Use health check endpoint for status
5. **Review Error Statistics**: Analyze error patterns and trends

## Integration with Monitoring Systems

### Alerting

Set up alerts based on error thresholds:

```python
def check_error_thresholds():
    stats = manager.get_error_stats()
    
    # Fatal error threshold
    if stats['errors_by_severity'].get('FATAL', 0) > 5:
        send_alert("High number of fatal errors")
    
    # Overall error rate threshold
    if stats['total_errors'] > 100:
        send_alert("High error rate detected")
```

### Dashboard Integration

Integrate with monitoring dashboards:

- **Error Rate Graphs**: Visualize error trends over time
- **Category Breakdown**: Show errors by category and severity
- **User Impact**: Track errors affecting specific users
- **Performance Metrics**: Monitor request performance

### Log Aggregation

Forward errors to log aggregation systems:

```python
# Custom log handler for external systems
class ExternalLogHandler(logging.Handler):
    def emit(self, record):
        # Forward to external logging system
        external_logger.log(record)

# Add to Crashlytics manager
manager.add_log_handler(ExternalLogHandler())
```

## Future Enhancements

### Planned Features

1. **Machine Learning Analysis**: Automatic error pattern detection
2. **Predictive Alerts**: Predict potential issues before they occur
3. **Advanced Filtering**: More sophisticated error filtering and grouping
4. **Integration APIs**: Better integration with external monitoring tools
5. **Real-time Dashboards**: Live error monitoring dashboards

### Scalability Improvements

1. **Distributed Processing**: Scale error processing across multiple instances
2. **Database Integration**: Store error data in database for analysis
3. **Batch Processing**: Efficient batch processing of error data
4. **Caching**: Cache frequently accessed error statistics

