import React from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  Avatar,
  Paper,
} from '@mui/material';
import {
  Architecture,
  AutoAwesome,
  Speed,
  Eco,
  TrendingUp,
  Group,
  ArrowForward,
  CheckCircle,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const { state } = useAuth();
  
  const features = [
    {
      icon: <AutoAwesome fontSize="large" />,
      title: 'AI 기반 설계',
      description: '인공지능이 최적의 건축 설계를 제안합니다',
      color: '#2563eb',
    },
    {
      icon: <Eco fontSize="large" />,
      title: '친환경 재료',
      description: '지속가능한 건축을 위한 친환경 재료 추천',
      color: '#10b981',
    },
    {
      icon: <Speed fontSize="large" />,
      title: '빠른 처리',
      description: '실시간으로 설계 요청을 처리하고 결과 제공',
      color: '#f59e0b',
    },
    {
      icon: <TrendingUp fontSize="large" />,
      title: '성능 분석',
      description: '건물의 에너지 효율성과 구조 안전성 분석',
      color: '#8b5cf6',
    },
  ];

  const stats = [
    { number: '10,000+', label: '처리된 프로젝트' },
    { number: '99.9%', label: '시스템 가용성' },
    { number: '0.1초', label: '평균 응답 시간' },
    { number: '500+', label: '등록된 사용자' },
  ];

  const testimonials = [
    {
      name: '김건축',
      role: '건축사',
      company: '현대건축사무소',
      content: 'VIBA AI 덕분에 설계 시간이 80% 단축되었습니다. 정말 혁신적인 도구입니다.',
      avatar: 'K',
    },
    {
      name: '이설계',
      role: '구조 엔지니어',
      company: '삼성엔지니어링',
      content: '구조 계산과 안전성 검토가 자동화되어 업무 효율성이 크게 향상되었습니다.',
      avatar: 'L',
    },
    {
      name: '박인테리어',
      role: '인테리어 디자이너',
      company: '프리랜서',
      content: '공간 배치부터 재료 선택까지 AI가 완벽하게 도와줍니다.',
      avatar: 'P',
    },
  ];

  return (
    <Box>
      {/* 히어로 섹션 */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)',
          color: 'white',
          py: { xs: 8, md: 12 },
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* 배경 패턴 */}
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
            opacity: 0.3,
          }}
        />
        
        <Container maxWidth="lg" sx={{ position: 'relative' }}>
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={6}>
              <Box>
                <Chip 
                  label="AI 건축 플랫폼" 
                  sx={{ 
                    bgcolor: 'rgba(255,255,255,0.2)', 
                    color: 'white',
                    fontWeight: 600,
                    mb: 2,
                  }} 
                />
                <Typography 
                  variant="h1" 
                  sx={{ 
                    fontSize: { xs: '2.5rem', md: '3.5rem' },
                    fontWeight: 800,
                    mb: 2,
                    lineHeight: 1.2,
                  }}
                >
                  차세대 AI 건축 설계 플랫폼
                </Typography>
                <Typography 
                  variant="h6" 
                  sx={{ 
                    opacity: 0.9, 
                    mb: 4,
                    fontSize: '1.25rem',
                    lineHeight: 1.6,
                  }}
                >
                  인공지능의 힘으로 건축 설계를 혁신하세요. 
                  친환경 재료 추천부터 구조 설계까지, 모든 것을 한 번에.
                </Typography>
                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                  {state.isAuthenticated ? (
                    <Button
                      variant="contained"
                      size="large"
                      endIcon={<ArrowForward />}
                      onClick={() => navigate('/dashboard')}
                      sx={{
                        bgcolor: 'white',
                        color: '#2563eb',
                        fontWeight: 700,
                        px: 4,
                        py: 1.5,
                        '&:hover': {
                          bgcolor: '#f8fafc',
                          transform: 'translateY(-2px)',
                          boxShadow: '0 8px 25px rgba(0,0,0,0.2)',
                        },
                      }}
                    >
                      대시보드로 이동
                    </Button>
                  ) : (
                    <>
                      <Button
                        variant="contained"
                        size="large"
                        endIcon={<ArrowForward />}
                        onClick={() => navigate('/register')}
                        sx={{
                          bgcolor: 'white',
                          color: '#2563eb',
                          fontWeight: 700,
                          px: 4,
                          py: 1.5,
                          '&:hover': {
                            bgcolor: '#f8fafc',
                            transform: 'translateY(-2px)',
                            boxShadow: '0 8px 25px rgba(0,0,0,0.2)',
                          },
                        }}
                      >
                        무료로 시작하기
                      </Button>
                      <Button
                        variant="outlined"
                        size="large"
                        onClick={() => navigate('/login')}
                        sx={{
                          borderColor: 'white',
                          color: 'white',
                          fontWeight: 600,
                          px: 4,
                          py: 1.5,
                          '&:hover': {
                            borderColor: 'white',
                            bgcolor: 'rgba(255,255,255,0.1)',
                          },
                        }}
                      >
                        로그인
                      </Button>
                    </>
                  )}
                </Box>
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <Box sx={{ textAlign: 'center' }}>
                <Architecture sx={{ fontSize: '20rem', opacity: 0.3 }} />
              </Box>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* 통계 섹션 */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Grid container spacing={4}>
          {stats.map((stat, index) => (
            <Grid item xs={6} md={3} key={index}>
              <Paper
                elevation={0}
                sx={{
                  p: 3,
                  textAlign: 'center',
                  background: 'linear-gradient(135deg, #f8fafc 0%, #ffffff 100%)',
                  border: '1px solid #e2e8f0',
                  borderRadius: 3,
                  '&:hover': {
                    boxShadow: '0 8px 25px rgba(0,0,0,0.1)',
                    transform: 'translateY(-4px)',
                  },
                  transition: 'all 0.3s ease',
                }}
              >
                <Typography 
                  variant="h3" 
                  sx={{ 
                    fontWeight: 800, 
                    color: '#2563eb',
                    mb: 1,
                  }}
                >
                  {stat.number}
                </Typography>
                <Typography variant="body2" color="textSecondary" sx={{ fontWeight: 500 }}>
                  {stat.label}
                </Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* 주요 기능 섹션 */}
      <Box sx={{ bgcolor: '#f8fafc', py: 8 }}>
        <Container maxWidth="lg">
          <Box sx={{ textAlign: 'center', mb: 6 }}>
            <Typography 
              variant="h2" 
              sx={{ 
                fontWeight: 800, 
                mb: 2,
                background: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              핵심 기능
            </Typography>
            <Typography variant="h6" color="textSecondary" sx={{ maxWidth: 600, mx: 'auto' }}>
              VIBA AI가 제공하는 혁신적인 건축 설계 도구들을 만나보세요
            </Typography>
          </Box>
          
          <Grid container spacing={4}>
            {features.map((feature, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <Card
                  sx={{
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    border: 'none',
                    borderRadius: 3,
                    '&:hover': {
                      transform: 'translateY(-8px)',
                      boxShadow: '0 12px 40px rgba(0,0,0,0.15)',
                    },
                    transition: 'all 0.3s ease',
                  }}
                >
                  <CardContent sx={{ flexGrow: 1, textAlign: 'center', p: 3 }}>
                    <Box
                      sx={{
                        width: 80,
                        height: 80,
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        mx: 'auto',
                        mb: 2,
                        background: `linear-gradient(135deg, ${feature.color}20 0%, ${feature.color}10 100%)`,
                        color: feature.color,
                      }}
                    >
                      {feature.icon}
                    </Box>
                    <Typography variant="h6" sx={{ fontWeight: 700, mb: 1 }}>
                      {feature.title}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      {feature.description}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* 사용자 후기 섹션 */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Box sx={{ textAlign: 'center', mb: 6 }}>
          <Typography 
            variant="h2" 
            sx={{ 
              fontWeight: 800, 
              mb: 2,
              background: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            사용자 후기
          </Typography>
          <Typography variant="h6" color="textSecondary" sx={{ maxWidth: 600, mx: 'auto' }}>
            전문가들이 직접 경험한 VIBA AI의 놀라운 성능
          </Typography>
        </Box>
        
        <Grid container spacing={4}>
          {testimonials.map((testimonial, index) => (
            <Grid item xs={12} md={4} key={index}>
              <Card
                sx={{
                  height: '100%',
                  p: 3,
                  borderRadius: 3,
                  border: '1px solid #e2e8f0',
                  '&:hover': {
                    boxShadow: '0 8px 25px rgba(0,0,0,0.1)',
                    transform: 'translateY(-4px)',
                  },
                  transition: 'all 0.3s ease',
                }}
              >
                <CardContent>
                  <Typography variant="body1" sx={{ mb: 3, fontStyle: 'italic' }}>
                    "{testimonial.content}"
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Avatar 
                      sx={{ 
                        bgcolor: '#2563eb', 
                        mr: 2,
                        width: 48,
                        height: 48,
                        fontSize: '1.2rem',
                        fontWeight: 700,
                      }}
                    >
                      {testimonial.avatar}
                    </Avatar>
                    <Box>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                        {testimonial.name}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        {testimonial.role} • {testimonial.company}
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* CTA 섹션 */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #1f2937 0%, #374151 100%)',
          color: 'white',
          py: 8,
        }}
      >
        <Container maxWidth="md" sx={{ textAlign: 'center' }}>
          <Typography variant="h3" sx={{ fontWeight: 800, mb: 2 }}>
            지금 바로 시작해보세요
          </Typography>
          <Typography variant="h6" sx={{ opacity: 0.9, mb: 4 }}>
            무료 계정을 만들고 VIBA AI의 혁신적인 건축 설계 도구를 체험해보세요
          </Typography>
          {!state.isAuthenticated && (
            <Button
              variant="contained"
              size="large"
              endIcon={<ArrowForward />}
              onClick={() => navigate('/register')}
              sx={{
                bgcolor: '#2563eb',
                fontWeight: 700,
                px: 6,
                py: 2,
                fontSize: '1.1rem',
                '&:hover': {
                  bgcolor: '#1d4ed8',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 8px 25px rgba(37, 99, 235, 0.4)',
                },
              }}
            >
              무료로 시작하기
            </Button>
          )}
        </Container>
      </Box>
    </Box>
  );
};

export default Home;