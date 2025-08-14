import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Alert,
  Animated,
  Dimensions,
  Modal,
  ScrollView,
  Share,
  Linking,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { useDispatch, useSelector } from 'react-redux';
import DocumentPicker from 'react-native-document-picker';
import * as FileSystem from 'expo-file-system';

import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';
import Card from '../../components/ui/Card';
import { Colors, Typography, Spacing, BorderRadius, Shadows } from '../../constants/theme';
import { RootState } from '../../store';
import { 
  loadFiles, 
  uploadFile, 
  deleteFile, 
  shareFile, 
  createFolder,
  loadProjects,
  downloadFile,
  previewFile
} from '../../store/slices/filesSlice';

const { width } = Dimensions.get('window');

interface FileItem {
  id: string;
  name: string;
  type: 'file' | 'folder';
  size: number;
  mimeType: string;
  createdAt: Date;
  modifiedAt: Date;
  path: string;
  isShared: boolean;
  downloadUrl?: string;
  thumbnailUrl?: string;
  tags: string[];
  project?: string;
}

interface Project {
  id: string;
  name: string;
  description: string;
  fileCount: number;
  totalSize: number;
  color: string;
  lastModified: Date;
}

const FILE_TYPE_ICONS: { [key: string]: string } = {
  'application/pdf': 'document-text',
  'application/msword': 'document',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'document',
  'application/vnd.ms-excel': 'grid',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'grid',
  'application/vnd.ms-powerpoint': 'easel',
  'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'easel',
  'text/plain': 'document-text',
  'text/csv': 'grid',
  'image/jpeg': 'image',
  'image/png': 'image',
  'image/gif': 'image',
  'video/mp4': 'videocam',
  'video/quicktime': 'videocam',
  'audio/mpeg': 'musical-notes',
  'audio/wav': 'musical-notes',
  'application/zip': 'archive',
  'application/x-zip-compressed': 'archive',
  'folder': 'folder',
};

const FILE_TYPE_COLORS: { [key: string]: string } = {
  'application/pdf': Colors.error,
  'application/msword': Colors.primary[500],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': Colors.primary[500],
  'application/vnd.ms-excel': Colors.success,
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': Colors.success,
  'application/vnd.ms-powerpoint': Colors.warning,
  'application/vnd.openxmlformats-officedocument.presentationml.presentation': Colors.warning,
  'text/plain': Colors.gray[500],
  'text/csv': Colors.success,
  'image/jpeg': Colors.secondary[500],
  'image/png': Colors.secondary[500],
  'image/gif': Colors.secondary[500],
  'video/mp4': Colors.purple[500],
  'video/quicktime': Colors.purple[500],
  'audio/mpeg': Colors.pink[500],
  'audio/wav': Colors.pink[500],
  'application/zip': Colors.gray[600],
  'application/x-zip-compressed': Colors.gray[600],
  'folder': Colors.primary[500],
};

const FileCard: React.FC<{ 
  file: FileItem; 
  onPress: () => void;
  onShare: () => void;
  onDelete: () => void;
  onMore: () => void;
}> = ({ file, onPress, onShare, onDelete, onMore }) => {
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const scaleAnim = useRef(new Animated.Value(0.95)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 300,
        useNativeDriver: true,
      }),
      Animated.spring(scaleAnim, {
        toValue: 1,
        tension: 50,
        friction: 8,
        useNativeDriver: true,
      }),
    ]).start();
  }, []);

  const getFileIcon = () => {
    return FILE_TYPE_ICONS[file.mimeType] || FILE_TYPE_ICONS[file.type] || 'document';
  };

  const getFileColor = () => {
    return FILE_TYPE_COLORS[file.mimeType] || FILE_TYPE_COLORS[file.type] || Colors.gray[500];
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const formatDate = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    return date.toLocaleDateString();
  };

  return (
    <Animated.View
      style={[
        styles.fileCard,
        {
          opacity: fadeAnim,
          transform: [{ scale: scaleAnim }],
        },
      ]}
    >
      <TouchableOpacity onPress={onPress} style={styles.fileCardContent}>
        <View style={styles.fileHeader}>
          <View style={[styles.fileIcon, { backgroundColor: getFileColor() + '20' }]}>
            <Ionicons name={getFileIcon() as any} size={24} color={getFileColor()} />
          </View>
          <View style={styles.fileInfo}>
            <Text style={styles.fileName} numberOfLines={1}>{file.name}</Text>
            <View style={styles.fileMeta}>
              {file.type === 'file' && (
                <>
                  <Text style={styles.fileSize}>{formatFileSize(file.size)}</Text>
                  <Text style={styles.fileSeparator}>•</Text>
                </>
              )}
              <Text style={styles.fileDate}>{formatDate(file.modifiedAt)}</Text>
              {file.isShared && (
                <>
                  <Text style={styles.fileSeparator}>•</Text>
                  <Ionicons name="people" size={12} color={Colors.primary[500]} />
                </>
              )}
            </View>
            {file.project && (
              <Text style={styles.fileProject}>{file.project}</Text>
            )}
          </View>
          <TouchableOpacity style={styles.fileMenu} onPress={onMore}>
            <Ionicons name="ellipsis-vertical" size={20} color={Colors.gray[400]} />
          </TouchableOpacity>
        </View>
        
        {file.tags.length > 0 && (
          <View style={styles.tagsContainer}>
            {file.tags.slice(0, 3).map((tag, index) => (
              <View key={index} style={styles.tag}>
                <Text style={styles.tagText}>{tag}</Text>
              </View>
            ))}
            {file.tags.length > 3 && (
              <Text style={styles.moreTagsText}>+{file.tags.length - 3}</Text>
            )}
          </View>
        )}
      </TouchableOpacity>
    </Animated.View>
  );
};

const ProjectCard: React.FC<{ 
  project: Project; 
  onPress: () => void;
}> = ({ project, onPress }) => {
  const formatFileCount = (count: number) => {
    return `${count} file${count !== 1 ? 's' : ''}`;
  };

  const formatSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  return (
    <TouchableOpacity style={styles.projectCard} onPress={onPress}>
      <LinearGradient
        colors={[project.color, project.color + '80']}
        style={styles.projectGradient}
      >
        <View style={styles.projectHeader}>
          <View style={styles.projectIcon}>
            <Ionicons name="folder" size={24} color="#ffffff" />
          </View>
          <Text style={styles.projectName}>{project.name}</Text>
        </View>
        <Text style={styles.projectDescription} numberOfLines={2}>
          {project.description}
        </Text>
        <View style={styles.projectStats}>
          <Text style={styles.projectStat}>{formatFileCount(project.fileCount)}</Text>
          <Text style={styles.projectSeparator}>•</Text>
          <Text style={styles.projectStat}>{formatSize(project.totalSize)}</Text>
        </View>
      </LinearGradient>
    </TouchableOpacity>
  );
};

const FileActionModal: React.FC<{
  visible: boolean;
  file: FileItem | null;
  onClose: () => void;
  onShare: () => void;
  onDownload: () => void;
  onDelete: () => void;
  onRename: () => void;
  onMove: () => void;
}> = ({ visible, file, onClose, onShare, onDownload, onDelete, onRename, onMove }) => {
  if (!file) return null;

  const actions = [
    { icon: 'eye', title: 'Preview', onPress: onClose },
    { icon: 'share', title: 'Share', onPress: onShare },
    { icon: 'download', title: 'Download', onPress: onDownload },
    { icon: 'create', title: 'Rename', onPress: onRename },
    { icon: 'folder-open', title: 'Move', onPress: onMove },
    { icon: 'trash', title: 'Delete', onPress: onDelete, color: Colors.error },
  ];

  return (
    <Modal visible={visible} animationType="slide" presentationStyle="pageSheet">
      <SafeAreaView style={styles.modalContainer}>
        <View style={styles.modalHeader}>
          <TouchableOpacity onPress={onClose}>
            <Text style={styles.modalCancel}>Cancel</Text>
          </TouchableOpacity>
          <Text style={styles.modalTitle} numberOfLines={1}>{file.name}</Text>
          <View style={{ width: 60 }} />
        </View>

        <ScrollView style={styles.modalContent}>
          <View style={styles.filePreview}>
            <View style={[
              styles.filePreviewIcon, 
              { backgroundColor: FILE_TYPE_COLORS[file.mimeType] || Colors.gray[500] }
            ]}>
              <Ionicons 
                name={FILE_TYPE_ICONS[file.mimeType] || 'document' as any} 
                size={48} 
                color="#ffffff" 
              />
            </View>
            <Text style={styles.filePreviewName}>{file.name}</Text>
            <Text style={styles.filePreviewMeta}>
              {file.type === 'file' && `${(file.size / 1024 / 1024).toFixed(1)} MB • `}
              {file.modifiedAt.toLocaleDateString()}
            </Text>
          </View>

          <View style={styles.actionsGrid}>
            {actions.map((action, index) => (
              <TouchableOpacity
                key={index}
                style={styles.actionItem}
                onPress={() => {
                  action.onPress();
                  onClose();
                }}
              >
                <View style={[
                  styles.actionIcon,
                  { backgroundColor: action.color ? action.color + '20' : Colors.gray[100] }
                ]}>
                  <Ionicons 
                    name={action.icon as any} 
                    size={24} 
                    color={action.color || Colors.gray[600]} 
                  />
                </View>
                <Text style={[
                  styles.actionTitle,
                  { color: action.color || Colors.light.text.primary }
                ]}>
                  {action.title}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </ScrollView>
      </SafeAreaView>
    </Modal>
  );
};

const UploadProgressModal: React.FC<{
  visible: boolean;
  progress: number;
  fileName: string;
  onCancel: () => void;
}> = ({ visible, progress, fileName, onCancel }) => {
  return (
    <Modal visible={visible} transparent animationType="fade">
      <View style={styles.uploadModalOverlay}>
        <View style={styles.uploadModalContent}>
          <View style={styles.uploadHeader}>
            <Text style={styles.uploadTitle}>Uploading</Text>
            <TouchableOpacity onPress={onCancel}>
              <Ionicons name="close" size={24} color={Colors.gray[500]} />
            </TouchableOpacity>
          </View>
          
          <Text style={styles.uploadFileName} numberOfLines={1}>{fileName}</Text>
          
          <View style={styles.progressContainer}>
            <View style={styles.progressBar}>
              <Animated.View 
                style={[
                  styles.progressFill,
                  { width: `${progress}%` }
                ]} 
              />
            </View>
            <Text style={styles.progressText}>{Math.round(progress)}%</Text>
          </View>
        </View>
      </View>
    </Modal>
  );
};

const FilesScreen: React.FC = () => {
  const dispatch = useDispatch();
  const { 
    files, 
    projects, 
    isLoading, 
    uploadProgress, 
    isUploading,
    storageUsed,
    storageLimit
  } = useSelector((state: RootState) => state.files);
  
  const [currentView, setCurrentView] = useState<'recent' | 'projects' | 'shared'>('recent');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFile, setSelectedFile] = useState<FileItem | null>(null);
  const [showActionModal, setShowActionModal] = useState(false);
  const [showUploadProgress, setShowUploadProgress] = useState(false);
  const [uploadingFileName, setUploadingFileName] = useState('');

  useEffect(() => {
    dispatch(loadFiles());
    dispatch(loadProjects());
  }, [dispatch]);

  useEffect(() => {
    setShowUploadProgress(isUploading);
  }, [isUploading]);

  const filteredFiles = files.filter(file => {
    const matchesSearch = file.name.toLowerCase().includes(searchQuery.toLowerCase());
    
    switch (currentView) {
      case 'recent':
        return matchesSearch;
      case 'projects':
        return matchesSearch && file.project;
      case 'shared':
        return matchesSearch && file.isShared;
      default:
        return matchesSearch;
    }
  });

  const handleFileUpload = useCallback(async () => {
    try {
      const result = await DocumentPicker.pick({
        type: [DocumentPicker.types.allFiles],
        allowMultiSelection: true,
      });

      for (const file of result) {
        setUploadingFileName(file.name);
        dispatch(uploadFile({
          uri: file.uri,
          name: file.name,
          type: file.type,
          size: file.size,
        }));
      }
    } catch (error) {
      if (!DocumentPicker.isCancel(error)) {
        Alert.alert('Error', 'Failed to select files');
      }
    }
  }, [dispatch]);

  const handleFilePress = useCallback((file: FileItem) => {
    if (file.type === 'folder') {
      // Navigate to folder contents
      return;
    }
    
    // Preview file
    dispatch(previewFile(file.id));
  }, [dispatch]);

  const handleFileShare = useCallback(async (file: FileItem) => {
    try {
      if (file.downloadUrl) {
        await Share.share({
          url: file.downloadUrl,
          title: file.name,
        });
      } else {
        dispatch(shareFile(file.id));
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to share file');
    }
  }, [dispatch]);

  const handleFileDownload = useCallback(async (file: FileItem) => {
    try {
      dispatch(downloadFile(file.id));
    } catch (error) {
      Alert.alert('Error', 'Failed to download file');
    }
  }, [dispatch]);

  const handleFileDelete = useCallback((file: FileItem) => {
    Alert.alert(
      'Delete File',
      `Are you sure you want to delete "${file.name}"? This action cannot be undone.`,
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Delete', 
          style: 'destructive',
          onPress: () => dispatch(deleteFile(file.id))
        },
      ]
    );
  }, [dispatch]);

  const handleCreateFolder = useCallback(() => {
    Alert.prompt(
      'Create Folder',
      'Enter folder name:',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Create',
          onPress: (folderName) => {
            if (folderName?.trim()) {
              dispatch(createFolder(folderName.trim()));
            }
          }
        },
      ],
      'plain-text'
    );
  }, [dispatch]);

  const storagePercentage = (storageUsed / storageLimit) * 100;

  return (
    <SafeAreaView style={styles.container}>
      <LinearGradient
        colors={[Colors.primary[50], '#ffffff']}
        style={StyleSheet.absoluteFill}
      />

      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Files</Text>
        <View style={styles.headerActions}>
          <TouchableOpacity style={styles.headerAction} onPress={handleCreateFolder}>
            <Ionicons name="folder-outline" size={24} color={Colors.gray[500]} />
          </TouchableOpacity>
          <TouchableOpacity style={styles.headerAction} onPress={handleFileUpload}>
            <LinearGradient
              colors={Colors.gradient.primary}
              style={styles.uploadButtonGradient}
            >
              <Ionicons name="add" size={24} color="#ffffff" />
            </LinearGradient>
          </TouchableOpacity>
        </View>
      </View>

      {/* Search */}
      <View style={styles.searchContainer}>
        <Input
          placeholder="Search files and folders..."
          value={searchQuery}
          onChangeText={setSearchQuery}
          leftIcon="search"
          style={styles.searchInput}
        />
      </View>

      {/* View Tabs */}
      <View style={styles.tabsContainer}>
        {[
          { key: 'recent', title: 'Recent', icon: 'time' },
          { key: 'projects', title: 'Projects', icon: 'folder' },
          { key: 'shared', title: 'Shared', icon: 'people' },
        ].map((tab) => (
          <TouchableOpacity
            key={tab.key}
            style={[
              styles.tab,
              currentView === tab.key && styles.tabActive,
            ]}
            onPress={() => setCurrentView(tab.key as any)}
          >
            <Ionicons 
              name={tab.icon as any} 
              size={16} 
              color={currentView === tab.key ? Colors.primary[500] : Colors.gray[500]} 
            />
            <Text style={[
              styles.tabText,
              currentView === tab.key && styles.tabTextActive,
            ]}>
              {tab.title}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Storage Usage */}
      <View style={styles.storageContainer}>
        <View style={styles.storageInfo}>
          <Text style={styles.storageText}>
            {(storageUsed / 1024 / 1024 / 1024).toFixed(1)} GB of {(storageLimit / 1024 / 1024 / 1024).toFixed(0)} GB used
          </Text>
          <Text style={styles.storagePercentage}>{storagePercentage.toFixed(1)}%</Text>
        </View>
        <View style={styles.storageBar}>
          <Animated.View 
            style={[
              styles.storageBarFill,
              { 
                width: `${Math.min(storagePercentage, 100)}%`,
                backgroundColor: storagePercentage > 90 ? Colors.error : 
                                storagePercentage > 75 ? Colors.warning : Colors.primary[500]
              }
            ]} 
          />
        </View>
      </View>

      {/* Projects Grid (when in projects view) */}
      {currentView === 'projects' && (
        <View style={styles.projectsSection}>
          <ScrollView 
            horizontal 
            showsHorizontalScrollIndicator={false}
            style={styles.projectsContainer}
          >
            {projects.map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                onPress={() => {/* Navigate to project files */}}
              />
            ))}
          </ScrollView>
        </View>
      )}

      {/* Files List */}
      <FlatList
        data={filteredFiles}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <FileCard
            file={item}
            onPress={() => handleFilePress(item)}
            onShare={() => handleFileShare(item)}
            onDelete={() => handleFileDelete(item)}
            onMore={() => {
              setSelectedFile(item);
              setShowActionModal(true);
            }}
          />
        )}
        style={styles.filesList}
        contentContainerStyle={styles.filesContent}
        showsVerticalScrollIndicator={false}
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <View style={styles.emptyIcon}>
              <Ionicons name="folder-open-outline" size={64} color={Colors.gray[300]} />
            </View>
            <Text style={styles.emptyTitle}>No files yet</Text>
            <Text style={styles.emptySubtitle}>
              Upload your first file to get started with file management
            </Text>
            <Button
              title="Upload File"
              onPress={handleFileUpload}
              variant="gradient"
              style={styles.emptyButton}
            />
          </View>
        }
      />

      {/* File Action Modal */}
      <FileActionModal
        visible={showActionModal}
        file={selectedFile}
        onClose={() => setShowActionModal(false)}
        onShare={() => selectedFile && handleFileShare(selectedFile)}
        onDownload={() => selectedFile && handleFileDownload(selectedFile)}
        onDelete={() => selectedFile && handleFileDelete(selectedFile)}
        onRename={() => {/* Implement rename */}}
        onMove={() => {/* Implement move */}}
      />

      {/* Upload Progress Modal */}
      <UploadProgressModal
        visible={showUploadProgress}
        progress={uploadProgress}
        fileName={uploadingFileName}
        onCancel={() => {/* Cancel upload */}}
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.primary[50],
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.lg,
  },
  headerTitle: {
    fontSize: Typography.fontSize['2xl'],
    fontWeight: Typography.fontWeight.bold,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
  },
  headerActions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  headerAction: {
    marginLeft: Spacing.md,
  },
  uploadButtonGradient: {
    width: 44,
    height: 44,
    borderRadius: 22,
    alignItems: 'center',
    justifyContent: 'center',
    ...Shadows.md,
  },
  searchContainer: {
    paddingHorizontal: Spacing.lg,
    marginBottom: Spacing.md,
  },
  searchInput: {
    marginBottom: 0,
  },
  tabsContainer: {
    flexDirection: 'row',
    paddingHorizontal: Spacing.lg,
    marginBottom: Spacing.md,
  },
  tab: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm,
    borderRadius: BorderRadius.full,
    backgroundColor: Colors.gray[100],
    marginRight: Spacing.sm,
  },
  tabActive: {
    backgroundColor: Colors.primary[50],
  },
  tabText: {
    fontSize: Typography.fontSize.sm,
    color: Colors.gray[600],
    fontFamily: Typography.fontFamily.primary,
    fontWeight: Typography.fontWeight.medium,
    marginLeft: Spacing.xs,
  },
  tabTextActive: {
    color: Colors.primary[500],
  },
  storageContainer: {
    paddingHorizontal: Spacing.lg,
    marginBottom: Spacing.md,
  },
  storageInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.xs,
  },
  storageText: {
    fontSize: Typography.fontSize.sm,
    color: Colors.light.text.secondary,
    fontFamily: Typography.fontFamily.primary,
  },
  storagePercentage: {
    fontSize: Typography.fontSize.sm,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
    fontWeight: Typography.fontWeight.medium,
  },
  storageBar: {
    height: 4,
    backgroundColor: Colors.gray[200],
    borderRadius: 2,
    overflow: 'hidden',
  },
  storageBarFill: {
    height: '100%',
    borderRadius: 2,
  },
  projectsSection: {
    marginBottom: Spacing.md,
  },
  projectsContainer: {
    paddingHorizontal: Spacing.lg,
  },
  projectCard: {
    width: 200,
    height: 120,
    borderRadius: BorderRadius.lg,
    marginRight: Spacing.md,
    overflow: 'hidden',
    ...Shadows.sm,
  },
  projectGradient: {
    flex: 1,
    padding: Spacing.md,
    justifyContent: 'space-between',
  },
  projectHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  projectIcon: {
    marginRight: Spacing.sm,
  },
  projectName: {
    fontSize: Typography.fontSize.base,
    fontWeight: Typography.fontWeight.semibold,
    color: '#ffffff',
    fontFamily: Typography.fontFamily.primary,
    flex: 1,
  },
  projectDescription: {
    fontSize: Typography.fontSize.sm,
    color: 'rgba(255, 255, 255, 0.8)',
    fontFamily: Typography.fontFamily.primary,
    marginVertical: Spacing.xs,
  },
  projectStats: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  projectStat: {
    fontSize: Typography.fontSize.xs,
    color: 'rgba(255, 255, 255, 0.9)',
    fontFamily: Typography.fontFamily.primary,
  },
  projectSeparator: {
    fontSize: Typography.fontSize.xs,
    color: 'rgba(255, 255, 255, 0.6)',
    marginHorizontal: Spacing.xs,
  },
  filesList: {
    flex: 1,
  },
  filesContent: {
    paddingHorizontal: Spacing.lg,
    paddingBottom: Spacing.xl,
  },
  fileCard: {
    marginBottom: Spacing.sm,
  },
  fileCardContent: {
    backgroundColor: '#ffffff',
    borderRadius: BorderRadius.lg,
    padding: Spacing.md,
    ...Shadows.sm,
  },
  fileHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  fileIcon: {
    width: 48,
    height: 48,
    borderRadius: BorderRadius.md,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: Spacing.md,
  },
  fileInfo: {
    flex: 1,
  },
  fileName: {
    fontSize: Typography.fontSize.base,
    fontWeight: Typography.fontWeight.medium,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
    marginBottom: 2,
  },
  fileMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 2,
  },
  fileSize: {
    fontSize: Typography.fontSize.xs,
    color: Colors.gray[500],
    fontFamily: Typography.fontFamily.primary,
  },
  fileSeparator: {
    fontSize: Typography.fontSize.xs,
    color: Colors.gray[400],
    marginHorizontal: Spacing.xs,
  },
  fileDate: {
    fontSize: Typography.fontSize.xs,
    color: Colors.gray[500],
    fontFamily: Typography.fontFamily.primary,
  },
  fileProject: {
    fontSize: Typography.fontSize.xs,
    color: Colors.primary[500],
    fontFamily: Typography.fontFamily.primary,
    fontWeight: Typography.fontWeight.medium,
  },
  fileMenu: {
    padding: Spacing.xs,
  },
  tagsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: Spacing.sm,
    paddingTop: Spacing.sm,
    borderTopWidth: 1,
    borderTopColor: Colors.gray[100],
  },
  tag: {
    backgroundColor: Colors.gray[100],
    borderRadius: BorderRadius.sm,
    paddingHorizontal: Spacing.xs,
    paddingVertical: 2,
    marginRight: Spacing.xs,
  },
  tagText: {
    fontSize: Typography.fontSize.xs,
    color: Colors.gray[600],
    fontFamily: Typography.fontFamily.primary,
  },
  moreTagsText: {
    fontSize: Typography.fontSize.xs,
    color: Colors.gray[400],
    fontFamily: Typography.fontFamily.primary,
  },
  emptyState: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: Spacing.xl,
    paddingVertical: Spacing['3xl'],
  },
  emptyIcon: {
    marginBottom: Spacing.lg,
  },
  emptyTitle: {
    fontSize: Typography.fontSize.xl,
    fontWeight: Typography.fontWeight.semibold,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
    marginBottom: Spacing.xs,
  },
  emptySubtitle: {
    fontSize: Typography.fontSize.base,
    color: Colors.light.text.secondary,
    fontFamily: Typography.fontFamily.primary,
    textAlign: 'center',
    lineHeight: Typography.lineHeight.relaxed * Typography.fontSize.base,
    marginBottom: Spacing.xl,
  },
  emptyButton: {
    paddingHorizontal: Spacing.xl,
  },
  modalContainer: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  modalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: Colors.gray[100],
  },
  modalTitle: {
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.semibold,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
    flex: 1,
    textAlign: 'center',
  },
  modalCancel: {
    fontSize: Typography.fontSize.base,
    color: Colors.gray[500],
    fontFamily: Typography.fontFamily.primary,
  },
  modalContent: {
    flex: 1,
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.md,
  },
  filePreview: {
    alignItems: 'center',
    paddingVertical: Spacing.xl,
    borderBottomWidth: 1,
    borderBottomColor: Colors.gray[100],
    marginBottom: Spacing.lg,
  },
  filePreviewIcon: {
    width: 80,
    height: 80,
    borderRadius: BorderRadius.lg,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: Spacing.md,
  },
  filePreviewName: {
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.semibold,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
    textAlign: 'center',
    marginBottom: Spacing.xs,
  },
  filePreviewMeta: {
    fontSize: Typography.fontSize.sm,
    color: Colors.light.text.secondary,
    fontFamily: Typography.fontFamily.primary,
    textAlign: 'center',
  },
  actionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  actionItem: {
    width: (width - Spacing.lg * 3) / 3,
    alignItems: 'center',
    paddingVertical: Spacing.lg,
  },
  actionIcon: {
    width: 56,
    height: 56,
    borderRadius: 28,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: Spacing.sm,
  },
  actionTitle: {
    fontSize: Typography.fontSize.sm,
    fontFamily: Typography.fontFamily.primary,
    textAlign: 'center',
  },
  uploadModalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  uploadModalContent: {
    backgroundColor: '#ffffff',
    borderRadius: BorderRadius.lg,
    padding: Spacing.lg,
    margin: Spacing.lg,
    minWidth: width * 0.8,
    ...Shadows.lg,
  },
  uploadHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.md,
  },
  uploadTitle: {
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.semibold,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
  },
  uploadFileName: {
    fontSize: Typography.fontSize.base,
    color: Colors.light.text.secondary,
    fontFamily: Typography.fontFamily.primary,
    marginBottom: Spacing.lg,
  },
  progressContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  progressBar: {
    flex: 1,
    height: 8,
    backgroundColor: Colors.gray[200],
    borderRadius: 4,
    overflow: 'hidden',
    marginRight: Spacing.md,
  },
  progressFill: {
    height: '100%',
    backgroundColor: Colors.primary[500],
    borderRadius: 4,
  },
  progressText: {
    fontSize: Typography.fontSize.sm,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
    fontWeight: Typography.fontWeight.medium,
    minWidth: 40,
    textAlign: 'right',
  },
});

export default FilesScreen;

