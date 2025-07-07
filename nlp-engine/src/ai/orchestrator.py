"""
VIBA 코어 오케스트레이터
======================

모든 AI 에이전트를 통합 관리하고 협력적 워크플로우를 조율하는 핵심 시스템
사용자 요청을 분석하여 적절한 에이전트들을 순차적/병렬적으로 실행

@version 1.0
@author VIBA AI Team
@date 2025.07.06
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid

# 프로젝트 임포트
from .base_agent import BaseVIBAAgent, AgentCapability
from .agents.design_theorist import DesignTheoristAgent
from .agents.bim_specialist import BIMSpecialistAgent
from .agents.performance_analyst import PerformanceAnalystAgent
from .agents.design_reviewer import DesignReviewerAgent
from .agents.mcp_integration_hub import MCPIntegrationHubAgent
from ..processors.korean_processor_final import KoreanArchitectureProcessor
from ..utils.metrics_collector import record_ai_inference_metric

logger = logging.getLogger(__name__)


class WorkflowType(Enum):
    """워크플로우 타입"""
    SIMPLE_DESIGN = "simple_design"       # 단순 설계: 이론가 → BIM 전문가
    FULL_DESIGN = "full_design"           # 완전 설계: 이론가 → BIM → 성능 → 검토
    PERFORMANCE_ONLY = "performance_only"  # 성능 분석만
    REVIEW_ONLY = "review_only"           # 검토만
    INTEGRATION_ONLY = "integration_only"  # 외부 연동만
    CUSTOM = "custom"                     # 사용자 정의


class ExecutionMode(Enum):
    """실행 모드"""
    SEQUENTIAL = "sequential"   # 순차 실행
    PARALLEL = "parallel"      # 병렬 실행
    HYBRID = "hybrid"         # 하이브리드 (일부 순차, 일부 병렬)


@dataclass
class WorkflowStep:
    """워크플로우 단계"""
    step_id: str
    agent_type: str
    agent_name: str
    dependencies: List[str] = field(default_factory=list)  # 의존하는 단계들
    input_mapping: Dict[str, str] = field(default_factory=dict)  # 입력 매핑
    timeout: float = 30.0
    retry_count: int = 3
    is_optional: bool = False
    

@dataclass
class WorkflowConfig:
    """워크플로우 설정"""
    workflow_id: str
    workflow_type: WorkflowType
    execution_mode: ExecutionMode
    steps: List[WorkflowStep]
    global_timeout: float = 300.0  # 5분
    enable_caching: bool = True
    enable_monitoring: bool = True


@dataclass
class ExecutionResult:
    """실행 결과"""
    step_id: str
    agent_name: str
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


@dataclass
class OrchestratorResult:
    """오케스트레이터 최종 결과"""
    workflow_id: str
    success: bool
    step_results: List[ExecutionResult]
    final_result: Optional[Dict[str, Any]] = None
    total_execution_time: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)


class VIBAOrchestrator:
    """VIBA 코어 오케스트레이터"""
    
    def __init__(self):
        """오케스트레이터 초기화"""
        self.agents: Dict[str, BaseVIBAAgent] = {}
        self.nlp_processor = KoreanArchitectureProcessor()
        self.active_workflows: Dict[str, WorkflowConfig] = {}
        self.execution_history: List[OrchestratorResult] = []
        
        # 메트릭 수집
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_execution_time": 0.0,
            "agent_usage_count": {},
            "workflow_type_count": {}
        }
        
        # 에이전트 초기화
        self._initialize_agents()
        
        # 기본 워크플로우 설정
        self._setup_default_workflows()
        
        logger.info("VIBA 오케스트레이터 초기화 완료")
    
    def _initialize_agents(self):
        """모든 AI 에이전트 초기화"""
        try:
            self.agents = {
                "design_theorist": DesignTheoristAgent(),
                "bim_specialist": BIMSpecialistAgent(),
                "performance_analyst": PerformanceAnalystAgent(),
                "design_reviewer": DesignReviewerAgent(),
                "mcp_integration_hub": MCPIntegrationHubAgent()
            }
            logger.info(f"AI 에이전트 {len(self.agents)}개 초기화 완료")
            
        except Exception as e:
            logger.error(f"에이전트 초기화 실패: {e}")
            raise
    
    def _setup_default_workflows(self):
        """기본 워크플로우 설정"""
        
        # 1. 단순 설계 워크플로우
        simple_design = WorkflowConfig(
            workflow_id="simple_design",
            workflow_type=WorkflowType.SIMPLE_DESIGN,
            execution_mode=ExecutionMode.SEQUENTIAL,
            steps=[
                WorkflowStep(
                    step_id="analyze_requirements",
                    agent_type="design_theorist",
                    agent_name="설계 이론가",
                    timeout=15.0
                ),
                WorkflowStep(
                    step_id="generate_bim",
                    agent_type="bim_specialist", 
                    agent_name="BIM 전문가",
                    dependencies=["analyze_requirements"],
                    input_mapping={"design_concept": "analyze_requirements.result"},
                    timeout=30.0
                )
            ]
        )
        
        # 2. 완전 설계 워크플로우
        full_design = WorkflowConfig(
            workflow_id="full_design",
            workflow_type=WorkflowType.FULL_DESIGN,
            execution_mode=ExecutionMode.HYBRID,
            steps=[
                WorkflowStep(
                    step_id="analyze_requirements",
                    agent_type="design_theorist",
                    agent_name="설계 이론가",
                    timeout=15.0
                ),
                WorkflowStep(
                    step_id="generate_bim",
                    agent_type="bim_specialist",
                    agent_name="BIM 전문가", 
                    dependencies=["analyze_requirements"],
                    input_mapping={"design_concept": "analyze_requirements.result"},
                    timeout=30.0
                ),
                WorkflowStep(
                    step_id="analyze_performance",
                    agent_type="performance_analyst",
                    agent_name="성능 분석가",
                    dependencies=["generate_bim"],
                    input_mapping={"bim_model": "generate_bim.result"},
                    timeout=45.0
                ),
                WorkflowStep(
                    step_id="review_design",
                    agent_type="design_reviewer",
                    agent_name="설계 검토자",
                    dependencies=["generate_bim", "analyze_performance"],
                    input_mapping={
                        "design_data": "analyze_requirements.result",
                        "bim_model": "generate_bim.result",
                        "performance_data": "analyze_performance.result"
                    },
                    timeout=30.0
                )
            ]
        )
        
        # 3. 성능 분석 전용 워크플로우
        performance_only = WorkflowConfig(
            workflow_id="performance_only",
            workflow_type=WorkflowType.PERFORMANCE_ONLY,
            execution_mode=ExecutionMode.SEQUENTIAL,
            steps=[
                WorkflowStep(
                    step_id="analyze_performance",
                    agent_type="performance_analyst",
                    agent_name="성능 분석가",
                    timeout=45.0
                )
            ]
        )
        
        self.active_workflows = {
            "simple_design": simple_design,
            "full_design": full_design,
            "performance_only": performance_only
        }
        
        logger.info(f"기본 워크플로우 {len(self.active_workflows)}개 설정 완료")
    
    async def process_request(
        self, 
        user_input: str, 
        workflow_type: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> OrchestratorResult:
        """사용자 요청 처리"""
        
        start_time = time.time()
        workflow_id = str(uuid.uuid4())
        
        try:
            # 메트릭 수집 시작
            self.metrics["total_requests"] += 1
            
            logger.info(f"새로운 요청 처리 시작: {workflow_id}")
            
            # 1. 자연어 분석
            with record_ai_inference_metric("orchestrator", "nlp_analysis"):
                nlp_result = self.nlp_processor.process_comprehensive_text(user_input)
            
            # 2. 워크플로우 결정
            if workflow_type is None:
                workflow_type = self._determine_workflow(user_input, nlp_result)
            
            if workflow_type not in self.active_workflows:
                raise ValueError(f"지원하지 않는 워크플로우: {workflow_type}")
            
            workflow_config = self.active_workflows[workflow_type]
            
            # 워크플로우 타입 카운트
            if workflow_type not in self.metrics["workflow_type_count"]:
                self.metrics["workflow_type_count"][workflow_type] = 0
            self.metrics["workflow_type_count"][workflow_type] += 1
            
            logger.info(f"선택된 워크플로우: {workflow_type}")
            
            # 3. 초기 데이터 준비
            initial_data = {
                "user_input": user_input,
                "nlp_analysis": nlp_result,
                "additional_context": additional_context or {},
                "workflow_id": workflow_id,
                "timestamp": datetime.now().isoformat()
            }
            
            # 4. 워크플로우 실행
            execution_result = await self._execute_workflow(
                workflow_config, 
                initial_data
            )
            
            # 5. 최종 결과 구성
            final_result = self._compile_final_result(execution_result)
            
            # 6. 실행 시간 계산
            total_time = time.time() - start_time
            
            # 7. 결과 객체 생성
            orchestrator_result = OrchestratorResult(
                workflow_id=workflow_id,
                success=True,
                step_results=execution_result,
                final_result=final_result,
                total_execution_time=total_time
            )
            
            # 8. 메트릭 업데이트
            self.metrics["successful_requests"] += 1
            self._update_average_execution_time(total_time)
            
            # 9. 실행 이력 저장
            self.execution_history.append(orchestrator_result)
            
            logger.info(f"요청 처리 완료: {workflow_id} ({total_time:.2f}초)")
            
            return orchestrator_result
            
        except Exception as e:
            # 실패 처리
            total_time = time.time() - start_time
            self.metrics["failed_requests"] += 1
            
            error_result = OrchestratorResult(
                workflow_id=workflow_id,
                success=False,
                step_results=[],
                final_result={"error": str(e)},
                total_execution_time=total_time
            )
            
            self.execution_history.append(error_result)
            logger.error(f"요청 처리 실패: {workflow_id} - {e}")
            
            return error_result
    
    def _determine_workflow(self, user_input: str, nlp_result) -> str:
        """사용자 입력을 기반으로 적절한 워크플로우 결정"""
        
        # 키워드 기반 분석
        input_lower = user_input.lower()
        
        # 성능 분석 전용 요청
        performance_keywords = ["성능", "에너지", "구조", "음향", "채광", "분석"]
        if any(keyword in input_lower for keyword in performance_keywords):
            if not any(keyword in input_lower for keyword in ["설계", "모델", "생성"]):
                return "performance_only"
        
        # 검토 전용 요청
        review_keywords = ["검토", "평가", "개선", "문제", "대안"]
        if any(keyword in input_lower for keyword in review_keywords):
            if not any(keyword in input_lower for keyword in ["설계", "모델", "생성"]):
                return "review_only"
        
        # 설계 요구사항이 복잡한 경우 완전 설계
        complex_indicators = [
            len(nlp_result.entities) > 5,  # 많은 엔티티
            len(nlp_result.spatial_relations) > 3,  # 복잡한 공간 관계  
            len(nlp_result.design_requirements) > 5,  # 많은 요구사항
            "친환경" in user_input,
            "인증" in user_input,
            "성능" in user_input and "설계" in user_input
        ]
        
        if sum(complex_indicators) >= 2:
            return "full_design"
        
        # 기본값: 단순 설계
        return "simple_design"
    
    async def _execute_workflow(
        self, 
        workflow_config: WorkflowConfig, 
        initial_data: Dict[str, Any]
    ) -> List[ExecutionResult]:
        """워크플로우 실행"""
        
        results: List[ExecutionResult] = []
        step_outputs: Dict[str, Any] = {"initial": initial_data}
        
        try:
            if workflow_config.execution_mode == ExecutionMode.SEQUENTIAL:
                # 순차 실행
                for step in workflow_config.steps:
                    result = await self._execute_step(step, step_outputs)
                    results.append(result)
                    
                    if result.success and result.result:
                        step_outputs[step.step_id] = result.result
                    elif not step.is_optional:
                        # 필수 단계가 실패하면 중단
                        break
                        
            elif workflow_config.execution_mode == ExecutionMode.PARALLEL:
                # 병렬 실행 (의존성 무시)
                tasks = []
                for step in workflow_config.steps:
                    task = self._execute_step(step, step_outputs)
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # 예외 처리
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        results[i] = ExecutionResult(
                            step_id=workflow_config.steps[i].step_id,
                            agent_name=workflow_config.steps[i].agent_name,
                            success=False,
                            error=str(result)
                        )
                        
            elif workflow_config.execution_mode == ExecutionMode.HYBRID:
                # 하이브리드 실행 (의존성 고려)
                results = await self._execute_hybrid_workflow(workflow_config, step_outputs)
            
            return results
            
        except Exception as e:
            logger.error(f"워크플로우 실행 실패: {e}")
            raise
    
    async def _execute_hybrid_workflow(
        self, 
        workflow_config: WorkflowConfig, 
        step_outputs: Dict[str, Any]
    ) -> List[ExecutionResult]:
        """하이브리드 워크플로우 실행 (의존성 기반 최적화)"""
        
        results: List[ExecutionResult] = []
        completed_steps: set = {"initial"}
        remaining_steps = workflow_config.steps.copy()
        
        while remaining_steps:
            # 실행 가능한 단계들 찾기
            ready_steps = []
            for step in remaining_steps:
                if all(dep in completed_steps for dep in step.dependencies):
                    ready_steps.append(step)
            
            if not ready_steps:
                # 데드락 상황
                remaining_step_names = [s.step_id for s in remaining_steps]
                raise RuntimeError(f"워크플로우 데드락: {remaining_step_names}")
            
            # 준비된 단계들을 병렬 실행
            tasks = []
            for step in ready_steps:
                task = self._execute_step(step, step_outputs)
                tasks.append(task)
            
            step_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 결과 처리
            for i, result in enumerate(step_results):
                step = ready_steps[i]
                
                if isinstance(result, Exception):
                    result = ExecutionResult(
                        step_id=step.step_id,
                        agent_name=step.agent_name,
                        success=False,
                        error=str(result)
                    )
                
                results.append(result)
                
                if result.success and result.result:
                    step_outputs[step.step_id] = result.result
                    completed_steps.add(step.step_id)
                elif not step.is_optional:
                    # 필수 단계 실패시 중단
                    logger.warning(f"필수 단계 실패: {step.step_id}")
                
                remaining_steps.remove(step)
        
        return results
    
    async def _execute_step(
        self, 
        step: WorkflowStep, 
        step_outputs: Dict[str, Any]
    ) -> ExecutionResult:
        """개별 단계 실행"""
        
        start_time = datetime.now()
        
        try:
            # 에이전트 선택
            if step.agent_type not in self.agents:
                raise ValueError(f"알 수 없는 에이전트: {step.agent_type}")
            
            agent = self.agents[step.agent_type]
            
            # 에이전트 사용 카운트
            if step.agent_type not in self.metrics["agent_usage_count"]:
                self.metrics["agent_usage_count"][step.agent_type] = 0
            self.metrics["agent_usage_count"][step.agent_type] += 1
            
            # 입력 데이터 구성
            input_data = self._prepare_step_input(step, step_outputs)
            
            # 에이전트 실행
            logger.info(f"단계 실행 시작: {step.step_id} ({step.agent_name})")
            
            with record_ai_inference_metric("orchestrator", f"step_{step.step_id}"):
                result = await asyncio.wait_for(
                    agent.process_task_async(input_data),
                    timeout=step.timeout
                )
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            logger.info(f"단계 실행 완료: {step.step_id} ({execution_time:.2f}초)")
            
            return ExecutionResult(
                step_id=step.step_id,
                agent_name=step.agent_name,
                success=True,
                result=result,
                execution_time=execution_time,
                start_time=start_time,
                end_time=end_time
            )
            
        except asyncio.TimeoutError:
            error_msg = f"단계 타임아웃: {step.step_id} ({step.timeout}초)"
            logger.error(error_msg)
            
            return ExecutionResult(
                step_id=step.step_id,
                agent_name=step.agent_name,
                success=False,
                error=error_msg,
                start_time=start_time,
                end_time=datetime.now()
            )
            
        except Exception as e:
            error_msg = f"단계 실행 오류: {step.step_id} - {e}"
            logger.error(error_msg)
            
            return ExecutionResult(
                step_id=step.step_id,
                agent_name=step.agent_name,
                success=False,
                error=error_msg,
                start_time=start_time,
                end_time=datetime.now()
            )
    
    def _prepare_step_input(
        self, 
        step: WorkflowStep, 
        step_outputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """단계별 입력 데이터 준비"""
        
        input_data = {}
        
        # 기본 입력 (초기 데이터)
        if "initial" in step_outputs:
            input_data.update(step_outputs["initial"])
        
        # 입력 매핑 적용
        for target_key, source_path in step.input_mapping.items():
            try:
                # 경로 파싱 (예: "analyze_requirements.result.design_concept")
                path_parts = source_path.split(".")
                current_data = step_outputs
                
                for part in path_parts:
                    current_data = current_data[part]
                
                input_data[target_key] = current_data
                
            except (KeyError, TypeError) as e:
                logger.warning(f"입력 매핑 실패: {target_key} <- {source_path}: {e}")
        
        return input_data
    
    def _compile_final_result(self, step_results: List[ExecutionResult]) -> Dict[str, Any]:
        """최종 결과 컴파일"""
        
        final_result = {
            "workflow_summary": {
                "total_steps": len(step_results),
                "successful_steps": sum(1 for r in step_results if r.success),
                "failed_steps": sum(1 for r in step_results if not r.success),
                "total_execution_time": sum(r.execution_time for r in step_results)
            },
            "step_results": {},
            "errors": [],
            "final_outputs": {}
        }
        
        # 각 단계 결과 정리
        for result in step_results:
            final_result["step_results"][result.step_id] = {
                "agent_name": result.agent_name,
                "success": result.success,
                "execution_time": result.execution_time,
                "result": result.result if result.success else None
            }
            
            if not result.success:
                final_result["errors"].append({
                    "step_id": result.step_id,
                    "agent_name": result.agent_name,
                    "error": result.error
                })
            
            # 주요 출력물 추출
            if result.success and result.result:
                if result.step_id == "generate_bim" and "bim_model" in result.result:
                    final_result["final_outputs"]["bim_model"] = result.result["bim_model"]
                
                if result.step_id == "analyze_performance" and "analysis_results" in result.result:
                    final_result["final_outputs"]["performance_analysis"] = result.result["analysis_results"]
                
                if result.step_id == "review_design" and "review_summary" in result.result:
                    final_result["final_outputs"]["design_review"] = result.result["review_summary"]
        
        return final_result
    
    def _update_average_execution_time(self, execution_time: float):
        """평균 실행 시간 업데이트"""
        current_avg = self.metrics["average_execution_time"]
        total_requests = self.metrics["total_requests"]
        
        # 누적 평균 계산
        new_avg = ((current_avg * (total_requests - 1)) + execution_time) / total_requests
        self.metrics["average_execution_time"] = new_avg
    
    async def get_agent_health_status(self) -> Dict[str, Any]:
        """모든 에이전트의 상태 확인"""
        
        health_status = {
            "orchestrator": {
                "status": "healthy",
                "total_requests": self.metrics["total_requests"],
                "success_rate": 0.0,
                "average_execution_time": self.metrics["average_execution_time"]
            },
            "agents": {}
        }
        
        # 성공률 계산
        if self.metrics["total_requests"] > 0:
            success_rate = self.metrics["successful_requests"] / self.metrics["total_requests"]
            health_status["orchestrator"]["success_rate"] = success_rate
        
        # 각 에이전트 상태 확인
        for agent_name, agent in self.agents.items():
            try:
                agent_health = await agent.health_check()
                health_status["agents"][agent_name] = agent_health
            except Exception as e:
                health_status["agents"][agent_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return health_status
    
    def get_execution_metrics(self) -> Dict[str, Any]:
        """실행 메트릭 조회"""
        return {
            "metrics": self.metrics.copy(),
            "recent_executions": [
                {
                    "workflow_id": result.workflow_id,
                    "success": result.success,
                    "execution_time": result.total_execution_time,
                    "created_at": result.created_at.isoformat()
                }
                for result in self.execution_history[-10:]  # 최근 10개
            ]
        }
    
    def register_custom_workflow(self, workflow_config: WorkflowConfig):
        """사용자 정의 워크플로우 등록"""
        self.active_workflows[workflow_config.workflow_id] = workflow_config
        logger.info(f"커스텀 워크플로우 등록: {workflow_config.workflow_id}")
    
    async def shutdown(self):
        """오케스트레이터 종료"""
        logger.info("VIBA 오케스트레이터 종료 중...")
        
        # 모든 에이전트 종료
        for agent_name, agent in self.agents.items():
            try:
                if hasattr(agent, 'shutdown'):
                    await agent.shutdown()
                logger.info(f"에이전트 종료 완료: {agent_name}")
            except Exception as e:
                logger.error(f"에이전트 종료 실패: {agent_name} - {e}")
        
        logger.info("VIBA 오케스트레이터 종료 완료")


# 전역 오케스트레이터 인스턴스
_orchestrator_instance: Optional[VIBAOrchestrator] = None


def get_orchestrator() -> VIBAOrchestrator:
    """전역 오케스트레이터 인스턴스 반환 (싱글톤 패턴)"""
    global _orchestrator_instance
    
    if _orchestrator_instance is None:
        _orchestrator_instance = VIBAOrchestrator()
    
    return _orchestrator_instance


async def process_user_request(
    user_input: str,
    workflow_type: Optional[str] = None,
    additional_context: Optional[Dict[str, Any]] = None
) -> OrchestratorResult:
    """편의 함수: 사용자 요청 처리"""
    orchestrator = get_orchestrator()
    return await orchestrator.process_request(user_input, workflow_type, additional_context)