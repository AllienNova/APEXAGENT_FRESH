#!/bin/bash
# ApexAgent Development Environment Setup Script
# This script sets up the local development environment for ApexAgent

set -e

# Print colored output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
  echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

check_dependency() {
  if ! command -v $1 &> /dev/null; then
    log_error "$1 is required but not installed. Please install it first."
    exit 1
  else
    log_info "$1 is installed."
  fi
}

# Check for required dependencies
log_info "Checking dependencies..."
check_dependency "docker"
check_dependency "docker-compose"
check_dependency "git"
check_dependency "node"
check_dependency "npm"

# Clone repository if not already in project directory
if [ ! -f "package.json" ]; then
  log_info "Cloning ApexAgent repository..."
  git clone https://github.com/AllienNova/ApexAgent.git
  cd ApexAgent
else
  log_info "Already in project directory."
fi

# Copy development configuration files
log_info "Setting up development configuration..."
mkdir -p config
cp -n src/devex/local_env/docker-compose.yml ./docker-compose.yml || log_warn "docker-compose.yml already exists, skipping."
cp -n src/devex/local_env/Dockerfile.dev ./Dockerfile.dev || log_warn "Dockerfile.dev already exists, skipping."

# Create feature flags file if it doesn't exist
if [ ! -f "config/feature_flags.json" ]; then
  log_info "Creating feature flags configuration..."
  mkdir -p config
  cat > config/feature_flags.json << EOF
{
  "enableNewUI": true,
  "enablePluginSystem": true,
  "enablePerformanceMetrics": true,
  "enableDebugMode": true
}
EOF
fi

# Create Prometheus configuration if it doesn't exist
if [ ! -f "config/prometheus.yml" ]; then
  log_info "Creating Prometheus configuration..."
  mkdir -p config
  cat > config/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'apexagent'
    static_configs:
      - targets: ['app:3000']
EOF
fi

# Create Grafana provisioning directories
log_info "Setting up Grafana provisioning..."
mkdir -p config/grafana/provisioning/{datasources,dashboards}

# Create Grafana datasource configuration
cat > config/grafana/provisioning/datasources/datasource.yml << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

# Create Grafana dashboard configuration
cat > config/grafana/provisioning/dashboards/dashboard.yml << EOF
apiVersion: 1

providers:
  - name: 'ApexAgent'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    options:
      path: /var/lib/grafana/dashboards
EOF

# Create database initialization script
log_info "Creating database initialization script..."
mkdir -p scripts
cat > scripts/init-db.sql << EOF
-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create schema
CREATE SCHEMA IF NOT EXISTS apexagent;

-- Create users table
CREATE TABLE IF NOT EXISTS apexagent.users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  username VARCHAR(255) NOT NULL UNIQUE,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  first_name VARCHAR(255),
  last_name VARCHAR(255),
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create resources table
CREATE TABLE IF NOT EXISTS apexagent.resources (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL,
  description TEXT,
  type VARCHAR(50) NOT NULL,
  created_by UUID REFERENCES apexagent.users(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create test user
INSERT INTO apexagent.users (username, email, password_hash, first_name, last_name)
VALUES ('testuser', 'test@example.com', '\$2b\$10\$EpRnTzVlqHNP0.fUbXUwSOyuiXe/QLSUG6xNekdHgTGmrpHEfIoxm', 'Test', 'User')
ON CONFLICT (username) DO NOTHING;
EOF

# Install dependencies
log_info "Installing dependencies..."
npm install

# Start development environment
log_info "Starting development environment..."
docker-compose up -d

# Wait for services to be ready
log_info "Waiting for services to be ready..."
sleep 10

# Display access information
log_info "Development environment is ready!"
echo -e "\n${GREEN}Access your services:${NC}"
echo -e "- ApexAgent App: http://localhost:3000"
echo -e "- Adminer (DB): http://localhost:8080"
echo -e "- MailHog (Email): http://localhost:8025"
echo -e "- Jaeger (Tracing): http://localhost:16686"
echo -e "- Prometheus (Metrics): http://localhost:9090"
echo -e "- Grafana (Dashboards): http://localhost:3001 (admin/admin)"
echo -e "- MinIO (S3): http://localhost:9001 (apexagent/development)"

echo -e "\n${GREEN}Development commands:${NC}"
echo -e "- Start environment: docker-compose up -d"
echo -e "- Stop environment: docker-compose down"
echo -e "- View logs: docker-compose logs -f [service]"
echo -e "- Restart service: docker-compose restart [service]"
echo -e "- Run tests: npm test"
echo -e "- Lint code: npm run lint"

echo -e "\n${YELLOW}Happy coding!${NC}"
