import React, { useState } from 'react';
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
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Divider,
  Paper,
  Tab,
  Tabs,
  LinearProgress,
  Alert,
  Badge,
  Tooltip,
} from '@mui/material';
import {
  Group,
  Add,
  VideoCall,
  Chat,
  Share,
  Edit,
  Delete,
  Notifications,
  Schedule,
  Assignment,
  CloudUpload,
  Download,
  Comment,
  Visibility,
  MoreVert,
  PersonAdd,
  Settings,
  LiveHelp,
  Update,
  CheckCircle,
  Warning,
  AccessTime,
  AccountCircle,
  Engineering,
  Architecture,
  Science,
  Analytics,
  Palette,
} from '@mui/icons-material';

interface TeamMember {
  id: string;
  name: string;
  role: string;
  avatar: string;
  status: 'online' | 'offline' | 'busy';
  lastActivity: string;
  permissions: string[];
}

interface Project {
  id: string;
  name: string;
  description: string;
  status: string;
  progress: number;
  members: TeamMember[];
  lastUpdate: string;
  priority: 'high' | 'medium' | 'low';
}

interface ActivityItem {
  id: string;
  type: 'comment' | 'update' | 'file' | 'ai_analysis' | 'meeting';
  user: string;
  action: string;
  timestamp: string;
  project?: string;
  details?: string;
}

const Collaboration: React.FC = () => {
  const [selectedTab, setSelectedTab] = useState(0);
  const [inviteDialogOpen, setInviteDialogOpen] = useState(false);
  const [meetingDialogOpen, setMeetingDialogOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState('viewer');

  // 팀 멤버 데이터
  const teamMembers: TeamMember[] = [
    {
      id: '1',
      name: '김건축',
      role: '프로젝트 매니저',
      avatar: '/api/placeholder/40/40',
      status: 'online',
      lastActivity: '5분 전',
      permissions: ['read', 'write', 'admin'],
    },
    {
      id: '2',
      name: '이구조',
      role: '구조 엔지니어',
      avatar: '/api/placeholder/40/40',
      status: 'busy',
      lastActivity: '15분 전',
      permissions: ['read', 'write'],
    },
    {
      id: '3',
      name: '박디자인',
      role: '인테리어 디자이너',
      avatar: '/api/placeholder/40/40',
      status: 'online',
      lastActivity: '2분 전',
      permissions: ['read', 'write'],
    },
    {
      id: '4',
      name: '정AI',
      role: 'AI 전문가',
      avatar: '/api/placeholder/40/40',
      status: 'offline',
      lastActivity: '1시간 전',
      permissions: ['read', 'write', 'ai_access'],
    },
    {
      id: '5',
      name: '최예산',
      role: '비용 관리자',
      avatar: '/api/placeholder/40/40',
      status: 'online',
      lastActivity: '10분 전',
      permissions: ['read', 'write'],
    },
  ];

  // 프로젝트 데이터
  const projects: Project[] = [
    {
      id: '1',
      name: '친환경 주택 설계',
      description: '30평 규모의 친환경 주택 프로젝트',
      status: '진행중',
      progress: 75,
      members: teamMembers.slice(0, 4),
      lastUpdate: '2025-01-06T14:30:00Z',
      priority: 'high',
    },
    {
      id: '2',
      name: '상업용 빌딩 구조 설계',
      description: '20층 규모의 오피스 빌딩 프로젝트',
      status: '검토중',
      progress: 45,
      members: teamMembers.slice(1, 5),
      lastUpdate: '2025-01-06T12:15:00Z',
      priority: 'medium',
    },
    {
      id: '3',
      name: '아파트 단지 계획',
      description: '500세대 규모의 아파트 단지',
      status: '기획중',
      progress: 20,
      members: teamMembers.slice(0, 3),
      lastUpdate: '2025-01-06T09:45:00Z',
      priority: 'low',
    },
  ];

  // 활동 기록
  const activities: ActivityItem[] = [
    {
      id: '1',
      type: 'ai_analysis',
      user: '정AI',
      action: 'AI 구조 분석 완료',
      timestamp: '2025-01-06T14:30:00Z',
      project: '친환경 주택 설계',
      details: '구조 안전성 검증 및 최적화 제안',
    },
    {
      id: '2',
      type: 'comment',
      user: '김건축',
      action: '새로운 댓글 작성',
      timestamp: '2025-01-06T14:15:00Z',
      project: '친환경 주택 설계',
      details: '외벽 단열재 변경 제안에 대한 검토 완료',
    },
    {
      id: '3',
      type: 'file',
      user: '박디자인',
      action: '파일 업로드',
      timestamp: '2025-01-06T13:45:00Z',
      project: '상업용 빌딩 구조 설계',
      details: '1층 평면도 수정본 (v2.1)',
    },
    {
      id: '4',
      type: 'update',
      user: '이구조',
      action: '프로젝트 상태 업데이트',
      timestamp: '2025-01-06T13:20:00Z',
      project: '친환경 주택 설계',
      details: '구조 계산 완료 → 진행중으로 변경',
    },
    {
      id: '5',
      type: 'meeting',
      user: '김건축',
      action: '회의 일정 생성',
      timestamp: '2025-01-06T12:30:00Z',
      project: '아파트 단지 계획',
      details: '내일 오후 2시 - 설계 검토 회의',
    },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return '#10b981';
      case 'busy':
        return '#f59e0b';
      case 'offline':
        return '#6b7280';
      default:
        return '#6b7280';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'online':
        return '온라인';
      case 'busy':
        return '바쁨';
      case 'offline':
        return '오프라인';
      default:
        return '알 수 없음';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return '#ef4444';
      case 'medium':
        return '#f59e0b';
      case 'low':
        return '#10b981';
      default:
        return '#6b7280';
    }
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'comment':
        return <Comment sx={{ color: '#2563eb' }} />;
      case 'update':
        return <Update sx={{ color: '#10b981' }} />;
      case 'file':
        return <CloudUpload sx={{ color: '#8b5cf6' }} />;
      case 'ai_analysis':
        return <Analytics sx={{ color: '#f59e0b' }} />;
      case 'meeting':
        return <Schedule sx={{ color: '#06b6d4' }} />;
      default:
        return <AccessTime sx={{ color: '#6b7280' }} />;
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    
    if (minutes < 60) {
      return `${minutes}분 전`;
    } else if (hours < 24) {
      return `${hours}시간 전`;
    } else {
      return date.toLocaleDateString('ko-KR');
    }
  };

  const handleInviteMember = () => {
    // TODO: 멤버 초대 API 호출
    console.log('멤버 초대:', { email: inviteEmail, role: inviteRole });
    setInviteDialogOpen(false);
    setInviteEmail('');
    setInviteRole('viewer');
  };

  const TabPanel: React.FC<{ children: React.ReactNode; value: number; index: number }> = ({
    children,
    value,
    index,
  }) => {
    return (
      <div role="tabpanel" hidden={value !== index}>
        {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
      </div>
    );
  };

  return (
    <Container maxWidth="xl">
      {/* 헤더 */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 800, mb: 1 }}>
          팀 협업 센터 👥
        </Typography>
        <Typography variant="h6" color="textSecondary">
          팀원들과 실시간으로 협업하고 프로젝트를 관리하세요
        </Typography>
      </Box>

      {/* 액션 버튼들 */}
      <Box sx={{ mb: 3, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        <Button
          variant="contained"
          startIcon={<PersonAdd />}
          onClick={() => setInviteDialogOpen(true)}
          sx={{ borderRadius: 2, fontWeight: 600 }}
        >
          멤버 초대
        </Button>
        <Button
          variant="outlined"
          startIcon={<VideoCall />}
          onClick={() => setMeetingDialogOpen(true)}
          sx={{ borderRadius: 2, fontWeight: 600 }}
        >
          회의 시작
        </Button>
        <Button
          variant="outlined"
          startIcon={<Chat />}
          sx={{ borderRadius: 2, fontWeight: 600 }}
        >
          채팅룸
        </Button>
        <Button
          variant="outlined"
          startIcon={<Share />}
          sx={{ borderRadius: 2, fontWeight: 600 }}
        >
          프로젝트 공유
        </Button>
      </Box>

      {/* 탭 네비게이션 */}
      <Paper sx={{ mb: 3, borderRadius: 2 }}>
        <Tabs
          value={selectedTab}
          onChange={(_, newValue) => setSelectedTab(newValue)}
          sx={{ px: 2 }}
        >
          <Tab label="팀 멤버" />
          <Tab label="프로젝트" />
          <Tab label="활동 기록" />
          <Tab label="파일 공유" />
        </Tabs>
      </Paper>

      {/* 팀 멤버 탭 */}
      <TabPanel value={selectedTab} index={0}>
        <Grid container spacing={3}>
          {teamMembers.map((member) => (
            <Grid item xs={12} sm={6} lg={4} key={member.id}>
              <Card
                sx={{
                  borderRadius: 3,
                  boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
                  '&:hover': {
                    boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
                    transform: 'translateY(-2px)',
                  },
                  transition: 'all 0.3s ease',
                }}
              >
                <CardContent sx={{ p: 3 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Badge
                      overlap="circular"
                      anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                      variant="dot"
                      sx={{
                        '& .MuiBadge-badge': {
                          bgcolor: getStatusColor(member.status),
                          width: 12,
                          height: 12,
                          borderRadius: '50%',
                          border: '2px solid white',
                        },
                      }}
                    >
                      <Avatar
                        sx={{
                          width: 64,
                          height: 64,
                          bgcolor: '#2563eb',
                          fontSize: '1.5rem',
                          fontWeight: 700,
                        }}
                      >
                        {member.name.charAt(0)}
                      </Avatar>
                    </Badge>
                    <Box sx={{ ml: 2, flexGrow: 1 }}>
                      <Typography variant="h6" sx={{ fontWeight: 700 }}>
                        {member.name}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        {member.role}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        {getStatusText(member.status)} • {member.lastActivity}
                      </Typography>
                    </Box>
                    <IconButton size="small">
                      <MoreVert />
                    </IconButton>
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 600, mb: 1, display: 'block' }}>
                      권한
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {member.permissions.map((permission) => (
                        <Chip
                          key={permission}
                          label={permission}
                          size="small"
                          sx={{
                            fontSize: '0.7rem',
                            height: 20,
                            bgcolor: '#f1f5f9',
                            color: '#475569',
                          }}
                        />
                      ))}
                    </Box>
                  </Box>

                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button
                      size="small"
                      startIcon={<Chat />}
                      sx={{ flex: 1, fontWeight: 500 }}
                    >
                      채팅
                    </Button>
                    <Button
                      size="small"
                      startIcon={<VideoCall />}
                      sx={{ flex: 1, fontWeight: 500 }}
                    >
                      통화
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      {/* 프로젝트 탭 */}
      <TabPanel value={selectedTab} index={1}>
        <Grid container spacing={3}>
          {projects.map((project) => (
            <Grid item xs={12} key={project.id}>
              <Card sx={{ borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}>
                <CardContent sx={{ p: 3 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="h6" sx={{ fontWeight: 700, mb: 1 }}>
                        {project.name}
                      </Typography>
                      <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                        {project.description}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                        <Chip
                          label={project.status}
                          size="small"
                          color="primary"
                          sx={{ fontWeight: 500 }}
                        />
                        <Chip
                          label={project.priority}
                          size="small"
                          sx={{
                            bgcolor: `${getPriorityColor(project.priority)}15`,
                            color: getPriorityColor(project.priority),
                            fontWeight: 500,
                          }}
                        />
                      </Box>
                    </Box>
                    <Box sx={{ textAlign: 'right' }}>
                      <Typography variant="caption" color="textSecondary">
                        마지막 업데이트: {formatTimestamp(project.lastUpdate)}
                      </Typography>
                    </Box>
                  </Box>

                  <Box sx={{ mb: 3 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2" color="textSecondary">
                        진행률
                      </Typography>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {project.progress}%
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={project.progress}
                      sx={{
                        height: 8,
                        borderRadius: 4,
                        bgcolor: '#e2e8f0',
                        '& .MuiLinearProgress-bar': {
                          bgcolor: project.progress >= 80 ? '#10b981' : '#2563eb',
                          borderRadius: 4,
                        },
                      }}
                    />
                  </Box>

                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Typography variant="body2" color="textSecondary" sx={{ mr: 1 }}>
                        팀원:
                      </Typography>
                      <Box sx={{ display: 'flex', ml: 1 }}>
                        {project.members.slice(0, 3).map((member, index) => (
                          <Tooltip key={member.id} title={member.name}>
                            <Avatar
                              sx={{
                                width: 32,
                                height: 32,
                                bgcolor: '#2563eb',
                                fontSize: '0.875rem',
                                ml: index > 0 ? -1 : 0,
                                border: '2px solid white',
                              }}
                            >
                              {member.name.charAt(0)}
                            </Avatar>
                          </Tooltip>
                        ))}
                        {project.members.length > 3 && (
                          <Avatar
                            sx={{
                              width: 32,
                              height: 32,
                              bgcolor: '#6b7280',
                              fontSize: '0.75rem',
                              ml: -1,
                              border: '2px solid white',
                            }}
                          >
                            +{project.members.length - 3}
                          </Avatar>
                        )}
                      </Box>
                    </Box>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Button
                        size="small"
                        startIcon={<Visibility />}
                        sx={{ fontWeight: 500 }}
                      >
                        보기
                      </Button>
                      <Button
                        size="small"
                        startIcon={<Edit />}
                        sx={{ fontWeight: 500 }}
                      >
                        편집
                      </Button>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      {/* 활동 기록 탭 */}
      <TabPanel value={selectedTab} index={2}>
        <Card sx={{ borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}>
          <CardContent sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ fontWeight: 700, mb: 3 }}>
              최근 활동 기록
            </Typography>
            <List>
              {activities.map((activity, index) => (
                <React.Fragment key={activity.id}>
                  <ListItem alignItems="flex-start">
                    <ListItemAvatar>
                      <Box
                        sx={{
                          width: 40,
                          height: 40,
                          borderRadius: '50%',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          bgcolor: '#f8fafc',
                        }}
                      >
                        {getActivityIcon(activity.type)}
                      </Box>
                    </ListItemAvatar>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                            {activity.user}
                          </Typography>
                          <Typography variant="body2">
                            {activity.action}
                          </Typography>
                          {activity.project && (
                            <Chip
                              label={activity.project}
                              size="small"
                              sx={{
                                height: 20,
                                fontSize: '0.7rem',
                                bgcolor: '#f1f5f9',
                                color: '#475569',
                              }}
                            />
                          )}
                        </Box>
                      }
                      secondary={
                        <Box sx={{ mt: 1 }}>
                          {activity.details && (
                            <Typography variant="body2" color="textSecondary" sx={{ mb: 0.5 }}>
                              {activity.details}
                            </Typography>
                          )}
                          <Typography variant="caption" color="textSecondary">
                            {formatTimestamp(activity.timestamp)}
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItem>
                  {index < activities.length - 1 && <Divider variant="inset" component="li" />}
                </React.Fragment>
              ))}
            </List>
          </CardContent>
        </Card>
      </TabPanel>

      {/* 파일 공유 탭 */}
      <TabPanel value={selectedTab} index={3}>
        <Card sx={{ borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}>
          <CardContent sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6" sx={{ fontWeight: 700 }}>
                공유 파일
              </Typography>
              <Button
                variant="contained"
                startIcon={<CloudUpload />}
                sx={{ borderRadius: 2, fontWeight: 600 }}
              >
                파일 업로드
              </Button>
            </Box>
            
            <Box sx={{ textAlign: 'center', py: 8 }}>
              <CloudUpload sx={{ fontSize: 64, color: '#6b7280', mb: 2 }} />
              <Typography variant="h6" color="textSecondary" sx={{ mb: 1 }}>
                파일 공유 기능
              </Typography>
              <Typography variant="body2" color="textSecondary">
                파일 업로드, 버전 관리, 공유 링크 생성 등의 기능이 여기에 구현됩니다.
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </TabPanel>

      {/* 멤버 초대 다이얼로그 */}
      <Dialog
        open={inviteDialogOpen}
        onClose={() => setInviteDialogOpen(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: { borderRadius: 3 },
        }}
      >
        <DialogTitle sx={{ pb: 2 }}>
          <Typography variant="h6" sx={{ fontWeight: 700 }}>
            팀 멤버 초대
          </Typography>
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="이메일 주소"
            type="email"
            value={inviteEmail}
            onChange={(e) => setInviteEmail(e.target.value)}
            margin="normal"
            sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
          />
          <TextField
            fullWidth
            label="역할"
            select
            value={inviteRole}
            onChange={(e) => setInviteRole(e.target.value)}
            margin="normal"
            sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
          >
            <MenuItem value="viewer">보기 전용</MenuItem>
            <MenuItem value="editor">편집자</MenuItem>
            <MenuItem value="admin">관리자</MenuItem>
          </TextField>
        </DialogContent>
        <DialogActions sx={{ p: 3, pt: 1 }}>
          <Button
            onClick={() => setInviteDialogOpen(false)}
            sx={{ borderRadius: 2, fontWeight: 600 }}
          >
            취소
          </Button>
          <Button
            onClick={handleInviteMember}
            variant="contained"
            sx={{ borderRadius: 2, fontWeight: 600 }}
          >
            초대 보내기
          </Button>
        </DialogActions>
      </Dialog>

      {/* 회의 시작 다이얼로그 */}
      <Dialog
        open={meetingDialogOpen}
        onClose={() => setMeetingDialogOpen(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: { borderRadius: 3 },
        }}
      >
        <DialogTitle sx={{ pb: 2 }}>
          <Typography variant="h6" sx={{ fontWeight: 700 }}>
            새 회의 시작
          </Typography>
        </DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2, borderRadius: 2 }}>
            화상 회의 기능은 추후 구현 예정입니다. 현재는 외부 서비스(Zoom, Teams 등)를 사용해주세요.
          </Alert>
          <TextField
            fullWidth
            label="회의 제목"
            margin="normal"
            sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
          />
          <TextField
            fullWidth
            label="회의 설명"
            multiline
            rows={3}
            margin="normal"
            sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
          />
        </DialogContent>
        <DialogActions sx={{ p: 3, pt: 1 }}>
          <Button
            onClick={() => setMeetingDialogOpen(false)}
            sx={{ borderRadius: 2, fontWeight: 600 }}
          >
            취소
          </Button>
          <Button
            onClick={() => setMeetingDialogOpen(false)}
            variant="contained"
            sx={{ borderRadius: 2, fontWeight: 600 }}
          >
            회의 시작
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Collaboration;