"""
건축 디자인 전문가 AI 에이전트
=============================

한국 건축의 모든 디자인 패턴, 스타일, 미학적 원리를 전문적으로 다루는 AI 에이전트
전통 한옥부터 현대 건축까지 한국 건축의 전 영역을 커버

@version 1.0
@author VIBA AI Team
@date 2025.07.06
"""

import asyncio
import json
import logging
import time
import math
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid

# 프로젝트 임포트 (절대 경로)
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from ai.base_agent import BaseVIBAAgent, AgentCapability
from utils.metrics_collector import record_ai_inference_metric

logger = logging.getLogger(__name__)


class KoreanArchitecturalStyle(Enum):
    """한국 건축 스타일"""
    # 전통 건축
    TRADITIONAL_HANOK = "traditional_hanok"           # 전통 한옥
    ROYAL_PALACE = "royal_palace"                     # 궁궐 건축
    BUDDHIST_TEMPLE = "buddhist_temple"               # 불교 사찰
    CONFUCIAN_SHRINE = "confucian_shrine"             # 유교 사당
    FOLK_HOUSE = "folk_house"                         # 민가
    FORTRESS = "fortress"                             # 성곽 건축
    
    # 근대 건축 (일제강점기~해방)
    JAPANESE_COLONIAL = "japanese_colonial"           # 일제강점기 건축
    EARLY_MODERN = "early_modern"                     # 초기 근대 건축
    
    # 현대 건축 (1960년대~)
    MODERNISM = "modernism"                           # 모더니즘
    BRUTALISM = "brutalism"                           # 브루털리즘
    POSTMODERN = "postmodern"                         # 포스트모던
    
    # 21세기 한국 건축
    NEO_KOREAN = "neo_korean"                         # 신한국 건축
    K_CONTEMPORARY = "k_contemporary"                 # K-현대 건축
    SUSTAINABLE_KOREAN = "sustainable_korean"         # 지속가능 한국 건축
    DIGITAL_KOREAN = "digital_korean"                 # 디지털 한국 건축
    
    # 하이브리드 스타일
    HANOK_MODERN = "hanok_modern"                     # 한옥+모던
    KOREAN_MINIMALISM = "korean_minimalism"           # 한국적 미니멀리즘
    URBAN_HANOK = "urban_hanok"                       # 도시형 한옥


class DesignElement(Enum):
    """디자인 요소"""
    # 구조적 요소
    STRUCTURE = "structure"
    FOUNDATION = "foundation"
    COLUMNS = "columns"
    BEAMS = "beams"
    ROOF = "roof"
    WALLS = "walls"
    
    # 공간적 요소
    SPATIAL_LAYOUT = "spatial_layout"
    CIRCULATION = "circulation"
    HIERARCHY = "hierarchy"
    TRANSITION = "transition"
    
    # 미학적 요소
    PROPORTION = "proportion"
    SYMMETRY = "symmetry"
    RHYTHM = "rhythm"
    SCALE = "scale"
    COLOR = "color"
    TEXTURE = "texture"
    LIGHT = "light"
    
    # 문화적 요소
    SYMBOLISM = "symbolism"
    RITUAL = "ritual"
    SOCIAL_FUNCTION = "social_function"
    ENVIRONMENTAL_HARMONY = "environmental_harmony"


class RegionalStyle(Enum):
    """지역별 건축 특색"""
    SEOUL_GYEONGGI = "seoul_gyeonggi"                 # 서울·경기 지역
    CHUNGCHEONG = "chungcheong"                       # 충청 지역
    JEOLLA = "jeolla"                                 # 전라 지역
    GYEONGSANG = "gyeongsang"                         # 경상 지역
    GANGWON = "gangwon"                               # 강원 지역
    JEJU = "jeju"                                     # 제주 지역
    NORTH_KOREA = "north_korea"                       # 북한 지역 (전통)


@dataclass
class ArchitecturalPattern:
    """건축 패턴"""
    pattern_id: str
    name: str
    korean_name: str
    style: KoreanArchitecturalStyle
    description: str
    key_features: List[str]
    materials: List[str]
    proportions: Dict[str, float]
    cultural_significance: str
    modern_applications: List[str]
    regional_variations: List[RegionalStyle] = field(default_factory=list)


@dataclass
class DesignRecommendation:
    """디자인 권장사항"""
    element: DesignElement
    recommendation: str
    rationale: str
    cultural_context: str
    implementation_details: List[str]
    priority: str  # high, medium, low
    style_compatibility: List[KoreanArchitecturalStyle]


@dataclass
class ArchitecturalAnalysis:
    """건축 디자인 분석 결과"""
    primary_style: KoreanArchitecturalStyle
    secondary_styles: List[KoreanArchitecturalStyle]
    design_patterns: List[ArchitecturalPattern]
    design_recommendations: List[DesignRecommendation]
    cultural_significance: str
    modern_adaptation_strategy: str
    aesthetic_principles: List[str]
    spatial_organization: Dict[str, Any]
    materials_palette: List[str]
    color_scheme: Dict[str, str]
    lighting_strategy: str


class ArchitecturalDesignSpecialist(BaseVIBAAgent):
    """건축 디자인 전문가 AI 에이전트"""
    
    def __init__(self):
        super().__init__(
            agent_id="architectural_design_specialist",
            name="Architectural Design Specialist",
            capabilities=[
                AgentCapability.DESIGN_THEORY_APPLICATION,
                AgentCapability.CULTURAL_ADAPTATION,
                AgentCapability.SPATIAL_PLANNING,
                AgentCapability.QUALITY_ASSESSMENT
            ]
        )
        
        # 한국 건축 지식 베이스
        self.architectural_patterns = self._initialize_architectural_patterns()
        self.design_principles = self._initialize_design_principles()
        self.regional_characteristics = self._initialize_regional_characteristics()
        self.material_traditions = self._initialize_material_traditions()
        self.color_palettes = self._initialize_color_palettes()
        
        logger.info("건축 디자인 전문가 AI 에이전트 초기화 완료")
    
    async def initialize(self) -> bool:
        """에이전트 초기화"""
        try:
            logger.info("건축 디자인 전문가 AI 초기화 시작")
            
            # 지식 베이스 검증
            assert len(self.architectural_patterns) > 0, "건축 패턴 데이터 없음"
            assert len(self.design_principles) > 0, "디자인 원칙 데이터 없음"
            
            self.is_initialized = True
            logger.info("건축 디자인 전문가 AI 초기화 완료")
            return True
            
        except Exception as e:
            logger.error(f"건축 디자인 전문가 AI 초기화 실패: {e}")
            return False
    
    async def execute_task(self, task) -> Dict[str, Any]:
        """작업 실행"""
        start_time = time.time()
        
        try:
            # 입력 데이터 파싱
            if isinstance(task, dict):
                user_input = task.get("user_input", "")
                building_type = task.get("building_type", "residential")
                style_preference = task.get("style_preference", "modern")
                location = task.get("location", "서울")
                cultural_context = task.get("cultural_context", "contemporary")
            else:
                user_input = str(task)
                building_type = "residential"
                style_preference = "modern"
                location = "서울"
                cultural_context = "contemporary"
            
            with record_ai_inference_metric("architectural_design", "style_analysis"):
                # 1. 스타일 분석 및 식별
                style_analysis = await self._analyze_architectural_style(
                    user_input, style_preference, cultural_context
                )
            
            with record_ai_inference_metric("architectural_design", "pattern_matching"):
                # 2. 적합한 건축 패턴 매칭
                matching_patterns = await self._find_matching_patterns(
                    style_analysis, building_type, location
                )
            
            with record_ai_inference_metric("architectural_design", "design_generation"):
                # 3. 디자인 권장사항 생성
                design_recommendations = await self._generate_design_recommendations(
                    style_analysis, matching_patterns, building_type
                )
            
            with record_ai_inference_metric("architectural_design", "cultural_adaptation"):
                # 4. 문화적 적응 방안
                cultural_adaptation = await self._develop_cultural_adaptation_strategy(
                    style_analysis, location, cultural_context
                )
            
            with record_ai_inference_metric("architectural_design", "spatial_planning"):
                # 5. 공간 구성 계획
                spatial_organization = await self._plan_spatial_organization(
                    style_analysis, building_type, matching_patterns
                )
            
            with record_ai_inference_metric("architectural_design", "material_selection"):
                # 6. 재료 및 색채 팔레트
                materials_and_colors = await self._select_materials_and_colors(
                    style_analysis, location, cultural_context
                )
            
            # 7. 종합 분석 결과 구성
            architectural_analysis = ArchitecturalAnalysis(
                primary_style=style_analysis["primary_style"],
                secondary_styles=style_analysis["secondary_styles"],
                design_patterns=matching_patterns,
                design_recommendations=design_recommendations,
                cultural_significance=cultural_adaptation["significance"],
                modern_adaptation_strategy=cultural_adaptation["strategy"],
                aesthetic_principles=style_analysis["aesthetic_principles"],
                spatial_organization=spatial_organization,
                materials_palette=materials_and_colors["materials"],
                color_scheme=materials_and_colors["colors"],
                lighting_strategy=materials_and_colors["lighting"]
            )
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "agent_type": "architectural_design_specialist",
                "analysis_result": architectural_analysis,
                "style_confidence": style_analysis["confidence"],
                "pattern_matches": len(matching_patterns),
                "recommendations_count": len(design_recommendations),
                "execution_time": execution_time,
                "cultural_authenticity_score": cultural_adaptation["authenticity_score"],
                "modern_relevance_score": cultural_adaptation["relevance_score"],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"건축 디자인 분석 실패: {e}")
            
            return {
                "success": False,
                "agent_type": "architectural_design_specialist",
                "error": str(e),
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _analyze_architectural_style(
        self, 
        user_input: str, 
        style_preference: str, 
        cultural_context: str
    ) -> Dict[str, Any]:
        """건축 스타일 분석"""
        
        # 키워드 기반 스타일 분석
        style_indicators = {
            "한옥": KoreanArchitecturalStyle.TRADITIONAL_HANOK,
            "전통": KoreanArchitecturalStyle.TRADITIONAL_HANOK,
            "궁궐": KoreanArchitecturalStyle.ROYAL_PALACE,
            "사찰": KoreanArchitecturalStyle.BUDDHIST_TEMPLE,
            "모던": KoreanArchitecturalStyle.MODERNISM,
            "현대": KoreanArchitecturalStyle.K_CONTEMPORARY,
            "미니멀": KoreanArchitecturalStyle.KOREAN_MINIMALISM,
            "친환경": KoreanArchitecturalStyle.SUSTAINABLE_KOREAN,
            "신한국": KoreanArchitecturalStyle.NEO_KOREAN
        }
        
        # 기본 스타일 결정
        primary_style = KoreanArchitecturalStyle.K_CONTEMPORARY
        for keyword, style in style_indicators.items():
            if keyword in user_input:
                primary_style = style
                break
        
        # 보조 스타일 결정
        secondary_styles = []
        if "모던" in user_input and "한옥" in user_input:
            secondary_styles.append(KoreanArchitecturalStyle.HANOK_MODERN)
        if "도시" in user_input and "한옥" in user_input:
            secondary_styles.append(KoreanArchitecturalStyle.URBAN_HANOK)
        
        # 미학적 원칙 추출
        aesthetic_principles = self._extract_aesthetic_principles(primary_style, user_input)
        
        return {
            "primary_style": primary_style,
            "secondary_styles": secondary_styles,
            "aesthetic_principles": aesthetic_principles,
            "confidence": 0.85,  # 실제로는 ML 모델 기반 계산
            "style_keywords": [k for k in style_indicators.keys() if k in user_input]
        }
    
    async def _find_matching_patterns(
        self, 
        style_analysis: Dict[str, Any], 
        building_type: str, 
        location: str
    ) -> List[ArchitecturalPattern]:
        """적합한 건축 패턴 찾기"""
        
        primary_style = style_analysis["primary_style"]
        matching_patterns = []
        
        # 스타일별 패턴 매칭
        for pattern in self.architectural_patterns:
            if pattern.style == primary_style:
                matching_patterns.append(pattern)
            elif primary_style in [KoreanArchitecturalStyle.HANOK_MODERN, KoreanArchitecturalStyle.NEO_KOREAN]:
                # 하이브리드 스타일의 경우 전통과 현대 패턴 모두 포함
                if pattern.style in [KoreanArchitecturalStyle.TRADITIONAL_HANOK, KoreanArchitecturalStyle.K_CONTEMPORARY]:
                    matching_patterns.append(pattern)
        
        # 건물 타입에 따른 필터링
        building_specific_patterns = []
        for pattern in matching_patterns:
            if building_type in pattern.modern_applications:
                building_specific_patterns.append(pattern)
        
        return building_specific_patterns if building_specific_patterns else matching_patterns[:3]
    
    async def _generate_design_recommendations(
        self, 
        style_analysis: Dict[str, Any], 
        patterns: List[ArchitecturalPattern], 
        building_type: str
    ) -> List[DesignRecommendation]:
        """디자인 권장사항 생성"""
        
        recommendations = []
        primary_style = style_analysis["primary_style"]
        
        # 스타일별 핵심 권장사항
        if primary_style == KoreanArchitecturalStyle.TRADITIONAL_HANOK:
            recommendations.extend(self._generate_hanok_recommendations())
        elif primary_style == KoreanArchitecturalStyle.K_CONTEMPORARY:
            recommendations.extend(self._generate_contemporary_recommendations())
        elif primary_style == KoreanArchitecturalStyle.HANOK_MODERN:
            recommendations.extend(self._generate_hybrid_recommendations())
        
        # 건물 타입별 특화 권장사항
        if building_type == "residential":
            recommendations.extend(self._generate_residential_recommendations(primary_style))
        elif building_type == "commercial":
            recommendations.extend(self._generate_commercial_recommendations(primary_style))
        elif building_type == "cultural":
            recommendations.extend(self._generate_cultural_recommendations(primary_style))
        
        return recommendations[:8]  # 상위 8개 권장사항 반환
    
    async def _develop_cultural_adaptation_strategy(
        self, 
        style_analysis: Dict[str, Any], 
        location: str, 
        cultural_context: str
    ) -> Dict[str, Any]:
        """문화적 적응 전략 개발"""
        
        primary_style = style_analysis["primary_style"]
        
        # 문화적 의미 분석
        cultural_significance = self._analyze_cultural_significance(primary_style)
        
        # 현대적 적응 전략
        adaptation_strategy = self._develop_adaptation_strategy(primary_style, cultural_context)
        
        # 진정성 점수 (전통성 유지 정도)
        authenticity_score = self._calculate_authenticity_score(primary_style, cultural_context)
        
        # 현대적 관련성 점수
        relevance_score = self._calculate_relevance_score(primary_style, cultural_context)
        
        return {
            "significance": cultural_significance,
            "strategy": adaptation_strategy,
            "authenticity_score": authenticity_score,
            "relevance_score": relevance_score,
            "location_considerations": self._get_location_considerations(location)
        }
    
    async def _plan_spatial_organization(
        self, 
        style_analysis: Dict[str, Any], 
        building_type: str, 
        patterns: List[ArchitecturalPattern]
    ) -> Dict[str, Any]:
        """공간 구성 계획"""
        
        primary_style = style_analysis["primary_style"]
        
        # 스타일별 공간 구성 원칙
        if primary_style == KoreanArchitecturalStyle.TRADITIONAL_HANOK:
            spatial_principles = {
                "layout_type": "ㅁ자형 또는 ㄱ자형",
                "core_spaces": ["대청", "안채", "사랑채", "부엌"],
                "circulation": "마당 중심의 순환 동선",
                "hierarchy": "안채(여성공간) - 사랑채(남성공간) 분리",
                "connection_to_nature": "마당, 뜰, 정원과의 연계"
            }
        elif primary_style == KoreanArchitecturalStyle.K_CONTEMPORARY:
            spatial_principles = {
                "layout_type": "오픈 플랜",
                "core_spaces": ["거실", "주방", "침실", "작업공간"],
                "circulation": "효율적 직선 동선",
                "hierarchy": "공용공간 - 사적공간 구분",
                "connection_to_nature": "대형 창호를 통한 자연 조망"
            }
        else:
            spatial_principles = {
                "layout_type": "하이브리드",
                "core_spaces": ["현대적 거실", "전통적 대청", "다목적 공간"],
                "circulation": "전통과 현대의 조화",
                "hierarchy": "유연한 공간 위계",
                "connection_to_nature": "내외부 공간의 연속성"
            }
        
        return spatial_principles
    
    async def _select_materials_and_colors(
        self, 
        style_analysis: Dict[str, Any], 
        location: str, 
        cultural_context: str
    ) -> Dict[str, Any]:
        """재료 및 색채 선택"""
        
        primary_style = style_analysis["primary_style"]
        
        # 스타일별 재료 팔레트
        if primary_style == KoreanArchitecturalStyle.TRADITIONAL_HANOK:
            materials = ["한국산 소나무", "황토", "한지", "자연석", "기와", "대나무"]
            colors = {
                "primary": "자연목 색상",
                "secondary": "황토색",
                "accent": "단청 색상 (청, 적, 황, 백, 흑)",
                "neutral": "회백색"
            }
        elif primary_style == KoreanArchitecturalStyle.K_CONTEMPORARY:
            materials = ["노출콘크리트", "강철", "유리", "천연석", "목재", "세라믹"]
            colors = {
                "primary": "화이트",
                "secondary": "그레이",
                "accent": "블랙",
                "neutral": "베이지"
            }
        else:  # 하이브리드 스타일
            materials = ["재생목재", "현대적 황토", "Low-E 유리", "자연석", "금속", "친환경 소재"]
            colors = {
                "primary": "웜 화이트",
                "secondary": "내추럴 그레이",
                "accent": "딥 그린",
                "neutral": "샌드 베이지"
            }
        
        # 조명 전략
        lighting_strategy = self._develop_lighting_strategy(primary_style)
        
        return {
            "materials": materials,
            "colors": colors,
            "lighting": lighting_strategy,
            "sustainability_considerations": self._get_sustainability_considerations(materials)
        }
    
    def _initialize_architectural_patterns(self) -> List[ArchitecturalPattern]:
        """건축 패턴 데이터베이스 초기화"""
        return [
            ArchitecturalPattern(
                pattern_id="hanok_001",
                name="Traditional Hanok Layout",
                korean_name="전통 한옥 배치",
                style=KoreanArchitecturalStyle.TRADITIONAL_HANOK,
                description="마당을 중심으로 한 ㅁ자형 또는 ㄱ자형 배치",
                key_features=["중정(마당)", "처마", "온돌", "대청", "기단"],
                materials=["목재", "황토", "기와", "자연석"],
                proportions={"width_height_ratio": 1.618, "column_spacing": 3.0},
                cultural_significance="자연과의 조화, 계절 변화 수용, 가족 질서 반영",
                modern_applications=["residential", "cultural", "hospitality"],
                regional_variations=[RegionalStyle.SEOUL_GYEONGGI, RegionalStyle.JEOLLA]
            ),
            ArchitecturalPattern(
                pattern_id="palace_001",
                name="Royal Palace Architecture",
                korean_name="궁궐 건축",
                style=KoreanArchitecturalStyle.ROYAL_PALACE,
                description="위계질서가 명확한 대규모 복합 건축",
                key_features=["정전", "편전", "행각", "담장", "문루"],
                materials=["최고급 목재", "단청", "기와", "자연석"],
                proportions={"width_height_ratio": 2.0, "column_spacing": 4.0},
                cultural_significance="왕권 상징, 유교 질서 구현",
                modern_applications=["cultural", "government", "ceremonial"],
                regional_variations=[RegionalStyle.SEOUL_GYEONGGI]
            ),
            ArchitecturalPattern(
                pattern_id="contemporary_001",
                name="K-Contemporary Style",
                korean_name="K-현대 건축",
                style=KoreanArchitecturalStyle.K_CONTEMPORARY,
                description="한국적 정서와 현대 기능의 조화",
                key_features=["큰 창호", "미니멀 디자인", "자연 소재", "수직 정원"],
                materials=["콘크리트", "스틸", "목재", "유리"],
                proportions={"width_height_ratio": 1.5, "column_spacing": 6.0},
                cultural_significance="글로벌 시대 한국 정체성 표현",
                modern_applications=["residential", "commercial", "office", "cultural"],
                regional_variations=[RegionalStyle.SEOUL_GYEONGGI]
            ),
            ArchitecturalPattern(
                pattern_id="hybrid_001",
                name="Modern Hanok",
                korean_name="모던 한옥",
                style=KoreanArchitecturalStyle.HANOK_MODERN,
                description="전통 한옥의 공간 구성과 현대 건축 기술의 융합",
                key_features=["현대적 마당", "대형 유리창", "현대식 온돌", "모던 처마"],
                materials=["재생목재", "현대 황토", "Low-E 유리", "천연석"],
                proportions={"width_height_ratio": 1.4, "column_spacing": 4.5},
                cultural_significance="전통의 현대적 계승",
                modern_applications=["residential", "boutique_hotel", "cultural"],
                regional_variations=[RegionalStyle.SEOUL_GYEONGGI, RegionalStyle.JEJU]
            )
        ]
    
    def _initialize_design_principles(self) -> Dict[str, List[str]]:
        """디자인 원칙 초기화"""
        return {
            "traditional": [
                "자연과의 조화 (自然調和)",
                "비움의 미학 (虛靜美)",
                "절제와 소박함 (質樸美)",
                "계절 변화 수용",
                "내외부 공간 연속성"
            ],
            "contemporary": [
                "기능적 단순성",
                "재료의 정직한 표현",
                "빛과 그림자의 활용",
                "지속가능성",
                "유연한 공간 구성"
            ],
            "hybrid": [
                "전통과 현대의 조화",
                "문화적 연속성",
                "현대적 편의성",
                "환경 친화성",
                "지역성 존중"
            ]
        }
    
    def _initialize_regional_characteristics(self) -> Dict[RegionalStyle, Dict[str, Any]]:
        """지역별 특성 초기화"""
        return {
            RegionalStyle.SEOUL_GYEONGGI: {
                "climate": "온대성 기후",
                "materials": ["화강암", "소나무", "황토"],
                "characteristics": ["단정한 비례", "격조 있는 장식"],
                "color_preference": ["백색", "회색", "자연목색"]
            },
            RegionalStyle.JEOLLA: {
                "climate": "온난습윤 기후",
                "materials": ["참나무", "대나무", "황토"],
                "characteristics": ["자유로운 곡선", "풍부한 장식"],
                "color_preference": ["따뜻한 황토색", "연두색", "적색"]
            },
            RegionalStyle.JEJU: {
                "climate": "해양성 기후",
                "materials": ["현무암", "삼나무", "바다풀"],
                "characteristics": ["바람에 견디는 구조", "낮은 처마"],
                "color_preference": ["현무암 검정", "바다색", "하늘색"]
            }
        }
    
    def _initialize_material_traditions(self) -> Dict[str, Dict[str, Any]]:
        """전통 재료 정보 초기화"""
        return {
            "목재": {
                "types": ["소나무", "참나무", "은행나무", "느티나무"],
                "characteristics": "항균성, 조습성, 온화한 촉감",
                "applications": ["기둥", "보", "벽체", "바닥"],
                "sustainability": "재생 가능, 탄소 저장"
            },
            "황토": {
                "types": ["적황토", "회황토", "백황토"],
                "characteristics": "조습성, 항균성, 원적외선 방출",
                "applications": ["벽체", "바닥", "온돌"],
                "sustainability": "자연 소재, 무공해"
            },
            "자연석": {
                "types": ["화강암", "사암", "현무암"],
                "characteristics": "내구성, 자연미, 열 축적",
                "applications": ["기단", "담장", "포장"],
                "sustainability": "반영구적 사용"
            }
        }
    
    def _initialize_color_palettes(self) -> Dict[KoreanArchitecturalStyle, Dict[str, List[str]]]:
        """색채 팔레트 초기화"""
        return {
            KoreanArchitecturalStyle.TRADITIONAL_HANOK: {
                "primary": ["자연목색", "황토색"],
                "secondary": ["회백색", "청회색"],
                "accent": ["단청 빨강", "단청 파랑", "단청 초록"],
                "neutral": ["베이지", "크림"]
            },
            KoreanArchitecturalStyle.K_CONTEMPORARY: {
                "primary": ["순백", "오프화이트"],
                "secondary": ["라이트그레이", "미디엄그레이"],
                "accent": ["딥블랙", "네이비블루"],
                "neutral": ["웜베이지", "쿨그레이"]
            },
            KoreanArchitecturalStyle.HANOK_MODERN: {
                "primary": ["웜화이트", "내추럴베이지"],
                "secondary": ["소프트그레이", "스톤그레이"],
                "accent": ["딥그린", "어스브라운"],
                "neutral": ["샌드베이지", "페블그레이"]
            }
        }
    
    def _extract_aesthetic_principles(
        self, 
        style: KoreanArchitecturalStyle, 
        user_input: str
    ) -> List[str]:
        """미학적 원칙 추출"""
        
        if style == KoreanArchitecturalStyle.TRADITIONAL_HANOK:
            return self.design_principles["traditional"]
        elif style == KoreanArchitecturalStyle.K_CONTEMPORARY:
            return self.design_principles["contemporary"]
        else:
            return self.design_principles["hybrid"]
    
    def _generate_hanok_recommendations(self) -> List[DesignRecommendation]:
        """한옥 디자인 권장사항"""
        return [
            DesignRecommendation(
                element=DesignElement.SPATIAL_LAYOUT,
                recommendation="마당을 중심으로 한 ㅁ자형 배치 적용",
                rationale="전통 한옥의 핵심 공간 구성 원리",
                cultural_context="가족 공동체 중심의 한국 전통 생활문화",
                implementation_details=["중앙 마당 확보", "안채-사랑채 분리", "대청마루 배치"],
                priority="high",
                style_compatibility=[KoreanArchitecturalStyle.TRADITIONAL_HANOK]
            ),
            DesignRecommendation(
                element=DesignElement.ROOF,
                recommendation="완만한 곡선의 처마와 기와지붕 적용",
                rationale="한국 건축의 독특한 곡선미와 자연 조화",
                cultural_context="하늘과 땅을 연결하는 한국적 우주관",
                implementation_details=["적정 처마 깊이", "자연스러운 곡선", "전통 기와 사용"],
                priority="high",
                style_compatibility=[KoreanArchitecturalStyle.TRADITIONAL_HANOK]
            )
        ]
    
    def _generate_contemporary_recommendations(self) -> List[DesignRecommendation]:
        """현대 건축 권장사항"""
        return [
            DesignRecommendation(
                element=DesignElement.SPATIAL_LAYOUT,
                recommendation="오픈 플랜과 유연한 공간 구성",
                rationale="현대 생활 패턴에 적합한 기능성",
                cultural_context="개인주의와 효율성을 중시하는 현대 문화",
                implementation_details=["큰 개방 공간", "가변형 파티션", "다목적 공간"],
                priority="high",
                style_compatibility=[KoreanArchitecturalStyle.K_CONTEMPORARY]
            ),
            DesignRecommendation(
                element=DesignElement.LIGHT,
                recommendation="자연광 최대 활용과 LED 조명 시스템",
                rationale="에너지 효율성과 웰빙 환경 조성",
                cultural_context="지속가능성을 중시하는 현대 가치관",
                implementation_details=["대형 창호", "천창 설치", "스마트 조명"],
                priority="medium",
                style_compatibility=[KoreanArchitecturalStyle.K_CONTEMPORARY]
            )
        ]
    
    def _generate_hybrid_recommendations(self) -> List[DesignRecommendation]:
        """하이브리드 스타일 권장사항"""
        return [
            DesignRecommendation(
                element=DesignElement.SPATIAL_LAYOUT,
                recommendation="전통 마당 개념의 현대적 해석",
                rationale="전통 공간 구성의 현대적 적용",
                cultural_context="전통과 현대의 조화로운 계승",
                implementation_details=["실내 정원", "아트리움", "테라스 정원"],
                priority="high",
                style_compatibility=[KoreanArchitecturalStyle.HANOK_MODERN]
            )
        ]
    
    def _generate_residential_recommendations(self, style: KoreanArchitecturalStyle) -> List[DesignRecommendation]:
        """주거용 건물 권장사항"""
        return [
            DesignRecommendation(
                element=DesignElement.SOCIAL_FUNCTION,
                recommendation="가족 공간과 개인 공간의 조화",
                rationale="한국 가족 문화의 현대적 적용",
                cultural_context="집단주의와 개인주의의 균형",
                implementation_details=["가족실", "개인 서재", "다목적실"],
                priority="medium",
                style_compatibility=[style]
            )
        ]
    
    def _generate_commercial_recommendations(self, style: KoreanArchitecturalStyle) -> List[DesignRecommendation]:
        """상업용 건물 권장사항"""
        return [
            DesignRecommendation(
                element=DesignElement.CIRCULATION,
                recommendation="직관적이고 편안한 동선 계획",
                rationale="고객 경험 최적화",
                cultural_context="한국인의 공간 인식과 행동 패턴",
                implementation_details=["명확한 진입부", "자연스러운 흐름", "휴게 공간"],
                priority="high",
                style_compatibility=[style]
            )
        ]
    
    def _generate_cultural_recommendations(self, style: KoreanArchitecturalStyle) -> List[DesignRecommendation]:
        """문화시설 권장사항"""
        return [
            DesignRecommendation(
                element=DesignElement.SYMBOLISM,
                recommendation="한국 문화의 상징성 강화",
                rationale="문화적 정체성 표현",
                cultural_context="한국 문화 유산의 현대적 해석",
                implementation_details=["전통 문양", "상징적 조형", "문화적 색채"],
                priority="high",
                style_compatibility=[style]
            )
        ]
    
    def _analyze_cultural_significance(self, style: KoreanArchitecturalStyle) -> str:
        """문화적 의미 분석"""
        significance_map = {
            KoreanArchitecturalStyle.TRADITIONAL_HANOK: "자연과의 조화, 가족 중심 공동체 문화, 계절 변화 수용",
            KoreanArchitecturalStyle.K_CONTEMPORARY: "글로벌 시대 한국 정체성, 현대적 효율성, 지속가능성",
            KoreanArchitecturalStyle.HANOK_MODERN: "전통의 현대적 계승, 문화적 연속성, 혁신과 보존의 조화"
        }
        return significance_map.get(style, "한국 건축의 다양성과 창의성")
    
    def _develop_adaptation_strategy(self, style: KoreanArchitecturalStyle, cultural_context: str) -> str:
        """적응 전략 개발"""
        if style == KoreanArchitecturalStyle.TRADITIONAL_HANOK:
            return "전통 요소의 기능적 현대화: 온돌 시스템의 현대적 적용, 한지의 현대적 해석"
        elif style == KoreanArchitecturalStyle.K_CONTEMPORARY:
            return "한국적 감성의 현대적 표현: 미니멀 디자인에 한국적 여백미 적용"
        else:
            return "선택적 전통 계승: 핵심 공간 구성은 유지하되 재료와 기술은 현대화"
    
    def _calculate_authenticity_score(self, style: KoreanArchitecturalStyle, cultural_context: str) -> float:
        """진정성 점수 계산"""
        if style == KoreanArchitecturalStyle.TRADITIONAL_HANOK:
            return 0.95
        elif style == KoreanArchitecturalStyle.HANOK_MODERN:
            return 0.75
        else:
            return 0.60
    
    def _calculate_relevance_score(self, style: KoreanArchitecturalStyle, cultural_context: str) -> float:
        """현대적 관련성 점수 계산"""
        if style == KoreanArchitecturalStyle.K_CONTEMPORARY:
            return 0.95
        elif style == KoreanArchitecturalStyle.HANOK_MODERN:
            return 0.85
        else:
            return 0.65
    
    def _get_location_considerations(self, location: str) -> List[str]:
        """지역별 고려사항"""
        location_map = {
            "서울": ["도시 밀도", "교통 접근성", "역사적 맥락"],
            "부산": ["해안 기후", "바람 대응", "산지 경사"],
            "제주": ["강풍 대응", "현무암 활용", "관광 기능"]
        }
        return location_map.get(location, ["일반적 지역 특성"])
    
    def _develop_lighting_strategy(self, style: KoreanArchitecturalStyle) -> str:
        """조명 전략 개발"""
        if style == KoreanArchitecturalStyle.TRADITIONAL_HANOK:
            return "자연광 중심의 부드러운 조명: 한지를 통한 확산광, 간접 조명"
        elif style == KoreanArchitecturalStyle.K_CONTEMPORARY:
            return "기능적 LED 조명: 태스크 라이팅, 앰비언트 라이팅, 스마트 제어"
        else:
            return "전통과 현대의 조화: 자연광 + 현대 조명 기술"
    
    def _get_sustainability_considerations(self, materials: List[str]) -> List[str]:
        """지속가능성 고려사항"""
        return [
            "로컬 재료 우선 사용",
            "재활용 가능 재료 선택",
            "생산 과정의 환경 영향 최소화",
            "내구성과 유지보수성 고려",
            "해체 시 재활용 가능성"
        ]


if __name__ == "__main__":
    # 테스트 실행
    async def test_architectural_design_specialist():
        print("=== 건축 디자인 전문가 AI 테스트 ===")
        
        agent = ArchitecturalDesignSpecialist()
        await agent.initialize()
        
        test_cases = [
            {
                "user_input": "전통 한옥 스타일의 게스트하우스를 설계해주세요",
                "building_type": "hospitality",
                "location": "서울"
            },
            {
                "user_input": "모던하면서도 한국적인 느낌의 사무빌딩",
                "building_type": "commercial",
                "location": "부산"
            },
            {
                "user_input": "친환경적이고 지속가능한 주택",
                "building_type": "residential",
                "location": "제주"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- 테스트 케이스 {i} ---")
            print(f"입력: {test_case['user_input']}")
            
            result = await agent.process_task_async(test_case)
            
            if result["success"]:
                analysis = result["analysis_result"]
                print(f"✅ 성공 (실행시간: {result['execution_time']:.3f}초)")
                print(f"주요 스타일: {analysis.primary_style.value}")
                print(f"디자인 패턴: {len(analysis.design_patterns)}개")
                print(f"권장사항: {len(analysis.design_recommendations)}개")
                print(f"문화적 진정성: {result['cultural_authenticity_score']:.2f}")
                print(f"현대적 관련성: {result['modern_relevance_score']:.2f}")
            else:
                print(f"❌ 실패: {result['error']}")
    
    asyncio.run(test_architectural_design_specialist())