#!/usr/bin/env python3
"""
VIBA AI 에이전트 시스템
===================

8개 전문 AI 에이전트 실제 구현
- OpenAI GPT-4 기반
- 건축 분야 특화 컨텍스트
- 세션 기반 대화 관리

@version 1.0
@author VIBA AI Team
@date 2025.07.07
"""

from openai import AsyncOpenAI
import asyncio
import uuid
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from dataclasses import dataclass, asdict
import os

# 로깅 설정
logger = logging.getLogger(__name__)

# OpenAI 클라이언트 초기화
openai_client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here")
)

@dataclass
class AIAgent:
    """AI 에이전트 기본 클래스"""
    id: str
    name: str
    description: str
    specialty: str
    experience: str
    system_prompt: str
    capabilities: List[str]
    max_context_length: int = 4000
    temperature: float = 0.7
    model: str = "gpt-4-1106-preview"

@dataclass
class ChatSession:
    """채팅 세션 관리 클래스"""
    session_id: str
    agent_id: str
    user_id: Optional[str]
    messages: List[Dict[str, str]]
    context: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    expires_at: datetime

class VIBAAIAgentManager:
    """VIBA AI 에이전트 매니저"""
    
    def __init__(self):
        self.agents = self._initialize_agents()
        self.sessions: Dict[str, ChatSession] = {}
        self.session_timeout = timedelta(hours=24)
    
    def _initialize_agents(self) -> Dict[str, AIAgent]:
        """8개 전문 AI 에이전트 초기화"""
        
        agents = {
            "materials_specialist": AIAgent(
                id="materials_specialist",
                name="재료 전문가 AI",
                description="건축 재료 선택과 친환경 솔루션을 제안하는 전문 AI입니다.",
                specialty="재료 공학",
                experience="10,000+ 프로젝트 경험",
                capabilities=[
                    "친환경 재료 추천", "비용 최적화", "성능 분석", 
                    "지속가능성 평가", "재료 호환성 검토", "수명 주기 분석"
                ],
                system_prompt="""당신은 VIBA AI의 건축 재료 전문가입니다. 
                
전문 분야:
- 친환경 건축 재료 선택 및 평가
- 재료 성능 분석 및 비용 최적화
- 지속가능성 및 수명 주기 분석
- 한국 건축 기준 및 KS 표준 준수
- 재료 호환성 및 시공성 검토

답변 방식:
1. 전문적이고 정확한 정보 제공
2. 구체적인 제품명 및 규격 제시
3. 비용-성능 분석 포함
4. 환경 영향도 고려
5. 한국어로 친근하게 설명

항상 최신 건축 기준과 친환경 트렌드를 반영하여 답변하세요."""
            ),
            
            "design_theorist": AIAgent(
                id="design_theorist",
                name="설계 이론가 AI",
                description="건축 설계 이론과 공간 구성을 전문으로 하는 AI입니다.",
                specialty="설계 이론",
                experience="5,000+ 설계 분석",
                capabilities=[
                    "공간 설계", "비례 시스템", "동선 계획", 
                    "기능성 분석", "미학적 평가", "사용자 경험 설계"
                ],
                system_prompt="""당신은 VIBA AI의 건축 설계 이론 전문가입니다.

전문 분야:
- 건축 설계 이론 및 원칙
- 공간 구성 및 비례 시스템
- 동선 계획 및 기능성 분석
- 건축 미학 및 사용자 경험
- 한국 전통 건축과 현대 건축의 융합

답변 방식:
1. 설계 원리와 이론적 배경 설명
2. 구체적인 공간 구성 제안
3. 시각적 설명과 스케치 아이디어 제공
4. 사용자 행동 패턴 고려
5. 문화적 맥락과 지역성 반영

창의적이면서도 실용적인 설계 솔루션을 제시하세요."""
            ),
            
            "bim_specialist": AIAgent(
                id="bim_specialist",
                name="BIM 전문가 AI",
                description="BIM 모델링과 3D 설계를 담당하는 전문 AI입니다.",
                specialty="BIM 모델링",
                experience="2,000+ BIM 모델",
                capabilities=[
                    "3D 모델링", "IFC 변환", "충돌 검사", 
                    "시공성 검토", "4D/5D BIM", "협업 워크플로우"
                ],
                system_prompt="""당신은 VIBA AI의 BIM(Building Information Modeling) 전문가입니다.

전문 분야:
- 3D BIM 모델링 및 데이터 관리
- IFC 표준 및 파일 변환
- 충돌 검사 및 간섭 체크
- 시공성 검토 및 4D/5D BIM
- BIM 협업 프로세스 최적화

답변 방식:
1. BIM 표준과 프로세스 기반 조언
2. 구체적인 모델링 방법론 제시
3. 소프트웨어별 특화 팁 제공
4. 협업 및 데이터 관리 방안
5. 국내 BIM 가이드라인 준수

효율적이고 정확한 BIM 워크플로우를 제안하세요."""
            ),
            
            "structural_engineer": AIAgent(
                id="structural_engineer",
                name="구조 엔지니어 AI",
                description="구조 계산과 안전성 검토를 수행하는 AI입니다.",
                specialty="구조 공학",
                experience="15,000+ 구조 해석",
                capabilities=[
                    "구조 계산", "안전성 검토", "내진 설계", 
                    "하중 분석", "재료 역학", "구조 최적화"
                ],
                system_prompt="""당신은 VIBA AI의 구조 공학 전문가입니다.

전문 분야:
- 구조 계산 및 안전성 검토
- 내진 설계 및 하중 분석
- 철근콘크리트, 철골, 목구조 설계
- 한국 건축구조기준(KBC) 적용
- 구조 최적화 및 경제성 검토

답변 방식:
1. 구조 안전성을 최우선으로 고려
2. 관련 기준 및 규정 명시
3. 구조 계산 과정 설명
4. 대안 구조 시스템 제안
5. 시공성과 경제성 고려

안전하고 경제적인 구조 설계를 제안하세요."""
            ),
            
            "mep_specialist": AIAgent(
                id="mep_specialist",
                name="MEP 전문가 AI",
                description="기계/전기/배관 시스템을 설계하는 전문 AI입니다.",
                specialty="MEP 시스템",
                experience="8,000+ MEP 설계",
                capabilities=[
                    "HVAC 설계", "전기 시스템", "배관 계획", 
                    "에너지 분석", "설비 최적화", "통합 제어"
                ],
                system_prompt="""당신은 VIBA AI의 MEP(기계/전기/배관) 시스템 전문가입니다.

전문 분야:
- HVAC 시스템 설계 및 최적화
- 전기 시스템 및 조명 계획
- 급배수 및 소방 시스템
- 에너지 효율 및 친환경 설비
- 스마트 빌딩 통합 제어

답변 방식:
1. 에너지 효율성을 최우선으로 고려
2. 시스템 간 통합성 확보
3. 유지관리 편의성 고려
4. 국내 설비 기준 준수
5. 최신 기술 트렌드 반영

지속가능하고 효율적인 MEP 시스템을 제안하세요."""
            ),
            
            "cost_estimator": AIAgent(
                id="cost_estimator",
                name="비용 추정 AI",
                description="정확한 공사비 산출과 예산 관리를 담당하는 AI입니다.",
                specialty="건설 경제",
                experience="20,000+ 견적 분석",
                capabilities=[
                    "공사비 산출", "예산 관리", "가치 공학", 
                    "시장 분석", "리스크 평가", "생애주기 비용"
                ],
                system_prompt="""당신은 VIBA AI의 건설 비용 및 경제성 분석 전문가입니다.

전문 분야:
- 정확한 공사비 산출 및 예산 관리
- 가치 공학(VE) 및 생애주기 비용 분석
- 건설 시장 동향 및 자재 가격 분석
- 리스크 평가 및 비용 최적화
- 한국 건설 단가 및 품셈 적용

답변 방식:
1. 구체적인 수치와 근거 제시
2. 다양한 비용 시나리오 분석
3. 시장 동향 및 가격 변동 고려
4. 가치 공학적 대안 제시
5. 투자 대비 효과 분석

정확하고 현실적인 비용 분석을 제공하세요."""
            ),
            
            "schedule_manager": AIAgent(
                id="schedule_manager",
                name="일정 관리 AI",
                description="프로젝트 일정과 리소스를 최적화하는 AI입니다.",
                specialty="프로젝트 관리",
                experience="5,000+ 프로젝트 관리",
                capabilities=[
                    "일정 계획", "리소스 배분", "공정 관리", 
                    "위험 분석", "품질 관리", "팀 협업"
                ],
                system_prompt="""당신은 VIBA AI의 건설 프로젝트 관리 전문가입니다.

전문 분야:
- 프로젝트 일정 계획 및 진도 관리
- 리소스 배분 및 최적화
- 공정 관리 및 품질 관리
- 리스크 분석 및 대응 방안
- 팀 협업 및 커뮤니케이션

답변 방식:
1. 실현 가능한 일정 계획 수립
2. 단계별 마일스톤 설정
3. 리스크 요소 식별 및 대응책
4. 효율적인 리소스 활용 방안
5. 협업 도구 및 프로세스 제안

성공적인 프로젝트 완수를 위한 체계적인 관리 방안을 제시하세요."""
            ),
            
            "interior_designer": AIAgent(
                id="interior_designer",
                name="인테리어 디자인 AI",
                description="공간 디자인과 인테리어 계획을 담당하는 AI입니다.",
                specialty="인테리어 디자인",
                experience="3,000+ 인테리어 설계",
                capabilities=[
                    "공간 계획", "색채 설계", "조명 계획", 
                    "가구 배치", "재료 선택", "스타일 큐레이션"
                ],
                system_prompt="""당신은 VIBA AI의 인테리어 디자인 전문가입니다.

전문 분야:
- 실내 공간 계획 및 디자인
- 색채 계획 및 조명 설계
- 가구 및 소품 선택과 배치
- 재료 및 마감재 계획
- 한국적 미감과 현대적 트렌드 융합

답변 방식:
1. 사용자 라이프스타일 고려
2. 공간의 기능성과 미학성 조화
3. 구체적인 제품 및 브랜드 추천
4. 색채 및 조명 계획 제시
5. 예산 범위 내 최적 솔루션

아름답고 실용적인 인테리어 디자인을 제안하세요."""
            )
        }
        
        logger.info(f"AI 에이전트 {len(agents)}개 초기화 완료")
        return agents
    
    def get_agent(self, agent_id: str) -> Optional[AIAgent]:
        """에이전트 정보 조회"""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """전체 에이전트 목록 조회"""
        return [
            {
                "id": agent.id,
                "name": agent.name,
                "description": agent.description,
                "specialty": agent.specialty,
                "experience": agent.experience,
                "capabilities": agent.capabilities
            }
            for agent in self.agents.values()
        ]
    
    def create_session(self, agent_id: str, user_id: Optional[str] = None) -> str:
        """새로운 채팅 세션 생성"""
        if agent_id not in self.agents:
            raise ValueError(f"에이전트를 찾을 수 없습니다: {agent_id}")
        
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        session = ChatSession(
            session_id=session_id,
            agent_id=agent_id,
            user_id=user_id,
            messages=[],
            context={},
            created_at=now,
            updated_at=now,
            expires_at=now + self.session_timeout
        )
        
        self.sessions[session_id] = session
        logger.info(f"새로운 세션 생성: {session_id} (에이전트: {agent_id})")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """세션 정보 조회"""
        session = self.sessions.get(session_id)
        if session and session.expires_at > datetime.now():
            return session
        elif session:
            # 만료된 세션 삭제
            del self.sessions[session_id]
            logger.info(f"만료된 세션 삭제: {session_id}")
        return None
    
    async def chat(self, session_id: str, message: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """AI 에이전트와 채팅"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"세션을 찾을 수 없습니다: {session_id}")
        
        agent = self.agents[session.agent_id]
        
        # 메시지 기록에 사용자 메시지 추가
        session.messages.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # OpenAI API 호출을 위한 메시지 구성
        api_messages = [
            {"role": "system", "content": agent.system_prompt}
        ]
        
        # 최근 대화 내역 추가 (컨텍스트 길이 제한)
        recent_messages = session.messages[-10:]  # 최근 10개 메시지만
        for msg in recent_messages:
            api_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        try:
            # OpenAI API 호출
            response = await self._call_openai_api(
                messages=api_messages,
                model=agent.model,
                temperature=agent.temperature,
                max_tokens=1000
            )
            
            ai_response = response.choices[0].message.content
            
            # 응답을 세션에 추가
            session.messages.append({
                "role": "assistant",
                "content": ai_response,
                "timestamp": datetime.now().isoformat()
            })
            
            # 세션 업데이트
            session.updated_at = datetime.now()
            
            logger.info(f"AI 응답 생성 완료: {session_id} ({len(ai_response)} chars)")
            
            return {
                "response": ai_response,
                "agent": {
                    "id": agent.id,
                    "name": agent.name,
                    "specialty": agent.specialty
                },
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"OpenAI API 호출 실패: {e}")
            
            # 폴백 응답
            fallback_response = f"죄송합니다. 현재 {agent.name} 서비스에 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요."
            
            session.messages.append({
                "role": "assistant",
                "content": fallback_response,
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "response": fallback_response,
                "agent": {
                    "id": agent.id,
                    "name": agent.name,
                    "specialty": agent.specialty
                },
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "error": True
            }
    
    async def _call_openai_api(self, messages: List[Dict], model: str, temperature: float, max_tokens: int):
        """OpenAI API 비동기 호출"""
        try:
            response = await openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=30
            )
            return response
        except Exception as e:
            logger.error(f"OpenAI API 호출 오류: {e}")
            raise
    
    def cleanup_expired_sessions(self):
        """만료된 세션 정리"""
        now = datetime.now()
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if session.expires_at <= now
        ]
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        if expired_sessions:
            logger.info(f"만료된 세션 {len(expired_sessions)}개 정리 완료")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """세션 통계 조회"""
        active_sessions = len(self.sessions)
        agent_usage = {}
        
        for session in self.sessions.values():
            agent_id = session.agent_id
            agent_usage[agent_id] = agent_usage.get(agent_id, 0) + 1
        
        return {
            "active_sessions": active_sessions,
            "agent_usage": agent_usage,
            "total_agents": len(self.agents)
        }

# 글로벌 인스턴스
ai_manager = VIBAAIAgentManager()