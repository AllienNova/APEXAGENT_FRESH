#!/bin/bash

# Aideon AI Lite BigQuery Setup Script
# Purpose: Initialize BigQuery analytics warehouse
# Project: aideonlite-ai (LIVE PRODUCTION)
# Replaces: SQLite mock data with enterprise-grade analytics

set -e

echo "🔥 BIGQUERY ANALYTICS WAREHOUSE SETUP"
echo "======================================"

# Configuration
PROJECT_ID="aideonlite-ai"
DATASET_ID="analytics"
LOCATION="US"

echo "📊 Project: $PROJECT_ID"
echo "📊 Dataset: $DATASET_ID"
echo "📊 Location: $LOCATION"
echo ""

# Check if gcloud is installed and authenticated
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI not found. Please install Google Cloud SDK."
    exit 1
fi

# Set the project
echo "🔧 Setting GCP project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable bigquery.googleapis.com
gcloud services enable bigquerydatatransfer.googleapis.com
gcloud services enable bigqueryreservation.googleapis.com

# Create dataset if it doesn't exist
echo "🔧 Creating BigQuery dataset..."
bq mk --location=$LOCATION --description="Aideon AI Lite Analytics Data Warehouse" $PROJECT_ID:$DATASET_ID || echo "Dataset already exists"

# Execute schema creation
echo "🔧 Creating tables and views..."
bq query --use_legacy_sql=false < analytics_schema.sql

# Create sample data for testing
echo "🔧 Inserting sample data for testing..."

# Sample events data
bq query --use_legacy_sql=false "
INSERT INTO \`$PROJECT_ID.$DATASET_ID.events\` (
  event_id, event_type, event_data, user_id, session_id, timestamp, 
  device_type, browser, os, country
) VALUES
  ('evt_001', 'page_view', JSON '{\"page\": \"/dashboard\", \"load_time\": 1.2}', 'user_001', 'sess_001', CURRENT_TIMESTAMP(), 'desktop', 'chrome', 'windows', 'US'),
  ('evt_002', 'api_call', JSON '{\"endpoint\": \"/api/analytics\", \"response_time\": 45.7}', 'user_001', 'sess_001', CURRENT_TIMESTAMP(), 'desktop', 'chrome', 'windows', 'US'),
  ('evt_003', 'conversion', JSON '{\"plan\": \"premium\", \"amount\": 29.99}', 'user_002', 'sess_002', CURRENT_TIMESTAMP(), 'mobile', 'safari', 'ios', 'CA'),
  ('evt_004', 'error', JSON '{\"error_type\": \"api_timeout\", \"endpoint\": \"/api/llm\"}', 'user_003', 'sess_003', CURRENT_TIMESTAMP(), 'desktop', 'firefox', 'linux', 'UK')
"

# Sample performance metrics
bq query --use_legacy_sql=false "
INSERT INTO \`$PROJECT_ID.$DATASET_ID.performance_metrics\` (
  metric_id, metric_type, metric_value, metric_unit, service_name, endpoint, timestamp
) VALUES
  ('perf_001', 'response_time', 45.7, 'ms', 'api_gateway', '/api/analytics', CURRENT_TIMESTAMP()),
  ('perf_002', 'response_time', 123.4, 'ms', 'llm_service', '/api/llm/openai', CURRENT_TIMESTAMP()),
  ('perf_003', 'throughput', 1250.0, 'rps', 'api_gateway', '/api/analytics', CURRENT_TIMESTAMP()),
  ('perf_004', 'error_rate', 0.02, 'percent', 'api_gateway', '/api/analytics', CURRENT_TIMESTAMP()),
  ('perf_005', 'cpu_usage', 65.3, 'percent', 'backend_service', NULL, CURRENT_TIMESTAMP()),
  ('perf_006', 'memory_usage', 78.9, 'percent', 'backend_service', NULL, CURRENT_TIMESTAMP())
"

# Sample business metrics
bq query --use_legacy_sql=false "
INSERT INTO \`$PROJECT_ID.$DATASET_ID.business_metrics\` (
  metric_id, metric_type, metric_value, metric_currency, user_id, subscription_tier, timestamp
) VALUES
  ('biz_001', 'revenue', 29.99, 'USD', 'user_002', 'premium', CURRENT_TIMESTAMP()),
  ('biz_002', 'revenue', 9.99, 'USD', 'user_004', 'basic', CURRENT_TIMESTAMP()),
  ('biz_003', 'revenue', 99.99, 'USD', 'user_005', 'enterprise', CURRENT_TIMESTAMP()),
  ('biz_004', 'users', 1.0, NULL, 'user_002', 'premium', CURRENT_TIMESTAMP()),
  ('biz_005', 'sessions', 1.0, NULL, 'user_002', 'premium', CURRENT_TIMESTAMP()),
  ('biz_006', 'conversions', 1.0, NULL, 'user_002', 'premium', CURRENT_TIMESTAMP())
"

# Sample user sessions
bq query --use_legacy_sql=false "
INSERT INTO \`$PROJECT_ID.$DATASET_ID.user_sessions\` (
  session_id, user_id, start_time, end_time, duration_seconds, page_views, events_count, revenue
) VALUES
  ('sess_001', 'user_001', TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 2 HOUR), TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR), 3600, 15, 25, 0.0),
  ('sess_002', 'user_002', TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR), CURRENT_TIMESTAMP(), 3600, 8, 12, 29.99),
  ('sess_003', 'user_003', TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 MINUTE), CURRENT_TIMESTAMP(), 1800, 5, 8, 0.0)
"

# Update daily metrics
echo "🔧 Updating daily metrics..."
bq query --use_legacy_sql=false "
INSERT INTO \`$PROJECT_ID.$DATASET_ID.daily_metrics\` (
  date, total_users, new_users, active_users, total_sessions, avg_session_duration,
  total_page_views, total_events, total_revenue, avg_response_time, error_rate, conversion_rate
)
SELECT
  CURRENT_DATE() as date,
  COUNT(DISTINCT user_id) as total_users,
  COUNT(DISTINCT user_id) as new_users,  -- Simplified for sample data
  COUNT(DISTINCT user_id) as active_users,
  COUNT(DISTINCT session_id) as total_sessions,
  AVG(duration_seconds) as avg_session_duration,
  SUM(page_views) as total_page_views,
  SUM(events_count) as total_events,
  SUM(revenue) as total_revenue,
  84.5 as avg_response_time,  -- Sample average
  0.02 as error_rate,  -- 2% error rate
  0.33 as conversion_rate  -- 33% conversion rate from sample data
FROM \`$PROJECT_ID.$DATASET_ID.user_sessions\`
WHERE DATE(start_time) = CURRENT_DATE()
"

# Verify setup
echo "🔧 Verifying BigQuery setup..."
echo ""
echo "📊 Events table:"
bq query --use_legacy_sql=false "SELECT COUNT(*) as event_count FROM \`$PROJECT_ID.$DATASET_ID.events\`"

echo "📊 Performance metrics table:"
bq query --use_legacy_sql=false "SELECT COUNT(*) as metrics_count FROM \`$PROJECT_ID.$DATASET_ID.performance_metrics\`"

echo "📊 Business metrics table:"
bq query --use_legacy_sql=false "SELECT COUNT(*) as business_count FROM \`$PROJECT_ID.$DATASET_ID.business_metrics\`"

echo "📊 User sessions table:"
bq query --use_legacy_sql=false "SELECT COUNT(*) as sessions_count FROM \`$PROJECT_ID.$DATASET_ID.user_sessions\`"

echo "📊 Daily metrics table:"
bq query --use_legacy_sql=false "SELECT COUNT(*) as daily_count FROM \`$PROJECT_ID.$DATASET_ID.daily_metrics\`"

echo ""
echo "✅ BigQuery Analytics Warehouse Setup Complete!"
echo "📊 Dataset: $PROJECT_ID:$DATASET_ID"
echo "🔗 Console: https://console.cloud.google.com/bigquery?project=$PROJECT_ID"
echo ""
echo "🎯 Next Steps:"
echo "1. Update Cloud Functions to use BigQuery instead of mock data"
echo "2. Configure real-time data streaming from Firebase"
echo "3. Set up Data Studio dashboards"
echo "4. Train ML models with real data"

