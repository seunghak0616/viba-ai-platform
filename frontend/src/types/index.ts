// API 응답 타입
export interface ApiResponse<T = any> {
  success: boolean;
  message?: string;
  data?: T;
  error?: string;
  errors?: Record<string, string[]>;
}

// 페이지네이션 타입
export interface Pagination {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

// 사용자 관련 타입
export type UserRole = 'USER' | 'PREMIUM' | 'ADMIN' | 'ARCHITECT';

export interface User {
  id: string;
  email: string;
  name: string;
  company?: string;
  role: UserRole;
  isActive: boolean;
  emailVerified: boolean;
  preferences?: Record<string, any>;
  subscription?: Record<string, any>;
  createdAt: string;
  updatedAt: string;
  lastLoginAt?: string;
}

// 인증 관련 타입
export interface AuthTokens {
  token: string;
  refreshToken: string;
}

export interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// 프로젝트 관련 타입
export type ProjectStatus = 'DRAFT' | 'IN_PROGRESS' | 'REVIEW' | 'COMPLETED' | 'ARCHIVED';

export interface Project {
  id: string;
  name: string;
  description?: string;
  status: ProjectStatus;
  metadata?: Record<string, any>;
  settings?: Record<string, any>;
  userId: string;
  createdAt: string;
  updatedAt: string;
  user?: Pick<User, 'id' | 'name' | 'email'>;
  bimModels?: BimModel[];
  collaborators?: Collaboration[];
  _count?: {
    bimModels: number;
    collaborators: number;
  };
}

// BIM 모델 관련 타입
export type BimModelType = 'APARTMENT' | 'HOUSE' | 'OFFICE' | 'COMMERCIAL' | 'INDUSTRIAL' | 'CUSTOM';

export interface BimModel {
  id: string;
  name: string;
  description?: string;
  type: BimModelType;
  naturalLanguageInput?: string;
  processedParams?: Record<string, any>;
  geometryData?: Record<string, any>;
  materials?: Record<string, any>;
  dimensions?: Record<string, any>;
  spatial?: Record<string, any>;
  metadata?: Record<string, any>;
  properties?: Record<string, any>;
  constraints?: Record<string, any>;
  ifcFileUrl?: string;
  thumbnailUrl?: string;
  previewUrl?: string;
  version: number;
  parentId?: string;
  isPublic: boolean;
  isTemplate: boolean;
  userId: string;
  projectId: string;
  createdAt: string;
  updatedAt: string;
  user?: Pick<User, 'id' | 'name' | 'email'>;
  project?: Pick<Project, 'id' | 'name' | 'status'>;
  parent?: Pick<BimModel, 'id' | 'name' | 'version'>;
  children?: Pick<BimModel, 'id' | 'name' | 'version' | 'createdAt'>[];
  files?: ProjectFile[];
  _count?: {
    children: number;
  };
}

// 파일 관련 타입
export type FileType = 'IFC' | 'DWG' | 'DXF' | 'PDF' | 'IMAGE' | 'MODEL';

export interface ProjectFile {
  id: string;
  filename: string;
  originalName: string;
  mimeType: string;
  size: number;
  fileType: FileType;
  url: string;
  metadata?: Record<string, any>;
  userId: string;
  projectId: string;
  bimModelId?: string;
  createdAt: string;
  updatedAt: string;
}

// 협업 관련 타입
export type CollaborationRole = 'VIEWER' | 'EDITOR' | 'ADMIN';

export interface Collaboration {
  id: string;
  userId: string;
  projectId: string;
  role: CollaborationRole;
  permissions?: Record<string, any>;
  invitedBy?: string;
  invitedAt?: string;
  acceptedAt?: string;
  createdAt: string;
  updatedAt: string;
  user?: Pick<User, 'id' | 'name' | 'email'>;
  project?: Pick<Project, 'id' | 'name'>;
}

// 활동 로그 타입
export interface ActivityLog {
  id: string;
  action: string;
  details?: Record<string, any>;
  ipAddress?: string;
  userAgent?: string;
  userId: string;
  projectId?: string;
  bimModelId?: string;
  createdAt: string;
  user?: Pick<User, 'id' | 'name'>;
  project?: Pick<Project, 'id' | 'name'>;
  bimModel?: Pick<BimModel, 'id' | 'name'>;
}

// NLP 처리 관련 타입
export interface NaturalLanguageRequest {
  input: string;
  context?: Record<string, any>;
  language?: string;
}

export interface ProcessedBimParams {
  buildingType: BimModelType;
  totalArea: {
    value: number;
    unit: '평' | 'm2';
    confidence: number;
  };
  rooms: Array<{
    type: string;
    count: number;
    area?: number;
    orientation?: string;
    requirements?: string[];
  }>;
  orientation: {
    primary: string;
    secondary?: string;
    confidence: number;
  };
  constraints: {
    budget?: number;
    timeframe?: string;
    regulations?: string[];
    preferences?: string[];
  };
  dimensions: {
    length?: number;
    width?: number;
    height?: number;
    floors?: number;
  };
  specialRequirements?: string[];
  confidence: number;
  language: string;
  processedAt: string;
}

// 최적화 관련 타입
export interface OptimizationSuggestion {
  category: string;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  title: string;
  description: string;
  impact: string;
  implementation: string;
  estimatedCost?: number;
  estimatedSavings?: number;
  difficulty: 'EASY' | 'MEDIUM' | 'HARD';
}

export interface OptimizationResult {
  overallScore: number;
  suggestions: OptimizationSuggestion[];
  compliance: {
    buildingCode: boolean;
    fireCode: boolean;
    accessibilityCode: boolean;
    issues: string[];
  };
  efficiency: {
    spaceUtilization: number;
    energyEfficiency: number;
    costEfficiency: number;
  };
  processedAt: string;
}

// 검증 관련 타입
export interface ValidationIssue {
  category: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  code: string;
  description: string;
  suggestion: string;
  location: string;
}

export interface ValidationResult {
  isValid: boolean;
  complianceScore: number;
  issues: ValidationIssue[];
  compliance: {
    buildingCode: { passed: boolean; details: string };
    fireCode: { passed: boolean; details: string };
    accessibility: { passed: boolean; details: string };
    structural: { passed: boolean; details: string };
    environmental: { passed: boolean; details: string };
  };
  recommendations: string[];
  processedAt: string;
}

// 3D 뷰어 관련 타입
export interface ViewerSettings {
  showGrid: boolean;
  showAxes: boolean;
  wireframe: boolean;
  shadows: boolean;
  lightIntensity: number;
  cameraPosition: { x: number; y: number; z: number };
  cameraTarget: { x: number; y: number; z: number };
}

export interface ViewerState {
  isLoading: boolean;
  error?: string;
  settings: ViewerSettings;
  selectedObjects: string[];
  highlightedObjects: string[];
}

// 채팅 관련 타입
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface ChatSession {
  id: string;
  projectId?: string;
  bimModelId?: string;
  messages: ChatMessage[];
  createdAt: string;
  updatedAt: string;
}

// 에러 타입
export interface AppError {
  code: string;
  message: string;
  details?: Record<string, any>;
  timestamp: string;
}

// 폼 관련 타입
export interface FormErrors {
  [field: string]: string | string[] | undefined;
}

export interface FormState<T = Record<string, any>> {
  data: T;
  errors: FormErrors;
  isSubmitting: boolean;
  isValid: boolean;
}

// 검색 및 필터링 타입
export interface SearchFilters {
  query?: string;
  type?: BimModelType | BimModelType[];
  status?: ProjectStatus | ProjectStatus[];
  dateRange?: {
    start: string;
    end: string;
  };
  tags?: string[];
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

// 알림 타입
export type NotificationType = 'success' | 'error' | 'warning' | 'info';

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  duration?: number;
  actions?: Array<{
    label: string;
    action: () => void;
  }>;
}

// 사용 통계 타입
export interface UsageStats {
  id: string;
  date: string;
  userId?: string;
  apiCalls: number;
  modelsGenerated: number;
  filesUploaded: number;
  storageUsed: number;
  createdAt: string;
}

// WebSocket 이벤트 타입
export interface SocketEvent {
  type: string;
  data: any;
  timestamp: string;
  userId?: string;
  projectId?: string;
}

// 유틸리티 타입들
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;
export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;
export type PartialExcept<T, K extends keyof T> = Partial<T> & Pick<T, K>;

// 환경 변수 타입
export interface EnvironmentConfig {
  NODE_ENV: 'development' | 'production' | 'test';
  VITE_API_URL: string;
  VITE_APP_VERSION: string;
  VITE_ENABLE_DEVTOOLS: boolean;
  VITE_SENTRY_DSN?: string;
}