/**
 * Authentication Routes
 * 
 * Handles user authentication, registration, and session management
 */

import { Router, Request, Response } from 'express';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import rateLimit from 'express-rate-limit';
import { body, validationResult } from 'express-validator';
import { logger } from '../utils/logger';
import { FirebaseService } from '../services/firebase';
import { RedisService } from '../services/redis';
import { SecurityService } from '../services/security';

const router = Router();

// Rate limiting for auth endpoints
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // 5 attempts per window
  message: {
    error: 'Too many authentication attempts, please try again later.',
    retryAfter: '15 minutes'
  },
  standardHeaders: true,
  legacyHeaders: false,
});

// Services
const firebaseService = new FirebaseService();
const redisService = new RedisService();
const securityService = new SecurityService();

// Validation middleware
const validateRegistration = [
  body('email').isEmail().normalizeEmail(),
  body('password').isLength({ min: 8 }).matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/),
  body('firstName').trim().isLength({ min: 1, max: 50 }),
  body('lastName').trim().isLength({ min: 1, max: 50 }),
];

const validateLogin = [
  body('email').isEmail().normalizeEmail(),
  body('password').isLength({ min: 1 }),
];

/**
 * POST /api/auth/register
 * Register a new user
 */
router.post('/register', authLimiter, validateRegistration, async (req: Request, res: Response) => {
  try {
    // Check validation errors
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Validation failed',
        details: errors.array()
      });
    }

    const { email, password, firstName, lastName } = req.body;

    // Check if user already exists
    const existingUser = await firebaseService.getUserByEmail(email);
    if (existingUser) {
      return res.status(409).json({
        error: 'User already exists',
        message: 'An account with this email address already exists'
      });
    }

    // Hash password
    const saltRounds = 12;
    const hashedPassword = await bcrypt.hash(password, saltRounds);

    // Create user in Firebase
    const userData = {
      email,
      password: hashedPassword,
      firstName,
      lastName,
      createdAt: new Date().toISOString(),
      isActive: true,
      role: 'user',
      subscription: {
        tier: 'basic',
        credits: 2000,
        apiKeysProvided: false
      }
    };

    const user = await firebaseService.createUser(userData);

    // Generate JWT token
    const token = jwt.sign(
      { 
        userId: user.uid,
        email: user.email,
        role: userData.role
      },
      process.env.JWT_SECRET!,
      { expiresIn: '7d' }
    );

    // Store session in Redis
    await redisService.setSession(user.uid, {
      userId: user.uid,
      email: user.email,
      role: userData.role,
      loginTime: new Date().toISOString()
    });

    // Log security event
    await securityService.logEvent({
      type: 'user_registration',
      userId: user.uid,
      email: user.email,
      ip: req.ip,
      userAgent: req.get('User-Agent')
    });

    logger.info(`New user registered: ${email}`);

    res.status(201).json({
      message: 'User registered successfully',
      user: {
        id: user.uid,
        email: user.email,
        firstName: userData.firstName,
        lastName: userData.lastName,
        role: userData.role,
        subscription: userData.subscription
      },
      token
    });

  } catch (error) {
    logger.error('Registration error:', error);
    res.status(500).json({
      error: 'Registration failed',
      message: 'An internal error occurred during registration'
    });
  }
});

/**
 * POST /api/auth/login
 * Authenticate user and return JWT token
 */
router.post('/login', authLimiter, validateLogin, async (req: Request, res: Response) => {
  try {
    // Check validation errors
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Validation failed',
        details: errors.array()
      });
    }

    const { email, password } = req.body;

    // Get user from Firebase
    const user = await firebaseService.getUserByEmail(email);
    if (!user) {
      return res.status(401).json({
        error: 'Authentication failed',
        message: 'Invalid email or password'
      });
    }

    // Check if user is active
    if (!user.isActive) {
      return res.status(401).json({
        error: 'Account disabled',
        message: 'Your account has been disabled. Please contact support.'
      });
    }

    // Verify password
    const isValidPassword = await bcrypt.compare(password, user.password);
    if (!isValidPassword) {
      // Log failed login attempt
      await securityService.logEvent({
        type: 'failed_login',
        userId: user.id,
        email: user.email,
        ip: req.ip,
        userAgent: req.get('User-Agent')
      });

      return res.status(401).json({
        error: 'Authentication failed',
        message: 'Invalid email or password'
      });
    }

    // Generate JWT token
    const token = jwt.sign(
      { 
        userId: user.id,
        email: user.email,
        role: user.role
      },
      process.env.JWT_SECRET!,
      { expiresIn: '7d' }
    );

    // Store session in Redis
    await redisService.setSession(user.id, {
      userId: user.id,
      email: user.email,
      role: user.role,
      loginTime: new Date().toISOString()
    });

    // Log successful login
    await securityService.logEvent({
      type: 'successful_login',
      userId: user.id,
      email: user.email,
      ip: req.ip,
      userAgent: req.get('User-Agent')
    });

    logger.info(`User logged in: ${email}`);

    res.json({
      message: 'Login successful',
      user: {
        id: user.id,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
        role: user.role,
        subscription: user.subscription
      },
      token
    });

  } catch (error) {
    logger.error('Login error:', error);
    res.status(500).json({
      error: 'Login failed',
      message: 'An internal error occurred during login'
    });
  }
});

/**
 * POST /api/auth/logout
 * Logout user and invalidate session
 */
router.post('/logout', async (req: Request, res: Response) => {
  try {
    const token = req.header('Authorization')?.replace('Bearer ', '');
    
    if (token) {
      const decoded = jwt.verify(token, process.env.JWT_SECRET!) as any;
      
      // Remove session from Redis
      await redisService.deleteSession(decoded.userId);
      
      // Log logout event
      await securityService.logEvent({
        type: 'user_logout',
        userId: decoded.userId,
        email: decoded.email,
        ip: req.ip,
        userAgent: req.get('User-Agent')
      });

      logger.info(`User logged out: ${decoded.email}`);
    }

    res.json({
      message: 'Logout successful'
    });

  } catch (error) {
    logger.error('Logout error:', error);
    res.status(500).json({
      error: 'Logout failed',
      message: 'An internal error occurred during logout'
    });
  }
});

/**
 * GET /api/auth/me
 * Get current user information
 */
router.get('/me', async (req: Request, res: Response) => {
  try {
    const token = req.header('Authorization')?.replace('Bearer ', '');
    
    if (!token) {
      return res.status(401).json({
        error: 'No token provided',
        message: 'Authorization token is required'
      });
    }

    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as any;
    
    // Get user from Firebase
    const user = await firebaseService.getUserById(decoded.userId);
    if (!user) {
      return res.status(404).json({
        error: 'User not found',
        message: 'User account no longer exists'
      });
    }

    // Check session in Redis
    const session = await redisService.getSession(decoded.userId);
    if (!session) {
      return res.status(401).json({
        error: 'Session expired',
        message: 'Please log in again'
      });
    }

    res.json({
      user: {
        id: user.id,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
        role: user.role,
        subscription: user.subscription,
        createdAt: user.createdAt,
        lastLogin: session.loginTime
      }
    });

  } catch (error) {
    if (error instanceof jwt.JsonWebTokenError) {
      return res.status(401).json({
        error: 'Invalid token',
        message: 'Authorization token is invalid'
      });
    }

    logger.error('Get user error:', error);
    res.status(500).json({
      error: 'Failed to get user information',
      message: 'An internal error occurred'
    });
  }
});

/**
 * POST /api/auth/refresh
 * Refresh JWT token
 */
router.post('/refresh', async (req: Request, res: Response) => {
  try {
    const token = req.header('Authorization')?.replace('Bearer ', '');
    
    if (!token) {
      return res.status(401).json({
        error: 'No token provided',
        message: 'Authorization token is required'
      });
    }

    // Verify token (allow expired tokens for refresh)
    const decoded = jwt.verify(token, process.env.JWT_SECRET!, { ignoreExpiration: true }) as any;
    
    // Check if session exists in Redis
    const session = await redisService.getSession(decoded.userId);
    if (!session) {
      return res.status(401).json({
        error: 'Session expired',
        message: 'Please log in again'
      });
    }

    // Generate new token
    const newToken = jwt.sign(
      { 
        userId: decoded.userId,
        email: decoded.email,
        role: decoded.role
      },
      process.env.JWT_SECRET!,
      { expiresIn: '7d' }
    );

    res.json({
      message: 'Token refreshed successfully',
      token: newToken
    });

  } catch (error) {
    logger.error('Token refresh error:', error);
    res.status(401).json({
      error: 'Token refresh failed',
      message: 'Unable to refresh authorization token'
    });
  }
});

export default router;

