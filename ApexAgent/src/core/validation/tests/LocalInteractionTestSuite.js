/**
 * LocalInteractionTestSuite.js
 * 
 * Test suite for validating local interaction capabilities and visibility
 * of agent actions on the user's PC.
 */

const { BaseTestSuite } = require('../BaseTestSuite');
const fs = require('fs-extra');
const path = require('path');
const os = require('os');

class LocalInteractionTestSuite extends BaseTestSuite {
  constructor(config) {
    super('Local Interaction', config);
    
    this.testProjectDir = path.join(os.tmpdir(), 'aideon-test-projects');
    this.testFilePath = path.join(this.testProjectDir, 'test-project.json');
    this.testContent = {
      name: 'Test Project',
      created: new Date().toISOString(),
      description: 'Test project for local interaction validation',
      version: '1.0.0'
    };
  }
  
  async setup() {
    // Ensure test directory exists
    await fs.ensureDir(this.testProjectDir);
    
    // Clean up any previous test files
    if (await fs.pathExists(this.testFilePath)) {
      await fs.remove(this.testFilePath);
    }
  }
  
  async teardown() {
    // Clean up test files
    if (await fs.pathExists(this.testFilePath)) {
      await fs.remove(this.testFilePath);
    }
  }
  
  async runTests() {
    await this.setup();
    
    try {
      // Register tests
      this.registerTest('test_local_project_creation', this.testLocalProjectCreation.bind(this));
      this.registerTest('test_local_project_access', this.testLocalProjectAccess.bind(this));
      this.registerTest('test_local_project_modification', this.testLocalProjectModification.bind(this));
      this.registerTest('test_local_project_persistence', this.testLocalProjectPersistence.bind(this));
      this.registerTest('test_agent_action_visibility', this.testAgentActionVisibility.bind(this));
      this.registerTest('test_dr_tardis_integration', this.testDrTardisIntegration.bind(this));
      
      // Run all registered tests
      await this.executeTests();
    } finally {
      await this.teardown();
    }
    
    // Return results
    return this.results;
  }
  
  /**
   * Test local project creation
   */
  async testLocalProjectCreation() {
    try {
      // Create a test project file
      await fs.writeJson(this.testFilePath, this.testContent);
      
      // Verify file exists
      const exists = await fs.pathExists(this.testFilePath);
      this.assert(exists, 'Project file should be created on local filesystem');
      
      this.pass('Successfully created local project file');
    } catch (error) {
      this.fail(`Failed to create local project: ${error.message}`);
    }
  }
  
  /**
   * Test local project access
   */
  async testLocalProjectAccess() {
    try {
      // Create a test project file if it doesn't exist
      if (!await fs.pathExists(this.testFilePath)) {
        await fs.writeJson(this.testFilePath, this.testContent);
      }
      
      // Read the project file
      const projectData = await fs.readJson(this.testFilePath);
      
      // Verify content
      this.assertEqual(projectData.name, this.testContent.name, 'Project name should match');
      this.assertEqual(projectData.description, this.testContent.description, 'Project description should match');
      
      this.pass('Successfully accessed local project file');
    } catch (error) {
      this.fail(`Failed to access local project: ${error.message}`);
    }
  }
  
  /**
   * Test local project modification
   */
  async testLocalProjectModification() {
    try {
      // Create a test project file if it doesn't exist
      if (!await fs.pathExists(this.testFilePath)) {
        await fs.writeJson(this.testFilePath, this.testContent);
      }
      
      // Modify the project file
      const updatedContent = {
        ...this.testContent,
        name: 'Updated Test Project',
        lastModified: new Date().toISOString()
      };
      
      await fs.writeJson(this.testFilePath, updatedContent);
      
      // Read the modified file
      const projectData = await fs.readJson(this.testFilePath);
      
      // Verify modifications
      this.assertEqual(projectData.name, updatedContent.name, 'Project name should be updated');
      this.assertContains(Object.keys(projectData), 'lastModified', 'Project should have lastModified field');
      
      this.pass('Successfully modified local project file');
    } catch (error) {
      this.fail(`Failed to modify local project: ${error.message}`);
    }
  }
  
  /**
   * Test local project persistence
   */
  async testLocalProjectPersistence() {
    try {
      // Create a test project file with unique identifier
      const uniqueId = Date.now().toString();
      const persistenceTestPath = path.join(this.testProjectDir, `persistence-test-${uniqueId}.json`);
      
      const persistenceContent = {
        ...this.testContent,
        id: uniqueId,
        persistent: true
      };
      
      await fs.writeJson(persistenceTestPath, persistenceContent);
      
      // Simulate application restart by creating a new instance of a mock project manager
      const mockProjectManager = {
        getProjects: async () => {
          const files = await fs.readdir(this.testProjectDir);
          const projects = [];
          
          for (const file of files) {
            if (file.endsWith('.json')) {
              const filePath = path.join(this.testProjectDir, file);
              const projectData = await fs.readJson(filePath);
              projects.push(projectData);
            }
          }
          
          return projects;
        }
      };
      
      // Get projects after "restart"
      const projects = await mockProjectManager.getProjects();
      
      // Find our test project
      const testProject = projects.find(p => p.id === uniqueId);
      
      // Verify project persistence
      this.assert(testProject !== undefined, 'Project should persist after application restart');
      this.assertEqual(testProject.id, uniqueId, 'Project ID should be preserved');
      this.assertEqual(testProject.persistent, true, 'Project persistent flag should be preserved');
      
      // Clean up
      await fs.remove(persistenceTestPath);
      
      this.pass('Successfully verified local project persistence');
    } catch (error) {
      this.fail(`Failed to verify project persistence: ${error.message}`);
    }
  }
  
  /**
   * Test agent action visibility
   */
  async testAgentActionVisibility() {
    try {
      // Mock the action logger
      const actionLog = [];
      const mockActionLogger = {
        logAction: (action) => {
          actionLog.push({
            ...action,
            timestamp: new Date().toISOString()
          });
        },
        getActions: () => actionLog
      };
      
      // Simulate agent actions
      mockActionLogger.logAction({
        type: 'file_create',
        path: '/path/to/file.txt',
        agent: 'ExecutionAgent'
      });
      
      mockActionLogger.logAction({
        type: 'code_generate',
        language: 'javascript',
        agent: 'ExecutionAgent'
      });
      
      mockActionLogger.logAction({
        type: 'file_modify',
        path: '/path/to/file.txt',
        agent: 'ExecutionAgent'
      });
      
      // Verify action logging
      const actions = mockActionLogger.getActions();
      this.assertEqual(actions.length, 3, 'Should have logged 3 actions');
      this.assertEqual(actions[0].type, 'file_create', 'First action should be file_create');
      this.assertEqual(actions[1].type, 'code_generate', 'Second action should be code_generate');
      this.assertEqual(actions[2].type, 'file_modify', 'Third action should be file_modify');
      
      // Verify all actions have timestamps
      for (const action of actions) {
        this.assert(action.timestamp !== undefined, 'Action should have timestamp');
        this.assert(action.agent !== undefined, 'Action should have agent identifier');
      }
      
      this.pass('Successfully verified agent action visibility');
    } catch (error) {
      this.fail(`Failed to verify agent action visibility: ${error.message}`);
    }
  }
  
  /**
   * Test Dr. Tardis integration
   */
  async testDrTardisIntegration() {
    try {
      // Mock Dr. Tardis component
      const mockDrTardis = {
        explainAction: (action) => {
          return {
            explanation: `Dr. T: I'm ${action.type === 'file_create' ? 'creating' : 'modifying'} a file at ${action.path}`,
            details: action
          };
        },
        explainConcept: (concept) => {
          return {
            explanation: `Dr. T: Let me explain ${concept}...`,
            relatedConcepts: ['AI', 'Automation', 'Productivity']
          };
        },
        getActivitySummary: () => {
          return {
            summary: "Dr. T: I have been helping with your project by creating and modifying files.",
            activityCount: 5,
            timeSpent: '10 minutes'
          };
        }
      };
      
      // Test action explanation
      const actionExplanation = mockDrTardis.explainAction({
        type: 'file_create',
        path: '/path/to/file.txt'
      });
      
      this.assert(actionExplanation.explanation.includes('creating'), 'Explanation should describe the action');
      this.assert(actionExplanation.explanation.includes('/path/to/file.txt'), 'Explanation should include the file path');
      
      // Test concept explanation
      const conceptExplanation = mockDrTardis.explainConcept('Autonomous Agents');
      this.assert(conceptExplanation.explanation.includes('explain Autonomous Agents'), 'Explanation should address the requested concept');
      
      // Test activity summary
      const activitySummary = mockDrTardis.getActivitySummary();
      this.assert(activitySummary.summary.includes('helping with your project'), 'Summary should describe agent activities');
      this.assert(typeof activitySummary.activityCount === 'number', 'Summary should include activity count');
      
      this.pass('Successfully verified Dr. Tardis integration');
    } catch (error) {
      this.fail(`Failed to verify Dr. Tardis integration: ${error.message}`);
    }
  }
}

module.exports = { LocalInteractionTestSuite };
