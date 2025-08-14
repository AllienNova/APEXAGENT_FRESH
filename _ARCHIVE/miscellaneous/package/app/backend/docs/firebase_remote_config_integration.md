# Firebase Remote Config Integration for Aideon AI Lite

This document provides comprehensive information about the Firebase Remote Config integration for feature flags and dynamic configuration management in Aideon AI Lite.

## Overview

Firebase Remote Config allows you to change the behavior and appearance of your app without publishing an app update. This integration provides:

- **Feature Flags**: Enable/disable features dynamically
- **Configuration Parameters**: Adjust app behavior without redeployment
- **A/B Testing Support**: Test different configurations with different user groups
- **Real-time Updates**: Changes take effect immediately without app restart

## Architecture

### Components

1. **FirebaseRemoteConfigManager**: Core class for interacting with Firebase Remote Config
2. **FeatureFlagMiddleware**: Flask middleware for automatic feature flag loading
3. **API Endpoints**: REST API for managing configuration through admin dashboard
4. **Decorators**: Convenient decorators for feature-gated functionality

### Integration Points

- **Flask Application**: Middleware integration for automatic feature flag loading
- **Admin Dashboard**: Web interface for managing feature flags and configuration
- **API Layer**: Programmatic access to configuration management
- **Provider System**: Integration with LLM providers for tier-based features

## Configuration Structure

### Feature Flags

Feature flags are boolean values that enable/disable specific functionality:

```json
{
  "together_ai_enabled": true,
  "video_generation_enabled": true,
  "llamacoder_integration_enabled": false,
  "free_tier_enabled": true,
  "premium_tier_enabled": true,
  "analytics_enabled": true,
  "debug_mode": false,
  "maintenance_mode": false,
  "new_user_registration": true,
  "experimental_features": false
}
```

### Configuration Parameters

Configuration parameters control app behavior:

```json
{
  "max_concurrent_requests": 10,
  "request_timeout_seconds": 30,
  "cache_ttl_minutes": 60,
  "rate_limit_per_minute": 100,
  "free_tier_daily_limit": 50,
  "premium_tier_daily_limit": 1000,
  "maintenance_message": "System maintenance in progress. Please try again later.",
  "feature_announcement": "",
  "api_version": "v1"
}
```

## Usage Examples

### Basic Feature Flag Check

```python
from src.firebase_remote_config import get_remote_config_manager

manager = get_remote_config_manager()

# Check if a feature is enabled
if manager.is_feature_enabled("together_ai"):
    # Use Together AI provider
    pass
```

### Using Decorators

```python
from src.feature_flags import require_feature, require_together_ai

@require_together_ai
def generate_with_together_ai():
    # This function only runs if Together AI is enabled
    pass

@require_feature("video_generation")
def generate_video():
    # This function only runs if video generation is enabled
    pass
```

### Flask Middleware Integration

```python
from flask import Flask
from src.feature_flags import FeatureFlagMiddleware

app = Flask(__name__)
feature_flags = FeatureFlagMiddleware(app)

@app.route('/api/generate')
def generate():
    # Feature flags are automatically loaded into Flask's g object
    from flask import g
    
    if g.feature_flags.get('together_ai_enabled', False):
        # Use Together AI
        pass
```

### Configuration Parameter Access

```python
from src.firebase_remote_config import get_remote_config_manager

manager = get_remote_config_manager()

# Get rate limit
rate_limit = manager.get_rate_limit()

# Get tier-specific limits
free_limit = manager.get_tier_daily_limit('free')
premium_limit = manager.get_tier_daily_limit('premium')
```

## API Endpoints

### Feature Flags

- `GET /api/v1/config/feature-flags` - Get all feature flags
- `GET /api/v1/config/feature-flags/{name}` - Get specific feature flag
- `PUT /api/v1/config/feature-flags/{name}` - Update feature flag (admin only)

### Configuration Parameters

- `GET /api/v1/config/parameters` - Get all configuration parameters
- `GET /api/v1/config/parameters/{name}` - Get specific parameter
- `PUT /api/v1/config/parameters/{name}` - Update parameter (admin only)

### Management

- `PUT /api/v1/config/bulk-update` - Bulk update multiple items (admin only)
- `POST /api/v1/config/refresh` - Force cache refresh
- `POST /api/v1/config/initialize` - Initialize default configuration (admin only)
- `GET /api/v1/config/status` - Get configuration status

## Admin Dashboard Integration

The Firebase Remote Config integrates with the Aideon admin dashboard to provide:

1. **Feature Flag Management**: Toggle features on/off with immediate effect
2. **Configuration Tuning**: Adjust parameters like rate limits and timeouts
3. **Maintenance Mode**: Enable maintenance mode with custom messages
4. **Tier Management**: Configure limits for different user tiers
5. **Real-time Monitoring**: View current configuration status and cache info

## Security Considerations

### Authentication

- Admin endpoints require proper authentication
- Feature flag updates are restricted to admin users
- API keys are managed through the existing admin dashboard system

### Validation

- All configuration updates are validated before publishing
- Type checking ensures parameter values are in expected format
- Fallback values are used when remote config is unavailable

### Caching

- Local caching reduces Firebase API calls
- Cache TTL is configurable (default: 5 minutes)
- Automatic cache invalidation on updates
- Graceful fallback to cached values during outages

## Error Handling

### Fallback Behavior

When Firebase Remote Config is unavailable:

1. Use cached values if available
2. Fall back to default configuration
3. Log errors for monitoring
4. Continue operation with reduced functionality

### Monitoring

- Comprehensive logging for all configuration operations
- Error tracking for failed remote config calls
- Cache hit/miss metrics
- Configuration change audit trail

## Testing

### Unit Tests

Comprehensive test suite covers:

- Remote config manager functionality
- Feature flag middleware behavior
- API endpoint responses
- Error handling scenarios
- Cache management

### Integration Tests

- Firebase Remote Config connectivity
- End-to-end feature flag workflows
- Admin dashboard integration
- Performance under load

## Deployment

### Firebase Setup

1. Ensure Firebase project is configured
2. Set up service account credentials
3. Initialize default configuration
4. Configure security rules

### Application Integration

1. Install required dependencies
2. Configure Firebase credentials
3. Register middleware with Flask app
4. Set up API endpoints
5. Configure admin dashboard

### Environment Variables

```bash
# Firebase configuration
FIREBASE_PROJECT_ID=aideonlite-ai
FIREBASE_CREDENTIALS_PATH=/path/to/credentials.json

# Cache configuration
REMOTE_CONFIG_CACHE_TTL=300  # 5 minutes
```

## Best Practices

### Feature Flag Naming

- Use descriptive names: `together_ai_enabled` not `feature1`
- Follow consistent naming convention: `{feature}_enabled`
- Group related flags: `video_generation_enabled`, `video_quality_hd`

### Configuration Management

- Use semantic versioning for configuration changes
- Test configuration changes in staging environment
- Implement gradual rollouts for major changes
- Monitor application metrics after configuration updates

### Performance Optimization

- Use caching to reduce Firebase API calls
- Batch configuration updates when possible
- Monitor cache hit rates and adjust TTL accordingly
- Implement circuit breakers for Firebase connectivity

## Troubleshooting

### Common Issues

1. **Firebase Connection Errors**
   - Check service account credentials
   - Verify project ID configuration
   - Ensure network connectivity

2. **Cache Issues**
   - Force cache refresh via API
   - Check cache TTL configuration
   - Monitor cache hit rates

3. **Feature Flag Not Working**
   - Verify flag name spelling
   - Check default values
   - Ensure middleware is properly configured

### Debugging

Enable debug logging to troubleshoot issues:

```python
import logging
logging.getLogger('src.firebase_remote_config').setLevel(logging.DEBUG)
```

## Future Enhancements

### Planned Features

1. **A/B Testing Integration**: Support for user segmentation and testing
2. **Conditional Activation**: Feature flags based on user attributes
3. **Scheduled Changes**: Time-based configuration updates
4. **Configuration Validation**: Schema validation for complex configurations
5. **Metrics Integration**: Automatic metrics collection for feature usage

### Scalability Improvements

1. **Distributed Caching**: Redis integration for multi-instance deployments
2. **Configuration Versioning**: Track and rollback configuration changes
3. **Bulk Operations**: Efficient batch updates for large configurations
4. **Real-time Notifications**: WebSocket updates for configuration changes

