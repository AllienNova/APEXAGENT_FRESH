// Artifact Version Control Component
import React, { useState, useEffect } from 'react';
import { Clock, GitBranch, GitCommit, GitMerge, ChevronDown, ChevronRight, Search, Filter, Download, Share2, Edit, Trash2, Plus, Check, X, FileText, Image, Code, File, Folder, ArrowLeft, ArrowRight, RefreshCw, Eye, EyeOff, Calendar, User, MessageSquare, MoreHorizontal, Copy, ExternalLink } from 'lucide-react';

// Mock data for demonstration
const artifactVersions = [
  {
    id: 'v1.0.0',
    name: 'Initial Version',
    timestamp: '2025-05-20 14:32:45',
    author: 'john.doe@example.com',
    changes: 12,
    status: 'committed',
    message: 'Initial version of the document',
    files: [
      { id: 'f1', name: 'document.md', type: 'markdown', size: '24.5 KB', status: 'added' },
      { id: 'f2', name: 'image1.png', type: 'image', size: '156 KB', status: 'added' },
      { id: 'f3', name: 'data.json', type: 'json', size: '8.2 KB', status: 'added' }
    ]
  },
  {
    id: 'v1.1.0',
    name: 'Content Update',
    timestamp: '2025-05-22 09:15:33',
    author: 'jane.smith@example.com',
    changes: 5,
    status: 'committed',
    message: 'Updated content with new research findings',
    files: [
      { id: 'f1', name: 'document.md', type: 'markdown', size: '26.8 KB', status: 'modified' },
      { id: 'f4', name: 'image2.png', type: 'image', size: '210 KB', status: 'added' }
    ]
  },
  {
    id: 'v1.2.0',
    name: 'Major Revision',
    timestamp: '2025-05-24 16:45:12',
    author: 'john.doe@example.com',
    changes: 18,
    status: 'committed',
    message: 'Major revision with restructured content and new sections',
    files: [
      { id: 'f1', name: 'document.md', type: 'markdown', size: '35.2 KB', status: 'modified' },
      { id: 'f5', name: 'image3.png', type: 'image', size: '180 KB', status: 'added' },
      { id: 'f6', name: 'references.bib', type: 'bibtex', size: '12.4 KB', status: 'added' },
      { id: 'f2', name: 'image1.png', type: 'image', size: '156 KB', status: 'deleted' }
    ]
  },
  {
    id: 'v1.3.0',
    name: 'Feedback Integration',
    timestamp: '2025-05-26 11:20:05',
    author: 'jane.smith@example.com',
    changes: 9,
    status: 'committed',
    message: 'Integrated feedback from review team',
    files: [
      { id: 'f1', name: 'document.md', type: 'markdown', size: '38.6 KB', status: 'modified' },
      { id: 'f7', name: 'feedback.md', type: 'markdown', size: '5.8 KB', status: 'added' }
    ]
  },
  {
    id: 'v1.4.0',
    name: 'Current Working Version',
    timestamp: '2025-05-27 10:05:18',
    author: 'john.doe@example.com',
    changes: 3,
    status: 'working',
    message: 'Final polishing before submission',
    files: [
      { id: 'f1', name: 'document.md', type: 'markdown', size: '39.2 KB', status: 'modified' },
      { id: 'f8', name: 'presentation.pptx', type: 'powerpoint', size: '2.4 MB', status: 'added' }
    ]
  }
];

const diffExample = {
  original: `# Introduction

This document outlines the architecture of our system. The system is designed to handle high loads and provide a seamless user experience.

## Key Components

1. Frontend Interface
2. Backend API
3. Database Layer
4. Caching System

## Performance Metrics

The system is designed to handle up to 1,000 concurrent users with response times under 200ms.`,
  
  modified: `# Introduction

This document outlines the architecture of our system. The system is designed to handle high loads, provide a seamless user experience, and ensure data security at all levels.

## Key Components

1. Frontend Interface
2. Backend API
3. Database Layer
4. Caching System
5. Security Layer
6. Monitoring System

## Performance Metrics

The system is designed to handle up to 10,000 concurrent users with response times under 100ms.

## Security Considerations

All data is encrypted both in transit and at rest using industry-standard encryption algorithms.`
};

const ArtifactVersionControl = () => {
  const [activeTab, setActiveTab] = useState('timeline');
  const [selectedVersion, setSelectedVersion] = useState(artifactVersions[artifactVersions.length - 1]);
  const [compareVersion, setCompareVersion] = useState(artifactVersions[artifactVersions.length - 2]);
  const [isComparing, setIsComparing] = useState(false);
  const [expandedItems, setExpandedItems] = useState({});
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showCreateVersionModal, setShowCreateVersionModal] = useState(false);
  const [showMergeModal, setShowMergeModal] = useState(false);
  
  // Toggle expanded state for a version
  const toggleExpanded = (id) => {
    setExpandedItems(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };
  
  // Select a version for viewing or comparison
  const handleVersionSelect = (version) => {
    if (isComparing) {
      setCompareVersion(version);
    } else {
      setSelectedVersion(version);
    }
  };
  
  // Toggle comparison mode
  const toggleComparisonMode = () => {
    setIsComparing(!isComparing);
    if (!isComparing && !compareVersion) {
      // Default to comparing with previous version
      const currentIndex = artifactVersions.findIndex(v => v.id === selectedVersion.id);
      if (currentIndex > 0) {
        setCompareVersion(artifactVersions[currentIndex - 1]);
      }
    }
  };
  
  // Get file icon based on type
  const getFileIcon = (type) => {
    switch (type) {
      case 'markdown':
        return <FileText className="w-4 h-4" />;
      case 'image':
        return <Image className="w-4 h-4" />;
      case 'json':
        return <Code className="w-4 h-4" />;
      case 'bibtex':
        return <FileText className="w-4 h-4" />;
      case 'powerpoint':
        return <File className="w-4 h-4" />;
      default:
        return <File className="w-4 h-4" />;
    }
  };
  
  // Get status color based on file status
  const getStatusColor = (status) => {
    switch (status) {
      case 'added':
        return 'text-green-500';
      case 'modified':
        return 'text-blue-500';
      case 'deleted':
        return 'text-red-500';
      default:
        return 'text-gray-500';
    }
  };
  
  // Timeline view component
  const TimelineView = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">Version Timeline</h2>
        <div className="flex items-center space-x-3">
          <div className="relative">
            <input 
              type="text" 
              placeholder="Search versions..."
              className="px-3 py-2 pr-8 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <Search className="w-4 h-4 absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
          </div>
          
          <div className="relative">
            <button className="flex items-center space-x-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 text-sm">
              <Filter className="w-4 h-4" />
              <span>Filters</span>
              <ChevronDown className="w-4 h-4" />
            </button>
          </div>
          
          <button 
            className="px-3 py-2 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center space-x-2"
            onClick={() => setShowCreateVersionModal(true)}
          >
            <Plus className="w-4 h-4" />
            <span>New Version</span>
          </button>
        </div>
      </div>
      
      <div className="relative">
        {/* Vertical timeline line */}
        <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200 dark:bg-gray-700"></div>
        
        <div className="space-y-4">
          {artifactVersions.map((version, index) => (
            <div key={version.id} className="relative">
              <div 
                className={`ml-8 p-4 rounded-lg border ${
                  selectedVersion.id === version.id 
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/10' 
                    : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900'
                } cursor-pointer hover:border-blue-300 dark:hover:border-blue-700`}
                onClick={() => handleVersionSelect(version)}
              >
                <div className="absolute left-2 top-4 w-4 h-4 rounded-full bg-blue-500 border-2 border-white dark:border-gray-900"></div>
                
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="font-medium">{version.name}</span>
                    <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-800">
                      {version.id}
                    </span>
                    {version.status === 'working' && (
                      <span className="text-xs px-2 py-0.5 rounded-full bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-300">
                        Working
                      </span>
                    )}
                  </div>
                  <div className="flex items-center space-x-2">
                    <button 
                      className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleExpanded(version.id);
                      }}
                    >
                      {expandedItems[version.id] ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                    </button>
                    <button className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                      <MoreHorizontal className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                
                <div className="flex items-center text-sm text-gray-500 dark:text-gray-400 mb-2">
                  <Clock className="w-3 h-3 mr-1" />
                  <span>{version.timestamp}</span>
                  <span className="mx-2">•</span>
                  <User className="w-3 h-3 mr-1" />
                  <span>{version.author}</span>
                  <span className="mx-2">•</span>
                  <GitCommit className="w-3 h-3 mr-1" />
                  <span>{version.changes} changes</span>
                </div>
                
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {version.message}
                </p>
                
                {expandedItems[version.id] && (
                  <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                    <h4 className="text-xs font-medium mb-2">Files Changed</h4>
                    <div className="space-y-2">
                      {version.files.map(file => (
                        <div key={file.id} className="flex items-center justify-between text-sm">
                          <div className="flex items-center space-x-2">
                            {getFileIcon(file.type)}
                            <span>{file.name}</span>
                            <span className="text-xs text-gray-500">{file.size}</span>
                          </div>
                          <span className={getStatusColor(file.status)}>
                            {file.status.charAt(0).toUpperCase() + file.status.slice(1)}
                          </span>
                        </div>
                      ))}
                    </div>
                    
                    <div className="flex items-center space-x-2 mt-3">
                      <button className="px-2 py-1 text-xs text-blue-600 dark:text-blue-400 hover:underline">
                        View Details
                      </button>
                      <button 
                        className="px-2 py-1 text-xs text-blue-600 dark:text-blue-400 hover:underline"
                        onClick={(e) => {
                          e.stopPropagation();
                          setCompareVersion(version);
                          setIsComparing(true);
                          setActiveTab('compare');
                        }}
                      >
                        Compare
                      </button>
                      {index < artifactVersions.length - 1 && (
                        <button 
                          className="px-2 py-1 text-xs text-blue-600 dark:text-blue-400 hover:underline"
                          onClick={(e) => {
                            e.stopPropagation();
                            setShowMergeModal(true);
                          }}
                        >
                          Merge
                        </button>
                      )}
                      {version.status === 'working' && (
                        <button className="px-2 py-1 text-xs text-red-600 dark:text-red-400 hover:underline">
                          Discard
                        </button>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
  
  // File browser component
  const FileBrowser = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-2">
          <h2 className="text-xl font-semibold">Files</h2>
          <span className="text-sm text-gray-500">({selectedVersion.name} - {selectedVersion.id})</span>
        </div>
        <div className="flex items-center space-x-3">
          <div className="relative">
            <input 
              type="text" 
              placeholder="Search files..."
              className="px-3 py-2 pr-8 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <Search className="w-4 h-4 absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
          </div>
          
          <button className="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center space-x-2">
            <Download className="w-4 h-4" />
            <span>Download</span>
          </button>
          
          <button className="px-3 py-2 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center space-x-2">
            <Plus className="w-4 h-4" />
            <span>Add File</span>
          </button>
        </div>
      </div>
      
      <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-2">
            <Folder className="w-5 h-5 text-blue-500" />
            <span className="font-medium">Project Root</span>
          </div>
        </div>
        <div className="p-4">
          <div className="space-y-2">
            {selectedVersion.files.map(file => (
              <div 
                key={file.id} 
                className="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer"
              >
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-800 flex items-center justify-center text-gray-500">
                    {getFileIcon(file.type)}
                  </div>
                  <div>
                    <h4 className="text-sm font-medium">{file.name}</h4>
                    <p className="text-xs text-gray-500">{file.size}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`text-xs ${getStatusColor(file.status)}`}>
                    {file.status.charAt(0).toUpperCase() + file.status.slice(1)}
                  </span>
                  <button className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                    <Download className="w-4 h-4" />
                  </button>
                  <button className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                    <Edit className="w-4 h-4" />
                  </button>
                  <button 
                    className="p-1 text-gray-400 hover:text-red-600 dark:hover:text-red-400"
                    onClick={() => setShowDeleteModal(true)}
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="font-semibold">File Preview</h3>
        </div>
        <div className="p-4">
          <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 font-mono text-sm overflow-x-auto">
            <pre>{diffExample.modified}</pre>
          </div>
        </div>
      </div>
    </div>
  );
  
  // Comparison view component
  const ComparisonView = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">Version Comparison</h2>
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-2">
            <div>
              <label className="block text-xs text-gray-500 mb-1">Base Version</label>
              <select 
                className="w-full bg-transparent text-sm"
                value={compareVersion.id}
                onChange={(e) => {
                  const selected = artifactVersions.find(v => v.id === e.target.value);
                  if (selected) setCompareVersion(selected);
                }}
              >
                {artifactVersions.map(version => (
                  <option key={version.id} value={version.id}>{version.name} ({version.id})</option>
                ))}
              </select>
            </div>
            <ArrowRight className="w-4 h-4 text-gray-400" />
            <div>
              <label className="block text-xs text-gray-500 mb-1">Compare Version</label>
              <select 
                className="w-full bg-transparent text-sm"
                value={selectedVersion.id}
                onChange={(e) => {
                  const selected = artifactVersions.find(v => v.id === e.target.value);
                  if (selected) setSelectedVersion(selected);
                }}
              >
                {artifactVersions.map(version => (
                  <option key={version.id} value={version.id}>{version.name} ({version.id})</option>
                ))}
              </select>
            </div>
          </div>
          
          <button className="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center space-x-2">
            <Download className="w-4 h-4" />
            <span>Export Diff</span>
          </button>
          
          <button 
            className="px-3 py-2 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center space-x-2"
            onClick={() => setShowMergeModal(true)}
          >
            <GitMerge className="w-4 h-4" />
            <span>Merge Changes</span>
          </button>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <h3 className="font-semibold">{compareVersion.name}</h3>
                <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-800">
                  {compareVersion.id}
                </span>
              </div>
              <div className="text-xs text-gray-500">
                {compareVersion.timestamp}
              </div>
            </div>
          </div>
          <div className="p-4">
            <div className="space-y-2 mb-4">
              <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <User className="w-3 h-3 mr-1" />
                <span>{compareVersion.author}</span>
              </div>
              <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <MessageSquare className="w-3 h-3 mr-1" />
                <span>{compareVersion.message}</span>
              </div>
            </div>
            
            <h4 className="text-xs font-medium mb-2">Files</h4>
            <div className="space-y-2">
              {compareVersion.files.map(file => (
                <div key={file.id} className="flex items-center justify-between text-sm p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800">
                  <div className="flex items-center space-x-2">
                    {getFileIcon(file.type)}
                    <span>{file.name}</span>
                  </div>
                  <span className="text-xs text-gray-500">{file.size}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <h3 className="font-semibold">{selectedVersion.name}</h3>
                <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-800">
                  {selectedVersion.id}
                </span>
              </div>
              <div className="text-xs text-gray-500">
                {selectedVersion.timestamp}
              </div>
            </div>
          </div>
          <div className="p-4">
            <div className="space-y-2 mb-4">
              <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <User className="w-3 h-3 mr-1" />
                <span>{selectedVersion.author}</span>
              </div>
              <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <MessageSquare className="w-3 h-3 mr-1" />
                <span>{selectedVersion.message}</span>
              </div>
            </div>
            
            <h4 className="text-xs font-medium mb-2">Files</h4>
            <div className="space-y-2">
              {selectedVersion.files.map(file => (
                <div key={file.id} className="flex items-center justify-between text-sm p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800">
                  <div className="flex items-center space-x-2">
                    {getFileIcon(file.type)}
                    <span>{file.name}</span>
                  </div>
                  <span className="text-xs text-gray-500">{file.size}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
      
      <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold">Diff View</h3>
            <div className="flex items-center space-x-2">
              <button className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                <RefreshCw className="w-4 h-4" />
              </button>
              <select className="text-xs border border-gray-300 dark:border-gray-600 rounded px-2 py-1 bg-white dark:bg-gray-800">
                <option>Unified View</option>
                <option>Split View</option>
                <option>Side-by-Side</option>
              </select>
            </div>
          </div>
        </div>
        <div className="p-4">
          <div className="bg-gray-50 dark:bg-gray-800 rounded-lg overflow-x-auto">
            <table className="w-full font-mono text-sm">
              <tbody>
                <tr className="bg-gray-100 dark:bg-gray-700">
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">1</td>
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">1</td>
                  <td className="px-4 py-1 whitespace-pre"># Introduction</td>
                </tr>
                <tr>
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">2</td>
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">2</td>
                  <td className="px-4 py-1 whitespace-pre"></td>
                </tr>
                <tr className="bg-red-100 dark:bg-red-900/20">
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">3</td>
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">-</td>
                  <td className="px-4 py-1 whitespace-pre text-red-600 dark:text-red-400">This document outlines the architecture of our system. The system is designed to handle high loads and provide a seamless user experience.</td>
                </tr>
                <tr className="bg-green-100 dark:bg-green-900/20">
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">-</td>
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">3</td>
                  <td className="px-4 py-1 whitespace-pre text-green-600 dark:text-green-400">This document outlines the architecture of our system. The system is designed to handle high loads, provide a seamless user experience, and ensure data security at all levels.</td>
                </tr>
                <tr>
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">4</td>
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">4</td>
                  <td className="px-4 py-1 whitespace-pre"></td>
                </tr>
                <tr className="bg-gray-100 dark:bg-gray-700">
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">5</td>
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">5</td>
                  <td className="px-4 py-1 whitespace-pre">## Key Components</td>
                </tr>
                <tr>
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">6</td>
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">6</td>
                  <td className="px-4 py-1 whitespace-pre"></td>
                </tr>
                <tr>
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">7</td>
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">7</td>
                  <td className="px-4 py-1 whitespace-pre">1. Frontend Interface</td>
                </tr>
                <tr>
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">8</td>
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">8</td>
                  <td className="px-4 py-1 whitespace-pre">2. Backend API</td>
                </tr>
                <tr>
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">9</td>
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">9</td>
                  <td className="px-4 py-1 whitespace-pre">3. Database Layer</td>
                </tr>
                <tr>
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">10</td>
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">10</td>
                  <td className="px-4 py-1 whitespace-pre">4. Caching System</td>
                </tr>
                <tr className="bg-green-100 dark:bg-green-900/20">
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">-</td>
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">11</td>
                  <td className="px-4 py-1 whitespace-pre text-green-600 dark:text-green-400">5. Security Layer</td>
                </tr>
                <tr className="bg-green-100 dark:bg-green-900/20">
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">-</td>
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">12</td>
                  <td className="px-4 py-1 whitespace-pre text-green-600 dark:text-green-400">6. Monitoring System</td>
                </tr>
                <tr>
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">11</td>
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">13</td>
                  <td className="px-4 py-1 whitespace-pre"></td>
                </tr>
                <tr className="bg-gray-100 dark:bg-gray-700">
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">12</td>
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">14</td>
                  <td className="px-4 py-1 whitespace-pre">## Performance Metrics</td>
                </tr>
                <tr>
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">13</td>
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">15</td>
                  <td className="px-4 py-1 whitespace-pre"></td>
                </tr>
                <tr className="bg-red-100 dark:bg-red-900/20">
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">14</td>
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">-</td>
                  <td className="px-4 py-1 whitespace-pre text-red-600 dark:text-red-400">The system is designed to handle up to 1,000 concurrent users with response times under 200ms.</td>
                </tr>
                <tr className="bg-green-100 dark:bg-green-900/20">
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">-</td>
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">16</td>
                  <td className="px-4 py-1 whitespace-pre text-green-600 dark:text-green-400">The system is designed to handle up to 10,000 concurrent users with response times under 100ms.</td>
                </tr>
                <tr className="bg-green-100 dark:bg-green-900/20">
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">-</td>
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">17</td>
                  <td className="px-4 py-1 whitespace-pre text-green-600 dark:text-green-400"></td>
                </tr>
                <tr className="bg-green-100 dark:bg-green-900/20">
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">-</td>
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">18</td>
                  <td className="px-4 py-1 whitespace-pre text-green-600 dark:text-green-400">## Security Considerations</td>
                </tr>
                <tr className="bg-green-100 dark:bg-green-900/20">
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">-</td>
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">19</td>
                  <td className="px-4 py-1 whitespace-pre text-green-600 dark:text-green-400"></td>
                </tr>
                <tr className="bg-green-100 dark:bg-green-900/20">
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">-</td>
                  <td className="px-4 py-1 text-gray-500 select-none w-12 text-right">20</td>
                  <td className="px-4 py-1 whitespace-pre text-green-600 dark:text-green-400">All data is encrypted both in transit and at rest using industry-standard encryption algorithms.</td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <div className="mt-4 flex items-center justify-between text-sm">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-1">
                <div className="w-3 h-3 bg-red-100 dark:bg-red-900/20"></div>
                <span className="text-xs text-gray-500">Removed</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-3 h-3 bg-green-100 dark:bg-green-900/20"></div>
                <span className="text-xs text-gray-500">Added</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-3 h-3 bg-yellow-100 dark:bg-yellow-900/20"></div>
                <span className="text-xs text-gray-500">Modified</span>
              </div>
            </div>
            <div className="text-xs text-gray-500">
              Showing changes for document.md
            </div>
          </div>
        </div>
      </div>
    </div>
  );
  
  // Branch view component
  const BranchView = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">Branches</h2>
        <div className="flex items-center space-x-3">
          <button className="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center space-x-2">
            <GitMerge className="w-4 h-4" />
            <span>Merge Branch</span>
          </button>
          
          <button className="px-3 py-2 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center space-x-2">
            <GitBranch className="w-4 h-4" />
            <span>New Branch</span>
          </button>
        </div>
      </div>
      
      <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="font-semibold">Active Branches</h3>
        </div>
        <div className="p-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 rounded-lg bg-blue-50 dark:bg-blue-900/10 border border-blue-200 dark:border-blue-800">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 rounded-lg bg-blue-100 dark:bg-blue-900/20 flex items-center justify-center text-blue-500">
                  <GitBranch className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-sm font-medium">main</h4>
                  <p className="text-xs text-gray-500">Default branch</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300">
                  Current
                </span>
                <button className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                  <MoreHorizontal className="w-4 h-4" />
                </button>
              </div>
            </div>
            
            <div className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 border border-gray-200 dark:border-gray-700">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 rounded-lg bg-purple-100 dark:bg-purple-900/20 flex items-center justify-center text-purple-500">
                  <GitBranch className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-sm font-medium">feature/new-section</h4>
                  <p className="text-xs text-gray-500">Created 2 days ago</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <button className="px-2 py-1 text-xs text-blue-600 dark:text-blue-400 hover:underline">
                  Switch
                </button>
                <button className="px-2 py-1 text-xs text-blue-600 dark:text-blue-400 hover:underline">
                  Merge
                </button>
                <button className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                  <MoreHorizontal className="w-4 h-4" />
                </button>
              </div>
            </div>
            
            <div className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 border border-gray-200 dark:border-gray-700">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 rounded-lg bg-green-100 dark:bg-green-900/20 flex items-center justify-center text-green-500">
                  <GitBranch className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-sm font-medium">bugfix/formatting</h4>
                  <p className="text-xs text-gray-500">Created 5 days ago</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <button className="px-2 py-1 text-xs text-blue-600 dark:text-blue-400 hover:underline">
                  Switch
                </button>
                <button className="px-2 py-1 text-xs text-blue-600 dark:text-blue-400 hover:underline">
                  Merge
                </button>
                <button className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                  <MoreHorizontal className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="font-semibold">Branch Visualization</h3>
        </div>
        <div className="p-4">
          <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 h-64 flex items-center justify-center">
            <div className="text-center text-gray-500">
              <GitBranch className="w-12 h-12 mx-auto mb-2" />
              <p>Branch visualization would be displayed here</p>
              <p className="text-sm">Showing commit history and branch relationships</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
  
  // Delete confirmation modal
  const DeleteModal = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-900 rounded-lg w-full max-w-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Confirm Deletion</h3>
          <button 
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            onClick={() => setShowDeleteModal(false)}
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
          Are you sure you want to delete this file? This action cannot be undone.
        </p>
        
        <div className="flex items-center justify-end space-x-3">
          <button 
            className="px-4 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800"
            onClick={() => setShowDeleteModal(false)}
          >
            Cancel
          </button>
          <button 
            className="px-4 py-2 text-sm bg-red-500 text-white rounded-lg hover:bg-red-600"
            onClick={() => setShowDeleteModal(false)}
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
  
  // Create version modal
  const CreateVersionModal = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-900 rounded-lg w-full max-w-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Create New Version</h3>
          <button 
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            onClick={() => setShowCreateVersionModal(false)}
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className="space-y-4 mb-6">
          <div>
            <label className="block text-sm font-medium mb-1">Version Name</label>
            <input 
              type="text" 
              placeholder="e.g., Final Draft"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Version ID</label>
            <input 
              type="text" 
              placeholder="e.g., v1.5.0"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Commit Message</label>
            <textarea 
              placeholder="Describe the changes in this version"
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            ></textarea>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Base Version</label>
            <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 focus:ring-2 focus:ring-blue-500 focus:border-transparent">
              {artifactVersions.map(version => (
                <option key={version.id} value={version.id}>{version.name} ({version.id})</option>
              ))}
            </select>
          </div>
          
          <div className="flex items-center space-x-2">
            <input type="checkbox" id="create-branch" className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
            <label htmlFor="create-branch" className="text-sm">Create new branch for this version</label>
          </div>
        </div>
        
        <div className="flex items-center justify-end space-x-3">
          <button 
            className="px-4 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800"
            onClick={() => setShowCreateVersionModal(false)}
          >
            Cancel
          </button>
          <button 
            className="px-4 py-2 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600"
            onClick={() => setShowCreateVersionModal(false)}
          >
            Create Version
          </button>
        </div>
      </div>
    </div>
  );
  
  // Merge modal
  const MergeModal = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-900 rounded-lg w-full max-w-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Merge Versions</h3>
          <button 
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            onClick={() => setShowMergeModal(false)}
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className="space-y-4 mb-6">
          <div className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-800">
            <div className="flex items-center space-x-2">
              <GitCommit className="w-4 h-4 text-blue-500" />
              <span className="text-sm font-medium">{compareVersion.name}</span>
            </div>
            <span className="text-xs text-gray-500">{compareVersion.id}</span>
          </div>
          
          <div className="flex items-center justify-center">
            <GitMerge className="w-6 h-6 text-purple-500" />
          </div>
          
          <div className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-800">
            <div className="flex items-center space-x-2">
              <GitCommit className="w-4 h-4 text-green-500" />
              <span className="text-sm font-medium">{selectedVersion.name}</span>
            </div>
            <span className="text-xs text-gray-500">{selectedVersion.id}</span>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Merge Strategy</label>
            <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 focus:ring-2 focus:ring-blue-500 focus:border-transparent">
              <option>Auto-merge (Recommended)</option>
              <option>Manual Resolution</option>
              <option>Theirs (Keep Target Version)</option>
              <option>Ours (Keep Source Version)</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Merge Message</label>
            <textarea 
              placeholder="Describe the purpose of this merge"
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              defaultValue={`Merge ${compareVersion.name} (${compareVersion.id}) into ${selectedVersion.name} (${selectedVersion.id})`}
            ></textarea>
          </div>
          
          <div className="flex items-center space-x-2">
            <input type="checkbox" id="create-version" className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" defaultChecked />
            <label htmlFor="create-version" className="text-sm">Create new version after merge</label>
          </div>
        </div>
        
        <div className="flex items-center justify-end space-x-3">
          <button 
            className="px-4 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800"
            onClick={() => setShowMergeModal(false)}
          >
            Cancel
          </button>
          <button 
            className="px-4 py-2 text-sm bg-purple-500 text-white rounded-lg hover:bg-purple-600"
            onClick={() => setShowMergeModal(false)}
          >
            Merge Versions
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="h-full">
      <div className="flex border-b border-gray-200 dark:border-gray-700 mb-6">
        <button 
          className={`px-4 py-2 font-medium text-sm ${activeTab === 'timeline' ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-500' : 'text-gray-600 dark:text-gray-400'}`}
          onClick={() => setActiveTab('timeline')}
        >
          Timeline
        </button>
        <button 
          className={`px-4 py-2 font-medium text-sm ${activeTab === 'files' ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-500' : 'text-gray-600 dark:text-gray-400'}`}
          onClick={() => setActiveTab('files')}
        >
          Files
        </button>
        <button 
          className={`px-4 py-2 font-medium text-sm ${activeTab === 'compare' ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-500' : 'text-gray-600 dark:text-gray-400'}`}
          onClick={() => setActiveTab('compare')}
        >
          Compare
        </button>
        <button 
          className={`px-4 py-2 font-medium text-sm ${activeTab === 'branches' ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-500' : 'text-gray-600 dark:text-gray-400'}`}
          onClick={() => setActiveTab('branches')}
        >
          Branches
        </button>
      </div>
      
      {activeTab === 'timeline' && <TimelineView />}
      {activeTab === 'files' && <FileBrowser />}
      {activeTab === 'compare' && <ComparisonView />}
      {activeTab === 'branches' && <BranchView />}
      
      {showDeleteModal && <DeleteModal />}
      {showCreateVersionModal && <CreateVersionModal />}
      {showMergeModal && <MergeModal />}
    </div>
  );
};

export default ArtifactVersionControl;
