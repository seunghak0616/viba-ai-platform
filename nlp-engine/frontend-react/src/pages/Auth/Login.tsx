import React, { useState } from 'react';
import {
  Container,
  Paper,
  Box,
  TextField,
  Button,
  Typography,
  Link,
  Alert,
  CircularProgress,
  Divider,
  Card,
  CardContent,
} from '@mui/material';
import { Architecture, Login as LoginIcon } from '@mui/icons-material';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { LoginCredentials } from '../../types/auth';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const { login, state } = useAuth();
  
  const [credentials, setCredentials] = useState<LoginCredentials>({
    username: '',
    password: '',
  });
  
  const [errors, setErrors] = useState<Partial<LoginCredentials>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // 입력값 변경 핸들러
  const handleChange = (field: keyof LoginCredentials) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setCredentials(prev => ({
      ...prev,
      [field]: event.target.value,
    }));
    
    // 에러 클리어
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: undefined,
      }));
    }
  };

  // 폼 검증
  const validateForm = (): boolean => {
    const newErrors: Partial<LoginCredentials> = {};

    if (!credentials.username.trim()) {
      newErrors.username = '사용자명을 입력해주세요';
    }

    if (!credentials.password) {
      newErrors.password = '비밀번호를 입력해주세요';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // 로그인 처리
  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    
    try {
      await login(credentials);
      navigate('/dashboard');
    } catch (error) {
      // 에러는 AuthContext에서 처리됨
    } finally {
      setIsSubmitting(false);
    }
  };

  // 데모 계정 로그인
  const handleDemoLogin = async () => {
    setIsSubmitting(true);
    
    try {
      await login({
        username: 'demo',
        password: 'demo123',
      });
      navigate('/dashboard');
    } catch (error) {
      // 에러는 AuthContext에서 처리됨
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
        display: 'flex',
        alignItems: 'center',
        py: 4,
      }}
    >
      <Container maxWidth="sm">
        <Paper
          elevation={0}
          sx={{
            p: { xs: 3, sm: 4 },
            borderRadius: 3,
            boxShadow: '0 20px 60px rgba(0,0,0,0.1)',
            border: '1px solid #e2e8f0',
          }}
        >
          {/* 헤더 */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Box
              sx={{
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: 80,
                height: 80,
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)',
                color: 'white',
                mb: 2,
              }}
            >
              <Architecture fontSize="large" />
            </Box>
            <Typography variant="h4" sx={{ fontWeight: 800, mb: 1 }}>
              VIBA AI 로그인
            </Typography>
            <Typography variant="body1" color="textSecondary">
              건축 설계 플랫폼에 오신 것을 환영합니다
            </Typography>
          </Box>

          {/* 에러 메시지 */}
          {state.error && (
            <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
              {state.error}
            </Alert>
          )}

          {/* 로그인 폼 */}
          <Box component="form" onSubmit={handleSubmit} noValidate>
            <TextField
              fullWidth
              label="사용자명"
              value={credentials.username}
              onChange={handleChange('username')}
              error={!!errors.username}
              helperText={errors.username}
              margin="normal"
              autoComplete="username"
              autoFocus
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                },
              }}
            />

            <TextField
              fullWidth
              label="비밀번호"
              type="password"
              value={credentials.password}
              onChange={handleChange('password')}
              error={!!errors.password}
              helperText={errors.password}
              margin="normal"
              autoComplete="current-password"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                },
              }}
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              disabled={isSubmitting}
              startIcon={isSubmitting ? <CircularProgress size={20} /> : <LoginIcon />}
              sx={{
                mt: 3,
                mb: 2,
                py: 1.5,
                fontSize: '1.1rem',
                fontWeight: 600,
                borderRadius: 2,
                background: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%)',
                },
              }}
            >
              {isSubmitting ? '로그인 중...' : '로그인'}
            </Button>

            {/* 링크들 */}
            <Box sx={{ textAlign: 'center', mb: 3 }}>
              <Link
                component={RouterLink}
                to="/forgot-password"
                variant="body2"
                sx={{ textDecoration: 'none', fontWeight: 500 }}
              >
                비밀번호를 잊으셨나요?
              </Link>
            </Box>

            <Divider sx={{ my: 3 }}>
              <Typography variant="body2" color="textSecondary">
                또는
              </Typography>
            </Divider>

            {/* 데모 로그인 */}
            <Card
              sx={{
                mb: 3,
                border: '1px solid #e2e8f0',
                borderRadius: 2,
                cursor: 'pointer',
                '&:hover': {
                  borderColor: '#2563eb',
                  boxShadow: '0 4px 12px rgba(37, 99, 235, 0.15)',
                },
                transition: 'all 0.2s ease',
              }}
              onClick={handleDemoLogin}
            >
              <CardContent sx={{ py: 2 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                  🚀 데모 계정으로 체험하기
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  회원가입 없이 바로 VIBA AI를 체험해보세요
                </Typography>
              </CardContent>
            </Card>

            {/* 회원가입 링크 */}
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="body2">
                계정이 없으신가요?{' '}
                <Link
                  component={RouterLink}
                  to="/register"
                  sx={{
                    fontWeight: 600,
                    textDecoration: 'none',
                    color: '#2563eb',
                    '&:hover': {
                      textDecoration: 'underline',
                    },
                  }}
                >
                  회원가입
                </Link>
              </Typography>
            </Box>
          </Box>
        </Paper>

        {/* 하단 정보 */}
        <Box sx={{ textAlign: 'center', mt: 4 }}>
          <Typography variant="caption" color="textSecondary">
            © 2025 VIBA AI. 모든 권리 보유.
          </Typography>
        </Box>
      </Container>
    </Box>
  );
};

export default Login;