/**
 * BIM 3D 뷰어 컴포넌트
 * Babylon.js를 사용한 안전하고 최적화된 3D 렌더링
 */
import React, { useRef, useEffect, useState, useCallback, useMemo } from 'react';
import { Box, Alert, CircularProgress, Typography, Paper } from '@mui/material';
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
  ActionManager,
  ExecuteCodeAction,
  PickingInfo,
  Mesh,
  TransformNode,
  SceneLoader,
  AssetContainer,
  Observable,
  Tools,
  GroundMesh,
  GridMaterial
} from '@babylonjs/core';
import '@babylonjs/loaders/glTF';
import '@babylonjs/materials/grid';

import { BimModel, ViewerSettings } from '@types/index';
import { useViewerState, useViewerActions } from '@stores/bimStore';
import BimViewerControls from './BimViewerControls';
import BimObjectInspector from './BimObjectInspector';

interface BimViewerProps {
  bimModel: BimModel | null;
  width?: string | number;
  height?: string | number;
  showControls?: boolean;
  showInspector?: boolean;
  onObjectSelect?: (objectId: string | null) => void;
  onObjectHover?: (objectId: string | null) => void;
  onError?: (error: Error) => void;
}

interface BimObject {
  id: string;
  name: string;
  type: string;
  mesh: Mesh;
  properties: Record<string, any>;
  metadata: Record<string, any>;
}

/**
 * BIM 3D 뷰어 메인 컴포넌트
 */
const BimViewer: React.FC<BimViewerProps> = ({
  bimModel,
  width = '100%',
  height = '600px',
  showControls = true,
  showInspector = true,
  onObjectSelect,
  onObjectHover,
  onError
}) => {
  // Refs
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const engineRef = useRef<Engine | null>(null);
  const sceneRef = useRef<Scene | null>(null);
  const cameraRef = useRef<FreeCamera | null>(null);
  
  // State
  const [isInitialized, setIsInitialized] = useState(false);
  const [initError, setInitError] = useState<string | null>(null);
  const [selectedObject, setSelectedObject] = useState<BimObject | null>(null);
  const [hoveredObject, setHoveredObject] = useState<BimObject | null>(null);
  const [bimObjects, setBimObjects] = useState<Map<string, BimObject>>(new Map());
  
  // Store
  const viewerState = useViewerState();
  const { setViewerLoading, setViewerError, updateViewerSettings } = useViewerActions();

  // 메모화된 뷰어 설정
  const settings = useMemo(() => viewerState.settings, [viewerState.settings]);

  /**
   * Babylon.js 엔진 및 씬 초기화
   */
  const initializeBabylon = useCallback(async () => {
    if (!canvasRef.current) {
      const error = new Error('Canvas 요소를 찾을 수 없습니다.');
      setInitError(error.message);
      onError?.(error);
      return;
    }

    try {
      setViewerLoading(true);
      setInitError(null);

      // 엔진 생성
      const engine = new Engine(canvasRef.current, true, {
        adaptToDeviceRatio: true,
        antialias: true,
        powerPreference: 'high-performance',
        preserveDrawingBuffer: true
      });

      // 씬 생성
      const scene = new Scene(engine);
      scene.useRightHandedSystem = true; // BIM 표준 좌표계

      // 카메라 설정
      const camera = new FreeCamera('camera', new Vector3(10, 10, 10), scene);
      camera.setTarget(Vector3.Zero());
      camera.attachControls(canvasRef.current, true);
      
      // 카메라 제약 설정
      camera.lowerBetaLimit = 0.1;
      camera.upperBetaLimit = Math.PI / 2;
      camera.lowerRadiusLimit = 2;
      camera.upperRadiusLimit = 100;

      // 조명 설정
      const hemisphericLight = new HemisphericLight('hemiLight', new Vector3(0, 1, 0), scene);
      hemisphericLight.intensity = 0.7;

      const directionalLight = new DirectionalLight('dirLight', new Vector3(-1, -1, -1), scene);
      directionalLight.intensity = 0.5;
      directionalLight.position = new Vector3(20, 20, 20);

      // 그리드 생성
      await createGrid(scene);

      // 축 표시
      if (settings.showAxes) {
        createAxes(scene);
      }

      // 씬 최적화
      optimizeScene(scene);

      // 이벤트 핸들러 설정
      setupEventHandlers(scene);

      // 렌더링 루프 시작
      engine.runRenderLoop(() => {
        if (scene && scene.activeCamera) {
          scene.render();
        }
      });

      // 창 크기 변경 처리
      const handleResize = () => engine.resize();
      window.addEventListener('resize', handleResize);

      // Refs에 저장
      engineRef.current = engine;
      sceneRef.current = scene;
      cameraRef.current = camera;

      setIsInitialized(true);
      setViewerLoading(false);

      console.log('Babylon.js viewer initialized successfully');

      // 클린업 함수 반환
      return () => {
        window.removeEventListener('resize', handleResize);
        engine.dispose();
      };

    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.';
      console.error('Failed to initialize Babylon.js viewer:', error);
      setInitError(errorMsg);
      setViewerLoading(false);
      onError?.(error instanceof Error ? error : new Error(errorMsg));
    }
  }, [settings.showAxes, setViewerLoading, onError]);

  /**
   * 그리드 생성
   */
  const createGrid = async (scene: Scene): Promise<void> => {
    if (!settings.showGrid) return;

    try {
      const ground = MeshBuilder.CreateGround('ground', { width: 100, height: 100 }, scene);
      
      // GridMaterial 사용
      const { GridMaterial } = await import('@babylonjs/materials/grid');
      const gridMaterial = new GridMaterial('gridMaterial', scene);
      gridMaterial.gridRatio = 1;
      gridMaterial.majorUnitFrequency = 10;
      gridMaterial.minorUnitVisibility = 0.3;
      gridMaterial.opacity = 0.8;
      
      ground.material = gridMaterial;
      ground.receiveShadows = settings.shadows;
    } catch (error) {
      console.error('Failed to create grid:', error);
    }
  };

  /**
   * 좌표축 생성
   */
  const createAxes = (scene: Scene): void => {
    const axisLength = 5;
    
    // X축 (빨간색)
    const xAxis = MeshBuilder.CreateLines('xAxis', {
      points: [Vector3.Zero(), new Vector3(axisLength, 0, 0)]
    }, scene);
    xAxis.color = Color3.Red();

    // Y축 (초록색)
    const yAxis = MeshBuilder.CreateLines('yAxis', {
      points: [Vector3.Zero(), new Vector3(0, axisLength, 0)]
    }, scene);
    yAxis.color = Color3.Green();

    // Z축 (파란색)
    const zAxis = MeshBuilder.CreateLines('zAxis', {
      points: [Vector3.Zero(), new Vector3(0, 0, axisLength)]
    }, scene);
    zAxis.color = Color3.Blue();
  };

  /**
   * 씬 최적화
   */
  const optimizeScene = (scene: Scene): void => {
    // 절두체 컬링 활성화
    scene.frustumPlanes = [];
    
    // 오클루전 컬링 활성화
    scene.occlusionQueries = scene.getEngine().getCaps().occlusionQueries;
    
    // LOD (Level of Detail) 활성화
    scene.useGeometryIdsMap = true;
    scene.useMaterialMeshMap = true;
    
    // 성능 모니터링
    scene.onBeforeRenderObservable.add(() => {
      // 프레임 시간 모니터링
      const deltaTime = scene.getEngine().getDeltaTime();
      if (deltaTime > 33) { // 30fps 이하
        console.warn(`Low framerate detected: ${(1000 / deltaTime).toFixed(1)}fps`);
      }
    });
  };

  /**
   * 이벤트 핸들러 설정
   */
  const setupEventHandlers = (scene: Scene): void => {
    // 액션 매니저 생성
    scene.actionManager = new ActionManager(scene);

    // 마우스 클릭 이벤트
    scene.actionManager.registerAction(
      new ExecuteCodeAction(ActionManager.OnPickTrigger, (event) => {
        handleObjectClick(event.meshUnderPointer);
      })
    );

    // 마우스 호버 이벤트
    scene.onPointerObservable.add((pointerInfo) => {
      if (pointerInfo.pickInfo?.hit && pointerInfo.pickInfo.pickedMesh) {
        handleObjectHover(pointerInfo.pickInfo.pickedMesh);
      } else {
        handleObjectHover(null);
      }
    });
  };

  /**
   * 객체 클릭 처리
   */
  const handleObjectClick = useCallback((mesh: Mesh | null) => {
    if (!mesh || mesh.name === 'ground') {
      setSelectedObject(null);
      onObjectSelect?.(null);
      return;
    }

    const bimObject = bimObjects.get(mesh.id);
    if (bimObject) {
      setSelectedObject(bimObject);
      onObjectSelect?.(bimObject.id);
      
      // 시각적 피드백
      highlightMesh(mesh, Color3.Yellow());
    }
  }, [bimObjects, onObjectSelect]);

  /**
   * 객체 호버 처리
   */
  const handleObjectHover = useCallback((mesh: Mesh | null) => {
    // 이전 호버 해제
    if (hoveredObject) {
      removeHighlight(hoveredObject.mesh);
    }

    if (!mesh || mesh.name === 'ground') {
      setHoveredObject(null);
      onObjectHover?.(null);
      return;
    }

    const bimObject = bimObjects.get(mesh.id);
    if (bimObject && bimObject !== selectedObject) {
      setHoveredObject(bimObject);
      onObjectHover?.(bimObject.id);
      
      // 시각적 피드백
      highlightMesh(mesh, Color3.Blue());
    }
  }, [bimObjects, hoveredObject, selectedObject, onObjectHover]);

  /**
   * 메쉬 하이라이트
   */
  const highlightMesh = (mesh: Mesh, color: Color3): void => {
    if (mesh.material instanceof StandardMaterial) {
      mesh.material.emissiveColor = color;
      mesh.material.emissiveIntensity = 0.3;
    }
  };

  /**
   * 하이라이트 제거
   */
  const removeHighlight = (mesh: Mesh): void => {
    if (mesh.material instanceof StandardMaterial) {
      mesh.material.emissiveColor = Color3.Black();
      mesh.material.emissiveIntensity = 0;
    }
  };

  /**
   * BIM 모델 로드
   */
  const loadBimModel = useCallback(async (model: BimModel) => {
    if (!sceneRef.current) {
      console.error('Scene is not initialized');
      return;
    }

    try {
      setViewerLoading(true);
      setViewerError(null);

      // 기존 모델 제거
      clearScene();

      // 모델 데이터에서 3D 객체 생성
      await createBimObjects(model, sceneRef.current);

      console.log(`BIM model loaded: ${model.name}`);
      
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'BIM 모델 로드에 실패했습니다.';
      console.error('Failed to load BIM model:', error);
      setViewerError(errorMsg);
      onError?.(error instanceof Error ? error : new Error(errorMsg));
    } finally {
      setViewerLoading(false);
    }
  }, [setViewerLoading, setViewerError, onError]);

  /**
   * 씬 정리
   */
  const clearScene = (): void => {
    if (!sceneRef.current) return;

    // BIM 객체들 제거
    bimObjects.forEach((bimObject) => {
      bimObject.mesh.dispose();
    });
    
    setBimObjects(new Map());
    setSelectedObject(null);
    setHoveredObject(null);
  };

  /**
   * BIM 객체들 생성
   */
  const createBimObjects = async (model: BimModel, scene: Scene): Promise<void> => {
    const newBimObjects = new Map<string, BimObject>();

    // 모델의 processedParams에서 방 정보 추출
    const rooms = model.processedParams?.rooms || [];
    
    let positionX = 0;
    const roomSpacing = 6;

    for (const room of rooms) {
      const roomId = `room_${room.type}_${Math.random().toString(36).substr(2, 9)}`;
      
      // 방 크기 계산 (기본값 설정)
      const width = room.area ? Math.sqrt(room.area) : 4;
      const depth = room.area ? room.area / width : 4;
      const height = 2.8; // 기본 천장 높이

      // 바닥 생성
      const floor = MeshBuilder.CreateBox(`${roomId}_floor`, {
        width,
        depth,
        height: 0.1
      }, scene);
      
      floor.position = new Vector3(positionX, 0, 0);

      // 벽 생성
      const walls = createWalls(roomId, width, depth, height, scene);
      walls.forEach(wall => {
        wall.position.x += positionX;
      });

      // 재료 설정
      const material = new StandardMaterial(`${roomId}_material`, scene);
      material.diffuseColor = getRoomColor(room.type);
      material.specularColor = Color3.White();
      
      floor.material = material;
      walls.forEach(wall => {
        wall.material = material;
      });

      // BIM 객체로 등록
      const bimObject: BimObject = {
        id: roomId,
        name: room.type,
        type: 'ROOM',
        mesh: floor,
        properties: {
          area: room.area || 0,
          width,
          depth,
          height,
          orientation: room.orientation
        },
        metadata: {
          modelId: model.id,
          roomData: room
        }
      };

      newBimObjects.set(roomId, bimObject);
      
      // 액션 매니저 설정
      floor.actionManager = new ActionManager(scene);
      
      positionX += width + roomSpacing;
    }

    setBimObjects(newBimObjects);
  };

  /**
   * 벽 생성
   */
  const createWalls = (roomId: string, width: number, depth: number, height: number, scene: Scene): Mesh[] => {
    const wallThickness = 0.2;
    const walls: Mesh[] = [];

    // 앞벽
    const frontWall = MeshBuilder.CreateBox(`${roomId}_wall_front`, {
      width,
      height,
      depth: wallThickness
    }, scene);
    frontWall.position = new Vector3(0, height / 2, depth / 2);
    walls.push(frontWall);

    // 뒷벽
    const backWall = MeshBuilder.CreateBox(`${roomId}_wall_back`, {
      width,
      height,
      depth: wallThickness
    }, scene);
    backWall.position = new Vector3(0, height / 2, -depth / 2);
    walls.push(backWall);

    // 왼쪽벽
    const leftWall = MeshBuilder.CreateBox(`${roomId}_wall_left`, {
      width: wallThickness,
      height,
      depth: depth - wallThickness * 2
    }, scene);
    leftWall.position = new Vector3(-width / 2, height / 2, 0);
    walls.push(leftWall);

    // 오른쪽벽
    const rightWall = MeshBuilder.CreateBox(`${roomId}_wall_right`, {
      width: wallThickness,
      height,
      depth: depth - wallThickness * 2
    }, scene);
    rightWall.position = new Vector3(width / 2, height / 2, 0);
    walls.push(rightWall);

    return walls;
  };

  /**
   * 방 타입별 색상
   */
  const getRoomColor = (roomType: string): Color3 => {
    const colorMap: Record<string, Color3> = {
      '거실': Color3.FromHexString('#FFE5B4'),
      '침실': Color3.FromHexString('#E5F3FF'),
      '주방': Color3.FromHexString('#E5FFE5'),
      '화장실': Color3.FromHexString('#F0F0F0'),
      '베란다': Color3.FromHexString('#FFF5E5'),
      '서재': Color3.FromHexString('#F5E5FF')
    };

    return colorMap[roomType] || Color3.Gray();
  };

  /**
   * 뷰어 설정 업데이트 처리
   */
  useEffect(() => {
    if (!sceneRef.current) return;

    const scene = sceneRef.current;

    // 그리드 표시/숨김
    const ground = scene.getMeshByName('ground');
    if (ground) {
      ground.setEnabled(settings.showGrid);
    }

    // 축 표시/숨김
    const axes = ['xAxis', 'yAxis', 'zAxis'];
    axes.forEach(axisName => {
      const axis = scene.getMeshByName(axisName);
      if (axis) {
        axis.setEnabled(settings.showAxes);
      }
    });

    // 와이어프레임 모드
    scene.meshes.forEach(mesh => {
      if (mesh.material instanceof StandardMaterial) {
        mesh.material.wireframe = settings.wireframe;
      }
    });

    // 그림자 설정
    scene.meshes.forEach(mesh => {
      mesh.receiveShadows = settings.shadows;
    });

    // 조명 강도
    const hemiLight = scene.getLightByName('hemiLight');
    if (hemiLight) {
      hemiLight.intensity = settings.lightIntensity * 0.7;
    }

    const dirLight = scene.getLightByName('dirLight');
    if (dirLight) {
      dirLight.intensity = settings.lightIntensity * 0.5;
    }

  }, [settings]);

  /**
   * BIM 모델 변경 처리
   */
  useEffect(() => {
    if (bimModel && isInitialized) {
      loadBimModel(bimModel);
    }
  }, [bimModel, isInitialized, loadBimModel]);

  /**
   * 초기화
   */
  useEffect(() => {
    const cleanup = initializeBabylon();
    
    return () => {
      cleanup?.then(cleanupFn => cleanupFn?.());
    };
  }, []); // 빈 의존성 배열로 한 번만 실행

  /**
   * 컴포넌트 언마운트 시 정리
   */
  useEffect(() => {
    return () => {
      if (engineRef.current) {
        engineRef.current.dispose();
      }
    };
  }, []);

  // 로딩 상태
  if (viewerState.isLoading) {
    return (
      <Paper 
        sx={{ 
          width, 
          height, 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          flexDirection: 'column',
          gap: 2
        }}
      >
        <CircularProgress size={48} />
        <Typography variant="body2" color="text.secondary">
          3D 모델을 불러오는 중...
        </Typography>
      </Paper>
    );
  }

  // 에러 상태
  if (initError || viewerState.error) {
    return (
      <Paper sx={{ width, height, p: 2 }}>
        <Alert severity="error">
          <Typography variant="h6" gutterBottom>
            3D 뷰어 오류
          </Typography>
          <Typography variant="body2">
            {initError || viewerState.error}
          </Typography>
        </Alert>
      </Paper>
    );
  }

  return (
    <Box sx={{ width, height, position: 'relative' }}>
      {/* 메인 캔버스 */}
      <canvas
        ref={canvasRef}
        style={{
          width: '100%',
          height: '100%',
          display: 'block',
          outline: 'none'
        }}
        onContextMenu={(e) => e.preventDefault()}
      />

      {/* 컨트롤 패널 */}
      {showControls && (
        <Box sx={{ position: 'absolute', top: 16, left: 16 }}>
          <BimViewerControls />
        </Box>
      )}

      {/* 객체 인스펙터 */}
      {showInspector && selectedObject && (
        <Box sx={{ position: 'absolute', top: 16, right: 16 }}>
          <BimObjectInspector 
            bimObject={selectedObject}
            onClose={() => setSelectedObject(null)}
          />
        </Box>
      )}
    </Box>
  );
};

export default BimViewer;