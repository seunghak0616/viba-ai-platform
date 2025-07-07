import React from 'react';
import { Box } from '@mui/material';
import Navbar from './Navbar';
import Sidebar from './Sidebar';
import { useAuth } from '../../contexts/AuthContext';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { state } = useAuth();
  const { isAuthenticated } = state;

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* 사이드바 (인증된 사용자만) */}
      {isAuthenticated && <Sidebar />}
      
      {/* 메인 콘텐츠 */}
      <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        <Navbar />
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            p: isAuthenticated ? 3 : 0,
            ml: isAuthenticated ? 0 : 0, // 사이드바 여백
            transition: 'margin 0.3s ease',
          }}
        >
          {children}
        </Box>
      </Box>
    </Box>
  );
};

export default Layout;