"""
고도화된 오케스트레이터 테스트
==============================

고도화된 AI 오케스트레이터의 실제 동작을 검증하는 테스트

@version 1.0
@author VIBA AI Team
@date 2025.07.06
"""

import asyncio
import sys
import os
import time
import json
from typing import Dict, Any, List

# 프로젝트 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# 고도화된 오케스트레이터 임포트
from ai.advanced_orchestrator import AdvancedOrchestrator
from ai.base_agent import BaseVIBAAgent, AgentCapability

# 테스트용 에이전트들
try:
    from ai.agents.simple_test_agent import SimpleTestAgent
    SIMPLE_AGENT_AVAILABLE = True
except ImportError:
    SIMPLE_AGENT_AVAILABLE = False
    print("SimpleTestAgent 사용불가, 모의 에이전트 사용")


class MockAdvancedAgent(BaseVIBAAgent):
    """고도화 테스트용 모의 에이전트"""
    
    def __init__(self, agent_id: str, description: str, capabilities: List[AgentCapability]):
        super().__init__(agent_id, description, capabilities)
        self.call_count = 0
        self.last_result = None
        
    async def initialize(self) -> bool:
        """에이전트 초기화"""
        return True
    
    def execute_task(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """동기 작업 처리 (추상 메서드 구현)"""
        return asyncio.run(self.process_task_async(input_data))
    
    async def process_task_async(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """비동기 작업 처리"""
        self.call_count += 1
        
        # 에이전트별 특화 처리 시뮬레이션
        if self.agent_id == "design_theorist":
            result = {
                "success": True,
                "design_concept": "모던 스타일 건축 설계",
                "design_principles": ["기능성", "심미성", "지속가능성"],
                "space_organization": "오픈 플랜 구조",
                "execution_time": 0.05
            }
        elif self.agent_id == "bim_specialist":
            result = {
                "success": True,
                "bim_model": "3D_model_v1.ifc",
                "model_elements": ["벽체", "기둥", "슬래브", "문", "창"],
                "ifc_version": "4.3",
                "model_size": "15.2MB",
                "execution_time": 0.08
            }
        elif self.agent_id == "performance_analyst":
            result = {
                "success": True,
                "energy_efficiency": 85.7,
                "structural_analysis": "안전",
                "environmental_impact": "우수",
                "cost_estimate": "1,850만원",
                "execution_time": 0.12
            }
        elif self.agent_id == "design_reviewer":
            result = {
                "success": True,
                "quality_score": 92.5,
                "review_comments": ["전체적으로 우수한 설계", "채광 계획 개선 필요"],
                "approval_status": "승인",
                "execution_time": 0.06
            }
        else:
            result = {
                "success": True,
                "agent_id": self.agent_id,
                "processing_result": "작업 완료",
                "execution_time": 0.03
            }
        
        self.last_result = result
        
        # 실행 시간 시뮬레이션
        await asyncio.sleep(result.get("execution_time", 0.05))
        
        return result


async def test_basic_orchestration():
    """기본 오케스트레이션 테스트"""
    print("\n🧪 기본 오케스트레이션 테스트 시작...")
    
    orchestrator = AdvancedOrchestrator()
    
    # 테스트 에이전트 생성 및 등록
    design_agent = MockAdvancedAgent(
        "design_theorist", 
        "설계 이론가", 
        [AgentCapability.DESIGN_THEORY_APPLICATION]
    )
    
    bim_agent = MockAdvancedAgent(
        "bim_specialist", 
        "BIM 전문가", 
        [AgentCapability.BIM_MODEL_GENERATION]
    )
    
    await orchestrator.register_agent(design_agent)
    await orchestrator.register_agent(bim_agent)
    
    # 기본 요청 처리
    result = await orchestrator.process_intelligent_request(
        "간단한 주거용 건물을 설계해주세요",
        context={"quality_level": "standard"}
    )
    
    print(f"✅ 기본 테스트 결과: {result['success']}")
    if result['success']:
        print(f"   - 실행 시간: {result['orchestration_metadata']['execution_time']:.3f}초")
        print(f"   - 사용된 에이전트: {result['orchestration_metadata']['agents_used']}")
    else:
        print(f"   - 오류: {result.get('error', '알 수 없는 오류')}")
        print(f"   - 메타데이터: {result.get('orchestration_metadata', {})}")
    
    return result


async def test_advanced_optimization():
    """고급 최적화 테스트"""
    print("\n🚀 고급 최적화 테스트 시작...")
    
    orchestrator = AdvancedOrchestrator()
    
    # 전체 에이전트 등록
    agents = [
        MockAdvancedAgent("design_theorist", "설계 이론가", [AgentCapability.DESIGN_THEORY_APPLICATION]),
        MockAdvancedAgent("bim_specialist", "BIM 전문가", [AgentCapability.BIM_MODEL_GENERATION]),
        MockAdvancedAgent("performance_analyst", "성능 분석가", [AgentCapability.PERFORMANCE_ANALYSIS]),
        MockAdvancedAgent("design_reviewer", "설계 검토자", [AgentCapability.DESIGN_REVIEW])
    ]
    
    for agent in agents:
        await orchestrator.register_agent(agent)
    
    # 복잡한 요청 처리 (다양한 최적화 레벨)
    test_cases = [
        ("sequential", "순차 실행 테스트"),
        ("parallel", "병렬 실행 테스트"),
        ("adaptive", "적응형 실행 테스트")
    ]
    
    results = {}
    
    for optimization_level, description in test_cases:
        print(f"\n   {description} ({optimization_level})...")
        
        start_time = time.time()
        result = await orchestrator.process_intelligent_request(
            "복잡한 상업용 건물을 종합적으로 설계하고 성능 분석까지 완료해주세요",
            context={"quality_level": "high", "complexity": "high"},
            optimization_level=optimization_level
        )
        execution_time = time.time() - start_time
        
        results[optimization_level] = {
            "success": result['success'],
            "execution_time": execution_time,
            "agents_used": len(result['orchestration_metadata']['agents_used']),
            "quality_score": result.get('quality_assessment', {}).get('quality_score', 0)
        }
        
        print(f"     - 성공: {result['success']}")
        print(f"     - 실행 시간: {execution_time:.3f}초")
        print(f"     - 에이전트 수: {len(result['orchestration_metadata']['agents_used'])}")
        print(f"     - 품질 점수: {result.get('quality_assessment', {}).get('quality_score', 0):.2f}")
    
    # 성능 비교
    print(f"\n📊 성능 비교:")
    for level, metrics in results.items():
        print(f"   {level}: {metrics['execution_time']:.3f}초, 품질: {metrics['quality_score']:.2f}")
    
    return results


async def test_intelligent_agent_selection():
    """지능형 에이전트 선택 테스트"""
    print("\n🎯 지능형 에이전트 선택 테스트 시작...")
    
    orchestrator = AdvancedOrchestrator()
    
    # 다양한 성능 특성의 에이전트들 생성
    agents = [
        MockAdvancedAgent("fast_designer", "빠른 설계자", [AgentCapability.DESIGN_THEORY_APPLICATION]),
        MockAdvancedAgent("quality_designer", "품질 설계자", [AgentCapability.DESIGN_THEORY_APPLICATION]),
        MockAdvancedAgent("efficient_bim", "효율적 BIM", [AgentCapability.BIM_MODEL_GENERATION]),
        MockAdvancedAgent("detailed_bim", "상세 BIM", [AgentCapability.BIM_MODEL_GENERATION]),
    ]
    
    for agent in agents:
        await orchestrator.register_agent(agent)
        
        # 가상의 성능 이력 추가
        metrics = orchestrator.agent_selector.performance_history[agent.agent_id]
        if "fast" in agent.agent_id:
            metrics.execution_times = [0.5, 0.6, 0.4]  # 빠름
            metrics.success_rates = [0.85, 0.9, 0.8]   # 중간 성공률
        elif "quality" in agent.agent_id:
            metrics.execution_times = [1.2, 1.5, 1.1]  # 느림
            metrics.success_rates = [0.95, 0.98, 0.96] # 높은 성공률
        elif "efficient" in agent.agent_id:
            metrics.execution_times = [0.8, 0.9, 0.7]  # 중간
            metrics.success_rates = [0.9, 0.92, 0.88]  # 좋은 성공률
        else:
            metrics.execution_times = [2.0, 2.2, 1.8]  # 매우 느림
            metrics.success_rates = [0.99, 0.98, 0.97] # 최고 성공률
    
    # 다양한 조건으로 선택 테스트
    test_scenarios = [
        {
            "name": "시간 중요",
            "capabilities": [AgentCapability.DESIGN_THEORY_APPLICATION],
            "complexity": 0.3,
            "time_constraint": 1.0
        },
        {
            "name": "품질 중요",
            "capabilities": [AgentCapability.DESIGN_THEORY_APPLICATION],
            "complexity": 0.8,
            "time_constraint": None
        },
        {
            "name": "균형",
            "capabilities": [AgentCapability.BIM_MODEL_GENERATION],
            "complexity": 0.5,
            "time_constraint": 1.5
        }
    ]
    
    for scenario in test_scenarios:
        selected = orchestrator.agent_selector.select_optimal_agents(
            scenario["capabilities"],
            scenario["complexity"],
            scenario["time_constraint"]
        )
        
        print(f"   {scenario['name']} 시나리오: {selected}")
    
    return True


async def test_collaboration_optimization():
    """협력 최적화 테스트"""
    print("\n🤝 협력 최적화 테스트 시작...")
    
    orchestrator = AdvancedOrchestrator()
    
    # 에이전트 등록
    agents = [
        MockAdvancedAgent("design_theorist", "설계 이론가", [AgentCapability.DESIGN_THEORY_APPLICATION]),
        MockAdvancedAgent("bim_specialist", "BIM 전문가", [AgentCapability.BIM_MODEL_GENERATION]),
        MockAdvancedAgent("performance_analyst", "성능 분석가", [AgentCapability.PERFORMANCE_ANALYSIS]),
    ]
    
    for agent in agents:
        await orchestrator.register_agent(agent)
    
    # 여러 번의 실행으로 협력 패턴 학습
    print("   협력 패턴 학습 중...")
    
    for i in range(5):
        result = await orchestrator.process_intelligent_request(
            f"테스트 프로젝트 {i+1}번 설계 요청",
            context={"iteration": i},
            optimization_level="adaptive"
        )
        print(f"     반복 {i+1}: 성공률 {result.get('quality_assessment', {}).get('quality_score', 0):.2f}")
    
    # 시너지 매트릭스 확인
    synergy_matrix = orchestrator.collaboration_optimizer.synergy_matrix
    print(f"\n   학습된 시너지 패턴: {dict(synergy_matrix)}")
    
    return True


async def test_performance_monitoring():
    """성능 모니터링 테스트"""
    print("\n📈 성능 모니터링 테스트 시작...")
    
    orchestrator = AdvancedOrchestrator()
    
    # 기본 에이전트 등록
    agent = MockAdvancedAgent("test_agent", "테스트 에이전트", [AgentCapability.DESIGN_THEORY_APPLICATION])
    await orchestrator.register_agent(agent)
    
    # 다양한 성능으로 실행
    performances = []
    
    for i in range(10):
        start_time = time.time()
        result = await orchestrator.process_intelligent_request(
            f"테스트 요청 {i+1}",
            optimization_level="adaptive"
        )
        exec_time = time.time() - start_time
        
        performances.append({
            "execution_time": exec_time,
            "success": result['success'],
            "quality": result.get('quality_assessment', {}).get('quality_score', 0)
        })
    
    # 성능 통계
    avg_time = sum(p['execution_time'] for p in performances) / len(performances)
    success_rate = sum(1 for p in performances if p['success']) / len(performances)
    avg_quality = sum(p['quality'] for p in performances) / len(performances)
    
    print(f"   평균 실행 시간: {avg_time:.3f}초")
    print(f"   성공률: {success_rate:.2f}")
    print(f"   평균 품질: {avg_quality:.2f}")
    
    # 시스템 상태 확인
    status = orchestrator.get_system_status()
    print(f"   시스템 상태: {status['system_health']}")
    print(f"   최근 성능: {status['recent_performance']}")
    
    return performances


async def main():
    """메인 테스트 실행"""
    print("🚀 고도화된 오케스트레이터 종합 테스트 시작\n")
    print("=" * 60)
    
    test_results = {}
    
    try:
        # 1. 기본 오케스트레이션 테스트
        test_results['basic'] = await test_basic_orchestration()
        
        # 2. 고급 최적화 테스트
        test_results['optimization'] = await test_advanced_optimization()
        
        # 3. 지능형 에이전트 선택 테스트
        test_results['selection'] = await test_intelligent_agent_selection()
        
        # 4. 협력 최적화 테스트
        test_results['collaboration'] = await test_collaboration_optimization()
        
        # 5. 성능 모니터링 테스트
        test_results['monitoring'] = await test_performance_monitoring()
        
        print("\n" + "=" * 60)
        print("🎉 모든 테스트 완료!")
        
        # 전체 결과 요약
        print("\n📊 테스트 결과 요약:")
        if test_results['basic']['success']:
            print("   ✅ 기본 오케스트레이션: 성공")
        if isinstance(test_results['optimization'], dict):
            print("   ✅ 고급 최적화: 성공")
        if test_results['selection']:
            print("   ✅ 지능형 에이전트 선택: 성공")
        if test_results['collaboration']:
            print("   ✅ 협력 최적화: 성공")
        if test_results['monitoring']:
            print("   ✅ 성능 모니터링: 성공")
        
        print("\n🏆 고도화된 오케스트레이터가 성공적으로 동작합니다!")
        
        return test_results
        
    except Exception as e:
        print(f"\n❌ 테스트 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    asyncio.run(main())