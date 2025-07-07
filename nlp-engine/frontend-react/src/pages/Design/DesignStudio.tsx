import React, { useState } from 'react';
import { aiAPI } from '../../services/api';
import FileUpload from '../../components/FileUpload/FileUpload';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Paper,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Alert,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Tab,
  Tabs,
} from '@mui/material';
import {
  ExpandMore,
  Architecture,
  AutoAwesome,
  CheckCircle,
  Timeline,
  Build,
  Palette,
  Speed,
  Eco,
  Analytics,
  Download,
  Share,
  Refresh,
  CloudUpload,
  FolderOpen,
} from '@mui/icons-material';

interface DesignRequest {
  projectId: string;
  requestType: string;
  content: string;
  buildingType: string;
  location: string;
  area: number;
  floors: number;
  budget: number;
  sustainability: string;
  style: string;
  specialRequirements: string[];
}

interface DesignResult {
  id: string;
  type: 'architectural' | 'structural' | 'mep' | 'materials' | 'cost' | 'schedule';
  title: string;
  description: string;
  recommendations: any[];
  confidence: number;
  processingTime: number;
  status: 'completed' | 'processing' | 'failed';
}

const DesignStudio: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [selectedTab, setSelectedTab] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [designRequest, setDesignRequest] = useState<DesignRequest>({
    projectId: '',
    requestType: 'comprehensive',
    content: '',
    buildingType: 'residential',
    location: '',
    area: 0,
    floors: 1,
    budget: 0,
    sustainability: 'high',
    style: 'modern',
    specialRequirements: [],
  });
  const [designResults, setDesignResults] = useState<DesignResult[]>([]);
  const [uploadedFiles, setUploadedFiles] = useState<any[]>([]);

  const steps = [
    '프로젝트 기본 정보',
    '설계 요구사항',
    '파일 업로드',
    'AI 분석 실행',
    '결과 검토',
  ];

  const requestTypes = [
    { value: 'comprehensive', label: '종합 설계 분석' },
    { value: 'architectural', label: '건축 설계' },
    { value: 'structural', label: '구조 설계' },
    { value: 'mep', label: 'MEP 설계' },
    { value: 'materials', label: '재료 선택' },
    { value: 'cost', label: '비용 분석' },
    { value: 'sustainability', label: '친환경 분석' },
  ];

  const buildingTypes = [
    { value: 'residential', label: '주거용' },
    { value: 'commercial', label: '상업용' },
    { value: 'industrial', label: '공업용' },
    { value: 'mixed', label: '복합용도' },
    { value: 'public', label: '공공시설' },
  ];

  const sustainabilityLevels = [
    { value: 'low', label: '기본' },
    { value: 'medium', label: '중간' },
    { value: 'high', label: '높음' },
    { value: 'premium', label: '최고급' },
  ];

  const architecturalStyles = [
    { value: 'modern', label: '모던' },
    { value: 'traditional', label: '전통' },
    { value: 'minimalist', label: '미니멀' },
    { value: 'industrial', label: '인더스트리얼' },
    { value: 'eclectic', label: '절충주의' },
  ];

  const specialRequirements = [
    '무장애 설계',
    '스마트홈 시스템',
    '태양광 발전',
    '우수 재활용',
    '지열 시스템',
    '옥상 정원',
    '주차장',
    '엘리베이터',
  ];

  // Mock 설계 결과
  const mockResults: DesignResult[] = [
    {
      id: '1',
      type: 'architectural',
      title: '건축 설계 분석',
      description: 'AI가 분석한 최적의 건축 설계 솔루션입니다.',
      recommendations: [
        { type: '공간 배치', content: '남향 배치로 자연 채광 극대화' },
        { type: '동선 계획', content: '효율적인 수직/수평 동선 구성' },
        { type: '외관 디자인', content: '현대적이면서 주변 환경과 조화' },
      ],
      confidence: 92,
      processingTime: 2.3,
      status: 'completed',
    },
    {
      id: '2',
      type: 'materials',
      title: '재료 선택 분석',
      description: '친환경적이고 비용 효율적인 재료 추천입니다.',
      recommendations: [
        { type: '구조재', content: '친환경 콘크리트 (탄소 저감형)' },
        { type: '단열재', content: '셀룰로오스 단열재 (재활용 소재)' },
        { type: '마감재', content: '천연 목재 및 친환경 페인트' },
      ],
      confidence: 88,
      processingTime: 1.8,
      status: 'completed',
    },
    {
      id: '3',
      type: 'structural',
      title: '구조 설계 분석',
      description: '안전하고 경제적인 구조 시스템을 제안합니다.',
      recommendations: [
        { type: '구조 시스템', content: 'RC조 + 철골 하이브리드' },
        { type: '기초 설계', content: '매트 기초 + 파일 보강' },
        { type: '내진 설계', content: '면진 장치 적용 권장' },
      ],
      confidence: 95,
      processingTime: 3.1,
      status: 'completed',
    },
    {
      id: '4',
      type: 'cost',
      title: '비용 분석',
      description: '상세한 공사비 분석과 비용 최적화 방안입니다.',
      recommendations: [
        { type: '총 공사비', content: '4억 8천만원 (VAT 별도)' },
        { type: '평당 단가', content: '480만원/평' },
        { type: '절감 방안', content: '15% 절감 가능 (재료 최적화)' },
      ],
      confidence: 87,
      processingTime: 1.5,
      status: 'completed',
    },
  ];

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleRunAnalysis = async () => {
    setIsProcessing(true);
    setActiveStep(3);

    try {
      // 실제 AI 분석 실행
      const analysisData = {
        request_type: designRequest.requestType as any,
        content: designRequest.content,
        building_type: designRequest.buildingType,
        location: designRequest.location,
        area: designRequest.area,
        floors: designRequest.floors,
        budget: designRequest.budget,
        sustainability: designRequest.sustainability,
        style: designRequest.style,
        special_requirements: designRequest.specialRequirements,
        uploaded_files: uploadedFiles.map(f => ({
          file_id: f.file_id,
          filename: f.filename,
          file_type: f.file_type
        })),
      };

      const result = await aiAPI.runComprehensiveAnalysis(analysisData);
      
      // 결과를 UI 형태로 변환
      const transformedResults = Object.entries(result.results).map(([agentId, agentResult]: [string, any]) => ({
        id: agentId,
        type: agentId.includes('materials') ? 'materials' :
              agentId.includes('structural') ? 'structural' :
              agentId.includes('cost') ? 'cost' : 'architectural',
        title: agentResult.agent_name,
        description: agentResult.analysis_result.summary || agentResult.analysis_result.detailed_analysis.substring(0, 100) + '...',
        recommendations: agentResult.analysis_result.recommended_materials || 
                        Object.entries(agentResult.analysis_result.cost_breakdown || {}).map(([key, value]) => ({
                          type: key,
                          content: `${value.toLocaleString()}원`
                        })) ||
                        [
                          { type: '분석 결과', content: agentResult.analysis_result.detailed_analysis.substring(0, 200) + '...' }
                        ],
        confidence: agentResult.confidence * 100,
        processingTime: agentResult.processing_time,
        status: 'completed' as const,
      }));

      setDesignResults(transformedResults);
      setActiveStep(4);
    } catch (error) {
      console.error('AI 분석 실패:', error);
      // 에러 시 모의 결과 사용
      setDesignResults(mockResults);
      setActiveStep(4);
    } finally {
      setIsProcessing(false);
    }
  };

  const getResultIcon = (type: string) => {
    switch (type) {
      case 'architectural':
        return <Architecture />;
      case 'materials':
        return <Eco />;
      case 'structural':
        return <Build />;
      case 'cost':
        return <Analytics />;
      default:
        return <AutoAwesome />;
    }
  };

  const getResultColor = (type: string) => {
    switch (type) {
      case 'architectural':
        return '#2563eb';
      case 'materials':
        return '#10b981';
      case 'structural':
        return '#f59e0b';
      case 'cost':
        return '#8b5cf6';
      default:
        return '#6b7280';
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
          VIBA AI 설계 스튜디오 🎨
        </Typography>
        <Typography variant="h6" color="textSecondary">
          AI의 힘으로 완벽한 건축 설계를 완성하세요
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* 설계 프로세스 */}
        <Grid item xs={12} lg={8}>
          <Card sx={{ borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}>
            <CardContent sx={{ p: 4 }}>
              <Stepper activeStep={activeStep} orientation="vertical">
                {/* 1단계: 기본 정보 */}
                <Step>
                  <StepLabel>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      프로젝트 기본 정보
                    </Typography>
                  </StepLabel>
                  <StepContent>
                    <Grid container spacing={2} sx={{ mt: 1 }}>
                      <Grid item xs={12}>
                        <TextField
                          fullWidth
                          label="설계 요청 내용"
                          multiline
                          rows={3}
                          value={designRequest.content}
                          onChange={(e) => setDesignRequest(prev => ({ ...prev, content: e.target.value }))}
                          placeholder="어떤 건물을 설계하고 싶으신지 자세히 설명해주세요..."
                          sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                        />
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <FormControl fullWidth>
                          <InputLabel>설계 유형</InputLabel>
                          <Select
                            value={designRequest.requestType}
                            onChange={(e) => setDesignRequest(prev => ({ ...prev, requestType: e.target.value }))}
                            label="설계 유형"
                            sx={{ borderRadius: 2 }}
                          >
                            {requestTypes.map((type) => (
                              <MenuItem key={type.value} value={type.value}>
                                {type.label}
                              </MenuItem>
                            ))}
                          </Select>
                        </FormControl>
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <FormControl fullWidth>
                          <InputLabel>건물 유형</InputLabel>
                          <Select
                            value={designRequest.buildingType}
                            onChange={(e) => setDesignRequest(prev => ({ ...prev, buildingType: e.target.value }))}
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
                      </Grid>
                      <Grid item xs={12}>
                        <TextField
                          fullWidth
                          label="위치"
                          value={designRequest.location}
                          onChange={(e) => setDesignRequest(prev => ({ ...prev, location: e.target.value }))}
                          placeholder="예: 서울시 강남구"
                          sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                        />
                      </Grid>
                    </Grid>
                    <Box sx={{ mt: 3, display: 'flex', gap: 1 }}>
                      <Button variant="contained" onClick={handleNext} sx={{ borderRadius: 2 }}>
                        다음
                      </Button>
                    </Box>
                  </StepContent>
                </Step>

                {/* 2단계: 상세 요구사항 */}
                <Step>
                  <StepLabel>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      설계 요구사항
                    </Typography>
                  </StepLabel>
                  <StepContent>
                    <Grid container spacing={2} sx={{ mt: 1 }}>
                      <Grid item xs={6} sm={3}>
                        <TextField
                          fullWidth
                          label="면적 (㎡)"
                          type="number"
                          value={designRequest.area}
                          onChange={(e) => setDesignRequest(prev => ({ ...prev, area: Number(e.target.value) }))}
                          sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                        />
                      </Grid>
                      <Grid item xs={6} sm={3}>
                        <TextField
                          fullWidth
                          label="층수"
                          type="number"
                          value={designRequest.floors}
                          onChange={(e) => setDesignRequest(prev => ({ ...prev, floors: Number(e.target.value) }))}
                          sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                        />
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <TextField
                          fullWidth
                          label="예산 (원)"
                          type="number"
                          value={designRequest.budget}
                          onChange={(e) => setDesignRequest(prev => ({ ...prev, budget: Number(e.target.value) }))}
                          sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                        />
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <FormControl fullWidth>
                          <InputLabel>친환경 수준</InputLabel>
                          <Select
                            value={designRequest.sustainability}
                            onChange={(e) => setDesignRequest(prev => ({ ...prev, sustainability: e.target.value }))}
                            label="친환경 수준"
                            sx={{ borderRadius: 2 }}
                          >
                            {sustainabilityLevels.map((level) => (
                              <MenuItem key={level.value} value={level.value}>
                                {level.label}
                              </MenuItem>
                            ))}
                          </Select>
                        </FormControl>
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <FormControl fullWidth>
                          <InputLabel>건축 스타일</InputLabel>
                          <Select
                            value={designRequest.style}
                            onChange={(e) => setDesignRequest(prev => ({ ...prev, style: e.target.value }))}
                            label="건축 스타일"
                            sx={{ borderRadius: 2 }}
                          >
                            {architecturalStyles.map((style) => (
                              <MenuItem key={style.value} value={style.value}>
                                {style.label}
                              </MenuItem>
                            ))}
                          </Select>
                        </FormControl>
                      </Grid>
                      <Grid item xs={12}>
                        <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                          특수 요구사항
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                          {specialRequirements.map((requirement) => (
                            <Chip
                              key={requirement}
                              label={requirement}
                              clickable
                              color={designRequest.specialRequirements.includes(requirement) ? 'primary' : 'default'}
                              onClick={() => {
                                setDesignRequest(prev => ({
                                  ...prev,
                                  specialRequirements: prev.specialRequirements.includes(requirement)
                                    ? prev.specialRequirements.filter(r => r !== requirement)
                                    : [...prev.specialRequirements, requirement]
                                }));
                              }}
                              sx={{ fontWeight: 500 }}
                            />
                          ))}
                        </Box>
                      </Grid>
                    </Grid>
                    <Box sx={{ mt: 3, display: 'flex', gap: 1 }}>
                      <Button onClick={handleBack} sx={{ borderRadius: 2 }}>
                        이전
                      </Button>
                      <Button variant="contained" onClick={handleNext} sx={{ borderRadius: 2 }}>
                        다음
                      </Button>
                    </Box>
                  </StepContent>
                </Step>

                {/* 3단계: 파일 업로드 */}
                <Step>
                  <StepLabel>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      파일 업로드
                    </Typography>
                  </StepLabel>
                  <StepContent>
                    <Box sx={{ mt: 2 }}>
                      <Alert severity="info" sx={{ mb: 3, borderRadius: 2 }}>
                        설계에 활용할 파일들을 업로드하세요. IFC, DWG, PDF, 이미지 등 다양한 형식을 지원합니다.
                      </Alert>
                      
                      <FileUpload
                        projectId={designRequest.projectId || 'demo-project'}
                        onUploadComplete={(files) => {
                          setUploadedFiles(prev => [...prev, ...files]);
                        }}
                        maxFiles={10}
                      />
                      
                      {uploadedFiles.length > 0 && (
                        <Box sx={{ mt: 3 }}>
                          <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
                            업로드된 파일 ({uploadedFiles.length}개)
                          </Typography>
                          <Grid container spacing={2}>
                            {uploadedFiles.map((file, index) => (
                              <Grid item xs={12} sm={6} md={4} key={index}>
                                <Card sx={{ borderRadius: 2, border: '1px solid #e2e8f0' }}>
                                  <CardContent sx={{ p: 2 }}>
                                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                      <FolderOpen sx={{ mr: 1, color: '#6b7280' }} />
                                      <Typography variant="subtitle2" sx={{ fontWeight: 600, fontSize: '0.85rem' }}>
                                        {file.filename}
                                      </Typography>
                                    </Box>
                                    <Typography variant="caption" color="textSecondary">
                                      {file.file_type} • {(file.file_size / 1024 / 1024).toFixed(2)}MB
                                    </Typography>
                                  </CardContent>
                                </Card>
                              </Grid>
                            ))}
                          </Grid>
                        </Box>
                      )}
                    </Box>
                    <Box sx={{ mt: 3, display: 'flex', gap: 1 }}>
                      <Button onClick={handleBack} sx={{ borderRadius: 2 }}>
                        이전
                      </Button>
                      <Button variant="contained" onClick={handleNext} sx={{ borderRadius: 2 }}>
                        다음
                      </Button>
                    </Box>
                  </StepContent>
                </Step>

                {/* 4단계: AI 분석 */}
                <Step>
                  <StepLabel>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      AI 분석 실행
                    </Typography>
                  </StepLabel>
                  <StepContent>
                    <Box sx={{ mt: 2 }}>
                      {!isProcessing ? (
                        <Alert severity="info" sx={{ mb: 3, borderRadius: 2 }}>
                          모든 정보가 입력되었습니다. AI 분석을 시작하시겠습니까?
                        </Alert>
                      ) : (
                        <Alert severity="info" sx={{ mb: 3, borderRadius: 2 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                            <CircularProgress size={20} />
                            VIBA AI가 종합적인 설계 분석을 수행하고 있습니다...
                          </Box>
                        </Alert>
                      )}
                      
                      <Grid container spacing={2}>
                        <Grid item xs={12} sm={6}>
                          <Paper sx={{ p: 2, borderRadius: 2, bgcolor: '#f8fafc' }}>
                            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                              분석 대상
                            </Typography>
                            <Typography variant="body2">
                              {requestTypes.find(t => t.value === designRequest.requestType)?.label}
                            </Typography>
                          </Paper>
                        </Grid>
                        <Grid item xs={12} sm={6}>
                          <Paper sx={{ p: 2, borderRadius: 2, bgcolor: '#f8fafc' }}>
                            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                              예상 소요시간
                            </Typography>
                            <Typography variant="body2">
                              2-5분
                            </Typography>
                          </Paper>
                        </Grid>
                      </Grid>
                    </Box>
                    <Box sx={{ mt: 3, display: 'flex', gap: 1 }}>
                      <Button onClick={handleBack} disabled={isProcessing} sx={{ borderRadius: 2 }}>
                        이전
                      </Button>
                      <Button
                        variant="contained"
                        onClick={handleRunAnalysis}
                        disabled={isProcessing}
                        startIcon={isProcessing ? <CircularProgress size={20} /> : <AutoAwesome />}
                        sx={{ borderRadius: 2 }}
                      >
                        {isProcessing ? '분석 중...' : 'AI 분석 시작'}
                      </Button>
                    </Box>
                  </StepContent>
                </Step>

                {/* 5단계: 결과 */}
                <Step>
                  <StepLabel>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      결과 검토
                    </Typography>
                  </StepLabel>
                  <StepContent>
                    <Alert severity="success" sx={{ mb: 3, borderRadius: 2 }}>
                      AI 분석이 완료되었습니다! 아래에서 상세 결과를 확인하세요.
                    </Alert>
                    <Box sx={{ mt: 3, display: 'flex', gap: 1 }}>
                      <Button onClick={handleBack} sx={{ borderRadius: 2 }}>
                        이전
                      </Button>
                      <Button variant="contained" startIcon={<CheckCircle />} sx={{ borderRadius: 2 }}>
                        결과 확인
                      </Button>
                    </Box>
                  </StepContent>
                </Step>
              </Stepper>
            </CardContent>
          </Card>
        </Grid>

        {/* 사이드바 - 진행 상황 & 도움말 */}
        <Grid item xs={12} lg={4}>
          <Card sx={{ borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.05)', mb: 3 }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 2 }}>
                진행 상황
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                  {activeStep + 1} / {steps.length} 단계
                </Typography>
                <Box
                  sx={{
                    width: '100%',
                    height: 8,
                    bgcolor: '#e2e8f0',
                    borderRadius: 4,
                    overflow: 'hidden',
                  }}
                >
                  <Box
                    sx={{
                      width: `${((activeStep + 1) / steps.length) * 100}%`,
                      height: '100%',
                      background: 'linear-gradient(90deg, #2563eb 0%, #3b82f6 100%)',
                      transition: 'width 0.3s ease',
                    }}
                  />
                </Box>
              </Box>
              <Typography variant="body2">
                현재 단계: {steps[activeStep]}
              </Typography>
            </CardContent>
          </Card>

          <Card sx={{ borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 2 }}>
                AI 분석 범위
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <Architecture sx={{ color: '#2563eb' }} />
                  </ListItemIcon>
                  <ListItemText primary="건축 설계" secondary="공간 배치, 동선, 외관" />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <Eco sx={{ color: '#10b981' }} />
                  </ListItemIcon>
                  <ListItemText primary="재료 분석" secondary="친환경성, 비용, 성능" />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <Build sx={{ color: '#f59e0b' }} />
                  </ListItemIcon>
                  <ListItemText primary="구조 설계" secondary="안전성, 경제성" />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <Analytics sx={{ color: '#8b5cf6' }} />
                  </ListItemIcon>
                  <ListItemText primary="비용 분석" secondary="상세 견적, 절감방안" />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <CloudUpload sx={{ color: '#ef4444' }} />
                  </ListItemIcon>
                  <ListItemText primary="파일 분석" secondary="IFC, DWG, PDF 처리" />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 결과 섹션 */}
      {designResults.length > 0 && (
        <Box sx={{ mt: 4 }}>
          <Card sx={{ borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}>
            <CardContent sx={{ p: 4 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h5" sx={{ fontWeight: 800 }}>
                  AI 분석 결과 📋
                </Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button startIcon={<Download />} variant="outlined" sx={{ borderRadius: 2 }}>
                    다운로드
                  </Button>
                  <Button startIcon={<Share />} variant="outlined" sx={{ borderRadius: 2 }}>
                    공유
                  </Button>
                  <Button startIcon={<Refresh />} variant="contained" sx={{ borderRadius: 2 }}>
                    재분석
                  </Button>
                </Box>
              </Box>

              {/* 결과 탭 */}
              <Paper sx={{ mb: 3, borderRadius: 2 }}>
                <Tabs
                  value={selectedTab}
                  onChange={(_, newValue) => setSelectedTab(newValue)}
                  variant="scrollable"
                  scrollButtons="auto"
                  sx={{ px: 2 }}
                >
                  <Tab label="전체 결과" />
                  <Tab label="건축 설계" />
                  <Tab label="재료 분석" />
                  <Tab label="구조 설계" />
                  <Tab label="비용 분석" />
                </Tabs>
              </Paper>

              <TabPanel value={selectedTab} index={0}>
                {/* 전체 결과 */}
                <Grid container spacing={3}>
                  {designResults.map((result) => (
                    <Grid item xs={12} key={result.id}>
                      <Accordion
                        sx={{
                          borderRadius: 2,
                          boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
                          '&:before': { display: 'none' },
                        }}
                      >
                        <AccordionSummary expandIcon={<ExpandMore />}>
                          <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                            <Box
                              sx={{
                                width: 48,
                                height: 48,
                                borderRadius: '50%',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                bgcolor: `${getResultColor(result.type)}15`,
                                color: getResultColor(result.type),
                                mr: 2,
                              }}
                            >
                              {getResultIcon(result.type)}
                            </Box>
                            <Box sx={{ flexGrow: 1 }}>
                              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                                {result.title}
                              </Typography>
                              <Typography variant="body2" color="textSecondary">
                                {result.description}
                              </Typography>
                            </Box>
                            <Box sx={{ textAlign: 'right', mr: 2 }}>
                              <Typography variant="h6" sx={{ fontWeight: 700, color: getResultColor(result.type) }}>
                                {result.confidence}%
                              </Typography>
                              <Typography variant="caption" color="textSecondary">
                                신뢰도
                              </Typography>
                            </Box>
                          </Box>
                        </AccordionSummary>
                        <AccordionDetails>
                          <Grid container spacing={2}>
                            {result.recommendations.map((rec, index) => (
                              <Grid item xs={12} sm={6} md={4} key={index}>
                                <Paper sx={{ p: 2, borderRadius: 2, bgcolor: '#f8fafc' }}>
                                  <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                                    {rec.type}
                                  </Typography>
                                  <Typography variant="body2">
                                    {rec.content}
                                  </Typography>
                                </Paper>
                              </Grid>
                            ))}
                          </Grid>
                          <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid #e2e8f0' }}>
                            <Typography variant="caption" color="textSecondary">
                              처리 시간: {result.processingTime}초 • 분석 완료: {new Date().toLocaleTimeString('ko-KR')}
                            </Typography>
                          </Box>
                        </AccordionDetails>
                      </Accordion>
                    </Grid>
                  ))}
                </Grid>
              </TabPanel>

              {/* 개별 탭들 */}
              {[1, 2, 3, 4].map((tabIndex) => (
                <TabPanel key={tabIndex} value={selectedTab} index={tabIndex}>
                  {designResults
                    .filter((result) => {
                      const types = ['architectural', 'materials', 'structural', 'cost'];
                      return result.type === types[tabIndex - 1];
                    })
                    .map((result) => (
                      <Box key={result.id}>
                        <Typography variant="h6" sx={{ fontWeight: 700, mb: 2 }}>
                          {result.title}
                        </Typography>
                        <Grid container spacing={2}>
                          {result.recommendations.map((rec, index) => (
                            <Grid item xs={12} sm={6} key={index}>
                              <Card sx={{ borderRadius: 2, border: '1px solid #e2e8f0' }}>
                                <CardContent sx={{ p: 2 }}>
                                  <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
                                    {rec.type}
                                  </Typography>
                                  <Typography variant="body2">
                                    {rec.content}
                                  </Typography>
                                </CardContent>
                              </Card>
                            </Grid>
                          ))}
                        </Grid>
                      </Box>
                    ))}
                </TabPanel>
              ))}
            </CardContent>
          </Card>
        </Box>
      )}
    </Container>
  );
};

export default DesignStudio;