# API Key Management Documentation

## Overview

The API Key Management system for Aideon AI Lite provides comprehensive management of API keys for all integrated services. This dual-dashboard solution addresses the needs of both individual users with partial API key coverage and enterprise deployments with centralized management requirements.

## Dual Dashboard Architecture

### 1. User API Key Dashboard

- **Personal API key management** with clear status indicators
- **Service-specific key management** for all integrated services (OpenAI, Anthropic, Midjourney, etc.)
- **Flexible fallback preferences**:
  - Use system API keys when user keys are unavailable
  - Try alternative services with available keys
  - No fallback (only use provided keys)
- **Transparent system coverage information** showing which services are available
- **Usage tracking** for each service with detailed reporting

### 2. System Admin Dashboard

- **Complete control over all API keys** across the platform
- **Three enterprise control policies**:
  - IT department controls all API keys
  - Hybrid (IT controls critical keys, users add supplemental keys)
  - Users control their own API keys
- **Fallback prioritization system** (Primary, Secondary, Tertiary)
- **Comprehensive usage monitoring** across all services
- **Automatic key rotation** and security controls

## Partial API Key Management

### Granular API Key Tracking
- The system tracks which specific API keys each user has provided (OpenAI, Anthropic, Midjourney, etc.)
- Each service has its own status indicator in the user dashboard

### Mixed Credit System
- Operations using services where the user has provided their own API keys do NOT consume credits
- Operations using services where the user has NOT provided API keys WILL consume credits from their allocation
- This creates a hybrid model where some operations are "free" (using their keys) while others use credits

### Smart Service Routing
- When a task can be completed by multiple services, the system prioritizes services where the user has provided their own API keys
- This minimizes credit consumption while maintaining functionality

### Transparent Usage Dashboard
- Users see a clear breakdown of which services are using their own API keys vs. system keys
- Credit consumption is tracked per service with detailed reporting

### Flexible API Key Addition
- Users can add new API keys at any time to reduce credit consumption
- The system immediately switches to using their keys for that service

## Enterprise Account Management

For enterprise deployments, the solution offers three configurable control policies:

### 1. IT Department Control
- All API keys managed centrally by IT
- Users cannot add or modify API keys
- Consistent experience across the organization
- Centralized billing and usage tracking

### 2. Hybrid Control
- IT manages critical services
- Users can add supplemental keys for specific services
- Balanced approach for flexibility and control
- Partial credit consumption based on available keys

### 3. User Control
- Individual users manage their own keys
- Central monitoring and oversight
- Maximum flexibility for users
- Potential for reduced organizational costs

## Credit System Integration

- Monthly credit allocation based on subscription tier
- No daily limits or refreshes
- Users can purchase additional credits if they exhaust their allocation
- 10% discount on monthly subscription when users provide their own API keys
- Operations using user-provided API keys do not count against credit allocation
