"""
건축 이론 지식 베이스
===================

건축 설계 이론과 원칙에 대한 포괄적인 지식 시스템

@version 1.0
@author VIBA AI Team
@date 2025.07.06
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class ArchitecturalTheoryType(Enum):
    """건축 이론 유형"""
    PROPORTIONAL_SYSTEMS = "proportional_systems"
    SPATIAL_ORGANIZATION = "spatial_organization"
    FORM_COMPOSITION = "form_composition"
    MATERIAL_THEORY = "material_theory"
    ENVIRONMENTAL_DESIGN = "environmental_design"
    CULTURAL_CONTEXT = "cultural_context"


@dataclass
class ProportionalSystem:
    """비례 시스템"""
    name: str
    ratio: float
    description: str
    applications: List[str] = field(default_factory=list)
    cultural_origin: str = ""
    
    @classmethod
    def golden_ratio(cls):
        return cls(
            name="황금비 (Golden Ratio)",
            ratio=1.618,
            description="자연에서 발견되는 이상적인 비례, 고전 건축의 기본 원리",
            applications=["파사드 설계", "공간 분할", "창 비례", "기둥 간격"],
            cultural_origin="고대 그리스"
        )
    
    @classmethod
    def korean_traditional(cls):
        return cls(
            name="한국 전통 비례",
            ratio=1.414,  # √2 비례
            description="한옥에서 사용되는 전통적인 비례 체계",
            applications=["기둥 배치", "공간 구성", "지붕 기울기"],
            cultural_origin="한국 전통"
        )


@dataclass
class SpatialOrganizationPrinciple:
    """공간 구성 원리"""
    name: str
    description: str
    key_concepts: List[str] = field(default_factory=list)
    applications: Dict[str, List[str]] = field(default_factory=dict)


class ArchitecturalTheoryKnowledgeBase:
    """건축 이론 지식 베이스"""
    
    def __init__(self):
        self._initialize_knowledge()
    
    def _initialize_knowledge(self):
        """지식 베이스 초기화"""
        self.proportional_systems = self._load_proportional_systems()
        self.spatial_principles = self._load_spatial_principles()
        self.design_principles = self._load_design_principles()
        self.cultural_contexts = self._load_cultural_contexts()
        self.material_theories = self._load_material_theories()
    
    def _load_proportional_systems(self) -> Dict[str, ProportionalSystem]:
        """비례 시스템 로드"""
        return {
            "golden_ratio": ProportionalSystem.golden_ratio(),
            "korean_traditional": ProportionalSystem.korean_traditional(),
            "modular": ProportionalSystem(
                name="모듈러 시스템",
                ratio=1.0,
                description="모던 건축의 표준화된 모듈 기반 설계",
                applications=["현대 건축", "공업화 건축", "프리팹"],
                cultural_origin="20세기 모더니즘"
            ),
            "fibonacci": ProportionalSystem(
                name="피보나치 수열",
                ratio=1.618,
                description="자연의 성장 패턴을 반영한 비례 체계",
                applications=["유기적 형태", "스파이럴 계단", "자연친화 설계"],
                cultural_origin="수학적 원리"
            )
        }
    
    def _load_spatial_principles(self) -> Dict[str, SpatialOrganizationPrinciple]:
        """공간 구성 원리 로드"""
        return {
            "centralized": SpatialOrganizationPrinciple(
                name="중심형 구성",
                description="중앙의 핵심 공간을 중심으로 주변 공간들이 배치되는 구성",
                key_concepts=["중심성", "방사형 배치", "위계적 구성"],
                applications={
                    "종교건축": ["교회", "사원", "성당"],
                    "공공건축": ["박물관", "도서관", "시청"],
                    "주거건축": ["중정형 주택", "아트리움"]
                }
            ),
            "linear": SpatialOrganizationPrinciple(
                name="선형 구성",
                description="일직선상에 공간들이 연속적으로 배치되는 구성",
                key_concepts=["연속성", "방향성", "흐름"],
                applications={
                    "교육건축": ["학교 복도", "대학 캠퍼스"],
                    "상업건축": ["쇼핑몰", "갤러리"],
                    "교통건축": ["공항", "기차역"]
                }
            ),
            "clustered": SpatialOrganizationPrinciple(
                name="군집형 구성",
                description="기능이나 성격이 유사한 공간들이 그룹을 이루는 구성",
                key_concepts=["그룹핑", "기능적 분화", "다양성"],
                applications={
                    "주거건축": ["아파트 단지", "타운하우스"],
                    "업무건축": ["오피스 빌딩", "연구소"],
                    "문화건축": ["복합문화시설", "대학"]
                }
            ),
            "grid": SpatialOrganizationPrinciple(
                name="격자형 구성",
                description="규칙적인 격자 체계에 따라 공간이 배치되는 구성",
                key_concepts=["질서", "효율성", "표준화"],
                applications={
                    "도시계획": ["맨하탄 그리드", "신도시"],
                    "업무건축": ["사무용 빌딩", "공장"],
                    "주거건축": ["아파트", "연립주택"]
                }
            )
        }
    
    def _load_design_principles(self) -> Dict[str, Dict[str, Any]]:
        """설계 원칙 로드"""
        return {
            "proportion": {
                "name": "비례 (Proportion)",
                "description": "부분과 전체, 각 요소 간의 적절한 크기 관계",
                "guidelines": [
                    "황금비 활용",
                    "인체 척도 고려",
                    "기능에 맞는 크기",
                    "시각적 균형"
                ],
                "examples": ["파르테논 신전", "한국 전통 한옥", "르 코르뷔지에 주택"]
            },
            "scale": {
                "name": "스케일 (Scale)",
                "description": "인간의 크기나 다른 기준과의 상대적 크기 관계",
                "guidelines": [
                    "인간 중심 스케일",
                    "건물 용도별 적정 스케일",
                    "환경과의 조화",
                    "위압감 방지"
                ],
                "examples": ["고딕 성당의 수직성", "일본 차실의 친밀감", "브루탈리즘의 거대함"]
            },
            "rhythm": {
                "name": "리듬 (Rhythm)",
                "description": "반복, 변화, 강조 등을 통한 시각적 리듬감",
                "guidelines": [
                    "규칙적 반복",
                    "점진적 변화",
                    "강조와 휴지",
                    "동적 흐름"
                ],
                "examples": ["고전 기둥 배치", "모던 커튼월", "한옥 처마선"]
            },
            "balance": {
                "name": "균형 (Balance)",
                "description": "대칭 또는 비대칭을 통한 시각적 안정감",
                "guidelines": [
                    "정적 균형",
                    "동적 균형",
                    "시각적 무게 고려",
                    "전체적 조화"
                ],
                "examples": ["팔라디오 빌라", "라이트의 낙수장", "한국 불국사"]
            }
        }
    
    def _load_cultural_contexts(self) -> Dict[str, Dict[str, Any]]:
        """문화적 맥락 로드"""
        return {
            "korean_traditional": {
                "name": "한국 전통 건축",
                "core_principles": [
                    "자연과의 조화 (天人合一)",
                    "음양오행 사상",
                    "풍수지리 적용",
                    "절제된 아름다움"
                ],
                "spatial_concepts": {
                    "중정": "가족의 중심 공간, 하늘과 땅의 연결",
                    "마당": "자연과 건축의 완충 공간",
                    "처마": "내외부의 중간 영역",
                    "온돌": "바닥 난방을 통한 수평적 생활"
                },
                "materials": ["목재", "기와", "한지", "흙", "돌"],
                "colors": ["단청", "백색", "회색", "자연색"]
            },
            "western_classical": {
                "name": "서구 고전 건축",
                "core_principles": [
                    "질서와 비례",
                    "기하학적 완전성",
                    "기둥과 보의 체계",
                    "장식과 구조의 통합"
                ],
                "spatial_concepts": {
                    "대칭": "중심축을 기준으로 한 균형",
                    "위계": "공간의 중요도에 따른 차별화",
                    "열주": "리듬감 있는 기둥 배치",
                    "아치": "구조와 미학의 결합"
                },
                "materials": ["대리석", "화강암", "벽돌", "석고"],
                "colors": ["백색", "크림색", "회색", "금색"]
            },
            "modern": {
                "name": "모던 건축",
                "core_principles": [
                    "기능이 형태를 결정",
                    "장식의 제거",
                    "새로운 재료와 기술",
                    "보편적 공간"
                ],
                "spatial_concepts": {
                    "자유평면": "구조로부터 자유로운 공간 구성",
                    "흐르는 공간": "실내외의 연속성",
                    "투명성": "유리를 통한 개방감",
                    "기하학": "단순하고 명확한 형태"
                },
                "materials": ["철근콘크리트", "유리", "강철", "플라스틱"],
                "colors": ["백색", "회색", "검정", "원색"]
            }
        }
    
    def _load_material_theories(self) -> Dict[str, Dict[str, Any]]:
        """재료 이론 로드"""
        return {
            "structural_expression": {
                "name": "구조의 표현",
                "description": "재료의 구조적 특성을 건축적으로 표현",
                "principles": [
                    "재료의 고유 특성 활용",
                    "구조 시스템의 가시화",
                    "하중 전달의 명확성",
                    "접합부의 정직한 표현"
                ],
                "examples": {
                    "목구조": "한옥의 목조 가구식 구조",
                    "철골구조": "에펠탑의 강철 트러스",
                    "콘크리트": "안도 타다오의 노출 콘크리트"
                }
            },
            "tactile_quality": {
                "name": "촉각적 품질",
                "description": "재료의 질감이 주는 공간적 경험",
                "principles": [
                    "표면 질감의 다양성",
                    "빛과 그림자의 효과",
                    "온도감과 친밀성",
                    "시간의 흔적 표현"
                ],
                "examples": {
                    "거친 콘크리트": "브루탈리즘의 강인함",
                    "부드러운 목재": "스칸디나비아의 따뜻함",
                    "차가운 금속": "하이테크의 미래성"
                }
            }
        }
    
    def get_proportional_system(self, style: str) -> Optional[ProportionalSystem]:
        """스타일에 맞는 비례 시스템 반환"""
        style_mapping = {
            "classical": "golden_ratio",
            "traditional": "korean_traditional",
            "hanok": "korean_traditional",
            "modern": "modular",
            "contemporary": "modular",
            "organic": "fibonacci"
        }
        
        system_key = style_mapping.get(style.lower(), "golden_ratio")
        return self.proportional_systems.get(system_key)
    
    def get_spatial_organization(self, building_type: str, style: str) -> Optional[SpatialOrganizationPrinciple]:
        """건물 유형과 스타일에 맞는 공간 구성 원리 반환"""
        
        # 건물 유형별 우선 공간 구성
        type_mapping = {
            "museum": "centralized",
            "library": "centralized", 
            "school": "linear",
            "office": "grid",
            "residential": "clustered",
            "house": "centralized",
            "cafe": "clustered",
            "restaurant": "linear"
        }
        
        # 스타일별 수정
        if style.lower() in ["hanok", "traditional"]:
            return self.spatial_principles.get("centralized")
        elif style.lower() in ["modern", "contemporary"]:
            return self.spatial_principles.get("grid")
        
        principle_key = type_mapping.get(building_type.lower(), "centralized")
        return self.spatial_principles.get(principle_key)
    
    def get_design_principles(self, style: str) -> List[str]:
        """스타일에 적합한 설계 원칙들 반환"""
        style_principles = {
            "classical": ["proportion", "scale", "balance"],
            "traditional": ["proportion", "balance"],
            "hanok": ["proportion", "balance"],
            "modern": ["scale", "rhythm"],
            "contemporary": ["rhythm", "balance"],
            "minimalist": ["proportion", "balance"]
        }
        
        return style_principles.get(style.lower(), ["proportion", "balance"])
    
    def get_cultural_context(self, style: str) -> Optional[Dict[str, Any]]:
        """스타일의 문화적 맥락 반환"""
        style_mapping = {
            "hanok": "korean_traditional",
            "traditional": "korean_traditional",
            "classical": "western_classical",
            "modern": "modern",
            "contemporary": "modern"
        }
        
        context_key = style_mapping.get(style.lower())
        return self.cultural_contexts.get(context_key) if context_key else None
    
    def apply_theory_to_design(self, building_type: str, style: str, requirements: List[str]) -> Dict[str, Any]:
        """설계에 이론 적용"""
        
        # 비례 시스템 선택
        proportional_system = self.get_proportional_system(style)
        
        # 공간 구성 원리 선택
        spatial_organization = self.get_spatial_organization(building_type, style)
        
        # 설계 원칙 선택
        design_principles = self.get_design_principles(style)
        
        # 문화적 맥락 적용
        cultural_context = self.get_cultural_context(style)
        
        return {
            "proportional_system": {
                "name": proportional_system.name if proportional_system else "기본 비례",
                "ratio": proportional_system.ratio if proportional_system else 1.618,
                "applications": proportional_system.applications if proportional_system else []
            },
            "spatial_organization": {
                "type": spatial_organization.name if spatial_organization else "중심형 구성",
                "key_concepts": spatial_organization.key_concepts if spatial_organization else [],
                "recommendations": self._generate_spatial_recommendations(building_type, style)
            },
            "design_principles": design_principles,
            "cultural_context": cultural_context,
            "material_guidelines": self._get_material_guidelines(style),
            "theoretical_framework": self._generate_theoretical_framework(building_type, style, requirements)
        }
    
    def _generate_spatial_recommendations(self, building_type: str, style: str) -> List[str]:
        """공간 구성 권장사항 생성"""
        recommendations = []
        
        if building_type.lower() == "cafe":
            recommendations.extend([
                "입구에서 내부가 한눈에 들어오는 개방적 구성",
                "다양한 크기의 좌석 공간 마련",
                "주방과 서빙 공간의 효율적 배치",
                "자연광을 최대한 활용할 수 있는 창가 배치"
            ])
        elif building_type.lower() in ["office", "사무실"]:
            recommendations.extend([
                "업무 효율을 위한 명확한 동선 계획",
                "개방형과 폐쇄형 공간의 적절한 조화",
                "휴게 공간과 업무 공간의 분리",
                "자연 채광과 환기 고려"
            ])
        elif building_type.lower() in ["house", "주택"]:
            if style.lower() in ["hanok", "traditional"]:
                recommendations.extend([
                    "중정을 중심으로 한 배치",
                    "안채, 사랑채, 행랑채의 위계적 구성",
                    "자연과의 조화를 위한 마당 공간",
                    "처마를 통한 내외부 공간의 연결"
                ])
            else:
                recommendations.extend([
                    "공용 공간과 사적 공간의 분리",
                    "가족 구성원 간의 프라이버시 고려",
                    "실내외 공간의 연속성",
                    "효율적인 수납 공간 계획"
                ])
        
        return recommendations
    
    def _get_material_guidelines(self, style: str) -> Dict[str, List[str]]:
        """스타일별 재료 가이드라인"""
        material_guidelines = {
            "hanok": {
                "primary": ["목재 (소나무, 참나무)", "기와", "한지"],
                "secondary": ["돌", "흙", "황토"],
                "finishes": ["단청", "옻칠", "들기름"]
            },
            "modern": {
                "primary": ["철근콘크리트", "유리", "강철"],
                "secondary": ["알루미늄", "플라스틱", "복합재료"],
                "finishes": ["노출콘크리트", "스테인리스", "화이트 페인트"]
            },
            "traditional": {
                "primary": ["목재", "석재", "점토"],
                "secondary": ["기와", "한지", "대나무"],
                "finishes": ["천연 오일", "라임 몰탈", "전통 안료"]
            },
            "contemporary": {
                "primary": ["콘크리트", "유리", "금속"],
                "secondary": ["목재", "세라믹", "복합재료"],
                "finishes": ["텍스처 콘크리트", "파우더 코팅", "천연석"]
            }
        }
        
        return material_guidelines.get(style.lower(), material_guidelines["modern"])
    
    def _generate_theoretical_framework(self, building_type: str, style: str, requirements: List[str]) -> Dict[str, Any]:
        """이론적 프레임워크 생성"""
        
        framework = {
            "primary_theory": self._get_primary_theory(style),
            "secondary_theories": self._get_secondary_theories(building_type, requirements),
            "application_strategy": self._get_application_strategy(building_type, style),
            "evaluation_criteria": self._get_evaluation_criteria(style)
        }
        
        return framework
    
    def _get_primary_theory(self, style: str) -> str:
        """주요 이론 선택"""
        theory_mapping = {
            "hanok": "한국 전통 건축 이론 (천인합일 사상)",
            "classical": "고전 건축 이론 (비트루비우스 3원칙)",
            "modern": "모던 건축 이론 (형태는 기능을 따른다)",
            "contemporary": "포스트모던 이론 (맥락주의)",
            "sustainable": "생태 건축 이론 (환경과의 조화)"
        }
        
        return theory_mapping.get(style.lower(), "통합 설계 이론")
    
    def _get_secondary_theories(self, building_type: str, requirements: List[str]) -> List[str]:
        """보조 이론들 선택"""
        theories = []
        
        # 건물 유형별 이론
        if building_type.lower() in ["cafe", "restaurant"]:
            theories.append("상업 공간 설계 이론")
            theories.append("고객 행동 패턴 이론")
        elif building_type.lower() in ["office", "사무실"]:
            theories.append("업무 환경 설계 이론")
            theories.append("조직 공간 이론")
        elif building_type.lower() in ["house", "주택"]:
            theories.append("주거 공간 이론")
            theories.append("가족 생활 패턴 이론")
        
        # 요구사항별 이론
        for req in requirements:
            if "친환경" in req or "sustainable" in req.lower():
                theories.append("지속가능 설계 이론")
            if "에너지" in req:
                theories.append("건물 에너지 효율 이론")
            if "접근성" in req or "장애인" in req:
                theories.append("유니버설 디자인 이론")
        
        return list(set(theories))  # 중복 제거
    
    def _get_application_strategy(self, building_type: str, style: str) -> List[str]:
        """적용 전략"""
        strategy = [
            "1단계: 대지 분석 및 맥락 이해",
            "2단계: 기능 프로그램 수립",
            "3단계: 공간 구성 개념 설정",
            "4단계: 형태 생성 및 비례 적용",
            "5단계: 재료 및 디테일 계획",
            "6단계: 성능 검증 및 최적화"
        ]
        
        return strategy
    
    def _get_evaluation_criteria(self, style: str) -> List[str]:
        """평가 기준"""
        base_criteria = [
            "기능적 효율성",
            "공간의 질",
            "구조적 안정성",
            "경제성",
            "시공성"
        ]
        
        style_specific = {
            "hanok": ["전통성", "자연과의 조화"],
            "modern": ["혁신성", "기능주의"],
            "sustainable": ["환경 성능", "에너지 효율"],
            "contemporary": ["창의성", "맥락성"]
        }
        
        criteria = base_criteria.copy()
        if style.lower() in style_specific:
            criteria.extend(style_specific[style.lower()])
        
        return criteria