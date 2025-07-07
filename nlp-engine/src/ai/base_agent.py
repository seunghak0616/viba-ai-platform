"""
VIBA AI 에이전트 기본 클래스
=========================

모든 VIBA AI 에이전트의 공통 인터페이스와 기본 기능을 제공하는 기본 클래스

@version 1.0
@author VIBA AI Team
@date 2025.07.06
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class AgentCapability(Enum):
    """에이전트 능력 정의"""
    NATURAL_LANGUAGE_UNDERSTANDING = "nlp_understanding"
    DESIGN_THEORY_APPLICATION = "design_theory"
    BIM_MODEL_GENERATION = "bim_generation"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    SPATIAL_PLANNING = "spatial_planning"
    CULTURAL_ADAPTATION = "cultural_adaptation"
    OPTIMIZATION = "optimization"
    QUALITY_ASSESSMENT = "quality_assessment"
    EXTERNAL_INTEGRATION = "external_integration"
    COLLABORATION = "collaboration"
    DESIGN_REVIEW = "design_review"


class AgentStatus(Enum):
    """에이전트 상태"""
    IDLE = "idle"
    INITIALIZING = "initializing"
    PROCESSING = "processing"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class TaskExecution:
    """작업 실행 정보"""
    task_id: str
    start_time: float
    end_time: Optional[float] = None
    status: str = "running"
    progress: float = 0.0
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class BaseVIBAAgent(ABC):
    """VIBA AI 에이전트 기본 클래스"""
    
    def __init__(self, agent_id: str, name: str, capabilities: List[AgentCapability], 
                 config: Optional[Dict[str, Any]] = None):
        """
        기본 에이전트 초기화
        
        Args:
            agent_id: 에이전트 고유 ID
            name: 에이전트 이름
            capabilities: 에이전트 능력 목록
            config: 설정 딕셔너리
        """
        self.agent_id = agent_id
        self.name = name
        self.capabilities = capabilities
        self.config = config or {}
        
        # 상태 관리
        self.status = AgentStatus.IDLE
        self.is_initialized = False
        self.last_activity = time.time()
        
        # 작업 관리
        self.active_tasks: Dict[str, TaskExecution] = {}
        self.completed_tasks: List[TaskExecution] = []
        self.max_concurrent_tasks = self.config.get('max_concurrent_tasks', 1)
        
        # 성능 메트릭
        self.performance_metrics = {
            'total_tasks': 0,
            'successful_tasks': 0,
            'failed_tasks': 0,
            'average_processing_time': 0.0,
            'total_processing_time': 0.0
        }
        
        logger.info(f"에이전트 {self.name} ({self.agent_id}) 생성 완료")
    
    @abstractmethod
    async def initialize(self) -> bool:
        """
        에이전트 초기화
        
        Returns:
            초기화 성공 여부
        """
        pass
    
    @abstractmethod
    async def execute_task(self, task) -> Dict[str, Any]:
        """
        작업 실행
        
        Args:
            task: 실행할 작업
            
        Returns:
            작업 실행 결과
        """
        pass
    
    async def process_task_async(self, task) -> Dict[str, Any]:
        """
        비동기 작업 처리 (공통 로직)
        
        Args:
            task: 처리할 작업
            
        Returns:
            작업 처리 결과
        """
        task_id = getattr(task, 'id', str(uuid.uuid4()))
        
        # 동시 작업 수 확인
        if len(self.active_tasks) >= self.max_concurrent_tasks:
            raise RuntimeError(f"최대 동시 작업 수({self.max_concurrent_tasks}) 초과")
        
        # 작업 실행 정보 생성
        task_execution = TaskExecution(
            task_id=task_id,
            start_time=time.time()
        )
        
        self.active_tasks[task_id] = task_execution
        self.status = AgentStatus.PROCESSING
        
        try:
            logger.info(f"작업 시작: {task_id} (에이전트: {self.agent_id})")
            
            # 실제 작업 실행
            result = await self.execute_task(task)
            
            # 성공 처리
            task_execution.end_time = time.time()
            task_execution.status = "completed"
            task_execution.result = result
            task_execution.progress = 1.0
            
            # 메트릭 업데이트
            self._update_performance_metrics(task_execution, success=True)
            
            logger.info(f"작업 완료: {task_id} ({task_execution.end_time - task_execution.start_time:.2f}초)")
            
            return result
            
        except Exception as e:
            # 실패 처리
            task_execution.end_time = time.time()
            task_execution.status = "failed"
            task_execution.error = str(e)
            
            # 메트릭 업데이트
            self._update_performance_metrics(task_execution, success=False)
            
            logger.error(f"작업 실패: {task_id} - {e}")
            raise
            
        finally:
            # 정리
            if task_id in self.active_tasks:
                completed_task = self.active_tasks.pop(task_id)
                self.completed_tasks.append(completed_task)
                
                # 최근 100개만 유지
                if len(self.completed_tasks) > 100:
                    self.completed_tasks = self.completed_tasks[-100:]
            
            # 상태 업데이트
            if not self.active_tasks:
                self.status = AgentStatus.IDLE
            
            self.last_activity = time.time()
    
    def _update_performance_metrics(self, task_execution: TaskExecution, success: bool):
        """성능 메트릭 업데이트"""
        self.performance_metrics['total_tasks'] += 1
        
        if success:
            self.performance_metrics['successful_tasks'] += 1
        else:
            self.performance_metrics['failed_tasks'] += 1
        
        if task_execution.end_time:
            processing_time = task_execution.end_time - task_execution.start_time
            self.performance_metrics['total_processing_time'] += processing_time
            
            # 평균 처리 시간 업데이트
            total_successful = self.performance_metrics['successful_tasks']
            if total_successful > 0:
                self.performance_metrics['average_processing_time'] = (
                    self.performance_metrics['total_processing_time'] / total_successful
                )
    
    def is_available(self) -> bool:
        """에이전트 사용 가능 여부"""
        return (
            self.is_initialized and
            self.status in [AgentStatus.IDLE, AgentStatus.PROCESSING] and
            len(self.active_tasks) < self.max_concurrent_tasks
        )
    
    def get_current_load(self) -> float:
        """현재 부하율 (0.0 - 1.0)"""
        if not self.is_initialized:
            return 1.0
        
        return len(self.active_tasks) / self.max_concurrent_tasks
    
    def has_capability(self, capability: AgentCapability) -> bool:
        """특정 능력 보유 여부"""
        return capability in self.capabilities
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """작업 상태 조회"""
        # 활성 작업 확인
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            return {
                "task_id": task_id,
                "status": task.status,
                "progress": task.progress,
                "start_time": task.start_time,
                "elapsed_time": time.time() - task.start_time,
                "agent_id": self.agent_id
            }
        
        # 완료된 작업 확인
        for task in self.completed_tasks:
            if task.task_id == task_id:
                return {
                    "task_id": task_id,
                    "status": task.status,
                    "progress": task.progress,
                    "start_time": task.start_time,
                    "end_time": task.end_time,
                    "processing_time": task.end_time - task.start_time if task.end_time else None,
                    "result": task.result,
                    "error": task.error,
                    "agent_id": self.agent_id
                }
        
        return None
    
    async def cancel_task(self, task_id: str) -> bool:
        """작업 취소"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.status = "cancelled"
            task.end_time = time.time()
            
            # 완료된 작업으로 이동
            completed_task = self.active_tasks.pop(task_id)
            self.completed_tasks.append(completed_task)
            
            logger.info(f"작업 취소: {task_id}")
            return True
        
        return False
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """성능 요약 정보"""
        metrics = self.performance_metrics.copy()
        
        # 성공률 계산
        total_tasks = metrics['total_tasks']
        if total_tasks > 0:
            metrics['success_rate'] = metrics['successful_tasks'] / total_tasks
            metrics['failure_rate'] = metrics['failed_tasks'] / total_tasks
        else:
            metrics['success_rate'] = 0.0
            metrics['failure_rate'] = 0.0
        
        # 현재 상태 정보 추가
        metrics.update({
            "status": self.status.value,
            "active_tasks_count": len(self.active_tasks),
            "current_load": self.get_current_load(),
            "is_available": self.is_available(),
            "last_activity": self.last_activity,
            "uptime": time.time() - self.last_activity if self.is_initialized else 0
        })
        
        return metrics
    
    async def health_check(self) -> Dict[str, Any]:
        """헬스 체크"""
        health_status = {
            "agent_id": self.agent_id,
            "name": self.name,
            "is_healthy": True,
            "status": self.status.value,
            "is_initialized": self.is_initialized,
            "is_available": self.is_available(),
            "current_load": self.get_current_load(),
            "capabilities": [cap.value for cap in self.capabilities],
            "performance": self.get_performance_summary(),
            "timestamp": time.time()
        }
        
        # 건강도 확인
        if not self.is_initialized:
            health_status["is_healthy"] = False
            health_status["health_issues"] = ["not_initialized"]
        elif self.status == AgentStatus.ERROR:
            health_status["is_healthy"] = False
            health_status["health_issues"] = ["error_state"]
        elif self.get_current_load() > 0.9:
            health_status["is_healthy"] = False
            health_status["health_issues"] = ["high_load"]
        
        return health_status
    
    async def shutdown(self):
        """에이전트 종료"""
        logger.info(f"에이전트 {self.name} 종료 시작...")
        
        # 활성 작업 취소
        for task_id in list(self.active_tasks.keys()):
            await self.cancel_task(task_id)
        
        # 상태 업데이트
        self.status = AgentStatus.MAINTENANCE
        self.is_initialized = False
        
        logger.info(f"에이전트 {self.name} 종료 완료")
    
    def __str__(self) -> str:
        return f"VIBAAgent({self.name}, {self.agent_id}, {self.status.value})"
    
    def __repr__(self) -> str:
        return (f"BaseVIBAAgent(agent_id='{self.agent_id}', name='{self.name}', "
                f"capabilities={[c.value for c in self.capabilities]}, "
                f"status='{self.status.value}')")


class AgentCollaboration:
    """에이전트 간 협업 관리"""
    
    def __init__(self):
        self.collaboration_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def start_collaboration(self, session_id: str, agents: List[BaseVIBAAgent], 
                                coordinator: Optional[BaseVIBAAgent] = None) -> Dict[str, Any]:
        """협업 세션 시작"""
        if session_id in self.collaboration_sessions:
            raise ValueError(f"협업 세션이 이미 존재합니다: {session_id}")
        
        session = {
            "session_id": session_id,
            "agents": {agent.agent_id: agent for agent in agents},
            "coordinator": coordinator,
            "start_time": time.time(),
            "status": "active",
            "messages": [],
            "shared_data": {}
        }
        
        self.collaboration_sessions[session_id] = session
        
        logger.info(f"협업 세션 시작: {session_id} (참여 에이전트: {len(agents)}개)")
        
        return {
            "session_id": session_id,
            "status": "started",
            "participant_count": len(agents)
        }
    
    async def send_message(self, session_id: str, from_agent_id: str, 
                          to_agent_id: str, message: Dict[str, Any]) -> bool:
        """에이전트 간 메시지 전송"""
        if session_id not in self.collaboration_sessions:
            return False
        
        session = self.collaboration_sessions[session_id]
        
        message_record = {
            "timestamp": time.time(),
            "from_agent": from_agent_id,
            "to_agent": to_agent_id,
            "message": message,
            "message_id": str(uuid.uuid4())
        }
        
        session["messages"].append(message_record)
        
        return True
    
    async def update_shared_data(self, session_id: str, key: str, value: Any) -> bool:
        """공유 데이터 업데이트"""
        if session_id not in self.collaboration_sessions:
            return False
        
        session = self.collaboration_sessions[session_id]
        session["shared_data"][key] = {
            "value": value,
            "timestamp": time.time()
        }
        
        return True
    
    async def end_collaboration(self, session_id: str) -> Dict[str, Any]:
        """협업 세션 종료"""
        if session_id not in self.collaboration_sessions:
            return {"status": "not_found"}
        
        session = self.collaboration_sessions[session_id]
        session["status"] = "completed"
        session["end_time"] = time.time()
        
        # 세션 요약 생성
        summary = {
            "session_id": session_id,
            "duration": session["end_time"] - session["start_time"],
            "message_count": len(session["messages"]),
            "participant_count": len(session["agents"]),
            "data_items": len(session["shared_data"])
        }
        
        logger.info(f"협업 세션 종료: {session_id} ({summary['duration']:.2f}초)")
        
        return summary


if __name__ == "__main__":
    # 기본 테스트
    class TestAgent(BaseVIBAAgent):
        async def initialize(self) -> bool:
            self.is_initialized = True
            return True
        
        async def execute_task(self, task) -> Dict[str, Any]:
            await asyncio.sleep(1)  # 작업 시뮬레이션
            return {"result": "test_completed", "task_id": getattr(task, 'id', 'unknown')}
    
    async def test_base_agent():
        agent = TestAgent(
            agent_id="test_agent_001",
            name="테스트 에이전트",
            capabilities=[AgentCapability.NATURAL_LANGUAGE_UNDERSTANDING]
        )
        
        # 초기화
        await agent.initialize()
        print(f"에이전트 초기화: {agent.is_initialized}")
        
        # 헬스 체크
        health = await agent.health_check()
        print(f"헬스 체크: {health['is_healthy']}")
        
        # 성능 요약
        performance = agent.get_performance_summary()
        print(f"성능 요약: {performance}")
    
    asyncio.run(test_base_agent())