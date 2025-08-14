-- Aideon AI Lite Cloud SQL PostgreSQL Schema
-- Purpose: Enterprise-grade relational database for transactional data
-- Complements: BigQuery analytics warehouse for OLAP workloads

-- =============================================
-- DATABASE CONFIGURATION
-- =============================================

-- Create database (executed via gcloud command)
-- CREATE DATABASE aideon_ai_lite_prod;

-- Connect to the database
\c aideon_ai_lite_prod;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =============================================
-- USER MANAGEMENT AND AUTHENTICATION
-- =============================================

-- Users table for authentication and profile management
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    display_name VARCHAR(200),
    avatar_url TEXT,
    email_verified BOOLEAN DEFAULT FALSE,
    phone_number VARCHAR(20),
    phone_verified BOOLEAN DEFAULT FALSE,
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    two_factor_secret VARCHAR(32),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'deleted')),
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'admin', 'enterprise_admin')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP WITH TIME ZONE,
    login_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- User sessions for authentication management
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    refresh_token VARCHAR(255) UNIQUE,
    ip_address INET,
    user_agent TEXT,
    device_info JSONB,
    location_info JSONB,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_accessed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- API keys for programmatic access
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    key_name VARCHAR(100) NOT NULL,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    key_prefix VARCHAR(20) NOT NULL,
    permissions JSONB DEFAULT '[]'::jsonb,
    rate_limit_per_minute INTEGER DEFAULT 1000,
    rate_limit_per_day INTEGER DEFAULT 100000,
    usage_count BIGINT DEFAULT 0,
    last_used_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- SUBSCRIPTION AND BILLING
-- =============================================

-- Subscription plans
CREATE TABLE subscription_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    display_name VARCHAR(200) NOT NULL,
    description TEXT,
    price_monthly DECIMAL(10,2),
    price_yearly DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'USD',
    features JSONB DEFAULT '[]'::jsonb,
    limits JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User subscriptions
CREATE TABLE user_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id UUID NOT NULL REFERENCES subscription_plans(id),
    stripe_subscription_id VARCHAR(255) UNIQUE,
    stripe_customer_id VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'canceled', 'past_due', 'unpaid', 'trialing')),
    billing_cycle VARCHAR(10) DEFAULT 'monthly' CHECK (billing_cycle IN ('monthly', 'yearly')),
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end TIMESTAMP WITH TIME ZONE,
    trial_start TIMESTAMP WITH TIME ZONE,
    trial_end TIMESTAMP WITH TIME ZONE,
    canceled_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Payment transactions
CREATE TABLE payment_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES user_subscriptions(id),
    stripe_payment_intent_id VARCHAR(255) UNIQUE,
    stripe_charge_id VARCHAR(255),
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'succeeded', 'failed', 'canceled', 'refunded')),
    payment_method VARCHAR(50),
    description TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- CREDIT SYSTEM AND USAGE TRACKING
-- =============================================

-- Credit packages
CREATE TABLE credit_packages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    display_name VARCHAR(200) NOT NULL,
    description TEXT,
    credit_amount INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    bonus_credits INTEGER DEFAULT 0,
    expires_days INTEGER, -- NULL means no expiration
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User credit balances
CREATE TABLE user_credits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    total_credits INTEGER DEFAULT 0,
    used_credits INTEGER DEFAULT 0,
    available_credits INTEGER GENERATED ALWAYS AS (total_credits - used_credits) STORED,
    last_purchase_at TIMESTAMP WITH TIME ZONE,
    last_usage_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- Credit transactions for detailed tracking
CREATE TABLE credit_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('purchase', 'usage', 'refund', 'bonus', 'expiration')),
    amount INTEGER NOT NULL, -- Positive for additions, negative for usage
    balance_before INTEGER NOT NULL,
    balance_after INTEGER NOT NULL,
    description TEXT,
    reference_id UUID, -- Reference to payment, API call, etc.
    reference_type VARCHAR(50), -- 'payment', 'api_call', 'refund', etc.
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- AI/LLM PROVIDER MANAGEMENT
-- =============================================

-- LLM providers configuration
CREATE TABLE llm_providers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    display_name VARCHAR(200) NOT NULL,
    description TEXT,
    api_endpoint TEXT,
    authentication_type VARCHAR(50) DEFAULT 'api_key',
    supported_models JSONB DEFAULT '[]'::jsonb,
    pricing_info JSONB DEFAULT '{}'::jsonb,
    rate_limits JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User LLM provider configurations
CREATE TABLE user_llm_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider_id UUID NOT NULL REFERENCES llm_providers(id),
    api_key_encrypted TEXT, -- Encrypted user's API key
    model_preferences JSONB DEFAULT '{}'::jsonb,
    usage_limits JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, provider_id)
);

-- API usage tracking
CREATE TABLE api_usage_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    api_key_id UUID REFERENCES api_keys(id),
    provider_id UUID REFERENCES llm_providers(id),
    model_name VARCHAR(100),
    endpoint VARCHAR(200),
    request_tokens INTEGER,
    response_tokens INTEGER,
    total_tokens INTEGER,
    cost_credits INTEGER,
    cost_usd DECIMAL(10,4),
    response_time_ms INTEGER,
    status_code INTEGER,
    error_message TEXT,
    request_metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- PROJECT AND WORKSPACE MANAGEMENT
-- =============================================

-- User projects/workspaces
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    project_type VARCHAR(50) DEFAULT 'general',
    settings JSONB DEFAULT '{}'::jsonb,
    is_public BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Project collaborators
CREATE TABLE project_collaborators (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'viewer' CHECK (role IN ('owner', 'editor', 'viewer')),
    permissions JSONB DEFAULT '[]'::jsonb,
    invited_by UUID REFERENCES users(id),
    invited_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    accepted_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(project_id, user_id)
);

-- Project files/documents
CREATE TABLE project_files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_type VARCHAR(50),
    file_size BIGINT,
    content_hash VARCHAR(64),
    storage_provider VARCHAR(50) DEFAULT 'firebase_storage',
    storage_path TEXT,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- SYSTEM CONFIGURATION AND SETTINGS
-- =============================================

-- System settings
CREATE TABLE system_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value JSONB NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Feature flags
CREATE TABLE feature_flags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    flag_name VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(200),
    description TEXT,
    is_enabled BOOLEAN DEFAULT FALSE,
    rollout_percentage INTEGER DEFAULT 0 CHECK (rollout_percentage >= 0 AND rollout_percentage <= 100),
    target_users JSONB DEFAULT '[]'::jsonb,
    conditions JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- AUDIT AND LOGGING
-- =============================================

-- Audit logs for security and compliance
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    session_id UUID,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- System health monitoring
CREATE TABLE system_health_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_name VARCHAR(100) NOT NULL,
    check_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'healthy' CHECK (status IN ('healthy', 'degraded', 'unhealthy')),
    response_time_ms INTEGER,
    error_message TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- INDEXES FOR PERFORMANCE
-- =============================================

-- User indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Session indexes
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);

-- API key indexes
CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_api_keys_hash ON api_keys(key_hash);
CREATE INDEX idx_api_keys_active ON api_keys(is_active);

-- Subscription indexes
CREATE INDEX idx_user_subscriptions_user_id ON user_subscriptions(user_id);
CREATE INDEX idx_user_subscriptions_status ON user_subscriptions(status);
CREATE INDEX idx_user_subscriptions_period_end ON user_subscriptions(current_period_end);

-- Credit indexes
CREATE INDEX idx_user_credits_user_id ON user_credits(user_id);
CREATE INDEX idx_credit_transactions_user_id ON credit_transactions(user_id);
CREATE INDEX idx_credit_transactions_created_at ON credit_transactions(created_at);

-- Usage tracking indexes
CREATE INDEX idx_api_usage_logs_user_id ON api_usage_logs(user_id);
CREATE INDEX idx_api_usage_logs_created_at ON api_usage_logs(created_at);
CREATE INDEX idx_api_usage_logs_provider_id ON api_usage_logs(provider_id);

-- Project indexes
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_created_at ON projects(created_at);
CREATE INDEX idx_project_collaborators_project_id ON project_collaborators(project_id);
CREATE INDEX idx_project_collaborators_user_id ON project_collaborators(user_id);

-- Audit indexes
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);

-- =============================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- =============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers to relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_subscription_plans_updated_at BEFORE UPDATE ON subscription_plans FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_subscriptions_updated_at BEFORE UPDATE ON user_subscriptions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_credit_packages_updated_at BEFORE UPDATE ON credit_packages FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_credits_updated_at BEFORE UPDATE ON user_credits FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_llm_providers_updated_at BEFORE UPDATE ON llm_providers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_llm_configs_updated_at BEFORE UPDATE ON user_llm_configs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_project_files_updated_at BEFORE UPDATE ON project_files FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_system_settings_updated_at BEFORE UPDATE ON system_settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_feature_flags_updated_at BEFORE UPDATE ON feature_flags FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to update credit balance
CREATE OR REPLACE FUNCTION update_credit_balance()
RETURNS TRIGGER AS $$
BEGIN
    -- Update user credits balance when credit transaction is inserted
    IF TG_OP = 'INSERT' THEN
        UPDATE user_credits 
        SET 
            total_credits = CASE 
                WHEN NEW.transaction_type IN ('purchase', 'bonus') THEN total_credits + NEW.amount
                ELSE total_credits
            END,
            used_credits = CASE 
                WHEN NEW.transaction_type = 'usage' THEN used_credits + ABS(NEW.amount)
                ELSE used_credits
            END,
            last_purchase_at = CASE 
                WHEN NEW.transaction_type = 'purchase' THEN NEW.created_at
                ELSE last_purchase_at
            END,
            last_usage_at = CASE 
                WHEN NEW.transaction_type = 'usage' THEN NEW.created_at
                ELSE last_usage_at
            END,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = NEW.user_id;
        
        -- Create user_credits record if it doesn't exist
        INSERT INTO user_credits (user_id, total_credits, used_credits)
        SELECT NEW.user_id, 
               CASE WHEN NEW.transaction_type IN ('purchase', 'bonus') THEN NEW.amount ELSE 0 END,
               CASE WHEN NEW.transaction_type = 'usage' THEN ABS(NEW.amount) ELSE 0 END
        WHERE NOT EXISTS (SELECT 1 FROM user_credits WHERE user_id = NEW.user_id);
    END IF;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ language 'plpgsql';

-- Apply credit balance trigger
CREATE TRIGGER update_credit_balance_trigger 
    AFTER INSERT ON credit_transactions 
    FOR EACH ROW EXECUTE FUNCTION update_credit_balance();

-- =============================================
-- INITIAL DATA SETUP
-- =============================================

-- Insert default subscription plans
INSERT INTO subscription_plans (name, display_name, description, price_monthly, price_yearly, features, limits) VALUES
('free', 'Free Plan', 'Perfect for getting started with AI assistance', 0.00, 0.00, 
 '["Basic AI chat", "5 projects", "Community support"]'::jsonb,
 '{"projects": 5, "api_calls_per_month": 1000, "storage_gb": 1}'::jsonb),
('basic', 'Basic Plan', 'Enhanced features for regular users', 9.99, 99.99,
 '["Advanced AI chat", "Unlimited projects", "Email support", "API access"]'::jsonb,
 '{"projects": -1, "api_calls_per_month": 10000, "storage_gb": 10}'::jsonb),
('premium', 'Premium Plan', 'Professional features for power users', 29.99, 299.99,
 '["All Basic features", "Priority support", "Advanced analytics", "Custom integrations"]'::jsonb,
 '{"projects": -1, "api_calls_per_month": 100000, "storage_gb": 100}'::jsonb),
('enterprise', 'Enterprise Plan', 'Full-featured solution for organizations', 99.99, 999.99,
 '["All Premium features", "Dedicated support", "SSO", "Custom deployment", "SLA"]'::jsonb,
 '{"projects": -1, "api_calls_per_month": -1, "storage_gb": 1000}'::jsonb);

-- Insert default credit packages
INSERT INTO credit_packages (name, display_name, description, credit_amount, price, bonus_credits) VALUES
('starter', 'Starter Pack', '1,000 credits for light usage', 1000, 9.99, 100),
('standard', 'Standard Pack', '5,000 credits with bonus', 5000, 39.99, 1000),
('premium', 'Premium Pack', '15,000 credits with extra bonus', 15000, 99.99, 5000),
('enterprise', 'Enterprise Pack', '50,000 credits for heavy usage', 50000, 299.99, 20000);

-- Insert default LLM providers
INSERT INTO llm_providers (name, display_name, description, supported_models, pricing_info) VALUES
('openai', 'OpenAI', 'GPT models from OpenAI', 
 '["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"]'::jsonb,
 '{"gpt-4": {"input": 0.03, "output": 0.06}, "gpt-3.5-turbo": {"input": 0.001, "output": 0.002}}'::jsonb),
('anthropic', 'Anthropic', 'Claude models from Anthropic',
 '["claude-3-opus", "claude-3-sonnet", "claude-3-haiku", "claude-2"]'::jsonb,
 '{"claude-3-opus": {"input": 0.015, "output": 0.075}, "claude-3-sonnet": {"input": 0.003, "output": 0.015}}'::jsonb),
('google', 'Google AI', 'Gemini models from Google',
 '["gemini-pro", "gemini-pro-vision", "gemini-ultra"]'::jsonb,
 '{"gemini-pro": {"input": 0.00025, "output": 0.0005}}'::jsonb),
('aws_bedrock', 'AWS Bedrock', 'Various models via AWS Bedrock',
 '["amazon-titan", "ai21-jurassic", "cohere-command", "meta-llama"]'::jsonb,
 '{"amazon-titan": {"input": 0.0008, "output": 0.0016}}'::jsonb);

-- Insert default system settings
INSERT INTO system_settings (setting_key, setting_value, description, is_public) VALUES
('app_name', '"Aideon AI Lite"', 'Application name', true),
('app_version', '"1.0.0"', 'Current application version', true),
('maintenance_mode', 'false', 'Enable maintenance mode', false),
('registration_enabled', 'true', 'Allow new user registration', false),
('default_credits', '1000', 'Default credits for new users', false),
('max_file_size_mb', '100', 'Maximum file upload size in MB', false),
('session_timeout_hours', '24', 'User session timeout in hours', false);

-- Insert default feature flags
INSERT INTO feature_flags (flag_name, display_name, description, is_enabled, rollout_percentage) VALUES
('advanced_analytics', 'Advanced Analytics', 'Enable advanced analytics dashboard', true, 100),
('ai_model_switching', 'AI Model Switching', 'Allow users to switch between AI models', true, 100),
('real_time_collaboration', 'Real-time Collaboration', 'Enable real-time project collaboration', false, 0),
('enterprise_sso', 'Enterprise SSO', 'Enable single sign-on for enterprise users', false, 0),
('beta_features', 'Beta Features', 'Enable access to beta features', false, 10);

-- =============================================
-- VIEWS FOR COMMON QUERIES
-- =============================================

-- User dashboard view
CREATE VIEW user_dashboard_view AS
SELECT 
    u.id,
    u.email,
    u.display_name,
    u.status,
    u.role,
    u.created_at,
    u.last_login_at,
    us.status as subscription_status,
    sp.display_name as plan_name,
    uc.available_credits,
    uc.total_credits,
    uc.used_credits,
    COUNT(p.id) as project_count,
    COUNT(DISTINCT aul.id) as api_calls_today
FROM users u
LEFT JOIN user_subscriptions us ON u.id = us.user_id AND us.status = 'active'
LEFT JOIN subscription_plans sp ON us.plan_id = sp.id
LEFT JOIN user_credits uc ON u.id = uc.user_id
LEFT JOIN projects p ON u.id = p.user_id AND p.is_archived = false
LEFT JOIN api_usage_logs aul ON u.id = aul.user_id AND aul.created_at >= CURRENT_DATE
GROUP BY u.id, u.email, u.display_name, u.status, u.role, u.created_at, u.last_login_at,
         us.status, sp.display_name, uc.available_credits, uc.total_credits, uc.used_credits;

-- Usage analytics view
CREATE VIEW usage_analytics_view AS
SELECT 
    DATE(aul.created_at) as usage_date,
    COUNT(*) as total_api_calls,
    COUNT(DISTINCT aul.user_id) as unique_users,
    SUM(aul.total_tokens) as total_tokens,
    SUM(aul.cost_credits) as total_credits_used,
    SUM(aul.cost_usd) as total_cost_usd,
    AVG(aul.response_time_ms) as avg_response_time,
    COUNT(CASE WHEN aul.status_code >= 400 THEN 1 END) as error_count
FROM api_usage_logs aul
WHERE aul.created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(aul.created_at)
ORDER BY usage_date DESC;

-- Revenue analytics view
CREATE VIEW revenue_analytics_view AS
SELECT 
    DATE(pt.created_at) as transaction_date,
    COUNT(*) as transaction_count,
    SUM(CASE WHEN pt.status = 'succeeded' THEN pt.amount ELSE 0 END) as total_revenue,
    COUNT(DISTINCT pt.user_id) as unique_customers,
    AVG(CASE WHEN pt.status = 'succeeded' THEN pt.amount ELSE NULL END) as avg_transaction_value
FROM payment_transactions pt
WHERE pt.created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(pt.created_at)
ORDER BY transaction_date DESC;

