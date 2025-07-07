import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { User, AuthState, LoginCredentials, RegisterCredentials } from '../types/auth';
import { authService } from '../services/authService';
import toast from 'react-hot-toast';

// Auth Context 타입 (강화된 버전)
interface AuthContextType {
  state: AuthState;
  permissions: string[];
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (credentials: RegisterCredentials) => Promise<void>;
  logout: () => void;
  updateUser: (user: Partial<User>) => void;
  refreshToken: () => Promise<boolean>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>;
  updateProfile: (profileData: Partial<User>) => Promise<void>;
  hasPermission: (permission: string) => boolean;
  hasRole: (role: string) => boolean;
  hasAnyRole: (roles: string[]) => boolean;
}

// Auth Reducer 액션 타입 (강화된 버전)
type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: { user: User; token: string; refreshToken: string; sessionId: string; permissions: string[] } }
  | { type: 'AUTH_FAILURE'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'UPDATE_USER'; payload: Partial<User> }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_PERMISSIONS'; payload: string[] }
  | { type: 'UPDATE_TOKEN'; payload: string };

// 초기 상태 (강화된 버전)
const initialState: AuthState = {
  user: null,
  token: localStorage.getItem('access_token'),
  isAuthenticated: false,
  isLoading: true,
  error: null,
};

// 초기 권한 상태
const initialPermissions: string[] = JSON.parse(localStorage.getItem('user_permissions') || '[]');

// Auth Reducer
function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'AUTH_START':
      return {
        ...state,
        isLoading: true,
        error: null,
      };
    case 'AUTH_SUCCESS':
      // 토큰들을 localStorage에 저장
      localStorage.setItem('access_token', action.payload.token);
      localStorage.setItem('refresh_token', action.payload.refreshToken);
      localStorage.setItem('session_id', action.payload.sessionId);
      localStorage.setItem('user_permissions', JSON.stringify(action.payload.permissions));
      
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };
    case 'AUTH_FAILURE':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload,
      };
    case 'LOGOUT':
      // 모든 인증 관련 데이터 삭제
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('session_id');
      localStorage.removeItem('user_permissions');
      
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      };
    case 'UPDATE_USER':
      return {
        ...state,
        user: state.user ? { ...state.user, ...action.payload } : null,
      };
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };
    case 'SET_PERMISSIONS':
      localStorage.setItem('user_permissions', JSON.stringify(action.payload));
      return state;
    case 'UPDATE_TOKEN':
      localStorage.setItem('access_token', action.payload);
      return {
        ...state,
        token: action.payload,
      };
    default:
      return state;
  }
}

// Context 생성
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider 컴포넌트
interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [state, dispatch] = useReducer(authReducer, initialState);
  const [permissions, setPermissions] = React.useState<string[]>(initialPermissions);

  // 토큰 자동 갱신 기능
  const refreshToken = async (): Promise<boolean> => {
    try {
      const refreshTokenValue = localStorage.getItem('refresh_token');
      if (!refreshTokenValue) {
        return false;
      }

      const response = await fetch('/api/auth/refresh', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshTokenValue }),
      });

      if (!response.ok) {
        return false;
      }

      const data = await response.json();
      
      dispatch({
        type: 'UPDATE_TOKEN',
        payload: data.access_token,
      });
      
      return true;
    } catch (error) {
      console.error('Token refresh error:', error);
      return false;
    }
  };

  // API 호출 헬퍼
  const apiCall = async (endpoint: string, options: RequestInit = {}) => {
    const token = localStorage.getItem('access_token');
    const sessionId = localStorage.getItem('session_id');
    
    const response = await fetch(`/api/auth${endpoint}`, {
      ...options,
      headers: {
        'Authorization': token ? `Bearer ${token}` : '',
        'X-Session-ID': sessionId || '',
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (response.status === 401) {
      // 토큰 갱신 시도
      const refreshed = await refreshToken();
      if (refreshed) {
        // 갱신 성공 시 원래 요청 재시도
        const newToken = localStorage.getItem('access_token');
        return fetch(`/api/auth${endpoint}`, {
          ...options,
          headers: {
            'Authorization': newToken ? `Bearer ${newToken}` : '',
            'X-Session-ID': sessionId || '',
            'Content-Type': 'application/json',
            ...options.headers,
          },
        });
      } else {
        // 갱신 실패 시 로그아웃
        logout();
        throw new Error('Authentication failed');
      }
    }

    return response;
  };

  // 초기 인증 상태 확인
  useEffect(() => {
    const checkAuthState = async () => {
      const token = localStorage.getItem('access_token');
      
      if (token) {
        try {
          dispatch({ type: 'AUTH_START' });
          
          // 사용자 정보 가져오기
          const userResponse = await apiCall('/me');
          const user = await userResponse.json();
          
          // 권한 정보 가져오기
          const permissionsResponse = await apiCall('/permissions');
          const permissionsData = await permissionsResponse.json();
          
          setPermissions(permissionsData.permissions || []);
          
          const refreshTokenValue = localStorage.getItem('refresh_token') || '';
          const sessionId = localStorage.getItem('session_id') || '';
          
          dispatch({
            type: 'AUTH_SUCCESS',
            payload: { 
              user, 
              token, 
              refreshToken: refreshTokenValue,
              sessionId,
              permissions: permissionsData.permissions || []
            },
          });
          
        } catch (error) {
          console.error('Auth check failed:', error);
          dispatch({ type: 'LOGOUT' });
        }
      } else {
        dispatch({ type: 'SET_LOADING', payload: false });
      }
    };

    checkAuthState();
  }, []);

  // 강화된 로그인
  const login = async (credentials: LoginCredentials) => {
    try {
      dispatch({ type: 'AUTH_START' });
      
      const formData = new FormData();
      formData.append('username', credentials.username);
      formData.append('password', credentials.password);

      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }

      const data = await response.json();
      
      setPermissions(data.permissions || []);
      
      dispatch({
        type: 'AUTH_SUCCESS',
        payload: {
          user: data.user,
          token: data.access_token,
          refreshToken: data.refresh_token,
          sessionId: data.session_id,
          permissions: data.permissions || []
        },
      });
      
      toast.success(`환영합니다, ${data.user.username}님!`);
      
    } catch (error: any) {
      const errorMessage = error.message || '로그인에 실패했습니다.';
      
      dispatch({
        type: 'AUTH_FAILURE',
        payload: errorMessage,
      });
      
      toast.error(errorMessage);
      throw error;
    }
  };

  // 회원가입
  const register = async (credentials: RegisterCredentials) => {
    try {
      dispatch({ type: 'AUTH_START' });
      
      const user = await authService.register(credentials);
      
      toast.success('회원가입이 완료되었습니다! 로그인해주세요.');
      
      dispatch({ type: 'SET_LOADING', payload: false });
      
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || '회원가입에 실패했습니다.';
      
      dispatch({
        type: 'AUTH_FAILURE',
        payload: errorMessage,
      });
      
      toast.error(errorMessage);
      throw error;
    }
  };

  // 강화된 로그아웃
  const logout = async () => {
    try {
      // 서버에 로그아웃 요청
      await apiCall('/logout', { method: 'POST' });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setPermissions([]);
      dispatch({ type: 'LOGOUT' });
      toast.success('로그아웃되었습니다.');
    }
  };

  // 사용자 정보 업데이트
  const updateUser = (userData: Partial<User>) => {
    dispatch({ type: 'UPDATE_USER', payload: userData });
  };

  // 프로필 업데이트
  const updateProfile = async (profileData: Partial<User>) => {
    try {
      const response = await apiCall('/me', {
        method: 'PUT',
        body: JSON.stringify(profileData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Profile update failed');
      }

      const data = await response.json();
      updateUser(data.user);
      toast.success('프로필이 업데이트되었습니다.');
    } catch (error: any) {
      const errorMessage = error.message || '프로필 업데이트에 실패했습니다.';
      toast.error(errorMessage);
      throw error;
    }
  };

  // 비밀번호 변경
  const changePassword = async (currentPassword: string, newPassword: string) => {
    try {
      const response = await apiCall('/change-password', {
        method: 'POST',
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Password change failed');
      }

      toast.success('비밀번호가 변경되었습니다.');
    } catch (error: any) {
      const errorMessage = error.message || '비밀번호 변경에 실패했습니다.';
      toast.error(errorMessage);
      throw error;
    }
  };

  // 권한 확인 함수들
  const hasPermission = (permission: string): boolean => {
    return permissions.includes(permission);
  };

  const hasRole = (role: string): boolean => {
    return state.user?.role === role;
  };

  const hasAnyRole = (roles: string[]): boolean => {
    return state.user ? roles.includes(state.user.role) : false;
  };

  // 토큰 자동 갱신 설정
  useEffect(() => {
    if (!state.isAuthenticated) return;

    const interval = setInterval(async () => {
      await refreshToken();
    }, 25 * 60 * 1000); // 25분마다 갱신

    return () => clearInterval(interval);
  }, [state.isAuthenticated]);

  const contextValue: AuthContextType = {
    state,
    permissions,
    login,
    register,
    logout,
    updateUser,
    refreshToken,
    changePassword,
    updateProfile,
    hasPermission,
    hasRole,
    hasAnyRole,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

// useAuth 훅
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
}