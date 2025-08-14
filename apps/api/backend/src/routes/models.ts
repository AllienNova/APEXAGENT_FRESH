/**
 * AI Models Routes
 * 
 * Handles AI model management, selection, and configuration
 */

import { Router, Request, Response } from 'express';
import { body, query, validationResult } from 'express-validator';
import { logger } from '../utils/logger';
import { AIModelService } from '../services/aiModels';
import { FirebaseService } from '../services/firebase';
import { AnalyticsService } from '../services/analytics';

const router = Router();

// Services
const aiModelService = new AIModelService();
const firebaseService = new FirebaseService();
const analyticsService = new AnalyticsService();

/**
 * GET /api/models
 * Get all available AI models
 */
router.get('/', async (req: Request, res: Response) => {
  try {
    const { provider, category, capability } = req.query;

    const models = await aiModelService.getAvailableModels({
      provider: provider as string,
      category: category as string,
      capability: capability as string
    });

    // Group models by provider
    const modelsByProvider = models.reduce((acc, model) => {
      if (!acc[model.provider]) {
        acc[model.provider] = [];
      }
      acc[model.provider].push(model);
      return acc;
    }, {} as Record<string, any[]>);

    res.json({
      models,
      modelsByProvider,
      totalModels: models.length,
      providers: Object.keys(modelsByProvider),
      categories: [...new Set(models.map(m => m.category))],
      capabilities: [...new Set(models.flatMap(m => m.capabilities))]
    });

  } catch (error) {
    logger.error('Get models error:', error);
    res.status(500).json({
      error: 'Failed to get models',
      message: 'An internal error occurred while fetching AI models'
    });
  }
});

/**
 * GET /api/models/:modelId
 * Get specific model details
 */
router.get('/:modelId', async (req: Request, res: Response) => {
  try {
    const { modelId } = req.params;

    const model = await aiModelService.getModelById(modelId);
    if (!model) {
      return res.status(404).json({
        error: 'Model not found',
        message: `Model with ID ${modelId} does not exist`
      });
    }

    // Get model usage statistics
    const usage = await analyticsService.getModelUsage(modelId);

    res.json({
      model,
      usage: {
        totalRequests: usage.totalRequests,
        averageResponseTime: usage.averageResponseTime,
        successRate: usage.successRate,
        lastUsed: usage.lastUsed
      }
    });

  } catch (error) {
    logger.error('Get model error:', error);
    res.status(500).json({
      error: 'Failed to get model',
      message: 'An internal error occurred while fetching model details'
    });
  }
});

/**
 * POST /api/models/test
 * Test a model with a sample prompt
 */
router.post('/test', [
  body('modelId').notEmpty().withMessage('Model ID is required'),
  body('prompt').isLength({ min: 1, max: 1000 }).withMessage('Prompt must be 1-1000 characters'),
  body('parameters').optional().isObject()
], async (req: Request, res: Response) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Validation failed',
        details: errors.array()
      });
    }

    const { modelId, prompt, parameters = {} } = req.body;
    const userId = (req as any).user?.userId;

    // Check if model exists
    const model = await aiModelService.getModelById(modelId);
    if (!model) {
      return res.status(404).json({
        error: 'Model not found',
        message: `Model with ID ${modelId} does not exist`
      });
    }

    // Check user's subscription and credits
    const user = await firebaseService.getUserById(userId);
    if (!user) {
      return res.status(404).json({
        error: 'User not found',
        message: 'User account does not exist'
      });
    }

    // Test the model
    const startTime = Date.now();
    const response = await aiModelService.testModel(modelId, prompt, {
      ...parameters,
      userId,
      testMode: true
    });
    const responseTime = Date.now() - startTime;

    // Log the test
    await analyticsService.logModelTest({
      userId,
      modelId,
      prompt,
      response: response.content,
      responseTime,
      success: response.success,
      timestamp: new Date().toISOString()
    });

    res.json({
      model: {
        id: model.id,
        name: model.name,
        provider: model.provider
      },
      test: {
        prompt,
        response: response.content,
        success: response.success,
        responseTime,
        tokensUsed: response.tokensUsed,
        cost: response.cost
      },
      metadata: {
        timestamp: new Date().toISOString(),
        testMode: true
      }
    });

  } catch (error) {
    logger.error('Model test error:', error);
    res.status(500).json({
      error: 'Model test failed',
      message: 'An internal error occurred while testing the model'
    });
  }
});

/**
 * POST /api/models/compare
 * Compare multiple models with the same prompt
 */
router.post('/compare', [
  body('modelIds').isArray({ min: 2, max: 5 }).withMessage('Must provide 2-5 model IDs'),
  body('prompt').isLength({ min: 1, max: 1000 }).withMessage('Prompt must be 1-1000 characters'),
  body('parameters').optional().isObject()
], async (req: Request, res: Response) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Validation failed',
        details: errors.array()
      });
    }

    const { modelIds, prompt, parameters = {} } = req.body;
    const userId = (req as any).user?.userId;

    // Validate all models exist
    const models = await Promise.all(
      modelIds.map(async (id: string) => {
        const model = await aiModelService.getModelById(id);
        if (!model) {
          throw new Error(`Model ${id} not found`);
        }
        return model;
      })
    );

    // Run comparison
    const comparisons = await Promise.all(
      models.map(async (model) => {
        const startTime = Date.now();
        try {
          const response = await aiModelService.testModel(model.id, prompt, {
            ...parameters,
            userId,
            testMode: true
          });
          const responseTime = Date.now() - startTime;

          return {
            model: {
              id: model.id,
              name: model.name,
              provider: model.provider,
              category: model.category
            },
            response: response.content,
            success: true,
            responseTime,
            tokensUsed: response.tokensUsed,
            cost: response.cost,
            error: null
          };
        } catch (error) {
          const responseTime = Date.now() - startTime;
          return {
            model: {
              id: model.id,
              name: model.name,
              provider: model.provider,
              category: model.category
            },
            response: null,
            success: false,
            responseTime,
            tokensUsed: 0,
            cost: 0,
            error: error instanceof Error ? error.message : 'Unknown error'
          };
        }
      })
    );

    // Log the comparison
    await analyticsService.logModelComparison({
      userId,
      modelIds,
      prompt,
      results: comparisons,
      timestamp: new Date().toISOString()
    });

    // Calculate summary statistics
    const successful = comparisons.filter(c => c.success);
    const summary = {
      totalModels: comparisons.length,
      successfulModels: successful.length,
      averageResponseTime: successful.length > 0 
        ? successful.reduce((sum, c) => sum + c.responseTime, 0) / successful.length 
        : 0,
      totalCost: comparisons.reduce((sum, c) => sum + c.cost, 0),
      fastestModel: successful.length > 0 
        ? successful.reduce((fastest, current) => 
            current.responseTime < fastest.responseTime ? current : fastest
          ).model
        : null,
      cheapestModel: successful.length > 0
        ? successful.reduce((cheapest, current) => 
            current.cost < cheapest.cost ? current : cheapest
          ).model
        : null
    };

    res.json({
      prompt,
      comparisons,
      summary,
      metadata: {
        timestamp: new Date().toISOString(),
        testMode: true
      }
    });

  } catch (error) {
    logger.error('Model comparison error:', error);
    res.status(500).json({
      error: 'Model comparison failed',
      message: 'An internal error occurred while comparing models'
    });
  }
});

/**
 * GET /api/models/recommendations
 * Get model recommendations based on user's usage patterns
 */
router.get('/recommendations', async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user?.userId;
    const { task, budget, speed, quality } = req.query;

    // Get user's usage history
    const usageHistory = await analyticsService.getUserModelUsage(userId);

    // Get recommendations
    const recommendations = await aiModelService.getRecommendations({
      userId,
      usageHistory,
      preferences: {
        task: task as string,
        budget: budget ? parseFloat(budget as string) : undefined,
        speed: speed as 'fast' | 'balanced' | 'quality',
        quality: quality as 'basic' | 'standard' | 'premium'
      }
    });

    res.json({
      recommendations,
      basedOn: {
        usageHistory: usageHistory.length > 0,
        preferences: { task, budget, speed, quality },
        totalPreviousRequests: usageHistory.reduce((sum, h) => sum + h.requestCount, 0)
      }
    });

  } catch (error) {
    logger.error('Get recommendations error:', error);
    res.status(500).json({
      error: 'Failed to get recommendations',
      message: 'An internal error occurred while generating recommendations'
    });
  }
});

/**
 * POST /api/models/configure
 * Configure user's preferred models and settings
 */
router.post('/configure', [
  body('preferences').isObject().withMessage('Preferences object is required'),
  body('preferences.defaultModel').optional().isString(),
  body('preferences.fallbackModels').optional().isArray(),
  body('preferences.maxCostPerRequest').optional().isNumeric(),
  body('preferences.categories').optional().isObject()
], async (req: Request, res: Response) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Validation failed',
        details: errors.array()
      });
    }

    const { preferences } = req.body;
    const userId = (req as any).user?.userId;

    // Validate model IDs if provided
    if (preferences.defaultModel) {
      const model = await aiModelService.getModelById(preferences.defaultModel);
      if (!model) {
        return res.status(400).json({
          error: 'Invalid default model',
          message: `Model ${preferences.defaultModel} does not exist`
        });
      }
    }

    if (preferences.fallbackModels) {
      for (const modelId of preferences.fallbackModels) {
        const model = await aiModelService.getModelById(modelId);
        if (!model) {
          return res.status(400).json({
            error: 'Invalid fallback model',
            message: `Model ${modelId} does not exist`
          });
        }
      }
    }

    // Save preferences
    await firebaseService.updateUserPreferences(userId, {
      modelPreferences: preferences,
      updatedAt: new Date().toISOString()
    });

    logger.info(`User ${userId} updated model preferences`);

    res.json({
      message: 'Model preferences updated successfully',
      preferences
    });

  } catch (error) {
    logger.error('Configure models error:', error);
    res.status(500).json({
      error: 'Failed to configure models',
      message: 'An internal error occurred while saving preferences'
    });
  }
});

/**
 * GET /api/models/usage
 * Get user's model usage statistics
 */
router.get('/usage', [
  query('period').optional().isIn(['day', 'week', 'month', 'year']),
  query('modelId').optional().isString()
], async (req: Request, res: Response) => {
  try {
    const userId = (req as any).user?.userId;
    const { period = 'month', modelId } = req.query;

    const usage = await analyticsService.getUserModelUsage(userId, {
      period: period as string,
      modelId: modelId as string
    });

    // Calculate summary statistics
    const summary = {
      totalRequests: usage.reduce((sum, u) => sum + u.requestCount, 0),
      totalCost: usage.reduce((sum, u) => sum + u.totalCost, 0),
      averageResponseTime: usage.length > 0 
        ? usage.reduce((sum, u) => sum + u.averageResponseTime, 0) / usage.length 
        : 0,
      mostUsedModel: usage.length > 0 
        ? usage.reduce((most, current) => 
            current.requestCount > most.requestCount ? current : most
          )
        : null,
      period,
      generatedAt: new Date().toISOString()
    };

    res.json({
      usage,
      summary
    });

  } catch (error) {
    logger.error('Get usage error:', error);
    res.status(500).json({
      error: 'Failed to get usage statistics',
      message: 'An internal error occurred while fetching usage data'
    });
  }
});

export default router;

