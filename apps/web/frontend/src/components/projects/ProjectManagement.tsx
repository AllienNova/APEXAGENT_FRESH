import React, { useState } from 'react';

/**
 * Project Management Component
 * 
 * This component implements the project management interface for Aideon AI Lite,
 * including project list, task management, and collaboration features.
 */
const ProjectManagement = () => {
  // State for projects
  const [projects, setProjects] = useState([
    {
      id: 1,
      title: 'Q2 Sales Analysis',
      description: 'Comprehensive analysis of Q2 sales data with visualizations and recommendations.',
      status: 'active',
      category: 'Data Analysis',
      createdBy: 'John Doe',
      createdOn: '2025-06-05',
      lastUpdated: '2 hours ago',
      tasks: [
        { id: 1, title: 'Data collection and cleaning', completed: true },
        { id: 2, title: 'Initial data analysis', completed: true },
        { id: 3, title: 'Create basic visualizations', completed: true },
        { id: 4, title: 'Generate advanced insights', completed: false },
        { id: 5, title: 'Prepare final report', completed: false },
        { id: 6, title: 'Present findings to stakeholders', completed: false }
      ],
      team: [
        { id: 1, name: 'John Doe', role: 'Owner' },
        { id: 2, name: 'Jane Smith', role: 'Editor' }
      ],
      files: [
        { id: 1, name: 'Q2_Sales_Data.xlsx', size: '2.4 MB', type: 'excel' },
        { id: 2, name: 'Q2_Sales_Analysis.pdf', size: '1.8 MB', type: 'pdf' },
        { id: 3, name: 'sales_analysis.py', size: '4.2 KB', type: 'python' }
      ],
      conversations: [
        { 
          id: 1, 
          sender: 'John Doe', 
          content: "I've completed the initial analysis. The Western region is showing strong growth, but we need to look into the Southern region's performance.",
          timestamp: '2 hours ago'
        },
        {
          id: 2,
          sender: 'Aideon AI',
          content: "I've analyzed the Southern region data and found that Product C is underperforming significantly. This appears to be the main factor in the region's low growth rate.",
          timestamp: '1 hour ago'
        }
      ]
    },
    {
      id: 2,
      title: 'Product Roadmap',
      description: 'Create a product roadmap for Q3 with feature prioritization.',
      status: 'planning',
      category: 'Product Management',
      createdBy: 'Jane Smith',
      createdOn: '2025-06-07',
      lastUpdated: '3 hours ago',
      tasks: [
        { id: 1, title: 'Gather stakeholder requirements', completed: false },
        { id: 2, title: 'Analyze market trends', completed: false },
        { id: 3, title: 'Draft initial roadmap', completed: false },
        { id: 4, title: 'Review with product team', completed: false },
        { id: 5, title: 'Finalize and publish roadmap', completed: false }
      ],
      team: [
        { id: 2, name: 'Jane Smith', role: 'Owner' },
        { id: 1, name: 'John Doe', role: 'Viewer' }
      ],
      files: [],
      conversations: []
    },
    {
      id: 3,
      title: 'Mobile Application',
      description: 'Develop a mobile application for iOS and Android platforms.',
      status: 'on-hold',
      category: 'Development',
      createdBy: 'John Doe',
      createdOn: '2025-05-20',
      lastUpdated: '1 week ago',
      tasks: [
        { id: 1, title: 'Create wireframes', completed: true },
        { id: 2, title: 'Design UI/UX', completed: true },
        { id: 3, title: 'Develop frontend', completed: false },
        { id: 4, title: 'Implement backend integration', completed: false },
        { id: 5, title: 'Testing and QA', completed: false },
        { id: 6, title: 'Deploy to app stores', completed: false }
      ],
      team: [
        { id: 1, name: 'John Doe', role: 'Owner' },
        { id: 3, name: 'Alex Johnson', role: 'Editor' }
      ],
      files: [],
      conversations: []
    }
  ]);
  
  // State for selected project
  const [selectedProject, setSelectedProject] = useState(null);
  
  // State for new task input
  const [newTaskTitle, setNewTaskTitle] = useState('');
  
  // Handle project selection
  const handleProjectSelect = (project) => {
    setSelectedProject(project);
  };
  
  // Handle task completion toggle
  const handleTaskToggle = (taskId) => {
    if (!selectedProject) return;
    
    const updatedTasks = selectedProject.tasks.map(task => 
      task.id === taskId ? { ...task, completed: !task.completed } : task
    );
    
    const updatedProject = { ...selectedProject, tasks: updatedTasks };
    
    setSelectedProject(updatedProject);
    
    // Update the project in the projects list
    const updatedProjects = projects.map(project => 
      project.id === selectedProject.id ? updatedProject : project
    );
    
    setProjects(updatedProjects);
  };
  
  // Handle new task addition
  const handleAddTask = () => {
    if (!selectedProject || !newTaskTitle.trim()) return;
    
    const newTask = {
      id: Math.max(0, ...selectedProject.tasks.map(t => t.id)) + 1,
      title: newTaskTitle,
      completed: false
    };
    
    const updatedTasks = [...selectedProject.tasks, newTask];
    const updatedProject = { ...selectedProject, tasks: updatedTasks };
    
    setSelectedProject(updatedProject);
    
    // Update the project in the projects list
    const updatedProjects = projects.map(project => 
      project.id === selectedProject.id ? updatedProject : project
    );
    
    setProjects(updatedProjects);
    setNewTaskTitle('');
  };
  
  // Handle project close
  const handleCloseProject = () => {
    setSelectedProject(null);
  };
  
  // Get status badge color
  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'planning':
        return 'bg-blue-100 text-blue-800';
      case 'on-hold':
        return 'bg-red-100 text-red-800';
      case 'completed':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };
  
  // Get file icon
  const getFileIcon = (type) => {
    switch (type) {
      case 'excel':
        return 'fa-file-excel';
      case 'pdf':
        return 'fa-file-pdf';
      case 'python':
        return 'fa-file-code';
      default:
        return 'fa-file';
    }
  };
  
  return (
    <div className="h-full">
      {selectedProject ? (
        // Project detail view
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">{selectedProject.title}</h2>
              <div className="flex space-x-2">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(selectedProject.status)}`}>
                  {selectedProject.status.charAt(0).toUpperCase() + selectedProject.status.slice(1)}
                </span>
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 p-6">
            <div className="md:col-span-2 space-y-6">
              {/* Description */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Description</h3>
                <p className="text-gray-700">{selectedProject.description}</p>
              </div>
              
              {/* Tasks */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Tasks</h3>
                <div className="space-y-2">
                  {selectedProject.tasks.map((task) => (
                    <div key={task.id} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={task.completed}
                        onChange={() => handleTaskToggle(task.id)}
                        className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                      />
                      <span 
                        className={`ml-2 text-gray-700 ${task.completed ? 'line-through text-gray-400' : ''}`}
                      >
                        {task.title}
                      </span>
                    </div>
                  ))}
                  
                  {/* Add new task */}
                  <div className="flex items-center mt-4">
                    <input
                      type="text"
                      value={newTaskTitle}
                      onChange={(e) => setNewTaskTitle(e.target.value)}
                      placeholder="Add a new task..."
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    />
                    <button
                      onClick={handleAddTask}
                      className="ml-2 px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                      Add Task
                    </button>
                  </div>
                </div>
              </div>
              
              {/* Conversations */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Conversations</h3>
                <div className="space-y-4">
                  {selectedProject.conversations.map((conversation) => (
                    <div key={conversation.id} className="bg-gray-50 p-4 rounded-lg">
                      <div className="flex items-center mb-2">
                        <div className="flex-shrink-0 h-8 w-8 rounded-full bg-gray-300 flex items-center justify-center">
                          {conversation.sender === 'Aideon AI' ? (
                            <i className="fas fa-robot text-gray-600"></i>
                          ) : (
                            <i className="fas fa-user text-gray-600"></i>
                          )}
                        </div>
                        <div className="ml-3">
                          <p className="text-sm font-medium text-gray-900">{conversation.sender}</p>
                          <p className="text-xs text-gray-500">{conversation.timestamp}</p>
                        </div>
                      </div>
                      <p className="text-gray-700">{conversation.content}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="space-y-6">
              {/* Project Details */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-md font-medium text-gray-900 mb-2">Project Details</h3>
                <div className="space-y-2">
                  <div>
                    <p className="text-xs text-gray-500">Created by</p>
                    <p className="text-sm text-gray-700">{selectedProject.createdBy}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Created on</p>
                    <p className="text-sm text-gray-700">{selectedProject.createdOn}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Last updated</p>
                    <p className="text-sm text-gray-700">{selectedProject.lastUpdated}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Category</p>
                    <p className="text-sm text-gray-700">{selectedProject.category}</p>
                  </div>
                </div>
              </div>
              
              {/* Team Members */}
              <div>
                <h3 className="text-md font-medium text-gray-900 mb-2">Team Members</h3>
                <div className="space-y-2">
                  {selectedProject.team.map((member) => (
                    <div key={member.id} className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-8 w-8 rounded-full bg-gray-300 flex items-center justify-center">
                          <i className="fas fa-user text-gray-600"></i>
                        </div>
                        <p className="ml-2 text-sm text-gray-700">{member.name}</p>
                      </div>
                      <span className="text-xs text-gray-500">{member.role}</span>
                    </div>
                  ))}
                  <button className="mt-2 flex items-center text-sm text-indigo-600 hover:text-indigo-800">
                    <i className="fas fa-plus mr-1"></i> Add Member
                  </button>
                </div>
              </div>
              
              {/* Files */}
              <div>
                <h3 className="text-md font-medium text-gray-900 mb-2">Files</h3>
                <div className="space-y-2">
                  {selectedProject.files.map((file) => (
                    <div key={file.id} className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-8 w-8 rounded-full bg-gray-100 flex items-center justify-center">
                          <i className={`fas ${getFileIcon(file.type)} text-gray-600`}></i>
                        </div>
                        <p className="ml-2 text-sm text-gray-700">{file.name}</p>
                      </div>
                      <span className="text-xs text-gray-500">{file.size}</span>
                    </div>
                  ))}
                  <button className="mt-2 flex items-center text-sm text-indigo-600 hover:text-indigo-800">
                    <i className="fas fa-upload mr-1"></i> Upload File
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <div className="px-6 py-4 border-t border-gray-200 flex justify-end space-x-3">
            <button
              onClick={handleCloseProject}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Close
            </button>
            <button
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Save Changes
            </button>
          </div>
        </div>
      ) : (
        // Project list view
        <div>
          <div className="mb-6 flex justify-between items-center">
            <h2 className="text-2xl font-bold text-gray-900">Projects</h2>
            <button className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
              <i className="fas fa-plus mr-2"></i> New Project
            </button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <div 
                key={project.id} 
                className="bg-white rounded-lg shadow-sm overflow-hidden hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => handleProjectSelect(project)}
              >
                <div className="px-4 py-5 sm:p-6">
                  <div className="flex justify-between items-start">
                    <h3 className="text-lg font-medium text-gray-900 mb-2">{project.title}</h3>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(project.status)}`}>
                      {project.status.charAt(0).toUpperCase() + project.status.slice(1)}
                    </span>
                  </div>
                  <p className="text-sm text-gray-500 mb-4">{project.description}</p>
                  
                  <div className="flex justify-between items-center text-xs text-gray-500">
                    <span>Updated {project.lastUpdated}</span>
                    <div className="flex items-center">
                      <i className="fas fa-tasks mr-1"></i>
                      <span>{project.tasks.filter(t => t.completed).length}/{project.tasks.length} tasks</span>
                    </div>
                  </div>
                </div>
                <div className="bg-gray-50 px-4 py-4 sm:px-6 flex justify-between items-center">
                  <div className="flex -space-x-2">
                    {project.team.slice(0, 3).map((member) => (
                      <div key={member.id} className="h-6 w-6 rounded-full bg-gray-300 flex items-center justify-center border-2 border-white">
                        <i className="fas fa-user text-xs text-gray-600"></i>
                      </div>
                    ))}
                    {project.team.length > 3 && (
                      <div className="h-6 w-6 rounded-full bg-gray-100 flex items-center justify-center border-2 border-white">
                        <span className="text-xs text-gray-600">+{project.team.length - 3}</span>
                      </div>
                    )}
                  </div>
                  <div className="flex space-x-2">
                    <button className="text-gray-400 hover:text-gray-500">
                      <i className="far fa-star"></i>
                    </button>
                    <button className="text-gray-400 hover:text-gray-500">
                      <i className="fas fa-ellipsis-v"></i>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ProjectManagement;
