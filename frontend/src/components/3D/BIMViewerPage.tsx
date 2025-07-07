import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab,
  Chip,
  Divider,
  Alert,
  CircularProgress
} from '@mui/material';
import {
  Architecture,
  ThreeDRotation,
  Settings,
  Download,
  Share,
  Edit,
  Visibility
} from '@mui/icons-material';
import BIMViewer from './BIMViewer';

interface Room {
  type: string;
  count: number;
  area: number;
  orientation?: string;
}

interface BIMData {
  id?: string;
  name?: string;
  description?: string;
  buildingType: string;
  totalArea: { value: number; unit: string };
  rooms: Room[];
  style?: {
    architectural: string;
    interior: string;
    keywords: string[];
  };
  location?: {
    address: string;
    region: string;
    climate: string;
  };
  naturalLanguageInput?: string;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const BIMViewerPage: React.FC = () => {
  const [selectedTab, setSelectedTab] = useState(0);
  const [bimData, setBimData] = useState<BIMData | null>(null);
  const [bimProjects, setBimProjects] = useState<BIMData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [openNLPDialog, setOpenNLPDialog] = useState(false);
  const [nlpInput, setNlpInput] = useState('');

  // 샘플 BIM 데이터
  const sampleBIMData: BIMData = {
    id: 'sample-1',
    name: '샘플 아파트',
    description: '3룸 아파트 샘플 모델',
    buildingType: 'RESIDENTIAL',
    totalArea: { value: 30, unit: '평' },
    rooms: [
      { type: '거실', count: 1, area: 12, orientation: '남향' },
      { type: '침실', count: 2, area: 8 },
      { type: '주방', count: 1, area: 6 },
      { type: '화장실', count: 1, area: 4 }
    ],
    style: {
      architectural: '현대적',
      interior: '모던',
      keywords: ['깔끔한', '실용적', '밝은']
    },
    location: {
      address: '서울시 강남구',
      region: '강남',
      climate: '온대'
    }
  };

  const sampleProjects: BIMData[] = [
    sampleBIMData,
    {
      id: 'sample-2',
      name: '모던 오피스',
      description: '소규모 사무공간',
      buildingType: 'OFFICE',
      totalArea: { value: 50, unit: '평' },
      rooms: [
        { type: '사무실', count: 3, area: 15 },
        { type: '회의실', count: 1, area: 10 },
        { type: '휴게실', count: 1, area: 8 },
        { type: '화장실', count: 1, area: 4 }
      ],
      style: {
        architectural: '모던',
        interior: '미니멀',
        keywords: ['효율적', '개방적']
      }
    },
    {
      id: 'sample-3',
      name: '카페 매장',
      description: '소규모 카페 인테리어',
      buildingType: 'COMMERCIAL',
      totalArea: { value: 25, unit: '평' },
      rooms: [
        { type: '홀', count: 1, area: 15 },
        { type: '주방', count: 1, area: 6 },
        { type: '화장실', count: 1, area: 3 }
      ],
      style: {
        architectural: '인더스트리얼',
        interior: '빈티지',
        keywords: ['아늑한', '따뜻한']
      }
    }
  ];

  useEffect(() => {
    // 로컬 스토리지에서 프로젝트 데이터 확인
    const storedProject = localStorage.getItem('currentBIMProject');
    
    if (storedProject) {
      try {
        const { project, bimData: projectBimData, timestamp } = JSON.parse(storedProject);
        
        // 1시간 이내의 데이터만 사용 (캐시 만료)
        const isRecent = new Date().getTime() - new Date(timestamp).getTime() < 3600000;
        
        if (isRecent && projectBimData) {
          setBimData(projectBimData);
          setBimProjects(prev => [projectBimData, ...prev.filter(p => p.id !== projectBimData.id)]);
          
          console.log('프로젝트 페이지에서 생성된 BIM 데이터 로드:', {
            projectName: project.name,
            rooms: projectBimData.rooms.length,
            buildingType: projectBimData.buildingType
          });
          
          // 사용된 데이터는 제거 (한 번만 사용)
          localStorage.removeItem('currentBIMProject');
          
          return;
        }
      } catch (error) {
        console.error('저장된 프로젝트 데이터 파싱 오류:', error);
      }
    }
    
    // 기본 샘플 데이터 사용
    setBimProjects(sampleProjects);
    setBimData(sampleBIMData);
  }, []);

  // BIM 프로젝트 로드
  const loadBIMProject = async (projectId: string) => {
    setLoading(true);
    try {
      // 실제로는 API 호출
      const project = sampleProjects.find(p => p.id === projectId);
      if (project) {
        setBimData(project);
      }
      setLoading(false);
    } catch (err) {
      setError('프로젝트를 로드할 수 없습니다.');
      setLoading(false);
    }
  };

  // 자연어 입력으로 BIM 생성
  const handleNLPGenerate = async () => {
    if (!nlpInput.trim()) return;

    setLoading(true);
    setOpenNLPDialog(false);

    try {
      // 실제로는 NLP API 호출
      const response = await fetch('/api/nlp/enhance', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          naturalLanguageInput: nlpInput,
          language: 'ko',
          includeValidation: true
        })
      });

      if (response.ok) {
        const result = await response.json();
        const bimParams = result.data.bimParameters;

        // BIM 데이터 형식으로 변환
        const newBIMData: BIMData = {
          id: `nlp-${Date.now()}`,
          name: bimParams.suggestedName,
          description: bimParams.description,
          buildingType: bimParams.buildingType,
          totalArea: bimParams.totalArea,
          rooms: bimParams.rooms,
          style: bimParams.style,
          location: bimParams.location,
          naturalLanguageInput: nlpInput
        };

        setBimData(newBIMData);
        setNlpInput('');
      } else {
        throw new Error('NLP 처리 실패');
      }
    } catch (err) {
      console.error('NLP 생성 오류:', err);
      // 폴백: 샘플 데이터 사용
      setBimData({
        ...sampleBIMData,
        name: '자연어 생성 모델',
        description: nlpInput.substring(0, 100),
        naturalLanguageInput: nlpInput
      });
    }

    setLoading(false);
  };

  // 탭 변경 핸들러
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setSelectedTab(newValue);
  };

  // 건물 유형별 색상
  const getBuildingTypeColor = (type: string) => {
    const colors = {
      RESIDENTIAL: '#4caf50',
      COMMERCIAL: '#2196f3', 
      OFFICE: '#ff9800',
      INDUSTRIAL: '#9e9e9e',
      PUBLIC: '#e91e63'
    };
    return colors[type as keyof typeof colors] || '#9e9e9e';
  };

  const getBuildingTypeName = (type: string) => {
    const names = {
      RESIDENTIAL: '주거',
      COMMERCIAL: '상업',
      OFFICE: '사무',
      INDUSTRIAL: '산업',
      PUBLIC: '공공'
    };
    return names[type as keyof typeof names] || type;
  };

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      {/* 헤더 */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            <ThreeDRotation sx={{ mr: 1, verticalAlign: 'middle' }} />
            3D BIM 뷰어
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            자연어로 생성한 BIM 모델을 3D로 시각화하고 탐색하세요
          </Typography>
        </Box>
        
        <Box display="flex" gap={2}>
          <Button
            variant="contained"
            startIcon={<Architecture />}
            onClick={() => setOpenNLPDialog(true)}
            disabled={loading}
          >
            자연어로 생성
          </Button>
          
          <Button
            variant="outlined"
            startIcon={<Download />}
            disabled={!bimData}
          >
            모델 다운로드
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* 왼쪽: 3D 뷰어 */}
        <Grid item xs={12} lg={8}>
          <Paper elevation={3}>
            <Box p={2}>
              <Typography variant="h6" gutterBottom>
                3D 모델 뷰어
                {bimData && (
                  <Chip
                    label={getBuildingTypeName(bimData.buildingType)}
                    size="small"
                    sx={{ 
                      ml: 2,
                      bgcolor: getBuildingTypeColor(bimData.buildingType),
                      color: 'white'
                    }}
                  />
                )}
              </Typography>
              
              {loading ? (
                <Box display="flex" justifyContent="center" alignItems="center" height={600}>
                  <CircularProgress />
                </Box>
              ) : (
                <BIMViewer
                  bimData={bimData || undefined}
                  height={600}
                  enableControls={true}
                  showGrid={true}
                  onSceneReady={(scene) => {
                    console.log('3D 씬 준비 완료:', scene);
                  }}
                  onModelLoad={(meshes) => {
                    console.log('모델 로드 완료:', meshes.length, '개 메쉬');
                  }}
                />
              )}
            </Box>
          </Paper>
        </Grid>

        {/* 오른쪽: 정보 패널 */}
        <Grid item xs={12} lg={4}>
          <Paper elevation={3}>
            <Tabs value={selectedTab} onChange={handleTabChange}>
              <Tab label="모델 정보" />
              <Tab label="프로젝트" />
              <Tab label="설정" />
            </Tabs>

            <TabPanel value={selectedTab} index={0}>
              {bimData ? (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    {bimData.name}
                  </Typography>
                  
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {bimData.description}
                  </Typography>

                  <Divider sx={{ my: 2 }} />

                  <Typography variant="subtitle2" gutterBottom>
                    기본 정보
                  </Typography>
                  
                  <Box display="flex" justifyContent="space-between" mb={1}>
                    <Typography variant="body2">건물 유형:</Typography>
                    <Typography variant="body2">
                      {getBuildingTypeName(bimData.buildingType)}
                    </Typography>
                  </Box>
                  
                  <Box display="flex" justifyContent="space-between" mb={1}>
                    <Typography variant="body2">총 면적:</Typography>
                    <Typography variant="body2">
                      {bimData.totalArea.value}{bimData.totalArea.unit}
                    </Typography>
                  </Box>
                  
                  <Box display="flex" justifyContent="space-between" mb={2}>
                    <Typography variant="body2">방 개수:</Typography>
                    <Typography variant="body2">
                      {bimData.rooms.length}개
                    </Typography>
                  </Box>

                  <Divider sx={{ my: 2 }} />

                  <Typography variant="subtitle2" gutterBottom>
                    공간 구성
                  </Typography>
                  
                  {bimData.rooms.map((room, index) => (
                    <Box key={index} display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="body2">
                        {room.type} {room.count > 1 && `×${room.count}`}:
                      </Typography>
                      <Typography variant="body2">
                        {room.area}㎡
                        {room.orientation && ` (${room.orientation})`}
                      </Typography>
                    </Box>
                  ))}

                  {bimData.style && (
                    <>
                      <Divider sx={{ my: 2 }} />
                      <Typography variant="subtitle2" gutterBottom>
                        스타일
                      </Typography>
                      <Typography variant="body2">
                        {bimData.style.architectural} / {bimData.style.interior}
                      </Typography>
                      <Box mt={1}>
                        {bimData.style.keywords.map((keyword, index) => (
                          <Chip
                            key={index}
                            label={keyword}
                            size="small"
                            variant="outlined"
                            sx={{ mr: 0.5, mb: 0.5 }}
                          />
                        ))}
                      </Box>
                    </>
                  )}

                  {bimData.naturalLanguageInput && (
                    <>
                      <Divider sx={{ my: 2 }} />
                      <Typography variant="subtitle2" gutterBottom>
                        원본 입력
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        "{bimData.naturalLanguageInput}"
                      </Typography>
                    </>
                  )}
                </Box>
              ) : (
                <Typography color="text.secondary">
                  표시할 BIM 데이터가 없습니다.
                </Typography>
              )}
            </TabPanel>

            <TabPanel value={selectedTab} index={1}>
              <Typography variant="h6" gutterBottom>
                프로젝트 목록
              </Typography>
              
              {bimProjects.map((project) => (
                <Card 
                  key={project.id} 
                  sx={{ 
                    mb: 2, 
                    cursor: 'pointer',
                    border: bimData?.id === project.id ? 2 : 1,
                    borderColor: bimData?.id === project.id ? 'primary.main' : 'divider'
                  }}
                  onClick={() => loadBIMProject(project.id!)}
                >
                  <CardContent sx={{ p: 2 }}>
                    <Box display="flex" justifyContent="space-between" alignItems="start">
                      <Box>
                        <Typography variant="subtitle2">
                          {project.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {project.totalArea.value}{project.totalArea.unit} · {project.rooms.length}개 공간
                        </Typography>
                      </Box>
                      <Chip
                        label={getBuildingTypeName(project.buildingType)}
                        size="small"
                        sx={{ 
                          bgcolor: getBuildingTypeColor(project.buildingType),
                          color: 'white'
                        }}
                      />
                    </Box>
                  </CardContent>
                </Card>
              ))}
            </TabPanel>

            <TabPanel value={selectedTab} index={2}>
              <Typography variant="h6" gutterBottom>
                뷰어 설정
              </Typography>
              
              <Typography variant="body2" color="text.secondary">
                3D 뷰어 설정 옵션이 여기에 표시됩니다.
              </Typography>
              
              {/* 추후 설정 옵션 추가 */}
            </TabPanel>
          </Paper>
        </Grid>
      </Grid>

      {/* 자연어 입력 대화상자 */}
      <Dialog open={openNLPDialog} onClose={() => setOpenNLPDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          자연어로 BIM 모델 생성
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" paragraph>
            건물에 대한 설명을 자연어로 입력하면 AI가 3D BIM 모델을 생성합니다.
          </Typography>
          
          <TextField
            fullWidth
            multiline
            rows={4}
            label="건물 설명"
            placeholder="예: 서울 강남구에 30평 아파트를 설계해주세요. 침실 2개, 거실, 주방, 화장실이 필요하고 남향으로 배치해주세요."
            value={nlpInput}
            onChange={(e) => setNlpInput(e.target.value)}
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenNLPDialog(false)}>
            취소
          </Button>
          <Button
            onClick={handleNLPGenerate}
            variant="contained"
            disabled={!nlpInput.trim() || loading}
          >
            3D 모델 생성
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default BIMViewerPage;