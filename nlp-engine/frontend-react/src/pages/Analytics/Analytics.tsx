import React, { useState } from 'react';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Paper,
  LinearProgress,
  Chip,
  Tab,
  Tabs,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  Divider,
} from '@mui/material';
import {
  TrendingUp,
  Architecture,
  Speed,
  Eco,
  MonetizationOn,
  Schedule,
  Analytics as AnalyticsIcon,
  Assessment,
  Timeline,
  PieChart,
  BarChart,
  ShowChart,
  Engineering,
  Science,
  Build,
  Palette,
  AccountBalance,
  Star,
  CheckCircle,
  Warning,
  Error,
} from '@mui/icons-material';

interface AnalyticsData {
  id: string;
  title: string;
  value: string | number;
  change: number;
  icon: React.ReactNode;
  color: string;
  description: string;
}

interface ProjectAnalytics {
  id: string;
  name: string;
  progress: number;
  efficiency: number;
  cost_variance: number;
  sustainability_score: number;
  status: 'excellent' | 'good' | 'average' | 'needs_attention';
}

const Analytics: React.FC = () => {
  const [selectedTab, setSelectedTab] = useState(0);
  const [selectedPeriod, setSelectedPeriod] = useState('month');

  // 전체 분석 데이터
  const overallAnalytics: AnalyticsData[] = [
    {
      id: 'projects',
      title: '진행 중인 프로젝트',
      value: 12,
      change: 8.5,
      icon: <Architecture />,
      color: '#2563eb',
      description: '이번 달 대비 증가',
    },
    {
      id: 'ai_usage',
      title: 'AI 분석 사용량',
      value: '1,247',
      change: 23.1,
      icon: <AnalyticsIcon />,
      color: '#10b981',
      description: '분석 요청 수',
    },
    {
      id: 'cost_savings',
      title: '비용 절감액',
      value: '₩2.3B',
      change: 15.2,
      icon: <MonetizationOn />,
      color: '#f59e0b',
      description: 'AI 최적화 결과',
    },
    {
      id: 'efficiency',
      title: '설계 효율성',
      value: '94%',
      change: 5.8,
      icon: <Speed />,
      color: '#8b5cf6',
      description: '평균 프로젝트 효율',
    },
    {
      id: 'sustainability',
      title: '친환경 점수',
      value: '8.7/10',
      change: 12.3,
      icon: <Eco />,
      color: '#06b6d4',
      description: '평균 지속가능성',
    },
    {
      id: 'completion_rate',
      title: '완료율',
      value: '89%',
      change: 3.2,
      icon: <CheckCircle />,
      color: '#84cc16',
      description: '예정 일정 내 완료',
    },
  ];

  // 프로젝트별 분석
  const projectAnalytics: ProjectAnalytics[] = [
    {
      id: '1',
      name: '친환경 주택 설계',
      progress: 85,
      efficiency: 92,
      cost_variance: -5.2,
      sustainability_score: 9.1,
      status: 'excellent',
    },
    {
      id: '2',
      name: '상업용 빌딩 구조 설계',
      progress: 67,
      efficiency: 88,
      cost_variance: 3.1,
      sustainability_score: 7.8,
      status: 'good',
    },
    {
      id: '3',
      name: '카페 인테리어 디자인',
      progress: 100,
      efficiency: 95,
      cost_variance: -12.5,
      sustainability_score: 8.3,
      status: 'excellent',
    },
    {
      id: '4',
      name: '아파트 단지 계획',
      progress: 34,
      efficiency: 78,
      cost_variance: 8.7,
      sustainability_score: 6.9,
      status: 'needs_attention',
    },
  ];

  // AI 에이전트 성능 데이터
  const aiAgentPerformance = [
    {
      id: 'materials_specialist',
      name: '재료 전문가 AI',
      icon: <Science />,
      color: '#10b981',
      usage: 89,
      accuracy: 94,
      satisfaction: 4.8,
      total_requests: 234,
    },
    {
      id: 'design_theorist',
      name: '설계 이론가 AI',
      icon: <Architecture />,
      color: '#2563eb',
      usage: 76,
      accuracy: 91,
      satisfaction: 4.6,
      total_requests: 187,
    },
    {
      id: 'structural_engineer',
      name: '구조 엔지니어 AI',
      icon: <Engineering />,
      color: '#f59e0b',
      usage: 82,
      accuracy: 96,
      satisfaction: 4.9,
      total_requests: 156,
    },
    {
      id: 'cost_estimator',
      name: '비용 추정 AI',
      icon: <MonetizationOn />,
      color: '#06b6d4',
      usage: 71,
      accuracy: 88,
      satisfaction: 4.4,
      total_requests: 203,
    },
    {
      id: 'mep_specialist',
      name: 'MEP 전문가 AI',
      icon: <AccountBalance />,
      color: '#ef4444',
      usage: 65,
      accuracy: 87,
      satisfaction: 4.3,
      total_requests: 142,
    },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'excellent':
        return '#10b981';
      case 'good':
        return '#06b6d4';
      case 'average':
        return '#f59e0b';
      case 'needs_attention':
        return '#ef4444';
      default:
        return '#6b7280';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'excellent':
        return '우수';
      case 'good':
        return '양호';
      case 'average':
        return '보통';
      case 'needs_attention':
        return '주의 필요';
      default:
        return '알 수 없음';
    }
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
          VIBA AI 분석 대시보드 📊
        </Typography>
        <Typography variant="h6" color="textSecondary">
          프로젝트와 AI 성능을 한눈에 확인하세요
        </Typography>
      </Box>

      {/* 기간 선택 */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'flex-end' }}>
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>기간</InputLabel>
          <Select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value)}
            label="기간"
            sx={{ borderRadius: 2 }}
          >
            <MenuItem value="week">지난 주</MenuItem>
            <MenuItem value="month">지난 달</MenuItem>
            <MenuItem value="quarter">지난 분기</MenuItem>
            <MenuItem value="year">지난 해</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {/* 탭 네비게이션 */}
      <Paper sx={{ mb: 3, borderRadius: 2 }}>
        <Tabs
          value={selectedTab}
          onChange={(_, newValue) => setSelectedTab(newValue)}
          sx={{ px: 2 }}
        >
          <Tab label="전체 개요" />
          <Tab label="프로젝트 분석" />
          <Tab label="AI 성능" />
          <Tab label="트렌드 분석" />
        </Tabs>
      </Paper>

      {/* 전체 개요 탭 */}
      <TabPanel value={selectedTab} index={0}>
        <Grid container spacing={3}>
          {overallAnalytics.map((item) => (
            <Grid item xs={12} sm={6} lg={4} key={item.id}>
              <Card
                sx={{
                  borderRadius: 3,
                  boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
                  border: 'none',
                  '&:hover': {
                    boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
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
                        borderRadius: 2,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        bgcolor: `${item.color}15`,
                        color: item.color,
                        mr: 2,
                      }}
                    >
                      {item.icon}
                    </Box>
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="body2" color="textSecondary" sx={{ fontWeight: 600 }}>
                        {item.title}
                      </Typography>
                      <Typography variant="h4" sx={{ fontWeight: 800, color: item.color }}>
                        {item.value}
                      </Typography>
                    </Box>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="textSecondary">
                      {item.description}
                    </Typography>
                    <Chip
                      icon={<TrendingUp />}
                      label={`+${item.change}%`}
                      color="success"
                      size="small"
                      sx={{ fontWeight: 600 }}
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      {/* 프로젝트 분석 탭 */}
      <TabPanel value={selectedTab} index={1}>
        <Grid container spacing={3}>
          {projectAnalytics.map((project) => (
            <Grid item xs={12} key={project.id}>
              <Card sx={{ borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}>
                <CardContent sx={{ p: 3 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                    <Typography variant="h6" sx={{ fontWeight: 700 }}>
                      {project.name}
                    </Typography>
                    <Chip
                      label={getStatusText(project.status)}
                      sx={{
                        bgcolor: `${getStatusColor(project.status)}15`,
                        color: getStatusColor(project.status),
                        fontWeight: 600,
                      }}
                    />
                  </Box>
                  
                  <Grid container spacing={3}>
                    <Grid item xs={12} sm={6} md={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                          진행률
                        </Typography>
                        <Typography variant="h4" sx={{ fontWeight: 800, mb: 1 }}>
                          {project.progress}%
                        </Typography>
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
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                          효율성
                        </Typography>
                        <Typography variant="h4" sx={{ fontWeight: 800, mb: 1 }}>
                          {project.efficiency}%
                        </Typography>
                        <LinearProgress
                          variant="determinate"
                          value={project.efficiency}
                          sx={{
                            height: 8,
                            borderRadius: 4,
                            bgcolor: '#e2e8f0',
                            '& .MuiLinearProgress-bar': {
                              bgcolor: '#8b5cf6',
                              borderRadius: 4,
                            },
                          }}
                        />
                      </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                          비용 차이
                        </Typography>
                        <Typography 
                          variant="h4" 
                          sx={{ 
                            fontWeight: 800, 
                            mb: 1,
                            color: project.cost_variance < 0 ? '#10b981' : '#ef4444'
                          }}
                        >
                          {project.cost_variance > 0 ? '+' : ''}{project.cost_variance}%
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          {project.cost_variance < 0 ? '예산 절감' : '예산 초과'}
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                          친환경 점수
                        </Typography>
                        <Typography variant="h4" sx={{ fontWeight: 800, mb: 1, color: '#10b981' }}>
                          {project.sustainability_score}/10
                        </Typography>
                        <LinearProgress
                          variant="determinate"
                          value={project.sustainability_score * 10}
                          sx={{
                            height: 8,
                            borderRadius: 4,
                            bgcolor: '#e2e8f0',
                            '& .MuiLinearProgress-bar': {
                              bgcolor: '#10b981',
                              borderRadius: 4,
                            },
                          }}
                        />
                      </Box>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      {/* AI 성능 탭 */}
      <TabPanel value={selectedTab} index={2}>
        <Grid container spacing={3}>
          {aiAgentPerformance.map((agent) => (
            <Grid item xs={12} md={6} key={agent.id}>
              <Card sx={{ borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}>
                <CardContent sx={{ p: 3 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                    <Avatar
                      sx={{
                        width: 56,
                        height: 56,
                        bgcolor: `${agent.color}15`,
                        color: agent.color,
                        mr: 2,
                      }}
                    >
                      {agent.icon}
                    </Avatar>
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="h6" sx={{ fontWeight: 700 }}>
                        {agent.name}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        총 {agent.total_requests}건 처리
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <Star sx={{ color: '#f59e0b', fontSize: 20 }} />
                      <Typography variant="h6" sx={{ fontWeight: 700 }}>
                        {agent.satisfaction}
                      </Typography>
                    </Box>
                  </Box>
                  
                  <Box sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2" color="textSecondary">
                        사용량
                      </Typography>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {agent.usage}%
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={agent.usage}
                      sx={{
                        height: 6,
                        borderRadius: 3,
                        bgcolor: '#e2e8f0',
                        '& .MuiLinearProgress-bar': {
                          bgcolor: agent.color,
                          borderRadius: 3,
                        },
                      }}
                    />
                  </Box>
                  
                  <Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2" color="textSecondary">
                        정확도
                      </Typography>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {agent.accuracy}%
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={agent.accuracy}
                      sx={{
                        height: 6,
                        borderRadius: 3,
                        bgcolor: '#e2e8f0',
                        '& .MuiLinearProgress-bar': {
                          bgcolor: '#10b981',
                          borderRadius: 3,
                        },
                      }}
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      {/* 트렌드 분석 탭 */}
      <TabPanel value={selectedTab} index={3}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card sx={{ borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}>
              <CardContent sx={{ p: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: 700, mb: 3 }}>
                  주요 트렌드 분석
                </Typography>
                
                <Grid container spacing={3}>
                  <Grid item xs={12} md={8}>
                    <Box sx={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: '#f8fafc', borderRadius: 2 }}>
                      <Box sx={{ textAlign: 'center' }}>
                        <ShowChart sx={{ fontSize: 64, color: '#6b7280', mb: 2 }} />
                        <Typography variant="h6" color="textSecondary">
                          차트 영역
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          실제 프로젝트에서는 Chart.js나 D3.js를 사용하여 구현
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                  
                  <Grid item xs={12} md={4}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
                      주요 인사이트
                    </Typography>
                    <List>
                      <ListItem>
                        <ListItemIcon>
                          <TrendingUp sx={{ color: '#10b981' }} />
                        </ListItemIcon>
                        <ListItemText 
                          primary="AI 활용도 23% 증가"
                          secondary="이전 달 대비 AI 에이전트 사용량 증가"
                        />
                      </ListItem>
                      <Divider />
                      <ListItem>
                        <ListItemIcon>
                          <MonetizationOn sx={{ color: '#f59e0b' }} />
                        </ListItemIcon>
                        <ListItemText 
                          primary="평균 15% 비용 절감"
                          secondary="AI 최적화를 통한 비용 효율성 향상"
                        />
                      </ListItem>
                      <Divider />
                      <ListItem>
                        <ListItemIcon>
                          <Eco sx={{ color: '#06b6d4' }} />
                        </ListItemIcon>
                        <ListItemText 
                          primary="친환경성 점수 향상"
                          secondary="지속가능한 설계 솔루션 증가"
                        />
                      </ListItem>
                      <Divider />
                      <ListItem>
                        <ListItemIcon>
                          <Speed sx={{ color: '#8b5cf6' }} />
                        </ListItemIcon>
                        <ListItemText 
                          primary="설계 속도 35% 향상"
                          secondary="AI 지원으로 인한 프로세스 효율화"
                        />
                      </ListItem>
                    </List>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>
    </Container>
  );
};

export default Analytics;