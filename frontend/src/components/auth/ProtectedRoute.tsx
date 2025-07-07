import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../stores/authStore';

interface ProtectedRouteProps {
  children?: React.ReactNode;
  redirectTo?: string;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  redirectTo = '/login' 
}) => {
  const location = useLocation();
  const { isAuthenticated, isInitialized } = useAuthStore((state) => ({
    isAuthenticated: state.isAuthenticated,
    isInitialized: state.isInitialized
  }));

  console.log('ProtectedRoute - isAuthenticated:', isAuthenticated, 'isInitialized:', isInitialized);

  // Wait for auth store to initialize before making any decisions
  if (!isInitialized) {
    console.log('ProtectedRoute - Waiting for initialization...');
    return <div>Loading...</div>; // or a loading spinner
  }

  if (!isAuthenticated) {
    console.log('ProtectedRoute - Redirecting to:', redirectTo, 'from:', location.pathname);
    // Save the attempted location so we can redirect back after login
    return <Navigate to={redirectTo} state={{ from: location }} replace />;
  }

  console.log('ProtectedRoute - Rendering children');
  return children ? <>{children}</> : <Outlet />;
};

export default ProtectedRoute;