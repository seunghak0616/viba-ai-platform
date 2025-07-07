import axios, { AxiosInstance, AxiosResponse } from 'axios';

// API 베이스 URL
const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Axios 인스턴스 생성
const api: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 토큰 관리
let authToken: string | null = localStorage.getItem('auth_token');

// 요청 인터셉터 - 인증 토큰 자동 추가
api.interceptors.request.use(
  (config) => {
    if (authToken) {
      config.headers.Authorization = `Bearer ${authToken}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터 - 에러 처리
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // 토큰 만료 시 로그아웃 처리
      logout();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// 토큰 설정 함수
export const setAuthToken = (token: string) => {
  authToken = token;
  localStorage.setItem('auth_token', token);
};

// 로그아웃 함수
export const logout = () => {
  authToken = null;
  localStorage.removeItem('auth_token');
};

// 타입 정의들
export interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  company?: string;
  role: string;
  created_at: string;
  last_active: string;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  building_type: string;
  location?: string;
  area?: number;
  floors?: number;
  budget?: number;
  owner_id: string;
  created_at: string;
  updated_at: string;
  status: string;
}

export interface AIAgent {
  name: string;
  description: string;
  capabilities: string[];
  system_prompt: string;
  specialty: string;
  status: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  response_time?: number;
}

export interface ChatSession {
  session_id: string;
  agent_id: string;
  user_id: string;
  context: any;
  started_at: string;
  message_history: ChatMessage[];
  status: string;
}

export interface AnalysisRequest {
  request_type: string;
  content: string;
  building_type: string;
  location: string;
  area: number;
  floors: number;
  budget: number;
  sustainability: string;
  style: string;
  special_requirements: string[];
}

export interface AnalysisResult {
  analysis_id: string;
  status: string;
  results: any;
  overall_score: number;
  processing_time: number;
  timestamp: string;
}

// API 함수들
export const authAPI = {
  // 로그인
  login: async (username: string, password: string) => {
    const response = await api.post('/auth/login', { username, password });
    const { access_token, user } = response.data;
    setAuthToken(access_token);
    return { token: access_token, user };
  },

  // 회원가입
  register: async (userData: {
    username: string;
    email: string;
    password: string;
    full_name?: string;
    company?: string;
    role?: string;
  }) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  // 현재 사용자 정보
  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

export const projectAPI = {
  // 프로젝트 목록 조회
  getProjects: async (): Promise<Project[]> => {
    const response = await api.get('/projects');
    return response.data;
  },

  // 프로젝트 생성
  createProject: async (projectData: {
    name: string;
    description?: string;
    building_type: string;
    location?: string;
    area?: number;
    floors?: number;
    budget?: number;
  }): Promise<Project> => {
    const response = await api.post('/projects', projectData);
    return response.data;
  },

  // 프로젝트 상세 조회
  getProject: async (projectId: string): Promise<Project> => {
    const response = await api.get(`/projects/${projectId}`);
    return response.data;
  },
};

export const aiAPI = {
  // 모든 AI 에이전트 조회
  getAgents: async () => {
    const response = await api.get('/api/ai/agents');
    return response.data;
  },

  // 특정 AI 에이전트 정보 조회
  getAgent: async (agentId: string) => {
    const response = await api.get(`/api/ai/agents/${agentId}`);
    return response.data;
  },

  // 채팅 세션 시작
  startChatSession: async (agentId: string, context?: any) => {
    const response = await api.post('/api/ai/chat/start', {
      agent_id: agentId,
      context,
    });
    return response.data;
  },

  // 메시지 전송
  sendMessage: async (sessionId: string, message: string) => {
    const response = await api.post('/api/ai/chat/message', {
      session_id: sessionId,
      message,
    });
    return response.data;
  },

  // 채팅 세션 종료
  endChatSession: async (sessionId: string) => {
    const response = await api.post('/api/ai/chat/end', null, {
      params: { session_id: sessionId },
    });
    return response.data;
  },

  // 종합 설계 분석
  runComprehensiveAnalysis: async (analysisData: AnalysisRequest): Promise<AnalysisResult> => {
    const response = await api.post('/api/ai/analysis/comprehensive', analysisData);
    return response.data;
  },

  // 분석 결과 조회
  getAnalysisResult: async (analysisId: string) => {
    const response = await api.get(`/api/ai/analysis/${analysisId}`);
    return response.data;
  },

  // 세션 정보 조회
  getSessionInfo: async (sessionId: string) => {
    const response = await api.get(`/api/ai/sessions/${sessionId}`);
    return response.data;
  },

  // AI 통계 조회
  getAIStats: async () => {
    const response = await api.get('/api/ai/stats');
    return response.data;
  },
};

// WebSocket 연결 관리
export class WebSocketManager {
  private ws: WebSocket | null = null;
  private userId: string | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 3000;
  private messageHandlers: Map<string, (data: any) => void> = new Map();

  constructor() {
    this.connect = this.connect.bind(this);
    this.disconnect = this.disconnect.bind(this);
    this.sendMessage = this.sendMessage.bind(this);
    this.addMessageHandler = this.addMessageHandler.bind(this);
    this.removeMessageHandler = this.removeMessageHandler.bind(this);
  }

  connect(userId: string) {
    this.userId = userId;
    const wsUrl = `ws://localhost:8000/api/ai/ws/${userId}`;

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('WebSocket 연결됨');
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        } catch (error) {
          console.error('WebSocket 메시지 파싱 오류:', error);
        }
      };

      this.ws.onclose = () => {
        console.log('WebSocket 연결 해제됨');
        this.attemptReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket 오류:', error);
      };
    } catch (error) {
      console.error('WebSocket 연결 실패:', error);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  sendMessage(type: string, data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const message = {
        type,
        ...data,
        timestamp: new Date().toISOString(),
      };
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket이 연결되지 않음');
    }
  }

  addMessageHandler(type: string, handler: (data: any) => void) {
    this.messageHandlers.set(type, handler);
  }

  removeMessageHandler(type: string) {
    this.messageHandlers.delete(type);
  }

  private handleMessage(data: any) {
    const handler = this.messageHandlers.get(data.type);
    if (handler) {
      handler(data);
    } else {
      console.log('처리되지 않은 메시지:', data);
    }
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts && this.userId) {
      this.reconnectAttempts++;
      console.log(`재연결 시도 ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
      
      setTimeout(() => {
        this.connect(this.userId!);
      }, this.reconnectInterval);
    }
  }
}

// 전역 WebSocket 인스턴스
export const wsManager = new WebSocketManager();

// 헬스체크
export const healthCheck = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    throw new Error('서버에 연결할 수 없습니다');
  }
};

export default api;