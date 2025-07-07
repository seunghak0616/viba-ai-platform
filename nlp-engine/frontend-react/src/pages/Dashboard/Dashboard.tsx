import React from 'react';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  Avatar,
  Chip,
  LinearProgress,
  IconButton,
} from '@mui/material';
import {
  FolderOpen,
  AutoAwesome,
  TrendingUp,
  Speed,
  Add,
  MoreVert,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { state } = useAuth();
  const { user } = state;

  // Mock 데이터
  const stats = [
    {
      title: '진행 중인 프로젝트',
      value: '3',
      icon: <FolderOpen />,
      color: '#2563eb',
      change: '+2 이번 주',
    },
    {
      title: 'AI 설계 요청',
      value: '15',
      icon: <AutoAwesome />,
      color: '#10b981',
      change: '+5 오늘',
    },
    {
      title: '완료된 프로젝트',
      value: '8',
      icon: <TrendingUp />,
      color: '#f59e0b',
      change: '+1 이번 달',
    },
    {
      title: '평균 처리 시간',
      value: '0.3초',
      icon: <Speed />,
      color: '#8b5cf6',
      change: '-0.1초 개선',
    },
  ];

  const recentProjects = [
    {
      id: '1',
      name: '친환경 주택 설계',
      description: '30평 규모의 친환경 주택 프로젝트',
      progress: 75,
      status: '진행중',
      lastUpdate: '2시간 전',
    },
    {
      id: '2',
      name: '상업용 빌딩',
      description: '20층 오피스 빌딩 구조 설계',
      progress: 45,
      status: '설계중',
      lastUpdate: '1일 전',
    },
    {
      id: '3',
      name: '카페 인테리어',
      description: '자연 친화적 카페 인테리어 디자인',
      progress: 90,
      status: '검토중',
      lastUpdate: '3시간 전',
    },
  ];

  const recentActivities = [
    {
      type: 'project',
      message: '친환경 주택 설계 프로젝트가 업데이트되었습니다',
      time: '10분 전',
      avatar: 'P',
    },
    {
      type: 'ai',
      message: 'AI가 새로운 재료 추천을 생성했습니다',
      time: '30분 전',
      avatar: 'AI',
    },
    {
      type: 'system',
      message: '시스템 성능이 최적화되었습니다',
      time: '1시간 전',
      avatar: 'S',
    },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case '진행중':
        return 'primary';
      case '설계중':
        return 'warning';
      case '검토중':
        return 'info';
      case '완료':
        return 'success';
      default:
        return 'default';
    }
  };

  return (
    <Container maxWidth="xl">
      {/* 헤더 */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 800, mb: 1 }}>
          안녕하세요, {user?.username}님! 👋
        </Typography>
        <Typography variant="h6" color="textSecondary">
          오늘도 멋진 건축 설계를 만들어보세요
        </Typography>
      </Box>

      {/* 통계 카드들 */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {stats.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card
              sx={{
                height: '100%',
                border: 'none',
                borderRadius: 3,
                boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
                '&:hover': {
                  boxShadow: '0 8px 25px rgba(0,0,0,0.1)',
                  transform: 'translateY(-2px)',
                },
                transition: 'all 0.3s ease',
              }}
            >
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Box
                    sx={{
                      width: 48,
                      height: 48,
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      bgcolor: `${stat.color}15`,
                      color: stat.color,
                      mr: 2,
                    }}
                  >
                    {stat.icon}
                  </Box>
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="h4" sx={{ fontWeight: 800, color: stat.color }}>
                      {stat.value}
                    </Typography>
                  </Box>
                </Box>
                <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
                  {stat.title}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  {stat.change}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3}>
        {/* 최근 프로젝트 */}
        <Grid item xs={12} lg={8}>
          <Card
            sx={{
              borderRadius: 3,
              boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
              border: 'none',
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: 700 }}>
                  최근 프로젝트
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<Add />}
                  onClick={() => navigate('/projects')}
                  sx={{
                    borderRadius: 2,
                    fontWeight: 600,
                  }}
                >
                  새 프로젝트
                </Button>
              </Box>

              {recentProjects.map((project) => (
                <Card
                  key={project.id}
                  sx={{
                    mb: 2,
                    border: '1px solid #e2e8f0',
                    borderRadius: 2,
                    '&:hover': {
                      borderColor: '#2563eb',
                      boxShadow: '0 4px 12px rgba(37, 99, 235, 0.15)',
                    },
                    transition: 'all 0.2s ease',
                    cursor: 'pointer',
                  }}
                  onClick={() => navigate(`/projects/${project.id}`)}
                >
                  <CardContent sx={{ p: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 0.5 }}>
                          {project.name}
                        </Typography>
                        <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                          {project.description}
                        </Typography>
                        <Chip
                          label={project.status}
                          size="small"
                          color={getStatusColor(project.status) as any}
                          sx={{ fontWeight: 500 }}
                        />
                      </Box>
                      <IconButton size="small">
                        <MoreVert />
                      </IconButton>
                    </Box>
                    <Box sx={{ mb: 1 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                        <Typography variant="caption" color="textSecondary">
                          진행률
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {project.progress}%
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={project.progress}
                        sx={{
                          height: 6,
                          borderRadius: 3,
                          backgroundColor: '#e2e8f0',
                          '& .MuiLinearProgress-bar': {
                            borderRadius: 3,
                          },
                        }}
                      />
                    </Box>
                    <Typography variant="caption" color="textSecondary">
                      마지막 업데이트: {project.lastUpdate}
                    </Typography>
                  </CardContent>
                </Card>
              ))}
            </CardContent>
          </Card>
        </Grid>

        {/* 최근 활동 */}
        <Grid item xs={12} lg={4}>
          <Card
            sx={{
              borderRadius: 3,
              boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
              border: 'none',
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 3 }}>
                최근 활동
              </Typography>

              {recentActivities.map((activity, index) => (
                <Box key={index} sx={{ display: 'flex', alignItems: 'flex-start', mb: 3 }}>
                  <Avatar
                    sx={{
                      width: 36,
                      height: 36,
                      mr: 2,
                      fontSize: '0.875rem',
                      fontWeight: 600,
                      bgcolor: activity.type === 'ai' ? '#10b981' : '#2563eb',
                    }}
                  >
                    {activity.avatar}
                  </Avatar>
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="body2" sx={{ mb: 0.5 }}>
                      {activity.message}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      {activity.time}
                    </Typography>
                  </Box>
                </Box>
              ))}

              <Button
                fullWidth
                variant="outlined"
                sx={{
                  mt: 2,
                  borderRadius: 2,
                  fontWeight: 600,
                }}
              >
                모든 활동 보기
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;