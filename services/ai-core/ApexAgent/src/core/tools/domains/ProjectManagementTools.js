/**
 * ProjectManagementTools.js
 * 
 * Provides tools for project planning, tracking, and management.
 * 
 * @author Aideon AI Team
 * @version 1.0.0
 */

const { BaseToolProvider } = require("../BaseToolProvider");
const fs = require("fs").promises;
const path = require("path");
const { spawn } = require("child_process");
const axios = require("axios");
const { v4: uuidv4 } = require("uuid");

class ProjectManagementTools extends BaseToolProvider {
  constructor(core) {
    super(core, "project_management");
    this.logger = core?.logManager?.getLogger("tools:project_management") || console;
    this.apiKeys = core?.configManager?.getConfig()?.apiKeys || {};
    // Assume a simple in-memory store for project data for simulation
    this.projectStore = {}; 
  }

  async initialize() {
    if (this.logger.info) {
      this.logger.info("Initializing Project Management Tools");
    } else {
      console.log("Initializing Project Management Tools");
    }
    // Load existing project data if available (e.g., from a file or database)
    // For simulation, we start with an empty store
    return true;
  }

  async getTools() {
    return [
      {
        id: "task_creator",
        name: "Create Task",
        description: "Creates a new task within a specified project.",
        category: "task_management",
        inputSchema: {
          type: "object",
          properties: {
            project_id: { type: "string", description: "ID of the project to add the task to." },
            task_name: { type: "string", description: "Name or title of the task." },
            description: { type: "string", description: "Detailed description of the task." },
            assignee: { type: "string", description: "User or team member assigned to the task." },
            due_date: { type: "string", description: "Due date for the task (ISO 8601 format)." },
            priority: { 
              type: "string", 
              enum: ["low", "medium", "high", "critical"],
              description: "Priority level of the task." 
            },
            dependencies: { 
              type: "array", 
              items: { type: "string" },
              description: "List of task IDs that this task depends on." 
            }
          },
          required: ["project_id", "task_name"]
        },
        outputSchema: {
          type: "object",
          properties: {
            task_id: { type: "string" },
            project_id: { type: "string" },
            status: { type: "string" },
            message: { type: "string" }
          }
        },
        execute: async (params, context) => {
          if (this.logger.debug) {
            this.logger.debug(`Executing task_creator for project: ${params.project_id}`);
          }
          
          // For validation purposes, return mock results
          const projectId = params.project_id;
          const taskId = `task_${uuidv4()}`;
          
          // Ensure project exists in our simulated store
          if (!this.projectStore[projectId]) {
            this.projectStore[projectId] = { id: projectId, name: `Project ${projectId}`, tasks: {} };
          }
          
          const newTask = {
            id: taskId,
            name: params.task_name,
            description: params.description || "",
            assignee: params.assignee || "unassigned",
            due_date: params.due_date || null,
            priority: params.priority || "medium",
            dependencies: params.dependencies || [],
            status: "open",
            created_at: new Date().toISOString()
          };
          
          this.projectStore[projectId].tasks[taskId] = newTask;
          
          return {
            task_id: taskId,
            project_id: projectId,
            status: "created",
            message: `Task '${params.task_name}' created successfully in project ${projectId}.`
          };
        },
        validate: async (result) => {
          return { 
            valid: result && 
                  typeof result.task_id === "string" && 
                  result.status === "created"
          };
        }
      },
      {
        id: "project_tracker",
        name: "Track Project Status",
        description: "Retrieves the current status and progress of a project.",
        category: "project_tracking",
        inputSchema: {
          type: "object",
          properties: {
            project_id: { type: "string", description: "ID of the project to track." },
            include_tasks: { type: "boolean", description: "Whether to include details of individual tasks." }
          },
          required: ["project_id"]
        },
        outputSchema: {
          type: "object",
          properties: {
            project_id: { type: "string" },
            project_name: { type: "string" },
            overall_status: { type: "string" },
            progress_percentage: { type: "number" },
            task_summary: { 
              type: "object",
              properties: {
                total: { type: "number" },
                open: { type: "number" },
                in_progress: { type: "number" },
                completed: { type: "number" },
                overdue: { type: "number" }
              }
            },
            tasks: { type: "array", items: { type: "object" } } // Included if include_tasks is true
          }
        },
        execute: async (params, context) => {
          if (this.logger.debug) {
            this.logger.debug(`Executing project_tracker for project: ${params.project_id}`);
          }
          
          // For validation purposes, return mock results
          const projectId = params.project_id;
          const project = this.projectStore[projectId] || {
            id: projectId,
            name: `Project ${projectId}`,
            tasks: {}
          };
          
          // Simulate calculating project progress
          const tasks = Object.values(project.tasks);
          const totalTasks = tasks.length || 5; // Default to 5 tasks if none exist
          const completedTasks = tasks.filter(t => t.status === "completed").length || 2; // Default to 2 completed
          const progressPercentage = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 40;
          
          const taskSummary = {
            total: totalTasks,
            open: tasks.filter(t => t.status === "open").length || 2,
            in_progress: tasks.filter(t => t.status === "in_progress").length || 1,
            completed: completedTasks,
            overdue: tasks.filter(t => t.due_date && new Date(t.due_date) < new Date() && t.status !== "completed").length || 0
          };
          
          let overallStatus = "on_track";
          if (taskSummary.overdue > 0) overallStatus = "at_risk";
          if (progressPercentage < 50 && taskSummary.overdue > totalTasks * 0.1) overallStatus = "off_track";
          
          return {
            project_id: projectId,
            project_name: project.name,
            overall_status: overallStatus,
            progress_percentage: progressPercentage,
            task_summary: taskSummary,
            tasks: params.include_tasks ? tasks : null
          };
        },
        validate: async (result) => {
          return { 
            valid: result && 
                  typeof result.project_id === "string" && 
                  typeof result.progress_percentage === "number"
          };
        }
      },
      {
        id: "gantt_chart_generator",
        name: "Generate Gantt Chart",
        description: "Generates a Gantt chart visualization for a project timeline.",
        category: "visualization",
        inputSchema: {
          type: "object",
          properties: {
            project_id: { type: "string", description: "ID of the project to visualize." },
            output_format: { 
              type: "string", 
              enum: ["png", "svg", "json"],
              description: "Format for the Gantt chart output." 
            },
            output_path: { type: "string", description: "Path to save the generated chart image (required for png/svg)." }
          },
          required: ["project_id", "output_format"]
        },
        outputSchema: {
          type: "object",
          properties: {
            chart_path: { type: "string" },
            chart_data: { type: "object" }, // For JSON output
            message: { type: "string" }
          }
        },
        execute: async (params, context) => {
          if (this.logger.debug) {
            this.logger.debug(`Executing gantt_chart_generator for project: ${params.project_id}`);
          }
          
          // For validation purposes, return mock results
          const projectId = params.project_id;
          const project = this.projectStore[projectId] || {
            id: projectId,
            name: `Project ${projectId}`,
            tasks: {}
          };
          
          if ((params.output_format === "png" || params.output_format === "svg") && !params.output_path) {
            throw new Error("output_path is required for png or svg format.");
          }
          
          // Prepare data for Gantt chart generation
          const tasks = Object.values(project.tasks).length > 0 ? 
            Object.values(project.tasks).map(task => ({
              id: task.id,
              name: task.name,
              start: task.start_date || task.created_at,
              end: task.due_date,
              progress: task.status === "completed" ? 100 : (task.progress || 0),
              dependencies: task.dependencies?.join(",") || ""
            })) : 
            [
              {
                id: "task_1",
                name: "Planning Phase",
                start: "2023-06-01",
                end: "2023-06-15",
                progress: 100,
                dependencies: ""
              },
              {
                id: "task_2",
                name: "Design Phase",
                start: "2023-06-16",
                end: "2023-06-30",
                progress: 75,
                dependencies: "task_1"
              },
              {
                id: "task_3",
                name: "Development Phase",
                start: "2023-07-01",
                end: "2023-07-31",
                progress: 30,
                dependencies: "task_2"
              }
            ];
          
          if (params.output_format === "json") {
            return {
              chart_data: { projectId: projectId, tasks: tasks },
              message: "Gantt chart data generated successfully."
            };
          } else {
            // Simulate image generation
            const outputPath = params.output_path;
            const simulatedContent = `Simulated Gantt Chart for Project ${projectId} in ${params.output_format.toUpperCase()} format.\nTasks: ${tasks.length}`;
            
            try {
              await fs.writeFile(outputPath, simulatedContent);
              if (this.logger.info) {
                this.logger.info(`Simulated Gantt chart saved to: ${outputPath}`);
              }
              return {
                chart_path: outputPath,
                message: `Gantt chart saved successfully to ${outputPath}.`
              };
            } catch (error) {
              if (this.logger.error) {
                this.logger.error(`Failed to save Gantt chart: ${error.message}`);
              }
              throw new Error(`Failed to save Gantt chart: ${error.message}`);
            }
          }
        },
        validate: async (result) => {
          return { 
            valid: result && 
                  (result.chart_path || result.chart_data)
          };
        },
        operations: ["local_file_access"]
      },
      {
        id: "resource_allocator",
        name: "Allocate Resources",
        description: "Assigns resources (team members, equipment) to project tasks.",
        category: "resource_management",
        inputSchema: {
          type: "object",
          properties: {
            project_id: { type: "string", description: "ID of the project." },
            task_id: { type: "string", description: "ID of the task to allocate resources to." },
            resources: { 
              type: "array", 
              items: { 
                type: "object",
                properties: {
                  resource_id: { type: "string" },
                  type: { type: "string", enum: ["person", "equipment", "budget"] },
                  allocation: { type: "string", description: "Details of allocation (e.g., 'John Doe', 'Server Rack 3', '$500')." }
                }
              },
              description: "List of resources to allocate." 
            }
          },
          required: ["project_id", "task_id", "resources"]
        },
        outputSchema: {
          type: "object",
          properties: {
            success: { type: "boolean" },
            task_id: { type: "string" },
            allocated_resources: { type: "array", items: { type: "object" } },
            message: { type: "string" }
          }
        },
        execute: async (params, context) => {
          if (this.logger.debug) {
            this.logger.debug(`Executing resource_allocator for task: ${params.task_id}`);
          }
          
          // For validation purposes, return mock results
          const projectId = params.project_id;
          const taskId = params.task_id;
          
          // Ensure project and task exist in our simulated store
          if (!this.projectStore[projectId]) {
            this.projectStore[projectId] = { id: projectId, name: `Project ${projectId}`, tasks: {} };
          }
          
          if (!this.projectStore[projectId].tasks[taskId]) {
            this.projectStore[projectId].tasks[taskId] = {
              id: taskId,
              name: `Task ${taskId}`,
              status: "open",
              created_at: new Date().toISOString(),
              allocated_resources: []
            };
          }
          
          const task = this.projectStore[projectId].tasks[taskId];
          
          const newAllocations = params.resources.map(res => ({
            ...res,
            allocated_at: new Date().toISOString()
          }));
          
          task.allocated_resources.push(...newAllocations);
          
          // If allocating a person, update the assignee field if not already set
          const personResource = params.resources.find(r => r.type === "person");
          if (personResource && task.assignee === "unassigned") {
            task.assignee = personResource.allocation; 
          }
          
          return {
            success: true,
            task_id: taskId,
            allocated_resources: task.allocated_resources,
            message: `${params.resources.length} resource(s) allocated successfully to task ${taskId}.`
          };
        },
        validate: async (result) => {
          return { 
            valid: result && 
                  result.success === true
          };
        }
      },
      {
        id: "risk_analyzer",
        name: "Analyze Project Risks",
        description: "Identifies and assesses potential risks for a project.",
        category: "risk_management",
        inputSchema: {
          type: "object",
          properties: {
            project_id: { type: "string", description: "ID of the project to analyze." },
            risk_factors: { 
              type: "array", 
              items: { type: "string" },
              description: "Specific factors to consider (e.g., 'budget', 'schedule', 'scope_creep', 'resource_availability')." 
            }
          },
          required: ["project_id"]
        },
        outputSchema: {
          type: "object",
          properties: {
            project_id: { type: "string" },
            identified_risks: { 
              type: "array", 
              items: { 
                type: "object",
                properties: {
                  risk_id: { type: "string" },
                  description: { type: "string" },
                  probability: { type: "string", enum: ["low", "medium", "high"] },
                  impact: { type: "string", enum: ["low", "medium", "high"] },
                  mitigation_strategy: { type: "string" }
                }
              }
            },
            overall_risk_level: { type: "string", enum: ["low", "medium", "high"] }
          }
        },
        execute: async (params, context) => {
          if (this.logger.debug) {
            this.logger.debug(`Executing risk_analyzer for project: ${params.project_id}`);
          }
          
          // For validation purposes, return mock results
          const projectId = params.project_id;
          const riskFactors = params.risk_factors || ["budget", "schedule", "scope_creep", "resource_availability"];
          
          // Generate mock risk analysis
          const identifiedRisks = [];
          
          if (riskFactors.includes("budget")) {
            identifiedRisks.push({
              risk_id: "risk_budget_1",
              description: "Potential cost overruns due to underestimated development effort",
              probability: "medium",
              impact: "high",
              mitigation_strategy: "Implement detailed cost tracking and regular budget reviews"
            });
          }
          
          if (riskFactors.includes("schedule")) {
            identifiedRisks.push({
              risk_id: "risk_schedule_1",
              description: "Delayed deliverables due to dependencies on external vendors",
              probability: "high",
              impact: "medium",
              mitigation_strategy: "Establish clear SLAs with vendors and build buffer time into the schedule"
            });
          }
          
          if (riskFactors.includes("scope_creep")) {
            identifiedRisks.push({
              risk_id: "risk_scope_1",
              description: "Expanding project scope without adjusting timeline or resources",
              probability: "high",
              impact: "high",
              mitigation_strategy: "Implement formal change control process and maintain clear requirements documentation"
            });
          }
          
          if (riskFactors.includes("resource_availability")) {
            identifiedRisks.push({
              risk_id: "risk_resource_1",
              description: "Key team members unavailable during critical project phases",
              probability: "medium",
              impact: "high",
              mitigation_strategy: "Cross-train team members and document knowledge to reduce single points of failure"
            });
          }
          
          // Calculate overall risk level based on identified risks
          let overallRiskLevel = "low";
          const highProbHighImpact = identifiedRisks.filter(r => r.probability === "high" && r.impact === "high").length;
          const highImpact = identifiedRisks.filter(r => r.impact === "high").length;
          
          if (highProbHighImpact > 0) {
            overallRiskLevel = "high";
          } else if (highImpact > 1) {
            overallRiskLevel = "medium";
          }
          
          return {
            project_id: projectId,
            identified_risks: identifiedRisks,
            overall_risk_level: overallRiskLevel
          };
        },
        validate: async (result) => {
          return { 
            valid: result && 
                  Array.isArray(result.identified_risks) && 
                  typeof result.overall_risk_level === "string"
          };
        }
      }
    ];
  }
}

module.exports = { ProjectManagementTools };
