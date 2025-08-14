const { Pool } = require('pg');
const { CloudSQLConnector } = require('@google-cloud/cloud-sql-connector');

/**
 * Aideon AI Lite Cloud SQL Connection Service
 * Purpose: Enterprise-grade PostgreSQL connection management
 * Features: Connection pooling, read replicas, SSL, monitoring
 */

class CloudSQLService {
  constructor() {
    this.primaryPool = null;
    this.replicaPool = null;
    this.connector = null;
    this.config = this.loadConfig();
    this.isInitialized = false;
  }

  /**
   * Load configuration from environment variables
   */
  loadConfig() {
    return {
      // Primary database configuration
      primary: {
        host: process.env.DB_HOST,
        port: parseInt(process.env.DB_PORT) || 5432,
        database: process.env.DB_NAME,
        user: process.env.DB_USER,
        password: process.env.DB_PASSWORD,
        ssl: {
          require: true,
          rejectUnauthorized: true,
          cert: process.env.DB_SSL_CERT ? require('fs').readFileSync(process.env.DB_SSL_CERT) : undefined,
          key: process.env.DB_SSL_KEY ? require('fs').readFileSync(process.env.DB_SSL_KEY) : undefined,
          ca: process.env.DB_SSL_CA ? require('fs').readFileSync(process.env.DB_SSL_CA) : undefined
        }
      },
      
      // Read replica configuration
      replica: {
        host: process.env.DB_REPLICA_HOST,
        port: parseInt(process.env.DB_REPLICA_PORT) || 5432,
        database: process.env.DB_NAME,
        user: process.env.DB_USER,
        password: process.env.DB_PASSWORD,
        ssl: {
          require: true,
          rejectUnauthorized: true,
          cert: process.env.DB_SSL_CERT ? require('fs').readFileSync(process.env.DB_SSL_CERT) : undefined,
          key: process.env.DB_SSL_KEY ? require('fs').readFileSync(process.env.DB_SSL_KEY) : undefined,
          ca: process.env.DB_SSL_CA ? require('fs').readFileSync(process.env.DB_SSL_CA) : undefined
        }
      },

      // Connection pool settings
      pool: {
        max: parseInt(process.env.DB_MAX_CONNECTIONS) || 20,
        min: 2,
        idleTimeoutMillis: parseInt(process.env.DB_IDLE_TIMEOUT) * 1000 || 600000,
        connectionTimeoutMillis: 30000,
        query_timeout: parseInt(process.env.DB_QUERY_TIMEOUT) || 30000,
        statement_timeout: 30000,
        application_name: 'aideon_ai_lite'
      },

      // Cloud SQL specific
      cloudSQL: {
        instanceConnectionName: `${process.env.CLOUD_SQL_PROJECT}:${process.env.CLOUD_SQL_REGION}:${process.env.CLOUD_SQL_INSTANCE}`,
        replicaConnectionName: process.env.CLOUD_SQL_REPLICA ? 
          `${process.env.CLOUD_SQL_PROJECT}:${process.env.CLOUD_SQL_REGION}:${process.env.CLOUD_SQL_REPLICA}` : null
      }
    };
  }

  /**
   * Initialize connection pools
   */
  async initialize() {
    try {
      console.log('🔄 Initializing Cloud SQL connection pools...');

      // Initialize Cloud SQL Connector for IAM authentication (optional)
      if (process.env.USE_IAM_AUTH === 'true') {
        this.connector = new CloudSQLConnector();
      }

      // Create primary connection pool
      this.primaryPool = new Pool({
        ...this.config.primary,
        ...this.config.pool,
        max: this.config.pool.max,
        min: this.config.pool.min,
        idleTimeoutMillis: this.config.pool.idleTimeoutMillis,
        connectionTimeoutMillis: this.config.pool.connectionTimeoutMillis
      });

      // Set up primary pool event handlers
      this.primaryPool.on('connect', (client) => {
        console.log('✅ Primary pool: New client connected');
        // Set session parameters
        client.query('SET application_name = $1', [this.config.pool.application_name]);
        client.query('SET statement_timeout = $1', [this.config.pool.statement_timeout]);
      });

      this.primaryPool.on('error', (err, client) => {
        console.error('❌ Primary pool error:', err);
        this.handlePoolError(err, 'primary');
      });

      this.primaryPool.on('remove', (client) => {
        console.log('🔄 Primary pool: Client removed');
      });

      // Create replica connection pool if configured
      if (this.config.replica.host && this.config.replica.host !== 'Replica not ready') {
        this.replicaPool = new Pool({
          ...this.config.replica,
          ...this.config.pool,
          max: Math.floor(this.config.pool.max / 2), // Use fewer connections for replica
          min: 1
        });

        this.replicaPool.on('connect', (client) => {
          console.log('✅ Replica pool: New client connected');
          client.query('SET application_name = $1', [`${this.config.pool.application_name}_replica`]);
          client.query('SET statement_timeout = $1', [this.config.pool.statement_timeout]);
          client.query('SET default_transaction_read_only = true'); // Ensure read-only
        });

        this.replicaPool.on('error', (err, client) => {
          console.error('❌ Replica pool error:', err);
          this.handlePoolError(err, 'replica');
        });
      }

      // Test connections
      await this.testConnections();

      this.isInitialized = true;
      console.log('✅ Cloud SQL connection pools initialized successfully');

      // Start health monitoring
      this.startHealthMonitoring();

    } catch (error) {
      console.error('❌ Failed to initialize Cloud SQL connection pools:', error);
      throw error;
    }
  }

  /**
   * Test database connections
   */
  async testConnections() {
    try {
      // Test primary connection
      const primaryClient = await this.primaryPool.connect();
      const primaryResult = await primaryClient.query('SELECT NOW() as timestamp, version() as version');
      primaryClient.release();
      console.log('✅ Primary database connection test successful:', primaryResult.rows[0]);

      // Test replica connection if available
      if (this.replicaPool) {
        const replicaClient = await this.replicaPool.connect();
        const replicaResult = await replicaClient.query('SELECT NOW() as timestamp, pg_is_in_recovery() as is_replica');
        replicaClient.release();
        console.log('✅ Replica database connection test successful:', replicaResult.rows[0]);
      }
    } catch (error) {
      console.error('❌ Database connection test failed:', error);
      throw error;
    }
  }

  /**
   * Execute query on primary database (for writes and critical reads)
   */
  async query(text, params = []) {
    if (!this.isInitialized) {
      throw new Error('CloudSQLService not initialized. Call initialize() first.');
    }

    const start = Date.now();
    try {
      const result = await this.primaryPool.query(text, params);
      const duration = Date.now() - start;
      
      // Log slow queries
      if (duration > 1000) {
        console.warn(`🐌 Slow query detected (${duration}ms):`, text.substring(0, 100));
      }

      return result;
    } catch (error) {
      console.error('❌ Primary database query error:', error);
      console.error('Query:', text);
      console.error('Params:', params);
      throw error;
    }
  }

  /**
   * Execute read-only query (uses replica if available, falls back to primary)
   */
  async queryRead(text, params = []) {
    if (!this.isInitialized) {
      throw new Error('CloudSQLService not initialized. Call initialize() first.');
    }

    const start = Date.now();
    const pool = this.replicaPool || this.primaryPool;
    const poolType = this.replicaPool ? 'replica' : 'primary';

    try {
      const result = await pool.query(text, params);
      const duration = Date.now() - start;
      
      // Log slow queries
      if (duration > 1000) {
        console.warn(`🐌 Slow read query detected on ${poolType} (${duration}ms):`, text.substring(0, 100));
      }

      return result;
    } catch (error) {
      // If replica fails, try primary
      if (this.replicaPool && poolType === 'replica') {
        console.warn('⚠️ Replica query failed, falling back to primary:', error.message);
        return this.query(text, params);
      }
      
      console.error(`❌ ${poolType} database read query error:`, error);
      console.error('Query:', text);
      console.error('Params:', params);
      throw error;
    }
  }

  /**
   * Execute transaction
   */
  async transaction(callback) {
    if (!this.isInitialized) {
      throw new Error('CloudSQLService not initialized. Call initialize() first.');
    }

    const client = await this.primaryPool.connect();
    
    try {
      await client.query('BEGIN');
      const result = await callback(client);
      await client.query('COMMIT');
      return result;
    } catch (error) {
      await client.query('ROLLBACK');
      console.error('❌ Transaction error:', error);
      throw error;
    } finally {
      client.release();
    }
  }

  /**
   * Get connection pool statistics
   */
  getPoolStats() {
    const stats = {
      primary: {
        totalCount: this.primaryPool?.totalCount || 0,
        idleCount: this.primaryPool?.idleCount || 0,
        waitingCount: this.primaryPool?.waitingCount || 0
      }
    };

    if (this.replicaPool) {
      stats.replica = {
        totalCount: this.replicaPool.totalCount,
        idleCount: this.replicaPool.idleCount,
        waitingCount: this.replicaPool.waitingCount
      };
    }

    return stats;
  }

  /**
   * Health check
   */
  async healthCheck() {
    try {
      const checks = {
        primary: { status: 'unknown', latency: null, error: null },
        replica: { status: 'unknown', latency: null, error: null }
      };

      // Check primary
      try {
        const start = Date.now();
        await this.query('SELECT 1');
        checks.primary.status = 'healthy';
        checks.primary.latency = Date.now() - start;
      } catch (error) {
        checks.primary.status = 'unhealthy';
        checks.primary.error = error.message;
      }

      // Check replica if available
      if (this.replicaPool) {
        try {
          const start = Date.now();
          await this.queryRead('SELECT 1');
          checks.replica.status = 'healthy';
          checks.replica.latency = Date.now() - start;
        } catch (error) {
          checks.replica.status = 'unhealthy';
          checks.replica.error = error.message;
        }
      } else {
        checks.replica.status = 'not_configured';
      }

      return {
        overall: checks.primary.status === 'healthy' ? 'healthy' : 'unhealthy',
        checks,
        poolStats: this.getPoolStats(),
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      return {
        overall: 'unhealthy',
        error: error.message,
        timestamp: new Date().toISOString()
      };
    }
  }

  /**
   * Handle pool errors
   */
  handlePoolError(error, poolType) {
    console.error(`❌ ${poolType} pool error:`, error);
    
    // Implement error handling logic
    if (error.code === 'ECONNREFUSED') {
      console.error('🔌 Database connection refused - check if database is running');
    } else if (error.code === 'ENOTFOUND') {
      console.error('🔍 Database host not found - check connection configuration');
    } else if (error.code === '28P01') {
      console.error('🔐 Authentication failed - check credentials');
    } else if (error.code === '3D000') {
      console.error('📁 Database does not exist');
    }

    // Could implement alerting here
    this.sendAlert(`${poolType} database pool error: ${error.message}`);
  }

  /**
   * Send alert (placeholder for actual alerting system)
   */
  sendAlert(message) {
    console.error('🚨 ALERT:', message);
    // Implement actual alerting (email, Slack, PagerDuty, etc.)
  }

  /**
   * Start health monitoring
   */
  startHealthMonitoring() {
    // Health check every 30 seconds
    setInterval(async () => {
      try {
        const health = await this.healthCheck();
        if (health.overall !== 'healthy') {
          console.warn('⚠️ Database health check failed:', health);
        }
      } catch (error) {
        console.error('❌ Health check error:', error);
      }
    }, 30000);

    // Pool stats logging every 5 minutes
    setInterval(() => {
      const stats = this.getPoolStats();
      console.log('📊 Connection pool stats:', stats);
    }, 300000);
  }

  /**
   * Graceful shutdown
   */
  async shutdown() {
    console.log('🔄 Shutting down Cloud SQL connection pools...');
    
    try {
      if (this.primaryPool) {
        await this.primaryPool.end();
        console.log('✅ Primary pool closed');
      }
      
      if (this.replicaPool) {
        await this.replicaPool.end();
        console.log('✅ Replica pool closed');
      }
      
      if (this.connector) {
        await this.connector.close();
        console.log('✅ Cloud SQL Connector closed');
      }
      
      console.log('✅ Cloud SQL service shutdown complete');
    } catch (error) {
      console.error('❌ Error during shutdown:', error);
    }
  }

  /**
   * Database migration helper
   */
  async runMigration(migrationSQL) {
    return this.transaction(async (client) => {
      console.log('🔄 Running database migration...');
      
      // Create migrations table if it doesn't exist
      await client.query(`
        CREATE TABLE IF NOT EXISTS migrations (
          id SERIAL PRIMARY KEY,
          name VARCHAR(255) UNIQUE NOT NULL,
          executed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
      `);
      
      // Execute migration
      const result = await client.query(migrationSQL);
      
      console.log('✅ Migration completed successfully');
      return result;
    });
  }

  /**
   * Bulk insert helper with conflict resolution
   */
  async bulkInsert(tableName, data, conflictColumns = [], updateColumns = []) {
    if (!data || data.length === 0) {
      return { rowCount: 0 };
    }

    const columns = Object.keys(data[0]);
    const values = data.map(row => columns.map(col => row[col]));
    
    // Build parameterized query
    const placeholders = values.map((_, rowIndex) => 
      `(${columns.map((_, colIndex) => `$${rowIndex * columns.length + colIndex + 1}`).join(', ')})`
    ).join(', ');
    
    let query = `INSERT INTO ${tableName} (${columns.join(', ')}) VALUES ${placeholders}`;
    
    // Add conflict resolution if specified
    if (conflictColumns.length > 0) {
      query += ` ON CONFLICT (${conflictColumns.join(', ')})`;
      
      if (updateColumns.length > 0) {
        const updates = updateColumns.map(col => `${col} = EXCLUDED.${col}`).join(', ');
        query += ` DO UPDATE SET ${updates}`;
      } else {
        query += ' DO NOTHING';
      }
    }
    
    const flatValues = values.flat();
    return this.query(query, flatValues);
  }
}

// Export singleton instance
const cloudSQLService = new CloudSQLService();

module.exports = cloudSQLService;

