/**
 * 파라메트릭 BIM 페이지
 * 프로젝트와 연동된 파라메트릭 BIM 모델링 환경
 */
import React, { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Typography,
  Paper,
  Button,
  ButtonGroup,
  Breadcrumbs,
  Link,
  Alert,
  Snackbar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Card,
  CardContent,
  Chip,
  Divider,
  CircularProgress
} from '@mui/material';
import {
  ArrowBack,
  Save,
  Share,
  Download,
  Upload,
  Settings,
  History,
  BugReport,
  AutoAwesome,
  Tune,
  Architecture,
  Engineering,
  ModelTraining
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import ParametricBIMEditor from '../../components/bim/ParametricBIMEditor';
import { ParametricBIMData } from '../../services/parametricBimEngine';
import { useAuthStore } from '../../stores/authStore';

interface ProjectInfo {
  id: string;
  name: string;
  description?: string;
  type: string;
  status: string;
  members: Array<{
    id: string;
    name: string;
    role: string;
  }>;
}

interface BIMModelVersion {
  id: string;
  version: number;
  name: string;
  description: string;
  createdAt: string;
  createdBy: string;
  isActive: boolean;
  fileSize: number;
  objectCount: number;
  parameterCount: number;
}

const ParametricBIMPage: React.FC = () => {
  const { projectId, modelId } = useParams<{ projectId: string; modelId?: string }>();
  const navigate = useNavigate();
  const { user } = useAuthStore();

  // 상태 관리
  const [projectInfo, setProjectInfo] = useState<ProjectInfo | null>(null);
  const [currentModel, setCurrentModel] = useState<ParametricBIMData | null>(null);
  const [modelVersions, setModelVersions] = useState<BIMModelVersion[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  
  // 다이얼로그 상태
  const [saveDialogOpen, setSaveDialogOpen] = useState(false);
  const [shareDialogOpen, setShareDialogOpen] = useState(false);
  const [settingsDialogOpen, setSettingsDialogOpen] = useState(false);
  const [versionDialogOpen, setVersionDialogOpen] = useState(false);
  
  // 저장 폼 상태
  const [saveFormData, setSaveFormData] = useState({
    name: '',
    description: '',
    isNewVersion: true
  });

  // 프로젝트 및 모델 정보 로드
  useEffect(() => {
    loadProjectData();
  }, [projectId, modelId]);

  const loadProjectData = async () => {
    try {
      setIsLoading(true);

      // 프로젝트 정보 로드
      const projectResponse = await fetch(`/api/projects/${projectId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (projectResponse.ok) {
        const project = await projectResponse.json();
        setProjectInfo({
          id: project.data.id,
          name: project.data.name,
          description: project.data.description,
          type: project.data.type || 'residential',
          status: project.data.status || 'active',
          members: project.data.members || []
        });
      }

      // BIM 모델 버전 목록 로드
      const versionsResponse = await fetch(`/api/projects/${projectId}/bim-models`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (versionsResponse.ok) {
        const versions = await versionsResponse.json();
        setModelVersions(versions.data || []);
      }

      // 특정 모델 로드 (modelId가 있는 경우)
      if (modelId) {
        const modelResponse = await fetch(`/api/projects/${projectId}/bim-models/${modelId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });

        if (modelResponse.ok) {
          const modelData = await modelResponse.json();
          setCurrentModel(modelData.data);
        }
      } else {
        // 새 모델 생성
        createNewModel();
      }

    } catch (error) {
      console.error('프로젝트 데이터 로드 오류:', error);
      setErrorMessage('프로젝트 데이터를 불러오는데 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  // 새 모델 생성
  const createNewModel = () => {
    const newModel: ParametricBIMData = {
      id: `model_${Date.now()}`,
      name: `${projectInfo?.name || '새 프로젝트'} - 파라메트릭 모델`,
      description: '파라메트릭 BIM 모델',
      version: 1,
      objects: [],
      globalParameters: [],
      relationships: [],
      metadata: {
        projectId: projectId || '',
        createdAt: new Date().toISOString(),
        createdBy: user?.id || '',
        buildingType: projectInfo?.type || 'residential'
      }
    };
    setCurrentModel(newModel);
  };

  // 모델 변경 핸들러
  const handleModelChange = (updatedModel: ParametricBIMData) => {
    setCurrentModel(updatedModel);
  };

  // 저장 핸들러
  const handleSave = async () => {
    if (!currentModel || !projectInfo) return;

    try {
      setIsSaving(true);

      const saveData = {
        ...currentModel,
        name: saveFormData.name || currentModel.name,
        description: saveFormData.description || currentModel.description,
        version: saveFormData.isNewVersion ? (currentModel.version + 1) : currentModel.version,
        metadata: {
          ...currentModel.metadata,
          updatedAt: new Date().toISOString(),
          updatedBy: user?.id
        }
      };

      const response = await fetch(
        saveFormData.isNewVersion 
          ? `/api/projects/${projectId}/bim-models`
          : `/api/projects/${projectId}/bim-models/${currentModel.id}`,
        {
          method: saveFormData.isNewVersion ? 'POST' : 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          },
          body: JSON.stringify(saveData)
        }
      );

      if (response.ok) {
        const result = await response.json();
        setCurrentModel(result.data);
        setSaveMessage('모델이 성공적으로 저장되었습니다.');
        setSaveDialogOpen(false);
        
        // 버전 목록 다시 로드
        loadProjectData();
      } else {
        throw new Error('저장 실패');
      }

    } catch (error) {
      console.error('저장 오류:', error);
      setErrorMessage('모델 저장 중 오류가 발생했습니다.');
    } finally {
      setIsSaving(false);
    }
  };

  // 공유 핸들러
  const handleShare = async () => {
    if (!currentModel) return;

    try {
      const shareData = {
        modelId: currentModel.id,
        projectId: projectId,
        permissions: ['view', 'comment'], // 기본 권한
        expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString() // 7일 후 만료
      };

      const response = await fetch(`/api/projects/${projectId}/bim-models/${currentModel.id}/share`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(shareData)
      });

      if (response.ok) {
        const result = await response.json();
        navigator.clipboard.writeText(result.data.shareUrl);
        setSaveMessage('공유 링크가 클립보드에 복사되었습니다.');
        setShareDialogOpen(false);
      }

    } catch (error) {
      console.error('공유 오류:', error);
      setErrorMessage('모델 공유 중 오류가 발생했습니다.');
    }
  };

  // 내보내기 핸들러
  const handleExport = () => {
    if (!currentModel) return;

    const dataStr = JSON.stringify(currentModel, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `${currentModel.name}_v${currentModel.version}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
    setSaveMessage('모델이 성공적으로 내보내졌습니다.');
  };

  // AI 최적화 실행
  const handleAIOptimization = async () => {
    if (!currentModel) return;

    try {
      const response = await fetch(`/api/ai/optimize-bim`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          model: currentModel,
          optimization_type: 'performance',
          constraints: ['budget', 'building_code', 'energy_efficiency']
        })
      });

      if (response.ok) {
        const result = await response.json();
        setCurrentModel(result.data.optimized_model);
        setSaveMessage('AI 최적화가 완료되었습니다.');
      }

    } catch (error) {
      console.error('AI 최적화 오류:', error);
      setErrorMessage('AI 최적화 중 오류가 발생했습니다.');
    }
  };

  if (isLoading) {
    return (
      <Container maxWidth="xl" sx={{ py: 4, textAlign: 'center' }}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ mt: 2 }}>
          프로젝트 데이터를 불러오는 중...
        </Typography>
      </Container>
    );
  }

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* 헤더 */}
      <Paper sx={{ p: 2, borderRadius: 0, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          {/* 브레드크럼 */}
          <Breadcrumbs>
            <Link
              color="inherit"
              href="#"
              onClick={() => navigate('/projects')}
              sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
            >
              <ArrowBack fontSize="small" />
              프로젝트
            </Link>
            <Typography color="text.primary">
              {projectInfo?.name || '프로젝트'}
            </Typography>
            <Typography color="text.primary" sx={{ fontWeight: 700 }}>
              파라메트릭 BIM
            </Typography>
          </Breadcrumbs>

          {/* 액션 버튼들 */}
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant="outlined"
              startIcon={<AutoAwesome />}
              onClick={handleAIOptimization}
              disabled={!currentModel}
            >
              AI 최적화
            </Button>
            <ButtonGroup variant="contained">
              <Button
                startIcon={<Save />}
                onClick={() => setSaveDialogOpen(true)}
                disabled={!currentModel || isSaving}
              >
                저장
              </Button>
              <Button
                startIcon={<Share />}
                onClick={() => setShareDialogOpen(true)}
                disabled={!currentModel}
              >
                공유
              </Button>
              <Button
                startIcon={<Download />}
                onClick={handleExport}
                disabled={!currentModel}
              >
                내보내기
              </Button>
            </ButtonGroup>
            <Button
              variant="outlined"
              startIcon={<History />}
              onClick={() => setVersionDialogOpen(true)}
            >
              버전 관리
            </Button>
            <Button
              variant="outlined"
              startIcon={<Settings />}
              onClick={() => setSettingsDialogOpen(true)}
            >
              설정
            </Button>
          </Box>
        </Box>

        {/* 프로젝트 정보 */}
        {projectInfo && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Chip 
              icon={<Architecture />} 
              label={projectInfo.type} 
              size="small" 
            />
            <Chip 
              label={projectInfo.status} 
              size="small" 
              color={projectInfo.status === 'active' ? 'success' : 'default'}
            />
            <Typography variant="body2" color="text.secondary">
              {projectInfo.members.length}명의 멤버
            </Typography>
            {currentModel && (
              <>
                <Divider orientation="vertical" flexItem />
                <Typography variant="body2" color="text.secondary">
                  모델 v{currentModel.version} • {currentModel.objects.length}개 객체
                </Typography>
              </>
            )}
          </Box>
        )}
      </Paper>

      {/* 파라메트릭 BIM 에디터 */}
      <Box sx={{ flexGrow: 1 }}>
        {currentModel ? (
          <ParametricBIMEditor
            initialModel={currentModel}
            onModelChange={handleModelChange}
            readOnly={false}
          />
        ) : (
          <Container maxWidth="md" sx={{ py: 8, textAlign: 'center' }}>
            <Architecture sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h4" gutterBottom>
              파라메트릭 BIM 모델 생성
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
              프로젝트를 위한 새로운 파라메트릭 BIM 모델을 생성하세요.
            </Typography>
            <Button
              variant="contained"
              size="large"
              startIcon={<ModelTraining />}
              onClick={createNewModel}
            >
              새 모델 생성
            </Button>
          </Container>
        )}
      </Box>

      {/* 저장 다이얼로그 */}
      <Dialog open={saveDialogOpen} onClose={() => setSaveDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>모델 저장</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            margin="normal"
            label="모델 이름"
            value={saveFormData.name}
            onChange={(e) => setSaveFormData({ ...saveFormData, name: e.target.value })}
            placeholder={currentModel?.name}
          />
          <TextField
            fullWidth
            margin="normal"
            label="설명"
            multiline
            rows={3}
            value={saveFormData.description}
            onChange={(e) => setSaveFormData({ ...saveFormData, description: e.target.value })}
            placeholder={currentModel?.description}
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>저장 옵션</InputLabel>
            <Select
              value={saveFormData.isNewVersion ? 'new' : 'update'}
              onChange={(e) => setSaveFormData({ ...saveFormData, isNewVersion: e.target.value === 'new' })}
            >
              <MenuItem value="new">새 버전으로 저장</MenuItem>
              <MenuItem value="update">현재 버전 업데이트</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSaveDialogOpen(false)}>취소</Button>
          <Button 
            onClick={handleSave} 
            variant="contained"
            disabled={isSaving}
            startIcon={isSaving ? <CircularProgress size={16} /> : <Save />}
          >
            {isSaving ? '저장 중...' : '저장'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* 공유 다이얼로그 */}
      <Dialog open={shareDialogOpen} onClose={() => setShareDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>모델 공유</DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            공유 링크를 생성하면 7일간 유효한 링크가 생성됩니다.
          </Alert>
          <Typography variant="body2" color="text.secondary">
            이 모델을 다른 사용자와 공유할 수 있습니다. 공유받은 사용자는 모델을 보고 댓글을 남길 수 있습니다.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShareDialogOpen(false)}>취소</Button>
          <Button onClick={handleShare} variant="contained" startIcon={<Share />}>
            공유 링크 생성
          </Button>
        </DialogActions>
      </Dialog>

      {/* 버전 관리 다이얼로그 */}
      <Dialog open={versionDialogOpen} onClose={() => setVersionDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>버전 관리</DialogTitle>
        <DialogContent>
          <Grid container spacing={2}>
            {modelVersions.map((version) => (
              <Grid item xs={12} key={version.id}>
                <Card variant={version.isActive ? "elevation" : "outlined"}>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <Box>
                        <Typography variant="h6" gutterBottom>
                          {version.name} v{version.version}
                          {version.isActive && <Chip label="현재" size="small" sx={{ ml: 1 }} />}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          {version.description}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {new Date(version.createdAt).toLocaleString()} • {version.createdBy}
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Chip label={`${version.objectCount}개 객체`} size="small" />
                        <Chip label={`${Math.round(version.fileSize / 1024)}KB`} size="small" />
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setVersionDialogOpen(false)}>닫기</Button>
        </DialogActions>
      </Dialog>

      {/* 알림 스낵바 */}
      <Snackbar
        open={!!saveMessage}
        autoHideDuration={4000}
        onClose={() => setSaveMessage(null)}
        message={saveMessage}
      />

      <Snackbar
        open={!!errorMessage}
        autoHideDuration={6000}
        onClose={() => setErrorMessage(null)}
      >
        <Alert severity="error" onClose={() => setErrorMessage(null)}>
          {errorMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default ParametricBIMPage;