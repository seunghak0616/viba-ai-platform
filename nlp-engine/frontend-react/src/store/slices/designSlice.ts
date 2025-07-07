import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface DesignRequest {
  id: string;
  project_id: string;
  request_type: string;
  content: string;
  context?: Record<string, any>;
  priority: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
}

export interface DesignResponse {
  id: string;
  request_id: string;
  content: string;
  recommendations: any[];
  execution_time: number;
  quality_score: number;
  created_at: string;
}

interface DesignState {
  requests: DesignRequest[];
  responses: DesignResponse[];
  currentRequest: DesignRequest | null;
  isProcessing: boolean;
  error: string | null;
}

const initialState: DesignState = {
  requests: [],
  responses: [],
  currentRequest: null,
  isProcessing: false,
  error: null,
};

const designSlice = createSlice({
  name: 'design',
  initialState,
  reducers: {
    addRequest: (state, action: PayloadAction<DesignRequest>) => {
      state.requests.push(action.payload);
    },
    updateRequestStatus: (
      state,
      action: PayloadAction<{ id: string; status: DesignRequest['status'] }>
    ) => {
      const request = state.requests.find(r => r.id === action.payload.id);
      if (request) {
        request.status = action.payload.status;
      }
    },
    addResponse: (state, action: PayloadAction<DesignResponse>) => {
      state.responses.push(action.payload);
    },
    setCurrentRequest: (state, action: PayloadAction<DesignRequest | null>) => {
      state.currentRequest = action.payload;
    },
    setProcessing: (state, action: PayloadAction<boolean>) => {
      state.isProcessing = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    clearRequests: (state) => {
      state.requests = [];
      state.responses = [];
      state.currentRequest = null;
    },
  },
});

export const {
  addRequest,
  updateRequestStatus,
  addResponse,
  setCurrentRequest,
  setProcessing,
  setError,
  clearRequests,
} = designSlice.actions;

export default designSlice.reducer;