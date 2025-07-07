/**
 * 파라메트릭 BIM 에디터 컴포넌트
 * 실시간으로 매개변수를 조정하여 3D 모델을 수정할 수 있는 인터페이스
 */
import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Slider,
  TextField,
  Switch,
  FormControlLabel,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Button,
  ButtonGroup,
  Chip,
  Grid,
  Card,
  CardContent,
  IconButton,
  Tooltip,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Divider,
  Alert,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction
} from '@mui/material';
import {
  ExpandMore,
  Tune,
  Architecture,
  Settings,
  Save,
  Upload,
  Download,
  Refresh,
  Add,
  Delete,
  Visibility,
  VisibilityOff,
  PlayArrow,
  Pause,
  Speed,
  Timeline,
  Assessment,
  Memory,
  AccountTree,
  Build,
  ColorLens,
  Lightbulb,
  Security,
  EcoRounded
} from '@mui/icons-material';
import { Engine, Scene, FreeCamera, Vector3, HemisphericLight } from '@babylonjs/core';
import { 
  ParametricBIMEngine, 
  ParametricParameter, 
  ParametricObject, 
  ParametricBIMData 
} from '../../services/parametricBimEngine';

interface ParametricBIMEditorProps {
  onModelChange?: (model: ParametricBIMData) => void;
  initialModel?: ParametricBIMData;
  readOnly?: boolean;
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
      id={`parametric-tabpanel-${index}`}
      aria-labelledby={`parametric-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const ParametricBIMEditor: React.FC<ParametricBIMEditorProps> = ({
  onModelChange,
  initialModel,
  readOnly = false
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [engine, setEngine] = useState<Engine | null>(null);
  const [scene, setScene] = useState<Scene | null>(null);
  const [bimEngine, setBimEngine] = useState<ParametricBIMEngine | null>(null);
  const [selectedTab, setSelectedTab] = useState(0);
  const [selectedObject, setSelectedObject] = useState<string | null>(null);
  const [objects, setObjects] = useState<Map<string, ParametricObject>>(new Map());
  const [globalParameters, setGlobalParameters] = useState<Map<string, ParametricParameter>>(new Map());
  const [isAnimating, setIsAnimating] = useState(false);
  const [performanceData, setPerformanceData] = useState<Record<string, any>>({});
  const [showPerformanceDialog, setShowPerformanceDialog] = useState(false);
  const [presetDialogOpen, setPresetDialogOpen] = useState(false);

  // Babylon.js 초기화
  useEffect(() => {
    if (!canvasRef.current) return;

    const babylonEngine = new Engine(canvasRef.current, true);
    const babylonScene = new Scene(babylonEngine);
    
    // 카메라 설정
    const camera = new FreeCamera('camera', new Vector3(0, 5, -10), babylonScene);
    camera.setTarget(Vector3.Zero());
    camera.attachToCanvas(canvasRef.current, true);
    
    // 조명 설정
    const light = new HemisphericLight('light', new Vector3(0, 1, 0), babylonScene);
    light.intensity = 0.7;
    
    // 파라메트릭 BIM 엔진 초기화
    const parametricEngine = new ParametricBIMEngine(babylonScene);
    
    setEngine(babylonEngine);
    setScene(babylonScene);
    setBimEngine(parametricEngine);

    // 렌더링 루프 시작
    babylonEngine.runRenderLoop(() => {
      babylonScene.render();
    });

    // 리사이즈 이벤트 처리
    const handleResize = () => {
      babylonEngine.resize();
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      babylonEngine.dispose();
    };
  }, []);

  // 초기 모델 로드
  useEffect(() => {
    if (bimEngine && initialModel) {
      bimEngine.importParametricModel(initialModel);
      updateDisplayData();
    } else if (bimEngine) {
      // 기본 예제 생성
      createDefaultExample();
    }
  }, [bimEngine, initialModel]);

  // 기본 예제 생성
  const createDefaultExample = () => {
    if (!bimEngine) return;

    // 벽 생성
    const wall1 = bimEngine.createParametricWall(
      'wall_1',
      new Vector3(-5, 0, -3),
      new Vector3(5, 0, -3)
    );

    const wall2 = bimEngine.createParametricWall(
      'wall_2',
      new Vector3(5, 0, -3),
      new Vector3(5, 0, 3)
    );

    const wall3 = bimEngine.createParametricWall(
      'wall_3',
      new Vector3(5, 0, 3),
      new Vector3(-5, 0, 3)
    );

    const wall4 = bimEngine.createParametricWall(
      'wall_4',
      new Vector3(-5, 0, 3),
      new Vector3(-5, 0, -3)
    );

    // 창문 생성
    bimEngine.createParametricWindow('window_1', 'wall_1', 0.3);
    bimEngine.createParametricWindow('window_2', 'wall_1', 0.7);

    // 방 생성
    bimEngine.createParametricRoom('room_1', [
      new Vector3(-5, 0, -3),
      new Vector3(5, 0, -3),
      new Vector3(5, 0, 3),
      new Vector3(-5, 0, 3)
    ]);

    updateDisplayData();
  };

  // 디스플레이 데이터 업데이트
  const updateDisplayData = () => {
    if (!bimEngine) return;

    const model = bimEngine.exportParametricModel();
    setObjects(new Map(model.objects.map(obj => [obj.id, obj])));
    setGlobalParameters(new Map(model.globalParameters.map(param => [param.name, param])));
    
    // 성능 데이터 업데이트
    const perfData = bimEngine.analyzePerformance();
    setPerformanceData(perfData);

    // 모델 변경 콜백
    if (onModelChange) {
      onModelChange(model);
    }
  };

  // 매개변수 업데이트 핸들러
  const handleParameterUpdate = useCallback((objectId: string | null, parameterName: string, value: any) => {
    if (!bimEngine) return;

    if (objectId) {
      bimEngine.updateParameter(objectId, parameterName, value);
    } else {
      bimEngine.updateGlobalParameter(parameterName, value);
    }

    updateDisplayData();
  }, [bimEngine]);

  // 매개변수 컨트롤 렌더링
  const renderParameterControl = (
    parameter: ParametricParameter,
    objectId: string | null = null
  ) => {
    const isReadOnly = readOnly;

    switch (parameter.type) {
      case 'number':
      case 'range':
        return (
          <Box key={parameter.name} sx={{ mb: 2 }}>
            <Typography variant="body2" gutterBottom>
              {parameter.label} 
              {parameter.unit && ` (${parameter.unit})`}
              <Chip 
                size="small" 
                label={parameter.category} 
                sx={{ ml: 1, fontSize: '0.6rem' }}
              />
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Slider
                value={parameter.value}
                min={parameter.min}
                max={parameter.max}
                step={parameter.step}
                onChange={(_, value) => handleParameterUpdate(objectId, parameter.name, value)}
                disabled={isReadOnly}
                sx={{ flexGrow: 1 }}
                marks={parameter.type === 'range'}
                valueLabelDisplay="auto"
              />
              <TextField
                size="small"
                type="number"
                value={parameter.value}
                onChange={(e) => handleParameterUpdate(objectId, parameter.name, parseFloat(e.target.value))}
                disabled={isReadOnly}
                sx={{ width: 80 }}
                inputProps={{
                  min: parameter.min,
                  max: parameter.max,
                  step: parameter.step
                }}
              />
            </Box>
            {parameter.description && (
              <Typography variant="caption" color="textSecondary">
                {parameter.description}
              </Typography>
            )}
          </Box>
        );

      case 'boolean':
        return (
          <Box key={parameter.name} sx={{ mb: 2 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={parameter.value}
                  onChange={(e) => handleParameterUpdate(objectId, parameter.name, e.target.checked)}
                  disabled={isReadOnly}
                />
              }
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  {parameter.label}
                  <Chip 
                    size="small" 
                    label={parameter.category} 
                    sx={{ fontSize: '0.6rem' }}
                  />
                </Box>
              }
            />
            {parameter.description && (
              <Typography variant="caption" color="textSecondary" display="block">
                {parameter.description}
              </Typography>
            )}
          </Box>
        );

      case 'string':
        if (parameter.name === 'materialType' || parameter.name === 'function') {
          const options = getStringParameterOptions(parameter.name);
          return (
            <Box key={parameter.name} sx={{ mb: 2 }}>
              <FormControl fullWidth size="small">
                <InputLabel>{parameter.label}</InputLabel>
                <Select
                  value={parameter.value}
                  label={parameter.label}
                  onChange={(e) => handleParameterUpdate(objectId, parameter.name, e.target.value)}
                  disabled={isReadOnly}
                >
                  {options.map(option => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              {parameter.description && (
                <Typography variant="caption" color="textSecondary">
                  {parameter.description}
                </Typography>
              )}
            </Box>
          );
        }
        return (
          <Box key={parameter.name} sx={{ mb: 2 }}>
            <TextField
              fullWidth
              size="small"
              label={parameter.label}
              value={parameter.value}
              onChange={(e) => handleParameterUpdate(objectId, parameter.name, e.target.value)}
              disabled={isReadOnly}
            />
            {parameter.description && (
              <Typography variant="caption" color="textSecondary">
                {parameter.description}
              </Typography>
            )}
          </Box>
        );

      default:
        return null;
    }
  };

  // 문자열 매개변수 옵션
  const getStringParameterOptions = (parameterName: string) => {
    const options: Record<string, Array<{value: string, label: string}>> = {
      materialType: [
        { value: 'concrete', label: '콘크리트' },
        { value: 'brick', label: '벽돌' },
        { value: 'wood', label: '목재' },
        { value: 'steel', label: '강재' }
      ],
      function: [
        { value: '거실', label: '거실' },
        { value: '침실', label: '침실' },
        { value: '주방', label: '주방' },
        { value: '화장실', label: '화장실' },
        { value: '사무실', label: '사무실' },
        { value: '회의실', label: '회의실' },
        { value: '휴게실', label: '휴게실' }
      ],
      floorMaterial: [
        { value: 'wood', label: '목재' },
        { value: 'tile', label: '타일' },
        { value: 'carpet', label: '카펫' },
        { value: 'concrete', label: '콘크리트' }
      ],
      glazingType: [
        { value: 'single', label: '단창' },
        { value: 'double', label: '복층' },
        { value: 'triple', label: '삼중창' },
        { value: 'low-e', label: 'Low-E 유리' }
      ]
    };

    return options[parameterName] || [];
  };

  // 카테고리별 아이콘
  const getCategoryIcon = (category: string) => {
    const icons: Record<string, React.ReactNode> = {
      geometry: <Architecture />,
      material: <ColorLens />,
      structure: <Build />,
      environment: <EcoRounded />,
      function: <Settings />
    };
    return icons[category] || <Tune />;
  };

  // 성능 분석 다이얼로그
  const renderPerformanceDialog = () => (
    <Dialog
      open={showPerformanceDialog}
      onClose={() => setShowPerformanceDialog(false)}
      maxWidth="md"
      fullWidth
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Assessment />
          성능 분석 결과
        </Box>
      </DialogTitle>
      <DialogContent>
        <Grid container spacing={2}>
          <Grid item xs={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <Memory sx={{ mr: 1 }} />
                  메모리 사용량
                </Typography>
                <Typography variant="h4" color="primary">
                  {Math.round(performanceData.memoryUsage / 1024)} KB
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <Speed sx={{ mr: 1 }} />
                  렌더링 복잡도
                </Typography>
                <Typography variant="h4" color="secondary">
                  {performanceData.renderComplexity?.toLocaleString() || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <AccountTree sx={{ mr: 1 }} />
                  객체 수
                </Typography>
                <Typography variant="h4" color="success.main">
                  {performanceData.objectCount}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <Tune sx={{ mr: 1 }} />
                  매개변수 수
                </Typography>
                <Typography variant="h4" color="info.main">
                  {performanceData.parameterCount}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setShowPerformanceDialog(false)}>
          닫기
        </Button>
      </DialogActions>
    </Dialog>
  );

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* 헤더 */}
      <Paper sx={{ p: 2, borderRadius: 0 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h5" sx={{ fontWeight: 700 }}>
            🎛️ 파라메트릭 BIM 에디터
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <ButtonGroup variant="outlined" size="small">
              <Button startIcon={<Save />}>저장</Button>
              <Button startIcon={<Upload />}>불러오기</Button>
              <Button startIcon={<Download />}>내보내기</Button>
            </ButtonGroup>
            <Button
              variant="contained"
              size="small"
              startIcon={<Assessment />}
              onClick={() => setShowPerformanceDialog(true)}
            >
              성능 분석
            </Button>
            <Button
              variant={isAnimating ? "contained" : "outlined"}
              size="small"
              startIcon={isAnimating ? <Pause /> : <PlayArrow />}
              onClick={() => setIsAnimating(!isAnimating)}
              color={isAnimating ? "secondary" : "primary"}
            >
              {isAnimating ? '일시정지' : '애니메이션'}
            </Button>
          </Box>
        </Box>
      </Paper>

      <Box sx={{ display: 'flex', flexGrow: 1 }}>
        {/* 3D 뷰어 */}
        <Box sx={{ flexGrow: 1, position: 'relative' }}>
          <canvas
            ref={canvasRef}
            style={{
              width: '100%',
              height: '100%',
              display: 'block',
              outline: 'none'
            }}
          />
          {performanceData.renderComplexity > 50000 && (
            <Alert 
              severity="warning" 
              sx={{ position: 'absolute', top: 16, left: 16, maxWidth: 300 }}
            >
              렌더링 복잡도가 높습니다. 성능 최적화를 권장합니다.
            </Alert>
          )}
        </Box>

        {/* 사이드 패널 */}
        <Paper sx={{ width: 400, borderRadius: 0, borderLeft: 1, borderColor: 'divider' }}>
          <Tabs
            value={selectedTab}
            onChange={(_, newValue) => setSelectedTab(newValue)}
            variant="fullWidth"
          >
            <Tab label="글로벌" icon={<Settings />} />
            <Tab label="객체" icon={<Architecture />} />
            <Tab label="분석" icon={<Assessment />} />
          </Tabs>

          <TabPanel value={selectedTab} index={0}>
            {/* 글로벌 매개변수 */}
            <Typography variant="h6" gutterBottom>
              글로벌 매개변수
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            {Array.from(globalParameters.values())
              .sort((a, b) => a.category.localeCompare(b.category))
              .reduce((acc, param) => {
                const category = param.category;
                if (!acc[category]) acc[category] = [];
                acc[category].push(param);
                return acc;
              }, {} as Record<string, ParametricParameter[]>)
              &&
              Object.entries(
                Array.from(globalParameters.values())
                  .reduce((acc, param) => {
                    const category = param.category;
                    if (!acc[category]) acc[category] = [];
                    acc[category].push(param);
                    return acc;
                  }, {} as Record<string, ParametricParameter[]>)
              ).map(([category, params]) => (
                <Accordion key={category} defaultExpanded>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {getCategoryIcon(category)}
                      <Typography variant="subtitle1" sx={{ textTransform: 'capitalize' }}>
                        {category === 'geometry' ? '형태' :
                         category === 'material' ? '재료' :
                         category === 'structure' ? '구조' :
                         category === 'environment' ? '환경' :
                         category === 'function' ? '기능' : category}
                      </Typography>
                      <Chip size="small" label={params.length} />
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    {params.map(param => renderParameterControl(param, null))}
                  </AccordionDetails>
                </Accordion>
              ))
            }
          </TabPanel>

          <TabPanel value={selectedTab} index={1}>
            {/* 객체 목록 */}
            <Typography variant="h6" gutterBottom>
              파라메트릭 객체
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <List>
              {Array.from(objects.values()).map(object => (
                <ListItem
                  key={object.id}
                  button
                  selected={selectedObject === object.id}
                  onClick={() => setSelectedObject(
                    selectedObject === object.id ? null : object.id
                  )}
                >
                  <ListItemIcon>
                    {getCategoryIcon(object.type)}
                  </ListItemIcon>
                  <ListItemText
                    primary={object.name}
                    secondary={`${object.type} • ${object.parameters.length}개 매개변수`}
                  />
                  <ListItemSecondaryAction>
                    <IconButton size="small">
                      <Visibility />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>

            {selectedObject && objects.get(selectedObject) && (
              <Box sx={{ mt: 2, p: 2, border: 1, borderColor: 'divider', borderRadius: 1 }}>
                <Typography variant="subtitle1" gutterBottom>
                  {objects.get(selectedObject)!.name} 속성
                </Typography>
                <Divider sx={{ mb: 2 }} />
                {objects.get(selectedObject)!.parameters.map(param =>
                  renderParameterControl(param, selectedObject)
                )}
              </Box>
            )}
          </TabPanel>

          <TabPanel value={selectedTab} index={2}>
            {/* 분석 및 최적화 */}
            <Typography variant="h6" gutterBottom>
              모델 분석
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Card>
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Memory color="primary" sx={{ fontSize: 40, mb: 1 }} />
                    <Typography variant="subtitle2">메모리</Typography>
                    <Typography variant="h6">
                      {Math.round((performanceData.memoryUsage || 0) / 1024)}KB
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6}>
                <Card>
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Speed color="secondary" sx={{ fontSize: 40, mb: 1 }} />
                    <Typography variant="subtitle2">복잡도</Typography>
                    <Typography variant="h6">
                      {(performanceData.renderComplexity || 0).toLocaleString()}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            <Box sx={{ mt: 3 }}>
              <Typography variant="subtitle1" gutterBottom>
                최적화 제안
              </Typography>
              <Alert severity="info" sx={{ mb: 1 }}>
                • 불필요한 매개변수 제거로 성능 향상 가능
              </Alert>
              <Alert severity="success" sx={{ mb: 1 }}>
                • 현재 모델 복잡도는 적정 수준입니다
              </Alert>
              {performanceData.renderComplexity > 50000 && (
                <Alert severity="warning">
                  • 렌더링 최적화가 필요합니다
                </Alert>
              )}
            </Box>
          </TabPanel>
        </Paper>
      </Box>

      {/* 성능 분석 다이얼로그 */}
      {renderPerformanceDialog()}
    </Box>
  );
};

export default ParametricBIMEditor;