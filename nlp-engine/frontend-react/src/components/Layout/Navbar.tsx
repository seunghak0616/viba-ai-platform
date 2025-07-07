import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Avatar,
  Menu,
  MenuItem,
  Box,
  Chip,
} from '@mui/material';
import {
  AccountCircle,
  Logout,
  Settings,
  Architecture,
  Notifications,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const { state, logout } = useAuth();
  const { user, isAuthenticated } = state;
  
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    handleMenuClose();
    navigate('/');
  };

  const handleProfile = () => {
    handleMenuClose();
    navigate('/profile');
  };

  return (
    <AppBar 
      position="sticky" 
      sx={{ 
        background: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)',
        boxShadow: '0 4px 20px rgba(37, 99, 235, 0.3)',
      }}
    >
      <Toolbar>
        {/* 로고 및 타이틀 */}
        <Box 
          sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            cursor: 'pointer',
            '&:hover': { opacity: 0.8 }
          }}
          onClick={() => navigate(isAuthenticated ? '/dashboard' : '/')}
        >
          <Architecture sx={{ mr: 1, fontSize: '2rem' }} />
          <Typography variant="h6" component="div" sx={{ fontWeight: 800 }}>
            VIBA AI
          </Typography>
        </Box>

        {/* 상태 표시 */}
        {isAuthenticated && (
          <Chip
            label="온라인"
            color="secondary"
            size="small"
            sx={{ ml: 2, fontWeight: 600 }}
          />
        )}

        {/* 네비게이션 버튼들 */}
        <Box sx={{ flexGrow: 1, display: 'flex', justifyContent: 'center' }}>
          {isAuthenticated && (
            <Box sx={{ display: { xs: 'none', md: 'flex' }, gap: 1 }}>
              <Button 
                color="inherit" 
                onClick={() => navigate('/dashboard')}
                sx={{ fontWeight: 600 }}
              >
                대시보드
              </Button>
              <Button 
                color="inherit" 
                onClick={() => navigate('/projects')}
                sx={{ fontWeight: 600 }}
              >
                프로젝트
              </Button>
            </Box>
          )}
        </Box>

        {/* 우측 영역 */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {isAuthenticated ? (
            <>
              {/* 알림 버튼 */}
              <IconButton color="inherit" size="large">
                <Notifications />
              </IconButton>

              {/* 사용자 메뉴 */}
              <IconButton
                size="large"
                edge="end"
                aria-label="account of current user"
                aria-controls="primary-search-account-menu"
                aria-haspopup="true"
                onClick={handleMenuOpen}
                color="inherit"
              >
                <Avatar 
                  sx={{ 
                    width: 32, 
                    height: 32, 
                    bgcolor: 'rgba(255,255,255,0.2)',
                    fontSize: '0.9rem',
                    fontWeight: 600,
                  }}
                >
                  {user?.username?.[0]?.toUpperCase() || 'U'}
                </Avatar>
              </IconButton>

              <Menu
                anchorEl={anchorEl}
                anchorOrigin={{
                  vertical: 'bottom',
                  horizontal: 'right',
                }}
                id="primary-search-account-menu"
                keepMounted
                transformOrigin={{
                  vertical: 'top',
                  horizontal: 'right',
                }}
                open={Boolean(anchorEl)}
                onClose={handleMenuClose}
                PaperProps={{
                  sx: {
                    mt: 1,
                    borderRadius: 2,
                    minWidth: 200,
                    boxShadow: '0 8px 32px rgba(0,0,0,0.12)',
                  },
                }}
              >
                <Box sx={{ px: 2, py: 1, borderBottom: '1px solid #e5e7eb' }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                    {user?.username}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    {user?.email}
                  </Typography>
                </Box>
                
                <MenuItem onClick={handleProfile}>
                  <AccountCircle sx={{ mr: 2 }} />
                  프로필
                </MenuItem>
                
                <MenuItem onClick={handleMenuClose}>
                  <Settings sx={{ mr: 2 }} />
                  설정
                </MenuItem>
                
                <MenuItem onClick={handleLogout}>
                  <Logout sx={{ mr: 2 }} />
                  로그아웃
                </MenuItem>
              </Menu>
            </>
          ) : (
            <>
              <Button 
                color="inherit" 
                onClick={() => navigate('/login')}
                sx={{ fontWeight: 600 }}
              >
                로그인
              </Button>
              <Button 
                variant="contained"
                onClick={() => navigate('/register')}
                sx={{ 
                  bgcolor: 'rgba(255,255,255,0.15)',
                  fontWeight: 600,
                  '&:hover': {
                    bgcolor: 'rgba(255,255,255,0.25)',
                  }
                }}
              >
                회원가입
              </Button>
            </>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;