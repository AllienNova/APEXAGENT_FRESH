import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { FilesState, FileItem, UploadProgress } from '../../types';
import { apiService } from '../../services/api.service';

const initialState: FilesState = {
  files: [],
  uploadProgress: {},
  selectedFiles: [],
  isLoading: false,
  error: null,
  lastUpdated: null,
};

export const loadFiles = createAsyncThunk(
  'files/loadFiles',
  async (_, { rejectWithValue }) => {
    try {
      const files = await apiService.getFiles();
      return files;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to load files');
    }
  }
);

export const uploadFile = createAsyncThunk(
  'files/uploadFile',
  async (
    { file, onProgress }: { file: { uri: string; type: string; name: string }; onProgress?: (progress: number) => void },
    { rejectWithValue, dispatch }
  ) => {
    try {
      const fileId = Date.now().toString();
      
      // Initialize upload progress
      dispatch(setUploadProgress({ fileId, progress: 0, status: 'uploading' }));

      // Simulate progress updates (in real implementation, this would come from the upload service)
      const progressInterval = setInterval(() => {
        dispatch(updateUploadProgress({ fileId, progress: Math.min(90, Math.random() * 90) }));
      }, 500);

      const result = await apiService.uploadFile(file);
      
      clearInterval(progressInterval);
      dispatch(setUploadProgress({ fileId, progress: 100, status: 'completed' }));

      return {
        ...result,
        fileId,
        file: {
          id: result.fileId,
          name: file.name,
          type: file.type.startsWith('image/') ? 'image' as const : 'document' as const,
          size: 0, // Would be provided by the API
          mimeType: file.type,
          url: result.url,
          uploadedAt: new Date().toISOString(),
          uploadedBy: 'current-user', // Would come from auth state
          tags: [],
          metadata: {
            checksum: '',
          },
          status: 'ready' as const,
        },
      };
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to upload file');
    }
  }
);

export const deleteFile = createAsyncThunk(
  'files/deleteFile',
  async (fileId: string, { rejectWithValue }) => {
    try {
      await apiService.deleteFile(fileId);
      return fileId;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to delete file');
    }
  }
);

const filesSlice = createSlice({
  name: 'files',
  initialState,
  reducers: {
    setSelectedFiles: (state, action: PayloadAction<string[]>) => {
      state.selectedFiles = action.payload;
    },
    toggleFileSelection: (state, action: PayloadAction<string>) => {
      const fileId = action.payload;
      if (state.selectedFiles.includes(fileId)) {
        state.selectedFiles = state.selectedFiles.filter(id => id !== fileId);
      } else {
        state.selectedFiles.push(fileId);
      }
    },
    clearFileSelection: (state) => {
      state.selectedFiles = [];
    },
    setUploadProgress: (state, action: PayloadAction<UploadProgress>) => {
      state.uploadProgress[action.payload.fileId] = action.payload;
    },
    updateUploadProgress: (state, action: PayloadAction<{ fileId: string; progress: number }>) => {
      const { fileId, progress } = action.payload;
      if (state.uploadProgress[fileId]) {
        state.uploadProgress[fileId].progress = progress;
      }
    },
    removeUploadProgress: (state, action: PayloadAction<string>) => {
      delete state.uploadProgress[action.payload];
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // Load Files
    builder
      .addCase(loadFiles.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(loadFiles.fulfilled, (state, action) => {
        state.isLoading = false;
        state.files = action.payload;
        state.lastUpdated = new Date().toISOString();
      })
      .addCase(loadFiles.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Upload File
    builder
      .addCase(uploadFile.pending, (state) => {
        state.error = null;
      })
      .addCase(uploadFile.fulfilled, (state, action) => {
        const { file, fileId } = action.payload;
        state.files.unshift(file);
        // Remove upload progress after successful upload
        setTimeout(() => {
          delete state.uploadProgress[fileId];
        }, 2000);
      })
      .addCase(uploadFile.rejected, (state, action) => {
        state.error = action.payload as string;
      });

    // Delete File
    builder
      .addCase(deleteFile.fulfilled, (state, action) => {
        state.files = state.files.filter(file => file.id !== action.payload);
        state.selectedFiles = state.selectedFiles.filter(id => id !== action.payload);
      });
  },
});

export const {
  setSelectedFiles,
  toggleFileSelection,
  clearFileSelection,
  setUploadProgress,
  updateUploadProgress,
  removeUploadProgress,
  clearError,
} = filesSlice.actions;

export default filesSlice.reducer;

