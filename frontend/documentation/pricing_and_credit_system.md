# Pricing and Credit System Documentation

## Overview

The Aideon AI Lite platform uses a subscription-based pricing model with a credit system for usage. This document outlines the complete pricing structure, credit allocations, and management policies.

## Four-Tier Pricing Structure

### Basic Tier
- **Monthly Price**: $59.99 ($29.99 with own API keys)
- **Initial Credits**: 2,000 credits per month
- **Features**:
  - Access to up to 2 standard LLMs
  - Document creation and editing capabilities
  - Basic support

### Pro Tier
- **Monthly Price**: $149.99 ($99.99 with own API keys)
- **Initial Credits**: 5,000 credits per month
- **Features**:
  - Access to 3 standard LLMs
  - Access to 2 advanced LLMs (High reasoning)
  - Document creation and editing capabilities
  - Priority support

### Expert Tier
- **Monthly Price**: $249.99 ($149.99 with own API keys)
- **Initial Credits**: 15,000 credits per month
- **Features**:
  - Access to all LLMs
  - Advanced document creation and editing capabilities
  - 24/7 dedicated support

### Enterprise Tier
- **Monthly Price**: Custom pricing
- **Initial Credits**: Custom allocation
- **Features**:
  - Access to all LLMs
  - Advanced document creation and editing capabilities
  - Dedicated account manager
  - Custom integrations

## Credit System Rules

### Credit Allocation
- Each tier comes with a fixed initial credit allocation per month
- No daily refresh of credits - credits are allocated for the entire month
- Credits do not automatically roll over to the next month

### Credit Usage
- Operations using the user's own API keys do NOT consume credits
- Operations using Aideon's API keys DO consume credits
- Different operations consume different amounts of credits based on complexity and resource usage

### Additional Credits
- Users can purchase additional credits at any time if they exhaust their monthly allocation
- Additional credits are available at the same rates for all users regardless of tier
- No limit on how many additional credits can be purchased

## API Key Management

### User-Provided API Keys
- Users receive a 10% discount on their monthly subscription when they provide their own API keys
- Operations performed using user-provided API keys do not count against credit allocation
- Users can provide keys for some services but not others (partial coverage)

### Partial API Key Coverage
- The system tracks which specific API keys each user has provided
- When a user has some but not all API keys:
  - Operations using services where they have provided keys do NOT consume credits
  - Operations using services where they have NOT provided keys DO consume credits
  - The system prioritizes using services where the user has provided keys when possible

## Enterprise Charging Options

### Per Team Member
- Enterprise accounts can be charged based on the number of team members
- Each team member receives their own credit allocation
- Team-wide pooling of credits is available as an option

### Per Computer
- Alternative charging model based on number of computers/devices
- Each device receives its own credit allocation
- Organization-wide pooling of credits is available as an option

## Transparent Reporting

- Users receive detailed reports of credit usage by service
- Clear distinction between operations using user keys vs. system keys
- Real-time credit balance and usage tracking
- Predictive analytics for credit usage trends
