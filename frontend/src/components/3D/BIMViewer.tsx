import React, { useRef, useEffect, useState, useCallback } from 'react';
import { Box, Paper, IconButton, Tooltip, Typography, Alert } from '@mui/material';
import {
  ZoomIn,
  ZoomOut,
  CenterFocusStrong,
  Fullscreen,
  FullscreenExit,
  Refresh,
  Visibility,
  VisibilityOff,
  GridOn,
  GridOff,
  Settings,
  Info
} from '@mui/icons-material';
import {
  Engine,
  Scene,
  FreeCamera,
  Vector3,
  HemisphericLight,
  DirectionalLight,
  MeshBuilder,
  StandardMaterial,
  Color3,
  GroundMesh,
  Mesh,
  UniversalCamera,
  ArcRotateCamera,
  Tools,
  Vector4,
  CSG,
  Animation,
  AnimationGroup
} from '@babylonjs/core';
import '@babylonjs/loaders/glTF';
import '@babylonjs/materials';
import { BIMToThreeService } from '../../services/bimToThreeService';

interface Room {
  type: string;
  count: number;
  area: number;
  orientation?: string;
  position?: { x: number; y: number; z: number };
  dimensions?: { width: number; height: number; depth: number };
}

interface BIMData {
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
}

interface BIMViewerProps {
  bimData?: BIMData;
  width?: string | number;
  height?: string | number;
  enableControls?: boolean;
  showGrid?: boolean;
  onSceneReady?: (scene: Scene) => void;
  onModelLoad?: (meshes: Mesh[]) => void;
}

const BIMViewer: React.FC<BIMViewerProps> = ({
  bimData,
  width = '100%',
  height = 600,
  enableControls = true,
  showGrid = true,
  onSceneReady,
  onModelLoad
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const engineRef = useRef<Engine | null>(null);
  const sceneRef = useRef<Scene | null>(null);
  const cameraRef = useRef<ArcRotateCamera | null>(null);
  
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isGridVisible, setIsGridVisible] = useState(showGrid);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [meshes, setMeshes] = useState<Mesh[]>([]);

  // 3D 씬 초기화
  const initializeScene = useCallback(() => {
    if (!canvasRef.current) return;

    try {
      // 엔진 생성
      const engine = new Engine(canvasRef.current, true, {
        preserveDrawingBuffer: true,
        stencil: true,
        antialias: true
      });
      engineRef.current = engine;

      // 씬 생성
      const scene = new Scene(engine);
      sceneRef.current = scene;

      // 카메라 설정
      const camera = new ArcRotateCamera(
        'camera',
        -Math.PI / 2,
        Math.PI / 2.5,
        15,
        Vector3.Zero(),
        scene
      );
      
      // 최신 Babylon.js에서는 attachControls가 scene.attachControl로 변경됨
      if (canvasRef.current) {
        scene.attachControl(canvasRef.current, true);
      }
      camera.setTarget(Vector3.Zero());
      cameraRef.current = camera;

      // 조명 설정
      const hemisphericLight = new HemisphericLight(
        'hemisphericLight',
        new Vector3(0, 1, 0),
        scene
      );
      hemisphericLight.intensity = 0.6;

      const directionalLight = new DirectionalLight(
        'directionalLight',
        new Vector3(-1, -1, -1),
        scene
      );
      directionalLight.intensity = 0.8;
      directionalLight.position = new Vector3(20, 20, 20);

      // 그리드 생성
      if (isGridVisible) {
        createGrid(scene);
      }

      // BIM 모델 생성
      if (bimData) {
        createBIMModel(scene, bimData);
      } else {
        createSampleModel(scene);
      }

      // 렌더링 시작
      engine.runRenderLoop(() => {
        scene.render();
      });

      // 리사이즈 핸들러
      const handleResize = () => {
        engine.resize();
      };
      window.addEventListener('resize', handleResize);

      onSceneReady?.(scene);
      setIsLoading(false);

      return () => {
        window.removeEventListener('resize', handleResize);
        engine.dispose();
      };
    } catch (err) {
      console.error('3D 씬 초기화 실패:', err);
      setError('3D 뷰어를 초기화할 수 없습니다.');
      setIsLoading(false);
    }
  }, [bimData, isGridVisible, onSceneReady]);

  // 그리드 생성
  const createGrid = (scene: Scene) => {
    const ground = MeshBuilder.CreateGround(
      'ground',
      { width: 50, height: 50, subdivisions: 50 },
      scene
    );
    
    const groundMaterial = new StandardMaterial('groundMaterial', scene);
    groundMaterial.wireframe = true;
    groundMaterial.emissiveColor = new Color3(0.2, 0.2, 0.2);
    ground.material = groundMaterial;
    ground.position.y = -0.1;
  };

  // BIM 모델 생성 (향상된 버전)
  const createBIMModel = (scene: Scene, data: BIMData) => {
    const createdMeshes: Mesh[] = [];

    try {
      // BIMToThreeService를 사용한 고급 모델 생성
      const bimService = new BIMToThreeService(scene);
      
      // 레이아웃 최적화
      const optimizedData = bimService.optimizeLayout(data);
      
      // 완전한 건물 생성
      const building = bimService.createBuilding(optimizedData);
      
      // 모든 메쉬 수집
      createdMeshes.push(building.foundation);
      createdMeshes.push(...building.walls);
      createdMeshes.push(...building.rooms.map(r => r.mesh));
      createdMeshes.push(...building.windows);
      createdMeshes.push(...building.doors);
      if (building.roof) {
        createdMeshes.push(building.roof);
      }

      // 애니메이션 추가
      const animationGroup = bimService.addBuildingAnimation(building);
      animationGroup.play();

      setMeshes(createdMeshes);
      onModelLoad?.(createdMeshes);

      console.log('고급 BIM 모델 생성 완료:', {
        foundation: 1,
        walls: building.walls.length,
        rooms: building.rooms.length,
        windows: building.windows.length,
        doors: building.doors.length,
        roof: building.roof ? 1 : 0
      });

    } catch (err) {
      console.error('BIM 모델 생성 실패:', err);
      setError('BIM 모델을 생성할 수 없습니다.');
      
      // 폴백: 기본 모델 생성
      createFallbackModel(scene, data);
    }
  };

  // 폴백 모델 생성 (기존 간단한 버전)
  const createFallbackModel = (scene: Scene, data: BIMData) => {
    const createdMeshes: Mesh[] = [];

    try {
      const totalArea = data.totalArea.value;
      const buildingWidth = Math.sqrt(totalArea * 3.3) * 0.8;
      const buildingDepth = Math.sqrt(totalArea * 3.3) * 0.6;
      const buildingHeight = 3;

      // 간단한 건물 구조
      const foundation = MeshBuilder.CreateBox(
        'foundation',
        { width: buildingWidth, height: 0.5, depth: buildingDepth },
        scene
      );
      foundation.position.y = -0.25;
      
      const foundationMaterial = new StandardMaterial('foundationMaterial', scene);
      foundationMaterial.diffuseColor = new Color3(0.6, 0.6, 0.6);
      foundation.material = foundationMaterial;
      createdMeshes.push(foundation);

      // 단순한 방 배치
      data.rooms.forEach((room, index) => {
        const roomArea = room.area || (totalArea / data.rooms.length);
        const roomWidth = Math.sqrt(roomArea * 3.3) * 0.6;
        const roomDepth = Math.sqrt(roomArea * 3.3) * 0.4;

        const roomMesh = MeshBuilder.CreateBox(
          `simple_room_${index}`,
          { width: roomWidth, height: buildingHeight, depth: roomDepth },
          scene
        );

        roomMesh.position = new Vector3(
          (index % 2) * roomWidth - roomWidth / 2,
          buildingHeight / 2,
          Math.floor(index / 2) * roomDepth - roomDepth / 2
        );

        const roomMaterial = new StandardMaterial(`simple_room_material_${index}`, scene);
        roomMaterial.diffuseColor = new Color3(0.8, 0.8, 0.9);
        roomMaterial.alpha = 0.7;
        roomMesh.material = roomMaterial;

        createdMeshes.push(roomMesh);
      });

      setMeshes(createdMeshes);
      onModelLoad?.(createdMeshes);

    } catch (err) {
      console.error('폴백 모델 생성도 실패:', err);
      setError('모델을 생성할 수 없습니다.');
    }
  };

  // 샘플 모델 생성
  const createSampleModel = (scene: Scene) => {
    const createdMeshes: Mesh[] = [];

    // 샘플 건물 생성
    const building = MeshBuilder.CreateBox(
      'sampleBuilding',
      { width: 10, height: 3, depth: 8 },
      scene
    );
    building.position.y = 1.5;

    const buildingMaterial = new StandardMaterial('buildingMaterial', scene);
    buildingMaterial.diffuseColor = new Color3(0.8, 0.8, 0.9);
    building.material = buildingMaterial;

    createdMeshes.push(building);
    setMeshes(createdMeshes);
    onModelLoad?.(createdMeshes);
  };

  // 카메라 리셋
  const resetCamera = () => {
    if (cameraRef.current) {
      cameraRef.current.setTarget(Vector3.Zero());
      cameraRef.current.alpha = -Math.PI / 2;
      cameraRef.current.beta = Math.PI / 2.5;
      cameraRef.current.radius = 15;
    }
  };

  // 줌 인
  const zoomIn = () => {
    if (cameraRef.current) {
      cameraRef.current.radius = Math.max(cameraRef.current.radius - 2, 2);
    }
  };

  // 줌 아웃
  const zoomOut = () => {
    if (cameraRef.current) {
      cameraRef.current.radius = Math.min(cameraRef.current.radius + 2, 50);
    }
  };

  // 그리드 토글
  const toggleGrid = () => {
    setIsGridVisible(!isGridVisible);
    if (sceneRef.current) {
      const ground = sceneRef.current.getMeshByName('ground');
      if (ground) {
        ground.dispose();
      }
      if (!isGridVisible) {
        createGrid(sceneRef.current);
      }
    }
  };

  // 전체화면 토글
  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      canvasRef.current?.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  // 씬 새로고침
  const refreshScene = () => {
    if (engineRef.current && sceneRef.current) {
      // 기존 메쉬 제거
      meshes.forEach(mesh => mesh.dispose());
      setMeshes([]);
      
      // BIM 모델 재생성
      if (bimData) {
        createBIMModel(sceneRef.current, bimData);
      } else {
        createSampleModel(sceneRef.current);
      }
    }
  };

  useEffect(() => {
    const cleanup = initializeScene();
    return cleanup;
  }, [initializeScene]);

  return (
    <Paper elevation={3} sx={{ position: 'relative', width, height }}>
      {/* 로딩 및 에러 표시 */}
      {isLoading && (
        <Box
          display="flex"
          alignItems="center"
          justifyContent="center"
          height="100%"
          position="absolute"
          top={0}
          left={0}
          right={0}
          bottom={0}
          bgcolor="rgba(255,255,255,0.8)"
          zIndex={10}
        >
          <Typography>3D 뷰어 로딩 중...</Typography>
        </Box>
      )}

      {error && (
        <Alert severity="error" sx={{ position: 'absolute', top: 10, left: 10, right: 10, zIndex: 10 }}>
          {error}
        </Alert>
      )}

      {/* 3D 캔버스 */}
      <canvas
        ref={canvasRef}
        style={{
          width: '100%',
          height: '100%',
          display: 'block',
          outline: 'none'
        }}
      />

      {/* 컨트롤 패널 */}
      {enableControls && !isLoading && (
        <Box
          position="absolute"
          top={10}
          right={10}
          display="flex"
          flexDirection="column"
          gap={1}
          zIndex={5}
        >
          <Tooltip title="줌 인">
            <IconButton size="small" onClick={zoomIn} sx={{ bgcolor: 'rgba(255,255,255,0.8)' }}>
              <ZoomIn />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="줌 아웃">
            <IconButton size="small" onClick={zoomOut} sx={{ bgcolor: 'rgba(255,255,255,0.8)' }}>
              <ZoomOut />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="카메라 리셋">
            <IconButton size="small" onClick={resetCamera} sx={{ bgcolor: 'rgba(255,255,255,0.8)' }}>
              <CenterFocusStrong />
            </IconButton>
          </Tooltip>
          
          <Tooltip title={isGridVisible ? "그리드 숨기기" : "그리드 보이기"}>
            <IconButton size="small" onClick={toggleGrid} sx={{ bgcolor: 'rgba(255,255,255,0.8)' }}>
              {isGridVisible ? <GridOff /> : <GridOn />}
            </IconButton>
          </Tooltip>
          
          <Tooltip title="새로고침">
            <IconButton size="small" onClick={refreshScene} sx={{ bgcolor: 'rgba(255,255,255,0.8)' }}>
              <Refresh />
            </IconButton>
          </Tooltip>
          
          <Tooltip title={isFullscreen ? "전체화면 해제" : "전체화면"}>
            <IconButton size="small" onClick={toggleFullscreen} sx={{ bgcolor: 'rgba(255,255,255,0.8)' }}>
              {isFullscreen ? <FullscreenExit /> : <Fullscreen />}
            </IconButton>
          </Tooltip>
        </Box>
      )}

      {/* 정보 패널 */}
      {bimData && (
        <Box
          position="absolute"
          bottom={10}
          left={10}
          bgcolor="rgba(255,255,255,0.9)"
          p={2}
          borderRadius={1}
          maxWidth={300}
          zIndex={5}
        >
          <Typography variant="h6" gutterBottom>
            {bimData.buildingType} 건물
          </Typography>
          <Typography variant="body2" color="text.secondary">
            총 면적: {bimData.totalArea.value}{bimData.totalArea.unit}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            방 개수: {bimData.rooms.length}개
          </Typography>
          {bimData.style && (
            <Typography variant="body2" color="text.secondary">
              스타일: {bimData.style.architectural}
            </Typography>
          )}
        </Box>
      )}
    </Paper>
  );
};

export default BIMViewer;