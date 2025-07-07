import axios from 'axios';
import { LoginCredentials, RegisterCredentials, LoginResponse, User } from '../types/auth';

// Axios 인스턴스 생성
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터 - 토큰 자동 추가
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('viba_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터 - 401 에러 시 로그아웃
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('viba_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authService = {
  // 로그인
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    
    return response.data;
  },

  // 회원가입
  async register(credentials: RegisterCredentials): Promise<User> {
    const response = await api.post('/auth/register', credentials);
    return response.data;
  },

  // 현재 사용자 정보 가져오기
  async getCurrentUser(): Promise<User> {
    const response = await api.get('/auth/me');
    return response.data;
  },

  // 로그아웃 (클라이언트 사이드만)
  logout(): void {
    localStorage.removeItem('viba_token');
  },
};

// API 인스턴스도 내보내기 (다른 서비스에서 사용)
export { api };