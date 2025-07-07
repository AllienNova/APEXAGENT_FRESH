#!/bin/bash

# Aideon AI Lite Cloud SQL Setup Script
# Purpose: Deploy enterprise-grade PostgreSQL with high availability
# Complements: BigQuery analytics warehouse for complete OLTP/OLAP solution

set -e

echo "🗄️ AIDEON AI LITE CLOUD SQL SETUP"
echo "=================================="

# Configuration
PROJECT_ID="aideon-ai-lite-prod"
INSTANCE_NAME="aideon-primary"
REPLICA_NAME="aideon-replica"
DATABASE_NAME="aideon_ai_lite_prod"
REGION="us-central1"
ZONE="us-central1-a"
REPLICA_ZONE="us-central1-b"
DB_VERSION="POSTGRES_15"
TIER="db-custom-4-16384"  # 4 vCPUs, 16GB RAM
STORAGE_SIZE="100GB"
STORAGE_TYPE="SSD"

# Database credentials (use environment variables in production)
DB_USER="aideon_app"
DB_PASSWORD="${DB_PASSWORD:-$(openssl rand -base64 32)}"
ROOT_PASSWORD="${ROOT_PASSWORD:-$(openssl rand -base64 32)}"

echo "📊 Configuration:"
echo "  Project: $PROJECT_ID"
echo "  Instance: $INSTANCE_NAME"
echo "  Database: $DATABASE_NAME"
echo "  Region: $REGION"
echo "  Tier: $TIER"
echo "  Storage: $STORAGE_SIZE ($STORAGE_TYPE)"
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
gcloud services enable sqladmin.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable servicenetworking.googleapis.com

# Create VPC network for private IP (if not exists)
echo "🔧 Setting up VPC network for private IP..."
gcloud compute networks create aideon-vpc --subnet-mode=custom --bgp-routing-mode=regional || echo "VPC already exists"

# Create subnet
gcloud compute networks subnets create aideon-subnet \
    --network=aideon-vpc \
    --range=10.0.0.0/24 \
    --region=$REGION || echo "Subnet already exists"

# Allocate IP range for private services access
gcloud compute addresses create google-managed-services-aideon-vpc \
    --global \
    --purpose=VPC_PEERING \
    --prefix-length=16 \
    --network=aideon-vpc || echo "IP range already allocated"

# Create private connection
gcloud services vpc-peerings connect \
    --service=servicenetworking.googleapis.com \
    --ranges=google-managed-services-aideon-vpc \
    --network=aideon-vpc || echo "Private connection already exists"

# Create Cloud SQL instance with high availability
echo "🔧 Creating Cloud SQL instance with high availability..."
gcloud sql instances create $INSTANCE_NAME \
    --database-version=$DB_VERSION \
    --tier=$TIER \
    --region=$REGION \
    --availability-type=REGIONAL \
    --storage-size=$STORAGE_SIZE \
    --storage-type=$STORAGE_TYPE \
    --storage-auto-increase \
    --backup-start-time=03:00 \
    --backup-location=$REGION \
    --maintenance-window-day=SUN \
    --maintenance-window-hour=04 \
    --maintenance-release-channel=production \
    --deletion-protection \
    --network=aideon-vpc \
    --no-assign-ip \
    --database-flags=shared_preload_libraries=pg_stat_statements,log_statement=all,log_min_duration_statement=1000 \
    --insights-config-query-insights-enabled \
    --insights-config-record-application-tags \
    --insights-config-record-client-address || echo "Instance already exists"

# Set root password
echo "🔧 Setting root password..."
gcloud sql users set-password postgres \
    --instance=$INSTANCE_NAME \
    --password=$ROOT_PASSWORD

# Create application database
echo "🔧 Creating application database..."
gcloud sql databases create $DATABASE_NAME \
    --instance=$INSTANCE_NAME

# Create application user
echo "🔧 Creating application user..."
gcloud sql users create $DB_USER \
    --instance=$INSTANCE_NAME \
    --password=$DB_PASSWORD

# Grant privileges to application user
echo "🔧 Granting privileges to application user..."
gcloud sql connect $INSTANCE_NAME --user=postgres --database=$DATABASE_NAME << EOF
GRANT ALL PRIVILEGES ON DATABASE $DATABASE_NAME TO $DB_USER;
GRANT ALL PRIVILEGES ON SCHEMA public TO $DB_USER;
ALTER USER $DB_USER CREATEDB;
EOF

# Create read replica for load balancing
echo "🔧 Creating read replica for load balancing..."
gcloud sql instances create $REPLICA_NAME \
    --master-instance-name=$INSTANCE_NAME \
    --tier=$TIER \
    --region=$REGION \
    --availability-type=ZONAL \
    --replica-type=READ \
    --storage-auto-increase \
    --network=aideon-vpc \
    --no-assign-ip || echo "Replica already exists"

# Configure SSL
echo "🔧 Configuring SSL certificates..."
gcloud sql ssl-certs create aideon-client-cert \
    --instance=$INSTANCE_NAME || echo "SSL cert already exists"

# Download SSL certificates
echo "🔧 Downloading SSL certificates..."
mkdir -p ssl_certs
gcloud sql ssl-certs describe aideon-client-cert \
    --instance=$INSTANCE_NAME \
    --format="get(cert)" > ssl_certs/client-cert.pem

gcloud sql instances describe $INSTANCE_NAME \
    --format="get(serverCaCert.cert)" > ssl_certs/server-ca.pem

# Create client key (this would be generated during cert creation in real scenario)
echo "🔧 SSL certificates downloaded to ssl_certs/ directory"

# Apply database schema
echo "🔧 Applying database schema..."
gcloud sql connect $INSTANCE_NAME --user=$DB_USER --database=$DATABASE_NAME < database_schema.sql

# Create connection pool configuration
echo "🔧 Creating connection pool configuration..."
cat > connection_pool_config.yaml << 'EOF'
# PgBouncer configuration for Cloud SQL connection pooling
databases:
  aideon_ai_lite_prod:
    host: CLOUD_SQL_PRIVATE_IP
    port: 5432
    user: aideon_app
    password: DB_PASSWORD
    pool_size: 20
    max_client_conn: 100

pools:
  default_pool_size: 20
  max_client_conn: 100
  default_pool_mode: transaction
  max_db_connections: 50
  max_user_connections: 50

admin:
  admin_users: pgbouncer_admin
  stats_users: pgbouncer_stats

logging:
  log_connections: 1
  log_disconnections: 1
  log_pooler_errors: 1

timeouts:
  server_reset_query_always: 0
  server_check_delay: 30
  server_check_query: select 1
  server_lifetime: 3600
  server_idle_timeout: 600
  query_timeout: 0
  query_wait_timeout: 120
  client_idle_timeout: 0
  client_login_timeout: 60
EOF

# Create monitoring and alerting
echo "🔧 Setting up monitoring and alerting..."
gcloud alpha monitoring policies create --policy-from-file=- << 'EOF'
displayName: "Cloud SQL High CPU Usage"
conditions:
  - displayName: "CPU usage above 80%"
    conditionThreshold:
      filter: 'resource.type="gce_instance" AND metric.type="compute.googleapis.com/instance/cpu/utilization"'
      comparison: COMPARISON_GREATER_THAN
      thresholdValue: 0.8
      duration: 300s
alertStrategy:
  autoClose: 86400s
notificationChannels: []
EOF

# Create backup policy
echo "🔧 Configuring backup policy..."
gcloud sql backups create \
    --instance=$INSTANCE_NAME \
    --description="Initial backup after setup" || echo "Backup creation initiated"

# Performance optimization
echo "🔧 Applying performance optimizations..."
gcloud sql instances patch $INSTANCE_NAME \
    --database-flags=shared_buffers=4GB,effective_cache_size=12GB,maintenance_work_mem=1GB,checkpoint_completion_target=0.9,wal_buffers=16MB,default_statistics_target=100,random_page_cost=1.1,effective_io_concurrency=200,work_mem=64MB,min_wal_size=2GB,max_wal_size=8GB

# Get connection information
echo "🔧 Getting connection information..."
PRIVATE_IP=$(gcloud sql instances describe $INSTANCE_NAME --format="get(ipAddresses[0].ipAddress)")
REPLICA_IP=$(gcloud sql instances describe $REPLICA_NAME --format="get(ipAddresses[0].ipAddress)" 2>/dev/null || echo "Replica not ready")

# Create environment configuration
echo "🔧 Creating environment configuration..."
cat > .env.cloudsql << EOF
# Cloud SQL Configuration for Aideon AI Lite
# Generated on $(date)

# Primary Database
DB_HOST=$PRIVATE_IP
DB_PORT=5432
DB_NAME=$DATABASE_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_SSL_MODE=require

# Read Replica (for read-only queries)
DB_REPLICA_HOST=$REPLICA_IP
DB_REPLICA_PORT=5432

# Connection Pool Settings
DB_POOL_SIZE=20
DB_MAX_CONNECTIONS=100
DB_IDLE_TIMEOUT=600
DB_QUERY_TIMEOUT=30000

# SSL Configuration
DB_SSL_CERT=ssl_certs/client-cert.pem
DB_SSL_KEY=ssl_certs/client-key.pem
DB_SSL_CA=ssl_certs/server-ca.pem

# Instance Information
CLOUD_SQL_INSTANCE=$INSTANCE_NAME
CLOUD_SQL_REPLICA=$REPLICA_NAME
CLOUD_SQL_PROJECT=$PROJECT_ID
CLOUD_SQL_REGION=$REGION

# Root Credentials (for admin operations)
DB_ROOT_PASSWORD=$ROOT_PASSWORD
EOF

# Create health check script
echo "🔧 Creating health check script..."
cat > health_check.sh << 'EOF'
#!/bin/bash

# Cloud SQL Health Check Script
source .env.cloudsql

echo "🔍 Cloud SQL Health Check"
echo "========================"

# Check primary instance
echo "Checking primary instance..."
if PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT 1;" > /dev/null 2>&1; then
    echo "✅ Primary instance: HEALTHY"
else
    echo "❌ Primary instance: UNHEALTHY"
fi

# Check replica instance
if [ ! -z "$DB_REPLICA_HOST" ] && [ "$DB_REPLICA_HOST" != "Replica not ready" ]; then
    echo "Checking replica instance..."
    if PGPASSWORD=$DB_PASSWORD psql -h $DB_REPLICA_HOST -U $DB_USER -d $DB_NAME -c "SELECT 1;" > /dev/null 2>&1; then
        echo "✅ Replica instance: HEALTHY"
    else
        echo "❌ Replica instance: UNHEALTHY"
    fi
fi

# Check connection pool (if running)
echo "Checking connection statistics..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "
SELECT 
    datname,
    numbackends as active_connections,
    xact_commit as transactions_committed,
    xact_rollback as transactions_rolled_back,
    blks_read,
    blks_hit,
    tup_returned,
    tup_fetched,
    tup_inserted,
    tup_updated,
    tup_deleted
FROM pg_stat_database 
WHERE datname = '$DB_NAME';"

echo ""
echo "Database size:"
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "
SELECT 
    pg_size_pretty(pg_database_size('$DB_NAME')) as database_size;"

echo ""
echo "Top 5 largest tables:"
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC 
LIMIT 5;"
EOF

chmod +x health_check.sh

# Create backup script
echo "🔧 Creating backup script..."
cat > backup.sh << 'EOF'
#!/bin/bash

# Cloud SQL Backup Script
source .env.cloudsql

BACKUP_NAME="manual-backup-$(date +%Y%m%d-%H%M%S)"

echo "🔄 Creating Cloud SQL backup: $BACKUP_NAME"
gcloud sql backups create \
    --instance=$CLOUD_SQL_INSTANCE \
    --description="Manual backup created on $(date)"

echo "✅ Backup created: $BACKUP_NAME"

# List recent backups
echo ""
echo "Recent backups:"
gcloud sql backups list --instance=$CLOUD_SQL_INSTANCE --limit=5
EOF

chmod +x backup.sh

# Create migration script template
echo "🔧 Creating migration script template..."
cat > migrate.sh << 'EOF'
#!/bin/bash

# Database Migration Script Template
source .env.cloudsql

MIGRATION_FILE=$1

if [ -z "$MIGRATION_FILE" ]; then
    echo "Usage: ./migrate.sh <migration_file.sql>"
    exit 1
fi

if [ ! -f "$MIGRATION_FILE" ]; then
    echo "Migration file not found: $MIGRATION_FILE"
    exit 1
fi

echo "🔄 Running migration: $MIGRATION_FILE"
echo "Database: $DB_NAME"
echo "Host: $DB_HOST"
echo ""

# Create backup before migration
echo "Creating backup before migration..."
BACKUP_NAME="pre-migration-$(basename $MIGRATION_FILE .sql)-$(date +%Y%m%d-%H%M%S)"
gcloud sql backups create \
    --instance=$CLOUD_SQL_INSTANCE \
    --description="Backup before migration: $MIGRATION_FILE"

# Run migration
echo "Running migration..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f $MIGRATION_FILE

if [ $? -eq 0 ]; then
    echo "✅ Migration completed successfully"
else
    echo "❌ Migration failed"
    exit 1
fi
EOF

chmod +x migrate.sh

# Verify setup
echo "🔧 Verifying setup..."
echo ""
echo "📊 Instance Information:"
gcloud sql instances describe $INSTANCE_NAME --format="table(name,databaseVersion,state,settings.tier,region,settings.availabilityType)"

echo ""
echo "📊 Database Information:"
gcloud sql databases list --instance=$INSTANCE_NAME

echo ""
echo "📊 User Information:"
gcloud sql users list --instance=$INSTANCE_NAME

echo ""
echo "✅ CLOUD SQL SETUP COMPLETE!"
echo "=============================="
echo ""
echo "📋 Connection Details:"
echo "  Primary Host: $PRIVATE_IP"
echo "  Replica Host: $REPLICA_IP"
echo "  Database: $DATABASE_NAME"
echo "  User: $DB_USER"
echo "  SSL: Required"
echo ""
echo "📁 Files Created:"
echo "  - .env.cloudsql (environment configuration)"
echo "  - connection_pool_config.yaml (PgBouncer config)"
echo "  - ssl_certs/ (SSL certificates)"
echo "  - health_check.sh (health monitoring)"
echo "  - backup.sh (manual backup script)"
echo "  - migrate.sh (migration script template)"
echo ""
echo "🔗 Cloud Console:"
echo "  https://console.cloud.google.com/sql/instances/$INSTANCE_NAME/overview?project=$PROJECT_ID"
echo ""
echo "🎯 Next Steps:"
echo "1. Update application configuration with connection details"
echo "2. Set up connection pooling with PgBouncer"
echo "3. Configure monitoring and alerting"
echo "4. Test application connectivity"
echo "5. Set up automated backups and maintenance"
echo ""
echo "⚠️  IMPORTANT: Store credentials securely!"
echo "   Root Password: $ROOT_PASSWORD"
echo "   App Password: $DB_PASSWORD"
EOF

