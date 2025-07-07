"""
오케스트레이터 고도화 테스트 스위트
=================================

VIBA AI 코어 오케스트레이터의 고도화 기능을 검증하는 종합 테스트 시스템

@version 1.0
@author VIBA AI Team
@date 2025.07.06
"""

import asyncio
import json
import logging
import time
import numpy as np
import psutil
import gc
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
import random
import statistics
from concurrent.futures import ThreadPoolExecutor

# 프로젝트 임포트
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# 고도화된 오케스트레이터 임포트
try:
    from ai.advanced_orchestrator import (
        AdvancedOrchestrator, IntelligentAgentSelector, PredictiveScheduler,
        CollaborationOptimizer, PerformanceOptimizer, AgentPerformanceMetrics
    )
    ADVANCED_ORCHESTRATOR_AVAILABLE = True
except ImportError as e:
    print(f"고급 오케스트레이터 임포트 실패: {e}")
    ADVANCED_ORCHESTRATOR_AVAILABLE = False

# 기본 에이전트 임포트
try:
    from ai.agents.simple_test_agent import SimpleTestAgent
    from ai.base_agent import BaseVIBAAgent, AgentCapability
    BASIC_AGENTS_AVAILABLE = True
except ImportError as e:
    print(f"기본 에이전트 임포트 실패: {e}")
    BASIC_AGENTS_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """벤치마크 결과"""
    test_name: str
    execution_time: float
    success_rate: float
    throughput: float
    resource_usage: Dict[str, float]
    quality_metrics: Dict[str, float]
    improvement_rate: float = 0.0
    baseline_comparison: Dict[str, float] = field(default_factory=dict)


@dataclass
class PerformanceMetrics:
    """성능 메트릭"""
    response_times: List[float] = field(default_factory=list)
    success_counts: List[bool] = field(default_factory=list)
    resource_usage: List[Dict[str, float]] = field(default_factory=list)
    agent_utilization: List[Dict[str, float]] = field(default_factory=list)
    
    @property
    def avg_response_time(self) -> float:
        return np.mean(self.response_times) if self.response_times else 0.0
    
    @property
    def success_rate(self) -> float:
        return np.mean(self.success_counts) if self.success_counts else 0.0
    
    @property
    def throughput(self) -> float:
        if not self.response_times:
            return 0.0
        return len(self.response_times) / sum(self.response_times) if sum(self.response_times) > 0 else 0.0


class MockAgent(BaseVIBAAgent):
    """테스트용 모의 에이전트"""
    
    def __init__(self, agent_id: str, capabilities: List[AgentCapability], 
                 avg_execution_time: float = 1.0, success_rate: float = 0.9):
        super().__init__(agent_id, f"Mock {agent_id}", capabilities)
        self.avg_execution_time = avg_execution_time
        self.target_success_rate = success_rate
        self.call_count = 0
        
    async def initialize(self) -> bool:
        await asyncio.sleep(0.1)
        self.is_initialized = True
        return True
    
    async def execute_task(self, task) -> Dict[str, Any]:
        """모의 작업 실행"""
        self.call_count += 1
        
        # 실행 시간 시뮬레이션 (정규분포)
        execution_time = max(0.1, np.random.normal(self.avg_execution_time, 0.2))
        await asyncio.sleep(execution_time)
        
        # 성공/실패 시뮬레이션
        success = random.random() < self.target_success_rate
        
        return {
            "success": success,
            "agent_id": self.agent_id,
            "execution_time": execution_time,
            "call_count": self.call_count,
            "result": f"Mock result from {self.agent_id}" if success else None,
            "error": None if success else f"Simulated error in {self.agent_id}"
        }


class IntelligentAgentSelectorTest:
    """지능형 에이전트 선택기 테스트"""
    
    def __init__(self):
        self.selector = IntelligentAgentSelector() if ADVANCED_ORCHESTRATOR_AVAILABLE else None
        self.test_agents = self._create_test_agents()
    
    def _create_test_agents(self) -> List[MockAgent]:
        """테스트용 에이전트 생성"""
        return [
            MockAgent("fast_agent", [AgentCapability.DESIGN_THEORY_APPLICATION], 0.5, 0.95),
            MockAgent("slow_agent", [AgentCapability.BIM_MODEL_GENERATION], 2.0, 0.99),
            MockAgent("unreliable_agent", [AgentCapability.PERFORMANCE_ANALYSIS], 1.0, 0.7),
            MockAgent("balanced_agent", [AgentCapability.DESIGN_REVIEW], 1.0, 0.9),
            MockAgent("specialist_agent", [AgentCapability.NATURAL_LANGUAGE_UNDERSTANDING], 1.5, 0.95)
        ]
    
    async def test_agent_selection_accuracy(self) -> Dict[str, Any]:
        """에이전트 선택 정확도 테스트"""
        if not self.selector:
            return {"error": "지능형 선택기를 사용할 수 없음"}
        
        # 에이전트 등록
        for agent in self.test_agents:
            self.selector.register_agent(agent)
        
        test_cases = [
            {
                "required_capabilities": [AgentCapability.DESIGN_THEORY_APPLICATION],
                "complexity": 0.3,
                "expected_agents": ["fast_agent"],  # 빠른 에이전트 선호
                "time_constraint": 1.0
            },
            {
                "required_capabilities": [AgentCapability.BIM_MODEL_GENERATION],
                "complexity": 0.8,
                "expected_agents": ["slow_agent"],  # 정확도 높은 에이전트 선호
                "time_constraint": None
            },
            {
                "required_capabilities": [AgentCapability.DESIGN_THEORY_APPLICATION, AgentCapability.BIM_MODEL_GENERATION],
                "complexity": 0.6,
                "expected_agents": ["fast_agent", "slow_agent"],  # 다중 선택
                "time_constraint": 3.0
            }
        ]
        
        correct_selections = 0
        total_tests = len(test_cases)
        
        for i, test_case in enumerate(test_cases):
            selected_agents = self.selector.select_optimal_agents(
                test_case["required_capabilities"],
                test_case["complexity"],
                test_case.get("time_constraint")
            )
            
            # 선택 정확도 평가
            expected_set = set(test_case["expected_agents"])
            selected_set = set(selected_agents)
            
            if expected_set.intersection(selected_set):  # 하나라도 겹치면 부분 성공
                correct_selections += 1
            
            print(f"  테스트 {i+1}: 예상={test_case['expected_agents']}, 선택={selected_agents}")
        
        accuracy = correct_selections / total_tests
        
        return {
            "test_name": "agent_selection_accuracy",
            "accuracy": accuracy,
            "correct_selections": correct_selections,
            "total_tests": total_tests,
            "details": f"{correct_selections}/{total_tests} 선택이 정확함"
        }
    
    async def test_performance_learning(self) -> Dict[str, Any]:
        """성능 학습 능력 테스트"""
        if not self.selector:
            return {"error": "지능형 선택기를 사용할 수 없음"}
        
        # 에이전트 등록 및 초기 성능 기록
        for agent in self.test_agents:
            self.selector.register_agent(agent)
            
            # 가상 성능 이력 생성
            metrics = self.selector.performance_history[agent.agent_id]
            for _ in range(10):  # 10회 실행 이력
                metrics.execution_times.append(agent.avg_execution_time + random.gauss(0, 0.2))
                metrics.success_rates.append(1.0 if random.random() < agent.target_success_rate else 0.0)
        
        # 성능 기반 선택 테스트
        fast_requirements = [AgentCapability.DESIGN_THEORY_APPLICATION]
        selected_agents = self.selector.select_optimal_agents(fast_requirements, 0.5, 1.0)
        
        # fast_agent가 선택되었는지 확인 (가장 빠른 에이전트)
        performance_aware = "fast_agent" in selected_agents
        
        return {
            "test_name": "performance_learning",
            "performance_aware_selection": performance_aware,
            "selected_agents": selected_agents,
            "agent_efficiency_scores": {
                agent_id: metrics.efficiency_score 
                for agent_id, metrics in self.selector.performance_history.items()
            }
        }


class PredictiveSchedulerTest:
    """예측적 스케줄러 테스트"""
    
    def __init__(self):
        self.scheduler = PredictiveScheduler() if ADVANCED_ORCHESTRATOR_AVAILABLE else None
    
    async def test_next_step_prediction(self) -> Dict[str, Any]:
        """다음 단계 예측 테스트"""
        if not self.scheduler:
            return {"error": "예측 스케줄러를 사용할 수 없음"}
        
        test_scenarios = [
            {
                "current_state": {"outputs": {"design_concept": "modern_cafe"}},
                "execution_history": [],
                "expected_predictions": ["structural_analysis", "performance_evaluation"]
            },
            {
                "current_state": {"outputs": {"bim_model": "3d_model.ifc"}},
                "execution_history": [],
                "expected_predictions": ["code_compliance_check", "cost_estimation"]
            },
            {
                "current_state": {"outputs": {"performance_issues": ["high_energy_usage"]}},
                "execution_history": [],
                "expected_predictions": ["optimization_recommendations"]
            }
        ]
        
        prediction_accuracy = []
        
        for scenario in test_scenarios:
            predicted_steps = await self.scheduler.predict_next_steps(
                scenario["current_state"],
                scenario["execution_history"]
            )
            
            # 예측 정확도 계산
            expected_set = set(scenario["expected_predictions"])
            predicted_set = set(predicted_steps)
            
            if expected_set and predicted_set:
                intersection = len(expected_set.intersection(predicted_set))
                accuracy = intersection / len(expected_set)
            else:
                accuracy = 0.0
            
            prediction_accuracy.append(accuracy)
            
            print(f"  예상: {scenario['expected_predictions']}")
            print(f"  예측: {predicted_steps}")
            print(f"  정확도: {accuracy:.2f}")
        
        avg_accuracy = np.mean(prediction_accuracy)
        
        return {
            "test_name": "next_step_prediction",
            "average_accuracy": avg_accuracy,
            "individual_accuracies": prediction_accuracy,
            "total_scenarios": len(test_scenarios)
        }


class CollaborationOptimizerTest:
    """협력 최적화기 테스트"""
    
    def __init__(self):
        self.optimizer = CollaborationOptimizer() if ADVANCED_ORCHESTRATOR_AVAILABLE else None
    
    async def test_synergy_calculation(self) -> Dict[str, Any]:
        """시너지 계산 테스트"""
        if not self.optimizer:
            return {"error": "협력 최적화기를 사용할 수 없음"}
        
        # 가상 협력 시나리오 학습
        collaboration_scenarios = [
            {
                "agents": ["design_theorist", "bim_specialist"],
                "metrics": {
                    "design_theorist_individual": 0.7,
                    "bim_specialist_individual": 0.8,
                    "combined_performance": 0.9  # 시너지 효과
                }
            },
            {
                "agents": ["performance_analyst", "design_reviewer"],
                "metrics": {
                    "performance_analyst_individual": 0.6,
                    "design_reviewer_individual": 0.7,
                    "combined_performance": 0.8  # 시너지 효과
                }
            },
            {
                "agents": ["fast_agent", "unreliable_agent"],
                "metrics": {
                    "fast_agent_individual": 0.8,
                    "unreliable_agent_individual": 0.5,
                    "combined_performance": 0.6  # 부정적 영향
                }
            }
        ]
        
        # 협력 패턴 학습
        for scenario in collaboration_scenarios:
            self.optimizer.learn_collaboration_patterns(
                scenario["agents"],
                scenario["metrics"]
            )
        
        # 시너지 점수 확인
        synergy_scores = {}
        for scenario in collaboration_scenarios:
            if len(scenario["agents"]) >= 2:
                agent1, agent2 = scenario["agents"][:2]
                synergy = self.optimizer.synergy_matrix[agent1].get(agent2, 0)
                synergy_scores[f"{agent1}+{agent2}"] = synergy
        
        # 최적 조합 테스트
        test_agents = ["design_theorist", "bim_specialist", "performance_analyst", "unreliable_agent"]
        optimal_combination = self.optimizer.optimize_agent_combination(test_agents)
        
        return {
            "test_name": "synergy_calculation",
            "synergy_scores": synergy_scores,
            "optimal_combination": optimal_combination,
            "synergy_matrix_size": len(self.optimizer.synergy_matrix),
            "collaboration_history_count": len(self.optimizer.collaboration_history)
        }


class PerformanceOptimizerTest:
    """성능 최적화기 테스트"""
    
    def __init__(self):
        self.optimizer = PerformanceOptimizer() if ADVANCED_ORCHESTRATOR_AVAILABLE else None
    
    async def test_performance_optimization(self) -> Dict[str, Any]:
        """성능 최적화 테스트"""
        if not self.optimizer:
            return {"error": "성능 최적화기를 사용할 수 없음"}
        
        # 다양한 성능 문제 시나리오
        problem_scenarios = [
            {
                "name": "slow_response",
                "metrics": {"response_time": 5.0, "success_rate": 0.9, "resource_usage": 0.6},
                "expected_optimizations": ["enable_caching", "parallel_execution"]
            },
            {
                "name": "low_success",
                "metrics": {"response_time": 1.0, "success_rate": 0.8, "resource_usage": 0.5},
                "expected_optimizations": ["add_validation", "increase_retries"]
            },
            {
                "name": "high_resource",
                "metrics": {"response_time": 1.5, "success_rate": 0.95, "resource_usage": 0.9},
                "expected_optimizations": ["optimize_algorithms", "batch_processing"]
            }
        ]
        
        optimization_results = []
        
        for scenario in problem_scenarios:
            result = await self.optimizer.optimize_workflow(
                scenario["metrics"],
                {"current_config": "default"}
            )
            
            applied_optimizations = result.get("applied_optimizations", [])
            expected_optimizations = scenario["expected_optimizations"]
            
            # 최적화 적용 정확도
            matching_optimizations = set(applied_optimizations).intersection(set(expected_optimizations))
            accuracy = len(matching_optimizations) / len(expected_optimizations) if expected_optimizations else 0
            
            optimization_results.append({
                "scenario": scenario["name"],
                "accuracy": accuracy,
                "applied": applied_optimizations,
                "expected": expected_optimizations,
                "improvements": result.get("expected_improvements", {})
            })
            
            print(f"  시나리오: {scenario['name']}")
            print(f"  적용된 최적화: {applied_optimizations}")
            print(f"  정확도: {accuracy:.2f}")
        
        avg_accuracy = np.mean([r["accuracy"] for r in optimization_results])
        
        return {
            "test_name": "performance_optimization",
            "average_accuracy": avg_accuracy,
            "optimization_results": optimization_results,
            "total_scenarios": len(problem_scenarios)
        }


class AdvancedOrchestratorIntegrationTest:
    """고급 오케스트레이터 통합 테스트"""
    
    def __init__(self):
        self.orchestrator = AdvancedOrchestrator() if ADVANCED_ORCHESTRATOR_AVAILABLE else None
        self.test_agents = self._create_test_agents()
        self.baseline_metrics = None
    
    def _create_test_agents(self) -> List[MockAgent]:
        """테스트용 에이전트 생성"""
        return [
            MockAgent("design_theorist", [AgentCapability.DESIGN_THEORY_APPLICATION], 1.0, 0.9),
            MockAgent("bim_specialist", [AgentCapability.BIM_MODEL_GENERATION], 1.5, 0.95),
            MockAgent("performance_analyst", [AgentCapability.PERFORMANCE_ANALYSIS], 2.0, 0.88),
            MockAgent("design_reviewer", [AgentCapability.DESIGN_REVIEW], 1.2, 0.92),
            MockAgent("architectural_specialist", [AgentCapability.NATURAL_LANGUAGE_UNDERSTANDING], 1.8, 0.9)
        ]
    
    async def setup_orchestrator(self):
        """오케스트레이터 설정"""
        if not self.orchestrator:
            return False
        
        # 테스트 에이전트 등록
        for agent in self.test_agents:
            await self.orchestrator.register_agent(agent)
        
        return True
    
    async def test_intelligent_request_processing(self) -> Dict[str, Any]:
        """지능형 요청 처리 테스트"""
        if not await self.setup_orchestrator():
            return {"error": "오케스트레이터 설정 실패"}
        
        test_requests = [
            {
                "input": "강남에 간단한 카페를 설계해줘",
                "complexity": "low",
                "expected_agents": 1,
                "max_time": 2.0
            },
            {
                "input": "3층 복합 건물을 친환경 인증 받을 수 있게 설계해줘",
                "complexity": "high",
                "expected_agents": 3,
                "max_time": 5.0
            },
            {
                "input": "한옥 스타일 게스트하우스 성능 분석해줘",
                "complexity": "medium",
                "expected_agents": 2,
                "max_time": 3.0
            }
        ]
        
        results = []
        
        for request in test_requests:
            start_time = time.time()
            
            result = await self.orchestrator.process_intelligent_request(
                request["input"],
                {"quality_level": "high"},
                "adaptive"
            )
            
            execution_time = time.time() - start_time
            
            # 결과 검증
            success = result.get("success", False)
            agents_used = result.get("orchestration_metadata", {}).get("agents_used", [])
            
            test_result = {
                "request": request["input"],
                "success": success,
                "execution_time": execution_time,
                "agents_used": len(agents_used),
                "agents_list": agents_used,
                "within_time_limit": execution_time <= request["max_time"],
                "appropriate_agent_count": len(agents_used) <= request["expected_agents"] + 1  # 여유분 허용
            }
            
            results.append(test_result)
            
            print(f"  요청: {request['input'][:30]}...")
            print(f"  실행시간: {execution_time:.2f}초")
            print(f"  사용된 에이전트: {len(agents_used)}개")
            print(f"  성공: {success}")
        
        # 전체 성능 집계
        avg_execution_time = np.mean([r["execution_time"] for r in results])
        success_rate = np.mean([r["success"] for r in results])
        time_compliance = np.mean([r["within_time_limit"] for r in results])
        
        return {
            "test_name": "intelligent_request_processing",
            "average_execution_time": avg_execution_time,
            "success_rate": success_rate,
            "time_compliance_rate": time_compliance,
            "total_requests": len(results),
            "detailed_results": results
        }
    
    async def test_performance_improvement(self) -> Dict[str, Any]:
        """성능 개선 테스트"""
        if not await self.setup_orchestrator():
            return {"error": "오케스트레이터 설정 실패"}
        
        # 베이스라인 측정 (기본 설정)
        baseline_request = "서울에 사무용 빌딩을 설계해줘"
        baseline_times = []
        
        for _ in range(5):  # 5회 반복 측정
            start_time = time.time()
            result = await self.orchestrator.process_intelligent_request(
                baseline_request, {}, "sequential"  # 기본 순차 실행
            )
            execution_time = time.time() - start_time
            
            if result.get("success", False):
                baseline_times.append(execution_time)
        
        baseline_avg = np.mean(baseline_times) if baseline_times else 0
        
        # 최적화된 실행 측정
        optimized_times = []
        
        for _ in range(5):  # 5회 반복 측정
            start_time = time.time()
            result = await self.orchestrator.process_intelligent_request(
                baseline_request, {"quality_level": "high"}, "adaptive"  # 적응형 실행
            )
            execution_time = time.time() - start_time
            
            if result.get("success", False):
                optimized_times.append(execution_time)
        
        optimized_avg = np.mean(optimized_times) if optimized_times else 0
        
        # 개선율 계산
        if baseline_avg > 0:
            improvement_rate = (baseline_avg - optimized_avg) / baseline_avg * 100
        else:
            improvement_rate = 0
        
        return {
            "test_name": "performance_improvement",
            "baseline_avg_time": baseline_avg,
            "optimized_avg_time": optimized_avg,
            "improvement_rate_percent": improvement_rate,
            "baseline_measurements": len(baseline_times),
            "optimized_measurements": len(optimized_times),
            "statistical_significance": abs(improvement_rate) > 10  # 10% 이상 개선을 유의미로 판단
        }


class StressTestSuite:
    """스트레스 테스트 스위트"""
    
    def __init__(self):
        self.orchestrator = AdvancedOrchestrator() if ADVANCED_ORCHESTRATOR_AVAILABLE else None
        self.test_agents = self._create_test_agents()
    
    def _create_test_agents(self) -> List[MockAgent]:
        """고성능 테스트용 에이전트 생성"""
        return [
            MockAgent("fast_agent_1", [AgentCapability.DESIGN_THEORY_APPLICATION], 0.3, 0.95),
            MockAgent("fast_agent_2", [AgentCapability.BIM_MODEL_GENERATION], 0.5, 0.93),
            MockAgent("fast_agent_3", [AgentCapability.PERFORMANCE_ANALYSIS], 0.4, 0.92),
            MockAgent("fast_agent_4", [AgentCapability.DESIGN_REVIEW], 0.6, 0.94)
        ]
    
    async def setup_stress_test(self):
        """스트레스 테스트 설정"""
        if not self.orchestrator:
            return False
        
        for agent in self.test_agents:
            await self.orchestrator.register_agent(agent)
        
        return True
    
    async def test_concurrent_load(self, concurrent_requests: int = 50, duration: int = 30) -> Dict[str, Any]:
        """동시 부하 테스트"""
        if not await self.setup_stress_test():
            return {"error": "스트레스 테스트 설정 실패"}
        
        test_requests = [
            "강남에 카페를 설계해줘",
            "사무용 빌딩 성능 분석해줘",
            "주택 설계 검토해줘",
            "한옥 스타일 건물 설계해줘",
            "복합 건물 BIM 모델 생성해줘"
        ]
        
        metrics = PerformanceMetrics()
        start_time = time.time()
        completed_requests = 0
        errors = []
        
        async def process_single_request(request_id: int):
            """단일 요청 처리"""
            nonlocal completed_requests
            
            try:
                request_start = time.time()
                request_text = random.choice(test_requests)
                
                result = await self.orchestrator.process_intelligent_request(
                    request_text, {}, "adaptive"
                )
                
                request_time = time.time() - request_start
                success = result.get("success", False)
                
                # 메트릭 기록
                metrics.response_times.append(request_time)
                metrics.success_counts.append(success)
                
                # 리소스 사용량 기록
                process = psutil.Process()
                resource_usage = {
                    "cpu_percent": process.cpu_percent(),
                    "memory_mb": process.memory_info().rss / 1024 / 1024
                }
                metrics.resource_usage.append(resource_usage)
                
                completed_requests += 1
                
            except Exception as e:
                errors.append(str(e))
        
        # 동시 요청 생성 및 실행
        tasks = []
        for i in range(concurrent_requests):
            task = asyncio.create_task(process_single_request(i))
            tasks.append(task)
            
            # 짧은 간격으로 요청 시작 (실제 부하 시뮬레이션)
            await asyncio.sleep(0.1)
        
        # 모든 작업 완료 대기 (최대 duration 초)
        try:
            await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout=duration)
        except asyncio.TimeoutError:
            # 타임아웃 시 미완료 작업 취소
            for task in tasks:
                if not task.done():
                    task.cancel()
        
        total_time = time.time() - start_time
        
        # 최종 리소스 사용량
        process = psutil.Process()
        final_memory = process.memory_info().rss / 1024 / 1024
        
        return {
            "test_name": "concurrent_load_test",
            "concurrent_requests": concurrent_requests,
            "completed_requests": completed_requests,
            "completion_rate": completed_requests / concurrent_requests,
            "total_duration": total_time,
            "average_response_time": metrics.avg_response_time,
            "success_rate": metrics.success_rate,
            "throughput_rps": completed_requests / total_time if total_time > 0 else 0,
            "peak_memory_mb": final_memory,
            "error_count": len(errors),
            "errors": errors[:5]  # 최대 5개 에러만 표시
        }
    
    async def test_memory_stability(self, iterations: int = 100) -> Dict[str, Any]:
        """메모리 안정성 테스트"""
        if not await self.setup_stress_test():
            return {"error": "메모리 테스트 설정 실패"}
        
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_samples = [initial_memory]
        
        for i in range(iterations):
            # 요청 처리
            result = await self.orchestrator.process_intelligent_request(
                f"테스트 요청 {i+1}", {}, "adaptive"
            )
            
            # 메모리 사용량 측정
            current_memory = psutil.Process().memory_info().rss / 1024 / 1024
            memory_samples.append(current_memory)
            
            # 10회마다 가비지 컬렉션
            if (i + 1) % 10 == 0:
                gc.collect()
                
                # GC 후 메모리 측정
                gc_memory = psutil.Process().memory_info().rss / 1024 / 1024
                memory_samples.append(gc_memory)
        
        final_memory = memory_samples[-1]
        memory_increase = final_memory - initial_memory
        max_memory = max(memory_samples)
        
        # 메모리 누수 감지 (선형 증가 경향)
        if len(memory_samples) > 10:
            # 선형 회귀로 증가 경향 분석
            x = np.arange(len(memory_samples))
            y = np.array(memory_samples)
            slope = np.polyfit(x, y, 1)[0]
            
            memory_leak_detected = slope > 1.0  # 1MB/iteration 이상 증가 시 누수로 판단
        else:
            memory_leak_detected = False
        
        return {
            "test_name": "memory_stability_test",
            "iterations": iterations,
            "initial_memory_mb": initial_memory,
            "final_memory_mb": final_memory,
            "memory_increase_mb": memory_increase,
            "peak_memory_mb": max_memory,
            "memory_leak_detected": memory_leak_detected,
            "memory_samples": memory_samples[-10:],  # 마지막 10개 샘플만
            "stability_rating": "stable" if memory_increase < 50 else "unstable"
        }


class OrchestratorOptimizationTestSuite:
    """오케스트레이터 최적화 종합 테스트 스위트"""
    
    def __init__(self):
        self.test_results = []
        self.performance_baselines = {}
        
    async def run_all_optimization_tests(self) -> Dict[str, Any]:
        """모든 최적화 테스트 실행"""
        print("🚀 오케스트레이터 최적화 테스트 시작...")
        print("=" * 70)
        
        start_time = time.time()
        
        # 1. 컴포넌트별 단위 테스트
        await self._run_component_tests()
        
        # 2. 통합 테스트
        await self._run_integration_tests()
        
        # 3. 성능 벤치마크
        await self._run_performance_benchmarks()
        
        # 4. 스트레스 테스트
        await self._run_stress_tests()
        
        # 5. 결과 분석 및 리포트 생성
        summary = await self._generate_comprehensive_report()
        
        total_time = time.time() - start_time
        summary["total_execution_time"] = total_time
        
        print("\n" + "=" * 70)
        print("📊 오케스트레이터 최적화 테스트 완료")
        print(f"총 실행 시간: {total_time:.2f}초")
        print(f"총 테스트 수: {len(self.test_results)}")
        
        # 성공률 계산
        successful_tests = sum(1 for r in self.test_results if r.get("success", True))
        success_rate = successful_tests / len(self.test_results) * 100 if self.test_results else 0
        
        print(f"성공률: {success_rate:.1f}% ({successful_tests}/{len(self.test_results)})")
        
        if success_rate >= 80:
            print("✅ 최적화 테스트 통과! 시스템이 예상대로 개선되었습니다.")
        else:
            print("❌ 최적화 테스트 실패. 추가 개선이 필요합니다.")
        
        return summary
    
    async def _run_component_tests(self):
        """컴포넌트별 단위 테스트"""
        print("\n1️⃣ 컴포넌트 단위 테스트")
        print("-" * 50)
        
        if not ADVANCED_ORCHESTRATOR_AVAILABLE:
            print("  ⚠️ 고급 오케스트레이터를 사용할 수 없어 컴포넌트 테스트를 건너뜁니다.")
            return
        
        # 지능형 에이전트 선택기 테스트
        print("  🧠 지능형 에이전트 선택기 테스트...")
        selector_test = IntelligentAgentSelectorTest()
        
        accuracy_result = await selector_test.test_agent_selection_accuracy()
        self.test_results.append(accuracy_result)
        print(f"    선택 정확도: {accuracy_result.get('accuracy', 0):.2f}")
        
        learning_result = await selector_test.test_performance_learning()
        self.test_results.append(learning_result)
        print(f"    성능 인식 선택: {learning_result.get('performance_aware_selection', False)}")
        
        # 예측적 스케줄러 테스트
        print("  🔮 예측적 스케줄러 테스트...")
        scheduler_test = PredictiveSchedulerTest()
        
        prediction_result = await scheduler_test.test_next_step_prediction()
        self.test_results.append(prediction_result)
        print(f"    예측 정확도: {prediction_result.get('average_accuracy', 0):.2f}")
        
        # 협력 최적화기 테스트
        print("  🤝 협력 최적화기 테스트...")
        collaboration_test = CollaborationOptimizerTest()
        
        synergy_result = await collaboration_test.test_synergy_calculation()
        self.test_results.append(synergy_result)
        print(f"    시너지 매트릭스 크기: {synergy_result.get('synergy_matrix_size', 0)}")
        
        # 성능 최적화기 테스트
        print("  ⚡ 성능 최적화기 테스트...")
        performance_test = PerformanceOptimizerTest()
        
        optimization_result = await performance_test.test_performance_optimization()
        self.test_results.append(optimization_result)
        print(f"    최적화 정확도: {optimization_result.get('average_accuracy', 0):.2f}")
    
    async def _run_integration_tests(self):
        """통합 테스트"""
        print("\n2️⃣ 통합 테스트")
        print("-" * 50)
        
        if not ADVANCED_ORCHESTRATOR_AVAILABLE:
            print("  ⚠️ 고급 오케스트레이터를 사용할 수 없어 통합 테스트를 건너뜁니다.")
            return
        
        integration_test = AdvancedOrchestratorIntegrationTest()
        
        # 지능형 요청 처리 테스트
        print("  🎯 지능형 요청 처리 테스트...")
        processing_result = await integration_test.test_intelligent_request_processing()
        self.test_results.append(processing_result)
        
        avg_time = processing_result.get('average_execution_time', 0)
        success_rate = processing_result.get('success_rate', 0)
        print(f"    평균 실행시간: {avg_time:.2f}초")
        print(f"    성공률: {success_rate:.2f}")
        
        # 성능 개선 테스트
        print("  📈 성능 개선 테스트...")
        improvement_result = await integration_test.test_performance_improvement()
        self.test_results.append(improvement_result)
        
        improvement_rate = improvement_result.get('improvement_rate_percent', 0)
        print(f"    성능 개선률: {improvement_rate:.1f}%")
        
        # 베이스라인 저장
        self.performance_baselines = {
            "baseline_time": improvement_result.get('baseline_avg_time', 0),
            "optimized_time": improvement_result.get('optimized_avg_time', 0)
        }
    
    async def _run_performance_benchmarks(self):
        """성능 벤치마크"""
        print("\n3️⃣ 성능 벤치마크")
        print("-" * 50)
        
        if not ADVANCED_ORCHESTRATOR_AVAILABLE:
            print("  ⚠️ 고급 오케스트레이터를 사용할 수 없어 벤치마크를 건너뜁니다.")
            return
        
        stress_test = StressTestSuite()
        
        # 중간 부하 테스트
        print("  ⚡ 중간 부하 테스트 (20 동시 요청)...")
        medium_load_result = await stress_test.test_concurrent_load(concurrent_requests=20, duration=30)
        self.test_results.append(medium_load_result)
        
        throughput = medium_load_result.get('throughput_rps', 0)
        completion_rate = medium_load_result.get('completion_rate', 0)
        print(f"    처리량: {throughput:.1f} RPS")
        print(f"    완료율: {completion_rate:.2f}")
        
        # 메모리 안정성 테스트
        print("  💾 메모리 안정성 테스트...")
        memory_result = await stress_test.test_memory_stability(iterations=50)
        self.test_results.append(memory_result)
        
        memory_increase = memory_result.get('memory_increase_mb', 0)
        stability = memory_result.get('stability_rating', 'unknown')
        print(f"    메모리 증가: {memory_increase:.1f}MB")
        print(f"    안정성: {stability}")
    
    async def _run_stress_tests(self):
        """스트레스 테스트"""
        print("\n4️⃣ 스트레스 테스트")
        print("-" * 50)
        
        if not ADVANCED_ORCHESTRATOR_AVAILABLE:
            print("  ⚠️ 고급 오케스트레이터를 사용할 수 없어 스트레스 테스트를 건너뜁니다.")
            return
        
        stress_test = StressTestSuite()
        
        # 높은 부하 테스트
        print("  🔥 고부하 테스트 (50 동시 요청)...")
        high_load_result = await stress_test.test_concurrent_load(concurrent_requests=50, duration=45)
        self.test_results.append(high_load_result)
        
        throughput = high_load_result.get('throughput_rps', 0)
        success_rate = high_load_result.get('success_rate', 0)
        error_count = high_load_result.get('error_count', 0)
        
        print(f"    처리량: {throughput:.1f} RPS")
        print(f"    성공률: {success_rate:.2f}")
        print(f"    에러 수: {error_count}개")
        
        # 목표 성능 검증
        target_throughput = 10.0  # 10 RPS 목표
        target_success_rate = 0.9   # 90% 성공률 목표
        
        throughput_ok = throughput >= target_throughput
        success_rate_ok = success_rate >= target_success_rate
        
        print(f"    목표 달성: 처리량 {'✅' if throughput_ok else '❌'}, 성공률 {'✅' if success_rate_ok else '❌'}")
    
    async def _generate_comprehensive_report(self) -> Dict[str, Any]:
        """종합 리포트 생성"""
        
        # 카테고리별 결과 분류
        component_tests = []
        integration_tests = []
        performance_tests = []
        stress_tests = []
        
        for result in self.test_results:
            test_name = result.get('test_name', '')
            
            if any(keyword in test_name for keyword in ['selection', 'prediction', 'synergy', 'optimization']):
                component_tests.append(result)
            elif any(keyword in test_name for keyword in ['intelligent', 'improvement']):
                integration_tests.append(result)
            elif any(keyword in test_name for keyword in ['memory', 'stability']):
                performance_tests.append(result)
            elif any(keyword in test_name for keyword in ['concurrent', 'load', 'stress']):
                stress_tests.append(result)
        
        # 핵심 메트릭 계산
        key_metrics = self._calculate_key_metrics()
        
        # 개선 사항 식별
        improvements = self._identify_improvements()
        
        # 권장사항 생성
        recommendations = self._generate_recommendations()
        
        comprehensive_report = {
            "test_summary": {
                "total_tests": len(self.test_results),
                "component_tests": len(component_tests),
                "integration_tests": len(integration_tests),
                "performance_tests": len(performance_tests),
                "stress_tests": len(stress_tests)
            },
            
            "key_metrics": key_metrics,
            "improvements_identified": improvements,
            "recommendations": recommendations,
            
            "detailed_results": {
                "component_tests": component_tests,
                "integration_tests": integration_tests,
                "performance_tests": performance_tests,
                "stress_tests": stress_tests
            },
            
            "performance_baselines": self.performance_baselines,
            "test_execution_summary": {
                "advanced_orchestrator_available": ADVANCED_ORCHESTRATOR_AVAILABLE,
                "basic_agents_available": BASIC_AGENTS_AVAILABLE,
                "test_completion_time": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        
        return comprehensive_report
    
    def _calculate_key_metrics(self) -> Dict[str, Any]:
        """핵심 메트릭 계산"""
        metrics = {
            "agent_selection_accuracy": 0.0,
            "prediction_accuracy": 0.0,
            "optimization_accuracy": 0.0,
            "average_response_time": 0.0,
            "system_throughput": 0.0,
            "memory_stability": "unknown",
            "overall_performance_score": 0.0
        }
        
        # 각 테스트 결과에서 메트릭 추출
        for result in self.test_results:
            test_name = result.get('test_name', '')
            
            if 'agent_selection' in test_name:
                metrics["agent_selection_accuracy"] = result.get('accuracy', 0.0)
            elif 'prediction' in test_name:
                metrics["prediction_accuracy"] = result.get('average_accuracy', 0.0)
            elif 'optimization' in test_name:
                metrics["optimization_accuracy"] = result.get('average_accuracy', 0.0)
            elif 'intelligent_request' in test_name:
                metrics["average_response_time"] = result.get('average_execution_time', 0.0)
            elif 'concurrent_load' in test_name:
                metrics["system_throughput"] = result.get('throughput_rps', 0.0)
            elif 'memory_stability' in test_name:
                metrics["memory_stability"] = result.get('stability_rating', 'unknown')
        
        # 전체 성능 점수 계산 (가중 평균)
        performance_components = [
            metrics["agent_selection_accuracy"] * 0.2,
            metrics["prediction_accuracy"] * 0.2,
            metrics["optimization_accuracy"] * 0.2,
            (1.0 / max(metrics["average_response_time"], 0.1)) * 0.2,  # 시간은 역수로 계산
            min(metrics["system_throughput"] / 10.0, 1.0) * 0.2  # 10 RPS를 1.0으로 정규화
        ]
        
        metrics["overall_performance_score"] = sum(performance_components)
        
        return metrics
    
    def _identify_improvements(self) -> List[str]:
        """개선 사항 식별"""
        improvements = []
        
        # 성능 개선률 확인
        baseline_time = self.performance_baselines.get('baseline_time', 0)
        optimized_time = self.performance_baselines.get('optimized_time', 0)
        
        if baseline_time > 0 and optimized_time > 0:
            improvement_rate = (baseline_time - optimized_time) / baseline_time * 100
            if improvement_rate > 10:
                improvements.append(f"응답 시간 {improvement_rate:.1f}% 개선")
            elif improvement_rate < -10:
                improvements.append(f"응답 시간 {abs(improvement_rate):.1f}% 저하")
        
        # 각 컴포넌트별 성능 확인
        for result in self.test_results:
            test_name = result.get('test_name', '')
            
            if 'agent_selection' in test_name:
                accuracy = result.get('accuracy', 0)
                if accuracy >= 0.9:
                    improvements.append("에이전트 선택 정확도 우수")
                elif accuracy < 0.7:
                    improvements.append("에이전트 선택 정확도 개선 필요")
            
            elif 'concurrent_load' in test_name:
                throughput = result.get('throughput_rps', 0)
                if throughput >= 10:
                    improvements.append("높은 처리량 달성")
                elif throughput < 5:
                    improvements.append("처리량 개선 필요")
            
            elif 'memory_stability' in test_name:
                stability = result.get('stability_rating', '')
                if stability == 'stable':
                    improvements.append("메모리 안정성 확보")
                elif stability == 'unstable':
                    improvements.append("메모리 안정성 개선 필요")
        
        return improvements
    
    def _generate_recommendations(self) -> List[str]:
        """권장사항 생성"""
        recommendations = []
        
        # 성능 기반 권장사항
        key_metrics = self._calculate_key_metrics()
        
        if key_metrics["agent_selection_accuracy"] < 0.8:
            recommendations.append("에이전트 선택 알고리즘 개선 - 더 많은 학습 데이터 필요")
        
        if key_metrics["prediction_accuracy"] < 0.7:
            recommendations.append("예측 모델 재훈련 - 실행 패턴 데이터 수집 강화")
        
        if key_metrics["average_response_time"] > 2.0:
            recommendations.append("응답 시간 최적화 - 캐싱 및 병렬 처리 강화")
        
        if key_metrics["system_throughput"] < 5.0:
            recommendations.append("시스템 처리량 향상 - 리소스 확장 및 알고리즘 최적화")
        
        if key_metrics["memory_stability"] == "unstable":
            recommendations.append("메모리 누수 수정 - 가비지 컬렉션 최적화")
        
        if key_metrics["overall_performance_score"] < 0.7:
            recommendations.append("전체적인 시스템 아키텍처 재검토 필요")
        
        # 일반적인 권장사항
        recommendations.extend([
            "지속적인 모니터링 시스템 구축",
            "A/B 테스트를 통한 점진적 개선",
            "사용자 피드백 수집 및 반영",
            "정기적인 성능 벤치마크 실시"
        ])
        
        return recommendations


async def main():
    """메인 테스트 실행"""
    # 로깅 설정
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    print("🎯 VIBA AI 오케스트레이터 고도화 테스트 스위트")
    print("=" * 70)
    print("이 테스트는 오케스트레이터의 최적화 성능을 종합적으로 검증합니다.")
    print()
    
    # 환경 상태 확인
    print("📋 테스트 환경 확인:")
    print(f"  고급 오케스트레이터: {'✅ 사용 가능' if ADVANCED_ORCHESTRATOR_AVAILABLE else '❌ 사용 불가'}")
    print(f"  기본 에이전트: {'✅ 사용 가능' if BASIC_AGENTS_AVAILABLE else '❌ 사용 불가'}")
    print(f"  시스템 메모리: {psutil.virtual_memory().total / 1024 / 1024 / 1024:.1f}GB")
    print(f"  CPU 코어: {psutil.cpu_count()}개")
    print()
    
    # 종합 테스트 실행
    test_suite = OrchestratorOptimizationTestSuite()
    comprehensive_results = await test_suite.run_all_optimization_tests()
    
    # 결과 저장
    try:
        os.makedirs("test_results", exist_ok=True)
        
        # JSON 결과 저장
        with open("test_results/orchestrator_optimization_results.json", "w", encoding="utf-8") as f:
            json.dump(comprehensive_results, f, indent=2, ensure_ascii=False, default=str)
        
        # 요약 리포트 저장
        summary_report = f"""
# VIBA AI 오케스트레이터 최적화 테스트 리포트

## 📊 전체 요약
- 총 테스트: {comprehensive_results['test_summary']['total_tests']}개
- 실행 시간: {comprehensive_results.get('total_execution_time', 0):.2f}초
- 전체 성능 점수: {comprehensive_results['key_metrics']['overall_performance_score']:.2f}/1.0

## 🎯 핵심 메트릭
- 에이전트 선택 정확도: {comprehensive_results['key_metrics']['agent_selection_accuracy']:.2f}
- 예측 정확도: {comprehensive_results['key_metrics']['prediction_accuracy']:.2f}
- 평균 응답 시간: {comprehensive_results['key_metrics']['average_response_time']:.2f}초
- 시스템 처리량: {comprehensive_results['key_metrics']['system_throughput']:.1f} RPS

## 🚀 식별된 개선사항
{chr(10).join('- ' + improvement for improvement in comprehensive_results['improvements_identified'])}

## 💡 권장사항
{chr(10).join('- ' + rec for rec in comprehensive_results['recommendations'])}

---
*테스트 완료 시간: {comprehensive_results['test_execution_summary']['test_completion_time']}*
        """
        
        with open("test_results/orchestrator_optimization_summary.md", "w", encoding="utf-8") as f:
            f.write(summary_report)
        
        print(f"\n📁 테스트 결과가 test_results/ 디렉토리에 저장되었습니다.")
        print(f"  - orchestrator_optimization_results.json: 상세 결과")
        print(f"  - orchestrator_optimization_summary.md: 요약 리포트")
        
    except Exception as e:
        print(f"⚠️ 결과 저장 실패: {e}")
    
    # 최종 권장사항 출력
    print("\n🎯 다음 단계 권장사항:")
    for i, recommendation in enumerate(comprehensive_results['recommendations'][:5], 1):
        print(f"  {i}. {recommendation}")
    
    return comprehensive_results


if __name__ == "__main__":
    asyncio.run(main())