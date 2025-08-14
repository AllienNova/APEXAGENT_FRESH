/**
 * Chat Routes - Multi-Model AI Integration
 * 
 * Handles all chat-related endpoints including:
 * - Multi-model chat completion
 * - Streaming responses
 * - Conversation management
 * - Message history
 * - Model switching and optimization
 */

import express from 'express';
import { body, param, query, validationResult } from 'express-validator';
import rateLimit from 'express-rate-limit';
import { AIModelService } from '../services/aiModels';
import { ConversationService } from '../services/conversation';
import { AnalyticsService } from '../services/analytics';
import { SecurityService } from '../services/security';
import { logger } from '../utils/logger';
import { ApiError } from '../utils/errors';

const router = express.Router();

// Initialize services
const aiModelService = new AIModelService();
const conversationService = new ConversationService();
const analyticsService = new AnalyticsService();
const securityService = new SecurityService();

// Rate limiting for chat endpoints
const chatRateLimit = rateLimit({
  windowMs: 1 * 60 * 1000, // 1 minute
  max: 30, // 30 requests per minute
  message: {
    error: 'Too many chat requests, please slow down',
    retryAfter: '1 minute'
  },
  standardHeaders: true,
});

const streamRateLimit = rateLimit({
  windowMs: 1 * 60 * 1000, // 1 minute
  max: 10, // 10 streaming requests per minute
  message: {
    error: 'Too many streaming requests, please slow down',
    retryAfter: '1 minute'
  },
  standardHeaders: true,
});

// Validation middleware
const validateChatRequest = [
  body('message')
    .isString()
    .isLength({ min: 1, max: 50000 })
    .withMessage('Message must be between 1 and 50,000 characters'),
  body('model')
    .isString()
    .isLength({ min: 1, max: 100 })
    .withMessage('Model must be specified'),
  body('conversationId')
    .optional()
    .isUUID()
    .withMessage('Conversation ID must be a valid UUID'),
  body('temperature')
    .optional()
    .isFloat({ min: 0, max: 2 })
    .withMessage('Temperature must be between 0 and 2'),
  body('maxTokens')
    .optional()
    .isInt({ min: 1, max: 32000 })
    .withMessage('Max tokens must be between 1 and 32,000'),
  body('systemPrompt')
    .optional()
    .isString()
    .isLength({ max: 10000 })
    .withMessage('System prompt must be less than 10,000 characters'),
  body('stream')
    .optional()
    .isBoolean()
    .withMessage('Stream must be a boolean'),
];

const validateConversationId = [
  param('conversationId')
    .isUUID()
    .withMessage('Conversation ID must be a valid UUID'),
];

const validatePagination = [
  query('page')
    .optional()
    .isInt({ min: 1 })
    .withMessage('Page must be a positive integer'),
  query('limit')
    .optional()
    .isInt({ min: 1, max: 100 })
    .withMessage('Limit must be between 1 and 100'),
];

// Helper function to handle validation errors
const handleValidationErrors = (req: express.Request, res: express.Response, next: express.NextFunction) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      error: 'Validation failed',
      details: errors.array()
    });
  }
  next();
};

/**
 * POST /api/chat/send
 * Send a message to an AI model
 */
router.post('/send', 
  chatRateLimit,
  validateChatRequest,
  handleValidationErrors,
  async (req: express.Request, res: express.Response, next: express.NextFunction) => {
    try {
      const userId = req.user?.uid;
      const {
        message,
        model,
        conversationId,
        temperature = 0.7,
        maxTokens = 2000,
        systemPrompt,
        stream = false
      } = req.body;

      // Security check
      await securityService.validateMessage(message, userId);

      // Get or create conversation
      const conversation = conversationId 
        ? await conversationService.getConversation(conversationId, userId)
        : await conversationService.createConversation({
            userId,
            model,
            title: message.substring(0, 50) + (message.length > 50 ? '...' : ''),
            settings: { temperature, maxTokens, systemPrompt }
          });

      // Add user message to conversation
      const userMessage = await conversationService.addMessage(conversation.id, {
        role: 'user',
        content: message,
        userId
      });

      // Track analytics
      analyticsService.track('chat_message_sent', {
        userId,
        model,
        conversationId: conversation.id,
        messageLength: message.length,
        hasSystemPrompt: !!systemPrompt
      });

      // Handle streaming response
      if (stream) {
        return handleStreamingResponse(req, res, {
          conversation,
          userMessage,
          model,
          temperature,
          maxTokens,
          systemPrompt,
          userId
        });
      }

      // Generate AI response
      const startTime = Date.now();
      const aiResponse = await aiModelService.generateResponse({
        model,
        messages: await conversationService.getMessageHistory(conversation.id),
        temperature,
        maxTokens,
        systemPrompt,
        userId
      });

      const responseTime = Date.now() - startTime;

      // Add AI message to conversation
      const aiMessage = await conversationService.addMessage(conversation.id, {
        role: 'assistant',
        content: aiResponse.content,
        model: aiResponse.model,
        tokens: aiResponse.tokens,
        cost: aiResponse.cost,
        processingTime: responseTime
      });

      // Update conversation metadata
      await conversationService.updateConversation(conversation.id, {
        lastActiveAt: new Date(),
        totalTokens: conversation.totalTokens + aiResponse.tokens.total,
        totalCost: conversation.totalCost + aiResponse.cost
      });

      // Track response analytics
      analyticsService.track('chat_response_generated', {
        userId,
        model: aiResponse.model,
        conversationId: conversation.id,
        tokensUsed: aiResponse.tokens.total,
        cost: aiResponse.cost,
        responseTime,
        success: true
      });

      res.json({
        success: true,
        data: {
          response: aiResponse.content,
          messageId: aiMessage.id,
          conversationId: conversation.id,
          model: aiResponse.model,
          tokens: aiResponse.tokens,
          cost: aiResponse.cost,
          responseTime
        }
      });

    } catch (error) {
      logger.error('Chat send error:', error);
      
      // Track error analytics
      analyticsService.track('chat_error', {
        userId: req.user?.uid,
        error: error instanceof Error ? error.message : 'Unknown error',
        endpoint: '/chat/send'
      });

      next(error);
    }
  }
);

/**
 * POST /api/chat/stream
 * Stream a response from an AI model
 */
router.post('/stream',
  streamRateLimit,
  validateChatRequest,
  handleValidationErrors,
  async (req: express.Request, res: express.Response, next: express.NextFunction) => {
    try {
      const userId = req.user?.uid;
      const {
        message,
        model,
        conversationId,
        temperature = 0.7,
        maxTokens = 2000,
        systemPrompt
      } = req.body;

      // Set up Server-Sent Events
      res.setHeader('Content-Type', 'text/event-stream');
      res.setHeader('Cache-Control', 'no-cache');
      res.setHeader('Connection', 'keep-alive');
      res.setHeader('Access-Control-Allow-Origin', '*');

      // Security check
      await securityService.validateMessage(message, userId);

      // Get or create conversation
      const conversation = conversationId 
        ? await conversationService.getConversation(conversationId, userId)
        : await conversationService.createConversation({
            userId,
            model,
            title: message.substring(0, 50) + (message.length > 50 ? '...' : ''),
            settings: { temperature, maxTokens, systemPrompt }
          });

      // Add user message
      const userMessage = await conversationService.addMessage(conversation.id, {
        role: 'user',
        content: message,
        userId
      });

      // Send initial response
      res.write(`data: ${JSON.stringify({
        type: 'start',
        conversationId: conversation.id,
        messageId: userMessage.id
      })}\n\n`);

      // Generate streaming response
      const startTime = Date.now();
      let fullResponse = '';
      let tokenCount = 0;

      const stream = await aiModelService.generateStreamingResponse({
        model,
        messages: await conversationService.getMessageHistory(conversation.id),
        temperature,
        maxTokens,
        systemPrompt,
        userId
      });

      for await (const chunk of stream) {
        if (chunk.content) {
          fullResponse += chunk.content;
          tokenCount += chunk.tokens || 0;
          
          res.write(`data: ${JSON.stringify({
            type: 'content',
            content: chunk.content,
            tokens: chunk.tokens
          })}\n\n`);
        }
      }

      const responseTime = Date.now() - startTime;
      const cost = await aiModelService.calculateCost(model, tokenCount);

      // Add AI message to conversation
      const aiMessage = await conversationService.addMessage(conversation.id, {
        role: 'assistant',
        content: fullResponse,
        model,
        tokens: { total: tokenCount, input: 0, output: tokenCount },
        cost,
        processingTime: responseTime
      });

      // Send completion event
      res.write(`data: ${JSON.stringify({
        type: 'complete',
        messageId: aiMessage.id,
        totalTokens: tokenCount,
        cost,
        responseTime
      })}\n\n`);

      res.write('data: [DONE]\n\n');
      res.end();

      // Track analytics
      analyticsService.track('chat_stream_completed', {
        userId,
        model,
        conversationId: conversation.id,
        tokensUsed: tokenCount,
        cost,
        responseTime
      });

    } catch (error) {
      logger.error('Chat stream error:', error);
      
      res.write(`data: ${JSON.stringify({
        type: 'error',
        error: error instanceof Error ? error.message : 'Unknown error'
      })}\n\n`);
      
      res.end();
      
      analyticsService.track('chat_stream_error', {
        userId: req.user?.uid,
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  }
);

/**
 * GET /api/chat/conversations
 * Get user's conversations with pagination
 */
router.get('/conversations',
  validatePagination,
  handleValidationErrors,
  async (req: express.Request, res: express.Response, next: express.NextFunction) => {
    try {
      const userId = req.user?.uid;
      const page = parseInt(req.query.page as string) || 1;
      const limit = parseInt(req.query.limit as string) || 20;
      const projectId = req.query.projectId as string;

      const result = await conversationService.getUserConversations(userId, {
        page,
        limit,
        projectId
      });

      res.json({
        success: true,
        data: result
      });

    } catch (error) {
      logger.error('Get conversations error:', error);
      next(error);
    }
  }
);

/**
 * GET /api/chat/conversations/:conversationId
 * Get a specific conversation with messages
 */
router.get('/conversations/:conversationId',
  validateConversationId,
  handleValidationErrors,
  async (req: express.Request, res: express.Response, next: express.NextFunction) => {
    try {
      const userId = req.user?.uid;
      const { conversationId } = req.params;

      const conversation = await conversationService.getConversationWithMessages(
        conversationId, 
        userId
      );

      if (!conversation) {
        throw new ApiError(404, 'Conversation not found');
      }

      res.json({
        success: true,
        data: conversation
      });

    } catch (error) {
      logger.error('Get conversation error:', error);
      next(error);
    }
  }
);

/**
 * PUT /api/chat/conversations/:conversationId
 * Update conversation (title, settings, etc.)
 */
router.put('/conversations/:conversationId',
  validateConversationId,
  [
    body('title')
      .optional()
      .isString()
      .isLength({ min: 1, max: 200 })
      .withMessage('Title must be between 1 and 200 characters'),
    body('settings')
      .optional()
      .isObject()
      .withMessage('Settings must be an object'),
  ],
  handleValidationErrors,
  async (req: express.Request, res: express.Response, next: express.NextFunction) => {
    try {
      const userId = req.user?.uid;
      const { conversationId } = req.params;
      const updates = req.body;

      const conversation = await conversationService.updateConversation(
        conversationId,
        updates,
        userId
      );

      res.json({
        success: true,
        data: conversation
      });

    } catch (error) {
      logger.error('Update conversation error:', error);
      next(error);
    }
  }
);

/**
 * DELETE /api/chat/conversations/:conversationId
 * Delete a conversation
 */
router.delete('/conversations/:conversationId',
  validateConversationId,
  handleValidationErrors,
  async (req: express.Request, res: express.Response, next: express.NextFunction) => {
    try {
      const userId = req.user?.uid;
      const { conversationId } = req.params;

      await conversationService.deleteConversation(conversationId, userId);

      res.json({
        success: true,
        message: 'Conversation deleted successfully'
      });

    } catch (error) {
      logger.error('Delete conversation error:', error);
      next(error);
    }
  }
);

/**
 * GET /api/chat/history/:conversationId
 * Get message history for a conversation
 */
router.get('/history/:conversationId',
  validateConversationId,
  validatePagination,
  handleValidationErrors,
  async (req: express.Request, res: express.Response, next: express.NextFunction) => {
    try {
      const userId = req.user?.uid;
      const { conversationId } = req.params;
      const page = parseInt(req.query.page as string) || 1;
      const limit = parseInt(req.query.limit as string) || 50;

      const messages = await conversationService.getMessageHistory(
        conversationId,
        userId,
        { page, limit }
      );

      res.json({
        success: true,
        data: messages
      });

    } catch (error) {
      logger.error('Get message history error:', error);
      next(error);
    }
  }
);

// Helper function for streaming responses
async function handleStreamingResponse(
  req: express.Request,
  res: express.Response,
  options: any
) {
  // Implementation would be similar to the /stream endpoint
  // but integrated with the existing conversation flow
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  
  // ... streaming implementation
}

export default router;

