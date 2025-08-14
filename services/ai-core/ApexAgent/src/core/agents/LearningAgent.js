/**
 * LearningAgent.js
 * 
 * Learning agent for Aideon AI Lite.
 * Responsible for federated learning, personalization, and adapting to improve performance.
 * 
 * @author Aideon AI Team
 * @version 1.0.0
 */

const EventEmitter = require("events");
const { v4: uuidv4 } = require("uuid");

class LearningAgent {
  constructor(core) {
    this.core = core;
    this.logger = core.logManager.getLogger("agent:learning");
    this.events = new EventEmitter();
    this.knowledgeBase = new Map(); // Simplified knowledge base
    this.modelProvider = null;
    this.config = {
      defaultModel: "gpt-4-turbo",
      learningRate: 0.1,
      knowledgeDecayFactor: 0.99,
      minConfidenceForLearning: 0.7,
      maxKnowledgeEntries: 10000,
      enableFederatedLearning: false, // Placeholder for future implementation
      personalizationLevel: "medium", // Options: none, low, medium, high
    };
    this.metrics = {
      knowledgeEntries: 0,
      successfulLearnings: 0,
      failedLearnings: 0,
      knowledgeApplications: 0,
    };
  }

  /**
   * Initialize the Learning Agent
   * @returns {Promise<boolean>} Success status
   */
  async initialize() {
    this.logger.info("Initializing Learning Agent");

    try {
      // Load configuration
      const agentConfig =
        this.core.configManager.getConfig().agents?.learning || {};
      this.config = { ...this.config, ...agentConfig };

      // Initialize model provider
      this.modelProvider =
        await this.core.modelIntegrationFramework.getModelProvider(
          this.config.defaultModel
        );

      if (!this.modelProvider) {
        throw new Error(
          `Failed to initialize model provider for ${this.config.defaultModel}`
        );
      }

      // Load existing knowledge base (if any)
      await this._loadKnowledgeBase();

      this.logger.info("Learning Agent initialized successfully");
      return true;
    } catch (error) {
      this.logger.error(
        `Failed to initialize Learning Agent: ${error.message}`,
        error
      );
      return false;
    }
  }

  /**
   * Learn from a completed task execution
   * @param {Object} task - Task object
   * @param {Object} executionResult - Execution result
   * @param {Object} verificationResult - Verification result
   * @returns {Promise<boolean>} Learning success status
   */
  async learnFromExecution(task, executionResult, verificationResult) {
    this.logger.info(`Learning from execution of task ${task.id}`);

    try {
      // Extract key information for learning
      const learningInput = this._prepareLearningInput(
        task,
        executionResult,
        verificationResult
      );

      // Use model to analyze and extract insights
      const insights = await this._extractInsights(learningInput);

      // Update knowledge base with insights
      const updated = this._updateKnowledgeBase(insights);

      if (updated) {
        this.metrics.successfulLearnings++;
        this.logger.info(`Successfully learned from task ${task.id}`);
        this.events.emit("learning:success", { taskId: task.id, insights });
      } else {
        this.metrics.failedLearnings++;
        this.logger.warn(`No significant insights gained from task ${task.id}`);
        this.events.emit("learning:no_insights", { taskId: task.id });
      }

      // Persist knowledge base changes
      await this._persistKnowledgeBase();

      return updated;
    } catch (error) {
      this.metrics.failedLearnings++;
      this.logger.error(
        `Failed to learn from execution for task ${task.id}: ${error.message}`,
        error
      );
      this.events.emit("learning:failed", { taskId: task.id, error });
      return false;
    }
  }

  /**
   * Apply learned knowledge to a new task or plan
   * @param {Object} context - Context for applying knowledge (e.g., task, plan)
   * @returns {Promise<Object>} Applied knowledge or suggestions
   */
  async applyKnowledge(context) {
    this.logger.info(`Applying learned knowledge to context: ${context.id}`);

    try {
      // Identify relevant knowledge entries
      const relevantKnowledge = this._findRelevantKnowledge(context);

      if (relevantKnowledge.length === 0) {
        this.logger.info("No relevant knowledge found for this context");
        return { applied: false, suggestions: [] };
      }

      // Generate suggestions based on relevant knowledge
      const suggestions = await this._generateSuggestionsFromKnowledge(
        context,
        relevantKnowledge
      );

      this.metrics.knowledgeApplications++;
      this.logger.info(
        `Applied knowledge, generated ${suggestions.length} suggestions`
      );
      this.events.emit("knowledge:applied", { contextId: context.id, suggestions });

      return {
        applied: true,
        suggestions,
      };
    } catch (error) {
      this.logger.error(
        `Failed to apply knowledge for context ${context.id}: ${error.message}`,
        error
      );
      this.events.emit("knowledge:apply_failed", { contextId: context.id, error });
      return { applied: false, suggestions: [] };
    }
  }

  /**
   * Get learning metrics
   * @returns {Object} Learning metrics
   */
  getMetrics() {
    return { ...this.metrics, knowledgeEntries: this.knowledgeBase.size };
  }

  /**
   * Register an event listener
   * @param {string} event - Event name
   * @param {Function} listener - Event listener
   */
  on(event, listener) {
    this.events.on(event, listener);
  }

  /**
   * Remove an event listener
   * @param {string} event - Event name
   * @param {Function} listener - Event listener
   */
  off(event, listener) {
    this.events.off(event, listener);
  }

  /**
   * Prepare input for the learning model
   * @param {Object} task - Task object
   * @param {Object} executionResult - Execution result
   * @param {Object} verificationResult - Verification result
   * @returns {Object} Learning input
   * @private
   */
  _prepareLearningInput(task, executionResult, verificationResult) {
    // Simplify and structure data for the model
    return {
      taskId: task.id,
      taskType: task.type || "general",
      taskComplexity: task.complexity || "medium",
      success: verificationResult.success,
      executionDuration: executionResult.duration,
      toolsUsed: executionResult.metadata?.tools || [],
      verificationIssues: verificationResult.issues || [],
      verificationConfidence: verificationResult.confidence,
      // Add more relevant fields as needed
    };
  }

  /**
   * Use the model to extract insights from learning input
   * @param {Object} learningInput - Prepared learning input
   * @returns {Promise<Array<Object>>} Extracted insights
   * @private
   */
  async _extractInsights(learningInput) {
    try {
      const prompt = `Analyze the following task execution data and extract key insights for improving future performance. Focus on patterns, successful strategies, common failures, and potential optimizations.

Execution Data:
${JSON.stringify(learningInput, null, 2)}

Format your response as a JSON array of insight objects, each with 'type', 'description', 'confidence', and 'relevance' fields. Types can be 'success_pattern', 'failure_pattern', 'optimization_opportunity', 'tool_effectiveness', etc.

Example:
[
  {
    "type": "failure_pattern",
    "description": "Using tool X for task type Y often leads to verification issues.",
    "confidence": 0.85,
    "relevance": 0.9
  }
]

Insights:
`;

      const response = await this.modelProvider.generateText({
        prompt,
        maxTokens: 500,
        temperature: 0.3,
        responseFormat: "json",
      });

      const insights = JSON.parse(response.text);
      return Array.isArray(insights) ? insights : [];
    } catch (error) {
      this.logger.error(`Failed to extract insights: ${error.message}`, error);
      return [];
    }
  }

  /**
   * Update the knowledge base with new insights
   * @param {Array<Object>} insights - Insights to add
   * @returns {boolean} Whether the knowledge base was updated
   * @private
   */
  _updateKnowledgeBase(insights) {
    let updated = false;
    for (const insight of insights) {
      if (insight.confidence >= this.config.minConfidenceForLearning) {
        const knowledgeId = uuidv4();
        this.knowledgeBase.set(knowledgeId, {
          ...insight,
          id: knowledgeId,
          addedAt: Date.now(),
          lastUsed: null,
          usageCount: 0,
        });
        updated = true;
      }
    }

    // Prune knowledge base if it exceeds max size
    this._pruneKnowledgeBase();

    return updated;
  }

  /**
   * Prune the knowledge base to maintain size limits
   * @private
   */
  _pruneKnowledgeBase() {
    if (this.knowledgeBase.size > this.config.maxKnowledgeEntries) {
      this.logger.info(
        `Pruning knowledge base (current size: ${this.knowledgeBase.size})`
      );
      const entries = Array.from(this.knowledgeBase.values());

      // Sort by relevance (usage count, recency, confidence)
      entries.sort((a, b) => {
        const scoreA = (a.usageCount || 0) + (a.lastUsed || a.addedAt) / 1e12 + a.confidence;
        const scoreB = (b.usageCount || 0) + (b.lastUsed || b.addedAt) / 1e12 + b.confidence;
        return scoreA - scoreB; // Sort ascending, lowest score first
      });

      // Remove least relevant entries
      const entriesToRemove = this.knowledgeBase.size - this.config.maxKnowledgeEntries;
      for (let i = 0; i < entriesToRemove; i++) {
        this.knowledgeBase.delete(entries[i].id);
      }

      this.logger.info(
        `Knowledge base pruned to ${this.knowledgeBase.size} entries`
      );
    }
  }

  /**
   * Find knowledge entries relevant to the current context
   * @param {Object} context - Context object (e.g., task, plan)
   * @returns {Array<Object>} Relevant knowledge entries
   * @private
   */
  _findRelevantKnowledge(context) {
    // In a real implementation, this would use more sophisticated matching
    // (e.g., embeddings, keyword matching, context analysis)

    // Simplified relevance check based on task type
    const relevantEntries = [];
    const contextType = context.type || "general";

    for (const entry of this.knowledgeBase.values()) {
      // Simple check: if insight description mentions task type
      if (
        entry.description
          .toLowerCase()
          .includes(contextType.toLowerCase())
      ) {
        relevantEntries.push(entry);
      }
    }

    // Sort by confidence and recency
    relevantEntries.sort((a, b) => {
        const scoreA = a.confidence + (a.lastUsed || a.addedAt) / 1e12;
        const scoreB = b.confidence + (b.lastUsed || b.addedAt) / 1e12;
        return scoreB - scoreA; // Sort descending, highest score first
    });

    return relevantEntries.slice(0, 10); // Limit to top 10 relevant entries
  }

  /**
   * Generate suggestions based on relevant knowledge
   * @param {Object} context - Context object
   * @param {Array<Object>} relevantKnowledge - Relevant knowledge entries
   * @returns {Promise<Array<Object>>} Generated suggestions
   * @private
   */
  async _generateSuggestionsFromKnowledge(context, relevantKnowledge) {
    try {
      const prompt = `Given the following context and relevant knowledge insights, generate actionable suggestions to improve the task or plan.

Context:
${JSON.stringify(context, null, 2)}

Relevant Knowledge:
${JSON.stringify(relevantKnowledge, null, 2)}

Format your response as a JSON array of suggestion objects, each with 'type', 'description', 'priority', and 'confidence' fields. Types can be 'tool_recommendation', 'process_change', 'parameter_tuning', 'risk_mitigation', etc.

Example:
[
  {
    "type": "tool_recommendation",
    "description": "Consider using tool Y instead of tool X for this task type.",
    "priority": "medium",
    "confidence": 0.9
  }
]

Suggestions:
`;

      const response = await this.modelProvider.generateText({
        prompt,
        maxTokens: 500,
        temperature: 0.4,
        responseFormat: "json",
      });

      const suggestions = JSON.parse(response.text);

      // Update usage stats for applied knowledge
      for (const entry of relevantKnowledge) {
        entry.usageCount = (entry.usageCount || 0) + 1;
        entry.lastUsed = Date.now();
      }
      await this._persistKnowledgeBase();

      return Array.isArray(suggestions) ? suggestions : [];
    } catch (error) {
      this.logger.error(
        `Failed to generate suggestions from knowledge: ${error.message}`,
        error
      );
      return [];
    }
  }

  /**
   * Load knowledge base from persistent storage
   * @private
   */
  async _loadKnowledgeBase() {
    // Placeholder for loading from a file or database
    this.logger.info("Loading knowledge base (placeholder - using in-memory)");
    // In a real implementation, load from this.core.storageManager
    this.metrics.knowledgeEntries = this.knowledgeBase.size;
  }

  /**
   * Persist knowledge base to storage
   * @private
   */
  async _persistKnowledgeBase() {
    // Placeholder for saving to a file or database
    // this.logger.debug("Persisting knowledge base (placeholder)");
    // In a real implementation, save using this.core.storageManager
    this.metrics.knowledgeEntries = this.knowledgeBase.size;
  }
}

module.exports = LearningAgent;

