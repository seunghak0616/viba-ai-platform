import React, { useState } from 'react';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
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
  Fab,
} from '@mui/material';
import {
  Add,
  MoreVert,
  Architecture,
  LocationOn,
  CalendarToday,
  Edit,
  Delete,
  Visibility,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const Projects: React.FC = () => {
  const navigate = useNavigate();
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newProject, setNewProject] = useState({
    name: '',
    description: '',
    building_type: 'residential',
    location: '',
    area: '',
    floors: '',
    budget: '',
  });

  // Mock 프로젝트 데이터
  const projects = [
    {
      id: '1',
      name: '친환경 주택 설계',
      description: '30평 규모의 친환경 주택 프로젝트입니다. 태양광 패널과 우수 재활용 시스템을 포함합니다.',
      building_type: '주거용',
      location: '서울시 강남구',
      area: 100,
      floors: 2,
      budget: 500000000,
      status: '진행중',
      progress: 75,
      created_at: '2025-01-01',
      updated_at: '2025-01-06',
    },
    {
      id: '2',
      name: '상업용 빌딩 구조 설계',
      description: '20층 규모의 오피스 빌딩 구조 설계 프로젝트입니다.',
      building_type: '상업용',
      location: '서울시 중구',
      area: 5000,
      floors: 20,
      budget: 15000000000,
      status: '설계중',
      progress: 45,
      created_at: '2024-12-15',
      updated_at: '2025-01-05',
    },
    {
      id: '3',
      name: '카페 인테리어 디자인',
      description: '자연 친화적 분위기의 카페 인테리어 설계입니다.',
      building_type: '상업용',
      location: '경기도 성남시',
      area: 80,
      floors: 1,
      budget: 100000000,
      status: '완료',
      progress: 100,
      created_at: '2024-11-20',
      updated_at: '2024-12-30',
    },
    {
      id: '4',
      name: '아파트 단지 계획',
      description: '500세대 규모의 친환경 아파트 단지 설계입니다.',
      building_type: '주거용',
      location: '인천시 연수구',
      area: 50000,
      floors: 15,
      budget: 50000000000,
      status: '기획중',
      progress: 20,
      created_at: '2025-01-03',
      updated_at: '2025-01-06',
    },
  ];

  const buildingTypes = [
    { value: 'residential', label: '주거용' },
    { value: 'commercial', label: '상업용' },
    { value: 'industrial', label: '공업용' },
    { value: 'mixed', label: '복합용도' },
    { value: 'public', label: '공공시설' },
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
      case '기획중':
        return 'secondary';
      default:
        return 'default';
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const formatArea = (area: number) => {
    return `${area.toLocaleString()}㎡`;
  };

  const handleCreateProject = () => {
    // TODO: API 호출로 프로젝트 생성
    console.log('새 프로젝트 생성:', newProject);
    setCreateDialogOpen(false);
    setNewProject({
      name: '',
      description: '',
      building_type: 'residential',
      location: '',
      area: '',
      floors: '',
      budget: '',
    });
  };

  return (
    <Container maxWidth="xl">
      {/* 헤더 */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 800, mb: 1 }}>
            프로젝트 관리
          </Typography>
          <Typography variant="h6" color="textSecondary">
            진행 중인 건축 프로젝트들을 관리하세요
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setCreateDialogOpen(true)}
          sx={{
            borderRadius: 2,
            fontWeight: 600,
            px: 3,
            py: 1.5,
          }}
        >
          새 프로젝트
        </Button>
      </Box>

      {/* 프로젝트 그리드 */}
      <Grid container spacing={3}>
        {projects.map((project) => (
          <Grid item xs={12} sm={6} lg={4} key={project.id}>
            <Card
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                border: 'none',
                borderRadius: 3,
                boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
                '&:hover': {
                  boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
                  transform: 'translateY(-4px)',
                },
                transition: 'all 0.3s ease',
                cursor: 'pointer',
              }}
              onClick={() => navigate(`/projects/${project.id}`)}
            >
              <CardContent sx={{ p: 3, flexGrow: 1 }}>
                {/* 헤더 */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="h6" sx={{ fontWeight: 700, mb: 1 }}>
                      {project.name}
                    </Typography>
                    <Chip
                      label={project.status}
                      size="small"
                      color={getStatusColor(project.status) as any}
                      sx={{ fontWeight: 500 }}
                    />
                  </Box>
                  <IconButton 
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation();
                      // TODO: 메뉴 열기
                    }}
                  >
                    <MoreVert />
                  </IconButton>
                </Box>

                {/* 설명 */}
                <Typography 
                  variant="body2" 
                  color="textSecondary" 
                  sx={{ 
                    mb: 3,
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden',
                  }}
                >
                  {project.description}
                </Typography>

                {/* 프로젝트 정보 */}
                <Box sx={{ mb: 3 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Architecture sx={{ fontSize: 16, mr: 1, color: '#64748b' }} />
                    <Typography variant="caption" color="textSecondary">
                      {project.building_type} • {project.floors}층 • {formatArea(project.area)}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <LocationOn sx={{ fontSize: 16, mr: 1, color: '#64748b' }} />
                    <Typography variant="caption" color="textSecondary">
                      {project.location}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <CalendarToday sx={{ fontSize: 16, mr: 1, color: '#64748b' }} />
                    <Typography variant="caption" color="textSecondary">
                      {new Date(project.updated_at).toLocaleDateString('ko-KR')} 업데이트
                    </Typography>
                  </Box>
                </Box>

                {/* 예산 */}
                <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2 }}>
                  예산: {formatCurrency(project.budget)}
                </Typography>

                {/* 진행률 바 */}
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="caption" color="textSecondary">
                      진행률
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      {project.progress}%
                    </Typography>
                  </Box>
                  <Box
                    sx={{
                      width: '100%',
                      height: 6,
                      backgroundColor: '#e2e8f0',
                      borderRadius: 3,
                      overflow: 'hidden',
                    }}
                  >
                    <Box
                      sx={{
                        width: `${project.progress}%`,
                        height: '100%',
                        background: `linear-gradient(90deg, ${
                          project.progress === 100 ? '#10b981' : '#2563eb'
                        } 0%, ${
                          project.progress === 100 ? '#34d399' : '#3b82f6'
                        } 100%)`,
                        transition: 'width 0.3s ease',
                      }}
                    />
                  </Box>
                </Box>
              </CardContent>

              {/* 액션 버튼들 */}
              <Box sx={{ p: 2, pt: 0, display: 'flex', gap: 1 }}>
                <Button
                  size="small"
                  startIcon={<Visibility />}
                  onClick={(e) => {
                    e.stopPropagation();
                    navigate(`/projects/${project.id}`);
                  }}
                  sx={{ flex: 1, fontWeight: 500 }}
                >
                  보기
                </Button>
                <Button
                  size="small"
                  startIcon={<Edit />}
                  onClick={(e) => {
                    e.stopPropagation();
                    // TODO: 편집 모달 열기
                  }}
                  sx={{ flex: 1, fontWeight: 500 }}
                >
                  편집
                </Button>
              </Box>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* 플로팅 액션 버튼 (모바일용) */}
      <Fab
        color="primary"
        aria-label="add"
        onClick={() => setCreateDialogOpen(true)}
        sx={{
          position: 'fixed',
          bottom: 24,
          right: 24,
          display: { xs: 'flex', sm: 'none' },
        }}
      >
        <Add />
      </Fab>

      {/* 프로젝트 생성 다이얼로그 */}
      <Dialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: { borderRadius: 3 },
        }}
      >
        <DialogTitle sx={{ pb: 2 }}>
          <Typography variant="h6" sx={{ fontWeight: 700 }}>
            새 프로젝트 생성
          </Typography>
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="프로젝트 명"
            value={newProject.name}
            onChange={(e) => setNewProject(prev => ({ ...prev, name: e.target.value }))}
            margin="normal"
            sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
          />
          <TextField
            fullWidth
            label="프로젝트 설명"
            value={newProject.description}
            onChange={(e) => setNewProject(prev => ({ ...prev, description: e.target.value }))}
            margin="normal"
            multiline
            rows={3}
            sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>건물 유형</InputLabel>
            <Select
              value={newProject.building_type}
              onChange={(e) => setNewProject(prev => ({ ...prev, building_type: e.target.value }))}
              label="건물 유형"
              sx={{ borderRadius: 2 }}
            >
              {buildingTypes.map((type) => (
                <MenuItem key={type.value} value={type.value}>
                  {type.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            fullWidth
            label="위치"
            value={newProject.location}
            onChange={(e) => setNewProject(prev => ({ ...prev, location: e.target.value }))}
            margin="normal"
            sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
          />
          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              label="면적 (㎡)"
              type="number"
              value={newProject.area}
              onChange={(e) => setNewProject(prev => ({ ...prev, area: e.target.value }))}
              margin="normal"
              sx={{ 
                flex: 1,
                '& .MuiOutlinedInput-root': { borderRadius: 2 } 
              }}
            />
            <TextField
              label="층수"
              type="number"
              value={newProject.floors}
              onChange={(e) => setNewProject(prev => ({ ...prev, floors: e.target.value }))}
              margin="normal"
              sx={{ 
                flex: 1,
                '& .MuiOutlinedInput-root': { borderRadius: 2 } 
              }}
            />
          </Box>
          <TextField
            fullWidth
            label="예산 (원)"
            type="number"
            value={newProject.budget}
            onChange={(e) => setNewProject(prev => ({ ...prev, budget: e.target.value }))}
            margin="normal"
            sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
          />
        </DialogContent>
        <DialogActions sx={{ p: 3, pt: 1 }}>
          <Button
            onClick={() => setCreateDialogOpen(false)}
            sx={{ borderRadius: 2, fontWeight: 600 }}
          >
            취소
          </Button>
          <Button
            onClick={handleCreateProject}
            variant="contained"
            sx={{ borderRadius: 2, fontWeight: 600 }}
          >
            생성
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Projects;