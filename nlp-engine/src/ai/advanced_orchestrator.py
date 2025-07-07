"""
고급 오케스트레이터 시스템
=========================

AI 에이전트들의 고도화된 협력과 최적화를 위한 고급 오케스트레이터

@version 2.0
@author VIBA AI Team
@date 2025.07.06
"""

import asyncio
import json
import logging
import time
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import heapq

# 프로젝트 임포트
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from .base_agent import BaseVIBAAgent, AgentCapability
    from ..utils.metrics_collector import record_ai_inference_metric
except ImportError:
    # 직접 실행 시 절대 경로로 임포트
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ai.base_agent import BaseVIBAAgent, AgentCapability
    
    # 메트릭 수집기가 없으면 더미 함수 사용
    def record_ai_inference_metric(*args, **kwargs):
        pass

logger = logging.getLogger(__name__)


class OrchestrationStrategy(Enum):
    """오케스트레이션 전략"""
    SEQUENTIAL = "sequential"           # 순차 실행
    PARALLEL = "parallel"              # 병렬 실행
    PIPELINE = "pipeline"              # 파이프라인
    HYBRID = "hybrid"                  # 하이브리드
    ADAPTIVE = "adaptive"              # 적응형
    REINFORCEMENT = "reinforcement"    # 강화학습 기반


@dataclass
class AgentPerformanceMetrics:
    """에이전트 성능 메트릭"""
    agent_id: str
    execution_times: List[float] = field(default_factory=list)
    success_rates: List[float] = field(default_factory=list)
    resource_usage: List[float] = field(default_factory=list)
    quality_scores: List[float] = field(default_factory=list)
    collaboration_scores: Dict[str, float] = field(default_factory=dict)
    
    @property
    def avg_execution_time(self) -> float:
        return np.mean(self.execution_times) if self.execution_times else 0.0
    
    @property
    def avg_success_rate(self) -> float:
        return np.mean(self.success_rates) if self.success_rates else 0.0
    
    @property
    def efficiency_score(self) -> float:
        if self.avg_execution_time > 0:
            return self.avg_success_rate / self.avg_execution_time
        return 0.0


@dataclass
class WorkflowNode:
    """워크플로우 노드"""
    node_id: str
    agent_id: str
    dependencies: List[str] = field(default_factory=list)
    parallel_group: Optional[str] = None
    priority: int = 1
    timeout: float = 30.0
    retry_count: int = 3
    conditions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionPlan:
    """실행 계획"""
    plan_id: str
    nodes: List[WorkflowNode]
    estimated_time: float
    confidence_score: float
    resource_requirements: Dict[str, float]
    fallback_plans: List['ExecutionPlan'] = field(default_factory=list)


class IntelligentAgentSelector:
    """지능형 에이전트 선택기"""
    
    def __init__(self):
        self.agent_capabilities = {}
        self.performance_history = {}
        self.collaboration_matrix = defaultdict(dict)
    
    def register_agent(self, agent: BaseVIBAAgent):
        """에이전트 등록"""
        self.agent_capabilities[agent.agent_id] = agent.capabilities
        if agent.agent_id not in self.performance_history:
            self.performance_history[agent.agent_id] = AgentPerformanceMetrics(agent.agent_id)
    
    def select_optimal_agents(self, 
                            required_capabilities: List[AgentCapability], 
                            task_complexity: float,
                            time_constraint: float = None) -> List[str]:
        """최적 에이전트 조합 선택"""
        
        # 1. 필수 역량을 가진 에이전트 필터링
        candidate_agents = []
        for agent_id, capabilities in self.agent_capabilities.items():
            if any(cap in capabilities for cap in required_capabilities):
                candidate_agents.append(agent_id)
        
        # 2. 성능 기반 점수 계산
        agent_scores = {}
        for agent_id in candidate_agents:
            metrics = self.performance_history.get(agent_id)
            if metrics:
                # 효율성, 성공률, 협력성을 종합한 점수
                efficiency = metrics.efficiency_score
                success_rate = metrics.avg_success_rate
                collaboration = np.mean(list(metrics.collaboration_scores.values())) if metrics.collaboration_scores else 0.5
                
                # 복잡도에 따른 가중치 조정
                complexity_weight = min(task_complexity * 2, 1.0)
                agent_scores[agent_id] = (efficiency * 0.4 + success_rate * 0.4 + collaboration * 0.2) * complexity_weight
            else:
                agent_scores[agent_id] = 0.5  # 기본점수
        
        # 3. 시간 제약 고려
        if time_constraint:
            for agent_id in candidate_agents:
                metrics = self.performance_history.get(agent_id)
                if metrics and metrics.avg_execution_time > time_constraint:
                    agent_scores[agent_id] *= 0.5  # 시간 초과 시 점수 감소
        
        # 4. 상위 에이전트 선택
        sorted_agents = sorted(agent_scores.items(), key=lambda x: x[1], reverse=True)
        
        # 복잡도에 따른 에이전트 수 결정
        if task_complexity < 0.3:
            return [sorted_agents[0][0]]  # 단일 에이전트
        elif task_complexity < 0.7:
            return [agent[0] for agent in sorted_agents[:2]]  # 2개 에이전트
        else:
            return [agent[0] for agent in sorted_agents[:4]]  # 최대 4개 에이전트


class PredictiveScheduler:
    """예측적 스케줄러"""
    
    def __init__(self):
        self.execution_patterns = {}
        self.prediction_model = None
    
    async def predict_next_steps(self, current_state: Dict[str, Any], execution_history: List[Dict]) -> List[str]:
        """다음 단계 예측"""
        predicted_steps = []
        
        # 현재 상태 분석
        current_outputs = current_state.get("outputs", {})
        
        # 패턴 기반 예측
        if "design_concept" in current_outputs:
            predicted_steps.append("structural_analysis")
            predicted_steps.append("performance_evaluation")
        
        if "bim_model" in current_outputs:
            predicted_steps.append("code_compliance_check")
            predicted_steps.append("cost_estimation")
        
        if "performance_issues" in current_outputs:
            predicted_steps.append("optimization_recommendations")
        
        # 실행 이력 기반 예측
        if execution_history:
            recent_patterns = self._analyze_execution_patterns(execution_history[-10:])
            predicted_steps.extend(recent_patterns)
        
        return list(set(predicted_steps))  # 중복 제거
    
    def _analyze_execution_patterns(self, history: List[Dict]) -> List[str]:
        """실행 패턴 분석"""
        patterns = []
        
        # 간단한 패턴 매칭 (실제로는 더 정교한 ML 모델 사용)
        for record in history:
            if record.get("success") and "next_recommended" in record:
                patterns.extend(record["next_recommended"])
        
        # 빈도 기반 정렬
        from collections import Counter
        pattern_counts = Counter(patterns)
        return [pattern for pattern, count in pattern_counts.most_common(3)]


class CollaborationOptimizer:
    """협력 최적화기"""
    
    def __init__(self):
        self.collaboration_history = []
        self.synergy_matrix = defaultdict(dict)
        self.conflict_patterns = set()
    
    def learn_collaboration_patterns(self, agents_used: List[str], performance_metrics: Dict):
        """협력 패턴 학습"""
        self.collaboration_history.append({
            "agents": agents_used,
            "metrics": performance_metrics,
            "timestamp": time.time()
        })
        
        # 에이전트 쌍별 시너지 계산
        for i, agent1 in enumerate(agents_used):
            for agent2 in agents_used[i+1:]:
                synergy_score = self._calculate_synergy(agent1, agent2, performance_metrics)
                self.synergy_matrix[agent1][agent2] = synergy_score
                self.synergy_matrix[agent2][agent1] = synergy_score
    
    def _calculate_synergy(self, agent1: str, agent2: str, metrics: Dict) -> float:
        """두 에이전트 간 시너지 점수 계산"""
        # 성능 향상도를 기반으로 시너지 계산
        individual_performance = (metrics.get(f"{agent1}_individual", 0.5) + 
                                metrics.get(f"{agent2}_individual", 0.5)) / 2
        combined_performance = metrics.get("combined_performance", 0.5)
        
        return max(0, combined_performance - individual_performance)
    
    def optimize_agent_combination(self, candidate_agents: List[str]) -> List[str]:
        """최적 에이전트 조합 선택"""
        if len(candidate_agents) <= 2:
            return candidate_agents
        
        # 시너지 점수 기반 조합 최적화
        best_combination = []
        best_score = 0
        
        from itertools import combinations
        for r in range(2, min(len(candidate_agents) + 1, 5)):  # 최대 4개 조합
            for combo in combinations(candidate_agents, r):
                score = self._calculate_combination_score(list(combo))
                if score > best_score:
                    best_score = score
                    best_combination = list(combo)
        
        return best_combination if best_combination else candidate_agents[:2]
    
    def _calculate_combination_score(self, agents: List[str]) -> float:
        """조합 점수 계산"""
        if len(agents) <= 1:
            return 0
        
        synergy_sum = 0
        pair_count = 0
        
        for i, agent1 in enumerate(agents):
            for agent2 in agents[i+1:]:
                synergy_score = self.synergy_matrix.get(agent1, {}).get(agent2, 0)
                synergy_sum += synergy_score
                pair_count += 1
        
        return synergy_sum / pair_count if pair_count > 0 else 0


class PerformanceOptimizer:
    """성능 최적화기"""
    
    def __init__(self):
        self.performance_thresholds = {
            "response_time": 2.0,
            "success_rate": 0.95,
            "resource_usage": 0.8,
            "quality_score": 0.9
        }
        self.optimization_actions = {
            "slow_response": ["enable_caching", "reduce_complexity", "parallel_execution"],
            "low_success": ["add_validation", "increase_retries", "fallback_agents"],
            "high_resource": ["optimize_algorithms", "batch_processing", "resource_pooling"],
            "low_quality": ["add_review_step", "quality_checks", "expert_validation"]
        }
    
    async def optimize_workflow(self, current_metrics: Dict, workflow_config: Dict) -> Dict[str, Any]:
        """워크플로우 최적화"""
        optimizations = []
        
        # 성능 문제 식별
        issues = self._identify_performance_issues(current_metrics)
        
        # 각 문제에 대한 최적화 방안 제시
        for issue in issues:
            if issue in self.optimization_actions:
                optimizations.extend(self.optimization_actions[issue])
        
        # 최적화 방안 적용
        optimized_config = workflow_config.copy()
        for optimization in set(optimizations):  # 중복 제거
            optimized_config = self._apply_optimization(optimized_config, optimization)
        
        return {
            "optimized_config": optimized_config,
            "applied_optimizations": list(set(optimizations)),
            "expected_improvements": self._estimate_improvements(optimizations)
        }
    
    def _identify_performance_issues(self, metrics: Dict) -> List[str]:
        """성능 문제 식별"""
        issues = []
        
        if metrics.get("response_time", 0) > self.performance_thresholds["response_time"]:
            issues.append("slow_response")
        
        if metrics.get("success_rate", 1) < self.performance_thresholds["success_rate"]:
            issues.append("low_success")
        
        if metrics.get("resource_usage", 0) > self.performance_thresholds["resource_usage"]:
            issues.append("high_resource")
        
        if metrics.get("quality_score", 1) < self.performance_thresholds["quality_score"]:
            issues.append("low_quality")
        
        return issues
    
    def _apply_optimization(self, config: Dict, optimization: str) -> Dict:
        """최적화 방안 적용"""
        optimized = config.copy()
        
        if optimization == "enable_caching":
            optimized["caching_enabled"] = True
            optimized["cache_ttl"] = 300  # 5분
        
        elif optimization == "parallel_execution":
            optimized["execution_strategy"] = "parallel"
            optimized["max_parallel_tasks"] = 3
        
        elif optimization == "add_validation":
            optimized["validation_enabled"] = True
            optimized["validation_threshold"] = 0.8
        
        elif optimization == "increase_retries":
            optimized["max_retries"] = max(optimized.get("max_retries", 1) + 1, 5)
        
        elif optimization == "add_review_step":
            optimized["review_enabled"] = True
            optimized["review_agent"] = "design_reviewer"
        
        return optimized
    
    def _estimate_improvements(self, optimizations: List[str]) -> Dict[str, float]:
        """개선 효과 추정"""
        improvements = {
            "response_time_reduction": 0,
            "success_rate_increase": 0,
            "resource_efficiency": 0,
            "quality_improvement": 0
        }
        
        improvement_map = {
            "enable_caching": {"response_time_reduction": 0.3},
            "parallel_execution": {"response_time_reduction": 0.4},
            "add_validation": {"success_rate_increase": 0.1, "quality_improvement": 0.2},
            "increase_retries": {"success_rate_increase": 0.05},
            "add_review_step": {"quality_improvement": 0.3}
        }
        
        for opt in optimizations:
            if opt in improvement_map:
                for metric, value in improvement_map[opt].items():
                    improvements[metric] += value
        
        return improvements


class AdvancedOrchestrator:
    """고급 오케스트레이터"""
    
    def __init__(self):
        self.agents = {}
        self.agent_selector = IntelligentAgentSelector()
        self.scheduler = PredictiveScheduler()
        self.collaboration_optimizer = CollaborationOptimizer()
        self.performance_optimizer = PerformanceOptimizer()
        
        self.execution_history = deque(maxlen=1000)
        self.current_workflows = {}
        self.performance_metrics = {}
        
        # 고급 설정
        self.adaptive_learning_enabled = True
        self.real_time_optimization = True
        self.predictive_caching = True
    
    async def register_agent(self, agent: BaseVIBAAgent):
        """에이전트 등록"""
        self.agents[agent.agent_id] = agent
        self.agent_selector.register_agent(agent)
        await agent.initialize()
        logger.info(f"고급 오케스트레이터에 {agent.agent_id} 등록됨")
    
    async def process_intelligent_request(self, 
                                        user_input: str, 
                                        context: Dict[str, Any] = None,
                                        optimization_level: str = "adaptive") -> Dict[str, Any]:
        """지능형 요청 처리"""
        
        start_time = time.time()
        request_id = f"req_{int(start_time * 1000)}"
        
        try:
            # 1. 요청 분석 및 복잡도 평가
            task_analysis = await self._analyze_task_complexity(user_input, context)
            
            # 2. 최적 에이전트 선택
            selected_agents = self.agent_selector.select_optimal_agents(
                task_analysis["required_capabilities"],
                task_analysis["complexity_score"],
                task_analysis.get("time_constraint")
            )
            
            # 3. 협력 최적화
            if len(selected_agents) > 1:
                selected_agents = self.collaboration_optimizer.optimize_agent_combination(selected_agents)
            
            # 4. 실행 계획 수립
            execution_plan = await self._create_execution_plan(
                selected_agents, 
                task_analysis, 
                optimization_level
            )
            
            # 5. 워크플로우 실행
            result = await self._execute_optimized_workflow(
                execution_plan, 
                user_input, 
                context
            )
            
            # 6. 성능 학습 및 최적화
            if self.adaptive_learning_enabled:
                await self._learn_from_execution(execution_plan, result, time.time() - start_time)
            
            # 7. 결과 후처리
            final_result = await self._post_process_results(result, task_analysis)
            
            execution_time = time.time() - start_time
            
            # 실행 이력 기록
            self.execution_history.append({
                "request_id": request_id,
                "execution_time": execution_time,
                "agents_used": selected_agents,
                "success": final_result.get("success", False),
                "optimization_level": optimization_level,
                "task_complexity": task_analysis["complexity_score"]
            })
            
            return {
                **final_result,
                "orchestration_metadata": {
                    "request_id": request_id,
                    "execution_time": execution_time,
                    "agents_used": selected_agents,
                    "optimization_applied": execution_plan.estimated_time,
                    "task_complexity": task_analysis["complexity_score"]
                }
            }
            
        except Exception as e:
            logger.error(f"지능형 요청 처리 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "orchestration_metadata": {
                    "request_id": request_id,
                    "execution_time": time.time() - start_time
                }
            }
    
    async def _analyze_task_complexity(self, user_input: str, context: Dict = None) -> Dict[str, Any]:
        """작업 복잡도 분석"""
        
        # 키워드 기반 복잡도 평가
        complexity_indicators = {
            "간단한": 0.1, "기본": 0.2, "표준": 0.3,
            "복잡한": 0.6, "고급": 0.7, "전문적인": 0.8,
            "종합적인": 0.9, "완전한": 1.0
        }
        
        capability_keywords = {
            "설계": [AgentCapability.DESIGN_THEORY_APPLICATION],
            "BIM": [AgentCapability.BIM_MODEL_GENERATION],
            "성능": [AgentCapability.PERFORMANCE_ANALYSIS],
            "검토": [AgentCapability.DESIGN_REVIEW],
            "분석": [AgentCapability.NATURAL_LANGUAGE_UNDERSTANDING, AgentCapability.PERFORMANCE_ANALYSIS]
        }
        
        # 복잡도 점수 계산
        complexity_score = 0.3  # 기본값
        for indicator, score in complexity_indicators.items():
            if indicator in user_input:
                complexity_score = max(complexity_score, score)
        
        # 필요한 역량 식별
        required_capabilities = []
        for keyword, capabilities in capability_keywords.items():
            if keyword in user_input:
                required_capabilities.extend(capabilities)
        
        if not required_capabilities:
            required_capabilities = [AgentCapability.NATURAL_LANGUAGE_UNDERSTANDING]
        
        # 컨텍스트 기반 조정
        if context:
            if context.get("urgent", False):
                complexity_score *= 1.2  # 긴급한 경우 복잡도 증가
            if context.get("high_quality", False):
                complexity_score *= 1.1  # 고품질 요구 시 복잡도 증가
        
        return {
            "complexity_score": min(complexity_score, 1.0),
            "required_capabilities": list(set(required_capabilities)),
            "time_constraint": context.get("time_limit") if context else None,
            "quality_requirements": context.get("quality_level", "standard") if context else "standard"
        }
    
    async def _create_execution_plan(self, 
                                   agents: List[str], 
                                   task_analysis: Dict,
                                   optimization_level: str) -> ExecutionPlan:
        """실행 계획 수립"""
        
        nodes = []
        estimated_time = 0
        
        if optimization_level == "adaptive" and len(agents) > 1:
            # 적응형: 의존성과 시너지를 고려한 최적 배치
            dependency_map = {
                "design_theorist": [],
                "bim_specialist": ["design_theorist"],
                "performance_analyst": ["bim_specialist"],
                "design_reviewer": ["bim_specialist", "performance_analyst"]
            }
            
            for i, agent_id in enumerate(agents):
                dependencies = [dep for dep in dependency_map.get(agent_id, []) if dep in agents]
                
                node = WorkflowNode(
                    node_id=f"node_{i}",
                    agent_id=agent_id,
                    dependencies=dependencies,
                    priority=len(dependencies) + 1,
                    timeout=30.0 * (1 + task_analysis["complexity_score"])
                )
                nodes.append(node)
                estimated_time += 15.0 * (1 + task_analysis["complexity_score"])
            
        elif optimization_level == "parallel" and len(agents) > 1:
            # 병렬: 독립 실행 가능한 에이전트들을 병렬 처리
            parallel_groups = self._identify_parallel_groups(agents)
            
            for group_id, group_agents in parallel_groups.items():
                for i, agent_id in enumerate(group_agents):
                    node = WorkflowNode(
                        node_id=f"node_{group_id}_{i}",
                        agent_id=agent_id,
                        parallel_group=group_id,
                        timeout=20.0 * (1 + task_analysis["complexity_score"])
                    )
                    nodes.append(node)
            
            # 병렬 실행으로 시간 단축
            estimated_time = max(10.0 * len(parallel_groups), 30.0) * (1 + task_analysis["complexity_score"])
            
        else:
            # 순차 실행 (기본)
            for i, agent_id in enumerate(agents):
                node = WorkflowNode(
                    node_id=f"node_{i}",
                    agent_id=agent_id,
                    dependencies=[f"node_{i-1}"] if i > 0 else [],
                    timeout=25.0 * (1 + task_analysis["complexity_score"])
                )
                nodes.append(node)
                estimated_time += 20.0 * (1 + task_analysis["complexity_score"])
        
        return ExecutionPlan(
            plan_id=f"plan_{int(time.time() * 1000)}",
            nodes=nodes,
            estimated_time=estimated_time,
            confidence_score=0.8 + (0.2 * (1 - task_analysis["complexity_score"])),
            resource_requirements={"cpu": 0.5 * len(agents), "memory": 1.0 * len(agents)}
        )
    
    def _identify_parallel_groups(self, agents: List[str]) -> Dict[str, List[str]]:
        """병렬 처리 가능한 에이전트 그룹 식별"""
        groups = {}
        
        # 독립적으로 실행 가능한 에이전트들을 그룹화
        independent_agents = ["design_theorist", "architectural_design_specialist"]
        dependent_agents = ["bim_specialist", "performance_analyst", "design_reviewer"]
        
        group_1 = [agent for agent in agents if agent in independent_agents]
        group_2 = [agent for agent in agents if agent in dependent_agents]
        
        if group_1:
            groups["independent"] = group_1
        if group_2:
            groups["dependent"] = group_2
        
        return groups
    
    async def _execute_optimized_workflow(self, 
                                        plan: ExecutionPlan, 
                                        user_input: str, 
                                        context: Dict) -> Dict[str, Any]:
        """최적화된 워크플로우 실행"""
        
        workflow_id = plan.plan_id
        self.current_workflows[workflow_id] = {
            "plan": plan,
            "status": "running",
            "start_time": time.time(),
            "results": {}
        }
        
        try:
            # 의존성 그래프 기반 실행 순서 결정
            execution_order = self._resolve_dependencies(plan.nodes)
            
            # 병렬 그룹별 실행
            parallel_groups = self._group_by_parallel(execution_order)
            
            accumulated_results = {"user_input": user_input, "context": context}
            
            for group in parallel_groups:
                if len(group) == 1:
                    # 단일 노드 실행
                    node = group[0]
                    result = await self._execute_single_node(node, accumulated_results)
                    accumulated_results[f"{node.agent_id}_result"] = result
                else:
                    # 병렬 실행
                    tasks = []
                    for node in group:
                        task = self._execute_single_node(node, accumulated_results)
                        tasks.append((node, task))
                    
                    # 병렬 실행 및 결과 수집
                    parallel_results = await asyncio.gather(
                        *[task for _, task in tasks], 
                        return_exceptions=True
                    )
                    
                    for (node, _), result in zip(tasks, parallel_results):
                        if isinstance(result, Exception):
                            logger.error(f"노드 {node.node_id} 실행 실패: {result}")
                            result = {"success": False, "error": str(result)}
                        accumulated_results[f"{node.agent_id}_result"] = result
            
            self.current_workflows[workflow_id]["status"] = "completed"
            self.current_workflows[workflow_id]["results"] = accumulated_results
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "results": accumulated_results,
                "execution_summary": self._generate_execution_summary(plan, accumulated_results)
            }
            
        except Exception as e:
            self.current_workflows[workflow_id]["status"] = "failed"
            self.current_workflows[workflow_id]["error"] = str(e)
            logger.error(f"워크플로우 {workflow_id} 실행 실패: {e}")
            
            return {
                "success": False,
                "workflow_id": workflow_id,
                "error": str(e)
            }
    
    def _resolve_dependencies(self, nodes: List[WorkflowNode]) -> List[List[WorkflowNode]]:
        """의존성 해결 및 실행 순서 결정"""
        # 위상 정렬 알고리즘 사용
        in_degree = {node.node_id: len(node.dependencies) for node in nodes}
        node_map = {node.node_id: node for node in nodes}
        
        execution_levels = []
        remaining_nodes = nodes.copy()
        
        while remaining_nodes:
            # 의존성이 없는 노드들 찾기
            ready_nodes = [node for node in remaining_nodes if in_degree[node.node_id] == 0]
            
            if not ready_nodes:
                # 순환 의존성 발생 - 강제로 하나 선택
                ready_nodes = [remaining_nodes[0]]
                logger.warning("순환 의존성 감지됨, 강제 실행")
            
            execution_levels.append(ready_nodes)
            
            # 실행될 노드들 제거 및 의존성 업데이트
            for ready_node in ready_nodes:
                remaining_nodes.remove(ready_node)
                
                # 이 노드에 의존하는 다른 노드들의 의존성 감소
                for node in remaining_nodes:
                    if ready_node.node_id in node.dependencies:
                        in_degree[node.node_id] -= 1
        
        return execution_levels
    
    def _group_by_parallel(self, execution_levels: List[List[WorkflowNode]]) -> List[List[WorkflowNode]]:
        """병렬 그룹별로 재구성"""
        parallel_groups = []
        
        for level in execution_levels:
            # 같은 병렬 그룹끼리 묶기
            group_map = defaultdict(list)
            
            for node in level:
                group_key = node.parallel_group or node.node_id
                group_map[group_key].append(node)
            
            # 각 그룹을 개별 실행 단위로 추가
            for group_nodes in group_map.values():
                parallel_groups.append(group_nodes)
        
        return parallel_groups
    
    async def _execute_single_node(self, node: WorkflowNode, context: Dict[str, Any]) -> Dict[str, Any]:
        """단일 노드 실행"""
        agent = self.agents.get(node.agent_id)
        if not agent:
            return {"success": False, "error": f"에이전트 {node.agent_id}를 찾을 수 없음"}
        
        try:
            # 조건 확인
            if node.conditions:
                if not self._check_conditions(node.conditions, context):
                    return {"success": True, "skipped": True, "reason": "조건 불충족"}
            
            # 실행
            start_time = time.time()
            result = await asyncio.wait_for(
                agent.process_task_async(context), 
                timeout=node.timeout
            )
            execution_time = time.time() - start_time
            
            # 성능 메트릭 업데이트
            agent_metrics = self.agent_selector.performance_history.get(node.agent_id)
            if agent_metrics:
                agent_metrics.execution_times.append(execution_time)
                agent_metrics.success_rates.append(1.0 if result.get("success", False) else 0.0)
            
            return result
            
        except asyncio.TimeoutError:
            logger.warning(f"노드 {node.node_id} 실행 시간 초과")
            return {"success": False, "error": "실행 시간 초과"}
        except Exception as e:
            logger.error(f"노드 {node.node_id} 실행 오류: {e}")
            return {"success": False, "error": str(e)}
    
    def _check_conditions(self, conditions: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """실행 조건 확인"""
        for key, expected_value in conditions.items():
            if key not in context:
                return False
            if context[key] != expected_value:
                return False
        return True
    
    def _generate_execution_summary(self, plan: ExecutionPlan, results: Dict[str, Any]) -> Dict[str, Any]:
        """실행 요약 생성"""
        successful_agents = []
        failed_agents = []
        
        for node in plan.nodes:
            agent_result = results.get(f"{node.agent_id}_result", {})
            if agent_result.get("success", False):
                successful_agents.append(node.agent_id)
            else:
                failed_agents.append(node.agent_id)
        
        return {
            "total_agents": len(plan.nodes),
            "successful_agents": successful_agents,
            "failed_agents": failed_agents,
            "success_rate": len(successful_agents) / len(plan.nodes) if plan.nodes else 0,
            "estimated_vs_actual": {
                "estimated_time": plan.estimated_time,
                "confidence_score": plan.confidence_score
            }
        }
    
    async def _learn_from_execution(self, plan: ExecutionPlan, result: Dict[str, Any], execution_time: float):
        """실행 결과로부터 학습"""
        
        # 성능 메트릭 업데이트
        agents_used = [node.agent_id for node in plan.nodes]
        performance_metrics = {
            "execution_time": execution_time,
            "success_rate": result.get("execution_summary", {}).get("success_rate", 0),
            "agents_count": len(agents_used)
        }
        
        # 협력 패턴 학습
        self.collaboration_optimizer.learn_collaboration_patterns(agents_used, performance_metrics)
        
        # 실시간 최적화 적용
        if self.real_time_optimization:
            current_metrics = {
                "response_time": execution_time,
                "success_rate": performance_metrics["success_rate"],
                "resource_usage": performance_metrics["agents_count"] / 10.0  # 정규화
            }
            
            optimization_result = await self.performance_optimizer.optimize_workflow(
                current_metrics, 
                {"current_config": "default"}
            )
            
            if optimization_result.get("applied_optimizations"):
                logger.info(f"실시간 최적화 적용: {optimization_result['applied_optimizations']}")
    
    async def _post_process_results(self, result: Dict[str, Any], task_analysis: Dict) -> Dict[str, Any]:
        """결과 후처리"""
        
        # 품질 점수 계산
        quality_score = self._calculate_quality_score(result, task_analysis)
        
        # 추천사항 생성
        recommendations = await self._generate_recommendations(result, task_analysis)
        
        return {
            **result,
            "quality_assessment": {
                "quality_score": quality_score,
                "quality_level": self._get_quality_level(quality_score)
            },
            "recommendations": recommendations,
            "next_steps": await self.scheduler.predict_next_steps(result, list(self.execution_history))
        }
    
    def _calculate_quality_score(self, result: Dict[str, Any], task_analysis: Dict) -> float:
        """품질 점수 계산"""
        base_score = 0.7  # 기본 점수
        
        # 성공률 기반 조정
        execution_summary = result.get("execution_summary", {})
        success_rate = execution_summary.get("success_rate", 0)
        base_score *= (0.5 + 0.5 * success_rate)
        
        # 복잡도 대비 성과 조정
        complexity = task_analysis.get("complexity_score", 0.5)
        if success_rate > complexity:
            base_score *= 1.1  # 복잡도 대비 좋은 성과
        
        # 에이전트 활용도 조정
        agents_used = len(execution_summary.get("successful_agents", []))
        if agents_used >= 2:
            base_score *= 1.05  # 다중 에이전트 활용 시 가산점
        
        return min(base_score, 1.0)
    
    def _get_quality_level(self, score: float) -> str:
        """품질 수준 반환"""
        if score >= 0.9:
            return "excellent"
        elif score >= 0.8:
            return "good"
        elif score >= 0.7:
            return "satisfactory"
        elif score >= 0.6:
            return "acceptable"
        else:
            return "needs_improvement"
    
    async def _generate_recommendations(self, result: Dict[str, Any], task_analysis: Dict) -> List[str]:
        """추천사항 생성"""
        recommendations = []
        
        execution_summary = result.get("execution_summary", {})
        success_rate = execution_summary.get("success_rate", 0)
        
        if success_rate < 0.8:
            recommendations.append("실행 성공률 개선을 위해 검증 단계를 추가하는 것을 고려하세요")
        
        if task_analysis.get("complexity_score", 0) > 0.7:
            recommendations.append("복잡한 작업의 경우 단계별 검토를 통해 품질을 향상시킬 수 있습니다")
        
        failed_agents = execution_summary.get("failed_agents", [])
        if failed_agents:
            recommendations.append(f"실패한 에이전트({', '.join(failed_agents)})에 대한 대체 방안을 고려하세요")
        
        return recommendations
    
    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 조회"""
        active_workflows = sum(1 for w in self.current_workflows.values() if w["status"] == "running")
        
        # 최근 성능 통계
        recent_executions = list(self.execution_history)[-50:]  # 최근 50개
        avg_execution_time = np.mean([ex["execution_time"] for ex in recent_executions]) if recent_executions else 0
        avg_success_rate = np.mean([1 if ex["success"] else 0 for ex in recent_executions]) if recent_executions else 0
        
        return {
            "system_health": "healthy" if avg_success_rate > 0.8 else "degraded",
            "active_workflows": active_workflows,
            "total_agents": len(self.agents),
            "recent_performance": {
                "avg_execution_time": avg_execution_time,
                "avg_success_rate": avg_success_rate,
                "total_executions": len(recent_executions)
            },
            "optimization_status": {
                "adaptive_learning": self.adaptive_learning_enabled,
                "real_time_optimization": self.real_time_optimization,
                "predictive_caching": self.predictive_caching
            }
        }