import React, { useState, useRef, useEffect } from 'react';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  ButtonGroup,
  IconButton,
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Alert,
  Tooltip,
  Paper,
  ToggleButton,
  ToggleButtonGroup,
} from '@mui/material';
import {
  View3D,
  ZoomIn,
  ZoomOut,
  RotateLeft,
  RotateRight,
  Fullscreen,
  FullscreenExit,
  Layers,
  Visibility,
  VisibilityOff,
  Settings,
  Download,
  Share,
  Upload,
  PhotoCamera,
  Straighten,
  Architecture,
  Engineering,
  Build,
  Palette,
  Science,
  Grid3x3,
  GridOff,
  Light,
  DarkMode,
  ColorLens,
  Speed,
  Info,
  Help,
} from '@mui/icons-material';

interface ModelLayer {
  id: string;
  name: string;
  type: 'structural' | 'architectural' | 'mep' | 'materials' | 'analysis';
  visible: boolean;
  opacity: number;
  color: string;
}

interface ViewSettings {
  showGrid: boolean;
  showAxes: boolean;
  wireframe: boolean;
  lighting: 'realistic' | 'bright' | 'soft';
  backgroundColor: string;
  renderQuality: 'low' | 'medium' | 'high';
}

interface Measurement {
  id: string;
  type: 'distance' | 'area' | 'angle';
  value: number;
  unit: string;
  points: number[][];
}

const ModelViewer: React.FC = () => {
  const viewerRef = useRef<HTMLDivElement>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [viewMode, setViewMode] = useState<'perspective' | 'orthographic'>('perspective');
  const [selectedTool, setSelectedTool] = useState<'select' | 'measure' | 'section'>('select');
  const [layersDialogOpen, setLayersDialogOpen] = useState(false);
  const [settingsDialogOpen, setSettingsDialogOpen] = useState(false);
  const [shareDialogOpen, setShareDialogOpen] = useState(false);
  const [zoom, setZoom] = useState(100);
  const [rotation, setRotation] = useState({ x: 0, y: 0, z: 0 });

  // 모델 레이어 설정
  const [layers, setLayers] = useState<ModelLayer[]>([
    {
      id: 'structural',
      name: '구조체',
      type: 'structural',
      visible: true,
      opacity: 100,
      color: '#64748b',
    },
    {
      id: 'walls',
      name: '벽체',
      type: 'architectural',
      visible: true,
      opacity: 100,
      color: '#e2e8f0',
    },
    {
      id: 'floors',
      name: '바닥',
      type: 'architectural',
      visible: true,
      opacity: 100,
      color: '#94a3b8',
    },
    {
      id: 'windows',
      name: '창호',
      type: 'architectural',
      visible: true,
      opacity: 80,
      color: '#3b82f6',
    },
    {
      id: 'hvac',
      name: 'HVAC 시스템',
      type: 'mep',
      visible: false,
      opacity: 70,
      color: '#10b981',
    },
    {
      id: 'electrical',
      name: '전기 시설',
      type: 'mep',
      visible: false,
      opacity: 70,
      color: '#f59e0b',
    },
    {
      id: 'plumbing',
      name: '배관',
      type: 'mep',
      visible: false,
      opacity: 70,
      color: '#06b6d4',
    },
  ]);

  // 뷰어 설정
  const [viewSettings, setViewSettings] = useState<ViewSettings>({
    showGrid: true,
    showAxes: true,
    wireframe: false,
    lighting: 'realistic',
    backgroundColor: '#f8fafc',
    renderQuality: 'high',
  });

  // 측정 데이터
  const [measurements, setMeasurements] = useState<Measurement[]>([
    {
      id: '1',
      type: 'distance',
      value: 12.5,
      unit: 'm',
      points: [[0, 0, 0], [12.5, 0, 0]],
    },
    {
      id: '2',
      type: 'area',
      value: 125.0,
      unit: '㎡',
      points: [[0, 0, 0], [10, 0, 0], [10, 12.5, 0], [0, 12.5, 0]],
    },
  ]);

  const handleLayerToggle = (layerId: string) => {
    setLayers(prev => prev.map(layer => 
      layer.id === layerId 
        ? { ...layer, visible: !layer.visible }
        : layer
    ));
  };

  const handleLayerOpacityChange = (layerId: string, opacity: number) => {
    setLayers(prev => prev.map(layer => 
      layer.id === layerId 
        ? { ...layer, opacity }
        : layer
    ));
  };

  const handleZoom = (delta: number) => {
    setZoom(prev => Math.max(10, Math.min(500, prev + delta)));
  };

  const handleRotation = (axis: 'x' | 'y' | 'z', delta: number) => {
    setRotation(prev => ({
      ...prev,
      [axis]: (prev[axis] + delta) % 360,
    }));
  };

  const handleFullscreen = () => {
    if (!isFullscreen && viewerRef.current) {
      if (viewerRef.current.requestFullscreen) {
        viewerRef.current.requestFullscreen();
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
    setIsFullscreen(!isFullscreen);
  };

  const handleExportScreenshot = () => {
    // TODO: 3D 뷰어 스크린샷 캡처 구현
    console.log('스크린샷 캡처');
  };

  const handleExportModel = (format: string) => {
    // TODO: 모델 내보내기 구현
    console.log(`모델 내보내기: ${format}`);
  };

  const getLayerIcon = (type: string) => {
    switch (type) {
      case 'structural':
        return <Engineering />;
      case 'architectural':
        return <Architecture />;
      case 'mep':
        return <Build />;
      case 'materials':
        return <Science />;
      case 'analysis':
        return <Speed />;
      default:
        return <Layers />;
    }
  };

  return (
    <Container maxWidth="xl">
      {/* 헤더 */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 800, mb: 1 }}>
          3D 모델 뷰어 🏗️
        </Typography>
        <Typography variant="h6" color="textSecondary">
          BIM 모델을 3D로 시각화하고 분석하세요
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* 3D 뷰어 영역 */}
        <Grid item xs={12} lg={9}>
          <Card sx={{ borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.05)', height: '70vh' }}>
            {/* 툴바 */}
            <Box sx={{ 
              p: 2, 
              borderBottom: '1px solid #e2e8f0',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              {/* 왼쪽 도구들 */}
              <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                <ToggleButtonGroup
                  value={selectedTool}
                  exclusive
                  onChange={(_, value) => setSelectedTool(value)}
                  size="small"
                >
                  <ToggleButton value="select">
                    <Tooltip title="선택">
                      <View3D />
                    </Tooltip>
                  </ToggleButton>
                  <ToggleButton value="measure">
                    <Tooltip title="측정">
                      <Straighten />
                    </Tooltip>
                  </ToggleButton>
                  <ToggleButton value="section">
                    <Tooltip title="단면">
                      <Architecture />
                    </Tooltip>
                  </ToggleButton>
                </ToggleButtonGroup>

                <Divider orientation="vertical" flexItem sx={{ mx: 1 }} />

                {/* 확대/축소 */}
                <ButtonGroup size="small">
                  <Button onClick={() => handleZoom(20)}>
                    <ZoomIn />
                  </Button>
                  <Button onClick={() => handleZoom(-20)}>
                    <ZoomOut />
                  </Button>
                </ButtonGroup>

                <Typography variant="body2" sx={{ mx: 1, minWidth: 60 }}>
                  {zoom}%
                </Typography>

                {/* 회전 */}
                <ButtonGroup size="small">
                  <Button onClick={() => handleRotation('y', -15)}>
                    <RotateLeft />
                  </Button>
                  <Button onClick={() => handleRotation('y', 15)}>
                    <RotateRight />
                  </Button>
                </ButtonGroup>
              </Box>

              {/* 오른쪽 도구들 */}
              <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                <Button
                  startIcon={<Layers />}
                  onClick={() => setLayersDialogOpen(true)}
                  size="small"
                >
                  레이어
                </Button>
                <Button
                  startIcon={<Settings />}
                  onClick={() => setSettingsDialogOpen(true)}
                  size="small"
                >
                  설정
                </Button>
                <Button
                  startIcon={<PhotoCamera />}
                  onClick={handleExportScreenshot}
                  size="small"
                >
                  캡처
                </Button>
                <Button
                  startIcon={<Share />}
                  onClick={() => setShareDialogOpen(true)}
                  size="small"
                >
                  공유
                </Button>
                <IconButton
                  onClick={handleFullscreen}
                  size="small"
                >
                  {isFullscreen ? <FullscreenExit /> : <Fullscreen />}
                </IconButton>
              </Box>
            </Box>

            {/* 3D 뷰어 컨테이너 */}
            <Box
              ref={viewerRef}
              sx={{
                height: 'calc(100% - 80px)',
                bgcolor: viewSettings.backgroundColor,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                position: 'relative',
                overflow: 'hidden',
              }}
            >
              {/* 3D 뷰어 플레이스홀더 */}
              <Box sx={{ textAlign: 'center' }}>
                <View3D sx={{ fontSize: 80, color: '#6b7280', mb: 2 }} />
                <Typography variant="h5" color="textSecondary" sx={{ fontWeight: 600 }}>
                  3D 모델 뷰어
                </Typography>
                <Typography variant="body1" color="textSecondary" sx={{ mt: 1 }}>
                  실제 프로젝트에서는 Three.js, Babylon.js 또는 다른 3D 라이브러리를 사용하여 구현
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<Upload />}
                  sx={{ mt: 2, borderRadius: 2 }}
                >
                  IFC 파일 업로드
                </Button>
              </Box>

              {/* 뷰어 정보 오버레이 */}
              <Paper
                sx={{
                  position: 'absolute',
                  top: 16,
                  left: 16,
                  p: 2,
                  bgcolor: 'rgba(255, 255, 255, 0.9)',
                  backdropFilter: 'blur(10px)',
                  borderRadius: 2,
                }}
              >
                <Typography variant="caption" color="textSecondary" sx={{ display: 'block' }}>
                  줌: {zoom}%
                </Typography>
                <Typography variant="caption" color="textSecondary" sx={{ display: 'block' }}>
                  회전: X:{rotation.x}° Y:{rotation.y}° Z:{rotation.z}°
                </Typography>
                <Typography variant="caption" color="textSecondary" sx={{ display: 'block' }}>
                  뷰 모드: {viewMode}
                </Typography>
              </Paper>

              {/* 네비게이션 큐브 */}
              <Paper
                sx={{
                  position: 'absolute',
                  top: 16,
                  right: 16,
                  width: 80,
                  height: 80,
                  bgcolor: 'rgba(255, 255, 255, 0.9)',
                  backdropFilter: 'blur(10px)',
                  borderRadius: 2,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Typography variant="caption" color="textSecondary" sx={{ textAlign: 'center' }}>
                  NAV<br />CUBE
                </Typography>
              </Paper>
            </Box>
          </Card>
        </Grid>

        {/* 사이드 패널 */}
        <Grid item xs={12} lg={3}>
          {/* 모델 정보 */}
          <Card sx={{ borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.05)', mb: 3 }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 2 }}>
                모델 정보
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 0.5 }}>
                  프로젝트명
                </Typography>
                <Typography variant="body1" sx={{ fontWeight: 600 }}>
                  친환경 주택 설계
                </Typography>
              </Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 0.5 }}>
                  파일 형식
                </Typography>
                <Chip label="IFC 4.3" size="small" color="primary" />
              </Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 0.5 }}>
                  파일 크기
                </Typography>
                <Typography variant="body2">
                  15.8 MB
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 0.5 }}>
                  요소 수
                </Typography>
                <Typography variant="body2">
                  1,247개 객체
                </Typography>
              </Box>
            </CardContent>
          </Card>

          {/* 레이어 컨트롤 */}
          <Card sx={{ borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.05)', mb: 3 }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 2 }}>
                레이어
              </Typography>
              <List dense>
                {layers.slice(0, 4).map((layer) => (
                  <ListItem key={layer.id} sx={{ px: 0 }}>
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      <IconButton
                        size="small"
                        onClick={() => handleLayerToggle(layer.id)}
                        sx={{ 
                          color: layer.visible ? layer.color : '#9ca3af',
                          '&:hover': { bgcolor: `${layer.color}15` }
                        }}
                      >
                        {layer.visible ? <Visibility /> : <VisibilityOff />}
                      </IconButton>
                    </ListItemIcon>
                    <ListItemText
                      primary={layer.name}
                      secondary={`${layer.opacity}% 투명도`}
                      primaryTypographyProps={{
                        variant: 'body2',
                        sx: { fontWeight: 500 }
                      }}
                      secondaryTypographyProps={{
                        variant: 'caption'
                      }}
                    />
                  </ListItem>
                ))}
              </List>
              <Button
                fullWidth
                variant="outlined"
                onClick={() => setLayersDialogOpen(true)}
                sx={{ mt: 1, borderRadius: 2 }}
              >
                전체 레이어 관리
              </Button>
            </CardContent>
          </Card>

          {/* 측정 결과 */}
          <Card sx={{ borderRadius: 3, boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 2 }}>
                측정 결과
              </Typography>
              <List dense>
                {measurements.map((measurement) => (
                  <ListItem key={measurement.id} sx={{ px: 0 }}>
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      <Straighten sx={{ color: '#2563eb' }} />
                    </ListItemIcon>
                    <ListItemText
                      primary={`${measurement.value} ${measurement.unit}`}
                      secondary={measurement.type === 'distance' ? '거리' : '면적'}
                      primaryTypographyProps={{
                        variant: 'body2',
                        sx: { fontWeight: 600 }
                      }}
                      secondaryTypographyProps={{
                        variant: 'caption'
                      }}
                    />
                  </ListItem>
                ))}
              </List>
              {measurements.length === 0 && (
                <Typography variant="body2" color="textSecondary" sx={{ textAlign: 'center', py: 2 }}>
                  측정 도구를 사용하여 거리나 면적을 측정하세요
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 레이어 관리 다이얼로그 */}
      <Dialog
        open={layersDialogOpen}
        onClose={() => setLayersDialogOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: { borderRadius: 3 },
        }}
      >
        <DialogTitle>
          <Typography variant="h6" sx={{ fontWeight: 700 }}>
            레이어 관리
          </Typography>
        </DialogTitle>
        <DialogContent>
          <List>
            {layers.map((layer, index) => (
              <React.Fragment key={layer.id}>
                <ListItem>
                  <ListItemIcon>
                    {getLayerIcon(layer.type)}
                  </ListItemIcon>
                  <ListItemText
                    primary={layer.name}
                    secondary={
                      <Box sx={{ mt: 1 }}>
                        <Typography variant="caption" color="textSecondary">
                          투명도: {layer.opacity}%
                        </Typography>
                        <Slider
                          value={layer.opacity}
                          onChange={(_, value) => handleLayerOpacityChange(layer.id, value as number)}
                          disabled={!layer.visible}
                          sx={{ mt: 1 }}
                        />
                      </Box>
                    }
                  />
                  <IconButton
                    onClick={() => handleLayerToggle(layer.id)}
                    sx={{ 
                      color: layer.visible ? layer.color : '#9ca3af',
                      ml: 2
                    }}
                  >
                    {layer.visible ? <Visibility /> : <VisibilityOff />}
                  </IconButton>
                </ListItem>
                {index < layers.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button onClick={() => setLayersDialogOpen(false)} sx={{ borderRadius: 2 }}>
            닫기
          </Button>
        </DialogActions>
      </Dialog>

      {/* 설정 다이얼로그 */}
      <Dialog
        open={settingsDialogOpen}
        onClose={() => setSettingsDialogOpen(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: { borderRadius: 3 },
        }}
      >
        <DialogTitle>
          <Typography variant="h6" sx={{ fontWeight: 700 }}>
            뷰어 설정
          </Typography>
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>조명 설정</InputLabel>
                <Select
                  value={viewSettings.lighting}
                  onChange={(e) => setViewSettings(prev => ({ ...prev, lighting: e.target.value as any }))}
                  label="조명 설정"
                >
                  <MenuItem value="realistic">사실적</MenuItem>
                  <MenuItem value="bright">밝음</MenuItem>
                  <MenuItem value="soft">부드러움</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>렌더링 품질</InputLabel>
                <Select
                  value={viewSettings.renderQuality}
                  onChange={(e) => setViewSettings(prev => ({ ...prev, renderQuality: e.target.value as any }))}
                  label="렌더링 품질"
                >
                  <MenuItem value="low">낮음 (빠름)</MenuItem>
                  <MenuItem value="medium">중간</MenuItem>
                  <MenuItem value="high">높음 (느림)</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button onClick={() => setSettingsDialogOpen(false)} sx={{ borderRadius: 2 }}>
            취소
          </Button>
          <Button variant="contained" sx={{ borderRadius: 2 }}>
            적용
          </Button>
        </DialogActions>
      </Dialog>

      {/* 공유 다이얼로그 */}
      <Dialog
        open={shareDialogOpen}
        onClose={() => setShareDialogOpen(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: { borderRadius: 3 },
        }}
      >
        <DialogTitle>
          <Typography variant="h6" sx={{ fontWeight: 700 }}>
            모델 공유
          </Typography>
        </DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2, borderRadius: 2 }}>
            모델을 다른 팀원들과 공유하거나 외부로 내보낼 수 있습니다.
          </Alert>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<Download />}
                onClick={() => handleExportModel('ifc')}
                sx={{ mb: 1, borderRadius: 2 }}
              >
                IFC 파일로 내보내기
              </Button>
            </Grid>
            <Grid item xs={12}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<Download />}
                onClick={() => handleExportModel('obj')}
                sx={{ mb: 1, borderRadius: 2 }}
              >
                OBJ 파일로 내보내기
              </Button>
            </Grid>
            <Grid item xs={12}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<Share />}
                sx={{ borderRadius: 2 }}
              >
                공유 링크 생성
              </Button>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button onClick={() => setShareDialogOpen(false)} sx={{ borderRadius: 2 }}>
            닫기
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ModelViewer;