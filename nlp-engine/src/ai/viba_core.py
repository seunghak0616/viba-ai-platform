"""
VIBA (Vibe Intelligent BIM Architect) Core Orchestrator
=======================================================

건축이론과 BIM 기술을 융합한 다중 AI 에이전트 시스템의 핵심 오케스트레이터

@version 2.0.0
@author VIBA AI Team
@date 2025.07.06
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
import json

from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.callbacks.base import BaseCallbackHandler

from .agents.design_theorist import DesignTheoristAgent
from .agents.bim_specialist import BIMSpecialistAgent  
from .agents.performance_analyst import PerformanceAnalystAgent
from .agents.design_reviewer import DesignReviewerAgent
from .agents.mcp_integration_hub import MCPIntegrationHub
from .communication.message_queue import MessageQueue
from .communication.workflow_manager import WorkflowManager
from .utils.metrics_collector import MetricsCollector
from .utils.quality_controller import QualityController

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """VIBA 에이전트 타입 정의"""
    DESIGN_THEORIST = "design_theorist"
    BIM_SPECIALIST = "bim_specialist"
    PERFORMANCE_ANALYST = "performance_analyst"
    DESIGN_REVIEWER = "design_reviewer"
    MCP_HUB = "mcp_integration_hub"


class TaskStatus(Enum):
    """작업 상태 정의"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class DesignTask:
    """설계 작업 정의"""
    id: str
    task_type: str
    description: str
    input_data: Dict[str, Any]
    required_agents: List[AgentType]
    priority: int = 1  # 1=최고, 5=최저
    status: TaskStatus = TaskStatus.PENDING
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    assigned_agent: Optional[AgentType] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    estimated_duration: Optional[float] = None


@dataclass
class AgentPerformanceMetrics:
    """에이전트 성능 메트릭"""
    agent_type: AgentType
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    average_completion_time: float = 0.0
    accuracy_score: float = 0.0
    last_active: float = field(default_factory=time.time)
    resource_usage: Dict[str, float] = field(default_factory=dict)


class VIBACoreOrchestrator:
    """
    VIBA AI 시스템의 핵심 오케스트레이터
    
    다중 에이전트 간의 협업, 작업 분배, 품질 관리를 담당
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        VIBA 코어 오케스트레이터 초기화
        
        Args:
            config: 설정 딕셔너리
        """
        self.config = config or {}
        self.is_initialized = False
        self.is_running = False
        
        # 에이전트 인스턴스
        self.agents: Dict[AgentType, Any] = {}
        
        # 작업 관리
        self.task_queue: List[DesignTask] = []
        self.active_tasks: Dict[str, DesignTask] = {}
        self.completed_tasks: Dict[str, DesignTask] = {}
        
        # 성능 및 품질 관리
        self.metrics_collector = MetricsCollector()
        self.quality_controller = QualityController()
        self.agent_metrics: Dict[AgentType, AgentPerformanceMetrics] = {}
        
        # 커뮤니케이션
        self.message_queue = MessageQueue()
        self.workflow_manager = WorkflowManager()
        
        # 실행 환경
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        logger.info("VIBA Core Orchestrator 초기화 완료")
    
    async def initialize(self) -> bool:
        """
        VIBA 시스템 초기화
        
        Returns:
            초기화 성공 여부
        """
        try:
            logger.info("VIBA AI 시스템 초기화 시작...")
            
            # 1. 에이전트 초기화
            await self._initialize_agents()
            
            # 2. 커뮤니케이션 시스템 초기화
            await self._initialize_communication()
            
            # 3. 품질 관리 시스템 초기화
            await self._initialize_quality_systems()
            
            # 4. 성능 메트릭 초기화
            self._initialize_metrics()
            
            self.is_initialized = True
            logger.info("✅ VIBA AI 시스템 초기화 완료")
            return True
            
        except Exception as e:
            logger.error(f"❌ VIBA 시스템 초기화 실패: {e}")
            return False
    
    async def _initialize_agents(self):
        """에이전트 초기화"""
        logger.info("🤖 AI 에이전트 초기화 중...")
        
        # Design Theorist Agent (건축 이론 전문가)
        self.agents[AgentType.DESIGN_THEORIST] = DesignTheoristAgent(
            config=self.config.get('design_theorist', {})
        )
        
        # BIM Specialist Agent (BIM 모델링 전문가)
        self.agents[AgentType.BIM_SPECIALIST] = BIMSpecialistAgent(
            config=self.config.get('bim_specialist', {})
        )
        
        # Performance Analyst Agent (성능 분석 전문가)
        self.agents[AgentType.PERFORMANCE_ANALYST] = PerformanceAnalystAgent(
            config=self.config.get('performance_analyst', {})
        )
        
        # Design Reviewer Agent (설계 검토 전문가)
        self.agents[AgentType.DESIGN_REVIEWER] = DesignReviewerAgent(
            config=self.config.get('design_reviewer', {})
        )
        
        # MCP Integration Hub (외부 도구 연동)
        self.agents[AgentType.MCP_HUB] = MCPIntegrationHub(
            config=self.config.get('mcp_hub', {})
        )
        
        # 모든 에이전트 초기화
        for agent_type, agent in self.agents.items():
            await agent.initialize()
            self.agent_metrics[agent_type] = AgentPerformanceMetrics(agent_type=agent_type)
            logger.info(f"✅ {agent_type.value} 에이전트 초기화 완료")
    
    async def _initialize_communication(self):
        """커뮤니케이션 시스템 초기화"""
        logger.info("📡 커뮤니케이션 시스템 초기화 중...")
        
        await self.message_queue.initialize()
        await self.workflow_manager.initialize()
        
        # 에이전트 간 메시지 라우팅 설정
        for agent_type, agent in self.agents.items():
            await self.message_queue.register_agent(agent_type, agent)
    
    async def _initialize_quality_systems(self):
        """품질 관리 시스템 초기화"""
        logger.info("🎯 품질 관리 시스템 초기화 중...")
        
        await self.quality_controller.initialize()
        
        # 품질 기준 설정
        quality_standards = {
            'design_accuracy_threshold': 0.9,
            'bim_compliance_threshold': 0.95,
            'performance_accuracy_threshold': 0.92,
            'overall_quality_threshold': 0.9
        }
        
        self.quality_controller.set_standards(quality_standards)
    
    def _initialize_metrics(self):
        """성능 메트릭 초기화"""
        logger.info("📊 성능 메트릭 시스템 초기화 중...")
        
        self.metrics_collector.register_metrics([
            'task_completion_rate',
            'average_response_time',
            'accuracy_scores',
            'resource_utilization',
            'agent_collaboration_efficiency'
        ])
    
    async def process_design_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        설계 요청 처리
        
        Args:
            request: 사용자 설계 요청
            
        Returns:
            처리 결과
        """
        if not self.is_initialized:
            raise RuntimeError("VIBA 시스템이 초기화되지 않았습니다")
        
        start_time = time.time()
        request_id = f"req_{int(start_time)}"
        
        logger.info(f"🎯 설계 요청 처리 시작: {request_id}")
        
        try:
            # 1. 요청 분석 및 작업 분해
            tasks = await self._decompose_design_request(request, request_id)
            
            # 2. 작업 스케줄링
            await self._schedule_tasks(tasks)
            
            # 3. 에이전트 실행 및 협업
            results = await self._execute_collaborative_workflow(tasks)
            
            # 4. 결과 통합 및 품질 검증
            final_result = await self._integrate_and_validate_results(results, request)
            
            # 5. 성능 메트릭 업데이트
            execution_time = time.time() - start_time
            await self._update_performance_metrics(request_id, execution_time, final_result)
            
            logger.info(f"✅ 설계 요청 처리 완료: {request_id} ({execution_time:.2f}초)")
            
            return {
                'request_id': request_id,
                'status': 'completed',
                'execution_time': execution_time,
                'result': final_result,
                'quality_score': final_result.get('quality_score', 0.0),
                'agent_contributions': final_result.get('agent_contributions', {})
            }
            
        except Exception as e:
            logger.error(f"❌ 설계 요청 처리 실패 {request_id}: {e}")
            return {
                'request_id': request_id,
                'status': 'failed',
                'error': str(e),
                'execution_time': time.time() - start_time
            }
    
    async def _decompose_design_request(self, request: Dict[str, Any], request_id: str) -> List[DesignTask]:
        """설계 요청을 세부 작업으로 분해"""
        logger.info(f"📋 설계 요청 분해 중: {request_id}")
        
        user_input = request.get('description', '')
        project_constraints = request.get('constraints', {})
        
        tasks = []
        
        # 1. 자연어 요구사항 분석 작업
        tasks.append(DesignTask(
            id=f"{request_id}_nlp_analysis",
            task_type="nlp_analysis",
            description="사용자 요구사항 자연어 분석",
            input_data={
                'user_input': user_input,
                'context': request.get('context', {})
            },
            required_agents=[AgentType.DESIGN_THEORIST],
            priority=1
        ))
        
        # 2. 건축 이론 적용 작업
        tasks.append(DesignTask(
            id=f"{request_id}_theory_application",
            task_type="theory_application", 
            description="건축 설계 이론 적용",
            input_data={
                'building_type': request.get('building_type', ''),
                'style_preferences': request.get('style', []),
                'constraints': project_constraints
            },
            required_agents=[AgentType.DESIGN_THEORIST],
            priority=1,
            dependencies=[f"{request_id}_nlp_analysis"]
        ))
        
        # 3. BIM 모델 생성 작업
        tasks.append(DesignTask(
            id=f"{request_id}_bim_generation",
            task_type="bim_generation",
            description="BIM 모델 자동 생성",
            input_data={
                'design_guidelines': {},  # 이전 작업 결과로 채워짐
                'technical_requirements': project_constraints
            },
            required_agents=[AgentType.BIM_SPECIALIST],
            priority=2,
            dependencies=[f"{request_id}_theory_application"]
        ))
        
        # 4. 성능 분석 작업
        tasks.append(DesignTask(
            id=f"{request_id}_performance_analysis",
            task_type="performance_analysis",
            description="건물 성능 종합 분석",
            input_data={
                'bim_model': {},  # BIM 생성 결과로 채워짐
                'analysis_types': ['energy', 'daylight', 'structural', 'acoustic']
            },
            required_agents=[AgentType.PERFORMANCE_ANALYST],
            priority=3,
            dependencies=[f"{request_id}_bim_generation"]
        ))
        
        # 5. 설계 검토 및 최적화 작업
        tasks.append(DesignTask(
            id=f"{request_id}_design_review",
            task_type="design_review",
            description="종합 설계 검토 및 개선안 제시",
            input_data={
                'design_solution': {},  # 모든 이전 결과 통합
                'quality_criteria': self.quality_controller.get_standards()
            },
            required_agents=[AgentType.DESIGN_REVIEWER],
            priority=4,
            dependencies=[f"{request_id}_performance_analysis"]
        ))
        
        return tasks
    
    async def _schedule_tasks(self, tasks: List[DesignTask]):
        """작업 스케줄링"""
        logger.info(f"⏰ {len(tasks)}개 작업 스케줄링 중...")
        
        # 의존성에 따른 우선순위 정렬
        sorted_tasks = self.workflow_manager.sort_by_dependencies(tasks)
        
        for task in sorted_tasks:
            self.task_queue.append(task)
            logger.debug(f"작업 큐에 추가: {task.id}")
    
    async def _execute_collaborative_workflow(self, tasks: List[DesignTask]) -> Dict[str, Any]:
        """에이전트 협업 워크플로우 실행"""
        logger.info("🤝 다중 에이전트 협업 워크플로우 실행 중...")
        
        results = {}
        
        while self.task_queue:
            # 실행 가능한 작업 찾기
            ready_tasks = [
                task for task in self.task_queue 
                if all(dep_id in results for dep_id in task.dependencies)
            ]
            
            if not ready_tasks:
                logger.warning("실행 가능한 작업이 없습니다. 의존성 순환 확인 필요")
                break
            
            # 병렬 실행을 위한 작업 그룹화
            parallel_tasks = self._group_parallel_tasks(ready_tasks)
            
            # 병렬 실행
            batch_results = await self._execute_task_batch(parallel_tasks)
            
            # 결과 통합
            results.update(batch_results)
            
            # 완료된 작업 제거
            for task in ready_tasks:
                if task.id in batch_results:
                    self.task_queue.remove(task)
                    self.completed_tasks[task.id] = task
        
        return results
    
    def _group_parallel_tasks(self, tasks: List[DesignTask]) -> List[List[DesignTask]]:
        """병렬 실행 가능한 작업 그룹화"""
        # 우선순위별로 그룹화
        priority_groups = {}
        for task in tasks:
            if task.priority not in priority_groups:
                priority_groups[task.priority] = []
            priority_groups[task.priority].append(task)
        
        # 우선순위 순으로 정렬된 그룹 반환
        return [priority_groups[p] for p in sorted(priority_groups.keys())]
    
    async def _execute_task_batch(self, task_groups: List[List[DesignTask]]) -> Dict[str, Any]:
        """작업 배치 실행"""
        results = {}
        
        for task_group in task_groups:
            # 같은 우선순위 작업들을 병렬 실행
            group_tasks = []
            for task in task_group:
                task.status = TaskStatus.IN_PROGRESS
                task.updated_at = time.time()
                self.active_tasks[task.id] = task
                
                group_tasks.append(self._execute_single_task(task))
            
            # 병렬 실행 및 결과 수집
            if group_tasks:
                task_results = await asyncio.gather(*group_tasks, return_exceptions=True)
                
                for i, result in enumerate(task_results):
                    task = task_group[i]
                    if isinstance(result, Exception):
                        logger.error(f"작업 실행 실패 {task.id}: {result}")
                        task.status = TaskStatus.FAILED
                        task.error_message = str(result)
                    else:
                        task.status = TaskStatus.COMPLETED
                        task.result = result
                        results[task.id] = result
                    
                    task.updated_at = time.time()
                    if task.id in self.active_tasks:
                        del self.active_tasks[task.id]
        
        return results
    
    async def _execute_single_task(self, task: DesignTask) -> Dict[str, Any]:
        """단일 작업 실행"""
        logger.info(f"🔄 작업 실행 중: {task.id}")
        
        start_time = time.time()
        
        try:
            # 적절한 에이전트 선택
            agent = self._select_agent_for_task(task)
            
            if not agent:
                raise ValueError(f"작업 {task.task_type}에 적합한 에이전트를 찾을 수 없습니다")
            
            # 에이전트에 작업 할당
            result = await agent.execute_task(task)
            
            # 품질 검증
            quality_score = await self.quality_controller.validate_result(task, result)
            result['quality_score'] = quality_score
            
            execution_time = time.time() - start_time
            result['execution_time'] = execution_time
            
            # 성능 메트릭 업데이트
            await self._update_agent_metrics(task.required_agents[0], execution_time, quality_score)
            
            logger.info(f"✅ 작업 완료: {task.id} ({execution_time:.2f}초, 품질: {quality_score:.2f})")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 작업 실행 실패 {task.id}: {e}")
            raise
    
    def _select_agent_for_task(self, task: DesignTask):
        """작업에 적합한 에이전트 선택"""
        if not task.required_agents:
            return None
        
        # 첫 번째 필요 에이전트 선택 (향후 로드 밸런싱 고려)
        primary_agent_type = task.required_agents[0]
        return self.agents.get(primary_agent_type)
    
    async def _integrate_and_validate_results(self, results: Dict[str, Any], original_request: Dict[str, Any]) -> Dict[str, Any]:
        """결과 통합 및 최종 검증"""
        logger.info("🔗 결과 통합 및 최종 검증 중...")
        
        # 결과 통합
        integrated_result = await self.workflow_manager.integrate_results(results)
        
        # 최종 품질 검증
        overall_quality = await self.quality_controller.validate_final_result(integrated_result, original_request)
        
        integrated_result['overall_quality_score'] = overall_quality
        integrated_result['validation_timestamp'] = time.time()
        
        return integrated_result
    
    async def _update_performance_metrics(self, request_id: str, execution_time: float, result: Dict[str, Any]):
        """성능 메트릭 업데이트"""
        await self.metrics_collector.record_request_metrics({
            'request_id': request_id,
            'execution_time': execution_time,
            'quality_score': result.get('overall_quality_score', 0.0),
            'success': result.get('status') == 'completed'
        })
    
    async def _update_agent_metrics(self, agent_type: AgentType, execution_time: float, quality_score: float):
        """에이전트 성능 메트릭 업데이트"""
        if agent_type in self.agent_metrics:
            metrics = self.agent_metrics[agent_type]
            metrics.total_tasks += 1
            metrics.completed_tasks += 1
            
            # 평균 완료 시간 업데이트
            if metrics.average_completion_time == 0:
                metrics.average_completion_time = execution_time
            else:
                metrics.average_completion_time = (
                    metrics.average_completion_time * (metrics.completed_tasks - 1) + execution_time
                ) / metrics.completed_tasks
            
            # 정확도 점수 업데이트
            if metrics.accuracy_score == 0:
                metrics.accuracy_score = quality_score
            else:
                metrics.accuracy_score = (
                    metrics.accuracy_score * (metrics.completed_tasks - 1) + quality_score
                ) / metrics.completed_tasks
            
            metrics.last_active = time.time()
    
    async def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 조회"""
        return {
            'system_status': {
                'is_initialized': self.is_initialized,
                'is_running': self.is_running,
                'active_tasks_count': len(self.active_tasks),
                'completed_tasks_count': len(self.completed_tasks),
                'pending_tasks_count': len(self.task_queue)
            },
            'agent_status': {
                agent_type.value: {
                    'is_available': agent.is_available(),
                    'current_load': agent.get_current_load(),
                    'performance_metrics': self.agent_metrics.get(agent_type, {}).__dict__
                }
                for agent_type, agent in self.agents.items()
            },
            'performance_summary': await self.metrics_collector.get_summary(),
            'quality_metrics': await self.quality_controller.get_metrics()
        }
    
    async def shutdown(self):
        """시스템 종료"""
        logger.info("🔄 VIBA AI 시스템 종료 중...")
        
        self.is_running = False
        
        # 진행 중인 작업 완료 대기
        if self.active_tasks:
            logger.info(f"{len(self.active_tasks)}개 진행 중인 작업 완료 대기...")
            max_wait_time = 30  # 30초 최대 대기
            wait_start = time.time()
            
            while self.active_tasks and (time.time() - wait_start) < max_wait_time:
                await asyncio.sleep(1)
        
        # 에이전트 종료
        for agent_type, agent in self.agents.items():
            await agent.shutdown()
            logger.info(f"🔴 {agent_type.value} 에이전트 종료 완료")
        
        # 실행자 종료
        self.executor.shutdown(wait=True)
        
        logger.info("✅ VIBA AI 시스템 종료 완료")


# 전역 VIBA 인스턴스 (싱글톤 패턴)
_viba_instance: Optional[VIBACoreOrchestrator] = None

async def get_viba_instance(config: Optional[Dict[str, Any]] = None) -> VIBACoreOrchestrator:
    """VIBA 인스턴스 획득 (싱글톤)"""
    global _viba_instance
    
    if _viba_instance is None:
        _viba_instance = VIBACoreOrchestrator(config)
        await _viba_instance.initialize()
    
    return _viba_instance


if __name__ == "__main__":
    # 개발/테스트용 실행
    async def main():
        viba = await get_viba_instance()
        
        # 테스트 요청
        test_request = {
            'description': '서울 강남구에 3층 현대식 단독주택을 설계해주세요',
            'building_type': '단독주택',
            'style': ['현대적', '미니멀'],
            'constraints': {
                'budget': 500000000,
                'lot_size': 200,
                'max_floors': 3
            }
        }
        
        result = await viba.process_design_request(test_request)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        await viba.shutdown()
    
    asyncio.run(main())