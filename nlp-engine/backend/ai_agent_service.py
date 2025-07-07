import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import openai
import uuid

logger = logging.getLogger(__name__)

class AgentType(str, Enum):
    """AI 에이전트 타입"""
    MATERIALS_SPECIALIST = "materials_specialist"
    DESIGN_THEORIST = "design_theorist"
    BIM_SPECIALIST = "bim_specialist"
    STRUCTURAL_ENGINEER = "structural_engineer"
    MEP_SPECIALIST = "mep_specialist"
    COST_ESTIMATOR = "cost_estimator"
    SCHEDULE_MANAGER = "schedule_manager"
    INTERIOR_DESIGNER = "interior_designer"

class AnalysisType(str, Enum):
    """분석 타입"""
    COMPREHENSIVE = "comprehensive"
    ARCHITECTURAL = "architectural"
    STRUCTURAL = "structural"
    MEP = "mep"
    MATERIALS = "materials"
    COST = "cost"
    SUSTAINABILITY = "sustainability"

class AIAgentService:
    """AI 에이전트 서비스"""
    
    def __init__(self, openai_api_key: str = None):
        self.agents = {}
        self.sessions = {}
        self.analysis_cache = {}
        
        # OpenAI 클라이언트 설정 (실제 API 키가 있을 경우)
        if openai_api_key:
            openai.api_key = openai_api_key
            self.use_real_ai = True
        else:
            self.use_real_ai = False
            logger.info("OpenAI API 키가 없어 모의 AI 응답을 사용합니다.")
            
        self._initialize_agents()
        
    def _initialize_agents(self):
        """AI 에이전트 초기화"""
        agent_configs = {
            AgentType.MATERIALS_SPECIALIST: {
                "name": "재료 전문가 AI",
                "description": "건축 재료 선택과 친환경 솔루션을 제안하는 전문 AI",
                "capabilities": ["친환경 재료 추천", "비용 최적화", "성능 분석", "지속가능성 평가"],
                "system_prompt": """당신은 건축 재료 전문가 AI입니다. 
                친환경적이고 비용 효율적인 건축 재료를 추천하고, 
                재료의 성능, 내구성, 지속가능성을 분석합니다.
                한국의 건축 환경과 기후를 고려한 전문적인 조언을 제공하세요.""",
                "specialty": "재료 공학",
                "status": "active"
            },
            AgentType.DESIGN_THEORIST: {
                "name": "설계 이론가 AI",
                "description": "건축 설계 이론과 공간 구성을 전문으로 하는 AI",
                "capabilities": ["공간 설계", "비례 시스템", "동선 계획", "기능성 분석"],
                "system_prompt": """당신은 건축 설계 이론 전문가 AI입니다.
                공간 구성, 동선 계획, 비례 시스템을 분석하고
                효율적이고 아름다운 건축 설계를 제안합니다.
                한국의 전통 건축과 현대 건축 이론을 결합한 솔루션을 제공하세요.""",
                "specialty": "설계 이론",
                "status": "active"
            },
            AgentType.BIM_SPECIALIST: {
                "name": "BIM 전문가 AI",
                "description": "BIM 모델링과 3D 설계를 담당하는 전문 AI",
                "capabilities": ["3D 모델링", "IFC 변환", "충돌 검사", "시공성 검토"],
                "system_prompt": """당신은 BIM(Building Information Modeling) 전문가 AI입니다.
                3D 모델링, IFC 표준, 시공성 검토를 수행하고
                디지털 건축 설계의 최적화 방안을 제시합니다.
                국제 BIM 표준과 한국의 BIM 가이드라인을 준수하는 솔루션을 제공하세요.""",
                "specialty": "BIM 모델링",
                "status": "active"
            },
            AgentType.STRUCTURAL_ENGINEER: {
                "name": "구조 엔지니어 AI",
                "description": "구조 계산과 안전성 검토를 수행하는 AI",
                "capabilities": ["구조 계산", "안전성 검토", "내진 설계", "하중 분석"],
                "system_prompt": """당신은 구조 공학 전문가 AI입니다.
                건물의 구조적 안전성을 분석하고, 내진 설계, 하중 계산을 수행합니다.
                한국 건축구조기준(KBC)과 국제 기준을 준수하는 
                안전하고 경제적인 구조 설계를 제안하세요.""",
                "specialty": "구조 공학",
                "status": "active"
            },
            AgentType.MEP_SPECIALIST: {
                "name": "MEP 전문가 AI",
                "description": "기계/전기/배관 시스템을 설계하는 전문 AI",
                "capabilities": ["HVAC 설계", "전기 시스템", "배관 계획", "에너지 분석"],
                "system_prompt": """당신은 MEP(기계/전기/배관) 전문가 AI입니다.
                HVAC 시스템, 전기 설비, 배관 시스템을 설계하고
                에너지 효율성을 최적화합니다.
                한국의 전력 시스템과 설비 기준에 맞는 솔루션을 제공하세요.""",
                "specialty": "MEP 시스템",
                "status": "active"
            },
            AgentType.COST_ESTIMATOR: {
                "name": "비용 추정 AI",
                "description": "정확한 공사비 산출과 예산 관리를 담당하는 AI",
                "capabilities": ["공사비 산출", "예산 관리", "가치 공학", "시장 분석"],
                "system_prompt": """당신은 건설 비용 추정 전문가 AI입니다.
                정확한 공사비를 산출하고 예산 최적화 방안을 제시합니다.
                한국의 건설 시장 동향과 자재 가격을 반영한
                현실적이고 정확한 비용 분석을 제공하세요.""",
                "specialty": "건설 경제",
                "status": "active"
            },
            AgentType.SCHEDULE_MANAGER: {
                "name": "일정 관리 AI",
                "description": "프로젝트 일정과 리소스를 최적화하는 AI",
                "capabilities": ["일정 계획", "리소스 배분", "공정 관리", "위험 분석"],
                "system_prompt": """당신은 건설 프로젝트 관리 전문가 AI입니다.
                효율적인 공정 계획과 리소스 배분을 수행하고
                프로젝트 위험 요소를 분석합니다.
                한국의 건설 환경과 법규를 고려한 현실적인 일정을 제안하세요.""",
                "specialty": "프로젝트 관리",
                "status": "active"
            },
            AgentType.INTERIOR_DESIGNER: {
                "name": "인테리어 디자인 AI",
                "description": "공간 디자인과 인테리어 계획을 담당하는 AI",
                "capabilities": ["공간 계획", "색채 설계", "조명 계획", "가구 배치"],
                "system_prompt": """당신은 인테리어 디자인 전문가 AI입니다.
                공간의 기능성과 미적 요소를 조화시키는 디자인을 제안하고
                사용자의 라이프스타일에 맞는 인테리어 솔루션을 제공합니다.
                한국인의 주거 문화와 트렌드를 반영한 디자인을 제안하세요.""",
                "specialty": "인테리어 디자인",
                "status": "active"
            }
        }
        
        for agent_type, config in agent_configs.items():
            self.agents[agent_type] = config
            
    async def start_session(self, agent_id: AgentType, user_id: str, context: Dict = None) -> str:
        """AI 에이전트 세션 시작"""
        session_id = str(uuid.uuid4())
        
        self.sessions[session_id] = {
            "session_id": session_id,
            "agent_id": agent_id,
            "user_id": user_id,
            "context": context or {},
            "started_at": datetime.now(),
            "message_history": [],
            "status": "active"
        }
        
        logger.info(f"AI 세션 시작: {session_id} (에이전트: {agent_id}, 사용자: {user_id})")
        return session_id
        
    async def send_message(self, session_id: str, message: str) -> Dict[str, Any]:
        """AI 에이전트에게 메시지 전송"""
        if session_id not in self.sessions:
            raise ValueError(f"세션을 찾을 수 없습니다: {session_id}")
            
        session = self.sessions[session_id]
        agent_id = session["agent_id"]
        agent_config = self.agents[agent_id]
        
        # 메시지 히스토리에 사용자 메시지 추가
        user_message = {
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        }
        session["message_history"].append(user_message)
        
        start_time = time.time()
        
        try:
            # AI 응답 생성
            if self.use_real_ai:
                ai_response = await self._generate_openai_response(agent_config, session["message_history"])
            else:
                ai_response = await self._generate_mock_response(agent_id, message, session["context"])
                
            # 응답 시간 계산
            response_time = time.time() - start_time
            
            # AI 응답을 히스토리에 추가
            assistant_message = {
                "role": "assistant",
                "content": ai_response,
                "timestamp": datetime.now().isoformat(),
                "response_time": response_time
            }
            session["message_history"].append(assistant_message)
            
            # 응답 반환
            return {
                "session_id": session_id,
                "agent_id": agent_id,
                "agent_name": agent_config["name"],
                "response": ai_response,
                "response_time": response_time,
                "timestamp": datetime.now().isoformat(),
                "confidence": 0.95  # 실제 AI의 경우 모델에서 가져와야 함
            }
            
        except Exception as e:
            logger.error(f"AI 응답 생성 오류: {e}")
            error_response = f"죄송합니다. 현재 {agent_config['name']}가 응답할 수 없습니다. 잠시 후 다시 시도해주세요."
            
            return {
                "session_id": session_id,
                "agent_id": agent_id,
                "agent_name": agent_config["name"],
                "response": error_response,
                "response_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat(),
                "error": True
            }
            
    async def _generate_openai_response(self, agent_config: Dict, message_history: List[Dict]) -> str:
        """OpenAI API를 사용한 실제 AI 응답 생성"""
        try:
            # 시스템 프롬프트와 메시지 히스토리 구성
            messages = [{"role": "system", "content": agent_config["system_prompt"]}]
            
            # 최근 10개 메시지만 사용 (토큰 제한 고려)
            recent_messages = message_history[-10:]
            for msg in recent_messages:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
                
            # OpenAI API 호출
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",  # 또는 gpt-3.5-turbo
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API 오류: {e}")
            raise
            
    async def _generate_mock_response(self, agent_id: AgentType, message: str, context: Dict) -> str:
        """모의 AI 응답 생성"""
        # 각 에이전트별 전문적인 응답 템플릿
        response_templates = {
            AgentType.MATERIALS_SPECIALIST: [
                f"재료 전문가 AI가 '{message}' 요청을 분석했습니다.\n\n추천 재료:\n• 친환경 콘크리트 (탄소 저감 30%)\n• 재활용 강재 (비용 절감 15%)\n• 고성능 단열재 (에너지 효율 25% 향상)\n\n지속가능성 점수: 8.5/10\n예상 비용 절감: 12%",
                f"'{message}' 관련하여 최신 친환경 건축 재료를 분석했습니다.\n\n핵심 추천사항:\n1. 생분해성 바이오 콘크리트 적용\n2. 재활용 플라스틱 복합재 사용\n3. 자연 단열재 (셀룰로오스, 양모) 활용\n\n환경 영향도: 65% 감소\n내구성: 기존 대비 120%"
            ],
            AgentType.DESIGN_THEORIST: [
                f"설계 이론가 AI가 '{message}' 요청을 검토했습니다.\n\n설계 원칙 분석:\n• 황금비 적용으로 시각적 조화 달성\n• 자연 채광 최적화 (남향 30도 배치)\n• 효율적 동선 구성 (최대 이동거리 15m)\n\n공간 효율성: 92%\n사용자 만족도 예측: 9.2/10",
                f"'{message}'에 대한 공간 구성 분석을 완료했습니다.\n\n주요 설계 제안:\n1. 오픈 플랜과 프라이빗 공간의 균형\n2. 수직적 공간 활용 (메자닌 구조)\n3. 내외부 공간의 연속성 확보\n\n기능성 점수: 8.8/10\n미적 완성도: 9.1/10"
            ],
            AgentType.STRUCTURAL_ENGINEER: [
                f"구조 엔지니어 AI가 '{message}' 요청을 분석했습니다.\n\n구조 검토 결과:\n• 안전율: 3.2 (법정 기준 2.4 초과)\n• 내진 등급: 1등급 (규모 7.0 대응)\n• 하중 분산: 최적화 완료\n\n구조재 절약: 18%\n시공 기간 단축: 2주",
                f"'{message}' 관련 구조 안전성 분석을 수행했습니다.\n\n핵심 분석 결과:\n1. 기초 구조: 매트 기초 + 파일 보강 추천\n2. 골조 시스템: RC조 + 철골 하이브리드\n3. 내진 보강: 면진 장치 적용\n\n안전성 등급: A+\n경제성: 기존 대비 12% 절감"
            ],
            AgentType.COST_ESTIMATOR: [
                f"비용 추정 AI가 '{message}' 요청을 분석했습니다.\n\n상세 견적:\n• 총 공사비: 4억 8천만원 (VAT 별도)\n• 평당 단가: 480만원\n• 절감 가능액: 7,200만원 (15%)\n\n주요 절감 방안:\n- 재료 대체로 2,000만원\n- 공법 개선으로 3,500만원\n- 일정 단축으로 1,700만원",
                f"'{message}'에 대한 종합적인 비용 분석을 완료했습니다.\n\n비용 구성:\n1. 구조체: 40% (1억 9천만원)\n2. 마감공사: 35% (1억 6천만원)\n3. 설비공사: 25% (1억 2천만원)\n\n리스크 요인:\n- 자재비 상승 가능성: 5-8%\n- 공기 지연 리스크: 중간"
            ]
        }
        
        # 에이전트별 응답 선택 (랜덤)
        import random
        if agent_id in response_templates:
            template = random.choice(response_templates[agent_id])
        else:
            template = f"{self.agents[agent_id]['name']}가 '{message}' 요청을 처리했습니다.\n\n전문적인 분석과 최적화된 솔루션을 제공드립니다."
            
        # 응답 생성 지연 시뮬레이션
        await asyncio.sleep(random.uniform(1, 3))
        
        return template
        
    async def end_session(self, session_id: str) -> Dict[str, Any]:
        """AI 에이전트 세션 종료"""
        if session_id not in self.sessions:
            raise ValueError(f"세션을 찾을 수 없습니다: {session_id}")
            
        session = self.sessions[session_id]
        session["status"] = "ended"
        session["ended_at"] = datetime.now()
        
        # 세션 통계 계산
        message_count = len([msg for msg in session["message_history"] if msg["role"] == "user"])
        duration = (session["ended_at"] - session["started_at"]).total_seconds()
        
        session_summary = {
            "session_id": session_id,
            "agent_id": session["agent_id"],
            "user_id": session["user_id"],
            "message_count": message_count,
            "duration_seconds": duration,
            "ended_at": session["ended_at"].isoformat()
        }
        
        # 세션 정리 (메모리 절약)
        del self.sessions[session_id]
        
        logger.info(f"AI 세션 종료: {session_id} (메시지: {message_count}개, 기간: {duration:.1f}초)")
        return session_summary
        
    async def run_comprehensive_analysis(self, project_data: Dict) -> Dict[str, Any]:
        """종합 설계 분석 실행"""
        analysis_id = str(uuid.uuid4())
        
        logger.info(f"종합 분석 시작: {analysis_id}")
        
        # 각 에이전트별 분석 결과
        analysis_results = {}
        
        # 병렬로 각 에이전트 분석 실행
        tasks = []
        agent_types = [
            AgentType.MATERIALS_SPECIALIST,
            AgentType.DESIGN_THEORIST,
            AgentType.STRUCTURAL_ENGINEER,
            AgentType.COST_ESTIMATOR
        ]
        
        for agent_type in agent_types:
            task = self._run_agent_analysis(agent_type, project_data)
            tasks.append(task)
            
        # 모든 분석 완료 대기
        results = await asyncio.gather(*tasks)
        
        # 결과 정리
        for i, agent_type in enumerate(agent_types):
            analysis_results[agent_type] = results[i]
            
        # 종합 점수 계산
        overall_score = self._calculate_overall_score(analysis_results)
        
        comprehensive_result = {
            "analysis_id": analysis_id,
            "project_data": project_data,
            "agent_results": analysis_results,
            "overall_score": overall_score,
            "recommendations": self._generate_recommendations(analysis_results),
            "generated_at": datetime.now().isoformat(),
            "processing_time": sum(result.get("processing_time", 0) for result in results)
        }
        
        # 캐시에 저장
        self.analysis_cache[analysis_id] = comprehensive_result
        
        logger.info(f"종합 분석 완료: {analysis_id} (점수: {overall_score})")
        return comprehensive_result
        
    async def _run_agent_analysis(self, agent_type: AgentType, project_data: Dict) -> Dict[str, Any]:
        """개별 에이전트 분석 실행"""
        start_time = time.time()
        
        # 에이전트별 분석 요청 메시지 생성
        analysis_request = self._generate_analysis_request(agent_type, project_data)
        
        # 임시 세션 생성
        session_id = await self.start_session(agent_type, "system", project_data)
        
        try:
            # 분석 실행
            response = await self.send_message(session_id, analysis_request)
            
            # 에이전트별 특화된 결과 생성
            specialized_result = await self._process_agent_result(agent_type, response, project_data)
            
            processing_time = time.time() - start_time
            
            return {
                "agent_id": agent_type,
                "agent_name": self.agents[agent_type]["name"],
                "analysis_result": specialized_result,
                "raw_response": response["response"],
                "confidence": response.get("confidence", 0.9),
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat()
            }
            
        finally:
            # 임시 세션 정리
            try:
                await self.end_session(session_id)
            except:
                pass
                
    def _generate_analysis_request(self, agent_type: AgentType, project_data: Dict) -> str:
        """에이전트별 분석 요청 메시지 생성"""
        base_info = f"""
        프로젝트 정보:
        - 건물 유형: {project_data.get('building_type', 'N/A')}
        - 위치: {project_data.get('location', 'N/A')}
        - 면적: {project_data.get('area', 'N/A')}㎡
        - 층수: {project_data.get('floors', 'N/A')}층
        - 예산: {project_data.get('budget', 'N/A')}원
        - 특수 요구사항: {', '.join(project_data.get('special_requirements', []))}
        """
        
        agent_specific_requests = {
            AgentType.MATERIALS_SPECIALIST: f"{base_info}\n친환경적이고 비용 효율적인 건축 재료를 추천하고, 지속가능성 점수를 평가해주세요.",
            AgentType.DESIGN_THEORIST: f"{base_info}\n효율적인 공간 구성과 설계 원칙을 적용한 최적화 방안을 제시해주세요.",
            AgentType.STRUCTURAL_ENGINEER: f"{base_info}\n구조적 안전성을 검토하고 최적의 구조 시스템을 제안해주세요.",
            AgentType.COST_ESTIMATOR: f"{base_info}\n상세한 공사비를 산출하고 비용 절감 방안을 제시해주세요."
        }
        
        return agent_specific_requests.get(agent_type, f"{base_info}\n전문적인 분석과 권장사항을 제공해주세요.")
        
    async def _process_agent_result(self, agent_type: AgentType, response: Dict, project_data: Dict) -> Dict[str, Any]:
        """에이전트별 결과 처리 및 구조화"""
        # 기본 결과 구조
        result = {
            "summary": response["response"][:200] + "..." if len(response["response"]) > 200 else response["response"],
            "detailed_analysis": response["response"],
            "score": round(85 + (hash(response["response"]) % 15), 1),  # 85-100 점수
            "recommendations": []
        }
        
        # 에이전트별 특화 데이터 추가
        if agent_type == AgentType.MATERIALS_SPECIALIST:
            result.update({
                "sustainability_score": round(7.5 + (hash(project_data.get('location', '')) % 25) / 10, 1),
                "cost_efficiency": round(80 + (hash(project_data.get('building_type', '')) % 20), 1),
                "recommended_materials": [
                    {"name": "친환경 콘크리트", "savings": "15%", "sustainability": "높음"},
                    {"name": "재활용 강재", "savings": "12%", "sustainability": "중간"},
                    {"name": "자연 단열재", "savings": "8%", "sustainability": "매우 높음"}
                ]
            })
        elif agent_type == AgentType.COST_ESTIMATOR:
            budget = project_data.get('budget', 500000000)
            result.update({
                "total_cost": budget,
                "cost_per_sqm": round(budget / max(project_data.get('area', 100), 1)),
                "potential_savings": round(budget * 0.15),
                "cost_breakdown": {
                    "structure": round(budget * 0.4),
                    "finishing": round(budget * 0.35),
                    "mep": round(budget * 0.25)
                }
            })
        elif agent_type == AgentType.STRUCTURAL_ENGINEER:
            result.update({
                "safety_factor": 3.2,
                "seismic_rating": "1등급",
                "structural_efficiency": 94,
                "recommended_system": "RC조 + 철골 하이브리드"
            })
            
        return result
        
    def _calculate_overall_score(self, analysis_results: Dict) -> float:
        """종합 점수 계산"""
        scores = []
        weights = {
            AgentType.MATERIALS_SPECIALIST: 0.25,
            AgentType.DESIGN_THEORIST: 0.30,
            AgentType.STRUCTURAL_ENGINEER: 0.25,
            AgentType.COST_ESTIMATOR: 0.20
        }
        
        for agent_type, result in analysis_results.items():
            score = result["analysis_result"].get("score", 85)
            weight = weights.get(agent_type, 0.25)
            scores.append(score * weight)
            
        return round(sum(scores), 1)
        
    def _generate_recommendations(self, analysis_results: Dict) -> List[str]:
        """종합 권장사항 생성"""
        recommendations = [
            "친환경 재료 사용으로 지속가능성 향상",
            "구조 최적화를 통한 비용 절감",
            "효율적인 공간 배치로 활용도 극대화",
            "에너지 효율적인 설비 시스템 적용"
        ]
        return recommendations
        
    def get_agent_info(self, agent_id: AgentType) -> Dict[str, Any]:
        """에이전트 정보 반환"""
        if agent_id not in self.agents:
            raise ValueError(f"에이전트를 찾을 수 없습니다: {agent_id}")
            
        return self.agents[agent_id]
        
    def get_all_agents(self) -> Dict[str, Any]:
        """모든 에이전트 정보 반환"""
        return self.agents
        
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """세션 정보 반환"""
        if session_id not in self.sessions:
            raise ValueError(f"세션을 찾을 수 없습니다: {session_id}")
            
        return self.sessions[session_id]
        
    def get_analysis_result(self, analysis_id: str) -> Dict[str, Any]:
        """분석 결과 반환"""
        if analysis_id not in self.analysis_cache:
            raise ValueError(f"분석 결과를 찾을 수 없습니다: {analysis_id}")
            
        return self.analysis_cache[analysis_id]

# 전역 AI 에이전트 서비스 인스턴스
ai_service = AIAgentService()