"""
한국어 건축 전문 자연어 처리 모듈 - 최종 버전
===============================================

건축 도메인 특화 한국어 텍스트 처리 및 설계 의도 분석
Korean Architecture-specific NLP processor with comprehensive analysis

@version 2.0
@author VIBA AI Team
@date 2025.07.06
"""

import re
import json
import time
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum
from collections import Counter

# 한국어 NLP 라이브러리
try:
    from konlpy.tag import Mecab, Okt, Komoran, Hannanum
except ImportError:
    print("ConlPy not available, using basic tokenization")
    Mecab = Okt = Komoran = Hannanum = None

try:
    from kiwipiepy import Kiwi
except ImportError:
    print("Kiwi not available")
    Kiwi = None

# AI/ML 라이브러리
from transformers import AutoTokenizer, AutoModel, pipeline
import torch
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# 프로젝트 임포트
from ..utils.logger import setup_logger
from ..utils.metrics_collector import record_ai_inference_metric

logger = setup_logger(__name__)


class TokenizerType(Enum):
    """지원하는 토크나이저 타입"""
    MECAB = "mecab"
    OKT = "okt"
    KOMORAN = "komoran"
    HANNANUM = "hannanum"
    KIWI = "kiwi"
    AUTO = "auto"  # 자동 선택


class ArchitecturalStyle(Enum):
    """건축 스타일 분류"""
    MODERN = "modern"
    TRADITIONAL = "traditional"
    HANOK = "hanok"
    MINIMALIST = "minimalist"
    CLASSICAL = "classical"
    SUSTAINABLE = "sustainable"
    INDUSTRIAL = "industrial"
    CONTEMPORARY = "contemporary"
    BAUHAUS = "bauhaus"
    POSTMODERN = "postmodern"


class DesignIntent(Enum):
    """설계 의도 분류"""
    FUNCTIONALITY = "functionality"  # 기능성 중심
    AESTHETICS = "aesthetics"       # 미적 가치 중심
    EFFICIENCY = "efficiency"       # 효율성 중심
    COMFORT = "comfort"             # 편안함 중심
    SUSTAINABILITY = "sustainability" # 지속가능성 중심
    ACCESSIBILITY = "accessibility"  # 접근성 중심
    PRIVACY = "privacy"             # 프라이버시 중심
    OPENNESS = "openness"           # 개방감 중심
    FLEXIBILITY = "flexibility"     # 유연성 중심
    TRADITION = "tradition"         # 전통성 중심


@dataclass
class ProcessedText:
    """처리된 텍스트 결과"""
    original_text: str
    normalized_text: str
    tokens: List[str]
    pos_tags: List[Tuple[str, str]]
    entities: List[Dict[str, Any]]
    keywords: List[str]
    confidence: float


@dataclass
class ArchitecturalEntity:
    """건축 관련 엔티티 (확장)"""
    text: str
    entity_type: str
    value: Any
    confidence: float
    start: int
    end: int
    context: Optional[str] = None
    semantic_role: Optional[str] = None


@dataclass
class SpatialRelation:
    """공간 관계 정보"""
    subject: str
    relation: str  # 인접, 연결, 분리, 포함 등
    object: str
    confidence: float


@dataclass
class DesignRequirement:
    """설계 요구사항"""
    requirement_type: str  # 기능적, 미적, 성능적, 법적 등
    description: str
    priority: str  # high, medium, low
    measurable: bool
    value: Optional[Any] = None
    unit: Optional[str] = None


@dataclass
class ArchitecturalAnalysis:
    """종합 건축 분석 결과"""
    original_text: str
    normalized_text: str
    entities: List[ArchitecturalEntity]
    spatial_relations: List[SpatialRelation]
    design_requirements: List[DesignRequirement]
    design_intent: List[DesignIntent]
    architectural_style: Optional[ArchitecturalStyle]
    keywords: List[str]
    technical_terms: List[str]
    confidence: float
    sentiment: str
    complexity_score: float


class KoreanArchitectureProcessor:
    """한국어 건축 전문 NLP 프로세서"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        한국어 건축 전문 NLP 프로세서 초기화
        
        Args:
            config: 설정 딕셔너리
        """
        self.config = config or {}
        self.tokenizer_type = TokenizerType(self.config.get('korean_tokenizer', 'auto'))
        
        # 토크나이저 및 모델
        self.tokenizers = {}  # 여러 토크나이저 지원
        self.sentence_model = None
        self.sentence_tokenizer = None
        self.classification_model = None
        
        # 건축 도메인 특화 사전
        self.building_types = self._load_comprehensive_building_types()
        self.room_types = self._load_comprehensive_room_types()
        self.architectural_elements = self._load_architectural_elements()
        self.construction_materials = self._load_construction_materials()
        self.spatial_concepts = self._load_spatial_concepts()
        self.design_patterns = self._load_design_patterns()
        self.architectural_styles = self._load_architectural_styles()
        
        # 패턴 컴파일
        self.area_patterns = self._compile_area_patterns()
        self.dimension_patterns = self._compile_dimension_patterns()
        self.orientation_patterns = self._compile_orientation_patterns()
        self.number_patterns = self._compile_number_patterns()
        self.spatial_relation_patterns = self._compile_spatial_relation_patterns()
        self.requirement_patterns = self._compile_requirement_patterns()
        
        # 성능 메트릭
        self.processing_stats = {
            'total_processed': 0,
            'average_confidence': 0.0,
            'entity_extraction_accuracy': 0.0
        }
        
        self._initialize_models()
    
    def _initialize_models(self):
        """모델 초기화"""
        try:
            # 형태소 분석기 초기화 - 자동 선택
            available_tokenizers = []
            
            if Mecab:
                try:
                    self.tokenizers['mecab'] = Mecab()
                    available_tokenizers.append('mecab')
                except:
                    pass
            
            if Okt:
                try:
                    self.tokenizers['okt'] = Okt()
                    available_tokenizers.append('okt')
                except:
                    pass
            
            if Kiwi:
                try:
                    self.tokenizers['kiwi'] = Kiwi()
                    available_tokenizers.append('kiwi')
                except:
                    pass
            
            # 기본 토크나이저 선택
            if available_tokenizers:
                default_tokenizer = available_tokenizers[0]
                self.tokenizer = self.tokenizers[default_tokenizer]
                logger.info(f"Using {default_tokenizer} as default tokenizer")
            else:
                logger.warning("No Korean tokenizers available, using basic split")
                self.tokenizer = None
            
            # 문장 임베딩 모델 초기화 (옵션)
            try:
                model_name = self.config.get('sentence_model', 'klue/bert-base')
                self.sentence_tokenizer = AutoTokenizer.from_pretrained(
                    model_name, cache_dir="./models_cache"
                )
                self.sentence_model = AutoModel.from_pretrained(
                    model_name, cache_dir="./models_cache"
                )
                logger.info(f"Sentence model initialized: {model_name}")
            except Exception as e:
                logger.warning(f"Failed to load sentence model: {e}")
            
            logger.info("Korean architecture processor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Korean processor: {e}")
            # 기본 설정으로 계속 진행
            self.tokenizer = None
    
    def _load_comprehensive_building_types(self) -> Dict[str, List[str]]:
        """종합 건물 타입 사전 로드 (확장)"""
        return {
            # 주거 시설
            "RESIDENTIAL_APARTMENT": [
                "아파트", "공동주택", "연립주택", "다세대주택", "빌라", "맨션",
                "타워", "단지", "아파트단지", "주공아파트", "임대아파트", "분양아파트"
            ],
            "RESIDENTIAL_HOUSE": [
                "단독주택", "일반주택", "전원주택", "단독", "주택", "집", "가정집",
                "독채", "단층집", "2층집", "3층집", "개인주택", "한옥", "양옥", "펜션"
            ],
            "RESIDENTIAL_STUDIO": [
                "원룸", "투룸", "쓰리룸", "포룸", "스튜디오", "오피스텔", "고시원", "셰어하우스"
            ],
            
            # 상업 시설
            "COMMERCIAL_RETAIL": [
                "상가", "상업시설", "매장", "상점", "쇼핑몰", "백화점", "마트", "편의점",
                "상업빌딩", "복합상가", "근린생활시설", "판매시설", "아울렛", "전문점가"
            ],
            "COMMERCIAL_RESTAURANT": [
                "음식점", "레스토랑", "카페", "식당", "푸드코트", "바", "클럽", "펜션",
                "호텔", "모텔", "리조트", "게스트하우스", "민박"
            ],
            
            # 업무 시설
            "OFFICE_BUILDING": [
                "사무실", "오피스", "업무시설", "사무공간", "업무공간", "사무소",
                "회사", "기업", "업무용빌딩", "사무동", "본사", "지사", "지점"
            ],
            "OFFICE_COWORKING": [
                "코워킹스페이스", "공유오피스", "창업센터", "인큐베이터", "액셀러레이터"
            ],
            
            # 공공 시설
            "PUBLIC_EDUCATION": [
                "학교", "유치원", "어린이집", "초등학교", "중학교", "고등학교",
                "대학교", "대학", "연구소", "도서관", "박물관", "미술관"
            ],
            "PUBLIC_MEDICAL": [
                "병원", "의원", "치과", "한의원", "약국", "보건소", "클리닉",
                "종합병원", "응급실", "수술실", "검사실"
            ],
            "PUBLIC_WELFARE": [
                "복지센터", "경로당", "어린이집", "보육원", "양로원", "요양원",
                "사회복지시설", "커뮤니티센터", "주민센터"
            ],
            
            # 문화/체육 시설
            "CULTURAL_SPORTS": [
                "체육관", "수영장", "골프장", "테니스장", "축구장", "야구장",
                "경기장", "스타디움", "아레나", "헬스장", "피트니스센터"
            ],
            "CULTURAL_ARTS": [
                "극장", "영화관", "콘서트홀", "전시장", "갤러리", "문화센터",
                "예술회관", "공연장", "스튜디오", "아틀리에"
            ],
            
            # 산업 시설
            "INDUSTRIAL_MANUFACTURING": [
                "공장", "제조시설", "생산시설", "작업장", "제조업", "생산라인",
                "조립공장", "가공공장", "화학공장", "철강공장"
            ],
            "INDUSTRIAL_LOGISTICS": [
                "창고", "물류센터", "배송센터", "유통센터", "저장시설",
                "냉동창고", "자동창고", "물류터미널"
            ],
            
            # 교통 시설
            "TRANSPORTATION": [
                "지하철역", "버스터미널", "기차역", "공항", "항구", "선착장",
                "주차장", "터널", "교량", "도로", "고속도로"
            ]
        }
    
    def _load_comprehensive_room_types(self) -> Dict[str, List[str]]:
        """종합 방 타입 사전 로드 (확장)"""
        return {
            # 주요 생활 공간
            "거실": ["거실", "리빙룸", "응접실", "거실공간", "메인룸", "대청마루", "사랑방"],
            "침실": ["침실", "침방", "방", "베드룸", "안방", "작은방", "큰방", "주침실", "게스트룸", "자녀방"],
            "주방": ["주방", "부엌", "키친", "조리공간", "요리공간", "아일랜드키친", "오픈키친", "ㄱ자키친"],
            "식당": ["식당", "다이닝룸", "식사공간", "다이닝", "식탁", "식사영역"],
            
            # 위생 공간
            "화장실": ["화장실", "욕실", "바스룸", "샤워실", "변기", "세면실", "목욕탕", "파우더룸"],
            "세면실": ["세면실", "세면대", "씻는곳", "화장대"],
            
            # 작업/학습 공간
            "서재": ["서재", "공부방", "작업실", "홈오피스", "독서실", "연구실", "아틀리에"],
            "홈오피스": ["홈오피스", "재택근무실", "업무공간", "사무공간"],
            
            # 수납/보관 공간
            "드레스룸": ["드레스룸", "옷방", "의상실", "탈의실", "옷장", "파우더룸"],
            "다용도실": ["다용도실", "세탁실", "창고", "보관실", "수납공간", "팬트리", "보조주방"],
            "창고": ["창고", "저장실", "물품보관실", "수납실"],
            
            # 외부 연결 공간
            "현관": ["현관", "입구", "로비", "엔트런스", "현관홀", "玄關"],
            "베란다": ["베란다", "발코니", "테라스", "옥상", "마당", "정원", "데크"],
            "테라스": ["테라스", "루프탑", "옥상정원", "야외공간"],
            
            # 동선 공간
            "계단": ["계단", "층계", "계단실", "나선계단", "직선계단"],
            "복도": ["복도", "홀", "아이엘", "동선", "회랑", "갤러리"],
            "현관홀": ["현관홀", "로비", "포이어", "입구홀"],
            
            # 특수 공간
            "지하실": ["지하실", "지하공간", "반지하", "지하저장고"],
            "다락방": ["다락방", "다락", "아틱", "로프트"],
            "선룸": ["선룸", "일광욕실", "온실", "겨울정원"],
            "사우나": ["사우나", "찜질방", "스팀룸"],
            
            # 전문 공간
            "미디어룸": ["미디어룸", "홈시어터", "영화감상실", "오디오룸"],
            "와인셀러": ["와인셀러", "와인저장고", "술저장고"],
            "펜트하우스": ["펜트하우스", "옥상층", "최상층"]
        }
    
    def _load_architectural_elements(self) -> Dict[str, List[str]]:
        """건축 요소 사전 로드"""
        return {
            "구조요소": [
                "기둥", "보", "슬래브", "벽체", "골조", "기초", "파일", "매트기초",
                "철골", "철근콘크리트", "목구조", "조적", "트러스", "아치", "돔"
            ],
            "마감재료": [
                "타일", "마루", "카펫", "리놀륨", "석재", "목재", "금속", "유리",
                "콘크리트", "벽돌", "페인트", "벽지", "몰딩", "코니스"
            ],
            "개구부": [
                "문", "창문", "현관문", "발코니문", "슬라이딩도어", "폴딩도어",
                "천창", "채광창", "환기창", "출입구", "비상구"
            ],
            "설비시설": [
                "난방", "냉방", "환기", "급수", "배수", "전기", "조명", "가스",
                "엘리베이터", "에스컬레이터", "인터컴", "CCTV", "자동문"
            ]
        }
    
    def _load_construction_materials(self) -> Dict[str, List[str]]:
        """건설 자재 사전 로드"""
        return {
            "구조재료": [
                "콘크리트", "철근", "철골", "목재", "벽돌", "블록", "석재",
                "프리캐스트", "프리스트레스트", "복합재료"
            ],
            "마감재료": [
                "타일", "석재", "목재", "금속", "유리", "플라스틱", "세라믹",
                "테라코타", "스테인리스", "알루미늄", "구리", "아연"
            ],
            "단열재료": [
                "단열재", "글라스울", "암면", "폴리스티렌", "우레탄", "셀룰로스",
                "진공단열재", "에어로젤"
            ],
            "방수재료": [
                "방수막", "방수시트", "방수도료", "실링재", "코킹", "씰런트"
            ]
        }
    
    def _load_spatial_concepts(self) -> Dict[str, List[str]]:
        """공간 개념 사전 로드"""
        return {
            "공간관계": [
                "인접", "연결", "분리", "포함", "겹침", "관통", "우회",
                "수직연결", "수평연결", "시각적연결", "물리적분리"
            ],
            "공간특성": [
                "개방", "폐쇄", "반개방", "투명", "반투명", "불투명",
                "유연", "고정", "가변", "다목적", "전용"
            ],
            "공간크기": [
                "넓은", "좁은", "높은", "낮은", "깊은", "얕은",
                "웅장한", "아늑한", "압축적", "확장적"
            ],
            "공간품질": [
                "밝은", "어두운", "조용한", "시끄러운", "따뜻한", "시원한",
                "습한", "건조한", "환기되는", "밀폐된"
            ]
        }
    
    def _load_design_patterns(self) -> Dict[str, List[str]]:
        """설계 패턴 사전 로드"""
        return {
            "평면패턴": [
                "중앙홀형", "복도형", "코어형", "아트리움형", "클러스터형",
                "선형", "ㄱ자형", "ㄷ자형", "ㅁ자형", "Y자형", "십자형"
            ],
            "입면패턴": [
                "수평분할", "수직분할", "격자형", "리듬형", "대칭형",
                "비대칭형", "단조형", "변화형", "반복형"
            ],
            "동선패턴": [
                "일방향", "양방향", "순환형", "분기형", "집중형",
                "분산형", "계층형", "네트워크형"
            ]
        }
    
    def _load_architectural_styles(self) -> Dict[str, List[str]]:
        """건축 양식 사전 로드"""
        return {
            "서양고전": [
                "그리스", "로마", "로마네스크", "고딕", "르네상스", "바로크",
                "로코코", "신고전주의", "절충주의"
            ],
            "근현대": [
                "모던", "포스트모던", "미니멀", "하이테크", "디컨스트럭티비즘",
                "바우하우스", "아르누보", "아르데코", "브루탈리즘"
            ],
            "한국전통": [
                "한옥", "궁궐", "사찰", "민가", "서원", "향교",
                "전통한옥", "현대한옥", "신한옥"
            ],
            "지역성": [
                "지중해", "스칸디나비아", "일본", "중국", "인도",
                "이슬람", "아프리카", "남미"
            ]
        }
    
    def _compile_area_patterns(self) -> List[re.Pattern]:
        """면적 패턴 컴파일"""
        patterns = [
            r'(\d+(?:\.\d+)?)\s*평',
            r'(\d+(?:\.\d+)?)\s*㎡',
            r'(\d+(?:\.\d+)?)\s*m2',
            r'(\d+(?:\.\d+)?)\s*제곱미터',
            r'(\d+(?:\.\d+)?)\s*평형',
            r'(\d+(?:\.\d+)?)\s*py',
            r'(\d+(?:\.\d+)?)\s*평\s*대',
            r'(\d+(?:\.\d+)?)\s*평\s*짜리',
        ]
        return [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def _compile_dimension_patterns(self) -> List[re.Pattern]:
        """치수 패턴 컴파일"""
        patterns = [
            r'(너비|Width)\s*(\d+(?:\.\d+)?)\s*(m|mm|cm|미터|센티미터|밀리미터)',
            r'(높이|Height)\s*(\d+(?:\.\d+)?)\s*(m|mm|cm|미터|센티미터|밀리미터)',
            r'(깊이|Depth)\s*(\d+(?:\.\d+)?)\s*(m|mm|cm|미터|센티미터|밀리미터)',
            r'(높이|Height)\s*(\d+(?:\.\d+)?)\s*(m|미터)',
            r'(청서|Drawings?)\s*(\d+(?:\.\d+)?)\s*(m|미터)'
        ]
        return [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def _compile_orientation_patterns(self) -> List[re.Pattern]:
        """방향 패턴 컴파일"""
        patterns = [
            r'(남향|남쪽\s*향|남쪽)',
            r'(북향|북쪽\s*향|북쪽)',
            r'(동향|동쪽\s*향|동쪽)',
            r'(서향|서쪽\s*향|서쪽)',
            r'(남동향|남동쪽\s*향|남동쪽)',
            r'(남서향|남서쪽\s*향|남서쪽)',
            r'(북동향|북동쪽\s*향|북동쪽)',
            r'(북서향|북서쪽\s*향|북서쪽)',
        ]
        return [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def _compile_number_patterns(self) -> Dict[str, re.Pattern]:
        """숫자 패턴 컴파일"""
        return {
            'korean_numbers': re.compile(r'(일|이|삼|사|오|육|칠|팔|구|십|백|천|만|억)'),
            'arabic_numbers': re.compile(r'\d+(?:\.\d+)?'),
            'ordinal': re.compile(r'(\d+|일|이|삼|사|오|육|칠|팔|구|십)\s*(번째|째|층|동|호)'),
        }
    
    def _compile_spatial_relation_patterns(self) -> List[re.Pattern]:
        """공간 관계 패턴 컴파일"""
        patterns = [
            r'(.+?)(에서|에서는|에서의)\s*(인접한|가까운|인근한)\s*(.+)',
            r'(.+?)(와|과)\s*(연결된|연결되어|연결하는)\s*(.+)',
            r'(.+?)(의|를)\s*(포함하는|포함한|내에|안에)\s*(.+)',
            r'(.+?)(에서|에서는)\s*(분리된|분리되어|떨어진)\s*(.+)',
            r'(.+?)(와|과)\s*(마주보는|마주한|대면한)\s*(.+)'
        ]
        return [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def _compile_requirement_patterns(self) -> List[re.Pattern]:
        """요구사항 패턴 컴파일"""
        patterns = [
            r'(.+?)(이|가)\s*(필요하다|필요한|요구된다|요구되는)',
            r'(.+?)(이|가)\s*(원하다|원하는|바란다|바라는|하고싶다)',
            r'(.+?)(이|가)\s*(중요하다|중요한|핵심이다)',
            r'(.+?)(이|가)\s*(반드시|반드|꼭|꼭상)\s*(.+)',
            r'(.+?)(를|을)\s*(고려해야|고려한|주의해야|주의한)\s*(.+)'
        ]
        return [re.compile(pattern, re.IGNORECASE) for pattern in patterns]

    def normalize_text(self, text: str) -> str:
        """텍스트 정규화"""
        if not text or not text.strip():
            return ""
        
        # 기본 정규화
        normalized = text.strip()
        
        # 특수문자 및 공백 정리
        normalized = re.sub(r'\s+', ' ', normalized)  # 연속 공백 제거
        normalized = re.sub(r'[^\w\s가-힣.,!?()-]', ' ', normalized)  # 특수문자 제거
        
        # 건축 용어 표준화
        normalized = self._standardize_building_terms(normalized)
        
        # 숫자 표현 정규화
        normalized = self._normalize_numbers(normalized)
        
        return normalized.strip()
    
    def _standardize_building_terms(self, text: str) -> str:
        """건축 용어 표준화"""
        synonyms = {
            '빌라': '아파트',
            '맨션': '아파트',
            '연립': '연립주택',
            '다세대': '다세대주택',
            '원룸': '아파트',
            '투룸': '아파트',
            '쓰리룸': '아파트',
            '방': '침실',
            '화장실': '욕실',
            '부엌': '주방',
            '발코니': '베란다',
        }
        
        for synonym, standard in synonyms.items():
            text = re.sub(rf'\b{synonym}\b', standard, text)
        
        return text
    
    def _normalize_numbers(self, text: str) -> str:
        """숫자 표현 정규화"""
        korean_to_arabic = {
            '일': '1', '이': '2', '삼': '3', '사': '4', '오': '5',
            '육': '6', '칠': '7', '팔': '8', '구': '9', '십': '10',
            '스무': '20', '서른': '30', '마흔': '40', '쉰': '50'
        }
        
        for korean, arabic in korean_to_arabic.items():
            text = re.sub(rf'\b{korean}\b', arabic, text)
        
        return text

    def tokenize(self, text: str) -> List[str]:
        """텍스트 토큰화"""
        if not text:
            return []
        
        try:
            # 형태소 분석기를 사용한 토큰화
            if self.tokenizer and hasattr(self.tokenizer, 'morphs'):
                tokens = self.tokenizer.morphs(text)
            else:
                tokens = text.split()
            
            # 불용어 제거 및 필터링
            filtered_tokens = self._filter_tokens(tokens)
            
            return filtered_tokens
            
        except Exception as e:
            logger.error(f"Tokenization failed: {e}")
            return text.split()  # 기본 분할로 폴백
    
    def _filter_tokens(self, tokens: List[str]) -> List[str]:
        """토큰 필터링"""
        stopwords = {
            '을', '를', '이', '가', '은', '는', '에', '에서', '로', '으로',
            '의', '와', '과', '도', '만', '조차', '마저', '부터', '까지',
            '하고', '하여', '하니', '하면', '해서', '해도', '하지만',
            '그리고', '그런데', '그러나', '그래서', '따라서', '또한',
            '또는', '혹은', '아니면', '만약', '비록', '설령', '설사'
        }
        
        filtered = []
        for token in tokens:
            if len(token) < 2:
                continue
            if token in stopwords:
                continue
            if token.isdigit():
                filtered.append(token)
                continue
            if re.search(r'[가-힣]', token):
                filtered.append(token)
        
        return filtered

    def pos_tag(self, text: str) -> List[Tuple[str, str]]:
        """품사 태깅"""
        if not text:
            return []
        
        try:
            if self.tokenizer and hasattr(self.tokenizer, 'pos'):
                pos_tags = self.tokenizer.pos(text)
            else:
                # 기본 품사 태깅
                tokens = self.tokenize(text)
                pos_tags = [(token, 'NNG') for token in tokens]
            
            return pos_tags
            
        except Exception as e:
            logger.error(f"POS tagging failed: {e}")
            return [(word, 'UNK') for word in text.split()]
    
    # =================================================================
    # 핵심 확장 메서드들
    # =================================================================
    
    def extract_comprehensive_entities(self, text: str) -> List[ArchitecturalEntity]:
        """종합 건축 엔티티 추출 (확장)"""
        entities = []
        
        # 기존 엔티티 추출
        entities.extend(self._extract_building_types_enhanced(text))
        entities.extend(self._extract_areas(text))
        entities.extend(self._extract_orientations(text))
        entities.extend(self._extract_room_types_enhanced(text))
        entities.extend(self._extract_floors(text))
        
        # 새로운 엔티티 추출
        entities.extend(self._extract_architectural_elements(text))
        entities.extend(self._extract_materials(text))
        entities.extend(self._extract_dimensions(text))
        entities.extend(self._extract_costs(text))
        entities.extend(self._extract_timeframes(text))
        
        return entities
    
    def _extract_building_types_enhanced(self, text: str) -> List[ArchitecturalEntity]:
        """향상된 건물 타입 추출"""
        entities = []
        
        for building_type, synonyms in self.building_types.items():
            for synonym in synonyms:
                pattern = rf'\b{re.escape(synonym)}\b'
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    # 문맥 정보 추가
                    context_start = max(0, match.start() - 20)
                    context_end = min(len(text), match.end() + 20)
                    context = text[context_start:context_end].strip()
                    
                    entities.append(ArchitecturalEntity(
                        text=match.group(),
                        entity_type="BUILDING_TYPE",
                        value=building_type,
                        confidence=0.9,
                        start=match.start(),
                        end=match.end(),
                        context=context,
                        semantic_role="building_classification"
                    ))
        
        return entities
    
    def _extract_room_types_enhanced(self, text: str) -> List[ArchitecturalEntity]:
        """향상된 방 타입 추출"""
        entities = []
        
        for room_type, synonyms in self.room_types.items():
            for synonym in synonyms:
                pattern = rf'\b{re.escape(synonym)}\b'
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    # 수량 정보 파악
                    quantity_pattern = r'(\d+)\s*개?\s*' + re.escape(synonym)
                    quantity_match = re.search(quantity_pattern, text)
                    quantity = int(quantity_match.group(1)) if quantity_match else 1
                    
                    entities.append(ArchitecturalEntity(
                        text=match.group(),
                        entity_type="ROOM_TYPE",
                        value={
                            "type": room_type,
                            "quantity": quantity
                        },
                        confidence=0.85,
                        start=match.start(),
                        end=match.end(),
                        semantic_role="space_component"
                    ))
        
        return entities
    
    def _extract_areas(self, text: str) -> List[ArchitecturalEntity]:
        """면적 정보 추출"""
        entities = []
        
        for pattern in self.area_patterns:
            matches = pattern.finditer(text)
            
            for match in matches:
                try:
                    value = float(match.group(1))
                    unit = "평" if "평" in match.group() else "m2"
                    
                    entities.append(ArchitecturalEntity(
                        text=match.group(),
                        entity_type="AREA",
                        value={"value": value, "unit": unit},
                        confidence=0.95,
                        start=match.start(),
                        end=match.end()
                    ))
                except (ValueError, IndexError):
                    continue
        
        return entities
    
    def _extract_orientations(self, text: str) -> List[ArchitecturalEntity]:
        """방향 정보 추출"""
        entities = []
        
        orientation_map = {
            "남향": "남향", "남쪽": "남향", "남쪽향": "남향",
            "북향": "북향", "북쪽": "북향", "북쪽향": "북향",
            "동향": "동향", "동쪽": "동향", "동쪽향": "동향",
            "서향": "서향", "서쪽": "서향", "서쪽향": "서향",
            "남동향": "남동향", "남동쪽": "남동향",
            "남서향": "남서향", "남서쪽": "남서향",
            "북동향": "북동향", "북동쪽": "북동향",
            "북서향": "북서향", "북서쪽": "북서향",
        }
        
        for pattern in self.orientation_patterns:
            matches = pattern.finditer(text)
            
            for match in matches:
                matched_text = match.group(1)
                standard_orientation = orientation_map.get(matched_text)
                
                if standard_orientation:
                    entities.append(ArchitecturalEntity(
                        text=match.group(),
                        entity_type="ORIENTATION",
                        value=standard_orientation,
                        confidence=0.9,
                        start=match.start(),
                        end=match.end()
                    ))
        
        return entities
    
    def _extract_floors(self, text: str) -> List[ArchitecturalEntity]:
        """층수 정보 추출"""
        entities = []
        
        floor_patterns = [
            r'(\d+)\s*층',
            r'(일|이|삼|사|오|육|칠|팔|구|십)\s*층',
            r'(\d+)\s*층\s*짜리',
            r'(\d+)\s*층\s*건물',
        ]
        
        for pattern_str in floor_patterns:
            pattern = re.compile(pattern_str, re.IGNORECASE)
            matches = pattern.finditer(text)
            
            for match in matches:
                try:
                    floor_text = match.group(1)
                    if floor_text.isdigit():
                        floor_value = int(floor_text)
                    else:
                        korean_numbers = {
                            '일': 1, '이': 2, '삼': 3, '사': 4, '오': 5,
                            '육': 6, '칠': 7, '팔': 8, '구': 9, '십': 10
                        }
                        floor_value = korean_numbers.get(floor_text, 1)
                    
                    entities.append(ArchitecturalEntity(
                        text=match.group(),
                        entity_type="FLOORS",
                        value=floor_value,
                        confidence=0.9,
                        start=match.start(),
                        end=match.end()
                    ))
                except (ValueError, KeyError):
                    continue
        
        return entities
    
    def _extract_architectural_elements(self, text: str) -> List[ArchitecturalEntity]:
        """건축 요소 추출"""
        entities = []
        
        for element_type, synonyms in self.architectural_elements.items():
            for synonym in synonyms:
                pattern = rf'\b{re.escape(synonym)}\b'
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    entities.append(ArchitecturalEntity(
                        text=match.group(),
                        entity_type="ARCHITECTURAL_ELEMENT",
                        value={
                            "category": element_type,
                            "element": synonym
                        },
                        confidence=0.8,
                        start=match.start(),
                        end=match.end(),
                        semantic_role="construction_component"
                    ))
        
        return entities
    
    def _extract_materials(self, text: str) -> List[ArchitecturalEntity]:
        """건설 자재 추출"""
        entities = []
        
        for material_type, synonyms in self.construction_materials.items():
            for synonym in synonyms:
                pattern = rf'\b{re.escape(synonym)}\b'
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    entities.append(ArchitecturalEntity(
                        text=match.group(),
                        entity_type="MATERIAL",
                        value={
                            "category": material_type,
                            "material": synonym
                        },
                        confidence=0.85,
                        start=match.start(),
                        end=match.end(),
                        semantic_role="material_specification"
                    ))
        
        return entities
    
    def _extract_dimensions(self, text: str) -> List[ArchitecturalEntity]:
        """치수 정보 추출"""
        entities = []
        
        for pattern in self.dimension_patterns:
            matches = pattern.finditer(text)
            
            for match in matches:
                try:
                    dimension_type = match.group(1)
                    value = float(match.group(2))
                    unit = match.group(3)
                    
                    entities.append(ArchitecturalEntity(
                        text=match.group(),
                        entity_type="DIMENSION",
                        value={
                            "type": dimension_type,
                            "value": value,
                            "unit": unit
                        },
                        confidence=0.95,
                        start=match.start(),
                        end=match.end(),
                        semantic_role="dimensional_specification"
                    ))
                except (ValueError, IndexError):
                    continue
        
        return entities
    
    def _extract_costs(self, text: str) -> List[ArchitecturalEntity]:
        """비용 정보 추출"""
        entities = []
        
        cost_patterns = [
            r'(\d+(?:,\d+)*)\s*(원|만원|억원|천원)',
            r'(\d+(?:\.\d+)?)\s*(억|만|천)',
            r'예산\s*(\d+(?:,\d+)*)\s*(원|만원|억원)',
            r'(\d+(?:,\d+)*)\s*만원\s*대'
        ]
        
        for pattern_str in cost_patterns:
            pattern = re.compile(pattern_str, re.IGNORECASE)
            matches = pattern.finditer(text)
            
            for match in matches:
                try:
                    value_str = match.group(1).replace(',', '')
                    value = float(value_str)
                    unit = match.group(2) if len(match.groups()) > 1 else "원"
                    
                    entities.append(ArchitecturalEntity(
                        text=match.group(),
                        entity_type="COST",
                        value={
                            "amount": value,
                            "unit": unit
                        },
                        confidence=0.9,
                        start=match.start(),
                        end=match.end(),
                        semantic_role="financial_specification"
                    ))
                except (ValueError, IndexError):
                    continue
        
        return entities
    
    def _extract_timeframes(self, text: str) -> List[ArchitecturalEntity]:
        """시간 관련 정보 추출"""
        entities = []
        
        time_patterns = [
            r'(\d+)\s*(년|개월|월|주|일)\s*내',
            r'(\d+)\s*(년|개월|월|주|일)\s*후',
            r'(\d+)\s*(년|개월|월|주|일)\s*걸림',
            r'완공\s*(\d+)\s*(년|월)',
            r'착공\s*(\d+)\s*(년|월)'
        ]
        
        for pattern_str in time_patterns:
            pattern = re.compile(pattern_str, re.IGNORECASE)
            matches = pattern.finditer(text)
            
            for match in matches:
                try:
                    value = int(match.group(1))
                    unit = match.group(2)
                    
                    entities.append(ArchitecturalEntity(
                        text=match.group(),
                        entity_type="TIMEFRAME",
                        value={
                            "duration": value,
                            "unit": unit
                        },
                        confidence=0.85,
                        start=match.start(),
                        end=match.end(),
                        semantic_role="temporal_specification"
                    ))
                except (ValueError, IndexError):
                    continue
        
        return entities
    
    def extract_spatial_relations(self, text: str) -> List[SpatialRelation]:
        """공간 관계 추출"""
        relations = []
        
        for pattern in self.spatial_relation_patterns:
            matches = pattern.finditer(text)
            
            for match in matches:
                try:
                    subject = match.group(1).strip()
                    connector = match.group(2).strip()
                    relation_type = match.group(3).strip()
                    object_part = match.group(4).strip()
                    
                    # 관계 유형 정규화
                    if "인접" in relation_type or "가까운" in relation_type:
                        relation = "인접"
                    elif "연결" in relation_type:
                        relation = "연결"
                    elif "포함" in relation_type or "내에" in relation_type:
                        relation = "포함"
                    elif "분리" in relation_type or "떨어진" in relation_type:
                        relation = "분리"
                    elif "마주" in relation_type or "대면" in relation_type:
                        relation = "대면"
                    else:
                        relation = "일반관계"
                    
                    relations.append(SpatialRelation(
                        subject=subject,
                        relation=relation,
                        object=object_part,
                        confidence=0.8
                    ))
                except (IndexError, AttributeError):
                    continue
        
        return relations
    
    def extract_design_requirements(self, text: str, tokens: List[str]) -> List[DesignRequirement]:
        """설계 요구사항 추출"""
        requirements = []
        
        for pattern in self.requirement_patterns:
            matches = pattern.finditer(text)
            
            for match in matches:
                try:
                    if len(match.groups()) >= 3:
                        requirement_text = match.group(1).strip()
                        requirement_type = self._classify_requirement_type(requirement_text)
                        priority = self._determine_priority(match.group())
                        
                        # 측정 가능성 판단
                        measurable = any(keyword in requirement_text for keyword in 
                                       ["평", "미터", "㎡", "층", "개", "명", "원", "만원", "억"])
                        
                        requirements.append(DesignRequirement(
                            requirement_type=requirement_type,
                            description=requirement_text,
                            priority=priority,
                            measurable=measurable
                        ))
                except (IndexError, AttributeError):
                    continue
        
        return requirements
    
    def _classify_requirement_type(self, text: str) -> str:
        """요구사항 유형 분류"""
        if any(keyword in text for keyword in ["넓은", "큰", "작은", "높은", "평", "㎡"]):
            return "공간적"
        elif any(keyword in text for keyword in ["밝은", "어두운", "조용한", "시원한"]):
            return "환경적"
        elif any(keyword in text for keyword in ["예산", "비용", "원", "만원", "억"]):
            return "경제적"
        elif any(keyword in text for keyword in ["안전한", "튼튼한", "내구성"]):
            return "안전성"
        elif any(keyword in text for keyword in ["아름다운", "예쁜", "멋진", "디자인"]):
            return "미적"
        else:
            return "기능적"
    
    def _determine_priority(self, text: str) -> str:
        """우선순위 결정"""
        if any(keyword in text for keyword in ["반드시", "필수", "꼭", "중요"]):
            return "high"
        elif any(keyword in text for keyword in ["가능하면", "원한다면", "바람직"]):
            return "medium"
        else:
            return "low"
    
    def analyze_design_intent(self, text: str, entities: List[ArchitecturalEntity]) -> List[DesignIntent]:
        """설계 의도 분석"""
        intents = []
        
        # 키워드 기반 의도 분석
        intent_keywords = {
            DesignIntent.FUNCTIONALITY: ["기능적", "실용적", "편리한", "효율적"],
            DesignIntent.AESTHETICS: ["아름다운", "예쁜", "멋진", "디자인", "스타일"],
            DesignIntent.EFFICIENCY: ["효율적", "절약", "경제적", "최적화"],
            DesignIntent.COMFORT: ["편안한", "쾌적한", "안락한", "편리한"],
            DesignIntent.SUSTAINABILITY: ["친환경", "지속가능", "에너지절약", "녹색"],
            DesignIntent.ACCESSIBILITY: ["접근성", "장애인", "노인", "유니버설"],
            DesignIntent.PRIVACY: ["프라이버시", "사생활", "개인적", "독립적"],
            DesignIntent.OPENNESS: ["개방적", "트인", "넓은", "확장"],
            DesignIntent.FLEXIBILITY: ["유연한", "가변적", "다목적", "변경가능"],
            DesignIntent.TRADITION: ["전통적", "한국적", "고전적", "한옥"]
        }
        
        for intent, keywords in intent_keywords.items():
            if any(keyword in text for keyword in keywords):
                intents.append(intent)
        
        return intents
    
    def classify_architectural_style(self, text: str, entities: List[ArchitecturalEntity]) -> Optional[ArchitecturalStyle]:
        """건축 스타일 분류"""
        style_scores = {}
        
        # 스타일별 키워드 매칭
        for style_category, keywords in self.architectural_styles.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                if "전통" in style_category:
                    style_scores[ArchitecturalStyle.HANOK] = score
                elif "근현대" in style_category:
                    style_scores[ArchitecturalStyle.MODERN] = score
                elif "고전" in style_category:
                    style_scores[ArchitecturalStyle.CLASSICAL] = score
        
        # 엔티티 기반 스타일 추론
        for entity in entities:
            if entity.entity_type == "BUILDING_TYPE":
                if "한옥" in str(entity.value):
                    style_scores[ArchitecturalStyle.HANOK] = style_scores.get(ArchitecturalStyle.HANOK, 0) + 3
                elif "아파트" in str(entity.value):
                    style_scores[ArchitecturalStyle.CONTEMPORARY] = style_scores.get(ArchitecturalStyle.CONTEMPORARY, 0) + 2
        
        # 최고 점수 스타일 반환
        if style_scores:
            return max(style_scores, key=style_scores.get)
        
        return None
    
    def analyze_sentiment(self, text: str) -> str:
        """감정 분석"""
        positive_words = ["좋은", "멋진", "아름다운", "훌륭한", "만족", "행복", "편안한"]
        negative_words = ["나쁜", "불편한", "문제", "어려운", "걱정", "불안", "답답한"]
        neutral_words = ["일반적인", "보통", "평범한", "기본적인"]
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        neutral_count = sum(1 for word in neutral_words if word in text)
        
        if positive_count > negative_count and positive_count > neutral_count:
            return "positive"
        elif negative_count > positive_count and negative_count > neutral_count:
            return "negative"
        else:
            return "neutral"
    
    def calculate_complexity_score(self, entities: List[ArchitecturalEntity], 
                                 spatial_relations: List[SpatialRelation],
                                 design_requirements: List[DesignRequirement]) -> float:
        """복잡도 점수 계산"""
        entity_score = len(entities) * 0.1
        relation_score = len(spatial_relations) * 0.2
        requirement_score = len(design_requirements) * 0.15
        
        # 엔티티 다양성 점수
        entity_types = set(entity.entity_type for entity in entities)
        diversity_score = len(entity_types) * 0.05
        
        total_score = entity_score + relation_score + requirement_score + diversity_score
        
        # 0.0 ~ 1.0 범위로 정규화
        return min(1.0, total_score)
    
    def _extract_keywords(self, tokens: List[str], pos_tags: List[Tuple[str, str]]) -> List[str]:
        """키워드 추출"""
        # 명사만 추출
        nouns = [word for word, pos in pos_tags if pos.startswith('N')]
        
        # 빈도 계산
        word_freq = Counter(nouns)
        
        # 상위 키워드 반환
        keywords = [word for word, count in word_freq.most_common(10)]
        return keywords
    
    def _extract_technical_terms(self, tokens: List[str], entities: List[ArchitecturalEntity]) -> List[str]:
        """전문 용어 추출"""
        technical_terms = []
        
        # 건축 전문 용어 사전
        architectural_terms = [
            "철근콘크리트", "조적", "목구조", "철골구조", "프리캐스트", "커튼월",
            "내력벽", "기둥", "보", "슬래브", "트러스", "아치", "돔",
            "단열재", "방수재", "마감재", "구조재", "시공", "설계", "시공도",
            "평면도", "입면도", "단면도", "배치도", "상세도", "구조도"
        ]
        
        for token in tokens:
            if token in architectural_terms:
                technical_terms.append(token)
        
        # 엔티티에서 전문 용어 추출
        for entity in entities:
            if entity.entity_type in ["ARCHITECTURAL_ELEMENT", "MATERIAL"]:
                if isinstance(entity.value, dict) and "element" in entity.value:
                    technical_terms.append(entity.value["element"])
                elif isinstance(entity.value, dict) and "material" in entity.value:
                    technical_terms.append(entity.value["material"])
        
        return list(set(technical_terms))  # 중복 제거
    
    def _calculate_comprehensive_confidence(self, entities: List[ArchitecturalEntity],
                                         spatial_relations: List[SpatialRelation],
                                         design_requirements: List[DesignRequirement],
                                         keywords: List[str]) -> float:
        """종합 신뢰도 계산"""
        if not entities and not spatial_relations and not design_requirements:
            return 0.0
        
        # 엔티티 신뢰도
        entity_confidence = sum(e.confidence for e in entities) / len(entities) if entities else 0.0
        
        # 관계 신뢰도
        relation_confidence = sum(r.confidence for r in spatial_relations) / len(spatial_relations) if spatial_relations else 0.0
        
        # 요구사항 품질 점수
        requirement_score = min(1.0, len(design_requirements) / 5.0) if design_requirements else 0.0
        
        # 키워드 커버리지
        keyword_score = min(1.0, len(keywords) / 10.0) if keywords else 0.0
        
        # 가중 평균
        weights = [0.4, 0.25, 0.2, 0.15]  # 엔티티, 관계, 요구사항, 키워드 순
        scores = [entity_confidence, relation_confidence, requirement_score, keyword_score]
        
        comprehensive_confidence = sum(w * s for w, s in zip(weights, scores))
        
        return max(0.0, min(1.0, comprehensive_confidence))
    
    def _update_processing_stats(self, result: ArchitecturalAnalysis) -> None:
        """처리 통계 업데이트"""
        self.processing_stats['total_processed'] += 1
        
        # 평균 신뢰도 업데이트
        total_confidence = (
            self.processing_stats['average_confidence'] * (self.processing_stats['total_processed'] - 1) +
            result.confidence
        ) / self.processing_stats['total_processed']
        
        self.processing_stats['average_confidence'] = total_confidence
        
        # 엔티티 추출 정확도 (간단한 휴리스틱)
        entity_accuracy = min(1.0, len(result.entities) / 10.0)
        self.processing_stats['entity_extraction_accuracy'] = (
            self.processing_stats['entity_extraction_accuracy'] * (self.processing_stats['total_processed'] - 1) +
            entity_accuracy
        ) / self.processing_stats['total_processed']
    
    def process_comprehensive_text(self, text: str) -> ArchitecturalAnalysis:
        """종합 건축 텍스트 처리 파이프라인 (확장)"""
        start_time = time.time()
        
        if not text or len(text.strip()) == 0:
            raise ValueError("텍스트가 비어있습니다")
        
        max_length = self.config.get('max_text_length', 10000)
        if len(text) > max_length:
            raise ValueError(f"텍스트 길이가 최대 제한을 초과합니다: {len(text)}")
        
        try:
            # 1. 텍스트 정규화
            normalized_text = self.normalize_text(text)
            
            # 2. 토크나이징 및 형태소 분석
            tokens = self.tokenize(normalized_text)
            pos_tags = self.pos_tag(normalized_text)
            
            # 3. 건축 엔티티 추출 (확장)
            entities = self.extract_comprehensive_entities(normalized_text)
            
            # 4. 공간 관계 분석
            spatial_relations = self.extract_spatial_relations(normalized_text)
            
            # 5. 설계 요구사항 추출
            design_requirements = self.extract_design_requirements(normalized_text, tokens)
            
            # 6. 설계 의도 분석
            design_intent = self.analyze_design_intent(normalized_text, entities)
            
            # 7. 건축 스타일 분류
            architectural_style = self.classify_architectural_style(normalized_text, entities)
            
            # 8. 키워드 및 전문용어 추출
            keywords = self._extract_keywords(tokens, pos_tags)
            technical_terms = self._extract_technical_terms(tokens, entities)
            
            # 9. 감정 분석
            sentiment = self.analyze_sentiment(normalized_text)
            
            # 10. 복잡도 평가
            complexity_score = self.calculate_complexity_score(entities, spatial_relations, design_requirements)
            
            # 11. 종합 신뢰도 계산
            confidence = self._calculate_comprehensive_confidence(
                entities, spatial_relations, design_requirements, keywords
            )
            
            # 성능 메트릭 기록
            processing_time = time.time() - start_time
            record_ai_inference_metric(
                model_type="korean_nlp",
                agent_type="korean_architecture_processor",
                duration=processing_time,
                accuracy=confidence,
                memory_usage=0,
                complexity="medium",
                status="success"
            )
            
            # 결과 생성
            result = ArchitecturalAnalysis(
                original_text=text,
                normalized_text=normalized_text,
                entities=entities,
                spatial_relations=spatial_relations,
                design_requirements=design_requirements,
                design_intent=design_intent,
                architectural_style=architectural_style,
                keywords=keywords,
                technical_terms=technical_terms,
                confidence=confidence,
                sentiment=sentiment,
                complexity_score=complexity_score
            )
            
            # 통계 업데이트
            self._update_processing_stats(result)
            
            logger.info(
                f"한국어 건축 분석 완료: 신뢰도 {confidence:.3f}, "
                f"엔티티 {len(entities)}개, 처리시간 {processing_time:.3f}초"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"한국어 건축 분석 오류: {e}")
            # 오류 메트릭 기록
            record_ai_inference_metric(
                model_type="korean_nlp",
                agent_type="korean_architecture_processor",
                duration=time.time() - start_time,
                accuracy=0.0,
                memory_usage=0,
                status="error"
            )
            raise


# 전역 프로세서 인스턴스
_korean_processor = None

def get_korean_architecture_processor() -> KoreanArchitectureProcessor:
    """한국어 건축 프로세서 싱글톤 인스턴스 반환"""
    global _korean_processor
    if _korean_processor is None:
        _korean_processor = KoreanArchitectureProcessor()
    return _korean_processor


# 하위 호환성을 위한 별칭
get_korean_processor = get_korean_architecture_processor
KoreanProcessor = KoreanArchitectureProcessor
BuildingEntity = ArchitecturalEntity


if __name__ == "__main__":
    # 테스트
    processor = KoreanArchitectureProcessor()
    
    test_text = """
    30평 규모의 현대적인 아파트를 설계하고 싶습니다. 
    거실과 주방이 연결된 개방적인 공간이 필요하고, 
    침실 3개와 화장실 2개가 있어야 합니다.
    남향으로 배치해서 밝고 쾌적한 환경을 만들고 싶습니다.
    """
    
    try:
        result = processor.process_comprehensive_text(test_text)
        print(f"분석 완료: 신뢰도 {result.confidence:.3f}")
        print(f"엔티티 수: {len(result.entities)}")
        print(f"공간 관계: {len(result.spatial_relations)}")
        print(f"설계 요구사항: {len(result.design_requirements)}")
        print(f"설계 의도: {[intent.value for intent in result.design_intent]}")
        print(f"건축 스타일: {result.architectural_style}")
        print(f"감정: {result.sentiment}")
        print(f"복잡도: {result.complexity_score:.3f}")
    except Exception as e:
        print(f"테스트 오류: {e}")