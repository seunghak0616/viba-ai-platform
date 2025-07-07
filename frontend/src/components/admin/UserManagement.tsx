import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Tabs,
  Tab,
  Grid,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Switch,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Security,
  Person,
  AdminPanelSettings,
  Engineering,
  Design,
  Visibility,
  Block,
  CheckCircle,
  Warning,
  Info,
} from '@mui/icons-material';
import { useAuthStore } from '../../stores/authStore';

interface User {
  user_id: string;
  username: string;
  email: string;
  full_name?: string;
  company?: string;
  department?: string;
  phone?: string;
  role: string;
  status: string;
  created_at: string;
  updated_at: string;
  last_login?: string;
  login_count: number;
  failed_login_attempts: number;
  two_factor_enabled: boolean;
}

interface UserCreateData {
  username: string;
  email: string;
  password: string;
  full_name?: string;
  company?: string;
  department?: string;
  phone?: string;
  role: string;
}

const UserManagement: React.FC = () => {
  const { user, hasPermission } = useAuthStore();
  const [users, setUsers] = useState<User[]>([]);
  const [selectedTab, setSelectedTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // 다이얼로그 상태
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  
  // 폼 데이터
  const [createFormData, setCreateFormData] = useState<UserCreateData>({
    username: '',
    email: '',
    password: '',
    full_name: '',
    company: '',
    department: '',
    phone: '',
    role: 'designer',
  });

  const [securityStats, setSecurityStats] = useState({
    total_users: 0,
    active_users: 0,
    suspended_users: 0,
    blocked_ips: 0,
    recent_login_attempts_24h: 0,
    failed_attempts_24h: 0,
    active_sessions: 0,
  });

  const roles = [
    { value: 'super_admin', label: '최고 관리자', icon: <AdminPanelSettings />, color: '#ef4444' },
    { value: 'admin', label: '관리자', icon: <Security />, color: '#f59e0b' },
    { value: 'architect', label: '건축사', icon: <Engineering />, color: '#3b82f6' },
    { value: 'engineer', label: '엔지니어', icon: <Engineering />, color: '#8b5cf6' },
    { value: 'designer', label: '설계자', icon: <Design />, color: '#10b981' },
    { value: 'client', label: '클라이언트', icon: <Person />, color: '#6b7280' },
    { value: 'viewer', label: '뷰어', icon: <Visibility />, color: '#9ca3af' },
  ];

  const statusColors = {
    active: 'success',
    inactive: 'default',
    suspended: 'warning',
    pending: 'info',
    deleted: 'error',
  } as const;

  // API 호출 함수
  const apiCall = async (endpoint: string, options: RequestInit = {}) => {
    const token = localStorage.getItem('access_token');
    const sessionId = localStorage.getItem('session_id');
    
    const response = await fetch(`/api/auth${endpoint}`, {
      ...options,
      headers: {
        'Authorization': token ? `Bearer ${token}` : '',
        'X-Session-ID': sessionId || '',
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Request failed');
    }

    return response;
  };

  // 사용자 목록 가져오기
  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await apiCall('/users');
      const data = await response.json();
      setUsers(data);
    } catch (error: any) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // 보안 통계 가져오기
  const fetchSecurityStats = async () => {
    try {
      const response = await apiCall('/security/stats');
      const data = await response.json();
      setSecurityStats(data.statistics);
    } catch (error: any) {
      console.error('보안 통계 조회 실패:', error);
    }
  };

  // 사용자 생성
  const handleCreateUser = async () => {
    try {
      const response = await apiCall('/users', {
        method: 'POST',
        body: JSON.stringify(createFormData),
      });

      if (response.ok) {
        setCreateDialogOpen(false);
        setCreateFormData({
          username: '',
          email: '',
          password: '',
          full_name: '',
          company: '',
          department: '',
          phone: '',
          role: 'designer',
        });
        fetchUsers();
      }
    } catch (error: any) {
      setError(error.message);
    }
  };

  // 사용자 수정
  const handleUpdateUser = async () => {
    if (!selectedUser) return;

    try {
      const updateData = {
        email: selectedUser.email,
        full_name: selectedUser.full_name,
        company: selectedUser.company,
        department: selectedUser.department,
        phone: selectedUser.phone,
        role: selectedUser.role,
        status: selectedUser.status,
      };

      const response = await apiCall(`/users/${selectedUser.username}`, {
        method: 'PUT',
        body: JSON.stringify(updateData),
      });

      if (response.ok) {
        setEditDialogOpen(false);
        setSelectedUser(null);
        fetchUsers();
      }
    } catch (error: any) {
      setError(error.message);
    }
  };

  // 사용자 삭제
  const handleDeleteUser = async (username: string) => {
    if (!confirm('정말로 이 사용자를 삭제하시겠습니까?')) return;

    try {
      const response = await apiCall(`/users/${username}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        fetchUsers();
      }
    } catch (error: any) {
      setError(error.message);
    }
  };

  useEffect(() => {
    if (hasPermission?.('user:read')) {
      fetchUsers();
      fetchSecurityStats();
    }
  }, []);

  // 권한 확인
  if (!hasPermission?.('user:read')) {
    return (
      <Alert severity="error">
        사용자 관리 권한이 없습니다.
      </Alert>
    );
  }

  const TabPanel: React.FC<{ children: React.ReactNode; value: number; index: number }> = ({
    children,
    value,
    index,
  }) => (
    <div role="tabpanel" hidden={value !== index}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );

  return (
    <Box sx={{ p: 3 }}>
      {/* 헤더 */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 800 }}>
          사용자 관리 👥
        </Typography>
        {hasPermission?.('user:create') && (
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setCreateDialogOpen(true)}
            sx={{ borderRadius: 2 }}
          >
            사용자 추가
          </Button>
        )}
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* 탭 */}
      <Paper sx={{ borderRadius: 3, mb: 3 }}>
        <Tabs
          value={selectedTab}
          onChange={(_, newValue) => setSelectedTab(newValue)}
          sx={{ px: 2 }}
        >
          <Tab label="사용자 목록" />
          <Tab label="보안 통계" />
          <Tab label="권한 관리" />
        </Tabs>

        <TabPanel value={selectedTab} index={0}>
          {/* 사용자 목록 */}
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>사용자명</TableCell>
                  <TableCell>이메일</TableCell>
                  <TableCell>이름</TableCell>
                  <TableCell>역할</TableCell>
                  <TableCell>상태</TableCell>
                  <TableCell>최근 로그인</TableCell>
                  <TableCell align="center">작업</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.user_id}>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {roles.find(r => r.value === user.role)?.icon}
                        {user.username}
                      </Box>
                    </TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>{user.full_name || '-'}</TableCell>
                    <TableCell>
                      <Chip
                        label={roles.find(r => r.value === user.role)?.label || user.role}
                        size="small"
                        sx={{
                          bgcolor: `${roles.find(r => r.value === user.role)?.color}15`,
                          color: roles.find(r => r.value === user.role)?.color,
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={user.status}
                        size="small"
                        color={statusColors[user.status as keyof typeof statusColors]}
                      />
                    </TableCell>
                    <TableCell>
                      {user.last_login ? new Date(user.last_login).toLocaleDateString('ko-KR') : '없음'}
                    </TableCell>
                    <TableCell align="center">
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        {hasPermission?.('user:update') && (
                          <IconButton
                            size="small"
                            onClick={() => {
                              setSelectedUser(user);
                              setEditDialogOpen(true);
                            }}
                          >
                            <Edit />
                          </IconButton>
                        )}
                        {hasPermission?.('user:delete') && (
                          <IconButton
                            size="small"
                            onClick={() => handleDeleteUser(user.username)}
                            color="error"
                          >
                            <Delete />
                          </IconButton>
                        )}
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        <TabPanel value={selectedTab} index={1}>
          {/* 보안 통계 */}
          <Grid container spacing={3} sx={{ p: 3 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ borderRadius: 2 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Person sx={{ color: '#3b82f6' }} />
                    <Typography variant="h6">전체 사용자</Typography>
                  </Box>
                  <Typography variant="h4">{securityStats.total_users}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ borderRadius: 2 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <CheckCircle sx={{ color: '#10b981' }} />
                    <Typography variant="h6">활성 사용자</Typography>
                  </Box>
                  <Typography variant="h4">{securityStats.active_users}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ borderRadius: 2 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Warning sx={{ color: '#f59e0b' }} />
                    <Typography variant="h6">차단된 IP</Typography>
                  </Box>
                  <Typography variant="h4">{securityStats.blocked_ips}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ borderRadius: 2 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Info sx={{ color: '#8b5cf6' }} />
                    <Typography variant="h6">활성 세션</Typography>
                  </Box>
                  <Typography variant="h4">{securityStats.active_sessions}</Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={selectedTab} index={2}>
          {/* 권한 관리 */}
          <Box sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              역할별 권한
            </Typography>
            <Grid container spacing={3}>
              {roles.map((role) => (
                <Grid item xs={12} md={6} key={role.value}>
                  <Card sx={{ borderRadius: 2 }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                        {role.icon}
                        <Typography variant="h6">{role.label}</Typography>
                      </Box>
                      <Typography variant="body2" color="textSecondary">
                        {role.value === 'super_admin' && '모든 시스템 권한'}
                        {role.value === 'admin' && '사용자 관리 및 시스템 모니터링'}
                        {role.value === 'architect' && '프로젝트 관리 및 AI 고급 분석'}
                        {role.value === 'engineer' && '설계 분석 및 파일 처리'}
                        {role.value === 'designer' && '기본 설계 도구 사용'}
                        {role.value === 'client' && '프로젝트 조회 및 기본 채팅'}
                        {role.value === 'viewer' && '읽기 전용 접근'}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        </TabPanel>
      </Paper>

      {/* 사용자 생성 다이얼로그 */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>새 사용자 추가</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="사용자명"
                value={createFormData.username}
                onChange={(e) => setCreateFormData(prev => ({ ...prev, username: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="이메일"
                type="email"
                value={createFormData.email}
                onChange={(e) => setCreateFormData(prev => ({ ...prev, email: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="비밀번호"
                type="password"
                value={createFormData.password}
                onChange={(e) => setCreateFormData(prev => ({ ...prev, password: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="이름"
                value={createFormData.full_name}
                onChange={(e) => setCreateFormData(prev => ({ ...prev, full_name: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>역할</InputLabel>
                <Select
                  value={createFormData.role}
                  onChange={(e) => setCreateFormData(prev => ({ ...prev, role: e.target.value }))}
                  label="역할"
                >
                  {roles.map((role) => (
                    <MenuItem key={role.value} value={role.value}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {role.icon}
                        {role.label}
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>취소</Button>
          <Button onClick={handleCreateUser} variant="contained">추가</Button>
        </DialogActions>
      </Dialog>

      {/* 사용자 수정 다이얼로그 */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>사용자 정보 수정</DialogTitle>
        <DialogContent>
          {selectedUser && (
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="이메일"
                  type="email"
                  value={selectedUser.email}
                  onChange={(e) => setSelectedUser(prev => prev ? { ...prev, email: e.target.value } : null)}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>역할</InputLabel>
                  <Select
                    value={selectedUser.role}
                    onChange={(e) => setSelectedUser(prev => prev ? { ...prev, role: e.target.value } : null)}
                    label="역할"
                  >
                    {roles.map((role) => (
                      <MenuItem key={role.value} value={role.value}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {role.icon}
                          {role.label}
                        </Box>
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>상태</InputLabel>
                  <Select
                    value={selectedUser.status}
                    onChange={(e) => setSelectedUser(prev => prev ? { ...prev, status: e.target.value } : null)}
                    label="상태"
                  >
                    <MenuItem value="active">활성</MenuItem>
                    <MenuItem value="inactive">비활성</MenuItem>
                    <MenuItem value="suspended">일시정지</MenuItem>
                    <MenuItem value="pending">대기</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>취소</Button>
          <Button onClick={handleUpdateUser} variant="contained">수정</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default UserManagement;