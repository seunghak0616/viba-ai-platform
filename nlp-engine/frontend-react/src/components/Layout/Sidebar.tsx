import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Box,
  Typography,
} from '@mui/material';
import {
  Dashboard,
  FolderOpen,
  AutoAwesome,
  Analytics,
  Settings,
  Help,
  Architecture,
  Psychology,
  Palette,
  Group,
  View3D,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

const drawerWidth = 240;

const menuItems = [
  { text: '대시보드', icon: <Dashboard />, path: '/dashboard' },
  { text: '프로젝트', icon: <FolderOpen />, path: '/projects' },
  { text: 'AI 에이전트', icon: <Psychology />, path: '/ai-agents' },
  { text: '설계 스튜디오', icon: <Palette />, path: '/design-studio' },
  { text: '3D 뷰어', icon: <View3D />, path: '/model-viewer' },
  { text: '분석', icon: <Analytics />, path: '/analytics' },
  { text: '협업', icon: <Group />, path: '/collaboration' },
];

const bottomMenuItems = [
  { text: '설정', icon: <Settings />, path: '/settings' },
  { text: '도움말', icon: <Help />, path: '/help' },
];

const Sidebar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const isSelected = (path: string) => location.pathname === path;

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          background: 'linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%)',
          borderRight: '1px solid #e2e8f0',
          boxShadow: '4px 0 12px rgba(0,0,0,0.05)',
        },
      }}
    >
      {/* 로고 영역 */}
      <Box
        sx={{
          p: 2,
          display: 'flex',
          alignItems: 'center',
          background: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)',
          color: 'white',
        }}
      >
        <Architecture sx={{ mr: 1, fontSize: '1.5rem' }} />
        <Typography variant="h6" sx={{ fontWeight: 700 }}>
          VIBA AI
        </Typography>
      </Box>

      {/* 메인 메뉴 */}
      <Box sx={{ overflow: 'auto', flexGrow: 1 }}>
        <List sx={{ pt: 2 }}>
          {menuItems.map((item) => (
            <ListItem key={item.text} disablePadding sx={{ px: 1 }}>
              <ListItemButton
                selected={isSelected(item.path)}
                onClick={() => navigate(item.path)}
                sx={{
                  borderRadius: 2,
                  mx: 1,
                  '&.Mui-selected': {
                    background: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)',
                    color: 'white',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%)',
                    },
                    '& .MuiListItemIcon-root': {
                      color: 'white',
                    },
                  },
                  '&:hover': {
                    backgroundColor: isSelected(item.path) 
                      ? 'linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%)'
                      : 'rgba(37, 99, 235, 0.08)',
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    color: isSelected(item.path) ? 'white' : '#64748b',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText 
                  primary={item.text}
                  primaryTypographyProps={{
                    fontWeight: isSelected(item.path) ? 600 : 500,
                  }}
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>

        {/* 구분선 */}
        <Divider sx={{ my: 2, mx: 2 }} />

        {/* 하단 메뉴 */}
        <List>
          {bottomMenuItems.map((item) => (
            <ListItem key={item.text} disablePadding sx={{ px: 1 }}>
              <ListItemButton
                selected={isSelected(item.path)}
                onClick={() => navigate(item.path)}
                sx={{
                  borderRadius: 2,
                  mx: 1,
                  '&.Mui-selected': {
                    backgroundColor: 'rgba(37, 99, 235, 0.12)',
                    color: '#2563eb',
                    '& .MuiListItemIcon-root': {
                      color: '#2563eb',
                    },
                  },
                  '&:hover': {
                    backgroundColor: 'rgba(37, 99, 235, 0.08)',
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    color: isSelected(item.path) ? '#2563eb' : '#64748b',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText 
                  primary={item.text}
                  primaryTypographyProps={{
                    fontWeight: isSelected(item.path) ? 600 : 500,
                  }}
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Box>

      {/* 하단 정보 */}
      <Box
        sx={{
          p: 2,
          background: 'rgba(37, 99, 235, 0.05)',
          borderTop: '1px solid #e2e8f0',
        }}
      >
        <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 500 }}>
          VIBA AI v1.0
        </Typography>
        <br />
        <Typography variant="caption" color="textSecondary">
          건축 설계 플랫폼
        </Typography>
      </Box>
    </Drawer>
  );
};

export default Sidebar;