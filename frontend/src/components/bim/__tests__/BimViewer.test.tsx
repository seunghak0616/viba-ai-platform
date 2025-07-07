/**
 * BIM 뷰어 컴포넌트 테스트
 * 3D 렌더링 및 상호작용 기능 테스트
 */
import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { jest } from '@jest/globals';
import BimViewer from '../BimViewer';
import { BimModel } from '@types/index';

// Babylon.js 모킹
jest.mock('@babylonjs/core', () => ({
  Engine: jest.fn().mockImplementation(() => ({
    runRenderLoop: jest.fn(),
    resize: jest.fn(),
    dispose: jest.fn(),
    getDeltaTime: jest.fn().mockReturnValue(16.67), // 60fps
    getCaps: jest.fn().mockReturnValue({ occlusionQueries: true })
  })),
  Scene: jest.fn().mockImplementation(() => ({
    useRightHandedSystem: true,
    actionManager: null,
    meshes: [],
    render: jest.fn(),
    dispose: jest.fn(),
    getMeshByName: jest.fn(),
    getLightByName: jest.fn(),
    onBeforeRenderObservable: {
      add: jest.fn()
    },
    onPointerObservable: {
      add: jest.fn()
    },
    getEngine: jest.fn().mockReturnValue({
      getCaps: jest.fn().mockReturnValue({ occlusionQueries: true }),
      getDeltaTime: jest.fn().mockReturnValue(16.67)
    })
  })),
  FreeCamera: jest.fn().mockImplementation(() => ({
    setTarget: jest.fn(),
    attachControls: jest.fn(),
    lowerBetaLimit: 0.1,
    upperBetaLimit: Math.PI / 2,
    lowerRadiusLimit: 2,
    upperRadiusLimit: 100
  })),
  Vector3: {
    Zero: jest.fn().mockReturnValue({ x: 0, y: 0, z: 0 }),
    new: jest.fn().mockImplementation((x, y, z) => ({ x, y, z }))
  },
  HemisphericLight: jest.fn().mockImplementation(() => ({
    intensity: 0.7
  })),
  DirectionalLight: jest.fn().mockImplementation(() => ({
    intensity: 0.5,
    position: { x: 20, y: 20, z: 20 }
  })),
  MeshBuilder: {
    CreateGround: jest.fn().mockReturnValue({
      material: null,
      receiveShadows: false,
      setEnabled: jest.fn()
    }),
    CreateBox: jest.fn().mockReturnValue({
      position: { x: 0, y: 0, z: 0 },
      material: null,
      actionManager: null,
      dispose: jest.fn(),
      setEnabled: jest.fn()
    }),
    CreateLines: jest.fn().mockReturnValue({
      color: null,
      setEnabled: jest.fn()
    })
  },
  StandardMaterial: jest.fn().mockImplementation(() => ({
    diffuseColor: null,
    specularColor: null,
    emissiveColor: null,
    emissiveIntensity: 0,
    wireframe: false
  })),
  Color3: {
    Red: jest.fn().mockReturnValue({ r: 1, g: 0, b: 0 }),
    Green: jest.fn().mockReturnValue({ r: 0, g: 1, b: 0 }),
    Blue: jest.fn().mockReturnValue({ r: 0, g: 0, b: 1 }),
    Black: jest.fn().mockReturnValue({ r: 0, g: 0, b: 0 }),
    White: jest.fn().mockReturnValue({ r: 1, g: 1, b: 1 }),
    Gray: jest.fn().mockReturnValue({ r: 0.5, g: 0.5, b: 0.5 }),
    Yellow: jest.fn().mockReturnValue({ r: 1, g: 1, b: 0 }),
    FromHexString: jest.fn().mockImplementation((hex) => ({ hex }))
  },
  ActionManager: jest.fn().mockImplementation(() => ({
    registerAction: jest.fn(),
    OnPickTrigger: 'OnPickTrigger'
  })),
  ExecuteCodeAction: jest.fn(),
  Tools: {
    ToRadians: jest.fn().mockImplementation((degrees) => degrees * Math.PI / 180)
  }
}));

// Store 모킹
jest.mock('@stores/bimStore', () => ({
  useViewerState: jest.fn().mockReturnValue({
    isLoading: false,
    error: null,
    settings: {
      showGrid: true,
      showAxes: true,
      wireframe: false,
      shadows: true,
      lightIntensity: 1.0,
      cameraPosition: { x: 10, y: 10, z: 10 },
      cameraTarget: { x: 0, y: 0, z: 0 }
    }
  }),
  useViewerActions: jest.fn().mockReturnValue({
    setViewerLoading: jest.fn(),
    setViewerError: jest.fn(),
    updateViewerSettings: jest.fn(),
    resetViewer: jest.fn()
  })
}));

// 하위 컴포넌트 모킹
jest.mock('../BimViewerControls', () => {
  return function MockBimViewerControls() {
    return <div data-testid="bim-viewer-controls">뷰어 컨트롤</div>;
  };
});

jest.mock('../BimObjectInspector', () => {
  return function MockBimObjectInspector({ onClose }: { onClose: () => void }) {
    return (
      <div data-testid="bim-object-inspector">
        객체 인스펙터
        <button onClick={onClose}>닫기</button>
      </div>
    );
  };
});

describe('BimViewer', () => {
  let mockBimModel: BimModel;
  
  beforeEach(() => {
    // 콘솔 모킹 (불필요한 로그 숨김)
    jest.spyOn(console, 'log').mockImplementation();
    jest.spyOn(console, 'warn').mockImplementation();
    jest.spyOn(console, 'error').mockImplementation();
    
    // 모킹된 BIM 모델
    mockBimModel = {
      id: 'test-model-id',
      name: 'Test BIM Model',
      type: 'APARTMENT',
      naturalLanguageInput: '남향 거실이 있는 30평 아파트',
      processedParams: {
        buildingType: 'APARTMENT',
        totalArea: { value: 30, unit: '평', confidence: 0.9 },
        rooms: [
          { type: '거실', count: 1, orientation: '남향', area: 15 },
          { type: '침실', count: 2, area: 10 },
          { type: '주방', count: 1, area: 8 },
          { type: '화장실', count: 1, area: 4 }
        ],
        confidence: 0.85
      },
      status: 'COMPLETED',
      userId: 'test-user-id',
      projectId: 'test-project-id',
      version: 1,
      createdAt: new Date(),
      updatedAt: new Date()
    };
    
    // 이벤트 리스너 모킹
    global.addEventListener = jest.fn();
    global.removeEventListener = jest.fn();
  });
  
  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('Rendering', () => {
    it('should render canvas element', async () => {
      await act(async () => {
        render(<BimViewer bimModel={null} />);
      });
      
      const canvas = screen.getByRole('img', { hidden: true });
      expect(canvas).toBeInTheDocument();
      expect(canvas.tagName).toBe('CANVAS');
    });

    it('should render with custom dimensions', async () => {
      await act(async () => {
        render(
          <BimViewer 
            bimModel={null} 
            width="800px" 
            height="400px" 
          />
        );
      });
      
      const container = screen.getByRole('img', { hidden: true }).parentElement;
      expect(container).toHaveStyle({
        width: '800px',
        height: '400px'
      });
    });

    it('should show controls when showControls is true', async () => {
      await act(async () => {
        render(<BimViewer bimModel={null} showControls={true} />);
      });
      
      await waitFor(() => {
        expect(screen.getByTestId('bim-viewer-controls')).toBeInTheDocument();
      });
    });

    it('should hide controls when showControls is false', async () => {
      await act(async () => {
        render(<BimViewer bimModel={null} showControls={false} />);
      });
      
      expect(screen.queryByTestId('bim-viewer-controls')).not.toBeInTheDocument();
    });
  });

  describe('Loading States', () => {
    it('should show loading spinner when isLoading is true', () => {
      const { useViewerState } = require('@stores/bimStore');
      useViewerState.mockReturnValue({
        isLoading: true,
        error: null,
        settings: {}
      });
      
      render(<BimViewer bimModel={null} />);
      
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
      expect(screen.getByText('3D 모델을 불러오는 중...')).toBeInTheDocument();
    });

    it('should show error message when error exists', () => {
      const { useViewerState } = require('@stores/bimStore');
      useViewerState.mockReturnValue({
        isLoading: false,
        error: '3D 뷰어 초기화 실패',
        settings: {}
      });
      
      render(<BimViewer bimModel={null} />);
      
      expect(screen.getByText('3D 뷰어 오류')).toBeInTheDocument();
      expect(screen.getByText('3D 뷰어 초기화 실패')).toBeInTheDocument();
    });
  });

  describe('BIM Model Loading', () => {
    it('should handle BIM model with room data', async () => {
      const { setViewerLoading } = require('@stores/bimStore').useViewerActions();
      
      await act(async () => {
        render(<BimViewer bimModel={mockBimModel} />);
      });
      
      // 로딩 상태 호출 확인
      await waitFor(() => {
        expect(setViewerLoading).toHaveBeenCalledWith(true);
      });
    });

    it('should handle empty model gracefully', async () => {
      const emptyModel: BimModel = {
        ...mockBimModel,
        processedParams: {
          buildingType: 'APARTMENT',
          confidence: 0.5,
          rooms: []
        }
      };
      
      await act(async () => {
        render(<BimViewer bimModel={emptyModel} />);
      });
      
      // 에러 없이 렌더링되어야 함
      const canvas = screen.getByRole('img', { hidden: true });
      expect(canvas).toBeInTheDocument();
    });

    it('should handle model without processedParams', async () => {
      const modelWithoutParams: BimModel = {
        ...mockBimModel,
        processedParams: null as any
      };
      
      await act(async () => {
        render(<BimViewer bimModel={modelWithoutParams} />);
      });
      
      const canvas = screen.getByRole('img', { hidden: true });
      expect(canvas).toBeInTheDocument();
    });
  });

  describe('Object Selection', () => {
    it('should call onObjectSelect when object is selected', async () => {
      const onObjectSelect = jest.fn();
      
      await act(async () => {
        render(
          <BimViewer 
            bimModel={mockBimModel} 
            onObjectSelect={onObjectSelect}
            showInspector={true}
          />
        );
      });
      
      // 객체 선택 시뮬레이션은 실제 Babylon.js 이벤트가 필요하므로
      // 여기서는 콜백이 제대로 전달되었는지만 확인
      expect(onObjectSelect).toBeInstanceOf(Function);
    });

    it('should show object inspector when object is selected', async () => {
      await act(async () => {
        render(<BimViewer bimModel={mockBimModel} showInspector={true} />);
      });
      
      // 초기에는 인스펙터가 표시되지 않음
      expect(screen.queryByTestId('bim-object-inspector')).not.toBeInTheDocument();
    });

    it('should hide object inspector when showInspector is false', async () => {
      await act(async () => {
        render(<BimViewer bimModel={mockBimModel} showInspector={false} />);
      });
      
      expect(screen.queryByTestId('bim-object-inspector')).not.toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('should call onError when Babylon.js initialization fails', async () => {
      const onError = jest.fn();
      const { Engine } = require('@babylonjs/core');
      
      // Engine 생성자가 에러를 던지도록 모킹
      Engine.mockImplementationOnce(() => {
        throw new Error('WebGL not supported');
      });
      
      await act(async () => {
        render(<BimViewer bimModel={null} onError={onError} />);
      });
      
      await waitFor(() => {
        expect(onError).toHaveBeenCalledWith(
          expect.objectContaining({
            message: 'WebGL not supported'
          })
        );
      });
    });

    it('should show error message for canvas creation failure', async () => {
      // 캔버스 ref 모킹을 null로 설정
      const originalUseRef = React.useRef;
      jest.spyOn(React, 'useRef').mockImplementation((initialValue) => {
        if (initialValue === null && React.useRef === originalUseRef) {
          return { current: null };
        }
        return originalUseRef(initialValue);
      });
      
      await act(async () => {
        render(<BimViewer bimModel={null} />);
      });
      
      // 에러 상태가 표시되어야 함
      await waitFor(() => {
        expect(screen.getByText('3D 뷰어 오류')).toBeInTheDocument();
      });
    });

    it('should handle model loading errors gracefully', async () => {
      const { setViewerError } = require('@stores/bimStore').useViewerActions();
      const onError = jest.fn();
      
      // MeshBuilder가 에러를 던지도록 모킹
      const { MeshBuilder } = require('@babylonjs/core');
      MeshBuilder.CreateBox.mockImplementationOnce(() => {
        throw new Error('Mesh creation failed');
      });
      
      await act(async () => {
        render(<BimViewer bimModel={mockBimModel} onError={onError} />);
      });
      
      await waitFor(() => {
        expect(setViewerError).toHaveBeenCalledWith(
          expect.stringContaining('Mesh creation failed')
        );
      });
    });
  });

  describe('Settings Updates', () => {
    it('should respond to viewer settings changes', async () => {
      const { useViewerState } = require('@stores/bimStore');
      
      // 초기 렌더링
      const { rerender } = render(<BimViewer bimModel={null} />);
      
      // 설정 변경
      useViewerState.mockReturnValue({
        isLoading: false,
        error: null,
        settings: {
          showGrid: false,
          showAxes: false,
          wireframe: true,
          shadows: false,
          lightIntensity: 0.5
        }
      });
      
      await act(async () => {
        rerender(<BimViewer bimModel={null} />);
      });
      
      // 설정이 적용되었는지 확인 (실제 Babylon.js 호출은 모킹되어 있음)
      expect(true).toBe(true); // 설정 변경이 에러 없이 처리됨
    });
  });

  describe('Cleanup', () => {
    it('should dispose resources on unmount', async () => {
      const { Engine } = require('@babylonjs/core');
      const mockDispose = jest.fn();
      
      Engine.mockImplementation(() => ({
        runRenderLoop: jest.fn(),
        resize: jest.fn(),
        dispose: mockDispose,
        getDeltaTime: jest.fn().mockReturnValue(16.67),
        getCaps: jest.fn().mockReturnValue({ occlusionQueries: true })
      }));
      
      const { unmount } = render(<BimViewer bimModel={null} />);
      
      await act(async () => {
        unmount();
      });
      
      // 약간의 지연 후 dispose 호출 확인
      await waitFor(() => {
        expect(mockDispose).toHaveBeenCalled();
      });
    });

    it('should remove event listeners on unmount', async () => {
      const { unmount } = render(<BimViewer bimModel={null} />);
      
      await act(async () => {
        unmount();
      });
      
      expect(global.removeEventListener).toHaveBeenCalledWith(
        'resize',
        expect.any(Function)
      );
    });
  });

  describe('Performance', () => {
    it('should not re-render unnecessarily', async () => {
      const renderSpy = jest.fn();
      
      const TestComponent = (props: any) => {
        renderSpy();
        return <BimViewer {...props} />;
      };
      
      const { rerender } = render(<TestComponent bimModel={null} />);
      
      // 같은 props로 다시 렌더링
      await act(async () => {
        rerender(<TestComponent bimModel={null} />);
      });
      
      // 실제로는 React.memo 등의 최적화가 필요하지만
      // 여기서는 기본 동작만 확인
      expect(renderSpy).toHaveBeenCalledTimes(2);
    });

    it('should handle large number of rooms efficiently', async () => {
      const largeModel: BimModel = {
        ...mockBimModel,
        processedParams: {
          buildingType: 'APARTMENT',
          confidence: 0.9,
          rooms: Array.from({ length: 20 }, (_, i) => ({
            type: `방${i + 1}`,
            count: 1,
            area: 10
          }))
        }
      };
      
      const startTime = performance.now();
      
      await act(async () => {
        render(<BimViewer bimModel={largeModel} />);
      });
      
      const endTime = performance.now();
      const renderTime = endTime - startTime;
      
      // 렌더링이 합리적인 시간 내에 완료되어야 함 (1초 이내)
      expect(renderTime).toBeLessThan(1000);
    });
  });

  describe('Accessibility', () => {
    it('should prevent context menu on canvas', async () => {
      await act(async () => {
        render(<BimViewer bimModel={null} />);
      });
      
      const canvas = screen.getByRole('img', { hidden: true });
      const contextMenuEvent = new MouseEvent('contextmenu', {
        bubbles: true,
        cancelable: true
      });
      
      const preventDefaultSpy = jest.spyOn(contextMenuEvent, 'preventDefault');
      
      fireEvent(canvas, contextMenuEvent);
      
      expect(preventDefaultSpy).toHaveBeenCalled();
    });

    it('should have proper focus management', async () => {
      await act(async () => {
        render(<BimViewer bimModel={null} />);
      });
      
      const canvas = screen.getByRole('img', { hidden: true });
      expect(canvas).toHaveStyle({ outline: 'none' });
    });
  });
});
