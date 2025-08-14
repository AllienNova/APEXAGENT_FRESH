/**
 * Agents Routes
 * 
 * Handles multi-agent orchestration, task management, and agent coordination
 */

import { Router, Request, Response } from 'express';
import { body, query, param, validationResult } from 'express-validator';
import { logger } from '../utils/logger';
import { AgentOrchestrator } from '../services/agentOrchestrator';
import { FirebaseService } from '../services/firebase';
import { AnalyticsService } from '../services/analytics';
import { WebSocketService } from '../services/websocket';

const router = Router();

// Services
const agentOrchestrator = new AgentOrchestrator();
const firebaseService = new FirebaseService();
const analyticsService = new AnalyticsService();

/**
 * GET /api/agents
 * Get all available agents and their capabilities
 */
router.get('/', async (req: Request, res: Response) => {
  try {
    const agents = await agentOrchestrator.getAvailableAgents();

    // Group agents by category
    const agentsByCategory = agents.reduce((acc, agent) => {
      if (!acc[agent.category]) {
        acc[agent.category] = [];
      }
      acc[agent.category].push(agent);
      return acc;
    }, {} as Record<string, any[]>);

    res.json({
      agents,
      agentsByCategory,
      totalAgents: agents.length,
      categories: Object.keys(agentsByCategory),
      capabilities: [...new Set(agents.flatMap(a => a.capabilities))]
    });

  } catch (error) {
    logger.error('Get agents error:', error);
    res.status(500).json({
      error: 'Failed to get agents',
      message: 'An internal error occurred while fetching agents'
    });
  }
});

/**
 * GET /api/agents/:agentId
 * Get specific agent details and status
 */
router.get('/:agentId', [
  param('agentId').notEmpty().withMessage('Agent ID is required')
], async (req: Request, res: Response) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Validation failed',
        details: errors.array()
      });
    }

    const { agentId } = req.params;

    const agent = await agentOrchestrator.getAgentById(agentId);
    if (!agent) {
      return res.status(404).json({
        error: 'Agent not found',
        message: `Agent with ID ${agentId} does not exist`
      });
    }

    // Get agent status and performance metrics
    const status = await agentOrchestrator.getAgentStatus(agentId);
    const metrics = await analyticsService.getAgentMetrics(agentId);

    res.json({
      agent,
      status,
      metrics: {
        totalTasks: metrics.totalTasks,
        successRate: metrics.successRate,
        averageExecutionTime: metrics.averageExecutionTime,
        lastActive: metrics.lastActive,
        currentLoad: metrics.currentLoad
      }
    });

  } catch (error) {
    logger.error('Get agent error:', error);
    res.status(500).json({
      error: 'Failed to get agent',
      message: 'An internal error occurred while fetching agent details'
    });
  }
});

/**
 * POST /api/agents/orchestrate
 * Orchestrate a complex task across multiple agents
 */
router.post('/orchestrate', [
  body('task').isObject().withMessage('Task object is required'),
  body('task.description').notEmpty().withMessage('Task description is required'),
  body('task.type').isIn(['research', 'analysis', 'creation', 'automation', 'problem_solving']),
  body('task.priority').optional().isIn(['low', 'medium', 'high', 'urgent']),
  body('task.deadline').optional().isISO8601(),
  body('preferences').optional().isObject(),
  body('context').optional().isObject()
], async (req: Request, res: Response) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Validation failed',
        details: errors.array()
      });
    }

    const { task, preferences = {}, context = {} } = req.body;
    const userId = (req as any).user?.userId;

    // Create orchestration plan
    const orchestrationPlan = await agentOrchestrator.createOrchestrationPlan({
      task,
      userId,
      preferences,
      context
    });

    // Start orchestration
    const orchestrationId = await agentOrchestrator.startOrchestration(orchestrationPlan);

    // Log the orchestration start
    await analyticsService.logOrchestrationStart({
      orchestrationId,
      userId,
      task,
      agentCount: orchestrationPlan.agents.length,
      estimatedDuration: orchestrationPlan.estimatedDuration,
      timestamp: new Date().toISOString()
    });

    logger.info(`Started orchestration ${orchestrationId} for user ${userId}`);

    res.json({
      orchestrationId,
      plan: {
        agents: orchestrationPlan.agents.map(a => ({
          id: a.id,
          name: a.name,
          role: a.role,
          estimatedDuration: a.estimatedDuration
        })),
        totalSteps: orchestrationPlan.steps.length,
        estimatedDuration: orchestrationPlan.estimatedDuration,
        priority: orchestrationPlan.priority
      },
      status: 'started',
      message: 'Orchestration started successfully'
    });

  } catch (error) {
    logger.error('Orchestration error:', error);
    res.status(500).json({
      error: 'Orchestration failed',
      message: 'An internal error occurred while starting orchestration'
    });
  }
});

/**
 * GET /api/agents/orchestrations/:orchestrationId
 * Get orchestration status and progress
 */
router.get('/orchestrations/:orchestrationId', [
  param('orchestrationId').notEmpty().withMessage('Orchestration ID is required')
], async (req: Request, res: Response) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Validation failed',
        details: errors.array()
      });
    }

    const { orchestrationId } = req.params;
    const userId = (req as any).user?.userId;

    const orchestration = await agentOrchestrator.getOrchestration(orchestrationId);
    if (!orchestration) {
      return res.status(404).json({
        error: 'Orchestration not found',
        message: `Orchestration with ID ${orchestrationId} does not exist`
      });
    }

    // Check if user owns this orchestration
    if (orchestration.userId !== userId) {
      return res.status(403).json({
        error: 'Access denied',
        message: 'You do not have permission to view this orchestration'
      });
    }

    res.json({
      orchestration: {
        id: orchestration.id,
        status: orchestration.status,
        progress: orchestration.progress,
        currentStep: orchestration.currentStep,
        totalSteps: orchestration.totalSteps,
        startedAt: orchestration.startedAt,
        estimatedCompletion: orchestration.estimatedCompletion,
        results: orchestration.results
      },
      agents: orchestration.agents.map(agent => ({
        id: agent.id,
        name: agent.name,
        status: agent.status,
        progress: agent.progress,
        currentTask: agent.currentTask,
        results: agent.results
      }))
    });

  } catch (error) {
    logger.error('Get orchestration error:', error);
    res.status(500).json({
      error: 'Failed to get orchestration',
      message: 'An internal error occurred while fetching orchestration status'
    });
  }
});

/**
 * POST /api/agents/orchestrations/:orchestrationId/cancel
 * Cancel a running orchestration
 */
router.post('/orchestrations/:orchestrationId/cancel', [
  param('orchestrationId').notEmpty().withMessage('Orchestration ID is required')
], async (req: Request, res: Response) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Validation failed',
        details: errors.array()
      });
    }

    const { orchestrationId } = req.params;
    const userId = (req as any).user?.userId;

    const orchestration = await agentOrchestrator.getOrchestration(orchestrationId);
    if (!orchestration) {
      return res.status(404).json({
        error: 'Orchestration not found',
        message: `Orchestration with ID ${orchestrationId} does not exist`
      });
    }

    // Check if user owns this orchestration
    if (orchestration.userId !== userId) {
      return res.status(403).json({
        error: 'Access denied',
        message: 'You do not have permission to cancel this orchestration'
      });
    }

    // Check if orchestration can be cancelled
    if (!['running', 'pending', 'paused'].includes(orchestration.status)) {
      return res.status(400).json({
        error: 'Cannot cancel orchestration',
        message: `Orchestration is ${orchestration.status} and cannot be cancelled`
      });
    }

    // Cancel the orchestration
    await agentOrchestrator.cancelOrchestration(orchestrationId);

    // Log the cancellation
    await analyticsService.logOrchestrationCancel({
      orchestrationId,
      userId,
      cancelledAt: new Date().toISOString(),
      progress: orchestration.progress
    });

    logger.info(`Cancelled orchestration ${orchestrationId} for user ${userId}`);

    res.json({
      message: 'Orchestration cancelled successfully',
      orchestrationId,
      status: 'cancelled'
    });

  } catch (error) {
    logger.error('Cancel orchestration error:', error);
    res.status(500).json({
      error: 'Failed to cancel orchestration',
      message: 'An internal error occurred while cancelling orchestration'
    });
  }
});

/**
 * GET /api/agents/orchestrations
 * Get user's orchestration history
 */
router.get('/orchestrations', [
  query('status').optional().isIn(['pending', 'running', 'completed', 'failed', 'cancelled']),
  query('limit').optional().isInt({ min: 1, max: 100 }),
  query('offset').optional().isInt({ min: 0 })
], async (req: Request, res: Response) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Validation failed',
        details: errors.array()
      });
    }

    const userId = (req as any).user?.userId;
    const { status, limit = 20, offset = 0 } = req.query;

    const orchestrations = await agentOrchestrator.getUserOrchestrations(userId, {
      status: status as string,
      limit: parseInt(limit as string),
      offset: parseInt(offset as string)
    });

    const total = await agentOrchestrator.getUserOrchestrationsCount(userId, {
      status: status as string
    });

    res.json({
      orchestrations: orchestrations.map(o => ({
        id: o.id,
        task: o.task,
        status: o.status,
        progress: o.progress,
        agentCount: o.agents.length,
        startedAt: o.startedAt,
        completedAt: o.completedAt,
        duration: o.duration,
        success: o.success
      })),
      pagination: {
        total,
        limit: parseInt(limit as string),
        offset: parseInt(offset as string),
        hasMore: total > parseInt(offset as string) + parseInt(limit as string)
      }
    });

  } catch (error) {
    logger.error('Get orchestrations error:', error);
    res.status(500).json({
      error: 'Failed to get orchestrations',
      message: 'An internal error occurred while fetching orchestrations'
    });
  }
});

/**
 * POST /api/agents/:agentId/task
 * Assign a direct task to a specific agent
 */
router.post('/:agentId/task', [
  param('agentId').notEmpty().withMessage('Agent ID is required'),
  body('task').isObject().withMessage('Task object is required'),
  body('task.description').notEmpty().withMessage('Task description is required'),
  body('task.input').optional().isObject(),
  body('task.parameters').optional().isObject(),
  body('priority').optional().isIn(['low', 'medium', 'high', 'urgent'])
], async (req: Request, res: Response) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Validation failed',
        details: errors.array()
      });
    }

    const { agentId } = req.params;
    const { task, priority = 'medium' } = req.body;
    const userId = (req as any).user?.userId;

    // Check if agent exists and is available
    const agent = await agentOrchestrator.getAgentById(agentId);
    if (!agent) {
      return res.status(404).json({
        error: 'Agent not found',
        message: `Agent with ID ${agentId} does not exist`
      });
    }

    const status = await agentOrchestrator.getAgentStatus(agentId);
    if (status.status !== 'available') {
      return res.status(409).json({
        error: 'Agent not available',
        message: `Agent is currently ${status.status} and cannot accept new tasks`
      });
    }

    // Assign task to agent
    const taskId = await agentOrchestrator.assignTask(agentId, {
      ...task,
      userId,
      priority,
      assignedAt: new Date().toISOString()
    });

    // Log the task assignment
    await analyticsService.logTaskAssignment({
      taskId,
      agentId,
      userId,
      task,
      priority,
      timestamp: new Date().toISOString()
    });

    logger.info(`Assigned task ${taskId} to agent ${agentId} for user ${userId}`);

    res.json({
      taskId,
      agent: {
        id: agent.id,
        name: agent.name,
        capabilities: agent.capabilities
      },
      task: {
        description: task.description,
        priority,
        status: 'assigned'
      },
      message: 'Task assigned successfully'
    });

  } catch (error) {
    logger.error('Assign task error:', error);
    res.status(500).json({
      error: 'Failed to assign task',
      message: 'An internal error occurred while assigning task to agent'
    });
  }
});

/**
 * GET /api/agents/system/status
 * Get overall agent system status
 */
router.get('/system/status', async (req: Request, res: Response) => {
  try {
    const systemStatus = await agentOrchestrator.getSystemStatus();

    res.json({
      system: {
        status: systemStatus.status,
        totalAgents: systemStatus.totalAgents,
        availableAgents: systemStatus.availableAgents,
        busyAgents: systemStatus.busyAgents,
        offlineAgents: systemStatus.offlineAgents,
        activeOrchestrations: systemStatus.activeOrchestrations,
        queuedTasks: systemStatus.queuedTasks
      },
      performance: {
        averageResponseTime: systemStatus.averageResponseTime,
        systemLoad: systemStatus.systemLoad,
        memoryUsage: systemStatus.memoryUsage,
        cpuUsage: systemStatus.cpuUsage
      },
      health: {
        lastHealthCheck: systemStatus.lastHealthCheck,
        uptime: systemStatus.uptime,
        errors: systemStatus.recentErrors
      }
    });

  } catch (error) {
    logger.error('Get system status error:', error);
    res.status(500).json({
      error: 'Failed to get system status',
      message: 'An internal error occurred while fetching system status'
    });
  }
});

export default router;

