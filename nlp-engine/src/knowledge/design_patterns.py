"""
건축 설계 패턴 라이브러리
========================

건축 설계에서 자주 사용되는 검증된 설계 패턴들의 체계적 분류 및 적용 가이드

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


class PatternCategory(Enum):
    """설계 패턴 카테고리"""
    SPATIAL_ORGANIZATION = "spatial_organization"  # 공간 구성
    CIRCULATION = "circulation"                    # 동선
    STRUCTURAL = "structural"                      # 구조
    ENVIRONMENTAL = "environmental"                # 환경
    FUNCTIONAL = "functional"                      # 기능
    AESTHETIC = "aesthetic"                        # 미학


class ContextType(Enum):
    """적용 맥락"""
    URBAN = "urban"                # 도시
    SUBURBAN = "suburban"          # 교외
    RURAL = "rural"               # 농촌
    COMMERCIAL = "commercial"      # 상업
    RESIDENTIAL = "residential"    # 주거
    INSTITUTIONAL = "institutional" # 기관
    CULTURAL = "cultural"         # 문화


@dataclass 
class DesignPattern:
    """설계 패턴"""
    name: str
    category: PatternCategory
    description: str
    problem: str                                    # 해결하는 문제
    solution: str                                   # 해결 방법
    context: List[ContextType] = field(default_factory=list)
    building_types: List[str] = field(default_factory=list)
    advantages: List[str] = field(default_factory=list)
    disadvantages: List[str] = field(default_factory=list)
    variations: List[str] = field(default_factory=list)
    examples: List[Dict[str, str]] = field(default_factory=list)
    guidelines: List[str] = field(default_factory=list)
    related_patterns: List[str] = field(default_factory=list)


class DesignPatternLibrary:
    """설계 패턴 라이브러리"""
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
        self.pattern_combinations = self._initialize_combinations()
    
    def _initialize_patterns(self) -> Dict[str, DesignPattern]:
        """패턴 라이브러리 초기화"""
        patterns = {}
        
        # 공간 구성 패턴들
        patterns.update(self._create_spatial_patterns())
        
        # 동선 패턴들
        patterns.update(self._create_circulation_patterns())
        
        # 구조 패턴들
        patterns.update(self._create_structural_patterns())
        
        # 환경 패턴들
        patterns.update(self._create_environmental_patterns())
        
        # 기능 패턴들  
        patterns.update(self._create_functional_patterns())
        
        # 미학 패턴들
        patterns.update(self._create_aesthetic_patterns())
        
        return patterns
    
    def _create_spatial_patterns(self) -> Dict[str, DesignPattern]:
        """공간 구성 패턴 생성"""
        return {
            "courtyard": DesignPattern(
                name="중정 (Courtyard)",
                category=PatternCategory.SPATIAL_ORGANIZATION,
                description="건물 내부에 외부 공간을 포함하여 자연과 건축을 연결하는 패턴",
                problem="밀도 높은 도시에서 자연과의 연결, 프라이버시 확보, 채광 및 환기 문제",
                solution="건물 중앙 또는 여러 곳에 중정을 배치하여 내외부 공간의 연속성 확보",
                context=[ContextType.URBAN, ContextType.RESIDENTIAL, ContextType.INSTITUTIONAL],
                building_types=["주택", "사무소", "학교", "병원", "박물관"],
                advantages=[
                    "자연 채광과 환기 개선",
                    "프라이버시 확보",
                    "내외부 공간의 연속성",
                    "미기후 조절",
                    "정신적 안정감 제공"
                ],
                disadvantages=[
                    "대지 활용도 감소",
                    "구조적 복잡성 증가",
                    "유지관리 비용 증가"
                ],
                variations=[
                    "단일 중정형",
                    "복수 중정형", 
                    "선큰 가든형",
                    "아트리움형"
                ],
                examples=[
                    {"name": "한국 전통 한옥", "location": "한국", "period": "조선시대"},
                    {"name": "알람브라 궁전", "location": "스페인", "period": "14세기"},
                    {"name": "루이스 칸 솔크 연구소", "location": "미국", "period": "1965년"}
                ],
                guidelines=[
                    "중정 크기는 둘러싼 건물 높이의 1-2배",
                    "남향 배치로 일조 확보",
                    "우수 처리 시설 필수",
                    "내부 공간과의 시각적 연결 고려"
                ],
                related_patterns=["garden_integration", "natural_ventilation"]
            ),
            
            "cluster": DesignPattern(
                name="클러스터 (Cluster)",
                category=PatternCategory.SPATIAL_ORGANIZATION,
                description="기능이나 성격이 유사한 공간들을 그룹화하는 패턴",
                problem="대규모 복합 시설에서 기능 분화와 연결의 균형",
                solution="기능별로 공간을 그룹화하고 중심 공간으로 연결",
                context=[ContextType.INSTITUTIONAL, ContextType.COMMERCIAL, ContextType.RESIDENTIAL],
                building_types=["대학", "병원", "쇼핑센터", "아파트 단지"],
                advantages=[
                    "기능적 효율성",
                    "단계적 확장 가능",
                    "다양성과 통일성 조화",
                    "관리 효율성"
                ],
                disadvantages=[
                    "전체적 통합감 부족 위험",
                    "동선의 복잡성",
                    "불균등한 이용도"
                ],
                variations=[
                    "방사형 클러스터",
                    "선형 클러스터",
                    "격자형 클러스터",
                    "유기적 클러스터"
                ],
                examples=[
                    {"name": "MIT 캠퍼스", "location": "미국", "period": "20세기"},
                    {"name": "반포 주공아파트", "location": "한국", "period": "1970년대"}
                ],
                guidelines=[
                    "클러스터 간 명확한 경계 설정",
                    "중심 공간의 접근성 확보",
                    "각 클러스터의 독립성 유지",
                    "단계적 확장 계획 수립"
                ],
                related_patterns=["linear_organization", "central_spine"]
            ),
            
            "terraced": DesignPattern(
                name="단계형 (Terraced)",
                category=PatternCategory.SPATIAL_ORGANIZATION,
                description="경사지를 활용하여 단계적으로 공간을 배치하는 패턴",
                problem="경사지에서의 건축, 일조권 확보, 조망권 보장",
                solution="지형을 따라 단계적으로 매스를 배치하여 모든 공간에 조망과 일조 확보",
                context=[ContextType.SUBURBAN, ContextType.RESIDENTIAL],
                building_types=["주거단지", "리조트", "대학", "전시장"],
                advantages=[
                    "모든 층에 조망권 확보",
                    "지형과의 조화",
                    "옥상 정원 활용 가능",
                    "자연스러운 단지 구성"
                ],
                disadvantages=[
                    "구조비 증가",
                    "방수 문제",
                    "접근성 제한"
                ],
                variations=[
                    "연속 테라스형",
                    "분절 테라스형",
                    "나선형 테라스",
                    "불규칙 테라스"
                ],
                examples=[
                    {"name": "Habitat 67", "location": "캐나다", "period": "1967년"},
                    {"name": "갈매기아파트", "location": "한국", "period": "1980년대"}
                ],
                guidelines=[
                    "각 단의 후퇴 거리 3m 이상",
                    "배수 시설 충분히 확보",
                    "상부층 하중 하부로 전달",
                    "조경과 건축의 통합 설계"
                ],
                related_patterns=["slope_adaptation", "green_roof"]
            )
        }
    
    def _create_circulation_patterns(self) -> Dict[str, DesignPattern]:
        """동선 패턴 생성"""
        return {
            "central_spine": DesignPattern(
                name="중앙 통로 (Central Spine)",
                category=PatternCategory.CIRCULATION,
                description="건물 중앙에 주 동선을 배치하고 양측에 기능 공간을 배치하는 패턴",
                problem="긴 건물에서의 효율적인 접근과 방향성 확보",
                solution="중앙에 주 복도를 배치하고 양측에 실을 배치하여 명확한 동선 체계 구축",
                context=[ContextType.INSTITUTIONAL, ContextType.COMMERCIAL],
                building_types=["학교", "사무소", "병원", "호텔"],
                advantages=[
                    "명확한 방향성",
                    "효율적인 공간 활용",
                    "단계적 확장 용이",
                    "관리 동선 효율적"
                ],
                disadvantages=[
                    "양측 채광의 불균형",
                    "복도의 단조로움",
                    "프라이버시 제한"
                ],
                variations=[
                    "직선형 스파인",
                    "곡선형 스파인",
                    "분기형 스파인",
                    "복층 스파인"
                ],
                examples=[
                    {"name": "알바 알토 핀란디아 홀", "location": "핀란드", "period": "1971년"},
                    {"name": "서울대학교 중앙도서관", "location": "한국", "period": "1974년"}
                ],
                guidelines=[
                    "복도 폭 최소 2.4m 확보",
                    "50m마다 휴게 공간 배치",
                    "자연 채광 적극 도입",
                    "끝단에 특별한 공간 배치"
                ],
                related_patterns=["double_loaded_corridor", "atrium_circulation"]
            ),
            
            "ring_circulation": DesignPattern(
                name="순환 동선 (Ring Circulation)",
                category=PatternCategory.CIRCULATION,
                description="원형 또는 고리형 동선으로 연속적인 이동이 가능한 패턴",
                problem="전시나 관람에서 연속적이고 방향성 있는 이동 필요",
                solution="고리형 동선을 통해 시작점으로 돌아오는 연속적 경험 제공",
                context=[ContextType.CULTURAL, ContextType.COMMERCIAL],
                building_types=["박물관", "갤러리", "쇼핑센터", "전시장"],
                advantages=[
                    "연속적인 경험 제공",
                    "누락 없는 관람",
                    "자연스러운 흐름",
                    "다양한 경로 선택"
                ],
                disadvantages=[
                    "역동선 발생 가능",
                    "혼잡 구간 발생",
                    "공간 효율성 저하"
                ],
                variations=[
                    "원형 순환",
                    "타원형 순환", 
                    "8자형 순환",
                    "복층 순환"
                ],
                examples=[
                    {"name": "구겐하임 뉴욕", "location": "미국", "period": "1959년"},
                    {"name": "국립현대미술관 과천", "location": "한국", "period": "1986년"}
                ],
                guidelines=[
                    "시작점과 끝점 명확히 표시",
                    "우회 경로 반드시 확보",
                    "휴게 공간 적절히 배치",
                    "역방향 진입 방지 설계"
                ],
                related_patterns=["spiral_circulation", "gallery_sequence"]
            ),
            
            "vertical_circulation": DesignPattern(
                name="수직 동선 (Vertical Circulation)",
                category=PatternCategory.CIRCULATION,
                description="계단, 엘리베이터 등을 건축적 요소로 강조하는 패턴",
                problem="고층 건물에서 수직 이동의 효율성과 건축적 표현",
                solution="수직 동선 요소를 건축의 핵심 요소로 디자인하여 공간의 중심축 형성",
                context=[ContextType.URBAN, ContextType.INSTITUTIONAL],
                building_types=["사무소", "박물관", "복합시설", "주상복합"],
                advantages=[
                    "건축적 표현력 증대",
                    "공간의 드라마틱한 연결",
                    "층간 연계성 강화",
                    "건물 내 랜드마크 역할"
                ],
                disadvantages=[
                    "공간 효율성 감소",
                    "시공비 증가",
                    "유지관리 복잡"
                ],
                variations=[
                    "나선형 계단",
                    "시스어 스테어",
                    "애트리움 엘리베이터",
                    "스카이 브리지"
                ],
                examples=[
                    {"name": "퐁피두 센터", "location": "프랑스", "period": "1977년"},
                    {"name": "동대문디자인플라자", "location": "한국", "period": "2014년"}
                ],
                guidelines=[
                    "안전 규정 철저히 준수",
                    "비상 계단 별도 확보",
                    "자연 채광 최대한 활용",
                    "이용자 편의 시설 배치"
                ],
                related_patterns=["atrium_space", "skylight_integration"]
            )
        }
    
    def _create_structural_patterns(self) -> Dict[str, DesignPattern]:
        """구조 패턴 생성"""
        return {
            "post_and_beam": DesignPattern(
                name="기둥-보 시스템 (Post and Beam)",
                category=PatternCategory.STRUCTURAL,
                description="기둥과 보로 구성된 가구식 구조 시스템",
                problem="자유로운 공간 구성과 구조적 안정성의 조화",
                solution="기둥과 보의 격자 시스템으로 구조를 해결하고 내부는 자유롭게 구성",
                context=[ContextType.RESIDENTIAL, ContextType.INSTITUTIONAL],
                building_types=["주택", "사무소", "학교", "공장"],
                advantages=[
                    "공간 구성의 자유도",
                    "시공의 단순성",
                    "재료 효율성",
                    "확장성"
                ],
                disadvantages=[
                    "기둥에 의한 공간 제약",
                    "대공간 구현 어려움",
                    "횡력 저항 보강 필요"
                ],
                variations=[
                    "목조 가구식",
                    "철골 라멘", 
                    "PC 구조",
                    "하이브리드 시스템"
                ],
                examples=[
                    {"name": "한국 전통 한옥", "location": "한국", "period": "조선시대"},
                    {"name": "미스 반 데어 로에 파빌리온", "location": "독일", "period": "1929년"}
                ],
                guidelines=[
                    "기둥 간격은 구조재 성능에 맞게",
                    "접합부 디테일 정교하게 설계",
                    "수평력 저항 요소 추가",
                    "기둥 위치와 공간 계획 통합"
                ],
                related_patterns=["modular_construction", "open_plan"]
            ),
            
            "shell_structure": DesignPattern(
                name="셸 구조 (Shell Structure)",
                category=PatternCategory.STRUCTURAL,
                description="곡면 형태로 하중을 지지하는 구조 시스템",
                problem="대공간 구현과 구조적 효율성, 형태의 자유도",
                solution="곡면의 기하학적 특성을 활용하여 효율적으로 하중 지지",
                context=[ContextType.INSTITUTIONAL, ContextType.CULTURAL],
                building_types=["체육관", "공연장", "전시장", "종교건축"],
                advantages=[
                    "대공간 무주 공간",
                    "재료 효율성",
                    "독특한 공간감",
                    "구조와 형태의 통일"
                ],
                disadvantages=[
                    "복잡한 설계와 시공",
                    "높은 시공비",
                    "유지관리 어려움",
                    "공간 활용의 제약"
                ],
                variations=[
                    "돔 구조",
                    "바렐 볼트",
                    "하이퍼볼릭 패러볼로이드",
                    "그리드 셸"
                ],
                examples=[
                    {"name": "시드니 오페라 하우스", "location": "호주", "period": "1973년"},
                    {"name": "서울올림픽 체조경기장", "location": "한국", "period": "1986년"}
                ],
                guidelines=[
                    "곡면의 연속성 유지",
                    "경계 조건 신중히 설계",
                    "시공 순서 면밀히 계획",
                    "구조 해석 정밀하게 수행"
                ],
                related_patterns=["vault_system", "tensile_structure"]
            )
        }
    
    def _create_environmental_patterns(self) -> Dict[str, DesignPattern]:
        """환경 패턴 생성"""
        return {
            "passive_solar": DesignPattern(
                name="패시브 솔라 (Passive Solar)",
                category=PatternCategory.ENVIRONMENTAL,
                description="태양 에너지를 기계 장치 없이 자연적으로 활용하는 패턴",
                problem="에너지 효율성과 쾌적한 실내 환경 조성",
                solution="건물 배치, 창호, 단열 등을 통해 태양 에너지를 효과적으로 활용",
                context=[ContextType.RESIDENTIAL, ContextType.INSTITUTIONAL],
                building_types=["주택", "사무소", "학교", "도서관"],
                advantages=[
                    "에너지 비용 절감",
                    "환경 친화적",
                    "자연 채광 극대화",
                    "건강한 실내 환경"
                ],
                disadvantages=[
                    "계절별 성능 편차",
                    "설계 복잡성 증가",
                    "초기 비용 증가",
                    "주변 환경 의존성"
                ],
                variations=[
                    "직접 취득형",
                    "간접 취득형",
                    "트롬월 시스템",
                    "태양광 통합형"
                ],
                examples=[
                    {"name": "마이클 레이놀즈 어스십", "location": "미국", "period": "1970년대"},
                    {"name": "노마드 건축 제로 에너지 하우스", "location": "한국", "period": "2010년대"}
                ],
                guidelines=[
                    "남향 위주 창호 배치",
                    "여름철 차양 장치 필수",
                    "충분한 단열 성능 확보",
                    "축열 성능 고려한 재료 선택"
                ],
                related_patterns=["natural_ventilation", "thermal_mass"]
            ),
            
            "green_roof": DesignPattern(
                name="녹색 지붕 (Green Roof)",
                category=PatternCategory.ENVIRONMENTAL, 
                description="건물 지붕에 식생을 조성하여 환경 성능을 향상시키는 패턴",
                problem="도시 열섬 현상, 우수 처리, 생태 환경 복원",
                solution="지붕면을 활용한 녹지 조성으로 환경적 이익과 공간적 가치 창출",
                context=[ContextType.URBAN, ContextType.INSTITUTIONAL],
                building_types=["사무소", "주상복합", "학교", "복합시설"],
                advantages=[
                    "단열 성능 향상",
                    "우수 유출 지연",
                    "도시 열섬 완화",
                    "생태 서식지 제공",
                    "추가 활용 공간 확보"
                ],
                disadvantages=[
                    "구조 하중 증가",
                    "방수 시설 강화 필요",
                    "유지관리 비용",
                    "초기 설치비 증가"
                ],
                variations=[
                    "집약형 녹색지붕",
                    "조방형 녹색지붕",
                    "세덤 지붕",
                    "정원형 지붕"
                ],
                examples=[
                    {"name": "아크로스 후쿠오카", "location": "일본", "period": "1995년"},
                    {"name": "서울시청 신청사", "location": "한국", "period": "2012년"}
                ],
                guidelines=[
                    "하중 검토 필수 실시",
                    "3중 방수 시스템 적용",
                    "배수 시설 충분히 확보",
                    "접근 및 유지관리 동선 확보"
                ],
                related_patterns=["rainwater_harvesting", "urban_agriculture"]
            )
        }
    
    def _create_functional_patterns(self) -> Dict[str, DesignPattern]:
        """기능 패턴 생성"""
        return {
            "mixed_use": DesignPattern(
                name="복합 기능 (Mixed Use)",
                category=PatternCategory.FUNCTIONAL,
                description="하나의 건물이나 단지에 여러 기능을 통합하는 패턴",
                problem="토지 효율성, 도시 활력, 생활 편의성 향상",
                solution="주거, 상업, 업무, 문화 기능을 수직 또는 수평적으로 통합",
                context=[ContextType.URBAN, ContextType.COMMERCIAL],
                building_types=["주상복합", "복합쇼핑몰", "혼합개발단지"],
                advantages=[
                    "토지 이용 효율성",
                    "도시 활력 증진",
                    "교통량 분산",
                    "24시간 활동 가능",
                    "시너지 효과"
                ],
                disadvantages=[
                    "기능 간 충돌 위험",
                    "관리 복잡성",
                    "법규 적용 복잡",
                    "소음, 진동 문제"
                ],
                variations=[
                    "수직 복합",
                    "수평 복합",
                    "블록 복합",
                    "타워형 복합"
                ],
                examples=[
                    {"name": "록펠러 센터", "location": "미국", "period": "1930년대"},
                    {"name": "여의도 IFC몰", "location": "한국", "period": "2012년"}
                ],
                guidelines=[
                    "기능 간 완충 공간 확보",
                    "독립적 출입구 계획",
                    "서비스 동선 분리",
                    "소음 차단 대책 수립"
                ],
                related_patterns=["podium_tower", "urban_integration"]
            ),
            
            "flexible_space": DesignPattern(
                name="가변 공간 (Flexible Space)",
                category=PatternCategory.FUNCTIONAL,
                description="용도 변경이나 공간 확장이 용이한 공간 구성 패턴",
                problem="변화하는 사용자 요구에 대한 적응성 필요",
                solution="가변 벽체, 모듈러 시스템 등을 활용한 변화 가능한 공간 구성",
                context=[ContextType.INSTITUTIONAL, ContextType.COMMERCIAL],
                building_types=["사무소", "전시장", "교육시설", "커뮤니티센터"],
                advantages=[
                    "사용자 요구 변화 대응",
                    "공간 효율성 극대화",
                    "건물 수명 연장",
                    "운영비 절감"
                ],
                disadvantages=[
                    "초기 비용 증가",
                    "구조적 제약",
                    "설비 계획 복잡",
                    "음향 문제"
                ],
                variations=[
                    "가변 벽체형",
                    "모듈러 시스템",
                    "슬라이딩 파티션",
                    "폴딩 도어"
                ],
                examples=[
                    {"name": "헤르만 헤르츠베르거 센트럴 베헤르", "location": "네덜란드", "period": "1972년"},
                    {"name": "삼성동 코엑스", "location": "한국", "period": "1988년"}
                ],
                guidelines=[
                    "최대 개방 시 구조 안전성 확보",
                    "설비 통합 시스템 구축",
                    "바닥과 천장 마감재 통일",
                    "수납 공간 충분히 확보"
                ],
                related_patterns=["modular_construction", "universal_design"]
            )
        }
    
    def _create_aesthetic_patterns(self) -> Dict[str, DesignPattern]:
        """미학 패턴 생성"""
        return {
            "rhythm_and_repetition": DesignPattern(
                name="리듬과 반복 (Rhythm and Repetition)",
                category=PatternCategory.AESTHETIC,
                description="건축 요소의 반복을 통해 시각적 리듬감을 만드는 패턴",
                problem="단조로운 파사드와 공간에 다이나믹한 특성 부여",
                solution="창, 기둥, 장식 요소 등의 규칙적 또는 변화하는 반복",
                context=[ContextType.URBAN, ContextType.INSTITUTIONAL],
                building_types=["사무소", "아파트", "학교", "상업시설"],
                advantages=[
                    "시각적 흥미 증대",
                    "건물의 스케일감 조절",
                    "통일성과 다양성 조화",
                    "건축적 아이덴티티 확보"
                ],
                disadvantages=[
                    "단조로움 위험",
                    "기능적 제약 가능",
                    "비용 증가",
                    "유지관리 복잡"
                ],
                variations=[
                    "등간격 반복",
                    "리듬 변화형",
                    "크기 점변형",
                    "재료 교체형"
                ],
                examples=[
                    {"name": "유니테 다비타시옹", "location": "프랑스", "period": "1952년"},
                    {"name": "경동 나진상가", "location": "한국", "period": "1960년대"}
                ],
                guidelines=[
                    "전체적 비례와 조화",
                    "기능과 미학의 균형",
                    "재료 특성 적극 활용",
                    "주변 환경과의 관계 고려"
                ],
                related_patterns=["facade_modulation", "pattern_integration"]
            ),
            
            "transparency_layering": DesignPattern(
                name="투명성과 레이어링 (Transparency and Layering)",
                category=PatternCategory.AESTHETIC,
                description="투명하거나 반투명한 재료를 겹겹이 배치하여 공간의 깊이감을 만드는 패턴",
                problem="공간의 단조로움과 경계의 경직성",
                solution="유리, 메시, 스크린 등을 레이어링하여 시각적 깊이와 변화 창출",
                context=[ContextType.URBAN, ContextType.COMMERCIAL],
                building_types=["사무소", "상업시설", "문화시설", "전시장"],
                advantages=[
                    "공간의 연속성",
                    "시각적 깊이감",
                    "자연 채광 활용",
                    "내외부 소통"
                ],
                disadvantages=[
                    "프라이버시 제한",
                    "에너지 손실",
                    "유지관리 어려움",
                    "구조적 복잡성"
                ],
                variations=[
                    "이중 스킨 파사드",
                    "메시 레이어",
                    "색상 투명성",
                    "동적 레이어"
                ],
                examples=[
                    {"name": "도쿄 국제포럼", "location": "일본", "period": "1996년"},
                    {"name": "동대문디자인플라자", "location": "한국", "period": "2014년"}
                ],
                guidelines=[
                    "레이어 간 적절한 간격 유지",
                    "청소 및 유지관리 동선 확보",
                    "구조적 안전성 철저히 검토",
                    "에너지 성능 종합 검토"
                ],
                related_patterns=["curtain_wall", "interactive_facade"]
            )
        }
    
    def _initialize_combinations(self) -> Dict[str, List[str]]:
        """패턴 조합 관계 정의"""
        return {
            "traditional_korean": ["courtyard", "post_and_beam", "passive_solar"],
            "modern_office": ["central_spine", "flexible_space", "curtain_wall"],
            "sustainable_design": ["passive_solar", "green_roof", "natural_ventilation"],
            "cultural_building": ["ring_circulation", "central_spine", "transparency_layering"],
            "residential_complex": ["cluster", "terraced", "mixed_use"],
            "urban_integration": ["mixed_use", "vertical_circulation", "podium_tower"]
        }
    
    def get_pattern(self, pattern_name: str) -> Optional[DesignPattern]:
        """특정 패턴 반환"""
        return self.patterns.get(pattern_name)
    
    def get_patterns_by_category(self, category: PatternCategory) -> List[DesignPattern]:
        """카테고리별 패턴 반환"""
        return [pattern for pattern in self.patterns.values() 
                if pattern.category == category]
    
    def get_patterns_by_building_type(self, building_type: str) -> List[DesignPattern]:
        """건물 유형별 적합한 패턴 반환"""
        return [pattern for pattern in self.patterns.values()
                if building_type.lower() in [bt.lower() for bt in pattern.building_types]]
    
    def get_patterns_by_context(self, context: ContextType) -> List[DesignPattern]:
        """맥락별 패턴 반환"""
        return [pattern for pattern in self.patterns.values()
                if context in pattern.context]
    
    def recommend_patterns(self, building_type: str, style: str, context: str) -> Dict[str, Any]:
        """건물 유형, 스타일, 맥락에 따른 패턴 추천"""
        
        # 기본 패턴 선별
        relevant_patterns = []
        
        # 건물 유형 기반 필터링
        for pattern in self.patterns.values():
            if building_type.lower() in [bt.lower() for bt in pattern.building_types]:
                relevant_patterns.append(pattern)
        
        # 스타일 기반 추가 필터링
        style_patterns = self._get_style_specific_patterns(style)
        
        # 맥락 기반 추가 필터링
        context_enum = self._map_context_string(context)
        if context_enum:
            context_patterns = self.get_patterns_by_context(context_enum)
        else:
            context_patterns = []
        
        # 추천 패턴 종합
        recommended = {
            "primary_patterns": relevant_patterns[:3],  # 상위 3개
            "style_specific": style_patterns,
            "context_specific": context_patterns[:2],  # 상위 2개
            "pattern_combinations": self._get_recommended_combinations(building_type, style)
        }
        
        return recommended
    
    def _get_style_specific_patterns(self, style: str) -> List[DesignPattern]:
        """스타일별 특화 패턴"""
        style_mapping = {
            "hanok": ["courtyard", "post_and_beam"],
            "traditional": ["courtyard", "post_and_beam"],
            "modern": ["flexible_space", "transparency_layering"],
            "contemporary": ["mixed_use", "transparency_layering"],
            "sustainable": ["passive_solar", "green_roof"]
        }
        
        pattern_names = style_mapping.get(style.lower(), [])
        return [self.patterns[name] for name in pattern_names if name in self.patterns]
    
    def _map_context_string(self, context: str) -> Optional[ContextType]:
        """문자열 맥락을 ContextType으로 매핑"""
        mapping = {
            "도시": ContextType.URBAN,
            "urban": ContextType.URBAN,
            "교외": ContextType.SUBURBAN,
            "suburban": ContextType.SUBURBAN,
            "농촌": ContextType.RURAL,
            "rural": ContextType.RURAL,
            "상업": ContextType.COMMERCIAL,
            "commercial": ContextType.COMMERCIAL,
            "주거": ContextType.RESIDENTIAL,
            "residential": ContextType.RESIDENTIAL
        }
        
        return mapping.get(context.lower())
    
    def _get_recommended_combinations(self, building_type: str, style: str) -> List[str]:
        """추천 패턴 조합"""
        combination_key = f"{style.lower()}_{building_type.lower()}"
        
        # 미리 정의된 조합이 있는지 확인
        for key, patterns in self.pattern_combinations.items():
            if key in combination_key or combination_key in key:
                return patterns
        
        # 기본 조합 반환
        if style.lower() in ["hanok", "traditional"]:
            return ["courtyard", "post_and_beam", "passive_solar"]
        elif style.lower() in ["modern", "contemporary"]:
            return ["flexible_space", "transparency_layering", "mixed_use"]
        else:
            return ["central_spine", "flexible_space", "natural_ventilation"]
    
    def generate_pattern_report(self, selected_patterns: List[str]) -> Dict[str, Any]:
        """선택된 패턴들의 종합 리포트 생성"""
        patterns = [self.patterns[name] for name in selected_patterns if name in self.patterns]
        
        if not patterns:
            return {"error": "선택된 패턴이 없습니다."}
        
        # 패턴 분석
        categories = {}
        advantages = []
        disadvantages = []
        guidelines = []
        examples = []
        
        for pattern in patterns:
            # 카테고리별 분류
            category = pattern.category.value
            if category not in categories:
                categories[category] = []
            categories[category].append(pattern.name)
            
            # 장단점 수집
            advantages.extend(pattern.advantages)
            disadvantages.extend(pattern.disadvantages)
            guidelines.extend(pattern.guidelines)
            examples.extend(pattern.examples)
        
        # 중복 제거 및 정리
        advantages = list(set(advantages))
        disadvantages = list(set(disadvantages))
        
        return {
            "pattern_summary": {
                "total_patterns": len(patterns),
                "categories": categories,
                "pattern_names": [p.name for p in patterns]
            },
            "combined_advantages": advantages,
            "potential_challenges": disadvantages,
            "implementation_guidelines": guidelines,
            "reference_examples": examples[:5],  # 상위 5개만
            "compatibility_analysis": self._analyze_pattern_compatibility(patterns),
            "recommendations": self._generate_implementation_recommendations(patterns)
        }
    
    def _analyze_pattern_compatibility(self, patterns: List[DesignPattern]) -> Dict[str, Any]:
        """패턴 간 호환성 분석"""
        compatibility = {
            "high_synergy": [],
            "potential_conflicts": [],
            "neutral": []
        }
        
        # 간단한 호환성 규칙 (실제로는 더 복잡한 로직 필요)
        for i, pattern1 in enumerate(patterns):
            for pattern2 in patterns[i+1:]:
                # 같은 카테고리면 잠재적 충돌
                if pattern1.category == pattern2.category:
                    compatibility["potential_conflicts"].append(
                        f"{pattern1.name} vs {pattern2.name}"
                    )
                # 환경+기능 패턴은 시너지
                elif (pattern1.category == PatternCategory.ENVIRONMENTAL and 
                      pattern2.category == PatternCategory.FUNCTIONAL):
                    compatibility["high_synergy"].append(
                        f"{pattern1.name} + {pattern2.name}"
                    )
                else:
                    compatibility["neutral"].append(
                        f"{pattern1.name} & {pattern2.name}"
                    )
        
        return compatibility
    
    def _generate_implementation_recommendations(self, patterns: List[DesignPattern]) -> List[str]:
        """구현 권장사항 생성"""
        recommendations = [
            "패턴 적용 우선순위를 명확히 설정하세요",
            "각 패턴의 핵심 원칙을 충실히 따르세요",
            "패턴 간 상호작용을 신중히 검토하세요",
            "지역 법규와 기준에 맞게 조정하세요",
            "사용자 요구사항과의 적합성을 지속적으로 검증하세요"
        ]
        
        # 패턴별 특화 권장사항 추가
        for pattern in patterns:
            if pattern.category == PatternCategory.ENVIRONMENTAL:
                recommendations.append("환경 성능 시뮬레이션을 통한 검증이 필요합니다")
            elif pattern.category == PatternCategory.STRUCTURAL:
                recommendations.append("구조 엔지니어와의 긴밀한 협업이 필수입니다")
        
        return list(set(recommendations))  # 중복 제거