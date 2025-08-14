import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { ProjectsState, Project } from '../../types';
import { apiService } from '../../services/api.service';

const initialState: ProjectsState = {
  projects: [],
  activeProject: null,
  isLoading: false,
  error: null,
  lastUpdated: null,
};

export const loadProjects = createAsyncThunk(
  'projects/loadProjects',
  async (_, { rejectWithValue }) => {
    try {
      const projects = await apiService.getProjects();
      return projects;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to load projects');
    }
  }
);

export const createProject = createAsyncThunk(
  'projects/createProject',
  async (projectData: Partial<Project>, { rejectWithValue }) => {
    try {
      const project = await apiService.createProject(projectData);
      return project;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to create project');
    }
  }
);

export const updateProject = createAsyncThunk(
  'projects/updateProject',
  async ({ projectId, projectData }: { projectId: string; projectData: Partial<Project> }, { rejectWithValue }) => {
    try {
      await apiService.updateProject(projectId, projectData);
      return { projectId, projectData };
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to update project');
    }
  }
);

export const deleteProject = createAsyncThunk(
  'projects/deleteProject',
  async (projectId: string, { rejectWithValue }) => {
    try {
      await apiService.deleteProject(projectId);
      return projectId;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to delete project');
    }
  }
);

const projectsSlice = createSlice({
  name: 'projects',
  initialState,
  reducers: {
    setActiveProject: (state, action: PayloadAction<Project | null>) => {
      state.activeProject = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
    updateProjectStatus: (state, action: PayloadAction<{ projectId: string; status: Project['status'] }>) => {
      const { projectId, status } = action.payload;
      const project = state.projects.find(p => p.id === projectId);
      if (project) {
        project.status = status;
        project.updatedAt = new Date().toISOString();
      }
    },
    addConversationToProject: (state, action: PayloadAction<{ projectId: string; conversationId: string }>) => {
      const { projectId, conversationId } = action.payload;
      const project = state.projects.find(p => p.id === projectId);
      if (project && !project.conversations.includes(conversationId)) {
        project.conversations.push(conversationId);
        project.updatedAt = new Date().toISOString();
      }
    },
    removeConversationFromProject: (state, action: PayloadAction<{ projectId: string; conversationId: string }>) => {
      const { projectId, conversationId } = action.payload;
      const project = state.projects.find(p => p.id === projectId);
      if (project) {
        project.conversations = project.conversations.filter(id => id !== conversationId);
        project.updatedAt = new Date().toISOString();
      }
    },
    addFileToProject: (state, action: PayloadAction<{ projectId: string; fileId: string }>) => {
      const { projectId, fileId } = action.payload;
      const project = state.projects.find(p => p.id === projectId);
      if (project && !project.files.includes(fileId)) {
        project.files.push(fileId);
        project.updatedAt = new Date().toISOString();
      }
    },
    removeFileFromProject: (state, action: PayloadAction<{ projectId: string; fileId: string }>) => {
      const { projectId, fileId } = action.payload;
      const project = state.projects.find(p => p.id === projectId);
      if (project) {
        project.files = project.files.filter(id => id !== fileId);
        project.updatedAt = new Date().toISOString();
      }
    },
  },
  extraReducers: (builder) => {
    // Load Projects
    builder
      .addCase(loadProjects.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(loadProjects.fulfilled, (state, action) => {
        state.isLoading = false;
        state.projects = action.payload;
        state.lastUpdated = new Date().toISOString();
      })
      .addCase(loadProjects.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Create Project
    builder
      .addCase(createProject.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(createProject.fulfilled, (state, action) => {
        state.isLoading = false;
        state.projects.unshift(action.payload);
        state.activeProject = action.payload;
      })
      .addCase(createProject.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Update Project
    builder
      .addCase(updateProject.fulfilled, (state, action) => {
        const { projectId, projectData } = action.payload;
        const project = state.projects.find(p => p.id === projectId);
        if (project) {
          Object.assign(project, projectData);
          project.updatedAt = new Date().toISOString();
        }
        if (state.activeProject?.id === projectId) {
          Object.assign(state.activeProject, projectData);
          state.activeProject.updatedAt = new Date().toISOString();
        }
      });

    // Delete Project
    builder
      .addCase(deleteProject.fulfilled, (state, action) => {
        state.projects = state.projects.filter(project => project.id !== action.payload);
        if (state.activeProject?.id === action.payload) {
          state.activeProject = null;
        }
      });
  },
});

export const {
  setActiveProject,
  clearError,
  updateProjectStatus,
  addConversationToProject,
  removeConversationFromProject,
  addFileToProject,
  removeFileFromProject,
} = projectsSlice.actions;

export default projectsSlice.reducer;

