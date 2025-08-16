/**
 * Agent-Model Integration for Aideon AI Lite
 * 
 * This file provides the integration between the Agent Manager and the Model Integration Framework,
 * allowing agents to seamlessly use different models across modalities.
 */

const path = require('path');
const fs = require('fs').promises;

/**
 * AgentModelIntegration class
 * Connects the Agent Manager with the Model Integration Framework
 */
class AgentModelIntegration {
  /**
   * Initialize the Agent-Model Integration
   * @param {Object} core - Reference to the AideonCore instance
   */
  constructor(core) {
    this.core = core;
    this.logger = core.logManager.getLogger('agent-model-integration');
    this.agentManager = core.agentManager;
    this.modelFramework = core.modelIntegrationFramework;
    this.config = core.configManager.getConfig().agentModel || {};
    
    // Agent-specific model preferences
    this.agentModelPreferences = new Map();
    
    // Model capability registry
    this.modelCapabilities = new Map();
    
    this.initialized = false;
    
    this.logger.info('Agent-Model Integration initialized');
  }
  
  /**
   * Initialize the integration
   * @returns {Promise<void>}
   */
  async initialize() {
    if (this.initialized) {
      return;
    }
    
    try {
      this.logger.info('Initializing Agent-Model Integration...');
      
      // Ensure model framework is initialized
      if (!this.modelFramework.initialized) {
        await this.modelFramework.initialize();
      }
      
      // Register with agent manager
      this._registerWithAgentManager();
      
      // Load agent model preferences
      await this._loadAgentModelPreferences();
      
      // Build model capability registry
      await this._buildModelCapabilityRegistry();
      
      this.initialized = true;
      this.logger.info('Agent-Model Integration initialized successfully');
    } catch (error) {
      this.logger.error('Failed to initialize Agent-Model Integration:', error);
      throw error;
    }
  }
  
  /**
   * Register with the agent manager
   * @private
   */
  _registerWithAgentManager() {
    // Register model capabilities with agent manager
    this.agentManager.registerCapabilityProvider('model', this);
    
    // Register event listeners
    this.agentManager.on('agent:created', this._handleAgentCreated.bind(this));
    this.agentManager.on('agent:destroyed', this._handleAgentDestroyed.bind(this));
    
    this.logger.info('Registered with Agent Manager');
  }
  
  /**
   * Handle agent created event
   * @param {Object} agent - Agent instance
   * @private
   */
  _handleAgentCreated(agent) {
    // Set default model preferences for the agent
    this._setDefaultModelPreferences(agent);
    
    this.logger.info(`Set default model preferences for agent ${agent.id}`);
  }
  
  /**
   * Handle agent destroyed event
   * @param {string} agentId - Agent ID
   * @private
   */
  _handleAgentDestroyed(agentId) {
    // Remove agent model preferences
    this.agentModelPreferences.delete(agentId);
    
    this.logger.info(`Removed model preferences for agent ${agentId}`);
  }
  
  /**
   * Set default model preferences for an agent
   * @param {Object} agent - Agent instance
   * @private
   */
  _setDefaultModelPreferences(agent) {
    // Get agent role
    const role = agent.role || 'general';
    
    // Get default preferences for the role
    const defaultPreferences = this._getDefaultPreferencesForRole(role);
    
    // Set preferences for the agent
    this.agentModelPreferences.set(agent.id, defaultPreferences);
  }
  
  /**
   * Get default model preferences for a role
   * @param {string} role - Agent role
   * @returns {Object} Default preferences
   * @private
   */
  _getDefaultPreferencesForRole(role) {
    // Default preferences for different roles
    const rolePreferences = {
      'planner': {
        text: {
          preferredModels: ['gpt-4.5', 'claude-3.7-sonnet', 'llama-3.1-70b'],
          requirements: {
            minContextWindow: 32000,
            processingPreference: 'cloud'
          }
        },
        code: {
          preferredModels: ['o3-mini', 'claude-3.7-sonnet', 'deepseek-coder-v2'],
          requirements: {
            processingPreference: 'cloud'
          }
        }
      },
      'execution': {
        text: {
          preferredModels: ['claude-3.7-sonnet', 'gpt-4.5', 'llama-3.1-70b'],
          requirements: {
            processingPreference: 'auto'
          }
        },
        code: {
          preferredModels: ['o3-mini', 'deepseek-coder-v2', 'qwen2-72b-coder'],
          requirements: {
            processingPreference: 'auto'
          }
        },
        image: {
          preferredModels: ['dall-e-3', 'flux-1-dev', 'stable-diffusion-3'],
          requirements: {
            processingPreference: 'auto'
          }
        },
        video: {
          preferredModels: ['skyreel-v1', 'hunyuan-video', 'ltx-video'],
          requirements: {
            processingPreference: 'auto'
          }
        },
        audio: {
          preferredModels: ['stable-audio-2.0', 'stable-audio-open-small', 'audiocraft-musicgen'],
          requirements: {
            processingPreference: 'auto'
          }
        }
      },
      'verification': {
        text: {
          preferredModels: ['claude-3.7-sonnet', 'gpt-4.5', 'llama-3.1-70b'],
          requirements: {
            processingPreference: 'cloud'
          }
        },
        code: {
          preferredModels: ['o3-mini', 'claude-3.7-sonnet', 'deepseek-coder-v2'],
          requirements: {
            processingPreference: 'cloud'
          }
        }
      },
      'security': {
        text: {
          preferredModels: ['claude-3.7-sonnet', 'gpt-4.5', 'llama-3.1-70b'],
          requirements: {
            processingPreference: 'cloud'
          }
        }
      },
      'optimization': {
        text: {
          preferredModels: ['gpt-4.5', 'claude-3.7-sonnet', 'llama-3.1-70b'],
          requirements: {
            processingPreference: 'auto'
          }
        }
      },
      'learning': {
        text: {
          preferredModels: ['gpt-4.5', 'claude-3.7-sonnet', 'llama-3.1-70b'],
          requirements: {
            processingPreference: 'auto'
          }
        }
      },
      'general': {
        text: {
          preferredModels: ['gpt-4.5', 'claude-3.7-sonnet', 'llama-3.1-70b'],
          requirements: {
            processingPreference: 'auto'
          }
        },
        code: {
          preferredModels: ['o3-mini', 'claude-3.7-sonnet', 'deepseek-coder-v2'],
          requirements: {
            processingPreference: 'auto'
          }
        },
        image: {
          preferredModels: ['dall-e-3', 'flux-1-dev', 'stable-diffusion-3'],
          requirements: {
            processingPreference: 'auto'
          }
        },
        video: {
          preferredModels: ['skyreel-v1', 'hunyuan-video', 'ltx-video'],
          requirements: {
            processingPreference: 'auto'
          }
        },
        audio: {
          preferredModels: ['stable-audio-2.0', 'stable-audio-open-small', 'audiocraft-musicgen'],
          requirements: {
            processingPreference: 'auto'
          }
        }
      }
    };
    
    // Return preferences for the role, or general if not found
    return rolePreferences[role] || rolePreferences.general;
  }
  
  /**
   * Load agent model preferences from configuration
   * @returns {Promise<void>}
   * @private
   */
  async _loadAgentModelPreferences() {
    try {
      // Check if preferences file exists
      const preferencesPath = path.join(process.cwd(), 'config', 'agent_model_preferences.json');
      
      try {
        await fs.access(preferencesPath);
        
        // Load preferences
        const preferencesData = await fs.readFile(preferencesPath, 'utf8');
        const preferences = JSON.parse(preferencesData);
        
        // Apply preferences to existing agents
        for (const [agentId, agentPreferences] of Object.entries(preferences)) {
          const agent = this.agentManager.getAgent(agentId);
          
          if (agent) {
            this.agentModelPreferences.set(agentId, agentPreferences);
          }
        }
        
        this.logger.info('Loaded agent model preferences from configuration');
      } catch (error) {
        // File doesn't exist or is invalid, just log and continue
        this.logger.info('No agent model preferences configuration found, using defaults');
      }
    } catch (error) {
      this.logger.error('Failed to load agent model preferences:', error);
      // Don't throw, just use defaults
    }
  }
  
  /**
   * Build model capability registry
   * @returns {Promise<void>}
   * @private
   */
  async _buildModelCapabilityRegistry() {
    try {
      // Get all modalities
      const modalities = ['text', 'code', 'image', 'video', 'audio'];
      
      for (const modality of modalities) {
        // Get all models for the modality
        const models = this.modelFramework.getModelsByModality(modality);
        
        // Register capabilities for each model
        for (const model of models) {
          this._registerModelCapabilities(model);
        }
      }
      
      this.logger.info('Built model capability registry');
    } catch (error) {
      this.logger.error('Failed to build model capability registry:', error);
      throw error;
    }
  }
  
  /**
   * Register capabilities for a model
   * @param {Object} model - Model instance
   * @private
   */
  _registerModelCapabilities(model) {
    // Basic capabilities based on modality
    const baseCapabilities = {
      'text': ['text_generation', 'summarization', 'translation', 'question_answering'],
      'code': ['code_generation', 'code_completion', 'code_explanation', 'debugging'],
      'image': ['image_generation', 'image_editing', 'style_transfer'],
      'video': ['video_generation', 'video_editing', 'animation'],
      'audio': ['audio_generation', 'text_to_speech', 'music_generation', 'sound_effects']
    };
    
    // Get base capabilities for the modality
    const capabilities = baseCapabilities[model.modality] || [];
    
    // Add model-specific capabilities
    switch (model.id) {
      case 'gpt-4.5':
        capabilities.push('reasoning', 'planning', 'creative_writing');
        break;
      case 'claude-3.7-sonnet':
        capabilities.push('reasoning', 'document_analysis', 'safety');
        break;
      case 'o3-mini':
        capabilities.push('code_optimization', 'technical_documentation');
        break;
      case 'dall-e-3':
        capabilities.push('photorealistic_images', 'text_rendering');
        break;
      case 'stable-diffusion-3':
        capabilities.push('text_rendering', 'style_customization');
        break;
      case 'skyreel-v1':
        capabilities.push('human_animation', 'cinematic_quality');
        break;
      case 'stable-audio-2.0':
        capabilities.push('high_quality_audio', 'music_composition');
        break;
      // Add more model-specific capabilities as needed
    }
    
    // Register capabilities
    this.modelCapabilities.set(model.id, capabilities);
  }
  
  /**
   * Get model capabilities
   * @param {string} modelId - Model ID
   * @returns {Array<string>} Capabilities
   */
  getModelCapabilities(modelId) {
    return this.modelCapabilities.get(modelId) || [];
  }
  
  /**
   * Get agent model preferences
   * @param {string} agentId - Agent ID
   * @returns {Object} Model preferences
   */
  getAgentModelPreferences(agentId) {
    return this.agentModelPreferences.get(agentId) || this._getDefaultPreferencesForRole('general');
  }
  
  /**
   * Set agent model preferences
   * @param {string} agentId - Agent ID
   * @param {Object} preferences - Model preferences
   */
  setAgentModelPreferences(agentId, preferences) {
    this.agentModelPreferences.set(agentId, preferences);
  }
  
  /**
   * Select model for an agent
   * @param {string} agentId - Agent ID
   * @param {string} modality - Model modality
   * @param {Object} taskRequirements - Task-specific requirements
   * @returns {Object} Selected model
   */
  selectModelForAgent(agentId, modality, taskRequirements = {}) {
    // Get agent preferences
    const agentPreferences = this.getAgentModelPreferences(agentId);
    
    // Get modality preferences
    const modalityPreferences = agentPreferences[modality] || {};
    
    // Merge requirements
    const requirements = {
      ...modalityPreferences.requirements,
      ...taskRequirements
    };
    
    // If preferred models are specified, try them first
    if (modalityPreferences.preferredModels && modalityPreferences.preferredModels.length > 0) {
      for (const modelId of modalityPreferences.preferredModels) {
        try {
          const model = this.modelFramework.getModel(modelId, modality);
          
          // Check if model meets requirements
          if (this._modelMeetsRequirements(model, requirements)) {
            return model;
          }
        } catch (error) {
          // Model not found or doesn't meet requirements, try next
          this.logger.debug(`Preferred model ${modelId} not available or doesn't meet requirements`);
        }
      }
    }
    
    // If no preferred model is available or meets requirements, select best model
    return this.modelFramework.selectModel(modality, requirements);
  }
  
  /**
   * Check if a model meets requirements
   * @param {Object} model - Model instance
   * @param {Object} requirements - Requirements
   * @returns {boolean} Whether the model meets requirements
   * @private
   */
  _modelMeetsRequirements(model, requirements) {
    // Check context window
    if (requirements.minContextWindow && model.contextWindow < requirements.minContextWindow) {
      return false;
    }
    
    // Check source preference
    if (requirements.sourcePreference === 'open-source' && !model.isOpenSource) {
      return false;
    }
    
    if (requirements.sourcePreference === 'proprietary' && model.isOpenSource) {
      return false;
    }
    
    // Check processing preference
    if (requirements.processingPreference === 'local' && !model.supportsLocalProcessing) {
      return false;
    }
    
    if (requirements.processingPreference === 'cloud' && !model.supportsCloudProcessing) {
      return false;
    }
    
    // Check required capabilities
    if (requirements.requiredCapabilities && requirements.requiredCapabilities.length > 0) {
      const modelCapabilities = this.getModelCapabilities(model.id);
      
      for (const capability of requirements.requiredCapabilities) {
        if (!modelCapabilities.includes(capability)) {
          return false;
        }
      }
    }
    
    return true;
  }
  
  /**
   * Execute model for an agent
   * @param {string} agentId - Agent ID
   * @param {string} modality - Model modality
   * @param {Object} params - Model parameters
   * @param {Object} options - Execution options
   * @returns {Promise<Object>} Model execution result
   */
  async executeModelForAgent(agentId, modality, params, options = {}) {
    try {
      // Get task requirements
      const taskRequirements = options.requirements || {};
      
      // Select model
      const model = this.selectModelForAgent(agentId, modality, taskRequirements);
      
      // Execute model
      return await this.modelFramework.execute(model.id, modality, params, options);
    } catch (error) {
      this.logger.error(`Failed to execute model for agent ${agentId}:`, error);
      
      // Try with fallback
      if (options.useFallback !== false) {
        this.logger.info(`Trying fallback for agent ${agentId}`);
        return await this.modelFramework.executeWithFallback(modality, params, options);
      }
      
      throw error;
    }
  }
  
  /**
   * Clean up resources
   * @returns {Promise<void>}
   */
  async shutdown() {
    if (!this.initialized) {
      return;
    }
    
    this.logger.info('Shutting down Agent-Model Integration...');
    
    // Unregister from agent manager
    this.agentManager.unregisterCapabilityProvider('model');
    
    // Remove event listeners
    this.agentManager.removeAllListeners('agent:created');
    this.agentManager.removeAllListeners('agent:destroyed');
    
    this.initialized = false;
    this.logger.info('Agent-Model Integration shut down successfully');
  }
}

module.exports = AgentModelIntegration;
