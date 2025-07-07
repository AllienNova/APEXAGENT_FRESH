# Aideon AI Lite Admin Dashboard Guide

## Overview

The Aideon AI Lite Admin Dashboard provides a comprehensive interface for managing all aspects of the Aideon AI Lite platform. This modern, high-performance dashboard enables administrators to monitor system health, manage API integrations, configure application settings, and control user access.

## Key Features

### API Management
- **Credential Management**: Securely store and manage API keys for all integrated services
- **Provider Configuration**: Configure settings for each API provider
- **Usage Monitoring**: Track API usage, costs, and rate limits
- **Performance Analytics**: Monitor API response times and success rates

### App Management
- **Configuration Management**: Modify application settings and parameters
- **Resource Allocation**: Control resource distribution across system components
- **Deployment Management**: Track deployment history and manage versions
- **System Information**: View detailed system information and status

### Health Monitoring
- **Real-time Metrics**: Monitor system performance metrics in real time
- **Historical Data**: View historical performance data with customizable time ranges
- **Alert Management**: Configure alerts for critical system events
- **Health Scoring**: Track overall system health with comprehensive scoring

### User Management
- **Role-based Access Control**: Manage user permissions with four predefined roles
- **User Administration**: Create, update, and manage user accounts
- **Activity Tracking**: Monitor user activity and system access
- **Security Controls**: Enforce password policies and access restrictions

## Architecture

The Admin Dashboard follows a modern, modular architecture:

1. **Frontend**: React with TypeScript and Tailwind CSS
   - Component-based UI with reusable elements
   - Responsive design for all device sizes
   - Real-time data visualization
   - Dark mode support

2. **Backend**: Node.js with Express
   - RESTful API endpoints
   - JWT authentication with refresh token rotation
   - Role-based access control
   - Comprehensive error handling

3. **Integration**: Seamless connection with Aideon AI Lite core system
   - Direct access to system metrics and configuration
   - Proxy support for core system API access
   - Event-based real-time updates

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **Role-based Access Control**: Granular permission management
- **HTTPS Encryption**: All communications encrypted in transit
- **Rate Limiting**: Protection against brute force and DoS attacks
- **Input Validation**: Comprehensive validation of all user inputs
- **Audit Logging**: Detailed logs of all administrative actions

## User Roles

1. **Super Admin**: Full system access with all privileges
2. **Admin**: Configuration and monitoring access
3. **API Manager**: API credential and usage management
4. **Viewer**: Read-only access to dashboards and reports

## Getting Started

### Accessing the Dashboard

The Admin Dashboard is available at:
```
http://localhost:3000
```

Default credentials:
- Username: `admin`
- Password: `admin123`

**Important**: Change the default password immediately after first login.

### Navigation

The dashboard is organized into the following main sections:

1. **Dashboard**: Overview of system status and key metrics
2. **API Management**: Manage API providers and credentials
3. **App Management**: Configure application settings
4. **Health Monitoring**: Monitor system health and performance
5. **User Management**: Manage user accounts and permissions
6. **Settings**: Configure dashboard preferences

### Common Tasks

#### Adding a New API Credential

1. Navigate to **API Management** > **Credentials**
2. Click **Add Credential**
3. Select the API provider
4. Enter the credential name and API key
5. Set active status
6. Click **Save**

#### Configuring Alert Thresholds

1. Navigate to **Health Monitoring** > **Alerts**
2. Click **Add Alert Configuration**
3. Select the metric type
4. Set the condition and threshold
5. Select severity level
6. Click **Save**

#### Adding a New User

1. Navigate to **User Management** > **Users**
2. Click **Add User**
3. Enter user details (username, email, etc.)
4. Select role
5. Set initial password
6. Click **Save**

## Performance Considerations

The Admin Dashboard is designed for optimal performance:

- Efficient data loading with pagination
- Real-time updates via WebSockets
- Lazy loading of components
- Optimized bundle size
- Response caching for frequently accessed data

## Troubleshooting

### Common Issues

1. **Dashboard Not Loading**
   - Check that the admin server is running
   - Verify network connectivity
   - Clear browser cache

2. **Authentication Failures**
   - Verify credentials
   - Check for expired tokens
   - Ensure user account is active

3. **Missing Data**
   - Verify data collection services are running
   - Check time range filters
   - Confirm user has appropriate permissions

### Support

For additional support, contact the system administrator or refer to the detailed technical documentation.

## Technical Documentation

For more detailed technical information, refer to:

- [API Management Documentation](/documentation/api_management.md)
- [App Management Documentation](/documentation/app_management.md)
- [Health Monitoring Documentation](/documentation/health_monitoring.md)
- [User Management Documentation](/documentation/user_management.md)
