import React, { useEffect, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ReactQueryDevtools } from 'react-query/devtools';
import { Toaster } from 'react-hot-toast';

// Theme and stores
import { theme } from '@/theme';
import { useAuthStore } from '@stores/authStore';

// Components
import LoadingSpinner from '@components/common/LoadingSpinner';
import ErrorBoundary from '@components/common/ErrorBoundary';
import ProtectedRoute from '@components/auth/ProtectedRoute';
import AuthGuard from '@components/auth/AuthGuard';

// Pages (lazy loaded for performance)
const LoginPage = React.lazy(() => import('@pages/auth/LoginPage'));
const RegisterPage = React.lazy(() => import('@pages/auth/RegisterPage'));
const DashboardPage = React.lazy(() => import('@pages/dashboard/DashboardPage'));
const ProjectsPage = React.lazy(() => import('@pages/projects/ProjectsPage'));
const ProjectDetailPage = React.lazy(() => import('@pages/projects/ProjectDetailPage'));
const BimModelPage = React.lazy(() => import('@pages/bim/BimModelPage'));
const BimEditorPage = React.lazy(() => import('@pages/bim/BimEditorPage'));
const ParametricBIMPage = React.lazy(() => import('@pages/bim/ParametricBIMPage'));
const BIMViewerPage = React.lazy(() => import('@components/3D/BIMViewerPage'));
const AIAgentsPage = React.lazy(() => import('@pages/ai/AIAgentsPage'));
const UserManagement = React.lazy(() => import('@components/admin/UserManagement'));
const SettingsPage = React.lazy(() => import('@pages/settings/SettingsPage'));
const NotFoundPage = React.lazy(() => import('@pages/error/NotFoundPage'));

// React Query 클라이언트 설정
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error: any) => {
        // 401, 403 에러는 재시도하지 않음
        if (error?.response?.status === 401 || error?.response?.status === 403) {
          return false;
        }
        // 3번까지 재시도
        return failureCount < 3;
      },
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000), // 지수 백오프
      staleTime: 5 * 60 * 1000, // 5분
      cacheTime: 10 * 60 * 1000, // 10분
      refetchOnWindowFocus: false,
      refetchOnMount: true,
    },
    mutations: {
      retry: false, // 뮤테이션은 재시도하지 않음
    },
  },
});

// 에러 처리를 위한 전역 에러 핸들러
const handleGlobalError = (error: Error, errorInfo: React.ErrorInfo) => {
  console.error('Global error:', error, errorInfo);
  
  // 프로덕션 환경에서는 에러 리포팅 서비스로 전송
  if (import.meta.env.PROD && import.meta.env.VITE_SENTRY_DSN) {
    // Sentry.captureException(error);
  }
};

// 페이지 로딩 컴포넌트
const PageLoadingFallback: React.FC = () => (
  <LoadingSpinner 
    size="large" 
    message="페이지를 불러오는 중..." 
    backdrop 
  />
);

// 메인 앱 컴포넌트
const App: React.FC = () => {
  const { initialize, isInitialized, isAuthenticated } = useAuthStore();

  // 앱 초기화
  useEffect(() => {
    const initializeApp = async () => {
      try {
        // 인증 스토어 초기화
        initialize();
        
        // 기타 초기화 작업들
        // - 테마 설정 로드
        // - 언어 설정 로드
        // - 캐시 정리 등
        
        console.log('App initialized successfully');
      } catch (error) {
        console.error('App initialization failed:', error);
      }
    };

    initializeApp();
  }, [initialize]);

  // 초기화가 완료되지 않았으면 로딩 표시
  if (!isInitialized) {
    return <PageLoadingFallback />;
  }

  return (
    <ErrorBoundary onError={handleGlobalError}>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <Router>
            <div className="App">
              <Suspense fallback={<PageLoadingFallback />}>
                <Routes>
                  {/* 공개 라우트 */}
                  <Route 
                    path="/login" 
                    element={
                      <AuthGuard requireAuth={false} redirectTo="/dashboard">
                        <LoginPage />
                      </AuthGuard>
                    } 
                  />
                  <Route 
                    path="/register" 
                    element={
                      <AuthGuard requireAuth={false} redirectTo="/dashboard">
                        <RegisterPage />
                      </AuthGuard>
                    } 
                  />

                  {/* 보호된 라우트 */}
                  <Route
                    path="/dashboard"
                    element={
                      <ProtectedRoute>
                        <DashboardPage />
                      </ProtectedRoute>
                    }
                  />
                  
                  <Route
                    path="/projects"
                    element={
                      <ProtectedRoute>
                        <ProjectsPage />
                      </ProtectedRoute>
                    }
                  />
                  
                  <Route
                    path="/projects/:projectId"
                    element={
                      <ProtectedRoute>
                        <ProjectDetailPage />
                      </ProtectedRoute>
                    }
                  />
                  
                  <Route
                    path="/projects/:projectId/models/:modelId"
                    element={
                      <ProtectedRoute>
                        <BimModelPage />
                      </ProtectedRoute>
                    }
                  />
                  
                  <Route
                    path="/projects/:projectId/models/:modelId/edit"
                    element={
                      <ProtectedRoute roles={['ADMIN', 'ARCHITECT', 'PREMIUM']}>
                        <BimEditorPage />
                      </ProtectedRoute>
                    }
                  />
                  
                  <Route
                    path="/projects/:projectId/parametric-bim"
                    element={
                      <ProtectedRoute roles={['ADMIN', 'ARCHITECT', 'PREMIUM']}>
                        <ParametricBIMPage />
                      </ProtectedRoute>
                    }
                  />
                  
                  <Route
                    path="/projects/:projectId/parametric-bim/:modelId"
                    element={
                      <ProtectedRoute roles={['ADMIN', 'ARCHITECT', 'PREMIUM']}>
                        <ParametricBIMPage />
                      </ProtectedRoute>
                    }
                  />
                  
                  <Route
                    path="/3d-viewer"
                    element={
                      <ProtectedRoute>
                        <BIMViewerPage />
                      </ProtectedRoute>
                    }
                  />
                  
                  <Route
                    path="/ai-agents"
                    element={
                      <ProtectedRoute>
                        <AIAgentsPage />
                      </ProtectedRoute>
                    }
                  />
                  
                  <Route
                    path="/admin/users"
                    element={
                      <ProtectedRoute roles={['ADMIN', 'SUPER_ADMIN']}>
                        <UserManagement />
                      </ProtectedRoute>
                    }
                  />
                  
                  <Route
                    path="/settings"
                    element={
                      <ProtectedRoute>
                        <SettingsPage />
                      </ProtectedRoute>
                    }
                  />

                  {/* 기본 리다이렉트 - 정확히 "/" 경로만 매칭 */}
                  <Route 
                    index
                    element={
                      <Navigate 
                        to={isAuthenticated ? "/dashboard" : "/login"} 
                        replace 
                      />
                    } 
                  />

                  {/* 404 페이지 */}
                  <Route path="*" element={<NotFoundPage />} />
                </Routes>
              </Suspense>

              {/* 전역 토스트 알림 */}
              <Toaster
                position="top-right"
                toastOptions={{
                  duration: 4000,
                  style: {
                    background: '#363636',
                    color: '#fff',
                  },
                  success: {
                    duration: 3000,
                    iconTheme: {
                      primary: '#4caf50',
                      secondary: '#fff',
                    },
                  },
                  error: {
                    duration: 5000,
                    iconTheme: {
                      primary: '#f44336',
                      secondary: '#fff',
                    },
                  },
                }}
              />
            </div>
          </Router>

          {/* 개발 환경에서만 React Query DevTools 표시 */}
          {import.meta.env.DEV && (
            <ReactQueryDevtools 
              initialIsOpen={false} 
              position="bottom-right"
            />
          )}
        </ThemeProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
};

export default App;