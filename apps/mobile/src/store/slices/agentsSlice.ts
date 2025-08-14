import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { AgentsState, Agent } from '../../types';
import { apiService } from '../../services/api.service';

const initialState: AgentsState = {
  agents: [],
  selectedAgent: null,
  isLoading: false,
  error: null,
  lastUpdated: null,
};

export const loadAgents = createAsyncThunk(
  'agents/loadAgents',
  async (_, { rejectWithValue }) => {
    try {
      const agents = await apiService.getAgents();
      return agents;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to load agents');
    }
  }
);

export const createAgent = createAsyncThunk(
  'agents/createAgent',
  async (agentData: Partial<Agent>, { rejectWithValue }) => {
    try {
      const agent = await apiService.createAgent(agentData);
      return agent;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to create agent');
    }
  }
);

export const updateAgent = createAsyncThunk(
  'agents/updateAgent',
  async ({ agentId, agentData }: { agentId: string; agentData: Partial<Agent> }, { rejectWithValue }) => {
    try {
      await apiService.updateAgent(agentId, agentData);
      return { agentId, agentData };
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to update agent');
    }
  }
);

export const deleteAgent = createAsyncThunk(
  'agents/deleteAgent',
  async (agentId: string, { rejectWithValue }) => {
    try {
      await apiService.deleteAgent(agentId);
      return agentId;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to delete agent');
    }
  }
);

const agentsSlice = createSlice({
  name: 'agents',
  initialState,
  reducers: {
    setSelectedAgent: (state, action: PayloadAction<Agent | null>) => {
      state.selectedAgent = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
    updateAgentStatus: (state, action: PayloadAction<{ agentId: string; status: Agent['status'] }>) => {
      const { agentId, status } = action.payload;
      const agent = state.agents.find(a => a.id === agentId);
      if (agent) {
        agent.status = status;
        agent.updatedAt = new Date().toISOString();
      }
    },
  },
  extraReducers: (builder) => {
    // Load Agents
    builder
      .addCase(loadAgents.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(loadAgents.fulfilled, (state, action) => {
        state.isLoading = false;
        state.agents = action.payload;
        state.lastUpdated = new Date().toISOString();
      })
      .addCase(loadAgents.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Create Agent
    builder
      .addCase(createAgent.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(createAgent.fulfilled, (state, action) => {
        state.isLoading = false;
        state.agents.unshift(action.payload);
      })
      .addCase(createAgent.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Update Agent
    builder
      .addCase(updateAgent.fulfilled, (state, action) => {
        const { agentId, agentData } = action.payload;
        const agent = state.agents.find(a => a.id === agentId);
        if (agent) {
          Object.assign(agent, agentData);
          agent.updatedAt = new Date().toISOString();
        }
      });

    // Delete Agent
    builder
      .addCase(deleteAgent.fulfilled, (state, action) => {
        state.agents = state.agents.filter(agent => agent.id !== action.payload);
        if (state.selectedAgent?.id === action.payload) {
          state.selectedAgent = null;
        }
      });
  },
});

export const { setSelectedAgent, clearError, updateAgentStatus } = agentsSlice.actions;
export default agentsSlice.reducer;

