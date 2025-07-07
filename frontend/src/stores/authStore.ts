import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { User, AuthTokens, AuthState } from '@types/index';
import { getStoredTokens, setStoredTokens, clearStoredTokens } from '@services/api';

interface AuthStore extends AuthState {
  // Actions
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  updateUser: (user: Partial<User>) => void;
  setLoading: (isLoading: boolean) => void;
  initialize: () => void;
  clearError: () => void;
  checkAuth: () => void;
  
  // State
  error: string | null;
  isInitialized: boolean;
}

// 초기 상태
const initialState: Omit<AuthStore, 'login' | 'logout' | 'updateUser' | 'setLoading' | 'initialize' | 'clearError' | 'checkAuth'> = {
  user: null,
  tokens: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  isInitialized: false,
};

// Zustand 스토어 생성
export const useAuthStore = create<AuthStore>()(
  devtools(
    persist(
      (set, get) => ({
        ...initialState,

        // 로그인 액션
        login: async (email: string, password: string) => {
          set({ isLoading: true, error: null });
          
          try {
            // API 호출
            const response = await fetch('http://localhost:5001/api/auth/login', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ email, password })
            });

            const data = await response.json();

            if (!response.ok) {
              throw new Error(data.message || 'Login failed');
            }

            if (data.success && data.data) {
              const user = data.data.user;
              const tokens = {
                token: data.data.token,
                refreshToken: data.data.refreshToken
              };

              // 토큰을 로컬 스토리지에 저장
              setStoredTokens(tokens);
              
              set({
                user,
                tokens,
                isAuthenticated: true,
                isLoading: false,
                error: null,
              },
              false,
              'auth/login'
            );
            } else {
              throw new Error('Invalid login response');
            }
          } catch (error: any) {
            set({
              isLoading: false,
              error: error.message || 'Login failed',
              isAuthenticated: false,
              user: null,
              tokens: null
            });
            throw error;
          }
        },

        // 로그아웃 액션
        logout: () => {
          try {
            // 토큰 클리어
            clearStoredTokens();
            
            set(
              {
                user: null,
                tokens: null,
                isAuthenticated: false,
                isLoading: false,
                error: null,
              },
              false,
              'auth/logout'
            );

            console.log('User logged out successfully');
          } catch (error) {
            console.error('Logout error:', error);
            // 로그아웃은 실패해도 상태는 클리어
            set(
              {
                user: null,
                tokens: null,
                isAuthenticated: false,
                isLoading: false,
                error: null,
              },
              false,
              'auth/logout-force'
            );
          }
        },

        // 사용자 정보 업데이트
        updateUser: (userData: Partial<User>) => {
          const currentUser = get().user;
          if (!currentUser) {
            console.warn('Cannot update user: no user is logged in');
            return;
          }

          try {
            const updatedUser = { ...currentUser, ...userData };
            
            set(
              {
                user: updatedUser,
                error: null,
              },
              false,
              'auth/update-user'
            );

            console.log('User updated successfully:', { userId: updatedUser.id });
          } catch (error) {
            console.error('Update user error:', error);
            set(
              {
                error: '사용자 정보 업데이트 중 오류가 발생했습니다.',
              },
              false,
              'auth/update-user-error'
            );
          }
        },

        // 로딩 상태 설정
        setLoading: (isLoading: boolean) => {
          set(
            { isLoading },
            false,
            `auth/set-loading-${isLoading}`
          );
        },

        // 스토어 초기화 (앱 시작시 호출)
        initialize: () => {
          try {
            const tokens = getStoredTokens();
            
            if (tokens?.token) {
              // 토큰이 있으면 인증된 상태로 설정
              // 실제 사용자 정보는 API 호출로 가져와야 함
              set(
                {
                  tokens,
                  isAuthenticated: true,
                  isInitialized: true,
                  isLoading: false,
                },
                false,
                'auth/initialize-with-token'
              );
            } else {
              // 토큰이 없으면 비인증 상태
              set(
                {
                  isInitialized: true,
                  isLoading: false,
                },
                false,
                'auth/initialize-without-token'
              );
            }

            console.log('Auth store initialized');
          } catch (error) {
            console.error('Auth initialization error:', error);
            set(
              {
                isInitialized: true,
                isLoading: false,
                error: '인증 초기화 중 오류가 발생했습니다.',
              },
              false,
              'auth/initialize-error'
            );
          }
        },

        // 에러 클리어
        clearError: () => {
          set(
            { error: null },
            false,
            'auth/clear-error'
          );
        },

        // 인증 상태 확인 (initialize와 동일한 동작)
        checkAuth: () => {
          get().initialize();
        },
      }),
      {
        name: 'bim-auth-store',
        // 민감한 정보는 persist에서 제외
        partialize: (state) => ({
          isInitialized: state.isInitialized,
          // 토큰은 localStorage에 별도 저장하므로 제외
          // user 정보도 보안상 제외 (API에서 다시 가져오기)
        }),
      }
    ),
    {
      name: 'auth-store',
    }
  )
);

// 선택자 함수들 (성능 최적화)
export const useAuthUser = () => useAuthStore((state) => state.user);
export const useAuthTokens = () => useAuthStore((state) => state.tokens);
export const useIsAuthenticated = () => useAuthStore((state) => state.isAuthenticated);
export const useAuthLoading = () => useAuthStore((state) => state.isLoading);
export const useAuthError = () => useAuthStore((state) => state.error);
export const useAuthActions = () => useAuthStore((state) => ({
  login: state.login,
  logout: state.logout,
  updateUser: state.updateUser,
  setLoading: state.setLoading,
  initialize: state.initialize,
  clearError: state.clearError,
  checkAuth: state.checkAuth,
}));

// 권한 체크 헬퍼 함수들
export const useHasRole = (role: User['role']) => {
  return useAuthStore((state) => state.user?.role === role);
};

export const useHasAnyRole = (roles: User['role'][]) => {
  return useAuthStore((state) => 
    state.user?.role ? roles.includes(state.user.role) : false
  );
};

export const useCanEdit = () => {
  return useAuthStore((state) => 
    state.user?.role ? ['ADMIN', 'ARCHITECT', 'PREMIUM'].includes(state.user.role) : false
  );
};

export const useCanAdmin = () => {
  return useAuthStore((state) => state.user?.role === 'ADMIN');
};

// 사용자 정보 가져오기 헬퍼
export const getCurrentUser = (): User | null => {
  return useAuthStore.getState().user;
};

export const getCurrentTokens = (): AuthTokens | null => {
  return useAuthStore.getState().tokens;
};

export const isUserAuthenticated = (): boolean => {
  return useAuthStore.getState().isAuthenticated;
};

// 개발 환경에서만 사용되는 디버그 함수
if (import.meta.env.DEV) {
  // @ts-ignore
  window.authStore = useAuthStore;
  console.log('Auth store attached to window.authStore for debugging');
}