import React, { useState, useEffect } from 'react';
import { FileSystemApi } from '../api/apiService';

interface FileSystemNavigatorProps {
  rootDirectory?: string;
  onFileSelect?: (file: FileItem) => void;
  onDirectoryChange?: (path: string) => void;
}

interface FileItem {
  name: string;
  type: 'file' | 'directory';
  path: string;
  size?: string;
  modified?: string;
  status?: 'new' | 'modified' | 'unmodified';
  children?: FileItem[];
}

const FileSystemNavigator: React.FC<FileSystemNavigatorProps> = ({
  rootDirectory = '/home/user',
  onFileSelect,
  onDirectoryChange
}) => {
  const [currentPath, setCurrentPath] = useState(rootDirectory);
  const [expandedDirs, setExpandedDirs] = useState<string[]>([rootDirectory]);
  const [selectedItem, setSelectedItem] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'tree' | 'list'>('tree');
  const [fileSystem, setFileSystem] = useState<FileItem | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  
  // Fetch file system data when component mounts or path changes
  useEffect(() => {
    fetchFileSystem(rootDirectory);
  }, [rootDirectory]);

  const fetchFileSystem = async (path: string) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await FileSystemApi.listFiles(path);
      
      if (response.data) {
        setFileSystem(response.data);
      }
    } catch (err: any) {
      console.error('Failed to fetch file system:', err);
      setError(err.message || 'Failed to load file system');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleDirectory = (path: string) => {
    if (expandedDirs.includes(path)) {
      setExpandedDirs(expandedDirs.filter(dir => dir !== path && !dir.startsWith(`${path}/`)));
    } else {
      setExpandedDirs([...expandedDirs, path]);
    }
  };

  const handleItemClick = (item: FileItem) => {
    setSelectedItem(item.path);
    
    if (item.type === 'directory') {
      toggleDirectory(item.path);
      if (onDirectoryChange) {
        onDirectoryChange(item.path);
      }
    } else if (onFileSelect) {
      onFileSelect(item);
    }
  };

  const getStatusIndicator = (status?: string) => {
    switch (status) {
      case 'new': return <span className="w-2 h-2 rounded-full bg-green-500"></span>;
      case 'modified': return <span className="w-2 h-2 rounded-full bg-amber-500"></span>;
      default: return <span className="w-2 h-2 rounded-full bg-gray-300"></span>;
    }
  };

  const getFileIcon = (name: string) => {
    const extension = name.split('.').pop()?.toLowerCase();
    
    switch (extension) {
      case 'pdf': return '📕';
      case 'doc':
      case 'docx': return '📘';
      case 'xls':
      case 'xlsx': return '📗';
      case 'ppt':
      case 'pptx': return '📙';
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif': return '🖼️';
      case 'mp3':
      case 'wav': return '🎵';
      case 'mp4':
      case 'mov': return '🎬';
      case 'zip':
      case 'rar': return '🗜️';
      case 'py': return '🐍';
      case 'js': return '📜';
      case 'html': return '🌐';
      case 'css': return '🎨';
      default: return '📄';
    }
  };

  const renderTreeView = (item: FileItem, depth = 0) => {
    const isExpanded = expandedDirs.includes(item.path);
    const isSelected = selectedItem === item.path;
    
    return (
      <div key={item.path}>
        <div 
          className={`flex items-center py-1 px-2 rounded-md ${
            isSelected ? 'bg-primary text-primary-foreground' : 'hover:bg-accent/50'
          }`}
          style={{ paddingLeft: `${(depth * 16) + 8}px` }}
          onClick={() => handleItemClick(item)}
        >
          {item.type === 'directory' ? (
            <span className="mr-1">{isExpanded ? '📂' : '📁'}</span>
          ) : (
            <span className="mr-1">{getFileIcon(item.name)}</span>
          )}
          <span className="flex-1 truncate">{item.name}</span>
          {getStatusIndicator(item.status)}
        </div>
        
        {item.type === 'directory' && isExpanded && item.children && (
          <div>
            {item.children.map(child => renderTreeView(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  const renderListView = () => {
    // Find the current directory in the file system
    const findDirectory = (path: string, item: FileItem): FileItem | null => {
      if (item.path === path) return item;
      if (item.children) {
        for (const child of item.children) {
          const found = findDirectory(path, child);
          if (found) return found;
        }
      }
      return null;
    };
    
    if (!fileSystem) return null;
    
    const currentDir = findDirectory(currentPath, fileSystem);
    if (!currentDir || currentDir.type !== 'directory') return null;
    
    return (
      <div>
        <div className="mb-2 flex items-center text-sm">
          <span className="text-muted-foreground">Path: </span>
          {currentPath.split('/').map((segment, index, array) => {
            if (!segment) return null;
            const path = array.slice(0, index + 1).join('/') || '/';
            return (
              <React.Fragment key={path}>
                <button 
                  className="hover:underline mx-1"
                  onClick={() => {
                    setCurrentPath(path);
                    if (onDirectoryChange) {
                      onDirectoryChange(path);
                    }
                  }}
                >
                  {segment}
                </button>
                {index < array.length - 1 && <span>/</span>}
              </React.Fragment>
            );
          })}
        </div>
        
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left py-2 px-2">Name</th>
              <th className="text-left py-2 px-2">Size</th>
              <th className="text-left py-2 px-2">Modified</th>
              <th className="text-left py-2 px-2">Status</th>
            </tr>
          </thead>
          <tbody>
            {currentDir.children?.map(item => (
              <tr 
                key={item.path} 
                className={`border-b border-border hover:bg-accent/30 ${
                  selectedItem === item.path ? 'bg-primary/10' : ''
                }`}
                onClick={() => handleItemClick(item)}
              >
                <td className="py-2 px-2 flex items-center">
                  {item.type === 'directory' ? (
                    <span className="mr-2">📁</span>
                  ) : (
                    <span className="mr-2">{getFileIcon(item.name)}</span>
                  )}
                  {item.name}
                </td>
                <td className="py-2 px-2">{item.size || '--'}</td>
                <td className="py-2 px-2">{item.modified || '--'}</td>
                <td className="py-2 px-2 flex items-center">
                  {getStatusIndicator(item.status)}
                  <span className="ml-2">
                    {item.status || 'unmodified'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div className="h-full flex flex-col">
      <div className="p-3 border-b border-border flex items-center justify-between">
        <h2 className="font-semibold text-sm">File System</h2>
        <div className="flex items-center space-x-1">
          <button 
            className={`p-1 rounded-md hover:bg-accent ${viewMode === 'tree' ? 'bg-accent' : ''}`}
            onClick={() => setViewMode('tree')}
            title="Tree view"
          >
            🌳
          </button>
          <button 
            className={`p-1 rounded-md hover:bg-accent ${viewMode === 'list' ? 'bg-accent' : ''}`}
            onClick={() => setViewMode('list')}
            title="List view"
          >
            📋
          </button>
          <button 
            className="p-1 rounded-md hover:bg-accent text-muted-foreground" 
            title="Refresh"
            onClick={() => fetchFileSystem(rootDirectory)}
          >
            🔄
          </button>
        </div>
      </div>
      
      <div className="flex-1 overflow-auto p-2">
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-muted-foreground">Loading file system...</div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-red-500">{error}</div>
          </div>
        ) : fileSystem ? (
          viewMode === 'tree' ? renderTreeView(fileSystem) : renderListView()
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-muted-foreground">No files found</div>
          </div>
        )}
      </div>
      
      <div className="border-t border-border p-2 flex items-center justify-between text-xs text-muted-foreground">
        <div>
          {fileSystem ? 
            `${fileSystem.children?.filter(item => item.type === 'directory').length || 0} directories, 
             ${fileSystem.children?.filter(item => item.type === 'file').length || 0} files` : 
            '0 directories, 0 files'}
        </div>
        <div>
          {fileSystem ? 
            `${fileSystem.children?.filter(item => item.status === 'new').length || 0} new, 
             ${fileSystem.children?.filter(item => item.status === 'modified').length || 0} modified` : 
            '0 new, 0 modified'}
        </div>
      </div>
    </div>
  );
};

export default FileSystemNavigator;
