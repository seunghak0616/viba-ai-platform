/**
 * BIM 뷰어 컨트롤 패널
 * 3D 뷰어 설정 및 제어 기능
 */
import React, { useState } from 'react';
import {
  Paper,
  IconButton,
  Tooltip,
  Divider,
  Switch,
  Slider,
  Typography,
  Collapse,
  Box,
  FormControlLabel,
  ButtonGroup,
  Button
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  GridOn as GridIcon,
  GridOff as GridOffIcon,
  ViewInAr as ViewInArIcon,
  Lightbulb as LightIcon,
  CameraAlt as CameraIcon,
  Refresh as RefreshIcon,
  ZoomIn as ZoomInIcon,
  ZoomOut as ZoomOutIcon,
  Home as HomeIcon,
  ExpandMore,
  ExpandLess
} from '@mui/icons-material';

import { useViewerState, useViewerActions } from '@stores/bimStore';
import { ViewerSettings } from '@types/index';

interface BimViewerControlsProps {
  className?: string;
}

/**
 * BIM 뷰어 컨트롤 패널 컴포넌트
 */
const BimViewerControls: React.FC<BimViewerControlsProps> = ({ className }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [activePanel, setActivePanel] = useState<'view' | 'lighting' | 'quality' | null>(null);

  // Store
  const viewerState = useViewerState();
  const { updateViewerSettings, resetViewer } = useViewerActions();
  const settings = viewerState.settings;

  /**
   * 설정 업데이트 핸들러
   */
  const handleSettingChange = <K extends keyof ViewerSettings>(
    key: K,
    value: ViewerSettings[K]
  ) => {
    updateViewerSettings({ [key]: value });
  };

  /**
   * 카메라 홈 위치로 리셋
   */
  const handleResetCamera = () => {
    updateViewerSettings({
      cameraPosition: { x: 10, y: 10, z: 10 },
      cameraTarget: { x: 0, y: 0, z: 0 }
    });
  };

  /**
   * 뷰어 전체 리셋
   */
  const handleResetViewer = () => {
    resetViewer();
  };

  /**
   * 패널 토글
   */
  const togglePanel = (panel: 'view' | 'lighting' | 'quality') => {
    setActivePanel(activePanel === panel ? null : panel);
  };

  return (
    <Paper 
      elevation={3} 
      className={className}
      sx={{ 
        display: 'flex',
        flexDirection: 'column',
        minWidth: 250,
        maxWidth: 300,
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(10px)'
      }}
    >
      {/* 헤더 */}
      <Box sx={{ p: 1, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography variant="subtitle2" fontWeight="bold">
          뷰어 컨트롤
        </Typography>
        <IconButton
          size="small"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          {isExpanded ? <ExpandLess /> : <ExpandMore />}
        </IconButton>
      </Box>

      {/* 기본 컨트롤 */}
      <Box sx={{ p: 1 }}>
        <ButtonGroup variant="outlined" size="small" fullWidth>
          <Tooltip title="홈 위치로 이동">
            <IconButton onClick={handleResetCamera}>
              <HomeIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="확대">
            <IconButton>
              <ZoomInIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="축소">
            <IconButton>
              <ZoomOutIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="뷰어 초기화">
            <IconButton onClick={handleResetViewer}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </ButtonGroup>
      </Box>

      <Divider />

      {/* 빠른 토글 */}
      <Box sx={{ p: 1 }}>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
          <Tooltip title={settings.showGrid ? "그리드 숨기기" : "그리드 표시"}>
            <IconButton
              size="small"
              color={settings.showGrid ? "primary" : "default"}
              onClick={() => handleSettingChange('showGrid', !settings.showGrid)}
            >
              {settings.showGrid ? <GridIcon /> : <GridOffIcon />}
            </IconButton>
          </Tooltip>
          
          <Tooltip title={settings.showAxes ? "축 숨기기" : "축 표시"}>
            <IconButton
              size="small"
              color={settings.showAxes ? "primary" : "default"}
              onClick={() => handleSettingChange('showAxes', !settings.showAxes)}
            >
              <ViewInArIcon />
            </IconButton>
          </Tooltip>
          
          <Tooltip title={settings.wireframe ? "솔리드 모드" : "와이어프레임 모드"}>
            <IconButton
              size="small"
              color={settings.wireframe ? "primary" : "default"}
              onClick={() => handleSettingChange('wireframe', !settings.wireframe)}
            >
              <VisibilityIcon />
            </IconButton>
          </Tooltip>
          
          <Tooltip title={settings.shadows ? "그림자 끄기" : "그림자 켜기"}>
            <IconButton
              size="small"
              color={settings.shadows ? "primary" : "default"}
              onClick={() => handleSettingChange('shadows', !settings.shadows)}
            >
              <LightIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* 확장 패널 */}
      <Collapse in={isExpanded}>
        <Divider />
        
        {/* 뷰 설정 */}
        <Box sx={{ p: 1 }}>
          <Button
            variant={activePanel === 'view' ? 'contained' : 'text'}
            size="small"
            fullWidth
            startIcon={<CameraIcon />}
            onClick={() => togglePanel('view')}
            sx={{ justifyContent: 'flex-start' }}
          >
            뷰 설정
          </Button>
          
          <Collapse in={activePanel === 'view'}>
            <Box sx={{ mt: 1, pl: 1 }}>
              <FormControlLabel
                control={
                  <Switch
                    size="small"
                    checked={settings.showGrid}
                    onChange={(e) => handleSettingChange('showGrid', e.target.checked)}
                  />
                }
                label="그리드 표시"
              />
              
              <FormControlLabel
                control={
                  <Switch
                    size="small"
                    checked={settings.showAxes}
                    onChange={(e) => handleSettingChange('showAxes', e.target.checked)}
                  />
                }
                label="좌표축 표시"
              />
              
              <FormControlLabel
                control={
                  <Switch
                    size="small"
                    checked={settings.wireframe}
                    onChange={(e) => handleSettingChange('wireframe', e.target.checked)}
                  />
                }
                label="와이어프레임"
              />
            </Box>
          </Collapse>
        </Box>

        <Divider />

        {/* 조명 설정 */}
        <Box sx={{ p: 1 }}>
          <Button
            variant={activePanel === 'lighting' ? 'contained' : 'text'}
            size="small"
            fullWidth
            startIcon={<LightIcon />}
            onClick={() => togglePanel('lighting')}
            sx={{ justifyContent: 'flex-start' }}
          >
            조명 설정
          </Button>
          
          <Collapse in={activePanel === 'lighting'}>
            <Box sx={{ mt: 1, pl: 1 }}>
              <FormControlLabel
                control={
                  <Switch
                    size="small"
                    checked={settings.shadows}
                    onChange={(e) => handleSettingChange('shadows', e.target.checked)}
                  />
                }
                label="그림자"
              />
              
              <Box sx={{ mt: 2 }}>
                <Typography variant="caption" gutterBottom>
                  조명 강도: {Math.round(settings.lightIntensity * 100)}%
                </Typography>
                <Slider
                  size="small"
                  value={settings.lightIntensity}
                  min={0.1}
                  max={2.0}
                  step={0.1}
                  onChange={(_, value) => handleSettingChange('lightIntensity', value as number)}
                  valueLabelDisplay="auto"
                  valueLabelFormat={(value) => `${Math.round(value * 100)}%`}
                />
              </Box>
            </Box>
          </Collapse>
        </Box>

        <Divider />

        {/* 품질 설정 */}
        <Box sx={{ p: 1 }}>
          <Button
            variant={activePanel === 'quality' ? 'contained' : 'text'}
            size="small"
            fullWidth
            startIcon={<SettingsIcon />}
            onClick={() => togglePanel('quality')}
            sx={{ justifyContent: 'flex-start' }}
          >
            품질 설정
          </Button>
          
          <Collapse in={activePanel === 'quality'}>
            <Box sx={{ mt: 1, pl: 1 }}>
              <Typography variant="caption" color="text.secondary">
                렌더링 품질 옵션은 향후 추가될 예정입니다.
              </Typography>
            </Box>
          </Collapse>
        </Box>
      </Collapse>

      {/* 푸터 정보 */}
      <Divider />
      <Box sx={{ p: 1 }}>
        <Typography variant="caption" color="text.secondary" align="center">
          Babylon.js v6.33.1
        </Typography>
      </Box>
    </Paper>
  );
};

export default BimViewerControls;