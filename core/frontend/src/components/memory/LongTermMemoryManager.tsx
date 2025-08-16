import React, { useState, useEffect } from 'react';

/**
 * Long-Term Memory Architecture Component
 * 
 * This component implements the core architecture for Aideon AI Lite's long-term memory system,
 * designed to maintain context and knowledge across very large or long-running projects
 * spanning months or even years.
 */
const LongTermMemoryManager = () => {
  // State for memory statistics
  const [memoryStats, setMemoryStats] = useState({
    totalProjects: 24,
    totalMemorySize: '1.2 TB',
    oldestProject: '18 months',
    averageContextSize: '450 MB',
    activeContexts: 8,
    indexedEntities: '1.2M',
    retrievalAccuracy: '98.7%'
  });
  
  // State for memory architecture visualization
  const [architectureView, setArchitectureView] = useState('logical');
  
  // State for sample projects with long-term memory
  const [sampleProjects, setSampleProjects] = useState([
    {
      id: 1,
      name: 'Enterprise Data Migration',
      duration: '14 months',
      memorySize: '320 GB',
      contextSegments: 42,
      lastAccessed: '2 hours ago',
      status: 'active'
    },
    {
      id: 2,
      name: 'Pharmaceutical Research Analysis',
      duration: '26 months',
      memorySize: '540 GB',
      contextSegments: 78,
      lastAccessed: '3 days ago',
      status: 'active'
    },
    {
      id: 3,
      name: 'Global Supply Chain Optimization',
      duration: '8 months',
      memorySize: '180 GB',
      contextSegments: 35,
      lastAccessed: '1 week ago',
      status: 'paused'
    }
  ]);
  
  // State for memory layers
  const [memoryLayers, setMemoryLayers] = useState([
    {
      id: 'episodic',
      name: 'Episodic Memory',
      description: 'Stores specific events, conversations, and interactions chronologically',
      retention: 'Indefinite with hierarchical compression',
      accessSpeed: 'Variable (recent: <50ms, archived: <500ms)',
      size: '850 GB'
    },
    {
      id: 'semantic',
      name: 'Semantic Memory',
      description: 'Stores facts, concepts, and knowledge extracted from interactions',
      retention: 'Indefinite with relevance-based pruning',
      accessSpeed: '<100ms for all entries',
      size: '220 GB'
    },
    {
      id: 'procedural',
      name: 'Procedural Memory',
      description: 'Stores methods, workflows, and processes learned during project execution',
      retention: 'Indefinite with version control',
      accessSpeed: '<80ms for all entries',
      size: '130 GB'
    }
  ]);
  
  // State for active memory operations
  const [activeOperations, setActiveOperations] = useState([
    {
      id: 1,
      type: 'consolidation',
      project: 'Enterprise Data Migration',
      status: 'in-progress',
      progress: 68,
      startTime: '10 minutes ago'
    },
    {
      id: 2,
      type: 'indexing',
      project: 'Pharmaceutical Research Analysis',
      status: 'queued',
      progress: 0,
      startTime: 'Pending'
    }
  ]);
  
  // Handle architecture view change
  const handleViewChange = (view) => {
    setArchitectureView(view);
  };
  
  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'paused':
        return 'bg-yellow-100 text-yellow-800';
      case 'archived':
        return 'bg-gray-100 text-gray-800';
      case 'in-progress':
        return 'bg-blue-100 text-blue-800';
      case 'queued':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };
  
  return (
    <div className="h-full">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Long-Term Memory Architecture</h2>
        <p className="text-gray-500">Enterprise-grade memory system for projects spanning months or years</p>
      </div>
      
      {/* Memory Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-lg shadow-sm p-4">
          <p className="text-sm text-gray-500 mb-1">Total Projects</p>
          <p className="text-2xl font-semibold text-gray-900">{memoryStats.totalProjects}</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-4">
          <p className="text-sm text-gray-500 mb-1">Total Memory Size</p>
          <p className="text-2xl font-semibold text-gray-900">{memoryStats.totalMemorySize}</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-4">
          <p className="text-sm text-gray-500 mb-1">Oldest Project</p>
          <p className="text-2xl font-semibold text-gray-900">{memoryStats.oldestProject}</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-4">
          <p className="text-sm text-gray-500 mb-1">Retrieval Accuracy</p>
          <p className="text-2xl font-semibold text-gray-900">{memoryStats.retrievalAccuracy}</p>
        </div>
      </div>
      
      {/* Architecture Visualization */}
      <div className="bg-white rounded-lg shadow-sm overflow-hidden mb-8">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-medium text-gray-900">Memory Architecture</h3>
            <div className="flex space-x-2">
              <button
                onClick={() => handleViewChange('logical')}
                className={`px-3 py-1 rounded-md text-sm ${
                  architectureView === 'logical'
                    ? 'bg-indigo-100 text-indigo-700'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Logical View
              </button>
              <button
                onClick={() => handleViewChange('physical')}
                className={`px-3 py-1 rounded-md text-sm ${
                  architectureView === 'physical'
                    ? 'bg-indigo-100 text-indigo-700'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Physical View
              </button>
              <button
                onClick={() => handleViewChange('performance')}
                className={`px-3 py-1 rounded-md text-sm ${
                  architectureView === 'performance'
                    ? 'bg-indigo-100 text-indigo-700'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Performance View
              </button>
            </div>
          </div>
        </div>
        
        <div className="p-6">
          {architectureView === 'logical' && (
            <div>
              <div className="mb-6">
                <p className="text-gray-700 mb-4">
                  The logical architecture of Aideon's long-term memory system is designed around three primary memory layers that work together to maintain comprehensive project context over extended periods:
                </p>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {memoryLayers.map((layer) => (
                    <div key={layer.id} className="bg-gray-50 p-4 rounded-lg">
                      <h4 className="text-md font-medium text-gray-900 mb-2">{layer.name}</h4>
                      <p className="text-sm text-gray-700 mb-3">{layer.description}</p>
                      <div className="space-y-2 text-xs">
                        <div className="flex justify-between">
                          <span className="text-gray-500">Retention:</span>
                          <span className="text-gray-900">{layer.retention}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-500">Access Speed:</span>
                          <span className="text-gray-900">{layer.accessSpeed}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-500">Current Size:</span>
                          <span className="text-gray-900">{layer.size}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="bg-indigo-50 p-4 rounded-lg">
                <h4 className="text-md font-medium text-indigo-900 mb-2">Key Architecture Features</h4>
                <ul className="space-y-2 text-sm text-indigo-800">
                  <li className="flex items-start">
                    <i className="fas fa-check-circle text-indigo-600 mt-1 mr-2"></i>
                    <span>Hierarchical compression for efficient storage of historical context</span>
                  </li>
                  <li className="flex items-start">
                    <i className="fas fa-check-circle text-indigo-600 mt-1 mr-2"></i>
                    <span>Semantic indexing for rapid retrieval of relevant information</span>
                  </li>
                  <li className="flex items-start">
                    <i className="fas fa-check-circle text-indigo-600 mt-1 mr-2"></i>
                    <span>Continuous background consolidation to optimize memory structures</span>
                  </li>
                  <li className="flex items-start">
                    <i className="fas fa-check-circle text-indigo-600 mt-1 mr-2"></i>
                    <span>Distributed storage with redundancy for enterprise reliability</span>
                  </li>
                  <li className="flex items-start">
                    <i className="fas fa-check-circle text-indigo-600 mt-1 mr-2"></i>
                    <span>Automatic context switching based on relevance and recency</span>
                  </li>
                </ul>
              </div>
            </div>
          )}
          
          {architectureView === 'physical' && (
            <div>
              <div className="mb-6">
                <p className="text-gray-700 mb-4">
                  The physical architecture implements a distributed, multi-tiered storage system optimized for both performance and reliability:
                </p>
                
                <div className="bg-gray-50 p-4 rounded-lg mb-6">
                  <h4 className="text-md font-medium text-gray-900 mb-2">Storage Tiers</h4>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm font-medium text-gray-700">Hot Storage (SSD)</span>
                        <span className="text-xs text-gray-500">250 GB</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-red-500 h-2 rounded-full" style={{ width: '65%' }}></div>
                      </div>
                      <p className="text-xs text-gray-500 mt-1">Active projects and frequently accessed contexts</p>
                    </div>
                    
                    <div>
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm font-medium text-gray-700">Warm Storage (Hybrid)</span>
                        <span className="text-xs text-gray-500">450 GB</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '40%' }}></div>
                      </div>
                      <p className="text-xs text-gray-500 mt-1">Recently accessed projects and intermediate contexts</p>
                    </div>
                    
                    <div>
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm font-medium text-gray-700">Cold Storage (Object Storage)</span>
                        <span className="text-xs text-gray-500">500 GB</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-blue-500 h-2 rounded-full" style={{ width: '25%' }}></div>
                      </div>
                      <p className="text-xs text-gray-500 mt-1">Historical contexts and archived projects</p>
                    </div>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="text-md font-medium text-gray-900 mb-2">Redundancy & Reliability</h4>
                    <ul className="space-y-2 text-sm text-gray-700">
                      <li className="flex items-start">
                        <i className="fas fa-shield-alt text-gray-600 mt-1 mr-2"></i>
                        <span>Triple redundancy for critical project contexts</span>
                      </li>
                      <li className="flex items-start">
                        <i className="fas fa-shield-alt text-gray-600 mt-1 mr-2"></i>
                        <span>Geographical distribution across multiple data centers</span>
                      </li>
                      <li className="flex items-start">
                        <i className="fas fa-shield-alt text-gray-600 mt-1 mr-2"></i>
                        <span>Continuous integrity verification with checksums</span>
                      </li>
                      <li className="flex items-start">
                        <i className="fas fa-shield-alt text-gray-600 mt-1 mr-2"></i>
                        <span>Automatic failover with &lt;10ms detection</span>
                      </li>
                    </ul>
                  </div>
                  
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="text-md font-medium text-gray-900 mb-2">Scaling Capabilities</h4>
                    <ul className="space-y-2 text-sm text-gray-700">
                      <li className="flex items-start">
                        <i className="fas fa-expand-arrows-alt text-gray-600 mt-1 mr-2"></i>
                        <span>Horizontal scaling up to 50 PB total capacity</span>
                      </li>
                      <li className="flex items-start">
                        <i className="fas fa-expand-arrows-alt text-gray-600 mt-1 mr-2"></i>
                        <span>Support for up to 10,000 concurrent projects</span>
                      </li>
                      <li className="flex items-start">
                        <i className="fas fa-expand-arrows-alt text-gray-600 mt-1 mr-2"></i>
                        <span>Dynamic resource allocation based on project activity</span>
                      </li>
                      <li className="flex items-start">
                        <i className="fas fa-expand-arrows-alt text-gray-600 mt-1 mr-2"></i>
                        <span>Automatic tiering based on access patterns</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {architectureView === 'performance' && (
            <div>
              <div className="mb-6">
                <p className="text-gray-700 mb-4">
                  The performance characteristics of the long-term memory system are optimized for both rapid access to recent contexts and reliable retrieval of historical information:
                </p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="text-md font-medium text-gray-900 mb-2">Access Performance</h4>
                    <div className="space-y-3">
                      <div>
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-sm text-gray-700">Recent Context (7 days)</span>
                          <span className="text-xs font-medium text-green-700">35-50ms</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div className="bg-green-500 h-2 rounded-full" style={{ width: '95%' }}></div>
                        </div>
                      </div>
                      
                      <div>
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-sm text-gray-700">Intermediate Context (30 days)</span>
                          <span className="text-xs font-medium text-green-700">80-120ms</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div className="bg-green-500 h-2 rounded-full" style={{ width: '85%' }}></div>
                        </div>
                      </div>
                      
                      <div>
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-sm text-gray-700">Historical Context (1+ year)</span>
                          <span className="text-xs font-medium text-yellow-700">300-500ms</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '70%' }}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="text-md font-medium text-gray-900 mb-2">Retrieval Accuracy</h4>
                    <div className="space-y-3">
                      <div>
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-sm text-gray-700">Factual Information</span>
                          <span className="text-xs font-medium text-green-700">99.8%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div className="bg-green-500 h-2 rounded-full" style={{ width: '99.8%' }}></div>
                        </div>
                      </div>
                      
                      <div>
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-sm text-gray-700">Contextual Relevance</span>
                          <span className="text-xs font-medium text-green-700">98.2%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div className="bg-green-500 h-2 rounded-full" style={{ width: '98.2%' }}></div>
                        </div>
                      </div>
                      
                      <div>
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-sm text-gray-700">Temporal Accuracy</span>
                          <span className="text-xs font-medium text-green-700">99.5%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div className="bg-green-500 h-2 rounded-full" style={{ width: '99.5%' }}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="bg-indigo-50 p-4 rounded-lg">
                  <h4 className="text-md font-medium text-indigo-900 mb-2">Performance Optimizations</h4>
                  <ul className="space-y-2 text-sm text-indigo-800">
                    <li className="flex items-start">
                      <i className="fas fa-bolt text-indigo-600 mt-1 mr-2"></i>
                      <span>Predictive pre-fetching based on context and user behavior</span>
                    </li>
                    <li className="flex items-start">
                      <i className="fas fa-bolt text-indigo-600 mt-1 mr-2"></i>
                      <span>Adaptive caching with multi-level priority queues</span>
                    </li>
                    <li className="flex items-start">
                      <i className="fas fa-bolt text-indigo-600 mt-1 mr-2"></i>
                      <span>Parallel retrieval across distributed storage nodes</span>
                    </li>
                    <li className="flex items-start">
                      <i className="fas fa-bolt text-indigo-600 mt-1 mr-2"></i>
                      <span>Background indexing and optimization during idle periods</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Sample Projects */}
      <div className="bg-white rounded-lg shadow-sm overflow-hidden mb-8">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Long-Running Projects</h3>
        </div>
        
        <div className="p-6">
          <div className="space-y-4">
            {sampleProjects.map((project) => (
              <div key={project.id} className="bg-gray-50 p-4 rounded-lg">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h4 className="text-md font-medium text-gray-900">{project.name}</h4>
                    <p className="text-sm text-gray-500">Running for {project.duration}</p>
                  </div>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(project.status)}`}>
                    {project.status.charAt(0).toUpperCase() + project.status.slice(1)}
                  </span>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Memory Size</p>
                    <p className="text-sm font-medium text-gray-900">{project.memorySize}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Context Segments</p>
                    <p className="text-sm font-medium text-gray-900">{project.contextSegments}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Last Accessed</p>
                    <p className="text-sm font-medium text-gray-900">{project.lastAccessed}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      {/* Active Memory Operations */}
      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Active Memory Operations</h3>
        </div>
        
        <div className="p-6">
          <div className="space-y-4">
            {activeOperations.map((operation) => (
              <div key={operation.id} className="bg-gray-50 p-4 rounded-lg">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h4 className="text-md font-medium text-gray-900">
                      {operation.type.charAt(0).toUpperCase() + operation.type.slice(1)}
                    </h4>
                    <p className="text-sm text-gray-500">{operation.project}</p>
                  </div>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(operation.status)}`}>
                    {operation.status.charAt(0).toUpperCase() + operation.status.slice(1)}
                  </span>
                </div>
                
                {operation.status === 'in-progress' && (
                  <div>
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-xs text-gray-500">Progress</span>
                      <span className="text-xs text-gray-700">{operation.progress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
                      <div 
                        className="bg-indigo-600 h-2 rounded-full" 
                        style={{ width: `${operation.progress}%` }}
                      ></div>
                    </div>
                  </div>
                )}
                
                <div className="text-xs text-gray-500">
                  Started: {operation.startTime}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LongTermMemoryManager;
