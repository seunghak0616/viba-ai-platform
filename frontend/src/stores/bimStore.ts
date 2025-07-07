import { create } from 'zustand';
import { devtools, subscribeWithSelector } from 'zustand/middleware';
import { BimModel, Project, ViewerState, ViewerSettings } from '@types/index';

interface BimStore {
  // Current data
  currentProject: Project | null;
  currentBimModel: BimModel | null;
  bimModels: BimModel[];
  projects: Project[];
  
  // Viewer state
  viewer: ViewerState;
  
  // UI state
  isLoading: boolean;
  error: string | null;
  selectedTab: 'models' | 'projects' | 'history' | 'settings';
  sidebarOpen: boolean;
  propertiesPanelOpen: boolean;
  
  // Actions - Projects
  setCurrentProject: (project: Project | null) => void;
  addProject: (project: Project) => void;
  updateProject: (projectId: string, updates: Partial<Project>) => void;
  removeProject: (projectId: string) => void;
  setProjects: (projects: Project[]) => void;
  
  // Actions - BIM Models
  setCurrentBimModel: (model: BimModel | null) => void;
  addBimModel: (model: BimModel) => void;
  updateBimModel: (modelId: string, updates: Partial<BimModel>) => void;
  removeBimModel: (modelId: string) => void;
  setBimModels: (models: BimModel[]) => void;
  
  // Actions - Viewer
  updateViewerSettings: (settings: Partial<ViewerSettings>) => void;
  setViewerLoading: (loading: boolean) => void;
  setViewerError: (error: string | null) => void;
  selectObjects: (objectIds: string[]) => void;
  highlightObjects: (objectIds: string[]) => void;
  resetViewer: () => void;
  
  // Actions - UI
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setSelectedTab: (tab: 'models' | 'projects' | 'history' | 'settings') => void;
  setSidebarOpen: (open: boolean) => void;
  setPropertiesPanelOpen: (open: boolean) => void;
  clearError: () => void;
  reset: () => void;
}

// 기본 뷰어 설정
const defaultViewerSettings: ViewerSettings = {
  showGrid: true,
  showAxes: true,
  wireframe: false,
  shadows: true,
  lightIntensity: 1.0,
  cameraPosition: { x: 10, y: 10, z: 10 },
  cameraTarget: { x: 0, y: 0, z: 0 },
};

// 초기 상태
const initialState = {
  // Current data
  currentProject: null,
  currentBimModel: null,
  bimModels: [],
  projects: [],
  
  // Viewer state
  viewer: {
    isLoading: false,
    error: undefined,
    settings: defaultViewerSettings,
    selectedObjects: [],
    highlightedObjects: [],
  } as ViewerState,
  
  // UI state
  isLoading: false,
  error: null,
  selectedTab: 'models' as const,
  sidebarOpen: true,
  propertiesPanelOpen: false,
};

export const useBimStore = create<BimStore>()(
  devtools(
    subscribeWithSelector((set, get) => ({
      ...initialState,

      // Project Actions
      setCurrentProject: (project) => {
        set(
          { currentProject: project },
          false,
          'bim/set-current-project'
        );
        
        // 프로젝트 변경시 현재 BIM 모델 초기화
        if (project?.id !== get().currentProject?.id) {
          set(
            { currentBimModel: null },
            false,
            'bim/clear-current-model'
          );
        }
      },

      addProject: (project) => {
        set(
          (state) => ({
            projects: [...state.projects, project].sort((a, b) => 
              new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
            ),
          }),
          false,
          'bim/add-project'
        );
      },

      updateProject: (projectId, updates) => {
        set(
          (state) => ({
            projects: state.projects.map(project =>
              project.id === projectId 
                ? { ...project, ...updates, updatedAt: new Date().toISOString() }
                : project
            ),
            currentProject: state.currentProject?.id === projectId
              ? { ...state.currentProject, ...updates, updatedAt: new Date().toISOString() }
              : state.currentProject,
          }),
          false,
          'bim/update-project'
        );
      },

      removeProject: (projectId) => {
        set(
          (state) => ({
            projects: state.projects.filter(project => project.id !== projectId),
            currentProject: state.currentProject?.id === projectId ? null : state.currentProject,
            bimModels: state.bimModels.filter(model => model.projectId !== projectId),
            currentBimModel: state.currentBimModel?.projectId === projectId ? null : state.currentBimModel,
          }),
          false,
          'bim/remove-project'
        );
      },

      setProjects: (projects) => {
        set(
          { 
            projects: projects.sort((a, b) => 
              new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
            ) 
          },
          false,
          'bim/set-projects'
        );
      },

      // BIM Model Actions
      setCurrentBimModel: (model) => {
        set(
          { currentBimModel: model },
          false,
          'bim/set-current-model'
        );
        
        // 모델 변경시 뷰어 상태 초기화
        if (model?.id !== get().currentBimModel?.id) {
          set(
            (state) => ({
              viewer: {
                ...state.viewer,
                selectedObjects: [],
                highlightedObjects: [],
                error: undefined,
              }
            }),
            false,
            'bim/reset-viewer-selection'
          );
        }
      },

      addBimModel: (model) => {
        set(
          (state) => ({
            bimModels: [...state.bimModels, model].sort((a, b) => 
              new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
            ),
          }),
          false,
          'bim/add-model'
        );
      },

      updateBimModel: (modelId, updates) => {
        set(
          (state) => ({
            bimModels: state.bimModels.map(model =>
              model.id === modelId 
                ? { ...model, ...updates, updatedAt: new Date().toISOString() }
                : model
            ),
            currentBimModel: state.currentBimModel?.id === modelId
              ? { ...state.currentBimModel, ...updates, updatedAt: new Date().toISOString() }
              : state.currentBimModel,
          }),
          false,
          'bim/update-model'
        );
      },

      removeBimModel: (modelId) => {
        set(
          (state) => ({
            bimModels: state.bimModels.filter(model => model.id !== modelId),
            currentBimModel: state.currentBimModel?.id === modelId ? null : state.currentBimModel,
          }),
          false,
          'bim/remove-model'
        );
      },

      setBimModels: (models) => {
        set(
          { 
            bimModels: models.sort((a, b) => 
              new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
            ) 
          },
          false,
          'bim/set-models'
        );
      },

      // Viewer Actions
      updateViewerSettings: (settings) => {
        set(
          (state) => ({
            viewer: {
              ...state.viewer,
              settings: { ...state.viewer.settings, ...settings }
            }
          }),
          false,
          'bim/update-viewer-settings'
        );
      },

      setViewerLoading: (loading) => {
        set(
          (state) => ({
            viewer: { ...state.viewer, isLoading: loading }
          }),
          false,
          'bim/set-viewer-loading'
        );
      },

      setViewerError: (error) => {
        set(
          (state) => ({
            viewer: { ...state.viewer, error: error || undefined }
          }),
          false,
          'bim/set-viewer-error'
        );
      },

      selectObjects: (objectIds) => {
        set(
          (state) => ({
            viewer: { ...state.viewer, selectedObjects: [...objectIds] }
          }),
          false,
          'bim/select-objects'
        );
      },

      highlightObjects: (objectIds) => {
        set(
          (state) => ({
            viewer: { ...state.viewer, highlightedObjects: [...objectIds] }
          }),
          false,
          'bim/highlight-objects'
        );
      },

      resetViewer: () => {
        set(
          (state) => ({
            viewer: {
              isLoading: false,
              error: undefined,
              settings: defaultViewerSettings,
              selectedObjects: [],
              highlightedObjects: [],
            }
          }),
          false,
          'bim/reset-viewer'
        );
      },

      // UI Actions
      setLoading: (loading) => {
        set(
          { isLoading: loading },
          false,
          'bim/set-loading'
        );
      },

      setError: (error) => {
        set(
          { error },
          false,
          'bim/set-error'
        );
      },

      setSelectedTab: (tab) => {
        set(
          { selectedTab: tab },
          false,
          'bim/set-selected-tab'
        );
      },

      setSidebarOpen: (open) => {
        set(
          { sidebarOpen: open },
          false,
          'bim/set-sidebar-open'
        );
      },

      setPropertiesPanelOpen: (open) => {
        set(
          { propertiesPanelOpen: open },
          false,
          'bim/set-properties-panel-open'
        );
      },

      clearError: () => {
        set(
          { error: null },
          false,
          'bim/clear-error'
        );
      },

      reset: () => {
        set(
          initialState,
          false,
          'bim/reset'
        );
      },
    })),
    {
      name: 'bim-store',
    }
  )
);

// 선택자 함수들 (성능 최적화)
export const useCurrentProject = () => useBimStore((state) => state.currentProject);
export const useCurrentBimModel = () => useBimStore((state) => state.currentBimModel);
export const useBimModels = () => useBimStore((state) => state.bimModels);
export const useProjects = () => useBimStore((state) => state.projects);
export const useViewerState = () => useBimStore((state) => state.viewer);
export const useViewerSettings = () => useBimStore((state) => state.viewer.settings);
export const useBimLoading = () => useBimStore((state) => state.isLoading);
export const useBimError = () => useBimStore((state) => state.error);
export const useSelectedTab = () => useBimStore((state) => state.selectedTab);
export const useSidebarOpen = () => useBimStore((state) => state.sidebarOpen);
export const usePropertiesPanelOpen = () => useBimStore((state) => state.propertiesPanelOpen);

// 액션 선택자
export const useBimActions = () => useBimStore((state) => ({
  setCurrentProject: state.setCurrentProject,
  setCurrentBimModel: state.setCurrentBimModel,
  addProject: state.addProject,
  updateProject: state.updateProject,
  removeProject: state.removeProject,
  addBimModel: state.addBimModel,
  updateBimModel: state.updateBimModel,
  removeBimModel: state.removeBimModel,
  setLoading: state.setLoading,
  setError: state.setError,
  clearError: state.clearError,
}));

export const useViewerActions = () => useBimStore((state) => ({
  updateViewerSettings: state.updateViewerSettings,
  setViewerLoading: state.setViewerLoading,
  setViewerError: state.setViewerError,
  selectObjects: state.selectObjects,
  highlightObjects: state.highlightObjects,
  resetViewer: state.resetViewer,
}));

export const useUIActions = () => useBimStore((state) => ({
  setSelectedTab: state.setSelectedTab,
  setSidebarOpen: state.setSidebarOpen,
  setPropertiesPanelOpen: state.setPropertiesPanelOpen,
}));

// 계산된 선택자들
export const useCurrentProjectBimModels = () => {
  return useBimStore((state) => 
    state.currentProject 
      ? state.bimModels.filter(model => model.projectId === state.currentProject!.id)
      : []
  );
};

export const useHasUnsavedChanges = () => {
  return useBimStore((state) => {
    // 현재 모델의 변경사항이 있는지 체크하는 로직
    // 실제 구현에서는 더 복잡한 로직이 필요할 수 있음
    return false;
  });
};

// 구독 헬퍼 함수들
export const subscribeToCurrentProject = (callback: (project: Project | null) => void) => {
  return useBimStore.subscribe(
    (state) => state.currentProject,
    callback
  );
};

export const subscribeToCurrentBimModel = (callback: (model: BimModel | null) => void) => {
  return useBimStore.subscribe(
    (state) => state.currentBimModel,
    callback
  );
};

export const subscribeToViewerSettings = (callback: (settings: ViewerSettings) => void) => {
  return useBimStore.subscribe(
    (state) => state.viewer.settings,
    callback
  );
};

// 개발 환경에서만 사용되는 디버그 함수
if (import.meta.env.DEV) {
  // @ts-ignore
  window.bimStore = useBimStore;
  console.log('BIM store attached to window.bimStore for debugging');
}