"""
한국어 건축 전문 자연어 처리 모듈
============================

건축 도메인 특화 한국어 텍스트 처리 및 설계 의도 분석

@version 2.0
@author VIBA AI Team
@date 2025.07.06
"""
import re
import json
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum

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
    """한국어 텍스트 처리 클래스"""
    
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
            # 형태소 분석기 초기화
            if self.tokenizer_type == TokenizerType.MECAB:
                self.tokenizer = Mecab()
            elif self.tokenizer_type == TokenizerType.OKT:
                self.tokenizer = Okt()
            elif self.tokenizer_type == TokenizerType.KOMORAN:
                self.tokenizer = Komoran()
            elif self.tokenizer_type == TokenizerType.HANNANUM:
                self.tokenizer = Hannanum()
            
            # 문장 임베딩 모델 초기화
            self.sentence_tokenizer = AutoTokenizer.from_pretrained(
                settings.sentence_model,
                cache_dir="./models_cache"
            )
            self.sentence_model = AutoModel.from_pretrained(
                settings.sentence_model,
                cache_dir="./models_cache"
            )
            
            logger.info(f"Korean processor initialized with {self.tokenizer_type.value} tokenizer")
            
        except Exception as e:
            logger.error(f"Failed to initialize Korean processor: {e}")
            raise
    
    def _load_comprehensive_building_types(self) -> Dict[str, List[str]]:
        """건물 타입 사전 로드"""
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
        """방 타입 사전 로드"""
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
    
    @log_execution_time("korean_text_normalization")
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
        
        logger.debug(f"Text normalized: {text[:50]}... -> {normalized[:50]}...")
        return normalized.strip()
    
    def _standardize_building_terms(self, text: str) -> str:
        """건축 용어 표준화"""
        # 동의어 매핑
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
        # 한글 숫자를 아라비아 숫자로 변환
        korean_to_arabic = {
            '일': '1', '이': '2', '삼': '3', '사': '4', '오': '5',
            '육': '6', '칠': '7', '팔': '8', '구': '9', '십': '10',
            '스무': '20', '서른': '30', '마흔': '40', '쉰': '50'
        }
        
        for korean, arabic in korean_to_arabic.items():
            text = re.sub(rf'\b{korean}\b', arabic, text)
        
        return text
    
    @log_execution_time("korean_tokenization")
    def tokenize(self, text: str) -> List[str]:
        """텍스트 토큰화"""
        if not text:
            return []
        
        try:
            # 형태소 분석기를 사용한 토큰화
            if hasattr(self.tokenizer, 'morphs'):
                tokens = self.tokenizer.morphs(text)
            else:
                tokens = text.split()
            
            # 불용어 제거 및 필터링
            filtered_tokens = self._filter_tokens(tokens)
            
            logger.debug(f"Tokenized {len(tokens)} -> {len(filtered_tokens)} tokens")
            return filtered_tokens
            
        except Exception as e:
            logger.error(f"Tokenization failed: {e}")
            return text.split()  # 기본 분할로 폴백
    
    def _filter_tokens(self, tokens: List[str]) -> List[str]:
        """토큰 필터링"""
        # 불용어 목록
        stopwords = {
            '을', '를', '이', '가', '은', '는', '에', '에서', '로', '으로',
            '의', '와', '과', '도', '만', '조차', '마저', '부터', '까지',
            '하고', '하여', '하니', '하면', '해서', '해도', '하지만',
            '그리고', '그런데', '그러나', '그래서', '따라서', '또한',
            '또는', '혹은', '아니면', '만약', '비록', '설령', '설사'
        }
        
        filtered = []
        for token in tokens:
            # 길이가 1인 토큰 제외 (조사, 어미 등)
            if len(token) < 2:
                continue
            
            # 불용어 제외
            if token in stopwords:
                continue
            
            # 숫자만 있는 토큰은 포함
            if token.isdigit():
                filtered.append(token)
                continue
            
            # 한글이 포함된 토큰만 포함
            if re.search(r'[가-힣]', token):
                filtered.append(token)
        
        return filtered
    
    @log_execution_time("korean_pos_tagging")
    def pos_tag(self, text: str) -> List[Tuple[str, str]]:
        """품사 태깅"""
        if not text:
            return []
        
        try:
            if hasattr(self.tokenizer, 'pos'):
                pos_tags = self.tokenizer.pos(text)
            else:
                # 기본 품사 태깅
                tokens = self.tokenize(text)
                pos_tags = [(token, 'NNG') for token in tokens]
            
            logger.debug(f"POS tagged {len(pos_tags)} tokens")
            return pos_tags
            
        except Exception as e:
            logger.error(f"POS tagging failed: {e}")
            return [(word, 'UNK') for word in text.split()]
    
    @log_execution_time("building_entity_extraction")
    def extract_building_entities(self, text: str) -> List[BuildingEntity]:
        """건축 관련 엔티티 추출"""
        entities = []
        
        # 건물 타입 추출
        entities.extend(self._extract_building_types(text))
        
        # 면적 정보 추출
        entities.extend(self._extract_areas(text))
        
        # 방향 정보 추출
        entities.extend(self._extract_orientations(text))
        
        # 방 타입 추출
        entities.extend(self._extract_room_types(text))
        
        # 층수 정보 추출
        entities.extend(self._extract_floors(text))
        
        logger.debug(f"Extracted {len(entities)} building entities")
        return entities
    
    def _extract_building_types(self, text: str) -> List[BuildingEntity]:
        """건물 타입 추출"""
        entities = []
        
        for building_type, synonyms in self.building_types.items():
            for synonym in synonyms:
                pattern = rf'\b{re.escape(synonym)}\b'
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    entities.append(BuildingEntity(
                        text=match.group(),
                        entity_type="BUILDING_TYPE",
                        value=building_type,
                        confidence=0.9,
                        start=match.start(),
                        end=match.end()
                    ))
        
        return entities
    
    def _extract_areas(self, text: str) -> List[BuildingEntity]:
        """면적 정보 추출"""
        entities = []
        
        for pattern in self.area_patterns:
            matches = pattern.finditer(text)
            
            for match in matches:
                try:
                    value = float(match.group(1))
                    unit = "평" if "평" in match.group() else "m2"
                    
                    entities.append(BuildingEntity(
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
    
    def _extract_orientations(self, text: str) -> List[BuildingEntity]:
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
                    entities.append(BuildingEntity(
                        text=match.group(),
                        entity_type="ORIENTATION",
                        value=standard_orientation,
                        confidence=0.9,
                        start=match.start(),
                        end=match.end()
                    ))
        
        return entities
    
    def _extract_room_types(self, text: str) -> List[BuildingEntity]:
        """방 타입 추출"""
        entities = []
        
        for room_type, synonyms in self.room_types.items():
            for synonym in synonyms:
                pattern = rf'\b{re.escape(synonym)}\b'
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    entities.append(BuildingEntity(
                        text=match.group(),
                        entity_type="ROOM_TYPE",
                        value=room_type,
                        confidence=0.85,
                        start=match.start(),
                        end=match.end()
                    ))
        
        return entities
    
    def _extract_floors(self, text: str) -> List[BuildingEntity]:
        """층수 정보 추출"""
        entities = []
        
        # 층수 패턴
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
                    # 한글 숫자를 아라비아 숫자로 변환
                    if floor_text.isdigit():
                        floor_value = int(floor_text)
                    else:
                        korean_numbers = {
                            '일': 1, '이': 2, '삼': 3, '사': 4, '오': 5,
                            '육': 6, '칠': 7, '팔': 8, '구': 9, '십': 10
                        }
                        floor_value = korean_numbers.get(floor_text, 1)
                    
                    entities.append(BuildingEntity(
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
    
    @log_execution_time("sentence_embedding")
    def get_sentence_embedding(self, text: str) -> np.ndarray:
        """문장 임베딩 생성"""
        if not text:
            return np.zeros(768)  # 기본 BERT 차원
        
        try:
            # 토큰화
            inputs = self.sentence_tokenizer(
                text,
                return_tensors="pt",
                max_length=512,
                truncation=True,
                padding=True
            )
            
            # 임베딩 생성
            with torch.no_grad():
                outputs = self.sentence_model(**inputs)
                # [CLS] 토큰의 임베딩 사용
                embedding = outputs.last_hidden_state[:, 0, :].numpy()
            
            return embedding.flatten()
            
        except Exception as e:
            logger.error(f"Sentence embedding failed: {e}")
            return np.zeros(768)
    
    def process_comprehensive_text(self, text: str) -> ArchitecturalAnalysis:
        """전체 텍스트 처리 파이프라인"""
        if not text or len(text) > settings.max_text_length:
            raise ValueError(f"Text length must be between 1 and {settings.max_text_length}")
        
        # 1. 텍스트 정규화
        normalized_text = self.normalize_text(text)
        
        # 2. 토큰화
        tokens = self.tokenize(normalized_text)
        
        # 3. 품사 태깅
        pos_tags = self.pos_tag(normalized_text)
        
        # 4. 엔티티 추출
        entities = self.extract_building_entities(normalized_text)
        
        # 5. 키워드 추출
        keywords = self._extract_keywords(tokens, pos_tags)
        
        # 6. 신뢰도 계산
        confidence = self._calculate_confidence(entities, keywords, tokens)
        
        result = ProcessedText(
            original_text=text,
            normalized_text=normalized_text,
            tokens=tokens,
            pos_tags=pos_tags,
            entities=[{
                "text": e.text,
                "type": e.entity_type,
                "value": e.value,
                "confidence": e.confidence,
                "start": e.start,
                "end": e.end
            } for e in entities],
            keywords=keywords,
            confidence=confidence
        )
        
        log_nlp_result("korean_processing", text, result.__dict__, confidence)
        return result
    
    def _extract_keywords(self, tokens: List[str], pos_tags: List[Tuple[str, str]]) -> List[str]:
        """키워드 추출"""
        # 명사만 추출
        nouns = [word for word, pos in pos_tags if pos.startswith('N')]
        
        # 빈도 계산
        from collections import Counter
        word_freq = Counter(nouns)
        
        # 상위 키워드 반환
        keywords = [word for word, count in word_freq.most_common(10)]
        return keywords
    
    def _calculate_confidence(self, entities: List[BuildingEntity], keywords: List[str], tokens: List[str]) -> float:
        """전체 처리 신뢰도 계산"""
        if not tokens:
            return 0.0
        
        # 엔티티 기반 신뢰도
        entity_confidence = sum(e.confidence for e in entities) / len(entities) if entities else 0.0
        
        # 키워드 기반 신뢰도
        keyword_ratio = len(keywords) / len(tokens) if tokens else 0.0
        
        # 텍스트 품질 기반 신뢰도
        quality_score = min(1.0, len(tokens) / 10)  # 토큰 수 기반
        
        # 종합 신뢰도
        overall_confidence = (entity_confidence * 0.5 + keyword_ratio * 0.3 + quality_score * 0.2)
        
        return max(0.0, min(1.0, overall_confidence))


# 전역 프로세서 인스턴스
_korean_processor = None

def get_korean_processor() -> KoreanProcessor:
    """한국어 프로세서 싱글톤 인스턴스 반환"""
    global _korean_processor
    if _korean_processor is None:
        _korean_processor = KoreanProcessor()
    return _korean_processor