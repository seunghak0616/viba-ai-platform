"""
한국어 건축 전문 NLP 프로세서 확장 메서드
===========================================

KoreanArchitectureProcessor의 추가 메서드들을 정의

@version 1.0
@author VIBA AI Team  
@date 2025.07.06
"""

import re
import time
from typing import Dict, List, Any, Optional
from collections import Counter

from .korean_processor import (
    ArchitecturalEntity, SpatialRelation, DesignRequirement, 
    DesignIntent, ArchitecturalStyle
)


class KoreanArchitectureProcessorExtensions:
    """한국어 건축 프로세서 확장 메서드 모음"""
    
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
    
    def _update_processing_stats(self, result) -> None:
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