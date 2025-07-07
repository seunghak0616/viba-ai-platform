"""
간단한 테스트용 AI 에이전트
=========================

외부 라이브러리 의존성 없이 기본 기능만 테스트하는 간단한 AI 에이전트

@version 1.0
@author VIBA AI Team
@date 2025.07.06
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional
import uuid

# 프로젝트 임포트 (절대 경로)
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from ai.base_agent import BaseVIBAAgent, AgentCapability

logger = logging.getLogger(__name__)


class SimpleTestAgent(BaseVIBAAgent):
    """테스트용 간단한 AI 에이전트"""
    
    def __init__(self):
        super().__init__(
            agent_id="simple_test_agent",
            name="Simple Test Agent",
            capabilities=[
                AgentCapability.NATURAL_LANGUAGE_UNDERSTANDING,
                AgentCapability.DESIGN_THEORY_APPLICATION
            ]
        )
        self.response_templates = {
            "design": {
                "concept": "모던 스타일 건물",
                "floors": 3,
                "style": "modern",
                "spaces": ["로비", "사무실", "회의실"]
            },
            "analysis": {
                "feasibility": "높음",
                "compliance": "적합",
                "recommendations": ["자연채광 개선", "에너지 효율 향상"]
            }
        }
    
    async def initialize(self) -> bool:
        """에이전트 초기화"""
        logger.info(f"SimpleTestAgent 초기화 시작")
        await asyncio.sleep(0.1)  # 초기화 시뮬레이션
        self.is_initialized = True
        logger.info(f"SimpleTestAgent 초기화 완료")
        return True
    
    async def execute_task(self, task) -> Dict[str, Any]:
        """작업 실행"""
        # 입력 데이터 파싱
        if isinstance(task, dict):
            user_input = task.get("user_input", "")
            task_type = task.get("task_type", "design")
        else:
            user_input = str(task)
            task_type = "design"
        
        logger.info(f"SimpleTestAgent 작업 실행: {user_input}")
        
        # 간단한 키워드 분석
        keywords = self._analyze_keywords(user_input)
        
        # 응답 생성
        if "설계" in user_input or "design" in task_type:
            result = self._generate_design_response(keywords)
        elif "분석" in user_input or "analysis" in task_type:
            result = self._generate_analysis_response(keywords)
        else:
            result = self._generate_default_response(keywords)
        
        # 실행 시뮬레이션 (약간의 지연)
        await asyncio.sleep(0.2)
        
        return {
            "success": True,
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "task_type": task_type,
            "input": user_input,
            "keywords": keywords,
            "result": result,
            "timestamp": time.time(),
            "execution_time": 0.2
        }
    
    def _analyze_keywords(self, text: str) -> List[str]:
        """간단한 키워드 추출"""
        keywords = []
        
        # 건물 타입
        building_types = ["카페", "사무실", "주택", "빌딩", "게스트하우스", "호텔"]
        for building_type in building_types:
            if building_type in text:
                keywords.append(f"건물타입_{building_type}")
        
        # 스타일
        styles = ["모던", "한옥", "클래식", "미니멀", "전통"]
        for style in styles:
            if style in text:
                keywords.append(f"스타일_{style}")
        
        # 위치
        locations = ["강남", "서울", "부산", "대구", "인천"]
        for location in locations:
            if location in text:
                keywords.append(f"위치_{location}")
        
        # 층수
        import re
        floor_match = re.search(r'(\d+)층', text)
        if floor_match:
            keywords.append(f"층수_{floor_match.group(1)}")
        
        return keywords
    
    def _generate_design_response(self, keywords: List[str]) -> Dict[str, Any]:
        """설계 응답 생성"""
        response = self.response_templates["design"].copy()
        
        # 키워드 기반 커스터마이징
        for keyword in keywords:
            if keyword.startswith("스타일_"):
                style = keyword.split("_")[1]
                response["style"] = style
                response["concept"] = f"{style} 스타일 건물"
            
            elif keyword.startswith("층수_"):
                floors = int(keyword.split("_")[1])
                response["floors"] = floors
            
            elif keyword.startswith("건물타입_"):
                building_type = keyword.split("_")[1]
                if building_type == "카페":
                    response["spaces"] = ["매장", "주방", "창고"]
                elif building_type == "사무실":
                    response["spaces"] = ["로비", "사무실", "회의실", "휴게실"]
                elif building_type == "주택":
                    response["spaces"] = ["거실", "침실", "주방", "화장실"]
        
        return response
    
    def _generate_analysis_response(self, keywords: List[str]) -> Dict[str, Any]:
        """분석 응답 생성"""
        response = self.response_templates["analysis"].copy()
        
        # 키워드 기반 분석 결과 조정
        if any("한옥" in k for k in keywords):
            response["recommendations"].append("전통 건축 요소 보존")
        
        if any("모던" in k for k in keywords):
            response["recommendations"].append("현대적 설비 도입")
        
        return response
    
    def _generate_default_response(self, keywords: List[str]) -> Dict[str, Any]:
        """기본 응답 생성"""
        return {
            "message": "요청을 처리했습니다",
            "keywords_found": len(keywords),
            "available_services": ["설계", "분석", "검토"]
        }


class SimpleNLPProcessor:
    """테스트용 간단한 NLP 프로세서"""
    
    def __init__(self):
        self.name = "SimpleNLPProcessor"
    
    def process_comprehensive_text(self, text: str):
        """간단한 텍스트 처리"""
        
        # Mock 결과 객체
        class MockResult:
            def __init__(self, processor, text):
                self.entities = processor._extract_entities(text)
                self.spatial_relations = processor._extract_relations(text)
                self.design_requirements = processor._extract_requirements(text)
                self.design_intents = processor._extract_intents(text)
        
        return MockResult(self, text)
    
    def _extract_entities(self, text: str):
        """간단한 엔티티 추출"""
        entities = []
        
        # Mock 엔티티 클래스
        class MockEntity:
            def __init__(self, text, entity_type):
                self.text = text
                self.entity_type = entity_type
        
        # 키워드 기반 엔티티 추출
        if "카페" in text:
            entities.append(MockEntity("카페", "building_type"))
        if "모던" in text:
            entities.append(MockEntity("모던", "style"))
        if "강남" in text:
            entities.append(MockEntity("강남", "location"))
        
        import re
        floor_match = re.search(r'(\d+)층', text)
        if floor_match:
            entities.append(MockEntity(floor_match.group(0), "floors"))
        
        return entities
    
    def _extract_relations(self, text: str):
        """간단한 공간 관계 추출"""
        relations = []
        
        class MockRelation:
            def __init__(self, relation_type):
                self.relation_type = relation_type
        
        if "연결" in text:
            relations.append(MockRelation("connection"))
        if "분리" in text:
            relations.append(MockRelation("separation"))
        
        return relations
    
    def _extract_requirements(self, text: str):
        """간단한 요구사항 추출"""
        requirements = []
        
        class MockRequirement:
            def __init__(self, requirement_type):
                self.requirement_type = requirement_type
        
        if "친환경" in text:
            requirements.append(MockRequirement("sustainability"))
        if "에너지" in text:
            requirements.append(MockRequirement("energy_efficiency"))
        
        return requirements
    
    def _extract_intents(self, text: str):
        """간단한 의도 추출"""
        intents = []
        
        class MockIntent:
            def __init__(self, intent_type):
                self.intent_type = intent_type
        
        if "설계" in text:
            intents.append(MockIntent("DESIGN"))
        if "편안" in text or "아늑" in text:
            intents.append(MockIntent("COMFORT"))
        
        return intents


# 간단한 오케스트레이터
class SimpleOrchestrator:
    """테스트용 간단한 오케스트레이터"""
    
    def __init__(self):
        self.agents = {
            "simple_test": SimpleTestAgent()
        }
        self.nlp_processor = SimpleNLPProcessor()
    
    async def initialize(self):
        """초기화"""
        for agent in self.agents.values():
            await agent.initialize()
    
    async def process_request(self, user_input: str) -> Dict[str, Any]:
        """요청 처리"""
        # NLP 분석
        nlp_result = self.nlp_processor.process_comprehensive_text(user_input)
        
        # 에이전트 실행
        agent = self.agents["simple_test"]
        task = {
            "user_input": user_input,
            "nlp_result": nlp_result,
            "task_type": "design"
        }
        
        result = await agent.process_task_async(task)
        
        return {
            "success": True,
            "user_input": user_input,
            "nlp_analysis": {
                "entities_count": len(nlp_result.entities),
                "relations_count": len(nlp_result.spatial_relations),
                "requirements_count": len(nlp_result.design_requirements),
                "intents_count": len(nlp_result.design_intents)
            },
            "agent_result": result,
            "workflow_id": str(uuid.uuid4()),
            "timestamp": time.time()
        }


# 전역 인스턴스
_simple_orchestrator = None

def get_simple_orchestrator():
    """간단한 오케스트레이터 인스턴스 반환"""
    global _simple_orchestrator
    if _simple_orchestrator is None:
        _simple_orchestrator = SimpleOrchestrator()
    return _simple_orchestrator


async def simple_process_user_request(user_input: str):
    """간단한 사용자 요청 처리"""
    orchestrator = get_simple_orchestrator()
    await orchestrator.initialize()
    return await orchestrator.process_request(user_input)


if __name__ == "__main__":
    # 테스트 실행
    async def test_simple_agent():
        print("=== Simple Agent Test ===")
        
        # 에이전트 테스트
        agent = SimpleTestAgent()
        await agent.initialize()
        
        test_input = "강남에 3층 모던 카페를 설계해줘"
        result = await agent.process_task_async(test_input)
        
        print(f"Input: {test_input}")
        print(f"Result: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # 오케스트레이터 테스트
        print("\n=== Simple Orchestrator Test ===")
        orch_result = await simple_process_user_request(test_input)
        print(f"Orchestrator Result: {json.dumps(orch_result, indent=2, ensure_ascii=False)}")
    
    asyncio.run(test_simple_agent())