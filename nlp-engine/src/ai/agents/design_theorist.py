"""
설계 이론가 AI 에이전트
====================

건축 설계 이론과 원칙을 적용하여 사용자 요구사항을 건축적 설계 개념으로 변환하는 AI 에이전트

@version 1.0
@author VIBA AI Team
@date 2025.07.06
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)

# AI/ML 라이브러리 (optional import with fallback)
try:
    from transformers import AutoTokenizer, AutoModel, pipeline
    import torch
    from sentence_transformers import SentenceTransformer
    ML_LIBRARIES_AVAILABLE = True
except ImportError:
    ML_LIBRARIES_AVAILABLE = False
    # Mock implementations
    class SentenceTransformer:
        def __init__(self, *args, **kwargs): pass
        def encode(self, texts): return np.random.rand(len(texts) if isinstance(texts, list) else 1, 384)

# 프로젝트 임포트
try:
    from ..base_agent import BaseVIBAAgent, AgentCapability
    from ...utils.metrics_collector import record_ai_inference_metric
except ImportError:
    # 직접 실행 시 절대 경로로 임포트
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ai.base_agent import BaseVIBAAgent, AgentCapability
    
    # 메트릭 수집기가 없으면 더미 함수 사용
    def record_ai_inference_metric(*args, **kwargs):
        pass

# Knowledge imports
try:
    from ...knowledge.architectural_theory import ArchitecturalTheoryKnowledgeBase
    from ...knowledge.design_patterns import DesignPatternLibrary
    KNOWLEDGE_MODULES_AVAILABLE = True
except ImportError:
    logger.warning("Knowledge modules not available, using basic implementations")
    ArchitecturalTheoryKnowledgeBase = None
    DesignPatternLibrary = None
    KNOWLEDGE_MODULES_AVAILABLE = False

try:
    from ...processors.korean_processor import KoreanArchitectureProcessor
except ImportError:
    logger.warning("Korean processor not available")
    KoreanArchitectureProcessor = None

logger = logging.getLogger(__name__)


class DesignStyle(Enum):
    """건축 설계 스타일"""
    MODERN = "modern"
    TRADITIONAL = "traditional"
    HANOK = "hanok"
    MINIMALIST = "minimalist"
    CLASSICAL = "classical"
    SUSTAINABLE = "sustainable"
    INDUSTRIAL = "industrial"
    CONTEMPORARY = "contemporary"


class DesignPrinciple(Enum):
    """설계 원칙"""
    PROPORTION = "proportion"  # 비례
    SCALE = "scale"           # 스케일
    RHYTHM = "rhythm"         # 리듬
    BALANCE = "balance"       # 균형
    UNITY = "unity"           # 통일성
    CONTRAST = "contrast"     # 대비
    EMPHASIS = "emphasis"     # 강조
    MOVEMENT = "movement"     # 동선


@dataclass
class DesignConcept:
    """설계 개념"""
    building_type: str
    primary_style: DesignStyle
    secondary_styles: List[DesignStyle] = field(default_factory=list)
    design_principles: List[DesignPrinciple] = field(default_factory=list)
    
    # 공간 구성
    spatial_organization: Dict[str, Any] = field(default_factory=dict)
    circulation_pattern: str = ""
    zoning_strategy: str = ""
    
    # 형태 및 비례
    form_concept: str = ""
    proportional_system: Dict[str, float] = field(default_factory=dict)
    dimensional_guidelines: Dict[str, float] = field(default_factory=dict)
    
    # 재료 및 색채
    material_palette: List[str] = field(default_factory=list)
    color_scheme: Dict[str, str] = field(default_factory=dict)
    texture_strategy: str = ""
    
    # 환경 및 지속가능성
    environmental_strategy: Dict[str, Any] = field(default_factory=dict)
    energy_concept: str = ""
    lighting_strategy: str = ""
    
    # 문화적 맥락
    cultural_references: List[str] = field(default_factory=list)
    regional_adaptations: Dict[str, Any] = field(default_factory=dict)
    
    # 품질 메트릭
    concept_confidence: float = 0.0
    theoretical_soundness: float = 0.0
    innovation_score: float = 0.0


class DesignTheoristAgent(BaseVIBAAgent):
    """설계 이론가 AI 에이전트"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        설계 이론가 에이전트 초기화
        
        Args:
            config: 에이전트 설정
        """
        super().__init__(
            agent_id="design_theorist",
            name="설계 이론가",
            capabilities=[
                AgentCapability.NATURAL_LANGUAGE_UNDERSTANDING,
                AgentCapability.DESIGN_THEORY_APPLICATION,
                AgentCapability.SPATIAL_PLANNING,
                AgentCapability.CULTURAL_ADAPTATION
            ],
            config=config
        )
        
        # AI 모델 초기화
        self.tokenizer: Optional[AutoTokenizer] = None
        self.model: Optional[AutoModel] = None
        self.sentence_transformer: Optional[SentenceTransformer] = None
        self.korean_processor: Optional[KoreanArchitectureProcessor] = None
        
        # 지식 베이스
        self.theory_knowledge: Optional[ArchitecturalTheoryKnowledgeBase] = None
        self.pattern_library: Optional[DesignPatternLibrary] = None
        
        # 설계 템플릿
        self.design_templates = self._load_design_templates()
        
        # 성능 캐시
        self.concept_cache: Dict[str, DesignConcept] = {}
        
        logger.info("설계 이론가 AI 에이전트 초기화 완료")
    
    async def initialize(self) -> bool:
        """에이전트 초기화"""
        try:
            logger.info("설계 이론가 에이전트 초기화 중...")
            
            # 1. AI 모델 로드
            await self._load_ai_models()
            
            # 2. 지식 베이스 로드
            await self._load_knowledge_bases()
            
            # 3. 한국어 처리기 초기화
            self.korean_processor = KoreanArchitectureProcessor()
            await self.korean_processor.initialize()
            
            # 4. 설계 이론 검증
            await self._validate_design_theories()
            
            self.is_initialized = True
            logger.info("✅ 설계 이론가 에이전트 초기화 완료")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 설계 이론가 에이전트 초기화 실패: {e}")
            return False
    
    async def _load_ai_models(self):
        """AI 모델 로드"""
        logger.info("AI 모델 로드 중...")
        
        # 1. 한국어 BERT 모델 (건축 도메인 특화)
        model_name = "klue/bert-base"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        
        # 2. 다국어 문장 임베딩 모델
        self.sentence_transformer = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        logger.info("AI 모델 로드 완료")
    
    async def _load_knowledge_bases(self):
        """지식 베이스 로드"""
        logger.info("건축 이론 지식 베이스 로드 중...")
        
        # 건축 이론 지식 베이스
        self.theory_knowledge = ArchitecturalTheoryKnowledgeBase()
        await self.theory_knowledge.initialize()
        
        # 설계 패턴 라이브러리
        self.pattern_library = DesignPatternLibrary()
        await self.pattern_library.initialize()
        
        logger.info("지식 베이스 로드 완료")
    
    async def _validate_design_theories(self):
        """설계 이론 검증"""
        # 로드된 이론들의 일관성 및 완전성 검증
        theory_count = len(self.theory_knowledge.theories) if self.theory_knowledge else 0
        pattern_count = len(self.pattern_library.patterns) if self.pattern_library else 0
        
        logger.info(f"검증 완료: {theory_count}개 이론, {pattern_count}개 패턴")
    
    def _load_design_templates(self) -> Dict[str, Dict[str, Any]]:
        """설계 템플릿 로드"""
        return {
            "residential": {
                "single_family": {
                    "spatial_zones": ["private", "semi_private", "public"],
                    "circulation": "centralized",
                    "proportion_system": "golden_ratio",
                    "materials": ["wood", "stone", "glass", "steel"],
                    "lighting": "natural_primary"
                },
                "multi_family": {
                    "spatial_zones": ["private", "shared", "public"],
                    "circulation": "corridor_based",
                    "proportion_system": "modular",
                    "materials": ["concrete", "brick", "glass"],
                    "lighting": "mixed"
                }
            },
            "commercial": {
                "office": {
                    "spatial_zones": ["work", "meeting", "support", "circulation"],
                    "circulation": "open_plan",
                    "proportion_system": "grid_based",
                    "materials": ["steel", "glass", "aluminum"],
                    "lighting": "artificial_primary"
                },
                "retail": {
                    "spatial_zones": ["display", "service", "storage", "customer"],
                    "circulation": "guided_flow",
                    "proportion_system": "flexible",
                    "materials": ["varied", "branded"],
                    "lighting": "accent_focused"
                }
            },
            "institutional": {
                "educational": {
                    "spatial_zones": ["learning", "social", "service", "administration"],
                    "circulation": "hierarchical",
                    "proportion_system": "human_scale",
                    "materials": ["durable", "natural"],
                    "lighting": "natural_optimized"
                }
            }
        }
    
    async def execute_task(self, task) -> Dict[str, Any]:
        """설계 작업 실행"""
        task_type = task.task_type
        start_time = time.time()
        
        try:
            if task_type == "nlp_analysis":
                result = await self._analyze_user_requirements(task.input_data)
            elif task_type == "theory_application":
                result = await self._apply_design_theory(task.input_data)
            else:
                raise ValueError(f"지원하지 않는 작업 타입: {task_type}")
            
            # 성능 메트릭 기록
            duration = time.time() - start_time
            record_ai_inference_metric(
                model_type="design_theory",
                agent_type="design_theorist", 
                duration=duration,
                accuracy=result.get('confidence', 0.0),
                memory_usage=self._get_memory_usage()
            )
            
            return result
            
        except Exception as e:
            logger.error(f"설계 작업 실행 실패: {e}")
            raise
    
    async def _analyze_user_requirements(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """사용자 요구사항 분석"""
        user_input = input_data.get('user_input', '')
        context = input_data.get('context', {})
        
        logger.info(f"사용자 요구사항 분석 시작: '{user_input[:50]}...'")
        
        # 1. 한국어 자연어 처리
        nlp_result = await self.korean_processor.process_text(user_input)
        
        # 2. 건축 요소 추출
        architectural_elements = await self._extract_architectural_elements(nlp_result)
        
        # 3. 의도 분류
        design_intent = await self._classify_design_intent(nlp_result, architectural_elements)
        
        # 4. 제약 조건 식별
        constraints = await self._identify_constraints(nlp_result, context)
        
        # 5. 우선순위 분석
        priorities = await self._analyze_priorities(nlp_result, architectural_elements)
        
        result = {
            "analysis_type": "user_requirements",
            "original_input": user_input,
            "nlp_result": nlp_result,
            "architectural_elements": architectural_elements,
            "design_intent": design_intent,
            "constraints": constraints,
            "priorities": priorities,
            "confidence": self._calculate_analysis_confidence(nlp_result, architectural_elements),
            "processing_time": time.time()
        }
        
        logger.info(f"요구사항 분석 완료: 신뢰도 {result['confidence']:.2f}")
        
        return result
    
    async def _extract_architectural_elements(self, nlp_result: Dict[str, Any]) -> Dict[str, Any]:
        """건축 요소 추출"""
        tokens = nlp_result.get('tokens', [])
        entities = nlp_result.get('entities', [])
        
        elements = {
            "building_type": None,
            "style_keywords": [],
            "spatial_requirements": [],
            "functional_requirements": [],
            "aesthetic_preferences": [],
            "technical_requirements": [],
            "location_context": {},
            "scale_indicators": {}
        }
        
        # 건물 유형 식별
        building_types = {
            "주택": "residential",
            "단독주택": "single_family_house", 
            "아파트": "apartment",
            "상가": "commercial",
            "사무소": "office",
            "오피스": "office",
            "학교": "school",
            "병원": "hospital",
            "교회": "church",
            "카페": "cafe",
            "레스토랑": "restaurant",
            "게스트하우스": "guesthouse",
            "펜션": "pension"
        }
        
        for token in tokens:
            for korean_term, building_type in building_types.items():
                if korean_term in token:
                    elements["building_type"] = building_type
                    break
        
        # 스타일 키워드 추출
        style_keywords = {
            "현대적": "modern",
            "모던": "modern", 
            "전통": "traditional",
            "한옥": "hanok",
            "미니멀": "minimalist",
            "클래식": "classical",
            "친환경": "sustainable",
            "지속가능": "sustainable",
            "산업": "industrial",
            "컨템포러리": "contemporary"
        }
        
        for token in tokens:
            for korean_style, style_type in style_keywords.items():
                if korean_style in token:
                    elements["style_keywords"].append(style_type)
        
        # 공간 요구사항 추출
        spatial_terms = {
            "거실": "living_room",
            "침실": "bedroom", 
            "주방": "kitchen",
            "화장실": "bathroom",
            "욕실": "bathroom",
            "서재": "study",
            "작업실": "workshop",
            "차고": "garage",
            "발코니": "balcony",
            "테라스": "terrace",
            "정원": "garden",
            "마당": "yard"
        }
        
        for token in tokens:
            for korean_space, space_type in spatial_terms.items():
                if korean_space in token:
                    elements["spatial_requirements"].append(space_type)
        
        # 기능적 요구사항 추출  
        functional_terms = {
            "주차": "parking",
            "저장": "storage",
            "수납": "storage",
            "채광": "natural_lighting",
            "통풍": "ventilation",
            "단열": "insulation",
            "방음": "soundproofing",
            "보안": "security",
            "접근성": "accessibility"
        }
        
        for token in tokens:
            for korean_func, func_type in functional_terms.items():
                if korean_func in token:
                    elements["functional_requirements"].append(func_type)
        
        # 위치 맥락 추출
        location_entities = [e for e in entities if e.get('label') == 'LOCATION']
        for entity in location_entities:
            location_text = entity.get('text', '')
            elements["location_context"]["raw"] = location_text
            
            # 지역별 특성 매핑
            if "강남" in location_text:
                elements["location_context"]["district"] = "gangnam"
                elements["location_context"]["characteristics"] = ["urban", "upscale", "dense"]
            elif "서울" in location_text:
                elements["location_context"]["city"] = "seoul"
                elements["location_context"]["characteristics"] = ["metropolitan", "urban"]
        
        # 규모 지표 추출
        numbers = nlp_result.get('numbers', [])
        for num_info in numbers:
            value = num_info.get('value')
            context_words = num_info.get('context', [])
            
            if any(word in context_words for word in ['층', '층수']):
                elements["scale_indicators"]["floors"] = value
            elif any(word in context_words for word in ['평', '제곱미터', 'm2']):
                elements["scale_indicators"]["area"] = value
            elif any(word in context_words for word in ['억', '만원']):
                elements["scale_indicators"]["budget"] = value
        
        return elements
    
    async def _classify_design_intent(self, nlp_result: Dict[str, Any], 
                                    architectural_elements: Dict[str, Any]) -> Dict[str, Any]:
        """설계 의도 분류"""
        text = nlp_result.get('original_text', '')
        
        # 문장 임베딩 생성
        embeddings = self.sentence_transformer.encode([text])
        
        # 의도 분류 카테고리
        intent_categories = {
            "functional": "기능성 중심",
            "aesthetic": "미적 가치 중심", 
            "sustainable": "지속가능성 중심",
            "comfort": "거주 편의성 중심",
            "economic": "경제성 중심",
            "cultural": "문화적 가치 중심",
            "innovative": "혁신성 중심"
        }
        
        # 키워드 기반 의도 분석
        intent_scores = {}
        
        # 기능성 키워드
        functional_keywords = ["편리", "실용", "기능", "효율", "활용", "동선"]
        functional_score = sum(1 for keyword in functional_keywords if keyword in text) / len(functional_keywords)
        intent_scores["functional"] = functional_score
        
        # 미적 키워드
        aesthetic_keywords = ["아름다운", "예쁜", "멋진", "세련된", "디자인", "스타일"]
        aesthetic_score = sum(1 for keyword in aesthetic_keywords if keyword in text) / len(aesthetic_keywords)
        intent_scores["aesthetic"] = aesthetic_score
        
        # 지속가능성 키워드
        sustainable_keywords = ["친환경", "에너지", "효율", "지속가능", "자연", "그린"]
        sustainable_score = sum(1 for keyword in sustainable_keywords if keyword in text) / len(sustainable_keywords)
        intent_scores["sustainable"] = sustainable_score
        
        # 편안함 키워드
        comfort_keywords = ["편안", "아늑", "따뜻", "쾌적", "안락", "휴식"]
        comfort_score = sum(1 for keyword in comfort_keywords if keyword in text) / len(comfort_keywords)
        intent_scores["comfort"] = comfort_score
        
        # 경제성 키워드
        economic_keywords = ["저렴", "경제", "예산", "비용", "효과", "절약"]
        economic_score = sum(1 for keyword in economic_keywords if keyword in text) / len(economic_keywords)
        intent_scores["economic"] = economic_score
        
        # 문화적 키워드
        cultural_keywords = ["전통", "한국", "한옥", "문화", "역사", "현지"]
        cultural_score = sum(1 for keyword in cultural_keywords if keyword in text) / len(cultural_keywords)
        intent_scores["cultural"] = cultural_score
        
        # 혁신성 키워드
        innovation_keywords = ["새로운", "혁신", "독특", "창의", "참신", "특별"]
        innovation_score = sum(1 for keyword in innovation_keywords if keyword in text) / len(innovation_keywords)
        intent_scores["innovative"] = innovation_score
        
        # 상위 의도 선정
        primary_intent = max(intent_scores.items(), key=lambda x: x[1])
        secondary_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)[1:3]
        
        return {
            "primary_intent": {
                "category": primary_intent[0],
                "description": intent_categories[primary_intent[0]],
                "confidence": primary_intent[1]
            },
            "secondary_intents": [
                {
                    "category": intent[0],
                    "description": intent_categories[intent[0]], 
                    "confidence": intent[1]
                }
                for intent in secondary_intents if intent[1] > 0.1
            ],
            "intent_scores": intent_scores
        }
    
    async def _identify_constraints(self, nlp_result: Dict[str, Any], 
                                  context: Dict[str, Any]) -> Dict[str, Any]:
        """제약 조건 식별"""
        constraints = {
            "budget": {},
            "site": {},
            "regulatory": {},
            "functional": {},
            "temporal": {},
            "aesthetic": {}
        }
        
        # 예산 제약
        numbers = nlp_result.get('numbers', [])
        for num_info in numbers:
            context_words = num_info.get('context', [])
            if any(word in context_words for word in ['예산', '비용', '억', '만원']):
                constraints["budget"] = {
                    "max_budget": num_info.get('value'),
                    "currency": "KRW",
                    "flexibility": "medium"
                }
        
        # 부지 제약
        if context.get('lot_size'):
            constraints["site"]["area"] = context['lot_size']
        if context.get('max_floors'):
            constraints["site"]["max_floors"] = context['max_floors']
        
        # 법규 제약 (컨텍스트에서)
        if context.get('building_coverage_ratio'):
            constraints["regulatory"]["building_coverage"] = context['building_coverage_ratio']
        if context.get('floor_area_ratio'):
            constraints["regulatory"]["floor_area_ratio"] = context['floor_area_ratio']
        
        # 기능적 제약
        text = nlp_result.get('original_text', '')
        if "주차" in text:
            constraints["functional"]["parking_required"] = True
        if "접근성" in text:
            constraints["functional"]["accessibility_required"] = True
        
        # 시간적 제약
        if context.get('timeline'):
            constraints["temporal"]["completion_deadline"] = context['timeline']
        
        return constraints
    
    async def _analyze_priorities(self, nlp_result: Dict[str, Any], 
                                architectural_elements: Dict[str, Any]) -> Dict[str, Any]:
        """우선순위 분석"""
        text = nlp_result.get('original_text', '')
        
        # 강조 표현 탐지
        emphasis_patterns = {
            "중요": 0.8,
            "필수": 0.9,
            "반드시": 0.9,
            "꼭": 0.8,
            "특히": 0.7,
            "우선": 0.8,
            "먼저": 0.7
        }
        
        priorities = {
            "functional_priorities": [],
            "aesthetic_priorities": [],
            "performance_priorities": [],
            "priority_scores": {}
        }
        
        # 기능적 우선순위
        functional_requirements = architectural_elements.get('functional_requirements', [])
        for requirement in functional_requirements:
            score = 0.5  # 기본 점수
            
            # 강조 표현으로 점수 조정
            for pattern, weight in emphasis_patterns.items():
                if pattern in text and requirement in text:
                    score = max(score, weight)
            
            priorities["functional_priorities"].append({
                "requirement": requirement,
                "priority_score": score
            })
        
        # 미적 우선순위
        style_keywords = architectural_elements.get('style_keywords', [])
        for style in style_keywords:
            score = 0.6  # 스타일 기본 점수
            priorities["aesthetic_priorities"].append({
                "style": style,
                "priority_score": score
            })
        
        # 성능 우선순위
        performance_keywords = {
            "에너지": "energy_efficiency",
            "단열": "thermal_performance", 
            "채광": "daylighting",
            "통풍": "ventilation",
            "방음": "acoustic_performance"
        }
        
        for keyword, performance_type in performance_keywords.items():
            if keyword in text:
                score = 0.7
                priorities["performance_priorities"].append({
                    "performance_type": performance_type,
                    "priority_score": score
                })
        
        return priorities
    
    def _calculate_analysis_confidence(self, nlp_result: Dict[str, Any], 
                                     architectural_elements: Dict[str, Any]) -> float:
        """분석 신뢰도 계산"""
        confidence_factors = []
        
        # 텍스트 길이 기반 신뢰도
        text_length = len(nlp_result.get('original_text', ''))
        length_confidence = min(1.0, text_length / 100)  # 100자 기준
        confidence_factors.append(length_confidence * 0.2)
        
        # 건축 요소 추출 완성도
        building_type = architectural_elements.get('building_type')
        type_confidence = 0.8 if building_type else 0.3
        confidence_factors.append(type_confidence * 0.3)
        
        # 스타일 키워드 존재
        style_count = len(architectural_elements.get('style_keywords', []))
        style_confidence = min(1.0, style_count / 2)  # 2개 기준
        confidence_factors.append(style_confidence * 0.2)
        
        # 공간 요구사항 명확성
        spatial_count = len(architectural_elements.get('spatial_requirements', []))
        spatial_confidence = min(1.0, spatial_count / 3)  # 3개 기준
        confidence_factors.append(spatial_confidence * 0.2)
        
        # 제약 조건 명시
        scale_indicators = architectural_elements.get('scale_indicators', {})
        constraint_confidence = len(scale_indicators) / 3  # 층수, 면적, 예산
        confidence_factors.append(min(1.0, constraint_confidence) * 0.1)
        
        return sum(confidence_factors)
    
    async def _apply_design_theory(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """설계 이론 적용"""
        building_type = input_data.get('building_type', '')
        style_preferences = input_data.get('style_preferences', [])
        constraints = input_data.get('constraints', {})
        
        logger.info(f"설계 이론 적용 시작: {building_type}, 스타일: {style_preferences}")
        
        # 1. 기본 설계 개념 생성
        base_concept = await self._generate_base_concept(building_type, style_preferences)
        
        # 2. 비례 시스템 적용
        proportional_system = await self._apply_proportional_system(base_concept, style_preferences)
        
        # 3. 공간 구성 이론 적용
        spatial_organization = await self._apply_spatial_theory(base_concept, building_type)
        
        # 4. 문화적 맥락 적용
        cultural_adaptation = await self._apply_cultural_context(base_concept, style_preferences)
        
        # 5. 지속가능성 원칙 적용
        sustainability_strategy = await self._apply_sustainability_principles(base_concept, constraints)
        
        # 6. 종합 설계 개념 생성
        design_concept = DesignConcept(
            building_type=building_type,
            primary_style=DesignStyle(style_preferences[0]) if style_preferences else DesignStyle.MODERN,
            secondary_styles=[DesignStyle(s) for s in style_preferences[1:3]],
            design_principles=self._extract_design_principles(style_preferences),
            spatial_organization=spatial_organization,
            proportional_system=proportional_system,
            environmental_strategy=sustainability_strategy,
            cultural_references=cultural_adaptation.get('references', []),
            regional_adaptations=cultural_adaptation.get('adaptations', {}),
            concept_confidence=self._calculate_concept_confidence(base_concept, proportional_system, spatial_organization),
            theoretical_soundness=self._evaluate_theoretical_soundness(base_concept),
            innovation_score=self._calculate_innovation_score(base_concept, style_preferences)
        )
        
        # 7. 설계 가이드라인 생성
        design_guidelines = await self._generate_design_guidelines(design_concept)
        
        result = {
            "analysis_type": "design_theory_application",
            "design_concept": design_concept.__dict__,
            "design_guidelines": design_guidelines,
            "theoretical_references": await self._get_theoretical_references(style_preferences),
            "confidence": design_concept.concept_confidence,
            "processing_time": time.time()
        }
        
        logger.info(f"설계 이론 적용 완료: 신뢰도 {design_concept.concept_confidence:.2f}")
        
        return result
    
    async def _generate_base_concept(self, building_type: str, style_preferences: List[str]) -> Dict[str, Any]:
        """기본 설계 개념 생성"""
        # 건물 유형별 기본 개념 매핑
        type_concepts = {
            "single_family_house": {
                "form_concept": "Human-scale domestic architecture",
                "circulation": "Central living with private wings",
                "zoning": "Public-private gradient"
            },
            "apartment": {
                "form_concept": "Efficient vertical living",
                "circulation": "Corridor-based access",
                "zoning": "Repeated unit modules"
            },
            "office": {
                "form_concept": "Flexible work environment",
                "circulation": "Open plan with circulation spine",
                "zoning": "Collaboration zones with quiet areas"
            }
        }
        
        base_concept = type_concepts.get(building_type, {
            "form_concept": "Context-responsive architecture",
            "circulation": "Efficient movement patterns", 
            "zoning": "Functional separation"
        })
        
        # 스타일 기반 조정
        if "hanok" in style_preferences:
            base_concept["form_concept"] += " with traditional Korean spatial principles"
            base_concept["circulation"] = "Courtyard-centered circulation"
            base_concept["zoning"] = "Inside-outside flow"
        elif "minimalist" in style_preferences:
            base_concept["form_concept"] = "Pure geometric forms with essential elements"
            base_concept["circulation"] = "Clean, unobstructed movement"
            base_concept["zoning"] = "Open, flexible spaces"
        
        return base_concept
    
    async def _apply_proportional_system(self, base_concept: Dict[str, Any], 
                                       style_preferences: List[str]) -> Dict[str, float]:
        """비례 시스템 적용"""
        proportional_systems = {
            "golden_ratio": {
                "primary_ratio": 1.618,
                "secondary_ratio": 2.618,  # φ + 1
                "tertiary_ratio": 0.618   # 1/φ
            },
            "modular": {
                "primary_ratio": 1.0,
                "secondary_ratio": 2.0,
                "tertiary_ratio": 0.5
            },
            "tatami": {  # 한옥/다다미 비례
                "primary_ratio": 2.0,     # 2:1 비례
                "secondary_ratio": 1.414, # √2
                "tertiary_ratio": 0.707   # 1/√2
            },
            "classical": {
                "primary_ratio": 1.667,   # 5:3
                "secondary_ratio": 1.333, # 4:3
                "tertiary_ratio": 0.75    # 3:4
            }
        }
        
        # 스타일에 따른 비례 시스템 선택
        if "hanok" in style_preferences or "traditional" in style_preferences:
            selected_system = "tatami"
        elif "classical" in style_preferences:
            selected_system = "classical"
        elif "minimalist" in style_preferences:
            selected_system = "modular"
        else:
            selected_system = "golden_ratio"  # 기본값
        
        proportions = proportional_systems[selected_system].copy()
        proportions["system_type"] = selected_system
        
        return proportions
    
    async def _apply_spatial_theory(self, base_concept: Dict[str, Any], 
                                  building_type: str) -> Dict[str, Any]:
        """공간 구성 이론 적용"""
        spatial_theories = {
            "single_family_house": {
                "organization_type": "zoned",
                "primary_zones": ["public", "private", "service"],
                "circulation_strategy": "central_core",
                "spatial_hierarchy": "living_centered",
                "flexibility": "medium",
                "privacy_gradation": True
            },
            "apartment": {
                "organization_type": "cellular",
                "primary_zones": ["living", "sleeping", "service"],
                "circulation_strategy": "linear",
                "spatial_hierarchy": "efficient_compact",
                "flexibility": "low",
                "privacy_gradation": True
            },
            "office": {
                "organization_type": "open_plan",
                "primary_zones": ["work", "meeting", "support", "circulation"],
                "circulation_strategy": "grid_based",
                "spatial_hierarchy": "collaborative_focused",
                "flexibility": "high",
                "privacy_gradation": False
            }
        }
        
        return spatial_theories.get(building_type, {
            "organization_type": "flexible",
            "primary_zones": ["primary", "secondary", "service"],
            "circulation_strategy": "adaptive",
            "spatial_hierarchy": "user_defined",
            "flexibility": "medium",
            "privacy_gradation": True
        })
    
    async def _apply_cultural_context(self, base_concept: Dict[str, Any], 
                                    style_preferences: List[str]) -> Dict[str, Any]:
        """문화적 맥락 적용"""
        cultural_adaptations = {
            "hanok": {
                "references": ["조선시대 한옥", "마당 중심 구성", "자연과의 조화"],
                "adaptations": {
                    "spatial_concept": "마루-온돌 시스템",
                    "material_preference": "목재, 기와, 한지",
                    "proportional_system": "柱間法 (주간법)",
                    "environmental_strategy": "자연 통풍, 채광 최적화"
                }
            },
            "traditional": {
                "references": ["한국 전통 건축", "지역 건축 문화"],
                "adaptations": {
                    "spatial_concept": "전통 공간 위계",
                    "material_preference": "자연 재료 중심",
                    "proportional_system": "전통 척도 시스템",
                    "environmental_strategy": "기후 적응형 설계"
                }
            },
            "modern": {
                "references": ["모더니즘", "국제양식", "기능주의"],
                "adaptations": {
                    "spatial_concept": "기능적 공간 분리",
                    "material_preference": "콘크리트, 강철, 유리",
                    "proportional_system": "모듈러 시스템",
                    "environmental_strategy": "기계적 환경 제어"
                }
            }
        }
        
        # 주요 스타일의 문화적 맥락 선택
        primary_style = style_preferences[0] if style_preferences else "modern"
        
        return cultural_adaptations.get(primary_style, {
            "references": ["현대 건축"],
            "adaptations": {
                "spatial_concept": "기능 중심 공간",
                "material_preference": "현대적 재료",
                "proportional_system": "합리적 비례",
                "environmental_strategy": "효율적 성능"
            }
        })
    
    async def _apply_sustainability_principles(self, base_concept: Dict[str, Any], 
                                             constraints: Dict[str, Any]) -> Dict[str, Any]:
        """지속가능성 원칙 적용"""
        sustainability_strategy = {
            "energy_concept": "passive_first",
            "materials_strategy": "local_sustainable",
            "water_management": "rainwater_harvesting",
            "waste_reduction": "construction_optimization",
            "bioclimatic_design": True,
            "renewable_energy": "solar_primary",
            "thermal_performance": {
                "insulation_strategy": "high_performance",
                "thermal_mass": "optimized",
                "air_sealing": "continuous"
            },
            "daylighting": {
                "strategy": "bilateral_lighting",
                "glare_control": "dynamic_shading",
                "light_quality": "full_spectrum"
            },
            "ventilation": {
                "strategy": "natural_primary",
                "heat_recovery": True,
                "air_quality": "filtered_fresh"
            }
        }
        
        # 제약 조건에 따른 조정
        budget = constraints.get('budget', {})
        if budget.get('max_budget', 0) < 500000000:  # 5억 미만
            sustainability_strategy["renewable_energy"] = "grid_tied_small"
            sustainability_strategy["materials_strategy"] = "cost_effective_sustainable"
        
        return sustainability_strategy
    
    def _extract_design_principles(self, style_preferences: List[str]) -> List[DesignPrinciple]:
        """설계 원칙 추출"""
        style_principles = {
            "modern": [DesignPrinciple.PROPORTION, DesignPrinciple.UNITY, DesignPrinciple.EMPHASIS],
            "minimalist": [DesignPrinciple.PROPORTION, DesignPrinciple.UNITY, DesignPrinciple.BALANCE],
            "hanok": [DesignPrinciple.BALANCE, DesignPrinciple.RHYTHM, DesignPrinciple.MOVEMENT],
            "classical": [DesignPrinciple.PROPORTION, DesignPrinciple.SCALE, DesignPrinciple.RHYTHM],
            "traditional": [DesignPrinciple.BALANCE, DesignPrinciple.UNITY, DesignPrinciple.MOVEMENT]
        }
        
        principles = set()
        for style in style_preferences:
            if style in style_principles:
                principles.update(style_principles[style])
        
        # 기본 원칙 (스타일이 없을 경우)
        if not principles:
            principles.update([DesignPrinciple.PROPORTION, DesignPrinciple.BALANCE, DesignPrinciple.UNITY])
        
        return list(principles)
    
    def _calculate_concept_confidence(self, base_concept: Dict[str, Any], 
                                    proportional_system: Dict[str, float],
                                    spatial_organization: Dict[str, Any]) -> float:
        """설계 개념 신뢰도 계산"""
        confidence_factors = []
        
        # 기본 개념 완성도
        base_completeness = len([v for v in base_concept.values() if v]) / len(base_concept)
        confidence_factors.append(base_completeness * 0.3)
        
        # 비례 시스템 일관성
        proportion_consistency = 1.0 if proportional_system.get('system_type') else 0.5
        confidence_factors.append(proportion_consistency * 0.2)
        
        # 공간 구성 논리성
        spatial_logic = len([v for v in spatial_organization.values() if v]) / len(spatial_organization)
        confidence_factors.append(spatial_logic * 0.3)
        
        # 이론적 근거
        theoretical_basis = 0.8  # 기본 이론 적용
        confidence_factors.append(theoretical_basis * 0.2)
        
        return sum(confidence_factors)
    
    def _evaluate_theoretical_soundness(self, base_concept: Dict[str, Any]) -> float:
        """이론적 건전성 평가"""
        # 설계 이론의 일관성과 논리성 평가
        soundness_score = 0.8  # 기본 점수
        
        # 개념 간 일관성 확인
        if base_concept.get('form_concept') and base_concept.get('circulation'):
            soundness_score += 0.1
        
        if base_concept.get('zoning'):
            soundness_score += 0.1
        
        return min(1.0, soundness_score)
    
    def _calculate_innovation_score(self, base_concept: Dict[str, Any], 
                                  style_preferences: List[str]) -> float:
        """혁신성 점수 계산"""
        innovation_score = 0.5  # 기본 점수
        
        # 스타일 혼합도
        style_count = len(style_preferences)
        if style_count > 1:
            innovation_score += 0.2
        if style_count > 2:
            innovation_score += 0.1
        
        # 전통과 현대의 융합
        if "hanok" in style_preferences and "modern" in style_preferences:
            innovation_score += 0.2
        
        return min(1.0, innovation_score)
    
    async def _generate_design_guidelines(self, design_concept: DesignConcept) -> Dict[str, Any]:
        """설계 가이드라인 생성"""
        guidelines = {
            "spatial_guidelines": {
                "organization": design_concept.spatial_organization,
                "circulation": design_concept.circulation_pattern,
                "zoning": design_concept.zoning_strategy
            },
            "formal_guidelines": {
                "concept": design_concept.form_concept,
                "proportions": design_concept.proportional_system,
                "dimensions": design_concept.dimensional_guidelines
            },
            "material_guidelines": {
                "palette": design_concept.material_palette,
                "color_scheme": design_concept.color_scheme,
                "texture": design_concept.texture_strategy
            },
            "environmental_guidelines": {
                "strategy": design_concept.environmental_strategy,
                "energy": design_concept.energy_concept,
                "lighting": design_concept.lighting_strategy
            },
            "cultural_guidelines": {
                "references": design_concept.cultural_references,
                "adaptations": design_concept.regional_adaptations
            }
        }
        
        return guidelines
    
    async def _get_theoretical_references(self, style_preferences: List[str]) -> List[Dict[str, Any]]:
        """이론적 참고 문헌"""
        references = []
        
        reference_db = {
            "modern": [
                {"title": "Towards a New Architecture", "author": "Le Corbusier", "relevance": 0.9},
                {"title": "Space, Time and Architecture", "author": "Sigfried Giedion", "relevance": 0.8}
            ],
            "hanok": [
                {"title": "한국의 전통건축", "author": "신영훈", "relevance": 0.9},
                {"title": "한옥의 공간문법", "author": "박언곤", "relevance": 0.8}
            ],
            "minimalist": [
                {"title": "Less is More", "author": "Mies van der Rohe", "relevance": 0.9},
                {"title": "The Architecture of Minimalism", "author": "Bertoni", "relevance": 0.8}
            ]
        }
        
        for style in style_preferences[:3]:  # 상위 3개 스타일
            if style in reference_db:
                references.extend(reference_db[style])
        
        return references
    
    def _get_memory_usage(self) -> int:
        """메모리 사용량 조회"""
        import psutil
        process = psutil.Process()
        return process.memory_info().rss
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """에이전트 상태 조회"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "is_initialized": self.is_initialized,
            "is_available": self.is_available(),
            "current_load": self.get_current_load(),
            "capabilities": [cap.value for cap in self.capabilities],
            "cache_size": len(self.concept_cache),
            "memory_usage_mb": self._get_memory_usage() / 1024 / 1024,
            "models_loaded": {
                "tokenizer": self.tokenizer is not None,
                "model": self.model is not None,
                "sentence_transformer": self.sentence_transformer is not None,
                "korean_processor": self.korean_processor is not None
            },
            "knowledge_bases": {
                "theory_knowledge": self.theory_knowledge is not None,
                "pattern_library": self.pattern_library is not None
            }
        }


if __name__ == "__main__":
    # 테스트용 실행
    async def test_design_theorist():
        agent = DesignTheoristAgent()
        
        # 초기화
        success = await agent.initialize()
        print(f"초기화 성공: {success}")
        
        if success:
            # 상태 확인
            status = await agent.get_agent_status()
            print(f"에이전트 상태: {json.dumps(status, indent=2, ensure_ascii=False)}")
    
    asyncio.run(test_design_theorist())