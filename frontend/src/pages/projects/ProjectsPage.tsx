import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Avatar,
  AvatarGroup,
  LinearProgress,
  IconButton,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  Fab,
  InputAdornment,
  Paper,
  Tabs,
  Tab,
  Pagination,
  Stack,
  Divider,
  Alert,
  Tooltip,
  Switch
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  FilterList as FilterListIcon,
  GridView as GridViewIcon,
  List as ListIcon,
  MoreVert as MoreVertIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Share as ShareIcon,
  ThreeDRotation as ThreeDRotationIcon,
  Folder as FolderIcon,
  CalendarToday as CalendarIcon,
  Person as PersonIcon,
  TrendingUp as TrendingUpIcon,
  Visibility as VisibilityIcon,
  Archive as ArchiveIcon,
  Close as CloseIcon,
  Tune as TuneIcon,
  ModelTraining as ModelTrainingIcon,
  AutoAwesome as AutoAwesomeIcon
} from '@mui/icons-material';
import { useAuthStore } from '../../stores/authStore';
import { BIMData } from '../../services/bimToThreeService';

// 타입 정의
interface ProjectMember {
  id: string;
  name: string;
  role: string;
  avatar?: string;
}

interface ArchitecturalStandard {
  id: string;
  name: string;
  description: string;
  requirements: string[];
  compliance: 'required' | 'recommended' | 'optional';
}

interface BuildingCode {
  id: string;
  name: string;
  category: 'fire' | 'structure' | 'accessibility' | 'energy' | 'zoning';
  description: string;
  requirements: string[];
  applicableTypes: string[];
}

interface Project {
  id: string;
  name: string;
  description: string;
  type: 'residential' | 'commercial' | 'office' | 'industrial' | 'public';
  status: 'active' | 'completed' | 'paused' | 'archived';
  progress: number;
  createdAt: string;
  updatedAt: string;
  dueDate?: string;
  budget?: number;
  area?: number;
  location?: string;
  members: ProjectMember[];
  tags: string[];
  thumbnail?: string;
  isStarred?: boolean;
  // 건축 전문 정보
  buildingHeight?: number;
  floorCount?: number;
  structureType?: 'reinforced_concrete' | 'steel' | 'timber' | 'masonry' | 'hybrid';
  buildingUse?: string;
  zoneClassification?: string;
  fireRating?: string;
  energyRating?: string;
  accessibilityCompliance?: boolean;
  environmentalFeatures?: string[];
  constructionStandards?: string[];
  materialSpecs?: string[];
  sustainabilityRating?: 'none' | 'green' | 'leed' | 'breeam' | 'korea_green';
}

interface ProjectStats {
  total: number;
  active: number;
  completed: number;
  paused: number;
  archived: number;
}

type ViewMode = 'grid' | 'list';
type SortBy = 'name' | 'created' | 'updated' | 'progress' | 'dueDate';
type FilterType = 'all' | 'residential' | 'commercial' | 'office' | 'industrial' | 'public';
type StatusFilter = 'all' | 'active' | 'completed' | 'paused' | 'archived';

const ProjectsPage: React.FC = () => {
  const { user } = useAuthStore();
  
  // 상태 관리
  const [projects, setProjects] = useState<Project[]>([]);
  const [filteredProjects, setFilteredProjects] = useState<Project[]>([]);
  const [stats, setStats] = useState<ProjectStats>({
    total: 0,
    active: 0,
    completed: 0,
    paused: 0,
    archived: 0
  });
  const [loading, setLoading] = useState(false);
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<SortBy>('updated');
  const [filterType, setFilterType] = useState<FilterType>('all');
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(12);
  
  // 모달 및 메뉴 상태
  const [createProjectOpen, setCreateProjectOpen] = useState(false);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  // 새 프로젝트 폼 상태
  const [newProject, setNewProject] = useState({
    name: '',
    description: '',
    type: 'residential' as const,
    location: '',
    area: '',
    budget: '',
    dueDate: '',
    tags: '',
    // 건축 전문 필드
    buildingHeight: '',
    floorCount: '',
    structureType: 'reinforced_concrete' as const,
    buildingUse: '',
    zoneClassification: '',
    fireRating: '',
    energyRating: '',
    accessibilityCompliance: true,
    environmentalFeatures: '',
    constructionStandards: '',
    materialSpecs: '',
    sustainabilityRating: 'none' as const,
    // 디자인 이론 필드
    designStyle: '',
    designPrinciples: '',
    spaceTypes: '',
    colorScheme: '',
    lightingConcept: ''
  });

  // 템플릿 선택 상태
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [autoFillEnabled, setAutoFillEnabled] = useState(true);

  // 프리셋 데이터 구조
  const fieldPresets = {
    location: [
      { value: '서울특별시 강남구', label: '서울 강남구' },
      { value: '서울특별시 서초구', label: '서울 서초구' },
      { value: '경기도 성남시 분당구', label: '성남 분당구' },
      { value: '인천광역시 연수구 송도동', label: '인천 송도' },
      { value: '부산광역시 해운대구', label: '부산 해운대구' },
      { value: '대전광역시 유성구', label: '대전 유성구' },
      { value: '제주특별자치도 서귀포시', label: '제주 서귀포시' }
    ],
    buildingUse: {
      residential: ['공동주택', '단독주택', '연립주택', '다세대주택', '기숙사'],
      commercial: ['판매시설', '숙박시설', '위락시설', '관광휴게시설', '전시시설'],
      office: ['업무시설', '오피스텔', '복합업무시설', '연구시설'],
      industrial: ['공장시설', '창고시설', '위험물저장처리시설', '자동차관련시설'],
      public: ['교육시설', '의료시설', '문화집회시설', '종교시설', '운동시설']
    },
    zoneClassification: [
      { value: '상업지역', label: '상업지역 (용적률 400-1500%)' },
      { value: '일반주거지역', label: '일반주거지역 (용적률 150-300%)' },
      { value: '준주거지역', label: '준주거지역 (용적률 200-500%)' },
      { value: '준공업지역', label: '준공업지역 (용적률 200-400%)' },
      { value: '자연녹지지역', label: '자연녹지지역 (용적률 50-100%)' },
      { value: '관광휴양지역', label: '관광휴양지역' },
      { value: '개발제한구역', label: '개발제한구역 (그린벨트)' }
    ],
    fireRating: [
      { value: '내화구조 3시간', label: '내화구조 3시간 (초고층)' },
      { value: '내화구조 2시간', label: '내화구조 2시간 (고층)' },
      { value: '내화구조 1시간', label: '내화구조 1시간 (중층)' },
      { value: '준내화구조 1시간', label: '준내화구조 1시간' },
      { value: '내화구조 미적용', label: '내화구조 미적용 (저층)' }
    ],
    energyRating: [
      { value: '1+++급', label: '1+++급 (최우수)' },
      { value: '1++급', label: '1++급 (우수)' },
      { value: '1+급', label: '1+급 (양호)' },
      { value: '1급', label: '1급 (일반)' },
      { value: '2급', label: '2급' },
      { value: '3급', label: '3급' },
      { value: '등급외', label: '등급 외' }
    ],
    environmentalFeatures: [
      'LED 조명시스템', '태양광 발전설비', '지열냉난방시스템', '빗물재활용시설',
      '절수형 위생기구', '고효율 HVAC 시스템', '자연채광 시스템', '옥상녹화',
      '벽면녹화', '재활용 자재 사용', '자동조명제어시스템', '스마트 미터링',
      '폐열회수 환기장치', '차열 유리창호', '단열성능 강화'
    ],
    constructionStandards: [
      'KS F 4009 (건축용 외벽 마감재료)', '건축물 에너지절약설계기준',
      '내진설계기준', '건축물 화재안전기준', '장애인 편의시설 설치기준',
      '친환경 건축물 인증기준', '건축물 방음설계기준', '건축구조기준',
      '공동주택 품질인증기준', '스마트홈 건설기준', '관광숙박시설 기준',
      '교육시설 설계기준', '의료시설 설계기준'
    ],
    materialSpecs: [
      '고강도 콘크리트 (C35 이상)', '친환경 단열재', '고효율 유리커튼월',
      '재활용 철근', '저탄소 시멘트', '친환경 마감재', '방음자재',
      '내화성능 자재', '항균 마감재', '조습기능 자재', '저독성 접착제',
      '재활용 골재', '고성능 방수재', '내구성 향상 자재'
    ],
    designStyles: [
      '모던 (Modern)', '컨템포러리 (Contemporary)', '미니멀 (Minimal)',
      '인더스트리얼 (Industrial)', '스칸디나비안 (Scandinavian)', '한국 전통',
      '바우하우스 (Bauhaus)', '포스트모던 (Post-Modern)', '데콘스트럭티비즘',
      '하이테크 (High-Tech)', '브루탈리즘 (Brutalism)', '네오클래식 (Neo-Classic)',
      '아르누보 (Art Nouveau)', '아르데코 (Art Deco)', '지속가능 디자인'
    ],
    designPrinciples: [
      '비례와 균형', '리듬과 반복', '강조와 대비', '조화와 통일',
      '기능주의', '형태는 기능을 따른다', '황금비율 적용', '모듈러 시스템',
      '빛과 그림자', '색채 조화', '질감 대비', '공간의 흐름',
      '시각적 연속성', '환경과의 조화', '사용자 중심 설계'
    ],
    spaceTypes: [
      '개방형 공간', '폐쇄형 공간', '반개방형 공간', '가변형 공간',
      '아트리움', '보이드 공간', '더블 하이트', '메자닌',
      '테라스', '발코니', '로비', '코어', '복도', '계단실'
    ]
  };

  // 건축 템플릿 프리셋
  const buildingTemplates = {
    residential: {
      apartment: {
        name: '일반 공동주택',
        floorCount: '15',
        structureType: 'reinforced_concrete',
        buildingUse: '공동주택',
        fireRating: '내화구조 1시간',
        energyRating: '1급',
        accessibilityCompliance: true,
        environmentalFeatures: 'LED 조명시스템, 절수형 위생기구, 자연채광 시스템',
        constructionStandards: 'KS F 4009, 공동주택 품질인증기준, 내진설계기준',
        materialSpecs: '고강도 콘크리트, 친환경 단열재, 고성능 방수재'
      },
      villa: {
        name: '단독주택',
        floorCount: '3',
        structureType: 'reinforced_concrete',
        buildingUse: '단독주택',
        fireRating: '준내화구조 1시간',
        energyRating: '1+급',
        accessibilityCompliance: false,
        environmentalFeatures: 'LED 조명시스템, 태양광 발전설비, 자연채광 시스템',
        constructionStandards: 'KS F 4009, 건축물 에너지절약설계기준',
        materialSpecs: '고강도 콘크리트, 친환경 단열재, 친환경 마감재'
      }
    },
    commercial: {
      shopping: {
        name: '쇼핑몰',
        floorCount: '5',
        structureType: 'steel',
        buildingUse: '판매시설',
        fireRating: '내화구조 2시간',
        energyRating: '1급',
        accessibilityCompliance: true,
        environmentalFeatures: 'LED 조명시스템, 고효율 HVAC 시스템, 스마트 미터링',
        constructionStandards: 'KS F 4009, 건축물 화재안전기준, 장애인 편의시설 설치기준',
        materialSpecs: '고강도 콘크리트, 고효율 유리커튼월, 내화성능 자재'
      },
      hotel: {
        name: '호텔',
        floorCount: '20',
        structureType: 'reinforced_concrete',
        buildingUse: '숙박시설',
        fireRating: '내화구조 2시간',
        energyRating: '1++급',
        accessibilityCompliance: true,
        environmentalFeatures: 'LED 조명시스템, 지열냉난방시스템, 스마트 미터링, 절수형 위생기구',
        constructionStandards: 'KS F 4009, 관광숙박시설 기준, 건축물 화재안전기준',
        materialSpecs: '고강도 콘크리트, 친환경 단열재, 방음자재, 항균 마감재'
      }
    },
    office: {
      general: {
        name: '일반 업무시설',
        floorCount: '25',
        structureType: 'reinforced_concrete',
        buildingUse: '업무시설',
        fireRating: '내화구조 2시간',
        energyRating: '1++급',
        accessibilityCompliance: true,
        environmentalFeatures: 'LED 조명시스템, 고효율 HVAC 시스템, 자동조명제어시스템, 스마트 미터링',
        constructionStandards: 'KS F 4009, 건축물 에너지절약설계기준, 장애인 편의시설 설치기준',
        materialSpecs: '고강도 콘크리트, 고효율 유리커튼월, 친환경 단열재'
      }
    },
    public: {
      school: {
        name: '교육시설',
        floorCount: '4',
        structureType: 'reinforced_concrete',
        buildingUse: '교육시설',
        fireRating: '내화구조 2시간',
        energyRating: '1+급',
        accessibilityCompliance: true,
        environmentalFeatures: 'LED 조명시스템, 자연채광 시스템, 자동조명제어시스템, 차열 유리창호',
        constructionStandards: 'KS F 4009, 교육시설 설계기준, 장애인 편의시설 설치기준',
        materialSpecs: '고강도 콘크리트, 친환경 단열재, 저독성 접착제, 조습기능 자재'
      },
      hospital: {
        name: '의료시설',
        floorCount: '8',
        structureType: 'reinforced_concrete',
        buildingUse: '의료시설',
        fireRating: '내화구조 2시간',
        energyRating: '1++급',
        accessibilityCompliance: true,
        environmentalFeatures: 'LED 조명시스템, 고효율 HVAC 시스템, 항균 시스템, 스마트 미터링',
        constructionStandards: 'KS F 4009, 의료시설 설계기준, 장애인 편의시설 설치기준',
        materialSpecs: '고강도 콘크리트, 항균 마감재, 친환경 단열재, 방음자재'
      }
    }
  };

  // 자동 규정 검토 시스템
  const autoComplianceChecker = {
    getRequiredStandards: (projectType: string, area?: number, floorCount?: number) => {
      const standards = [];
      
      // 기본 적용 기준
      standards.push('KS F 4009');
      
      // 면적별 기준
      if (area && area >= 3000) {
        standards.push('건축물 에너지절약설계기준');
      }
      
      // 층수별 기준
      if (floorCount && floorCount >= 5) {
        standards.push('건축물 화재안전기준');
      }
      
      // 용도별 기준
      if (['office', 'commercial', 'public'].includes(projectType)) {
        standards.push('장애인 편의시설 설치기준');
      }
      
      // 프로젝트 유형별 특화 기준
      const typeSpecificStandards = {
        residential: ['공동주택 품질인증기준'],
        commercial: ['관광숙박시설 기준'],
        office: ['업무시설 설계기준'],
        public: ['교육시설 설계기준', '의료시설 설계기준'],
        industrial: ['산업시설 안전기준']
      };
      
      if (typeSpecificStandards[projectType as keyof typeof typeSpecificStandards]) {
        standards.push(...typeSpecificStandards[projectType as keyof typeof typeSpecificStandards]);
      }
      
      return standards;
    },
    
    getRecommendedFireRating: (floorCount?: number, area?: number) => {
      if (!floorCount) return '내화구조 미적용';
      if (floorCount >= 30) return '내화구조 3시간';
      if (floorCount >= 11) return '내화구조 2시간';
      if (floorCount >= 5) return '내화구조 1시간';
      return '준내화구조 1시간';
    },
    
    getRecommendedEnergyRating: (area?: number, projectType?: string) => {
      if (!area) return '1급';
      if (area >= 10000) return '1+++급';
      if (area >= 5000) return '1++급';
      if (area >= 3000) return '1+급';
      if (projectType === 'public') return '1++급'; // 공공건물은 높은 등급 권장
      return '1급';
    },
    
    getRecommendedEnvironmentalFeatures: (projectType: string, area?: number) => {
      const baseFeatures = ['LED 조명시스템'];
      
      if (area && area >= 3000) {
        baseFeatures.push('고효율 HVAC 시스템', '스마트 미터링');
      }
      
      const typeFeatures = {
        residential: ['절수형 위생기구', '자연채광 시스템'],
        commercial: ['자동조명제어시스템', '빗물재활용시설'],
        office: ['자동조명제어시스템', '차열 유리창호'],
        public: ['자연채광 시스템', '항균 시스템'],
        industrial: ['폐열회수 환기장치', '환경모니터링 시스템']
      };
      
      if (typeFeatures[projectType as keyof typeof typeFeatures]) {
        baseFeatures.push(...typeFeatures[projectType as keyof typeof typeFeatures]);
      }
      
      return baseFeatures;
    }
  };

  // 건축 지식 데이터
  const architecturalStandards: ArchitecturalStandard[] = [
    {
      id: 'ks-f-4009',
      name: 'KS F 4009 건축용 외벽 마감재료',
      description: '외벽 마감재료의 품질기준 및 시험방법',
      requirements: ['내화성능', '내구성', '방수성', '단열성능'],
      compliance: 'required'
    },
    {
      id: 'green-building',
      name: '친환경 건축물 인증기준',
      description: '에너지 효율성 및 환경 친화적 설계 기준',
      requirements: ['에너지 효율 등급', '신재생에너지 사용', '친환경 자재'],
      compliance: 'recommended'
    }
  ];

  const buildingCodes: BuildingCode[] = [
    {
      id: 'fire-safety-code',
      name: '건축물 화재안전기준',
      category: 'fire',
      description: '건축물의 화재 예방 및 안전 기준',
      requirements: ['스프링클러 설치', '방화구획', '피난시설'],
      applicableTypes: ['office', 'commercial', 'residential']
    },
    {
      id: 'accessibility-code',
      name: '장애인 편의시설 설치기준',
      category: 'accessibility',
      description: '장애인의 접근성을 보장하는 시설 기준',
      requirements: ['경사로', '승강기', '점자블록', '장애인 화장실'],
      applicableTypes: ['office', 'commercial', 'public']
    },
    {
      id: 'energy-efficiency',
      name: '건축물 에너지 효율등급 인증기준',
      category: 'energy',
      description: '건축물의 에너지 성능 평가 및 인증 기준',
      requirements: ['단열성능', 'HVAC 효율', '조명 효율', '신재생에너지'],
      applicableTypes: ['residential', 'office', 'commercial']
    }
  ];

  // 샘플 데이터 초기화
  useEffect(() => {
    const sampleProjects: Project[] = [
      {
        id: '1',
        name: '강남 오피스 빌딩',
        description: '25층 규모의 현대적 오피스 건물 설계 프로젝트',
        type: 'office',
        status: 'active',
        progress: 75,
        createdAt: '2024-01-15',
        updatedAt: '2024-07-05',
        dueDate: '2024-12-31',
        budget: 15000000000,
        area: 12000,
        location: '서울시 강남구',
        members: [
          { id: '1', name: '김건축', role: '프로젝트 매니저', avatar: '' },
          { id: '2', name: '이설계', role: '건축사', avatar: '' },
          { id: '3', name: '박구조', role: '구조기사', avatar: '' }
        ],
        tags: ['고층건물', '상업용', '친환경'],
        isStarred: true,
        // 건축 전문 정보
        buildingHeight: 98.5,
        floorCount: 25,
        structureType: 'reinforced_concrete',
        buildingUse: '업무시설',
        zoneClassification: '상업지역',
        fireRating: '내화구조 2시간',
        energyRating: '1++급',
        accessibilityCompliance: true,
        environmentalFeatures: ['LED 조명', '태양광 패널', '빗물 재활용', '고효율 HVAC'],
        constructionStandards: ['KS F 4009', '내진설계기준', '친환경 건축물 인증'],
        materialSpecs: ['고강도 콘크리트', '친환경 단열재', '고효율 유리커튼월'],
        sustainabilityRating: 'leed'
      },
      {
        id: '2',
        name: '판교 주상복합',
        description: '주거와 상업시설이 결합된 복합건물',
        type: 'residential',
        status: 'active',
        progress: 45,
        createdAt: '2024-02-20',
        updatedAt: '2024-07-03',
        dueDate: '2025-06-30',
        budget: 8000000000,
        area: 8500,
        location: '경기도 성남시',
        members: [
          { id: '1', name: '김건축', role: '프로젝트 매니저' },
          { id: '4', name: '최인테리어', role: '인테리어 디자이너' }
        ],
        tags: ['주상복합', '스마트홈', '커뮤니티'],
        isStarred: false,
        // 건축 전문 정보
        buildingHeight: 45.2,
        floorCount: 15,
        structureType: 'reinforced_concrete',
        buildingUse: '공동주택',
        zoneClassification: '일반주거지역',
        fireRating: '내화구조 1시간',
        energyRating: '1급',
        accessibilityCompliance: true,
        environmentalFeatures: ['지열냉난방', '절수설비', '자연채광', '옥상녹화'],
        constructionStandards: ['주택건설기준', '공동주택 품질인증', '스마트홈 기준'],
        materialSpecs: ['친환경 콘크리트', '고성능 단열재', '복층유리'],
        sustainabilityRating: 'korea_green'
      },
      {
        id: '3',
        name: '서울역 상업시설',
        description: '대형 쇼핑몰 및 업무시설',
        type: 'commercial',
        status: 'completed',
        progress: 100,
        createdAt: '2023-08-10',
        updatedAt: '2024-03-15',
        dueDate: '2024-03-31',
        budget: 25000000000,
        area: 18000,
        location: '서울시 용산구',
        members: [
          { id: '1', name: '김건축', role: '프로젝트 매니저' },
          { id: '2', name: '이설계', role: '건축사' },
          { id: '5', name: '정시공', role: '시공관리자' }
        ],
        tags: ['쇼핑몰', '복합시설', '교통허브'],
        isStarred: true
      },
      {
        id: '4',
        name: '인천공항 터미널',
        description: '국제공항 터미널 확장 프로젝트',
        type: 'public',
        status: 'paused',
        progress: 30,
        createdAt: '2024-03-01',
        updatedAt: '2024-06-20',
        dueDate: '2025-12-31',
        budget: 50000000000,
        area: 35000,
        location: '인천시 중구',
        members: [
          { id: '1', name: '김건축', role: '총괄 책임자' },
          { id: '6', name: '한항공', role: '항공 전문가' },
          { id: '7', name: '공공간', role: '공공건축가' }
        ],
        tags: ['공항', '대규모', '국제시설'],
        isStarred: false
      },
      {
        id: '5',
        name: '부산 산업단지',
        description: '첨단 제조업 단지 마스터플랜',
        type: 'industrial',
        status: 'active',
        progress: 20,
        createdAt: '2024-05-10',
        updatedAt: '2024-07-01',
        dueDate: '2026-03-31',
        budget: 30000000000,
        area: 50000,
        location: '부산시 강서구',
        members: [
          { id: '8', name: '산업설계', role: '산업건축가' },
          { id: '9', name: '환경공학', role: '환경전문가' }
        ],
        tags: ['산업단지', '스마트팩토리', '친환경'],
        isStarred: false
      },
      {
        id: '6',
        name: '제주 리조트',
        description: '친환경 휴양 리조트 개발',
        type: 'commercial',
        status: 'active',
        progress: 60,
        createdAt: '2024-01-25',
        updatedAt: '2024-07-04',
        dueDate: '2024-11-30',
        budget: 12000000000,
        area: 15000,
        location: '제주시 애월읍',
        members: [
          { id: '10', name: '리조트건축', role: '리조트 전문가' },
          { id: '11', name: '조경설계', role: '조경 디자이너' }
        ],
        tags: ['리조트', '관광', '자연친화'],
        isStarred: true
      }
    ];

    setProjects(sampleProjects);
    setFilteredProjects(sampleProjects);
    
    // 통계 계산
    const newStats = sampleProjects.reduce((acc, project) => {
      acc.total++;
      acc[project.status]++;
      return acc;
    }, { total: 0, active: 0, completed: 0, paused: 0, archived: 0 });
    
    setStats(newStats);
  }, []);

  // 필터링 및 검색
  useEffect(() => {
    let filtered = projects;

    // 검색 필터
    if (searchQuery) {
      filtered = filtered.filter(project =>
        project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        project.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        project.location?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        project.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      );
    }

    // 타입 필터
    if (filterType !== 'all') {
      filtered = filtered.filter(project => project.type === filterType);
    }

    // 상태 필터
    if (statusFilter !== 'all') {
      filtered = filtered.filter(project => project.status === statusFilter);
    }

    // 정렬
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'created':
          return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
        case 'updated':
          return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
        case 'progress':
          return b.progress - a.progress;
        case 'dueDate':
          if (!a.dueDate && !b.dueDate) return 0;
          if (!a.dueDate) return 1;
          if (!b.dueDate) return -1;
          return new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime();
        default:
          return 0;
      }
    });

    setFilteredProjects(filtered);
    setCurrentPage(1);
  }, [projects, searchQuery, filterType, statusFilter, sortBy]);

  // 프로젝트 타입, 면적, 층수 변경 시 자동 규정 검토
  useEffect(() => {
    if (newProject.type || newProject.area || newProject.floorCount) {
      autoFillFields(newProject.type, newProject.area, newProject.floorCount);
    }
  }, [newProject.type, newProject.area, newProject.floorCount, autoFillEnabled]);

  // 템플릿 선택 시 적용
  useEffect(() => {
    if (selectedTemplate) {
      applyTemplate(selectedTemplate);
    }
  }, [selectedTemplate]);

  // 페이지네이션 계산
  const totalPages = Math.ceil(filteredProjects.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedProjects = filteredProjects.slice(startIndex, startIndex + itemsPerPage);

  // 유틸리티 함수들
  const getTypeColor = (type: string) => {
    const colors = {
      residential: '#4CAF50',
      commercial: '#2196F3',
      office: '#FF9800',
      industrial: '#9E9E9E',
      public: '#E91E63'
    };
    return colors[type as keyof typeof colors] || '#9E9E9E';
  };

  const getTypeName = (type: string) => {
    const names = {
      residential: '주거',
      commercial: '상업',
      office: '사무',
      industrial: '산업',
      public: '공공'
    };
    return names[type as keyof typeof names] || type;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'primary';
      case 'completed': return 'success';
      case 'paused': return 'warning';
      case 'archived': return 'default';
      default: return 'default';
    }
  };

  const getStatusName = (status: string) => {
    const names = {
      active: '진행중',
      completed: '완료',
      paused: '일시중지',
      archived: '보관됨'
    };
    return names[status as keyof typeof names] || status;
  };

  const formatBudget = (budget?: number) => {
    if (!budget) return '미정';
    if (budget >= 1000000000) {
      return `${(budget / 1000000000).toFixed(1)}억원`;
    }
    if (budget >= 100000000) {
      return `${(budget / 100000000).toFixed(1)}억원`;
    }
    return `${(budget / 10000).toFixed(0)}만원`;
  };

  const formatArea = (area?: number) => {
    if (!area) return '미정';
    if (area >= 3000) {
      return `${(area / 3000).toFixed(1)}천㎡`;
    }
    return `${area.toLocaleString()}㎡`;
  };

  const formatStructureType = (type?: string) => {
    const types = {
      reinforced_concrete: '철근콘크리트',
      steel: '철골구조',
      timber: '목구조',
      masonry: '조적구조',
      hybrid: '복합구조'
    };
    return types[type as keyof typeof types] || type;
  };

  const formatSustainabilityRating = (rating?: string) => {
    const ratings = {
      none: '없음',
      green: '녹색건축인증',
      leed: 'LEED 인증',
      breeam: 'BREEAM 인증',
      korea_green: '한국녹색건축인증'
    };
    return ratings[rating as keyof typeof ratings] || rating;
  };

  const getSustainabilityColor = (rating?: string) => {
    switch (rating) {
      case 'leed': return '#2E7D32';
      case 'breeam': return '#388E3C';
      case 'korea_green': return '#4CAF50';
      case 'green': return '#66BB6A';
      default: return '#9E9E9E';
    }
  };

  const getApplicableBuildingCodes = (projectType: string) => {
    return buildingCodes.filter(code => 
      code.applicableTypes.includes(projectType)
    );
  };

  const validateArchitecturalCompliance = (project: any) => {
    const applicableCodes = getApplicableBuildingCodes(project.type);
    const issues = [];
    
    // 화재안전 검증
    if (project.floorCount && project.floorCount > 5 && !project.fireRating) {
      issues.push('5층 이상 건물은 화재안전등급이 필요합니다.');
    }
    
    // 접근성 검증
    if (['office', 'commercial', 'public'].includes(project.type) && !project.accessibilityCompliance) {
      issues.push('해당 건물 유형은 장애인 편의시설이 필수입니다.');
    }
    
    // 에너지 효율 검증
    if (project.area && project.area > 3000 && !project.energyRating) {
      issues.push('3천㎡ 이상 건물은 에너지효율등급이 필요합니다.');
    }
    
    return issues;
  };

  // 자동 필드 채우기 함수
  const autoFillFields = (projectType: string, area?: string, floorCount?: string) => {
    if (!autoFillEnabled) return;

    const areaNum = area ? parseFloat(area) : undefined;
    const floorNum = floorCount ? parseInt(floorCount) : undefined;

    const updates: any = {};

    // 건축 기준 자동 설정
    if (!newProject.constructionStandards) {
      const requiredStandards = autoComplianceChecker.getRequiredStandards(projectType, areaNum, floorNum);
      updates.constructionStandards = requiredStandards.join(', ');
    }

    // 내화등급 자동 설정
    if (!newProject.fireRating && floorNum) {
      updates.fireRating = autoComplianceChecker.getRecommendedFireRating(floorNum, areaNum);
    }

    // 에너지등급 자동 설정
    if (!newProject.energyRating && areaNum) {
      updates.energyRating = autoComplianceChecker.getRecommendedEnergyRating(areaNum, projectType);
    }

    // 친환경 시설 자동 설정
    if (!newProject.environmentalFeatures) {
      const features = autoComplianceChecker.getRecommendedEnvironmentalFeatures(projectType, areaNum);
      updates.environmentalFeatures = features.join(', ');
    }

    // 건물 용도 자동 설정
    if (!newProject.buildingUse && fieldPresets.buildingUse[projectType as keyof typeof fieldPresets.buildingUse]) {
      const uses = fieldPresets.buildingUse[projectType as keyof typeof fieldPresets.buildingUse];
      updates.buildingUse = uses[0]; // 첫 번째 옵션을 기본값으로
    }

    // 접근성 자동 설정
    if (['office', 'commercial', 'public'].includes(projectType)) {
      updates.accessibilityCompliance = true;
    }

    if (Object.keys(updates).length > 0) {
      setNewProject(prev => ({ ...prev, ...updates }));
    }
  };

  // 템플릿 적용 함수
  const applyTemplate = (templateKey: string) => {
    const [category, template] = templateKey.split('.');
    const templateData = buildingTemplates[category as keyof typeof buildingTemplates]?.[template as any];
    
    if (templateData) {
      setNewProject(prev => ({
        ...prev,
        floorCount: templateData.floorCount,
        structureType: templateData.structureType as any,
        buildingUse: templateData.buildingUse,
        fireRating: templateData.fireRating,
        energyRating: templateData.energyRating,
        accessibilityCompliance: templateData.accessibilityCompliance,
        environmentalFeatures: templateData.environmentalFeatures,
        constructionStandards: templateData.constructionStandards,
        materialSpecs: templateData.materialSpecs
      }));
    }
  };

  // 프리셋 선택 처리 함수
  const handlePresetSelect = (fieldName: string, value: string) => {
    setNewProject(prev => ({ ...prev, [fieldName]: value }));
  };

  // 다중 선택 프리셋 처리 함수 (체크박스 형태)
  const handleMultiPresetToggle = (fieldName: string, value: string) => {
    const currentValues = newProject[fieldName as keyof typeof newProject] as string;
    const valuesArray = currentValues ? currentValues.split(', ') : [];
    
    if (valuesArray.includes(value)) {
      const newValues = valuesArray.filter(v => v !== value);
      setNewProject(prev => ({ ...prev, [fieldName]: newValues.join(', ') }));
    } else {
      const newValues = [...valuesArray, value];
      setNewProject(prev => ({ ...prev, [fieldName]: newValues.join(', ') }));
    }
  };

  // 프로젝트를 BIM 데이터로 변환
  const convertProjectToBIMData = (project: Project): BIMData => {
    // 방 정보 추출 및 생성
    const rooms = [];
    
    // 프로젝트 유형별 기본 방 구성
    const roomTemplates = {
      residential: [
        { type: '거실', area: project.area ? project.area * 0.3 : 30, count: 1 },
        { type: '주방', area: project.area ? project.area * 0.15 : 15, count: 1 },
        { type: '침실', area: project.area ? project.area * 0.25 : 20, count: 2 },
        { type: '화장실', area: project.area ? project.area * 0.1 : 8, count: 1 }
      ],
      commercial: [
        { type: '홀', area: project.area ? project.area * 0.4 : 100, count: 1 },
        { type: '사무실', area: project.area ? project.area * 0.3 : 80, count: 3 },
        { type: '회의실', area: project.area ? project.area * 0.15 : 40, count: 2 },
        { type: '휴게실', area: project.area ? project.area * 0.15 : 30, count: 1 }
      ],
      office: [
        { type: '사무실', area: project.area ? project.area * 0.5 : 120, count: 4 },
        { type: '회의실', area: project.area ? project.area * 0.2 : 50, count: 2 },
        { type: '휴게실', area: project.area ? project.area * 0.15 : 30, count: 1 },
        { type: '화장실', area: project.area ? project.area * 0.15 : 20, count: 2 }
      ],
      industrial: [
        { type: '생산공간', area: project.area ? project.area * 0.6 : 200, count: 2 },
        { type: '사무실', area: project.area ? project.area * 0.2 : 60, count: 1 },
        { type: '창고', area: project.area ? project.area * 0.2 : 80, count: 1 }
      ],
      public: [
        { type: '홀', area: project.area ? project.area * 0.4 : 150, count: 1 },
        { type: '사무실', area: project.area ? project.area * 0.3 : 100, count: 2 },
        { type: '회의실', area: project.area ? project.area * 0.15 : 50, count: 1 },
        { type: '화장실', area: project.area ? project.area * 0.15 : 30, count: 2 }
      ]
    };

    const template = roomTemplates[project.type] || roomTemplates.residential;
    template.forEach(roomTemplate => {
      for (let i = 0; i < roomTemplate.count; i++) {
        rooms.push({
          type: roomTemplate.type,
          count: 1,
          area: roomTemplate.area,
          orientation: i === 0 ? '남향' : undefined // 첫 번째 방은 남향으로 설정
        });
      }
    });

    // 건축 정보 키워드 추가
    const architecturalKeywords = [
      ...(project.tags || []),
      project.structureType ? formatStructureType(project.structureType) : '철근콘크리트',
      project.sustainabilityRating && project.sustainabilityRating !== 'none' ? 
        formatSustainabilityRating(project.sustainabilityRating) : '',
      project.fireRating || '',
      project.energyRating || '',
      ...(project.environmentalFeatures || [])
    ].filter(Boolean);

    return {
      id: project.id,
      name: project.name,
      description: `${project.description}${project.floorCount ? ` (${project.floorCount}층)` : ''}${project.buildingHeight ? ` 높이 ${project.buildingHeight}m` : ''}`,
      buildingType: project.type.toUpperCase(),
      totalArea: {
        value: project.area || 100,
        unit: '㎡'
      },
      rooms,
      style: {
        architectural: project.designStyle || '모던',
        interior: project.colorScheme || '현대적',
        keywords: architecturalKeywords
      },
      location: {
        address: project.location || '서울시',
        region: project.location?.split(' ')[0] || '서울시',
        climate: project.location?.includes('제주') ? '아열대' : 
                project.location?.includes('부산') ? '온대해양성' : '온대'
      },
      naturalLanguageInput: `${project.name}: ${project.description}. 위치: ${project.location}. 면적: ${project.area}㎡${project.floorCount ? `. 층수: ${project.floorCount}층` : ''}${project.structureType ? `. 구조: ${formatStructureType(project.structureType)}` : ''}`
    };
  };

  // 3D 뷰어에서 프로젝트 열기
  const openProjectIn3DViewer = (project: Project) => {
    try {
      const bimData = convertProjectToBIMData(project);
      
      // 로컬 스토리지에 BIM 데이터 저장
      localStorage.setItem('currentBIMProject', JSON.stringify({
        project,
        bimData,
        timestamp: new Date().toISOString()
      }));
      
      // 3D 뷰어 페이지로 이동
      window.open('/3d-viewer', '_blank');
      
      console.log('프로젝트 3D 모델 생성 완료:', {
        projectId: project.id,
        projectName: project.name,
        rooms: bimData.rooms.length,
        totalArea: bimData.totalArea.value
      });
    } catch (error) {
      console.error('3D 모델 생성 실패:', error);
      alert('3D 모델을 생성할 수 없습니다. 다시 시도해주세요.');
    }
  };

  // 이벤트 핸들러
  const handleCreateProject = () => {
    // 건축 규정 검증
    const tempProject = {
      ...newProject,
      area: newProject.area ? parseFloat(newProject.area) : undefined,
      floorCount: newProject.floorCount ? parseInt(newProject.floorCount) : undefined,
      accessibilityCompliance: newProject.accessibilityCompliance
    };
    
    const complianceIssues = validateArchitecturalCompliance(tempProject);
    
    if (complianceIssues.length > 0) {
      alert(`건축 규정 검토 필요:\n${complianceIssues.join('\n')}`);
      return;
    }

    // 실제로는 API 호출
    const project: Project = {
      id: Date.now().toString(),
      name: newProject.name,
      description: newProject.description,
      type: newProject.type,
      status: 'active',
      progress: 0,
      createdAt: new Date().toISOString().split('T')[0],
      updatedAt: new Date().toISOString().split('T')[0],
      dueDate: newProject.dueDate || undefined,
      budget: newProject.budget ? parseFloat(newProject.budget) * 100000000 : undefined,
      area: newProject.area ? parseFloat(newProject.area) : undefined,
      location: newProject.location || undefined,
      members: [{ id: user?.id || '1', name: user?.name || '사용자', role: '프로젝트 매니저' }],
      tags: newProject.tags ? newProject.tags.split(',').map(tag => tag.trim()) : [],
      isStarred: false,
      // 건축 전문 정보
      buildingHeight: newProject.buildingHeight ? parseFloat(newProject.buildingHeight) : undefined,
      floorCount: newProject.floorCount ? parseInt(newProject.floorCount) : undefined,
      structureType: newProject.structureType,
      buildingUse: newProject.buildingUse || undefined,
      zoneClassification: newProject.zoneClassification || undefined,
      fireRating: newProject.fireRating || undefined,
      energyRating: newProject.energyRating || undefined,
      accessibilityCompliance: newProject.accessibilityCompliance,
      environmentalFeatures: newProject.environmentalFeatures ? newProject.environmentalFeatures.split(',').map(f => f.trim()) : [],
      constructionStandards: newProject.constructionStandards ? newProject.constructionStandards.split(',').map(s => s.trim()) : [],
      materialSpecs: newProject.materialSpecs ? newProject.materialSpecs.split(',').map(m => m.trim()) : [],
      sustainabilityRating: newProject.sustainabilityRating,
      // 디자인 이론 정보
      designStyle: newProject.designStyle,
      designPrinciples: newProject.designPrinciples ? newProject.designPrinciples.split(',').map(p => p.trim()) : [],
      spaceTypes: newProject.spaceTypes ? newProject.spaceTypes.split(',').map(s => s.trim()) : [],
      colorScheme: newProject.colorScheme,
      lightingConcept: newProject.lightingConcept
    };

    setProjects(prev => [project, ...prev]);
    setCreateProjectOpen(false);
    
    // 프로젝트 생성 후 3D 뷰어에서 자동으로 열기
    setTimeout(() => {
      if (window.confirm(`"${project.name}" 프로젝트가 생성되었습니다.\n3D 뷰어에서 확인하시겠습니까?`)) {
        openProjectIn3DViewer(project);
      }
    }, 500);
    setNewProject({
      name: '',
      description: '',
      type: 'residential',
      location: '',
      area: '',
      budget: '',
      dueDate: '',
      tags: '',
      // 건축 전문 필드 초기화
      buildingHeight: '',
      floorCount: '',
      structureType: 'reinforced_concrete',
      buildingUse: '',
      zoneClassification: '',
      fireRating: '',
      energyRating: '',
      accessibilityCompliance: true,
      environmentalFeatures: '',
      constructionStandards: '',
      materialSpecs: '',
      sustainabilityRating: 'none',
      // 디자인 이론 필드 초기화
      designStyle: '',
      designPrinciples: '',
      spaceTypes: '',
      colorScheme: '',
      lightingConcept: ''
    });
    setSelectedTemplate('');
    setAutoFillEnabled(true);
  };

  const handleProjectAction = (action: string, project: Project) => {
    switch (action) {
      case 'edit':
        // 편집 페이지로 이동 또는 편집 모달 열기
        console.log('Edit project:', project.id);
        break;
      case 'view3d':
        // 3D 뷰어에서 프로젝트 열기
        openProjectIn3DViewer(project);
        break;
      case 'parametric':
        // 파라메트릭 BIM 에디터 열기
        window.open(`/projects/${project.id}/parametric-bim`, '_blank');
        break;
      case 'ai-optimize':
        // AI 최적화 실행
        console.log('AI optimize project:', project.id);
        // TODO: AI 최적화 API 호출
        break;
      case 'share':
        // 공유 기능
        console.log('Share project:', project.id);
        break;
      case 'archive':
        // 프로젝트 보관
        setProjects(prev => 
          prev.map(p => p.id === project.id ? { ...p, status: 'archived' } : p)
        );
        break;
      case 'delete':
        // 프로젝트 삭제 (확인 대화상자 후)
        if (window.confirm(`"${project.name}" 프로젝트를 삭제하시겠습니까?`)) {
          setProjects(prev => prev.filter(p => p.id !== project.id));
        }
        break;
    }
    setAnchorEl(null);
  };

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      {/* 헤더 섹션 */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            프로젝트 관리
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            모든 BIM 프로젝트를 한 곳에서 관리하세요
          </Typography>
        </Box>
        <Button
          variant="contained"
          size="large"
          startIcon={<AddIcon />}
          onClick={() => setCreateProjectOpen(true)}
        >
          새 프로젝트
        </Button>
      </Box>

      {/* 통계 카드 */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card elevation={2}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography color="text.secondary" gutterBottom>
                전체 프로젝트
              </Typography>
              <Typography variant="h4" component="div">
                {stats.total}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card elevation={2}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography color="text.secondary" gutterBottom>
                진행중
              </Typography>
              <Typography variant="h4" component="div" color="primary.main">
                {stats.active}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card elevation={2}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography color="text.secondary" gutterBottom>
                완료
              </Typography>
              <Typography variant="h4" component="div" color="success.main">
                {stats.completed}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card elevation={2}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography color="text.secondary" gutterBottom>
                일시중지
              </Typography>
              <Typography variant="h4" component="div" color="warning.main">
                {stats.paused}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card elevation={2}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography color="text.secondary" gutterBottom>
                보관됨
              </Typography>
              <Typography variant="h4" component="div" color="text.secondary">
                {stats.archived}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 검색 및 필터 바 */}
      <Paper elevation={1} sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              placeholder="프로젝트 검색..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={6} md={2}>
            <FormControl fullWidth>
              <InputLabel>프로젝트 유형</InputLabel>
              <Select
                value={filterType}
                label="프로젝트 유형"
                onChange={(e) => setFilterType(e.target.value as FilterType)}
              >
                <MenuItem value="all">전체</MenuItem>
                <MenuItem value="residential">주거</MenuItem>
                <MenuItem value="commercial">상업</MenuItem>
                <MenuItem value="office">사무</MenuItem>
                <MenuItem value="industrial">산업</MenuItem>
                <MenuItem value="public">공공</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={6} md={2}>
            <FormControl fullWidth>
              <InputLabel>상태</InputLabel>
              <Select
                value={statusFilter}
                label="상태"
                onChange={(e) => setStatusFilter(e.target.value as StatusFilter)}
              >
                <MenuItem value="all">전체</MenuItem>
                <MenuItem value="active">진행중</MenuItem>
                <MenuItem value="completed">완료</MenuItem>
                <MenuItem value="paused">일시중지</MenuItem>
                <MenuItem value="archived">보관됨</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={6} md={2}>
            <FormControl fullWidth>
              <InputLabel>정렬</InputLabel>
              <Select
                value={sortBy}
                label="정렬"
                onChange={(e) => setSortBy(e.target.value as SortBy)}
              >
                <MenuItem value="updated">최근 수정순</MenuItem>
                <MenuItem value="created">생성일순</MenuItem>
                <MenuItem value="name">이름순</MenuItem>
                <MenuItem value="progress">진행률순</MenuItem>
                <MenuItem value="dueDate">마감일순</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={6} md={2}>
            <Box display="flex" justifyContent="flex-end" gap={1}>
              <IconButton
                onClick={() => setViewMode('grid')}
                color={viewMode === 'grid' ? 'primary' : 'default'}
              >
                <GridViewIcon />
              </IconButton>
              <IconButton
                onClick={() => setViewMode('list')}
                color={viewMode === 'list' ? 'primary' : 'default'}
              >
                <ListIcon />
              </IconButton>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* 프로젝트 목록 */}
      {filteredProjects.length === 0 ? (
        <Paper elevation={1} sx={{ p: 4, textAlign: 'center' }}>
          <FolderIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            프로젝트가 없습니다
          </Typography>
          <Typography variant="body2" color="text.secondary" mb={3}>
            새 프로젝트를 생성하여 시작해보세요
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setCreateProjectOpen(true)}
          >
            첫 번째 프로젝트 만들기
          </Button>
        </Paper>
      ) : (
        <>
          <Grid container spacing={3}>
            {paginatedProjects.map((project) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={project.id}>
                <Card 
                  elevation={2}
                  sx={{ 
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    '&:hover': { elevation: 4 }
                  }}
                >
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                      <Box flex={1}>
                        <Typography variant="h6" component="h3" gutterBottom noWrap>
                          {project.name}
                        </Typography>
                        <Box display="flex" gap={1} mb={1}>
                          <Chip
                            label={getStatusName(project.status)}
                            color={getStatusColor(project.status) as any}
                            size="small"
                          />
                          <Chip
                            label={getTypeName(project.type)}
                            size="small"
                            sx={{ 
                              bgcolor: getTypeColor(project.type),
                              color: 'white'
                            }}
                          />
                        </Box>
                      </Box>
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          setSelectedProject(project);
                          setAnchorEl(e.currentTarget);
                        }}
                      >
                        <MoreVertIcon />
                      </IconButton>
                    </Box>

                    <Typography variant="body2" color="text.secondary" mb={2} sx={{
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden'
                    }}>
                      {project.description}
                    </Typography>

                    <Box mb={2}>
                      <Box display="flex" justifyContent="space-between" mb={1}>
                        <Typography variant="body2">진행률</Typography>
                        <Typography variant="body2">{project.progress}%</Typography>
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={project.progress}
                        sx={{ height: 6, borderRadius: 3 }}
                      />
                    </Box>

                    <Stack spacing={1}>
                      {project.location && (
                        <Box display="flex" alignItems="center" gap={1}>
                          <CalendarIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                          <Typography variant="caption" color="text.secondary">
                            {project.location}
                          </Typography>
                        </Box>
                      )}
                      
                      {project.area && (
                        <Box display="flex" alignItems="center" gap={1}>
                          <Typography variant="caption" color="text.secondary">
                            면적: {formatArea(project.area)}
                          </Typography>
                        </Box>
                      )}
                      
                      {project.budget && (
                        <Box display="flex" alignItems="center" gap={1}>
                          <Typography variant="caption" color="text.secondary">
                            예산: {formatBudget(project.budget)}
                          </Typography>
                        </Box>
                      )}

                      {/* 건축 전문 정보 */}
                      {project.floorCount && (
                        <Box display="flex" alignItems="center" gap={1}>
                          <Typography variant="caption" color="text.secondary">
                            규모: {project.floorCount}층
                          </Typography>
                        </Box>
                      )}

                      {project.structureType && (
                        <Box display="flex" alignItems="center" gap={1}>
                          <Typography variant="caption" color="text.secondary">
                            구조: {formatStructureType(project.structureType)}
                          </Typography>
                        </Box>
                      )}

                      {project.sustainabilityRating && project.sustainabilityRating !== 'none' && (
                        <Box display="flex" alignItems="center" gap={1}>
                          <Chip
                            label={formatSustainabilityRating(project.sustainabilityRating)}
                            size="small"
                            sx={{
                              bgcolor: getSustainabilityColor(project.sustainabilityRating),
                              color: 'white',
                              fontSize: '0.7rem',
                              height: 20
                            }}
                          />
                        </Box>
                      )}

                      {project.energyRating && (
                        <Box display="flex" alignItems="center" gap={1}>
                          <Typography variant="caption" color="text.secondary">
                            에너지: {project.energyRating}
                          </Typography>
                        </Box>
                      )}
                    </Stack>

                    <Box mt={2}>
                      <AvatarGroup max={4}>
                        {project.members.map((member) => (
                          <Tooltip title={`${member.name} (${member.role})`} key={member.id}>
                            <Avatar sx={{ width: 24, height: 24, fontSize: 12 }}>
                              {member.name.charAt(0)}
                            </Avatar>
                          </Tooltip>
                        ))}
                      </AvatarGroup>
                    </Box>
                  </CardContent>

                  <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Button size="small" startIcon={<VisibilityIcon />}>
                        보기
                      </Button>
                      <Button 
                        size="small" 
                        startIcon={<TuneIcon />}
                        onClick={() => handleProjectAction('parametric', project)}
                        variant="outlined"
                        color="primary"
                      >
                        파라메트릭
                      </Button>
                    </Box>
                    <Button 
                      size="small" 
                      startIcon={<ThreeDRotationIcon />}
                      onClick={() => handleProjectAction('view3d', project)}
                    >
                      3D
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>

          {/* 페이지네이션 */}
          {totalPages > 1 && (
            <Box display="flex" justifyContent="center" mt={4}>
              <Pagination
                count={totalPages}
                page={currentPage}
                onChange={(_, page) => setCurrentPage(page)}
                color="primary"
                size="large"
              />
            </Box>
          )}
        </>
      )}

      {/* 프로젝트 액션 메뉴 */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={() => setAnchorEl(null)}
      >
        <MenuItem onClick={() => selectedProject && handleProjectAction('edit', selectedProject)}>
          <EditIcon sx={{ mr: 1, fontSize: 20 }} />
          편집
        </MenuItem>
        <MenuItem onClick={() => selectedProject && handleProjectAction('view3d', selectedProject)}>
          <ThreeDRotationIcon sx={{ mr: 1, fontSize: 20 }} />
          3D 보기
        </MenuItem>
        <MenuItem onClick={() => selectedProject && handleProjectAction('parametric', selectedProject)}>
          <TuneIcon sx={{ mr: 1, fontSize: 20 }} />
          파라메트릭 BIM
        </MenuItem>
        <MenuItem onClick={() => selectedProject && handleProjectAction('ai-optimize', selectedProject)}>
          <AutoAwesomeIcon sx={{ mr: 1, fontSize: 20 }} />
          AI 최적화
        </MenuItem>
        <MenuItem onClick={() => selectedProject && handleProjectAction('share', selectedProject)}>
          <ShareIcon sx={{ mr: 1, fontSize: 20 }} />
          공유
        </MenuItem>
        <Divider />
        <MenuItem onClick={() => selectedProject && handleProjectAction('archive', selectedProject)}>
          <ArchiveIcon sx={{ mr: 1, fontSize: 20 }} />
          보관
        </MenuItem>
        <MenuItem 
          onClick={() => selectedProject && handleProjectAction('delete', selectedProject)}
          sx={{ color: 'error.main' }}
        >
          <DeleteIcon sx={{ mr: 1, fontSize: 20 }} />
          삭제
        </MenuItem>
      </Menu>

      {/* 새 프로젝트 생성 모달 */}
      <Dialog 
        open={createProjectOpen} 
        onClose={() => {}} // 빈 영역 클릭으로 닫히지 않도록 설정
        maxWidth="xl" 
        fullWidth
        disableEscapeKeyDown // ESC 키로도 닫히지 않도록 설정
      >
        <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box>
            새 프로젝트 생성
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              건축 기준 및 규정에 따라 프로젝트 정보를 입력하세요
            </Typography>
          </Box>
          <IconButton
            aria-label="close"
            onClick={() => setCreateProjectOpen(false)}
            sx={{ mt: -1, mr: -1 }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          {/* 자동 채우기 설정 */}
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Box display="flex" alignItems="center" gap={2}>
              <Typography variant="body2">자동 규정 검토:</Typography>
              <Switch
                checked={autoFillEnabled}
                onChange={(e) => setAutoFillEnabled(e.target.checked)}
                size="small"
              />
              <Typography variant="caption" color="text.secondary">
                프로젝트 유형과 규모에 따라 자동으로 건축 기준을 적용합니다
              </Typography>
            </Box>
            
            {/* 템플릿 선택 */}
            <FormControl size="small" sx={{ minWidth: 200 }}>
              <InputLabel>건축 템플릿</InputLabel>
              <Select
                value={selectedTemplate}
                label="건축 템플릿"
                onChange={(e) => setSelectedTemplate(e.target.value)}
              >
                <MenuItem value="">템플릿 없음</MenuItem>
                <MenuItem value="residential.apartment">공동주택 템플릿</MenuItem>
                <MenuItem value="residential.villa">단독주택 템플릿</MenuItem>
                <MenuItem value="commercial.shopping">쇼핑몰 템플릿</MenuItem>
                <MenuItem value="commercial.hotel">호텔 템플릿</MenuItem>
                <MenuItem value="office.general">일반 업무시설 템플릿</MenuItem>
                <MenuItem value="public.school">교육시설 템플릿</MenuItem>
                <MenuItem value="public.hospital">의료시설 템플릿</MenuItem>
              </Select>
            </FormControl>
          </Box>

          <Tabs value={0} sx={{ mb: 3 }}>
            <Tab label="기본 정보" />
            <Tab label="건축 정보" />
            <Tab label="규정 준수" />
            <Tab label="디자인 이론" />
          </Tabs>

          <Grid container spacing={3}>
            {/* 기본 정보 섹션 */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>기본 정보</Typography>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="프로젝트 이름"
                value={newProject.name}
                onChange={(e) => setNewProject(prev => ({ ...prev, name: e.target.value }))}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="프로젝트 설명"
                multiline
                rows={3}
                value={newProject.description}
                onChange={(e) => setNewProject(prev => ({ ...prev, description: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth required>
                <InputLabel>프로젝트 유형</InputLabel>
                <Select
                  value={newProject.type}
                  label="프로젝트 유형"
                  onChange={(e) => setNewProject(prev => ({ ...prev, type: e.target.value as any }))}
                >
                  <MenuItem value="residential">주거 (공동주택, 단독주택)</MenuItem>
                  <MenuItem value="commercial">상업 (쇼핑몰, 호텔, 리조트)</MenuItem>
                  <MenuItem value="office">업무 (사무용 건물)</MenuItem>
                  <MenuItem value="industrial">산업 (공장, 창고)</MenuItem>
                  <MenuItem value="public">공공 (학교, 병원, 관공서)</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Box>
                <TextField
                  fullWidth
                  label="위치"
                  value={newProject.location}
                  onChange={(e) => setNewProject(prev => ({ ...prev, location: e.target.value }))}
                  placeholder="예: 서울시 강남구 테헤란로"
                />
                <Box mt={1}>
                  <Typography variant="caption" color="text.secondary">빠른 선택:</Typography>
                  <Box display="flex" flexWrap="wrap" gap={0.5} mt={0.5}>
                    {fieldPresets.location.map((preset) => (
                      <Chip
                        key={preset.value}
                        label={preset.label}
                        size="small"
                        variant="outlined"
                        onClick={() => handlePresetSelect('location', preset.value)}
                        sx={{ fontSize: '0.7rem' }}
                      />
                    ))}
                  </Box>
                </Box>
              </Box>
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="면적 (㎡)"
                type="number"
                value={newProject.area}
                onChange={(e) => setNewProject(prev => ({ ...prev, area: e.target.value }))}
                helperText="연면적을 입력하세요"
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="예산 (억원)"
                type="number"
                value={newProject.budget}
                onChange={(e) => setNewProject(prev => ({ ...prev, budget: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="마감일"
                type="date"
                value={newProject.dueDate}
                onChange={(e) => setNewProject(prev => ({ ...prev, dueDate: e.target.value }))}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>

            {/* 건축 정보 섹션 */}
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom>건축 정보</Typography>
            </Grid>
            <Grid item xs={12} sm={3}>
              <TextField
                fullWidth
                label="층수"
                type="number"
                value={newProject.floorCount}
                onChange={(e) => setNewProject(prev => ({ ...prev, floorCount: e.target.value }))}
                helperText="지상층수"
              />
            </Grid>
            <Grid item xs={12} sm={3}>
              <TextField
                fullWidth
                label="건물 높이 (m)"
                type="number"
                value={newProject.buildingHeight}
                onChange={(e) => setNewProject(prev => ({ ...prev, buildingHeight: e.target.value }))}
                helperText="최고 높이"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>구조 형식</InputLabel>
                <Select
                  value={newProject.structureType}
                  label="구조 형식"
                  onChange={(e) => setNewProject(prev => ({ ...prev, structureType: e.target.value as any }))}
                >
                  <MenuItem value="reinforced_concrete">철근콘크리트구조</MenuItem>
                  <MenuItem value="steel">철골구조</MenuItem>
                  <MenuItem value="timber">목구조</MenuItem>
                  <MenuItem value="masonry">조적구조</MenuItem>
                  <MenuItem value="hybrid">복합구조</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Box>
                <TextField
                  fullWidth
                  label="건물 용도"
                  value={newProject.buildingUse}
                  onChange={(e) => setNewProject(prev => ({ ...prev, buildingUse: e.target.value }))}
                  placeholder="예: 업무시설, 공동주택, 근린생활시설"
                />
                {newProject.type && fieldPresets.buildingUse[newProject.type as keyof typeof fieldPresets.buildingUse] && (
                  <Box mt={1}>
                    <Typography variant="caption" color="text.secondary">빠른 선택 ({getTypeName(newProject.type)}):</Typography>
                    <Box display="flex" flexWrap="wrap" gap={0.5} mt={0.5}>
                      {fieldPresets.buildingUse[newProject.type as keyof typeof fieldPresets.buildingUse].map((use) => (
                        <Chip
                          key={use}
                          label={use}
                          size="small"
                          variant="outlined"
                          onClick={() => handlePresetSelect('buildingUse', use)}
                          sx={{ fontSize: '0.7rem' }}
                        />
                      ))}
                    </Box>
                  </Box>
                )}
              </Box>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Box>
                <TextField
                  fullWidth
                  label="지역 지구"
                  value={newProject.zoneClassification}
                  onChange={(e) => setNewProject(prev => ({ ...prev, zoneClassification: e.target.value }))}
                  placeholder="예: 상업지역, 일반주거지역"
                />
                <Box mt={1}>
                  <Typography variant="caption" color="text.secondary">빠른 선택:</Typography>
                  <Box display="flex" flexWrap="wrap" gap={0.5} mt={0.5}>
                    {fieldPresets.zoneClassification.map((zone) => (
                      <Chip
                        key={zone.value}
                        label={zone.label}
                        size="small"
                        variant="outlined"
                        onClick={() => handlePresetSelect('zoneClassification', zone.value)}
                        sx={{ fontSize: '0.7rem' }}
                      />
                    ))}
                  </Box>
                </Box>
              </Box>
            </Grid>

            {/* 규정 준수 섹션 */}
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom>규정 준수 정보</Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Box>
                <TextField
                  fullWidth
                  label="내화등급"
                  value={newProject.fireRating}
                  onChange={(e) => setNewProject(prev => ({ ...prev, fireRating: e.target.value }))}
                  placeholder="예: 내화구조 2시간"
                />
                <Box mt={1}>
                  <Typography variant="caption" color="text.secondary">빠른 선택:</Typography>
                  <Box display="flex" flexWrap="wrap" gap={0.5} mt={0.5}>
                    {fieldPresets.fireRating.map((rating) => (
                      <Chip
                        key={rating.value}
                        label={rating.label}
                        size="small"
                        variant="outlined"
                        onClick={() => handlePresetSelect('fireRating', rating.value)}
                        sx={{ fontSize: '0.7rem' }}
                      />
                    ))}
                  </Box>
                </Box>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Box>
                <TextField
                  fullWidth
                  label="에너지 효율등급"
                  value={newProject.energyRating}
                  onChange={(e) => setNewProject(prev => ({ ...prev, energyRating: e.target.value }))}
                  placeholder="예: 1++급, 1급"
                />
                <Box mt={1}>
                  <Typography variant="caption" color="text.secondary">빠른 선택:</Typography>
                  <Box display="flex" flexWrap="wrap" gap={0.5} mt={0.5}>
                    {fieldPresets.energyRating.map((rating) => (
                      <Chip
                        key={rating.value}
                        label={rating.label}
                        size="small"
                        variant="outlined"
                        onClick={() => handlePresetSelect('energyRating', rating.value)}
                        sx={{ fontSize: '0.7rem' }}
                      />
                    ))}
                  </Box>
                </Box>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>친환경 인증</InputLabel>
                <Select
                  value={newProject.sustainabilityRating}
                  label="친환경 인증"
                  onChange={(e) => setNewProject(prev => ({ ...prev, sustainabilityRating: e.target.value as any }))}
                >
                  <MenuItem value="none">인증 없음</MenuItem>
                  <MenuItem value="green">녹색건축인증</MenuItem>
                  <MenuItem value="leed">LEED 인증</MenuItem>
                  <MenuItem value="breeam">BREEAM 인증</MenuItem>
                  <MenuItem value="korea_green">한국녹색건축인증</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Box display="flex" alignItems="center" gap={2}>
                <Typography>장애인 편의시설 준수</Typography>
                <Switch
                  checked={newProject.accessibilityCompliance}
                  onChange={(e) => setNewProject(prev => ({ ...prev, accessibilityCompliance: e.target.checked }))}
                />
              </Box>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="친환경 시설 (쉼표로 구분)"
                value={newProject.environmentalFeatures}
                onChange={(e) => setNewProject(prev => ({ ...prev, environmentalFeatures: e.target.value }))}
                placeholder="예: LED 조명, 태양광 패널, 빗물 재활용, 지열냉난방"
                multiline
                rows={2}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="적용 건축기준 (쉼표로 구분)"
                value={newProject.constructionStandards}
                onChange={(e) => setNewProject(prev => ({ ...prev, constructionStandards: e.target.value }))}
                placeholder="예: KS F 4009, 내진설계기준, 건축물 에너지절약설계기준"
                multiline
                rows={2}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="주요 건축자재 (쉼표로 구분)"
                value={newProject.materialSpecs}
                onChange={(e) => setNewProject(prev => ({ ...prev, materialSpecs: e.target.value }))}
                placeholder="예: 고강도 콘크리트, 친환경 단열재, 고효율 유리커튼월"
                multiline
                rows={2}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="태그 (쉼표로 구분)"
                placeholder="예: 고층건물, 친환경, 스마트빌딩"
                value={newProject.tags}
                onChange={(e) => setNewProject(prev => ({ ...prev, tags: e.target.value }))}
              />
            </Grid>

            {/* 적용 가능한 건축법규 안내 */}
            {newProject.type && getApplicableBuildingCodes(newProject.type).length > 0 && (
              <Grid item xs={12}>
                <Alert severity="info" sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    해당 프로젝트 유형에 적용되는 주요 건축법규:
                  </Typography>
                  <ul style={{ margin: 0, paddingLeft: 20 }}>
                    {getApplicableBuildingCodes(newProject.type).map(code => (
                      <li key={code.id}>
                        <strong>{code.name}</strong>: {code.description}
                      </li>
                    ))}
                  </ul>
                </Alert>
              </Grid>
            )}

            {/* 디자인 이론 섹션 */}
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom>디자인 이론</Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Box>
                <TextField
                  fullWidth
                  label="디자인 스타일"
                  value={newProject.designStyle}
                  onChange={(e) => setNewProject(prev => ({ ...prev, designStyle: e.target.value }))}
                  placeholder="예: 모던, 미니멀, 인더스트리얼"
                />
                <Box mt={1}>
                  <Typography variant="caption" color="text.secondary">빠른 선택:</Typography>
                  <Box display="flex" flexWrap="wrap" gap={0.5} mt={0.5}>
                    {fieldPresets.designStyles.map((style) => (
                      <Chip
                        key={style}
                        label={style}
                        size="small"
                        variant="outlined"
                        onClick={() => handlePresetSelect('designStyle', style)}
                        sx={{ fontSize: '0.7rem' }}
                      />
                    ))}
                  </Box>
                </Box>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Box>
                <TextField
                  fullWidth
                  label="설계 원칙"
                  value={newProject.designPrinciples}
                  onChange={(e) => setNewProject(prev => ({ ...prev, designPrinciples: e.target.value }))}
                  placeholder="예: 비례와 균형, 기능주의"
                  multiline
                  rows={2}
                />
                <Box mt={1}>
                  <Typography variant="caption" color="text.secondary">빠른 선택 (다중 선택 가능):</Typography>
                  <Box display="flex" flexWrap="wrap" gap={0.5} mt={0.5}>
                    {fieldPresets.designPrinciples.map((principle) => (
                      <Chip
                        key={principle}
                        label={principle}
                        size="small"
                        variant={newProject.designPrinciples.includes(principle) ? "filled" : "outlined"}
                        onClick={() => handleMultiPresetToggle('designPrinciples', principle)}
                        sx={{ fontSize: '0.7rem' }}
                      />
                    ))}
                  </Box>
                </Box>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Box>
                <TextField
                  fullWidth
                  label="공간 유형"
                  value={newProject.spaceTypes}
                  onChange={(e) => setNewProject(prev => ({ ...prev, spaceTypes: e.target.value }))}
                  placeholder="예: 개방형 공간, 아트리움"
                  multiline
                  rows={2}
                />
                <Box mt={1}>
                  <Typography variant="caption" color="text.secondary">빠른 선택 (다중 선택 가능):</Typography>
                  <Box display="flex" flexWrap="wrap" gap={0.5} mt={0.5}>
                    {fieldPresets.spaceTypes.map((spaceType) => (
                      <Chip
                        key={spaceType}
                        label={spaceType}
                        size="small"
                        variant={newProject.spaceTypes.includes(spaceType) ? "filled" : "outlined"}
                        onClick={() => handleMultiPresetToggle('spaceTypes', spaceType)}
                        sx={{ fontSize: '0.7rem' }}
                      />
                    ))}
                  </Box>
                </Box>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="색채 계획"
                value={newProject.colorScheme}
                onChange={(e) => setNewProject(prev => ({ ...prev, colorScheme: e.target.value }))}
                placeholder="예: 모노톤, 어스톤, 비비드"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="조명 계획"
                value={newProject.lightingConcept}
                onChange={(e) => setNewProject(prev => ({ ...prev, lightingConcept: e.target.value }))}
                placeholder="예: 자연광 중심, 간접조명, 포인트조명"
                multiline
                rows={2}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateProjectOpen(false)}>
            취소
          </Button>
          <Button 
            onClick={handleCreateProject}
            variant="contained"
            disabled={!newProject.name.trim()}
          >
            프로젝트 생성
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ProjectsPage;