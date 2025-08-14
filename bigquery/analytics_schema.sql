-- Aideon AI Lite Analytics Data Warehouse Schema
-- BigQuery Dataset: analytics
-- Purpose: Replace SQLite mock data with enterprise-grade analytics

-- =============================================
-- DATASET CREATION
-- =============================================

-- Create main analytics dataset
CREATE SCHEMA IF NOT EXISTS `aideon-ai-lite-prod.analytics`
OPTIONS (
  description = "Aideon AI Lite Analytics Data Warehouse",
  location = "US"
);

-- =============================================
-- CORE ANALYTICS TABLES
-- =============================================

-- Events table for real-time analytics data
CREATE OR REPLACE TABLE `aideon-ai-lite-prod.analytics.events` (
  event_id STRING NOT NULL,
  event_type STRING NOT NULL,
  event_data JSON,
  user_id STRING,
  session_id STRING,
  timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  ip_address STRING,
  user_agent STRING,
  referrer STRING,
  page_url STRING,
  device_type STRING,
  browser STRING,
  os STRING,
  country STRING,
  region STRING,
  city STRING,
  processed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(timestamp)
CLUSTER BY event_type, user_id
OPTIONS (
  description = "Real-time analytics events replacing mock data",
  partition_expiration_days = 1095  -- 3 years retention
);

-- Performance metrics table
CREATE OR REPLACE TABLE `aideon-ai-lite-prod.analytics.performance_metrics` (
  metric_id STRING NOT NULL,
  metric_type STRING NOT NULL,  -- 'response_time', 'throughput', 'error_rate', 'cpu_usage', 'memory_usage'
  metric_value FLOAT64 NOT NULL,
  metric_unit STRING NOT NULL,  -- 'ms', 'rps', 'percent', 'bytes'
  service_name STRING NOT NULL,
  endpoint STRING,
  method STRING,
  status_code INT64,
  timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  tags JSON,  -- Additional metadata
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(timestamp)
CLUSTER BY service_name, metric_type
OPTIONS (
  description = "Performance metrics replacing hardcoded 45.7ms mock values",
  partition_expiration_days = 365  -- 1 year retention
);

-- Business metrics table
CREATE OR REPLACE TABLE `aideon-ai-lite-prod.analytics.business_metrics` (
  metric_id STRING NOT NULL,
  metric_type STRING NOT NULL,  -- 'revenue', 'users', 'sessions', 'conversions', 'churn'
  metric_value FLOAT64 NOT NULL,
  metric_currency STRING,  -- For revenue metrics
  user_id STRING,
  subscription_tier STRING,
  payment_method STRING,
  timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  period_start TIMESTAMP,
  period_end TIMESTAMP,
  metadata JSON,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(timestamp)
CLUSTER BY metric_type, subscription_tier
OPTIONS (
  description = "Business metrics replacing hardcoded $1,250 mock values",
  partition_expiration_days = 2555  -- 7 years retention for financial data
);

-- User sessions table
CREATE OR REPLACE TABLE `aideon-ai-lite-prod.analytics.user_sessions` (
  session_id STRING NOT NULL,
  user_id STRING,
  start_time TIMESTAMP NOT NULL,
  end_time TIMESTAMP,
  duration_seconds INT64,
  page_views INT64 DEFAULT 0,
  events_count INT64 DEFAULT 0,
  revenue FLOAT64 DEFAULT 0.0,
  conversion_events ARRAY<STRING>,
  device_info JSON,
  location_info JSON,
  referrer_info JSON,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(start_time)
CLUSTER BY user_id
OPTIONS (
  description = "User session data for comprehensive analytics",
  partition_expiration_days = 1095  -- 3 years retention
);

-- Daily aggregated metrics
CREATE OR REPLACE TABLE `aideon-ai-lite-prod.analytics.daily_metrics` (
  date DATE NOT NULL,
  total_users INT64 DEFAULT 0,
  new_users INT64 DEFAULT 0,
  active_users INT64 DEFAULT 0,
  total_sessions INT64 DEFAULT 0,
  avg_session_duration FLOAT64 DEFAULT 0.0,
  total_page_views INT64 DEFAULT 0,
  total_events INT64 DEFAULT 0,
  total_revenue FLOAT64 DEFAULT 0.0,
  avg_response_time FLOAT64 DEFAULT 0.0,
  error_rate FLOAT64 DEFAULT 0.0,
  conversion_rate FLOAT64 DEFAULT 0.0,
  churn_rate FLOAT64 DEFAULT 0.0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY date
OPTIONS (
  description = "Daily aggregated metrics for trend analysis",
  partition_expiration_days = 2555  -- 7 years retention
);

-- =============================================
-- AI/ML ENHANCED TABLES
-- =============================================

-- User behavior patterns (for ML analysis)
CREATE OR REPLACE TABLE `aideon-ai-lite-prod.analytics.user_behavior_patterns` (
  pattern_id STRING NOT NULL,
  user_id STRING NOT NULL,
  pattern_type STRING NOT NULL,  -- 'usage_trend', 'feature_preference', 'churn_risk'
  pattern_data JSON NOT NULL,
  confidence_score FLOAT64,
  model_version STRING,
  timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  expires_at TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(timestamp)
CLUSTER BY user_id, pattern_type
OPTIONS (
  description = "ML-generated user behavior patterns for personalization",
  partition_expiration_days = 365
);

-- Anomaly detection results
CREATE OR REPLACE TABLE `aideon-ai-lite-prod.analytics.anomalies` (
  anomaly_id STRING NOT NULL,
  anomaly_type STRING NOT NULL,  -- 'performance', 'usage', 'revenue', 'security'
  severity STRING NOT NULL,  -- 'low', 'medium', 'high', 'critical'
  metric_name STRING NOT NULL,
  expected_value FLOAT64,
  actual_value FLOAT64,
  deviation_score FLOAT64,
  detection_model STRING,
  model_confidence FLOAT64,
  timestamp TIMESTAMP NOT NULL,
  resolved BOOLEAN DEFAULT FALSE,
  resolution_notes STRING,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(timestamp)
CLUSTER BY anomaly_type, severity
OPTIONS (
  description = "AI-powered anomaly detection replacing mock algorithms",
  partition_expiration_days = 1095
);

-- =============================================
-- INDEXES AND OPTIMIZATION
-- =============================================

-- Create search indexes for common queries
CREATE SEARCH INDEX events_search_idx
ON `aideon-ai-lite-prod.analytics.events`(ALL COLUMNS)
OPTIONS (
  description = "Full-text search index for events table"
);

-- =============================================
-- VIEWS FOR COMMON ANALYTICS QUERIES
-- =============================================

-- Real-time dashboard view
CREATE OR REPLACE VIEW `aideon-ai-lite-prod.analytics.realtime_dashboard` AS
SELECT
  DATE(timestamp) as date,
  COUNT(*) as total_events,
  COUNT(DISTINCT user_id) as unique_users,
  COUNT(DISTINCT session_id) as total_sessions,
  COUNTIF(event_type = 'conversion') as conversions,
  ROUND(AVG(CASE WHEN event_type = 'page_load' THEN 
    CAST(JSON_EXTRACT_SCALAR(event_data, '$.load_time') AS FLOAT64) END), 2) as avg_load_time,
  ROUND(COUNTIF(event_type = 'error') * 100.0 / COUNT(*), 2) as error_rate_percent
FROM `aideon-ai-lite-prod.analytics.events`
WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
GROUP BY DATE(timestamp)
ORDER BY date DESC;

-- Performance metrics summary view
CREATE OR REPLACE VIEW `aideon-ai-lite-prod.analytics.performance_summary` AS
SELECT
  service_name,
  metric_type,
  ROUND(AVG(metric_value), 2) as avg_value,
  ROUND(MIN(metric_value), 2) as min_value,
  ROUND(MAX(metric_value), 2) as max_value,
  ROUND(STDDEV(metric_value), 2) as stddev_value,
  COUNT(*) as sample_count,
  MAX(timestamp) as last_updated
FROM `aideon-ai-lite-prod.analytics.performance_metrics`
WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
GROUP BY service_name, metric_type
ORDER BY service_name, metric_type;

-- Business metrics summary view
CREATE OR REPLACE VIEW `aideon-ai-lite-prod.analytics.business_summary` AS
SELECT
  DATE(timestamp) as date,
  metric_type,
  SUM(metric_value) as total_value,
  AVG(metric_value) as avg_value,
  COUNT(*) as transaction_count,
  COUNT(DISTINCT user_id) as unique_users
FROM `aideon-ai-lite-prod.analytics.business_metrics`
WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY DATE(timestamp), metric_type
ORDER BY date DESC, metric_type;

-- =============================================
-- MACHINE LEARNING MODELS SETUP
-- =============================================

-- User churn prediction model
CREATE OR REPLACE MODEL `aideon-ai-lite-prod.analytics.churn_prediction_model`
OPTIONS (
  model_type = 'LOGISTIC_REG',
  input_label_cols = ['will_churn'],
  auto_class_weights = TRUE
) AS
SELECT
  user_id,
  EXTRACT(DAYOFWEEK FROM last_session) as last_session_day,
  days_since_last_session,
  total_sessions,
  avg_session_duration,
  total_revenue,
  feature_usage_score,
  support_tickets_count,
  CASE WHEN days_since_last_session > 30 THEN TRUE ELSE FALSE END as will_churn
FROM (
  SELECT
    user_id,
    MAX(start_time) as last_session,
    DATE_DIFF(CURRENT_DATE(), DATE(MAX(start_time)), DAY) as days_since_last_session,
    COUNT(*) as total_sessions,
    AVG(duration_seconds) as avg_session_duration,
    SUM(revenue) as total_revenue,
    -- Placeholder for feature usage score calculation
    0.5 as feature_usage_score,
    -- Placeholder for support tickets count
    0 as support_tickets_count
  FROM `aideon-ai-lite-prod.analytics.user_sessions`
  WHERE start_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
  GROUP BY user_id
  HAVING COUNT(*) >= 5  -- Only users with sufficient data
);

-- Revenue forecasting model
CREATE OR REPLACE MODEL `aideon-ai-lite-prod.analytics.revenue_forecast_model`
OPTIONS (
  model_type = 'ARIMA_PLUS',
  time_series_timestamp_col = 'date',
  time_series_data_col = 'daily_revenue'
) AS
SELECT
  date,
  SUM(metric_value) as daily_revenue
FROM `aideon-ai-lite-prod.analytics.business_metrics`
WHERE metric_type = 'revenue'
  AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 365 DAY)
GROUP BY date
ORDER BY date;

-- Usage trend analysis model
CREATE OR REPLACE MODEL `aideon-ai-lite-prod.analytics.usage_trend_model`
OPTIONS (
  model_type = 'ARIMA_PLUS',
  time_series_timestamp_col = 'date',
  time_series_data_col = 'daily_active_users'
) AS
SELECT
  date,
  active_users as daily_active_users
FROM `aideon-ai-lite-prod.analytics.daily_metrics`
WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 365 DAY)
ORDER BY date;

