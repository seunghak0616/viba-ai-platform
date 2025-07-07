import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { ApiResponse, AuthTokens } from '@types/index';

// API 기본 설정
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Axios 인스턴스 생성
const createApiClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000, // 30초 타임아웃
    headers: {
      'Content-Type': 'application/json',
    },
    withCredentials: true, // 쿠키 포함
  });

  // 요청 인터셉터
  client.interceptors.request.use(
    (config) => {
      // 인증 토큰 추가
      const tokens = getStoredTokens();
      if (tokens?.token) {
        config.headers.Authorization = `Bearer ${tokens.token}`;
      }

      // 요청 시작 시간 기록 (디버깅용)
      if (import.meta.env.DEV) {
        config.metadata = { startTime: new Date() };
      }

      return config;
    },
    (error) => {
      console.error('Request interceptor error:', error);
      return Promise.reject(error);
    }
  );

  // 응답 인터셉터
  client.interceptors.response.use(
    (response: AxiosResponse) => {
      // 응답 시간 로깅 (개발 환경)
      if (import.meta.env.DEV && response.config.metadata) {
        const endTime = new Date();
        const duration = endTime.getTime() - response.config.metadata.startTime.getTime();
        console.log(`API ${response.config.method?.toUpperCase()} ${response.config.url}: ${duration}ms`);
      }

      return response;
    },
    async (error: AxiosError) => {
      const originalRequest = error.config;

      // 토큰 만료 처리 (401 에러)
      if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
        originalRequest._retry = true;

        try {
          const tokens = getStoredTokens();
          if (tokens?.refreshToken) {
            const newTokens = await refreshAccessToken(tokens.refreshToken);
            setStoredTokens(newTokens);
            
            // 원래 요청 재시도
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${newTokens.token}`;
            }
            return client(originalRequest);
          }
        } catch (refreshError) {
          // 리프레시 토큰도 만료된 경우 로그아웃 처리
          clearStoredTokens();
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      }

      // 네트워크 에러 처리
      if (!error.response) {
        console.error('Network error:', error.message);
        return Promise.reject(new Error('네트워크 연결을 확인해주세요.'));
      }

      // 서버 에러 로깅
      console.error('API Error:', {
        status: error.response.status,
        data: error.response.data,
        url: error.config?.url,
        method: error.config?.method
      });

      return Promise.reject(error);
    }
  );

  return client;
};

// API 클라이언트 인스턴스
const apiClient = createApiClient();

// 토큰 관리 함수들
const TOKEN_STORAGE_KEY = 'bim_auth_tokens';

export const getStoredTokens = (): AuthTokens | null => {
  try {
    const stored = localStorage.getItem(TOKEN_STORAGE_KEY);
    return stored ? JSON.parse(stored) : null;
  } catch (error) {
    console.error('Failed to get stored tokens:', error);
    return null;
  }
};

export const setStoredTokens = (tokens: AuthTokens): void => {
  try {
    localStorage.setItem(TOKEN_STORAGE_KEY, JSON.stringify(tokens));
  } catch (error) {
    console.error('Failed to store tokens:', error);
  }
};

export const clearStoredTokens = (): void => {
  try {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
  } catch (error) {
    console.error('Failed to clear stored tokens:', error);
  }
};

// 토큰 갱신 함수
export const refreshAccessToken = async (refreshToken: string): Promise<AuthTokens> => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/auth/refresh`,
      { refreshToken },
      { timeout: 10000 }
    );

    if (response.data.success && response.data.data.token) {
      return {
        token: response.data.data.token,
        refreshToken: refreshToken // 기존 리프레시 토큰 유지
      };
    }

    throw new Error('Invalid refresh response');
  } catch (error) {
    console.error('Token refresh failed:', error);
    throw error;
  }
};

// API 응답 타입 가드
export const isApiResponse = <T>(data: any): data is ApiResponse<T> => {
  return typeof data === 'object' && data !== null && 'success' in data;
};

// 안전한 API 호출 함수
export const safeApiCall = async <T>(
  apiCall: () => Promise<AxiosResponse<ApiResponse<T>>>
): Promise<T> => {
  try {
    const response = await apiCall();
    
    if (!isApiResponse<T>(response.data)) {
      throw new Error('Invalid API response format');
    }

    if (!response.data.success) {
      throw new Error(response.data.message || response.data.error || 'API call failed');
    }

    if (response.data.data === undefined) {
      throw new Error('No data in API response');
    }

    return response.data.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      // Axios 에러 처리
      if (error.response?.data?.message) {
        throw new Error(error.response.data.message);
      }
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
      if (error.code === 'ECONNABORTED') {
        throw new Error('요청 시간이 초과되었습니다. 다시 시도해주세요.');
      }
      if (error.code === 'ERR_NETWORK') {
        throw new Error('네트워크 연결을 확인해주세요.');
      }
    }
    
    // 일반 에러 처리
    if (error instanceof Error) {
      throw error;
    }
    
    throw new Error('알 수 없는 오류가 발생했습니다.');
  }
};

// 파일 업로드를 위한 특별한 API 호출
export const uploadFile = async (
  url: string,
  file: File,
  onProgress?: (progress: number) => void
): Promise<any> => {
  const formData = new FormData();
  formData.append('file', file);

  const config: AxiosRequestConfig = {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    timeout: 300000, // 5분 타임아웃 (파일 업로드용)
  };

  if (onProgress) {
    config.onUploadProgress = (progressEvent) => {
      if (progressEvent.total) {
        const progress = (progressEvent.loaded / progressEvent.total) * 100;
        onProgress(Math.round(progress));
      }
    };
  }

  return safeApiCall(() => apiClient.post(url, formData, config));
};

// HTTP 메서드별 헬퍼 함수들
export const apiGet = <T>(url: string, config?: AxiosRequestConfig): Promise<T> => {
  return safeApiCall(() => apiClient.get<ApiResponse<T>>(url, config));
};

export const apiPost = <T>(
  url: string,
  data?: any,
  config?: AxiosRequestConfig
): Promise<T> => {
  return safeApiCall(() => apiClient.post<ApiResponse<T>>(url, data, config));
};

export const apiPut = <T>(
  url: string,
  data?: any,
  config?: AxiosRequestConfig
): Promise<T> => {
  return safeApiCall(() => apiClient.put<ApiResponse<T>>(url, data, config));
};

export const apiPatch = <T>(
  url: string,
  data?: any,
  config?: AxiosRequestConfig
): Promise<T> => {
  return safeApiCall(() => apiClient.patch<ApiResponse<T>>(url, data, config));
};

export const apiDelete = <T>(url: string, config?: AxiosRequestConfig): Promise<T> => {
  return safeApiCall(() => apiClient.delete<ApiResponse<T>>(url, config));
};

// 쿼리 파라미터 생성 헬퍼
export const buildQueryString = (params: Record<string, any>): string => {
  const searchParams = new URLSearchParams();
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      if (Array.isArray(value)) {
        value.forEach(v => searchParams.append(key, String(v)));
      } else {
        searchParams.append(key, String(value));
      }
    }
  });
  
  const queryString = searchParams.toString();
  return queryString ? `?${queryString}` : '';
};

// 에러 메시지 표준화 함수
export const getErrorMessage = (error: unknown): string => {
  if (typeof error === 'string') {
    return error;
  }
  
  if (error instanceof Error) {
    return error.message;
  }
  
  if (axios.isAxiosError(error)) {
    if (error.response?.data?.message) {
      return error.response.data.message;
    }
    if (error.response?.data?.error) {
      return error.response.data.error;
    }
    return error.message;
  }
  
  return '알 수 없는 오류가 발생했습니다.';
};

// 개발 환경에서만 사용되는 API 디버깅 함수
export const enableApiDebugging = (): void => {
  if (import.meta.env.DEV) {
    // 요청/응답 로깅
    apiClient.interceptors.request.use(request => {
      console.log('API Request:', {
        method: request.method?.toUpperCase(),
        url: request.url,
        data: request.data,
        headers: request.headers
      });
      return request;
    });

    apiClient.interceptors.response.use(
      response => {
        console.log('API Response:', {
          status: response.status,
          data: response.data,
          url: response.config.url
        });
        return response;
      },
      error => {
        console.error('API Error:', {
          status: error.response?.status,
          data: error.response?.data,
          message: error.message,
          url: error.config?.url
        });
        return Promise.reject(error);
      }
    );
  }
};

// 개발 환경에서 디버깅 활성화
if (import.meta.env.DEV) {
  enableApiDebugging();
}

export default apiClient;