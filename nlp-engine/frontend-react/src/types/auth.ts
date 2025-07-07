// 사용자 타입 정의
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

// 인증 상태 타입
export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

// 로그인 자격 증명
export interface LoginCredentials {
  username: string;
  password: string;
}

// 회원가입 자격 증명
export interface RegisterCredentials {
  username: string;
  email: string;
  password: string;
  full_name?: string;
  company?: string;
  role?: string;
}

// 로그인 응답
export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// API 에러 응답
export interface APIError {
  detail: string;
  status_code?: number;
}