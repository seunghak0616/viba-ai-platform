import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Avatar,
  AvatarGroup,
  LinearProgress,
  IconButton,
  Paper,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  ListItemSecondaryAction
} from '@mui/material';
import {
  Add as AddIcon,
  Architecture as ArchitectureIcon,
  Group as GroupIcon,
  AccessTime as TimeIcon,
  TrendingUp as TrendingUpIcon,
  Folder as FolderIcon,
  ThreeDRotation as ThreeDRotationIcon,
  Edit as EditIcon,
  Share as ShareIcon,
  MoreVert as MoreVertIcon,
  Notifications as NotificationsIcon,
  Description as DescriptionIcon,
  Upload as UploadIcon
} from '@mui/icons-material';
import { useAuthStore } from '../../stores/authStore';
import ActivityChart from '../../components/dashboard/ActivityChart';

// 타입 정의
interface Project {
  id: string;
  name: string;
  description: string;
  progress: number;
  status: 'active' | 'completed' | 'paused';
  lastModified: string;
  teamMembers: Array<{
    id: string;
    name: string;
    avatar?: string;
  }>;
  thumbnail?: string;
  type: 'residential' | 'commercial' | 'office' | 'industrial';
}

interface Activity {
  id: string;
  type: 'project_created' | 'model_generated' | 'team_joined' | 'comment_added';
  message: string;
  timestamp: string;
  user: string;
  avatar?: string;
}

interface Stats {
  totalProjects: number;
  activeModels: number;
  teamMembers: number;
  weeklyHours: number;
  projectsChange: number;
  modelsChange: number;
  membersChange: number;
  hoursChange: number;
}

const DashboardPage: React.FC = () => {
  const { user } = useAuthStore();
  const [stats, setStats] = useState<Stats>({
    totalProjects: 12,
    activeModels: 8,
    teamMembers: 5,
    weeklyHours: 32,
    projectsChange: 2,
    modelsChange: 1,
    membersChange: 1,
    hoursChange: 8
  });

  const [recentProjects, setRecentProjects] = useState<Project[]>([
    {
      id: '1',
      name: '강남 오피스 빌딩',
      description: '25층 규모의 현대적 오피스 건물',
      progress: 85,
      status: 'active',
      lastModified: '2시간 전',
      teamMembers: [
        { id: '1', name: '김건축', avatar: '/api/placeholder/32/32' },
        { id: '2', name: '이설계', avatar: '/api/placeholder/32/32' },
        { id: '3', name: '박구조', avatar: '/api/placeholder/32/32' }
      ],
      type: 'office'
    },
    {
      id: '2',
      name: '판교 주상복합',
      description: '주거와 상업시설이 결합된 복합건물',
      progress: 60,
      status: 'active',
      lastModified: '1일 전',
      teamMembers: [
        { id: '1', name: '김건축', avatar: '/api/placeholder/32/32' },
        { id: '4', name: '최인테리어', avatar: '/api/placeholder/32/32' }
      ],
      type: 'residential'
    },
    {
      id: '3',
      name: '서울역 상업시설',
      description: '대형 쇼핑몰 및 업무시설',
      progress: 95,
      status: 'completed',
      lastModified: '3일 전',
      teamMembers: [
        { id: '1', name: '김건축', avatar: '/api/placeholder/32/32' },
        { id: '2', name: '이설계', avatar: '/api/placeholder/32/32' },
        { id: '5', name: '정시공', avatar: '/api/placeholder/32/32' }
      ],
      type: 'commercial'
    }
  ]);

  const [recentActivities, setRecentActivities] = useState<Activity[]>([
    {
      id: '1',
      type: 'model_generated',
      message: '강남 오피스 빌딩 3D 모델이 생성되었습니다',
      timestamp: '10분 전',
      user: '김건축',
      avatar: '/api/placeholder/32/32'
    },
    {
      id: '2',
      type: 'team_joined',
      message: '박구조님이 판교 주상복합 프로젝트에 참여했습니다',
      timestamp: '1시간 전',
      user: '박구조',
      avatar: '/api/placeholder/32/32'
    },
    {
      id: '3',
      type: 'project_created',
      message: '서초 아파트 단지 프로젝트가 생성되었습니다',
      timestamp: '2시간 전',
      user: '이설계',
      avatar: '/api/placeholder/32/32'
    },
    {
      id: '4',
      type: 'comment_added',
      message: '강남 오피스 빌딩에 새로운 댓글이 추가되었습니다',
      timestamp: '3시간 전',
      user: '최인테리어',
      avatar: '/api/placeholder/32/32'
    }
  ]);

  // 상태별 색상 가져오기
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'primary';
      case 'completed': return 'success';
      case 'paused': return 'warning';
      default: return 'default';
    }
  };

  // 상태별 텍스트
  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return '진행중';
      case 'completed': return '완료';
      case 'paused': return '일시중지';
      default: return '알 수 없음';
    }
  };

  // 프로젝트 타입별 색상
  const getTypeColor = (type: string) => {
    switch (type) {
      case 'residential': return '#4CAF50';
      case 'commercial': return '#2196F3';
      case 'office': return '#FF9800';
      case 'industrial': return '#9E9E9E';
      default: return '#9E9E9E';
    }
  };

  // 프로젝트 타입별 텍스트
  const getTypeText = (type: string) => {
    switch (type) {
      case 'residential': return '주거';
      case 'commercial': return '상업';
      case 'office': return '사무';
      case 'industrial': return '산업';
      default: return '기타';
    }
  };

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      {/* 헤더 섹션 */}
      <Box mb={4}>
        <Typography variant="h4" component="h1" gutterBottom>
          안녕하세요, {user?.name || '사용자'}님! 👋
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          오늘도 멋진 건축 프로젝트를 만들어보세요
        </Typography>
      </Box>

      {/* 통계 카드 섹션 */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="h6">
                    총 프로젝트
                  </Typography>
                  <Typography variant="h4" component="div">
                    {stats.totalProjects}
                  </Typography>
                  <Typography variant="body2" color="success.main">
                    +{stats.projectsChange} 이번 주
                  </Typography>
                </Box>
                <FolderIcon sx={{ fontSize: 40, color: 'primary.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="h6">
                    활성 모델
                  </Typography>
                  <Typography variant="h4" component="div">
                    {stats.activeModels}
                  </Typography>
                  <Typography variant="body2" color="success.main">
                    +{stats.modelsChange} 새로 생성
                  </Typography>
                </Box>
                <ThreeDRotationIcon sx={{ fontSize: 40, color: 'secondary.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="h6">
                    팀 멤버
                  </Typography>
                  <Typography variant="h4" component="div">
                    {stats.teamMembers}
                  </Typography>
                  <Typography variant="body2" color="success.main">
                    +{stats.membersChange} 새로 참여
                  </Typography>
                </Box>
                <GroupIcon sx={{ fontSize: 40, color: 'info.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="h6">
                    이번주 작업
                  </Typography>
                  <Typography variant="h4" component="div">
                    {stats.weeklyHours}h
                  </Typography>
                  <Typography variant="body2" color="success.main">
                    +{stats.hoursChange}h 증가
                  </Typography>
                </Box>
                <TimeIcon sx={{ fontSize: 40, color: 'warning.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* 활동 차트 섹션 */}
        <Grid item xs={12} md={6}>
          <ActivityChart />
        </Grid>

        {/* 우측 사이드바 */}
        <Grid item xs={12} md={6}>
          {/* 빠른 작업 */}
          <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" component="h2" gutterBottom>
              빠른 작업
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Button
                  fullWidth
                  variant="contained"
                  startIcon={<AddIcon />}
                  href="/projects"
                  sx={{ py: 1.5 }}
                >
                  새 프로젝트
                </Button>
              </Grid>
              <Grid item xs={6}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<ArchitectureIcon />}
                  href="/3d-viewer"
                  sx={{ py: 1.5 }}
                >
                  자연어 생성
                </Button>
              </Grid>
              <Grid item xs={6}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<UploadIcon />}
                  sx={{ py: 1.5 }}
                >
                  파일 가져오기
                </Button>
              </Grid>
              <Grid item xs={6}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<GroupIcon />}
                  sx={{ py: 1.5 }}
                >
                  팀 초대
                </Button>
              </Grid>
            </Grid>
          </Paper>

          {/* 최근 활동 */}
          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h6" component="h2" gutterBottom>
              최근 활동
            </Typography>
            <List dense>
              {recentActivities.map((activity, index) => (
                <React.Fragment key={activity.id}>
                  <ListItem alignItems="flex-start" sx={{ px: 0 }}>
                    <ListItemAvatar>
                      <Avatar src={activity.avatar} sx={{ width: 32, height: 32 }}>
                        {activity.user.charAt(0)}
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={activity.message}
                      secondary={
                        <Typography variant="caption" color="text.secondary">
                          {activity.timestamp}
                        </Typography>
                      }
                      primaryTypographyProps={{ variant: 'body2' }}
                    />
                  </ListItem>
                  {index < recentActivities.length - 1 && <Divider component="li" />}
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>

      {/* 최근 프로젝트 섹션 */}
      <Grid container spacing={3} mt={2}>
        <Grid item xs={12}>
          <Paper elevation={2} sx={{ p: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
              <Typography variant="h6" component="h2">
                최근 프로젝트
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                href="/projects"
              >
                새 프로젝트
              </Button>
            </Box>

            <Grid container spacing={2}>
              {recentProjects.map((project) => (
                <Grid item xs={12} key={project.id}>
                  <Card variant="outlined">
                    <CardContent>
                      <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                        <Box flex={1}>
                          <Box display="flex" alignItems="center" gap={1} mb={1}>
                            <Typography variant="h6" component="h3">
                              {project.name}
                            </Typography>
                            <Chip
                              label={getStatusText(project.status)}
                              color={getStatusColor(project.status) as any}
                              size="small"
                            />
                            <Chip
                              label={getTypeText(project.type)}
                              size="small"
                              sx={{ 
                                bgcolor: getTypeColor(project.type),
                                color: 'white'
                              }}
                            />
                          </Box>
                          <Typography variant="body2" color="text.secondary" mb={1}>
                            {project.description}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            마지막 수정: {project.lastModified}
                          </Typography>
                        </Box>
                        <IconButton>
                          <MoreVertIcon />
                        </IconButton>
                      </Box>

                      <Box mb={2}>
                        <Box display="flex" justifyContent="space-between" mb={1}>
                          <Typography variant="body2">진행률</Typography>
                          <Typography variant="body2">{project.progress}%</Typography>
                        </Box>
                        <LinearProgress 
                          variant="determinate" 
                          value={project.progress}
                          sx={{ height: 8, borderRadius: 4 }}
                        />
                      </Box>

                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <AvatarGroup max={4}>
                          {project.teamMembers.map((member) => (
                            <Avatar
                              key={member.id}
                              alt={member.name}
                              src={member.avatar}
                              sx={{ width: 32, height: 32 }}
                            >
                              {member.name.charAt(0)}
                            </Avatar>
                          ))}
                        </AvatarGroup>

                        <Box display="flex" gap={1}>
                          <Button
                            size="small"
                            startIcon={<ThreeDRotationIcon />}
                            href="/3d-viewer"
                          >
                            3D 보기
                          </Button>
                          <Button
                            size="small"
                            startIcon={<EditIcon />}
                            href={`/projects/${project.id}`}
                          >
                            편집
                          </Button>
                          <Button
                            size="small"
                            startIcon={<ShareIcon />}
                          >
                            공유
                          </Button>
                        </Box>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default DashboardPage;