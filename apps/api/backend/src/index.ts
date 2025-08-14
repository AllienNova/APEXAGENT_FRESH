/**
 * ApexAgent Backend Server
 * 
 * Main entry point for the ApexAgent AI system backend API.
 * Provides comprehensive AI model integration, authentication, and real-time capabilities.
 */

import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import morgan from 'morgan';
import rateLimit from 'express-rate-limit';
import { createServer } from 'http';
import { Server as SocketIOServer } from 'socket.io';
import dotenv from 'dotenv';
import winston from 'winston';

// Import routes
import authRoutes from './routes/auth';
import chatRoutes from './routes/chat';
import modelsRoutes from './routes/models';
import projectsRoutes from './routes/projects';
import filesRoutes from './routes/files';
import agentsRoutes from './routes/agents';
import analyticsRoutes from './routes/analytics';
import healthRoutes from './routes/health';

// Import middleware
import { errorHandler } from './middleware/errorHandler';
import { authMiddleware } from './middleware/auth';
import { requestLogger } from './middleware/requestLogger';
import { validateRequest } from './middleware/validation';

// Import services
import { FirebaseService } from './services/firebase';
import { RedisService } from './services/redis';
import { AIModelService } from './services/aiModels';
import { WebSocketService } from './services/websocket';
import { AnalyticsService } from './services/analytics';
import { SecurityService } from './services/security';

// Import utilities
import { logger } from './utils/logger';
import { config } from './utils/config';

// Load environment variables
dotenv.config();

class ApexAgentServer {
  private app: express.Application;
  private server: any;
  private io: SocketIOServer;
  private port: number;

  // Services
  private firebaseService: FirebaseService;
  private redisService: RedisService;
  private aiModelService: AIModelService;
  private websocketService: WebSocketService;
  private analyticsService: AnalyticsService;
  private securityService: SecurityService;

  constructor() {
    this.app = express();
    this.port = parseInt(process.env.PORT || '3001', 10);
    
    // Initialize services
    this.initializeServices();
    
    // Setup server
    this.setupMiddleware();
    this.setupRoutes();
    this.setupWebSocket();
    this.setupErrorHandling();
  }

  private async initializeServices(): Promise<void> {
    try {
      logger.info('Initializing services...');

      // Initialize Firebase
      this.firebaseService = new FirebaseService();
      await this.firebaseService.initialize();

      // Initialize Redis
      this.redisService = new RedisService();
      await this.redisService.connect();

      // Initialize AI Model Service
      this.aiModelService = new AIModelService();
      await this.aiModelService.initialize();

      // Initialize Analytics
      this.analyticsService = new AnalyticsService();
      await this.analyticsService.initialize();

      // Initialize Security Service
      this.securityService = new SecurityService();
      await this.securityService.initialize();

      logger.info('All services initialized successfully');
    } catch (error) {
      logger.error('Failed to initialize services:', error);
      process.exit(1);
    }
  }

  private setupMiddleware(): void {
    // Security middleware
    this.app.use(helmet({
      contentSecurityPolicy: {
        directives: {
          defaultSrc: ["'self'"],
          styleSrc: ["'self'", "'unsafe-inline'"],
          scriptSrc: ["'self'"],
          imgSrc: ["'self'", "data:", "https:"],
          connectSrc: ["'self'", "wss:", "https:"],
        },
      },
      crossOriginEmbedderPolicy: false,
    }));

    // CORS configuration
    this.app.use(cors({
      origin: process.env.NODE_ENV === 'production' 
        ? [
            'https://apexagent.ai',
            'https://app.apexagent.ai',
            'https://admin.apexagent.ai'
          ]
        : true, // Allow all origins in development
      credentials: true,
      methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
      allowedHeaders: [
        'Origin',
        'X-Requested-With',
        'Content-Type',
        'Accept',
        'Authorization',
        'X-API-Key',
        'X-Request-ID'
      ],
    }));

    // Rate limiting
    const limiter = rateLimit({
      windowMs: 15 * 60 * 1000, // 15 minutes
      max: process.env.NODE_ENV === 'production' ? 100 : 1000, // requests per window
      message: {
        error: 'Too many requests from this IP, please try again later.',
        retryAfter: '15 minutes'
      },
      standardHeaders: true,
      legacyHeaders: false,
    });
    this.app.use(limiter);

    // Body parsing middleware
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));

    // Compression
    this.app.use(compression());

    // Request logging
    this.app.use(morgan('combined', {
      stream: { write: (message) => logger.info(message.trim()) }
    }));

    // Custom request logger
    this.app.use(requestLogger);

    // Trust proxy for accurate IP addresses
    this.app.set('trust proxy', 1);
  }

  private setupRoutes(): void {
    // Health check (no auth required)
    this.app.use('/api/health', healthRoutes);

    // Public routes
    this.app.use('/api/auth', authRoutes);

    // Protected routes (require authentication)
    this.app.use('/api/chat', authMiddleware, chatRoutes);
    this.app.use('/api/models', authMiddleware, modelsRoutes);
    this.app.use('/api/projects', authMiddleware, projectsRoutes);
    this.app.use('/api/files', authMiddleware, filesRoutes);
    this.app.use('/api/agents', authMiddleware, agentsRoutes);
    this.app.use('/api/analytics', authMiddleware, analyticsRoutes);

    // API documentation
    this.app.get('/api', (req, res) => {
      res.json({
        name: 'ApexAgent API',
        version: '1.0.0',
        description: 'Advanced AI System API',
        documentation: 'https://docs.apexagent.ai/api',
        endpoints: {
          auth: '/api/auth',
          chat: '/api/chat',
          models: '/api/models',
          projects: '/api/projects',
          files: '/api/files',
          agents: '/api/agents',
          analytics: '/api/analytics',
          health: '/api/health'
        }
      });
    });

    // 404 handler
    this.app.use('*', (req, res) => {
      res.status(404).json({
        error: 'Endpoint not found',
        message: `The requested endpoint ${req.originalUrl} does not exist`,
        availableEndpoints: [
          '/api/auth',
          '/api/chat',
          '/api/models',
          '/api/projects',
          '/api/files',
          '/api/agents',
          '/api/analytics',
          '/api/health'
        ]
      });
    });
  }

  private setupWebSocket(): void {
    this.server = createServer(this.app);
    
    this.io = new SocketIOServer(this.server, {
      cors: {
        origin: process.env.NODE_ENV === 'production' 
          ? [
              'https://apexagent.ai',
              'https://app.apexagent.ai',
              'https://admin.apexagent.ai'
            ]
          : true,
        credentials: true,
      },
      transports: ['websocket', 'polling'],
    });

    // Initialize WebSocket service
    this.websocketService = new WebSocketService(this.io);
    this.websocketService.initialize();

    logger.info('WebSocket server initialized');
  }

  private setupErrorHandling(): void {
    // Global error handler
    this.app.use(errorHandler);

    // Unhandled promise rejections
    process.on('unhandledRejection', (reason, promise) => {
      logger.error('Unhandled Rejection at:', promise, 'reason:', reason);
      // Don't exit the process in production
      if (process.env.NODE_ENV !== 'production') {
        process.exit(1);
      }
    });

    // Uncaught exceptions
    process.on('uncaughtException', (error) => {
      logger.error('Uncaught Exception:', error);
      // Graceful shutdown
      this.gracefulShutdown();
    });

    // Graceful shutdown on SIGTERM
    process.on('SIGTERM', () => {
      logger.info('SIGTERM received, shutting down gracefully');
      this.gracefulShutdown();
    });

    // Graceful shutdown on SIGINT
    process.on('SIGINT', () => {
      logger.info('SIGINT received, shutting down gracefully');
      this.gracefulShutdown();
    });
  }

  private async gracefulShutdown(): Promise<void> {
    logger.info('Starting graceful shutdown...');

    try {
      // Close server
      if (this.server) {
        await new Promise<void>((resolve) => {
          this.server.close(() => {
            logger.info('HTTP server closed');
            resolve();
          });
        });
      }

      // Close WebSocket server
      if (this.io) {
        this.io.close();
        logger.info('WebSocket server closed');
      }

      // Close Redis connection
      if (this.redisService) {
        await this.redisService.disconnect();
        logger.info('Redis connection closed');
      }

      // Close other services
      if (this.analyticsService) {
        await this.analyticsService.shutdown();
        logger.info('Analytics service shutdown');
      }

      logger.info('Graceful shutdown completed');
      process.exit(0);
    } catch (error) {
      logger.error('Error during graceful shutdown:', error);
      process.exit(1);
    }
  }

  public async start(): Promise<void> {
    try {
      // Start the server
      this.server.listen(this.port, '0.0.0.0', () => {
        logger.info(`🚀 ApexAgent Server running on port ${this.port}`);
        logger.info(`📚 API Documentation: http://localhost:${this.port}/api`);
        logger.info(`🔗 WebSocket Server: ws://localhost:${this.port}`);
        logger.info(`🌍 Environment: ${process.env.NODE_ENV || 'development'}`);
        
        // Log available AI models
        this.logAvailableModels();
      });

      // Health check endpoint
      this.app.get('/health', (req, res) => {
        res.json({
          status: 'healthy',
          timestamp: new Date().toISOString(),
          uptime: process.uptime(),
          version: '1.0.0',
          environment: process.env.NODE_ENV || 'development',
          services: {
            firebase: this.firebaseService.isConnected(),
            redis: this.redisService.isConnected(),
            aiModels: this.aiModelService.getStatus(),
          }
        });
      });

    } catch (error) {
      logger.error('Failed to start server:', error);
      process.exit(1);
    }
  }

  private async logAvailableModels(): Promise<void> {
    try {
      const models = await this.aiModelService.getAvailableModels();
      logger.info(`🤖 Available AI Models: ${models.length}`);
      
      const modelsByProvider = models.reduce((acc, model) => {
        if (!acc[model.provider]) acc[model.provider] = 0;
        acc[model.provider]++;
        return acc;
      }, {} as Record<string, number>);

      Object.entries(modelsByProvider).forEach(([provider, count]) => {
        logger.info(`   ${provider}: ${count} models`);
      });
    } catch (error) {
      logger.warn('Could not load AI models:', error);
    }
  }

  // Getter methods for services (for testing)
  public getApp(): express.Application {
    return this.app;
  }

  public getServer(): any {
    return this.server;
  }

  public getIO(): SocketIOServer {
    return this.io;
  }
}

// Create and start the server
const server = new ApexAgentServer();

// Start the server if this file is run directly
if (require.main === module) {
  server.start().catch((error) => {
    logger.error('Failed to start ApexAgent server:', error);
    process.exit(1);
  });
}

export default server;
export { ApexAgentServer };

