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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  FormControlLabel,
} from '@mui/material';
import { Architecture, PersonAdd } from '@mui/icons-material';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { RegisterCredentials } from '../../types/auth';

const Register: React.FC = () => {
  const navigate = useNavigate();
  const { register, state } = useAuth();
  
  const [credentials, setCredentials] = useState<RegisterCredentials>({
    username: '',
    email: '',
    password: '',
    full_name: '',
    company: '',
    role: 'architect',
  });
  
  const [confirmPassword, setConfirmPassword] = useState('');
  const [agreedToTerms, setAgreedToTerms] = useState(false);
  const [errors, setErrors] = useState<Partial<RegisterCredentials & { confirmPassword: string; terms: string }>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // 역할 옵션
  const roleOptions = [
    { value: 'architect', label: '건축사' },
    { value: 'engineer', label: '구조 엔지니어' },
    { value: 'designer', label: '인테리어 디자이너' },
    { value: 'contractor', label: '시공업체' },
    { value: 'developer', label: '개발업체' },
    { value: 'student', label: '학생' },
    { value: 'other', label: '기타' },
  ];

  // 입력값 변경 핸들러
  const handleChange = (field: keyof RegisterCredentials) => (
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
    const newErrors: Partial<RegisterCredentials & { confirmPassword: string; terms: string }> = {};

    // 사용자명 검증
    if (!credentials.username.trim()) {
      newErrors.username = '사용자명을 입력해주세요';
    } else if (credentials.username.length < 3) {
      newErrors.username = '사용자명은 3자 이상이어야 합니다';
    } else if (!/^[a-zA-Z0-9_]+$/.test(credentials.username)) {
      newErrors.username = '사용자명은 영문, 숫자, 언더스코어만 사용 가능합니다';
    }

    // 이메일 검증
    if (!credentials.email.trim()) {
      newErrors.email = '이메일을 입력해주세요';
    } else if (!/^[^@]+@[^@]+\.[^@]+$/.test(credentials.email)) {
      newErrors.email = '올바른 이메일 형식이 아닙니다';
    }

    // 비밀번호 검증
    if (!credentials.password) {
      newErrors.password = '비밀번호를 입력해주세요';
    } else if (credentials.password.length < 6) {
      newErrors.password = '비밀번호는 6자 이상이어야 합니다';
    }

    // 비밀번호 확인
    if (!confirmPassword) {
      newErrors.confirmPassword = '비밀번호 확인을 입력해주세요';
    } else if (credentials.password !== confirmPassword) {
      newErrors.confirmPassword = '비밀번호가 일치하지 않습니다';
    }

    // 약관 동의
    if (!agreedToTerms) {
      newErrors.terms = '이용약관에 동의해주세요';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // 회원가입 처리
  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    
    try {
      await register(credentials);
      navigate('/login');
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
              VIBA AI 회원가입
            </Typography>
            <Typography variant="body1" color="textSecondary">
              무료 계정을 만들고 AI 건축 설계를 시작하세요
            </Typography>
          </Box>

          {/* 에러 메시지 */}
          {state.error && (
            <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
              {state.error}
            </Alert>
          )}

          {/* 회원가입 폼 */}
          <Box component="form" onSubmit={handleSubmit} noValidate>
            <TextField
              fullWidth
              label="사용자명"
              value={credentials.username}
              onChange={handleChange('username')}
              error={!!errors.username}
              helperText={errors.username || '영문, 숫자, 언더스코어만 사용 가능'}
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
              label="이메일"
              type="email"
              value={credentials.email}
              onChange={handleChange('email')}
              error={!!errors.email}
              helperText={errors.email}
              margin="normal"
              autoComplete="email"
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
              helperText={errors.password || '6자 이상 입력해주세요'}
              margin="normal"
              autoComplete="new-password"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                },
              }}
            />

            <TextField
              fullWidth
              label="비밀번호 확인"
              type="password"
              value={confirmPassword}
              onChange={(e) => {
                setConfirmPassword(e.target.value);
                if (errors.confirmPassword) {
                  setErrors(prev => ({ ...prev, confirmPassword: undefined }));
                }
              }}
              error={!!errors.confirmPassword}
              helperText={errors.confirmPassword}
              margin="normal"
              autoComplete="new-password"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                },
              }}
            />

            <TextField
              fullWidth
              label="이름 (선택사항)"
              value={credentials.full_name}
              onChange={handleChange('full_name')}
              margin="normal"
              autoComplete="name"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                },
              }}
            />

            <TextField
              fullWidth
              label="회사명 (선택사항)"
              value={credentials.company}
              onChange={handleChange('company')}
              margin="normal"
              autoComplete="organization"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                },
              }}
            />

            <FormControl fullWidth margin="normal">
              <InputLabel>직업/역할</InputLabel>
              <Select
                value={credentials.role}
                onChange={(e) => setCredentials(prev => ({ ...prev, role: e.target.value }))}
                label="직업/역할"
                sx={{ borderRadius: 2 }}
              >
                {roleOptions.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {/* 약관 동의 */}
            <FormControlLabel
              control={
                <Checkbox
                  checked={agreedToTerms}
                  onChange={(e) => {
                    setAgreedToTerms(e.target.checked);
                    if (errors.terms) {
                      setErrors(prev => ({ ...prev, terms: undefined }));
                    }
                  }}
                  color="primary"
                />
              }
              label={
                <Typography variant="body2">
                  <Link href="/terms" target="_blank" sx={{ textDecoration: 'none' }}>
                    이용약관
                  </Link>
                  {' 및 '}
                  <Link href="/privacy" target="_blank" sx={{ textDecoration: 'none' }}>
                    개인정보처리방침
                  </Link>
                  에 동의합니다
                </Typography>
              }
              sx={{ mt: 2, alignItems: 'flex-start' }}
            />
            {errors.terms && (
              <Typography variant="caption" color="error" sx={{ mt: 1, display: 'block' }}>
                {errors.terms}
              </Typography>
            )}

            <Button
              type="submit"
              fullWidth
              variant="contained"
              disabled={isSubmitting}
              startIcon={isSubmitting ? <CircularProgress size={20} /> : <PersonAdd />}
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
              {isSubmitting ? '가입 중...' : '회원가입'}
            </Button>

            {/* 로그인 링크 */}
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="body2">
                이미 계정이 있으신가요?{' '}
                <Link
                  component={RouterLink}
                  to="/login"
                  sx={{
                    fontWeight: 600,
                    textDecoration: 'none',
                    color: '#2563eb',
                    '&:hover': {
                      textDecoration: 'underline',
                    },
                  }}
                >
                  로그인
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

export default Register;